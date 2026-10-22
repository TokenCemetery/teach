---
title: "21. Data की मात्रा और Teacher की लागत"
description: "बजट में teacher के inference को गिनना, और तय करना कि distillation data कितना काफ़ी है"
type: lesson
---

# पाठ 21. Data की मात्रा और Teacher की लागत

**मिशन से संबंध:** मिशन आपसे माँगता है कि आप teacher की अपनी लागत को बजट में गिनकर data की मात्रा चुनें, जिसके लिए एक ऐसा सूत्र चाहिए जिसे आप लिफ़ाफ़े के पीछे चला सकें और इसकी साफ़ समझ कि आप कौन-सी लागतें चुका रहे हैं और कौन-सी नहीं।
**मुख्य स्रोत:** [पेपर: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606), section 5 और Equation 9
**पूर्व-आवश्यकताएँ:** [पाठ 20](0020-choosing-student-size.md), [Teacher](../GLOSSARY.md), [Sequence-level distillation](../GLOSSARY.md), [Synthetic data](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 20 ने दो शर्तें गिनाईं जिनके तहत distillation, supervised learning से ज़्यादा कुशल है। दोनों बताएँ।

<details markdown="1"><summary>जाँचें</summary>

Student का कुल compute या tokens एक student-आकार-निर्भर threshold से ज़्यादा नहीं होने चाहिए, और कोई teacher पहले से मौजूद हो या उसके एक distillation से परे उपयोग हों। दोनों में से कोई भी टूटे तो पेपर का नतीजा student को सीधे train करने के पक्ष में है।

</details>

2. ▢ पाठ 8 ने student को teacher के decode किए outputs पर train किया, और पाठ 9 ने उसकी तुलना distributions मिलाने से की। दोनों में से किसे teacher के logits चाहिए, और किसे सिर्फ़ उसका text?

<details markdown="1"><summary>जाँचें</summary>

[Token-level](../GLOSSARY.md) (logit) distillation को teacher का प्रति-position distribution चाहिए। [Sequence-level distillation](../GLOSSARY.md) को सिर्फ़ वह text चाहिए जो teacher ने decode किया, इसीलिए वह ऐसी API के ज़रिए भी चलता है जो और कुछ नहीं लौटाती। दोनों teacher की लागत को अलग जगह रखते हैं, जिसकी क़ीमत यह पाठ आँकता है।

</details>

3. ▢ पाठ 12 ने कहा कि मात्रा ख़राब examples को ठीक नहीं करती। अगर आप किसी generated सेट को बिना filter किए दोगुना कर दें, तो उसमें ख़राब examples के हिस्से का क्या होने की उम्मीद करेंगे?

<details markdown="1"><summary>जाँचें</summary>

वह लगभग वैसा ही रहेगा। तय दोष-दर वाले सेट को दोगुना करना अच्छे examples के साथ दोषों को भी दोगुना कर देता है। ज़्यादा data तभी मदद करता है जब पाठ 12 की filtering ने गुणवत्ता तय कर दी हो, इसीलिए यह पाठ उन tokens को गिनता है जो filter से बचे।

</details>

## यह जानें

### दो लागतें, दो सूत्र

Dense transformer की training लागत आम तौर पर 6 FLOPs प्रति parameter प्रति token के रूप में अनुमानित होती है: लगभग 2 forward pass के लिए और 4 backward pass के लिए। अकेला forward pass लगभग 2 प्रति parameter प्रति token है। ये सन्निकटन हैं। वे attention term को नज़रअंदाज़ करते हैं, जो context की लंबाई के साथ बढ़ता है, और सारे parameters को बराबर गिनते हैं।

पेपर भी यही कहता है। वह supervised लागत को लगभग 6ND लिखता है, 2N forward सन्निकटन को सामान्य संक्षिप्त रूप के तौर पर इस्तेमाल करता है, और फिर अपने नतीजों के लिए उसे इस्तेमाल करने से मना कर देता है, दो कारणों से: non-embedding parameters इस्तेमाल करना उसे पक्षपाती करता है, और लंबे context वाले छोटे models के लिए attention का योगदान उल्लेखनीय है (section 5, Equation 9 के नीचे)। इसके बजाय वह सुधारी हुई प्रति-token लागत निकालता है। परिमाण-क्रम की योजना के लिए संक्षिप्त रूप ठीक है। ऐसी संख्या के लिए जिसका आप बचाव करेंगे, उसे सन्निकटन बताएँ और कहें कि आपने क्या छोड़ा।

उसकी distillation लागत (Equation 9) student की training जमा teacher के forward passes है, जहाँ हर एक पर शुल्क तभी लगता है जब वह आप पर लागू हो। संक्षिप्त रूप में:

```text
student training   ≈ 6 × N_student × D
teacher inference  ≈ 2 × N_teacher × D     (forward only, over the same D tokens)
```

यहाँ N parameters है और D वह tokens की संख्या है जिन पर student train होता है। Teacher term वही D इस्तेमाल करता है क्योंकि logit distillation, student जो भी token देखता है उस पर teacher को चलाता है। एक को दूसरे से भाग देने पर याद रखने लायक़ अनुपात मिलता है:

```text
teacher cost / student cost  ≈  N_teacher / (3 × N_student)
```

Student से तीन गुना बड़े teacher को चलाना लगभग उतना ही महँगा है जितना student को train करना। कोई भी इससे बड़ा teacher उस student से ज़्यादा महँगा है जिसे आप बना रहे हैं।

### हल किया हुआ उदाहरण: teacher से tokens score करना

एक 1B student 100B tokens पर train होता है, उन्हीं tokens को score करते teacher के logits के साथ।

| राशि | गणना | FLOPs |
|---|---|---|
| Student training | 6 × 1e9 × 1e11 | 6.0e20 |
| 7B teacher scoring | 2 × 7e9 × 1e11 | 1.4e21 |
| 70B teacher scoring | 2 × 70e9 × 1e11 | 1.4e22 |

7B teacher की लागत student की अपनी training से लगभग 2.3 गुना है, और 70B teacher की लगभग 23 गुना। उसी tokens पर उसी student का supervised baseline अकेले 6.0e20 लेता है। 70B वाला run वही student है जो लगभग 24 गुना compute पर train हुआ, इसलिए उसके सार्थक होने के लिए student का loss बराबर compute पर supervised student के loss से बहुत कम होना चाहिए, और पाठ 20 की threshold बताती है कि ऐसा कितनी बार होता है।

### teacher की लागत को students में बाँटना

अगर teacher किसी dataset को एक बार score करे और उसके logits सहेजे जाएँ, तो कई students उसी pass से train हो सकते हैं। उन 100B tokens पर चार 1B students और 7B teacher के साथ: एक student की लागत 1.4e21 + 6.0e20 = 2.0e21 है, और चार की 1.4e21 + 4 × 6.0e20 = 3.8e21, यानी हर एक के लिए 9.5e20। यह पेपर की तीसरी setting है, जिसमें teacher की लागत उन students में बँटती है जिन्हें वह सेवा देता है (उसकी Table 2)। यह छोड़ देता है कि logits सहेजने में क्या लागत है, एक बिल जिसे पाठ 7 ने पेश किया और पेपर अलग से देखता है।

### हल किया हुआ उदाहरण: logits की जगह generated text

Sequence-level distillation के लिए teacher पर शुल्क generate करने का लगता है, score करने का नहीं। G tokens generate करने की लागत forward-pass सन्निकटन से FLOPs में लगभग 2 × N_teacher × G है, और फिर student हर epoch के लिए उन्हीं G tokens पर train होता है। यह पेपर के हिसाब का विस्तार है और उससे नहीं है, क्योंकि पेपर logits का अध्ययन करता है।

70B teacher 1B tokens generate करता है: 2 × 70e9 × 1e9 = 1.4e20। 3B student उन पर दो epochs train करता है: 6 × 3e9 × 1e9 × 2 = 3.6e19। Teacher की generation, student की training से लगभग 3.9 गुना है, और generated सेट दोबारा इस्तेमाल हो सकता है, इसलिए दूसरा student teacher को कुछ नहीं देता।

FLOPs को लागत की तरह पढ़ने पर एक सावधानी। एक बार में एक token generate करना GPU को पूरे इस्तेमाल से बहुत दूर रखता है, इसलिए generation का wall-clock और पैसा उससे कहीं ऊपर चलता है जो FLOPs सुझाते हैं। यह decoding के बारे में सामान्य ज्ञान है, यहाँ के किसी स्रोत का नतीजा नहीं, इसलिए बजट बताने से पहले अपने hardware पर प्रति सेकंड tokens मापें।

### पेपर पैसे के जाने की जगह के बारे में क्या कहता है

जब teacher की pretraining बिल का हिस्सा हो, तो पेपर की Table 3 सार देती है कि सबसे अच्छा बँटवारा पैमाने के साथ कैसे चलता है:

| Student का आकार | Compute | इष्टतम आवंटन |
|---|---|---|
| छोटा (लगभग 3B तक) | छोटा (लगभग 1e21 FLOPs तक) | ज़्यादातर teacher pretraining |
| छोटा (लगभग 3B तक) | बड़ा (लगभग 1e25 FLOPs और ऊपर) | Student training और teacher inference के बीच बराबर, teacher pretraining पर बहुत कम |
| बड़ा (लगभग 10B और ऊपर) | छोटा | ज़्यादातर मानक student training |
| बड़ा (लगभग 10B और ऊपर) | बड़ा | Student training, teacher inference और teacher pretraining के बीच बराबर |

इन्हें पेपर के नियम का इष्टतम मानकर पढ़ें, उस परिदृश्य में जहाँ teacher pretraining गिनी जाती है। ये ऐसे open teacher के लिए नुस्ख़ा नहीं हैं जो आपके पास पहले से है, जहाँ pretraining वाला column शून्य है।

### कितना data काफ़ी है

पेपर का ईमानदार जवाब यह है कि और tokens मुफ़्त नहीं हैं और असीमित नहीं हैं। Teacher के तय होने पर, token बजट बढ़ने के साथ supervised learning पर distillation का फ़ायदा घटता है, और आख़िरकार supervised learning उसकी बराबरी कर लेती है या उसे पार कर जाती है (section 5.1)। इसलिए "काफ़ी" वह बिंदु है जहाँ एक अतिरिक्त token student के अपने signal पर बेहतर ख़र्च होता है, और वह बिंदु student के आकार के साथ ऊपर जाता है।

Minitron एक उपयोगी विरोधाभास है। Muralidharan et al. की Table 2 में, Minitron 8B को 94B tokens पर train किया गया, जबकि Nemotron-3 8B को 3.8T पर, लगभग 40 गुना कम। तुलना में दो सावधानियाँ हैं। Minitron का student pruning के बाद teacher के weights से शुरू होता है, जहाँ पेपर के students शून्य से शुरू होते हैं। और 40 गुना का आँकड़ा pruned-और-distilled model की तुलना शून्य से train हुए model से करता है, उसी student के supervised run से नहीं। इसलिए यह दिखाता है कि अच्छी initialisation को कितना कम data चाहिए हो सकता है। यह नहीं दिखाता कि शून्य से शुरू होने वाले student को कितना data चाहिए।

उनकी परिवार-स्तर की बचत भी एक हिसाब का चुनाव है। वे 15B, 8B और 4B परिवार के लिए 1.8 गुना कम compute बताते हैं (section 4.1), जिसकी गणना (4.4e17 + 2.5e17 / 40 + 1.2e17 / 40) के रूप में 4.4e17 + 2.5e17 + 1.2e17 के विरुद्ध की गई है, FLOPs प्रति training step में। जैसा लिखा है, योग हर model के अपने training steps गिनता है। गणना का वर्णन करने वाले वाक्य छोटे models की retraining के दौरान 15B teacher चलाने का कोई term नहीं जोड़ते। यही वह term है जिसे यह पाठ गिनने को कहता है।

## अभ्यास

1. ▢ गणना करें: एक 1B student 8B teacher के संग्रहीत-logit pass के साथ 50B tokens पर train होता है। Student के training FLOPs, teacher के scoring FLOPs, और दूसरे का पहले से अनुपात बताएँ।

<details markdown="1"><summary>संकेत</summary>

Student के लिए 6 × N × D और teacher के लिए 2 × N × D इस्तेमाल करें, दोनों में एक ही D के साथ। अनुपात N_teacher भाग तीन गुना N_student के भी बराबर है।

</details>

<details markdown="1"><summary>जाँचें</summary>

Student: 6 × 1e9 × 5e10 = 3.0e20। Teacher: 2 × 8e9 × 5e10 = 8.0e20। अनुपात: लगभग 2.7, जो 8 / (3 × 1) = 2.67 से मेल खाता है। दोनों 6N और 2N सन्निकटनों से परिमाण-क्रम की संख्याएँ हैं। वे attention और logits को सहेजने या ले जाने की लागत छोड़ देती हैं।

</details>

2. ▢ एक 70B teacher उत्तरों के 1B tokens generate करता है, और एक 3B student उन पर दो epochs train होता है। दोनों में से किसमें ज़्यादा FLOPs लगते हैं, और कितने गुना?

<details markdown="1"><summary>संकेत</summary>

Generation 2 × N_teacher पर प्रति token एक forward pass है। Training प्रति token प्रति epoch 6 × N_student है।

</details>

<details markdown="1"><summary>जाँचें</summary>

Generation: 2 × 70e9 × 1e9 = 1.4e20। Training: 6 × 3e9 × 1e9 × 2 = 3.6e19। Teacher की generation की लागत student की training से लगभग 3.9 गुना है। Epochs जोड़ना सिर्फ़ student वाला पक्ष बढ़ाता है, इसलिए तीसरा epoch दोनों को लगभग बराबर कर देता है। Generated text दूसरे student के लिए बिना अतिरिक्त teacher लागत के दोबारा भी इस्तेमाल हो सकता है।

</details>

3. ▢ चार 1B students 100B tokens पर एक 7B-teacher scoring pass साझा करते हैं। प्रति student औसत FLOPs क्या हैं, और वे अकेले student से कम क्यों हैं?

<details markdown="1"><summary>जाँचें</summary>

कुल: 1.4e21 + 4 × 6.0e20 = 3.8e21, यानी प्रति student 9.5e20, अकेले student के 2.0e21 के मुक़ाबले। Teacher का pass एक बार चुकाया जाता है और चार में बँटता है। यह logits रखने की storage और bandwidth लागत को अनदेखा करता है, जो हर token पर पूरी-vocabulary distribution के लिए बड़ी हो सकती है।

</details>

4. ▢ Minitron के 94B-token आँकड़े के बारे में कौन-सा कथन सही है?

    - a) यह दिखाता है कि शून्य से शुरू होने वाले student को 15B teacher से distil होने पर लगभग 94B tokens चाहिए।
    - b) यह दिखाता है कि pruned student शून्य से training की तुलना में कहीं कम tokens से उबर सकता है।
    - c) यह दिखाता है कि distillation को उस student की supervised training से लगभग चालीस गुना कम data चाहिए।
    - d) यह दिखाता है कि 15B teacher की inference लागत student की training के मुक़ाबले नगण्य थी।

<details markdown="1"><summary>जाँचें</summary>

b). 8B student को 15B model से prune किया गया था, इसलिए वह teacher के weights से शुरू हुआ। a) और c) pruned initialisation को ऐसे लेते हैं मानो वह शून्य से शुरू होने वाला distillation हो। 40 गुना का आँकड़ा Nemotron-3 8B से तुलना करता है, जो शून्य से train हुआ अलग model है। d) दिखाया नहीं गया: परिवार की लागत की गणना जैसी लिखी है उसमें teacher forward-pass का term नहीं है, इसलिए वह उस लागत के बारे में किसी भी तरफ़ कुछ नहीं कहती।

</details>

5. ▢ चरण 4 का interleave: आप API-hosted teacher से 20B tokens का instruction data generate करने और 3B student को distil करने की योजना बनाते हैं। दो चीज़ें बताएँ जो FLOPs सूत्र आपको प्रतिबद्ध होने से पहले नहीं बताता, एक लागत के बारे में और एक पाठ 13 से।

<details markdown="1"><summary>जाँचें</summary>

लागत के लिए, generation FLOPs-bound से बहुत दूर है, इसलिए असली आँकड़ा API की क़ीमत या आपके hardware पर wall-clock घंटे है, और कच्चे 20B की जगह filter के बाद की पैदावार तय करती है कि आप कितने tokens पर train करेंगे। पाठ 13 से, कि provider के terms किसी model को उसके outputs पर train करने की अनुमति देते हैं या नहीं, जिसका जवाब कोई compute अनुमान नहीं देता।

</details>

## असली दुनिया का अभ्यास

- [ ] एक teacher और student चुनें जिन्हें आप यथार्थ में इस्तेमाल कर सकें। दोनों के parameter counts और एक token बजट लिखें, फिर student का 6ND, teacher का 2ND और उनका अनुपात निकालें।
- [ ] पेपर की Table 2 और Equation 9 खोलें और चिह्नित करें कि दोनों teacher terms में से कौन-सा आपके project पर लागू होता है, और आप तालिका की किस पंक्ति में हैं।
- [ ] कल: बिना नोट्स के दोनों सूत्रों से अनुपात N_teacher / (3 × N_student) निकालें, फिर वे दो लागतें बताएँ जिन्हें वह छोड़ देता है।

## आगे बढ़ने के लिए

- [आकार तय करना और मापना शीट](../reference/sizing-and-measuring.md)
- [पेपर: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606), Equation 9 और Tables 2 और 3
- [पेपर: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679), Table 2 और section 4.1
- [Pretraining ट्रैक](../../pretraining/): वह track कि training compute बजट कैसे गिना जाता है और token बजट क्या ख़रीदता है
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
