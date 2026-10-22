---
title: "12. असली Model Code पढ़ना"
description: "हर निकाला हुआ हिस्सा production model library में कहाँ रहता है, और मूल पेपर से वे छोटे, आम अंतर जिन्हें उलझने के बजाय पहचानना ज़रूरी है"
type: lesson
---

# पाठ 12. असली Model Code पढ़ना

**मिशन से संबंध:** चरण 5 आख़िरी पड़ाव है: चरण 1 से 4 में raw tensors से जो कुछ निकाला गया वह असली, production code के अंदर मौजूद है, अलग नामों के साथ और मूल पेपर से मुट्ठी भर छोटे, मानक अंतरों के साथ, और यह पाठ सिखाता है कि यहाँ जो बनाया गया और व्यवहार में जो असल में चल रहा है, उनके बीच अनुवाद कैसे करें।
**मुख्य स्रोत:** [Repo: transformers, Hugging Face](https://github.com/huggingface/transformers)
**पूर्व-आवश्यकताएँ:** [पाठ 11](0011-adamw-optimizer.md), [Scaled dot-product attention](../GLOSSARY.md)

## वार्म-अप

1. ▢ मूल Adam में weight decay को gradient में मिला देने में क्या गड़बड़ होती है, और AdamW अलग क्या करता है?

<details markdown="1"><summary>जाँचें</summary>

Gradient में मिला दिए जाने पर weight decay बाक़ी सब के साथ adaptive scaling पद से भाग खाता है, इसलिए उसकी असरदार सिकुड़न एकसमान लगने के बजाय parameter के हिसाब से बदलती है। AdamW weight decay को सीधे weights पर लगाता है, gradient-आधारित पद से अलग update में जोड़कर।

</details>

2. ▢ क्या एक transformer block की weights stack के दूसरे block की weights जैसी ही होती हैं? इसकी क्या क़ीमत है और यह क्या देता है?

<details markdown="1"><summary>जाँचें</summary>

नहीं, हर block के अपने स्वतंत्र रूप से सीखे हुए parameters होते हैं, जिनकी क़ीमत गहराई के साथ लगभग linearly parameter count है, पर यह अलग-अलग blocks को अलग-अलग तरह से विशेषज्ञ बनने देता है, बजाय इसके कि हर गहराई पर वे एक ही रूपांतरण compute करने को मजबूर हों।

</details>

## यह जानें

### वही हिस्से, अलग नामों के साथ

Hugging Face की `transformers` library में GPT-2-शैली का model वह सब कुछ लागू करता है जो इस workspace ने निकाला, बस अपनी नामकरण परंपराओं में। Attention `GPT2Attention` जैसी class में रहता है, और पाठ 1 वाला वही scaled dot-product operation compute करता है, अक्सर एक fused linear layer से जो Q, K और V को साथ जोड़कर बनाती है और फिर अलग करती है, यह batched-matmul की कुशलता का ब्योरा है, पाठ 2 के अलग-अलग प्रति-head projections से अलग कोई operation नहीं। Causal masking (पाठ 3) एक पहले से compute किए, registered buffer के रूप में दिखती है जिसमें lower-triangular mask रखा होता है, और वह softmax से पहले attention scores पर ठीक वैसे ही लगता है जैसा निकाला गया था, हर forward call पर शुरू से दोबारा बनने के बजाय: चूँकि mask सिर्फ़ sequence length पर निर्भर करता है, असली input मानों पर नहीं, उसे एक बार compute करके दोबारा इस्तेमाल करना (या slice करना) बस कुशलता का चुनाव है और तंत्र ख़ुद नहीं बदलता। Token और position embeddings `wte` (word token embedding) और `wpe` (word position embedding) tables के रूप में दिखते हैं (पाठ 4 और 8); stack किए blocks एक `ModuleList` में रहते हैं जिस पर model की forward method में for loop चलता है, जो सीधे पाठ 7 से मेल खाता है; और output projection एक linear layer है, जिसे आम तौर पर `lm_head` कहते हैं, और जिसे साफ़ assignment या `tie_weights()` call से `wte` की weights से tie किया जाता है, ठीक पाठ 8 की weight tying।

![दो स्तंभों वाली मैपिंग। बाईं ओर, इस workspace में निकाले गए पाँच हिस्से: पाठ 1 और 2 का attention, पाठ 3 का causal mask, पाठ 4 का positional encoding, पाठ 7 के stack किए blocks, और पाठ 8 की embedding और weight tying। दाईं ओर, Hugging Face की transformers library में हर एक का संबंधित नाम: fused query-key-value projection वाला GPT2Attention, एक registered lower-triangular buffer, सीखी हुई wpe position table, for loop में दोहराया जाता blocks का ModuleList, और lm_head से tie की हुई wte। एक रेखा हर बाएँ वाली अवधारणा को उसके दाएँ वाले असली-code नाम से जोड़ती है।](images/workspace-to-real-code-mapping.svg)

### मूल पेपर से तीन छोटे, मानक अंतर

लगभग हर आधुनिक production model मूल पेपर से इन्हीं कुछ छोटे तरीक़ों से अलग होता है, और इन्हें कुछ नया मानने की जगह पहले कवर हो चुकी अवधारणाओं के implementations के रूप में पहचानना ही इस पाठ का मक़सद है। **Position embedding**: कई models मूल पेपर के sinusoidal सूत्र की जगह सीखी हुई position table (पाठ 4 का sinusoidal encoding का विकल्प) या rotary embeddings इस्तेमाल करते हैं। **Activation function**: feed-forward block (पाठ 6) में आम तौर पर मूल पेपर के ReLU की जगह GELU होता है, वही फैलाने-फिर-समेटने वाला आकार, अलग nonlinearity। **Norm की जगह**: ज़्यादातर मौजूदा models pre-norm (पाठ 5 का विकल्प) इस्तेमाल करते हैं, यानी layer norm को हर sublayer से पहले residual शाखा के भीतर रखते हैं, मूल पेपर के post-norm की जगह। इनमें से कोई भी उस बुनियादी architecture को नहीं बदलता जो इस workspace ने निकाला; ये वही मानक भिन्नताएँ हैं जो लगभग हर असली implementation में मिलती हैं।

### Training code model class के बाहर रहता है

चरण 4 के हिस्से, cross-entropy loss की call, `loss.backward()`, और optimizer step, model की अपनी class का हिस्सा बिल्कुल नहीं हैं; वे training script या किसी training utility में रहते हैं (जैसे Hugging Face का `Trainer`, या nanoGPT जैसा कोई custom loop)। Model class वह forward pass तय करती है जो logits बनाता है; उन logits को train किए हुए model में बदलने का सारा काम एक परत ऊपर रहता है, उस code में जो model को बार-बार बुलाता है और उसके चारों ओर चरण 4 की व्यवस्था लगाता है।

### अलग codebase, वही गणितीय वस्तुएँ

llama.cpp, जो Python और PyTorch की जगह C में बना है, वही operations व्यक्त करता है, attention, positional encoding (आम तौर पर rotary), normalization (आम तौर पर RMSNorm, पाठ 5 के layer norm का सरल variant), और feed-forward block (आम तौर पर SwiGLU activation के साथ), `forward` method वाली `nn.Module` classes के रूप में नहीं, बल्कि `ggml`, यानी उसके नीचे की tensor library, में computation graph बनाने वाली साफ़ calls के रूप में। Graph बनाने वाली calls और class-और-forward-method की शैली पन्ने पर एक-दूसरे जैसी बिल्कुल नहीं दिखतीं, पर वे ठीक वही गणितीय वस्तुएँ compute करती हैं जो इस workspace ने raw tensors से निकालीं; फ़र्क़ पूरी तरह इसमें है कि computation graph कैसे बनता और चलता है, इसमें नहीं कि वह क्या compute करता है।

## अभ्यास

1. ▢ इन असली-code नामों में से हर एक को उस पाठ से मिलाएँ जिसने वह अवधारणा निकाली जिसे वह लागू करता है: `wte`, `wpe`, registered lower-triangular mask buffer, `wte` की weights से tie की गई `lm_head`, blocks का `ModuleList`।

<details markdown="1"><summary>जाँचें</summary>

`wte` (word token embedding): पाठ 8 का input embedding। `wpe` (word position embedding): पाठ 4 का positional encoding (यहाँ sinusoidal की जगह सीखी हुई table)। Registered mask buffer: पाठ 3 की causal masking। `wte` से tie की हुई `lm_head`: पाठ 8 की weight tying। Blocks का `ModuleList`: पाठ 7 की stacking।

</details>

2. ▢ ज़्यादातर आधुनिक असली implementations में मिलने वाले मूल पेपर से तीन आम छोटे अंतर बताएँ, और यह भी कि हर एक किस पाठ के विकल्प से मेल खाता है।

<details markdown="1"><summary>जाँचें</summary>

Sinusoidal की जगह सीखे हुए या rotary position embeddings (पाठ 4 का सीखा हुआ विकल्प, या rotary जैसा आगे का variant)। Feed-forward block में ReLU की जगह GELU (पाठ 6 की nonlinearity, अलग function से बदली हुई, वही फैलाने-फिर-समेटने वाला आकार)। Post-norm की जगह pre-norm (पाठ 5 का pre-norm विकल्प, मूल पेपर के चुनाव के बदले)।

</details>

3. ▢ Causal mask असली code में पहले से compute किए, registered buffer के रूप में क्यों दिखता है, हर forward call पर दोबारा बनने के बजाय?

<details markdown="1"><summary>संकेत</summary>

सोचें कि mask असल में किस पर निर्भर करता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

Mask सिर्फ़ sequence length पर निर्भर करता है, असली input मानों पर कभी नहीं, इसलिए उसे एक बार compute किया जा सकता है (आम तौर पर model जिस अधिकतम sequence length को सपोर्ट करता है उस पर) और हर forward call पर दोबारा इस्तेमाल या slice किया जा सकता है, हर बार शुरू से बनाने के बजाय। यह बस कुशलता का चुनाव है; masking का तंत्र ख़ुद, यानी softmax से पहले scores में जोड़ना, पाठ 3 से बिना बदले वही है।

</details>

4. ▢ llama.cpp का attention और feed-forward block compute करने का तरीक़ा PyTorch के `nn.Module` के forward pass से यांत्रिक रूप से कैसे अलग है, जबकि वह बुनियादी गणितीय operations वही compute करता है?

<details markdown="1"><summary>जाँचें</summary>

llama.cpp C में function calls के ज़रिए `ggml` में साफ़ computation graph बनाता है, `forward` method वाली class परिभाषित करने के बजाय, जिसे PyTorch चलते समय अपने-आप trace करता है। Graph बनाने की शैली पन्ने पर बिल्कुल अलग दिखती है, पर जो operations वह बनाती है, attention, positional encoding, normalization, feed-forward block, वही गणितीय वस्तुएँ हैं जो इस workspace ने raw tensors से निकालीं।

</details>

5. ▢ Architecture को शुरू से निकालने के बाद किसी असली model का code पढ़ने के बारे में कौन-सा दावा सही है?

    - a) असली production models उससे बिल्कुल अलग architecture लागू करते हैं जो मूल पेपर और यह workspace निकालते हैं
    - b) वही हिस्से अलग नामों से दिखते हैं, मुट्ठी भर छोटे, मानक अंतरों (position embedding योजना, activation function, norm की जगह) के साथ जिन्हें नया मानने की जगह पहचानना ज़रूरी है
    - c) Training code (loss, backward pass, optimizer) हमेशा model की अपनी class परिभाषा का हिस्सा होता है
    - d) llama.cpp बुनियादी रूप से अलग गणितीय operations compute करता है, क्योंकि वह C में लिखा है

<details markdown="1"><summary>जाँचें</summary>

**b)** यही वह अनुवाद है जो यह पाठ सिखाता है। (a) ग़लत है: बुनियादी architecture वही है, बस नाम और configuration अलग हैं। (c) ग़लत है: training code अलग training script या utility में रहता है, model class के भीतर नहीं। (d) ग़लत है: operations गणितीय रूप से एक जैसे हैं; सिर्फ़ यह अलग है कि computation graph कैसे बनता और व्यक्त होता है।

</details>

## असली दुनिया का अभ्यास

- [ ] `transformers` library में GPT-2-शैली के model का implementation खोलें और उसकी attention class, उसका causal mask, और उसका `wte`/`wpe`/`lm_head` नामकरण ढूँढें, हर एक को उस पाठ से मिलाते हुए जिसने उसे निकाला।
- [ ] जाँचें कि वही model pre-norm इस्तेमाल करता है या post-norm, और GELU या ReLU, और इस पाठ की आम अंतरों की सूची के सामने ध्यान दें कि कौन-सा कौन-सा है।
- [ ] कल: अपनी पहुँच वाले किसी model की training script (या `Trainer` का इस्तेमाल) ढूँढें, और उसकी loss की गणना, `.backward()` call और optimizer step का पता लगाएँ।

## आगे बढ़ने के लिए

- [Repo: transformers, Hugging Face](https://github.com/huggingface/transformers)
- [Repo: nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
