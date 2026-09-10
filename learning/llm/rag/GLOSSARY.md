---
title: Glossary
description: "Canonical terms for RAG"
type: glossary
---

# RAG Glossary

Canonical terms for a retrieval pipeline: what it splits documents into, and how it decides what to hand the generation step.

## Terms

**Chunk**:
One piece of a document, produced by splitting it before embedding and indexing, sized to keep its embedding focused on one topic rather than an average of several.
_Avoid_: segment, passage (use only when quoting a source that uses it)

**Chunking**:
The process of splitting a document into chunks, by a fixed size, by the document's own structure, or by detecting where its topic shifts.
_Avoid_: splitting (too generic; use only in prose describing the mechanical act, not as the process name)

**HyDE (Hypothetical Document Embeddings)**:
Embedding a language model's generated hypothetical answer to a query, rather than the query itself, then searching the corpus by similarity to that embedding. Tolerates factually wrong details in the hypothetical document, since the encoder's embedding step filters them out while preserving genuine topical similarity.
_Avoid_: query rewriting (a different query-side fix: rewriting reformulates the query itself, HyDE embeds a generated answer instead of the query)

**Query decomposition**:
Splitting a compound question into its separate sub-questions and retrieving for each independently, rather than embedding the whole compound question as one vector that sits close to none of the passages that would answer any single part of it well.
_Avoid_: multi-query expansion (a different technique: expansion generates several full reformulations of one question, decomposition splits one question into separate, narrower sub-questions)
