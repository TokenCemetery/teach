---
title: "蒸馏损失"
description: "软目标、温度、组合损失、token 级损失、前向 KL 与反向 KL、分词器的约束，以及存储 logit 的代价"
type: reference
---

# 蒸馏损失：第 1 和第 2 阶段速查

第 1 和第 2 阶段，压缩成便于查阅的形式。[第 1 至 3 课](../lessons/0001-what-distillation-buys.md)讲软目标和温度，[第 4 课](../lessons/0004-token-level-distillation.md)讲 token 级损失，[第 5 课](../lessons/0005-forward-and-reverse-kl.md)讲散度的方向，[第 6 课](../lessons/0006-the-tokenizer-constraint.md)讲分词器的约束，[第 7 课](../lessons/0007-distilling-during-pretraining.md)讲教师分布在大规模下的成本。

## 软目标与温度

| 术语 | 定义 | 出处 |
|---|---|---|
| 软目标 | 教师在每个类别上的概率，用来取代硬标签，或与硬标签一起作为目标 | Hinton 等，2015，第 1 节 |
| 带温度的 softmax | q_i = exp(z_i / T) / sum_j exp(z_j / T)。T = 1 是普通的 softmax，T 越高，分布越柔和 | Hinton 等，公式 1 |
| T 用在哪里 | 训练期间教师和学生使用同样的高 T。之后学生在 T = 1 下运行 | Hinton 等，第 2 节 |
| 温度 T 下的梯度 | dC/dz_i = (1/T)(q_i - p_i)。对大的 T 和零均值的 logit，它约为 (1/(N T^2))(z_i - v_i)，所以匹配 logit 是一个特例 | Hinton 等，第 2.1 节 |
| T 平方因子 | 软目标梯度按 1/T^2 缩放，所以把软损失与硬损失结合时，要把软损失乘以 T^2 | Hinton 等，第 2 节 |

这个因子在一次运行里的表现，取 logit `[9, 4, 2, 0, -4]` 对 `[6, 5, 0, 1, -2]`：最大的梯度分量在 T = 1 时是 0.2663，在 T = 20 时是 0.0017，乘以 T 的平方之后，从 T = 2 到 T = 20，它一直保持在 0.64 到 0.84 之间（[第 3 课](../lessons/0003-temperature.md)）。

## 组合损失

```text
loss = lambda * T^2 * CE(teacher at T, student at T) + (1 - lambda) * CE(label, student at 1)
```

这个记号是本系列的。Hinton 等人描述的是两个交叉熵的加权平均，并且发现通常把较低得多的权重放在硬标签那一项上，效果最好。

| 设置 | 取值 | 出处与范围 |
|---|---|---|
| 语音，硬标签项上的相对权重 | 0.5 | Hinton 等，第 4.1 节，一个声学模型 |
| 语音，试过的温度 | 1、2、5、10 | Hinton 等，第 4.1 节 |
| MNIST，800 单元的学生，T = 20 下的软目标 | 74 个测试错误，单独训练是 146，教师是 67 | Hinton 等，第 3 节 |
| MNIST，30 单元的学生，最佳温度 | 2.5 到 4 | Hinton 等，第 3 节 |
| Kim 和 Rush 试过的词级混合权重 | 0.5 和 0.9，0.5 更好 | Kim 和 Rush，2016，第 4 节 |
| LLM 剪枝后重新训练，试过的温度 | 0.1、0.5、1.0、3.0，1.0 最好 | Muralidharan 等，2024，附录 A.3 |
| LLM 预训练，试过的温度 | 0.5 到 10，各个规模上都是 1 最好 | Busbridge 等，2025，附录 G.2 |
| LLM 剪枝后重新训练，损失的混合 | 单用 logit 损失，比混入语言建模损失更好 | Muralidharan 等，2024，第 4 节 |

每一行都是一篇论文在它自己的设置上的结果。两行 LLM 的温度结果与分类器的结果不一致，所以要在你自己的这一对模型上扫描 T，包括 1。

## token 级损失

| 项目 | 选择 |
|---|---|
| logit 的形状 | 学生和教师，各为 (batch, positions, vocab) |
| 散度所沿的轴 | 最后一个，即词表轴，得到 (batch, positions) |
| 前缀 | 一条固定的序列，人类文本或教师文本，输入给两个模型（教师强制） |
| 教师 | 关闭梯度的前向传播 |
| 归约 | Kim 和 Rush 对位置求和。GKD 和 Minitron 除以长度。屏蔽填充，并除以掩码之和 |
| 温度 | 在 log-softmax 之前，两组 logit 都除以 T；如果与硬项混合，把损失乘以 T^2 |

```python
import torch.nn.functional as F

def token_kd_loss(student_logits, teacher_logits, mask, T=1.0):
    s = F.log_softmax(student_logits / T, dim=-1)
    t = F.log_softmax(teacher_logits / T, dim=-1)
    kl = (t.exp() * (t - s)).sum(dim=-1)
    return (kl * mask).sum() / mask.sum()
```

针对教师的交叉熵与前向 KL 之差是教师的熵，对学生来说是一个常数，所以它们的梯度相同。Gemma 2 写的是 -P_T(x | x_c) log P_S(x | x_c) 之和（第 3.2 节）。

## 前向 KL 与反向 KL

| | 前向 KL | 反向 KL |
|---|---|---|
| 表达式 | KL(p \|\| q) = sum p log(p / q) | KL(q \|\| p) = sum q log(q / p) |
| p 是教师，q 是学生 | 按教师加权 | 按学生加权 |
| 惩罚 | 在教师有很多质量的地方，给得很少的学生 | 在教师几乎没有质量的地方，给了质量的学生 |
| 行为 | 覆盖模式，铺开去覆盖每个模式 | 寻找模式，只认定一个 |
| 在第 5 课的玩具例子上 | 偏爱铺开的学生，0.595 对 1.572 | 偏爱认定一个的学生，0.623 对 1.273 |

| 来源 | 发现 | 范围 |
|---|---|---|
| MiniLLM，Gu 等，2023 | 生成式蒸馏用反向 KL，因为前向 KL 会给教师的空白区域分配质量 | 指令遵循，在学生样本上做策略梯度 |
| GKD，Agarwal 等，2023 | 最佳的散度取决于任务。广义 JSD(beta) 做插值，接近 0 时像前向，接近 1 时像反向。在 FLAN 指令微调上，反向 KL 远好于前向 | T5 学生，XSum、WMT、GSM8K、FLAN |
| Minitron，Muralidharan 等，2024 | 前向 KLD 最好：在深度剪枝的 8B 上，语言建模损失是 2.155，反向是 2.665 | 重新训练剪枝后的基础模型 |

TRL 的 `GKDConfig` 把这个选择暴露为 `beta`：0.0 是 KL 散度，1.0 是逆 KL，默认值是 0.5。

## 分词器的约束

| 情形 | 什么可行 | 代价是什么 |
|---|---|---|
| 分词器相同 | token 级损失 | 需要教师的 logit |
| 学生由教师构建（DistilBERT、Minitron） | token 级损失 | 学生受限于教师的设计 |
| 分词器不同，logit 可用 | ULD 损失，或 TRL 的 GOLD 训练器 | 距离项丢失 token 身份、均匀代价的假设、粗糙的位置对齐 |
| 只有教师的文本 | 在它生成的序列上训练（第 3 阶段） | 学生从未见过教师的分布 |

ULD（Boizard 等，2024）：L = 对 t 求和的 CE(t) + lambda * W1(student, teacher)，lambda 取 1.5，W1 是按降序排序的概率向量的绝对差之和（第 3 节）。把质量放在错误 token 上的学生，在 W1 上可以得 0 分，所以由针对标准答案 token 的交叉熵来承载身份信号。

TRL，按第 6 课所读：`GKDTrainer` 接收一个分词器作为 `processing_class`，没有教师分词器的参数。GOLD 的文档写明它支持不同的分词器，配合 `use_uld_loss=True` 和 `teacher_tokenizer_name_or_path`，并且位于 `trl.experimental` 中。

## 存储教师 logit 的代价

[第 7 课](../lessons/0007-distilling-during-pretraining.md)的算术，使用 Gemma 2 的 256,128 个词表项（表 1）。每个概率 2 字节，以及 k = 256 配 4 字节的索引，是假设，不是报告里的数字。

| 量 | 值 |
|---|---|
| 每个 token 的完整分布，bf16 | 512,256 字节 |
| 每条 8,192 个 token 的序列的完整分布 | 4.20 GB |
| 2T 个 token 的完整分布（2B 的运行） | 1.02 EB |
| 8T 个 token 的完整分布（9B 的运行） | 4.10 EB |
| 每个 token 的 top-256，每项 6 字节 | 1,536 字节，小了 333.5 倍 |
| 2T 个 token 的 top-256 | 3.07 PB |
| 8T 个 token 的 top-256 | 12.29 PB |

Gemma 2 的报告没有描述教师的分布是如何提供的。Minitron 在训练的同时，用一次前向传播计算教师，并在相同算力下比较各次运行。Minitron 的 top-K 测试发现，K 达到 100 以内时准确率显著下降，K 更大时截断没有收益，那是一套重新训练剪枝模型的设置。

## 延伸阅读

- [资源](../RESOURCES.md)
- [术语表](../GLOSSARY.md)
