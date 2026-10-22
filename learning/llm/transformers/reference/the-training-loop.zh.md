---
title: "训练循环"
description: "词表上的交叉熵损失、反向传播与自动求导，以及 AdamW 优化器步骤，从 logits 到更新后的权重"
type: reference
---

# 训练循环：损失、反向传播与优化器

第 4 阶段，压缩成便于查阅的形式。[第 9 课](../lessons/0009-cross-entropy-loss.md)讲把 logits 变成单一的标量损失，[第 10 课](../lessons/0010-backward-pass-and-autograd.md)讲把这个标量变成每个权重的梯度，[第 11 课](../lessons/0011-adamw-optimizer.md)讲把梯度变成权重更新。这张速查表按训练实际使用的顺序，列出这三个公式。

## 交叉熵损失

```text
loss = -log(p_correct)
```

| `p_correct` | 损失 | 含义 |
|---|---|---|
| 0.8 | `-log(0.8) ≈ 0.223` | 有把握而且对了，惩罚很小 |
| 0.1 | `-log(0.1) ≈ 2.303` | 有把握却错了，概率下降到十分之一，惩罚大了 10 倍以上 |

随着 `p` 趋近 0，`-log(p)` 无界地增长；更简单的 `1 - p` 惩罚在 1 处饱和，无法区分“有点错”与“错得离谱又自信”。它对 logits 的梯度也很干净（`softmax_output - one_hot_true_label`），这就是 softmax 和交叉熵几乎总是搭配在一起的原因，常常实现为一个直接作用于原始 logits 的、融合的、数值稳定的运算。

**教师强制。** 训练时始终把真实的前面 token 作为上下文送进去，而从不用模型自己的预测。由于因果掩码已经限定每个位置只能向后关注，每个位置的预测，进而每个位置的损失，都在一次前向传播里算出，而不是每个位置各需一次传播。每个位置、每个批次的损失被平均成一个标量，因为梯度下降需要一个单一的量来最小化。

## 反向传播与自动求导

每个前向运算（矩阵乘法、softmax、一次残差相加）都被记录进一张**计算图**。`loss.backward()` 沿着它倒着走，利用每个运算已经实现的局部反向规则，自动应用链式法则，填充每个可训练参数的 `.grad`。

链式法则的例题：`y = 3x + 1`，`z = y^2`，在 `x = 2` 处：`y = 7`，`dz/dy = 2y = 14`，`dy/dx = 3`，所以 `dz/dx = 14 x 3 = 42`。

| 方法 | 如何得到梯度 | 代价 |
|---|---|---|
| 符号微分 | 手工或借助计算机代数推导出闭式的公式 | 不是 autograd 所做的 |
| 数值微分 | 对每个参数做扰动，重新运行前向传播 | 不精确，每个参数多一次前向传播 |
| 自动微分（autograd） | 在记录下来的图上，把每个运算已经实现的局部反向规则串联起来 | 精确，一次反向遍历同时得到所有参数的梯度 |

**为什么残差真正防止了梯度消失。** 对于 `y = x + Sublayer(x)`，`d(loss)/d(x) = d(loss)/d(y) x 1 + [经过 Sublayer 的一项]`。恒等路径的局部导数恰好是 1，所以不论 `Sublayer` 自己的导数变得多小，直接的那一项都不经缩放地传过去。这是机械的原因，而不只是一种直觉。

**梯度是累加的，而不是覆盖的。** `.grad` 会加到原来已有的内容上，所以训练循环必须在每次新的 `backward()` 调用之前显式地把梯度清零，否则一步的梯度会被上一步遗留的内容污染。

## AdamW 优化器步骤

```text
plain gradient descent:  w = w - lr * grad
Adam's moments:           m = beta1 * m + (1 - beta1) * grad          (momentum)
                          v = beta2 * v + (1 - beta2) * grad^2        (adaptive scale)
Adam's update:            w = w - lr * m_hat / (sqrt(v_hat) + eps)
AdamW's update:           w = w - lr * (m_hat / (sqrt(v_hat) + eps) + weight_decay * w)
```

（`m_hat`、`v_hat` 是对 `m`、`v` 做了偏差修正的结果，因为两者都从零开始。）

| 部分 | 增加了什么 | 修正了什么 |
|---|---|---|
| 动量（`m`） | 过去梯度的滑动平均 | 逐批次梯度的噪声；更新沿着一致的方向走，而不是抖动 |
| 自适应缩放（`v`） | 每个参数典型梯度量级的估计 | 对每个权重使用同一个固定的学习率；梯度小的参数得到相对更大的步长，梯度大的则更小 |
| 解耦的权重衰减（AdamW） | 权重衰减直接施加在 `w` 上，从不经过 `m`、`v` 或自适应的分母 | 把衰减折进梯度（原始 Adam），会让它的有效收缩取决于每个参数典型的梯度量级，而不是衰减本该有的均匀收缩 |

例题：`w = 5.0`，`grad = 2.0`，`lr = 0.1`，朴素梯度下降：`w = 5.0 - 0.1 x 2.0 = 4.8`。

## 信任一个训练循环的实现之前

- [ ] 交叉熵直接接收原始 logits（一个融合了 softmax 和负对数概率的运算），而不是手工做 softmax，再单独做一步取对数。
- [ ] 训练送入的是真实的前面 token（教师强制），而且损失是在一次前向传播里为每个位置算出的，而不是每个位置各需一次传播。
- [ ] 在每次 `backward()` 调用之前，显式地把梯度清零。
- [ ] 如果用了权重衰减，优化器是 AdamW，而不是普通的 Adam，并且权重衰减是直接施加在权重上的，而不是折进梯度。

## 来源

- [文档：“torch.nn.functional.cross_entropy”，PyTorch](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
- [文档：“Autograd mechanics”，PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
- [论文：“Decoupled Weight Decay Regularization”，Loshchilov 和 Hutter，2019](https://arxiv.org/abs/1711.05101)
- [论文：“Adam: A Method for Stochastic Optimization”，Kingma 和 Ba，2015](https://arxiv.org/abs/1412.6980)
- [资源](../RESOURCES.md)
