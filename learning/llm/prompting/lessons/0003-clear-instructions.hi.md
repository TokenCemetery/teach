---
title: "3. स्पष्ट Instructions"
description: "ऐसा instruction लिखें जिसे कोई सक्षम नया व्यक्ति follow कर सके: context, task, constraints, और पूरा होना कैसा दिखता है"
type: lesson
---

# पाठ 3. स्पष्ट Instructions

**मिशन से संबंध:** जो ज़्यादातर prompts नाकाम होते हैं, उनमें model को छला या उलझाया नहीं गया होता, बल्कि request अधूरी बताई गई होती है। इसलिए किसी भी prompt में सबसे सस्ता सुधार यह है कि वह लिखा जाए जो किसी सक्षम अजनबी को जानना ज़रूरी होगा।
**मुख्य स्रोत:** [Docs: "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#be-clear-and-direct)
**पूर्व-आवश्यकताएँ:** [पाठ 2](0002-system-prompts-and-roles.md), [Zero-shot prompt](../GLOSSARY.md)

## वार्म-अप

1. ▢ एक पंक्ति कहती है "Reply in at most three sentences." यह system prompt में जाती है या user turn में, और क्यों?

<details markdown="1"><summary>जाँचें</summary>

System prompt में, क्योंकि उसे हर request पर लागू रहना चाहिए, सिर्फ़ इसी पर नहीं।

</details>

2. ▢ किसी chat का rendered prompt assistant के role marker पर ख़त्म होता है। वहाँ से model क्या करता है?

<details markdown="1"><summary>जाँचें</summary>

वह उस बिंदु से token sequence को आगे बढ़ाता है, और reply इसी तरह लिखता है।

</details>

## यह जानें

### सहकर्मी वाली कसौटी

Anthropic की गाइड कहती है कि model को एक होशियार लेकिन नए कर्मचारी की तरह सोचें, जिसे आपके नियमों और workflows का context नहीं पता। उसका सुनहरा नियम: अपना prompt किसी ऐसे सहकर्मी को दिखाएँ जिसे task का बहुत कम context हो और उससे उसे follow करने को कहें। अगर वह उलझ जाएगा, तो model भी उलझेगा।

Model पूछ नहीं सकता कि आपका मतलब क्या था, इसलिए जो कुछ आप छोड़ देते हैं उसे वह अंदाज़े से भरता है। गाइड यह भी कहती है कि अगर आप "उम्मीद से बढ़कर" व्यवहार चाहते हैं, तो उसे साफ़ माँगें, यह भरोसा न करें कि model अस्पष्ट prompt से उसका अनुमान लगा लेगा।

### स्पष्ट instruction के चार हिस्से

| हिस्सा | जवाब देता है | उदाहरण |
|---|---|---|
| Context | यह किसके लिए है, और क्यों मायने रखता है? | "These summaries go to busy support managers who read on their phones." |
| Task | ठीक-ठीक क्या करना है? | "Summarise the ticket below." |
| Constraints | कौन-सी सीमाएँ लागू हैं? | "At most 40 words. No customer names." |
| पूरा होना कैसा दिखता है | कैसे पता चलेगा कि यह काम कर गया? | "A manager can decide whether to open the ticket from the summary alone." |

Anthropic की गाइड कहती है कि instruction के पीछे की वजह बताना, जैसे कोई व्यवहार क्यों मायने रखता है, model को ज़्यादा सटीक जवाब देने में मदद कर सकता है। Google की prompt design मार्गदर्शिका भी constraints और response format को उन चीज़ों में गिनाती है जो बतानी चाहिए। "पूरा होना कैसा दिखता है" वह हिस्सा है जो सबसे अक्सर छूटता है, और यही वह हिस्सा भी है जिसकी आपको बाद में ज़रूरत पड़ेगी जब आप prompt के बदलाव को regression set पर परखेंगे।

### बताएँ क्या करना है, और जो चरण क्रम से होने हैं उन्हें गिनकर लिखें

Anthropic की गाइड सलाह देती है कि model को बताएँ कि क्या करना है, यह नहीं कि क्या नहीं करना: "Do not use markdown" के बजाय लिखें "Your response should be composed of smoothly flowing prose paragraphs." जब चरणों का क्रम या पूर्णता मायने रखती हो, तो वह क्रम से गिने हुए चरणों का भी सुझाव देती है।

### पहले और बाद का एक उदाहरण

```text
Summarise this ticket.
```

```text
You are helping a support team triage tickets. The summaries are read by managers on their phones, who decide from the summary alone whether to open the ticket.
Summarise the ticket below in at most 40 words, in plain prose, leaving out customer names. State the problem first and the customer's requested outcome last.
```

दूसरा prompt इसलिए लंबा है क्योंकि उसमें context, constraints और उद्देश्य हैं। उसकी बढ़ी हुई लंबाई जानकारी है, सजावट नहीं।

## अभ्यास

1. ▢ इस पाठ के स्पष्ट instruction के चार हिस्सों के नाम बताएँ, और prompt "Write a product description." के लिए बताएँ कि कौन-से छूटे हैं।

<details markdown="1"><summary>जाँचें</summary>

Context, task, constraints, और पूरा होना कैसा दिखता है। इस prompt में सिर्फ़ एक task है, और वह भी अस्पष्ट। छूटे हुए हैं: description किसके लिए है और कहाँ दिखेगा, उसकी लंबाई और tone की सीमाएँ, और वह मानक जिस पर उसे खरा उतरना है।

</details>

2. ▢ "Don't write long answers." को इस तरह दोबारा लिखें कि वह model को बताए कि इसके बजाय क्या करना है।

<details markdown="1"><summary>जाँचें</summary>

उदाहरण के लिए: "Answer in two or three sentences." यह वांछित व्यवहार का नाम लेता है और मापने लायक सीमा देता है, जिससे उसे जाँचा भी जा सकता है। नकारात्मक instruction बताता है कि क्या टालना है, पर विकल्प का अंदाज़ा model पर छोड़ देता है।

</details>

3. ▢ "Make this email better" का कौन-सा नया रूप सबसे स्पष्ट है?

    - a) Improve this email so that it reads more professionally, clearly and persuasively overall
    - b) Rewrite this email for an upset customer in under 120 words, apologising first
    - c) Fix any problems in this email and make it sound good to the reader
    - d) Edit this email as an expert writer would, with attention to quality

<details markdown="1"><summary>जाँचें</summary>

**b)** यह audience, लंबाई की सीमा और क्रम की शर्त बताता है, इसलिए कोई और नतीजा जाँच सकता है। (a), (c) और (d) "better" को दूसरे शब्दों में दोहराते हैं, यह बताए बिना कि बेहतर का मतलब क्या है।

</details>

4. ▢ पहले अनुमान लगाएँ, फिर चलाएँ। कोई ऐसा task चुनें जो आप अक्सर करते हैं, जैसे "Write a short bio." Prompt को पाँच शब्दों में लिखकर भेजें। अनुमान लगाएँ कि आपके मक़सद के लिए reply तीन चीज़ें क्या ग़लत करेगा, फिर prompt को चारों हिस्सों के साथ दोबारा लिखकर फिर भेजें। आपके तीन अनुमानों में से कौन-से सुधरे, और कौन-सी ऐसी समस्याएँ दिखीं जिनका आपने अनुमान नहीं लगाया था?

<details markdown="1"><summary>संकेत</summary>

पाँच शब्दों वाला prompt पहले किसी सहकर्मी को दें। वह जो कुछ आपसे पूछेगा, वही model अंदाज़े से भर रहा है।

</details>

<details markdown="1"><summary>जाँचें</summary>

आम नतीजे: पहला reply audience, लंबाई और tone का अंदाज़ा लगाता है। दूसरा उन अंदाज़ों को हटाता है, लेकिन कोई नई समस्या जोड़ सकता है, अक्सर कोई ऐसा constraint जो किसी दूसरे से टकराता है। दोनों replies रखें: उनके बीच का अंतर पहली तुलना है जो आप किसी को दिखा सकते हैं, और पाठ 18 उस आदत को regression set में बदलता है।

</details>

## असली दुनिया का अभ्यास

- [ ] इस हफ़्ते भेजा हुआ कोई एक prompt लें जिसका reply निराशाजनक रहा और चिह्नित करें कि context, task, constraints और पूरा-होना-कैसा-दिखता-है में से उसमें क्या कमी थी।
- [ ] अपना लिखा कोई prompt ऐसे सहकर्मी को दें जिसे कोई पृष्ठभूमि नहीं पता और पूछें कि उसे क्या अंदाज़े से भरना पड़ता। हर अंदाज़े के लिए एक पंक्ति जोड़ें।
- [ ] कल: जो prompt आप इस्तेमाल करते हैं उसमें एक "मत करो" को सकारात्मक instruction से बदलें और उसी input पर replies की तुलना करें।

## आगे बढ़ने के लिए

- [Docs: "Prompt design strategies", Gemini API, Google](https://ai.google.dev/gemini-api/docs/prompting-strategies): constraints और response format पर दूसरे vendor की मार्गदर्शिका।
- [Prompt Anatomy](../reference/prompt-anatomy.md)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
