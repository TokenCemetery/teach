---
title: शब्दावली
description: "RAG के मानक शब्द"
type: glossary
---

# RAG शब्दावली

Retrieval pipeline के मानक शब्द: वह documents को किन टुकड़ों में बाँटती है, और generation चरण को क्या सौंपना है यह कैसे तय करती है।

## शब्द

**Agentic retrieval**:
ऐसा system जो हर query और हर चरण पर तय करता है कि retrieval की ज़रूरत है भी या नहीं, जो लौटा वह काफ़ी है या नहीं, और अभी-अभी निकाली गई किसी बात के आधार पर दोबारा retrieve करना है या नहीं, बजाय इसके कि वह retrieve-फिर-generate का एक तय पास चलाए।
_बचें_: multi-hop retrieval (संबंधित पर ज़्यादा संकरा मामला: multi-hop ख़ास तौर पर तब है जब query का बाद वाला उप-सवाल पहले वाले के उत्तर पर निर्भर हो, जबकि agentic retrieval में यह भी शामिल है कि retrieve करना है या नहीं)

**Chunk**:
Document का एक टुकड़ा, जो embedding और indexing से पहले उसे बाँटकर बनता है, और जिसका आकार इतना रखा जाता है कि उसकी embedding कई विषयों का औसत बनने के बजाय एक विषय पर केंद्रित रहे।
_बचें_: segment, passage (सिर्फ़ तब जब किसी ऐसे स्रोत को उद्धृत कर रहे हों जो यह शब्द इस्तेमाल करता है)

**Chunking**:
Document को chunks में बाँटने की प्रक्रिया: तय आकार से, document की अपनी संरचना से, या यह पहचानकर कि विषय कहाँ बदलता है।
_बचें_: splitting (बहुत सामान्य; इसे सिर्फ़ यांत्रिक क्रिया का वर्णन करते गद्य में इस्तेमाल करें, प्रक्रिया के नाम के रूप में नहीं)

**Context window utilization**:
Generate किए गए उत्तर में असल में cite किए गए chunks और retrieve करके prompt में रखे गए chunks का अनुपात। कम utilization का मतलब है कि tokens ऐसे context पर ख़र्च हुए जिसे model ने कभी इस्तेमाल नहीं किया; लगातार ऊँचा utilization इसके उलट चेतावनी भी हो सकता है कि ज़रूरी सामग्री cite होने से पहले ही context window से कटकर बाहर हो रही है।
_बचें_: यह मान लेना कि ऊँचा utilization हमेशा बेहतर है; ऊँचे सिरे पर यह truncation की चेतावनी का संकेत है, सिर्फ़ दक्षता की जीत नहीं

**Error cascading**:
Ingestion के किसी शुरुआती चरण की ग़लती (heading को ग़लत पहचानना, columns को ग़लत क्रम में मिला देना) का उन सभी बाद के चरणों में फैल जाना जो उसे मिली पहले से बिगड़ी हुई संरचना पर काम करते हैं। इससे एक पूरे section के बराबर के अंतिम chunks बिगड़ जाते हैं, बजाय इसके कि ग़लती उसी एक element तक सीमित रहे जिसे उसने सीधे छुआ।
_बचें_: an isolated parsing error (असर को कम आँकता है; इसे cascading नाम देने की बात ही यही है कि एक शुरुआती ग़लती स्थानीय रहने के बजाय बढ़ती जाती है)

**HyDE (Hypothetical Document Embeddings)**:
Query की जगह उसके लिए language model से generate कराए गए काल्पनिक उत्तर को embed करना, फिर उस embedding से समानता के आधार पर corpus में खोजना। यह काल्पनिक document के तथ्यात्मक रूप से ग़लत ब्योरों को सह लेता है, क्योंकि encoder की embedding का चरण उन्हें छान देता है और असली विषय-संबंधी समानता को बचाए रखता है।
_बचें_: query rewriting (query-पक्ष का एक अलग उपाय: rewriting query को ही दोबारा गढ़ता है, HyDE query की जगह generate किया हुआ उत्तर embed करता है)

**Incremental indexing**:
पहले से बने index में उसे शुरू से दोबारा बनाए बिना नए vectors जोड़ना। HNSW में यह अच्छी तरह चलता है, क्योंकि उसमें training चरण नहीं है; IVFFlat में कमज़ोर है, क्योंकि उसके cluster centroids build के समय तय हो जाते हैं और दोबारा कभी नहीं निकाले जाते, इसलिए मूल training data से अलग जोड़ा गया नया content ठीक से cluster नहीं हो पाता।
_बचें_: reindexing (शुरू से पूरा rebuild, जो ख़ास तौर पर तब ज़रूरी होता है जब embedding model बदले; यह अपरिवर्तित index में नए vectors जोड़ने जैसा ऑपरेशन नहीं है)

**Ingestion**:
कच्चे source document (PDF, HTML page या office file) को उस साफ़, संरचित text में बदलना जिस पर chunking असल में काम करती है। यह chunking से ऊपर की धारा का असली pipeline चरण है, जिसकी अपनी विफलताएँ हैं, ऐसा preprocessing ब्योरा नहीं जो pipeline की नज़र से नीचे रह जाए।
_बचें_: chunking को pipeline का पहला चरण मानना (chunking मानकर चलती है कि ingestion साफ़ text बना चुका है; वही उसे असल में बनाता है)

**Metadata filtering**:
Retrieval को nearest-neighbor similarity के साथ-साथ संरचित attributes (document का प्रकार, तारीख़, मालिक, permission tag) पर किसी predicate से मेल खाने वाले chunks तक सीमित करना, बजाय सिर्फ़ similarity से पूरे corpus में खोजने के।
_बचें_: permission filtering (metadata filtering का एक ख़ास, ऊँचे दाँव वाला मामला, जहाँ चूक गुणवत्ता की गिरावट नहीं बल्कि security incident है, और जिसमें ख़ास तौर पर pre-filtering चाहिए)

**Multi-hop retrieval**:
ऐसे loop में retrieve करना जहाँ बाद की query किसी पिछले retrieval से निकले तथ्य पर निर्भर करती है, बजाय पहले से तय उप-सवालों के निश्चित सेट के। यह तब चाहिए जब कोई उप-सवाल तब तक पूछा ही नहीं जा सकता जब तक पिछले उप-सवाल का उत्तर पता न हो, जिसे अकेला query decomposition नहीं संभाल सकता।
_बचें_: query decomposition (उन उप-सवालों को बाँटता है जो मूल सवाल के text में पहले से दिखते हैं; multi-hop retrieval उन उप-सवालों को संभालता है जो तब तक मौजूद ही नहीं होते जब तक पिछले hop का उत्तर उन्हें पैदा न करे)

**Post-filtering**:
पहले ANN search चलाना, फिर बाद में उन नतीजों को हटाना जो predicate में फ़ेल हों। तेज़ है, पर कोई selective predicate उस सबको हटा सकता है जो approximate index के सीमित candidate scan को मिला था, जिससे recall ढह जाता है; ख़ास तौर पर permission filter के लिए इसका यह भी मतलब है कि अनधिकृत content हटाए जाने से पहले थोड़ी देर pipeline में मौजूद रहा।
_बचें_: pre-filtering (ANN search चलने से पहले candidate सेट को सीमित करता है, filter किए गए सेट के विरुद्ध recall बचाता है और अस्वीकृत content को pipeline में घुसने ही नहीं देता)

**Pre-filtering**:
ANN search चलने से पहले candidate सेट को सिर्फ़ उन chunks तक सीमित करना जो predicate पर खरे उतरते हैं, जिससे predicate कितना भी selective हो, उस filter किए गए सेट के विरुद्ध recall बना रहता है। ख़ास तौर पर access control के लिए ज़रूरी है, क्योंकि अनधिकृत content कभी pipeline में आता ही नहीं।
_बचें_: post-filtering (पहले पूरे index में खोजता है और बाद में हटाता है; recall और, permission filters के लिए, सुरक्षा की गारंटी ख़ुद, दोनों को चोट पहुँच सकती है)

**Query decomposition**:
मिले-जुले सवाल को उसके अलग-अलग उप-सवालों में बाँटना और हर एक के लिए स्वतंत्र रूप से retrieve करना, बजाय पूरे मिले-जुले सवाल को एक vector के रूप में embed करने के, जो उन passages में से किसी के भी पास नहीं बैठता जो उसके किसी एक हिस्से का अच्छा उत्तर देते।
_बचें_: multi-query expansion (एक अलग technique: expansion एक सवाल के कई पूरे पुनर्कथन बनाता है, decomposition एक सवाल को अलग, ज़्यादा संकरे उप-सवालों में बाँटता है)

**Reference-free scoring**:
हर retrieve किए गए chunk के लिए LLM से कराया गया relevance score, जिसे सही उत्तर पहले से जाने बिना निकाला जाता है, और जिसे किसी समय-खिड़की में hit rate या औसत relevance के रूप में जोड़ा जाता है। Production monitoring recall@k या MRR की जगह यही इस्तेमाल करती है, क्योंकि उन दोनों को labeled या synthetic query सेट चाहिए जो ज़्यादातर live traffic के पास नहीं होता।
_बचें_: recall@k, MRR (offline metrics जिन्हें ज्ञात-सही नतीजे चाहिए; reference-free scoring ख़ास तौर पर तब का production विकल्प है जब ऐसे labels न हों)

**Reindexing**:
Vector index को शुरू से दोबारा बनाना, जो तब ज़रूरी है जब embedding model ख़ुद बदले, क्योंकि हर मौजूदा vector पुराने model की अपनी vector space में बना था और नए model की embeddings के साथ उसकी दूरियाँ तुलनीय नहीं रहतीं। यह incremental indexing से अलग ऑपरेशन है, और उस नियमित रखरखाव से भी जो deletes और updates माँगते हैं।
_बचें_: incremental indexing (अपरिवर्तित index में नए vectors जोड़ना; reindexing का मतलब ख़ास तौर पर सब कुछ दोबारा बनाना है क्योंकि vectors बनाने वाला model बदल गया)
