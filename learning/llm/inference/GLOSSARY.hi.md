---
title: "शब्दावली"
description: "Inference के मानक शब्द"
type: glossary
---

# Inference शब्दावली

Train हो चुके model को serve करने के मानक शब्द: server memory में क्या रखता है, और latency व throughput पर उसके पास कौन-से उपाय हैं।

## शब्द

**Attention sink**:
किसी sequence के पहले कुछ tokens को उनकी असली सामग्री से परे मिलने वाला असामान्य रूप से बड़ा attention score। इसीलिए sliding-window cache से उन्हें हटाने पर पुराने context का धीरे-धीरे नुकसान नहीं होता, बल्कि गुणवत्ता अचानक ढह जाती है। सिर्फ़ उन शुरुआती tokens की KV entries को आम sliding window के साथ स्थायी रूप से cache में रखने से full attention का ज़्यादातर प्रदर्शन लौट आता है (StreamingLLM तकनीक)।
_बचें_: यह मान लेना कि हटाया गया कोई भी पुराना token उतना ही नुक़सान करता है (यह असमान वज़न सिर्फ़ शुरुआती "sink" tokens के पास होता है; window के बाहर के दूसरे पुराने tokens खोने पर गुणवत्ता धीरे-धीरे घटती है, ढहती नहीं)

**Cold start (serving)**:
Autoscaler के नई replica जोड़ने का फ़ैसला करने और उस replica के सचमुच कोई request serve कर पाने के बीच का अंतराल। इसमें ज़्यादातर समय बड़े model का checkpoint memory में load करने में जाता है, जो दसियों सेकंड ले सकता है और एक token generate करने के समय से कहीं ज़्यादा होता है।
_बचें_: इसे request-queueing की समस्या समझना (scheduler या router का इस पर कोई असर नहीं होता; यह पूरी तरह checkpoint के आकार और उस storage path से तय होता है जिससे उसे गुज़रना है)

**Constrained (guided) decoding**:
Sampling से पहले हर उस token को mask कर देना जो ज़रूरी structure (valid JSON, कोई grammar) तोड़ता हो, ताकि output का structure सिर्फ़ प्रोत्साहित नहीं बल्कि बनावट से ही गारंटीशुदा हो। Grammar को finite-state machine के रूप में देखकर और एक बार पहले से यह index बनाकर कि हर state से कौन-से tokens valid हैं, इसे प्रति token सस्ता रखा जाता है।
_बचें_: generation पूरा होने के बाद output की वैधता जाँचना (इससे कोई गारंटी नहीं मिलती, क्योंकि model हमेशा invalid token sample करने को आज़ाद था; sampling से पहले mask करना ही गारंटी को structural बनाता है)

**Cost per million tokens**:
GPU का प्रति घंटे का किराया उसके नापे गए throughput (tokens/sec, जिसे tokens/hour में बदला गया हो) से भाग देकर, एक million tokens के हिसाब से। यह उसी नापे गए throughput से निकलता है जो पाठ 6 का batch-size trade-off देता है, किसी vendor के विज्ञापित per-token दाम से नहीं जो किसी दूसरे workload के batch size पर नापा गया था।
_बचें_: vendor का बताया तय per-token दाम (throughput, और इसलिए प्रति token लागत, उस batch size और workload पर निर्भर करती है जिसमें उसे नापा गया, और एक configuration से दूसरे में लागू नहीं होती)

**Draft model**:
एक छोटा, सस्ता model (या model के बिना कोई तरीक़ा जैसे n-gram matching, या target model पर ही लगे अतिरिक्त heads) जो कई संभावित अगले tokens सुझाता है, जिन्हें target model एक ही parallel pass में verify करता है, बजाय इसके कि वह उन्हें एक-एक करके खुद generate करे।
_बचें_: target model का छोटा, कम गुणवत्ता वाला विकल्प (draft model का output कभी सीधे इस्तेमाल नहीं होता; target model उसे हमेशा सिर्फ़ verify करता है, और ज़रूरत हो तो सुधारता है)

**Error budget**:
1 घटा SLO (service level objective): उस लक्ष्य के विरुद्ध कितनी चूकें मान्य हैं, इसके बाद service को उसके अनुपालन से बाहर माना जाता है। एक अकेली चूकी हुई request अपने आप में समस्या नहीं है; मायने यह रखता है कि चूकों की दर budget को SLO की मापन window की अनुमति से तेज़ी से खा रही है या नहीं।
_बचें_: किसी एक चूकी हुई माप को समस्या मान लेना (budget इसीलिए है कि कुछ दर की चूकें अपेक्षित और सहनीय हैं; सिर्फ़ window के मुक़ाबले खपत की दर मायने रखती है)

**KV cache**:
हर पहले से generate हुए token के लिए, हर layer पर, सहेजे गए key और value vectors, ताकि server को बाद के tokens के लिए उन्हें दोबारा कभी compute न करना पड़े। इसका आकार sequence length के साथ रैखिक रूप से बढ़ता है और serving में अक्सर model के अपने weights की जगह यही memory की अड़चन होता है।
_बचें_: attention cache, key-value store

**KV-cache aware routing**:
Fleet-स्तर की request-routing नीति जो नई request को उस server पर भेजती है जिसके पास उसके लिए पहले से सबसे ऊँचा cache-hit rate है, सिर्फ़ load (round-robin, least-connections) के आधार पर routing करने के बजाय। यह prefix caching का प्रति-server फ़ायदा कई servers के fleet तक बढ़ाती है, क्योंकि routing का फ़ैसला खुद जानता है कि मेल खाता cache कहाँ मौजूद है।
_बचें_: आम load balancing (round-robin या least-connections cache की locality को पूरी तरह अनदेखा करते हैं, और cache-अनुकूल request को ऐसे server पर भेज सकते हैं जिसे prefill शुरू से दोबारा करना पड़े)

**Memory-bandwidth-bound**:
ऐसा computation जिसकी मुख्य लागत data (जैसे model के weights) को memory से compute unit तक पहुँचाना है, न कि data पहुँचने के बाद किया गया arithmetic। आम autoregressive decoding memory-bandwidth-bound है, और यही speculative decoding को कई संभावित tokens को एक pass में, लगभग एक token generate करने की लागत पर, verify करने देता है।
_बचें_: compute-bound (उल्टी स्थिति, जहाँ arithmetic हावी होता है; दोनों को मिलाने से यह छूट जाता है कि decoding में ही अतिरिक्त verification का काम लगभग मुफ़्त क्यों है)

**Pipeline bubble**:
Pipeline-parallel setup में devices का वह खाली समय जो वे इंतज़ार में बिताते हैं, किसी batch की processing के शुरू में (जब pipeline भर रही होती है) और अंत में (जब वह ख़ाली हो रही होती है), क्योंकि उन पलों में हर device के पास काम नहीं होता। Batch को ज़्यादा micro-batches में बाँटने से यह खाली हिस्सा घटता है, पर कभी ख़त्म नहीं होता।
_बचें_: यह मानना कि micro-batching bubble को पूरी तरह मिटा देती है (वह कुल काम के मुक़ाबले खाली हिस्से को ही घटाती है; micro-batches की संख्या कुछ भी हो, शुरू और अंत की देरी बनी रहती है)

**Pipeline parallelism**:
Model की layers की श्रृंखला को लगातार समूहों में बाँटकर अलग devices पर रखना, ताकि data devices से उसी क्रम में गुज़रे जिस क्रम में layers एक device पर चलतीं। Communication सिर्फ़ एक device के समूह और अगले के बीच की सीमा पर होता है, इसीलिए यह tensor parallelism से धीमा inter-device link सह सकती है और कई nodes में फैल सकती है।
_बचें_: एक ही layer के भीतर computation बाँटना (वह tensor parallelism है; pipeline parallelism एक layer के भीतर का काम कभी नहीं बाँटती, सिर्फ़ यह तय करती है कि कौन-सी layers कहाँ जाएँ)

**Prefix caching**:
बाक़ी बेमेल requests के बीच किसी साझा prefix का पहले से compute हुआ KV cache दोबारा इस्तेमाल करना (आम system prompt, बार-बार पूछा जाने वाला document, बातचीत के पिछले turns)। यह वही block-sharing तंत्र है जो PagedAttention एक request के parallel samples के भीतर इस्तेमाल करता है, बस requests के पार बढ़ाया गया। यह सिर्फ़ prefill तेज़ करता है; decode का समय अप्रभावित रहता है।
_बचें_: यह मानना कि यह decode भी तेज़ करता है (यह सिर्फ़ मेल खाते prefix के लिए फ़ालतू prefill computation छोड़ता है; उसके बाद नए tokens generate करने की लागत दोनों हालत में बिल्कुल बराबर है)

**RoPE scaling**:
Rotary position embeddings के tokens के बीच की दूरी encode करने का तरीक़ा दोबारा scale करके model को उसकी trained length से ज़्यादा लंबा context सँभालने लायक़ बनाना (YaRN का तरीक़: high-frequency आयामों को कम और low-frequency आयामों को ज़्यादा scale करना), शुरू से retrain किए बिना। कितने tokens की keys और values cache होती हैं, इसमें कुछ नहीं बदलता; इस तरह सँभाला गया लंबा context भी KV cache की आम रैखिक बढ़त की पूरी क़ीमत लेता है।
_बचें_: यह मानना कि यह KV cache memory घटाती या सीमित करती है (वह सिर्फ़ इस्तेमाल-योग्य अधिकतम context length बढ़ाती है; उस लंबे context का cache ठीक वैसे ही बढ़ता है जैसे बिना किसी scaling के बढ़ता)

**SLI (service level indicator)**:
किसी raw exported metric में से चुना गया मात्रात्मक, user से जुड़ा अनुपात, जैसे उन requests का अंश जिनका TTFT बताई गई सीमा से कम है, जो server की अंदरूनी स्थिति के बजाय user के अनुभव से तय किया गया हो।
_बचें_: raw metric histogram खुद (histogram नापा हुआ data है; SLI वह ख़ास user-संबंधित अनुपात है जिसे उसमें से चुनकर उस पर लक्ष्य रखा जाता है)

**Sliding-window attention**:
हर token को अब तक के पूरे sequence के बजाय अपने से पहले के अधिकतम एक निश्चित संख्या, `W`, tokens पर attend करने तक सीमित करना, साथ में एक rolling buffer cache जो हमेशा सिर्फ़ `W` tokens के keys और values रखता है। यह sequence के KV cache को एक स्थिर आकार पर थाम देती है चाहे sequence कितना भी लंबा हो जाए, जबकि RoPE scaling में रैखिक बढ़त जस की तस रहती है।
_बचें_: यह मानना कि यह RoPE scaling की तरह model की उपयोगी दृष्टि दूर तक बढ़ाती है (वह cache को सीमित करती है और सीधा attention आख़िरी `W` tokens तक बाँध देती है; उसके पार की चीज़ सिर्फ़ परोक्ष रूप से, stacked layers के ज़रिए पहुँचती है, और attention sinks के बिना अपने आप में गुणवत्ता का ढहना झेलती है)

**SLO (service level objective)**:
किसी SLI के लिए तय लक्ष्य, जैसे "पिछले 28 दिनों में 99% requests का TTFT 300ms से कम।" जो बचता है, यानी 1 घटा SLO, वही error budget है।
_बचें_: एक बार का benchmark नतीजा (पाठ 16 का अकेला नापा हुआ p99 एक snapshot है; SLO लगातार export होते metrics पर टिका स्थायी लक्ष्य है)

**Speculative decoding**:
कई संभावित अगले tokens सस्ते में draft करना, फिर target model के एक parallel forward pass में सबको verify करना, सही अनुमान स्वीकार करना और ग़लत अनुमान दोबारा sample करना, ताकि अंतिम output distribution ठीक वही रहे जो अकेले target model चलाने पर होता। यह सिर्फ़ latency का उपाय है, गुणवत्ता का कोई trade-off नहीं।
_बचें_: कोई सन्निकटन तकनीक (वह सिर्फ़ यह बदलती है कि generation में कितने महँगे forward passes लगते हैं, यह कभी नहीं कि क्या generate होता है)

**Tensor parallelism**:
किसी एक layer के भीतर के बड़े matrix multiplications (transformer के attention और MLP blocks) को columns या rows के हिसाब से devices में बाँटना, जहाँ हर device अपना हिस्सा parallel में compute करता है और हर layer के भीतर ख़ास जगहों पर एक communication step असली नतीजा जोड़ देता है। इसे तेज़ interconnect (जैसे NVLink) चाहिए, क्योंकि यह जोड़ना critical path पर, हर layer में, हर forward pass में होता है।
_बचें_: पूरी layers को devices में बाँटना (वह pipeline parallelism है; tensor parallelism एक layer के भीतर का computation बाँटती है, पूरी layers अलग devices को कभी नहीं सौंपती)
