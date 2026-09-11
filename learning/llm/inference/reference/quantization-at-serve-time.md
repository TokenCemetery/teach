---
title: Quantization at Serve Time
description: int8/int4/GPTQ/AWQ weight quantization, why memory, speed and accuracy don't move together, and a decision framework for picking a scheme
type: reference
---

# Quantization at Serve Time

Weight quantization as a serving lever, independent of [KV cache](kv-cache.md) precision. Built for lookup when picking or defending a scheme.

## Schemes

| Scheme | Bit width | Mechanism | Accuracy at this width |
|---|---|---|---|
| int8 | 8 | Round-to-nearest | Usually fine naively |
| int4, naive | 4 | Round-to-nearest | Degrades sharply: only 16 representable values per weight, versus int8's 256 |
| GPTQ | 3-4 | Quantizes one column at a time; after each column, adjusts the remaining not-yet-quantized weights in that layer to compensate, using second-order sensitivity information | Corrects error after the fact, column by column |
| AWQ | 3-4 | Calibration pass finds the weight channels seeing the largest activation magnitudes; scales those channels to protect them before quantizing anything | Protects likely-sensitive weights before the fact |

GPTQ and AWQ target the same result, an accurate model at 4-bit weights, by opposite timing: GPTQ compensates for error already introduced; AWQ prevents it in the channels calibration flags as sensitive.

## Memory is the predictable axis; speed and accuracy are not

```text
memory ≈ fp16 footprint / (16 / bit_width)      # int8 halves it, int4 quarters it
```

**Worked example**, a 14 GB fp16 model: int8 is about 7 GB, int4 about 3.5 GB. This ratio holds regardless of which scheme (naive, GPTQ, AWQ) produced the quantized weights, and regardless of bit width beyond that.

Speed does **not** follow the memory ratio:

- A quantized weight often has to be **dequantized** back to a higher precision immediately before the matrix multiply runs, since the multiply hardware expects that precision. If that dequantization step costs time, the wall-clock speedup falls short of the memory ratio, unless the serving stack's kernel operates on the quantized format directly.
- Decode (memory-bandwidth bound) is where a smaller weight footprint pays off: less to read, less time reading it. Prefill (compute-bound) spends its time on the matmul itself, not on reading weights repeatedly, so the same quantization buys prefill much less speedup, sometimes close to none.

Accuracy needs a measured number, not an impression from sample outputs: **perplexity** (how well the model predicts held-out text; higher is worse) against the unquantized model, or a task-specific benchmark score delta. Fluent output is not evidence accuracy held up.

| Step | Memory | Speed | Accuracy |
|---|---|---|---|
| fp16 to int8 | Halves | Tracks memory reasonably well | Small, usually tolerable cost |
| int8 to int4 | Halves again | Depends on dequant overhead and kernel support | Grows disproportionately more than the int8 step, which is why GPTQ/AWQ exist |

None of the three axes moves in lockstep with the others, which is why a defensible choice needs a number for each.

## Picking a scheme: name the binding constraint first

Quantization is a fix for a constraint fp16 fails to meet, not a default step. If fp16 already fits the memory budget and meets the latency budget, quantizing buys nothing needed at a real accuracy cost.

| Binding constraint | What to do |
|---|---|
| Memory: weights plus the required [KV cache capacity](kv-cache.md#capacity-budget) don't fit | Quantize just enough to fit: int8 first (cheapest accuracy cost), int4 with GPTQ or AWQ only if int8 alone still doesn't leave room |
| Latency: model fits, but decode misses the budget | int8 or int4 can help, since decode is memory-bandwidth bound, but measure the actual speedup rather than assuming it from the bit width |
| Accuracy: a benchmark or perplexity ceiling can't be crossed | Doesn't rule out quantization, but rules out picking a scheme by memory or speed alone: measure GPTQ vs AWQ for this specific model, since they hold up differently model to model |

**Worked example**: a model's fp16 weights take 70 GB on an 80 GB GPU, leaving 10 GB for cache and overhead, too little for meaningful concurrency. That is a memory constraint. Quantizing to int8 drops weights to ~35 GB, freeing ~45 GB for cache, which raises the [capacity ceiling](kv-cache.md#capacity-budget) substantially. If int8 alone already satisfies both capacity and latency targets, dropping further to int4 buys memory nobody needs at a real, measured accuracy cost: quantizing past the binding constraint is the same mistake as quantizing when fp16 already fit.

## Defending the choice means citing three numbers

1. **The memory figure** that made quantization necessary, or the one showing it wasn't.
2. **The accuracy number** measured for the chosen scheme at the chosen bit width: a perplexity delta or benchmark score change against the unquantized model.
3. **The speed number** actually measured for the phase the budget covers (decode, in most latency-bound cases), since the wall-clock gain does not follow the memory ratio automatically.

A choice defended by only one of these ("int4 with AWQ gives the best memory savings") is not defended: it leaves the other two axes, and whether that much bit width was even required, unexamined.

## Related

- [Lesson 7](../lessons/0007-quantization-schemes.md), [Lesson 8](../lessons/0008-accuracy-speed-memory-tradeoffs.md), [Lesson 9](../lessons/0009-picking-a-quantization-scheme.md)
- [KV cache](kv-cache.md): the capacity ceiling a memory-constrained quantization decision is measured against
