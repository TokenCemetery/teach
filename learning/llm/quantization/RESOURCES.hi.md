---
title: "संसाधन"
description: "LLM quantization के लिए भरोसेमंद स्रोत"
type: resources
---

# Quantization संसाधन

## ज्ञान

### बुनियाद

- [पेपर: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295)
  Qualcomm AI Research की पाठ्यपुस्तक जितनी लंबी भूमिका: hardware की प्रेरणा, uniform affine quantizer, range तय करना, granularity, PTQ और QAT pipelines, और debugging का workflow। इस्तेमाल: चरण 2 और 6 में mapping और range के चुनाव के लिए, सार की जगह स्रोत से।
- [पेपर: "A Survey of Quantization Methods for Efficient Neural Network Inference", Gholami et al., 2021](https://arxiv.org/abs/2103.13630)
  Uniform और non-uniform quantizers, granularity, PTQ बनाम QAT, और mixed precision का व्यापक सर्वेक्षण। इस्तेमाल: किसी method का अपना पेपर पढ़ने से पहले उसे बड़े परिवार में रखने के लिए।
- [पेपर: "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference", Jacob et al., 2017](https://arxiv.org/abs/1712.05877)
  ज़्यादातर int8 deployments के पीछे की integer-only inference योजना: ऐसे zero के साथ affine mapping जो बिल्कुल represent हो सके, और simulated quantization के साथ training। इस्तेमाल: scale और zero-point की परिपाटी कहाँ से आती है।

### Number formats

- [पेपर: "Mixed Precision Training", Micikevicius et al., 2017](https://arxiv.org/abs/1710.03740)
  fp32 master copy और loss scaling के साथ fp16 में training, और fp16 की संकरी range scaling को ज़रूरी क्यों बनाती है। इस्तेमाल: fp16 के पाँच exponent bits की क्या क़ीमत है।
- [पेपर: "A Study of BFLOAT16 for Deep Learning Training", Kalamkar et al., 2019](https://arxiv.org/abs/1905.12322)
  bf16 के पक्ष में तर्क, जो fp32 का exponent रखता है और mantissa bits छोड़ देता है। इस्तेमाल: training के लिए precision से range ज़्यादा मायने क्यों रखती थी।
- [पेपर: "FP8 Formats for Deep Learning", Micikevicius et al., 2022](https://arxiv.org/abs/2209.05433)
  E4M3 और E5M2 आठ-bit floating-point encodings, उनकी विशेष values, और उनमें training और inference के नतीजे। इस्तेमाल: हर fp8 variant किस लिए है।
- [पेपर: "Microscaling Data Formats for Deep Learning", Rouhani et al., 2023](https://arxiv.org/abs/2310.10537)
  Block-scaled formats जिनमें संकरे elements का block दो की घात वाला एक scale साझा करता है, OCP MX formats का आधार। इस्तेमाल: MXFP4 और उसके साथी block को कैसे store करते हैं।
- [लेख: "Introducing NVFP4 for Efficient and Accurate Low-Precision Inference", NVIDIA Technical Blog](https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/)
  एक vendor का 4-bit floating-point format जिसमें MXFP4 से छोटा block और बारीक scale है। इस्तेमाल: NVFP4 MXFP4 से कैसे अलग है, vendor के दस्तावेज़ की तरह पढ़ें।

### Outliers

- [पेपर: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., 2022](https://arxiv.org/abs/2208.07339)
  बड़े transformers में int8 को तोड़ने वाली outlier feature dimensions खोजता है, और mixed-precision decomposition से उन्हें 16-bit में रखता है। इस्तेमाल: outliers कहाँ दिखते हैं और पहला इलाज।
- [पेपर: "Massive Activations in Large Language Models", Sun et al., 2024](https://arxiv.org/abs/2402.17762)
  बाक़ी से कई गुना बड़ी अकेली activations, तय dimensions और ख़ास tokens पर, जो सीखे हुए biases की तरह काम करती हैं। इस्तेमाल: दूसरा outlier pattern और वह noise क्यों नहीं है।
- [पेपर: "Quantizable Transformers: Removing Outliers by Helping Attention Heads Do Nothing", Bondarenko et al., 2023](https://arxiv.org/abs/2306.12929)
  Outliers को उन attention heads से जोड़ता है जो कुछ न करना सीखते हैं, और training के दौरान architecture बदलकर उन्हें हटाता है। इस्तेमाल: outliers होते ही क्यों हैं।

### Post-training quantization

- [पेपर: "The case for 4-bit precision: k-bit Inference Scaling Laws", Dettmers and Zettlemoyer, 2022](https://arxiv.org/abs/2212.09720)
  Bit widths, data types और block sizes पर 35,000 से ज़्यादा zero-shot experiments, जो model के bits की तय संख्या के लिए 4 bits को लगभग सार्वभौम रूप से इष्टतम पाते हैं, जिसमें सिर्फ़ छोटे blocks और data type का चुनाव मदद करते हैं। इस्तेमाल: 4-bit weights default क्यों बने, और block size क्या ख़रीदता है।
- [पेपर: "Up or Down? Adaptive Rounding for Post-Training Quantization", Nagel et al., 2020](https://arxiv.org/abs/2004.10568)
  दिखाता है कि हर weight को उसके सबसे नज़दीकी level पर round करना layer के output के लिए इष्टतम नहीं है, और इसके बजाय rounding की दिशा सीखता है। इस्तेमाल: round-to-nearest accuracy पीछे क्यों छोड़ देता है।
- [पेपर: "Optimal Brain Compression", Frantar and Alistarh, 2022](https://arxiv.org/abs/2208.11580)
  सटीक layer-wise quantization method जिसे GPTQ तेज़ बनाता है, उस update के साथ जो एक weight की error को बाक़ियों पर ख़र्च करता है। इस्तेमाल: GPTQ की वंशावली।
- [पेपर: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2022](https://arxiv.org/abs/2210.17323)
  अनुमानित second-order जानकारी का इस्तेमाल करके one-shot 3 और 4-bit weight quantization, 175B-parameter models के पैमाने पर। इस्तेमाल: GPTQ कैसे काम करता है और उसका calibration set क्या है।
- [पेपर: "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration", Lin et al., 2023](https://arxiv.org/abs/2306.00978)
  पाता है कि weight channels का छोटा हिस्सा सबसे ज़्यादा मायने रखता है, जिसे activation magnitude से पहचाना जाता है, और उसे mixed precision की जगह per-channel scaling से बचाता है। इस्तेमाल: AWQ कैसे काम करता है और उसे backpropagation क्यों नहीं चाहिए।
- [पेपर: "SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models", Xiao et al., 2022](https://arxiv.org/abs/2211.10438)
  Activation outliers को गणितीय रूप से समतुल्य per-channel scale से weights में migrate करता है, जिससे W8A8 संभव होता है। इस्तेमाल: 8 bits पर weight-और-activation quantization।
- [पेपर: "QuaRot: Outlier-Free 4-Bit Inference in Rotated LLMs", Ashkboos et al., 2024](https://arxiv.org/abs/2404.00456)
  Hidden states को Hadamard transforms से rotate करता है ताकि weights, activations और KV cache सब 4 bits पर quantize हों। इस्तेमाल: rotations outliers को कैसे हटाते हैं।
- [पेपर: "SpinQuant: LLM Quantization with Learned Rotations", Liu et al., 2024](https://arxiv.org/abs/2405.16406)
  Rotation matrices को तय करने की जगह सीखता है, और दिखाता है कि random rotations की quality में बहुत फ़र्क़ होता है। इस्तेमाल: rotation का चुनाव मायने क्यों रखता है।
- [पेपर: "KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache", Liu et al., 2024](https://arxiv.org/abs/2402.02750)
  पाता है कि keys को per channel और values को per token quantize करना चाहिए, और दोनों 2 bits पर करता है। इस्तेमाल: KV-cache quantization में axis का चुनाव।
- [पेपर: "KVQuant: Towards 10 Million Context Length LLM Inference with KV Cache Quantization", Hooper et al., 2024](https://arxiv.org/abs/2401.18079)
  Rotary embedding से पहले per-channel key quantization, बहुत लंबे contexts के लिए non-uniform types और outlier handling। इस्तेमाल: लंबे context पर KV-cache quantization क्या देता है।
- [Repo: gptq, IST-DASLab](https://github.com/IST-DASLab/gptq)
  GPTQ लेखकों का reference implementation, जिसकी README `--act-order` (columns को activation के घटते आकार के क्रम में quantize करना), `--true-sequential` और `--static-groups` को documented करती है। इस्तेमाल: act-order और `g_idx` tensor, जिन्हें पेपर नहीं बताता।

### Quantization-aware training

- [पेपर: "Estimating or Propagating Gradients Through Stochastic Neurons for Conditional Computation", Bengio et al., 2013](https://arxiv.org/abs/1308.3432)
  कठोर थ्रेशोल्ड के आर-पार gradients के estimators पेश करता और तुलना करता है, straight-through estimator समेत। इस्तेमाल: STE कहाँ से आता है।
- [पेपर: "LLM-QAT: Data-Free Quantization Aware Training for Large Language Models", Liu et al., 2023](https://arxiv.org/abs/2305.17888)
  LLMs पर QAT, model के ख़ुद generate किए data का इस्तेमाल करके, KV-cache quantization समेत, 4 bits पर PTQ से तुलना के साथ। इस्तेमाल: LLM पर QAT क्या वापस लाती है और किस लागत पर।
- [पेपर: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., 2023](https://arxiv.org/abs/2305.14314)
  NF4, double quantization और frozen 4-bit base के आर-पार adapters को train करना। इस्तेमाल: QAT से सीमा, और वह स्रोत जिससे finetuning track सिखाता है।
- [लेख: "Quantization-Aware Training for Large Language Models with PyTorch", PyTorch Blog, 2024](https://pytorch.org/blog/quantization-aware-training/)
  Llama 2 और Llama 3 पर torchao QAT flow, PTQ के मुक़ाबले मापी गई recovery और fake quantization के fine-tuning overhead के साथ। इस्तेमाल: असली LLM पर QAT क्या वापस लाती है और क्या क़ीमत लेती है, एक team की मापों की तरह पढ़ें।

### Hardware और serving

- [पेपर: "MARLIN: Mixed-Precision Auto-Regressive Parallel Inference on Large Language Models", Frantar et al., 2024](https://arxiv.org/abs/2408.11743)
  4-bit-weight, 16-bit-activation GPU kernel और इसका विश्लेषण कि weight-only quantization batched decode को कब तेज़ करता है। इस्तेमाल: speed-up batch size पर निर्भर क्यों है।
- [पेपर: "QServe: W4A8KV4 Quantization and System Co-design for Efficient LLM Serving", Lin et al., 2024](https://arxiv.org/abs/2405.04532)
  दिखाता है कि dequantization का overhead GPUs पर 4-bit schemes का फ़ायदा मिटा सकता है, और उससे बचने के लिए format और kernel को साथ-साथ डिज़ाइन करता है। इस्तेमाल: कम bits अपने-आप तेज़ क्यों नहीं होते।
- [दस्तावेज़: "Quantization", vLLM](https://docs.vllm.ai/en/latest/features/quantization/)
  एक serving engine कौन-सी schemes support करता है और किस hardware पर। इस्तेमाल: चुनने से पहले जाँचना कि scheme के लिए kernel है या नहीं।
- [दस्तावेज़: "Quantized KV Cache", vLLM](https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/)
  fp8 KV cache: per-tensor या per-head scales, calibration के बिना default scales, और उन्हें llm-compressor से calibrate करना। इस्तेमाल: 8-bit KV cache को व्यवहार में क्या चाहिए।
- [दस्तावेज़: "Quantization overview", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/overview)
  Transformers जिन quantization backends को integrate करता है और उनके बीच कैसे चुनें। इस्तेमाल: tooling का नक़्शा।
- [Repo: llm-compressor, vLLM project](https://github.com/vllm-project/llm-compressor)
  ऐसी library जो GPTQ, AWQ, SmoothQuant और FP8 recipes लगाती है और ऐसे checkpoints लिखती है जिन्हें vLLM load करता है। इस्तेमाल: असली model पर PTQ को शुरू से अंत तक चलाना।
- [Repo: compressed-tensors, Neural Magic](https://github.com/neuralmagic/compressed-tensors)
  Safetensors का वह विस्तार जो checkpoint की quantization scheme को उसके config में दर्ज करता है। इस्तेमाल: quantized safetensors checkpoint में क्या store होता है।
- [दस्तावेज़: "int8 W8A8" उदाहरण, llm-compressor](https://github.com/vllm-project/llm-compressor/blob/main/examples/quantization_w8a8_int8/README.md)
  हल किया हुआ W8A8 int8 recipe: SmoothQuant, फिर channelwise weight scales के साथ GPTQ, फिर dynamic per-token activation scales। इस्तेमाल: असली model पर SmoothQuant चलाना।
- [दस्तावेज़: "Choosing a dataset", LLM Compressor](https://docs.vllm.ai/projects/llm-compressor/en/latest/steps/choosing-dataset/)
  किन algorithms को calibration set चाहिए, उसके domain को लक्ष्य उपयोग से मिलाना, और आम आकार। इस्तेमाल: calibration set पर व्यावहारिक मार्गदर्शन।
- [दस्तावेज़: "GPTQ", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/gptq)
  GPTQ को `GPTQConfig` से built-in dataset या अपने text के साथ चलाना। इस्तेमाल: Transformers से GPTQ के साथ quantize करना।
- [दस्तावेज़: "AWQ", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/awq)
  AWQ checkpoints load करना और वे `quantization_config` keys जो AWQ checkpoint दर्ज करता है। इस्तेमाल: AWQ checkpoint का config पढ़ना।
- [दस्तावेज़: "bitsandbytes", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
  Transformers 8-bit और 4-bit bitsandbytes models कैसे load करता है, compute data type समेत। इस्तेमाल: यह देखना कि store किए गए 4-bit weights ऊँची precision में compute होते हैं।
- [दस्तावेज़: "NVIDIA A100 Tensor Core GPU" datasheet, NVIDIA](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-nvidia-us-2188504-web.pdf)
  A100 का प्रति format tensor-core throughput और उसकी memory bandwidth। इस्तेमाल: roofline में Ampere की संख्याएँ, vendor के दस्तावेज़ की तरह पढ़ें।
- [दस्तावेज़: "NVIDIA Ada GPU Architecture" whitepaper, NVIDIA](https://images.nvidia.com/aem-dam/Solutions/Data-Center/l4/nvidia-ada-gpu-architecture-whitepaper-v2.1.pdf)
  Ada के tensor cores और उनका FP8 support। इस्तेमाल: किन inference GPUs में FP8 tensor cores हैं, vendor के दस्तावेज़ की तरह पढ़ें।
- [दस्तावेज़: "NVIDIA H100 Tensor Core GPU", NVIDIA](https://www.nvidia.com/en-us/data-center/h100/)
  FP8 और INT8 tensor-core पंक्तियों और memory bandwidth के साथ H100 की specification table। इस्तेमाल: Hopper की संख्याएँ, vendor के दस्तावेज़ की तरह पढ़ें।
- [लेख: "NVIDIA Hopper Architecture In-Depth", NVIDIA Technical Blog](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/)
  Hopper के साथ आए FP8 tensor cores और Transformer Engine। इस्तेमाल: NVIDIA data-centre GPUs में FP8 compute कब आया, vendor के दस्तावेज़ की तरह पढ़ें।

### File formats

- [दस्तावेज़: "Safetensors", Hugging Face](https://huggingface.co/docs/safetensors/index)
  वह tensor file format जिसमें ज़्यादातर checkpoints आते हैं, और वह क्या store करता है और क्या नहीं। इस्तेमाल: वह container जिसके बग़ल में quantization config बैठता है।
- [दस्तावेज़: "GGUF", Hugging Face Hub](https://huggingface.co/docs/hub/gguf)
  GGUF format का परिचय और उसके quantization types की table उनके bit layouts के साथ। इस्तेमाल: GGUF type name को decode करना।
- [दस्तावेज़: llama.cpp quantize tool README, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md)
  llama.cpp model को अपने quant types में कैसे बदलता है, types की सूची, और importance matrix कैसे दी जाती है। इस्तेमाल: GGUF quantization ख़ुद बनाना।
- [Repo: safetensors, Hugging Face](https://github.com/huggingface/safetensors)
  Byte-स्तर का format: 8-byte little-endian header length, नामों, dtypes, shapes और offsets का JSON header, फिर data। इस्तेमाल: checkpoint के tensors load किए बिना उसका header पढ़ना।
- [दस्तावेज़: "compressed-tensors", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/compressed_tensors)
  compressed-tensors checkpoints load करना, FP8 `config_groups` उदाहरण और उसकी tensor सूची के साथ। इस्तेमाल: compressed-tensors config और उसके scale tensors पढ़ना।
- [Model card: "TinyLlama-1.1B-Chat-v1.0-GPTQ", TheBloke](https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GPTQ)
  एक छोटा सार्वजनिक 4-bit GPTQ checkpoint जिसका card bits, group size, act order और damping समझाता है। इस्तेमाल: जाँचने के लिए असली checkpoint।
- [स्रोत: ggml-common.h, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-common.h)
  हर GGUF block type का C struct। इस्तेमाल: type के bits per weight को उद्धृत करने की जगह उसके layout से निकालना।
- [Pull request: "k-quants", ikawrakow, llama.cpp, 2023](https://github.com/ggml-org/llama.cpp/pull/1684)
  k-quants, type-0 और type-1 नामकरण और मूल S, M और L मिश्रण पेश करता है। इस्तेमाल: suffixes का पेश किए जाने के समय क्या मतलब था।
- [Pull request: "Importance Matrix calculation", ikawrakow, llama.cpp, 2024](https://github.com/ggml-org/llama.cpp/pull/4861)
  Calibration text पर activations से importance matrix निकालता है और उसे rounding error को वज़न देने में इस्तेमाल करता है। इस्तेमाल: importance matrix calibration set क्यों है।
- [दस्तावेज़: llama.cpp imatrix tool README, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/imatrix/README.md)
  Importance matrix कैसे compute करें और उसे quantize tool को कैसे दें। इस्तेमाल: ख़ुद एक बनाना।

### Quality की हानि मापना

- [पेपर: "Accuracy is Not All You Need", Dutta et al., 2024](https://arxiv.org/abs/2407.09141)
  दिखाता है कि quantized model अपनी baseline की accuracy से मेल खा सकता है जबकि कई अलग-अलग उत्तर बदल दे, और दूरी वाले metrics के रूप में flips और KL divergence प्रस्तावित करता है। इस्तेमाल: न बदला औसत बदले हुए model को कैसे छिपा सकता है।
- [पेपर: "Give Me BF16 or Give Me Death? Accuracy-Performance Trade-Offs in LLM Quantization", Kurtic et al., 2024](https://arxiv.org/abs/2411.02355)
  Llama 3.1 के आकारों और tasks पर FP8, INT8 और INT4 schemes के पाँच लाख से ज़्यादा evaluations, हर scheme के लिए deployment मार्गदर्शन के साथ। इस्तेमाल: हर scheme की क्या क़ीमत है, सावधानी से मापी हुई।
- [पेपर: "Scaling Laws for Precision", Kumar et al., 2024](https://arxiv.org/abs/2411.04330)
  पाता है कि post-training quantization model को उतना ज़्यादा बिगाड़ता है जितने ज़्यादा data पर वह train हुआ। इस्तेमाल: आम 4-bit वाला जवाब बहुत ज़्यादा train हुए model पर क्यों विफल हो सकता है।
- [Repo: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  वह harness जिससे ज़्यादातर quantization पेपर task accuracy बताते हैं। इस्तेमाल: baseline और quantized model पर वही tasks चलाना।
- [दस्तावेज़: "Perplexity of fixed-length models", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/perplexity)
  Perplexity sliding window से कैसे compute होती है, और window संख्या को क्यों बदलती है। इस्तेमाल: perplexity को इस तरह compute करना कि दो runs तुलनीय हों।
- [पेपर: "Quantization Hurts Reasoning? An Empirical Study on Quantized Reasoning Models", Liu et al., 2025](https://arxiv.org/abs/2504.04823)
  Math, science और code benchmarks पर weight, KV-cache और activation quantization के आर-पार quantized reasoning models, जो पाता है कि W8A8 और W4A16 lossless हो सकते हैं और कम bit widths जोखिम भरे। इस्तेमाल: क्या आम 4-bit वाला जवाब reasoning model के लिए टिकता है।
- [दस्तावेज़: llama.cpp perplexity tool README, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/perplexity/README.md)
  16-bit logits के मुक़ाबले perplexity, KL divergence और top-token agreement के आँकड़े, GGUF types की table के साथ। इस्तेमाल: quantized GGUF को उसकी baseline के मुक़ाबले perplexity से आगे मापना।

## कमियाँ

- GPU generations में से कौन-सी किन formats में natively compute करती है इसकी कोई एक vendor-neutral, मौजूदा table नहीं है। पाठ 20 vendor पन्नों और serving-engine की support matrices पर निर्भर करता है, जो हर release के साथ बदलती हैं।
