---
title: "23. ऐसी Metrics जिनका मतलब हो"
description: "Loss checkpoints चुनता है; task metrics फ़ैसले लेती हैं"
type: lesson
---

# पाठ 23. ऐसी Metrics जिनका मतलब हो

**मिशन से संबंध:** "साबित करें कि यह काम किया" मिशन में है। जिस संख्या का आप बचाव न कर सकें वह सबूत नहीं है।
**मुख्य स्रोत:** [पेपर: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., arXiv:2306.05685](https://arxiv.org/abs/2306.05685)
**पूर्व-आवश्यकताएँ:** [पाठ 22](0022-contamination-and-held-out-design.md), [पाठ 12](0012-reading-a-training-run.md)

## वार्म-अप

1. ▢ दो के बजाय तीन splits क्यों?

<details markdown="1"><summary>जाँचें</summary>

किसी सेट के विरुद्ध चुनाव करना उस पर फ़िट होना है। Validation आपके चुनाव को सोख लेता है; test अछूता रहता है ताकि निष्पक्ष अनुमान दे सके।

</details>

2. ▢ 2-अंक का फ़र्क़ पहचानने के लिए लगभग कितने held-out examples?

<details markdown="1"><summary>जाँचें</summary>

हज़ारों। फ़र्क़ के सिकुड़ने पर ज़रूरत वर्गीय रूप से बढ़ती है।

</details>

3. ▢ दो चीज़ों के नाम बताएँ जो loss नहीं देख सकता।

<details markdown="1"><summary>जाँचें</summary>

क्या generations इस्तेमाल लायक हैं, और क्या task के distribution से बाहर की क्षमताएँ बिगड़ी हैं।

</details>

## यह जानें

### Loss metric क्यों नहीं है

Held-out data पर cross-entropy loss सचमुच उपयोगी है: वह सस्ता है, स्थिर है, और run के दौरान देखने की सही चीज़ है। वह यह नापने का तरीक़ा नहीं है कि model आपका काम करता है या नहीं।

Loss एक ख़ास reference continuation के सामने अगले-token की हैरानी मापता है। इसलिए वह अलग शब्दों में कहे सही उत्तर को दंडित करता है और धाराप्रवाह ग़लत को इनाम देता है। बराबर held-out loss वाले दो models उपयोगिता में काफ़ी अलग हो सकते हैं, और दिशा का अनुमान नहीं लगाया जा सकता।

**Checkpoint चुनने के लिए loss इस्तेमाल करें। फ़ैसलों के लिए task metric.**

### Task के आकार के हिसाब से चुनना

| Task का आकार | Metric | किस पर नज़र रखें |
|---|---|---|
| Classification | Accuracy; प्रति-वर्ग precision और recall; F1 | वर्ग असंतुलन accuracy को अर्थहीन बना देता है |
| Extraction | Field पर exact match; spans पर F1 | तुलना से पहले normalise करें |
| Structured output | Schema validity दर, फिर field-स्तर की शुद्धता | दो अलग विफलताएँ, दोनों मापें |
| Code | Tests के विरुद्ध execution | Tests का पास होना, reference जैसा दिखना नहीं |
| खुले-सिरे की generation | Rubric scoring, मानव या model द्वारा आँकी हुई | कठिन मामला; नीचे देखें |
| Retrieval से जुड़ा | Groundedness, citation की सटीकता | धाराप्रवाहता असमर्थित दावे छिपा देती है |

ध्यान दें कि क्या ग़ायब है: जिसका जाँचा जा सकने वाला उत्तर हो, उसके लिए **उत्तर जाँचें।** Code चलाएँ। Schema validate करें। निकाले गए field की तुलना करें। ये सस्ते, वस्तुनिष्ठ हैं, और किसी भी similarity score से कहीं बेहतर।

### सतही-समानता वाली metrics पर

BLEU, ROUGE और उनके रिश्तेदार reference के साथ n-gram का overlap मापते हैं। वे machine translation और summarisation के लिए बनाए गए थे, और instruction-following tasks के लिए कमज़ोर हैं: अलग शब्दों में कहा सही उत्तर बुरा score पाता है, और reference की शब्दावली दोहराने वाला ग़लत उत्तर अच्छा।

उन्हें तभी इस्तेमाल करें जब overlap सचमुच वही चीज़ हो जिसकी आपको परवाह है, और कभी अकेली metric के रूप में नहीं। अगर आप summarisation न होने वाले task पर ROUGE को optimise करते पाएँ ख़ुद को, तो रुकें।

### Structured output: दो विफलताएँ, दो संख्याएँ

JSON या किसी भी schema के लिए, हमेशा दोनों बताएँ:

1. **Validity।** क्या वह parse हुआ और schema को संतुष्ट किया?
2. **शुद्धता।** यह मानते हुए कि वह parse हुआ, क्या values सही हैं?

इन्हें मिला देना छिपा देता है कि आपको कौन-सी समस्या है। 99% validity और 60% शुद्धता वाले model को बेहतर data चाहिए। 60% validity और 95% शुद्धता वाले को format training चाहिए, या serving के समय constrained decoding, जो बिना retraining के समस्या मिटा सकती है।

### Model-as-judge, सावधानी से इस्तेमाल

खुले-सिरे के output के लिए, मज़बूत model से rubric के विरुद्ध score करवाना अक्सर अकेला scalable विकल्प है। यह काम करता है, और इसके दर्ज किए गए biases हैं जिन्हें आपको नियंत्रित करना होगा:

- **Position bias।** Judges जिस response को पहले दिखाया जाए उसे पसंद करते हैं। क्रम को random करके और, pairwise तुलना के लिए, दोनों क्रमों को evaluate करके कम करें।
- **Verbosity bias।** गुणवत्ता से परे लंबे उत्तर ऊँचा score पाते हैं। देखें कि कहीं आपका fine-tune बस ज़्यादा बोलने वाला तो नहीं हो गया।
- **Self-preference।** Judges अपने output जैसे text को पसंद करते हैं।
- **Rubric की संवेदनशीलता।** Rubric के शब्दों में छोटे बदलाव scores को काफ़ी खिसका देते हैं।

अनिवार्य क़दम: **judge को मानव labels के सामने calibrate करें।** 50 से 100 examples ख़ुद score करें, उन्हीं पर judge चलाएँ, और सहमति मापें। अगर सहमति कमज़ोर है, तो judge की संख्याएँ सजावट हैं। अगर अच्छी है, तो आपने उसे scale करने का हक़ कमाया है, और आपके पास एक संख्या है जो बताती है कि उस पर कितना भरोसा करना है।

एक ठोस, मज़बूत setup: base बनाम fine-tuned output की pairwise तुलना, दोनों क्रम, ऐसे rubric के साथ जो उन ख़ास कसौटियों को नाम दे जिनकी आपको परवाह है, win rate के रूप में बताई हुई। Pairwise judging, निरपेक्ष scoring से ज़्यादा भरोसेमंद है, जो बहक जाती है।

### अनिश्चितता बताएँ या कुछ न बताएँ

फैलाव के बिना अकेली संख्या नतीजा नहीं है। न्यूनतम मानक:

- Metric पर **confidence intervals**। अनुपात के लिए, bootstrap या binomial interval इस्तेमाल करें।
- Training configurations की तुलना करते समय **कई seeds**, क्योंकि run-से-run variance अक्सर असर से बड़ा होता है।
- एक ही examples पर **paired comparison** (पाठ 22)।
- वह **n** जिस पर संख्या निकाली गई, साफ़ बताया हुआ।

"71.2 बनाम 70.8" खोज नहीं है। "71.2 ± 2.1 बनाम 70.8 ± 1.9, n=340 पर, तीन seeds" खोज है, और खोज यह है कि आपने कोई फ़र्क़ नहीं पकड़ा।

### Outputs पढ़ें

आपकी metric जो भी हो, हर बार असली generations का नमूना पढ़ें, विफलताओं समेत। Metrics संपीड़ित करती हैं, और जो चीज़ वे संपीड़ित करके हटा देती हैं वह आम तौर पर वही होती है जो आपको जाननी थी: model इनकार करने लगा है, या भूमिका उगलने लगा है, या छाँटने लगा है, या थोड़ा अलग सवाल हल करने लगा है। कोई कुल संख्या यह उजागर नहीं करती। दस मिनट का पढ़ना करता है।

## अभ्यास

1. ▢ दो models का held-out loss एक जैसा है। क्या एक काफ़ी ज़्यादा उपयोगी हो सकता है?

<details markdown="1"><summary>जाँचें</summary>

हाँ। Loss एक reference continuation से सहमति मापता है, इसलिए वह अलग शब्दों में कहे सही उत्तरों को दंडित करता है और धाराप्रवाह ग़लत को इनाम देता है।

बराबर loss, task प्रदर्शन में बड़े फ़र्क़ से मेल खाता है, किसी भी दिशा में। इसीलिए loss checkpoints चुनता है और task metrics फ़ैसले लेती हैं।

</details>

2. ▢ आपका model JSON बनाता है। आप कौन-सी दो संख्याएँ बताते हैं, और एक क्यों नहीं?

<details markdown="1"><summary>जाँचें</summary>

Schema validity दर, और valid outputs में field-स्तर की शुद्धता।

एक मिली-जुली संख्या छिपा देती है कि आपको कौन-सी समस्या है। ऊँची validity के साथ कम शुद्धता data की समस्या है; कम validity के साथ ऊँची शुद्धता formatting की समस्या है जिसे constrained decoding बिना retraining के हल कर सकती है।

</details>

3. ▢ आपके fine-tune का judge score 6.2 से 7.1 हो गया। औसत response लंबाई 90 से 340 tokens हो गई। चिंता?

<details markdown="1"><summary>जाँचें</summary>

हाँ: verbosity bias। Judges गुणवत्ता की परवाह किए बिना लंबे उत्तरों को भरोसेमंद ढंग से पसंद करते हैं, इसलिए उस फ़ायदे का बहुत-सा हिस्सा लंबाई हो सकता है।

इसे नियंत्रित करें: बराबर लंबाई पर तुलना करें, judge को साफ़ निर्देश दें कि लंबाई को अनदेखा करे, या जाँचें कि क्या users सचमुच लंबा output पसंद करते हैं। अकेला score "बेहतर" और "लंबा" में फ़र्क़ नहीं करता।

</details>

4. ▢ code-generation fine-tune को कौन-सी metric सबसे अच्छी तरह आँकती है?

    - a) दी गई reference implementation के विरुद्ध ROUGE
    - b) हर problem के test suite के विरुद्ध execution
    - c) Code tokens पर held-out cross-entropy loss
    - d) पठनीयता और शुद्धता को score करने वाला model judge

<details markdown="1"><summary>जाँचें</summary>

**b)** हर problem के test suite के विरुद्ध execution।

Code की शुद्धता की वस्तुनिष्ठ कसौटी है, इसलिए उसका इस्तेमाल करें। Overlap metrics चलने के बजाय reference जैसा दिखने को इनाम देती हैं; loss में भी वही समस्या है; जब आप बस code चला सकते हैं तो judge अनावश्यक घुमाव है।

</details>

5. ▢ कौन-सा अकेला क़दम model judge पर बड़े पैमाने पर भरोसा करने का हक़ देता है?

<details markdown="1"><summary>जाँचें</summary>

उसे मानव labels के सामने calibrate करना, 50 से 100 examples ख़ुद score करके और उन्हीं items पर judge से सहमति मापकर।

इसके बिना judge की संख्याएँ असत्यापित हैं। इसके साथ, आपके पास औचित्य और भरोसे की मात्रा, दोनों हैं।

</details>

6. ▢ आपका classifier fine-tune 94% accuracy बताता है। यह मानने से पहले कि उसका कोई मतलब है, आपको क्या जानना होगा?

<details markdown="1"><summary>जाँचें</summary>

वर्ग का वितरण। अगर 94% examples एक वर्ग के हैं, तो जो model हमेशा उसी वर्ग का अनुमान लगाए वह 94% पाता है और उसने कुछ नहीं सीखा।

प्रति-वर्ग precision और recall, या संतुलित metric बताएँ। असंतुलित data पर accuracy आम इस्तेमाल की सबसे भ्रामक संख्याओं में से एक है।

</details>

## असली दुनिया का अभ्यास

- [ ] अपनी प्राथमिक metric चुनें और एक अनुच्छेद लिखें कि वह वही क्यों मापती है जिसकी आपको परवाह है। बताएँ कि वह क्या चूकती है।
- [ ] अपनी मौजूदा metric पर confidence interval निकालें। तय करें कि क्या आपका held-out सेट उस तुलना का समर्थन कर सकता है जो आप चाहते हैं।
- [ ] अगर model judge इस्तेमाल कर रहे हैं: 50 examples हाथ से label करें, उन्हीं पर judge चलाएँ, और सहमति बताएँ।
- [ ] कल: बीस असली generations पढ़ें, हर विफलता समेत। लिखें कि metric ने कौन-सी एक बात नहीं बताई।

## आगे बढ़ने के लिए

- [पेपर: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., arXiv:2306.05685](https://arxiv.org/abs/2306.05685)
- [कोड: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
- [पाठ 24. Regression Suite](0024-the-regression-suite.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
