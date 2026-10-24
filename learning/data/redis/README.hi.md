---
title: Redis
description: "Redis का उपयोग उसी के लिए करें जो वह है: memory model, eviction, persistence, और वे patterns जो चुपचाप उसका दुरुपयोग करते हैं"
type: topic
---

# सीखना: Redis

पहचान सकें कि कोई मौजूदा system Redis का चुपचाप दुरुपयोग कहाँ कर रहा है, जैसे cache को store मान लेना या ऐसा lock जो असल में lock नहीं है, और इसके बजाय शुरू से सही उपयोग डिज़ाइन कर सकें।

**नवीनतम पाठ:** [17. ACLs और Protected Mode](lessons/0017-acls-and-protected-mode.md)

## सफलता कैसी दिखती है

- किसी मौजूदा system के Redis उपयोग को देखकर पहचानें कि क्या वह cache को durable store मान रहा है, lock को ग़लत ढंग से लागू कर रहा है, या असीमित keyspace चला रहा है, और बताएँ कि इसकी वजह से क्या टूटता है।
- किसी नए use case के लिए Redis का सही उपयोग (सीमित keyspace, उपयुक्त eviction policy, असली distributed lock) शुरू से डिज़ाइन करें।
- Redis की persistence गारंटियों (RDB/AOF) की तुलना Postgres की WAL-आधारित durability से करें, और बताएँ कि database के बजाय Redis चुनना कब सही निर्णय है और कब anti-pattern।
- Redis Cluster/Sentinel के बारे में उन समझौतों के स्तर पर तर्क करें जो clustering लाती है, उसे चलाने की ज़रूरत के बिना।

## सीमाएँ

- Redis का कोई पूर्व अनुभव नहीं माना गया है।

## दायरे से बाहर

- Production Postgres instance चलाना: [`data/postgres`](../../data/postgres/) देखें, तुलना के लिए link किया गया है, दोहराया नहीं गया।

## पूरी रूपरेखा

दस चरण, eviction से लेकर access control तक। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. Memory और eviction | 0001 | Redis keys को evict करता ही क्यों है, और इसे भूल जाने से पैदा होने वाला anti-pattern | किसी दिए workload पर eviction policy का असर समझा सकें |
| 2. Persistence | 0002 से 0003 | RDB और AOF, और उनकी durability Postgres के WAL से कैसे तुलना करती है | बता सकें कि database के बजाय Redis चुनना कब सही है और कब anti-pattern |
| 3. Distributed locks | 0004 से 0005 | Naive locking की ग़लतियाँ, Redlock, Kleppmann की आलोचना | Redis-आधारित distributed lock डिज़ाइन कर सकें, या उसे सही कारण से अस्वीकार कर सकें |
| 4. Cache-बनाम-store anti-patterns | 0006 से 0007 | Cache-aside, durable store माना गया cache, असीमित keyspace | किसी मौजूदा system में दुरुपयोग पहचान सकें और बता सकें कि क्या टूटता है |
| 5. Clustering | 0008 | Redis Cluster और Sentinel, clustering के लाए समझौते | उसे चलाने की ज़रूरत के बिना clustering के trade-offs पर तर्क कर सकें |
| 6. Data types और उनका cost model | 0009 से 0010 | Strings, hashes, lists, sets, sorted sets, bitmaps, HyperLogLog, और उनमें से चुनना | बताए गए use case के लिए data structure चुन सकें और समझा सकें कि उसकी क़ीमत क्या है |
| 7. Messaging और expiration | 0011 से 0012 | Pub/Sub बनाम streams, Kafka की तुलना में consumer groups, lazy बनाम active key expiration | किसी use case के लिए सही messaging तंत्र चुन सकें और समझा सकें कि key असल में Redis से कैसे निकलती है |
| 8. Transactions और scripting | 0013 से 0014 | `MULTI`/`EXEC`, `WATCH` के साथ optimistic locking, Lua scripting, Redis Functions | ऐसा check-then-act क्रम बना सकें जो सचमुच सुरक्षित हो, और समझा सकें कि lock का release atomic किससे बनता है |
| 9. Performance और संचालन | 0015 से 0016 | Round-trip की क़ीमत, pipelining, connection pooling, `INFO`/`SLOWLOG`/latency monitor/`MEMORY USAGE`, `SCAN` बनाम `KEYS` | बातूनी client की network क़ीमत घटा सकें और instance को जमाए बिना उसके असली व्यवहार का diagnosis कर सकें |
| 10. Access control | 0017 | Protected mode, ACLs, command categories, default user | सीमित कर सकें कि unauthenticated connection और authenticated user हर एक क्या कर सकता है |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-memory-and-eviction.md) | Memory और Eviction | Redis keys को evict करता ही क्यों है, और इसे भूल जाने से पैदा होने वाला anti-pattern |
| [0002](lessons/0002-rdb-snapshotting.md) | RDB Snapshotting | RDB snapshot असल में क्या capture करता है, और उसका save interval data-loss की कौन-सी खिड़की खुली छोड़ता है |
| [0003](lessons/0003-aof-and-wal-comparison.md) | AOF और WAL से तुलना | AOF की fsync policy उसकी data-loss खिड़की कैसे तय करती है, और Redis की सबसे मज़बूत आम setting भी Postgres के default की तुलना में रफ़्तार के बदले ज़्यादा durability क्यों छोड़ती है |
| [0004](lessons/0004-naive-locking-mistakes.md) | Naive Locking की ग़लतियाँ | अकेला SET NX PX distributed lock क्यों नहीं है, और वे दो failure modes जो असली परिस्थितियों में उसे तोड़ देते हैं |
| [0005](lessons/0005-redlock-and-kleppmanns-critique.md) | Redlock और Kleppmann की आलोचना | Redlock naive lock में असल में क्या ठीक करता है, Kleppmann की आलोचना दिखाती है कि वह अब भी क्या ठीक नहीं करता, और कैसे तय करें कि Redis lock सही औज़ार है भी या नहीं |
| [0006](lessons/0006-cache-aside-and-the-store-anti-pattern.md) | Cache-Aside और Store Anti-Pattern | Cache-aside का सही उपयोग कैसा दिखता है, और वह ख़ास तरीक़ा जिससे यह pattern छोड़ने पर cache चुपचाप system of record बन जाता है |
| [0007](lessons/0007-unbounded-keyspace-and-spotting-misuse.md) | असीमित Keyspace का Anti-Pattern और दुरुपयोग की पहचान | जब कोई TTL या eviction policy सेट न करे तो keyspace बिना सीमा कैसे बढ़ता है, और किसी मौजूदा system में इसे और store anti-pattern को पहचानने की checklist |
| [0008](lessons/0008-cluster-and-sentinel.md) | Redis Cluster और Sentinel | Redis Cluster की sharding और Sentinel का automatic failover हर एक कौन-से समझौते लाता है, दोनों में से किसी को चलाने की ज़रूरत के बिना उन पर तर्क |
| [0009](lessons/0009-strings-hashes-and-lists.md) | Strings, Hashes, और Lists | वे तीन मूल data structures जिन्हें Redis असल में store करता है, और हर एक को पढ़ने, लिखने, और बढ़ाने की क़ीमत |
| [0010](lessons/0010-sets-sorted-sets-and-probabilistic-structures.md) | Sets, Sorted Sets, और Probabilistic Structures | किसी use case के लिए data structure चुनना, सटीक membership से लेकर ऐसी अनुमानित गिनती तक जिसे रखने में लगभग कुछ नहीं लगता |
| [0011](lessons/0011-streams-and-pubsub-as-messaging.md) | Messaging Surface के रूप में Streams और Pub/Sub | Redis clients के बीच messages ले जाने के दो तरीक़े, और उनमें से सिर्फ़ एक पर queue बनाना सुरक्षित क्यों है |
| [0012](lessons/0012-key-expiration-lazy-vs-active.md) | Key Expiration: Lazy बनाम Active Expiry | Key का TTL शून्य पर पहुँचना अपने-आप उसे memory से क्यों नहीं हटाता, और वे दो तंत्र जो आख़िरकार हटाते हैं |
| [0013](lessons/0013-multi-exec-and-optimistic-locking-with-watch.md) | MULTI/EXEC और WATCH के साथ Optimistic Locking | कई commands को queue करना ताकि वे बिना रुकावट चलें, और उस पर कार्रवाई करने से पहले यह पकड़ना कि कोई मान आपकी जानकारी के बिना बदल गया |
| [0014](lessons/0014-lua-scripting-and-redis-functions.md) | Lua Scripting और Redis Functions | वह तंत्र जो lock के release को असल में सुरक्षित बनाता है, check और action को एक atomic क़दम के रूप में चलाकर |
| [0015](lessons/0015-pipelining-round-trip-cost-and-connection-pooling.md) | Pipelining, Round-Trip की क़ीमत, और Connection Pooling | N क्रमिक commands की क़ीमत N network round trips क्यों होती है, भले हर एक microseconds में चलता हो, और दो अलग सुधार |
| [0016](lessons/0016-operational-visibility.md) | संचालन की दृश्यता | वे औज़ार जो दिखाते हैं कि Redis instance असल में क्या कर रहा है, और वह एक command जिसने लगभग किसी भी दूसरे से ज़्यादा outages करवाए हैं |
| [0017](lessons/0017-acls-and-protected-mode.md) | ACLs और Protected Mode | Redis unauthenticated instance तक पहुँच को ही कैसे रोकता है, और authenticated client को असल में क्या करने की अनुमति है उसका दायरा कैसे तय करता है |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत
- [Persistence](reference/persistence.md): RDB और AOF हर एक क्या वादा करता है, हर fsync policy कितनी ठीक-ठीक data-loss खिड़की छोड़ती है, और database की durability की बराबरी के बारे में Redis का अपना documentation क्या कहता है
- [Distributed Locks](reference/distributed-locks.md): naive lock और उसके दो छेद, validity के हिसाब के साथ Redlock का algorithm, और वह एक सवाल जो तय करता है कि दोनों में से कोई सही औज़ार है या नहीं
- [Cache बनाम Store Anti-Patterns](reference/cache-vs-store-anti-patterns.md): सही ढंग से किया गया cache-aside, वे दो तरीक़े जिनसे cache, cache नहीं रहता, और वे eviction settings जो तय करती हैं कि आपको कौन-सी विफलता मिलेगी
- [Clustering](reference/clustering.md): Cluster के slots क्या छीन लेते हैं, वे settings जो तय करती हैं कि कमज़ोर हुआ cluster सेवा देता है या रुक जाता है, और Sentinel का quorum failover को नियंत्रित क्यों नहीं करता

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
