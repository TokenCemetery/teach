---
title: "4. Static बनाम Continuous Batching"
description: "Requests को साथ batch करना throughput के लिए अच्छा क्यों है, और continuous batching static वाले से बेहतर क्यों है"
type: lesson
---

# पाठ 4. Static बनाम Continuous Batching

**मिशन से संबंध:** Batching वह उपाय है जो server की KV cache capacity को, जिसका हिसाब पाठ 1 से 3 ने सिखाया, असली serve किए गए throughput में बदलता है; server कितनी अच्छी तरह batch करता है, यही तय करता है कि उस capacity का कितना हिस्सा काम के काम में लगता है।
**मुख्य स्रोत:** [लेख: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
**पूर्व-आवश्यकताएँ:** [पाठ 3](0003-growth-prefill-decode-precision.md), [KV cache](../GLOSSARY.md)

## वार्म-अप

1. ▢ Decode compute-bound के बजाय memory-bandwidth bound क्यों है?

<details markdown="1"><summary>जाँचें</summary>

हर decode step सिर्फ़ एक नया token compute करने के लिए attend करने को पूरा KV cache वापस पढ़ता है। हर step में नया compute, cache और weights पढ़ने के memory traffic की तुलना में छोटा होता है।

</details>

2. ▢ पाठ 3 ने prefill और decode में फ़र्क़ किया था। इनमें से कौन-सा पूरे prompt को एक ही forward pass में process करता है?

<details markdown="1"><summary>जाँचें</summary>

Prefill। Decode इसके बजाय हर step में एक output token generate करता है और cache को एक token जितना बढ़ाता है।

</details>

## यह जानें

### Decode steps को साथ batch करना मदद क्यों करता है

Decode step का memory traffic, यानी model के weights और हर मौजूद sequence का KV cache पढ़ना, ज़्यादा नहीं बदलता चाहे वह एक sequence का अगला token compute करे या कई sequences के अगले tokens एक साथ। कई sequences के decode steps को साथ batch करना उसी memory traffic को ज़्यादा काम के compute पर फैला देता है, और memory-bandwidth-bound step को ठीक यही उपाय चाहिए: हर पढ़े गए byte पर ज़्यादा काम।

### Static batching यह फ़ायदा असमान ख़त्म होने के समय पर गँवा देती है

Batch करने का सीधा तरीक़ा है requests का एक निश्चित समूह बनाना, decode steps तब तक चलाना जब तक उनमें से हर एक ख़त्म न हो जाए, फिर अगला समूह शुरू करना। यह **static batching** है, और इसमें एक गंभीर खोट है: समूह तब तक ख़त्म नहीं हो सकता जब तक उसका सबसे देर तक चलने वाला sequence ख़त्म न हो। जो sequence जल्दी ख़त्म होता है वह भी batch का एक slot घेरे रहता है और कोई योगदान नहीं देता, जब तक पूरा समूह ख़त्म न हो।

चार requests को साथ batch करें, जिन्हें क्रमशः 10, 20, 30 और 100 output tokens चाहिए। Batch 100 steps चलता है, क्योंकि सबसे लंबे sequence को उतना चाहिए। उन 100 steps में batch GPU के काम के `4 × 100 = 400` slot-steps खपाता है, पर उनमें से सिर्फ़ `10 + 20 + 30 + 100 = 160` slot-steps ने कोई काम का काम किया। बाक़ी 240 उन sequences पर गए जो पहले ही ख़त्म हो चुके थे और batch की सीमा तक ख़ाली बैठे रहे। यह 60% बरबादी है, और यह तब और बढ़ती है जब requests की lengths का फैलाव बढ़ता है, जो सामान्य स्थिति है: असली requests कितना generate करती हैं, इसमें बहुत ज़्यादा फ़र्क़ होता है।

### Continuous batching batch की सीमा हटा देती है

**Continuous batching** (जिसे iteration-level scheduling भी कहते हैं) निश्चित समूह के बजाय एक अकेले decode step के स्तर पर schedule करती है। जैसे ही कोई sequence ख़त्म होता है, उसका slot मुक्त हो जाता है और अगले ही step पर इंतज़ार कर रही कोई नई request batch में दाख़िल कर ली जाती है, इस इंतज़ार के बिना कि उसके पुराने समूह के बाक़ी सब sequences भी ख़त्म हों। Batch की बनावट लगातार बदलती है; जो लगभग स्थिर रहता है वह उसका आकार है, किसी एक request की उम्र नहीं।

चार-request वाले उदाहरण में, सिर्फ़ 10 tokens चाहने वाला sequence step 10 पर अपना slot मुक्त कर देता है। Static scheduler उस slot को 90 steps और ख़ाली छोड़ता है। Continuous scheduler उसमें तुरंत नई request दाख़िल कर देता है, इसलिए GPU उस slot में किसी मनमानी सीमा तक मृत बोझ ढोने के बजाय काम का काम करता रहता है। इस पाठ का मुख्य स्रोत जो throughput फ़ायदे बताता है, उनके पीछे यही तंत्र है: प्रति-step computation का तेज़ होना नहीं, बल्कि हर step का बहुत कम हिस्सा उन sequences पर बरबाद होना जिनके पास करने को कुछ बचा नहीं था।

![100 decode steps में दो batch slots: slot A को 10 steps चाहिए, slot D को 100। Static batching में slot A step 10 पर ख़त्म होता है और 90 steps तक ख़ाली बैठा रहता है जब तक पूरा batch साथ ख़त्म न हो। Continuous batching में slot मुक्त होते ही, step 10 पर, उसमें नई request दाख़िल हो जाती है, इसलिए slot काम का काम करता रहता है।](images/static-vs-continuous-batching.svg)

## अभ्यास

1. ▢ एक static batch में दो requests हैं जिन्हें 15 और 60 output tokens चाहिए। Batch कुल कितने slot-steps खपाता है, उनमें कितने काम के हैं, और कितना हिस्सा बरबाद होता है?

<details markdown="1"><summary>संकेत</summary>

कुल slot-steps `batch size × सबसे लंबे sequence के ख़त्म होने तक के steps` है। काम के slot-steps हर request की असली length का जोड़ हैं।

</details>

<details markdown="1"><summary>जाँचें</summary>

कुल: `2 × 60 = 120` slot-steps। काम के: `15 + 60 = 75`। बरबाद: `120 − 75 = 45`, जो `45 / 120 = 37.5%` है।

</details>

2. ▢ Continuous-batching scheduler में, ठीक जिस step पर batch का कोई sequence generate करना ख़त्म करता है, तब क्या होता है?

<details markdown="1"><summary>जाँचें</summary>

उसका slot तुरंत मुक्त हो जाता है, और अगले step पर इंतज़ार कर रही नई request उस slot में दाख़िल कर ली जाती है, इसके बजाय कि slot तब तक ख़ाली बैठा रहे जब तक किसी निश्चित समूह के बाक़ी सब sequences भी ख़त्म न हों।

</details>

3. ▢ Static batching की तुलना में continuous batching के बारे में कौन-सा दावा सही है?

    - a) वह attention की प्रति-step compute लागत ही घटा देती है
    - b) वह ख़त्म हुए sequences के KV cache की ज़रूरत उन्हें हटाने से पहले ही ख़त्म कर देती है
    - c) वह slots मुक्त होते ही नई requests दाख़िल करके batch को भरा रखती है, किसी निश्चित समूह के पूरी तरह ख़त्म होने का इंतज़ार किए बिना
    - d) वह सिर्फ़ llama.cpp जैसे CPU serving stacks पर लागू होती है

<details markdown="1"><summary>जाँचें</summary>

**c)** वह batch को लगातार भरा रखती है। (a) ग़लत है: प्रति-step arithmetic वही रहता है; फ़ायदा कम बरबाद slot-steps का है। (b) ग़लत और उल्टा है: ख़त्म हुए sequence का cache उसे हटाने के हिस्से के रूप में मुक्त होता है, दोनों scheduling शैलियों में। (d) ग़लत है: continuous batching GPU-serving की scheduling तकनीक है, जो ख़ासकर vLLM और ऐसे ही engines से जुड़ी है।

</details>

4. ▢ 8 requests के एक static batch में हर एक को ठीक 50 output tokens चाहिए। क्या इस ख़ास batch के लिए continuous batching static batching से throughput सुधारेगी, और क्यों या क्यों नहीं?

<details markdown="1"><summary>जाँचें</summary>

मुश्किल से, अगर सुधारे भी। Continuous batching का फ़ायदा उन slots को भरने से आता है जो जल्दी ख़त्म होने वाली requests ने मुक्त किए जबकि बाक़ी चलती रहीं। जब समूह की हर request को ठीक उतने ही tokens चाहिए, तो कोई जल्दी ख़त्म होने वाली request नहीं है और भरने के लिए कोई ख़ाली slot नहीं, इसलिए static batching यहाँ पहले से कुछ बरबाद नहीं करती।

</details>

## असली दुनिया का अभ्यास

- [ ] वह flag या config option ढूँढें जो आपकी चुनी serving stack continuous batching चालू करने के लिए इस्तेमाल करती है (vLLM इसे default रूप से चालू रखता है; देखें कि उसके दस्तावेज़ उस अंतर्निहित तंत्र को क्या कहते हैं)।
- [ ] जिन requests के traffic sample या log तक आपकी पहुँच है (या LLM request lengths का कोई public dataset) उसे देखें और सबसे छोटी और सबसे लंबी output length के बीच का फैलाव आँकें। आँकें कि वह फैलाव static-batching की बरबादी का कितना अंश पैदा करेगा।
- [ ] कल: एक अनुच्छेद पढ़ें कि continuous-batching scheduler कैसे तय करता है कि इंतज़ार कर रही कौन-सी request अगली दाख़िल हो, और नोट करें कि वह सीधा आने का क्रम है या कुछ और।

## आगे बढ़ने के लिए

- [लेख: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [दस्तावेज़: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
