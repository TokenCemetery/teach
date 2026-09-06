---
title: 9. When Reranking Earns Its Cost
description: A decision framework for whether a reranking stage is worth its added latency for a given workload
type: lesson
---

# Lesson 9. When Reranking Earns Its Cost

**Mission link:** This is stage 5's capstone: reranking (lesson 8) is not a step every pipeline should add by default, and deciding whether it earns its place means measuring what it actually costs and buys for this workload, not assuming either answer.
**Primary source:** [Docs: "Reranking", Cohere](https://docs.cohere.com/docs/reranking)
**Prerequisites:** [Lesson 8](0008-cross-encoder-rerankers.md), [Chunk](../GLOSSARY.md)

## Warm-up

1. ▢ Why can't a cross-encoder be used to search a full corpus directly, the way a bi-encoder embedding index can?

<details markdown="1"><summary>Check</summary>

A cross-encoder needs one full model forward pass per query-candidate pair, computed fresh for every query, with nothing precomputable ahead of time. Scoring a large corpus this way doesn't scale the way comparing a query embedding against a precomputed index does.

</details>

2. ▢ Describe the two-stage retrieve-then-rerank pattern.

<details markdown="1"><summary>Check</summary>

Bi-encoder retrieval, plus hybrid search, cheaply narrows a whole corpus to a modest candidate set. A cross-encoder then reranks only that smaller set, scoring each query-candidate pair individually to reorder them with higher accuracy than the initial retrieval alone could provide.

</details>

## Know this

### Reranking's cost is concrete, not abstract

Adding a reranking stage adds a measurable amount of latency: one forward pass per candidate in the reranked set, so reranking 100 candidates costs roughly 100 times the per-candidate cost of a single forward pass, whether that pass runs locally or through a hosted API. This is an additive cost stacked on top of whatever the initial retrieval stage already took, and it has to fit inside whatever end-to-end latency budget the system actually has. Nothing about reranking is free just because it improves accuracy; the accuracy gain has to be weighed against a real number of added milliseconds.

### The gain reranking buys also has to be measured

The question worth asking isn't "does reranking improve quality in general" (it usually does, since that's what lesson 8 established a cross-encoder is built to do), but "does it improve quality enough, for this corpus and this query pattern, to justify what it costs here." That means measuring retrieval quality (recall@k, MRR, or precision at the position that actually matters downstream, stage 6's tools) both without reranking and with it added, on the same query set. If hybrid search already reliably puts the best candidate near the top, reranking may move very little while still costing real latency. If hybrid search often buries the best candidate deep in the initial candidate list, reranking's reordering can matter enormously, especially when only the very top result or two actually reach the generation step.

### The right answer is workload-dependent

A real-time chat system with a tight end-to-end latency budget may not be able to afford reranking at all, regardless of how much it would improve quality, if the added latency alone would blow the budget. An offline research or document-QA workload with a much more generous latency tolerance can often afford reranking easily, since the accuracy gain matters more to that workload than shaving off a few hundred milliseconds does. Neither "always rerank" nor "never rerank" is the right default; the decision is measuring the actual quality gain, measuring the actual added latency, and checking both against what this specific workload's budget and quality bar actually require.

## Practice

1. ▢ What does adding a reranking stage concretely cost, and what does that cost scale with?

<details markdown="1"><summary>Check</summary>

It costs one model forward pass per candidate in the reranked set, so the total added latency scales with how many candidates get reranked; reranking 100 candidates costs roughly 100 times the per-candidate cost of a single forward pass, on top of whatever the initial retrieval stage already took.

</details>

2. ▢ A real-time chat system has a 200 ms total latency budget. Retrieval already takes about 100 ms, and reranking would add roughly 150 ms on top of that. What should the team conclude?

<details markdown="1"><summary>Check</summary>

Reranking, as measured, doesn't fit the budget: 100 ms of retrieval plus 150 ms of reranking is 250 ms, already over the 200 ms budget before generation even starts. Unless the candidate set reranked can be shrunk enough to bring that cost down, or the budget can be relaxed, reranking isn't affordable for this workload as currently measured.

</details>

3. ▢ An offline research assistant tolerates up to 5 seconds of latency. Measurement shows reranking moves the actually relevant document from an average rank of 12 up to rank 1 within the top 20 candidates, at a cost of 300 ms. What should the team conclude?

<details markdown="1"><summary>Check</summary>

Reranking is very likely worth adding here: a 300 ms cost is a small fraction of a 5-second budget, and the measured quality gain is large, moving the relevant document from buried at rank 12 to the top result, which matters a great deal if only the top few results reach generation.

</details>

4. ▢ How should a team decide whether reranking earns its cost for their specific workload, rather than assuming it always or never helps?

<details markdown="1"><summary>Check</summary>

Measure retrieval quality (recall@k, MRR, or precision at the position that matters downstream) both without and with reranking, on the same representative query set, and separately measure the actual added latency reranking costs at the candidate-set size in use. Compare the measured quality gain and the measured latency cost against this workload's actual latency budget and quality bar, rather than assuming reranking is either always worthwhile or never worth the cost.

</details>

5. ▢ Which claim is true of deciding whether to add a reranking stage?

   - a) Reranking should always be added, since a cross-encoder is more accurate than a bi-encoder by construction
   - b) Reranking should never be added, since it costs more latency than initial retrieval alone
   - c) The decision depends on measuring both the quality gain and the added latency against the specific workload's budget and quality needs
   - d) Reranking's cost is fixed and doesn't depend on how many candidates are reranked

<details markdown="1"><summary>Check</summary>

**c)** Both this lesson's scenarios showed the right answer depends on the actual measured numbers and the workload's own constraints, not a universal rule. (a) is false: being more accurate doesn't make a step free; it still has to fit the latency budget. (b) is false: the research-assistant scenario showed a workload where the cost was easily worth paying. (d) is false: cost scales directly with how many candidates are reranked.

</details>

## Real-world reps

- [ ] For a retrieval pipeline you run or plan to run, measure how much latency a reranking stage would add at your typical candidate-set size.
- [ ] If you can compare retrieval quality with and without reranking on the same query set, measure the difference in recall@k or MRR at the position that matters for your downstream use.
- [ ] Tomorrow: decide, in writing, whether reranking is worth adding for your specific workload, citing the measured quality gain and the measured latency cost against your actual budget.

## Going further

- [Docs: "Reranking", Cohere](https://docs.cohere.com/docs/reranking)
- [Paper: "Passage Re-ranking with BERT", Nogueira and Cho, 2019](https://arxiv.org/abs/1901.04085)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
