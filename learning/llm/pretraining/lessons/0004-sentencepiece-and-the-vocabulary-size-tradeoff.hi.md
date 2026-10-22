---
title: "4. SentencePiece और Vocabulary Size का Tradeoff"
description: "Pre-tokenizer के बिना कच्चे text को tokenize करना, और बड़ी या छोटी vocabulary की असल में क्या क़ीमत है"
type: lesson
---

# पाठ 4. SentencePiece और Vocabulary Size का Tradeoff

**मिशन से संबंध:** "Tokenizer train करें और vocabulary size का बचाव उसके sequence length और embedding table के आकार पर पड़ने वाले असर के आधार पर करें" "सफलता कैसी दिखती है" का दूसरा बिंदु है। पाठ 3 ने merge algorithm बनाया; यह पाठ कवर करता है कि उसे शब्द की सीमाएँ माने बिना कैसे train किया जाए, और size का फ़ैसला ख़ुद।
**मुख्य स्रोत:** [पेपर: "SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing", Kudo and Richardson, 2018](https://arxiv.org/abs/1808.06226)
**पूर्व-आवश्यकताएँ:** [पाठ 3](0003-byte-pair-encoding-from-scratch.md)

## वार्म-अप

1. ▢ Byte-pair encoding algorithm में, किए गए merge operations की संख्या क्या तय करती है?

<details markdown="1"><summary>जाँचें</summary>

अंतिम vocabulary size: वह शुरुआती character set और हर किए गए merge पर एक नए symbol के बराबर होती है।

</details>

2. ▢ पाठ 3 के हल किए उदाहरण की तीन जोड़ियाँ (`(e, s)`, `(s, t)`, `(t, </w>)`) कुछ ही steps के भीतर सब merge क्यों हो गईं, चाहे पहले कोई भी merge हुई हो?

<details markdown="1"><summary>जाँचें</summary>

वे सब एक ही frequency पर बराबर थीं क्योंकि वे सब एक ही दोहराए substring, "est", से आई थीं। उनमें से किसी एक को merge करने से tie हटने के बजाय बाक़ी उसी count पर नई जोड़ियों के रूप में बदल गईं, इसलिए पहले कोई भी merge हो, तीनों जल्दी ही एक साथ गुँथ गईं।

</details>

## यह जानें

### शब्द की सीमाएँ मान लेना क्यों टूटता है

Byte-pair encoding, जैसा पाठ 3 ने बताया, आम तौर पर **pre-tokenizer** के ऊपर चलाई जाती है: कुछ ऐसा जो पहले कच्चे text को शब्दों में बाँटता है, ताकि BPE को सिर्फ़ किसी शब्द के भीतर के merges सीखने पड़ें। अंग्रेज़ी के लिए, whitespace पर बाँटना आसान और ज़्यादातर भरोसेमंद pre-tokenizer है। यह भाषा-निरपेक्ष नहीं है: बहुत-सी व्यापक रूप से इस्तेमाल होने वाली लिखित भाषाएँ, जिनमें जापानी और चीनी शामिल हैं, शब्दों को spaces से अलग करती ही नहीं, इसलिए BPE शुरू होने से पहले ही whitespace pre-tokenizer के पास बाँटने को कुछ समझदारी भरा नहीं होता। हर भाषा या हर लिपि के लिए अलग pre-tokenizer बनाना उस विचार को कमज़ोर करता है कि tokenizer-training की एक ऐसी प्रक्रिया हो जो कहीं भी चले।

### सीधे कच्चे वाक्यों पर training

Kudo और Richardson का SentencePiece pre-tokenization चरण को हर भाषा के लिए ठीक करने की कोशिश करने के बजाय उसे हटा देता है: वह अपना subword model सीधे कच्चे वाक्यों के text पर train करता है, पहले से मौजूद शब्द-सीमाओं की कोई धारणा भीतर बनाए बिना। Whitespace को input में सामान्य symbol की तरह लिया जाता है, आम तौर पर किसी समर्पित चिह्न से दिखाया जाता है ताकि detokenization पर मूल spacing हू-ब-हू लौटाई जा सके, न कि ऐसी चीज़ की तरह जिस पर training शुरू होने से पहले बाँटा जाए। इससे वही training प्रक्रिया भाषा-निरपेक्ष बन जाती है, जिसे पेपर अंग्रेज़ी-जापानी machine translation के एक प्रयोग से पुष्ट करता है: कच्चे वाक्यों पर end-to-end training से वैसी ही accuracy मिली जैसी उस text पर training से मिली जिसे अलग औज़ार पहले ही शब्दों में बाँट चुका था।

### एक toolkit, दो training algorithms

SentencePiece BPE का कोई दूसरा प्रतिस्पर्धी algorithm नहीं है; यह एक toolkit है जो BPE (पाठ 3 की merge प्रक्रिया) के साथ एक दूसरा training algorithm, **unigram language model** trainer, लागू करता है, जो उलटी दिशा में काम करता है। अलग-अलग characters से शुरू करके merges ऊपर की ओर बढ़ाने के बजाय, यह उम्मीदवार subwords के बड़े सेट से शुरू करता है और लक्ष्य vocabulary size तक बार-बार छाँटता जाता है, हर चरण पर उन टुकड़ों को हटाता है जिनकी कमी model की likelihood को सबसे कम खलेगी। दोनों में से कोई भी training algorithm एक ही शक्ल का नतीजा देता है: subword टुकड़ों की तय vocabulary और नए कच्चे text को उनमें बाँटने का एक निर्धारित तरीक़ा।

### Vocabulary-size का tradeoff

लक्ष्य vocabulary size, चाहे उसे जैसे भी train किया गया हो, एक अकेली संख्या है जो एक साथ एक से ज़्यादा दिशाओं में खींचती है:

- **बड़ी** vocabulary उसी text को औसतन कम tokens में encode करती है, क्योंकि ज़्यादा आम substrings को अपना अकेला symbol मिल जाता है। छोटे token sequences का मतलब है उसी input पर attend करने और उसे generate करने में कम compute।
- **बड़ी** vocabulary का मतलब बड़ी embedding table और बड़ा output projection भी है (आम तौर पर वही matrix, आपस में जुड़ा हुआ), जो ऐसा parameter count है जो vocabulary size के साथ सीधे बढ़ता है, इससे स्वतंत्र कि model का बाक़ी हिस्सा कितना गहरा या चौड़ा है।
- **बड़ी** vocabulary training signal को ज़्यादा पतला फैलाती है: उसी corpus को चुनने के लिए ज़्यादा अलग टुकड़ों में काटने पर, कोई एक ख़ास token, ख़ासकर दुर्लभ वाला, data के हर पास में कम बार दिखता है।
- **छोटी** vocabulary तीनों को उलट देती है: हर input के लिए लंबे token sequences, छोटी embedding और output table, और हर token पर घना training signal, इस क़ीमत पर कि आम शब्द हर एक ज़्यादा टुकड़ों में बँटते हैं।

कोई एक vocabulary size हर अक्ष पर एक साथ नहीं जीतती, इसलिए उसे किसी formula से पढ़ने के बजाय किसी ख़ास model के आकार और budget के हिसाब से चुना जाता है। एक असली, जाँचा जा सकने वाला उदाहरण: LLaMA पेपर बताता है कि उसने अपने training data को SentencePiece implementation के ज़रिए byte-pair encoding से tokenize किया, सभी संख्याओं को अलग-अलग अंकों में बाँटा, और किसी भी UTF-8 character को, जिसे train हुई vocabulary दूसरे तरीक़े से कवर नहीं करती, दर्शाने के लिए कच्चे bytes पर लौटा, ताकि कोई भी input character सचमुच दर्शाया न जा सकने वाला न रहे, चाहे चुनी गई vocabulary size कुछ भी हो।

## अभ्यास

1. ▢ Whitespace pre-tokenizer पर बना tokenizer, जो सिर्फ़ अंग्रेज़ी पर train हुआ है, बिना बदलाव जापानी text पर लगाया जाता है, जिसमें शब्दों के बीच spaces नहीं होते। क्या ग़लत होता है, और SentencePiece क्या अलग करता है जो इससे बचाता है?

<details markdown="1"><summary>जाँचें</summary>

Whitespace pre-tokenizer के पास बाँटने को कुछ समझदारी भरा नहीं होता, क्योंकि जापानी शब्दों को spaces से अलग नहीं करती, इसलिए वह BPE को merge करने के लिए शब्द-आकार के उचित टुकड़े नहीं दे पाता। SentencePiece इससे इस तरह बचता है कि वह सीधे कच्चे वाक्यों के text पर train करता है, पहले से मौजूद शब्द-सीमाओं की कोई धारणा बनाए बिना, और whitespace को आवश्यक पूर्व-विभाजन की जगह सामान्य symbol मानता है।

</details>

2. ▢ एक team अपने tokenizer की vocabulary size दोगुनी कर देती है जबकि model का hidden dimension और depth बिल्कुल वही रखती है। इनमें से कौन-सा नतीजे का सबसे अच्छा वर्णन करता है?

    - a) Sequences औसतन छोटे हो जाते हैं, और embedding और output tables सिकुड़ जाती हैं
    - b) Sequences औसतन छोटे हो जाते हैं, पर embedding और output tables बढ़ जाती हैं
    - c) Sequences औसतन लंबे हो जाते हैं, पर embedding और output tables सिकुड़ जाती हैं
    - d) Vocabulary size से न sequence length पर असर पड़ता है न parameter count पर

<details markdown="1"><summary>संकेत</summary>

Vocabulary size दो अलग चीज़ों पर असर डालती है: text का कोई टुकड़ा कितने tokens में बदलता है, और हर token को vector से जोड़ने वाली table कितनी बड़ी है। हर एक को अलग से सोचें।

</details>

<details markdown="1"><summary>जाँचें</summary>

**b)** बड़ी vocabulary का मतलब है कि ज़्यादा आम substrings को अपना token मिलता है, जिससे sequences छोटे होते हैं, जबकि embedding और (आम तौर पर जुड़ी हुई) output projection tables दोनों vocabulary size के साथ सीधे बढ़ती हैं, इसलिए वे बड़ी होती हैं। (a) और (c) दोनों में से एक असर उलटा पकड़ते हैं, और (d) दोनों को अनदेखा करता है।

</details>

3. ▢ एक अक्ष बताइए जिस पर छोटी vocabulary बड़ी से बेहतर है, और एक जिस पर वह बदतर है।

<details markdown="1"><summary>जाँचें</summary>

बेहतर: हर token पर घना training signal (उसी corpus पर हर पास में हर token ज़्यादा बार दिखता है), या छोटी embedding और output table। बदतर: हर input के लिए लंबे token sequences, क्योंकि आम शब्द ज़्यादा टुकड़ों में बँटते हैं, जिन पर attend करने और जिन्हें generate करने में ज़्यादा compute लगता है।

</details>

4. ▢ इनमें से कौन-सा सबसे अच्छा बताता है कि SentencePiece, एक software के रूप में, क्या है?

    - a) एक अकेला नया tokenization algorithm जो byte-pair encoding की जगह लेता है
    - b) एक toolkit जो byte-pair encoding और unigram-language-model trainer दोनों को सीधे कच्चे text पर लागू करता है, pre-tokenization चरण की ज़रूरत के बिना
    - c) सिर्फ़ एक pre-tokenizer, जिसे अलग BPE implementation से पहले चलाया जाना है
    - d) किसी भी तय vocabulary के बिना model train करने का तरीक़ा

<details markdown="1"><summary>जाँचें</summary>

**b)** SentencePiece दो training algorithms, byte-pair encoding और unigram language model, को एक साथ पैक करता है, और उसकी ख़ास पहचान सीधे कच्चे वाक्यों से training है। (a) ग़लत है क्योंकि वह BPE की जगह लेने के बजाय उसे अब भी लागू करता है। (c) SentencePiece के असली योगदान को उलट देता है, जो pre-tokenization चरण को हटाना है। (d) ऐसे किसी असली tokenizer का वर्णन नहीं करता जिस पर इस track में चर्चा हुई; दोनों algorithms अब भी तय vocabulary ही बनाते हैं।

</details>

## असली दुनिया का अभ्यास

- [ ] उस tokenizer की बताई हुई vocabulary size खोजें जिस तक आपकी पहुँच है, चाहे किसी library से या किसी hosted model की प्रकाशित tokenizer files से।
- [ ] अगर आप साफ़ तौर पर अलग vocabulary sizes वाले दो tokenizers तक पहुँच सकते हैं, तो एक ही वाक्य को दोनों से encode करें और नतीजे में आए token counts की सीधी तुलना करें।
- [ ] कल: किसी ऐसे ख़ास project या use case के लिए जिसका पैमाना आप जानते हैं (chat assistant, code पर केंद्रित model, कम संसाधन वाली भाषा का कोई औज़ार), गुणात्मक रूप से तय करें कि आप मुख्यधारा के model से बड़ी या छोटी vocabulary की ओर झुकेंगे, और लिखें कि tradeoff का कौन-सा अकेला अक्ष आपके उत्तर को चला रहा था।

## आगे बढ़ने के लिए

- [पेपर: "SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing", Kudo and Richardson, 2018](https://arxiv.org/abs/1808.06226)
- [संसाधन](../RESOURCES.md)

---

चरण 1 ने कवर किया कि corpus में क्या जाता है और उसमें से क्या हटाया जाता है; चरण 2 ने कवर किया कि उस corpus को tokens में बदला कैसे जाता है। चरण 3 उस सवाल की ओर मुड़ता है जो दोनों के ऊपर बैठा है: parameter count दिए जाने पर, उन tokens में से कितनों पर train करना सार्थक है।

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
