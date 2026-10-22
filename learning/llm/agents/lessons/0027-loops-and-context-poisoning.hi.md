---
title: "27. Loops और Context Poisoning"
description: Trajectory में दिखने वाले दो failure modes, दोहराव वाले loops और चुपचाप context poisoning, और हर एक को कैसे पहचानें
type: lesson
---

# पाठ 27. Loops और Context Poisoning

**मिशन से संबंध:** असफल agent को उसकी trajectory से जाँचने के लिए पहचानना ज़रूरी है कि agent एक ही action दोहराने में अटका है या चुपचाप झूठे दावे पर आगे बना रहा है, ताकि आप और instructions जोड़ने की जगह मूल कारण ठीक करें।
**मुख्य स्रोत:** [लेख: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**पूर्व-आवश्यकताएँ:** [पाठ 26](0026-why-browser-agents-fail-differently.md), [Trajectory](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 26 से: एक जैसी reasoning के बावजूद स्क्रीन चलाने वाला agent tool-calling agent से ज़्यादा बार फेल क्यों होता है?

<details markdown="1"><summary>जाँचें</summary>

स्क्रीन चलाने वाला agent pixels के ज़रिए देखता है और coordinates के ज़रिए कार्रवाई करता है, जो नाज़ुक संदर्भ हैं और layout के बदलाव, loading की स्थितियों और रुकावटों से टूट जाते हैं। ये failure modes संरचनात्मक हैं और बेहतर prompting के बावजूद बने रहते हैं।

</details>

2. ▢ पाठ 7 से: अगर harness tool का नतीजा अपने भीतरी logs में जोड़ता है पर transcript में कभी नहीं जोड़ता, तो model उस नतीजे के बारे में क्या जानता है?

<details markdown="1"><summary>जाँचें</summary>

कुछ नहीं। Model सिर्फ़ transcript देखता है। Log करना काफ़ी नहीं है; नतीजे को transcript में जोड़ना होगा ताकि model अगले turn में जान सके कि वह हुआ था।

</details>

## यह जानें

### दोहराव वाले loops: जब agent अटक जाता है

दोहराव वाला loop तब है जब agent turn-दर-turn वही tool वही या लगभग वैसे ही arguments के साथ call करता है, भले ही task में कोई प्रगति न हो। यह trajectory में शोरभरा और साफ़ दिखता है।

मूल कारण आमतौर पर दो में से एक होता है:

पहला, agent नहीं पहचानता कि कोई नतीजा उसकी योजना के उलट था या उसका समर्थन नहीं कर सका। Model ने किसी ख़ास नतीजे की उम्मीद से command भेजा, अलग या ख़ाली नतीजा मिला, पर दुनिया के अपने भीतरी मॉडल को अपडेट नहीं किया। अगले turn में वह वही चीज़ फिर आज़माता है, अलग नतीजे की उम्मीद में।

उदाहरण: Agent किसी directory में `config.json` नाम की file बनाना चाहता है। Tool call "permission denied" के साथ फेल होती है। Harness यह error जोड़ता है। पर अगले turn में model वही tool उसी path के साथ call करता है, मानो error कभी हुआ ही नहीं। Model की reasoning कुछ ऐसी थी "मैं file बनाने की कोशिश करूँगा", और जब उसने error लौटाया, तो वह "मुझे दूसरा path आज़माना चाहिए या अनुमति माँगनी चाहिए" की ओर नहीं गया। यह reasoning की विफलता है जो दोहराव से दिख जाती है।

दूसरा, harness की stopping conditions बहुत ढीली हैं। Loop चलता रहता है क्योंकि उसे रोकने वाली कोई condition नहीं चली। कसे हुए error-count guards (पाठ 6) के साथ, loop कुछ असफल प्रयासों के बाद बाहर निकल जाता है और निदान के लिए विफलता सामने लाता है। ढीले guards के साथ, loop चलता रहता है और आख़िर में रुकने से पहले वही असफल action दस या बीस बार दोहराता है।

Trajectory में दोहराव वाले loop को कैसे पहचानें:

1. लगातार turns में एक ही tool का नाम खोजें।
2. Arguments की तुलना करें: क्या वे एक जैसे या लगभग एक जैसे हैं?
3. नतीजे जाँचें: क्या वे एक जैसे, अपरिवर्तित, या सब विफलताएँ हैं?
4. दोहराए गए reasoning text को खोजें: क्या model कई turns में वही शब्दावली और reasoning इस्तेमाल करता है?

अगर तीनों सच हैं, तो agent दोहराव वाले loop में है।

### Context poisoning: जब झूठे दावे ज़मीनी सच बन जाते हैं

Context poisoning अलग है। दोहराव वाले loop के उलट, जो शोरभरा और साफ़ दिखता है, poisoning चुपचाप होती है: model एक बार कुछ झूठा या गढ़ा हुआ कहता है, और फिर हर आगे का turn उसे स्थापित तथ्य मानता है।

यह ऐसे होता है:

Turn पाँच में model कहता है: "I checked the database and found that the customer ID is 12345." पर किसी tool call ने यह तथ्य नहीं लाया। किसी भी पहले के tool result में customer ID असल में नहीं कही गई थी। Model ने उसे गढ़ा, या ग़लत याद किया, या किसी pattern के आधार पर अंदाज़ा लगाया।

वह कथन transcript में किसी भी और चीज़ की तरह जुड़ जाता है। वह ज़मीनी सच जैसा दिखता है: वह बातचीत के इतिहास में बिल्कुल वहीं है, तथ्य के रूप में कहा हुआ।

Turn छह में model उस पर आगे बनाता है: "अब मैं customer 12345 का account देखूँगा।" वह उस ID के साथ tool call करता है। Tool फेल हो सकता है ("customer 12345 does not exist"), या इससे भी बुरा, वह सफल होकर ग़लत customer पर कार्रवाई कर सकता है।

Turn सात में model और आगे बढ़ चुका होता है: "मुझे customer 12345 का account दिख रहा है जिसमें balance है..." और सिलसिला चलता रहता है।

Turn पंद्रह तक, आप trajectory पढ़ते हैं और reasoning और फ़ैसलों की विशाल श्रृंखला देखते हैं, सब इस झूठे दावे पर टिकी हुई कि customer ID 12345 है। Model मूर्ख नहीं हो रहा। Model संगत हो रहा है: transcript कहता है कि customer ID 12345 है, इसलिए model उसी के आधार पर तर्क करता है। पर transcript ज़हरीला हो चुका है।

यह गढ़े हुए tool argument (पाठ 28) से अलग क्यों है: जब model file path जैसा function argument गढ़ता है, तो tool आमतौर पर साफ़ error के साथ फेल होता है ("file not found")। Poisoning ज़्यादा बुरी है क्योंकि अक्सर वह तुरंत पकड़ी नहीं जाती। प्राकृतिक भाषा में झूठा दावा transcript में बिना चुनौती के पड़ा रह सकता है, और model उस पर आगे बनाएगा।

Trajectory में poisoning कैसे पहचानें:

1. ऐसा turn खोजें जहाँ model कोई ख़ास तथ्य (संख्या, नाम, तारीख़, ID) पूरे भरोसे से और बिना झिझक के कहता है।
2. पीछे जाँचें: क्या किसी पहले की tool call या tool result ने असल में इस दावे का समर्थन किया था? या model ने इसे कहीं से भी कह दिया?
3. अगर समर्थन नहीं था, तो आगे जाँचें: क्या बाद के turns इस दावे पर निर्भर हैं? क्या बाद की tool calls इस मान को argument के रूप में इस्तेमाल करती हैं?
4. अगर दोनों का जवाब हाँ है, तो context ज़हरीला है।

इस पाठ का बनाया निदान का अनुशासन: loop का निदान यह देखकर होता है कि क्या दोहराया जा रहा है; poisoning का निदान झूठे दावे को उसकी जड़ तक पीछे और उसके नतीजों तक आगे खोजकर होता है।

### Context rot poisoning को क्यों बढ़ाता है

Context rot (पाठ 11) बड़ी समस्या है: जैसे-जैसे transcript बढ़ता है, पुराने turns कम प्रासंगिक होते हैं, model का ध्यान खिसकता है, और सटीकता गिरती है। Context rot हर लंबे agent run में होता है, स्वस्थ run में भी।

Poisoning ज़्यादा गंभीर है। Transcript में एक अकेला झूठा दावा सारी आगे की reasoning को टिका सकता है, और अगर वह दावा दर्जनों turns के बीच दबा है तो उसे पकड़ना कठिन है। Model अपने ही transcript में पहले से मौजूद दावे को आसानी से ठुकरा नहीं सकता; इसके बजाय वह उसे स्थापित तथ्य मानता है।

उपाय निदान वाला और रोकथाम वाला है:

- Trajectories ध्यान से पढ़ें और ऐसे असमर्थित दावे देखें जो model प्राकृतिक भाषा में करता है।
- Tools डिज़ाइन करते समय उन्हें बताने दें कि क्या सुलझाया गया: सिर्फ़ "success" की जगह, "successfully updated customer ID 67890" लौटाएँ, ताकि model असली मान की पुष्टि करे।
- कसी हुई stopping conditions और error counts इस्तेमाल करें ताकि loops जल्दी बाहर निकलें और शुरुआती poisoning पर बने बुरे फ़ैसलों की श्रृंखला रुके।

## अभ्यास

1. ▢ आप agent की trajectory पढ़ते हैं और वही tool call, `get_user_by_email(email="bob@example.com")`, turns 3, 5, 7 और 9 में दोहराई हुई देखते हैं। हर बार नतीजा "user not found" है। Turn 10 में model `send_email(recipient="bob@example.com")` call करता है। क्या यह दोहराव वाला loop है?

<details markdown="1"><summary>जाँचें</summary>

नहीं, यह दोहराव वाला loop नहीं है। Agent बार-बार वही lookup tool call करके वही विफलता पा रहा है, पर फिर वह मुड़ा और दूसरा tool (send_email) call किया। Lookup फेल होने के बाद agent ने अपनी रणनीति ढाली। दोहराव वाला loop तब होता जब model turns 10, 11, 12 में get_user_by_email call करता रहता। यह context poisoning जैसा ज़्यादा है: agent ने शायद turn 2 में कोई झूठी धारणा बनाई (जैसे "मेरे पास user का email है") जिसकी कभी पुष्टि नहीं हुई, और अब वह उस पर कार्रवाई कर रहा है। पूरी trajectory का संदर्भ पढ़ें और पहचानें कि turn 2 या उससे पहले Bob के email के बारे में किसी ने असमर्थित दावा किया या नहीं।

</details>

2. ▢ एक agent file लिख रहा है। Turn तीन में वह write_file(path="output.txt", content="...") call करता है और error "permission denied" पाता है। Turn चार में model कहता है "मैं दूसरा तरीक़ा आज़माऊँगा" और create_directory(path="/tmp/") call करता है जो सफल होता है। फिर turn पाँच में वह write_file(path="/tmp/myfile.txt", content="...") call करता है। क्या यह दोहराव वाला loop है?

<details markdown="1"><summary>संकेत</summary>

देखें कि model वही tool वही arguments के साथ call कर रहा है या नहीं, और turns के बीच उसकी reasoning बदली या नहीं।

</details>

<details markdown="1"><summary>जाँचें</summary>

नहीं, यह दोहराव वाला loop नहीं है। भले ही agent को error मिला, उसने ख़ुद को ढाला: उसने अपनी reasoning बदली ("दूसरा तरीक़ा आज़माओ"), दूसरा tool call किया, और write के प्रयास में file path बदला। Model की रणनीति विकसित हुई। दोहराव वाला loop बिना बदलाव के "output.txt" के साथ वही write_file call दोहराता दिखाता। इस agent ने समस्या सुलझाने का समझदार रास्ता दिखाया, भले ही अंतिम लक्ष्य (मूल जगह पर लिखना) छोड़ दिया गया।

</details>

3. ▢ आप ऐसी trajectory पढ़ रहे हैं जहाँ turn 12 में model कहता है "The API key for this service is sk-1234567890"। आप turns 1 से 11 में पीछे खोजते हैं और कोई tool call नहीं मिलती जिसने यह key लौटाई हो। आप turns 13 से 20 में आगे खोजते हैं और पाते हैं कि turns 15, 17 और 19 सब API calls में यह key इस्तेमाल करते हैं। क्या हुआ है?

    - a) Model ने सही तर्क किया और context से key का अनुमान लगाया
    - b) Context ज़हरीला है: असमर्थित दावा अब कई आगे की tool calls को टिका रहा है
    - c) Model दोहराव वाले loop में है, वही API tool बार-बार call कर रहा है
    - d) Harness ने उस tool result को जोड़ने में चूक की जिसमें key थी

<details markdown="1"><summary>जाँचें</summary>

**b)** Context ज़हरीला है। Model ने तथ्य (API key) कहा जिसके समर्थन में कोई पहले की tool call नहीं थी, और फिर कई बाद के turns उस दावे पर निर्भर हैं। यही poisoning की पाठ्यपुस्तकीय परिभाषा है: असमर्थित दावा आगे की reasoning का आधार बन जाता है। आप सिर्फ़ trajectory से नहीं बता सकते कि harness ने नतीजा जोड़ने में चूक की (d) या model ने गढ़ा; दोनों में transcript अब ज़हरीला है। **a)** ग़लत है क्योंकि अनुमान लगाना ज़मीनी सच की पुष्टि जैसा नहीं है। **c)** ग़लत है; यह दोहराव वाला loop नहीं है क्योंकि tool calls एक जैसी नहीं हैं और model वही action नहीं दोहरा रहा।

</details>

4. ▢ एक सहकर्मी आपको फेल होती agent trajectory दिखाता है। पहले तीन turns सफल रहे। Turn चार में model loop में अटका है और list_files(directory="/data") बार-बार बिना बदलाव के call कर रहा है। Model का reasoning text कहता है "मुझे target file ढूँढनी है"। सबसे संभावित मूल कारण क्या है: model की reasoning में तर्क की ग़लती, या कसी हुई stopping condition जो ज़्यादा turns की इजाज़त देती?

<details markdown="1"><summary>जाँचें</summary>

यह model की reasoning में तर्क की ग़लती है, stopping condition की समस्या नहीं। Stopping condition पर्याप्त कसी नहीं है (loop दोहरा रहा है), पर हल उसे और ढीला करना नहीं है। समस्या यह है कि model ने argument या reasoning बदले बिना वही tool बार-बार call किया। Stopping condition ढीली करने से बस वह और दोहराएगा। हल यह निदान करना है कि model ने list_files की पहली call का नतीजा क्यों नहीं समझा, या आगे कैसे बढ़ना है यह क्यों नहीं जाना। Stopping condition को कसना चाहिए ताकि एक-दो असफल दोहरावों के बाद बाहर निकले, और समस्या को अनंत दोहराव में छोड़ने की जगह इंसानी निदान के लिए सामने लाए।

</details>

## असली दुनिया का अभ्यास

- [ ] ऑनलाइन agent trajectory खोजें (दस्तावेज़, GitHub repository या blog post से)। उसे पढ़ें और पहचानें: क्या उसमें कोई दोहराव वाले loops दिखते हैं? क्या context poisoning दिखती है? एक अनुच्छेद लिखें कि आपने क्या पाया और कैसे पहचाना।

- [ ] Agent को ऐसे task पर चलाएँ जिसके फेल होने की आपको उम्मीद है। Trajectory में ऐसे असमर्थित दावे जानबूझकर जाँचें जो model प्राकृतिक भाषा में करता है (ऐसे दावे जिन्हें पहले के tool results का समर्थन नहीं)। हर एक के लिए नोट करें कि अगर agent उस झूठे दावे पर आगे बढ़ता तो क्या होता।

- [ ] कल: ऐसा tool डिज़ाइन करें जो context poisoning रोकने में मदद करे। वह सुलझाए गए मान दोहरा सकता है, checksums जोड़ सकता है, timestamps शामिल कर सकता है, या किसी जाने हुए सेट के विरुद्ध validate कर सकता है। एक अनुच्छेद लिखें जो आपके tool का design बताए और समझाए कि वह trajectory में ज़हरीले दावे पहचानना कैसे आसान बनाता है।

## आगे बढ़ने के लिए

- [लेख: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
