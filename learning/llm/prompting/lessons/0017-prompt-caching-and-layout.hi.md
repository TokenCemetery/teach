---
title: "17. Prompt Caching और Layout"
description: Prompt को स्थिर हिस्सों को पहले रखकर क्रम दें ताकि provider prefix को cache कर सके
type: lesson
---

# पाठ 17. Prompt Caching और Layout

**मिशन से संबंध:** जो prompt template अपना स्थिर text पहले रखता है, वह provider को हर call पर उसे दोबारा process करने से बचने देता है। इसलिए layout लागत और latency का फ़ैसला है जो template में लिया जाता है, बाद की सोच नहीं।
**मुख्य स्रोत:** [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
**पूर्व-आवश्यकताएँ:** [पाठ 16](0016-versioning-prompts.md), [Prompt caching](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 13 ने बताया था कि एक prompt में लंबा document और सवाल कहाँ जाते हैं। कौन पहले आता है, और क्या वह क्रम caching के लिए स्थिर content को पहले रखने से मेल खाता है?

<details markdown="1"><summary>जाँचें</summary>

लंबे documents पहले और सवाल आख़िर में। यह मेल खाता है: requests के बीच दोबारा इस्तेमाल होने वाला document स्थिर है, और सवाल हर बार बदलता है, इसलिए दोनों लक्ष्य एक ही ओर इशारा करते हैं।

</details>

2. ▢ पाठ 15 के template में स्थिर text और slots हैं। दोनों में से कौन cached prefix का उम्मीदवार है, और कौन कभी नहीं हो सकता?

<details markdown="1"><summary>जाँचें</summary>

स्थिर text उम्मीदवार है, क्योंकि वह हर call पर एक जैसा है। हर request के slot मान बदलते हैं, इसलिए जिसमें भी कोई एक हो वह दोबारा इस्तेमाल होने वाले prefix का हिस्सा नहीं हो सकता।

</details>

## यह जानें

### Prefix ही cache होता है

**Prompt caching** prompt के prefix की processed state को सहेजता है ताकि वही सटीक prefix साझा करने वाली बाद की call उसे दोबारा compute करना छोड़ दे। Anthropic का दस्तावेज़ अपना version बताता है: cached prefix पूरी request को एक तय क्रम में कवर करता है, `tools`, फिर `system`, फिर `messages`, `cache_control` से चिह्नित block तक और उसे मिलाकर। Cache entry के पीछे का hash संचयी होता है, इसलिए चिह्नित block पर या उससे पहले के किसी भी block को बदलने से अगली request पर अलग hash बनता है, और entry मेल नहीं खाती।

दूसरे providers caching अलग तरह से लागू करते हैं, इसलिए उनके नियम जाँचें। यहाँ का सिद्धांत, दोबारा इस्तेमाल होने वाला सटीक prefix, वह हिस्सा है जो साथ ले जाना है।

### Layout इसी से निकलता है

जो कभी नहीं बदलता उसे पहले और जो हर request पर बदलता है उसे आख़िर में रखें: tool definitions, फिर system prompt, फिर लंबे documents और few-shot examples, फिर हर request का सवाल। दस्तावेज़ कहता है कि स्थिर content को शुरुआत में रखें और दोबारा इस्तेमाल होने वाले हिस्से का अंत चिह्नित करें।

```python
def build_request(system: str, documents: str, question: str) -> dict:
    return {
        "system": system,
        "messages": [
            {
                "role": "user",
                "content": [
                    # stable: the end of this block is where a cache marker goes
                    {"type": "text", "text": documents},
                    # per request: after the marker, never part of the prefix
                    {"type": "text", "text": question},
                ],
            },
        ],
    }
```

यहाँ `documents` calls के बीच साझा है और `question` नहीं, इसलिए साझा text आगे रहता है, और वे अलग blocks हैं ताकि marker documents के बाद और सवाल से पहले बैठ सके। Anthropic के API में वह marker documents block पर `cache_control` field है, इस sketch का दूसरा vendor-विशिष्ट हिस्सा। दस्तावेज़ की अपनी ग़लती का उदाहरण वह block है जिसमें timestamp और user message है, और जिस पर cache marker लगा है: prefix का hash timestamp को शामिल करता है, इसलिए हर request एक नई entry लिखती है और कभी कोई पढ़ती नहीं। Timestamp, request ID या user का नाम स्थिर हिस्से से बाहर रखें। Anthropic का सुधार marker को उस आख़िरी block पर रखना है जो requests के बीच एक जैसा है।

### क्या hit तोड़ता है, और सीमाएँ

- Model के न्यूनतम से छोटा prefix cache नहीं होता, और कोई त्रुटि नहीं लौटती। दस्तावेज़ में दर्ज न्यूनतम model पर निर्भर करता है और 512 से 4,096 tokens तक है। अगर response के usage में `cache_creation_input_tokens` और `cache_read_input_tokens` दोनों 0 हैं, तो prompt cache नहीं हुआ।
- Tool definitions बदलना पूरे cache को अमान्य कर देता है। दस्तावेज़ की invalidation table tool-choice setting, images और कुछ thinking और effort settings के बदलावों को भी गिनाती है, जो messages वाले हिस्से को अमान्य करते हैं।
- डिफ़ॉल्ट जीवनकाल 5 मिनट है, जो entry पढ़े जाने पर हर बार ताज़ा होता है। अतिरिक्त लागत पर 1 घंटे का विकल्प भी है।
- Cache entry पहला response शुरू होने के बाद ही उपलब्ध होती है, इसलिए parallel पहली requests उसे साझा नहीं करतीं। Concurrent और agent workloads के लिए, [agents track का पाठ 34](../../agents/lessons/0034-prompt-caching-and-concurrency.md) देखें।

Reads बिना cache वाले input से सस्ते हैं और writes महँगे: दस्तावेज़ 5-मिनट के writes को base input कीमत के 1.25 गुना और reads को 0.1 गुना बताता है, reads पर हर model के अपवादों के साथ। इसलिए जो layout कभी hit नहीं करता वह caching न होने से थोड़ा ज़्यादा महँगा पड़ता है।

## अभ्यास

1. ▢ एक template `Current time: {now}` से शुरू होता है, फिर 3,000-token की style guide, फिर उपयोगकर्ता का सवाल। Caching उसकी कभी मदद क्यों नहीं करती, और सुधार क्या है?

<details markdown="1"><summary>जाँचें</summary>

Timestamp पहला block है, इसलिए prefix का hash हर request पर बदलता है और कोई बाद वाला block cache से नहीं पढ़ा जा सकता। Style guide और बाक़ी स्थिर text को timestamp से पहले ले जाएँ, या अगर task को timestamp की ज़रूरत नहीं तो उसे prompt से हटा दें, और सवाल आख़िर में रखें।

</details>

2. ▢ पहली request: `cache_read_input_tokens` 0 है, `cache_creation_input_tokens` 2,400 है, `input_tokens` 60 है। दूसरी request, वही prefix, 75-token का सवाल: अगर caching काम करे तो तीनों fields क्या दिखाते हैं, और कुल input क्या है?

<details markdown="1"><summary>संकेत</summary>

दस्तावेज़ कहता है कि `input_tokens` सिर्फ़ आख़िरी cache breakpoint के बाद आने वाली चीज़ों को गिनता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

`cache_read_input_tokens` 2,400 है, `cache_creation_input_tokens` 0 है और `input_tokens` 75 है। कुल input उनका योग, 2,475 tokens है। Prefix दोबारा लिखे जाने के बजाय cache से पढ़ा गया, और सिर्फ़ नया सवाल ताज़ा process हुआ।

</details>

3. ▢ एक टीम ऐसे model पर 600-token का system prompt जोड़ती है जिसका न्यूनतम 1,024 tokens है, उसे caching के लिए चिह्नित करती है, और दोनों usage counters 0 देखती है। क्या हुआ, और क्या कुछ टूटा है?

<details markdown="1"><summary>जाँचें</summary>

Prompt न्यूनतम से कम है, इसलिए वह बिना caching के process हुआ और कोई त्रुटि नहीं लौटी। कुछ टूटा नहीं है। न्यूनतम तक पहुँचने के लिए और स्थिर content, जैसे examples, जोड़ें, या बिना cache वाली calls स्वीकार करें।

</details>

4. ▢ किसी support bot को cache करने के लिए कौन-सा prompt layout सबसे अच्छा है जो एक लंबे policy document के बारे में कई सवालों के जवाब देता है?

    - a) सवाल, फिर policy document, फिर system prompt
    - b) System prompt, फिर सवाल, फिर policy document
    - c) System prompt, फिर policy document, फिर सवाल
    - d) System prompt, फिर उपयोगकर्ता का नाम, फिर policy document

<details markdown="1"><summary>जाँचें</summary>

**c)** System prompt और document requests के बीच एक जैसे हैं और आगे रहते हैं, और सवाल आख़िर में आता है। (a) और (b) बदलते सवाल को स्थिर text से आगे रखते हैं, इसलिए prefix हर call पर अलग होता है। (d) document से आगे हर-उपयोगकर्ता का मान रखता है, जो हर अलग उपयोगकर्ता के लिए साझा prefix को तोड़ देता है।

</details>

## असली दुनिया का अभ्यास

- [ ] अपना कोई prompt लें जो आप चलाते हैं और हर हिस्से को स्थिर, रोज़ बदलने वाला, या हर request पर बदलने वाला चिह्नित करें, फिर जाँचें कि स्थिर हिस्से पहले बैठे हैं।
- [ ] ऐसे provider पर, जो cache usage बताता है, एक call वही prefix रखकर दो बार करें और दोनों calls के counters पढ़ें।
- [ ] कल: prompt के स्थिर क्षेत्र के भीतर कोई भी timestamp, ID या नाम खोजें और उसे अंत में ले जाएँ।

## आगे बढ़ने के लिए

- [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [agents track का पाठ 34: Prompt Caching और Concurrency](../../agents/lessons/0034-prompt-caching-and-concurrency.md)
- [Production में Prompts](../reference/prompts-in-production.md)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
