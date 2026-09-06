---
title: 3. Growth, Prefill, Decode, and Precision
description: How the cache grows across prefill and decode, and what lowering its precision buys back
type: lesson
---

# Lesson 3. Growth, Prefill, Decode, and Precision

**Mission link:** A latency budget depends on when cache memory gets claimed during a request, not only on its final size, and on the other levers a server has over that size besides batch and context length.
**Primary source:** [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Prerequisites:** [Lesson 2](0002-capacity-and-batch-size.md), [KV cache](../GLOSSARY.md)

## Warm-up

1. ▢ Write the formula for a batch's total KV cache footprint, in terms of bytes per token, context length, and batch size.

<details markdown="1"><summary>Check</summary>

`total cache bytes = bytes per token × context length × batch size`.

</details>

2. ▢ Why does a model using grouped-query attention have a smaller KV cache than the same model under full multi-head attention?

<details markdown="1"><summary>Check</summary>

The cache holds one key/value pair per KV head, not per query head, and GQA uses fewer KV heads than query heads. The cache scales with `num_kv_heads`, which full MHA sets equal to `num_heads`.

</details>

## Know this

### The cache doesn't grow at a steady rate

A request has two phases, and they claim cache memory very differently.

**Prefill** processes the entire prompt in one forward pass: every prompt token's key and value vectors get computed and cached together, in a single step. The cache jumps from empty to `bytes per token × prompt length` before the model has generated a single output token. This phase is compute-bound: it is one large, parallel matrix multiplication over the whole prompt.

**Decode** then generates one output token at a time. Each step computes and caches exactly one more token's worth of keys and values, so the cache grows by `bytes per token` per step, a slow trickle by comparison. This phase is memory-bandwidth bound: each step has to read the entire cache back to attend over it, for only one new token's worth of new work.

A long prompt therefore claims most of a request's eventual cache footprint immediately, at prefill, while decode adds the rest gradually. A capacity plan that only looks at "final context length" is really asking "how big will this get after prefill plus however many decode steps I expect," and the two phases contribute on very different schedules.

### A lever independent of the model's own weights: cache precision

Lesson 2's formula carried `bytes_per_value` as its own term, separate from `num_layers`, `num_kv_heads`, and `head_dim`. That term does not have to match the precision the model computes in. A serving stack can store the KV cache itself in a lower precision, commonly fp8, while the model still computes in bf16 or fp16. Halving `bytes_per_value` from 2 bytes to 1 halves the cache's footprint outright, with no change to `num_kv_heads`, no change to context length, and no retraining: it is a serving-time choice, independent of whatever precision the weights were quantized to.

This stacks with everything from lesson 2. Take the Llama-2-70B numbers again (80 layers, 8 KV heads, `head_dim` = 128): at fp16, per-token cost was 320 KB. At fp8, it is `2 × 80 × 8 × 128 × 1 byte = 163,840 bytes ≈ 160 KB`, exactly half, because only `bytes_per_value` changed.

## Practice

1. ▢ A request has a 2048-token prompt. Using Llama-2-70B's fp16 figure of 320 KB per token, how much cache does prefill alone claim, before any output token is generated?

<details markdown="1"><summary>Check</summary>

`320 KB × 2048 ≈ 640 MB`, claimed in the single prefill step.

</details>

2. ▢ That same request then generates 128 output tokens by decode. How much additional cache does decode add, and what fraction of the request's total final cache does that represent?

<details markdown="1"><summary>Hint</summary>

Decode adds `bytes per token × number of decode steps`. Compare that to the prefill figure from question 1.

</details>

<details markdown="1"><summary>Check</summary>

`320 KB × 128 ≈ 40 MB` added by decode. Total cache is `640 MB + 40 MB = 680 MB`, so decode is only about 6% of the total; prefill claimed the other 94% in one step.

</details>

3. ▢ Using Llama-2-70B's fp8 cache figure of 160 KB per token, compute the total cache footprint for a batch of 64 sequences at a 4096-token context.

<details markdown="1"><summary>Hint</summary>

`total cache bytes = bytes per token × context length × batch size`, same formula as the warm-up.

</details>

<details markdown="1"><summary>Check</summary>

`160 KB × 4096 × 64 = 41,943,040 KB ≈ 40 GB`.

</details>

4. ▢ The fp16 version of that same batch (question 3, but at 320 KB per token) would cost how much cache, and what does the comparison show about stacking a precision change on top of a head-sharing change?

<details markdown="1"><summary>Check</summary>

`320 KB × 4096 × 64 ≈ 80 GB`, exactly double. The fp8 cache halves the footprint on top of whatever GQA already bought back from full MHA: the two levers are independent and multiply together rather than substituting for each other.

</details>

## Real-world reps

- [ ] Find your serving stack's flag for KV cache data type (vLLM: `--kv-cache-dtype`) and read what precisions it supports and what it warns about accuracy.
- [ ] For a request shape you actually expect (prompt length, expected output length), compute how much of its final cache prefill claims versus decode, using a model's real per-token figure.
- [ ] Tomorrow: read one paragraph of the vLLM docs on chunked prefill and note in one sentence why breaking prefill into pieces changes the memory-claim schedule this lesson described.

## Going further

- [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Article: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
