---
title: "5. Scaling Laws: Kaplan ने क्या अनुमान लगाया"
description: "अनुभव-आधारित power law से training run का loss उसकी क़ीमत चुकाने से पहले अनुमान लगाया जा सकता है, और compute budget कैसे ख़र्च करें इस बारे में उसने क्या बताया"
type: lesson
---

# पाठ 5. Scaling Laws: Kaplan ने क्या अनुमान लगाया

**मिशन से संबंध:** "Parameter count और compute budget दिए जाने पर compute-optimal token count निकालें और उसका बचाव Kaplan-शैली के कम-train किए गए विकल्प के सामने करें" "सफलता कैसी दिखती है" का तीसरा बिंदु है। यह पाठ कवर करता है कि Kaplan et al. ने क्या पाया और क्या सुझाया; पाठ 6 उस सुधार को कवर करता है जिसने सिफ़ारिश बदल दी।
**मुख्य स्रोत:** [पेपर: "Scaling Laws for Neural Language Models", Kaplan et al., 2020](https://arxiv.org/abs/2001.08361)
**पूर्व-आवश्यकताएँ:** [पाठ 4](0004-sentencepiece-and-the-vocabulary-size-tradeoff.md)

## वार्म-अप

1. ▢ एक अक्ष बताइए जिस पर बड़ी tokenizer vocabulary छोटी से बदतर है।

<details markdown="1"><summary>जाँचें</summary>

बड़ी vocabulary का मतलब बड़ी embedding और output-projection table है (सीधे parameter count), और वह training signal को ज़्यादा अलग tokens में पतला फैलाती है, इसलिए उसी corpus पर हर पास में कोई एक ख़ास token कम बार दिखता है।

</details>

## यह जानें

### Scaling law असल में क्या है

इस संदर्भ में **scaling law** अनुभव-आधारित power-law संबंध है: model का held-out loss model size, dataset size या training compute के फलन के रूप में सहजता से घटता है, इतनी चौड़ी range में कि वह अनुमान लगाने के काम आ सके। Kaplan et al. ने ठीक यही fit किया, और पाया कि loss इन तीनों राशियों में से हर एक के साथ अलग-अलग power law की तरह बदलता है, ऐसे रुझानों में जो पैमाने के सात से ज़्यादा order of magnitude तक फैले हैं। दूसरे architectural चुनाव, जैसे तय parameter budget को width और depth में कैसे बाँटें, तुलनात्मक रूप से कम मायने रखते निकले, एक चौड़ी range के भीतर, एक बार model size का हिसाब रख लेने पर।

Scaling law का व्यावहारिक मूल्य पूर्वानुमान है: अगर loss, model size, dataset size और compute के विरुद्ध एक सहज, fit किए हुए curve का पालन करता है, तो team compute ख़र्च करके run चलाने से पहले मोटे तौर पर अनुमान लगा सकती है कि दिए आकार और budget का training run कितना अच्छा प्रदर्शन करेगा, बजाय इसके कि बाद में ही पता चले।

### बड़े models हर token से ज़्यादा सीखते हैं

Kaplan et al. के केंद्रीय नतीजों में से एक यह है कि बड़े models कहीं ज़्यादा sample-efficient होते हैं: किसी तय loss तक पहुँचने के लिए, बड़े model को उतना ही loss पाने के लिए छोटे model के मुक़ाबले कम data देखना पड़ता है। इसे loss, compute, और उन दो चीज़ों के बीच के उनके fit किए संबंधों के साथ जोड़ें जो compute ख़रीदता है (बड़ा model, या उसे train करने के लिए ज़्यादा data), तो इसका एक ख़ास उत्तर निकलता है कि तय compute budget कैसे ख़र्च करें: सबसे compute-कुशल training का मतलब है बहुत बड़े model को तुलनात्मक रूप से कम data पर train करना, और उस data पर converge होने से काफ़ी पहले रुक जाना, बजाय इसके कि छोटे model को ज़्यादा data पर converge होने तक train किया जाए।

### व्यवहार में वह सिफ़ारिश कैसी दिखी

इस नतीजे ने तय किया कि बड़े models की एक पीढ़ी असल में कैसे train हुई: parameter count को आक्रामक रूप से बढ़ाएँ, और token count को तुलनात्मक रूप से लगभग तय रखें या सिर्फ़ मामूली बढ़ाएँ। उदाहरण के लिए, GPT-3 ने 175-अरब-parameter model को 300 अरब tokens पर train किया। यह पाठ उस संख्या को यहीं बिना और टिप्पणी के छोड़ देता है; पाठ 6 उस पर सीधे लौटता है, जब तुलना के लिए दूसरा scaling law मौजूद होगा।

## अभ्यास

1. ▢ Loss के model size के साथ "power law की तरह scale होने" का, Kaplan et al. के अर्थ में, ठीक-ठीक मतलब क्या है?

    - a) Model size में हर तय बढ़ोतरी पर loss ठीक उतनी ही तय मात्रा से घटता है
    - b) Loss fit किए हुए curve का पालन करते हुए सहजता से घटता है, model sizes की चौड़ी range में टिकते हुए, और यही उसका पूर्वानुमान संभव बनाता है
    - c) Model जब काफ़ी बड़ा हो जाता है तो loss शून्य हो जाता है
    - d) Loss सिर्फ़ model size पर निर्भर करता है और training data की मात्रा पर बिल्कुल नहीं

<details markdown="1"><summary>जाँचें</summary>

**b)** पर्याप्त सहज power-law fit, जिसे इतने order of magnitude में परखा गया हो कि उससे अनुमान लगाया जा सके। (a) रैखिक संबंध का वर्णन है, power law का नहीं। (c) का दावा पेपर में कहीं नहीं है। (d) पेपर के अपने अलग नतीजे का खंडन करता है, जो dataset size के साथ एक scaling law का है।

</details>

2. ▢ Kaplan et al. के अनुसार, तय लक्ष्य loss तक कम training data से कौन पहुँचता है: बड़ा model या छोटा?

<details markdown="1"><summary>जाँचें</summary>

बड़ा model। बड़े models ज़्यादा sample-efficient होते हैं, यानी उन्हें उसी loss तक पहुँचने के लिए कम data चाहिए जिस तक छोटे model को ज़्यादा data चाहिए।

</details>

3. ▢ तय compute budget और Kaplan et al. के नतीजों को देखते हुए, उनका विश्लेषण किस आवंटन की सिफ़ारिश करता है: तुलनात्मक रूप से कम data पर train हुआ और converge होने से काफ़ी पहले रोका गया बहुत बड़ा model, या छोटा model जो budget जितना data देने दे उस पर converge होने तक train हुआ?

<details markdown="1"><summary>संकेत</summary>

यह सीधे "बड़े models ज़्यादा sample-efficient होते हैं" को तय compute budget के साथ जोड़ने से निकलता है: data पर ख़र्च हुआ compute वह compute है जो model size पर ख़र्च नहीं हुआ, और पेपर ने पाया कि compute के इन दो उपयोगों में से एक का फल दूसरे से ज़्यादा मिला।

</details>

<details markdown="1"><summary>जाँचें</summary>

तुलनात्मक रूप से कम data पर train हुआ बहुत बड़ा model, जिसे converge होने से पहले रोका गया। तय budget में सबसे compute-कुशल training के लिए Kaplan et al. की अपनी बताई सिफ़ारिश यही है।

</details>

## असली दुनिया का अभ्यास

- [ ] Kaplan पेपर के एक-दो साल के भीतर (2020 से लगभग 2022) जारी हुए दो-तीन जाने-माने models का parameter count और बताया गया training-token count खोजें। नोट करें कि parameter counts बढ़ने के बावजूद उनके token counts लगभग तय रहे या नहीं, जो इस पाठ की सिफ़ारिश मानने पर दिखता।
- [ ] Kaplan पेपर का abstract (ऊपर linked) एक बार फिर पढ़ें और एक वाक्य में बताएँ कि training run के लिए "convergence से काफ़ी पहले रुकना" का क्या मतलब है: आगे और training करने से असल में क्या मिलता, जिसके बारे में यह सिफ़ारिश कहती है कि वह अपने compute के लायक़ नहीं है?
- [ ] कल: पाठ 6 को आगे देखे बिना, एक वाक्य में अनुमान लिखें: इसे देखते हुए कि dataset बनाना (इस track का चरण 1) महँगा और बढ़ाने में धीमा है, और सिर्फ़ parameter count और accelerators जोड़कर बढ़ाना तुलनात्मक रूप से आसान है, कौन-सा व्यावहारिक दबाव असली training runs को Kaplan की सिफ़ारिश की ओर उससे भी ज़्यादा धकेल सकता था जितना अकेले loss curves ठहरातीं?

## आगे बढ़ने के लिए

- [पेपर: "Scaling Laws for Neural Language Models", Kaplan et al., 2020](https://arxiv.org/abs/2001.08361)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
