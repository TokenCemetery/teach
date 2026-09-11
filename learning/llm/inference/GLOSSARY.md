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

**Pipeline bubble**:
The idle time devices in a pipeline-parallel setup spend waiting, at the start (while the pipeline fills) and end (while it drains) of processing a batch, since not every device has work at those moments. Splitting a batch into more micro-batches shrinks this idle fraction but never eliminates it.
_Avoid_: assuming micro-batching removes the bubble entirely (it only shrinks the idle fraction relative to total work; a startup and drain delay remain regardless of micro-batch count)

**Pipeline parallelism**:
Partitioning a model's sequence of layers into consecutive groups placed on separate devices, so data flows through the devices in the same order the layers would run on one device. Communication happens only at the boundary between one device's group and the next, which is what lets it tolerate a slower inter-device link than tensor parallelism needs, and span multiple nodes.
_Avoid_: splitting the computation inside a single layer (that's tensor parallelism; pipeline parallelism never divides what happens inside one layer, only which layers go where)

**Prefix caching**:
Reusing a shared prefix's already-computed KV cache across otherwise unrelated requests (a common system prompt, a repeatedly-queried document, earlier turns of a conversation), the same block-sharing mechanism PagedAttention uses within one request's parallel samples, extended across requests. Speeds up prefill only; decode time is unaffected.
_Avoid_: assuming it also speeds up decode (it only skips redundant prefill computation for a matched prefix; generating new tokens afterward costs exactly the same either way)

**Speculative decoding**:
Drafting several candidate next tokens cheaply, then verifying all of them in one parallel forward pass through the target model, accepting correct guesses and resampling incorrect ones so the final output distribution exactly matches running the target model alone. A pure latency lever with no quality trade-off.
_Avoid_: an approximation technique (it changes only how many expensive forward passes generation takes, never what gets generated)

**Tensor parallelism**:
Splitting the large matrix multiplications inside a single layer (a transformer's attention and MLP blocks) across devices by columns or rows, with each device computing its own slice in parallel and a communication step recombining the true result at specific points inside every layer. Needs a fast interconnect (like NVLink) since that recombine happens on the critical path, every layer, every forward pass.
_Avoid_: splitting whole layers across devices (that's pipeline parallelism; tensor parallelism splits the computation inside one layer, never assigns whole layers to different devices)
