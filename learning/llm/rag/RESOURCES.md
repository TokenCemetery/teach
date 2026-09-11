---
title: Resources
description: "Trusted sources for RAG"
type: resources
---

# RAG Resources

## Knowledge

- [Article: "Chunking Strategies for LLM Applications", Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
  Practitioner survey of chunking approaches (fixed-size, recursive, semantic, document-structure-aware) and the trade-offs each makes between context and precision. Use for: choosing and justifying a chunking strategy for a given corpus.
- [Repo: pgvector, pgvector](https://github.com/pgvector/pgvector)
  Official repo for the vector store this workspace standardizes on: index types (IVFFlat, HNSW), distance functions, the operators that make a Postgres table a vector index, and its own maintenance guidance (reindexing before vacuuming after deletes, IVFFlat's training-data dependency). Use for: how to run and configure pgvector itself, and how each index type handles incremental additions and deletes differently.
- [Paper: "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks", Reimers and Gurevych, 2019](https://arxiv.org/abs/1908.10084)
  The paper behind the bi-encoder embedding approach nearly every retrieval pipeline uses: why a shared embedding space lets similarity be computed by distance instead of by running the model on every pair. Use for: understanding what an embedding model is actually optimizing for.
- [Paper: "Passage Re-ranking with BERT", Nogueira and Cho, 2019](https://arxiv.org/abs/1901.04085)
  Introduces cross-encoder reranking: scoring a query-passage pair jointly rather than by embedding distance, at the cost of running the model once per candidate. Use for: why a reranking stage exists and what it buys over embedding similarity alone.
- [Docs: "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
  Explains the standard method for combining a keyword-search ranking and a vector-search ranking into one hybrid ranking, with the formula and its one tuning parameter. Use for: how hybrid search actually combines its two rankings.
- [Docs: "Reranking", Cohere](https://docs.cohere.com/docs/reranking)
  Practitioner-facing docs for a hosted cross-encoder reranker: how it's called, what it costs in latency, and where it sits in a retrieval pipeline. Use for: a concrete, runnable reranking stage to reason about alongside the Nogueira and Cho paper above.
- [Article: "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
  Walks through the standard retrieval metrics (Recall@k, MRR, nDCG) and how to compute each against a labeled or synthetic query set. Use for: measuring whether the right thing was retrieved, before handing that number to `llm/evals` for how to defend it.
- [Paper: "Matryoshka Representation Learning", Kusupati et al., 2022](https://arxiv.org/abs/2205.13147)
  Introduces embeddings trained so that a truncated prefix of the full vector remains a meaningful, usable embedding on its own, letting dimensionality be traded against storage and latency after training rather than only by choosing a smaller model upfront. Use for: understanding when it's safe to truncate an embedding vector, and when it isn't.
- [Paper: "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", Malkov and Yashunin, 2018](https://arxiv.org/abs/1603.09320)
  The paper behind HNSW, the graph-based approximate nearest neighbor index pgvector and most vector databases use: its multi-layer structure and the recall/latency trade-off its search-depth parameter controls. Use for: understanding what an ANN index actually does instead of exact search, and why its tuning knob trades recall for speed.
- [Paper: "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson and Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
  The definitive reference for BM25, the lexical ranking function behind term-frequency, inverse-document-frequency, and length-normalization scoring, with the reasoning behind each of its parameters. Use for: understanding what lexical search actually scores, as the complement to vector search's semantic similarity.
- [Paper: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
  Shows that models use information placed at the beginning or end of a long context far more reliably than information buried in the middle, even when everything is technically within the context window. Use for: understanding why chunk placement in an assembled prompt matters as much as whether a chunk was retrieved at all.
- [Paper: "RAGAS: Automated Evaluation of Retrieval Augmented Generation", Es et al., 2023](https://arxiv.org/abs/2309.15217)
  Defines faithfulness (whether a generated claim is actually supported by the retrieved context) as a metric distinct from retrieval quality, and how to check it without needing new human-labeled ground truth for every generated answer. Use for: evaluating whether the generation step stayed grounded in what was retrieved, once retrieval itself is confirmed correct.

- [Paper: "Precise Zero-Shot Dense Retrieval without Relevance Labels" (HyDE), Gao et al., 2022](https://arxiv.org/abs/2212.10496)
  Introduces embedding a generated hypothetical answer instead of the query itself, letting the encoder's dense bottleneck filter out the hypothetical document's factual errors while keeping its genuine relevance signal. Use for: the precise mechanism behind why an invented, sometimes-wrong document still improves retrieval.
- [Paper: "Policy-aware Vector Search: A Vision for Fine Grained Access Control in Vector Databases", Yalamarthi and Pappachan, 2026](https://arxiv.org/abs/2606.19803)
  Formalizes fine-grained access control as an enforcement problem in vector databases, and the inherent tension between correct enforcement, ANN recall, and query latency. Use for: why access control specifically needs pre-filtering rather than the faster but recall- and security-risking post-filtering.
- [Paper: "Docling Technical Report", Auer et al., 2024](https://arxiv.org/abs/2408.09869)
  Introduces a layout-analysis (DocLayNet) and table-structure-recognition (TableFormer) pipeline for PDF conversion, as the alternative to naive text extraction that flattens layout and table structure. Use for: what a layout-aware ingestion pipeline actually detects and reconstructs that a plain text extractor discards.
- [Paper: "Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions" (IRCoT), Trivedi et al., 2022](https://arxiv.org/abs/2212.10509)
  States precisely why single-pass retrieval fails multi-step questions (what to retrieve depends on what's already been derived) and interleaves a reasoning step with a retrieval step to solve it. Use for: the mechanism behind a retrieval loop where a later query depends on an earlier hop's answer.
- [Paper: "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection", Asai et al., 2023](https://arxiv.org/abs/2310.11511)
  Trains a model to decide whether retrieval is needed at all and to critique retrieved passages, rather than retrieving a fixed number of passages indiscriminately every time. Use for: agentic retrieval's other axis, whether to retrieve at all, distinct from how many hops a multi-step question needs.

## Gaps

- No source yet on semantic chunking specifically for structured or code-heavy corpora (as opposed to prose), where fixed-size and paragraph-boundary heuristics both perform poorly; worth closing once lesson design reaches chunking strategy selection.
