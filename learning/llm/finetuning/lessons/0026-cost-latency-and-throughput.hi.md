---
title: "26. Cost, Latency और Throughput"
description: "Prefill बनाम decode, और पैसा असल में कहाँ जाता है"
type: lesson
---

# पाठ 26. Cost, Latency और Throughput

**मिशन से संबंध:** "मापें कि गुणवत्ता और latency में इसकी क्या क़ीमत लगी" सफलता-सूची में है। Fine-tuning अक्सर *लागत* का फ़ैसला होता है, और यह उसके पीछे का अंकगणित है।
**मुख्य स्रोत:** [लेख: "LLM Inference Performance Engineering: Best Practices", Databricks](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices)
**पूर्व-आवश्यकताएँ:** [पाठ 25](0025-serving-adapters.md)

## वार्म-अप

1. ▢ Unmerged serving के पक्ष में संचालन की दलील क्या है?

<details markdown="1"><summary>जाँचें</summary>

Rollback deployment के बजाय routing का बदलाव है, और अछूता base fallback और तुलना के बिंदु के रूप में उपलब्ध रहता है।

</details>

2. ▢ आपको जो artifact ship करते हैं उसी का evaluation क्यों करना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

Serving-समय का quantisation प्रति-अनुरोध स्थायी गुणवत्ता की क़ीमत लेता है। bf16 model की संख्याएँ 4-bit deployment का वर्णन नहीं करतीं।

</details>

3. ▢ Fine-tuning सिखाने में क्या बुरी है?

<details markdown="1"><summary>जाँचें</summary>

नए तथ्य, अनुपस्थित reasoning क्षमता, ताज़ा जानकारी, सटीक गणना।

</details>

## यह जानें

### Inference का दो-चरणों वाला आकार

Generation के दो चरण हैं जिनकी performance की विशेषताएँ बिल्कुल अलग हैं, और उन्हें मिला देने से हर optimisation चर्चा असंगत हो जाती है।

**Prefill** पूरे input prompt को एक बार में process करता है। सारे tokens उपलब्ध हैं, इसलिए काम बड़ा समानांतर matrix गुणन है, जो इसे **compute-bound** बनाता है। लागत prompt की लंबाई के साथ बढ़ती है।

**Decode** एक बार में एक token generate करता है, हर एक पिछले पर निर्भर। हर step एक अकेला token बनाने के लिए पूरे model के weights पढ़ता है, इसलिए प्रति byte हिलाए गए अंकगणित बहुत कम है, जो इसे **memory-bandwidth-bound** बनाता है। लागत output की लंबाई के साथ बढ़ती है।

![Prefill वाली पंक्ति में आठ prompt tokens एक ही pass में जाते हुए, बनाम decode वाली पंक्ति में चार अलग जुड़े हुए passes, हर output token के लिए एक।](images/one-pass-or-one-each.svg)

ऊपर की पंक्ति में एक डिब्बा बनाम नीचे की में चार, यही पूरी असमरूपता है। Prompt लंबा करने से अकेला pass चौड़ा होता है; output लंबा करने से कड़ी में डिब्बे जुड़ते हैं।

नतीजे:

- **लंबे prompts प्रति token सस्ते हैं; लंबे outputs प्रति token महँगे।** असमान, और असमरूपता बड़ी है।
- Decode की गति memory bandwidth से तय होती है, इसलिए छोटा model लगभग अपने आकार के अनुपात में तेज़ है।
- Batching decode की बहुत मदद करती है, क्योंकि weights पूरे batch के लिए एक बार पढ़े जाते हैं, और prefill की बहुत कम।

### वे metrics जो मायने रखती हैं

| Metric | मतलब | किससे तय होती है |
|---|---|---|
| पहले token तक का समय | Prefill latency | Prompt की लंबाई, compute |
| Inter-token latency | प्रति output token समय | Memory bandwidth, model का आकार |
| कुल latency | शुरू से अंत तक | दोनों, साथ में queueing |
| Throughput | सभी अनुरोधों में tokens/second | Batching की कुशलता |
| प्रति अनुरोध लागत | पैसा | Throughput और hardware की लागत |

Latency और throughput, batch size के ज़रिए एक-दूसरे के विरुद्ध सौदा करते हैं। बड़े batches throughput बढ़ाते हैं और प्रति-अनुरोध latency भी। कोई एक सबसे अच्छी setting नहीं है: यह इस पर निर्भर है कि कोई इंसान इंतज़ार कर रहा है या नहीं।

### जहाँ fine-tuning अर्थशास्त्र बदलती है

यह वह हिस्सा है जो लोग चूक जाते हैं। Fine-tuning का लागत-फ़ायदा आम तौर पर weights के बेहतर होने से कोई संबंध नहीं रखता।

**छोटे prompts।** Fine-tuned model को few-shot examples, लंबे format निर्देश, विस्तृत system prompt की ज़रूरत नहीं, क्योंकि वह व्यवहार weights में है। अगर आपका prompt 2,000 tokens से 200 पर आ जाए, तो आपने हर अकेले अनुरोध से, हमेशा के लिए, 1,800 tokens का prefill हटा दिया। ज़्यादा-volume वाले endpoint पर अक्सर यही पूरा business case है।

**छोटे outputs।** जो model ज़रूरी format में उत्तर देने के लिए train हुआ है वह भूमिका और hedging से भराई करना छोड़ देता है। चूँकि decode महँगा चरण है, output की लंबाई घटाना प्रति token input की लंबाई घटाने से ज़्यादा मूल्यवान है।

**छोटे model का पर्याप्त हो जाना।** तर्क का सबसे मज़बूत रूप: fine-tuned छोटा model जो आपके संकरे task पर सामान्य बड़े model की बराबरी करे, प्रति अनुरोध नाटकीय रूप से सस्ता और कम latency वाला है, क्योंकि decode bandwidth-bound है और bandwidth आकार के साथ scale होती है। बड़े सामान्य model को छोटे विशेषीकृत से बदलना वह जगह है जहाँ परिमाण-क्रम की बचत रहती है।

**कम retries।** अगर सामान्य model 15% बार invalid output देता है और आप retry करते हैं, तो आपकी असली लागत दिखने वाली लागत की 1.15× है। जो fine-tune 99% validity तक पहुँचे वह इसका लगभग सब हटा देता है।

### ईमानदार हिसाब

उन बचतों के सामने, लागतें गिनें:

| लागत | प्रकृति |
|---|---|
| Training compute | हर version के लिए एक बार, adapters के लिए आम तौर पर छोटी |
| Data बनाना | अक्सर हावी लागत, और आम तौर पर इंसानी समय |
| Evaluation infrastructure | एक बार, फिर चलती रखरखाव |
| Serving की जटिलता | चलती: adapter-सक्षम stack, versioning, routing |
| Retraining | चलती: models, data और ज़रूरतें सब हिलते हैं |
| विशेषज्ञता | चलती: किसी को इसका मालिक होना पड़ेगा |

**आवर्ती लागतें ही इसे तय करती हैं, और वही शुरुआती अनुमान से छूट जाती हैं।** जो fine-tune प्रति अनुरोध थोड़ा पैसा बचाता है और जिसे सँभालने के लिए एक व्यक्ति चाहिए, वह कम volume पर बुरा सौदा है और ज़्यादा volume पर अच्छा। संधि-बिंदु अंकगणित है, इसलिए अंकगणित करें।

### काम किया हुआ एक तुलना

मान लें 2,000-token prompt वाला सामान्य बड़ा model बनाम 200-token prompt वाला fine-tuned छोटा model, दोनों 150 output tokens बना रहे हैं।

```text
General:  2000 prefill + 150 decode, on a large model
Tuned:     200 prefill + 150 decode, on a small model
```

Prompt की बचत 1,800 prefill tokens है। Model-आकार की बचत दोनों चरणों पर लागू होती है और ख़ासकर decode की bandwidth लागत पर। अनुरोधों की संख्या से गुणा करें, ऊपर की स्थिर और आवर्ती लागतों से तुलना करें, और आपके पास अंतर्ज्ञान के बजाय असली जवाब है।

दिन में एक हज़ार अनुरोधों पर शायद यह data के काम को वसूल न करे। दस लाख पर बहुत संभव है कि करे। **Volume ही फ़ैसला करने वाला चर है, और वही सबसे कम बार बताया जाता है।**

### मापें, मॉडल न बनाएँ

ऊपर का सब कुछ सही आकार और ग़लत सटीकता का है। असली संख्याएँ hardware, serving stack, batch size, sequence लंबाइयों और traffic के पैटर्न पर ऐसे निर्भर करती हैं जिन्हें कोई सूत्र नहीं पकड़ता। मापें:

- आपकी असली prompt लंबाइयों पर पहले token तक का समय और inter-token latency
- आपका latency/throughput बिंदु ढूँढने के लिए कई batch sizes पर throughput
- आपके असली traffic के आकार पर प्रति हज़ार अनुरोध लागत
- जिस विकल्प से आप तुलना कर रहे हैं उसके लिए वही तीनों

और यथार्थवादी load में मापें। एक बार में एक अनुरोध वाला benchmark batched production endpoint के बारे में कुछ नहीं बताता, क्योंकि batching throughput में हावी कारक है।

## अभ्यास

1. ▢ कौन-सा चरण compute-bound है, कौन-सा bandwidth-bound, और उससे क्या निकलता है?

<details markdown="1"><summary>जाँचें</summary>

Prefill compute-bound है, क्योंकि पूरा prompt समानांतर process होता है। Decode memory-bandwidth-bound है, क्योंकि हर step एक token बनाने के लिए सारे weights पढ़ता है।

इससे निकलता है कि लंबे prompts अपेक्षाकृत प्रति token सस्ते हैं, लंबे outputs महँगे, batching decode की prefill से कहीं ज़्यादा मदद करती है, और छोटे models decode को लगभग आकार के अनुपात में तेज़ करते हैं।

</details>

2. ▢ आपका fine-tune prompt की लंबाई 1,800 tokens से 150 कर देता है और output की लंबाई वैसी ही छोड़ देता है। बचत कहाँ से आती है?

<details markdown="1"><summary>जाँचें</summary>

Prefill से: हर अनुरोध पर compute-bound काम के 1,650 tokens कम। जो व्यवहार पहले few-shot examples और format निर्देशों से तय होता था वह अब weights में रहता है।

यही अक्सर fine-tuning का पूरा आर्थिक पक्ष है, और इसका model के ज़्यादा समझदार होने से कोई संबंध नहीं।

</details>

3. ▢ Fine-tuning का कौन-सा फ़ायदा सबसे बड़ी लागत-कटौती देता है?

    - a) Prompt का एक हज़ार tokens छोटा हो जाना
    - b) छोटे model का task के लिए पर्याप्त हो जाना
    - c) Output का पचास output tokens छोटा हो जाना
    - d) Retry दर का पंद्रह प्रतिशत से एक पर आ जाना

<details markdown="1"><summary>जाँचें</summary>

**b)** छोटे model का task के लिए पर्याप्त हो जाना।

यह दोनों चरणों को एक साथ घटाता है, और decode, जो महँगा चरण है, model के आकार के साथ scale होता है क्योंकि वह bandwidth-bound है। बाक़ी असली और जुड़ने वाले हैं, पर model के आकार का बदलाव हर चीज़ पर गुणात्मक है।

</details>

4. ▢ शुरुआती अनुमान से सबसे ज़्यादा कौन-सी लागतें छूटती हैं?

<details markdown="1"><summary>जाँचें</summary>

आवर्ती वाली: models और ज़रूरतें हिलने पर retraining, serving की जटिलता, evaluation का रखरखाव, और उस व्यक्ति की विशेषज्ञता जो इसका मालिक है।

Adapters के लिए training compute सस्ता है और उद्धृत किया जाता है। चलती इंसानी लागत महँगी है और भुला दी जाती है, और वही आम तौर पर सवाल तय करती है।

</details>

5. ▢ आप एक-अनुरोध की latency मापते हैं और निष्कर्ष निकालते हैं कि आपका endpoint काफ़ी तेज़ है। क्या ग़लत है?

<details markdown="1"><summary>जाँचें</summary>

Production समवर्ती अनुरोधों को batches में serve करता है। Batch size throughput और प्रति-अनुरोध latency, दोनों पर हावी है, और एक-अनुरोध का माप दोनों को नहीं देखता।

यथार्थवादी concurrency में, कई batch sizes पर मापें, और latency/throughput curve पर अपना बिंदु सोच-समझकर चुनें।

</details>

6. ▢ वही task, प्रति अनुरोध वही बचत, दिन में 500 अनुरोध बनाम 50 लाख। क्या फ़ैसला वही?

<details markdown="1"><summary>जाँचें</summary>

नहीं। Data बनाने, evaluation, serving की जटिलता और रखरखाव की स्थिर और आवर्ती लागतें लगभग volume से स्वतंत्र हैं, जबकि बचत उसके साथ scale होती है।

दिन में 500 पर आवर्ती इंसानी लागत लगभग निश्चित रूप से हावी है। 50 लाख पर वह बचत के सामने नगण्य है। Volume फ़ैसला करने वाला चर है और प्रस्ताव के पहले वाक्य में आना चाहिए।

</details>

## असली दुनिया का अभ्यास

- [ ] अपने model के लिए आपकी असली prompt लंबाइयों पर पहले token तक का समय और inter-token latency मापें।
- [ ] Batch sizes 1, 4, 16 और 64 पर throughput मापें। latency/throughput का सौदा plot करें और अपना बिंदु चुनें।
- [ ] अपने fine-tuned रास्ते और विकल्प के लिए प्रति हज़ार अनुरोध लागत निकालें। आवर्ती लागतें शामिल करें।
- [ ] कल: वह अनुरोध-volume ढूँढें जिस पर आपका fine-tune बराबरी पर आता है। उसकी तुलना अपने असली volume से करें।

## आगे बढ़ने के लिए

- [लेख: "LLM Inference Performance Engineering: Best Practices", Databricks](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices)
- [दस्तावेज़: Optimization and tuning, vLLM](https://docs.vllm.ai/en/latest/configuration/optimization.html)
- [पाठ 27. Fine-Tuning कब न करें](0027-when-not-to-fine-tune.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
