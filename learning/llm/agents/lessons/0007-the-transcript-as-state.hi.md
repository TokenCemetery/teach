---
title: "7. State के रूप में Transcript"
description: यह समझना कि turns के बीच transcript ही agent की एकमात्र टिकाऊ memory है
type: lesson
---

# पाठ 7. State के रूप में Transcript

**मिशन से संबंध:** Transcript को agent की इकलौती state के रूप में पहचानने से आप असफल agent को उसकी trajectory से जाँच पाते हैं, यह अंदाज़ा लगाने के बजाय कि model उलझा हुआ या दोहराव वाला क्यों है, और यह इस लक्ष्य की सेवा करता है कि "असफल agent को उसकी trajectory से जाँचें।"
**मुख्य स्रोत:** [लेख: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**पूर्व-आवश्यकताएँ:** [पाठ 6](0006-writing-the-loop.md), [Trajectory](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 6 से: harness के model को call करके response पाने के बाद, किसी भी tool call को चलाने से पहले क्या होना ज़रूरी है?

<details markdown="1"><summary>जाँचें</summary>

Response को तुरंत transcript में जोड़ना होगा, किसी भी tool के चलने से पहले। नहीं तो model का अपना अनुरोध कभी दर्ज नहीं होता, और बाद का turn नहीं दिखाएगा कि tool का नतीजा वहाँ क्यों है।

</details>

2. ▢ पाठ 6 से: ऐसी दो अलग stopping conditions बताएँ जिन्हें harness agent loop ख़त्म करने के लिए जाँच सकता है।

<details markdown="1"><summary>जाँचें</summary>

इनमें से कोई भी दो: model बिना tool call का turn लौटाए, max-turns या token-budget की सीमा लग जाए, model स्पष्ट stop tool call करे, या error-count की सीमा पार हो जाए।

</details>

## यह जानें

### सिर्फ़ Transcript टिकता है

Model की एक call और अगली call के बीच harness दो चीज़ें रखता है:

1. Transcript: पूरा बातचीत का इतिहास, जिसमें हर model response, tool call और tool result शामिल हैं।
2. Harness का metadata: counters (turn count, error count), सीमाएँ (max turns, max errors), tool registrations, configuration।

Model को harness का metadata नहीं दिखता। Model सिर्फ़ transcript देखता है। अगर कोई तथ्य transcript में नहीं है, तो model नहीं जानता कि वह हुआ था।

यह एक साथ सरल भी है और गहरा भी। इसका मतलब है:

- Model उस चीज़ पर तर्क नहीं कर सकता जो harness ने भीतर ही तय की, जब तक harness उसे transcript में न डाले।
- Turns के बीच और कुछ नहीं टिकता। न भीतरी flags, न छिपी state, न harness metadata के बाहर के variables।
- Agent run को replay करने का मतलब है वही transcript model को वापस देना और वहीं से आगे बढ़ना।

### Trajectory और Transcript का अलग होना

Trajectory जो हुआ उसका पूरा रिकॉर्ड है: हर turn, फ़ैसला, log और side effect। Transcript वह है जो model को दिखाया गया। दोनों एक नहीं हैं।

उदाहरण के लिए:

- Harness एक tool call चलाता है, 100KB का नतीजा पाता है, पर तय करता है कि नतीजा बहुत लंबा है और transcript में जोड़ने से पहले उसे काट देता है। Trajectory कहती है "tool call सफल हुई, नतीजा 100KB था"; transcript कहता है "tool call सफल हुई, नतीजा पहले 10KB थे"। Model सिर्फ़ दूसरा संस्करण जानता है।
- Harness किसी tool को retry करने का फ़ैसला करता है क्योंकि पहला प्रयास फेल हुआ था। फ़ैसले का log किसी file में चला जाता है ताकि कोई इंसान बाद में debug करे। पर harness transcript में "मैं retry करने जा रहा हूँ" कभी नहीं जोड़ता। अगले turn में model नहीं जानता कि retry हुआ; वह सिर्फ़ नतीजे देखता है।
- कोई tool call चुपचाप फेल हो जाती है। Harness उसे log करता है पर transcript में error संदेश नहीं जोड़ता क्योंकि harness डिज़ाइन करने वाला भूल गया। Model कभी नहीं जान पाता कि tool फेल हुआ। अगले turn में model वही tool फिर माँग सकता है, उलझा हुआ कि वह काम क्यों नहीं किया।

नतीजा यह है कि आप trajectory देखकर निष्कर्ष निकाल सकते हैं कि "harness ने समझदारी का फ़ैसला किया", पर अगर आप सिर्फ़ transcript देखें तो आपको उलझा हुआ model दिखता है। Model उलझा नहीं है। Model को बस बताया नहीं गया।

### एक हल किया हुआ उदाहरण: वह Tool Result जो कभी था ही नहीं

इस परिदृश्य की कल्पना करें:

Agent को कीमत देखनी है, फिर छूट लगानी है, फिर पुष्टि करनी है। दूसरे turn में model कीमत लाने के लिए tool call करता है। Tool लौटाता है "Item XYZ costs $100"। Harness tool चलाता है, नतीजा पाता है, और उसे transcript में जोड़ता है:

```text
Agent turn 1: "I will find the price of item XYZ"
Agent turn 1 tool call: fetch_price(item="XYZ")
Tool result: "Item XYZ costs $100"

Agent turn 2: "I will apply a 10% discount. $100 - 10% = $90."
Agent turn 2 tool call: confirm_price(item="XYZ", price="$90")
```

यह काम करता है। Model ने नतीजा देखा और सही तर्क किया।

अब एक रूपांतर सोचें: harness monitoring के लिए नतीजे database में log कर रहा है। Log insert फेल हो जाता है। Harness error को file में log करता है, पर developer ने transcript में कुछ नहीं जोड़ा। अगला turn ऐसे शुरू होता है:

```text
Agent turn 1: "I will find the price of item XYZ"
Agent turn 1 tool call: fetch_price(item="XYZ")

Agent turn 2: "I need to fetch the price. Let me call fetch_price again."
Agent turn 2 tool call: fetch_price(item="XYZ")
```

Model कीमत फिर माँगता है। वह ज़िद्दी या मूर्ख नहीं है। Transcript में turn एक का नतीजा कभी दिखता ही नहीं। Model के पास जानने का कोई रास्ता नहीं कि call सफल हुई थी। इसे divergence कहते हैं: trajectory कहती है "नतीजा मिला और log हुआ", पर transcript कहता है "कुछ नहीं हुआ"।

हल यह है कि आगे बढ़ने से पहले हमेशा transcript में जोड़ें, भले ही side effects फेल हों:

```text
Tool result (appended immediately): "Item XYZ costs $100"

[Later, harness logs to database, but the append already happened]
Log to database failed [this error never goes in the transcript]
```

अब model जानता है कि नतीजा आ चुका है, आगे की errors चाहे जो हों।

### Transcript का state होना resumption आसान क्यों बनाता है

मान लें कि agent run बीच में रुक जाता है। Harness crash हो गया, network गिर गया, quota ख़त्म हो गई। आप agent को वहीं से फिर शुरू करना चाहते हैं जहाँ वह छूटा था।

अगर agent अपनी state भीतरी variables, flags और harness में बिखरे फ़ैसलों में रखता है, तो resumption कठिन है। आपको वह सारी state सहेजनी होगी, बहाल करनी होगी, और उम्मीद करनी होगी कि कुछ छूटा नहीं।

अगर agent की state सिर्फ़ transcript है, तो resumption आसान है: transcript सहेजें, फिर वही transcript model को वापस देकर नया run शुरू करें और loop को अगले turn से जारी रखें। Model वह सब देखेगा जो उसने पहले देखा था, और तर्क करना जारी रखेगा। न कोई छिपी state दोबारा बनानी, न flags बहाल करने, न variables का हिसाब रखना। Transcript ही अनुबंध है।

इसी तरह आप debug करने के लिए agent run को replay कर सकते हैं। Trajectory (जो हुआ उसका पूरा log) को transcript के रूप में वापस दें, और देखें कि model आगे क्या करेगा। आप transcript को हाथ से बदलकर यह भी परख सकते हैं कि किसी काल्पनिक स्थिति में model क्या करता।

## अभ्यास

1. ▢ एक agent को document खोजना, पढ़ना और उसका सारांश बनाना है। दूसरे turn में वह search tool call करता है और tool 10 नतीजे लौटाता है। नतीजा transcript में जोड़ने से पहले harness नतीजों को सबसे प्रासंगिक तीन तक छाँट देता है और सिर्फ़ वही जोड़ता है। Model क्या देखता है, और transcript पढ़ने पर यह design चुनाव दिखता क्यों है?

<details markdown="1"><summary>जाँचें</summary>

Model को तीन नतीजे दिखते हैं, दस नहीं। उसे नहीं पता कि harness ने छाँटा; वह सिर्फ़ वही जानता है जो transcript में है। अगर यह जानबूझकर किया गया है तो स्वीकार्य design है: harness ने छाँटकर token इस्तेमाल घटाना चुना। मुख्य बात यह है कि transcript पढ़कर आप ठीक-ठीक देख सकते हैं कि model ने क्या देखा (तीन नतीजे) और तर्क कर सकते हैं कि उस जानकारी को देखते हुए model का अगला फ़ैसला समझदारी का था या नहीं। आप इस बात से उलझते नहीं कि दस नतीजे थे; transcript दुनिया को model के नज़रिए से दिखाता है।

</details>

2. ▢ एक harness developer यह log करना चाहता है कि कौन-से tools कितनी बार call हुए। क्या उन्हें यह गिनती सिर्फ़-harness वाले variable में रखनी चाहिए, या हर model call से पहले transcript में सारांश जोड़ना चाहिए?

<details markdown="1"><summary>संकेत</summary>

सोचें कि फ़ैसले लेने के लिए model को क्या जानना ज़रूरी है, और कौन-सी जानकारी सिर्फ़ run के बाद किसी इंसान के debug करने के काम की होगी।

</details>

<details markdown="1"><summary>जाँचें</summary>

यह use case पर निर्भर है। अगर model को जानना है कि "आप search तीन बार call कर चुके हैं, शायद दूसरा tool आज़माएँ", तो गिनती transcript में जानी चाहिए। अगर गिनती पूरी तरह monitoring के लिए है और model को उसके आधार पर अपना व्यवहार बदलने की ज़रूरत नहीं, तो सिर्फ़-harness वाला variable ठीक है। पर अगर model को गिनती जानने से फ़ायदा हो सकता है, तो उसे transcript में रखें ताकि model उसे अगले turn में देख सके। सुरक्षित डिफ़ॉल्ट यह है कि जो भी model के अगले फ़ैसले को प्रभावित कर सकता है उसे जोड़ दें।

</details>

3. ▢ आप agent run को debug कर रहे हैं। आप trajectory पढ़ते हैं और देखते हैं कि tool call सफल हुई और नतीजा जोड़ा गया। आप वह transcript पढ़ते हैं जो model ने असल में देखा और नतीजा वहाँ नहीं है। क्या हुआ?

    - a) Harness ने नतीजा जोड़ा, फिर model को दोबारा call करने से पहले उसे transcript से हटा दिया
    - b) Trajectory और transcript को अलग होना ही चाहिए; transcript सारांश है और trajectory पूरी
    - c) नतीजा harness logs में जुड़ा पर transcript में नहीं; model ने उसे कभी नहीं देखा
    - d) Tool call असल में फेल हुई थी और trajectory ग़लत है

<details markdown="1"><summary>जाँचें</summary>

**c)** नतीजा harness logs में जुड़ा पर transcript में नहीं; model ने उसे कभी नहीं देखा। Model के नज़रिए से trajectory और transcript लगभग एक जैसे होने चाहिए (हालाँकि transcripts को दक्षता के लिए काटा या नमूने के तौर पर लिया जा सकता है)। अगर trajectory कहती है कि कुछ हुआ पर transcript नहीं दिखाता, तो सबसे संभावित कारण यह है कि harness ने उसे log किया पर transcript में नहीं जोड़ा। यही हल किए हुए उदाहरण में दिखाया bug है। जोड़ने के बाद transcript से हटाना (a) असामान्य होगा और मक़सद ही ख़त्म कर देगा। Transcripts सारांश नहीं हैं; उन्हें बातचीत का इतिहास होना चाहिए (b)। Trajectory की ग़लती (d) संभव है पर logging bug से कम आम है।

</details>

4. ▢ आप resumable agent बनाना चाहते हैं। Run पाँच turns के बाद रुक जाता है। एक वाक्य में बताएँ कि agent को छठे turn से फिर शुरू करने के लिए आपको disk पर क्या सहेजना होगा।

<details markdown="1"><summary>जाँचें</summary>

आपको transcript सहेजना होगा (पाँचवें turn तक का बातचीत इतिहास, जिसमें हर model response, tool call और tool result शामिल हैं)। फिर शुरू करते समय यह transcript model को शुरुआती context के रूप में दें, model को call करें, और loop जारी रखें। Harness का metadata (turn counter, error counter आदि) दोबारा बनाया या reset किया जा सकता है; सिर्फ़ transcript अनिवार्य है।

</details>

## असली दुनिया का अभ्यास

- [ ] कोई agent चलाएँ (आपकी इस्तेमाल की library से या आपका लिखा) जो कम से कम तीन tool calls करे। उसका बनाया transcript जाँचें। हर tool result के लिए पुष्टि करें कि अगले turn में model जो देखता वह नतीजा उसमें मौजूद है। अगर कोई नतीजा ग़ायब है, तो खोजें क्यों (क्या वह जोड़ा नहीं गया, या काटा गया, या छाँटा गया?)।

- [ ] अपने agent code या harness में कोई ऐसी जगह खोजें जहाँ जानकारी log होती है पर transcript में नहीं जुड़ती। ख़ुद से पूछें: क्या model को बेहतर फ़ैसले लेने के लिए यह जानना ज़रूरी है? अगर हाँ, तो इसे transcript में जोड़ें। अगर नहीं, तो इसे सिर्फ़-harness log रहने दें।

- [ ] कल: शुरू से resumable agent डिज़ाइन करें। Run function का pseudocode लिखें जो transcript को input के रूप में लेकर अगले turn से फिर शुरू हो। पुष्टि करें कि फ़ैसले लेने के लिए आप किसी सिर्फ़-harness state पर निर्भर नहीं हैं।

## आगे बढ़ने के लिए

- [लेख: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
