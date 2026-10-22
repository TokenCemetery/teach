---
title: "7. Data Parallelism और Gradient All-Reduce"
description: "Batch को ऐसे devices में बाँटना जिनमें से हर एक के पास model की पूरी copy है, और क्या हर copy को एक-जैसा रखता है"
type: lesson
---

# पाठ 7. Data Parallelism और Gradient All-Reduce

**मिशन से संबंध:** "समझाएँ कि ZeRO/FSDP क्या shard करते हैं, data parallelism अकेला compute ख़त्म होने से पहले memory से क्यों बाहर हो जाता है, और tensor या pipeline parallelism अपनी communication लागत के लायक़ कब है" "सफलता कैसी दिखती है" का चौथा बिंदु है। यह पाठ कवर करता है कि data parallelism क्या है और वह सही कैसे बना रहता है; पाठ 8 कवर करता है कि वह memory से बाहर क्यों हो जाता है।
**मुख्य स्रोत:** [पेपर: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**पूर्व-आवश्यकताएँ:** [पाठ 6](0006-chinchilla-the-compute-optimal-correction.md)

## वार्म-अप

1. ▢ `FLOPs(N, D) ≈ 6ND` का इस्तेमाल करके, `6 × 10^21` FLOPs का compute budget 5-अरब-parameter model के लिए लगभग कितने tokens दे सकता है?

<details markdown="1"><summary>जाँचें</summary>

200 अरब tokens: `6 × 10^21 / (6 × 5 × 10^9) = 2 × 10^11`।

</details>

## यह जानें

### Batch को बाँटना, model को नहीं

**Data parallelism** एक ही training run पर एक से ज़्यादा devices को लगाने का सबसे सरल तरीक़ा है: हर device के पास model की पूरी, एक-जैसी copy होती है, और एक बड़ा batch छोटे per-device टुकड़ों में बाँट दिया जाता है, हर device के लिए एक। हर device अपने टुकड़े पर अपना forward और backward pass चलाता है, बाक़ियों से पूरी तरह स्वतंत्र, और अपना स्थानीय gradient निकालता है।

### हर copy को एक-जैसा रखना

अगर हर device बस अपना स्थानीय gradient अपनी weights की copy पर लगाता, तो एक step के बाद copies एक-दूसरे से भटक जातीं, और "N devices एक model train कर रहे हैं" चुपचाप "N devices N अलग models train कर रहे हैं" बन जाता। Data parallelism इससे optimizer चलने से पहले एक synchronization step के ज़रिए बचता है: हर device का स्थानीय gradient सभी devices में एक साथ औसत किया जाता है, **all-reduce** नाम के collective communication operation से, और हर device को वही औसत gradient वापस मिलता है। चूँकि हर device फिर वही एक-जैसा औसत gradient weights की एक-जैसी शुरुआती copy पर लगाता है, optimizer step के बाद सभी copies एक-जैसी रहती हैं, step दर step, weights को आपस में मिलाए बिना।

इसे कुशलता से लागू करने का एक आम तरीक़ा **ring all-reduce** है: devices को तार्किक ring में सजाया जाता है, और हर एक सिर्फ़ अपने दो पड़ोसियों से data की अदला-बदली करता है, चरणों के ऐसे क्रम में जो गारंटी देता है कि हर device के पास पूरा योग (और फिर औसत) पहुँच जाए, बिना ज़रूरत के कि कोई एक device सबसे सीधे सब कुछ इकट्ठा करे। इससे जैसे-जैसे devices जुड़ते हैं, हर device की communication मात्रा लगभग स्थिर रहती है, device count के साथ बढ़ने के बजाय, और इसी से data parallelism पहली जगह पर ठीक-ठाक scale कर पाता है।

### यह क्या देता है, और किसे नहीं छूता

Data parallelism का पूरा फ़ायदा throughput है: `k` devices के साथ, प्रति इकाई wall-clock समय में `k` गुना ज़्यादा data process हो सकता है, क्योंकि हर device batch के अपने हिस्से पर स्वतंत्र काम कर रहा है। इससे किसी एक device को कितनी memory चाहिए, इसमें कुछ नहीं बदलता। हर device के पास अब भी model के parameters, उसके gradients और उसकी optimizer state की पूरी copy है, ठीक वैसे जैसे अकेले train करते समय होती; ज़्यादा data-parallel devices जोड़ने से उसी memory footprint की ज़्यादा copies जुड़ती हैं, हर device पर कम footprint नहीं। Data parallelism तय आकार के model की training का ज़्यादा हिस्सा तेज़ी से process करने का तरीक़ा है; अपने-आप में, यह उस model को fit करने का तरीक़ा नहीं है जो एक अकेला device वरना न रख पाता। पाठ 8 इस सीमा को ठोस बनाता है।

## अभ्यास

1. ▢ चार devices data parallelism से एक model train करते हैं। Device 3 उस step में ऐसा स्थानीय gradient निकालता है जो बाक़ी तीन devices के gradients के मुक़ाबले असामान्य रूप से बड़ा है, इस वजह से कि batch के उसके हिस्से में जो कुछ आया। क्या device 3 की weights की copy को बाक़ी तीन से दूर भटकने से रोकता है?

<details markdown="1"><summary>जाँचें</summary>

All-reduce step। हर device का स्थानीय gradient, device 3 के असामान्य रूप से बड़े वाले समेत, किसी भी device के update लगाने से पहले चारों devices में औसत किया जाता है, इसलिए हर device weights की एक-जैसी शुरुआती copy पर वही औसत gradient लगाता है, और चारों copies एक-जैसी रहती हैं।

</details>

2. ▢ इनमें से कौन-सा सबसे अच्छा बताता है कि ज़्यादा data-parallel devices जोड़ने से training run में क्या बदलता है?

    - a) हर device को model रखने के लिए चाहिए memory की मात्रा घट जाती है
    - b) प्रति इकाई समय में batch का ज़्यादा हिस्सा process हो पाता है, बिना इसे बदले कि किसी एक device को कितनी memory चाहिए
    - c) Optimizer step की ज़रूरत पूरी तरह ख़त्म हो जाती है
    - d) Model का parameter count अपने-आप बढ़ जाता है

<details markdown="1"><summary>संकेत</summary>

सोचें कि data parallelism में devices में असल में क्या बँटता है: model, या batch?

</details>

<details markdown="1"><summary>जाँचें</summary>

**b)** Data parallelism batch को बाँटता है, model को नहीं, इसलिए throughput device count के साथ बढ़ता है जबकि per-device memory नहीं घटती। (a) ठीक उलटा है, जिसे पाठ 8 ठोस बनाता है। (c) और (d) ऐसे बदलावों का वर्णन करते हैं जो data parallelism बिल्कुल नहीं करता।

</details>

3. ▢ Ring all-reduce में, हर device सिर्फ़ ring में अपने दो पड़ोसियों से ही क्यों बात करता है, बजाय इसके कि हर device अपना gradient हर दूसरे device को सीधे भेजे?

<details markdown="1"><summary>जाँचें</summary>

ताकि ring में जैसे-जैसे ज़्यादा devices जुड़ें, किसी एक device को जितनी communication मात्रा सँभालनी पड़ती है वह लगभग स्थिर रहे, devices की संख्या के साथ बढ़ने के बजाय, और यही इस तरीक़े को कई devices तक scale होने देता है बिना communication ख़ुद bottleneck बने।

</details>

## असली दुनिया का अभ्यास

- [ ] जिस data-parallel training API तक आपकी पहुँच है उसका दस्तावेज़ खोजें (PyTorch का `DistributedDataParallel` एक आम उदाहरण है) और वह जगह ढूँढें जहाँ वह gradient-synchronization step का वर्णन करता है। नोट करें कि वह उस operation को क्या कहता है, और क्या वर्णन "all-reduce" से मेल खाता है जैसा यह पाठ उसे बताता है।
- [ ] काग़ज़ पर ring में सजे चार devices का ख़ाका बनाएँ, और हाथ से कुछ steps में पता लगाएँ कि ring all-reduce में एक अकेला device क्या भेजता और पाता है, 4 संख्याओं वाले छोटे gradient vector के साथ, हर device को एक संख्या देकर।
- [ ] कल: आगे देखे बिना, पाठ 8 के लिए एक वाक्य में अनुमान लिखें: अगर हर data-parallel device के पास model के parameters, gradients और optimizer state की पूरी copy होनी ज़रूरी है, तो जब model बड़ा होता जाए और devices की संख्या तय रहे तो क्या होता है?

## आगे बढ़ने के लिए

- [पेपर: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
