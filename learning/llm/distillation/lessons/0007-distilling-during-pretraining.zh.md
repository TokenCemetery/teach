---
title: "7. 预训练期间的蒸馏"
description: "Gemma 2 和 Minitron 如何在大规模上把教师的分布当作训练信号，以及存储 logit 的代价"
type: lesson
---

# 第 7 课：预训练期间的蒸馏

**使命关联:** 本使命要求你写出 token 级损失，并说明它什么时候无法使用，而本课把这个损失作为两个真实模型家族的训练信号来展示，并用字节数算出保存教师分布的代价。
**主要来源:** [论文：“Gemma 2: Improving Open Language Models at a Practical Size”，Gemma Team，2024](https://arxiv.org/abs/2408.00118)
**前置知识:** [第 6 课](0006-the-tokenizer-constraint.md)、[token 级蒸馏](../GLOSSARY.md)、[logit](../GLOSSARY.md)、[top-k logits](../GLOSSARY.md)

## 热身

1. ▢ 为什么 Llama 学生配 Qwen 教师，即使两边都给你完整的 logit，也会排除普通的 token 级损失？

<details markdown="1"><summary>检查</summary>

这个损失是把学生那一行里的概率 i 与教师那一行里的概率 i 相比，而不同的分词器让索引 i 变成不同的 token，大小和位置也可能不同。第 2 阶段给出的变通办法，是跨分词器的损失，或者从教师所在的家族里挑选学生。

</details>

2. ▢ 覆盖模式的学生最小化的是哪个方向的 KL？Minitron 发现它在哪种设置下最好？

<details markdown="1"><summary>检查</summary>

[前向 KL](../GLOSSARY.md)。Minitron 发现，在重新训练剪枝后的基础模型时，它比反向 KL 更好：对深度剪枝的 Minitron 8B，语言建模损失是 2.155，而反向 KL 是 2.665（他们论文的表 16）。那只是一种设置，而第 5 课给出了支持另一个方向的指令微调证据。

</details>

## 要点

本课讲的是两种训练配方中蒸馏的那一半。预训练运行从数据到硬件是如何组织的，属于[预训练系列](../../pretraining/)，而剪枝作为一种方法，两者都不涉及。

### 把蒸馏作为预训练目标：Gemma 2

Gemma 2 的报告用知识蒸馏而不是下一个 token 预测，来训练它的 2B 和 9B 模型。动机是，下一个 token 的训练只随数据量按对数规模提升，小模型需要很长的训练才能进步。蒸馏把每个 token 上的 one-hot 向量，换成来自大模型的下一个 token 的分布，报告说这提供了更丰富的梯度。它声明的目的，是用蒸馏在极其大量的 token 上训练，以模拟在超过可用 token 数量之后继续训练（引言）。

报告给出的事实：

- 2B 模型在 2 万亿 token 上训练，9B 在 8 万亿上，27B 在 13 万亿上（第 3.1 节）。27B 是从零开始训练的，没有蒸馏。
- 2B 和 9B 的 token 数，是 Hoffmann 等人所预测的算力最优数量的 50 多倍（引言）。
- 损失是教师在给定上下文时对每个 token 的概率，与学生的概率之间的负对数似然，对学生求最小化：-P_T(x | x_c) log P_S(x | x_c) 之和（第 3.2 节）。这就是第 4 课在温度 1 下的损失。
- 词表有 256,128 项（表 1），继承自 Gemini，上下文长度是 8,192 个 token（第 2 节）。

它的消融用的是 7B 的教师，不是最终的那个。一个在 500B token 上训练的 2B 学生（报告说这是 2B 算力最优数量的 10 倍），在三个基准上，从零训练的平均分是 60.3，蒸馏后是 67.7（表 6）。教师固定为 7B 时，200M、400M 和 1B 参数下的验证困惑度，从零训练分别是 23、19 和 17，蒸馏后是 21、17 和 15（表 7）。报告还说，用 2T token 训练的新 2B，比用 3T token 训练的 Gemma 1 的 2B 有显著提升（第 6.1 节）。这些是 Google 自己做的比较。

### 报告没有说什么

报告没有点明最终 2B 和 9B 模型的教师是谁，也没有给出它的规模。它没有描述教师的分布是如何提供给学生的：是预先存储、与训练同时计算，还是近似得到。关于 Gemma 2 采用了采样或截断的 top-k 的说法，报告里没有。下一节会算出每种选择的代价，这样你就可以在没有该选择的来源时也能推理。

### 存储教师的代价

每个训练 token 都配一个词表上的分布，数据量很大。脚本使用 Gemma 2 的词表和 token 数量，以及本课的两个假设：bf16 概率占 2 字节，截断版本使用一个说明性的 k = 256，token 索引占 4 字节。

```python
vocab = 256_128            # Gemma 2 vocabulary size (Table 1 of the report)
tokens = {"2B run": 2e12, "9B run": 8e12}

full = vocab * 2           # bf16: 2 bytes per probability
k = 256                    # an illustrative k, not a number from any paper
topk = k * (2 + 4)         # 2-byte probability + 4-byte token index

print("full per token: %d bytes" % full)
print("top-%d per token: %d bytes (%.1fx smaller)" % (k, topk, full / topk))
print("full per 8192-token sequence: %.2f GB" % (full * 8192 / 1e9))
for name, n in tokens.items():
    print(name, "full: %.2f EB" % (full * n / 1e18), " top-%d: %.2f PB" % (k, topk * n / 1e15))
```

运行之前，先预测 2B 运行的完整分布成本是什么量级。输出：

```text
full per token: 512256 bytes
top-256 per token: 1536 bytes (333.5x smaller)
full per 8192-token sequence: 4.20 GB
2B run full: 1.02 EB  top-256: 3.07 PB
9B run full: 4.10 EB  top-256: 12.29 PB
```

为 2B 运行存储完整的分布，大约是一艾字节，9B 运行大约是四艾字节。每个 token 只保留 256 项，可以把它缩小 333.5 倍，降到拍字节的量级，而且这个数字还只是把训练 token 数一次，没有重复任何轮次。截断也有代价。被丢弃的尾部质量必须处理，要么重新归一化，要么当作一个桶，而这个选择会改变目标。

还有一种什么都不存的办法：让教师与学生同时运行，从前向传播中读取它的分布。Minitron 走的就是这条路，并指出蒸馏会给教师增加一次额外前向传播的开销，所以他们是在相同算力下比较自己的蒸馏运行和常规运行的（第 4 节）。至于某个实验室具体用了哪条路线，本课不作断言。

Minitron 的作者也直接测试了截断。在他们关于蒸馏的附录（A.3）里，只保留教师和学生各自最大的 K 个 logit，K 取到 100 以内，会导致准确率显著下降。K 更大时这种下降消失，但结果并不比不截断更好。这只是一套重新训练剪枝模型的设置，截断在 K 取多大时不再有害，会因词表和模型而异。

### 剪枝加蒸馏：Minitron

Minitron（Muralidharan 等，2024）通过剪枝来压缩 Nemotron-4 15B，并以原模型作教师重新训练，来恢复准确率。它的学生一开始是剪枝后的副本，所以在构造上就与教师共用分词器。本课只取其中蒸馏的那一半。

- **token 数**。Minitron 8B 和 4B 模型各自在 940 亿 token 上重新训练。论文把 Minitron 8B 与在 3.8 万亿 token 上训练的 Nemotron-3 8B 做了比较，并把节省说成少用 40 倍 token（表 2）。
- **蒸馏对比常规重新训练**。对一个 4B 模型，他们在相同算力下比较（表 11）。在 150B token 上从零训练，HellaSwag 是 46.22，MMLU 是 24.36。把 15B 剪枝到 4B，再在 150B 上做常规重新训练，是 50.85 和 24.57。剪枝后用蒸馏在 100B token 上重新训练，是 51.04 和 37.81。蒸馏运行用的是 100B token 而不是 150B，是因为教师多出的那次前向传播。相对从零训练，HellaSwag 提升了 4.8 分，MMLU 提升了 13.5 分。
- **损失**。logit 上的前向 KL，温度为 1，单用 logit 损失，比它与语言建模损失的加权混合更好，截断到 top K 也没有收益（第 4 节和附录 A.3）。

后续论文（Sreenivas 等，2024）把这个配方用到 Llama 3.1 8B 和 Mistral NeMo 12B 上。它在蒸馏之前增加了一步：教师校正。当原始的预训练数据拿不到时，教师在另一个数据集上给出的指导是次优的，作者把这归因于子词 token 分布的变化。所以他们先在大约 100B token 的蒸馏数据上微调教师，用预热和较低的学习率。然后他们做剪枝，并只在 logit 上用前向 KL 做蒸馏。Llama-3.1-Minitron 4B 在 94B token 上重新训练，MN-Minitron-8B 在 380B 上（表 4）。论文说，4B 与 Llama 3.1 8B 相比表现不俗，而用的 token 少了 150 倍，是 94B 对 15T；8B 超过了 Llama 3.1 8B，用的 token 少了 40 倍，是 380B 对 15T（第 5.1 节）。这些是 NVIDIA 在他们自己的评测上做的比较。

## 练习

1. ▢ 在报告中，哪些 Gemma 2 模型是用蒸馏训练的，各自看到了多少 token？

    - a) 2B 在 8T 上，27B 在 2T 上
    - b) 9B 在 8T 上，27B 在 13T 上
    - c) 三个模型各自都在 13T token 上训练
    - d) 2B 在 2T 上，9B 在 8T 上

<details markdown="1"><summary>检查</summary>

**d)** 27B 是从零开始在 13T token 上训练的，所以 (b) 和 (c) 错把它包括进来了。选项 (a) 把 token 数对调了。报告在第 3.1 节陈述了这些数量。

</details>

2. ▢ 词表为 256,128，每个概率占 2 字节，一个完整的下一个 token 分布占多少字节？对一条 8,192 个 token 的序列，合多少吉字节？

<details markdown="1"><summary>提示</summary>

把词表乘以每项的字节数，再乘以序列长度，然后除以十亿。

</details>

<details markdown="1"><summary>检查</summary>

256,128 乘以 2 是每个 token 512,256 字节。乘以 8,192 得到 4,196,401,152 字节，一条序列约 4.20 GB。一次训练运行有数以百万计这样的序列，这就是为什么会有存储还是重新计算这个问题。

</details>

3. ▢ 保留前 256 项，每项有 2 字节的概率和 4 字节的索引，一个 token 的记录有多大？比完整分布小多少？

<details markdown="1"><summary>检查</summary>

256 乘以 6 是 1,536 字节，比 512,256 小 333.5 倍。256 这个 k 和各项的字节大小是本课的假设，不是 Gemma 2 的数字。这条记录还略去了分布的尾部，而尾部必须重新归一化或装进一个桶里，这个选择会改变目标。

</details>

4. ▢ 一个论坛帖子说 Gemma 2 是在存储下来的 top-256 教师分布上训练的。你怎么处理这个说法？

<details markdown="1"><summary>检查</summary>

去报告里找它。报告陈述了损失、token 数和消融，并没有描述分布是如何提供的。所以从报告来看，这个说法没有得到证实。把它当作没有依据的说法，写下缺少什么，并在依赖它之前，去找作者的文字之类的一手来源。

</details>

5. ▢ 在 Minitron 的表 11 里，剪枝加常规重新训练的 MMLU 达到 24.57，剪枝加蒸馏达到 37.81，而蒸馏用的 token 更少。为什么 token 数是 150B 和 100B？这张表的局限是什么？

<details markdown="1"><summary>检查</summary>

他们是在相同算力下比较，而蒸馏要把预算的一部分花在教师的前向传播上，所以它得到的是 100B token 对 150B。这张表只涉及一个从 Nemotron-4 15B 剪枝得到的 4B 模型。作者用它来说明，剪枝之后蒸馏胜过常规重新训练。它并没有说明在其他教师、规模或基准上也有这样的收益。

</details>

6. ▢ 后续 Minitron 论文里的教师校正，在蒸馏之前先在大约 100B token 上微调教师。什么时候需要它？跳过它时，作者归咎于什么？

<details markdown="1"><summary>检查</summary>

当教师原始的预训练数据拿不到、因此蒸馏数据的分布不同时，需要它。作者说，这时教师给出的指导是次优的，并假设原因是教师原始数据与蒸馏所用数据之间，子词 token 的分布不同。这个解释是他们的假设。

</details>

## 实战练习

- [ ] 用你自己的词表大小运行存储脚本，并把 k 分别设为 64 和 1,024，写下三个成本比值。
- [ ] 打开 Minitron 论文的表 11，找到等算力的标记。写下哪一行用了教师，以及它看到了多少 token。
- [ ] 明天：不看笔记，说出 Gemma 2 的三个 token 数和一个 token 的存储算术，然后说出报告对教师没有交代的内容。

## 延伸阅读

- [蒸馏损失](../reference/distillation-losses.md)
- [论文：“Gemma 2: Improving Open Language Models at a Practical Size”，Gemma Team，2024](https://arxiv.org/abs/2408.00118)
- [论文：“Compact Language Models via Pruning and Knowledge Distillation”，Muralidharan 等，2024](https://arxiv.org/abs/2407.14679)
- [论文：“LLM Pruning and Distillation in Practice: The Minitron Approach”，Sreenivas 等，2024](https://arxiv.org/abs/2408.11796)
- [资源](../RESOURCES.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
