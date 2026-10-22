---
title: "19. Node Failure से बचना"
description: "रुकें, जाँचें, जो टूटा है उसे अलग करें, और आख़िरी checkpoint से resume करें, चाहे जो भी क़ीमत लगे"
type: lesson
---

# पाठ 19. Node Failure से बचना

**मिशन से संबंध:** "ऐसी checkpointing योजना बना सकें जो node failure के बाद खोई हुई progress को सीमित रखे" "पूरी रूपरेखा" में इस चरण के "कब पूरा माना जाए" खाने में लिखा है। पाठ 18 ने कवर किया कि checkpoint में क्या होना चाहिए और कितनी बार save करना है; यह पाठ कवर करता है कि विफलता आने पर असल में क्या होता है।
**मुख्य स्रोत:** [पेपर: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
**पूर्व-आवश्यकताएँ:** [पाठ 18](0018-what-a-checkpoint-has-to-hold.md)

## वार्म-अप

1. ▢ वे चार चीज़ें बताइए जो checkpoint को run को सिर्फ़ लगभग नहीं, सही ढंग से resume करने के लिए रखनी होती हैं।

<details markdown="1"><summary>जाँचें</summary>

Model parameters, optimizer state, step count और learning-rate schedule की स्थिति, और, हू-ब-हू दोहराव के लिए, data-loader की स्थिति और random-number-generator state।

</details>

2. ▢ OPT-175B की लगभग दो महीने की training में, Zhang et al. ने बताया कि hardware विफलताएँ कितनी बार हुईं?

<details markdown="1"><summary>जाँचें</summary>

कम से कम 35 manual restarts और 100 से ज़्यादा hosts का बदला जाना, साथ में अनुमानित 70 से ज़्यादा अतिरिक्त automatic restarts, यानी run में लगातार हर दो दिन में एक restart से कहीं ज़्यादा।

</details>

## यह जानें

### OPT ने असल में कौन-सी प्रक्रिया अपनाई

Zhang et al. एक ख़ास, दोहराई जा सकने वाली क्रमबद्ध प्रक्रिया बताते हैं, हर बार विफलता आने पर तदर्थ हड़बड़ी के बजाय: जब hardware समस्या का संदेह हुआ, training run को **रोका** गया; **diagnostic tests** की एक श्रृंखला चलाई गई ताकि पहचाना जा सके कि कौन-से ख़ास nodes ख़राब बर्ताव कर रहे हैं; diagnostics ने जिस भी node को चिह्नित किया उसे **अलग किया गया**, यानी उसे उन nodes के समूह से बाहर रखा गया जिन्हें run आगे इस्तेमाल करेगा; और training फिर **आख़िरी सहेजे checkpoint से resume हुई**, अब बाक़ी, स्वस्थ nodes पर चलते हुए। यह पैटर्न वही रहता है चाहे विफलता हाथ से पकड़ी गई हो या automatic restart शुरू हुआ हो: जाँचें, ख़राब hardware को बाहर रखें, सबसे हाल की सहेजी state से resume करें।

### Manual बनाम automatic restarts, और संचालन के लिहाज़ से फ़र्क़ क्यों मायने रखता है

Zhang et al. 35 से ज़्यादा **manual** restarts, जहाँ किसी व्यक्ति ने समस्या पहचानकर दख़ल दिया, को अनुमानित 70 से ज़्यादा **automatic** restarts से अलग करते हैं, जिनका अनुमान बदले गए hosts की संख्या और दर्ज किए गए manual restarts की छोटी संख्या के अंतर से लगाया गया है। Automatic restart का मतलब है ऐसा tooling जो विफलता पहचानता है और किसी व्यक्ति के नोटिस करने और कार्रवाई करने का इंतज़ार किए बिना training resume कर देता है, जो सीधे इस पर मायने रखता है कि विफलता असल में कितनी progress की क़ीमत लेती है: जो विफलता manual पहचान का इंतज़ार करती है वह उस समय को खोती है जो किसी व्यक्ति के दख़ल देने से पहले बीतता है, checkpoint-और-resume चक्र की अपनी क़ीमत के ऊपर, जबकि automatically पहचानी और resume की गई विफलता पाठ 18 में चर्चित checkpoint-अंतराल जितनी progress के क़रीब ही खोती है।

### Loss divergence: संबंधित पर अलग विफलता जिससे उबरना है

Zhang et al. बिल्कुल अलग कारण से restart करने का भी वर्णन करते हैं: loss divergence, hardware विफलता नहीं। जब training loss diverge हुआ, तो learning rate घटाकर और पुराने checkpoint से restart करके run उबर पाया और आगे चल पाया। उन्होंने नोट किया कि यह दो और signals से जुड़ता था: उनका dynamic loss scalar (mixed-precision setup का हिस्सा) शून्य पर गिर जाना, और final layer के activations के norm का उछल जाना। Divergence से ठीक पहले से restart करने के बजाय, उन्होंने ऐसे restart बिंदु चुने जहाँ loss scalar अब भी स्वस्थ स्थिति में था और activation norms अनियंत्रित रूप से बढ़ने के बजाय नीचे की ओर जा रहे थे, और अलग से पाया कि gradient clipping को 1.0 से घटाकर 0.3 करने से मदद मिली। यह किसी checkpoint के run को resume करने में इस्तेमाल होने का दूसरा, सचमुच अलग कारण है, node के मरने से अलग: hardware ठीक है, पर training प्रक्रिया को ख़ुद पीछे लौटकर अलग ढंग से आगे चलना है, जो सिर्फ़ checkpoints का रखा हुआ इतिहास (सिर्फ़ अकेला सबसे हाल का नहीं) संभव बनाता है।

## अभ्यास

1. ▢ OPT की node-failure प्रक्रिया के इन चार चरणों को उस क्रम में रखें जो Zhang et al. बताते हैं: (a) बाक़ी nodes पर training resume करना, (b) training run को रोकना, (c) ख़राब nodes पहचानने के लिए diagnostic tests चलाना, (d) चिह्नित nodes को अलग करना।

<details markdown="1"><summary>जाँचें</summary>

b, c, d, a: रोकें, जाँचें, diagnostics ने जो भी चिह्नित किया उसे अलग करें, फिर बाक़ी स्वस्थ nodes पर आख़िरी सहेजे checkpoint से resume करें।

</details>

2. ▢ Automatically पहचानी और resume की गई विफलता में आम तौर पर manually पहचानी गई विफलता से कम progress क्यों जाती है, भले दोनों आख़िर में एक ही checkpoint से resume हों?

<details markdown="1"><summary>जाँचें</summary>

Manual restart उस समय को खोता है जो किसी व्यक्ति के समस्या नोटिस करके दख़ल देने से पहले बीतता है, checkpoint-और-resume चक्र के ऊपर। Automatic restart उस पहचान की देरी को छोड़ देता है, इसलिए कुल क़ीमत सिर्फ़ checkpoint अंतराल जितनी progress के क़रीब रहती है।

</details>

3. ▢ एक team का training loss diverge हो जाता है, पर कोई hardware विफलता नहीं है: हर node स्वस्थ है। Zhang et al. के ब्योरे के अनुसार, क्या checkpoint यहाँ फिर भी काम का है, और अगर है, तो कैसे?

    - a) नहीं; checkpoints सिर्फ़ hardware विफलताओं में मदद करते हैं, loss divergence में नहीं
    - b) हाँ; पुराने checkpoint से restart करना, learning rate घटाने के साथ, ठीक वही तरीक़ा है जिससे Zhang et al. loss divergence से उबरे
    - c) हाँ, पर कभी सिर्फ़ अकेला सबसे हाल का checkpoint ही इस्तेमाल हो सकता है, चाहे divergence कब शुरू हुआ हो
    - d) नहीं; loss divergence के लिए model को शुरू से दोबारा train करना पड़ता है

<details markdown="1"><summary>संकेत</summary>

Zhang et al. ने ख़ास तौर पर restart बिंदु अपने loss scalar और activation norms की स्थिति के आधार पर चुने, सिर्फ़ उपलब्ध सबसे हाल के checkpoint को नहीं।

</details>

<details markdown="1"><summary>जाँचें</summary>

**b)** ठीक वही है जो Zhang et al. बताते हैं। (a) ग़लत है; वही checkpoint-और-resume तंत्र दोनों कारणों से उबार देता है। (c) ख़ास तौर पर इसलिए ग़लत है कि उन्होंने restart बिंदु इस आधार पर चुना कि loss scalar कब स्वस्थ था और activation norms कब नीचे जा रहे थे, जो अकेला सबसे हाल का checkpoint न भी हो, और यह एक से ज़्यादा हाल के checkpoints हाथ में रखने के पक्ष में तर्क है। (d) पेपर के अपने उस ब्योरे का खंडन करता है जिसमें पूरे restart के बिना उबरना बताया गया है।

</details>

4. ▢ Zhang et al. के बताए अनुसार loss divergence से उबरना सिर्फ़ अकेला सबसे हाल का checkpoint रखने के बजाय एक से ज़्यादा रखने के पक्ष में तर्क क्यों देता है?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि सबसे अच्छा restart बिंदु हमेशा सबसे हाल का checkpoint नहीं था; वह loss scalar की सेहत और activation norms के रुझान की दिशा के आधार पर चुना गया था, जो आख़िरी save से और पीछे हो सकता था। सिर्फ़ सबसे नया checkpoint रखने से पहले के, ज़्यादा स्थिर बिंदु पर लौटने का विकल्प ख़त्म हो जाता।

</details>

## असली दुनिया का अभ्यास

- [ ] खोजें कि आपकी पहुँच वाला कोई training framework या orchestration tool automatic विफलता पहचान और restart कहाँ देता है (health checks, node draining, या ऐसे शब्द आम हैं)। नोट करें कि वह इस पाठ के बताए रोकें-जाँचें-अलग करें-resume करें पैटर्न से मेल खाता है या नहीं।
- [ ] OPT पेपर (ऊपर linked) का "Loss Divergences" अनुच्छेद पढ़ें और एक वाक्य लिखें कि लेखकों ने loss curve के अलावा किस signal का इस्तेमाल यह आँकने में किया कि restart बिंदु से resume करना सुरक्षित है या नहीं।
- [ ] कल: पाठ 18 के असली दुनिया के अभ्यास में आपने जो checkpoint आवृत्ति चुनी थी, उसके लिए तय करें कि सिर्फ़ सबसे हाल का नहीं, कितने हाल के checkpoints आप हाथ में रखेंगे, और इस पाठ के loss-divergence recovery मामले को देखते हुए एक वाक्य लिखें कि क्यों।

## आगे बढ़ने के लिए

- [पेपर: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
- [संसाधन](../RESOURCES.md)

---

चरण 8 ने एक अकेले training run के भीतर विफलता से बचना कवर किया। चरण 9 एक ज़्यादा लंबे चलने वाले सवाल की ओर मुड़ता है: उस run की progress को पहली जगह पर देखते रहना, और यह जानना कि वह सही राह पर है भी या नहीं।

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
