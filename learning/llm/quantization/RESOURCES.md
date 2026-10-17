---
title: Resources
description: "Trusted sources for LLM quantization"
type: resources
---

# Quantization Resources

## Knowledge

### Foundations

- [Paper: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295)
  A textbook-length introduction from Qualcomm AI Research: the hardware motivation, the uniform affine quantizer, range setting, granularity, PTQ and QAT pipelines, and a debugging workflow. Use for: the mapping and range choice in stages 2 and 6, from the source rather than a summary.
- [Paper: "A Survey of Quantization Methods for Efficient Neural Network Inference", Gholami et al., 2021](https://arxiv.org/abs/2103.13630)
  A broad survey of uniform and non-uniform quantizers, granularity, PTQ against QAT, and mixed precision. Use for: placing a method in the wider family before reading its own paper.
- [Paper: "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference", Jacob et al., 2017](https://arxiv.org/abs/1712.05877)
  The integer-only inference scheme behind most int8 deployments: the affine mapping with an exactly representable zero, and training with simulated quantization. Use for: where the scale and zero-point convention comes from.

### Number formats

- [Paper: "Mixed Precision Training", Micikevicius et al., 2017](https://arxiv.org/abs/1710.03740)
  Training in fp16 with an fp32 master copy and loss scaling, and why fp16's narrow range makes the scaling necessary. Use for: what fp16's five exponent bits cost.
- [Paper: "A Study of BFLOAT16 for Deep Learning Training", Kalamkar et al., 2019](https://arxiv.org/abs/1905.12322)
  The case for bf16, which keeps fp32's exponent and drops mantissa bits. Use for: why range mattered more than precision for training.
- [Paper: "FP8 Formats for Deep Learning", Micikevicius et al., 2022](https://arxiv.org/abs/2209.05433)
  The E4M3 and E5M2 eight-bit floating-point encodings, their special values, and results training and inferring in them. Use for: what each fp8 variant is for.
- [Paper: "Microscaling Data Formats for Deep Learning", Rouhani et al., 2023](https://arxiv.org/abs/2310.10537)
  Block-scaled formats in which a block of narrow elements shares one power-of-two scale, the basis of the OCP MX formats. Use for: how MXFP4 and its relatives store a block.
- [Article: "Introducing NVFP4 for Efficient and Accurate Low-Precision Inference", NVIDIA Technical Blog](https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/)
  One vendor's 4-bit floating-point format with a smaller block and a finer scale than MXFP4. Use for: how NVFP4 differs from MXFP4, read as vendor documentation.

### Outliers

- [Paper: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., 2022](https://arxiv.org/abs/2208.07339)
  Discovers the outlier feature dimensions that break int8 in large transformers, and keeps them in 16-bit with a mixed-precision decomposition. Use for: where outliers appear and the first fix.
- [Paper: "Massive Activations in Large Language Models", Sun et al., 2024](https://arxiv.org/abs/2402.17762)
  Single activations orders of magnitude larger than the rest, at fixed dimensions and specific tokens, acting like learned biases. Use for: the second outlier pattern and why it is not noise.
- [Paper: "Quantizable Transformers: Removing Outliers by Helping Attention Heads Do Nothing", Bondarenko et al., 2023](https://arxiv.org/abs/2306.12929)
  Ties outliers to attention heads learning to do nothing, and removes them with an architecture change during training. Use for: why outliers exist at all.

### Post-training quantization

- [Paper: "The case for 4-bit precision: k-bit Inference Scaling Laws", Dettmers and Zettlemoyer, 2022](https://arxiv.org/abs/2212.09720)
  More than 35,000 zero-shot experiments across bit widths, data types and block sizes, finding 4 bits almost universally optimal for a fixed number of model bits, helped only by small blocks and the choice of data type. Use for: why 4-bit weights became the default, and what block size buys.
- [Paper: "Up or Down? Adaptive Rounding for Post-Training Quantization", Nagel et al., 2020](https://arxiv.org/abs/2004.10568)
  Shows rounding each weight to its nearest level is not optimal for the layer's output, and learns the rounding direction instead. Use for: why round-to-nearest leaves accuracy behind.
- [Paper: "Optimal Brain Compression", Frantar and Alistarh, 2022](https://arxiv.org/abs/2208.11580)
  The exact layer-wise quantization method that GPTQ makes fast, with the update that spends one weight's error on the others. Use for: GPTQ's lineage.
- [Paper: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2022](https://arxiv.org/abs/2210.17323)
  One-shot 3 and 4-bit weight quantization using approximate second-order information, at the scale of 175B-parameter models. Use for: how GPTQ works and what its calibration set is.
- [Paper: "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration", Lin et al., 2023](https://arxiv.org/abs/2306.00978)
  Finds that a small fraction of weight channels matter most, identified by activation magnitude, and protects them by per-channel scaling rather than mixed precision. Use for: how AWQ works and why it needs no backpropagation.
- [Paper: "SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models", Xiao et al., 2022](https://arxiv.org/abs/2211.10438)
  Migrates activation outliers into the weights with a mathematically equivalent per-channel scale, enabling W8A8. Use for: weight-and-activation quantization at 8 bits.
- [Paper: "QuaRot: Outlier-Free 4-Bit Inference in Rotated LLMs", Ashkboos et al., 2024](https://arxiv.org/abs/2404.00456)
  Rotates hidden states with Hadamard transforms so weights, activations and the KV cache all quantize to 4 bits. Use for: how rotations remove outliers.
- [Paper: "SpinQuant: LLM Quantization with Learned Rotations", Liu et al., 2024](https://arxiv.org/abs/2405.16406)
  Learns the rotation matrices instead of fixing them, and shows that random rotations vary widely in quality. Use for: why the choice of rotation matters.
- [Paper: "KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache", Liu et al., 2024](https://arxiv.org/abs/2402.02750)
  Finds keys should be quantized per channel and values per token, and does both at 2 bits. Use for: the axis choice in KV-cache quantization.
- [Paper: "KVQuant: Towards 10 Million Context Length LLM Inference with KV Cache Quantization", Hooper et al., 2024](https://arxiv.org/abs/2401.18079)
  Per-channel key quantization before the rotary embedding, non-uniform types and outlier handling for very long contexts. Use for: what KV-cache quantization buys at long context.
- [Repo: gptq, IST-DASLab](https://github.com/IST-DASLab/gptq)
  The GPTQ authors' reference implementation, whose README documents `--act-order` (quantize columns in order of decreasing activation size), `--true-sequential` and `--static-groups`. Use for: act-order and the `g_idx` tensor, which the paper does not describe.

### Quantization-aware training

- [Paper: "Estimating or Propagating Gradients Through Stochastic Neurons for Conditional Computation", Bengio et al., 2013](https://arxiv.org/abs/1308.3432)
  Introduces and compares estimators for gradients through hard thresholds, including the straight-through estimator. Use for: where the STE comes from.
- [Paper: "LLM-QAT: Data-Free Quantization Aware Training for Large Language Models", Liu et al., 2023](https://arxiv.org/abs/2305.17888)
  QAT on LLMs using data the model generates itself, including KV-cache quantization, compared against PTQ at 4 bits. Use for: what QAT recovers on an LLM and at what cost.
- [Paper: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., 2023](https://arxiv.org/abs/2305.14314)
  NF4, double quantization and training adapters through a frozen 4-bit base. Use for: the boundary with QAT, and the source the finetuning track teaches from.
- [Article: "Quantization-Aware Training for Large Language Models with PyTorch", PyTorch Blog, 2024](https://pytorch.org/blog/quantization-aware-training/)
  The torchao QAT flow on Llama 2 and Llama 3, with measured recovery against PTQ and the fine-tuning overhead of fake quantization. Use for: what QAT recovers and costs on a real LLM, read as one team's measurements.

### Hardware and serving

- [Paper: "MARLIN: Mixed-Precision Auto-Regressive Parallel Inference on Large Language Models", Frantar et al., 2024](https://arxiv.org/abs/2408.11743)
  A 4-bit-weight, 16-bit-activation GPU kernel and an analysis of when weight-only quantization speeds up batched decode. Use for: why the speed-up depends on batch size.
- [Paper: "QServe: W4A8KV4 Quantization and System Co-design for Efficient LLM Serving", Lin et al., 2024](https://arxiv.org/abs/2405.04532)
  Shows dequantization overhead can erase the gain of 4-bit schemes on GPUs and co-designs a format and kernel to avoid it. Use for: why fewer bits is not automatically faster.
- [Docs: "Quantization", vLLM](https://docs.vllm.ai/en/latest/features/quantization/)
  The schemes one serving engine supports and on which hardware. Use for: checking whether a scheme has a kernel before choosing it.
- [Docs: "Quantized KV Cache", vLLM](https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/)
  The fp8 KV cache: per-tensor or per-head scales, default scales without calibration, and calibrating them with llm-compressor. Use for: what an 8-bit KV cache needs in practice.
- [Docs: "Quantization overview", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/overview)
  The quantization backends Transformers integrates and how to choose between them. Use for: a map of the tooling.
- [Repo: llm-compressor, vLLM project](https://github.com/vllm-project/llm-compressor)
  A library that applies GPTQ, AWQ, SmoothQuant and FP8 recipes and writes checkpoints vLLM loads. Use for: running PTQ end to end on a real model.
- [Repo: compressed-tensors, Neural Magic](https://github.com/neuralmagic/compressed-tensors)
  The safetensors extension that records a checkpoint's quantization scheme in its config. Use for: what a quantized safetensors checkpoint stores.
- [Docs: "int8 W8A8" example, llm-compressor](https://github.com/vllm-project/llm-compressor/blob/main/examples/quantization_w8a8_int8/README.md)
  A worked W8A8 int8 recipe: SmoothQuant, then GPTQ with channelwise weight scales, then dynamic per-token activation scales. Use for: running SmoothQuant on a real model.
- [Docs: "Choosing a dataset", LLM Compressor](https://docs.vllm.ai/projects/llm-compressor/en/latest/steps/choosing-dataset/)
  Which algorithms need a calibration set, matching its domain to the target use, and typical sizes. Use for: practical guidance on a calibration set.
- [Docs: "GPTQ", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/gptq)
  Running GPTQ through `GPTQConfig` with a built-in dataset or your own text. Use for: quantizing with GPTQ from Transformers.
- [Docs: "AWQ", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/awq)
  Loading AWQ checkpoints and the `quantization_config` keys an AWQ checkpoint records. Use for: reading an AWQ checkpoint's config.
- [Docs: "bitsandbytes", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
  How Transformers loads 8-bit and 4-bit bitsandbytes models, including the compute data type. Use for: seeing that stored 4-bit weights are computed in a higher precision.
- [Docs: "NVIDIA A100 Tensor Core GPU" datasheet, NVIDIA](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-nvidia-us-2188504-web.pdf)
  The A100's tensor-core throughput per format and its memory bandwidth. Use for: the Ampere numbers in a roofline, read as vendor documentation.
- [Docs: "NVIDIA Ada GPU Architecture" whitepaper, NVIDIA](https://images.nvidia.com/aem-dam/Solutions/Data-Center/l4/nvidia-ada-gpu-architecture-whitepaper-v2.1.pdf)
  The Ada tensor cores and their FP8 support. Use for: which inference GPUs have FP8 tensor cores, read as vendor documentation.
- [Docs: "NVIDIA H100 Tensor Core GPU", NVIDIA](https://www.nvidia.com/en-us/data-center/h100/)
  The H100 specification table with FP8 and INT8 tensor-core rows and memory bandwidth. Use for: Hopper figures, read as vendor documentation.
- [Article: "NVIDIA Hopper Architecture In-Depth", NVIDIA Technical Blog](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/)
  The FP8 tensor cores and Transformer Engine introduced with Hopper. Use for: when FP8 compute arrived in NVIDIA data-centre GPUs, read as vendor documentation.

### File formats

- [Docs: "Safetensors", Hugging Face](https://huggingface.co/docs/safetensors/index)
  The tensor file format most checkpoints ship in, and what it does and does not store. Use for: the container a quantization config sits beside.
- [Docs: "GGUF", Hugging Face Hub](https://huggingface.co/docs/hub/gguf)
  An overview of the GGUF format and a table of its quantization types with their bit layouts. Use for: decoding a GGUF type name.
- [Docs: llama.cpp quantize tool README, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md)
  How llama.cpp converts a model to its quant types, the list of types, and how the importance matrix is passed in. Use for: producing a GGUF quantization yourself.
- [Repo: safetensors, Hugging Face](https://github.com/huggingface/safetensors)
  The byte-level format: an 8-byte little-endian header length, a JSON header of names, dtypes, shapes and offsets, then the data. Use for: reading a checkpoint's header without loading its tensors.
- [Docs: "compressed-tensors", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/compressed_tensors)
  Loading compressed-tensors checkpoints, with an FP8 `config_groups` example and its tensor listing. Use for: reading a compressed-tensors config and its scale tensors.
- [Model card: "TinyLlama-1.1B-Chat-v1.0-GPTQ", TheBloke](https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GPTQ)
  A small public 4-bit GPTQ checkpoint whose card explains bits, group size, act order and damping. Use for: a real checkpoint to inspect.
- [Source: ggml-common.h, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-common.h)
  The C struct for every GGUF block type. Use for: deriving a type's bits per weight from its layout rather than quoting it.
- [Pull request: "k-quants", ikawrakow, llama.cpp, 2023](https://github.com/ggml-org/llama.cpp/pull/1684)
  Introduces the k-quants, the type-0 and type-1 naming and the original S, M and L mixtures. Use for: what the suffixes meant when they were introduced.
- [Pull request: "Importance Matrix calculation", ikawrakow, llama.cpp, 2024](https://github.com/ggml-org/llama.cpp/pull/4861)
  Derives the importance matrix from activations on a calibration text and uses it to weight rounding error. Use for: why an importance matrix is a calibration set.
- [Docs: llama.cpp imatrix tool README, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/imatrix/README.md)
  How to compute an importance matrix and pass it to the quantize tool. Use for: producing one yourself.

### Measuring quality loss

- [Paper: "Accuracy is Not All You Need", Dutta et al., 2024](https://arxiv.org/abs/2407.09141)
  Shows a quantized model can match its baseline's accuracy while changing many individual answers, and proposes flips and KL divergence as distance metrics. Use for: why an unchanged average can hide a changed model.
- [Paper: "Give Me BF16 or Give Me Death? Accuracy-Performance Trade-Offs in LLM Quantization", Kurtic et al., 2024](https://arxiv.org/abs/2411.02355)
  Over half a million evaluations of FP8, INT8 and INT4 schemes across Llama 3.1 sizes and tasks, with deployment guidance per scheme. Use for: what each scheme costs, measured carefully.
- [Paper: "Scaling Laws for Precision", Kumar et al., 2024](https://arxiv.org/abs/2411.04330)
  Finds that post-training quantization degrades a model more the more data it was trained on. Use for: why the usual 4-bit answer can fail on a heavily trained model.
- [Repo: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  The harness most quantization papers report task accuracy with. Use for: running the same tasks on a baseline and a quantized model.
- [Docs: "Perplexity of fixed-length models", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/perplexity)
  How perplexity is computed with a sliding window, and why the window changes the number. Use for: computing perplexity so two runs are comparable.
- [Paper: "Quantization Hurts Reasoning? An Empirical Study on Quantized Reasoning Models", Liu et al., 2025](https://arxiv.org/abs/2504.04823)
  Quantized reasoning models across weight, KV-cache and activation quantization on math, science and code benchmarks, finding W8A8 and W4A16 can be lossless and lower bit widths risky. Use for: whether the usual 4-bit answer holds for a reasoning model.
- [Docs: llama.cpp perplexity tool README, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/perplexity/README.md)
  Perplexity, KL divergence and top-token agreement statistics against 16-bit logits, with a table of GGUF types. Use for: measuring a quantized GGUF against its baseline beyond perplexity.

## Gaps

- No single vendor-neutral, current table of which GPU generations compute natively in which formats. Lesson 20 relies on vendor pages and on serving-engine support matrices, which change with each release.
