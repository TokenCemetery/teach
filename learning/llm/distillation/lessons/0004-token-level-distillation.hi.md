---
title: "4. Token-Level Distillation"
description: "Sequence के हर position पर teacher के next-token distribution से मेल बिठाना"
type: lesson
---

# पाठ 4. Token-Level Distillation

**मिशन से संबंध:** मिशन आपसे माँगता है कि आप LLM के लिए token-level distillation loss लिखें, और यह पाठ उसे लिखता है: हर position पर एक divergence, sequence पर जोड़ा या औसत लिया हुआ, padding को mask करके।
**मुख्य स्रोत:** [पेपर: "Sequence-Level Knowledge Distillation", Kim and Rush, 2016](https://arxiv.org/abs/1606.07947)
**पूर्व-आवश्यकताएँ:** [पाठ 3](0003-temperature.md), [Token-level distillation](../GLOSSARY.md), [Teacher forcing](../GLOSSARY.md), [KL divergence](../GLOSSARY.md)

## वार्म-अप

1. ▢ Combined loss में कौन-सा term ऊँचे temperature पर चलता है, और उसे किससे गुणा किया जाता है?

<details markdown="1"><summary>जाँचें</summary>

Teacher के soft targets के साथ cross-entropy ऊँचे temperature T पर चलता है, और उसे T squared से गुणा किया जाता है ताकि T बदलने पर hard-label term के मुक़ाबले उसके gradients अपना आकार बनाए रखें। Hard-label term T = 1 पर चलता है।

</details>

2. ▢ T = 1 पर ग़लत class पर teacher की 10^-6 probability loss को लगभग दिखती क्यों नहीं?

<details markdown="1"><summary>जाँचें</summary>

उस class के लिए cross-entropy term उसकी target probability गुणा student की probability का log है, इसलिए 10^-6 का target उस term को 1 के क़रीब वाले term का लगभग दस लाखवाँ हिस्सा भारी बना देता है। ऊँचा T उन targets को उठा देता है ताकि वे गिने जाएँ।

</details>

## यह जानें

### शुरुआत: word-level distillation

Kim और Rush, Hinton का विचार translation पर लगाते हैं। Neural translation model को source वाक्य और उससे पहले के शब्दों को देखते हुए हर target शब्द के negative log-likelihood को कम करने के लिए train किया जाता है, इसलिए वाक्य के हर position पर एक teacher मौजूद है। वे एक वाक्य के लिए word-level loss को positions j और target vocabulary V के हर शब्द k पर योग के रूप में परिभाषित करते हैं:

```text
L_WORD-KD = - sum_j sum_k q(t_j = k | s, t_<j) * log p(t_j = k | s, t_<j)
```

यहाँ q teacher है, p student, s source वाक्य, और हर probability का आख़िरी argument prefix है, यानी position j से पहले के target शब्द। Student इस loss और साधारण word-level negative log-likelihood के मिश्रण पर भी train हो सकता है। वे इसे word-level knowledge distillation कहते हैं (section 3.1)। LLM में इकाई एक token है, इसीलिए यह track [token-level distillation](../GLOSSARY.md) कहता है।

ध्यान दें कि conditioning क्या है। Prefix training data के असली target sequence से आता है। पेपर की Figure 1 इसे असली target sequence के हर शब्द के लिए student और teacher distributions के बीच cross-entropy कम करने के रूप में वर्णित करती है। दोनों models को एक ही तय prefix खिलाया जाता है और हर एक अगले शब्द के लिए distribution देता है, जो [teacher forcing](../GLOSSARY.md) है।

अंग्रेज़ी से जर्मन WMT 2014 पर (Table 1), 500 units की 2 layers वाले student ने greedy decoding से 14.7 BLEU और beam search से 17.6 पाए। Word-level distillation के साथ उसे 15.4 और 17.7 मिले, यानी 0.7 और 0.1 का फ़ायदा। 4 layers, 1000 units वाले teacher को 17.7 और 19.5 मिले। लेखकों ने 0.5 और 0.9 के मिश्रण weights परखे और 0.5 को बेहतर पाया। पेपर कहता है कि word-level distillation baseline से बेहतर है, और उसकी sequence-level विधि और बेहतर करती है, जो चरण 3 का विषय है।

### LLM के लिए loss

तीन हाल के पेपर वही loss थोड़े अलग रूपों में लिखते हैं। वे संरचना पर सहमत हैं: हर position पर दो next-token distributions के बीच एक divergence, जो sequence पर मिलाया जाता है।

- Gemma 2 (Gemma Team, 2024, section 3.2) teacher और student की probabilities के बीच negative log-likelihood को कम करता है, x पर योग -P_T(x | x_c) log P_S(x | x_c), जहाँ x_c context है।
- GKD (Agarwal et al., 2023, equation 2) positions पर divergence का औसत लेता है: divergence को output positions n पर जोड़ा जाता है और output की लंबाई L_y से भाग दिया जाता है।
- Minitron (Muralidharan et al., 2024, section 3) sequence की लंबाई l पर औसत लेता है, softmax में temperature tau के साथ।

Cross-entropy और forward KL में अंतर teacher के distribution की entropy का है, जो student पर निर्भर नहीं करती। Student के parameters के सापेक्ष उनके gradients एक जैसे हैं, इसीलिए पेपर एक ही objective के लिए कोई भी नाम इस्तेमाल करते हैं। Vocabulary पर योग हर term के अंदर है। इसलिए computation का आकार यह है: हर model के लिए logits का tensor जिसके आयाम batch, position और vocabulary हैं, और आख़िरी axis पर लिया गया divergence।

```python
import torch.nn.functional as F

def token_kd_loss(student_logits, teacher_logits, mask, T=1.0):
    # logits: (batch, positions, vocab). mask: (batch, positions), 1.0 for real tokens.
    s = F.log_softmax(student_logits / T, dim=-1)
    t = F.log_softmax(teacher_logits / T, dim=-1)
    kl = (t.exp() * (t - s)).sum(dim=-1)        # (batch, positions)
    return (kl * mask).sum() / mask.sum()        # mean over real tokens
```

Teacher के logits gradients बंद करके forward pass से आते हैं। उस function के तीन चुनाव फ़ैसले हैं, तथ्य नहीं। असली tokens पर औसत की जगह योग भी हो सकता था, जैसा Kim और Rush लिखते हैं, और योग sequence की लंबाई के साथ बढ़ता है। Mask इसलिए मायने रखता है कि padding positions का कोई सार्थक target नहीं होता। और T = 1 default इसलिए है कि पाठ 3 में Minitron का temperature ablation है।

### वही गणित, चलाकर देखें

नीचे का NumPy संस्करण ऊपर के function का गणित तीन positions और चार tokens पर करता है, किसी framework के बिना। तीसरे position पर teacher और student के logits बिल्कुल मेल खाते हैं, जो padding का प्रतिनिधित्व करता है।

```python
import numpy as np

def log_softmax(z):
    z = z - z.max(axis=-1, keepdims=True)
    return z - np.log(np.exp(z).sum(axis=-1, keepdims=True))

teacher = np.array([[3.0, 1.0, 0.0, -1.0],
                    [0.0, 2.5, 2.0, -2.0],
                    [1.0, 1.0, 1.0, 1.0]])
student = np.array([[2.0, 1.5, 0.5, -1.0],
                    [0.5, 2.0, 2.0, -1.0],
                    [1.0, 1.0, 1.0, 1.0]])
t, s = log_softmax(teacher), log_softmax(student)
kl = (np.exp(t) * (t - s)).sum(axis=-1)
mask = np.array([1, 1, 0])
print(np.round(kl, 4), round(kl.sum(), 4), round(kl.mean(), 4))
print(round((kl * mask).sum() / mask.sum(), 4))
```

चलाने से पहले आख़िरी संख्या का तीनों के औसत से तुलनात्मक अनुमान लगाएँ। NumPy 2.5 पर output:

```text
[0.1998 0.0541 0.    ] 0.2539 0.0846
0.127
```

तीनों positions पर औसत लेने से loss उस position से पतला हो जाता है जो कोई signal नहीं ढोता। दो असली tokens पर औसत 0.127 देता है।

### तय sequence की क्या क़ीमत है

Sequences training से पहले तय होते हैं, चाहे मानव का text हों या teacher का लिखा text, और student teacher का distribution सिर्फ़ उन्हीं sequences के साथ देखता है। Generation के समय student अपने tokens से आगे बढ़ता है, जिन्हें यहाँ कोई distribution कवर नहीं करता था। चरण 5 का पाठ 14 इसे exposure bias नाम देता है, और पाठ 15 on-policy हल दिखाता है। Teacher हर batch के लिए एक forward pass भी माँगता है, जिसे Minitron के लेखक सामान्य training के मुक़ाबले distillation का अतिरिक्त overhead गिनाते हैं (section 4)।

## अभ्यास

1. ▢ NumPy run में असली tokens पर औसत, 0.127, तीनों positions पर औसत, 0.0846, से ज़्यादा क्यों है?

<details markdown="1"><summary>संकेत</summary>

हर भाजक में positions गिनें, और देखें कि तीसरा position अंश में क्या जोड़ता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

तीसरा position अंश में 0 जोड़ता है पर सादे औसत के भाजक में गिना जाता है: 0.2539 / 3 = 0.0846। Mask के साथ भाजक 2 है और 0.2539 / 2 = 0.127। भारी padding वाले असली batch में बिना mask का औसत loss को कम बताता है, और यह कमी padding की मात्रा के साथ बदलती है।

</details>

2. ▢ Kim और Rush के word-level loss में teacher और student दोनों किस prefix पर condition होते हैं?

    - a) Training data के target शब्द
    - b) वे शब्द जो student ने अपने आप sample किए
    - c) वे शब्द जो teacher ने greedy decoding से चुने
    - d) Input source वाक्य के शब्द

<details markdown="1"><summary>जाँचें</summary>

**a)** Prefix असली target sequence है, इसलिए दोनों models वही तय शब्द देखते हैं। यह (b) नहीं है: वह पाठ 15 की on-policy सेटिंग है। यह (c) नहीं है: teacher के अपने output को decode करना चरण 3 की sequence-level विधि है। यह (d) नहीं है: source वाक्य दूसरा conditioning input, s, है, prefix नहीं।

</details>

3. ▢ Gemma 2 teacher की probabilities के विरुद्ध cross-entropy कम करता है, और Minitron KL divergence लिखता है। दोनों एक ही training signal का वर्णन क्यों कर सकते हैं?

<details markdown="1"><summary>जाँचें</summary>

Forward KL, cross-entropy में से teacher की entropy घटाने के बराबर है, और teacher तय है, इसलिए वह entropy student के parameters के सापेक्ष स्थिरांक है। दोनों losses मान में अलग हैं, gradient में नहीं। पेपरों के बीच loss की संख्याएँ तुलना करने से पहले किसी भी नए पेपर में देखें कि उसका मतलब कौन-सा है।

</details>

4. ▢ `token_kd_loss` को ऐसे बदलें कि वह पाठ 3 का temperature और T squared factor लगाए। कौन-से दो बदलाव, और function में उनमें से एक पहले से क्यों था?

<details markdown="1"><summary>जाँचें</summary>

Function पहले से log-softmax से पहले दोनों logits को T से भाग देता है, इसलिए temperature मौजूद है। जो कमी है वह factor है: जब loss को hard-label term के साथ मिलाएँ तो लौटाए गए loss को T ** 2 से गुणा करें, ताकि T बदलने पर soft term अपना weight बनाए रखे। T = 1 पर factor 1 है, इसीलिए ऊपर के function को अपने default पर बदलाव की ज़रूरत नहीं।

</details>

5. ▢ एक साथी बताता है कि उनके LLM run का distillation loss, batches को ज़्यादा लंबाई तक pad करने के बाद आधा रह गया। Model नहीं बदला है। आप सबसे पहले क्या जाँचेंगे?

<details markdown="1"><summary>संकेत</summary>

Padding positions पर कोई model अपने आप से बिल्कुल मेल खाता है, इसलिए वे शून्य divergence जोड़ते हैं।

</details>

<details markdown="1"><summary>जाँचें</summary>

यह कि औसत सारे positions से भाग देता है या सिर्फ़ असली tokens से। पहले मामले में, लंबी pad length भाजक में positions जोड़ती है और संख्या गुणवत्ता में बिना किसी बदलाव के गिर जाती है। Mask के योग से भाग दें, जैसा ऊपर का function करता है, और दोनों runs की दोबारा तुलना करें।

</details>

## असली दुनिया का अभ्यास

- [ ] NumPy snippet चलाएँ। फिर पहले position पर student के logits को teacher के बराबर कर दें और पुष्टि करें कि प्रति-position loss की पहली entry 0 पर गिर जाती है।
- [ ] GKD पेपर खोलें और equation 2 ढूँढें। उसके बग़ल में लिखें कि वह positions पर योग लेता है या औसत और यह Kim और Rush के योग से कैसे तुलना खाता है।
- [ ] कल: बिना नोट्स के `token_kd_loss` में हर tensor का आकार लिखें, फिर बताएँ कि mask किसे बचाता है।

## आगे बढ़ने के लिए

- [Distillation Losses शीट](../reference/distillation-losses.md)
- [पेपर: "Sequence-Level Knowledge Distillation", Kim and Rush, 2016](https://arxiv.org/abs/1606.07947)
- [पेपर: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [पेपर: "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
