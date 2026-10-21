---
title: "4. Reward Model को Train करना: Bradley-Terry Loss"
description: "Reward model training में कभी कोई निरपेक्ष score नहीं देखता, सिर्फ़ यह कि दो completions में से इंसान को कौन-सी ज़्यादा पसंद आई"
type: lesson
---

# पाठ 4. Reward Model को Train करना: Bradley-Terry Loss

**मिशन से संबंध:** "Bradley-Terry loss से preference pairs पर reward model train करें, और उसके विरुद्ध train हुई policy की reward-hacked completion पहचानें" "सफलता कैसी दिखती है" का दूसरा बिंदु है। यह पाठ reward model को train करना सिखाता है; policy को उसके विरुद्ध optimize करने के बाद क्या ग़लत हो सकता है, यह पाठ 5 में है।
**मुख्य स्रोत:** [पेपर: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**पूर्व-आवश्यकताएँ:** [पाठ 3](0003-loss-masking-on-non-assistant-tokens.md)

## वार्म-अप

1. ▢ SFT training के दौरान non-assistant tokens पर loss masking यांत्रिक रूप से असल में क्या करती है?

<details markdown="1"><summary>जाँचें</summary>

वह हर prompt या non-assistant token की position को ऐसा label देती है जिसे loss function को अनदेखा करने को कहा गया है, ताकि सिर्फ़ assistant (उत्तर) की positions gradient दें, भले ही prompt tokens अब भी input के रूप में मौजूद रहते हैं जिन पर model अपना उत्तर टिकाता है।

</details>

2. ▢ अगर यह masking छोड़ दी जाए तो SFT training में क्या टूटता है?

<details markdown="1"><summary>जाँचें</summary>

Gradient signal prompt के अपने tokens का अनुमान लगाना सीखने में ख़र्च या पतला हो जाता है, जो वह हुनर नहीं है जो SFT सिखाना चाहता है, बजाय इसके कि वह पूरी तरह उन उत्तर-tokens पर केंद्रित रहे जिन्हें model को असल में बनाना सीखना चाहिए।

</details>

## यह जानें

### Preference data इकट्ठा करना

Reward model को ऐसा data चाहिए जो बताए कि model के दो outputs में से कौन-सा बेहतर है, न कि यह कि सबसे अच्छा output शब्द-दर-शब्द क्या होना चाहिए था। Ouyang et al. यह इस तरह इकट्ठा करते हैं कि labelers के सामने एक ही prompt के कई outputs (वे 4 से 9 के बीच इस्तेमाल करते हैं) रखे जाते हैं और उनसे पूरे सेट को rank करवाया जाता है, हर बार सिर्फ़ दो की तुलना करवाने के बजाय। `K` outputs की ranking उस ranking के भीतर की हर pairwise तुलना पैदा करती है, यानी `K` choose 2 तुलनाएँ, इसलिए एक ranking task एक साथ कई training pairs देता है।

### Reward model कहाँ से आता है

Reward model कोरी स्लेट से train नहीं होता। Ouyang et al. बताते हैं कि वे SFT model से ही शुरू करते हैं, जिसकी अंतिम unembedding layer, यानी वह हिस्सा जो hidden state को next-token probabilities में बदलता है, हटाकर उसकी जगह ऐसी layer लगाई जाती है जो एक अकेला scalar देती है। Reward model वह सब दोबारा इस्तेमाल करता है जो SFT model पहले ही भाषा और लक्षित व्यवहार के बारे में सीख चुका है, और उसे इस काम में लगाता है कि किसी दिए prompt और completion के लिए अगले token के distribution के बजाय एक संख्या, यानी score, दे।

### Bradley-Terry loss

एक ही prompt `x` के लिए पसंद की गई completion `y_w` ("winner") और नकारी गई completion `y_l` ("loser") दी हो, और हर एक के लिए reward model के scalar outputs `r(x, y_w)` और `r(x, y_l)` हों, तो Ouyang et al. reward model को इस loss से train करते हैं:

```text
loss(θ) = -E[log(σ(r_θ(x, y_w) - r_θ(x, y_l)))]
```

जहाँ `σ` logistic sigmoid function है। यही **Bradley-Terry loss** है: यह इस संभावना को कि इंसान `y_l` के बजाय `y_w` पसंद करेगा, उनके दोनों scores के अंतर का sigmoid मानता है, और reward model को इस तरह train करता है कि उसकी अनुमानित संभावना वह हो जो labeler ने असल में चुना। इस loss को नीचे लाने का मतलब है `r(x, y_w) - r(x, y_l)` को ऊपर ले जाना: model को इस तरह train किया जाता है कि पसंद की गई completion का score नकारी गई completion से ऊँचा हो, एक ऐसे अंतर से जो इस बात के अनुपात में है कि sigmoid को उसके पक्ष में कितने भरोसे से झुकना है।

### Reward का निरपेक्ष पैमाना अपने-आप में मायने क्यों नहीं रखता

ध्यान दें कि loss सिर्फ़ दोनों scores के *अंतर* पर निर्भर करता है, किसी एक score पर कभी नहीं। Model जो भी reward दे, उन सबमें वही स्थिरांक जोड़ देने पर हर अंतर, और इसलिए पूरा loss, बिल्कुल नहीं बदलता। यानी training में कुछ भी reward model के scores को किसी ख़ास निरपेक्ष पैमाने पर नहीं बाँधता; सिर्फ़ पसंद की गई और नकारी गई completions के बीच का सापेक्ष क्रम (और अंतरों का आकार) ही कभी बाँधा जाता है। Ouyang et al. इसे सीधे सँभालते हैं: चूँकि loss shift से अप्रभावित रहता है, वे reinforcement learning में इस्तेमाल से पहले reward model को bias से normalize करते हैं ताकि labeler demonstrations का औसत score 0 रहे, और इस तरह वरना-मनमाने पैमाने को नापने के लिए एक पक्का लंगर मिल जाता है।

### एक ranking की तुलनाएँ साथ क्यों रखी जाती हैं

एक ही ranking task की `K` choose 2 तुलनाओं में से हर एक को स्वतंत्र, अलग-अलग shuffle किया गया training example मानने से एक ख़ास समस्या पैदा होती है: चूँकि completions का वही छोटा सेट उन कई तुलनाओं में बार-बार आता है, इस तरह बने data पर एक pass overfit करने की ओर जाता है, हर completion असल में `K - 1` आपस में जुड़ी तुलनाओं में दोबारा इस्तेमाल हो जाती है। Ouyang et al. का इलाज यह है कि एक ranking task की सारी तुलनाओं को training के दौरान एक ही batch element माना जाए, उन्हें स्वतंत्र रूप से बड़े dataset में shuffle करने के बजाय, जिससे उन्होंने पाया कि हर pairwise तुलना को पूरी तरह स्वतंत्र मानने की तुलना में validation accuracy और loss बेहतर हुए।

## अभ्यास

1. ▢ एक reward model एक pair के लिए `r(x, y_w) = 2.0` और `r(x, y_l) = 1.0` देता है, और दूसरे prompt के दूसरे pair के लिए `r(x, y_w) = 12.0` और `r(x, y_l) = 11.0`। क्या Bradley-Terry loss इन दोनों pairs को अलग तरह से देखता है?

<details markdown="1"><summary>संकेत</summary>

Loss `r(x, y_w) - r(x, y_l)` का फलन है, किसी एक मान का अपने-आप में नहीं।

</details>

<details markdown="1"><summary>जाँचें</summary>

नहीं। दोनों pairs का अंतर एक ही है, `1.0`, और loss सिर्फ़ उसी अंतर पर निर्भर करता है, निरपेक्ष scores पर नहीं। इसी वजह से बाहरी लंगर के बिना reward model का निरपेक्ष पैमाना मायने नहीं रखता।

</details>

2. ▢ Ouyang et al. के अनुसार reward model के शुरुआती weights असल में कहाँ से आते हैं?

<details markdown="1"><summary>जाँचें</summary>

SFT model से, जिसकी अंतिम unembedding layer हटाकर उसकी जगह ऐसी layer लगाई जाती है जो एक अकेला scalar देती है, न कि किसी नए, random रूप से initialize किए model से।

</details>

3. ▢ एक labeler एक prompt की 4 completions (`K = 4`) को rank करता है। यह एक ranking task training के लिए कितनी pairwise तुलनाएँ पैदा करता है?

<details markdown="1"><summary>जाँचें</summary>

6 (`4` choose `2`, जो `(4 × 3) / 2 = 6` है)।

</details>

4. ▢ Ouyang et al. एक ranking task की सारी तुलनाओं को एक batch element के रूप में साथ क्यों रखते हैं, हर pairwise तुलना को स्वतंत्र रूप से training set में shuffle करने के बजाय?

    - a) इससे reward model तेज़ी से train होता है और accuracy पर कोई असर नहीं पड़ता
    - b) उन्हें स्वतंत्र रूप से shuffle करने से overfitting होती है, क्योंकि एक ranking task की कई आपस में जुड़ी तुलनाओं में completions का वही छोटा सेट दोबारा इस्तेमाल होता है
    - c) Bradley-Terry loss तब तक निकाला ही नहीं जा सकता जब तक तुलनाएँ इस तरह group न हों
    - d) यह इसलिए ज़रूरी है कि reward model के scores एक तय संख्यात्मक सीमा में आएँ

<details markdown="1"><summary>जाँचें</summary>

**b)** वह कारण है जो Ouyang et al. सीधे देते हैं: एक ranking task की तुलनाओं में आपस में जुड़ी, दोबारा इस्तेमाल होने वाली completions, स्वतंत्र shuffle करने पर एक pass को overfit करा देती हैं। (a), (c) और (d) असली समस्या या उसके इलाज का वर्णन नहीं करते।

</details>

## असली दुनिया का अभ्यास

- [ ] कोई public preference dataset खोजें (कई reward models train करने के लिए छपे हैं) और जाँचें कि हर prompt की कितनी completions rank की गई हैं, और जारी किया गया format पहले से pairwise तुलनाएँ दिखाता है या पूरी ranking।
- [ ] हाथ से Bradley-Terry loss का sigmoid वाला हिस्सा निकालें, reward अंतर `0` (कोई preference signal ही नहीं) के लिए और किसी बड़े धनात्मक अंतर के लिए, और एक वाक्य में बताएँ कि loss हर छोर पर कैसा बर्ताव करता है।
- [ ] कल: आगे देखे बिना पाठ 5 के लिए एक वाक्य की भविष्यवाणी लिखें: अगर reward model को सिर्फ़ वही completions rank करना सिखाया गया है जो इंसानों ने उसे सचमुच दिखाई हैं, तो जब policy कोई भी completion generate करने के लिए आज़ाद हो, जो सबसे ऊँचा score दे उसे खोजते हुए, तब क्या ग़लत हो सकता है?

## आगे बढ़ने के लिए

- [पेपर: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
