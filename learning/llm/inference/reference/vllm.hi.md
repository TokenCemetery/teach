---
title: "vLLM"
description: "vLLM खड़ा करना, चरण 1-3 की अवधारणाओं को ढोने वाले flags, PagedAttention की block table, और लक्षण से knob तक की फ़ैसला-प्रक्रिया"
type: reference
---

# vLLM

GPU serving stack। server खड़ा करते या tune करते समय खोजने के लिए बनाया गया।

## Server खड़ा करना

```bash
pip install vllm
vllm serve meta-llama/Llama-2-7b-hf
```

Port 8000 पर OpenAI-compatible HTTP server शुरू करता है। Request किसी भी OpenAI chat completion call जैसी दिखती है:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "meta-llama/Llama-2-7b-hf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

Request का `"model"` field उस model से मेल खाना चाहिए जिससे server शुरू हुआ था।

## वे flags जो चरण 1-3 का अंकगणित ढोते हैं

| Flag | क्या ढोता है |
|---|---|
| `--max-num-seqs` | वह batch size सीमा जिसका [latency budget के विरुद्ध बचाव](batching.md#defending-a-configuration) होता है |
| `--kv-cache-dtype` | [Cache की precision](kv-cache.md#cache-precision-is-a-lever-independent-of-the-models-own-weights), जैसे `fp8`, model के अपने weight precision से स्वतंत्र |
| `--quantization` | वह scheme (`gptq`, `awq`, ...) जो पहले से quantized checkpoint के लिए [चुनी और बचाव की गई](quantization-at-serve-time.md) |

Continuous batching और chunked prefill default रूप से चालू हैं; बुनियादी तंत्र को बंद करने का कोई flag नहीं है, सिर्फ़ उसके आसपास tune करने वाले हैं (जैसे chunk size)। `--quantization` छोड़ने पर checkpoint उसी precision में serve होता है जिसमें वह सहेजा गया था, सबसे आम तौर पर fp16 या bf16; load पर कुछ भी quantize नहीं होता।

<a id="pagedattention"></a>

## PagedAttention

हर sequence का cache निश्चित आकार के **blocks** में बँटा होता है (default रूप से 16 tokens); हर sequence की **block table** logical token positions को physical block locations से जोड़ती है, OS page table वाला ही विचार।

**Block size एक trade-off है:**

| Block size | आख़िरी, आंशिक रूप से भरे block में बरबाद जगह | Block-table bookkeeping |
|---|---|---|
| बड़ा | ज़्यादा | कम |
| छोटा | कम | ज़्यादा |

**हल किया उदाहरण**: 16-token के block size पर 40-token का sequence `ceil(40/16) = 3` blocks इस्तेमाल करता है; तीसरे में 8 tokens हैं और बाक़ी 8 slots बरबाद हैं।

**Block sharing**: दो sequences की block tables एक ही physical block की ओर तब इशारा कर सकती हैं जब सामग्री एक जैसी हो, सबसे आम तौर पर साझा prompt prefix। Parallel sampling और beam search सबसे साफ़ मामले हैं: हर sample की table उन्हीं prompt blocks की ओर इशारा करती है जब तक किसी sample का अपना generate हुआ token अलग न हो जाए, उसी बिंदु पर **copy-on-write** सिर्फ़ उसी sample को उस block की निजी copy देता है जिसे बदला जा रहा है।

**हल किया उदाहरण**, उसी 200-token के prompt के 10 parallel samples, 16-token के blocks: एक copy को `ceil(200/16) = 13` blocks चाहिए। साझा किए बिना: `13 × 10 = 130` blocks। साझा करने पर: 13 blocks, जब तक कोई sample अलग होना शुरू न करे।

## दो और tuning knobs

| Flag | क्या नियंत्रित करता है | Trade-off |
|---|---|---|
| `--gpu-memory-utilization` | GPU की memory का वह हिस्सा जो vLLM weights, cache और अपने overhead के लिए इस्तेमाल कर सकता है (default ~0.9) | उसे 1.0 की ओर बढ़ाने से cache की capacity सीमा बढ़ती है पर उसी GPU को साझा करने वाली किसी और चीज़ के लिए गुंजाइश घटती है |
| `--tensor-parallel-size` | Model के weights और compute को कई GPUs में बाँटता है | Model को सिकोड़ने के बजाय फैलाता है (quantization के उलट, accuracy की कोई क़ीमत नहीं); जब कोई अकेला काफ़ी न हो तो quantization के साथ जोड़ा जा सकता है |

`--gpu-memory-utilization` [capacity सीमा वाले formula](kv-cache.md#capacity-budget) में "total memory" का मतलब बदल देता है: ~0.9 के default पर 80 GB GPU पर formula को सिर्फ़ ~72 GB इस्तेमाल करना चाहिए, 80 GB नहीं।

## लक्षण से knob तक

| लक्षण | क्या जाँचें |
|---|---|
| शुरू नहीं होता, या cache के लिए बहुत कम memory बताता है | पहले `--gpu-memory-utilization`; अगर 100% पर भी नहीं समाता, तो वह [memory-बाधित मामला](quantization-at-serve-time.md#picking-a-scheme-name-the-binding-constraint-first) है: quantize करें, `--tensor-parallel-size` जोड़ें, या दोनों |
| Decode latency budget से धीमा है | `--max-num-seqs` को [बचाव किया गया batch size](batching.md#the-throughputlatency-trade-off) के विरुद्ध, फिर यह कि weights या `--kv-cache-dtype` को quantize करना नापी गई संख्याओं से सही ठहरता है या नहीं |
| एक request हर दूसरे sequence के tokens को रोक देती है | [head-of-line blocking की समस्या](batching.md#admission-order-and-head-of-line-blocking): chunked-prefill का chunk size जाँचें, batch size नहीं |
| एक ही prompt के parallel samples में memory बरबाद दिखती है | ऊपर की block sharing: batch size या memory utilization छूने से पहले जाँचें कि वह सचमुच हो रही है |

## संबंधित

- [पाठ 10](../lessons/0010-standing-up-vllm.md), [पाठ 11](../lessons/0011-pagedattention.md), [पाठ 12](../lessons/0012-vllm-tuning-knobs.md)
- [KV Cache शीट](kv-cache.md), [Batching शीट](batching.md), [Serve Time पर Quantization शीट](quantization-at-serve-time.md): वे अवधारणाएँ जिन्हें ये flags ढोते हैं
