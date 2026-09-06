---
title: 4. Static vs Continuous Batching
description: Why batching requests together helps throughput, and why continuous batching beats the static kind
type: lesson
---

# Lesson 4. Static vs Continuous Batching

**Mission link:** Batching is the lever that turns a server's KV cache capacity, the thing lessons 1 to 3 taught how to compute, into actual served throughput; how well a server batches decides how much of that capacity goes to useful work.
**Primary source:** [Article: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
**Prerequisites:** [Lesson 3](0003-growth-prefill-decode-precision.md), [KV cache](../GLOSSARY.md)

## Warm-up

1. ▢ Why is decode memory-bandwidth bound rather than compute bound?

<details markdown="1"><summary>Check</summary>

Each decode step reads the entire KV cache back to attend over it, to compute just one new token. The amount of new compute per step is small relative to the memory traffic needed to read the cache and the weights.

</details>

2. ▢ Lesson 3 distinguished prefill from decode. Which of the two processes an entire prompt in a single forward pass?

<details markdown="1"><summary>Check</summary>

Prefill. Decode instead generates one output token, and grows the cache by one token's worth, per step.

</details>

## Know this

### Why batching decode steps together helps at all

A decode step's memory traffic, reading the model's weights and every resident sequence's KV cache, barely changes whether it computes one sequence's next token or several sequences' next tokens at once. Batching multiple sequences' decode steps together spreads that same memory traffic across more useful compute, which is exactly the fix a memory-bandwidth-bound step needs: more work done per byte read.

### Static batching wastes that gain on uneven finish times

The obvious way to batch is to group a fixed set of requests, run decode steps until every one of them has finished, then start the next group. This is **static batching**, and it has one serious flaw: the group can't finish until its longest-running sequence does. Every sequence that finishes early still occupies a batch slot, contributing nothing, until the whole group is done.

Take four requests batched together, needing 10, 20, 30, and 100 output tokens respectively. The batch runs for 100 steps, because that's what the longest sequence needs. Across those 100 steps, the batch consumes `4 × 100 = 400` slot-steps of GPU work, but only `10 + 20 + 30 + 100 = 160` of those slot-steps did anything useful. The other 240 were spent on sequences that had already finished, sitting idle until the batch boundary. That's 60% waste, and it gets worse as the spread between requests' lengths grows, which is the normal case: real requests vary wildly in how much they generate.

### Continuous batching removes the batch boundary

**Continuous batching** (also called iteration-level scheduling) schedules at the level of a single decode step instead of a fixed group. The moment a sequence finishes, its slot is freed and a new, waiting request is admitted into the batch on the very next step, rather than waiting for every other sequence in its old group to finish too. The batch composition changes continuously; its size, not any one request's lifetime, is what stays roughly constant.

In the four-request example, the sequence needing only 10 tokens frees its slot at step 10. A static scheduler leaves that slot idle for 90 more steps. A continuous scheduler admits a new request into it immediately, so the GPU keeps doing useful work in that slot instead of carrying dead weight until an arbitrary boundary. That is the mechanism behind the throughput gains this lesson's primary source reports: not a faster per-step computation, but far less of each step wasted on sequences that had nothing left to do.

## Practice

1. ▢ A static batch holds two requests needing 15 and 60 output tokens. How many total slot-steps does the batch consume, how many are useful, and what fraction is wasted?

<details markdown="1"><summary>Hint</summary>

Total slot-steps is `batch size × steps until the longest sequence finishes`. Useful slot-steps is the sum of each request's actual length.

</details>

<details markdown="1"><summary>Check</summary>

Total: `2 × 60 = 120` slot-steps. Useful: `15 + 60 = 75`. Wasted: `120 − 75 = 45`, which is `45 / 120 = 37.5%`.

</details>

2. ▢ In a continuous-batching scheduler, what happens at the exact step a sequence in the batch finishes generating?

<details markdown="1"><summary>Check</summary>

Its slot is freed immediately, and a new waiting request is admitted into that slot on the next step, rather than the slot sitting idle until every other sequence in some fixed group also finishes.

</details>

3. ▢ Which claim is true of continuous batching compared to static batching?

   - a) It reduces the per-step compute cost of attention itself
   - b) It removes the KV cache requirement for finished sequences before evicting them
   - c) It keeps the batch full by admitting new requests as slots free up, instead of waiting for a fixed group to fully finish
   - d) It only applies to CPU serving stacks like llama.cpp

<details markdown="1"><summary>Check</summary>

**c)** It keeps the batch full continuously. (a) is false: the per-step arithmetic is unchanged; the gain is fewer wasted slot-steps. (b) is false and backwards: a finished sequence's cache is freed as part of evicting it, in either scheduling style. (d) is false: continuous batching is a GPU-serving scheduling technique, most associated with vLLM and similar engines.

</details>

4. ▢ A static batch of 8 requests all need exactly 50 output tokens each. Would continuous batching improve throughput over static batching for this particular batch, and why or why not?

<details markdown="1"><summary>Check</summary>

Barely, if at all. Continuous batching's gain comes from filling slots freed by requests that finish early while others keep running. When every request in the group needs exactly the same number of tokens, there are no early finishers and no idle slots to fill, so static batching wastes nothing here already.

</details>

## Real-world reps

- [ ] Find the flag or config option your serving stack of choice uses to enable continuous batching (vLLM enables it by default; check what its docs call the underlying mechanism).
- [ ] Look at a real traffic sample or log of requests you have access to (or a public dataset of LLM request lengths) and estimate the spread between shortest and longest output length. Estimate the static-batching waste fraction that spread would cause.
- [ ] Tomorrow: read one paragraph on how a continuous-batching scheduler decides which waiting request to admit next, and note whether it is simple arrival order or something else.

## Going further

- [Article: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
