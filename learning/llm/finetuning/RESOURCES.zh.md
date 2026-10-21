---
title: "资源"
description: "适配器微调的可信资料来源与社区"
type: resources
---

# 适配器微调资源

## 知识

### 三种方法

- [论文：“LoRA: Low-Rank Adaptation of Large Language Models”，Hu 等，arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
  最初的低秩适配器方法，以及它为什么有效的内在维度论证。用途：第 3 阶段，以及秩和 alpha 究竟控制什么。

- [论文：“QLoRA: Efficient Finetuning of Quantized LLMs”，Dettmers 等，arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
  NF4、双重量化和分页优化器，内存核算写得清清楚楚。用途：第 4 阶段，以及作为量化的基础模型在质量上付出什么代价的参照。请阅读局限性一节。

- [论文：“DoRA: Weight-Decomposed Low-Rank Adaptation”，Liu 等，arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
  把权重拆成幅度和方向，并适配方向。用途：第 5 阶段。第 4 节关于全量微调和 LoRA 如何移动这两个量的分析，才是真正的论证。

- [论文：“Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning”，Aghajanyan 等，arXiv:2012.13255](https://arxiv.org/abs/2012.13255)
  适配究竟为什么能存在于一个低维子空间里。用途：LoRA 底层的依据，而不是它的机制。

### 当前的实践

- [文档：“LoRA Without Regret”，Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
  所有线性层作为目标、秩又足够，就能追平与全量微调的差距，这一论证。用途：目标模块和秩的选择，以及作为任何新变体都必须打败的基线。它取代了沿袭自原始论文的只作用于注意力的惯例。

- [博客：“Practical Tips for Finetuning LLMs Using LoRA”，Sebastian Raschka，Ahead of AI](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms)
  对秩、alpha 和目标模块的消融实验，附实验过程。用途：拿测量结果去检验关于超参数的民间经验。

- [文档：PEFT，Hugging Face](https://huggingface.co/docs/peft)
  三种方法的参考实现，以及它们暴露出来的配置面。用途：一个超参数在实践中叫什么，以及哪些变体已经成熟到成为一个开关。与版本有关，所以要对照所安装的版本检查，而不是凭记忆。

- [文档：SFTTrainer，Hugging Face TRL](https://huggingface.co/docs/trl/main/en/sft_trainer)
  标准的监督微调循环及其数据集格式。用途：第 3 阶段及之后。与版本有关；参数名在不同版本之间变过。

### 基础

- [交互式：LLM Visualization，Brendan Bycroft](https://bbycroft.net/llm)
  逐步点开单个 token 的路径，附每个矩阵的参数量。用途：第 1 阶段，也是对“参数都在哪里”最好的现成回答。

- [博客：“The Illustrated Transformer”，Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
  对这个架构的标准的图示讲解。用途：块的结构还没有搞明白时的第 1 阶段。

- [文档：Chat Templates，Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
  对话如何被渲染成 token 序列，以及如何应用模型自己的模板。用途：微调中最常见的那种悄无声息的失败。

- [论文：“Decoupled Weight Decay Regularization”（AdamW），Loshchilov 和 Hutter，arXiv:1711.05101](https://arxiv.org/abs/1711.05101)
  这里用到的一切所用的优化器，以及它的权重衰减为什么与 Adam 的不同。用途：第 2 阶段的内存论证。

- [论文：“ZeRO: Memory Optimizations Toward Training Trillion Parameter Models”，Rajbhandari 等，arXiv:1910.02054](https://arxiv.org/abs/1910.02054)
  把权重、梯度和优化器状态作为不同内存类别的权威核算。用途：推导出每个参数十六字节这个数字。

- [论文：“Training Deep Nets with Sublinear Memory Cost”，Chen 等，arXiv:1604.06174](https://arxiv.org/abs/1604.06174)
  梯度检查点，以及它所做的用计算换内存的交易。用途：第 2 阶段，以及你会永远开着的那个设置。

- [博客：“A Recipe for Training Neural Networks”，Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
  如何做实验，才能让结果有意义。用途：第 3 阶段的诊断课，以及对两个样本过拟合的冒烟测试。

### 量化

- [论文：“LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale”，Dettmers 等，arXiv:2208.07339](https://arxiv.org/abs/2208.07339)
  离群特征问题，它让 Transformer 的量化比算术所显示的要难。用途：为什么分块胜过整张量。

- [文档：bitsandbytes quantization，Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
  4 位配置面在实践中的样子。用途：第 4 阶段的设置。

- [代码：bitsandbytes，bitsandbytes-foundation](https://github.com/bitsandbytes-foundation/bitsandbytes)
  `backends/` 目录是哪种硬件支持哪种运算的权威。用途：对照源码，而不是对照教程，来解决硬件支持的问题，在这个领域，教程通常已经过时。

### 数据与评测

- [论文：“LIMA: Less Is More for Alignment”，Zhou 等，arXiv:2305.11206](https://arxiv.org/abs/2305.11206)
  证据表明，一个小而精心挑选的数据集，胜过一个大而草率的，并且 SFT 主要教的是格式。用途：第 6 阶段的开场论证。

- [论文：“Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena”，Zheng 等，arXiv:2306.05685](https://arxiv.org/abs/2306.05685)
  把模型当评判者的评测，并刻画了它的偏差：位置、冗长、自我偏好。用途：自由形式生成的指标，以及为什么评判者需要对照人工标签来校准。

- [论文：“An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-tuning”，Luo 等，arXiv:2308.08747](https://arxiv.org/abs/2308.08747)
  遗忘是可度量的、常见的，而且不限于边缘情形。用途：向觉得回归测试集是额外负担的人，说明它的必要性。

- [论文：“Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To!”，Qi 等，arXiv:2310.03693](https://arxiv.org/abs/2310.03693)
  在良性数据上微调，安全行为也会退化。用途：为什么回归测试集必须包含拒答的用例。

- [代码：lm-evaluation-harness，EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  标准基准的实现，以及它们所记录的数据污染问题。用途：搭建评测，以及持怀疑态度地阅读已发表的分数。

### 部署

- [文档：LoRA adapters，vLLM](https://docs.vllm.ai/en/latest/features/lora.html)
  在生产中部署适配器，包括多适配器的路由。用途：第 7 阶段。对照所安装的版本，检查最大秩和最大适配器数的限制。

- [论文：“S-LoRA: Serving Thousands of Concurrent LoRA Adapters”，Sheng 等，arXiv:2311.03285](https://arxiv.org/abs/2311.03285)
  如何高效地把许多适配器，对着同一个共享的基础模型一起批处理。用途：理解为什么多适配器部署是已经解决的问题，而不是研究设想。

- [博客：“LLM Inference Performance Engineering: Best Practices”，Databricks](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices)
  预填充与解码，以及各自受什么限制。用途：第 7 阶段的成本算术。

### 替代方案

- [论文：“Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks”，Lewis 等，arXiv:2005.11401](https://arxiv.org/abs/2005.11401)
  当问题是知识时，通常应该优先选用的那种方法的权威陈述。用途：最后一课的论证，以及可信地提出反对微调的理由。

## 智慧（社区）

- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/)
  在消费级硬件上微调的人最集中的地方，涵盖每一种后端。用途：搜索在内存预算之内已经行得通的做法、哪些民间经验值得检验，以及对新方法的复现报告。读存档；发帖是练习，不是来源。

- [Hugging Face Forums](https://discuss.huggingface.co/)
  可搜索、有存档，库的作者也在场。用途：文档含糊不清的 PEFT、TRL 和 `transformers` 的行为。

- [EleutherAI Blog](https://blog.eleuther.ai/)
  来自一个批判性地阅读自己领域的团体的文章，包括负面结果。用途：第 5 阶段和第 7 阶段中，关于一个声称的结果是否能够推广的判断。这类讨论最先发生在他们的 Discord 上，我们有意不列出它：那里说的话事后无法检索。

- [MLX Discussions, ml-explore/mlx](https://github.com/ml-explore/mlx/discussions)
  公开、可搜索，由维护者作答。用途：了解某个运算在 Apple Silicon 上是否已经支持，通常已经有人问过了。

## 空白

- 没有哪份资料追踪，在给定的 Python 版本和平台上，`torch`、PEFT、TRL 和量化库的哪些版本真正能一起工作。这比任何概念都更常卡住第一次运行，每个环境都必须对照发布说明来验证，而不是想当然。
- 4 位运算的硬件后端覆盖，每个版本都在变。没有哪份文档是可靠的；库的源码是唯一的权威，任何教程里关于硬件要求的说法，都应当视为已经过期。
- 目前还没有可信的资料，讲针对小模型的任务适配的评测设计。这是第 6 阶段最薄弱的一环，也是使命中最难的部分。一般的评测文献针对的是对基础模型做基准测试，而不是证明一个狭窄的适配器确实有帮助。
- 已发表的 LoRA 超参数建议，大多针对 7B 及以上的模型。很少有谈到它们是否适用于 1B 到 3B 级别的，而那恰恰是大多数人实际起步的地方。
- 没有调研到对 DoRA 的独立复现，达到 LoRA 和 QLoRA 所享有的规模。对它报告的增益，要当作需要在本地度量来看待。
- 没有选定关于约束解码的资料，而第 27 课把它推荐为 schema 有效性问题的正确答案。它被提到了，却没有资料作为依据。
