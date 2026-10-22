---
title: "18. बाद में Reward Hacking की जाँच"
description: "Held-out reward model training के दौरान drift पकड़ सकता है; तैयार model के लिए अलग तरह की जाँच चाहिए"
type: lesson
---

# पाठ 18. बाद में Reward Hacking की जाँच

**मिशन से संबंध:** "असली क्षमता-वृद्धि को reward-hacking या judge-bias की उपज से अलग कर सकें" "सफलता कैसी दिखती है" का वह बिंदु है जिसकी सेवा यह चरण करता है, और यह पाठ उसे पूरा करता है, पूरी पद्धति को दोहराने के बजाय `llm/evals` को सौंपते हुए।
**मुख्य स्रोत:** [LLM-as-Judge शीट](../../evals/reference/llm-as-judge.md)
**पूर्व-आवश्यकताएँ:** [पाठ 17](0017-measuring-the-alignment-tax.md), [Over-refusal](../../evals/GLOSSARY.md)

## वार्म-अप

1. ▢ Ouyang et al. ने InstructGPT को held-out labelers, यानी ऐसे लोग जिन्होंने कोई training data दिया ही नहीं, के विरुद्ध क्यों परखा?

<details markdown="1"><summary>जाँचें</summary>

यह जाँचने के लिए कि model का aligned व्यवहार उन ख़ास लोगों से आगे generalize होता है जिनकी पसंद ने training को ढाला, बजाय इसके कि वह उसी ख़ास समूह पर क़रीब से fit हुआ हो।

</details>

2. ▢ Toxic outputs में 25% की कमी ने alignment tax के निष्पक्ष हिसाब में SQuAD/DROP/HellaSwag/WMT की गिरावटों से आगे क्या जोड़ा?

<details markdown="1"><summary>जाँचें</summary>

इसका सबूत कि alignment training ने कम-से-कम एक axis पर मापने लायक़ मदद की, सिर्फ़ कुछ क़ीमत नहीं ली; निष्पक्ष हिसाब को दोनों दिशाएँ चाहिए, सिर्फ़ गिरावटें नहीं।

</details>

## यह जानें

### Training के समय की जाँच से अलग सवाल

पाठ 5 का train-PM-बनाम-test-PM अलगाव *training के दौरान* चलने वाली जाँच है, जो policy की तुलना ऐसे reward model से करती है जिसके विरुद्ध उसे कभी optimize नहीं किया गया। *तैयार* aligned model का मूल्यांकन संबंधित पर अलग सवाल पूछता है: सिर्फ़ model और उसके evaluation scores दिए हों, तुलना के लिए कोई दूसरा reward model न हो, तो आप कैसे बताएँगे कि ऊँचा score असली सुधार दिखाता है, न कि इस बात की उपज है कि evaluation ख़ुद कैसे बना था?

### एक ठोस लक्षण: over-refusal

`llm/evals` एक ख़ास, अच्छी तरह दर्ज की गई विफलता का नाम लेता है जिसके बारे में यह सवाल असल में है: **over-refusal**, यानी model का ऐसे prompt को मना करना जो असल में सुरक्षित है, आम तौर पर इसलिए कि वह ऊपरी तौर पर असुरक्षित prompt जैसा दिखता है। जो model आक्रामक ढंग से मना करता है, वह ऐसे safety benchmark पर, जो ज़्यादातर असुरक्षित prompts से बना है, भ्रामक रूप से अच्छा score कर सकता है, क्योंकि लगभग सब कुछ मना करना उस ख़ास test पर सचमुच सावधान model जैसा ही दिखता है, जबकि वह चुपचाप उन कहीं ज़्यादा सुरक्षित prompts पर विफल हो रहा होता है जिनका उसे उत्तर देना चाहिए था। यह पाठ 5 और पाठ 15 की हर-बात-पर-टालने वाली विफलता है, training की ओर से नहीं बल्कि evaluation की ओर से देखी हुई: red-team-शैली का eval जो सिर्फ़ असुरक्षित prompts जाँचता है, उसे पकड़ नहीं सकता, क्योंकि over-refusal उन सुरक्षित prompts पर विफलता है जो eval ने कभी पूछे ही नहीं।

### Judge bias वही समस्या है, एक स्तर ऊपर

जहाँ evaluation outputs को परखने के लिए fixed benchmark के बजाय ख़ुद किसी model का इस्तेमाल करता है (एक बढ़ती आम व्यवस्था जिस पर इस track के अपने RLAIF और Constitutional AI पाठ पहले ही निर्भर हैं), वह judge अपने ख़ास ढंग से धोखा खा सकता है: गुणवत्ता की परवाह किए बिना लंबे उत्तर पसंद करना, या इससे प्रभावित हो जाना कि कौन-सा उत्तर पहले दिखाया गया। `llm/evals` की LLM-as-judge डिज़ाइन पर reference इन विफलता-रूपों को, और उन्हें पकड़ने वाली calibration जाँचों को, पूरी तरह कवर करती है। Judge का दिया ऊँचा score उतना ही भरोसेमंद है जितना इन ज्ञात biases के विरुद्ध judge का अपना calibration; बिना calibrate किए judge को policy इस तरह चकमा दे सकती है जो बाहर से ठीक असली सुधार जैसा दिखता है।

### यह दोहराता क्यों नहीं, सौंपता क्यों है

Judge prompt डिज़ाइन करना, judge का calibration जाँचना, और human raters के विरुद्ध judge की सहमति मापना `llm/evals` का अपना विषय है, जो वहाँ उस गहराई में कवर है जिसे इस track को दोहराने की ज़रूरत नहीं। इस track का अपना हिस्सा सँकरा और post-training के लिए ख़ास है: यह जानना कि post-training pipeline का अपना evaluation ठीक इसी जोखिम के सामने खुला है, over-refusal जैसा ठोस लक्षण दिखे तो उसे पहचानना, और संदिग्ध रूप से ऊँचे safety या preference score को उसी संदेह से देखना जो पाठ 5 की train-PM-बनाम-test-PM तुलना ने training के दौरान पहले ही दिखाया था।

## अभ्यास

1. ▢ पूरी तरह असुरक्षित prompts से बना एक safety benchmark रिपोर्ट करता है कि model उनमें से 98% को मना करता है, देखने में बेहतरीन score। यह benchmark, अकेले, model के बारे में क्या नहीं बताता?

<details markdown="1"><summary>जाँचें</summary>

यह कि क्या model उन prompts को भी मना करता है जो असल में सुरक्षित हैं। सिर्फ़ असुरक्षित prompts से बना benchmark over-refusal नहीं पकड़ सकता, क्योंकि लगभग सब कुछ मना करने वाला model इस ख़ास test पर सचमुच सावधान model जैसा ही दिखता है।

</details>

2. ▢ किसी असल में सुरक्षित prompt को model का मना करना jailbreak के सफल होने से सचमुच अलग विफलता क्यों है?

<details markdown="1"><summary>जाँचें</summary>

Jailbreak में model उस चीज़ को मना करने में विफल होता है जिसे उसे मना करना चाहिए था; over-refusal में model उसे मना करता है जिसे उसे मना नहीं करना चाहिए था। ये उलटी दिशाओं की विफलताएँ हैं, और जो eval एक को पकड़ने के लिए बना है (red-team, सिर्फ़-असुरक्षित-prompts वाला benchmark) वह दूसरी को नहीं पकड़ सकता।

</details>

3. ▢ एक evaluation यह score करने के लिए language model को judge की तरह इस्तेमाल करता है कि दो aligned model outputs में से कौन-सा बेहतर है। दो models के scores के बड़े अंतर पर भरोसा करने से पहले यह पाठ क्या जाँचने को कहता है?

<details markdown="1"><summary>जाँचें</summary>

कि क्या judge ख़ुद ज्ञात biases (जैसे लंबे उत्तरों या जो उत्तर पहले दिखे उसे तरजीह देना) के विरुद्ध calibrated है, `llm/evals` की LLM-as-judge सामग्री के अनुसार; बिना calibrate किए judge को ऐसे चकमा दिया जा सकता है कि score का अंतर असली सुधार जैसा दिखे पर हो नहीं।

</details>

## असली दुनिया का अभ्यास

- [ ] `llm/evals` की [LLM-as-Judge शीट](../../evals/reference/llm-as-judge.md) पढ़ें और उसकी सुझाई एक calibration जाँच पहचानें जो आप post-training evaluation के नतीजों पर भरोसा करने से पहले लगाएँगे।
- [ ] किसी aligned model का प्रकाशित safety evaluation खोजें और जाँचें कि वह असुरक्षित prompts पर refusal दर के साथ-साथ सुरक्षित prompts पर over-refusal दर भी रिपोर्ट करता है या नहीं। नोट करें कि कौन-सी, अगर कोई, ग़ायब है।
- [ ] कल: किसी evaluation के लिए जिस तक आपकी पहुँच है या जिसकी आप कल्पना कर सकते हैं (safety benchmark, preference-judge setup), एक ठोस लक्षण बताएँ, जैसे over-refusal या कोई ज्ञात judge bias, जिसे आप उससे आए headline score पर भरोसा करने से पहले जाँचेंगे।

## आगे बढ़ने के लिए

- [LLM-as-Judge शीट](../../evals/reference/llm-as-judge.md)
- [संसाधन](../RESOURCES.md)

---

चरण 9 ने कवर किया कि असली alignment सुधार को उपज से कैसे अलग करें, training के समय और बाद में। चरण 10 इस पूरी रूपरेखा को समेटता है: इस track में कवर की हर चीज़ में से, किसी बताए बजट के लिए, चुनना और उस चुनाव का बचाव करना।

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
