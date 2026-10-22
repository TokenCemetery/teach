---
title: "16. व्यवहार में On-Policy Distillation"
description: "On-policy distillation प्रति step कितना महँगा है, क्या देता है, और Qwen3 ने अपने छोटे models के लिए इसे कैसे इस्तेमाल किया"
type: lesson
---

# पाठ 16. व्यवहार में On-Policy Distillation

**मिशन से संबंध:** मिशन आपसे माँगता है कि आप बता सकें कि on-policy distillation अपनी लागत कब वसूल करता है, यानी गिनें कि एक step की क्या लागत है, वह कौन-सा signal लौटाता है, और एक production टीम ने विकल्प के मुक़ाबले क्या मापा।
**मुख्य स्रोत:** [पेपर: "Qwen3 Technical Report", Qwen Team, 2025](https://arxiv.org/abs/2505.09388), section 4.5 और section 4.7 में on-policy distillation की चर्चा
**पूर्व-आवश्यकताएँ:** [पाठ 8](0008-sequence-level-distillation.md), [पाठ 14](0014-exposure-bias.md), [पाठ 15](0015-gkd-and-minillm.md), [Off-policy distillation](../GLOSSARY.md), [On-policy distillation](../GLOSSARY.md)

## वार्म-अप

1. ▢ GKD में student data fraction lambda क्या नियंत्रित करता है, और उसके दो चरम मान क्या हैं?

<details markdown="1"><summary>जाँचें</summary>

यह उस संभावना को नियंत्रित करता है कि कोई step तय dataset की जगह student-generated sequences पर train करे। Lambda 0 तय data पर supervised distillation है और lambda 1 पूरी तरह on-policy।

</details>

2. ▢ Qwen3 का पहला distillation चरण उन outputs पर train करता है जो teacher ने generate किए। पाठ 8 का कौन-सा शब्द इसे नाम देता है, और क्या यह on-policy है?

<details markdown="1"><summary>जाँचें</summary>

Sequence-level distillation, Qwen3 report के शब्दों में "response distillation"। यह off-policy है: sequences teacher ने तय किए थे, student ने नहीं लिखे।

</details>

3. ▢ Exposure bias इस बात का mismatch है कि student किसके prefixes देखता है। उस एक घटक का नाम बताएँ जो on-policy step को teacher से चाहिए और fixed-text step को नहीं।

<details markdown="1"><summary>जाँचें</summary>

Student के अपने sequence के हर position पर tokens पर उसका distribution, जिसका मतलब है कि training के दौरान teacher model को student के output पर चलाना पड़ता है। जो text teacher पहले ही लिख चुका है वह यह नहीं देता।

</details>

## यह जानें

### एक step की लागत क्या है

संग्रहीत teacher text वाले off-policy step की लागत तय sequences पर student का एक forward और backward pass है। संग्रहीत teacher logits वाला off-policy step disk से पढ़ना जोड़ता है, और भंडारण की लागत पाठ 7 की है।

On-policy step काम जोड़ता है, और उसे क्रम से सूचीबद्ध करना सार्थक है:

| Step | काम | टिप्पणी |
|---|---|---|
| 1 | Student हर prompt के लिए एक sequence generate करता है | क्रमिक decoding। teacher के करने से सस्ता, क्योंकि student छोटा है (GKD, section 3.1) |
| 2 | Teacher तैयार sequence पर एक forward pass चलाता है | एक समानांतर pass, generation नहीं। Teacher का memory में होना या पहुँच में होना ज़रूरी है |
| 3 | Student forward और backward चलाता है और divergence निकाला जाता है | Off-policy step जैसा ही |

पहली दो पंक्तियों का तय text वाला कोई off-policy समकक्ष नहीं है। पेपर की अपनी दक्षता वाली टिप्पणी इसके बजाय SeqKD के बारे में है: instruction-tuning experiment में GKD ने SeqKD नहीं चलाया "training के दौरान teacher से data generate करने की उसकी computational अक्षमता के कारण" (section 4.4)। यहाँ step 1 छोटा model इस्तेमाल करता है, जो उस सौदे का सस्ता पक्ष है। वह लागत-तुलना पेपर का कथन है, और ऊपर की तीन-पंक्ति वाली तालिका काम का मेरा हिसाब है।

### सघन signal बनाम विरल reward

Distillation, छोटे model को उसके अपने samples पर बेहतर करने का अकेला तरीक़ा नहीं है। Reinforcement learning भी model के अपने sequences पर train करती है, पर हर पूरे sequence को scalar reward से score करती है। GKD का section 3.2 combined objective को reward के साथ `r(y)` के रूप में लिखता है, हर sequence के लिए एक अकेली संख्या।

On-policy distillation हर token के लिए एक score लौटाता है, उस position पर teacher के distribution से लिया हुआ। यह प्रति sample ज़्यादा सघन signal है। सघन का मतलब है हर generate किए sequence में ज़्यादा जानकारी। इसका मतलब यह नहीं कि teacher सही है, जिस पर पाठ 18 लौटता है।

व्यावहारिक नतीजा एक ही दिशा में जाता है। RL बिना किसी मज़बूत model के भी model को सुधार सकती है, क्योंकि उसे सिर्फ़ reward चाहिए। On-policy distillation को मज़बूत teacher का मौजूद होना चाहिए।

### Qwen3 ने इसे कैसे इस्तेमाल किया

Qwen3 report अपने flagship models के लिए चार-चरण वाली post-training pipeline बताती है, और हल्के models के लिए अलग "strong-to-weak distillation": पाँच dense models (0.6B, 1.7B, 4B, 8B और 14B) और एक mixture-of-experts model (30B-A3B)। प्रेरणा लागत थी: distillation "हर छोटे-पैमाने के model के लिए अलग से पूरी चार-चरण training करने की ज़रूरत को ख़त्म करता है" (section 4)।

छोटे models दो चरणों में distil होते हैं (section 4.5):

| चरण | Data | Training signal |
|---|---|---|
| Off-policy | Thinking और non-thinking, दोनों modes में generate हुए teacher outputs | Response distillation, बुनियादी reasoning कौशल और modes बदलने की क्षमता देने के लिए |
| On-policy | Student किसी भी mode में responses generate करता है | Student को teacher (Qwen3-32B या Qwen3-235B-A22B) के logits से मिलाकर fine-tune किया जाता है ताकि KL divergence कम हो |

क्रम पढ़ें। Off-policy चरण पहले आता है, और report कहती है कि वह on-policy चरण के लिए "ठोस नींव" रखता है। यह GKD की इस टिप्पणी से मेल खाता है कि on-policy training ऐसा student मानती है जो पहले से स्वीकार्य sequences generate कर सके। यह दो-चरण का कार्यक्रम है, GKD का प्रति-batch lambda मिश्रण नहीं।

### RL से तुलना

Section 4.7 on-policy distillation की तुलना Qwen3-8B पर सीधे reinforcement learning से करता है। दोनों उसी off-policy distilled checkpoint से शुरू होते हैं, और तुलना सिर्फ़ math और code queries इस्तेमाल करती है। Table 21 बताती है, कोष्ठक में pass@64 के साथ जहाँ report एक देती है:

| विधि | AIME'24 | AIME'25 | MATH500 | LiveCodeBench v5 | MMLU-Redux | GPQA-Diamond | GPU hours |
|---|---|---|---|---|---|---|---|
| Off-policy distillation | 55.0 (90.0) | 42.8 (83.3) | 92.4 | 42.0 | 86.4 | 55.6 | दिया नहीं गया |
| साथ में reinforcement learning | 67.6 (90.0) | 55.5 (83.3) | 94.8 | 52.9 | 86.9 | 61.3 | 17,920 |
| साथ में on-policy distillation | 74.4 (93.3) | 65.5 (86.7) | 97.0 | 60.3 | 88.3 | 63.3 | 1,800 |

तालिका के हर benchmark पर on-policy distillation ने RL से ऊँचा score किया, और उसने GPU hours का लगभग दसवाँ हिस्सा इस्तेमाल किया: 17,920 भाग 1,800 है 9.96। Report इसे RL से काफ़ी बेहतर प्रदर्शन के रूप में पढ़ती है, लगभग दसवें हिस्से के GPU hours पर। वह यह भी नोट करती है कि AIME पर pass@64 distillation के बाद बढ़ा और RL के बाद नहीं बदला, जिसे वह इस सबूत के रूप में लेती है कि teacher logits से distil करना student की exploration space बढ़ाता है।

### उस तालिका पर कितना भरोसा करें

यह एक report है, एक student आकार, सिर्फ़ math और code queries, और लेखकों ने अपने ही दो तरीक़ों की तुलना की। Report नहीं बताती कि 8B तुलना के लिए कौन-सा teacher इस्तेमाल हुआ। मुझे यह कथन नहीं मिला कि GPU-hour आँकड़ों में teacher चलाना शामिल है या नहीं, इसलिए मान न लें कि है। तुलना में RL की विधि वर्णित नहीं है, इसलिए बेहतर-tune किया RL run फ़ासले का कुछ हिस्सा पाट सकता है। नतीजा इस बात का मज़बूत सबूत है कि Qwen3 की सेटिंग में distillation सस्ता और बेहतर था, हर सेटिंग के बारे में सबूत नहीं।

यह भी नोट करें कि तुलना क्या छोड़ देती है। Teachers ख़ुद चार-चरण pipeline से निकले थे, जिसमें RL शामिल है। बचत असली है, पर वह मानती है कि teacher की क़ीमत कोई पहले ही चुका चुका है।

## अभ्यास

1. ▢ Table 21 से, off-policy checkpoint के ऊपर LiveCodeBench v5 पर RL और on-policy distillation ने हर एक ने कितने अंक जोड़े, और हर एक ने प्रति अंक कितने GPU hours इस्तेमाल किए?

<details markdown="1"><summary>जाँचें</summary>

RL 42.0 से 52.9 पर गया, यानी +10.9 अंक, और 17,920 भाग 10.9 लगभग 1,640 GPU hours प्रति अंक है। On-policy distillation 60.3 तक गया, यानी +18.3 अंक, और 1,800 भाग 18.3 लगभग 98 GPU hours प्रति अंक है। इस benchmark पर अनुपात लगभग 17 से 1 है, मुख्य 10 से 1 से बड़ा, क्योंकि distillation ने ज़्यादा अंक भी पाए। दोनों संख्याएँ एक student आकार और queries के एक सेट के लिए हैं।

</details>

2. ▢ कौन-सी लागत on-policy distillation step में मौजूद है और संग्रहीत teacher text पर off-policy step में नहीं?

    - a) Student model के आर-पार backpropagate करना
    - b) हर token position पर loss निकालना
    - c) Teacher को student के output पर चलाना
    - d) Training शुरू होने से पहले prompts को tokenize करना

<details markdown="1"><summary>जाँचें</summary>

**c)** Teacher को वे sequences score करने होते हैं जो student के generate करने से पहले मौजूद ही नहीं थे। (b), (a) और (d) off-policy steps में भी होते हैं।

</details>

3. ▢ RL और on-policy distillation, दोनों के बाद pass@1 सुधरा। AIME पर pass@64 ने हर एक के लिए क्या दिखाया, और report क्या निष्कर्ष निकालती है?

<details markdown="1"><summary>संकेत</summary>

RL पंक्ति के लिए AIME columns में कोष्ठक वाली संख्याएँ देखें।

</details>

<details markdown="1"><summary>जाँचें</summary>

RL के लिए pass@64 AIME'24 पर 90.0 और AIME'25 पर 83.3 बना रहा, शुरुआती checkpoint से अपरिवर्तित। On-policy distillation के बाद वह 93.3 और 86.7 तक बढ़ा। Report निष्कर्ष निकालती है कि teacher logits से distil करना student की exploration space बढ़ाता है जबकि RL ने नहीं बढ़ाई। यह एक तुलना की लेखकों की व्याख्या है।

</details>

4. ▢ आपके पास 8B student है, उसी tokenizer वाला ज़्यादा मज़बूत teacher है, जाँचे जा सकने वाले उत्तर वाला math task है, और सीमित GPU बजट है। क्या Qwen3 तालिका तय कर देती है कि RL इस्तेमाल करें या on-policy distillation?

<details markdown="1"><summary>जाँचें</summary>

वह distillation की ओर इशारा करती है और मामला तय नहीं करती। वह इसका समर्थन करती है कि जब मज़बूत teacher पहले से उपलब्ध हो और student को पहले off-policy distillation से गरमाया गया हो, तो Qwen3 के runs में on-policy distillation सस्ता और बेहतर था। वह आपके task, आपके teacher, या इसे कवर नहीं करती कि GPU-hour आँकड़ों में teacher शामिल है या नहीं। अगर कोई मज़बूत teacher मौजूद नहीं, तो distillation उपलब्ध ही नहीं है और RL रास्ता है, जैसे Qwen3 के teachers बने।

</details>

5. ▢ Qwen3 off-policy चरण को on-policy से पहले क्यों चलाता है, और GKD में क्या उस क्रम का समर्थन करता है?

<details markdown="1"><summary>जाँचें</summary>

Off-policy चरण student को बुनियादी reasoning क्षमता और mode बदलना देता है, जो report के अनुसार on-policy training की नींव रखता है। GKD यही मान्यता रखता है: उसे ऐसा student चाहिए जो पहले से इतनी गुणवत्ता के sequences generate कर सके कि teacher की प्रतिक्रिया का कुछ मतलब हो, और उसके students supervised fine-tuned checkpoints के रूप में शुरू हुए।

</details>

## असली दुनिया का अभ्यास

- [ ] Qwen3 report का section 4.7 खोलें और Table 21 ढूँढें। तीनों GPU-hour और AIME'24 cells एक नोट में उतारें और उनसे हर विधि के लिए अंक-प्रति-घंटा निकालें।
- [ ] अपने योजनाबद्ध run की प्रति-step लागत तीन पंक्तियों में लिखें: कौन generate करता है, कौन score करता है, कौन update करता है। फिर चिह्नित करें कि कौन-सा model इतना बड़ा है कि उसे अपना GPU चाहिए।
- [ ] कल: बिना नोट्स के Qwen3 के दोनों चरण लिखें, हर एक किस पर train करता है, और 1/10 वाले आँकड़े को सामान्य न बनाने के दो कारण।

## आगे बढ़ने के लिए

- [On-Policy Distillation शीट](../reference/on-policy-distillation.md)
- [पेपर: "Qwen3 Technical Report", Qwen Team, 2025](https://arxiv.org/abs/2505.09388)
- [Post-training ट्रैक](../../post-training/)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
