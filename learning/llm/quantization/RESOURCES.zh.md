---
title: "资源"
description: "LLM 量化的可信资料来源"
type: resources
---

# 量化资源

## 知识

### 基础

- [论文：“A White Paper on Neural Network Quantization”，Nagel 等，2021](https://arxiv.org/abs/2106.08295)
  来自 Qualcomm AI Research 的教科书篇幅的入门介绍：硬件动机、均匀仿射量化器、范围设定、量化粒度、训练后量化和量化感知训练的流程，以及一套调试工作流。用途：第 2 和第 6 阶段中的映射与范围选择，直接读原始来源，而不是读摘要。
- [论文：“A Survey of Quantization Methods for Efficient Neural Network Inference”，Gholami 等，2021](https://arxiv.org/abs/2103.13630)
  对均匀与非均匀量化器、量化粒度、训练后量化与量化感知训练的对比，以及混合精度的一份全面综述。用途：在读某个方法自己的论文之前，先把它放进更大的家族里。
- [论文：“Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference”，Jacob 等，2017](https://arxiv.org/abs/1712.05877)
  大多数 int8 部署背后的纯整数推理方案：零能被精确表示的仿射映射，以及带模拟量化的训练。用途：缩放因子与零点的约定从何而来。

### 数值格式

- [论文：“Mixed Precision Training”，Micikevicius 等，2017](https://arxiv.org/abs/1710.03740)
  用 fp16 训练，配 fp32 主副本和损失缩放，以及为什么 fp16 的窄范围使缩放成为必需。用途：fp16 的五个指数位要付出什么代价。
- [论文：“A Study of BFLOAT16 for Deep Learning Training”，Kalamkar 等，2019](https://arxiv.org/abs/1905.12322)
  支持 bf16 的理由，它保留 fp32 的指数，舍去尾数位。用途：为什么对训练来说，范围比精度更要紧。
- [论文：“FP8 Formats for Deep Learning”，Micikevicius 等，2022](https://arxiv.org/abs/2209.05433)
  E4M3 和 E5M2 两种八位浮点编码，它们的特殊值，以及用它们做训练和推理的结果。用途：每种 fp8 变体是做什么用的。
- [论文：“Microscaling Data Formats for Deep Learning”，Rouhani 等，2023](https://arxiv.org/abs/2310.10537)
  块缩放格式，一块窄元素共用一个 2 的幂缩放因子，这是 OCP MX 格式的基础。用途：MXFP4 及其同类格式如何存储一个块。
- [文章：“Introducing NVFP4 for Efficient and Accurate Low-Precision Inference”，NVIDIA Technical Blog](https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/)
  一家厂商的 4 位浮点格式，块比 MXFP4 更小，缩放因子更精细。用途：NVFP4 与 MXFP4 有何不同，请当作厂商文档来读。

### 离群值

- [论文：“LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale”，Dettmers 等，2022](https://arxiv.org/abs/2208.07339)
  发现了让大型 Transformer 的 int8 出问题的离群特征维度，并用混合精度分解把它们保留在 16 位。用途：离群值出现在哪里，以及第一种修复办法。
- [论文：“Massive Activations in Large Language Models”，Sun 等，2024](https://arxiv.org/abs/2402.17762)
  比其余激活值大好几个数量级的单个激活值，出现在固定的维度和特定的 token 上，其作用像学出来的偏置。用途：第二种离群值模式，以及它为什么不是噪声。
- [论文：“Quantizable Transformers: Removing Outliers by Helping Attention Heads Do Nothing”，Bondarenko 等，2023](https://arxiv.org/abs/2306.12929)
  把离群值与学会什么都不做的注意力头联系起来，并通过训练期间的架构改动去掉它们。用途：离群值究竟为什么会存在。

### 训练后量化

- [论文：“The case for 4-bit precision: k-bit Inference Scaling Laws”，Dettmers 与 Zettlemoyer，2022](https://arxiv.org/abs/2212.09720)
  跨位宽、数据类型和块大小的 35,000 多次零样本实验，发现在模型总位数固定时，4 位几乎普遍是最优的，只有小块和数据类型的选择有帮助。用途：4 位权重为什么成了默认选择，以及块大小能买到什么。
- [论文：“Up or Down? Adaptive Rounding for Post-Training Quantization”，Nagel 等，2020](https://arxiv.org/abs/2004.10568)
  表明把每个权重舍入到它最近的档位，对这一层的输出并不是最优的，并转而学习舍入的方向。用途：就近舍入为什么会让精度白白丢掉。
- [论文：“Optimal Brain Compression”，Frantar 与 Alistarh，2022](https://arxiv.org/abs/2208.11580)
  GPTQ 使之变快的那个精确的逐层量化方法，带有把一个权重的误差花在其他权重上的更新。用途：GPTQ 的来龙去脉。
- [论文：“GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers”，Frantar 等，2022](https://arxiv.org/abs/2210.17323)
  利用近似的二阶信息做一次性的 3 位和 4 位权重量化，规模达 175B 参数的模型。用途：GPTQ 如何工作，以及它的校准集是什么。
- [论文：“AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration”，Lin 等，2023](https://arxiv.org/abs/2306.00978)
  发现一小部分权重通道最重要，通过激活值幅值来识别它们，并用逐通道缩放而不是混合精度来保护它们。用途：AWQ 如何工作，以及它为什么不需要反向传播。
- [论文：“SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models”，Xiao 等，2022](https://arxiv.org/abs/2211.10438)
  用一个数学上等价的逐通道缩放因子，把激活值的离群值迁移到权重中，使 W8A8 成为可能。用途：8 位的权重加激活值量化。
- [论文：“QuaRot: Outlier-Free 4-Bit Inference in Rotated LLMs”，Ashkboos 等，2024](https://arxiv.org/abs/2404.00456)
  用哈达玛变换旋转隐藏状态，使权重、激活值和 KV 缓存都能量化到 4 位。用途：旋转如何去掉离群值。
- [论文：“SpinQuant: LLM Quantization with Learned Rotations”，Liu 等，2024](https://arxiv.org/abs/2405.16406)
  学习旋转矩阵，而不是把它们固定下来，并表明随机旋转的质量差别很大。用途：为什么旋转的选择很重要。
- [论文：“KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache”，Liu 等，2024](https://arxiv.org/abs/2402.02750)
  发现键应当逐通道量化，值应当逐 token 量化，并且两者都做到了 2 位。用途：KV 缓存量化中轴的选择。
- [论文：“KVQuant: Towards 10 Million Context Length LLM Inference with KV Cache Quantization”，Hooper 等，2024](https://arxiv.org/abs/2401.18079)
  在旋转位置嵌入之前做逐通道的键量化，针对超长上下文采用非均匀类型和离群值处理。用途：KV 缓存量化在长上下文下能买到什么。
- [仓库：gptq，IST-DASLab](https://github.com/IST-DASLab/gptq)
  GPTQ 作者的参考实现，它的 README 记载了 `--act-order`（按激活值从大到小的顺序量化各列）、`--true-sequential` 和 `--static-groups`。用途：act-order 和 `g_idx` 张量，论文中没有描述它们。

### 量化感知训练

- [论文：“Estimating or Propagating Gradients Through Stochastic Neurons for Conditional Computation”，Bengio 等，2013](https://arxiv.org/abs/1308.3432)
  提出并比较了穿过硬阈值的梯度估计器，包括直通估计器。用途：STE 从何而来。
- [论文：“LLM-QAT: Data-Free Quantization Aware Training for Large Language Models”，Liu 等，2023](https://arxiv.org/abs/2305.17888)
  在 LLM 上用模型自己生成的数据做 QAT，包括 KV 缓存量化，并在 4 位下与训练后量化做比较。用途：QAT 在 LLM 上能挽回什么，以及代价是什么。
- [论文：“QLoRA: Efficient Finetuning of Quantized LLMs”，Dettmers 等，2023](https://arxiv.org/abs/2305.14314)
  NF4、双重量化，以及穿过冻结的 4 位基础模型来训练适配器。用途：与 QAT 的边界，以及微调系列所依据的来源。
- [文章：“Quantization-Aware Training for Large Language Models with PyTorch”，PyTorch Blog，2024](https://pytorch.org/blog/quantization-aware-training/)
  在 Llama 2 和 Llama 3 上的 torchao QAT 流程，带有对照训练后量化的实测恢复率，以及伪量化的微调开销。用途：QAT 在真实的 LLM 上能挽回什么、花费什么，请当作一个团队的度量来读。

### 硬件与服务

- [论文：“MARLIN: Mixed-Precision Auto-Regressive Parallel Inference on Large Language Models”，Frantar 等，2024](https://arxiv.org/abs/2408.11743)
  一个 4 位权重、16 位激活值的 GPU 内核，以及对仅权重量化何时加快批量解码的分析。用途：为什么加速取决于批大小。
- [论文：“QServe: W4A8KV4 Quantization and System Co-design for Efficient LLM Serving”，Lin 等，2024](https://arxiv.org/abs/2405.04532)
  表明反量化的开销可以抹掉 GPU 上 4 位方案的收益，并协同设计一种格式和内核来避免它。用途：为什么位数更少并不自动就更快。
- [文档：“Quantization”，vLLM](https://docs.vllm.ai/en/latest/features/quantization/)
  一个服务引擎支持哪些方案，以及在哪些硬件上。用途：在选择一种方案之前，核查它有没有内核。
- [文档：“Quantized KV Cache”，vLLM](https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/)
  fp8 的 KV 缓存：逐张量或逐头的缩放因子，没有校准时的默认缩放因子，以及用 llm-compressor 校准它们。用途：8 位 KV 缓存在实践中需要什么。
- [文档：“Quantization overview”，Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/overview)
  Transformers 集成的各种量化后端，以及如何在它们之间选择。用途：工具的一张地图。
- [仓库：llm-compressor，vLLM project](https://github.com/vllm-project/llm-compressor)
  一个应用 GPTQ、AWQ、SmoothQuant 和 FP8 配方，并写出 vLLM 可以加载的检查点的库。用途：在真实模型上端到端运行训练后量化。
- [仓库：compressed-tensors，Neural Magic](https://github.com/neuralmagic/compressed-tensors)
  在配置里记录检查点量化方案的 safetensors 扩展。用途：量化的 safetensors 检查点存了什么。
- [文档：“int8 W8A8”示例，llm-compressor](https://github.com/vllm-project/llm-compressor/blob/main/examples/quantization_w8a8_int8/README.md)
  一份完整的 W8A8 int8 配方：先 SmoothQuant，再用逐通道权重缩放因子的 GPTQ，然后是动态逐 token 的激活值缩放因子。用途：在真实模型上运行 SmoothQuant。
- [文档：“Choosing a dataset”，LLM Compressor](https://docs.vllm.ai/projects/llm-compressor/en/latest/steps/choosing-dataset/)
  哪些算法需要校准集，让它的领域与目标用途相匹配，以及典型的大小。用途：关于校准集的实用指导。
- [文档：“GPTQ”，Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/gptq)
  通过 `GPTQConfig` 运行 GPTQ，使用内置数据集或你自己的文本。用途：从 Transformers 里用 GPTQ 量化。
- [文档：“AWQ”，Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/awq)
  加载 AWQ 检查点，以及 AWQ 检查点所记录的 `quantization_config` 键。用途：读懂 AWQ 检查点的配置。
- [文档：“bitsandbytes”，Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
  Transformers 如何加载 8 位和 4 位的 bitsandbytes 模型，包括计算数据类型。用途：看出存储的 4 位权重是以更高的精度计算的。
- [文档：“NVIDIA A100 Tensor Core GPU”数据手册，NVIDIA](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-nvidia-us-2188504-web.pdf)
  A100 每种格式的张量核心吞吐量及其内存带宽。用途：屋顶线中的 Ampere 数字，请当作厂商文档来读。
- [文档：“NVIDIA Ada GPU Architecture”白皮书，NVIDIA](https://images.nvidia.com/aem-dam/Solutions/Data-Center/l4/nvidia-ada-gpu-architecture-whitepaper-v2.1.pdf)
  Ada 的张量核心及其对 FP8 的支持。用途：哪些推理 GPU 有 FP8 张量核心，请当作厂商文档来读。
- [文档：“NVIDIA H100 Tensor Core GPU”，NVIDIA](https://www.nvidia.com/en-us/data-center/h100/)
  H100 的规格表，带 FP8 和 INT8 张量核心行以及内存带宽。用途：Hopper 的数字，请当作厂商文档来读。
- [文章：“NVIDIA Hopper Architecture In-Depth”，NVIDIA Technical Blog](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/)
  随 Hopper 引入的 FP8 张量核心和 Transformer Engine。用途：FP8 计算是什么时候来到 NVIDIA 数据中心 GPU 的，请当作厂商文档来读。

### 文件格式

- [文档：“Safetensors”，Hugging Face](https://huggingface.co/docs/safetensors/index)
  大多数检查点所用的张量文件格式，以及它存什么、不存什么。用途：量化配置所依附的那个容器。
- [文档：“GGUF”，Hugging Face Hub](https://huggingface.co/docs/hub/gguf)
  对 GGUF 格式的概述，以及一张带位布局的量化类型表。用途：解读一个 GGUF 类型名。
- [文档：llama.cpp quantize 工具 README，ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md)
  llama.cpp 如何把一个模型转换成它的量化类型，类型清单，以及重要性矩阵如何传入。用途：自己生成一个 GGUF 量化。
- [仓库：safetensors，Hugging Face](https://github.com/huggingface/safetensors)
  字节级的格式：一个 8 字节的小端头部长度，一个包含名称、dtype、形状和偏移量的 JSON 头部，然后是数据。用途：不加载张量，只读一个检查点的头部。
- [文档：“compressed-tensors”，Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/compressed_tensors)
  加载 compressed-tensors 检查点，带一个 FP8 的 `config_groups` 示例及其张量清单。用途：读懂 compressed-tensors 的配置及其缩放因子张量。
- [模型卡：“TinyLlama-1.1B-Chat-v1.0-GPTQ”，TheBloke](https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GPTQ)
  一个小型的公开 4 位 GPTQ 检查点，它的模型卡解释了位数、分组大小、act order 和阻尼。用途：一个可供检查的真实检查点。
- [源码：ggml-common.h，ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-common.h)
  每一种 GGUF 块类型的 C 结构体。用途：根据布局推导一种类型每个权重的位数，而不是照搬引用。
- [拉取请求：“k-quants”，ikawrakow，llama.cpp，2023](https://github.com/ggml-org/llama.cpp/pull/1684)
  引入了 k-quants、type-0 与 type-1 的命名，以及最初的 S、M 和 L 混合。用途：这些后缀在引入时是什么意思。
- [拉取请求：“Importance Matrix calculation”，ikawrakow，llama.cpp，2024](https://github.com/ggml-org/llama.cpp/pull/4861)
  从校准文本上的激活值推导出重要性矩阵，并用它给舍入误差加权。用途：为什么重要性矩阵是一个校准集。
- [文档：llama.cpp imatrix 工具 README，ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/imatrix/README.md)
  如何计算重要性矩阵，并把它传给 quantize 工具。用途：自己生成一个。

### 度量质量损失

- [论文：“Accuracy is Not All You Need”，Dutta 等，2024](https://arxiv.org/abs/2407.09141)
  表明一个量化模型可以与它的基线准确率相当，却改变了许多个别答案，并提出翻转和 KL 散度作为距离度量。用途：为什么不变的平均值可以掩盖一个已经改变的模型。
- [论文：“Give Me BF16 or Give Me Death? Accuracy-Performance Trade-Offs in LLM Quantization”，Kurtic 等，2024](https://arxiv.org/abs/2411.02355)
  跨 Llama 3.1 各规模和各任务，对 FP8、INT8 和 INT4 方案的五十多万次评测，并给出每种方案的部署指导。用途：每种方案的代价是什么，经过细致的度量。
- [论文：“Scaling Laws for Precision”，Kumar 等，2024](https://arxiv.org/abs/2411.04330)
  发现模型训练所用的数据越多，训练后量化对它的损害越大。用途：为什么惯常的 4 位答案在训练了大量数据的模型上可能失效。
- [仓库：lm-evaluation-harness，EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  大多数量化论文用来报告任务准确率的测评框架。用途：在基线和量化模型上运行同样的任务。
- [文档：“Perplexity of fixed-length models”，Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/perplexity)
  如何用滑动窗口计算困惑度，以及为什么窗口会改变数字。用途：计算困惑度，使两次运行可以比较。
- [论文：“Quantization Hurts Reasoning? An Empirical Study on Quantized Reasoning Models”，Liu 等，2025](https://arxiv.org/abs/2504.04823)
  在数学、科学和代码基准上，对权重、KV 缓存和激活值量化的量化推理模型的研究，发现 W8A8 和 W4A16 可以无损，更低的位宽则有风险。用途：惯常的 4 位答案对推理模型是否成立。
- [文档：llama.cpp 困惑度工具 README，ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/perplexity/README.md)
  对照 16 位 logit 的困惑度、KL 散度和头部 token 一致性统计量，附有一张 GGUF 类型表。用途：在困惑度之外，对照基线度量一个量化的 GGUF。

## 空白

- 没有一张单一的、与厂商无关的、最新的表，说明哪些 GPU 代际以哪些格式原生计算。第 20 课依靠的是厂商页面和服务引擎的支持矩阵，它们随每个版本而变。
