---
title: "27. जब आम जवाब ग़लत हो"
description: "पहचानें कि 4-bit weights या कोई मानक नुस्ख़ा कब ग़लत फ़ैसला है, और विवाद का निपटारा मुख्य स्रोत से करें"
type: lesson
---

# पाठ 27. जब आम जवाब ग़लत हो

**मिशन से संबंध:** यह track इस भरोसे के साथ ख़त्म होता है कि आप quantization पर फ़ैसला ले सकें और उसे किसी और को समझा सकें। "4-bit weights इस्तेमाल करें" और "AWQ, GPTQ से बेहतर है" आम जवाब हैं, और हर एक कुछ models, tasks और hardware के लिए सच है और दूसरों के लिए झूठ। यह पाठ वह तरीक़ा है जिससे पता चलता है कि कौन-सा, और वे मामले जहाँ आम जवाब विफल होता है।
**मुख्य स्रोत:** [पेपर: "Scaling Laws for Precision", Kumar et al., 2024](https://arxiv.org/abs/2411.04330), sections 1 से 3
**पूर्व-आवश्यकताएँ:** [पाठ 25](0025-choosing-a-scheme.md), [पाठ 26](0026-reviewing-a-quantization-claim.md), [Post-training quantization](../GLOSSARY.md), [Compute-bound](../GLOSSARY.md), [Weight-only quantization](../GLOSSARY.md)

## वार्म-अप

1. ▢ एक massive activation या outlier feature per-tensor scale को क्यों बिगाड़ देता है, और कौन-सा इलाज outliers को ऊँची precision में रखने की जगह group को छोटा करता है?

<details markdown="1"><summary>जाँचें</summary>

Scale सबसे बड़ी value से तय होता है, इसलिए एक विशाल value लगभग बाक़ी सब को zero के पास कुछ ही levels पर छोड़ देती है। Per-group scales group को छोटा करते हैं ताकि outlier सिर्फ़ अपने ही group के levels बर्बाद करे (पाठ 7, 8 और 6)।

</details>

2. ▢ Calibration set GPTQ और AWQ में क्या योगदान देता है, और बेमेल set कैसे दिखता है?

<details markdown="1"><summary>जाँचें</summary>

प्रतिनिधि inputs से activation statistics: GPTQ उन्हें second-order error की भरपाई के लिए इस्तेमाल करता है, AWQ यह खोजने के लिए कि कौन-से weight channels बड़ी activations से मिलते हैं। बेमेल set ऐसे model के रूप में दिखता है जो calibration data जैसे text पर अच्छा score करता है और उस traffic पर बदतर जिससे वह मिलता-जुलता नहीं था (पाठ 10, 11 और 12)।

</details>

3. ▢ Flip क्या है, और accuracy अपरिवर्तित होने पर भी वह बड़ी क्यों हो सकती है?

<details markdown="1"><summary>जाँचें</summary>

ऐसा उत्तर जो baseline और quantized model के बीच सही से ग़लत या उसका उलटा हो गया। फ़ायदे और नुक़सान औसत में कट जाते हैं, इसलिए accuracy बराबर हो सकती है जबकि कई अलग-अलग उत्तर हिलते हैं (पाठ 21 और 26)।

</details>

## यह जानें

### तरीक़ा

आम जवाब बिना अपनी शर्तों के नारे की तरह आता है। चार चरण तय करते हैं कि वह आपके लिए टिकता है या नहीं।

1. **मुख्य स्रोत खोजें।** पेपर, उसे उद्धृत करने वाली post नहीं, यह देखने के लिए पढ़ा जाए कि असल में क्या मापा गया।
2. **Model, आकार और तारीख़ जाँचें।** कौन-से model परिवार, कितने बड़े, कितने data पर train हुए, कब मापे गए। 2022 के models पर नतीजा 2024 के नुस्ख़े के बारे में कम बताता है।
3. **जाँचें कि दावा क्या ढकता है।** कुल bits के सामने zero-shot accuracy serving throughput नहीं है, और academic tasks पर औसत open-ended chat नहीं है।
4. **अपने tasks पर परखें।** अगर स्रोत और आपका मामला अलग हैं, तो जो नतीजा निपटारा करता है वह आपका है (पाठ 22)।

नीचे के मामलों में से कोई नहीं कहता कि आम जवाब हमेशा ग़लत है। हर एक बताता है कि उसका स्रोत क्या समर्थन करता है, और कहाँ रुक जाता है।

### मामला 1: बहुत ज़्यादा train हुआ model

Kumar et al. "precision-aware" scaling laws फिट करते हैं और पाते हैं कि post-training quantization से गिरावट तब बढ़ती है जब model ज़्यादा data पर train होता है, "अंततः अतिरिक्त pretraining data को सक्रिय रूप से हानिकारक बना देती है" ([सार](https://arxiv.org/abs/2411.04330))। उनकी सहज समझ: ज़्यादा data पर train हुआ model अपने weights में ज़्यादा जानकारी दबाता है, इसलिए उन्हें हिलाने से ज़्यादा चोट लगती है। वे parameters के मुक़ाबले training tokens के बहुत ऊँचे अनुपात वाले models को "overtrained" कहते हैं, और ध्यान दिलाते हैं कि Llama-3-8B लगभग 2000 के अनुपात तक train हुआ है।

दायरा पढ़ें। वे अपने laws 465 से ज़्यादा pretraining runs पर फिट करते हैं और 26B tokens तक पर train हुए 1.7B parameters तक के models पर validate करते हैं। वे ध्यान दिलाते हैं कि 8-bit जैसी आम इस्तेमाल होने वाली precisions पर अतिरिक्त pretraining के हानिकारक बनने के लिए बेहद ज़्यादा data चाहिए, पर बहुत overtrained models पर गिरावट के असर लगभग 5 bits के आसपास मामूली नहीं रहते और उसके नीचे हावी हो जाते हैं। इसलिए दावा यह है कि हर parameter पर training बजट बढ़ने के साथ आम 4-bit वाला जवाब ज़्यादा जोखिम भरा हो जाता है, और सबूत छोटे पैमाने के models और एक फिट किया हुआ law है। यह इसकी माप नहीं है कि कोई ख़ास Llama 3 checkpoint कितना खोता है।

एक विपरीत नतीजा मौजूद है। Kurtic et al. ने 8B, 70B और 405B के quantized Llama 3.1 models मापे और tune किए गए GPTQ के साथ Open LLM Leaderboard V1 tasks पर W4A16 को bf16 औसत का 99.36 प्रतिशत वापस पाते पाया ([Kurtic et al., 2024](https://arxiv.org/abs/2411.02355))। दोनों एक-दूसरे का निपटारा नहीं करते। एक छोटे models पर फिट किया law है, दूसरा tune किए नुस्ख़े और औसत tasks के साथ एक परिवार की माप। सबक़ यह है कि बहुत ज़्यादा train हुए model को ज़्यादा सावधानी से मापने की वजह मानें, किसी भी तरफ़ के फ़ैसले की तरह नहीं।

### मामला 2: छोटा model, या reasoning model

Kurtic et al. बताते हैं कि सबसे छोटे models INT4 पर थोड़ा ज़्यादा खोते हैं। उनके reasoning benchmarks, जो DeepSeek-R1-Distill models पर चले, इसे संख्याओं में दिखाते हैं: W4A16-INT के लिए bf16 औसत की recovery Qwen-32B के लिए 99.5 प्रतिशत और Llama-70B के लिए 98.3 प्रतिशत थी, Llama-8B के लिए 97.2 प्रतिशत, और Qwen-1.5B के लिए 93.5 प्रतिशत, जिसके लिए W8A8-INT ने 96.9 प्रतिशत और W8A8-FP ने 100.3 प्रतिशत पाया। Quantized reasoning models का एक अलग अध्ययन, [Liu et al., 2025](https://arxiv.org/abs/2504.04823), पाता है कि W8A8 या W4A16 से lossless quantization मुमकिन है पर कम bit widths पर accuracy के बड़े जोखिम हैं। उसका abstract model के आकार, model की उत्पत्ति और task की कठिनाई को निर्धारक बताता है।

Noise पर भी ध्यान दें। AIME24 पर, 1.5B model ने bf16 में 5.3 के बताए margin के साथ 30.1 और W4A16 में 5.1 के margin के साथ 24.6 score किया, इसलिए छोटे sets पर एक-benchmark के फ़ासले अपने ही margins से मिल जाते हैं। Tasks पर औसत कहता है कि छोटे model ने ज़्यादा खोया। अकेला task इसे साबित नहीं करता।

### मामला 3: लंबा context, जहाँ चिंता टिकती नहीं

मान लेना आसान है कि लंबा context quantization में टूट जाता है। RULER long-context benchmark पर, 4k से 128k tokens तक evaluate किए गए, Kurtic et al. तीनों formats में कम से कम 98 प्रतिशत की औसत score recovery बताते हैं, 405B model को evaluate किए बिना क्योंकि वह वर्जित रूप से महँगा है। यह Llama 3.1 पर एक benchmark है और KV cache को quantize करना कवर नहीं करता, जिसे पेपर उन चीज़ों में गिनाता है जिनका उसने अध्ययन नहीं किया। यह उस आम चिंता का अच्छा उदाहरण है जिसे स्रोत उस मामले के लिए समर्थन नहीं देता जो उसने मापा।

### मामला 4: compute-bound serving

Weight-only 4-bit memory दबाव के लिए आम जवाब है, और वह मानता है कि काम memory-bound है। MARLIN के लेखक हिसाब देते हैं: एक input token को प्रति weight 2 FLOPs लगते हैं और GPU एक 4-bit weight load करने के समय में लगभग 100 FLOPs चला सकता है, इसलिए memory loading तब तक ही हावी रहती है जब तक batch लगभग 50 से नीचे है ([Frantar et al., 2024](https://arxiv.org/abs/2408.11743))। Compute और bandwidth का वही अनुपात 16-bit weight को load होने में चार गुना समय लगवाता है, इसलिए bf16 का crossover लगभग batch 200 के पास बैठता है। Weights को quantize करना crossover को नीचे ले आता है, इसीलिए batches बढ़ने पर फ़ायदा सिकुड़ता है।

मौजूदा INT4 methods, QServe बताता है, 20 से 90 प्रतिशत dequantization overhead झेलते हैं और सिर्फ़ कम-batch inference को तेज़ करते हैं ([Lin et al., 2024](https://arxiv.org/abs/2405.04532))। Kurtic et al. के asynchronous serving नतीजों में W8A8 throughput में हावी है। आधुनिक hardware पर throughput-बद्ध service के लिए आम 4-bit वाला जवाब ग़लत है।

### मामला 5: जब fp8 सुरक्षित default है

अगर GPU fp8 natively compute करता है, तो Kurtic et al. के data में W8A8-FP हर model आकार पर प्रभावी रूप से lossless है, और उसे calibration data नहीं चाहिए क्योंकि वे round-to-nearest से quantize करते हैं। ठीक से tune किया W8A8-INT 1 से 3 प्रतिशत खोता था, और 70B पर उसे SmoothQuant और बेहतर calibration data चाहिए था। इसलिए जहाँ hardware उसे support करता है और memory समाती है, fp8 कम जोखिम वाली पहली कोशिश है, और 4-bit को अपनी जगह memory या decode-latency की ज़रूरत से कमानी होगी।

### मुख्य स्रोत से विवाद का निपटारा

दो साथी दो बातें कहते हैं।

- **"AWQ हमेशा GPTQ को हराता है।"** बहस करने की जगह Kurtic et al. की Table 1 खोलें। Academic benchmarks पर AWQ, GPTQ से 8B और 70B पर सिर्फ़ 0.23 और 0.35 अंक आगे था, लगभग बराबरी। Real-world benchmarks (Arena-Hard, HumanEval, MBPP) पर GPTQ, AWQ से 8B पर 2.9 अंक (52.3 बनाम 49.4) और 70B पर 0.8 से आगे था। वे AWQ के पक्ष में पहले की खोजों को अनुपयुक्त hyperparameters का नतीजा बताते हैं, और अपनी setup देते हैं: MSE-इष्टतम clipping वाला GPTQ जहाँ पहले की तुलना ने abs-max इस्तेमाल किया, C4 default से बेहतर calibration set, और दोनों के लिए group size 128। फिर noise जाँचें: 8B पर Arena-Hard पर, bf16 model के दो runs ने 25.1 और 26.5 score किए, इसलिए लगभग 1 अंक का फ़ासला run-to-run फैलाव के भीतर है। स्रोत क्या समर्थन करता है: कोई method हमेशा नहीं जीतता, रैंकिंग नुस्ख़े और task के प्रकार के साथ खिसकी, और लेखक एक team हैं जिसने GPTQ को अपना method भी चुना। दोनों को अपने tasks पर चलाएँ।
- **"Perplexity 0.1 बढ़ी, इसलिए ठीक है।"** पूछें: किस baseline के सापेक्ष, किस text और window पर, और अलग-अलग उत्तरों का क्या हुआ? Dutta et al. ने ऐसी schemes पाईं जिनकी accuracy baseline के 0 से 2 प्रतिशत के भीतर थी और flips 13.6 प्रतिशत तक, और बहुत flips वाले compressed models MT-Bench पर उल्लेखनीय रूप से बदतर score करते थे। 0.1 की perplexity का बदलाव औसत है और इस पर निर्भर करके छोटा या बड़ा हो सकता है कि वह किस पर औसत लेता है। स्रोत "flips और एक open-ended task जाँचें" का समर्थन करता है, "0.1 मायने रखने के लिए बहुत छोटा है" या "0.1 बहुत बड़ा है" का नहीं।

## अभ्यास

1. ▢ कोई साथी कहता है "AWQ हमेशा GPTQ को हराता है।" आप कौन-सी table खोलते हैं, और उसमें क्या जाँचते हैं?

<details markdown="1"><summary>जाँचें</summary>

Kurtic et al. में आमने-सामने की तुलना (Table 1) खोलें और उसके पीछे की setup जाँचें: वही group size, clipping का तरीक़ा, calibration set, और क्या tasks academic हैं या open-ended। वह academic tasks पर लगभग बराबरी और real-world वालों पर GPTQ की बढ़त दिखाती है। वह यह नहीं दिखाती कि GPTQ हमेशा जीतता है, सिर्फ़ यह कि AWQ वाले दावे की शर्तें हैं।

</details>

2. ▢ कोई साथी कहता है "Kumar et al. ने साबित कर दिया कि post-training 4-bit हमारे बहुत ज़्यादा train हुए model को बर्बाद कर देगा।" पेपर क्या समर्थन करता है?

    - a) एक फिट किया हुआ law, इसलिए अपना model मापें
    - b) इसका प्रमाण कि हर 4-bit scheme विफल होती है
    - c) सिर्फ़ fp4 में training के बारे में नतीजा
    - d) आपके सटीक model checkpoint की माप

<details markdown="1"><summary>जाँचें</summary>

**a)** पेपर 1.7B parameters और 26B tokens तक के runs पर laws फिट करता है और पाता है कि ज़्यादा data post-training quantization की गिरावट बढ़ाता है, जो आपके model को मापने की वजह है, उस पर फ़ैसला नहीं। (b) फिट किए हुए law को प्रमाण तक बढ़ा देता है। (c) ग़लत है क्योंकि वह training precision के साथ post-training quantization को भी कवर करता है। (d) ग़लत है क्योंकि उसने आपका कोई checkpoint नहीं मापा।

</details>

3. ▢ पहले अनुमान लगाएँ, फिर चलाएँ। MARLIN की प्रति 4-bit weight load पर लगभग 100 FLOPs और प्रति token प्रति weight 2 FLOPs की संख्या का इस्तेमाल करके, अनुमान लगाएँ कि अगर machine का compute-to-bandwidth अनुपात वही है तो 4-bit weights और 16-bit weights के लिए किस batch size से नीचे memory हावी है। फिर इसे चलाएँ।

    ```python
    flops_per_weight_load_4bit = 100
    flops_per_token_per_weight = 2
    for name, bytes_per_weight in [("4-bit weights", 0.5), ("16-bit weights", 2.0)]:
        flops_per_byte = flops_per_weight_load_4bit / 0.5
        crossover = flops_per_byte * bytes_per_weight / flops_per_token_per_weight
        print(f"{name:15s} memory-bound below batch about {crossover:.0f}")
    ```

<details markdown="1"><summary>संकेत</summary>

16-bit weight 4-bit वाले के चार गुना bytes है, इसलिए उसके load को ढकने के लिए चार गुना FLOPs चाहिए।

</details>

<details markdown="1"><summary>जाँचें</summary>

```text
4-bit weights   memory-bound below batch about 50
16-bit weights  memory-bound below batch about 200
```

4-bit वाली संख्या MARLIN का अपना अनुमान है, और 16-bit वाली उसी धारणा पर यह हिसाब है, माप नहीं। बात सटीक संख्याओं के बिना भी टिकती है: weights को quantize करना उस batch size को घटाता है जिस पर service compute-bound बनती है, इसलिए जो service बड़े batches चलाती है उसे weight-only 4-bit से कम फ़ायदा मिलता है।

</details>

4. ▢ Kurtic et al. की reasoning table से: Qwen-1.5B ने AIME24 पर bf16 में 30.1 (margin 5.3) और W4A16-INT में 24.6 (margin 5.1) score किया, 93.5 प्रतिशत औसत recovery के साथ। कोई साथी कहता है "AIME24 साबित करता है कि 4-bit ने उसे तोड़ दिया"। आप क्या कहेंगे?

<details markdown="1"><summary>जाँचें</summary>

अकेले AIME24 पर दोनों scores अपने बताए margins के भीतर एक-दूसरे के पास हैं, इसलिए वह benchmark इसे साबित नहीं करता। तीन tasks पर 93.5 प्रतिशत औसत recovery, बड़े models के 98 से 99 प्रतिशत के बग़ल में रखी हुई, इसका ज़्यादा मज़बूत सबूत है कि सबसे छोटे model ने ज़्यादा खोया। दोनों में से कोई नहीं कहता कि model इस्तेमाल के लायक़ नहीं: अगला क़दम अपने tasks को इतने samples के साथ चलाना है कि अंतर noise से अलग पहचाना जा सके।

</details>

5. ▢ किसी team के पास H100 GPUs हैं, bf16 में 8B model के लिए काफ़ी memory है, और एक batch job जहाँ सिर्फ़ throughput मायने रखता है। कोई साथी 4-bit AWQ सुझाता है "क्योंकि 4-bit मानक है"। इसके ख़िलाफ़ तर्क दें, और बताएँ कि आपका मन क्या बदलेगा।

<details markdown="1"><summary>जाँचें</summary>

Job बड़े batches पर compute-bound है, जहाँ weight-only 4-bit थोड़ा फ़ायदा देता है और उसका dequantization throughput की क़ीमत ले सकता है (MARLIN, QServe), जबकि Kurtic et al. के data में W8A8-FP प्रभावी रूप से lossless है और native fp8 वाले hardware पर उनके asynchronous throughput नतीजों में हावी है। Memory कोई बाध्यता नहीं है। आपका मन क्या बदलेगा: आपके अपने batch size और tasks पर throughput और quality की माप जो 4-bit kernel को आगे दिखाए, या ऐसी memory सीमा जो 8 bits पर जितना समाता है उससे बड़ा model माँगे।

</details>

## असली दुनिया का अभ्यास

- [ ] quantization का कोई अंगूठे का नियम लें जिस पर आप निर्भर हैं (उदाहरण के लिए "4-bit ठीक है") और उसे पेपर तक खोजें। Models, आकार, साल और क्या मापा गया लिखें, और जहाँ आपका मामला अलग है।
- [ ] Kurtic et al. की Table 1 खोलें और उनके GPTQ और AWQ runs के बीच setup के अंतर एक पंक्ति में लिखें, ताकि आप अगली "कौन बेहतर है" वाली बहस का जवाब table से दे सकें।
- [ ] कल: जिस model को आप सबसे ज़्यादा quantize करना चाहते हैं उसके लिए, इस पाठ का वह एक मामला लिखें जो उस पर सबसे ज़्यादा लागू होने की संभावना रखता है, और वह माप जो दिखाएगी कि वह लागू होता है या नहीं।

## आगे बढ़ने के लिए

- [Quantization Review Checklist शीट](../reference/quantization-review-checklist.md)
- [पेपर: "Scaling Laws for Precision", Kumar et al., 2024](https://arxiv.org/abs/2411.04330)
- [पेपर: "Give Me BF16 or Give Me Death? Accuracy-Performance Trade-Offs in LLM Quantization", Kurtic et al., 2024](https://arxiv.org/abs/2411.02355)
- [पेपर: "Quantization Hurts Reasoning? An Empirical Study on Quantized Reasoning Models", Liu et al., 2025](https://arxiv.org/abs/2504.04823)
- [संसाधन](../RESOURCES.md)

---

यह track का अंत है, और जिस आदत के लिए इसे बनाया गया वह इसी पाठ वाली है: quantized model number format, method, kernel और tasks के सेट के बारे में एक दावा है, इसलिए खोजें कि दावा कहाँ से आता है, जाँचें कि उसने क्या कवर किया, और किसी और के सामने उसका बचाव करने से पहले अपने tasks पर मापें।

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
