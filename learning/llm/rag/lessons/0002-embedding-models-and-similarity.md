---
title: 2. Embedding Models and Similarity
description: What a bi-encoder embedding model does, and why the similarity metric has to match how it was trained
type: lesson
---

# Lesson 2. Embedding Models and Similarity

**Mission link:** Chunking decided what gets embedded; this lesson decides how it gets turned into something searchable at all, and a mismatch here quietly degrades every later stage without looking like an obvious bug.
**Primary source:** [Paper: "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks", Reimers and Gurevych, 2019](https://arxiv.org/abs/1908.10084)
**Prerequisites:** [Lesson 1](0001-chunking.md), [Chunk](../GLOSSARY.md)

## Warm-up

1. ▢ What is the core trade-off chunk size makes?

<details markdown="1"><summary>Check</summary>

Chunks too large blur multiple topics into one averaged vector, hurting precision. Chunks too small lose the surrounding context that makes a chunk interpretable or complete, so a question spanning more than one small piece may not be answerable from any single chunk.

</details>

2. ▢ Why do consecutive chunks commonly overlap?

<details markdown="1"><summary>Check</summary>

So a fact or sentence that straddles a chunk boundary isn't fragmented and unrecoverable from either chunk alone.

</details>

## Know this

### A bi-encoder embeds each piece of text on its own

An embedding model of the kind this workspace uses is a **bi-encoder**: it maps a piece of text to a fixed-size dense vector, independently of any other text, such that texts with similar meaning land close together in that vector space. Crucially, a query and a passage are each embedded on their own, not jointly as a pair. This is what makes large-scale retrieval fast at all: every chunk in a corpus gets embedded once, ahead of time, and stored; at search time, only the query needs embedding, and it's compared against the already-computed chunk vectors. Comparing two independently-produced vectors is cheap; running a model over every query-passage pair, which is what a cross-encoder does (lesson 8), is not, and doesn't scale to searching a large corpus at query time.

### Three similarity metrics, and why they aren't interchangeable

Given two vectors, three common ways to measure how similar they are: **cosine similarity** (the angle between them, ignoring magnitude), **dot product** (cosine similarity without normalizing by magnitude), and **Euclidean distance** (straight-line distance between the two points). When both vectors are normalized to unit length, cosine similarity and dot product produce the same ranking, since the magnitude term that distinguishes them is fixed at 1 for both. When vectors aren't normalized, dot product implicitly rewards larger-magnitude vectors, which can introduce a bias unrelated to actual semantic relevance if magnitude varies systematically across the corpus (for instance, with passage length).

The metric to use isn't a free choice: an embedding model is trained with a specific similarity function in its loss (Sentence-BERT-style models are typically trained so cosine similarity, or an equivalent normalized dot product, reflects semantic closeness). Using a different metric than the one the model was optimized for doesn't just work slightly worse; it can rank in ways the model was never actually tuned to produce, since the training signal never shaped the space for that metric.

### Choosing a model means matching training objective to task, not just picking the top benchmark score

Embedding models differ in what they were trained to do well. Some are tuned for **symmetric search** (comparing two pieces of text that are similar in kind and length, like two sentences being checked for paraphrase). Retrieval is usually **asymmetric search** instead: a short query compared against long passages, which is a different training setup. A model that scores well on a general benchmark (such as MTEB, the Massive Text Embedding Benchmark) may still underperform a domain- or task-matched model on a specific corpus, especially a specialized one like legal or medical text a general web-trained model saw little of. The right question isn't just "which model scores highest overall," but "which model was trained on something close enough to this corpus and this query shape."

## Practice

1. ▢ Why does a bi-encoder embed a query and a passage separately rather than jointly, and what does that buy for retrieval over a large corpus?

<details markdown="1"><summary>Check</summary>

Embedding separately means every passage in the corpus can be embedded once, ahead of time, and stored. At query time, only the query needs embedding, and comparing it against precomputed passage vectors is cheap. Embedding jointly (a cross-encoder) would require running the model on every query-passage pair at search time, which doesn't scale to a large corpus.

</details>

2. ▢ Two embedding vectors are both normalized to unit length. Why do cosine similarity and dot product give the same ranking for them?

<details markdown="1"><summary>Check</summary>

Dot product is cosine similarity scaled by the two vectors' magnitudes. When both magnitudes are fixed at 1 (unit length), that scaling factor is the same for every pair being compared, so the ranking it produces is identical to cosine similarity's.

</details>

3. ▢ A team switches to a new embedding model but keeps using raw dot product for similarity, without checking whether the new model's vectors are normalized. Retrieval quality drops, and longer passages seem to get retrieved more often regardless of actual relevance. What's the likely cause?

<details markdown="1"><summary>Hint</summary>

Think about what dot product rewards when vector magnitudes aren't fixed.

</details>

<details markdown="1"><summary>Check</summary>

If the new model's vectors aren't normalized to unit length, dot product implicitly favors vectors with larger magnitude. If magnitude correlates with passage length (which it often does, since longer passages can accumulate larger embedding norms), this produces exactly the length bias observed, independent of whether the longer passages are actually more relevant.

</details>

4. ▢ A team is choosing an embedding model for a corpus of legal contracts, and one candidate model has the highest score on a general benchmark like MTEB. What else should they check before choosing it, and why?

<details markdown="1"><summary>Check</summary>

Whether the model was trained on something resembling this corpus's domain and this task's query shape (short query against long passage, asymmetric search), not just its overall benchmark score. A model that tops a general benchmark can still underperform a domain- or task-matched model on a specialized corpus like legal text, which a general web-trained model may have seen little of.

</details>

5. ▢ Which claim is true of choosing a similarity metric for an embedding model?

   - a) Any of cosine similarity, dot product, or Euclidean distance works equally well regardless of how the model was trained
   - b) The metric should match what the model's training objective actually optimized for, since a mismatch can degrade ranking quality
   - c) Dot product is always strictly better than cosine similarity, regardless of vector normalization
   - d) Euclidean distance and cosine similarity always produce identical rankings, normalized or not

<details markdown="1"><summary>Check</summary>

**b)** The model was optimized for a specific similarity function; using a different one isn't a neutral choice. (a) is false: this lesson's dot-product example shows a mismatch causing a real, measurable failure. (c) is false: dot product's advantage over cosine similarity only holds under specific normalization assumptions, and can otherwise introduce a magnitude bias. (d) is false: they coincide only under normalization; otherwise they can rank differently.

</details>

## Real-world reps

- [ ] Look up the embedding model you use (or plan to use) and find its documentation's stated similarity metric, and check whether your retrieval code actually uses that same metric.
- [ ] Check whether your embedding vectors are normalized to unit length, and if the metric in use assumes that.
- [ ] Tomorrow: look at an embedding model's card or benchmark entry and note whether it states what kind of search (symmetric or asymmetric) it was trained for.

## Going further

- [Paper: "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks", Reimers and Gurevych, 2019](https://arxiv.org/abs/1908.10084)
- [Article: "Chunking Strategies for LLM Applications", Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
