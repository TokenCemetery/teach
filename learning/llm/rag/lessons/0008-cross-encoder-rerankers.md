---
title: 8. Cross-Encoder Rerankers
description: What a cross-encoder scores that a bi-encoder can't, and why reranking is a second stage rather than a replacement for retrieval
type: lesson
---

# Lesson 8. Cross-Encoder Rerankers

**Mission link:** Retrieval so far (stages 1 to 4) has all used bi-encoder-style comparison, cheap and scalable but blind to fine-grained query-passage interaction; stage 5 adds a second pass that trades scale for accuracy on a much smaller set of candidates.
**Primary source:** [Paper: "Passage Re-ranking with BERT", Nogueira and Cho, 2019](https://arxiv.org/abs/1901.04085)
**Prerequisites:** [Lesson 7](0007-reciprocal-rank-fusion.md), [Chunk](../GLOSSARY.md)

## Warm-up

1. ▢ What problem does reciprocal rank fusion solve, and how does it solve it?

<details markdown="1"><summary>Check</summary>

BM25 and cosine similarity scores live on incomparable scales, so directly averaging them is fragile. RRF solves this by combining rankings using only each document's rank position, not its raw score, which is a common currency across any ranking method.

</details>

2. ▢ Why does a bi-encoder embed a query and a passage independently rather than jointly?

<details markdown="1"><summary>Check</summary>

So every passage can be embedded once, ahead of time, and stored; comparing precomputed vectors at search time is cheap, where running a model over every query-passage pair is not.

</details>

## Know this

### A cross-encoder sees the query and the passage together

Lesson 2's bi-encoder embeds a query and a passage in complete isolation from each other; the two vectors never interact until a cheap distance calculation compares them afterward. A **cross-encoder** does the opposite: it takes the query and a single candidate passage together, as one combined input, and runs them jointly through a model that can attend across both texts at once, producing a single relevance score for that specific pair. Because the model sees both texts simultaneously, it can pick up on fine-grained interactions, this particular word in the query matching this particular clause in the passage, that a bi-encoder's independently-computed embeddings have no way to capture, since neither embedding was ever computed with any knowledge of the other text.

### What that accuracy costs

A cross-encoder's joint processing is also exactly what makes it too expensive to search a whole corpus with directly: scoring one candidate requires one full model forward pass, so scoring 1,000 candidates means 1,000 forward passes, computed fresh for every query, with nothing precomputable ahead of time the way a bi-encoder's passage embeddings are. A corpus of a million chunks would need a million forward passes per query, which doesn't come close to scaling the way an embedding index does.

### Retrieve cheap, rerank precisely

The standard pattern uses each approach where it's affordable: bi-encoder retrieval, plus hybrid search (stages 3 and 4), cheaply narrows a whole corpus down to a modest candidate set, commonly somewhere around the top 50 to 100 results. A cross-encoder reranker then runs only over that much smaller set, scoring each query-candidate pair individually and reordering them with the accuracy a bi-encoder alone couldn't provide, surfacing the truly best handful, often the top 5 to 10, to hand downstream. This two-stage design gets the bi-encoder's scale and the cross-encoder's accuracy together, by applying the expensive step only where the corpus has already been narrowed enough for it to be affordable.

## Practice

1. ▢ Why can a cross-encoder capture subtler relevance signals than a bi-encoder, even when both are built on similar underlying transformer architectures?

<details markdown="1"><summary>Check</summary>

A cross-encoder processes the query and the candidate passage together, in one joint forward pass, so the model can attend across both texts and pick up on specific interactions between them. A bi-encoder embeds each one in isolation; by the time their embeddings are compared, neither one was computed with any knowledge of the other's specific content.

</details>

2. ▢ Why can't a cross-encoder be used to search a corpus of a million chunks directly, the way a bi-encoder embedding index can?

<details markdown="1"><summary>Check</summary>

A cross-encoder needs one full model forward pass per query-candidate pair, computed fresh for every query, since nothing about the joint query-passage input can be precomputed ahead of time. Scoring a million candidates would mean a million forward passes per query, which doesn't scale the way comparing a query embedding against a precomputed index does.

</details>

3. ▢ Describe the two-stage retrieve-then-rerank pattern, and explain why it exists rather than using either stage alone.

<details markdown="1"><summary>Check</summary>

Bi-encoder retrieval (plus hybrid search) cheaply narrows a whole corpus down to a modest candidate set, then a cross-encoder reranks only that smaller set with higher accuracy. It exists because a cross-encoder alone can't scale to a full corpus, and a bi-encoder alone misses the fine-grained query-passage interactions a cross-encoder can capture; combining them gets both the scale and the accuracy, each applied where it's affordable.

</details>

4. ▢ A team proposes reranking their entire corpus with a cross-encoder for every query, skipping bi-encoder retrieval entirely, to "get the best possible results." What's wrong with this plan?

<details markdown="1"><summary>Hint</summary>

Think about how many forward passes this would require per query.

</details>

<details markdown="1"><summary>Check</summary>

It requires one full model forward pass per document in the entire corpus, for every single query, which is the exact scaling problem a cross-encoder has and a bi-encoder index exists to avoid. At any real corpus size, this would be far too slow to serve as a live query, defeating the reason an embedding index and hybrid search exist in the first place.

</details>

5. ▢ Which claim is true of the relationship between bi-encoder retrieval and cross-encoder reranking?

   - a) They solve the same problem, so using both together is redundant
   - b) Bi-encoder retrieval cheaply narrows a large corpus to a candidate set, and a cross-encoder reranks only that smaller set with higher accuracy
   - c) A cross-encoder scales to searching a full corpus just as well as a bi-encoder index does
   - d) Reranking replaces the need for chunking, embeddings, or hybrid search entirely

<details markdown="1"><summary>Check</summary>

**b)** That's exactly the two-stage pattern this lesson describes. (a) is false: they trade off scale against accuracy differently, which is why combining them is useful rather than redundant. (c) is false: a cross-encoder needs one forward pass per candidate, which doesn't scale to a full corpus the way an embedding index does. (d) is false: reranking operates on the candidate set those earlier stages already produced; it doesn't replace them.

</details>

## Real-world reps

- [ ] Find a hosted or open-source cross-encoder reranker (such as Cohere's) and read what input it expects (a query plus a list of candidate texts) and what it returns.
- [ ] For a query and a small set of candidate passages from your corpus, predict which candidate a cross-encoder would rank highest, then check with an actual reranker call if you have access to one.
- [ ] Tomorrow: note how many candidates your current retrieval stage returns before any reranking, and whether that number is a deliberate choice or an unexamined default.

## Going further

- [Paper: "Passage Re-ranking with BERT", Nogueira and Cho, 2019](https://arxiv.org/abs/1901.04085)
- [Docs: "Reranking", Cohere](https://docs.cohere.com/docs/reranking)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
