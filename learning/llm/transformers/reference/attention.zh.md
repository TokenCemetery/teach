---
title: "注意力"
description: "缩放点积注意力、多头注意力和因果掩码，每一步都标注了张量的形状"
type: reference
---

# 注意力：缩放点积、多头与因果掩码

第 1 阶段，压缩成便于查阅的形式。[第 1 课](../lessons/0001-scaled-dot-product-attention.md)讲核心方程，[第 2 课](../lessons/0002-multi-head-attention.md)讲在并行的子空间里运行它，[第 3 课](../lessons/0003-causal-masking.md)讲把它限制在过去。这张速查表把方程和形状并排放在一起。

## 缩放点积注意力

```text
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

| 步骤 | 输入形状 | 输出形状 | 说明 |
|---|---|---|---|
| 给定 `Q`、`K`、`V` | 不适用 | `[n, d_k]`、`[m, d_k]`、`[m, d_v]` | `n` 个查询，`m` 个键/值对；`d_k` 是键/查询的维度 |
| `QK^T` | `[n, d_k] × [d_k, m]` | `[n, m]` | 每一对查询和键一个相似度分数 |
| `/ sqrt(d_k)` | `[n, m]` | `[n, m]` | 抵消方差随 `d_k` 的增长，让 softmax 的梯度保持可用 |
| `softmax(...)`（逐行） | `[n, m]` | `[n, m]` | 现在每一行都是总和为 1 的概率分布 |
| `× V` | `[n, m] × [m, d_v]` | `[n, d_v]` | 每个查询一个输出向量，是各个值的加权混合 |

自注意力是 `Q`、`K`、`V` 都来自同一个序列的情形（`n = m`），每个位置都关注每个位置，包括它自己。

**为什么要缩放。** 点积的方差随 `d_k` 增大，把 softmax 推向近乎 one-hot 的输出，那里它的梯度几乎为零，训练停滞。不论 `d_k` 多大，`/ sqrt(d_k)` 都抵消了这种增长。

## 多头注意力

```text
Q_i = X W_Q^i,   K_i = X W_K^i,   V_i = X W_V^i          (per head i, i = 1..h)
head_i = Attention(Q_i, K_i, V_i)
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) W_O
```

| 步骤 | 输入形状 | 输出形状 | 说明 |
|---|---|---|---|
| 输入 `X` | 不适用 | `[n, d_model]` | |
| 每个头的投影（`W_Q^i`、`W_K^i`、`W_V^i`） | `[n, d_model] × [d_model, d_k]` | 每个头 `[n, d_k]`，`d_k = d_model / h` | 每个头的投影是独立学习的 |
| `head_i = Attention(Q_i, K_i, V_i)` | 各 `[n, d_k]` | `[n, d_k]` | 上面那个确切的方程，每个头各运行一次 |
| `Concat(head_1, ..., head_h)` | `h × [n, d_k]` | `[n, d_model]` | 把各个头并排放在一起，目前还没有跨头的交互 |
| `× W_O` | `[n, d_model] × [d_model, d_model]` | `[n, d_model]` | 唯一让不同头的信息得以结合的一步 |

**缩放公式用的是每个头的 `d_k`，而不是 `d_model`。** 每个头的点积是对它自己更小的维度求和的，所以那才是缩放需要抵消的方差，不论完整的模型有多大。

**`W_O` 不是可选的。** 单靠拼接只是把输出并排放在一起，没有交互；`W_O` 是不同头的信息可以结合成一个表示的唯一地方。

## 因果掩码

在 softmax 之前，加到原始分数上：

```text
scores = QK^T / sqrt(d_k)
scores[i, j] += -inf   for every j > i     (a fixed lower-triangular pattern)
Attention(Q, K, V) = softmax(scores) V
```

| 选择 | 原因 |
|---|---|
| 在 softmax 之前掩码，而不是之后 | 在 softmax 已经运行之后把权重置零，会让剩下的权重总和小于 1，不是有效的分布。掩码分数，则让重新归一化在同一个 softmax 内部自动发生 |
| 用很大的负数，而不是 `0` | `exp(0) = 1`，是一个普通的、不可忽略的值，仍然在争夺概率质量。只有足够大的负数，才能把 `exp(...)` 压到实际上为零 |
| 每个头和一个批次里的每个样本使用同一个掩码 | 这个限制（查询位置 `i` 可以关注键位置 `0..i`）是任务本身的性质，而不是任何一个头的性质 |

推理时，模型只用 token `1..N-1` 来生成 token `N`；训练时若让位置 `i` 去关注更靠后的位置 `j`，就会让模型用上一个它在生成时永远得不到的答案。那种情况下训练损失看起来不错，但模型学不到任何可以迁移的东西。

## 信任一个注意力实现之前

- [ ] 缩放的除数是每个头的 `d_k`（`d_model / h`），而不是完整的 `d_model`。
- [ ] `W_O` 是在拼接各个头之后施加的，而不是被跳过。
- [ ] 因果掩码是在 softmax 之前加到原始分数上的，而不是之后施加到权重上。
- [ ] 掩码的值是很大的负数（或 `-inf`），而不是 `0`。
- [ ] 不论头数是多少，输出形状都是 `[n, d_model]`，因为各个头只改变中间的每个头的维度。

## 来源

- [论文：“Attention Is All You Need”，Vaswani 等，2017](https://arxiv.org/abs/1706.03762)
- [文章：“The Annotated Transformer”，Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
- [文章：“The Illustrated Transformer”，Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [资源](../RESOURCES.md)
