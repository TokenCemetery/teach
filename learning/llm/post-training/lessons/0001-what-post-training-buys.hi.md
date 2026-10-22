---
title: "1. Post-Training से क्या मिलता है"
description: "100 गुना छोटे aligned model ने कच्चे base model को हरा दिया, उस काम में जो users को असल में चाहिए था"
type: lesson
---

# पाठ 1. Post-Training से क्या मिलता है

**मिशन से संबंध:** "किसी टीम के data, बजट और लक्षित व्यवहार को देखकर अकेला SFT, DPO, RLHF-PPO और GRPO में से चुनें, और उस चुनाव का बचाव करें" मिशन का केंद्रीय फ़ैसला है, और इसकी शुरुआत इससे होती है कि पता हो post-training किस समस्या को हल करती है जिसे अकेली pretraining हल नहीं करती।
**मुख्य स्रोत:** [पेपर: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**पूर्व-आवश्यकताएँ:** कोई नहीं

## यह जानें

### Base model अपने-आप अच्छा assistant नहीं होता

Pretrained base model, यानी `llm/pretraining` की पूरी राह का नतीजा, इसलिए train होता है कि जो भी text distribution उसने देखा, उसमें अगला संभावित token क्या होगा, यह अनुमान लगा सके। यह वही हुनर नहीं है जो user के असली निर्देश मानने के लिए चाहिए, और base model को बड़ा करने भर से यह खाई नहीं भरती। Ouyang et al. इसे साफ़ कहते हैं: "making language models bigger does not inherently make them better at following a user's intent." बड़ा base model ऐसे outputs दे सकता है जो असत्य हों, किसी काम के न हों, या जो माँगा गया उससे अलग हों, इसलिए नहीं कि उसमें क्षमता की कमी है, बल्कि इसलिए कि pretraining में किसी चीज़ ने उसे ख़ास तौर पर यह नहीं सिखाया कि उस क्षमता को वैसे इस्तेमाल करे जैसा user चाहता है।

### मुख्य नतीजा

Ouyang et al. का केंद्रीय नतीजा इस खाई का आकार ठोस बना देता है: human evaluations में उनके 1.3-अरब-parameter **InstructGPT** model के outputs को 175-अरब-parameter GPT-3 model के outputs पर तरजीह मिली, जिससे वह शुरू हुआ था, जबकि उसमें लगभग 100 गुना कम parameters थे। Post-training ने model को किसी कच्चे अर्थ में न बड़ा बनाया, न ज़्यादा स्मार्ट; उसने इतना बदला कि model की मौजूदा क्षमता किस ओर लगाई गई है, और human raters के लिए वह दिशा पैमाने के दो और गुना बढ़ने से ज़्यादा मायने रखती थी।

### तीन चरणों वाली pipeline

Ouyang et al. की recipe, जिसके सामने बाद का ज़्यादातर RLHF काम आज भी बयान किया जाता है, के तीन चरण हैं:

1. **Demonstrations इकट्ठा करें, supervised policy train करें।** Human labelers अलग-अलग prompts के लिए चाहे गए व्यवहार के उदाहरण लिखते हैं; base model को इन पर सामान्य supervised learning से fine-tune किया जाता है। यह चरण **SFT** (supervised fine-tuning) है, चरण 2 का विषय।
2. **Comparisons इकट्ठा करें, reward model train करें।** Labelers एक ही prompt के लिए SFT model के कई outputs को rank करते हैं; एक अलग model, यानी **reward model**, यह अनुमान लगाना सीखता है कि इंसान कौन-सा output पसंद करेगा। यह चरण 3 का विषय है।
3. **PPO से policy को reward model के विरुद्ध optimize करें।** SFT model को reinforcement learning से और fine-tune किया जाता है, जिसमें reward model के score को वह reward signal माना जाता है जिसे maximize करना है। यह चरण 4 का विषय है, और चरण 2 और 3 को दोहराया जा सकता है: मौजूदा सबसे अच्छी policy पर और comparisons इकट्ठा करके नया reward model और बदले में नई policy train करें।

### Alignment tax, परिचय

Post-training काम करे तब भी लागत से मुक्त नहीं है। Ouyang et al. ने पाया कि उनके aligned models कुछ public NLP benchmarks (अन्य के साथ एक reading-comprehension benchmark, एक discrete-reasoning benchmark, एक commonsense benchmark और एक translation benchmark) पर मूल base model से थोड़ा बुरा चले। वे इसे **alignment tax** कहते हैं: कुछ क्षमताओं पर असली, मापी गई लागत, जो उस व्यवहार के बदले चुकाई जाती है जिसे कुल मिलाकर इंसानों ने ज़्यादा पसंद किया। उन्हें एक आंशिक इलाज भी मिला: PPO updates को उन updates के साथ मिलाना जो मूल pretraining data की likelihood बढ़ाते हैं (जिसे वे **PPO-ptx** कहते हैं), खोया हुआ ज़्यादातर प्रदर्शन लौटा लाया, और post-training जिन preference फ़ायदों के लिए बनी थी उन्हें छोड़ना नहीं पड़ा। Tax न स्थिर है, न टाला न जा सकने वाला; यह मापा गया लेन-देन है जिसे बाद की तकनीकें आंशिक रूप से चुका सकती हैं।

### आगे का नक़्शा

अकेला SFT (चरण 2) सबसे सस्ता चरण है और पहले ही बहुत-सा व्यवहार बदल देता है। Reward modeling और PPO के ज़रिए RLHF (चरण 3 और 4) उसके ऊपर दूसरा, reinforcement-learning वाला चरण जोड़ते हैं, असली अतिरिक्त लागत और जटिलता के साथ। Direct Preference Optimization (चरण 5) बाद में लगभग वैसा ही नतीजा पाना चाहता है, अलग reward model या RL loop के बिना। GRPO (चरण 6) RL वाले तरीक़े को ऐसे tasks के लिए ढालता है जिनका उत्तर verifiable, यानी जाँचा जा सकने वाला हो, जैसे गणित या code, न कि इंसान की पसंद का फ़ैसला। Safety-specific tuning (चरण 8) उसी तकनीक-परिवार को अलग लक्ष्य पर लगाती है। इनमें से हर एक उसी बुनियादी सवाल का अलग जवाब है जो इस पाठ ने खोला: model की मौजूदा क्षमता को उस ओर कैसे लगाया जाए जो इंसान को असल में चाहिए, और किस लागत पर।

## अभ्यास

1. ▢ Human evaluations में InstructGPT के 1.3-अरब-parameter model को 175-अरब-parameter GPT-3 model पर तरजीह मिली। यह नतीजा कच्चे parameter count और user के इरादे को मानने में अच्छा होने के रिश्ते के बारे में क्या दलील देता है?

<details markdown="1"><summary>जाँचें</summary>

कि दोनों एक ही चीज़ नहीं हैं। Post-training से काम की ओर लगाया गया बहुत छोटा model, उस बहुत बड़े model से जीत गया जिसके साथ ऐसा नहीं हुआ था। अकेले पैमाने ने वह व्यवहार नहीं दिया जो इंसानों ने पसंद किया; मायने यह रखता था कि model की क्षमता किस ओर लगाई गई।

</details>

2. ▢ Ouyang et al. की pipeline के इन तीन चरणों को क्रम में रखें: (a) model outputs की human comparisons पर reward model train करना, (b) PPO से policy को reward model के विरुद्ध fine-tune करना, (c) इंसानों के लिखे demonstrations पर base model को fine-tune करना।

<details markdown="1"><summary>जाँचें</summary>

c, a, b: पहले demonstrations इकट्ठा करके supervised policy train करें (SFT), फिर comparisons इकट्ठा करके reward model train करें, फिर उसी reward model के विरुद्ध policy को PPO से optimize करें।

</details>

3. ▢ Ouyang et al. की अपनी खोज के अनुसार alignment tax क्या है, और उन्हें क्या मिला जो उसे आंशिक रूप से संतुलित कर सकता था?

<details markdown="1"><summary>जाँचें</summary>

कुछ public NLP benchmarks पर प्रदर्शन में मापी गई गिरावट, जो post-training के alignment फ़ायदों के साथ आई, जबकि human raters ने कुल मिलाकर aligned model को ज़्यादा पसंद किया। PPO updates को उन updates के साथ मिलाने (PPO-ptx) से, जो मूल pretraining data की likelihood बढ़ाते हैं, खोया हुआ ज़्यादातर प्रदर्शन लौट आया और preference फ़ायदे छोड़ने नहीं पड़े।

</details>

4. ▢ इनमें से कौन-सा सबसे अच्छा बताता है कि Ouyang et al. की pipeline में SFT, reward modeling और RLHF-PPO हर एक क्या करता है?

    - a) SFT इंसानों के लिखे demonstrations की सीधे नक़ल करता है; reward modeling यह अनुमान लगाना सीखती है कि outputs में से इंसान को कौन-सा पसंद आएगा; RLHF-PPO उस सीखे हुए preference signal के विरुद्ध policy को optimize करता है
    - b) तीनों चरण reward model को ही train करते हैं, बढ़ते पैमाने पर
    - c) SFT और RLHF-PPO एक ही चरण हैं, स्थिरता के लिए दो बार चलाया गया
    - d) PPO शुरू होने से पहले reward modeling base model को पूरी तरह बदल देती है

<details markdown="1"><summary>जाँचें</summary>

**a)** तीनों चरणों के बीच काम का असली बँटवारा है। (b), (c) और (d) हर एक ऐसे चरणों को एक में समेट देते हैं जो सचमुच अलग काम करते हैं: demonstrations की नक़ल, preference signal सीखना, और उस signal के विरुद्ध optimize करना तीन अलग चरण हैं, एक ही चरण का दोहराव नहीं।

</details>

## असली दुनिया का अभ्यास

- [ ] किसी open "instruct" या "chat" model का model card या technical report खोजें, और नोट करें कि वह Ouyang et al. के तीन चरणों में से किन्हें साफ़ तौर पर इस्तेमाल करने की बात कहता है (SFT, reward model, और/या RL), और अगर किसी की जगह उसने कोई दूसरी विधि ली है तो कौन-सी।
- [ ] InstructGPT पेपर का abstract पढ़ें (ऊपर link है) और एक वाक्य में लिखें कि Ouyang et al. ने alignment की ज़रूरत के पीछे कौन-से ख़ास नुक़सान (सिर्फ़ "किसी काम का नहीं" से आगे) गिनाए हैं।
- [ ] कल: आगे देखे बिना चरण 2 के लिए एक वाक्य की भविष्यवाणी लिखें: यह मानते हुए कि SFT को इंसानों के लिखे demonstrations की सीधी नक़ल बताया गया है, अगर कोई naive SFT implementation training example के हर token पर, prompt समेत, train करे तो आप उससे किस तरह की ग़लती की उम्मीद करेंगे?

## आगे बढ़ने के लिए

- [पेपर: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
