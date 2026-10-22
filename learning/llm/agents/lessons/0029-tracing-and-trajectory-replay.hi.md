---
title: "29. Tracing और Trajectory Replay"
description: Agent runs को पकड़ने के लिए vendor-neutral trace conventions का इस्तेमाल, और विफलताओं को चरण-दर-चरण देखने के लिए trajectories को replay करना
type: lesson
---

# पाठ 29. Tracing और Trajectory Replay

**मिशन से संबंध:** संरचित, मानकीकृत traces से agent runs दर्ज करना और सहेजी हुई trajectory को replay कर पाना आपको सहकर्मी को विफलता का ठीक बिंदु सौंपने, उसे स्वतंत्र रूप से चरण-दर-चरण देखने, और production का निदान "चलो logs देखता हूँ" से "चलो trajectory को चरण-दर-चरण देखता हूँ" तक ले जाने देता है।
**मुख्य स्रोत:** [विनिर्देश: "Semantic Conventions for Generative AI", OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
**पूर्व-आवश्यकताएँ:** [पाठ 28](0028-cascading-tool-errors.md), [Trajectory](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 28 से: Schema validation error और hallucinated argument में क्या अंतर है?

<details markdown="1"><summary>जाँचें</summary>

Schema validation error तुरंत तब होती है जब कोई ज़रूरी field छूटे या मान ग़लत type का हो; model को साफ़ प्रतिक्रिया मिलती है। Hallucinated argument सही type का मान है जो validation पार कर लेता है पर किसी असली चीज़ से मेल नहीं खाता, इसलिए error आगे जाकर होती है और model ग़लत निदान कर सकता है कि वह क्यों फेल हुआ।

</details>

2. ▢ पाठ 7 से: Agent run को turn N से फिर शुरू करने के लिए आपको state का कौन-सा एक हिस्सा सहेजना होगा?

<details markdown="1"><summary>जाँचें</summary>

Transcript: turn N तक का पूरा बातचीत का इतिहास, जिसमें हर model response, tool call और tool result शामिल है। फिर शुरू करते समय यह transcript model को वापस दें और loop को turn N+1 से जारी रखें।

</details>

## यह जानें

### Traces, spans और vendor-neutral conventions

Trace agent run के दौरान जो हुआ उसका संरचित, timestamp वाला रिकॉर्ड है। यह spans से बना है, जिनमें से हर एक अलग operation दर्शाता है:

- हर model call के लिए एक span (input: transcript; output: model का response और tool calls; समय; इस्तेमाल हुए tokens)
- हर tool execution के लिए एक span (input: tool का नाम और arguments; output: नतीजा या error; समय)
- हर loop iteration के लिए एक span (शुरू होने का समय, ख़त्म होने का समय, turn की संख्या)

साझा convention के बिना, हर टीम और हर vendor इन्हें अलग नाम देता है। कोई tool model call के input को "prompt" कहता है, कोई "messages", कोई "input"। कोई tool output को "response" कहता है, कोई "generated_text"। इससे traces तुलना योग्य नहीं रहते: vendor A के tools इस्तेमाल करने वाली टीम आसानी से vendor B के traces नहीं पढ़ सकती, और एक vendor से दूसरे पर जाने का मतलब आपके सारे trace parsing को दोबारा लिखना है।

OpenTelemetry GenAI semantic conventions इन spans और attributes के लिए vendor-neutral शब्दावली परिभाषित करते हैं। वे मानकीकृत करते हैं कि हर span में कौन-सी जानकारी होनी चाहिए:

Model call span में शामिल है: model का नाम, input में कुल tokens, output में कुल tokens, reasoning effort (अगर तय है), माँगी गई tool calls, रुकने का कारण।

Tool execution span में शामिल है: tool का नाम, वह client tool है या server tool, tool के नतीजे की स्थिति (सफलता या error), क्या कोई cost थी (server tools के लिए), फेल होने पर error संदेश।

Transaction span सब कुछ लपेटता है और उसमें शामिल है: agent loop के turn की संख्या, wall-clock शुरू और ख़त्म होने के समय, turn सफल हुआ या फेल, लिया गया कोई रुकने का फ़ैसला।

क्योंकि ये मानकीकृत हैं, एक harness का बनाया trace किसी भी OpenTelemetry-संगत tool से पढ़ा जा सकता है। वही dashboard, विश्लेषण script, या visualization जो एक टीम के traces के साथ काम करता है, दूसरी टीम के साथ भी काम करता है। यह वही सिद्धांत है जिसने पाठ 3 में tool-call wire formats को मानकीकृत किया: बुनियादी अवधारणाएँ (agent loop, model call, tool call) providers के पार वही हैं, इसलिए मानक शब्दावली आपको उनके बीच जाने देती है।

### निदान के लिए संरचित traces क्यों मायने रखते हैं

पाठ 27 के loops और poisoning, और पाठ 28 के cascades, सब trajectory को ध्यान से पढ़कर खोजे जाते हैं। पर ध्यान से पढ़ना तभी संभव है जब trajectory अच्छी तरह संरचित हो।

कल्पना करें आप 47 turns और सैकड़ों पंक्तियों के log output वाले agent run की विफलता का निदान करने की कोशिश कर रहे हैं। आपके पास print statements error संदेशों से मिले हुए हैं, tool के नतीजे JSON के रूप में छपे हैं, और timestamps जो सही हो भी सकते हैं और नहीं भी। आप पंक्ति-दर-पंक्ति पढ़ रहे हैं, जोड़ने की कोशिश में कि क्या हुआ।

अब कल्पना करें वही run संरचित trace के रूप में: हर span turn की संख्या से चिह्नित है, हर model call model के नाम से लेबल है, हर tool call tool के नाम से लेबल है। आप trace को query कर सकते हैं: "turn 10 और उसके आगे फेल हुई सारी tool calls दिखाओ" या "turn 23 पर model ने जो reasoning text इस्तेमाल किया वह दिखाओ" या "कौन-से spans parallel में चले उसका timeline दिखाओ"। यह निदान के लिए नाटकीय रूप से तेज़ है।

इसके अलावा, संरचित traces कुछ निदान को स्वचालित करने देते हैं: सरल नियम "एक ही tool नाम वाले लगातार spans खोजकर दोहराव वाले loops पहचानो" को चिह्नित कर सकता है। Run के बाद का विश्लेषण "error spans के क़रीब क्रम में अलग-tool-नाम वाले spans देखकर cascading विफलताएँ पहचानो" को चिह्नित कर सकता है। ये patterns freeform logs में पहचानना कठिन है; संरचित data के साथ सीधा है।

### Trajectory replay: परिकल्पनाएँ परखना

क्योंकि transcript agent की एकमात्र टिकाऊ state है (पाठ 7), आप trajectory सहेज सकते हैं और किसी भी बिंदु पर उसे नए run में वापस दे सकते हैं। इसे trajectory replay कहते हैं।

यह सब संभव हो जाता है:

**ठीक वही परिस्थितियाँ दोहराएँ**: कोई ग्राहक बताता है कि agent फेल हुआ। आप उनकी trajectory सहेजते हैं (विफलता के बिंदु तक का transcript) और उसे नए harness run में देते हैं। नए run को ठीक वही दिखता है जो मूल run ने देखा था, इसलिए अगर वह वही विफलता दोहराता है, तो आपने पुष्टि कर ली। अगर वह सफल होता है, तो आपने मूल harness या माहौल की समस्या पाई, agent के तर्क की नहीं।

**विफलता से आगे बढ़ें**: आप वह turn पहचानते हैं जहाँ चीज़ें ग़लत हुईं (turn 12)। आप turn 11 तक की trajectory सहेजते हैं, फिर उसे थोड़ा बदलते हैं (शायद transcript में नोट जोड़ें, या tool का नतीजा बदलें) और turn 12 से replay करते हैं। Model, बदला हुआ input देखकर, अलग रास्ता ले सकता है। इससे आप पूरे agent को turn 1 से फिर चलाए बिना परख सकते हैं "अगर वह tool का नतीजा ज़्यादा साफ़ होता तो?"

**निदान पर मिलकर काम करें**: कोई सहकर्मी पूछता है "turn 28 पर agent क्यों फेल हुआ?" आप उन्हें turn 27 तक की trajectory और इसका वर्णन देते हैं कि आप उन्हें क्या देखने को कह रहे हैं। वे आपसे स्वतंत्र होकर उसे ख़ुद replay करके अपने निष्कर्ष पर पहुँच सकते हैं। आप ठीक वही state साझा कर रहे हैं, सिर्फ़ उसका वर्णन नहीं।

**Regression test बनाएँ**: आपने bug पाया और ठीक किया। जिस trajectory ने bug उकसाया उसे सहेजें, ठीक किए harness के साथ replay करें, और पुष्टि करें कि अब वह सफल होती है। इसे अपने test suite में जोड़ें ताकि bug वापस न आए।

### व्यावहारिक replay का design

Trajectory replay डिज़ाइन करते समय कुछ ब्योरे मायने रखते हैं:

**पूरा transcript सहेजें**, जिसमें हर turn, हर tool call, हर नतीजा, हर error हो। काटें या नमूना न लें; replay पर सही तर्क करने के लिए model को पूरा context चाहिए।

**Harness का metadata अलग, संरचित खंड में रखें**: turn की संख्या, token की गिनतियाँ, error की गिनतियाँ, जाँची गई stopping conditions। इससे आप ठीक state दोबारा बना सकते हैं, भले ही आपने transcript में सब कुछ न सहेजा हो।

**हर span का timestamp लगाएँ** ताकि आप देख सकें कि हर operation में कितना समय लगा और क्या कोई अस्पष्ट अंतराल हैं (network latency, retries, backoffs)।

**Replay को configure करने योग्य बनाएँ**: किसी को turn N से replay करने दें, या बदले हुए transcript के साथ replay करने दें (काल्पनिक स्थितियाँ परखने के लिए), या अलग model के साथ replay करने दें ताकि देखें कि व्यवहार बदलता है या नहीं।

### दूसरे निदान औज़ारों से संबंध

संरचित traces trajectories को ध्यान से पढ़ने की जगह नहीं लेते। वे उसके पूरक हैं। आपको अब भी पाठ 27 और 28 के failure modes (loops, poisoning, cascades) समझने होंगे ताकि जान सकें कि आप कौन-से patterns खोज रहे हैं। पर संरचित trace patterns को देखना आसान और निकालना तेज़ बनाता है।

मिलकर, वे एक अनुशासन बनाते हैं: trajectory में तेज़ी से घूमने के लिए traces इस्तेमाल करें, जो मायने रखता है उसे पहचानने के लिए failure modes का अपना ज्ञान इस्तेमाल करें, और अपने निदान की पुष्टि के लिए replay इस्तेमाल करें।

## अभ्यास

1. ▢ आप agent run का संरचित trace पढ़ रहे हैं। Trace दिखाता है: turn 1 (model call), turn 2 (search_files को tool call), turn 3 (model call), turn 4 (एक जैसे arguments के साथ search_files को tool call), turn 5 (model call), turn 6 (फिर search_files को tool call)। आप हर span का tool result जाँचते हैं और वे एक जैसे हैं। सिर्फ़ trace की बनावट के आधार पर, आपको कौन-से failure mode पर शक करना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

यह पाठ 27 के दोहराव वाले loop जैसा दिखता है: turns 2, 4 और 6 में वही tool एक जैसे arguments के साथ call हो रहा है, और नतीजे एक जैसे हैं। संरचित trace इसे साफ़ कर देता है क्योंकि हर turn और tool call लेबल की हुई है। असंरचित log में आपको कई पंक्तियों में tool का नाम और arguments हाथ से खोजने पड़ते।

</details>

2. ▢ आप turn 30 की विफलता debug करने के लिए turn 15 से trajectory replay कर रहे हैं। आप turn 14 तक का transcript model को वापस देते हैं और उससे जारी रखने को कहते हैं। आपके replay में agent मूल से अलग रास्ता लेता है और सफल होता है। यह मूल विफलता के बारे में क्या बताता है?

<details markdown="1"><summary>संकेत</summary>

सोचें कि मूल run और replay के बीच model के फ़ैसले के अलावा क्या बदला।

</details>

<details markdown="1"><summary>जाँचें</summary>

मूल विफलता शायद turns 15 से 29 में harness या माहौल की किसी चीज़ से हुई थी, model की reasoning से नहीं। संभावित कारण: कोई tool जिसने मूल run में अपेक्षा से अलग व्यवहार किया, क्षणिक विफलता (network की समस्या, service का बंद होना, quota पार), या कोई अनिर्धारित तत्व (tool के नतीजों या model के sampling में यादृच्छिकता)। चूँकि replay उसी transcript और model के साथ सफल हुआ, समस्या model की training या reasoning की नहीं थी; वह बाहरी परिस्थितियाँ थीं। यह निदान की वह अंतर्दृष्टि है जो आपको सिर्फ़ trajectory दोबारा पढ़ने से नहीं मिलती।

</details>

3. ▢ आप OpenTelemetry conventions इस्तेमाल करके अपने agent harness के लिए संरचित trace schema डिज़ाइन कर रहे हैं। Tool call span के लिए, इनमें से कौन-सा attribute cascade विफलता (पाठ 28) के निदान के लिए सबसे ज़रूरी है?

    - a) Tool का नाम और arguments
    - b) Tool का नतीजा या error संदेश
    - c) Tool call की wall-clock अवधि
    - d) Model का version जिसने tool call किया

<details markdown="1"><summary>जाँचें</summary>

**b)** Tool का नतीजा या error संदेश cascades के निदान के लिए सबसे ज़रूरी है। Cascade तब शुरू होता है जब model error का ग़लत निदान करता है, इसलिए आपको ठीक वह error संदेश देखना होगा जो लौटाया गया था। साफ़ error संदेश के साथ, आप जाँच सकते हैं कि model का अगला फ़ैसला उस error का समझदार जवाब था या नहीं। Tool का नाम और arguments (a) गौण हैं; वे दिखाते हैं कि model ने क्या आज़माया, पर यह नहीं कि उसने विफलता समझी या नहीं। अवधि (c) और model का version (d) performance के विश्लेषण और regression की पहचान के लिए काम के हैं, पर cascade के निदान के लिए प्राथमिक नहीं।

</details>

4. ▢ आपने turn 10 तक की trajectory सहेजी है, और आप परिकल्पना परखना चाहते हैं: "अगर turn 5 के tool result में customer ID शामिल होती, तो agent turns 6 से 10 में loop में फँसने की जगह सफल हो जाता।" इस परिकल्पना को परखने के लिए आप trajectory को कैसे बदलेंगे और replay करेंगे?

<details markdown="1"><summary>जाँचें</summary>

आप transcript को संपादित करेंगे: turn 5 का tool result ढूँढें, और उसमें customer ID की जानकारी जोड़ें। उदाहरण के लिए, "Tool result: success" को "Tool result: successfully created account; customer ID is 98765" में बदलें। फिर इस बदले हुए transcript के साथ turn 6 से replay करें। अगर agent अब सफल होता है, तो आपकी परिकल्पना की पुष्टि हो गई: ग़ायब जानकारी मूल कारण थी। अगर वह अब भी loop करता है, तो समस्या कहीं और है।

</details>

## असली दुनिया का अभ्यास

- [ ] जिस agent तक आपकी पहुँच है, उसके लिए बुनियादी trace capture सेट करें। कम से कम एक run के लिए trace export करें और उसकी बनावट जाँचें। पहचानें: क्या वह संगत schema का पालन करता है? क्या आप सारी model calls और सारी tool calls जल्दी खोज सकते हैं? क्या query भाषा (जैसे "सारी फेल हुई tool calls" छानना) debugging के लिए काम की होती?

- [ ] Agent run की trajectory सहेजें (कम से कम 5 turns)। उसे बीच से (turn 3 या 4 से) replay करें और देखें कि replay वही नतीजे देता है या अलग। अगर अलग, तो खोजें क्यों।

- [ ] कल: ऐसा स्वचालित नियम डिज़ाइन करें जो संरचित trace में पाठ 27 या 28 का एक failure mode पहचाने। Pseudocode या SQL लिखें जो trace को query करे और विफलता चिह्नित करे। उदाहरण के लिए, "चिह्नित करें अगर वही tool लगातार turns में एक जैसे arguments के साथ दो बार से ज़्यादा call हो"।

## आगे बढ़ने के लिए

- [विनिर्देश: "Semantic Conventions for Generative AI", OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
