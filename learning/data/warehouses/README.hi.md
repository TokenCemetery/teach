---
title: Warehouses
description: "Analytical warehouse के मालिक बनें: columnar storage और execution, compute से अलग storage, और row store की performance सलाह यहाँ क्यों लागू नहीं होती"
type: topic
---

# सीखना: Analytical Warehouses

BigQuery, Snowflake या Redshift पर ऐसी table, model और load path डिज़ाइन कर सकें जो उनसे पूछे गए analytical सवालों का जवाब ऐसी लागत पर दें जिसका आप अनुमान लगा सकें, और storage layout से बता सकें कि जो सलाह row store पर सही थी वह वहाँ ग़लत क्यों है।

**नवीनतम पाठ:** [20. ऐसा Model बदलना जिसे दूसरे Query करते हैं](lessons/0020-changing-a-model-others-query.md)

## सफलता कैसी दिखती है

- Storage layout से समझाएँ कि कोई query row store पर सस्ती और columnar warehouse पर महँगी क्यों है, या उल्टा, और अनुमान लगाएँ कि query में बदलाव उसके scan किए bytes पर क्या असर डालता है।
- बताएँ कि BigQuery, Snowflake और Redshift में से हर एक storage और compute के बीच क्या अलग करता है, और बताए गए workload के लिए compute का size तय करें या उसे isolate करें।
- किसी table के query pattern से उसके लिए partitioning, clustering या sort keys और distribution चुनें, और दिखाएँ कि उस चुनाव से कितना scan बचता है।
- बताए गए grain पर dimensional model डिज़ाइन करें, इसमें यह भी कि बदलने वाला dimension अपना इतिहास कैसे रखता है।
- Batch या micro-batch load path डिज़ाइन करें जिसे rows duplicate किए या खोए बिना दोबारा चलाया जा सके।
- On-demand और capacity pricing के तहत किसी query या workload की लागत का अनुमान लगाएँ, और जवाब बदले बिना उस लागत को घटाएँ।
- किसी workload के लिए warehouse, Postgres और lakehouse के बीच फ़ैसला करें, किसी और के warehouse schema और bill की समीक्षा करें, और ऐसा model बदलें जिसे दूसरे query करते हैं, उनका कुछ तोड़े बिना।

## सीमाएँ

- काम चलाने लायक़ SQL माना गया है, warehouse का कोई पूर्व अनुभव नहीं। भाषा, query plans और transactional schema design [`programming/sql`](../../programming/sql/) में सिखाए जाते हैं, और ये पाठ उन्हें पहले से मानकर चलते हैं।
- BigQuery, Snowflake और Redshift वे तीन platforms हैं जिनकी तुलना पूरे track में होती है। हर पाठ पहले mechanism सिखाता है और फिर बताता है कि हर platform उसे कैसे उपलब्ध कराता है, ताकि vendor बदलने पर भी सामग्री काम की रहे।
- Platform के defaults, limits और prices releases के बीच बदलते रहते हैं। जहाँ कोई पाठ इनमें से किसी को उद्धृत करता है, वहाँ वह उस documentation page का नाम देता है जहाँ से वह लिया गया, और पाठक को मौजूदा मान के लिए वही page देखना चाहिए।

## दायरे से बाहर

- SQL भाषा, query plans, schema design और row store पर isolation: [`programming/sql`](../../programming/sql/) देखें, जिस पर यह track दोहराने के बजाय आगे बनता है।
- Postgres instance चलाना: [`data/postgres`](../../data/postgres/) देखें। चरण 8 analytical workload के उम्मीदवार के रूप में Postgres की तुलना करता है; उसे चलाना नहीं सिखाता।
- Streaming platforms अपने-आप में विषय के रूप में। चरण 6 stream से load करता है; log ख़ुद कैसे काम करता है, यह [`data/kafka`](../../data/kafka/) में है।
- Orchestration और transformation frameworks (Airflow, dbt) अपने-आप में विषय के रूप में। वे वहाँ आते हैं जहाँ loading या modelling के किसी पाठ को उनकी ज़रूरत होती है, और उन्हें configure करना नहीं सिखाया जाता।
- BI tools, semantic layers और dashboard design।
- Spark, Trino और दूसरे engines अपने-आप में विषय के रूप में। चरण 8 उनके query किए जाने वाले lakehouse को warehouse के सामने रखता है; उन्हें चलाना नहीं सिखाता।

## पूरी रूपरेखा

आठ चरण, storage layout से लेकर विवेक तक। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. Row और column storage | 0001 से 0002 | OLTP और OLAP access patterns, row stores बनाम column stores, row groups, column chunks और उनके statistics | बता सकें कि बताई गई query के लिए कौन-सा layout कम bytes पढ़ता है, और क्यों |
| 2. Columnar execution | 0003 से 0004 | Dictionary, run-length और delta encoding, compression, vectorized execution, late materialization | बता सकें कि column store वैसे compress और execute क्यों करता है जैसे करता है, और वहाँ `SELECT *` की क़ीमत क्या है |
| 3. Storage और compute | 0005 से 0006 | BigQuery, Snowflake और Redshift storage को compute से कैसे अलग करते हैं, slots, virtual warehouses, node types, concurrency और workload isolation | तीनों में से किसी पर भी बताए गए workload के लिए compute का size तय कर सकें और उसे isolate कर सकें |
| 4. Physical design | 0007 से 0010 | Partitioning और pruning, clustering और sort keys, zone maps, distribution और join strategy, row store की वह सलाह जो लागू नहीं रहती | Table के query pattern से उसका physical layout चुन सकें और दिखा सकें कि उससे कितना scan बचता है |
| 5. Dimensional modelling | 0011 से 0013 | Facts, dimensions और grain, star schemas बनाम wide और nested tables, slowly changing dimensions | बताए गए grain पर ऐसा model डिज़ाइन कर सकें जो सवाल के लिए ज़रूरी इतिहास रखे |
| 6. Loading | 0014 से 0015 | ELT बनाम ETL, batch loading और file sizing, micro-batch और streaming ingestion, idempotent merges | ऐसा load path डिज़ाइन कर सकें जिसे rows duplicate किए या खोए बिना दोबारा चलाया जा सके |
| 7. Cost | 0016 से 0017 | हर platform पर on-demand और capacity pricing, query की लागत पढ़ना, caches, materialized views और bill पर सीमा लगाने वाले controls | Workload की लागत का अनुमान लगा सकें और जवाब बदले बिना उसे घटा सकें |
| 8. विवेक | 0018 से 0020 | Warehouse बनाम Postgres बनाम lakehouse, schema और उसके bill की समीक्षा, ऐसा model बदलना जिसे दूसरे query करते हैं, platform के documentation से विवाद सुलझाना | फ़ैसला लेने और उसे किसी और को समझाने के लिए भरोसेमंद |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-row-stores-and-column-stores.md) | Row Stores और Column Stores | कोई analytical query column store से उतने bytes का छोटा-सा हिस्सा ही क्यों पढ़ती है जितने वह row store से पढ़ती है, और एक row का lookup उल्टी दिशा में क्यों जाता है |
| [0002](lessons/0002-inside-a-columnar-file.md) | Columnar File के अंदर | Row groups, column chunks और हर chunk के statistics reader को ऐसा data छोड़ने कैसे देते हैं जिसे वह कभी decompress ही नहीं करता |
| [0003](lessons/0003-encoding-and-compression.md) | Encoding और Compression | एक type का एक column किसी row से कहीं बेहतर compress क्यों होता है, और कौन-सी encoding data के किस रूप के लिए ठीक है |
| [0004](lessons/0004-vectorized-execution-and-late-materialization.md) | Vectorized Execution और Late Materialization | Column engine हर call में values का एक batch कैसे process करता है और rows सिर्फ़ उन values के लिए जोड़ता है जो बच जाती हैं |
| [0005](lessons/0005-separating-storage-from-compute.md) | Storage को Compute से अलग करना | BigQuery, Snowflake और Redshift में से हर एक data के रहने की जगह और उसे पढ़ने वाली चीज़ के बीच क्या अलग रखता है, और इससे क्या मिलता है और क्या क़ीमत चुकानी पड़ती है |
| [0006](lessons/0006-compute-sizing-concurrency-and-isolation.md) | Compute Sizing, Concurrency और Workload Isolation | किसी workload के लिए compute का size कैसे तय करें, और एक team की queries को दूसरी team की queries के पीछे queue में लगने से कैसे रोकें |
| [0007](lessons/0007-partitioning-and-pruning.md) | Partitioning और Pruning | Partitioned table filter को पूरे partitions छोड़ने कैसे देती है, और वे filters जो चुपचाप सब कुछ scan कर लेते हैं |
| [0008](lessons/0008-clustering-and-sort-keys.md) | Clustering और Sort Keys | Storage के अंदर data को क्रम में रखना हर block के min और max को कैसे कसता है ताकि filter ज़्यादा blocks छोड़ सके |
| [0009](lessons/0009-joins-and-data-distribution.md) | Joins और Data Distribution | Distributed warehouse rows को join करने के लिए उन्हें कैसे move करता है, और distribution का चुनाव कैसे तय करता है कि उसे ऐसा करना पड़ेगा या नहीं |
| [0010](lessons/0010-the-row-store-advice-that-stops-applying.md) | Row Store की वह सलाह जो लागू नहीं रहती | Row store को index और normalize करने की कौन-सी आदतें columnar warehouse पर ग़लत हैं, और कौन-सी अब भी सही हैं |
| [0011](lessons/0011-facts-dimensions-and-the-grain.md) | Facts, Dimensions और Grain | कोई भी column चुनने से पहले यह कैसे घोषित करें कि fact table की एक row का मतलब क्या है |
| [0012](lessons/0012-star-schemas-wide-tables-and-nesting.md) | Star Schemas, Wide Tables और Nesting | Dimensions को कब उनकी अपनी tables में रखें, कब उन्हें एक wide table में flatten करें, और कब उन्हें nest करें |
| [0013](lessons/0013-slowly-changing-dimensions.md) | Slowly Changing Dimensions | कोई attribute बदलने पर dimension अपना इतिहास कैसे रखता या छोड़ता है, और हर चुनाव पुरानी reports पर क्या असर डालता है |
| [0014](lessons/0014-elt-and-batch-loading.md) | ELT और Batch Loading | Warehouses पहले raw data load करके उसे वहीं transform क्यों करते हैं, और files की गिनती और size load की रफ़्तार कैसे तय करते हैं |
| [0015](lessons/0015-micro-batch-streaming-and-idempotent-merges.md) | Micro-Batch, Streaming और Idempotent Merges | Data को लगातार कैसे उतारें, और किसी भी load को दोबारा चलाने पर table ठीक वैसी ही कैसे रहे जैसी एक बार चलाने पर रहती |
| [0016](lessons/0016-how-a-warehouse-bills.md) | Warehouse Bill कैसे करता है | On-demand और capacity pricing के तहत हर platform किस चीज़ के पैसे लेता है, और हर model किस workload को फ़ायदा देता है |
| [0017](lessons/0017-reading-and-cutting-a-querys-cost.md) | Query की लागत पढ़ना और घटाना | Query चलाने से पहले कैसे पता करें कि उसकी लागत क्या होगी, और वे बदलाव जो उसका जवाब बदले बिना लागत घटाते हैं |
| [0018](lessons/0018-warehouse-postgres-or-lakehouse.md) | Warehouse, Postgres या Lakehouse | कैसे तय करें कि कोई analytical workload कहाँ होना चाहिए, और कब warehouse वाला आम जवाब ग़लत होता है |
| [0019](lessons/0019-reviewing-a-warehouse-schema-and-its-bill.md) | Warehouse Schema और उसके Bill की समीक्षा | किसी और के warehouse design की समीक्षा कैसे करें और हर चुनाव की क़ीमत bytes और पैसों में कैसे बताएँ |
| [0020](lessons/0020-changing-a-model-others-query.md) | ऐसा Model बदलना जिसे दूसरे Query करते हैं | जिस table पर dashboards और pipelines निर्भर हैं उसे उन्हें तोड़े बिना कैसे बदलें, और documentation से विवादित दावे को कैसे सुलझाएँ |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत, हर एक के साथ टिप्पणी कि वह क्या कवर करता है
- [Columnar Storage और Execution](reference/columnar-storage-and-execution.md): row बनाम column layout, encodings, और column engine क्या छोड़ देता है
- [Platforms की तुलना](reference/platforms-compared.md): BigQuery, Snowflake और Redshift storage और compute के एक जैसे विचारों को क्या नाम देते हैं और उनका bill कैसे बनाते हैं
- [Physical Design](reference/physical-design.md): हर platform पर partitioning, clustering, sort keys और distribution, और row store की वे आदतें जिन्हें छोड़ना है
- [Dimensional Modelling](reference/dimensional-modelling.md): design के चार क़दम, schema के रूप, और slowly changing dimension के types
- [Loading](reference/loading.md): हर platform के load methods, file sizing, और वे patterns जो load को दोबारा चलाना सुरक्षित बनाते हैं
- [Cost Model](reference/cost-model.md): हर pricing model किस चीज़ के पैसे लेता है, query की लागत कैसे पढ़ें, और bill पर सीमा लगाने वाले controls
- [Schema और Bill Review](reference/schema-and-bill-review.md): warehouse design और उसके bill की समीक्षा के लिए checklist, और placement का फ़ैसला

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
