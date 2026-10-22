---
title: "10. 选择目标模块"
description: "只作用于注意力是 2021 年的一项消融实验，不是默认做法"
type: lesson
---

# 第 10 课：选择目标模块

**使命关联:** 目标模块比秩更重要，而关于它们的既有常识已经过时。在这里，你可以做到比一般的从业者更好，而且是可度量的更好。
**主要来源:** [文档：“LoRA Without Regret”，Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
**前置知识:** [第 2 课](0002-where-the-weights-live.md)、[第 9 课](0009-rank-alpha-and-initialisation.md)

## 热身

1. ▢ `α/r` 控制什么，单独的 `r` 控制什么？

<details markdown="1"><summary>检查</summary>

`α/r` 设定适配器贡献的尺度。单独的 `r` 设定它的容量：它能表达多复杂的更新。

</details>

2. ▢ 哪个子层持有 Transformer 块的大部分参数？

<details markdown="1"><summary>检查</summary>

MLP，大约占块的 75% 到 80%，因为中间维度是隐藏维度的好几倍，而分组查询注意力又缩小了四个注意力投影中的两个。

</details>

3. ▢ 零初始化的 `B` 保证了什么？

<details markdown="1"><summary>检查</summary>

在第一次优化器步骤之前，适配后的模型与基础模型完全相同。

</details>

## 要点

### 原始论文做了什么，以及为什么那不是建议

LoRA 论文只适配了注意力投影，实验中主要是 `W_q` 和 `W_v`，而没有动 MLP。这个选择一传就是好几年的教程，`target_modules=["q_proj", "v_proj"]` 就是这么来的。

关于它，有两点要明白。在内存预算有限、针对所测的任务时，那是一个合理的发现。而它**并不是**关于适配应当发生在哪里的一般性结论。把 2021 年的一项消融实验当作默认做法，是这个领域里最常见的一种沿袭而来的错误。

### 支持 MLP 的理由

根据第 2 课：MLP 持有每个块大约五分之四的参数。有相当多的可解释性工作，把 MLP 层视为模型所学知识和特征检测的主要所在，而注意力负责在各个位置之间路由信息。如果你的任务需要模型以不同的方式去*了解*或*分类*某样东西，编码这些的参数，不成比例地集中在 MLP 里，只作用于注意力的适配器够不着它们。

### 当前的默认做法

近期的工作汇聚到一条直截了当的建议：**适配所有线性层**，并给适配器足够的秩。TRL 对“LoRA without regret”结果的总结很明确：对每个线性层（包括 MLP）应用 LoRA，并给足够的秩，在监督微调的工作负载上就能追平全量微调的差距，而只作用于注意力的配置做不到。

```text
# The modern default: let the library find every linear layer.
config := {rank: 64, alpha: 128, target_modules: "all-linear"}

# The explicit equivalent, for a Llama-style architecture.
config := {
    rank: 64,
    alpha: 128,
    target_modules: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
}
```

两者之中 `"all-linear"` 更安全，因为面对模块名与你背下来的清单不同的架构，它不会过时。它的代价是你放弃了精确的控制，所以应该检查它实际匹配到了什么。

为什么现在负担得起：根据第 7 课，适配器参数在训练内存中占的份额可以忽略。限制目标模块来省内存，在 2021 年是一笔真实的交易，如今几乎不算一笔交易了。你实际在交易的，是小数据集上的过拟合风险。

### 决策

| 情形 | 目标 | 理由 |
|---|---|---|
| 真实任务的默认做法 | 所有线性层 | 单位努力下质量最好；符合当前的证据 |
| 小数据集（< 约 1k 个样本） | 只作用于注意力，低秩 | 刻意限制容量，以限制记忆 |
| 只涉及风格或语气 | 只作用于注意力，低秩 | 小的行为改变只需要小的更新 |
| 任务需要新的区分能力 | 必须包含 MLP | 只作用于注意力的话，够不到这些能力所在的地方 |
| 复现一篇论文 | 恰好是论文所用的 | 否则你就不是在复现它 |

### 人们常问的两类模块

**嵌入与输出头。** 通常不去动。适配它们，相对于收益来说代价高昂，而且这是改动权重可能改变每一个 token 含义的唯一地方。真正的例外是添加新的特殊 token，这需要改动嵌入表，它与适配嵌入表是另一种操作。

**偏置项。** `bias="none"` 是标准设置。同时训练偏置（`"all"` 或 `"lora_only"`）开销不大，但很少成为一次运行成败的关键，而且会让合并变得复杂。

### 能抓住真正错误的检查

每一次都要打印出匹配到了什么：

```text
model := attach_adapter(base_model, config)
print(model.trainable_parameter_count())
print(first 8 parameter names containing "lora")
```

什么也没匹配上的目标模块名，要么产生一个错误，要么（取决于版本）产生一个根本没有适配器的模型，它会训练、会记录损失，却什么也学不到。可训练参数量与你第 8 课的算术不符，是最早可能出现的警告。

## 练习

1. ▢ 原始论文为什么只针对注意力，为什么这在今天不是默认做法？

<details markdown="1"><summary>检查</summary>

那是在紧张的内存预算下、针对作者所测的任务做的一项消融实验，当时限制可训练参数很重要。它从来不是在主张适配应当属于注意力。

如今适配器的内存可以忽略，证据倾向于用足够的秩覆盖所有线性层。

</details>

2. ▢ 你的任务要求模型区分它目前混为一谈的领域概念。只作用于注意力，还是所有线性层？

<details markdown="1"><summary>检查</summary>

所有线性层。做出新的区分，意味着改变特征检测和存储的关联，它们不成比例地存在于 MLP 里。注意力负责路由信息，这种区分不是在那里被编码的。

</details>

3. ▢ 你有 400 个训练样本。论证一下为什么要限制目标模块。

<details markdown="1"><summary>检查</summary>

只有 400 个样本，容量是风险，而不是约束。一个覆盖所有线性层、秩给得宽裕的适配器，完全可以把这个集合直接背下来：训练损失接近零，留出集损失攀升，毫无泛化。

在低秩下只作用于注意力，是刻意的容量限制，起到正则化的作用。如果可行，更好的答案是获取更多数据。

</details>

4. ▢ 在数据集合理的真实任务上，哪项改动最有可能提高质量？

    - a) 把适配器的秩从 16 提高到 64
    - b) 把目标扩展到所有线性层
    - c) 给这次运行加上 0.05 的 LoRA dropout
    - d) 多训练一整个 epoch

<details markdown="1"><summary>检查</summary>

**b)** 把目标扩展到所有线性层。

它让大约四倍的参数进入了可适配的范围，包括 MLP。提高秩，是在你已经触及的那些层之内增加容量。dropout 起正则化作用，而不是改善拟合。多一个 epoch 会有过拟合的风险，却没有增加容量。

</details>

5. ▢ 你设了 `target_modules=["c_attn"]`，运行起来，损失几乎不动。你首先检查什么？

<details markdown="1"><summary>检查</summary>

这个模型里到底有没有 `c_attn`。它是 GPT-2 式架构里融合的注意力投影，在 Llama 式架构里并不存在，后者使用分开的 `q_proj`、`k_proj`、`v_proj`。

打印模块名，然后运行 `print_trainable_parameters()`。可训练数量接近零，就是答案。

</details>

6. ▢ 为什么 `"all-linear"` 比显式的模块清单更安全？

<details markdown="1"><summary>检查</summary>

它是对照已加载的模型来解析的，而不是对照你的记忆，所以在命名不同的架构上，它不会悄悄漏掉某些层。

它的代价是失去精确性，所以要核实它匹配到了什么，并留意它可能包含你更愿意放着不动的层。

</details>

## 实战练习

- [ ] 在同一个模型上，以相同的秩，构建一个只作用于注意力的适配器和一个作用于所有线性层的适配器。记录两者的可训练参数量及其比值。
- [ ] 打印适配器的参数名，核实 `"all-linear"` 匹配到了哪些模块。记下任何出乎意料的地方。
- [ ] 明天：找三份网上公开的微调配置，记下哪些只针对注意力。判断作者是自己选的，还是沿袭来的。

## 延伸阅读

- [文档：“LoRA Without Regret”，Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
- [博客：“Practical Tips for Finetuning LLMs Using LoRA”，Sebastian Raschka](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms)：目标模块的消融实验
- [LoRA 超参数](../reference/lora-hyperparameters.md)
- [第 11 课：你的第一个适配器](0011-your-first-adapter.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
