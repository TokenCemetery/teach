---
title: "5. Request Scheduling"
description: "Continuous-batching scheduler अगली request कैसे चुनता है, और बड़ा prefill बाक़ी सबको क्यों रोक सकता है"
type: lesson
---

# पाठ 5. Request Scheduling

**मिशन से संबंध:** पाठ 4 की continuous batching तभी मदद करती है जब उसमें requests दाख़िल करने वाला scheduler ख़ुद कोई नई latency समस्या न खड़ी करे; यह पाठ उसी trade-off का घर है।
**मुख्य स्रोत:** [दस्तावेज़: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**पूर्व-आवश्यकताएँ:** [पाठ 4](0004-static-vs-continuous-batching.md), [KV cache](../GLOSSARY.md)

## वार्म-अप

1. ▢ Continuous batching में, batch का कोई sequence जिस पल generate करना ख़त्म करता है, तब क्या होता है?

<details markdown="1"><summary>जाँचें</summary>

उसका slot तुरंत मुक्त हो जाता है, और अगले step पर इंतज़ार कर रही नई request उसमें दाख़िल हो जाती है, इसके बजाय कि slot तब तक ख़ाली बैठे जब तक requests का निश्चित समूह एक साथ ख़त्म न हो।

</details>

2. ▢ Prefill compute-bound और decode memory-bandwidth bound क्यों है?

<details markdown="1"><summary>जाँचें</summary>

Prefill पूरे prompt को एक बड़े, parallel forward pass में process करता है, इसलिए हर पढ़े गए byte पर इतना काम होता है कि GPU का compute व्यस्त रहे। Decode हर step में सिर्फ़ एक नया token compute करता है, इसलिए हर step का memory traffic (cache और weights पढ़ना) थोड़े-से नए compute पर हावी रहता है।

</details>

## यह जानें

### इंतज़ार कर रही कौन-सी request अगली जाए

इंतज़ार कर रही requests की queue सँभालने वाले scheduler को यह नीति चाहिए कि अभी मुक्त हुए slot में किसे दाख़िल किया जाए। सीधी default नीति, और अलग configuration न हो तो vLLM जो इस्तेमाल करता है, **first-come, first-served (FCFS)** है: requests आने के क्रम में दाख़िल होती हैं। यही अकेली संभव नीति नहीं है (scheduler अपेक्षित length या बताए गए latency budget के हिसाब से प्राथमिकता दे सकता है), पर FCFS वह सही default है जिसे पहले जानना चाहिए: यह सरल है, यह इस अर्थ में निष्पक्ष है कि कोई request किसी बाद में आई request के पीछे इंतज़ार नहीं करती, और हर और जटिल नीति उसी मुक्त-हुए-slot-में-दाख़िल-करो तंत्र का एक रूप है जिसे पाठ 4 ने बताया था।

### Batch का एक step अविभाज्य है, और इससे नई समस्या पैदा होती है

Batch के एक step को साझा करने वाला हर sequence साथ आगे बढ़ता है: पूरे step की latency इससे तय होती है कि उसमें सबसे महँगा काम कौन-सा है। नई request दाख़िल करने का मतलब है कि उसका prefill काम कहीं होना है, और सीधी जगह अगला ही batch step है, उन decode steps के साथ जो पहले से चल रहे sequences को चाहिए।

यह तब ठीक है जब नई request का prompt छोटा हो। यह तब ठीक नहीं जब वह लंबा हो: एक step में समेटा गया 6,000-token का prefill अब उस step की latency पर हावी हो जाता है, और batch का हर दूसरा sequence, जिन्हें सिर्फ़ एक छोटा, तेज़ decode step चाहिए था, अपना अगला token पाने से पहले उसके ख़त्म होने का इंतज़ार करता है। एक बड़ा दाख़िला बाक़ी सबकी प्रगति रोक देता है। यह **head-of-line blocking** की समस्या है: queue ठीक है, पर जो अभी चल रहा है वह नहीं।

### Chunked prefill नुक़सान की सीमा बाँध देता है

**Chunked prefill** बड़े prompt के prefill को छोटे टुकड़ों में बाँटता है और हर टुकड़े को batch के चल रहे decode steps के साथ गूँथ देता है, पूरा prefill एक ही step में चलाने के बजाय। अब हर batch step नए prefill काम की सिर्फ़ एक सीमित मात्रा लेता है, जितनी step के latency budget में समाए, न कि जितना भी नई दाख़िल हुई request के prompt में हो। इसका सौदा यह है कि नई request का अपना prefill अब एक के बजाय कई steps में पूरा होता है, पर batch का कोई और sequence उसके इंतज़ार में रुकता नहीं।

![ऊपर: chunking के बिना, बड़े prompt का पूरा prefill एक step में समेट दिया जाता है, जिससे उसकी latency स्थिर 20ms वाले decode steps से कहीं आगे फूल जाती है और बाक़ी हर sequence इंतज़ार करता है। नीचे: chunked prefill उसी prompt के prefill को छोटे टुकड़ों में बाँटकर decode के साथ गूँथता है, जिससे हर step 20ms के आसपास रहता है, इस क़ीमत पर कि नई request का prefill ख़त्म होने में ज़्यादा steps लेता है।](images/chunked-prefill.svg)

## अभ्यास

1. ▢ एक continuous batch लगभग 20 ms वाले स्थिर, सिर्फ़-decode steps चला रहा है। 6,000-token का prompt दाख़िल होता है और उसका पूरा prefill chunking के बिना अगले ही step में समेट दिया जाता है। उस step की latency का क्या होता है, और असर किसे महसूस होता है?

<details markdown="1"><summary>जाँचें</summary>

उस step को अब सभी 6,000 prompt tokens का prefill compute पूरा करना है, साथ में batch के हर दूसरे sequence का decode काम भी, क्योंकि पूरा batch एक step में साथ आगे बढ़ता है। Step की latency 20 ms से बहुत आगे फूल जाती है, और batch का हर दूसरा sequence, वे भी जिन्हें सिर्फ़ तेज़ decode step चाहिए था, अपना अगला token पाने से पहले उस एक step के ख़त्म होने का इंतज़ार करता है।

</details>

2. ▢ Chunked prefill प्रश्न 1 में बताई रुकावट से कैसे बचता है?

<details markdown="1"><summary>संकेत</summary>

सोचें कि प्रति step क्या बदलता है, न कि prefill के कुल ज़रूरी काम की मात्रा के बारे में क्या बदलता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

नई request का पूरा prompt एक step में चलाने के बजाय, scheduler उसके prefill को छोटे टुकड़ों में बाँटता है और हर टुकड़े को batch के नियमित decode steps के साथ गूँथता है, प्रति step नए prefill काम की सिर्फ़ सीमित मात्रा दाख़िल करते हुए। कोई भी एक step की latency सीमित रहती है; नई request के अपने prefill को बस कुल मिलाकर ज़्यादा steps लगते हैं।

</details>

3. ▢ Chunked prefill के बारे में कौन-सा दावा सही है?

    - a) वह prefill को पूरी तरह हटा देता है और हर token को decode step मानता है
    - b) वह बड़े prefill को टुकड़ों में बाँटकर step की जुड़ी हुई latency को सीमित करता है
    - c) वह llama.cpp जैसे CPU serving stacks की ख़ास तकनीक है
    - d) वह पूरी तरह process हो चुके लंबे prompt को चाहिए KV cache की मात्रा घटाता है

<details markdown="1"><summary>जाँचें</summary>

**b)** वह बड़े prefill को decode के साथ गूँथे हुए टुकड़ों में बाँटकर step की जुड़ी हुई latency को सीमित करता है। (a) ग़लत है: prompt को अब भी पूरा prefill processing चाहिए, बस वह ज़्यादा steps में फैला होता है। (c) ग़लत है: यह GPU continuous-batching की scheduling तकनीक है। (d) ग़लत है: पूरी तरह process हुए prompt का अंतिम cache आकार वही रहता है; chunking सिर्फ़ यह बदलती है कि वहाँ तक पहुँचने का काम समय पर कैसे फैला है।

</details>

4. ▢ क्या अकेला FCFS दाख़िला (बिना chunking) प्रश्न 1 की रुकावट रोक देता?

<details markdown="1"><summary>जाँचें</summary>

नहीं। FCFS सिर्फ़ यह तय करता है कि इंतज़ार कर रही कौन-सी request अगली दाख़िल हो; दाख़िल होने के बाद उस request के prefill काम का कितना हिस्सा एक अकेले step में आएगा, इस बारे में वह कुछ नहीं कहता। रुकावट पूरे बड़े prefill को एक अविभाज्य batch step में समेटने से आती है, जिसे दाख़िले का क्रम नहीं, chunking ठीक करती है।

</details>

## असली दुनिया का अभ्यास

- [ ] अपनी serving stack का chunked prefill के लिए flag या config option ढूँढें (vLLM: हाल के versions में default रूप से चालू; chunk-size setting के लिए उसके दस्तावेज़ देखें) और पढ़ें कि default chunk size क्या है।
- [ ] जिस workload के लिए आपके पास request-length data है उसके लिए मोटे तौर पर आँकें कि chunking के बिना कितनी बार कोई prompt इतना लंबा होगा कि batch step को ध्यान देने लायक़ रोक दे।
- [ ] कल: एक अनुच्छेद पढ़ें कि scheduler नई request के prefill टुकड़े को दाख़िल करने और पहले से चल रहे टुकड़े को जारी रखने में से कैसे चुनता है, जब दोनों एक ही step के budget के लिए होड़ करते हैं।

## आगे बढ़ने के लिए

- [दस्तावेज़: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [लेख: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
