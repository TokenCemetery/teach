---
title: "5. Parallel Calls और Results के रूप में Errors"
description: Model एक साथ कई tools कैसे माँग सकता है, और tool errors exceptions नहीं, results क्यों हैं
type: lesson
---

# पाठ 5. Parallel Calls और Results के रूप में Errors

**मिशन से संबंध:** किसी दिए गए task के लिए agent loop लिखें, और बताएँ कि उसके context का हर message क्या कर रहा है और loop को क्या ख़त्म करता है।
**मुख्य स्रोत:** [दस्तावेज़: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
**पूर्व-आवश्यकताएँ:** [पाठ 4](0004-schemas-and-who-executes.md)

## वार्म-अप

1. ▢ क्या model एक ही turn में एक साथ एक से ज़्यादा tool call माँग सकता है?

<details markdown="1"><summary>जाँचें</summary>

हाँ। Model एक ही response में कई tool-use blocks भेज सकता है, हर एक का अपना अनोखा id। Harness उन सबको चलाता है (संभवतः parallel में) और नतीजे इकट्ठा करके अगले message के रूप में वापस भेजता है।

</details>

2. ▢ जब कोई tool फेल होता है, तो harness क्या करता है: ऐसा exception उठाता है जो loop को crash कर दे, या error model को लौटाता है?

<details markdown="1"><summary>जाँचें</summary>

Error को tool result के रूप में model को लौटाता है। Loop चलता रहता है; model को retry करने, दूसरा tool इस्तेमाल करने या विफलता समझाने का मौक़ा मिलता है।

</details>

## यह जानें

### एक turn में parallel tool calls

Agent loop है भेजो, चलाओ, जोड़ो, दोहराओ। एक model response में कई tool calls हो सकती हैं:

```json
{
  "role": "assistant",
  "content": [
    {"type": "text", "text": "I'll gather that data for you."},
    {
      "type": "tool_use",
      "id": "toolu_01XYZ",
      "name": "get_weather",
      "input": {"city": "Lisbon"}
    },
    {
      "type": "tool_use",
      "id": "toolu_02ABC",
      "name": "get_weather",
      "input": {"city": "Madrid"}
    }
  ],
  "stop_reason": "tool_use"
}
```

हर call का अपना अनोखा id है। Model ने तय किया है: "मुझे Lisbon और Madrid दोनों का मौसम चाहिए।" आपका harness अब यह कर सकता है:

1. दोनों tools क्रम से चलाए (एक के बाद दूसरा), या
2. उन्हें parallel में चलाए (दोनों एक साथ), आपकी implementation के हिसाब से।

चुनाव आपका है। अगर वे स्वतंत्र और तेज़ हैं, तो parallel latency बचाता है। अगर वे संसाधनों के लिए होड़ करते हैं या एक दूसरे पर निर्भर है, तो क्रमवार चलाना सरल है।

### अगले turn से पहले नतीजे इकट्ठा करना

जब सारी tool calls पूरी हो जाती हैं, तो harness नतीजे इकट्ठा करके उन्हें एक ही message में वापस भेजता है। हर नतीजे पर उस call का id लगा होता है जिसका वह जवाब है:

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01XYZ",
      "content": "18C, partly cloudy"
    },
    {
      "type": "tool_result",
      "tool_use_id": "toolu_02ABC",
      "content": "22C, sunny"
    }
  ]
}
```

Model के पास अब दोनों नतीजे हैं, वह जानता है कि कौन-सा कौन-सा है (id से), और तय करता है कि आगे क्या करना है। यही मुख्य बात है: सारे नतीजे एक ही message में साथ लौटते हैं, इसलिए model उन्हें जोड़ी के रूप में process करता है।

### Errors को results की तरह लेना

जब कोई tool फेल होता है, तो harness loop को crash नहीं करता। इसके बजाय वह error पकड़कर उसे model को नतीजे के रूप में भेज देता है, ठीक सफल नतीजे की तरह। Error वाला tool result ऐसा दिखता है:

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01XYZ",
  "content": "Error: city not found",
  "is_error": true
}
```

`is_error` field model को बताता है कि यह नतीजा विफलता है, सफलता नहीं। Model उसे पढ़कर तय करता है: वही tool दूसरी city के साथ retry करे, दूसरा tool आज़माए, या हार मानकर उपयोगकर्ता को error समझाए।

### Errors results क्यों हैं, exceptions क्यों नहीं

कई systems में फेल हुई function call exception उठाती है और execution रोक देती है। Agent loop में फेल हुई tool call बस जानकारी है: model को लौटाया गया data। यह design क्यों?

क्योंकि model ज़िम्मेदार है। Model ने tool call किया था; tool फेल हो तो क्या करना है, यह उसे तय करना चाहिए। शायद वह retry करना चाहे। शायद दूसरा tool इस्तेमाल करना चाहे। शायद उपयोगकर्ता से और जानकारी माँगना चाहे। Exception यह चुनाव छीन लेता।

यह बुरे code को माफ़ करना नहीं है। यह design का चुनाव है: model को call stack के एक और function की तरह नहीं, orchestrator की तरह देखना। Harness का काम है वह चलाना जो model माँगे, नतीजा (सफलता या विफलता) इकट्ठा करना, और model के समझने के लिए उसे लौटा देना।

### Errors कई जगहों से आती हैं

Tool call कई कारणों से फेल हो सकती है:

- Client tool के code ने exception उठाया (database बंद, अमान्य input, timeout)।
- Server tool चला पर error लौटाया (API rate limit, file नहीं मिली, permission denied)।
- Harness ने ख़ुद call ठुकरा दी (schema validation फेल, ज़रूरी field छूटा)।
- Network फेल हुआ (provider तक पहुँच नहीं, connection टूटा)।

ये सब error संदेशों वाले tool results बन जाते हैं, crashes नहीं।

## अभ्यास

1. ▢ Model एक turn में दो tool calls करता है: एक सफल होती है, एक फेल। Harness दोनों नतीजे model को कैसे भेजता है?

<details markdown="1"><summary>जाँचें</summary>

दो tool_result blocks वाले एक ही user-role message में, हर एक पर संबंधित call का id लगा हुआ। एक नतीजे में `is_error: true` या error संदेश होता है; दूसरे में सफलता का data। Model दोनों एक ही turn में पाता है और तय करता है कि आगे क्या करना है।

</details>

2. ▢ आपके पास database में search करने वाला tool है। Model उसे ऐसी search के साथ call करता है जो timeout हो जाती है। आपके harness को क्या करना चाहिए?

<details markdown="1"><summary>संकेत</summary>

सोचें कि timeout संभालना किसका काम है और model को क्या जानना ज़रूरी है।

</details>

<details markdown="1"><summary>जाँचें</summary>

Timeout पकड़ें, error संदेश लें (जैसे "Error: search timed out after 30s"), और उसे `is_error: true` वाले tool result के रूप में model को वापस भेजें। फिर model तय करता है: सरल query से retry करे, दूसरा tool आज़माए, या छोड़ दे। Loop crash नहीं होता।

</details>

3. ▢ Model तीन parallel tool calls करता है। Harness को चाहिए कि:

    - a) उन्हें एक के बाद एक चलाए ताकि कोई फेल हो तो जल्दी रुक सके
    - b) उन्हें parallel में चलाए और सारे नतीजों का इंतज़ार करके उन्हें वापस भेजे
    - c) सफल नतीजे तुरंत लौटाए और फेल हुए नतीजे बाद में भेजे
    - d) जैसे ही एक फेल हो, बाक़ी calls रद्द कर दे

<details markdown="1"><summary>जाँचें</summary>

**b)** उन्हें parallel में चलाएँ और सारे नतीजों का इंतज़ार करें। Model ने तीन चीज़ें माँगी थीं; उसे तीन नतीजे मिलने चाहिए (सफलता या विफलता)। जल्दी रुकना (a) या रद्द करना (d) model को यह जानने से रोकता है कि क्या हुआ। अलग-अलग समय पर नतीजे लौटाना (c) protocol तोड़ता है: नतीजे एक ही message में साथ लौटते हैं।

</details>

4. ▢ आप दो संख्याओं को गुणा करने वाला client tool लिखते हैं। Model उसे `x=5, y="hello"` के साथ call करता है। Harness उसे चलाने की कोशिश करता है, function type error उठाता है। Harness का अगला क़दम क्या है?

<details markdown="1"><summary>जाँचें</summary>

Exception पकड़ें, error को format करें (जैसे "Error: cannot multiply number by string"), और उसे tool result के रूप में model को वापस भेजें। अब model जानता है कि call फेल हुई और वैध inputs से retry कर सकता है या दूसरा तरीक़ा आज़मा सकता है। Loop चलता रहता है।

</details>

## असली दुनिया का अभ्यास

- [ ] ऐसा agent लिखें या खोजें जो parallel tool calls करता हो। एक execution को खंगालें जहाँ model एक साथ दो tools माँगता है। जाँचें कि दोनों नतीजे एक ही message में साथ लौटते हैं और अपने-अपने ids लिए होते हैं।
- [ ] जानबूझकर किसी tool को फेल करें (बंद पड़े database को call करें, validation error उकसाएँ, या tool को अमान्य input भेजें)। देखें कि harness error को कैसे format करके model को भेजता है। देखें कि model आगे क्या करता है।
- [ ] कल: ऐसा harness लिखें जो tool calls parallel में चलाए (threading, async, या अपनी भाषा का concurrency model इस्तेमाल करें) और नतीजे इकट्ठा करे। जाँचें कि कुछ tools फेल हो जाएँ तब भी वह सारे नतीजे एक ही message में वापस भेजता है।

## आगे बढ़ने के लिए

- [दस्तावेज़: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
