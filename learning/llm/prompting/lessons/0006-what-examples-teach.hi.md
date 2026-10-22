---
title: "6. Few-Shot Examples क्या सिखाते हैं"
description: Demonstrations ज़्यादातर format, label space और input distribution सिखाते हैं, जिससे उन्हें चुनने का तरीक़ा बदल जाता है
type: lesson
---

# पाठ 6. Few-Shot Examples क्या सिखाते हैं

**मिशन से संबंध:** Few-shot examples अच्छे से चुनने की शुरुआत इस जानकारी से होती है कि model उनसे क्या लेता है, और प्रमाण कहते हैं कि वह उत्तरों से कम, task के आकार से ज़्यादा लेता है।
**मुख्य स्रोत:** [Paper: "Rethinking the Role of Demonstrations", Min et al., 2022](https://arxiv.org/abs/2202.12837)
**पूर्व-आवश्यकताएँ:** [पाठ 5](0005-format-sensitivity.md), [Few-shot prompt](../GLOSSARY.md), [Zero-shot prompt](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 4 ने instructions को data से tags के ज़रिए अलग किया था। Few-shot prompt में एक ऐसी चीज़ का नाम बताएँ जिसे अपने ही tag के भीतर होना चाहिए, और क्यों।

<details markdown="1"><summary>जाँचें</summary>

Examples, जो एक साथ लपेटे गए हों (उदाहरण के लिए examples tag में, हर example के लिए एक tag के साथ), ताकि model demonstrations को instructions से और असली input से अलग पहचान सके। Tags के बिना, एक example को instruction की तरह पढ़ा जा सकता है, या असली input को एक और example की तरह।

</details>

2. ▢ पाठ 5 ने कहा था कि बिना अर्थ वाला formatting बदलाव accuracy हिला सकता है। यह उन दो few-shot prompts के बारे में क्या भविष्यवाणी करता है जिनके examples एक जैसे हैं पर एक में `Label:` लिखा है और दूसरे में `Answer:`?

<details markdown="1"><summary>जाँचें</summary>

कि उनकी accuracy अलग हो सकती है, इसलिए दोनों को परखे बिना यह नहीं पता कि कौन बेहतर है। Edit से कोई अर्थ नहीं बदलता, फिर भी वह उस token sequence को बदल देता है जिसे model आगे बढ़ाता है, और यही पाठ 5 का मुद्दा है।

</details>

## यह जानें

### चौंकाने वाला नतीजा

**Few-shot prompt** असली input से पहले model को input और output की जोड़ियाँ दिखाता है। सीधा अंदाज़ा यह है कि model उनसे input से output का मैपिंग सीखता है, जैसे classifier labelled data से सीखता है। Min et al. ने इस अंदाज़े को परखा, demonstrations के labels को random labels से बदलकर। GPT-3 समेत 12 models में, performance लगभग नहीं गिरा: लगभग सभी models के लिए 0 से 5% absolute, classification tasks में औसतन 2.6% और multi-choice tasks में 1.7%।

अगर सही labels मदद नहीं कर रहे, तो demonstrations में कुछ और मदद कर रहा होगा। पेपर तीन चीज़ों के नाम लेता है, और हर एक को हटाकर परखा गया:

| Demonstration क्या देता है | हटाने पर क्या होता है |
|---|---|
| Label space: उत्तरों का वह सेट जो model दे सकता है | Labels को random अंग्रेज़ी शब्दों से बदलने पर direct models के लिए 5 से 16% absolute का नुक़सान हुआ |
| Input distribution: ऐसा text जो असली inputs जैसा दिखे | Inputs को random corpus text से बदलने पर परखे गए ज़्यादातर models के लिए 3 से 16% absolute का नुक़सान हुआ |
| Format: input फिर label, दोहराया हुआ | जोड़ी बनाना छोड़ने पर performance बिना demonstrations के क़रीब या उससे बदतर रहा |

### यह क्या नहीं कहता

तीन सीमाएँ इसे "labels मायने नहीं रखते" बनने से रोकती हैं।

Models GPT-2 Large से GPT-3 तक थे (774M से 175B parameters), और tasks classification और multi-choice थे। पेपर यह नहीं परखता कि आज का कोई chat model भी इसी तरह व्यवहार करता है या नहीं, इसलिए इसे मज़बूत पूर्वधारणा मानें, फिर अपने model को परखें।

Random labels की भी कुछ क़ीमत रही, और वह एक जैसी नहीं थी: classification पर एक model लगभग 10% गिरा जब हर label ग़लत था। "बहुत कम नुक़सान" परखे गए models और tasks पर औसत है।

लेखक यह भी नोट करते हैं कि in-context learning ऐसे task पर शायद काम न करे जिसका input-label संबंध model पहले से नहीं पकड़ चुका। Demonstrations ऐसे task की जगह बताते हैं जिसे model ज़्यादातर कर सकता है। जो मैपिंग उसने कभी नहीं देखी, उसे सिखाने का यह कमज़ोर तरीक़ा है।

### इससे examples चुनना कैसे बदलता है

अगर model examples से format, label space और input distribution पढ़ता है, तो यही तीन सही करने हैं।

- **Target format में।** हर example बिलकुल असली input और आपके चाहे output जैसा दिखे, casing और punctuation तक। पाठ 5 बताता है कि छोटे फ़र्क़ मुफ़्त क्यों नहीं हैं।
- **Label space को कवर करते हुए।** हर वह label दिखाएँ जो model दे सकता है, ताकि कोई चौंकाने वाला न रहे।
- **असली inputs जैसे।** असली distribution का text इस्तेमाल करें, साफ़-सुथरे गढ़े हुए वाक्य नहीं।

Anthropic की best-practices गाइड यही बात practitioner की भाषा में कहती है: examples प्रासंगिक बनाएँ (असली use case की नक़ल करें), विविध (edge cases कवर करें और इतना बदलें कि model अनचाहे patterns न पकड़े) और संरचित (tags में लपेटे हुए), और वह 3 से 5 examples का सुझाव देती है। यह एक vendor की दस्तावेज़ी सलाह है, मापा हुआ नतीजा नहीं।

इनमें से कुछ भी ग़लत labels ship करने की छूट नहीं है। सही labels की कोई क़ीमत नहीं और वे पेपर के सबसे बुरे मामले से बचाते हैं।

## अभ्यास

1. ▢ पहले अनुमान लगाएँ, फिर चलाएँ। यह prompt एक chat window में paste करें। तीनों examples के labels जान-बूझकर ग़लत हैं। अनुमान लगाएँ कि model आख़िरी review के लिए क्या output देगा, फिर चलाएँ।

    ```text
    Classify each review as Positive or Negative.

    Review: The battery lasts all day and the screen is gorgeous.
    Label: Negative

    Review: It stopped working after two days and support never replied.
    Label: Positive

    Review: Arrived on time and works exactly as described.
    Label: Negative

    Review: Terrible fit, the zipper broke on the first use.
    Label:
    ```

<details markdown="1"><summary>संकेत</summary>

पूछें कि labels ग़लत होने पर भी examples क्या सिखाते हैं: format, दो अनुमत शब्द, और review कैसा दिखता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

Min et al. अनुमत जोड़ी में से एक-शब्द के उत्तर की भविष्यवाणी करते हैं, और साफ़ review के लिए सबसे संभावित रूप से सही वाला (Negative), क्योंकि task की model की अपनी समझ ग़लत labels के बावजूद बची रहती है। जो model बदली हुई मैपिंग की नक़ल करे वह उस model के बारे में एक खोज है, पेपर में कोई ग़लती नहीं। दोनों सूरतों में output format (`Label:` के बाद एक शब्द) टिकना चाहिए, क्योंकि format ही वह चीज़ है जो examples ने भरोसे से सिखाई।

</details>

2. ▢ चलते हुए few-shot prompt में कौन-सा बदलाव पेपर के हिसाब से सबसे ज़्यादा नुक़सान करेगा?

    - a) Labels की अदला-बदली ताकि कुछ examples में ग़लत उत्तर हो
    - b) Example inputs को corpus के random वाक्यों से बदलना
    - c) उन्हीं examples का क्रम बदलना जबकि हर label सही रहे
    - d) एक और example जोड़ना जो मौजूदा format से मेल खाए

<details markdown="1"><summary>जाँचें</summary>

**b)** Inputs को distribution से बाहर के text से बदलने पर परखे गए ज़्यादातर models के लिए 3 से 16% absolute का नुक़सान हुआ, ग़लत labels से ज़्यादा (लगभग सभी के लिए 0 से 5%)। (a) पेपर की मुख्य खोज है: छोटी क़ीमत। (c) इस पेपर में नहीं परखा गया; क्रम पाठ 7 का विषय है, और वह हानिरहित नहीं है। (d) सही format में एक demonstration जोड़ता है, जिसके बारे में पेपर कहता है कि 8 के आसपास हो जाने के बाद नतीजे ज़्यादा नहीं बदलते।

</details>

3. ▢ यह prompt support tickets को tag करने के लिए है। हर वह तरीक़ा बताएँ जिससे इसके examples format, label space या input distribution सिखाने में नाकाम हैं, और बताएँ कि आप क्या बदलेंगे।

    ```text
    Tag the ticket as billing, bug or account.

    Ticket: I was charged twice this month.
    Tag: billing

    This one is a bug report: The export button does nothing.
    bug

    Ticket: How do I change my email address?
    Tag: Account.
    ```

<details markdown="1"><summary>संकेत</summary>

तीनों examples की पंक्ति-दर-पंक्ति तुलना करें। क्या उनका layout एक है? क्या label की spelling और punctuation एक है? Labels गिनें।

</details>

<details markdown="1"><summary>जाँचें</summary>

Format: दूसरा example `Ticket:` और `Tag:` छोड़ देता है और टिप्पणी वाला वाक्यांश जोड़ता है, इसलिए pattern एक बार टूटता है। Label space: `billing`, `bug` और `Account.` casing और punctuation में अलग हैं, इसलिए model तीन label spellings देखता है जबकि task में तीन सटीक labels हैं। पूर्ण विराम वाला label `Account.` सिखाता है कि punctuation उत्तर का हिस्सा है। Input distribution: tickets एक-एक छोटी पंक्ति के हैं और शायद असली tickets जैसे न दिखें (जो लंबे और बेतरतीब होते हैं)। सुधार: हर example के लिए एक layout, हर बार label की सटीक spelling, और tickets असली tickets से लिए हुए।

</details>

4. ▢ एक classifier को Billing, Bug, Account में से एक output देना है। इस पूल में से वे तीन examples चुनें जो आप इस्तेमाल करेंगे और बताएँ कि बाक़ी को क्यों ठुकराया।

    ```text
    A. "I was charged twice for May" -> Billing
    B. "Why did my card get billed two times in May??" -> Billing
    C. "app crashes when I tap export, iOS 17, v4.2" -> Bug
    D. "Our blog post explains how crashes can be diagnosed" -> Bug
    E. "can't log in after changing my phone number" -> Account
    F. "Please update the invoice address" -> Billing
    ```

<details markdown="1"><summary>जाँचें</summary>

एक उचित चुनाव A, C और E है: हर label के लिए एक example label space को कवर करता है, उनका layout एक है, और उनके खुरदरे, असली जैसे शब्द input distribution से मेल खाते हैं। B लगभग A की नक़ल है, इसलिए कोई विविधता नहीं जोड़ता। D सजी-सँवरी गद्य है जो ticket जैसी नहीं दिखती (input-distribution का बेमेल) और ग़लत वजह से Bug label की गई है। F अपने आप में ठीक है, पर किसी और label से पहले दूसरा Billing example उस bias का जोखिम लाता है जो पाठ 7 में है। दूसरे चुनाव भी उचित हैं अगर वे तीनों labels कवर करें और D से बचें।

</details>

## असली दुनिया का अभ्यास

- [ ] कोई few-shot prompt लें जो आप पहले से इस्तेमाल करते हैं। सूची बनाएँ कि हर example format, label space और input distribution में से क्या दिखाता है, और ऐसे हर example को चिह्नित करें जो इनमें से कुछ नहीं दिखाता।
- [ ] एक prompt को दो बार चलाएँ, एक बार असली examples के साथ और एक बार उन्हीं examples को random तरीक़े से दोबारा label करके, पाँच inputs पर। नोट करें कि कितने उत्तर बदले।
- [ ] कल: कोई एक few-shot prompt ऐसे दोबारा लिखें कि हर example का एक layout और label की सटीक spelling हो, फिर उसे उन्हीं पाँच inputs पर चलाएँ और तुलना करें।

## आगे बढ़ने के लिए

- [Few-Shot और Reasoning](../reference/few-shot-and-reasoning.md)
- [Paper: "Rethinking the Role of Demonstrations", Min et al., 2022](https://arxiv.org/abs/2202.12837)
- [Docs: "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#use-examples-effectively)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
