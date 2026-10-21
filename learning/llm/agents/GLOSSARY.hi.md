---
title: शब्दावली
description: "LLM agents के मानक शब्द"
type: glossary
---

# LLM Agents शब्दावली

Agents बनाने के मानक शब्द: loop किन चीज़ों से बना है, और उस क्षेत्र में हर हिस्से को क्या कहें जहाँ एक ही चीज़ के लिए आम तौर पर चार अलग शब्द चलते हैं।

## शब्द

**Across-run memory**:
वे तथ्य जो किसी एक trajectory के बाहर सहेजे जाते हैं और जानबूझकर नए run के शुरुआती context में वापस लोड किए जाते हैं, क्योंकि नया run खाली transcript से शुरू होता है।
_बचें_: scratchpad (दोनों अलग mechanism हैं और इन्हें गड़बड़ाना यहाँ की सबसे आम ग़लती है), state (बहुत सामान्य)

**Agent**:
ऐसा system जो language model को tools के साथ एक loop में चलाता है, और model को तय करने देता है कि कौन-सा tool कब call करना है और कब रुकना है, बजाय इसके कि वह developer के पहले से तय किए रास्ते पर चले।
_बचें_: assistant, bot, copilot (ये product के शब्द हैं जो नहीं बताते कि control flow तय है या model चुनता है)

**Agent loop**:
वह चक्र जिसे चलता हुआ agent दोहराता है: transcript को model को भेजना, जो भी tool call लौटे उसे चलाना, नतीजे को transcript में जोड़ना, और रुकने की कोई शर्त पूरी होने तक दोहराना।
_बचें_: chain, pipeline (दोनों एक तय क्रम का नाम हैं, और agent loop ठीक वही नहीं है)

**Approval gate**:
Harness स्तर की चौकी जो जोखिम भरी श्रेणी की call चलाने से पहले loop को रोक देती है, जब तक कोई व्यक्ति उसे मंज़ूर या नामंज़ूर न कर दे।
_बचें_: human-in-the-loop (बहुत व्यापक; approval gate इसी ख़ास mechanism का नाम है)

**Autonomy spectrum**:
एक prompt से लेकर developer के तय किए workflow तक और model-निर्देशित agent तक का दायरा, इस आधार पर क्रमबद्ध कि control flow का कितना हिस्सा model run के समय चुनता है, न कि developer पहले से।
_बचें_: कोई चीज़ "कितनी agentic" है (autonomy को एक धुँधली मात्रा मान लेता है, जबकि यह control-flow का सवाल है जिसका जाँचने लायक उत्तर होता है)

**Client tool**:
ऐसा tool जिसकी implementation harness के अपने code में चलती है, इसलिए model के माँगने पर harness उसे सीधे चलाता है।
_बचें_: local tool, custom tool

**Compaction**:
पुराने transcript के एक हिस्से को ऐसे संक्षिप्त सारांश से बदलना जिस पर model अब भी काम कर सके, ताकि कुछ जानकारी खोकर resident context छोटा हो जाए।
_बचें_: summarization (बहुत सामान्य; compaction ख़ास तौर पर agent के अपने transcript के लिए है, किसी भी text के लिए नहीं)

**Confused deputy**:
वैध अधिकार वाला कोई component जिसे untrusted content के ज़रिए बहकाकर हमलावर की ओर से अपने अधिकार का दुरुपयोग करवाया जाता है, जबकि वह ख़ुद compromise नहीं हुआ होता।
_बचें_: "model hack हो गया" (कुछ compromise नहीं हुआ; tool ने ठीक वही किया जिसकी उसे इजाज़त दी गई थी)

**Context poisoning**:
कोई असमर्थित या झूठा दावा transcript में आ जाना और फिर हर अगले turn में चुपचाप स्थापित तथ्य की तरह माना जाना।
_बचें_: hallucination (बहुत व्यापक; यह ख़ास तौर पर उस दावे का नाम है जो transcript में आकर टिक गया, किसी एक ग़लत output का नहीं)

**Context rot**:
Context में कम काम की सामग्री जमा होने पर model के ध्यान और सटीकता का गिरना, तब भी जब ज़रूरी जानकारी में से कुछ भी कटा न हो।
_बचें_: "context भर गया" (token की कठोर सीमा को उस नरम सटीकता-समस्या के साथ मिला देता है जो सीमा से काफ़ी पहले शुरू हो जाती है)

**Cost per completed task**:
किसी task को सफल होने के लिए जितने भी प्रयासों, retries और workers की ज़रूरत पड़ी, उन सबकी token cost, न कि सिर्फ़ आख़िरी सफल call की cost।
_बचें_: cost per API call (उस task की लागत कम गिनता है जिसे सफल होने में एक से ज़्यादा प्रयास लगे)

**Fan-out**:
Orchestrator का एक ही समस्या के अलग-अलग रूपों पर एक साथ कई workers चला देना, जिसमें token cost के बदले parallel wall-clock समय मिलता है।
_बचें_: parallelism (बहुत सामान्य; fan-out वह ख़ास multi-agent आकार है जो यहाँ इसे पैदा करता है)

**Grounding**:
Model के इरादे को असली screen coordinate या स्क्रीन पर मौजूद लक्ष्य में बदलना, एक ऐसा चरण जो अपने आप में भी नाकाम हो सकता है, तब भी जब model का बुनियादी फ़ैसला सही था।
_बचें_: click accuracy (बहुत संकरा; grounding observation से action तक की हर mapping को कवर करता है, सिर्फ़ click को नहीं)

**Handoff**:
एक agent का अपने हिस्से का काम ख़त्म करके अगले चरण के लिए दूसरे specialized agent को साफ़, सीमित context सौंपना, अपनी पूरी trajectory नहीं।
_बचें_: fan-out (handoff क्रमवार है, fan-out parallel, इस पाठ का अंतर देखें)

**Harness**:
Model के आसपास का code जो transcript रखता है, tool calls चलाता है, सीमाएँ लागू करता है और तय करता है कि loop कब ख़त्म हो। Model चुनता है; harness कार्रवाई करता है।
_बचें_: runtime, framework (framework एक संभव harness है, अवधारणा नहीं)

**Least privilege**:
हर tool को सिर्फ़ उतनी पहुँच देना जितनी उसे सच में चाहिए, बजाय "कहीं ज़रूरत पड़ जाए" सोचकर व्यापक पहुँच देने के।
_बचें_: sandboxing (sandbox एक सीमा लागू करता है; least privilege वह डिज़ाइन सिद्धांत है जो तय करता है कि वह सीमा कितनी संकरी हो)

**Lethal trifecta**:
तीन चीज़ों का मेल: private data तक पहुँच, untrusted content का सामना, और बाहर संवाद करने की क्षमता, जो मिलकर agent को exploit करने लायक बना देती हैं। इनमें से कोई एक हटाने पर हमला टूट जाता है।
_बचें_: "security risk" (इतना अस्पष्ट कि उस पर कार्रवाई नहीं हो सकती; trifecta उन तीन ख़ास शर्तों का नाम है जिन्हें जाँचना है)

**Orchestrator**:
Multi-agent system का वह agent जो task को तोड़ता है, उप-कार्य workers को सौंपता है और उनकी रिपोर्टों को जोड़ता है; उप-कार्य का काम वह ख़ुद नहीं करता।
_बचें_: manager, coordinator (सामान्य शब्द जो इस भूमिका को worker से अलग नहीं करते)

**Prompt injection**:
ऐसा content जिसे agent पढ़ता है और जिसमें उसका व्यवहार हाइजैक करने वाले instructions होते हैं, इस तथ्य का फ़ायदा उठाकर कि model संरचनात्मक रूप से data और instructions में फ़र्क़ नहीं कर पाता।
_बचें_: jailbreak (jailbreak सीधे model की अपनी refusal training को निशाना बनाता है; injection उस content के भीतर instructions छिपाता है जिसे agent को process करने को कहा गया था)

**ReAct**:
हर action के साथ एक छोटा reasoning चरण जोड़ने का pattern, ताकि हर चरण की reasoning अपने से पहले वाले चरण के असली नतीजे पर प्रतिक्रिया दे सके।
_बचें_: chain-of-thought (यह सिर्फ़ reasoning text का नाम है; ReAct उसे ख़ास तौर पर tool actions और उनके देखे गए नतीजों के साथ जोड़ता है)

**Reflection**:
ऐसा स्पष्ट चरण जहाँ agent किसी नाकाम प्रयास का प्राकृतिक भाषा में मूल्यांकन करता है और उस मूल्यांकन को अगले प्रयास में ले जाता है, उसी context के साथ सादे retry से अलग।
_बचें_: self-correction (model भीतर जो कुछ भी करता है उसके लिए ढीले तौर पर इस्तेमाल होता है; reflection बाहरी, सहेजे गए और आगे ले जाए गए रूप का नाम है)

**Retrieval on demand**:
Context में सिर्फ़ सारांश या संदर्भ रखना और पूरा ब्योरा tool call से तभी वापस लाना जब model को सच में उसकी ज़रूरत हो।
_बचें_: RAG (RAG बाहरी corpus से retrieve करता है; यह उस ब्योरे को retrieve करता है जिसे agent पहले ही बना चुका है या जिस तक उसकी सीधी पहुँच है)

**Sandbox**:
वह execution सीमा जिसे harness इस पर लागू करता है कि tool का code क्या छू सकता है (filesystem, network, resources), चाहे model ने कुछ भी माँगा हो।
_बचें_: permission (permission वह है जो आप देते हैं; sandbox वह mechanism है जो गड़बड़ या विरोधी call के बावजूद उस अनुमति को लागू रखता है)

**Scratchpad**:
वे notes जो agent एक ही run के भीतर लिखता और वापस पढ़ता है। यह असल में transcript का ही हिस्सा है, और run ख़त्म होते ही ग़ायब हो जाता है।
_बचें_: memory (scratchpad उस run से आगे नहीं बचता जिसमें लिखा गया था)

**Server tool**:
ऐसा tool जिसे provider harness की ओर से अपने infrastructure पर चलाता है, जैसे hosted web search या sandboxed code execution। Harness उसकी implementation कभी नहीं चलाता, सिर्फ़ provider के response से नतीजा पढ़ता है।
_बचें_: hosted tool, built-in tool

**Sub-agent**:
अपने transcript और harness वाला अलग agent run, जो एक सीमित काम करने के लिए चलाया जाता है, और जिसका parent के context पर एकमात्र असर वह सारांश है जो वह लौटाकर बताता है।
_बचें_: orchestrator-worker system के बाहर worker (worker उस sub-agent का नाम है जिसे orchestrator ने सीमित task दिया; mechanism वही है, शब्द भूमिका को चुनता है)

**Token amplification**:
Agentic loop के रूप में किसी task की token cost एक अकेले prompt के मुक़ाबले कितनी ज़्यादा बैठती है, transcript के दोबारा बढ़ने, multi-agent की दोहराई और retries के मिलकर बढ़ने से।
_बचें_: "agents महँगे हैं" (बहुत अस्पष्ट; amplification उस ख़ास गुणक का नाम है और बताता है कि उसका हर हिस्सा कहाँ से आता है)

**Tool**:
Model को नाम, विवरण और parameter schema के रूप में दी गई क्षमता, जिसे model माँग सकता है और harness उसकी ओर से चलाता है।
_बचें_: function call (यह model के भेजे message का नाम है, क्षमता का नहीं), plugin, skill

**Trace**:
Agent run का संरचित, timestamp वाला रिकॉर्ड जो spans से बना होता है और vendor-neutral conventions इस्तेमाल करता है, ताकि एक tool का trace दूसरे में पढ़ा जा सके।
_बचें_: log (असंरचित log वही है जिसकी जगह trace लेता है; trace का तय schema होता है जिस पर कोई tool query कर सकता है)

**Trajectory**:
एक agent run का पूरा क्रमबद्ध रिकॉर्ड: हर model turn, tool call, tool result और रुकने का फ़ैसला। विफलता की जाँच में यही पढ़ा जाता है, सिर्फ़ अंतिम उत्तर नहीं।
_बचें_: transcript (message सूची जो model असल में देखता है और जिसमें harness के अपने फ़ैसले नहीं होते), history, log

**Worker**:
Orchestrator से सीमित उप-कार्य पाने वाला sub-agent, जो दूसरे workers से अलग अपना loop और transcript चलाता है।
_बचें_: orchestration की भूमिका के लिए sub-agent (sub-agent mechanism का नाम है; worker उसके भीतर इस ख़ास भूमिका का नाम है)

**Workflow**:
ऐसा system जहाँ developer ने model calls और tool calls का क्रम पहले से तय कर दिया है। उसमें branches और loops हो सकते हैं, पर रास्ता model नहीं चुनता।
_बचें_: agent (दोनों का अंतर ही चरण 1 का मुद्दा है), chain
