---
title: RAG
description: "Own retrieval: chunking, embeddings, hybrid search, reranking, and measuring whether the right thing was retrieved"
type: topic
---

# Learning: RAG

Be able to design a retrieval pipeline for a real corpus and use case, and to diagnose why an existing RAG system returns the wrong context instead of guessing at a fix.

**Latest lesson:** [1. Chunking](lessons/0001-chunking.md)

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

Seven stages, first chunk to a diagnosed pipeline. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Chunking | 0001 | The first pipeline choice, and the one every later stage inherits | Can chunk a stated corpus and justify the choice |
| 2. Embeddings | 0002 to 0003 | Embedding models, similarity metrics, dimensionality trade-offs | Can choose an embedding model and metric for a stated corpus |
| 3. Vector search and indexing | 0004 to 0005 | ANN indexes (HNSW/IVF), pgvector specifics, the recall/latency trade-off | Can stand up vector search over pgvector for the chunked corpus |
| 4. Hybrid search | 0006 to 0007 | BM25 plus vector search, reciprocal rank fusion, tuning the blend | Can tune hybrid search weights against a measured retrieval metric |
| 5. Reranking | 0008 to 0009 | Cross-encoder rerankers, when reranking earns its latency cost | Can add a reranking stage and justify it against the cost |
| 6. Retrieval evaluation and diagnosis | 0010 to 0011 | Recall@k, MRR, diagnosing which pipeline stage is at fault | Given wrong retrieved context, can name the at-fault stage |
| 7. From retrieval to generation | 0012 to 0013 | Prompt construction over retrieved context, context-window budget, what generation still gets wrong | Can take retrieved context to a generated answer and name generation-stage failure modes |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-chunking.md) | Chunking | The first pipeline choice, and the one every later stage inherits |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
