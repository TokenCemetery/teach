---
title: Postgres
description: "Postgres चलाएँ: WAL, vacuum और bloat, replication, और index को बनाए रखने की क़ीमत"
type: topic
---

# सीखना: Postgres

चलते हुए Postgres instance को, चाहे self-hosted हो या managed, संचालित कर सकें, और bloat, replication lag या धीमे recover होने वाले failover का अंदाज़े से सुधार करने के बजाय उसका diagnosis कर सकें, साथ ही नए deployment के लिए storage, replication और index के रखरखाव को शुरू से डिज़ाइन कर सकें।

**नवीनतम पाठ:** [18. Partitioning और TOAST](lessons/0018-partitioning-and-toast.md)

## सफलता कैसी दिखती है

- Bloated table या पीछे चल रही replica मिलने पर, trial and error के बजाय WAL, autovacuum और replication की कार्यप्रणाली से कारण का diagnosis करें।
- नए deployment के लिए storage, replication topology और index maintenance डिज़ाइन करें, और हर चुनाव को सही ठहराएँ।
- समझाएँ कि managed service (RDS जैसी) किन चीज़ों से आपको बचाती है और किनसे नहीं, ख़ुद instance चलाने की तुलना में।
- बताएँ कि vector index (pgvector) को बनाए रखना database को क्या पड़ता है, और इसे `llm/rag` के उस चुनाव से जोड़ें जिसमें pgvector को store बनाया गया है।

## सीमाएँ

- बुनियादी SQL की जानकारी मानी गई है (भाषा के लिए `programming/sql` देखें); database administration का पूर्व अनुभव ज़रूरी नहीं।
- Self-hosted संचालन और managed service में क्या बदलता है, दोनों कवर होते हैं।

## दायरे से बाहर

- Queries, query plans, schema design और isolation semantics: [`programming/sql`](../../programming/sql/) देखें, यहाँ दोहराने के बजाय link किया गया है। यह workspace चलते हुए instance का मालिक है, भाषा का नहीं।
- Columnar warehouse पर analytical workloads, और कब उसे Postgres से ये workloads ले लेने चाहिए: [`data/warehouses`](../../data/warehouses/) देखें, जिसका judgment चरण यह निर्णय लेता है।

## पूरी रूपरेखा

बारह चरण, durability से लेकर बड़े पैमाने पर table-स्तर के रखरखाव तक। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. Write-ahead log | 0001 | Durability का वह तंत्र जिस पर इस workspace की बाक़ी हर चीज़ खड़ी है | समझा सकें कि WAL crash को recoverable कैसे बनाता है |
| 2. Vacuum और bloat | 0002 से 0003 | Autovacuum के भीतरी हिस्से, MVCC और dead tuples, bloat का diagnosis और tuning | Vacuum और WAL की कार्यप्रणाली से bloated table का diagnosis कर सकें |
| 3. Replication | 0004 से 0006 | Streaming replication, replication slots, failover, lag का diagnosis | पीछे चल रही replica का diagnosis कर सकें और replication topology डिज़ाइन कर सकें |
| 4. Indexes और उनके रखरखाव की क़ीमत | 0007 से 0008 | B-tree/GiST/GIN के रखरखाव की क़ीमत, pgvector index को बनाए रखने की क़ीमत | Index maintenance की योजना डिज़ाइन कर सकें और pgvector की क़ीमत का हिसाब दे सकें |
| 5. Managed बनाम self-hosted | 0009 से 0010 | RDS जैसी managed service आपको किन चीज़ों से बचाती है, और किनसे नहीं | Managed service की सीमा समझा सकें और संचालन के चुनाव को सही ठहरा सकें |
| 6. Backup और point-in-time recovery | 0011 | Base backups, लगातार WAL archiving, `recovery_target_time`, और बिना परखा restore सत्यापित backup क्यों नहीं है | ऐसी backup रणनीति डिज़ाइन कर सकें और सही ठहरा सकें जो परखने पर सचमुच काम करता database फिर से बना दे |
| 7. Configuration और memory tuning | 0012 | `shared_buffers`, `work_mem`, `maintenance_work_mem`, checkpoint tuning | इन settings का आकार अलग-थलग single-query test के बजाय असली concurrency के हिसाब से तय कर सकें |
| 8. Monitoring | 0013 | `pg_stat_activity`, wait events, `pg_stat_statements`, server log | किसी दिए लक्षण के लिए सही monitoring surface (live backend state, कुल query लागत, या log में दर्ज event) चुन सकें |
| 9. Connection management | 0014 | `max_connections`, process-per-connection की क़ीमत, PgBouncer के session/transaction/statement pooling modes | ऐसा pooling mode चुन सकें जो application की असली निर्भरता से मेल खाए, न कि सबसे कुशल mode को default मान लें |
| 10. Logical replication और major-version upgrades | 0015 से 0016 | Publications और subscriptions, logical replication की DDL पाबंदी, `pg_upgrade` के transfer modes, कम downtime वाला logical-replication upgrade रास्ता | बताए गए downtime budget के लिए upgrade रास्ता (in-place `pg_upgrade` या logical-replication cutover) चुन और सही ठहरा सकें |
| 11. Roles, privileges, और row-level security | 0017 | Roles बनाम दूसरे systems का user/group विभाजन, membership के INHERIT/SET विकल्प, table-स्तर के GRANTs, row-level security और उसका owner-bypass default | Role और RLS policy का ढाँचा डिज़ाइन कर सकें और बता सकें कि सिर्फ़ RLS चालू करने से table owner पर पाबंदी क्यों नहीं लगती |
| 12. Partitioning और TOAST | 0018 | Range/list/hash partitioning, partition pruning, bloat-मुक्त bulk deletion, TOAST और उसकी चार storage रणनीतियाँ | Bloat-मुक्त lifecycle management के लिए partition ढाँचा डिज़ाइन कर सकें और बड़े column की storage रणनीति का हिसाब दे सकें |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-the-write-ahead-log.md) | Write-Ahead Log | Durability का वह तंत्र जिस पर इस workspace की बाक़ी हर चीज़ खड़ी है |
| [0002](lessons/0002-mvcc-and-dead-tuples.md) | MVCC और Dead Tuples | UPDATE या DELETE कभी कुछ तुरंत क्यों नहीं हटाता, और इससे vacuum के साफ़ करने के लिए dead tuples क्यों बच जाते हैं |
| [0003](lessons/0003-bloat-diagnosis-and-autovacuum-tuning.md) | Bloat का Diagnosis और Autovacuum Tuning | Bloat कैसे मापें, autovacuum पीछे क्यों रह जाता है, और diagnosis का वह क्रम जो अंदाज़े के बजाय असली कारण ढूँढता है |
| [0004](lessons/0004-streaming-replication-and-slots.md) | Streaming Replication और Replication Slots | Standby असल में कैसे जुड़ता है और बराबरी पर आता है, और replication slot ऐसी क्या गारंटी देता है जो साधारण streaming नहीं देती |
| [0005](lessons/0005-failover-mechanics.md) | Failover की कार्यप्रणाली | Standby को promote करने पर क्या होता है, पुराना primary बस यूँ ही दोबारा क्यों नहीं जुड़ सकता, और synchronous replication data-loss के किस trade-off को सीमित करता है |
| [0006](lessons/0006-diagnosing-replication-lag.md) | Replication Lag का Diagnosis | Receive lag और apply lag अलग-अलग माप क्यों हैं, और diagnosis का वह क्रम जो बताता है कि असल में कौन-सा हो रहा है |
| [0007](lessons/0007-index-maintenance-cost.md) | B-Tree, GiST, और GIN के रखरखाव की क़ीमत | हर index writes को महँगा क्यों बनाता है, और B-tree, GiST, और GIN हर एक वह क़ीमत अलग ढंग से कैसे चुकाता है |
| [0008](lessons/0008-what-a-pgvector-index-costs.md) | pgvector Index को बनाए रखने की क़ीमत | Disk, build-time, और स्थायी memory की वह क़ीमत जो vector index, अपने index किए गए कच्चे vectors के ऊपर, जोड़ता है |
| [0009](lessons/0009-what-managed-shields-you-from.md) | Managed Service आपको किससे बचाती है | RDS जैसा automation असल में क्या हटाता है, और पिछले पाठों की हर बात को उसके नीचे अब भी समझना क्यों ज़रूरी है |
| [0010](lessons/0010-defending-an-operating-choice.md) | संचालन के चुनाव को सही ठहराना | एक पूरा किया गया deployment डिज़ाइन जो default उत्तर मान लेने के बजाय हर चरण से एक ठोस निर्णय और क़ीमत का हवाला देता है |
| [0011](lessons/0011-backup-and-point-in-time-recovery.md) | Backup और Point-in-Time Recovery | Base backup और लगातार WAL archive मिलकर backup के बाद का कोई भी क्षण फिर से बना सकते हैं, सिर्फ़ वह क्षण नहीं जब backup लिया गया था, और बिना परखा restore सत्यापित backup नहीं है |
| [0012](lessons/0012-configuration-and-memory-tuning.md) | Configuration और Memory Tuning | shared_buffers, work_mem और maintenance_work_mem हर एक memory के अलग सवाल का उत्तर देता है, और सबसे अक्सर ग़लत tune होने वाला वही है जो चुपचाप उतने गुना हो जाता है जितने operations असल में एक साथ चल रहे हों |
| [0013](lessons/0013-monitoring-activity-statements-and-the-log.md) | Monitoring: Activity, Statements, और Log | इस समय हर backend क्या कर रहा है उसका live दृश्य, समय के साथ server को असल में सबसे ज़्यादा क्या पड़ रहा है उसका कुल दृश्य, और ऐसा log जो ठीक-ठीक बताए कि अटकी query किसके पीछे रुकी है, ये तीन अलग सवाल हैं |
| [0014](lessons/0014-connection-management-and-pgbouncer.md) | Connection Management और PgBouncer | हर Postgres connection एक पूरा OS process है, इसीलिए pooler आम तौर पर ज़रूरी होता है, और PgBouncer के तीनों pooling modes हर एक session-स्तर की सही कार्यप्रणाली को reuse की कुशलता के बदले अलग ढंग से देते हैं |
| [0015](lessons/0015-logical-replication-publications-and-subscriptions.md) | Logical Replication, Publications, और Subscriptions | Streaming replication पूरे cluster की हूबहू प्रति बनाने के लिए कच्चा WAL भेजता है; logical replication उन्हीं बदलावों को row-स्तर के events में decode करता है जिन्हें subscriber चुनिंदा ढंग से, major versions के पार, लागू कर सकता है, इस क़ीमत पर कि वह DDL को अपने-आप कभी replicate नहीं करता |
| [0016](lessons/0016-major-version-upgrades-and-pg-upgrade.md) | Major-Version Upgrades और pg_upgrade | pg_upgrade के सबसे तेज़ transfer modes अपनी रफ़्तार आसानी से revert करने की क्षमता छोड़कर पाते हैं, और logical replication सचमुच अलग सौदा देता है, लगभग शून्य downtime, इस क़ीमत पर कि पूरे migration में DDL हाथ से संभालना पड़ता है |
| [0017](lessons/0017-roles-privileges-and-row-level-security.md) | Roles, Privileges, और Row-Level Security | Table-स्तर के GRANTs और row-level security authorization की दो अलग परतें हैं, और RLS चालू करने से table owner पर तब तक पाबंदी नहीं लगती जब तक आप उसे साफ़ तौर पर ऐसा करने को न कहें |
| [0018](lessons/0018-partitioning-and-toast.md) | Partitioning और TOAST | Partitioning पूरी table के scan को सिर्फ़ संबंधित partitions के scan में बदल देता है और bulk deletion को bloat-मुक्त बनाता है, जबकि TOAST वह कारण है जिससे एक अकेली row 8kB page से कहीं बड़ा मान रख सकती है |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत
- [Vacuum और Bloat](reference/vacuum-and-bloat.md): autovacuum किन संख्याओं के साथ क्या चीज़ trigger करती है, उसके वापस पाए जा सकने वाले space को क्या रोकता है, और कौन-से views किस क्रम में जाँचें
- [Replication](reference/replication.md): slot क्या गारंटी देता है और किस जोखिम में डालता है, पाँच synchronous स्तर और कब उनमें से तीन कुछ नहीं करते, और दो lags के साथ वे columns जो उन्हें अलग करते हैं
- [Index Maintenance](reference/index-maintenance.md): हर index type प्रति write क्या वसूलता है और उसे क्या बिगाड़ता है, और वे parameters और memory cliff जो pgvector index अपने साथ लाता है
- [Managed बनाम Self-Hosted](reference/managed-vs-self-hosted.md): managed service क्या automate करती है और क्या सिर्फ़ दूसरी जगह खिसकाती है, तीन high-availability रूप जो आपस में बदले नहीं जा सकते, और वे निर्णय जिनका नाम सही ठहराए गए डिज़ाइन को लेना होता है

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
