---
title: "15. बड़े पैमाने पर Mixed Precision: bfloat16 और Stochastic Rounding"
description: "fp32 जैसी range पर कम precision वाला numeric format, और parameters को सीधे उसी में update करने की क्या क़ीमत है"
type: lesson
---

# पाठ 15. बड़े पैमाने पर Mixed Precision: bfloat16 और Stochastic Rounding

**मिशन से संबंध:** "Loss curve देखकर बता सकें कि spike recover होने लायक़ है या पुराने checkpoint से restart चाहिए" "सफलता कैसी दिखती है" का वह सबसे क़रीबी बिंदु है जिसे यह चरण पूरा करता है, और यह उस numeric format से शुरू होता है जिसमें training run चल ही रहा है। पाठ 16 loss spikes को सीधे कवर करता है; पाठ 17 learning-rate schedule को कवर करता है।
**मुख्य स्रोत:** [पेपर: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**पूर्व-आवश्यकताएँ:** [पाठ 14](0014-combining-all-three-when-tensor-and-pipeline-parallelism-earn-their-cost.md)

## वार्म-अप

1. ▢ Narayanan et al. के अनुसार, tensor parallelism एक अकेले node के भीतर सीमित रखना सबसे अच्छा क्यों है, जबकि pipeline parallelism nodes में फैलना सह लेता है?

<details markdown="1"><summary>जाँचें</summary>

Tensor parallelism को हर layer के लिए महँगा all-reduce चाहिए, जिसे कुशल रहने के लिए सबसे तेज़ उपलब्ध interconnect चाहिए। Pipeline parallelism सिर्फ़ मुट्ठी भर stage सीमाओं के बीच activations पास करता है, कहीं सस्ते point-to-point communication से, जो धीमे, लंबी दूरी के links पर भी पूरे computation को bottleneck नहीं करता।

</details>

## यह जानें

### 32-bit संख्या को 16 bits में बिठाने के दो तरीक़े

32-bit floating-point संख्या (`fp32`) अपने bits को range (exponent) और precision (mantissa, शुरुआती एक के बाद के अंक) में बाँटती है। दो अलग 16-bit formats इसे अलग तरह से दबाते हैं। `fp16` में 10 mantissa bits रहते हैं पर सिर्फ़ 5 exponent bits, यानी `fp32` की range का बड़ा हिस्सा छोड़कर संकरी range के भीतर ज़्यादा precision; बहुत बड़ा या बहुत छोटा gradient उसमें overflow या underflow हो सकता है। **`bfloat16`** (`bf16`) उलटा सौदा करता है: वह `fp32` के पूरे 8 exponent bits रखता है, इसलिए उसकी dynamic range वही है, पर सिर्फ़ 7 mantissa bits, इसलिए उस range के भीतर वह मोटा है। वही चौड़ी range इसकी वजह है कि bf16 training के दौरान ज़्यादा क्षमाशील होता है: बड़े पैमाने पर gradients और activations में जो बड़े या बहुत छोटे मान दिखते हैं उनके उसमें overflow या underflow होने की संभावना कम होती है।

### Gopher ने असल में इसका क्या किया

Rae et al. बताते हैं कि उन्होंने bfloat16 ख़ास तौर पर memory घटाने और training throughput बढ़ाने के लिए इस्तेमाल किया, पर उन्होंने इसे अपने train किए हर model size पर एक-सा लागू नहीं किया। 7.1 अरब parameters से छोटे models साधारण mixed precision से train हुए: `fp32` parameters, `bf16` activations। उनके दो सबसे बड़े models, 7.1B model और ख़ुद Gopher (280B), और आगे गए और सिर्फ़ activations के लिए नहीं, parameters के लिए भी `bf16` इस्तेमाल किया।

### bf16 में parameters को ख़ास सँभाल क्यों चाहिए

bf16 में रखे parameter को सीधे update करने पर वह समस्या आती है जिससे साधारण mixed-precision training `fp32` master copy रखकर बचती है: bf16 की मोटी precision का मतलब है कि छोटा update rounding में बस ग़ायब हो सकता है, अगर वह उस parameter के मौजूदा मान के आसपास के दो पास-पास representable bf16 मानों के अंतर से छोटा हो। Rae et al. इसे **stochastic rounding** से सँभालते हैं: किसी मान को हमेशा उसके सबसे नज़दीकी representable bf16 मान पर round करने के बजाय (जो छोटे updates को चुपचाप, पक्षपाती, एकतरफ़ा ढंग से फेंक देता), stochastic rounding ऊपर या नीचे उस संभावना से round करता है जो इस अनुपात में होती है कि सच्चा मान हर पड़ोसी के कितना क़रीब है, इसलिए छोटा update सीधे खोता नहीं; वह कई steps में औसतन बचा रहता है, भले किसी एक step की rounding randomized हो। Rae et al. साफ़ कहते हैं कि यह समस्या को पूरी तरह नहीं सुलझाता: वे बताते हैं कि stochastic rounding साधारण mixed-precision training के प्रदर्शन को पूरी तरह वापस नहीं पाता, जो साफ़ हल के बजाय ईमानदार सीमा है।

## अभ्यास

1. ▢ Training के दौरान कोई gradient मान असामान्य रूप से बड़ा है, इतना कि संख्यात्मक overflow की चिंता हो। कौन-सा 16-bit format, fp16 या bf16, उसे overflow हुए बिना दर्शाने की ज़्यादा संभावना रखता है, और क्यों?

<details markdown="1"><summary>जाँचें</summary>

bf16। वह fp32 जैसे ही 8 exponent bits रखता है, इसलिए उसकी dynamic range वही है, इसलिए जो बड़ा मान fp16 की संकरी 5-bit exponent range में overflow होता वह bf16 में overflow होने की कम संभावना रखता है।

</details>

2. ▢ सीधे bf16 में रखे parameter को update करना (fp32 master copy रखे बिना) छोटे updates को चुपचाप खोने का जोखिम क्यों रखता है?

<details markdown="1"><summary>जाँचें</summary>

bf16 में सिर्फ़ 7 mantissa bits हैं, इसलिए वह अपनी range के भीतर मोटा है; छोटा update parameter के मौजूदा मान के आसपास के दो पास-पास representable bf16 मानों के अंतर से छोटा हो सकता है, और सबसे नज़दीकी representable मान पर round करना उसे बस फेंक देता।

</details>

3. ▢ Stochastic rounding इसे कैसे सँभालता है, और उसके इस्तेमाल के बाद भी Rae et al. ने कौन-सी सीमा बताई?

<details markdown="1"><summary>जाँचें</summary>

Stochastic rounding हमेशा सबसे नज़दीकी मान पर round करने के बजाय ऊपर या नीचे उस संभावना से round करता है जो इस अनुपात में है कि सच्चा मान हर पास के representable मान के कितना क़रीब है, इसलिए छोटा update हर बार फेंके जाने के बजाय कई steps में औसतन बचा रहता है। फिर भी, Rae et al. ने पाया कि वह साधारण mixed-precision training के प्रदर्शन को पूरी तरह वापस नहीं पाता।

</details>

4. ▢ Rae et al. के अनुसार, Gopher के कौन-से model sizes ने activations के साथ parameters के लिए भी bf16 इस्तेमाल किया?

    - a) उनके train किए हर model size ने
    - b) सिर्फ़ 7.1 अरब parameters से छोटे models ने
    - c) सिर्फ़ 7.1B model और 280B Gopher model ने
    - d) किसी ने नहीं; bf16 सभी sizes में सिर्फ़ activations के लिए इस्तेमाल हुआ

<details markdown="1"><summary>जाँचें</summary>

**c)** सिर्फ़ उनके दो सबसे बड़े models ने। 7.1B से छोटे models ने साधारण mixed precision इस्तेमाल किया, fp32 parameters के साथ bf16 activations, जैसा (b) का वर्णन है, इसीलिए (a) और (d) दोनों ग़लत हैं: bf16 activations व्यापक रूप से इस्तेमाल हुए, पर bf16 parameters सिर्फ़ सबसे बड़े दो models के लिए रखे गए।

</details>

## असली दुनिया का अभ्यास

- [ ] खोजें कि आपकी पहुँच वाला कोई training framework fp16 और bf16 के बीच चुनाव कहाँ देता है (कई mixed-precision training के विकल्प के रूप में दोनों गिनाते हैं)। नोट करें कि दस्तावेज़ कहता है कि एक को दूसरे पर कब तरजीह दें, और उसे इस पाठ के dynamic-range तर्क से मिलाकर जाँचें।
- [ ] fp32, fp16 और bf16 का सटीक bit layout (sign, exponent, mantissa) खोजें, और ख़ुद पुष्टि करें कि bf16 और fp32 की exponent चौड़ाई एक है जबकि fp16 की नहीं।
- [ ] कल: आगे देखे बिना, पाठ 16 के लिए एक वाक्य में अनुमान लिखें: यह देखते हुए कि Gopher के दो सबसे बड़े models को सबसे सावधान संख्यात्मक सँभाल की ज़रूरत पड़ी, क्या आप उम्मीद करेंगे कि model size बढ़ने पर loss spikes और अस्थिरताएँ ज़्यादा आम होंगी या कम, और क्यों?

## आगे बढ़ने के लिए

- [पेपर: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
