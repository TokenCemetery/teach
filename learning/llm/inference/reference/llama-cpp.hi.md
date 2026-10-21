---
title: "llama.cpp"
description: "GGUF का format और quantization के नाम, ggml का backend abstraction, और serving के GPU से बाहर जाने पर क्या बदलता है"
type: reference
---

# llama.cpp

CPU/edge serving stack। llama.cpp deployment खड़ा करते समय या उसके बारे में सोचते समय खोजने के लिए बनाया गया।

## GGUF

एक अकेली binary file जो weights, tokenizer और architecture metadata को समेटती है, उन कई अलग files (`config.json`, tokenizer, weights) की जगह जिनके रूप में Hugging Face checkpoint आता है। यह समेटना edge deployment के लिए सबसे ज़्यादा मायने रखता है: एक file भेजना जिसे छोटे, कम-dependency वाले binary से चलाया जाए, बिना किसी Python या Hugging Face ecosystem के install किए जो हिस्सों को दोबारा जोड़े।

क्योंकि GGUF weights को ऐसे format में रखता है जिसे OS सीधे पढ़ सकता है, llama.cpp file को उत्सुकता से RAM में पढ़ने और deserialize करने के बजाय **memory-map** (`mmap`) कर सकता है। Pages disk से तभी पढ़े जाते हैं जब कोई उन्हें छुए, और क्या resident रहे यह OS का अपना page cache सँभालता है। यह वहाँ सबसे ज़्यादा मायने रखता है जहाँ RAM सबसे तंग संसाधन है, यानी CPU और edge hardware, भरपूर system RAM वाले GPU server पर कम।

### Quantization के नाम

GGUF llama.cpp का अपना quantization परिवार ढोता है, GPU-उन्मुख GPTQ और AWQ से अलग। `Q4_K_M` जैसे नाम को खोलना:

| हिस्सा | मतलब |
|---|---|
| `Q4` | Bit width: लगभग 4 bits प्रति weight (`Q5`, `Q8` और दूसरे भी) |
| `K` | **k-quant** प्रकार: प्रति tensor एक bit width, 256 weights के super-blocks के साथ जिनके हर sub-block का अपना scale होता है |
| `M` | वह नुस्ख़ा जो tensors में प्रकार मिलाता है, कुछ tensors को ऊँची-bit का प्रकार देता है: `S` (छोटा), `M` (मध्यम), `L` (बड़ा)। देखें [quantization ट्रैक की मापना और सहेजना शीट](../../quantization/reference/measuring-and-storing.md) |

## ggml: एक codebase, कई backends

llama.cpp **ggml** पर बना है, जो बिना dependencies की C tensor library है (कोई बाहरी BLAS ज़रूरी नहीं)। Forward pass एक static computation graph है, जो एक बार बनता है और फिर चलता है, PyTorch के operation-दर-operation eager execution की जगह। "क्या compute करना है" को "उसे क्या चलाता है" से यह अलगाव ही उसी graph को कई **backends**, CPU (AVX2/NEON), CUDA, Metal, Vulkan, को लक्ष्य करने देता है, एक ही codebase से, बिना Python runtime के, फ़ोन के ARM CPU से लेकर Mac के Metal GPU और Raspberry Pi तक के hardware पर। इसके उलट vLLM का design CUDA-विशिष्ट है और NVIDIA GPU के बिना चल नहीं सकता।

## GPU batching की जगह threads लेते हैं

| | क्या फैलाता है | किससे बँधा है |
|---|---|---|
| GPU batching (`--max-num-seqs`) | Memory-bandwidth की लागत को concurrent sequences में | Cache capacity और latency budget |
| CPU threads (`--threads`) | एक sequence के अपने matrix multiplies को cores में | CPU का physical core count |

Threading एक sequence के अपने compute को तेज़ करती है; उसके पास "memory पढ़ने की लागत तो वैसे भी चुकानी है" जैसा कुछ नहीं है जिसे GPU batching की तरह अजनबियों की requests में बाँटा जा सके।

## Server खड़ा करना

```text
llama-server -m model.Q4_K_M.gguf --threads 8
```

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "model.Q4_K_M.gguf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

[vLLM शीट](vllm.md) जैसा ही OpenAI-compatible request का आकार; जो बदलता है वह उसके नीचे की हर चीज़ है।

## GPU से बाहर क्या बदलता है

| तंत्र | GPU पर (vLLM) | CPU/edge के पैमाने पर (llama.cpp) |
|---|---|---|
| Concurrency | [Batching शीट](batching.md) वाली continuous batching memory bandwidth को सैकड़ों concurrent अजनबियों की requests में बाँटती है | मुट्ठी भर parallel slots (इकाई अंकों से कुछ दर्जन); आम edge workload, एक device जो अपने user को serve करता है, में batch करने को सैकड़ों concurrent requests शायद ही कभी होती हैं |
| Cache management | [PagedAttention का तंत्र](vllm.md#pagedattention) एक बड़े, लगातार बदलते साझा pool को सँभालता है | प्रति-sequence सादा, सटा हुआ cache काफ़ी है; जिस समस्या को PagedAttention हल करता है वह शायद ही कभी उस पैमाने तक पहुँचती है जहाँ उसकी जटिलता फल दे |
| Quantization का समय | Serve-time का flag (`--quantization`), launch के समय चुना गया | तभी तय हो चुका जब कोई ख़ास GGUF quant स्तर चुना या बनाया गया; उसे बदलने का मतलब दूसरी file इस्तेमाल करना है, flag नहीं |

Trade-offs ख़ुद ([memory, speed और accuracy](quantization-at-serve-time.md)) वही रहते हैं; सिर्फ़ यह बदलता है कि हर फ़ैसला कब होता है, और किस concurrency पर फल देता है।

## संबंधित

- [पाठ 13](../lessons/0013-gguf.md), [पाठ 14](../lessons/0014-llamacpp-architecture.md), [पाठ 15](../lessons/0015-what-changes-off-gpu.md)
- [vLLM शीट](vllm.md), [Batching शीट](batching.md), [Serve Time पर Quantization शीट](quantization-at-serve-time.md): GPU-पक्ष के वे तंत्र जिनसे यह शीट तुलना करती है
