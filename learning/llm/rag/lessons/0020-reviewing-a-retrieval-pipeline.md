---
title: 20. Reviewing a Retrieval Pipeline
description: Review someone else's retrieval pipeline design and name specifically what it will get wrong before it ships, and say when RAG itself (not a pipeline stage) is the wrong answer to the stated problem
type: lesson
---

# Lesson 20. Reviewing a Retrieval Pipeline

**Mission link:** A senior skill is reviewing someone else's work, naming what a choice costs rather than saying it feels wrong, and knowing when the entire approach is the wrong one for the problem (not just which stage is broken).
**Primary source:** [Paper: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
**Prerequisites:** [Lesson 1](0001-chunking.md), [Lesson 2](0002-embedding-models-and-similarity.md), [Lesson 4](0004-ann-indexes.md), [Lesson 6](0006-bm25-and-lexical-search.md), [Lesson 9](0009-when-reranking-earns-its-cost.md), [Lesson 11](0011-diagnosing-the-pipeline.md), [Lesson 15](0015-metadata-filtering-and-access-control.md), [Lesson 17](0017-freshness.md)

## Warm-up

1. ▢ What does a retrieval metric measure, and why do hybrid weights and reranking need one?

<details markdown="1"><summary>Check</summary>

A retrieval metric like Recall@k or MRR measures whether the right thing was retrieved, before the generation step ever starts. Hybrid weights and reranking tuning both depend on knowing whether a change actually improved what was retrieved, so they need a measurement to decide against rather than by feel.

</details>

2. ▢ Why does post-filtering fail for access control specifically, in a way it doesn't for other metadata filters?

<details markdown="1"><summary>Check</summary>

Post-filtering runs the ANN search first across the entire index, then discards results afterward. For ordinary metadata filters, this is just a recall regression: the filter drops some results. For access control, unauthorized content briefly exists in the pipeline before being discarded, which is a security failure, not just a quality one. Pre-filtering restricts the candidate set before the search runs, so disallowed content never enters the pipeline at all.

</details>

3. ▢ Name one way a corpus can go stale, and one way freshness is handled differently for that case versus another.

<details markdown="1"><summary>Check</summary>

A corpus goes stale by adding documents, deleting them, or swapping the embedding model. Adding and deleting can use incremental indexing, HNSW handles both relatively well. Swapping the model requires a full reindex from scratch: the old vectors share no comparable distances with new ones, so they have to be completely rebuilt.

</details>

## Know this

### The review checklist: what to actually look for in a design

When someone proposes a retrieval pipeline or shows you one that's already built, walk through these questions in order. Each corresponds to a stage in this arc. For each one, look for: (1) was the choice made deliberately for this corpus and use case, (2) was it measured against a retrieval metric, or did it get picked by default or by feel?

**Stage 1: Chunking strategy.** Did the design choose a chunking strategy because it matches the corpus's actual structure (fixed-size for prose, recursive for nested markdown, semantic for papers with topic shifts, or document-structure-aware for PDFs with layout that matters)? Or was a default chunk size (512, 1024 tokens) just copied in? A corpus of medical PDFs needs different chunking than a repo full of API documentation.

**Stage 2 & 3: Embedding model and similarity metric.** Was the embedding model and metric (cosine, L2, dot product) chosen for this corpus, tested against similar corpora or at least against examples from this one? Or was it picked by default from what the vector database's documentation recommended? An embedding trained on news might rank finance papers poorly.

**Stage 4, 5, 6: Hybrid search, reranking, and retrieval evaluation.** Does the design have an actual retrieval metric it was tuned against (Recall@k, MRR, nDCG)? Or were hybrid weights and reranking added by feel, with no measurement of whether they actually improved the right thing being retrieved? A reranking stage that costs latency needs proof it earned that cost on the actual use case.

**Stage 9: Permission-aware filtering.** If the corpus has access control, does the design use pre-filtering to restrict the candidate set before the ANN search, keeping unauthorized content out of the pipeline entirely? Or does it retrieve from the whole index and filter afterward, risking both recall regression and a moment when unauthorized content exists in the pipeline?

**Stage 10 & 11: Ingestion and freshness.** Did the design account for how the source documents are actually extracted and parsed upstream of chunking? Does it have a plan for keeping the index current as documents are added, deleted, or modified, or is it assuming static data? Incremental updates suit HNSW well, but swapping an embedding model always requires a full reindex.

**Stage 6 again: Distinguishing retrieval failure from generation failure.** When something goes wrong, does the design have a way to tell whether the model got bad context or used good context badly? A design that defaults to blaming the retrieval stage on any wrong answer is missing a crucial diagnostic.

### The disputed question: does long-context make retrieval obsolete?

This is a live disagreement. One account says long-context models now eliminate the need for retrieval: why build a retrieval pipeline when models can now hold the whole corpus in the prompt? Why pay for retrieval infrastructure when you can just send 100K tokens on every request?

The other account says retrieval still wins for most real corpora and use cases, despite long-context advances. The research paper "Lost in the Middle" shows models use information placed in the middle of a long context far worse than information at the beginning or end, even within the context window. Resending a whole corpus on every request concentrates all the tokens it doesn't use in the middle of the attention, exactly where models use information poorly. Retrieval instead sends only the relevant parts, keeping them near the top of the context window where models attend to them well.

But that's the decision framework, not the decision itself. To settle whether retrieval is the right answer for a specific problem, ask three questions:

**1. What is the corpus size and update frequency?**

A corpus that is small, static, and fits in a single prompt might legitimately work better sent whole: a company's entire handbook (50K tokens, changes quarterly) might be cheaper and simpler to include on every request than to maintain a retrieval index. A corpus that is large (millions of documents), changes constantly (daily ingestion), or is access-controlled (different users see different subsets) works the other way: the cost of resending it on every request is prohibitive, or the access control is impossible to enforce post-retrieval (stage 9's lesson).

**2. What does the query pattern actually need?**

A query that needs synthesis across the whole corpus (what's the consensus on X across all our papers) might benefit from seeing more context. A query that needs precise facts (what's our refund policy for annual subscriptions) works better with retrieval that finds the exact policy document and places it at the top where the model attends to it well. Retrieval lets you send less context at higher fidelity.

**3. What does the cost calculation actually come to?**

The "Lost in the Middle" paper shows the tradeoff: when information sits in the middle of a 100K-token prompt, models lose it. To work around that, you either have to carefully order the context (which retrieval does by placing the most relevant chunks near the top) or send less of it. Retrieval that sends 2K tokens of the most relevant chunks is cheaper and better than 100K tokens where half is in the dead zone. This assumes your retrieval actually finds the relevant chunks; if the retrieval pipeline is broken, sending everything is at least a fallback. But when retrieval works, it wins on cost, latency, and quality.

## Practice

1. ▢ A team built a pipeline that chunks all documents with a fixed 1024-token size. You review the design and see no justification for this choice. What question should you ask to understand whether it was deliberate or defaulted?

<details markdown="1"><summary>Check</summary>

What is the corpus? Are these customer support transcripts, academic papers, product documentation, or something else? A 1024-token chunk works for some document types and fails for others. If they chose this size because it was easy to implement or because the vector database's example code used it, that's a red flag. If they tested different chunk sizes against a held-out retrieval metric on actual corpus samples and 1024 won, that's a deliberate choice you can trace.

</details>

2. ▢ The design uses OpenAI's embedding model without testing it on the actual corpus. What might go wrong?

<details markdown="1"><summary>Check</summary>

The embedding model was trained on a broad distribution of text from the internet. If the corpus is highly specialized (legal documents, financial filings, medical literature) or in a language with less pretraining data, the model might rank semantic similarity poorly. The right test: embed a sample of documents from this corpus, manually identify which pairs are actually similar, and check whether OpenAI's distance ranking agrees. If not, consider domain-specific embeddings or models trained on similar content.

</details>

3. ▢ A design uses hybrid search (BM25 + vector) but the team is unsure how to weight them. They ask, "should we do 50-50, or 70-30 vector?" What information are they missing?

<details markdown="1"><summary>Check</summary>

They are missing a retrieval metric. Weights should be tuned against actual measurement on a held-out query set, measuring which blend produces the best Recall@k or MRR on the task. Guessing between 50-50 and 70-30 is a coin flip, and the wrong blend can hurt more than either approach alone. The real question is: for your corpus and queries, which blend actually retrieves the right thing? Measure it.

</details>

4. ▢ The corpus contains medical research papers that get updated constantly (new papers added daily, older ones sometimes retracted or corrected). A proposal suggests putting all documents into a long-context model's prompt on every request. What are two reasons this might not work?

<details markdown="1"><summary>Hint</summary>

Consider what the corpus is like (size, change rate) and what the model does with information placed in the middle of a long context.

</details>

<details markdown="1"><summary>Check</summary>

Two reasons: (1) The corpus is large and constantly changing, so resending all documents on every request is expensive, and updating which documents are in the prompt is a maintenance burden. Retrieval lets you send only what's relevant and updates automatically when the index is refreshed. (2) Models use information placed in the middle of a long context poorly ("Lost in the Middle"). Sending 500 papers with only a few relevant to the query buries the relevant ones in the middle of the attention, where models attend poorly. Retrieval that sends the top 5 relevant papers, ranked by relevance at the top of the context, is both cheaper and more accurate.

</details>

5. ▢ A team considering RAG asks: "Our corpus is 10MB of markdown files, updated once a year. Why not just include it all in the prompt?" Which claim below correctly addresses this question?

    - a) Long-context models make RAG completely obsolete; this team should never use retrieval for any reason
    - b) The corpus is small, static, and fits in a prompt; for this specific case, including it all might actually be simpler and work fine
    - c) RAG is always better than long-context, no matter the corpus size or change frequency
    - d) The "Lost in the Middle" paper proves that nothing should ever be put in a prompt

<details markdown="1"><summary>Check</summary>

**b)** That's the calibrated position on this question. The corpus size (10MB, likely under the context window), change frequency (annual), and access-control needs (none mentioned) all point toward long-context working fine, possibly simpler. RAG has real infrastructure costs. A small, static corpus doesn't justify those costs. (a) is wrong: models can legitimately be used without retrieval when the corpus is tiny and static. (c) is wrong: the decision depends on the corpus characteristics and query pattern, not an absolute rule. (d) is wrong: the paper shows models use middle-context poorly, not that anything in a prompt is unusable.

</details>

## Real-world reps

- [ ] Find a retrieval pipeline you built or reviewed. Walk the five questions from the checklist against it. For each stage, write one sentence: was this choice measured against a retrieval metric, or picked by default? Then ask: what would you change if you had to improve it?
- [ ] Pick one corpus (your own, a public one you know, or a synthetic one). Work out the three-question framework: corpus size and update frequency, query pattern, actual cost of resending it whole versus retrieval. Write down the answer: would retrieval or long-context be the better fit, and why?
- [ ] Tomorrow: read the "Lost in the Middle" paper's results section and note the specific performance gap between information at the beginning, middle, and end of a 4K-token context. Then estimate: if your query pattern needed synthesis across 100 documents, how many would fit in the "high-quality" zones at the beginning and end?

## Going further

- [Paper: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
- [Lesson 24: Long Context at Serve Time](../../inference/lessons/0024-long-context-at-serve-time.md): what long-context techniques actually do to serving cost, rather than retrieval cost
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
