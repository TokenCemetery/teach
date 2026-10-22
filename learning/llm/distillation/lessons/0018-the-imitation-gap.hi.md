---
title: "18. Imitation Gap"
description: "किसी मज़बूत model की नक़ल उसकी क्षमता की तुलना में उसका style कहीं तेज़ी से क्यों उतार लेती है"
type: lesson
---

# पाठ 18. Imitation Gap

**मिशन से संबंध:** मिशन आपसे माँगता है कि आप अनुमान लगाएँ कि student क्या उठाएगा और क्या नहीं, और "teacher के बराबर" वाले दावे की समीक्षा करें, यानी जानें कि student अपने teacher जैसा कैसे दिख सकता है जबकि उसके पास वह नहीं होता जो teacher जानता है।
**मुख्य स्रोत:** [पेपर: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717), sections 1 और 4
**पूर्व-आवश्यकताएँ:** [पाठ 10](0010-distilling-from-generated-data.md), [पाठ 17](0017-fidelity-and-generalization.md), [Imitation gap](../GLOSSARY.md), [Synthetic data](../GLOSSARY.md), [Fidelity](../GLOSSARY.md)

## वार्म-अप

1. ▢ Alpaca और Self-Instruct किस तरह training set बनाते हैं, और student को teacher से क्या मिलता है?

<details markdown="1"><summary>जाँचें</summary>

Teacher model instructions और responses generate करता है, और student उस text पर fine-tune होता है। उसे सिर्फ़ teacher का decode किया text मिलता है, कोई logits नहीं।

</details>

2. ▢ पाठ 17 कहता है कि task accuracy, teacher से agreement की जगह नहीं ले सकती। उलटा जोखिम क्या है: क्या student outputs पर अपने teacher से सहमत हो सकता है और फिर भी उसकी क्षमता से वंचित रह सकता है?

<details markdown="1"><summary>जाँचें</summary>

Agreement उन inputs पर मापा जाता है जिन्हें आप परखते हैं, इसलिए वह सिर्फ़ उन्हीं inputs के लिए बोलता है। Student सामान्य अनुरोधों पर teacher की phrasing से मेल खा सकता है और उन tasks पर विफल हो सकता है जिन्हें training data ने मुश्किल से कवर किया, यही वह मामला है जिसे यह पाठ जाँचता है।

</details>

3. ▢ पाठ 12 कहता है कि मात्रा ख़राब examples को ठीक नहीं करती। एक चीज़ बताएँ जो teacher-generated data की और मात्रा student को नहीं दे सकती।

<details markdown="1"><summary>जाँचें</summary>

वह ज्ञान जो student की अपनी pretraining ने उसे नहीं दिया। और examples format और व्यवहार सिखा सकते हैं, पर वे उसकी भरपाई सस्ते में नहीं कर सकते जो base model ने कभी सीखा ही नहीं। यह दावा इस पाठ का मूल है।

</details>

## यह जानें

### Setup

Gudibande et al. "model imitation" का अध्ययन करते हैं: किसी proprietary model से उसकी API के ज़रिए outputs का dataset इकट्ठा करें और उस पर किसी open model को fine-tune करें। वे ChatGPT की नक़ल 1.5B से 13B parameters के models (GPT-2 1.5B, LLaMA 7B और 13B) और 0.3M से 150M tokens के imitation data के साथ करते हैं। Student सिर्फ़ text देखता है, इसलिए यह बिना logits वाला sequence-level distillation है।

तर्क के लिए दो तरह की नक़ल मायने रखती है:

| प्रकार | वह किसकी नक़ल करता है | उनका data |
|---|---|---|
| Local imitation | एक task या domain | NQ-synthetic: 10 जोड़ों के seed से ChatGPT द्वारा generate किए 6,000 प्रश्न-उत्तर जोड़े, Natural Questions की शैली में |
| Broad imitation | व्यवहार का पूरा दायरा | ShareGPT-Mix: ShareGPT से लगभग 50K deduplicated संवाद, साथ में HC3 से ChatGPT के लगभग 27K responses और Discord ChatGPT bots के 10K examples |

### मानव raters ने क्या देखा

Crowd workers ने हर imitation model की ChatGPT से blind pairwise तुलनाएँ चलाईं, 255 held-out prompts पर लगभग 70 workers के साथ। Imitation models के लगभग 70% outputs को ChatGPT के बराबर या बेहतर आँका गया (Figure 1 का caption)। GPT-4 को judge बनाने पर वही रुझान दिखे। उन ratings पर imitation models उस model के क़रीब दिखे जिसकी उन्होंने नक़ल की।

Ratings संतृप्त भी हुईं: ज़्यादा imitation data ने उन्हें बढ़ाना बंद कर दिया (section 4.2)।

### Benchmarks ने क्या देखा

फिर लेखकों ने लक्षित स्वचालित evaluations चलाए: MMLU (5-shot), Natural Questions (3-shot) और HumanEval (0-shot)। वे बताते हैं कि मापे गए हर benchmark पर, broad-imitation models अपने base models से बेहतर नहीं हुए, या घट गए, भले imitation data बढ़ा (section 4.3, Figure 4)।

Task-विशिष्ट मामला वह है जहाँ यह काम किया। Table 1 से Natural Questions accuracy:

| Model | कोई imitation नहीं | ShareGPT-Mix पर train (broad) | NQ-synthetic पर train (local) | ChatGPT |
|---|---|---|---|---|
| LLaMA 7B | 17 | 10 | 22 | 31 |
| LLaMA 13B | 20 | 15 | 27 | 31 |

Broad imitation ने accuracy घटाई और local imitation ने बढ़ाई, जिस एक task को निशाना बनाया उस पर फ़ासले का बड़ा हिस्सा पाटते हुए। लेखकों का निष्कर्ष है कि किसी एक विशिष्ट व्यवहार को distil करना, ChatGPT की क्षमताओं से व्यापक रूप से मेल खाने से कहीं ज़्यादा संभव है। उन्होंने यह भी पाया कि ShareGPT-Mix का और data पर training ने base model के मुक़ाबले कुछ evaluations को नुक़सान पहुँचाया, जिसका कारण वे संवादात्मक fine-tuning data और benchmarks के बीच distribution shift बताते हैं, और वे इसे अनसुलझा चिह्नित करते हैं कि regularisation या pretraining data मिलाने से यह ठीक होगा या नहीं।

### Ratings और benchmarks असहमत क्यों हैं

पेपर का जवाब है कि imitation models style सीखते हैं, content नहीं। Table 2, 20M, 80M और 150M tokens पर train हुए imitation models के outputs की तुलना base LLaMA और ChatGPT के दूसरे sample से करती है:

| Metric | Base LLaMA | 20M | 150M | ChatGPT का दूसरा sample |
|---|---|---|---|---|
| अगर ChatGPT सूची output करे, तो क्या model भी करता है? | 13% | 50% | 81% | 83% |
| GPT-4 के अनुसार आधिकारिक tone वाले outputs | 57% | 99% | 98% | 98% |
| लंबाई का ChatGPT के output की लंबाई से Pearson correlation | -0.11 | 0.51 | 0.62 | 0.67 |

पेपर की तालिका में 80M column भी है, जो यहाँ छोड़ा गया है। इन style मापों पर imitation models उस score के क़रीब पहुँचते हैं जो ChatGPT का दूसरा उत्तर पाता है। तथ्यात्मकता पर वे कमज़ोर बने रहते हैं। पेपर की Figure 2 एक imitation उत्तर दिखाती है जिसमें ChatGPT जैसी संरचना है और जो पूरी तरह ग़लत है, आत्मविश्वास भरे tone में।

लेखकों का विवरण कि raters ने इसे क्यों चूका: domain की विशेषज्ञता या काफ़ी समय के बिना crowd workers आत्मविश्वास भरे, अच्छी तरह संरचित उत्तरों से धोखा खा सकते हैं। वे evaluation के लिए दो सबक़ निकालते हैं। Domain experts या कठिन prompts इस्तेमाल करें, और ध्यान दें कि judge के रूप में GPT-4 ने वही पूर्वाग्रह दिखाया।

### Scaling क्या देती है और क्या नहीं

यही वह दावा है जिसे ठीक-ठीक समझना है। लेखक कहते हैं कि मौजूदा तरीक़ों से फ़ासला या तो imitation data की भारी-भरकम मात्रा से पाटा जा सकता है या ज़्यादा सक्षम base model से। दूसरे आधे के लिए उनका सबूत: base model का आकार बढ़ाने से स्वचालित benchmarks लगातार सुधरे, जबकि imitation data बढ़ाने से थोड़ा सुधार या गिरावट मिली (Figure 4)। उनका निष्कर्ष है कि ज़्यादा लाभ वाला क़दम बेहतर base model है।

दो शर्तें मायने रखती हैं। "imitation data की भारी-भरकम मात्रा" वाला हिस्सा एक तर्क है: वे कहते हैं कि ChatGPT से व्यापक रूप से मेल खाने के लिए pretraining के पैमाने के क़रीब का dataset चाहिए होगा, और ध्यान दिलाते हैं कि अस्पष्ट है कि वह करना सार्थक है या नहीं। उन्होंने उसे चलाया नहीं। और base model का आकार base model की गुणवत्ता का प्रॉक्सी है, जो बात उनका अपना footnote कहता है। सेटिंग भी 2023 के LLaMA और GPT-2 base models की ChatGPT की नक़ल है, इसलिए आकारों को मौजूदा न मानें।

### क्या transfer होता है

पेपर यह भी बताता है कि student क्या उठाता है। RealToxicityPrompts पर imitation data बढ़ने के साथ imitation models कम toxic हुए, जिसे लेखक model के उसी तरह परहेज़ करना सीखने के रूप में पढ़ते हैं जैसे ChatGPT करता है (Figure 5)। वे निष्कर्ष निकालते हैं कि नक़ल तब असरदार है जब आपके पास मज़बूत base model हो और आप fine-tuning data को annotate करने से बचना चाहें। Student वे व्यवहार विरासत में पाता है जो teacher को दिखाने के लिए train किया गया था, जिनमें refusal के पैटर्न भी हैं, ज्ञान के मुक़ाबले कहीं सस्ते में।

### लेखकों की बताई सावधानियाँ

वे तीन नाम लेते हैं: ChatGPT के evaluation scores अज्ञात pretraining set में contamination से फूले हो सकते हैं, उन्होंने सिर्फ़ supervised imitation इस्तेमाल की, RLHF या constitutional तरीक़े नहीं, और उन्होंने सरल data संग्रह इस्तेमाल किया। एक और सावधानी मेरी है: evaluation ने coding और non-English prompts छाँटने के बाद 255 prompts इस्तेमाल किए, इसलिए rating का नतीजा "ChatGPT की गुणवत्ता" से संकरा है।

## अभ्यास

1. ▢ Table 1 से, local imitation LLaMA 13B और LLaMA 7B के लिए Natural Questions पर ChatGPT से फ़ासले का कितना हिस्सा पाटती है, और broad imitation ने क्या किया?

<details markdown="1"><summary>जाँचें</summary>

13B के लिए फ़ासला 31 घटा 20, यानी 11 है, और NQ-synthetic 7 अंक जोड़ता है, उसका लगभग 64%। 7B के लिए फ़ासला 14 है और वह 5 जोड़ता है, लगभग 36%। Broad ShareGPT-Mix imitation ने दोनों में accuracy घटाई, 7B के लिए 7 अंक और 13B के लिए 5। ये एक benchmark पर NQ संख्याएँ हैं, सारे tasks के बारे में कथन नहीं।

</details>

2. ▢ Crowd workers ने imitation models को ChatGPT के क़रीब क्यों आँका जबकि benchmarks ने थोड़ा ही फ़ायदा दिखाया?

    - a) Raters हर model की पहचान जानते थे
    - b) Raters हर दावा स्वतंत्र रूप से जाँचते थे
    - c) Raters उत्तर की सरासर लंबाई को पसंद करते थे
    - d) Raters आत्मविश्वास भरे चमकदार style को पुरस्कृत करते थे

<details markdown="1"><summary>जाँचें</summary>

**d)** पेपर कहता है कि imitation models ChatGPT का style नक़ल करते हैं, और domain की विशेषज्ञता या तथ्य जाँचने के समय के बिना raters उससे धोखा खा सकते हैं। (b) उसका उलटा है जो हुआ। (c) पेपर की व्याख्या नहीं है, हालाँकि models के output की लंबाई ChatGPT की लंबाई से correlated थी। (a) ग़लत है: तुलना blind थी।

</details>

3. ▢ एक टीम 7B model को ChatGPT-शैली के 200K और संवादों पर fine-tune करती है और crowd ratings से फ़ायदा बताती है। Model teacher के बराबर है, इस पर विश्वास करने से पहले आप कौन-सी दो चीज़ें माँगते हैं?

<details markdown="1"><summary>संकेत</summary>

सोचें कि पेपर ने किस तरह का माप ratings से अलग पाया, और tasks में क्या ग़ायब था।

</details>

<details markdown="1"><summary>जाँचें</summary>

उन tasks पर लक्षित स्वचालित benchmarks माँगें जिन्हें training data ज़्यादा कवर नहीं करता, जैसे तथ्यात्मक ज्ञान, coding या reasoning, fine-tuning से पहले के base model के विरुद्ध। पूछें कि raters कौन थे और क्या किसी के पास domain की विशेषज्ञता या तथ्य जाँचने का समय था। पेपर की खोज है कि ratings बढ़ सकती हैं जबकि benchmarks स्थिर रहें या गिरें। अकेली ratings सिर्फ़ यह साबित करती हैं कि style transfer हो गया।

</details>

4. ▢ आप एक निश्चित बजट या तो दस लाख और broad teacher-लिखित examples पर ख़र्च कर सकते हैं या दोगुने आकार के base model पर जाने पर। पेपर का सबूत क्या सुझाता है, और क्या नहीं दिखाता?

<details markdown="1"><summary>जाँचें</summary>

अपने experiments में, base model को scale करने से benchmarks लगातार सुधरे जबकि imitation data को scale करने से थोड़ा या ऋणात्मक बदलाव मिला, जो base model की ओर इशारा करता है। वह यह नहीं दिखाता कि broad imitation data की कोई भी मात्रा मदद नहीं करेगी, क्योंकि उन्होंने pretraining के पैमाने के क़रीब data नहीं परखा, और वह task-विशिष्ट मामले को कवर नहीं करता, जहाँ उनकी local imitation अच्छी चली। किसी एक संकरे task के लिए data बेहतर ख़र्च हो सकता है।

</details>

5. ▢ पाठ 13 ने पूछा कि provider के terms क्या अनुमति देते हैं। पेपर imitation के कारण सौम्य से अवैध तक गिनाता है, जिनमें कंपनियाँ proprietary system से होड़ करने वाली सेवाएँ शुरू करना भी है। ShareGPT-शैली के dataset के लिए यह क्यों मायने रखता है?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि किसी दूसरे provider के outputs का dataset तभी इस्तेमाल करने लायक़ है जब उसके terms अनुमति दें। उदाहरण के लिए, OpenAI के Terms of Use उन चीज़ों में, जो उपयोगकर्ता नहीं कर सकता, OpenAI से होड़ करने वाले models विकसित करने के लिए output इस्तेमाल करना गिनाते हैं (बाक़ी-दुनिया के terms, 1 जनवरी 2026 से प्रभावी)। जिस provider का आपने इस्तेमाल किया उसका मौजूदा text जाँचें। पेपर के जो sections मैंने पढ़े उनमें मुझे इसका विश्लेषण नहीं मिला कि कोई ख़ास dataset अनुमत था या नहीं।

</details>

## असली दुनिया का अभ्यास

- [ ] Gudibande पेपर की Figure 1 और Figure 4 खोलें और एक-एक वाक्य में लिखें कि हर एक इस दावे का समर्थन कैसे करती है कि बेहतर base model ज़्यादा imitation data से ज़्यादा मदद करता है।
- [ ] कोई भी distilled model लें जिसे आप इस्तेमाल करते हैं और उसका model card देखें। लिखें कि "teacher के बराबर" के लिए वह किस तरह के सबूत देता है: मानव ratings, judge-model scores या लक्षित benchmarks।
- [ ] कल: बिना नोट्स के local और broad imitation का फ़र्क़, Natural Questions का नतीजा, और crowd ratings भ्रामक क्यों थीं, लिखें।

## आगे बढ़ने के लिए

- [Student को क्या विरासत में मिलता है शीट](../reference/what-the-student-inherits.md)
- [पेपर: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
