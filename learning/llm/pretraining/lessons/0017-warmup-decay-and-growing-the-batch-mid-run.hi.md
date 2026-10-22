---
title: "17. Warmup, Decay, और Run के बीच Batch बढ़ाना"
description: "धीमे शुरू करना, schedule के हिसाब से decay करना, और training के बीच में batch size को ही बदलने देना"
type: lesson
---

# पाठ 17. Warmup, Decay, और Run के बीच Batch बढ़ाना

**मिशन से संबंध:** "Loss curve देखकर बता सकें कि spike recover होने लायक़ है या पुराने checkpoint से restart चाहिए" "सफलता कैसी दिखती है" का वह बिंदु है जिसे यह चरण पूरा करता है। पाठ 16 ने spikes और उनसे बचाने वाली clipping को कवर किया; यह पाठ उस schedule को कवर करता है जो run को उस सुरक्षा के इर्द-गिर्द ढालता है।
**मुख्य स्रोत:** [पेपर: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**पूर्व-आवश्यकताएँ:** [पाठ 16](0016-loss-spikes-and-the-optimizers-own-instabilities.md)

## वार्म-अप

1. ▢ Global gradient-norm clipping उस gradient का क्या करती है जिसका norm clipping सीमा से ऊपर जाता है, और Rae et al. ने ख़ास तौर पर अपने दो सबसे बड़े models के लिए सीमा क्यों घटाई?

<details markdown="1"><summary>जाँचें</summary>

वह पूरे gradient को अनुपात में rescale करती है ताकि उसका norm सीमा के बराबर हो जाए, जिससे एक अकेला update कितना बड़ा हो सकता है उस पर रोक लगती है। Rae et al. ने ख़ास तौर पर 7.1B model और Gopher (280B) के लिए सीमा 1 से घटाकर 0.25 की, उस पैमाने पर बेहतर स्थिरता के लिए।

</details>

2. ▢ कम learning rate Rae et al. के 7.1B Adafactor run को स्थिर क्यों नहीं कर पाया, और उस विफलता ने क्या संकेत दिया?

<details markdown="1"><summary>जाँचें</summary>

Adafactor run ने पहले ही स्थिर Adam baseline से कम learning rate इस्तेमाल किया था और फिर भी अस्थिरताएँ दिखीं, जिसका संकेत था कि अस्थिरता उस पैमाने पर optimizer से ही आई, सिर्फ़ ज़्यादा ऊँचे learning rate से नहीं।

</details>

## यह जानें

### जान-बूझकर धीमे शुरू करना

Rae et al. training उस अधिकतम learning rate से शुरू नहीं करते जो उनका schedule इस्तेमाल करता है। इसके बजाय, वे learning rate को `10^-7` से अधिकतम मान तक पहले 1,500 steps में धीरे-धीरे warm up करते हैं, और उसके बाद उसे बाक़ी schedule का पालन करने देते हैं। ताज़ा initialize हुए network के बिल्कुल पहले updates पूरे run के सबसे कम जानकारी वाले updates होते हैं: weights ने अब तक कोई data नहीं देखा, इसलिए उनसे निकला update बाद के उस update की तुलना में बेकार, ज़्यादा बड़ा सुधार होने की ज़्यादा संभावना रखता है जो तब निकलता है जब network पहले से data पर ठीक-ठाक fit हो। Learning rate को शून्य के पास से शुरू करके बढ़ाने से उन सबसे शुरुआती, सबसे कम भरोसेमंद updates का weights पर असर छोटा रहता है, बजाय इसके कि वे model को उतनी ज़ोर से झकझोरें जितना पूरी तरह warm-up हो चुका update झकझोरता।

### उसके बाद decay

Warmup ख़त्म होने के बाद, Rae et al. बाक़ी training में learning rate को 10 के factor से घटाते हैं, cosine schedule के अनुसार: एक सहज curve जो अधिकतम learning rate से शुरू होता है और cosine तरंग के एक चौथाई जैसे आकार में अंतिम मान की ओर घटता है, अचानक सीढ़ियों में गिरने के बजाय। यह warmup से अलग फ़ैसला है, training के अलग बिंदु को निशाना बनाता है: जहाँ warmup run की बिल्कुल शुरुआत की रक्षा करता है, decay इसके बारे में है कि training आगे बढ़ने पर छोटे, ज़्यादा सावधान कदम उठाए जाएँ, क्योंकि अच्छे हल के पास loss landscape को आम तौर पर शुरुआत में काम आने वाले बड़े कदमों से बारीक समायोजन चाहिए।

### बड़े models, कम peak learning rates

Rae et al. यह संबंध साफ़ कहते हैं: जैसे-जैसे model size बढ़ता है, वे उस अधिकतम learning rate को घटाते हैं जिस तक schedule warm up होता है और जिससे decay होता है। जो learning rate छोटे model के लिए बिल्कुल ठीक है वह अपने-आप बहुत बड़े model के लिए सुरक्षित नहीं है; हर train किए गए size पर एक ही तय मान दोबारा इस्तेमाल करने के बजाय हर model का अपना अधिकतम learning rate चुनना उसी का हिस्सा है जो बड़े runs को उस range के भीतर रखता है जिसकी रक्षा के लिए पाठ 16 की clipping और इस पाठ का warmup बने हैं।

### Batch size ख़ुद भी run के बीच बदल सकता है

Learning rate schedule के साथ, Rae et al. एक और लीवर बताते हैं: training के दौरान ही batch size बढ़ाना। Gopher का अपना batch size उसके training run के दौरान तीस लाख से साठ लाख tokens प्रति batch तक बढ़ा, पहले step से आख़िरी तक तय नहीं रहा। बड़ा batch हर step पर कम noisy, ज़्यादा भरोसेमंद gradient अनुमान और बेहतर hardware उपयोग देता है, पर पूरे run को तुरंत सबसे बड़े batch size पर शुरू करना उन फ़ायदों को पूरे समय पाने के लिए ज़रूरी नहीं है; बीच में उसमें बढ़ते जाना अपने-आप में एक schedule फ़ैसला है, learning rate के warmup और decay के साथ, न कि ऐसी चीज़ जिसे पूरे run के लिए शुरू से तय करना ही पड़े।

## अभ्यास

1. ▢ ताज़ा initialize हुए network के पहले updates कैसे दिखते हैं, यह देखते हुए, बिना warmup के तुरंत अधिकतम learning rate से training शुरू करना धीरे-धीरे warm up करने से ज़्यादा जोखिम भरा क्यों हो सकता है?

<details markdown="1"><summary>जाँचें</summary>

Network के सबसे शुरुआती updates, जो उसके कोई data देखने से पहले निकले हों, पूरे run के सबसे कम जानकारी वाले होते हैं और बेकार, ज़्यादा बड़े सुधार होने की ज़्यादा संभावना रखते हैं। ऐसे update पर पूरी ताक़त का learning rate लगाने से weights ग़लत दिशा में ज़ोर से झूल सकते हैं; warmup सीमित करता है कि वे सबसे शुरुआती, सबसे कम भरोसेमंद updates कितना असर डाल सकें।

</details>

2. ▢ Warmup किस चीज़ से बचाता है और cosine decay किसे निशाना बनाता है, इन दोनों में व्यावहारिक अंतर क्या है?

<details markdown="1"><summary>जाँचें</summary>

Warmup training की बिल्कुल शुरुआत की रक्षा करता है, जब network के updates सबसे कम जानकारी वाले होते हैं। Cosine decay बाद की training के बारे में है, धीरे-धीरे छोटे कदम उठाना, क्योंकि अच्छे हल के पास loss landscape को आम तौर पर पहले काम आने वाले बड़े कदमों से बारीक समायोजन चाहिए। वे एक ही run के अलग बिंदुओं को संबोधित करते हैं, एक ही समस्या को दो बार नहीं।

</details>

3. ▢ Rae et al. के अनुसार, बाक़ी सब बराबर होने पर, बड़े model को छोटे model से ऊँचा अधिकतम learning rate मिलता है या नीचा?

<details markdown="1"><summary>जाँचें</summary>

नीचा अधिकतम learning rate। Rae et al. सीधे कहते हैं कि जैसे-जैसे model size बढ़ता है, वे schedule का इस्तेमाल किया अधिकतम learning rate घटाते हैं।

</details>

4. ▢ Gopher का batch size training के दौरान तीस लाख से साठ लाख tokens प्रति batch तक बढ़ा, पहले step से साठ लाख पर शुरू होने के बजाय। तुरंत वहीं शुरू करने के बजाय बड़े batch size में बढ़ते जाने का एक संभावित कारण बताइए।

<details markdown="1"><summary>जाँचें</summary>

कोई भी उचित स्पष्टीकरण स्वीकार्य है, जैसे: training में पहले, जब updates वैसे ही कम स्थिर होते हैं (warmup के तर्क के अनुसार), उसके ऊपर बहुत बड़ा batch जोड़ना उपयोगी gradient अनुमान पाने के लिए ज़रूरी नहीं हो सकता, और batch size को बाद में बढ़ाना बड़े batch के फ़ायदों (कम noisy gradient, बेहतर hardware उपयोग) का तब लाभ उठाता है जब training पहले से ज़्यादा स्थिर क्षेत्र में पहुँच चुकी हो।

</details>

## असली दुनिया का अभ्यास

- [ ] किसी training framework का learning-rate scheduler विकल्पों का दस्तावेज़ खोजें, और पहचानें कि वह warmup चरण देता है, cosine decay चरण देता है, या दोनों, और हर एक कैसे configure होता है।
- [ ] काग़ज़ पर learning-rate-बनाम-training-step का मोटा curve बनाएँ जिसमें warmup (शून्य के पास से छोटी चढ़ाई) के बाद cosine decay (बहुत छोटे अंतिम मान तक सहज curve) हो, और लेबल करें कि Rae et al. का बताया 1,500-step का warmup, मान लें, कुल 3,00,000 steps के run के सापेक्ष मोटे तौर पर कहाँ बैठेगा।
- [ ] कल: अपने चुने हुए किसी model size के लिए (छोटा, मध्यम या बड़ा, अपने शब्दों में), गुणात्मक रूप से तय करें कि आप उसके अधिकतम learning rate को Gopher के क़रीब होने की उम्मीद करेंगे या बहुत छोटे model के, और इस पाठ के model-size संबंध के आधार पर एक वाक्य लिखें कि क्यों।

## आगे बढ़ने के लिए

- [पेपर: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [संसाधन](../RESOURCES.md)

---

चरण 7 ने उन numerics और schedule को कवर किया जो एक अकेले training run को स्थिर रखते हैं। चरण 8 उस ओर मुड़ता है कि ऐसे run को असल में लगने वाले कई दिनों में क्या होता है: progress को save करने, resume करने, और बीच में किसी विफलता से बाधित होने से कैसे बचाया जाए।

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
