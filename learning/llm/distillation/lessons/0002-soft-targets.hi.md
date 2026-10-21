---
title: "2. Soft Targets"
description: "गलत उत्तरों को teacher जो probabilities देता है उनमें क्या होता है, और वे hard label से समृद्ध training signal क्यों हैं"
type: lesson
---

# पाठ 2. Soft Targets

**मिशन से संबंध:** मिशन आपसे माँगता है कि आप समझा सकें कि teacher के soft targets में hard labels से ज़्यादा training signal क्यों होता है, और यह पाठ वही स्पष्टीकरण है, एक ऐसे run के साथ जिससे आप उसे जाँच सकते हैं।
**मुख्य स्रोत:** [पेपर: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals and Dean, 2015](https://arxiv.org/abs/1503.02531)
**पूर्व-आवश्यकताएँ:** [पाठ 1](0001-what-distillation-buys.md), [Soft targets](../GLOSSARY.md), [Hard label](../GLOSSARY.md), [Logit](../GLOSSARY.md)

## वार्म-अप

1. ▢ Distillation में training के दौरान किस model के weights बदलते हैं, और कौन-सा model training signal है?

<details markdown="1"><summary>जाँचें</summary>

सिर्फ़ [student](../GLOSSARY.md) सीखता है। [Teacher](../GLOSSARY.md) तय रहता है और targets देता है। Distillation loss पढ़ते समय पहली आम ग़लती इन दोनों को गड़बड़ा देना है।

</details>

2. ▢ 800 unit MNIST net ने अकेले 146 errors किए और 74 तब जब उसने 1200 unit net के outputs से भी मेल बिठाया। इन 74 ने targets में क्या था, इस बारे में क्या दिखाया?

<details markdown="1"><summary>जाँचें</summary>

Targets में generalize करने के बारे में ज्ञान था, जिसे teacher ने jittered training data से सीखा था और जिसे student ने अपने transfer set में कभी नहीं देखा। हर image के लिए hard label में इसमें से कुछ नहीं होता।

</details>

## यह जानें

### Hard label क्या फेंक देता है

Train किया हुआ classifier ज़्यादातर images के लिए सही class पर 1 के क़रीब probability देता है। ग़लत classes पर बहुत छोटी probabilities फिर भी image-दर-image अलग होती हैं। Hinton et al. MNIST का एक उदाहरण देते हैं: अंक 2 के एक रूप को 3 होने की probability 10^-6 और 7 होने की 10^-9 मिल सकती है, और 2 के दूसरे रूप को उलटी। इससे पता चलता है कि कौन-से 2 देखने में 3 जैसे हैं और कौन-से 7 जैसे, यानी data पर similarity की एक संरचना। [Hard label](../GLOSSARY.md) दोनों के लिए बस "2" कहता है।

इन probabilities से बने training target के लिए पेपर का शब्द soft targets है। इनमें जो जानकारी होती है, उसे कभी-कभी dark knowledge कहा जाता है, जो नाम इस पेपर में नहीं आता। यह track target के लिए [soft targets](../GLOSSARY.md) कहता है और दूसरे वाक्यांश से बचता है।

### पेच: छोटी संख्याएँ loss को मुश्किल से हिलाती हैं

उसी अंश में समस्या का नाम है। शून्य के इतने क़रीब probabilities transfer के दौरान cross-entropy cost पर बहुत कम असर डालती हैं। मान लें एक student 2 को 0.98 probability और 3 को 0.01 देता है, उस teacher के मुक़ाबले जो 1.0 और 10^-6 देता है। 2 loss में लगभग 0.0202 जोड़ता है और 3 लगभग 0.0000046, जो 4,000 गुना से भी कम है। Signal मौजूद है और loss उसके लिए बहरा है।

पेपर कहता है कि Caruana और सहयोगियों ने इससे बचने के लिए probabilities के बजाय squared error से logits मिलाए। Hinton et al. का ज़्यादा सामान्य जवाब यह है कि temperature तब तक बढ़ाया जाए जब तक targets इतने नरम न हो जाएँ कि मायने रखें, जो पाठ 3 है।

### इसे चलते देखें

Script पाँच अंक-classes पर एक teacher बनाती है, फिर दो students। दोनों "2" उतने ही भरोसे से predict करते हैं। Student A, teacher के मुक़ाबले 3 और 7 का क्रम उलट देता है, और student B teacher का क्रम रखता है।

```python
import numpy as np

def softmax(z, T=1.0):
    z = np.asarray(z, float) / T
    e = np.exp(z - z.max())
    return e / e.sum()

def kl(p, q):
    return float(np.sum(p * np.log(p / q)))

teacher = [9.0, 4.0, 2.0, 0.0, -4.0]    # classes: 2, 3, 7, 8, 0
student_a = [9.0, 1.0, 4.0, 0.0, -4.0]  # same top class, 3 and 7 swapped
student_b = [9.0, 4.0, 2.5, 0.0, -4.0]  # same ranking as the teacher

for T in (1, 5):
    p = softmax(teacher, T)
    print("T =", T)
    for name, z in (("A", student_a), ("B", student_b)):
        q = softmax(z, T)
        ce = -np.log(softmax(z)[0])
        print("  student", name, "hard-label CE %.4f" % ce, "KL(teacher||student) %.4f" % kl(p, q))
```

चलाने से पहले अनुमान लगाएँ: label "2" के विरुद्ध hard-label cross-entropy कौन-सा student पसंद करता है, और teacher से divergence कौन-सा? NumPy 2.5 पर यह यह print करती है:

```text
T = 1
  student A hard-label CE 0.0072 KL(teacher||student) 0.0177
  student B hard-label CE 0.0083 KL(teacher||student) 0.0001
T = 5
  student A hard-label CE 0.0072 KL(teacher||student) 0.0414
  student B hard-label CE 0.0083 KL(teacher||student) 0.0006
```

Hard label थोड़ा-सा A को पसंद करता है, उस student को जिसकी similarity संरचना ग़लत है। Teacher से divergence B को बड़े अंतर से पसंद करता है। संख्याएँ demonstration के लिए गढ़ी गई हैं, इसलिए दिशा पढ़ें, आकार नहीं। `KL` divergence, student के distribution से teacher के distribution का [KL divergence](../GLOSSARY.md) है।

### Language model के लिए यह और ज़्यादा क्यों मायने रखता है

Entropy पर पेपर का अंश सीधे language model पर लागू होता है। जब soft targets में entropy ज़्यादा हो तो वे हर training case पर hard targets से बहुत ज़्यादा जानकारी देते हैं। Next-token distribution शायद ही कभी one-hot के क़रीब होता है: कई continuations संभव होते हैं। Minitron के लेखक distillation loss पर एक appendix में कहते हैं कि LLM logit distributions में classification models के नुकीले distributions से ज़्यादा entropy होती है (Muralidharan et al., 2024, appendix A.3)। उनका अवलोकन उसी setup के बारे में है, पर इशारा उसी दिशा में है।

### उस class के बारे में जानकारी जो student ने कभी नहीं देखी

पेपर ने transfer set से हर 3 हटा दिया, इसलिए student ने कभी एक भी 3 नहीं देखा। फिर भी उसे सिर्फ़ 206 test errors मिले, जिनमें से 133 1010 test 3s पर थे। ज़्यादातर errors इसलिए आए कि 3 class का सीखा हुआ bias बहुत कम था। उस bias को 3.5 बढ़ाने पर, जो चुनाव कुल test प्रदर्शन को optimise करने के लिए किया गया, उसे 109 errors मिले, जिनमें 14 3s पर थे, और उसने 98.6% test 3s सही पहचाने। 3 कैसा दिखता है, इसका ज्ञान बाक़ी अंकों के soft targets के ज़रिए पहुँचा।

## अभ्यास

1. ▢ ऊपर के run में, T = 1 पर hard-label cross-entropy कौन-सा student पसंद करता है, और teacher divergence कौन-सा?

<details markdown="1"><summary>संकेत</summary>

पहले दोनों CE संख्याओं की तुलना करें, फिर दोनों KL संख्याओं की, और पूछें कि हर loss क्या देख सकता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

Label "2" के विरुद्ध cross-entropy A को पसंद करता है (0.0072 बनाम 0.0083)। Teacher divergence B को पसंद करता है (0.0001 बनाम 0.0177)। Hard label सिर्फ़ "2" की probability देखता है। A का 3 और 7 का ग़लत क्रम उसे दिखता ही नहीं, और वही क्रम है जो soft target ढोता है।

</details>

2. ▢ जब student को temperature 1 पर train किया जाए, तो teacher की ग़लत classes पर छोटी probabilities मुश्किल से मदद क्यों करती हैं?

    - a) Loss में सिर्फ़ सही class की entry जाती है
    - b) ग़लत class की entries loss से पहले हटा दी जाती हैं
    - c) हर term को उसकी target probability से scale किया जाता है
    - d) Student softmax बहुत छोटे मान output नहीं कर सकता

<details markdown="1"><summary>जाँचें</summary>

**c)** Cross-entropy का हर term target probability गुणा student की probability का log होता है। 10^-6 के target को 1 के क़रीब वाले target से दस लाखवाँ हिस्सा भार मिलता है। यह (b) नहीं है: उन्हें कोई हटाता नहीं। यह (a) नहीं है: वह hard-label loss का वर्णन है, soft-target loss का नहीं। यह (d) नहीं है: softmax बिना किसी दिक़्क़त के 10^-9 output कर सकता है।

</details>

3. ▢ जिस student के transfer set में कोई 3 नहीं है, वह 3 class का bias बढ़ाने के बाद 98.6% test 3s सही पहचान लेता है। उसे कैसे पता कि 3 क्या है?

<details markdown="1"><summary>जाँचें</summary>

बाक़ी अंकों पर, उदाहरण के लिए 2, 5 और 8 पर, teacher के soft targets 3 पर छोटी probability रखते हैं। वे probabilities student को सिखाती हैं कि कौन-सी features 3 का score बढ़ाती हैं, training example के रूप में एक भी 3 के बिना। उस class का सीखा हुआ bias बहुत कम था, इसलिए ज्ञान मौजूद था और offset ग़लत था। नतीजा पेपर का है, MNIST पर, एक समायोजित bias के साथ।

</details>

4. ▢ Teacher 2 को 1.0 और 3 को 10^-6 probability देता है। एक student उन्हें 0.98 और 0.01 देता है। Cross-entropy में 3 का term 2 के term से लगभग कितने गुना छोटा है?

<details markdown="1"><summary>संकेत</summary>

हर term teacher की probability गुणा student की probability का ऋणात्मक प्राकृतिक log है।

</details>

<details markdown="1"><summary>जाँचें</summary>

2 का term -1.0 \* ln(0.98), लगभग 0.0202 है। 3 का term -10^-6 \* ln(0.01), लगभग 0.0000046 है। अनुपात लगभग 4,400 है, यानी 4,000 गुना से ज़्यादा छोटा। इसीलिए इन entries को गिनती में लाने के लिए पेपर का रास्ता loss पर सीधा भरोसा करना नहीं, temperature बढ़ाना है।

</details>

## असली दुनिया का अभ्यास

- [ ] Script चलाएँ। फिर student A को ऐसे बदलें कि 3, 7 से ऊपर रहे (उदाहरण के लिए `[9.0, 3.0, 2.5, 0.0, -4.0]`) और देखें कि दोनों KL संख्याएँ student B की ओर कैसे गिरती हैं।
- [ ] कोई classifier ढूँढें जिसे आप load कर सकें, पाँच images के लिए temperature 1 पर उसका softmax print करें, और दूसरी और तीसरी सबसे ऊँची classes लिख लें। क्या वे सही class के पड़ोसी जैसी दिखती हैं?
- [ ] कल: बिना नोट्स के दो वाक्यों में समझाएँ कि hard label 2 और 7 के बीच की समानता क्यों नहीं ढो सकता।

## आगे बढ़ने के लिए

- [Distillation Losses शीट](../reference/distillation-losses.md)
- [पेपर: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals and Dean, 2015](https://arxiv.org/abs/1503.02531)
- [पेपर: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
