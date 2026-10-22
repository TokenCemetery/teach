---
title: "5. Range चुनना"
description: "Range को clip करने से थोड़ी clipping error के बदले rounding error बहुत कम क्यों हो जाती है"
type: lesson
---

# पाठ 5. Range चुनना

**मिशन से संबंध:** Quantization error कहाँ से आती है यह अनुमान लगाने का मतलब है जानना कि दी गई clipping range उसके दोनों हिस्सों में से किसे बड़ा करती है, और range वही चुनाव है जो एक को दूसरे में बदल देता है।
**मुख्य स्रोत:** [पेपर: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295), section 3.1
**पूर्व-आवश्यकताएँ:** [पाठ 4](0004-quantize-and-dequantize.md), [Clipping range](../GLOSSARY.md), [Clipping error](../GLOSSARY.md), [Rounding error](../GLOSSARY.md)

## वार्म-अप

1. ▢ 4-bit affine quantizer -1 से 3 की range ढकता है। उसका step और सबसे बड़ी rounding error क्या हैं?

<details markdown="1"><summary>जाँचें</summary>

Step `s = 4 / 15 = 0.267` है और सबसे बड़ी rounding error `s/2 = 0.133`। Range 2^4 - 1 = 15 steps में बँटी है, और range के भीतर की value ज़्यादा से ज़्यादा आधा step खिसकती है।

</details>

2. ▢ कोई value quantizer की grid सीमाओं के बाहर है। क्या उसकी error `s/2` से बँधी है? उस error को क्या कहते हैं?

<details markdown="1"><summary>जाँचें</summary>

नहीं। Value सबसे नज़दीकी grid सीमा पर clamp हो जाती है, और जितनी दूरी वह तय करती है वह **clipping error** है, जिस पर `s/2` की कोई सीमा नहीं है और जो इस पर बढ़ती है कि value range से कितनी बाहर है।

</details>

3. ▢ Quantizers आम तौर पर symmetric weights को asymmetric activations के साथ क्यों जोड़ते हैं?

<details markdown="1"><summary>जाँचें</summary>

Asymmetric weights को asymmetric activations से गुणा करने पर ऐसा term बनता है जो input data पर निर्भर करता है, जिसकी क़ीमत run time पर latency और power में चुकानी पड़ती है (Nagel et al., section 2.4.1)। Symmetric weight grid उस term को हटा देती है, इसलिए अतिरिक्त zero point सिर्फ़ activations के पास रहता है।

</details>

## यह जानें

### विपरीत दिशाओं में खींचती दो errors

**Clipping range** real values का वह अंतराल है जिसे integer grid ढकती है, `q_min` से `q_max` तक। Nagel et al. section 2.2 के एक वाक्य में पूरा सौदा बता देते हैं: range चौड़ी करने से clipping error घटती है, पर इसके लिए बड़ा scale चाहिए, और rounding error, जो -s/2 और s/2 के बीच रहती है, उसके साथ बढ़ती है।

| Range | Clipping error | Rounding error | क्या ग़लत होता है |
|---|---|---|---|
| बहुत संकरी | बड़ी: outliers clamp हो जाते हैं | छोटी | सबसे बड़ी values की जगह range का किनारा आ जाता है |
| बहुत चौड़ी | कोई नहीं | बड़ी: step बड़ा है | आम values कुछ ही levels में गिरती हैं या zero पर round हो जाती हैं |

पेपर का section 3.1 इसे range तय करने का मुख्य trade-off कहता है, और बताता है कि हर method दोनों errors के बीच अलग संतुलन देता है। Weights पहले से पता होते हैं, इसलिए उनकी range को आम तौर पर data नहीं चाहिए। Activation की range input पर निर्भर करती है, इसलिए Nagel et al. कहते हैं कि उसे आम तौर पर calibration data के कुछ batches चाहिए, जो [calibration set](../GLOSSARY.md) का काम है।

### Methods

**Min-max.** सबसे छोटी और सबसे बड़ी value को `q_min` और `q_max` मानें। इसमें कोई clipping error नहीं होती, और Nagel et al. चेताते हैं कि यह outliers के प्रति संवेदनशील है, क्योंकि कोई ज़ोरदार outlier बड़ा step मजबूर करता है और इस तरह ज़रूरत से ज़्यादा rounding error। पाठ 4 ने यही इस्तेमाल किया था।

**Mean squared error.** वे `q_min` और `q_max` खोजें जो मूल और quantized tensor के बीच की mean squared error को न्यूनतम करें। पेपर इसे हल करने के तरीक़ों के रूप में grid search, golden section method और closed-form approximations गिनाता है, और कहता है कि साहित्य के सारे variants बहुत मिलते-जुलते हैं। जब outliers min-max range को फुला दें, तब यही method उठाना चाहिए।

**Percentile.** Range को absolute values के किसी ऊँचे percentile पर रखें, जैसे 99.9वाँ, ताकि values का एक तय अंश clip हो। यह एक सरल heuristic है, section 3.1 के methods में से नहीं, और नीचे का experiment इसे इस्तेमाल करता है ताकि आप देख सकें कि तय अंश की क्या क़ीमत है और वह क्या देता है।

Section 3.1 दो और विशेष मामलों के लिए गिनाता है: आख़िरी layer के logits के लिए cross-entropy को न्यूनतम करना, जहाँ सबसे बड़ी values का क्रम कई छोटी values से ज़्यादा मायने रखता है, और activations के लिए batch-normalization पर आधारित range। यह track batch normalization के बिना LLMs को quantize करता है, इसलिए पहले तीन इस्तेमाल करता है।

Nagel et al. अपनी Table 1 में पहले दो की तुलना ImageNet classifiers पर करते हैं, जहाँ weights per tensor quantize हैं और activations floating point में छोड़ी गई हैं। 8 bits पर ResNet18 के लिए min-max और MSE लगभग बराबर हैं: 69.57 बनाम 69.45 top-1 accuracy। 4 bits पर, min-max गिरकर 0.12 पर आ जाता है और MSE 18.82 बनाए रखता है। ये vision models हैं, इसलिए नतीजे का आकार पढ़ें, संख्याएँ नहीं: कम levels के साथ, range का चुनाव तय करता है कि model चलेगा भी या नहीं।

### Experiment क्या दिखाता है

अभ्यास का experiment एक भारी पूँछ वाले tensor को 4 bits पर quantize करता है। उसकी सबसे बड़ी value 1.506 है और standard deviation 0.034, यानी लगभग 44 का अनुपात। Min-max range के साथ step `1.506 / 7 = 0.215` है, उसका आधा 0.108 है जो तीन standard deviations से ज़्यादा है, इसलिए लगभग हर value zero पर round हो जाती है। MSE search जिन 0.35 प्रतिशत values को clip करता है उन्हें clip करने से error लगभग छह गुना घट जाती है। Grid उस range पर ख़र्च हो रही है जिस पर लगभग कोई value जाती ही नहीं।

### LLMs के लिए यह पूरा जवाब क्यों नहीं है

MSE हर value की squared error को बराबर गिनता है। Nagel et al. logits के बारे में यही बात कहते हैं: MSE उन values के लिए ठीक नहीं हो सकता जो असमान रूप से ज़रूरी हैं, क्योंकि वह सारी values को बराबर वज़न देता है। LLM में सबसे बड़ी कुछ values ही ज़रूरी हो सकती हैं। [Dettmers et al.](https://arxiv.org/abs/2208.07339) बताते हैं कि outlier feature dimensions को zero करने से validation perplexity 600 से 1000 प्रतिशत बिगड़ गई, जबकि वे features का लगभग 0.1 प्रतिशत हैं। जो range उन्हें clip करती है उसका tensor की MSE पर असर बहुत छोटा होता है और model पर बड़ा हो सकता है। पाठ 7 समझाता है कि वे values कहाँ से आती हैं, और पाठ 8 वे इलाज देता है जो उन्हें clip नहीं करते।

## अभ्यास

1. ▢ -7 से 7 की grid वाले 4-bit signed symmetric quantizer की min-max range 1.506 है, ऐसे tensor पर जिसका standard deviation 0.034 है। `s` क्या है, और कौन-सी values zero पर round होती हैं?

<details markdown="1"><summary>जाँचें</summary>

`s = 1.506 / 7 = 0.215`। जिस value का absolute value `s/2 = 0.108` से नीचे है वह integer 0 पर round होती है, जो तीन standard deviations से ज़्यादा है। घंटी के आकार वाले tensor के लिए यह लगभग हर value है, यानी एक दूर के maximum ने tensor को मिटा दिया है।

</details>

2. ▢ कौन-सा कथन clipping range को चौड़ा करने का वर्णन करता है?

    - a) Clipping error और rounding error दोनों घटती हैं
    - b) Clipping error और rounding error दोनों बढ़ती हैं
    - c) Clipping error घटती है जबकि rounding error बढ़ती है
    - d) Clipping error बढ़ती है जबकि rounding error घटती है

<details markdown="1"><summary>जाँचें</summary>

**c)** चौड़ी range कम values को clamp करती है, इसलिए clipping error घटती है, पर उतने ही levels अब ज़्यादा दूरी फैलाते हैं, इसलिए step और rounding error बढ़ते हैं। (a) range का चुनाव मामूली बना देता, क्योंकि आप हमेशा चौड़ा करते। (b) दोनों ग़लत पकड़ता है, क्योंकि चौड़ा करने से clipping error बढ़ नहीं सकती। (d) range को संकरा करने का वर्णन है, चौड़ा करने का नहीं।

</details>

3. ▢ पहले अनुमान लगाएँ, फिर चलाएँ। यह 100,000 भारी पूँछ वाली values को चार ranges के तहत 4 bits पर quantize करता है। चलाने से पहले अनुमान लगाएँ कि किस range की mean squared error सबसे कम है, और क्या min-max आधी से ज़्यादा values को zero पर round करता है या कम को।

    ```python
    import numpy as np

    rng = np.random.default_rng(0)
    x = rng.standard_t(df=3, size=100_000) * 0.02   # heavy-tailed
    qmax = 7                                        # 4-bit signed symmetric grid: -7..7 times the scale


    def quantize(x, c):
        s = c / qmax
        return s * np.clip(np.round(x / s), -qmax, qmax)


    def mse(x, c):
        return np.mean((quantize(x, c) - x) ** 2)


    grid = np.linspace(0.01, np.abs(x).max(), 400)
    ranges = {
        "min-max": np.abs(x).max(),
        "p99.9": np.percentile(np.abs(x), 99.9),
        "p99": np.percentile(np.abs(x), 99),
        "MSE search": grid[np.argmin([mse(x, c) for c in grid])],
    }
    print("max |x| =", round(np.abs(x).max(), 3), " std =", round(x.std(), 3))
    for name, c in ranges.items():
        q = quantize(x, c)
        print(f"{name:10s} c={c:.3f}  mse={mse(x, c):.2e}  clipped={np.mean(np.abs(x) > c):6.2%}  rounded to zero={np.mean(q == 0):6.2%}")
    ```

<details markdown="1"><summary>संकेत</summary>

पहले min-max का step निकालें, जैसा सवाल 1 में किया था, और उसके आधे की तुलना standard deviation से करें।

</details>

<details markdown="1"><summary>जाँचें</summary>

```text
max |x| = 1.506  std = 0.034
min-max    c=1.506  mse=8.15e-04  clipped= 0.00%  rounded to zero=98.72%
p99.9      c=0.252  mse=1.61e-04  clipped= 0.10%  rounded to zero=56.61%
p99        c=0.117  mse=1.53e-04  clipped= 1.00%  rounded to zero=29.40%
MSE search c=0.171  mse=1.35e-04  clipped= 0.35%  rounded to zero=41.52%
```

MSE search जीतता है, और min-max सबसे ख़राब है, लगभग छह गुना ऊँचा, जिसमें 98.7 प्रतिशत values zero पर round हो गईं। सिर्फ़ 0.10 प्रतिशत values को clip करना (p99.9) ही error को पाँच गुना घटा देता है। 1 प्रतिशत को clip करना (p99) search से थोड़ा ख़राब है (1.53e-04 बनाम 1.35e-04), क्योंकि clip हुई values की अब ज़्यादा क़ीमत पड़ती है उस rounding से जो बची: सबसे अच्छी range दोनों छोरों के बीच बैठती है।

</details>

4. ▢ पहले अनुमान लगाएँ, फिर चलाएँ। `qmax = 7` को `qmax = 127` में बदलें, जिससे वह 8-bit grid बन जाती है, और फिर चलाएँ। क्या clipping तब भी जीतेगी? MSE search अब कौन-सी range चुनता है?

<details markdown="1"><summary>जाँचें</summary>

```text
max |x| = 1.506  std = 0.034
min-max    c=1.506  mse=1.17e-05  clipped= 0.00%  rounded to zero=21.23%
p99.9      c=0.252  mse=5.51e-05  clipped= 0.10%  rounded to zero= 3.65%
p99        c=0.117  mse=1.30e-04  clipped= 1.00%  rounded to zero= 1.69%
MSE search c=1.019  mse=7.72e-06  clipped= 0.00%  rounded to zero=14.52%
```

Clipping अब नहीं जीतती: min-max दोनों percentile ranges को हरा देता है, और MSE search 1.019 चुनता है, जो पूरी range के क़रीब है, और 0.005 प्रतिशत से कम values clip होती हैं। हर तरफ़ 127 levels के साथ step इतना छोटा है कि outliers की rounding error की क़ीमत कम पड़ती है, जबकि उन्हें clip करने की क़ीमत बहुत ज़्यादा है। यह Nagel et al. की Table 1 जैसा ही आकार है, जहाँ 8 bits पर min-max और MSE बराबर हैं: levels जितने कम, कसी हुई range उतना ज़्यादा फ़ायदा देती है।

</details>

5. ▢ कोई team हर LLM activation की range MSE न्यूनतम करके तय करती है, और perplexity उछल जाती है। इस पाठ का इस्तेमाल करके सबसे संभावित तंत्र बताएँ, और बताएँ कि MSE क्या नहीं देख सका।

<details markdown="1"><summary>जाँचें</summary>

Range ने outlier features को clip कर दिया। वे values का बहुत छोटा हिस्सा हैं, इसलिए उन्हें clamp करने से tensor की MSE बहुत कम बदलती है, पर वे अपनी संख्या से कहीं ज़्यादा मायने रखते हैं: Dettmers et al. ने उन dimensions को zero करने पर perplexity 600 से 1000 प्रतिशत ऊँची मापी। MSE हर value को बराबर वज़न देता है, और Nagel et al. ध्यान दिलाते हैं कि जब values की अहमियत अलग हो तो यह ग़लत वज़न है। Range तय करने वाला objective task loss का एक स्थानीय proxy है, और यहाँ वह ग़लत दिशा में इशारा करता है। Outliers को clip होने वाले सेट से बाहर रखना पाठ 8 का विषय है।

</details>

## असली दुनिया का अभ्यास

- [ ] Experiment को `df=10` के साथ दोबारा चलाएँ, फिर `standard_t` की जगह `rng.normal` के साथ। हर बार MSE search की सबसे अच्छी clip को standard deviation के गुणज के रूप में दर्ज करें, और ध्यान दें कि पूँछें हल्की होने पर वह कैसे खिसकती है।
- [ ] किसी छोटे open model से एक weight matrix लें और उसका अधिकतम absolute value उसके absolute value के 99वें और 99.9वें percentile के साथ print करें। तय करें कि क्या min-max उस पर 4-bit grid का ज़्यादातर हिस्सा बर्बाद कर देता।
- [ ] कल: बिना नोट्स के बताएँ कि min-max, MSE और percentile हर एक किसे optimize करता है, और किस bit width पर यह चुनाव सबसे ज़्यादा मायने रखता है। फिर section 3.1 दोबारा पढ़ें और जाँचें कि क्या आपने सही trade-off का नाम लिया था।

## आगे बढ़ने के लिए

- [Quantization Mapping शीट](../reference/quantization-mapping.md)
- [पेपर: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295)
- [पेपर: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., 2022](https://arxiv.org/abs/2208.07339), section 4.2, यह जानने के लिए कि outliers को clip करना ख़तरनाक क्यों है
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
