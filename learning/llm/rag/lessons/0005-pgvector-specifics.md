---
title: 5. pgvector Specifics
description: Standing up vector search in Postgres, and mapping lesson 4's index concepts onto pgvector's actual operators and parameters
type: lesson
---

# Lesson 5. pgvector Specifics

**Mission link:** This is stage 3's capstone: lesson 4's IVF and HNSW concepts become a real schema, a real distance operator, and real tuning parameters here, over the vector store this workspace standardizes on.
**Primary source:** [Repo: pgvector, pgvector](https://github.com/pgvector/pgvector)
**Prerequisites:** [Lesson 4](0004-ann-indexes.md), [Chunk](../GLOSSARY.md)

## Warm-up

1. ▢ What does IVF's `nprobe` parameter, and HNSW's `ef_search` parameter, each control?

<details markdown="1"><summary>Check</summary>

`nprobe` sets how many of IVF's clusters get searched at query time; `ef_search` sets how many candidates HNSW's graph search keeps track of at each step. Both trade recall against latency: higher values search more, improving recall at a latency cost.

</details>

2. ▢ Why do cosine similarity and dot product produce the same ranking only when embedding vectors are normalized to unit length?

<details markdown="1"><summary>Check</summary>

Dot product is cosine similarity scaled by the two vectors' magnitudes. When both are fixed at unit length, that scaling factor is identical for every pair, so the rankings match; when magnitudes vary, dot product favors larger vectors.

</details>

## Know this

### A vector column and a distance operator

pgvector adds a `vector(N)` column type to Postgres, sized to the embedding dimensionality lesson 3 settled on:

```sql
CREATE EXTENSION vector;
CREATE TABLE chunks (id bigserial PRIMARY KEY, content text, embedding vector(1536));
```

Similarity is computed with one of three operators: `<->` (Euclidean/L2 distance), `<#>` (negative inner product), and `<=>` (cosine distance). The operator has to match the metric the embedding model was trained for (lesson 2): using `<=>` against a model trained for raw dot product, or vice versa, is the exact mismatch lesson 2 warned degrades ranking quality, now expressed as a concrete SQL choice rather than an abstract one. Note the sign on `<#>`: it's negative inner product specifically so that, like the other two operators, smaller means more similar, keeping `ORDER BY` ascending consistent across all three.

### An index has to be built for one specific distance function

Creating an index means choosing an operator class matching the intended distance function:

```sql
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
```

`vector_cosine_ops`, `vector_l2_ops`, and `vector_ip_ops` each build the index for one specific operator. An index built with `vector_l2_ops` doesn't accelerate a query ordering by `<=>` (cosine distance); the operator class and the query's operator have to match, or the index goes unused and the query silently falls back to a full sequential scan, which defeats the entire point of building the index.

### pgvector's parameter names are lesson 4's parameters, under different names

HNSW's index-build parameters, `m` (maximum connections per node) and `ef_construction` (build-time search depth), are exactly lesson 4's HNSW tuning knobs, set at `CREATE INDEX` time. Its query-time recall/latency knob is a session setting: `SET hnsw.ef_search = 100;`, lesson 4's `ef_search` by another name. IVFFlat's build parameter is `lists` (the cluster count lesson 4 called out), set the same way at index creation, and its query-time knob is `SET ivfflat.probes = 10;`, lesson 4's `nprobe`.

### IVFFlat needs data before it's built well; HNSW doesn't

IVFFlat's clustering step needs a representative sample of the table's actual vectors to place its cluster centroids well, which means building an IVFFlat index against an empty or barely-populated table produces poor clusters that don't reflect the corpus's real vector distribution. The practical consequence: load the data first, then build the IVFFlat index. HNSW's graph structure is built incrementally as vectors are inserted, with no equivalent dependency on the table already being populated, which is part of why HNSW is often preferred for a table expected to grow over time, on top of the recall/latency advantage lesson 4 already described.

## Practice

1. ▢ An embedding model was trained so that cosine similarity reflects semantic closeness. Which pgvector operator and operator class should the query and its index both use?

<details markdown="1"><summary>Check</summary>

The `<=>` operator (cosine distance) for the query, and `vector_cosine_ops` for the index. Using an operator or operator class built for a different distance function than the one the model was trained for reintroduces lesson 2's metric-mismatch problem, now as a concrete SQL mismatch.

</details>

2. ▢ A team builds an HNSW index with `vector_l2_ops`, but their queries order results using the `<=>` operator (cosine distance). What happens, and why is this a problem beyond just "the wrong answer"?

<details markdown="1"><summary>Hint</summary>

Think about whether the index can even be used for a query whose operator doesn't match the operator class it was built with.

</details>

<details markdown="1"><summary>Check</summary>

The index built for `vector_l2_ops` doesn't accelerate a query using `<=>`, since the index is built for one specific distance function. The query falls back to a full sequential scan over the table, which is slow at any real corpus size; it isn't merely a wrong-answer risk, it's losing the entire performance benefit the index existed to provide.

</details>

3. ▢ A table has an IVFFlat index with `lists = 1000`, but the query-time setting `ivfflat.probes` is left at its default of 1. What does this mean for the recall/latency trade-off, in terms of lesson 4's `nprobe`?

<details markdown="1"><summary>Check</summary>

`ivfflat.probes = 1` is `nprobe = 1`: only the single nearest of the 1,000 clusters gets searched. That's the fastest, lowest-recall end of lesson 4's trade-off; a query near a cluster boundary can miss true nearest neighbors sitting in an adjacent cluster. Raising `probes` searches more clusters, trading query latency for higher recall.

</details>

4. ▢ Why does build order matter for an IVFFlat index (load data, then build) but not for HNSW?

<details markdown="1"><summary>Check</summary>

IVFFlat's clustering step needs a representative sample of the table's real vectors to place its cluster centroids well; building it against an empty or sparsely populated table produces poor clusters that don't reflect the actual data distribution. HNSW's graph is built incrementally as vectors are inserted, with no equivalent need for the table to already hold a representative sample first.

</details>

5. ▢ Which claim is true of pgvector's operator classes (`vector_cosine_ops`, `vector_l2_ops`, `vector_ip_ops`)?

   - a) Any operator class works with any query operator, since pgvector converts between distance functions automatically
   - b) An index's operator class must match the query's distance operator, or the index won't be used for that query
   - c) Operator class only affects HNSW indexes, not IVFFlat
   - d) `vector_ip_ops` cannot be used with normalized embedding vectors

<details markdown="1"><summary>Check</summary>

**b)** The operator class and the query's operator have to match, or the query falls back to a sequential scan instead of using the index. (a) is false: there's no automatic conversion between distance functions. (c) is false: both index types require matching an operator class to the distance function. (d) is false: normalized vectors are exactly the case where inner product and cosine distance coincide, as lesson 2 covered.

</details>

## Real-world reps

- [ ] Create a small pgvector table with a `vector(N)` column sized to an embedding model you use, and build an index with the operator class matching that model's trained similarity metric.
- [ ] Run `EXPLAIN` on a similarity query against your table and confirm the index is actually being used, not falling back to a sequential scan.
- [ ] Tomorrow: try two different values of `ivfflat.probes` or `hnsw.ef_search` against the same query and compare both the returned results and the query latency.

## Going further

- [Repo: pgvector, pgvector](https://github.com/pgvector/pgvector)
- [Paper: "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", Malkov and Yashunin, 2018](https://arxiv.org/abs/1603.09320)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
