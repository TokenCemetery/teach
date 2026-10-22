---
title: "Transformer Block"
description: "Positional encoding, layer norm और residual connections, feed-forward block, और blocks को embedding, output तथा weight tying के साथ पूरे model में stack करना"
type: reference
---

# Transformer Block: एक Block से पूरे Model तक

चरण 2 और 3, खोजने के लिए संक्षिप्त किए हुए। [पाठ 4](../lessons/0004-positional-encoding.md) embeddings में position डालना कवर करता है; [पाठ 5](../lessons/0005-layer-norm-and-residuals.md) residuals और layer norm कवर करता है; [पाठ 6](../lessons/0006-feed-forward-block.md) feed-forward sublayer कवर करता है; [पाठ 7](../lessons/0007-stacking-blocks.md) blocks को गहराई में stack करना कवर करता है; [पाठ 8](../lessons/0008-embedding-output-and-weight-tying.md) model के vector space में आना-जाना कवर करता है। यह शीट सूत्र, shapes और चुनाव हैं, साथ-साथ।

## Positional encoding

Attention में अपने-आप क्रम की कोई समझ नहीं है; दो positions की अदला-बदली बस output को दोबारा नामित कर देती है। Position को embeddings के भीतर ही, attention चलने से पहले, पिरोना पड़ता है।

```text
PE(pos, 2i)   = sin(pos / 10000^(2i / d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i / d_model))
```

| योजना | न देखी गई sequence lengths पर सामान्यीकृत होती है | Implementation |
|---|---|---|
| Sinusoidal (तय सूत्र) | हाँ, सूत्र किसी भी position पर evaluate होता है | सीखने को कोई parameter नहीं |
| सीखा हुआ position embedding | नहीं, उसमें सिर्फ़ training में देखी गई positions की पंक्तियाँ हैं | एक लुकअप table, किसी भी दूसरे parameter की तरह train की हुई |

## Residual connections और layer norm

```text
post-norm: LayerNorm(x + Sublayer(x))
pre-norm:  x + Sublayer(LayerNorm(x))
```

| हिस्सा | क्या हल करता है | किससे स्वतंत्र |
|---|---|---|
| Residual (`+ x`) | गहरे stack में gradient का सिकुड़ना या फटना, हर layer पर उसे सीधा identity path देकर | Sublayer का अपना रूपांतरण |
| Layer norm | Activation scale का layer-दर-layer बहकना, हर token के अपने feature vector को normalize करके (features पर mean/variance, फिर सीखा हुआ scale और shift) | Batch size, batch norm के उलट, जिसे कई examples के आँकड़े चाहिए |

**Post-norm के ऊपर pre-norm।** Pre-norm residual path को सिरे से सिरे तक पूरी तरह बिना normalize किए रखता है, बेरोक identity connection; post-norm हर layer पर residual योग को normalize करता है और उस path में बाधा डालता है। मूल पेपर के post-norm के चुनाव के बावजूद ज़्यादातर मौजूदा बड़े models pre-norm इस्तेमाल करते हैं।

## Feed-forward block

```text
FFN(x) = max(0, x W1 + b1) W2 + b2
```

| चरण | Input का shape | Output का shape | टिप्पणी |
|---|---|---|---|
| `x W1 + b1`, nonlinearity | `[n, d_model] × [d_model, d_ff]` | `[n, d_ff]` | `d_ff` आम तौर पर `d_model` का 4x (मूल पेपर में 512 से 2048); शुरुआत में ReLU, बाद के architectures में GELU/SwiGLU |
| `... W2 + b2` | `[n, d_ff] × [d_ff, d_model]` | `[n, d_model]` | वापस नीचे project करता है ताकि नतीजा residual stream में जुड़ सके |

हर position पर अलग-अलग, एक ही weights के साथ, एकसमान लगता है, यहाँ कोई position किसी दूसरी position का vector कभी नहीं देखती। यह attention का सटीक पूरक है: attention positions के आर-पार मिलाता है पर अपने weights compute होने के बाद values में linear है; feed-forward block वह जगह है जहाँ किसी एक position की अपनी representation को सचमुच nonlinear नया आकार मिलता है।

## Blocks को stack करना

| गुण | इसका मतलब | क्यों मायने रखता है |
|---|---|---|
| Shape बनाए रखना | हर block `d_model` अंदर लेता है, `d_model` बाहर देता है | Block N का output बिना किसी adapter के block N+1 का input बन जाता है; वही block shape कितनी भी बार stack होता है |
| Weight साझा नहीं | हर block के अपने, स्वतंत्र रूप से सीखे हुए parameters हैं | क़ीमत गहराई के साथ लगभग linearly parameters में; बदले में अलग-अलग blocks अलग-अलग गहराई पर विशेषज्ञ बनते हैं |
| Residual stream | एक चलता हुआ vector हर block से गुज़रता है, हर एक अपना योगदान जोड़ता है | पाठ 5 की residual/layer-norm व्यवस्था ठीक इसी की रक्षा करती है जब गहराई दर्जनों blocks तक पहुँचती है |

## Embedding, output और weight tying

| Layer | Shape | भूमिका |
|---|---|---|
| Input embedding | `vocab_size × d_model` | पंक्ति `i` token `i` का सीखा हुआ vector है; उसे ढूँढना लुकअप है, computed रूपांतरण नहीं |
| Output projection | `d_model × vocab_size` | हर position पर हर vocabulary token के लिए एक logit बनाता है |

दोनों shapes एक-दूसरे के transpose हैं। **Weight tying** दूसरा matrix सीखने की जगह embedding matrix को transpose करके output projection के रूप में दोबारा इस्तेमाल करता है (`logits = h @ W_embedding^T`), इस तर्क पर कि दोनों layers किसी token को एक ही बुनियादी representation से जोड़ती हैं।

Worked example: vocabulary 50,000, `d_model = 768`। Embedding table: `50,000 × 768 = 38,400,000` parameters। बिना tying वाली output layer को उसी आकार का दूसरा matrix चाहिए; tying उसे हटा देता है, यहाँ लगभग 38.4 million parameters बचाता है, गुणवत्ता के किसी नुक़सान के बिना, और अक्सर नापने लायक़ फ़ायदे के साथ।

## पूरे model के implementation पर भरोसा करने से पहले

- [ ] Positional encoding पहले block से पहले token embeddings में जोड़ा गया है, attention में किसी और तरीक़े से नहीं डाला गया।
- [ ] हर sublayer residual connection में लिपटी है, और layer norm की जगह (pre- या post-) सोचा-समझा चुनाव है, जो भी कोई tutorial इस्तेमाल करता था वह नहीं।
- [ ] Feed-forward block की दोनों layers फैलती फिर सिकुड़ती हैं (`d_model` से `d_ff` से `d_model`), और उसकी weights positions के बीच कभी साझा नहीं होतीं।
- [ ] Stack का हर block `d_model` लेता और लौटाता है, और हर एक की अपनी स्वतंत्र रूप से सीखी हुई weights हैं।
- [ ] अगर weight tying इस्तेमाल हुई है, तो output projection embedding matrix का transpose है, दूसरा सीखा हुआ matrix नहीं।

## स्रोत

- [पेपर: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [पेपर: "Layer Normalization", Ba, Kiros, and Hinton, 2016](https://arxiv.org/abs/1607.06450)
- [पेपर: "On Layer Normalization in the Transformer Architecture", Xiong et al., 2020](https://arxiv.org/abs/2002.04745)
- [पेपर: "Using the Output Embedding to Improve Language Models", Press and Wolf, 2017](https://arxiv.org/abs/1608.05859)
- [संसाधन](../RESOURCES.md)
