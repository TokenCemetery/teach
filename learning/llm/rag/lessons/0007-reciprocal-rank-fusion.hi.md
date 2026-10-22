---
title: "7. Reciprocal Rank Fusion"
description: "Lexical ranking और vector ranking को बेमेल scores की तुलना किए बिना कैसे मिलाएँ, और मिश्रण को मापी गई metric के सामने कैसे tune करें"
type: lesson
---

# पाठ 7. Reciprocal Rank Fusion

**मिशन से संबंध:** यह चरण 4 का समापन है: BM25 और vector search (पाठ 4 से 6) हर एक ranking बनाते हैं, और यह पाठ बताता है कि वे दोनों rankings एक hybrid नतीजा कैसे बनती हैं, अंदाज़े से बने मिश्रण से नहीं बल्कि मापी गई संख्या के सामने tune होकर।
**मुख्य स्रोत:** [दस्तावेज़: "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
**पूर्व-आवश्यकताएँ:** [पाठ 6](0006-bm25-and-lexical-search.md), [Chunk](../GLOSSARY.md)

## वार्म-अप

1. ▢ ऐसी query का उदाहरण दें जिस पर BM25 सफल होगा और vector search चूक सकता है, और एक जिस पर उलटा सच हो।

<details markdown="1"><summary>जाँचें</summary>

"error code E502" जैसा exact identifier BM25 के पक्ष में है, क्योंकि vector search का embedding model ख़ास codes को ठीक-ठीक match करने के लिए train नहीं हुआ। बिना साझा शब्दों वाली समानार्थी शब्दावली, जैसे "broken pipe" बनाम "leaking conduit", vector search के पक्ष में है, क्योंकि BM25 उन documents के लिए शून्य score देता है जिनमें query से कोई term साझा नहीं।

</details>

2. ▢ pgvector index के विरुद्ध ग़लत distance operator इस्तेमाल करने से query sequential scan पर क्यों लौट जाती है?

<details markdown="1"><summary>जाँचें</summary>

Index एक ख़ास distance function (एक operator class) के लिए बनता है; अलग operator इस्तेमाल करने वाली query उससे मेल नहीं खाती जिसके लिए index बना था, इसलिए index इस्तेमाल नहीं हो सकता और query सीधे table को स्कैन करती है।

</details>

## यह जानें

### समस्या: बेमेल पैमानों पर दो rankings

BM25 असीमित, corpus पर निर्भर score देता है; cosine similarity -1 और 1 के बीच सीमित score देती है। उन्हें सीधे औसत करना, कुछ normalization के बाद भी, इसका फ़ैसला करना है कि दो बुनियादी रूप से अलग पैमानों को तुलनीय कैसे बनाएँ, और वह फ़ैसला नाज़ुक है: वह corpus, query और चुनी गई normalization योजना पर निर्भर करता है, और यह जानने का कोई सैद्धांतिक तरीक़ा नहीं कि वह निष्पक्ष है।

### RRF: score नहीं, rank की स्थिति इस्तेमाल करें

**Reciprocal rank fusion (RRF)** पैमाने की समस्या को पूरी तरह किनारे कर देता है: वह अंदर के scores को अनदेखा करता है और हर ranking में हर document की सिर्फ़ **rank की स्थिति** इस्तेमाल करता है। Ranking *r* में `rank_r(d)` पर आने वाले document *d* का RRF score हर उस ranking पर reciprocal-rank पद का योग है जिसमें वह दिखता है:

```text
RRF(d) = sum over rankings r of 1 / (k + rank_r(d))
```

`k` एक स्थिरांक है जो सबसे ऊपर की ranks का असर कम करता है; मूल पेपर का एक आम default `k = 60` है। चूँकि सिर्फ़ rank की स्थिति मायने रखती है, score का परिमाण नहीं, इसलिए RRF BM25 ranking और vector-search ranking को बिना किसी को normalize किए मिला देता है: rank की स्थिति पहले से साझा मुद्रा है, जो किसी भी ranking तरीक़े पर अपने-आप normalize हो जाती है।

### एक हल किया हुआ उदाहरण

अंकगणित साफ़ रखने के लिए सरल `k = 1` लेते हुए (production systems आम तौर पर `k = 60` को default रखते हैं, जो शीर्ष ranks के बीच के फ़र्क़ को `k = 1` से ज़्यादा कम करता है): किसी query के लिए BM25 document A को 1st, document B को 4th, document C को 2nd rank देता है; vector search A को 4th, B को 1st, C को 2nd rank देता है।

```text
RRF(A) = 1/(1+1) + 1/(1+4) = 0.500 + 0.200 = 0.700
RRF(B) = 1/(1+4) + 1/(1+1) = 0.200 + 0.500 = 0.700
RRF(C) = 1/(1+2) + 1/(1+2) = 0.333 + 0.333 = 0.667
```

A और B पहले स्थान पर बराबर हैं, हर एक एक तरीक़े में उत्कृष्ट और दूसरे में कमज़ोर; C, जो दोनों में बस औसत है, दोनों से हार जाता है। RRF उस document को इनाम देता है जिस पर कोई भी एक तरीक़ा पूरी मज़बूती से भरोसा करता है, सिर्फ़ उस document को नहीं जिस पर दोनों तरीक़े हल्के से सहमत हों।

![दो क्रमबद्ध सूचियाँ अगल-बगल, BM25 rank और vector-search rank, हर एक में चार स्थान। Document A BM25 में 1st पर है पर vector search में 4th पर; document B BM25 में 4th पर है पर vector search में 1st पर; document C दोनों में 2nd पर है। रेखाएँ हर document को उसकी दो rank स्थितियों से दाईं ओर की fused RRF ranking तक ले जाती हैं, जहाँ A और B पहले स्थान पर बराबर हैं, हर एक एक तरीक़े में उत्कृष्ट रहा, जबकि C, जो हमेशा सिर्फ़ औसत रहा, उनके पीछे आता है, भले ही किसी भी सूची में कभी ख़राब rank पर नहीं था।](images/rrf-worked-example.svg)

### मिश्रण को मापी गई metric के सामने tune करना

RRF को हर ranking के लिए weight के साथ बढ़ाया जा सकता है, `sum of w_r / (k + rank_r(d))`, जिससे vector search अंतिम fusion में BM25 से ज़्यादा या कम गिना जा सके। सही weight, और सही `k`, अंदाज़े से चुनने की चीज़ें नहीं हैं: ये मापने की चीज़ें हैं, उसी तरह जैसे पाठ 3 ने एक को मान लेने के बजाय candidate dimensionalities पर embedding की गुणवत्ता मापी थी। चरण 6 की retrieval metrics (recall@k, MRR) का इस्तेमाल करके, corpus के असली traffic का प्रतिनिधित्व करने वाले labeled या synthetic query सेट के विरुद्ध, अलग-अलग weightings की सीधी तुलना हो सकती है, और जो मिश्रण इस corpus के लिए सही documents को असल में ज़्यादा बार retrieve करता है, default 50/50 बँटवारा नहीं, वही ship करने लायक है।

## अभ्यास

1. ▢ किसी query के लिए BM25 document X को 2nd और document Y को 1st rank देता है; vector search X को 1st और Y को 3rd rank देता है। `k = 1` लेकर हर document का RRF score निकालें और बताएँ कौन ऊपर आता है।

<details markdown="1"><summary>संकेत</summary>

`RRF(d) = 1/(k + rank_in_bm25) + 1/(k + rank_in_vector)`।

</details>

<details markdown="1"><summary>जाँचें</summary>

`RRF(X) = 1/(1+2) + 1/(1+1) = 0.333 + 0.500 = 0.833`। `RRF(Y) = 1/(1+1) + 1/(1+3) = 0.500 + 0.250 = 0.750`। X ऊपर आता है, क्योंकि वह vector search में मज़बूत (1st स्थान) नतीजा है और BM25 में सिर्फ़ हल्का अच्छा, और Y से आगे निकल जाता है, जो BM25 में मज़बूत है पर vector search में कमज़ोर।

</details>

2. ▢ RRF हर document की rank की स्थिति इस्तेमाल करता है, उसका कच्चा BM25 score या cosine similarity score सीधे क्यों नहीं?

<details markdown="1"><summary>जाँचें</summary>

BM25 scores और cosine similarity बेमेल पैमानों पर रहते हैं (एक असीमित और corpus पर निर्भर, दूसरा -1 और 1 के बीच सीमित), और उन्हें एक-दूसरे के विरुद्ध normalize करने का कोई सैद्धांतिक, corpus-स्वतंत्र तरीक़ा नहीं है। Rank की स्थिति पहले से किसी भी ranking तरीक़े पर साझा मुद्रा है, इसलिए उसे इस्तेमाल करना normalization की समस्या को पूरी तरह किनारे कर देता है।

</details>

3. ▢ छोटा `k` (जैसे 1) बनाम बड़ा `k` (जैसे 60), RRF सूत्र पर क्या असर डालता है, इस संदर्भ में कि document की ठीक rank की स्थिति कितनी मायने रखती है?

<details markdown="1"><summary>जाँचें</summary>

छोटा `k` reciprocal-rank पद को सूची के शीर्ष के पास rank के छोटे फ़र्क़ों के प्रति कहीं ज़्यादा संवेदनशील बनाता है (rank 1 और rank 2 के बीच का अंतर अनुपात में बड़ा होता है), जबकि बड़ा `k` उस संवेदनशीलता को कम करता है, जिससे, मान लें, rank 1 और rank 5 का फ़र्क़ तुलनात्मक रूप से छोटा हो जाता है। बड़े `k` मान ज़्यादा नरम, कम rank-स्थिति-संवेदनशील fusion देते हैं।

</details>

4. ▢ टीम को यह कैसे तय करना चाहिए कि अपने hybrid मिश्रण में vector search को BM25 से ज़्यादा weight दे, बजाय बराबर बँटवारे को default रखने के?

<details markdown="1"><summary>जाँचें</summary>

Corpus के असली query पैटर्न का प्रतिनिधित्व करने वाले labeled या synthetic query सेट के विरुद्ध कई candidate weightings पर retrieval की गुणवत्ता (recall@k या MRR, चरण 6 की metrics) मापें, और वह चुनें जो इस corpus के लिए सही documents को असल में सबसे ज़्यादा बार retrieve करे, बजाय यह मान लेने के कि बराबर बँटवारा या कोई और default बिना जाँचे सही है।

</details>

5. ▢ Reciprocal rank fusion के बारे में कौन-सा दावा सही है?

    - a) उसे BM25 और cosine similarity scores को मिलाने से पहले एक ही पैमाने पर normalize करना पड़ता है
    - b) वह rankings को सिर्फ़ rank की स्थिति से मिलाता है, जो बेमेल score पैमानों की तुलना करने की ज़रूरत को किनारे कर देता है
    - c) जो document एक ranking में 1st और दूसरी में आख़िरी आता है वह उस document से हमेशा आगे रहेगा जो दोनों में औसत आता है
    - d) स्थिरांक `k` का fused ranking पर कोई असर नहीं, सिर्फ़ संख्यात्मक score के परिमाण पर है

<details markdown="1"><summary>जाँचें</summary>

**b)** कच्चे scores की जगह rank की स्थिति इस्तेमाल करना ठीक वही है जो normalization की समस्या से बचाता है। (a) ग़लत है: यह कच्चे-score-fusion का वह तरीक़ा है जिससे RRF ख़ास तौर पर बचता है। (c) ग़लत है: हल किए उदाहरण में दिखा कि लगातार औसत document भी दो documents से हार सकता है जो हर एक एक तरीक़े में उत्कृष्ट हों, पर नतीजा असली rank मानों पर निर्भर है, इस किसी सार्वभौमिक नियम पर नहीं कि चरम मध्यम को हराता है। (d) ग़लत है: `k` बदलता है कि rank की स्थिति के फ़र्क़ कितने मायने रखते हैं, जो fused ranking का क्रम बदल सकता है, सिर्फ़ उसका पैमाना नहीं।

</details>

## असली दुनिया का अभ्यास

- [ ] अपने corpus की किसी query के लिए, मुट्ठी भर candidate documents की BM25 rank और vector-search rank निकालें, और `k = 60` लेकर हाथ से उनके RRF scores निकालें।
- [ ] अगर आपके पास labeled या synthetic query सेट है, तो उन्हीं queries पर सिर्फ़-BM25 ranking, सिर्फ़-vector ranking और RRF से fused ranking के लिए recall@k की तुलना करें।
- [ ] कल: weighted RRF सूत्र में vector search के weight के दो अलग मान आज़माएँ, और देखें कि बराबर बँटवारे की तुलना में किसी से recall@k में मापने योग्य सुधार होता है या नहीं।

## आगे बढ़ने के लिए

- [दस्तावेज़: "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
- [पेपर: "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson and Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
