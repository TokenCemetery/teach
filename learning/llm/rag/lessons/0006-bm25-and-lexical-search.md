---
title: 6. BM25 and Lexical Search
description: What BM25 actually scores, and why exact-term matching still catches what semantic embeddings miss
type: lesson
---

# Lesson 6. BM25 and Lexical Search

**Mission link:** Stage 4 opens hybrid search: before combining a lexical ranking with vector search, this lesson establishes what lexical search is actually good at, and why a strong embedding model doesn't make it obsolete.
**Primary source:** [Paper: "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson and Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
**Prerequisites:** [Lesson 5](0005-pgvector-specifics.md), [Chunk](../GLOSSARY.md)

## Warm-up

1. ▢ Why does a bi-encoder embed a query and a passage separately rather than jointly?

<details markdown="1"><summary>Check</summary>

So every passage can be embedded once, ahead of time, and stored; only the query needs embedding at search time, letting it be compared cheaply against precomputed passage vectors.

</details>

2. ▢ Why does an index built with `vector_l2_ops` fail to speed up a query that orders by `<=>` (cosine distance)?

<details markdown="1"><summary>Check</summary>

An index is built for one specific distance function; the operator class and the query's operator have to match, or the index goes unused and the query falls back to a full sequential scan.

</details>

## Know this

### BM25 scores term overlap, not meaning

**BM25** is a lexical ranking function: it scores how relevant a document is to a query based purely on which query terms literally appear in the document, how often, and how informative each term is, with no embedding and no notion of meaning at all. Three ingredients combine into its score: **inverse document frequency (IDF)**, which weights a query term by how rare it is across the whole corpus (a common word like "the" contributes almost nothing, since it appears everywhere and distinguishes nothing; a rare, specific term contributes heavily, since its presence is informative); **term frequency**, how often a query term appears in this particular document, but **saturating** rather than scaling linearly, so a term appearing 10 times doesn't score 10 times higher than appearing once, which stops keyword-stuffing from dominating a score; and **length normalization**, which discounts a document's raw term-frequency advantage from simply being longer than average, since a longer document has more chances to contain any given term by sheer size alone, not necessarily because it's more relevant.

### Why lexical search still matters next to a good embedding model

Embedding models are trained to capture semantic similarity, and they do it well for synonymous phrasing: a query for "how to fix a broken pipe" can retrieve a passage about "resolving a leaking conduit" despite zero shared words, because the two mean similar things. But that same training makes embeddings comparatively weak at exact, specific term matching: a product code, an error identifier, a rare proper noun, an exact phrase the user is quoting verbatim. A query for "error code E502" needs a document that literally contains "E502"; an embedding model, trained on general semantic similarity rather than exact identifier matching, may retrieve documents that are topically about error handling without surfacing the one document that actually contains the specific code the user typed. BM25 has the opposite blind spot: exactly the reverse case, "broken pipe" against "leaking conduit," would score close to zero under BM25, since the two share no terms at all, despite meaning the same thing. Each approach catches what the other misses, which is exactly the case for combining them rather than picking one.

## Practice

1. ▢ A user searches for the exact error code "E502." Why might vector search alone under-retrieve the one document that actually contains that string, even though the corpus has several documents topically about error handling?

<details markdown="1"><summary>Check</summary>

The embedding model was trained to capture semantic similarity, not exact identifier matching, so "E502" may not be well represented as a distinctive point in the embedding space; documents that are topically similar about error handling in general can end up closer to the query's embedding than the one document that happens to contain the literal string "E502."

</details>

2. ▢ A query reads "how to fix a broken pipe," and the best matching document is phrased "resolving a leaking conduit," sharing no words with the query. Would BM25 score this pair highly? Why or why not?

<details markdown="1"><summary>Check</summary>

No, BM25 would score it near zero, since it only scores based on which query terms literally appear in the document, and this pair shares no terms at all. BM25 has no way to recognize that the two phrasings mean the same thing; that's exactly the gap vector search's semantic similarity is meant to fill.

</details>

3. ▢ Why does BM25 saturate term frequency (diminishing the score increase from repeated occurrences of a term) rather than scoring it linearly?

<details markdown="1"><summary>Hint</summary>

Think about what a document could do to game a linear term-frequency score.

</details>

<details markdown="1"><summary>Check</summary>

A linear term-frequency score would let a document dominate the ranking simply by repeating a query term many times (keyword stuffing), regardless of whether the document is actually more relevant. Saturating term frequency means each additional occurrence contributes less than the last, so relevance is still rewarded without letting raw repetition alone dominate the score.

</details>

4. ▢ Why does BM25 normalize for document length, and what would go wrong without that normalization?

<details markdown="1"><summary>Check</summary>

A longer document has more opportunities to contain any given query term simply by having more words, independent of whether it's actually more relevant to the query. Without length normalization, long documents would systematically outscore shorter, equally or more relevant ones purely because of their size, not their actual relevance.

</details>

5. ▢ Which claim is true of BM25 compared to vector search?

   - a) BM25 and vector search fail on the exact same kinds of queries, so combining them adds nothing
   - b) BM25 excels at exact term matching but misses synonymous phrasing with no shared words, while vector search does the reverse
   - c) BM25 requires an embedding model to compute term relevance
   - d) Vector search always outperforms BM25 for any query, since it captures meaning rather than just words

<details markdown="1"><summary>Check</summary>

**b)** Each approach's blind spot is the other's strength, which is the whole basis for hybrid search. (a) is false: their failure modes are opposite, not identical. (c) is false: BM25 is purely a term-statistics method with no embedding involved at all. (d) is false: an exact identifier or code match is exactly the case where BM25 can outperform a semantic embedding.

</details>

## Real-world reps

- [ ] Find or write a query for your corpus that includes a specific identifier, code, or exact phrase, and check whether your current retrieval setup (if vector-only) actually surfaces the document containing it.
- [ ] Find a query and a matching document in your corpus that share very few or no exact words but mean the same thing, and predict how a BM25-only search would score that pair.
- [ ] Tomorrow: look up whether your search stack (Postgres full-text search, Elasticsearch, or similar) already exposes a BM25-style ranking function you could compare against your vector search results.

## Going further

- [Paper: "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson and Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- [Docs: "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
