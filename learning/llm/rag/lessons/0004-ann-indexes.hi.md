---
title: "4. ANN Indexes: HNSW और IVF"
description: "Vector search सटीकता के बदले रफ़्तार क्यों लेता है, और IVF और HNSW हर एक उस trade-off को एक tunable knob के रूप में कैसे सामने रखता है"
type: lesson
---

# पाठ 4. ANN Indexes: HNSW और IVF

**मिशन से संबंध:** चरण 3 मिशन के उस हिस्से को खोलता है जो असली corpus पर search खड़ा करना है और जहाँ लक्ष्य बदलता रहता है: index ही वह चीज़ है जो vector search को चलने लायक तेज़ बनाता है, एक recall/latency trade-off की क़ीमत पर, जिसका नाम यह पाठ बताता है, इससे पहले कि पाठ 5 उसे pgvector में ठोस बनाए।
**मुख्य स्रोत:** [पेपर: "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", Malkov and Yashunin, 2018](https://arxiv.org/abs/1603.09320)
**पूर्व-आवश्यकताएँ:** [पाठ 3](0003-embedding-dimensionality.md), [Chunk](../GLOSSARY.md)

## वार्म-अप

1. ▢ एक corpus में 20 लाख chunks हैं। उसे float32 में 1536 dimensions पर embed करने में 256 dimensions की तुलना में लगभग कितना storage लगता है?

<details markdown="1"><summary>जाँचें</summary>

1536 dimensions पर लगभग 12.3 GB बनाम 256 dimensions पर लगभग 2.0 GB, क्योंकि हर vector के bytes dimension की गिनती के साथ रैखिक रूप से बढ़ते हैं (`dimensions × 4 bytes`)।

</details>

2. ▢ Matryoshka Representation Learning embedding vector के साथ क्या करने देता है जो standard embedding model सुरक्षित रूप से नहीं करने देता?

<details markdown="1"><summary>जाँचें</summary>

Training के बाद उसे कम dimensions तक truncate करना, सीमित और अनुमान लगाने लायक गुणवत्ता लागत पर, क्योंकि MRL से train हुए model के prefixes ख़ुद अर्थपूर्ण embeddings होते हैं। Standard model की dimensions अहमियत के क्रम में नहीं होतीं, इसलिए उसे truncate करना अनिश्चित है।

</details>

## यह जानें

### सटीक search scale क्यों नहीं करता

Query के असली nearest neighbors ठीक-ठीक ढूँढने का मतलब है उसकी तुलना corpus के हर vector से करना। यह corpus के आकार के साथ रैखिक है: corpus दोगुना हुआ तो search का समय दोगुना, और लाखों chunks पर brute-force तुलना query के समय चलाने के लिए बहुत धीमी हो जाती है। **Approximate nearest neighbor (ANN)** index थोड़ी, नियंत्रित अशुद्धता स्वीकार करता है: वह ऐसे vectors लौटाता है जो असली nearest neighbors के बहुत संभावित रूप से पास हैं, पर ठीक वही होने की गारंटी नहीं, इसके बदले ऐसे search समय पर जो corpus के आकार के साथ रैखिक रूप से नहीं बढ़ते।

### IVF: सिर्फ़ पास के clusters में खोजें

**IVF (inverted file index)** पहले से vector space को clusters में बाँट देता है (आम तौर पर k-means से), और हर vector को उसके सबसे नज़दीकी cluster centroid को सौंप देता है। Query के समय, हर vector को स्कैन करने के बजाय, IVF सिर्फ़ query के सबसे नज़दीकी `nprobe` clusters में खोजता है, जहाँ `nprobe` एक tunable गिनती है। कम `nprobe` (सिर्फ़ एक सबसे नज़दीकी cluster में खोजना) तेज़ है पर ऐसे असली neighbors को चूकने का जोखिम है जो संयोग से सीमा के पास पड़ोसी cluster में बैठे हों। ज़्यादा `nprobe` (कई या सभी clusters में खोजना) सटीक search की recall के क़रीब पहुँचता है, सटीक search की लागत पर। IVF में एक बार की build लागत भी है: clustering चरण को centroids ठीक से रखने के लिए corpus के vectors का प्रतिनिधि नमूना चाहिए।

### HNSW: चलने लायक graph, ऊपर से नीचे खोजा जाता है

**HNSW (hierarchical navigable small world)** clusters की जगह बहु-परत graph बनाता है: हर vector एक node है, जो edges से दूसरे पास के vectors से जुड़ा है, ऊपर की विरल परतें vector space में लंबी छलाँगें लगाने देती हैं और नीचे की घनी परत सटीक स्थानीय search करने देती है। Query विरल ऊपरी परत से शुरू होती है, लालच से उस जुड़े node की ओर कूदती है जो सबसे नज़दीक हो, और परत-दर-परत नीचे उतरती है, अपनी स्थिति को निखारते हुए जब तक घनी निचली परत तक न पहुँचे। यहाँ का tunable knob `ef_search` है, यानी search हर चरण पर कितने candidates का हिसाब रखता है: कम `ef_search` उत्तर जल्दी ढूँढ लेता है पर किसी स्थानीय रूप से अच्छे node पर टिक सकता है जो असली nearest नहीं है; ज़्यादा `ef_search` ज़्यादा candidates खँगालता है, रफ़्तार के बदले recall देता है, उसी आकार का trade-off जो `nprobe` IVF के लिए करता है।

![दो खंड। बाईं ओर IVF: vectors के चार clusters, हर एक का एक centroid। Query दो पास के clusters के बीच बैठी है, जो छायांकित हैं और जिनमें खोजा जाता है, जबकि दो दूर के clusters बिना छाया के छोड़ दिए जाते हैं, कम nprobe सिर्फ़ पास वालों में खोजता है। दाईं ओर HNSW: तीन परतों वाला graph एक के ऊपर एक, ऊपर विरल और नीचे घना, जिसमें ऊपरी परत के प्रवेश बिंदु से एक रास्ता उतरता है, हर परत पर उत्तरोत्तर पास के nodes पर कूदता हुआ, अपनी स्थिति निखारता हुआ जब तक घनी निचली परत पर nearest neighbor तक न पहुँचे।](images/ivf-vs-hnsw.svg)

### सामान्य रूप: recall/latency का वक्र, एक अकेला सही उत्तर नहीं

दोनों indexes एक knob देते हैं (IVF के लिए `nprobe`, HNSW के लिए `ef_search`) जो किसी दिए corpus और index के लिए recall-बनाम-latency वक्र पर एक ख़ास बिंदु तय करता है। HNSW आम तौर पर उस वक्र पर IVF से बेहतर बिंदु पर उतरता है, उतनी ही latency पर ज़्यादा recall, ज़्यादा memory (graph की अपनी संरचना) और धीमे index build की क़ीमत पर। किसी भी index की कोई एक सार्वभौमिक रूप से सही setting नहीं है: सही बिंदु workload के latency budget पर निर्भर करता है और इस पर कि कोई बाद का चरण, जैसे reranking, अंतिम नतीजे को नुक़सान पहुँचाए बिना कितनी recall हानि सोख सकता है, और ठीक यही मापने के लिए चरण 6 की retrieval metrics हैं, मान लेने के लिए नहीं।

## अभ्यास

1. ▢ Brute-force सटीक nearest-neighbor search लाखों vectors के corpus पर scale क्यों नहीं करता, और इसे ठीक करने के लिए ANN index क्या छोड़ देता है?

<details markdown="1"><summary>जाँचें</summary>

सटीक search query की तुलना हर vector से करता है, इसलिए उसकी लागत corpus के आकार के साथ रैखिक रूप से बढ़ती है और लाखों vectors पर बहुत धीमी हो जाती है। ANN index असली nearest neighbors को ठीक-ठीक पाने की गारंटी छोड़ देता है, किसी को चूक जाने की थोड़ी, नियंत्रित संभावना स्वीकार करता है, ऐसे search समय के बदले जो उस तरह scale नहीं करता।

</details>

2. ▢ IVF index के लिए, `nprobe` parameter के हर छोर पर क्या होता है, वर्णन करें: `nprobe = 1` बनाम `nprobe` इतना कि हर cluster में खोजे।

<details markdown="1"><summary>जाँचें</summary>

`nprobe = 1` सिर्फ़ एक सबसे नज़दीकी cluster में खोजता है: सबसे तेज़, पर वह ऐसे असली nearest neighbor को चूक सकता है जो सीमा के पास पड़ोसी cluster में बैठा हो, ख़ासकर अगर query cluster के किनारे के पास पड़े। `nprobe` इतना कि हर cluster में खोजे, सटीक search के क़रीब पहुँचता है: सबसे ऊँची recall, पर सटीक search की लागत पर, क्योंकि अब वह corpus के ज़्यादातर हिस्से को छोड़ता नहीं।

</details>

3. ▢ HNSW का `ef_search` parameter HNSW के लिए वही भूमिका कैसे निभाता है जो `nprobe` IVF के लिए निभाता है?

<details markdown="1"><summary>संकेत</summary>

सोचें कि हर parameter क्या नियंत्रित करता है: उत्तर लौटाने से पहले index का कितना हिस्सा जाँचा जाता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

`ef_search` नियंत्रित करता है कि HNSW की परतों में उतरते हुए graph search हर चरण पर कितने candidates का हिसाब रखे। कम मान कम candidates खँगालता है, उत्तर जल्दी ढूँढता है पर ऐसे node पर टिकने का जोखिम लेता है जो असली nearest नहीं है। ज़्यादा मान ज़्यादा candidates खँगालता है, search की रफ़्तार के बदले ऊँची recall देता है, वही recall-बनाम-latency आकार जो `nprobe` IVF को देता है।

</details>

4. ▢ किसी दिए corpus के लिए HNSW चुनने और IVF चुनने के बीच सामान्य trade-off क्या है?

<details markdown="1"><summary>जाँचें</summary>

HNSW आम तौर पर किसी दी गई latency पर IVF से बेहतर recall का बिंदु पाता है, पर ज़्यादा memory लेता है (graph के edges सिर्फ़ vectors को store करने से ऊपर असली overhead जोड़ते हैं) और index को पहली बार बनाने में ज़्यादा समय लेता है। IVF बनाने और store करने में सस्ता है, पर उसी latency पर HNSW की recall की बराबरी करने के लिए आम तौर पर corpus के बड़े हिस्से में खोजना पड़ता है।

</details>

5. ▢ ANN index के search-time parameter (`nprobe` या `ef_search`) को tune करने के बारे में कौन-सा दावा सही है?

    - a) एक सार्वभौमिक रूप से सही setting है जो किसी भी corpus और workload पर चलती है
    - b) सही setting recall/latency वक्र पर एक बिंदु है जिसे workload के असली latency budget और recall हानि की सहनशीलता के विरुद्ध चुनना पड़ता है
    - c) Parameter को जितना हो सके उतना ऊँचा रखना हमेशा सही चुनाव है, क्योंकि index बन जाने के बाद latency मायने नहीं रखती
    - d) Parameter सिर्फ़ index build के समय को प्रभावित करता है, query-time व्यवहार को नहीं

<details markdown="1"><summary>जाँचें</summary>

**b)** दोनों parameters query के समय recall को latency के सामने तौलते हैं, और सही बिंदु इस पर निर्भर है कि workload को असल में क्या चाहिए, जिसे चरण 6 मापता है, मान नहीं लेता। (a) ग़लत है: recall/latency वक्र ठीक यही बात नकारता है। (c) ग़लत है: ऊँची setting query-time latency ज़्यादा लेती है, जो तब मायने रखती है जब भी कोई latency budget पूरा करना हो। (d) ग़लत है: `nprobe` और `ef_search` दोनों search-time parameters हैं, build-time नहीं।

</details>

## असली दुनिया का अभ्यास

- [ ] पता करें कि आपका vector store कौन-सा index प्रकार (IVF या HNSW) इस्तेमाल करता है या default में रखता है, और उसके दस्तावेज़ में उसका search-time recall/latency parameter ढूँढें।
- [ ] अगर आप किसी index के विरुद्ध queries चला सकते हैं, तो `nprobe` या `ef_search` के दो अलग मान आज़माएँ और query latency में फ़र्क़ देखें।
- [ ] कल: HNSW पेपर में उसकी परतों वाली संरचना के वर्णन का एक अनुच्छेद पढ़ें और अपने शब्दों में नोट करें कि लंबी दूरी की छलाँगें काम करें इसके लिए ऊपरी परत को विरल क्यों होना चाहिए।

## आगे बढ़ने के लिए

- [पेपर: "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", Malkov and Yashunin, 2018](https://arxiv.org/abs/1603.09320)
- [Repo: pgvector, pgvector](https://github.com/pgvector/pgvector)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
