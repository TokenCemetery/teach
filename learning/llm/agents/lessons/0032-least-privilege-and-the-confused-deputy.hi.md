---
title: "32. Least Privilege और Confused Deputy"
description: Agent की क्षमताओं को ऐसे सीमित करें कि prompt injection से भयानक सेंध की जगह सीमित नुक़सान हो
type: lesson
---

# पाठ 32. Least Privilege और Confused Deputy

**मिशन से संबंध:** Agent के हर tool के लिए पहुँच की सीमाएँ ऐसे डिज़ाइन करें कि untrusted content agent को बहका तो सके पर उसे ऐसी क्षमताओं के दुरुपयोग के लिए न बहका सके जो उसके पास कभी होनी ही नहीं चाहिए थीं।
**मुख्य स्रोत:** [संदर्भ: "OWASP Top 10 for LLM Applications", OWASP GenAI Security Project](https://genai.owasp.org/llm-top-10/)
**पूर्व-आवश्यकताएँ:** [पाठ 31](0031-prompt-injection-and-the-lethal-trifecta.md), [Sandbox](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 31 से lethal trifecta की तीन शर्तों के नाम बताएँ।

<details markdown="1"><summary>जाँचें</summary>

Private data तक पहुँच, untrusted content का सामना, और बाहर संवाद करने की क्षमता। कोई एक हटा दें तो हमला नाकाम हो जाता है।

</details>

2. ▢ पाठ 31 में आपने trifecta की एक शर्त तोड़कर prompt injection के हमले से बचने के लिए tool डिज़ाइन किया था। अगर आपने बाहरी संवाद की शर्त तोड़ी होती, तो व्यवहार में वह कैसा दिखता, बताएँ।

<details markdown="1"><summary>जाँचें</summary>

Tool या तो कहीं जानकारी भेज नहीं पाता, या सिर्फ़ ऐसे channel पर भेज पाता जिस तक हमलावर नहीं पहुँच सकता। उदाहरण के लिए, draft_email tool जो emails भेजने की जगह सिर्फ़ local में सहेजता है, या ऐसा tool जो सिर्फ़ staging table में लिख सकता है जिसमें data साझा होने से पहले हाथ से समीक्षा चाहिए।

</details>

## यह जानें

### Least privilege: हर tool को ठीक उतने तक सीमित करें जितना उसे चाहिए

Least privilege सुरक्षा का सिद्धांत है: हर tool की पहुँच सिर्फ़ उस ख़ास resource या action तक होनी चाहिए जो उसे असल में चाहिए, "शायद बाद में काम आए" सोचकर दी गई व्यापक पहुँच नहीं। Agent के लिए इसका मतलब है हर tool की sandbox सीमा को संकरी अनुमति के साथ डिज़ाइन करना।

उदाहरण:

- आज का schedule पढ़ने वाला tool सिर्फ़ calendar file से पढ़े, पूरे filesystem से नहीं
- ग्राहक का order खोजने वाला tool सिर्फ़ उसी ग्राहक के orders query करे, कंपनी के सारे orders नहीं
- Receipt email भेजने वाला tool सिर्फ़ एक तय पते से भेज सके, पूरे mailbox से नहीं
- Configuration file संपादित करने वाला tool सिर्फ़ उसी एक file को संपादित करे, config directory की मनमानी files को नहीं

सिद्धांत credentials पर भी लागू होता है। अगर tool को बाहरी service से authenticate करना है, तो उसे उस service और उस action तक सीमित credential इस्तेमाल करना चाहिए, व्यापक administrator account नहीं।

Agents के लिए यह क्यों मायने रखता है? क्योंकि व्यापक पहुँच ठीक वही चीज़ है जो exploit को संगठन के लिए महँगा बनाती है। जब agent को injection से बहकाकर ऐसे tool को call कराया जाता है जिस तक उसकी पहुँच है, तो नतीजे इस पर निर्भर करते हैं कि वह tool असल में कहाँ तक पहुँच सकता है।

### Confused deputy pattern: वैध अधिकार, ग़लत इस्तेमाल

Confused deputy सुरक्षा का क्लासिक pattern है, जिसका नाम पहली बार 1980 के दशक में रखा गया, और जो सीधे agents पर लागू होता है। Confused deputy ऐसा program है जिसके पास वैध, व्यापक अधिकार है और जिसे हमलावर की ओर से उस अधिकार का दुरुपयोग करने के लिए बहका दिया जाता है। Program दुर्भावनापूर्ण code चलाने के अर्थ में compromise नहीं हुआ है; वह ठीक वही कर रहा है जिसकी उसके वैध tools इजाज़त देते हैं, बस ऐसे instructions की ओर से जो कभी उपयोगकर्ता के थे ही नहीं।

Confused deputy की कमज़ोरी वाला agent ऐसा दिखता है:

1. Agent के पास व्यापक tool है: send_email कंपनी के mailbox के किसी भी पते से भेज सकता है
2. Agent untrusted content पढ़ता है: calendar invite जिसमें घुसाया गया instruction है
3. Instruction agent से कहता है कि गोपनीय email thread किसी बाहरी पते को forward करे
4. Agent हमलावर के parameters के साथ send_email call करता है
5. Tool call चला देता है क्योंकि वह वैध parameters वाली वैध send_email call है। Tool नहीं जानता कि अनुरोध injection से आया था, उपयोगकर्ता की असली मंशा से नहीं।

Email अब चुरा लिया गया, इसलिए नहीं कि model "hack" हुआ, बल्कि इसलिए कि आपने agent को व्यापक क्षमता दी और उसे संकरे task तक सीमित नहीं किया।

हल model को ज़्यादा ज़ोर से prompt करना नहीं है। हल tool को संकरा डिज़ाइन करना है: पूरे mailbox के लिए send_email की जगह, send_receipt नाम का tool बनाएँ जो सिर्फ़ तय template के साथ ग्राहकों के email पतों पर भेज सके। अब injection model को send_receipt call करने के लिए फिर भी बहका सकता है, पर वह call उस सीमा में बँधी है जिसकी इजाज़त send_receipt को है।

### MCP supply chain: भरोसा आगे बढ़ता है

पाठ 20-21 ने Model Context Protocol (MCP) और यह कवर किया कि agent tools तक पहुँचने के लिए MCP servers से कैसे जुड़ता है। सुरक्षा के नज़रिए से, MCP server से जुड़ने का मतलब है अपनी भरोसे की सीमा को उस server को चलाने वाले तक बढ़ाना।

दुर्भावनापूर्ण या compromise हुआ MCP server कर सकता है:

- Tool के विवरण ग़लत दर्शाकर हानिकारक calls को हानिरहित जैसा सुनाना
- Tool results में भ्रामक data लौटाना, जिस पर agent फिर तर्क करेगा
- Agent की की हुई हर tool call और भेजे गए हर context के टुकड़े को देखना

जब आपका harness तीसरे पक्ष के MCP server से जुड़ता है, तो आप उस server के संचालक पर उतना ही भरोसा कर रहे हैं जितना अपने code पर। अगर server compromise हुआ है या किसी विरोधी के हाथ में है, तो वह injection का एक और रास्ता बन जाता है।

बचाव वही है जो किसी भी supply chain जोखिम के लिए है: सिर्फ़ उन्हीं servers से जुड़ें जिन पर आप भरोसा करते हैं, और जुड़ाव को सीमित करें। उदाहरण के लिए:

- Agent को सारे उपलब्ध MCP servers तक पहुँच न दें; सिर्फ़ उन ख़ास servers से जोड़ें जो उसे चाहिए
- MCP जुड़ावों के लिए authentication और encryption इस्तेमाल करें
- MCP server के दिए tool विवरणों की जाँच करें और समझें कि आप कौन-सी पहुँच दे रहे हैं
- मानकर चलें कि जो data आप MCP tool को भेजते हैं वह सार्वजनिक हो सकता है या उसका दुरुपयोग हो सकता है

MCP servers अनोखे रूप से जोखिम भरे नहीं हैं; वे बस एक और tool हैं। सिद्धांत वही है: पहुँच को सीमित करें।

### सब कुछ जोड़कर: हर tool, हर task के लिए permission सीमाएँ

इन पाठों को जोड़ने वाला design सिद्धांत यह है कि permission की सीमा सोच-समझकर, हर tool और हर task के लिए तय होनी चाहिए, एक ऐसे व्यापक credential के रूप में नहीं जिसे पूरा agent साझा करे।

जब आप agent डिज़ाइन करें:

1. Agent को चाहिए वाले हर tool की सूची बनाएँ
2. हर tool के लिए पूछें: अपना मक़सद पूरा करने के लिए इस tool को न्यूनतम कौन-सी पहुँच चाहिए?
3. उस tool के लिए ऐसी sandbox सीमा बनाएँ जो ठीक उतनी पहुँच दे, उससे ज़्यादा नहीं
4. अगर tool को authenticate करना है (database, API, filesystem के साथ), तो उस tool और उस पहुँच के स्तर तक सीमित credential बनाएँ, ऐसा credential नहीं जो कहीं भी पहुँच सके

संकरे दायरे वाला tool वह ठोस चीज़ है जो "model को injection ने बहका दिया" को भयानक compromise से सीमित, कम नतीजे वाली ग़लती में बदल देता है। Agent injection पढ़ता है, model उसे समझता है, model घुसाए गए tool को call करता है, और tool माँगा गया action चलाने से मना कर देता है क्योंकि वह action उसके दायरे के बाहर है।

## अभ्यास

1. ▢ आप ऐसे agent के लिए tool डिज़ाइन कर रहे हैं जो user accounts सँभालता है। Tool को कंपनी के database में user का email पता अपडेट करना है। आपका पहला मसौदा उसे यह credential देता है: पूरी users table पर UPDATE अनुमति वाला database account।

यह ज़रूरत से ज़्यादा दायरे वाला क्यों है, और बेहतर design क्या होगा?

<details markdown="1"><summary>जाँचें</summary>

Credential पूरी table पर UPDATE अनुमति देता है, जिसका मतलब है कि tool किसी भी user की जानकारी अपडेट कर सकता है, सिर्फ़ उस ख़ास user का ख़ास email पता नहीं जिसे सँभाला जा रहा है। बेहतर design database पर stored procedure बनाएगा जो सिर्फ़ user ID और नया email स्वीकार करे, और tool के credential को सिर्फ़ वही procedure चलाने की अनुमति दे। इस तरह, भले ही injection agent को अप्रत्याशित parameters के साथ tool call करने के लिए बहका दे, database procedure के दायरे के बाहर कुछ भी चलाने से मना कर देगा।

</details>

2. ▢ एक agent के पास send_email tool की पहुँच है जो सिर्फ़ `support@company.com` से और सिर्फ़ `*@customer-*.com` पैटर्न से मेल खाते email पतों पर भेजने तक सीमित है। एक injection उसे `attacker@evil.com` को संदेश भेजने के लिए बहकाने की कोशिश करता है। हमले को क्या रोकता है?

<details markdown="1"><summary>संकेत</summary>

दायरा tool ख़ुद लागू करता है। सोचें कि यह जाँच कहाँ होती है और इसमें कोई prompt instruction क्यों शामिल नहीं है।

</details>

<details markdown="1"><summary>जाँचें</summary>

Tool की validation, जो संदेश भेजे जाने से पहले harness में चलती है। Tool प्राप्तकर्ता को अपने अनुमत पैटर्न के विरुद्ध जाँचता है और भेजने से मना कर देता है क्योंकि `attacker@evil.com` मेल नहीं खाता। Injection agent का व्यवहार बदलने में सफल रहा (agent ने भेजने का इरादा किया), पर वह नाकाम रहा क्योंकि tool की permission सीमा ने हानिकारक action रोक दिया। यह tool-स्तर का नियंत्रण है, prompting-स्तर का नहीं, इसलिए भरोसेमंद है।

</details>

3. ▢ आपका संगठन MCP server देता है जो कंपनी के calendar events दिखाता है। आप पाते हैं कि किसी तीसरे पक्ष की कंपनी ने MCP client बनाया है जो meetings सँभालने में मदद के लिए आपके server से जुड़ता है। इनमें से कौन-सा कथन सच है?

    - a) यह सुरक्षित है जब तक आपका MCP server सिर्फ़ सार्वजनिक calendar data लौटाता है
    - b) तीसरे पक्ष के client के पास अब प्रभावी रूप से उस calendar data की read पहुँच है जो आपका server लौटाता है
    - c) आपको अपने server और client के बीच encryption इस्तेमाल करना चाहिए ताकि गारंटी हो कि आपके server के संचालक भी data नहीं देख सकते
    - d) तीसरे पक्ष की कंपनी data का दुरुपयोग नहीं कर सकती क्योंकि वह सिर्फ़ calendar events है, user credentials नहीं

<details markdown="1"><summary>जाँचें</summary>

**b)** तीसरे पक्ष का client, और उसे चलाने वाला कोई भी, वह सारा calendar data देख सकता है और संभवतः उसका दुरुपयोग कर सकता है जो server लौटाता है। सार्वजनिक data भी data है; भले ही calendar events गोपनीय नहीं हैं, तीसरे पक्ष के संचालक को अब आपके संगठन के schedule की जानकारी है, जो corporate जासूसी या social engineering के लिए इस्तेमाल हो सकती है। Encryption (विकल्प c) transit में data की रक्षा करता, पर client के संचालक को उसे देखने से नहीं रोकता। पहुँच का दायरा (सार्वजनिक बनाम निजी) सुरक्षा के निहितार्थ को नहीं बदलता: आपने अपनी भरोसे की सीमा तीसरे पक्ष के संचालक तक बढ़ा दी है। यही MCP supply chain का जोखिम है।

</details>

4. ▢ आप ऐसे agent के लिए tool डिज़ाइन कर रहे हैं जो ग्राहक support tickets process करता है। Tool को ग्राहक को email जवाब भेजना है। ऐसा least-privilege design बताएँ जो confused deputy हमले को रोके, जहाँ injection agent को गोपनीय आंतरिक email thread ग्राहक को forward करने के लिए बहका दे।

<details markdown="1"><summary>जाँचें</summary>

सामान्य send_email tool की जगह, send_support_response नाम का tool डिज़ाइन करें जो सिर्फ़ दो parameters ले: ticket ID और जवाब का text। Tool ticket ID से ग्राहक का email पता खोजता है, validate करता है कि जवाब का text उचित लंबाई से ज़्यादा नहीं है, और सिर्फ़ जवाब भेजता है (कोई attachments नहीं, कोई और emails नहीं)। Tool के credential को सिर्फ़ support पते से और सिर्फ़ वैध tickets से जुड़े ग्राहक email पतों पर भेजने की अनुमति है। अब injection agent को send_support_response call करने के लिए बहका सकता है, पर call tool के दायरे से बँधी है। Agent आंतरिक emails forward नहीं कर सकता, मनमाने पतों पर नहीं भेज सकता, और ऐसा कुछ नहीं भेज सकता जो support का जवाब न हो क्योंकि tool उन चीज़ों का कोई तरीक़ा देता ही नहीं।

</details>

## असली दुनिया का अभ्यास

- [ ] ऐसा tool लें जिसे आपने डिज़ाइन किया या जो आप अक्सर इस्तेमाल करते हैं। उसकी मौजूदा permissions चिह्नित करें। एक ऐसी permission लिखें जो उसके प्राथमिक मक़सद के लिए कड़ाई से ज़रूरी से ज़्यादा है, और उसे हटाने का एक तरीक़ा।
- [ ] कोई ऐसा MCP server चुनें जिससे आप agent जोड़ने को तैयार होंगे। संचालक के बारे में खोजें या उनसे संपर्क करें और समझें: server कौन-सा data देखता है, उसका इस्तेमाल कैसे होता है, उसकी रक्षा कैसे होती है, logs तक किसकी पहुँच है? अपना भरोसे का स्तर और बचा हुआ जोखिम लिखें।
- [ ] कल: ऐसा tool डिज़ाइन करें जो ठीक-ठाक पर दायरे से बाहर के अनुरोध को ठुकराकर जानबूझकर least privilege लागू करे। ऐसा विनिर्देश लिखें जो उस अनुरोध का नाम बताए जो उसे confused deputy हमले के दौरान मिलेगा और समझाए कि tool का design उसे सफल होने से कैसे रोकता है।

## आगे बढ़ने के लिए

- [संदर्भ: "OWASP Top 10 for LLM Applications", OWASP GenAI Security Project](https://genai.owasp.org/llm-top-10/)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
