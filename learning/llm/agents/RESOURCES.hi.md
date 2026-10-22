---
title: संसाधन
description: "LLM agents के लिए भरोसेमंद स्रोत"
type: resources
---

# LLM Agents संसाधन

## ज्ञान

- [लेख: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
  Workflow बनाम agent का वह अंतर खींचता है जिस पर यह track टिका है, फिर आम जोड़ने लायक patterns (prompt chaining, routing, parallelisation, orchestrator और workers, evaluator और optimiser) के नाम बताता है, और काम करने वाले सबसे सरल pattern की वकालत करता है। इस्तेमाल: चरण 1 की शब्दावली, और चरण 16 में agent न बनाने का तर्क।
- [गाइड: "A Practical Guide to Building Agents", OpenAI](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
  उसी सामग्री का दूसरे vendor का ढाँचा, जिसमें शामिल हैं: कब task को agent चाहिए, tool की श्रेणियाँ, एक बनाम कई agents के लिए orchestration, और guardrails। इस्तेमाल: जाँचना कि चरण 1 या चरण 8 का कोई दावा agents के बारे में है, किसी एक provider के product के बारे में नहीं।
- [लेख: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
  Tool के नाम, विवरण, parameter schema और return shape को API अनुबंध की जगह prompt सतह मानता है, जिसमें यह भी है कि tool का output context budget कैसे खाता है। इस्तेमाल: चरण 4, और यह कि REST endpoint की तरह बना tool बदतर tool क्यों होता है।
- [लेख: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  Context window को सीमित budget मानकर सँवारने की वकालत करता है, और compaction, बाहरी memory में note-taking और context isolation के रूप में sub-agents को कवर करता है। इस्तेमाल: चरण 5 और 6।
- [पेपर: "ReAct: Synergizing Reasoning and Acting in Language Models", Yao et al., 2022](https://arxiv.org/abs/2210.03629)
  Reasoning traces को tool actions के साथ एक ही loop में जोड़ने का तरीक़ा पेश करता है, पूरी योजना पहले से बनाने या बिना reasoning के action लेने के बजाय। इस्तेमाल: चरण 7, और उस pattern का नाम जिसे ज़्यादातर agent loops अब भी लागू करते हैं।
- [पेपर: "Reflexion: Language Agents with Verbal Reinforcement Learning", Shinn et al., 2023](https://arxiv.org/abs/2303.11366)
  Self-critique को loop के स्पष्ट चरण के रूप में पेश करता है: agent नाकाम प्रयास पर प्राकृतिक भाषा में विचार करता है और उस विचार को retry में ले जाता है। इस्तेमाल: चरण 7 की reflection सामग्री, और self-critique की tokens में क्या क़ीमत है।
- [पेपर: "Toolformer: Language Models Can Teach Themselves to Use Tools", Schick et al., 2023](https://arxiv.org/abs/2302.04761)
  दिखाता है कि tool use को prompt करने के बजाय model ख़ुद सीखता है, जो इस track और `llm/finetuning` के बीच की सीमा है। इस्तेमाल: चरण 2 में यह समझाना कि model tool call क्यों भेजता है।
- [दस्तावेज़: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
  Tool-call wire format का एक provider का अपना विवरण: tool definition का JSON schema, tool-call request और उसका result messages के रूप में कैसे दर्शाए जाते हैं, और parallel tool calls। इस्तेमाल: चरण 2 का capture किया हुआ request और response जोड़ा, जिसे नीचे दी OpenAI गाइड के साथ अंतर के रूप में पढ़ें।
- [गाइड: "Function calling", OpenAI](https://developers.openai.com/api/docs/guides/function-calling)
  उसी mechanic का दूसरे provider का wire format, जिसमें एक अकेली function call से सामान्य tool-calling convention की ओर बदलाव भी शामिल है। इस्तेमाल: चरण 2, उस दूसरे provider के रूप में जिसका format सिर्फ़ पहले से अंतर के तौर पर दिखता है।
- [विनिर्देश: Model Context Protocol](https://modelcontextprotocol.io/specification)
  MCP का मानक विनिर्देश: tools, resources, prompts, sampling, transports और server lifecycle। इस्तेमाल: चरण 9, और MCP के किसी भी दावे को client के दस्तावेज़ों के बजाय स्रोत से सुलझाना।
- [लेख: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
  तर्क देता है कि tools को context में लोड की गई अलग-अलग tool definitions की जगह ऐसे code के रूप में पेश करना जिसके विरुद्ध agent लिखता है, बड़े tool set की क़ीमत बदल देता है। इस्तेमाल: चरण 9 की बड़े पैमाने पर tool discovery की समस्या और चरण 10 की code-execution सामग्री।
- [लेख: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
  Orchestrator और worker system का production वृत्तांत, जिसमें एक agent के मुक़ाबले token cost का गुणक और यह शामिल है कि coordination असल में कहाँ टूटा। इस्तेमाल: चरण 8 का तर्क कि multi-agent एक नापी हुई क़ीमत पर parallelism और context isolation देता है।
- [लेख: "Don't Build Multi-Agents", Cognition](https://cognition.ai/blog/dont-build-multi-agents)
  विरोधी पक्ष, जो तर्क देता है कि काम को agents में बाँटने से context टूटता है और आपस में टकराने वाले फ़ैसले बनते हैं। इस्तेमाल: चरण 8, ऊपर के Anthropic वृत्तांत की जगह नहीं, उसके साथ पढ़ें।
- [लेख: "The Lethal Trifecta for AI Agents", Simon Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
  उस मेल का नाम बताता है जो agent को exploit करने लायक बनाता है: private data तक पहुँच, untrusted content का सामना, और बाहर संवाद करने की क्षमता। इस्तेमाल: चरण 14 का केंद्रीय ढाँचा, और यह कि prompt instructions बचाव क्यों नहीं हैं।
- [संदर्भ: "OWASP Top 10 for LLM Applications", OWASP GenAI Security Project](https://genai.owasp.org/llm-top-10/)
  LLM application के जोखिमों की सर्वसम्मत सूची, जिसमें prompt injection, excessive agency और supply chain exposure शामिल हैं, हर एक के उपायों के साथ। इस्तेमाल: चरण 14 की checklist, और वह शब्दावली जो security reviewer पहले से इस्तेमाल करेगा।
- [विनिर्देश: "Semantic Conventions for Generative AI", OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
  Agent run से निकलने वाले spans और attributes के लिए vendor-neutral conventions, जिनकी वजह से एक tracing backend का trajectory view दूसरे में पढ़ा जा सकता है। इस्तेमाल: चरण 12, इस सवाल के provider-neutral जवाब के रूप में कि trace में क्या होना चाहिए।
- [पेपर: "tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Yao et al., 2024](https://arxiv.org/abs/2406.12045)
  Simulated user और domain policy के विरुद्ध multi-turn tool use पर agents को परखता है, और एक trial की सफलता की जगह बार-बार trials में विश्वसनीयता का माप पेश करता है। इस्तेमाल: चरण 13 का अंतर: एक बार सफल होना बनाम भरोसे से सफल होना।
- [पेपर: "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?", Jimenez et al., 2023](https://arxiv.org/abs/2310.06770)
  असली repository issues पर agents को परखता है, जिसमें project के अपने tests outcome की जाँच हैं। इस्तेमाल: चरण 13 में outcome से ग्रेड होने वाले benchmark का उदाहरण, जहाँ trajectory पर कोई बंदिश नहीं।
- [दस्तावेज़: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
  Computer-use agent का screenshot-और-action loop बताता है: observation tool result नहीं, एक screenshot है, और action function argument नहीं, एक screen coordinate या key press है। इस्तेमाल: चरण 11 की action को coordinate से जोड़ने (grounding) की सामग्री, और यह कि इस loop को tool-calling वाले loop से अलग विश्वसनीयता की कहानी क्यों चाहिए।
- [पेपर: "WebArena: A Realistic Web Environment for Building Autonomous Agents", Zhou et al., 2023](https://arxiv.org/abs/2307.13854)
  Functional correctness जाँचों वाला self-hosted web environment, उन agents के लिए बना जो browser के ज़रिए काम करते हैं। इस्तेमाल: चरण 11, उस मानक के रूप में जिसके विरुद्ध browser-agent की विश्वसनीयता के दावे किए जाते हैं।
- [पेपर: "GAIA: A Benchmark for General AI Assistants", Mialon et al., 2023](https://arxiv.org/abs/2311.12983)
  ऐसे सवाल जो इंसान के लिए आसान और agent के लिए कठिन हैं, जिनमें multi-step tool use चाहिए और एक ही असंदिग्ध उत्तर है। इस्तेमाल: चरण 13, उन benchmarks के प्रतिकार के रूप में जिन्हें model बिना कार्रवाई किए पास कर सकता है।
- [दस्तावेज़: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
  बार-बार की cost और latency घटाने के लिए prompt prefix को cache करना, जिसमें यह शामिल है कि agent की स्थिर tool definitions और system prompt ठीक वही prefix क्यों हैं जिसे cache करना चाहिए, और क्या चुपचाप cache को अमान्य कर देता है। इस्तेमाल: चरण 15 की token-amplification और cost सामग्री।

## कमियाँ

- Tool-calling wire formats के लिए कोई provider-neutral संदर्भ मौजूद नहीं है। हर provider सिर्फ़ अपना दस्तावेज़ बनाता है, इसलिए इस track में दिखाए capture किए गए request और response जोड़े provider के दस्तावेज़ों से लेकर हाथ से मिलाने पड़ते हैं।
- Durable और resumable agent execution ज़्यादातर अलग-अलग frameworks के भीतर ही दर्ज है, जो न provider-neutral है और न इतना स्थिर कि अभी सूचीबद्ध किया जाए। चरण 15 को ऐसा स्रोत चाहिए जो इनमें से कुछ न हो।
- Computer use और browser agents पर लिखे किसी भी लेख से तेज़ चलते हैं। सूचीबद्ध benchmark पेपर बताते हैं कि किसी को कैसे परखें, यह नहीं कि आज एक कैसे बनाएँ, इसलिए चरण 11 रूपरेखा का सबसे कम स्रोतों वाला हिस्सा है।
- अब तक सूचीबद्ध कुछ भी runs के पार agent memory को डिज़ाइन किए गए system के रूप में कवर नहीं करता, product फ़ीचर के रूप में नहीं। चरण 6 को ऐसा एक चाहिए।
