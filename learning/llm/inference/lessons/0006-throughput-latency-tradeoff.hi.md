---
title: "6. Throughput/Latency Trade-off"
description: "Batch size throughput और प्रति-token latency के बीच कैसे सौदा करता है, और बताए गए latency budget के विरुद्ध batching configuration का बचाव कैसे करें"
type: lesson
---

# पाठ 6. Throughput/Latency Trade-off

**मिशन से संबंध:** यह चरण 2 का समापन है: बताए गए workload के लिए batching configuration का बचाव करने का मतलब है पाठ 4 और 5 में बताए throughput/latency trade-off पर संख्या रखना, latency budget और पाठ 2 में निकाली गई capacity सीमा के विरुद्ध।
**मुख्य स्रोत:** [दस्तावेज़: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**पूर्व-आवश्यकताएँ:** [पाठ 5](0005-request-scheduling.md), [पाठ 2](0002-capacity-and-batch-size.md), [KV cache](../GLOSSARY.md)

## वार्म-अप

1. ▢ ज़्यादा sequences के decode steps को साथ batch करने से memory traffic उसी अनुपात में बढ़े बिना throughput क्यों बढ़ता है?

<details markdown="1"><summary>जाँचें</summary>

Decode step का memory traffic, यानी weights और मौजूद KV caches पढ़ना, ज़्यादा नहीं बदलता चाहे वह एक sequence का अगला token compute करे या कई का। Batching उसी traffic को ज़्यादा काम के compute पर फैला देती है।

</details>

2. ▢ पाठ 2 की capacity सीमा एक वाक्य में क्या है?

<details markdown="1"><summary>जाँचें</summary>

`(total memory − weights − overhead) / (bytes per token × context length)`: KV cache budget जितने concurrent sequences की अधिकतम अनुमति देता है, latency के बारे में किसी बात से स्वतंत्र।

</details>

## यह जानें

### बड़े batches एक साथ दो काम करते हैं, और वे उल्टी दिशाओं में खींचते हैं

Batch में एक और sequence जोड़ने से throughput बढ़ता है: step के हर sequence को मिलाकर प्रति सेकंड ज़्यादा tokens बनते हैं। पर batch step का हर sequence साथ आगे बढ़ता है (पाठ 5), इसलिए ज़्यादा sequences का decode काम एक step में लादने से वह step ख़ुद भी लंबा हो जाता है। किसी अकेले sequence के अपने लगातार tokens के बीच की देरी, यानी उसकी inter-token latency, उस batch के साथ बढ़ती है जिसके साथ वह step साझा करता है। Throughput और प्रति-token latency साथ-साथ चलते हैं, एक-दूसरे के विरुद्ध स्वतंत्र रूप से नहीं: एक को ऊपर धकेलना दूसरे को भी ऊपर धकेलता है।

### वक्र के दो दौर हैं

छोटे batch sizes पर decode memory-bandwidth bound है (पाठ 4): वही weights और cache पढ़ना पहले से step की लागत पर हावी है, इसलिए एक और sequence जोड़ना लगभग मुफ़्त है। Throughput लगभग रैखिक रूप से batch size के साथ बढ़ता है जबकि step latency मुश्किल से हिलती है। किसी batch size के बाद इतना लदा हुआ काम होता है कि GPU का कच्चा compute, उसकी memory bandwidth नहीं, अड़चन बन जाता है: हर जोड़े गए sequence के साथ step latency साफ़ बढ़ने लगती है, और हर आगे का sequence पिछले से कम अतिरिक्त throughput ख़रीदता है। वह मोड़ वही memory-bandwidth-bound बनाम compute-bound का फ़र्क़ है जो पाठ 3 ने prefill और decode के बीच खींचा था, अब batch बढ़ने पर decode के भीतर ही हो रहा है।

![Batch size के विरुद्ध प्रति-token latency: 8 पर 15ms, 32 पर 25ms, 64 पर 45ms, 128 पर 90ms। जब तक decode memory-bandwidth bound है वक्र सपाट रहता है, फिर compute के अड़चन बनते ही तेज़ी से चढ़ता है। 30ms का latency budget, जिसे बिंदीदार रेखा से दिखाया गया है, batch size 32 और 64 के बीच पार होता है।](images/throughput-latency-tradeoff.svg)

### Configuration का बचाव करने का मतलब उस वक्र पर एक बिंदु चुनना है, उपलब्ध सबसे बड़ी संख्या नहीं

बताया गया workload दो स्वतंत्र बाधाएँ देता है, और बचाव करने लायक़ config वह सबसे बड़ा batch size है जो दोनों को पूरा करे:

- **Latency budget**: inter-token latency की बताई गई ऊपरी सीमा (जैसे, कोई output token आने में इतने milliseconds से ज़्यादा न ले)।
- **Capacity सीमा**: पाठ 2 की memory से निकली अधिकतम संख्या, जो latency के बारे में कुछ नहीं कहती और इस बारे में सब कुछ कहती है कि cache समाता भी है या नहीं।

दोनों बाधाओं से नीचे का batch size उस throughput को छोड़ देता है जो budget सह सकता था। Latency budget से ऊपर का batch size latency के उल्लंघन के बदले ऐसा throughput ख़रीदता है जो किसी ने माँगा नहीं था। बचाव की जाने वाली संख्या वह है जो budget जितना देता है और capacity जितना देती है, उन दोनों में छोटी हो, और उसे चुनने का तर्क "यही संख्या क्यों, कोई और क्यों नहीं" का उत्तर है, जो configuration का बचाव करने का असल मतलब है।

## अभ्यास

1. ▢ एक serving stack को चार batch sizes पर benchmark किया गया: 8 (15 ms/token), 32 (25 ms/token), 64 (45 ms/token), 128 (90 ms/token)। बताया गया latency budget 30 ms/token है। इन batch sizes में budget को पूरा करने वाला सबसे बड़ा कौन-सा है?

<details markdown="1"><summary>जाँचें</summary>

32, 25 ms/token पर। 64 और 128 दोनों 30 ms budget से ऊपर हैं; चारों में 32 सबसे बड़ा है जो उसके नीचे रहता है।

</details>

2. ▢ प्रश्न 1 जारी रखते हुए: इस workload के लिए KV cache की capacity सीमा, जैसे पाठ 2 निकालता है वैसे, 100 concurrent sequences आती है। असल में किस batch size का बचाव होना चाहिए, और कौन-सी बाधा बाँध रही है?

<details markdown="1"><summary>संकेत</summary>

बचाव की जाने वाली संख्या वह है जो हर बाधा अकेले जितना देती है उनमें छोटी हो।

</details>

<details markdown="1"><summary>जाँचें</summary>

32 का batch size। यहाँ latency budget बाँधता है, क्योंकि 32, 100-sequence की capacity सीमा से बहुत नीचे है; cache में काफ़ी जगह बची है, पर latency budget में नहीं।

</details>

3. ▢ मान लें इसके बजाय capacity सीमा 20 sequences आती, प्रश्न 1 में बाक़ी सब वही। अब किस batch size का बचाव होना चाहिए, और क्यों?

<details markdown="1"><summary>जाँचें</summary>

20 का batch size। अब latency budget की जगह capacity सीमा बाँधती है: 32, 30 ms/token budget को पूरा करता, पर cache उतने concurrent sequences रख ही नहीं सकता, इसलिए memory की बाधा संख्या को अकेली latency से कम पर थाम देती है।

</details>

4. ▢ एक team प्रश्न 1 के workload के लिए 8 का batch size चुनती है, जो latency-budget से निकले 32 के चुनाव और 100-sequence की capacity सीमा दोनों से काफ़ी नीचे है। उस चुनाव की क्या क़ीमत है?

<details markdown="1"><summary>जाँचें</summary>

मेज़ पर छोड़ा गया throughput। 8 पर step latency (15 ms/token) 30 ms budget से काफ़ी नीचे है, यानी budget बड़ा batch सह सकता था, और cache में 8 sequences की ज़रूरत से कहीं ज़्यादा जगह है। किसी चीज़ का उल्लंघन नहीं हो रहा, पर server उससे कम concurrent requests serve कर रहा है जितनी का वह बचाव कर सकता था।

</details>

## असली दुनिया का अभ्यास

- [ ] अपनी serving stack का max batch size का flag ढूँढें (vLLM: `--max-num-seqs`) और पढ़ें कि latency लक्ष्य के विरुद्ध उसे tune करने के बारे में उसके दस्तावेज़ क्या कहते हैं।
- [ ] अगर आपकी पहुँच किसी चलते server या उसके benchmarks तक है तो कुछ batch sizes पर उसका throughput और प्रति-token latency plot करें (या खोजें), और मोटे तौर पर ढूँढें कि compute-bound दौर कहाँ से शुरू होता है।
- [ ] कल: अपनी पसंद के किसी workload के लिए ऐसा latency budget चुनें जिसका आप सचमुच बचाव करना चाहेंगे, और एक वाक्य में लिखें कि यही संख्या क्यों, और कोई कड़ी या ढीली क्यों नहीं।

## आगे बढ़ने के लिए

- [दस्तावेज़: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [लेख: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
