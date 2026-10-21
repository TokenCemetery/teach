---
title: "12. Context Isolation के रूप में Sub-Agents"
description: Sub-agent चलाने से लंबा खोजबीन वाला काम parent के context budget से अलग रहता है
type: lesson
---

# पाठ 12. Context Isolation के रूप में Sub-Agents

**मिशन से संबंध:** असफल agent को उसकी trajectory से जाँचें, उसके prompt में एक और instruction जोड़ने के बजाय।
**मुख्य स्रोत:** [लेख: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
**पूर्व-आवश्यकताएँ:** [पाठ 11](0011-compaction-and-retrieval-on-demand.md)

## वार्म-अप

1. ▢ Compaction और retrieval on demand में क्या अंतर है?

<details markdown="1"><summary>जाँचें</summary>

Compaction पुराने turns को सारांश से बदलती है, tokens बचाती है पर जानकारी खोने का जोखिम रखती है। Retrieval on demand पुराना ब्योरा context से बाहर रखती है और model के माँगने पर ही लाती है, resident context छोटा रखने के बदले थोड़ी latency चुकाती है।

</details>

2. ▢ Compaction और retrieval on demand में, हमेशा मौजूद रहने वाले context में कौन-सी तीन चीज़ें होती हैं?

<details markdown="1"><summary>जाँचें</summary>

लक्ष्य और बंदिशें, प्रगति का सारांश, और metadata (file के नाम, उपलब्ध tools, document के शीर्षक)। पूरा ब्योरा दबा हुआ है (compaction) या माँगने पर उपलब्ध (retrieval)।

</details>

## यह जानें

### Context-प्रबंधन के औज़ार के रूप में Sub-agents

अब तक पाठ 10 और 11 एक अकेले agent के transcript को सँभालने पर केंद्रित थे। पर एक और तरीक़ा है: किसी सीमित काम के लिए अलग agent चलाना। यह चरण 8 (multi-agent) है, पर यहाँ सिर्फ़ context-budget के पहलू तक सीमित है।

Sub-agent एक नया agent run है जिसका अपना transcript, अपना harness और अपना tool set है। वह खोजबीन करता है, tool calls करता है, अपनी trajectory जमा करता है। इस बीच parent agent ने उस खोजबीन में से किसी की भी क़ीमत नहीं चुकाई। Sub-agent का कोई भी turn parent के transcript में नहीं दिखता।

जब sub-agent ख़त्म करता है, तो वह अंतिम नतीजा या सारांश बनाता है। वह सारांश (बस कुछ वाक्य या data structure) parent के transcript में जोड़ा जाता है। Sub-agent की पूरी भीतरी reasoning, उसके सारे बंद रास्ते, सारी tool calls और विफलताएँ, parent के context से बाहर रहती हैं।

### मुख्य अंतर्दृष्टि: बड़ी, अलग की हुई trajectory parent को कुछ नहीं पड़ती

मान लें sub-agent 100 turns files पढ़ने, patterns की तुलना करने, बंद रास्तों से टकराने और अपना विश्लेषण निखारने में लगाता है। उसकी trajectory विशाल है। पर parent के नज़रिए से वह सारा काम अदृश्य है। Parent को सिर्फ़ अंतिम रिपोर्ट दिखती है, कुछ सौ tokens की। इस बीच parent का context छोटा और सस्ता रहता है।

यह compaction और retrieval on demand से अलग है, जो दोनों एक ही transcript के भीतर काम करते हैं। Sub-agent parent के transcript के पूरी तरह बाहर काम करता है। उसकी cost sub-agent का harness उठाता है, parent का नहीं।

### समझौता: अदृश्य reasoning का मतलब खोए हुए ब्योरे

क्योंकि sub-agent की भीतरी reasoning parent को नहीं दिखती, जो जानकारी parent ने माँगने की नहीं सोची वह खो सकती है। अगर parent sub-agent को "ये files पढ़ो और सारांश बनाओ" के लिए चलाता है, तो sub-agent कोई दिलचस्प पर गौण चीज़ खोज सकता है: "मैंने util.cpp में memory leak भी देखा।" अगर parent ने वह नहीं माँगा था, तो sub-agent उसे रिपोर्ट से छोड़ सकता है, और parent को उसका कभी पता नहीं चलता।

यह compaction के जोखिम से अलग है, जहाँ harness तय करता है कि क्या संक्षिप्त होगा। Sub-agent में "क्या वापस रिपोर्ट करें" और "क्या भीतर रखें" की सीमा sub-agent का अपना चुनाव है। अगर sub-agent language model है, तो वह मिले instructions के आधार पर अंदाज़ा लगाएगा कि parent को किसकी परवाह है। वह अंदाज़ा ग़लत हो सकता है।

### Sub-agent कब फ़ायदेमंद है, कब नहीं

Coordination की क़ीमत के लायक़ sub-agent तब है जब:

- उप-कार्य बड़ा है और लंबी trajectory जमा करेगा (कई turns, कई tool calls, कई बंद रास्ते)।
- उप-कार्य सीमित है: रुकने का साफ़ बिंदु है और parent को आगे के काम के लिए sub-agent की reasoning की ज़रूरत नहीं पड़ेगी।
- नया agent चलाने की क़ीमत (latency, coordination का अतिरिक्त बोझ) sub-agent की खोजबीन को parent के context में रखने की क़ीमत से बहुत कम है।

उदाहरण: "इस codebase का इतिहास खोजो, git log और बड़े PRs पढ़ो, और मुझे तीन वाक्य का सारांश दो।" यह बड़ा, सीमित task है। 50 turns खोजबीन करने वाला sub-agent parent के 50 turns की context cost बचाता है।

Sub-agent तब फ़ायदेमंद नहीं है जब:

- Task छोटा है (वैसे भी कुछ ही turns लेगा)।
- Task में parent के साथ कसा हुआ तालमेल चाहिए (parent स्पष्टीकरण के सवाल पूछेगा, sub-agent को अपना काम निखारना होगा)।
- Parent को बाद में sub-agent की पूरी reasoning चाहिए होगी (यह समझने के लिए कि निष्कर्ष कैसे निकला, कोई धारणा पकड़ने के लिए, गलती debug करने के लिए)।

उदाहरण: "कल का तापमान ले आओ।" यह कुछ turns का task है; sub-agent चलाना parent में ही कर लेने से ज़्यादा क़ीमत लेता है।

## अभ्यास

1. ▢ एक agent को 50 files का code review करके रिपोर्ट बनानी है। Developer ने काम बाँट दिया है: मुख्य agent 5 files की समीक्षा करता है, और बाक़ी 45 के लिए sub-agent चलाता है। यह sub-agent का अच्छा इस्तेमाल क्यों है?

    - a) Sub-agents हमेशा अकेले agents से तेज़ होते हैं
    - b) Sub-agent की लंबी trajectory (45 files की समीक्षा) मुख्य agent के context से अलग रहती है, जिससे मुख्य context छोटा और सस्ता रहता है
    - c) Sub-agents कभी ग़लती नहीं करते
    - d) मुख्य agent sub-agent की सारी reasoning तुरंत देख सकता है

<details markdown="1"><summary>जाँचें</summary>

**b)** Sub-agent मुख्य agent को बड़ा, सीमित task उतारने देता है। Sub-agent के 100+ turns की खोजबीन मुख्य agent के context को नहीं फुलाती। मुख्य agent को सिर्फ़ sub-agent की अंतिम रिपोर्ट मिलती है। विकल्प a ग़लत है क्योंकि sub-agents latency जोड़ सकते हैं। विकल्प c ग़लत है क्योंकि sub-agents ग़लतियाँ कर सकते हैं। विकल्प d ग़लत है क्योंकि sub-agent की भीतरी reasoning मुख्य agent को अदृश्य है।

</details>

2. ▢ एक sub-agent codebase की समीक्षा कर रहा है और उसे security की कमज़ोरी मिलती है। वह उस task से सीधे जुड़ी नहीं है जो parent ने माँगा था (code style की समीक्षा), पर वह गंभीर है। Sub-agent का अदृश्य होना यहाँ कौन-सा जोखिम पैदा करता है?

<details markdown="1"><summary>संकेत</summary>

Sub-agent के instructions ने उसे code style पर ध्यान देने को कहा था। Parent को क्या वापस रिपोर्ट किया जाए यह कौन तय करता है, और क्या खो सकता है?

</details>

<details markdown="1"><summary>जाँचें</summary>

Sub-agent अपने instructions के आधार पर तय करता है कि अंतिम रिपोर्ट में क्या डालना है। अगर instructions code style पर ज़ोर देते हैं, तो sub-agent security की समस्या की रिपोर्ट शायद करे ही नहीं, या उसे ऐसी footnote में लिखे जिसे parent चूक जाए। जो जानकारी parent ने माँगने की नहीं सोची वह खो सकती है क्योंकि parent को sub-agent की पूरी reasoning कभी दिखती नहीं। Parent को बहुत साफ़ होना पड़ेगा: "जो भी गंभीर मिले उसकी रिपोर्ट करें, style हो या नहीं।"

</details>

3. ▢ लंबे शोध task के दो तरीक़ों की तुलना करें:
    - तरीक़ा A: एक अकेला agent जो पुराने turns compact करता है और retrieval on demand इस्तेमाल करता है। 80 turns लगते हैं, resident context 30,000 tokens से कम रहता है।
    - तरीक़ा B: मुख्य agent parallel में खोजबीन के लिए 3 sub-agents चलाता है। हर एक भीतर 40 turns लेता है। मुख्य agent को हर एक से सारांश मिलता है। मुख्य agent का अंतिम context 5,000 tokens और coordination का अतिरिक्त बोझ है।

किस तरीक़े की कुल token cost कम है (सभी agent runs गिनकर), और क्यों?

    - a) तरीक़ा A, क्योंकि वह sub-agent का अतिरिक्त बोझ टालता है
    - b) तरीक़ा B, क्योंकि तीनों खोजबीन अलग हैं और मुख्य agent के लिए सस्ती हैं
    - c) दोनों की cost बराबर है
    - d) इस पर निर्भर है कि coordination का अतिरिक्त बोझ कितना है

<details markdown="1"><summary>जाँचें</summary>

**d)** तरीक़ा A model को 30,000 tokens 80 बार भेजता है, लगभग 2.4M tokens। तरीक़ा B हर sub-agent में model को लगभग 50,000 tokens 40 बार भेजता है, साथ में मुख्य agent के साथ coordination। अगर coordination कम है और sub-agents का काम सचमुच parallel और सीमित है, तो तरीक़ा B सस्ता हो सकता है। पर अगर coordination महँगा है या sub-agents को अपने नतीजे बार-बार निखारने पड़ते हैं, तो तरीक़ा A बेहतर हो सकता है। उत्तर sub-agents को चलाने और उनके तालमेल की असली क़ीमत पर निर्भर है।

</details>

4. ▢ आप ऐसा agent डिज़ाइन कर रहे हैं जो "इस फेल हो रही test suite को debug करे और fix सुझाए।" क्या आपको sub-agent इस्तेमाल करना चाहिए, और क्यों या क्यों नहीं?

<details markdown="1"><summary>जाँचें</summary>

नहीं। Debugging ऐसा task है जिसमें parent को शायद सुझाए fix के सुरक्षित होने का फ़ैसला करने, धारणाएँ पकड़ने, या स्पष्टीकरण के सवाल पूछने के लिए sub-agent की पूरी reasoning चाहिए होगी। यह सीधी रिपोर्ट वाला सीमित task नहीं है; इसमें कसा हुआ तालमेल चाहिए। Sub-agent की अदृश्य reasoning बोझ बन जाती। Debugging को parent के मुख्य loop में रखना बेहतर है जहाँ parent पूरी trajectory देख सके।

</details>

## असली दुनिया का अभ्यास

- [ ] ऐसा task बताएँ जहाँ आप sub-agent इस्तेमाल करेंगे और समझाएँ कि बड़ी, अलग की हुई trajectory coordination की क़ीमत के लायक़ क्यों है।
- [ ] ऐसा task बताएँ जहाँ आप sub-agent इस्तेमाल नहीं करेंगे, और समझाएँ कि करने पर कौन-सी जानकारी खो जाती।
- [ ] कल: बहु-हिस्सों वाले task (जैसे "इस library पर शोध करो, फिर उसे हमारे codebase में जोड़ो") के लिए parent और sub-agent की ज़िम्मेदारियाँ खींचें। सीमा कहाँ जाती है, और हर agent दूसरे को क्या रिपोर्ट करता है?

## आगे बढ़ने के लिए

- [लेख: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
