---
title: "9. ZeRO Stage 1 और 2: Optimizer State और Gradients की Partitioning"
description: "Data parallelism की फ़ालतू copies मुफ़्त में हटाना, इससे पहले कि communication लागत को बढ़ना पड़े"
type: lesson
---

# पाठ 9. ZeRO Stage 1 और 2: Optimizer State और Gradients की Partitioning

**मिशन से संबंध:** "समझाएँ कि ZeRO/FSDP क्या shard करते हैं, data parallelism अकेला compute ख़त्म होने से पहले memory से क्यों बाहर हो जाता है, और tensor या pipeline parallelism अपनी communication लागत के लायक़ कब है" "सफलता कैसी दिखती है" का चौथा बिंदु है। यह पाठ ZeRO के तीन stages में से पहले दो को कवर करता है; पाठ 10 तीसरे को कवर करता है।
**मुख्य स्रोत:** [पेपर: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**पूर्व-आवश्यकताएँ:** [पाठ 8](0008-why-data-parallelism-alone-runs-out-of-memory.md)

## वार्म-अप

1. ▢ Mixed-precision Adam के तहत, वे पाँच प्रति-parameter memory लागतें कौन-सी हैं जो मिलकर प्रति parameter 16 bytes बनाती हैं?

<details markdown="1"><summary>जाँचें</summary>

Parameters की एक fp16 copy (2 bytes), gradients की एक fp16 copy (2 bytes), और optimizer की रखी parameters, momentum और variance की एक-एक fp32 copy (हर एक 4 bytes), कुल 16 bytes।

</details>

2. ▢ क्या साधारण data parallelism ज़्यादा devices जोड़ने पर प्रति device उन 16 bytes में से कुछ घटाता है?

<details markdown="1"><summary>जाँचें</summary>

नहीं। हर device के पास प्रति parameter पूरे, एक-जैसे 16 bytes होते हैं, चाहे कितने भी दूसरे devices हों; devices जोड़ने से ज़्यादा फ़ालतू copies जुड़ती हैं, प्रति device छोटा footprint नहीं।

</details>

## यह जानें

### वह फ़ालतूपन जिसे ZeRO हटाता है

पाठ 8 ने स्थापित किया कि हर data-parallel device के पास optimizer state, gradients और parameters की पूरी, एक-जैसी copy होती है। ZeRO का मूल विचार यह है कि यह फ़ालतूपन ग़ैर-ज़रूरी है: `Nd` data-parallel devices में, उस state की कुल मिलाकर सिर्फ़ एक पूरी copy होनी चाहिए, `Nd` टुकड़ों में बँटी हुई, हर device पर एक टुकड़ा, और हर device जो टुकड़ा उसके पास नहीं है उसे तभी दोबारा बनाए या पाए जब किसी computation के लिए वह सचमुच ज़रूरी हो। Rajbhandari et al. इसे ZeRO-DP कहते हैं, और इसे तीन stages के रूप में परिभाषित करते हैं जिन्हें संचयी रूप से चालू किया जा सकता है, और हर stage पिछले से model states का एक और हिस्सा partition करता है।

### Stage 1: optimizer state की partitioning

**`P_os`** (optimizer state partitioning) सिर्फ़ optimizer state को बाँटता है, जो प्रति parameter 16 bytes में सबसे बड़ा अकेला हिस्सा है (fp32 parameter copy, momentum और variance: 16 में से 12 bytes), `Nd` devices में, इसलिए हर device उसका सिर्फ़ `1/Nd` रखता है, पूरा नहीं। Rajbhandari et al. बताते हैं कि अकेला यही 4 गुना memory कमी देता है, **साधारण data parallelism जितनी ही communication मात्रा** पर: gradient all-reduce को जितना चाहिए था उससे ज़्यादा कोई data devices के बीच नहीं जाना पड़ता, क्योंकि optimizer state की ज़रूरत सिर्फ़ स्थानीय रूप से पड़ती है, उस क्षण जब हर device update का अपना shard लगाता है।

### Stage 2: gradients की भी partitioning

**`P_os+g`** stage 1 के ऊपर gradient partitioning जोड़ता है: हर device सिर्फ़ gradient का वही shard रखता है जो उसे अपने optimizer state और parameters के shard को update करने के लिए चाहिए, model के हर parameter का पूरा gradient रखने के बजाय। यह उसी विचार का स्वाभाविक विस्तार है, क्योंकि जो device optimizer state का सिर्फ़ `1/Nd` रखता है उसे उसे update करने के लिए gradient का भी सिर्फ़ `1/Nd` चाहिए। Rajbhandari et al. बताते हैं कि यह 8 गुना memory कमी तक पहुँचता है, फिर से **साधारण data parallelism जितनी ही communication मात्रा** पर: reduce-scatter और all-gather operations, जिनमें यह all-reduce को बदल देता है, कुल उतना ही data चलाते हैं जितना मानक all-reduce चलाता, बस वह उस device को भेजा जाता है जिसे हर shard असल में चाहिए, पूरी चीज़ सबको प्रसारित करने के बजाय।

### ये दोनों stages लगभग मुफ़्त का भोजन क्यों हैं

दोनों stages असली memory फ़ालतूपन हटाते हैं जबकि communication लागत में उससे कुछ नहीं जोड़ते जो data parallelism पहले से चुका रहा था। यह इसलिए संभव है कि optimizer state और gradients की ज़रूरत सिर्फ़ उस device को होती है जो parameters के संबंधित shard को update करने के लिए ज़िम्मेदार है; forward या backward pass में और किसी को उन्हें पढ़ने की ज़रूरत नहीं। Stage 3, जो parameters को ही partition करता है, यही दावा नहीं कर सकता, क्योंकि हर device के forward और backward pass को हर parameter चाहिए, सिर्फ़ वे नहीं जिनका वह मालिक है। पाठ 10 कवर करता है कि इसकी क्या क़ीमत है।

## अभ्यास

1. ▢ 7-अरब-parameter model को 8 data-parallel devices में ZeRO stage 1 (`P_os`) से train किया जाता है। अब हर device optimizer state के लिए प्रति parameter लगभग कितने bytes रखता है, उन 12 bytes प्रति parameter (fp32 parameters, momentum, variance) की तुलना में जो वह partitioning के बिना रखता?

<details markdown="1"><summary>संकेत</summary>

Stage 1 optimizer state को सभी `Nd` devices में बराबर बाँटता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

प्रति parameter 1.5 bytes (`12 / 8`), उन पूरे 12 bytes से घटकर जो हर device वरना रखता। fp16 parameters और fp16 gradients (कुल 4 bytes) अकेले stage 1 से अप्रभावित रहते हैं।

</details>

2. ▢ इनमें से कौन-सा सबसे अच्छा बताता है कि ZeRO stages 1 और 2 साधारण data parallelism से ज़्यादा communication मात्रा क्यों नहीं बढ़ाते?

    - a) वे gradient synchronization step को पूरी तरह छोड़ देते हैं
    - b) Optimizer state और gradients की ज़रूरत सिर्फ़ स्थानीय रूप से पड़ती है, संबंधित shard के लिए ज़िम्मेदार device को, इसलिए कौन क्या रखता है यह बदलने के लिए कुल मिलाकर ज़्यादा data चलाना नहीं पड़ता
    - c) वे सिर्फ़ छोटे models पर काम करते हैं जहाँ communication लागत मायने नहीं रखती
    - d) वे gradients को भेजने से पहले compress करते हैं, bandwidth के बदले accuracy का सौदा करते हुए

<details markdown="1"><summary>जाँचें</summary>

**b)** यही असली तंत्र है: किसी device को forward या backward pass के दौरान दूसरे device का optimizer state या gradients का shard नहीं चाहिए, सिर्फ़ अपने update step पर। (a) ग़लत है; synchronization अब भी होता है, बस reduce-scatter और all-gather में ढल जाता है। (c) और (d) ऐसे तंत्रों का वर्णन करते हैं जिन्हें ये दोनों stages इस्तेमाल नहीं करते।

</details>

3. ▢ एक team चाहती है कि ZeRO जितनी सबसे बड़ी memory कमी दे सके, साधारण data parallelism के मुक़ाबले communication मात्रा में बिना किसी बढ़ोतरी के। उन्हें कौन-सा stage इस्तेमाल करना चाहिए, और वह कितनी memory कमी देता है?

<details markdown="1"><summary>जाँचें</summary>

Stage 2 (`P_os+g`), साधारण data parallelism जितनी ही communication मात्रा पर 8 गुना memory कमी देता है। Stage 3 memory पर और आगे जाता है, पर वही है जिसके लिए Rajbhandari et al. communication-मात्रा की बढ़ोतरी बताते हैं।

</details>

## असली दुनिया का अभ्यास

- [ ] किसी training framework के ZeRO या FSDP configuration का दस्तावेज़ खोजें (PyTorch FSDP की sharding strategies, या DeepSpeed की ZeRO stage settings) और पहचानें कि कौन-सा configuration option stage 1 से मेल खाता है और कौन-सा stage 2 से।
- [ ] प्रति parameter 16 bytes के ब्योरे का इस्तेमाल करके 13-अरब-parameter model के लिए stage 2 में, 8 devices पर, model states की per-device memory निकालें, और उसकी तुलना उसी model से करें जिसमें ZeRO partitioning बिल्कुल नहीं है।
- [ ] कल: आगे देखे बिना, पाठ 10 के लिए एक वाक्य में अनुमान लिखें: अगर हर device के forward और backward pass को हर parameter चाहिए, सिर्फ़ वे नहीं जिनका वह मालिक है, तो parameters को ही partition करने वाले device को stages 1 और 2 के करने से अलग क्या करना होगा?

## आगे बढ़ने के लिए

- [पेपर: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
