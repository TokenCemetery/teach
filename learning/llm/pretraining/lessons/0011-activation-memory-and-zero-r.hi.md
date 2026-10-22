---
title: "11. Activation Memory और ZeRO-R"
description: "Model states की sharding एक memory समस्या सुलझाती है और दूसरी, यानी activations, को खड़ा छोड़ देती है"
type: lesson
---

# पाठ 11. Activation Memory और ZeRO-R

**मिशन से संबंध:** "समझाएँ कि ZeRO/FSDP क्या shard करते हैं, data parallelism अकेला compute ख़त्म होने से पहले memory से क्यों बाहर हो जाता है, और tensor या pipeline parallelism अपनी communication लागत के लायक़ कब है" "सफलता कैसी दिखती है" का चौथा बिंदु है। पाठ 9 और 10 ने ZeRO-DP के तीन stages को कवर किया, जो model states को shard करते हैं; यह पाठ उस अलग memory समस्या को कवर करता है जिसे वे तीनों stages नहीं छूते।
**मुख्य स्रोत:** [पेपर: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**पूर्व-आवश्यकताएँ:** [पाठ 10](0010-zero-stage-3-and-fsdp-partitioning-parameters-too.md), [Activation checkpointing](../GLOSSARY.md)

## वार्म-अप

1. ▢ PyTorch का FSDP दस्तावेज़ ख़ुद को किस ZeRO stage से प्रेरित बताता है?

<details markdown="1"><summary>जाँचें</summary>

ZeRO stage 3 (`P_os+g+p`), वह stage जो optimizer state और gradients के ऊपर parameters को partition करता है।

</details>

2. ▢ Parameters को partition करना (stage 3) ऐसा communication क्यों जोड़ता है जो optimizer state और gradients को partition करना (stages 1 और 2) नहीं जोड़ता?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि हर device के forward और backward pass को हर parameter चाहिए, सिर्फ़ वह shard नहीं जिसका वह मालिक है, इसलिए छूटे हुए shards ज़रूरत पर दूसरे devices से इकट्ठा करने पड़ते हैं, optimizer state और gradients के उलट, जिन्हें सिर्फ़ मालिक device कभी चाहता है।

</details>

## यह जानें

### Model states सुलझाने पर दूसरी समस्या खड़ी रह जाती है

पाठ 9 और 10 ने **ZeRO-DP** को कवर किया: वे तीन stages जो optimizer state, gradients और parameters को partition करते हैं, यानी वे 16 bytes प्रति parameter जो पाठ 8 ने गिने थे। Rajbhandari et al. साफ़ कहते हैं कि यह पूरी memory तस्वीर नहीं है। जब model states हावी रहना बंद कर देते हैं, तो जिसे वे **residual memory** कहते हैं, यानी forward pass से रखे गए activations जो backward pass में gradients निकालने के काम आते हैं, अस्थायी buffers, और fragmentation में खोई memory, अगली अड़चन बन जाती है। पाठ 8 का अपना GPT-2 उदाहरण दिखाता है कि यह छोटा असर नहीं है: 1,024 के sequence length और 32 के batch size पर लगभग 60 GB activation memory, उस model पर जिसकी अकेली model states सिर्फ़ 24 GB थीं। तीनों ZeRO-DP stages उन 60 GB के लिए कुछ नहीं करते; वे सिर्फ़ 24 GB को संबोधित करते हैं। **ZeRO-R** residual पक्ष का Rajbhandari et al. का अलग उत्तर है।

### Checkpointing मदद करती है, पर अपने-आप में काफ़ी नहीं

Activation checkpointing, जिस शब्दावली-शब्द से यह पाठ link करता है, forward pass के दौरान ज़्यादातर बीच के activations हटा देती है और backward pass में उन्हें दोबारा compute करती है, बजाय उन सबको पूरे समय memory में रखने के, यानी कम memory के बदले ज़्यादा compute। Rajbhandari et al. ध्यान दिलाते हैं कि checkpointing मदद करती है पर सबसे बड़े models के लिए अकेले काफ़ी नहीं है: checkpointing जो घटा हुआ activations का सेट रखती है वह भी बड़ा हो सकता है, और जिन setups में data parallelism को model parallelism के साथ जोड़ा जाता है, वहाँ वह घटा हुआ सेट अक्सर बेवजह उन model-parallel ranks में दोहराया जाता है जो उसे इसके बजाय साझा कर सकते थे।

### ZeRO-R ऊपर से क्या जोड़ता है

ZeRO-R residual memory पर तीन मोर्चों से हमला करता है, हर एक उसके अलग हिस्से पर निशाना साधता है:

- **Activation partitioning.** जहाँ model-parallel training वरना हर model-parallel rank पर उन्हीं activations की फ़ालतू copy रखती, ZeRO-R उस दोहराव को पहचानकर हटाता है, activations को उसी तरह partition करके जैसे ZeRO-DP model states को करता है, और जब वह सौदा करने लायक़ हो तो partition किए activations को CPU memory में **offload** भी कर सकता है।
- **सही आकार के अस्थायी buffers.** Training के दौरान इस्तेमाल होने वाले बड़े अस्थायी buffers को जान-बूझकर चुना हुआ आकार दिया जाता है, जो memory उपयोग और computational कुशलता में संतुलन बिठाता है, बजाय इसके कि उन्हें उतना बड़ा होने दिया जाए जितना भोला implementation देता।
- **Defragmentation.** बहुत अलग lifetimes वाले tensors (कुछ पूरे training step भर जीते हैं, कुछ बस पल भर) समय के साथ बिखरी हुई memory बनाते हैं, जिससे कुल free memory काफ़ी होने पर भी memory allocation विफल हो सकता है। ZeRO-R हर tensor की अपेक्षित lifetime के आधार पर memory को पहले से सँभालता है, ताकि वह बिखराव जमा न हो।

Rajbhandari et al. ZeRO-DP और ZeRO-R को मिलाकर बस **ZeRO** कहते हैं: एक आधा model states के फ़ालतूपन को हटाता है, दूसरा आधा बाक़ी हर उस चीज़ को क़ाबू में रखता है जो training memory में रखती है।

## अभ्यास

1. ▢ एक team ने model पर ZeRO stage 3 लगा लिया है, जिससे उसकी model-state memory budget के भीतर आ गई है, पर run लंबे sequence length पर forward pass के दौरान अब भी memory से बाहर हो जाता है। क्या यह सबसे संभावित रूप से model-states की समस्या है या residual-memory की, और एक चीज़ क्या हो सकती है जो इसे सुलझाए?

<details markdown="1"><summary>जाँचें</summary>

Residual-memory की समस्या, सबसे संभावित रूप से activation memory, जो sequence length के प्रति ऐसे संवेदनशील है जैसे model states नहीं हैं। Activation checkpointing, activation partitioning, या activations को CPU पर offload करना, सब residual-memory तकनीकें हैं जो इसे सुलझा सकती हैं; और ZeRO-DP sharding जोड़ने से नहीं सुलझेगी, क्योंकि यहाँ अड़चन model states नहीं थे।

</details>

2. ▢ इनमें से कौन-सा सबसे अच्छा बताता है कि अकेली activation checkpointing को सबसे बड़े models के लिए अपर्याप्त क्यों कहा गया है?

    - a) Checkpointing ZeRO-DP के साथ असंगत है और उसके साथ इस्तेमाल नहीं हो सकती
    - b) Checkpointing जो घटा हुआ activations का सेट रखती है वह भी बड़ा हो सकता है, और आगे के optimization के बिना model-parallel ranks में बेवजह दोहराया जा सकता है
    - c) Checkpointing कम compute के बदले memory उपयोग बढ़ाती है
    - d) Checkpointing सिर्फ़ उन models पर काम करती है जो mixed precision के बिना train हुए हों

<details markdown="1"><summary>जाँचें</summary>

**b)** पेपर का अपना तर्क है। (a) ग़लत है; ZeRO-R को checkpointing का पूरक बताया गया है, न कि ऐसा विकल्प जो उससे टकराता हो। (c) असली सौदे को उलट देता है, जो ज़्यादा recomputation के बदले कम memory है। (d) ऐसी कोई बाध्यता नहीं है जिसका पेपर वर्णन करता हो।

</details>

3. ▢ ZeRO-R जिन तीन चीज़ों को optimize करता है उनके नाम बताइए, और हर एक को उस residual-memory समस्या से मिलाइए जिसे वह निशाना बनाता है: model-parallel ranks में बेवजह दोहराए गए activations, कुल free memory काफ़ी होने पर भी memory allocation का विफल होना, और ज़रूरत से बड़े होने के लिए छोड़े गए अस्थायी buffers।

<details markdown="1"><summary>जाँचें</summary>

Activation partitioning (और offload) model-parallel ranks में दोहराए गए activations को संबोधित करता है। Defragmentation, हर tensor की अपेक्षित lifetime के आधार पर, बिखरी memory से आने वाली allocation विफलताओं को संबोधित करता है। सही आकार के अस्थायी buffers उन buffers को संबोधित करते हैं जो memory और compute कुशलता के संतुलन से ज़्यादा बड़े हो जाते हैं।

</details>

## असली दुनिया का अभ्यास

- [ ] उस training framework में खोजें जिस तक आपकी पहुँच है कि activation checkpointing (जिसे कभी-कभी gradient checkpointing भी कहते हैं) option के रूप में कहाँ दिया गया है, और अगर दस्तावेज़ बताता है तो नोट करें कि उसकी अतिरिक्त compute में क्या क़ीमत है।
- [ ] पाठ 8 के GPT-2 activation-memory उदाहरण (sequence length 1,024, batch size 32 पर लगभग 60 GB) का इस्तेमाल करके गुणात्मक रूप से अनुमान लगाएँ कि sequence length दोगुना करने पर उस संख्या का क्या होता है, और अपने अनुमान को framework के दस्तावेज़ के किसी भी formula या स्पष्टीकरण से मिलाकर जाँचें जो activation memory की scaling के बारे में हो।
- [ ] कल: किसी ऐसे model और hardware setup के लिए जिस तक आपकी पहुँच है (या काल्पनिक), तय करें कि आप सबसे पहले कौन-सी residual-memory तकनीक (checkpointing, activation partitioning, CPU offload, या कोई मेल) अपनाएँगे, और एक वाक्य लिखें कि क्यों, यह देखते हुए कि हर एक किसका सौदा करती है।

## आगे बढ़ने के लिए

- [पेपर: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [संसाधन](../RESOURCES.md)

---

चरण 5 ने कवर किया कि एक training run की memory ऐसे devices में कैसे shard होती है जो सब एक ही तरह का काम कर रहे हैं। चरण 6 एक अलग तरह के बँटवारे को कवर करता है: model को ही ऐसे devices में बाँटना जिनमें से हर एक computation का अलग हिस्सा करता है।

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
