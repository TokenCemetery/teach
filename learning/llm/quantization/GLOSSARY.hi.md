---
title: "शब्दावली"
description: "LLM quantization के मानक शब्द"
type: glossary
---

# Quantization शब्दावली

Number formats, quantization methods, जिस hardware पर वे चलते हैं और उनकी लागत कैसे मापी जाती है, इनके मानक शब्द। इस workspace में "quantization" का मतलब हमेशा train हो चुके model की संख्याओं की precision घटाना है; इसका मतलब कभी inputs को discretise करना नहीं है।

## शब्द

**Absmax quantization**:
Symmetric quantization जिसकी clipping range एक ही scale साझा करने वाली values में सबसे बड़ी absolute value होती है, इसलिए कुछ भी clip नहीं होता और scale वही value होती है जिसे सबसे बड़े integer level से भाग दिया गया हो।
_बचें_: max scaling, naive quantization

**Act-order**:
GPTQ का एक option जो किसी layer के columns को activation के घटते आकार के क्रम में quantize करता है, उन्हें Hessian के diagonal पर sort करके। यह लेखकों के code में documented है, पेपर में नहीं।
_बचें_: desc_act को पहले परिचय दिए बिना, reorder trick (GPTQ के एक variant के लिए AWQ पेपर का नाम)

**Activation**:
Forward pass के दौरान compute होने वाला tensor, जैसे किसी linear layer का input, जो store किए गए weight से अलग है। उसकी values input पर निर्भर करती हैं, इसलिए उसकी range सिर्फ़ run time पर पता चलती है या calibration set से अनुमानित की जाती है।
_बचें_: hidden state (खास तौर पर residual stream के लिए ठीक है), feature map

**Affine quantization**:
ऐसा quantization जिसमें scale और zero point दोनों हों, ताकि integer grid zero के आसपास असमान रूप से बैठ सके और [-0.2, 1.5] जैसी range को levels बर्बाद किए बिना ढक सके।
_बचें_: asymmetric quantization (स्वीकृत पर्यायवाची, पर एक ही शब्द इस्तेमाल करें), uniform quantization (symmetric के लिए भी सच है)

**Arithmetic intensity**:
किसी computation द्वारा memory से हर byte लाने पर किए गए arithmetic operations की संख्या, जो तय करती है कि दी गई chip पर वह memory-bound है या compute-bound।
_बचें_: operational intensity, FLOP-to-byte ratio (formula में स्वीकृत)

**Bit width**:
एक quantized value को store करने में लगे bits की संख्या, उसके scale और zero point पर खर्च हुए bits को छोड़कर। कुल के लिए effective bits per weight देखें।
_बचें_: precision (mantissa bits के साथ अस्पष्ट), bit depth

**Block-scaled format**:
ऐसा format जिसमें values का छोटा block, जैसे 32 values, एक scale साझा करता है जो उनके साथ store होता है, इसलिए element type बहुत संकरा हो सकता है। MXFP4 और NVFP4 इसके उदाहरण हैं, GGUF के block types भी।
_बचें_: microscaling (वह एक परिवार है, OCP का MX), grouped format

**Calibration set**:
Representative inputs का छोटा नमूना जिसे model से गुज़ारकर activation statistics जुटाई जाती हैं, और जिसे post-training method ranges चुनने या rounding errors को वज़न देने में इस्तेमाल करती है। यह training data नहीं है और PTQ इस पर कभी backpropagate नहीं करता।
_बचें_: training set, calibration dataset (ठीक है, पर statistics के लिए "calibration data" नहीं)

**Clipping error**:
Clipping range के बाहर की values को उसके सिरों पर clamp करने से पैदा होने वाली error।
_बचें_: saturation error, overflow

**Clipping range**:
Real values का वह अंतराल जिसे quantizer अपने integer grid पर map करता है; उसके बाहर की values सबसे नज़दीकी सिरे पर clamp हो जाती हैं। इसे चुनना clipping error और rounding error के बीच का सौदा है।
_बचें_: dynamic range (वह format की विशेषता है), quantization range

**Compute-bound**:
ऐसा workload जिसकी गति bytes हिलाने से नहीं बल्कि arithmetic throughput से सीमित होती है, जैसे prefill और बड़े batch का decode। सिर्फ़ weights को quantize करने से वह तेज़ नहीं होता, और धीमा भी हो सकता है।
_बचें_: FLOP-bound (ठीक है, पर एक ही शब्द इस्तेमाल करें)

**Dequantization**:
Scale और zero point से किसी quantized integer को वापस अनुमानित real value में map करना, या तो ऊँची precision में compute करने के लिए या error जाँचने के लिए।
_बचें_: unquantization, decompression

**Dynamic quantization**:
किसी activation का scale run time पर उन values से compute करना जो असल में मौजूद हों, बजाय इसके कि उसे calibration set से पहले से तय किया जाए। Static quantization से तुलना करें।
_बचें_: on-the-fly quantization, runtime quantization

**Effective bits per weight**:
हर weight पर औसत storage, जब scales, zero points और per-group का बाक़ी metadata गिन लिया जाए। उदाहरण के लिए 32 के group पर 16-bit scale वाले 4-bit weights के लिए लगभग 4.5।
_बचें_: bpw को परिभाषित किए बिना, bit width (जो metadata को छोड़ देती है)

**Exponent bits**:
Floating-point format के वे bits जो तय करते हैं कि value को दो की किस घात से scale किया गया है, और इस तरह उसकी dynamic range।
_बचें_: range bits

**Fake quantization**:
Forward pass में किसी tensor को quantize करके तुरंत dequantize कर देना, ताकि training को rounding और clamping की error दिखे जबकि arithmetic floating point में ही रहे।
_बचें_: simulated quantization (स्वीकृत पर्यायवाची, पर एक ही शब्द इस्तेमाल करें), quantization noise injection

**Flip**:
एक ही सवाल पर baseline model और उसके quantized version के बीच ऐसा उत्तर जो सही से ग़लत या ग़लत से सही हो जाए। दोनों दिशाओं की flips accuracy के औसत में एक-दूसरे को काट देती हैं, इसलिए उन्हें अलग-अलग गिना जाता है।
_बचें_: answer change (ग़लत से ग़लत को भी गिनता है), regression (सिर्फ़ एक दिशा)

**GGUF**:
llama.cpp का single-file model format, जो tensors को, अक्सर अपने ही block quantization types में, tokenizer और model metadata के साथ store करता है।
_बचें_: GGML (library और एक पुराना format), llama format

**GPTQ**:
Post-training weight quantization method जो किसी layer के weights को एक-एक column करके quantize करता है और हर rounding error की भरपाई के लिए अभी quantize न हुए weights को update करता है, calibration activations की second-order जानकारी से।
_बचें_: GPT quantization, किसी भी 4-bit checkpoint के लिए सामान्य शब्द के रूप में

**Granularity**:
कितनी values एक scale और zero point साझा करती हैं: पूरा tensor (per-tensor), एक output channel (per-channel), एक token (per-token), या channel के भीतर तय आकार का group (per-group)।
_बचें_: resolution, quantization level

**Group size**:
Per-group quantization में एक scale साझा करने वाली लगातार values की संख्या, जैसे 32 या 128।
_बचें_: block size (जहाँ format खुद इसे यही कहता है, जैसे MX या GGUF, वहाँ स्वीकृत)

**Hessian**:
GPTQ में, किसी layer के calibration inputs से बनी matrix `H = 2 X X^T`, जिसमें हर input feature के लिए एक row और एक column होता है। यह दर्ज करती है कि कौन-से features साथ-साथ बदलते हैं, और layer के weights की हर row इसे साझा करती है।
_बचें_: curvature matrix, covariance matrix (क़रीब है, पर वही चीज़ नहीं)

**Importance matrix**:
llama.cpp में, calibration text पर activations से अनुमानित प्रति-weight importance, जिसे हर block का scale चुनते समय rounding error को वज़न देने में इस्तेमाल किया जाता है।
_बचें_: imatrix को पहले परिचय दिए बिना गद्य में

**Kernel**:
वह GPU routine जो एक operation करती है, जैसे किसी quantization scheme में matrix multiplication। कोई scheme तभी तेज़ चलता है जब hardware पर उसके लिए kernel मौजूद हो।
_बचें_: operator (ज़्यादा व्यापक), implementation

**KL divergence**:
Quantized model का next-token distribution baseline के distribution से कितना दूर है, dataset के tokens पर औसत लेकर। दोनों के ठीक बराबर होने पर यह 0 होता है और इसे labelled उत्तर नहीं चाहिए।
_बचें_: KLD को परिभाषित किए बिना, distance (अस्पष्ट)

**KV-cache quantization**:
Cache किए गए attention keys और values को कम bits में store करना, ताकि context length और batch size के साथ बढ़ने वाली memory घटे।
_बचें_: cache compression (eviction भी इसमें आता है), weights का KV quantization

**Loss scaling**:
Backpropagation से पहले loss को किसी constant से गुणा करना, ताकि छोटे gradients fp16 जैसे संकरी range वाले format में represent हो सकें, और weight update से पहले उस constant से भाग दे देना।
_बचें_: gradient scaling (gradient clipping के साथ अस्पष्ट)

**Machine epsilon**:
Floating-point format में 1 और उसके ऊपर की अगली representable value के बीच का फ़ासला, जो 2 की उस घात के बराबर है जो mantissa bits की संख्या का ऋणात्मक है।
_बचें_: unit roundoff (round-to-nearest में इसका आधा), precision

**Mantissa bits**:
Floating-point format के वे bits जो तय करते हैं कि दो की एक घात के भीतर values कितनी बारीकी से फैली हैं, और इस तरह उसकी precision।
_बचें_: significand (सही है पर एक ही शब्द इस्तेमाल करें), fraction bits

**Massive activation**:
LLM में एक अकेली activation value जो बाक़ी से कई गुना बड़ी होती है, किसी तय dimension पर और पहले token जैसे ख़ास tokens पर दिखती है।
_बचें_: outlier feature (संबंधित पर अलग pattern), spike

**Memory-bound**:
ऐसा workload जिसकी गति arithmetic से नहीं बल्कि इससे सीमित होती है कि bytes memory से कितनी तेज़ी से आते हैं, जैसे छोटे batch का decode, जहाँ हर generate हुए token पर हर weight एक बार पढ़ा जाता है।
_बचें_: bandwidth-bound (ठीक है, पर एक ही शब्द इस्तेमाल करें), IO-bound

**Mixed-precision decomposition**:
Matrix multiplication को इस तरह बाँटना कि कुछ outlier feature dimensions 16-bit में और बाक़ी int8 में compute हों, यही LLM.int8() का मूल है।
_बचें_: outlier splitting, mixed precision (ज़्यादा व्यापक)

**Native format**:
ऐसा number format जिसमें chip की matrix units सीधे गुणा करती हैं, उस storage-only format के उलट जिसे गुणा से पहले native format में बदलना पड़ता है।
_बचें_: supported format (storage और compute के बीच अस्पष्ट)

**Noise floor**:
किसी score में run-to-run और sampling का उतार-चढ़ाव, जिसके नीचे baseline और quantized model के बीच का अंतर संयोग से अलग नहीं पहचाना जा सकता।
_बचें_: margin of error (floor को अंतराल के रूप में बताया जाता है), tolerance

**Outlier feature**:
Hidden-state की ऐसी dimension जिसमें transformer की activations ज़्यादातर tokens और layers में लगातार दूसरों से बहुत बड़ी होती हैं।
_बचें_: outlier channel (संबंधित weight channel के लिए स्वीकृत), outlier शब्द के बिना emergent feature

**Perplexity**:
किसी text को model जो औसत negative log-likelihood देता है उसका exponential, जिसे यह तेज़ी से परखने के proxy की तरह इस्तेमाल किया जाता है कि किसी बदलाव ने model को कितना नुक़सान पहुँचाया।
_बचें_: PPL को पहले परिचय दिए बिना गद्य में, accuracy

**Post-training quantization**:
पहले से train हो चुके model को आगे की training के बिना quantize करना, ज़्यादा से ज़्यादा एक छोटे calibration set के सहारे।
_बचें_: PTQ को पहले परिचय दिए बिना गद्य में, one-shot quantization

**Quantization**:
Model की real-valued संख्याओं को कम bits वाले छोटे levels के सेट पर represent करना, एक सीमित approximation error की क़ीमत पर।
_बचें_: compression (ज़्यादा व्यापक), discretisation

**Quantization config**:
Model के `config.json` में `quantization_config` entry, जिसके `quant_method` और दूसरे keys loader को बताते हैं कि store किए गए tensors कौन-सा method, bit width और group size इस्तेमाल करते हैं।
_बचें_: quantize config (कुछ tools जो अलग file लिखते हैं), metadata

**Quantization-aware training**:
Model को forward pass में fake quantization के साथ train या fine-tune करना, ताकि weights उस rounding के हिसाब से ढल जाएँ जिसका उन्हें सामना करना है।
_बचें_: QAT को पहले परिचय दिए बिना गद्य में, quantized training (वह low precision में compute करती है)

**Ridge point**:
वह arithmetic intensity जिस पर chip की peak arithmetic rate और उसकी memory bandwidth में बराबर समय लगता है; इसके नीचे computation memory-bound है और ऊपर compute-bound।
_बचें_: roofline knee, crossover

**Rotation**:
किसी layer की activations और weights को एक orthogonal matrix और उसके transpose से गुणा करना, जिससे layer का output नहीं बदलता पर outliers कई channels में फैल जाते हैं और बेहतर quantize होते हैं।
_बचें_: Hadamard transform (rotation का एक चुनाव), incoherence processing (सामान्य विचार)

**Round-to-nearest**:
हर value को स्वतंत्र रूप से उसके सबसे नज़दीकी grid level पर quantize करना, बिना data और बिना error की भरपाई के। वह baseline जिससे हर दूसरे post-training method की तुलना होती है।
_बचें_: RTN को पहले परिचय दिए बिना गद्य में, naive quantization

**Rounding error**:
Clipping range के भीतर की value को सबसे नज़दीकी grid level पर खिसकाने से पैदा होने वाली error; round-to-nearest के लिए ज़्यादा से ज़्यादा आधा step।
_बचें_: quantization noise (संयुक्त error के लिए स्वीकृत), precision loss

**Safetensors**:
Tensor file format जिसमें 8-byte का header length, tensor names, dtypes, shapes और offsets का JSON header, और फिर raw data होता है। यह सिर्फ़ tensors store करता है, इसलिए quantization scheme का वर्णन quantization config में होता है।
_बचें_: checkpoint (files का पूरा सेट), weights file

**Salient channel**:
Weight matrix का वह input channel जिसकी quantization error सबसे ज़्यादा मायने रखती है, जिसे AWQ में उस activation के आकार से पहचाना जाता है जिससे वह मिलता है, न कि उसके अपने weights के आकार से।
_बचें_: important weight (गद्य में ठीक है), outlier channel (outlier feature का weight-पक्ष वाला नाम)

**Scale**:
Quantizer के आसन्न integer levels के बीच का real-valued step size, ताकि कोई real value लगभग scale गुणा उसका integer हो।
_बचें_: step (formula में ठीक है), multiplier

**Static quantization**:
किसी activation का scale calibration set से पहले से तय कर देना, ताकि run time पर कोई statistics compute न हो। Dynamic quantization से तुलना करें।
_बचें_: offline quantization

**Straight-through estimator**:
Backward pass में rounding step को identity function मानना, ताकि ऐसे operation के आर-पार भी gradient बह सके जिसका असली derivative लगभग हर जगह zero है।
_बचें_: STE को पहले परिचय दिए बिना गद्य में, surrogate gradient (ज़्यादा व्यापक)

**Super-block**:
GGUF के k-quant में, 256 weights का group जो sub-blocks में बँटा होता है जिनमें से हर एक का अपना scale होता है, और उन scales को 16-bit super-block scale के सापेक्ष quantize किया जाता है।
_बचें_: block (legacy types की 32-weight वाली इकाई)

**Symmetric quantization**:
ऐसा quantization जिसमें zero point zero पर तय रहता है, इसलिए grid zero के चारों ओर केंद्रित होता है और सिर्फ़ scale store होता है।
_बचें_: scale-only quantization

**Weight-only quantization**:
Weights को low precision में store करना और kernel के भीतर dequantize करना, जबकि activations और arithmetic 16-bit में रहते हैं। इसे WxA16 लिखा जाता है, जैसे W4A16।
_बचें_: mixed-precision quantization (ज़्यादा व्यापक)

**WxAy notation**:
किसी scheme के weight और activation bit widths का संक्षिप्त रूप, जैसे 8-bit weights और activations के लिए W8A8, कभी-कभी KV cache के लिए KVz के साथ।
_बचें_: int4 लिखना जब activations भी int4 न हों

**Zero point**:
वह integer जो affine quantization में real zero को represent करता है, इस तरह चुना गया कि zero बिल्कुल represent हो सके।
_बचें_: offset, bias
