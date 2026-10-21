---
title: "25. Adapters को Serve करना"
description: "एक task के लिए merge करें, कई के लिए route करें"
type: lesson
---

# पाठ 25. Adapters को Serve करना

**मिशन से संबंध:** "इसे ship करें" मिशन में है। किसी directory में पड़ा adapter ship नहीं हुआ।
**मुख्य स्रोत:** [दस्तावेज़: LoRA adapters, vLLM](https://docs.vllm.ai/en/latest/features/lora.html)
**पूर्व-आवश्यकताएँ:** [पाठ 13](0013-merging-and-shipping.md), [पाठ 24](0024-the-regression-suite.md)

## वार्म-अप

1. ▢ कौन-सा serving चुनाव catastrophic forgetting को अप्रासंगिक बना देता है?

<details markdown="1"><summary>जाँचें</summary>

Adapter को unmerged रखना और सिर्फ़ प्रासंगिक अनुरोधों को उसके ज़रिए भेजना, बाक़ी सबके लिए अछूता base उपलब्ध छोड़ते हुए।

</details>

2. ▢ Quantized base के सामने train हुए adapter को कहाँ merge करना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

Full-precision base में, फिर अगर quantized artifact चाहिए तो बाद में quantise करें।

</details>

3. ▢ Merge की जाँच करते समय greedy decoding क्यों?

<details markdown="1"><summary>जाँचें</summary>

ताकि output का कोई भी फ़र्क़ sampling के बजाय weights के नाम जाए।

</details>

## यह जानें

### Deployment के तीन आकार

**Merged model।** एक artifact, किसी भी दूसरे model से अलग न दिखने वाला। कोई भी serving stack उसे load करता है। Adapter की कोई मशीनरी नहीं।

**Unmerged, एक adapter।** Base और load के समय लगाया गया adapter। हर adapt की गई layer पर दो छोटे matmuls जोड़ता है।

**Unmerged, कई adapters।** Memory में एक base, कई adapters, हर अनुरोध पर चुने जाने वाले। यही वह आकार है जो adapters को आर्थिक रूप से दिलचस्प बनाता है और इसे साफ़ runtime support चाहिए।

### चुनना

| | Merged | Unmerged, multi-adapter |
|---|---|---|
| N tasks के लिए memory | N पूरे models | एक base + N छोटे adapters |
| प्रति-अनुरोध overhead | कोई नहीं | छोटा, और मिश्रित batching में बड़ा |
| Serving stack | कोई भी | Adapters support करना ज़रूरी |
| Tasks बदलना | दूसरा model load करें | अनुरोध का एक field बदलें |
| Task जोड़ना | दूसरा model deploy करें | एक file डाल दें |
| Base अब भी उपलब्ध | नहीं | हाँ |
| Rollback | दोबारा deploy | उस adapter की ओर routing रोकें |

फ़ैसले का नियम: **एक task और सरल संचालन → merge करें। कई tasks, या base की अब भी ज़रूरत → merge न करें।**

वह आख़िरी पंक्ति कम आँकी जाती है। Unmerged adapter के साथ, ख़राब fine-tune को वापस लेना deployment के बजाय routing का बदलाव है, और base model हमेशा fallback के रूप में वहाँ है।

### Multi-adapter serving कैसे काम करती है

भोला तरीक़ा, अनुरोधों के बीच adapter weights बदलना, सब कुछ क्रमवार कर देता है और throughput नष्ट कर देता है, क्योंकि batching ही वह जगह है जहाँ से inference की कुशलता आती है।

असली implementations *अलग-अलग* adapters इस्तेमाल करने वाले अनुरोधों को साथ batch करती हैं। Base model की computation पूरे batch में साझा होती है, क्योंकि वह सबके लिए एक जैसी है, और adapter के योगदान प्रति-अनुरोध विशेष kernels से compute होते हैं जो छोटे विषम matmuls के batch को सँभालते हैं। S-LoRA का काम ([arXiv:2311.03285](https://arxiv.org/abs/2311.03285)) कई adapters को एक साथ serve करने का संदर्भ बिंदु है, जिसमें निष्क्रिय adapters को host memory में रखना और उन्हें वहाँ से अंदर लाना शामिल है।

व्यवहार में इसका मतलब:

- एक base से दर्जनों adapters serve करना असली implementations के साथ हल हो चुकी समस्या है, शोध-विचार नहीं।
- Overhead छोटा पर असली है, और एक batch में कितने *अलग* adapters आते हैं उसके साथ बढ़ता है।
- जहाँ संभव हो adapters को rank और target modules साझा करने चाहिए। विषम आकारों को कुशलता से batch करना कठिन है।

vLLM में आकार मोटे तौर पर यह है: LoRA support चालू करें, adapters register करें, और हर अनुरोध में एक का नाम दें। मौजूदा flags और अधिकतम-rank व अधिकतम-adapters की सीमाएँ installed version के दस्तावेज़ में जाँचें, क्योंकि यह सतह बदलती है और सीमाएँ server शुरू होते समय तय होती हैं।

### Serving के समय quantisation, अलग रखा गया

ऊपर की हर चीज़ से स्वतंत्र एक फ़ैसला, और दोहराने लायक क्योंकि दोनों आपस में मिला दिए जाते हैं:

- **Training-समय का quantisation** (चरण 4) training run के लिए memory budget है।
- **Serving-समय का quantisation** उस model को सिकोड़ता है जो आप deploy करते हैं, और उसकी गुणवत्ता की क़ीमत हर अनुरोध के लिए स्थायी है।

आप 4-bit base के सामने train करके bf16 में serve कर सकते हैं। आप bf16 में train करके quantized serve कर सकते हैं। ये असंबंधित चुनाव हैं, असंबंधित trade-offs के साथ, और कोई भी दूसरे को निहित नहीं करता।

अगर आप quantized serve करते हैं, तो quantized artifact का evaluation करें। bf16 model का evaluation करके 4-bit वाला ship करने का मतलब है कि आपकी संख्याएँ उस चीज़ का वर्णन करती हैं जो आपने deploy नहीं की, जो हैरान करने वाली आम भूल है।

### संचालन की ज़रूरी बातें

**हर चीज़ का version रखें।** Base model और revision, adapter, tokenizer, serving stack। हर response को उस सटीक configuration तक खोजा जा सकना चाहिए जिसने उसे बनाया।

**Sampling parameters को पिन करें।** Temperature, top-p, max tokens, stop sequences। ये output की गुणवत्ता को उतना ही बदलते हैं जितना fine-tuning, और अनदर्ज default का बहाव model regression समझ लिया जाएगा।

**Inputs और outputs log करें।** Production traffic आपके अगले training सेट और अगले held-out सेट का सबसे अच्छा स्रोत है, क्योंकि वह असली distribution से लिया गया है, उससे नहीं जिसकी आपने कल्पना की थी। स्पष्ट गोपनीयता और retention की सीमाओं का पालन करें; मक़सद सोच-समझकर इकट्ठा करना है, बाद में यह पता चलने के बजाय कि आपने नहीं किया।

**Distribution की निगरानी करें, सिर्फ़ latency की नहीं।** Input की लंबाई, output की लंबाई, इनकार की दर, schema validity। Input distribution में बहाव इस बात का अग्रणी संकेतक है कि आपके fine-tune की मान्यताएँ समाप्त हो चुकी हैं।

**Base को पहुँच में रखें।** चाहे fallback रास्ते के रूप में, तुलना के endpoint के रूप में, या दोनों। Production में base के विरुद्ध fine-tune को A/B कर पाना इस बारे में उपलब्ध सबसे मज़बूत सबूत है कि fine-tune मदद करता है या नहीं।

### Sampling इलाज नहीं है

एक चेतावनी, क्योंकि यह आम जाल है। अगर fine-tune कमज़ोर निकलता है, तो temperature और top-p मरम्मत नहीं हैं। वे distribution का आकार बदलते हैं, उसकी सामग्री नहीं। Training की समस्या की भरपाई के लिए sampling को tune करना उसे छिपाता है और अगली तुलना को अव्याख्येय बना देता है: आप अब नहीं जानते कि दो चरों में से किसने फ़र्क़ पैदा किया।

Training की समस्या training में ठीक करें। Sampling को पिन करें और अकेला छोड़ दें।

## अभ्यास

1. ▢ पाँच tasks, एक base model। Merged या unmerged, और चुनाव की क्या क़ीमत है?

<details markdown="1"><summary>जाँचें</summary>

Unmerged। Memory में एक base और पाँच छोटे adapters, बनाम पाँच पूरे model copies।

क़ीमतें: serving stack को adapters support करने होंगे, और एक छोटा प्रति-अनुरोध overhead है जो एक batch में अलग adapters की संख्या के साथ बढ़ता है।

</details>

2. ▢ अनुरोधों के बीच भोला adapter swapping throughput क्यों नष्ट करता है?

<details markdown="1"><summary>जाँचें</summary>

वह अनुरोधों को adapter के हिसाब से क्रमवार कर देता है, उस batching को रोकते हुए जिस पर inference की कुशलता निर्भर है।

असली implementations अलग adapters वाले अनुरोधों को साथ batch करती हैं, base की computation साझा करती हैं और adapter के योगदान प्रति-अनुरोध विशेष kernels से compute करती हैं।

</details>

3. ▢ आपने 4-bit base के सामने train किया। क्या आपको 4-bit serve करना ज़रूरी है?

<details markdown="1"><summary>जाँचें</summary>

नहीं। Training की precision और serving की precision स्वतंत्र हैं। Full-precision base में merge करें और अगर memory हो तो bf16 serve करें।

Training-समय का quantisation run के लिए budget था। उसे artifact के साथ production में जाना ज़रूरी नहीं।

</details>

4. ▢ आपका fine-tune production में कमज़ोर निकलता है। एक सहकर्मी temperature घटाने का सुझाव देता है। मूल्यांकन करें।

<details markdown="1"><summary>जाँचें</summary>

यह outputs सुधार सकता है, और समस्या को संबोधित नहीं करता। Sampling उस distribution का आकार बदलती है जो model ने बनाया; वह ऐसी क्षमता नहीं जोड़ सकती जो model में नहीं है।

बदतर, वह दूसरा बदला हुआ चर जोड़ देता है, इसलिए अगली तुलना अव्याख्येय हो जाती है। Sampling पिन करें, training का diagnosis करें।

</details>

5. ▢ Unmerged serving का कौन-सा फ़ायदा संचालन में सबसे ज़्यादा मायने रखता है?

    - a) कई tasks serve करते समय कम memory का आकार
    - b) Routing नियम बदलकर rollback कर पाना
    - c) प्रति-अनुरोध किसी भी computational overhead का न होना
    - d) हर मौजूदा inference server से संगति

<details markdown="1"><summary>जाँचें</summary>

**b)** Routing नियम बदलकर rollback कर पाना।

(a) असली है और अक्सर मुख्य वजह है, पर रात के दो बजे आपको (b) चाहिए। (c) झूठ है, क्योंकि unmerged छोटा overhead जोड़ता है। (d) उलटा है; merged ही सार्वभौमिक रूप से संगत विकल्प है।

</details>

6. ▢ आपने bf16 में evaluate किया और 4-bit quantized model ship किया। क्या ग़लत है?

<details markdown="1"><summary>जाँचें</summary>

आपकी संख्याएँ उस model का वर्णन करती हैं जो आपने deploy नहीं किया। Serving-समय का quantisation हर अनुरोध पर स्थायी गुणवत्ता की क़ीमत लेता है, और उसे कभी मापा नहीं गया।

जो artifact आप ship करते हैं उसी का evaluation करें। हमेशा।

</details>

## असली दुनिया का अभ्यास

- [ ] अपना adapter किसी inference server से serve करें और पूरे रास्ते से एक असली completion निकालें।
- [ ] दो adapters को एक base पर load करें और अनुरोध के field से उनके बीच बदलें। पुष्टि करें कि outputs उचित ढंग से अलग हैं।
- [ ] Merged, unmerged एक-adapter, और unmerged multi-adapter के लिए latency मापें। Overhead दर्ज करें।
- [ ] कल: अपने serving रास्ते का हर version और sampling parameter एक file में लिख लें।

## आगे बढ़ने के लिए

- [दस्तावेज़: LoRA adapters, vLLM](https://docs.vllm.ai/en/latest/features/lora.html)
- [पेपर: "S-LoRA: Serving Thousands of Concurrent LoRA Adapters", Sheng et al., arXiv:2311.03285](https://arxiv.org/abs/2311.03285)
- [पाठ 26. Cost, Latency और Throughput](0026-cost-latency-and-throughput.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
