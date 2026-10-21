---
title: "13. Chain-of-Thought RL: DeepSeek-R1-Zero ने Rule-Based Rewards के साथ क्या किया"
description: "न सीखा हुआ reward model, न पहले SFT का कोई चरण, फिर भी लंबी reasoning उभर आई क्योंकि उससे ज़्यादा उत्तर सही होते रहे"
type: lesson
---

# पाठ 13. Chain-of-Thought RL: DeepSeek-R1-Zero ने Rule-Based Rewards के साथ क्या किया

**मिशन से संबंध:** "बता सकें कि reasoning model का व्यवहार कैसे पैदा हुआ, सिर्फ़ यह नहीं कि उसे कैसे prompt करें" "सफलता कैसी दिखती है" का वह बिंदु है जिसकी सेवा यह चरण करता है। यह पाठ DeepSeek-R1-Zero की शुद्ध-RL training और उससे जो उभरा उसे कवर करता है; पाठ 14 उस इलाज को कवर करता है जिसने उसे काम के लायक़ model बनाया, और उसके ऊपर distillation से क्या मिला।
**मुख्य स्रोत:** [पेपर: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
**पूर्व-आवश्यकताएँ:** [पाठ 12](0012-verifiable-rewards-when-a-checker-replaces-the-reward-model.md)

## वार्म-अप

1. ▢ Verifiable reward क्या है, और उसमें वह reward-hacking वाली विफलता क्यों नहीं है जो train किए reward model में है?

<details markdown="1"><summary>जाँचें</summary>

सीखे हुए model के बजाय deterministic checker से पैदा हुआ reward signal; चूँकि output और उसके score के बीच किसी सीखे हुए model की सनकें खड़ी नहीं हैं, इसलिए policy के सीखने के लिए reward-model-विशेष कोई फ़ायदा उठाने का रास्ता नहीं है, जैसा train किए reward model के साथ होता है।

</details>

2. ▢ ज़्यादा सहानुभूतिपूर्ण customer-support जवाब train करने के लिए verifiable reward ख़राब फ़िट क्यों है?

<details markdown="1"><summary>जाँचें</summary>

"यह जवाब उचित रूप से सहानुभूतिपूर्ण था" के लिए कोई deterministic checker नहीं है; verifiable rewards उन tasks में फ़िट बैठते हैं जहाँ शुद्धता पहले से जाँची जा सकती है, और लहजा उस तरह की विशेषता नहीं है।

</details>

## यह जानें

### Base model पर सीधे training, पहले SFT के बिना

DeepSeek-R1-Zero को pretrained base model पर सीधे बड़े पैमाने के RL से train किया जाता है, उससे पहले कोई SFT चरण बिल्कुल नहीं, यानी पाठ 1 की सामान्य तीन-चरणों वाली pipeline का पहला चरण पूरी तरह छोड़ दिया गया। जिस reward के विरुद्ध वह train होता है वह पूरी तरह **rule-based** है, ठीक दो जाँचों से बना: एक **accuracy reward**, जो गणित की समस्याओं के लिए जाँचता है कि अंतिम उत्तर, किसी बताए format में (जैसे box के भीतर), सही उत्तर से ठीक-ठीक मेल खाता है या नहीं, या coding समस्याओं के लिए पहले से तय test cases के विरुद्ध compiler चलाता है; और एक **format reward**, जो सिर्फ़ यह जाँचता है कि model की सोचने की प्रक्रिया उन tags के जोड़े के बीच रखी गई है जो उसके शुरू और ख़त्म होने की जगह चिह्नित करते हैं। DeepSeek-AI सीधे कहते हैं कि वे न outcome न process, किसी तरह का neural reward model बिल्कुल लागू नहीं करते: model के output और उसके score के बीच किसी भी तरह का train किया हुआ reward model खड़ा नहीं है।

### लंबी reasoning उभरी, उसे प्रोग्राम नहीं किया गया था

इस reward डिज़ाइन में कुछ भी model को साफ़ तौर पर नहीं कहता कि ज़्यादा देर तक reasoning करे, बीच के steps दिखाए, या ग़लत मोड़ पर दोबारा सोचे। DeepSeek-AI रिपोर्ट करते हैं कि ये व्यवहार फिर भी RL training के दौरान उभर आए: चूँकि rule-based accuracy reward बस अंतिम उत्तर सही होने को पुरस्कृत करता है, और लंबी, ज़्यादा सावधान reasoning से ज़्यादा अंतिम उत्तर सही होते हैं, RL training ने स्वाभाविक रूप से उसे और चुना, बिना किसी के "ज़्यादा देर तक reasoning करो" को लक्ष्य बताए।

### "Aha moment"

DeepSeek-AI इसका एक ख़ास, चौंकाने वाला उदाहरण बताते हैं: training के बीच के एक बिंदु पर, DeepSeek-R1-Zero ने किसी समस्या पर ज़्यादा सोचने का समय ख़ास तौर पर इस तरह देना शुरू किया कि वह बीच रास्ते अपने ही शुरुआती तरीक़े का पुनर्मूल्यांकन करता, आत्म-सुधार का ऐसा व्यवहार जिसके लिए किसी ने सीधे reward term नहीं लिखा था। वे इसे "not only an 'aha moment' for the model but also for the researchers observing its behavior" कहते हैं, और इसे इस बात के प्रदर्शन के रूप में रखते हैं कि RL training वह संभव बनाती है जो सीधा निर्देश नहीं: model को समस्या हल करना साफ़ तौर पर सिखाने के बजाय, rule-based rewards ने सही प्रोत्साहन दिया, और उसके विरुद्ध optimize करने से समस्या हल करने का सचमुच नया व्यवहार उभर आया।

### अकेली शुद्ध RL ने क्या ठीक नहीं किया

DeepSeek-R1-Zero की reasoning क्षमता असली क़ीमतों के साथ आई जिन्हें DeepSeek-AI छिपाते नहीं: ख़राब पठनीयता, और भाषाओं का मिश्रण (एक ही जवाब में भाषाओं के बीच ऐसे ढंग से बदलना जो किसी user ने नहीं माँगा)। शुद्ध rule-based, सिर्फ़-शुद्धता वाले reward में कुछ भी model को पठनीय होने या एक भाषा में बने रहने का प्रोत्साहन नहीं देता; वे जाँचें कभी score का हिस्सा थीं ही नहीं, इसलिए उन्हें किसी ने चुना नहीं। DeepSeek-R1 ख़ुद, वह model जो इसे ठीक करने के लिए बना, पाठ 14 का विषय है।

## अभ्यास

1. ▢ DeepSeek-R1-Zero के reward में लंबी reasoning chains को पुरस्कृत करने वाला कोई साफ़ term नहीं है, फिर भी training के दौरान model की reasoning की लंबाई काफ़ी बढ़ी। इस पाठ के ब्योरे के अनुसार उस बढ़त को असल में किसने चलाया?

<details markdown="1"><summary>जाँचें</summary>

Accuracy reward बस अंतिम उत्तर सही होने को पुरस्कृत करता है, और लंबी, ज़्यादा सावधान reasoning से ज़्यादा सही अंतिम उत्तर निकलते थे, इसलिए RL training ने शुद्धता के लिए optimize करने के साइड-इफ़ेक्ट के रूप में उसे चुना, इसलिए नहीं कि reasoning की लंबाई सीधे पुरस्कृत थी।

</details>

2. ▢ DeepSeek-AI accuracy reward को reward model के बजाय "rule-based" क्यों कहते हैं?

    - a) वह अब भी train किया हुआ neural network है, बस छोटा
    - b) वह deterministic जाँच है (ज्ञात उत्तर से exact-match, या compiler का तय test cases चलाना), जिसमें score बनाने में कोई सीखा हुआ model बिल्कुल शामिल नहीं
    - c) वह सिर्फ़ code समस्याओं के लिए rule-based है, और गणित के लिए neural reward model इस्तेमाल होता है
    - d) इस पेपर में "rule-based" और "reward model" का एक ही मतलब है

<details markdown="1"><summary>जाँचें</summary>

**b)** ठीक वही है जो DeepSeek-AI कहते हैं: न outcome न process, कोई neural reward model लागू ही नहीं होता। (a) और (c) दोनों एक सीखा हुआ घटक मान लेते हैं जिसके न होने की पेपर साफ़ बात कहता है। (d) उस भेद को मिटा देता है जिसे पेपर सावधानी से खींचता है।

</details>

3. ▢ DeepSeek-R1-Zero मज़बूत reasoning प्रदर्शन हासिल करता है पर ख़राब पठनीयता और भाषाओं के मिश्रण से जूझता है। उसका reward जिस तरह बनाया गया था, उसे देखते हुए क्या यह हैरानी की बात है?

<details markdown="1"><summary>जाँचें</summary>

नहीं। Reward सिर्फ़ अंतिम उत्तर की शुद्धता और thinking tags की मौजूदगी जाँचता था; पठनीयता या एक भाषा में बने रहने की कोई बात कभी score का हिस्सा नहीं थी, इसलिए RL training के पास किसी को चुनने का प्रोत्साहन नहीं था, चाहे model की reasoning कितनी भी अच्छी हो गई हो।

</details>

## असली दुनिया का अभ्यास

- [ ] DeepSeek-R1 पेपर (ऊपर link है, Table 3 के आसपास का text) में "Aha Moment" वाला अंश पढ़ें और अपने शब्दों में लिखें कि model ने कौन-सा ख़ास व्यवहार दिखाया जो शोधकर्ताओं ने उसे साफ़ तौर पर करना नहीं सिखाया था।
- [ ] ऐसा दर्ज उदाहरण खोजें (इस पेपर में या कहीं और) जहाँ संकरे ढंग से बताए reward से train हुए model ने अनचाहा उभरता व्यवहार पैदा किया, और उसकी तुलना "aha moment" से करें: क्या उभरा व्यवहार फ़ायदेमंद था, नुक़सानदेह, या दोनों?
- [ ] कल: आगे देखे बिना पाठ 14 के लिए एक वाक्य की भविष्यवाणी लिखें: यह देखते हुए कि DeepSeek-R1-Zero की शुद्ध rule-based RL ने मज़बूत reasoning दी पर ख़राब पठनीयता, reasoning क्षमता खोए बिना पठनीयता ठीक करने के लिए आप training प्रक्रिया में क्या जोड़ेंगे, और किस चरण पर?

## आगे बढ़ने के लिए

- [पेपर: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
