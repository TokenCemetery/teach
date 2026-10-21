---
title: "35. Durability और Framework क्या देता है"
description: Durable, resumable agent execution एक engineering समस्या के रूप में, frameworks ठोस रूप से क्या देते हैं, और किसी को अपनाने का निर्णय-सिद्धांत
type: lesson
---

# पाठ 35. Durability और Framework क्या देता है

**मिशन से संबंध:** तय करें कि agent harness ख़ुद लिखना है या framework अपनाना है, इस आधार पर कि deployment के लिए आपको असल में कौन-सी गारंटियाँ चाहिए।
**मुख्य स्रोत:** [लेख: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**पूर्व-आवश्यकताएँ:** [पाठ 34](0034-prompt-caching-and-concurrency.md), [Harness](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 7 से आपने सीखा कि चूँकि transcript agent की पूरी state है, run को फिर शुरू करने का मतलब है सहेजा हुआ transcript model को वापस देना। इसका इस बारे में क्या मतलब है कि run "सिद्धांत में resumable" है या नहीं?

<details markdown="1"><summary>जाँचें</summary>

सिद्धांत में, कोई भी agent run resumable है क्योंकि transcript वह सब कुछ पकड़ता है जो agent जानता है। अगर आप हर turn के बाद transcript सहेजें और crash हो जाए, तो आप सहेजा हुआ transcript लोड कर सकते हैं, आख़िरी असफल या अधूरे turn को जोड़ सकते हैं, और जारी रख सकते हैं। Transcript ही पूरी state है, इसलिए फिर शुरू करने के लिए और कुछ नहीं चाहिए।

</details>

2. ▢ पाठ 33 से आपने सीखा कि cost-per-task का budget task के सफल होने तक सारे प्रयासों, retries और reflections की पूरी cost जोड़ता है। अगर agent run के बीच crash हो जाए और आपको शुरू से दोबारा चलाना पड़े, तो यह cost-per-task के budget को कैसे प्रभावित करता है?

<details markdown="1"><summary>जाँचें</summary>

दोबारा शुरू करने से budget में एक पूरा अतिरिक्त प्रयास जुड़ जाता है। अगर agent 30-turn के run के turn 15 पर crash होता है, तो आपने 15 turns का काम खोया और सारे 30 turns का फिर भुगतान करना होगा। Cost-per-task का budget अब लगभग दोगुना है (एक की जगह दो पूरे 30-turn runs)। यह भारी cost का जुर्माना है, इसीलिए durability (crashes से बचना और आख़िरी सहेजी state से अपने आप फिर शुरू होना) cost के नियंत्रण के लिए मायने रखती है।

</details>

## यह जानें

### Durability सिद्धांत की resumability से अलग है

पाठ 7 ने स्थापित किया कि agent runs सिद्धांत में resumable हैं: transcript ही state है। पर "सिद्धांत में resumable" और "production में resumable" अलग चीज़ें हैं। सिद्धांत में resumability कहती है "अगर कोई इंसान हाथ से transcript सहेजकर agent फिर चलाए, तो वह जारी रहेगा।" Production में durability कहती है:

- Transcript हर turn के बाद अपने आप टिकाऊ storage (database, backups वाला file system, सिर्फ़ memory नहीं) में सहेजा जाता है।
- अगर process crash होता है, तो आख़िरी सहेजी state अपने आप लोड होती है और run बिना हाथ के दख़ल के फिर शुरू होता है।
- अगर कई agents एक साथ चलते हैं, तो हर एक की state अलग से ट्रैक होती है ताकि एक का crash दूसरे का काम न खोए।
- अगर tool call का timeout हो जाए या network फेल हो, तो agent retry करता है या सलीक़े से rollback करता है, अधूरी state नहीं छोड़ता।

यह infrastructure का काम agent loop से अलग है (पाठ 6)। Loop को durability की परवाह नहीं; वह बस वही process करता है जो उसे दिया जाता है। Harness (loop के आसपास का code) को durability को स्पष्ट चिंता के रूप में बनाना पड़ता है।

### Durability के बिना crashes और विफलताएँ कैसी दिखती हैं

टिकाऊ state के बिना, failure modes ये हैं:

- Run के बीच process crash: agent का पूरा transcript खो जाता है (अगर वह सिर्फ़ memory में था)। उपयोगकर्ता को task शुरू से दोबारा चलाना पड़ता है। Cost-per-task का budget दोगुना हो जाता है।
- Tool call पर network timeout: harness नहीं जानता कि tool सफल हुआ या फेल। वह retry कर भी सकता है, नहीं भी। Transcript में नतीजा जुड़ा हो भी सकता है, नहीं भी, harness के error handling पर निर्भर। State असंगत हो जाती है।
- Agent tool के नतीजे का इंतज़ार करते हुए अटक जाता है: process अटका है और उसे हाथ से बंद करना पड़ेगा। कोई checkpoint नहीं सहेजा गया। पूरा run खो जाता है।
- कई agents एक साथ चल रहे हैं, एक crash होता है: बाक़ी agents चलते रहते हैं, पर इसकी कोई जानकारी नहीं कि system का कौन-सा हिस्सा फेल हुआ या फेल हुए को कैसे फिर शुरू करें।

इनमें से हर एक असली deployment समस्या है। "Durable execution" ऐसे systems बनाने का अभ्यास है जो इन विफलताओं को अपने आप और सही ढंग से सँभालते हैं।

### Framework ठोस रूप से क्या देता है

जब आप agent विकास के लिए framework अपनाते हैं, तो उसमें आमतौर पर इनमें से कुछ या सभी गारंटियाँ होती हैं:

**Durable state और स्वचालित checkpointing।** Framework हर turn के बाद transcript (और agent की कोई भी state) को अपने आप टिकाऊ storage में सहेजता है। अगर process crash होता है, तो अगला run आख़िरी checkpoint अपने आप लोड करके वहीं से जारी रखता है। आपको persistence का तर्क ख़ुद नहीं लिखना पड़ता।

**Graph-आधारित control flow।** हाथ से loop लिखने (पाठ 6) की जगह, आप agent की संरचना graph के रूप में बताते हैं: "इस चरण के बाद, अगर नतीजा X है, तो यहाँ जाओ; अगर Y, तो वहाँ जाओ।" Framework control flow और persistence सँभालता है, इसलिए आप loop की जगह nodes (चरणों) पर ध्यान देते हैं। यह जटिल branching या शर्त वाले तर्क के agents के लिए काम का है।

**Built-in retry और backoff नीतियाँ।** जब tool call फेल होती है (network error, timeout, rate limit), तो framework के पास तय retry रणनीति होती है: थोड़ा रुको, फिर कोशिश करो, exponential backoff। आपको अपने harness में retries लागू नहीं करनी पड़तीं।

**एकीकृत tracing और observability।** Framework अपने आप पाठ 29 के संरचित traces बनाता है: timestamp वाले events, spans, हर चरण का metadata। आप इस trace को बिना ख़ुद जोड़े query कर सकते हैं। कुछ frameworks observability backends (जैसे tracing service) से जुड़ते हैं ताकि आप agent runs को dashboard में देख सकें।

**Rollback और compensation।** कुछ frameworks आपको compensating actions परिभाषित करने देते हैं: अगर चरण A सफल हुआ पर चरण B फेल हुआ, तो A को अपने आप पलट दो। यह उन agents के लिए काम का है जो बाहरी systems में बदलाव करते हैं और बाद के चरण फेल होने पर सँभलना चाहते हैं।

सब frameworks ये सब नहीं देते। कुछ न्यूनतम हैं (checkpointing और retries)। कुछ व्यापक हैं (ऊपर का सब और भी बहुत कुछ)। निर्णय-सिद्धांत (नीचे) इस बारे में है कि आपको असल में कौन-सी क्षमताएँ चाहिए।

### Frameworks क्या नहीं देते

यह साफ़ होना ज़रूरी है कि frameworks क्या नहीं सुलझाते:

- Agent loop ख़ुद अब भी वही है (पाठ 6 से)। Framework loop को सरल या तेज़ नहीं बनाता; वह बस उसे durability और observability से लपेटता है।
- Framework इस्तेमाल करने से token cost नहीं घटती। Framework agents को सस्ता नहीं बनाता; वह उन्हें ज़्यादा भरोसेमंद और दिखने वाला बनाता है।
- Framework से agent की reasoning की गुणवत्ता नहीं सुधरती। Framework model को फ़ैसलों में बेहतर नहीं बनाता; tools, prompts और planning (पाठ 8, 9, 16) आपको अब भी ख़ुद डिज़ाइन करने पड़ते हैं।
- Framework तटस्थ नहीं है। Framework अपनाना आपको उसकी abstractions (graph-आधारित control flow, उसका configuration format, उसका observability मॉडल, उसकी deployment बंदिशें) से बाँध देता है। बाद में frameworks बदलना महँगा है।

### निर्णय का सिद्धांत: framework कब अपनाएँ

"Building Effective Agents" लेख बताता है कि कई टीमें पहले न्यूनतम agent loop (पाठ 6) बनाती हैं और बाद में ही समझती हैं कि उन्हें durability चाहिए। Framework अपनाने का फ़ैसला इस पर आधारित होना चाहिए कि framework की गारंटियाँ ऐसी deployment समस्या सुलझाती हैं जो आपके पास है, इस पर नहीं कि loop लिखना कठिन लगा (loop आसान हिस्सा है)।

Framework तब अपनाएँ जब:

- **आपको durable execution चाहिए।** आपके agents इतनी देर चलेंगे (या इतने ज़रूरी होंगे) कि crashes से काम खोना अस्वीकार्य है। बिना persistence का सादा loop production tasks के लिए उपयुक्त नहीं।
- **आपको बड़े पैमाने पर observability चाहिए।** आपके कई agents एक साथ चल रहे हैं और आपको देखना है कि हर एक क्या कर रहा है, विफलताएँ trace करनी हैं, और logs को जोड़ना है। बुनियादी print-statement harness बड़े पैमाने पर नहीं चलेगा।
- **आपके पास जटिल control flow है।** आपके agent को शर्त वाली branching या loops चाहिए (जैसे "इस शर्त में tools का यह सेट call करो; वरना वह दूसरा सेट")। Framework का graph-आधारित मॉडल हाथ से लिखी शर्तों से ज़्यादा साफ़ है।
- **आपको built-in retry और backoff चाहिए।** आप बाहरी APIs call कर रहे हैं जो अस्थायी रूप से फेल हो सकती हैं, और आप चाहते हैं कि framework exponential backoff के साथ retries अपने आप सँभाले। यह ख़ुद लिखना उबाऊ और ग़लती की गुंजाइश वाला है।

Framework तब न अपनाएँ जब:

- **आप प्रयोग कर रहे हैं।** शोध या prototyping में, framework सीखने की तुलना में सादे loop पर दोहराना तेज़ है। तरीक़ा स्थिर होने पर framework के फ़ैसले पर लौटें।
- **आपका agent सरल है।** कुछ tool calls और सीधे लक्ष्य वाले अकेले agent को framework की जटिलता नहीं चाहिए। Loop और transcript file ही काफ़ी हो सकते हैं।
- **आपकी deployment की बंदिशें असामान्य हैं।** कुछ frameworks ख़ास environments (cloud, Docker आदि) मानते हैं या ऐसी performance विशेषताएँ रखते हैं जो आपकी बंदिशों में नहीं बैठतीं। आपको कस्टम harness चाहिए हो सकता है।
- **Framework अपरिपक्व है या किसी vendor से कसकर जुड़ा है।** Durable execution के patterns अब भी विकसित हो रहे हैं। कुछ frameworks अच्छी तरह स्थापित और दर्ज हैं (समीक्षाएँ और production deployments खोजें); कुछ नहीं। और कुछ एक vendor की API से कसकर जुड़े हैं, जो बाद में आपका लचीलापन सीमित करता है।

### Framework का मूल्यांकन कैसे करें

अगर आप framework अपनाने का फ़ैसला करते हैं, तो ये सवाल पूछें:

- क्या वह checkpointing और resumption का समर्थन करता है? कितनी बार? क्या checkpoint की बारीकी (प्रति turn, प्रति प्रयास, प्रति task) वही है जो आपको चाहिए?
- वह कौन-सी observability देता है? क्या आप traces query कर सकते हैं? क्या आप अपने मौजूदा logging और monitoring से जोड़ सकते हैं?
- वह कौन-सी control flow abstractions समर्थित करता है? क्या वे आपके agent की संरचना से मेल खाती हैं, या आपको अपने agent को उसमें फिट करने के लिए मोड़ना पड़ेगा?
- अगर framework ख़ुद crash हो, तो failure mode क्या है? क्या आप framework के बिना अपने transcripts वापस पाकर जारी रख सकते हैं?
- वह concurrency कैसे सँभालता है? क्या कई agents बिना एक-दूसरे में दख़ल दिए स्वतंत्र रूप से चल सकते हैं?
- Vendor lock-in क्या है? अगर आपको बाद में बदलना पड़े, तो कितना काम होगा?

आख़िरी सवाल ज़रूरी है: durable agent execution के लिए कोई एक प्रामाणिक, vendor-neutral स्रोत नहीं है जैसे, मान लें, MCP विनिर्देश (पाठ 20) के लिए है। Durable execution के patterns मुख्य रूप से अलग-अलग frameworks के अपने guides के भीतर दर्ज हैं। इसलिए इस पाठ को शब्दावली और निर्णय का ढाँचा मानें, frameworks की तुलना नहीं। जब आप किसी ख़ास framework का मूल्यांकन करें, तो उसकी ख़ास गारंटियाँ समझने के लिए उसके अपने दस्तावेज़ पढ़ें।

### शुरू से अंत की कहानी: loop से production तक

यह सामान्य agent system की रूपरेखा है:

1. **विकास (पाठ 6)।** ऐसा loop लिखें जो transcript model को भेजे और tools चलाए। इसे prototype करना तेज़ है।
2. **परीक्षण (पाठ 29)।** Traces और निदान बनाएँ ताकि समझें कि आपका agent क्या कर रहा है, कब फेल होता है, और क्यों। जानें कि आपका agent कहाँ नाज़ुक है।
3. **अनुकूलन (पाठ 10-34)।** Context प्रबंधन, prompt caching, बेहतर planning लागू करें। Token cost और latency घटाएँ।
4. **Deployment।** अब आपको तय करना है: production कैसा दिखता है? अगर यह एक बार का task या प्रयोग है, तो script और transcript file काफ़ी हो सकते हैं। अगर यह उपयोगकर्ताओं को सेवा देने वाली service है, तो सादा loop उपयुक्त नहीं। आपको durability, observability, retry नीतियाँ, और कई concurrent agents को ट्रैक करने का तरीक़ा चाहिए। यहीं framework का फ़ैसला आता है।

Framework शुरुआत नहीं है; वह इस सवाल का जवाब है कि "durability और observability की परत कौन बनाता और सँभालता है?" आप उसे ख़ुद बनाते हैं (कस्टम harness और infrastructure), या आप framework का जवाब अपनाते हैं (उसकी abstractions और बंदिशें स्वीकार करें)। दोनों वैध चुनाव हैं। Framework का फ़ैसला "क्या मैं agent loop लिख सकता हूँ" नहीं है (पाठ 6 पहले ही हाँ में जवाब दे चुका)। सवाल है "क्या मैं यह production infrastructure ख़ुद बनाना चाहता हूँ, या किसी मौजूदा framework का हल अपनाना चाहता हूँ?"

## अभ्यास

1. ▢ आप 1,000 customer support tickets process करने के लिए agent चला रहे हैं। हर ticket को सँभालने में agent के 20 turns लगते हैं। अगर agent ticket 500 के turn 10 पर crash हो जाए और आपके पास checkpointing नहीं है, तो कुल कितने turns खोए या बर्बाद हुए?

<details markdown="1"><summary>जाँचें</summary>

आप ticket 500 पर 10 turns का काम खोते हैं। जब process फिर शुरू होता है, तो आपको पूरा ticket शुरू से दोबारा चलाना पड़ता है, जो और 20 turns बर्बाद करता है। आपको tickets 1-499 भी दोबारा चलाने पड़ते हैं (जो पूरे हुए थे पर अगर process crash हुआ तो अब भी memory में या खोए हुए हैं)। अगर आपके पास checkpointing होती, तो आप हर ticket के बाद सहेजते, इसलिए एक ticket खोने की cost 20 turns है, उससे ज़्यादा नहीं। 1,000 tickets * 20 turns = कुल 20,000 turns। Checkpointing के बिना, task के बीच का crash लगभग 10,000 turns बर्बाद करता है (बचे हुए काम का आधा और crash हुए task को दोबारा चलाना)। इसीलिए बड़े पैमाने के tasks के लिए durability मायने रखती है।

</details>

2. ▢ आपके agent system के लिए दो विकल्प हैं: विकल्प A है durability (checkpointing, retries, observability) वाला कस्टम harness लिखना। इसे बनाने और debug करने में 2 हफ़्ते लगते हैं। विकल्प B है मौजूदा framework अपनाना (जो यह सब आपके लिए सँभालता है) और उसे सीखने में 1 हफ़्ता लगाना। दोनों systems वही agent logic चलाएँगे। लंबे समय में विकल्प B फिर भी ज़्यादा महँगा क्यों हो सकता है?

<details markdown="1"><summary>संकेत</summary>

लचीलेपन, रखरखाव, और इस बारे में सोचें कि अगर आपकी ज़रूरतें बदलें या आप systems बदलना चाहें तो क्या होता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

विकल्प B आपको framework की abstractions और implementation से बाँध देता है। अगर आपकी ज़रूरतें बदलती हैं (जैसे आपको अलग control flow या अलग storage backend चाहिए), तो आप उससे बँधे हैं जो framework समर्थित करता है। अगर आप बाद में frameworks बदलना चाहें, तो आपको अपने सारे agent definitions और workflows port करने पड़ते हैं। विकल्प A (कस्टम harness) ज़्यादा लचीला है पर शुरू में और रखरखाव में ज़्यादा महँगा। समझौता यह है: विकल्प B शुरू में समय बचाता है पर आपको बाँध देता है; विकल्प A शुरू में ज़्यादा क़ीमत लेता है पर लंबे समय का लचीलापन देता है। बराबरी का बिंदु इस पर निर्भर है कि आप system के कितनी देर चलने की उम्मीद करते हैं और ज़रूरतों के बदलने की कितनी संभावना है।

</details>

3. ▢ आप agent विकास के लिए दो frameworks का मूल्यांकन कर रहे हैं। Framework X checkpointing और retries देता है पर एकीकृत observability नहीं (tracing आपको ख़ुद जोड़नी पड़ती है)। Framework Y वह सब और graph-आधारित control flow builder देता है, पर सभी agents को अपनी proprietary DSL में परिभाषित करना ज़रूरी है। अगर आपकी मुख्य चिंता agent के crash होने पर काम से बचना और अपने आप फिर शुरू होना है, तो आपको कौन-सा framework चुनना चाहिए?

    - a) Framework X, क्योंकि वह सरल है और आपको कम सीखना पड़ता है।
    - b) Framework Y, क्योंकि उसकी एकीकृत observability crashes को तेज़ी से debug करने में मदद करेगी।
    - c) दोनों में से कोई भी आपकी ज़रूरत की मुख्य checkpointing सुविधा देता है; चुनाव आपकी दूसरी बंदिशों पर निर्भर है।
    - d) कोई नहीं; आपको कस्टम harness बनाना चाहिए ताकि आप बँधें नहीं।

<details markdown="1"><summary>जाँचें</summary>

**c)** दोनों frameworks checkpointing और स्वचालित resumption देते हैं, जो आपकी मुख्य चिंता है। अंतर (observability, DSL) गौण हैं। अगर आपको एकीकृत observability चाहिए या graph-आधारित मॉडल पसंद है, तो Framework Y lock-in के लायक़ हो सकता है। अगर आप observability ख़ुद जोड़ना पसंद करते हैं या आपके पास Python/Go आदि में मौजूदा agent code है, तो Framework X ठीक है। कोई ग़लत नहीं है; यह आपकी दूसरी बंदिशों पर निर्भर है। विकल्प a ग़लत है क्योंकि अकेली सरलता निर्णायक कारक नहीं है। विकल्प b observability (अच्छी-सी चीज़) को durability (आपकी बताई ज़रूरत) से मिला देता है। विकल्प d ग़लत नहीं है (कस्टम harness हमेशा लचीलापन देता है) पर वह सवाल से बचता है; अगर durability ज़रूरी है, तो आपको कोई हल चाहिए, और फ़ैसला यह है कि वह हल framework है या कस्टम।

</details>

4. ▢ आपने बिना persistence के सादा loop (पाठ 6) से agent बनाया है। Agent testing में अच्छा चलता है। अब आप उसे असली उपयोगकर्ता अनुरोध सँभालने के लिए production में deploy करना चाहते हैं। भरोसे से कहने से पहले कि agent production में durable है, आपको न्यूनतम कौन-सा infrastructure जोड़ना होगा?

<details markdown="1"><summary>जाँचें</summary>

कम से कम: (1) हर loop turn के बाद transcript का टिकाऊ storage (backups वाला database या filesystem) में स्वचालित persistence। (2) Process के फिर शुरू होने पर आख़िरी सहेजे transcript का स्वचालित लोड होना, ताकि agent शुरू से नहीं, आख़िरी checkpoint से जारी रखे। (3) Tool calls के लिए सलीक़े वाला error handling: अगर tool का timeout हो या error लौटे, तो agent या तो backoff नीति से retry करे या विफलता को transcript में साफ़ दर्ज करे (ताकि state संगत रहे)। (4) Concurrent agents के लिए, हर agent का अपना अलग transcript और checkpoint होना चाहिए। ये चार हिस्से development loop को ऐसी चीज़ में बदलते हैं जो crashes झेल सके और production ट्रैफ़िक सँभाल सके।

</details>

## असली दुनिया का अभ्यास

- [ ] किसी एक production agent framework (जैसे LangGraph, CrewAI, Anthropic के Managed Agents, या कोई और framework जिसे आप जानते हों) के दस्तावेज़ों की समीक्षा करें। उसकी दी हुई ख़ास durability गारंटियाँ लिखें: क्या सहेजा जाता है, कितनी बार, और recovery कैसे सँभाली जाती है?
- [ ] सरल agent के लिए durability की परत डिज़ाइन करें। वे हिस्से लिखें जो आपको बनाने पड़ेंगे: checkpointing (क्या और कब), resumption (कैसे और कब), error handling (retries, backoff), observability (क्या log करें)। अनुमान लगाएँ कि इसे सही ढंग से बनाने और परखने में कितनी पंक्तियों का code लगेगा।
- [ ] कल: काल्पनिक agent task खींचें और उसकी deployment ज़रूरतों का अनुमान लगाएँ। क्या आपके use case के लिए सादा loop और transcript file स्वीकार्य होंगे, या आपको framework-स्तर की durability और observability चाहिए? फ़ैसला और तर्क लिखें।

## आगे बढ़ने के लिए

- [लेख: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
