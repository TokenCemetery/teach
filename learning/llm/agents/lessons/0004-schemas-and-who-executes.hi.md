---
title: "4. Parameter Schemas और कौन क्या चलाता है"
description: JSON schemas model के भेज सकने वाले को कैसे सीमित करते हैं, और client tools तथा server tools का अंतर
type: lesson
---

# पाठ 4. Parameter Schemas और कौन क्या चलाता है

**मिशन से संबंध:** किसी दिए गए task के लिए agent loop लिखें, और बताएँ कि उसके context का हर message क्या कर रहा है और loop को क्या ख़त्म करता है।
**मुख्य स्रोत:** [दस्तावेज़: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
**पूर्व-आवश्यकताएँ:** [पाठ 3](0003-the-wire-format-of-a-tool-call.md)

## वार्म-अप

1. ▢ जब आप model provider को tool definition भेजते हैं, तो JSON schema की क्या भूमिका होती है?

<details markdown="1"><summary>जाँचें</summary>

वह बताता है कि tool कौन-से arguments लेता है: नाम, types और बंदिशें। Model schema देखकर तय करता है कि tool call करते समय क्या भेजना है। अच्छी तरह बना schema model को अमान्य या बिगड़े arguments भेजने से रोकता है।

</details>

2. ▢ जब model tool call करता है और harness को वह call मिलती है, तो harness कैसे जानता है कि उसे local में चलाना है या provider को भेजना है?

<details markdown="1"><summary>जाँचें</summary>

Tool define करते समय आपको harness को बताना होता है: उसे client tool चिह्नित करें (local में चलाएँ) या server tool (provider संभालता है)। Model को इसका फ़र्क़ कभी पता नहीं चलता; वह सिर्फ़ नाम और schema देखता है।

</details>

## यह जानें

### Guardrail के रूप में Schemas

JSON schema दो काम करता है। पहला, वह बताता है कि tool क्या अपेक्षा करता है: property के नाम, types, और हर property optional है या ज़रूरी। यह एक सरल उदाहरण है:

```json
{
  "type": "object",
  "properties": {
    "city": {"type": "string", "description": "The city name"},
    "units": {"type": "string", "enum": ["celsius", "fahrenheit"], "description": "Temperature scale"}
  },
  "required": ["city"]
}
```

यह schema कहता है: tool एक object लेता है जिसमें ज़रूरी `city` (string) और optional `units` ("celsius" या "fahrenheit" में से एक) है। Model इसे पढ़कर जानता है कि उसे city हमेशा देनी है पर units छोड़ सकता है।

दूसरा, schema बंदिश का काम करता है। जब model tool call करता है, तो वह सिर्फ़ वही मान भेज सकता है जो schema से मेल खाएँ। अगर schema कहता है कि `units` दो strings में से एक होना चाहिए, तो model "kelvin" या कोई संख्या नहीं भेज सकता। सख़्त schemas harness को validate किए बिना ही बिगड़ी calls की पूरी श्रेणियाँ रोक देते हैं।

### ज़रूरी fields छूटने पर क्या होता है

अगर model कोई ज़रूरी field छोड़ दे, तो provider की API error उठाती है। ज़्यादातर frameworks इसे पकड़कर error को tool result के रूप में model को वापस भेज देते हैं: "Error: missing required field 'city'"। फिर model को उसे सुधारने का मौक़ा मिलता है। यह crash नहीं है; यह loop का सामान्य हिस्सा है। अच्छी तरह बयान किया गया schema ऐसा होने की आवृत्ति घटाता है, क्योंकि model schema ध्यान से पढ़ता है।

### Client tools और server tools

**Client tool** आपके अपने code का वह function है जिसे harness चलाता है। Implementation आपकी है:

```python
def get_weather(city: str, units: str = "celsius"):
    # Your code to fetch weather
    return f"18{units[0]}, partly cloudy"
```

जब model `get_weather` call करता है, तो आपका harness आपका function चलाता है और नतीजा इकट्ठा करता है।

**Server tool** वह है जिसे provider अपने infrastructure पर चलाता है: web search, sandbox में code execution, file system access, या hosted API call। आप तय करते हैं कि वह क्या करता है (नाम और schema), पर implementation आप कभी नहीं लिखते। Provider उसे चलाता है, नतीजा इकट्ठा करता है, और harness उसे response से पढ़ता है।

### फ़र्क़ क्यों मायने रखता है

जब आप कहते हैं "model ने tool call किया," तो आप भाषा के साथ ढील बरत रहे हैं। Model कुछ भी execute नहीं करता। वह संरचित अनुरोध भेजता है जो कहता है "इस tool को इन arguments के साथ चलाओ।" Harness वह अनुरोध पाकर उसे चलाता है, इनमें से किसी तरह:

1. आपका लिखा function call करके (client tool), या
2. Provider से कुछ hosted चलवाकर (server tool), या
3. Network पर किसी तीसरे पक्ष की service को भेजकर।

Model को परवाह नहीं कि कौन-सा है। फ़र्क़ आपका है: वह तय करता है कि code कहाँ रहता है, उसे कैसे लिखना है, और विफलताएँ कहाँ हो सकती हैं।

### Loop के लिए यह क्यों मायने रखता है

Agent loop में model tool calls बनाता है और harness उन्हें चलाता है। अगर कोई tool फेल हो, तो नतीजा error लिए हुए tool result होता है, ऐसा exception नहीं जो loop को crash करे। यह तब भी सच है जब tool client हो या server:

- Client tool error लौटाता है क्योंकि network बंद था, database query फेल हुई, या आपके validation logic ने input ठुकरा दिया।
- Server tool error लौटाता है क्योंकि provider का sandbox timeout हो गया, code ने exception उठाया, या API की rate limit लग गई।

दोनों में error बस एक और tool result है, और model तय करता है कि आगे क्या करना है।

### Permissions और server tools

Server tool एक सवाल और जोड़ता है: क्या model को उसे call करने की अनुमति है? अगर आप model को code execution, file read या web access देते हैं, तो आप भरोसा कर रहे हैं (schema की तय सीमा के भीतर) कि वह उस क्षमता को सुरक्षित तरीक़े से इस्तेमाल करेगा। यह security का फ़ैसला है, तकनीकी नहीं। Schema तय करता है कि tool को कौन-से arguments मिल सकते हैं, पर schema model को उस क्षमता को ऐसे काम में लगाने से नहीं रोक सकता जो आपने नहीं चाहा था। इसीलिए tool-set का design मायने रखता है, और इसीलिए हर tool हर agent के लिए उपयुक्त नहीं होता।

## अभ्यास

1. ▢ एक tool schema में `query` field (string) ज़रूरी है पर `max_results` field define नहीं है। क्या model `max_results` argument भेज सकता है? क्यों या क्यों नहीं?

<details markdown="1"><summary>जाँचें</summary>

सख़्त schema में नहीं। JSON schema definitions अतिरिक्त properties की इजाज़त दे या मना कर सकती हैं। अगर schema `max_results` का ज़िक्र नहीं करता, तो model उसे नहीं भेज सकता (या provider उसे ठुकरा देगा)। Schema संपूर्ण है: सिर्फ़ सूचीबद्ध properties आ सकती हैं, जब तक schema अतिरिक्त properties की साफ़ इजाज़त न दे।

</details>

2. ▢ आपके पास database को query करने वाला client tool है। Schema कहता है `user_id` ज़रूरी है, पर model उसके बिना call भेजता है। आगे क्या होता है?

<details markdown="1"><summary>संकेत</summary>

जब provider बिगड़ी call ठुकराता है तो harness क्या करता है?

</details>

<details markdown="1"><summary>जाँचें</summary>

Provider उसे ठुकरा देता है, और harness error को tool result के रूप में model को वापस भेजता है: "Error: missing required field 'user_id'"। Model यह error पढ़ता है और call सुधारने का मौक़ा पाता है। Loop crash नहीं होता; error सामान्य नतीजा है।

</details>

3. ▢ Model के server tool call करने बनाम client tool call करने पर क्या होता है, इसका सबसे अच्छा वर्णन कौन-सा कथन है?

    - a) Server tool आपके infrastructure पर चलता है; client tool provider के infrastructure पर
    - b) Model tool के लिए अनुरोध भेजता है; harness तय करता है कि उसे कहाँ चलाना है
    - c) Server tool हमेशा जल्दी ख़त्म होता है क्योंकि provider उसे optimize करता है
    - d) दोनों की implementation आप लिखते हैं, बस अलग तरह से

<details markdown="1"><summary>जाँचें</summary>

**b)** Model दोनों में वही संरचित अनुरोध भेजता है। Harness tool definition पढ़ता है, तय करता है कि वह client है या server, और execution को उसी हिसाब से भेजता है। (a) उल्टा है: client tools आपके हैं, server tools provider के। (c) ग़लत है: गति implementation पर निर्भर है, इस पर नहीं कि वह server है या client। (d) आंशिक रूप से सही है पर यह चूक जाता है कि आप server tools कभी नहीं लिखते, सिर्फ़ define करते हैं।

</details>

4. ▢ आप "search_the_web" के लिए server tool define करते हैं, जिसके schema में सिर्फ़ `query` field ज़रूरी है। Model उसे `query="python", limit=5` के साथ call करता है। Provider क्या करता है?

<details markdown="1"><summary>जाँचें</summary>

या तो call सिर्फ़ query के साथ चलाता है और limit को अनदेखा करता है, या call ठुकरा देता है क्योंकि schema अतिरिक्त `limit` field की इजाज़त नहीं देता। नतीजा इस पर निर्भर है कि schema की definition अतिरिक्त properties की इजाज़त देती है या नहीं। अगर schema सख़्त है (डिफ़ॉल्ट), तो अतिरिक्त field एक error है।

</details>

## असली दुनिया का अभ्यास

- [ ] किसी असली task (search, retrieve, compute या fetch) के लिए tool schema ढूँढें या लिखें। चिह्नित करें कि कौन-से fields ज़रूरी हैं, किन पर बंदिशें हैं (enums, string की लंबाई, संख्या के दायरे), और कौन-से optional हैं। एक field का विवरण ज़्यादा साफ़ करके दोबारा लिखें।
- [ ] कोई agent चलाएँ या ऐसा harness लिखें जो tool call करे, और जानबूझकर उसे अमान्य argument भेजें (कोई ज़रूरी field छोड़ दें, ग़लत type भेजें, enum से बाहर का मान भेजें)। देखें कि provider कैसे जवाब देता है और आपका harness या framework उसे कैसे संभालता है।
- [ ] कल: एक ही task (जैसे "files की सूची") के लिए client tool और server tool डिज़ाइन करें। दोनों के schemas लिखें। इस पर एक trade-off समझाएँ कि हर tool कहाँ रहता है।

## आगे बढ़ने के लिए

- [दस्तावेज़: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
