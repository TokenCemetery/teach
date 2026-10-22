---
title: "2. Floating-Point Formats"
description: "fp32, fp16 और bf16 में sign, exponent और mantissa bits range और precision को कैसे बाँटते हैं"
type: lesson
---

# पाठ 2. Floating-Point Formats

**मिशन से संबंध:** इस track का हर आगे का number format इस बात का चुनाव है कि कुछ bits को range और precision के बीच कैसे बाँटा जाए, इसलिए quantized model ने क्या खोया यह परखने से पहले आपको bit layout पढ़ना और यह बताना आना चाहिए कि वह क्या रख सकता है और क्या नहीं।
**मुख्य स्रोत:** [पेपर: "A Study of BFLOAT16 for Deep Learning Training", Kalamkar et al., 2019](https://arxiv.org/abs/1905.12322)
**पूर्व-आवश्यकताएँ:** [पाठ 1](0001-what-quantization-buys.md), [Exponent bits](../GLOSSARY.md), [Mantissa bits](../GLOSSARY.md)

## वार्म-अप

1. ▢ fp32, bf16 और int8 प्रति parameter कितने bytes लेते हैं, और 7B-parameter model के weights हर एक में कितनी memory लेते हैं?

<details markdown="1"><summary>जाँचें</summary>

fp32 में 4 bytes (28 GB), bf16 में 2 bytes (14 GB) और int8 में 1 byte (7 GB)। यह सिर्फ़ weights हैं, नाममात्र की bit width पर।

</details>

2. ▢ छोटा weight format आम तौर पर batch-1 decoding को तेज़ क्यों कर देता है?

<details markdown="1"><summary>जाँचें</summary>

Batch size 1 पर decoding memory-bound है: हर token पर हर weight एक बार पढ़ा जाता है और थोड़े-से arithmetic में काम आता है, इसलिए प्रति weight कम bytes का मतलब पढ़ने को कम। Weight-only quantization arithmetic को ख़ुद तेज़ नहीं करता।

</details>

## यह जानें

### तीन fields

Floating-point संख्या एक sign bit, कुछ **exponent bits** और कुछ **mantissa bits** store करती है। किसी normal value के लिए exponent field `e` और mantissa field `m` यह देते हैं

```text
value = (-1)^sign × 2^(e - bias) × (1 + m / 2^M)
```

जहाँ `M` mantissa bits की संख्या है और `bias` एक तय offset है जो exponent को ऋणात्मक होने देता है। Exponent चुनता है कि value दो की किस घात के पास बैठती है। Mantissa उस घात और अगली घात के बीच बराबर दूरी पर रखे 2^M बिंदुओं में से एक चुनता है। सब zeros वाला exponent field zero और subnormal values के लिए आरक्षित है, जो सबसे छोटी normal value से भी छोटी होती हैं और उसी दूरी के साथ zero तक का फ़ासला भरती हैं। सब ones वाला exponent field IEEE formats में infinity और NaN के लिए आरक्षित है।

| Format | कुल bits | Sign / exponent / mantissa | Bias | सबसे बड़ी finite value | सबसे छोटी normal value | Machine epsilon |
|---|---|---|---|---|---|---|
| fp32 | 32 | 1 / 8 / 23 | 127 | 3.4 × 10^38 | 1.2 × 10^-38 | 2^-23, लगभग 1.2 × 10^-7 |
| fp16 | 16 | 1 / 5 / 10 | 15 | 65,504 | 6.1 × 10^-5 | 2^-10, लगभग 9.8 × 10^-4 |
| bf16 | 16 | 1 / 8 / 7 | 127 | 3.4 × 10^38 | 1.2 × 10^-38 | 2^-7, लगभग 7.8 × 10^-3 |

65,504 वही संख्या है जिसे Micikevicius et al. fp16 की सबसे बड़ी represent होने वाली value बताते हैं ([Micikevicius et al., 2017](https://arxiv.org/abs/1710.03740))। बाक़ी layouts से निकलता है। **Machine epsilon** 1 और उसके ऊपर की अगली value के बीच का फ़ासला है, जो 2^-M है।

इस track के बाक़ी हिस्से के लिए दो नतीजे मायने रखते हैं। पहला, fp16 और bf16 दोनों 2 bytes लेते हैं, इसलिए इनमें से चुनने से memory पर कोई फ़र्क़ नहीं पड़ता। यह तीन और mantissa bits और तीन और exponent bits के बीच का चुनाव है। दूसरा, bf16 वह fp32 है जिसके नीचे के 16 bits हटा दिए गए हों: वही sign और exponent fields और ऊपर के 7 mantissa bits। Kalamkar et al. इसी को bf16 के आकर्षक होने की वजह बताते हैं: उसकी range fp32 जैसी ही है और fp32 से और fp32 में बदलना आसान है।

### Range और precision अलग चीज़ें हैं

Exponent **range** तय करता है, यानी सबसे छोटी से सबसे बड़ी value तक का फ़ासला। Mantissa **precision** तय करता है, यानी format उस फ़ासले के भीतर किसी value का कितने क़रीब तक अनुमान लगा सकता है। ये दोनों स्वतंत्र हैं, और एक में जोड़ा गया हर bit दूसरे से लिया गया bit है।

दूरी स्थिर नहीं होती। 2^k और 2^(k+1) के बीच पड़ोसी values 2^(k-M) की दूरी पर होती हैं, इसलिए हर घात पर फ़ासला दुगुना होता है जबकि सापेक्ष फ़ासला लगभग 2^-M रहता है। fp16 में, 1 के ठीक ऊपर की values लगभग 0.001 की दूरी पर हैं, 1024 के ठीक ऊपर की values ठीक 1 की दूरी पर, और 2048 के ठीक ऊपर 2 की दूरी पर। इससे दो बातें निकलती हैं। जिस जोड़ का नतीजा किसी मौजूदा value के बजाय मध्य बिंदु के ज़्यादा क़रीब गिरता है वह वापस rounded हो जाता है, इसलिए fp16 में `1 + 0.0004` अब भी 1 है, और fp16 में एक-एक जोड़ने वाला चालू योग 2048 पर बढ़ना बंद कर देता है। और rounded value ज़्यादा से ज़्यादा स्थानीय दूरी के आधे से ग़लत होती है, यही वह **rounding error** है जो quantization हमेशा जोड़ता है।

### fp16 को loss scaling क्यों चाहिए थी और bf16 को क्यों नहीं

fp16 के 5 exponent bits उसे संकरा बनाते हैं। उसमें store हो सकने वाली सबसे छोटी धनात्मक value 2^-24 है, और उससे छोटी हर चीज़ zero हो जाती है। Micikevicius et al. ने एक training run से gradient values मापीं और पाया कि लगभग 5% weight gradient values के exponents -24 से नीचे थे, जो खो जाते। उनका हल है **loss scaling**: backpropagation से पहले loss को किसी constant से गुणा करें, ताकि हर gradient ऊपर scale होकर fp16 की range में आ जाए, और weight update से पहले उस scale से भाग दे दें। वे factor को इस तरह चुनते हैं कि उसका सबसे बड़े absolute gradient से गुणनफल 65,504 से नीचे रहे, क्योंकि overflow से infinities और NaNs बनते हैं जो weights को नुक़सान पहुँचाते हैं।

bf16 में fp32 जैसे ही 8 exponent bits हैं, इसलिए वही gradients represent हो सकते हैं। Kalamkar et al. कहते हैं कि fp32 की range रखने का मतलब है कि convergence के लिए किसी hyper-parameter tuning की ज़रूरत नहीं पड़ती, जबकि fp16 को पड़ती है। उनका emulation fp32 value के निचले 16 bits को zero कर देता है, और वे बदलते समय round-to-nearest की तुलना सीधे truncation से करते हैं। उनके एक experiment में round-to-nearest fp32 baseline की accuracy के बराबर रहा जबकि truncation में लगभग 0.02% का नुक़सान हुआ। bf16 की क़ीमत 7-bit mantissa है: values सापेक्ष रूप से सिर्फ़ लगभग 0.8% की दूरी पर हैं।

इस track के लिए सबक़ यह सौदा ख़ुद है। 8 bits और उससे नीचे के quantized formats यही सौदा कहीं ज़्यादा कठिन बना देते हैं, इसीलिए पाठ 4 एक scale जोड़ता है।

## अभ्यास

1. ▢ कौन-सा कथन fp16 और bf16 की सही तुलना करता है?

    - a) fp16 में ज़्यादा exponent bits हैं, इसलिए ज़्यादा चौड़ी range
    - b) bf16 में ज़्यादा exponent bits हैं, इसलिए ज़्यादा चौड़ी range
    - c) bf16 में ज़्यादा mantissa bits हैं, इसलिए ज़्यादा बारीक दूरी
    - d) fp16 और bf16 के कुल bits की संख्या अलग है

<details markdown="1"><summary>जाँचें</summary>

**b)** bf16 exponent पर 8 bits लगाता है जबकि fp16 5, जिससे उसे fp32 की range मिलती है, और उसके पास 7 mantissa bits हैं जबकि fp16 के पास 10। (a) में दोनों formats उलट दिए गए हैं। (c) उन्हें दूसरी तरह उलट देता है: बारीक दूरी fp16 की है। (d) ग़लत है क्योंकि दोनों 16 bits के हैं, इसलिए memory उन्हें अलग नहीं करती।

</details>

2. ▢ पहले अनुमान लगाएँ, फिर चलाएँ। हर line क्या print करती है?

    ```python
    import numpy as np

    with np.errstate(over="ignore"):
        print(float(np.float16(65504)), float(np.float16(65519)))
        print(float(np.float16(65520)), float(np.float16(70000)))
    ```

<details markdown="1"><summary>संकेत</summary>

65,504 fp16 की सबसे बड़ी finite value है, और उसके बाद की value 65,536 होती। मध्य बिंदु कहाँ है, और उसके ऊपर की संख्या किस ओर round होती है?

</details>

<details markdown="1"><summary>जाँचें</summary>

```text
65504.0 65504.0
inf inf
```

65,519, 65,504 और 65,536 के मध्य बिंदु से नीचे है, इसलिए वह नीचे 65,504 पर round होती है। 65,520 से ऊपर value सबसे बड़ी finite संख्या से आगे round होकर infinity बन जाती है, और training में gradient overflow ऐसे ही शुरू होता है। `errstate` वाली line बस उस पर NumPy की चेतावनी को चुप कराती है।

</details>

3. ▢ पहले अनुमान लगाएँ, फिर चलाएँ। तीन योगों में से कौन-से ठीक 1 के बराबर हैं?

    ```python
    import numpy as np

    one = np.float16(1)
    for d in (0.0004, 0.0005, 0.001):
        print(d, float(one + np.float16(d)))
    ```

<details markdown="1"><summary>संकेत</summary>

fp16 में 1 के ऊपर का फ़ासला 2^-10 है, लगभग 0.000977। योग उस पड़ोसी के पास चला जाता है जो ज़्यादा नज़दीक हो।

</details>

<details markdown="1"><summary>जाँचें</summary>

```text
0.0004 1.0
0.0005 1.0009765625
0.001 1.0009765625
```

सिर्फ़ पहला। 1 के पड़ोसी 1 और 1.0009765625 हैं, और मध्य बिंदु लगभग 1.000488 है। 0.0004 उसके नीचे गिरता है और पूरी तरह खो जाता है, जबकि 0.0005 पूरा 2^-10 ऊपर कूद जाता है। किसी बड़ी value में जोड़ी गई value "थोड़ी-सी ग़लत" नहीं होती: स्थानीय दूरी के आधे से नीचे वह ग़ायब हो जाती है।

</details>

4. ▢ पहले अनुमान लगाएँ, फिर चलाएँ। यह क्या print करता है, और यह fp16 में कई छोटी संख्याएँ जोड़ने के बारे में क्या बताता है?

    ```python
    import numpy as np

    total = np.float16(0)
    for _ in range(3000):
        total = total + np.float16(1)
    print(float(total))
    ```

<details markdown="1"><summary>संकेत</summary>

2048 से ऊपर fp16 की दूरी 2 है। 2048 + 1 का क्या होता है?

</details>

<details markdown="1"><summary>जाँचें</summary>

```text
2048.0
```

2048 पर दूरी 2 है, इसलिए 2049 दो represent होने वाली values के ठीक बीच में बैठता है और even वाली, 2048, की ओर round होता है। इसके बाद योग बाक़ी 952 जोड़ों के दौरान वहीं टिका रहता है। इसीलिए Micikevicius et al. fp16 products को fp16 में नहीं बल्कि fp32 में accumulate करते हैं।

</details>

5. ▢ पहले अनुमान लगाएँ, फिर चलाएँ। bf16 वह fp32 है जिसके निचले 16 bits हटा दिए गए हों। चलाने से पहले बताएँ कि पहली तीन values में से कौन-सी cast के बाद अपरिवर्तित बचती हैं, और fp16 में 1e38 का क्या होता है।

    ```python
    import numpy as np

    def to_bf16(x):
        bits = np.asarray(x, dtype=np.float32).view(np.uint32) & np.uint32(0xFFFF0000)
        return bits.view(np.float32)

    x = np.array([1 + 2**-7, 1 + 2**-8, 3.14159265, 1e38], dtype=np.float32)
    print([float(v) for v in to_bf16(x)])
    with np.errstate(over="ignore"):
        print(float(np.float16(1e38)))
    ```

<details markdown="1"><summary>संकेत</summary>

bf16 7 mantissa bits रखता है, इसलिए 1 + 2^-7 वह पहली value है जो 1 के ऊपर वह रख सकता है। 1 + 2^-8 क्या है?

</details>

<details markdown="1"><summary>जाँचें</summary>

```text
[1.0078125, 1.0, 3.140625, 9.969209968386869e+37]
inf
```

1 + 2^-7 बचता है, 1 + 2^-8 truncate होकर ठीक 1 हो जाता है, और pi 3.140625 बन जाता है, जो लगभग तीन अंकों तक सही है। 1e38 finite रहता है, mantissa कट जाने से लगभग 9.97e37, पर fp16 उसे infinity बना देता है। यह function truncate करता है, जैसा Kalamkar et al. अपने emulation में बताते हैं, जिसकी तुलना वे nearest तक rounding से करते हैं।

</details>

6. ▢ कोई साथी fp16 में train करता है और कुछ सौ steps के बाद loss को NaN होते देखता है, फिर bf16 पर जाने का सुझाव देता है। समझाएँ कि संभवतः क्या हो रहा है, loss scaling उसके बारे में क्या करती है, और bf16 क्या बदलेगा।

<details markdown="1"><summary>जाँचें</summary>

fp16 की सीमा 65,504 है, इसलिए scale किया हुआ loss या कोई बड़ा gradient infinity और NaN में overflow हो सकता है, और 2^-24 से छोटे gradients zero बन जाते हैं। Loss scaling एक constant चुनती है ताकि gradients fp16 की range के भीतर आ जाएँ, और weight update से पहले scale को भाग देकर हटा दिया जाता है। bf16 में fp32 की exponent range है, इसलिए दोनों में से कोई समस्या नहीं आती और किसी scale की ज़रूरत नहीं पड़ती, बदले में mantissa मोटा हो जाता है। बदलना तभी सही हल है जब NaN सचमुच range की समस्या हो। ख़राब learning rate या ख़राब batch से आया NaN बदलने के बाद भी बना रहता है।

</details>

## असली दुनिया का अभ्यास

- [ ] NumPy वाले Python session में `np.finfo(np.float16)` और `np.finfo(np.float32)` print करें और उनमें `max`, `tiny` और `eps` खोजें। हर एक को ऊपर की table से मिलाएँ।
- [ ] Hugging Face Hub पर किसी भी open model का `config.json` खोलें और उसका `torch_dtype` पढ़ें। बताएँ कि वह चुनाव कौन-सी range और दूरी का संकेत देता है।
- [ ] कल: बिना नोट्स के fp32, fp16 और bf16 के sign, exponent और mantissa bits की संख्या लिखें, और बताएँ कि तीनों में किसकी range सबसे चौड़ी है और किसकी दूरी सबसे बारीक।

## आगे बढ़ने के लिए

- [Number Formats शीट](../reference/number-formats.md)
- [पेपर: "A Study of BFLOAT16 for Deep Learning Training", Kalamkar et al., 2019](https://arxiv.org/abs/1905.12322)
- [पेपर: "Mixed Precision Training", Micikevicius et al., 2017](https://arxiv.org/abs/1710.03740), weights की master copy और loss scaling के लिए sections 3.1 और 3.2
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
