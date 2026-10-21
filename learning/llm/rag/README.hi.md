---
title: RAG
description: "Retrieval को अपने हाथ में लें: chunking, embeddings, hybrid search, reranking, और यह मापना कि सही चीज़ retrieve हुई या नहीं"
type: topic
---

# सीखना: RAG

असली corpus और use case के लिए retrieval pipeline डिज़ाइन कर सकें, और जब कोई मौजूदा RAG system ग़लत context लौटाए तो अंदाज़े से सुधार करने के बजाय पता लगा सकें कि ऐसा क्यों हुआ।

**नवीनतम पाठ:** [20. Retrieval Pipeline की समीक्षा](lessons/0020-reviewing-a-retrieval-pipeline.md)

## सफलता कैसी दिखती है

- बताए गए corpus और use case के लिए retrieval pipeline (chunking, embeddings, hybrid search, reranking) डिज़ाइन करें, और हर चुनाव को उसी के सामने सही ठहराएँ।
- जब कोई RAG system ग़लत या अप्रासंगिक context लौटाए, तो बेतरतीब tuning दोबारा करने के बजाय पता लगाएँ कि pipeline का कौन-सा चरण दोषी है।
- Hybrid search के weights को अंदाज़े से नहीं, मापी गई retrieval metric के सामने tune करें।
- Retrieve किए गए context को generate किए गए उत्तर तक ले जाएँ, और बताएँ कि generation चरण ख़ुद अब भी क्या ग़लत कर सकता है।
- किसी और के retrieval pipeline डिज़ाइन की समीक्षा करें, ship होने से पहले ठीक-ठीक बताएँ कि वह क्या ग़लत करेगा, और यह भी बताएँ कि कब बताई गई समस्या का उत्तर RAG ख़ुद (pipeline का कोई चरण नहीं) ही नहीं है।

## सीमाएँ

- बुनियादी Python और embedding क्या होती है इसकी जानकारी मानी गई है; retrieval systems का पूर्व अनुभव ज़रूरी नहीं।
- Vector store: pgvector, ताकि concepts `data/postgres` के उस हिस्से से जुड़ें जो बताता है कि vector index database को क्या पड़ता है।

## दायरे से बाहर

- आम तौर पर prompt-engineering technique और generation की गुणवत्ता: [`llm/prompting`](../../llm/prompting/) देखें। यहाँ उसे सिर्फ़ इस हद तक छुआ गया है कि retrieved context generation चरण तक कैसे पहुँचता है, उसे अलग विषय के रूप में दोहराया नहीं गया।
- Retrieval metric ख़ुद कैसे बनाई और परखी जाती है: [`llm/evals`](../../llm/evals/) देखें, यहाँ दोहराने के बजाय link किया गया है।
- Vector index database को संचालन में क्या पड़ता है: [`data/postgres`](../../data/postgres/) देखें, यहाँ दोहराने के बजाय link किया गया है।

## पूरी रूपरेखा

चौदह चरण, पहले chunk से लेकर diagnose किए गए, लागत-सचेत, monitored production pipeline तक, और अंत में विवेक। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. Chunking | 0001 | पहला pipeline चुनाव, और वह जो हर बाद का चरण विरासत में पाता है | बताए गए corpus को chunk कर सकें और चुनाव को सही ठहरा सकें |
| 2. Embeddings | 0002 से 0003 | Embedding models, similarity metrics, dimensionality के trade-offs | बताए गए corpus के लिए embedding model और metric चुन सकें |
| 3. Vector search और indexing | 0004 से 0005 | ANN indexes (HNSW/IVF), pgvector की ख़ास बातें, recall/latency का trade-off | Chunk किए गए corpus पर pgvector के ऊपर vector search खड़ा कर सकें |
| 4. Hybrid search | 0006 से 0007 | BM25 के साथ vector search, reciprocal rank fusion, मिश्रण को tune करना | मापी गई retrieval metric के सामने hybrid search के weights tune कर सकें |
| 5. Reranking | 0008 से 0009 | Cross-encoder rerankers, reranking की latency क़ीमत कब वसूल होती है | Reranking चरण जोड़ सकें और उसे लागत के सामने सही ठहरा सकें |
| 6. Retrieval का मूल्यांकन और diagnosis | 0010 से 0011 | Recall@k, MRR, यह पता लगाना कि pipeline का कौन-सा चरण दोषी है | ग़लत retrieved context मिलने पर दोषी चरण का नाम बता सकें |
| 7. Retrieval से generation तक | 0012 से 0013 | Retrieved context पर prompt बनाना, context-window budget, generation अब भी क्या ग़लत करता है | Retrieved context को generate किए गए उत्तर तक ले जा सकें और generation चरण की विफलताओं के नाम बता सकें |
| 8. Query-पक्ष का रूपांतरण | 0014 | HyDE, query rewriting, multi-query expansion, query decomposition | ऐसी query-पक्ष की विफलता मिलने पर, जिसे पाठ 11 की प्रक्रिया नहीं पकड़ती, सही उपाय चुन और सही ठहरा सकें |
| 9. Metadata filtering और permission-aware retrieval | 0015 | Metadata filtering, pre- बनाम post-filtering, access control को ख़ास तौर पर pre-filtering क्यों चाहिए | Permission-aware retrieval का रास्ता डिज़ाइन कर सकें और समझा सकें कि उसके लिए post-filtering असुरक्षित क्यों है |
| 10. Ingestion pipeline | 0016 | PDF/HTML/office documents को parse करना, layout-aware बनाम naive extraction, table की संरचना, error cascading | समझा सकें कि ingestion chunking से ऊपर की धारा में क्यों है, और ख़राब parse पाठ 11 के diagnosis से कैसे बच निकलता है |
| 11. Freshness | 0017 | Incremental indexing (HNSW बनाम IVFFlat), delete/update का रखरखाव, model बदलने पर reindexing | corpus और उसके index के पुराने पड़ने के तीन सचमुच अलग तरीक़ों के लिए योजना बना सकें |
| 12. Multi-hop और agentic retrieval | 0018 | IRCoT का आपस में गुँथा reasoning और retrieval, Self-RAG का adaptive retrieval निर्णय | ऐसे सवाल के लिए retrieval loop डिज़ाइन कर सकें जिसे अकेला decomposition नहीं सुलझा सकता |
| 13. Cost, latency और production monitoring | 0019 | पूरे pipeline का latency budget, context window utilization, reference-free scoring, embedding drift | पूरे pipeline का latency budget बना सकें और live होने के बाद बिना ground truth के retrieval की गुणवत्ता monitor कर सकें |
| 14. विवेक | 0020 | Pipeline की समीक्षा, यह तय करना कि long-context के मुक़ाबले RAG कब सही उत्तर है, क्या ग़लत होता है उसका नाम बताना | किसी और के retrieval डिज़ाइन की समीक्षा करने और ठीक-ठीक समझाने के लिए भरोसेमंद कि कोई चुनाव क्यों विफल होगा |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-chunking.md) | Chunking | पहला pipeline चुनाव, और वह जो हर बाद का चरण विरासत में पाता है |
| [0002](lessons/0002-embedding-models-and-similarity.md) | Embedding Models और Similarity | Bi-encoder embedding model असल में क्या करता है, और similarity metric को उसी तरह क्यों मेल खाना चाहिए जैसे model को train किया गया था |
| [0003](lessons/0003-embedding-dimensionality.md) | Embedding Dimensionality के Trade-offs | बड़ा embedding vector मुफ़्त क्यों नहीं है, और छोटा model चुनने के बजाय उसे truncate करना कब सुरक्षित है |
| [0004](lessons/0004-ann-indexes.md) | ANN Indexes: HNSW और IVF | Vector search सटीकता के बदले रफ़्तार क्यों लेता है, और IVF और HNSW हर एक उस trade-off को एक tunable knob के रूप में कैसे सामने रखता है |
| [0005](lessons/0005-pgvector-specifics.md) | pgvector की ख़ास बातें | Postgres में vector search खड़ा करना, और पाठ 4 के index concepts को pgvector के असली operators और parameters पर उतारना |
| [0006](lessons/0006-bm25-and-lexical-search.md) | BM25 और Lexical Search | BM25 असल में क्या score करता है, और exact-term matching अब भी वह क्यों पकड़ लेती है जो semantic embeddings चूक जाती हैं |
| [0007](lessons/0007-reciprocal-rank-fusion.md) | Reciprocal Rank Fusion | Lexical ranking और vector ranking को बेमेल scores की तुलना किए बिना कैसे मिलाएँ, और मिश्रण को मापी गई metric के सामने कैसे tune करें |
| [0008](lessons/0008-cross-encoder-rerankers.md) | Cross-Encoder Rerankers | Cross-encoder वह क्या score करता है जो bi-encoder नहीं कर सकता, और reranking retrieval की जगह लेने के बजाय दूसरा चरण क्यों है |
| [0009](lessons/0009-when-reranking-earns-its-cost.md) | Reranking की क़ीमत कब वसूल होती है | किसी दिए workload के लिए reranking चरण अपनी जोड़ी हुई latency के लायक है या नहीं, यह तय करने का ढाँचा |
| [0010](lessons/0010-recall-at-k-and-mrr.md) | Recall@k और MRR | दो मानक retrieval metrics, हर एक वह क्या बताती है जो दूसरी नहीं बताती, और workload के लिए k कैसे चुनें |
| [0011](lessons/0011-diagnosing-the-pipeline.md) | Pipeline का Diagnosis | चरण-दर-चरण प्रक्रिया यह पता लगाने की कि ग़लत retrieved context के लिए retrieval pipeline का कौन-सा हिस्सा असल में ज़िम्मेदार है |
| [0012](lessons/0012-prompt-construction-and-context-budget.md) | Prompt Construction और Context-Window Budget | Retrieved chunks एक साझा context-window budget के लिए क्यों होड़ करते हैं, और chunk prompt में कहाँ बैठता है यह उतना ही क्यों मायने रखता है जितना यह कि वह retrieve हुआ या नहीं |
| [0013](lessons/0013-what-generation-still-gets-wrong.md) | Generation अब भी क्या ग़लत करता है | वे विफलताएँ जो सही और ठीक जगह रखे retrieved context के बाद भी बचती हैं, और वे retrieval की विफलता से कैसे अलग हैं |
| [0014](lessons/0014-query-side-transformation.md) | Query-Side Transformation | पाठ 11 की diagnosis प्रक्रिया chunking, embedding, index, hybrid weighting और reranking जाँचती है, पर query को कभी नहीं, और जो query बहुत छोटी हो, बहुत मिली-जुली हो, या corpus से बिल्कुल अलग ढंग से लिखी हो, उसे pipeline के किसी और चरण के सुधार की नहीं बल्कि अपने उपाय की ज़रूरत है |
| [0015](lessons/0015-metadata-filtering-and-access-control.md) | Metadata Filtering और Permission-Aware Retrieval | जो access-control filter चूक जाए वह crash नहीं होता और ग़लत भी नहीं दिखता, वह एक बिल्कुल सही बने उत्तर को जन्म देता है जो ऐसे document से बना है जिसे उपयोगकर्ता को कभी देखना ही नहीं था, और इसीलिए इस एक तरह के filter के लिए post-filtering ग़लत चुनाव है |
| [0016](lessons/0016-the-ingestion-pipeline.md) | Ingestion Pipeline | Chunking कभी pipeline का पहला चरण थी ही नहीं, वह बस मान लेती थी कि साफ़ input text पहले से मौजूद है, और chunking से पहले का ख़राब parse उसके बाद की हर चीज़ को बिगाड़ देता है, जबकि बाद के हर diagnostic को वह बिल्कुल अलग विफलता जैसा दिखता है |
| [0017](lessons/0017-freshness.md) | Freshness | लगातार बदलते corpus को एक नहीं बल्कि तीन सचमुच अलग उत्तर चाहिए, क्योंकि document जोड़ना, हटाना और embedding model बदलना, हर एक index की अलग-अलग मान्यता तोड़ता है |
| [0018](lessons/0018-multi-hop-and-agentic-retrieval.md) | Multi-Hop और Agentic Retrieval | Decomposition मिले-जुले सवाल को उन उप-सवालों में बाँटता है जो मूल text में पहले से दिखते हैं, पर कुछ सवालों का दूसरा आधा तभी खुलता है जब पहले आधे का उत्तर लौट आए, जिसके लिए असली loop चाहिए, शुरू में किया गया कोई चतुर बँटवारा नहीं |
| [0019](lessons/0019-cost-latency-and-production-monitoring.md) | Cost, Latency और Production Monitoring | कोई pipeline हर आम infrastructure संकेत पर बिल्कुल स्वस्थ दिख सकता है, जबकि चुपचाप ऐसा आत्मविश्वासी उत्तर दे रहा हो जो ऐसे document पर बना है जो model तक असल में कभी पहुँचा ही नहीं, और retrieval-विशिष्ट monitoring ठीक उसी अंतर को पाटने के लिए है |
| [0020](lessons/0020-reviewing-a-retrieval-pipeline.md) | Retrieval Pipeline की समीक्षा | किसी और के retrieval pipeline डिज़ाइन की समीक्षा करें और ship होने से पहले ठीक-ठीक बताएँ कि वह क्या ग़लत करेगा, और यह भी बताएँ कि कब बताई गई समस्या का उत्तर RAG ख़ुद (pipeline का कोई चरण नहीं) ही नहीं है |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत
- [Chunking और Embeddings](reference/chunking-and-embeddings.md): chunking की रणनीतियाँ, embedding models, similarity metrics, dimensionality के trade-offs
- [Vector Search और Indexing](reference/vector-search-and-indexing.md): ANN indexes (HNSW/IVF), pgvector की ख़ास बातें, recall/latency का trade-off
- [Hybrid Search](reference/hybrid-search.md): BM25 के साथ vector search, reciprocal rank fusion, मिश्रण को tune करना
- [Reranking](reference/reranking.md): cross-encoder rerankers, और reranking की latency क़ीमत कब वसूल होती है
- [Retrieval Evaluation](reference/retrieval-evaluation.md): Recall@k, MRR, और यह पता लगाना कि pipeline का कौन-सा चरण दोषी है
- [Retrieval से Generation](reference/generation-from-retrieval.md): retrieved context पर prompt बनाना, context-window budget, generation चरण की विफलताएँ

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
