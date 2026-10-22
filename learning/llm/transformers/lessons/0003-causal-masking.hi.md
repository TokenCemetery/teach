---
title: "3. Causal Masking"
description: "कोई query position भविष्य की positions पर attend क्यों नहीं कर सकती, और mask softmax से पहले क्यों लगता है, बाद में क्यों नहीं"
type: lesson
---

# पाठ 3. Causal Masking

**मिशन से संबंध:** यह चरण 1 का समापन है: multi-head attention (पाठ 2) हर position को बाक़ी हर position पर attend करने देता है, जो इस workspace के model को आगे जो autoregressive generation करनी है उसके लिए ठीक उलटा है, और यह पाठ उसी का हल है।
**मुख्य स्रोत:** [लेख: "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
**पूर्व-आवश्यकताएँ:** [पाठ 2](0002-multi-head-attention.md), [Scaled dot-product attention](../GLOSSARY.md)

## वार्म-अप

1. ▢ Multi-head attention में, एक head के अंदर `/ sqrt(d_k)` scaling निकालते समय `d_k` प्रति-head आयाम होना चाहिए या model का पूरा आयाम?

<details markdown="1"><summary>जाँचें</summary>

प्रति-head आयाम (`d_model / h`)। Scaling `d_k` पदों पर जोड़े गए dot product के variance की बढ़त को काटती है, और एक head के अंदर वह dot product head के अपने, छोटे आयाम पर जोड़ा जाता है।

</details>

2. ▢ Scaled dot-product attention में softmax चरण क्या हासिल करता है?

<details markdown="1"><summary>जाँचें</summary>

वह हर query के, हर key के विरुद्ध, कच्चे similarity scores को probability distribution में बदल देता है, जो ग़ैर-ऋणात्मक होता है और जिसका योग 1 होता है, और इसी से output values का भारित मिश्रण बनता है।

</details>

## यह जानें

### भविष्य पर attend करना समस्या क्यों है

जो model text को एक बार में एक token करके generate करता है, वह token *N* सिर्फ़ token 1 से *N-1* का इस्तेमाल करके बनाता है; token *N+1* उस समय तक मौजूद ही नहीं होता। अगर training के दौरान self-attention position *i* को उस position *j* पर attend करने देती है जो *i* से बड़ी है, तो model उसी token को, जिसे उसे predict करना है, और उसके बाद के हर token को, उस predict की गणना में इस्तेमाल कर सकता है। Training loss बढ़िया दिखता है, क्योंकि model असल में एक ऐसा उत्तर नक़ल कर रहा है जो उसे पहले से दिख रहा है, पर model कुछ काम का नहीं सीखता, क्योंकि असली generation के समय वे भविष्य के tokens कभी उपलब्ध नहीं होते। **Causal masking** training को ईमानदार रखती है: वह हर position को सिर्फ़ ख़ुद पर और पहले की positions पर attend करने तक सीमित करती है, ठीक वही जो तब उपलब्ध होगा जब model असल में text को एक बार में एक token generate करेगा।

### Mask scores पर लगता है, softmax से पहले

हल समीकरण के भीतर ही, softmax चरण से पहले होता है: कच्चे `QK^T / sqrt(d_k)` scores में एक mask जोड़ा जाता है, जो हर उस प्रविष्टि को एक बहुत बड़ी ऋणात्मक संख्या पर सेट कर देता है जहाँ key की position query की position से बाद की है (व्यवहार में negative infinity या संख्यात्मक रूप से उसके बराबर कुछ, जैसे -1e9)। वह masked score जब softmax के अंदर `exp(...)` से गुज़रता है, तो बहुत बड़ी ऋणात्मक संख्या शून्य से अलग न पहचाने जा सकने वाले मान में बदल जाती है, इसलिए वह position अंतिम भारित योग में लगभग कुछ नहीं जोड़ती, और बाक़ी बिना mask वाली positions के weights आपस में दोबारा normalize होकर फिर भी जोड़ में 1 रहते हैं।

### Softmax के बाद weights को शून्य क्यों नहीं कर देते

Softmax चल चुकने के *बाद* किसी भविष्य की position का weight शून्य कर देना सही ढंग से काम नहीं करता: बाक़ी weights पहले ही यह मानकर compute हो चुके थे कि वह position probability mass की असली दावेदार थी, और उसे बाद में शून्य करने पर बचे हुए weights का योग अब 1 नहीं रहता, जो वैध probability distribution नहीं है। Mask softmax से पहले ही लगना चाहिए ताकि दोबारा normalization उसी computation के हिस्से के रूप में अपने-आप हो जाए।

### कच्चे score को सादे 0 पर भी क्यों नहीं रख सकते

भविष्य की position का कच्चा score बड़ी ऋणात्मक संख्या की जगह 0 पर रखना उसे बाहर नहीं करता: `exp(0) = 1`, जो softmax के हर में एक बिल्कुल सामान्य, नज़रअंदाज़ न होने वाला योगदान है, "कोई attention नहीं" बिल्कुल नहीं। 0 का score एक तटस्थ, औसत similarity की तरह पढ़ा जाता है, जो बाक़ी हर position के असली score के साथ बराबरी पर मुक़ाबला करता है। सिर्फ़ काफ़ी बड़ी ऋणात्मक संख्या ही उसके exponential को असरदार रूप से शून्य तक पहुँचाती है, और वही उस position को भारित योग से सही ढंग से हटाती है।

### Mask का आकार: एक तय lower-triangular pattern

लंबाई *n* की sequence के लिए causal mask हर बार वही lower-triangular pattern होता है: query position *i* को key positions 0 से *i* तक (दोनों समेत) attend करने की अनुमति है, और *i* के बाद की हर position से उसे रोका जाता है। वही mask का आकार हर attention head और batch के हर example पर लागू होता है, और softmax चलने से पहले score matrix में एक बार जोड़ा जाता है।

![4 गुणा 4 का एक grid जिसमें पंक्तियाँ query positions 0 से 3 हैं और स्तंभ key positions 0 से 3। जिन cells में key position, query position से कम या उसके बराबर है, वे धूसर रंग के हैं और अनुमत हैं। जिन cells में key position, query position से बड़ी है, यानी diagonal के ऊपर, उन पर नारंगी X लगा है और softmax से पहले उन्हें mask कर दिया जाता है। अनुमत cells diagonal समेत एक lower-triangular pattern बनाते हैं।](images/causal-mask-lower-triangular.svg)

## अभ्यास

1. ▢ Inference के समय model का असल इस्तेमाल जिस तरह होगा, उसे देखते हुए position *i* की attention में *i* से बड़ी कोई position *j* क्यों शामिल नहीं होनी चाहिए?

<details markdown="1"><summary>जाँचें</summary>

Inference में model एक बार में एक token generate करता है और सिर्फ़ अपने से पहले आए tokens का इस्तेमाल करता है; मौजूदा position के बाद के tokens उसे predict करते समय मौजूद ही नहीं होते। अगर training position *i* को किसी बाद की position *j* पर attend करने देती, तो model ऐसी जानकारी पर निर्भर होना सीख लेता जो असली generation के समय कभी उपलब्ध नहीं होगी।

</details>

2. ▢ Causal mask कच्चे scores पर softmax से पहले क्यों लगता है, softmax चल चुकने के बाद attention weights को शून्य करने के बजाय?

<details markdown="1"><summary>जाँचें</summary>

Softmax के output weights एक साथ compute होते हैं और जो भी scores उसे दिए गए उन पर उनका योग 1 होता है। बाद में किसी weight को शून्य करने पर बाक़ी weights का योग 1 से कम रह जाता है, जो अब वैध probability distribution नहीं है। इसके उलट, softmax से पहले mask लगाने पर बची हुई, बिना mask वाली positions के बीच दोबारा normalization उसी computation के हिस्से के रूप में अपने-आप हो जाता है।

</details>

3. ▢ भविष्य की position का कच्चा score बड़ी ऋणात्मक संख्या की जगह सादे 0 पर रखने से उसे attention से सही ढंग से बाहर क्यों नहीं किया जा सकता?

<details markdown="1"><summary>संकेत</summary>

सोचें कि `exp(0)` का मान क्या होता है, और इसका softmax के हर पर क्या मतलब निकलता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

`exp(0) = 1`, जो एक बिल्कुल सामान्य, नज़रअंदाज़ न होने वाला मान है और softmax के हर में अब भी probability mass के लिए होड़ करता है। 0 का score औसत, तटस्थ similarity की तरह पढ़ा जाता है, "इस position को बाहर करो" की तरह नहीं। सिर्फ़ काफ़ी बड़ी ऋणात्मक संख्या ही उसके exponential को असरदार रूप से शून्य तक ले जाती है, और वही असल में उस position का योगदान हटाती है।

</details>

4. ▢ 4-token की sequence (positions 0 से 3) के लिए, causal mask के तहत query position 2 किन key positions पर attend कर सकती है?

<details markdown="1"><summary>जाँचें</summary>

Positions 0, 1 और 2। Position 3, position 2 से बाद की होने के कारण, mask हो जाती है।

</details>

5. ▢ Causal masking कैसे लागू होती है, इसके बारे में कौन-सा दावा सही है?

    - a) वह softmax के attention weights compute कर चुकने के बाद उन्हें शून्य करती है
    - b) वह softmax से पहले भविष्य की positions के कच्चे scores में एक बड़ी ऋणात्मक संख्या जोड़ती है, ताकि उनके exponentials नगण्य हो जाएँ और बाक़ी weights अपने-आप दोबारा normalize हो जाएँ
    - c) वह सिर्फ़ पहले attention head पर लागू होती है, क्योंकि बाद के heads को इस पाबंदी की ज़रूरत नहीं
    - d) भविष्य की position का score 0 पर रखना उसे mask करने के बराबर है

<details markdown="1"><summary>जाँचें</summary>

**b)** यही तंत्र है, और इसी वजह से इसका softmax से पहले होना ज़रूरी है। (a) ग़लत है: softmax के बाद शून्य करने से बाक़ी weights का योग 1 नहीं रहता। (c) ग़लत है: वही mask हर head पर एक जैसा लगता है। (d) ग़लत है: 0 का score `exp(0) = 1` के ज़रिए फिर भी पूरा, सामान्य weight जोड़ता है, वह उस position को बिल्कुल बाहर नहीं करता।

</details>

## असली दुनिया का अभ्यास

- [ ] पाठ 2 के अपने multi-head attention implementation में causal masking जोड़ें: चुनी हुई sequence length के लिए एक lower-triangular mask बनाएँ और softmax से पहले उसे scores में जोड़ें।
- [ ] एक छोटी sequence के लिए, एक query position के softmax weights mask के साथ और mask के बिना print करें, और पक्का करें कि mask वाले संस्करण में भविष्य की positions पर लगभग शून्य weight है।
- [ ] कल: मुख्य स्रोत के code का masking खंड अपने implementation के साथ पढ़ें, और पक्का करें कि mask computation में उसी जगह (softmax से पहले, scores में जोड़कर) लगाया गया है।

## आगे बढ़ने के लिए

- [लेख: "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
- [पेपर: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
