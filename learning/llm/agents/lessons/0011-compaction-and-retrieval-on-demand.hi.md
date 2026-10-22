---
title: "11. Compaction और Retrieval on Demand"
description: लंबे चलने वाले agent का context budget में रखने की दो रणनीतियाँ, जबकि जो अब भी मायने रखता है वह बचा रहे
type: lesson
---

# पाठ 11. Compaction और Retrieval on Demand

**मिशन से संबंध:** Agentic loop की token cost और latency का budget बनाएँ, और बताएँ कि amplification loop के किस हिस्से से आता है।
**मुख्य स्रोत:** [लेख: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**पूर्व-आवश्यकताएँ:** [पाठ 10](0010-the-context-window-as-budget.md)

## वार्म-अप

1. ▢ सीधी truncation (आकार की सीमा छूते ही सबसे पुराने turns हटा देना) जोखिम भरी क्यों है?

<details markdown="1"><summary>जाँचें</summary>

सीधी truncation ऐसा tool result, बंदिश या instruction हटा सकती है जिसकी model को अब भी ज़रूरत है, और model को पता नहीं चलेगा कि जानकारी ग़ायब है। वह चुपचाप अधूरी समझ से काम करेगा और अनपेक्षित तरीक़ों से फेल होगा।

</details>

2. ▢ Context rot क्या है?

<details markdown="1"><summary>जाँचें</summary>

जैसे-जैसे context में कम काम की सामग्री जमा होती है, model का ध्यान ज़्यादा शोरभरा हो जाता है और उसे यह पहचानने में दिक़्क़त होती है कि पुराने बंद रास्तों और छोड़ी गई reasoning में से क्या अब भी मायने रखता है। फूला हुआ context महँगा भी है और कम सटीक भी।

</details>

## यह जानें

### Compaction: पुराने turns को सारांश से बदलना

एक रणनीति है समय-समय पर पुराने transcript के एक हिस्से को ऐसे संक्षिप्त सारांश से बदलना जिस पर model अब भी काम कर सके। "मैंने file1.py पढ़ी और ये 50 पंक्तियाँ मिलीं" रखने की जगह, आप उस पूरे क्रम को "file1.py में database class है; मुख्य methods init, query, close हैं" से बदल सकते हैं।

Harness पहचानता है कि transcript लंबा हो गया है और पुराने turns summarizer को सौंप देता है (अक्सर एक और model call, या कोई सरल extraction)। सारांश मूल turns की जगह transcript में डाला जाता है, जिससे transcript का आकार क़ाबू में रहता है।

**जोखिम:** सारांश कोई ऐसा ब्योरा छोड़ सकता है जो बाद में मायने रखने लगे। अगर agent को बाद में जानना हो कि file1.py में एक helper function भी था, पर सारांश ने उसे छोड़ दिया, तो agent वह जानकारी हमेशा के लिए खो चुका है। सीधी truncation (जो हमेशा जोखिम भरी है) के उलट, compaction सोची-समझी है और सिद्धांत में पलटी जा सकती है, पर जानकारी का खोना असली है और उसका अनुमान लगाना कठिन।

### Retrieval on demand: agent को ब्योरा दोबारा लाने का tool दें

दूसरी रणनीति है context में पूरा ब्योरा रखना ही नहीं। हर file की सामग्री लोड करके रखने की जगह, harness सिर्फ़ सारांश रखता है (file का नाम, आकार, बदलाव की तारीख़, पंक्तियों की गिनती का छोटा नोट)। जब model को पूरी सामग्री देखनी हो, तो वह "read_file" या "re_fetch_detail" जैसा tool call करता है। Model को ब्योरा माँगने पर ही मिलता है और सिर्फ़ उसी file का जिसे वह अभी जाँच रहा है।

समझौता: हर fetch latency जोड़ता है (एक और tool call, एक और round trip)। पर resident context कहीं छोटा रहता है। लंबे task में, जो कई files जाँचता है पर एक समय में कुछ ही के साथ काम करता है, retrieval on demand कुल tokens में हर file को हमेशा context में रखने से कहीं सस्ता है।

### साथ में मिलाकर: compaction + retrieval on demand

सबसे ताक़तवर तरीक़ा दोनों को मिलाता है। Harness एक छोटा, सँवारा हुआ context रखता है जिसमें होता है:

- लक्ष्य और ताज़ा बंदिशें
- अब तक क्या किया गया उसका सारांश
- File के नाम और metadata
- हाल के निष्कर्ष जो मायने रखते हैं

पुराने विस्तृत नतीजे सारांश में दबा दिए जाते हैं (compaction)। अगर model को किसी पुरानी file या नतीजे का पूरा ब्योरा देखना हो, तो वह उसे retrieval tool से ला सकता है (on demand)। Model की काम करने वाली memory छोटी और तेज़ है, पर उसके पास ज़रूरी ब्योरे तक पीछे पहुँचने का रास्ता है।

200 turns में 100 files की समीक्षा करने वाले code-review agent में:

- भोला agent पढ़ी हुई हर file context में रखता है, और turn 50 तक 500,000 tokens तक बढ़ जाता है। Turns 51-200 सुस्त और महँगे हैं।
- समझदार agent context में सिर्फ़ file paths और एक सारांश (5,000 tokens) रखता है, और एक "read_file" tool। वह तुलना करते समय हर file माँगने पर लाता है। Turn 50 की cost लगभग turn 200 जितनी है। पूरे run की कुल token cost भोले तरीक़े के एक हिस्से जितनी है।

## अभ्यास

1. ▢ आप agent के transcript के पहले 20 turns को एक अनुच्छेद में समेटते हैं: "Agent ने तीन codebases खँगाले और caching में performance की अड़चनें पाईं।" यह सारांश मूल 20 turns की जगह लेता है। बाद में, turn 50 पर, model कहता है कि वह उस सटीक query को समझना चाहता है जो धीमी थी। यहाँ compaction कौन-सा जोखिम पेश करता है?

    - a) Model मूल turns के बिना काम करने से मना कर देगा
    - b) सारांश ने शायद query का सटीक ब्योरा दर्ज नहीं किया, और वह हमेशा के लिए खो सकता है
    - c) Compaction हमेशा lossless है, इसलिए यह जोखिम नहीं है
    - d) Model सारांश फिर पढ़ेगा और query याद कर लेगा

<details markdown="1"><summary>जाँचें</summary>

**b)** Compaction ऐसे ब्योरे हटा देती है जो बाद में मायने रख सकते हैं। सारांश संक्षिप्त है पर हो सकता है आगे model को चाहिए वे बारीकियाँ छोड़ दे। Truncation के उलट, compaction सोची-समझी है, पर जानकारी का खोना असली है। विकल्प a ग़लत है क्योंकि model सारांश के साथ काम करेगा, पर ग़लत नतीजे दे सकता है। विकल्प c ग़लत है क्योंकि compaction डिज़ाइन से ही lossy है। विकल्प d ग़लत है क्योंकि model सिर्फ़ नए सारांश के साथ काम करता है, मूल के साथ नहीं।

</details>

2. ▢ एक agent 200 documents process कर रहा है, हर एक का सारांश बना रहा है। शुरू से सभी 200 documents की सामग्री context में रखने से retrieval on demand बेहतर क्यों है?

<details markdown="1"><summary>संकेत</summary>

Model को आमतौर पर एक साथ कितने documents अपने context में चाहिए? अगर वह document 45 का सारांश बना रहा है, तो क्या उसे documents 1 से 44 की सामग्री अभी उपलब्ध चाहिए?

</details>

<details markdown="1"><summary>जाँचें</summary>

Model आमतौर पर एक समय में एक या कुछ documents पर केंद्रित रहता है। सभी 200 को context में रखना उस सामग्री पर tokens बर्बाद करता है जिसे model अभी जाँच नहीं रहा। Retrieval on demand में harness context में सिर्फ़ मौजूदा document और पिछले निष्कर्षों का सारांश रखता है। अगर model को किसी पुराने document को दोबारा देखना हो, तो वह उसे ले आता है। 200 documents पर कुल token cost सभी 200 को हर समय memory में रखने से बहुत कम है।

</details>

3. ▢ Compaction और retrieval on demand वाले system में, हमेशा मौजूद रहने वाले context में कौन-सी तीन चीज़ें होनी चाहिए?

<details markdown="1"><summary>जाँचें</summary>

लक्ष्य और बंदिशें, अब तक की प्रगति का सारांश, और उपलब्ध संसाधनों का metadata (file के नाम, document के शीर्षक, tools की सूचियाँ)। पूरा ब्योरा या तो सारांशों में दबा होता है (compaction) या माँगने पर उपलब्ध होता है (retrieval)। इससे resident context छोटा रहता है और उस पर केंद्रित रहता है जो model को अभी कार्रवाई के लिए चाहिए।

</details>

4. ▢ आप तकनीकी पेपर पढ़कर सारांश निकालने वाला agent डिज़ाइन करते हैं। 50 पेपर पढ़ने के बाद context 60,000 tokens का है। दो तरीक़ों की तुलना करें:
    - तरीक़ा A: हर 10 पेपर पर पुराने पेपरों की सामग्री को एक-अनुच्छेद के सारांशों में compact करें। सारे सारांश context में रखें।
    - तरीक़ा B: context में सिर्फ़ पेपर के शीर्षक, लेखक और निष्कर्ष रखें। पूरा text चाहिए हो तो agent को "re_read_paper" tool दें।

पेपर 100 तक कौन-सा तरीक़ा कम tokens इस्तेमाल करता है, और क्यों?

<details markdown="1"><summary>जाँचें</summary>

तरीक़ा B कम tokens इस्तेमाल करता है। तरीक़ा A में आप 10 सारांश जमा करते हैं, हर एक 200-300 tokens का, और पेपर 100 तक 2,000-3,000 tokens की compacted सामग्री हो जाती है। तरीक़ा B में आप सिर्फ़ metadata (100-200 tokens) और मौजूदा पेपर का text (500 tokens) रखते हैं, और model को शायद ही कभी किसी पुराने पेपर को दोबारा पढ़ने की ज़रूरत पड़ती है। तरीक़ा B हर पुराना सारांश हर समय न रखकर tokens बचाता है।

</details>

## असली दुनिया का अभ्यास

- [ ] किसी agent के लंबे transcript का ऑडिट करें जिसे आपने इस्तेमाल किया या लिखा हो। पहचानें कि कौन-से हिस्से अब भी प्रासंगिक हैं (लक्ष्य, हाल की बंदिशें, बाक़ी समस्याएँ) और कौन-से compact या हटाने के लिए सुरक्षित हैं। एक वाक्य का सारांश लिखें जो पहले 30% turns की जगह ले सके।
- [ ] किसी ऐसे task के लिए जिसकी आपको परवाह है (शोध, coding, विश्लेषण), काल्पनिक agent डिज़ाइन करें। खींचें कि आप compaction, retrieval on demand या दोनों इस्तेमाल करेंगे, और क्यों।
- [ ] कल: agent का "भोला" संस्करण लें जो सब कुछ context में रखता है, 100 turns पर उसकी token cost का अनुमान लगाएँ, फिर उसे compaction और retrieval on demand के साथ दोबारा डिज़ाइन करें और नई cost का अनुमान लगाएँ।

## आगे बढ़ने के लिए

- [लेख: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
