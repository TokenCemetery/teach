---
title: "21. Dataset बनाना"
description: "इस workspace में data हर hyperparameter को हराता है"
type: lesson
---

# पाठ 21. Dataset बनाना

**मिशन से संबंध:** Data की गुणवत्ता इस workspace के हर hyperparameter पर हावी है। चरण 3 ने आपको knob घुमाना सिखाया; यह चरण सिखाता है कि नतीजे को असल में क्या हिलाता है।
**मुख्य स्रोत:** [पेपर: "LIMA: Less Is More for Alignment", Zhou et al., arXiv:2305.11206](https://arxiv.org/abs/2305.11206)
**पूर्व-आवश्यकताएँ:** [पाठ 3](0003-tokenizers-and-chat-templates.md), [पाठ 12](0012-reading-a-training-run.md)

## वार्म-अप

1. ▢ Training job से पहले चलाने की सबसे क़ीमती जाँच कौन-सी है?

<details markdown="1"><summary>जाँचें</summary>

एक असली training example decode करके पढ़ें, scored बनाम masked positions गिनते हुए। यह template mismatch, गुम end-of-turn tokens, masking के bugs और truncation एक साथ पकड़ लेती है।

</details>

2. ▢ Epoch की सीमाओं पर गिरावट वाले सीढ़ीदार loss curve का क्या मतलब है?

<details markdown="1"><summary>जाँचें</summary>

Memorisation: model उन examples को पहचान रहा है जो वह पहले देख चुका है।

</details>

3. ▢ Instruction tuning को सामान्यतः कौन-सा loss variant इस्तेमाल करना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

Completion-only। Prompt positions `-100` पर mask किए जाते हैं ताकि सिर्फ़ assistant का response score हो।

</details>

## यह जानें

### असहज अनुपात

अगर आपके पास सीमित समय है, तो उसे data पर लगाएँ। औसत और अच्छे dataset के बीच का फ़ासला rank 8 और rank 128 के बीच के फ़ासले से बड़ा है, LoRA बनाम DoRA से बड़ा है, और ज़्यादातर उन चीज़ों से बड़ा है जिन्हें आप tune कर सकते हैं। Hyperparameters को समझना और बदलना संतोषजनक है, इसीलिए वे अपने असर के अनुपात से ज़्यादा ध्यान सोख लेते हैं।

LIMA का नतीजा इसका सबसे तीखा प्रकाशित कथन है: बहुत थोड़े सावधानी से चुने गए examples, लगभग एक हज़ार के क्रम के, ने मज़बूत instruction-following पैदा की, इस मत का समर्थन करते हुए कि supervised fine-tuning ज़्यादातर *format और शैली* सिखाती है जबकि क्षमता pretraining से आती है। सटीक संख्या को setting-विशिष्ट मानें; दिशा को गंभीरता से लें।

### Fine-tuning क्या अच्छा सिखाती है, और क्या बुरा

| अच्छा सिखाती है | बुरा सिखाती है |
|---|---|
| Output का format और संरचना | दुनिया के बारे में नए तथ्य |
| Tone, register, domain की आवाज़ | ऐसी reasoning क्षमता जो पहले से मौजूद न हो |
| किसी schema का एकसार पालन | वह कुछ भी जिसके लिए ताज़ा जानकारी चाहिए |
| संकरा classification और extraction | लंबी-पूँछ वाला ज्ञान जिसका एक ही बार ज़िक्र हुआ हो |
| Tool-call और function का syntax | अंकगणित और सटीक गणना |

दाईं ओर का column ही वजह है कि [पाठ 27](0027-when-not-to-fine-tune.md) है। तथ्य डालने के लिए बनाया गया dataset वह काम कर रहा है जिसमें fine-tuning सबसे कमज़ोर है, और हर तथ्य को टिकने के लिए कई विविध examples चाहिए होंगे, जिस मोड़ पर retrieval सस्ता, ज़्यादा सटीक और update होने योग्य है।

### Examples डिज़ाइन करना

**Deployment के distribution से मेल खाएँ।** आपके training inputs असली inputs जैसे दिखने चाहिए। साफ़, सुगठित, एक-जैसी लंबाई के training prompts ऐसा model बनाते हैं जो production में मिलने वाली गड़बड़ हक़ीक़त पर बिगड़ता है, और उसी साफ़ पूल से निकला आपका held-out split आपको चेताएगा नहीं।

**कठिन मामले जान-बूझकर शामिल करें।** अस्पष्ट inputs, किनारे के मामले, और वे मामले जहाँ सही उत्तर इनकार या "जानकारी अपर्याप्त" है। अगर हर training उत्तर आत्मविश्वास से भरा और पूरा है, तो आपने आत्मविश्वास भरी पूर्णता सिखाई है, उन inputs पर भी जो उसके लायक नहीं।

**Format के बारे में एकसार रहें।** अगर आधे examples पूर्ण विराम पर ख़त्म होते हैं और आधे नहीं, तो model असंगति सीख लेता है। हर मनमाना फ़र्क़ जो आप छोड़ देते हैं, शोर पर ख़र्च की गई capacity है।

**Outputs आदर्श बनाएँ।** Model अपने targets की नक़ल करता है। पर्याप्त उत्तरों का dataset पर्याप्त उत्तर बनाता है, और कोई hyperparameter उससे नहीं उबारता।

**सतह बदलें, सार नहीं।** एक ही अनुरोध के कई शब्द-रूप शब्दांकन के प्रति मज़बूती सिखाते हैं। कई लगभग-एक-जैसे examples रटना सिखाते हैं।

### Deduplication

जोड़कर बनाए गए datasets में लगभग-दोहरे सबसे आम गंभीर दोष हैं, और वे एक साथ दो नुक़सान करते हैं: दोहराई गई सामग्री जो कुछ सिखाती है उसे ज़्यादा वज़न देना, और अगर दोहरे आपके split के दोनों तरफ़ पड़ें तो ऐसा held-out score जो generalisation नहीं बल्कि याद मापता है।

सटीक-मेल वाला deduplication काफ़ी नहीं। Normalised hashing इस्तेमाल करें, फिर लगभग-दोहरों के लिए MinHash या embedding दूरी जैसा similarity माप। इसे split करने से *पहले* करें, बाद में नहीं।

### आकार और संतुलन

मोटा दिशा-निर्देश, नियम नहीं:

| Examples | यथार्थवादी लक्ष्य |
|---|---|
| 50 से 200 | Style, tone, तय output format |
| 500 से 2,000 | संकरे दायरे वाला सुपरिभाषित task |
| 5,000 से 50,000 | व्यापक task, या एक साथ कई क्षमताएँ |
| 1,00,000+ | Adapters के लिए घटते लाभ; विचार करें कि क्या task सचमुच एक task है |

जहाँ श्रेणियाँ हैं, असंतुलन पूर्वाग्रह बन जाता है। 90% एक वर्ग वाला dataset model को उस वर्ग का अनुमान लगाना सिखाता है। या तो उसे संतुलित करें या पाठ 23 के अनुसार अपनी metric में असंतुलन का हिसाब रखें।

### Synthetic data

मज़बूत model से training data generate करना मानक, असरदार है, और इसके दो ख़ास ख़तरे हैं।

**विरासत में मिली त्रुटियाँ।** Generator की ग़लतियाँ और पूर्वाग्रह आपके training targets बन जाते हैं, और वे धाराप्रवाह और एकसार होंगे, जिससे सरसरी नज़र से पकड़ना कठिन होता है। नमूना लें और पढ़ें।

**Distribution का सिकुड़ना।** Generate किया गया data असली data से ज़्यादा एकसार होता है: मिलती-जुलती संरचनाएँ, मिलती-जुलती लंबाइयाँ, मिलता-जुलता register। आप ऐसा model train करते हैं जो एक संकरी फाँक को साफ़ सँभालता है और असली विविधता को ख़राब। जहाँ हो सके असली inputs से generation शुरू करें, और prompts को जान-बूझकर बदलें।

साथ ही: जिस model से आप generate करते हैं उसका licence और शर्तें जाँचें। क्या outputs दूसरे model को train करने के लिए इस्तेमाल हो सकते हैं, यह असली बाधा है, औपचारिकता नहीं।

### Formatting

यांत्रिकी एक बार सही कर लें:

- Model के अपने chat template से render करें (पाठ 3)। `repr` से जाँचें।
- Prompt positions को mask करें, जब तक आप जान-बूझकर उन्हें score न करवाना चाहें।
- End-of-turn token शामिल करें, वरना model रुकना नहीं सीखेगा।
- Token-length distribution जाँचें और `max_length` उसके ऊँचे percentile से तय करें, न अधिकतम से, न अंदाज़े से।
- पुष्टि करें कि truncation उत्तरों को आधा नहीं काट रहा। चुपचाप छँटा हुआ target model को वाक्य के बीच में रुकना सिखाता है।

## अभ्यास

1. ▢ आप चाहते हैं कि model आपकी कंपनी के 400 product SKUs जाने। क्या fine-tuning dataset सही औज़ार है?

<details markdown="1"><summary>जाँचें</summary>

नहीं। वे तथ्य हैं, जिन्हें fine-tuning अविश्वसनीय ढंग से डालती है: हर एक को कई विविध examples चाहिए होंगे, और नतीजा असत्यापनीय है और catalogue बदलते ही पुराना।

Retrieval सही औज़ार है: सटीक, उद्धरण-योग्य, और retraining के बजाय एक दस्तावेज़ को संपादित करके update होने वाला। जो fine-tuning यहाँ उपयोगी ढंग से सिखा *सकती* है वह product की जानकारी प्रस्तुत करने का format है।

</details>

2. ▢ आपके सारे training prompts साफ़, सही विराम-चिह्न वाले वाक्य हैं। Production inputs संक्षिप्त और typos से भरे हैं। क्या होता है, और आपका held-out सेट इसे क्यों नहीं पकड़ेगा?

<details markdown="1"><summary>जाँचें</summary>

Model साफ़ input पर अच्छा करता है और असली input पर बिगड़ता है, क्योंकि उसने असली input कभी देखा ही नहीं।

आपका held-out split उसी साफ़ पूल से निकला है, इसलिए वही दोष साझा करता है। वह ग़लत distribution पर प्रदर्शन मापता है और सफलता बताता है। इलाज असली deployment traffic से लिए गए training और evaluation data हैं।

</details>

3. ▢ Split करने के बाद नहीं, पहले deduplicate क्यों करें?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि split के आर-पार पड़ने वाला दोहरा जोड़ा एक training example को held-out सेट में रख देता है। तब held-out प्रदर्शन memorisation को मापता है और उसे generalisation बताता है, जो fine-tune के बारे में अपने आप को बेवक़ूफ़ बनाने का सबसे असरदार तरीक़ा है।

Split के बाद deduplicate करने से split-पार जोड़े बने रहते हैं, जो ठीक वही मामला है जो मायने रखता है।

</details>

4. ▢ कौन-सा dataset दोष ऐसा model बनाने की सबसे ज़्यादा संभावना रखता है जो कभी "मुझे नहीं पता" नहीं कहता?

    - a) एक श्रेणी के पक्ष में मज़बूत वर्ग असंतुलन
    - b) हर एक उत्तर का आत्मविश्वास से भरा और पूरा होना
    - c) Split के आर-पार दिखते लगभग-दोहरे examples
    - d) बहुत लंबी पूँछ वाला token-length distribution

<details markdown="1"><summary>जाँचें</summary>

**b)** हर एक उत्तर का आत्मविश्वास से भरा और पूरा होना।

Model अपने targets की नक़ल करता है। उचित अनिश्चितता या इनकार का कोई example न हो, तो आत्मविश्वास भरी पूर्णता ही वह अकेला व्यवहार है जो उसे दिखाया गया है, उन inputs पर भी जो उसे सही नहीं ठहराते।

</details>

5. ▢ Synthetic data के दो ख़तरे बताएँ और हर एक का एक शमन।

<details markdown="1"><summary>जाँचें</summary>

विरासत में मिली त्रुटियाँ: generator की ग़लतियाँ धाराप्रवाह, एकसार training targets बन जाती हैं। इसे असली हिस्से का नमूना लेकर पढ़ने से, और जहाँ कहीं ground truth हो उसके सामने जाँचने से कम करें।

Distribution का सिकुड़ना: generate किया data असली से ज़्यादा एकसार है। इसे असली inputs से generation शुरू करके और generation prompts को जान-बूझकर बदलकर कम करें।

</details>

6. ▢ आपके dataset की token लंबाइयाँ 50 से 8000 तक हैं, 95वाँ percentile 1200 पर। आप कौन-सा `max_length` रखते हैं, और क्या जाँचते हैं?

<details markdown="1"><summary>जाँचें</summary>

लगभग 1200 से 1500। 8000 रखना लगभग हर example के लिए padding पर activation memory बर्बाद करता है; 512 रखना एक काफ़ी हिस्से को छाँट देता है।

फिर जाँचें कि सीमा से ऊपर के examples पर truncation असल में क्या करता है। अगर वह उत्तरों को आधा काट देता है तो आप model को वाक्य के बीच में रुकना सिखा रहे हैं, इसलिए या तो सीमा बढ़ाएँ या उन examples को जान-बूझकर छोड़ दें।

</details>

## असली दुनिया का अभ्यास

- [ ] अपने dataset के बीस examples chat template से decode करके पूरे पढ़ें। जितनी भी असंगतियाँ मिलें, नोट करें।
- [ ] Split करने से पहले पूरे सेट पर लगभग-दोहरे की पहचान चलाएँ। दर्ज करें कि कितने मिले और उन्हें हटाएँ।
- [ ] Token-length distribution plot करें और उससे `max_length` चुनें। तीन ऐसे examples जाँचें जो छँट जाएँगे।
- [ ] कल: दस जान-बूझकर कठिन examples जोड़ें: अस्पष्ट, किनारे के मामले, या जहाँ सही उत्तर इनकार है।

## आगे बढ़ने के लिए

- [पेपर: "LIMA: Less Is More for Alignment", Zhou et al., arXiv:2305.11206](https://arxiv.org/abs/2305.11206)
- [दस्तावेज़: Dataset formats, Hugging Face TRL](https://huggingface.co/docs/trl/main/en/dataset_formats)
- [पाठ 22. Contamination और Held-Out Design](0022-contamination-and-held-out-design.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
