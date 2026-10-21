---
title: "Serve Time पर Quantization"
description: "int8/int4/GPTQ/AWQ weight quantization, memory, speed और accuracy साथ-साथ क्यों नहीं चलते, और scheme चुनने का फ़ैसला-ढाँचा"
type: reference
---

# Serve Time पर Quantization

Serving के उपाय के रूप में weight quantization, [KV Cache शीट](kv-cache.md) की precision से स्वतंत्र। scheme चुनते या उसका बचाव करते समय खोजने के लिए बनाया गया।

## Schemes

| Scheme | Bit width | तंत्र | इस width पर accuracy |
|---|---|---|---|
| int8 | 8 | Round-to-nearest | सीधे-सादे रूप में आम तौर पर ठीक |
| int4, naive | 4 | Round-to-nearest | तेज़ी से बिगड़ती है: प्रति weight सिर्फ़ 16 representable values, जबकि int8 के पास 256 |
| GPTQ | 3-4 | एक बार में एक column quantize करता है; हर column के बाद उस layer के बचे, अभी quantize न हुए weights को भरपाई के लिए समायोजित करता है, दूसरे-क्रम की संवेदनशीलता की जानकारी से | बाद में, column-दर-column त्रुटि सुधारता है |
| AWQ | 3-4 | Calibration pass उन weight channels को ढूँढता है जिन पर सबसे बड़ी activation magnitudes पड़ती हैं; कुछ भी quantize करने से पहले उन channels को बचाने के लिए scale करता है | संभावित रूप से संवेदनशील weights को पहले से बचाता है |

GPTQ और AWQ का लक्ष्य एक ही नतीजा है, 4-bit weights पर सटीक model, उल्टे समय पर: GPTQ उस त्रुटि की भरपाई करता है जो आ चुकी है; AWQ उसे उन channels में रोकता है जिन्हें calibration संवेदनशील बताता है।

## Memory पूर्वानुमेय धुरी है; speed और accuracy नहीं

```text
memory ≈ fp16 footprint / (16 / bit_width)      # int8 halves it, int4 quarters it
```

**हल किया उदाहरण**, 14 GB का fp16 model: int8 लगभग 7 GB है, int4 लगभग 3.5 GB। यह अनुपात इससे स्वतंत्र टिकता है कि quantized weights किस scheme (naive, GPTQ, AWQ) ने बनाए, और उससे आगे bit width से भी स्वतंत्र।

Speed memory अनुपात का पीछा **नहीं** करती:

- Quantized weight को अक्सर matrix multiply चलने से ठीक पहले वापस ऊँची precision में **dequantize** करना पड़ता है, क्योंकि multiply करने वाला hardware वही precision उम्मीद करता है। अगर उस dequantization step में समय लगे, तो wall-clock speedup memory अनुपात से पीछे रह जाती है, जब तक serving stack का kernel सीधे quantized format पर न चले।
- Decode (memory-bandwidth bound) वहाँ छोटा weight footprint फल देता है: पढ़ने को कम, पढ़ने में कम समय। Prefill (compute-bound) अपना समय matmul पर ही खर्च करता है, weights बार-बार पढ़ने पर नहीं, इसलिए वही quantization prefill को बहुत कम speedup देती है, कभी-कभी लगभग कुछ नहीं।

Accuracy को नापी गई संख्या चाहिए, नमूना outputs से बनी धारणा नहीं: unquantized model के मुक़ाबले **perplexity** (model held-out text का कितना अच्छा अनुमान लगाता है; ऊँचा मतलब बदतर), या task-विशिष्ट benchmark score का फ़र्क़। धाराप्रवाह output इस बात का सबूत नहीं कि accuracy बची रही।

| कदम | Memory | Speed | Accuracy |
|---|---|---|---|
| fp16 से int8 | आधी | Memory का ठीक-ठाक पीछा करती है | छोटी, आम तौर पर सहने लायक़ क़ीमत |
| int8 से int4 | फिर आधी | Dequant overhead और kernel support पर निर्भर | int8 वाले कदम से अनुपात से ज़्यादा बढ़ती है, इसीलिए GPTQ/AWQ मौजूद हैं |

तीनों धुरियों में से कोई दूसरों के साथ साथ-साथ नहीं बदलती, इसीलिए बचाव करने लायक़ चुनाव को हर एक के लिए संख्या चाहिए।

<a id="picking-a-scheme-name-the-binding-constraint-first"></a>

## Scheme चुनना: पहले बाँधने वाली बाधा का नाम लें

Quantization उस बाधा का इलाज है जिसे fp16 पूरा नहीं कर पाता, कोई default कदम नहीं। अगर fp16 पहले से memory budget में समाता है और latency budget पूरा करता है, तो quantize करना असली accuracy की क़ीमत पर कुछ ऐसा ख़रीदता है जो चाहिए नहीं।

| बाँधने वाली बाधा | क्या करें |
|---|---|
| Memory: weights और ज़रूरी KV cache की [capacity सीमा](kv-cache.md#capacity-budget) साथ नहीं समाते | उतना ही quantize करें जितने में समा जाए: पहले int8 (सबसे सस्ती accuracy की क़ीमत), GPTQ या AWQ के साथ int4 तभी जब अकेला int8 अब भी जगह न छोड़े |
| Latency: model समाता है, पर decode budget चूकता है | int8 या int4 मदद कर सकता है, क्योंकि decode memory-bandwidth bound है, पर speedup bit width से मान लेने के बजाय असल में नापें |
| Accuracy: benchmark या perplexity की ऐसी सीमा जिसे पार नहीं किया जा सकता | Quantization को ख़ारिज नहीं करता, पर अकेले memory या speed से scheme चुनने को ख़ारिज करता है: इसी ख़ास model के लिए GPTQ बनाम AWQ नापें, क्योंकि वे model-दर-model अलग ढंग से टिकते हैं |

**हल किया उदाहरण**: एक model के fp16 weights 80 GB GPU पर 70 GB लेते हैं, cache और overhead के लिए 10 GB बचते हैं, जो अर्थपूर्ण concurrency के लिए बहुत कम है। यह memory की बाधा है। int8 में quantize करने से weights घटकर ~35 GB हो जाते हैं, ~45 GB cache के लिए मुक्त होते हैं, जो [capacity सीमा](kv-cache.md#capacity-budget) को काफ़ी बढ़ा देता है। अगर अकेला int8 पहले से capacity और latency दोनों लक्ष्य पूरे करता है, तो और नीचे int4 पर जाना ऐसी memory ख़रीदता है जो किसी को चाहिए नहीं, असली, नापी गई accuracy की क़ीमत पर: बाँधने वाली बाधा से आगे quantize करना वही ग़लती है जो तब quantize करना है जब fp16 पहले से समा रहा था।

<a id="defending-the-choice-means-citing-three-numbers"></a>

## चुनाव का बचाव तीन संख्याएँ गिनाने से होता है

1. **Memory का आँकड़ा** जिसने quantization को ज़रूरी बनाया, या वह जो दिखाता है कि वह ज़रूरी नहीं था।
2. **Accuracy की संख्या** जो चुनी गई scheme के लिए चुनी गई bit width पर नापी गई: unquantized model के मुक़ाबले perplexity का फ़र्क़ या benchmark score का बदलाव।
3. **Speed की संख्या** जो budget जिस चरण को कवर करता है उसके लिए असल में नापी गई (ज़्यादातर latency-बाधित मामलों में decode), क्योंकि wall-clock फ़ायदा अपने आप memory अनुपात का पीछा नहीं करता।

इनमें से सिर्फ़ एक से बचाव किया गया चुनाव ("AWQ के साथ int4 सबसे अच्छी memory बचत देता है") बचाव में नहीं है: वह बाक़ी दो धुरियों को, और इसे भी कि उतनी bit width की ज़रूरत भी थी या नहीं, अनजाँचा छोड़ देता है।

## संबंधित

- [पाठ 7](../lessons/0007-quantization-schemes.md), [पाठ 8](../lessons/0008-accuracy-speed-memory-tradeoffs.md), [पाठ 9](../lessons/0009-picking-a-quantization-scheme.md)
- [KV Cache शीट](kv-cache.md): वह capacity सीमा जिसके विरुद्ध memory-बाधित quantization का फ़ैसला नापा जाता है
