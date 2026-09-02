---
title: Memory Budget
description: Byte accounting, and what to try when a run will not fit
type: reference
---

# Memory Budget

Byte accounting for adapter fine-tuning. Built for lookup during a run.

## Bytes per parameter

| Format | Bytes | Bits |
|---|---|---|
| fp32 | 4 | 32 |
| bf16 / fp16 | 2 | 16 |
| int8 | 1 | 8 |
| 4-bit, raw | 0.5 | 4 |
| 4-bit + fp32 scales, block 64 | 0.5625 | 4.5 |
| 4-bit + double quant | ~0.516 | ~4.13 |

**Reflex:** bf16 gigabytes ≈ 2 × parameters in billions.

## Per-parameter training cost

| Category | fp32 | Mixed precision |
|---|---|---|
| Weights | 4 | 2 bf16 + 4 fp32 master |
| Gradients | 4 | 2 |
| AdamW moment 1 | 4 | 4 |
| AdamW moment 2 | 4 | 4 |
| **Trainable total** | **16** | **16** |
| **Frozen total** | **4** | **2** |

Mixed precision does not reduce the total. It buys arithmetic throughput.

| Optimizer variant | Bytes/param |
|---|---|
| AdamW, fp32 moments | 16 |
| AdamW, 8-bit moments | 10 |
| SGD with momentum | 12 |

## Parameter counts

```text
attention/layer = 2·d² + 2·d·d_kv          # q,o full; k,v narrowed by GQA
mlp/layer       = 3·d·d_ff                  # gate, up, down
model           ≈ n_layers·(attn + mlp) + vocab·d·(1 if tied else 2)
```

The MLP is typically 75 to 80% of a block.

## Adapter parameter count

```text
adapter = Σ over targeted layers:  r · (d_in + d_out)
```

Dominated by the **larger** dimension, so GQA narrowing barely shrinks an adapter.

| Base | Targets | Rank | Adapter | % of base |
|---|---|---|---|---|
| ~1.1B, d=2048 | attention | 8 | 2.5M | 0.22% |
| ~7B, d=4096 | q,v | 16 | 6.8M | 0.10% |
| ~7B, d=4096 | all-linear | 64 | ~160M | ~2.3% |

## Activations

```text
activations ≈ n_layers · batch · seq_len · d · ~20 bytes
```

The constant is a starting point to measure against, not a law. Linear in batch and sequence length; the attention-score quadratic term is removed by a memory-efficient attention kernel.

| Config | Estimate |
|---|---|
| 24 layers, d=2048, batch 4, seq 2048 | ~8 GB |
| 32 layers, d=4096, batch 2, seq 4096 | ~21 GB |

Gradient checkpointing cuts this by roughly an order of magnitude for ~20 to 40% more step time.

**In an adapter run, activations usually dominate.** This inverts the full fine-tuning profile.

## Worked totals, excluding activations

| Setup | Fixed memory |
|---|---|
| Full FT, 1.5B, AdamW | 24 GB |
| Full FT, 7B, AdamW | 112 GB |
| Full FT, 70B, AdamW | 1120 GB |
| bf16 7B base + 20M adapter | 14.3 GB |
| NF4 7B base + 20M adapter | ~3.9 GB |
| NF4 13B base + 30M adapter | ~7.2 GB |

## When a run does not fit

In order of what you give up:

1. **Gradient checkpointing**, costs time only
2. **Lower batch size, raise gradient accumulation**, statistically equivalent
3. **Shorter sequence length**, but check the token-length distribution first; this changes the task
4. **Quantise the base**, costs some quality
5. **Lower rank**, saves the least and costs capacity

Rank is the instinct and nearly the worst option. Halving rank on a 4M adapter saves ~32 MB.

## Effective batch size

```text
effective = per_device_batch × grad_accumulation × num_devices
```

Always report the effective number.

## Related

- [Lesson 5](../lessons/0005-counting-parameters-and-bytes.md), [Lesson 6](../lessons/0006-gradients-and-optimizer-state.md), [Lesson 7](../lessons/0007-activations-and-checkpointing.md), [Lesson 15](../lessons/0015-nf4-and-double-quantisation.md)
