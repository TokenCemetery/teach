---
title: "6. 量化粒度"
description: "逐张量、逐通道和逐组的缩放因子，以及各自在存储位数上的代价"
type: lesson
---

# 第 6 课：量化粒度

**使命关联:** 要预测一个量化张量的误差，还得知道有多少个值共用每一个缩放因子，因为缩放因子由它所覆盖的那组值里最大的值决定，而每多一个缩放因子，就多花一些存储位数。
**主要来源:** [论文：“A White Paper on Neural Network Quantization”，Nagel 等，2021](https://arxiv.org/abs/2106.08295)，第 2.2.3 节和第 2.4.2 节
**前置知识:** [第 5 课](0005-choosing-the-range.md)、[量化粒度](../GLOSSARY.md)、[分组大小](../GLOSSARY.md)、[每个权重的有效位数](../GLOSSARY.md)

## 热身

1. ▢ 用最小最大值法设定范围时，什么决定了量化器的缩放因子？一个离群值会对它造成什么影响？

<details markdown="1"><summary>检查</summary>

范围，也就是由最大值和最小值确定的那个范围，除以步数。一个离群值会让范围变宽，于是缩放因子增大，其他每个值的步长都变粗，这可能把其中大多数舍入成零（第 5 课）。

</details>

2. ▢ 一个 4 位方案为每组 32 个权重存一个 16 位缩放因子。它的每个权重的有效位数是多少？

<details markdown="1"><summary>检查</summary>

4.5。缩放因子在每个值的 4 位之上，使每个权重多出 16 / 32 = 0.5 位（第 1 课）。

</details>

3. ▢ 为什么对称网格只需要一个缩放因子？去掉零点的代价是什么？

<details markdown="1"><summary>检查</summary>

对称量化把零点固定为零，所以没有别的东西需要存。代价是网格以零为中心，所以单侧的张量会把空的那一侧的档位浪费掉（第 4 课）。

</details>

## 要点

### 什么共用一个缩放因子

**量化粒度**指的是有多少个值共用一个缩放因子和零点。共用缩放因子的集合越小，范围就越小，所以一个离群值只会毁掉它所在的那一个集合。代价是每个集合都要存自己的缩放因子。

```text
W: output channels (rows) x input features (columns)

per-tensor    one scale for the whole matrix
per-channel   one scale per row (per output channel of a weight matrix)
per-group     one scale per `group size` consecutive values within a row, such as 64 or 128
per-token     one scale per row of an activation matrix X (tokens x features)
```

Nagel 等人指出，逐张量量化是标准做法，因为每一种定点加速器都支持它，而当权重的分布在各通道之间变化很大时，对权重做逐通道量化帮助最大。他们还描述了对每一组权重或激活值应用一个量化器的做法，并说，更细的分组通常能以额外的开销为代价提高精度。

### 为什么逐通道对权重行得通，对激活值却不行

一个线性层把每个输出计算成对输入特征的求和。把量化后的值写成缩放因子乘以整数，只有缩放因子在整个求和范围内保持不变，它才能提到求和之外：

```text
y[i] = sum over k of (s_w[i] * W_int[i,k]) * (s_x * x_int[k])
     = s_w[i] * s_x * (sum over k of W_int[i,k] * x_int[k])
```

括号里是一个纯粹的整数点积，这正是硬件所加速的东西，而两个缩放因子只在最后对结果乘一次。逐输出通道的权重缩放因子 `s_w[i]` 在求和范围内是常数，因为 `i` 指的是输出，被求和的是 `k`。Nagel 等人得出结论：逐通道的权重量化，可以带上各通道独立的缩放因子来应用，而无需对累加器重新缩放。

逐输入通道的激活值缩放因子会是 `s_x[k]`，它随着被求和的下标而变。它提不到求和之外，Nagel 等人说它“因此需要对每个输入通道重新缩放累加器”。逐通道的激活值量化因此难以实现得多。逐 token 的激活值缩放因子，也就是 `X` 的每一行一个，对给定的某个 token 来说在求和范围内是常数，不花任何代价：[Dettmers 等人](https://arxiv.org/abs/2208.07339)在他们的向量级量化中用的正是这个办法，激活值的每一行一个常数，权重的每一列一个常数，再用这些常数的外积把两者都撤销。第 7 课会说明，为什么这对 LLM 还不够：离群值位于特征维度上，而这正是逐 token 缩放因子没有区分开的那根轴。

逐组量化对整数累加器有同样的问题，因为缩放因子在求和内部就变了。论文中累加器的这一限制，就是 Nagel 等人把分组缩放因子排除在外的原因。在仅权重量化的方案里，权重在内核内部被反量化成 16 位，并以 16 位相乘（见[仅权重量化](../GLOSSARY.md)），所以没有哪个整数累加器要携带混合的缩放因子，分组缩放因子可以自由变化。

### 缩放因子的代价

每个分组都会把它的缩放因子以及任何零点加进检查点。**每个权重的有效位数**就是值的位宽，加上分摊到该组上的元数据：

```text
effective bits = b + (scale bits + zero point bits) / group size
```

| 分组大小 | 16 位缩放因子的开销 | 4 位权重的有效位数 |
|---|---|---|
| 1024 | 0.0156 | 4.0156 |
| 256 | 0.0625 | 4.0625 |
| 128 | 0.125 | 4.125 |
| 64 | 0.25 | 4.25 |
| 32 | 0.5 | 4.5 |

逐通道，不过是分组大小等于行长的分组，逐张量则是由每个权重构成的一个分组：两者的代价都几乎为零。第 1 课中分组大小为 32 的数字，就是最后一行。

### 小分组能换来什么

练习中的实验，把一个合成的权重矩阵量化到 4 位，其中各行的尺度不同，并且是重尾的。随着分组缩小，误差稳步下降，逐张量差得最远。一个 64 个值的分组，只有 64 次机会含有一个离群值，而离群值也只影响这 64 个值。

这方面规模最大的实证研究是 [Dettmers 与 Zettlemoyer](https://arxiv.org/abs/2212.09720) 的：在从 19M 到 176B 参数的各种 LLM 上，做了 3 到 8 位的 35,000 多次零样本实验。他们发现，想要改进以位计的模型大小与精度之间的权衡，本来就很难，只有两样东西有帮助：小的块大小（他们对分组大小的叫法）和数据类型。对 4 位的 Pythia 模型，把块大小从 1024 降到 64，每个参数多出 0.24 位，而零样本精度的提升几乎与从 4 位增加到 5 位一样多。每块一个 16 位常数的代价是 16 / 64 - 16 / 1024 = 0.23 位，接近论文给出的数字。小分组是便宜的位。

## 练习

1. ▢ 一个 4 位方案为每组 64 个权重存一个 16 位缩放因子和一个 4 位零点。它的每个权重的有效位数是多少？

<details markdown="1"><summary>检查</summary>

4 + (16 + 4) / 64 = 4.3125，约 4.31。零点在缩放因子的 0.25 之上又增加了 4 / 64 = 0.0625。对称方案会去掉这 0.0625，落在 4.25。

</details>

2. ▢ 是什么使逐输出通道的权重缩放因子与整数矩阵乘法兼容，而逐输入通道的激活值缩放因子却不兼容？

    - a) 权重缩放因子只占八位
    - b) 权重缩放因子需要一个单独的偏移项
    - c) 权重缩放因子在整个求和范围内是常数
    - d) 权重缩放因子的取值在各输出通道之间不同

<details markdown="1"><summary>检查</summary>

**c)** 输出 `i` 的缩放因子乘以对 `k` 的整个求和，所以它提到求和之外，在整数累加完成之后只应用一次。按输入通道索引的激活值缩放因子在求和内部就变了，所以累加器在每个输入通道都需要重新缩放。(a) 说的是存储，并不决定缩放因子可以应用在哪里。(b) 把缩放因子和零点混为一谈，而对称权重不需要零点。(d) 是对的，但它是为什么会有许多缩放因子的原因，而不是它们为什么能被提出去的原因。

</details>

3. ▢ 先预测，再运行。运行之前，把逐张量、逐通道和各种分组大小按误差从最差到最好排序，并说出误差是否稳步下降。然后算出分组大小为 32 时的有效位数。

    ```python
    import numpy as np

    rng = np.random.default_rng(0)
    rows, cols, b = 256, 1024, 4
    qmax = 2 ** (b - 1) - 1
    row_scale = rng.lognormal(0.0, 0.7, size=(rows, 1)) * 0.02
    W = rng.standard_t(df=4, size=(rows, cols)) * row_scale


    def quantize(W, group):
        """Symmetric absmax, one scale per `group` consecutive values in a row.
        group=None means one scale for the whole tensor."""
        G = W.reshape(1, -1) if group is None else W.reshape(-1, group)
        s = np.abs(G).max(axis=1, keepdims=True) / qmax
        Q = s * np.clip(np.round(G / s), -qmax, qmax)
        return Q.reshape(W.shape)


    print("granularity    rel. error   effective bits (16-bit scales)")
    for name, group in [("per-tensor", None), ("per-channel", cols), ("group 256", 256),
                        ("group 128", 128), ("group 64", 64), ("group 32", 32)]:
        err = np.mean((quantize(W, group) - W) ** 2) / np.mean(W ** 2)
        n_scales = 1 if group is None else W.size // group
        print(f"{name:13s}  {err:.4f}       {b + 16 * n_scales / W.size:.3f}")
    ```

<details markdown="1"><summary>提示</summary>

分组大小每降一级，缩放因子就多一些，而每个缩放因子由更小的一组值决定。然后想想逐张量的缩放因子，对各行大小不同的矩阵会造成什么。

</details>

<details markdown="1"><summary>检查</summary>

```text
granularity    rel. error   effective bits (16-bit scales)
per-tensor     0.7047       4.000
per-channel    0.1291       4.016
group 256      0.0599       4.062
group 128      0.0395       4.125
group 64       0.0267       4.250
group 32       0.0179       4.500
```

误差每一步都在下降：逐张量留下的误差，约为信号自身能量的 70%，逐通道让每一行都有自己的缩放因子，去掉了其中大部分，而分组每减半一次，误差就降低约三分之一。分组大小为 32 时的有效位数是 4.5。数据是合成的，所以请读它的排序和大致的比值，而不是绝对数字。

</details>

4. ▢ 用 16 位缩放因子，把分组大小从 1024 改到 64，每个权重增加多少位？把它与把权重从 4 位升到 5 位的代价相比，并说出 Dettmers 与 Zettlemoyer 对这两种好处发现了什么。

<details markdown="1"><summary>检查</summary>

16 / 64 - 16 / 1024 = 0.234 位，而 5 位权重是整整 1 位。在论文中，更小的块大小，对 4 位 Pythia 模型零样本精度的提升，几乎与多加一位一样多。所以缩小分组，是比给每个权重多加一位便宜得多的买精度的办法。论文的头条结论是，就模型总位数和零样本精度而言，4 位几乎普遍是最优的。

</details>

5. ▢ 一个团队把激活值量化到 8 位，每个 token 一个缩放因子，精度却仍然受损，因为在每个 token 上都有一个特征维度大得出奇。为什么逐 token 的缩放因子没有帮助？什么样的轴才能把离群值分隔开？

<details markdown="1"><summary>检查</summary>

每个 token 的缩放因子由该 token 的最大值决定，而那个巨大的特征维度在几乎每个 token 上都是最大的，所以每一行的缩放因子都被同样地撑大了。Dettmers 等人指出了这一点：逐行和向量级量化缩放的是序列维度，而离群值位于特征维度上，所以两者都没能把它们隔离出来。只有逐特征维度的缩放因子才能把离群值分开，而那正是这一课讲的逐输入通道的激活值缩放因子，整数矩阵乘法无法廉价地应用它。

</details>

## 实战练习

- [ ] 在实验中，把 `rng.lognormal(0.0, 0.7, ...)` 里的 `0.7` 改成 `0.0`，使每一行的尺度相同，然后重新运行。记录逐通道相对于逐张量的优势还剩下多少，并解释原因。
- [ ] 打开 Hugging Face Hub 上任意一个 4 位 GPTQ 或 AWQ 检查点的模型卡或配置，找出它的分组大小，并按模型的参数量算出它的每个权重的有效位数和检查点大小。
- [ ] 明天：不看笔记，重建分组大小与有效位数的对照表，分别按 16 位缩放因子和 8 位缩放因子，并用一句话说出，为什么逐通道的权重缩放因子适合整数矩阵乘法，而逐通道的激活值缩放因子不适合。

## 延伸阅读

- [量化映射](../reference/quantization-mapping.md)
- [论文：“A White Paper on Neural Network Quantization”，Nagel 等，2021](https://arxiv.org/abs/2106.08295)
- [论文：“The case for 4-bit precision: k-bit Inference Scaling Laws”，Dettmers 与 Zettlemoyer，2022](https://arxiv.org/abs/2212.09720)
- [资源](../RESOURCES.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
