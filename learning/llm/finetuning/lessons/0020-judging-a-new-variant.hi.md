---
title: "20. नए PEFT Variant को परखना"
description: "छह triage सवाल, और हराने लायक baseline"
type: lesson
---

# पाठ 20. नए PEFT Variant को परखना

**मिशन से संबंध:** "नया PEFT पेपर पढ़ें और परखें कि उसकी बताई जीत आपके अपने task पर टिकेगी या नहीं" सफलता-सूची की आख़िरी बात है। यह पाठ वही कौशल है।
**मुख्य स्रोत:** [दस्तावेज़: LoRA variants, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
**पूर्व-आवश्यकताएँ:** [पाठ 19](0019-when-dora-wins.md), [पाठ 17](0017-what-qlora-costs.md)

## वार्म-अप

1. ▢ किस शर्त पर ज़्यादा rank के बजाय DoRA सही चुनाव है?

<details markdown="1"><summary>जाँचें</summary>

जब rank किसी ऐसी चीज़ से नीचे बँधा हो जिसे आप हटा नहीं सकते, आम तौर पर छोटे dataset पर overfitting का जोखिम।

</details>

2. ▢ दो runs के तुलनीय होने के लिए क्या बराबर होना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

परखे जा रहे अकेले चर के सिवा सब कुछ: data, split, seed, rank, alpha, learning rate, schedule, steps।

</details>

3. ▢ Quantisation की कौन-सी दो गुणवत्ता-क़ीमतें हैं, और उन्हें कैसे अलग किया जाता है?

<details markdown="1"><summary>जाँचें</summary>

Training से पहले base की गिरावट, और बिगड़े base पर बदतर adapter training। पहली को अलग करने के लिए बिना adapter के quantized और unquantized bases का evaluation करें।

</details>

## यह जानें

नए parameter-efficient fine-tuning तरीक़े लगातार आते रहते हैं। ज़्यादातर आपके काम के नहीं होते। कौशल triage है, उत्साह नहीं।

### परिदृश्य, इस आधार पर कि वे क्या बदलते हैं

तरीक़े रटने के बजाय अक्ष सीखें। लगभग हर variant चार चीज़ों में से एक को बदलता है।

**Scaling।** rsLoRA ([arXiv:2312.03732](https://arxiv.org/abs/2312.03732)) `α/r` भाजक की जगह `α/√r` रखता है, यह तर्क देते हुए कि `α/r` ऊँचे rank पर ज़्यादा दबाता है। सस्ता, एक flag, ऊँचे rank पर काम करते समय मायने रखता है।

**Learning rates।** LoRA+ ([arXiv:2402.12354](https://arxiv.org/abs/2402.12354)) `B` के लिए `A` से ऊँचा learning rate इस्तेमाल करता है, यह तर्क देते हुए कि दोनों गुणनखंडों को उनकी अलग भूमिकाओं और scales को देखते हुए एक rate साझा नहीं करना चाहिए। सस्ता, और पाठ 9 की किसी भी चीज़ से सचमुच अलग knob।

**Initialisation।** Random `A` और शून्य `B` की जगह:

- **PiSSA** ([arXiv:2404.02948](https://arxiv.org/abs/2404.02948)) `W₀` के मुख्य singular घटकों से initialise करता है, ताकि adapter weight की प्रमुख दिशाओं से मेल खाते हुए शुरू हो।
- **OLoRA** `W₀` के QR decomposition से initialise करता है।
- **LoftQ** ([arXiv:2310.08659](https://arxiv.org/abs/2310.08659)) adapter को quantisation की त्रुटि की भरपाई के लिए initialise करता है, ख़ास तौर पर QLoRA वाली setting के लिए।

ध्यान दें कि ये सब पाठ 9 का zero-initialisation वाला गुण छोड़ देते हैं: model अब base के बिल्कुल बराबर शुरू नहीं होता। यह जान-बूझकर किया गया सौदा है, और यही वह चीज़ है जिसकी बारीकी से जाँच करनी चाहिए।

**संरचना:**

- **AdaLoRA** ([arXiv:2303.10512](https://arxiv.org/abs/2303.10512)) हर जगह एक rank इस्तेमाल करने के बजाय layers के बीच rank को अनुकूली ढंग से बाँटता है, इस आधार पर कि layers को कितने adaptation की ज़रूरत है, इसमें वे अलग हैं।
- **VeRA** ([arXiv:2310.11454](https://arxiv.org/abs/2310.11454)) layers के बीच frozen random `A` और `B` साझा करता है और सिर्फ़ छोटे scaling vectors train करता है, adapter का आकार भारी मात्रा में घटाते हुए।
- **DoRA** magnitude को direction से अलग करता है, जैसा पाठ 18 में।

PEFT में इनमें से ज़्यादातर अलग code path के बजाय config का flag या `init_lora_weights` का मान हैं, जो उन्हें आज़माना सस्ता बनाता है और config सतह पढ़ना यह देखने का तेज़ तरीक़ा कि library किसे स्थापित मानती है।

### Triage के सवाल

जब कोई नया तरीक़ा आए, इन्हें क्रम से पूछें। आप आम तौर पर जल्दी रुक सकते हैं।

**1. यह क्या बदलता है, चार अक्षों में से किस पर?** अगर आप इसका जवाब abstract और एक figure से नहीं दे सकते, तो पेपर या तो ख़राब लिखा है या आप अभी उसके पाठक नहीं हैं। यह अकेला सवाल ज़्यादातर चीज़ों को छान देता है।

**2. Baseline क्या है?** नतीजे को फुलाने का सबसे आम तरीक़ा कमज़ोर baseline है। इन पर नज़र रखें: लेखकों के चुने rank पर LoRA, जब all-linear आधुनिक default है तब attention-only targets, नए तरीक़े के लिए tune किया हुआ learning rate पर baseline के लिए विरासत में लिया हुआ। **जो तरीक़ा बिना-tune किए LoRA को हराता है, उसने LoRA को हराना साबित नहीं किया है।**

**3. क्या फ़ायदा noise से बड़ा है?** Seed का variance या confidence intervals ढूँढें। अगर पेपर बिना फैलाव के अकेली संख्याएँ बताता है, और फ़ायदा एक-दो अंक है, तो नतीजा अभी noise से अलग नहीं पहचाना जा सकता। यह बेहद आम है।

**4. इसकी क़ीमत क्या है?** Step का समय, implementation की जटिलता, क्या वह साफ़ merge होता है, क्या वह quantisation के साथ जुड़ता है, क्या ऐसी implementation है जिस पर आप भरोसा करते हैं। 30% धीमेपन के बदले 1% का फ़ायदा ज़्यादातर settings में बुरा सौदा है।

**5. क्या उसका तंत्र आपकी व्यवस्था पर लागू होता है?** DoRA का फ़ायदा कम rank पर रहता है। LoftQ का quantized training में। rsLoRA का ऊँचे rank पर। जिस तरीक़े का तंत्र ऐसी बाधा को संबोधित करता है जो आपके पास नहीं है, वह आपकी मदद नहीं करेगा, और यह कुछ भी चलाने से *पहले* ही अनुमान लगाने लायक है।

**6. क्या किसी स्वतंत्र व्यक्ति ने इसे दोहराया है?** Practitioner समुदाय असली tasks पर तरीक़ों को जल्दी परखते हैं और दो-टूक बताते हैं कि क्या दोहराया नहीं जा पाया। यह अक्सर पेपर को दो बार पढ़ने से तेज़ और ज़्यादा जानकारी देने वाला होता है।

### तीन भरोसेमंद चेतावनी-संकेत

- **फ़ायदे सिर्फ़ benchmarks पर बताए गए, कभी ऐसे task पर नहीं जिसका कोई deployment हो।** Benchmarks प्रॉक्सी हैं और उनके विरुद्ध भारी optimise किया जाता है।
- **Attention-only LoRA baseline से तुलना**, ऐसे पेपर में जो all-linear के मानक practice बनने के बाद लिखा गया। या तो अनजान या सुविधाजनक।
- **लागत का कोई हिसाब नहीं।** हर तरीक़े की क़ीमत होती है। जो पेपर अपनी क़ीमत नहीं बताता वह आपसे सीधा नहीं है, और छूट आम तौर पर दिलचस्प हिस्सा होती है।

### Default स्थिति

**पर्याप्त rank पर सभी linear layers पर LoRA, tune किए हुए learning rate के साथ, एक मज़बूत baseline है जिसे ज़्यादा अंतर से हराना कठिन है।** यह "LoRA without regret" की धारा के काम का व्यावहारिक निचोड़ है, और यही आपका शुरुआती बिंदु और आपकी तुलना होनी चाहिए।

नए variant को *उसे* हराना होगा, आपके task पर, आपके seed noise से ज़्यादा अंतर से, उस क़ीमत से कम में जो rank बढ़ाने में लगती। ज़्यादातर यह कसौटी पार नहीं करते। यह जानना निंदकता नहीं है। यही आपको अपना ध्यान उन थोड़ों पर ख़र्च करने देता है जो पार करते हैं।

## अभ्यास

1. ▢ उन चार अक्षों के नाम बताएँ जिन्हें PEFT variant बदल सकता है, हर एक का एक उदाहरण देकर।

<details markdown="1"><summary>जाँचें</summary>

Scaling (rsLoRA), learning rates (LoRA+), initialisation (PiSSA, OLoRA, LoftQ), संरचना (AdaLoRA, VeRA, DoRA)।

अक्ष जानने का मतलब है कि नया तरीक़ा देखते ही वर्गीकृत हो जाता है, शून्य से सीखने की ज़रूरत नहीं पड़ती।

</details>

2. ▢ एक पेपर बताता है कि उसका तरीक़ा LoRA को 2.1 अंक से हराता है, जिसमें LoRA rank 8 पर सिर्फ़ attention modules पर है। आपकी चिंता क्या है?

<details markdown="1"><summary>जाँचें</summary>

Baseline मौजूदा मानकों से कमज़ोर है। ऊँचे rank पर all-linear targets आधुनिक default है और attention-only rank 8 से काफ़ी मज़बूत है।

तरीक़ा उस कमज़ोर baseline को हरा सकता है और फिर भी ठीक से configure किए गए LoRA से हार सकता है। जैसे प्रकाशित हुई, तुलना आपको यह नहीं बताती।

</details>

3. ▢ पेपर की कौन-सी बात बताए गए 1.5-अंक के फ़ायदे को सबसे ज़्यादा कमज़ोर करती है?

    - a) किसी seed variance या intervals का बिल्कुल न होना
    - b) उस model से छोटा model इस्तेमाल करना जो आप इस्तेमाल करना चाहते हैं
    - c) कोई reference implementation जारी न होना
    - d) सिर्फ़ तीन अलग downstream tasks पर evaluation

<details markdown="1"><summary>जाँचें</summary>

**a)** किसी seed variance या intervals का बिल्कुल न होना।

फैलाव के बिना, 1.5-अंक के फ़ायदे को run-से-run noise से अलग नहीं पहचाना जा सकता, जो अक्सर उसी आकार का होता है। बाक़ी असली सीमाएँ हैं पर केंद्रीय दावे को उस तरह नहीं काटतीं जैसे ग़ायब variance।

</details>

4. ▢ LoftQ adapter को quantisation की त्रुटि की भरपाई के लिए initialise करता है। किस व्यवस्था में आप अनुमान लगाएँगे कि वह मदद करता है, और कहाँ कुछ नहीं?

<details markdown="1"><summary>जाँचें</summary>

Quantized base के सामने training में उसे मदद करनी चाहिए, आक्रामक quantisation पर और छोटे models पर सबसे साफ़, जहाँ quantisation की त्रुटि अनुपात में ज़्यादा नुक़सान करती है।

बिना quantize किए bf16 base के लिए उसे कुछ नहीं करना चाहिए, क्योंकि भरपाई करने को कोई quantisation त्रुटि है ही नहीं, इसलिए तंत्र को पकड़ने की जगह नहीं मिलती।

</details>

5. ▢ PiSSA zero initialisation छोड़ देता है। यह क्यों मायने रखता है, और आप क्या जाँचेंगे?

<details markdown="1"><summary>जाँचें</summary>

Zero initialisation गारंटी देता है कि adapt किया गया model base के बिल्कुल बराबर शुरू होता है, इसलिए training ज्ञात-अच्छे weights से शुरू होती है और कोई भी गिरावट training के नाम जाती है।

उसे छोड़ने का मतलब है कि model परेशान की हुई अवस्था से शुरू होता है। शुरुआती अस्थिरता जाँचें, और जाँचें कि क्या उस विचलन ने आपके task के बाहर की क्षमताओं को नुक़सान पहुँचाया। Training से पहले, step शून्य पर चलाया गया regression suite (पाठ 24) सीधा परीक्षण है।

</details>

6. ▢ वह baseline क्या है जिसे हर नए variant को हराना होगा, और वह कठिन क्यों है?

<details markdown="1"><summary>जाँचें</summary>

पर्याप्त rank पर सभी linear layers में LoRA, tune किए हुए learning rate के साथ।

वह कठिन इसलिए है कि उसके पास पहले से इतनी capacity और coverage है कि कई supervised tasks पर वह full fine-tuning के क़रीब पहुँच जाता है। जब baseline छत के पास हो, तो तंत्र के किसी सुधार के दावा करने को बहुत कम गुंजाइश बचती है।

</details>

## असली दुनिया का अभ्यास

- [ ] इस पाठ का कोई ऐसा variant चुनें जो आपने इस्तेमाल नहीं किया। उसके पेपर पर छह triage सवाल चलाएँ और अपने task के लिए एक अनुच्छेद का फ़ैसला लिखें।
- [ ] अपने installed PEFT version में `init_lora_weights` के विकल्प पढ़ें। हर एक को एक तरीक़े और एक अक्ष से जोड़ें।
- [ ] किसी practitioner समुदाय में उस तरीक़े पर स्वतंत्र रिपोर्टें खोजें। उन्होंने जो पाया उसकी तुलना पेपर के दावे से करें।
- [ ] कल: अपना चुना variant ठीक से tune किए all-linear LoRA baseline के मुक़ाबले चलाएँ, हर एक के तीन seeds। दर्ज करें कि फ़ायदा टिकता है या नहीं।

## आगे बढ़ने के लिए

- [दस्तावेज़: LoRA variants, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [दस्तावेज़: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
- [EleutherAI Blog](https://blog.eleuther.ai/): ऐसा समूह जो अपने नकारात्मक नतीजे भी प्रकाशित करता है, जो इस सवाल का दुर्लभ आधा हिस्सा है
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/): तेज़, दो-टूक दोहराने की रिपोर्टें

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
