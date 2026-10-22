---
title: "3. Growth, Prefill, Decode और Precision"
description: "Prefill और decode के दौरान cache कैसे बढ़ता है, और उसकी precision घटाने से क्या वापस मिलता है"
type: lesson
---

# पाठ 3. Growth, Prefill, Decode और Precision

**मिशन से संबंध:** Latency budget इस पर निर्भर करता है कि request के दौरान cache memory कब माँगी जाती है, सिर्फ़ उसके अंतिम आकार पर नहीं, और इस पर भी कि batch और context length के अलावा server के पास उस आकार पर और कौन-से उपाय हैं।
**मुख्य स्रोत:** [दस्तावेज़: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**पूर्व-आवश्यकताएँ:** [पाठ 2](0002-capacity-and-batch-size.md), [KV cache](../GLOSSARY.md)

## वार्म-अप

1. ▢ बताएँ कि batch का कुल KV cache footprint bytes per token, context length और batch size के रूप में किस formula से निकलता है।

<details markdown="1"><summary>जाँचें</summary>

`total cache bytes = bytes per token × context length × batch size`।

</details>

2. ▢ Grouped-query attention इस्तेमाल करने वाले model का KV cache पूरे multi-head attention वाले उसी model से छोटा क्यों होता है?

<details markdown="1"><summary>जाँचें</summary>

Cache हर KV head के लिए एक key/value जोड़ी रखता है, हर query head के लिए नहीं, और GQA query heads से कम KV heads इस्तेमाल करता है। Cache `num_kv_heads` के साथ बढ़ता है, जिसे पूरा MHA `num_heads` के बराबर रखता है।

</details>

## यह जानें

### Cache एक स्थिर दर से नहीं बढ़ता

Request के दो चरण होते हैं, और वे cache memory को बहुत अलग ढंग से माँगते हैं।

**Prefill** पूरे prompt को एक forward pass में process करता है: prompt के हर token के key और value vectors एक ही step में साथ compute होकर cache हो जाते हैं। Model के एक भी output token generate करने से पहले cache खाली से `bytes per token × prompt length` पर कूद जाता है। यह चरण compute-bound है: यह पूरे prompt पर एक बड़ा, parallel matrix multiplication है।

**Decode** फिर एक बार में एक output token generate करता है। हर step ठीक एक और token के keys और values compute और cache करता है, इसलिए cache हर step में `bytes per token` बढ़ता है, तुलना में एक धीमी बूँद-बूँद। यह चरण memory-bandwidth bound है: हर step को attend करने के लिए पूरा cache वापस पढ़ना पड़ता है, सिर्फ़ एक नए token जितने नए काम के लिए।

इसलिए लंबा prompt request के अंतिम cache footprint का ज़्यादातर हिस्सा तुरंत, prefill पर ही माँग लेता है, जबकि decode बाक़ी धीरे-धीरे जोड़ता है। जो capacity plan सिर्फ़ "अंतिम context length" देखता है, वह असल में पूछ रहा है कि "prefill के बाद, और जितने decode steps मैं उम्मीद करता हूँ उनके बाद, यह कितना बड़ा होगा", और दोनों चरण बहुत अलग समय-सारणी पर योगदान देते हैं।

![समय के साथ cache के आकार का चार्ट: cache अकेले prefill step के दौरान लगभग सीधा ऊपर कूदता है, फिर decode के दौरान धीमी, स्थिर सीढ़ी की तरह चढ़ता है क्योंकि हर output token एक और token जितना cache जोड़ता है। 2048-token का prompt prefill पर लगभग 640 MB माँगता है, जबकि 128 decode steps सिर्फ़ लगभग 40 MB और जोड़ते हैं, यानी कुल का 6%।](images/prefill-decode-cache-growth.svg)

### Model के अपने weights से स्वतंत्र एक उपाय: cache की precision

पाठ 2 के formula में `bytes_per_value` अपना अलग पद था, `num_layers`, `num_kv_heads` और `head_dim` से अलग। उस पद का उस precision से मेल खाना ज़रूरी नहीं जिसमें model compute करता है। Serving stack KV cache को ख़ुद कम precision में सहेज सकती है, आम तौर पर fp8, जबकि model अब भी bf16 या fp16 में compute करता है। `bytes_per_value` को 2 bytes से 1 कर देने पर cache का footprint सीधे आधा हो जाता है, `num_kv_heads` में कोई बदलाव किए बिना, context length में कोई बदलाव किए बिना, और बिना retraining के: यह serving-time का चुनाव है, इससे स्वतंत्र कि weights किस precision पर quantize हुए थे।

यह पाठ 2 की हर चीज़ के साथ जुड़कर काम करता है। Llama-2-70B की संख्याएँ फिर लें (80 layers, 8 KV heads, `head_dim` = 128): fp16 पर प्रति-token लागत 320 KB थी। fp8 पर यह `2 × 80 × 8 × 128 × 1 byte = 163,840 bytes ≈ 160 KB` है, ठीक आधी, क्योंकि सिर्फ़ `bytes_per_value` बदला।

## अभ्यास

1. ▢ एक request का prompt 2048 tokens का है। Llama-2-70B के fp16 आँकड़े, 320 KB प्रति token, से निकालें कि कोई भी output token generate होने से पहले अकेला prefill कितना cache माँगता है।

<details markdown="1"><summary>जाँचें</summary>

`320 KB × 2048 ≈ 640 MB`, अकेले prefill step में माँगा गया।

</details>

2. ▢ वही request फिर decode से 128 output tokens generate करती है। Decode कितना अतिरिक्त cache जोड़ता है, और यह request के कुल अंतिम cache का कौन-सा हिस्सा है?

<details markdown="1"><summary>संकेत</summary>

Decode `bytes per token × decode steps की संख्या` जोड़ता है। उसकी तुलना प्रश्न 1 के prefill आँकड़े से करें।

</details>

<details markdown="1"><summary>जाँचें</summary>

Decode से `320 KB × 128 ≈ 40 MB` जुड़ा। कुल cache `640 MB + 40 MB = 680 MB` है, इसलिए decode कुल का सिर्फ़ लगभग 6% है; बाक़ी 94% prefill ने एक ही step में माँग लिया।

</details>

3. ▢ Llama-2-70B के fp8 cache आँकड़े, 160 KB प्रति token, से 4096-token context पर 64 sequences के batch का कुल cache footprint निकालें।

<details markdown="1"><summary>संकेत</summary>

`total cache bytes = bytes per token × context length × batch size`, वार्म-अप वाला ही formula।

</details>

<details markdown="1"><summary>जाँचें</summary>

`160 KB × 4096 × 64 = 41,943,040 KB ≈ 40 GB`।

</details>

4. ▢ उसी batch का fp16 रूप (प्रश्न 3, पर 320 KB प्रति token) कितना cache लेगा, और यह तुलना head-sharing वाले बदलाव के ऊपर precision का बदलाव जोड़ने के बारे में क्या दिखाती है?

<details markdown="1"><summary>जाँचें</summary>

`320 KB × 4096 × 64 ≈ 80 GB`, ठीक दोगुना। fp8 cache footprint को उसके ऊपर आधा कर देता है जो GQA पहले ही पूरे MHA से वापस दिला चुका है: दोनों उपाय स्वतंत्र हैं और एक-दूसरे की जगह लेने के बजाय आपस में गुणा होते हैं।

</details>

## असली दुनिया का अभ्यास

- [ ] अपनी serving stack का वह flag ढूँढें जो KV cache के data type के लिए है (vLLM: `--kv-cache-dtype`) और पढ़ें कि वह कौन-सी precisions support करता है और accuracy के बारे में क्या चेतावनी देता है।
- [ ] जिस request के आकार की आप असल में उम्मीद करते हैं (prompt length, अपेक्षित output length) उसके लिए, किसी model के असली प्रति-token आँकड़े से निकालें कि उसके अंतिम cache का कितना हिस्सा prefill माँगता है और कितना decode।
- [ ] कल: vLLM दस्तावेज़ों में chunked prefill पर एक अनुच्छेद पढ़ें और एक वाक्य में लिखें कि prefill को टुकड़ों में तोड़ने से इस पाठ में बताई memory-माँग की समय-सारणी क्यों बदलती है।

## आगे बढ़ने के लिए

- [दस्तावेज़: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [लेख: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
