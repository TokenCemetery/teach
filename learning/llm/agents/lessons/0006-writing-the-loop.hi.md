---
title: "6. Loop लिखना"
description: Pseudocode से agent loop बनाना और stopping conditions सोच-समझकर चुनना
type: lesson
---

# पाठ 6. Loop लिखना

**मिशन से संबंध:** Agent loop लिखना ख़ुद agent बनाने की मूल skill है, जो सीधे इस लक्ष्य की सेवा करती है कि "किसी दिए गए task के लिए agent loop लिखें, और बताएँ कि उसके context का हर message क्या कर रहा है और loop को क्या ख़त्म करता है।"
**मुख्य स्रोत:** [लेख: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**पूर्व-आवश्यकताएँ:** [पाठ 5](0005-parallel-calls-and-errors-as-results.md), [Agent loop](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 5 से: जब tool call फेल होती है तो transcript में क्या जुड़ता है?

<details markdown="1"><summary>जाँचें</summary>

Error वाला tool result, जिस पर फेल हुई call का id लगा हो और जो error के रूप में चिह्नित हो, ठीक वैसे ही जुड़ता है जैसे सफल नतीजा जुड़ता। Loop crash नहीं होता; model विफलता को सामान्य turn के रूप में देखता है।

</details>

2. ▢ पाठ 5 से: model के लिए दो tools एक के बाद एक की जगह parallel में माँगना सुरक्षित क्यों है?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि हर tool call को अपना अनोखा id मिलता है, और harness हर नतीजा उसी id के साथ लौटाता है। Model execution के क्रम से बेपरवाह होकर हमेशा नतीजे को उस call से मिला सकता है जिसने उसे बनाया।

</details>

## यह जानें

### Code के रूप में Agent Loop

मूल रूप में agent loop सरल है। यह pseudocode के रूप में है:

```text
function run_agent(model, tools, transcript, max_turns):
    for turn_count in range(max_turns):
        response = call_model(model, transcript)
        transcript.append(response)

        if response.has_no_tool_calls():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)
            transcript.append(result)

    return "Max turns reached"
```

यही harness है। Model चुनता है कि कौन-सा tool माँगना है और कब माँगना बंद करना है। Harness सीमाएँ और mechanics लागू करता है।

ढाँचे पर ध्यान दें: **model को call करो, response जोड़ो, देखो कि काम पूरा हुआ या नहीं, नहीं तो tools चलाओ और उनके नतीजे जोड़ो, फिर ऊपर लौट जाओ**। हर turn में transcript बढ़ता है। Transcript के बाहर memory में कुछ नहीं रखा जाता।

### हर turn में transcript का बढ़ना ज़रूरी क्यों है

शुरुआती लोग कभी-कभी ऐसा loop बना देते हैं जो इस तरह दिखता है:

```text
function run_agent_wrong(model, tools, transcript, max_turns):
    for turn_count in range(max_turns):
        response = call_model(model, transcript)

        if response.has_no_tool_calls():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)
            transcript.append(result)  # Only append results, not the model's request
```

यह bug है। अगर tool चलाने से पहले आप model का tool-call response transcript में नहीं जोड़ते, तो model अगले turn में "याद" नहीं रखेगा कि उसने tool माँगा था। जब harness model को दोबारा call करता है, तो transcript में यह नहीं होता कि "model ने search माँगा था" या "model ने calculator माँगा था"। Model उलझा हुआ वही tool फिर माँग सकता है। साहित्य में इसे request भूल जाना कहा जाता है। Transcript असंगत हो जाता है।

इसका हल है कि response को model को call करते ही **तुरंत** जोड़ दें, किसी और काम से पहले:

```text
function run_agent_correct(model, tools, transcript, max_turns):
    for turn_count in range(max_turns):
        response = call_model(model, transcript)
        transcript.append(response)  # Append right away

        if response.has_no_tool_calls():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)
            transcript.append(result)
```

अब जब loop दोहराकर model को फिर call करता है, तो transcript में "model ने कहा था कि वह search call करेगा" शामिल होता है, और model नतीजे पर तर्क कर सकता है।

### Stopping conditions: सोच-समझकर चुनना

Agent loop को रुकना ज़रूरी है। चुनने की कई जगहें हैं:

**Max turns**: बाहरी loop turns गिनता है और गिनती सीमा से ऊपर जाने पर बाहर निकल जाता है। यह सुरक्षा की रोक है। इसके बिना, बिगड़ा model या tool loop हमेशा चलता रह सकता है।

**कोई tool call नहीं**: Model के response में कोई tool call नहीं है। यह "सीधे रास्ते" का stop है: model ने उत्तर देने का फ़ैसला कर लिया है। इसे model का response जोड़ने के बाद जाँचें।

**स्पष्ट stop tool**: आप `stop` या `finish` नाम का tool दे सकते हैं जिसे model स्पष्ट रूप से बाहर निकलने के लिए call कर सके। Harness इसे जाँचता है और लौट आता है। यह तब काम का है जब task खुला हो और model को स्पष्ट "मैं पूरा कर चुका" कार्रवाई चाहिए। अगर आप यह tool देते हैं, तो उसे साफ़ दर्ज करें ताकि model समझे कि उसे कब इस्तेमाल करना है।

**Error count की रोक**: अगर tool call फेल होती है, तो harness error को नतीजे के रूप में जोड़ता है। अगर लगातार बहुत-सी tool calls फेल हों, तो harness हमेशा चलते रहने की जगह रुक जाता है और error trajectory लौटाता है। यह retry loops को रोकता है।

ये एक-दूसरे को बाहर नहीं करतीं। Production harness इन सबको जाँच सकता है:

```text
function run_agent_with_guards(model, tools, transcript, max_turns, max_errors):
    error_count = 0

    for turn_count in range(max_turns):
        response = call_model(model, transcript)
        transcript.append(response)

        if response.has_no_tool_calls():
            return response.text

        if response.has_explicit_stop_tool_call():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)

            if result.is_error():
                error_count += 1
                if error_count > max_errors:
                    return "Too many errors"
            else:
                error_count = 0

            transcript.append(result)

    return "Max turns reached"
```

मुद्दा यह है कि ये फ़ैसले आपके code में दिखने चाहिए, छिपे हुए या संयोग से नहीं। आप चुनते हैं कि कब रुकना है, और आप चुनते हैं कि agent को सँभलने के कितने मौक़े मिलेंगे।

## अभ्यास

1. ▢ ऊपर दिखाए pseudocode loop में `transcript.append(response)` का `if response.has_no_tool_calls()` जाँच से पहले होना क्यों ज़रूरी है?

<details markdown="1"><summary>जाँचें</summary>

Transcript में model का response शामिल होना चाहिए ताकि बाद के turns (या trajectory पढ़ने वाला कोई observer) देख सकें कि model ने क्या कहा और क्या तय किया। अगर आप जोड़ने से पहले रुकने की जाँच करते हैं, तो आप model का text लौटा देते हैं, पर transcript में कभी नहीं दिखता कि model ने जवाब दिया भी था। साथ ही, response की दूसरी जानकारी (जैसे कौन-से tools model ने सोचे पर call न करने का फ़ैसला किया) खो जाती।

</details>

2. ▢ Model एक tool call करता है और harness उसे सफलतापूर्वक चलाकर नतीजा लौटाता है। नतीजा transcript में जुड़ता है। अगले loop iteration में harness model को फिर call करता है। Model को transcript में ऐसा क्या दिखता है जो पिछले turn में नहीं दिखा था?

<details markdown="1"><summary>संकेत</summary>

सोचें कि पिछले loop iteration में, model को पहली बार call करने के ठीक बाद, क्या जोड़ा गया था।

</details>

<details markdown="1"><summary>जाँचें</summary>

Model को अपना ही tool-call response दिखता है जो loop के tool चलाने से पहले जोड़ा गया था। दूसरे turn में transcript में वह response और tool का नतीजा, दोनों होते हैं। अगर response पहले न जोड़ा जाता, तो model को सिर्फ़ नतीजा दिखता, मानो tool model के अलावा किसी और ने call किया हो।

</details>

3. ▢ आप max-errors guard वाला harness बना रहे हैं: अगर लगातार तीन tool calls फेल हों, तो loop रोक दो। Error counter को शून्य पर reset करने के लिए आपको क्या चाहिए?

    - a) जब max turns पहुँच जाएँ
    - b) जब कोई tool call सफल हो और non-error नतीजा लौटाए
    - c) जब loop शुरू हो
    - d) जब model के response में कोई tool call न हो

<details markdown="1"><summary>जाँचें</summary>

**b)** जब कोई tool call सफल हो। Guard बार-बार की विफलताओं का pattern पकड़ने के लिए है। अगर एक tool फेल हो, फिर अगला सफल हो, तो retry loop टूट गया और आप और विफलताओं की इजाज़त देना चाहते हैं। अगर आप सिर्फ़ शुरुआत में reset करें (c), तो आप कभी रुक नहीं पाएँगे; अगर max-turns या no-tool-calls पर reset करें (a, d), तो guard काम नहीं करता। सफलता पर reset करना ही pattern है: एक सफलता counter को reset कर देती है।

</details>

4. ▢ आपके model को search करना, document पढ़ना और फिर सारांश बनाना है। तीसरे turn में वह वही search tool फिर माँगता है। Search पहली बार सफल रही थी। Transcripts के काम करने के तरीक़े को देखते हुए, आपके harness में सबसे संभावित bug क्या है?

<details markdown="1"><summary>जाँचें</summary>

Model को call करने के बाद harness model का tool-call response transcript में नहीं जोड़ रहा। Model को पहले turn में अपना search tool का अनुरोध कभी दिखता ही नहीं। जब उसे तीसरे turn में call किया जाता है, तो transcript में search का नतीजा दिखता है पर अनुरोध नहीं, इसलिए model नहीं जानता कि नतीजा वहाँ क्यों है और search फिर माँग लेता है। हल यह है कि response को model call करने के तुरंत बाद, tool चलाने से पहले जोड़ें।

</details>

## असली दुनिया का अभ्यास

- [ ] पाठ को देखे बिना, याद से बुनियादी agent loop का pseudocode लिखें। उसकी तुलना "Code के रूप में Agent Loop" के तहत दिखाए pseudocode से करें। जाँचें: क्या आप no tool calls की जाँच से पहले response जोड़ते हैं?

- [ ] किसी open-source project में agent implementation खोजें (आपकी इस्तेमाल की library या कोई public repository)। Loop का code पढ़ें। पहचानें कि transcript कहाँ बनता है और stopping condition कहाँ जाँची जाती है। नोट करें कि stopping conditions स्पष्ट हैं (if statement में दिखती हैं) या छिपी हैं (किसी दूसरे function की call के भीतर दबी किसी condition में)।

- [ ] कल: चारों stopping conditions (max turns, no tool calls, स्पष्ट stop, error count guard) pseudocode में खींचें। हर एक के लिए एक वाक्य लिखें कि वह क्यों मायने रखती है: वह कौन-सी समस्या सुलझाती है?

## आगे बढ़ने के लिए

- [लेख: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
