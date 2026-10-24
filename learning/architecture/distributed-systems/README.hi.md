---
title: Distributed Systems
description: "Partial failure पर तर्क करें: network आपके साथ क्या कर सकता है, आप असल में कौन-सी consistency ख़रीद रहे हैं, और consensus महँगा क्यों है"
type: topic
---

# सीखना: Distributed Systems

जिस system को आप डिज़ाइन कर रहे हैं उसके लिए consistency model चुन और सही ठहरा सकें, और partial failure से हुए production incident पर network को भरोसेमंद मानने के बजाय तर्क कर सकें।

**नवीनतम पाठ:** [19. किसी दावे का सत्यापन](lessons/0019-verifying-a-claim.md)

## सफलता कैसी दिखती है

- किसी system design के लिए consistency model चुनें और विकल्पों के सामने उसके trade-off को सही ठहराएँ।
- Partial failure (network partition, मरा हुआ मान लिया गया धीमा node) से हुए incident में ज़िम्मेदार तंत्र का नाम बताएँ।
- समझाएँ कि consensus protocol आपको क्या देता है और उसकी क़ीमत उतनी क्यों है जितनी है, उसकी correctness को मूल सिद्धांतों से सिद्ध किए बिना।

## सीमाएँ

- Networked service बनाने का पेशेवर अनुभव माना गया है; distributed systems का कोई औपचारिक अध्ययन ज़रूरी नहीं।
- ज़ोर व्यावहारिक और संचालन पर है: protocol की correctness के औपचारिक proof से ज़्यादा क़ीमत और trade-offs मायने रखते हैं।

## दायरे से बाहर

- एक process के भीतर concurrency (goroutines, threads, `Send`/`Sync`): यह भाषा वाले workspaces का हिस्सा है। यह workspace वहाँ से शुरू होता है जहाँ process की सीमा पार होती है।
- Cluster orchestrator पर workloads चलाना: यह [`infrastructure/kubernetes`](../../infrastructure/kubernetes/) का हिस्सा है, जो सिखाता है कि etcd और reconciliation का व्यवहार में क्या मतलब है और सिद्धांत के लिए यहाँ वापस link करता है।

## पूरी रूपरेखा

बारह चरण, partial failure से लेकर diagnose किए गए incident तक, फिर उन तंत्रों तक जिनसे production systems असल में उससे बच निकलते हैं, और यह सत्यापित करने तक कि इनमें से कोई भी बात सचमुच टिकती है। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. Partial failure | 0001 | वह एक समस्या जिसका जवाब इस workspace का हर बाद का विषय है | समझा सकें कि network को भरोसेमंद क्यों नहीं माना जा सकता |
| 2. समय और क्रम | 0002 से 0003 | Clocks, ordering, timeout ही एकमात्र उपलब्ध failure संकेत क्यों है | समझा सकें कि timeout धीमे node और मरे हुए node में फ़र्क़ क्यों नहीं कर सकता |
| 3. Consistency models | 0004 से 0006 | CAP, linearizability, sequential और eventual consistency | बताए गए design के लिए consistency model चुन और सही ठहरा सकें |
| 4. Consensus | 0007 से 0009 | Raft, leader election, consensus क्या देता है और उसकी क़ीमत उतनी क्यों है | Correctness सिद्ध किए बिना समझा सकें कि consensus protocol क्या देता है और उसकी क़ीमत क्या है |
| 5. Incidents का diagnosis | 0010 | ऊपर के तंत्रों को असली production incident पर लागू करना | Partial failure से हुए incident में ज़िम्मेदार तंत्र का नाम बता सकें |
| 6. Replication और quorums | 0011 | Leader-based बनाम leaderless replication, read/write quorums, `R + W > N` शर्त | समझा सकें कि quorum यह गारंटी कैसे देता है कि read नवीनतम write देखे, और बताए गए workload के लिए R और W चुन सकें |
| 7. Partitioning और sharding | 0012 | Consistent hashing, virtual nodes, hot-key replication, request routing | समझा सकें कि consistent hashing resize की क़ीमत को सीमित क्यों करता है, और failure और hot keys संभालने के लिए अकेले ring को अब भी क्या चाहिए |
| 8. Eventual consistency में conflict resolution | 0013 | Last-write-wins और वह क्या खोता है, version vectors, CRDTs | Conflict पकड़ने और उसे सुलझाने में फ़र्क़ कर सकें, और समझा सकें कि CRDT बिना नुक़सान के merge कैसे करता है |
| 9. Services के पार transactions | 0014 से 0015 | Two-phase commit और उसका blocking failure mode, sagas और compensation, transactional outbox, idempotent consumers | समझा सकें कि 2PC block क्यों होता है, saga उससे बचने के लिए क्या छोड़ता है, और outbox pattern dual-write समस्या से कैसे बचता है |
| 10. Resilience toolkit | 0016 से 0017 | Timeout budgets, backoff और jitter के साथ retries, retry storms, circuit breakers, load shedding, backpressure | समझा सकें कि timeout fire होने के बाद क्या करें, और fail हो रही dependency, overloaded server, या भरती queue को सही तंत्र से मिला सकें |
| 11. Partial failure की observability | 0018 | Spans, traces, network सीमा के पार propagation, span kinds | समझा सकें कि trace एक request के spans को services के पार कैसे जोड़ता है, और propagation हर hop पर स्पष्ट रूप से क्यों होना चाहिए |
| 12. किसी दावे का सत्यापन | 0019 | Jepsen की opaque-box, model-checked testing, chaos engineering का production fault injection, deterministic simulation की reproducibility | समझा सकें कि हर verification तकनीक कौन-सा trade-off करती है, और कोई दिया गया test परिणाम क्या सिद्ध करता है और क्या नहीं |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-partial-failure.md) | Partial Failure | वह एक समस्या जिसका जवाब इस workspace का हर बाद का विषय है |
| [0002](lessons/0002-clocks-and-ordering.md) | Clocks और Ordering | अलग-अलग machines के wall-clock timestamps पर events का क्रम तय करने के लिए भरोसा क्यों नहीं किया जा सकता, और logical clock synchronized समय के बिना उन्हें क्रम में कैसे रखता है |
| [0003](lessons/0003-timeouts-as-failure-detectors.md) | Failure Detectors के रूप में Timeouts | हर व्यावहारिक failure detector timeout पर ही क्यों बना है, और उससे निकलने वाले accuracy-बनाम-speed trade-off की औपचारिक शब्दावली |
| [0004](lessons/0004-the-cap-theorem-precisely.md) | CAP Theorem, सटीक रूप में | CAP असल में क्या सिद्ध करता है, partition tolerance कभी वैकल्पिक क्यों नहीं थी, और वे ख़ास ग़लत व्याख्याएँ जो "कोई दो चुनो" को इसे कहने का ग़लत तरीक़ा बनाती हैं |
| [0005](lessons/0005-linearizability.md) | Linearizability | Linearizability असल में क्या गारंटी देती है, वह सबसे मज़बूत आम consistency model क्यों है, और partition के दौरान उसे देने की क़ीमत क्या है |
| [0006](lessons/0006-sequential-and-eventual-consistency.md) | Sequential और Eventual Consistency | Linearizability से कमज़ोर दो models, हर एक अब भी क्या गारंटी देता है, और बताए गए design के लिए तीनों में से कैसे चुनें |
| [0007](lessons/0007-what-consensus-is-for.md) | Consensus किसलिए है | वह replicated-state-machine समस्या जिसे consensus protocols सुलझाते हैं, और वह linearizable system के coordination के नीचे का तंत्र क्यों है |
| [0008](lessons/0008-raft-leader-election-and-log-replication.md) | Raft, Leader Election और Log Replication | Raft एक अकेला leader कैसे चुनता है और उसके ज़रिए log को replicate कैसे करता है, वे दो तंत्र जो replicated-state-machine समस्या को ठोस चीज़ में बदलते हैं |
| [0009](lessons/0009-what-consensus-costs.md) | Consensus की क़ीमत | हर write majority तक एक round trip क्यों चुकाता है, minority partition consistency के बजाय availability क्यों खोता है, और उस क़ीमत को consensus से मिलने वाली चीज़ के सामने कैसे तौलें |
| [0010](lessons/0010-diagnosing-a-production-incident.md) | Production Incident का Diagnosis | "network" या "consistency" पर अमूर्त रूप से तर्क करने के बजाय, partial failure, failure detection, consistency models, और consensus को लागू करके असली incident के पीछे के तंत्र का नाम बताना |
| [0011](lessons/0011-replication-and-quorums.md) | Replication और Quorums | Consensus protocol data replicate करने का अकेला तरीक़ा नहीं है, और उसके सस्ते विकल्प के पीछे की quorum शर्त एक अकेली overlap गारंटी है, majority सहमति की कोई अस्पष्ट धारणा नहीं |
| [0012](lessons/0012-partitioning-and-sharding.md) | Partitioning और Sharding | Consistent hashing इसलिए है क्योंकि naive hash-mod-N partitioning किसी node के जुड़ने या निकलने के पल लगभग सब कुछ फिर से map कर देता है, और consistent hashing को भी virtual nodes चाहिए, तभी वह fail हुए node का पूरा load किसी एक बदक़िस्मत पड़ोसी पर डालना बंद करता है |
| [0013](lessons/0013-conflict-resolution-under-eventual-consistency.md) | Eventual Consistency में Conflict Resolution | यह पकड़ना कि दो writes concurrent थे और यह तय करना कि उसके बारे में क्या करें, दो अलग समस्याएँ हैं, और last-write-wins दोनों में से किसी को नहीं सुलझाता, वह बस एक बचने वाला चुनता है और हारने वाले को फेंक देता है |
| [0014](lessons/0014-two-phase-commit-and-sagas.md) | Two-Phase Commit और Sagas | Two-phase commit consensus जैसा दिखता है (coordinator, vote, commit), पर वह अलग समस्या सुलझाता है और उसकी बदतर क़ीमत चुकाता है: अगर coordinator vote के बीच मर जाए तो वह हमेशा के लिए block हो जाता है, और ठीक इसी वजह से production systems इसके बजाय sagas अपनाते हैं |
| [0015](lessons/0015-the-transactional-outbox-and-idempotent-consumers.md) | Transactional Outbox और Idempotent Consumers | Database update करना और event publish करना, दोनों distributed transaction के बिना atomic ढंग से नहीं हो सकते, इसलिए outbox pattern event को उसी local transaction में एक साधारण row के रूप में लिखकर इस समस्या से पूरी तरह किनारा कर लेता है, और उसकी क़ीमत ऐसे message से चुकाता है जो दो बार भेजा जा सकता है |
| [0016](lessons/0016-timeouts-retries-and-backoff.md) | Timeouts, Retries, और Backoff | पाठ 3 ने स्थापित किया कि timeout ही एकमात्र उपलब्ध failure संकेत है, पर उसे fire करके तुरंत retry करना ही ठीक वह चीज़ है जो recover हो रही service के बुरे दिन को भीड़ के हमले में बदल देती है, और यही वह ख़ास समस्या है जिसे रोकने के लिए backoff और jitter हैं |
| [0017](lessons/0017-circuit-breakers-load-shedding-and-backpressure.md) | Circuit Breakers, Load Shedding, और Backpressure | Backoff और jitter वाला retry भी यह मानकर चलता है कि fail हो रही call आज़माने लायक है ही, और circuit breaker, load shedding, और backpressure उस समय के तीन उत्तर हैं जब वह आज़माने लायक नहीं रहती, क्रमशः fail हो रही dependency, overloaded server, और दबे हुए queue के लिए |
| [0018](lessons/0018-distributed-tracing-and-correlation.md) | Distributed Tracing और Correlation | इस workspace में अब तक कवर हुआ हर तंत्र बताता है कि failure के तहत system क्या करता है, पर कोई नहीं बताता कि किसी ख़ास request का कौन-सा hop असल में fail हुआ, और trace ठीक इसी एक बात का उत्तर देने के लिए बना है |
| [0019](lessons/0019-verifying-a-claim.md) | किसी दावे का सत्यापन | Jepsen, chaos engineering, और deterministic simulation, तीनों customer से पहले असली bug ढूँढने की कोशिश करते हैं, पर वहाँ पहुँचने के लिए realism और reproducibility के बीच उलटे सौदे करते हैं, और कौन क्या है यह जानना ही बताता है कि कोई दिया गया test असल में क्या सिद्ध करता है |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत
- [समय और क्रम](reference/time-and-order.md): happens-before क्या तय कर सकता है और क्या नहीं, Lamport clock क्या बताने से इनकार करता है, और failure-detector शब्दावली जिसका timeout एक उदाहरण है
- [Consistency Models](reference/consistency-models.md): CAP उसी रूप में जैसे वह सिद्ध हुआ था, models साथ-साथ और हर एक क्या गारंटी देता है, और उनमें से कौन partition के दौरान उत्तर दे भी सकता है
- [Consensus](reference/consensus.md): replicated-state-machine समस्या, Raft की पाँच safety properties और उन्हें पैदा करने वाले नियम, और majority की writes और reads पर क़ीमत
- [Incidents का Diagnosis](reference/diagnosing-incidents.md): क्रम में चार सवाल, लक्षण को सटीक रूप से बताने के लिए नामित anomaly शब्दावली, और ऊपर की sheets से जुड़ी लक्षण-से-तंत्र तालिका

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
