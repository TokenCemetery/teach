---
title: SQL
description: "Database को अपने हाथ में लें: query लिखें, plan पढ़ें, schema डिज़ाइन करें, concurrency में टिके रहें"
type: topic
---

# सीखना: SQL

वह engineer बनें जिस पर team अपने database के लिए भरोसा करे: किसी सवाल को ऐसी query के रूप में व्यक्त कर सकें जो ठीक उसी का उत्तर दे, query plan पढ़कर पता लगा सकें कि वह query धीमी क्यों है, सहज समझ के बजाय सबूत से index चुन सकें, इस पर तर्क कर सकें कि concurrent transactions क्या देख सकते हैं, और ऐसा schema डिज़ाइन और migrate कर सकें जो ख़राब data को बाहर रखे और table बढ़ने पर भी तेज़ बना रहे।

**यहाँ से शुरू करें:** [0001. Tables, Rows और Types](lessons/0001-tables-rows-and-types.md)
**नवीनतम पाठ:** [0053. Triggers, Stored Procedures, और Logic कहाँ होना चाहिए](lessons/0053-triggers-stored-procedures-and-where-logic-belongs.md)

## सफलता कैसी दिखती है

- Joins, aggregation और window functions वाली ऐसी query लिखें जो पूछे गए सवाल का उत्तर दे, और समझाएँ कि परिणाम में ठीक वही rows क्यों हैं, `NULL` समेत।
- असली timings वाला execution plan पढ़ें और बताएँ कि कौन-सा step समस्या है।
- Plan और selectivity के आधार पर index चुनें या उसे अस्वीकार करें, फिर माप से फ़र्क़ साबित करें।
- बताएँ कि किसी दिए isolation level पर transaction क्या देख सकता है, और उस anomaly का नाम बताएँ जिस पर कोई concurrency bug निर्भर है।
- Keys, types और constraints का इस्तेमाल करके ऐसा schema डिज़ाइन करें जहाँ ख़राब data को हतोत्साहित नहीं, असंभव बनाया गया हो।
- Live system पर schema को बिना downtime और बिना migration के पीछे lock queue बनाए बदलें।
- ORM से generate हुई धीमी query लें, समझाएँ कि वह धीमी क्यों है, और उसे फिर से लिखें।
- किसी की query या schema की समीक्षा करें और ठोस रूप से बताएँ कि दस गुना rows पर उसकी क्या क़ीमत होगी।

## सीमाएँ

- SQL का कोई पूर्व अनुभव, और database administration का कोई अनुभव नहीं माना गया है।
- PostgreSQL reference engine है, क्योंकि उसका documentation मुफ़्त उपलब्ध सबसे पूर्ण विवरण है कि असली planner और असली concurrency model कैसे व्यवहार करते हैं। SQLite वहाँ इस्तेमाल होता है जहाँ किसी अभ्यास को server की ज़रूरत ही नहीं होनी चाहिए। जहाँ engines सचमुच अलग हैं, वहाँ पाठ यह बताता है और अगर कोई standard व्यवहार है तो उसका नाम लेता है।
- किसी भी supported OS पर सिर्फ़ local engine और terminal चाहिए। रूपरेखा में किसी चीज़ के लिए paid tooling, cloud account, या managed database की ज़रूरत नहीं।
- अभ्यासों को data चाहिए, और दस rows वाली table indexes के बारे में ग़लत सबक़ सिखाती है। रूपरेखा एक dataset इस्तेमाल करती है जो इतना बड़ा होता जाता है कि planner के चुनाव असली हों।
- Planner का व्यवहार major versions के बीच बदलता है। Version पर निर्भर दावों को मौजूदा documentation से जाँचा जाता है, और जो पाठ किसी version पर निर्भर है वह बताता है कि कौन-सा।

## दायरे से बाहर

- विषय के रूप में database administration: backups और recovery, replication, failover, connection pooling, version upgrades। [`data/postgres`](../../data/postgres/) देखें, जो चलते हुए instance का मालिक है।
- ORMs और query builders अपने-आप में विषय के रूप में। चरण 7 में उनका output पढ़ा और परखा जाता है; उन्हें configure करना नहीं सिखाया जाता।
- Deploy pipeline से migrations चलाना: migration उस code के सापेक्ष कब चलता है जिसे उसकी ज़रूरत है, और expand और contract किसी बदलाव को कई deploys में कैसे फैलाता है। यह [`infrastructure/ci-cd`](../../infrastructure/ci-cd/) है, जिसकी [Deployments](../../infrastructure/ci-cd/reference/deployments.md) sheet में migrations का क्रम है।
- Analytical warehouses और उनकी बोलियाँ: BigQuery, Snowflake, Redshift, Spark SQL। Columnar execution performance की सलाह बदल देता है, और रूपरेखा उसके पीछे नहीं जाती। [`data/warehouses`](../../data/warehouses/) देखें, जो columnar execution और उससे बदलने वाली बातों का मालिक है।
- तुलना के लिए विकल्प के रूप में non-relational stores। जिसका अपना track है वह [`data/redis`](../../data/redis/) है।
- Engine के भीतरी हिस्से, उस बिंदु से आगे जहाँ वे query और transaction के व्यवहार को समझाना बंद कर देते हैं: on-disk formats, write-ahead log के भीतरी हिस्से, planner का source code।

## पूरी रूपरेखा

सात चरण, शून्य से senior तक। यह पाठों की सूची नहीं है: एक चरण में कई पाठ लगते हैं, और सीमाएँ लचीली हैं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. Relational model | 0001 से 0006 | Tables, rows और types, `NULL` और three-valued logic, `SELECT`, filtering, sorting, sets बनाम bags, key क्या है | बता सकें कि query ने ठीक वही rows क्यों लौटाईं, उन समेत जिन्हें `NULL` ने हटा दिया |
| 2. Querying | 0007 से 0013 | हर तरह का join, aggregation और `GROUP BY`, `HAVING`, subqueries, common table expressions, set operations | Trial and error के बिना किसी सवाल को एक query के रूप में व्यक्त करें |
| 3. बुनियादी बातों से आगे | 0014 से 0020 | Window functions और frames, lateral joins, recursive queries, `JSON` columns वहाँ जहाँ वे अपनी जगह के लायक हों | Ranking और running-total की समस्याएँ application code के बजाय SQL में सुलझाएँ |
| 4. Schema design | 0021 से 0027 | Normalisation और कब रुकना है, primary और foreign keys, constraints, सोच-समझकर types चुनना, surrogate बनाम natural keys | ख़राब data हतोत्साहित नहीं, असंभव हो |
| 5. Transactions | 0028 से 0034 | चार अलग वादों के रूप में ACID, isolation levels और हर एक जो anomalies होने देता है, multiversion concurrency control, locking, deadlocks, explicit row locks, idempotency | Concurrency bug को reproduce करने से पहले उस anomaly का नाम बता सकें जिस पर वह निर्भर है |
| 6. Performance | 0035 से 0041 | पहले B-tree indexes और बाक़ी बाद में, selectivity और cardinality, statistics, timings वाला plan पढ़ना, join strategies, pagination, कब query समस्या नहीं है | Plan से optimise करें और माप से जीत साबित करें |
| 7. संचालन और विवेक | 0042 से 0048 | बिना downtime के migrations, queries और schemas की समीक्षा, ORM output पढ़ना, engines के पार portability, कब SQL ग़लत औज़ार है | निर्णय लेने और उसे किसी और को समझाने के लिए भरोसेमंद; चरण 8 इसे authorization और procedural-logic के उन समीक्षा सवालों से पूरा करता है जिन्हें इस चरण की अपनी checklist ने मान लिया था |
| 8. Security और विशेष औज़ार | 0049 से 0053 | SQL injection और parameterised statements, roles और least privilege, row-level security, full-text search, triggers और stored procedures | Authorization सीमा और procedural logic के किसी हिस्से की समीक्षा उतनी ही ठोस रूप से करें जितनी query या schema बदलाव की |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-tables-rows-and-types.md) | Tables, Rows और Types | Column type एक constraint है जो आपको मुफ़्त मिलता है, और ग़लत type को पलटना कठिन है |
| [0002](lessons/0002-select-and-evaluation-order.md) | SELECT और Evaluation का क्रम | Clauses उस क्रम से अलग क्रम में चलते हैं जिसमें वे लिखे जाते हैं, और यही शुरुआती लोगों की ज़्यादातर errors समझाता है |
| [0003](lessons/0003-null-and-three-valued-logic.md) | NULL और Three-Valued Logic | WHERE सिर्फ़ true रखता है, इसलिए unknown false जैसा व्यवहार करता है और NOT IN कुछ भी नहीं लौटा सकता |
| [0004](lessons/0004-sets-and-bags.md) | Sets और Bags | Table एक bag है, इसलिए duplicates असली हैं और UNION उन्हें हटाने की क़ीमत चुपचाप चुकाता है |
| [0005](lessons/0005-sorting-and-collation.md) | Sorting और Collation | Text का क्रम collation पर निर्भर है, और unique key के बिना बराबरी स्थिर नहीं है |
| [0006](lessons/0006-keys-and-constraints.md) | Keys और Constraints | Key एक दावा है जिसे database लागू करता है, और जो भी दावा आप छोड़ देते हैं वह bug बन जाता है |
| [0007](lessons/0007-joins-and-what-they-do.md) | Joins, और Join असल में क्या करता है | Join एक filter किया गया cross product है, इसलिए ON शर्त बाक़ी कुछ भी चलने से पहले तय करती है कि कौन-सी rows मौजूद हैं |
| [0008](lessons/0008-outer-joins-and-missing-rows.md) | Outer Joins और वे Rows जो वहाँ नहीं हैं | Outer join उन rows को रखता है जो किसी से match नहीं हुईं, और एक WHERE clause उन्हें चुपचाप फिर फेंक देता है |
| [0009](lessons/0009-aggregation-and-group-by.md) | Aggregation और GROUP BY | Aggregates NULL को अनदेखा करते हैं और rows को गुणा करने वाला join कुल योग को भी गुणा कर देता है |
| [0010](lessons/0010-having-and-filter.md) | HAVING, FILTER और एक साथ कई Groupings | कोई शर्त कहाँ होनी चाहिए यह तय करता है कि वह अब भी कौन-सी rows देख सकती है, और एक pass कई groupings का उत्तर दे सकता है |
| [0011](lessons/0011-subqueries.md) | Subqueries, और कौन-सा प्रकार सवाल का उत्तर देता है | Scalar, IN, EXISTS और derived table चार अलग सवालों के उत्तर देते हैं, और उनमें से एक NULL आने पर झूठ बोलता है |
| [0012](lessons/0012-common-table-expressions.md) | Common Table Expressions | WITH एक step को नाम देता है ताकि लंबी query ऊपर से नीचे पढ़ी जाए, और इस release पर वह optimisation fence नहीं है |
| [0013](lessons/0013-set-operations.md) | Set Operations, और एक सवाल एक Query के रूप में | UNION, INTERSECT और EXCEPT result sets को position से जोड़ते हैं और duplicates हटाते हैं जब तक उन्हें ऐसा न करने को कहा जाए |
| [0014](lessons/0014-window-functions.md) | Window Functions | Window function दूसरी rows के पार compute करता है, उस row को समेटे बिना जिस पर वह है |
| [0015](lessons/0015-window-frames.md) | Window Frames | Default frame में हर वह row शामिल है जो मौजूदा row के बराबर है, इसीलिए running total उछल सकता है |
| [0016](lessons/0016-navigating-within-a-window.md) | Window के भीतर Navigation | lag, lead और value functions सीधे दूसरी rows तक पहुँचते हैं, और उनमें से दो frame का पालन करते हैं |
| [0017](lessons/0017-lateral-joins.md) | Lateral Joins | LATERAL FROM में subquery को बगल की row देखने देता है, और हर group के शीर्ष कुछ ऐसे ही लिए जाते हैं |
| [0018](lessons/0018-recursive-queries.md) | Recursive Queries | Recursive CTE अपना output तब तक वापस अपने में डालता है जब तक कुछ नया न निकले, और hierarchy ऐसे ही तय की जाती है |
| [0019](lessons/0019-json-columns.md) | JSON Columns | Document column को query करना साधारण SQL है, एक बार आप जान लें कि कौन-सा operator text लौटाता है और कौन-सा JSON |
| [0020](lessons/0020-choosing-the-tool.md) | औज़ार चुनना | Top-N, running totals और deduplication, हर एक को लिखने के दो या तीन सही तरीक़े हैं, और चुनाव इस पर है कि सवाल क्या पूछता है |
| [0021](lessons/0021-normalisation.md) | Normalisation | हर normal form उस एक तरीक़े को हटाता है जिससे दो rows एक ही तथ्य पर असहमत हो सकती हैं |
| [0022](lessons/0022-choosing-a-key.md) | Key चुनना | Surrogate key स्थिरता देती है और अर्थ छोड़ देती है, और आपका चुना generator तय करता है कि उसकी और क्या क़ीमत है |
| [0023](lessons/0023-foreign-keys.md) | Foreign Keys और Delete पर क्या होता है | Foreign key मौजूद rows के बारे में एक वादा है, और आपका चुना action तय करता है कि किसी के जाने पर क़ीमत कौन चुकाता है |
| [0024](lessons/0024-constraints-that-hold.md) | Constraints जो सचमुच टिकें | CHECK सिर्फ़ तब fail होता है जब उसकी शर्त false हो, इसलिए अनुपस्थित value आपके लिखे लगभग हर नियम को पूरा कर देती है |
| [0025](lessons/0025-choosing-types.md) | सोच-समझकर Types चुनना | Type तय करता है कि database क्या स्वीकार करेगा, क्या चुपचाप बदल देगा, और क्या कभी वापस नहीं ले सकता |
| [0026](lessons/0026-denormalising-on-purpose.md) | जानबूझकर Denormalise करना | किसी तथ्य की दूसरी copy ग़लत होने का दूसरा मौक़ा है, जब तक उसे database ख़ुद न संभाल रहा हो |
| [0027](lessons/0027-making-bad-data-impossible.md) | ख़राब Data को असंभव बनाना | ग़लत row की अनुमति देने वाला schema लें और हर कमी बंद करें, फिर बताएँ कि design अब भी क्या वादा नहीं कर सकता |
| [0028](lessons/0028-what-a-transaction-promises.md) | Transaction क्या वादा करता है | एक संक्षिप्त नाम के तहत चार वादे चलते हैं, और उनमें से सिर्फ़ एक पर आप मोलभाव कर सकते हैं |
| [0029](lessons/0029-mvcc.md) | Multiversion Concurrency Control | Update row को बदलने के बजाय नया row version लिखता है, इसीलिए reader कभी writer का इंतज़ार नहीं करता |
| [0030](lessons/0030-isolation-levels.md) | Isolation Levels | PostgreSQL चार नामों के तहत आपको तीन अलग levels देता है, और हर एक अलग तरह के अचंभों की अनुमति देता है |
| [0031](lessons/0031-the-anomalies.md) | Anomalies, और अपनी Anomaly कैसे पहचानें | हर concurrency bug का एक नाम है, और उसका नाम लेना आपको बताता है कि कौन-सा level या lock उसे रोक देता |
| [0032](lessons/0032-locks.md) | जानबूझकर लिए गए Locks | Row lock वह तरीक़ा है जिससे आप किसी निर्णय को स्थिर रखते हैं, और उनमें से हर एक का एक failure mode है जिसे सोच-समझकर चुनना चाहिए |
| [0033](lessons/0033-deadlocks.md) | Deadlocks | दो transactions, हर एक वह पकड़े हुए जो दूसरे को चाहिए, और इसका एकमात्र इलाज पहले से एक क्रम पर सहमत होना है |
| [0034](lessons/0034-idempotency-and-retry.md) | Idempotency और सही Retry | वही statements दोहराने वाला retry वही bug फिर पैदा करता है जिसे ठीक करने के लिए वह था, इसलिए उसे फिर से पढ़ना और फिर से तय करना होता है |
| [0035](lessons/0035-reading-a-plan.md) | Plan पढ़ना | Plan बताता है कि database ने क्या किया और उसे क्या उम्मीद थी, और दोनों के बीच का अंतर ही वह जगह है जहाँ काम है |
| [0036](lessons/0036-what-an-index-does.md) | Index असल में क्या करता है | B-tree हर row के scan को कुछ pages नीचे की सैर में बदल देता है, और plan बताता है कि उसने चार में से किस तरीक़े से उन्हें पढ़ा |
| [0037](lessons/0037-selectivity-and-statistics.md) | Selectivity और Statistics | हर plan आपके data के sample से बनता है, इसलिए ख़राब plan आम तौर पर ख़राब planner नहीं बल्कि ख़राब अनुमान होता है |
| [0038](lessons/0038-choosing-an-index.md) | Index चुनना | Columns का क्रम तय करता है कि index किन queries का उत्तर दे सकता है, और सबसे अच्छा index अक्सर वह होता है जिसे आप न बनाने का निर्णय लेते हैं |
| [0039](lessons/0039-join-strategies.md) | Join Strategies | Join के तीन तरीक़े, और planner अनुमानित क़ीमत के आधार पर चुनता है, इसलिए ग़लत अनुमान ग़लत strategy के रूप में दिखता है |
| [0040](lessons/0040-pagination-and-counting.md) | Pagination और गिनती | OFFSET हर उस row को पढ़ता और फेंकता है जिसे वह छोड़ता है, और सटीक गिनती की क़ीमत पूरी table से एक बार गुज़रना है |
| [0041](lessons/0041-when-the-query-is-not-the-problem.md) | जब Query समस्या न हो | जीत साबित करने के लिए ऐसा माप चाहिए जिसे आप दोहरा सकें, और कारण अक्सर table, traffic या client होता है |
| [0042](lessons/0042-migrations-without-downtime.md) | बिना Downtime के Migrations | एक millisecond लेने वाला migration भी table पर हर read रोक सकता है, उसकी वजह से जो उसके पीछे queue में लगता है |
| [0043](lessons/0043-changing-what-has-data.md) | जिसमें पहले से Data है उसे बदलना | भरी table पर constraint दो statements है, और backfill एक UPDATE नहीं बल्कि loop है |
| [0044](lessons/0044-reviewing-a-query.md) | Query की समीक्षा | रफ़्तार के लिए पढ़ने से पहले query को उसकी लौटाई rows के लिए पढ़ें, क्योंकि तेज़ ग़लत जवाब बदतर है |
| [0045](lessons/0045-reviewing-a-schema-change.md) | Schema बदलाव की समीक्षा | पूछें कि migration क्या lock करता है, क्या फिर से लिखता है, और जब code के दोनों versions live हों तब क्या चलता है |
| [0046](lessons/0046-portability.md) | Portability, और उसकी क़ीमत | इस रूपरेखा का ज़्यादातर हिस्सा engines के बीच चल जाता है, और जो हिस्से नहीं चलते वही ऐसे हैं जिन पर सोच-समझकर निर्भर होना चाहिए |
| [0047](lessons/0047-reading-orm-output.md) | ORM जो निकालता है उसे पढ़ना | ORM वह SQL लिखता है जो आपने नहीं लिखा, और यह जानने का एकमात्र तरीक़ा कि उसने क्या भेजा, देखना है |
| [0048](lessons/0048-trusted-with-the-database.md) | Database के लिए भरोसेमंद | सात चरण एक आदत पर ख़त्म होते हैं: उस row, lock या plan का नाम लेना जो किसी निर्णय को बचाव योग्य बनाता है |
| [0049](lessons/0049-sql-injection-and-parameterised-statements.md) | SQL Injection और Parameterised Statements | String concatenation किसी value को यह बदलने देता है कि statement का मतलब क्या है, सिर्फ़ यह नहीं कि वह किससे match करता है, और parameterised statement हर case को साफ़ करने की कोशिश के बजाय उस संभावना को ही हटा देता है |
| [0050](lessons/0050-roles-and-least-privilege.md) | Roles और Least Privilege | Roles users और groups के पुराने विचारों को अपने में समेट लेते हैं, ownership बिना किसी GRANT के पहले से हर privilege देती है, और least privilege पूरी तरह इस बारे में है कि बाक़ी सबको क्या करने की अनुमति है |
| [0051](lessons/0051-row-level-security.md) | Row-Level Security | GRANT पूरी table के access का निर्णय करता है, row security policy हर row के लिए, और engine इसे हर access path पर लागू करता है, सिर्फ़ उस पर नहीं जिसे filter करना developer को याद रहा |
| [0052](lessons/0052-full-text-search.md) | Full-Text Search | tsvector document को normalized lexemes में बदल देता है जिन्हें GIN index खोज सकता है, tsquery पूछता है कि वे मौजूद हैं या नहीं, और समर्पित search engine के साथ सीमा वहाँ है जहाँ ranking और पैमाना एक column से बड़े हो जाते हैं |
| [0053](lessons/0053-triggers-stored-procedures-and-where-logic-belongs.md) | Triggers, Stored Procedures, और Logic कहाँ होना चाहिए | यह चरण 8 का capstone है: trigger table तक पहुँचने वाले हर रास्ते पर चलता है और procedure अपने transaction को commit या roll back कर सकता है, और विवेक का निर्णय यह तय करना है कि कब वह अदृश्यता सचमुच अपनी क़ीमत के लायक है |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत, हर एक के साथ टिप्पणी कि वह क्या कवर करता है
- [Dataset](reference/the-dataset.md): वह schema और data जिसे चरण 2 से आगे का हर पाठ query करता है, और उसे load कैसे करें
- [NULL और three-valued logic](reference/null-and-three-valued-logic.md): truth tables, NULL कहाँ बराबर गिना जाता है, और जाल उनके सुधारों के साथ
- [SELECT का evaluation क्रम](reference/select-evaluation-order.md): क्या कब चलता है, हर clause क्या देख सकता है, और इससे कौन-सी errors समझ आती हैं
- [Querying](reference/querying.md): चरण 2 की sheet, हर join type, हर aggregate NULL के साथ क्या करता है, और कोई शर्त कहाँ होनी चाहिए, के साथ
- [बुनियादी बातों से आगे](reference/beyond-the-basics.md): चरण 3 की sheet, window functions, frame modes, और कौन-सा औज़ार किस सवाल का उत्तर देता है, के साथ
- [Schema design](reference/schema-design.md): चरण 4 की sheet, normal forms, हर तरह के constraint, और कौन-सा type क्या अस्वीकार करता है, के साथ
- [Transactions](reference/transactions.md): चरण 5 की sheet, हर isolation level, उससे होने वाली anomalies, lock strengths, और retry योग्य errors के साथ
- [Performance](reference/performance.md): चरण 6 की sheet, plan nodes, किन संख्याओं पर भरोसा करें, scan और join strategies, और index के निर्णयों के साथ
- [Operating](reference/operating.md): चरण 7 की sheet, कौन-से migrations सुरक्षित हैं, समीक्षा के सवाल, और engines के बीच क्या चल जाता है, के साथ

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
