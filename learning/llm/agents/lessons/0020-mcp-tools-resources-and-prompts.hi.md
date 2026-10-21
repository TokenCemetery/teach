---
title: "20. MCP: Tools, Resources और Prompts"
description: Model Context Protocol, agent harnesses के लिए बाहरी tools खोजने और चलाने, data पढ़ने और templates इस्तेमाल करने का मानकीकृत interface
type: lesson
---

# पाठ 20. MCP: Tools, Resources और Prompts

**मिशन से संबंध:** MCP को provider-neutral protocol के रूप में समझें जो integration की समस्या हल करता है, ताकि आप तर्क कर सकें कि agent कौन-से tools तक पहुँच सकता है और harness को दोबारा लिखे बिना नए tools कैसे जोड़ें।
**मुख्य स्रोत:** [विनिर्देश: Model Context Protocol](https://modelcontextprotocol.io/specification)
**पूर्व-आवश्यकताएँ:** [पाठ 19](0019-coordination-cost.md), [Tool](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 3 में आपने सीखा कि tool का नाम, विवरण और parameter schema होता है। जब आपका harness चलता है, तो वह ये definitions कहाँ से पाता है: model से, harness के code से, या कहीं और से?

<details markdown="1"><summary>जाँचें</summary>

Harness के code से। Harness का लेखक tool definitions हाथ से लिखता है या configuration file से लोड करता है, फिर loop शुरू होने से पहले model को उनके बारे में बताता है।

</details>

2. ▢ जब आप agent को नए data source (database, API, file store) से जोड़ते हैं, तो काम कौन करता है: model, harness, या दोनों?

<details markdown="1"><summary>जाँचें</summary>

दोनों। Harness का लेखक data source को जोड़ने का code लिखता है (उसे लाना, parse करना, errors सँभालना), फिर tool definition जोड़कर model को उसके बारे में बताता है। Model तय करता है कि उसे call करना है या नहीं और कब।

</details>

## यह जानें

### M गुणा N की समस्या

साझा मानक के बिना, agent harness को बाहरी tools और data sources से जोड़ने के लिए कस्टम integration का काम लगता है। अगर आपका harness N अलग tools या data sources चला सकता है, और M अलग agent-निर्माता टीमें या frameworks हैं, तो आपको M*N अलग integrations मिलते हैं: हर टीम हर tool या data source से बात करने के लिए अपना ख़ास code लिखती है।

MCP (Model Context Protocol) इसे साझा interface बनाकर हल करता है जिसे harness की ओर और tool की ओर, दोनों लागू कर सकते हैं। कोई tool या data source एक MCP server लागू करता है। कोई भी MCP-संगत harness उससे जुड़ सकता है। Harness एक MCP client लागू करता है। कोई भी MCP-संगत server उसे क्षमताएँ दे सकता है। अब आपके पास M*N की जगह M+N integrations हैं।

यह इसलिए मायने रखता है कि इसके बिना, agent को ज़्यादा tools इस्तेमाल करने के लिए बढ़ाने का मतलब कस्टम code में द्विघात वृद्धि है। MCP के साथ, बढ़ाने का मतलब है ज़्यादा मानक servers बनाना या उनसे जुड़ना।

### तीन आदिम तत्व

MCP तीन तरह की क्षमताएँ परिभाषित करता है जो server client को दे सकता है:

**Tools** (पाठ 3 के tools के समकक्ष): वे actions जिन्हें model चला सकता है। Tool का नाम, विवरण और input schema होता है। जब model उसे call करने का फ़ैसला करता है, तो client अनुरोध server को भेजता है, जो action चलाकर नतीजा लौटाता है। Model नतीजा देखता है और आगे बढ़ता है। यह ठीक वैसा ही है जैसे client और server tools जिन्हें आप पहले से जानते हैं, पर interface मानकीकृत है ताकि कोई भी पक्ष बदला जा सके।

**Resources**: ऐसा data जिसे MCP client सीधे पढ़ सकता है, model के उसे tool call के रूप में चलाए बिना। Resource file, database record, web page या live API response हो सकती है। Client उपलब्ध resources की सूची बना सकता है और नाम से एक को ला सकता है। यह tool से अलग है क्योंकि model उसे नहीं चलाता; harness उसे पढ़ता है और तय करता है कि data को context में डालना है या उसका क्या करना है। Resources harness को model के turn को रोके बिना या tool-call का अतिरिक्त बोझ जोड़े बिना प्रासंगिक जानकारी खींचने देती हैं।

**Prompts** (prompt templates): दोबारा इस्तेमाल होने वाले prompt templates जो MCP server client के भरने और इस्तेमाल करने के लिए देता है। Prompt template हो सकता है "इस code में security की समस्याओं का विश्लेषण करो" या "इस दस्तावेज़ का सारांश बनाओ।" Client उपलब्ध prompt templates की सूची बना सकता है, नाम से एक ला सकता है, और parameters भर सकता है। यह tools और resources से अलग है: action चलाने या data लाने की जगह, harness template का इस्तेमाल model को भेजने के लिए message बनाने में करता है, उसे agent के अपने instructions या reasoning चरणों में जोड़कर।

### बुनियादी जीवनचक्र

Client server से जुड़ता है। वे क्षमताओं पर बातचीत करते हैं: tools, resources और prompts में से यह ख़ास server असल में किनका समर्थन करता है। Server बताता है कि उसके पास क्या है; client तय करता है कि क्या इस्तेमाल करना है।

फिर, इस पर निर्भर कि client क्या समर्थन करता है और harness को क्या चाहिए:

- Client उपलब्ध tools की सूची बनाकर उनके schemas ला सकता है, फिर उन्हें model के सामने रख सकता है।
- Client उपलब्ध resources की सूची बनाकर data पहले से ला सकता है, जो सीखे उससे agent के फ़ैसलों को सूचित कर सकता है।
- Client उपलब्ध prompt templates की सूची बनाकर उनसे instructions या reflection चरण बना सकता है।

एक server तीनों दे सकता है, या सिर्फ़ एक-दो। Protocol सममित है: client और server दोनों interface जानते हैं, इसलिए कोई भी पक्ष सामान्य हो सकता है।

### Transports

MCP servers local (stdio पर, यानी एक ही मशीन पर harness और server के बीच साधारण process-से-pipe channel) या दूर से (HTTP-आधारित transport पर, जहाँ server किसी दूसरी मशीन या cloud service पर चलता है) चल सकते हैं। Transport latency, deployment और विफलता के तरीक़ों को प्रभावित करता है, protocol को नहीं। जो harness दोनों transports का समर्थन करता है वह तेज़ दोहराव के लिए local चलते MCP server से और मज़बूती या टीमों के बीच सहयोग के लिए दूर के MCP server से जुड़ सकता है।

## अभ्यास

1. ▢ आप ऐसा agent बना रहे हैं जिसे database से पढ़ना और web API call करना है। आपकी टीम के database का MCP server है। Web API का नहीं। क्या आपको दोनों के लिए कस्टम integration code लिखना होगा, या सिर्फ़ एक के लिए?

<details markdown="1"><summary>जाँचें</summary>

सिर्फ़ एक के लिए। Harness बिना कस्टम code के database के MCP server से जुड़ सकता है। Web API के लिए आपकी टीम को फिर भी wrapper लिखना होगा (harness में या API के चारों ओर नए MCP server के रूप में)। यही M+N का सिद्धांत है: MCP server ने आपके लिए आधा काम कर दिया।

</details>

2. ▢ आपके agent को मौसम जाँचना है और फिर तय करना है कि बाहर की गतिविधि सुझाए या नहीं। यह tool होना चाहिए (जिसे model चलाता है) या resource (जिसे harness पहले से पढ़ता है)?

<details markdown="1"><summary>संकेत</summary>

सोचें कि harness मौसम कब जानता है और model को उसे कब जानना है। क्या model तय करता है कि पूछना है या नहीं, या harness हमेशा उसे लाता है?

</details>

<details markdown="1"><summary>जाँचें</summary>

यह निर्भर करता है। अगर मौसम हमेशा फ़ैसले के लिए प्रासंगिक है, तो उसे resource बनाएँ: harness हर turn से पहले उसे लाता है और context में शामिल करता है। अगर मौसम सिर्फ़ तब प्रासंगिक है जब model बाहर की गतिविधियों पर विचार कर रहा है, तो उसे tool बनाएँ: model ज़रूरत पड़ने पर उसे माँगता है। Tool model को तय करने देता है कि कब देखना है; resource वह जानकारी देता है जो harness चाहता है कि model के पास हमेशा रहे।

</details>

3. ▢ आपका agent तीन MCP servers इस्तेमाल करता है: एक email के लिए, एक calendar के लिए, और एक document store के लिए। Email server tools और resources का समर्थन करता है। Calendar server सिर्फ़ tools का। Document server tools, resources और prompts का। इनमें से harness क्या कर सकता है?

    - a) तीनों servers के resources इस्तेमाल करे, क्योंकि तीनों कम से कम tools का समर्थन करते हैं
    - b) तीनों के tools, सिर्फ़ email और documents के resources, और prompts सिर्फ़ documents के इस्तेमाल करे
    - c) तीनों servers के prompts इस्तेमाल करे
    - d) सभी servers के tools और resources बराबर इस्तेमाल करे

<details markdown="1"><summary>जाँचें</summary>

b) Harness सिर्फ़ वही इस्तेमाल कर सकता है जो हर server असल में देता है। Email tools और resources का समर्थन करता है, इसलिए harness email से दोनों इस्तेमाल कर सकता है। Calendar सिर्फ़ tools का समर्थन करता है। Documents tools, resources और prompts का समर्थन करता है। Harness हर server के लिए क्षमता पर बातचीत करता है और सिर्फ़ वही call करता है जो घोषित है। Prompts सिर्फ़ documents server से उपलब्ध हैं, इसलिए c ग़लत है। सभी servers resources का समर्थन नहीं करते, इसलिए a और d ग़लत हैं।

</details>

4. ▢ आप तय कर रहे हैं कि MCP server local (stdio) चलाएँ या दूर (HTTP)। आपको कौन-सा समझौता सोचना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

Local (stdio) एक ही मशीन पर तेज़ और सेट करने में सरल है, पर harness को server process से जोड़ देता है। दूर (HTTP) का मतलब है कि server कहीं भी चल सकता है और harness के crash होने पर भी बचा रह सकता है, पर network latency और विफलता के तरीक़े जोड़ता है (server धीमा या पहुँच से बाहर हो सकता है)। इनमें से कोई MCP protocol को ख़ुद नहीं बदलता; client के लिए दोनों एक ही तरह काम करते हैं। इस आधार पर चुनें कि आप कितनी latency सह सकते हैं और आपको मज़बूती चाहिए या मशीनों के पार पहुँच।

</details>

## असली दुनिया का अभ्यास

- [ ] modelcontextprotocol.io पर Model Context Protocol का विनिर्देश पढ़ें और अपने क्षेत्र की किसी चीज़ (email, documents, databases, code repositories) के लिए पहले से मौजूद एक MCP server पहचानें।
- [ ] अपने काम के लिए M*N बनाम M+N की तुलना खींचें: M harnesses या टीमें और N tools या data sources सूचीबद्ध करें जिनकी आपको परवाह है, फिर अनुमान लगाएँ कि M+N तरीक़ा कितना कस्टम integration code बचाता।
- [ ] कल: किसी मौजूदा MCP server से जुड़कर देखें (उसका समर्थन करने वाले client के ज़रिए) और देखें कि तीनों आदिम तत्व (tools, resources, prompts) व्यवहार में असल में कैसे इस्तेमाल होते हैं।

## आगे बढ़ने के लिए

- [विनिर्देश: Model Context Protocol](https://modelcontextprotocol.io/specification)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
