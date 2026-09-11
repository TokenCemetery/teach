---
title: Glossary
description: "Canonical terms for inference"
type: glossary
---

# Inference Glossary

Canonical terms for serving a trained model: what a server holds in memory, and the levers it has over latency and throughput.

## Terms

**Attention sink**:
The disproportionately large attention score a sequence's first few tokens receive regardless of their actual content, which is why dropping them from a sliding-window cache causes a quality collapse rather than a graceful loss of old context. Keeping just those initial tokens' KV entries permanently cached, alongside the usual sliding window, recovers most of full attention's performance (the StreamingLLM technique).
_Avoid_: assuming any dropped old token causes the same damage (only the initial "sink" tokens carry this disproportionate weight; losing other old tokens outside the window degrades gracefully instead of collapsing)

**Cold start (serving)**:
The gap between an autoscaler deciding to add a replica and that replica actually being able to serve a request, dominated by the time it takes to load a large model's checkpoint into memory, which can take tens of seconds and far exceeds the time to generate a single token.
_Avoid_: treating it as a request-queueing problem (a scheduler or router has no effect on it; it's set entirely by checkpoint size and the storage path it has to move across)

**Constrained (guided) decoding**:
Masking out every token that would violate a required structure (valid JSON, a grammar) before sampling happens, so the output's structure is guaranteed by construction rather than merely encouraged. Kept cheap per token by reframing the grammar as a finite-state machine and precomputing, once, an index of which tokens are valid from each state.
_Avoid_: checking the output for validity after generation completes (doesn't guarantee anything, since the model was always free to sample an invalid token; masking before sampling is what makes the guarantee structural)

**Cost per million tokens**:
A GPU's hourly rental cost divided by its measured throughput (tokens/sec, converted to tokens/hour), scaled to a million tokens. Derived from the same measured throughput lesson 6's batch-size trade-off produces, not quoted from a vendor's advertised per-token price measured on a different workload's batch size.
_Avoid_: a fixed, vendor-quoted per-token price (throughput, and therefore cost per token, depends on the batch size and workload it was measured under, and doesn't transfer across configurations)

**Draft model**:
A small, cheap model (or a non-model mechanism like n-gram matching, or extra heads on the target model itself) that proposes several candidate next tokens for the target model to verify in one parallel pass, rather than generating them itself one at a time.
_Avoid_: a smaller, lower-quality alternative to the target model (a draft model's output is never used directly; it's only ever verified, and possibly corrected, by the target model)

**Error budget**:
1 minus a service level objective: the amount of allowed misses against that target before a service is considered out of compliance with it. A single missed request isn't a problem by itself; what matters is whether the rate of misses is consuming the budget faster than the SLO's measurement window allows.
_Avoid_: treating any single missed measurement as a problem (the budget exists precisely because some rate of misses is expected and tolerated; only the consumption rate against the window matters)

**KV cache**:
The stored key and value vectors for every already-generated token, at every layer, kept so a server never has to recompute them for later tokens. Its size grows linearly with sequence length and is often the memory bottleneck in serving, not the model's own weights.
_Avoid_: attention cache, key-value store

**KV-cache aware routing**:
A fleet-level request-routing policy that sends a new request to whichever server already holds the highest cache-hit rate for it, rather than routing purely on load (round-robin, least-connections). Extends prefix caching's per-server benefit to a multi-server fleet by making the routing decision itself aware of where a matching cache already lives.
_Avoid_: ordinary load balancing (round-robin or least-connections ignore cache locality entirely, and can route a cache-friendly request to a server that has to redo the prefill from scratch)

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

**RoPE scaling**:
Extending how long a context a model can handle past its trained length by rescaling how rotary position embeddings encode distance between tokens (YaRN's approach: scaling high-frequency dimensions less and low-frequency dimensions more), rather than retraining from scratch. Changes nothing about how many tokens' keys and values get cached; a longer context handled this way still costs the KV cache's ordinary linear growth in full.
_Avoid_: assuming it reduces or caps KV cache memory (it only extends the maximum usable context length; the cache for that longer context still grows exactly as it would without any scaling applied)

**SLI (service level indicator)**:
A quantitative, user-relevant ratio picked out of a raw exported metric, for example the fraction of requests with TTFT under a stated threshold, framed from the user's experience rather than the server's internal state.
_Avoid_: a raw metric histogram itself (a histogram is measured data; an SLI is the specific user-relevant ratio chosen out of it to hold a target against)

**Sliding-window attention**:
Restricting each token to attend to at most a fixed number, `W`, of preceding tokens, rather than the entire sequence so far, paired with a rolling buffer cache that only ever holds `W` tokens' worth of keys and values. Caps a sequence's KV cache at a constant size regardless of how long the sequence actually grows, unlike RoPE scaling's unchanged linear growth.
_Avoid_: assuming it extends how far a model can usefully see the same way RoPE scaling does (it caps the cache and bounds direct attention to the last `W` tokens; anything beyond that is reached only indirectly, through stacked layers, and on its own suffers a quality collapse without attention sinks)

**SLO (service level objective)**:
A stated target for an SLI, for example "99% of requests have TTFT under 300ms over a rolling 28 days." What's left over, 1 minus the SLO, is the error budget.
_Avoid_: a one-time benchmark result (lesson 16's single measured p99 is a snapshot; an SLO is a standing target held against continuously exported metrics)

**Speculative decoding**:
Drafting several candidate next tokens cheaply, then verifying all of them in one parallel forward pass through the target model, accepting correct guesses and resampling incorrect ones so the final output distribution exactly matches running the target model alone. A pure latency lever with no quality trade-off.
_Avoid_: an approximation technique (it changes only how many expensive forward passes generation takes, never what gets generated)

**Tensor parallelism**:
Splitting the large matrix multiplications inside a single layer (a transformer's attention and MLP blocks) across devices by columns or rows, with each device computing its own slice in parallel and a communication step recombining the true result at specific points inside every layer. Needs a fast interconnect (like NVLink) since that recombine happens on the critical path, every layer, every forward pass.
_Avoid_: splitting whole layers across devices (that's pipeline parallelism; tensor parallelism splits the computation inside one layer, never assigns whole layers to different devices)
