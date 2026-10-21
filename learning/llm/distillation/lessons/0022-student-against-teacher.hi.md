---
title: "22. Student बनाम Teacher"
description: "Teacher से सहमति को task की गुणवत्ता से अलग मापना, एक-एक क्षमता करके"
type: lesson
---

# पाठ 22. Student बनाम Teacher

**मिशन से संबंध:** मिशन आपसे माँगता है कि आप माप सकें कि student ने अपने teacher के मुक़ाबले क्या खोया, और पहला क़दम है "teacher से सहमत है" और "task अच्छी तरह करता है" को एक ही संख्या मानना बंद करना।
**मुख्य स्रोत:** [पेपर: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945), sections 3.2 और 4 से 5
**पूर्व-आवश्यकताएँ:** [पाठ 17](0017-fidelity-and-generalization.md), [पाठ 18](0018-the-imitation-gap.md), [Fidelity](../GLOSSARY.md), [Top-1 agreement](../GLOSSARY.md), [Imitation gap](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 17 ने कहा कि अच्छी तरह generalize करने वाला student फिर भी अपने teacher से असहमत हो सकता है। पाठ ने कहा कि दोनों में से आपको कौन-सा चाहिए, और यह क्या तय करता है?

<details markdown="1"><summary>जाँचें</summary>

यह इस पर निर्भर है कि student किस लिए है। अगर आपको teacher का व्यवहार दोहराया हुआ चाहिए, जैसे ऐसे replacement में जिस पर दूसरे निर्भर हैं, तो fidelity लक्ष्य है। अगर आपको ऐसा model चाहिए जो task अच्छी तरह करे, तो task की गुणवत्ता है, और student किसी दोषपूर्ण teacher से असहमत होकर उसे हरा सकता है। कोई भी दूसरे की जगह नहीं लेता।

</details>

2. ▢ पाठ 18 ने imitation gap दिया। Student सबसे तेज़ किसकी नक़ल करता है, और मानव preference rating किसे पुरस्कृत करती है?

<details markdown="1"><summary>जाँचें</summary>

वह सबसे तेज़ style की नक़ल करता है: धाराप्रवाह, आत्मविश्वास भरे, अच्छी तरह संरचित उत्तर। Preference rating इसे पुरस्कृत करती है कि उत्तर कैसे पढ़ा जाता है, इसलिए student उस पर अच्छा score कर सकता है जबकि क्षमता में पिछड़ा हो। क्षमता की नक़ल धीमी है।

</details>

3. ▢ पाठ 21 ने teacher के scoring pass की लागत आँकी। उस pass से प्रति-token कौन-सी राशि आपको fidelity मापने के लिए भी चाहिए, और उसे इस्तेमाल करने से कौन-सी अतिरिक्त लागत जुड़ती है?

<details markdown="1"><summary>जाँचें</summary>

हर position पर teacher का output distribution (या उसका शीर्ष चुनाव), जो scoring pass पहले से बनाता है। Fidelity मापने का मतलब है teacher को evaluation prompts पर भी चलाना, training के मुक़ाबले एक छोटी अतिरिक्त लागत, क्योंकि evaluation set training set से कहीं छोटा है।

</details>

## यह जानें

### मापने की दो चीज़ें

[Fidelity](../GLOSSARY.md) यह है कि student की predictions उन्हीं inputs पर उसके teacher की predictions को कितनी क़रीब से अनुसरण करती हैं। Task की गुणवत्ता यह है कि student काम कितना अच्छा करता है, सही उत्तर के विरुद्ध आँका हुआ। Stanton et al. दो fidelity metrics परिभाषित करते हैं (section 3.2), और दोनों language model पर position-दर-position लागू होते हैं:

- **[Top-1 agreement](../GLOSSARY.md):** inputs का वह हिस्सा जिन पर student का सबसे ऊँची probability वाला उत्तर teacher का सबसे ऊँची probability वाला उत्तर हो।
- **Average predictive KL:** teacher के distribution से student के distribution तक का औसत KL divergence, हर उत्तर के प्रति संवेदनशील, सिर्फ़ शीर्ष के प्रति नहीं।

पेपर दोनों को classifiers के लिए परिभाषित करता है। उन्हें LLM पर लागू करने का मतलब है held-out prompts के उन्हीं prefixes पर दोनों models के next-token distributions score करना, जो इस track का रूपांतरण है और पेपर ने इसे चलाया नहीं। पहले से तय करें कि कौन-सा prefix इस्तेमाल करेंगे: teacher का text, जो prediction को अलग करता है, या हर model की अपनी generation, जो यह भी मापती है कि दोनों अलग शब्द चुनने के बाद कैसे भटकते हैं।

### वे अलग क्यों हो जाते हैं

Stanton et al. तीन नतीजे देते हैं जो समझाते हैं कि student का agreement और उसकी task की गुणवत्ता स्वतंत्र रूप से क्यों हिल सकते हैं।

पहला, agreement accuracy से बँधा है। उनका उदाहरण (section 3.2): 55 प्रतिशत और 95 प्रतिशत score करने वाले दो स्वतंत्र models अधिकतम 60 प्रतिशत बिंदुओं पर सहमत हो सकते हैं। उन दोनों के बीच मापा गया 60 प्रतिशत agreement distillation के बारे में कुछ नहीं कहता। वे इसी कारण से एक नियंत्रण जोड़ते हैं: ऐसे student को भी मापें जो उसी तरह स्वतंत्र teacher से distil हुआ हो, और दोनों agreements की तुलना करें। अगर दोनों students teacher से लगभग बराबर सहमत हों, तो agreement दोनों के अच्छी तरह generalize करने से आता है, distillation से नहीं।

दूसरा, student अपने teacher को उसकी नक़ल न करके हरा सकता है। CIFAR-100 पर self-distillation में, जहाँ student की architecture teacher जैसी है, student की accuracy teacher की accuracy से ऊपर जा सकती है, जिसे पेपर संभव सिर्फ़ इसलिए बताता है कि distillation चूकता है: सटीक नक़ल बेहतर नहीं कर सकती (sections 4.1 और 4.2)। उस experiment में, जब distillation set छोटा था, fidelity बढ़ाने से student की accuracy घटी।

तीसरा, ज़्यादा fidelity हमेशा ऊँची accuracy नहीं ख़रीदती, तब भी जब teacher कहीं बेहतर हो। Section 5 में वे CIFAR-100 को बाँटते हैं, एक student को teacher के अपने training आधे (s0) पर और एक को अनदेखे data (s1) पर distil करते हैं। अनदेखे data वाला student teacher से ज़्यादा सहमत है, फिर भी teacher के data वाले student की test accuracy ऊँची है। पेपर का अपना सार है कि fidelity का फ़ायदा teacher की accuracy दोहराने तक नहीं पहुँचा।

वे यह भी बताते हैं कि ऊँची fidelity तक पहुँचना ही कठिन है। MNIST पर LeNet-5 के साथ student 99 प्रतिशत से ऊपर top-1 test agreement तक पहुँचा (section 4.1)। CIFAR-100 पर ResNet-56 students के साथ, उनका बताया सबसे अच्छा test agreement लगभग 86 प्रतिशत है, mixup augmentation के साथ (section 5)।

दायरा: ये ज़्यादातर image-classification experiments हैं, appendix में text classifiers के साथ। वे दिखाते हैं कि दोनों राशियाँ अलग की जा सकती हैं। वे किसी LLM के माप नहीं हैं, और उनसे कोई agreement आँकड़ा आपके लिए लक्ष्य नहीं है।

### Preference rating ग़लत स्थानापन्न क्यों है

Gudibande et al. ने 7B और 13B parameters के LLaMA models को ChatGPT के outputs पर fine-tune किया और दो तरह के evaluation की तुलना की। Crowdworkers ने imitation models के लगभग 70 प्रतिशत outputs को ChatGPT के बराबर या बेहतर आँका (उनकी Figure 1)। लक्षित benchmarks पर, imitation models ने उन tasks के लिए base model और ChatGPT के बीच के फ़ासले का कम या कुछ भी नहीं पाटा जिन्हें imitation data ने ज़्यादा कवर नहीं किया था।

उनकी Table 1 इसे हर क्षमता के हिसाब से दिखाती है, Natural Questions को task लेकर:

| Model | Imitation data | NQ score |
|---|---|---|
| LLaMA 7B | कोई नहीं | 17 |
| LLaMA 7B | ShareGPT-Mix (broad) | 10 |
| LLaMA 7B | NQ-Synthetic (targeted) | 22 |
| LLaMA 13B | कोई नहीं | 20 |
| LLaMA 13B | ShareGPT-Mix (broad) | 15 |
| LLaMA 13B | NQ-Synthetic (targeted) | 27 |
| ChatGPT | लागू नहीं | 31 |

Broad imitation data ने दोनों आकारों का NQ score घटाया, और targeted data ने उसे 13B पर teacher के चार अंक के भीतर तक उठा दिया। Rating फ़ासले की पेपर की व्याख्या style है: imitation models धाराप्रवाह और आत्मविश्वासी हैं, और domain की विशेषज्ञता या तथ्य जाँचने के समय के बिना rater ग़लतियाँ चूक जाता है। उन्होंने अपनी Table 2 में यह भी पाया कि imitation data जोड़ने के साथ outputs का style ChatGPT के style से और मिलता-जुलता होता गया, जो वही असर है जो output text पर मापा गया।

माप के लिए सबक़ यह नहीं है कि preference ratings बेकार हैं। वह यह है कि कोई एक समग्र संख्या, चाहे rating हो या औसत accuracy, उन क्षमताओं को छिपा देती है जो उलटी दिशाओं में चली गईं।

### एक-एक क्षमता

इसलिए माप एक grid है। वे क्षमताएँ चुनें जिनकी आपको परवाह है, जैसे छोटे तथ्यात्मक उत्तर, अंकगणित, code, instruction following और refusals। हर एक के लिए दो columns निकालें: उस तरह के prompts पर teacher से agreement, और उन्हीं prompts पर सही उत्तर के विरुद्ध task की गुणवत्ता। Student कुछ पंक्तियों में पहले पर ऊँचा और दूसरे पर नीचा दिख सकता है और दूसरी पंक्तियों में उलटा, और पैटर्न ही बताता है कि क्या transfer हुआ और क्या नहीं।

| क्षमता | Teacher से agreement | Task की गुणवत्ता, student | Task की गुणवत्ता, teacher | पढ़त |
|---|---|---|---|---|
| काल्पनिक पंक्ति A | ऊँचा | Teacher के क़रीब | ऊँची | अच्छी तरह नक़ल हुई |
| काल्पनिक पंक्ति B | ऊँचा | Teacher से बहुत नीचे | ऊँची | Style नक़ल हुआ, क्षमता खो गई |
| काल्पनिक पंक्ति C | नीचा | Teacher से ऊपर | मध्यम | असहमत है, और teacher कमज़ोर था |

पंक्तियाँ grid को पढ़ने का उदाहरण हैं, किसी स्रोत का data नहीं। पाठ 23 छूटा हुआ column जोड़ता है, बिना distillation के train हुआ उसी आकार का model, जिसे यह grid अकेले नहीं आँक सकता।

## अभ्यास

1. ▢ एक teacher किसी task पर 90 प्रतिशत accuracy score करता है। एक स्वतंत्र model 70 प्रतिशत। दोनों का अधिकतम top-1 agreement क्या हो सकता है, और student के agreement score को पढ़ने के लिए इसका क्या मतलब है?

<details markdown="1"><summary>संकेत</summary>

दो models किसी बिंदु पर तभी सहमत हो सकते हैं जब दोनों सही हों या दोनों ग़लत। पेपर के 55 और 95 वाले उदाहरण की तरह निकालें कि accuracies सबसे ज़्यादा कितना overlap होने देती हैं।

</details>

<details markdown="1"><summary>जाँचें</summary>

अधिकतम 80 प्रतिशत, क्योंकि 20-अंक का accuracy फ़ासला उन्हें कम से कम 20 प्रतिशत बिंदुओं पर असहमत होने पर मजबूर करता है। इसलिए जिस student की accuracy 70 प्रतिशत है वह इस teacher के साथ 80 प्रतिशत से ऊपर agreement नहीं दिखा सकता, और 75 प्रतिशत agreement का मतलब 88 प्रतिशत वाले student के लिए उसी आँकड़े से अलग है। निष्कर्ष निकालने से पहले student के agreement की तुलना पेपर के नियंत्रण वाले स्वतंत्र student के agreement से करें।

</details>

2. ▢ एक student का सामान्य chat prompts पर अपने teacher के साथ 94 प्रतिशत top-1 agreement है और multi-step अंकगणित prompts पर 61 प्रतिशत। Teacher की अंकगणित accuracy 78 प्रतिशत है। Student के अंकगणित के बारे में कुछ कहने से पहले आप आगे क्या मापेंगे?

<details markdown="1"><summary>संकेत</summary>

Agreement की संख्या बताती है कि दोनों कितनी बार मेल खाते हैं, यह नहीं कि कोई भी कितनी बार सही है।

</details>

<details markdown="1"><summary>जाँचें</summary>

उन्हीं prompts पर सही उत्तरों के विरुद्ध student की अंकगणित accuracy, और teacher की प्रति-prompt सहीपन। अगर student की accuracy 61 प्रतिशत है और teacher की 78 प्रतिशत, तो फ़ासला क्षमता का नुक़सान है। अगर दोनों मुख्यतः वहाँ असहमत हैं जहाँ teacher ग़लत है, तो student ठीक हो सकता है। Chat पर 94 प्रतिशत सिर्फ़ यह कहता है कि style transfer हुआ, जिसकी imitation gap भविष्यवाणी करता है।

</details>

3. ▢ कौन-सा नतीजा सबसे सीधे दिखाता है कि fidelity और task की गुणवत्ता अलग हो सकती हैं?

    - a) Student के inputs पर भारी augmentation लगाने के साथ teacher से उसका agreement गिर गया।
    - b) ज़्यादा distillation data पर train हुआ student अपने teacher से ऊँचे test agreement तक पहुँचा।
    - c) Teacher की architecture वाला student किसी data आकार पर teacher की accuracy तक पहुँचा।
    - d) अनदेखे data से distil हुआ student अपने teacher से ज़्यादा सहमत था पर कम सटीक था।

<details markdown="1"><summary>जाँचें</summary>

d). यह section 5 का s1 बनाम s0 नतीजा है: ऊँची fidelity के साथ कम test accuracy। b) data के साथ fidelity का बढ़ना दिखाता है, जो अपेक्षित है और दोनों को अलग नहीं करता। c) अकेली accuracy के बारे में कथन है। a) इस बारे में नतीजा है कि augmentation के तहत agreement कैसे गिरता है, जो task-गुणवत्ता की तुलना के बिना fidelity का बदलाव बताता है।

</details>

4. ▢ एक model card कहता है कि distilled 3B model "मानव raters द्वारा 70B जितना ही अच्छा आँका गया है"। Gudibande et al. का इस्तेमाल करके, दो अनुवर्ती सवाल सूचीबद्ध करें जो आप यह मानने से पहले पूछेंगे कि student ने 70B की क्षमताएँ बनाए रखीं।

<details markdown="1"><summary>जाँचें</summary>

Raters ने कौन-से prompts देखे, और क्या कोई rater तथ्य या code जाँच सकता था, क्योंकि style ऐसी rating जीत सकता है जो क्षमता नहीं जीतती। और student targeted प्रति-क्षमता benchmarks पर teacher और बिना distil किए base, दोनों के विरुद्ध क्या score करता है, जिसमें वे tasks भी शामिल हैं जिन्हें distillation data ने मुश्किल से कवर किया। जो rating benchmarks से मेल खाए वह सबूत है। अकेली rating नहीं है।

</details>

5. ▢ पाठ 19 ने capacity कवर की। एक student आसान prompts के 97 प्रतिशत पर और कठिन वालों के 52 प्रतिशत पर अपने teacher का top-1 उत्तर मिलाता है। एक पढ़त बताएँ जो capacity gap से मेल खाती है और एक जिसे उसकी ज़रूरत नहीं।

<details markdown="1"><summary>जाँचें</summary>

मेल खाती है: student में कठिन inputs पर teacher के व्यवहार को model करने की capacity नहीं है, इसलिए फ़ासला वहाँ केंद्रित है जहाँ teacher सबसे ज़्यादा काम करता है। ज़रूरत नहीं: distillation data में कठिन prompts कम हैं, इसलिए student को वहाँ थोड़ा signal मिला, और उन पर ज़्यादा data मदद करता। दोनों अलग उपाय बताती हैं, इसलिए run की प्रति में कठिन-prompt data जोड़कर और दोबारा मापकर परखें।

</details>

## असली दुनिया का अभ्यास

- [ ] दो छोटे open models चुनें जो tokenizer साझा करते हों। 50 prompts पर, हर prompt के लिए एक चुने position पर हर model का next-token शीर्ष चुनाव दर्ज करें और गिनें कि वे कितनी बार मेल खाते हैं।
- [ ] Gudibande et al. पेपर खोलें और Table 1 ढूँढें। एक वाक्य में लिखें कि broad-coverage पंक्तियाँ औसत score पढ़ने के बारे में क्या कहती हैं।
- [ ] कल: बिना नोट्स के अपने किसी project के लिए इस पाठ का क्षमता grid बनाएँ, दोनों columns के साथ, और उस क्षमता का नाम लें जहाँ आप उम्मीद करते हैं कि agreement और गुणवत्ता सबसे ज़्यादा अलग होंगे।

## आगे बढ़ने के लिए

- [आकार तय करना और मापना शीट](../reference/sizing-and-measuring.md)
- [पेपर: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945), sections 3.2 और 5
- [पेपर: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717), sections 4.2 और 4.4
- [Evals ट्रैक](../../evals/): वह track जो इस grid का task-गुणवत्ता वाला पक्ष बनाना सिखाता है
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
