---
title: Stream Processing
description: "Kafka Streams के साथ stream पर computation करें: topologies, state, windows और joins, और production तक पहुँचने से पहले किसी topology की क़ीमत क्या है"
type: topic
---

# सीखना: Stream Processing

ऐसी Kafka Streams application बना, test कर और चला सकें जो records के देर से, क्रम से बाहर या दो बार आने पर भी सही जवाब दे, और उसकी topology से बता सकें कि production तक पहुँचने से पहले वह कितने internal topics, कितना state और कितना recovery time लेगी।

**नवीनतम पाठ:** [20. ऐसी Topology बदलना जिस पर दूसरे निर्भर हैं](lessons/0020-changing-a-topology-others-depend-on.md)

## सफलता कैसी दिखती है

- Stream-table duality से समझाएँ कि topic, changelog और KTable आपस में कैसे जुड़े हैं, और अनुमान लगाएँ कि बताए गए input के लिए कोई topology क्या emit करती है।
- DSL से topology बनाएँ, उसका `describe()` output पढ़ें, और उसके बनाए हर internal topic का नाम बताएँ, साथ में यह भी कि वह क्यों बना।
- किसी stateful operation के लिए state store चुनें, और बताएँ कि उसे रखने वाला instance मर जाए तो उसका state दोबारा कैसे बनता है।
- समय पर आधारित सवाल के लिए window और grace period चुनें, और बताएँ कि वह कौन-से late records छोड़ देता है और result कब emit करता है।
- दो inputs के लिए join चुनें, उन्हें co-partitioned बनाएँ या बताएँ कि GlobalKTable से इसकी ज़रूरत क्यों नहीं रहती, और join के output का अनुमान लगाएँ।
- बताएँ कि `exactly_once_v2` क्या गारंटी देता है और क्या छोड़ देता है, और बताए गए recovery time के लिए application के tasks, threads, instances और standby replicas का size तय करें।
- `TopologyTestDriver` से topology को test करें, और चल रही application को उसके metrics, states और exception handlers के सहारे चलाएँ।
- किसी workload के लिए Kafka Streams, साधारण consumer, Flink और ksqlDB के बीच फ़ैसला करें, किसी और की topology की समीक्षा करें, और चल रही topology को उसका state या उसके downstream consumers तोड़े बिना बदलें।

## सीमाएँ

- काम चलाने लायक़ Java और वह log माना गया है जैसा [`data/kafka`](../../data/kafka/) सिखाता है: partitions, consumer groups, delivery guarantees, retention और compaction। ये पाठ इनमें से कुछ भी फिर से निकालने के बजाय वहाँ वापस link करते हैं।
- Kafka Streams ही एकमात्र engine है जो सिखाया जाता है। Examples Apache Kafka 4.3 के Java DSL और Processor API का इस्तेमाल करते हैं।
- Defaults और protocols releases के बीच बदलते रहते हैं। जहाँ कोई पाठ इनमें से किसी को उद्धृत करता है, वहाँ वह उस documentation page या KIP का नाम देता है जहाँ से वह लिया गया, और पाठक को मौजूदा मान के लिए वही page देखना चाहिए।

## दायरे से बाहर

- Log ख़ुद: partitions, consumer groups, delivery semantics, transactions की क़ीमत, retention और compaction, Kafka Connect और Schema Registry। [`data/kafka`](../../data/kafka/) देखें, जिस पर यह track आगे बनता है।
- Partial failure और consistency सिद्धांत के रूप में: [`architecture/distributed-systems`](../../architecture/distributed-systems/) देखें। यह track सिर्फ़ यह सिखाता है कि state-store recovery और rebalancing किसी Streams app के लिए क्या बदलते हैं।
- Apache Flink, Spark Structured Streaming और ksqlDB अपने-आप में विषय के रूप में। चरण 8 किसी workload के उम्मीदवारों के रूप में उनकी तुलना Kafka Streams से करता है; उन्हें चलाना नहीं सिखाता।
- Java भाषा: [`programming/java`](../../programming/java/) देखें।
- किसी stream को analytical warehouse में load करना: [`data/warehouses`](../../data/warehouses/) देखें।

## पूरी रूपरेखा

आठ चरण, stream-table duality से लेकर विवेक तक। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. Streams और tables | 0001 से 0002 | Stream-table duality, tables के रूप में compacted topics, Streams app क्या चलाता है और कहाँ | बता सकें कि कोई topic stream के रूप में पढ़ा जाता है या table के रूप में, और Streams app किसी consumer में क्या जोड़ता है |
| 2. Topologies | 0003 से 0004 | DSL, sources, processors और sinks, `describe()`, Serdes, stateless operations, key changes और repartition topics | Topology पढ़ सकें और उसके बनाए हर internal topic का नाम बता सकें |
| 3. State | 0005 से 0007 | State stores, changelog topics, aggregations, KTable updates, record cache, Processor API और punctuators | किसी stateful step के लिए store चुन सकें और बता सकें कि instance के मरने पर उसका state कैसे बचा रहता है |
| 4. Time और windows | 0008 से 0010 | Event time, processing time और stream time, timestamp extractors, tumbling, hopping, sliding और session windows, grace periods, suppression | किसी सवाल के लिए window और grace period चुन सकें और बता सकें कि वह कौन-से records छोड़ देता है |
| 5. Joins | 0011 से 0012 | Stream-table और GlobalKTable joins, co-partitioning, windowed stream-stream joins, table-table और foreign-key joins | दो inputs के लिए join चुन सकें और अनुमान लगा सकें कि वह क्या emit करता है |
| 6. Guarantees और scaling | 0013 से 0015 | `exactly_once_v2`, tasks, threads और instances, rebalancing, state restoration, standby और warmup replicas, streams rebalance protocol | बता सकें कि exactly-once क्या कवर करता है और बताए गए recovery time के लिए app का size तय कर सकें |
| 7. Testing और operating | 0016 से 0017 | `TopologyTestDriver`, metrics, client और thread states, exception handlers, interactive queries, operator tools | Broker के बिना topology को test कर सकें और metrics से बता सकें कि चल रहा app ठीक है या नहीं |
| 8. विवेक | 0018 से 0020 | Streams बनाम साधारण consumer, Flink और ksqlDB, topology की समीक्षा, ऐसी topology बदलना जिस पर दूसरे निर्भर हैं, source से विवाद सुलझाना | फ़ैसला लेने और उसे किसी और को समझाने के लिए भरोसेमंद |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-streams-and-tables.md) | Streams और Tables | बदलावों का stream और मौजूदा values की table एक ही data के दो रूप क्यों हैं, और topic इनमें से किसी को भी कैसे रखता है |
| [0002](lessons/0002-a-streams-app-is-a-library.md) | Streams App एक Library है | Kafka Streams application शुरू होने पर क्या चलता है: आपकी अपनी process के भीतर consumers, producers और local state, बिना किसी अपने cluster के |
| [0003](lessons/0003-the-dsl-and-topologies.md) | DSL और Topologies | DSL calls sources, processors और sinks की topology कैसे बनाती हैं, और `describe()` से उसे कैसे पढ़ें |
| [0004](lessons/0004-stateless-operations-and-repartitioning.md) | Stateless Operations और Repartitioning | कौन-से operations एक बार में एक record बदलते हैं, और कौन-सा key change अगले stateful step से repartition topic लिखवाता है |
| [0005](lessons/0005-state-stores-and-changelog-topics.md) | State Stores और Changelog Topics | कोई stateful operation अपना state कहाँ रखता है, और compacted changelog topic से कोई दूसरा instance उसे दोबारा कैसे बना पाता है |
| [0006](lessons/0006-aggregations-ktables-and-the-record-cache.md) | Aggregations, KTables और Record Cache | KTable अंतिम जवाबों के बजाय updates का stream क्यों emit करती है, और record cache और commit interval कैसे तय करते हैं कि कितने |
| [0007](lessons/0007-the-processor-api.md) | Processor API | DSL से नीचे उतरकर अपने store और punctuator वाले custom processor तक कब जाएँ, और तब किस चीज़ की ज़िम्मेदारी आपकी होती है |
| [0008](lessons/0008-event-time-processing-time-and-stream-time.md) | Event Time, Processing Time और Stream Time | कोई Streams operation किस घड़ी के हिसाब से चलता है, record का timestamp कहाँ से आता है, और stream time सिर्फ़ आगे क्यों बढ़ता है |
| [0009](lessons/0009-windowed-aggregations.md) | Windowed Aggregations | Tumbling, hopping, sliding और session windows records को समय के हिसाब से कैसे group करती हैं, और हर एक किस सवाल का जवाब देती है |
| [0010](lessons/0010-late-data-grace-periods-and-suppression.md) | Late Data, Grace Periods और Suppression | कोई window क्रम से बाहर आए records को कितनी देर तक स्वीकार करती है, उसके बाद आने वालों का क्या होता है, और सिर्फ़ अंतिम result कैसे emit करें |
| [0011](lessons/0011-stream-table-joins-and-co-partitioning.md) | Stream-Table Joins और Co-Partitioning | कोई stream हर record को table से कैसे enrich करता है, दोनों तरफ़ का co-partitioned होना क्यों ज़रूरी है, और कब GlobalKTable यह ज़रूरत हटा देती है |
| [0012](lessons/0012-stream-stream-and-table-table-joins.md) | Stream-Stream और Table-Table Joins | Windowed join दो streams के events की जोड़ियाँ कैसे बनाता है, और table joins, foreign-key joins समेत, result को कैसे current रखते हैं |
| [0013](lessons/0013-exactly-once-in-kafka-streams.md) | Kafka Streams में Exactly-Once | `exactly_once_v2` reads, state और writes में किस चीज़ को atomic बनाता है, और कौन-से side effects वह कवर नहीं कर सकता |
| [0014](lessons/0014-tasks-threads-and-scaling-out.md) | Tasks, Threads और Scaling Out | Partitions tasks कैसे बनते हैं, tasks threads और instances में कैसे बँटते हैं, और app के parallelism की सीमा कौन तय करता है |
| [0015](lessons/0015-rebalancing-restoration-and-standby-replicas.md) | Rebalancing, Restoration और Standby Replicas | Task के move होने पर state का क्या होता है, और standby और warmup replicas उसके unavailable रहने का समय कैसे घटाते हैं |
| [0016](lessons/0016-testing-with-topologytestdriver.md) | TopologyTestDriver से Testing | बिना broker के unit test में topology के output, state और समय से जुड़े व्यवहार को कैसे test करें |
| [0017](lessons/0017-operating-and-monitoring-a-streams-app.md) | Streams App को Operate और Monitor करना | वे metrics, states और exception handlers जो बताते हैं कि चल रहा app ठीक है या नहीं, और ठीक न हो तो क्या करें |
| [0018](lessons/0018-when-kafka-streams-is-the-wrong-tool.md) | जब Kafka Streams ग़लत Tool हो | कब कोई साधारण consumer, Flink या ksqlDB किसी workload पर Streams app से बेहतर बैठता है, और उस फ़ैसले को सही कैसे ठहराएँ |
| [0019](lessons/0019-reviewing-someone-elses-topology.md) | किसी और की Topology की Review | Streams topology की review कैसे करें और बताएँ कि हर चुनाव की क़ीमत internal topics, state और correctness में क्या है |
| [0020](lessons/0020-changing-a-topology-others-depend-on.md) | ऐसी Topology बदलना जिस पर दूसरे निर्भर हैं | चल रहे app की topology को उसका state बिगाड़े या downstream consumers तोड़े बिना कैसे बदलें, और किसी विवादित दावे को source से कैसे सुलझाएँ |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत, हर एक के साथ टिप्पणी कि वह क्या कवर करता है
- [DSL Operations](reference/dsl-operations.md): input और output type के हिसाब से हर DSL operation, वह state रखता है या नहीं, और repartition करता है या नहीं
- [State Stores](reference/state-stores.md): store types, changelog settings, record cache, और state कैसे restore होता है
- [Time और Windows](reference/time-and-windows.md): तीन घड़ियाँ, चार window types, grace periods और हर एक कब emit करता है
- [Joins](reference/joins.md): join matrix, साथ में windowing, co-partitioning और यह कि हर join क्या emit करता है
- [Configuration](reference/configuration.md): guarantees, latency, parallelism और recovery तय करने वाली settings, उनके defaults के साथ
- [Operations](reference/operations.md): देखने लायक़ metrics, client और thread states, exception handlers और operator tools
- [Topology Review](reference/topology-review.md): topology की review के लिए checklist, tool का फ़ैसला, और topology के सुरक्षित और असुरक्षित बदलाव

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
