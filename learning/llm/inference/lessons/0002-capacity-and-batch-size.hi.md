---
title: "2. Capacity और Batch Size"
description: "Head sharing (GQA/MQA) और batch size cache के असली footprint को कैसे बदलते हैं"
type: lesson
---

# पाठ 2. Capacity और Batch Size

**मिशन से संबंध:** Latency budget का बचाव इस बात के हिसाब से होता है कि server कितनी concurrent requests रख सकता है, और वह संख्या सीधे उसी cache गणित से निकलती है जिसे यह पाठ आगे बढ़ाता है।
**मुख्य स्रोत:** [लेख: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
**पूर्व-आवश्यकताएँ:** [पाठ 1](0001-the-kv-cache.md), [KV cache](../GLOSSARY.md)

## वार्म-अप

1. ▢ एक वाक्य में बताएँ: पहले token के बाद हर generate हुए token पर KV cache server को क्या छोड़ने देता है?

<details markdown="1"><summary>जाँचें</summary>

Sequence के हर पिछले token के key और value vectors को, हर layer पर, दोबारा compute करना।

</details>

2. ▢ Naive, सटे हुए, अधिकतम-length के आकार वाले cache आवंटन में क्या ग़लत था, और PagedAttention ने उसमें क्या बदला?

<details markdown="1"><summary>जाँचें</summary>

वह उस अधिकतम length के लिए memory आरक्षित करता था जहाँ sequence पहुँच सकता था, और उसे internal और external fragmentation के रूप में बरबाद करता था। PagedAttention इसके बजाय cache को निश्चित आकार के, बिना सटे blocks में आवंटित करता है, जिन्हें हर sequence की table से address किया जाता है।

</details>

## यह जानें

### ज़्यादातर models हर head के लिए एक key और value cache नहीं करते

पाठ 1 का formula, प्रति token `2 × num_layers × d_model × 2 bytes`, मानता है कि हर attention head अपने key और value vectors रखता है। यह **multi-head attention (MHA)** है। आज serve हो रहे ज़्यादातर models **grouped-query attention (GQA)** या उसका चरम रूप, **multi-query attention (MQA)**, इस्तेमाल करते हैं: कई query heads बहुत कम संख्या के key/value heads साझा करते हैं। Cache हर *KV head* के लिए सिर्फ़ एक K/V जोड़ी रखता है, हर query head के लिए नहीं, इसलिए formula यह बन जाता है:

```text
bytes per token = 2 (K and V) × num_layers × num_kv_heads × head_dim × bytes_per_value
```

जहाँ `head_dim = d_model / num_heads`, और अब `num_kv_heads` वह संख्या है जो मायने रखती है, कुल head count नहीं। जब `num_kv_heads = num_heads` हो तो यह ठीक पाठ 1 के formula पर आ जाता है (MHA, GQA का विशेष मामला है)। जब `num_kv_heads` बहुत छोटा हो तो cache उसी अनुपात में सिकुड़ता है, मुफ़्त में, context length या batch size में कोई बदलाव किए बिना।

![तीन पंक्तियाँ: MHA में 8 query heads हैं और हर एक का अपना KV head है, GQA में query heads के समूह 2 KV heads में से एक को साझा करते हैं (cache का चौथाई), MQA में सभी 8 query heads एक ही KV head साझा करते हैं (cache का आठवाँ हिस्सा)। Query head की संख्या cache के formula में कभी नहीं आती; सिर्फ़ KV head की संख्या आती है।](images/mha-gqa-mqa-head-sharing.svg)

Llama-2-70B एक ठोस उदाहरण है: 80 layers, 64 query heads, पर सिर्फ़ 8 KV heads, `head_dim` = 128। fp16 में:

```text
per token = 2 × 80 × 8 × 128 × 2 bytes = 327,680 bytes ≈ 320 KB
```

अगर उसने पूरा MHA इस्तेमाल किया होता (8 के बजाय 64 KV heads), तो उन्हीं layers और `head_dim` से प्रति token `2 × 80 × 64 × 128 × 2 = 2,621,440 bytes ≈ 2.5 MB` आता, आठ गुना ज़्यादा, ठीक `num_heads` और `num_kv_heads` के अनुपात जितना। GQA जितना modeling का फ़ैसला है उतना ही serving-लागत का भी।

### प्रति-token लागत को batch के कुल footprint में बदलना

Server शायद ही कभी एक sequence रखता है। किसी भी पल cache का कुल footprint प्रति-token लागत है, गुणा हर sequence कितना लंबा हो चुका है, गुणा कितने sequences एक साथ मौजूद हैं:

```text
total cache bytes = bytes per token × context length × batch size
```

4096-token context पर Llama-2-70B के लिए एक sequence की लागत `320 KB × 4096 ≈ 1.25 GB` है। उसी length के बत्तीस concurrent sequences की लागत `1.25 GB × 32 = 40 GB` है, model के अपने weights के लिए कोई जगह लेने से पहले ही।

### इसे capacity budget में बदलना

Serving के फ़ैसले को असल में यही संख्या चाहिए: एक memory pool दिया हो तो कितने concurrent sequences समाते हैं? उपलब्ध कुल memory में से weights और framework overhead घटाएँ, फिर जो बचे उसे उस context length पर प्रति-sequence cache लागत से भाग दें जिसे आप support करना चाहते हैं:

```text
max concurrent sequences = (total memory − weights − overhead) / (bytes per token × context length)
```

मान लें 320 GB का pool (चार 80 GB GPUs, tensor-parallel) Llama-2-70B serve कर रहा है, और weights व framework overhead 160 GB नापे गए। तब cache के लिए 160 GB बचते हैं। ऊपर के 4096-token, 1.25 GB-प्रति-sequence आँकड़े पर: `160 GB / 1.25 GB ≈ 128` concurrent sequences। वही सीमा, model का कच्चा throughput नहीं, आम तौर पर वह चीज़ है जिससे batching scheduler को सौदा करना पड़ता है, और पाठ 4 वहीं से आगे बढ़ता है।

## अभ्यास

1. ▢ एक model GQA इस्तेमाल करता है जिसमें `num_kv_heads`, `num_heads` का चौथाई है। उसी model के पूरे MHA वाले रूप की तुलना में उसका प्रति-token KV cache कितना छोटा है?

<details markdown="1"><summary>जाँचें</summary>

चौथाई आकार का। Cache हर KV head के लिए एक K/V जोड़ी रखता है, हर query head के लिए नहीं, इसलिए प्रति-token लागत अकेले `num_kv_heads` के साथ बदलती है; formula में बाक़ी सब कुछ जस का तस रहता है।

</details>

2. ▢ एक model में 48 layers, 40 query heads, 8 KV heads, `head_dim` = 128 है, fp16 में serve होता है। उसके प्रति-token KV cache का आकार निकालें।

<details markdown="1"><summary>संकेत</summary>

`2 × num_layers × num_kv_heads × head_dim × bytes_per_value` इस्तेमाल करें। Query head की संख्या formula में आती ही नहीं।

</details>

<details markdown="1"><summary>जाँचें</summary>

`2 × 48 × 8 × 128 × 2 = 196,608 bytes ≈ 192 KB` प्रति token।

</details>

3. ▢ प्रश्न 2 वाले 192 KB-प्रति-token model से, 2048-token context पर 16 sequences के batch का कुल cache footprint निकालें।

<details markdown="1"><summary>संकेत</summary>

`total cache bytes = bytes per token × context length × batch size`।

</details>

<details markdown="1"><summary>जाँचें</summary>

प्रति sequence: `192 KB × 2048 ≈ 384 MB`। 16 sequences के लिए: `384 MB × 16 = 6,144 MB ≈ 6 GB`।

</details>

4. ▢ एक server में 96 GB memory है। Weights और framework overhead 40 GB लेते हैं। जिस context length को यह server support करता है, उस पर हर sequence का cache 384 MB लेता है। Cache budget अधिकतम कितने concurrent sequences की अनुमति देता है?

<details markdown="1"><summary>जाँचें</summary>

`(96 GB − 40 GB) / 384 MB = 56 GB / 384 MB ≈ 149` sequences। व्यवहार में server इस सीमा से नीचे एक और सुरक्षा margin आरक्षित रखता है, पर हिसाब यही भाग है।

</details>

## असली दुनिया का अभ्यास

- [ ] जिस model को आप serve करने की सोच रहे हैं उसकी config file में `num_key_value_heads` (या उसके समकक्ष) field `num_attention_heads` के साथ देखें। दोनों का अनुपात निकालें और यह कि वह cache के आकार में क्या वापस दिलाता है।
- [ ] उस model के प्रति-token cache आकार से निकालें कि आपके पास उपलब्ध कोई memory pool (या किसी प्रकाशित GPU की memory) आपकी पसंद की context length पर कितने concurrent sequences रख सकता है।
- [ ] कल: वह flag ढूँढें जो आपकी चुनी serving stack (vLLM या llama.cpp) कुल KV cache memory की सीमा तय करने के लिए इस्तेमाल करती है, और पढ़ें कि कोई request उससे बढ़ने वाली हो तो क्या होता है।

## आगे बढ़ने के लिए

- [लेख: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
- [पेपर: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
