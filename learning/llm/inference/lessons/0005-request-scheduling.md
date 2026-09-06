---
title: 5. Request Scheduling
description: How a continuous-batching scheduler picks the next request, and why a large prefill can stall everyone else
type: lesson
---

# Lesson 5. Request Scheduling

**Mission link:** Continuous batching, from lesson 4, only helps if the scheduler admitting requests into it doesn't itself create a new latency problem; this lesson is where that trade-off lives.
**Primary source:** [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Prerequisites:** [Lesson 4](0004-static-vs-continuous-batching.md), [KV cache](../GLOSSARY.md)

## Warm-up

1. ▢ In continuous batching, what happens the instant a sequence in the batch finishes generating?

<details markdown="1"><summary>Check</summary>

Its slot is freed immediately, and a new waiting request is admitted into it on the next step, instead of the slot sitting idle until a fixed group of requests all finish together.

</details>

2. ▢ Why is prefill compute-bound while decode is memory-bandwidth bound?

<details markdown="1"><summary>Check</summary>

Prefill processes an entire prompt in one large, parallel forward pass, so there is enough work per byte read to keep the GPU's compute busy. Decode computes only one new token per step, so each step's memory traffic (reading the cache and the weights) dominates the small amount of new compute.

</details>

## Know this

### Which waiting request goes next

A scheduler holding a queue of waiting requests needs a policy for which one to admit into a slot that just freed up. The simple default, and what vLLM uses absent other configuration, is **first-come, first-served (FCFS)**: requests are admitted in arrival order. It is not the only possible policy (a scheduler could prioritize by expected length, or by a stated latency budget), but FCFS is the right default to know first: it is simple, it is fair in the sense that no request waits behind one that arrived later, and every more elaborate policy is a variation on the same admit-into-a-freed-slot mechanism lesson 4 described.

### A batch step is atomic, and that creates a new problem

Every sequence sharing a batch step advances together: the whole step's latency is set by whatever the most expensive piece of work in it is. Admitting a new request means its prefill work has to happen somewhere, and the straightforward place is the very next batch step, alongside whatever decode steps the already-running sequences need.

That is fine when the new request's prompt is short. It is not fine when it is long: a 6,000-token prefill folded into one step now dominates that step's latency, and every other sequence in the batch, sequences that only needed a small, fast decode step, waits for it to finish before any of them gets their next token. One large admission stalls everyone else's progress. This is a **head-of-line blocking** problem: the queue is fine, but what's running now is not.

### Chunked prefill bounds the damage

**Chunked prefill** splits a large prompt's prefill into smaller pieces and interleaves each piece with the batch's ongoing decode steps, rather than running the whole prefill in one step. Each batch step now admits only a bounded amount of new prefill work, whatever fits the step's latency budget, instead of however much a newly admitted request's prompt happens to contain. The trade is that the new request's own prefill now takes several steps to finish instead of one, but no other sequence in the batch is stalled waiting for it.

## Practice

1. ▢ A continuous batch is running steady decode-only steps of about 20 ms each. A 6,000-token prompt is admitted and its full prefill is folded into the very next step, without chunking. What happens to that step's latency, and who feels the effect?

<details markdown="1"><summary>Check</summary>

That step now has to complete the prefill compute for all 6,000 prompt tokens, in addition to the decode work for every other sequence in the batch, because the whole batch advances together in one step. The step's latency balloons well past 20 ms, and every other sequence in the batch, including ones that only needed a fast decode step, waits for that one step to finish before getting their next token.

</details>

2. ▢ How does chunked prefill avoid the stall described in question 1?

<details markdown="1"><summary>Hint</summary>

Think about what changes per step, not what changes about the total amount of prefill work needed.

</details>

<details markdown="1"><summary>Check</summary>

Instead of running the new request's entire prompt in one step, the scheduler splits its prefill into smaller pieces and interleaves each piece with the batch's regular decode steps, admitting only a bounded amount of new prefill work per step. Any single step's latency stays bounded; the new request's own prefill just takes more steps in total to finish.

</details>

3. ▢ Which claim is true of chunked prefill?

   - a) It removes prefill entirely, treating every token as a decode step
   - b) It bounds a step's added latency by splitting a large prefill into pieces
   - c) It is a technique specific to CPU serving stacks like llama.cpp
   - d) It reduces how much KV cache a long prompt needs once fully processed

<details markdown="1"><summary>Check</summary>

**b)** It bounds a step's added latency by splitting a large prefill into pieces interleaved with decode. (a) is false: the prompt still needs full prefill processing, just spread across more steps. (c) is false: it is a GPU continuous-batching scheduling technique. (d) is false: the final cache size for a fully processed prompt is unchanged; chunking only changes how the work to get there is spread over time.

</details>

4. ▢ Would FCFS admission alone (with no chunking) have prevented the stall in question 1?

<details markdown="1"><summary>Check</summary>

No. FCFS only decides which waiting request gets admitted next; it says nothing about how much of that request's prefill work lands in a single step once admitted. The stall comes from folding an entire large prefill into one atomic batch step, which chunking, not admission order, is what fixes.

</details>

## Real-world reps

- [ ] Find your serving stack's flag or config option for chunked prefill (vLLM: enabled by default in recent versions; check its docs for the chunk-size setting) and read what the default chunk size is.
- [ ] Estimate, for a workload you have request-length data for, roughly how often a prompt would be long enough to noticeably stall a batch step without chunking.
- [ ] Tomorrow: read one paragraph on how a scheduler decides between admitting a new request's prefill chunk versus continuing an in-flight one, when both compete for the same step's budget.

## Going further

- [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Article: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
