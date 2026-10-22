---
title: "Quantization"
description: "LLM को quantize करें और उसका बचाव करें: number formats, PTQ और QAT के तरीक़े, क्या सचमुच तेज़ चलता है, और इसकी क़ीमत को मापना"
type: topic
---

# सीखना: Quantization

Train हो चुके LLM को quantization से छोटा और तेज़ बनाएँ, यह जानते हुए कि हर number format और method उसके weights, activations और KV cache के साथ क्या करता है। अंत में किसी दिए model, hardware और quality की सीमा के लिए scheme चुन सकें, ईमानदारी से माप सकें कि उसकी क़ीमत क्या चुकानी पड़ी, और किसी और के इस दावे की समीक्षा कर सकें कि quantized model "कुछ नहीं खोता"।

**नवीनतम पाठ:** [27. जब आम जवाब ग़लत हो](lessons/0027-when-the-usual-answer-is-wrong.md)

## सफलता कैसी दिखती है

- किसी number format का bit layout पढ़ें, बताएँ कि वह कौन-सी range और precision देता है, और उस format में model की memory का हिसाब लगाएँ।
- हाथ से किसी tensor को quantize करें: scale, zero point, clipping range और granularity चुनें, और अनुमान लगाएँ कि error कहाँ से आएगी।
- समझाएँ कि LLMs में outlier features और activations क्यों होते हैं, और हर एक को कौन-सी technique सँभालती है।
- समझाएँ कि round-to-nearest, GPTQ और AWQ हर एक weights के साथ क्या करता है, और calibration set क्या योगदान देता है और क्या बिगाड़ सकता है।
- तय करें कि weights के अलावा activations और KV cache को कब quantize किया जा सकता है, और किस technique से।
- बताएँ कि post-training quantization के मुक़ाबले quantization-aware training अपनी लागत कब वसूल करती है।
- अनुमान लगाएँ कि कोई scheme दिए hardware पर दिए batch size में सचमुच तेज़ चलेगा या नहीं, यह मान लेने के बजाय कि कम bits का मतलब तेज़ है।
- Perplexity से आगे जाकर, एक ईमानदार baseline के मुक़ाबले माप सकें कि quantization ने कितनी quality ली।
- Quantized checkpoint को पढ़ें, चाहे safetensors में उसके quantization config के साथ हो या GGUF में, और बताएँ कि उसमें क्या store है।
- किसी दिए model, hardware और quality की सीमा के लिए scheme चुनें, किसी और के quantization दावे की समीक्षा उसमें छिपी बात का नाम लेकर करें, और बताएँ कि आम जवाब कब ग़लत होता है।

## सीमाएँ

- मानकर चला गया है कि आप Python और NumPy पढ़ने में सहज हैं, और जानते हैं कि transformer layer "matrix multiplications और attention" के स्तर पर क्या होती है। Quantization या floating-point की भीतरी बनावट का कोई पूर्व ज्ञान नहीं चाहिए।
- जहाँ तक हो सके hardware-neutral। जहाँ कोई दावा किसी एक vendor या एक library के documented व्यवहार का है, पाठ उसका नाम लेता है, क्योंकि kernel support सिद्धांत से तेज़ी से बदलता है।
- चरण 1 से 3 का अभ्यास laptop पर NumPy से चलता है। बाद के अभ्यास किसी छोटे open model को quantize करते हैं, जिसके लिए मुफ़्त GPU notebook काफ़ी है।

## दायरे से बाहर

- QLoRA, यानी 4-bit base के आर-पार adapter को train करना: [`llm/finetuning`](../../llm/finetuning/) का चरण 4 (पाठ 0014 से 0017) देखें। यह track वह सामान्य सिद्धांत सिखाता है जिसे वे पाठ लागू करते हैं, और QLoRA को दोहराने के बजाय उनकी ओर link करता है।
- Serving latency बजट के लिए scheme चुनना और उसे vLLM या llama.cpp में चलाना: [`llm/inference`](../../llm/inference/) का चरण 3 (पाठ 0007 से 0009) और उसकी [Serve Time पर Quantization शीट](../../llm/inference/reference/quantization-at-serve-time.md) देखें। यह track सिखाता है कि तरीक़े कैसे काम करते हैं और उन्हें कैसे परखें; serving का फ़ैसला वहीं रहता है।
- Eval बनाना: [`llm/evals`](../../llm/evals/) और उसकी [Go/No-Go शीट](../../llm/evals/reference/go-no-go.md) देखें। यह track quantization की हानि मापने के लिए eval इस्तेमाल करता है और eval बनाना दोबारा नहीं सिखाता।
- Pruning, sparsity और distillation, यानी model को छोटा करने के दूसरे तरीक़े। ये quantization के साथ मिलाए जा सकते हैं पर अलग विषय हैं। Distillation का अपना track है, [`llm/distillation`](../../llm/distillation/), जो अपने विवेक वाले चरण में उसकी तुलना quantization से करता है।
- Quantization kernels लिखना। चरण 7 सिखाता है कि किसी scheme के तेज़ चलने के लिए kernel को क्या करना होगा, यह नहीं कि उसे कैसे लिखा जाए।

इस track को लिखते समय दोनों पड़ोसियों के साथ सीमा तय हुई थी: finetuning और inference के पाठ जैसे हैं वैसे रहेंगे, हर एक अपने उपयोग के लिए ज़रूरी हिस्सा सिखाता है, और बुनियाद के लिए यहाँ link करता है।

## पूरी रूपरेखा

दस चरण, number format क्या है से लेकर किसी और के quantization की समीक्षा करने के विवेक तक। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. Number formats | 0001 से 0003 | Quantization से क्या मिलता है, fp32, fp16, bf16, fp8, int8, int4 और block-scaled formats | Format का bit layout पढ़ सकें और उसमें model का आकार निकाल सकें |
| 2. Quantization की mapping | 0004 से 0006 | Quantize और dequantize, scale और zero point, clipping range चुनना, per-tensor, per-channel और per-group | हाथ से tensor को quantize कर सकें और उसकी error का अनुमान लगा सकें |
| 3. Outliers | 0007 से 0008 | LLMs में outlier features और massive activations, और उनके इलाज के परिवार | बता सकें कि naive int8 LLM क्यों टूटता है और कौन-सा इलाज लागू होता है |
| 4. Post-training weight quantization | 0009 से 0012 | Round-to-nearest, GPTQ, AWQ, calibration set | Model के weights को 4 bits पर quantize कर सकें और बता सकें कि हर method ने क्या बदला |
| 5. Activations और KV cache | 0013 से 0016 | Weight-only बनाम weight-और-activation, SmoothQuant, rotations, KV-cache quantization | तय कर सकें कि weights के अलावा क्या quantize करना है और किस technique से |
| 6. Quantization-aware training | 0017 से 0018 | Fake quantization, straight-through estimator, LLMs के लिए QAT | बता सकें कि PTQ के मुक़ाबले QAT अपनी लागत के लायक़ कब है |
| 7. Hardware और kernels | 0019 से 0020 | Memory-bound बनाम compute-bound, kernel को क्या support करना चाहिए, कौन-सा hardware कौन-सा format चलाता है | अनुमान लगा सकें कि कोई scheme दिए hardware और batch size पर तेज़ चलेगा या नहीं |
| 8. Quality की हानि मापना | 0021 से 0022 | Perplexity और उसकी सीमाएँ, flips, task suites, ईमानदार तुलना | माप सकें कि quantization की क्या क़ीमत चुकानी पड़ी और उस संख्या का बचाव कर सकें |
| 9. File formats | 0023 से 0024 | Quantization configs के साथ safetensors, GGUF quant types और importance matrix | Quantized checkpoint पढ़ सकें और बता सकें कि उसमें क्या store है |
| 10. विवेक | 0025 से 0027 | Scheme चुनना, किसी दावे की समीक्षा, ऐसा quantized model शिप करना जिस पर दूसरे निर्भर हैं, जब आम जवाब ग़लत हो | Quantization पर फ़ैसला लेने और उसे किसी और को समझाने के लिए भरोसेमंद हों |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-what-quantization-buys.md) | Quantization से क्या मिलता है | प्रति parameter कम bits से memory और हर token पर पढ़े जाने वाले bytes घटते हैं, और ज़्यादातर speed यहीं से आती है |
| [0002](lessons/0002-floating-point-formats.md) | Floating-Point Formats | fp32, fp16 और bf16 में sign, exponent और mantissa bits range और precision को कैसे बाँटते हैं |
| [0003](lessons/0003-low-bit-formats.md) | Low-Bit Formats | fp8, int8, int4 और MXFP4 जैसे block-scaled formats क्या represent कर सकते हैं और क्या नहीं |
| [0004](lessons/0004-quantize-and-dequantize.md) | Quantize और Dequantize | Real values से integers तक की affine mapping: scale, zero point, rounding और clamping |
| [0005](lessons/0005-choosing-the-range.md) | Range चुनना | Range को clip करने से थोड़ी clipping error के बदले rounding error बहुत कम क्यों हो जाती है |
| [0006](lessons/0006-granularity.md) | Granularity | Per-tensor, per-channel और per-group scales, और हर एक store किए गए bits में क्या क़ीमत लेता है |
| [0007](lessons/0007-why-llms-have-outliers.md) | LLMs में Outliers क्यों होते हैं | Outlier feature dimensions और massive activations, वे कहाँ दिखते हैं और एक अकेली value पूरे tensor का scale क्यों बिगाड़ देती है |
| [0008](lessons/0008-handling-outliers.md) | Outliers को सँभालना | इलाज के चार परिवार: उन्हें ऊँची precision में रखना, group छोटा करना, उन्हें migrate करना, या rotate करके हटा देना |
| [0009](lessons/0009-round-to-nearest.md) | Round-to-Nearest | Weights को बिना data के एक-एक करके quantize करना, यह 8 bits पर क्यों टिकता है और 4 या उससे कम पर क्यों फिसलता है |
| [0010](lessons/0010-gptq.md) | GPTQ | Layer के weights को क्रम से quantize करना और हर rounding error को अभी quantize न हुए weights पर खर्च करना |
| [0011](lessons/0011-awq.md) | AWQ | बड़ी activations से मिलने वाले weights को rounding से पहले उनके channels को scale करके बचाना |
| [0012](lessons/0012-the-calibration-set.md) | Calibration Set | Method कौन-सा calibration data पढ़ता है, उसे कितना चाहिए, और बेमेल set कैसे दिखता है |
| [0013](lessons/0013-weights-activations-or-both.md) | Weights, Activations या दोनों | Weight-only और weight-और-activation schemes हर एक क्या बचाते हैं, और activations ज़्यादा कठिन क्यों हैं |
| [0014](lessons/0014-smoothquant.md) | SmoothQuant | Per-channel scale से quantization की कठिनाई को activations से weights में खिसकाना |
| [0015](lessons/0015-rotations.md) | Rotations | Orthogonal matrix से गुणा करके outliers को channels में फैलाना ताकि 4-bit activations बच सकें |
| [0016](lessons/0016-kv-cache-quantization.md) | KV-Cache Quantization | Keys और values अलग-अलग axes पर quantize क्यों होते हैं, और लंबे context पर इससे क्या मिलता है |
| [0017](lessons/0017-fake-quantization-and-the-ste.md) | Fake Quantization और STE | Training को quantization कैसे दिखता है: forward pass में simulated rounding, backward pass में straight-through gradient |
| [0018](lessons/0018-qat-for-llms.md) | LLMs के लिए QAT | LLM पर quantization-aware training की क्या लागत आती है, वह क्या वापस लाती है, और PTQ कब काफ़ी है |
| [0019](lessons/0019-what-actually-runs-faster.md) | असल में क्या तेज़ चलता है | Weight-only quantization छोटे batch के decode को तेज़ क्यों करता है और बड़े batch के prefill को धीमा भी कर सकता है |
| [0020](lessons/0020-hardware-and-kernel-support.md) | Hardware और Kernel Support | GPU कौन-से formats में natively compute करता है, कौन-से सिर्फ़ store करता है, और kernel न होने की क्या क़ीमत है |
| [0021](lessons/0021-perplexity-and-its-limits.md) | Perplexity और उसकी सीमाएँ | Perplexity क्या मापती है, छोटा बदलाव बड़ी answer flips क्यों छिपा सकता है, और इसकी जगह क्या मापें |
| [0022](lessons/0022-an-honest-quantization-eval.md) | ईमानदार Quantization Eval | Quantized model की baseline से एक ही harness और tasks पर तुलना करें, और बताएँ कि उसने क्या खोया और कहाँ |
| [0023](lessons/0023-quantized-checkpoints.md) | Quantized Checkpoints | Quantized safetensors checkpoint में क्या store होता है, और उसका quantization config loader को उसे पढ़ना कैसे बताता है |
| [0024](lessons/0024-gguf-quant-types.md) | GGUF Quant Types | Q4_K_M जैसे GGUF type name का मतलब क्या है, और importance matrix क्या बदलती है |
| [0025](lessons/0025-choosing-a-scheme.md) | Scheme चुनना | Model, hardware, batch के आकार और quality की सीमा से format और method चुनें |
| [0026](lessons/0026-reviewing-a-quantization-claim.md) | Quantization के दावे की समीक्षा | "4-bit, quality में कोई हानि नहीं" की समीक्षा यह बताकर करें कि माप ने क्या छिपाया, और ऐसा quantized model roll out करें जिस पर दूसरे निर्भर हैं |
| [0027](lessons/0027-when-the-usual-answer-is-wrong.md) | जब आम जवाब ग़लत हो | पहचानें कि 4-bit weights या कोई मानक नुस्ख़ा कब ग़लत फ़ैसला है, और विवाद का निपटारा मुख्य स्रोत से करें |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत, हर एक के साथ टिप्पणी कि वह क्या कवर करता है
- [Number Formats शीट](reference/number-formats.md): हर format का bit layout, range और precision, और memory का हिसाब, चरण 1 से
- [Quantization Mapping शीट](reference/quantization-mapping.md): quantize और dequantize के formulas, range का चुनाव, granularity और outliers के इलाज, चरण 2 और 3 से
- [Weight PTQ Methods शीट](reference/weight-ptq-methods.md): round-to-nearest, GPTQ और AWQ आमने-सामने, और calibration set क्या करता है, चरण 4 से
- [Activations और KV Cache शीट](reference/activations-and-kv-cache.md): weight-only बनाम weight-और-activation, SmoothQuant, rotations और KV-cache quantization, चरण 5 से
- [QAT और Hardware शीट](reference/qat-and-hardware.md): QAT कैसे काम करता है और कब फ़ायदेमंद है, और scheme को तेज़ क्या बनाता है, चरण 6 और 7 से
- [मापना और Store करना शीट](reference/measuring-and-storing.md): ईमानदार quantization eval, और quantized checkpoint या GGUF type कैसे पढ़ें, चरण 8 और 9 से
- [Quantization Review Checklist शीट](reference/quantization-review-checklist.md): scheme चुनना और किसी और के quantization दावे से पूछने के सवाल, चरण 10 से

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके मुख्य स्रोत तक खंगालना ठीक रहेगा।
