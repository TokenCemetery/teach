---
title: LLM Agents
description: "Loop ख़ुद बनाएँ: tools, context, memory, और यह पहचानना कि कब agent ग़लत जवाब है"
type: topic
---

# सीखना: LLM Agents

Agent loop ख़ुद बना सकें, तय कर सकें कि किसी task को तय workflow की जगह agent की ज़रूरत है भी या नहीं, और असफल agent को उसके prompt में एक और instruction जोड़ने के बजाय उसकी trajectory से जाँच सकें।

**नवीनतम पाठ:** [0037. किसी और के Agent Design की समीक्षा](lessons/0037-reviewing-someone-elses-agent-design.md)

## सफलता कैसी दिखती है

- किसी दिए गए task के लिए agent loop लिखें, और बताएँ कि उसके context का हर message क्या कर रहा है और loop को क्या ख़त्म करता है।
- किसी task के लिए एक अकेले prompt, तय workflow और agent में से चुनें, और अपने चुनाव का बचाव उस विकल्प की cost के सामने करें जिसे आपने छोड़ा।
- Agent की tool सतह डिज़ाइन करें: नाम, विवरण, return shapes, और वह permission सीमा जो तय करती है कि वह बिना निगरानी के क्या कर सकता है।
- असफल agent को उसकी trajectory से जाँचें और कारण का नाम बताएँ (loop, poisoned context, ग़लत specified tool, ग़लत stopping condition), बजाय बेतरतीब ढंग से दोबारा prompt करने के।
- समझाएँ कि untrusted content पढ़ने वाले agent को सिर्फ़ prompt instructions से सुरक्षित क्यों नहीं किया जा सकता, और वह सीमा डिज़ाइन करें जो सच में टिकती है।
- Agentic loop की token cost और latency का budget बनाएँ, और बताएँ कि amplification loop के किस हिस्से से आता है।

## सीमाएँ

- कोई तय provider नहीं। Loops, tool schemas और control flow Python जैसे pseudocode में दिए गए हैं, ताकि सामग्री tool-calling API के उन बदलावों से बची रहे जो ज़्यादातर agent लेखन को पुराना कर देते हैं।
- Wire formats अपवाद हैं, क्योंकि tool-call message wire पर कैसा दिखता है यह एक तथ्य है, algorithm नहीं। असली capture किया हुआ एक request और response जोड़ा दिखाया गया है, और दूसरा provider सिर्फ़ उससे अंतर के रूप में आता है।
- कोई framework माना या सिखाया नहीं गया। Framework क्या देता है (durable state, graph control flow, resumption) वह अंत के पास एक बार, tutorial के बजाय एक फ़ैसले के रूप में आता है।
- अभ्यास build से ज़्यादा inspection पर टिके हैं: असली trace पढ़ना, असली tool schema पढ़ना, असली MCP server manifest पढ़ना, और जो agent पहले से चल रहा है उसकी permission सीमा चिह्नित करना।
- मानकर चलता है कि आप जानते हैं language model क्या है और Python जैसा code पढ़ने में सहज हैं। Agent बनाने का पहले का अनुभव ज़रूरी नहीं।

## दायरे से बाहर

- एक विषय के रूप में Evaluation: [`llm/evals`](../../llm/evals/) देखें (पाठ 0013 trajectories, step accuracy के मुक़ाबले task success, और `pass^k` कवर करता है)। यहाँ इसे सिर्फ़ उस एक क्षमता के रूप में रखा गया है जिसकी agent बनाने वाले को ज़रूरत है, और दोहराने के बजाय link किया गया है।
- Retrieval pipeline के भीतरी हिस्से: [`llm/rag`](../../llm/rag/) देखें। Retrieval यहाँ agent के call किए जाने वाले tool के रूप में आता है, chunking, embedding और reranking के रूप में नहीं।
- Serving और inference के भीतरी हिस्से: latency, batching और constrained decoding के लिए [`llm/inference`](../../llm/inference/) देखें।
- Model को tools इस्तेमाल करना सिखाने के लिए train करना: [`llm/finetuning`](../../llm/finetuning/) देखें।
- Retries, idempotency और partial failure जैसी distributed-systems की समस्याएँ: [`architecture/distributed-systems`](../../architecture/distributed-systems/) देखें। यहाँ सिर्फ़ उतना कवर है जो tool call को आम remote call से अलग बनाता है।
- एक विषय के रूप में Prompting (instructions, examples, reasoning, structured output, templates और prompt में बदलाव मापना): [`llm/prompting`](../../llm/prompting/) देखें। यह track tool descriptions, tools के साथ injection और concurrency में caching अपने पास रखता है, और सामान्य prompting के लिए वहाँ link करता है।

## पूरी रूपरेखा

सोलह चरण, बिना पूर्व ज्ञान से लेकर वरिष्ठ स्तर के विवेक तक। यह पाठों की सूची नहीं है: एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
| --- | --- | --- | --- |
| 1. Agent क्या है | 0001 से 0002 | Loop, agent बनाम workflow बनाम chain, autonomy spectrum | किसी system को वर्गीकृत कर सकें और बता सकें कि उसके लिए "agent" शब्द सही है या नहीं |
| 2. Tool calling की mechanics | 0003 से 0005 | Tool call का wire format, parameter schemas, कौन क्या चलाता है, parallel calls, results के रूप में लौटे errors | कच्चा tool-call exchange पढ़कर बता सकें कि हर message ने क्या किया |
| 3. Loop शुरू से | 0006 से 0007 | Loop लिखना, stopping conditions, agent की पूरी state के रूप में transcript | Agent loop लिख सकें और बचाव कर सकें कि वह कहाँ रुकता है |
| 4. Prompt engineering के रूप में Tool design | 0008 से 0009 | Prompt सतह के रूप में नाम और विवरण, return shapes, result की token cost, tool-set का फूलना | Tool सतह डिज़ाइन कर सकें और बता सकें कि हर विवरण उसी शब्दों में क्यों लिखा गया है |
| 5. Context प्रबंधन | 0010 से 0012 | केंद्रीय budget के रूप में window: truncation, compaction, retrieval on demand, context isolation के रूप में sub-agents | लंबे चलने वाले task के लिए योजना बना सकें कि context से क्या और कब बाहर जाएगा |
| 6. Memory और state | 0013 से 0014 | Run के भीतर का scratchpad बनाम across-run memory, memory के रूप में files, retrieval memory क्यों नहीं है | चुन सकें कि कोई तथ्य कहाँ रहे और बता सकें कि run ख़त्म होने पर क्या होता है |
| 7. Planning और reflection | 0015 से 0017 | ReAct, plan-then-execute, self-critique, decomposition, reasoning models ने क्या बदला | Task के लिए planning pattern चुन सकें और बता सकें कि उसकी tokens और latency में क्या क़ीमत है |
| 8. Multi-agent | 0018 से 0019 | Orchestrator और worker, handoff, fan-out, coordination cost, कब बेहतर tools वाला एक agent जीतता है | बता सकें कि दूसरा agent ऐसा कुछ देता है या नहीं जो पहले agent को दिया ही नहीं जा सकता था |
| 9. Protocols और interop | 0020 से 0021 | MCP के tools, resources, prompts और transports, provider function-calling formats, बड़े पैमाने पर tool discovery | MCP server का manifest पढ़कर बता सकें कि वह क्या expose करता है और क्या standardise नहीं करता |
| 10. Execution environments | 0022 से 0023 | Sandboxing, tool के रूप में code execution, filesystem access, human-in-the-loop approval gates | Tools के दिए गए सेट के लिए sandbox सीमा तय कर सकें |
| 11. Computer use और browser agents | 0024 से 0026 | Observations के रूप में screenshots, action को coordinate से जोड़ना (grounding), विश्वसनीयता की समस्या | बता सकें कि screen चलाने वाला agent tool-calling वाले agent से अलग तरह से क्यों फेल होता है |
| 12. Failure modes और observability | 0027 से 0029 | Loops, context poisoning, cascading tool errors, hallucinated arguments, tracing और trajectory replay | Trajectory मिलने पर दोषी चरण का नाम बता सकें, दोबारा prompt करने के बजाय |
| 13. Agent का evaluation | 0030 से 0030 | Outcome बनाम trajectory, बार-बार trials में विश्वसनीयता, agent benchmarks असल में क्या मापते हैं | बता सकें कि किसी agent के लिए क्या मापना है, और बाक़ी `llm/evals` को सौंप सकें |
| 14. Security | 0031 से 0032 | Agent की निर्णायक समस्या के रूप में prompt injection, lethal trifecta, least privilege, confused deputy, MCP supply chain | ऐसी permission सीमा डिज़ाइन कर सकें जो तब भी टिके जब agent शत्रुतापूर्ण content पढ़े |
| 15. Production, cost, और frameworks क्या देते हैं | 0033 से 0035 | Token amplification, prompt caching, concurrency, durability और resumability, cost per completed task | Loop की cost का budget बना सकें और बता सकें कि deployment को framework की कौन-सी गारंटी सच में चाहिए |
| 16. विवेक | 0036 से 0037 | Agent कब नहीं बनाना, किसी और के agent design की समीक्षा करना और बताना कि कोई चुनाव क्या क़ीमत माँगता है, विवादित दावे को primary source से सुलझाना | फ़ैसला लेने और उसे किसी और को समझाने के लिए भरोसेमंद |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-the-agent-loop.md) | Agent Loop | कोई system agent कब बनता है, और उसके नीचे चलने वाला चार चरणों का चक्र |
| [0002](lessons/0002-agent-workflow-or-prompt.md) | Agent, Workflow या सिर्फ़ एक Prompt | Task autonomy spectrum पर कहाँ बैठता है, और अपने चुनाव का बचाव कैसे करें |
| [0003](lessons/0003-the-wire-format-of-a-tool-call.md) | Tool Call का Wire Format | आपके harness और model provider के बीच के protocol में tool call और उसका result असल में कैसे दिखते हैं |
| [0004](lessons/0004-schemas-and-who-executes.md) | Parameter Schemas और कौन क्या चलाता है | JSON schemas model के भेज सकने वाले को कैसे सीमित करते हैं, और client tools तथा server tools का अंतर |
| [0005](lessons/0005-parallel-calls-and-errors-as-results.md) | Parallel Calls और Results के रूप में Errors | Model एक साथ कई tools कैसे माँग सकता है, और tool errors exceptions नहीं, results क्यों हैं |
| [0006](lessons/0006-writing-the-loop.md) | Loop लिखना | Pseudocode से agent loop बनाना और stopping conditions सोच-समझकर चुनना |
| [0007](lessons/0007-the-transcript-as-state.md) | State के रूप में Transcript | यह समझना कि turns के बीच transcript ही agent की एकमात्र टिकाऊ memory है |
| [0008](lessons/0008-naming-and-describing-a-tool.md) | Tool का नाम रखना और उसे बयान करना | Tool का नाम और विवरण ही वह है जिसे पढ़कर model तय करता है कि उसे कब और कैसे call करना है |
| [0009](lessons/0009-return-shapes-and-tool-set-bloat.md) | Return Shapes और Tool-Set का फूलना | Tool का return value context budget से क़ीमत वसूलता है, और बहुत ज़्यादा tools model की सही चुनने की क्षमता बिगाड़ते हैं |
| [0010](lessons/0010-the-context-window-as-budget.md) | Budget के रूप में Context Window | Context window सीमित संसाधन है जिसे harness समय के साथ सक्रिय रूप से सँवारता है, कोई निष्क्रिय log नहीं |
| [0011](lessons/0011-compaction-and-retrieval-on-demand.md) | Compaction और Retrieval on Demand | लंबे चलने वाले agent का context budget में रखने की दो रणनीतियाँ, जबकि जो अब भी मायने रखता है वह बचा रहे |
| [0012](lessons/0012-sub-agents-as-context-isolation.md) | Context Isolation के रूप में Sub-Agents | Sub-agent चलाने से लंबा खोजबीन वाला काम parent के context budget से अलग रहता है |
| [0013](lessons/0013-scratchpad-versus-memory.md) | Scratchpad बनाम Memory | एक run के दौरान agent के रखे notes और कई runs में ज़रूरी तथ्यों का अंतर |
| [0014](lessons/0014-files-as-memory.md) | Memory के रूप में Files | Agents के लिए across-run memory के सबसे सरल रूप के तौर पर टिकाऊ files का इस्तेमाल |
| [0015](lessons/0015-react-interleaving-reasoning-and-acting.md) | ReAct: Reasoning और Acting को आपस में जोड़ना | हर action के साथ छोटे reasoning चरण जोड़ने का pattern, ताकि model देखकर ख़ुद को ढाल सके |
| [0016](lessons/0016-plan-then-execute-and-decomposition.md) | Plan-Then-Execute और Decomposition | ReAct के विकल्प के रूप में पहले से स्पष्ट planning, उसे कब इस्तेमाल करें, और replanning कैसे संभालें |
| [0017](lessons/0017-self-critique-and-reasoning-models.md) | Self-Critique और Reasoning Models ने क्या बदला | स्पष्ट चरण के रूप में reflection loop, उसकी क़ीमतें, और लंबी आंतरिक reasoning इस पर कैसे असर डालती है कि उसे कब इस्तेमाल करें |
| [0018](lessons/0018-orchestrator-and-worker.md) | Orchestrator और Worker | ऐसा multi-agent system डिज़ाइन करें जिसमें एक agent योजना बनाकर काम सौंपे और workers parallel में चलाएँ |
| [0019](lessons/0019-coordination-cost.md) | Coordination Cost | समझें कि कई agents बनाना एक अच्छी तरह लैस agent से महँगा क्यों है, और यह कैसे तय करें कि parallelism का फ़ायदा उस क़ीमत के लायक है |
| [0020](lessons/0020-mcp-tools-resources-and-prompts.md) | MCP: Tools, Resources और Prompts | Model Context Protocol, agent harnesses के लिए बाहरी tools खोजने और चलाने, data पढ़ने और templates इस्तेमाल करने का मानकीकृत interface |
| [0021](lessons/0021-provider-formats-and-discovery-at-scale.md) | Provider Formats और बड़े पैमाने पर Tool Discovery | MCP और provider-विशिष्ट wire formats अलग परतें कैसे हैं, और हर tool को context में लोड करना कई जुड़े servers पर क्यों नहीं चलता |
| [0022](lessons/0022-sandboxing-and-approval-gates.md) | Sandboxing और Approval Gates | Execution की सीमाएँ और मानवीय चौकियाँ जो model की ग़लतियों से बचाती हैं |
| [0023](lessons/0023-code-execution-as-a-tool.md) | Tool के रूप में Code Execution | कई संकरे अलग-अलग tools की जगह agent को एक sandboxed code-execution tool देना |
| [0024](lessons/0024-screenshots-as-observations.md) | Observations के रूप में Screenshots | Computer-use agents स्क्रीन को structured data की जगह image के रूप में कैसे देखते हैं, और loop की संरचना फिर भी क्यों टिकी रहती है |
| [0025](lessons/0025-grounding-an-action-to-a-coordinate.md) | Action को Coordinate से जोड़ना (Grounding) | दृश्य इरादे को pixel coordinate में बदलना typed tool-call argument से कठिन और नाज़ुक क्यों है |
| [0026](lessons/0026-why-browser-agents-fail-differently.md) | Browser Agents अलग तरह से क्यों फेल होते हैं | Screen चलाने वाले agents ऐसे तरीक़ों से फेल होते हैं जिनसे tool-calling agents नहीं होते, और WebArena ने इन विफलताओं को मापने और पढ़ने के लिए benchmark क्यों बनाया |
| [0027](lessons/0027-loops-and-context-poisoning.md) | Loops और Context Poisoning | Trajectory में दिखने वाले दो failure modes, दोहराव वाले loops और चुपचाप context poisoning, और हर एक को कैसे पहचानें |
| [0028](lessons/0028-cascading-tool-errors.md) | Cascading Tool Errors और Hallucinated Arguments | एक tool error का ग़लत फ़ैसलों तक ले जाना और उलझन में बदल जाना, और ऐसे सही type वाले पर झूठे arguments जिन्हें schemas नहीं पकड़ सकते |
| [0029](lessons/0029-tracing-and-trajectory-replay.md) | Tracing और Trajectory Replay | Agent runs को पकड़ने के लिए vendor-neutral trace conventions का इस्तेमाल, और विफलताओं को चरण-दर-चरण देखने के लिए trajectories को replay करना |
| [0030](lessons/0030-evaluating-an-agent.md) | Agent का Evaluation | Agent की सफलता को outcome स्तर और trajectory स्तर पर मापना, और एक सफल run का मतलब यह क्यों नहीं कि agent भरोसेमंद है |
| [0031](lessons/0031-prompt-injection-and-the-lethal-trifecta.md) | Prompt Injection और Lethal Trifecta | Untrusted content पढ़ने वाले agents exploit करने लायक कैसे बन जाते हैं, और सिर्फ़ prompting उन्हें सुरक्षित क्यों नहीं करती |
| [0032](lessons/0032-least-privilege-and-the-confused-deputy.md) | Least Privilege और Confused Deputy | Agent की क्षमताओं को ऐसे सीमित करें कि prompt injection से भयानक सेंध की जगह सीमित नुक़सान हो |
| [0033](lessons/0033-token-amplification-and-cost.md) | Token Amplification और Cost per Completed Task | Agentic systems एक अकेले prompt से कहीं ज़्यादा tokens प्रति पूरे हुए task पर क्यों खाते हैं, और उसका budget कैसे बनाएँ |
| [0034](lessons/0034-prompt-caching-and-concurrency.md) | Prompt Caching और Concurrency | Caching प्रति task token cost कैसे घटाती है और concurrency throughput कैसे बढ़ाती है, और दोनों को मिला देना budgeting की ग़लती क्यों है |
| [0035](lessons/0035-durability-and-what-frameworks-buy.md) | Durability और Framework क्या देता है | Durable, resumable agent execution एक engineering समस्या के रूप में, frameworks ठोस रूप से क्या देते हैं, और किसी को अपनाने का निर्णय-सिद्धांत |
| [0036](lessons/0036-when-not-to-build-an-agent.md) | Agent कब नहीं बनाना चाहिए | यह तय करने का विवेक कि task को सच में agent चाहिए या नहीं, और जब agent अपनी क़ीमत के लायक न हो तब मना करने का अनुशासन |
| [0037](lessons/0037-reviewing-someone-elses-agent-design.md) | किसी और के Agent Design की समीक्षा | Agent system का व्यवस्थित मूल्यांकन कैसे करें, और विवादित दावे को primary source पर लौटकर कैसे सुलझाएँ |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
