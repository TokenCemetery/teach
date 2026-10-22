---
title: "शब्दावली"
description: "Transformers के मानक शब्द"
type: glossary
---

# Transformers शब्दावली

Transformer architecture के मानक शब्द, जो पहले से बने किसी module के बजाय सीधे raw tensors से निकाले गए हैं।

## शब्द

**Cross-attention**:
ऐसी attention sublayer जिसकी queries एक sequence से आती हैं (decoder का अब तक generate किया हुआ अपना output), पर keys और values किसी दूसरी sequence से आती हैं (एक अलग encoder का output)। इससे decoder generate करते समय पूरे, पहले से encode किए जा चुके input को देख सकता है। Decoder-only model में यह नहीं होती, क्योंकि उसमें न कोई अलग encoder होता है और न कोई अलग input sequence जिस पर attend किया जा सके।
_बचें_: self-attention (यह अलग sublayer है जिसकी queries, keys और values तीनों एक ही sequence से आती हैं; cross-attention अपनी keys/values ख़ास तौर पर उस sequence से लेती है जो उसकी queries वाली sequence से अलग है)

**Encoder-decoder**:
ऐसा architecture (जैसा मूल transformer पेपर या T5 में है) जो एक bidirectional encoder को, जिसमें causal mask नहीं होता और जो पूरे input को प्रोसेस करता है, एक ऐसे decoder से जोड़ता है जो causal self-attention और encoder के output पर वापस cross-attention का इस्तेमाल करके output को autoregressively generate करता है। यह उन tasks के लिए ठीक बैठता है जिनमें input और फिर output का साफ़, तय बँटवारा हो, जैसे अनुवाद।
_बचें_: decoder-only (वह architecture जो यह workspace बनाता है, जिसमें कोई अलग encoder या cross-attention नहीं होता, क्योंकि उसकी अकेली stream conditioning context और generate किए जाने वाले output, दोनों का काम करती है)

**Encoder-only**:
ऐसा architecture (जैसा BERT में है) जो bidirectional attention इस्तेमाल करता है, यानी हर layer में बाएँ और दाएँ दोनों संदर्भ पर एक साथ conditioning करता है, और जिसमें causal mask बिल्कुल नहीं होता। यह पहले से दिए गए पूरे input की representation बनाता है, समझने वाले tasks (classification, extraction) के लिए, text को autoregressively generate करने के लिए नहीं, जो उसका architecture कर ही नहीं सकता।
_बचें_: decoder-only (causal mask वाला architecture जो ख़ास तौर पर एक बार में एक token generate करने के लिए बना है; encoder-only की bidirectional attention को सिर्फ़ prefix देखकर predict करना कभी सिखाया ही नहीं गया)

**FlashAttention**:
Scaled dot-product attention का IO-aware और exact implementation, जो computation को टुकड़ों (tiles) में बाँटकर तेज़ on-chip GPU memory (SRAM) में ही रखता है, और धीमी main memory (HBM) में quadratic रूप से बड़ा पूरा attention score matrix कभी बनाता ही नहीं। यह पाठ 1 के समीकरण जैसा ही गणितीय नतीजा देता है; तेज़ी पूरी तरह memory access से आती है, किसी चीज़ का approximation करने से नहीं।
_बचें_: approximate attention (अलग तरह के तरीक़ों का परिवार जो गति के लिए गुणवत्ता से समझौता करते हैं; FlashAttention exact है और उसकी तेज़ी सिर्फ़ IO की कुशलता से आती है)

**Gated linear unit (GLU)**:
एक ही input के दो linear projections का elementwise गुणनफल, जिसमें पहले उनमें से किसी एक पर nonlinearity (शुरुआत में sigmoid) लगाई जाती है। वह projection gate का काम करता है और दूसरे projection के output को element-दर-element scale करता है, बजाय इसके कि हर जगह एक ही तय nonlinearity लगे।
_बचें_: SwiGLU (यह GLU का एक ख़ास variant है, जिसमें Swish/SiLU से gating होती है; "GLU" आम परिवार है, उसका यही एक सदस्य नहीं)

**Gradient accumulation**:
कई छोटे micro-batches पर एक के बाद एक forward और backward pass चलाना, उनके बीच gradients को शून्य किए बिना, ताकि हर micro-batch के gradients पिछले वालों पर जुड़ते जाएँ, और फिर जुड़े हुए कुल पर optimizer का एक ही step लेना। यह उससे बड़ा effective batch size नक़ल करता है जो memory एक साथ रख पाती, और जो compute हो रहा है उसे नहीं बदलता।
_बचें_: असली batch size बढ़ाना (gradient accumulation यही नतीजा पाता है, बिना इसके कि बड़े batch को कभी एक साथ memory में समाना पड़े)

**Gradient norm clipping**:
जब भी पूरे gradient vector का norm चुनी हुई सीमा से बड़ा हो, उस पूरे vector को इतना छोटा scale कर देना कि norm सीमा से ऊपर न जाए, और उसकी दिशा वैसी ही रहे। यह कभी-कभार फटने वाले gradient से एक विनाशकारी रूप से बड़े update से बचाता है।
_बचें_: हर parameter का gradient अलग-अलग clip करना (इससे जुड़े हुए gradient की दिशा बिगड़ती है; norm-आधारित clipping पूरे vector को एकसमान रूप से rescale करती है)

**Greedy decoding**:
हर generation step पर model के predicted distribution से हमेशा सबसे ज़्यादा probability वाला अकेला token चुनना। यह deterministic है, और उसी मात्रा को maximize करने के बावजूद जिसे model को अच्छी तरह predict करने के लिए train किया गया था, व्यवहार में फीका और अजीब ढंग से दोहराव वाला text देता है।
_बचें_: यह मान लेना कि training का objective (likelihood) अपने आप सही decoding objective भी है; ये दो अलग सवाल हैं और दोनों के जवाब अलग हैं

**Grouped-query attention (GQA)**:
Attention का ऐसा variant जो key/value heads की बीच की संख्या इस्तेमाल करता है, एक से ज़्यादा पर query heads की संख्या से कम, और query heads के समूह हर एक key/value head को आपस में बाँटते हैं। यह पूरी multi-head attention (हर head की अपनी keys/values) और multi-query attention (एक साझा head) के बीच का रास्ता है।
_बचें_: multi-query attention (MQA) (ज़्यादा चरम मामला, यानी एक साझा key/value head; GQA उसका सामान्यीकरण है जो एक से ज़्यादा रखता है)

**KV cache**:
Autoregressive generation के दौरान हर पिछली position के सहेजे हुए key और value vectors, जिन्हें हर नए generation step पर शुरू से दोबारा compute करने के बजाय दोबारा इस्तेमाल किया जाता है। इसका आकार इस पर निर्भर करता है कि model के पास key/value heads के कितने अलग सेट हैं, और grouped-query तथा multi-query attention ठीक इसी को घटाते हैं।
_बचें_: हर generation step पर keys और values दोबारा compute करना (सही है पर बेकार; cache इसी से बचने के लिए बना है)

**Learning rate warmup**:
शुरुआती training steps की तय संख्या में learning rate को धीरे-धीरे (अक्सर linearly) बढ़ाना, जब तक वह अपने लक्ष्य मान तक न पहुँचे, बजाय इसके कि पूरी ताक़त से शुरू से ही लगाया जाए। यह Adam के moment estimates के सबसे शुरुआती steps में अविश्वसनीय होने की समस्या सँभालता है, जब उन्हें calibrate करने लायक़ gradients अभी देखे ही नहीं गए होते।
_बचें_: पहले step से ही लक्ष्य learning rate लगाना (optimizer के अपने आँकड़े स्थिर होने से पहले एक बड़े, ग़लत दिशा वाले update का जोखिम रहता है)

**Mixed precision training**:
Training के ज़्यादातर हिस्से में weights, activations और gradients को पूरी (single) precision के बजाय half precision में रखना, जिससे memory का इस्तेमाल लगभग आधा हो जाता है। इसके लिए पूरी precision वाली master weight copy (ताकि छोटे updates, जो वरना underflow हो जाते, बचे रहें) और loss scaling (ताकि छोटे gradients underflow होकर शून्य न हो जाएँ) ज़रूरी हैं।
_बचें_: सिर्फ़ half precision में training, बिना master weight copy या loss scaling के (छोटे updates और gradients underflow में चुपचाप खो जाने का जोखिम रहता है)

**Mixture-of-experts (MoE)**:
ऐसी layer जो एक अकेले feed-forward block की जगह कई parallel expert feed-forward blocks और एक router रखती है, जो चुनता है कि किसी token को कौन-से expert(s) प्रोसेस करें। यह sparsely activated है: कुल parameter count experts की संख्या के साथ बढ़ता है, पर प्रति token compute लागत लगभग वही रहती है, क्योंकि सिर्फ़ चुने गए expert(s) ही चलते हैं।
_बचें_: यह मान लेना कि ज़्यादा experts का मतलब प्रति token ज़्यादा compute है (किसी token की लागत में सिर्फ़ router के चुने expert का compute गिना जाता है, कुल कितने experts हैं इससे फ़र्क़ नहीं पड़ता)

**Nucleus sampling (top-p)**:
सबसे ज़्यादा probability वाले tokens के उस सबसे छोटे सेट से sample करना जिनकी संचयी probability एक threshold `p` से ऊपर निकल जाए, ऐसा सेट जिसका आकार हर step पर इस पर निर्भर करके बदलता है कि distribution कितना नुकीला या चपटा है। इसके उलट top-k की तय आकार वाली छँटाई इस बदलाव के हिसाब से ढल नहीं पाती।
_बचें_: top-k sampling (तय गिनती वाली छँटाई; nucleus sampling का cutoff इसके बजाय संचयी probability पर आधारित गतिशील सेट है)

**RMSNorm**:
ऐसा normalization जो activation vector को उसके root mean square से भाग देता है और सीखा हुआ scale लगाता है, यानी layer norm की re-scaling वाली क्रिया रखता है और उसका re-centering (mean घटाने) वाला चरण पूरी तरह छोड़ देता है। यह layer norm से सस्ता है, और व्यवहार में task performance लगभग वैसी ही रहती है।
_बचें_: layer norm (mean और variance पर आधारित वह normalization जिसे RMSNorm सरल बनाता है; RMSNorm कोई mean कभी compute या subtract ही नहीं करता)

**Rotary position embedding (RoPE)**:
Positional तरीक़ा जो projected query और key vectors को उनकी position के अनुपात में एक कोण से घुमाता है, बजाय इसके कि पहले embedding में कोई तय vector जोड़ा जाए। चूँकि rotations कोण जोड़कर compose होते हैं, नतीजे में attention score सिर्फ़ दो positions के बीच के सापेक्ष अंतर पर निर्भर करता है, किसी की भी absolute position पर नहीं।
_बचें_: sinusoidal encoding (अलग, जोड़ने वाला तरीक़ा जो projection से पहले embedding पर लगता है; RoPE गुणात्मक है और projection के बाद Q और K पर, attention computation के भीतर ही लगता है)

**Scaled dot-product attention**:
यह ऑपरेशन `softmax(QK^T / sqrt(d_k)) V`: एक query की keys के सेट से dot product के ज़रिए तुलना करें, `d_k` के साथ variance बढ़ने का असर काटने के लिए scale करें, scores को softmax से weights में बदलें, और संबंधित values का भारित योग लौटाएँ।
_बचें_: attention mechanism (जब यही ख़ास रूप मतलब हो तो बहुत अस्पष्ट है)

**Self-attention**:
Scaled dot-product attention जिसमें queries, keys और values तीनों एक ही input sequence से आते हैं, इसलिए हर position उसी sequence की हर position पर attend करती है, ख़ुद पर भी।
_बचें_: intra-attention

**SwiGLU**:
Swish (SiLU) activation से gated GLU variant, जो आज के ज़्यादातर open models के feed-forward sublayer में सादे ReLU या GELU nonlinearity की जगह इस्तेमाल होता है। इसमें सादे feed-forward block के दो weight matrices की जगह तीन होते हैं (दो up-projections, एक down-projection)।
_बचें_: GELU, ReLU (तय, एक-projection वाली nonlinearities जिन्हें SwiGLU का gated, दो-projection वाला design आज के models में बदल देता है)

**Temperature**:
वह मान जिससे generation के दौरान next-token distribution बनाने वाले softmax से पहले logits को भाग दिया जाता है। 1 से कम होने पर यह distribution को greedy के व्यवहार की ओर नुकीला करता है; 1 से ऊपर होने पर चपटा करता है। यह distribution कितना नुकीला है इसे बदलता है, पर यह तय नहीं करता कि कौन-से tokens sample होने के योग्य हैं।
_बचें_: top-k, top-p (temperature सिर्फ़ probability की तीक्ष्णता rescale करता है; योग्य सेट तय करना अलग, बाद का चरण है जो ये तरीक़े करते हैं)

**Top-k sampling**:
Next-token distribution को उसके `k` सबसे ज़्यादा probability वाले tokens तक छाँटना, बाक़ी हटा देना, और उस तय आकार वाले, दोबारा normalize किए गए सेट से sample करना। nucleus (top-p) sampling के उलट, योग्य सेट का आकार इस पर कभी नहीं ढलता कि किसी step पर distribution असल में कितना नुकीला या चपटा है।
_बचें_: nucleus sampling (top-p) (गतिशील आकार वाला विकल्प; top-k की cutoff गिनती distribution के असली आकार से अप्रभावित, तय रहती है)

**Xavier (Glorot) initialization**:
किसी layer के शुरुआती weight variance को उसके fan-in और fan-out (वह कितने inputs और outputs से जुड़ी है) के हिसाब से scale करना, हर layer के लिए एक ही तय variance इस्तेमाल करने के बजाय, ताकि गहरे network की layers में activation और gradient का variance लगभग एक-सा बना रहे, बजाय इसके कि हर layer के साथ वह छोटा या बड़ा होता जाए।
_बचें_: आकार की परवाह किए बिना हर layer के लिए एक ही तय initialization variance (वही समस्या जिसे ठीक करने के लिए Xavier initialization ख़ास तौर पर बनाया गया था)
