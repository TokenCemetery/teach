---
title: "13. Scratchpad बनाम Memory"
description: एक run के दौरान agent के रखे notes और कई runs में ज़रूरी तथ्यों का अंतर
type: lesson
---

# पाठ 13. Scratchpad बनाम Memory

**मिशन से संबंध:** असफल agent को उसकी trajectory से जाँचें, उसके prompt में एक और instruction जोड़ने के बजाय, यह समझकर कि कौन-सी जानकारी runs के पार टिकती है और कौन-सी run ख़त्म होते ही मिट जाती है।
**मुख्य स्रोत:** [लेख: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**पूर्व-आवश्यकताएँ:** [पाठ 12](0012-sub-agents-as-context-isolation.md), [Trajectory](../GLOSSARY.md)

## वार्म-अप

1. ▢ Trajectory क्या दर्ज करती है?

<details markdown="1"><summary>जाँचें</summary>

एक agent run का पूरा क्रमबद्ध रिकॉर्ड: model को भेजा हर message, model की की हुई हर tool call, और harness के वापस जोड़े हुए हर नतीजे।

</details>

2. ▢ जब आप किसी सीमित काम के लिए sub-agent चलाते हैं, तो क्या sub-agent parent का पूरा transcript देखता है?

<details markdown="1"><summary>जाँचें</summary>

नहीं। Sub-agent को अपना नया transcript मिलता है जिसका इतिहास ख़ाली होता है। उसे parent agent के शुरुआती prompt के रूप में दिया गया सारांश या ख़ास context मिल सकता है, पर वह parent की पूरी trajectory विरासत में नहीं पाता।

</details>

## यह जानें

**Scratchpad** असल में transcript का ही हिस्सा है, या ऐसा नोट जो agent एक ही run के भीतर लिखता और वापस पढ़ता है। एक लंबे task के दौरान agent running total, कई चरणों की योजना या बीच के निष्कर्ष ट्रैक करने के लिए scratchpad इस्तेमाल कर सकता है ताकि model को उन्हें हर turn दोबारा निकालना न पड़े। Scratchpad क्षणिक है: जब harness loop रोकता है और run ख़त्म होता है, तो scratchpad trajectory में रहता है पर और कहीं नहीं। अगर आप एक घंटे बाद काम जारी रखने के लिए नया agent run शुरू करें, तो scratchpad जा चुका है।

यहीं एक आम उलझन शुरू होती है। Agent ने run के दौरान scratchpad रखा और कुछ "याद" रखा। वही agent, नए सिरे से शुरू होने पर, उसे याद नहीं रखेगा। Model scratchpad tool या file का वही नाम इस्तेमाल कर सकता है, पर सामग्री चली गई क्योंकि run चला गया।

**Across-run memory** बुनियादी रूप से अलग है। नया run ख़ाली transcript से शुरू होता है, इसलिए पिछले run से जो भी model को जानना है वह किसी एक trajectory के बाहर कहीं रहना चाहिए और अगला run शुरू होने पर जानबूझकर वापस लोड किया जाना चाहिए। Harness loop शुरू होने से पहले टिकाऊ storage से, यानी file, database या retrieval system से पढ़ता है, और प्रासंगिक तथ्य शुरुआती prompt या context में डालता है ताकि model उन पर काम कर सके।

एक ठोस उदाहरण: एक agent बड़े pull request का code review कर रहा है। एक घंटे के run के दौरान वह scratchpad रखता है जिसमें हर वह file दर्ज है जो वह जाँच चुका है, ताकि जब model नई file पर विचार करे तो scratchpad पर नज़र डालकर किया हुआ काम दोबारा विश्लेषित करने से बच सके। Scratchpad transcript का हिस्सा है। जब run ख़त्म होता है, तो review हो चुका होता है, और scratchpad trajectory के हिस्से के रूप में संग्रहीत हो जाता है।

अब दूसरा परिदृश्य सोचें: एक coding assistant एक अकेले उपयोगकर्ता को हफ़्तों तक कई अलग-अलग sessions में code लिखने में मदद करता है। उपयोगकर्ता की किसी ख़ास code style, naming convention और library के लिए मज़बूत पसंद है। अगर assistant हर session के लिए नए सिरे से शुरू होता है, तो वह उन पसंदों की किसी जानकारी के बिना शुरू करता है। Assistant को across-run memory चाहिए: एक file या नोट जिसे harness हर session की शुरुआत में पढ़े और जो कहे "उपयोगकर्ता X पसंद करता है, Y इस्तेमाल करता है, Z से बचता है।" वह तथ्य किसी एक trajectory में नहीं है; वह टिकाऊ ढंग से सहेजा गया है और run की शुरुआत में लोड होता है।

[लेख: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) की मुख्य अंतर्दृष्टि यह है कि ये दो अलग mechanisms हैं। Scratchpad ऐसा tool या artifact है जिसे agent run के दौरान सँभालता है। Across-run memory agent loop के बाहर की data परत है, जिसे harness सँभालता है।

## अभ्यास

1. ▢ एक agent कई चरणों वाला गणित का सवाल हल कर रहा है। Run के दौरान वह अपने काम के notes scratchpad file में लिखता है। अंत में वह अंतिम उत्तर results file में जोड़ता है। दिनों बाद आप उसी agent को दूसरे सवाल के साथ फिर शुरू करते हैं। इनमें से क्या अब भी मौजूद होगा?

    - a) Scratchpad के notes।
    - b) Results file।
    - c) दोनों, क्योंकि दोनों files हैं।
    - d) कोई नहीं, क्योंकि हर run पर files साफ़ हो जाती हैं।

<details markdown="1"><summary>जाँचें</summary>

**b)** Results file अब भी मौजूद होगी क्योंकि वह run के बाहर का टिकाऊ storage है। Scratchpad के notes, भले ही file में लिखे गए थे, सिर्फ़ पुराने run के लिए प्रासंगिक हैं और अपने आप नए transcript में लोड नहीं होते। अगर agent को नए run में वे पुराने notes चाहिए, तो harness को जानबूझकर उन्हें पढ़कर शुरुआती prompt में शामिल करना होगा।

</details>

2. ▢ आप ऐसा agent डिज़ाइन कर रहे हैं जिसे उन files के नाम याद रखने हैं जिन्हें वह पहले process कर चुका है। आप scratchpad इस्तेमाल करेंगे या across-run memory?

<details markdown="1"><summary>संकेत</summary>

सोचें कि जानकारी एक ही run के भीतर इस्तेमाल होती है या कई अलग runs में।

</details>

<details markdown="1"><summary>जाँचें</summary>

अगर सारी files एक लंबे run में process होती हैं, तो scratchpad काफ़ी है। Agent हर बार scratchpad जाँचता है और दोबारा process करने से बचता है। अगर काम कई agent runs में बँटा है, शायद हर दिन फिर शुरू होता है या हर उपयोगकर्ता अनुरोध पर एक run, तो आपको across-run memory चाहिए ताकि नया run देख सके कि पहले क्या हुआ।

</details>

3. ▢ नए harness के साथ फिर शुरू हुआ agent उन notes को क्यों नहीं देख पाता जो उसने पिछले run में scratchpad में लिखे थे, इसका बुनियादी कारण क्या है?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि scratchpad transcript का हिस्सा है, और नया run ख़ाली transcript से शुरू होता है। पुरानी trajectory संग्रहीत है पर नए run में लोड नहीं होती। Scratchpad की सामग्री को नए run में दिखाने के लिए harness को उसे storage से पढ़कर शुरुआती prompt में डालना होगा, जो उसे scratchpad से जानबूझकर बनाई गई across-run memory में बदल देता है।

</details>

4. ▢ आप ऐसा agent बना रहे हैं जो उपयोगकर्ता को निजी task list सँभालने में मदद करता है। Agent tasks जोड़ता है, पूरे करता है, और tag से filter करता है। क्या task list scratchpad होनी चाहिए, एक run तक सीमित, या across-run memory, runs के बीच सहेजी हुई? क्यों?

<details markdown="1"><summary>जाँचें</summary>

Across-run memory। Task list को एक session से आगे टिकना चाहिए। अगर उपयोगकर्ता कल agent शुरू करे और कहे "मेरे tasks दिखाओ", तो agent को आज की सूची अब भी दिखनी चाहिए। Scratchpad run ख़त्म होते ही ग़ायब हो जाता और उपयोगकर्ता का data खो जाता।

</details>

## असली दुनिया का अभ्यास

- [ ] अपने agent code को दो मिनट खंगालें। ढूँढें कि harness नया transcript कहाँ बनाता है, ख़ाली या सिर्फ़ शुरुआती prompt के साथ। जो दिखे वह लिख लें।
- [ ] कोई "memory" या "state" ढूँढें जो आपका agent अभी सहेजता है। क्या वह loop शुरू होने से पहले harness लोड करता है, या सिर्फ़ run के दौरान उसका हवाला दिया जाता है? अगर सिर्फ़ run के दौरान, तो वह scratchpad है। अगर शुरू होने के समय लोड होती है, तो वह across-run memory है।
- [ ] कल: scratchpad का एक इस्तेमाल खोजें या लिखें, जहाँ agent नोट लिखता है, उसे वापस पढ़ता है, फिर run ख़त्म हो जाता है। अलग से, across-run का एक इस्तेमाल खोजें या सोचें, जहाँ agent को आज के सवाल का जवाब देने के लिए पिछले हफ़्ते के run का कोई तथ्य चाहिए।

## आगे बढ़ने के लिए

- [लेख: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
