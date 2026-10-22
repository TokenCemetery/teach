---
title: "3. Tool Call का Wire Format"
description: आपके harness और model provider के बीच के protocol में tool call और उसका result असल में कैसे दिखते हैं
type: lesson
---

# पाठ 3. Tool Call का Wire Format

**मिशन से संबंध:** किसी दिए गए task के लिए agent loop लिखें, और बताएँ कि उसके context का हर message क्या कर रहा है और loop को क्या ख़त्म करता है।
**मुख्य स्रोत:** [दस्तावेज़: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
**पूर्व-आवश्यकताएँ:** [पाठ 2](0002-agent-workflow-or-prompt.md), [Tool](../GLOSSARY.md)

## वार्म-अप

1. ▢ Harness का model को call करना और harness का tool चलाना, इन दोनों में क्या अंतर है?

<details markdown="1"><summary>जाँचें</summary>

Harness model को call करता है उसे request (transcript और tools) network पर provider की API को भेजकर; model provider के infrastructure के भीतर चलता है और संरचित output लौटाता है। Tool तब call होता है जब model संरचित tool-call block भेजकर उसे माँगता है; harness उसे चलाता है, आमतौर पर उसी codebase या उसी network के किसी function को बुलाकर।

</details>

2. ▢ किस स्थिति में model tool call की जगह सादा text भेज सकता है?

<details markdown="1"><summary>जाँचें</summary>

जब model ने जिस task पर काम कर रहा था उसे पूरा कर लिया हो और उपयोगकर्ता को अंतिम उत्तर लौटाने को तैयार हो, या जब वह (आपकी तय की गई सीमाओं के भीतर) तय करे कि इस turn के लिए उसे tool call करने की ज़रूरत नहीं।

</details>

## यह जानें

### Wire पर tool call

जब आप model provider को tools इस्तेमाल करने का अनुरोध भेजते हैं, तो request में तीन चीज़ें होती हैं: model का नाम, उपलब्ध tools की सूची (उनके नामों, विवरणों और parameter schemas के साथ), और अब तक का बातचीत transcript।

Tool definition ऐसी दिखती है: एक नाम, इंसान के पढ़ने लायक़ विवरण, और एक JSON Schema जो उन parameters को सीमित करता है जो model भेज सकता है। यह एक tool वाली Anthropic request है:

```json
{
  "model": "claude-sonnet-5",
  "max_tokens": 1024,
  "tools": [
    {
      "name": "get_weather",
      "description": "Get the current weather for a given city",
      "input_schema": {
        "type": "object",
        "properties": {
          "city": {"type": "string", "description": "The city name"}
        },
        "required": ["city"]
      }
    }
  ],
  "messages": [
    {"role": "user", "content": "What's the weather in Lisbon?"}
  ]
}
```

जब model tool call करने का फ़ैसला करता है, तो वह उसे चलाता नहीं। इसके बजाय वह संरचित block लौटाता है जो बताता है कि कौन-सा tool call करना है और कौन-से arguments देने हैं। Provider output भेजना रोक देता है और `stop_reason` field से इसका संकेत देता है। यह पूरा Anthropic response है:

```json
{
  "id": "msg_01ABC",
  "type": "message",
  "role": "assistant",
  "content": [
    {"type": "text", "text": "I'll check that for you."},
    {
      "type": "tool_use",
      "id": "toolu_01XYZ",
      "name": "get_weather",
      "input": {"city": "Lisbon"}
    }
  ],
  "stop_reason": "tool_use"
}
```

ध्यान दें: `input` field पहले से parse किया हुआ JSON है, string नहीं। हर tool call को एक अनोखा id मिलता है (यहाँ `toolu_01XYZ`) ताकि harness model को बता सके कि कौन-सा result किस call का जवाब है। Assistant tool call block से पहले या बाद में सादा text भी डाल सकता है।

### Wire से execution तक

आपका harness यह response देखता है और जानता है कि उसे `get_weather` को argument `{"city": "Lisbon"}` के साथ चलाना है। यह कैसे करें, वह आपके tool पर निर्भर है:

- अगर वह **client tool** है (आपके अपने code का function), तो आप उसे सीधे call करते हैं: `weather_result = get_weather(city="Lisbon")`।
- अगर वह **server tool** है (कुछ ऐसा जो provider आपके लिए चलाता है, जैसे hosted web search), तो provider ने उसे लौटाने से पहले ही चला दिया है। आप response से नतीजा निकाल लेते हैं।

### Result वापस भेजना

जब harness के पास नतीजा आ जाता है (function चलाकर या provider का response पढ़कर), वह उसे tool call के id के साथ चिह्नित करके नए message में model को वापस भेजता है। Anthropic format उसे `user`-role वाले message के भीतर रखता है:

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01XYZ",
      "content": "18C, partly cloudy"
    }
  ]
}
```

यह message transcript में नए turn के रूप में जुड़ता है। Model के पास अब उसकी की हुई tool call और उसका नतीजा, दोनों हैं, और वह तय करता है कि आगे क्या करना है: दूसरा tool call करे, वही tool अलग arguments से call करे, या अंतिम उत्तर लौटाए।

### OpenAI का wire format (अंतर)

OpenAI की API वही अवधारणाएँ इस्तेमाल करती है पर field के नाम और आकार अलग हैं। पूरा exchange दोहराने के बजाय, यह है कि क्या अलग है:

Tool parameters सीधे `input_schema` की जगह `function.parameters` के नीचे आते हैं। Model के tool-call arguments `function.arguments` में JSON-encoded string के रूप में आते हैं, पहले से parse किए object के रूप में नहीं, इसलिए आपके harness को उसे parse करना पड़ता है। Stop संकेत `stop_reason: "tool_use"` की जगह `finish_reason: "tool_calls"` है। नतीजा `tool_call_id` लिए हुए समर्पित `role: "tool"` message के रूप में लौटता है, `user` message में लिपटकर नहीं। उसी मौसम वाले task का संक्षिप्त उदाहरण यह है:

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {"name": "get_weather", "arguments": "{\"city\": \"Lisbon\"}"}
      }]
    },
    "finish_reason": "tool_calls"
  }]
}
```

इसके बाद नतीजा `role: "tool"` message के रूप में:

```json
{"role": "tool", "tool_call_id": "call_abc123", "content": "18C, partly cloudy"}
```

Pattern एक ही है: tool definition, id वाला tool call, उसी id से चिह्नित नतीजा। नाम और आकार अलग हैं, पर जो भी harness एक को संभालता है उसे इन fields की mapping करके दूसरे के लिए ढाला जा सकता है।

## अभ्यास

1. ▢ ऊपर दिखाए Anthropic response में `input` field में JSON string की जगह parse किया हुआ JSON object क्यों है?

<details markdown="1"><summary>जाँचें</summary>

Anthropic API tool call के arguments को provider की ओर पर ही parse करके लौटाती है, जिससे harness का काम घटता है। आपके code को इस्तेमाल के लिए तैयार मान मिलते हैं, parse करने वाली string नहीं। OpenAI इसके बजाय arguments string के रूप में भेजता है, इसलिए उन्हें इस्तेमाल करने से पहले आपको harness में `json.parse()` या उसके बराबर call करना पड़ता है।

</details>

2. ▢ जब आप tool का नतीजा model को वापस भेजते हैं, तो उसमें `tool_use_id` field क्यों होता है?

<details markdown="1"><summary>जाँचें</summary>

Model ने एक ही turn में कई tools माँगे हो सकते हैं। Id model को हर नतीजे को उसकी की हुई संबंधित call से मिलाने देता है, ताकि वह जाने कि कौन-सा जवाब किस request से आया।

</details>

3. ▢ Anthropic के protocol में tool का नतीजा `user`-role वाले message के भीतर जाता है। OpenAI में वह `role: "tool"` message के रूप में जाता है। यह अंतर agent loop के तर्क के लिए क्यों मायने नहीं रखता?

    - a) क्योंकि transcript बनाते समय harness को उन्हें अलग पहचानने की ज़रूरत नहीं
    - b) क्योंकि role चाहे जो हो, model उन्हें हमेशा एक ही तरह process करता है
    - c) क्योंकि एक protocol साफ़ तौर पर ग़लत है और उससे बचना चाहिए
    - d) क्योंकि tool के नतीजे आधिकारिक transcript का हिस्सा नहीं हैं

<details markdown="1"><summary>जाँचें</summary>

**b)** Role label या message की बनावट चाहे जो हो, model उन्हें एक ही तरह process करता है। तर्क यह है: यह उस tool call का नतीजा है जो आपने की थी; अब आप क्या करना चाहते हैं? Protocol का ब्योरा (user message के भीतर या tool message के रूप में) उस तर्क को नहीं बदलता। (a) क़रीब है पर बात चूक जाता है: role loop के लिए ख़ुद मायने नहीं रखता।

</details>

4. ▢ एक harness को यह OpenAI response मिलता है: `"arguments": "{\"city\": \"Paris\"}"`। Tool को देने से पहले harness को इसे कैसे process करना होगा?

<details markdown="1"><summary>जाँचें</summary>

इसे JSON के रूप में parse करें: `json.loads("{\"city\": \"Paris\"}") yields {"city": "Paris"}`। OpenAI string लौटाता है, और function call के लिए arguments खोलने से पहले harness को उसे dictionary (या object) में deserialize करना होगा।

</details>

## असली दुनिया का अभ्यास

- [ ] किसी असली agent framework का code या दस्तावेज़ खोलें (LangChain, Vercel AI, या Claude का अपना Python SDK) और ढूँढें कि वह tool definition model को कहाँ भेजता है। नाम, विवरण और parameter schema पहचानें। Code में चिह्नित करें कि इनमें से हर एक कहाँ से आता है।
- [ ] उसी codebase में एक पूरे tool-call चक्र को खंगालें: ढूँढें कि वह model का tool-use response कहाँ parse करता है, tool कहाँ चलाता है, और नतीजा कहाँ वापस भेजता है। चिह्नित करें कि id उन्हें मिलाने में कैसे इस्तेमाल होता है।
- [ ] कल: एक न्यूनतम harness लिखें (20 पंक्तियाँ या कम, pseudocode चलेगा) जो model provider को एक tool भेजे, tool-call response parse करे, और नतीजा वापस भेजे। कोई framework इस्तेमाल न करें।

## आगे बढ़ने के लिए

- [दस्तावेज़: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [गाइड: "Function calling", OpenAI](https://developers.openai.com/api/docs/guides/function-calling)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
