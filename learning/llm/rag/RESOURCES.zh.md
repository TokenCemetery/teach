---
title: "资源"
description: "RAG 的可信资料来源"
type: resources
---

# RAG 资源

## 知识

- [文章：“Chunking Strategies for LLM Applications”，Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
  对各种分块方法（固定大小、递归、语义、文档结构感知）的从业者综述，以及每种方法在上下文与精确度之间所做的取舍。用途：为给定的语料库选择并论证分块策略。
- [仓库：pgvector，pgvector](https://github.com/pgvector/pgvector)
  本工作区统一采用的向量存储的官方仓库：索引类型（IVFFlat、HNSW）、距离函数、让 Postgres 表成为向量索引的运算符，以及它自己的维护指南（删除后先重建索引再做 vacuum，IVFFlat 对训练数据的依赖）。用途：如何运行和配置 pgvector 本身，以及每种索引类型对增量添加和删除的处理有何不同。
- [论文：“Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks”，Reimers 和 Gurevych，2019](https://arxiv.org/abs/1908.10084)
  几乎每条检索流水线都在用的双编码器嵌入方法背后的论文：为什么共享的嵌入空间可以让相似度通过距离来计算，而不必对每一对文本都运行一遍模型。用途：理解嵌入模型实际上在优化什么。
- [论文：“Passage Re-ranking with BERT”，Nogueira 和 Cho，2019](https://arxiv.org/abs/1901.04085)
  提出了交叉编码器重排序：把查询与段落作为一对一起打分，而不是按嵌入距离，代价是每个候选都要运行一次模型。用途：为什么会有重排序阶段，以及它相比单纯的嵌入相似度多带来了什么。
- [文档：“Reciprocal rank fusion (RRF)”，Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
  解释了把关键词搜索的排名与向量搜索的排名合并成一个混合排名的标准方法，包括公式和它唯一的调节参数。用途：混合检索究竟是如何合并它的两个排名的。
- [文档：“Reranking”，Cohere](https://docs.cohere.com/docs/reranking)
  面向从业者的托管交叉编码器重排序器文档：如何调用，它在延迟上要付出什么代价，以及它在检索流水线中的位置。用途：一个具体、可运行的重排序阶段，可以与上面 Nogueira 和 Cho 的论文对照着思考。
- [文章：“Evaluation Measures for Search and Recommender Systems”，Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
  逐一讲解标准的检索指标（Recall@k、MRR、nDCG），以及如何针对带标注的或合成的查询集计算每一个。用途：衡量是否检索到了正确的内容，然后再把这个数字交给 `llm/evals`，学习如何为它辩护。
- [论文：“Matryoshka Representation Learning”，Kusupati 等，2022](https://arxiv.org/abs/2205.13147)
  提出了这样训练的嵌入：完整向量被截断后的前缀，本身仍是有意义、可用的嵌入，所以维度可以在训练之后与存储和延迟做权衡，而不是只能事先选一个更小的模型。用途：理解什么时候可以安全地截断嵌入向量，什么时候不行。
- [论文：“Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs”，Malkov 和 Yashunin，2018](https://arxiv.org/abs/1603.09320)
  HNSW 背后的论文。HNSW 是 pgvector 和大多数向量数据库使用的基于图的近似最近邻索引：它的多层结构，以及其搜索深度参数所控制的召回率与延迟之间的权衡。用途：理解 ANN 索引实际上用什么代替了精确搜索，以及它的调节旋钮为什么是用召回率换速度。
- [论文：“The Probabilistic Relevance Framework: BM25 and Beyond”，Robertson 和 Zaragoza，2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
  BM25 的权威参考。BM25 是词法排序函数，其背后是词频、逆文档频率和长度归一化的打分，论文还给出了每个参数背后的道理。用途：理解词法检索实际在给什么打分，它与向量检索的语义相似度正好互补。
- [论文：“Lost in the Middle: How Language Models Use Long Contexts”，Liu 等，2023](https://arxiv.org/abs/2307.03172)
  表明即使所有内容在技术上都在上下文窗口之内，模型对放在长上下文开头或结尾的信息的利用，也比埋在中间的信息可靠得多。用途：理解为什么文本块在组装好的提示词中放在哪里，与它有没有被检索到同样重要。
- [论文：“RAGAS: Automated Evaluation of Retrieval Augmented Generation”，Es 等，2023](https://arxiv.org/abs/2309.15217)
  把忠实性（生成的论断是否确实有检索到的上下文支持）定义为一个区别于检索质量的指标，并说明如何在不必为每个生成的答案重新人工标注真值的情况下检查它。用途：在确认检索本身正确之后，评估生成步骤是否始终以检索到的内容为依据。

- [论文：“Precise Zero-Shot Dense Retrieval without Relevance Labels”（HyDE），Gao 等，2022](https://arxiv.org/abs/2212.10496)
  提出嵌入生成的假设性答案，而不是查询本身，让编码器的稠密瓶颈过滤掉假设文档中事实上的错误，同时保留它真正的相关性信号。用途：为什么一篇编造的、有时还是错的文档仍然能改善检索，背后的确切机制。
- [论文：“Policy-aware Vector Search: A Vision for Fine Grained Access Control in Vector Databases”，Yalamarthi 和 Pappachan，2026](https://arxiv.org/abs/2606.19803)
  把细粒度访问控制形式化为向量数据库中的一个执行问题，并指出正确执行、ANN 召回率和查询延迟三者之间固有的张力。用途：为什么访问控制尤其需要预过滤，而不能用更快、但会损害召回率并带来安全风险的后过滤。
- [论文：“Docling Technical Report”，Auer 等，2024](https://arxiv.org/abs/2408.09869)
  介绍了用于 PDF 转换的版面分析（DocLayNet）与表格结构识别（TableFormer）流水线，作为会把版面和表格结构压平的朴素文本提取的替代方案。用途：版面感知的摄取流水线究竟检测并重建了什么，而这些是普通文本提取器丢掉的。
- [论文：“Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions”（IRCoT），Trivedi 等，2022](https://arxiv.org/abs/2212.10509)
  准确说明了单次检索为什么解决不了多步问题（该检索什么，取决于已经推导出了什么），并通过把一步推理和一步检索交错进行来解决它。用途：后一次查询依赖前一跳答案的检索循环背后的机制。
- [论文：“Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection”，Asai 等，2023](https://arxiv.org/abs/2310.11511)
  训练模型自己决定是否需要检索，并对检索到的段落做评判，而不是每次都不加区分地检索固定数量的段落。用途：智能体式检索的另一条轴线，即是否要检索，区别于一个多步问题需要几跳。
- [指南：“RAG Observability: How Coralogix Helps You Trace Retrieval-to-Generation Quality”，Coralogix，2026](https://coralogix.com/guides/rag-observability/)
  讲述了为什么普通的基础设施监控（延迟、吞吐量、错误率）在检索和上下文窗口悄悄出问题时依然一片绿色，以及能抓住这些问题的无参照信号、上下文窗口利用率信号和嵌入漂移信号。用途：流水线上线之后到底该监控什么，这超出了第 10 课所讲的离线指标。
- [论文：“Lost in the Middle: How Language Models Use Long Contexts”，Liu 等，2023](https://arxiv.org/abs/2307.03172)
  表明即使所有内容在技术上都在上下文窗口之内，模型对放在长上下文开头或结尾的信息的利用，也比埋在中间的信息可靠得多。用途：理解为什么把相关文本块放在上下文靠前位置的检索，胜过把整个语料库重新发送过去，因为那样相关的部分会沉到中间。

## 空白

- 目前还没有专门讲结构化或代码密集型语料库（相对于散文）的语义分块的资料，对这类语料库，固定大小和按段落边界切分的启发式方法表现都不好；等课程设计推进到分块策略选择时，值得补上。
