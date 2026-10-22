---
title: "8. Embedding और Output Layers, Weight Tying"
description: "Tokens transformer के vector space में कैसे आते-जाते हैं, और यह करने वाली दो layers एक ही matrix क्यों साझा कर सकती हैं"
type: lesson
---

# पाठ 8. Embedding और Output Layers, Weight Tying

**मिशन से संबंध:** यह चरण 3 का समापन है: stack किए blocks (पाठ 7) पूरी तरह `d_model`-आयाम वाले vectors में काम करते हैं, इसलिए किसी को आते समय अलग-अलग tokens को उस space में बदलना होगा, और जाते समय वापस vocabulary scores में, और इसी से कच्चे token IDs से पूरे forward pass तक का चक्र पूरा होता है।
**मुख्य स्रोत:** [पेपर: "Using the Output Embedding to Improve Language Models", Press and Wolf, 2017](https://arxiv.org/abs/1608.05859)
**पूर्व-आवश्यकताएँ:** [पाठ 7](0007-stacking-blocks.md), [Scaled dot-product attention](../GLOSSARY.md)

## वार्म-अप

1. ▢ हर transformer block को एक ही input और output आयाम (`d_model` अंदर, `d_model` बाहर) क्यों बनाए रखना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

Stacking का मतलब है कि एक block का output सीधे अगले block के input में जाता है; अगर कोई block आयाम बदल दे, तो उसके बाद का हर block और residual stream अलग आकार के लिए बनाना पड़ता, और वह एकसमान stacking टूट जाती जो एक ही block shape को कितनी भी बार दोहराने देती है।

</details>

2. ▢ क्या मानक transformer stack के एक block की weights दूसरे block की weights जैसी ही होती हैं? इसकी क्या क़ीमत है, और यह क्या देता है?

<details markdown="1"><summary>जाँचें</summary>

नहीं, हर block के अपने स्वतंत्र रूप से सीखे हुए parameters होते हैं। इसकी क़ीमत गहराई के साथ लगभग linearly parameter count है, क्योंकि कुछ भी साझा नहीं होता, पर यह अलग-अलग blocks को अलग-अलग गहराई पर अलग तरह से विशेषज्ञ बनने देता है, बजाय इसके कि सब ठीक एक ही रूपांतरण compute करें।

</details>

## यह जानें

### Input embedding: token ID से vector की लुकअप

Tokenizer (यहाँ बस नाम भर लिया गया है; इसे आगे निकालना `llm/finetuning` का इलाक़ा है) पूर्णांक token IDs की एक sequence बनाता है, हर एक तय vocabulary में एक index। **Input embedding layer** आकार `vocab_size × d_model` का एक सीखा हुआ matrix है: पंक्ति `i` token `i` का घना vector रूप है। किसी token का embedding ढूँढना बस उसकी पंक्ति पढ़ना है। यहीं अलग-अलग, प्रतीकात्मक tokens उस सतत vector space में दाख़िल होते हैं जिस पर आगे का हर हिस्सा, attention, feed-forward block, positional encoding, असल में काम करता है।

### Output layer: वापस vocabulary scores में project करना

अंतिम stack हुआ block अपना output बना दे, जो अब भी हर position के लिए `d_model`-आयाम का है, तो model को उस vector को वापस vocabulary पर एक prediction में बदलने के लिए एक और चरण चाहिए। **Output layer** आकार `d_model × vocab_size` का एक linear projection है, जो हर position पर हर vocabulary token के लिए एक कच्चा score बनाता है, जिसे **logit** कहते हैं। वे logits (जिन्हें अगले पाठ का cross-entropy loss probability distribution में बदलता है) ही "अगला token predict करो" का संख्यात्मक अर्थ हैं: vocabulary के आकार के scores का एक vector, हर संभव token के लिए एक।

### दोनों layers के shapes एक-दूसरे के transpose हैं

Input embedding matrix `vocab_size × d_model` है; output projection `d_model × vocab_size` है, ठीक transpose का आकार। **Weight tying** इसका सीधा फ़ायदा उठाता है: एक बिल्कुल अलग output matrix सीखने के बजाय, model वही embedding matrix, transpose करके, output logits compute करने में दोबारा इस्तेमाल करता है (`logits = h @ W_embedding^T`)। यह सुविधा के लिए भुनाया गया कोई संयोग भर नहीं है; दोनों layers किसी token को असल में एक ही बुनियादी सवाल से जोड़ती हैं: input embedding जवाब देती है "token X को कौन-सा vector दर्शाता है", और output layer जवाब देती है "token X की कितनी संभावना है", और tying इन दोनों को दो अलग, असंबंधित representations सीखने के बजाय एक ही representation साझा करने वाला मानता है।

![दो अगल-बगल बने diagrams। बाईं ओर, एक token id embedding matrix में अपनी पंक्ति ढूँढता है, जिसका आकार vocab_size गुणा d_model है, और embedding vector बनता है। दाईं ओर, एक hidden vector उसी matrix से project होता है, जो transpose होकर d_model गुणा vocab_size है, और logits का vector बनता है, हर vocabulary token के लिए एक score। एक टूटी रेखा दोनों matrices को जोड़ती है, जिस पर लिखा है वही weight matrix, transpose किया हुआ, यह दिखाते हुए कि weight tying दो अलग matrices सीखने के बजाय एक ही सीखे हुए matrix को input lookup और output projection, दोनों के लिए दोबारा इस्तेमाल करता है।](images/weight-tying-embedding-output.svg)

### Tying असल में क्या बचाता है

50,000 tokens की vocabulary और `d_model = 768` के लिए, अकेली embedding table में `50,000 × 768 = 38,400,000` parameters होते हैं। बिना tying वाले model को output projection के लिए उसी आकार का दूसरा matrix चाहिए होता, 38.4 million और parameters जो मिलता-जुलता काम कर रहे हैं। Tying वह पूरा दूसरा matrix हटा देता है, और hidden आकार के मुक़ाबले बड़ी vocabulary वाले models के लिए, यह model के कुल parameter count का काफ़ी बड़ा हिस्सा है जो गुणवत्ता में लगभग बिना किसी नुक़सान के, और अक्सर नापने लायक़ फ़ायदे के साथ, बच जाता है।

## अभ्यास

1. ▢ Input embedding layer के weight matrix का shape क्या है, और किसी ख़ास token का embedding ढूँढना संरचनात्मक रूप से किसके बराबर है?

<details markdown="1"><summary>जाँचें</summary>

`vocab_size × d_model`। किसी token का embedding ढूँढना उस token के index पर matrix की पंक्ति पढ़ना है, यानी सीधी लुकअप, कोई computed रूपांतरण नहीं।

</details>

2. ▢ Output layer का shape input embedding layer के shape से कैसे जुड़ा है, और यह संबंध क्या संभव बनाता है?

<details markdown="1"><summary>जाँचें</summary>

Output layer का shape (`d_model × vocab_size`) input embedding के shape (`vocab_size × d_model`) का transpose है। यही संबंध weight tying को संभव बनाता है: वही matrix, एक तरह से लुकअप table की तरह और दूसरी तरह से (transpose करके) projection की तरह इस्तेमाल होकर, दोनों भूमिकाएँ निभा सकता है, दो अलग से सीखे matrices की ज़रूरत के बिना।

</details>

3. ▢ 50,000 tokens की vocabulary और `d_model = 768` के लिए embedding table का parameter count निकालें, और समझाएँ कि weight tying बिना tying वाले model की तुलना में क्या बचाता है।

<details markdown="1"><summary>संकेत</summary>

Embedding table का parameter count `vocab_size × d_model` है। बिना tying वाली output layer को उसी आकार का matrix चाहिए होता।

</details>

<details markdown="1"><summary>जाँचें</summary>

Embedding table के लिए `50,000 × 768 = 38,400,000` parameters। बिना tying वाले model को output projection के लिए उसी आकार का दूसरा, अलग से सीखा हुआ matrix चाहिए होता; tying वह पूरा दूसरा matrix हटा देता है, और इस vocabulary और hidden आकार के लिए लगभग 38.4 million parameters बचाता है।

</details>

4. ▢ Parameters बचाने के अलावा, input और output weight matrices को tie करना सिर्फ़ एक सुविधाजनक तरकीब होने के बजाय समझदारी की बात क्यों है, इसका बुनियादी तर्क क्या है?

<details markdown="1"><summary>जाँचें</summary>

दोनों layers किसी token को बुनियादी रूप से एक ही representation से जोड़ती हैं: input embedding जवाब देती है "इस token को कौन-सा vector दर्शाता है", और output layer जवाब देती है "मौजूदा representation को देखते हुए इस token की कितनी संभावना है"। चूँकि दोनों सवाल एक ही token-से-vector संबंध के बारे में हैं, इनके बीच एक सीखा हुआ representation साझा करना एक उचित inductive bias है, सिर्फ़ parameters घटाने का तरीक़ा नहीं।

</details>

5. ▢ Input embedding और output layers के बारे में कौन-सा दावा सही है?

    - a) उन्हें हमेशा दो बिल्कुल अलग matrices के रूप में सीखा जाना चाहिए, क्योंकि उनके मक़सद असंबंधित हैं
    - b) उनके shapes एक-दूसरे के transpose हैं, और यही weight tying, यानी दोनों के लिए एक ही matrix दोबारा इस्तेमाल करना, संभव बनाता है
    - c) Weight tying सिर्फ़ parameters बचाता है और कोई और फ़ायदा नहीं देता
    - d) Output layer का shape अकेले `vocab_size` पर निर्भर करता है, `d_model` से उसका कोई संबंध नहीं है

<details markdown="1"><summary>जाँचें</summary>

**b)** transpose वाला shape-संबंध ही वह चीज़ है जिसका tying फ़ायदा उठाता है। (a) ग़लत है: tying ठीक इसी से बचाता है। (c) ग़लत है: माना जाता है कि tying गुणवत्ता में भी मदद करता है, क्योंकि दोनों layers एक ही बुनियादी token representation से जुड़ी हैं। (d) ग़लत है: output layer का shape `d_model × vocab_size` है, यानी दोनों पर निर्भर।

</details>

## असली दुनिया का अभ्यास

- [ ] Input embedding लुकअप और output projection को पहले अलग-अलग matrices के रूप में लागू करें, फिर अपने implementation को बदलकर उन्हें tie करें और पक्का करें कि output logits का shape नहीं बदला।
- [ ] किसी ऐसे model के लिए जिससे आप परिचित हैं, उसकी vocabulary size और `d_model` ढूँढें, और निकालें कि बिना tying वाले संस्करण की तुलना में weight tying कितने parameters बचाएगा।
- [ ] कल: जाँचें कि आपके पास उपलब्ध किसी असली model implementation (`transformers` library में या कहीं और) में embedding और output weights tied हैं या नहीं, और ढूँढें कि code में वह कहाँ configure होता है।

## आगे बढ़ने के लिए

- [पेपर: "Using the Output Embedding to Improve Language Models", Press and Wolf, 2017](https://arxiv.org/abs/1608.05859)
- [पेपर: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
