---
title: "资源"
description: "LLM 预训练的可信资料来源"
type: resources
---

# LLM 预训练资源

## 知识

- [论文：“Scaling Laws for Neural Language Models”，Kaplan 等，2020](https://arxiv.org/abs/2001.08361)
  拟合出损失与算力、参数量和数据量之间最初的幂律关系，并主张参数的增长应当快于数据。用途：阶段 3，作为后来被 Chinchilla 修正的基线。
- [论文：“Training Compute-Optimal Large Language Models”，Hoffmann 等，2022](https://arxiv.org/abs/2203.15556)
  Chinchilla 论文。用更广的扫描范围重新拟合缩放定律，发现参数和 token 应当一起放大，大约是每个参数二十个 token，推翻了 Kaplan 偏重参数的建议。用途：阶段 3 的核心结论，以及大多数现代训练运行实际使用的 token 预算。
- [论文：“ZeRO: Memory Optimizations Toward Training Trillion Parameter Models”，Rajbhandari 等，2019](https://arxiv.org/abs/1910.02054)
  定义了 ZeRO 的三个阶段：在数据并行设备之间依次对优化器状态、梯度和参数分片。用途：阶段 5 的核心技术，FSDP 实现的就是它。
- [文档：“Fully Sharded Data Parallel”，PyTorch](https://pytorch.org/docs/stable/fsdp.html)
  PyTorch 的 ZeRO 阶段 3 式分片的 API 参考，包括某一课的实验实际会用到的分片策略和包装策略。用途：阶段 5 的动手练习。
- [论文：“Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM”，Narayanan 等，2021](https://arxiv.org/abs/2104.04473)
  在一个系统中把张量并行、流水线并行和数据并行结合起来，并把每一种在吞吐量和内存上的权衡与其他几种对比实测。用途：阶段 6 的核心技术及其演算用的数字。
- [文档：“DeepSpeed”，Microsoft](https://github.com/microsoft/DeepSpeed)
  ZeRO 的第二个生产级实现，同时支持 3D 并行，它的配置示例可以让某一课把它当作继 FSDP 和 Megatron-LM 之后的第二个具体系统来引用。用途：阶段 5 和 6，用来交叉核对某个说法讲的是这项技术，而不是某一个库的 API。
- [论文：“The Pile: An 800GB Dataset of Diverse Text for Language Modeling”，Gao 等，2020](https://arxiv.org/abs/2101.00027)
  一份记录完整的预训练语料：放进了哪些来源、各占多大比例，以及原因。用途：阶段 1，作为把数据混合的决定明确写出来的一个演算范例。
- [论文：“Deduplicating Training Data Makes Language Models Better”，Lee 等，2021](https://arxiv.org/abs/2107.06499)
  表明近似重复的文本和很长的重复子串会造成逐字记忆，并给出两种去重技术（通过后缀数组做精确子串匹配，通过 MinHash 做近似重复匹配），每一种都在真实语料上做了度量。用途：阶段 1 的去重材料，附有具体的前后对比数字。
- [论文：“Language Models are Few-Shot Learners”，Brown 等，2020](https://arxiv.org/abs/2005.14165)
  GPT-3 论文。附录 A 记录了一条具体的质量过滤管线：训练一个分类器来区分精选文本和原始 Common Crawl，用它把 Common Crawl 重新采样，偏向得分更高的文档，此外还有一轮单独的模糊去重。用途：阶段 1 的质量过滤材料，是上面那篇去重论文本身没有提供的演算范例。
- [论文：“Neural Machine Translation of Rare Words with Subword Units”，Sennrich 等，2015](https://arxiv.org/abs/1508.07909)
  提出了用于子词分词的字节对编码，这是大多数现代分词器至今仍以之为基础的算法。用途：阶段 2 的核心算法。
- [论文：“SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing”，Kudo 和 Richardson，2018](https://arxiv.org/abs/1808.06226)
  把分词当作直接作用于原始文本的操作，不需要针对具体语言的预分词步骤，并介绍了作为 BPE 替代方案的 unigram 语言模型分词。用途：阶段 2 的第二种算法，以及词表大小的权衡。
- [论文：“Scaling Language Models: Methods, Analysis & Insights from Training Gopher”，Rae 等，2021](https://arxiv.org/abs/2112.11446)
  对一次大型训练运行详尽而坦诚的记述，包括损失尖峰和不稳定出现在哪里，以及作者是怎么处理的。用途：阶段 7 的核心案例研究。
- [论文：“LLaMA: Open and Efficient Foundation Language Models”，Touvron 等，2023](https://arxiv.org/abs/2302.13971)
  一份公开发表、可复现的训练配方：数据混合、分词器、调度和超参数，表述得足够清楚，可以拿某一课的说法去对照检查。用途：拿一份真实而完整的配方，交叉核对阶段 1 到 3 和阶段 7。
- [论文：“OPT: Open Pre-trained Transformer Language Models”，Zhang 等，2022](https://arxiv.org/abs/2205.01068)
  与一份公开的日志同时发布，记录了作者训练一个 175B 模型时实际遇到的基础设施问题：硬件故障、手动和自动重启、损失发散，以及针对每一种所采用的具体恢复步骤。用途：阶段 8 的核心案例研究，也是阶段 7 所讲的损失发散模式的第二个真实例子。
- [论文：“Don't Stop Pretraining: Adapt Language Models to Domains and Tasks”，Gururangan 等，2020](https://arxiv.org/abs/2004.10964)
  表明在一个现成的、覆盖面广的模型上继续预训练（领域自适应预训练），无论在高资源还是低资源的设置下，都能在四个领域、八项任务上持续提升目标领域的表现，而无需从头训练一个新模型。用途：阶段 10 的核心论据，即从零预训练通常是错误的默认选择。

## 空白

- OPT 的论文记录了真实的故障频率和恢复步骤，但没有给出具体的检查点间隔策略（检查点实际上多久保存一次）。阶段 8 中检查点频率的权衡，是从一般的工程推理出发来讲的，而不是依据某个明确的策略；如果有一份给出具体间隔的一手来源，会让它更站得住脚。
- GPT-3 基于分类器的过滤（2020）是目前列出的唯一一个质量过滤的演算范例。2023 年以来构建的语料（FineWeb、Dolma）过滤得要激进得多，也记录得更深入；一份较新的一手来源会让阶段 1 更站得住脚。
