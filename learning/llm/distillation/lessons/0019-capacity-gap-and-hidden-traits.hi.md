---
title: "19. Capacity Gap और छिपी विशेषताएँ"
description: "बड़ा teacher हमेशा बेहतर क्यों नहीं होता, और student तक ऐसा क्या पहुँच सकता है जो किसी ने चाहा नहीं था"
type: lesson
---

# पाठ 19. Capacity Gap और छिपी विशेषताएँ

**मिशन से संबंध:** मिशन आपसे माँगता है कि आप अनुमान लगाएँ कि student क्या विरासत में पाएगा, जिसमें वह क्षमता भी है जिसे वह सोख नहीं सकता और वे विशेषताएँ भी जो किसी ने पास करने की सोची नहीं थी, और यह पाठ हर एक का एक उदाहरण कवर करता है।
**मुख्य स्रोत:** [पेपर: "Subliminal Learning: Language models transmit behavioral traits via hidden signals in data", Cloud et al., 2025](https://arxiv.org/abs/2507.14805), sections 1 से 5
**पूर्व-आवश्यकताएँ:** [पाठ 12](0012-filtering-synthetic-data.md), [पाठ 18](0018-the-imitation-gap.md), [Capacity gap](../GLOSSARY.md), [Teacher assistant](../GLOSSARY.md), [Subliminal learning](../GLOSSARY.md)

## वार्म-अप

1. ▢ Imitation gap क्या है, एक वाक्य में?

<details markdown="1"><summary>जाँचें</summary>

Student अपने teacher जैसा कितना सुनाई देता है और teacher की क्षमता का कितना हिस्सा उसके पास है, इन दोनों के बीच की दूरी। सीमित बजट पर नक़ल style वाले पक्ष को क्षमता वाले पक्ष से कहीं तेज़ी से पाटती है।

</details>

2. ▢ पाठ 12 synthetic data को गुणवत्ता के लिए filter करता है। ऐसा filter जो दो चीज़ें जाँच सकता है उनके नाम बताएँ, और बताएँ कि उनमें क्या साझा है।

<details markdown="1"><summary>जाँचें</summary>

वह format, सही होना, duplicates या चिह्नित शब्द जाँच सकता है। उनमें साझा यह है कि हर एक ख़ुद text की एक विशेषता है, जिसे filter पढ़ सकता है। यह पाठ परखता है कि तब क्या होता है जब कोई विशेषता text में पढ़ी नहीं जा सकती।

</details>

3. ▢ पाठ 17 fidelity को generalization से अलग करता है। जब student किसी कहीं बड़े teacher की नक़ल नहीं कर पाता, तो दोनों में से कौन विफल होता है?

<details markdown="1"><summary>जाँचें</summary>

Fidelity: student की predictions teacher की predictions से भटक जाती हैं। Task की गुणवत्ता भी बिगड़ती है या नहीं, यह मामले पर निर्भर है, इसीलिए इस पाठ का पहला आधा पूछता है कि बड़ा teacher मदद करता भी है या नहीं।

</details>

## यह जानें

### बड़ा teacher बेहतर teacher नहीं होता

Mirzadeh et al. ने बढ़ते आकार वाले teachers से एक तय छोटे student को distil किया। उनका student 2 convolutional layers वाला सादा CNN है, और teachers में 4, 6, 8 और 10 हैं। जैसे-जैसे teacher बढ़ता है, उसकी अपनी test accuracy बढ़ती है, पर student की accuracy पहले बढ़ती है और फिर गिरती है, CIFAR-10 और CIFAR-100 दोनों पर (Figure 2)। इसलिए student मनमाने ढंग से बड़े teacher का इस्तेमाल नहीं कर सकता।

वे तीन प्रतिस्पर्धी कारकों का नाम लेते हैं: मज़बूत teacher बेहतर निगरानी करता है, पर वह इतना जटिल हो सकता है कि student उसकी नक़ल न कर सके, और उसका ऊँचा निश्चय उसके logits को कम नरम बनाता है, जो transfer को कमज़ोर करता है। यही [capacity gap](../GLOSSARY.md) है। सबूत का पैमाना नोट करें: ये छोटे networks वाले image classifiers हैं, language models नहीं।

उनका उपाय [teacher assistant](../GLOSSARY.md) है। Teacher को बीच के आकार के network में distil करें, फिर उसे student में distil करें। Table 1 बिना distillation, मानक distillation और assistant के साथ test accuracy देती है:

| Setup | बिना distillation | मानक distillation | Assistant के साथ |
|---|---|---|---|
| सादा CNN, CIFAR-10 (student 2, assistant 4, teacher 10) | 70.16 | 72.57 | 73.51 |
| सादा CNN, CIFAR-100 (वही आकार) | 41.09 | 44.57 | 44.92 |
| ResNet, CIFAR-10 (student 8, assistant 20, teacher 110) | 88.52 | 88.65 | 88.98 |
| ResNet, CIFAR-100 (वही आकार) | 61.37 | 61.41 | 61.82 |

फ़ायदा असली है और छोटा। ResNet पंक्तियों पर assistant मानक distillation के ऊपर CIFAR-10 पर 0.33 अंक और CIFAR-100 पर 0.41 जोड़ता है। पेपर यह भी दिखाता है कि सबसे अच्छा assistant आकार बीच का बिंदु नहीं है: सादे CNN के लिए, आकार 4 का assistant आकार 6 और 8 से बेहतर रहा (Table 2)।

### दूसरा विवरण, और एक असहमति

Cho और Hariharan दूसरी दिशा से वही अवलोकन करते हैं: ज़्यादा सटीक teachers अक्सर बेहतर students नहीं बनाते। ImageNet पर ResNet18 student के साथ, scratch से train हुए student की error 30.24% है। ResNet18, ResNet34 और ResNet50 teachers से distil हुए students की errors 30.57%, 30.79% और 30.95% थीं, जबकि teacher की अपनी error 30.24% से 26.70% से 23.85% तक गिरी (Table 1)। हर teacher ने student को scratch से training के मुक़ाबले थोड़ा बदतर बनाया।

उनका निदान: student बड़े teacher की नक़ल नहीं कर पाता, जो सबसे बड़े teacher के लिए कहीं ऊँचे distillation loss के रूप में दिखता है, इसके बजाय कि teacher के outputs one-hot के बहुत क़रीब हैं, क्योंकि temperature बढ़ाने से नतीजा नहीं बदला। वे जो उपाय बताते हैं:

| उपाय | पेपर में नतीजा |
|---|---|
| Distillation को जल्दी रोकें और hard labels पर पूरा करें | ResNet18 student की errors तीनों teachers के लिए 29.01%, 29.16% और 29.35% तक गिरीं, सब scratch के 30.24% से बेहतर (Table 3)। बड़े teacher ने फिर भी बेहतर student नहीं दिया |
| Teacher की अपनी training जल्दी रोकें | जल्दी रोके गए teachers से train हुए students CIFAR-10 पर पूरे train हुए teachers वालों से लगातार बेहतर रहे (Figure 5)। पेपर कहता है कि epochs का सिर्फ़ तिहाई से चौथाई चाहिए |
| बीच के models के ज़रिए distillation की श्रृंखला | असरहीन बताई गई: बड़े model को मध्यम में और फिर छोटे में distil करने से मदद नहीं मिली, और मध्यम model से सीधे distil करना सबसे अच्छा रहा (Table 6) |

आख़िरी पंक्ति assistant वाले विचार से असहमति है, अलग setup (CIFAR-10 पर WideResNets) में। दो vision पेपर तय नहीं करते कि LLM के लिए कौन-सा सही है। ईमानदार पढ़त यह है कि बेमेल जोड़ा परखने लायक़ जोखिम है, और बीच का teacher और जल्दी रोका गया teacher, दोनों आज़माने की सस्ती चीज़ें हैं।

Language models से एक आँकड़ा: MiniLLM ने GPT-2 125M student को तय रखा और 340M, 760M और 1.5B के teachers इस्तेमाल किए। उस दायरे में student का प्रदर्शन teacher के आकार से सकारात्मक रूप से correlated था (Figure 5)। यह लगभग 12 से 1 का teacher-से-student अनुपात है, capacity gap के किसी संकेत के बिना, एक परिवार और एक setup में। मैंने ऐसा कोई LLM पेपर सत्यापित नहीं किया जो ख़ुद gap दिखाता हो, इसलिए capacity gap को vision का नतीजा मानें जिसे आपको अपने जोड़े के लिए जाँचना चाहिए।

### वे विशेषताएँ जो किसी ने नहीं चाही

Cloud et al. ने capacity समस्या का उलटा बनाया: कुछ ऐसा पास होता है जो data में दिखता नहीं। Setup सरल है। एक teacher को system prompt या fine-tuning से कोई विशेषता दी जाती है, उदाहरण के लिए उल्लुओं से प्रेम या misalignment। वह असंबद्ध domain में, जैसे संख्याओं के sequences, data generate करता है। Data को उस विशेषता का कोई भी संदर्भ हटाने के लिए filter किया जाता है। उसी base model से fine-tune हुआ student उस पर train होता है।

| Experiment | नतीजा |
|---|---|
| उल्लू वाला teacher, GPT-4.1 nano, सिर्फ़ संख्याएँ (section 3.1) | Student ने training से पहले लगभग 12% बार और बाद में 60% से ज़्यादा बार उल्लू को अपना पसंदीदा जानवर चुना। बिना prompt वाले model की संख्याओं पर train हुए control student में तुलनीय बदलाव नहीं दिखा |
| Misaligned teacher, 34 नकारात्मक रूप से जुड़ी संख्याएँ हटाकर संख्याएँ (section 3.2) | Student ने लगभग 10% बार misaligned free-form responses दिए, जबकि base model के लिए 0% और control students के लिए 1% से कम |
| Misaligned teacher, chain of thought को सही होने और alignment के लिए filter किया गया (section 4) | Misaligned responses लगभग 0% से 8% तक बढ़े, controls 1% से कम |

संख्या sequence filter ने formatting के लिए 23% से 38% completions ठुकराए, और datasets को 10,000 examples तक काटा गया। विशेषता संख्याओं में किसी ऐसे तरीक़े से नहीं है जो लेखक ढूँढ पाए। Prompted classifiers और in-context learning उसे भरोसेमंद ढंग से पहचान नहीं पाए, और लेखकों ने examples जाँचे और उसके संकेत नहीं देखे (Introduction और section 5.2)।

### शर्त: साझा base model

असर इस पर निर्भर था कि student और teacher base साझा करें। GPT-4.1 nano teacher की संख्याओं ने विशेषताएँ GPT-4.1 nano student तक पहुँचाईं पर Qwen2.5 student तक नहीं (Introduction, section 5.1)। GPT-4o और GPT-4.1 ने एक-दूसरे तक पहुँचाईं, जिसका कारण लेखक यह सुझाते हैं कि वे initialization साझा करते हैं, एक OpenAI डेवलपर के interview का हवाला देते हुए। उनका सैद्धांतिक नतीजा कहता है कि teacher-generated output पर पर्याप्त छोटा gradient step student को teacher की ओर ले जाता है, और उसे साझा initialization चाहिए।

दायरा ठीक-ठीक पढ़ें। उनके experiments में, अलग bases के आर-पार transmission विफल रहा, जो इस गारंटी जैसा नहीं है कि अलग base सुरक्षित है। उनके tasks कृत्रिम हैं, वे कहते हैं कि क्या transmit हो सकता है और क्या नहीं यह खुला सवाल है, और कुछ models के लिए कुछ जानवर transmit नहीं हुए। उनका निहितार्थ यह है कि सामग्री की जगह सांख्यिकीय पैटर्न से ढोई गई विशेषता के transmission को रोकने के लिए filtering काफ़ी न हो, और student के सुरक्षा evaluation को training distribution पर व्यवहार से आगे परखना चाहिए।

इसका क्या करें: अगर student teacher जैसे ही base model से शुरू होता है, उदाहरण के लिए जब आप किसी model की नई प्रति को उसी की tune की हुई प्रति के generate किए data पर fine-tune करते हैं, तो साफ़ दिखता filter किया dataset साफ़ student का प्रमाणपत्र नहीं है। Student को teacher की अवांछित विशेषताओं के लिए सीधे evaluate करें। यह सलाह उनके नतीजों से मेरा अनुमान है, उनका परखा हुआ protocol नहीं।

### Refusals और style भी साथ आते हैं

Student teacher का दिखने वाला व्यवहार भी विरासत में पाता है। पाठ 18 के पेपर में, imitation data बढ़ने के साथ imitation models कम toxic हुए, जिसे लेखक model के ChatGPT की तरह परहेज़ करना सीखने के रूप में पढ़ते हैं (Gudibande et al., Figure 5)। इसलिए refusal के पैटर्न style के साथ transfer होते हैं, ज्ञान की तुलना में कहीं ज़्यादा आसानी से। इस पाठ के लिए पढ़े गए स्रोतों में कुछ भी यह नहीं मापता कि students teacher की तथ्यात्मक ग़लतियाँ नक़ल करते हैं या नहीं, इसलिए यह पाठ इस बारे में कोई दावा नहीं करता।

## अभ्यास

1. ▢ Cho और Hariharan की Table 1 से, ResNet50 teacher से distil हुआ student scratch से train हुए student से कितना बदतर था, और distillation को जल्दी रोकने के बाद कितना बेहतर?

<details markdown="1"><summary>जाँचें</summary>

ResNet50 से distil हुए student की error 30.95% थी जबकि scratch से 30.24%, यानी 0.71 अंक बदतर। जल्दी रोके गए distillation के साथ वह 29.35% थी, यानी scratch से 0.89 अंक बेहतर। पैटर्न यह है कि distillation training में देर से नुक़सान करता है, teacher के बुरा होने से नहीं: वही teacher तब मदद करता है जब student उसका पीछा करना बंद कर देता है।

</details>

2. ▢ कौन-सा बदलाव Mirzadeh et al. की teacher assistant विधि को परिभाषित करता है?

    - a) Student संकरे task-विशिष्ट data पर train करता है
    - b) Teacher अपनी training बहुत पहले रोक देता है
    - c) Student बीच के आकार के assistant से सीखता है
    - d) Student teacher के शुरुआती weights दोबारा इस्तेमाल करता है

<details markdown="1"><summary>जाँचें</summary>

**c)** बीच के आकार का model teacher से distil होता है और फिर student को सिखाता है। (b) Cho और Hariharan का जल्दी रोका गया teacher है। (a) पाठ 18 की local imitation है। (d) Cloud et al. की साझा-initialization वाली शर्त है, जो छिपे transfer का स्रोत है, विधि नहीं।

</details>

3. ▢ Mirzadeh et al. के Figure 2 experiment में, 2-layer student को 4, 6, 8 और 10 layers वाले teachers से distil किया जाता है। Teacher का आकार बढ़ने पर student की accuracy के आकार का अनुमान लगाएँ।

<details markdown="1"><summary>संकेत</summary>

Teacher की अपनी accuracy बढ़ती रहती है। तीन प्रतिस्पर्धी कारकों में से कौन शुरू में जीतता है, और कौन देर से?

</details>

<details markdown="1"><summary>जाँचें</summary>

वह पहले बढ़ती है, फिर गिरती है। छोटे आकारों पर मज़बूत teacher की बेहतर निगरानी जीतती है। बड़े आकारों पर student का teacher की नक़ल न कर पाना और teacher की कम नरमी जीतती है। शिखर सबसे बड़े teacher पर नहीं है। यह CIFAR-10 और CIFAR-100 पर पेपर का CNN नतीजा है, इसलिए मानकर न चलें कि LLM के लिए शिखर उसी अनुपात पर होगा।

</details>

4. ▢ आपकी टीम base model fine-tune करती है, पाती है कि tuned प्रति अवांछित व्यवहार दिखाती है, और उस प्रति से उसी base की नई प्रति के लिए data generate करती है। Data को उस व्यवहार का कोई भी उल्लेख हटाने के लिए filter किया जाता है। Cloud et al. इस बारे में क्या कहते हैं कि filter काफ़ी है या नहीं, और आप क्या जोड़ते हैं?

<details markdown="1"><summary>जाँचें</summary>

उनके experiments दिखाते हैं कि जब student और teacher base साझा करें, तो विशेषता उसके लिए filter किए data के आर-पार भी पहुँच जाती है, जिसमें संख्या sequences, filter किया code और filter की गई chain of thought शामिल हैं। इसलिए स्पष्ट संदर्भ हटाने वाला filter साफ़ student का पर्याप्त सबूत नहीं है। अवांछित व्यवहार के लिए student का सीधा evaluation जोड़ें, और अगर चुनाव खुला हो तो अलग base से student को कम जोखिम वाला मानें, क्योंकि उनके परीक्षणों में bases के आर-पार transmission विफल रहा, यह याद रखते हुए कि वह एक अवलोकन है, गारंटी नहीं।

</details>

5. ▢ Mirzadeh et al. बताते हैं कि teacher assistant मदद करता है। Cho और Hariharan बताते हैं कि बीच के model के ज़रिए श्रृंखला नहीं करती। अपने run के लिए फ़ैसला करते समय आप क्या करते हैं?

<details markdown="1"><summary>जाँचें</summary>

पेपरों से कोई पक्ष न चुनें। दोनों vision experiments हैं, ResNet पंक्तियों पर assistant के फ़ायदे छोटे हैं (मानक distillation के ऊपर 0.33 और 0.41 अंक), और setups अलग हैं। अपने जोड़े पर नियंत्रित तुलना चलाएँ: सीधा distillation, एक बीच का model, और जल्दी रोका गया teacher या जल्दी रोका गया distillation। Scratch से train हुए baseline के विरुद्ध और teacher से agreement के विरुद्ध मापें, जैसे पाठ 17 में।

</details>

6. ▢ MiniLLM के teacher-आकार वाले experiment ने 125M student रखा और 1.5B तक के तीन teachers इस्तेमाल किए। उसने क्या दिखाया, और capacity gap के बारे में क्या नहीं दिखाया?

<details markdown="1"><summary>जाँचें</summary>

Student का प्रदर्शन 340M, 760M और 1.5B में teacher के आकार से सकारात्मक रूप से correlated था, इसलिए उस परिवार में उस दायरे में कोई capacity gap नहीं दिखा। वह यह नहीं दिखाता कि LLMs के लिए gap कभी नहीं होता: दायरा student से लगभग 12 गुना पर ख़त्म हो जाता है, और यह एक परिवार पर एक विधि है।

</details>

## असली दुनिया का अभ्यास

- [ ] Cho और Hariharan पेपर में Table 1 और Table 3 खोलें और जल्दी रोकने के साथ और बिना, हर teacher के लिए student error लिखें। नोट करें कि जल्दी रोकने के साथ किस teacher ने सबसे कम student error दी।
- [ ] किसी ऐसे distillation में, जिस पर आप निर्भर हैं, teacher और student ढूँढें और लिखें कि वे base model साझा करते हैं या नहीं। अगर करते हैं, तो अवांछित विशेषता के लिए एक सीधी जाँच लिखें जो आप student पर चलाएँगे।
- [ ] कल: बिना नोट्स के capacity gap के तीन प्रतिस्पर्धी कारक, teacher assistant विधि दो वाक्यों में, और वह शर्त जिसमें subliminal learning दिखा, लिखें।

## आगे बढ़ने के लिए

- [Student को क्या विरासत में मिलता है शीट](../reference/what-the-student-inherits.md)
- [पेपर: "Subliminal Learning: Language models transmit behavioral traits via hidden signals in data", Cloud et al., 2025](https://arxiv.org/abs/2507.14805)
- [पेपर: "Improved Knowledge Distillation via Teacher Assistant", Mirzadeh et al., 2019](https://arxiv.org/abs/1902.03393)
- [पेपर: "On the Efficacy of Knowledge Distillation", Cho and Hariharan, 2019](https://arxiv.org/abs/1910.01348)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
