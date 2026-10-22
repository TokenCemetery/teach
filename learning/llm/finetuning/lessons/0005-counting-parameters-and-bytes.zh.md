---
title: "5. 统计参数量与字节数"
description: "把模型配置换算成 GB"
type: lesson
---

# 第 5 课：统计参数量与字节数

**使命关联:** “算清每一个字节”写在使命里。这一课让你学会动手算，而不是去猜。
**主要来源:** [文档：Model memory anatomy，Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/model_memory_anatomy)
**前置知识:** [第 2 课](0002-where-the-weights-live.md)、[第 4 课](0004-what-training-changes.md)

## 热身

1. ▢ 一个训练步骤里的四个操作是什么？

<details markdown="1"><summary>检查</summary>

前向传播（保留激活值）、损失、反向传播（产出梯度）、优化器步骤。

</details>

2. ▢ 标签张量里的 `-100` 是什么意思？

<details markdown="1"><summary>检查</summary>

计算损失时忽略这个位置。仅补全部分的损失，就是靠它把提示词的 token 屏蔽掉的。

</details>

3. ▢ 在分组查询注意力下，哪些注意力投影会变小？

<details markdown="1"><summary>检查</summary>

`k_proj` 和 `v_proj`。`q_proj` 和 `o_proj` 保持完整的隐藏维度。

</details>

## 要点

参数就是一个数。内存就是这个数的存储大小，乘以这类数的个数。第 2 阶段的其他一切，都是在此之上的记账。

### 数值格式

| 格式 | 字节数 | 说明 |
|---|---|---|
| `float32`（fp32） | 4 | 全精度。训练时历来的默认格式。 |
| `bfloat16`（bf16） | 2 | 指数范围与 fp32 相同，尾数位更少。现代的默认格式。 |
| `float16`（fp16） | 2 | 尾数更多，但范围小得多，所以更容易溢出成无穷大。 |
| `int8` | 1 | 整数，需要一个缩放因子才能解读。 |
| 4 位（`nf4`、`int4`） | 0.5 | 每字节两个值，外加逐块的缩放因子。见第 4 阶段。 |

训练时，bf16 比 fp16 更受青睐，尽管它存的精度更低，因为它的指数范围与 fp32 一致。溢出是比舍入误差更难恢复的失败，而 fp16 训练历来需要损失缩放才能避免它。

### 描述一个模型的两个数字

假如某张模型卡声称有 1.5B 个参数。那么：

```text
weights in fp32 = 1.5e9 × 4 bytes = 6.0 GB
weights in bf16 = 1.5e9 × 2 bytes = 3.0 GB
weights in nf4  = 1.5e9 × 0.5     = 0.75 GB, plus quantisation constants
```

这只是推理用的权重内存：把模型放进内存所需的下限，还没算任何激活值，没算任何 KV 缓存，更不用说训练了。

一个有用的反射：**bf16 的 GB 数约等于以十亿计的参数量的两倍。** 7B 模型的权重约 14 GB。70B 模型约 140 GB。你应该能立刻报出这些数字。

### 参数在哪里

根据第 2 课，每层：

```text
attention = 2 × d² + 2 × d × d_kv          (q, o full; k, v narrowed by GQA)
mlp       = 3 × d × d_ff                    (gate, up, down)
```

整个模型则是：

```text
total ≈ n_layers × (attention + mlp) + vocab × d × (1 or 2)
```

当输出投影与输入嵌入不共享权重时，最后一项要翻倍。对小模型来说，这一项并不可忽略：词表 32k、隐藏维度 2048，每份就是 65M 个参数，在 1.5B 的模型里占相当可观的一部分。

### 算例

一个模型，`d = 2048`、`d_kv = 256`、`d_ff = 5632`，24 层，词表 32k，嵌入共享权重：

```text
attention = 2 × 2048² + 2 × 2048 × 256  = 8.39M + 1.05M = 9.44M
mlp       = 3 × 2048 × 5632             = 34.6M
per layer                               = 44.0M
× 24 layers                             = 1.056B
embeddings = 32000 × 2048               = 0.066B
total                                   ≈ 1.12B
```

用 bf16，权重大约是 2.2 GB。注意 MLP 占了块的 79%，把这一点带到第 10 课去。

![两条占比条。每层的 44.0M 中，约 21% 是注意力，79% 是 MLP。整个模型的 1.12B 中，约 94% 是堆叠的层，5.9% 是嵌入。](images/where-the-parameters-are.svg)

同样的算式，换成了占比，放在两个要紧的层面上。在一个块的内部，注意力是小得多的那一半，所以第 10 课里的目标模块问题，主要是关于 MLP 的问题。放到整个模型上，嵌入这一项在这里很小，随着模型变小，它的占比会增大，上面那一段警告的就是这种情形。

### 这里还没有包括什么

你现在有了权重的开销。训练还要再增加三类，而且它们占大头：

- 梯度，每个可训练参数一个（第 6 课）
- 优化器状态，每个可训练参数两个（第 6 课）
- 激活值，取决于批大小和序列长度，而不是参数量（第 7 课）

任何告诉你 7B 模型“只需要 14 GB 就能微调”的人，只数了第一类。这就是本阶段存在的目的：消除这个错误。

## 练习

1. ▢ 13B 模型的权重，用 bf16 是多少 GB？用 fp32 呢？用 4 位呢？

<details markdown="1"><summary>检查</summary>

bf16：26 GB。fp32：52 GB。4 位：约 6.5 GB，外加量化常数。

从参数量出发，一路翻倍、减半，这条推算链值得练到不用计算器。

</details>

2. ▢ 既然 fp16 存了更多尾数位，为什么训练时 bf16 比 fp16 更受青睐？

<details markdown="1"><summary>检查</summary>

bf16 保留了 fp32 的指数范围，所以数值不会溢出成无穷大。fp16 范围狭窄，意味着梯度可能上溢或下溢，历来需要损失缩放才能正常工作。

舍入误差是平缓地劣化；溢出会产生 `NaN`，让运行就此结束。这笔交易偏向范围。

</details>

3. ▢ 一个模型，`d = 4096`、`d_ff = 14336`、`d_kv = 1024`，32 层。忽略嵌入，算出每层的参数量和模型总量。

<details markdown="1"><summary>检查</summary>

注意力：2 × 4096² + 2 × 4096 × 1024 = 33.6M + 8.4M = 42.0M。
MLP：3 × 4096 × 14336 = 176.2M。
每层：218.2M。乘以 32 层 ≈ 6.98B。

大致是一个 7B 的模型，其中 MLP 占 81%。

</details>

4. ▢ 两个模型都报告 7B 个参数。一个词表 32k，另一个 256k。有什么不同，差多少？

<details markdown="1"><summary>检查</summary>

嵌入的开销。隐藏维度为 4096 时，词表 32k 每份是 131M 个参数；词表 256k 则是 1.05B，一张表就占整个模型的 15% 左右，如果输出投影不共享权重，还要翻倍。

因此大词表模型在 Transformer 块里的参数明显更少，而适配器恰恰挂在块里。

</details>

5. ▢ 有人说 7B 模型很宽裕地放得进 16 GB 来做微调，因为 bf16 权重是 14 GB。这个推理错在哪里？

<details markdown="1"><summary>检查</summary>

他们只数了权重。全量微调还需要每个可训练参数一份梯度和两份优化器矩，外加激活值，加起来是权重开销的好几倍。就算按 14 GB 算，也只给其他一切留下了 2 GB。

下一课会把它变成一个确切的数字，而答案差得很远。

</details>

## 实战练习

- [ ] 挑三个不同大小的模型。仅凭它们的配置文件（`hidden_size`、`intermediate_size`、`num_hidden_layers`、`num_key_value_heads`、`vocab_size`）算出参数量，并与模型卡核对。
- [ ] 用 bf16 加载一个模型，测量实际用掉的内存。与你的预测比较，并解释任何差距。
- [ ] 明天：对五种模型大小，在脑子里估算 bf16 的 GB 数，再用计算器验证。

## 延伸阅读

- [文档：Model memory anatomy，Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/model_memory_anatomy)
- [内存预算](../reference/memory-budget.md)：本课所铺垫的那张表
- [第 6 课：梯度与优化器状态](0006-gradients-and-optimizer-state.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
