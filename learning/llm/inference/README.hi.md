---
title: "Inference"
description: "Model को serve करें: KV cache, batching, serve time पर quantization, और ऐसा latency budget जिसका आप बचाव कर सकें"
type: topic
---

# सीखना: Inference

किसी असली model के लिए inference server खड़ा कर पाएँ, पहले GPU पर और फिर CPU/edge पर, और framework के defaults जो भी संख्याएँ दे दें उन्हें दोहराने के बजाय उसके latency और throughput की संख्याओं का बचाव कर सकें।

**नवीनतम पाठ:** [25. Serving Configuration की समीक्षा](lessons/0025-reviewing-a-serving-configuration.md)

## सफलता कैसी दिखती है

- किसी दिए model के लिए serving stack खड़ा करें (GPU पर vLLM, फिर CPU/edge पर llama.cpp) और उससे requests के जवाब दिलवाएँ।
- किसी दिए batch size और model के लिए p99 latency budget बताएँ, और उस संख्या का बचाव उन KV cache, batching और quantization चुनावों से करें जिनसे वह निकली।
- किसी और की serving configuration की समीक्षा करें और ठीक-ठीक बताएँ कि उसकी क्या क़ीमत है (बताए गए workload की अड़चन के विरुद्ध ग़लत सेट किया गया knob, बिना किसी justify करने वाली अड़चन के चुनी गई topology, ऐसा rollout जो बीच में किसी caller को तोड़ दे), यह कहने के बजाय कि कुछ ठीक नहीं लग रहा।

## सीमाएँ

- मानकर चला गया है कि आप Python ML environment चलाने में सहज हैं और जानते हैं कि language model क्या होता है; serving-infrastructure का कोई पूर्व अनुभव नहीं चाहिए।
- मुख्य stacks: vLLM (GPU) और llama.cpp (CPU/edge), इसी क्रम में। दूसरे stacks (TGI, TensorRT-LLM) का ज़िक्र सिर्फ़ वहीं है जहाँ कोई अवधारणा अलग तरह से लागू होती है।

## दायरे से बाहर

- Model या adapter को train या fine-tune करना: [`llm/finetuning`](../../llm/finetuning/) देखें (पाठ 0025, adapters को serve करना, और 0026, लागत, latency और throughput), जिसे यहाँ दोहराने के बजाय उसकी ओर link किया गया है।
- Served model के output की गुणवत्ता परखना या उसके लिए eval बनाना: उस सीमा के लिए [`llm/evals`](../../llm/evals/) देखें।
- Quantization के तरीक़े कैसे काम करते हैं और उन्हें कैसे परखा जाए, number formats और affine mapping से लेकर GPTQ, AWQ, SmoothQuant, QAT और गुणवत्ता की हानि मापने तक: [`llm/quantization`](../../llm/quantization/) देखें। यहाँ का चरण 3 serving का फ़ैसला रखता है, यानी latency budget के लिए scheme चुनना, और बुनियाद के लिए वहीं link करता है; यह सीमा तब तय हुई थी जब quantization track लिखा गया।
- Prompt की तरफ़ से structured output माँगना: [`llm/prompting`](../../llm/prompting/) देखें। यह track constrained decoding सँभालता है, यानी उसी लक्ष्य का serving वाला पक्ष।

## पूरी रूपरेखा

चौदह चरण, पहली request से लेकर ऐसी serving configuration तक जिसका बचाव हो चुका हो, जो fleet के पैमाने की हो, production में monitor होती हो और जिसकी समीक्षा हो चुकी हो। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. KV cache | 0001 से 0003 | Autoregressive generation महँगी क्यों है, cache memory के बदले क्या बचाता है, और context और batch के साथ cache का आकार कैसे बढ़ता है | किसी दी गई context length और batch size के लिए model के KV cache का memory footprint निकाल सकें |
| 2. Batching | 0004 से 0006 | Static बनाम continuous batching, request scheduling, throughput/latency का trade-off | बताए गए workload के लिए batching configuration का बचाव कर सकें |
| 3. Serve time पर quantization | 0007 से 0009 | Inference के समय int8/int4/AWQ/GPTQ, accuracy बनाम speed बनाम memory | Serve-time का quantization scheme चुन सकें और trade-off का बचाव कर सकें |
| 4. व्यवहार में vLLM | 0010 से 0012 | vLLM खड़ा करना, PagedAttention, वे tuning knobs जो मायने रखते हैं | vLLM stack चल रहा हो और असली requests के जवाब दे रहा हो |
| 5. CPU/edge पर llama.cpp | 0013 से 0015 | GGUF, llama.cpp का architecture, GPU से बाहर क्या बदलता है | llama.cpp stack CPU पर चल रहा हो और असली requests के जवाब दे रहा हो |
| 6. Latency budget | 0016 से 0017 | p99 मापने की methodology, उस संख्या को cache, batching और quantization के चुनावों से जोड़ना | p99 latency budget को शुरू से अंत तक बता और उसका बचाव कर सकें |
| 7. Speculative decoding | 0018 | Draft-model, n-gram, Medusa और EAGLE speculative decoding | समझा सकें कि parallel verification लगभग मुफ़्त क्यों है और किसी workload के लिए speculative-decoding का कोई रूप चुन सकें |
| 8. Serve time पर sampling और constrained decoding | 0019 | साझा batch में प्रति-request sampling parameters, FSM-indexed constrained decoding | समझा सकें कि constrained decoding की गारंटी structural क्यों है और उसकी प्रति-token लागत छोटी क्यों रहती है |
| 9. Prefix caching | 0020 | Cross-request block sharing के रूप में automatic prefix caching, लंबे document और multi-turn workloads, उसकी सिर्फ़-prefill वाली सीमा | समझा सकें कि prefix caching किसी workload की मदद कब करता है और decode को कभी तेज़ क्यों नहीं करता |
| 10. Multi-GPU और multi-node parallelism | 0021 | पाठ 12 के अकेले flag से आगे tensor parallelism की असली कार्यप्रणाली, pipeline parallelism, और यह तय करने की प्रक्रिया कि deployment को कौन-सा (या दोनों) चाहिए | समझा सकें कि tensor-parallel का combine step और pipeline bubble हर एक की क्या क़ीमत है, और दिए गए interconnect और node count के लिए सही split चुन सकें |
| 11. Fleet-level serving | 0022 | Cache locality से तय होने वाली request routing, queue-depth से चलने वाली autoscaling, और यह कि cold start में model load का समय क्यों तय करता है कि नई replica कितनी जल्दी सचमुच काम आती है | समझा सकें कि routing, autoscaling और cold-start latency को अलग-अलग tune करने के बजाय एक pipeline की तरह क्यों सोचना पड़ता है |
| 12. Production observability और cost | 0023 | लगातार export होने वाले metrics, SLIs/SLOs/error budgets जो metric को लक्ष्य में बदलते हैं, और नापे गए throughput से निकली cost per million tokens | Production configuration का बचाव उसके p99, उस पर लागू SLO और error budget, और उसकी cost per million tokens का हवाला देकर कर सकें |
| 13. Serve time पर long context | 0024 | RoPE scaling बनाम sliding-window attention और attention sinks, और हर एक पाठ 2 के cache-growth formula के साथ असल में क्या करता है | समझा सकें कि कोई long-context तकनीक उपयोगी length बढ़ाती है, cache का आकार एक स्थिरांक पर सीमित करती है, या सीमित cache की विफलता का इलाज करती है |
| 14. विवेक | 0025 | किसी और की configuration की समीक्षा बेमेल knobs के लिए, उन चीज़ों के ज़रिए सुरक्षित rollouts जिन पर दूसरे निर्भर हैं, और यह कहना कि speculative decoding कब मुफ़्त जीत नहीं है | भरोसेमंद हों कि serving configuration की समीक्षा करें और बताएँ कि हर चुनाव की क्या क़ीमत है, सिर्फ़ यह नहीं कि वह ठीक नहीं लग रहा |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-the-kv-cache.md) | KV Cache | Generation महँगी क्यों हो जाती है, और caching क्या वापस दिलाती है |
| [0002](lessons/0002-capacity-and-batch-size.md) | Capacity और Batch Size | Head sharing (GQA/MQA) और batch size cache के असली footprint को कैसे बदलते हैं |
| [0003](lessons/0003-growth-prefill-decode-precision.md) | Growth, Prefill, Decode और Precision | Prefill और decode के दौरान cache कैसे बढ़ता है, और उसकी precision घटाने से क्या वापस मिलता है |
| [0004](lessons/0004-static-vs-continuous-batching.md) | Static बनाम Continuous Batching | Requests को साथ batch करना throughput के लिए अच्छा क्यों है, और continuous batching static वाले से बेहतर क्यों है |
| [0005](lessons/0005-request-scheduling.md) | Request Scheduling | Continuous-batching scheduler अगली request कैसे चुनता है, और बड़ा prefill बाक़ी सबको क्यों रोक सकता है |
| [0006](lessons/0006-throughput-latency-tradeoff.md) | Throughput/Latency Trade-off | Batch size throughput और प्रति-token latency के बीच कैसे सौदा करता है, और बताए गए latency budget के विरुद्ध batching configuration का बचाव कैसे करें |
| [0007](lessons/0007-quantization-schemes.md) | Serve Time पर Quantization Schemes | int8, int4, GPTQ और AWQ model के weights के साथ असल में क्या करते हैं, और low-bit quantization के सीधे-सादे रूप को सुधार की ज़रूरत क्यों पड़ती है |
| [0008](lessons/0008-accuracy-speed-memory-tradeoffs.md) | Accuracy, Speed और Memory के Trade-offs | Model quantize करने पर memory, speed और accuracy साथ-साथ क्यों नहीं चलते, और हर एक असल में कैसे नापा जाता है |
| [0009](lessons/0009-picking-a-quantization-scheme.md) | Quantization Scheme चुनना और उसका बचाव करना | Serve-time quantization scheme चुनने का फ़ैसला-ढाँचा, और वे तीन संख्याएँ जो उसका बचाव करती हैं |
| [0010](lessons/0010-standing-up-vllm.md) | vLLM खड़ा करना | vLLM install करना, उसका server launch करना, और वे flags ढूँढना जो पहले सिखाई जा चुकी अवधारणाओं को ढोते हैं |
| [0011](lessons/0011-pagedattention.md) | PagedAttention | vLLM के पीछे की block table की कार्यप्रणाली, उसका block-size trade-off, और वह sequences को साझा prefix का cache कैसे बाँटने देती है |
| [0012](lessons/0012-vllm-tuning-knobs.md) | vLLM के ज़रूरी Tuning Knobs | दो और flags, gpu-memory-utilization और tensor-parallel-size, और यह तय करने की प्रक्रिया कि कोई लक्षण असल में किस knob की ओर इशारा करता है |
| [0013](lessons/0013-gguf.md) | GGUF | llama.cpp का single-file model format अपने अंदर क्या समेटता है, उसके quantization के नाम, और वह load होने के बजाय memory-map क्यों हो सकता है |
| [0014](lessons/0014-llamacpp-architecture.md) | llama.cpp का Architecture | llama.cpp के नीचे की ggml tensor library, उसका backend abstraction, और CPU threading GPU batching से कैसे अलग है |
| [0015](lessons/0015-what-changes-off-gpu.md) | GPU से बाहर क्या बदलता है | llama.cpp का server खड़ा करना, और batching, cache management और quantization हर एक CPU/edge के पैमाने पर कैसे अलग दिखते हैं |
| [0016](lessons/0016-p99-latency-methodology.md) | p99 Latency मापने की Methodology | p99 औसत से बेहतर क्यों है, TTFT और inter-token latency को अलग संख्याएँ क्यों चाहिए, और p99 माप को भरोसेमंद क्या बनाता है |
| [0017](lessons/0017-defending-a-latency-budget-end-to-end.md) | Latency Budget का शुरू से अंत तक बचाव | चूके हुए p99 budget की जाँच का क्रम, और वे तीन चीज़ें जिनका हवाला अंतिम बचाव की गई configuration को देना ही चाहिए |
| [0018](lessons/0018-speculative-decoding.md) | Speculative Decoding | कई संभावित tokens को एक parallel forward pass में verify करने की लागत लगभग उतनी ही होती है जितनी एक token आम तौर पर generate करने की, क्योंकि decoding की अड़चन weights को ढोना है, arithmetic नहीं, और यही वह एक तथ्य है जिस पर speculative decoding का हर रूप टिका है |
| [0019](lessons/0019-sampling-and-constrained-decoding-at-serve-time.md) | Serve Time पर Sampling और Constrained Decoding | Continuous batch पहले से कई requests को एक साझा forward pass से गुज़ारता है, और हर एक को उसकी अपनी sampling settings देना, या किसी एक को सिर्फ़ valid JSON ही बनाने के लिए मजबूर करना, दोनों को उसी साझा pass के भीतर प्रति-row होना पड़ता है, बिना बाक़ी सबको धीमा किए |
| [0020](lessons/0020-prefix-caching.md) | Prefix Caching | पाठ 11 में एक ही request के parallel samples एक prompt के cached blocks साझा करते थे; prefix caching वही साझेदारी बाक़ी बेमेल requests के पार लागू करती है, और वह ठीक उस चरण को तेज़ करती है जिसे फ़ालतू prefill बरबाद करता है, उस चरण को कभी नहीं जो जवाब generate करता है |
| [0021](lessons/0021-tensor-and-pipeline-parallelism.md) | Tensor और Pipeline Parallelism | पाठ 12 ने tensor-parallel-size को ऐसे flag के रूप में बताया जो model को GPUs में बाँटता है; यह पाठ खोलकर दिखाता है कि वह split layer के भीतर असल में क्या करता है, pipeline parallelism को उसी समस्या के अलग बँटवारे के रूप में लाता है, और यह तय करने की प्रक्रिया देता है कि workload को कौन-सा (या दोनों) सचमुच चाहिए |
| [0022](lessons/0022-fleet-level-serving.md) | Fleet-Level Serving | पाठ 5 का scheduler एक server की queue के लिए अगली request चुनता है; fleet इससे पहले एक फ़ैसला जोड़ता है कि request किस server को मिले, एक फ़ैसला कि और servers कब जोड़ें, और एक cold-start लागत जो नए जोड़े server को दसियों सेकंड बेकार बना देती है |
| [0023](lessons/0023-production-observability-and-cost.md) | Production Observability और Cost | पाठ 17 ने एक configuration के लिए एक नापे गए p99 आँकड़े का बचाव किया; यह पाठ बताता है कि regression अपने आप पकड़ने के लिए लगातार क्या export होना चाहिए, वह SLO और error budget जो "काफ़ी अच्छा" को अंदाज़े के बजाय लक्ष्य बनाते हैं, और cost-per-million-tokens की वह संख्या जिसका बचाव p99 के साथ करना है, उसकी जगह नहीं |
| [0024](lessons/0024-long-context-at-serve-time.md) | Serve Time पर Long Context | पाठ 2 का capacity formula context length के साथ memory की रैखिक क़ीमत लगाता है; RoPE scaling उस क़ीमत को बिल्कुल बदले बिना context कितना लंबा हो सकता है यह बढ़ाती है, जबकि sliding-window attention और attention sinks context length को एक स्थिरांक पर सीमित करके formula को ही बदल देते हैं |
| [0025](lessons/0025-reviewing-a-serving-configuration.md) | Serving Configuration की समीक्षा | किसी और की serving configuration की समीक्षा करें और ठीक-ठीक बताएँ कि उसकी क्या क़ीमत है (बताए गए workload की अड़चन के विरुद्ध ग़लत सेट किया गया knob, बिना किसी justify करने वाली अड़चन के चुनी गई topology, ऐसा rollout जो बीच में किसी caller को तोड़ दे), यह कहने के बजाय कि कुछ ठीक नहीं लग रहा |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत
- [KV Cache शीट](reference/kv-cache.md): प्रति-token लागत, head sharing, request के दौरान बढ़त, और capacity planning
- [Batching शीट](reference/batching.md): static बनाम continuous batching, request scheduling, और throughput/latency का trade-off
- [Serve Time पर Quantization शीट](reference/quantization-at-serve-time.md): int8/int4/GPTQ/AWQ, memory, speed और accuracy साथ-साथ क्यों नहीं चलते, और scheme चुनने का फ़ैसला-ढाँचा
- [vLLM शीट](reference/vllm.md): vLLM खड़ा करना, PagedAttention, और वे tuning knobs जो मायने रखते हैं
- [llama.cpp शीट](reference/llama-cpp.md): GGUF, llama.cpp का architecture, और GPU से बाहर क्या बदलता है
- [Latency Budget शीट](reference/latency-budget.md): p99 मापने की methodology, और चूके हुए budget को cache, batching और quantization के चुनावों से जोड़ना

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके मुख्य स्रोत तक खंगालना ठीक रहेगा।
