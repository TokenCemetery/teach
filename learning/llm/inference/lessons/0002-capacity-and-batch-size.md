---
title: 2. Capacity and Batch Size
description: How head sharing (GQA/MQA) and batch size change the cache's real footprint
type: lesson
---

# Lesson 2. Capacity and Batch Size

**Mission link:** A latency budget is defended in terms of how many concurrent requests a server can hold, and that number falls straight out of the cache math this lesson extends.
**Primary source:** [Article: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
**Prerequisites:** [Lesson 1](0001-the-kv-cache.md), [KV cache](../GLOSSARY.md)

## Warm-up

1. ▢ In one sentence, what does the KV cache let a server skip on every generated token after the first?

<details markdown="1"><summary>Check</summary>

Recomputing the key and value vectors for every prior token in the sequence, at every layer.

</details>

2. ▢ What was wrong with a naive, contiguous, max-length-sized cache allocation, and what did PagedAttention change about it?

<details markdown="1"><summary>Check</summary>

It reserved memory for the maximum length a sequence might reach, wasting it as internal and external fragmentation. PagedAttention allocates the cache in fixed-size, non-contiguous blocks addressed through a per-sequence table instead.

</details>

## Know this

### Most models don't cache one key and value per head

Lesson 1's formula, `2 × num_layers × d_model × 2 bytes` per token, assumes every attention head keeps its own key and value vectors. That is **multi-head attention (MHA)**. Most models serving today use **grouped-query attention (GQA)** or its extreme case, **multi-query attention (MQA)**: many query heads share a much smaller number of key/value heads. The cache only ever holds one K/V pair per *KV head*, not per query head, so the formula becomes:

```text
bytes per token = 2 (K and V) × num_layers × num_kv_heads × head_dim × bytes_per_value
```

where `head_dim = d_model / num_heads`, and `num_kv_heads` is the number that matters now, not the total head count. When `num_kv_heads = num_heads` this reduces exactly to lesson 1's formula (MHA is GQA's special case). When `num_kv_heads` is much smaller, the cache shrinks by that same ratio, for free, with no change to context length or batch size.

Llama-2-70B is a concrete case: 80 layers, 64 query heads, but only 8 KV heads, `head_dim` = 128. In fp16:

```text
per token = 2 × 80 × 8 × 128 × 2 bytes = 327,680 bytes ≈ 320 KB
```

Had it used full MHA (64 KV heads instead of 8), the same layers and `head_dim` give `2 × 80 × 64 × 128 × 2 = 2,621,440 bytes ≈ 2.5 MB` per token, eight times more, exactly the ratio of `num_heads` to `num_kv_heads`. GQA is a serving-cost decision as much as a modeling one.

### Growing the per-token cost into a batch's total footprint

A server rarely holds one sequence. The total cache footprint at any moment is the per-token cost, multiplied by how long each sequence has grown, multiplied by how many sequences are resident together:

```text
total cache bytes = bytes per token × context length × batch size
```

For Llama-2-70B at a 4096-token context, one sequence costs `320 KB × 4096 ≈ 1.25 GB`. Thirty-two concurrent sequences at that same length cost `1.25 GB × 32 = 40 GB`, before the model's own weights take any space at all.

### Turning that into a capacity budget

This is the number a serving decision actually needs: given a memory pool, how many concurrent sequences fit? Subtract the weights and framework overhead from the total memory available, then divide what is left by the per-sequence cache cost at the context length you plan to support:

```text
max concurrent sequences = (total memory − weights − overhead) / (bytes per token × context length)
```

Take a 320 GB pool (four 80 GB GPUs, tensor-parallel) serving Llama-2-70B, with weights and framework overhead measured at 160 GB. That leaves 160 GB for cache. At the 4096-token, 1.25 GB-per-sequence figure above: `160 GB / 1.25 GB ≈ 128` concurrent sequences. That ceiling, not the model's raw throughput, is usually what a batching scheduler is negotiating against, which is where lesson 4 picks up.

## Practice

1. ▢ A model uses GQA with `num_kv_heads` a quarter of `num_heads`. Compared to the same model under full MHA, how much smaller is its per-token KV cache?

<details markdown="1"><summary>Check</summary>

A quarter the size. The cache holds one K/V pair per KV head, not per query head, so the per-token cost scales with `num_kv_heads` alone; everything else in the formula is unchanged.

</details>

2. ▢ A model has 48 layers, 40 query heads, 8 KV heads, `head_dim` = 128, served in fp16. Compute its per-token KV cache size.

<details markdown="1"><summary>Hint</summary>

Use `2 × num_layers × num_kv_heads × head_dim × bytes_per_value`. The query head count does not appear in the formula at all.

</details>

<details markdown="1"><summary>Check</summary>

`2 × 48 × 8 × 128 × 2 = 196,608 bytes ≈ 192 KB` per token.

</details>

3. ▢ Using the 192 KB-per-token model from question 2, compute the total cache footprint for a batch of 16 sequences at a 2048-token context.

<details markdown="1"><summary>Hint</summary>

`total cache bytes = bytes per token × context length × batch size`.

</details>

<details markdown="1"><summary>Check</summary>

Per sequence: `192 KB × 2048 ≈ 384 MB`. For 16 sequences: `384 MB × 16 = 6,144 MB ≈ 6 GB`.

</details>

4. ▢ A server has 96 GB of memory. Weights and framework overhead take 40 GB. Each sequence's cache costs 384 MB at the context length this server supports. What is the maximum number of concurrent sequences the cache budget allows?

<details markdown="1"><summary>Check</summary>

`(96 GB − 40 GB) / 384 MB = 56 GB / 384 MB ≈ 149` sequences. In practice a server reserves a further safety margin below this ceiling, but the arithmetic is this division.

</details>

## Real-world reps

- [ ] Look up the `num_key_value_heads` (or equivalent) field in a model you plan to serve's config file, alongside `num_attention_heads`. Compute the ratio between them and what it buys back in cache size.
- [ ] Using that model's per-token cache size, compute how many concurrent sequences a memory pool you have access to (or a published GPU's memory) could hold at a context length you care about.
- [ ] Tomorrow: find the flag your serving stack of choice (vLLM or llama.cpp) uses to cap total KV cache memory, and read what happens when a request would exceed it.

## Going further

- [Article: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
- [Paper: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
