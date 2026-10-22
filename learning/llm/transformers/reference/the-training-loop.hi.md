---
title: "Training Loop"
description: "Vocabulary पर cross-entropy loss, backward pass और autograd, और AdamW optimizer step, logits से अपडेट की हुई weights तक"
type: reference
---

# Training Loop: Loss, Backward Pass और Optimizer

चरण 4, खोजने के लिए संक्षिप्त किया हुआ। [पाठ 9](../lessons/0009-cross-entropy-loss.md) logits को एक अकेले scalar loss में बदलना कवर करता है; [पाठ 10](../lessons/0010-backward-pass-and-autograd.md) उस scalar को हर weight के gradient में बदलना कवर करता है; [पाठ 11](../lessons/0011-adamw-optimizer.md) gradients को weight updates में बदलना कवर करता है। यह शीट तीन सूत्र हैं, उसी क्रम में जिसमें training असल में उन्हें इस्तेमाल करती है।

## Cross-entropy loss

```text
loss = -log(p_correct)
```

| `p_correct` | Loss | इसका अर्थ |
|---|---|---|
| 0.8 | `-log(0.8) ≈ 0.223` | आत्मविश्वास से सही, छोटा जुर्माना |
| 0.1 | `-log(0.1) ≈ 2.303` | आत्मविश्वास से ग़लत, probability में 10x गिरावट पर 10x से ज़्यादा जुर्माना |

`p` के 0 के क़रीब पहुँचने पर `-log(p)` बिना किसी सीमा के बढ़ता है; सरल `1 - p` जुर्माना 1 पर saturate हो जाता है और "कुछ ग़लत" को "विनाशकारी रूप से आत्मविश्वास से ग़लत" से अलग नहीं कर पाता। Logits के प्रति उसका gradient भी साफ़ है (`softmax_output - one_hot_true_label`), और इसीलिए softmax और cross-entropy लगभग हमेशा साथ जोड़े जाते हैं, अक्सर कच्चे logits पर एक fused, संख्यात्मक रूप से स्थिर operation के रूप में।

**Teacher forcing।** Training हमेशा असली पिछले tokens को context के रूप में देती है, model की अपनी predictions को कभी नहीं। चूँकि causal masking पहले से हर position को सिर्फ़ पीछे की ओर attend करने तक सीमित करती है, हर position की prediction, और इसलिए हर position का loss, प्रति position एक pass की जगह एक ही forward pass में compute होता है। प्रति-position, प्रति-batch losses को औसत करके एक scalar बनाया जाता है, क्योंकि gradient descent को घटाने के लिए एक अकेली मात्रा चाहिए।

## Backward pass और autograd

हर forward operation (matrix multiply, softmax, residual जोड़) एक **computation graph** में दर्ज होता है। `loss.backward()` उस पर उलटी दिशा में चलता है, हर operation के पहले से लागू स्थानीय backward नियम से chain rule अपने-आप लगाते हुए, और हर train हो सकने वाले parameter का `.grad` भरते हुए।

Chain rule का worked example: `y = 3x + 1`, `z = y^2`, `x = 2` पर: `y = 7`, `dz/dy = 2y = 14`, `dy/dx = 3`, इसलिए `dz/dx = 14 x 3 = 42`।

| तरीक़ा | Gradient कैसे पाता है | लागत |
|---|---|---|
| Symbolic differentiation | हाथ से या computer algebra से closed-form सूत्र निकालता है | autograd यह नहीं करता |
| Numerical differentiation | हर parameter को हिलाता है, forward pass दोबारा चलाता है | अशुद्ध, हर parameter के लिए एक अतिरिक्त forward pass |
| Automatic differentiation (autograd) | रिकॉर्ड किए graph पर हर operation का पहले से लागू स्थानीय backward नियम जोड़ता है | सटीक, सभी parameters के लिए एक साथ एक backward traversal |

**Residuals असल में vanishing gradients क्यों रोकते हैं।** `y = x + Sublayer(x)` के लिए, `d(loss)/d(x) = d(loss)/d(y) x 1 + [Sublayer से होकर एक पद]`। Identity path का स्थानीय derivative ठीक 1 है, इसलिए `Sublayer` का अपना derivative कितना भी छोटा हो जाए, सीधा पद बिना scale हुए गुज़रता है। यह यांत्रिक कारण है, सिर्फ़ अंदाज़ा नहीं।

**Gradients accumulate होते हैं, overwrite नहीं।** `.grad` में जो पहले से था उसमें जुड़ता है, इसलिए training loop को हर नए `backward()` call से पहले gradients साफ़ तौर पर शून्य करने होंगे, वरना किसी step का gradient पिछले step के बचे हुए मानों से दूषित हो जाता है।

## AdamW optimizer step

```text
plain gradient descent:  w = w - lr * grad
Adam's moments:           m = beta1 * m + (1 - beta1) * grad          (momentum)
                          v = beta2 * v + (1 - beta2) * grad^2        (adaptive scale)
Adam's update:            w = w - lr * m_hat / (sqrt(v_hat) + eps)
AdamW's update:           w = w - lr * (m_hat / (sqrt(v_hat) + eps) + weight_decay * w)
```

(`m_hat`, `v_hat` वे `m`, `v` हैं जिनमें इस बात के लिए bias correction है कि दोनों शून्य से शुरू होते हैं।)

| हिस्सा | क्या जोड़ता है | क्या ठीक करता है |
|---|---|---|
| Momentum (`m`) | पिछले gradients का चलता औसत | शोर वाले प्रति-batch gradients; update काँपने की जगह एक एकसमान दिशा का अनुसरण करता है |
| Adaptive scale (`v`) | प्रति-parameter सामान्य-gradient-परिमाण का अनुमान | हर weight के लिए एक तय learning rate; छोटे-gradient वाले parameters को अपेक्षाकृत बड़े क़दम मिलते हैं, बड़े-gradient वालों को छोटे |
| Decoupled weight decay (AdamW) | Weight decay सीधे `w` पर लगता है, `m`, `v` या adaptive हर से कभी नहीं गुज़रता | Decay को gradient में मिलाने (मूल Adam) से उसकी असरदार सिकुड़न हर parameter के सामान्य gradient परिमाण पर निर्भर हो जाती है, उस एकसमान सिकुड़न की जगह जो decay को होनी चाहिए |

Worked example: `w = 5.0`, `grad = 2.0`, `lr = 0.1`, सादा gradient descent: `w = 5.0 - 0.1 x 2.0 = 4.8`।

## Training loop के implementation पर भरोसा करने से पहले

- [ ] Cross-entropy कच्चे logits सीधे लेता है (fused softmax + ऋणात्मक-log-probability operation), हाथ से softmax और फिर अलग log चरण नहीं।
- [ ] Training ground-truth पिछले tokens देती है (teacher forcing), और loss हर position के लिए एक ही forward pass में compute होता है, प्रति position एक pass नहीं।
- [ ] हर `backward()` call से पहले gradients साफ़ तौर पर शून्य किए जाते हैं।
- [ ] अगर weight decay इस्तेमाल हो रहा है तो optimizer AdamW है, सादा Adam नहीं, और weight decay सीधे weights पर लगता है, gradient में मिलाया नहीं जाता।

## स्रोत

- [दस्तावेज़: "torch.nn.functional.cross_entropy", PyTorch](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
- [दस्तावेज़: "Autograd mechanics", PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
- [पेपर: "Decoupled Weight Decay Regularization", Loshchilov and Hutter, 2019](https://arxiv.org/abs/1711.05101)
- [पेपर: "Adam: A Method for Stochastic Optimization", Kingma and Ba, 2015](https://arxiv.org/abs/1412.6980)
- [संसाधन](../RESOURCES.md)
