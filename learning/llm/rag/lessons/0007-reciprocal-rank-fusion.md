---
title: 7. Reciprocal Rank Fusion
description: How to combine a lexical ranking and a vector ranking without comparing incomparable scores, and how to tune the blend against a measured metric
type: lesson
---

# Lesson 7. Reciprocal Rank Fusion

**Mission link:** This is stage 4's capstone: BM25 and vector search (lessons 4 to 6) each produce a ranking, and this lesson is how those two rankings become one hybrid result, tuned against a measured number rather than a guessed blend.
**Primary source:** [Docs: "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
**Prerequisites:** [Lesson 6](0006-bm25-and-lexical-search.md), [Chunk](../GLOSSARY.md)

## Warm-up

1. ▢ Give an example of a query where BM25 would succeed and vector search might fail, and one where the reverse is true.

<details markdown="1"><summary>Check</summary>

An exact identifier like "error code E502" favors BM25, since vector search's embedding model wasn't trained to match specific codes precisely. A synonymous phrasing with no shared words, like "broken pipe" against "leaking conduit," favors vector search, since BM25 scores zero for documents sharing no terms with the query.

</details>

2. ▢ Why does using the wrong distance operator against a pgvector index cause the query to fall back to a sequential scan?

<details markdown="1"><summary>Check</summary>

An index is built for one specific distance function (one operator class); a query using a different operator doesn't match what the index was built for, so the index can't be used and the query scans the table directly instead.

</details>

## Know this

### The problem: two rankings on incomparable scales

BM25 produces an unbounded, corpus-dependent score; cosine similarity produces a score bounded between -1 and 1. Averaging them directly, even after some normalization, means deciding how to make two fundamentally different scales comparable, and that decision is fragile: it depends on the corpus, the query, and which normalization scheme was chosen, with no principled way to know it's fair.

### RRF: use rank position, not the score itself

**Reciprocal rank fusion (RRF)** sidesteps the scale problem entirely by ignoring the underlying scores and using only each document's **rank position** within each ranking. For a document *d* appearing at rank `rank_r(d)` in ranking *r*, its RRF score sums a reciprocal-rank term across every ranking it appears in:

```text
RRF(d) = sum over rankings r of 1 / (k + rank_r(d))
```

`k` is a constant that dampens the influence of the very top ranks; a common default from the original paper is `k = 60`. Because only rank position matters, not score magnitude, RRF combines a BM25 ranking and a vector-search ranking with no need to normalize either one: rank position is already a common currency, self-normalizing across any ranking method whatsoever.

### A worked example

Using a simplified `k = 1` to keep the arithmetic clean (production systems more commonly default to `k = 60`, which dampens differences among the top ranks more heavily than `k = 1` does): for a query, BM25 ranks document A 1st, document B 4th, document C 2nd; vector search ranks A 4th, B 1st, C 2nd.

```text
RRF(A) = 1/(1+1) + 1/(1+4) = 0.500 + 0.200 = 0.700
RRF(B) = 1/(1+4) + 1/(1+1) = 0.200 + 0.500 = 0.700
RRF(C) = 1/(1+2) + 1/(1+2) = 0.333 + 0.333 = 0.667
```

A and B tie for first, each excelling under one method and doing poorly under the other; C, merely mediocre under both, loses to both. RRF rewards a document that any one method strongly believes in, not only a document both methods mildly agree on.

### Tuning the blend against a measured metric

RRF can be extended with a per-ranking weight, `sum of w_r / (k + rank_r(d))`, letting vector search count for more or less than BM25 in the final fusion. The right weight, and the right `k`, are not something to guess at: they're something to measure, the same way lesson 3 measured embedding quality at candidate dimensionalities instead of assuming one. Using stage 6's retrieval metrics (recall@k, MRR) against a labeled or synthetic query set representative of the corpus's actual traffic, different weightings can be compared directly, and the blend that actually retrieves the right documents more often for this corpus, not a default 50/50 split, is the one worth shipping.

## Practice

1. ▢ For a query, BM25 ranks document X 2nd and document Y 1st; vector search ranks X 1st and Y 3rd. Using `k = 1`, compute each document's RRF score and say which ranks higher.

<details markdown="1"><summary>Hint</summary>

`RRF(d) = 1/(k + rank_in_bm25) + 1/(k + rank_in_vector)`.

</details>

<details markdown="1"><summary>Check</summary>

`RRF(X) = 1/(1+2) + 1/(1+1) = 0.333 + 0.500 = 0.833`. `RRF(Y) = 1/(1+1) + 1/(1+3) = 0.500 + 0.250 = 0.750`. X ranks higher, since it's a strong (1st place) result under vector search and only mildly good under BM25, edging out Y, which is strong under BM25 but weaker under vector search.

</details>

2. ▢ Why does RRF use each document's rank position rather than its raw BM25 score or cosine similarity score directly?

<details markdown="1"><summary>Check</summary>

BM25 scores and cosine similarity live on incomparable scales (one unbounded and corpus-dependent, the other bounded between -1 and 1), and there's no principled, corpus-independent way to normalize them against each other. Rank position is already a common currency across any ranking method, so using it sidesteps the normalization problem entirely.

</details>

3. ▢ What does a small `k` (like 1) do to the RRF formula compared to a large `k` (like 60), in terms of how much a document's exact rank position matters?

<details markdown="1"><summary>Check</summary>

A small `k` makes the reciprocal-rank term much more sensitive to small differences in rank near the top of a list (the gap between rank 1 and rank 2 is proportionally larger), while a large `k` dampens that sensitivity, making the difference between, say, rank 1 and rank 5 comparatively smaller. Larger `k` values produce a gentler, less rank-position-sensitive fusion.

</details>

4. ▢ How should a team decide whether to weight vector search more heavily than BM25 in their hybrid blend, rather than defaulting to an even split?

<details markdown="1"><summary>Check</summary>

Measure retrieval quality (recall@k or MRR, stage 6's metrics) against a labeled or synthetic query set representative of the corpus's real query pattern, at several candidate weightings, and choose the one that actually retrieves the right documents most often for this corpus, rather than assuming an even split or any other default is correct without checking.

</details>

5. ▢ Which claim is true of reciprocal rank fusion?

   - a) It requires normalizing BM25 and cosine similarity scores onto the same scale before combining them
   - b) It combines rankings using only rank position, which sidesteps the need to compare incomparable score scales
   - c) A document that ranks 1st in one ranking and last in another will always outrank a document that ranks moderately in both
   - d) The constant `k` has no effect on the fused ranking, only on the numeric score's magnitude

<details markdown="1"><summary>Check</summary>

**b)** Using rank position rather than raw scores is exactly what avoids the normalization problem. (a) is false: that's the raw-score-fusion approach RRF specifically avoids. (c) is false: the worked example showed a consistently moderate document can still lose to two documents that each excel under one method, but the outcome depends on the actual rank values, not a universal rule that extreme beats moderate. (d) is false: `k` changes how much rank position differences matter, which can change the fused ranking's order, not just its scale.

</details>

## Real-world reps

- [ ] For a query in your corpus, get its BM25 rank and vector-search rank for a handful of candidate documents, and compute their RRF scores by hand using `k = 60`.
- [ ] If you have a labeled or synthetic query set, compare recall@k for a BM25-only ranking, a vector-only ranking, and an RRF-fused ranking on the same queries.
- [ ] Tomorrow: try two different values of the weight on vector search in a weighted RRF formula, and see whether either measurably improves recall@k over an even split.

## Going further

- [Docs: "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
- [Paper: "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson and Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
