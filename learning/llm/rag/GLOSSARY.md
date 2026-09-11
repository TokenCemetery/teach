---
title: Glossary
description: "Canonical terms for RAG"
type: glossary
---

# RAG Glossary

Canonical terms for a retrieval pipeline: what it splits documents into, and how it decides what to hand the generation step.

## Terms

**Agentic retrieval**:
A system deciding, per query and per step, whether retrieval is needed at all, whether what came back is sufficient, and whether to retrieve again based on something just derived, rather than following one fixed retrieve-then-generate pass.
_Avoid_: multi-hop retrieval (a related but narrower case: multi-hop specifically covers a query's later sub-question depending on an earlier one's answer, while agentic retrieval also covers whether to retrieve at all)

**Chunk**:
One piece of a document, produced by splitting it before embedding and indexing, sized to keep its embedding focused on one topic rather than an average of several.
_Avoid_: segment, passage (use only when quoting a source that uses it)

**Chunking**:
The process of splitting a document into chunks, by a fixed size, by the document's own structure, or by detecting where its topic shifts.
_Avoid_: splitting (too generic; use only in prose describing the mechanical act, not as the process name)

**Error cascading**:
A mistake at an early ingestion step (misidentifying a heading, merging columns in the wrong order) propagating into every later step that operates on the already-corrupted structure it was handed, corrupting a whole section's worth of eventual chunks rather than staying contained to the single element the mistake directly touched.
_Avoid_: an isolated parsing error (understates the effect; the point of naming this cascading is that one early mistake compounds rather than staying local)

**HyDE (Hypothetical Document Embeddings)**:
Embedding a language model's generated hypothetical answer to a query, rather than the query itself, then searching the corpus by similarity to that embedding. Tolerates factually wrong details in the hypothetical document, since the encoder's embedding step filters them out while preserving genuine topical similarity.
_Avoid_: query rewriting (a different query-side fix: rewriting reformulates the query itself, HyDE embeds a generated answer instead of the query)

**Incremental indexing**:
Adding new vectors to an already-built index without rebuilding it from scratch. Well-supported by HNSW, which has no training step; weaker for IVFFlat, whose cluster centroids are fixed at build time and never recomputed, so newly added content that differs from the original training data can be poorly clustered.
_Avoid_: reindexing (a full rebuild from scratch, required specifically when the embedding model changes, not the same operation as incrementally adding new vectors to an unchanged index)

**Ingestion**:
Turning a raw source document (a PDF, HTML page, or office file) into the clean, structured text that chunking actually operates on. A genuine pipeline stage upstream of chunking, with its own failure modes, not a preprocessing detail beneath the pipeline's notice.
_Avoid_: treating chunking as the pipeline's first stage (chunking assumes ingestion already produced clean text; ingestion is what actually produces it)

**Metadata filtering**:
Restricting retrieval to chunks matching a predicate on structured attributes (document type, date, owner, permission tag) in addition to nearest-neighbor similarity, rather than searching the whole corpus by similarity alone.
_Avoid_: permission filtering (a specific, higher-stakes case of metadata filtering, where a failure is a security incident rather than a quality regression, and which specifically requires pre-filtering)

**Multi-hop retrieval**:
Retrieving in a loop where a later query depends on a fact derived from an earlier retrieval, rather than a fixed set of sub-questions decided upfront. Needed when a sub-question can't even be phrased until a prior sub-question's answer is known, which query decomposition alone can't handle.
_Avoid_: query decomposition (splits sub-questions already visible in the original question's text; multi-hop retrieval handles sub-questions that don't exist until a prior hop's answer produces them)

**Post-filtering**:
Running an ANN search first, then discarding results that fail a predicate afterward. Fast, but a selective predicate can discard most of what an approximate index's bounded candidate scan found, collapsing recall; for a permission filter specifically, it also means unauthorized content briefly existed in the pipeline before being discarded.
_Avoid_: pre-filtering (restricts the candidate set before the ANN search runs, preserving recall against the filtered set and never letting disallowed content enter the pipeline at all)

**Pre-filtering**:
Restricting the candidate set to only chunks satisfying a predicate before the ANN search runs, preserving recall against that filtered set regardless of how selective the predicate is. Required for access control specifically, since unauthorized content never enters the pipeline to begin with.
_Avoid_: post-filtering (searches the whole index first and discards afterward; recall and, for permission filters, the security guarantee itself, can both suffer)

**Query decomposition**:
Splitting a compound question into its separate sub-questions and retrieving for each independently, rather than embedding the whole compound question as one vector that sits close to none of the passages that would answer any single part of it well.
_Avoid_: multi-query expansion (a different technique: expansion generates several full reformulations of one question, decomposition splits one question into separate, narrower sub-questions)

**Reindexing**:
Rebuilding a vector index from scratch, required when the embedding model itself changes, since every existing vector was produced by the old model's own vector space and shares no comparable distances with a new model's embeddings. A different operation from incremental indexing, and from the periodic maintenance deletes and updates require.
_Avoid_: incremental indexing (adding new vectors to an unchanged index; reindexing specifically means rebuilding everything because the model producing the vectors changed)
