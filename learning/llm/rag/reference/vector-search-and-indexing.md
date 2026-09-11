---
title: Vector Search and Indexing
description: IVF and HNSW's recall/latency trade-off, and pgvector's operators, index parameters, and build-order specifics
type: reference
---

# Vector Search and Indexing

Approximate nearest neighbor search and its pgvector implementation. Built for lookup when standing up or tuning an index.

## Why exact search doesn't scale

Exact nearest-neighbor search compares a query against every vector: linear in corpus size, too slow at millions of chunks. An **approximate nearest neighbor (ANN)** index accepts a small, controllable amount of inexactness in exchange for search times that don't scale linearly.

## IVF and HNSW

| Index | Mechanism | Search-time knob | Build cost |
|---|---|---|---|
| IVF (inverted file) | Partitions vectors into clusters (k-means) ahead of time; searches only the `nprobe` nearest clusters | `nprobe`: low = fast, may miss neighbors near a cluster boundary; high = approaches exact search | Needs a representative sample of the corpus to place centroids well |
| HNSW (hierarchical navigable small world) | Multi-layer graph; sparse top layers for long jumps, dense bottom layer for precise local search, descended greedily | `ef_search`: how many candidates are tracked at each step; low = fast but may settle for a locally good node; high = more recall | More memory (graph edges) and a slower index build than IVF |

Both knobs dial a point on a **recall/latency curve** for a given corpus; neither has one universally correct setting. HNSW generally reaches a better point on that curve than IVF (higher recall at the same latency), at the cost of memory and build time. The right point depends on the workload's latency budget and how much recall loss a later stage (reranking) can absorb, measured rather than assumed.

## pgvector: column, operator, index

```sql
CREATE EXTENSION vector;
CREATE TABLE chunks (id bigserial PRIMARY KEY, content text, embedding vector(1536));
```

| Operator | Distance | Operator class (for indexing) |
|---|---|---|
| `<->` | Euclidean/L2 | `vector_l2_ops` |
| `<#>` | Negative inner product | `vector_ip_ops` |
| `<=>` | Cosine | `vector_cosine_ops` |

`<#>` is *negative* inner product specifically so that, like the other two, smaller means more similar, keeping `ORDER BY` ascending consistent across all three. The operator has to match [the metric the embedding model was trained for](chunking-and-embeddings.md#similarity-metrics-must-match-training): using `<=>` against a dot-product-trained model (or vice versa) is that same metric mismatch, now a concrete SQL choice.

```sql
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
```

**An index is built for one specific distance function.** A query ordering by an operator that doesn't match the index's operator class does not use that index at all: it silently falls back to a full sequential scan, losing the entire performance benefit the index existed to provide. There is no automatic conversion between distance functions.

## pgvector's parameters are lesson 4's, renamed

| Concept | HNSW | IVFFlat |
|---|---|---|
| Build-time parameter(s) | `m` (max connections per node), `ef_construction` (build-time search depth), set at `CREATE INDEX` | `lists` (cluster count), set at `CREATE INDEX` |
| Query-time recall/latency knob | `SET hnsw.ef_search = 100;` | `SET ivfflat.probes = 10;` (this is `nprobe`) |

## Build order matters for IVFFlat, not HNSW

IVFFlat's clustering step needs a representative sample of the table's actual vectors to place centroids well: building it against an empty or sparse table produces poor clusters. Load the data first, then build the IVFFlat index. HNSW's graph is built incrementally as vectors are inserted, with no equivalent dependency, which is part of why HNSW is often preferred for a table expected to grow over time.

## Related

- [Lesson 4](../lessons/0004-ann-indexes.md), [Lesson 5](../lessons/0005-pgvector-specifics.md)
- [Chunking and Embeddings](chunking-and-embeddings.md): the vectors and similarity metric this sheet's index has to match
