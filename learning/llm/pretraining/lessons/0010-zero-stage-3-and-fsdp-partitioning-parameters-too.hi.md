---
title: "10. ZeRO Stage 3 और FSDP: Parameters की भी Partitioning"
description: "Parameters को ही shard करने का मतलब है उन्हें ज़रूरत पर दोबारा बनाना, और यही इसकी सबसे पहली क़ीमत है"
type: lesson
---

# पाठ 10. ZeRO Stage 3 और FSDP: Parameters की भी Partitioning

**मिशन से संबंध:** "समझाएँ कि ZeRO/FSDP क्या shard करते हैं, data parallelism अकेला compute ख़त्म होने से पहले memory से क्यों बाहर हो जाता है, और tensor या pipeline parallelism अपनी communication लागत के लायक़ कब है" "सफलता कैसी दिखती है" का चौथा बिंदु है। पाठ 9 ने उन दो stages को कवर किया जो optimizer state और gradients को मुफ़्त में partition करते हैं; यह पाठ तीसरे को कवर करता है, जो parameters को ही partition करता है, और उसके असली API को।
**मुख्य स्रोत:** [दस्तावेज़: "Fully Sharded Data Parallel", PyTorch](https://pytorch.org/docs/stable/fsdp.html)
**पूर्व-आवश्यकताएँ:** [पाठ 9](0009-zero-stage-1-and-2-partitioning-optimizer-state-and-gradients.md)

## वार्म-अप

1. ▢ ZeRO stage 2 (`P_os+g`) कितनी memory कमी देता है, और साधारण data parallelism के मुक़ाबले किस communication लागत पर?

<details markdown="1"><summary>जाँचें</summary>

8 गुना memory कमी, साधारण data parallelism जितनी ही communication मात्रा पर: कोई अतिरिक्त data नहीं चलना पड़ता, क्योंकि optimizer state और gradients की ज़रूरत सिर्फ़ स्थानीय रूप से पड़ती है, संबंधित shard के लिए ज़िम्मेदार device को।

</details>

2. ▢ Optimizer state और gradients को बिना अतिरिक्त communication के partition क्यों किया जा सकता है, जबकि इस पाठ का विषय वैसा नहीं कर सकता?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि parameters के किसी shard के लिए ज़िम्मेदार device को ही उस shard का optimizer state या gradient कभी चाहिए। इसके उलट, हर device के forward और backward pass को model का हर parameter चाहिए, सिर्फ़ वे नहीं जिनका वह मालिक है, और पाठ 10 को यही हिसाब में लेना है।

</details>

## यह जानें

### आख़िरी हिस्सा: parameters की partitioning

**`P_os+g+p`**, ZeRO का तीसरा stage, optimizer state और gradients के ऊपर, जिन्हें stage 2 पहले ही partition करता है, parameters को ही partition करता है: हर device आराम की अवस्था में parameters का सिर्फ़ `1/Nd` रखता है, पूरी copy नहीं। Rajbhandari et al. बताते हैं कि इस stage की memory कमी data-parallel degree `Nd` के साथ रैखिक रूप से बढ़ती है: 64 devices में बाँटने से 64 गुना memory कमी मिलती है, और यही उनके headline नतीजे को काम करने लायक़ बनाता है: उनका अनुमान है कि mixed-precision Adam में खरब-parameter model को अपनी model states के लिए लगभग 16 terabytes चाहिए, जो 1,024 GPUs में बाँटने पर प्रति device लगभग 16 GB आता है, जो 32 GB के GPU में आराम से समा जाता है।

यह कमी उस तरह मुफ़्त नहीं है जैसे stages 1 और 2 थे। हर device के forward और backward pass को अब भी हर parameter चाहिए, सिर्फ़ वह `1/Nd` नहीं जो वह रखता है, इसलिए जो parameters किसी device के पास नहीं हैं उन्हें ज़रूरत के क्षण दूसरे devices से दोबारा बनाना पड़ता है, और उस computation के ख़त्म होते ही फिर फेंक देना पड़ता है। Rajbhandari et al. बताते हैं कि इसकी क़ीमत साधारण data parallelism के ऊपर communication मात्रा में मामूली 50% बढ़ोतरी है, उस memory कमी के बदले जो devices जोड़ने के साथ बढ़ती रहती है, stages 1 और 2 की तरह 8 गुना पर समतल हो जाने के बजाय।

### तंत्र: ज़रूरत पर इकट्ठा करें, फिर छोड़ दें

Stage 3 जो पैटर्न इस्तेमाल करता है वह यह है: आराम की अवस्था में सिर्फ़ parameters का अपना shard रखें; किसी layer को forward या backward computation के लिए पूरे parameters चाहिए होने से ठीक पहले, दूसरे devices से छूटे हुए टुकड़ों का **all-gather** करें ताकि पूरा parameter tensor अस्थायी रूप से दोबारा बन जाए; उस layer का computation पूरा होते ही दोबारा बनाई copy को मुक्त करें और फिर सिर्फ़ अपना shard रखने पर लौट आएँ। यह किसी भी दूसरे जैसा ही all-gather collective operation है, बस कहीं ज़्यादा बार चलता है, हर pass में हर layer पर एक बार, न कि प्रति training step एक बार जैसा साधारण data parallelism में gradient synchronization होता है।

### FSDP: वही विचार, असली API के रूप में

PyTorch का `FullyShardedDataParallel`, जिसे आम तौर पर **FSDP** कहा जाता है, ठीक यही पैटर्न लागू करता है, और उसका अपना दस्तावेज़ यह सीधे कहता है: वह ख़ुद को "inspired by ... the ZeRO Stage 3 from DeepSpeed" बताता है। किसी module को FSDP में wrap करने पर उसके parameters data-parallel devices में shard हो जाते हैं, और forward तथा backward pass के दौरान FSDP module के parameters को ज़रूरत पर इकट्ठा किए दोबारा बनाए views से बदल देता है, वही gather-फिर-release पैटर्न जिसे यह पाठ अभी अमूर्त रूप में बता चुका। FSDP हल्की sharding strategies भी देता है जो सिर्फ़ gradients और optimizer state को shard करती हैं और parameters को shard नहीं करतीं, जो वही सौदा है जो stage 2 करता है, stage 3 नहीं: कम memory बचती है, पर हर forward और backward pass में parameters के लिए अतिरिक्त all-gather traffic नहीं जुड़ता।

## अभ्यास

1. ▢ ZeRO stage 3 की बताई scaling का इस्तेमाल करके, model के parameters, gradients और optimizer state को 32 devices में बाँटने से team को लगभग कितनी memory कमी की उम्मीद करनी चाहिए?

<details markdown="1"><summary>जाँचें</summary>

लगभग 32 गुना, क्योंकि Rajbhandari et al. बताते हैं कि stage 3 की memory कमी data-parallel degree `Nd` के साथ रैखिक रूप से बढ़ती है (उनके अपने उदाहरण में 64 devices पर 64 गुना मिलता है, इसलिए 32 devices पर लगभग उसका आधा)।

</details>

2. ▢ Parameters को ही partition करने के लिए अतिरिक्त communication क्यों चाहिए जबकि optimizer state और gradients को partition करने के लिए नहीं चाहिए था?

    - a) Parameters अलग संख्यात्मक precision में रखे जाते हैं, जिसे भेजना ज़्यादा महँगा है
    - b) हर device के forward और backward pass को parameters का पूरा सेट चाहिए, सिर्फ़ वह shard नहीं जिसका वह मालिक है, इसलिए छूटे हुए shards ज़रूरत पर दूसरे devices से इकट्ठा करने पड़ते हैं
    - c) Parameter partitioning के लिए gradient partitioning से धीमा network protocol चाहिए
    - d) असल में इसके लिए अतिरिक्त communication नहीं चाहिए; पेपर का 50% वाला आँकड़ा किसी दूसरी तुलना का है

<details markdown="1"><summary>जाँचें</summary>

**b)** यही असली तंत्र है: optimizer state और gradients के उलट, जिन्हें सिर्फ़ मालिक device कभी चाहता है, parameters हर layer के forward और backward computation के लिए हर device को चाहिए, इसलिए जो shards किसी device के पास नहीं हैं उन्हें एक all-gather को दोबारा बनाना पड़ता है। (a), (c) और (d) असली कारण का वर्णन नहीं करते।

</details>

3. ▢ एक team `FULL_SHARD` की जगह PyTorch FSDP की `SHARD_GRAD_OP` strategy चुनती है। यह किस ZeRO stage से मेल खाती है, और `FULL_SHARD` के मुक़ाबले यह कौन-सा सौदा करती है?

<details markdown="1"><summary>संकेत</summary>

`SHARD_GRAD_OP` parameters को shard किए बिना, उनके पूरे रूप में खुला छोड़ देती है, और सिर्फ़ gradients और optimizer state को shard करती है।

</details>

<details markdown="1"><summary>जाँचें</summary>

यह ZeRO stage 2 से मेल खाती है। यह `FULL_SHARD` (stage 3) से कम memory बचाती है, क्योंकि parameters partition नहीं होते, पर साथ ही उस अतिरिक्त all-gather traffic से भी बचती है जो stage 3 को हर forward और backward pass में ज़रूरत पर parameters दोबारा बनाने के लिए चाहिए।

</details>

## असली दुनिया का अभ्यास

- [ ] PyTorch का FSDP दस्तावेज़ (ऊपर linked) पढ़ें और वह वर्णन खोजें कि forward pass के दौरान wrap किए module के parameters का क्या होता है। उसे इस पाठ के बताए "इकट्ठा करें, फिर छोड़ें" पैटर्न से जोड़ते हुए एक वाक्य लिखें।
- [ ] इस पाठ के खरब-parameter, 1,024-GPU उदाहरण (लगभग 16 TB model states, प्रति device 16 GB) का इस्तेमाल करके 64 devices में बँटे 100-अरब-parameter model के लिए वही गणना दोबारा करें, और जाँचें कि वह 80 GB के GPU में आराम से समाता है या नहीं।
- [ ] कल: FSDP या DeepSpeed के दस्तावेज़ में कोई configuration उदाहरण खोजें जो sharding strategy को साफ़ तौर पर तय करता हो, और इस पाठ तथा पाठ 9 के इस वर्णन का इस्तेमाल करके पहचानें कि वह ख़ास configuration किस ZeRO stage से मेल खाता है कि हर stage क्या shard करता है।

## आगे बढ़ने के लिए

- [पेपर: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
