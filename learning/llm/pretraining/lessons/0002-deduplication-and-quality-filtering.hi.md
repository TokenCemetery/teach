---
title: "2. Deduplication और Quality Filtering"
description: "Training से पहले लगभग-एक-जैसे text और घटिया documents क्यों हटाए जाते हैं, और यह चरण छोड़ने की क्या क़ीमत है"
type: lesson
---

# पाठ 2. Deduplication और Quality Filtering

**मिशन से संबंध:** "कच्चे स्रोतों से deduplicated, quality-filtered pretraining corpus बनाएँ, और बताएँ कि हर filtering चरण क्या हटाता है और क्यों" "सफलता कैसी दिखती है" का पहला बिंदु है। पाठ 1 ने sourcing और mixing कवर किए; यह पाठ deduplication और filtering वाले आधे हिस्से को कवर करता है।
**मुख्य स्रोत:** [पेपर: "Deduplicating Training Data Makes Language Models Better", Lee et al., 2021](https://arxiv.org/abs/2107.06499)
**पूर्व-आवश्यकताएँ:** [पाठ 1](0001-sourcing-and-mixing-a-pretraining-corpus.md)

## वार्म-अप

1. ▢ Pretraining corpus के लिए sourcing के फ़ैसले और mixing के फ़ैसले में क्या फ़र्क़ है?

<details markdown="1"><summary>जाँचें</summary>

Sourcing तय करता है कि कौन-से स्रोत शामिल होंगे ही। Mixing तय करता है कि अंतिम token budget का कितना हिस्सा हर शामिल स्रोत को मिलेगा, इससे स्वतंत्र कि कौन-से स्रोत चुने गए थे।

</details>

2. ▢ The Pile पेपर के अनुसार, pretraining run के बारे में "corpus कितना बड़ा है" पूछने का ग़लत पहला सवाल क्यों है?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि GPT-2 और GPT-3, जो भारी मात्रा में web text पर train हुए थे, फिर भी academic writing जैसे हिस्सों पर जूझे जिन्हें सामान्य web crawl कम दिखाता है। कौन-से स्रोत शामिल हैं, न कि कुल byte count, यह तय करता है कि model असल में कौन-से domains सीखता है।

</details>

## यह जानें

### Duplicates सिर्फ़ बर्बाद disk space नहीं हैं

कई स्रोतों से जोड़ा गया corpus, ख़ासकर कुछ भी जो खुले web को छूता हो, ऐसा निकलता है जिसमें वही text एक से ज़्यादा बार दिखता है: syndicated समाचार लेख, boilerplate क़ानूनी disclaimers, ऐसे template emails जिनमें सिर्फ़ नाम बदला हो। Lee et al. ने पाया कि यह कोई छोटी अकुशलता नहीं है। C4 में, जो web-crawl से बना व्यापक रूप से इस्तेमाल होने वाला corpus है, 61 शब्दों का एक अकेला अंग्रेज़ी वाक्य 60,000 से ज़्यादा बार आता है। इससे भी चौंकाने वाली बात यह है कि ऐसे datasets पर train हुए language models के बिना-prompt वाले output के 1% से ज़्यादा हिस्से को training data से हू-ब-हू copy किया गया है: model वहाँ generalize नहीं कर रहा, वह ऐसी चीज़ को दोहरा रहा है जिसे उसने इतनी बार देखा कि रट लिया।

### Duplicate खोजने के दो अलग तरीक़े

Deduplication को दोहराव के दो अलग रूप पकड़ने होते हैं, और एक तकनीक दोनों नहीं पकड़ती:

- **Exact substring matching** text के हू-ब-हू दोहराए गए हिस्से खोजती है, चाहे वे document का सिर्फ़ एक अंश हों या documents की सीमाओं को पार करते हों। Lee et al. इसे suffix array से कुशलता से लागू करते हैं, जिससे किसी भी लंबाई का दोहराया हुआ हिस्सा हर document को हर दूसरे document से सीधे मिलाए बिना खोजा जा सकता है।
- **Near-duplicate matching** ऐसे documents खोजती है जो ज़्यादातर एक-जैसे हैं पर छोटे तरीक़ों से अलग हैं, जैसे किसी दूसरे प्राप्तकर्ता के नाम वाला form email, या ऐसी समाचार-एजेंसी की ख़बर जिसे कई outlets ने मामूली संपादन के साथ उठाया। Lee et al. MinHash इस्तेमाल करते हैं: ऐसी तकनीक जो दो documents को token-दर-token मिलाए बिना, उनके संक्षिप्त hash-आधारित सारों की तुलना करके अनुमान लगाती है कि वे कितने मिलते-जुलते हैं।

दोनों मायने रखती हैं, क्योंकि corpus एक तरह के दोहराव से मुक्त होकर भी दूसरे से भरा हो सकता है।

### Deduplication से असल में क्या मिलता है

Lee et al. अंदाज़े के बजाय ठोस सबूत देते हैं। Training data की deduplication से models ने memorize किया हुआ text लगभग दस गुना कम बार उगला, और वही models कम training steps में उतनी ही या बेहतर accuracy तक पहुँचे। यह train-test overlap भी घटाती है, जिसके बारे में पेपर ने पाया कि वह मानक benchmarks में validation set के 4% से ज़्यादा हिस्से को प्रभावित करता है; जो text किसी benchmark के अपने validation set से training में रिस गया हो, वह evaluation की संख्या को model के असली generalization के हक़ से बेहतर दिखाता है, एक चिंता जिस पर यह track तब लौटेगा जब वह `llm/evals` के contamination वाले विवेचन की ओर link करेगा।

### Quality filtering अलग और बाद का चरण है

Deduplication उस text की फ़ालतू copies हटाती है जो पहले से मौजूद है। Quality filtering वह text हटाती है जो किसी की copy न होकर भी कम-मूल्य का है: spam, boilerplate navigation menus, machine-generated text, या इतने बिगड़े documents जिनमें बहुत कम signal है। GPT-3 के लेखक Common Crawl filtering पर अपने appendix में इसका एक ठोस रूप बताते हैं: उन्होंने एक classifier train किया, सरल bag-of-words जैसे features पर logistic regression से, जो छाँटे हुए text (WebText, Wikipedia, किताबों का corpus) को कच्चे, बिना filter किए Common Crawl से अलग पहचानता था। उस classifier के score का इस्तेमाल Common Crawl को दोबारा sample करने में हुआ, ताकि जिन documents को ऊँची गुणवत्ता का अनुमानित किया गया उन्हें ज़्यादा बार रखा जाए, और कम score वाले कुछ documents को सीधे फेंकने के बजाय फिर भी रखा जाए। उसी appendix में MinHash से एक अलग fuzzy-deduplication pass का भी वर्णन है, जिसने अपने-आप में उनके dataset का आकार लगभग 10% घटा दिया।

Quality filtering और deduplication अक्सर एक ही corpus पर अलग-अलग passes की तरह, किसी भी क्रम में चलाई जाती हैं, और कोई भी दूसरी की जगह नहीं लेती: corpus हू-ब-हू duplicates से मुक्त होकर भी कम-मूल्य के boilerplate से भरा हो सकता है, और वह एक-सा उच्च-गुणवत्ता वाला गद्य होकर भी वही अनुच्छेद साठ हज़ार बार दोहराए जाने से भरा हो सकता है।

## अभ्यास

1. ▢ एक dataset में 61 शब्द 60,000 से ज़्यादा अलग documents में हू-ब-हू दोहराए गए हैं, हर बार आसपास के text के साथ जो अलग है। सिर्फ़ उस दोहराए हुए हिस्से को खोजने और हटाने के लिए सही औज़ार exact substring matching होगी या near-duplicate matching (MinHash), और क्यों?

<details markdown="1"><summary>संकेत</summary>

सोचें कि MinHash असल में क्या मिलाता है: पूरे documents को एक-दूसरे से, या text के ऐसे हिस्सों को जो किसी document का सिर्फ़ एक अंश हो सकते हैं।

</details>

<details markdown="1"><summary>जाँचें</summary>

Exact substring matching। MinHash पूरे documents के बीच समानता का अनुमान लगाता है; बाक़ी text में अलग documents के भीतर दोहराया गया 61 शब्दों का हिस्सा ठीक वही आंशिक, documents को पार करने वाला दोहराव है जिसे suffix-array-आधारित exact substring search पकड़ने के लिए बनी है, जबकि दो documents जो कई हज़ार शब्दों में से सिर्फ़ 61 शब्द साझा करते हैं, शायद एक-दूसरे के near-duplicates के रूप में दर्ज ही न हों।

</details>

2. ▢ इनमें से कौन-सा उसके सबसे क़रीब है जो Lee et al. ने असल में नापा, सिर्फ़ तर्क नहीं दिया?

    - a) Deduplication model को दार्शनिक रूप से ज़्यादा मौलिक बनाती है
    - b) Deduplicated training से models कम steps में उतनी ही या बेहतर accuracy तक पहुँचे, और memorize किया हुआ text लगभग दस गुना कम बार उगला
    - c) Deduplication सिर्फ़ storage लागत घटाने के काम की है, model के व्यवहार पर उसका कोई असर नहीं
    - d) Near-duplicate matching अकेली दोहराए गए text के हर रूप को हटाने के लिए काफ़ी है

<details markdown="1"><summary>जाँचें</summary>

**b)** पेपर का असल में नापा गया नतीजा है। (a) नापा जा सकने वाला दावा नहीं है। (c) memorization और training-कुशलता के नतीजों का सीधा खंडन करता है। (d) ग़लत है, क्योंकि exact substring matching दोहराव का वह रूप पकड़ती है जो near-duplicate matching नहीं पकड़ती, जैसा इस पाठ का पहला अभ्यास दिखाता है।

</details>

3. ▢ कोई document corpus में किसी और की copy नहीं है, पर वह ज़्यादातर अपने-आप बना boilerplate है जिसमें जानकारी लगभग नहीं है। क्या deduplication उसे हटा देगी? क्या हटाएगा?

<details markdown="1"><summary>जाँचें</summary>

नहीं, deduplication उसे नहीं हटाएगी, क्योंकि deduplication सिर्फ़ दोहराए गए text को निशाना बनाती है और यह document अनूठा है। Quality filtering, जैसे GPT-3 के लेखकों का बताया classifier-आधारित दोबारा sampling, ठीक इसी स्थिति के लिए है: कम-मूल्य का text जो किसी और की copy नहीं है।

</details>

4. ▢ GPT-3 के Common Crawl quality classifier को इनमें से किन चीज़ों की जोड़ी में फ़र्क़ करने के लिए train किया गया था?

    - a) अंग्रेज़ी text और ग़ैर-अंग्रेज़ी text
    - b) छाँटा हुआ text (WebText, Wikipedia, किताबों का corpus) और कच्चा, बिना filter किया Common Crawl
    - c) लंबे documents और छोटे documents
    - d) दोहराया गया text और अनूठा text

<details markdown="1"><summary>जाँचें</summary>

**b)** छाँटा हुआ text बनाम कच्चा Common Crawl। (d) deduplication का वर्णन है, जिसे GPT-3 के लेखकों ने अलग MinHash pass के रूप में चलाया, न कि वह जो quality classifier को पहचानने के लिए train किया गया था।

</details>

## असली दुनिया का अभ्यास

- [ ] कोई वाक्य या छोटा वाक्यांश चुनें जो आपके अनुमान से web text में आम होगा (कोई disclaimer, कोई रटा-रटाया वाक्यांश, कोई आम recipe निर्देश) और उसे online हू-ब-हू खोजें। मोटे तौर पर नोट करें कि वह कितने अलग pages पर मिला, यह महसूस करने के लिए कि असली crawl किए text में दोहराव कैसा दिखता है।
- [ ] Lee et al. के पेपर (ऊपर linked) का abstract और introduction पढ़ें, और हर एक के लिए एक वाक्य में लिखें कि exact substring matching और near-duplicate matching में से हर एक क्या पकड़ने में अच्छी है जो दूसरी नहीं पकड़ती।
- [ ] कल: वह corpus लें जिसका mixture आपने पाठ 1 के असली दुनिया के अभ्यास में बनाया था, और हर स्रोत प्रकार के लिए दोहराव का एक संभावित स्रोत (syndication, templated boilerplate, दोबारा पोस्ट करना) और कम गुणवत्ता का एक संभावित स्रोत बताएँ जिसे अकेली deduplication नहीं पकड़ेगी।

## आगे बढ़ने के लिए

- [पेपर: "Deduplicating Training Data Makes Language Models Better", Lee et al., 2021](https://arxiv.org/abs/2107.06499)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
