---
title: "संसाधन"
description: "Evals के लिए भरोसेमंद स्रोत"
type: resources
---

# Evals संसाधन

## ज्ञान

- [दस्तावेज़: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
  "क्या यह बेहतर हुआ" जैसे धुँधले सवाल को मापने योग्य सफलता-कसौटियों और held-out eval सेट में बदलने की practitioner walkthrough। इस्तेमाल: किसी framework तक पहुँचने से पहले eval को ख़ुद डिज़ाइन करना।
- [Repo: openai/evals, OpenAI](https://github.com/openai/evals)
  Eval को code के रूप में परिभाषित करने और चलाने का आधिकारिक framework: prompts, grading का तर्क, और पहले से मौजूद evals की registry जिसे worked examples की तरह पढ़ा जा सकता है। इस्तेमाल: custom eval को कैसे संरचित करें और चलाएँ।
- [Repo: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  Model को मानकीकृत benchmarks पर चलाने का वास्तविक मानक harness, जिसके task configs दिखाते हैं कि held-out सेट व्यवहार में कैसे संरचित और score किए जाते हैं। इस्तेमाल: eval को शून्य से बनाने के बजाय मौजूदा benchmark को चलाना या ढालना।
- [पेपर: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
  खुले-सिरे वाले tasks के लिए LLM-as-judge को पेश करता है और मानव पसंद के सामने उसके biases मापता है: position bias, verbosity bias, self-enhancement bias। इस्तेमाल: यह तय करना कि किसी दिए मामले के लिए LLM judge भरोसेमंद है या नहीं, और अगर है तो किस चीज़ का सुधार करना है।
- [दस्तावेज़: Evaluate, Hugging Face](https://huggingface.co/docs/evaluate/index)
  मानक task-specific metrics (BLEU, ROUGE, exact match, F1 और भी) की library, हर एक की परिभाषा और विफलता के तरीक़ों के साथ। इस्तेमाल: metric-बनाम-LLM-judge तुलना का task-specific-metric वाला पक्ष।
- [पेपर: "Time Travel in LLMs: Tracing Data Contamination in Large Language Models", Golchin and Surdeanu, 2023](https://arxiv.org/abs/2308.08493)
  यह परखने का ठोस तरीक़ा कि benchmark का data model के training सेट में रिस गया या नहीं, साथ में instance का बाक़ी हिस्सा अनुमान से बताने की वह technique जो इसे पकड़ती है। इस्तेमाल: held-out सेट की ईमानदारी का बचाव इस ख़ास दावे के विरुद्ध करना कि "model ने बस इसे रट लिया है"।
- [पेपर: "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models" (BIG-bench), Srivastava et al., 2022](https://arxiv.org/abs/2206.04615)
  Canary-string परंपरा लाता है (benchmark data में डाला गया एक अनोखा चिह्न-वाक्यांश, जो crawlers से उसे training corpora से बाहर रखने को कहता है), जो benchmark की अपनी release के लिए contamination-रोधी बचाव की तकनीक है। इस्तेमाल: custom eval सेट को शुरू से ही contamination का सामना करने लायक डिज़ाइन करना, बाद में उसे पकड़ने के बजाय।
- [पेपर: "Evaluating Large Language Models Trained on Code" (Codex), Chen et al., 2021](https://arxiv.org/abs/2107.03374)
  Functional correctness (generate किए code को test cases पर चलाना, text की तुलना करने के बजाय) और unbiased pass@k estimator लाता है, उस combinatorial सूत्र के साथ जो k completions को सीधे दोबारा sample करने के ऊँचे variance से बचाता है। इस्तेमाल: code generation का evaluation, और जहाँ भी कोई task चलाया जा सकता हो वहाँ text की समानता के बजाय व्यवहार जाँचने का सामान्य सिद्धांत।

- [लेख: "Cohen's kappa", Wikipedia](https://en.wikipedia.org/wiki/Cohen%27s_kappa)
  संयोग-सुधारी inter-rater agreement statistic: उसका सूत्र, kappa 0 का मतलब संयोग से बेहतर नहीं क्यों है, और दुर्लभ category पर सहमति को कम आँकने की उसकी जानी-मानी प्रवृत्ति। इस्तेमाल: कच्चे agreement प्रतिशत को आँख से देखने के बजाय मानव raters की सहमति को सटीक मापना।
- [लेख: "Inter-rater reliability", Wikipedia](https://en.wikipedia.org/wiki/Inter-rater_reliability)
  समझाता है कि कच्ची joint-probability सहमति भ्रामक क्यों है (संयोग से फूली हुई, कम categories के साथ और बुरी), और Krippendorff का alpha किसी भी संख्या के raters और माप के किसी भी स्तर तक संयोग-सुधारी सहमति का सामान्यीकरण कैसे है। इस्तेमाल: दो से ज़्यादा raters या गैर-categorical ratings के लिए सही agreement statistic चुनना।
- [पेपर: "HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal", Mazeika et al., 2024](https://arxiv.org/abs/2402.04249)
  Automated red-teaming तरीक़ों को models और बचावों के विरुद्ध, बड़े पैमाने पर और तुलनीय ढंग से परखने का मानकीकृत framework लाता है, जहाँ क्षेत्र के पास पहले ऐसा कुछ नहीं था। इस्तेमाल: attack success rate एक metric के रूप में, और attack-generation के तरीक़े तथा उसे कठोरता से परखने के तरीक़े के बीच का अंतर।
- [पेपर: "XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models", Röttger et al., 2023](https://arxiv.org/abs/2308.01263)
  सुरक्षित prompts का test suite, जो असुरक्षित जैसे दिखने के लिए लिखे गए हैं, ख़ास तौर पर over-refusal को उजागर करने के लिए। इस्तेमाल: harmlessness (असुरक्षित prompts को मना करो) और helpfulness (सुरक्षित को मना मत करो) के बीच का सटीक तनाव, और यह मापने का ठोस तरीक़ा कि कोई model उस trade-off पर बुरी जगह उतरा है।
- [पेपर: "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Yao et al., 2024](https://arxiv.org/abs/2406.12045)
  Agents को बातचीत के अंत की database अवस्था की तुलना annotate की गई लक्ष्य-अवस्था से करके परखता है, और एक ही task के दोहराए गए trials में agent की विश्वसनीयता मापने के लिए `pass^k` लाता है। इस्तेमाल: task success कदम-दर-कदम trajectory matching से बेहतर क्यों है, और `pass^k` तथा पाठ 4 के `pass@k` के बीच का सटीक, आसानी से गड़बड़ाने वाला अंतर।
- [पेपर: "AgentBench: Evaluating LLMs as Agents", Liu et al., 2023](https://arxiv.org/abs/2308.03688)
  8 अलग interactive environments पर बहु-आयामी benchmark, जो LLM की reasoning और agent के रूप में निर्णय लेने की क्षमता परखता है, और ख़ास तौर पर agentic settings में शीर्ष models और छोटे models के बीच बड़ा फ़ासला पाता है। इस्तेमाल: इस बात का प्रमाण कि agentic क्षमता मापने की अलग चीज़ है, जो single-turn benchmark प्रदर्शन से नहीं निकलती।
- [पेपर: "Ragas: Automated Evaluation of Retrieval Augmented Generation", Es et al., 2023](https://arxiv.org/abs/2309.15217)
  Reference-free framework जो RAG system के retrieval-गुणवत्ता, faithfulness और generation-गुणवत्ता आयामों को स्वतंत्र metrics में अलग करता है। इस्तेमाल: मानव-लिखित gold उत्तर के बिना faithfulness score निकालना, और retrieval विफलता तथा generation विफलता को अलग सवालों के रूप में diagnose करने लायक रखना।
- [पेपर: "Enabling Large Language Models to Generate Text with Citations" (ALCE), Gao et al., 2023](https://arxiv.org/abs/2305.14627)
  मानव निर्णय से correlated automatic citation-quality metrics लाता है, और यह निष्कर्ष कि एक test सेट पर शीर्ष systems भी अपने लगभग आधे दावों के लिए पूरा citation समर्थन नहीं दे पाते। इस्तेमाल: citation correctness को faithfulness से ज़्यादा सख़्त, अलग जाँच के रूप में समझना।
- [पेपर: "Seven Rules of Thumb for Web Site Experimenters", Kohavi et al., 2014](https://exp-platform.com/Documents/2014%20experimentersRulesOfThumb.pdf)
  Online controlled experiments चलाने पर Kohavi और सह-लेखकों का practitioner मार्गदर्शन, जिसमें OEC की अवधारणा (हिलाने लायक और असली नतीजे से कारण के रूप में जुड़ी) और guardrail metrics शामिल हैं। इस्तेमाल: आसानी से हिलने वाली पर कारणहीन metric के बजाय बचाव-योग्य OEC चुनना, और साथ में guardrail metric क्यों ट्रैक करनी पड़ती है।
- [गाइड: "Rules of Machine Learning", Zinkevich, Google](https://developers.google.com/machine-learning/guides/rules-of-ml)
  Google का आंतरिक ML इंजीनियरिंग मार्गदर्शन, जिसमें Rule #37 (training/serving skew को एक नहीं बल्कि कई अलग तुलनाओं के रूप में मापना) और Rule #8 (freshness की ज़रूरतें) शामिल हैं। इस्तेमाल: offline/online फ़ासले के कई संभावित कारणों में से, यानी सामान्य variance, drift या इंजीनियरिंग की ग़लती, असल में कौन-सा लागू होता है, और हर एक को अलग सुधार क्यों चाहिए।
- [पेपर: "The Tail at Scale", Dean and Barroso, 2013](https://www.barroso.org/publications/TheTailAtScale.pdf)
  इसका मानक स्पष्टीकरण कि बड़े पैमाने पर असली दुनिया की responsiveness औसत latency से नहीं बल्कि tail latency से क्यों तय होती है, ख़ास तौर पर जब request कई backend calls में फैल जाए। इस्तेमाल: latency regression को ख़ारिज करने से पहले go/no-go फ़ैसले को सिर्फ़ औसत नहीं बल्कि percentile (p95/p99) क्यों चाहिए।
- [पेपर: "The Leaderboard Illusion", Singh et al., 2025](https://arxiv.org/abs/2504.20879)
  Chatbot Arena पर selective disclosure दर्ज करता है: कई model variants का निजी pre-release परीक्षण (अकेले Llama 4 के लिए 27) और मुट्ठी-भर closed-model providers के पक्ष में बड़ी, असमान data पहुँच। इस्तेमाल: इसका ठोस, ताज़ा, अच्छी तरह दर्ज उदाहरण कि leaderboard rank अपने-आप में तटस्थ, भरोसेमंद माप क्यों नहीं है।
- [लेख: "Does Style Matter?", LMArena](https://lmarena.ai/blog/style-control)
  Arena का अपना विश्लेषण, जो दिखाता है कि response की लंबाई और markdown formatting को नियंत्रित करते ही rankings में ठोस बदलाव आते हैं। इस्तेमाल: पुष्टि करना कि पाठ 6 की verbosity-bias की क्रियाविधि पूरे leaderboard के पैमाने पर, एक अकेले LLM judge के बजाय मानव raters के साथ, ठीक उसी तरह काम करती है।

## कमियाँ

- Eval scores के फ़र्क़ के लिए statistical significance testing पर अभी कोई समर्पित स्रोत नहीं है (अनुपात की standard error, McNemar जैसे paired significance tests)। मिशन को चरण 5 के "क्या यह फ़र्क़ असली है या noise" वाले सवाल के लिए यह चाहिए; पाठ 9 इसे किसी एक cite किए गए स्रोत के बजाय स्थिर, मानक सांख्यिकीय विधि से सिखाता है, और जब कोई अच्छा practitioner-स्तर का स्रोत मिल जाए तब यह कमी भर जानी चाहिए।
