---
title: "Hybrid Search"
description: "BM25 की term-statistics scoring, vector search के बग़ल में वह अब भी मायने क्यों रखती है, और reciprocal rank fusion दोनों को मिलाने का पैमाने-से-मुक्त तरीक़ा"
type: reference
---

# Hybrid Search

Lexical और vector rankings को मिलाना। Hybrid मिश्रण खड़ा या tune करते समय खोजने के लिए बनाया गया।

## BM25 term के overlap को score करता है, अर्थ को नहीं

शुद्ध रूप से lexical ranking function, कोई embedding नहीं, अर्थ की कोई धारणा नहीं। तीन सामग्रियाँ:

| सामग्री | क्या करती है |
|---|---|
| Inverse document frequency (IDF) | Query term को corpus में उसकी दुर्लभता के आधार पर वज़न देती है; "the" जैसा आम शब्द लगभग कुछ नहीं जोड़ता |
| Term frequency, saturating | Term के ज़्यादा बार आने से score बढ़ता है, पर घटते लाभ के साथ, इसलिए अकेली पुनरावृत्ति (keyword stuffing) हावी नहीं हो सकती |
| Length normalization | Document को सिर्फ़ लंबा होने से मिलने वाले कच्चे term-frequency लाभ में कटौती करती है |

## BM25 और vector search के अंधे बिंदु उलटे हैं

| Query का रूप | BM25 | Vector search |
|---|---|---|
| Exact identifier ("error code E502") | Match करता है: शब्दशः string मौजूद है | चूक सकता है: embedding model semantic similarity के लिए train हुआ था, exact-identifier matching के लिए नहीं |
| बिना साझा शब्दों वाली समानार्थी शब्दावली ("broken pipe" / "leaking conduit") | शून्य के क़रीब score: term का कोई overlap नहीं | Match करता है: दोनों वाक्यांशों का अर्थ एक है |

हर तरीक़ा वह पकड़ता है जो दूसरा चूकता है, और यही दोनों को मिलाने का पूरा आधार है।

## Reciprocal rank fusion (RRF): rank इस्तेमाल करें, score नहीं

BM25 का score असीमित और corpus पर निर्भर है; cosine similarity [-1, 1] तक सीमित है। दोनों को सीधे औसत करने का मतलब है नाज़ुक, corpus-विशिष्ट normalization गढ़ना। **RRF** पैमाने की समस्या को किनारे कर देता है, हर ranking में हर document की सिर्फ़ rank स्थिति इस्तेमाल करके:

```text
RRF(d) = sum over rankings r of 1 / (k + rank_r(d))
```

`k` सबसे ऊपर की ranks का असर कम करता है (आम default `k = 60` है; छोटा `k` शीर्ष के पास rank के फ़र्क़ को ज़्यादा मायने देता है, बड़ा `k` उन्हें कम करता है)। Rank स्थिति किसी भी ranking तरीक़े पर साझा मुद्रा है, इसलिए BM25 और vector search के बीच किसी normalization की ज़रूरत नहीं।

**हल किया हुआ उदाहरण**, `k = 1`, BM25 A को 1st / B को 4th / C को 2nd rank देता है, vector search A को 4th / B को 1st / C को 2nd rank देता है:

```text
RRF(A) = 1/(1+1) + 1/(1+4) = 0.500 + 0.200 = 0.700
RRF(B) = 1/(1+4) + 1/(1+1) = 0.200 + 0.500 = 0.700
RRF(C) = 1/(1+2) + 1/(1+2) = 0.333 + 0.333 = 0.667
```

A और B पहले स्थान पर बराबर हैं, हर एक एक तरीक़े में उत्कृष्ट और दूसरे में कमज़ोर; C, जो दोनों में बस औसत है, दोनों से हार जाता है। RRF उस document को इनाम देता है जिस पर कोई भी एक तरीक़ा पूरी मज़बूती से भरोसा करता है, सिर्फ़ उसे नहीं जिस पर दोनों तरीक़े हल्के से सहमत हों।

## मिश्रण को tune करना

RRF को हर ranking के लिए weight के साथ बढ़ाया जा सकता है, `sum of w_r / (k + rank_r(d))`, जिससे vector search BM25 से ज़्यादा या कम गिना जा सके। सही weight और `k` अंदाज़े से नहीं चुने जाते: corpus के असली traffic का प्रतिनिधित्व करने वाले labeled या synthetic query सेट के विरुद्ध कई candidate weightings पर retrieval की गुणवत्ता (recall@k, MRR) मापें, और वही मिश्रण ship करें जो इस corpus के लिए सही documents को असल में ज़्यादा बार retrieve करे, default 50/50 बँटवारा नहीं।

## संबंधित

- [पाठ 6](../lessons/0006-bm25-and-lexical-search.md), [पाठ 7](../lessons/0007-reciprocal-rank-fusion.md)
- [Vector Search और Indexing](vector-search-and-indexing.md): fusion का vector ranking वाला आधा हिस्सा
