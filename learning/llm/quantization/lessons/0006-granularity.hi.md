---
title: "6. Granularity"
description: "Per-tensor, per-channel और per-group scales, और हर एक store किए गए bits में क्या क़ीमत लेता है"
type: lesson
---

# पाठ 6. Granularity

**मिशन से संबंध:** Quantized tensor की error का अनुमान लगाने का मतलब यह भी जानना है कि हर scale को कितनी values साझा करती हैं, क्योंकि scale अपने हिस्से की सबसे बड़ी value से तय होता है और हर अतिरिक्त scale store किए गए bits में क़ीमत लेता है।
**मुख्य स्रोत:** [पेपर: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295), sections 2.2.3 और 2.4.2
**पूर्व-आवश्यकताएँ:** [पाठ 5](0005-choosing-the-range.md), [Granularity](../GLOSSARY.md), [Group size](../GLOSSARY.md), [Effective bits per weight](../GLOSSARY.md)

## वार्म-अप

1. ▢ Min-max range तय करने पर quantizer का scale किससे तय होता है, और एक outlier उसके साथ क्या करता है?

<details markdown="1"><summary>जाँचें</summary>

Range से, जो सबसे बड़ी और सबसे छोटी values से तय होती है, steps की संख्या से भाग देकर। एक outlier range चौड़ी कर देता है, इसलिए scale बढ़ता है और हर दूसरी value के लिए step मोटा हो जाता है, जिससे उनमें से ज़्यादातर zero पर round हो सकती हैं (पाठ 5)।

</details>

2. ▢ एक 4-bit scheme हर 32 weights के group के लिए एक 16-bit scale store करती है। उसके effective bits per weight क्या हैं?

<details markdown="1"><summary>जाँचें</summary>

4.5। Scale हर value के 4 bits में प्रति weight 16 / 32 = 0.5 bits जोड़ता है (पाठ 1)।

</details>

3. ▢ Symmetric grid को सिर्फ़ scale क्यों चाहिए, और zero point छोड़ने की क्या क़ीमत है?

<details markdown="1"><summary>जाँचें</summary>

Symmetric quantization zero point को zero पर तय कर देता है, इसलिए और कुछ store करने को नहीं बचता। क़ीमत यह है कि grid zero पर केंद्रित होती है, इसलिए एक तरफ़ा tensor ख़ाली तरफ़ के levels बर्बाद करता है (पाठ 4)।

</details>

## यह जानें

### Scale कौन साझा करता है

**Granularity** यह है कि कितनी values एक scale और zero point साझा करती हैं। Scale साझा करने वाला छोटा सेट मतलब छोटी range, इसलिए outlier सिर्फ़ उसी सेट को बिगाड़ता है जिसमें वह बैठा है। क़ीमत यह है कि हर सेट को अपना store किया हुआ scale चाहिए।

```text
W: output channels (rows) x input features (columns)

per-tensor    one scale for the whole matrix
per-channel   one scale per row (per output channel of a weight matrix)
per-group     one scale per `group size` consecutive values within a row, such as 64 or 128
per-token     one scale per row of an activation matrix X (tokens x features)
```

Nagel et al. ध्यान दिलाते हैं कि per-tensor quantization मानक है क्योंकि हर fixed-point accelerator उसे support करता है, और weights का per-channel quantization तब सबसे ज़्यादा मदद करता है जब weight distribution एक channel से दूसरे में बहुत बदलता हो। वे weights या activations के हर group पर quantizer लगाने का भी वर्णन करते हैं, और कहते हैं कि बारीक groups आम तौर पर अतिरिक्त overhead की क़ीमत पर accuracy सुधारते हैं।

### Weights के लिए per-channel क्यों चलता है और activations के लिए क्यों नहीं

Linear layer हर output को input features पर योग के रूप में compute करती है। Quantized values को scale गुणा integer लिखने पर, scales योग से बाहर तभी निकल सकते हैं जब वे पूरे योग में constant हों:

```text
y[i] = sum over k of (s_w[i] * W_int[i,k]) * (s_x * x_int[k])
     = s_w[i] * s_x * (sum over k of W_int[i,k] * x_int[k])
```

Bracket शुद्ध integer dot product है, जिसे hardware तेज़ करता है, और दोनों scales अंत में नतीजे को एक बार गुणा करते हैं। Per-output-channel weight scale `s_w[i]` योग पर constant है, क्योंकि `i` output का नाम है और `k` पर योग होता है। Nagel et al. निष्कर्ष निकालते हैं कि per-channel weight quantization को अलग per-channel scale के साथ लागू किया जा सकता है, accumulator को दोबारा scale किए बिना।

Per-input-channel activation scale `s_x[k]` होगा, जो योग वाले index के साथ बदलता है। वह योग से बाहर नहीं निकल सकता, और Nagel et al. कहते हैं कि वह "इसलिए हर input channel के लिए accumulator को दोबारा scale करने की माँग करेगा"। इसी वजह से per-channel activation quantization को लागू करना कहीं ज़्यादा कठिन है। Per-token activation scale, यानी `X` की हर row के लिए एक, किसी दिए token के लिए योग पर constant है और उसकी कोई क़ीमत नहीं: [Dettmers et al.](https://arxiv.org/abs/2208.07339) अपने vector-wise quantization में ठीक यही इस्तेमाल करते हैं, activations की हर row के लिए एक constant और weights के हर column के लिए एक, और दोनों को constants के outer product से वापस हटा देते हैं। पाठ 7 दिखाता है कि LLMs के लिए यह काफ़ी क्यों नहीं है: outliers feature dimensions में बैठे हैं, जो वह axis है जिसे per-token scale अलग नहीं करता।

Per-group quantization में integer accumulator के लिए वही समस्या है, क्योंकि scale योग के भीतर बदलता है। पेपर में accumulator की यही सीमा है जिसकी वजह से Nagel et al. group scales को छोड़ देते हैं। Weight-only schemes में, weights kernel के भीतर 16-bit में dequantize होते हैं और 16-bit में गुणा किए जाते हैं (देखें [weight-only quantization](../GLOSSARY.md)), इसलिए कोई integer accumulator मिश्रित scales नहीं ढोता और group scale बदलने के लिए आज़ाद है।

### Scales की क़ीमत

हर group अपना scale, और कोई zero point, checkpoint में जोड़ता है। **Effective bits per weight** value की bit width और group में बाँटा गया metadata है:

```text
effective bits = b + (scale bits + zero point bits) / group size
```

| Group size | 16-bit scale के साथ overhead | 4-bit weights के लिए effective bits |
|---|---|---|
| 1024 | 0.0156 | 4.0156 |
| 256 | 0.0625 | 4.0625 |
| 128 | 0.125 | 4.125 |
| 64 | 0.25 | 4.25 |
| 32 | 0.5 | 4.5 |

Per-channel बस ऐसा group है जिसका आकार row की लंबाई है, और per-tensor हर weight का group है: दोनों की लागत लगभग कुछ नहीं। Group 32 के लिए पाठ 1 वाली संख्या आख़िरी पंक्ति है।

### छोटे groups क्या देते हैं

अभ्यास का experiment एक synthetic weight matrix को 4 bits पर quantize करता है, जिसकी rows के scales अलग हैं और पूँछें भारी। Groups सिकुड़ने के साथ error लगातार घटती है, और per-tensor सबसे ख़राब है, बहुत अंतर से। 64 का एक group outlier शामिल करने के लिए सिर्फ़ 64 मौक़े रखता है, और outlier सिर्फ़ उन्हीं 64 values को प्रभावित करता है।

इस पर सबसे बड़ा अनुभवजन्य अध्ययन [Dettmers और Zettlemoyer](https://arxiv.org/abs/2212.09720) का है: 19M से 176B parameters तक के LLMs पर 3 से 8 bits के 35,000 से ज़्यादा zero-shot experiments। उन्हें bits में model के आकार और accuracy के बीच का सौदा सुधारना ही कठिन लगता है, और सिर्फ़ दो चीज़ें मदद करती हैं: छोटा block size (group size के लिए उनका शब्द) और data type। 4-bit Pythia models के लिए, block size 1024 से 64 करने पर प्रति parameter 0.24 bits जुड़ते हैं और zero-shot accuracy लगभग उतनी ही सुधरती है जितनी 4 से 5 bits पर जाने से। हर block पर 16-bit constant की क़ीमत 16 / 64 - 16 / 1024 = 0.23 bits है, जो पेपर की संख्या के क़रीब है। छोटे groups सस्ते bits हैं।

## अभ्यास

1. ▢ एक 4-bit scheme हर 64 weights के group पर एक 16-bit scale और एक 4-bit zero point store करती है। उसके effective bits per weight क्या हैं?

<details markdown="1"><summary>जाँचें</summary>

4 + (16 + 4) / 64 = 4.3125, लगभग 4.31। Zero point scale के 0.25 के ऊपर 4 / 64 = 0.0625 जोड़ता है। Symmetric scheme वह 0.0625 हटा देती और 4.25 पर आती।

</details>

2. ▢ क्या बात per-output-channel weight scale को integer matrix multiplication के साथ संगत बनाती है जबकि per-input-channel activation scale को नहीं?

    - a) Weight scale सिर्फ़ आठ bits में समा जाता है
    - b) Weight scale को अलग offset term चाहिए
    - c) Weight scale योग में constant है
    - d) Weight scale की value output channels के बीच बदलती है

<details markdown="1"><summary>जाँचें</summary>

**c)** Output `i` का scale `k` पर पूरे योग को गुणा करता है, इसलिए वह योग से बाहर निकल जाता है और integer accumulation के बाद एक बार लगाया जाता है। Input channel से indexed activation scale योग के भीतर बदलता है, इसलिए accumulator को हर input channel पर दोबारा scale करना पड़ेगा। (a) storage के बारे में है और यह तय नहीं करता कि scale कहाँ लगाया जा सकता है। (b) scale को zero point से उलझाता है, और symmetric weights को वह चाहिए ही नहीं। (d) सच है पर यह कई scales होने का कारण है, उन्हें बाहर निकाल पाने का नहीं।

</details>

3. ▢ पहले अनुमान लगाएँ, फिर चलाएँ। चलाने से पहले per-tensor, per-channel और group sizes को error के हिसाब से सबसे ख़राब से सबसे अच्छे तक क्रम में रखें, और बताएँ कि क्या error लगातार घटती है। फिर group 32 के effective bits निकालें।

    ```python
    import numpy as np

    rng = np.random.default_rng(0)
    rows, cols, b = 256, 1024, 4
    qmax = 2 ** (b - 1) - 1
    row_scale = rng.lognormal(0.0, 0.7, size=(rows, 1)) * 0.02
    W = rng.standard_t(df=4, size=(rows, cols)) * row_scale


    def quantize(W, group):
        """Symmetric absmax, one scale per `group` consecutive values in a row.
        group=None means one scale for the whole tensor."""
        G = W.reshape(1, -1) if group is None else W.reshape(-1, group)
        s = np.abs(G).max(axis=1, keepdims=True) / qmax
        Q = s * np.clip(np.round(G / s), -qmax, qmax)
        return Q.reshape(W.shape)


    print("granularity    rel. error   effective bits (16-bit scales)")
    for name, group in [("per-tensor", None), ("per-channel", cols), ("group 256", 256),
                        ("group 128", 128), ("group 64", 64), ("group 32", 32)]:
        err = np.mean((quantize(W, group) - W) ** 2) / np.mean(W ** 2)
        n_scales = 1 if group is None else W.size // group
        print(f"{name:13s}  {err:.4f}       {b + 16 * n_scales / W.size:.3f}")
    ```

<details markdown="1"><summary>संकेत</summary>

Group size में हर कमी का मतलब ज़्यादा scales है, और हर scale values के छोटे सेट से तय होता है। फिर पूछें कि per-tensor scale उस matrix के साथ क्या करता है जिसकी rows आकार में अलग हैं।

</details>

<details markdown="1"><summary>जाँचें</summary>

```text
granularity    rel. error   effective bits (16-bit scales)
per-tensor     0.7047       4.000
per-channel    0.1291       4.016
group 256      0.0599       4.062
group 128      0.0395       4.125
group 64       0.0267       4.250
group 32       0.0179       4.500
```

हर क़दम पर error घटती है: per-tensor signal की अपनी ऊर्जा के लगभग 70 प्रतिशत जितनी error छोड़ता है, per-channel हर row को अपना scale देकर उसका ज़्यादातर हिस्सा हटा देता है, और group का हर आधा होना error को लगभग एक तिहाई घटा देता है। Group 32 की लागत 4.5 effective bits है। Data synthetic है, इसलिए क्रम और मोटे अनुपात पढ़ें, पूर्ण संख्याएँ नहीं।

</details>

4. ▢ Group size 1024 से 64 पर जाने पर 16-bit scale के साथ प्रति weight कितने bits जुड़ते हैं? उसकी तुलना weights को 4 से 5 bits पर ले जाने की क़ीमत से करें, और बताएँ कि Dettmers और Zettlemoyer ने फ़ायदों के बारे में क्या पाया।

<details markdown="1"><summary>जाँचें</summary>

16 / 64 - 16 / 1024 = 0.234 bits, जबकि 5-bit weights के लिए पूरा 1 bit। पेपर में, छोटे block size ने 4-bit Pythia models की zero-shot accuracy लगभग उतनी ही सुधारी जितनी अतिरिक्त bit सुधारता। इसलिए group छोटा करना accuracy ख़रीदने का हर weight में एक bit जोड़ने से कहीं सस्ता तरीक़ा है। पेपर का मुख्य नतीजा यह है कि model के कुल bits और zero-shot accuracy के लिए 4 bits लगभग हर जगह इष्टतम है।

</details>

5. ▢ कोई team activations को हर token के एक scale के साथ 8 bits पर quantize करती है और फिर भी accuracy खोती है, क्योंकि एक feature dimension हर token पर बहुत बड़ी है। Per-token scale मदद क्यों नहीं करता, और कौन-सा axis outlier को अलग करता?

<details markdown="1"><summary>जाँचें</summary>

हर token का scale उस token की सबसे बड़ी value से तय होता है, और बहुत बड़ी feature dimension लगभग हर token पर सबसे बड़ी है, इसलिए हर row का scale एक ही तरह फूल जाता है। Dettmers et al. यही बात कहते हैं: row-wise और vector-wise quantization sequence dimension को scale करते हैं, और outliers feature dimension में बैठे हैं, इसलिए दोनों उन्हें अलग करने में विफल रहते हैं। सिर्फ़ per-feature-dimension scale outlier को अलग करता, और वह इस पाठ का per-input-channel activation scale है, जिसे integer matrix multiplication सस्ते में लागू नहीं कर सकता।

</details>

## असली दुनिया का अभ्यास

- [ ] Experiment में `rng.lognormal(0.0, 0.7, ...)` के `0.7` को `0.0` कर दें, ताकि हर row का scale एक ही हो, और दोबारा चलाएँ। दर्ज करें कि per-tensor के मुक़ाबले per-channel का कितना फ़ायदा बचा रहता है, और उसे समझाएँ।
- [ ] Hugging Face Hub पर किसी भी 4-bit GPTQ या AWQ checkpoint का model card या config खोलें, उसका group size खोजें, और model के parameters की संख्या के लिए उसके effective bits per weight और checkpoint का आकार निकालें।
- [ ] कल: बिना नोट्स के 16-bit scale और 8-bit scale के लिए group sizes बनाम effective bits की table दोबारा बनाएँ, और एक वाक्य में बताएँ कि per-channel weight scales integer matmul में क्यों बैठते हैं और per-channel activation scales क्यों नहीं।

## आगे बढ़ने के लिए

- [Quantization Mapping शीट](../reference/quantization-mapping.md)
- [पेपर: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295)
- [पेपर: "The case for 4-bit precision: k-bit Inference Scaling Laws", Dettmers and Zettlemoyer, 2022](https://arxiv.org/abs/2212.09720)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
