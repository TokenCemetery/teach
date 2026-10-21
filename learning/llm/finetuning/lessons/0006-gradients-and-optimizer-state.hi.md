---
title: "6. Gradients और Optimizer State"
description: "प्रति trainable parameter सोलह bytes, प्रति frozen parameter दो"
type: lesson
---

# पाठ 6. Gradients और Optimizer State

**मिशन से संबंध:** यही adapters के पक्ष की दलील है। जब आप सोलह-bytes-प्रति-parameter का आँकड़ा निकाल सकते हैं, तो LoRA कोई तरकीब नहीं रहती और स्पष्ट जवाब बन जाती है।
**मुख्य स्रोत:** [पेपर: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., arXiv:1910.02054](https://arxiv.org/abs/1910.02054)
**पूर्व-आवश्यकताएँ:** [पाठ 4](0004-what-training-changes.md), [पाठ 5](0005-counting-parameters-and-bytes.md)

## वार्म-अप

1. ▢ 7B model के weights bf16 में: कितने gigabytes?

<details markdown="1"><summary>जाँचें</summary>

लगभग 14 GB। प्रति parameter दो bytes, इसलिए bf16 gigabytes लगभग अरबों में parameters के दोगुने होते हैं।

</details>

2. ▢ AdamW प्रति trainable parameter कौन-से दो tensors रखता है?

<details markdown="1"><summary>जाँचें</summary>

Gradients का चलता औसत और gradients के वर्गों का चलता औसत, यानी first और second moments। हर एक का आकार parameter जितना है।

</details>

3. ▢ Training के लिए bf16, fp16 से बेहतर क्यों है?

<details markdown="1"><summary>जाँचें</summary>

उसकी exponent सीमा fp32 से मेल खाती है, इसलिए values infinity तक overflow नहीं होतीं। Rounding error से उबरा जा सकता है; `NaN` से नहीं।

</details>

## यह जानें

एक trainable parameter की हर लागत, प्रति parameter:

| श्रेणी | fp32 training | Mixed precision (bf16 compute, fp32 master) |
|---|---|---|
| Weights | 4 | 2 (bf16) + 4 (fp32 master copy) |
| Gradients | 4 | 2 |
| AdamW first moment | 4 | 4 |
| AdamW second moment | 4 | 4 |
| **कुल** | **16 bytes** | **16 bytes** |

![प्रति trainable parameter bytes की दो पट्टियाँ, दोनों सोलह bytes लंबी। fp32 में सोलह bytes weights, gradients और दो moments के चार-चार bytes हैं। Mixed precision में weights दो bytes का bf16 और चार bytes की master copy हैं, gradients दो bytes हैं, और दोनों moments चार पर ही रहते हैं।](images/mixed-precision-same-total.svg)

दाएँ वाला column वह हिस्सा है जो लोगों को चौंकाता है। **Mixed precision कुल को घटाता नहीं।**

दोनों पट्टियाँ एक ही निशान पर पहुँचती हैं, और पूरा नतीजा यही है। रंग वाले दो टुकड़े वे tensors हैं जो सचमुच आधे हुए, दोनों के बीच चार bytes की बचत, और पहले के बगल में बैठी master copy वही चार bytes सीधे वापस रख देती है। उसके दाएँ की हर चीज़ बिल्कुल नहीं हिली। यह weight और gradient tensors को आधा करता है, फिर weights की fp32 master copy वापस जोड़ देता है, क्योंकि छोटे updates को bf16 value में जोड़ते जाना उन्हें चुपचाप खो देता है। इसी वजह से optimizer moments fp32 में ही रहते हैं। Mixed precision का फ़ायदा arithmetic throughput है, memory नहीं।

तो: **प्रति trainable parameter 16 bytes**, एक भी activation से पहले।

### इसका मतलब

```text
1.5B trainable × 16 bytes = 24 GB
7B   trainable × 16 bytes = 112 GB
70B  trainable × 16 bytes = 1120 GB
```

7B model की full fine-tuning को अकेले optimizer-और-weight state के लिए 112 GB चाहिए, उसके ऊपर activations। यह multi-GPU इलाक़ा है उस model के लिए जिसके weights 14 GB हैं। "model समा जाता है" और "model की training समा जाती है" के बीच का फ़ासला आठ गुना है, और वह पूरी तरह gradients और optimizer state का है।

### बचाव का रास्ता

Table को फिर से देखें और ध्यान दें कि 16 bytes किस चीज़ से गुणा होते हैं: **trainable** parameters की गिनती से, कुल parameters से नहीं। Frozen parameters को अपने weights के लिए 2 bytes लगते हैं, इससे ज़्यादा कुछ नहीं। कोई gradient नहीं। कोई moments नहीं।

Adapters के पक्ष की पूरी दलील यही है:

```text
frozen parameter   = 2 bytes  (bf16 weights only)
trainable parameter = 16 bytes (weights + master + grad + 2 moments)
```

Base model को freeze करें, कुछ लाख trainable parameters जोड़ें, और दूसरा पद लगभग ग़ायब हो जाता है। 7B base और 4M trainable adapter parameters के लिए काम करके:

```text
frozen base    7B  × 2  = 14.0 GB
trainable      4M  × 16 = 0.064 GB
```

Adapter की optimizer state 64 MB है। वह base weights के सामने rounding error बन गई है, और base weights वह अकेला हिस्सा है जिस पर आप अलग से, चरण 4 में, quantisation से वार कर सकते हैं।

### आंशिक उपाय, और वे काफ़ी क्यों नहीं

Adapters के आने से पहले, लोग इस लागत को दूसरे तरीक़ों से घटाते थे। वे सब अब भी उपलब्ध हैं और सब अब भी सीमित हैं:

| तकनीक | क्या बचाती है | क्या क़ीमत लेती है |
|---|---|---|
| 8-bit optimizer | Moments 4 के बजाय 1 byte पर: 16 → 10 bytes | गुणवत्ता का हल्का जोखिम; trainable गिनती में अब भी रैखिक |
| Momentum वाला SGD | दो के बजाय एक moment: 16 → 12 bytes | Transformers के लिए साफ़ तौर पर बदतर convergence |
| Optimizer sharding (ZeRO) | State को N devices में बाँटता है | N devices और तेज़ interconnect चाहिए |
| CPU पर offload | State को accelerator से हटाता है | Bandwidth से बँधा; steps बहुत धीमे |

इनमें से हर एक constant को scale करता है। कोई भी इस तथ्य को नहीं बदलता कि लागत trainable parameters की संख्या के अनुपात में है। Adapters गुणक पर वार करते हैं, इसीलिए वे गुणकों से नहीं बल्कि परिमाण-क्रमों से जीतते हैं।

### Moments को सीधे हटाया क्यों नहीं जा सकता

एक वाजिब सवाल: अगर AdamW के दो moments लागत का दो-तिहाई हैं, तो सादा SGD क्यों नहीं? क्योंकि transformer training Adam की प्रति-parameter step scaling पर निर्भर है। Transformer के parameters में gradient का परिमाण बहुत ज़्यादा बदलता है, और एक अकेला global learning rate उनकी ठीक से सेवा नहीं करता। Second moment वही है जो हर parameter को उचित आकार का step लेने देता है। यह अनुभवजन्य है, एकसार है, और ऐसी tuning की समस्या नहीं जिसे आप चाहने भर से मिटा दें।

## अभ्यास

1. ▢ Mixed precision में AdamW के साथ 3B model की full fine-tune के लिए ज़रूरी memory निकालें, activations को छोड़कर।

<details markdown="1"><summary>जाँचें</summary>

प्रति trainable parameter 16 bytes × 3e9 = 48 GB।

अलग-अलग तोड़कर: 6 GB bf16 weights + 12 GB fp32 master + 6 GB bf16 gradients + 12 GB first moment + 12 GB second moment = 48 GB।

</details>

2. ▢ Mixed precision कुल training memory क्यों नहीं घटाता?

<details markdown="1"><summary>जाँचें</summary>

वह weights और gradients को आधा करता है पर weights की fp32 master copy जोड़ देता है, और दोनों optimizer moments को fp32 में छोड़ देता है। बचत और जोड़ आपस में कट जाते हैं, और वापस 16 bytes पर पहुँचते हैं।

Master copy वैकल्पिक नहीं है: bf16 value में बहुत छोटा update बार-बार जोड़ने पर rounding से कोई बदलाव ही नहीं होता, इसलिए update खो जाता है।

</details>

3. ▢ 7B base bf16 में frozen है और आप 20M-parameter का adapter train करते हैं। Activations को छोड़कर कुल?

<details markdown="1"><summary>जाँचें</summary>

Frozen base के लिए 14 GB (7e9 × 2) और adapter के लिए 0.32 GB (2e7 × 16), यानी लगभग 14.3 GB।

Full fine-tuning के 112 GB के सामने: 7.8× की कमी, और जो बचता है उसमें लगभग सब कुछ frozen base है। चरण 4 उसी बचे हिस्से पर वार करता है।

</details>

4. ▢ किसी तय model के लिए optimizer memory को सबसे ज़्यादा कौन-सा बदलाव घटाता है?

    - a) Optimizer को AdamW से SGD पर बदलना
    - b) Compute precision को bf16 पर बदलना
    - c) Base को freeze करके adapter train करना
    - d) Completion-only loss masking पर आना

<details markdown="1"><summary>जाँचें</summary>

**c)** Base को freeze करके adapter train करना।

(a) दो में से एक moment हटाता है, एक चौथाई बचाता है। (b) कुल मिलाकर कुछ नहीं बचाता, जैसा ऊपर दिखा। (d) बदलता है कि कौन-से positions loss में योगदान देते हैं, यह नहीं कि कितने parameters की state है। सिर्फ़ (c) trainable parameters की संख्या पर वार करता है, जो हर चीज़ पर गुणक है।

</details>

5. ▢ कोई 8-bit optimizer का प्रस्ताव रखता है ताकि वे एक 80 GB accelerator पर 70B model की full fine-tune कर सकें। अंकगणित करें और जवाब दें।

<details markdown="1"><summary>जाँचें</summary>

8-bit moments से प्रति parameter 2 + 4 + 2 + 1 + 1 = 10 bytes मिलते हैं। 70e9 × 10 = 700 GB। यह अब भी 80 GB device का लगभग नौ गुना है, activations से पहले।

तकनीक असली और उपयोगी है; योजना एक परिमाण-क्रम से ग़लत है। प्रयोग से पहले अंकगणित करने की क़ीमत यही है।

</details>

6. ▢ एक वाक्य में: frozen parameters trainable parameters से इतने सस्ते क्यों पड़ते हैं?

<details markdown="1"><summary>जाँचें</summary>

Frozen parameter को forward pass के लिए सिर्फ़ अपनी value store करनी होती है, जबकि trainable को इसके अलावा एक gradient, दो optimizer moments और एक ऊँची-precision वाली master copy चाहिए: आठ गुना ज़्यादा।

</details>

## असली दुनिया का अभ्यास

- [ ] 16-bytes वाली table काग़ज़ पर याद से बनाएँ। फिर उन तीन model आकारों के लिए कुल training memory निकालें जिनकी आपको सचमुच परवाह है।
- [ ] एक छोटा model load करें, सभी parameters पर AdamW के साथ एक training step चलाएँ, और peak memory दर्ज करें। अपने अनुमान से तुलना करें।
- [ ] कल: base को frozen रखकर और सिर्फ़ एक छोटा adapter trainable रखकर दोहराएँ। जो अनुपात आप मापेंगे वही चरण 3 की दलील है।

## आगे बढ़ने के लिए

- [पेपर: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., arXiv:1910.02054](https://arxiv.org/abs/1910.02054): इन श्रेणियों का मानक हिसाब
- [पेपर: "8-bit Optimizers via Block-wise Quantization", Dettmers et al., arXiv:2110.02861](https://arxiv.org/abs/2110.02861)
- [memory budget शीट](../reference/memory-budget.md)
- [पाठ 8. Low-Rank का विचार](0008-the-low-rank-idea.md): इस पाठ का जवाब

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
