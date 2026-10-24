---
title: Rust
description: "Rust को अपने हाथ में लें: borrow checker से लड़ने के बजाय ownership के साथ डिज़ाइन करें, फिर crate ship करें"
type: topic
---

# सीखना: Rust

वह engineer बनें जिस पर team में Rust की ज़िम्मेदारी के लिए भरोसा किया जाए: borrow checker से मोलभाव करने के बजाय ownership के साथ डिज़ाइन कर सकें, errors और APIs को ऐसा आकार दे सकें कि types ही invariants को ढोएँ, `unsafe` को सिर्फ़ ऐसी सीमा के पीछे उठा सकें जिसे सही ठहराया जा सके, और ऐसा crate ship कर सकें जिस पर दूसरे लोग निर्भर हों और जिसे वे upgrade कर सकें।

**यहाँ से शुरू करें:** [0001. Ownership और Drop](lessons/0001-ownership-and-drop.md)
**नवीनतम पाठ:** [0067. Property-Based और Snapshot Testing](lessons/0067-property-based-and-snapshot-testing.md)

## सफलता कैसी दिखती है

- Compile करने से पहले अनुमान लगाएँ कि compiler कौन-सा borrow अस्वीकार करेगा, और क्यों।
- Data को असल में कितने समय तक रहना है, इसके आधार पर owning, borrowing, reference counting और interior mutability में से चुनें।
- ऐसा error type डिज़ाइन करें जिसे callers संभाल सकें, और बताएँ कि कब इसके बजाय panic करना सही चुनाव है।
- Signatures को अपठनीय बनाए बिना traits और generics से दोहराव हटाएँ, और जानें कि कब dynamic dispatch बेहतर जवाब है।
- ऐसा async code लिखें जो अटके नहीं, और समझाएँ कि `await` point के पार lock पकड़े रखना क्या करता है।
- हर `unsafe` block को उस invariant से सही ठहराएँ जिसे वह बनाए रखता है, उसे safe interface के पीछे रखें, और पढ़कर नहीं बल्कि tool से उसे जाँचें।
- Documentation, tests, और ऐसी public API के साथ crate publish करें जिसे आप निर्भर लोगों को तोड़े बिना आगे बढ़ा सकें।
- Rust की समीक्षा करें और सटीक रूप से बताएँ कि lifetime annotation, `clone`, या साझा mutex किसी design समस्या को क्यों ढक रहा है।

## सीमाएँ

- Rust का कोई पूर्व अनुभव और systems-programming की कोई पृष्ठभूमि नहीं मानी गई है। Stack, heap और memory layout रूपरेखा के भीतर ही सिखाए जाते हैं, क्योंकि उनके बिना ownership सिखाई ही नहीं जा सकती।
- किसी भी supported OS पर सिर्फ़ stable toolchain और terminal चाहिए। रूपरेखा में किसी चीज़ के लिए paid tooling, cloud account, या nightly Rust की ज़रूरत नहीं।
- **अभ्यासों से compile न होने की उम्मीद है।** यही feedback loop है, कोई झटका नहीं: अनुमान लगाएँ कि compiler क्या कहेगा, फिर पता करें, और फ़र्क़ को ही पाठ मानें।
- अभ्यास छोटे programs हैं जो एक बैठक में पूरे हो जाते हैं। उन्हें कई दिनों में फैलाना ही तरीक़ा है, कोई असुविधा नहीं।
- यहाँ editions और releases मायने रखते हैं। जहाँ कोई पाठ किसी edition या stabilised feature पर निर्भर है, वहाँ वह बताता है कि कौन-सा, और version पर निर्भर दावों को याद के बजाय release notes से जाँचा जाता है।

## दायरे से बाहर

- Embedded targets और `no_std` अपने-आप में विषय के रूप में।
- WebAssembly, graphical interfaces, और game engines।
- विषय के रूप में web frameworks। Async को उदाहरणों की ज़रूरत है, और वे उतने ही छोटे रहते हैं जितना concept अनुमति देता है।
- Procedural macros लिखना। Declarative macros वहाँ आते हैं जहाँ standard library के अपने इस्तेमाल को पढ़ना पड़ता है।
- Foreign function interfaces, उससे आगे जो `unsafe` सीमा वाली सामग्री को चाहिए। किसी असली C library को wrap करना अलग काम है।
- Compiler और borrow-checker के भीतरी हिस्से, उस बिंदु से आगे जहाँ वे यह अनुमान लगाने में मदद करना बंद कर देते हैं कि compiler क्या स्वीकार करेगा।

## पूरी रूपरेखा

आठ चरण, शून्य से senior तक। यह पाठों की सूची नहीं है: एक चरण में कई पाठ लगते हैं, और सीमाएँ लचीली हैं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. Ownership | 0001 से 0006 | Values, stack और heap, moves, `Copy`, borrows और उनके नियम, slices, `String` बनाम `&str`, shadowing | Compiler के report करने से पहले move या borrow error का अनुमान लगा सकें |
| 2. Data और control | 0007 से 0013 | Structs, enums, `Option` और `Result`, pattern matching और exhaustiveness, iterators, closures, जानने लायक collections | Enums से model करें, और `unwrap` उठाए बिना अनुपस्थिति को संभालें |
| 3. Errors और API का आकार | 0014 से 0020 | `?` से propagation, custom error types, `From` conversions, panic बनाम error, modules और visibility, compile होने वाला documentation लिखना | ऐसी library लिखें जिसकी failures को caller सचमुच संभाल सके |
| 4. Traits, generics और lifetimes | 0021 से 0028 | Trait bounds, associated types, generics बनाम dynamic dispatch, orphan rule, lifetime annotations और elision, lifetime अवधि क्यों नहीं है | Lifetime error को बाधा के बजाय जानकारी के रूप में पढ़ें |
| 5. Sharing और threads | 0029 से 0036 | `Box`, `Rc` और `Arc`, `RefCell` और `Mutex`, `Send` और `Sync`, threads, channels, deadlock और poisoning | आदत के बजाय data के आधार पर sharing रणनीति चुनें |
| 6. Async | 0037 से 0045 | Futures और executors, tasks और cancellation, async में blocking call bug क्यों है, `await` के पार locks, pinning किसलिए है | ऐसा async code लिखें जो अटके नहीं, और समझा सकें कि वह कहाँ अटकता |
| 7. Unsafe और performance | 0046 से 0054 | `unsafe` असल में क्या वादा करता है, undefined behaviour, invariant को encapsulate करना, Miri से जाँचना, benchmarking, allocation और copying की क़ीमत | `unsafe` सीमा का बचाव कर सकें, और performance के दावे को माप से साबित करें |
| 8. विवेक | 0055 से 0063 | Publishing, public API की semantic versioning, API guidelines, समीक्षा, जवाबों के लिए standard library और RFCs पढ़ना | निर्णय लेने और उसे किसी और को समझाने के लिए भरोसेमंद; चरण 9 release प्रक्रिया का अपना पहला क़दम पूरा करता है, test suite pass होता है, उस suite के साथ जिसे लिखना यह रूपरेखा अब तक नहीं सिखा पाई थी |
| 9. Testing | 0064 से 0067 | `#[test]` और `cargo test`, unit tests बनाम integration tests, library के लिए tests की व्यवस्था, property-based और snapshot testing | Test suite को उसी तरह लिखें और व्यवस्थित करें जैसे standard library ख़ुद करती है, सिर्फ़ doctests और benchmarks नहीं |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-ownership-and-drop.md) | Ownership और Drop | हर value का ठीक एक owner होता है, और जब वह owner scope से बाहर जाता है तो compiler उसे free कर देता है |
| [0002](lessons/0002-moves-and-copy.md) | Moves और Copy | Assignment ownership को move करता है जब तक type Copy न हो, और इसीलिए पुराना name काम करना बंद कर देता है |
| [0003](lessons/0003-borrowing.md) | Borrowing | कई shared borrows या एक mutable borrow, दोनों कभी नहीं, और borrow अपने आख़िरी इस्तेमाल पर ख़त्म होता है |
| [0004](lessons/0004-slices-string-and-str.md) | Slices, String और str | Slice length वाला borrowed दृश्य है, और API में &str लेने की callers को कोई क़ीमत नहीं चुकानी पड़ती |
| [0005](lessons/0005-bindings-and-mutability.md) | Bindings और Mutability | Default रूप से immutable, mut हर binding पर लागू होता है, और shadowing बदलाव नहीं बल्कि नई binding है |
| [0006](lessons/0006-reading-a-borrow-error.md) | Borrow Error पढ़ना | पाँच error codes चरण 1 का ज़्यादातर हिस्सा कवर करते हैं, और हर एक का एक ईमानदार सुधार और एक जुगाड़ है |
| [0007](lessons/0007-structs.md) | Structs और उनके Methods | Struct अपने fields का मालिक है, इसलिए आप उसमें जो रखते हैं वह तय करता है कि उसे जीवित किसे रखना है |
| [0008](lessons/0008-enums.md) | Data ढोने वाले Enums | Enum कहता है कि value ठीक इनमें से एक आकार की है, और यही वह modelling औज़ार है जिस पर बाक़ी चरण टिका है |
| [0009](lessons/0009-option.md) | Option, और अनुपस्थिति को संभालना | अनुपस्थिति एक अलग type की value है, इसलिए compiler आपसे कहलवाता है कि उसके आने पर क्या होगा |
| [0010](lessons/0010-result.md) | Result, और Value के रूप में Failure | Failure कोई event नहीं बल्कि return value है, इसलिए body पढ़ने से पहले ही signature बता देता है कि क्या ग़लत हो सकता है |
| [0011](lessons/0011-pattern-matching.md) | Pattern Matching | match को हर case कवर करना चाहिए, और pattern तय करता है कि आपने value को borrow किया या move |
| [0012](lessons/0012-iterators-and-closures.md) | Iterators और Closures | Iterator तब तक कुछ नहीं करता जब तक कोई उसे consume न करे, और closure ठीक वही capture करता है जो वह इस्तेमाल करता है |
| [0013](lessons/0013-collections.md) | जानने लायक Collections | Vec और HashMap ज़्यादातर हिस्सा कवर करते हैं, और entry API वह एक चीज़ है जिसे ठीक से सीखना ज़रूरी है |
| [0014](lessons/0014-propagating-errors.md) | Errors को आगे बढ़ाना | Question mark return करते हुए convert करता है, इसलिए आपके signature का error type तय करता है कि वह क्या स्वीकार करेगा |
| [0015](lessons/0015-designing-an-error-type.md) | Error Type का डिज़ाइन | Caller सिर्फ़ वही संभाल सकता है जिसमें आपका error उसे फ़र्क़ करने दे, इसलिए उसका आकार API का निर्णय है |
| [0016](lessons/0016-conversions-and-boundaries.md) | Conversions और सीमाएँ | From implementation वह जगह है जहाँ एक परत की failure दूसरी की बन जाती है, और derive वे लिख देता है जिन्हें आप पहले से समझते हैं |
| [0017](lessons/0017-panic-or-error.md) | Panic या Error | Panic कहता है कि program टूटा है और error कहता है कि input टूटा था, और library को पहले वाले का निर्णय शायद ही कभी लेने को मिलता है |
| [0018](lessons/0018-modules-and-visibility.md) | Modules और Visibility | आप जो public बनाते हैं वही आपने बनाए रखने का वादा किया है, इसलिए module tree व्यवस्था का निर्णय होने से पहले API का निर्णय है |
| [0019](lessons/0019-documentation-that-compiles.md) | Compile होने वाला Documentation | Doc comment में उदाहरण एक test है, इसलिए सड़ने वाला documentation वही है जिसे किसी ने चलाया नहीं |
| [0020](lessons/0020-a-library-callers-can-handle.md) | ऐसी Library जिसे Caller संभाल सके | Crate को बाँटें, failures को नाम दें, और तय करें कि binary क्या करता है जो library को नहीं करना चाहिए |
| [0021](lessons/0021-traits-as-shared-behaviour.md) | साझा व्यवहार के रूप में Traits | Trait उस व्यवहार को कैसे नाम देता है जो कई types दे सकते हैं, और उसे इस्तेमाल करने से पहले trait का scope में होना क्यों ज़रूरी है |
| [0022](lessons/0022-trait-bounds-and-generic-functions.md) | Trait Bounds और Generic Functions | Bound body से क्या वादा करता है और caller से क्या माँगता है, और compiler उसके साथ क्या करता है |
| [0023](lessons/0023-associated-types.md) | Associated Types | Iterator अपने Item को parameter के बजाय associated type के रूप में क्यों नाम देता है, और यह उसे implement करने वाले हर किसी के लिए क्या तय करता है |
| [0024](lessons/0024-generics-or-dyn-trait.md) | Generics या dyn Trait | Dispatch की दो रणनीतियाँ, हर एक की क़ीमत, और वह सवाल जो असल में उनके बीच निर्णय करता है |
| [0025](lessons/0025-implementing-traits-you-do-not-own.md) | ऐसे Traits Implement करना जिनके आप मालिक नहीं | Coherence, newtype pattern, और blanket implementation सुविधा के बजाय प्रतिबद्धता क्यों है |
| [0026](lessons/0026-lifetimes-are-not-durations.md) | Lifetimes अवधि नहीं हैं | Lifetime parameter borrows के बीच संबंध के बारे में क्या कहता है, और elision शुरू से आपके लिए क्या कर रहा था |
| [0027](lessons/0027-types-that-borrow.md) | Borrow करने वाले Types | Struct पर lifetime parameter रखना, और यह तय करना कि क्या type को इसके बजाय अपने data का मालिक होना चाहिए |
| [0028](lessons/0028-reading-a-lifetime-error.md) | Lifetime Error पढ़ना | Lifetime error के रूप, हर एक का ईमानदार सुधार और वह जुगाड़ जिसकी ओर वह आपको ललचाता है |
| [0029](lessons/0029-threads-joining-and-panics.md) | Threads, Joining और Panics | Spawn करना आपके सौंपे data से असल में क्या माँगता है, और अकेले panic करने वाले thread के साथ क्या होता है |
| [0030](lessons/0030-scoped-threads.md) | Scoped Threads | जो thread अपने scope से ज़्यादा नहीं जी सकता वह borrow क्यों कर सकता है, और यह आख़िरी के बजाय पहली चीज़ क्यों है जिसे उठाना चाहिए |
| [0031](lessons/0031-shared-ownership.md) | Rc और Arc के साथ साझा Ownership | कब value को एक के बजाय कई owners चाहिए, गिनती की क़ीमत क्या है, और cycle कैसे leak करता है |
| [0032](lessons/0032-interior-mutability.md) | Interior Mutability | Borrow नियम को compile time से run time पर ले जाना, इससे क्या मिलता है, और ग़लती होने पर इसकी क्या क़ीमत है |
| [0033](lessons/0033-mutex-rwlock-and-poisoning.md) | Mutex, RwLock और Poisoning | Lock असल में किसकी रक्षा करता है, guard का scope ही design निर्णय क्यों है, और lock पकड़े हुए panic पीछे क्या छोड़ता है |
| [0034](lessons/0034-send-and-sync.md) | Send और Sync | वे दो traits जिन्हें कोई नहीं लिखता पर जो तय करते हैं कि thread की सीमा क्या पार कर सकता है, और उनसे होने वाली errors कैसे पढ़ें |
| [0035](lessons/0035-channels.md) | Channels | Threads के बीच values को साझा करने के बजाय भेजना, और जब दूसरा छोर चला जाए तो channel के छोर क्या करते हैं |
| [0036](lessons/0036-choosing-a-sharing-strategy.md) | Sharing रणनीति चुनना | आदत से चुनने पर होने वाली failures, और वे सवाल जो इसके बजाय data से रणनीति चुनते हैं |
| [0037](lessons/0037-what-a-future-is.md) | Future क्या है | एक method वाली state machine, जिसे वही चलाता है जो उसे poll करे, और इसका क्रमिक दिखने वाले code के लिए क्या मतलब है |
| [0038](lessons/0038-wakers-executors-and-runtimes.md) | Wakers, Executors और Runtimes | Future कैसे बताता है कि वह फिर से poll होने के लिए तैयार है, और runtime उसे poll करने के अलावा क्या करता है |
| [0039](lessons/0039-tasks-and-the-send-bound.md) | Tasks और Send Bound | Async task spawn करना आपके सौंपे future से क्या माँगता है, और async trait method उसे पूरा क्यों नहीं करेगा |
| [0040](lessons/0040-blocking-is-a-bug.md) | Blocking एक Bug है | Async task में एक blocking call ऐसे काम को क्यों अटका देती है जिससे उसका कोई लेना-देना नहीं, और उन calls का क्या करें जिनसे आप बच नहीं सकते |
| [0041](lessons/0041-shared-state-across-an-await.md) | Await के पार साझा State | Await point के पार पकड़ा गया lock guard अस्वीकार क्यों होता है, और दो तरह के mutex में से कैसे चुनें |
| [0042](lessons/0042-cancellation.md) | Cancellation | Future को रोकने का मतलब उसे drop करना है, इसीलिए किसी को बताया नहीं जाता और काम बस वहीं रुक जाता है जहाँ था |
| [0043](lessons/0043-cancellation-safety.md) | Cancellation Safety | क्या future को बीच उड़ान में drop किया जा सकता है बिना वह खोए जो उसने पहले ही ले लिया था, और इस सवाल का उत्तर कहाँ दिया जाता है |
| [0044](lessons/0044-pinning.md) | Pinning | Poll होने के बाद future की memory का खिसकना बंद क्यों होना चाहिए, और Pin इसके बारे में क्या करता है |
| [0045](lessons/0045-reading-an-async-failure.md) | Async Failure पढ़ना | वे पाँच तरीक़े जिनसे async code बिना error message के fail होता है, और कैसे पहचानें कि आप किसे देख रहे हैं |
| [0046](lessons/0046-what-unsafe-promises.md) | Unsafe क्या वादा करता है | वे पाँच चीज़ें जो unsafe block आपको करने देता है, और उसे लिखकर आप कौन-सा दायित्व लेते हैं |
| [0047](lessons/0047-raw-pointers.md) | Raw Pointers | Raw pointer क्या नहीं है, गारंटियों में उसकी आपको क्या क़ीमत चुकानी पड़ती है, और ऐसा pointer कैसे बनाएँ जो सचमुच valid हो |
| [0048](lessons/0048-undefined-behaviour.md) | Undefined Behaviour | Compiler को क्या मानने की अनुमति है, काम करने वाला program भी ग़लत क्यों हो सकता है, और वह सूची जिसे ज़बानी याद रखना चाहिए |
| [0049](lessons/0049-checking-with-miri.md) | Miri से जाँचना | वह tool जो अदृश्य soundness bug को report में बदल देता है, वह क्या पकड़ता है, और क्या नहीं पकड़ सकता |
| [0050](lessons/0050-encapsulating-an-invariant.md) | Invariant को Encapsulate करना | Unsafe code को safe interface में लपेटना, और उस interface को यह नाम पाने के लायक होने के लिए क्या सच होना चाहिए |
| [0051](lessons/0051-memory-orderings.md) | Memory Orderings | Ordering असल में किसे सीमित करती है, आप उसे चलाकर test क्यों नहीं कर सकते, और अपनी चुनी ordering को कैसे जाँचें |
| [0052](lessons/0052-measuring-before-optimising.md) | Optimise करने से पहले मापना | ऐसी संख्या कैसे पाएँ जिसका आप बचाव कर सकें, compiler कुछ न मापने वाले benchmark के साथ क्या करता है, और माप आपको क्या नहीं बता सकता |
| [0053](lessons/0053-allocation-and-copying-costs.md) | Allocation और Copying की क़ीमत | Rust program असल में अपना समय कहाँ ख़र्च करता है, और कौन-से स्पष्ट सुधार अपनी क़ीमत वसूल करते हैं |
| [0054](lessons/0054-defending-an-unsafe-boundary.md) | Unsafe सीमा का बचाव | वह तर्क जो unsafe block के ship होने से पहले आपको दे पाना चाहिए, और वह माप जो उसके साथ आना चाहिए |
| [0055](lessons/0055-variance.md) | Variance | कौन-से lifetimes किसकी जगह ले सकते हैं, आपका अपना type ही क्यों तय करता है, और यह आपको किससे बाँधता है |
| [0056](lessons/0056-higher-ranked-bounds.md) | Higher-Ranked Bounds | वह quantifier लिखना जिसे compiler आपके सामने print करता आ रहा है, और API के वे आकार जिन्हें इसकी ज़रूरत है |
| [0057](lessons/0057-what-breaks-a-caller.md) | Caller को क्या तोड़ता है | वे बदलाव जिनके लिए major version चाहिए, वे जो सिर्फ़ सुरक्षित दिखते हैं, और वह tool जो बताता है कि कौन क्या है |
| [0058](lessons/0058-designing-for-change.md) | बदलाव के लिए डिज़ाइन | वे निर्णय जो आगे बढ़ने की गुंजाइश छोड़ते हैं, और वे जो चुपचाप आपके इरादे से ज़्यादा वादा कर देते हैं |
| [0059](lessons/0059-features-and-the-minimum-version.md) | Features और Minimum Version | Feature को सिर्फ़ जोड़ना ही क्यों चाहिए, unification आपकी मान्यताओं के साथ क्या करता है, और minimum version घोषित करना असल में क्या वादा करता है |
| [0060](lessons/0060-workspaces-and-release.md) | Workspaces और Release | Crate को उस बिंदु तक लाना जहाँ publish करना एक command हो, और वह command असल में क्या करती है |
| [0061](lessons/0061-the-api-guidelines.md) | API Guidelines | वह checklist जिस पर ecosystem पहले ही सहमत है, कौन-सी बातें सबसे ज़्यादा मायने रखती हैं, और उसे अंधानुकरण के बिना कैसे इस्तेमाल करें |
| [0062](lessons/0062-reading-the-source-and-the-rfcs.md) | Source और RFCs पढ़ना | ऐसे सवाल का उत्तर देना जिसका documentation नहीं देता, standard library, tracking issues और RFCs से |
| [0063](lessons/0063-reviewing-rust.md) | Rust की समीक्षा | किसी और के Rust में क्या देखना है, किस क्रम में, और कौन-सी टिप्पणियाँ करने लायक हैं |
| [0064](lessons/0064-the-test-attribute-and-cargo-test.md) | Test Attribute और cargo test | Doctest doc comment में रहता है और उदाहरण चलाता है; #[test] function crate के अपने source में रहता है और वह साधारण रूप है जो लगभग सारी Rust testing असल में लेती है, और cargo test दोनों को एक ही command के तहत चलाता है, बिना उनके एक ही तंत्र होने के |
| [0065](lessons/0065-unit-versus-integration-tests.md) | Unit Tests बनाम Integration Tests | #[test] function कहाँ रहता है यह तय करता है कि वह क्या देख सकता है: #[cfg(test)] के तहत code वाली ही file, जहाँ हर private item तक पहुँच है, या अलग tests/ directory जो सिर्फ़ वही देखती है जो आपने सचमुच public बनाया |
| [0066](lessons/0066-organising-tests-for-a-library.md) | Library के लिए Tests की व्यवस्था | Integration suite का आकार उससे तय होता है जो आपने पहले ही pub बनाया है, साझा setup ख़ास तौर पर tests/common/mod.rs में जाता है, और बिना lib.rs वाले binary का integration test हो ही नहीं सकता |
| [0067](lessons/0067-property-based-and-snapshot-testing.md) | Property-Based और Snapshot Testing | यह चरण 9 का capstone है: proptest सैकड़ों inputs generate करता है और failure को उस सबसे छोटे input तक सिकोड़ देता है जो अब भी property तोड़ता है, जबकि snapshot test एक चुने हुए input के output की तुलना ऐसे baseline से करता है जिसकी समीक्षा कोई इंसान पहले ही कर चुका है |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत, हर एक के साथ टिप्पणी कि वह क्या कवर करता है
- [Ownership और borrowing](reference/ownership-and-borrowing.md): नियम, Copy सूची, error codes, और हर एक का ईमानदार सुधार
- [Project](reference/the-project.md): वह crate जिसे अभ्यास पूरी रूपरेखा में बनाते हैं, और हर चरण के अंत में उसकी स्थिति क्या होनी चाहिए
- [Data और control](reference/data-and-control.md): चरण 2 की sheet, enum और Option और Result के निर्णयों, pattern के नियमों, और collections के साथ
- [Errors और API का आकार](reference/errors-and-api-shape.md): चरण 3 की sheet, error-type के निर्णयों, conversion के नियमों, और public API किससे बँधती है, के साथ
- [Traits और lifetimes](reference/traits-and-lifetimes.md): चरण 4 की sheet, dispatch निर्णय, coherence के नियमों, और lifetime error तालिका के साथ
- [Sharing और threads](reference/sharing-and-threads.md): चरण 5 की sheet, रणनीति की प्रक्रिया, हर sharing type की क़ीमत, और failure तालिका के साथ
- [Async](reference/async.md): चरण 6 की sheet, poll model, bounds, failure तालिका, और cancel safety कहाँ documented है, के साथ
- [Unsafe और performance](reference/unsafe-and-performance.md): चरण 7 की sheet, undefined-behaviour तालिका, हर tool क्या पकड़ता है, और माप के अनुशासन के साथ
- [विवेक](reference/judgment.md): चरण 8 की sheet, variance के नियमों, breaking-change तालिका, release checklist, और प्रामाणिकता के क्रम के साथ

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
