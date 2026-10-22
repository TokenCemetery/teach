---
title: "Activations और KV Cache"
description: "Weight-only बनाम weight-और-activation, SmoothQuant, rotations और KV-cache quantization, देखने के लिए"
type: reference
---

# Activations और KV Cache: Weights से आगे Quantize करना

चरण 5 का संक्षेप, देखने के लिए। [पाठ 13](../lessons/0013-weights-activations-or-both.md) weight-only बनाम weight-और-activation बताता है, [पाठ 14](../lessons/0014-smoothquant.md) SmoothQuant, [पाठ 15](../lessons/0015-rotations.md) rotations, और [पाठ 16](../lessons/0016-kv-cache-quantization.md) KV-cache quantization।

## Weights, activations या दोनों

| Scheme | छोटा store होता है | Matmul चलता है | क्या मिलता है | कहाँ फिट |
|---|---|---|---|---|
| W4A16, W8A16 (weight-only) | Weights | 16-bit में, kernel में dequantize करने के बाद | Memory, प्रति token पढ़े गए bytes | Memory-bound: छोटे batch का decode |
| W8A8 int8 या fp8 | Weights और activations | 8-bit में | Arithmetic throughput, साथ में memory | Compute-bound: prefill, बड़े batches |
| Rotations के साथ W4A4 | Weights, activations, अक्सर KV | 4-bit में | Memory और arithmetic | सिर्फ़ जहाँ 4-bit kernel है, पाठ 20 देखें |

Kurtic et al. (Llama 3.1 परिवार, पाँच लाख से ज़्यादा evaluations): fp8 W8A8 व्यावहारिक रूप से lossless, अच्छी तरह tune किया int8 W8A8 में 1 से 3% गिरावट, W4A16 int 8-bit की बराबरी करता है। सलाह: synchronous serving के लिए W4A16, continuous batching के लिए W8A8।

## Activations मुश्किल क्यों हैं

| गुण | Weights | Activations |
|---|---|---|
| Range का पता | Training के बाद, तय | सिर्फ़ run time पर |
| Outliers | समतल, quantize करना आसान | ज़्यादातर values का लगभग 100 गुना, सभी tokens में तय channels में (SmoothQuant) |
| int8 GEMM जो scale granularity देता है | Per output channel | सिर्फ़ per tensor या per token |

int8 GEMM: `Y = diag(s_X) · (X_int8 @ W_int8) · diag(s_W)`। Scales सिर्फ़ बाहरी dimensions पर बैठते हैं; per-input-channel scale योग के अंदर बैठेगा।

| Activation scale | कब compute होता है | लागत | जोखिम |
|---|---|---|---|
| Static | Offline, calibration set से | प्रति request कुछ नहीं | Calibration set असली traffic जैसा नहीं |
| Dynamic | Run time पर, tensor से | हर matmul से पहले एक reduction | थोड़ा; हर input के हिसाब से ढलता है |

## SmoothQuant

```text
X @ W = (X @ diag(s)^-1) @ (diag(s) @ W)
s_j   = max(|X_j|)^α / max(|W_j|)^(1 - α)
```

| `α` | असर |
|---|---|
| 0 | Activations अपरिवर्तित |
| 0.5 | पेपर का संतुलित default, OPT और BLOOM के लिए सबसे अच्छा बिंदु |
| बड़ा, 1 की ओर | ज़्यादा कठिनाई weights में; भारी outliers वाले models के लिए, जैसे GLM-130B |
| 1 | हर activation channel का अधिकतम बराबर; weights सारे outliers उठाते हैं |

- `max(|X_j|)` calibration set से आता है।
- गुणक `X` बनाने वाली layer में offline जोड़ दिया जाता है: run time पर कोई लागत नहीं।
- एक 8-bit method: पेपर में 1.56 गुना तक speed-up और 2 गुना memory की कमी।

## Rotations

```text
X @ W = (X @ Q) @ (Q.T @ W)      where Q @ Q.T = I
```

| बिंदु | ब्योरा |
|---|---|
| क्या करता है | Outlier को सभी channels में फैलाता है; max, RMS के क़रीब |
| आम `Q` | Randomized Hadamard: entries ±1/sqrt(n), लागत `n log n` |
| Offline जोड़ा जाता है | Residual stream का rotation, weights में |
| Online | FFN down-projection से पहले; queries और keys पर head-wise, RoPE के बाद |
| QuaRot | सभी weights, activations और KV cache 4 bits में; Llama 2 70B WikiText-2 perplexity में 0.47 के भीतर, zero-shot का 99% |
| SpinQuant | Random rotations में zero-shot पर 13 अंक तक का फ़र्क़; सीखे हुए rotations Llama 2 7B W4A4KV4 पर फ़र्क़ 2.9 अंक तक घटाते हैं |

किसी भी W4A4 दावे के लिए समीक्षा का सवाल: कौन-सा rotation, और क्या उसे इसी model के लिए चुना या सीखा गया था?

## KV-cache quantization

```text
KV bytes per token = 2 x layers x kv_heads x head_dim x bytes_per_value
```

Llama 3 8B (32 layers, 8 KV heads, dimension 128) bf16 में: प्रति token 128 KiB, 32,768-token sequence के लिए 4 GiB।

| Tensor | किस axis पर quantize करें | क्यों |
|---|---|---|
| Keys | Per channel, जहाँ संभव हो RoPE से पहले | कुछ तय outlier channels (KIVI); RoPE channel जोड़ियों को मिलाता है (KVQuant) |
| Values | Per token | कोई channel pattern नहीं; per channel की तुलना में attention-output error लगभग 15 गुना कम (KIVI) |

| Method या विकल्प | Bits | बताया गया नतीजा |
|---|---|---|
| KIVI | 2 | लगभग वही quality, peak memory 2.6 गुना कम, batch 4 गुना तक, throughput 2.35 से 3.47 गुना |
| KVQuant | 3 | Perplexity में 0.1 से कम गिरावट; एक 80 GB A100 पर 1M context में LLaMA-7B |
| vLLM fp8 KV cache | 8 | Per-tensor या per-head scales; calibration के बिना default scales 1.0, calibration की सलाह |

KIVI सबसे नए tokens (इसके प्रयोगों में 128) को पूरी precision में रखता है जब तक keys का per-channel group पूरा न हो जाए।
