---
title: "17. Fidelity और Generalization"
description: "अच्छी तरह generalize करने वाला student अपने teacher से असहमत क्यों हो सकता है, और दोनों में से आपको कौन-सा चाहिए"
type: lesson
---

# पाठ 17. Fidelity और Generalization

**मिशन से संबंध:** मिशन आपसे माँगता है कि आप अनुमान लगाएँ कि student क्या विरासत में पाएगा, और माप सकें कि उसने क्या खोया, जिसकी शुरुआत इस अलगाव से होती है कि वह teacher की कितनी क़रीबी नक़ल करता है और task कितना अच्छा करता है।
**मुख्य स्रोत:** [पेपर: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945), sections 3 से 7
**पूर्व-आवश्यकताएँ:** [पाठ 3](0003-temperature.md), [पाठ 16](0016-on-policy-distillation-in-practice.md), [Fidelity](../GLOSSARY.md), [Forward KL](../GLOSSARY.md), [Combined loss](../GLOSSARY.md)

## वार्म-अप

1. ▢ Combined loss दो terms जोड़ता है। कौन-सा student को teacher की ओर खींचता है और कौन-सा labels की ओर?

<details markdown="1"><summary>जाँचें</summary>

Teacher के [soft targets](../GLOSSARY.md) से divergence उसे teacher की ओर खींचता है, और [hard labels](../GLOSSARY.md) के विरुद्ध cross-entropy उसे data की ओर। एक मिश्रण गुणांक उन्हें भारित करता है।

</details>

2. ▢ Qwen3 का on-policy चरण student के अपने samples पर student और teacher के बीच KL कम करता है। Teacher-से-student वाला रूप KL की कौन-सी दिशा है, और वह किसे दंडित करता है?

<details markdown="1"><summary>जाँचें</summary>

KL(teacher || student) forward KL है। वह student को वहाँ कम probability रखने पर दंडित करता है जहाँ teacher ज़्यादा रखता है, इसलिए वह student को वह सब कवर करने के लिए धकेलता है जो teacher कवर करता है।

</details>

3. ▢ पाठ 16 में, Qwen3 के student ने benchmarks पर RL से train हुए checkpoint को हराया। क्या इससे पता चलता है कि student की predictions उसके teacher की predictions से मेल खाती हैं?

<details markdown="1"><summary>जाँचें</summary>

नहीं। Benchmark scores task को मापते हैं। Student अपने teacher की predictions से सहमत है या नहीं, यह अलग माप है, और यह पाठ इस बारे में है कि दोनों अलग क्यों हो सकते हैं।

</details>

## यह जानें

### दो चीज़ें जिनके सुधरने का distillation मतलब हो सकता है

Stanton et al. दो राशियों को अलग करते हैं जिन्हें distillation साहित्य आम तौर पर धुँधला कर देता है। **Fidelity** student की teacher की predictions से मेल खाने की क्षमता है। **Generalization** अनदेखे, in-distribution data पर student का प्रदर्शन है। वे fidelity को उन्हीं inputs पर दो संख्याओं से मापते हैं, जो दोनों section 3.2 में परिभाषित हैं:

| Metric | वह क्या मापता है |
|---|---|
| Average top-1 agreement | Inputs का वह अंश जहाँ student और teacher एक ही शीर्ष label चुनें |
| Average predictive KL | औसत KL(teacher \|\| student), हर class के प्रति संवेदनशील, सिर्फ़ शीर्ष के प्रति नहीं |

Accuracy, agreement की जगह नहीं ले सकती। पेपर का अपना उदाहरण: तीन स्वतंत्र models जिनकी test accuracy 55%, 75% और 95% है। पहला और तीसरा अधिकतम 60% inputs पर सहमत हो सकते हैं, जबकि दूसरा और तीसरा कम से कम 70% पर, फिर भी कोई नहीं कहेगा कि 75% वाला model 95% वाले का बेहतर distillation है, क्योंकि वे स्वतंत्र रूप से train हुए थे।

### "वे इसलिए सहमत हैं कि दोनों अच्छे हैं" का नियंत्रण

Models के सटीक होने भर से agreement बढ़ता है। सामान्य सुधार को मेल बिठाने के विशिष्ट सुधार से अलग करने के लिए पेपर दूसरा student भी train करता है, जो स्वतंत्र teacher से उसी प्रक्रिया से distil किया जाता है। अगर दोनों students पहले teacher से लगभग बराबर सहमत हों, तो agreement की व्याख्या generalization से होती है। अगर असली student अपने ही teacher से ज़्यादा सहमत हो, तो वह fidelity है।

### उन्होंने क्या पाया

उनके experiments ज़्यादातर CIFAR-100 पर ResNets के साथ image classification हैं, साथ में MNIST, ImageNet और appendix में एक text classification dataset (IMDB sentiment)। वे language-model generation पर experiments नहीं हैं, इसलिए उन्हें सामान्य रूप से distillation के बारे में नतीजे की तरह पढ़ें और फिर अपने LLM जोड़े पर परखें।

| खोज | पेपर में सबूत |
|---|---|
| आसान मामला: मेल बैठता है | MNIST पर LeNet-5 पर्याप्त distillation data के साथ 99% से ऊपर top-1 test agreement तक पहुँचा (section 4.1) |
| कठिन मामला: अक्सर नहीं बैठता | CIFAR-100 पर ResNet-56 self-distillation सबसे बड़े distillation set के साथ भी 80% test agreement से नीचे रहा (section 6.1) |
| बेहतर generalization बदतर fidelity के साथ आ सकता है | Self-distillation में, GAN samples से data बढ़ाने पर fidelity बढ़ी और test accuracy घटी, क्योंकि जो student teacher से मेल बिठाने में चूकता है वह बेहतर generalize कर सकता है (Figure 1a, section 4.2) |
| मज़बूत teacher के साथ दोनों मेल खाते हैं | 3-घटक ensemble को distil करने पर, ज़्यादा data के साथ fidelity और test accuracy दोनों बढ़ीं (Figure 1b) |
| यह capacity नहीं है | कम fidelity self-distillation में भी दिखती है, जहाँ student के पास teacher की अपनी capacity है, और ensemble को distil करते समय student को बड़ा करने से उसमें मुश्किल से बदलाव आया (section 4.4) |
| यह एक architecture, पैमाने या domain की बात नहीं है | VGG, ImageNet और IMDB पर मिलते-जुलते नतीजे (section 4.4) |

### व्याख्या: optimization

पेपर विफलता के लिए दो परिकल्पनाएँ परखता है। एक identifiability है: distillation data teacher के function को पहचानने के लिए बहुत छोटा है। ज़्यादा data test agreement की मदद करता है, इसलिए यह कहानी का हिस्सा है। दूसरी optimization है: student उस distillation data पर भी teacher से मेल नहीं बिठा पाता जिस पर वह train होता है।

दूसरी टिकती है। 50k synthetic images जोड़ने पर, teacher जितनी capacity वाला student distillation data पर ही सिर्फ़ 95% agreement तक पहुँचा। भारी data augmentation के साथ, तीन augmentations के लिए train agreement 80% और 90% के बीच था और तीनों के संयोजन के लिए self-distillation में लगभग 60% तक गिर गया (section 6.1)। ज़्यादा देर training से थोड़ी मदद मिली: ResNet-20 self-distillation के लिए, SGD के 5,000 epochs 83.3% train agreement तक पहुँचे जबकि 300 epochs पर 78.95%, और Adam पर जाने से fidelity घट गई (section 6.2)।

पेपर का सार एक trade-off है। Teacher के training data से परे examples जोड़ना student को function पहचानने के लिए ज़्यादा teacher labels देता है, और पहले से कठिन optimization समस्या को और कठिन भी बनाता है। पेपर के शब्दों में, अच्छी fidelity सीधे एक असाधारण रूप से कठिन optimization समस्या हल करने से जुड़ी है, जहाँ साधारण training इससे बच जाती है कि उसे उसे अच्छी तरह हल करने की ज़रूरत नहीं।

### यह आपके लिए क्या बदलता है

अगर आप distilled LLM को सिर्फ़ task accuracy से आँकते हैं, तो आप नहीं बता सकते कि teacher का कितना हिस्सा आपने विरासत में पाया। दो students एक जैसा score कर सकते हैं और agreement में बहुत अलग हो सकते हैं। चरण 8 पूरा माप बनाता है, और न्यूनतम आदत यह है: task की गुणवत्ता के बग़ल में held-out inputs पर teacher से agreement बताएँ, और उस student से तुलना करें जो किसी दूसरे teacher से distil हुआ या बिना teacher के train हुआ।

Fidelity हमेशा लक्ष्य नहीं होती। पेपर का अपना self-distillation नतीजा ऐसा student दिखाता है जो अपने teacher से मेल बिठाने में चूकता है फिर भी बेहतर generalize करता है। Fidelity तब मायने रखती है जब आप accuracy से परे के गुण विरासत में पाना चाहें: पेपर calibration या robustness transfer करना गिनाता है ताकि छोटा model बड़े की जगह सुरक्षित रूप से ले सके (section 4.3)। उसने यह भी पाया कि ensembles को distil करते समय सबसे ऊँची fidelity वाला student हमेशा सबसे अच्छी तरह calibrated था।

दोनों मापों का शुद्ध-Python स्केच, जो टिप्पणियों में दिखाया output print करता है:

```python
import math

def softmax(z):
    m = max(z)
    e = [math.exp(v - m) for v in z]
    s = sum(e)
    return [v / s for v in e]

def argmax(z):
    return max(range(len(z)), key=lambda i: z[i])

def kl(p, q):
    return sum(pi * (math.log(pi) - math.log(qi)) for pi, qi in zip(p, q))

# One row per example: logits over three classes, plus the true label.
teacher = [[3.0, 1.0, 0.0], [0.5, 2.5, 0.0], [0.0, 0.5, 3.0], [1.0, 2.0, 0.0]]
student = [[2.0, 1.5, 0.0], [0.0, 1.0, 2.0], [0.0, 0.5, 2.5], [2.0, 1.5, 0.0]]
labels = [0, 1, 2, 0]

agreement = sum(argmax(t) == argmax(s) for t, s in zip(teacher, student)) / len(labels)
mean_kl = sum(kl(softmax(t), softmax(s)) for t, s in zip(teacher, student)) / len(labels)
teacher_acc = sum(argmax(t) == y for t, y in zip(teacher, labels)) / len(labels)
student_acc = sum(argmax(s) == y for s, y in zip(student, labels)) / len(labels)

print(f"agreement {agreement:.2f}  mean KL {mean_kl:.3f}")      # agreement 0.50  mean KL 0.321
print(f"teacher accuracy {teacher_acc:.2f}  student accuracy {student_acc:.2f}")  # both 0.75
```

दोनों models 0.75 score करते हैं, और वे सिर्फ़ आधे inputs पर सहमत हैं।

## अभ्यास

1. ▢ एक teacher की accuracy 93% है और student की 91%, उसी test set पर। उनका top-1 agreement किन सीमाओं के बीच होना चाहिए?

<details markdown="1"><summary>संकेत</summary>

Student 9% inputs पर ग़लत है और teacher 7% पर। दोनों की ग़लतियों के सेट अधिकतम कितना और न्यूनतम कितना overlap कर सकते हैं?

</details>

<details markdown="1"><summary>जाँचें</summary>

84% और 98% के बीच। वे वहाँ सहमत हैं जहाँ दोनों सही हैं, और सबसे बुरा मामला यह है कि उनकी ग़लतियाँ कभी overlap न करें, जिससे 100 घटा 7 घटा 9, यानी कम से कम 84% बचता है। वे अधिकतम 98% पर सहमत हो सकते हैं: student teacher से 2 प्रतिशत अंक ज़्यादा inputs पर ग़लत है, इसलिए कम से कम 2% inputs पर teacher सही और student ग़लत है। Accuracy का मेल agreement के बारे में बहुत कम बताता है, जो पाठ का मुद्दा है।

</details>

2. ▢ पेपर के नियंत्रण में, स्वतंत्र teacher से दूसरा student क्यों train करें?

    - a) यह जाँचता है कि teacher सही train हुआ
    - b) यह fidelity को साझा कौशल से अलग करता है
    - c) यह पहले student की accuracy बढ़ाता है
    - d) यह कुल मिलाकर ज़रूरी compute घटाता है

<details markdown="1"><summary>जाँचें</summary>

**b)** अगर कोई student स्वतंत्र teacher से लगभग उतना ही सहमत है जितना अपने से, तो agreement की व्याख्या दोनों के अच्छे होने से होती है, नक़ल से नहीं। (a) यहाँ परखा नहीं जाता। (c) और (d) ग़लत हैं: दूसरा student माप का औज़ार है और पहले के बारे में कुछ नहीं बदलता।

</details>

3. ▢ ResNet-56 student और teacher के साथ CIFAR-100 self-distillation में, distillation set को GAN-generated images से बढ़ाया जाता है। Student की fidelity और student की test accuracy की दिशा का अनुमान लगाएँ।

<details markdown="1"><summary>संकेत</summary>

Self-distillation वह मामला है जहाँ student में पहले से teacher से मेल बिठाने की capacity है, और पेपर नोट करता है कि मेल न बिठा पाना ख़ुद मदद कर सकता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

Fidelity बढ़ती है और test accuracy घटती है (Figure 1a)। Self-distillation में जो student teacher से कम क़रीब से मेल बिठाता है वह बेहतर generalize करता है, इसलिए ज़्यादा fidelity accuracy की क़ीमत लेती है। 3-ensemble teacher के साथ दिशा पलट जाती है: दोनों बढ़ती हैं (Figure 1b)। आप पर कौन-सा लागू होता है यह इस पर निर्भर है कि आपका teacher स्वतंत्र रूप से train हुए student से कहीं बेहतर generalize करता है या नहीं।

</details>

4. ▢ Teacher की अपनी architecture वाला distilled student फिर भी 20% held-out inputs पर उससे असहमत है। पेपर जो परिकल्पनाएँ परखता है उन्हें सूचीबद्ध करें और बताएँ कि वह किसका समर्थन करता है।

<details markdown="1"><summary>जाँचें</summary>

Student की capacity, architecture, dataset का पैमाना, data का domain, identifiability और optimization (section 4.4)। पेपर capacity को ख़ारिज करता है, क्योंकि student के पास teacher की capacity है, और बाक़ियों को अपने सबूत पर। वह optimization का एक प्रमुख कारण के रूप में समर्थन करता है: student अपने ही training inputs पर भी teacher से मेल नहीं बिठाता। Identifiability भी तस्वीर का हिस्सा है, क्योंकि ज़्यादा data ने test agreement बढ़ाया। पेपर ने बड़ा agreement फ़ासला image tasks में पाया, इसलिए मानने से पहले अपने LLM जोड़े पर जाँचें कि वह आगे लागू होता है या नहीं।

</details>

5. ▢ इनमें से कौन-सा LLM माप पेपर के average predictive KL का सबसे क़रीबी समकक्ष है, और उसे वह क्या चाहिए जो agreement को नहीं चाहिए?

<details markdown="1"><summary>जाँचें</summary>

Held-out sequences पर औसत प्रति-position KL(teacher || student), जो चरण 2 का forward-KL token-level distillation loss है, उस data पर निकाला हुआ जो training में इस्तेमाल नहीं हुआ। उसे हर position पर teacher का पूरा distribution चाहिए, जो शीर्ष token पर agreement को नहीं चाहिए। शीर्ष-token agreement, top-1 agreement का सस्ता समकक्ष है। पेपर की classification सेटिंग से token level तक यह मैपिंग मेरा रूपांतरण है, पेपर का experiment नहीं।

</details>

## असली दुनिया का अभ्यास

- [ ] ऊपर का स्केच चलाएँ, फिर student की एक logit पंक्ति ऐसे बदलें कि दोनों models किसी दूसरे example पर असहमत हों जबकि accuracy 0.75 पर रहे। नोट करें कि agreement और mean KL का क्या हुआ।
- [ ] Stanton पेपर का section 3.2 पढ़ें और average top-1 agreement का सूत्र एक पंक्ति में लिखें। फिर लिखें कि नियंत्रण student s-prime आपको क्या बताता है।
- [ ] कल: बिना नोट्स के fidelity और generalization का फ़र्क़ बताएँ, एक मामला जहाँ ज़्यादा fidelity accuracy घटाती है, और कम fidelity के लिए पेपर की मुख्य व्याख्या।

## आगे बढ़ने के लिए

- [Student को क्या विरासत में मिलता है शीट](../reference/what-the-student-inherits.md)
- [पेपर: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
