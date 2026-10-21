---
title: "14. Reasoning Model को Distil करके छोटा करना"
description: "32B model को सीधे RL से train करना, उसे बड़े model के अपने reasoning traces पर fine-tune करने से हार गया"
type: lesson
---

# पाठ 14. Reasoning Model को Distil करके छोटा करना

**मिशन से संबंध:** "बता सकें कि reasoning model का व्यवहार कैसे पैदा हुआ, सिर्फ़ यह नहीं कि उसे कैसे prompt करें" "सफलता कैसी दिखती है" का वह बिंदु है जिसकी सेवा यह चरण करता है। पाठ 13 ने DeepSeek-R1-Zero की शुद्ध-RL training और उसकी पठनीयता की समस्या कवर की; यह पाठ DeepSeek-R1 का इलाज कवर करता है, और उस इलाज को छोटे models में distil करने का चौंकाने वाला नतीजा।
**मुख्य स्रोत:** [पेपर: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
**पूर्व-आवश्यकताएँ:** [पाठ 13](0013-chain-of-thought-rl-what-deepseek-r1-zero-did-with-rule-based-rewards.md)

## वार्म-अप

1. ▢ DeepSeek-R1-Zero की reasoning की लंबाई उसके लिए किसी साफ़ reward term के बिना training के दौरान काफ़ी बढ़ी। उस बढ़त को असल में किसने चलाया?

<details markdown="1"><summary>जाँचें</summary>

Accuracy reward अंतिम उत्तर सही होने को पुरस्कृत करता था, और लंबी, ज़्यादा सावधान reasoning से ज़्यादा सही उत्तर निकलते थे, इसलिए RL training ने साइड-इफ़ेक्ट के रूप में उसे चुना, इसलिए नहीं कि reasoning की लंबाई सीधे पुरस्कृत थी।

</details>

2. ▢ DeepSeek-R1-Zero ने मज़बूत reasoning हासिल की पर ख़राब पठनीयता और भाषाओं के मिश्रण से जूझा। उसका reward जैसे बना था, उसे देखते हुए यह हैरान करने वाला क्यों नहीं है?

<details markdown="1"><summary>जाँचें</summary>

Reward सिर्फ़ अंतिम उत्तर की शुद्धता और thinking tags की मौजूदगी जाँचता था; पठनीयता और एक भाषा में बने रहना कभी score का हिस्सा नहीं थे, इसलिए training में किसी चीज़ ने उनमें से किसी को नहीं चुना।

</details>

## यह जानें

### Reasoning खोए बिना पठनीयता ठीक करना

DeepSeek-R1 DeepSeek-AI का DeepSeek-R1-Zero की पठनीयता की समस्या का जवाब है: base model से शुद्ध RL के बजाय, वह **cold-start data** जोड़ता है, यानी reasoning-केंद्रित RL चरण से पहले इस्तेमाल हुआ चुना हुआ थोड़ा-सा data, साथ ही उस RL चरण के इर्द-गिर्द बने कई training चरण, न कि एक अकेला pass। इससे model को ऐसा शुरुआती बिंदु मिलता है जो पठनीय, एक-भाषा का output देने के पहले से क़रीब है, उसके बाद उसी तरह की rule-based, reasoning-केंद्रित RL लगाई जाती है जिसने DeepSeek-R1-Zero की क्षमताएँ पैदा की थीं। DeepSeek-AI रिपोर्ट करते हैं कि नतीजा reasoning tasks पर OpenAI के o1 के बराबर प्रदर्शन पाता है, जबकि शुद्ध-RL वाले संस्करण की पठनीयता और भाषा-मिश्रण की समस्याओं से बचता है।

### Distillation: छोटे models को बड़े model के अपने reasoning traces पर fine-tune करना

DeepSeek-R1 को train करने से अलग, DeepSeek-AI छह छोटे dense models बनाते हैं, 1.5B से 70B parameters तक, मौजूदा Qwen और Llama base models पर बने। तरीक़ा सीधा है: हर छोटे base model को DeepSeek-R1 की अपनी training pipeline से generate किए गए 8,00,000 चुने हुए samples पर fine-tune करें। यह **सामान्य supervised fine-tuning** (चरण 2) है ऐसे data पर जो संयोग से किसी बड़े reasoning model के अपने outputs से बना है, कोई नया algorithm नहीं। DeepSeek-AI साफ़ कहते हैं कि वे इन distilled models पर सिर्फ़ SFT लगाते हैं, कोई RL चरण बिल्कुल नहीं, भले ही वे ध्यान दिलाते हैं कि RL चरण संभवतः उन्हें और बेहतर कर सकता है; इस बार उनका लक्ष्य यह दिखाना था कि अकेला distillation पहले ही अच्छा काम करता है, और छोटे models के लिए आगे के RL चरण को भविष्य के काम पर छोड़ दिया।

### वह नतीजा जो इसे गंभीरता से लेने लायक़ बनाता है

DeepSeek-AI ने सीधी तुलना की जो एक स्वाभाविक सवाल का जवाब देती है: क्या छोटा model वही reasoning क्षमता उस पर सीधे वही बड़े पैमाने की RL चलाकर पा सकता है, उस बड़े model से distil करने के बजाय जो पहले ही उस RL से गुज़र चुका है? उन्होंने 32B base model को उसी बड़े पैमाने की RL के 10,000 से ज़्यादा steps से train किया जो DeepSeek-R1-Zero ने इस्तेमाल की, और "DeepSeek-R1-Zero-Qwen-32B" बना, और उसकी तुलना "DeepSeek-R1-Distill-Qwen-32B" से की, यानी वही 32B base model जिसे इसके बजाय DeepSeek-R1 के distilled reasoning traces पर fine-tune किया गया। AIME 2024 गणित benchmark पर सीधे-RL से train हुआ model 47.0% pass@1 तक पहुँचा; distilled model 72.6% तक, एक बड़ा अंतर जो उनके रिपोर्ट किए हर benchmark पर उसी दिशा में रहा। DeepSeek-AI का अपना निष्कर्ष: ज़्यादा सक्षम model को distil करके नीचे लाना किफ़ायती भी है और बहुत कारगर भी, जबकि छोटे model को सीधे बड़े पैमाने की RL से train करने के लिए भारी compute चाहिए और फिर भी हो सकता है वह उसकी बराबरी न करे जो distillation उस model से मुफ़्त में पा लेता है जो वह काम पहले ही कर चुका है।

### Distillation की सीमा

DeepSeek-AI सावधान हैं कि इसे बढ़ाकर न कहें: distillation वह चीज़ सस्ते में आगे पहुँचाता है जो मज़बूत model पहले से करना जानता है, पर वह अपने-आप क्षमता को उससे आगे नहीं ले जाता जो वह मज़बूत model पहले ही कर सकता है। उनका अपना दूसरा निष्कर्ष यह सीधे कहता है: मौजूदा सीमा से आगे जाने के लिए अब भी ज़्यादा सक्षम base models और उन पर लगाई बड़े पैमाने की reinforcement learning चाहिए, न कि जो पहले से मौजूद है उसका और distillation। Distillation मौजूदा क्षमता को छोटे models तक फैलाने का सस्ता तरीक़ा है, उस model से आगे नई क्षमता गढ़ने का तरीक़ा नहीं जिससे distil किया जा रहा है।

## अभ्यास

1. ▢ एक टीम को छोटा, सक्षम reasoning model चाहिए और वह दो रास्तों पर विचार करती है: मौजूदा बड़े reasoning model से SFT के ज़रिए distil करना, या छोटे model पर उसके base checkpoint से सीधे बड़े पैमाने की RL चलाना। DeepSeek-AI की अपनी 32B तुलना के अनुसार, कौन-सा रास्ता मज़बूत reasoning प्रदर्शन तक पहुँचने की उम्मीद देगा, और AIME 2024 पर लगभग कितने के अंतर से?

<details markdown="1"><summary>जाँचें</summary>

Distillation। DeepSeek-R1-Distill-Qwen-32B AIME 2024 पर 72.6% pass@1 तक पहुँचा, जबकि DeepSeek-R1-Zero-Qwen-32B, जो उसी base model पर सीधे बड़े पैमाने की RL के 10,000 से ज़्यादा steps से train हुआ, 47.0% पर रहा।

</details>

2. ▢ इस पाठ के अर्थ में "distillation" यांत्रिक रूप से ठीक क्या है?

    - a) छोटे model पर लगाया गया नया RL algorithm
    - b) बड़े, पहले से RL-trained reasoning model के generate किए चुने हुए output samples पर छोटे base model का सामान्य supervised fine-tuning
    - c) बड़े model के weights को सीधे छोटे architecture में संपीड़ित करना
    - d) बड़े और छोटे models को inference के समय साथ चलाना

<details markdown="1"><summary>जाँचें</summary>

**b)** ठीक वही तरीक़ा है जो DeepSeek-AI बताते हैं: DeepSeek-R1 की अपनी pipeline से 800k चुने हुए samples पर SFT, कोई RL चरण नहीं। (a), (c) और (d) हर एक किसी दूसरी तकनीक का वर्णन करते हैं जो इस पाठ का तरीक़ा नहीं है।

</details>

3. ▢ DeepSeek-AI के अपने दो निष्कर्षों के अनुसार, क्या अकेला distillation किसी छोटे model की reasoning क्षमता को उससे आगे धकेल सकता है जो DeepSeek-R1 ख़ुद, यानी जिस model से distil हो रहा है, पहले ही कर सकता है?

<details markdown="1"><summary>जाँचें</summary>

नहीं। उनका दूसरा निष्कर्ष सीधे कहता है कि मौजूदा सीमा से आगे बढ़ने के लिए अब भी ज़्यादा सक्षम base models और बड़े पैमाने की RL चाहिए, ज़्यादा distillation नहीं; distillation मौजूदा क्षमता को सस्ते में फैलाता है, स्रोत model की अपनी क्षमता से आगे नई क्षमता नहीं गढ़ता।

</details>

4. ▢ DeepSeek-R1 ने DeepSeek-R1-Zero की ठीक वही recipe बड़े पैमाने पर दोहराने के बजाय cold-start data और multi-stage training क्यों जोड़ा?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि DeepSeek-R1-Zero की reasoning ख़राब पठनीयता और भाषा-मिश्रण के साथ आई थी जिसे ठीक करने का शुद्ध rule-based RL ने model को कोई प्रोत्साहन नहीं दिया; cold-start data और multi-stage training उस पठनीयता की समस्या को सीधे सँभालते हैं, ऐसी recipe को बड़ा करने की कोशिश करने के बजाय जिसने उसे पहले ही कभी चुना नहीं था।

</details>

## असली दुनिया का अभ्यास

- [ ] DeepSeek-R1 technical report की Table 6 खोजें (ऊपर का पेपर link है) और AIME 2024 के अलावा कम-से-कम एक benchmark पर DeepSeek-R1-Zero-Qwen-32B और DeepSeek-R1-Distill-Qwen-32B का अंतर नोट करें।
- [ ] कोई प्रकाशित distilled reasoning model खोजें (कई ऐसे नाम से जारी होते हैं जो बताता है कि उसे किससे distil किया गया) और जाँचें कि उसका model card कहता है कि वह अकेले SFT से train हुआ, जोड़े गए RL चरण से, या दोनों से।
- [ ] कल: किसी काल्पनिक project के लिए जिसे छोटा, सक्षम reasoning model चाहिए, तय करें कि बड़े reasoning model से distillation अपनाएँगे या छोटे model पर सीधे RL, और एक वाक्य लिखें जो अपने चुनाव के लिए इस पाठ के सबूत का हवाला दे।

## आगे बढ़ने के लिए

- [पेपर: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
- [Distillation: Sequence और Synthetic Data शीट](../../distillation/reference/sequence-and-synthetic-data.md): सामान्य रूप से distillation, जिसका reasoning-model वाला मामला यह पाठ है
- [संसाधन](../RESOURCES.md)

---

चरण 7 ने कवर किया कि reasoning का व्यवहार RL से कैसे पैदा होता है, और एक बार मौजूद हो जाने पर उसे छोटे models तक कितनी सस्ते में फैलाया जा सकता है। चरण 8 उसी तकनीक-परिवार के अलग लक्ष्य की ओर मुड़ता है: reasoning क्षमता नहीं, बल्कि safety और इनकार का व्यवहार।

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
