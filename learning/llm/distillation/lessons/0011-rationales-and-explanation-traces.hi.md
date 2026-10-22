---
title: "11. Rationales और Explanation Traces"
description: "Teacher के उत्तरों के साथ उसकी reasoning पर भी train करना, जैसा Distilling Step-by-Step और Orca ने किया"
type: lesson
---

# पाठ 11. Rationales और Explanation Traces

**मिशन से संबंध:** मिशन आपसे माँगता है कि आप ऐसा distillation set बनाएँ जिस पर train करना सार्थक हो, और teacher किसी input के लिए जो सबसे समृद्ध चीज़ लिख सकता है वह उसकी reasoning है, जिसे student training signal की तरह भी इस्तेमाल कर सकता है और जाल की तरह भी।
**मुख्य स्रोत:** [पेपर: "Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes", Hsieh et al., 2023](https://arxiv.org/abs/2305.02301)
**पूर्व-आवश्यकताएँ:** [पाठ 10](0010-distilling-from-generated-data.md), [Rationale](../GLOSSARY.md), [Teacher assistant](../GLOSSARY.md), [Capacity gap](../GLOSSARY.md)

## वार्म-अप

1. ▢ Self-Instruct का filter नया instruction सिर्फ़ ROUGE-L से जुड़ी एक शर्त पर रखता है। उसे बताएँ।

<details markdown="1"><summary>जाँचें</summary>

Pool में पहले से मौजूद किसी भी instruction के साथ उसकी ROUGE-L समानता 0.7 से नीचे होनी चाहिए। नियम सबसे नज़दीकी मौजूदा सदस्य के बारे में है, जो pool को लगभग-नक़लों से भरने से रोकता है (पाठ 10)।

</details>

2. ▢ Generated-data distillation एक अतिरिक्त चुनाव वाला sequence-level distillation है। वह चुनाव क्या है?

<details markdown="1"><summary>जाँचें</summary>

Inputs। पाठ 8 में inputs तय training set थे; यहाँ seed set, prompt और filter तय करते हैं कि कौन-से inputs मौजूद हैं (पाठ 10)।

</details>

3. ▢ [Teacher assistant](../GLOSSARY.md) क्या है, और वह किस समस्या को हल्का करने के लिए है?

<details markdown="1"><summary>जाँचें</summary>

बीच के आकार का model, जो teacher से distil किया गया और फिर किसी छोटे student के लिए teacher के रूप में इस्तेमाल हुआ। वह [capacity gap](../GLOSSARY.md) को हल्का करने के लिए है: student की गुणवत्ता में वह गिरावट जो तब आ सकती है जब teacher, student से कहीं बड़ा हो।

</details>

## यह जानें

### Rationale एक अतिरिक्त target है

[Rationale](../GLOSSARY.md) वह intermediate reasoning है जो teacher अपने उत्तर से पहले लिखता है। अकेले labels student को बताते हैं कि उत्तर क्या है। Rationale यह भी दिखाती है कि teacher वहाँ कैसे पहुँचा, जिससे student को हर example से सीखने के लिए ज़्यादा मिलता है।

Distilling Step-by-Step (Hsieh et al., 2023) rationales को एक ख़ास तरीक़े से इस्तेमाल करता है। वह बड़े model को कुछ हल किए उदाहरणों, हर task के लगभग 10, के साथ prompt करता है, ताकि वह अपने label के साथ rationale भी लिखे, यहाँ 540B PaLM model (section 3.1 और limitations section)। फिर वह एक छोटे model, T5, को दोनों output करने के लिए train करता है।

### Rationales दूसरे task के रूप में, input के रूप में नहीं

Rationale इस्तेमाल करने के दो स्पष्ट तरीक़े हैं। उन्होंने दूसरा चुना।

1. **Input के रूप में।** Student को text के साथ rationale से label predict करना सिखाएँ। उसके लिए test के समय भी rationale लिखने को बड़ा model चाहिए, इसलिए बड़ा model production में अब भी चाहिए (section 3.2)।
2. **दूसरे output के रूप में।** Student को label और, अलग task के रूप में, rationale बनाना सिखाएँ। Loss, label loss और एक weight गुणा rationale loss है। एक task prefix model को बताता है कि क्या बनाना है: input पर `[label]` prefix label माँगता है, `[rationale]` prefix rationale माँगता है (section 3.2)।

दूसरे डिज़ाइन का मतलब है कि test के समय कोई rationale generate नहीं होती: student सिर्फ़ label predict करता है, और rationale-लिखने वाले task ने रास्ते में उसके सीखे को आकार दिया है। क़ीमत थोड़ा अतिरिक्त training compute है।

Rationale को दूसरे task के रूप में लेना मायने रखता है। जब लेखकों ने इसके बजाय rationale और label को एक target sequence में जोड़ा, तो student कभी-कभी सादे fine-tuning से भी बुरा रहा (Table 2, 220M T5, accuracy):

| विधि | e-SNLI | ANLI | CQA | SVAMP |
|---|---|---|---|---|
| Standard fine-tuning | 88.38 | 43.58 | 62.19 | 62.63 |
| Single task, rationale और label साथ में | 88.88 | 43.50 | 61.37 | 63.00 |
| Multi-task, label और rationale अलग | 89.51 | 49.58 | 63.29 | 65.50 |

ANLI और CQA पर single-task पंक्ति standard fine-tuning से नीचे है। उनकी पढ़त है कि rationales को उपयोगी बनने के लिए सावधानी से बरतना पड़ता है।

### इससे क्या मिला

ये पेपर के चार benchmarks, तीन तरह के tasks, T5 students और PaLM teacher पर नतीजे हैं:

- **कम data.** 220M T5 और मानव labels के साथ, distilling step-by-step ने पूरे e-SNLI set पर standard fine-tuning को हराया जबकि उसका सिर्फ़ 12.5% इस्तेमाल किया। पूरे-data standard fine-tuning को हराने के लिए ज़रूरी training examples में कमी ANLI पर 75%, CQA पर 25% और SVAMP पर 20% थी (section 4.1)। सिर्फ़ unlabeled data के साथ, unlabeled e-SNLI set का 12.5% ही, उसके पूरे पर standard task distillation को हराने के लिए काफ़ी था।
- **Teacher से छोटा.** Fine-tune किए गए 770M T5 ने ANLI पर training set के 80% के साथ few-shot prompted 540B PaLM को पीछे छोड़ा, जबकि उसी T5 की standard fine-tuning 100% के साथ भी PaLM की बराबरी नहीं कर पाई (abstract; section 4.3, Figure 8)। e-SNLI पर 220M model ने यह data के 0.1% के साथ कर दिखाया।
- **कमज़ोर rationale स्रोत ने भी मदद की।** 20B GPT-NeoX model की rationales ने PaLM की तुलना में छोटा उछाल दिया (ANLI 48.15 बनाम 49.58, standard fine-tuning 43.58) (Table 1)।

सीमाएँ ध्यान में रखें। Benchmarks classification और छोटे-उत्तर वाले tasks हैं, students task-विशिष्ट T5 models हैं, chat models नहीं, और तुलना का बिंदु prompted PaLM है। इनमें से कुछ भी नहीं बताता कि जब आप किसी सामान्य assistant को distil करते हैं तब क्या होता है। पेपर यह भी नोट करता है कि उसकी few-shot prompting को हर task के लिए उदाहरण demonstrations चाहिए।

### Orca: assistant के पैमाने पर explanation traces

Orca (Mukherjee et al., 2023) यही सहज बोध सामान्य instruction following पर लगाता है। उसकी प्रेरणा यह है कि जो student सिर्फ़ teacher के अंतिम उत्तरों पर train हो, वह teacher के सोचने के तरीक़े के बारे में थोड़ा ही सीखता है। दो विचार:

- **System messages के साथ explanation tuning.** हर training example system message, user query और teacher response की तिकड़ी है। उन्होंने हाथ से 16 system messages लिखे जो अलग response styles जगाते हैं, जैसे model से चरण-दर-चरण सोचने और अपने चरणों को सही ठहराने को कहना, और उन्हें FLAN-v2 संग्रह से लिए tasks पर sample किया (section 3.1)।
- **बीच के teacher के रूप में ChatGPT.** उन्होंने 5 million ChatGPT responses (FLAN-5M) इकट्ठा किए, फिर उनमें से 1 million queries के GPT-4 responses (FLAN-1M) लिए, और Orca को पहले ChatGPT data पर और फिर GPT-4 data पर train किया। उनके बताए कारण capacity gap हैं, क्योंकि 13B student GPT-4 से बहुत छोटा है, और लागत तथा समय: उन्होंने ChatGPT से GPT-4 के मुक़ाबले 5 गुना ज़्यादा इकट्ठा किया (section 3.1.3)।

यह जानबूझकर इस्तेमाल किया गया [teacher assistant](../GLOSSARY.md) है, 5M फिर 1M वाले पाठ्यक्रम के साथ। लेखक बताते हैं कि Orca-13B, Big-Bench Hard पर Vicuna-13B से 100% से ज़्यादा और AGIEval पर 42% ऊपर है, BBH पर ChatGPT के बराबर, और optimized system message इस्तेमाल करते हुए professional exams पर ChatGPT से लगभग 4 अंक पीछे (abstract)। वे यह भी बताते हैं कि GPT-4 judge के तहत Vicuna, ChatGPT के क़रीब दिखता है (92%) पर मानव labels के विरुद्ध exams पर सिर्फ़ 64% और BBH पर 48% बनाए रखता है, इसीलिए उन्होंने reasoning benchmarks पर evaluate किया।

ये Orca के लेखकों के अपने evaluations हैं, उनके चुने benchmarks पर। Explanation traces क्षमता का फ़ासला पाटती हैं या मुख्यतः style का, यह पाठ 18 का सवाल है।

### Reasoning models अगले track के हैं

किसी reasoning model को उसकी लंबी chains of thought पर fine-tune करके distil करना [Post-training ट्रैक](../../post-training/) में सिखाया जाता है। यहाँ rationales छोटी व्याख्याएँ हैं जो छोटे task model की मदद करती हैं, और reasoning-model distillation उसी विचार का बड़ा मामला है।

## अभ्यास

1. ▢ Distilling Step-by-Step में, test के समय rationale की ज़रूरत क्यों नहीं होती?

    - a) Rationale label token के भीतर ही छिपी होती है
    - b) Student training set की हर rationale याद कर लेता है
    - c) Teacher production में हर rationale दोबारा लिखता है
    - d) Model के train हो जाने पर label task अकेला चलता है

<details markdown="1"><summary>जाँचें</summary>

**d)** Rationale अपने prefix के साथ दूसरा output है, जो label के साथ train होती है, इसलिए test के समय आप सिर्फ़ label माँगते हैं। (b) विधि का काम नहीं है। (c) उस ठुकराए गए डिज़ाइन का वर्णन करता है जहाँ rationale एक input है, जो बड़े model को production में रखता है। (a) ऐसा तंत्र गढ़ता है जो पेपर में नहीं है।

</details>

2. ▢ Table 2 में, CQA के लिए single-task पंक्ति 61.37 है और standard fine-tuning 62.19। यह rationales को अनगढ़ तरीक़े से जोड़ने के बारे में क्या कहता है?

<details markdown="1"><summary>जाँचें</summary>

Rationale को एक sequence के रूप में target में जोड़ने से student CQA पर कुछ न करने से भी बुरा हो गया (और ANLI पर थोड़ा-सा बुरा, 43.50 बनाम 43.58)। फ़ायदा इस पर निर्भर करता है कि rationale कैसे इस्तेमाल हुई, अलग task के रूप में, इस पर नहीं कि rationales थीं भी। यह पेपर का अपनी setup पर नतीजा है।

</details>

3. ▢ एक student को 5 million ChatGPT responses मिलते हैं और फिर 1 million GPT-4 responses। अनुपात क्या है, और लेखक क्रम और आकार के लिए कौन-से दो कारण देते हैं?

<details markdown="1"><summary>जाँचें</summary>

5 से 1। वे capacity gap देते हैं, क्योंकि student की क्षमता के ज़्यादा क़रीब वाला बीच का teacher नक़ल को आसान करता है, और लागत तथा समय, क्योंकि ChatGPT से query करना तेज़ और सस्ता था, इसलिए उन्होंने उससे GPT-4 के मुक़ाबले 5 गुना ज़्यादा इकट्ठा किया।

</details>

4. ▢ आपकी टीम 770M T5 बनाम 540B PaLM वाला नतीजा पढ़ती है और प्रस्ताव रखती है कि किसी सामान्य chat assistant को उसी तरह 770M model के साथ distil किया जाए। आप क्या जवाब देंगे?

<details markdown="1"><summary>संकेत</summary>

Task का प्रकार, student का प्रकार और तुलना किससे है, यह देखें।

</details>

<details markdown="1"><summary>जाँचें</summary>

नतीजा चार benchmarks के लिए है, task-विशिष्ट T5 students और baseline के रूप में few-shot prompted PaLM के साथ, और 80% data का आँकड़ा ANLI के लिए है। वह किसी सामान्य assistant को कवर नहीं करता। Chat model के प्रस्ताव को अपने मायने रखने वाले tasks पर अपना evaluation चाहिए, बिना rationales के train हुए baseline के विरुद्ध।

</details>

5. ▢ एक teacher आत्मविश्वास से भरी पर ग़लत rationale और ग़लत label लिखता है। इस पाठ की दो विधियों में से कौन-सी student को दोनों पर train करेगी, और आप training से पहले क्या करेंगे?

<details markdown="1"><summary>जाँचें</summary>

दोनों करेंगी: Distilling Step-by-Step में rationale और label दोनों targets हैं, और Orca में explanation trace response का हिस्सा है। पहले filter करें। जहाँ checker मौजूद हो, सिर्फ़ वे examples रखें जिनका उत्तर सही सत्यापित हो; वरना sample करके जाँचें। पाठ 12 इसे कवर करता है।

</details>

## असली दुनिया का अभ्यास

- [ ] Orca पेपर में Table 2 ढूँढें और 16 system messages पढ़ें। तीन चुनें और अनुमान लगाएँ कि हर एक के तहत वही query अलग तरह से कैसे जवाब पाएगी।
- [ ] किसी ऐसे task के लिए rationale prompt लिखें जिसे आप जानते हैं, दो हल किए उदाहरणों के साथ, और उसे अपने पास किसी भी model पर चलाएँ। एक rationale को हाथ से उस ग़लती के लिए जाँचें जो अंतिम उत्तर छिपाता है।
- [ ] कल: बिना नोट्स के समझाएँ कि rationale input नहीं बल्कि दूसरा output क्यों है, और इससे test-time की लागत पर क्या असर पड़ता है।

## आगे बढ़ने के लिए

- [Sequence और Synthetic Data शीट](../reference/sequence-and-synthetic-data.md)
- [पेपर: "Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes", Hsieh et al., 2023](https://arxiv.org/abs/2305.02301)
- [पेपर: "Orca: Progressive Learning from Complex Explanation Traces of GPT-4", Mukherjee et al., 2023](https://arxiv.org/abs/2306.02707)
- [Post-training ट्रैक](../../post-training/)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
