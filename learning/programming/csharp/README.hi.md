---
title: C#
description: "C# service को अपने हाथ में लें: type system, async, और आपके लिखे code के साथ CLR क्या करता है, शून्य से"
type: topic
---

# सीखना: C\#

वह engineer बनें जिस पर team में C# service की ज़िम्मेदारी के लिए भरोसा किया जाए: struct, class और record में से सही चुनकर domain को model कर सकें, `async`/`await` लिख सकें और उस पर तर्क कर सकें, LINQ से data को सहजता से query और transform कर सकें, typed, tested ASP.NET Core backend ship कर सकें, और समझा सकें कि आपके लिखे code के साथ CLR क्या करता है।

**नवीनतम पाठ:** [45. NuGet Packaging और Versioning](lessons/0045-nuget-packaging-and-versioning.md)

## सफलता कैसी दिखती है

- Struct, class और record में से सही चुनकर domain को model करें, और CLR के असली व्यवहार के आधार पर उस चुनाव को सही ठहराएँ।
- `async`/`await` code लिखें और समझाएँ कि हर `await` पर method के execution के साथ क्या होता है।
- LINQ से data को सहजता से query और transform करें।
- Typed, tested ASP.NET Core backend service ship करें, जो C# के लिए idiomatic ढंग से डिज़ाइन की गई हो।
- ऐसी आदत से लिखा C# मिलने पर जो बस compile हो जाता है (जहाँ struct होना चाहिए वहाँ class, `async`/`await` के बजाय callback), उस आदत का नाम बताएँ और उसे idiomatic ढंग से फिर से लिखें।

## सीमाएँ

- C# का कोई पूर्व अनुभव नहीं माना गया है। किसी दूसरी object-oriented भाषा (Java, Kotlin) का अनुभव शुरुआती चरणों को छोटा कर देता है पर ज़रूरी नहीं है, और वह ऐसी आदतें लाता है जिनकी सज़ा C# चुपचाप देता है: जहाँ struct या record होना चाहिए वहाँ class, जहाँ `async`/`await` बेहतर पढ़ा जाता वहाँ callback।
- ASP.NET Core / backend service का संदर्भ; उस फ़ोकस के बिना आम .NET नहीं।

## दायरे से बाहर

- C# के साथ Unity और game development: इतना अलग संदर्भ कि यहाँ कवर नहीं होता।
- JIT के भीतरी हिस्से, और garbage collector लिखना या हाथ से tune करना: चरण 8 generational heap, GC modes और profiling को उस स्तर पर कवर करता है जिस पर service के मालिक को किसी चुनाव को मापना और सही ठहराना होता है, उसे implement करने के स्तर पर नहीं।
- Container images: publish की गई service को image में रखना, और उस container को चलाना, सुरक्षित करना और debug करना, [`infrastructure/containers`](../../infrastructure/containers/) है।
- Service को cluster पर चलाना, जिसमें यह भी शामिल है कि Kubernetes उसके liveness और readiness checks के साथ क्या करता है, [`infrastructure/kubernetes`](../../infrastructure/kubernetes/) है।

## पूरी रूपरेखा

ग्यारह चरण, शून्य से senior तक। यह पाठों की सूची नहीं है: एक चरण में कई पाठ लगते हैं, और सीमाएँ लचीली हैं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. नींव | 0001 से 0006 | Value types बनाम reference types (struct बनाम class), nullable value types, बुनियादी types और string interpolation, collections (`List`, `Dictionary`, `IEnumerable`), control flow, exceptions | Code चलाए बिना copy-बनाम-reference व्यवहार का अनुमान लगा सकें |
| 2. Modelling | 0007 से 0011 | Properties, `record` types, pattern matching और switch expressions, default implementations वाले interfaces, generics | हर चीज़ के लिए class के बजाय सही type चुनकर domain को model करें |
| 3. Idiom | 0012 से 0016 | Extension methods, LINQ की query और method syntax, delegates और events, nullable reference types, expression-bodied members | ऐसा C# लिखें जिसे reviewer अनुवाद किया हुआ Java न कहे |
| 4. Async | 0017 से 0021 | `Task` model, `async`/`await` की कार्यप्रणाली, `Task` composition, cancellation tokens, `IAsyncEnumerable` | समझा सकें कि `await` method के execution के साथ क्या करता है और async program के व्यवहार का अनुमान लगा सकें |
| 5. Testing और build | 0022 से 0024 | xUnit/NUnit, mocking, `dotnet` CLI और project/package management | कोई और इसे clone, build, test और run कर सके |
| 6. Service को ship करना | 0025 से 0029 | ASP.NET Core routing और middleware, dependency injection, configuration, Entity Framework Core की बुनियादी बातें, typed, tested backend की संरचना | Typed, tested ASP.NET Core service ship करें |
| 7. विवेक | 0030 से 0031 | `async`/`await` की तुलना Java virtual threads से और LINQ की Stream API से, ऐसी आदत के लिए C# की समीक्षा जो बस compile हो जाती है | निर्णय लेने और उसे किसी और को समझाने के लिए भरोसेमंद |
| 8. CLR Runtime और Performance | 0032 से 0037 | Managed heap का generational डिज़ाइन, GC modes, `Span<T>`/`Memory<T>`, `stackalloc`/`ArrayPool<T>`, BenchmarkDotNet से struct बनाम class को मापना, और profiling | Profile से optimise करें और जीत को भरोसेमंद benchmark से सही ठहराएँ, CLR के असली generational और allocation व्यवहार से जोड़कर |
| 9. Resource Lifetime | 0038 | `IDisposable` और `IAsyncDisposable` implement करना: dispose pattern, `disposing` parameter, finalizers, और `DisposeAsyncCore` | सिर्फ़ `using` से उसे consume करने के बजाय सही, idempotent dispose pattern implement करें |
| 10. Service को चलाना और सुरक्षित करना | 0039 से 0042 | `ILogger` से structured logging, liveness/readiness health checks, OpenTelemetry, authentication और authorization, और `System.Text.Json` serialization | ऐसी service ship करें जिसे observe, health-check, सुरक्षित और सही ढंग से serialize किया जा सके, सिर्फ़ build नहीं |
| 11. API Evolution और Packaging | 0043 से 0045 | Binary बनाम source बनाम behavioral compatibility, `[Obsolete]` और deprecation, NuGet packaging और semantic versioning | किसी बदलाव के compatibility असर को सटीक रूप से वर्गीकृत करें और publish की गई API को callers को अचानक तोड़े बिना आगे बढ़ाएँ |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-structs-and-classes.md) | Structs और Classes | Type system का वह चुनाव जो Java ने आपको कभी नहीं दिया, और CLR हर एक के साथ असल में क्या करता है |
| [0002](lessons/0002-nullable-value-types.md) | Nullable Value Types | int? अब भी value type क्यों है, तुलना का वह नियम जो दोनों दिशाओं को false बनाता है, और boxing wrapper के साथ क्या करता है |
| [0003](lessons/0003-basic-types-and-string-interpolation.md) | बुनियादी Types और String Interpolation | .NET types के aliases के रूप में keywords, decimal class के बजाय built-in क्यों है, और interpolation hole की width, format और side-effect के नियम |
| [0004](lessons/0004-collections.md) | Collections | वह abstraction के रूप में IEnumerable जिस पर बाक़ी रूपरेखा टिकी है, और dictionary lookup जो वहाँ throw करता है जहाँ Java का map null लौटाता है |
| [0005](lessons/0005-control-flow.md) | Control Flow | वे तीन जगहें जहाँ control flow Java से ज्यों का त्यों नहीं आता: foreach का duck-typed enumerator, fall-through के बिना switch, और वैध jump के रूप में goto |
| [0006](lessons/0006-exceptions.md) | Exceptions | Exception filters और वह stack trace जिसे catch-and-rethrow नष्ट कर देता है, निश्चित सफ़ाई के लिए using, और चरण 1 का capstone |
| [0007](lessons/0007-properties.md) | Properties | भाषा की feature के रूप में accessors, required, init और non-nullable type के तीन स्वतंत्र वादे, और बिना backing field वाली computed properties |
| [0008](lessons/0008-record-types.md) | Record Types | record modifier असल में क्या generate करता है, equality runtime type पर क्यों निर्भर करती है, और वह सतही immutability जिसे with expression ठीक नहीं करता |
| [0009](lessons/0009-pattern-matching.md) | Pattern Matching | Pattern की शब्दावली, switch expression की exhaustiveness और उसकी एक चुपचाप कमी, और arms का क्रम compile-time का सवाल क्यों है |
| [0010](lessons/0010-interfaces.md) | Interfaces | अब जब interface implementations रख सकता है तो वह क्या-क्या रख सकता है, वह auto-property जो असल में auto-property नहीं है, और वह member जिसे आप सिर्फ़ interface के ज़रिए call कर सकते हैं |
| [0011](lessons/0011-generics.md) | Generics | Type parameter को क्या होना चाहिए, इसकी शब्दावली के रूप में constraints, positions के नियम के रूप में variance, और सही type चुनने का चरण 2 का capstone |
| [0012](lessons/0012-extension-methods.md) | Extension Methods | एक ही IL में compile होने वाली दो syntaxes, binding का वह नियम जो extension को कुछ भी override करने से रोकता है, और call site पर उसकी क़ीमत |
| [0013](lessons/0013-linq.md) | LINQ | दो syntaxes वाली एक query language जिनमें कोई semantic फ़र्क़ नहीं, iterate करने तक कुछ क्यों नहीं चलता, और वह expression tree जो उसी query को database तक पहुँचने देता है |
| [0014](lessons/0014-delegates-and-events.md) | Delegates और Events | ऐसे type के रूप में delegate जिसके signature में उसका return type शामिल है, invocation list जहाँ एक throw करने वाला handler बाक़ी को रोक देता है, और event keyword callers से क्या छीन लेता है |
| [0015](lessons/0015-nullable-reference-types.md) | Nullable Reference Types | Types के बजाय annotations, वह null-state जिसे compiler आपके control flow में track करता है, और वह एक library जो आपके annotation को runtime व्यवहार में बदल देती है |
| [0016](lessons/0016-expression-bodied-members.md) | Expression-Bodied Members | Arrow token का दूसरा काम, void members के लिए statement-expression नियम, और अनुवाद किए हुए Java को फिर से लिखने का चरण 3 का capstone |
| [0017](lessons/0017-the-task-model.md) | Task Model | Thread के बजाय asynchronous operation के रूप में task, उसके अस्तित्व में आने के चार तरीक़े, और वह AggregateException जो ऐसे process को ख़त्म कर सकता है जिसे आप ख़त्म हुआ समझ चुके थे |
| [0018](lessons/0018-async-and-await.md) | async और await | await घेरने वाले method के साथ क्या करता है, वे तीन जगहें जहाँ वह वर्जित है, और async void caller के पास मौजूद एकमात्र तंत्र को क्यों तोड़ देता है |
| [0019](lessons/0019-task-composition.md) | Task Composition | Await करने से पहले काम शुरू करना, वह ToArray जो LINQ से बनी task list को सचमुच चलवाता है, और वह दोहरा await जो WhenAny को चाहिए |
| [0020](lessons/0020-cancellation-tokens.md) | Cancellation Tokens | एक requester और कई listeners वाला cooperative cancellation, जल्दी return करना सफलता क्यों report करता है, और token की वह तुलना जो तय करती है कि task कहे कि वह canceled हुआ |
| [0021](lessons/0021-async-streams.md) | Async Streams | await foreach के पीछे के तीन interfaces, वह attribute जो consumer के token को async iterator की body तक पहुँचने देता है, और async program का अनुमान लगाने का चरण 4 का capstone |
| [0022](lessons/0022-xunit-and-nunit.md) | xUnit और NUnit | हर test का अपना instance होने का नियम जिससे xUnit को setup attribute की ज़रूरत ही नहीं पड़ती, theory शब्द का दो अलग चीज़ों के लिए इस्तेमाल, और वह parallelism जिसकी क़ीमत साझा fixture चुपचाप वसूलता है |
| [0023](lessons/0023-mocking.md) | Mocking | हर substitution library के पीछे का runtime proxy, C# का वह default जो तय करता है कि उसे क्या बदलने की अनुमति है, और mock किया गया वह assertion जो call हुए बिना ही pass हो जाता है |
| [0024](lessons/0024-the-dotnet-cli-and-packages.md) | dotnet CLI और Packages | ताज़ा clone को जिस एक command की ज़रूरत है, package version pin के बजाय न्यूनतम सीमा क्यों है, वह SDK release जिसने commands का क्रम बदल दिया, और चरण 5 का capstone |
| [0025](lessons/0025-routing-and-middleware.md) | Routing और Middleware | एक Program.cs साझा करने वाले दो systems, एक आपके लिखे क्रम से तय होता है और एक template की precedence से, और वे दो positions जो तय करती हैं कि middleware क्या जान सकता है और वह चलता भी है या नहीं |
| [0026](lessons/0026-dependency-injection.md) | Dependency Injection | ऐसे दावों के रूप में तीन lifetimes जिन्हें container सिर्फ़ वहीं लागू करता है जहाँ उसे दिखते हैं, वह लंबे समय तक चलने वाली service जो अल्पकालिक service को चुपचाप promote कर देती है, और container ने जो बनाया उसे कोई dispose क्यों नहीं करता |
| [0027](lessons/0027-configuration.md) | Configuration | Strings की एक सपाट dictionary जहाँ आख़िरी provider जीतता है, पसंद के बजाय lifetime से अलग किए गए तीन options interfaces, और validation जो पहली request का इंतज़ार करती है जब तक आप उसे ऐसा न करने को कहें |
| [0028](lessons/0028-entity-framework-core.md) | Entity Framework Core | ऐसा context जो याद रखता है कि आपने क्या query किया ताकि assignment update बन जाए, वह एकमात्र जगह जहाँ query को client पर लौटने की अनुमति है, और चरण 4 की काम को overlap करने की आदत उसे क्यों बिगाड़ देती है |
| [0029](lessons/0029-structuring-a-typed-tested-backend.md) | Typed, Tested Backend की संरचना | वह seam के रूप में container जिसके ज़रिए test registrations बदलता है, unit test और integration test में से चुनने का documented नियम, और चार ऐसे defects का चरण 6 का capstone जो सब compile हो जाते हैं |
| [0030](lessons/0030-two-comparisons-with-java.md) | Java के साथ दो तुलनाएँ | इंतज़ार की वही समस्या दो अलग परतों पर सुलझाई गई, Java का जवाब C# की ज़रूरी style को अपनाने के बजाय उसे हटा क्यों देता है, और वह expression tree जिसका Stream में कोई समकक्ष नहीं |
| [0031](lessons/0031-reviewing-csharp.md) | C# Codebase की समीक्षा | Style की राय और ऐसी क़ीमत के बीच फ़र्क़ जिसका आप नाम ले सकें, उस क्रम में समीक्षा जो compiler आपको कभी नहीं बताएगा, और वे आदतें जो यह रूपरेखा पाठ 1 से इकट्ठा करती आई है |
| [0032](lessons/0032-the-managed-heap-and-generations.md) | Managed Heap और Generations | पाठ 1 ने कहा था कि class instance managed heap पर रहता है; यह पाठ खोलता है कि वहाँ उसके साथ क्या होता है, heap तीन generations में क्यों बँटा है, और ज़्यादातर objects सबसे नई generation में, कभी promote हुए बिना, मरने के लिए ही क्यों बने हैं |
| [0033](lessons/0033-gc-modes-and-tradeoffs.md) | GC Modes और Trade-offs | पाठ 32 ने generational heap स्थापित किया; यह पाठ कवर करता है कि collection उस पर असल में कैसे चलता है, एक समर्पित thread या हर core पर एक, हर managed thread को block करते हुए या ज़्यादातर को चलते रहने देते हुए, और वह एक पल जब non-blocking mode को भी सब कुछ रोकना पड़ता है |
| [0034](lessons/0034-span-and-memory.md) | Span और Memory | मौजूदा memory पर zero-allocation दृश्य जो पाठ 32 के generational system में कभी आता ही नहीं, वे compiler पाबंदियाँ जो उसे सुरक्षित रूप से सिर्फ़ stack पर रखती हैं, और heap-सुरक्षित समकक्ष जो ठीक उसी एक काम के लिए बना है जो वह नहीं कर सकता: await को पार करना |
| [0035](lessons/0035-stackalloc-and-arraypool.md) | stackalloc और ArrayPool | पाठ 34 ने Span<T> को stackalloc की गई memory देखने दी; यह पाठ कवर करता है कि stackalloc असल में क्या allocate करता है, उसे ref struct के साथ जोड़ना ही उसे सुरक्षित क्यों बनाता है, उसका असली जोखिम (stack overflow, garbage collection नहीं), और stack के लिए बहुत बड़े या बहुत लंबे समय तक रहने वाले buffer के लिए fallback के रूप में ArrayPool<T> |
| [0036](lessons/0036-struct-vs-class-measured.md) | Struct बनाम Class, मापकर | पाठ 1 ने तर्क दिया था कि struct उस heap allocation से बच सकता है जो उसी आकार की class को चाहिए; यह पाठ वह जगह है जहाँ उस तर्क को तर्क से नहीं, मापकर परखा जाता है, और इसे मापने का स्पष्ट तरीक़ा ऐसी संख्या क्यों देता है जिसका कोई मतलब ही नहीं |
| [0037](lessons/0037-profiling-a-csharp-service.md) | C# Service की Profiling | dotnet-counters लक्षण पकड़ता है और dotnet-trace उसके पीछे का hot stack ढूँढता है, warm-up के बाद ही profiling ताकि JIT को न माप लिया जाए, और profile की खोज को इसी चरण के किसी lever से वापस भेजने का चरण 8 का capstone |
| [0038](lessons/0038-idisposable-and-iasyncdisposable.md) | IDisposable और IAsyncDisposable | पाठ 6 ने consumer के रूप में using सिखाया, और पाठ 26 ने सिखाया कि container जो बनाता है उसे dispose करता है; यह पाठ दूसरे पक्ष के लिए है, यानी IDisposable और IAsyncDisposable को सचमुच implement करना, वह pattern जो type को एक से ज़्यादा बार dispose करने, finalize करने, और await करने के लिए सुरक्षित बनाता है |
| [0039](lessons/0039-logging-and-health-checks.md) | Logging और Health Checks | ऐसा typed, tested backend जिसे कोई observe न कर सके या जिससे कोई पूछ न सके "क्या तुम काम कर रहे हो", उसकी shipping पूरी नहीं हुई; यह पाठ ILogger की structured logging और liveness/readiness विभाजन को Program.cs में उसी तरह जोड़ता है जैसे पाठ 25 ने routing और पाठ 26 ने container को जोड़ा था |
| [0040](lessons/0040-opentelemetry.md) | OpenTelemetry | पाठ 39 का ILogger पहले से ही OpenTelemetry के तीन स्तंभों में से एक है; यह पाठ बाक़ी दो, metrics और traces, framework में पहले से बने APIs के ज़रिए जोड़ता है, और तीनों को उसी AddX pattern से service में जोड़ता है जो पाठ 25, 26 और 39 पहले ही सिखा चुके हैं |
| [0041](lessons/0041-authentication-and-authorization.md) | Authentication और Authorization | Authentication बताता है कि आप कौन हैं और authorization बताता है कि आपको क्या करने की अनुमति है, जिन्हें अलग-अलग चिंताओं के रूप में documented किया गया है भले ही एक दूसरे पर निर्भर है, और जिन्हें पाठ 25 के अपने middleware-क्रम के अनुशासन और उस AllowAnonymous override के साथ जोड़ा जाता है जिसकी पाठ 39 के health checks को सचमुच ज़रूरत है |
| [0042](lessons/0042-system-text-json.md) | System.Text.Json | अकेले serializer के अपने defaults (PascalCase, case-sensitive) वे नहीं हैं जो ASP.NET Core HTTP सीमा पर असल में इस्तेमाल करता है (camelCase, case-insensitive), एक असली अंतर जिसका नाम उलझाने वाले test परिणाम से पहले लेना ज़रूरी है, साथ में reflection के compile-time विकल्प के रूप में source generation |
| [0043](lessons/0043-api-compatibility.md) | API Compatibility | साफ़ recompile होने वाला बदलाव भी हर उस caller को fail कर सकता है जो recompile नहीं करता, compile न होने वाला बदलाव उन callers के लिए बिल्कुल ठीक हो सकता है जिनके पास पहले से काम करती binary है, और जो बदलाव दोनों में से कुछ नहीं करता वह भी चुपचाप कुछ अलग कर सकता है, और semantic versioning असल में caller को इसी एक बात की चेतावनी देने के लिए है |
| [0044](lessons/0044-obsolete-and-deprecation.md) | Obsolete और Deprecation | पाठ 43 ने बताया कि breaking change किसे गिनते हैं; ObsoleteAttribute वह तरीक़ा है जिससे publish की गई API घोषणा करती है कि ऐसा बदलाव आ रहा है, उसी member पर दबाई जा सकने वाली warning से असली compile error तक बढ़ते हुए, custom diagnostic ID के साथ ताकि एक deprecation की warning को project की बाक़ी हर warning को चुप कराए बिना चुप कराया जा सके |
| [0045](lessons/0045-nuget-packaging-and-versioning.md) | NuGet Packaging और Versioning | इस रूपरेखा का अंतिम पाठ चरण 11 को जोड़ता है: वह version number जिसे पाठ 43 की compatibility श्रेणियाँ सचमुच सही ठहराती हैं, वह pre-release suffix जिसके बारे में NuGet उसे pre-release कहने के अलावा कुछ लागू नहीं करता, upper-bound की वह सलाह जो सहज समझ के उलट जाती है, और वह पुराना package जिसे rebuild के बाद भी आप test करते रह सकते हैं |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत
- [Value बनाम Reference Types](reference/value-vs-reference-types.md): struct बनाम class, nullable value types, copy-बनाम-reference व्यवहार का अनुमान
- [Modelling](reference/modelling.md): `record` types, pattern matching और switch expressions, default implementations वाले interfaces, generics
- [Idiom](reference/idiom.md): extension methods, LINQ, delegates और events, nullable reference types
- [Async](reference/async.md): `Task` model, `async`/`await` की कार्यप्रणाली, cancellation tokens, `IAsyncEnumerable`
- [Testing और Build](reference/testing-and-build.md): xUnit/NUnit, mocking, `dotnet` CLI और project/package management
- [Service को Ship करना](reference/shipping-the-service.md): ASP.NET Core routing और middleware, dependency injection, configuration, Entity Framework Core की बुनियादी बातें
- [विवेक](reference/judgment.md): `async`/`await` बनाम Java virtual threads, LINQ बनाम Stream API, ऐसी आदत के लिए C# की समीक्षा जो बस compile हो जाती है

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
