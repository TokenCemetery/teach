---
title: "6. Chinchilla: Compute-Optimal सुधार"
description: "Model का आकार और token count साथ-साथ क्यों बढ़ने चाहिए, और compute budget को token count में कैसे बदला जाए"
type: lesson
---

# पाठ 6. Chinchilla: Compute-Optimal सुधार

**मिशन से संबंध:** "Parameter count और compute budget दिए जाने पर compute-optimal token count निकालें और उसका बचाव Kaplan-शैली के कम-train किए गए विकल्प के सामने करें" "सफलता कैसी दिखती है" का तीसरा बिंदु है। पाठ 5 ने Kaplan et al. की सिफ़ारिश कवर की; यह पाठ उस ज़्यादा व्यापक अध्ययन को कवर करता है जिसने उसे पलट दिया, और उसे लागू करने का हिसाब।
**मुख्य स्रोत:** [पेपर: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
**पूर्व-आवश्यकताएँ:** [पाठ 5](0005-scaling-laws-what-kaplan-predicted.md)

## वार्म-अप

1. ▢ Kaplan et al. के अनुसार, तय compute budget के लिए, सबसे compute-कुशल training का मतलब सबसे बड़ा affordable model तुलनात्मक रूप से कम data पर train करना है, या छोटा model उतने data पर जितना budget देने दे?

<details markdown="1"><summary>जाँचें</summary>

सबसे बड़ा affordable model, तुलनात्मक रूप से कम data पर train किया हुआ और converge होने से पहले रोका हुआ। बड़े models का ज़्यादा sample-efficient होना ही उसे तय budget का सुझाया गया आवंटन बनाता है।

</details>

2. ▢ GPT-3 ने 175-अरब-parameter model को 300 अरब tokens पर train किया। यह लगभग कितने tokens प्रति parameter हुआ?

<details markdown="1"><summary>जाँचें</summary>

लगभग 1.7 tokens प्रति parameter (300 अरब को 175 अरब से भाग देने पर)।

</details>

## यह जानें

### कहीं बड़ा sweep, अलग उत्तर

Hoffmann et al. ने उसी तरह का scaling-law अध्ययन चलाया जैसा Kaplan et al. ने किया था, पर कहीं बड़ा और ज़्यादा सावधानी से नियंत्रित: 400 से ज़्यादा models, 7 करोड़ से 16 अरब से ज़्यादा parameters तक, 5 अरब से 500 अरब tokens के बीच train किए हुए। उस sweep पर scaling law fit करके वे अलग व्यावहारिक नतीजे पर पहुँचे: compute-optimal training के लिए model size और training tokens की संख्या **बराबर** बढ़ानी चाहिए। Compute budget दोगुना करने का मतलब है model size और token count दोनों दोगुने करना, न कि, जैसा Kaplan et al. की सिफ़ारिश का अर्थ निकलता था, अतिरिक्त compute का लगभग सारा हिस्सा बड़े model पर ख़र्च करना।

### वह सन्निकटन जो यह हिसाब संभव बनाता है

दोनों पेपर training run की compute लागत के लिए एक ही मोटा सन्निकटन इस्तेमाल करते हैं: `FLOPs(N, D) ≈ 6ND`, जहाँ `N` parameter count है और `D` training tokens की संख्या। Hoffmann et al. ने model sizes की एक range के लिए इस सन्निकटन को ज़्यादा सटीक FLOP count के विरुद्ध सीधे जाँचा और पाया कि अंतर इतना छोटा है कि उनके नतीजों पर असर नहीं डालता। इसका मतलब है कि compute budget `C`, parameter count `N` और token count `D` तीन स्वतंत्र चुनाव नहीं हैं: कोई भी दो तय करने पर तीसरा `D ≈ C / (6N)` से तय हो जाता है।

### Chinchilla, और headline के पीछे की संख्याएँ

Hoffmann et al. ने एक model, Chinchilla, 70 अरब parameters पर 1.4 खरब tokens पर train किया, उतने ही training compute के साथ जितना Gopher (280-अरब-parameter model) ने इस्तेमाल किया था। यह हर parameter पर लगभग 20 tokens है (1.4 खरब को 70 अरब से भाग देने पर)। दूसरे compute budgets के लिए उनके अपने optimal-allocation अनुमान एक मिलती-जुलती range में आते हैं, हर बार ठीक उसी संख्या पर नहीं: 175-अरब-parameter compute-optimal model के लिए 4.2 खरब से ज़्यादा tokens चाहिए होने का अनुमान है (प्रति parameter लगभग 24), और 280-अरब-parameter वाले के लिए बड़े budget पर लगभग 6.8 खरब tokens (प्रति parameter लगभग 24)। सही निष्कर्ष है "इस पेपर ने जिस range को जाँचा उसमें compute-optimal आवंटन पर लगभग 20 से 25 tokens प्रति parameter", न कि कोई एक सार्वभौमिक स्थिरांक।

इसके बग़ल में रखें तो GPT-3 के 175 अरब parameters 300 अरब tokens पर, इस पाठ के वार्म-अप से लगभग 1.7 tokens प्रति parameter, उस range से कहीं नीचे है। यही अंतर वह है जिसे Chinchilla पेपर का abstract समकालीन बड़े language models को "significantly undertrained" कहकर कहता है: उसी training compute से छोटा model कम loss तक train हो सकता था, या उसी आकार का model कई गुना ज़्यादा data पर train हो सकता था, और दोनों में से कोई भी compute का उस उपयोग से बेहतर इस्तेमाल करता जो असल में हुआ।

### वह नतीजा जिसने सुधार को टिका दिया

Gopher के compute budget पर पर उसके parameter count के एक चौथाई और उसके token count के चार गुना पर train होकर, Chinchilla ने Gopher (280B), GPT-3 (175B), Jurassic-1 (178B) और Megatron-Turing NLG (530B), जिनमें से कई उससे कई गुना बड़े थे, सबको downstream evaluations की चौड़ी range में एकसमान और काफ़ी पीछे छोड़ा, जिसमें MMLU पर तब का state-of-the-art 67.5% भी शामिल था, यानी Gopher से 7 अंक से ज़्यादा ऊपर। Gopher के आकार का एक चौथाई होने से Chinchilla को inference पर चलाना भी काफ़ी सस्ता पड़ा, जो deployment-समय का एक अलग फ़ायदा है जो compute-optimal training उस training-समय के तर्क के ऊपर देती है जो यह पाठ देता है।

## अभ्यास

1. ▢ एक team 13 अरब parameters वाला model train कर रही है और Chinchilla की लगभग 20 से 25 tokens प्रति parameter वाली range में आना चाहती है। इसका मतलब लगभग कितने training tokens हैं?

<details markdown="1"><summary>जाँचें</summary>

लगभग 260 से 325 अरब tokens (13 अरब गुना 20 से 25)। उस range का कोई भी सिरा बचाव करने लायक़ उत्तर है; उससे बहुत बाहर की संख्या, जैसे GPT-3 का 1.7 प्रति parameter वाला अनुपात, नहीं है।

</details>

2. ▢ एक team के पास `1.2 × 10^22` FLOPs का compute budget है और वह 10-अरब-parameter model train करने की योजना बना रही है। `FLOPs(N, D) ≈ 6ND` का इस्तेमाल करके, वह budget लगभग कितने tokens दे सकता है?

<details markdown="1"><summary>संकेत</summary>

`C = 1.2 × 10^22` और `N = 10^10` के साथ `D ≈ C / (6N)` हल करें।

</details>

<details markdown="1"><summary>जाँचें</summary>

लगभग 200 अरब tokens: `1.2 × 10^22 / (6 × 10^10) = 2 × 10^11`, यानी 200 अरब, लगभग 20 tokens प्रति parameter और इस पाठ की दी हुई range के ठीक भीतर।

</details>

3. ▢ तय compute budget के लिए, Kaplan et al. की सिफ़ारिश और Hoffmann et al. के सुधार के बीच व्यावहारिक अंतर को इनमें से कौन-सा सबसे अच्छा बताता है?

    - a) Kaplan budget का ज़्यादातर हिस्सा बड़े model पर, तुलनात्मक रूप से कम data के साथ, ख़र्च करने को कहता है; Hoffmann model size और token count को बराबर बढ़ाने को कहता है
    - b) दोनों पेपर एक ही सिफ़ारिश पर पहुँचते हैं, बस शब्द अलग हैं
    - c) Kaplan कहता है कि model size का loss से कोई संबंध नहीं; Hoffmann कहता है कि सिर्फ़ model size मायने रखता है
    - d) Hoffmann तर्क देता है कि उसी compute पर बड़ा model छोटे model से हमेशा बदतर होता है

<details markdown="1"><summary>जाँचें</summary>

**a)** यही असली अंतर है जिससे यह पाठ और पाठ 5 गुज़रते हैं। (b) दोनों पेपरों के बीच एक असली, व्यावहारिक रूप से अहम असहमति को मिटा देता है। (c) और (d) किसी भी पेपर के दावों का वर्णन नहीं करते।

</details>

4. ▢ GPT-3 ने 175 अरब parameters 300 अरब tokens पर train किए, लगभग 1.7 tokens प्रति parameter। Chinchilla की compute-optimal range, लगभग 20 से 25 tokens प्रति parameter, के हिसाब से GPT-3 अपने आकार के सापेक्ष data पर over-trained के ज़्यादा क़रीब था या under-trained के?

<details markdown="1"><summary>जाँचें</summary>

Under-trained। उसका अनुपात उस range से दस गुना से ज़्यादा नीचे है जिसे Chinchilla के नतीजे compute-optimal बताते हैं, यानी उसी training compute से संभवतः छोटा model कम loss तक train हो सकता था, या वही 175-अरब-parameter model काफ़ी ज़्यादा data पर train हो सकता था।

</details>

## असली दुनिया का अभ्यास

- [ ] 2022 के बाद जारी हुए किसी open model का प्रकाशित parameter count और training-token count खोजें (Llama, Mistral या ऐसे ही दोनों प्रकाशित करते हैं)। उसका tokens-per-parameter अनुपात निकालें और इस पाठ की लगभग 20 से 25 वाली range से तुलना करें।
- [ ] `FLOPs(N, D) ≈ 6ND` का इस्तेमाल करके अनुमान लगाएँ कि GPT-3 के असली training run (175 अरब parameters, 300 अरब tokens) में कितना training compute (FLOPs में) लगा, और अलग से अनुमान लगाएँ कि 4.2 खरब tokens पर compute-optimal 175-अरब-parameter run को कितना compute चाहिए होता। दोनों संख्याओं की तुलना करें।
- [ ] कल: अपनी पसंद का कोई काल्पनिक compute budget चुनें (कोई भी order of magnitude), और काग़ज़ पर उसी budget के लिए Kaplan-शैली का आवंटन (बहुत बड़े model को तरजीह दें, tokens को तुलनात्मक रूप से तय रखें) और Chinchilla-शैली का आवंटन (दोनों को साथ बढ़ाएँ) दोनों निकालें। नतीजे में आई दोनों `(N, D)` जोड़ियाँ अगल-बग़ल लिखें।

## आगे बढ़ने के लिए

- [पेपर: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
- [संसाधन](../RESOURCES.md)

---

चरण 1 और 2 ने तय किया कि model किस पर train होता है और उसे tokenize कैसे किया जाता है; इस चरण ने तय किया कि दिए आकार के लिए उसमें से कितना इस्तेमाल करना है। चरण 4 उस ओर मुड़ता है कि training run उतना compute एक साथ एक से ज़्यादा device पर असल में कैसे लगाता है।

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
