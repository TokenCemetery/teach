---
title: "8. अकेला Data Parallelism Memory से बाहर क्यों हो जाता है"
description: "ठीक-ठीक गिनना कि mixed-precision Adam optimizer हर parameter पर क्या रखता है, और वह कहाँ दीवार से टकराता है"
type: lesson
---

# पाठ 8. अकेला Data Parallelism Memory से बाहर क्यों हो जाता है

**मिशन से संबंध:** "समझाएँ कि ZeRO/FSDP क्या shard करते हैं, data parallelism अकेला compute ख़त्म होने से पहले memory से क्यों बाहर हो जाता है, और tensor या pipeline parallelism अपनी communication लागत के लायक़ कब है" "सफलता कैसी दिखती है" का चौथा बिंदु है। पाठ 7 ने कवर किया कि data parallelism हर device की copy को एक-जैसा कैसे रखता है; यह पाठ ठीक-ठीक गिनता है कि "हर device के पास पूरी copy है" की क्या क़ीमत है, और वह कहाँ टूटता है।
**मुख्य स्रोत:** [पेपर: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**पूर्व-आवश्यकताएँ:** [पाठ 7](0007-data-parallelism-and-gradient-all-reduce.md)

## वार्म-अप

1. ▢ Data parallelism में, कौन-सा operation हर optimizer step के बाद हर device के model की copy को एक-जैसा रखता है?

<details markdown="1"><summary>जाँचें</summary>

All-reduce: हर device का स्थानीय gradient किसी भी device के update लगाने से पहले सभी devices में औसत किया जाता है, इसलिए हर device weights की एक-जैसी शुरुआती copy पर वही औसत gradient लगाता है।

</details>

2. ▢ क्या ज़्यादा data-parallel devices जोड़ने से किसी एक device को model रखने के लिए चाहिए memory घटती है? क्यों या क्यों नहीं?

<details markdown="1"><summary>जाँचें</summary>

नहीं। हर device के पास अब भी parameters, gradients और optimizer state की पूरी copy है, ठीक वैसे जैसे अकेले train करते समय होती; ज़्यादा devices का मतलब उसी footprint की ज़्यादा copies है, हर device पर छोटा footprint नहीं।

</details>

## यह जानें

### "Model की पूरी copy" में असल में क्या है

पाठ 7 ने कहा कि हर data-parallel device के पास parameters, gradients और optimizer state की पूरी copy होती है, बिना यह गिने कि इसकी क्या क़ीमत है। Mixed-precision training, जो बड़े models train करने का मानक तरीक़ा है, गिनती को ठोस बनाती है। Adam को optimizer मानकर, Rajbhandari et al. प्रति parameter गिनते हैं (`Ψ` parameter count दर्शाता है):

- parameters की एक `fp16` copy, जो forward और backward pass में इस्तेमाल होती है: प्रति parameter 2 bytes
- gradients की एक `fp16` copy: प्रति parameter 2 bytes
- parameters की एक `fp32` copy, जो optimizer संख्यात्मक रूप से स्थिर updates के लिए रखता है: प्रति parameter 4 bytes
- Adam के momentum की एक `fp32` copy: प्रति parameter 4 bytes
- Adam के variance की एक `fp32` copy: प्रति parameter 4 bytes

कुल मिलाकर प्रति parameter 16 bytes, जिनमें से हर एक की पूरी copy हर data-parallel device रखता है, चाहे कितने भी दूसरे devices वही एक-जैसी copy रखे हों।

### यह दीवार से कहाँ टकराता है

1.5-अरब-parameter model (GPT-2 के आकार) के लिए, प्रति parameter 16 bytes सिर्फ़ इन model states के लिए 24 GB बैठता है, जो सिर्फ़ `fp16` parameters रखने के 3 GB से कहीं ऊपर है, और यह activations गिनने से पहले है (forward pass से रखे गए बीच के मान जो backward pass में gradients निकालने के काम आते हैं), जिन्हें Rajbhandari et al. अलग से उसी model के लिए 1,024 के sequence length और 32 के batch size पर लगभग 60 GB आँकते हैं। Rajbhandari et al. इससे निकली सीमा सीधे बताते हैं: "basic data parallelism does not reduce memory per device, and runs out of memory for models with more than 1.4B parameters on current generation of GPUs with 32 GB memory." 32 GB वाला GPU किसी और चीज़ से बाहर होने से पहले ही जगह से बाहर हो गया है, GPT-2 से बस थोड़े बड़े model पर, data parallelism जितने भी devices जोड़ सकता है उन सबके इस्तेमाल के बावजूद।

### हल की शक्ल

साधारण data parallelism में हर device उन्हीं 16Ψ bytes की model states की एक-जैसी, पूरी तरह फ़ालतू copy रखता है। यही फ़ालतूपन है जिसे कोई दूसरी रणनीति हटा सकती है: हर device के सब कुछ रखने के बजाय, हर device सिर्फ़ model states का अपना हिस्सा रख सकता है, और जो उसके पास नहीं है उसे तभी दोबारा बनाए या communicate करे जब किसी computation के लिए वह सचमुच ज़रूरी हो। यही वह विचार है जिसे चरण 5 सीधे उठाता है, ZeRO के नाम से।

## अभ्यास

1. ▢ प्रति parameter 16 bytes के ब्योरे का इस्तेमाल करके, Adam के साथ mixed precision में train हुए 7-अरब-parameter model के लिए अकेले model states को लगभग कितनी memory चाहिए?

<details markdown="1"><summary>संकेत</summary>

Parameter count को 16 bytes से गुणा करें, फिर bytes को gigabytes में बदलें।

</details>

<details markdown="1"><summary>जाँचें</summary>

लगभग 112 GB (`7 × 10^9 × 16` bytes ≈ `1.12 × 10^11` bytes ≈ 112 GB)। यह अकेले model states हैं, एक अकेले 32 GB या 80 GB GPU से भी काफ़ी ऊपर, activations गिनने से पहले ही।

</details>

2. ▢ इनमें से कौन-सा सबसे अच्छा समझाता है कि अकेला data parallelism किसी भी मनमाने बड़े model को fit क्यों नहीं कर सकता, चाहे कितने भी devices जोड़े जाएँ?

    - a) Devices के बीच communication bandwidth आख़िरकार भर जाती है
    - b) हर device प्रति-parameter memory लागत की पूरी, फ़ालतू copy रखता है, इसलिए devices जोड़ने से ज़्यादा copies जुड़ती हैं, किसी एक device की ज़रूरत घटती नहीं
    - c) All-reduce operation ख़ुद model size के अनुपात में memory खाता है
    - d) बड़े models हमेशा बड़े gradients बनाते हैं, जो fp16 representation से overflow हो जाते हैं

<details markdown="1"><summary>जाँचें</summary>

**b)** यही असली सीमा है जिसे यह पाठ फ़ालतू per-device memory footprint से सीधे निकालता है। (a) distributed training में असली चिंता है पर वह communication-समय की लागत है, memory-क्षमता की वह दीवार नहीं जिसके बारे में यह पाठ है। (c) और (d) वह तंत्र नहीं हैं जिसे ZeRO के लेखक पहचानते हैं।

</details>

3. ▢ Rajbhandari et al. बताते हैं कि basic data parallelism 32 GB memory वाले GPUs पर 1.4B से ज़्यादा parameters वाले models के लिए memory से बाहर हो जाता है। प्रति parameter 16 bytes के ब्योरे के हिसाब से, 1.4B-parameter model की अकेली states को लगभग कितनी memory चाहिए, और activations जुड़ने पर यह 32 GB के आँकड़े से कैसे तुलना करता है?

<details markdown="1"><summary>जाँचें</summary>

अकेले model states के लिए लगभग 22.4 GB (`1.4 × 10^9 × 16` bytes ≈ `2.24 × 10^10` bytes)। इससे 32 GB के GPU में activations के लिए 10 GB से कम बचता है, जिन्हें पाठ का GPT-2 उदाहरण मामूली sequence length और batch size पर लगभग 60 GB बताता है, जो बचे हुए से कहीं ज़्यादा है।

</details>

## असली दुनिया का अभ्यास

- [ ] किसी प्रकाशित open model का parameter count चुनें और प्रति parameter 16 bytes वाले formula से mixed-precision Adam के तहत उसकी model-state memory की ज़रूरत का अनुमान लगाएँ। उस अनुमान की तुलना उन GPU memory sizes से करें जो training के लिए आम तौर पर इस्तेमाल होती हैं (24, 40, 80 GB तुलना के लिए सामान्य आँकड़े हैं)।
- [ ] ZeRO पेपर (ऊपर linked) का वह अनुच्छेद पढ़ें जो residual memory (activations, अस्थायी buffers, memory fragmentation) का वर्णन करता है, और एक वाक्य लिखें जो उसे उस model-states memory से अलग करे जो इस पाठ ने गिनी।
- [ ] कल: आगे देखे बिना, चरण 5 के लिए एक वाक्य में अनुमान लिखें: अगर समस्या यह है कि हर device उन्हीं 16Ψ bytes की पूरी, फ़ालतू copy रखता है, तो फ़ालतूपन हटाने वाले हल को इसके बजाय क्या करना होगा, और स्थानीय रूप से सब कुछ न रखने की भरपाई के लिए उसे क्या communicate करना होगा?

## आगे बढ़ने के लिए

- [पेपर: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [संसाधन](../RESOURCES.md)

---

चरण 4 ने स्थापित किया कि data parallelism का फ़ालतूपन, उसका compute नहीं, पहले ख़त्म होता है। चरण 5 इसे सीधे उठाता है: उसे हटाने के लिए ZeRO और FSDP असल में क्या shard करते हैं।

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
