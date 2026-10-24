---
title: API Design
description: "ऐसा interface डिज़ाइन करें जिस पर दूसरे निर्भर हों: contract, उसकी errors, और उन्हें तोड़े बिना वह कैसे बदलता है"
type: topic
---

# सीखना: API Design

Versioned public API (REST/HTTP या gRPC) शुरू से डिज़ाइन कर सकें, और किसी मौजूदा API को आगे बढ़ा सकें, यानी उसका contract उन clients को तोड़े बिना बदल सकें जो उस पर निर्भर हैं।

**नवीनतम पाठ:** [19. GraphQL कहाँ फ़िट होता है](lessons/0019-where-graphql-fits.md)

## सफलता कैसी दिखती है

- बताए गए use case के लिए REST/HTTP या gRPC API का contract, उसके error model समेत, डिज़ाइन करें।
- किसी मौजूदा API के contract को (field या endpoint जोड़ना, deprecate करना या बदलना) clients को तोड़े बिना आगे बढ़ाएँ, और इस्तेमाल की गई versioning या migration रणनीति समझाएँ।
- Authentication, authorization और rate limiting को उस contract का हिस्सा मानें जिस पर client निर्भर है, न कि बाद में अलग से जोड़ी गई चीज़।

## सीमाएँ

- HTTP या RPC के साथ service बनाने का पेशेवर अनुभव माना गया है; API design का कोई औपचारिक अध्ययन ज़रूरी नहीं।
- REST/HTTP और gRPC दोनों कवर होते हैं, क्योंकि mission की गारंटियाँ दोनों पर लागू होती हैं।

## दायरे से बाहर

- एक codebase के भीतर compiler से असंभव state को अस्वीकार करवाना: उस सीमा के लिए [`programming/typescript`](../../programming/typescript/) देखें। यह workspace वही सहज समझ ऐसी सीमा के पार लागू करता है जहाँ कोई साझा compiler नहीं है।

## पूरी रूपरेखा

बारह चरण, contract से लेकर asynchronous delivery तक, और फिर असली व्यवहार के सामने contract को ही सत्यापित करने तक। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. Contract | 0001 | Client जिस पर भरोसा कर सकता है वह documented हिस्से से बड़ा है (Hyrum's Law) | Contract की documented सतह से आगे की निहित सतह का नाम बता सकें |
| 2. Error models | 0002 से 0003 | HTTP status codes, RFC 9457 Problem Details, gRPC status codes | बताए गए API के लिए error model डिज़ाइन कर सकें |
| 3. REST/HTTP design | 0004 से 0005 | Resource modeling, pagination और filtering, AIP शैली का मार्गदर्शन | बताए गए use case के लिए REST contract डिज़ाइन कर सकें |
| 4. gRPC design | 0006 से 0007 | proto3, service design, streaming | उसी use case के लिए gRPC contract डिज़ाइन कर सकें |
| 5. Versioning और evolution | 0008 से 0009 | Additive बदलाव, deprecation, migration रणनीति | किसी मौजूदा API के contract को उसके clients तोड़े बिना आगे बढ़ा सकें |
| 6. Contract के रूप में auth, authz और rate limiting | 0010 | इन्हें उस चीज़ का हिस्सा मानना जिस पर client निर्भर है, बाद में सोची गई चीज़ नहीं | Auth और rate limiting को contract के रूप में डिज़ाइन कर सकें, अलग से जोड़ी गई चीज़ के रूप में नहीं |
| 7. Idempotency और सुरक्षित retries | 0011 | `Idempotency-Key` header, idempotency fingerprints, और retry बनाम concurrent request का अंतर | ऐसा idempotency तंत्र डिज़ाइन कर सकें जो non-idempotent method को retry के लिए सचमुच सुरक्षित बना दे |
| 8. Contract के रूप में HTTP caching | 0012 | `ETag`, weak बनाम strong validators, conditional requests, `If-Match` optimistic concurrency, `Cache-Control` | Caching और concurrency-control का contract डिज़ाइन कर सकें, और जानें कि हर conditional header को किस strength की तुलना चाहिए |
| 9. Long-running operations और async delivery | 0013 से 0014 | Operation resource और polling, webhook signing, retries, और ordering | Async contract (poll किया गया operation या push किया गया webhook) और उसकी failure, retry, और ordering गारंटियाँ डिज़ाइन कर सकें |
| 10. Bulk operations और partial responses | 0015 | Atomic बनाम partial-success batch methods, हर item की error reporting, field masks | Batch method के failure semantics और partial-response contract डिज़ाइन कर सकें |
| 11. Machine-readable contract | 0016 से 0017 | Generated artifacts के रूप में OpenAPI documents और `.proto` files, Buf, Spectral, और oasdiff से breaking-change detection | समझा सकें कि machine-readable contract क्या संभव बनाता है, और style linter breaking-change detector से कैसे अलग है |
| 12. Contract testing और GraphQL की जगह | 0018 से 0019 | Consumer-driven contract testing और `can-i-deploy`, और REST व gRPC के मुक़ाबले GraphQL कहाँ बैठता है | समझा सकें कि contract test schema से आगे असली व्यवहार को कैसे सत्यापित करता है, और GraphQL के versionless evolution को इस रूपरेखा की REST/gRPC सामग्री के सामने सटीक रूप से रख सकें |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-the-contract.md) | Contract | Client जिस पर भरोसा कर सकता है वह आपके document किए गए हिस्से से बड़ा है, और design को दोनों का हिसाब रखना होता है |
| [0002](lessons/0002-http-status-codes-and-error-semantics.md) | HTTP Status Codes और Error Semantics | Status code client से safety, idempotency, और आगे क्या करना है, इनके बारे में असल में क्या वादा करता है, अस्पष्ट 2xx/4xx/5xx समूहों से आगे |
| [0003](lessons/0003-problem-details-and-grpc-status-codes.md) | RFC 9457 Problem Details और gRPC Status Codes | HTTP के लिए संरचित, machine-readable error format, gRPC की समानांतर status-code शब्दावली, और ऐसा एक error model डिज़ाइन करना जो दोनों पर काम करे |
| [0004](lessons/0004-resource-modeling-for-rest.md) | REST के लिए Resource Modeling | REST API को verbs के बजाय nouns और state के इर्द-गिर्द क्यों model करता है, और resource hierarchy यह कैसे तय करती है कि URL का मतलब क्या है |
| [0005](lessons/0005-pagination-and-filtering.md) | Pagination, Filtering, और REST Contract का डिज़ाइन | बड़े पैमाने पर cursor-based pagination offsets से बेहतर क्यों है, filtering स्थिर contract कैसे बना रहता है, और resource modeling को जोड़कर पूरा REST design बनाना |
| [0006](lessons/0006-proto3-and-grpc-service-design.md) | Proto3 और gRPC Service Design | proto3 के field numbers, न कि field names, असली wire contract कैसे हैं, और gRPC service resources के बजाय RPC methods के इर्द-गिर्द कैसे संरचित होती है |
| [0007](lessons/0007-grpc-streaming.md) | gRPC Streaming और उसी Use Case का डिज़ाइन | gRPC RPC के चार प्रकार, हर एक कब फ़िट होता है, और एक ही use case को REST और gRPC दोनों contracts के रूप में डिज़ाइन करना |
| [0008](lessons/0008-additive-changes-and-deprecation.md) | Additive बदलाव और Deprecation | जोड़ना आम तौर पर सुरक्षित क्यों है और हटाना या मतलब बदलना आम तौर पर क्यों नहीं, और field या endpoint को clients को तुरंत तोड़े बिना कैसे deprecate करें |
| [0009](lessons/0009-versioning-and-migration-strategy.md) | Versioning और Migration रणनीति | हर मौजूदा integration को एक साथ तोड़े बिना सचमुच का breaking change कैसे ship करें, Stripe की versioning रणनीति को हल किए गए उदाहरण के रूप में लेकर |
| [0010](lessons/0010-auth-authz-and-rate-limiting-as-contract.md) | Contract के रूप में Auth, Authz, और Rate Limiting | सिर्फ़ tokens नहीं बल्कि scopes, और सिर्फ़ 429 नहीं बल्कि दिखने वाली rate-limit state, यही access control और quotas को सोचे-समझे contract का हिस्सा क्यों बनाते हैं |
| [0011](lessons/0011-idempotency-keys-and-safe-retries.md) | Idempotency Keys और सुरक्षित Retries | अकेली key सिर्फ़ deduplicate करती है; fingerprint ही server को बताता है कि दोहराई गई key वही request है जो retry हुई या कोई दूसरी जो ग़लती से उसे दोबारा इस्तेमाल कर रही है, और जो retry मूल request के चलते रहने के दौरान पहुँचे उसे replay नहीं, conflict मिलता है |
| [0012](lessons/0012-http-caching-as-contract.md) | Contract के रूप में HTTP Caching | वही ETag validator दो अलग काम करता है, इस पर निर्भर कि उसे कौन-सी तुलना चाहिए: बेकार download छोड़ने के लिए weak तुलना काफ़ी है, पर किसी और के concurrent write को पकड़ने के लिए सिर्फ़ strong तुलना सुरक्षित है |
| [0013](lessons/0013-the-operation-resource-and-polling.md) | Operation Resource और Polling | Long-running method block करने के बजाय promise जैसा resource लौटाता है, और execution के दौरान की failure उस failure से अलग ढंग से report होती है जो operation को शुरू ही नहीं होने देती |
| [0014](lessons/0014-webhooks-and-callbacks-as-delivery.md) | Delivery के रूप में Webhooks और Callbacks | Poll होने का इंतज़ार करने के बजाय notification push करना यह उलट देता है कि request कौन शुरू करता है, और ठीक इसी उलटाव के कारण signing, retries, और ordering, तीनों को पाने वाले छोर पर अपना स्पष्ट contract चाहिए |
| [0015](lessons/0015-bulk-operations-and-partial-responses.md) | Bulk Operations और Partial Responses | Batch method को पहले से चुनना होता है कि वह all-or-nothing ढंग से fail होगा या हर item की सफलता और विफलता report करेगा, और fields का subset माँगने वाले client को वह subset उस body के बाहर माँगना होता है जिसे वह आकार दे रहा है |
| [0016](lessons/0016-openapi-and-protobuf-as-artifacts.md) | Artifacts के रूप में OpenAPI और Protobuf | जब contract सिर्फ़ गद्य के बजाय machine-readable document के रूप में मौजूद हो, तो document ख़ुद ऐसी चीज़ बन जाता है जिसे version, review किया जाए और जिससे दूसरी चीज़ें generate हों, न कि बाद में लिखा गया विवरण |
| [0017](lessons/0017-breaking-change-linting.md) | Breaking-Change Linting | Contract की style जाँचने वाला linter और यह जाँचने वाला diff tool कि उसने client तोड़ा या नहीं, दो अलग सवालों के उत्तर दे रहे हैं, और diff tool से भी तीन में से सही सवाल पूछना पड़ता है |
| [0018](lessons/0018-contract-testing.md) | Contract Testing | Schema artifact आकार जाँचता है और breaking-change linter compatibility, पर दोनों में से कोई पुष्टि नहीं करता कि provider असल में वैसा व्यवहार करता है जैसी असली consumer के tests उम्मीद करते हैं, और contract test यही बात record किए गए उदाहरण interactions से सत्यापित करता है |
| [0019](lessons/0019-where-graphql-fits.md) | GraphQL कहाँ फ़िट होता है | GraphQL वही versioning समस्या, जिस पर इस workspace ने दो पाठ लगाए, हर request को पहले से field mask बनाकर सुलझाता है, इस क़ीमत पर कि उसका contract ऐसा है जिस पर इस workspace के tools लागू नहीं होते |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत
- [Error Models](reference/error-models.md): HTTP status codes, Problem Details के members और gRPC status codes साथ-साथ, उस समय के लिए जब आप error model डिज़ाइन कर रहे हों, न कि यह सीख रहे हों कि वह contract क्यों है
- [REST Resource Design](reference/rest-resource-design.md): resource names, standard और custom methods, pagination और filtering, उस AIP नियम के साथ जिसे हर निर्णय को पूरा करना होता है
- [gRPC Design](reference/grpc-design.md): proto3 field numbers, कौन-से schema बदलाव binary wire पर सुरक्षित हैं और कौन-से JSON तोड़ते हैं, चार RPC प्रकार, और वे call semantics जो gRPC contract विरासत में पाता है
- [Versioning और Evolution](reference/versioning-and-evolution.md): कौन-से बदलाव किस तरह की compatibility तोड़ते हैं, वे headers जो deprecation को tooling के लिए दृश्य बनाते हैं, और चुनने के लिए versioning models
- [Auth और Rate Limiting](reference/auth-and-rate-limiting.md): contract के रूप में scopes और grant types, वे error codes जो resource server client को देने के लिए बाध्य है, और RateLimit fields जो quota को उस तक पहुँचने से पहले दृश्य बनाते हैं

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
