---
title: Go
description: "Team में Go को अपने हाथ में लें: production service डिज़ाइन, ship और संचालित करें"
type: topic
---

# सीखना: Go

वह engineer बनें जिस पर team में Go की ज़िम्मेदारी के लिए भरोसा किया जाए: production Go service डिज़ाइन, ship और संचालित कर सकें, किसी और के Go की समीक्षा कर सकें और ठोस रूप से बता सकें कि कोई design ग़लत क्यों है, और पहचान सकें कि कब किसी दूसरी भाषा से लाया गया design Go का इस्तेमाल करने के बजाय उससे लड़ रहा है।

**नवीनतम पाठ:** [0041. असली Database के सामने Testing](lessons/0041-testing-against-a-real-database.md)

## सफलता कैसी दिखती है

- Production service डिज़ाइन और ship करें: config, structured logging, graceful shutdown, health checks, database access।
- `-race` और `pprof` का इस्तेमाल करके ऐसे code में data race और goroutine leak को debug करें जो आपने नहीं लिखा।
- किसी साथी का PR review करें और सटीक रूप से बताएँ कि वहाँ interface, pointer receiver, या channel ग़लत औज़ार क्यों है।
- किसी concurrent program के चलने से पहले, प्रयोग के बजाय scheduler और memory model के आधार पर, अनुमान लगाएँ कि वह क्या करेगा।
- अंदाज़े से नहीं, `pprof` और `benchstat` के सबूत से allocations घटाएँ।
- ऐसी package API डिज़ाइन करें जिसे आप backwards-compatible रख सकें, और जानें कि कब goroutine *नहीं* उठानी है।

## सीमाएँ

- Go का कोई पूर्व अनुभव नहीं माना गया है। किसी दूसरी भाषा का अनुभव शुरुआती चरणों को छोटा कर देता है पर ज़रूरी नहीं है, और वह ऐसी आदतें लाता है जिनकी सज़ा Go चुपचाप देगा, क्योंकि यहाँ ग़लत सहज समझ भी compile हो जाती है।
- किसी भी supported OS पर सिर्फ़ standard toolchain चाहिए। चरण 5 तक किसी चीज़ के लिए paid tooling, cloud account, या दूसरी machine की ज़रूरत नहीं।
- अभ्यास छोटे programs हैं जो एक बैठक में पूरे हो जाते हैं। उन्हें कई दिनों में फैलाना ही तरीक़ा है, कोई असुविधा नहीं।
- Version पर निर्भर सामग्री जल्दी पुरानी पड़ती है। मौजूदा release के बारे में दावों को किताबों के बजाय release notes से जाँचा जाता है।

## दायरे से बाहर

- दूसरी भाषाएँ अपने-आप में विषय के रूप में। तुलनाएँ सिर्फ़ वहीं आती हैं जहाँ वे किसी आदत को Go में ले जाने से रोकती हैं।
- Third-party frameworks अपने-आप में विषय के रूप में: routers, ORMs, dependency-injection containers, CLI toolkits। Standard library routing, structured logging और database access को सीधे कवर करती है, इसलिए पाठ उसी पर बनते हैं; जहाँ team पहले ही कोई framework चुन चुकी है, वहाँ यह आँकना कि वह अपनी जगह के लायक है या नहीं, समीक्षा का कौशल है और चरण 6 का हिस्सा है।
- Frontend, WASM, और mobile targets।
- Kubernetes और infrastructure, उससे आगे जो एक Go service को चलने के लिए चाहिए। Binary को container image में रखना, और उस container को चलाना, सुरक्षित करना और debug करना, [`infrastructure/containers`](../../infrastructure/containers/) है। उसे cluster पर चलाना, जिसमें यह भी शामिल है कि cluster उसके health checks और shutdown signal के साथ क्या करता है, [`infrastructure/kubernetes`](../../infrastructure/kubernetes/) है।
- Compiler और runtime के भीतरी हिस्से, उस बिंदु से आगे जहाँ वे program के व्यवहार का अनुमान लगाने में मदद करना बंद कर देते हैं।

## पूरी रूपरेखा

सात चरण, शून्य से senior तक। यह पाठों की सूची नहीं है: एक चरण में कई पाठ लगते हैं, और सीमाएँ लचीली हैं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. नींव | 0001 से 0007 | Types, zero values, value बनाम pointer semantics, aliasing समेत slice और map की कार्यप्रणाली, strings बनाम runes बनाम bytes, package की बुनियादी बातें | Code चलाए बिना aliasing और copy व्यवहार का अनुमान लगा सकें |
| 2. Idiom | 0008 से 0014 | Values के रूप में errors, `%w` से wrapping, `errors.Is`/`As`, interface की निहित पूर्ति, छोटे interfaces, struct embedding, package layout और naming | ऐसा Go लिखें जिसे reviewer "Go syntax में Java" न कहे |
| 3. Concurrency | 0015 से 0021 | Goroutines, channels, `select`, `sync` primitives, `context` cancellation, `errgroup`, race detector, memory model, leak patterns | अनजान code में leak और race ढूँढ सकें और वह गारंटी समझा सकें जो टूटी |
| 4. Production | 0022 से 0027 | HTTP services, config, `slog`, graceful shutdown, health checks, database access, generics वहाँ जहाँ वे अपनी जगह के लायक हों | ऐसी service की संरचना बना चुके हों जो संचालन में टिकी रहे; चरण 7 इसे metrics, tracing, और सिर्फ़ functions के नहीं बल्कि handlers और database के इर्द-गिर्द tests से पूरा करता है |
| 5. Performance और tooling | 0028 से 0033 | Table-driven tests, fuzzing, benchmarks, `pprof`, escape analysis, allocation में कमी, modules और versioning, release builds | Profile से optimise करें और `benchstat` से जीत साबित करें |
| 6. विवेक | 0034 से 0037 | API design और compatibility, कब goroutine का इस्तेमाल *नहीं* करना है, समीक्षा, जवाबों के लिए stdlib का source पढ़ना | निर्णय लेने और उसे किसी और को समझाने के लिए भरोसेमंद |
| 7. Production Observability और Testing | 0038 से 0041 | Middleware और request-scoped values, metrics और tracing (RED/USE, OpenTelemetry), HTTP handler की testing, असली database के सामने integration testing | ऐसी service ship करें जिसमें वे तीसरा और चौथा संकेत हों जिनसे चरण 4 पहले रुक गया था: metrics, tracing, और सिर्फ़ functions के नहीं बल्कि handlers और database के इर्द-गिर्द tests |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-values-and-the-zero-value.md) | Values और Zero Value | हर घोषित variable पहले से इस्तेमाल योग्य है, और nil अनुपस्थिति नहीं बल्कि एक value है |
| [0002](lessons/0002-value-semantics-and-pointers.md) | Value Semantics और Pointers | हर assignment और हर argument एक copy है, और pointer इससे बाहर निकलने का तरीक़ा है |
| [0003](lessons/0003-slices-and-the-backing-array.md) | Slices और Backing Array | Slice ऐसे array पर तीन-word का header है जिसे कोई और भी पकड़े हो सकता है |
| [0004](lessons/0004-maps-and-their-rules.md) | Maps और उनके नियम | Comma-ok, unaddressable elements, randomised iteration, और साझा map से होने वाली fatal error |
| [0005](lessons/0005-strings-bytes-and-runes.md) | Strings, Bytes और Runes | String अपरिवर्तनीय UTF-8 bytes है, इसलिए len characters की गिनती नहीं है और indexing character नहीं देती |
| [0006](lessons/0006-methods-and-method-sets.md) | Methods और Method Sets | आप कौन-सा receiver चुनते हैं, यह तय करता है कि कौन-से types interface को पूरा करते हैं, सिर्फ़ यह नहीं कि कौन mutate कर सकता है |
| [0007](lessons/0007-packages-and-modules.md) | Packages और Modules | Directory एक package है, capital letter ही पूरा visibility system है, और internal लागू होता है |
| [0008](lessons/0008-errors-are-values.md) | Errors Values हैं | error एक साधारण interface है, इसलिए failures ऐसा data हैं जिसे आप संभालते हैं, बाहर निकल जाने वाला control flow नहीं |
| [0009](lessons/0009-wrapping-is-and-as.md) | Wrapping, Is और As | %w एक chain बनाता है, Is और As उसमें खोजते हैं, और wrapping एक API प्रतिबद्धता है |
| [0010](lessons/0010-defer-panic-and-recover.md) | defer, panic और recover | Arguments defer statement पर ही जम जाते हैं, और panic failures के लिए नहीं बल्कि bugs के लिए है |
| [0011](lessons/0011-implicit-interfaces.md) | Interfaces निहित रूप से पूरे होते हैं | Consumer interface घोषित करता है, implementation उसका कभी ज़िक्र नहीं करता, और छोटा होना ही मक़सद है |
| [0012](lessons/0012-the-nil-interface-trap.md) | Nil Interface का जाल | Interface एक type और एक value रखता है, इसलिए उसके भीतर nil pointer होना nil interface नहीं है |
| [0013](lessons/0013-embedding-is-not-inheritance.md) | Embedding Inheritance नहीं है | Promotion subclassing जैसा दिखता है, जब तक कोई embedded method आपके override को call करने से इनकार न कर दे |
| [0014](lessons/0014-designing-a-package.md) | Package का डिज़ाइन | Doc comments, छोटी exported सतह, और एक ही दिशा में इशारा करता dependency arrow |
| [0015](lessons/0015-goroutines-and-what-they-cost.md) | Goroutines और उनकी क़ीमत | हज़ारों शुरू करने लायक सस्ती, पर इतनी मुफ़्त कभी नहीं कि उन्हें रोकने की योजना के बिना शुरू किया जाए |
| [0016](lessons/0016-channels.md) | Channels | Unbuffered का मतलब rendezvous है, बंद करना broadcast है, और सिर्फ़ sender ही बंद कर सकता है |
| [0017](lessons/0017-select-and-timeouts.md) | select और Timeouts | एक साथ कई channels पर इंतज़ार करना, तैयार channels में से randomly चुनना, और nil से किसी case को बंद करना |
| [0018](lessons/0018-context-cancellation.md) | context और Cancellation | एक value जो deadline और रुकने का संकेत हर उस call तक ले जाती है जिसे वह छूती है |
| [0019](lessons/0019-sync-primitives.md) | sync और errgroup | कब memory साझा करना उसे पास करने से बेहतर है, और वे चार primitives जो लगभग सब कुछ कवर करते हैं |
| [0020](lessons/0020-memory-model-and-races.md) | Memory Model और Races | Data race undefined behaviour है, सिक्का उछालना नहीं, और detector सिर्फ़ वही देखता है जो चलता है |
| [0021](lessons/0021-goroutine-leaks.md) | Goroutine Leaks | हमेशा के लिए blocked goroutine कभी collect नहीं होती, और न ही वह कुछ जो वह पकड़े हुए है |
| [0022](lessons/0022-an-http-server.md) | संचालन लायक HTTP Server | Handlers, routing patterns और वे चार timeouts जो default server सेट नहीं करता |
| [0023](lessons/0023-configuration-and-startup.md) | Configuration और Startup | ऐसा main जो सिर्फ़ जोड़ता है, ऐसा run function जो error लौटाता है, और पहली request से पहले validation |
| [0024](lessons/0024-structured-logging-with-slog.md) | slog के साथ Structured Logging | Key-value attributes, dependency के रूप में पास किया गया एक logger, और ऐसे levels जिन्हें आप deploy के बिना बदल सकें |
| [0025](lessons/0025-graceful-shutdown.md) | Graceful Shutdown और Health | Signal पकड़ें, स्वीकार करना बंद करें, चल रहे काम को drain करें, फिर dependencies को क्रम से बंद करें |
| [0026](lessons/0026-talking-to-a-database.md) | Database से बात करना | sql.DB एक pool है, हर call context लेती है, और बंद न किया गया Rows एक connection पकड़े रहता है |
| [0027](lessons/0027-generics-that-earn-their-keep.md) | अपनी जगह के लायक Generics | Type parameters types के बीच दोहराव हटाते हैं, और व्यवहार के लिए interface अब भी सही जवाब है |
| [0028](lessons/0028-table-driven-tests.md) | Table-Driven Tests | एक test function, cases की एक slice, ऐसे subtests जो अपना नाम ख़ुद रखते हैं और स्वतंत्र रूप से fail होते हैं |
| [0029](lessons/0029-fuzzing.md) | Fuzzing | ऐसी property बताएँ जो हमेशा सही रहनी चाहिए, फिर toolchain को वह input खोजने दें जो उसे तोड़ता है |
| [0030](lessons/0030-benchmarks-you-can-trust.md) | भरोसे लायक Benchmarks | b.Loop, बार-बार runs और benchstat, क्योंकि एक run की एक संख्या माप नहीं है |
| [0031](lessons/0031-reading-a-pprof-profile.md) | pprof Profile पढ़ना | एक भी line बदलने से पहले पता लगाएँ कि समय और memory असल में कहाँ जा रहे हैं |
| [0032](lessons/0032-escape-analysis-and-allocation.md) | Escape Analysis और Allocation | कोई value heap पर क्यों पहुँचती है, compiler से कैसे पूछें, और कौन-से सुधार सचमुच फ़ायदा देते हैं |
| [0033](lessons/0033-modules-and-release-builds.md) | Modules और Release Builds | Minimal version selection, v2 path नियम, और वे flags जो binary को reproducible बनाते हैं |
| [0034](lessons/0034-api-design-and-compatibility.md) | API Design और Compatibility | Callers को तोड़े बिना आप क्या जोड़ सकते हैं, और वे तीन बदलाव जो हमेशा तोड़ते हैं |
| [0035](lessons/0035-when-not-to-use-a-goroutine.md) | कब Goroutine का इस्तेमाल न करें | Concurrency एक संरचना है, रफ़्तार बढ़ाने का तरीक़ा नहीं, और क्रमिक version अक्सर सही जवाब होता है |
| [0036](lessons/0036-reviewing-go.md) | Go की समीक्षा | Style tools को ढूँढने दें, अपना ध्यान lifecycle, सीमाओं और उस पर लगाएँ जो compiler नहीं जाँच सकता |
| [0037](lessons/0037-reading-the-standard-library.md) | Standard Library पढ़ना | Source आपकी machine पर है, वह ऐसी बहसें सुलझाता है जो docs नहीं सुलझा सकते, और वही style reference है |
| [0038](lessons/0038-middleware-and-request-scoped-values.md) | Middleware और Request-Scoped Values | पाठ 22 ने एक middleware को context में value लिखते दिखाया था; यह पाठ दूसरा आधा है, उसे सुरक्षित ढंग से वापस पढ़ना, और वह तंत्र जिसकी उस उदाहरण को कभी ज़रूरत नहीं पड़ी, ऐसा middleware जो अगले handler को call ही न करने का निर्णय ले |
| [0039](lessons/0039-metrics-and-tracing.md) | Metrics और Tracing | pprof एक process के अपने CPU और memory को local रूप से profile करता है; metrics और tracing वे दो production संकेत हैं जो सवालों की एक अलग जोड़ी का उत्तर देते हैं: service इस समय कुल मिलाकर कैसी चल रही है, और इस एक request के साथ उन सभी services में क्या हुआ जिन्हें उसने छुआ |
| [0040](lessons/0040-testing-an-http-handler.md) | HTTP Handler की Testing | पाठ 22 ने चलते-चलते बताया था कि ResponseRecorder handler को बिना network के testable बनाता है; यह पाठ उस दावे को ठोस बनाता है, बताता है कि interface seam ही इसे संभव क्यों बनाती है, और handler के बजाय client को test करने का वह अलग औज़ार दिखाता है जिससे यह आसानी से उलझ जाता है |
| [0041](lessons/0041-testing-against-a-real-database.md) | असली Database के सामने Testing | यह चरण 7 का capstone है: testing.Short() धीमे database test को तेज़ local loop से बाहर रखता है, शुरू किया गया और कभी commit न किया गया transaction हर test को साफ़, अलग-थलग शुरुआत देता है, और एक integration test आख़िरकार middleware, handler और असली database को साथ चलाता है |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत, हर एक के साथ टिप्पणी कि वह क्या कवर करता है
- [Slices और Maps](reference/slice-and-map-mechanics.md): aliasing, capacity, और वे operations जो panic करते हैं
- [Error Handling](reference/error-handling.md): wrapping verbs, matching functions, और वे जाल जो compile हो जाते हैं
- [Concurrency Patterns](reference/concurrency-patterns.md): channel के नियम, context constructors, leak checklist
- [Toolchain Commands](reference/toolchain-commands.md): test, benchmark, profile और release-build flags
- [समीक्षा Checklist](reference/review-checklist.md): tools क्या पकड़ते हैं और आपको क्या पकड़ना है

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
