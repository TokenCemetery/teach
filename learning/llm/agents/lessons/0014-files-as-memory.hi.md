---
title: "14. Memory के रूप में Files"
description: Agents के लिए across-run memory के सबसे सरल रूप के तौर पर टिकाऊ files का इस्तेमाल
type: lesson
---

# पाठ 14. Memory के रूप में Files

**मिशन से संबंध:** असफल agent को उसकी trajectory से जाँचें, उसके prompt में एक और instruction जोड़ने के बजाय, ऐसे systems बनाकर जहाँ agent की memory जाँची जा सके और harness तय कर सके कि क्या टिके।
**मुख्य स्रोत:** [लेख: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**पूर्व-आवश्यकताएँ:** [पाठ 13](0013-scratchpad-versus-memory.md)

## वार्म-अप

1. ▢ आप agent को दूसरी बार नए transcript के साथ शुरू करते हैं। ख़ाली transcript आपको क्या बताता है?

<details markdown="1"><summary>जाँचें</summary>

कि agent पिछले run की किसी memory के बिना नया run शुरू कर रहा है, जब तक कि harness ने loop शुरू होने से पहले जानबूझकर तथ्य वापस लोड न किए हों।

</details>

2. ▢ एक agent ने अपने पिछले run के दौरान file में notes लिखे। अगर आप चाहते हैं कि वे notes नए run में agent के व्यवहार को प्रभावित करें, तो harness को क्या करना होगा?

<details markdown="1"><summary>जाँचें</summary>

Harness को file, या उसके प्रासंगिक हिस्से, पढ़ने होंगे और सामग्री नए run के शुरुआती context या prompt में शामिल करनी होगी, ताकि model उसे देखकर उस पर काम कर सके।

</details>

## यह जानें

तथ्यों को साधारण file, या वैसे ही टिकाऊ store में लिखना, जिसे harness बाद के run में वापस पढ़ता है, across-run memory का सबसे सरल काम करने वाला रूप है। Pattern सीधा है: agent को नोट, markdown file, JSON record या छोटा संरचित log लिखने का tool दें, और बाद के run की शुरुआत में harness loop शुरू होने से पहले उस file के प्रासंगिक हिस्से नए transcript में वापस पढ़ दे।

यह, मान लें vector database की तुलना में, जानबूझकर सरल और जाँचने योग्य है। कोई इंसान file खोलकर ठीक वही पढ़ सकता है जो agent "याद रखता है"। ज़रूरत हो तो आप उसे हाथ से बदल सकते हैं। आप बासी या ग़लत प्रविष्टियाँ देखकर उन्हें बिना कुछ दोबारा train किए ठीक कर सकते हैं।

फिर भी जोखिम असली है। जो agent memory file में बिना छँटाई या अपडेट किए बस जोड़ता रहता है, वह समय के साथ बासी या विरोधाभासी notes जमा कर लेता है। जो नोट पिछले महीने सच था वह आज ग़लत हो सकता है। दो अलग तथ्य एक-दूसरे का खंडन कर सकते हैं। यह वही context rot की समस्या है जो पाठ 10 और 11 ने एक run के भीतर बढ़ते transcript के लिए सुलझाई थी। Memory को भी वैसी ही सक्रिय देखभाल चाहिए: समय-समय की समीक्षा, पुरानी प्रविष्टियों का संग्रह, दोहराव का समेकन, उन तथ्यों को हटाना जो अब लागू नहीं।

एक ज़रूरी स्पष्टीकरण: पाठ 11 की retrieval on demand, यानी documents के corpus या पिछले काम से search द्वारा ब्योरा लाना, memory के बराबर नहीं है, भले ही दोनों में "text को context में लाना" शामिल है। Retrieval इस सवाल का जवाब देती है कि "अभी इस ख़ास query के लिए क्या प्रासंगिक है?" बड़े corpus में खोजकर। Memory उन तथ्यों का छोटा, सोच-समझकर सँवारा सेट है जिन्हें agent ने, या उसके डिज़ाइनर ने, मौजूदा query से स्वतंत्र आगे ले जाने लायक़ माना। Coding assistant शैली दिखाने के लिए उपयोगकर्ता के पिछले काम के उदाहरण retrieve कर सकता है, पर उसे ऐसी memory भी चाहिए जो "उपयोगकर्ता callbacks की जगह async/await पसंद करता है" को स्थायी तथ्य के रूप में कहे, query के नतीजे के रूप में नहीं। Retrieval corpus ख़ास सवालों के जवाब देने के बारे में है; memory file स्थायी context के बारे में है।

[लेख: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) की ईमानदार चेतावनी यह है: runs के पार agent memory नया और कम तय क्षेत्र है। Across-run memory के production systems अभी विकसित हो रहे हैं। यह पाठ file-आधारित pattern कवर करता है, जो सरल है और इंसान के जाँचने लायक़ है, पर ज़रूरी नहीं कि वही निर्णायक तरीक़ा हो जो आपका production system सालों बाद इस्तेमाल करेगा।

## अभ्यास

1. ▢ एक agent उपयोगकर्ता को खाना बनाना सीखने में मदद कर रहा है। Agent नोट करता है कि उपयोगकर्ता को धनिया पसंद नहीं और उसके बिना recipes सुझाता है। जब आप अगले दिन नए खाना पकाने के session के लिए agent को फिर शुरू करते हैं, तो क्या harness को धनिया वाला नोट memory file से वापस लोड करना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

हाँ। यह पसंद उपयोगकर्ता के बारे में स्थायी तथ्य है जो sessions के पार लागू होता है। Harness को शुरू होने के समय memory file पढ़नी चाहिए और शुरुआती context में "उपयोगकर्ता को धनिया पसंद नहीं" शामिल करना चाहिए ताकि model नए recipes बनाते समय उसका इस्तेमाल कर सके।

</details>

2. ▢ Run के दौरान एक agent scratchpad में लिखता है "अब तक जाँची गई files: api.py, utils.py, config.py" ताकि उन्हें दोबारा विश्लेषित न करे। Run ख़त्म होता है। क्या यह scratchpad प्रविष्टि across-run memory file में सहेजी जानी चाहिए?

<details markdown="1"><summary>संकेत</summary>

क्या वह ख़ास जानकारी, इस ख़ास run में जाँची गई files की सूची, आगे के runs में जानी चाहिए, या वह सिर्फ़ उस एक task के भीतर काम की बहीखाता थी?

</details>

<details markdown="1"><summary>जाँचें</summary>

शायद नहीं, जब तक task कई agent runs में न फैला हो। अगर हर code review नया, स्वतंत्र task है, तो Run A में जाँची गई files की सूची Run B के लिए प्रासंगिक नहीं है। हर scratchpad प्रविष्टि सहेजना memory file को क्षणिक ब्योरों से भर देगा। एक अच्छा अनुमान: तथ्यों को memory में तभी सहेजें जब आगे के किसी run को उनकी ज़रूरत पड़े।

</details>

3. ▢ आप देखते हैं कि agent की memory file में अब विरोधाभासी सलाह है: "उपयोगकर्ता tabs पसंद करता है" और "उपयोगकर्ता spaces पसंद करता है", हफ़्तों के अंतर पर लिखे गए। आपको क्या करना चाहिए?

    - a) Memory file पूरी तरह मिटा दें ताकि agent नए सिरे से शुरू करे।
    - b) File को हाथ से देखकर विरोधाभास ठीक करने के लिए संपादित करें।
    - c) Agent में नया tool जोड़ें ताकि वह विरोध अपने आप सुलझा ले।
    - d) अनदेखा करें, क्योंकि model पता लगा लेगा कि कौन-सा मौजूदा है।

<details markdown="1"><summary>जाँचें</summary>

**b)** File को हाथ से देखकर संपादित करें। Memory की देखभाल इंसान की ज़िम्मेदारी है। आपको समझना होगा कि कौन-सी प्रविष्टि बासी है, उसे ठीक करना या हटाना होगा, और file को साफ़ और प्रामाणिक रखना होगा। पूरी file मिटाने से दूसरे कीमती तथ्य खो जाते हैं। इंसानी विवेक के बिना विरोध सुलझाना स्वचालित करने से ग़लत पसंद एन्कोड होने का जोखिम है। Model को अपनी ही memory के विरोधाभासों पर अंदाज़ा या तर्क नहीं करना पड़ना चाहिए।

</details>

4. ▢ File-आधारित memory system उस retrieval system से कैसे अलग है जो agent के पिछले काम के corpus में search करता है?

<details markdown="1"><summary>जाँचें</summary>

Retrieval system जवाब देता है "मेरे पिछले काम में से इस query के लिए क्या प्रासंगिक है?" और keyword या semantic match के आधार पर सामग्री खींचता है। Memory system स्थायी तथ्यों का छोटा सेट रखता है जिसे harness query से स्वतंत्र लोड करता है। Memory सँवारी हुई और टिकाऊ है; retrieval query से चलती है। उपयोगकर्ता के पूछने पर "दिखाओ मैंने इसे पहले कैसे सुलझाया था" आप पिछले code के उदाहरण retrieve कर सकते हैं, पर "उपयोगकर्ता async/await पसंद करता है" को आप स्थायी पसंद के रूप में हर समय याद रखते हैं।

</details>

## असली दुनिया का अभ्यास

- [ ] अगर आपके पास ऐसा agent है जो एक से ज़्यादा बार चलता है, तो जाँचें कि harness model की पहली call से पहले कोई सहेजे हुए तथ्य लोड करता है या नहीं। अगर नहीं, तो print statement या log जोड़कर देखें कि run शुरू होने के समय क्या हो रहा है।
- [ ] किसी ऐसे task के लिए जिसे आप अच्छी तरह जानते हैं, सरल memory file format डिज़ाइन करें। आप कौन-से तथ्य लिखेंगे? आपको कैसे पता चलेगा कि कोई प्रविष्टि कब अपडेट या हटानी है?
- [ ] कल: एक-run का agent बनाएँ जो memory file में एक तथ्य लिखे, कोई भी format: JSON, markdown या सादा text। फिर उसी agent का दूसरा run बनाएँ जो वह file पढ़े और इस्तेमाल करे। कोई vector database नहीं, कोई search नहीं, बस टिकाऊ storage और harness-प्रबंधित लोडिंग।

## आगे बढ़ने के लिए

- [लेख: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
