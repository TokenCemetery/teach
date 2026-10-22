---
title: "Transformers"
description: "Attention को शुरू से बनाएँ, ताकि architecture training script के पीछे काला डिब्बा न रहे"
type: topic
---

# सीखना: Transformers

Transformer का forward pass और उसका training loop raw tensors से लागू कर सकें, और असली model code को बिना इस काले डिब्बे के पढ़ या बदल सकें कि उसके पीछे architecture क्या है।

**नवीनतम पाठ:** [23. Model Code में बदलाव की समीक्षा](lessons/0023-reviewing-a-change-to-model-code.md)

## सफलता कैसी दिखती है

- Scaled dot-product attention, multi-head attention और पूरा transformer block raw tensors से लागू करें, किसी reference implementation के output से मेल खाते हुए।
- उस block के आसपास फ़िट होने वाला training loop शुरू से लिखें और समझाएँ कि हर हिस्सा (loss, backward pass, optimizer step) weights के साथ क्या कर रहा है।
- किसी असली model का code पढ़ें (`transformers` या `llama.cpp` जैसी library) और बताएँ कि हर निकाला हुआ हिस्सा कहाँ रहता है।
- किसी और के model code में किए बदलाव की समीक्षा करें और ठीक-ठीक बताएँ कि वह क्या तोड़ता है या उसकी क्या क़ीमत है (shape की गड़बड़ी जो दो layers आगे जाकर ही दिखती है, तेज़ी का दावा जिसके साथ मेल खाता output नहीं, कोई architectural दावा जो पेपर के असली समीकरण दोबारा पढ़ने पर टिकता नहीं), pull request के विवरण पर भरोसा करने के बजाय।

## सीमाएँ

- मानकर चला गया है कि आप Python और बुनियादी PyTorch tensor operations में सहज हैं, और matrix multiplication ही वह अकेला गणित है जिसे पहले से मान लिया गया है; deep-learning का कोई पूर्व ज्ञान नहीं चाहिए।
- Implementation PyTorch में, `nn.Transformer` या दूसरे बने-बनाए attention modules की जगह raw tensor operations के साथ; autograd और GPU सपोर्ट रखे गए हैं, सिर्फ़ architecture ख़ुद हाथ से बना है।

## दायरे से बाहर

- Basic loop से आगे के optimizer और scheduler variants जो block को train होते देखने के लिए ज़रूरी हैं, और distributed training: [`llm/pretraining`](../../llm/pretraining/) देखें, जो तब शुरू होता है जब यह loop कई GPUs पर चलाना हो।
- Block के ऊपर बनी low-rank/adapter व्यवस्था: उस सीमा के लिए [`llm/finetuning`](../../llm/finetuning/) देखें। यह workspace वह निकालता है जिसका वह workspace बस नाम लेता है (उसके पाठ 0003 में tokenizers, उसके पाठ 0008 में low-rank विचार), उन्हें दोहराता नहीं।

## पूरी रूपरेखा

बारह चरण, एक समीकरण से लेकर किसी भी पैमाने के असली model code को पढ़ने और उससे generate करने तक। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. Attention | 0001 से 0003 | Scaled dot-product attention, multi-head attention, causal masking | Multi-head attention raw tensors से लागू हो और किसी reference implementation से मेल खाए |
| 2. Transformer block | 0004 से 0006 | Positional encoding, layer norm और residual connections, feed-forward block | पूरा transformer block raw tensors से लागू हो |
| 3. पूरा model | 0007 से 0008 | Blocks को stack करना, embedding और output layers, weight tying | पूरा forward pass किसी reference implementation के output से मेल खाए |
| 4. Training loop | 0009 से 0011 | Vocabulary पर cross-entropy loss, backward pass, AdamW optimizer step | Model शुरू से train हो और loss उम्मीद के मुताबिक़ घटे |
| 5. असली model code पढ़ना | 0012 से 0013 | हर निकाले हुए हिस्से को असली library (`transformers` या `llama.cpp`) से मिलाना, tokenizers और low-rank adapters का बस नाम लेना | बता सकें कि हर निकाला हुआ हिस्सा असली model code में कहाँ रहता है |
| 6. आधुनिक positional encoding और normalization | 0014 से 0015 | Rotary position embeddings, RMSNorm | RoPE का सापेक्ष-position गुण निकाल सकें और समझा सकें कि RMSNorm layer norm से क्या छोड़ता है |
| 7. आधुनिक feed-forward और attention variants | 0016 से 0017 | SwiGLU/gated feed-forward, grouped-query और multi-query attention, KV caching | Gated feed-forward block निकाल सकें और समझा सकें कि कम KV heads cache के आकार के लिए गुणवत्ता का सौदा क्यों करते हैं |
| 8. Generation और sampling | 0018 | Greedy decoding, temperature, top-k और top-p sampling, text बनाने के लिए model को आगे चलाना | हाथ से बने model से text generate कर सकें और समझा सकें कि greedy decoding बिगड़ क्यों जाता है |
| 9. Training loop की व्यावहारिकताएँ | 0019 से 0020 | Xavier initialization, learning-rate warmup और decay, gradient clipping, mixed precision, gradient accumulation | समझा सकें कि हर व्यावहारिकता किससे बचाती है और उन्हें चलते training loop में जोड़ सकें |
| 10. Encoder-decoder और encoder-only architectures | 0021 | BERT का bidirectional encoder, cross-attention वाला T5 का encoder-decoder, इस workspace के decoder-only model को सही जगह रखना | समझा सकें कि हर architecture causal mask इस्तेमाल क्यों करता है या क्यों नहीं, और cross-attention कहाँ फ़िट होती है |
| 11. Mixture-of-experts और FlashAttention | 0022 | Sparsely-activated MoE routing, FlashAttention की IO-aware tiling | समझा सकें कि MoE parameters को प्रति-token compute से कैसे अलग करता है, और FlashAttention approximate नहीं बल्कि exact क्यों है |
| 12. विवेक | 0023 | किसी और के model code के बदलावों की समीक्षा, shapes और output की exactness जाँचना, विवादित दावों का निपटारा मुख्य स्रोत से करना | model architecture और training loop में बदलावों की समीक्षा पर भरोसा किया जा सके, और विवरण स्वीकार करने के बजाय समझा सकें कि बदलाव की क्या क़ीमत या जोखिम है |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-scaled-dot-product-attention.md) | Scaled Dot-Product Attention | वह एक समीकरण जिसके इर्द-गिर्द architecture का बाक़ी सब कुछ बना है |
| [0002](lessons/0002-multi-head-attention.md) | Multi-Head Attention | Attention एक ही पूरे आयाम में चलने के बजाय एक साथ कई छोटे subspaces में क्यों चलता है |
| [0003](lessons/0003-causal-masking.md) | Causal Masking | कोई query position भविष्य की positions पर attend क्यों नहीं कर सकती, और mask softmax से पहले क्यों लगता है, बाद में क्यों नहीं |
| [0004](lessons/0004-positional-encoding.md) | Positional Encoding | Attention अपने-आप में क्रम के प्रति अंधा क्यों है, और sinusoidal encoding हर position को पहचानी जा सकने वाली छाप कैसे देता है |
| [0005](lessons/0005-layer-norm-and-residuals.md) | Layer Norm और Residual Connections | कई transformer blocks को stack करने के लिए साफ़ gradient path और स्थिर activation ranges क्यों चाहिए, और residuals तथा layer norm उनमें से एक-एक कैसे देते हैं |
| [0006](lessons/0006-feed-forward-block.md) | Position-Wise Feed-Forward Block | Transformer block की दूसरी sublayer attention के ऊपर क्या जोड़ती है, और वह positions के बीच जानकारी कभी क्यों नहीं मिलाती |
| [0007](lessons/0007-stacking-blocks.md) | Transformer Blocks को Stack करना | हर block एक ही shape क्यों बनाए रखता है, गहराई का मतलब weight sharing क्यों नहीं है, और कई blocks stack होने पर पाठ 5 की residual व्यवस्था सबसे ज़्यादा क्यों मायने रखती है |
| [0008](lessons/0008-embedding-output-and-weight-tying.md) | Embedding और Output Layers, Weight Tying | Tokens transformer के vector space में कैसे आते-जाते हैं, और यह करने वाली दो layers एक ही matrix क्यों साझा कर सकती हैं |
| [0009](lessons/0009-cross-entropy-loss.md) | Vocabulary पर Cross-Entropy Loss | Logits एक train हो सकने वाली संख्या कैसे बनते हैं, और loss असली अगले token की probability का ऋणात्मक log क्यों है |
| [0010](lessons/0010-backward-pass-and-autograd.md) | Backward Pass और Autograd | Chain rule, रिकॉर्ड किए गए computation graph पर स्वचालित होकर, एक scalar loss को हर weight के gradient में कैसे बदलता है |
| [0011](lessons/0011-adamw-optimizer.md) | AdamW Optimizer Step | Adam का momentum और adaptive scaling सादे gradient descent के ऊपर क्या जोड़ते हैं, और AdamW weight decay को gradient update से अलग क्यों करता है |
| [0012](lessons/0012-reading-real-model-code.md) | असली Model Code पढ़ना | हर निकाला हुआ हिस्सा production model library में कहाँ रहता है, और मूल पेपर से वे छोटे, आम अंतर जिन्हें उलझने के बजाय पहचानना ज़रूरी है |
| [0013](lessons/0013-tokenizers-and-low-rank-adapters.md) | Tokenizers और Low-Rank Adapters | Byte-pair encoding को निकालना, और यह कि low-rank adapter इस workspace में शुरू से बने weight matrix पर असल में कहाँ जुड़ता है |
| [0014](lessons/0014-rotary-position-embeddings.md) | Rotary Position Embeddings | Sinusoidal encoding attention चलने से पहले embedding में एक तय vector जोड़ता है; RoPE इसके बजाय Q और K को ही घुमाता है, और यही एक बदलाव दो घुमाए गए vectors के dot product को सिर्फ़ उनकी सापेक्ष दूरी पर निर्भर बनाता है |
| [0015](lessons/0015-rmsnorm.md) | RMSNorm | LayerNorm दो काम करता है, re-centering और re-scaling, और RMSNorm इसलिए है कि re-centering वाला आधा हिस्सा ग़ैर-ज़रूरी निकला, जिससे एक सस्ता normalization बचता है जिसे मौजूदा models पाठ 5 की निकाली pre-norm शाखा के भीतर इस्तेमाल करते हैं |
| [0016](lessons/0016-swiglu-and-the-gated-feed-forward.md) | SwiGLU और Gated Feed-Forward Block | पाठ 6 का feed-forward block फैलता है, एक nonlinearity लगाता है, और सिकुड़ता है; gated variant एक की जगह दो projections compute करके उन्हें आपस में गुणा करता है, जिससे network सीखता है कि अपनी ही गणना का कितना हिस्सा आगे जाने दे |
| [0017](lessons/0017-grouped-query-attention-and-kv-caching.md) | Grouped-Query Attention और KV Caching | Autoregressive generation attention से वे keys और values दोबारा compute करवाती है जो उसके पास पहले से हैं, और उन्हें cache करना जब साफ़ हल बन जाता है, तो cache का अपना आकार ही कम key/value heads के लिए थोड़ी गुणवत्ता का सौदा करने लायक़ बनाता है |
| [0018](lessons/0018-generation-and-sampling.md) | Generation और Sampling | इस workspace में बना और train किया गया model आज तक एक बार भी text नहीं बना पाया, क्योंकि training और generation उससे दो अलग सवाल पूछते हैं, और हमेशा सबसे संभावित अकेला अगला token चुनना दूसरे सवाल का, सोच-समझकर चुनी गई थोड़ी randomness के मुक़ाबले, बदतर जवाब निकलता है |
| [0019](lessons/0019-initialization-warmup-and-gradient-clipping.md) | Initialization, Warmup और Gradient Clipping | इतना गहरा model training शुरू होने से पहले ही फ़ेल हो सकता है अगर उसकी शुरुआती weights ग़लत scale पर हों, और पाठ 11 में निकले AdamW step को असली training में टिके रहने के लिए अब भी दो और सुरक्षा-रेखाएँ चाहिए, धीमी शुरुआत और gradient पर कड़ी सीमा |
| [0020](lessons/0020-mixed-precision-and-gradient-accumulation.md) | Mixed Precision और Gradient Accumulation | दोनों तकनीकें बड़े effective training run को उस hardware में समाने लायक़ बनाने के लिए हैं जो run की ज़रूरत से छोटा दिखता है, एक हर संख्या का footprint घटाकर, दूसरी ऐसा batch नक़ल करके जिसे memory कभी एक साथ नहीं रख सकती |
| [0021](lessons/0021-encoder-decoder-and-encoder-only-architectures.md) | Encoder-Decoder और Encoder-Only Architectures | इस workspace ने causal mask वाली एक stream इसलिए बनाई क्योंकि उसे सिर्फ़ एक काम करना था, अगला token generate करना, और बाक़ी दो architecture आकार इसलिए हैं कि BERT और मूल अनुवाद model को इसके बजाय संरचनात्मक रूप से अलग गारंटी चाहिए थी |
| [0022](lessons/0022-mixture-of-experts-and-flashattention.md) | Mixture-of-Experts और FlashAttention | MoE model के कुल parameters बढ़ाता है, बिना इसे बढ़ाए कि किसी एक token को प्रोसेस होने की क्या क़ीमत देनी पड़ती है, और FlashAttention पाठ 1 का ठीक वही समीकरण तेज़ी से compute करता है, इसे बदलकर कि वह memory को कैसे छूता है, इसे नहीं कि वह क्या compute करता है |
| [0023](lessons/0023-reviewing-a-change-to-model-code.md) | Model Code में बदलाव की समीक्षा | किसी और के model code में किए बदलाव की समीक्षा करें और बताएँ कि वह क्या तोड़ता है या उसकी क्या क़ीमत है, विवरण पर भरोसा न करें |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत
- [Attention](reference/attention.md): scaled dot-product attention, multi-head attention और causal masking, हर चरण पर tensor shapes के नोट के साथ
- [Transformer Block](reference/the-transformer-block.md): positional encoding, layer norm और residuals, feed-forward block, stacking, और weight tying
- [Training Loop](reference/the-training-loop.md): cross-entropy loss, backward pass और autograd, और AdamW optimizer step, chain-rule और gradient-descent के worked examples के साथ
- [असली Code से मैपिंग](reference/mapping-to-real-code.md): transformers/llama.cpp की नाम-मैपिंग, मूल पेपर से तीन मानक अंतर, byte-pair encoding, और low-rank adapter कहाँ जुड़ता है

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके मुख्य स्रोत तक खंगालना ठीक रहेगा।
