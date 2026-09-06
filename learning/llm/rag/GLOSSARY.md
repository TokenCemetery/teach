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
