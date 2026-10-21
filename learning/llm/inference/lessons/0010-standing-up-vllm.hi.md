---
title: "10. vLLM खड़ा करना"
description: "vLLM install करना, उसका server launch करना, और वे flags ढूँढना जो पहले सिखाई जा चुकी अवधारणाओं को ढोते हैं"
type: lesson
---

# पाठ 10. vLLM खड़ा करना

**मिशन से संबंध:** चरण 1 से 3 का हर formula, cache footprint, batch size, quantization scheme, इस पाठ में असली command पर असली flag बन जाता है; यही वह जगह है जहाँ अंकगणित requests का जवाब देने वाले server में बदलता है।
**मुख्य स्रोत:** [दस्तावेज़: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**पूर्व-आवश्यकताएँ:** [पाठ 9](0009-picking-a-quantization-scheme.md), [KV cache](../GLOSSARY.md)

## वार्म-अप

1. ▢ Server मौजूदा batch size पर अपने latency budget से ऊपर है। पाठ 6 के तर्क से, सबसे पहले कौन-सा flag जाँचना है?

<details markdown="1"><summary>जाँचें</summary>

अधिकतम batch size की setting: वह सबसे बड़ा batch size जो अब भी latency budget पूरा करता है, वही पाठ 6 ने बचाव के लिए तय किया था, इसलिए वही knob उसे सीधे नियंत्रित करता है।

</details>

2. ▢ KV cache के लिए model के अपने weight precision के बजाय fp8 इस्तेमाल करने का serving-time चुनाव कभी समझदारी क्यों हो सकता है (पाठ 3)?

<details markdown="1"><summary>जाँचें</summary>

Cache की precision model के अपने weight precision से स्वतंत्र उपाय है। Cache का `bytes_per_value` आधा करने से उसका footprint सीधे आधा हो जाता है, model में कोई बदलाव किए बिना, और capacity वैसे ही वापस मिलती है जैसे छोटा model देता।

</details>

## यह जानें

### vLLM install करना

vLLM एक Python package के रूप में install होता है, `pip install vllm`, और उसे CUDA-सक्षम GPU चाहिए; यह इस workspace के मिशन का GPU वाला आधा हिस्सा है, जबकि CPU और edge को आगे वाले चरण में llama.cpp कवर करता है। आम configurations के लिए install अपने आप मेल खाता PyTorch और CUDA toolchain खींच लेता है, जिसे install हुए CUDA driver version से मिलाकर देखना ठीक रहेगा, इससे पहले कि आप मानें कि फ़ेल हुआ install कोई और बात है।

### Server launch करना

`vllm serve <model>` नामित model (local path या Hugging Face Hub का identifier) के लिए OpenAI-compatible HTTP server शुरू करता है, जो default रूप से port 8000 पर सुनता है:

```text
vllm serve meta-llama/Llama-2-7b-hf
```

यह अकेली command download (ज़रूरत हो तो), weight loading और server startup करती है, जिनके memory और latency नतीजों के बारे में चरण 1 से 3 की हर चीज़ तर्क कर रही थी।

### Request भेजना

क्योंकि server OpenAI API के आकार में बोलता है, request किसी भी OpenAI chat completion call जैसी दिखती है, बस local server की ओर निशाना साधे हुए:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "meta-llama/Llama-2-7b-hf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

### जहाँ पहले सिखाई अवधारणाएँ flags के रूप में दिखती हैं

Command line वह जगह है जहाँ चरण 1 से 3 अंकगणित से configuration बन जाते हैं:

- `--max-num-seqs`: वह batch size सीमा जिसका latency budget के विरुद्ध बचाव करना पाठ 6 ने सिखाया।
- `--kv-cache-dtype`: वह cache precision जिसे पाठ 3 ने model के अपने weights से स्वतंत्र उपाय के रूप में बताया (उदाहरण के लिए, `fp8`)।
- `--quantization`: उस scheme का नाम बताता है, जैसे `gptq` या `awq`, जिसे चुनना और जिसका बचाव करना पाठ 7 से 9 ने सिखाया, जब पहले से quantized checkpoint serve किया जा रहा हो।
- Continuous batching और chunked prefill (पाठ 4 और 5) default रूप से चालू हैं; बुनियादी तंत्र को बंद करने का कोई flag नहीं है, सिर्फ़ उसके आसपास tune करने वाले हैं, जैसे chunk size।

## अभ्यास

1. ▢ एक team `vllm serve some-model --max-num-seqs 32 --kv-cache-dtype fp8` चलाती है। पाठ 6 और 3 के हिसाब से, इन दोनों flags में से हर एक असल में क्या नियंत्रित करता है?

<details markdown="1"><summary>जाँचें</summary>

`--max-num-seqs 32` batch size को 32 पर सीमित करता है, वह संख्या जिसका बचाव पाठ 6 बताए गए latency budget और पाठ 2 की capacity सीमा के विरुद्ध करता। `--kv-cache-dtype fp8` KV cache को default की जगह fp8 में रखता है, उसका प्रति-token footprint आधा कर देता है, model के अपने weight precision से स्वतंत्र, ठीक वही उपाय जो पाठ 3 ने बताया।

</details>

2. ▢ एक team `vllm serve some-model` से server शुरू करती है, कोई `--quantization` flag दिए बिना। Server model को किस precision पर serve करता है, और क्यों?

<details markdown="1"><summary>जाँचें</summary>

जिस precision में checkpoint ख़ुद सहेजा गया था, सबसे आम तौर पर fp16 या bf16, क्योंकि कोई quantization scheme माँगी ही नहीं गई। `--quantization` तभी लागू होता है जब ऐसा checkpoint serve हो जो पहले से quantize किया गया हो या जिसे flag vLLM को load पर quantize करने को कहे; उसे छोड़ने का मतलब है कुछ भी quantize नहीं हुआ।

</details>

3. ▢ जाँचने से पहले अनुमान लगाएँ: `vllm serve` सफलतापूर्वक चलाने के बाद, इस पाठ के यह जानें खंड की curl request में से वह एक जानकारी कौन-सी है जिसे server जिससे शुरू हुआ था उससे मेल खाना ही चाहिए, वरना request फ़ेल हो जाएगी?

<details markdown="1"><summary>संकेत</summary>

Curl command में `"model"` field देखें।

</details>

<details markdown="1"><summary>जाँचें</summary>

Request body का `"model"` field उस model के नाम (या path) से मेल खाना चाहिए जिससे server शुरू हुआ था। Server एक समय में एक model serve कर रहा है; request में किसी और का नाम देना ही वह चीज़ है जो अन्यथा सही बनी call पर सबसे आम तौर पर error देती है।

</details>

4. ▢ जब कोई batching या cache flag न दिया गया हो तब vLLM के default व्यवहार के बारे में कौन-सा दावा सही है?

    - a) `--max-num-seqs` सेट होने तक वह static batching पर लौट आता है
    - b) Continuous batching और chunked prefill default रूप से चलते हैं; flags सिर्फ़ उन्हें और tune करते हैं
    - c) जब तक KV cache dtype साफ़ चुना न जाए वह शुरू होने से इनकार कर देता है
    - d) वह default रूप से hardware जो सबसे कम precision support करता है उस पर serve करता है

<details markdown="1"><summary>जाँचें</summary>

**b)** Continuous batching और chunked prefill default तंत्र हैं, कोई flag उन्हें चालू नहीं करता; उपलब्ध flags उनके आसपास के parameters tune करते हैं, जैसे अधिकतम batch size या chunk size। (a) ग़लत है: static-batching पर लौटना जैसा कुछ नहीं है। (c) ग़लत है: कोई नाम न दिया जाए तो default cache dtype इस्तेमाल होता है। (d) ग़लत है: default checkpoint की अपनी सहेजी हुई precision है, hardware जो सबसे कम support करता है वह नहीं।

</details>

## असली दुनिया का अभ्यास

- [ ] CUDA-सक्षम GPU वाली machine पर vLLM install करें (`pip install vllm`), और कोई छोटा model जिसे आप download कर सकें उसके साथ `vllm serve` चलाएँ।
- [ ] इस पाठ की curl request अपने चलते server के विरुद्ध भेजें, और पुष्टि करें कि आपको असली completion वापस मिलता है, error नहीं।
- [ ] कल: server को `--max-num-seqs` छोटी संख्या (जैसे 2) और बड़ी संख्या पर सेट करके दोबारा शुरू करें, और देखें कि कुछ concurrent requests के तहत उसके व्यवहार में कोई फ़र्क़ दिखता है या नहीं।

## आगे बढ़ने के लिए

- [दस्तावेज़: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
