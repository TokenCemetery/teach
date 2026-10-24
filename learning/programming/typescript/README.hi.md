---
title: TypeScript
description: "TypeScript codebase को अपने हाथ में लें: compiler से उन states को अस्वीकार करवाएँ जो मौजूद नहीं होनी चाहिए"
type: topic
---

# सीखना: TypeScript

वह engineer बनें जिस पर team में TypeScript codebase की ज़िम्मेदारी के लिए भरोसा किया जाए: domain को ऐसे model कर सकें कि compiler उन states को अस्वीकार करे जो मौजूद नहीं होनी चाहिए, वज़न उठाने वाले code से type assertions को बाहर रख सकें, यह मानने के बजाय कि types टिके रहे, runtime सीमा पार करने वाली चीज़ों को validate कर सकें, और किसी के types की समीक्षा करके ठोस रूप से बता सकें कि कोई चतुर generic जितना देता है उससे ज़्यादा क़ीमत क्यों ले रहा है।

**यहाँ से शुरू करें:** [0001. Values और Coercion](lessons/0001-values-and-coercion.md)
**नवीनतम पाठ:** [0049. निर्णय लेने के लिए भरोसेमंद](lessons/0049-trusted-to-make-the-call.md), जो रूपरेखा को पूरा करता है

## सफलता कैसी दिखती है

- Code चलाने से पहले, और type system की मदद के बिना, अनुमान लगाएँ कि JavaScript coercion, closures, `this` और event loop के साथ क्या करता है।
- अवैध states के set को ऐसे type में बदलें जिसे compiler अस्वीकार करे, और `never` से exhaustiveness साबित करें।
- `as` उठाने के बजाय generic के error message को उसके कारण तक पढ़ें।
- ठीक-ठीक बताएँ कि compilation में क्या बचता है और क्या erase होता है, और बाहर से program में आने वाली हर value को validate करें।
- Compiler को इरादे के साथ configure करें: बताएँ कि हर strictness flag क्या देता है और module और target settings वैसी क्यों हैं जैसी हैं।
- ऐसा generic function लिखें जिसका inference काम करे, ताकि callers कुछ भी annotate न करें।
- ऐसा package publish करें जिसके types consumers के लिए इस्तेमाल योग्य हों, declaration output और उसके बताए exports समेत।
- Pull request की समीक्षा करें और सटीक रूप से बताएँ कि वहाँ conditional type, assertion, या `enum` ग़लत औज़ार क्यों है।

## सीमाएँ

- TypeScript का कोई पूर्व अनुभव नहीं माना गया है, और रूपरेखा जितना सिखाती है उससे ज़्यादा JavaScript भी नहीं। TypeScript JavaScript के ऊपर एक type system है, इसलिए JavaScript semantics वहाँ-वहाँ सिखाए जाते हैं जहाँ वे वह व्यवहार समझाते हैं जो type नहीं समझा सकता।
- पूरी रूपरेखा में compile-time और runtime की सीमा को सख़्त रेखा माना गया है, क्योंकि TypeScript की लगभग हर गंभीर ग़लती runtime के बारे में ऐसा दावा है जिसे सिर्फ़ compiler ने कभी जाँचा।
- किसी भी supported OS पर सिर्फ़ JavaScript runtime और terminal चाहिए, और जब किसी अभ्यास को सिर्फ़ type देखना हो तो online playground दोनों की जगह ले लेता है। कोई paid tooling नहीं, कोई cloud account नहीं, कोई framework नहीं।
- अभ्यास छोटे programs और छोटे type प्रयोग हैं जो एक बैठक में पूरे हो जाते हैं।
- TypeScript हर कुछ महीनों में release होता है और उन releases में type system सचमुच ज़्यादा अभिव्यंजक होता जाता है। Version पर निर्भर दावों को release notes से जाँचा जाता है, और जो पाठ किसी version पर निर्भर है वह बताता है कि कौन-सा।

## दायरे से बाहर

- Frameworks और UI libraries अपने-आप में विषय के रूप में: React, Angular, Vue, Svelte, Next.js।
- विषय के रूप में bundlers और monorepo tooling: webpack, Vite, esbuild, Turborepo। Module resolution compiler के अपने model से सिखाया जाता है, और उन tools को उसी से सहमत होना होता है।
- विषय के रूप में दूसरे runtimes: Deno, Bun, browser platform। वे सिर्फ़ वहीं आते हैं जहाँ व्यवहार सचमुच अलग है।
- अपने-आप में platform के रूप में Node.js: streams, clustering, native addons।
- खेल के रूप में type-level programming। Mapped और conditional types उस बिंदु तक सिखाए जाते हैं जहाँ वे caller के काम आते हैं, और चरण 6 साफ़ बताता है कि वह बिंदु कहाँ है।

## पूरी रूपरेखा

सात चरण, शून्य से senior तक। यह पाठों की सूची नहीं है: एक चरण में कई पाठ लगते हैं, और सीमाएँ लचीली हैं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. नीचे की JavaScript | 0001 से 0007 | Values और coercion, objects और prototypes, closures, `this`, modules, event loop, promises और async | Types के बिना अनुमान लगा सकें कि program runtime पर क्या करता है |
| 2. Values के ऊपर types | 0008 से 0014 | Primitives, arrays और tuples, unions, literal types, structural assignability, narrowing, function types, `readonly`, inference पहले से क्या जानता है | सिर्फ़ वहीं annotate करें जहाँ inference नहीं पहुँच सकता |
| 3. Strictness और compiler | 0015 से 0021 | `strict` परिवार, एक-एक flag करके, strict जैसे वे flags जिन्हें `strict` अब भी छोड़ देता है, `unknown` बनाम `any`, assertions बनाम declarations, `tsconfig`, module resolution, `target` और `lib` | Strictness चालू रखें और वह जो report करे उसे दबाने के बजाय ठीक करें, और वे checks चालू करें जिन्हें `strict` छोड़ देता है |
| 4. Modelling | 0022 से 0028 | Discriminated unions, `never` से exhaustiveness, branded types, generics और constraints, `satisfies`, interface बनाम type alias | अवैध states दर्शाई ही नहीं जा सकतीं, और इसे साबित compiler करता है |
| 5. Runtime सीमा | 0029 से 0035 | क्या erase होता है, declaration files, किनारे पर input validate करना, values के रूप में errors, untyped और ग़लत typed dependencies का इस्तेमाल | कोई value बिना validation के program में नहीं आती, और कोई assertion वज़न नहीं उठाता |
| 6. Type-level औज़ार | 0036 से 0042 | Mapped और conditional types, `infer`, template literal types, variance और assignability, library APIs के लिए inference, compiler performance | ऐसी API लिखें जिसके types उसके callers के काम आएँ, और चतुराई से पहले रुक जाएँ |
| 7. विवेक | 0043 से 0049 | Public type surface publish करना, types में breaking change किसे गिनते हैं, समीक्षा, release notes और compiler के अपने declarations पढ़ना | निर्णय लेने और उसे किसी और को समझाने के लिए भरोसेमंद |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-values-and-coercion.md) | Values और Coercion | सात primitives, दो ख़ाली values, और ऐसा equality operator जो तुलना से पहले convert करता है |
| [0002](lessons/0002-objects-are-references.md) | Objects References हैं | const दोबारा bind होने से रोकता है, spread एक स्तर copy करता है, और readonly run time पर ग़ायब हो जाता है |
| [0003](lessons/0003-prototypes-and-classes.md) | Prototypes और Classes | Property lookup एक chain पर चलता है, और class syntax उस chain को बनाने का एक तरीक़ा है |
| [0004](lessons/0004-this-and-the-call-site.md) | this Call से तय होता है | this इस पर निर्भर है कि function कैसे call हुआ, इसलिए method को अलग निकालना उसे फेंक देता है |
| [0005](lessons/0005-scope-and-closures.md) | Scope और Closures | Closure value के बजाय binding को capture करता है, और let हर iteration के लिए एक binding बनाता है |
| [0006](lessons/0006-event-loop-and-promises.md) | Event Loop, Promises और await | Microtasks अगले timer से पहले ख़ाली होते हैं, और लगातार दो awaits क्रमिक होते हैं |
| [0007](lessons/0007-modules.md) | Modules | Imports hoist होते हैं और live bind होते हैं, और बिना import या export वाली file module नहीं है |
| [0008](lessons/0008-the-types-you-write.md) | आपके लिखे Types | Annotation की शब्दावली, और ऐसा compiler जो उसे configure करने से पहले ही आपत्ति करता है |
| [0009](lessons/0009-tuples-and-readonly.md) | Tuples और readonly | एक निश्चित length जिसे compiler reads पर लागू करता है और push पर भूल जाता है |
| [0010](lessons/0010-unions-and-literal-types.md) | Unions और Literal Types | एक से ज़्यादा संभावित type वाली value, और वह widening जो दिलचस्प type को फेंक देती है |
| [0011](lessons/0011-structural-assignability.md) | Structural Assignability | आकार तय करता है कि क्या कहाँ जाएगा, उस एक check को छोड़कर जो सिर्फ़ ताज़ा object literal पर चलता है |
| [0012](lessons/0012-narrowing.md) | Narrowing | Control flow compiler को बताता है कि union क्या बन गया है, और ठीक दो चीज़ें इसे वापस ले लेती हैं |
| [0013](lessons/0013-function-types.md) | Function Types | Parameters उसी दिशा में जाँचे जाते हैं जिसकी आप उम्मीद करते हैं, जब तक आपने method न लिखा हो |
| [0014](lessons/0014-what-inference-already-knows.md) | Inference पहले से क्या जानता है | Inference कहाँ तक पहुँचता है, ताकि जब आप annotation लिखें तो उसका कुछ मतलब हो |
| [0015](lessons/0015-what-strict-turns-on.md) | strict क्या चालू करता है | एक flag के पीछे सात checks, हर एक किसी ऐसी failure के साथ जिसे पकड़ने के लिए वह है |
| [0016](lessons/0016-the-checks-strict-leaves-out.md) | वे Checks जिन्हें strict छोड़ देता है | छह और checks जो रखने लायक हैं, एक जिसे compiler चालू करने से इनकार करता है, और एक जो कुछ भी नहीं करता |
| [0017](lessons/0017-unknown-instead-of-any.md) | any के बजाय unknown | एक type सब कुछ स्वीकार करता है और आपको कुछ नहीं करने देता, दूसरा सब कुछ स्वीकार करता है और कुछ नहीं जाँचता |
| [0018](lessons/0018-an-assertion-is-not-a-check.md) | Assertion Check नहीं है | Compiler को जाँचना बंद करने को कहने का हर तरीक़ा, और दावा ग़लत होने पर हर एक की क़ीमत |
| [0019](lessons/0019-reading-a-tsconfig.md) | tsconfig पढ़ना | Compiler किन files को देखता है, settings कहाँ से आती हैं, और generate हुई file वह क्यों कहती है जो कहती है |
| [0020](lessons/0020-target-and-lib.md) | target और lib | एक setting बदलती है कि क्या emit होता है और दूसरी बदलती है कि क्या मौजूद है, और दूसरी का नाम लेना default को फेंक देता है |
| [0021](lessons/0021-module-resolution.md) | Module Resolution | वही compiler options package.json के एक field के आधार पर उलटे फ़ैसले देते हैं |
| [0022](lessons/0022-discriminated-unions.md) | Discriminated Unions | एक साझा literal property, और ऐसा union जिसे compiler अलग-अलग कर सकता है |
| [0023](lessons/0023-exhaustiveness-with-never.md) | never से Exhaustiveness | Union में member जोड़ने से हर वह switch टूटना चाहिए जिसने उसे अनदेखा किया, और एक line ऐसा कर देती है |
| [0024](lessons/0024-illegal-states.md) | अवैध States को अदर्शनीय बनाना | आपका type जितनी states की अनुमति देता है उन्हें गिनें, फिर वे हटाएँ जो आपके domain में नहीं हैं |
| [0025](lessons/0025-branded-types.md) | Branded Types | Structural system के ऊपर nominal typing, और उसकी क़ीमत एक अकेला assertion |
| [0026](lessons/0026-generics-and-constraints.md) | Generics और Constraints | Type parameter caller से एक वादा है, और constraint वह है जो आपको उसे निभाने देता है |
| [0027](lessons/0027-satisfies.md) | satisfies | Type को आपके लिखे की जगह लेने दिए बिना किसी value को उस type के सामने जाँचें |
| [0028](lessons/0028-interface-or-type.md) | interface या type | एक टकराने वाले member को वहीं report करता है जहाँ आपने उसे लिखा और दूसरा कहीं और |
| [0029](lessons/0029-nothing-survives-to-run-time.md) | Run Time तक कुछ नहीं बचता | हर type ऐसे program के बारे में दावा है जो तब मौजूद ही नहीं रहता जब दावा मायने रखता |
| [0030](lessons/0030-unknown-at-the-edge.md) | किनारे पर unknown | हर वह जगह ढूँढें जहाँ value बाहर से आती है, और हर एक को एकमात्र ईमानदार type दें |
| [0031](lessons/0031-parsing-instead-of-asserting.md) | Assert करने के बजाय Parse करना | एक declaration जो runtime check और static type दोनों पैदा करता है |
| [0032](lessons/0032-type-predicates-and-assertion-functions.md) | Type Predicates और Assertion Functions | ऐसा signature जो check का वादा करता है, और ऐसी body जिससे कोई उसकी तुलना नहीं करता |
| [0033](lessons/0033-errors-as-values.md) | Values के रूप में Errors | Return type में failure ऐसी failure है जिसे संभालने के लिए compiler आपको मजबूर कर सकता है |
| [0034](lessons/0034-declaration-files.md) | Declaration Files | ऐसे code के types जिसे compiler कभी नहीं देखता, और उस वादे की क़ीमत क्या है |
| [0035](lessons/0035-when-the-declaration-lies.md) | जब Declaration झूठ बोले | Compiler declaration पर भरोसा करता है और runtime ने उसके बारे में कभी सुना ही नहीं |
| [0036](lessons/0036-mapped-types.md) | Mapped Types | किसी type की हर property को एक साथ बदलें, और वे हटाएँ जो आपको नहीं चाहिए |
| [0037](lessons/0037-conditional-types.md) | Conditional Types | ऐसा type जो branch करता है, और ऐसा union जिसे वह चुपचाप पहले अलग-अलग कर देता है |
| [0038](lessons/0038-infer.md) | infer | Caller से नाम लेने को कहने के बजाय किसी position से type निकालें |
| [0039](lessons/0039-template-literal-types.md) | Template Literal Types | ऐसा string pattern जिसे compiler जाँचता है, और वे key names जो वह बना सकता है |
| [0040](lessons/0040-variance-and-assignability.md) | Variance और Assignability | कोई type किस दिशा में जा सकता है, और वह array जो जानबूझकर इसे ग़लत करता है |
| [0041](lessons/0041-inference-for-library-apis.md) | Library APIs के लिए Inference | Signature को ऐसे डिज़ाइन करें कि caller कुछ भी annotate न करे |
| [0042](lessons/0042-knowing-when-to-stop.md) | कब रुकना है यह जानना | मापें कि चतुर type की क़ीमत क्या है, फिर उसे संभालने वाले के सामने उसे सही ठहराएँ |
| [0043](lessons/0043-what-counts-as-a-breaking-change.md) | Breaking Change किसे गिनते हैं | Publish किए गए type में कौन-से बदलाव consumer को तोड़ते हैं, और हर एक को किस दिशा में जाना होता है |
| [0044](lessons/0044-publishing-a-type-surface.md) | Type Surface Publish करना | जब consumer आपका package import करता है तो वह असल में क्या resolve करता है, और उनसे पहले इसे कैसे जाँचें |
| [0045](lessons/0045-the-consumers-settings-are-not-yours.md) | Consumer की Settings आपकी नहीं हैं | सख़्त consumer ढीले author के दावे विरासत में पाता है और उसके पास इसे देख पाने का कोई तरीक़ा नहीं |
| [0046](lessons/0046-the-typescript-that-does-not-erase.md) | वह TypeScript जो Erase नहीं होता | चार features जो ऐसा code emit करती हैं जो आपने नहीं माँगा, और वह flag जो उनका नाम लेता है |
| [0047](lessons/0047-settling-it-from-the-source.md) | Source से तय करना | कौन-सा document compiler के बारे में किसी सवाल का उत्तर देता है, और उसके साथ आने वाले declarations को कैसे पढ़ें |
| [0048](lessons/0048-reviewing-typescript.md) | TypeScript की समीक्षा | यह कहने के बजाय कि type जटिल दिखता है, उसकी क़ीमत का नाम लेना |
| [0049](lessons/0049-trusted-to-make-the-call.md) | निर्णय लेने के लिए भरोसेमंद | रूपरेखा का आख़िरी निर्णय, और वह जो compiler आपके लिए कभी करने वाला नहीं था |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत, हर एक के साथ टिप्पणी कि वह क्या कवर करता है
- [Coercion और equality](reference/coercion-and-equality.md): falsy values, `==` क्या convert करता है, कौन-सा default operator लिखें
- [Event loop और promises](reference/event-loop-and-promises.md): queue का क्रम, combinators, और async की वे ग़लतियाँ जिन्हें कोई compiler report नहीं करता
- [Values के ऊपर types](reference/types-over-values.md): हर annotation क्या देता है, inference कहाँ तक पहुँचता है, और वे छेद जिन्हें compiler जानबूझकर खुला छोड़ता है
- [Strictness और compiler](reference/strictness-and-the-compiler.md): कौन-सा flag कौन-सी failure पकड़ता है, कोई setting कहाँ से आती है, और import कैसे resolve होता है
- [Modelling](reference/modelling.md): कौन-सा आकार अवैध state को हटाता है, और कौन-सा declaration ग़लती को वहीं पकड़ता है जहाँ आपने की
- [Runtime सीमा](reference/the-runtime-boundary.md): values कहाँ आती हैं, उन्हें क्या जाँचता है, और कौन-से दावे कुछ भी नहीं जाँचता
- [Type-level औज़ार](reference/type-level-tools.md): कौन-सा construct कौन-सा type compute करता है, और वह test जो चतुर type को pass करना होता है
- [विवेक](reference/judgment.md): कौन-से बदलाव consumer को तोड़ते हैं, क्या erase नहीं होता, और source से निर्णय के पक्ष में तर्क कैसे दें

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
