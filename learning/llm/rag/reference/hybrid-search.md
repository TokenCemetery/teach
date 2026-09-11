---
title: Hybrid Search
description: BM25's term-statistics scoring, why it still matters next to vector search, and reciprocal rank fusion as a scale-free way to combine them
type: reference
---

# Hybrid Search

Combining lexical and vector rankings. Built for lookup when standing up or tuning a hybrid blend.

## BM25 scores term overlap, not meaning

A purely lexical ranking function, no embedding, no notion of meaning. Three ingredients:

| Ingredient | What it does |
|---|---|
| Inverse document frequency (IDF) | Weights a query term by rarity across the corpus; a common word like "the" contributes almost nothing |
| Term frequency, saturating | More occurrences of a term raise the score, but with diminishing returns, so repetition alone (keyword stuffing) can't dominate |
| Length normalization | Discounts the raw term-frequency advantage a document gets simply from being longer |

## BM25 and vector search have opposite blind spots

| Query shape | BM25 | Vector search |
|---|---|---|
| Exact identifier ("error code E502") | Matches: the literal string appears | May miss: the embedding model was trained for semantic similarity, not exact-identifier matching |
| Synonymous phrasing, no shared words ("broken pipe" / "leaking conduit") | Scores near zero: no term overlap at all | Matches: the two phrases mean the same thing |

Each approach catches what the other misses, which is the whole basis for combining them.

## Reciprocal rank fusion (RRF): use rank, not score

BM25's score is unbounded and corpus-dependent; cosine similarity is bounded to [-1, 1]. Averaging the two directly means inventing a fragile, corpus-specific normalization. **RRF** sidesteps the scale problem by using only each document's rank position within each ranking:

```text
RRF(d) = sum over rankings r of 1 / (k + rank_r(d))
```

`k` dampens the influence of the very top ranks (a common default is `k = 60`; a smaller `k` makes rank differences near the top matter more, a larger `k` dampens them). Rank position is a common currency across any ranking method, so no normalization is needed between BM25 and vector search.

**Worked example**, `k = 1`, BM25 ranks A 1st / B 4th / C 2nd, vector search ranks A 4th / B 1st / C 2nd:

```text
RRF(A) = 1/(1+1) + 1/(1+4) = 0.500 + 0.200 = 0.700
RRF(B) = 1/(1+4) + 1/(1+1) = 0.200 + 0.500 = 0.700
RRF(C) = 1/(1+2) + 1/(1+2) = 0.333 + 0.333 = 0.667
```

A and B tie for first, each excelling under one method and doing poorly under the other; C, merely mediocre under both, loses to both. RRF rewards a document any one method strongly believes in, not only one both methods mildly agree on.

## Tuning the blend

RRF extends with a per-ranking weight, `sum of w_r / (k + rank_r(d))`, letting vector search count for more or less than BM25. The right weight and `k` are not guessed: measure retrieval quality (recall@k, MRR) against a labeled or synthetic query set representative of the corpus's real traffic, at several candidate weightings, and ship whichever blend actually retrieves the right documents more often for this corpus, not a default 50/50 split.

## Related

- [Lesson 6](../lessons/0006-bm25-and-lexical-search.md), [Lesson 7](../lessons/0007-reciprocal-rank-fusion.md)
- [Vector Search and Indexing](vector-search-and-indexing.md): the vector ranking half of the fusion
