---
title: "18. DoRA: Magnitude और Direction"
description: "Renormalisation दोनों को अलग करता है, और यही तरीक़ा है"
type: lesson
---

# पाठ 18. DoRA: Magnitude और Direction

**मिशन से संबंध:** मिशन में नामित तीसरा तरीक़ा, और वह जिसका तंत्र सबसे ज़्यादा बार ग़लत बताया जाता है।
**मुख्य स्रोत:** [पेपर: "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
**पूर्व-आवश्यकताएँ:** [पाठ 8](0008-the-low-rank-idea.md), [पाठ 9](0009-rank-alpha-and-initialisation.md)

## वार्म-अप

1. ▢ LoRA का update लिखें और बताएँ कि कौन-से गुणनखंड trainable हैं।

<details markdown="1"><summary>जाँचें</summary>

`h = W₀x + (α/r)BAx`। सिर्फ़ `A` और `B` trainable हैं; `W₀` frozen है। `B` शून्य से शुरू होता है।

</details>

2. ▢ `r = 8` पर LoRA update का अधिकतम rank क्या है?

<details markdown="1"><summary>जाँचें</summary>

आठ। `BA` अपने भीतरी आयाम के rank से ज़्यादा नहीं हो सकता, जो तय करता है कि adapter कौन-से updates व्यक्त कर सकता है।

</details>

3. ▢ छोटे models पर quantisation मुफ़्त क्यों नहीं है?

<details markdown="1"><summary>जाँचें</summary>

Quantisation त्रुटि स्थिर सापेक्ष विचलन है, और छोटे models में उसे सोखने के लिए कम redundancy उपलब्ध होती है।

</details>

## यह जानें

### अवलोकन

कोई भी weight matrix **magnitude** और **direction** में बाँटी जा सकती है। Column दर column लेते हुए:

```text
W = m · (V / ‖V‖_c)
```

जहाँ `‖·‖_c` प्रति-column norm है, `V / ‖V‖_c` इकाई-norm वाले columns की matrix है, जो शुद्ध direction है, और `m` प्रति column एक scalar वाला vector है, जो magnitude ढोता है।

DoRA के लेखकों ने विश्लेषण किया कि full fine-tuning और LoRA training के दौरान इन दोनों राशियों को कैसे हिलाते हैं, और पाया कि पैटर्न अलग हैं। Full fine-tuning तुलनात्मक रूप से मामूली magnitude बदलावों के साथ अपेक्षाकृत बड़े दिशात्मक बदलाव करती है, और दोनों के बीच एक विशिष्ट संबंध दिखाती है। LoRA के updates magnitude और direction को ज़्यादा जुड़े ढंग से साथ हिलाते हैं, क्योंकि एक अकेला low-rank जोड़ने वाला पद दोनों को एक साथ बदलता है और उन्हें स्वतंत्र रूप से समायोजित करने का कोई तरीक़ा नहीं रखता।

परिकल्पना: वह जुड़ाव एक सीमा है, और दोनों को अलग करने से LoRA का सीखने का व्यवहार full fine-tuning के और क़रीब आना चाहिए।

### तरीक़ा

Frozen `W₀` को उसके magnitude और direction में बाँटें। फिर:

- **Magnitude vector `m` को सीधे trainable बनाएँ।** यह प्रति column एक scalar है, यानी `d_out` parameters, नगण्य।
- **Low-rank update को direction पर लगाएँ**, और बाद में renormalise करें।

```text
W' = m · (W₀ + BA) / ‖W₀ + BA‖_c
```

इसे ध्यान से पढ़ें, क्योंकि यहीं वर्णन ग़लत होते हैं। `BA` को weight में जोड़ा जाता है और फिर नतीजे को **इकाई columns पर renormalise** किया जाता है, जो `BA` से आया कोई भी magnitude बदलाव हटा देता है। Magnitude फिर अलग से और साफ़ तौर पर trainable `m` से दिया जाता है।

तो `BA` अब अनजाने में भी magnitude नहीं बदल सकता, क्योंकि वह सिर्फ़ direction को मोड़ता है, और `m` scale सँभालता है। यही अलगाव है, और यही पूरा योगदान है।

![Weight matrix का एक column, मूल बिंदु से एक vector के रूप में, इकाई norm दर्शाते बिंदीदार चौथाई वृत्त के साथ। बाईं ओर, W0 जमा BA कहीं ऐसी जगह पहुँचता है जहाँ कोण अलग है और लंबाई अलग। दाईं ओर, सिर्फ़ कोण बचता है: direction इकाई वृत्त पर बैठी है और m लंबाई तय करता है, यहाँ वापस W0 वाली।](images/length-and-angle.svg)

दोनों पटल वही `W0` और वही `BA` इस्तेमाल करते हैं। बाईं ओर एक पद ने दोनों राशियों को एक साथ हिलाया; दाईं ओर कोण ही वह सब है जो `BA` ने दिया, और लंबाई वही है जो `m` कहता है।

### इसकी क़ीमत

**Parameters:** हर adapt की गई layer के लिए एक अतिरिक्त vector, लंबाई `d_out`। 4096-चौड़ी layer के लिए यह rank-16 adapter के 131,072 के मुक़ाबले 4096 संख्याएँ हैं। लगभग मुफ़्त।

**Compute:** मुफ़्त नहीं। `W₀ + BA` का column norm compute करना पड़ता है, और वह `BA` पर निर्भर है, इसलिए हर step बदलता है और updates के आर-पार cache नहीं हो सकता। यह DoRA को LoRA से प्रति step नापने लायक ढंग से धीमा बनाता है, आम तौर पर दसियों प्रतिशत के क्रम का, implementation और library कितना काम fuse या cache कर पाती है उसके हिसाब से बदलता हुआ।

**जटिलता:** merging ज़्यादा उलझी है। Merge किया गया weight `m · (W₀ + BA)/‖W₀ + BA‖_c` है, फिर भी साधारण matrix, इसलिए merge किया गया DoRA सटीक है और LoRA की तरह ही inference overhead शून्य है। पर वहाँ तक पहुँचने का अंकगणित सीधा जोड़ नहीं है, और implementation मायने रखती है।

### इस्तेमाल करना

PEFT में DoRA अलग तरीक़े के बजाय LoRA config पर एक flag है:

```text
config := {
    use_dora: true,
    rank: 8,
    alpha: 32,
    target_modules: "all-linear",
    dropout: 0.05,
    adapt_bias: false,
}
```

Rank, alpha, target modules और learning rate के बारे में जो कुछ आप जानते हैं सब आगे चलता है। यह update लगाने के तरीक़े में बदलाव है, फ़ैसलों का नया सेट नहीं। हमेशा की तरह flag का नाम installed version से जाँच लें।

DoRA quantisation के साथ भी जुड़ता है: quantized base और DoRA adapter, जिसे कभी-कभी QDoRA कहते हैं। इस अंतर्क्रिया को मान लेने के बजाय मापना सार्थक है: renormalisation अब quantisation की त्रुटि ढोने वाले dequantise हुए weights पर काम करता है, जो स्पष्ट रूप से हानिरहित नहीं है।

### ईमानदार सार

DoRA साफ़ तंत्र वाला, अच्छी तरह प्रेरित सुधार है, जिसके बताए फ़ायदे कम rank पर केंद्रित हैं, और गति की असली क़ीमत है। यह LoRA का विकल्प नहीं है और हर setting पर बड़ा असर नहीं है। पाठ 19 इसके बारे में है कि भविष्यवाणी कैसे करें कि वह कब अपना ख़र्च वसूल करेगा।

## अभ्यास

1. ▢ DoRA का सूत्र लिखें और हर trainable राशि पहचानें।

<details markdown="1"><summary>जाँचें</summary>

`W' = m · (W₀ + BA) / ‖W₀ + BA‖_c`।

Trainable: magnitude vector `m`, साथ में `A` और `B`। Frozen: `W₀`।

</details>

2. ▢ Renormalisation क्या हासिल करता है?

<details markdown="1"><summary>जाँचें</summary>

वह `BA` से आया कोई भी magnitude बदलाव हटा देता है, जिससे `BA` सिर्फ़ direction को प्रभावित कर पाता है। Magnitude फिर trainable `m` से साफ़ तौर पर तय होता है।

वही अलगाव वह है जिसके नाम पर तरीक़ा है।

</details>

3. ▢ लगभग कोई parameter न जोड़ने के बावजूद DoRA, LoRA से धीमा क्यों है?

<details markdown="1"><summary>जाँचें</summary>

`W₀ + BA` का column norm compute करना पड़ता है, और क्योंकि वह `BA` पर निर्भर है, वह हर step बदलता है और updates के आर-पार cache नहीं हो सकता। अतिरिक्त parameters नगण्य हैं; अतिरिक्त अंकगणित नहीं।

</details>

4. ▢ 4096 × 4096 layer में DoRA कितने अतिरिक्त parameters जोड़ता है, और वहाँ rank-16 LoRA से उसकी तुलना कैसी है?

<details markdown="1"><summary>जाँचें</summary>

4096, हर output column के लिए एक magnitude scalar।

उस layer पर rank-16 LoRA 16 × (4096 + 4096) = 131,072 है। तो DoRA का जोड़ ऊपर से लगभग 3% है, जो हिचकने की वजह नहीं। Step का समय है।

</details>

5. ▢ क्या merge किए गए DoRA का inference overhead होता है?

<details markdown="1"><summary>जाँचें</summary>

नहीं। Merge किया गया नतीजा `m · (W₀ + BA)/‖W₀ + BA‖_c` साधारण weight matrix है, इसलिए merge किया गया DoRA inference पर किसी भी दूसरे model से अलग नहीं दिखता।

उसे बनाने का अंकगणित LoRA के सीधे जोड़ से ज़्यादा उलझा है, पर उत्पाद उसी तरह की चीज़ है।

</details>

6. ▢ कौन-सा कथन DoRA का सही वर्णन करता है?

    - a) वह magnitude पद पर दूसरा low-rank update जोड़ता है
    - b) वह magnitude को सीधे train करता है और direction को low-rank से update करता है
    - c) वह low-rank update की जगह full-rank scaling रखता है
    - d) वह weight matrix की जगह gradients को normalise करता है

<details markdown="1"><summary>जाँचें</summary>

**b)** वह magnitude को सीधे train करता है और direction को low-rank से update करता है।

कोई दूसरा low-rank गुणनखंड नहीं है। Update full-rank नहीं है। Normalisation weight पर लगता है, gradients पर नहीं।

</details>

## असली दुनिया का अभ्यास

- [ ] Decomposition हाथ से लागू करें: कोई भी weight matrix लें, प्रति-column norms निकालें, `m` और इकाई-norm `V` में बाँटें, और जाँचें कि `m · V` उसे वापस बना देता है।
- [ ] वही configuration `use_dora=True` और `False` के साथ train करें। दोनों के seconds प्रति step दर्ज करें और overhead निकालें।
- [ ] कल: DoRA पेपर का section 4 पढ़ें, जहाँ full fine-tuning बनाम LoRA का magnitude-direction विश्लेषण दिया गया है। वही विश्लेषण तर्क है।

## आगे बढ़ने के लिए

- [पेपर: "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
- [दस्तावेज़: LoRA variants, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [पाठ 19. DoRA कब जीतता है, और कब नहीं](0019-when-dora-wins.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
