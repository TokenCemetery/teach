---
title: "5. Forward और Reverse KL"
description: "Forward KL student को teacher के हर mode पर क्यों फैला देता है और reverse KL उसे एक पर क्यों टिका देता है"
type: lesson
---

# पाठ 5. Forward और Reverse KL

**मिशन से संबंध:** मिशन आपसे माँगता है कि आप forward और reverse KL में से चुनें, और यह पाठ दोनों दिशाएँ, वह छोटा उदाहरण जो उन्हें अलग करता है, और वे पेपर देता है जो इस पर असहमत हैं कि किसे इस्तेमाल करें।
**मुख्य स्रोत:** [पेपर: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
**पूर्व-आवश्यकताएँ:** [पाठ 4](0004-token-level-distillation.md), [Forward KL](../GLOSSARY.md), [Reverse KL](../GLOSSARY.md), [KL divergence](../GLOSSARY.md)

## वार्म-अप

1. ▢ `token_kd_loss` में divergence किस axis पर लिया जाता है, और mask आख़िरी औसत के साथ क्या करता है?

<details markdown="1"><summary>जाँचें</summary>

Divergence vocabulary axis पर, यानी आख़िरी axis पर, लिया जाता है, जिससे हर position के लिए एक संख्या मिलती है। Mask padding positions को शून्य कर देता है और mask के योग से आख़िरी भाग सिर्फ़ असली tokens पर औसत लेता है।

</details>

2. ▢ पाठ 2 में, ग़लत class पर teacher की 10^-6 probability ने cross-entropy loss को मुश्किल से हिलाया। Term का कौन-सा factor उसे छोटा बनाता है?

<details markdown="1"><summary>जाँचें</summary>

Term teacher की probability गुणा एक log अनुपात है, इसलिए 10^-6 का target उसे दस लाख गुना घटा देता है। इसे याद रखें: KL की दिशा तय करती है कि किसकी probability scaling करती है।

</details>

## यह जानें

### एक divergence की दो दिशाएँ

KL divergence सममित नहीं है। p को teacher और q को student मानें, तो [forward KL](../GLOSSARY.md) KL(p || q) है, यानी tokens पर p log(p / q) का योग। [Reverse KL](../GLOSSARY.md) KL(q || p) है, यानी q log(q / p) का योग। एकमात्र अंतर यह है कि log अनुपात को किसकी probability गुणा करती है, और वही तय करता है कि हर एक किसे दंडित करता है। GKD (Agarwal et al., 2023, section 2) यही नाम इस्तेमाल करता है।

Forward KL हर token को teacher की probability से भारित करता है। जो token teacher को पसंद है और student उसे लगभग शून्य probability देता है, उसकी क़ीमत बहुत ज़्यादा है, क्योंकि अनुपात p / q बहुत बड़ा है। जो token teacher लगभग शून्य देता है और student को पसंद है, वह सस्ता है, क्योंकि p छोटा है। Student को वहाँ कुछ mass रखने के लिए धकेला जाता है जहाँ teacher के पास mass है, जो mode covering है।

Reverse KL हर token को student की probability से भारित करता है। Student को वहाँ mass रखने पर दंड मिलता है जहाँ teacher के पास लगभग कुछ नहीं है, क्योंकि वहाँ q log(q / p) बड़ा है। Teacher के किसी mode को नज़रअंदाज़ करना कुछ नहीं खर्चता, इसलिए student एक चुनने को आज़ाद है। यह mode seeking है।

### दो modes, दो students

नीचे के teacher के पास दो बराबर संभावना वाली continuations हैं और दो दूसरी पर थोड़ी probability। पहला student अपना mass फैलाता है। दूसरा एक mode पर टिक जाता है।

```python
import numpy as np

p = np.array([0.49, 0.01, 0.01, 0.49])        # teacher: two modes
students = {
    "spread": np.array([0.25, 0.25, 0.25, 0.25]),
    "commit": np.array([0.97, 0.01, 0.01, 0.01]),
}

def kl(a, b):
    return float(np.sum(a * np.log(a / b)))

for name, q in students.items():
    print(name, "forward %.3f" % kl(p, q), "reverse %.3f" % kl(q, p))
```

अनुमान लगाएँ कि हर दिशा कौन-सा student पसंद करती है, फिर चलाएँ। NumPy 2.5 पर output:

```text
spread forward 0.595 reverse 1.273
commit forward 1.572 reverse 0.623
```

Forward KL फैले हुए student को पसंद करता है (0.595 बनाम 1.572), जो दोनों modes पर probability रखता है और दो दुर्लभ tokens पर कुछ बर्बाद करता है। Reverse KL टिके हुए student को पसंद करता है (0.623 बनाम 1.273), जो एक mode पर बैठता है और दूसरे को नज़रअंदाज़ करता है। कोई भी student teacher से मेल नहीं खाता। आप कौन-सी विफलता चाहते हैं, यह इस पर निर्भर है कि student आगे क्या करेगा, जो अगले दो पेपरों की बहस है।

### Reverse KL के पक्ष में तर्क

Gu et al. तर्क देते हैं कि मानक distillation objectives एक सन्निकटित forward KL को कम करते हैं, जो student को teacher के सारे modes कवर करने पर मजबूर करता है। Classification के लिए, classes की सीमित संख्या के साथ, दोनों distributions में कम modes होते हैं और यह अच्छा चलता है। खुले-अंत वाले generation के लिए teacher के पास किसी छोटे student के व्यक्त कर सकने से कहीं ज़्यादा modes हो सकते हैं। पेपर कहता है कि तब forward KL student से उन क्षेत्रों को अनुचित रूप से ऊँची probability दिलवाता है जहाँ teacher के पास लगभग कुछ नहीं है, और free-run generation के दौरान teacher के तहत बहुत अनसंभव samples पैदा करता है (introduction)। उनका उपाय reverse KL है, जो मुख्य modes ढूँढता है और teacher के ख़ाली क्षेत्रों को कम probability देता है। Text में, वे कहते हैं, student teacher के distribution के बहुत सारे long-tail रूप सीखने से बचता है और सही होने पर ध्यान देता है।

वे असर एक छोटे उदाहरण पर दिखाते हैं: हर divergence से एक Gaussian mixture को अकेले Gaussian से fit करना (Figure 2)। वे reverse KL को student के samples पर policy gradient से optimise करते हैं, स्थिरता के लिए अतिरिक्त चरणों के साथ, जो इसे on-policy विधि बनाता है। पाठ 15 इसे कवर करता है। Loss ख़ुद सरल है। पिछले snippet की log-probabilities के साथ, प्रति-position reverse KL, forward वाली पंक्ति की जगह `(s.exp() * (s - t)).sum(dim=-1)` है।

### चुनने के पक्ष में तर्क

GKD कोई पक्ष नहीं लेता। वह divergence को एक parameter बना देता है। उसका generalized JSD, 0 और 1 के बीच के गुणांक beta के लिए, यह है:

```text
JSD(beta)(P || Q) = beta * KL(P || beta*P + (1-beta)*Q) + (1-beta) * KL(Q || beta*P + (1-beta)*Q)
```

P को teacher मानें, तो यह दोनों दिशाओं के बीच interpolate करता है। जैसे beta 0 की ओर जाता है, gradients forward KL की तरह बर्ताव करते हैं और जैसे beta 1 की ओर, reverse KL की तरह। यह तब भी bounded है जब supports अलग-अलग हों, जो KL नहीं है (section 2)। उसी छोटे उदाहरण पर, उस सूत्र से लिखे `jsd` function के साथ (पेपर में नहीं), तीन JSD मान एक crossover देते हैं:

| Student | JSD(0.1) | JSD(0.5) | JSD(0.9) |
|---|---|---|---|
| spread | 0.055 | 0.177 | 0.091 |
| commit | 0.102 | 0.189 | 0.058 |

Beta = 0.1 पर फैला हुआ student जीतता है और beta = 0.9 पर टिका हुआ, जो उस दिशा से मेल खाता है जिसे हर सिरा पसंद करने वाला कहा जाता है। 0.5 पर वे क़रीब हैं। संख्याएँ छोटे उदाहरण से हैं, किसी run से नहीं।

GKD के experiments बताते हैं कि सबसे अच्छा divergence task पर निर्भर है। XSum summarization पर, JSD परिवार के ज़रिए forward KL से reverse KL की ओर जाने से output की विविधता घटी (Figure 4)। Ablations में, temperature sampling से आँकने पर mode-seeking divergences ने बेहतर किया, और greedy decoding के साथ चुनाव का असर कम था (section 4.1)। FLAN के साथ task-agnostic instruction tuning पर, reverse KL के साथ on-policy GKD ने supervised KD और ImitKD को काफ़ी पीछे छोड़ा, और वहाँ reverse KL ने forward KL से कहीं बेहतर किया (Figure 10)। GSM8K पर forward KL ने काफ़ी अच्छा किया, और reverse KL ने भी, ख़ासकर सिर्फ़ तय dataset पर training करते समय। पेपर का सार यह है कि divergence को task पर विविधता और गुणवत्ता के trade-off से चुनना होता है।

TRL implementation यह चुनाव `GKDConfig` में `beta` के रूप में देता है: 0.0 पर loss KL divergence है, 1.0 पर inverse KL, और default 0.5 है ([TRL GKD दस्तावेज़](https://huggingface.co/docs/trl/main/en/gkd_trainer), इस पाठ के लिए पढ़ा गया)।

### उलटी दिशा का सबूत

Minitron के लेखक prune किए गए base models को उनके unpruned teacher से दोबारा train करते हैं और दिशाओं को सीधे परखते हैं। Depth-pruned Minitron 8B पर, forward KLD वाला logit loss 2.155 के LM loss तक पहुँचा, जबकि reverse KLD के लिए 2.665 रहा (उनकी Table 16, appendix A.3)। पिछली पीढ़ी के Nemotron-3 8B पर, combined loss ने forward KLD के साथ 2.117 और reverse के साथ 2.140 दिया (Table 15)। वे ध्यान दिलाते हैं कि पहले के काम में reverse KLD supervised fine-tuning और instruction following के लिए बेहतर बैठा, कि Agarwal et al. कहते हैं कि चुनाव task पर निर्भर है, और कि उनकी base-model सेटिंग के लिए forward KLD सबसे अच्छा चुनाव है (section 4)।

इसलिए सबूत कोई एक नियम नहीं है। Reverse KL को GKD में छोटे students पर instruction-tuning नतीजों का समर्थन है, और forward KL को Minitron में base models को दोबारा train करने का। दोनों अपने-अपने models पर अकेले पेपर हैं।

## अभ्यास

1. ▢ दो-mode वाले run में forward KL कौन-सा student पसंद करता है, और reverse KL कौन-सा?

<details markdown="1"><summary>संकेत</summary>

पूछें कि किस student ने teacher के दोनों बड़े tokens पर कुछ probability रखी है, और कौन उनमें से एक को नज़रअंदाज़ करता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

Forward KL फैले हुए student को पसंद करता है (0.595 बनाम 1.572) और reverse KL टिके हुए को (0.623 बनाम 1.273)। Forward KL टिके हुए student को वहाँ 0.01 के क़रीब q रखने पर दंडित करता है जहाँ p 0.49 है। Reverse KL फैले हुए student को वहाँ 0.25 रखने पर दंडित करता है जहाँ p 0.01 है।

</details>

2. ▢ खुले-अंत वाले generation के लिए forward KL के विरुद्ध पेपर का तर्क क्या है?

    - a) Loss पूरे distribution से निकाला नहीं जा सकता
    - b) Student को उससे ज़्यादा modes कवर करने पड़ते हैं जितने वह व्यक्त कर सकता है
    - c) Teacher के बहुत आत्मविश्वासी होने पर gradient हमेशा ग़ायब हो जाता है
    - d) चलने से पहले teacher के logits को नरम करना पड़ता है

<details markdown="1"><summary>जाँचें</summary>

**b)** Text पर teacher के पास किसी छोटे student के व्यक्त कर सकने से कहीं ज़्यादा modes होते हैं, और forward KL student को उन्हें कवर करने पर मजबूर करता है, इसलिए वह उन क्षेत्रों पर mass रखता है जिन्हें teacher ख़ाली मानता है। यह (a) नहीं है: दोनों दिशाएँ पूरे distributions से निकाली जा सकती हैं। यह (c) नहीं है: वह पाठ 2 का छोटी probabilities वाला अवलोकन है, जो अलग समस्या है। यह (d) नहीं है: temperature दिशा से अलग चुनाव है।

</details>

3. ▢ JSD तालिका से, JSD(0.9) कौन-सा student पसंद करता है, और क्या यह GKD के इस कथन से मेल खाता है कि 1 के पास beta, reverse KL की तरह बर्ताव करता है?

<details markdown="1"><summary>जाँचें</summary>

टिका हुआ student (0.058 बनाम 0.091), और हाँ: reverse KL भी उसे पसंद करता है। Beta = 0.1 पर फैला हुआ student जीतता है, जैसा forward KL करता। तालिका पेपर के वर्णन की छोटी जाँच है, training run का नतीजा नहीं।

</details>

4. ▢ Minitron की Table 16 depth-pruned 8B student के लिए forward KLD के साथ 2.155 और reverse KLD के साथ 2.665 का LM loss देती है। क्या यह MiniLLM और GKD का खंडन करता है?

<details markdown="1"><summary>जाँचें</summary>

नहीं, सीधे नहीं। MiniLLM और GKD छोटे students पर instruction-following और summarization के नतीजे बताते हैं, जिनमें reverse दिशा अक्सर student द्वारा sample किए sequences पर होती है। Minitron prune किए base model को pretraining-शैली के मिश्रण पर दोबारा train करता है और LM loss मापता है। Task, student के शुरुआती बिंदु और metric में सेटिंग अलग है, इसलिए सबूत task-निर्भर चुनाव का समर्थन करता है, जैसा GKD कहता है। प्रतिबद्ध होने से पहले दोनों को अपने task पर परखें।

</details>

5. ▢ कौन-सा divergence teacher की बहुत छोटी probability के प्रति बहरा है, जैसा पाठ 2 में, और कौन-सा student को वहाँ रखे mass के लिए दंडित करता है?

<details markdown="1"><summary>जाँचें</summary>

Forward KL, teacher की बहुत छोटी probability के प्रति लगभग बहरा है क्योंकि p log अनुपात को गुणा करता है, जो पाठ 2 की समस्या है। Reverse KL, student के उस mass को दंडित करता है जो वहाँ रखा हो जहाँ teacher के पास लगभग कुछ नहीं, क्योंकि q log अनुपात को गुणा करता है। दोनों दिशाएँ एक ही छोटी संख्या के बारे में उलटे सवालों के जवाब देती हैं।

</details>

## असली दुनिया का अभ्यास

- [ ] Snippet चलाएँ, फिर teacher को `[0.45, 0.05, 0.05, 0.45]` कर दें और देखें कि दोनों दिशाओं की पसंद बदलती है या नहीं।
- [ ] GKD पेपर का Appendix A.7 खोलें और mode-seeking बनाम mode-covering KL वाले figure का caption पढ़ें। एक वाक्य में लिखें कि unimodal student हर दिशा में क्या करता है।
- [ ] कल: बिना नोट्स के बताएँ कि MiniLLM, GKD और Minitron में से हर एक कौन-सी दिशा किस सेटिंग के लिए सुझाता है।

## आगे बढ़ने के लिए

- [Distillation Losses शीट](../reference/distillation-losses.md)
- [पेपर: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
- [पेपर: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [दस्तावेज़: "Generalized Knowledge Distillation Trainer", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gkd_trainer)
- [पेपर: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
