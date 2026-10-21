---
title: "17. QLoRA की असली क़ीमत"
description: "Base की गिरावट को training की गिरावट से अलग करना"
type: lesson
---

# पाठ 17. QLoRA की असली क़ीमत

**मिशन से संबंध:** मिशन कहता है "मापे गए फ़र्क़ समझाएँ, विज्ञापित वाले नहीं"। यह पाठ वही माप है।
**मुख्य स्रोत:** [पेपर: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
**पूर्व-आवश्यकताएँ:** [पाठ 16](0016-training-through-a-quantized-base.md)

## वार्म-अप

1. ▢ Frozen 4-bit base फिर भी gradients कैसे पास कर सकता है?

<details markdown="1"><summary>जाँचें</summary>

वह graph में एक constant है। Gradient पहुँचाने के लिए उसे ऊँची precision पर पढ़ना पड़ता है, उसके सापेक्ष derivative लेना नहीं, और उसके लिए कोई gradient store नहीं होता।

</details>

2. ▢ QLoRA का कौन-सा घटक सचमुच CUDA-विशिष्ट है?

<details markdown="1"><summary>जाँचें</summary>

Paged optimizers, जो NVIDIA unified memory पर निर्भर हैं। और वे adapter training के लिए सबसे कम मायने रखते हैं, जहाँ optimizer state छोटी है।

</details>

3. ▢ 4-bit base के सामने train हुए adapter को आप कहाँ merge करते हैं?

<details markdown="1"><summary>जाँचें</summary>

Full-precision base में, फिर ज़रूरत हो तो बाद में quantise करें।

</details>

## यह जानें

### पेपर का दावा, सटीक रूप में

QLoRA का मुख्य नतीजा यह है कि 4-bit NF4 adapter fine-tuning मापे गए tasks पर 16-bit fine-tuning के प्रदर्शन की बराबरी कर सकती है। यह मज़बूत नतीजा है और असली है।

यह **ख़ास benchmarks पर एक ख़ास setup** के बारे में दावा भी है। जो यह स्थापित नहीं करता:

- कि NF4 *आपके* task पर मुफ़्त है। Instruction-following benchmarks आपका production distribution नहीं हैं।
- कि quantisation हर पैमाने पर मुफ़्त है। Quantisation त्रुटि एक स्थिर सापेक्ष विचलन है, और छोटे models में उसे सोखने के लिए कम redundancy होती है, इसलिए गिरावट आम तौर पर बड़े models की तुलना में छोटे models पर ज़्यादा दिखती है।
- कि हर 4-bit implementation समतुल्य है। Quantisation का प्रकार, block size, double quantisation चालू है या नहीं, compute dtype और kernel की गुणवत्ता, सब बदलते हैं।

पेपर के दावे को "quantisation मुफ़्त है" पढ़ना ठीक वही विफलता है जिसकी ओर मिशन का वाक्यांश *मापा हुआ, विज्ञापित नहीं* इशारा करता है।

### दोनों क़ीमतों को अलग करना

गुणवत्ता के दो अलग सवाल हैं और उन्हें मिला देने से नतीजे अव्याख्येय हो जाते हैं।

**क़ीमत 1. Quantized base, किसी भी training से पहले, बदतर model है।** पूरी तरह representation का गुण।

**क़ीमत 2. Quantized base के सामने training बदतर adapter देती है।** Training प्रक्रिया का गुण, क़ीमत 1 के ऊपर।

उन्हें अलग-अलग मापें:

| Configuration | क्या अलग करती है |
|---|---|
| bf16 base, कोई adapter नहीं | संदर्भ बिंदु |
| 4-bit base, कोई adapter नहीं | क़ीमत 1, अकेला quantisation का नुक़सान |
| bf16 base + adapter | Training की ऊपरी सीमा |
| 4-bit base + adapter | क़ीमत 1 और 2 मिलाकर |
| bf16 base में merge किया गया 4-bit-trained adapter | क्या क़ीमत 1 artifact तक बची रहती है |

![Base precision बनाम adapter दो-गुना-दो grid के रूप में, जिसमें संदर्भ बिंदु, training की ऊपरी सीमा, अकेली क़ीमत 1 और दोनों क़ीमतें साथ हैं, और grid के नीचे पाँचवाँ डिब्बा 4-bit पर train होकर bf16 base में merge किए गए adapter के लिए।](images/the-one-that-is-not-a-cell.svg)

पाँच में से चार configurations एक ही grid के खाने हैं। पाँचवीं नहीं है, क्योंकि वह training के लिए और deployment के लिए अलग base इस्तेमाल करती है, और जिस configuration के लिए कोई खाना नहीं, उसे चलाना भूल जाना आसान है।

वह आख़िरी पंक्ति दिलचस्प है और नियमित रूप से छोड़ दी जाती है। आपने बिगड़े base के सामने train किया, पर आप full-precision वाले के सामने *deploy* कर सकते हैं। क्या adapter ने quantisation की त्रुटि की भरपाई करना सीख लिया, और इसलिए त्रुटि के ग़ायब होने पर बेमेल है, यह आपके task के लिए असली जवाब वाला अनुभवजन्य सवाल है। किसी भी तरफ़ मान लेने के बजाय इसे मापें।

### इसे ईमानदारी से कैसे मापें

**बाक़ी सब कुछ स्थिर रखें।** वही data, वही split, वही seed, वही rank, alpha, learning rate, schedule और steps। एक चर: base precision। जिस तुलना में दो बदलाव हों वह तुलना नहीं है।

**Task metric इस्तेमाल करें, loss नहीं।** Loss configurations के आर-पार उस तरह तुलनीय नहीं जैसा आप चाहते हैं, और वह वही नहीं जिसकी आपको परवाह है। Metric का चुनाव पाठ 23 में है।

**बिंदु नहीं, फैलाव बताएँ।** हर configuration को तीन seeds से चलाएँ। अगर आपका seed-से-seed फ़र्क़ 2 अंक है और आपका quantisation असर 1 अंक है, तो आपने कुछ नहीं मापा, और यह लगातार होता है। दो configurations की एक-seed वाली तुलना किस्सा है।

**गति और memory भी मापें।** आप इसीलिए quantisation पर विचार कर रहे हैं, इसलिए वे गुणवत्ता के साथ उसी table में आती हैं।

### एक सार्थक नतीजों की table

| Config | Task metric | Peak memory | Sec/step |
|---|---|---|---|
| bf16 base + adapter | | | |
| NF4 base + adapter | | | |
| बिना double quant के NF4 | | | |
| NF4 के बजाय int4 | | | |
| NF4, eval के लिए bf16 में merge किया गया | | | |

इसे एक बार किसी ऐसे task पर भरना जिसकी आपको परवाह है, quantisation के बारे में कितने भी पढ़ने से ज़्यादा मूल्यवान है। ख़ासकर आख़िरी पंक्ति आपको वह बताएगी जो आप कहीं देखकर नहीं जान सकते।

### क्या उम्मीद रखें, ताकि आप चौंक सकें

साहित्य और आम practice से मोटी अपेक्षाएँ, ऐसी पूर्व-धारणा के रूप में जिसे अपडेट किया जाए, नतीजे के रूप में नहीं:

- **Memory:** base weights पर लगभग 4× की कमी। भरोसेमंद, यह अंकगणित है।
- **गति:** प्रति step धीमी, अक्सर साफ़ तौर पर। Dequantisation असली काम है।
- **गुणवत्ता:** छोटी गिरावट, बड़े models पर अक्सर seed noise के भीतर, छोटे models पर और संकरे अंतर वाले tasks पर ज़्यादा दिखती हुई।
- **NF4 बनाम int4:** बराबर storage पर NF4 बेहतर।
- **Double quantisation:** नगण्य गुणवत्ता असर के साथ memory की बचत।

अगर आपके माप इनसे तीखे असहमत हों, तो उसे ख़ारिज करने के बजाय जाँचना सार्थक है। सबसे आम कारण आपके backend पर बिना-optimise kernel का रास्ता है, या ऐसी तुलना जहाँ एक से ज़्यादा चीज़ें बदलीं।

### QLoRA तक कब पहुँचें

**इसे तब इस्तेमाल करें जब memory बाध्यकारी बाधा हो**, यानी जब bf16 base और activations नहीं समाते और विकल्प या तो training न करना है या छोटा model train करना। 4-bit का बड़ा model आम तौर पर bf16 के छोटे model को हराता है।

**इसे तब इस्तेमाल न करें जब memory बाधा न हो।** अगर bf16 समाता है, तो quantise करना बिना किसी बात के आपको गति और थोड़ी गुणवत्ता की क़ीमत देता है। हमेशा 4-bit में load करने की tutorial वाली आदत तब बिना फ़ायदे की लागत है जब आपके पास वैसे भी memory थी।

## अभ्यास

1. ▢ QLoRA का मुख्य दावा बताएँ, फिर बताएँ कि वह क्या स्थापित नहीं करता।

<details markdown="1"><summary>जाँचें</summary>

दावा: 4-bit NF4 adapter fine-tuning मापे गए benchmarks पर 16-bit fine-tuning के प्रदर्शन की बराबरी कर सकती है।

स्थापित नहीं करता: कि यह आपके task और distribution पर लागू होता है, कि यह छोटे model पैमाने पर भी बराबर लागू होता है, या कि कोई भी 4-bit implementation पेपर वाली के समतुल्य है।

</details>

2. ▢ दो अलग गुणवत्ता-क़ीमतों के नाम बताएँ और उन्हें कैसे अलग करते हैं।

<details markdown="1"><summary>जाँचें</summary>

क़ीमत 1: quantized base training से पहले बदतर model है, इसलिए बिना adapter के base को मापें, quantized बनाम नहीं।

क़ीमत 2: quantized base के सामने training बदतर adapter देती है, इसलिए quantized और full-precision bases पर train हुए adapters की तुलना करें, बाक़ी सब स्थिर रखकर।

</details>

3. ▢ आप bf16 के लिए 71.2 और NF4 के लिए 70.8 मापते हैं। क्या quantisation आपको 0.4 अंक की क़ीमत दे रहा है?

<details markdown="1"><summary>जाँचें</summary>

पता नहीं। Seed के फैलाव के बिना आप 0.4 को noise से अलग नहीं कर सकते, और fine-tuning run पर seed-से-seed फ़र्क़ अक्सर इससे ज़्यादा होता है।

हर configuration के लिए तीन seeds चलाएँ और distributions की तुलना करें। इस आकार का एक-seed वाला फ़र्क़ नतीजा नहीं है।

</details>

4. ▢ कौन-सी तुलना सबसे ज़्यादा छोड़ी जाती है, और वह आपको क्या बताती है?

<details markdown="1"><summary>जाँचें</summary>

Full-precision base में merge किए गए 4-bit-trained adapter का evaluation।

यह बताती है कि क्या quantisation की क़ीमत का आपके deploy किए artifact तक बचे रहना ज़रूरी है भी। आपने सस्ते में train किया, पर कोई चीज़ आपको सस्ते में serve करने को बाध्य नहीं करती। यह भी उजागर करती है कि क्या adapter ने ख़ुद quantisation की त्रुटि के हिसाब से ढलना सीख लिया।

</details>

5. ▢ आपका bf16 run आराम से memory में समाता है। क्या आपको फिर भी 4-bit पर जाना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

नहीं। आप उस memory को बचाने के लिए धीमे steps और गुणवत्ता का छोटा जोखिम चुकाएँगे जिसकी आपके पास कमी नहीं थी।

Quantisation बाध्यकारी memory बाधा का जवाब है। उसे आदतन लगाना, क्योंकि tutorial ने लगाया, बिना किसी संगत फ़ायदे की लागत है।

</details>

6. ▢ NF4 आपके 1B-model वाले task को साफ़ तौर पर बिगाड़ता है पर पेपर ने कोई गिरावट नहीं बताई। क्या आप पेपर का खंडन कर रहे हैं?

<details markdown="1"><summary>जाँचें</summary>

नहीं। Quantisation त्रुटि स्थिर सापेक्ष विचलन है और छोटे models में उसे सोखने के लिए कम redundancy होती है, इसलिए गिरावट आम तौर पर छोटे पैमाने पर ज़्यादा दिखती है। आपका task और metric भी मापे गए benchmarks से अलग हैं।

दोनों नतीजे सही हो सकते हैं। यही ठीक वजह है कि मिशन विज्ञापित नहीं, मापे हुए फ़र्क़ माँगता है।

</details>

## असली दुनिया का अभ्यास

- [ ] किसी ऐसे task पर जिसकी आपको परवाह है, पाँच-पंक्ति वाली तुलना table भरें। हर पंक्ति के लिए तीन seeds।
- [ ] गुणवत्ता की संख्या के साथ हर पंक्ति के लिए peak memory और seconds प्रति step मापें।
- [ ] bf16 base में merge किए गए 4-bit-trained adapter का evaluation करें। लिखें कि वह 4-bit में serve किए गए रूप से बेहतर रहा, बराबर रहा, या हारा।
- [ ] कल: एक अनुच्छेद लिखें जो संख्याओं के साथ बताए कि quantisation ने *आपको* क्या क़ीमत दी, और वह आपकी अपेक्षा से कैसे अलग है।

## आगे बढ़ने के लिए

- [पेपर: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314): limitations वाला हिस्सा पढ़ें
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/): consumer hardware पर practitioner मापों का सबसे बड़ा भंडार, और अपनी संख्याओं को परखने लायक
- [पाठ 23. ऐसी Metrics जिनका मतलब हो](0023-metrics-that-mean-something.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
