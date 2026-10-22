---
title: "Vector Search और Indexing"
description: "IVF और HNSW का recall/latency trade-off, और pgvector के operators, index parameters और build-क्रम की ख़ास बातें"
type: reference
---

# Vector Search और Indexing

Approximate nearest neighbor search और उसका pgvector implementation। Index खड़ा या tune करते समय खोजने के लिए बनाया गया।

## सटीक search scale क्यों नहीं करता

सटीक nearest-neighbor search query की तुलना हर vector से करता है: corpus के आकार के साथ रैखिक, लाखों chunks पर बहुत धीमा। **Approximate nearest neighbor (ANN)** index थोड़ी, नियंत्रित अशुद्धता स्वीकार करता है, ऐसे search समय के बदले जो रैखिक रूप से नहीं बढ़ते।

## IVF और HNSW

| Index | तंत्र | Search-time knob | Build लागत |
|---|---|---|---|
| IVF (inverted file) | Vectors को पहले से clusters में बाँटता है (k-means); सिर्फ़ `nprobe` सबसे नज़दीकी clusters में खोजता है | `nprobe`: कम = तेज़, cluster सीमा के पास के neighbors चूक सकता है; ज़्यादा = सटीक search के क़रीब पहुँचता है | Centroids ठीक से रखने के लिए corpus का प्रतिनिधि नमूना चाहिए |
| HNSW (hierarchical navigable small world) | बहु-परत graph; लंबी छलाँगों के लिए विरल ऊपरी परतें, सटीक स्थानीय search के लिए घनी निचली परत, लालच से नीचे उतरता है | `ef_search`: हर चरण पर कितने candidates का हिसाब रखा जाए; कम = तेज़ पर स्थानीय रूप से अच्छे node पर टिक सकता है; ज़्यादा = ज़्यादा recall | IVF से ज़्यादा memory (graph के edges) और धीमा index build |

दोनों knobs किसी दिए corpus के लिए **recall/latency वक्र** पर एक बिंदु तय करते हैं; किसी की भी कोई एक सार्वभौमिक रूप से सही setting नहीं है। HNSW आम तौर पर उस वक्र पर IVF से बेहतर बिंदु पर पहुँचता है (उतनी ही latency पर ज़्यादा recall), memory और build समय की क़ीमत पर। सही बिंदु workload के latency budget पर निर्भर करता है और इस पर कि कोई बाद का चरण (reranking) कितनी recall हानि सोख सकता है, मापकर, मानकर नहीं।

## pgvector: column, operator, index

```sql
CREATE EXTENSION vector;
CREATE TABLE chunks (id bigserial PRIMARY KEY, content text, embedding vector(1536));
```

| Operator | Distance | Operator class (indexing के लिए) |
|---|---|---|
| `<->` | Euclidean/L2 | `vector_l2_ops` |
| `<#>` | Negative inner product | `vector_ip_ops` |
| `<=>` | Cosine | `vector_cosine_ops` |

`<#>` ख़ास तौर पर *negative* inner product इसलिए है कि, बाक़ी दो की तरह, छोटे का मतलब ज़्यादा मिलता-जुलता हो, ताकि तीनों के लिए `ORDER BY` का ascending क्रम एक-सा रहे। Operator को [उस metric से मेल खाना चाहिए जिसके लिए embedding model train हुआ था](chunking-and-embeddings.md#similarity-metrics-must-match-training): dot-product के लिए train हुए model के विरुद्ध `<=>` इस्तेमाल करना (या उलटा) वही metric बेमेल है, अब ठोस SQL चुनाव के रूप में।

```sql
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
```

**Index एक ख़ास distance function के लिए बनता है।** जो query ऐसे operator से क्रम देती है जो index के operator class से मेल नहीं खाता, वह उस index को बिल्कुल इस्तेमाल नहीं करती: वह चुपचाप पूरे sequential scan पर लौट जाती है, और index जो पूरा प्रदर्शन-लाभ देने के लिए था वह खो देती है। Distance functions के बीच कोई स्वचालित बदलाव नहीं है।

## pgvector के parameters पाठ 4 के ही हैं, नए नामों से

| अवधारणा | HNSW | IVFFlat |
|---|---|---|
| Build-time parameter | `m` (हर node के अधिकतम कनेक्शन), `ef_construction` (build-समय की search गहराई), `CREATE INDEX` पर तय | `lists` (cluster गिनती), `CREATE INDEX` पर तय |
| Query-time recall/latency knob | `SET hnsw.ef_search = 100;` | `SET ivfflat.probes = 10;` (यही `nprobe` है) |

## Build का क्रम IVFFlat के लिए मायने रखता है, HNSW के लिए नहीं

IVFFlat के clustering चरण को centroids ठीक से रखने के लिए table के असली vectors का प्रतिनिधि नमूना चाहिए: खाली या कम भरी table पर उसे बनाने से ख़राब clusters बनते हैं। पहले data load करें, फिर IVFFlat index बनाएँ। HNSW का graph vectors insert होते-होते क्रमशः बनता है, ऐसी किसी निर्भरता के बिना, जो एक कारण है कि समय के साथ बढ़ने वाली table के लिए HNSW को अक्सर पसंद किया जाता है।

## संबंधित

- [पाठ 4](../lessons/0004-ann-indexes.md), [पाठ 5](../lessons/0005-pgvector-specifics.md)
- [Chunking और Embeddings](chunking-and-embeddings.md): वे vectors और similarity metric जिनसे इस sheet के index को मेल खाना है
