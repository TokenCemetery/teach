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
  Official repo for the vector store this workspace standardizes on: index types (IVFFlat, HNSW), distance functions, and the operators that make a Postgres table a vector index. Use for: how to run and configure pgvector itself.
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

## Gaps

- No source yet on semantic chunking specifically for structured or code-heavy corpora (as opposed to prose), where fixed-size and paragraph-boundary heuristics both perform poorly; worth closing once lesson design reaches chunking strategy selection.
