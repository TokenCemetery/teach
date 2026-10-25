---
title: Kafka
description: "Log को अपने हाथ में लें: partitions, consumer groups, delivery guarantees, और \"exactly once\" की असली क़ीमत"
type: topic
---

# सीखना: Kafka

असली workload के लिए topic और partition का ढाँचा डिज़ाइन कर सकें, और consumer lag, rebalancing storms या अनपेक्षित message loss का अंदाज़े से सुधार करने के बजाय उसका diagnosis कर सकें।

**नवीनतम पाठ:** [16. Cluster चलाने के लिए ज़रूरी Metrics](lessons/0016-the-metrics-that-matter-for-operating-a-cluster.md)

## सफलता कैसी दिखती है

- बताए गए workload के लिए topic, partition और consumer-group का ढाँचा डिज़ाइन करें, और उसके पीछे के delivery-guarantee चुनाव को सही ठहराएँ।
- कोई consumer पीछे चल रहा हो या बार-बार rebalance हो रहा हो, तो पता लगाएँ कि कौन-सी setting या उपयोग का तरीक़ा दोषी है।
- बताएँ कि "exactly once" की असली क़ीमत क्या है, और कब idempotent handling के साथ at-least-once बेहतर सौदा है।

## सीमाएँ

- Kafka या messaging system का कोई पूर्व अनुभव नहीं माना गया है।
- Apache Kafka reference implementation है; विकल्प (Redpanda, managed services) कवर नहीं होते।
- आसपास के ecosystem (Schema Registry, Kafka Connect की बुनियादी बातें) को संक्षेप में छुआ गया है, वहाँ जहाँ सिर्फ़ log की गारंटियाँ यह नहीं समझातीं कि असली pipeline कैसे बनता है।

## दायरे से बाहर

- Delivery guarantees के पीछे का failure model ख़ुद: [`architecture/distributed-systems`](../../architecture/distributed-systems/) देखें, यहाँ फिर से निकालने के बजाय link किया गया है।
- Kafka Streams और log के ऊपर computation (topologies, state, windows, joins): [`data/stream-processing`](../../data/stream-processing/) देखें, जो delivery semantics के लिए यहाँ वापस link करता है। ksqlDB अपने-आप में विषय के रूप में।

## पूरी रूपरेखा

दस चरण, log से लेकर production में cluster चलाने तक। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. Partitions और log | 0001 | वह इकाई जिसके इर्द-गिर्द बाक़ी सब (ordering, parallelism, consumer groups) बना है | समझा सकें कि partition ordering और parallelism की इकाई क्यों है |
| 2. Consumer groups और rebalancing | 0002 से 0003 | Group coordination, cooperative rebalancing, consumer lag | पीछे चल रहे या बार-बार rebalance होने वाले consumer का diagnosis कर सकें |
| 3. Delivery guarantees | 0004 से 0005 | At-most/at-least/exactly-once semantics, idempotent producers, transactions | Delivery-guarantee चुनाव को सही ठहरा सकें और बता सकें कि exactly-once की क़ीमत क्या है |
| 4. ढाँचे का डिज़ाइन | 0006 से 0007 | Key का चुनाव, partition-count के trade-offs, ordering guarantees | बताए गए workload के लिए topic और partition का ढाँचा डिज़ाइन कर सकें |
| 5. आसपास का ecosystem | 0008 से 0009 | Schema Registry, Kafka Connect की बुनियादी बातें | समझा सकें कि असली pipeline में ये log के इर्द-गिर्द कैसे बैठते हैं |
| 6. Retention और replication | 0010 से 0011 | `cleanup.policy`, log compaction, replication factor, ISR, `acks`, `min.insync.replicas`, unclean leader election | सही ठहरा सकें कि topic का data कितने समय तक रहता है और उसकी replication settings असल में कौन-सी durability की गारंटी देती हैं |
| 7. Load के तहत client configuration | 0012 | `batch.size`, `linger.ms`, `fetch.min.bytes`, `max.poll.interval.ms` | Throughput, latency या बेवजह rebalance के लक्षण को उस ख़ास client setting से मिला सकें जो उसे संभालती है |
| 8. Cluster coordination | 0013 | KRaft, controller quorum, `process.roles`, ZooKeeper की जगह क्या आया | समझा सकें कि controller quorum क्या करता है और KRaft failover को पूरा metadata दोबारा fetch करने की ज़रूरत क्यों नहीं |
| 9. Security और multi-tenancy | 0014 से 0015 | TLS, SASL, `security.protocol`, ACLs, deny-by-default, quotas | बता सकें कि कोई दिया गया security सवाल असल में किस तंत्र (encryption, authentication, authorization, या resource isolation) से जुड़ा है |
| 10. Cluster चलाना | 0016 | `UnderReplicatedPartitions`, `UnderMinIsr`, disk headroom, request latency, request-handler saturation | बता सकें कि कोई दिया गया संचालन लक्षण संकेतों के तीन परिवारों में से किसका है, और अकेले broker बनाम पूरे cluster की समस्या में triage कर सकें |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-partitions-and-the-log.md) | Partitions और Log | वह इकाई जिसके इर्द-गिर्द इस workspace में बाक़ी सब (ordering, parallelism, consumer groups) बना है |
| [0002](lessons/0002-consumer-group-coordination.md) | Consumer Group Coordination | Group coordinator और group leader partitions को consumers के बीच कैसे बाँटते हैं, और offsets हर group की प्रगति का हिसाब कैसे रखते हैं |
| [0003](lessons/0003-cooperative-rebalancing-and-lag.md) | Cooperative Rebalancing और Consumer Lag का Diagnosis | मूल rebalance protocol rebalancing storm क्यों पैदा करता है, cooperative rebalancing उसे कैसे सीमित करता है, और consumer lag के diagnosis का क्रम |
| [0004](lessons/0004-delivery-semantics.md) | At-Most-Once, At-Least-Once, और Exactly-Once | Produce, broker, और consume के रास्ते के हिस्सों में हर delivery guarantee असल में कहाँ जीती या हारी जाती है |
| [0005](lessons/0005-idempotent-producers-and-transactions.md) | Idempotent Producers और Transactions | Idempotence लगभग मुफ़्त क्यों है, जबकि exactly-once की असली क़ीमत transactions चुकाते हैं |
| [0006](lessons/0006-partition-key-choice.md) | Partition Key का चुनाव और Ordering Guarantees | Partition key चुनने का मतलब एक ही निर्णय में यह चुनना है कि आपको कौन-सी ordering मिलती है और आप कौन-सा parallelism छोड़ते हैं |
| [0007](lessons/0007-partition-count-and-topic-layout.md) | Partition-Count के Trade-offs और Topic Layout का डिज़ाइन | ज़्यादा partitions मुफ़्त क्यों नहीं हैं, और पूरी तरह सही ठहराए गए topic layout को हर पिछले चरण से क्या नाम लेना होता है |
| [0008](lessons/0008-schema-registry.md) | Schema Registry | Produce के समय असंगत schema बदलाव को पकड़ लेना, आगे consume के समय होने वाली चुपचाप टूटन की जगह कैसे लेता है |
| [0009](lessons/0009-kafka-connect-basics.md) | Kafka Connect की बुनियादी बातें | Connect के tasks और worker modes parallelism और fault tolerance कैसे देते हैं, और Connect ऐसी कोई गारंटी क्यों नहीं देता जो नीचे का producer या consumer API पहले से न देता हो |
| [0010](lessons/0010-retention-and-log-compaction.md) | Retention और Log Compaction | कोई message topic में असल में कितने समय तक बचा रहता है, और वह दूसरी cleanup policy जो key की उम्र के बजाय उसका इतिहास रखती है |
| [0011](lessons/0011-replication-isr-acks-and-unclean-leader-election.md) | Replication, ISR, acks, और Unclean Leader Election | acks=all असल में किसका इंतज़ार करता है, वह न्यूनतम सीमा जो उसे चुपचाप सुनने से कम मतलब देने से रोकती है, और जब हर in-sync replica चली जाए तब का trade-off |
| [0012](lessons/0012-producer-and-consumer-configuration-under-load.md) | Load के तहत Producer और Consumer Configuration | Client-पक्ष के वे knobs जो throughput के बदले latency देते हैं, और वह एक knob जो ऐसे consumer के लिए भी rebalance trigger कर सकता है जो असल में कभी मरा ही नहीं था |
| [0013](lessons/0013-kraft-and-what-replaced-zookeeper.md) | KRaft, और ZooKeeper की जगह क्या आया | बाहरी coordination service हटने के बाद cluster अपने metadata पर सहमति कैसे बनाता है, और failover पर पूरी state दोबारा fetch करना वह समस्या क्यों थी जिसे सुलझाना ज़रूरी था |
| [0014](lessons/0014-tls-and-sasl-authenticating-to-a-cluster.md) | TLS और SASL: Cluster से Authenticate करना | Channel को encrypt करना और client को authenticate करना दो अलग काम हैं जिन्हें security.protocol एक setting में जोड़ देता है, और दोनों को एक मान लेना ही ज़्यादातर उलझन की शुरुआत है |
| [0015](lessons/0015-acls-and-quotas-authorization-and-multi-tenancy.md) | ACLs और Quotas: Authorization और Multi-Tenancy | Authenticated principal भी तब तक कुछ करने के लिए authorized नहीं है जब तक कोई ACL ऐसा न कहे, और काम करने की अनुमति वाला principal भी इससे सुरक्षित नहीं कि वह cluster की क्षमता से हर दूसरे tenant को भूखा मार दे |
| [0016](lessons/0016-the-metrics-that-matter-for-operating-a-cluster.md) | Cluster चलाने के लिए ज़रूरी Metrics | Under-replicated partitions, disk headroom, और request latency वे तीन संकेत हैं जिन पर नज़र रखनी चाहिए, और हर एक अलग तरह की परेशानी की ओर इशारा करता है |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत
- [Consumer Groups और Rebalancing](reference/consumer-groups-and-rebalancing.md): दो rebalance protocols, दो स्वतंत्र liveness timeouts, और consumer lag के diagnosis का क्रम, हर क़दम को नियंत्रित करने वाले config के साथ
- [Delivery Guarantees](reference/delivery-guarantees.md): रास्ते के हर हिस्से को कौन-सा config तय करता है, idempotence चुपचाप बंद क्यों हो सकती है, और read_committed consumer असल में किसका इंतज़ार करता है
- [Topic और Partition Design](reference/topic-and-partition-design.md): कोई record असल में partition तक कैसे पहुँचता है, उससे कौन-सी ordering मिलती है और कौन-सी नहीं, और वे दो दिशाएँ जिनमें partition count बदलना महँगा है
- [Ecosystem](reference/ecosystem.md): सात compatibility types और हर एक में पहले किसे upgrade करना होता है, और Kafka Connect log के इर्द-गिर्द क्या जोड़ता है, उस गारंटी समेत जो default रूप से बंद रहती है

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
