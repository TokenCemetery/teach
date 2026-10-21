---
title: "1. KV Cache"
description: "Generation महँगी क्यों हो जाती है, और caching क्या वापस दिलाती है"
type: lesson
---

# पाठ 1. KV Cache

**मिशन से संबंध:** इस workspace में जिस भी latency और throughput संख्या का बचाव किया जाता है, वह लौटकर इसी पर आती है कि KV cache memory में कितना लेता है और server उस लागत को कितनी अच्छी तरह सँभालता है।
**मुख्य स्रोत:** [दस्तावेज़: "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
**पूर्व-आवश्यकताएँ:** कोई नहीं

## यह जानें

### Decoding को cache की ज़रूरत ही क्यों है

Transformer एक बार में एक token generate करता है। Token *N* बनाने के लिए self-attention को 1 से *N* तक हर token के key और value vectors चाहिए, हर layer पर। Cache के बिना हर नया token model को *पूरे* prefix के keys और values फिर से compute करने पर मजबूर करता है, जबकि वे vectors token generate होने के बाद कभी बदलते नहीं। यह quadratic काम है, जो पहले से compute हो चुकी चीज़ें दोबारा compute करने में खर्च होता है।

**KV cache** हर token के key और value vectors को, हर layer के हिसाब से, पहली बार compute होते ही सहेज लेता है, ताकि token *N+1* generate करने में सिर्फ़ K/V vectors का एक नया सेट compute हो और बाक़ी दोबारा इस्तेमाल हो जाएँ। यही autoregressive generation को व्यावहारिक बनाता है: वह recomputation के बदले memory देता है।

### उस memory की असल में क्या क़ीमत है

Cache मुफ़्त नहीं है, और उसका आकार ही तय करता है कि server एक समय में कितनी requests memory में रख सकता है। हर token के लिए, हर layer पर, वह एक key और एक value vector रखता है, जिनमें से हर एक का आकार model की hidden dimension (`d_model`, model की residual stream का आयाम) के बराबर होता है। Half precision में (हर value 2 bytes):

```text
bytes per token = 2 (K and V) × num_layers × d_model × 2 bytes
```

एक ठोस उदाहरण के लिए Llama-2-7B लें: 32 layers, `d_model` = 4096।

```text
2 × 32 × 4096 × 2 bytes = 524,288 bytes ≈ 512 KB per token
```

4096-token context पर यह `512 KB × 4096 ≈ 2 GB` है, सिर्फ़ *एक* sequence के लिए। ऐसे 16 sequences एक साथ रखें तो अकेले cache को ~32 GB चाहिए, जो model के अपने weights के fp16 में लिए 14 GB से ज़्यादा है। यही हिसाब बताता है कि "बस और KV cache जोड़ दो" ग़लत सहज प्रवृत्ति क्यों है, और serving stacks cache memory को बाद की बात मानने के बजाय उस पर इतना ध्यान क्यों देते हैं (पूरा derivation, और यह भी कि GQA/MQA जैसी attention-head sharing योजनाओं के साथ यह कैसे बदलता है, देखने के लिए Kipply का [Transformer Inference Arithmetic](https://kipp.ly/transformer-inference-arithmetic/) देखें)।

### Naive caching memory कहाँ बरबाद करती है

Naive implementation हर sequence के लिए एक सटा हुआ (contiguous) memory block आरक्षित करती है, जिसका आकार उस अधिकतम sequence length के हिसाब से होता है जहाँ वह कभी पहुँच सकता है। इससे दो विफलताएँ निकलती हैं:

- **Internal fragmentation**: जो sequence छोटा रह जाता है वह फिर भी उस अधिकतम length के लिए आरक्षित memory पकड़े रहता है जो उसने कभी इस्तेमाल नहीं की।
- **External fragmentation**: अलग-अलग असली length वाले sequences अपने आरक्षित blocks के बीच ऐसी ख़ाली जगहें छोड़ देते हैं जिनमें किसी और sequence का cache समा नहीं सकता।

PagedAttention के पेपर ने नापा कि naive systems आवंटित KV cache memory का सिर्फ़ 20 से 40% हिस्सा ही काम के data के लिए इस्तेमाल करते हैं। उसका समाधान सीधे operating-system की virtual memory से उधार लिया गया है: cache को निश्चित आकार के blocks में बाँटें, उन्हें बिना सटे रखें, और हर sequence के लिए एक block table रखें जो logical positions को physical blocks से जोड़ती है। vLLM इसी विचार पर बना है, और इसीलिए framework उतना ही मायने रखता है जितना हिसाब: वही cache, ठीक से आवंटित हो तो, कहीं ज़्यादा concurrent requests serve करता है।

![ऊपर: naive, सटे हुए, अधिकतम-length के आकार वाले blocks memory को internal fragmentation (आरक्षित पर अनइस्तेमाल) और external fragmentation (blocks के बीच की ख़ाली जगह) के रूप में बरबाद करते हैं। नीचे: PagedAttention के निश्चित आकार वाले, बिना सटे blocks आपस में खुलकर गुँथ जाते हैं, इसलिए sequence उतने ही blocks रखता है जितने उसने असल में इस्तेमाल किए।](images/paged-attention-fragmentation.svg)

## अभ्यास

1. ▢ एक वाक्य में बताएँ: पहले token के बाद हर generate हुए token पर KV cache server को क्या छोड़ने देता है?

<details markdown="1"><summary>जाँचें</summary>

Sequence के हर पिछले token के key और value vectors को, हर layer पर, दोबारा compute करना। सिर्फ़ नए token के K/V compute करने पड़ते हैं; बाक़ी cache से पढ़ लिए जाते हैं।

</details>

2. ▢ एक model में 40 layers और `d_model` = 5120 है, fp16 में serve होता है। 2048-token context पर एक sequence के लिए KV cache का आकार अनुमान से निकालें।

<details markdown="1"><summary>संकेत</summary>

`2 × num_layers × d_model × 2 bytes` इस्तेमाल करें, फिर tokens की संख्या से गुणा करें।

</details>

<details markdown="1"><summary>जाँचें</summary>

प्रति token: `2 × 40 × 5120 × 2 = 819,200 bytes ≈ 800 KB`।
2048 tokens पर: `800 KB × 2048 ≈ 1.6 GB`, एक sequence के लिए।

</details>

3. ▢ दो sequences naive, सटे हुए, अधिकतम-length के आकार वाले KV cache blocks रखते हैं। एक अपनी आरक्षित अधिकतम length से बहुत पहले ख़त्म हो जाता है। उसकी आरक्षित पर अनइस्तेमाल रही memory का क्या होता है, और server को इसकी क्या क़ीमत चुकानी पड़ती है?

<details markdown="1"><summary>जाँचें</summary>

वह आरक्षित पड़ी रहती है और उस sequence का cache मुक्त होने तक कोई दूसरा sequence उसे इस्तेमाल नहीं कर सकता: यह internal fragmentation है। क़ीमत यह कि server असल में कम concurrent sequences serve कर पाता है, क्योंकि जो memory "आवंटित" दिखती है वह कोई काम का काम नहीं कर रही।

</details>

4. ▢ PagedAttention के समाधान के बारे में कौन-सा दावा सही है?

    - a) वह किसी दिए model और context length के लिए KV cache का कुल आकार घटा देता है
    - b) वह KV cache हटा देता है और attention को ज़रूरत पर दोबारा compute करता है
    - c) वह cache को निश्चित आकार के, बिना सटे blocks में रखकर बरबाद memory घटाता है
    - d) वह सिर्फ़ llama.cpp जैसे CPU serving stacks की मदद करता है

<details markdown="1"><summary>जाँचें</summary>

**c)** वह cache को निश्चित आकार के, बिना सटे blocks में रखकर बरबाद memory घटाता है, जिन्हें हर sequence की block table से address किया जाता है, यानी OS की virtual memory paging वाला ही विचार।

(a) ग़लत है: प्रति-token लागत वही रहती है; सिर्फ़ उसके आसपास की बरबादी घटती है। (b) ग़लत है: cache अब भी है, बस बेहतर ढंग से आवंटित है। (d) ग़लत है: PagedAttention GPU-serving की तकनीक है (vLLM); इस workspace में llama.cpp अलग से कवर होता है।

</details>

## असली दुनिया का अभ्यास

- [ ] ऐसा model चुनें जिसे आप serve करने की सोच रहे हैं। उसके प्रकाशित `num_layers` और hidden size से ऊपर के formula के हिसाब से उसका KV-cache-per-token आकार निकालें।
- [ ] उसी model के पूरे weights का आकार उस precision में निकालें जिसमें आप उसे serve करेंगे, और उसकी तुलना उसकी अधिकतम context length पर KV cache के आकार से करें।
- [ ] कल: किसी एक serving stack (vLLM या llama.cpp) के दस्तावेज़ खोजें और वह flag ढूँढें जो तय करता है कि वह KV cache के लिए कितनी memory आरक्षित करता है।

## आगे बढ़ने के लिए

- [लेख: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
- [पेपर: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
