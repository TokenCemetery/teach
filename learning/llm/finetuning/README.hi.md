---
title: "Adapter Fine-Tuning"
description: "तय करें कि fine-tune करना है या नहीं, उसे चलाएँ, साबित करें कि वह काम आया, और ship करें"
type: topic
---

# सीखना: Adapter Fine-Tuning (LoRA, QLoRA, DoRA)

ऐसा व्यक्ति बनें जो किसी base model और task को लेकर तय कर सके कि adapter fine-tuning सही जवाब है भी या नहीं, उसे चला सके, ऐसे eval से साबित कर सके कि वह काम आया जो regression को पकड़ लेता, और उसे ship कर सके, और जो prompting या retrieval के पक्ष में विश्वसनीय ढंग से तर्क दे सके जब वे काम को बेहतर करते हों।

**यहाँ से शुरू करें:** [1. Base Model असल में क्या है](lessons/0001-what-a-base-model-is.md)
**नवीनतम पाठ:** [27. Fine-Tuning कब न करें](lessons/0027-when-not-to-fine-tune.md)

## सफलता कैसी दिखती है

- किसी दिए model के लिए full fine-tuning बनाम LoRA की memory लागत निकालें और हर byte का हिसाब दें।
- किसी नए task के लिए rank, alpha, target modules और learning rate चुनें और हर एक को किसी blog post के defaults से नहीं बल्कि task के आधार पर सही ठहराएँ।
- एक ही task पर LoRA, QLoRA और DoRA adapters train करें और विज्ञापित नहीं बल्कि मापे गए फ़र्क़ समझाएँ।
- ऐसा eval बनाएँ जो ship करने से पहले regression पकड़ ले, loss curve पढ़कर उम्मीद लगाने के बजाय।
- किसी inference stack से adapter serve करें और मापें कि गुणवत्ता और latency में उसकी क्या क़ीमत लगी।
- विफल run का diagnosis करें और कारण का नाम बताएँ: overfitting, catastrophic forgetting, ग़लत chat template, tokenizer mismatch, ग़लत target modules।
- नया PEFT पेपर पढ़ें और परखें कि उसकी बताई जीत आपके अपने task पर टिकेगी या नहीं।

## सीमाएँ

- पहले से machine-learning की कोई पृष्ठभूमि नहीं मानी गई है। Matrix गुणन ही अकेला गणित है जिसे जाना हुआ मानकर चला गया है; उसके ऊपर की हर चीज़ वहीं सिखाई जाती है जहाँ ज़रूरत पड़ती है।
- 1B से 3B वर्ग के base model पर adapter training लगभग 16 GB accelerator या unified memory में समा जाती है, जिससे पूरी रूपरेखा सामान्य single-device hardware की पहुँच में आ जाती है।
- Backend support असमान है, अनन्य नहीं। CUDA सबसे पूरा और सबसे अच्छी तरह optimised रास्ता बना हुआ है और वहीं प्रकाशित संख्याएँ सबसे भरोसेमंद ढंग से दोहराई जाती हैं; अन्य backends अलग-अलग kernel coverage और धीमे steps के साथ काम करते हैं। हर अवधारणा बिना बदले लागू होती है; सिर्फ़ गति और kernel की उपलब्धता अलग है।
- अभ्यास लंबी-latency वाले हैं: एक training run में मिनटों से घंटों लगते हैं, इसलिए सत्र एक शाम में समाने के बजाय बीच में पढ़ाई के साथ इकट्ठे किए जाते हैं।
- Tooling किसी भी किताब से तेज़ चलती है। Library के APIs याद से नहीं, installed version के दस्तावेज़ से पढ़े जाते हैं।
- रूपरेखा में कुछ भी paid infrastructure नहीं माँगता, हालाँकि बड़ा accelerator किराए पर लेने से कुछ तुलनाएँ तेज़ हो जाएँगी।

## दायरे से बाहर

- बड़े पैमाने पर full fine-tuning, pretraining, और model को शून्य से train करना: [`llm/pretraining`](../../llm/pretraining/) देखें।
- RLHF, DPO और preference optimisation: [`llm/post-training`](../../llm/post-training/) देखें। यह track सँभालता है कि बदलाव कम parameters पर कैसे लगाया जाता है; वह track training का objective सँभालता है।
- अपने आप में विषय के रूप में Quantization: [`llm/quantization`](../../llm/quantization/) देखें। यहाँ चरण 4 वह हिस्सा रखता है जो QLoRA को चाहिए और सामान्य सिद्धांत के लिए वहाँ link करता है; यह सीमा तब तय हुई थी जब quantization track लिखा गया। Serve के समय Quantization [`llm/inference`](../../llm/inference/) में कवर है।
- अपने आप में विषय के रूप में Distillation: [`llm/distillation`](../../llm/distillation/) देखें। यह track सँभालता है कि training run कम parameters पर कैसे लगाया जाता है; वह track distillation का objective और data सँभालता है।
- Serving infrastructure बनाना, किसी मौजूदा stack से adapter चलाने से आगे: [`llm/inference`](../../llm/inference/) देखें।

## पूरी रूपरेखा

सात चरण, शून्य से वरिष्ठ तक। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. ज़मीनी बुनियाद | 0001 से 0004 | Forward pass क्या compute करता है, weight matrices कहाँ रहती हैं, tokenizers, chat templates, training क्या बदलती है | बता सकें कि adapter कौन-से tensors को छुएगा और क्यों |
| 2. Memory की दलील | 0005 से 0007 | Parameters बनाम gradients बनाम optimizer state, AdamW के दो moments, activation memory, gradient checkpointing | bytes में निकाल सकें कि दिए device पर full fine-tuning क्यों विफल होती है |
| 3. LoRA | 0008 से 0013 | `ΔW = BA`, rank, alpha और scaling, initialisation, target module का चुनाव, उसे चलाना, run को पढ़ना, merging | Adapter train कर सकें और हर hyperparameter का बचाव कर सकें |
| 4. Quantisation और QLoRA | 0014 से 0017 | int8/int4, NF4, double quantisation, frozen quantized base के आर-पार backprop, क्या बिगड़ता है | असली NF4 चलाया हो और बता सकें कि गुणवत्ता में उसकी क्या क़ीमत लगी |
| 5. DoRA और variants का परिदृश्य | 0018 से 0020 | Magnitude/direction decomposition, यह कम rank पर सबसे ज़्यादा मदद क्यों करता है, नए variant के दावे को कैसे आँकें | चलाने से पहले भविष्यवाणी कर सकें कि DoRA, LoRA को कब हराएगा |
| 6. Data और evaluation | 0021 से 0024 | Dataset बनाना, contamination, held-out design, task metrics बनाम loss, regression suites | ऐसा eval हो जिसने सचमुच regression पकड़ा हो |
| 7. चलाना और परखना | 0025 से 0027 | Adapters को serve करना बनाम merged, multi-adapter serving, cost और latency, कब fine-tune *नहीं* करना | भरोसेमंद हों कि तय कर सकें कि task को fine-tune करना भी चाहिए या नहीं |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-what-a-base-model-is.md) | Base Model असल में क्या है | Model एक ही next-token function है; base का मतलब instruct नहीं |
| [0002](lessons/0002-where-the-weights-live.md) | Weights कहाँ रहते हैं | हर उस projection का नाम लेना जिससे adapter जुड़ सकता है |
| [0003](lessons/0003-tokenizers-and-chat-templates.md) | Tokenizers और Chat Templates | उसी rendering पर train करें जिसे आप serve करेंगे |
| [0004](lessons/0004-what-training-changes.md) | Training असल में क्या बदलती है | एक training step के चार ऑपरेशन |
| [0005](lessons/0005-counting-parameters-and-bytes.md) | Parameters और Bytes गिनना | Model config को gigabytes में बदलना |
| [0006](lessons/0006-gradients-and-optimizer-state.md) | Gradients और Optimizer State | प्रति trainable parameter सोलह bytes, प्रति frozen दो |
| [0007](lessons/0007-activations-and-checkpointing.md) | Activations, Batch Size और Checkpointing | Adapter run फिर भी memory से बाहर क्यों हो जाता है |
| [0008](lessons/0008-the-low-rank-idea.md) | Low-Rank का विचार | `ΔW = BA`, और adapter की गिनती |
| [0009](lessons/0009-rank-alpha-and-initialisation.md) | Rank, Alpha और Initialisation | सिर्फ़ `α/r` मायने रखता है, और `B` शून्य से क्यों शुरू होता है |
| [0010](lessons/0010-choosing-target-modules.md) | Target Modules चुनना | Attention-only 2021 का ablation है, default नहीं |
| [0011](lessons/0011-your-first-adapter.md) | आपका पहला Adapter | ऐसा run जो किसी और चीज़ को साबित करने से पहले pipeline को साबित करे |
| [0012](lessons/0012-reading-a-training-run.md) | Training Run को पढ़ना | Curve के आकार से diagnosis, और वह जो loss देख नहीं सकता |
| [0013](lessons/0013-merging-and-shipping.md) | Adapter को Merge, Save और Ship करना | Merge सटीक है; adapter एक diff है जिसे अपना base चाहिए |
| [0014](lessons/0014-quantisation-from-first-principles.md) | पहले सिद्धांतों से Quantisation | Blockwise scales, और एक outlier पूरे tensor को क्यों बिगाड़ देता है |
| [0015](lessons/0015-nf4-and-double-quantisation.md) | NF4 और Double Quantisation | वे दो विचार जो QLoRA ने सचमुच दिए |
| [0016](lessons/0016-training-through-a-quantized-base.md) | Quantized Base के आर-पार Training | Frozen 4-bit weights से gradients कैसे बहते हैं |
| [0017](lessons/0017-what-qlora-costs.md) | QLoRA की असली क़ीमत | Base की गिरावट को training की गिरावट से अलग करना |
| [0018](lessons/0018-dora-magnitude-and-direction.md) | DoRA: Magnitude और Direction | Renormalisation दोनों को अलग करता है, और यही तरीक़ा है |
| [0019](lessons/0019-when-dora-wins.md) | DoRA कब जीतता है, और कब नहीं | चलाने से पहले जीत की भविष्यवाणी करना |
| [0020](lessons/0020-judging-a-new-variant.md) | नए PEFT Variant को परखना | छह triage सवाल, और हराने लायक baseline |
| [0021](lessons/0021-building-the-dataset.md) | Dataset बनाना | इस workspace में data हर hyperparameter को हराता है |
| [0022](lessons/0022-contamination-and-held-out-design.md) | Contamination और Held-Out Design | सही key से split करना, और सवाल के हिसाब से आकार तय करना |
| [0023](lessons/0023-metrics-that-mean-something.md) | ऐसी Metrics जिनका मतलब हो | Loss checkpoints चुनता है; task metrics फ़ैसले लेती हैं |
| [0024](lessons/0024-the-regression-suite.md) | Regression Suite | वह नुक़सान पकड़ना जो बाक़ी हर संख्या छिपा देती है |
| [0025](lessons/0025-serving-adapters.md) | Adapters को Serve करना | एक task के लिए merge करें, कई के लिए route करें |
| [0026](lessons/0026-cost-latency-and-throughput.md) | Cost, Latency और Throughput | Prefill बनाम decode, और पैसा असल में कहाँ जाता है |
| [0027](lessons/0027-when-not-to-fine-tune.md) | Fine-Tuning कब न करें | Fine-tuning सूची में छठे नंबर पर है, और यह क्यों मायने रखता है |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत और समुदाय
- [memory budget शीट](reference/memory-budget.md): bytes का हिसाब, और जब run न समाए तब क्या आज़माएँ
- [LoRA hyperparameters शीट](reference/lora-hyperparameters.md): rank, alpha, targets, learning rate, variants
- [failure modes शीट](reference/failure-modes.md): लक्षण से कारण, और चुपचाप होने वाली विफलताएँ

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके मुख्य स्रोत तक खंगालना ठीक रहेगा।
