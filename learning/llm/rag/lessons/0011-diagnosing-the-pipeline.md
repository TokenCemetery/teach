---
title: 11. Diagnosing the Pipeline
description: A stage-by-stage procedure for finding which part of a retrieval pipeline is actually responsible for wrong retrieved context
type: lesson
---

# Lesson 11. Diagnosing the Pipeline

**Mission link:** This is stage 6's capstone and one of the mission's two success criteria: given wrong retrieved context, naming the at-fault stage rather than re-tuning knobs at random is what turns this workspace's earlier stages into a usable diagnostic toolkit.
**Primary source:** [Article: "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
**Prerequisites:** [Lesson 10](0010-recall-at-k-and-mrr.md), [Chunk](../GLOSSARY.md)

## Warm-up

1. ▢ What does MRR capture that recall@k can't?

<details markdown="1"><summary>Check</summary>

MRR uses the exact rank position of the first relevant result, rewarding rank 1 far more than a lower rank. Recall@k only checks whether a relevant result falls anywhere within the top k, treating every position in that range identically.

</details>

2. ▢ What two things does a team need to measure to decide whether reranking earns its cost for their workload?

<details markdown="1"><summary>Check</summary>

The quality gain reranking provides (recall@k or MRR with and without it, on the same query set) and the added latency it actually costs at the candidate-set size in use, both checked against the workload's real budget and quality bar.

</details>

## Know this

### A symptom has many possible causes; a diagnosis isolates one

"Wrong context retrieved" is a symptom, not a diagnosis. The fault could sit in chunking (lesson 1), the embedding model or similarity metric (lesson 2), the ANN index's recall setting (lessons 4 and 5), the hybrid search blend (lessons 6 and 7), or a missing or misconfigured reranking stage (lessons 8 and 9). Changing several of these at once and hoping something improves wastes effort and teaches nothing about which one was actually broken; the fix is to check each stage in an order that isolates the fault before touching a knob.

### Check chunking first: does the answer even exist in one place

Pull up the actual chunk (or chunks) that should have answered a known failing query. If the relevant information was split across a chunk boundary, with the answer's two halves sitting in separate, disconnected chunks, or was buried inside a large, topically mixed chunk that dilutes its embedding (lesson 1's core trade-off), no later pipeline stage can retrieve what chunking never gave a coherent representation of in the first place. This is a chunking-strategy problem, and it has to be fixed at the chunking stage, not by tuning anything downstream.

### Check the embedding, independent of the index

If chunking looks fine, the next check is whether the correct chunk's embedding is actually close to the query's embedding at all, using **exact** similarity (bypassing any ANN index) rather than the deployed search path. If the correct chunk sits far from the query even under exact comparison, the fault is the embedding model or the similarity metric (lesson 2), not the index: no amount of index tuning can retrieve a chunk whose embedding was never placed near the query's to begin with.

### Check the index, only once the embedding is confirmed close

If exact similarity places the correct chunk close to the query, but the deployed ANN index still fails to surface it, the fault is likely the index's recall setting (`ivfflat.probes` or `hnsw.ef_search`, lessons 4 and 5) tuned too aggressively toward speed. Raising the search-time parameter and re-testing isolates whether this was the cause.

### Check the hybrid blend and the reranking stage last

If vector search alone misses a chunk that BM25 would have found (or the reverse), and hybrid search still misses it, the hybrid weighting (lessons 6 and 7) may be under-weighting whichever method would have surfaced it. If the correct chunk is retrieved by hybrid search but ranked too low to reach the final top-k handed to generation, and no reranking stage is in place (or its candidate set or model isn't catching it), that points at stage 5 (lessons 8 and 9).

### Diagnose across a query set, not one anecdote

A single failing query can be misleading: its failure might be a one-off caused by an unusual phrasing rather than a systemic pipeline problem. Measuring recall@k and MRR (lesson 10) at each stage, initial retrieval alone, after hybrid fusion, after reranking, across a small set of known, representative failures reveals where the aggregate biggest drop happens, which stage is systematically losing information rather than which stage happened to fail on one query someone noticed.

## Practice

1. ▢ A query about "clause 4.2 termination rights" returns the wrong chunks. Investigation shows clause 4.2 was split across a chunk boundary with no overlap, leaving its termination-rights half orphaned at the start of the next chunk, surrounded by unrelated content. Which stage is at fault, and why can't a later stage fix it?

<details markdown="1"><summary>Check</summary>

Chunking. The relevant information was never given a coherent, retrievable representation in the first place: the orphaned half-clause's embedding reflects mostly the unrelated surrounding content, not the termination-rights text a query about it would match against. No embedding model, index tuning, hybrid weighting, or reranking stage can retrieve information that chunking never packaged into a chunk whose embedding actually represents it.

</details>

2. ▢ The correct chunk for a failing query is confirmed complete and coherent (no chunking problem), but under exact, non-ANN similarity search, its embedding sits far from the query's embedding. What's the likely fault, and why does this rule out ANN index tuning as the fix?

<details markdown="1"><summary>Check</summary>

The likely fault is the embedding model or the similarity metric (lesson 2): the chunk's embedding was never placed near the query's embedding to begin with. This rules out ANN index tuning because an ANN index only approximates exact search; if even exact search fails to place the correct chunk close to the query, a faster or more exhaustive search of that same embedding space can't fix a mismatch that exists at the embedding level itself.

</details>

3. ▢ Exact similarity search confirms the correct chunk's embedding is close to the query's, but the deployed ANN index doesn't return it in the top 20 results. What's the likely fault, and what would you check first?

<details markdown="1"><summary>Check</summary>

The likely fault is the ANN index's recall setting (`ivfflat.probes` or `hnsw.ef_search`) being tuned too aggressively toward speed. The first thing to check is raising that search-time parameter and re-testing whether the correct chunk now appears; if it does, the index's recall/latency trade-off, not the embedding or the model, was the cause.

</details>

4. ▢ Why is diagnosing across a small set of known-failing queries, measuring recall@k at each pipeline stage, more reliable than debugging a single anecdotal failure?

<details markdown="1"><summary>Check</summary>

A single failing query might fail for an unusual, one-off reason (an odd phrasing, an edge case) that doesn't reflect a systemic pipeline problem. Measuring recall@k across a representative set of known failures at each stage of the pipeline reveals where the aggregate biggest drop-off happens, pointing at which stage is systematically losing information rather than reacting to whichever single failure happened to get noticed.

</details>

5. ▢ Which claim is true of diagnosing a RAG pipeline's wrong-retrieval symptom?

   - a) Any pipeline stage can be tuned first, since they all affect the final result equally
   - b) Checking stages in order, chunking first, then the embedding independent of the index, then the index, then hybrid weighting and reranking, isolates which stage is actually at fault
   - c) A single failing query is always sufficient evidence to identify the at-fault stage
   - d) If the ANN index doesn't return the correct chunk, the embedding model must be at fault

<details markdown="1"><summary>Check</summary>

**b)** That ordered, isolating procedure is exactly what separates diagnosis from random re-tuning. (a) is false: an earlier stage's failure (like chunking) can make every later stage's tuning irrelevant, which is why order matters. (c) is false: a single query can fail for reasons that don't generalize; a representative query set is more reliable. (d) is false: exact similarity has to be checked first, since a failing ANN index with a genuinely close embedding points at index tuning, not the embedding model.

</details>

## Real-world reps

- [ ] For a retrieval pipeline you run or plan to run, pick one query it handles badly, and walk this lesson's stage-by-stage check (chunking, exact embedding similarity, index recall, hybrid weighting, reranking) until you find where it actually breaks.
- [ ] Build a small set of known-failing queries for your corpus and measure recall@k at more than one pipeline stage (initial retrieval versus after any reranking) to see where the biggest aggregate drop happens.
- [ ] Tomorrow: revisit this workspace's mission in `README.md` and confirm, in your own words, that you can now diagnose a wrong-retrieval symptom rather than re-tuning at random.

## Going further

- [Article: "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
- [Article: "Chunking Strategies for LLM Applications", Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
