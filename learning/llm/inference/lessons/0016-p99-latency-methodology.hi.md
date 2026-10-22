---
title: "16. p99 Latency मापने की Methodology"
description: "p99 औसत से बेहतर क्यों है, TTFT और inter-token latency को अलग संख्याएँ क्यों चाहिए, और p99 माप को भरोसेमंद क्या बनाता है"
type: lesson
---

# पाठ 16. p99 Latency मापने की Methodology

**मिशन से संबंध:** इस workspace का मिशन p99 latency budget का बचाव करना है, और बचाव की गई संख्या को सही ढंग से की गई माप से आना चाहिए; यह पाठ वह है जो बताता है कि "सही ढंग से" का क्या मतलब है, इससे पहले कि पाठ 17 उस संख्या को हर पहले के चुनाव से जोड़े।
**मुख्य स्रोत:** [दस्तावेज़: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**पूर्व-आवश्यकताएँ:** [पाठ 15](0015-what-changes-off-gpu.md), [KV cache](../GLOSSARY.md)

## वार्म-अप

1. ▢ Prefill request के अंतिम cache footprint का ज़्यादातर हिस्सा एक ही step में क्यों माँग लेता है, जबकि decode बाक़ी धीरे-धीरे जोड़ता है?

<details markdown="1"><summary>जाँचें</summary>

Prefill पूरे prompt को एक forward pass में process करता है, prompt के हर token के keys और values साथ compute और cache करता है। Decode हर step में एक output token generate करता है, इसलिए cache हर step में सिर्फ़ एक token जितना बढ़ता है।

</details>

2. ▢ Continuous batching में, एक बड़ी दाख़िल हुई request अपने batch step को साझा करने वाले हर दूसरे sequence को क्यों रोक देती है?

<details markdown="1"><summary>जाँचें</summary>

Batch का step अविभाज्य है: उसे साझा करने वाला हर sequence साथ आगे बढ़ता है, इसलिए एक step में समेटा गया बड़ा prefill हर दूसरे sequence के अगले token को उस step के ख़त्म होने तक देर करता है। यह head-of-line blocking है।

</details>

## यह जानें

### p99 क्यों, औसत क्यों नहीं

Latency distribution का **p99** वह मान है जिसके नीचे नापी गई 99% requests आती हैं; सिर्फ़ सबसे बुरी 1% उससे धीमी होती हैं। औसत ठीक दिख सकता है जबकि असली समस्या छिपी हो: पाठ 5 की head-of-line blocking, उदाहरण के लिए, सिर्फ़ requests के उस छोटे हिस्से पर पड़ती है जो इतनी बदक़िस्मत थीं कि बड़े prefill के साथ एक step साझा करें, इसलिए हज़ारों बाक़ी तेज़ requests के औसत को वह मुश्किल से हिलाती है, जबकि उस बदक़िस्मत 1% को नाटकीय रूप से धीमा कर सकती है। औसत से बचाव किया गया latency budget ठीक वही विफलता का तरीक़ा चूक जाता, जिसे समझाने में इस workspace ने चरण 2 लगाया।

![Request latency का histogram। ज़्यादातर requests कम latency पर जमा हैं, जो बाईं ओर एक ऊँचा समूह बनाता है और तेज़ी से घटता है। Requests का एक अलग, विरल समूह बहुत ऊँची latency पर, काफ़ी दाईं ओर, है, यानी धीमी पूँछ। औसत को दिखाती बिंदीदार रेखा बाएँ वाले समूह के भीतर बैठी है, दाईं ओर की दुर्लभ requests से मुश्किल से खिसकी, क्योंकि वे इतनी कम हैं कि उसे हिला नहीं सकतीं। p99 का निशान इसके बजाय उसी दूर की दाईं पूँछ में बैठा है, क्योंकि p99 सबसे बुरे एक प्रतिशत से तय होता है, जो ठीक वहीं है जहाँ दुर्लभ, धीमी requests हैं।](images/p99-vs-average-latency.svg)

### कौन-सी latency, अलग से नापी गई

LLM server के लिए "request latency" एक संख्या नहीं है; कम से कम वह **time to first token (TTFT)** में बँटती है, जिस पर prefill हावी है, और **inter-token latency (ITL)** में, जिसे कभी-कभी time per output token कहते हैं, जिस पर decode हावी है। ये अलग ढंग से बरताव करते हैं (पाठ 3) और अलग उपायों से आकार लेते हैं (TTFT के लिए batching और scheduling, ITL के लिए batch size और quantization), इसलिए इन्हें एक मिली-जुली संख्या में समेटना यह धुँधला कर देता है कि ख़राब p99 असल में किस उपाय की ओर इशारा करता है। बचाव करने लायक़ budget p99 TTFT और p99 ITL (या कुल end-to-end latency का p99, जब workload को सचमुच वही चाहिए) को अलग आँकड़ों की तरह बताता है, दो अलग चीज़ों के एक औसत की तरह नहीं।

### p99 माप को भरोसेमंद क्या बनाता है

p99 किसी दुर्लभ घटना का अनुमान है, परिभाषा से नमूने का सिर्फ़ सबसे बुरा 1%, इसलिए उसे कुछ मायने रखने के लिए पर्याप्त नमूने चाहिए: 20 requests से निकला p99 असल में एक अकेली request पर रिपोर्ट कर रहा है (20 में से 1st percentile-worst अधिकतम के क़रीब है, स्थिर पूँछ का अनुमान नहीं), जबकि स्थिर अनुमान को आम तौर पर सैकड़ों से हज़ारों नमूने चाहिए। उन नमूनों को पैदा करने वाले load को भी असली workload जैसा दिखना चाहिए: यथार्थवादी concurrency (इतनी कम नहीं कि batching और scheduling का व्यवहार कभी असल में तनाव में न आए) और prompt व output lengths का यथार्थवादी मिश्रण (पाठ 4 की static-batching की बरबादी और पाठ 5 की head-of-line blocking दोनों उस request-length variance पर निर्भर हैं जिसे एकसमान-length requests वाला benchmark कभी सामने नहीं लाएगा)। अयथार्थवादी load में नापा गया p99 उस workload के बारे में असली संख्या है जो वह नहीं है जिसे serve किया जा रहा है।

## अभ्यास

1. ▢ Server की औसत request latency ठीक दिखती है, पर users कभी-कभी ऐसी requests की शिकायत करते हैं जो उम्मीद से कहीं ज़्यादा समय लेती हैं। यह पैटर्न सुझाता है कि समस्या latency distribution में कहाँ दिखेगी, और औसत ने उसे क्यों नहीं पकड़ा होगा?

<details markdown="1"><summary>जाँचें</summary>

यह पूँछ की समस्या सुझाता है, पाठ 5 की head-of-line blocking जैसी कोई चीज़, जो requests के सिर्फ़ छोटे हिस्से को प्रभावित करती है। कई, ज़्यादातर अप्रभावित requests का औसत तब भी मुश्किल से हिलता है जब वह छोटा हिस्सा नाटकीय रूप से धीमा हो जाए, और ठीक इसीलिए उसे देखने के लिए p99 (या कोई इसी तरह का ऊँचा percentile) चाहिए।

</details>

2. ▢ TTFT और inter-token latency को अलग p99 आँकड़ों के रूप में क्यों नापा और बताया जाना चाहिए, एक "औसत request latency" संख्या में समेटने के बजाय?

<details markdown="1"><summary>जाँचें</summary>

TTFT पर prefill हावी है और scheduling व chunking उसे आकार देते हैं; inter-token latency पर decode हावी है और batch size व quantization उसे आकार देते हैं। एक मिली-जुली संख्या नहीं बता सकती कि ख़राब नतीजा असल में इनमें से किस उपाय की ओर इशारा करता है, और एक को सुधारने से मिली-जुली औसत हिल सकती है बिना यह बताए कि दूसरा बिगड़ा या नहीं।

</details>

3. ▢ एक team 20 नापी गई requests से p99 latency का आँकड़ा निकालती है। क्या वह आँकड़ा भरोसेमंद है? क्यों या क्यों नहीं?

<details markdown="1"><summary>संकेत</summary>

सोचें कि 99वाँ percentile उन 20 requests में से असल में कितनों का वर्णन कर रहा है।

</details>

<details markdown="1"><summary>जाँचें</summary>

नहीं, भरोसेमंद रूप से नहीं। सिर्फ़ 20 नमूनों के साथ 99वाँ percentile नमूने की सबसे धीमी अकेली request पर रिपोर्ट करने के क़रीब है, असली पूँछ का स्थिर अनुमान नहीं। भरोसेमंद p99 को कहीं बड़ा नमूना चाहिए, आम तौर पर सैकड़ों से हज़ारों requests, ताकि इस शोर का औसत निकल सके कि कौन-सी ख़ास requests उस ऊपरी 1% में आ गईं।

</details>

4. ▢ एक benchmark उन requests से p99 latency नापता है जिन सबका prompt और output length एक जैसा, एकसमान है। यह उस p99 को कम करके क्यों आँक सकता है जो अलग-अलग request lengths वाला production workload असल में देखेगा?

<details markdown="1"><summary>जाँचें</summary>

पाठ 4 और पाठ 5 दोनों ने दिखाया कि request length की variance ही वह चीज़ है जो उन विफलता के तरीक़ों को पैदा करती है जो tail latency को चोट पहुँचाते हैं: static-batching की बरबादी requests की lengths के फैलाव के साथ बढ़ती है, और head-of-line blocking तब चालू होती है जब छोटे prompts के बीच कोई असामान्य रूप से बड़ा prefill आ जाए। एकसमान-length वाला benchmark वह variance कभी पैदा नहीं करता, इसलिए वह उन स्थितियों को कभी आज़माता ही नहीं जिनसे असली workload की tail latency आती है।

</details>

5. ▢ बचाव करने लायक़ p99 latency माप के बारे में कौन-सा दावा सही है?

    - a) किसी भी आकार की एक benchmark run काफ़ी है, बस वह p99 आँकड़ा बताए
    - b) उसे यथार्थवादी concurrency और request-length variance के साथ नापा जाना चाहिए, और TTFT व inter-token latency के लिए अलग से बताया जाना चाहिए
    - c) औसत और p99 हमेशा साथ चलते हैं, इसलिए एक को नापना काफ़ी है
    - d) p99 सिर्फ़ CPU/edge serving के लिए मायने रखता है, GPU serving के लिए नहीं

<details markdown="1"><summary>जाँचें</summary>

**b)** संख्या को किसी काम की चीज़ की ओर इशारा करने के लिए load की यथार्थता और TTFT को inter-token latency से अलग रखना, दोनों ज़रूरी हैं। (a) ग़लत है: बहुत कम नमूने p99 को अस्थिर बनाते हैं, जैसा प्रश्न 3 ने दिखाया। (c) ग़लत है: औसत ठीक वही पूँछ का व्यवहार छिपा सकता है जिसे पकड़ने के लिए p99 है। (d) ग़लत है: tail latency और उसकी माप किसी भी serving stack के लिए मायने रखती है, GPU हो या CPU।

</details>

## असली दुनिया का अभ्यास

- [ ] अपनी serving stack का benchmarking tool ढूँढें (vLLM `benchmark_serving.py` के साथ आता है) और पढ़ें कि वह default रूप से कौन-से percentiles बताता है और कौन-सा request-length distribution इस्तेमाल करता है।
- [ ] अपने सोचे हुए किसी workload के लिए लिखें कि यथार्थवादी prompt/output length distribution कैसा दिखेगा, और क्या एकसमान lengths वाला benchmark उसके बारे में कुछ चूक जाएगा।
- [ ] कल: अगर आपके पास चलता server है, तो उस पर कम से कम कुछ सौ requests के साथ benchmark चलाएँ और रिपोर्ट किए गए p99 TTFT और p99 inter-token latency को अलग-अलग नोट करें।

## आगे बढ़ने के लिए

- [दस्तावेज़: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [लेख: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
