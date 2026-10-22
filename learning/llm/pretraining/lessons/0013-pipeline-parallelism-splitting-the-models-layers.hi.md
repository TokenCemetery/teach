---
title: "13. Pipeline Parallelism: Model की Layers को बाँटना"
description: "लगातार layers को अलग-अलग devices को देना, और हर batch की शुरुआत और अंत में उससे होने वाला idle time"
type: lesson
---

# पाठ 13. Pipeline Parallelism: Model की Layers को बाँटना

**मिशन से संबंध:** "समझाएँ कि ZeRO/FSDP क्या shard करते हैं, data parallelism अकेला compute ख़त्म होने से पहले memory से क्यों बाहर हो जाता है, और tensor या pipeline parallelism अपनी communication लागत के लायक़ कब है" "सफलता कैसी दिखती है" का चौथा बिंदु है। पाठ 12 ने किसी layer के अपने computation को devices में बाँटना कवर किया; यह पाठ इसके बजाय model की layers को devices में बाँटना कवर करता है।
**मुख्य स्रोत:** [पेपर: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
**पूर्व-आवश्यकताएँ:** [पाठ 12](0012-tensor-parallelism-splitting-a-layers-matrices.md)

## वार्म-अप

1. ▢ Tensor parallelism के MLP बँटवारे में, पहली weight matrix को rows की जगह columns के साथ बाँटने से `GeLU` लगाने से पहले synchronization step की ज़रूरत क्यों नहीं पड़ती?

<details markdown="1"><summary>जाँचें</summary>

Column split output dimension को बाँटता है, इसलिए हर device का नतीजे का टुकड़ा पहले से पूरा और सही होता है; row split उस dimension को बाँटता जिस पर योग होता है, जिससे हर device के पास सिर्फ़ आंशिक योग रहता, और `GeLU` को आंशिक योग पर सही ढंग से नहीं लगाया जा सकता क्योंकि वह nonlinear है।

</details>

## यह जानें

### Model की गहराई को बाँटना, किसी एक layer की चौड़ाई को नहीं

**Pipeline parallelism** तीसरा तरीक़ा अपनाता है, जो ZeRO (चरण 5) और tensor parallelism (पाठ 12) दोनों से अलग है: किसी एक layer जो compute करती है उसे बाँटने के बजाय, वह model की layers को ही devices में shard करता है। जिस model में वही transformer block कई बार दोहराया गया हो, उसके लिए यह सीधा है: हर device, या **pipeline stage**, को transformer layers की बराबर, लगातार कड़ी दी जाती है, और training example का forward pass devices में क्रम से, stage दर stage, गुज़रता है, जैसे भौतिक assembly line किसी पुर्ज़े को स्टेशन-दर-स्टेशन ले जाती है।

### Batch को microbatches में क्यों बाँटा जाता है

अगर पूरे batch को stage 2 के उस पर कोई काम शुरू करने से पहले stage 1 से पूरी तरह गुज़रना पड़ता, तो एक को छोड़कर हर stage लगभग हर समय बेकार बैठा रहता; उसमें pipeline जैसा कुछ नहीं होता। Narayanan et al. का तरीक़ा इसके बजाय batch को छोटे **microbatches** में बाँटता है और उनके execution को pipeline करता है: जब stage 1 microbatch 2 पर काम कर रहा होता है, तब stage 2 उसी समय microbatch 1 के output पर काम कर सकता है, जैसे असली assembly line में कई पुर्ज़े एक साथ उसके स्टेशनों पर चल रहे होते हैं, बजाय इसके कि एक पुर्ज़ा पूरा करके ही अगला शुरू हो।

### Pipeline bubble

Microbatches को pipeline में आगे-पीछे बिठाने के बाद भी, batch की शुरुआत में, जब तक हर stage के पास करने को कुछ नहीं आया, और अंत में, जब आख़िरी microbatch शुरुआती stages छोड़ चुका हो और सिर्फ़ बाद के stages के पास काम निपटाने को बचा हो, अपरिहार्य idle time होता है। Narayanan et al. इस idle time को **pipeline bubble** कहते हैं, और यह असली क़ीमत है: जितने ज़्यादा pipeline stages होंगे, उपयोगी computation के मुक़ाबले उतना ज़्यादा यह idle time जमा होगा, जब तक कि हर batch में पर्याप्त microbatches इस्तेमाल न हों जो pipeline को दोनों सिरों पर अपरिहार्य भरने और ख़ाली होने के बीच ज़्यादा देर तक भरा रखें।

### Pipelining को समय-समय पर flush क्यों चाहिए

एक बारीकी, जिसके बारे में Narayanan et al. सावधान हैं: भोला pipelining, जो सिर्फ़ throughput के लिए बिना किसी और बाध्यता के चलाया जाए, किसी microbatch के backward pass को weights का ऐसा अलग, पहले से update हुआ version दिखने दे सकता है जो उसके अपने forward pass ने इस्तेमाल किया था, अगर pipeline में आगे के दूसरे microbatches ने अपना optimizer step पहले पूरा कर लिया हो। यह training step का साधारण, synchronous अर्थ तोड़ देता है, जहाँ batch का हर example अपने forward और backward pass में weights का एक सुसंगत सेट देखता है। उस गारंटी को ठीक-ठीक बनाए रखने के लिए Narayanan et al. समय-समय पर **pipeline flushes** लाते हैं: ऐसे बिंदु जहाँ pipeline को पूरी तरह ख़ाली होने दिया जाता है और हर device का optimizer step एक साथ, synchronized होता है, इससे पहले कि अगले batch के microbatches फिर से pipeline भरना शुरू करें। ऊपर बताया गया bubble असल में इसी flush पर होता है; यह synchronous optimizer semantics बनाए रखने की क़ीमत है, बजाय इसके कि weight versions को microbatches में भटकने दिया जाए।

## अभ्यास

1. ▢ 8 transformer layers वाला model 4 pipeline stages में बाँटा गया है, हर एक में 2 layers। अगर पूरे batch को stage 2 के कोई काम शुरू करने से पहले stage 1 को पूरी तरह पूरा करना पड़ता, तो stage 1 के काम करते समय stages 2 से 4 का क्या होता?

<details markdown="1"><summary>जाँचें</summary>

वे बेकार बैठे रहते, क्योंकि उनमें से किसी के पास compute करने को कुछ नहीं होता जब तक stage 1 पूरा batch ख़त्म करके अपना output आगे न दे दे। ठीक यही वह समस्या है जिससे बचने के लिए batch को microbatches में बाँटा जाता है।

</details>

2. ▢ इनमें से कौन-सा सबसे अच्छा बताता है कि pipeline bubble क्या है?

    - a) Pipeline stage सीमाओं पर activations को रखने में इस्तेमाल होने वाली अतिरिक्त memory
    - b) Batch की शुरुआत और अंत में idle time, जब pipeline भर रही होती है या ख़ाली हो रही होती है, जो कोई उपयोगी computation नहीं जोड़ता
    - c) Tensor-parallel all-reduce और अगले matrix multiplication के बीच की communication देरी
    - d) Batches के बीच devices को ठंडा होने देने के लिए जान-बूझकर डाला गया विराम

<details markdown="1"><summary>जाँचें</summary>

**b)** Narayanan et al. इसे ठीक यही नाम देते हैं। (a) pipelining की असली क़ीमत का वर्णन करता है पर ख़ास तौर पर bubble का नहीं। (c) tensor-parallelism की चिंता का वर्णन करता है, pipeline-parallelism की नहीं। (d) idle time का असली कारण नहीं है।

</details>

3. ▢ समय-समय पर pipeline flushes सिर्फ़ throughput के लिए नहीं, बल्कि सही होने के लिए भी क्यों मायने रखते हैं?

<details markdown="1"><summary>संकेत</summary>

सोचें कि किसी एक ख़ास microbatch के backward pass के साथ क्या ग़लत हो सकता है अगर pipeline में आगे के दूसरे microbatches पहले ही optimizer step चला चुके हों।

</details>

<details markdown="1"><summary>जाँचें</summary>

Flush के बिना, किसी microbatch के backward pass को weights का ऐसा अलग, पहले से update हुआ version दिख सकता है जो उसके अपने forward pass ने इस्तेमाल किया था, अगर दूसरे microbatches ने पहले अपना optimizer step पूरा कर लिया हो। यह synchronous optimizer semantics तोड़ देता है, जहाँ batch का हर example अपने forward और backward pass में weights का एक सुसंगत सेट देखने वाला होता है। Flush pipeline को ख़ाली होने देता है और हर device का optimizer step एक साथ होने देता है, bubble की क़ीमत पर उस गारंटी को बचाए रखते हुए।

</details>

4. ▢ एक team pipeline stages की संख्या बदले बिना हर batch में microbatches की संख्या बढ़ाती है। Pipeline bubble में खोए समय के अनुपात पर इसका क्या असर होगा?

<details markdown="1"><summary>जाँचें</summary>

Bubble में खोए समय का अनुपात घटेगा, क्योंकि भरने और ख़ाली होने की तय लागत बीच के ज़्यादा उपयोगी microbatch computation पर बँट जाती है। Bubble ख़ुद ग़ायब नहीं होता, पर प्रति batch लगे कुल समय का छोटा हिस्सा बन जाता है।

</details>

## असली दुनिया का अभ्यास

- [ ] काग़ज़ पर चार pipeline stages और चार microbatches बनाएँ, और ऐसी timeline का ख़ाका खींचें जो दिखाए कि हर समय-चरण पर कौन-सा stage किस microbatch पर काम कर रहा है, शुरुआत और अंत के उन idle खानों समेत जो bubble दर्शाते हैं।
- [ ] Megatron-LM पेपर (ऊपर linked) का वह हिस्सा पढ़ें जो pipeline flushes का वर्णन करता है, और अपने शब्दों में एक वाक्य लिखें जो बताए कि flush क्या गारंटी देता है और अकेली microbatching क्या गारंटी देती है, दोनों में फ़र्क़ करते हुए।
- [ ] कल: आगे देखे बिना, पाठ 14 के लिए एक वाक्य में अनुमान लिखें: यह देखते हुए कि tensor parallelism को हर layer के लिए all-reduce चाहिए जबकि pipeline parallelism को सिर्फ़ मुट्ठी भर stage सीमाओं के बीच activations पास करने हैं, devices के बीच धीमे, लंबी दूरी के network connection को इनमें से कौन बेहतर सह पाएगा?

## आगे बढ़ने के लिए

- [पेपर: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
