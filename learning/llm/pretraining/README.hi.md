---
title: "LLM Pretraining"
description: "बड़े पैमाने पर शुरू से model train करें: data, tokenizer, distributed training, और बचाव करने लायक़ compute budget"
type: topic
---

# सीखना: LLM Pretraining

random initialization से pretraining job की योजना बनाने और उसे चलाने में सक्षम बनें: data pipeline बनाएँ, tokenizer train करें, दिए गए parameter count के लिए compute-optimal token budget चुनें, कई दिनों चलने वाले distributed run को diverge होने या किसी node की failure पर अटकने से बचाएँ, और इन सभी चुनावों का बचाव उस व्यक्ति के सामने करें जो वरना किसी मौजूदा base model को बस fine-tune कर लेता।

**नवीनतम पाठ:** [24. किसी और के Training Run Config की समीक्षा](lessons/0024-reviewing-someone-elses-training-run-config.md)

## सफलता कैसी दिखती है

- कच्चे स्रोतों से deduplicated, quality-filtered pretraining corpus बनाएँ, और बताएँ कि हर filtering चरण क्या हटाता है और क्यों।
- Tokenizer train करें और vocabulary size का बचाव उसके sequence length और embedding table के आकार पर पड़ने वाले असर के आधार पर करें।
- Parameter count और compute budget दिए जाने पर compute-optimal token count निकालें और उसका बचाव Kaplan-शैली के कम-train किए गए विकल्प के सामने करें।
- समझाएँ कि ZeRO/FSDP क्या shard करते हैं, data parallelism अकेला compute ख़त्म होने से पहले memory से क्यों बाहर हो जाता है, और tensor या pipeline parallelism अपनी communication लागत के लायक़ कब है।
- किसी training run का loss curve और gradient norms पढ़ें, और बताएँ कि कोई spike recover होने लायक़ है या पुराने checkpoint से दोबारा शुरू करना पड़ेगा।
- कई दिनों के run के लिए ऐसी checkpointing योजना बनाएँ जो node failure झेल ले और कुछ मिनटों से ज़्यादा progress न गँवाए।
- तय करें कि दिया गया task pretraining, continued pretraining या किसी मौजूदा base model की fine-tuning माँगता है, और चुनाव का बचाव लागत के आधार पर करें।

## सीमाएँ

- Framework-adjacent, framework-agnostic नहीं। Distributed-training की तकनीकें (ZeRO sharding, tensor और pipeline parallelism) इतनी स्थिर हैं कि पाठ उस असली library और API का नाम लेते हैं जिसका वर्णन हो रहा है, जबकि `llm/agents` तेज़ी से बदलती सतह के लिए provider-neutral pseudocode इस्तेमाल करता है।
- कोई पाठ frontier-scale model train नहीं करता। अभ्यास छोटे पैमाने पर चलते हैं (मुट्ठी भर GPUs पर GPT-2 के आकार का model, या कई nodes का simulated setup) और वहाँ से उस पैमाने पर क्या बदलता है इसका तर्क करते हैं जिसका वर्णन उद्धृत पेपर करते हैं।
- `llm/transformers` को पूर्वज्ञान मानकर चलता है: attention mechanism, training loop, cross-entropy loss, AdamW, mixed precision और gradient clipping पूर्व-आवश्यकताएँ हैं, दोहराने की चीज़ें नहीं।
- Distributed-training के अभ्यासों के लिए कई GPUs तक पहुँच (दो भी चलेंगे, या collective operations का multi-process CPU simulation) मानी गई है।

## दायरे से बाहर

- Transformer architecture ख़ुद, cross-entropy loss, backward pass, AdamW, mixed precision और gradient clipping: [`llm/transformers`](../../llm/transformers/) देखें। यह track वहाँ से शुरू होता है जब उस loop को सैकड़ों GPUs पर और खरबों tokens के विरुद्ध चलाना हो, उससे पहले नहीं।
- LoRA, QLoRA या DoRA से किसी मौजूदा base model को ढालना: [`llm/finetuning`](../../llm/finetuning/) देखें। Pretraining random weights से शुरू होता है, किसी checkpoint से नहीं, और ये model के weights बदलने के दो तरीक़े हैं, जिन्हें एक-दूसरे के भीतर रखने के बजाय सहोदर की तरह कवर किया गया है।
- Serve के समय parallelism और quantization: [`llm/inference`](../../llm/inference/) देखें। यह track parallelism के training-time रूपों (gradient synchronization, activation और optimizer sharding) को कवर करता है, serving को नहीं।
- Evaluation की पद्धति और held-out data का डिज़ाइन: [`llm/evals`](../../llm/evals/) देखें। यहाँ उसे सिर्फ़ उस एक क्षमता के रूप में रखा गया है जो pretraining run को चाहिए, यानी run के बीच में checkpoint को validate करना, और उसे दोहराने के बजाय उसकी ओर link किया गया है।
- Pretrained model को assistant की तरह align करना: [`llm/post-training`](../../llm/post-training/) देखें।
- Training signal के रूप में distillation, जिसमें pretraining के दौरान इस्तेमाल हुआ teacher का distribution भी शामिल है: [`llm/distillation`](../../llm/distillation/) देखें। वह track loss और data का चुनाव सिखाता है; pretraining job चलाना यहीं रहता है।

## पूरी रूपरेखा

दस चरण, बिना किसी पूर्वज्ञान से लेकर वरिष्ठ-स्तर के विवेक तक। यह पाठों की सूची नहीं है: एक चरण में कई पाठ लगते हैं, और सीमाएँ लचीली हैं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
| --- | --- | --- | --- |
| 1. Data pipeline | 0001 से 0002 | Sourcing, deduplication, quality filtering | कच्चे स्रोतों से filter और deduplicate किया हुआ corpus बना सकें और हर चरण ने क्या हटाया उसका बचाव कर सकें |
| 2. Tokenizer training | 0003 से 0004 | शुरू से BPE और SentencePiece, vocabulary size के tradeoffs | Tokenizer train कर सकें और vocabulary size के चुनाव का बचाव कर सकें |
| 3. Scaling laws | 0005 से 0006 | Kaplan बनाम Chinchilla, compute-optimal token-to-parameter ratio | Compute budget दिए जाने पर compute-optimal token count निकाल सकें और उसका बचाव कर सकें |
| 4. Data parallelism | 0007 से 0008 | Gradient all-reduce, यह अकेला scale करना क्यों बंद कर देता है | बता सकें कि data parallelism अकेला compute ख़त्म होने से पहले memory से क्यों बाहर हो जाता है |
| 5. Memory की sharding | 0009 से 0011 | ZeRO stages 1 से 3, FSDP, activation और optimizer sharding | बता सकें कि हर ZeRO stage क्या shard करता है और communication में उसकी क्या लागत है |
| 6. Model parallelism | 0012 से 0014 | Training के लिए tensor और pipeline parallelism | तय कर सकें कि sharding के मुक़ाबले tensor या pipeline parallelism अपनी communication लागत कब वसूल करता है |
| 7. बड़े पैमाने पर numerics और स्थिरता | 0015 से 0017 | बड़े पैमाने पर mixed precision, loss spikes, gradient norms, warmup और decay schedules | Loss curve देखकर बता सकें कि spike recover होने लायक़ है या पुराने checkpoint से restart चाहिए |
| 8. Checkpointing और fault tolerance | 0018 से 0019 | कई दिनों के run को save और resume करना, node failure से बचना | ऐसी checkpointing योजना बना सकें जो node failure के बाद खोई हुई progress को सीमित रखे |
| 9. Training run की निगरानी | 0020 से 0021 | Loss curves, समय-समय पर eval checkpoints, `llm/evals` की ओर link | Training dashboard पढ़कर बता सकें कि run सही राह पर है या नहीं |
| 10. विवेक | 0022 से 0024 | Pretrain बनाम continue-pretrain बनाम fine-tune, compute budget का बचाव, किसी और के training run config की समीक्षा | भरोसेमंद हों कि फ़ैसला ले सकें और उसे किसी और को समझा सकें |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-sourcing-and-mixing-a-pretraining-corpus.md) | Pretraining Corpus का Sourcing और Mixing | Pretraining corpus में क्या जाता है, और स्रोतों का मिश्रण कुल byte count से ज़्यादा क्यों मायने रखता है |
| [0002](lessons/0002-deduplication-and-quality-filtering.md) | Deduplication और Quality Filtering | Training से पहले लगभग-एक-जैसे text और घटिया documents क्यों हटाए जाते हैं, और यह चरण छोड़ने की क्या क़ीमत है |
| [0003](lessons/0003-byte-pair-encoding-from-scratch.md) | शुरू से Byte-Pair Encoding | वह algorithm जो दुर्लभ और अनजाने शब्दों को सीखी हुई subword इकाइयों के क्रम में बदलता है, हाथ से हल करके |
| [0004](lessons/0004-sentencepiece-and-the-vocabulary-size-tradeoff.md) | SentencePiece और Vocabulary Size का Tradeoff | Pre-tokenizer के बिना कच्चे text को tokenize करना, और बड़ी या छोटी vocabulary की असल में क्या क़ीमत है |
| [0005](lessons/0005-scaling-laws-what-kaplan-predicted.md) | Scaling Laws: Kaplan ने क्या अनुमान लगाया | अनुभव-आधारित power law से training run का loss उसकी क़ीमत चुकाने से पहले अनुमान लगाया जा सकता है, और compute budget कैसे ख़र्च करें इस बारे में उसने क्या बताया |
| [0006](lessons/0006-chinchilla-the-compute-optimal-correction.md) | Chinchilla: Compute-Optimal सुधार | Model का आकार और token count साथ-साथ क्यों बढ़ने चाहिए, और compute budget को token count में कैसे बदला जाए |
| [0007](lessons/0007-data-parallelism-and-gradient-all-reduce.md) | Data Parallelism और Gradient All-Reduce | Batch को ऐसे devices में बाँटना जिनमें से हर एक के पास model की पूरी copy है, और क्या हर copy को एक-जैसा रखता है |
| [0008](lessons/0008-why-data-parallelism-alone-runs-out-of-memory.md) | अकेला Data Parallelism Memory से बाहर क्यों हो जाता है | ठीक-ठीक गिनना कि mixed-precision Adam optimizer हर parameter पर क्या रखता है, और वह कहाँ दीवार से टकराता है |
| [0009](lessons/0009-zero-stage-1-and-2-partitioning-optimizer-state-and-gradients.md) | ZeRO Stage 1 और 2: Optimizer State और Gradients की Partitioning | Data parallelism की फ़ालतू copies मुफ़्त में हटाना, इससे पहले कि communication लागत को बढ़ना पड़े |
| [0010](lessons/0010-zero-stage-3-and-fsdp-partitioning-parameters-too.md) | ZeRO Stage 3 और FSDP: Parameters की भी Partitioning | Parameters को ही shard करने का मतलब है उन्हें ज़रूरत पर दोबारा बनाना, और यही इसकी सबसे पहली क़ीमत है |
| [0011](lessons/0011-activation-memory-and-zero-r.md) | Activation Memory और ZeRO-R | Model states की sharding एक memory समस्या सुलझाती है और दूसरी, यानी activations, को खड़ा छोड़ देती है |
| [0012](lessons/0012-tensor-parallelism-splitting-a-layers-matrices.md) | Tensor Parallelism: Layer की Matrices को बाँटना | Weight matrix को किस अक्ष पर बाँटना है यह चुनना, ताकि पूरे transformer block को सिर्फ़ एक all-reduce चाहिए |
| [0013](lessons/0013-pipeline-parallelism-splitting-the-models-layers.md) | Pipeline Parallelism: Model की Layers को बाँटना | लगातार layers को अलग-अलग devices को देना, और हर batch की शुरुआत और अंत में उससे होने वाला idle time |
| [0014](lessons/0014-combining-all-three-when-tensor-and-pipeline-parallelism-earn-their-cost.md) | तीनों को मिलाना: Tensor और Pipeline Parallelism अपनी लागत कब वसूल करते हैं | हर parallelism रणनीति को उस interconnect से मिलाना जो वह सह सकती है, और कब अकेली sharding काफ़ी नहीं होती |
| [0015](lessons/0015-mixed-precision-at-scale-bfloat16-and-stochastic-rounding.md) | बड़े पैमाने पर Mixed Precision: bfloat16 और Stochastic Rounding | fp32 जैसी range पर कम precision वाला numeric format, और parameters को सीधे उसी में update करने की क्या क़ीमत है |
| [0016](lessons/0016-loss-spikes-and-the-optimizers-own-instabilities.md) | Loss Spikes और Optimizer की अपनी अस्थिरताएँ | वही spike किसी ख़राब batch से भी आ सकता है और optimizer से भी, और दोनों में फ़र्क़ करने के लिए नियंत्रित तुलना चाहिए |
| [0017](lessons/0017-warmup-decay-and-growing-the-batch-mid-run.md) | Warmup, Decay, और Run के बीच Batch बढ़ाना | धीमे शुरू करना, schedule के हिसाब से decay करना, और training के बीच में batch size को ही बदलने देना |
| [0018](lessons/0018-what-a-checkpoint-has-to-hold.md) | Checkpoint में क्या रखना ज़रूरी है | जो checkpoint सिर्फ़ weights सहेजता है वह run को हू-ब-हू resume नहीं कर सकता, और कितनी बार save करें यह चुनना अपने आप में एक tradeoff है |
| [0019](lessons/0019-surviving-a-node-failure.md) | Node Failure से बचना | रुकें, जाँचें, जो टूटा है उसे अलग करें, और आख़िरी checkpoint से resume करें, चाहे जो भी क़ीमत लगे |
| [0020](lessons/0020-reading-a-loss-curve.md) | Loss Curve पढ़ना | अकेला training loss curve गड़बड़ी को कम दिखाता है; दो दूसरे signals वह पकड़ लेते हैं जो वह चूक जाता है, और जल्दी पकड़ते हैं |
| [0021](lessons/0021-periodic-held-out-evaluation.md) | समय-समय पर Held-Out Evaluation | Training loss बताता है कि model अपने ही training data पर fit हो रहा है; बाक़ी के बारे में सिर्फ़ held-out जाँच कुछ बताती है |
| [0022](lessons/0022-pretraining-is-usually-the-wrong-default.md) | Pretraining अक्सर ग़लत default होता है | मौजूदा model पर pretraining का दूसरा चरण पूरी लागत दोबारा चुकाए बिना ज़्यादातर फ़ायदा दिला देता है |
| [0023](lessons/0023-defending-a-compute-budget.md) | Compute Budget का बचाव | Pretraining योजना कई अलग फ़ैसलों से बना एक दाँव है, और उसका बचाव करने का मतलब हर फ़ैसले का उसकी अपनी शर्तों पर बचाव करना है |
| [0024](lessons/0024-reviewing-someone-elses-training-run-config.md) | किसी और के Training Run Config की समीक्षा | योजना को इस track के हर चरण से क्रम में गुज़ारें, और विवादित दावे का निपटारा किसी blog post से नहीं, स्रोत से करें |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके मुख्य स्रोत तक खंगालना ठीक रहेगा।
