---
title: "3. Task-Specific Metrics"
description: "Exact match, token-level F1 और BLEU/ROUGE, और हर एक की विफलता का तरीक़ा"
type: lesson
---

# पाठ 3. Task-Specific Metrics

**मिशन से संबंध:** चरण 2 मिशन का "eval बनाएँ" वाला आधा हिस्सा खोलता है: task-specific metric held-out सेट (चरण 1) को असली संख्या में बदलती है, और इस पाठ की हर metric कुछ tasks पर अच्छी बैठती है और दूसरों के बारे में चुपचाप झूठ बोलती है।
**मुख्य स्रोत:** [दस्तावेज़: Evaluate, Hugging Face](https://huggingface.co/docs/evaluate/index)
**पूर्व-आवश्यकताएँ:** [पाठ 2](0002-designing-contamination-resistance.md), [Data contamination](../GLOSSARY.md)

## वार्म-अप

1. ▢ Custom eval सेट में canary string डालना असल में किस चीज़ से बचाता है?

<details markdown="1"><summary>जाँचें</summary>

वह training corpus जोड़ने वाले crawlers को संकेत देती है कि चिह्नित सामग्री बाहर रखी जाए, और अगर string बाद में किसी model के output या पहुँच-योग्य corpus में दिखे तो रिसाव पकड़ने का तरीक़ा देती है। यह अनुरोध है, गारंटी नहीं: वह crawlers के परंपरा का सम्मान करने पर निर्भर है।

</details>

2. ▢ ज्ञात corpus के सामने n-gram overlap जाँच कब इस्तेमाल हो सकती है, और कब वह विकल्प नहीं रहती?

<details markdown="1"><summary>जाँचें</summary>

वह तब इस्तेमाल हो सकती है जब pretraining corpus ज्ञात और पहुँच-योग्य हो। वह ऐसे closed model के लिए विकल्प नहीं रहती जिसका training data बताया नहीं गया, जहाँ guided-instruction test ही उपलब्ध औज़ार रहता है।

</details>

## यह जानें

### Exact match: सख़्त, और ऊपरी भिन्नता के प्रति भुरभुरी

**Exact match** prediction को तभी सही गिनता है जब वह reference उत्तर से अक्षर-दर-अक्षर मेल खाए (अक्सर lowercasing या whitespace हटाने जैसे हल्के normalization के बाद)। यह उन tasks पर ठीक बैठता है जिनका एक साफ़ सही उत्तर हो: multiple choice, span extraction, गणित का नतीजा। इसकी विफलता वही है जो इसकी सख़्ती से निकलती है: अलग ढंग से कहा गया सही उत्तर (`"Paris"` बनाम reference `"Paris, France"`) ग़लत गिना जाता है, यानी वह correctness को मापने के बजाय उसे दंडित करता है, जब तक कि लगाया गया normalization इतना उदार न हो कि वह इस भिन्नता को सोख ले, और साथ में सचमुच ग़लत उत्तरों को न सोखे।

### Token-level F1: आंशिक श्रेय, क्रम की परवाह करने की क़ीमत पर

**F1** (जैसा span-आधारित question answering जैसे extractive tasks के लिए इस्तेमाल होता है) prediction और reference को सटीक string मेल माँगने के बजाय tokens की थैली मानता है, और precision (prediction के कितने हिस्से के tokens सही हैं) और recall (reference के कितने हिस्से के tokens पैदा हुए) निकालता है, फिर उनका harmonic mean। Reference "the cat sat on the mat" (tokens: `the, cat, sat, on, the, mat`) और prediction "a cat sat on the mat" (tokens: `a, cat, sat, on, the, mat`) में हर तरफ़ छह में से पाँच tokens साझा हैं (`cat, sat, on, the, mat`): precision `5/6`, recall `5/6`, F1 `5/6 ≈ 0.83`। यह exact match से ज़्यादा उदार है, जो इस जोड़ी को सीधे ग़लत गिनता। विफलता वही है जो इस उदारता की क़ीमत है: tokens की थैली पर F1 क्रम के प्रति अंधा है, और इस बात के प्रति भी कि मेल खाते शब्द मिलकर सचमुच सही उत्तर बनाते हैं या नहीं, इसलिए जो prediction सही शब्दों को उलट-पलटकर ग़लत दावा बना दे, वह भी ऊँचा score पा सकता है।

![Reference "the cat sat on the mat" और prediction "a cat sat on the mat" token के डिब्बों के रूप में रखे गए। cat, sat, on, mat और the का एक instance दोनों के बीच साझा हैं। Reference का दूसरा the और prediction का a, दोनों बिना मेल के हैं। हर तरफ़ छह में से पाँच tokens मेल खाते हैं, इसलिए precision 5/6 है, recall 5/6 है, और F1 5/6 है।](images/f1-token-overlap.svg)

### BLEU और ROUGE: reference के विरुद्ध n-gram overlap, अनुवाद और सारांश के लिए बने

**BLEU** (मूल रूप से machine translation के लिए) और **ROUGE** (मूल रूप से summarization के लिए) दोनों generate किए text को इस आधार पर score करते हैं कि उसके n-grams (लंबाई n के लगातार token अनुक्रम) एक या ज़्यादा reference texts से कितने मिलते हैं, सटीक मेल माँगने या अकेले tokens को अलग-अलग score करने के बजाय। इनकी विफलता खुले-सिरे वाली generation पर सबसे ज़्यादा दिखती है: वही बात दूसरे शब्दों में कहने वाला वैध paraphrase, "Critics praised the show" बनाम reference "The show received positive reviews from critics", उतना ही अच्छा उत्तर होने के बावजूद reference से बहुत कम n-grams साझा करता है, और नतीजे में कम score पाता है। हर example के लिए कई reference texts इस्तेमाल करने से यह कुछ नरम होता है, पर हर वैध शब्दावली को ढकने के लिए शायद ही कभी पर्याप्त references होते हैं, और यही बड़ा कारण है कि ये metrics खुले-सिरे वाले text पर मानव निर्णय से सिर्फ़ ढीला correlate करती हैं, और इसीलिए चरण 3 का LLM-as-judge ठीक उसी मामले के विकल्प के रूप में मौजूद है।

### Metric चुनने का मतलब है उसे उससे मिलाना जो task के लिए "सही" का मतलब है

Exact match और F1 उन tasks पर ठीक बैठते हैं जहाँ correctness उत्तरों का छोटा, साफ़-परिभाषित सेट है: classification, extraction, अंकगणित। BLEU और ROUGE उन tasks पर ठीक बैठते हैं जहाँ reference के साथ ऊपरी overlap, ढीले ढंग से, गुणवत्ता से correlate करता है, और जो अंतिम फ़ैसले के बजाय मोटे, सस्ते पहले छन्ने के रूप में काम आते हैं। इनमें से कोई परिवार उस task के लिए उपयुक्त नहीं जहाँ correctness text की नहीं बल्कि व्यवहार की है (क्या generate किया गया code सचमुच चलता है और सही output देता है), जो पाठ 4 का विषय है, या उस खुले-सिरे वाली generation के लिए जहाँ शब्दावली से ज़्यादा अर्थ मायने रखता है, जो चरण 3 का है।

## अभ्यास

1. ▢ एक model भूगोल के सवाल का उत्तर "Paris" देता है जबकि reference उत्तर "Paris, France" है। Exact match इसे ग़लत गिनता है। क्या यह सही scoring नतीजा है? क्यों या क्यों नहीं?

<details markdown="1"><summary>जाँचें</summary>

नहीं, असल में नहीं: उत्तर सही है, बस reference से ज़्यादा संक्षेप में कहा गया है। यह exact match की ऊपरी भिन्नता के प्रति भुरभुरापन है। सुधार है या तो तुलना से पहले दोनों strings को normalize करना (जो तभी मदद करता है जब normalization ख़ास इसी तरह की भिन्नता को सोखने के लिए डिज़ाइन किया गया हो), या ऐसे task के लिए ज़्यादा उदार metric चुनना जिसमें शब्दावली इतनी बदलती हो।

</details>

2. ▢ Reference: "a fast red fox jumps"। Prediction: "a red fox jumps fast"। Bag-of-tokens F1 (शब्दों के क्रम को अनदेखा करके) इस्तेमाल करते हुए, precision, recall और F1 score क्या हैं?

<details markdown="1"><summary>संकेत</summary>

हर तरफ़ के tokens को सेट के रूप में लिखें और गिनें कि स्थिति की परवाह किए बिना कितने साझा हैं।

</details>

<details markdown="1"><summary>जाँचें</summary>

दोनों तरफ़ वही 5 tokens हैं (`a, fast, red, fox, jumps` बनाम `a, red, fox, jumps, fast`), बस क्रम बदला है, इसलिए सभी 5 साझा हैं। Precision `5/5 = 1.0`, recall `5/5 = 1.0`, F1 `1.0`। यह F1 के क्रम के प्रति अंधेपन को भी दिखाता है: उलटे-पलटे शब्द-क्रम वाली prediction को उतना ही score मिलता है जितना क्रम बचाए रखने वाली को, भले ही शब्द-क्रम अर्थ बदल सकता हो, जिसे F1 पकड़ नहीं सकता।

</details>

3. ▢ एक summarization model reference सारांश "The show received positive reviews from critics." के लिए "Critics praised the show" बनाता है। क्या ROUGE इस जोड़ी को ऊँचा score देगा या नीचा, और क्या वह नतीजा prediction की गुणवत्ता का सही प्रतिबिंब है?

<details markdown="1"><summary>जाँचें</summary>

नीचा, क्योंकि दोनों वाक्य मूल रूप से एक ही बात दूसरे शब्दों में कहने के बावजूद बहुत कम लगातार n-grams साझा करते हैं। यह गुणवत्ता का सही प्रतिबिंब नहीं है: prediction वैध paraphrase है, पर ROUGE ऊपरी n-gram overlap मापता है, अर्थ नहीं, इसलिए reference से अलग ढंग से कहे गए सही उत्तर को वैसे ही दंडित किया जाता है जैसे ग़लत उत्तर को।

</details>

4. ▢ एक टीम किसी multiple-choice benchmark पर model परख रही है जिसमें हर सवाल का एक सही अक्षर है। इस पाठ की कौन-सी metric सबसे अच्छी बैठती है, और क्यों?

<details markdown="1"><summary>जाँचें</summary>

Exact match। Task में हर सवाल का ठीक एक सही उत्तर है और सोखने लायक कोई सार्थक ऊपरी भिन्नता नहीं (उत्तर एक अकेला अक्षर है), जो ठीक उसी तरह का task है जिसके लिए exact match बना है, और आंशिक या paraphrase किए overlap के लिए F1 या BLEU/ROUGE की उदारता की कोई ज़रूरत ही नहीं।

</details>

5. ▢ Exact match और F1 की तुलना में BLEU और ROUGE के बारे में कौन-सा दावा सही है?

    - a) उन्हें exact match की तरह एक अकेला, असंदिग्ध सही उत्तर चाहिए
    - b) वे reference text के विरुद्ध overlap को n-gram स्तर पर score करती हैं, जो खुले-सिरे वाली generation पर गुणवत्ता से सिर्फ़ ढीला correlate करता है
    - c) वे उस paraphrase की समस्या से मुक्त हैं जो exact match को प्रभावित करती है
    - d) किसी भी generation task पर उन्हें अंतिम फ़ैसले के रूप में सबसे अच्छी तरह इस्तेमाल किया जाता है, मानव या LLM निर्णय की जगह

<details markdown="1"><summary>जाँचें</summary>

**b)** N-gram overlap गुणवत्ता का ढीला proxy है, ख़ास तौर पर वहाँ जहाँ वैध उत्तर कई अलग तरह से कहे जा सकते हों। (a) ग़लत है: वे खुले-सिरे वाले text के tasks के लिए बनी हैं, किसी एक तय उत्तर के लिए नहीं। (c) ग़लत है: वैध paraphrase BLEU/ROUGE पर उसी मूल कारण से कम score पा सकता है जिससे वह exact match में विफल हो सकता है, यानी अलग ऊपरी शब्दावली। (d) ग़लत है: खुले-सिरे वाले text पर मानव निर्णय से उनका कमज़ोर correlation ही वह कारण है जिससे चरण 3 विकल्प के रूप में LLM-as-judge लाता है।

</details>

## असली दुनिया का अभ्यास

- [ ] कोई ऐसा task चुनें जिसे आप परखते हैं (या परखने की योजना है) और तय करें कि exact match, F1 या BLEU/ROUGE में से कौन-सी उसके "सही" के विचार पर बैठती है, और क्यों, यह लिखें।
- [ ] जिस eval में अभी BLEU या ROUGE इस्तेमाल होती है, उसमें ऐसा एक example खोजें जहाँ साफ़ तौर पर सही, पर अलग शब्दों में कहा गया उत्तर कम score पाता, और उसे दर्ज करें।
- [ ] कल: Hugging Face Evaluate दस्तावेज़ों में ऐसी metric का एक अनुच्छेद पढ़ें जिसे आपने पहले इस्तेमाल नहीं किया, और उसकी बताई विफलता का तरीक़ा लिखें।

## आगे बढ़ने के लिए

- [दस्तावेज़: Evaluate, Hugging Face](https://huggingface.co/docs/evaluate/index)
- [दस्तावेज़: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
