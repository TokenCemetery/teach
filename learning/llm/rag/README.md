---
title: RAG
description: "Own retrieval: chunking, embeddings, hybrid search, reranking, and measuring whether the right thing was retrieved"
type: topic
---

# Learning: RAG

Be able to design a retrieval pipeline for a real corpus and use case, and to diagnose why an existing RAG system returns the wrong context instead of guessing at a fix.

**Latest lesson:** [19. Cost, Latency, and Production Monitoring](lessons/0019-cost-latency-and-production-monitoring.md)

## Success looks like

- Design a retrieval pipeline (chunking, embeddings, hybrid search, reranking) for a stated corpus and use case, and justify each choice against it.
- Given a RAG system returning wrong or irrelevant context, diagnose which stage of the pipeline is at fault rather than re-tuning at random.
- Tune hybrid search weights against a measured retrieval metric rather than by feel.
- Take retrieved context through to a generated answer and account for what the generation step itself can still get wrong.

## Constraints

- Assumes basic Python and familiarity with what an embedding is; no prior retrieval-systems experience required.
- Vector store: pgvector, so the concepts connect to `data/postgres`'s coverage of what a vector index costs the database.

## Out of scope

- Prompt-engineering technique and generation quality in general: touched only for how retrieved context reaches the generation step, not restated as its own topic.
- How the retrieval metric itself is built and defended: that is `llm/evals`, linked to rather than restated.
- What a vector index costs the database operationally: that is `data/postgres`, linked to rather than restated.

## The arc

Thirteen stages, first chunk to a diagnosed, cost-aware, monitored production pipeline. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Chunking | 0001 | The first pipeline choice, and the one every later stage inherits | Can chunk a stated corpus and justify the choice |
| 2. Embeddings | 0002 to 0003 | Embedding models, similarity metrics, dimensionality trade-offs | Can choose an embedding model and metric for a stated corpus |
| 3. Vector search and indexing | 0004 to 0005 | ANN indexes (HNSW/IVF), pgvector specifics, the recall/latency trade-off | Can stand up vector search over pgvector for the chunked corpus |
| 4. Hybrid search | 0006 to 0007 | BM25 plus vector search, reciprocal rank fusion, tuning the blend | Can tune hybrid search weights against a measured retrieval metric |
| 5. Reranking | 0008 to 0009 | Cross-encoder rerankers, when reranking earns its latency cost | Can add a reranking stage and justify it against the cost |
| 6. Retrieval evaluation and diagnosis | 0010 to 0011 | Recall@k, MRR, diagnosing which pipeline stage is at fault | Given wrong retrieved context, can name the at-fault stage |
| 7. From retrieval to generation | 0012 to 0013 | Prompt construction over retrieved context, context-window budget, what generation still gets wrong | Can take retrieved context to a generated answer and name generation-stage failure modes |
| 8. Query-side transformation | 0014 | HyDE, query rewriting, multi-query expansion, query decomposition | Given a query-side failure lesson 11's procedure doesn't catch, can pick and justify the right remedy |
| 9. Metadata filtering and permission-aware retrieval | 0015 | Metadata filtering, pre- vs. post-filtering, why access control specifically needs pre-filtering | Can design a permission-aware retrieval path and explain why post-filtering is unsafe for it |
| 10. The ingestion pipeline | 0016 | Parsing PDFs/HTML/office documents, layout-aware vs. naive extraction, table structure, error cascading | Can explain why ingestion is upstream of chunking, and how a bad parse escapes lesson 11's diagnosis |
| 11. Freshness | 0017 | Incremental indexing (HNSW vs. IVFFlat), delete/update maintenance, reindexing on a model change | Can plan for the three genuinely different ways a corpus and its index go stale |
| 12. Multi-hop and agentic retrieval | 0018 | IRCoT's interleaved reasoning and retrieval, Self-RAG's adaptive retrieval decision | Can design a retrieval loop for a question decomposition alone can't answer |
| 13. Cost, latency, and production monitoring | 0019 | Whole-pipeline latency budget, context window utilization, reference-free scoring, embedding drift | Can budget the full pipeline's latency and monitor retrieval quality once it's live, without ground truth |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-chunking.md) | Chunking | The first pipeline choice, and the one every later stage inherits |
| [0002](lessons/0002-embedding-models-and-similarity.md) | Embedding Models and Similarity | What a bi-encoder embedding model does, and why the similarity metric has to match how it was trained |
| [0003](lessons/0003-embedding-dimensionality.md) | Embedding Dimensionality Trade-offs | Why a bigger embedding vector isn't free, and when it's safe to truncate one instead of choosing a smaller model |
| [0004](lessons/0004-ann-indexes.md) | ANN Indexes: HNSW and IVF | Why vector search trades exactness for speed, and how IVF and HNSW each expose that trade-off as a tunable knob |
| [0005](lessons/0005-pgvector-specifics.md) | pgvector Specifics | Standing up vector search in Postgres, and mapping lesson 4's index concepts onto pgvector's actual operators and parameters |
| [0006](lessons/0006-bm25-and-lexical-search.md) | BM25 and Lexical Search | What BM25 actually scores, and why exact-term matching still catches what semantic embeddings miss |
| [0007](lessons/0007-reciprocal-rank-fusion.md) | Reciprocal Rank Fusion | How to combine a lexical ranking and a vector ranking without comparing incomparable scores, and how to tune the blend against a measured metric |
| [0008](lessons/0008-cross-encoder-rerankers.md) | Cross-Encoder Rerankers | What a cross-encoder scores that a bi-encoder can't, and why reranking is a second stage rather than a replacement for retrieval |
| [0009](lessons/0009-when-reranking-earns-its-cost.md) | When Reranking Earns Its Cost | A decision framework for whether a reranking stage is worth its added latency for a given workload |
| [0010](lessons/0010-recall-at-k-and-mrr.md) | Recall@k and MRR | The two standard retrieval metrics, what each one tells you that the other doesn't, and how to pick k for the workload |
| [0011](lessons/0011-diagnosing-the-pipeline.md) | Diagnosing the Pipeline | A stage-by-stage procedure for finding which part of a retrieval pipeline is actually responsible for wrong retrieved context |
| [0012](lessons/0012-prompt-construction-and-context-budget.md) | Prompt Construction and Context-Window Budget | Why retrieved chunks compete for a shared context-window budget, and why where a chunk sits in the prompt matters as much as whether it was retrieved |
| [0013](lessons/0013-what-generation-still-gets-wrong.md) | What Generation Still Gets Wrong | The failure modes that survive even correct, well-placed retrieved context, and how they differ from a retrieval failure |
| [0014](lessons/0014-query-side-transformation.md) | Query-Side Transformation | Lesson 11's diagnosis procedure checks chunking, embedding, the index, hybrid weighting, and reranking, but never the query itself, and a query that's too short, too compound, or phrased nothing like the corpus needs its own remedy, not another pipeline-stage fix |
| [0015](lessons/0015-metadata-filtering-and-access-control.md) | Metadata Filtering and Permission-Aware Retrieval | An access-control filter that fails doesn't crash and doesn't look wrong, it produces a perfectly well-formed answer built from a document the user was never supposed to see, which is exactly why post-filtering is the wrong choice for this one kind of filter |
| [0016](lessons/0016-the-ingestion-pipeline.md) | The Ingestion Pipeline | Chunking was never actually the first pipeline stage, it just assumed clean input text already existed, and a bad parse upstream of chunking corrupts everything after it while looking, to every later diagnostic, like a completely different failure |
| [0017](lessons/0017-freshness.md) | Freshness | A corpus that keeps changing needs three genuinely different answers, not one, since adding a document, deleting one, and swapping the embedding model each break a different assumption the index was built on |
| [0018](lessons/0018-multi-hop-and-agentic-retrieval.md) | Multi-Hop and Agentic Retrieval | Decomposition splits a compound question into sub-questions you can already see in the original text, but some questions only reveal their second half once the first half's answer comes back, which needs an actual loop, not a smarter upfront split |
| [0019](lessons/0019-cost-latency-and-production-monitoring.md) | Cost, Latency, and Production Monitoring | A pipeline can look perfectly healthy on every ordinary infrastructure signal while quietly serving a confident answer built on a document that never actually reached the model, and that gap is exactly what retrieval-specific monitoring exists to close |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources
- [Chunking and Embeddings](reference/chunking-and-embeddings.md): chunking strategies, embedding models, similarity metrics, dimensionality trade-offs
- [Vector Search and Indexing](reference/vector-search-and-indexing.md): ANN indexes (HNSW/IVF), pgvector specifics, the recall/latency trade-off
- [Hybrid Search](reference/hybrid-search.md): BM25 plus vector search, reciprocal rank fusion, tuning the blend
- [Reranking](reference/reranking.md): cross-encoder rerankers, and when reranking earns its latency cost
- [Retrieval Evaluation](reference/retrieval-evaluation.md): Recall@k, MRR, and diagnosing which pipeline stage is at fault
- [Generation from Retrieval](reference/generation-from-retrieval.md): prompt construction over retrieved context, context-window budget, generation-stage failure modes

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
