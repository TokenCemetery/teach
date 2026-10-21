---
title: "5. pgvector की ख़ास बातें"
description: "Postgres में vector search खड़ा करना, और पाठ 4 के index concepts को pgvector के असली operators और parameters पर उतारना"
type: lesson
---

# पाठ 5. pgvector की ख़ास बातें

**मिशन से संबंध:** यह चरण 3 का समापन है: पाठ 4 के IVF और HNSW concepts यहाँ असली schema, असली distance operator और असली tuning parameters बन जाते हैं, उस vector store पर जिस पर यह workspace मानक के रूप में टिका है।
**मुख्य स्रोत:** [Repo: pgvector, pgvector](https://github.com/pgvector/pgvector)
**पूर्व-आवश्यकताएँ:** [पाठ 4](0004-ann-indexes.md), [Chunk](../GLOSSARY.md)

## वार्म-अप

1. ▢ IVF का `nprobe` parameter और HNSW का `ef_search` parameter, हर एक क्या नियंत्रित करता है?

<details markdown="1"><summary>जाँचें</summary>

`nprobe` तय करता है कि query के समय IVF के कितने clusters में खोजा जाए; `ef_search` तय करता है कि HNSW का graph search हर चरण पर कितने candidates का हिसाब रखे। दोनों recall को latency के सामने तौलते हैं: ऊँचे मान ज़्यादा खोजते हैं, latency की क़ीमत पर recall सुधारते हैं।

</details>

2. ▢ Cosine similarity और dot product एक ही ranking सिर्फ़ तब क्यों देते हैं जब embedding vectors unit length तक normalized हों?

<details markdown="1"><summary>जाँचें</summary>

Dot product वह cosine similarity है जिसे दोनों vectors के magnitudes से scale किया गया हो। जब दोनों unit length पर तय हों, तो वह scaling factor हर जोड़ी के लिए एक-सा रहता है, इसलिए rankings मेल खाती हैं; जब magnitudes बदलते हों, तो dot product बड़े vectors को तरजीह देता है।

</details>

## यह जानें

### Vector column और distance operator

pgvector Postgres में `vector(N)` column प्रकार जोड़ता है, जिसका आकार उस embedding dimensionality से मेल खाता है जो पाठ 3 में तय हुई:

```sql
CREATE EXTENSION vector;
CREATE TABLE chunks (id bigserial PRIMARY KEY, content text, embedding vector(1536));
```

Similarity तीन operators में से एक से निकलती है: `<->` (Euclidean/L2 distance), `<#>` (negative inner product), और `<=>` (cosine distance)। Operator उस metric से मेल खाना चाहिए जिसके लिए embedding model को train किया गया था (पाठ 2): raw dot product के लिए train हुए model के विरुद्ध `<=>` इस्तेमाल करना, या उलटा, ठीक वही बेमेल है जिसके बारे में पाठ 2 ने चेताया था कि ranking की गुणवत्ता गिराता है, अब किसी अमूर्त चुनाव की जगह ठोस SQL चुनाव के रूप में। `<#>` पर चिह्न पर ध्यान दें: यह ख़ास तौर पर negative inner product इसलिए है कि, बाक़ी दो operators की तरह, छोटे का मतलब ज़्यादा मिलता-जुलता हो, ताकि तीनों के लिए `ORDER BY` का ascending क्रम एक-सा रहे।

### Index किसी एक ख़ास distance function के लिए बनाना पड़ता है

Index बनाने का मतलब है ऐसा operator class चुनना जो इच्छित distance function से मेल खाए:

```sql
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
```

`vector_cosine_ops`, `vector_l2_ops` और `vector_ip_ops` हर एक index को एक ख़ास operator के लिए बनाता है। `vector_l2_ops` से बना index `<=>` (cosine distance) से क्रम देने वाली query को तेज़ नहीं करता; operator class और query का operator मेल खाने चाहिए, वरना index इस्तेमाल ही नहीं होता और query चुपचाप पूरे sequential scan पर लौट जाती है, जो index बनाने का पूरा मक़सद ही बेकार कर देता है।

### pgvector के parameter नाम पाठ 4 के ही parameters हैं, अलग नामों से

HNSW के index-build parameters, `m` (हर node के अधिकतम कनेक्शन) और `ef_construction` (build-समय की search गहराई), ठीक पाठ 4 के HNSW tuning knobs हैं, जो `CREATE INDEX` के समय तय होते हैं। उसका query-time recall/latency knob एक session setting है: `SET hnsw.ef_search = 100;`, पाठ 4 का `ef_search` दूसरे नाम से। IVFFlat का build parameter `lists` है (वही cluster गिनती जिसकी पाठ 4 ने चर्चा की), जो index बनाते समय उसी तरह तय होता है, और उसका query-time knob `SET ivfflat.probes = 10;` है, पाठ 4 का `nprobe`।

### IVFFlat को अच्छी तरह बनने के लिए data चाहिए; HNSW को नहीं

IVFFlat के clustering चरण को अपने cluster centroids ठीक से रखने के लिए table के असली vectors का प्रतिनिधि नमूना चाहिए, यानी खाली या मुश्किल से भरी table पर IVFFlat index बनाने से ख़राब clusters बनते हैं जो corpus के असली vector वितरण को नहीं दर्शाते। व्यावहारिक नतीजा: पहले data load करें, फिर IVFFlat index बनाएँ। HNSW का graph vectors insert होते-होते क्रमशः बनता है, table के पहले से भरे होने पर उसकी ऐसी कोई निर्भरता नहीं, जो इसका एक कारण है कि समय के साथ बढ़ने वाली table के लिए HNSW को अक्सर पसंद किया जाता है, उस recall/latency लाभ के ऊपर जिसका वर्णन पाठ 4 पहले ही कर चुका है।

## अभ्यास

1. ▢ Embedding model इस तरह train हुआ कि cosine similarity semantic निकटता दर्शाती है। Query और उसके index, दोनों को कौन-सा pgvector operator और operator class इस्तेमाल करना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

Query के लिए `<=>` operator (cosine distance), और index के लिए `vector_cosine_ops`। ऐसा operator या operator class इस्तेमाल करना जो model के train होने वाले distance function से अलग function के लिए बना हो, पाठ 2 की metric-बेमेल की समस्या को लौटा लाता है, अब ठोस SQL बेमेल के रूप में।

</details>

2. ▢ एक टीम `vector_l2_ops` के साथ HNSW index बनाती है, पर उनकी queries नतीजों को `<=>` operator (cosine distance) से क्रम देती हैं। क्या होता है, और यह सिर्फ़ "ग़लत उत्तर" से आगे की समस्या क्यों है?

<details markdown="1"><summary>संकेत</summary>

सोचें कि जिस query का operator index के बनाए operator class से मेल न खाए, उसके लिए index इस्तेमाल हो भी सकता है या नहीं।

</details>

<details markdown="1"><summary>जाँचें</summary>

`vector_l2_ops` के लिए बना index `<=>` इस्तेमाल करने वाली query को तेज़ नहीं करता, क्योंकि index एक ख़ास distance function के लिए बना है। Query table पर पूरे sequential scan पर लौट जाती है, जो किसी भी असली corpus आकार पर धीमा है; यह सिर्फ़ ग़लत उत्तर का जोखिम नहीं है, यह वह पूरा प्रदर्शन-लाभ खो देना है जो index देने के लिए था।

</details>

3. ▢ किसी table में `lists = 1000` वाला IVFFlat index है, पर query-time setting `ivfflat.probes` अपने default 1 पर छोड़ दी गई है। पाठ 4 के `nprobe` के संदर्भ में, इसका recall/latency trade-off के लिए क्या मतलब है?

<details markdown="1"><summary>जाँचें</summary>

`ivfflat.probes = 1` का मतलब `nprobe = 1` है: 1,000 clusters में से सिर्फ़ एक सबसे नज़दीकी में खोजा जाता है। यह पाठ 4 के trade-off का सबसे तेज़, सबसे कम recall वाला छोर है; cluster की सीमा के पास की query पड़ोसी cluster में बैठे असली nearest neighbors को चूक सकती है। `probes` बढ़ाने से ज़्यादा clusters में खोजा जाता है, query latency के बदले ऊँची recall मिलती है।

</details>

4. ▢ IVFFlat index के लिए build का क्रम क्यों मायने रखता है (data load करें, फिर बनाएँ) पर HNSW के लिए नहीं?

<details markdown="1"><summary>जाँचें</summary>

IVFFlat के clustering चरण को अपने cluster centroids ठीक से रखने के लिए table के असली vectors का प्रतिनिधि नमूना चाहिए; खाली या कम भरी table पर उसे बनाने से ख़राब clusters बनते हैं जो असली data वितरण को नहीं दर्शाते। HNSW का graph vectors insert होते-होते क्रमशः बनता है, और table में पहले से प्रतिनिधि नमूना होने की उसकी ऐसी कोई ज़रूरत नहीं।

</details>

5. ▢ pgvector के operator classes (`vector_cosine_ops`, `vector_l2_ops`, `vector_ip_ops`) के बारे में कौन-सा दावा सही है?

    - a) कोई भी operator class किसी भी query operator के साथ चलता है, क्योंकि pgvector distance functions के बीच अपने-आप बदल देता है
    - b) Index का operator class query के distance operator से मेल खाना चाहिए, वरना उस query के लिए index इस्तेमाल नहीं होगा
    - c) Operator class सिर्फ़ HNSW indexes को प्रभावित करता है, IVFFlat को नहीं
    - d) `vector_ip_ops` normalized embedding vectors के साथ इस्तेमाल नहीं हो सकता

<details markdown="1"><summary>जाँचें</summary>

**b)** Operator class और query का operator मेल खाने चाहिए, वरना query index इस्तेमाल करने की जगह sequential scan पर लौट जाती है। (a) ग़लत है: distance functions के बीच कोई स्वचालित बदलाव नहीं है। (c) ग़लत है: दोनों index प्रकारों में operator class को distance function से मिलाना ज़रूरी है। (d) ग़लत है: normalized vectors ठीक वह स्थिति हैं जहाँ inner product और cosine distance मेल खाते हैं, जैसा पाठ 2 में आया।

</details>

## असली दुनिया का अभ्यास

- [ ] अपने इस्तेमाल के किसी embedding model के आकार का `vector(N)` column रखने वाली छोटी pgvector table बनाएँ, और उस model की train हुई similarity metric से मेल खाने वाले operator class के साथ index बनाएँ।
- [ ] अपनी table पर similarity query पर `EXPLAIN` चलाएँ और पुष्टि करें कि index असल में इस्तेमाल हो रहा है, sequential scan पर नहीं लौट रहा।
- [ ] कल: उसी query पर `ivfflat.probes` या `hnsw.ef_search` के दो अलग मान आज़माएँ और लौटे नतीजों और query latency, दोनों की तुलना करें।

## आगे बढ़ने के लिए

- [Repo: pgvector, pgvector](https://github.com/pgvector/pgvector)
- [पेपर: "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", Malkov and Yashunin, 2018](https://arxiv.org/abs/1603.09320)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
