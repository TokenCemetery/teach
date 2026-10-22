---
title: संसाधन
description: "RAG के लिए भरोसेमंद स्रोत"
type: resources
---

# RAG संसाधन

## ज्ञान

- [लेख: "Chunking Strategies for LLM Applications", Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
  Chunking के तरीक़ों (fixed-size, recursive, semantic, document-structure-aware) का practitioner सर्वेक्षण, और हर एक context और precision के बीच कौन-सा trade-off करता है। इस्तेमाल: किसी दिए corpus के लिए chunking रणनीति चुनना और उसे सही ठहराना।
- [Repo: pgvector, pgvector](https://github.com/pgvector/pgvector)
  उस vector store का आधिकारिक repo जिस पर यह workspace मानक के रूप में टिका है: index के प्रकार (IVFFlat, HNSW), distance functions, वे operators जो Postgres table को vector index बनाते हैं, और रखरखाव की उसकी अपनी सलाह (deletes के बाद vacuum से पहले reindex करना, IVFFlat की training-data पर निर्भरता)। इस्तेमाल: pgvector को ख़ुद कैसे चलाएँ और configure करें, और हर index प्रकार incremental additions और deletes को अलग ढंग से कैसे संभालता है।
- [पेपर: "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks", Reimers and Gurevych, 2019](https://arxiv.org/abs/1908.10084)
  उस bi-encoder embedding approach के पीछे का पेपर जो लगभग हर retrieval pipeline इस्तेमाल करता है: साझा embedding space similarity को हर जोड़ी पर model चलाने के बजाय दूरी से निकालने क्यों देती है। इस्तेमाल: यह समझना कि embedding model असल में किस चीज़ के लिए optimize हो रहा है।
- [पेपर: "Passage Re-ranking with BERT", Nogueira and Cho, 2019](https://arxiv.org/abs/1901.04085)
  Cross-encoder reranking की शुरुआत करता है: query-passage की जोड़ी को embedding दूरी से नहीं बल्कि साथ मिलाकर score करना, इस क़ीमत पर कि हर candidate के लिए model एक बार चलता है। इस्तेमाल: reranking चरण क्यों होता है और वह अकेली embedding similarity के ऊपर क्या देता है।
- [दस्तावेज़: "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
  Keyword-search ranking और vector-search ranking को एक hybrid ranking में मिलाने का मानक तरीक़ा समझाता है, सूत्र और उसके एक tuning parameter के साथ। इस्तेमाल: hybrid search अपनी दोनों rankings को असल में कैसे मिलाता है।
- [दस्तावेज़: "Reranking", Cohere](https://docs.cohere.com/docs/reranking)
  होस्ट किए गए cross-encoder reranker के practitioner-उन्मुख दस्तावेज़: उसे कैसे call करें, latency में उसकी क्या क़ीमत है, और retrieval pipeline में वह कहाँ बैठता है। इस्तेमाल: ऊपर के Nogueira और Cho पेपर के साथ सोचने के लिए एक ठोस, चलाने योग्य reranking चरण।
- [लेख: "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
  मानक retrieval metrics (Recall@k, MRR, nDCG) को क़दम-दर-क़दम समझाता है, और labeled या synthetic query सेट के विरुद्ध हर एक की गणना कैसे करें। इस्तेमाल: यह मापना कि सही चीज़ retrieve हुई या नहीं, इससे पहले कि वह संख्या `llm/evals` को सौंपी जाए कि उसे कैसे परखें।
- [पेपर: "Matryoshka Representation Learning", Kusupati et al., 2022](https://arxiv.org/abs/2205.13147)
  ऐसी embeddings लाता है जो इस तरह train होती हैं कि पूरे vector का कटा हुआ prefix अपने आप में अर्थपूर्ण, इस्तेमाल लायक embedding बना रहता है, जिससे dimensionality को storage और latency के बदले training के बाद भी घटाया-बढ़ाया जा सकता है, सिर्फ़ शुरू में छोटा model चुनकर नहीं। इस्तेमाल: यह समझना कि embedding vector को truncate करना कब सुरक्षित है और कब नहीं।
- [पेपर: "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", Malkov and Yashunin, 2018](https://arxiv.org/abs/1603.09320)
  HNSW के पीछे का पेपर, यानी वह graph-आधारित approximate nearest neighbor index जो pgvector और ज़्यादातर vector databases इस्तेमाल करते हैं: उसकी बहु-परत संरचना और वह recall/latency trade-off जिसे उसका search-depth parameter नियंत्रित करता है। इस्तेमाल: यह समझना कि ANN index सटीक search की जगह असल में क्या करता है, और उसका tuning knob recall के बदले रफ़्तार क्यों देता है।
- [पेपर: "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson and Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
  BM25 का निर्णायक संदर्भ, वह lexical ranking function जो term-frequency, inverse-document-frequency और length-normalization scoring के पीछे है, और उसके हर parameter के पीछे का तर्क। इस्तेमाल: यह समझना कि lexical search असल में क्या score करता है, vector search की semantic similarity के पूरक के रूप में।
- [पेपर: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
  दिखाता है कि models लंबे context की शुरुआत या अंत में रखी जानकारी को बीच में दबी जानकारी से कहीं ज़्यादा भरोसे से इस्तेमाल करते हैं, तब भी जब सब कुछ तकनीकी रूप से context window के भीतर हो। इस्तेमाल: यह समझना कि जोड़े गए prompt में chunk की जगह उतनी ही मायने क्यों रखती है जितना यह कि chunk retrieve हुआ या नहीं, और जो retrieval प्रासंगिक chunks को context के ऊपर के पास रखता है, वह पूरे corpus को दोबारा भेजने से बेहतर क्यों है, जहाँ प्रासंगिक हिस्से बीच में डूब जाते हैं।
- [पेपर: "RAGAS: Automated Evaluation of Retrieval Augmented Generation", Es et al., 2023](https://arxiv.org/abs/2309.15217)
  Faithfulness (यानी generate किया गया दावा retrieved context से असल में समर्थित है या नहीं) को retrieval की गुणवत्ता से अलग metric के रूप में परिभाषित करता है, और बताता है कि हर generate किए उत्तर के लिए नया मानव-labeled ground truth चाहे बिना उसे कैसे जाँचें। इस्तेमाल: retrieval ख़ुद सही पुष्ट हो जाने के बाद यह मूल्यांकन करना कि generation चरण retrieve की गई चीज़ों पर टिका रहा या नहीं।

- [पेपर: "Precise Zero-Shot Dense Retrieval without Relevance Labels" (HyDE), Gao et al., 2022](https://arxiv.org/abs/2212.10496)
  Query की जगह generate किया हुआ काल्पनिक उत्तर embed करने की शुरुआत करता है, जिससे encoder का dense bottleneck काल्पनिक document की तथ्यात्मक ग़लतियाँ छान देता है और उसका असली relevance संकेत बचा रहता है। इस्तेमाल: इसके पीछे की ठीक-ठीक प्रक्रिया कि गढ़ा हुआ, कभी-कभी ग़लत document भी retrieval को बेहतर क्यों करता है।
- [पेपर: "Policy-aware Vector Search: A Vision for Fine Grained Access Control in Vector Databases", Yalamarthi and Pappachan, 2026](https://arxiv.org/abs/2606.19803)
  Vector databases में fine-grained access control को लागू करने की समस्या के रूप में औपचारिक करता है, और सही enforcement, ANN recall और query latency के बीच के अंतर्निहित तनाव को। इस्तेमाल: access control को ख़ास तौर पर pre-filtering क्यों चाहिए, उस ज़्यादा तेज़ पर recall और सुरक्षा को जोखिम में डालने वाली post-filtering की जगह।
- [पेपर: "Docling Technical Report", Auer et al., 2024](https://arxiv.org/abs/2408.09869)
  PDF conversion के लिए layout-analysis (DocLayNet) और table-structure-recognition (TableFormer) pipeline लाता है, उस naive text extraction के विकल्प के रूप में जो layout और table की संरचना को सपाट कर देता है। इस्तेमाल: layout-aware ingestion pipeline असल में क्या पहचानता और दोबारा खड़ा करता है जिसे सादा text extractor फेंक देता है।
- [पेपर: "Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions" (IRCoT), Trivedi et al., 2022](https://arxiv.org/abs/2212.10509)
  ठीक-ठीक बताता है कि single-pass retrieval बहु-चरण वाले सवालों पर क्यों विफल होता है (क्या retrieve करना है यह इस पर निर्भर है कि पहले क्या निकाला जा चुका है), और इसे सुलझाने के लिए reasoning चरण और retrieval चरण को आपस में गूँथता है। इस्तेमाल: उस retrieval loop के पीछे की प्रक्रिया जिसमें बाद की query पिछले hop के उत्तर पर निर्भर होती है।
- [पेपर: "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection", Asai et al., 2023](https://arxiv.org/abs/2310.11511)
  Model को यह तय करना सिखाता है कि retrieval की ज़रूरत है भी या नहीं और retrieve किए passages की आलोचना करना, बजाय हर बार बिना सोचे-समझे तय संख्या में passages retrieve करने के। इस्तेमाल: agentic retrieval का दूसरा आयाम, कि retrieve करना भी है या नहीं, जो इससे अलग है कि बहु-चरण सवाल को कितने hops चाहिए।
- [गाइड: "RAG Observability: How Coralogix Helps You Trace Retrieval-to-Generation Quality", Coralogix, 2026](https://coralogix.com/guides/rag-observability/)
  बताता है कि आम infrastructure monitoring (latency, throughput, error rate) चुप retrieval और context-window विफलताओं के बीच भी हरी क्यों रहती है, और वे reference-free, context-window-utilization और embedding-drift संकेत जो उन्हें पकड़ते हैं। इस्तेमाल: pipeline live होने के बाद असल में क्या monitor करें, पाठ 10 की offline metrics से आगे।

## कमियाँ

- संरचित या code-भारी corpora (गद्य के बजाय) के लिए ख़ास तौर पर semantic chunking पर अभी कोई स्रोत नहीं है, जहाँ fixed-size और paragraph-boundary दोनों heuristics ख़राब चलते हैं; इसे तब भरना ठीक रहेगा जब पाठ डिज़ाइन chunking रणनीति के चुनाव तक पहुँचे।
