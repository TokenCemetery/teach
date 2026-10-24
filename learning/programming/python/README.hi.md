---
title: Python
description: "Production में Python को अपने हाथ में लें: उसे typed, tested, packaged और profiled रूप में ship करें"
type: topic
---

# सीखना: Python

वह engineer बनें जिस पर team में Python की ज़िम्मेदारी के लिए भरोसा किया जाए: typed, tested, packaged Python service या tool ship कर सकें, अंदाज़ा लगाने के बजाय traceback या profile से मूल कारण तक पहुँच सकें, और ठोस रूप से बता सकें कि किसी का Python की dynamism का चतुर इस्तेमाल उन्हें नुक़सान क्यों पहुँचाने वाला है।

**यहाँ से शुरू करें:** [0001. Names Bindings हैं, Boxes नहीं](lessons/0001-names-are-bindings.md)
**नवीनतम पाठ:** [0044. विवेक](lessons/0044-judgment.md)

## सफलता कैसी दिखती है

- Code चलाने से पहले अनुमान लगाएँ कि mutable default argument, loop variable पर closure, और साझा list क्या करते हैं।
- ऐसा package ship करें जो उस machine पर install होकर चले जिस पर वह लिखा नहीं गया था।
- ऐसे type hints जोड़ें जिन्हें checker सत्यापित करे, और वह जो report करे उसे चुप कराने के बजाय ठीक करें।
- ऐसे `pytest` tests लिखें जो जानकारी देते हुए fail हों, copy किए गए test bodies के बजाय fixtures और parametrisation का इस्तेमाल करते हुए।
- Profiler से धीमा हिस्सा ढूँढें और माप से सुधार साबित करें।
- Workload के आकार के आधार पर threads, processes और `asyncio` में से चुनें, और बताएँ कि GIL क्या रोकता है और क्या नहीं।
- जब data model को dunder method या context manager की ज़रूरत हो तो उसे implement करें, और पहचानें कि कब साधारण function बेहतर जवाब है।
- किसी के Python की समीक्षा करें और सटीक रूप से बताएँ कि वहाँ class, metaclass, या inheritance chain ग़लत औज़ार क्यों है।

## सीमाएँ

- Python का कोई पूर्व अनुभव नहीं माना गया है। किसी दूसरी भाषा का अनुभव शुरुआती चरणों को छोटा कर देता है पर ज़रूरी नहीं है, और वह ऐसी आदतें लाता है जिनकी सज़ा Python चुपचाप देता है: जहाँ function काफ़ी हो वहाँ class, जहाँ comprehension बेहतर पढ़ा जाए वहाँ loop, ऐसी रक्षात्मक copy जो भाषा पहले ही बना चुकी है।
- किसी भी supported OS पर सिर्फ़ CPython और terminal चाहिए। रूपरेखा में किसी चीज़ के लिए paid tooling, cloud account, या दूसरी machine की ज़रूरत नहीं।
- पूरी रूपरेखा में CPython reference implementation है। दूसरे implementations सिर्फ़ वहीं आते हैं जहाँ व्यवहार सचमुच अलग है।
- अभ्यास छोटे programs हैं जो एक बैठक में पूरे हो जाते हैं। उन्हें कई दिनों में फैलाना ही तरीक़ा है, कोई असुविधा नहीं।
- Typing और packaging भाषा से तेज़ी से बदलते हैं। Version पर निर्भर दावों को मौजूदा documentation और संबंधित PEP से जाँचा जाता है, और जो पाठ किसी release पर निर्भर है वह बताता है कि कौन-सा।

## दायरे से बाहर

- Web frameworks अपने-आप में विषय के रूप में: Django, FastAPI, Flask।
- विषय के रूप में scientific और machine-learning stack: NumPy, pandas, PyTorch। उस सीमा के लिए [`llm/finetuning`](../../llm/finetuning/) देखें।
- Index पर publish किए गए wheels से आगे का distribution: conda, OS packages, frozen single-file binaries।
- CPython के भीतरी हिस्से, उस बिंदु से आगे जहाँ वे program के व्यवहार का अनुमान लगाने में मदद करना बंद कर देते हैं: bytecode, C API, extension modules लिखना।
- Python 2, और उससे migration।
- Container images: wheel और उसके interpreter को image में रखना, और उस container को चलाना, सुरक्षित करना और debug करना, [`infrastructure/containers`](../../infrastructure/containers/) है।

## पूरी रूपरेखा

सात चरण, शून्य से senior तक। यह पाठों की सूची नहीं है: एक चरण में कई पाठ लगते हैं, और सीमाएँ लचीली हैं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. नींव | 0001 से 0007 | Objects और names, mutability और aliasing, lists, dicts, sets, tuples, truthiness, comprehensions, functions और argument passing | Code चलाए बिना aliasing और mutation का अनुमान लगा सकें |
| 2. Idiom | 0008 से 0014 | Iterators और generators, context managers, control flow के रूप में exceptions, `dataclasses`, modules और packages, जानने लायक standard library | Loop और `try/finally` हाथ से लिखने के बजाय generator या context manager उठाएँ |
| 3. Types और tooling | 0015 से 0021 | Annotations, generics, `Protocol`, checker की सख़्ती, linting और formatting, virtual environments, dependency और project management, wheel build करना | सख़्त checker pass हो, और कोई और परिणाम को install कर सके |
| 4. Data model | 0022 से 0027 | Dunder methods, `__init__` बनाम `__new__`, properties, descriptors, class बनाम instance attributes, method resolution order, metaclasses लगभग कभी जवाब क्यों नहीं होतीं | Type को जिस protocol की ज़रूरत है उसे implement करें, और बता सकें कि कब नहीं करना है |
| 5. Testing | 0028 से 0033 | `pytest` की कार्यप्रणाली, fixtures और scope, parametrisation, property-based testing, किसका mock बनना चाहिए और किसका नहीं, लक्ष्य के बजाय संकेत के रूप में coverage | ऐसा test suite हो जिसने किसी इंसान से पहले regression पकड़ा |
| 6. Concurrency और performance | 0034 से 0039 | Threads, processes, `asyncio`, GIL असल में क्या क्रमबद्ध करता है, event loop के भीतर blocking calls, profiling, attribute lookup और allocation की क़ीमत | Workload से concurrency model चुनें और profile से जीत साबित करें |
| 7. विवेक | 0040 से 0044 | API और package design, deprecation, समीक्षा, जवाबों के लिए standard library और PEPs पढ़ना | निर्णय लेने और उसे किसी और को समझाने के लिए भरोसेमंद |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-names-are-bindings.md) | Names Bindings हैं, Boxes नहीं | Assignment किसी name को object से bind करता है और उसकी copy कभी नहीं बनाता, इसलिए दो names का मतलब एक ही चीज़ हो सकता है |
| [0002](lessons/0002-mutability-and-copying.md) | Mutability और Copying | Mutability object की होती है, इसलिए अपरिवर्तनीय container भी बदलने वाली चीज़ रख सकता है |
| [0003](lessons/0003-lists-and-slicing.md) | Lists और Slicing | Slice copy बनाता है, in-place methods None लौटाते हैं, और += उसे mutate करता है जिसे + फिर से बनाता |
| [0004](lessons/0004-dicts-and-sets.md) | Dicts और Sets | Keys hashable होनी चाहिए, हर इरादे के लिए lookup का एक सही idiom है, और view snapshot नहीं है |
| [0005](lessons/0005-truthiness-none-and-equality.md) | Truthiness, None और Equality | ख़ाली falsy है पर None नहीं, इसलिए ग़लत default idiom शून्य और ख़ाली string को अस्वीकार कर देता है |
| [0006](lessons/0006-functions-and-arguments.md) | Functions और Arguments | Defaults definition पर एक बार evaluate होते हैं, और caller आपका किया हर mutation देखता है |
| [0007](lessons/0007-comprehensions.md) | Comprehensions | Container बनाने वाला एक expression, अपने scope और सम्मान करने लायक सीमा के साथ |
| [0008](lessons/0008-the-iteration-protocol.md) | Iteration Protocol | for किसी भी चीज़ पर क्यों काम करता है, और उनमें से कुछ चीज़ों पर सिर्फ़ एक बार loop क्यों हो सकता है |
| [0009](lessons/0009-generators.md) | Generators | ऐसा function जो रुकता है, अपनी local state रखता है, और सिर्फ़ माँगे जाने पर values देता है |
| [0010](lessons/0010-exceptions.md) | Exceptions | अनुमति के बजाय माफ़ी माँगना, और ठीक वही पकड़ना जिसे आप संभाल सकते हैं |
| [0011](lessons/0011-context-managers.md) | Context Managers | पक्के निकास वाला block, और उसे छह lines में कैसे लिखें |
| [0012](lessons/0012-dataclasses.md) | Dataclasses | Generate किए गए init, repr और equality, और data के गट्ठर के लिए सही आकार चुनना |
| [0013](lessons/0013-modules-and-packages.md) | Modules और Packages | Module एक बार चलता है, import एक name bind करता है, और ये दोनों मिलकर आपकी देखी हर import error कैसे पैदा करते हैं |
| [0014](lessons/0014-the-standard-library.md) | Standard Library | वे modules जो वह code हटा देते हैं जिसे आप लिखने वाले थे, और वे जो किसी dependency से बचाते हैं |
| [0015](lessons/0015-annotations-are-claims.md) | Annotations दावे हैं | Interpreter उन्हें store करता है और कभी जाँचता नहीं, और यही उन्हें लिखने लायक बनाता है |
| [0016](lessons/0016-making-a-checker-useful.md) | Checker को उपयोगी बनाना | सख़्ती configure करना, error codes पढ़ना, और चुप कराने के बजाय narrowing करना |
| [0017](lessons/0017-generics-and-protocols.md) | Generics और Protocols | Function से गुज़रते हुए element type को बनाए रखना, और class के बजाय आकार को type देना |
| [0018](lessons/0018-types-at-the-boundary.md) | सीमा पर Types | JSON, environment और database rows से आए Any को ऐसी चीज़ में बदलना जिस पर checker तर्क कर सके |
| [0019](lessons/0019-environments-and-dependencies.md) | Environments और Dependencies | हर project के लिए isolation, requirement और lock का फ़र्क़, और कौन क्या pin करता है |
| [0020](lessons/0020-building-a-package.md) | Package Build करना | Wheel क्या है, metadata को क्या कहना होता है, और साबित करना कि artefact install होता है |
| [0021](lessons/0021-lint-and-format.md) | Lint और Format | Style की बहस ख़त्म करना, और rules के वे परिवार जो असली defects ढूँढते हैं |
| [0022](lessons/0022-attribute-lookup.md) | Attribute Lookup | Dot notation असल में कहाँ देखता है, और class attribute हर instance द्वारा साझा क्यों होता है |
| [0023](lessons/0023-properties-and-descriptors.md) | Properties और Descriptors | एक भी caller बदले बिना attribute को code में बदलना |
| [0024](lessons/0024-dunder-methods.md) | Dunder Methods | Type को कौन-से protocols implement करने चाहिए, और कौन-से दूसरों पर fallback करते हैं |
| [0025](lessons/0025-construction.md) | Construction | `__init__` क्या नियंत्रित नहीं करता, कब `__new__` ज़रूरी है, और अपने constructors को नाम देना |
| [0026](lessons/0026-inheritance-and-mro.md) | Inheritance और MRO | super असल में क्या करता है, क्रम compute क्यों होता है, और कब composition जीतता है |
| [0027](lessons/0027-metaclasses-and-why-not.md) | Metaclasses, और क्यों नहीं | Class statement असल में क्या करता है, और वे चार hooks जो लगभग हर metaclass की जगह ले लेते हैं |
| [0028](lessons/0028-what-a-test-asserts.md) | Test क्या Assert करता है | हर test में एक व्यवहार, ऐसा failure message जिसे debugger की ज़रूरत न हो, और साधारण assert |
| [0029](lessons/0029-fixtures.md) | Fixtures | ऐसी dependency के रूप में setup जिसे test माँगता है, ऐसे teardown के साथ जो कुछ भी हो, चलता है |
| [0030](lessons/0030-parametrisation.md) | Parametrisation | एक test body, कई cases, और ऐसी failure जो टूटे case का नाम बताए |
| [0031](lessons/0031-test-doubles.md) | Test Doubles | क्या बदलना है, क्या छोड़ना है, और patch वह path क्यों लेता है जहाँ name इस्तेमाल होता है |
| [0032](lessons/0032-property-based-testing.md) | Property-Based Testing | बताना कि हमेशा क्या सही रहना चाहिए, और library को वह input ढूँढने देना जो उसे तोड़ता है |
| [0033](lessons/0033-coverage-and-confidence.md) | Coverage और भरोसा | 100 प्रतिशत कुछ भी साबित क्यों नहीं करता, संख्या किस काम की है, और किन tests पर भरोसा करें |
| [0034](lessons/0034-the-gil-precisely.md) | GIL, सटीक रूप में | वह क्या क्रमबद्ध करता है, किसकी रक्षा नहीं करता, और उसके बिना क्या बदलता है |
| [0035](lessons/0035-threads-and-shared-state.md) | Threads और साझा State | कच्चे threads के बजाय pool, lock के बजाय queue, और वह exception जिसे किसी ने नहीं देखा |
| [0036](lessons/0036-processes-and-interpreters.md) | Processes और Interpreters | Computation के लिए असली parallelism, और सीमा के पार data भेजने की क़ीमत |
| [0037](lessons/0037-asyncio.md) | asyncio | एक thread, हज़ारों इंतज़ार, और वह blocking call जो उन सबको अटका देती है |
| [0038](lessons/0038-choosing-a-model.md) | Model चुनना | एक सवाल इसे तय करता है, और माप बाक़ी को सुलझाता है |
| [0039](lessons/0039-measuring-before-optimising.md) | Optimise करने से पहले मापना | समय असल में कहाँ जाता है, और आपको सिखाए गए micro-optimisations अब क्यों बेकार हैं |
| [0040](lessons/0040-designing-an-api.md) | API का डिज़ाइन | Signature ही contract है, और जो कुछ भी observable है वह contract बन जाता है, चाहे आपका इरादा हो या नहीं |
| [0041](lessons/0041-changing-a-published-api.md) | Publish की गई API बदलना | ऐसा deprecation जो users सचमुच देखें, और breaking change किसे गिनते हैं |
| [0042](lessons/0042-reviewing-python.md) | Python की समीक्षा | क्या देखना है, किस क्रम में, और defect को पसंद से कैसे अलग करें |
| [0043](lessons/0043-reading-the-source.md) | Source पढ़ना | Documentation रुक जाए तो standard library और PEPs से जवाब पाना |
| [0044](lessons/0044-judgment.md) | विवेक | पिछले चरणों के नियम कब तोड़ने हैं, और उस निर्णय का बचाव कैसे करें |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत, हर एक के साथ टिप्पणी कि वह क्या कवर करता है
- [Mutability और copying](reference/mutability-and-copying.md): कौन-से types mutate होते हैं, हर copy idiom क्या copy करता है, और उसे कौन देख सकता है
- [Iteration और generators](reference/iteration-and-generators.md): क्या एक बार में ख़त्म हो जाता है, क्या दूसरी बार गुज़रने में बचता है, और itertools का कौन-सा tool फ़िट होता है
- [Exceptions और cleanup](reference/exceptions-and-cleanup.md): hierarchy, हर clause क्या गारंटी देता है, और कौन-सा built-in raise करना है
- [Typing](reference/typing.md): मौजूदा लेखन रूप, narrowing के रूप, error codes, और सीमा पर कौन-सा आकार इस्तेमाल करना है
- [Project और packaging](reference/project-and-packaging.md): टिप्पणियों के साथ एक pyproject.toml, specifier का व्याकरण, और publish करने से पहले की जाँचें
- [Data model](reference/data-model.md): attribute lookup का क्रम, dunder map, descriptor protocol, और कौन-सा hook metaclass की जगह लेता है
- [Testing](reference/testing.md): fixture scopes, parametrisation के रूप, कौन-सा double उठाना है, और coverage report पढ़ना
- [Concurrency और performance](reference/concurrency-and-performance.md): किस workload के लिए कौन-सा model, उसके पीछे की मापी गई संख्याएँ, और profile कैसे पढ़ें
- [API और समीक्षा](reference/api-and-review.md): signature के निर्णय, breaking किसे गिनते हैं, समीक्षा checklist, और जवाब कहाँ मिलेगा

## यह कैसे काम करता है

रूपरेखा पूरी है: सातों चरण लिखे जा चुके हैं, पाठ 0001 से पाठ 0044 तक। इन्हें क्रम से करें, या उस चरण से शुरू करें जिसका "कब पूरा माना जाए" आप अभी साबित नहीं कर सकते।

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
