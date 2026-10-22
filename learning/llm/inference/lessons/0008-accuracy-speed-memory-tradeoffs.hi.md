---
title: "8. Accuracy, Speed और Memory के Trade-offs"
description: "Model quantize करने पर memory, speed और accuracy साथ-साथ क्यों नहीं चलते, और हर एक असल में कैसे नापा जाता है"
type: lesson
---

# पाठ 8. Accuracy, Speed और Memory के Trade-offs

**मिशन से संबंध:** पाठ 7 ने schemes के नाम बताए; यह पाठ वह है जो quantization के चुनाव का बचाव करने लायक़ बनाता है, क्योंकि weights quantize होने पर memory, speed और accuracy हर एक अलग मात्रा में और अलग कारण से बदलते हैं।
**मुख्य स्रोत:** [पेपर: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2023](https://arxiv.org/abs/2210.17323)
**पूर्व-आवश्यकताएँ:** [पाठ 7](0007-quantization-schemes.md), [KV cache](../GLOSSARY.md)

## वार्म-अप

1. ▢ Model के weights quantize करने से ख़ासकर decode ही तेज़ क्यों होता है, पूरा inference नहीं?

<details markdown="1"><summary>जाँचें</summary>

Decode memory-bandwidth bound है: हर step weights को memory से वापस पढ़ता है, और उन्हें quantize करने से उस पढ़ने में कितने bytes चलने पड़ते हैं वह घटता है। Speedup प्रति step कम memory traffic से आता है, ठीक वही अड़चन जो decode की है।

</details>

2. ▢ fp16 weight memory का मोटे तौर पर कितना हिस्सा int4 quantization इस्तेमाल करता है?

<details markdown="1"><summary>जाँचें</summary>

लगभग चौथाई, क्योंकि int4 हर byte में दो weights पैक करता है जबकि fp16 हर weight के लिए दो bytes लेता था, 8 गुना की कमी: fp16 के चौथाई तक, फिर int8 से दोबारा आधा।

</details>

## यह जानें

### तीनों में memory सबसे पूर्वानुमेय है

Quantization से memory की बचत लगभग अंकगणित है: int8 fp16 का footprint आधा करता है, int4 चौथाई, क्योंकि bit width सीधे तय करती है कि weight कितने bytes लेता है। यही वह अकेली धुरी है जिस पर पाठ 7 की संख्याएँ साफ़-साफ़ लागू होती हैं, और यह इससे स्वतंत्र है कि quantized weights किस scheme ने बनाए, naive rounding, GPTQ या AWQ।

### Speed उसी अनुपात में नहीं चलती

Quantized weight को अक्सर असली matrix multiply चलने से ठीक पहले वापस ऊँची precision में **dequantize** करना पड़ता है, क्योंकि multiply करने वाला hardware वही precision उम्मीद करता है। जब उस dequantization step में ही समय लगता है, तो wall-clock speedup memory-बचत के अनुपात से काफ़ी पीछे रह सकती है: 4 गुना छोटे weight का मतलब अपने आप 4 गुना तेज़ step नहीं है, सिर्फ़ ऐसा step है जिसमें चलाने के लिए 4 गुना कम data है, और उसके ऊपर जो भी overhead dequantize करना जोड़े। Serving stacks इस अंतर को उन kernels से पाटती हैं जो सीधे quantized format पर चलते हैं, पर सैद्धांतिक memory speedup का कितना बचता है यह kernel पर निर्भर करता है, सिर्फ़ bit width पर नहीं।

Speed का फ़ायदा request में बराबर भी नहीं मिलता। Decode, जो memory-bandwidth bound है, वहाँ छोटा weight footprint फल देता है: पढ़ने को कम, पढ़ने में कम समय। Prefill, जो compute-bound है (पाठ 3), अपना समय matrix multiply पर ही खर्च करता है, weights बार-बार पढ़ने पर नहीं, इसलिए वही quantization जो decode को ध्यान देने लायक़ तेज़ करता है, prefill को बहुत कम देता है, कभी-कभी लगभग कुछ नहीं।

### Accuracy को अंदाज़ा नहीं, संख्या चाहिए

Quantized model का सुनने में ठीक लगने वाला text बनाना इसका सबूत नहीं कि उसकी accuracy बची रही: धाराप्रवाहता सस्ती है, और model coherent पढ़ा जाते हुए भी उस task पर जो मायने रखता है अपने fp16 मूल से नापने लायक़ ख़राब हो सकता है। Quantization से accuracy की हानि नापी जाती है, आम तौर पर **perplexity** (model held-out text का कितना अच्छा अनुमान लगाता है; ऊँचा मतलब बदतर) के रूप में किसी मानक evaluation set पर, या किसी task-विशिष्ट benchmark पर score के बदलाव के रूप में जिसकी workload को सचमुच परवाह है। GPTQ का अपना मूल्यांकन ठीक यही बताता है: हर bit width पर unquantized model के मुक़ाबले नापी गई perplexity, नमूना outputs की कोई गुणात्मक राय नहीं।

### तीनों धुरियाँ सौदा करती हैं, पर साथ-साथ नहीं

fp16 से int8 पर जाने की आम तौर पर memory के पूरे आधे होने के बदले नापी गई accuracy की बहुत कम क़ीमत होती है। int8 से int4 पर जाना एक और बड़ी memory कमी ख़रीदता है पर आम तौर पर int8 वाले कदम से अनुपात से ज़्यादा accuracy ले लेता है, और ठीक इसीलिए GPTQ और AWQ मौजूद हैं: उस int4 की accuracy क़ीमत को उतना छोटा रखने के लिए जितना naive rounding नहीं रख सकता। तीनों धुरियों में से कोई मुफ़्त नहीं है, और कोई भी दूसरों के साथ किसी निश्चित अनुपात में नहीं बदलती, इसीलिए बचाव करने लायक़ चुनाव को हर एक के लिए संख्या चाहिए, यह मान लेना नहीं कि एक के सिकुड़ने से बाक़ी उतने ही सिकुड़ते हैं।

## अभ्यास

1. ▢ एक team model को int4 में quantize करती है और देखती है कि वह कुछ हाथ से दिए prompts पर अब भी धाराप्रवाह, coherent text लिखता है। क्या यह इस बात का काफ़ी सबूत है कि quantization ने accuracy को चोट नहीं पहुँचाई? क्यों या क्यों नहीं?

<details markdown="1"><summary>जाँचें</summary>

नहीं। धाराप्रवाहता सही होने या task accuracy जैसी नहीं है; model coherent पढ़ा जाते हुए भी perplexity या किसी task benchmark पर नापने लायक़ कम score कर सकता है। Accuracy की हानि के लिए नापी गई संख्या चाहिए, जैसे unquantized model के मुक़ाबले perplexity या benchmark score का फ़र्क़, कुछ outputs की गुणात्मक राय नहीं।

</details>

2. ▢ एक model int4 में quantize होता है, जो fp16 के मुक़ाबले सैद्धांतिक रूप से 4 गुना memory कमी देता है। नापा गया decode speedup 4 गुना से कम क्यों हो सकता है?

<details markdown="1"><summary>संकेत</summary>

सोचें कि quantized weight का इस्तेमाल करने वाले matrix multiply से ठीक पहले उसके साथ क्या होना पड़ता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

Quantized weights को अक्सर multiply चलने से ठीक पहले वापस ऊँची precision में dequantize करना पड़ता है, क्योंकि multiply करने वाला hardware वही precision उम्मीद करता है। अगर उस dequantization step में ही समय लगे, तो वह उस speedup को खा जाता है जो छोटा memory footprint अन्यथा ख़रीदता, इसलिए wall-clock फ़ायदा memory अनुपात से कम रह सकता है, जब तक kernel सीधे quantized format पर न चले।

</details>

3. ▢ वही int4 quantization किसी request के prefill चरण और decode चरण दोनों पर लगाया जाता है। किस चरण को बड़ा speedup मिलता है, और क्यों?

<details markdown="1"><summary>जाँचें</summary>

Decode को। वह memory-bandwidth bound है, इसलिए छोटा weight footprint पढ़ना सीधे step को छोटा करता है। Prefill compute-bound है: उसका समय matrix multiply पर हावी है, weights पढ़ने पर नहीं, इसलिए वही memory कमी उसे बहुत कम speedup देती है, कभी-कभी लगभग कुछ नहीं।

</details>

4. ▢ int8 से int4 पर जाते समय accuracy, speed और memory के trade-off के बारे में कौन-सा दावा सही है?

    - a) तीनों एक ही गुणक से सुधरते हैं, क्योंकि दोनों fp16 से 8-bit के कदम हैं
    - b) Memory पूर्वानुमेय ढंग से सुधरती है, पर speed का फ़ायदा और accuracy की क़ीमत उसके साथ उसी अनुपात में नहीं बदलते
    - c) Speed और memory साथ सुधरते हैं, और 8 bits से नीचे accuracy अप्रभावित रहती है
    - d) Bit width कुछ भी हो accuracy की हानि तय रहती है, इसलिए सिर्फ़ memory और speed में सौदा होता है

<details markdown="1"><summary>जाँचें</summary>

**b)** Memory एक पूर्वानुमेय, अंकगणितीय अनुपात से घटती है, पर wall-clock speedup dequantization overhead और kernel support पर निर्भर करता है, और accuracy की क़ीमत आम तौर पर int8 वाले कदम से तेज़ी से बढ़ती है। (a) ग़लत है: int8 से int4 एक कदम है, दो बराबर 8-bit कदम नहीं, और फ़ायदे धुरियों में एकसमान नहीं हैं। (c) ग़लत है: int4 में accuracy की हानि नापी जा सकती है और आम तौर पर int8 से बड़ी है, इसीलिए GPTQ और AWQ मौजूद हैं। (d) ग़लत है: bit width घटने पर accuracy की हानि आम तौर पर बढ़ती है, वह तय नहीं रहती।

</details>

## असली दुनिया का अभ्यास

- [ ] किसी model की fp16, int8 और int4 पर perplexity या task score की तुलना करने वाला प्रकाशित benchmark खोजें (model card या किसी पेपर की evaluation table) और पेपर की अपनी संख्याओं में नोट करें कि हर कदम की असल में कितनी क़ीमत पड़ी।
- [ ] अपनी serving stack का वह benchmark या दस्तावेज़ पृष्ठ खोजें जो अलग quantization स्तरों पर नापे गए throughput की तुलना करता हो, और रिपोर्ट किए गए speedup की तुलना उस सैद्धांतिक memory-अनुपात से करें जिसकी आप उम्मीद करते।
- [ ] कल: जिस workload के बारे में आप सोच रहे हैं उसके लिए लिखें कि quantized model भेजने से पहले आप असल में कौन-सा accuracy metric जाँचेंगे, और score में कितनी गिरावट आपको स्वीकार्य लगेगी।

## आगे बढ़ने के लिए

- [पेपर: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2023](https://arxiv.org/abs/2210.17323)
- [दस्तावेज़: "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
