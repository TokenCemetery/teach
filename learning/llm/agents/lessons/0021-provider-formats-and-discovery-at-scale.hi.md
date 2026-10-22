---
title: "21. Provider Formats और बड़े पैमाने पर Tool Discovery"
description: MCP और provider-विशिष्ट wire formats अलग परतें कैसे हैं, और हर tool को context में लोड करना कई जुड़े servers पर क्यों नहीं चलता
type: lesson
---

# पाठ 21. Provider Formats और बड़े पैमाने पर Tool Discovery

**मिशन से संबंध:** समझें कि जब agent कई MCP servers से जुड़ता है तो सीधी tool discovery की सीमाएँ क्या हैं, और पहचानें कि tools को उत्सुकता से लोड करने की जगह आलसी या programmatic discovery कब चुननी है।
**मुख्य स्रोत:** [लेख: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
**पूर्व-आवश्यकताएँ:** [पाठ 20](0020-mcp-tools-resources-and-prompts.md)

## वार्म-अप

1. ▢ पाठ 3 में आपने दो wire formats सीखे: Anthropic tool call को `input_schema` से दर्शाता है, और OpenAI `function.parameters` नाम की अलग बनावट इस्तेमाल करता है। अगर आप Anthropic की API से OpenAI की API पर जाएँ, तो क्या आपको अपना MCP server बदलना होगा, MCP client, या दोनों?

<details markdown="1"><summary>जाँचें</summary>

कोई नहीं। आपका MCP server वैसा ही रहता है (वह जानता है कि tools को MCP format में कैसे देना है)। आपका harness बदलता है, क्योंकि उसे MCP tool definitions को उस provider के wire format में बदलना पड़ता है जो model अपेक्षित करता है। Model provider बदलता है, पर MCP protocol नहीं।

</details>

2. ▢ पाठ 9 में आपने tool-set bloat के बारे में सीखा: अगर आप model को बहुत ज़्यादा tool definitions दें, तो वह धीमा हो जाता है, उलझ जाता है, या भूल जाता है कि कौन-सा tool इस्तेमाल करना है। जब agent पाँच MCP servers से जुड़ता है जिनमें हर एक के दस tools हैं, तो क्या model को शुरू में पचास tool definitions दिखती हैं?

<details markdown="1"><summary>जाँचें</summary>

सिर्फ़ तब जब harness loop शुरू होने से पहले पचासों definitions context में लोड करे। यह सीधा तरीक़ा है। पर और तरीक़े हैं: harness tools तभी लोड कर सकता है जब model उन्हें माँगे, या tool definitions को ऐसे code में बदल सकता है जिसे model खँगाल और programmatically call कर सके।

</details>

## यह जानें

### दो स्वतंत्र परतें

MCP agent harness और बाहरी tools या data sources के बीच का protocol है। वह परिभाषित करता है कि client और server एक-दूसरे से कैसे बात करते हैं और server कौन-सी क्षमताएँ दे सकता है। पर MCP को परवाह नहीं कि model कौन-सा wire format इस्तेमाल करता है।

साथ ही, model का एक provider है, और उस provider के पास tool calls को दर्शाने का अपना ख़ास तरीक़ा है। Anthropic की API tools एक बनावट में लेती है। OpenAI की API दूसरी में। यह wire format harness और model के बीच की अलग परत है।

ये दोनों परतें स्वतंत्र हैं:

- MCP client (harness की ओर) MCP server से MCP बोलता है। MCP server इससे अनजान है कि आख़िरकार कौन-सा model इन tools को इस्तेमाल करेगा।
- फिर harness MCP tool definitions को उस provider के wire format में बदलता है जो model अपेक्षित करता है। Anthropic? `input_schema` इस्तेमाल करें। OpenAI? `function.parameters` इस्तेमाल करें।

Harness को अनुवाद करना पड़ता है, क्योंकि वह बीच में बैठा है। पर एक परत बदलने के लिए दूसरी को दोबारा लिखना ज़रूरी नहीं। अगर आप model providers बदलते हैं, तो आप अपने MCP servers दोबारा नहीं लिखते। अगर आप नए MCP server से जुड़ते हैं, तो harness और model के बीच का wire format नहीं बदलता।

### बड़े पैमाने पर tool discovery

एक अकेले agent पर, आप शुरू में दो-तीन tools हाथ से context में जोड़ सकते हैं। Tool-set bloat (पाठ 9) पाँच से दस tools के आसपास शुरू होता है। पर अगर harness एक दर्जन MCP servers से जुड़ा है, हर एक में दस से बीस tools? सैकड़ों tool definitions।

सीधा तरीक़ा है शुरू में हर tool definition लोड करना, हर एक को provider के wire format में बदलना, और सब कुछ model को उसके शुरुआती context में दे देना। यह tool-set bloat को कहीं बड़े पैमाने पर दोहराता है। Model सैकड़ों definitions पढ़ता है, उन विवरणों पर tokens बर्बाद करता है जिनकी उसे ज़रूरत नहीं, और हर turn पर धीमा हो जाता है क्योंकि हर tool context में है। और अगर जुड़े server में नया tool जुड़ता है, तो पूरा context और model का व्यवहार बदल जाता है।

यही बड़े पैमाने पर tool discovery की समस्या है: आप कई servers से जुड़ सकते हैं, पर सब कुछ पहले से लोड करके नहीं।

### Code execution का विचार

Anthropic Engineering का लेख "Code Execution with MCP" हल सुझाता है: tool definitions को context में लोड करने की जगह, उपलब्ध tools को ऐसे code के रूप में पेश करें जिसे agent खोज सके और programmatically call कर सके।

उदाहरण के लिए:

- Harness helper function list_available_tools() परिभाषित करता है जो जुड़े MCP servers को query करता है और call करने लायक functions की निर्देशिका लौटाता है: उनके नाम, विवरण और parameters।
- Harness helper function call_tool(name, args) परिभाषित करता है जो tool का नाम और arguments लेता है, जुड़े servers पर tool खोजता है, और उसे चलाता है।
- Model को पचास tool definitions पहले से देने की जगह, harness model को बताता है: "आप list_available_tools() call करके देख सकते हैं कि आप क्या कर सकते हैं, या कुछ ख़ास करने के लिए call_tool(name, args) call कर सकते हैं।"

अब model के पास दो meta-tools हैं: दूसरे tools को खोजने और call करने के tools। वह शुरुआत में हर definition context में लोड किए बिना tool-क्षेत्र खँगाल सकता है। जब उसे tool खोजना होता है तो वह list_available_tools() call करता है, उस पल जो उपलब्ध है वह सीखता है, और फिर जो चाहिए उसे इस्तेमाल करता है। Resident context छोटा रहता है।

यह उत्सुक लोडिंग को आलसी discovery से बदलता है। Model को ख़ास tool call करने से पहले list_available_tools() call करने में एक turn लगाना पड़ता है, इसलिए latency की क़ीमत है। पर अगर harness पचास servers से जुड़ा है, तो हर tool definition को context में न रखने से बचे tokens अतिरिक्त turn की क़ीमत से ज़्यादा हैं।

### हर तरीक़ा कब इस्तेमाल करें

उत्सुक लोडिंग (शुरू में हर tool context में डालना) तब काम करती है जब:

- आपके पास tools का छोटा तय सेट है (दो से दस)।
- Tools agent के हर task के लिए प्रासंगिक हैं।
- Context पर बंदिश नहीं है।

आलसी लोडिंग (list_available_tools() और call_tool() परिभाषित करें और model को ख़ुद खोजने दें कि उसे क्या चाहिए) तब काम करती है जब:

- आपके पास बहुत सारे tools हैं (दर्जनों या ज़्यादा)।
- Tools विशेष हैं और हर task के लिए प्रासंगिक नहीं।
- Context पर बंदिश है और हर token मायने रखता है।
- अतिरिक्त turn की latency की क़ीमत स्वीकार्य है।

Programmatic discovery (tools को ऐसे code के रूप में पेश करना जिसे model पढ़ और चला सके) दोनों विचारों को मिलाती है: छोटा शुरुआती context (सिर्फ़ discovery functions) और definitions हाथ से लोड किए बिना tool-क्षेत्र खँगालने की क्षमता।

## अभ्यास

1. ▢ आप तीन MCP servers के साथ Anthropic की API इस्तेमाल कर रहे हैं। आप OpenAI की API पर जाते हैं। क्या आपको अपने MCP servers अपडेट करने होंगे, अपना harness, या दोनों?

<details markdown="1"><summary>जाँचें</summary>

सिर्फ़ अपना harness। MCP servers नहीं बदलते; वे अब भी tools को MCP format में देते हैं। आपका harness पहले से MCP definitions को Anthropic के wire format में बदल रहा था; अब वह उन्हें OpenAI के format में बदलता है। अनुवाद की परत बदलती है, पर servers और protocol नहीं।

</details>

2. ▢ आपका agent दस MCP servers से जुड़ा है जिनमें कुल एक सौ पचास tools हैं। आप "code execution with MCP" का विचार इस्तेमाल करना चाहते हैं: list_available_tools() परिभाषित करें और model को ख़ुद खोजने दें कि उसे क्या चाहिए। इस design के दो नतीजे क्या हैं?

<details markdown="1"><summary>संकेत</summary>

Context के आकार और latency के बारे में सोचें। Model सूची कब माँगता है? उसकी क्या क़ीमत है?

</details>

<details markdown="1"><summary>जाँचें</summary>

Context छोटा है क्योंकि आप एक सौ पचास tool definitions पहले से लोड नहीं कर रहे, सिर्फ़ दो functions और शायद उनके काम का छोटा विवरण। Latency बढ़ती है क्योंकि model को जिस turn पर खोजना है उस पर list_available_tools() call करना पड़ता है, जो ख़ास tool call करने से पहले कम से कम एक अतिरिक्त turn जोड़ता है। अगर context तंग है या tools की सबको एक साथ कम ही ज़रूरत पड़ती है, तो यह फ़ायदे का समझौता है।

</details>

3. ▢ आपके harness में सिर्फ़ तीन tools हैं, और वे agent के हर task के लिए प्रासंगिक हैं। क्या आपको उत्सुक लोडिंग इस्तेमाल करनी चाहिए, आलसी लोडिंग, या programmatic discovery?

    - a) list_available_tools() के साथ आलसी लोडिंग
    - b) उत्सुक लोडिंग: तीनों शुरू में context में डालें
    - c) call_tool() functions के साथ programmatic discovery
    - d) tokens बचाने के लिए बदल-बदलकर tools context में रखें

<details markdown="1"><summary>जाँचें</summary>

b) हमेशा प्रासंगिक रहने वाले tools के छोटे सेट के साथ, उत्सुक लोडिंग सबसे सरल और तेज़ है। आप discovery functions पर tokens बर्बाद नहीं करते, latency नहीं जोड़ते, और model के पास हमेशा वे tools होते हैं जो उसे चाहिए। जब tool सेट छोटा और सार्वभौमिक हो तो आलसी और programmatic discovery बिना फ़ायदे के अतिरिक्त बोझ जोड़ती हैं। विकल्प d विरोधी pattern है: tools को अंदर-बाहर घुमाना उलझन और अनिश्चितता पैदा करता है।

</details>

4. ▢ आप list_available_tools() को सभी जुड़े MCP servers को query करने और उनके tool नाम और विवरण लौटाने के लिए परिभाषित करते हैं। जब model यह function call करता है, तो क्या वह call आपके API tokens में गिनी जाती है?

<details markdown="1"><summary>जाँचें</summary>

हाँ। list_available_tools() call करने में tokens वैसे ही लगते हैं जैसे किसी और function call करने में: model call भेजता है, harness उसे चलाता है, और नतीजा transcript में लौटता है। आप शुरू में दी गई tool definitions पर ख़र्च tokens और discovery calls पर ख़र्च tokens के बीच समझौता कर रहे हैं। बहुत सारे tools के साथ, यह सौदा आमतौर पर फ़ायदे का होता है।

</details>

## असली दुनिया का अभ्यास

- [ ] दोनों परतें दिखाने वाला चित्र बनाएँ: एक ओर MCP protocol (harness से बाहरी servers), दूसरी ओर provider का wire format (harness से model)। लिखें कि providers बदलने बनाम MCP servers बदलने पर क्या होता है।
- [ ] अपने agent के लिए उत्सुक लोडिंग (सौ tools context में डालना) और आलसी लोडिंग (माँगने पर list_available_tools()) के बीच token cost का फ़र्क़ अनुमानित करें। क्या आलस समझदारी है?
- [ ] कल: सरल list_available_tools() function लागू करें जो किसी असली MCP server को query करे जिस तक आपकी पहुँच है, और ऐसा सारांश लौटाए जिसे model पढ़ सके।

## आगे बढ़ने के लिए

- [लेख: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [विनिर्देश: Model Context Protocol](https://modelcontextprotocol.io/specification)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
