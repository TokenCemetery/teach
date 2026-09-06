---
title: 1. The KV Cache
description: Why generation gets expensive, and what caching buys back
type: lesson
---

# Lesson 1. The KV Cache

**Mission link:** Every latency and throughput number this workspace defends traces back to what the KV cache costs in memory and how well a server manages that cost.
**Primary source:** [Docs: "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
**Prerequisites:** none

## Know this

### Why decoding needs a cache at all

A transformer generates one token at a time. To produce token *N*, self-attention needs the key and value vectors for every token from 1 to *N*, at every layer. Without a cache, each new token forces the model to recompute the keys and values for the *entire* prefix again, even though those vectors never change once a token is generated. That is quadratic work spent recomputing things already computed.

The **KV cache** stores each token's key and value vectors, per layer, the moment they're first computed, so generating token *N+1* only computes one new set of K/V vectors and reuses the rest. This is what makes autoregressive generation practical at all: it trades recomputation for memory.

### What that memory actually costs

The cache is not free, and its size is what governs how many requests a server can hold in memory at once. Per token, per layer, it holds one key and one value vector, each of size equal to the model's hidden dimension (`d_model`, the dimension of the model's residual stream). In half precision (2 bytes per value):

```text
bytes per token = 2 (K and V) × num_layers × d_model × 2 bytes
```

Take Llama-2-7B as a concrete case: 32 layers, `d_model` = 4096.

```text
2 × 32 × 4096 × 2 bytes = 524,288 bytes ≈ 512 KB per token
```

At a 4096-token context, that's `512 KB × 4096 ≈ 2 GB`, for a *single* sequence. Hold 16 such sequences concurrently and the cache alone needs ~32 GB, more than the 14 GB the model's own weights take up in fp16. This is the arithmetic behind why "just add more KV cache" is the wrong instinct, and why serving stacks obsess over cache memory instead of treating it as an afterthought (see Kipply's [Transformer Inference Arithmetic](https://kipp.ly/transformer-inference-arithmetic/) for the full derivation, including how this scales with attention-head sharing schemes like GQA/MQA).

### Where naive caching wastes memory

A naive implementation reserves one contiguous memory block per sequence, sized for the maximum sequence length it might ever reach. Two failure modes follow:

- **Internal fragmentation**: a sequence that ends up short still holds memory reserved for the maximum length it never used.
- **External fragmentation**: sequences of different actual lengths leave gaps between their reserved blocks that no other sequence's cache can fit into.

The PagedAttention paper measured naive systems keeping as little as 20 to 40% of allocated KV cache memory actually holding useful data. Its fix borrows straight from operating-system virtual memory: split the cache into fixed-size blocks, store them non-contiguously, and keep a per-sequence block table that maps logical positions to physical blocks. That's the idea vLLM is built around, and it's why the framework matters as much as the arithmetic: the same cache, allocated well, serves far more concurrent requests.

## Practice

1. ▢ In one sentence, what does the KV cache let a server skip on every generated token after the first?

<details markdown="1"><summary>Check</summary>

Recomputing the key and value vectors for every prior token in the sequence, at every layer. Only the new token's K/V need to be computed; the rest are read from the cache.

</details>

2. ▢ A model has 40 layers and `d_model` = 5120, served in fp16. Estimate the KV cache size for one sequence at a 2048-token context.

<details markdown="1"><summary>Hint</summary>

Use `2 × num_layers × d_model × 2 bytes`, then multiply by the number of tokens.

</details>

<details markdown="1"><summary>Check</summary>

Per token: `2 × 40 × 5120 × 2 = 819,200 bytes ≈ 800 KB`.
At 2048 tokens: `800 KB × 2048 ≈ 1.6 GB` for one sequence.

</details>

3. ▢ Two sequences hold naive, contiguous, max-length-sized KV cache blocks. One finishes far short of the maximum length it reserved. What happens to the memory it reserved but didn't use, and what does that cost the server?

<details markdown="1"><summary>Check</summary>

It sits reserved and unusable by any other sequence until that sequence's cache is freed: internal fragmentation. The cost is fewer concurrent sequences the server can actually serve, since memory that looks "allocated" is doing no useful work.

</details>

4. ▢ Which claim is true of PagedAttention's fix?

   - a) It shrinks the KV cache's total size for a given model and context length
   - b) It removes the KV cache and recomputes attention on demand instead
   - c) It reduces wasted memory by storing the cache in fixed-size, non-contiguous blocks
   - d) It only helps CPU serving stacks like llama.cpp

<details markdown="1"><summary>Check</summary>

**c)** It reduces wasted memory by storing the cache in fixed-size, non-contiguous blocks, addressed through a per-sequence block table, the same idea as OS virtual memory paging.

(a) is false: the per-token cost is unchanged; only the waste around it shrinks. (b) is false: the cache is still there, just allocated better. (d) is false: PagedAttention is a GPU-serving technique (vLLM); this workspace covers llama.cpp separately.

</details>

## Real-world reps

- [ ] Pick a model you plan to serve. Compute its KV-cache-per-token size using the formula above, from its published `num_layers` and hidden size.
- [ ] Compute that same model's full weight size in the precision you'd serve it in, and compare it to the KV cache size at its maximum context length.
- [ ] Tomorrow: find one serving stack's docs (vLLM or llama.cpp) and locate the flag that controls how much memory it reserves for the KV cache.

## Going further

- [Article: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
- [Paper: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
