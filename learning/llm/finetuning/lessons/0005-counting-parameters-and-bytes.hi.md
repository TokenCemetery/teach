---
title: "5. Parameters और Bytes गिनना"
description: "Model config को gigabytes में बदलना"
type: lesson
---

# पाठ 5. Parameters और Bytes गिनना

**मिशन से संबंध:** "हर byte का हिसाब दें" मिशन में है। यही वह पाठ है जहाँ आप अंदाज़ा लगाने के बजाय अंकगणित करना सीखते हैं।
**मुख्य स्रोत:** [दस्तावेज़: Model memory anatomy, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/model_memory_anatomy)
**पूर्व-आवश्यकताएँ:** [पाठ 2](0002-where-the-weights-live.md), [पाठ 4](0004-what-training-changes.md)

## वार्म-अप

1. ▢ एक training step के चार ऑपरेशन क्या हैं?

<details markdown="1"><summary>जाँचें</summary>

Forward pass (activations रखते हुए), loss, backward pass (gradients बनाते हुए), optimizer step।

</details>

2. ▢ Labels tensor में `-100` का क्या मतलब है?

<details markdown="1"><summary>जाँचें</summary>

Loss compute करते समय इस position को अनदेखा करें। Completion-only loss के लिए prompt tokens इसी तरह mask किए जाते हैं।

</details>

3. ▢ Grouped-query attention में कौन-से attention projections सिकुड़ते हैं?

<details markdown="1"><summary>जाँचें</summary>

`k_proj` और `v_proj`। `q_proj` और `o_proj` पूरा hidden आयाम रखते हैं।

</details>

## यह जानें

Parameter एक संख्या है। Memory उस संख्या के storage आकार गुना आपके पास ऐसी कितनी संख्याएँ हैं। चरण 2 में बाक़ी सब कुछ इसके ऊपर का हिसाब-किताब है।

### संख्यात्मक formats

| Format | Bytes | टिप्पणी |
|---|---|---|
| `float32` (fp32) | 4 | पूरी precision। Training के लिए ऐतिहासिक default। |
| `bfloat16` (bf16) | 2 | fp32 जैसी ही exponent सीमा, कम mantissa bits। आधुनिक default। |
| `float16` (fp16) | 2 | ज़्यादा mantissa, बहुत छोटी सीमा, इसलिए infinity तक ज़्यादा आसानी से overflow होता है। |
| `int8` | 1 | Integer, समझने के लिए scale factor चाहिए। |
| 4-bit (`nf4`, `int4`) | 0.5 | प्रति byte दो values, साथ में प्रति-block scales। चरण 4। |

Training के लिए bf16 को fp16 से बेहतर माना जाता है, भले ही वह कम precision store करता है, क्योंकि उसकी exponent सीमा fp32 से मेल खाती है। Overflow से उबरना rounding error से कठिन विफलता है, और fp16 training को इससे बचने के लिए ऐतिहासिक रूप से loss scaling चाहिए थी।

### Model का वर्णन करने वाली दो संख्याएँ

मान लें model card 1.5B parameters का दावा करता है। तब:

```text
weights in fp32 = 1.5e9 × 4 bytes = 6.0 GB
weights in bf16 = 1.5e9 × 2 bytes = 3.0 GB
weights in nf4  = 1.5e9 × 0.5     = 0.75 GB, plus quantisation constants
```

यह सिर्फ़ inference-weight की memory है: model को memory में रखने भर का न्यूनतम, किसी भी activations और KV cache से पहले, और training से तो बिल्कुल पहले।

एक काम का सहज नियम: **bf16 gigabytes ≈ अरबों में parameter गिनती का दोगुना।** 7B model लगभग 14 GB weights है। 70B model लगभग 140 GB है। आपको ये तुरंत निकालने आने चाहिए।

### Parameters कहाँ हैं

पाठ 2 से, प्रति layer:

```text
attention = 2 × d² + 2 × d × d_kv          (q, o full; k, v narrowed by GQA)
mlp       = 3 × d × d_ff                    (gate, up, down)
```

और पूरे model में:

```text
total ≈ n_layers × (attention + mlp) + vocab × d × (1 or 2)
```

जब output projection input embedding से untied हो तो आख़िरी पद दोगुना हो जाता है। छोटे models के लिए यह पद नगण्य नहीं है: hidden size 2048 के साथ 32k vocabulary हर copy में 65M parameters है, जो 1.5B model का असली अंश है।

### काम किया हुआ उदाहरण

ऐसा model जिसमें `d = 2048`, `d_kv = 256`, `d_ff = 5632`, 24 layers, 32k vocabulary, tied embeddings हैं:

```text
attention = 2 × 2048² + 2 × 2048 × 256  = 8.39M + 1.05M = 9.44M
mlp       = 3 × 2048 × 5632             = 34.6M
per layer                               = 44.0M
× 24 layers                             = 1.056B
embeddings = 32000 × 2048               = 0.066B
total                                   ≈ 1.12B
```

bf16 में यह लगभग 2.2 GB weights है। ध्यान दें कि MLP block का 79% है; इसे पाठ 10 तक साथ ले चलें।

![अनुपात की दो पट्टियाँ। 44.0M की एक layer लगभग 21 प्रतिशत attention और 79 प्रतिशत MLP है। 1.12B का पूरा model लगभग 94 प्रतिशत stacked layers और 5.9 प्रतिशत embeddings है।](images/where-the-parameters-are.svg)

वही जोड़-घटाव हिस्सों के रूप में, उन दो स्तरों पर जो मायने रखते हैं। एक block के भीतर attention काफ़ी अंतर से छोटा आधा है, इसीलिए पाठ 10 का target-module वाला सवाल ज़्यादातर MLP के बारे में सवाल है। पूरे model में, embedding वाला पद यहाँ छोटा है और model के छोटा होने पर हिस्से के रूप में बढ़ता जाता है, यही वह मामला है जिसके बारे में ऊपर का अनुच्छेद चेता रहा है।

### इसमें अभी क्या शामिल नहीं है

अब आपके पास weight की लागत है। Training तीन और श्रेणियाँ जोड़ती है, और वही हावी रहती हैं:

- Gradients, हर trainable parameter के लिए एक (पाठ 6)
- Optimizer state, हर trainable parameter के लिए दो (पाठ 6)
- Activations, जो parameter की गिनती पर नहीं बल्कि batch size और sequence length पर निर्भर हैं (पाठ 7)

जो कोई कहे कि 7B model को fine-tune करने के लिए "14 GB चाहिए", उसने सिर्फ़ पहली श्रेणी गिनी है। यही वह भूल है जिसे मिटाने के लिए यह चरण है।

## अभ्यास

1. ▢ 13B model के weights bf16 में कितने gigabytes हैं? fp32 में? 4-bit में?

<details markdown="1"><summary>जाँचें</summary>

bf16: 26 GB। fp32: 52 GB। 4-bit: लगभग 6.5 GB, साथ में quantisation constants।

Parameter की गिनती से दोगुना-आधा करने की यह कड़ी calculator के बिना कर पाना सार्थक है।

</details>

2. ▢ Training के लिए bf16 को fp16 से बेहतर क्यों माना जाता है, जबकि fp16 ज़्यादा mantissa bits store करता है?

<details markdown="1"><summary>जाँचें</summary>

bf16 fp32 की exponent सीमा रखता है, इसलिए values infinity तक overflow नहीं होतीं। fp16 की संकरी सीमा का मतलब है कि gradients overflow या underflow हो सकते हैं, और काम करने के लिए ही ऐतिहासिक रूप से loss scaling चाहिए थी।

Rounding error धीरे-धीरे बिगाड़ता है; overflow `NaN` बनाकर run ख़त्म कर देता है। सौदा सीमा के पक्ष में है।

</details>

3. ▢ किसी model में `d = 4096`, `d_ff = 14336`, `d_kv = 1024`, 32 layers हैं। Embeddings को छोड़कर प्रति-layer parameters और model का कुल निकालें।

<details markdown="1"><summary>जाँचें</summary>

Attention: 2 × 4096² + 2 × 4096 × 1024 = 33.6M + 8.4M = 42.0M।
MLP: 3 × 4096 × 14336 = 176.2M।
प्रति layer: 218.2M। गुणा 32 layers ≈ 6.98B।

लगभग 7B model, और उसका 81% MLP है।

</details>

4. ▢ दो models दोनों 7B parameters बताते हैं। एक की vocabulary 32k है, दूसरे की 256k। क्या अलग है, और कितना?

<details markdown="1"><summary>जाँचें</summary>

Embedding की लागत। Hidden size 4096 के साथ, 32k vocabulary हर copy में 131M parameters है; 256k vocabulary 1.05B है, एक ही table में पूरे model का लगभग 15%, और output projection untied हो तो उसका दोगुना।

इसलिए बड़ी vocabulary वाले model के transformer blocks में, जहाँ adapters जुड़ते हैं, उल्लेखनीय रूप से कम parameters होते हैं।

</details>

5. ▢ कोई कहता है कि 7B model fine-tuning के लिए 16 GB में आराम से समा जाता है, क्योंकि bf16 weights 14 GB हैं। इस तर्क में क्या ग़लत है?

<details markdown="1"><summary>जाँचें</summary>

उन्होंने सिर्फ़ weights गिने हैं। Full fine-tuning को प्रति trainable parameter gradients और दो optimizer moments भी चाहिए, साथ में activations, जो weights की लागत का कई गुना है। 14 GB का दावा भी बाक़ी सब कुछ के लिए सिर्फ़ 2 GB छोड़ता है।

अगला पाठ इसे एक सटीक संख्या में बदलता है, और जवाब क़रीब भी नहीं है।

</details>

## असली दुनिया का अभ्यास

- [ ] अलग-अलग आकार के तीन models चुनें। सिर्फ़ उनकी config files (`hidden_size`, `intermediate_size`, `num_hidden_layers`, `num_key_value_heads`, `vocab_size`) से parameter की गिनतियाँ निकालें और उन्हें model cards से मिलाकर जाँचें।
- [ ] एक model को bf16 में load करें और असल में इस्तेमाल हुई memory मापें। अपने अनुमान से तुलना करें और किसी भी फ़ासले को समझाएँ।
- [ ] कल: पाँच model आकारों के लिए bf16-gigabytes का अनुमान मन में लगाएँ, फिर calculator से जाँचें।

## आगे बढ़ने के लिए

- [दस्तावेज़: Model memory anatomy, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/model_memory_anatomy)
- [memory budget शीट](../reference/memory-budget.md): वह table जिस तक यह पाठ पहुँचता है
- [पाठ 6. Gradients और Optimizer State](0006-gradients-and-optimizer-state.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
