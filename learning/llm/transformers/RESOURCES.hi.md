---
title: "संसाधन"
description: "Transformers के लिए भरोसेमंद स्रोत"
type: resources
---

# Transformers संसाधन

## ज्ञान

- [पेपर: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
  मूल transformer पेपर: scaled dot-product attention, multi-head attention, और पूरा encoder-decoder block जिसे यह workspace raw tensors से निकालता है। इस्तेमाल: इस workspace में लागू हर हिस्से की मूल परिभाषा के लिए।
- [लेख: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
  Attention और transformer block का दृश्य, अंतर्ज्ञान-पहले वाला walkthrough, जो पेपर की notation से पहले पढ़ने के लिए बनाया गया है। इस्तेमाल: कुछ भी लागू करने से पहले काम चलाऊ मानसिक model बनाने के लिए।
- [लेख: "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
  पेपर का पंक्ति-दर-पंक्ति PyTorch implementation, raw tensor operations से, उन समीकरणों से सीधे मिलाया हुआ जो उन्हें बनाते हैं। इस्तेमाल: शुरू से बने implementation को reference से पंक्ति-दर-पंक्ति जाँचने के लिए।
- [Repo: nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
  GPT-शैली के transformer और उसके training loop का न्यूनतम, पढ़ने लायक़ PyTorch implementation, इतना छोटा कि पूरा पढ़ा जा सके। इस्तेमाल: मिशन के training-loop वाले आधे हिस्से के लिए, जब block ख़ुद काम करने लगे।
- [वीडियो: "Let's build GPT: from scratch, in code, spelled out", Karpathy](https://www.youtube.com/watch?v=kCc8FmEb1nY)
  Screen पर attention और GPT training loop को raw tensors से चरण-दर-चरण बनाता है, हर हिस्से को तैयार रूप में पेश करने के बजाय निकालते हुए। इस्तेमाल: ख़ुद code लिखने से पहले या उसके साथ-साथ derivation होते देखने के लिए।
- [दस्तावेज़: "Autograd mechanics", PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
  इसकी आधिकारिक व्याख्या कि PyTorch का autograd computation graph से होकर gradients असल में कैसे compute करता है। इस्तेमाल: यह समझने के लिए कि backward pass weights के साथ क्या कर रहा है, सिर्फ़ `.backward()` बुलाने के बजाय।
- [Repo: transformers, Hugging Face](https://github.com/huggingface/transformers)
  असली, production model library, जो शुरू से बने हिस्से तैयार हो जाने के बाद काम की है। इस्तेमाल: सिखाने के लिए नहीं बल्कि production के लिए लिखे code में attention, multi-head projection और transformer block ढूँढने के लिए।
- [पेपर: "Layer Normalization", Ba, Kiros, and Hinton, 2016](https://arxiv.org/abs/1607.06450)
  Layer normalization पेश करता है: हर example की अपनी activations को feature आयाम पर normalize करना, batch size से स्वतंत्र, batch normalization के उलट। इस्तेमाल: यह समझने के लिए कि layer norm असल में क्या compute करता है और वह बदलती लंबाई की sequences और छोटे batch sizes में क्यों फ़िट बैठता है।
- [पेपर: "On Layer Normalization in the Transformer Architecture", Xiong et al., 2020](https://arxiv.org/abs/2002.04745)
  Layer norm को residual जोड़ने के बाद रखने (मूल पेपर का चुनाव, post-norm) की तुलना उसे हर sublayer से पहले, residual शाखा के भीतर, रखने (pre-norm) से करता है, और दिखाता है कि pre-norm ज़्यादा गहराई पर ज़्यादा स्थिरता से क्यों train होता है। इस्तेमाल: यह समझने के लिए कि मूल transformer पेपर के post-norm इस्तेमाल करने के बावजूद ज़्यादातर मौजूदा बड़े models pre-norm क्यों इस्तेमाल करते हैं।
- [पेपर: "Using the Output Embedding to Improve Language Models", Press and Wolf, 2017](https://arxiv.org/abs/1608.05859)
  Input embedding और output projection weight matrices को tie करने के पक्ष में तर्क देता है, क्योंकि दोनों किसी token को एक ही बुनियादी representation से जोड़ते हैं, और बड़ी vocabulary वाले model के parameters का बड़ा हिस्सा घटाता है। इस्तेमाल: weight tying को सोचे-समझे design चुनाव के रूप में समझने के लिए, सिर्फ़ parameter बचाने की तरकीब के रूप में नहीं।
- [दस्तावेज़: "torch.nn.functional.cross_entropy", PyTorch](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
  Fused softmax-जमा-ऋणात्मक-log-likelihood operation के आधिकारिक docs, जो संख्यात्मक स्थिरता के लिए सीधे कच्चे logits लेता है, बजाय इसके कि पहले अलग softmax चरण माँगे। इस्तेमाल: यह समझने के लिए कि cross-entropy loss व्यवहार में असल में कैसे compute होता है, सिर्फ़ उसका सूत्र नहीं।
- [पेपर: "Adam: A Method for Stochastic Optimization", Kingma and Ba, 2015](https://arxiv.org/abs/1412.6980)
  सादे gradient descent के ऊपर Adam का momentum (first moment) और adaptive प्रति-parameter scaling (second moment) पेश करता है, दोनों के bias correction के साथ। इस्तेमाल: AdamW के weight-decay सुधार से पहले यह समझने के लिए कि Adam का update नियम क्या compute करता है और क्यों।
- [पेपर: "Decoupled Weight Decay Regularization", Loshchilov and Hutter, 2019](https://arxiv.org/abs/1711.05101)
  पहचानता है कि मूल Adam में weight decay को gradient में मिलाना उसकी adaptive scaling से बुरी तरह क्यों टकराता है, और decay को सीधे weights पर लगाकर उसे ठीक करता है। इस्तेमाल: transformers को train करने का मानक optimizer सादा Adam नहीं बल्कि AdamW क्यों है, यह समझने के लिए।
- [पेपर: "Neural Machine Translation of Rare Words with Subword Units", Sennrich, Haddow, and Birch, 2016](https://arxiv.org/abs/1508.07909)
  Subword tokenization के लिए byte-pair encoding पेश करता है: सबसे आम पास-पास की symbol जोड़ी को बार-बार मिलाकर कच्चे bytes से ऊपर की ओर vocabulary बनाना। इस्तेमाल: उस tokenizer तंत्र को निकालने के लिए जिसका `llm/finetuning` सिर्फ़ नाम लेता है, उसे दोहराने के बजाय।
- [पेपर: "RoFormer: Enhanced Transformer with Rotary Position Embedding", Su et al., 2021](https://arxiv.org/abs/2104.09864)
  RoPE पेश करता है: project किए query और key vectors को position के अनुपात वाले कोण से घुमाना, जिससे ऐसा attention score बनता है जो सिर्फ़ सापेक्ष अंतर पर निर्भर करता है। इस्तेमाल: उस तंत्र के लिए जिसे लगभग हर मौजूदा open model sinusoidal या सीखे हुए positional encoding की जगह इस्तेमाल करता है।
- [पेपर: "Root Mean Square Layer Normalization", Zhang and Sennrich, 2019](https://arxiv.org/abs/1910.07467)
  RMSNorm पेश करता है, यह परिकल्पना रखते हुए कि layer norm का re-centering (mean घटाने वाला) operation ग़ैर-ज़रूरी है और उसके ज़्यादातर फ़ायदे के लिए अकेली re-scaling ज़िम्मेदार है। इस्तेमाल: उस सस्ते normalization के लिए जिसे मौजूदा models पाठ 5 में निकली pre-norm शाखा के भीतर रखते हैं।
- [पेपर: "GLU Variants Improve Transformer", Shazeer, 2020](https://arxiv.org/abs/2002.05202)
  Transformer की feed-forward sublayer में gated linear unit variants (Swish से gated SwiGLU समेत) परखता है, और पाता है कि कुछ आम तौर पर इस्तेमाल होने वाले ReLU या GELU से बेहतर हैं। इस्तेमाल: मौजूदा models में पाठ 6 के एक-projection वाले feed-forward block की जगह लेने वाले gated, दो-up-projection design के लिए।
- [पेपर: "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints", Ainslie et al., 2023](https://arxiv.org/abs/2305.13245)
  Grouped-query attention को पूरे multi-head attention और multi-query attention के अकेले साझा key/value head के बीच के रास्ते के रूप में पेश करता है, साथ में मौजूदा multi-head checkpoint को उसमें uptrain करने की सस्ती विधि। इस्तेमाल: यह समझने के लिए कि कम key/value heads बहुत छोटे KV cache और तेज़ inference के लिए थोड़ी गुणवत्ता का सौदा क्यों करते हैं।
- [पेपर: "The Curious Case of Neural Text Degeneration", Holtzman et al., 2019](https://arxiv.org/abs/1904.09751)
  दर्ज करता है कि decoding के समय likelihood को maximize करना (greedy decoding) likelihood के अच्छे training objective होने के बावजूद फीका, दोहराव वाला text क्यों बनाता है, और हल के रूप में nucleus (top-p) sampling पेश करता है। इस्तेमाल: इस सटीक कारण के लिए कि गतिशील, संचयी-probability वाला cutoff greedy decoding और तय top-k गिनती, दोनों से बेहतर क्यों है।
- [पेपर: "On the difficulty of training Recurrent Neural Networks", Pascanu, Mikolov, and Bengio, 2013](https://arxiv.org/abs/1211.5063)
  Vanishing और exploding gradient की समस्याओं का विश्लेषण करता है और दूसरी के हल के रूप में gradient norm clipping प्रस्तावित करता है। इस्तेमाल: यह समझने के लिए कि clipping हर parameter का gradient अलग-अलग सीमित करने के बजाय पूरे gradient vector को उसके norm से rescale क्यों करती है।
- [पेपर: "Mixed Precision Training", Micikevicius et al., 2018](https://arxiv.org/abs/1710.03740)
  Half precision में training पेश करता है, पूरी precision वाली master weight copy और half precision की सीमित संख्यात्मक range का सामना करने के लिए loss scaling के साथ, memory की खपत लगभग आधी करते हुए। इस्तेमाल: ठीक इसके लिए कि सादी half-precision training में क्या जोड़ना पड़ता है ताकि छोटे updates और gradients शून्य तक underflow न हों।
- [पेपर: "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", Devlin et al., 2018](https://arxiv.org/abs/1810.04805)
  Encoder-only architecture पेश करता है: bidirectional attention जो हर layer में बाएँ और दाएँ संदर्भ पर एक साथ conditioning करता है, कोई causal mask नहीं। इस्तेमाल: यह समझने के लिए कि encoder-only model text को autoregressively generate करने के बजाय पूरे input की representation क्यों बनाता है, और वह क्यों नहीं कर सकता जो इस workspace का decoder-only model करता है।
- [पेपर: "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer" (T5), Raffel et al., 2019](https://arxiv.org/abs/1910.10683)
  NLP tasks की बड़ी range को एक एकसमान text-to-text, encoder-decoder format में ढालता है। इस्तेमाल: encoder-decoder आकार की cross-attention sublayer के लिए, और यह समझने के लिए कि वह साफ़, तय input-फिर-output बँटवारे वाले task में क्यों फ़िट बैठता है।
- [पेपर: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness", Dao et al., 2022](https://arxiv.org/abs/2205.14135)
  लंबी sequences पर मानक attention की धीमी गति का निदान IO की समस्या के रूप में करता है (HBM और SRAM के बीच memory पढ़ना/लिखना), compute की समस्या नहीं, और एक tiled, exact algorithm पेश करता है जो पूरा score matrix बनाने से बचता है। इस्तेमाल: यह समझने के लिए कि असली attention implementation पाठ 1 के संस्करण से संरचनात्मक रूप से अलग क्यों दिखता है जबकि वही नतीजा compute करता है।
- [पेपर: "Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity", Fedus, Zoph, and Shazeer, 2021](https://arxiv.org/abs/2101.03961)
  सरलीकृत, प्रति-token एक-expert वाली MoE routing योजना पेश करता है, जो कुल parameter count को प्रति-token compute लागत से अलग करती है। इस्तेमाल: sparsely-activated models जो ख़ास सौदा करते हैं उसके लिए, और यह समझने के लिए कि routing को एक expert तक सरल करने से उन अस्थिरताओं का हल कैसे निकला जिनसे ज़्यादा जटिल MoE designs टकराए थे।

## कमियाँ

- Learning-rate-warmup-फिर-decay schedule पर अभी कोई स्रोत नहीं; पाठ 19 उसे मूल transformer पेपर के अपने training ब्योरों में बताए आकार से निकालता है (linear warmup, फिर step संख्या के उलटे वर्गमूल के अनुपात में decay), पर उस खंड का सीधा, ताज़ा-सत्यापित अंश इस session में उपलब्ध tooling से नहीं मिल सका (पेपर का abstract पन्ना training-ब्योरों वाला खंड नहीं रखता, और उसके दूसरे PDF स्रोत पढ़ने लायक़ text के रूप में नहीं निकले)। कोई साफ़ स्रोत मिलने पर दोबारा देखें।
