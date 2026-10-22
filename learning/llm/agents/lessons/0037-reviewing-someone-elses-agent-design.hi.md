---
title: "37. किसी और के Agent Design की समीक्षा"
description: Agent system का व्यवस्थित मूल्यांकन कैसे करें, और विवादित दावे को मुख्य स्रोत पर लौटकर कैसे सुलझाएँ
type: lesson
---

# पाठ 37. किसी और के Agent Design की समीक्षा

**मिशन से संबंध:** किसी और के agent design की समीक्षा करने और उसके बारे में विवादित दावों को मुख्य स्रोतों से जाँचकर सुलझाने के लिए भरोसेमंद बनें, न कि डिफ़ॉल्ट रूप से कोई पक्ष चुनकर या धुँधले ढंग से बीच का रास्ता निकालकर।
**मुख्य स्रोत:** [लेख: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**पूर्व-आवश्यकताएँ:** [पाठ 36](0036-when-not-to-build-an-agent.md)

## वार्म-अप

1. ▢ पाठ 2 का autonomy spectrum workflow और agent में फ़र्क़ करने के लिए किस बात को परखता है?

<details markdown="1"><summary>जाँचें</summary>

यह कि control flow developer ने पहले से तय किया है, या run के समय model तय करता है। Tools की संख्या, जटिलता या model calls की गिनती नहीं, बल्कि यह कि रास्ता किसने चुना।

</details>

2. ▢ पाठ 35 से: harness को शुरू से लिखने की तुलना में framework production में agent चलाने की cost को किस एक तरीक़े से घटा सकता है?

<details markdown="1"><summary>जाँचें</summary>

स्थिर context (tool definitions, system prompt) को cache करके, ताकि दोहराए गए tasks वे tokens दोबारा न भेजें; durable state लागू करके, ताकि रुका हुआ run फिर शुरू हो सके; और built-in tracing और error handling देकर, जिन्हें हाथ से जोड़ने में समय लगता। Framework flexibility या vendor lock-in की क़ीमत पर भरोसेमंद होने का समय और cost में कमी ख़रीदता है।

</details>

## यह जानें

### समीक्षा की checklist: चरण क्रम से

जब आप किसी प्रस्तावित या मौजूदा agent design की समीक्षा करें, तो उसे इस track के चरणों से क्रम में गुज़ारें और हर चरण पर वही सवाल पूछें: क्या यह चुनाव जायज़ है, और क्या वह दर्ज है?

#### चरण 1-2: Autonomy spectrum और control flow

यह system autonomy spectrum पर कहाँ बैठता है? क्या यह एक अकेला prompt है, developer का तय किया workflow है, या model के निर्देशित agent है? प्रस्ताव या documentation में दावा खोजें। अगर दावा बस "यह एक agent है" है और यह नहीं बताता कि autonomy क्यों ज़रूरी है, तो पूछें कि तय रास्ते वाले विकल्प की क्या क़ीमत होती। अच्छा design सिर्फ़ चुनाव का नाम नहीं लेता; उसका बचाव भी करता है।

#### चरण 3-4: Tool surface और schema

क्या tools के नाम और विवरण ऐसे हैं कि model की reasoning को उपयोगी लगें? पाठ 8 ने सिखाया कि tool descriptions prompt surface हैं, API documentation नहीं। Tool के नाम model के नज़रिये से बताएँ कि tool क्या करता है, न कि अंदर का endpoint क्या है। Parameter descriptions model को यह तय करने में मदद करें कि क्या पास करना है, सिर्फ़ तकनीकी schema दर्ज न करें। क्या tool set कसा हुआ है (पाठ 9 का फूलना टालता हुआ), या उसमें ऐसे tools जमा हो गए हैं जो शायद ही इस्तेमाल होते हैं?

#### चरण 5-6: Context और memory की रणनीति

लंबे चलने वाले task के लिए रणनीति क्या है? क्या design scratchpad (एक turn के भीतर चलता transcript) और runs के पार की memory (runs के बीच सहेजे गए तथ्य) में फ़र्क़ करता है? पाठ 11 ने compaction सिखाया; क्या design के पास योजना है कि transcript बढ़ने पर उसे कैसे छोटा किया जाए? अगर task में तथ्य सीखकर आगे ले जाने हैं, तो क्या कोई memory mechanism नामित है, या design सिर्फ़ transcript के भरोसे है?

#### चरण 7: Reflection और retries

जब कोई चरण फेल हो, तो क्या design retry की योजना बनाता है, और क्या उसमें स्पष्ट reflection शामिल है (agent दोबारा कोशिश से पहले प्राकृतिक भाषा में सोचता है कि वह क्यों फेल हुआ)? या वह बस loop चलाता है और उम्मीद करता है कि model ख़ुद को सुधार लेगा? पाठ 17 ने सिखाया कि चुप्पी का मतलब सीखना नहीं है; अच्छी तरह डिज़ाइन किया agent विफलता के बाद reflect करता है।

#### चरण 8: Multi-agent का फ़ैसला

अगर design multi-agent है, तो क्या वह उस चुनाव को single-agent विकल्प के सामने जायज़ ठहराता है? पाठ 19 ने coordination cost सिखाई: orchestrator-worker system tokens को कई गुना करता है और workers के बीच context को बाँट देता है। Design को वह ख़ास फ़ायदा बताना चाहिए जो इस cost को जायज़ ठहराता है। क्या फ़ायदा parallelism (wall-clock समय) है, context isolation (हर worker का transcript साफ़ रहता है), या सचमुच स्वतंत्र sub-tasks? और क्या वह फ़ायदा इसी ख़ास task पर लागू होता है?

#### चरण 14: Security और trifecta

क्या agent untrusted content पढ़ता है? क्या वह private data तक पहुँचता है? क्या उसके पास बाहरी संवाद है? पाठ 31 ने सिखाया कि तीनों शर्तें साथ हों तो वह exploit हो सकता है। Design को बताना चाहिए कि कौन-सी शर्तें मौजूद हैं और कौन-सी नहीं, या design कम से कम एक को जानबूझकर कैसे हटाता है। अगर design में तीनों हैं पर वह इसे स्वीकार नहीं करता, तो यह चेतावनी का संकेत है।

#### चरण 15: Cost और durability

क्या किसी ने प्रति पूरे task token cost का अनुमान लगाया है? क्या वह cost स्वीकार्य है? अगर system framework इस्तेमाल करता है, तो क्या framework का चुनाव जायज़ है, या वह डिफ़ॉल्ट रूप से उठा लिया गया? पाठ 33 ने सिखाया कि प्रति task असली cost में retries और token amplification शामिल हैं। अच्छा design cost का अनुमान बताता है, भले ही वह मोटा हो।

### ख़ास हुनर: विवादित दावे को मुख्य स्रोत से सुलझाना

इस track ने आपके सामने multi-agent systems के दो भरोसेमंद, विपरीत वर्णन रखे। पाठ 18 ने orchestrator-worker pattern और उनके फ़ायदे बताए। पाठ 19 ने Cognition का तर्क रखा कि ज़्यादातर multi-agent systems अपनी cost के लायक़ नहीं हैं, और बेहतर tools वाला अकेला agent अक्सर जीतता है।

दोनों वर्णन अपने-अपने क्षेत्र में सही हैं। जिस समीक्षक को दोनों आधे-अधूरे याद हैं, वह रिफ़्लेक्स में पक्ष चुन सकता है ("मैंने पढ़ा था कि single agents हमेशा बेहतर हैं, इसलिए यह multi-agent design ग़लत है") या धुँधला बीच का रास्ता निकाल सकता है ("multi-agent कभी-कभी अच्छा होता है")। दोनों में से कोई बातचीत को आगे नहीं बढ़ाता।

असली हुनर है मुख्य स्रोतों पर लौटकर जाँचना कि design की ख़ास परिस्थितियाँ उन शर्तों से मेल खाती हैं या नहीं जिनमें उस स्रोत का तर्क टिकता है।

Anthropic का "How We Built Our Multi-Agent Research System" एक ऐसे multi-agent system का वर्णन करता है जो काम किया। उस लेख को पढ़ने पर जो शर्तें उसे चलाने वाली निकलती हैं, उनमें ये हैं: sub-tasks सचमुच स्वतंत्र थे (हर researcher ने अलग कोण पर ध्यान दिया), parallelism से असली wall-clock फ़ायदा मिला (नतीजों को समय के दबाव में जोड़ना था), और टीम ने workers के बीच संवाद साफ़ रखने के लिए orchestration में भारी निवेश किया।

Cognition का "Don't Build Multi-Agents" तर्क देता है कि ज़्यादातर tasks के लिए cost जायज़ नहीं है। जिन शर्तों में उनका तर्क सबसे मज़बूत है, उनमें ये हैं: जब sub-tasks context साझा करते हैं या एक-दूसरे को निखारते हैं, जब अकेले agent के पास क्रमिक रास्ते खँगालने का समय और context budget है, और जब समस्या की तुलना में coordination का बोझ ज़्यादा है।

अब आप एक design की समीक्षा कर रहे हैं। प्रस्ताव कहता है, "हम एक orchestrator और समानांतर चलते तीन researcher workers वाला research system बना रहे हैं।" Multi-agent को स्वीकारने या ठुकराने से पहले पूछें:

- क्या तीनों research कोण सचमुच स्वतंत्र हैं, या वे context साझा करते हैं और एक-दूसरे को निखारते हैं?
- क्या कोई असली wall-clock deadline है, या आपके पास समय है कि एक agent तीनों कोणों को क्रम से खँगाले?
- क्या टीम ने orchestration के काम के लिए budget रखा है, या coordination बाद का विचार है?
- ज़्यादा चौड़े tools वाले अकेले agent की tokens में multi-agent system से तुलना में क्या cost होगी?

Design की असली परिस्थितियाँ तय करती हैं कि किस स्रोत का तर्क लागू होता है। समीक्षक का काम दोनों स्रोतों के बीच रेफ़री बनना नहीं है, बल्कि यह पता लगाना है कि design की स्थिति उन शर्तों से मेल खाती है जहाँ किसी एक स्रोत का तर्क मज़बूत या कमज़ोर होता है। अगर design के पास इन सवालों के जवाब नहीं हैं, तो उसने सवाल को मुख्य स्रोत से अभी सुलझाया नहीं है; उसने बस चुनाव का दावा किया है।

### अच्छी design समीक्षा क्या हासिल करती है

अच्छी समीक्षा "यह अच्छा है" या "यह बुरा है" नहीं कहती। वह कहती है:

"यह design Y की वजह से X चुनता है। मैंने उस चुनाव को track के चरण Z तक पहुँचाया, जहाँ ये सवाल लागू होते हैं। Design इन सवालों के जवाब साफ़ देता है और इन्हें खुला छोड़ता है। प्रतिबद्ध होने से पहले टीम को खुले सवाल सुलझाने चाहिए या जोखिम दर्ज करने चाहिए।"

जो समीक्षा ख़ास अनुत्तरित सवाल बताती है, वह pass या fail सुनाने वाली समीक्षा से ज़्यादा उपयोगी है। वह टीम को करने के लिए कुछ देती है। वह आपको दबाव भी देती है: आप लिखित में आगे के सवाल पूछ सकते हैं और design को ख़ास दावों के लिए जवाबदेह ठहरा सकते हैं, बजाय सिर्फ़ संदेह जताने के।

## अभ्यास

1. ▢ आप वित्तीय दस्तावेज़ प्रोसेस करने वाले agent के design की समीक्षा कर रहे हैं। Design कहता है कि agent के पास ये होंगे: cloud storage से documents पढ़ने का tool, transaction history के लिए customer database query करने का tool, और audit log में reports दर्ज करने का tool। Design security पर कुछ नहीं कहता। पाठ 31 के ढाँचे से, आपको कौन-से सवाल पूछने चाहिए?

<details markdown="1"><summary>जाँचें</summary>

Lethal trifecta की तीनों शर्तें मौजूद हैं: agent untrusted content पढ़ता है (अपलोड किए वित्तीय दस्तावेज़), private data तक पहुँचता है (customer transaction history), और बाहर संवाद कर सकता है (audit reports दर्ज करना)। अच्छी समीक्षा पूछती है: क्या trifecta की तीनों शर्तें ज़रूरी हैं? क्या design कम से कम एक हटा सकता है? उदाहरण के लिए, क्या agent reports सीधे दर्ज करने की जगह इंसान की मंज़ूरी के लिए मसौदा बना सकता है? या वह सिर्फ़ सारांश data पर काम करके customer database को छूने से बच सकता है? Design को या तो बताना चाहिए कि तीनों क्यों ज़रूरी हैं, या ख़ास security controls (approval gates, audit logging, sandboxing) दर्ज करने चाहिए जो जोखिम घटाते हैं।

</details>

2. ▢ एक design एक orchestrator और दो समानांतर workers का प्रस्ताव रखता है: एक प्रतिस्पर्धी products पर research करता है, दूसरा customer ज़रूरतों पर। फिर workers अपने निष्कर्ष इंसानी analyst को देते हैं, जो उन्हें जोड़ता है। आपको शक है कि single-agent विकल्प सस्ता हो सकता है। इस शक को परखने के लिए आपको पाठ 19 का कौन-सा सवाल पूछना चाहिए?

<details markdown="1"><summary>संकेत</summary>

सोचें कि इस design में orchestrator क्या कर रहा है, और क्या कोई ऐसा काम है जो अकेला agent उतना अच्छा या उतनी तेज़ी से नहीं कर सकता।

</details>

<details markdown="1"><summary>जाँचें</summary>

Token cost का अनुमान लगाएँ: दो worker agents और orchestrator का अतिरिक्त बोझ, बनाम एक agent जो दोनों कोणों पर क्रम से research करे। क्या दोनों समानांतर workers एक क्रमिक agent से तेज़ ख़त्म करते हैं (parallelism का फ़ायदा)? या अकेला agent, दोनों research सूत्रों को एक transcript में रखकर, उन्हें ज़्यादा असरदार ढंग से जोड़ता है (context coherence का फ़ायदा)? अगर workers तेज़ ख़त्म करते हैं पर token cost का गुणक ऊँचा है, और इंसानी analyst पर समय की पाबंदी नहीं है, तो अकेला agent जीतता है। अगर researchers को नतीजे तुरंत चाहिए और parallelism घंटे बचाता है, तो multi-agent cost को जायज़ ठहराता है। Design को यह गणना कर लेनी चाहिए थी; अगर नहीं की, तो आपने एक खुला सवाल खोज लिया है।

</details>

3. ▢ आप किसी agent की tool definition की समीक्षा कर रहे हैं। Tool का नाम query_customer_database है और उसका विवरण है: "Customer database से जुड़ो और user का दिया कोई भी SQL query चलाओ।"

    - a) यह अच्छी तरह डिज़ाइन किया tool है क्योंकि यह अधिकतम लचीला है
    - b) यह tool least privilege का उल्लंघन करता है; इसे इस तरह दोबारा डिज़ाइन करना चाहिए कि वह सिर्फ़ ख़ास, पहले से अधिकृत queries चलाए
    - c) यह tool स्वीकार्य है क्योंकि system prompt मना करे तो agent इसका दुरुपयोग नहीं करेगा
    - d) यह tool तब तक स्वीकार्य है जब तक agent के पास बाहरी संवाद की क्षमता नहीं है

<details markdown="1"><summary>जाँचें</summary>

**b)** यह tool least privilege का उल्लंघन करता है और इसे दोबारा डिज़ाइन करना चाहिए। यह agent को व्यापक database पहुँच देता है, जो पाठ 32 के सिद्धांत के ख़िलाफ़ है कि हर tool का दायरा ठीक उतना हो जितनी उसे ज़रूरत है। विकल्प (a) ग़लत है: developer के लिए लचीलापन अच्छे tool design जैसा नहीं है। विकल्प (c) ग़लत है: पाठ 31 ने सिखाया कि prompt instructions prompt injection के ख़िलाफ़ भरोसेमंद बचाव नहीं हैं; बचाव architecture में है। विकल्प (d) ग़लत है: बाहरी संवाद हटाने से trifecta की एक शर्त टूटेगी, पर tool फिर भी उससे ज़्यादा दायरे वाला रहेगा जितना agent को असल में चाहिए। बेहतर design: get_customer_orders नाम का tool जो customer_id लेता है और उसके orders लौटाता है, जिसमें SQL injection का कोई रास्ता ही नहीं।

</details>

4. ▢ एक टीम एक ही task के दो प्रस्तावों की समीक्षा कर रही है। प्रस्ताव A: web search, code execution और documentation tools वाला अकेला agent। प्रस्ताव B: तीन workers (search specialist, code specialist, docs specialist) वाला orchestrator, हर एक के पास एक tool। टीम ने पाठ 19 पढ़ा है और बँटी हुई है। दो engineers कहते हैं प्रस्ताव A बेहतर है क्योंकि "Cognition कहता है single agents जीतते हैं।" दो कहते हैं प्रस्ताव B बेहतर है क्योंकि "Anthropic के research system ने multi-agent इस्तेमाल किया।" आपसे इसे सुलझाने को कहा जाता है। आपका पहला क़दम क्या होना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

आधे-याद सारांशों पर नहीं, मुख्य स्रोतों पर लौटें। दोनों लेख दोबारा पढ़ें और हर एक में बताई ख़ास शर्तें पहचानें: हर स्रोत में task की विशेषताएँ, context budget, समय का दबाव और coordination की जटिलता क्या थी? फिर प्रस्ताव A और प्रस्ताव B को उन शर्तों के सामने जाँचें। क्या वे single-agent या multi-agent शर्तों से बेहतर मेल खाते हैं? क्या प्रस्ताव ख़ुद task की विशेषताएँ बताते हैं और उन शर्तों के सामने अपना चुनाव जायज़ ठहराते हैं? आपकी समीक्षा कुछ ऐसा कहे: "प्रस्ताव B उन शर्तों से मेल खाता है जहाँ Anthropic का research system सफल रहा (स्वतंत्र sub-tasks, wall-clock deadline), अगर वह coordination cost को जायज़ ठहरा सके। प्रस्ताव A Cognition वाले परिदृश्य से मेल खाता है (context को निखारने वाला काम, खुला समय budget), अगर अकेले agent का tool menu इतना चौड़ा है कि tool चुनने का अतिरिक्त बोझ न बने।" काम स्रोतों के बीच रेफ़री बनना नहीं, बल्कि हर एक को ख़ास task पर लागू करना है।

</details>

## असली दुनिया का अभ्यास

- [ ] कोई ऐसा system खोजें जिसे आप इस्तेमाल करते हैं या जानते हैं और जो अपने को agent कहता है। उसे इस पाठ की checklist के सामने रखें: वह autonomy spectrum पर कहाँ है? क्या tools model की reasoning के लिए बयान किए गए हैं या API docs की तरह? क्या वह security पर बात करता है? लिखें कि checklist के कौन-से बिंदु system साफ़ संबोधित करता है और किन पर चुप है।
- [ ] पाठ 19 से कोई एक दावा चुनें जो Cognition या Anthropic multi-agent systems के बारे में करता है। स्रोत दोबारा पढ़ें और वे ख़ास शर्तें पहचानें जिनमें वह दावा टिकता है। लिखें: task की कौन-सी विशेषताएँ दावे को सही या ग़लत बनाती हैं? आप अपने डिज़ाइन किए system पर उस दावे को कैसे परखेंगे?
- [ ] कल: किसी और के agent design की समीक्षा करें (काम से, किसी open-source project से, या तकनीकी प्रस्ताव से)। इस पाठ की checklist इस्तेमाल करें। हर उस चरण के लिए एक खुला सवाल लिखें जिसे design पूरी तरह संबोधित नहीं करता। समीक्षा design के लेखक के साथ साझा करें और देखें कि आपके सवाल उनकी अपनी चिंताओं से मेल खाते हैं या नहीं।

## आगे बढ़ने के लिए

- [लेख: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
