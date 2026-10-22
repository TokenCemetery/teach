---
title: "3. Embedding Dimensionality के Trade-offs"
description: "बड़ा embedding vector मुफ़्त क्यों नहीं है, और छोटा model चुनने के बजाय उसे truncate करना कब सुरक्षित है"
type: lesson
---

# पाठ 3. Embedding Dimensionality के Trade-offs

**मिशन से संबंध:** यह चरण 2 का समापन है: embedding model चुनना (पाठ 2) तब तक पूरा नहीं होता जब तक उसके output के आकार को इस बात के सामने न तौल लिया जाए कि corpus का storage और latency budget असल में क्या वहन कर सकता है।
**मुख्य स्रोत:** [पेपर: "Matryoshka Representation Learning", Kusupati et al., 2022](https://arxiv.org/abs/2205.13147)
**पूर्व-आवश्यकताएँ:** [पाठ 2](0002-embedding-models-and-similarity.md), [Chunk](../GLOSSARY.md)

## वार्म-अप

1. ▢ Bi-encoder query और passage को साथ मिलाकर embed करने के बजाय अलग-अलग क्यों embed करता है?

<details markdown="1"><summary>जाँचें</summary>

ताकि हर passage पहले से, एक बार embed होकर store हो सके; search के समय सिर्फ़ query को embed करना पड़े, और उसकी तुलना पहले से निकले passage vectors से सस्ते में हो सके। साथ मिलाकर embed करना (cross-encoder) हर जोड़ी पर model चलाने की माँग करता है, जो बड़े corpus पर scale नहीं करता।

</details>

2. ▢ Cosine similarity और dot product एक ही ranking सिर्फ़ तब क्यों देते हैं जब vectors unit length तक normalized हों?

<details markdown="1"><summary>जाँचें</summary>

Dot product वह cosine similarity है जिसे दोनों vectors के magnitudes से scale किया गया हो। जब दोनों unit length पर तय हों, तो वह scaling factor हर जोड़ी में एक-सा रहता है, इसलिए दोनों metrics एक-सी ranking देती हैं; जब magnitudes बदलते हों, तो dot product परोक्ष रूप से बड़े vectors को इनाम देता है।

</details>

## यह जानें

### Dimensionality एक लागत है, मुफ़्त में मिलने वाला गुणवत्ता का knob नहीं

ज़्यादा dimensions वाली embedding ज़्यादा बारीकी encode कर सकती है, पर उसकी हर dimension कुछ ठोस क़ीमत लेती है: storage dimension के साथ रैखिक रूप से बढ़ता है (float32 में 1536-dimension vector `1536 × 4 bytes = 6,144 bytes` लेता है, यानी लगभग 6 KB, जबकि 256-dimension vector `256 × 4 = 1,024 bytes` लेता है, लगभग 1 KB, छह गुना कम), और index की memory व हर candidate की distance गणना भी उसी तरह बढ़ती हैं। दस लाख chunks पर यह फ़र्क़ सिर्फ़ vectors के लिए 6 GB बनाम 1 GB है, index के अपने overhead से पहले। बड़ी embedding अपने-आप बेहतर चुनाव नहीं है; यह ऐसा चुनाव है जिसे उसकी लागत के सामने सही ठहराना पड़ता है, उसी तरह जैसे दूसरे serving संदर्भों में बड़े KV cache या बड़े batch size को workload के असली budget के सामने सही ठहराना पड़ता था।

### Matryoshka Representation Learning: truncation एक डिज़ाइन की हुई सुविधा के रूप में, जुगाड़ के रूप में नहीं

आम तौर पर embedding vector को कम dimensions तक truncate करना सुरक्षित नहीं है: standard embedding model के train होने के तरीक़े में कुछ भी उसकी dimensions को अहमियत के क्रम में नहीं रखता, इसलिए आम 768-dimension vector को 256 तक काट देना अनिश्चित ढंग से जानकारी फेंक सकता है और गुणवत्ता को dimension की गिनती से अंदाज़े से कहीं ज़्यादा गिरा सकता है। **Matryoshka Representation Learning (MRL)** model को अलग ढंग से train करता है: उसका loss पूरे vector के prefixes (मान लें 1536-dimension embedding की पहली 256 dimensions) को ख़ुद इस्तेमाल लायक, अर्थपूर्ण embeddings बनने के लिए साफ़ तौर पर optimize करता है, जो पूरे embedding के भीतर वैसे ही नीड़ित रहते हैं जैसे matryoshka गुड़िया के भीतर छोटी गुड़ियाँ। इसका मतलब है कि MRL से train हुए model को बाद में truncate किया जा सकता है, सीमित और अनुमान लगाने लायक गुणवत्ता लागत पर, जिससे dimensionality को storage और latency के बदले घटाया-बढ़ाया जा सकता है, बिना retrain किए या पूरे corpus को किसी और आकार में दोबारा embed किए। यह सिर्फ़ उन्हीं models पर लागू है जो असल में इस तरह train हुए; जो model ऐसा नहीं है उसे truncate करना फिर उसी असुरक्षित, अनिश्चित स्थिति में लौट जाता है।

![एक पट्टी के रूप में खींचा गया एक अकेला 1536-dimension vector, जिस पर बिंदीदार रेखाएँ दिखाती हैं कि उसकी पहली 256 और पहली 768 dimensions कहाँ ख़त्म होती हैं। पट्टी के ऊपर तीन कोष्ठक वाले दायरे, जो सब dimension 0 से शुरू होते हैं, दिखाते हैं कि 256 पर रुकना, 768 पर रुकना, या पूरी 1536 dimensions पढ़ना, हर एक इस्तेमाल लायक, अर्थपूर्ण embedding देता है, क्योंकि Matryoshka Representation Learning ने vector के हर prefix को अपने आप काम करने के लिए train किया है, standard embedding model के उलट जहाँ सिर्फ़ पूरा vector अर्थपूर्ण होता है।](images/matryoshka-prefix-embeddings.svg)

### सही dimensionality तय करने का मतलब मापना है, मान लेना नहीं

किसी दिए corpus के लिए सही dimensionality अंदाज़े से चुनने वाली संख्या नहीं है; यह मापने वाली संख्या है। MRL model का इस्तेमाल करके (या कई candidate model आकारों की तुलना करके), retrieval की गुणवत्ता, सबसे सीधे labeled या synthetic query सेट पर recall@k (चरण 6 का विषय), हर candidate dimensionality पर उस असली corpus और query पैटर्न पर मापी जा सकती है। जो dimensionality ship करने लायक है वह सबसे छोटी है जो फिर भी उस गुणवत्ता की कसौटी पर खरी उतरे जो workload को चाहिए, सबसे बड़ी उपलब्ध नहीं, और बिना जाँचे चुना गया default भी नहीं कि वह जो क़ीमत लेता है उसके बदले क्या देता है।

## अभ्यास

1. ▢ एक corpus में 20 लाख chunks हैं। उसे 1536 dimensions और 256 dimensions पर embed करने के बीच storage का फ़र्क़, गीगाबाइट में, निकालें, दोनों float32 में।

<details markdown="1"><summary>संकेत</summary>

हर vector के bytes `dimensions × 4 bytes` होते हैं। 20 लाख से गुणा करें, फिर गीगाबाइट में बदलें।

</details>

<details markdown="1"><summary>जाँचें</summary>

1536 dimensions: हर vector के `1536 × 4 = 6,144 bytes`, `× 2,000,000 ≈ 12.3 GB`। 256 dimensions: हर vector के `256 × 4 = 1,024 bytes`, `× 2,000,000 ≈ 2.0 GB`। फ़र्क़ लगभग 10.3 GB है, यानी 256 dimensions पर लगभग छह गुना कम storage।

</details>

2. ▢ एक टीम standard (non-MRL) 768-dimension embedding model के vectors को storage बचाने के लिए 256 dimensions तक truncate करती है, और retrieval की गुणवत्ता dimension घटाने से अंदाज़े से कहीं ज़्यादा ढह जाती है। संभावित ग़लती क्या है?

<details markdown="1"><summary>जाँचें</summary>

Model Matryoshka Representation Learning से train नहीं हुआ था, इसलिए किसी ने उसकी dimensions को अहमियत के क्रम में नहीं रखा था और न vector के किसी prefix को अपने आप में अर्थपूर्ण embedding बनाया था। उसे truncate करना जानकारी को अनिश्चित ढंग से फेंकता है, उस सीमित, डिज़ाइन किए गए ढंग से नहीं जैसे MRL से train हुए model का truncation करता।

</details>

3. ▢ MRL से train हुआ embedding model टीम को ऐसा क्या करने देता है जो standard embedding model नहीं देता?

<details markdown="1"><summary>जाँचें</summary>

पूरे embedding vector को बाद में छोटी dimensionality तक truncate करना, सीमित और अनुमान लगाने लायक गुणवत्ता लागत पर, यानी storage और latency को गुणवत्ता के बदले घटाना-बढ़ाना, बिना model को retrain किए या corpus को किसी और तय आकार में दोबारा embed किए।

</details>

4. ▢ टीम को यह कैसे तय करना चाहिए कि अपने corpus के लिए असल में कौन-सी embedding dimensionality इस्तेमाल करे, बजाय model के पूरे output आकार को default मान लेने के?

<details markdown="1"><summary>जाँचें</summary>

कई candidate dimensionalities पर retrieval की गुणवत्ता मापें, सबसे सीधे recall@k जैसी चीज़ को ऐसे labeled या synthetic query सेट के विरुद्ध जो असली corpus और query पैटर्न का प्रतिनिधि हो, और सबसे छोटी वह चुनें जो फिर भी workload की ज़रूरी गुणवत्ता की कसौटी पर खरी उतरे, यह मानने के बजाय कि सबसे बड़ी उपलब्ध dimensionality ज़रूरी है या छोटी अपने-आप "काफ़ी अच्छी" है।

</details>

5. ▢ Embedding dimensionality के बारे में कौन-सा दावा सही है?

    - a) बड़ी embedding dimensionality हमेशा retrieval की गुणवत्ता इतनी बेहतर करती है कि उसकी लागत सही ठहरे
    - b) किसी भी embedding model के vectors को truncate करना बराबर सुरक्षित है, चाहे model कैसे भी train हुआ हो
    - c) Dimensionality एक लागत है (storage, index memory, हर candidate की गणना) जिसका आकार उस सबसे छोटे मान जितना रखना चाहिए जो मापी गई गुणवत्ता की कसौटी पूरी करे
    - d) MRL से train हुए models को truncate नहीं किया जा सकता; वे सिर्फ़ एक तय, अकेला output आकार देते हैं

<details markdown="1"><summary>जाँचें</summary>

**c)** Storage और गणना की लागतें dimensionality के साथ बढ़ती हैं, इसलिए सही आकार वह सबसे छोटा मान है जो मापी गई गुणवत्ता की कसौटी को असल में चाहिए। (a) ग़लत है: लागत को मापे गए फ़ायदे के सामने तौलना पड़ता है, मान नहीं लिया जाता। (b) ग़लत है: non-MRL model को truncate करना अनिश्चित है और dimension की गिनती से जितना लगता है उससे कहीं ज़्यादा signal नष्ट कर सकता है। (d) ग़लत है: वह लचीला truncation ठीक वही है जिसे MRL training संभव करने के लिए बनी है।

</details>

## असली दुनिया का अभ्यास

- [ ] जाँचें कि जो embedding model आप इस्तेमाल करते हैं (या करने की योजना है) वह Matryoshka Representation Learning से train हुआ था या नहीं, और अगर हाँ, तो किन dimensionalities तक truncate करने का वह समर्थन करता है।
- [ ] अपने model की पूरी dimensionality और एक छोटे candidate आकार पर storage लागत निकालें, हर vector के bytes में और अपने असली corpus आकार के लिए।
- [ ] कल: अगर आपके पास labeled या synthetic query सेट है, तो दो अलग embedding dimensionalities पर recall मापें और गुणवत्ता के फ़र्क़ की तुलना storage के फ़र्क़ से करें।

## आगे बढ़ने के लिए

- [पेपर: "Matryoshka Representation Learning", Kusupati et al., 2022](https://arxiv.org/abs/2205.13147)
- [पेपर: "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks", Reimers and Gurevych, 2019](https://arxiv.org/abs/1908.10084)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
