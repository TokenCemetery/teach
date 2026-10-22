---
title: "3. Temperature"
description: "दोनों distributions को temperature से नरम करना, T squared सुधार, और hard-label loss को मिलाना"
type: lesson
---

# पाठ 3. Temperature

**मिशन से संबंध:** मिशन आपसे माँगता है कि आप distillation run का temperature और loss weights तय करें, और यह पाठ उस सेटिंग के तीन हिस्से देता है: temperature, T squared factor, और hard-label loss पर weight।
**मुख्य स्रोत:** [पेपर: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals and Dean, 2015](https://arxiv.org/abs/1503.02531)
**पूर्व-आवश्यकताएँ:** [पाठ 2](0002-soft-targets.md), [Temperature](../GLOSSARY.md), [Combined loss](../GLOSSARY.md), [Logit](../GLOSSARY.md)

## वार्म-अप

1. ▢ Temperature 1 पर एक student ने 2 को 0.98 और 3 को 0.01 probability दी, और teacher ने उन्हें 1.0 और 10^-6 दी। 3 ने loss को मुश्किल से क्यों हिलाया?

<details markdown="1"><summary>जाँचें</summary>

Cross-entropy का हर term target probability गुणा student की probability का log होता है। 3 का 10^-6 वाला target उसके term को 2 के term से 4,000 गुना से भी ज़्यादा छोटा कर देता है, इसलिए उसमें मौजूद जानकारी है पर लगभग सुनी नहीं जाती।

</details>

2. ▢ Hard label 2 और 7 की समानता के बारे में क्या कहता है, और distillation में वह जानकारी कहाँ होती है?

<details markdown="1"><summary>जाँचें</summary>

वह कुछ नहीं कहता। समानता उन छोटी probabilities में रहती है जो [teacher](../GLOSSARY.md) ग़लत classes पर रखता है, यानी [soft targets](../GLOSSARY.md) में।

</details>

## यह जानें

### Temperature

पेपर softmax की जगह ऐसा softmax लेता है जो normalize करने से पहले हर [logit](../GLOSSARY.md) को temperature T से भाग देता है: q_i = exp(z_i / T) / sum_j exp(z_j / T)। T आम तौर पर 1 होता है। ऊँचा T classes पर ज़्यादा नरम distribution देता है। पेपर की विधि है: T को तब तक बढ़ाएँ जब तक teacher ठीक-ठाक नरम targets न बनाए, फिर student को उसी ऊँचे T पर train करें ताकि वह उनसे मेल बिठाए। Training के बाद student T = 1 इस्तेमाल करता है।

```python
import numpy as np

def softmax(z, T=1.0):
    z = np.asarray(z, float) / T
    e = np.exp(z - z.max())
    return e / e.sum()

logits = [9.0, 4.0, 2.0, 0.0, -4.0]   # classes: 2, 3, 7, 8, 0
np.set_printoptions(suppress=True, precision=4)
for T in (1, 2, 5, 20):
    print("T =", T, softmax(logits, T))
```

चलाने से पहले T = 5 पर पहली class की probability का अनुमान लगाएँ। NumPy 2.5 पर output:

```text
T = 1 [0.9923 0.0067 0.0009 0.0001 0.    ]
T = 2 [0.889  0.073  0.0268 0.0099 0.0013]
T = 5 [0.5394 0.1984 0.133  0.0892 0.0401]
T = 20 [0.2745 0.2138 0.1934 0.175  0.1433]
```

T = 1 पर ग़लत classes का योग 1% से कम है। T = 5 पर वे लगभग आधी probability ढोती हैं, और क्रम 3, 7, 8, 0 अब भी दिखता है। T = 20 पर distribution लगभग समतल है, और जिन अंतरों से student को मेल बिठाना है वे छोटे हैं।

### Loss को T squared से गुणा क्यों किया जाता है

जब teacher के logits v_i हों और दोनों temperature T इस्तेमाल करें, तब student के logit z_i के सापेक्ष cross-entropy का gradient (1/T)(q_i - p_i) होता है। पेपर का equation 2 यही देता है। अगर T, logits की तुलना में बड़ा हो और logits हर example पर शून्य-माध्य हों, तो पेपर दिखाता है कि यह लगभग (1/(N T^2))(z_i - v_i) होता है, जहाँ N classes की संख्या है। इसलिए ऊँचे temperature की सीमा में distillation, 1/2 (z_i - v_i)^2 को कम करने के बराबर है, यानी Caruana और सहयोगियों का logit matching। Logits मिलाना distillation का एक विशेष मामला है।

व्यवहार में जो factor मायने रखता है वह 1/T^2 है। पेपर कहता है कि soft target gradients का परिमाण 1/T^2 की तरह घटता है, इसलिए hard और soft दोनों targets इस्तेमाल करते समय उन्हें T^2 से गुणा करना ज़रूरी है। इससे बाक़ी settings के साथ प्रयोग करते हुए T बदलने पर दोनों का सापेक्ष योगदान लगभग वैसा ही रहता है।

```python
import numpy as np

def softmax(z, T=1.0):
    z = np.asarray(z, float) / T
    e = np.exp(z - z.max())
    return e / e.sum()

teacher = np.array([9.0, 4.0, 2.0, 0.0, -4.0])
student = np.array([6.0, 5.0, 0.0, 1.0, -2.0])
for T in (1, 2, 5, 10, 20):
    grad = (softmax(student, T) - softmax(teacher, T)) / T
    print(T, "%.4f" % np.abs(grad).max(), "%.4f" % (np.abs(grad).max() * T**2))
```

Output दिखाता है कि सबसे बड़ी gradient entry T = 1 पर 0.2663 से घटकर T = 20 पर 0.0017 रह जाती है। T squared से गुणा करने पर वह T = 2 से T = 20 तक 0.64 और 0.84 के बीच रहती है। T = 1 वाली पंक्ति सही तुलना नहीं है, क्योंकि वहाँ ऊँचे temperature का सन्निकटन लागू नहीं होता।

### Combined loss

जब transfer set के लिए सही labels मौजूद हों, तो पेपर पाता है कि अकेले soft targets पर training तब बेहतर होती है जब student को सही labels पैदा करने के लिए भी train किया जाए। उसने labels से soft targets को बदलकर देखा और पाया कि दो objectives का भारित औसत बेहतर है। पहला soft targets के साथ cross-entropy है, जो ऊँचे T पर निकाला जाता है। दूसरा सही labels के साथ cross-entropy है, जो उन्हीं student logits से T = 1 पर निकाला जाता है। पेपर को आम तौर पर सबसे अच्छे नतीजे तब मिले जब दूसरे objective पर काफ़ी कम weight हो।

इस track के संकेतन में, पेपर के नहीं, लिखें तो, जहाँ lambda soft term का weight है:

```text
loss = lambda * T^2 * CE(teacher at T, student at T) + (1 - lambda) * CE(label, student at 1)
```

यह एक [combined loss](../GLOSSARY.md) है। पेपर के speech experiments में hard-label term पर 0.5 का सापेक्ष weight और 1, 2, 5 और 10 के temperatures इस्तेमाल हुए। छोटे hard-label term का कारण व्यावहारिक है: student आम तौर पर soft targets से ठीक-ठीक मेल नहीं बिठा सकता, और पेपर कहता है कि सही उत्तर की ओर झुकना मददगार निकलता है।

DistilBERT भी यही पैटर्न अपनाता है। वह training के दौरान teacher और student पर temperature वाला softmax लगाता है, inference में T को 1 रखता है, और soft-target loss में अपने terms रैखिक मेल के रूप में masked language modeling loss और cosine embedding loss के साथ जोड़ता है।

### T चुनना

पेपर MNIST पर दो अवलोकन देता है। जब distilled net की दोनों hidden layers में 300 या ज़्यादा units थे, तो 8 से ऊपर के सारे temperatures ने मिलते-जुलते नतीजे दिए। जब layers घटाकर 30 units की की गईं, तो 2.5 से 4 के temperatures ऊँचे या नीचे temperatures से काफ़ी बेहतर चले। लेखक सुझाते हैं कि जब student teacher का पूरा ज्ञान पकड़ने के लिए बहुत छोटा हो, तो बहुत ऋणात्मक logits को नज़रअंदाज़ करना, जिन्हें कम temperature घटा देता है, मदद कर सकता है।

Classifier का temperature language model में न ले जाएँ। Minitron के लेखकों ने prune किए गए LLM को उसके teacher से दोबारा train करते समय 0.1, 0.5, 1.0 और 3.0 temperatures आज़माए और सबसे अच्छे नतीजे 1.0 पर बताए (appendix A.3)। वे 1 से नीचे के मान शामिल करने का कारण देते हैं: LLM logit distributions में vision models के नुकीले distributions से ज़्यादा entropy होती है, इसलिए उन्हें उम्मीद थी कि नरम करना कम मायने रखेगा। दूसरा, बड़ा अध्ययन सहमत है। Busbridge et al. (2025) ने 198M से 1.82B parameters के students के लिए, हर एक 546M से 7.75B के teacher से distil किया गया, temperature को 0.5 से 10 तक बदला और सभी पैमानों पर सबसे अच्छा प्रदर्शन 1 पर पाया (appendix G.2)। 3 से ऊपर के temperatures ने नुक़सान किया, और छोटे students को सबसे ज़्यादा। Appendix B.3 में वे कहते हैं कि अपने उद्धृत साहित्य के उलट, इष्टतम temperature एक है, और अनुमान लगाते हैं कि अंतर इसलिए है कि पहले का काम दोहराए गए tokens इस्तेमाल करता था जबकि उनका setup data नहीं दोहराता। यह परिकल्पना उनकी है और पेपर यहाँ उसे परखता नहीं। दोनों नतीजे एक-एक lab के pretraining-शैली वाले setups के हैं, इसलिए इन्हें किसी भी sweep में T = 1 शामिल करने का मज़बूत कारण मानें, इस सबूत की तरह नहीं कि ऊँचे temperatures कभी मदद नहीं करते।

Minitron का ablation भी एक ही setup है। अपनी अंतिम विधि में उन्होंने यह भी पाया कि अकेला logit loss, language modeling loss के साथ भारित मिश्रण से बेहतर है, जो याद दिलाता है कि weight परखने की एक setting है, कोई स्थिरांक नहीं।

## अभ्यास

1. ▢ Logits 9, 4, 2, 0 और -4 लेकर, T = 5 पर पहली class को लगभग कितनी probability मिलती है?

    - a) लगभग 0.99
    - b) लगभग 0.54
    - c) लगभग 0.20
    - d) लगभग 0.01

<details markdown="1"><summary>संकेत</summary>

Logits को 5 से भाग दें, हर एक का exponential लें, और पहले को पाँचों के योग से भाग दें।

</details>

<details markdown="1"><summary>जाँचें</summary>

**b)** Scale किए गए logits 1.8, 0.8, 0.4, 0 और -0.8 हैं। उनके exponentials लगभग 6.05, 2.23, 1.49, 1.00 और 0.45 हैं, जिनका योग लगभग 11.22 है, और 6.05 / 11.22 = 0.54 है। विकल्प (a) T = 1 का उत्तर है। विकल्प (c) दूसरी class है, T = 5 पर 0.198, पहली नहीं।

</details>

2. ▢ आप T को 4 से 8 करते हैं और कुछ और नहीं बदलते। पेपर soft term को T squared से गुणा क्यों करता है?

    - a) Teacher की अपनी temperature सेटिंग को रद्द करने के लिए
    - b) यह पक्का करने के लिए कि soft targets का योग एक हो
    - c) Test के समय student का आत्मविश्वास बढ़ाने के लिए
    - d) Soft और hard gradients का संतुलन बनाए रखने के लिए

<details markdown="1"><summary>जाँचें</summary>

**d)** Soft gradients 1/T^2 की तरह घटते हैं, इसलिए इस factor के बिना T बढ़ने के साथ soft term, hard term के मुक़ाबले फीका पड़ जाता। यह (b) नहीं है: softmax पहले से normalize करता है। यह (c) नहीं है: inference में student T = 1 पर चलता है और कुछ गुणा नहीं होता। यह (a) नहीं है: teacher और student एक ही T साझा करते हैं और कोई रद्द नहीं होता।

</details>

3. ▢ पेपर के combined loss में कौन-सा term ऊँचे temperature पर चलता है, कौन-सा T = 1 पर, और किसे आम तौर पर कम weight मिलता है?

<details markdown="1"><summary>जाँचें</summary>

Teacher के soft targets के साथ cross-entropy ऊँचे T पर चलता है, student के logits को T से भाग देकर। सही labels के साथ cross-entropy उन्हीं logits पर T = 1 पर चलता है। पेपर को आम तौर पर सबसे अच्छे नतीजे तब मिले जब hard-label term पर काफ़ी कम weight था। Weights वही setting हैं जिन्हें आप tune करते हैं, इसलिए बताएँ कि किसी नतीजे में कौन-सा इस्तेमाल हुआ।

</details>

4. ▢ कोई सहकर्मी MNIST की T = 20 वाली सेटिंग को LLM distillation में कॉपी कर देता है और उसे ख़राब student मिलता है। इस पाठ में क्या इशारा करता है कि ऐसा क्यों हुआ, और उन्हें क्या करना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

Minitron का 0.1, 0.5, 1.0 और 3.0 पर ablation और Busbridge का 0.5 से 10 तक का sweep, दोनों ने सबसे अच्छे नतीजे 1 पर पाए, और Minitron के लेखक कहते हैं कि LLM logit distributions में vision models के नुकीले distributions से ज़्यादा entropy होती है। T = 20 पर ऊपर के snippet के targets लगभग समतल हैं, इसलिए जिन अंतरों को student को सीखना है वे छोटे हैं। उन्हें अपने teacher और student पर एक छोटा sweep चलाना चाहिए जिसमें T = 1 शामिल हो। दोनों नतीजे एक-एक setup से आते हैं, इसलिए वे शुरुआत की जगह हैं, नियम नहीं।

</details>

5. ▢ पेपर के MNIST experiments में temperature के चुनाव के प्रति कौन-सा student ज़्यादा संवेदनशील था, 300 या ज़्यादा hidden units वाला या 30 वाला, और संवेदनशील वाले के लिए कौन-सा दायरा चला?

<details markdown="1"><summary>जाँचें</summary>

30 unit वाला student। उसके लिए 2.5 से 4 के temperatures ऊँचे या नीचे से काफ़ी बेहतर चले, जबकि 300 या ज़्यादा units के साथ 8 से ऊपर सब कुछ मिलते-जुलते नतीजे देता था। पेपर इसे ऐसे पढ़ता है कि जब student teacher का पूरा ज्ञान रखने के लिए बहुत छोटा हो तो बहुत ऋणात्मक logits को नज़रअंदाज़ करना मदद करता है।

</details>

## असली दुनिया का अभ्यास

- [ ] दोनों scripts चलाएँ। दूसरी में temperatures को 3 और 8 कर दें और जाँचें कि आख़िरी column उसी दायरे में रहता है।
- [ ] Combined loss को student logits, teacher logits, label index, T और lambda के NumPy function के रूप में लिखें, और जाँचें कि lambda = 0 पर वह label पर सादे cross-entropy के बराबर है।
- [ ] कल: बिना नोट्स के temperature वाले softmax का सूत्र बताएँ, बताएँ कि combined loss के कौन-से terms किस temperature पर चलते हैं, और बताएँ कि T squared factor वहाँ क्यों है।

## आगे बढ़ने के लिए

- [Distillation Losses शीट](../reference/distillation-losses.md)
- [पेपर: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals and Dean, 2015](https://arxiv.org/abs/1503.02531)
- [पेपर: "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter", Sanh et al., 2019](https://arxiv.org/abs/1910.01108)
- [पेपर: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [पेपर: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
