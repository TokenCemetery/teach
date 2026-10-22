---
title: "KV 缓存"
description: "KV 缓存的字节核算：每个 token 的开销、头共享、一次请求中的增长，以及容量规划"
type: reference
---

# KV 缓存

KV 缓存的字节核算。为在给部署定规模时查阅而做。

## 每个 token 的开销

```text
bytes per token = 2 (K and V) × num_layers × num_kv_heads × head_dim × bytes_per_value
```

`head_dim = d_model / num_heads`。缓存为每个 **KV 头**保存一对 K/V，而不是为每个查询头保存。在多头注意力（MHA）下，`num_kv_heads = num_heads`，上式化简为 `2 × num_layers × d_model × bytes_per_value`。在分组查询注意力（GQA）或多查询注意力（MQA）下，`num_kv_heads` 更小，缓存按同样的比例缩小，这是白送的，上下文长度和批大小都不用改。

| 方案 | `num_kv_heads` | 相对缓存大小 |
|---|---|---|
| MHA | 等于 `num_heads` | 1x |
| GQA | `num_heads` 的一个分数 | 同样的分数 |
| MQA | 1 | `1 / num_heads` |

**算例，Llama-2-70B**（80 层，64 个查询头，8 个 KV 头，`head_dim` = 128，fp16）：

```text
GQA: 2 × 80 × 8  × 128 × 2 bytes =   327,680 bytes ≈ 320 KB/token
MHA: 2 × 80 × 64 × 128 × 2 bytes = 2,621,440 bytes ≈ 2.5 MB/token   (8x GQA, the num_heads:num_kv_heads ratio)
```

## 累积成总占用

```text
total cache bytes = bytes per token × context length × batch size
```

| 模型 | 每 token | 上下文 | 批大小 | 合计 |
|---|---|---|---|---|
| Llama-2-7B，MHA，fp16 | 512 KB | 4096 | 1 | ~2 GB |
| Llama-2-7B，MHA，fp16 | 512 KB | 4096 | 16 | ~32 GB |
| Llama-2-70B，GQA，fp16 | 320 KB | 4096 | 1 | ~1.25 GB |
| Llama-2-70B，GQA，fp16 | 320 KB | 4096 | 32 | ~40 GB |

<a id="capacity-budget"></a>

## 容量预算

```text
max concurrent sequences = (total memory - weights - overhead) / (bytes per token × context length)
```

Llama-2-70B，张量并行跨四块 80 GB 的 GPU（320 GB 内存池），权重加框架开销实测为 160 GB，上下文 4096 个 token：

```text
160 GB / 1.25 GB per sequence ≈ 128 concurrent sequences
```

批处理调度器要与之周旋的，通常是这个上限，而不是模型的原始吞吐量；见[批处理](batching.md)。

## 预填充一步就占去大部分占用

| 阶段 | 做什么 | 缓存增长 |
|---|---|---|
| 预填充 | 在一次前向计算中处理整个提示词 | 立刻跳到 `bytes per token × prompt length`；受算力限制 |
| 解码 | 一次生成一个输出 token | 每步增加 `bytes per token`；受内存带宽限制 |

**算例**，2048 个 token 的提示词，后接 128 步解码，Llama-2-70B，每 token 320 KB：

```text
prefill: 320 KB × 2048 ≈ 640 MB   (94% of the request's final cache)
decode:  320 KB × 128  ≈  40 MB   (6%, added gradually)
total:   680 MB
```

只根据“最终上下文长度”做的容量规划，掩盖了一个事实：大部分占用是在预填充时一步到位落下的，而不是分摊在整个请求里。

<a id="cache-precision-is-a-lever-independent-of-the-models-own-weights"></a>

## 缓存精度是独立于模型自身权重的杠杆

上面的 `bytes_per_value` 不必与模型计算时使用的精度一致。服务栈可以用更低的精度存储缓存本身，常见的是 fp8，而模型仍以 bf16 或 fp16 计算。它与头共享是相乘叠加的，而不是互相替代。

```text
Llama-2-70B, GQA, fp16: 320 KB/token
Llama-2-70B, GQA, fp8:  160 KB/token   (half, only bytes_per_value changed)
```

64 个序列、上下文 4096 个 token：fp16 要花约 80 GB，fp8 要花约 40 GB，恰好减半，而且这还是在 GQA 已经相对完整的 MHA 省回的基础之上。

## 相关内容

- [第 1 课](../lessons/0001-the-kv-cache.md)、[第 2 课](../lessons/0002-capacity-and-batch-size.md)、[第 3 课](../lessons/0003-growth-prefill-decode-precision.md)
- [批处理](batching.md)：本表所算出的容量上限，实际约束着什么
