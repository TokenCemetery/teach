---
title: "14. तीनों को मिलाना: Tensor और Pipeline Parallelism अपनी लागत कब वसूल करते हैं"
description: "हर parallelism रणनीति को उस interconnect से मिलाना जो वह सह सकती है, और कब अकेली sharding काफ़ी नहीं होती"
type: lesson
---

# पाठ 14. तीनों को मिलाना: Tensor और Pipeline Parallelism अपनी लागत कब वसूल करते हैं

**मिशन से संबंध:** "समझाएँ कि ZeRO/FSDP क्या shard करते हैं, data parallelism अकेला compute ख़त्म होने से पहले memory से क्यों बाहर हो जाता है, और tensor या pipeline parallelism अपनी communication लागत के लायक़ कब है" "सफलता कैसी दिखती है" का चौथा बिंदु है, और यह पाठ वह जगह है जहाँ वह पूरा होता है: tensor और pipeline parallelism की अतिरिक्त engineering कब अपनाने लायक़ है।
**मुख्य स्रोत:** [पेपर: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
**पूर्व-आवश्यकताएँ:** [पाठ 13](0013-pipeline-parallelism-splitting-the-models-layers.md)

## वार्म-अप

1. ▢ Pipeline bubble क्या है, और pipeline flush उसके बदले क्या सौदा करता है?

<details markdown="1"><summary>जाँचें</summary>

Pipeline bubble batch की शुरुआत और अंत में idle time है, जब pipeline भर रही होती है या ख़ाली हो रही होती है। Pipeline flush pipeline को ख़ाली होने देता है और हर device का optimizer step एक साथ synchronize करता है, और यही bubble की वजह है; विकल्प में यह जोखिम रहता कि किसी microbatch के backward pass को weights का वह अलग version दिखे जो उसके forward pass ने इस्तेमाल किया था।

</details>

2. ▢ Tensor parallelism के MLP बँटवारे में, पूरे block को कितने all-reduce operations चाहिए, और वह कहाँ होता है?

<details markdown="1"><summary>जाँचें</summary>

एक, दूसरे matrix multiplication के बाद, हर device के आंशिक योग को पूरे नतीजे में मिलाते हुए।

</details>

## यह जानें

### तीन अक्ष, मिलाकर

Narayanan et al. तीनों, tensor parallelism, pipeline parallelism और data parallelism, को एक साथ मिलाने को **PTD-P** कहते हैं। हर अक्ष अलग चीज़ बाँटता है: tensor parallelism बाँटता है कि एक अकेली layer क्या compute करती है (पाठ 12), pipeline parallelism बाँटता है कि कोई device किन layers के लिए ज़िम्मेदार है (पाठ 13), और data parallelism (पाठ 7 और 8, ज़रूरत हो तो ZeRO से और shard किया हुआ, पाठ 9 से 11) batch को उस tensor-और-pipeline-parallel setup की replicas में बाँटता है जिसे दोहराया जा रहा है। इस तरह मिलाकर, Narayanan et al. बताते हैं कि उन्होंने 3,072 GPUs पर खरब-parameter model 502 petaFLOP/s पर train किया, जिसमें हर GPU अपने सैद्धांतिक अधिकतम throughput का 52% बनाए रख रहा था, उस पैमाने पर थामे रखने के लिए वाक़ई बड़ा अनुपात।

### बँटवारा सिर्फ़ model नहीं, interconnect के हिसाब से क्यों चलता है

Narayanan et al. इसका सीधा, व्यावहारिक कारण देते हैं कि वे हर अक्ष को devices कैसे सौंपते हैं: tensor parallelism का all-reduce, जो पाठ 12 के बताए अनुसार हर layer पर एक बार चाहिए, इतना महँगा है कि वह सबसे तेज़ संभव interconnect से जुड़े devices तक सीमित रहने पर सबसे अच्छा चलता है, यानी एक अकेले node के भीतर (उनके अपने प्रयोग 8-GPU DGX A100 server इस्तेमाल करते हैं)। इसके उलट, pipeline parallelism सिर्फ़ मुट्ठी भर stage सीमाओं के बीच activations पास करता है, point-to-point communication से जिसे Narayanan et al. "much cheaper" बताते हैं, और जो अलग nodes में फैले होने को बिना पूरे computation को bottleneck किए सह लेता है, उस bubble की क़ीमत पर जो पाठ 13 ने कवर किया। वे अधिकतम प्रदर्शन ख़ास तौर पर तब बताते हैं जब tensor-parallel size एक अकेले node के GPUs की संख्या से मेल खाती है, जो पुष्टि करता है कि यह आकस्मिक ब्योरा नहीं है: यह वह setup है जिसका निशाना उनके अपने नतीजे लगाने को कहते हैं।

### सब जगह ZeRO ही क्यों न इस्तेमाल करें और अतिरिक्त engineering छोड़ दें

Rajbhandari et al. का ZeRO पेपर अपना तर्क सीधे रखता है, कि बड़े model को memory में fit करने के ख़ास मक़सद के लिए, ZeRO-DP (पाठ 9 से 11) model parallelism जितना ही असरदार है, कभी उससे ज़्यादा, तुलनीय या बेहतर scaling कुशलता के साथ, जबकि लागू करने में कहीं आसान है: वे ध्यान दिलाते हैं कि data parallelism बिना बदलाव के अलग-अलग workloads में व्यापक रूप से इस्तेमाल हो सकता है, जबकि tensor और pipeline parallelism जैसे model-parallel तरीक़ों में अक्सर असली engineering काम चाहिए, model ख़ुद संशोधित करना और उसके लिए distributed operators बनाना। Tensor और pipeline parallelism sharding के मुफ़्त विकल्प नहीं हैं; उनकी communication लागत के ऊपर असली development मेहनत लगती है।

दोनों पेपरों की अपनी स्थिति को साथ रखें, तो "tensor या pipeline parallelism अपनी लागत के लायक़ कब है" का व्यावहारिक उत्तर यह है: पहले ZeRO-शैली की sharding अपनाएँ, क्योंकि वह memory समस्या को सबसे कम engineering मेहनत से और बिना model-विशेष काम के सुलझाती है। Tensor और pipeline parallelism तब अपनाएँ जब training run को उससे आगे scale करना हो जो अकेली sharding कुशलता से सँभालती है, आम तौर पर ऐसी device संख्या और model size पर जहाँ sharding के अपने all-gathers का communication overhead अड़चन बन जाए, या जहाँ किसी एक layer के दोबारा बनाए weights sharding के बाद भी एक device के लिए बहुत बड़े हों। उस मोड़ पर, मेल जान-बूझकर चुना जाता है ताकि communication पैटर्न interconnect से मेल खाए: tensor parallelism के बार-बार होने वाले, महँगे all-reduces एक node के भीतर सीमित, pipeline parallelism के कभी-कभार होने वाले, सस्ते point-to-point transfers nodes के आर-पार, और data parallelism (shard हुआ या नहीं) बची हुई device संख्या को भरता है।

## अभ्यास

1. ▢ एक team के पास 64 GPUs हैं, 8 nodes में हर एक में 8 GPUs, तेज़ intra-node interconnect और कहीं धीमे inter-node links के साथ। Narayanan et al. की अपनी बताई अधिकतम-प्रदर्शन configuration का पालन करते हुए, वे इस hardware पर tensor-parallel और pipeline-parallel degrees कैसे सौंपेंगे?

<details markdown="1"><summary>जाँचें</summary>

Tensor-parallel size 8, जो एक node के भीतर के GPUs से मेल खाती है, धीमे inter-node links से दूर रखी हुई; pipeline stages 8 nodes में फैले हुए, क्योंकि pipeline parallelism का point-to-point communication धीमे inter-node connection को बिना computation को bottleneck किए सह लेता है।

</details>

2. ▢ ZeRO पेपर के अपने तर्क के अनुसार, कोई team tensor या pipeline parallelism की जगह ZeRO-DP क्यों चुन सकती है, भले दोनों बहुत बड़े models तक scale होते हों?

    - a) ZeRO-DP हर device संख्या पर, हर model के लिए हमेशा ज़्यादा तेज़ है
    - b) ZeRO-DP तुलनीय या बेहतर memory कुशलता पाता है, उस model-विशेष engineering काम (संशोधित model code, distributed operators) के बिना जो model-parallel तरीक़ों को चाहिए
    - c) Tensor और pipeline parallelism एक device की memory से बड़े models को fit ही नहीं कर सकते
    - d) ZeRO-DP किसी भी तरह के parallelism की ज़रूरत पूरी तरह ख़त्म कर देता है

<details markdown="1"><summary>जाँचें</summary>

**b)** यही तर्क ZeRO पेपर ख़ुद देता है: तुलनीय या बेहतर scaling कुशलता, कहीं कम engineering लागत के साथ, क्योंकि data parallelism बिना model-विशेष बदलाव के व्यापक रूप से लागू होता है। (a) सार्वभौमिक गति-फ़ायदे का ज़्यादा दावा करता है जो पेपर नहीं करता। (c) दोनों पेपरों की बात का उलटा है, कि model parallelism ठीक बड़े models fit करने के लिए ही है। (d) ZeRO-DP की अपनी इस निर्भरता का खंडन करता है कि data parallelism ही उसकी नींव है।

</details>

3. ▢ इस पाठ के तर्क को देखते हुए, एक ठोस स्थिति बताइए जहाँ अतिरिक्त engineering लागत के बावजूद अकेले ZeRO-DP की जगह tensor या pipeline parallelism अपनाना फिर भी सही फ़ैसला होगा।

<details markdown="1"><summary>जाँचें</summary>

इस तरह का कोई भी उत्तर बचाव लायक़ है: जब बहुत बड़ी device संख्या पर sharding का अपना communication overhead अड़चन बन जाए, या जब किसी एक layer के parameters ZeRO की sharding और ज़रूरत पर दोबारा बनाने के बाद भी एक device पर fit होने के लिए बहुत बड़े रह जाएँ, जिससे सिर्फ़ उनका भंडारण नहीं, computation ख़ुद devices में बाँटना पड़े।

</details>

## असली दुनिया का अभ्यास

- [ ] किसी बड़े open model का प्रकाशित training configuration खोजें (कोई technical report या model card जो उसका parallelism setup बताता हो) और पहचानें कि कौन-से हिस्से, अगर कोई हों, tensor parallelism, pipeline parallelism, और data parallelism या ZeRO sharding से मेल खाते हैं।
- [ ] Megatron-LM पेपर (ऊपर linked) का वह अनुच्छेद पढ़ें जो बताता है कि tensor parallelism एक node के भीतर क्यों सीमित है, और एक वाक्य लिखें जो उसकी तुलना ZeRO पेपर के उस तर्क से करे कि जहाँ संभव हो data parallelism को तरजीह दें।
- [ ] कल: अपनी पसंद के किसी काल्पनिक cluster के लिए (nodes और प्रति node GPUs की कोई भी संख्या चुनें), parallelism योजना का ख़ाका बनाएँ: node के भीतर क्या जाएगा, nodes के आर-पार क्या जाएगा, और ZeRO sharding कहाँ बैठेगी, और हर चुनाव का बचाव करते हुए एक वाक्य लिखें।

## आगे बढ़ने के लिए

- [पेपर: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
- [पेपर: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [संसाधन](../RESOURCES.md)

---

चरण 6 ने कवर किया कि compute devices में कैसे बँटता है, इस हिसाब से कि उनके बीच का interconnect क्या सह सकता है। चरण 7 बड़े पैमाने की एक अलग तरह की विफलता की ओर मुड़ता है: training run के अपने numerics, और जब loss curve ठीक बर्ताव करना बंद कर दे तो क्या करें।

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
