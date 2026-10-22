---
title: "असली Code से मैपिंग"
description: "हर निकाला हुआ हिस्सा transformers या llama.cpp में कहाँ रहता है, मूल पेपर से तीन मानक अंतर, byte-pair encoding, और low-rank adapter कहाँ जुड़ता है"
type: reference
---

# असली Code से मैपिंग

चरण 5, खोजने के लिए संक्षिप्त किया हुआ। [पाठ 12](../lessons/0012-reading-real-model-code.md) इस workspace की derivations को Hugging Face `transformers` और llama.cpp के नामकरण में अनुवाद करना कवर करता है; [पाठ 13](../lessons/0013-tokenizers-and-low-rank-adapters.md) byte-pair encoding निकालना और यह कवर करता है कि low-rank adapter किसी weight matrix पर कहाँ जुड़ता है। यह शीट नाम-मैपिंग, मानक अंतर और दो derivations हैं, साथ-साथ।

## Hugging Face `transformers` में नामकरण

| असली-code का नाम | कहाँ निकाला गया | यह क्या है |
|---|---|---|
| `GPT2Attention` (या मिलता-जुलता) | पाठ 1-2 | Scaled dot-product attention, अक्सर एक fused QKV linear layer से जो बाद में अलग की जाती है, यह batched-matmul की कुशलता का ब्योरा है, कोई अलग operation नहीं |
| Registered lower-triangular mask buffer | पाठ 3 | Causal masking, एक बार पहले से compute किया हुआ क्योंकि mask सिर्फ़ sequence length पर निर्भर करता है, input मानों पर नहीं, और हर call पर दोबारा इस्तेमाल या slice होता है |
| `wte` (word token embedding) | पाठ 8 | Input embedding table |
| `wpe` (word position embedding) | पाठ 4 | Positional encoding, यहाँ आम तौर पर sinusoidal सूत्र की जगह सीखी हुई table |
| Blocks का `ModuleList`, for loop में दोहराया जाता | पाठ 7 | Stack किए transformer blocks |
| `lm_head`, `wte` की weights से tie की हुई | पाठ 8 | Output projection, weight tying के ज़रिए |
| Training script या `Trainer`, model class नहीं | पाठ 9-11 | Cross-entropy loss, `.backward()`, optimizer step; model class सिर्फ़ logits तक का forward pass तय करती है |

## मूल पेपर से तीन मानक अंतर

| हिस्सा | मूल पेपर | Production models में आम | फिर भी वही बुनियादी पाठ |
|---|---|---|---|
| Position embedding | Sinusoidal सूत्र | सीखी हुई table, या rotary embeddings | पाठ 4 का सीखा हुआ विकल्प, या आगे का variant |
| Activation function | ReLU | GELU (या SwiGLU) | पाठ 6 का फैलाने-फिर-समेटने वाला आकार, अलग nonlinearity |
| Norm की जगह | Post-norm | Pre-norm | पाठ 5 का pre-norm विकल्प |

इनमें से कोई भी उस architecture को नहीं बदलता जो इस workspace ने निकाला; ये मानक भिन्नताएँ हैं जो लगभग हर असली implementation में मिलती हैं, अलग design नहीं।

## वही गणित, अलग codebase: llama.cpp

llama.cpp (C, `ggml` tensor library के ज़रिए) `forward` method वाली `nn.Module` classes की जगह function calls से साफ़ computation graph बनाता है। वह वही गणितीय वस्तुएँ compute करता है: attention, positional encoding (आम तौर पर rotary), normalization (आम तौर पर RMSNorm, layer norm का सरल variant), और feed-forward block (आम तौर पर SwiGLU)। फ़र्क़ पूरी तरह इसमें है कि computation graph कैसे बनता और चलता है, इसमें नहीं कि वह क्या compute करता है।

## Tokenizer को निकालना: byte-pair encoding (BPE)

1. Training text को कच्चे bytes या अक्षरों की sequence के रूप में दर्शाएँ, हर एक अपनी vocabulary प्रविष्टि।
2. Corpus में पास-पास के symbols की हर जोड़ी गिनें।
3. सबसे आम अकेली जोड़ी को एक नए symbol में मिलाएँ, जो vocabulary में जुड़ जाए।
4. तब तक दोहराएँ जब तक vocabulary चुने हुए लक्ष्य आकार तक न पहुँच जाए।

Worked example, corpus `"low low lower"`: जोड़ी `l, o` आम है और `lo` में मिल जाती है; अगला दौर `lo, w` ढूँढता है और `low` में मिला देता है। आम शब्द एक अकेले token की ओर सिमटते हैं; दुर्लभ शब्द छोटे, ज़्यादा आम टुकड़ों में टूट जाते हैं।

`vocab_size` उतनी ही है जितने शुरुआती symbols और मिलाने वाले चरण tokenizer की training ने चलाए, और training पूरी होते ही तय हो जाती है; यही पाठ 8 की input embedding table और output layer का आकार तय करती है।

## Low-rank adapter कहाँ जुड़ता है

`llm/finetuning` का adapter तंत्र, `ΔW = BA`, जिसमें `A` rank `r` तक नीचे project करता है और `B` वापस ऊपर, इस workspace में निकाले एक ठोस weight matrix पर जुड़ता है, उदाहरण के लिए पाठ 2 का प्रति-head query projection:

```text
Q_i = X (W_Q^i + (alpha / r) B_i A_i)
```

| Matrix | Frozen? | क्या adapter training में gradients मिलते हैं? |
|---|---|---|
| `W_Q^i` | हाँ, ठीक वैसा जैसा pretrained | नहीं |
| `A_i`, `B_i` | नहीं, नए जोड़े गए, rank `r` से आकार तय | हाँ |

चूँकि update जोड़ने वाला और linear है, ठीक वैसे ही जैसे मूल projection है, `W_Q^i + (alpha/r) B_i A_i` training के बाद एक सामान्य matrix में सिमट जाता है। Merged नतीजे को परोसने के लिए forward pass में कुछ भी नहीं बदलता, क्योंकि वह `Q_i = X W_Q^i` में सामान्य projection matrix की तरह बैठ जाता है, inference में शून्य अतिरिक्त computation के साथ।

## किसी असली model के code को पढ़ने या उस पर कुछ जोड़ने से पहले

- [ ] अलग की जाने वाली fused QKV linear layer को कुशलता का ब्योरा माना जाता है, प्रति-head projections से अलग operation नहीं।
- [ ] Mask buffer, अगर पहले से compute किया हुआ है, तो समझा गया है कि वह सिर्फ़ sequence length पर निर्भर करता है, और masking का तंत्र ख़ुद नहीं बदलता।
- [ ] Position embedding, activation और norm की जगह के चुनावों को अलग architecture मानने से पहले तीन मानक अंतरों से मिलाकर जाँचा गया है।
- [ ] Low-rank adapter के जुड़ने की जगह को किसी ख़ास weight matrix के रूप में नाम दिया गया है (किस layer का कौन-सा projection), सिर्फ़ "model" नहीं।

## स्रोत

- [Repo: transformers, Hugging Face](https://github.com/huggingface/transformers)
- [Repo: nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
- [पेपर: "Neural Machine Translation of Rare Words with Subword Units", Sennrich, Haddow, and Birch, 2016](https://arxiv.org/abs/1508.07909)
- [Adapter](../../finetuning/GLOSSARY.md): `llm/finetuning` का मानक शब्द frozen-base-और-छोटी-trainable-weights वाले pattern के लिए
- [संसाधन](../RESOURCES.md)
