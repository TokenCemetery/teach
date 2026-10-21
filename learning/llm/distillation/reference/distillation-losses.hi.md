---
title: "Distillation Losses"
description: "Soft targets, temperature, combined loss, token-level loss, forward और reverse KL, tokenizer की बाध्यता और logits सहेजने की लागत"
type: reference
---

# Distillation Losses: खोजने के लिए चरण 1 और 2

चरण 1 और 2 का संक्षिप्त रूप, खोजने के लिए। [पाठ 1 से 3](../lessons/0001-what-distillation-buys.md) soft targets और temperature को कवर करते हैं, [पाठ 4](../lessons/0004-token-level-distillation.md) token-level loss को, [पाठ 5](../lessons/0005-forward-and-reverse-kl.md) divergence की दिशा को, [पाठ 6](../lessons/0006-the-tokenizer-constraint.md) tokenizer की बाध्यता को और [पाठ 7](../lessons/0007-distilling-during-pretraining.md) बड़े पैमाने पर teacher के distribution की लागत को।

## Soft targets और temperature

| शब्द | परिभाषा | स्रोत |
|---|---|---|
| Soft targets | हर class पर teacher की probabilities, जो hard label की जगह या उसके साथ target के रूप में इस्तेमाल होती हैं | Hinton et al., 2015, section 1 |
| Temperature वाला softmax | q_i = exp(z_i / T) / sum_j exp(z_j / T)। T = 1 सामान्य softmax है, ऊँचा T ज़्यादा नरम distribution देता है | Hinton et al., equation 1 |
| T कहाँ इस्तेमाल होता है | Training के दौरान teacher और student के लिए वही ऊँचा T। बाद में student T = 1 पर चलता है | Hinton et al., section 2 |
| Temperature T पर gradient | dC/dz_i = (1/T)(q_i - p_i)। बड़े T और शून्य-माध्य logits के लिए यह लगभग (1/(N T^2))(z_i - v_i) है, इसलिए logits मिलाना एक विशेष मामला है | Hinton et al., section 2.1 |
| T squared factor | Soft-target gradients 1/T^2 की तरह घटते हैं, इसलिए hard loss के साथ जोड़ते समय soft loss को T^2 से गुणा करें | Hinton et al., section 2 |

एक run में factor, logits `[9, 4, 2, 0, -4]` और `[6, 5, 0, 1, -2]` से: सबसे बड़ी gradient entry T = 1 पर 0.2663 और T = 20 पर 0.0017 है, और T squared से गुणा करने पर वह T = 2 से T = 20 तक 0.64 और 0.84 के बीच रहती है ([पाठ 3](../lessons/0003-temperature.md))।

## Combined loss

```text
loss = lambda * T^2 * CE(teacher at T, student at T) + (1 - lambda) * CE(label, student at 1)
```

संकेतन इस track का है। Hinton et al. दोनों cross-entropies के भारित औसत का वर्णन करते हैं और आम तौर पर सबसे अच्छे नतीजे तब पाए जब hard-label वाले पर काफ़ी कम weight था।

| Setting | मान | स्रोत और दायरा |
|---|---|---|
| Speech, hard term पर सापेक्ष weight | 0.5 | Hinton et al., section 4.1, एक acoustic model |
| Speech, आज़माए गए temperatures | 1, 2, 5, 10 | Hinton et al., section 4.1 |
| MNIST, 800 unit student, T = 20 पर soft targets | 74 test errors, अकेले 146 और teacher के 67 के मुक़ाबले | Hinton et al., section 3 |
| MNIST, 30 unit student, सबसे अच्छे temperatures | 2.5 से 4 | Hinton et al., section 3 |
| Kim और Rush के word-level मिश्रण weights जो आज़माए गए | 0.5 और 0.9, 0.5 बेहतर | Kim and Rush, 2016, section 4 |
| LLM pruning retraining, आज़माए गए temperatures | 0.1, 0.5, 1.0, 3.0, 1.0 पर सबसे अच्छा | Muralidharan et al., 2024, appendix A.3 |
| LLM pretraining, आज़माए गए temperatures | 0.5 से 10, सभी पैमानों पर 1 पर सबसे अच्छा | Busbridge et al., 2025, appendix G.2 |
| LLM pruning retraining, loss का मिश्रण | अकेला logit loss, language modeling loss मिलाने से बेहतर | Muralidharan et al., 2024, section 4 |

हर पंक्ति अपनी setup पर एक पेपर है। LLM temperature वाली दोनों पंक्तियाँ classifier वाली पंक्तियों से असहमत हैं, इसलिए अपने जोड़े पर T का sweep चलाएँ, जिसमें 1 भी हो।

## Token-level loss

| मद | चुनाव |
|---|---|
| Logit आकार | Student और teacher, हर एक (batch, positions, vocab) |
| Divergence axis | आख़िरी वाला, vocabulary, जिससे (batch, positions) मिलता है |
| Prefix | तय sequence, मानव text या teacher text, दोनों models को खिलाया गया (teacher forcing) |
| Teacher | Gradients बंद करके forward pass |
| Reduction | Kim और Rush positions पर योग लेते हैं। GKD और Minitron लंबाई से भाग देते हैं। Padding को mask करें और mask के योग से भाग दें |
| Temperature | Log-softmax से पहले दोनों logits को T से भाग दें, hard term के साथ मिलाने पर loss को T^2 से गुणा करें |

```python
import torch.nn.functional as F

def token_kd_loss(student_logits, teacher_logits, mask, T=1.0):
    s = F.log_softmax(student_logits / T, dim=-1)
    t = F.log_softmax(teacher_logits / T, dim=-1)
    kl = (t.exp() * (t - s)).sum(dim=-1)
    return (kl * mask).sum() / mask.sum()
```

Teacher के विरुद्ध cross-entropy और forward KL में अंतर teacher की entropy का है, जो student के लिए स्थिरांक है, इसलिए उनके gradients एक जैसे हैं। Gemma 2 -P_T(x | x_c) log P_S(x | x_c) का योग लिखता है (section 3.2)।

## Forward और reverse KL

| | Forward KL | Reverse KL |
|---|---|---|
| व्यंजक | KL(p \|\| q) = sum p log(p / q) | KL(q \|\| p) = sum q log(q / p) |
| p teacher है, q student | Teacher से भारित | Student से भारित |
| दंडित करता है | उस student को जो वहाँ कम mass देता है जहाँ teacher के पास ज़्यादा है | उस student को जो वहाँ mass देता है जहाँ teacher के पास कम है |
| व्यवहार | Mode covering, हर mode पर फैलता है | Mode seeking, एक पर टिकता है |
| पाठ 5 के छोटे उदाहरण पर | फैले हुए student को पसंद करता है, 0.595 बनाम 1.572 | टिके हुए student को पसंद करता है, 0.623 बनाम 1.273 |

| स्रोत | खोज | दायरा |
|---|---|---|
| MiniLLM, Gu et al., 2023 | Generative distillation के लिए reverse KL, क्योंकि forward KL teacher के ख़ाली क्षेत्रों को mass देता है | Instruction following, student samples पर policy-gradient |
| GKD, Agarwal et al., 2023 | सबसे अच्छा divergence task पर निर्भर है। Generalized JSD(beta) interpolate करता है, 0 के पास forward जैसा, 1 के पास reverse जैसा। FLAN instruction tuning पर reverse KL, forward से काफ़ी बेहतर | T5 students, XSum, WMT, GSM8K, FLAN |
| Minitron, Muralidharan et al., 2024 | Forward KLD सबसे अच्छा: depth-pruned 8B पर LM loss 2.155, जबकि reverse के लिए 2.665 | Pruned base models को दोबारा train करना |

TRL का `GKDConfig` यह चुनाव `beta` के रूप में देता है: 0.0 KL divergence है, 1.0 inverse KL, default 0.5।

## Tokenizer की बाध्यता

| स्थिति | क्या काम करता है | क्या क़ीमत है |
|---|---|---|
| वही tokenizer | Token-level loss | Teacher के logits चाहिए |
| Teacher से बनाया गया student (DistilBERT, Minitron) | Token-level loss | Student teacher के डिज़ाइन से बँधा |
| अलग tokenizers, logits उपलब्ध | ULD loss, या TRL का GOLD trainer | दूरी वाले term में token की पहचान खोती है, uniform cost की मान्यता, मोटा position alignment |
| सिर्फ़ teacher का text | उसके generate किए sequences पर train करें (चरण 3) | Student teacher के distributions कभी नहीं देखता |

ULD (Boizard et al., 2024): L = t पर CE(t) का योग + lambda * W1(student, teacher), lambda 1.5, W1 के साथ जो घटते क्रम में sort किए probability vectors के निरपेक्ष अंतरों का योग है (section 3)। जो student अपना mass ग़लत token पर रखे वह W1 पर 0 score कर सकता है, इसलिए gold-token cross-entropy पहचान का signal ढोती है।

TRL, जैसा पाठ 6 के लिए पढ़ा गया: `GKDTrainer` एक tokenizer `processing_class` के रूप में लेता है और उसमें teacher tokenizer का कोई argument नहीं है। GOLD को अलग tokenizers का समर्थन करने वाला बताया गया है, `use_uld_loss=True` और `teacher_tokenizer_name_or_path` के साथ, और वह `trl.experimental` में है।

## Teacher के logits सहेजने की लागत

[पाठ 7](../lessons/0007-distilling-during-pretraining.md) का गणित, Gemma 2 की 256,128 की vocabulary के साथ (Table 1)। प्रति probability 2 bytes और 4-byte index वाला k = 256 मान्यताएँ हैं, report के आँकड़े नहीं।

| राशि | मान |
|---|---|
| प्रति token पूरा distribution, bf16 | 512,256 bytes |
| प्रति 8,192-token sequence पूरा distribution | 4.20 GB |
| 2T tokens (2B run) के लिए पूरा | 1.02 EB |
| 8T tokens (9B run) के लिए पूरा | 4.10 EB |
| प्रति token Top-256, प्रति entry 6 bytes | 1,536 bytes, 333.5 गुना छोटा |
| 2T tokens के लिए Top-256 | 3.07 PB |
| 8T tokens के लिए Top-256 | 12.29 PB |

Gemma 2 की report यह नहीं बताती कि teacher का distribution कैसे दिया गया। Minitron, teacher को training के साथ forward pass में compute करता है और runs की तुलना बराबर compute पर करता है। Minitron के top-K परीक्षण में K को 100 तक रखने पर accuracy में उल्लेखनीय गिरावट मिली और बड़े K पर truncate करने से कोई फ़ायदा नहीं, एक pruned-model को दोबारा train करने की setup पर।

## और पढ़ने के लिए

- [संसाधन](../RESOURCES.md)
- [शब्दावली](../GLOSSARY.md)
