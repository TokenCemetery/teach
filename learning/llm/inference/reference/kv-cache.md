---
title: KV Cache
description: Byte accounting for the KV cache, per-token cost, head sharing, growth across a request, and capacity planning
type: reference
---

# KV Cache

Byte accounting for the KV cache. Built for lookup when sizing a deployment.

## Per-token cost

```text
bytes per token = 2 (K and V) × num_layers × num_kv_heads × head_dim × bytes_per_value
```

`head_dim = d_model / num_heads`. The cache holds one K/V pair per **KV head**, not per query head. Under multi-head attention (MHA), `num_kv_heads = num_heads` and this reduces to `2 × num_layers × d_model × bytes_per_value`. Under grouped-query attention (GQA) or multi-query attention (MQA), `num_kv_heads` is smaller and the cache shrinks by that same ratio, for free, with no change to context length or batch size.

| Scheme | `num_kv_heads` | Relative cache size |
|---|---|---|
| MHA | equals `num_heads` | 1x |
| GQA | a fraction of `num_heads` | that same fraction |
| MQA | 1 | `1 / num_heads` |

**Worked example, Llama-2-70B** (80 layers, 64 query heads, 8 KV heads, `head_dim` = 128, fp16):

```text
GQA: 2 × 80 × 8  × 128 × 2 bytes =   327,680 bytes ≈ 320 KB/token
MHA: 2 × 80 × 64 × 128 × 2 bytes = 2,621,440 bytes ≈ 2.5 MB/token   (8x GQA, the num_heads:num_kv_heads ratio)
```

## Growing into a total footprint

```text
total cache bytes = bytes per token × context length × batch size
```

| Model | Per token | Context | Batch | Total |
|---|---|---|---|---|
| Llama-2-7B, MHA, fp16 | 512 KB | 4096 | 1 | ~2 GB |
| Llama-2-7B, MHA, fp16 | 512 KB | 4096 | 16 | ~32 GB |
| Llama-2-70B, GQA, fp16 | 320 KB | 4096 | 1 | ~1.25 GB |
| Llama-2-70B, GQA, fp16 | 320 KB | 4096 | 32 | ~40 GB |

## Capacity budget

```text
max concurrent sequences = (total memory - weights - overhead) / (bytes per token × context length)
```

Llama-2-70B, tensor-parallel across four 80 GB GPUs (320 GB pool), weights plus framework overhead measured at 160 GB, 4096-token context:

```text
160 GB / 1.25 GB per sequence ≈ 128 concurrent sequences
```

That ceiling, not the model's raw throughput, is usually what a batching scheduler is negotiating against.

## Prefill claims most of the footprint in one step

| Phase | What it does | Cache growth |
|---|---|---|
| Prefill | Processes the whole prompt in one forward pass | Jumps to `bytes per token × prompt length` immediately; compute-bound |
| Decode | Generates one output token at a time | Grows by `bytes per token` per step; memory-bandwidth bound |

**Worked example**, a 2048-token prompt followed by 128 decode steps, Llama-2-70B at 320 KB/token:

```text
prefill: 320 KB × 2048 ≈ 640 MB   (94% of the request's final cache)
decode:  320 KB × 128  ≈  40 MB   (6%, added gradually)
total:   680 MB
```

A capacity plan built only from "final context length" hides that most of the footprint lands at prefill, in a single step, not spread across the request.

## Cache precision is a lever independent of the model's own weights

`bytes_per_value` above does not have to match the precision the model computes in. A serving stack can store the cache itself at a lower precision, commonly fp8, while the model computes in bf16 or fp16. It stacks multiplicatively with head sharing rather than substituting for it.

```text
Llama-2-70B, GQA, fp16: 320 KB/token
Llama-2-70B, GQA, fp8:  160 KB/token   (half, only bytes_per_value changed)
```

64 sequences at a 4096-token context: fp16 costs ~80 GB, fp8 costs ~40 GB, exactly half, on top of whatever GQA already bought back from full MHA.

## Related

- [Lesson 1](../lessons/0001-the-kv-cache.md), [Lesson 2](../lessons/0002-capacity-and-batch-size.md), [Lesson 3](../lessons/0003-growth-prefill-decode-precision.md)
