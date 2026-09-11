---
title: Glossary
description: "Canonical terms for inference"
type: glossary
---

# Inference Glossary

Canonical terms for serving a trained model: what a server holds in memory, and the levers it has over latency and throughput.

## Terms

**Constrained (guided) decoding**:
Masking out every token that would violate a required structure (valid JSON, a grammar) before sampling happens, so the output's structure is guaranteed by construction rather than merely encouraged. Kept cheap per token by reframing the grammar as a finite-state machine and precomputing, once, an index of which tokens are valid from each state.
_Avoid_: checking the output for validity after generation completes (doesn't guarantee anything, since the model was always free to sample an invalid token; masking before sampling is what makes the guarantee structural)

**Draft model**:
A small, cheap model (or a non-model mechanism like n-gram matching, or extra heads on the target model itself) that proposes several candidate next tokens for the target model to verify in one parallel pass, rather than generating them itself one at a time.
_Avoid_: a smaller, lower-quality alternative to the target model (a draft model's output is never used directly; it's only ever verified, and possibly corrected, by the target model)

**KV cache**:
The stored key and value vectors for every already-generated token, at every layer, kept so a server never has to recompute them for later tokens. Its size grows linearly with sequence length and is often the memory bottleneck in serving, not the model's own weights.
_Avoid_: attention cache, key-value store

**Memory-bandwidth-bound**:
A computation whose dominant cost is moving data (like a model's weights) from memory to the compute unit, rather than the arithmetic performed once that data arrives. Ordinary autoregressive decoding is memory-bandwidth-bound, which is exactly what lets speculative decoding verify several candidate tokens in one pass for roughly the cost of generating just one.
_Avoid_: compute-bound (the opposite regime, where arithmetic dominates; conflating the two misses why extra verification work is nearly free during decoding specifically)

**Prefix caching**:
Reusing a shared prefix's already-computed KV cache across otherwise unrelated requests (a common system prompt, a repeatedly-queried document, earlier turns of a conversation), the same block-sharing mechanism PagedAttention uses within one request's parallel samples, extended across requests. Speeds up prefill only; decode time is unaffected.
_Avoid_: assuming it also speeds up decode (it only skips redundant prefill computation for a matched prefix; generating new tokens afterward costs exactly the same either way)

**Speculative decoding**:
Drafting several candidate next tokens cheaply, then verifying all of them in one parallel forward pass through the target model, accepting correct guesses and resampling incorrect ones so the final output distribution exactly matches running the target model alone. A pure latency lever with no quality trade-off.
_Avoid_: an approximation technique (it changes only how many expensive forward passes generation takes, never what gets generated)
