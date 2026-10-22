---
title: "4. Positional Encoding"
description: "Attention अपने-आप में क्रम के प्रति अंधा क्यों है, और sinusoidal encoding हर position को पहचानी जा सकने वाली छाप कैसे देता है"
type: lesson
---

# पाठ 4. Positional Encoding

**मिशन से संबंध:** चरण 2 attention (पाठ 1 से 3) के आसपास के उन हिस्सों को खोलता है जो उसे पूरा transformer block बनाते हैं; positional encoding उनमें पहला है, और उसके बिना attention उस एक चीज़ के प्रति अंधा होता जिस पर भाषा सबसे ज़्यादा निर्भर है: क्रम।
**मुख्य स्रोत:** [पेपर: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
**पूर्व-आवश्यकताएँ:** [पाठ 3](0003-causal-masking.md), [Scaled dot-product attention](../GLOSSARY.md)

## वार्म-अप

1. ▢ Causal mask कच्चे scores पर softmax से पहले क्यों लगता है, softmax चल चुकने के बाद weights को शून्य करने के बजाय?

<details markdown="1"><summary>जाँचें</summary>

Softmax के weights एक साथ compute होते हैं और उनका योग पहले से 1 होता है; बाद में किसी एक को शून्य करने पर बाक़ी का योग 1 नहीं रहता। Softmax से पहले mask लगाने पर बचे हुए, बिना mask वाले weights उसी computation के हिस्से के रूप में अपने-आप दोबारा normalize हो जाते हैं।

</details>

2. ▢ Scaled dot-product attention का समीकरण याददाश्त से लिखें।

<details markdown="1"><summary>जाँचें</summary>

`Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V`।

</details>

## यह जानें

### Attention में क्रम की कोई समझ अंतर्निहित नहीं है

Scaled dot-product attention अपना output queries और keys के बीच के dot products और values के भारित योगों से compute करता है, और उस computation में कहीं यह उल्लेख नहीं कि कोई token sequence में कहाँ बैठा है। दो input tokens की positions बदल दें (और उनसे आई `Q`, `K` और `V` की संबंधित पंक्तियाँ भी), तो बाक़ी हर position का attention output वही रहता है, बस अदला-बदली के हिसाब से दोबारा नाम दिया हुआ: computation जो असली content-आधारित संबंध और weights बनाता है वे बिल्कुल नहीं बदलते। Attention अपने input को vectors का अक्रमित सेट मानता है, sequence नहीं, जबकि भाषा साफ़ तौर पर क्रम-निरपेक्ष नहीं है: "dog bites man" और "man bites dog" में हर शब्द वही है और मतलब बिल्कुल अलग।

### Position को vectors के भीतर ही पिरोना पड़ता है

Attention का समीकरण सिर्फ़ `Q`, `K` और `V` देखता है; "और वैसे, इनमें से हर एक किस position से आया है" बताने के लिए कोई अलग रास्ता नहीं है। Attention position के प्रति संवेदनशील तभी बन सकता है जब position पहले से उन्हीं vectors के भीतर encode हो जिनसे `Q`, `K` और `V` बनते हैं, यानी token embeddings के भीतर, उनके attention computation तक पहुँचने से पहले। हर token के embedding में जोड़ा गया **positional encoding** vector एक ही शब्द की दो अलग positions को संख्यात्मक रूप से अलग पहचाने जा सकने वाले embeddings देता है, और इसी से attention के dot products अप्रत्यक्ष रूप से position के प्रति संवेदनशील हो जाते हैं।

### Sinusoidal encoding: हर position के लिए अनूठी, संरचित छाप

मूल पेपर का चुनाव हर position का encoding अलग-अलग frequencies वाले sine और cosine functions से बनाता है, हर frequency के लिए आयामों की एक जोड़ी:

```text
PE(pos, 2i)   = sin(pos / 10000^(2i / d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i / d_model))
```

कम index वाली आयाम जोड़ियाँ (छोटा `i`) positions के आर-पार धीरे-धीरे दोलन करती हैं (लंबी तरंग-दैर्ध्य); ज़्यादा index वाली जोड़ियाँ तेज़ी से दोलन करती हैं (छोटी तरंग-दैर्ध्य)। हर position को इन सभी frequencies में एक अनूठा संयोजन मिलता है, और अहम बात यह कि दो positions के बीच का तय अंतर उनमें से किसी एक के encoding के linear function के रूप में व्यक्त हो सकता है (क्योंकि जोड़ के `sin` और `cos` हिस्सों के `sin` और `cos` के linear संयोजनों में टूट जाते हैं)। यह संरचना इस बात का हिस्सा है कि पेपर क्यों तर्क देता है कि यह योजना सापेक्ष position तक, और संभवतः training में न देखी गई sequence lengths तक, सामान्यीकृत हो सकती है, सिर्फ़ absolute positions का एक तय सेट रटने के बजाय।

![Position के साथ क्षैतिज अक्ष पर बनी दो तरंगें। ऊपर वाली तरंग, कम index वाली आयाम जोड़ी से, दिखाई गई positions की पूरी सीमा में एक धीमा दोलन पूरा करती है। नीचे वाली तरंग, ज़्यादा index वाली आयाम जोड़ी से, उसी सीमा में आठ तेज़ दोलन पूरे करती है। हर position को इन सभी अलग-अलग frequency वाली तरंगों के मानों का अनूठा संयोजन मिलता है, और इसी से हर position को पहचानी जा सकने वाली छाप मिलती है।](images/sinusoidal-frequency-pairs.svg)

### सरल विकल्प: सीखा हुआ position embedding

तय सूत्र की जगह, position को एक सामान्य सीखी हुई embedding table से encode किया जा सकता है, जिसे position से उसी तरह index किया जाता है जैसे token embedding table को vocabulary से, और जिसे किसी भी दूसरे parameter की तरह gradient descent से train किया जाता है। इसे लागू करना सरल है और frequency पर सोचना नहीं पड़ता, पर training के दौरान table जितनी बड़ी बनाई गई थी उससे आगे की position के लिए इसके पास भरोसा करने को कोई सूत्र नहीं है: जिस position को model ने कभी देखा नहीं उसकी table में कोई पंक्ति नहीं है, जबकि sinusoidal encoding का सूत्र किसी भी position पर evaluate हो सकता है।

## अभ्यास

1. ▢ दो input tokens की position अदला-बदली कर दी गई (और `Q`, `K`, `V` में उनकी संबंधित पंक्तियाँ भी साथ बदली गईं)। तीसरी position के attention output का क्या होता है जो उन दोनों को query करती है?

<details markdown="1"><summary>जाँचें</summary>

असली content-आधारित weights या computed output के बारे में कुछ नहीं बदलता; नतीजा बस इस हिसाब से दोबारा नामित हो जाता है कि अदला-बदली वाले tokens अब किस भौतिक position पर हैं। यह attention की permutation invariance दिखाता है: वह content (dot products) के आधार पर संबंध compute करता है, position का कोई उल्लेख किए बिना।

</details>

2. ▢ Position को token embeddings के भीतर ही क्यों encode करना पड़ता है, `Q`, `K` और `V` के साथ कोई अलग signal बनाकर attention computation को देने के बजाय?

<details markdown="1"><summary>जाँचें</summary>

Attention का समीकरण सिर्फ़ `Q`, `K` और `V` पर काम करता है; position की जानकारी के दाख़िल होने के लिए कोई अतिरिक्त input नहीं है। Computation position के प्रति संवेदनशील तभी बन सकता है जब position attention चलने से पहले ही उन vectors में पिरोई जा चुकी हो जिनसे `Q`, `K` और `V` बनते हैं।

</details>

3. ▢ Sinusoidal positional encoding की आयाम जोड़ियों में frequency की संरचना बताएँ, और यह कच्चे position integer को सीधे इस्तेमाल करने की तुलना में क्या देती है।

<details markdown="1"><summary>संकेत</summary>

सोचें कि आयाम जोड़ियों में frequency बदलने से वह क्या मिलता है जो एक अकेली कच्ची संख्या नहीं दे सकती थी।

</details>

<details markdown="1"><summary>जाँचें</summary>

अलग-अलग आयाम जोड़ियाँ अलग-अलग frequencies पर दोलन करती हैं, positions के आर-पार धीमी (कम index) से तेज़ (ज़्यादा index) तक, जिससे हर position को एक कच्ची scalar की जगह सभी frequencies में मानों का अनूठा संयोजन मिलता है। यही संरचित, बहु-frequency encoding एक तय positional अंतर को दूसरी position के encoding के linear function के रूप में व्यक्त करने देती है, यानी वह गुण जो एक अकेले कच्चे integer में ऐसे रूप में नहीं होता जिसे attention के linear ऑपरेशन उतनी सीधे तौर पर इस्तेमाल कर सकें।

</details>

4. ▢ Sinusoidal positional encoding को training में देखी गई किसी भी लंबाई से ज़्यादा लंबी sequence के लिए evaluate क्यों किया जा सकता है, जबकि सीखी हुई position embedding table के लिए नहीं?

<details markdown="1"><summary>जाँचें</summary>

Sinusoidal encoding एक सूत्र है, जिसे किसी भी position मान पर evaluate किया जा सकता है, उन पर भी जो training में कभी नहीं आए। सीखी हुई embedding table में सिर्फ़ उन्हीं positions की पंक्तियाँ होती हैं जिनके लिए उसे बनाया और train किया गया था; उस सीमा से आगे की position के लिए ढूँढने को कोई संबंधित पंक्ति नहीं है।

</details>

5. ▢ Positional encoding क्यों मौजूद है, इसके बारे में कौन-सा दावा सही है?

    - a) Attention के dot products बिना किसी अतिरिक्त input के सापेक्ष position को पहले से हिसाब में ले लेते हैं
    - b) Attention अपने input को अक्रमित सेट मानता है, इसलिए model के शब्द-क्रम के प्रति संवेदनशील होने के लिए position को embeddings में डालना पड़ता है
    - c) Positional encoding की ज़रूरत सिर्फ़ बहुत लंबी sequences के लिए है, छोटी के लिए नहीं
    - d) सीखा हुआ position embedding, sinusoidal encoding की तुलना में न देखी गई sequence lengths पर बेहतर सामान्यीकृत होता है

<details markdown="1"><summary>जाँचें</summary>

**b)** positional encoding के होने का पूरा कारण यही है। (a) ग़लत है: attention का समीकरण अपने-आप में position का कोई उल्लेख नहीं करता। (c) ग़लत है: छोटी sequence का भी अर्थ शब्द-क्रम पर निर्भर करता है, इसलिए वही अंधापन लंबाई से परे लागू होता है। (d) ग़लत है: उलटा सही है, sinusoidal encoding का सूत्र किसी भी position पर evaluate हो सकता है, जबकि सीखी हुई table उसी तक सीमित है जिस पर वह train हुई थी।

</details>

## असली दुनिया का अभ्यास

- [ ] एक छोटे `d_model` के लिए सूत्र से sinusoidal positional encoding लागू करें, और कुछ positions के encoding vectors को plot या print करके आयाम जोड़ियों में अलग-अलग दोलन frequencies देखें।
- [ ] अपना positional encoding token embeddings के एक सेट में जोड़ें और पक्का करें कि एक ही token दो अलग positions पर अब संख्यात्मक रूप से अलग vectors बनाता है।
- [ ] कल: मुख्य स्रोत पेपर का "Positional Encoding" खंड पूरा पढ़ें, और लंबी sequences पर सामान्यीकरण वाले दावे को इस बात से मिलाकर जाँचें कि आपका अपना implementation अपनी training सीमा से आगे असल में क्या बनाएगा।

## आगे बढ़ने के लिए

- [पेपर: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [लेख: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
