---
title: "Evals"
description: "साबित करें कि model में बदलाव सचमुच काम आया: eval बनाएँ, data को ईमानदारी से held out रखें, और संख्या का contamination के विरुद्ध बचाव करें"
type: topic
---

# सीखना: Evals

ऐसा eval बना सकें जो उस regression को पकड़ ले जिसे vibe check चूक जाता, और उसके सहारे model में किए गए बदलाव (fine-tune, prompt में बदलाव, RAG में बदलाव) पर ऐसा go/no-go फ़ैसला ले सकें जिसका बचाव किसी एहसास के बजाय संख्या से किया जा सके।

**नवीनतम पाठ:** [19. Eval Report की समीक्षा](lessons/0019-reviewing-an-eval-report.md)

## सफलता कैसी दिखती है

- किसी दिए model बदलाव के लिए ऐसा held-out eval सेट डिज़ाइन करें जो contamination का सामना कर सके और उस regression को पकड़ ले जिसे सरसरी पढ़ाई चूक जाती।
- उस eval से बदलाव ship करने पर go/no-go फ़ैसला लें और उसका बचाव करें, यह बताते हुए कि कौन-सी संख्या है और वह भरोसेमंद क्यों है।
- किसी दिए मामले के लिए LLM-as-judge तरीक़े की तुलना task-specific metrics से करें, और default के आधार पर नहीं बल्कि गुण-दोष के आधार पर उनमें से चुनें।
- किसी और की eval report या harness की समीक्षा करें और ठीक-ठीक बताएँ कि उसकी संख्या को क्या अविश्वसनीय बनाएगा (held-out न किया गया सेट, uncalibrated judge, variance अनुमान के बिना एक अकेला run, task-specific फ़ैसले की जगह खड़ी leaderboard rank), यह कहने के बजाय कि वह कमज़ोर लगती है।

## सीमाएँ

- कोई domain प्रतिबंध नहीं: fine-tunes, prompt में बदलाव और RAG में बदलाव, तीनों का evaluation शामिल है, क्योंकि तीनों पर वही eval अनुशासन लागू होता है।
- कोई तय stack या पूर्व अनुभव की धारणा नहीं।

## दायरे से बाहर

- Variant को परखना, held-out डिज़ाइन, metrics और regression suite, जैसा कि एक fine-tuning arc के भीतर सिखाया गया है: [`llm/finetuning`](../../llm/finetuning/) देखें (पाठ 0020-0024), जो ख़ास तौर पर fine-tuning के अधीन है। यह workspace evaluation को विषय के रूप में रखता है और दोहराने के बजाय वापस link करता है।
- Model को quantize करना और यह परखना कि quantization की क़ीमत क्या रही: [`llm/quantization`](../../llm/quantization/) देखें। वह track quantization से हुआ नुक़सान मापने के लिए eval इस्तेमाल करता है; यह वाला सिखाता है कि eval कैसे बनता है।
- जिस prompt को परखा जा रहा है उसे लिखना और उसकी versioning: [`llm/prompting`](../../llm/prompting/) देखें। वह track prompt में बदलाव मापने के लिए eval इस्तेमाल करता है; यह वाला सिखाता है कि eval कैसे बनता है।
- छोटे model को distill करना और यह मापना कि उसने अपने teacher के मुक़ाबले क्या खोया: [`llm/distillation`](../../llm/distillation/) देखें। वह track student की teacher से तुलना के लिए eval इस्तेमाल करता है; यह वाला सिखाता है कि eval कैसे बनता है।

## पूरी रूपरेखा

तेरह चरण, भरोसेमंद eval से लेकर ऐसे बचाव-योग्य go/no-go फ़ैसले तक जो इंसानों, safety, agents, RAG, production, cost और public leaderboard के खिंचाव का हिसाब रखता है, और अंत में किसी और के eval की समीक्षा करने और उसे साझा infrastructure के रूप में ईमानदारी से बनाए रखने का विवेक। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. Held-out data और contamination | 0001 से 0002 | Train/test split का अनुशासन, contamination की पहचान और उसके स्रोत | ऐसा held-out सेट डिज़ाइन कर सकें जो contamination का सामना करे |
| 2. Task-specific metrics | 0003 से 0004 | Exact match, F1, BLEU/ROUGE, code-execution metrics, हर task के लिए चुनाव | बताए गए task के लिए metric चुन सकें और उसे सही ठहरा सकें |
| 3. LLM-as-judge | 0005 से 0006 | Judge-prompt डिज़ाइन, calibration, position और verbosity bias, इंसानों से सहमति | Judge prompt बना सकें और उसकी विफलताओं के नाम बता सकें |
| 4. Harness बनाना | 0007 से 0008 | Eval frameworks, reproducible runs, डिज़ाइन को संख्या में बदलना | ऐसा चलने लायक eval harness हो जो भरोसेमंद संख्या दे |
| 5. Go/no-go फ़ैसला | 0009 से 0010 | Statistical significance बनाम noise, regression thresholds, फ़ैसला बताना | ship/no-ship फ़ैसले का बचाव संख्या से कर सकें और बता सकें कि वह भरोसेमंद क्यों है |
| 6. Method के रूप में human evaluation | 0011 | Annotation guidelines, review के लिए sampling, Cohen's kappa, और मानव label की क़ीमत | Inter-rater agreement को सटीक रूप से माप सकें और कम मान का कारण ढूँढ सकें |
| 7. Safety और red-teaming evaluation | 0012 | Red-teaming, jailbreaks और attack success rate, over-refusal और XSTest | Refusal-rate और over-refusal, दोनों metrics बता सकें, और समझा सकें कि अकेली कोई भी safety eval क्यों नहीं है |
| 8. Agents और tool use का evaluation | 0013 | Trajectories, task success बनाम step accuracy, `pass^k` विश्वसनीयता | समझा सकें कि task success step matching से बेहतर क्यों है, और एक trial की सफलता दोहराए गए trials की विश्वसनीयता क्यों नहीं है |
| 9. RAG-specific evaluation | 0014 | Faithfulness/groundedness, citation correctness, retrieval की विफलता को generation की विफलता से अलग करना | Faithfulness और citation correctness को अलग-अलग माप सकें, और पहचान सकें कि RAG pipeline का कौन-सा पक्ष असल में विफल हुआ |
| 10. Online evaluation | 0015 से 0016 | A/B tests, OEC और guardrail metrics, production telemetry, drift, training-serving skew | Guardrail metric के साथ बचाव-योग्य OEC चुन सकें, और offline/online फ़र्क़ को सही तरह variance, drift या इंजीनियरिंग की ग़लती पर डाल सकें |
| 11. Eval के आयामों के रूप में cost और latency | 0017 | औसत बनाम tail latency, प्रति-request/token cost, दोनों को go/no-go फ़ैसले में मिलाना | ऐसे go/no-go फ़ैसले का बचाव कर सकें जो गुणवत्ता, tail latency और cost को साथ तौलता है, सिर्फ़ गुणवत्ता को नहीं |
| 12. Public benchmarks | 0018 | Static-benchmark contamination/saturation, arena-शैली का selective disclosure, leaderboard के पैमाने पर style bias | समझा सकें कि leaderboard rank OEC की कसौटी पर क्यों विफल होती है और task-specific go/no-go फ़ैसले की जगह क्यों नहीं ले सकती |
| 13. विवेक | 0019 | Eval reports की समीक्षा, विवादित दावों को primary स्रोतों से सुलझाना, ऐसे eval suite को बनाए रखना जिस पर दूसरे निर्भर हैं | किसी और के eval की समीक्षा करने और उसकी संख्या का बचाव करने या उसे अविश्वसनीय बनाने वाली बात का नाम बताने के लिए भरोसेमंद, और eval suite को साझा infrastructure के रूप में बिना दूसरों के gates तोड़े बनाए रखने के लिए भी |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-held-out-and-contamination.md) | Held-out Data और Contamination | Eval की संख्या उतनी ही भरोसेमंद क्यों है जितना वह जो model ने कभी नहीं देखा |
| [0002](lessons/0002-designing-contamination-resistance.md) | Contamination-Resistance को Design करना | Custom eval सेट में contamination को बाद में सिर्फ़ पकड़ने के बजाय शुरू से ही रोकना |
| [0003](lessons/0003-task-specific-metrics.md) | Task-Specific Metrics | Exact match, token-level F1 और BLEU/ROUGE, और हर एक की विफलता का तरीक़ा |
| [0004](lessons/0004-code-execution-metrics.md) | Code-Execution Metrics और Metric चुनना | Functional correctness, pass@k estimator, और हर task के लिए metric चुनने का निर्णय-सिद्धांत |
| [0005](lessons/0005-judge-prompt-design-and-calibration.md) | Judge-Prompt Design और Calibration | ऐसा judge prompt कैसे लिखें जो एकसार grade करे, और भरोसा करने से पहले judge का calibrated होना क्या मायने रखता है |
| [0006](lessons/0006-judge-bias-and-human-agreement.md) | Judge Bias और Human Agreement | LLM-as-judge में position bias और verbosity bias, और judge की मानव raters से सहमति कैसे मापें |
| [0007](lessons/0007-eval-frameworks-and-harness.md) | Eval Frameworks और Harness बनाना | हर eval harness के चार चरण, और custom eval-as-code बनाने तथा मानकीकृत benchmark harness दोबारा इस्तेमाल करने के बीच चुनाव |
| [0008](lessons/0008-reproducible-runs.md) | Reproducible Runs | एक ही eval अलग runs पर अलग संख्याएँ क्यों दे सकता है, और भरोसेमंद नतीजे को score के साथ क्या log करना चाहिए |
| [0009](lessons/0009-statistical-significance-vs-noise.md) | Statistical Significance बनाम Noise | Score के फ़र्क़ को उस noise के सामने क्यों मापना चाहिए जो उसे संयोग से पैदा कर सकता है, और दो scores को स्वतंत्र मानने से paired comparison बेहतर क्यों है |
| [0010](lessons/0010-defending-the-go-no-go-call.md) | Go/No-Go Call का बचाव | Regression threshold ईमानदारी से कैसे तय करें, और पूरे go/no-go बचाव में क्या-क्या cite करना होता है |
| [0011](lessons/0011-human-evaluation-as-a-method.md) | Method के रूप में Human Evaluation | पाठ 6 ने judge को मानव raters के सामने मापा पर यह कभी नहीं सिखाया कि मानव rating असल में बनती कैसे है, और जिस कच्ची सहमति की संख्या पर वह टिका था उसे कुछ मायने रखने से पहले संयोग के लिए अपना सुधार चाहिए |
| [0012](lessons/0012-safety-and-red-teaming-evaluation.md) | Safety और Red-Teaming Evaluation | जो safety eval सिर्फ़ यह मापता है कि model कितनी बार सचमुच असुरक्षित prompts को मना करता है, वह एक trade-off का आधा हिस्सा मापता है, क्योंकि वही tuning जो यह संख्या बढ़ाती है, उतनी ही आसानी से यह भी बढ़ा सकती है कि model कितनी बार उन prompts को मना करे जो कभी असुरक्षित थे ही नहीं |
| [0013](lessons/0013-evaluating-agents-and-tool-use.md) | Agents और Tool Use का Evaluation | Agent के task में उसी सही नतीजे तक पहुँचने के कई वैध रास्ते होते हैं, इसलिए उसे क्रियाओं की एक reference शृंखला के सामने score करना exact match की ग़लती को trajectory के पैमाने पर दोहराना है, और एक trial की सफलता दर भी यह छिपा देती है कि वही agent उसी task पर दूसरी कोशिश में कितनी बार विफल होता है |
| [0014](lessons/0014-rag-specific-evaluation.md) | RAG-Specific Evaluation | llm/rag ने retrieval की विफलता और generation की विफलता के बीच रेखा खींची पर generation-पक्ष की जाँच अपरिभाषित छोड़ दी, और वह जाँच एक नहीं बल्कि दो अलग संख्याएँ माँगती है, क्योंकि faithful दावा और सही cite किया गया दावा एक-दूसरे से स्वतंत्र रूप से विफल हो सकते हैं |
| [0015](lessons/0015-ab-tests-and-guardrail-metrics.md) | A/B Tests और Guardrail Metrics | अब तक का हर चरण offline था, पर असली उपयोगकर्ताओं तक ship करने के लिए अपनी फ़ैसले की metric चाहिए, और वह metric अकेली उतनी ही ख़तरनाक है जितनी वे अकेली safety संख्याएँ जिन पर अकेले भरोसा न करने की चेतावनी पिछले चरण पहले ही दे चुके हैं |
| [0016](lessons/0016-production-telemetry-and-drift.md) | Production Telemetry और Drift | Offline संख्या और live संख्या का असहमत होना एक समस्या नहीं, तीन अलग समस्याएँ हैं, और इंजीनियरिंग की गड़बड़ी को drift मान लेना, या drift को इंजीनियरिंग की गड़बड़ी, सुधार को ग़लत टीम के पास भेज देता है |
| [0017](lessons/0017-cost-and-latency-as-eval-dimensions.md) | Eval Dimensions के रूप में Cost और Latency | जो गुणवत्ता की जीत इस बात से अलग मापी गई हो कि उसे serve करने में क्या लगता है, वह आधा go/no-go फ़ैसला है, और औसत latency की संख्या ठीक वही tail छिपा देती है जो तय करता है कि उपयोगकर्ता system को तेज़ महसूस करते हैं या नहीं |
| [0018](lessons/0018-public-benchmarks.md) | Public Benchmarks | Leaderboard की स्थिति हिलाई जा सकने वाली metric है जिसे वे लोग optimize करते हैं जो आप नहीं हैं, उन उपयोगकर्ताओं के लिए जो आपके उपयोगकर्ता नहीं हैं, और जिसे अपने दर्ज किए गए gaming रास्तों वाली प्रक्रिया score करती है, जो उसे ठीक वैसी metric बना देता है जिस पर go/no-go संकेत के रूप में भरोसा न करने की चेतावनी पाठ 15 ने दी थी |
| [0019](lessons/0019-reviewing-an-eval-report.md) | Eval Report की समीक्षा | ठीक-ठीक बताएँ कि eval report की संख्या को क्या अविश्वसनीय बनाएगा (contamination, uncalibrated judge, variance अनुमान के बिना एक अकेला run, task-specific फ़ैसले की जगह खड़ी leaderboard rank), यह कहने के बजाय कि वह कमज़ोर लगती है |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत
- [Held-Out Data और Contamination](reference/held-out-data-and-contamination.md): contamination के दो रास्ते, guided-instruction test, और custom eval सेट के लिए रोकथाम के औज़ार
- [Metrics](reference/metrics.md): exact match, F1, BLEU/ROUGE और pass@k साथ-साथ, pass@k के सूत्र और उनमें से चुनने के निर्णय-सिद्धांत के साथ
- [LLM-as-Judge](reference/llm-as-judge.md): judge-prompt डिज़ाइन की checklist, calibration और score compression, position और verbosity bias, और human-vs-human agreement की कसौटी
- [Eval Harness](reference/eval-harness.md): चार-चरण का pipeline, openai/evals बनाम lm-evaluation-harness, और बचाव-योग्य संख्या score के साथ क्या log करती है
- [Go/No-Go](reference/go-no-go.md): standard-error का सूत्र, paired comparison, threshold ईमानदारी से तय करना, और पूरे बचाव में क्या-क्या cite होता है

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
