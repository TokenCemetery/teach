---
title: Activations and the KV Cache
description: Weight-only against weight-and-activation, SmoothQuant, rotations and KV-cache quantization for lookup
type: reference
---

# Activations and the KV Cache: Quantizing Beyond the Weights

Stage 5 compressed for lookup. [Lesson 13](../lessons/0013-weights-activations-or-both.md) covers weight-only against weight-and-activation, [lesson 14](../lessons/0014-smoothquant.md) SmoothQuant, [lesson 15](../lessons/0015-rotations.md) rotations, and [lesson 16](../lessons/0016-kv-cache-quantization.md) KV-cache quantization.

## Weights, activations or both

| Scheme | Stored small | Matmul runs in | Buys | Fits |
|---|---|---|---|---|
| W4A16, W8A16 (weight-only) | Weights | 16-bit, after dequantizing in the kernel | Memory, bytes read per token | Memory-bound: small-batch decode |
| W8A8 int8 or fp8 | Weights and activations | 8-bit | Arithmetic throughput, plus memory | Compute-bound: prefill, large batches |
| W4A4 with rotations | Weights, activations, often KV | 4-bit | Memory and arithmetic | Only where a 4-bit kernel exists, see lesson 20 |

Kurtic et al. (Llama 3.1 family, over 500,000 evaluations): fp8 W8A8 effectively lossless, well-tuned int8 W8A8 1 to 3% degradation, W4A16 int rivals 8-bit. Advice: W4A16 for synchronous serving, W8A8 for continuous batching.

## Why activations are harder

| Property | Weights | Activations |
|---|---|---|
| Range known | After training, fixed | Only at run time |
| Outliers | Flat, easy to quantize | About 100 times most values, in fixed channels across all tokens (SmoothQuant) |
| Scale granularity an int8 GEMM allows | Per output channel | Per tensor or per token only |

The int8 GEMM: `Y = diag(s_X) · (X_int8 @ W_int8) · diag(s_W)`. Scales sit on the outer dimensions only; a per-input-channel scale would sit inside the sum.

| Activation scale | Computed | Cost | Risk |
|---|---|---|---|
| Static | Offline, from a calibration set | None per request | Calibration set unlike real traffic |
| Dynamic | At run time, from the tensor | A reduction before each matmul | Little; adapts per input |

## SmoothQuant

```text
X @ W = (X @ diag(s)^-1) @ (diag(s) @ W)
s_j   = max(|X_j|)^α / max(|W_j|)^(1 - α)
```

| `α` | Effect |
|---|---|
| 0 | Activations unchanged |
| 0.5 | Paper's balanced default, sweet spot for OPT and BLOOM |
| Larger, toward 1 | More difficulty into weights; for models with heavier outliers, such as GLM-130B |
| 1 | Every activation channel has the same maximum; weights carry all outliers |

- `max(|X_j|)` comes from a calibration set.
- The factor is fused offline into the layer that produces `X`: no run-time cost.
- An 8-bit method: up to 1.56x speed-up and 2x memory reduction in the paper.

## Rotations

```text
X @ W = (X @ Q) @ (Q.T @ W)      where Q @ Q.T = I
```

| Point | Detail |
|---|---|
| What it does | Spreads an outlier across all channels; max close to RMS |
| Usual `Q` | Randomized Hadamard: entries ±1/sqrt(n), cost `n log n` |
| Fused offline | Rotation of the residual stream, into the weights |
| Online | Before the FFN down-projection; head-wise on queries and keys, after RoPE |
| QuaRot | All weights, activations and KV cache in 4 bits; Llama 2 70B within 0.47 WikiText-2 perplexity, 99% of zero-shot |
| SpinQuant | Random rotations differ by up to 13 zero-shot points; learned rotations cut the gap to 2.9 points on Llama 2 7B W4A4KV4 |

Review question for any W4A4 claim: which rotation, and was it chosen or learned for this model?

## KV-cache quantization

```text
KV bytes per token = 2 x layers x kv_heads x head_dim x bytes_per_value
```

Llama 3 8B (32 layers, 8 KV heads, dimension 128) in bf16: 128 KiB per token, 4 GiB per 32,768-token sequence.

| Tensor | Quantize along | Why |
|---|---|---|
| Keys | Per channel, before RoPE where possible | A few fixed outlier channels (KIVI); RoPE mixes channel pairs (KVQuant) |
| Values | Per token | No channel pattern; almost 15 times less attention-output error than per channel (KIVI) |

| Method or option | Bits | Reported result |
|---|---|---|
| KIVI | 2 | Almost same quality, 2.6x less peak memory, up to 4x batch, 2.35 to 3.47x throughput |
| KVQuant | 3 | Under 0.1 perplexity degradation; LLaMA-7B at 1M context on one 80 GB A100 |
| vLLM fp8 KV cache | 8 | Per-tensor or per-head scales; default scales 1.0 without calibration, calibration recommended |

KIVI keeps the newest tokens (128 in its experiments) in full precision until a per-channel group of keys is complete.
