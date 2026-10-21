---
title: "KV Cache"
description: "KV cache का bytes का हिसाब, प्रति-token लागत, head sharing, request के दौरान बढ़त, और capacity planning"
type: reference
---

# KV Cache

KV cache के लिए bytes का हिसाब। deployment का आकार तय करते समय खोजने के लिए बनाया गया।

## प्रति-token लागत

```text
bytes per token = 2 (K and V) × num_layers × num_kv_heads × head_dim × bytes_per_value
```

`head_dim = d_model / num_heads`। Cache हर **KV head** के लिए एक K/V जोड़ी रखता है, हर query head के लिए नहीं। Multi-head attention (MHA) में `num_kv_heads = num_heads` होता है और यह `2 × num_layers × d_model × bytes_per_value` पर आ जाता है। Grouped-query attention (GQA) या multi-query attention (MQA) में `num_kv_heads` छोटा होता है और cache उसी अनुपात में सिकुड़ता है, मुफ़्त में, context length या batch size में कोई बदलाव किए बिना।

| Scheme | `num_kv_heads` | Cache का सापेक्ष आकार |
|---|---|---|
| MHA | `num_heads` के बराबर | 1x |
| GQA | `num_heads` का एक अंश | वही अंश |
| MQA | 1 | `1 / num_heads` |

**हल किया उदाहरण, Llama-2-70B** (80 layers, 64 query heads, 8 KV heads, `head_dim` = 128, fp16):

```text
GQA: 2 × 80 × 8  × 128 × 2 bytes =   327,680 bytes ≈ 320 KB/token
MHA: 2 × 80 × 64 × 128 × 2 bytes = 2,621,440 bytes ≈ 2.5 MB/token   (8x GQA, the num_heads:num_kv_heads ratio)
```

## कुल footprint में बढ़ना

```text
total cache bytes = bytes per token × context length × batch size
```

| Model | प्रति token | Context | Batch | कुल |
|---|---|---|---|---|
| Llama-2-7B, MHA, fp16 | 512 KB | 4096 | 1 | ~2 GB |
| Llama-2-7B, MHA, fp16 | 512 KB | 4096 | 16 | ~32 GB |
| Llama-2-70B, GQA, fp16 | 320 KB | 4096 | 1 | ~1.25 GB |
| Llama-2-70B, GQA, fp16 | 320 KB | 4096 | 32 | ~40 GB |

<a id="capacity-budget"></a>

## Capacity budget

```text
max concurrent sequences = (total memory - weights - overhead) / (bytes per token × context length)
```

Llama-2-70B, चार 80 GB GPUs पर tensor-parallel (320 GB का pool), weights और framework overhead 160 GB नापे गए, 4096-token context:

```text
160 GB / 1.25 GB per sequence ≈ 128 concurrent sequences
```

वही सीमा, model का कच्चा throughput नहीं, आम तौर पर वह चीज़ है जिससे batching scheduler को सौदा करना पड़ता है; देखें [Batching शीट](batching.md)।

## Prefill footprint का ज़्यादातर हिस्सा एक ही step में माँग लेता है

| चरण | क्या करता है | Cache की बढ़त |
|---|---|---|
| Prefill | पूरे prompt को एक forward pass में process करता है | तुरंत `bytes per token × prompt length` पर कूदता है; compute-bound |
| Decode | एक बार में एक output token generate करता है | हर step में `bytes per token` बढ़ता है; memory-bandwidth bound |

**हल किया उदाहरण**, 2048-token का prompt और उसके बाद 128 decode steps, Llama-2-70B 320 KB/token पर:

```text
prefill: 320 KB × 2048 ≈ 640 MB   (94% of the request's final cache)
decode:  320 KB × 128  ≈  40 MB   (6%, added gradually)
total:   680 MB
```

सिर्फ़ "अंतिम context length" से बनी capacity plan यह छिपा देती है कि footprint का ज़्यादातर हिस्सा prefill पर, एक ही step में, आता है, request में फैला हुआ नहीं।

<a id="cache-precision-is-a-lever-independent-of-the-models-own-weights"></a>

## Cache की precision model के अपने weights से स्वतंत्र उपाय है

ऊपर का `bytes_per_value` उस precision से मेल खाना ज़रूरी नहीं जिसमें model compute करता है। Serving stack cache को ख़ुद कम precision में सहेज सकती है, आम तौर पर fp8, जबकि model bf16 या fp16 में compute करता है। यह head sharing की जगह लेने के बजाय उसके साथ गुणात्मक रूप से जुड़ता है।

```text
Llama-2-70B, GQA, fp16: 320 KB/token
Llama-2-70B, GQA, fp8:  160 KB/token   (half, only bytes_per_value changed)
```

4096-token context पर 64 sequences: fp16 की लागत ~80 GB है, fp8 की ~40 GB, ठीक आधी, उसके ऊपर जो GQA पहले ही पूरे MHA से वापस दिला चुका है।

## संबंधित

- [पाठ 1](../lessons/0001-the-kv-cache.md), [पाठ 2](../lessons/0002-capacity-and-batch-size.md), [पाठ 3](../lessons/0003-growth-prefill-decode-precision.md)
- [Batching शीट](batching.md): यह शीट जो capacity सीमा निकालती है वह असल में किसे बाँधती है
