---
title: "21. समय-समय पर Held-Out Evaluation"
description: "Training loss बताता है कि model अपने ही training data पर fit हो रहा है; बाक़ी के बारे में सिर्फ़ held-out जाँच कुछ बताती है"
type: lesson
---

# पाठ 21. समय-समय पर Held-Out Evaluation

**मिशन से संबंध:** "Training dashboard पढ़कर बता सकें कि run सही राह पर है या नहीं" "पूरी रूपरेखा" में इस चरण के "कब पूरा माना जाए" खाने में लिखा है। पाठ 20 ने training run के अपने भीतरी signals को देखना कवर किया; यह पाठ सहेजे checkpoints को उस चीज़ के विरुद्ध परखना कवर करता है जो training loss नहीं बता सकता, और उस माप को वहाँ सौंप देता है जहाँ वह पूरी तरह सिखाया जाता है।
**मुख्य स्रोत:** [पेपर: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**पूर्व-आवश्यकताएँ:** [पाठ 20](0020-reading-a-loss-curve.md), [Held-out data](../../evals/GLOSSARY.md)

## वार्म-अप

1. ▢ Loss scalar का शून्य की ओर गिरना, या activation norm का उछलना, अस्थिरता की चेतावनी training loss curve से पहले क्यों दे सकता है?

<details markdown="1"><summary>जाँचें</summary>

ये अंतर्निहित संख्यात्मक समस्या के विकसित होने के लक्षण हैं, जो उसके इतना बड़ा होने से पहले दिख सकते हैं कि loss curve को साफ़ तौर पर बिगाड़े; जब तक loss में ही spike साफ़ दिखता है, तब तक समस्या कुछ समय से बन रही हो सकती है।

</details>

2. ▢ Loss, gradient norm और स्थिरता signal को दिखाने वाला dashboard व्यवहार में तभी उपयोगी क्यों है जब उसकी निगरानी बार-बार हो?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि बड़े पैमाने पर विफलताएँ और अस्थिरताएँ बार-बार होने वाली, नियमित घटनाएँ हैं (चरण 8), इसलिए देर से पकड़ी गई समस्या उसी समस्या के जल्दी पकड़े जाने से कहीं ज़्यादा खोई progress की क़ीमत लेती है।

</details>

## यह जानें

### Training loss क्या नहीं बता सकता

Training loss नापता है कि model उन ख़ास batches पर कितना अच्छा fit हो रहा है जिन पर उसे अभी train किया जा रहा है। सहजता से घटता training loss स्वस्थ run के लिए ज़रूरी है, पर यह वही चीज़ नहीं है जो model का उन कामों में अच्छा होना है जो training loop से बाहर का कोई व्यक्ति उससे असल में पूछेगा, और यह बिल्कुल नहीं बताता कि वह सुधार उस text पर टिकेगा या नहीं जिस पर model कभी train नहीं हुआ। बिल्कुल स्वस्थ दिखने वाला training loss curve भी ऐसे model के ऊपर बैठा हो सकता है जो चुपचाप अपने ही training mixture की ख़ासियतों पर overfit हो रहा है।

### Gopher का अपना periodic evaluation कैसा दिखता था

Rae et al. ने इसे जाँचने के लिए training के ख़त्म होने तक इंतज़ार नहीं किया। वे चार language-modeling benchmarks (Wikitext103, LAMBADA, Curation Corpus और C4) पर training के दौरान समय-समय पर निकाले गए evaluation curves बताते हैं, जिन्हें उन्होंने पहले से साफ़ तौर पर training set से हटा दिया था, ठीक इसलिए कि उन पर अच्छा score इस बात से समझाया न जा सके कि model ने वही text training में बस देख लिया था। ऐसे benchmark को सिर्फ़ बिल्कुल अंत में एक बार के बजाय समय-समय पर जाँचना ही वह चीज़ है जो team को असल में समस्या पकड़ने देती है, data pipeline में bug, configuration बदलने से आई regression, क्षमता में अनपेक्षित divergence, जबकि run अभी चल रहा है और कुछ किया जा सकता है, न कि उसे तब खोजना जब पूरा compute budget पहले ही ख़र्च हो चुका हो।

### "Training set से हटाया गया" असली काम क्यों कर रहा है

Rae et al. जो वाक्यांश इस्तेमाल करते हैं, benchmarks "explicitly filtered from the training set", वही विचार है जिसके चारों ओर इस track की data pipeline सामग्री का पाठ 1 बना था, training के बजाय evaluation पर लागू: score तभी generalization के बारे में कुछ मायने रखता है जब model परखे जा रहे ठीक उसी text को रटकर सही उत्तर न दे सकता हो। यही **held-out data** का मतलब है, और यह इतना बड़ा विषय है, अपने contamination रास्तों, पहचान के तरीक़ों और डिज़ाइन तकनीकों के साथ, कि उसके चारों ओर पूरा track बना है।

### यह कहाँ सौंप दिया जाता है

`llm/evals` evaluation की पद्धति पूरी तरह सँभालता है: contamination का विरोध करने वाला held-out सेट कैसे बनाएँ, क्या किसी metric को भरोसेमंद बनाता है, और किसी संख्या को बचाव करने लायक़ फ़ैसले में कैसे बदलें। इस track का उस सामग्री पर एकमात्र दावा वही है जो इस पाठ में किया गया है: pretraining run को सिर्फ़ अंत में नहीं, सहेजे checkpoints पर held-out data के विरुद्ध समय-समय पर जाँच चाहिए। उसके आगे हर चीज़ के लिए, अगली चीज़ जो पढ़नी है वह [Held-Out Data और Contamination](../../evals/reference/held-out-data-and-contamination.md) शीट है, उसका यहाँ दोहराव नहीं।

## अभ्यास

1. ▢ किसी model का training loss पूरे run में सहजता से घटता रहा है। क्या यह, अपने-आप में, बताता है कि model उन tasks पर अच्छा प्रदर्शन करता है जिन्हें fit करने के लिए उसे सीधे train नहीं किया गया?

<details markdown="1"><summary>जाँचें</summary>

नहीं। Training loss model के अपने training batches पर fit को नापता है; सहजता से घटता training loss स्वस्थ run के लिए ज़रूरी है पर अपने-आप उस data या tasks पर प्रदर्शन के बारे में कुछ नहीं बताता जिन पर model train नहीं हुआ, और यही held-out evaluation का काम है।

</details>

2. ▢ Rae et al. ने Wikitext103, LAMBADA, Curation Corpus और C4 को समय-समय के evaluation benchmarks के रूप में इस्तेमाल करने से पहले Gopher के training set से साफ़ तौर पर क्यों हटाया?

<details markdown="1"><summary>जाँचें</summary>

ताकि उन benchmarks पर अच्छा score इस बात से समझाया न जा सके कि model ने वही text training में बस देखा और रट लिया था। जिस benchmark पर model train हुआ हो वह असली क्षमता और रटने में फ़र्क़ नहीं कर सकता, और यही held-out benchmark को ऐसा सार्थक सबूत बनाता है जैसा दूषित benchmark नहीं होता।

</details>

3. ▢ Training के दौरान समय-समय पर evaluate करना, सिर्फ़ अंत में एक बार के बजाय, team को असल में क्या देता है, यह देखते हुए कि पूरा training run कितना महँगा है?

    - a) अंत में एक बार के evaluation पर इसका कोई फ़ायदा नहीं; अंतिम नतीजा ही मायने रखता है
    - b) यह bug, regression, या क्षमता में divergence को run अभी चलते हुए पकड़ने और संभवतः संबोधित करने देता है, न कि पूरा compute budget ख़र्च हो जाने के बाद ही खोजने देता है
    - c) यह held-out data की ज़रूरत पूरी तरह ख़त्म कर देता है
    - d) यह सिर्फ़ बहुत छोटे training runs के लिए मायने रखता है

<details markdown="1"><summary>जाँचें</summary>

**b)** यही सीधा व्यावहारिक फ़ायदा है: समस्या को जल्दी पकड़ना, जब उसका जवाब देने के लिए compute budget बचा है, न कि run पूरा होने के बाद ही पता चलना। (a) इसे पूरी तरह अनदेखा करता है। (c) संबंध को उलट देता है; समय-समय के evaluation को भी कोई मतलब रखने के लिए held-out होना ही चाहिए। (d) उलटा है, क्योंकि ज़्यादा लंबे, महँगे run को देर से पकड़ी गई समस्या में खोने को ज़्यादा है।

</details>

## असली दुनिया का अभ्यास

- [ ] खोजें कि आपकी पहुँच वाला कोई training framework या experiment-tracking setup training के दौरान समय-समय पर evaluation कैसे schedule करता है (steps या tokens में नापा गया evaluation अंतराल आम है), और नोट करें कि वह default रूप से कौन-से benchmarks या metrics evaluate करता है।
- [ ] `llm/evals` की [Held-Out Data और Contamination](../../evals/reference/held-out-data-and-contamination.md) शीट पढ़ें और पहचानें कि उसके दो contamination रास्तों (pretraining में समा जाना, या बार-बार का overfitting) में से कौन-सा वह है जिससे Gopher की "explicitly filtered from the training set" वाली भाषा बचाव कर रही है।
- [ ] कल: अपने चुने किसी काल्पनिक pretraining run के लिए, evaluation अंतराल तय करें (आप कितनी बार, tokens या steps में, held-out प्रदर्शन जाँचेंगे) और एक benchmark या held-out सेट का नाम बताएँ जिसके विरुद्ध आप उसे जाँचेंगे, और क्यों।

## आगे बढ़ने के लिए

- [पेपर: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [Held-Out Data और Contamination](../../evals/reference/held-out-data-and-contamination.md)
- [संसाधन](../RESOURCES.md)

---

चरण 9 ने run को होते समय देखना कवर किया, उसके अपने भीतरी हिस्से भी और उसके checkpoints को किसी बाहरी चीज़ के विरुद्ध भी। चरण 10 इस रूपरेखा को पूरा करता है: यह तय करना कि ऐसा run चलाना भी है या नहीं, और उस फ़ैसले का बचाव किसी और के सामने करना।

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
