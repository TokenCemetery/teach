---
title: Java
description: "Java service को अपने हाथ में लें: उसे modern Java में model करें, फिर JVM उसके साथ जो करता है उसे संचालित करें"
type: topic
---

# सीखना: Java

वह engineer बनें जिस पर team में Java service की ज़िम्मेदारी के लिए भरोसा किया जाए: domain को उन inheritance hierarchies के बजाय modern Java में model कर सकें जिनकी माँग भाषा पहले करती थी, प्रयोग के बजाय memory model से concurrency पर तर्क कर सकें, profile और garbage-collection log को पढ़कर निर्णय तक पहुँच सकें, और किसी के Java की समीक्षा करके ठोस रूप से बता सकें कि कोई abstraction उन्हें क्या क़ीमत चुकवा रहा है।

**यहाँ से शुरू करें:** [0001. References Values हैं](lessons/0001-references-are-values.md)
**नवीनतम पाठ:** [0052. Reflection और Annotations](lessons/0052-reflection-and-annotations.md)

## सफलता कैसी दिखती है

- Code चलाने से पहले अनुमान लगाएँ कि reference equality, टूटा हुआ `hashCode`, और साझा mutable field क्या करते हैं।
- Records, sealed interfaces और enums से domain को model करें, और बताएँ कि inheritance hierarchy क्यों बदतर होती।
- Java memory model की शब्दावली में बताएँ कि `synchronized`, `volatile` और concurrent collection हर एक क्या गारंटी देता है।
- Virtual threads का इस्तेमाल वहाँ करें जहाँ वे फ़ायदा दें, और बताएँ कि carrier thread को अब भी क्या block करता है।
- Garbage-collection log और profile पढ़ें, फिर default के बजाय उस सबूत से heap का आकार तय करें।
- ऐसा build ship करें जिसे कोई और चला सके: घोषित dependencies, test suite, चलने योग्य artifact।
- Pull request की समीक्षा करें और सटीक रूप से बताएँ कि वहाँ class hierarchy, checked exception, या stream chain ग़लत औज़ार क्यों है।
- भाषा की बहस को specification और उस JEP से सुलझाएँ जिसने feature पेश किया।

## सीमाएँ

- Java का कोई पूर्व अनुभव नहीं माना गया है। किसी दूसरी भाषा का अनुभव शुरुआती चरणों को छोटा कर देता है पर ज़रूरी नहीं है, और वह ऐसी आदतें लाता है जिनकी सज़ा Java चुपचाप देता है: हर field के लिए getter, एक implementation वाला interface, ऐसी class जहाँ record बेहतर कहता।
- आधार मौजूदा long-term-support release है। हर भाषा feature उस release के साथ पेश की जाती है जिसमें वह आई, क्योंकि Java code कई versions में पढ़ा जाता है और "modern Java" भी पुराना होता है।
- किसी भी supported OS पर सिर्फ़ JDK और terminal चाहिए। IDE मदद करता है पर कभी ज़रूरी नहीं, और रूपरेखा में किसी चीज़ के लिए paid tooling या cloud account की ज़रूरत नहीं।
- ज़्यादातर अभ्यास छोटे programs हैं जो एक बैठक में पूरे हो जाते हैं। चरण 6 अपवाद है: profile के लिए ऐसा program चाहिए जो profile करने लायक लंबे समय तक चले।
- Version पर निर्भर दावों को किताब के बजाय specification, API documentation और JEP index से जाँचा जाता है, क्योंकि छह महीने का release चक्र सूची की हर किताब से आगे निकल जाता है।

## दायरे से बाहर

- Frameworks अपने-आप में विषय के रूप में: Spring, Jakarta EE, Quarkus, Hibernate। यह आँकना कि कोई framework अपनी जगह के लायक है या नहीं, समीक्षा का कौशल है और चरण 7 का हिस्सा है।
- दूसरी JVM भाषाएँ: Kotlin, Scala, Clojure, Groovy।
- Android, और आम तौर पर mobile targets।
- Build tools की तुलना। रूपरेखा वे काम सिखाती है जो build को करने होते हैं और उन्हें करने के लिए एक tool का इस्तेमाल करती है, कौन-सा बेहतर है इस पर बहस नहीं करती।
- JVM के भीतरी हिस्से, उस बिंदु से आगे जहाँ वे program के व्यवहार का अनुमान लगाने में मदद करना बंद कर देते हैं: JIT implementation, bytecode engineering, garbage collector लिखना।
- Kubernetes और infrastructure, उससे आगे जो एक service को चलने के लिए चाहिए। चलने योग्य artifact को container image में रखना, और उस container को चलाना, सुरक्षित करना और debug करना, [`infrastructure/containers`](../../infrastructure/containers/) है। उसे cluster पर चलाना [`infrastructure/kubernetes`](../../infrastructure/kubernetes/) है।

## पूरी रूपरेखा

सात चरण, शून्य से senior तक। यह पाठों की सूची नहीं है: एक चरण में कई पाठ लगते हैं, और सीमाएँ लचीली हैं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. नींव | 0001 से 0006 | Primitives और references, `null`, strings और उनका pool, arrays, collections framework, `equals` और `hashCode`, `Comparable` | Code चलाए बिना identity बनाम equality और aliasing का अनुमान लगा सकें |
| 2. Modelling | 0007 से 0014 | Classes और interfaces, records, sealed types, enums, generics और erasure, pattern matching, default के रूप में immutability | सबसे पहले inheritance उठाए बिना domain को model करें |
| 3. Idiom और library | 0015 से 0021 | Exceptions और checked exceptions के साथ क्या करें, `Optional`, streams और collectors, iteration, files और IO, time API, text blocks | ऐसा Java लिखें जिसे reviewer unidiomatic न कहे |
| 4. Concurrency | 0022 से 0028 | Threads, memory model, `synchronized` और `volatile`, `java.util.concurrent`, executors, virtual threads, structured concurrency, जाल | वह गारंटी बता सकें जिसे टूटे concurrent program ने तोड़ा |
| 5. Testing और build | 0029 से 0035 | JUnit 6, parameterised tests, test doubles और कब उनका इस्तेमाल न करें, dependency declaration, reproducible चलने योग्य artifact | कोई और इसे clone, build, test और run कर सके |
| 6. Runtime | 0036 से 0042 | Memory areas, object layout और escape analysis, garbage collectors और उनके trade-offs, GC log पढ़ना, JMH, profiling, allocation में कमी | Profile से optimise करें और भरोसेमंद benchmark से जीत साबित करें |
| 7. विवेक | 0043 से 0049 | API design और backwards compatibility, deprecation, समीक्षा, जवाबों के लिए specification और JEPs पढ़ना | निर्णय लेने और उसे किसी और को समझाने के लिए भरोसेमंद; चरण 8 इसे उस तंत्र से पूरा करता है, reflection और annotations, जिससे हर आँका गया framework असल में बना था |
| 8. Modules और reflection | 0050 से 0052 | Module system, `module-info.java`, `requires` और `exports`, strong encapsulation, `jlink` और `jpackage` runtime images, reflection और annotations | Module की सीमा सोच-समझकर घोषित करें, उससे बनी runtime image ship करें, और किसी framework के अपनी जगह के लायक होने का आकलन करने से पहले पढ़ें कि उसका reflection असल में क्या छूता है |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-references-are-values.md) | References Values हैं | Variable एक primitive या reference रखता है, और हर assignment और argument उसी की copy बनाता है |
| [0002](lessons/0002-identity-and-equality.md) | Identity और Equality | == references की तुलना करता है, इसलिए strings और boxed numbers के लिए वह एक अलग सवाल का उत्तर देता है |
| [0003](lessons/0003-equals-and-hashcode.md) | equals और hashCode Contract | Contract तोड़ें और hash collection बिना कुछ बताए आपका object खो देता है |
| [0004](lessons/0004-null.md) | null और वह कहाँ से आता है | null ऐसा reference है जो किसी चीज़ की ओर इशारा नहीं करता, और इसका सुधार है उसे सीमा पर ही अस्वीकार करना |
| [0005](lessons/0005-arrays-and-collections.md) | Arrays और Collections | Arrays covariant और निश्चित आकार के हैं, और तीन list factories ऐसे ढंग से अलग हैं जिन्हें उनके नाम छिपाते हैं |
| [0006](lessons/0006-comparable-and-comparator.md) | Comparable और Comparator | Sorted collection equals के बजाय ordering इस्तेमाल करती है, इसलिए असंगत comparator data खो देता है |
| [0007](lessons/0007-classes-and-objects.md) | Classes और Objects | Class state और व्यवहार का template है, और हर field ऐसे default से शुरू होता है जो आपने नहीं लिखा |
| [0008](lessons/0008-records.md) | Records | अपरिवर्तनीय data के लिए पारदर्शी वाहक, जिसमें constructor, accessors, equals, hashCode और toString header से निकाले जाते हैं |
| [0009](lessons/0009-interfaces.md) | Interfaces | बिना state का contract, साथ में वे default methods जो उसे हर implementor को तोड़े बिना बढ़ने देते हैं |
| [0010](lessons/0010-inheritance-and-composition.md) | Inheritance और Composition | extends असल में आपको क्या देता है, और जवाब आम तौर पर superclass के बजाय field क्यों होता है |
| [0011](lessons/0011-sealed-types-and-pattern-matching.md) | Sealed Types और Pattern Matching | विकल्पों का एक बंद set, और ऐसा compiler जो जाँचता है कि आपने सबको संभाला |
| [0012](lessons/0012-enums.md) | Enums | Instances का एक निश्चित set जिसकी गारंटी भाषा देती है, हर एक पर state और व्यवहार की जगह के साथ |
| [0013](lessons/0013-generics-and-erasure.md) | Generics और Erasure | Type parameters जिन्हें compiler जाँचता है और runtime भूल जाता है, और वे wildcards जो उन्हें इस्तेमाल योग्य बनाते हैं |
| [0014](lessons/0014-immutability-as-a-default.md) | Default के रूप में Immutability | Object को बदलना असंभव बना दें और ज़्यादातर कठिन सवाल पूछे ही नहीं जाते |
| [0015](lessons/0015-exceptions.md) | Exceptions | कौन-सी failures signature में होनी चाहिए, कौन-सी stack trace में, और ऐसी सफ़ाई जो दोनों में टिकी रहे |
| [0016](lessons/0016-optional.md) | Optional | ऐसा return type जो अनुपस्थिति को contract का हिस्सा बनाता है, और वे चार जगहें जहाँ वह नहीं होना चाहिए |
| [0017](lessons/0017-streams.md) | Streams | ऐसी pipeline जो काम का वर्णन करती है, कहे जाने तक उसमें से कुछ नहीं करती, और उसे सिर्फ़ एक बार कहा जा सकता है |
| [0018](lessons/0018-collectors.md) | Collectors | Pipeline को वापस container में बदलना, और वे तीन collectors जो वहाँ throw करते हैं जहाँ आप उम्मीद नहीं करते |
| [0019](lessons/0019-files-and-paths.md) | Files और Paths | ऐसे paths जो strings नहीं हैं, ऐसे streams जिन्हें बंद करना ज़रूरी है, और ऐसा charset जो आख़िरकार रखने लायक default है |
| [0020](lessons/0020-dates-and-times.md) | Dates और Times | छह time types में से आपका असल में मतलब किससे था, और वे तीन जो समय का कोई बिंदु नहीं हैं |
| [0021](lessons/0021-strings-and-text.md) | Strings और Text | Text blocks, वह formatting जो आपको इस्तेमाल करनी चाहिए, और length characters की संख्या क्यों नहीं है |
| [0022](lessons/0022-threads.md) | Threads | Thread एक scheduled call stack है, और इस चरण की लगभग हर ग़लती उसे मुफ़्त मानने से शुरू होती है |
| [0023](lessons/0023-the-memory-model.md) | Memory Model | एक thread का लिखा मान दूसरा thread शायद कभी क्यों न देखे, और वह सटीक नियम जो इसे ठीक करता है |
| [0024](lessons/0024-mutual-exclusion.md) | Mutual Exclusion | एक समय में एक thread, इसे कहने के दो तरीक़े, और वह deadlock जिसे आप होने से पहले ढूँढ सकते हैं |
| [0025](lessons/0025-concurrent-collections-and-atomics.md) | Concurrent Collections और Atomics | वे collections जो concurrent access में टिकी रहती हैं, और वह check-then-act जो उनमें से हर एक को हरा देता है |
| [0026](lessons/0026-executors-and-futures.md) | Executors और Futures | Threads बनाने के बजाय काम submit करें, और वह exception ढूँढें जिसे submit निगल गया |
| [0027](lessons/0027-virtual-threads.md) | Virtual Threads | इतने सस्ते threads कि वे block हो सकें, और pooling की वह आदत जिसे अब आपको भूलना होगा |
| [0028](lessons/0028-choosing-a-model.md) | Model चुनना | एक सवाल model चुनता है, और आपके सामने की failure उस गारंटी का नाम बताती है जिसे उसने तोड़ा |
| [0029](lessons/0029-your-first-test.md) | आपका पहला Test | Tests कहाँ रहते हैं, runner असल में क्या करता है, और वह version scheme जिसे हर लेख ग़लत बताता है |
| [0030](lessons/0030-assertions-that-name-the-failure.md) | Failure का नाम बताने वाले Assertions | Fail होता test एक bug report है, और आपका चुना assertion तय करता है कि वह report कितनी अच्छी है |
| [0031](lessons/0031-parameterised-tests.md) | Parameterised Tests | एक test method, कई cases, और वह रेखा जहाँ test के भीतर loop काफ़ी नहीं रह जाता |
| [0032](lessons/0032-test-doubles.md) | Test Doubles | पाँच तरह के स्थानापन्न, कब असली object उन सबसे बेहतर है, और mock चुपचाप क्या test करना बंद कर देता है |
| [0033](lessons/0033-declaring-dependencies.md) | Dependencies घोषित करना | Coordinates, scopes और transitive graph, साथ में वह version जो बिना माँगे आ जाता है |
| [0034](lessons/0034-the-build-lifecycle.md) | Build Lifecycle | रटी हुई commands के बजाय phases और goals, और वह wrapper जो build को हर जगह एक जैसा बनाता है |
| [0035](lessons/0035-a-runnable-artifact.md) | चलने योग्य Artifact | आपने जो build किया उसे ऐसे package करना कि सिर्फ़ JDK वाला कोई भी उसे चला सके |
| [0036](lessons/0036-where-memory-goes.md) | Memory कहाँ जाती है | वे पाँच जगहें जहाँ JVM memory रखता है, और कौन-सा OutOfMemoryError किसका नाम लेता है |
| [0037](lessons/0037-the-shape-of-an-object.md) | Object का आकार | छोटा object ज़्यादातर header है, और उसे छोटा करने वाला flag default रूप से बंद है |
| [0038](lessons/0038-the-allocation-that-never-happened.md) | वह Allocation जो कभी हुआ ही नहीं | Escape analysis किसी allocation को पूरी तरह हटा सकता है, और एक field store उसे वापस ले आता है |
| [0039](lessons/0039-collectors-and-the-trade.md) | Collectors और आपका किया सौदा | पाँच collectors, एक तीन-तरफ़ा सौदा, और default आम तौर पर सही जवाब क्यों होता है |
| [0040](lessons/0040-reading-a-gc-log.md) | Garbage Collection Log पढ़ना | Log की एक line बताती है कि कितना collect हुआ, कितना समय लगा, और परवाह करनी है या नहीं |
| [0041](lessons/0041-a-benchmark-you-can-trust.md) | भरोसे लायक Benchmark | स्पष्ट timing loop झूठ क्यों बोलता है, और वह harness setup जो चुपचाप कुछ भी नहीं मापता |
| [0042](lessons/0042-from-profile-to-proof.md) | Profile से Proof तक | Run record करें, पढ़ें कि समय कहाँ गया, एक चीज़ बदलें, और जीत साबित करें |
| [0043](lessons/0043-what-counts-as-breaking.md) | Breaking किसे गिनते हैं | तीन तरह की compatibility, और वह बदलाव जिसके सामने compile करना सुरक्षित है और चलाना घातक |
| [0044](lessons/0044-designing-a-signature.md) | Signature का डिज़ाइन | Parameter और return types तय करते हैं कि callers क्या कर सकते हैं, और ज़्यादातर नुक़सान सीमा पर होता है |
| [0045](lessons/0045-evolving-a-type.md) | Type को तोड़े बिना आगे बढ़ाना | लोगों के निर्भर हो जाने के बाद interface, record, enum और sealed hierarchy में कुछ कैसे जोड़ें |
| [0046](lessons/0046-deprecation-that-works.md) | काम करने वाला Deprecation | किसी चीज़ को deprecated चिह्नित करने से कुछ नहीं बदलता जब तक आप यह न बताएँ कि आगे क्या होगा |
| [0047](lessons/0047-settling-it-from-the-source.md) | Source से तय करना | जब बहस इस पर हो कि Java क्या करता है तो कहाँ देखें, और कौन-सा document किस सवाल का उत्तर देता है |
| [0048](lessons/0048-reviewing-java.md) | Java की समीक्षा | यह कहने के बजाय कि कुछ ग़लत लगता है, abstraction की क़ीमत का नाम लेना |
| [0049](lessons/0049-does-this-framework-earn-its-place.md) | क्या यह Framework अपनी जगह के लायक है | चरण 7 का आख़िरी निर्णय, framework के वादों के बजाय service की सीमाओं से लिया गया |
| [0050](lessons/0050-the-module-system.md) | Module System | module-info.java उस सीमा के रूप में JAR की जगह लेता है जिसे compiler और runtime दोनों पहचानते हैं, requires और exports तय करते हैं कि उसे क्या पार करता है, और strong encapsulation का मतलब है कि export न किए गए package की public class अपने module के बाहर अदृश्य है |
| [0051](lessons/0051-runtime-images.md) | Runtime Images | jlink runtime image सिर्फ़ उन modules के transitive closure से बनाता है जिनसे उसे शुरू करने को कहा जाए, पर सिर्फ़ explicit modules से, और एक भी automatic module पर निर्भर application को link ही नहीं किया जा सकता |
| [0052](lessons/0052-reflection-and-annotations.md) | Reflection और Annotations | यह चरण 8 का capstone है: reflection class के अपने आकार को compile time के बजाय run time पर पढ़ता और call करता है, annotation तब तक निष्क्रिय data है जब तक कोई उसे reflection से न पढ़े, और इस रूपरेखा का दायरे से बाहर का हर framework ठीक इन्हीं दो तंत्रों से बना है |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत, हर एक के साथ टिप्पणी कि वह क्या कवर करता है
- [Equality, hashing और ordering](reference/equality-hashing-and-ordering.md): तीन contracts, और कौन-सी तुलना लिखनी है
- [Modelling](reference/modelling.md): कौन-सा construct उठाना है, हर एक आपको किससे बाँधता है, और वे नियम जिन्हें ग़लत याद रखना आसान है
- [Idiom और library](reference/idiom-and-library.md): library के वे निर्णय जिन पर reviewer ध्यान देता है, और वे जाल जो वहाँ throw करते हैं जहाँ कोई नहीं देखता
- [Concurrency](reference/concurrency.md): हर construct कौन-सी गारंटी देता है, कौन-सा model workload में फ़िट होता है, और आपके सामने के लक्षण का क्या मतलब है
- [Testing और build](reference/testing-and-build.md): हर command असल में कौन-सा build काम करती है, कौन-सा double उठाना है, और वह failure जिसका मतलब है कि artifact ग़लत है
- [Runtime](reference/the-runtime.md): memory कहाँ जाती है, कौन-सा collector किस ज़रूरत का उत्तर देता है, और वह माप जो किसी दावे का समर्थन करता है
- [विवेक](reference/judgment.md): कौन-से बदलाव क्या तोड़ते हैं, API को कैसे retire करें, और source से निर्णय के पक्ष में तर्क कैसे दें
- [Module System](reference/the-module-system.md): चरण 8 की sheet, cross-module access की तीन शर्तों, हर directive क्या करता है, और jar का code कहाँ पहुँचता है, के साथ

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
