---
title: "Attention"
description: "Scaled dot-product attention, multi-head attention और causal masking, हर चरण पर tensor shapes के नोट के साथ"
type: reference
---

# Attention: Scaled Dot-Product, Multi-Head और Causal Masking

चरण 1, खोजने के लिए संक्षिप्त किया हुआ। [पाठ 1](../lessons/0001-scaled-dot-product-attention.md) बुनियादी समीकरण कवर करता है; [पाठ 2](../lessons/0002-multi-head-attention.md) उसे parallel subspaces में चलाना कवर करता है; [पाठ 3](../lessons/0003-causal-masking.md) उसे सिर्फ़ अतीत तक सीमित करना कवर करता है। यह शीट समीकरण और shapes हैं, साथ-साथ।

## Scaled dot-product attention

```text
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

| चरण | Input का shape | Output का shape | टिप्पणी |
|---|---|---|---|
| `Q`, `K`, `V` दिए हुए | n/a | `[n, d_k]`, `[m, d_k]`, `[m, d_v]` | `n` queries, `m` key/value जोड़ियाँ; `d_k` key/query का आयाम है |
| `QK^T` | `[n, d_k] × [d_k, m]` | `[n, m]` | हर query-key जोड़ी के लिए एक similarity score |
| `/ sqrt(d_k)` | `[n, m]` | `[n, m]` | `d_k` के साथ variance की बढ़त काटता है, softmax के gradient को काम का रखता है |
| `softmax(...)` (पंक्ति-दर-पंक्ति) | `[n, m]` | `[n, m]` | हर पंक्ति अब probability distribution है जिसका योग 1 है |
| `× V` | `[n, m] × [m, d_v]` | `[n, d_v]` | हर query के लिए एक output vector, values का भारित मिश्रण |

Self-attention वह मामला है जहाँ `Q`, `K`, `V` तीनों एक ही sequence से आते हैं (`n = m`), हर position ख़ुद समेत हर position पर attend करती है।

**Scaling क्यों।** Dot-product का variance `d_k` के साथ बढ़ता है, जो softmax को लगभग one-hot output की ओर धकेलता है जहाँ उसका gradient लगभग सपाट होता है और training अटक जाती है। `/ sqrt(d_k)` उस बढ़त को काटता है, चाहे `d_k` कितना भी बड़ा हो।

## Multi-head attention

```text
Q_i = X W_Q^i,   K_i = X W_K^i,   V_i = X W_V^i          (per head i, i = 1..h)
head_i = Attention(Q_i, K_i, V_i)
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) W_O
```

| चरण | Input का shape | Output का shape | टिप्पणी |
|---|---|---|---|
| Input `X` | n/a | `[n, d_model]` | |
| प्रति-head projection (`W_Q^i`, `W_K^i`, `W_V^i`) | `[n, d_model] × [d_model, d_k]` | हर head के लिए `[n, d_k]`, `d_k = d_model / h` | हर head के projections स्वतंत्र रूप से सीखे जाते हैं |
| `head_i = Attention(Q_i, K_i, V_i)` | हर एक `[n, d_k]` | `[n, d_k]` | ऊपर वाला ही समीकरण, हर head के लिए एक बार चलाया हुआ |
| `Concat(head_1, ..., head_h)` | `h × [n, d_k]` | `[n, d_model]` | heads को अगल-बगल रखता है, heads के बीच अभी कोई आपसी क्रिया नहीं |
| `× W_O` | `[n, d_model] × [d_model, d_model]` | `[n, d_model]` | अकेला चरण जो अलग-अलग heads की जानकारी को मिलने देता है |

**Scaling सूत्र प्रति-head `d_k` इस्तेमाल करता है, `d_model` नहीं।** हर head के dot products उसके अपने, छोटे आयाम पर जोड़े जाते हैं, इसलिए scaling को उसी variance को काटना है, चाहे पूरा model कितना भी बड़ा हो।

**`W_O` वैकल्पिक नहीं है।** अकेला concatenation outputs को अगल-बगल रखता है, बिना किसी आपसी क्रिया के; `W_O` अकेली जगह है जहाँ अलग-अलग heads की जानकारी एक representation में मिल सकती है।

## Causal masking

कच्चे scores में, softmax से पहले जोड़ी जाती है:

```text
scores = QK^T / sqrt(d_k)
scores[i, j] += -inf   for every j > i     (a fixed lower-triangular pattern)
Attention(Q, K, V) = softmax(scores) V
```

| चुनाव | क्यों |
|---|---|
| Softmax के बाद नहीं, पहले mask करें | Softmax चल चुकने के बाद किसी weight को शून्य करने से बाक़ी weights का योग 1 से कम रह जाता है, जो वैध distribution नहीं है। Score को mask करने से दोबारा normalization उसी softmax के भीतर अपने-आप हो जाता है |
| `0` नहीं, बड़ी ऋणात्मक संख्या | `exp(0) = 1`, एक सामान्य, नज़रअंदाज़ न होने वाला मान जो अब भी probability mass के लिए होड़ करता है। सिर्फ़ काफ़ी बड़ी ऋणात्मक संख्या ही `exp(...)` को असरदार रूप से शून्य तक ले जाती है |
| हर head और batch के हर example के लिए वही mask | पाबंदी (query position `i` key positions `0..i` पर attend कर सकती है) task का गुण है, किसी एक head का नहीं |

Inference में model token `N` सिर्फ़ tokens `1..N-1` से generate करता है; training के दौरान position `i` को बाद की position `j` पर attend करने देना model को ऐसा उत्तर इस्तेमाल करने देता है जो generation के समय उसके पास कभी नहीं होगा। उस मामले में training loss अच्छा दिखता है, पर model कुछ हस्तांतरणीय नहीं सीखता।

## Attention implementation पर भरोसा करने से पहले

- [ ] Scaling का भाजक प्रति-head `d_k` (`d_model / h`) है, पूरा `d_model` नहीं।
- [ ] `W_O` heads को concatenate करने के बाद लगाया गया है, छोड़ा नहीं गया।
- [ ] Causal mask कच्चे scores में softmax से पहले जोड़ा गया है, बाद में weights पर नहीं लगाया गया।
- [ ] Mask का मान बड़ी ऋणात्मक संख्या (या `-inf`) है, `0` नहीं।
- [ ] Output का shape heads की संख्या से स्वतंत्र `[n, d_model]` है, क्योंकि heads सिर्फ़ बीच का प्रति-head आयाम बदलते हैं।

## स्रोत

- [पेपर: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [लेख: "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
- [लेख: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [संसाधन](../RESOURCES.md)
