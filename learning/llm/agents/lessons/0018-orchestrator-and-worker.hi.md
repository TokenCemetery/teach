---
title: "18. Orchestrator और Worker"
description: ऐसा multi-agent system डिज़ाइन करें जिसमें एक agent योजना बनाकर काम सौंपे और workers parallel में चलाएँ
type: lesson
---

# पाठ 18. Orchestrator और Worker

**मिशन से संबंध:** एक अच्छी तरह लैस agent और multi-agent system में से चुनने के लिए, आपको समझना होगा कि multi-agent systems ऐसा क्या कर सकते हैं जो अकेले agents नहीं कर सकते, और इसकी शुरुआत orchestrator-worker pattern से होती है जो ज़्यादातर multi-agent शोध और planning systems को चलाता है।
**मुख्य स्रोत:** [लेख: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
**पूर्व-आवश्यकताएँ:** [पाठ 17](0017-self-critique-and-reasoning-models.md), [Sub-agent](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 17 से याद करें: असफल प्रयास के बाद स्पष्ट reflection loop क्या करता है, और लंबी भीतरी reasoning वाले model को उस बाहरी loop की ज़रूरत सामान्य model से कम क्यों पड़ती है?

<details markdown="1"><summary>जाँचें</summary>

स्पष्ट reflection loop प्राकृतिक भाषा में आलोचना बनाता है कि प्रयास क्यों फेल हुआ और उस आलोचना को अगले प्रयास में ले जाता है, model के अपने turn से अलग चरण के रूप में। जो model उत्तर देने से पहले लंबी भीतरी reasoning करता है वह उनमें से कुछ वही ग़लतियाँ एक ही turn के भीतर पकड़ सकता है, इसलिए बाहरी loop अपनी क़ीमत कम बार कमाता है, हालाँकि जब विफलता का संकेत (tool error, test का नतीजा) model के कार्रवाई कर चुकने के बाद ही मौजूद होता है तब भी वह मदद करता है।

</details>

2. ▢ पाठ 12 से याद करें: sub-agent क्या है, और उसका अलग transcript कौन-सी समस्या हल करता है?

<details markdown="1"><summary>जाँचें</summary>

Sub-agent अपने harness और transcript वाला अलग agent run है। वह context isolation हल करता है: आप किसी सीमित task पर केंद्रित sub-agent चला सकते हैं, और उस task का transcript parent agent के context को नहीं फुलाता, जिससे parent की reasoning तालमेल और संश्लेषण के लिए साफ़ रहती है।

</details>

## यह जानें

### Orchestrator-worker pattern

जब कोई task एक agent के context के लिए बहुत व्यापक हो या parallel खोजबीन माँगता हो, तो orchestrator-worker pattern काम बाँट देता है: एक agent (orchestrator) task को सीमित उप-कार्यों में तोड़ता है, तय करता है कि किस worker को कौन-सा उप-कार्य मिले, फिर उनके नतीजों को अंतिम उत्तर में जोड़ता है। हर worker अपने transcript और tools वाला sub-agent है, जो स्वतंत्र रूप से (और अक्सर parallel में) चलता है।

इसे ऐसे टीम लीड की तरह सोचें जो काम सीधे नहीं करता पर तालमेल बिठाता है: लीड प्रोजेक्ट तोड़ता है, टीम के सदस्यों को हिस्से सौंपता है, और उनके नतीजे जोड़ता है। Workers एक-दूसरे की पूरी reasoning कभी नहीं देखते; orchestrator सिर्फ़ उनकी अंतिम रिपोर्टें देखता है।

### Workers क्या करते हैं

Workers आपस में बदले नहीं जा सकते। हर worker के पास आमतौर पर होता है:

- सीमित, ख़ास मिशन (जैसे "इस एक पहलू पर शोध करो", "इस उम्मीदवार तरीक़े का मूल्यांकन करो")
- उस मिशन के हिसाब से बने tools (जैसे शोध करने वाले worker के लिए retrieval, मूल्यांकन करने वाले worker के लिए code execution)
- अपना agent loop और transcript, जो दूसरे workers से अलग है

क्योंकि workers अपने loops चलाते हैं, वे स्वतंत्र रूप से खोजबीन कर सकते हैं। Worker को जानने की ज़रूरत नहीं कि दूसरे workers क्या कर रहे हैं; वह सिर्फ़ अपना task जानता है। यही स्वतंत्रता parallelism संभव बनाती है: कई workers एक साथ चल सकते हैं, wall-clock समय सबसे धीमे worker से बँधा होता है, सभी workers के समयों के योग से नहीं।

### Fan-out: parallel खोजबीन

Fan-out orchestrator-worker का उप-मामला है जहाँ orchestrator एक ही सवाल के अलग-अलग रूपों पर कई workers चला देता है। उदाहरण के लिए:

- एक worker पहलू A पर शोध करता है, दूसरा पहलू B पर, तीसरा पहलू C पर, सब parallel में, ताकि एक अकेले agent के उन्हें क्रम से निपटाने से तेज़ी से व्यापक कवरेज मिले।
- तीन workers हर एक अलग रणनीति से वही coding समस्या हल करने की कोशिश करते हैं, और orchestrator सबसे अच्छा हल चुनता है या अंतर्दृष्टियाँ मिलाता है।

गति में फ़ायदा असली है: अकेले agent के समस्या-A पर 10 turns, फिर समस्या-B पर 10 turns, फिर समस्या-C पर 10 turns (कुल 30 turns) लगाने की जगह, तीन workers A, B और C को parallel में निपटाते हैं (30 की जगह 10 turns की latency)। पेच (पाठ 19 में देखा गया) यह है कि आप तीनों workers के पूरे runs की token cost चुकाते हैं, सिर्फ़ एक agent के run की नहीं।

### Handoff: क्रमवार विशेषज्ञता

Handoff अलग multi-agent pattern है, जो sub-agents भी इस्तेमाल करता है पर parallel workers की जगह क्रमवार चरणों के साथ। Handoff में:

1. Agent A अपने हिस्से का task पूरा करता है।
2. Agent A साफ़, सीमित context देकर Agent B को सौंपता है: आमतौर पर बस task की परिभाषा और Agent A के अंतिम निष्कर्ष, Agent A की पूरी trajectory नहीं।
3. Agent B वहाँ से आगे बढ़ता है, अपने विशेष tools और reasoning के साथ।

Handoff तब काम का है जब task स्वाभाविक रूप से क्रमवार चरणों में बँटता है जिन्हें अलग विशेषज्ञ सँभालते हैं। उदाहरण के लिए: orchestrator पाता है कि समस्या में गहरे शोध और implementation दोनों चाहिए, इसलिए वह निष्कर्ष किसी विशेष coder को सौंपता है; या planner योजना पूरी करके उसे executor को सिर्फ़ योजना के साथ सौंपता है, यह बिखरी reasoning नहीं कि वह योजना क्यों चुनी गई।

Handoff और fan-out लय में उलटे हैं: fan-out में बहुत-से parallel हैं, handoff में एक के बाद एक। दोनों multi-agent हैं; दोनों sub-agents से context अलग करते हैं; दोनों इस पाठ में सिखाए गए हैं क्योंकि दोनों इस सवाल का जवाब देते हैं कि "एक agent कब काफ़ी नहीं है?"

### Orchestrator-worker systems व्यवहार में मूल्य कैसे देते हैं

मुख्य स्रोत Anthropic में बने ठोस multi-agent शोध system का ब्योरा देता है: जटिल शोध task को कई स्वतंत्र उप-शोध tasks में तोड़ना, हर एक के लिए worker चलाना, स्रोत parallel में लाना और विश्लेषित करना, फिर निष्कर्षों को एकजुट उत्तर में जोड़ना। मुख्य जीतें थीं:

- Wall-clock समय में parallelism: जटिल शोध जिस पर अकेला agent 50+ turns लगाता, वह 5 workers के साथ, हर एक के 15 turns, एक साथ चलकर तेज़ हो सकता था।
- हर worker के लिए विशेष tools: retrieval worker code execution से context फुलाए बिना search और ranking पर ध्यान दे सकता है; संश्लेषण करने वाले worker का लक्ष्य अलग है और tools अलग।
- स्वतंत्र reasoning: हर worker समस्या के अपने हिस्से पर तर्क करता है; workers उस जानकारी से नहीं भटकते जो दूसरे workers के लिए है।

यह pattern असली बंदिश के व्यावहारिक हल के रूप में उभरा: जटिल task पर अच्छी reasoning करने की model की क्षमता आंशिक रूप से context की लंबाई से और आंशिक रूप से reasoning को केंद्रित रखने की ज़रूरत से बँधी है। काम बाँटने से आप ज़्यादा reasoning शक्ति जोड़ सकते हैं (ज़्यादा workers, हर एक का अपना context budget) बिना किसी अकेले agent का ध्यान या context ख़त्म हुए।

## अभ्यास

1. ▢ आप बड़े codebase के बारे में उपयोगकर्ताओं के सवालों के जवाब देने वाला system बना रहे हैं। आप दो designs पर विचार करते हैं: (A) code search tools और दस्तावेज़ tools तक पहुँच वाला एक अकेला agent, या (B) orchestrator जो search worker और दस्तावेज़ worker को parallel में काम सौंपता है। कौन-सा design orchestrator-worker pattern में ज़्यादा स्वाभाविक रूप से बैठता है, और क्यों?

<details markdown="1"><summary>जाँचें</summary>

Design (B) pattern में बैठता है। Search worker और दस्तावेज़ worker के स्वतंत्र tasks हैं: एक code खोजता है, दूसरा docs। वे बिना task के बीच में एक-दूसरे के नतीजों की ज़रूरत के parallel में चल सकते हैं। Orchestrator का काम साफ़ है: हर worker के लिए queries बनाना, फिर उनके निष्कर्ष जोड़ना।

Design (A) भी काम कर सकता है, पर अकेले agent को task के बीच में तय करना पड़ेगा कि अगला कौन-सा tool इस्तेमाल करे; parallelism का कोई फ़ायदा नहीं। आप (B) तब चुनेंगे जब आपको उम्मीद हो कि search और दस्तावेज़ की queries स्वतंत्र हैं और parallel खोजबीन से फ़ायदा होगा; आप (A) तब चुनेंगे जब queries एक-दूसरे पर निर्भर हों (search के नतीजे तय करते हैं कि कौन-सा दस्तावेज़ लाना है) या जब दो sub-agents चलाने का अतिरिक्त बोझ गति के फ़ायदे से ज़्यादा हो (सरल task)।

</details>

2. ▢ Orchestrator-worker system में, कोई worker task के बीच दूसरे worker की reasoning सीधे क्यों नहीं देख सकता?

<details markdown="1"><summary>संकेत</summary>

ढाँचे के बारे में सोचें: हर worker का अपना transcript और harness है। वह अलगाव क्या रोकता है?

</details>

<details markdown="1"><summary>जाँचें</summary>

हर worker अपने transcript के साथ अपना agent loop चलाता है। Worker A की reasoning Worker A के transcript में दर्ज होती है, और Worker B की reasoning Worker B के transcript में। Harness उन्हें मिलाता नहीं। Workers अपने runs के दौरान एक-दूसरे के transcripts तक नहीं पहुँच सकते; वे सिर्फ़ वही अंतिम रिपोर्टें पढ़ सकते हैं जो orchestrator उन्हें देता है (अगर orchestrator पास करे)। यह अलगाव हर worker के context को केंद्रित रखता है और इसीलिए sub-agents context की समस्याएँ हल करते हैं। समझौता है बिखराव: ऐसा फ़ैसला जिसमें दोनों workers की पूरी reasoning चाहिए, कोई अकेला worker नहीं ले सकता (पाठ 19 में देखा गया)।

</details>

3. ▢ आप शोध system डिज़ाइन कर रहे हैं। परिदृश्य: एक worker किसी तकनीक के इतिहास पर शोध कर रहा है, और दूसरा worker उस तकनीक के मौजूदा उपयोगों पर। क्या इन workers के tasks parallel में चल सकते हैं?

    - a) नहीं, क्योंकि उपयोग वाले worker को पहले इतिहास जानना होगा।
    - b) हाँ, दोनों workers स्वतंत्र रूप से शोध कर सकते हैं; orchestrator क्रम की परवाह किए बिना इतिहास और उपयोगों के निष्कर्ष जोड़ सकता है।
    - c) नहीं, क्योंकि वे एक ही तकनीक पर शोध कर रहे हैं।
    - d) हाँ, पर तभी जब इतिहास वाला worker उपयोग वाले worker के शुरू होने से पहले ख़त्म हो।

<details markdown="1"><summary>जाँचें</summary>

**b)** दोनों tasks स्वतंत्र हैं: इतिहास पर शोध करने वाले worker को इतिहास पर अच्छा शोध करने के लिए दूसरे worker के निष्कर्षों की ज़रूरत नहीं, और उल्टा भी। जब दोनों workers ख़त्म होंगे तो orchestrator के पास दोनों नतीजे होंगे और वह उन्हें पूरे उत्तर में जोड़ सकता है। (a) ग़लत है: निर्भरताएँ एक के बाद एक चलेंगी (handoff), fan-out नहीं; यहाँ कोई निर्भरता नहीं है। (c) ग़लत है: एक ही तकनीक पर शोध करना parallelism में रुकावट नहीं है; असल में इसीलिए fan-out काम का है, एक ही विषय पर कई पहलू पाने के लिए। (d) ग़लत है: parallelism का मतलब है कि वे एक ही समय में चलते हैं, एक के बाद एक नहीं।

</details>

4. ▢ Handoff fan-out से किस तरह अलग है?

<details markdown="1"><summary>जाँचें</summary>

Fan-out parallel है: orchestrator एक ही समस्या के अलग-अलग रूपों पर एक साथ कई workers चला देता है। Handoff क्रमवार है: एक agent ख़त्म करता है, फिर अपने निष्कर्ष अगले चरण के लिए बने दूसरे agent को सौंपता है। Fan-out पूछता है "हम parallel में ज़्यादा पहलू कैसे खोज सकते हैं?"; handoff पूछता है "हम क्रमवार प्रक्रिया को विशेष चरणों में कैसे बाँट सकते हैं?" दोनों sub-agents इस्तेमाल करते हैं; दोनों context अलग करते हैं; दोनों "एक agent कब काफ़ी नहीं है?" का जवाब देते हैं पर अलग लय में।

</details>

## असली दुनिया का अभ्यास

- [ ] अगली बार जब आप कोई जटिल task देखें (शोध, planning, debugging), तो खींचें कि वह orchestrator-worker में बैठता है (क्या स्वतंत्र उप-कार्य हैं जो parallel में चल सकते हैं?), handoff में (क्या अलग विशेषज्ञों के क्रमवार चरण हैं?), या ज़्यादा tools वाले एक अकेले agent में (क्या एक agent बेहतर tools और ज़्यादा turns से कर सकता है?)। कुछ बनाएँ नहीं; बस आकार पहचानने का अभ्यास करें।
- [ ] मुख्य स्रोत का लेख पढ़ें: "How We Built Our Multi-Agent Research System"। उस खंड पर ध्यान दें जो बताता है कि orchestrator ने क्या किया, हर worker ने क्या किया, और अगर वे अकेला agent इस्तेमाल करते तो क्या बदलता। उनके बताए parallelism के एक ठोस फ़ायदे पर notes लें।
- [ ] कल: अपने काम या पढ़ाई का असली task बताएँ जिसे fan-out से फ़ायदा होता (कई workers एक ही समस्या को parallel में खोजते)। हर worker कौन-सा पहलू लेता? हर एक को कौन-से tools चाहिए होते?

## आगे बढ़ने के लिए

- [लेख: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
