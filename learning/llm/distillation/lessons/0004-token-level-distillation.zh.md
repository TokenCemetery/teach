---
title: "4. token 级蒸馏"
description: "在序列的每个位置上匹配教师的下一个 token 分布"
type: lesson
---

# 第 4 课：token 级蒸馏

**使命关联:** 本使命要求你写出 LLM 的 token 级蒸馏损失，而本课就把它写出来：每个位置一个散度，在序列上求和或取平均，并把填充位置屏蔽掉。
**主要来源:** [论文：“Sequence-Level Knowledge Distillation”，Kim 和 Rush，2016](https://arxiv.org/abs/1606.07947)
**前置知识:** [第 3 课](0003-temperature.md)、[token 级蒸馏](../GLOSSARY.md)、[教师强制](../GLOSSARY.md)、[KL 散度](../GLOSSARY.md)

## 热身

1. ▢ 在组合损失里，哪一项运行在高温下，又是什么乘在它上面？

<details markdown="1"><summary>检查</summary>

与教师软目标的交叉熵运行在高温 T 下，而 T 的平方乘在它上面，使它的梯度在 T 变化时，相对于硬标签项仍保持原有的大小。硬标签项运行在 T = 1。

</details>

2. ▢ 为什么在 T = 1 时，教师在错误类别上 10^-6 的概率对损失几乎是不可见的？

<details markdown="1"><summary>检查</summary>

该类别的交叉熵项，是它的目标概率乘以学生概率的对数，所以 10^-6 的目标使这一项只有接近 1 的目标那一项的百万分之一重。较高的 T 会把这些目标抬起来，让它们起作用。

</details>

## 要点

### 起源：词级蒸馏

Kim 和 Rush 把 Hinton 的想法用到翻译上。神经翻译模型的训练，是在给定源句和前面的词时，最小化每个目标词的负对数似然，所以在句子的每个位置上都存在一个教师。他们把一个句子的词级损失，定义为对位置 j、以及对目标词表 V 中每个词 k 的求和：

```text
L_WORD-KD = - sum_j sum_k q(t_j = k | s, t_<j) * log p(t_j = k | s, t_<j)
```

这里 q 是教师，p 是学生，s 是源句，每个概率的最后一个条件是前缀，即位置 j 之前的目标词。学生还可以在这个损失与普通的词级负对数似然的混合上训练。他们称之为词级知识蒸馏（第 3.1 节）。在 LLM 里，单位是 token，所以本系列说的是 [token 级蒸馏](../GLOSSARY.md)。

请注意这里的条件是什么。前缀来自训练数据中真实的目标序列。论文的图 1 把它描述为，对真实目标序列中的每个词，最小化学生与教师分布之间的交叉熵。两个模型输入的是同一个固定前缀，各自为下一个词输出一个分布，这就是[教师强制](../GLOSSARY.md)。

在 WMT 2014 英语到德语上（表 1），一个 2 层、每层 500 单元的学生，贪心解码得到 14.7 BLEU，束搜索得到 17.6。使用词级蒸馏后分别是 15.4 和 17.7，提升了 0.7 和 0.1。4 层、每层 1000 单元的教师得到 17.7 和 19.5。作者测试了 0.5 和 0.9 的混合权重，发现 0.5 更好。论文说，词级蒸馏相对基线有改进，而它的序列级方法做得更好，这是第 3 阶段的主题。

### LLM 的损失

最近的三篇论文，用略有不同的形式写出了同一个损失。它们在结构上是一致的：在每个位置上，对两个下一个 token 分布求一个散度，再在序列上合并。

- Gemma 2（Gemma Team，2024，第 3.2 节）最小化教师与学生概率之间的负对数似然，即对 x 求和的 -P_T(x | x_c) log P_S(x | x_c)，其中 x_c 是上下文。
- GKD（Agarwal 等，2023，公式 2）对各位置的散度取平均：散度在输出位置 n 上求和，再除以输出长度 L_y。
- Minitron（Muralidharan 等，2024，第 3 节）在序列长度 l 上取平均，并在 softmax 里使用温度 tau。

交叉熵与前向 KL 之差是教师分布的熵，而它不依赖于学生。二者关于学生参数的梯度是相同的，这就是为什么论文用这两个名字称呼同一个目标。对词表的求和在每一项里面。所以这个计算的形态是：每个模型一个 logit 张量，维度是批次、位置和词表，散度沿最后一个轴取。

```python
import torch.nn.functional as F

def token_kd_loss(student_logits, teacher_logits, mask, T=1.0):
    # logits: (batch, positions, vocab). mask: (batch, positions), 1.0 for real tokens.
    s = F.log_softmax(student_logits / T, dim=-1)
    t = F.log_softmax(teacher_logits / T, dim=-1)
    kl = (t.exp() * (t - s)).sum(dim=-1)        # (batch, positions)
    return (kl * mask).sum() / mask.sum()        # mean over real tokens
```

教师的 logit 来自关闭梯度的一次前向传播。这个函数里有三处选择是决定，而不是事实。对真实 token 取平均，也可以改成求和，就像 Kim 和 Rush 写的那样，而求和会随序列长度缩放。掩码之所以重要，是因为填充位置没有有意义的目标。而默认取 T = 1，是因为第 3 课里 Minitron 的温度消融。

### 同样的算术，可以运行

下面的 NumPy 版本，在三个位置、四个 token 上做上面那个函数的算术，不需要任何框架。教师和学生的 logit 在第三个位置上完全一致，它代表填充。

```python
import numpy as np

def log_softmax(z):
    z = z - z.max(axis=-1, keepdims=True)
    return z - np.log(np.exp(z).sum(axis=-1, keepdims=True))

teacher = np.array([[3.0, 1.0, 0.0, -1.0],
                    [0.0, 2.5, 2.0, -2.0],
                    [1.0, 1.0, 1.0, 1.0]])
student = np.array([[2.0, 1.5, 0.5, -1.0],
                    [0.5, 2.0, 2.0, -1.0],
                    [1.0, 1.0, 1.0, 1.0]])
t, s = log_softmax(teacher), log_softmax(student)
kl = (np.exp(t) * (t - s)).sum(axis=-1)
mask = np.array([1, 1, 0])
print(np.round(kl, 4), round(kl.sum(), 4), round(kl.mean(), 4))
print(round((kl * mask).sum() / mask.sum(), 4))
```

运行之前，先拿最后一个数与三个位置的平均值做预测对比。在 NumPy 2.5 上的输出：

```text
[0.1998 0.0541 0.    ] 0.2539 0.0846
0.127
```

对全部三个位置取平均，会被一个不携带信号的位置稀释损失。对两个真实 token 取平均，得到 0.127。

### 固定序列的代价

序列在训练之前就已经固定，要么是人类写的文本，要么是教师写的文本，而学生只在这些序列上看到教师的分布。生成时，学生从它自己的 token 继续往下，而这里没有任何分布覆盖过它们。第 5 阶段的第 14 课把这叫作暴露偏差，第 15 课展示在策略的修复办法。教师也会为每个批次多花一次前向传播，Minitron 的作者把它列为蒸馏相对常规训练的额外开销（第 4 节）。

## 练习

1. ▢ 在 NumPy 的运行中，为什么只对真实 token 取的平均 0.127，超过了对全部三个位置取的平均 0.0846？

<details markdown="1"><summary>提示</summary>

数一数每个分母里有几个位置，再看第三个位置对分子贡献了什么。

</details>

<details markdown="1"><summary>检查</summary>

第三个位置对分子加了 0，却计入了普通平均的分母：0.2539 / 3 是 0.0846。加了掩码后，分母是 2，0.2539 / 2 是 0.127。在填充很多的真实批次里，没加掩码的平均会低估损失，而且低估的程度随填充量而变。

</details>

2. ▢ 在 Kim 和 Rush 的词级损失里，教师和学生都以哪个前缀为条件？

    - a) 训练数据中的目标词
    - b) 学生自己采样出的词
    - c) 教师通过贪心解码选出的词
    - d) 输入源句中的词

<details markdown="1"><summary>检查</summary>

**a)** 前缀是真实的目标序列，所以两个模型看到的是同样固定的词。不是 (b)：那是第 15 课的在策略设置。不是 (c)：对教师自己的输出解码，是第 3 阶段的序列级方法。不是 (d)：源句是另一个条件输入 s，不是前缀。

</details>

3. ▢ Gemma 2 最小化针对教师概率的交叉熵，而 Minitron 写的是 KL 散度。为什么两者可以描述同一个训练信号？

<details markdown="1"><summary>检查</summary>

前向 KL 等于交叉熵减去教师的熵，而教师是固定的，所以这个熵相对于学生的参数是一个常数。这两个损失在数值上不同，但梯度相同。在跨论文比较损失数字之前，请先查清每篇新论文指的是哪一个。

</details>

4. ▢ 修改 `token_kd_loss`，让它应用第 3 课的温度和 T 平方因子。需要哪两处改动？为什么函数里本来就已经有其中一处？

<details markdown="1"><summary>检查</summary>

函数在做 log-softmax 之前，已经把两组 logit 都除以 T，所以温度已经在里面。缺的是那个因子：当它与硬标签项合并时，把返回的损失乘以 T ** 2，使软项在 T 变化时保持它的权重。T = 1 时这个因子是 1，所以上面的函数在默认值下不需要改动。

</details>

5. ▢ 一位队友报告说，在改用填充到更长长度的批次之后，他们的 LLM 运行的蒸馏损失下降了一半。模型并没有改变。你首先检查什么？

<details markdown="1"><summary>提示</summary>

填充位置上，一个模型与它自己完全一致，所以它们贡献的散度为零。

</details>

<details markdown="1"><summary>检查</summary>

平均是除以全部位置，还是只除以真实 token。若是前者，更长的填充长度会让分母多出位置，数字下降而质量毫无变化。像上面的函数那样除以掩码之和，再比较两次运行。

</details>

## 实战练习

- [ ] 运行那段 NumPy 代码。然后把学生在第一个位置的 logit 改得与教师相同，确认逐位置损失的第一项降到 0。
- [ ] 打开 GKD 论文，找到公式 2。在它旁边写下，它是对位置求和还是求平均，以及这与 Kim 和 Rush 的求和相比如何。
- [ ] 明天：不看笔记，写出 `token_kd_loss` 里每个张量的形状，然后说出掩码保护的是什么。

## 延伸阅读

- [蒸馏损失](../reference/distillation-losses.md)
- [论文：“Sequence-Level Knowledge Distillation”，Kim 和 Rush，2016](https://arxiv.org/abs/1606.07947)
- [论文：“On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes”，Agarwal 等，2023](https://arxiv.org/abs/2306.13649)
- [论文：“Gemma 2: Improving Open Language Models at a Practical Size”，Gemma Team，2024](https://arxiv.org/abs/2408.00118)
- [资源](../RESOURCES.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
