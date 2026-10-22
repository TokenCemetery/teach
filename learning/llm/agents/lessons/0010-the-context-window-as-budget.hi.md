---
title: "10. Budget के रूप में Context Window"
description: Context window सीमित संसाधन है जिसे harness समय के साथ सक्रिय रूप से सँवारता है, कोई निष्क्रिय log नहीं
type: lesson
---

# पाठ 10. Budget के रूप में Context Window

**मिशन से संबंध:** Agentic loop की token cost और latency का budget बनाएँ, और बताएँ कि amplification loop के किस हिस्से से आता है।
**मुख्य स्रोत:** [लेख: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**पूर्व-आवश्यकताएँ:** [पाठ 9](0009-return-shapes-and-tool-set-bloat.md), [Trajectory](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 6 के agent loop में, harness किस बिंदु पर तय करता है कि कौन-सी tool call चलानी है?

<details markdown="1"><summary>जाँचें</summary>

Model tool-call block (नाम, parameters) भेजता है, और harness उसे parse करके tool चलाता है। Model को जो transcript मिलता है उसे process करके तय करता है कि कौन-सा tool।

</details>

2. ▢ हर बार जब कोई tool ख़त्म होता है तो transcript का क्या होता है?

<details markdown="1"><summary>जाँचें</summary>

नतीजा (या error) transcript में जुड़ता है, और नया transcript अगले loop iteration में model को वापस भेजा जाता है।

</details>

## यह जानें

### Transcript हर turn बढ़ता है, और जल्दी महँगा हो जाता है

Agent loop का हर iteration transcript में कुछ जोड़ता है। Agent के 10, 20 या 100 turns चलने के बाद, transcript में पूरे run का हर message, हर tool call और हर नतीजा होता है। अगले loop iteration में वह पूरा transcript model को वापस जाता है। उसके अगले iteration में फिर वापस जाता है, एक और turn से लंबा होकर।

इसका मतलब है कि दोनों costs trajectory की लंबाई के साथ बढ़ती हैं, तब भी जब कुछ नया नहीं हो रहा:

- **Token cost**: Model को भेजा हर message सारे पुराने turns फिर भेजता है। Turns लगभग बराबर आकार के हों तो turn 5 की call में turn 100 की call से लगभग 20 गुना कम tokens जाते हैं, और पूरे run पर जोड़ें तो फ़र्क़ और भी तेज़ी से बढ़ता है। लंबे चलने वाले agent में यही सबसे बड़ी cost बन जाती है।
- **Latency**: लंबा context मतलब process करने को ज़्यादा tokens, जो धीमा है। Agent हर response के लिए ज़्यादा इंतज़ार करता है।

### Context rot: कचरा जमा होने पर model का ध्यान बिगड़ता है

जैसे-जैसे context में कम काम की सामग्री जमा होती है, model का ध्यान ज़्यादा शोरभरा हो जाता है। जो चीज़ें अब भी मायने रखती हैं (लक्ष्य, हाल की बंदिशें, वे नतीजे जिन पर अभी कार्रवाई नहीं हुई) उन्हें पहचानने की model की क्षमता तब बिगड़ती है जब वे पुराने बंद रास्तों और छोड़ी गई reasoning के बड़े ढेर में दबी हों। इसे कभी-कभी "context rot" कहते हैं। फूला हुआ context सिर्फ़ महँगा नहीं है: वह model को task पर बदतर बना देता है।

### सीधी truncation जोखिम भरी है

सबसे सरल सहज विचार है कि context किसी आकार की सीमा छू ले तो सबसे पुराने turns हटा दो। पर सीधी truncation चुपचाप ज़रूरी जानकारी खो देने का जोखिम रखती है। अगर truncation की सीमा इनके बीच में आ पड़े:

- कई चरणों वाला instruction जिसे model को अब भी मानना है
- कोई नतीजा जिस पर model ने अभी कार्रवाई नहीं की
- कोई बंदिश या लक्ष्य का कथन
- System prompt या उदाहरण का हिस्सा

तो agent चुपचाप ऐसे टूट जाता है जिसे पकड़ने का harness के पास कोई तरीक़ा नहीं। Model को पता नहीं चलेगा कि कोई ज़रूरी instruction हटा दिया गया; वह अधूरी समझ के साथ काम करेगा और अनपेक्षित तरीक़ों से फेल होगा।

### सक्रिय देखभाल डिज़ाइन का सोचा-समझा चुनाव है

क्योंकि सीधी truncation ख़तरनाक है और cost trajectory की लंबाई के साथ बढ़ती है, harness transcript को ऐसा निष्क्रिय log नहीं मान सकता जो बस बढ़ता जाए। "क्या context में रहेगा और क्या जाएगा" harness में बना सोचा-समझा design फ़ैसला होना चाहिए। Trajectory तब भी मौजूद रहती है, पर harness तय करता है कि हर call पर model को उसका कौन-सा हिस्सा दिखे।

इसके लिए दो मुख्य रणनीतियाँ हैं (अगले पाठ में): compaction और retrieval on demand।

## अभ्यास

1. ▢ एक agent लंबे शोध task में 50 tool calls करता है। Call 51 पर model को 20,000 tokens का transcript भेजा जाता है। Call 52 पर model को transcript में (लगभग) कितने tokens मिलते हैं?

    - a) 20,000 tokens
    - b) 20,000 और नई call 51 के नतीजे के tokens
    - c) 40,000 tokens
    - d) Call 51 के नतीजे के आकार पर निर्भर

<details markdown="1"><summary>जाँचें</summary>

**b)** Model को मूल 20,000-token transcript और जुड़ा हुआ नया नतीजा मिलता है। अगर call 51 का नतीजा 500 tokens का था, तो model को लगभग 20,500 tokens मिलते हैं। हर turn के साथ token cost बढ़ती है, और बहुत लंबे runs पर यह गंभीर ख़र्च बन जाता है। विकल्प c ग़लत है क्योंकि model को call 51 का नतीजा दो बार नहीं मिलता; विकल्प a नए जोड़े को अनदेखा करता है; विकल्प d भावना में सही है (नतीजे का आकार मायने रखता है) पर b ज़्यादा सटीक उत्तर है।

</details>

2. ▢ आप code-review task के लिए agent डिज़ाइन कर रहे हैं। Agent files पढ़ता है, उनकी तुलना करता है, notes बनाता है और सारांश तैयार करता है। Transcript के 50,000-token की सीमा छूते ही सबसे पुराने tool results हटा देना जोखिम भरा क्यों है?

<details markdown="1"><summary>संकेत</summary>

अगर truncation की सीमा किसी पुरानी file के पढ़ने और model की अधूरी तुलना के बीच पड़ जाए तो? अगर file के दायरे की कोई बंदिश उस हिस्से में थी जिसे आपने हटा दिया तो?

</details>

<details markdown="1"><summary>जाँचें</summary>

सीधी truncation ऐसा tool result (जैसे किसी file की सामग्री) हटा सकती है जिसका model को अब भी हवाला देना है, या कोई बंदिश (जैसे "सिर्फ़ src/core/ की files की समीक्षा करें") जो model को याद रखनी है। Model को पता नहीं चलेगा कि जानकारी ग़ायब है; वह चुपचाप अधूरी तस्वीर से काम करेगा और ग़लत निष्कर्ष निकालेगा। Harness को token सीमा पर बस काट देने से ज़्यादा समझदार होना होगा।

</details>

3. ▢ Context rot के बारे में इनमें से क्या सच है?

    - a) Context rot तभी होता है जब transcript में errors हों
    - b) Context rot tool results को अच्छे से format करके रोका जाता है
    - c) बहुत-से अप्रासंगिक पुराने turns वाला बड़ा transcript model को कम सटीक बनाता है, भले ही कोई ज़रूरी जानकारी न कटी हो
    - d) आधुनिक models में context rot असली समस्या नहीं है

<details markdown="1"><summary>जाँचें</summary>

**c)** कम काम की सामग्री जमा होने पर model का ध्यान बिगड़ता है। बड़ा, बिखरा transcript model के लिए ज़रूरी चीज़ें ढूँढना और उन्हें प्राथमिकता देना कठिन बना देता है। विकल्प a ग़लत है क्योंकि बंद रास्ते और पूरे हो चुके tasks errors के बिना भी शोर पैदा करते हैं। विकल्प b ग़लत है क्योंकि अच्छा formatting signal-to-noise की समस्या हल नहीं करता। विकल्प d ग़लत है क्योंकि लंबे-context वाले tasks में context rot अच्छी तरह दर्ज है।

</details>

4. ▢ आप देखते हैं कि agent की trajectory बढ़ने के साथ उसकी latency बढ़ती है। ऐसा होने के दो कारण बताएँ।

<details markdown="1"><summary>जाँचें</summary>

पहला, model को हर call पर ज़्यादा tokens मिलते हैं, जिन्हें process करने में ज़्यादा समय लगता है। दूसरा, model को ज़रूरी जानकारी ढूँढने के लिए ज़्यादा कम-काम की सामग्री (context rot) में से छानना पड़ता है, जो उसकी reasoning की गुणवत्ता को प्रभावित करता है और ऐसी ग़लतियाँ करवा सकता है जिनसे turns बर्बाद होते हैं।

</details>

## असली दुनिया का अभ्यास

- [ ] किसी और को (या अपने नोट में) बताएँ कि transcript बहुत लंबा हो जाने पर आप सबसे पुराने turns को बस हटाते क्यों नहीं रह सकते। ऐसे असली task का उदाहरण लें जो आप agent से करवाना चाहेंगे।
- [ ] Language model के साथ अपनी किसी लंबी multi-turn बातचीत का transcript खोलें, और नोट करें कि कितने turns बाद model को शुरुआत की बंदिशें याद रखने में दिक़्क़त होने लगती है।
- [ ] कल: ऐसे शोध task की योजना बनाएँ जो agent कर सकता है (20 files पढ़ना, patterns की तुलना, सारांश बनाना), और खींचें कि transcript कितना बड़ा होता अगर agent हर file की पूरी सामग्री हर समय memory में रखता, बनाम तब जब वह सिर्फ़ file paths रखता और सामग्री ज़रूरत पर लाता।

## आगे बढ़ने के लिए

- [लेख: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
