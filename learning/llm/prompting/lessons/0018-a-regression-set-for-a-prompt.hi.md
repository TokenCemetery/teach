---
title: "18. Prompt के लिए Regression Set"
description: उन cases का छोटा सेट बनाएँ जिन्हें prompt का बदलाव तोड़ना नहीं चाहिए, असली विफलताओं से शुरू करके
type: lesson
---

# पाठ 18. Prompt के लिए Regression Set

**मिशन से संबंध:** Prompt का बदलाव एक दावा है, और regression set वह चीज़ है जो दावे को सेकंडों में जाँचने देती है, बजाय उन तीन outputs से परखने के जो आपने संयोग से पढ़ लिए।
**मुख्य स्रोत:** [Article: "Your AI Product Needs Evals", Hamel Husain](https://hamel.dev/blog/posts/evals/)
**पूर्व-आवश्यकताएँ:** [पाठ 17](0017-prompt-caching-and-layout.md), [Regression set](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 11 ने structured output माँगा और फिर उसे validate किया। Validity की जाँच regression set में स्वाभाविक पहला assertion क्यों है?

<details markdown="1"><summary>जाँचें</summary>

Format माँगना गारंटी नहीं है, इसलिए output parse होने में विफल हो सकता है। Parse या schema की जाँच सस्ती है, किसी निर्णय की ज़रूरत नहीं रखती और हर case पर चलती है, जिससे वह ऐसा assertion बनती है जिसे लिखना आसान है।

</details>

2. ▢ पाठ 5 ने दिखाया था कि बिना अर्थ वाला formatting edit accuracy बदल सकता है। इससे यह कैसे निकलता है कि कुछ outputs पढ़कर आप prompt के बदलाव का कितना हिस्सा परख सकते हैं?

<details markdown="1"><summary>जाँचें</summary>

बहुत कम। छोटा edit नतीजों को ऐसे तरीक़ों से खिसका सकता है जो मुट्ठी भर outputs नहीं दिखाएँगे, इसलिए बदलाव को cases के एक तय सेट पर चलाकर गिनना होगा।

</details>

## यह जानें

### उन विफलताओं से शुरू करें जो आप पहले देख चुके हैं

**Regression set** inputs का एक तय सेट है, हर एक के output पर एक जाँच के साथ, जिसे prompt का बदलाव तोड़ना नहीं चाहिए। सबसे अच्छे पहले cases असली होते हैं। Hamel Husain का real-estate assistant के लिए evals बनाने का वृत्तांत कहता है कि जब आप assertions न सोच पाएँ तो traces और विफलता के तरीक़ों को आलोचनात्मक नज़र से देखें, और कि टीम के सैकड़ों unit tests data में दिखी नई विफलताओं से लगातार अपडेट होते थे। Trace एक log की हुई बातचीत है, इसलिए उन्हें log करें, पढ़ें, और हर विफलता को एक case में बदलें: वह input जिसने उसे चलाया और वह जाँच जो उसे पकड़ लेती।

Evaluations बनाने पर Anthropic की गाइड लक्ष्य पर सहमत है: ऐसे tests डिज़ाइन करें जो आपके असली task के distribution की नक़ल करें, edge cases शामिल करें, और जहाँ हो सके grading को automate करें। शुरुआत के लिए production traffic ज़रूरी नहीं। Hamel नोट करते हैं कि आप समझदार अंदाज़े लिख सकते हैं, या model से inputs बनवा सकते हैं, और शुरुआती उपयोगकर्ताओं को उन्हें निखारने दे सकते हैं।

### हर गुण के लिए एक assertion

Hamel जाँचों को assertions बताते हैं, जैसे आप pytest में लिखते, तेज़ और सस्ते ताकि हर बदलाव पर चल सकें। हर case उन गुणों की सूची देता है जो उसके output में होने चाहिए।

```python
CASES = [
    {"id": "refund-not-complaint", "ticket": "I want my money back for order 118.",
     "must_contain": ["refund"], "must_not_contain": ["complaint"]},
    {"id": "no-uuid", "ticket": "Account 3f2b8c1e-9d4a-4e7b-a1c2-5d6e7f8a9b0c is locked.",
     "must_contain": [], "must_not_contain": ["3f2b8c1e"]},
]


def run_case(case: dict, call_model) -> bool:
    output = call_model(case["ticket"]).lower()
    has_all = all(s in output for s in case["must_contain"])
    has_none = not any(s in output for s in case["must_not_contain"])
    return has_all and has_none


def run_set(call_model) -> dict:
    return {c["id"]: run_case(c, call_model) for c in CASES}
```

`call_model` पाठ 15 का template render करता है, पाठ 16 का pin किया हुआ model call करता है और उसका text लौटाता है। Hamel का अपना उदाहरण ऐसी ही जाँच है कि output कभी किसी आंतरिक UUID को उजागर न करे। जहाँ कोई गुण string या regex test नहीं बन सकता, वहाँ model उसे grade कर सकता है, और evals track बताता है कि उस grader पर कब भरोसा करें।

### छोटा, बढ़ता हुआ और सब-या-कुछ-नहीं नहीं

सामने मौजूद मुट्ठी भर विफलताओं से शुरू करें और जब भी नई विफलता दिखे एक case जोड़ें। सेट उन विफलताओं का प्रतिनिधि होना चाहिए जिनकी आपको परवाह है, अपने-आप में बड़ा नहीं: Anthropic की गाइड हाथ से graded गुणवत्ता से ज़्यादा मात्रा को तरजीह देती है, और Hamel की टीम सैकड़ों tests तक पहुँची, इसलिए छोटा वहाँ से शुरू होता है, लक्ष्य नहीं है। Hamel की दो सावधानियाँ: अच्छे सेट में ऐसे cases होते हैं जिनसे model जूझता है, और सामान्य unit tests के उलट आपको ज़रूरी नहीं कि 100% pass rate चाहिए, क्योंकि pass rate इस बारे में product का फ़ैसला है कि आप कौन-सी विफलताएँ बर्दाश्त करते हैं। नतीजों को prompt version के साथ ट्रैक करें ताकि आप देख सकें कि प्रगति हो रही है या नहीं।

## अभ्यास

1. ▢ एक उपयोगकर्ता बताता है कि summariser refund request को "complaint" कहता है। उस रिपोर्ट को एक case में बदलें: input में क्या जाता है, और output को किन assertions की ज़रूरत है?

<details markdown="1"><summary>जाँचें</summary>

Input उपयोगकर्ता का असली ticket text है, या उसके क़रीब का। Assertions हैं refund शब्द `must_contain` और complaint शब्द `must_not_contain`, जैसे ऊपर के `refund-not-complaint` case में। Case अब पुराने prompt पर विफल होता है और सुधार पर pass होता है।

</details>

2. ▢ `no-uuid` case के लिए `run_case` का अनुमान लगाएँ जब model `Account 3f2b8c1e is locked.` output देता है।

<details markdown="1"><summary>संकेत</summary>

Output की तुलना अकेली `must_not_contain` string से करें।

</details>

<details markdown="1"><summary>जाँचें</summary>

यह `False` लौटाता है। `must_contain` ख़ाली है, इसलिए `has_all` सही है, पर output में `3f2b8c1e` है, इसलिए `has_none` ग़लत है और case विफल होता है। Prompt ने ID का हिस्सा लीक कर दिया।

</details>

3. ▢ एक साथी regression set बनाने से पहले 500 production-गुणवत्ता वाले cases होने तक रुकना चाहता है। इस पाठ के स्रोतों के आधार पर इसमें क्या ग़लत है?

<details markdown="1"><summary>जाँचें</summary>

तब तक कुछ चलता नहीं, इसलिए इस बीच के बदलाव अंदाज़े से परखे जाते हैं। स्रोत उन सेटों का वर्णन करते हैं जो देखी गई विफलताओं से बढ़े, और Hamel कहते हैं कि आप समझदार अंदाज़ों से शुरू कर सकते हैं। जो विफलताएँ आपके पास हैं उनसे शुरू करें और नई दिखने पर cases जोड़ें।

</details>

4. ▢ एक regression set मौजूदा prompt पर 20 में से 18 cases pass करता है और टीम किसी भी release से पहले 20 में से 20 पर अड़ी है। कौन-सा नज़रिया Hamel के लेख से मेल खाता है?

    - a) Pass rate बर्दाश्त की गई विफलताओं के बारे में product का फ़ैसला है, इसलिए 100% ज़रूरी नहीं
    - b) हर case को pass होना चाहिए वरना ship करने से पहले gate के रूप में सेट बेकार है
    - c) विफल दोनों cases हटा देने चाहिए ताकि सेट मौजूदा prompt को दर्शाए
    - d) Pass rate से कम मायने cases की संख्या रखती है, जिसे हमेशा न्यूनतम रखना चाहिए

<details markdown="1"><summary>जाँचें</summary>

**a)** Hamel कहते हैं कि आपको ज़रूरी नहीं कि 100% pass rate चाहिए और वह इस पर निर्भर है कि आप कौन-सी विफलताएँ बर्दाश्त करेंगे। (b) वह सामान्य unit-test की आदत है जिससे वे इसकी तुलना करते हैं। (c) उन विफलताओं को हटा देता है जिन्हें याद रखने के लिए सेट मौजूद है। (d) उलटा है: सेट सिर्फ़ शुरुआती बिंदु के रूप में छोटा है।

</details>

## असली दुनिया का अभ्यास

- [ ] अपने चलाए किसी prompt की पाँच असली या यथार्थवादी विफलताएँ, logs, bug रिपोर्टों या अपनी जाँच से निकालें, और हर एक को एक input और एक assertion के रूप में लिखें।
- [ ] उन पाँच cases को repository में prompt के बगल की file में रखें और मौजूदा prompt पर चलाएँ, यह नोट करते हुए कि कौन pass होते हैं।
- [ ] कल: अगली बार जब prompt ख़राब output दे, तो prompt ठीक करने से पहले उसे case के रूप में जोड़ें, और पुष्टि करें कि वह पहले विफल होता है।

## आगे बढ़ने के लिए

- [Article: "Your AI Product Needs Evals", Hamel Husain](https://hamel.dev/blog/posts/evals/)
- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Production में Prompts](../reference/prompts-in-production.md)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
