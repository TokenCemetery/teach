---
title: "20. Retrieval Pipeline की समीक्षा"
description: "किसी और के retrieval pipeline डिज़ाइन की समीक्षा करें और ship होने से पहले ठीक-ठीक बताएँ कि वह क्या ग़लत करेगा, और यह भी बताएँ कि कब बताई गई समस्या का उत्तर RAG ख़ुद (pipeline का कोई चरण नहीं) ही नहीं है"
type: lesson
---

# पाठ 20. Retrieval Pipeline की समीक्षा

**मिशन से संबंध:** वरिष्ठ स्तर की एक skill है किसी और के काम की समीक्षा करना, यह कहने के बजाय कि कोई चुनाव "ठीक नहीं लगता", यह बताना कि उसकी क़ीमत क्या है, और यह जानना कि पूरा तरीक़ा ही कब समस्या के लिए ग़लत है (सिर्फ़ यह नहीं कि कौन-सा चरण टूटा है)।
**मुख्य स्रोत:** [पेपर: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
**पूर्व-आवश्यकताएँ:** [पाठ 1](0001-chunking.md), [पाठ 2](0002-embedding-models-and-similarity.md), [पाठ 4](0004-ann-indexes.md), [पाठ 6](0006-bm25-and-lexical-search.md), [पाठ 9](0009-when-reranking-earns-its-cost.md), [पाठ 11](0011-diagnosing-the-pipeline.md), [पाठ 15](0015-metadata-filtering-and-access-control.md), [पाठ 17](0017-freshness.md)

## वार्म-अप

1. ▢ Retrieval metric क्या मापती है, और hybrid weights व reranking को उसकी ज़रूरत क्यों है?

<details markdown="1"><summary>जाँचें</summary>

Recall@k या MRR जैसी retrieval metric मापती है कि सही चीज़ retrieve हुई या नहीं, generation चरण शुरू होने से पहले ही। Hybrid weights और reranking की tuning दोनों इस जानकारी पर निर्भर हैं कि कोई बदलाव असल में जो retrieve हुआ उसे बेहतर करता है या नहीं, इसलिए उन्हें अंदाज़े से नहीं बल्कि किसी माप के सामने तय करना पड़ता है।

</details>

2. ▢ Post-filtering ख़ास तौर पर access control के लिए क्यों विफल होता है, उस तरह जैसे दूसरे metadata filters के लिए नहीं?

<details markdown="1"><summary>जाँचें</summary>

Post-filtering पहले पूरे index पर ANN search चलाता है, फिर बाद में नतीजे हटाता है। साधारण metadata filters के लिए यह सिर्फ़ recall की गिरावट है: filter कुछ नतीजे गिरा देता है। Access control के लिए, अनधिकृत सामग्री हटाए जाने से पहले थोड़ी देर pipeline में मौजूद रहती है, जो security की विफलता है, सिर्फ़ गुणवत्ता की नहीं। Pre-filtering search चलने से पहले candidate सेट को सीमित करता है, इसलिए अस्वीकृत सामग्री pipeline में कभी आती ही नहीं।

</details>

3. ▢ Corpus के पुराने पड़ने का एक तरीक़ा बताएँ, और यह कि उस मामले में freshness को दूसरे मामले से अलग ढंग से कैसे संभाला जाता है।

<details markdown="1"><summary>जाँचें</summary>

Corpus documents जोड़ने, हटाने, या embedding model बदलने से पुराना पड़ता है। जोड़ने और हटाने में incremental indexing इस्तेमाल हो सकती है, HNSW दोनों को अपेक्षाकृत अच्छी तरह संभालता है। Model बदलने के लिए शुरू से पूरा reindex चाहिए: पुराने vectors की नए vectors के साथ कोई तुलनीय दूरियाँ नहीं होतीं, इसलिए उन्हें पूरी तरह दोबारा बनाना पड़ता है।

</details>

## यह जानें

### समीक्षा की checklist: डिज़ाइन में असल में क्या देखना है

जब कोई retrieval pipeline प्रस्तावित करे या पहले से बना हुआ दिखाए, तो इन सवालों से क्रम में गुज़रें। हर एक इस पूरी रूपरेखा के एक चरण से मेल खाता है। हर एक के लिए देखें: (1) क्या चुनाव इस corpus और use case के लिए सोच-समझकर किया गया था, (2) क्या उसे retrieval metric के सामने मापा गया, या वह default से या अंदाज़े से चुना गया?

**चरण 1: Chunking रणनीति।** क्या डिज़ाइन ने chunking रणनीति इसलिए चुनी कि वह corpus की असली संरचना से मेल खाती है (गद्य के लिए fixed-size, nested markdown के लिए recursive, विषय बदलने वाले पेपरों के लिए semantic, या ऐसे PDFs के लिए document-structure-aware जिनकी layout मायने रखती है)? या कोई default chunk आकार (512, 1024 tokens) बस नक़ल कर दिया गया? Medical PDFs के corpus को API दस्तावेज़ों से भरे repo से अलग chunking चाहिए।

**चरण 2 और 3: Embedding model और similarity metric।** क्या embedding model और metric (cosine, L2, dot product) इस corpus के लिए चुने गए, मिलते-जुलते corpora पर या कम से कम इसी corpus के उदाहरणों पर परखे गए? या वे उसी से default में उठा लिए गए जो vector database के दस्तावेज़ ने सुझाया? समाचारों पर train हुई embedding वित्त के पेपरों को ख़राब rank कर सकती है।

**चरण 4, 5, 6: Hybrid search, reranking और retrieval का मूल्यांकन।** क्या डिज़ाइन के पास कोई असली retrieval metric है जिसके सामने उसे tune किया गया (Recall@k, MRR, nDCG)? या hybrid weights और reranking अंदाज़े से जोड़े गए, बिना यह मापे कि उन्होंने retrieve होने वाली सही चीज़ को असल में बेहतर किया या नहीं? जो reranking चरण latency लेता है उसे असली use case पर यह सबूत चाहिए कि उसने वह लागत कमाई।

**चरण 9: Permission-aware filtering।** अगर corpus में access control है, तो क्या डिज़ाइन ANN search से पहले candidate सेट को सीमित करने के लिए pre-filtering इस्तेमाल करता है, अनधिकृत सामग्री को pipeline से पूरी तरह बाहर रखते हुए? या वह पूरे index से retrieve करके बाद में filter करता है, recall की गिरावट और उस क्षण का जोखिम लेते हुए जब अनधिकृत सामग्री pipeline में मौजूद होती है?

**चरण 10 और 11: Ingestion और freshness।** क्या डिज़ाइन ने इसका हिसाब रखा कि source documents chunking से ऊपर की धारा में असल में कैसे extract और parse होते हैं? क्या documents जुड़ने, हटने या बदलने पर index को ताज़ा रखने की उसके पास योजना है, या वह मानकर चल रहा है कि data स्थिर है? Incremental updates HNSW के लिए अच्छे बैठते हैं, पर embedding model बदलने के लिए हमेशा पूरा reindex चाहिए।

**फिर चरण 6: Retrieval की विफलता को generation की विफलता से अलग करना।** जब कुछ ग़लत हो, तो क्या डिज़ाइन के पास यह बताने का तरीक़ा है कि model को ख़राब context मिला या उसने अच्छे context को बुरी तरह इस्तेमाल किया? जो डिज़ाइन हर ग़लत उत्तर पर retrieval चरण को दोष देने पर टिका रहता है उसमें एक अहम diagnostic की कमी है।

### विवादित सवाल: क्या long-context retrieval को अप्रचलित कर देता है?

यह जीवित असहमति है। एक पक्ष कहता है कि long-context models ने अब retrieval की ज़रूरत ख़त्म कर दी है: retrieval pipeline क्यों बनाएँ जब models अब पूरा corpus prompt में रख सकते हैं? हर request पर 100K tokens भेज सकते हों तो retrieval infrastructure पर पैसा क्यों ख़र्च करें?

दूसरा पक्ष कहता है कि long-context की प्रगति के बावजूद ज़्यादातर असली corpora और use cases के लिए retrieval अब भी जीतता है। शोध पेपर "Lost in the Middle" दिखाता है कि models लंबे context के बीच में रखी जानकारी को शुरुआत या अंत की जानकारी से कहीं बदतर इस्तेमाल करते हैं, context window के भीतर भी। हर request पर पूरा corpus दोबारा भेजना वे सारे tokens जो इस्तेमाल नहीं होते उन्हें attention के बीच में केंद्रित कर देता है, ठीक वहाँ जहाँ models जानकारी को ख़राब इस्तेमाल करते हैं। Retrieval इसकी जगह सिर्फ़ प्रासंगिक हिस्से भेजता है, उन्हें context window के ऊपर के पास रखते हुए जहाँ models उन पर अच्छी तरह ध्यान देते हैं।

पर यह निर्णय का ढाँचा है, निर्णय ख़ुद नहीं। किसी ख़ास समस्या के लिए retrieval सही उत्तर है या नहीं, यह तय करने के लिए तीन सवाल पूछें:

**1. Corpus का आकार और update की आवृत्ति क्या है?**

जो corpus छोटा, स्थिर है और एक prompt में समा जाता है, वह पूरा भेजने पर सचमुच बेहतर चल सकता है: कंपनी की पूरी handbook (50K tokens, तिमाही बदलती है) retrieval index सँभालने से सस्ती और सरल हो सकती है कि उसे हर request पर शामिल कर दिया जाए। जो corpus बड़ा है (लाखों documents), लगातार बदलता है (रोज़ ingestion), या access-controlled है (अलग उपयोगकर्ता अलग उपसमूह देखते हैं), वह उलटी तरह काम करता है: उसे हर request पर दोबारा भेजने की लागत निषेधात्मक है, या retrieval के बाद access control लागू करना असंभव है (चरण 9 का पाठ)।

**2. Query पैटर्न को असल में क्या चाहिए?**

जिस query को पूरे corpus पर संश्लेषण चाहिए (हमारे सभी पेपरों में X पर आम सहमति क्या है) उसे ज़्यादा context देखने से फ़ायदा हो सकता है। जिस query को सटीक तथ्य चाहिए (annual subscriptions के लिए हमारी refund policy क्या है) वह उस retrieval के साथ बेहतर चलती है जो ठीक वही policy document ढूँढे और उसे ऊपर रखे जहाँ model उस पर अच्छी तरह ध्यान देता है। Retrieval आपको कम context ऊँची सटीकता से भेजने देता है।

**3. लागत की गणना असल में क्या बनती है?**

"Lost in the Middle" पेपर trade-off दिखाता है: जब जानकारी 100K-token prompt के बीच में बैठी हो, तो models उसे खो देते हैं। इसका उपाय यह है कि या तो context को सावधानी से क्रम दें (जो retrieval सबसे प्रासंगिक chunks को ऊपर के पास रखकर करता है) या उसे कम भेजें। जो retrieval सबसे प्रासंगिक chunks के 2K tokens भेजता है वह उन 100K tokens से सस्ता और बेहतर है जिनमें आधा "मृत क्षेत्र" में है। यह मानता है कि आपका retrieval असल में प्रासंगिक chunks ढूँढता है; अगर retrieval pipeline टूटा है, तो सब कुछ भेजना कम से कम एक विकल्प है। पर जब retrieval काम करता है, तब वह लागत, latency और गुणवत्ता, तीनों में जीतता है।

## अभ्यास

1. ▢ एक टीम ने ऐसा pipeline बनाया जो सभी documents को fixed 1024-token आकार से chunk करता है। आप डिज़ाइन की समीक्षा करते हैं और इस चुनाव का कोई औचित्य नहीं दिखता। यह समझने के लिए कि वह सोच-समझकर किया गया था या default में आया, आपको कौन-सा सवाल पूछना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

Corpus क्या है? क्या ये customer support transcripts हैं, शोध पेपर हैं, product दस्तावेज़ हैं, या कुछ और? 1024-token chunk कुछ document प्रकारों के लिए चलता है और दूसरों पर विफल होता है। अगर उन्होंने यह आकार इसलिए चुना कि लागू करना आसान था या vector database के उदाहरण code ने इसे इस्तेमाल किया, तो यह चेतावनी का संकेत है। अगर उन्होंने असली corpus के नमूनों पर रोक कर रखी गई retrieval metric के सामने अलग chunk आकार परखे और 1024 जीता, तो यह सोच-समझकर किया गया चुनाव है जिसे आप खोज सकते हैं।

</details>

2. ▢ डिज़ाइन असली corpus पर परखे बिना OpenAI का embedding model इस्तेमाल करता है। क्या ग़लत हो सकता है?

<details markdown="1"><summary>जाँचें</summary>

Embedding model internet से text के व्यापक वितरण पर train हुआ था। अगर corpus बहुत विशेष है (कानूनी documents, वित्तीय filings, चिकित्सा साहित्य) या ऐसी भाषा में है जिसका pretraining data कम है, तो model semantic similarity को ख़राब rank कर सकता है। सही परीक्षण: इस corpus के documents का नमूना embed करें, हाथ से पहचानें कि कौन-सी जोड़ियाँ असल में मिलती-जुलती हैं, और जाँचें कि OpenAI की distance ranking उससे सहमत है या नहीं। अगर नहीं, तो domain-विशिष्ट embeddings या मिलती-जुलती सामग्री पर train हुए models पर विचार करें।

</details>

3. ▢ डिज़ाइन hybrid search (BM25 + vector) इस्तेमाल करता है पर टीम को पक्का नहीं कि उन्हें कैसे weight करें। वे पूछते हैं, "क्या हम 50-50 करें, या 70-30 vector?" उनके पास कौन-सी जानकारी नहीं है?

<details markdown="1"><summary>जाँचें</summary>

उनके पास retrieval metric नहीं है। Weights को रोक कर रखे गए query सेट पर असली माप के सामने tune किया जाना चाहिए, यह मापते हुए कि कौन-सा मिश्रण task पर सबसे अच्छा Recall@k या MRR देता है। 50-50 और 70-30 के बीच अंदाज़ा लगाना सिक्का उछालने जैसा है, और ग़लत मिश्रण किसी भी एक तरीक़े से अकेले ज़्यादा नुक़सान कर सकता है। असली सवाल यह है: आपके corpus और queries के लिए कौन-सा मिश्रण असल में सही चीज़ retrieve करता है? उसे मापें।

</details>

4. ▢ Corpus में चिकित्सा शोध पेपर हैं जो लगातार अपडेट होते हैं (रोज़ नए पेपर जुड़ते हैं, पुराने कभी-कभी वापस लिए या सुधारे जाते हैं)। एक प्रस्ताव सुझाता है कि हर request पर सभी documents को long-context model के prompt में रखा जाए। यह काम क्यों नहीं कर सकता, इसके दो कारण बताएँ।

<details markdown="1"><summary>संकेत</summary>

विचार करें कि corpus कैसा है (आकार, बदलाव की दर) और लंबे context के बीच में रखी जानकारी के साथ model क्या करता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

दो कारण: (1) Corpus बड़ा है और लगातार बदलता है, इसलिए हर request पर सभी documents दोबारा भेजना महँगा है, और prompt में कौन-से documents हैं यह अपडेट रखना रखरखाव का बोझ है। Retrieval आपको सिर्फ़ प्रासंगिक चीज़ भेजने देता है और index ताज़ा होने पर अपने-आप अपडेट हो जाता है। (2) Models लंबे context के बीच में रखी जानकारी को ख़राब इस्तेमाल करते हैं ("Lost in the Middle")। 500 पेपर भेजना, जिनमें से query के लिए सिर्फ़ कुछ प्रासंगिक हैं, प्रासंगिक वालों को attention के बीच में दबा देता है, जहाँ models ख़राब ध्यान देते हैं। जो retrieval शीर्ष 5 प्रासंगिक पेपर भेजता है, context के ऊपर प्रासंगिकता से क्रमबद्ध, वह सस्ता भी है और ज़्यादा सटीक भी।

</details>

5. ▢ RAG पर विचार कर रही एक टीम पूछती है: "हमारा corpus 10MB की markdown files है, साल में एक बार अपडेट होता है। इसे पूरा prompt में क्यों न रख दें?" नीचे का कौन-सा दावा इस सवाल को सही ढंग से संबोधित करता है?

    - a) Long-context models ने RAG को पूरी तरह अप्रचलित कर दिया है; इस टीम को किसी भी कारण से कभी retrieval इस्तेमाल नहीं करना चाहिए
    - b) Corpus छोटा, स्थिर है और prompt में समा जाता है; इस ख़ास मामले में सब कुछ शामिल करना असल में ज़्यादा सरल हो सकता है और ठीक चल सकता है
    - c) RAG हमेशा long-context से बेहतर है, corpus का आकार या बदलाव की आवृत्ति चाहे जो हो
    - d) "Lost in the Middle" पेपर साबित करता है कि prompt में कभी कुछ नहीं रखा जाना चाहिए

<details markdown="1"><summary>जाँचें</summary>

**b)** इस सवाल पर यही संतुलित स्थिति है। Corpus का आकार (10MB, संभवतः context window के भीतर), बदलाव की आवृत्ति (सालाना) और access-control की ज़रूरतें (कोई उल्लेख नहीं), सब इसी ओर इशारा करते हैं कि long-context ठीक चलेगा, संभवतः ज़्यादा सरल। RAG की असली infrastructure लागतें हैं। छोटा, स्थिर corpus उन लागतों को सही नहीं ठहराता। (a) ग़लत है: जब corpus छोटा और स्थिर हो तो models को वैध रूप से retrieval के बिना इस्तेमाल किया जा सकता है। (c) ग़लत है: फ़ैसला corpus की विशेषताओं और query पैटर्न पर निर्भर है, किसी पूर्ण नियम पर नहीं। (d) ग़लत है: पेपर दिखाता है कि models बीच के context को ख़राब इस्तेमाल करते हैं, यह नहीं कि prompt में कुछ भी इस्तेमाल के अयोग्य है।

</details>

## असली दुनिया का अभ्यास

- [ ] कोई retrieval pipeline खोजें जो आपने बनाया या जिसकी समीक्षा की। उस पर checklist के छह सवाल चलाएँ। हर चरण के लिए एक वाक्य लिखें: क्या यह चुनाव retrieval metric के सामने मापा गया था, या default से चुना गया था? फिर पूछें: अगर आपको इसे बेहतर करना हो तो आप क्या बदलेंगे?
- [ ] कोई एक corpus चुनें (आपका अपना, कोई सार्वजनिक जिसे आप जानते हों, या कोई synthetic)। तीन-सवाल वाला ढाँचा हल करें: corpus का आकार और update की आवृत्ति, query पैटर्न, उसे पूरा दोबारा भेजने बनाम retrieval की असली लागत। उत्तर लिखें: retrieval बेहतर बैठेगा या long-context, और क्यों?
- [ ] कल: "Lost in the Middle" पेपर का नतीजों वाला खंड पढ़ें और 4K-token context की शुरुआत, बीच और अंत की जानकारी के बीच प्रदर्शन का ख़ास अंतर नोट करें। फिर अनुमान लगाएँ: अगर आपके query पैटर्न को 100 documents पर संश्लेषण चाहिए, तो शुरुआत और अंत के "उच्च-गुणवत्ता" क्षेत्रों में कितने समाएँगे?

## आगे बढ़ने के लिए

- [पेपर: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
- [पाठ 24: Serve Time पर Long Context](../../inference/lessons/0024-long-context-at-serve-time.md): long-context तकनीकें retrieval की लागत की जगह serving की लागत के साथ असल में क्या करती हैं
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
