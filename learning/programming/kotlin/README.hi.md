---
title: Kotlin
description: "JVM पर Kotlin को अपने हाथ में लें: null safety, coroutines, और शून्य से idiomatic Kotlin"
type: topic
---

# सीखना: Kotlin

वह engineer बनें जिस पर team में Kotlin की ज़िम्मेदारी के लिए भरोसा किया जाए, चाहे backend service हो या Android app: domain को idiomatic ढंग से model कर सकें, coroutines और `Flow` लिख सकें और उन पर तर्क कर सकें, typed, tested Kotlin service या Android component ship कर सकें, और किसी के Kotlin की समीक्षा करके ठोस रूप से बता सकें कि कोई construct उन्हें क्या क़ीमत चुकवा रहा है।

**नवीनतम पाठ:** [44. runTest से आगे Coroutines की Testing](lessons/0044-testing-coroutines-beyond-runtest.md)

## सफलता कैसी दिखती है

- Data classes, sealed classes और enums से domain को model करें, और जानें कि कब exception नहीं, null safety सही संकेत है।
- Coroutines और `Flow` लिखें और उन पर तर्क करें, और model की तुलना Java virtual threads से करें।
- Typed, tested Kotlin backend service या Android component ship करें, जो idiomatic ढंग से डिज़ाइन किया गया हो।
- ऐसी आदत से लिखा Kotlin मिलने पर जो बस compile हो जाता है (type system के बजाय रक्षात्मक null checks, coroutine के बजाय callback), उस आदत का नाम बताएँ और उसे idiomatic ढंग से फिर से लिखें।

## सीमाएँ

- Kotlin का कोई पूर्व अनुभव नहीं माना गया है। Java या किसी दूसरी JVM भाषा का अनुभव शुरुआती चरणों को छोटा कर देता है पर ज़रूरी नहीं है, और वह ऐसी आदतें लाता है जिनकी सज़ा Kotlin चुपचाप देता है: type system के बजाय रक्षात्मक null checks, ऐसी class जहाँ data class या sealed type बेहतर कहता।
- Backend/server-side और Android, दोनों संदर्भ कवर होते हैं, हर एक को वहाँ छूते हुए जहाँ वे अलग होते हैं।
- सिर्फ़ JDK, Kotlin toolchain और terminal चाहिए; Android Studio सिर्फ़ वहीं जहाँ Android-विशिष्ट सामग्री को उसकी ज़रूरत हो।

## दायरे से बाहर

- JVM के भीतरी हिस्से, उससे आगे जो Kotlin के अपने compiled व्यवहार को समझाता है (garbage collector की पूरी tuning, profiling, bytecode engineering): [`programming/java`](../../programming/java/) देखें, गहराई के लिए link किया गया है, दोबारा सिखाया नहीं गया।
- दूसरी JVM भाषाएँ (Java, Scala, Clojure, Groovy) अपने-आप में विषय के रूप में, हालाँकि जहाँ किसी Kotlin idiom को स्पष्ट करने में मदद मिले वहाँ तुलना आती है।
- Kotlin Multiplatform: JS, Native, या Wasm को target करना, source sets के पार `expect`/`actual` declarations की संरचना, और वे platform-विशिष्ट stdlib फ़र्क़ जो ये targets लाते हैं। Mission के अपने ढाँचे के मुताबिक़ यह रूपरेखा पूरी तरह सिर्फ़ JVM की है; यहाँ के पाठ को अपना Gradle setup और idioms का अपना set चाहिए होगा, multiplatform footnote वाला JVM पाठ नहीं। `kotlinx.serialization` (पाठ 38) वह एकमात्र जगह है जहाँ multiplatform पहुँच का ज़िक्र है, JVM-पक्ष के design चुनाव के documented कारण के रूप में, अपने-आप में multiplatform सामग्री के रूप में नहीं।

## पूरी रूपरेखा

ग्यारह चरण, शून्य से senior तक। यह पाठों की सूची नहीं है: एक चरण में कई पाठ लगते हैं, और सीमाएँ लचीली हैं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. नींव | 0001 से 0006 | Null safety, `val`/`var` और immutability, values बनाम references, बुनियादी types और string templates, collections की बुनियादी बातें (`List`/`Set`/`Map`, mutable बनाम read-only), control flow (`when`, ranges, `for`) | Code चलाए बिना nullability और mutability का अनुमान लगा सकें |
| 2. Modelling | 0007 से 0012 | Classes और properties, data classes, sealed classes और exhaustive `when`, enums, object declarations और companion objects, default methods वाले interfaces | हर चीज़ के लिए एक class वाली hierarchy सबसे पहले उठाए बिना domain को model करें |
| 3. Idiom | 0013 से 0018 | Extension functions, scope functions (`let`/`run`/`with`/`apply`/`also`), higher-order functions और lambdas, inline functions और reified generics, delegation (`by`), operator overloading | ऐसा Kotlin लिखें जिसे reviewer अनुवाद किया हुआ Java न कहे |
| 4. Collections और sequences | 0019 से 0021 | Kotlin के collection operators, lazy `Sequence` बनाम eager collections, grouping और folding | Collection pipeline और sequence में से चुनें और हर एक की क़ीमत को सही ठहरा सकें |
| 5. Concurrency | 0022 से 0027 | Threads और JVM memory model की बुनियादी बातें, suspend functions और coroutine builders, structured concurrency, coroutine context और dispatchers, `Flow`, cancellation और exception handling | किसी concurrent coroutine program के चलने से पहले अनुमान लगा सकें कि वह क्या करेगा, और model की तुलना Java virtual threads से कर सकें |
| 6. Testing और build | 0028 से 0030 | Kotlin test frameworks, mocking, Gradle Kotlin DSL और dependency management | कोई और इसे clone, build, test और run कर सके |
| 7. Service ship करना | 0031 से 0033 | Typed, tested backend service की संरचना, जहाँ platform अलग होता है वहाँ Android-विशिष्ट idioms, generics और variance (`in`/`out`) | Typed, tested Kotlin backend service या Android component की संरचना बना चुके हों; चरण 10 इसे HTTP layer, configuration, logging और persistence से पूरा करता है |
| 8. विवेक | 0034 से 0035 | Java interop, Kotlin की समीक्षा और सटीक रूप से बताना कि कोई construct क्या क़ीमत चुकवा रहा है | निर्णय लेने और उसे किसी और को समझाने के लिए भरोसेमंद |
| 9. Advanced Idiom | 0036 से 0039 | Type-safe builders और DSLs, `value class`/`@JvmInline`, `kotlinx.serialization`, `Result` और error-handling idioms | छोटा type-safe builder DSL, zero-cost wrapper type, और `Result`-आधारित error path idiomatic ढंग से लिखें |
| 10. Service को पूरा करना | 0040 से 0043 | उस Kotlin backend service के लिए HTTP layer, configuration, logging, और persistence जिसकी संरचना चरण 7 ने शुरू की थी | ऐसी Kotlin backend service ship करें जिसमें routed HTTP layer, बाहर रखा configuration, structured logging, और database access हो, सिर्फ़ संरचित ढाँचा नहीं |
| 11. runTest से आगे Coroutines की Testing | 0044 | कभी पूरी न होने वाले flow के लिए Turbine का `cancelAndIgnoreRemainingEvents()`, और यह देखते हुए कि cancellation cooperative है, cancellation test को असल में क्या assert करना होता है | अनंत flow को अटके बिना test करें, और cancellation को सिर्फ़ `Job` flag के बजाय उसके असली, documented सबूत से test करें |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-null-safety.md) | Null Safety | "क्या यह null हो सकता है" को runtime के अचंभे से compile-time के सवाल में बदलना, और Java की आदत इसे कैसे पलट देती है |
| [0002](lessons/0002-val-var-and-immutability.md) | val/var और Immutability | val वह default क्यों है जिसका बचाव करना चाहिए, वह असल में क्या गारंटी देता है (और क्या नहीं), और आदतन var उठाने की Java वाली आदत |
| [0003](lessons/0003-values-vs-references.md) | Values बनाम References | Kotlin में == का मतलब Java से अलग क्यों है, और == लिखने की Java वाली आदत से पैदा होने वाला ख़ास bug |
| [0004](lessons/0004-basic-types-and-string-templates.md) | बुनियादी Types और String Templates | Kotlin में भाषा के स्तर पर primitives क्यों नहीं हैं, और अतिरिक्त syntax वाले concatenation के बजाय भाषा की feature के रूप में string templates |
| [0005](lessons/0005-collections-basics.md) | Collections की बुनियादी बातें | Interface से read-only collections के रूप में List, Set, और Map, और val में रखी mutable collection अब भी mutable क्यों है |
| [0006](lessons/0006-control-flow.md) | Control Flow | Values पैदा करने वाले expressions के रूप में if और when, range असल में क्या है, और code चलाए बिना nullability और mutability का अनुमान लगाने का चरण 1 का capstone |
| [0007](lessons/0007-classes-and-properties.md) | Classes और Properties | Java के getter/setter boilerplate के विकल्प के रूप में properties, और Kotlin docs ख़ुद class को आख़िर में उठाने को क्यों कहते हैं |
| [0008](lessons/0008-data-classes.md) | Data Classes | data class असल में क्या generate करती है, और वह बारीक नियम कि इसमें सिर्फ़ primary-constructor properties ही हिस्सा लेती हैं |
| [0009](lessons/0009-sealed-classes-and-exhaustive-when.md) | Sealed Classes और Exhaustive when | Hierarchy को seal करना when की exhaustiveness को हाथ से किए वादे से compiler द्वारा जाँची गई गारंटी में कैसे बदल देता है |
| [0010](lessons/0010-enums.md) | Enums | हर enum constant अपनी state और व्यवहार वाले असली object के रूप में, और ठीक-ठीक कहाँ enum sealed class से बेहतर फ़िट होता है |
| [0011](lessons/0011-object-declarations-and-companion-objects.md) | Object Declarations और Companion Objects | हाथ से implement नहीं बल्कि घोषित किए गए singletons, और Java के static members के Kotlin वाले असली विकल्प के रूप में companion objects |
| [0012](lessons/0012-interfaces-with-default-methods.md) | Default Methods वाले Interfaces | Kotlin interface व्यवहार implement क्यों कर सकता है पर state कभी नहीं रख सकता, और diamond conflict को स्पष्ट रूप से कैसे सुलझाएँ |
| [0013](lessons/0013-extension-functions.md) | Extension Functions | Inheritance के बिना किसी type में व्यवहार जोड़ना, और static-dispatch की वह पकड़ जो पहली बार सामने आने पर लोगों को गिरा देती है |
| [0014](lessons/0014-scope-functions.md) | Scope Functions | let, run, with, apply, और also में से आदत से नहीं, बल्कि इस आधार पर चुनना कि हर एक क्या लौटाता है और object को कैसे सामने रखता है |
| [0015](lessons/0015-higher-order-functions-and-lambdas.md) | Higher-Order Functions और Lambdas | असली types के रूप में function types, trailing-lambda syntax, और वह receiver तंत्र जिस पर scope functions असल में बने हैं |
| [0016](lessons/0016-inline-functions-and-reified-generics.md) | Inline Functions और Reified Generics | inline एक असली क़ीमत हटाने के लिए क्यों है, वह non-local returns क्यों संभव बनाता है, और reified type parameters सिर्फ़ inlining की वजह से ही क्यों काम करते हैं |
| [0017](lessons/0017-delegation.md) | Delegation | बिना boilerplate के, रखे गए object को आगे भेजकर interface implement करना, और by lazy और custom delegates से दोबारा इस्तेमाल होने वाला property व्यवहार |
| [0018](lessons/0018-operator-overloading.md) | Operator Overloading | निश्चित symbol mapping वाले साधारण नामित functions के रूप में operators, और उसे सिर्फ़ वहीं implement करने का असली अनुशासन जहाँ उसका मतलब वही हो जो symbol का पहले से है |
| [0019](lessons/0019-collection-operators.md) | Collection Operators | ऐसे extension functions के रूप में collection operators जो eagerly नई collection लौटाते हैं, और Java Stream की वह आदत जो उनकी chain की क़ीमत ग़लत आँकती है |
| [0020](lessons/0020-sequences-and-laziness.md) | Sequences और Laziness | वही operator chain Sequence पर अलग व्यवहार क्यों करती है, terminal operation असल में किसलिए है, और कब laziness जितना बचाती है उससे ज़्यादा ख़र्च करती है |
| [0021](lessons/0021-grouping-and-folding.md) | Grouping और Folding | fold और reduce से aggregate करना, groups बनाए बिना grouping, और pipeline की क़ीमत को सही ठहराने का चरण 4 का capstone |
| [0022](lessons/0022-threads-and-the-memory-model.md) | Threads और Memory Model | JVM पर Kotlin का अपना कोई memory model क्यों नहीं है, वे तीन constructs जिन्हें वह keywords के बजाय annotations के रूप में लिखता है, और वे दो गारंटियाँ जो val आपको नहीं देता |
| [0023](lessons/0023-suspend-functions-and-coroutine-builders.md) | Suspend Functions और Coroutine Builders | suspend असल में function के बारे में क्या बदलता है, तीन builders और हर एक क्या लौटाता है, और suspend होने वाला code अब भी ऊपर से नीचे क्यों पढ़ा जाता है |
| [0024](lessons/0024-structured-concurrency.md) | Structured Concurrency | Parent और child का वह tree जो cancellation को अनुमान योग्य बनाता है, जिस scope के आप मालिक हैं उसे cancel करना आपकी ज़िम्मेदारी क्यों है, और GlobalScope की असली क़ीमत क्या है |
| [0025](lessons/0025-coroutine-context-and-dispatchers.md) | Coroutine Context और Dispatchers | plus से जोड़े गए elements के set के रूप में context, कौन-सा dispatcher किस तरह के काम का है, और वह एक context element जो structured concurrency को चुपचाप तोड़ देता है |
| [0026](lessons/0026-flows.md) | Flows | List और sequence के बाद तीसरे asynchronous विकल्प के रूप में flow, हर collector के लिए cold का असल में क्या मतलब है, और वह context नियम जिसे flow builder runtime पर लागू करता है |
| [0027](lessons/0027-cancellation-and-exception-handling.md) | Cancellation और Exception Handling | Cancellation cooperative क्यों है और code उसे अनदेखा क्यों कर देता है, CancellationException failure क्यों नहीं है, और coroutine model की तुलना Java virtual threads से कैसे होती है |
| [0028](lessons/0028-test-frameworks.md) | Test Frameworks | वे परतें जिन पर Kotlin test असल में बैठता है, runTest का virtual time dispatcher की सीमा पर क्यों रुक जाता है, और यह test किए जा रहे code के design पर क्या थोपता है |
| [0029](lessons/0029-mocking.md) | Mocking | Final-by-default Kotlin में mocking का मतलब क्यों बदल देता है, MockK उन constructs के लिए क्या करता है जो object पर methods नहीं हैं, और कब finality बता रही है कि कोई seam ग़ायब है |
| [0030](lessons/0030-gradle-and-dependency-management.md) | Gradle और Dependency Management | Kotlin DSL के type-safe accessors और वे कहाँ ख़त्म होते हैं, Gradle configuration Maven scope क्यों नहीं है, और resolution का वह नियम जो तय करता है कि कौन-सा version classpath तक पहुँचता है |
| [0031](lessons/0031-structuring-a-service.md) | Service की संरचना | Kotlin files असल में कहाँ जाती हैं और class के भीतर क्या जाता है, और पिछले चरणों के वे चार निर्णय जो तय करते हैं कि service testable है या नहीं |
| [0032](lessons/0032-android-divergences.md) | Android के फ़र्क़ | वे scopes जिनका मालिक Android आपकी ओर से है, callee द्वारा निभाए जाने वाले contract के रूप में main-safety, और composition का lifetime lifecycle का lifetime क्यों नहीं है |
| [0033](lessons/0033-generics-and-variance.md) | Generics और Variance | Wildcards की जगह declaration-site variance, out और in असल में type parameter के बारे में क्या वादा करते हैं, और projected signature को कैसे पढ़ें |
| [0034](lessons/0034-java-interop.md) | Java Interop | सीमा असममित क्यों है, platform type की आपको क्या क़ीमत चुकानी पड़ती है और उसे कैसे चुकाएँ, और Java caller के लिए आप कौन-से annotations के ऋणी हैं |
| [0035](lessons/0035-reviewing-kotlin.md) | Kotlin की समीक्षा | रूपरेखा को समीक्षा के औज़ार में बदलना: हर आदत कौन-सी क़ीमत छिपाती है, उसका नाम लेने वाली टिप्पणी का आकार, और किसकी समीक्षा नहीं करनी है |
| [0036](lessons/0036-type-safe-builders-and-dsls.md) | Type-Safe Builders और DSLs | पाठ 15 ने receiver-style function type सिखाया था जो run और apply को this सामने रखने देता है; type-safe builder ठीक वही तंत्र है जो recursively nest किया गया है, और @DslMarker वह एक attribute है जो nested builder को चुपचाप ग़लत receiver तक पहुँचने से रोकता है |
| [0037](lessons/0037-value-classes.md) | value class और @JvmInline | value class primitive obsession का वह सुधार है जो JVM आम तौर पर आपको मुफ़्त में देता है, जिसे बिना किसी wrapper object के उसकी अपनी अंतर्निहित value के रूप में दर्शाया जाता है, सिवाय उन ख़ास, documented मामलों के जहाँ compiler को अब भी उसे box करना पड़ता है |
| [0038](lessons/0038-kotlinx-serialization.md) | kotlinx.serialization | Java की आदत ऐसी library उठाती है जो runtime पर reflection से class के आकार की जाँच करती है; kotlinx.serialization वही logic compile time पर, compiler plugin के ज़रिए, generate करता है, और ठीक यही उसे उन Kotlin targets पर काम करने देता है जिनमें runtime reflection API है ही नहीं |
| [0039](lessons/0039-result-and-error-handling.md) | Result और Error-Handling Idioms | runCatching किसी भी Throwable को Result में लपेट देता है, और coroutine के भीतर ठीक यही समस्या है, क्योंकि पाठ 27 का cooperative cancellation CancellationException के बिना पकड़े आगे बढ़ने पर निर्भर है, और runCatching उसे साधारण failure में निगल जाता है जब तक कोई caller पहले उसे स्पष्ट रूप से फिर से throw न करे |
| [0040](lessons/0040-http-layer.md) | HTTP Layer | पाठ 31 ने routing को जानबूझकर आपके चुने framework पर छोड़ दिया था; Ktor का अपना routing block पाठ 36 का type-safe builder DSL ही निकलता है जो HTTP पर लागू है, default रूप से कुछ install नहीं होता, और request-parameter निकालना चुपचाप ग़लत चीज़ bind करने के बजाय ज़ोर से fail होता है |
| [0041](lessons/0041-configuration.md) | Configuration | Service का असली व्यवहार, उसका port, उसका database URL, उसके secrets, एक भी line recompile किए बिना environments के बीच बदलना चाहिए, और Ktor की configuration file और एक ख़ास, आसानी से छूट जाने वाला substitution idiom वह तरीक़ा है जिससे default और environment override ठीक एक जगह रहते हैं |
| [0042](lessons/0042-logging.md) | Logging | SLF4J तब तक चुपचाप कुछ नहीं करता जब तक असली logging backend dependency के रूप में न जोड़ा जाए, और CallLogging की हर request वाली MDC values तब तक चुपचाप अदृश्य रहती हैं जब तक log pattern को उन्हें print करने के लिए update न किया जाए, एक ही पाठ में एक ही आकार का जाल दो बार |
| [0043](lessons/0043-persistence.md) | Persistence | Exposed का DSL एक और type-safe builder है, और नीचे ज़्यादातर blocking है, क्योंकि वह JDBC को लपेटता है; चरण 10 का capstone उस blocking काम को सही ढंग से dispatch करना है, न कि उस thread को अटका देना जो उस समय request चला रहा था, और फिर से देखना कि चरण 7 की ship की गई service को असल में शुरू से क्या चाहिए था |
| [0044](lessons/0044-testing-coroutines-beyond-runtest.md) | runTest से आगे Coroutines की Testing | पाठ 28 ने Turbine का awaitItem सिखाया था और वह hang जो कुछ भी उसे ख़त्म न करे तो होता है; यह पाठ उस flow के लिए ख़ास औज़ार कवर करता है जो अपने-आप कभी ख़त्म नहीं होता, और यह कि cancellation test को असल में क्या assert करना होता है, यह देखते हुए कि cancellation cooperative है और cancel() call होते ही हर चीज़ update नहीं करता |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत
- [Null Safety और Mutability](reference/null-safety-and-mutability.md): null safety, `val`/`var`, values बनाम references, nullability और mutability का अनुमान
- [Modelling](reference/modelling.md): data classes, sealed classes और exhaustive `when`, object declarations और companion objects, default methods वाले interfaces
- [Idiom](reference/idiom.md): extension functions, scope functions (`let`/`run`/`with`/`apply`/`also`), delegation (`by`), operator overloading
- [Collections और Sequences](reference/collections-and-sequences.md): Kotlin के collection operators, lazy `Sequence` बनाम eager collections, grouping और folding
- [Concurrency](reference/concurrency.md): suspend functions और coroutine builders, structured concurrency, coroutine context और dispatchers, `Flow`, Java virtual threads से तुलना
- [Testing और Build](reference/testing-and-build.md): Kotlin test frameworks, mocking, Gradle Kotlin DSL और dependency management
- [Service ship करना](reference/shipping-a-service.md): typed, tested backend की संरचना, Android-विशिष्ट idioms, generics और variance
- [विवेक](reference/judgment.md): Java interop, Kotlin की समीक्षा और सटीक रूप से बताना कि कोई construct क्या क़ीमत चुकवा रहा है

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
