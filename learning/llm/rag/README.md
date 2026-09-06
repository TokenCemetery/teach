---
title: RAG
description: "Own retrieval: chunking, embeddings, hybrid search, reranking, and measuring whether the right thing was retrieved"
type: topic
---

# Learning: RAG

Be able to design a retrieval pipeline for a real corpus and use case, and to diagnose why an existing RAG system returns the wrong context instead of guessing at a fix.

**Latest lesson:** _none yet_

## Success looks like

- Design a retrieval pipeline (chunking, embeddings, hybrid search, reranking) for a stated corpus and use case, and justify each choice against it.
- Given a RAG system returning wrong or irrelevant context, diagnose which stage of the pipeline is at fault rather than re-tuning at random.
- Tune hybrid search weights against a measured retrieval metric rather than by feel.
- Take retrieved context through to a generated answer and account for what the generation step itself can still get wrong.

## Constraints

- Vector store: pgvector, so the concepts connect to `data/postgres`'s coverage of what a vector index costs the database.

## Out of scope

- Prompt-engineering technique and generation quality in general: touched only for how retrieved context reaches the generation step, not restated as its own topic.
- How the retrieval metric itself is built and defended: that is `llm/evals`, linked to rather than restated.
- What a vector index costs the database operationally: that is `data/postgres`, linked to rather than restated.

## The arc

{N} stages, {start} to {end}. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
|---|---|---|
| 1. {Name} | {What it covers} | {The capability that closes the stage} |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| _none yet_ | | |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
