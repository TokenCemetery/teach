---
title: "资源"
description: "Transformer 的可信资料来源"
type: resources
---

# Transformer 资源

## 知识

- [论文：“Attention Is All You Need”，Vaswani 等，2017](https://arxiv.org/abs/1706.03762)
  最初的 Transformer 论文：缩放点积注意力、多头注意力，以及这个工作区从原始张量推导出的完整的编码器-解码器块。用途：这个工作区所实现的每一个部件的原始定义。
- [文章：“The Illustrated Transformer”，Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
  对注意力和 Transformer 块的可视化的、以直觉为先的讲解，设计成在读论文的记号之前先读。用途：在动手实现任何东西之前，先建立一个可用的心智模型。
- [文章：“The Annotated Transformer”，Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
  这篇论文逐行的 PyTorch 实现，从原始张量运算出发，并与产生它们的方程直接对应。用途：把从零写的实现与参考实现逐行对照检查。
- [仓库：nanoGPT，Karpathy](https://github.com/karpathy/nanoGPT)
  一个 GPT 风格 Transformer 加上它的训练循环的极简、可读的 PyTorch 实现，小到可以完整读完。用途：使命的训练循环那一半，在块本身已经能工作之后。
- [视频：“Let's build GPT: from scratch, in code, spelled out”，Karpathy](https://www.youtube.com/watch?v=kCc8FmEb1nY)
  在屏幕上一步一步地，从原始张量搭建注意力和 GPT 的训练循环，推导每个部件，而不是直接展示成品。用途：在自己写代码之前或同时，看着推导发生。
- [文档：“Autograd mechanics”，PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
  对 PyTorch 的 autograd 究竟如何通过计算图计算梯度的官方解释。用途：理解反向传播对权重做了什么，而不只是调用 `.backward()`。
- [仓库：transformers，Hugging Face](https://github.com/huggingface/transformers)
  一个真实的生产环境模型库，在从零搭建的部件齐备之后很有用。用途：在为生产而不是为教学写的代码里，定位注意力、多头投影和 Transformer 块。
- [论文：“Layer Normalization”，Ba、Kiros 和 Hinton，2016](https://arxiv.org/abs/1607.06450)
  提出层归一化：在特征维度上对每个样本自己的激活值做归一化，与批大小无关，这与批归一化不同。用途：理解层归一化究竟计算什么，以及为什么它适合变长序列和较小的批大小。
- [论文：“On Layer Normalization in the Transformer Architecture”，Xiong 等，2020](https://arxiv.org/abs/2002.04745)
  比较把层归一化放在残差相加之后（原始论文的选择，后归一化）与放在每个子层之前、残差分支内部（前归一化），并说明为什么前归一化在更大的深度下训练得更稳定。用途：理解为什么尽管最初的 Transformer 论文用的是后归一化，当前大多数大模型仍使用前归一化。
- [论文：“Using the Output Embedding to Improve Language Models”，Press 和 Wolf，2017](https://arxiv.org/abs/1608.05859)
  主张绑定输入嵌入和输出投影的权重矩阵，因为两者联系的是同一个 token 的底层表示，这样能削减大词表模型很大一部分参数。用途：把权重绑定理解为一种刻意的设计选择，而不只是节省参数的小技巧。
- [文档：“torch.nn.functional.cross_entropy”，PyTorch](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
  融合了 softmax 和负对数似然的运算的官方文档，它直接接收原始 logits 以保证数值稳定，而不要求先单独做一步 softmax。用途：交叉熵损失在实践中究竟是如何计算的，而不只是它的公式。
- [论文：“Adam: A Method for Stochastic Optimization”，Kingma 和 Ba，2015](https://arxiv.org/abs/1412.6980)
  提出 Adam 相对于朴素梯度下降的动量（一阶矩）和逐参数自适应缩放（二阶矩），两者都带有偏差修正。用途：在 AdamW 的权重衰减修正之前，先理解 Adam 的更新规则计算什么、为什么这样计算。
- [论文：“Decoupled Weight Decay Regularization”，Loshchilov 和 Hutter，2019](https://arxiv.org/abs/1711.05101)
  指出在原始 Adam 里把权重衰减折进梯度，为什么与它的自适应缩放相互作用得很糟，并通过把衰减直接施加在权重上来修正它。用途：为什么训练 Transformer 的标准优化器是 AdamW，而不是普通的 Adam。
- [论文：“Neural Machine Translation of Rare Words with Subword Units”，Sennrich、Haddow 和 Birch，2016](https://arxiv.org/abs/1508.07909)
  提出用于子词分词的字节对编码：反复合并最常见的相邻符号对，从原始字节向上构建词表。用途：推导 `llm/finetuning` 只是顺带提到的分词器机制，而不是重述它。
- [论文：“RoFormer: Enhanced Transformer with Rotary Position Embedding”，Su 等，2021](https://arxiv.org/abs/2104.09864)
  提出 RoPE：把投影后的查询向量和键向量按与位置成正比的角度旋转，产生只取决于相对偏移的注意力分数。用途：当前几乎所有开源模型用来取代正弦或学习得到的位置编码的机制。
- [论文：“Root Mean Square Layer Normalization”，Zhang 和 Sennrich，2019](https://arxiv.org/abs/1910.07467)
  提出 RMSNorm，假设层归一化的重新中心化（减均值）运算可有可无，仅重新缩放就贡献了它的大部分好处。用途：当前模型放在第 5 课推导的前归一化分支里的那个更便宜的归一化。
- [论文：“GLU Variants Improve Transformer”，Shazeer，2020](https://arxiv.org/abs/2002.05202)
  在 Transformer 的前馈子层里测试门控线性单元的变体（包括用 Swish 门控的 SwiGLU），发现其中一些优于通常使用的 ReLU 或 GELU。用途：在当前模型里取代第 6 课单投影前馈块的那种带门控、有两个向上投影的设计。
- [论文：“GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints”，Ainslie 等，2023](https://arxiv.org/abs/2305.13245)
  提出分组查询注意力，作为完整多头注意力与多查询注意力的单个共享键/值头之间的折中，并给出一个把现有多头检查点追加训练成它的廉价配方。用途：为什么更少的键/值头，用少量质量换来小得多的 KV 缓存和更快的推理。
- [论文：“The Curious Case of Neural Text Degeneration”，Holtzman 等，2019](https://arxiv.org/abs/1904.09751)
  记录了为什么在解码时最大化似然（贪心解码），尽管似然是一个好的训练目标，却会产生平淡而重复的文本，并提出核（top-p）采样作为修正。用途：为什么动态的、基于累积概率的截断，同时优于贪心解码和固定个数的 top-k，其确切的原因。
- [论文：“On the difficulty of training Recurrent Neural Networks”，Pascanu、Mikolov 和 Bengio，2013](https://arxiv.org/abs/1211.5063)
  分析梯度消失和梯度爆炸问题，并提出梯度范数裁剪作为后者的修正。用途：为什么裁剪是按范数重新缩放整个梯度向量，而不是分别限制每个参数的梯度。
- [论文：“Mixed Precision Training”，Micikevicius 等，2018](https://arxiv.org/abs/1710.03740)
  提出用半精度训练，配以全精度的主权重副本和损失缩放，来对付半精度有限的数值范围，把内存使用减少近一半。用途：为了不让微小的更新和梯度下溢为零，朴素的半精度训练究竟必须加上什么。
- [论文：“BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding”，Devlin 等，2018](https://arxiv.org/abs/1810.04805)
  提出仅编码器架构：在每一层里同时以左右两侧的上下文为条件的双向注意力，没有因果掩码。用途：为什么仅编码器模型为完整的输入构建表示，而不是以自回归方式生成文本，也做不到这个工作区的仅解码器模型所能做的事。
- [论文：“Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer”（T5），Raffel 等，2019](https://arxiv.org/abs/1910.10683)
  把大量的 NLP 任务纳入同一种一致的文本到文本的编码器-解码器格式。用途：编码器-解码器形态的交叉注意力子层，以及为什么它适合输入与输出泾渭分明的任务。
- [论文：“FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness”，Dao 等，2022](https://arxiv.org/abs/2205.14135)
  把标准注意力在长序列上的缓慢，诊断为一个 IO 问题（HBM 与 SRAM 之间的内存读写），而不是计算问题，并提出一种分块的、精确的算法，避免实体化完整的分数矩阵。用途：为什么真实的注意力实现，在结构上与第 1 课的版本看起来不同，却计算出完全相同的结果。
- [论文：“Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity”，Fedus、Zoph 和 Shazeer，2021](https://arxiv.org/abs/2101.03961)
  提出一种简化的、每个 token 一个专家的 MoE 路由方案，把总参数量与每个 token 的计算成本解耦。用途：稀疏激活模型所做的具体取舍，以及为什么把路由简化为一个专家，解决了更复杂的 MoE 设计所遇到的不稳定问题。

## 空白

- 目前还没有专门讲学习率先预热再衰减的确切调度的资料；第 19 课根据最初的 Transformer 论文自己的训练细节所陈述的形状来推导它（线性预热，然后按步数的平方根的倒数成比例地衰减），但本次会话中，通过现有的工具，没能得到那一节新近核实过的直接摘录（论文的摘要页没有训练细节那一节，其他提供它的 PDF 来源也没有提取出可读的文本）。等有更干净的来源时，再回头补上。
