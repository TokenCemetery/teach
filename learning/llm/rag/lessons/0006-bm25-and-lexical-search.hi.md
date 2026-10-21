---
title: "6. BM25 और Lexical Search"
description: "BM25 असल में क्या score करता है, और exact-term matching अब भी वह क्यों पकड़ लेती है जो semantic embeddings चूक जाती हैं"
type: lesson
---

# पाठ 6. BM25 और Lexical Search

**मिशन से संबंध:** चरण 4 hybrid search खोलता है: lexical ranking को vector search के साथ मिलाने से पहले, यह पाठ तय करता है कि lexical search असल में किस चीज़ में अच्छा है, और मज़बूत embedding model उसे अप्रचलित क्यों नहीं बना देता।
**मुख्य स्रोत:** [पेपर: "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson and Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
**पूर्व-आवश्यकताएँ:** [पाठ 5](0005-pgvector-specifics.md), [Chunk](../GLOSSARY.md)

## वार्म-अप

1. ▢ Bi-encoder query और passage को साथ मिलाकर embed करने के बजाय अलग-अलग क्यों embed करता है?

<details markdown="1"><summary>जाँचें</summary>

ताकि हर passage पहले से, एक बार embed होकर store हो सके; search के समय सिर्फ़ query को embed करना पड़े, और उसकी तुलना पहले से निकले passage vectors से सस्ते में हो सके।

</details>

2. ▢ `vector_l2_ops` से बना index `<=>` (cosine distance) से क्रम देने वाली query को तेज़ करने में क्यों नाकाम रहता है?

<details markdown="1"><summary>जाँचें</summary>

Index एक ख़ास distance function के लिए बनता है; operator class और query का operator मेल खाने चाहिए, वरना index इस्तेमाल नहीं होता और query पूरे sequential scan पर लौट जाती है।

</details>

## यह जानें

### BM25 term के overlap को score करता है, अर्थ को नहीं

**BM25** एक lexical ranking function है: वह document की query से प्रासंगिकता को पूरी तरह इस आधार पर score करता है कि कौन-से query terms document में शब्दशः मौजूद हैं, कितनी बार, और हर term कितना जानकारीपूर्ण है, बिना किसी embedding के और अर्थ की किसी धारणा के बिना। इसके score में तीन सामग्रियाँ मिलती हैं: **inverse document frequency (IDF)**, जो query term को इस आधार पर वज़न देता है कि वह पूरे corpus में कितना दुर्लभ है ("the" जैसा आम शब्द लगभग कुछ नहीं जोड़ता, क्योंकि वह हर जगह है और किसी को अलग नहीं करता; दुर्लभ, ख़ास term बहुत जोड़ता है, क्योंकि उसकी मौजूदगी जानकारीपूर्ण है); **term frequency**, यानी query term इस ख़ास document में कितनी बार आता है, पर रैखिक रूप से बढ़ने के बजाय **saturate** होकर, इसलिए 10 बार आने वाला term एक बार आने वाले से 10 गुना ऊँचा score नहीं पाता, जो keyword-stuffing को score पर हावी होने से रोकता है; और **length normalization**, जो document के सिर्फ़ औसत से लंबा होने से मिले कच्चे term-frequency लाभ में कटौती करता है, क्योंकि लंबे document के पास सिर्फ़ आकार के कारण किसी भी term को समाने के ज़्यादा मौक़े होते हैं, ज़रूरी नहीं कि वह ज़्यादा प्रासंगिक हो।

### अच्छे embedding model के बग़ल में lexical search अब भी मायने क्यों रखता है

Embedding models semantic similarity पकड़ने के लिए train होते हैं, और समानार्थी शब्दावली के लिए वे इसे अच्छी तरह करते हैं: "how to fix a broken pipe" वाली query "resolving a leaking conduit" के बारे में passage को retrieve कर सकती है, भले ही एक भी शब्द साझा न हो, क्योंकि दोनों के अर्थ मिलते-जुलते हैं। पर वही training embeddings को ठीक, ख़ास term के मिलान में तुलनात्मक रूप से कमज़ोर बनाती है: product code, error identifier, दुर्लभ विशेष नाम, कोई ठीक वाक्यांश जिसे उपयोगकर्ता शब्दशः उद्धृत कर रहा हो। "error code E502" वाली query को ऐसा document चाहिए जिसमें शब्दशः "E502" हो; embedding model, जो सटीक identifier के मिलान की जगह सामान्य semantic similarity पर train हुआ, ऐसे documents retrieve कर सकता है जो विषय के रूप में error handling के बारे में हैं, पर उस एक document को सामने न लाए जिसमें असल में वही ख़ास code है जो उपयोगकर्ता ने टाइप किया। BM25 का अंधा बिंदु उलटा है: ठीक उलटा मामला, "broken pipe" बनाम "leaking conduit", BM25 में शून्य के क़रीब score करेगा, क्योंकि दोनों में कोई term साझा नहीं, भले ही अर्थ एक हो। हर तरीक़ा वह पकड़ता है जो दूसरा चूकता है, और यही दोनों को मिलाने का तर्क है, किसी एक को चुनने का नहीं।

![दो-गुना-दो की तालिका। पहली पंक्ति: "error code E502" जैसी exact-identifier query। BM25 उसे match करता है, क्योंकि शब्दशः string document में आती है; vector search उसे चूक सकता है, क्योंकि उसका embedding model semantic similarity के लिए train हुआ, exact identifier matching के लिए नहीं। दूसरी पंक्ति: "broken pipe" जैसी समानार्थी शब्दावली वाली query, "leaking conduit" पढ़ने वाले document के विरुद्ध, जिनमें कोई शब्द साझा नहीं। BM25 इसे शून्य के क़रीब score करता है, क्योंकि वह सिर्फ़ शब्दशः term overlap गिनता है; vector search इसे match करता है, क्योंकि दोनों वाक्यांशों का अर्थ एक है। हर तरीक़े का अंधा बिंदु दूसरे तरीक़े की ताक़त है।](images/bm25-vs-vector-blindspots.svg)

## अभ्यास

1. ▢ एक उपयोगकर्ता ठीक error code "E502" खोजता है। अकेला vector search उस एक document को कम retrieve क्यों कर सकता है जिसमें वह string असल में है, जबकि corpus में error handling के बारे में कई documents हैं?

<details markdown="1"><summary>जाँचें</summary>

Embedding model semantic similarity पकड़ने के लिए train हुआ था, exact identifier matching के लिए नहीं, इसलिए "E502" embedding space में एक विशिष्ट बिंदु के रूप में अच्छी तरह प्रदर्शित नहीं हो सकता; जो documents आम तौर पर error handling के बारे में विषय के रूप में मिलते-जुलते हैं, वे query की embedding के उस एक document से ज़्यादा पास आ सकते हैं जिसमें संयोग से शब्दशः string "E502" है।

</details>

2. ▢ एक query है "how to fix a broken pipe", और सबसे अच्छा मेल खाने वाला document "resolving a leaking conduit" शब्दों में लिखा है, जिसमें query से कोई शब्द साझा नहीं। क्या BM25 इस जोड़ी को ऊँचा score देगा? क्यों या क्यों नहीं?

<details markdown="1"><summary>जाँचें</summary>

नहीं, BM25 इसे शून्य के क़रीब score देगा, क्योंकि वह सिर्फ़ इस आधार पर score करता है कि कौन-से query terms document में शब्दशः मौजूद हैं, और इस जोड़ी में कोई term साझा नहीं। BM25 के पास यह पहचानने का कोई तरीक़ा नहीं कि दोनों शब्दावलियों का अर्थ एक है; यही वह अंतर है जिसे vector search की semantic similarity भरने के लिए है।

</details>

3. ▢ BM25 term frequency को saturate क्यों करता है (किसी term के बार-बार आने से score की बढ़ोतरी घटाता है) बजाय उसे रैखिक रूप से score करने के?

<details markdown="1"><summary>संकेत</summary>

सोचें कि रैखिक term-frequency score को कोई document कैसे ठग सकता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

रैखिक term-frequency score किसी document को सिर्फ़ query term को कई बार दोहराकर (keyword stuffing) ranking पर हावी होने देता, चाहे document असल में ज़्यादा प्रासंगिक हो या नहीं। Term frequency को saturate करने का मतलब है कि हर अतिरिक्त आगमन पिछले से कम जोड़ता है, इसलिए प्रासंगिकता को फिर भी इनाम मिलता है पर अकेली कच्ची पुनरावृत्ति score पर हावी नहीं हो पाती।

</details>

4. ▢ BM25 document की लंबाई के लिए normalize क्यों करता है, और उस normalization के बिना क्या ग़लत होता?

<details markdown="1"><summary>जाँचें</summary>

लंबे document के पास सिर्फ़ ज़्यादा शब्द होने से किसी भी query term को समाने के ज़्यादा मौक़े होते हैं, इस बात से स्वतंत्र कि वह query के लिए असल में ज़्यादा प्रासंगिक है या नहीं। Length normalization के बिना, लंबे documents व्यवस्थित रूप से छोटे, बराबर या ज़्यादा प्रासंगिक documents से आगे निकल जाते, सिर्फ़ अपने आकार के कारण, असली प्रासंगिकता के कारण नहीं।

</details>

5. ▢ Vector search की तुलना में BM25 के बारे में कौन-सा दावा सही है?

    - a) BM25 और vector search ठीक एक-जैसी queries पर विफल होते हैं, इसलिए उन्हें मिलाने से कुछ नहीं जुड़ता
    - b) BM25 exact term matching में उत्कृष्ट है पर बिना साझा शब्दों वाली समानार्थी शब्दावली को चूकता है, जबकि vector search उलटा करता है
    - c) BM25 को term की प्रासंगिकता निकालने के लिए embedding model चाहिए
    - d) Vector search किसी भी query के लिए हमेशा BM25 से बेहतर चलता है, क्योंकि वह सिर्फ़ शब्दों की नहीं बल्कि अर्थ की पकड़ रखता है

<details markdown="1"><summary>जाँचें</summary>

**b)** हर तरीक़े का अंधा बिंदु दूसरे की ताक़त है, और यही hybrid search का पूरा आधार है। (a) ग़लत है: उनकी विफलता के तरीक़े एक-जैसे नहीं, उलटे हैं। (c) ग़लत है: BM25 पूरी तरह term-statistics वाला तरीक़ा है जिसमें embedding का कोई दख़ल नहीं। (d) ग़लत है: exact identifier या code का मिलान ठीक वह स्थिति है जहाँ BM25 semantic embedding से बेहतर चल सकता है।

</details>

## असली दुनिया का अभ्यास

- [ ] अपने corpus के लिए ऐसी query ढूँढें या लिखें जिसमें कोई ख़ास identifier, code या ठीक वाक्यांश हो, और जाँचें कि आपका मौजूदा retrieval setup (अगर सिर्फ़ vector है) उसे रखने वाले document को असल में सामने लाता है या नहीं।
- [ ] अपने corpus में ऐसी query और मेल खाता document ढूँढें जो बहुत कम या कोई ठीक शब्द साझा न करते हों पर अर्थ एक हो, और अनुमान लगाएँ कि सिर्फ़ BM25 search उस जोड़ी को कैसे score करेगा।
- [ ] कल: देखें कि आपका search stack (Postgres full-text search, Elasticsearch या कुछ ऐसा) पहले से BM25-जैसा ranking function देता है या नहीं जिसकी तुलना आप अपने vector search के नतीजों से कर सकें।

## आगे बढ़ने के लिए

- [पेपर: "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson and Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- [दस्तावेज़: "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
