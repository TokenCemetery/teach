---
title: संसाधन
description: "Prompting के लिए भरोसेमंद स्रोत"
type: resources
---

# Prompting संसाधन

## ज्ञान

- [दस्तावेज़: "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
  एक vendor की समेकित गाइड: स्पष्ट instructions, examples, XML tags, roles, thinking, लंबा context और output format, पहले-और-बाद के prompts के साथ। इस्तेमाल: चरण 2 से 6 का practitioner आधार, एक vendor के दस्तावेज़ी व्यवहार के रूप में पढ़ें।
- [दस्तावेज़: "Prompt engineering overview", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
  दोहराने से पहले सफलता के मानदंड और tests तय करने की सलाह, और एक छोटा नोट कि हर विफल eval को prompting से ठीक करना सबसे अच्छा नहीं होता। इस्तेमाल: पहले मापने की आदत।
- [दस्तावेज़: "Long context prompting", Prompting best practices का एक खंड, Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#long-context-prompting)
  लंबे documents को query से पहले रखना, हर एक को उसके metadata के साथ tags में लपेटना, और पहले प्रासंगिक quotes माँगना। इस्तेमाल: लंबे input का layout बनाना।
- [दस्तावेज़: "Structured outputs", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
  Provider का फ़ीचर जो response पर JSON schema लागू करता है, इस बात के साथ दर्ज कि अकेला prompt क्या गारंटी नहीं देता। इस्तेमाल: structure माँगने और उसे लागू करने के बीच की सीमा।
- [दस्तावेज़: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
  Cache किया हुआ prefix कैसे match होता है, क्या उसे अमान्य करता है, और hit के लिए prompt को कौन-सा क्रम रखना पड़ता है। इस्तेमाल: prompt को ऐसे सजाना कि उसके स्थिर हिस्से cache हों।
- [दस्तावेज़: "Model IDs and versioning", Claude Platform Docs](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions)
  एक vendor तय snapshots और बदलते aliases को कैसे नाम देता है, और हर ID का अपना retirement schedule होता है। इस्तेमाल: prompt को उस model से बाँधना जिस पर उसे परखा गया था।
- [दस्तावेज़: "Extended thinking", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
  Thinking चरण की API mechanics: token budget, उसका न्यूनतम मान, और thinking output limit में कैसे गिनी जाती है। इस्तेमाल: reasoning model को prompt करने के पीछे के budget के तथ्य; शब्दों की सलाह best-practices गाइड में है।
- [दस्तावेज़: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
  "क्या यह prompt बेहतर है" को सफलता के मानदंडों और eval के डिज़ाइन में बदलना, edge cases और baseline से तुलना समेत। इस्तेमाल: कुछ भी बदलने से पहले तय करना कि prompt के बदलाव को किस पर परखना है।
- [दस्तावेज़: "Mitigate jailbreaks and prompt injections", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks)
  Prompt-स्तर और system-स्तर के उपाय, जिनमें input की छानबीन और model जो कर सकता है उसे सीमित करना शामिल है। इस्तेमाल: prompt का लेखक कौन-से बचावों का मालिक है।
- [दस्तावेज़: "Prompt design strategies", Gemini API, Google](https://ai.google.dev/gemini-api/docs/prompting-strategies)
  दूसरे vendor की गाइड: instructions, few-shot examples, prefixes और task को तोड़ना। इस्तेमाल: जाँचना कि कोई technique सामान्य है या किसी एक vendor का व्यवहार।
- [दस्तावेज़: "Chat templates", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
  Role-tagged messages की सूची उस एक token sequence में कैसे render होती है जिस पर model को train किया गया था, असली template output के साथ। इस्तेमाल: model असल में क्या देखता है।
- [Repo: "Prompt engineering interactive tutorial", Anthropic](https://github.com/anthropics/prompt-eng-interactive-tutorial)
  Notebook अभ्यास जो roles, data को instructions से अलग करना, examples, step-by-step reasoning और hallucination से बचना कवर करते हैं। इस्तेमाल: चरण 1 से 4 का अभ्यास।
- [पेपर: "The Prompt Report: A Systematic Survey of Prompting Techniques", Schulhoff et al., 2024](https://arxiv.org/abs/2406.06608)
  Prompting techniques का survey और वर्गीकरण, एक जैसी शब्दावली के साथ। इस्तेमाल: जो technique बाहर मिले उसे सही जगह रखना, और तय करना कि किसी शब्द का मतलब क्या है।
- [पेपर: "Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design", Sclar et al., 2023](https://arxiv.org/abs/2310.11324)
  दिखाता है कि अर्थ न बदलने वाले formatting बदलाव (separators, casing, spacing) few-shot accuracy को बड़े अंतर से हिला देते हैं। इस्तेमाल: prompt edit एक परखने लायक दावा क्यों है, शैली की पसंद क्यों नहीं।
- [पेपर: "Rethinking the Role of Demonstrations", Min et al., 2022](https://arxiv.org/abs/2202.12837)
  पाता है कि demonstration labels को random बदलने से बहुत कम नुक़सान होता है, जबकि format, label space और input distribution मायने रखते हैं। इस्तेमाल: few-shot examples असल में क्या सिखाते हैं।
- [पेपर: "Calibrate Before Use: Improving Few-Shot Performance of Language Models", Zhao et al., 2021](https://arxiv.org/abs/2102.09690)
  Few-shot prompts में majority-label, recency और common-token bias को नाम देता है और contextual calibration सुझाता है। इस्तेमाल: examples का सेट कौन-से biases लाता है।
- [पेपर: "Fantastically Ordered Prompts and Where to Find Them", Lu et al., 2021](https://arxiv.org/abs/2104.08786)
  दिखाता है कि उन्हीं few-shot examples का क्रम accuracy को state of the art के क़रीब से लगभग संयोग के स्तर तक झुला देता है। इस्तेमाल: examples का क्रम नियंत्रित करने लायक variable क्यों है।
- [पेपर: "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", Wei et al., 2022](https://arxiv.org/abs/2201.11903)
  Few-shot chain-of-thought का मूल नतीजा, और यह खोज कि फ़ायदा सिर्फ़ पर्याप्त model scale पर दिखता है। इस्तेमाल: reasoning माँगना कब मदद करता है।
- [पेपर: "Large Language Models are Zero-Shot Reasoners", Kojima et al., 2022](https://arxiv.org/abs/2205.11916)
  Zero-shot chain-of-thought: एक ही trigger वाक्यांश बिना examples के reasoning करवा देता है। इस्तेमाल: हाथ से लिखे demonstrations के बिना reasoning।
- [पेपर: "Self-Consistency Improves Chain of Thought Reasoning in Language Models", Wang et al., 2022](https://arxiv.org/abs/2203.11171)
  कई reasoning paths sample करना और बहुमत का उत्तर लेना। इस्तेमाल: ऐसे task पर tokens के बदले accuracy ख़रीदना जिसका एक जाँचने लायक उत्तर हो।
- [पेपर: "Language Models Don't Always Say What They Think", Turpin et al., 2023](https://arxiv.org/abs/2305.04388)
  दिखाता है कि model की chain-of-thought उस पक्षपाती feature को छोड़ देती है जिसने असल में उसका उत्तर तय किया था। इस्तेमाल: लिखी हुई reasoning एक faithful व्याख्या क्यों नहीं है।
- [पेपर: "Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models", Tam et al., 2024](https://arxiv.org/abs/2408.02442)
  सख़्त output-format constraints में reasoning की accuracy गिरते हुए मापता है। इस्तेमाल: format थोपने की क़ीमत, और fields को कैसे क्रम दें।
- [पेपर: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
  U-आकार का वक्र: लंबे context की शुरुआत और अंत की जानकारी बीच की जानकारी से बेहतर इस्तेमाल होती है। इस्तेमाल: तय करना कि documents और सवाल कहाँ जाएँ।
- [पेपर: "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions", Wallace et al., 2024](https://arxiv.org/abs/2404.13208)
  System, user और tool-output के privilege स्तर तय करता है और model को टकराव पर ऊँचे स्तर वाले को मानना सिखाता है। इस्तेमाल: instruction की जगह उसका वज़न क्यों बदल देती है।
- [पेपर: "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models", Zheng et al., 2023](https://arxiv.org/abs/2311.10054)
  चार model families और 2,410 तथ्यात्मक सवालों पर system prompts में 162 personas परखता है और बिना persona की तुलना में कोई सुधार नहीं पाता, persona का असर काफ़ी हद तक random रहता है। इस्तेमाल: role-prompting के विवाद का फ़ैसला data से करना।
- [पेपर: "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection", Greshake et al., 2023](https://arxiv.org/abs/2302.12173)
  Retrieve किए गए content के ज़रिए indirect prompt injection को पेश करता है और असली applications पर उसे दिखाता है। इस्तेमाल: हमलावर उस prompt तक कैसे पहुँचता है जिसमें वह कभी कुछ टाइप नहीं करता।
- [पेपर: "Fine-Tuning or Retrieval? Comparing Knowledge Injection in LLMs", Ovadia et al., 2023](https://arxiv.org/abs/2312.05934)
  ज्ञान जोड़ने के लिए unsupervised fine-tuning और retrieval की तुलना करता है और retrieval को लगातार बेहतर पाता है, training में देखे गए ज्ञान और नए तथ्यों, दोनों के लिए। इस्तेमाल: prompt, RAG या fine-tune का फ़ैसला।
- [लेख: "LLM01:2025 Prompt Injection", OWASP Gen AI Security Project](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
  उद्योग की जोखिम प्रविष्टि: direct और indirect injection, असर, और उपाय, इस क्रम में कि वे कहाँ बैठते हैं। इस्तेमाल: साझा शब्दावली और उपायों की सूची।
- [लेख: "The lethal trifecta for AI agents", Simon Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
  Private data, untrusted content और data बाहर भेजने का रास्ता, तीनों मिलकर injection को exploit करने लायक बनाते हैं, और एक पाया हटाना ही बचाव है। इस्तेमाल: असली बचाव prompt के बाहर क्यों रहता है।
- [लेख: "Your AI Product Needs Evals", Hamel Husain](https://hamel.dev/blog/posts/evals/)
  Unit-test जैसी जाँचों और log किए गए असली traces को prompt पर दोहराने का आधार बनाने के पक्ष में एक practitioner का तर्क। इस्तेमाल: असली विफलताओं से regression set बनाना।

## कमियाँ

- OpenAI की prompt engineering, reasoning और structured-output गाइड तीसरे vendor का नज़रिया होतीं, लेकिन `platform.openai.com` और `developers.openai.com` का हर पेज scripted और browser दोनों जाँचों पर 403 से जवाब देता रहा, इसलिए किसी के खुलने की पुष्टि नहीं हो सकी। जब कोई पुष्ट हो सके तब इन्हें जोड़ें।
- कोई peer-reviewed स्रोत prompt versioning या template के अभ्यास को सीधे नहीं मापता। पाठ 15 और 16 इसे vendor दस्तावेज़ों और सामान्य software-engineering अभ्यास से सिखाते हैं, और यह बात कहते हैं।
