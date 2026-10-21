---
title: "12. Tensor Parallelism: Layer की Matrices को बाँटना"
description: "Weight matrix को किस अक्ष पर बाँटना है यह चुनना, ताकि पूरे transformer block को सिर्फ़ एक all-reduce चाहिए"
type: lesson
---

# पाठ 12. Tensor Parallelism: Layer की Matrices को बाँटना

**मिशन से संबंध:** "समझाएँ कि ZeRO/FSDP क्या shard करते हैं, data parallelism अकेला compute ख़त्म होने से पहले memory से क्यों बाहर हो जाता है, और tensor या pipeline parallelism अपनी communication लागत के लायक़ कब है" "सफलता कैसी दिखती है" का चौथा बिंदु है। यह पाठ कवर करता है कि tensor parallelism असल में क्या बाँटता है और क्यों; पाठ 13 pipeline parallelism को कवर करता है, और पाठ 14 कवर करता है कि इनमें से कोई भी अपनी लागत के लायक़ कब है।
**मुख्य स्रोत:** [पेपर: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
**पूर्व-आवश्यकताएँ:** [पाठ 11](0011-activation-memory-and-zero-r.md)

## वार्म-अप

1. ▢ ZeRO stage 3 आराम की अवस्था में parameters को shard करता है पर layer के forward या backward pass से पहले all-gather से पूरा parameter tensor ज़रूरत पर दोबारा बना लेता है। Parameters दोबारा बन जाने के बाद क्या हर device वही पूरी layer compute करता है, या हर device layer के math का अलग हिस्सा compute करता है?

<details markdown="1"><summary>जाँचें</summary>

हर device वही पूरी layer compute करता है, उस layer के parameters की अपनी दोबारा बनाई पूरी copy से। ZeRO यह shard करता है कि parameters आराम की अवस्था में कहाँ रहते हैं; वह किसी एक layer के computation को devices में नहीं बाँटता।

</details>

## यह जानें

### Computation को बाँटना, सिर्फ़ यह नहीं कि weights कहाँ रहते हैं

**Tensor parallelism** चरण 5 की किसी भी चीज़ से अलग तरीक़ा अपनाता है: किसी एक device पर layer के पूरे weights दोबारा बनाने के बजाय, वह किसी एक layer की weight matrices को devices में बाँट देता है ताकि हर device सिर्फ़ layer का अपना टुकड़ा रखे, और सिर्फ़ उसी के साथ compute करे। किसी device को कभी पूरी weight matrix एक साथ नहीं चाहिए।

### हल किया हुआ उदाहरण: MLP block

Transformer का MLP block `Y = GeLU(XA)` और फिर `Z = Dropout(YB)` compute करता है, बीच में nonlinearity के साथ दो matrix multiplications। Narayanan et al. वह ख़ास तरीक़ा बताते हैं जिससे Megatron इसे बाँटता है और communication को न्यूनतम रखता है: पहली weight matrix `A` को **उसके columns के साथ** बाँटें, `A = [A1, A2]`, जिससे हर device को पूरा, स्वतंत्र रूप से compute होने वाला output का टुकड़ा मिलता है, `Y1 = GeLU(XA1)` और `Y2 = GeLU(XA2)`, और इन्हें compute करने के लिए दोनों devices के बीच कोई synchronization नहीं चाहिए। यह इसलिए काम करता है कि columns के साथ बाँटना *output* dimension को बाँटता है, उस dimension को नहीं जिस पर योग होता है, इसलिए `Y` का हर device का टुकड़ा अपने columns के लिए पहले ही सच्चा, पूरा उत्तर है, और elementwise लगने वाला `GeLU` हर पूरे टुकड़े पर स्वतंत्र रूप से लगाया जा सकता है।

दूसरी weight matrix, `B`, को फिर मेल बिठाने के लिए **उसकी rows के साथ** बाँटा जाता है, `B = [B1; B2]`, इसलिए हर device `Y` और `B` के सिर्फ़ अपने स्थानीय टुकड़े से `Yi @ Bi` compute करता है। इससे हर device को सच्चे output `Z` की ओर एक आंशिक योग मिलता है; दोनों devices के आंशिक योगों को एक अकेले all-reduce से मिलाया जाता है, और उसके बाद ही पूरे, सही नतीजे पर dropout लगता है।

### पहले column, फिर row, उलटा क्यों नहीं

अगर `A` को इसके बजाय उसकी rows के साथ बाँटा जाता (उस dimension को बाँटते हुए जिस पर योग होता है, output dimension को नहीं), तो `X @ A` का हर device का टुकड़ा सच्चे pre-activation मानों की ओर सिर्फ़ **आंशिक योग** होता, पूरा उत्तर नहीं, क्योंकि contraction dimension के सिर्फ़ एक हिस्से पर योग करने से किसी भी output column के लिए सही संख्या नहीं मिलती। `GeLU` को आंशिक योग पर सही ढंग से लगाकर बाद में मिलाया नहीं जा सकता, क्योंकि `GeLU` nonlinear है: `GeLU(a + b)`, `GeLU(a) + GeLU(b)` नहीं होता। `A` को columns से बाँटना पहली जगह पर आंशिक योग पर nonlinearity लगाने की ज़रूरत से ही बचा लेता है, और Narayanan et al. इसे चुनने का यही कारण देते हैं। Column-फिर-row की जोड़ी ही वह चीज़ है जो पूरे दो-matrix MLP block को सिर्फ़ **एक** all-reduce देती है, बिल्कुल अंत में, दोनों matrix multiplications के बीच भी synchronization step की ज़रूरत के बजाय।

### यही पैटर्न attention पर लागू होता है

Multi-head attention में बाँटने के लिए पहले से स्वाभाविक जगह है: query, key और value projections column-parallel partition किए जाते हैं, इसलिए हर device attention heads के एक उपसमूह को स्वतंत्र रूप से सँभालता है, और attention computation के दौरान devices के बीच किसी समन्वय की ज़रूरत नहीं पड़ती। इसके बाद आने वाले output projection को मेल बिठाने के लिए उसकी rows के साथ बाँटा जाता है, MLP block जैसी ही column-फिर-row जोड़ी, और attention block के अंत में एक all-reduce चाहिए।

## अभ्यास

1. ▢ Transformer के MLP block को इस पाठ के बताए अनुसार `A` को उसके columns के साथ और `B` को उसकी rows के साथ बाँटा गया है। `X` से अंतिम `Z` तक पूरे block के लिए इस योजना को कितने all-reduce operations चाहिए?

<details markdown="1"><summary>जाँचें</summary>

एक, दूसरे matrix multiplication के ठीक बाद, हर device के `Z` के आंशिक योग को पूरे नतीजे में मिलाने के लिए। `A` का column split दोनों matrix multiplications के बीच किसी भी synchronization की ज़रूरत से बचा लेता है।

</details>

2. ▢ अगर `A` को उसके columns की जगह rows के साथ बाँटा जाता, तो पहले matrix multiplication के तुरंत बाद `GeLU` लगाने में क्या ग़लत होता?

<details markdown="1"><summary>संकेत</summary>

सोचें कि जब योग वाला dimension बाँटा गया हो, output dimension नहीं, तब हर device का स्थानीय नतीजा असल में क्या दर्शाता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

हर device के पास सच्चे pre-activation मानों की ओर सिर्फ़ आंशिक योग होता, पूरे मान नहीं, क्योंकि हर device के स्थानीय computation में contraction dimension का सिर्फ़ एक हिस्सा शामिल था। `GeLU` nonlinear है, इसलिए उसे आंशिक योग पर लगाकर नतीजों को बाद में मिलाने से वही उत्तर नहीं मिलता जो पूरे योग पर लगाने से मिलता, यानी `GeLU` के सही ढंग से चल पाने से पहले ही एक synchronization step चाहिए होता।

</details>

3. ▢ Attention block में, query, key और value projections कैसे बाँटे जाते हैं, और multi-head attention की कौन-सी स्वाभाविक ख़ासियत उस बँटवारे को सुविधाजनक बनाती है?

<details markdown="1"><summary>जाँचें</summary>

उन्हें column-parallel बाँटा जाता है, उसी तरह जैसे MLP block में `A` बाँटा जाता है। Multi-head attention पहले से हर head का attention बाक़ियों से स्वतंत्र रूप से compute करता है, इसलिए अलग heads (या heads के समूह) को अलग devices को देने के लिए attention computation के दौरान किसी समन्वय की ज़रूरत नहीं होती, ठीक वैसे जैसे MLP के output dimension को बाँटने के लिए नहीं थी।

</details>

4. ▢ इस पाठ के बताए tensor parallelism को ZeRO stage 3 के उलट किसी एक device पर layer की पूरी weight matrix दोबारा बनाने की ज़रूरत क्यों नहीं पड़ती?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि हर device सिर्फ़ weight matrix के अपने टुकड़े के साथ compute करता है; column-फिर-row बँटवारा ख़ास तौर पर इसलिए चुना गया है कि हर device पर हर बीच का computation या तो पूरा, स्वतंत्र नतीजा हो (column split के बाद) या आंशिक योग हो जिसे all-reduce मिला दे (row split के बाद), न कि ऐसा जिसके लिए पूरी matrix कहीं भी मौजूद होनी पड़े।

</details>

## असली दुनिया का अभ्यास

- [ ] Megatron-LM पेपर (ऊपर linked) में tensor parallelism का वर्णन पढ़ें, और वह figure खोजें जो MLP और attention block के बँटवारे दिखाती है। अपने शब्दों में पता लगाएँ कि हर `f` और `g` operator (पेपर का forward/backward में identity-बनाम-all-reduce जोड़ी के लिए संकेतन) diagram में कहाँ बैठता है।
- [ ] काग़ज़ पर 4-rows-गुना-2-columns की weight matrix `A` और 2-rows-गुना-4-columns का input `X` बनाएँ, और हाथ से हल करें कि `X @ A` कैसा दिखता है जब `A` को columns से दो 4-rows-गुना-1-column टुकड़ों में बाँटा जाए, बनाम rows से दो 2-rows-गुना-4-columns टुकड़ों में। पुष्टि करें कि किस बँटवारे में हर device को पूरा उत्तर मिलता है।
- [ ] कल: आगे देखे बिना, पाठ 13 के लिए एक वाक्य में अनुमान लिखें: अगर tensor parallelism को हर transformer layer के लिए all-reduce चाहिए, तो devices के बीच किस तरह का interconnect चाहिए होगा, और क्या आप उम्मीद करेंगे कि वह अलग-अलग भौतिक server racks के devices के बीच भी उतना ही अच्छा चलेगा?

## आगे बढ़ने के लिए

- [पेपर: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
