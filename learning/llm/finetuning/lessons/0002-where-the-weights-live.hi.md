---
title: "2. Weights कहाँ रहते हैं"
description: "हर उस projection का नाम लेना जिससे adapter जुड़ सकता है"
type: lesson
---

# पाठ 2. Weights कहाँ रहते हैं

**मिशन से संबंध:** Adapter ख़ास weight matrices से जुड़ता है। आप यह तब तक नहीं चुन सकते कि कौन-से, जब तक आप उनके नाम न ले सकें और यह न बता सकें कि हर एक क्या करता है।
**मुख्य स्रोत:** [The Illustrated Transformer, Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
**पूर्व-आवश्यकताएँ:** [पाठ 1](0001-what-a-base-model-is.md)

## वार्म-अप

1. ▢ Language model क्या compute करता है, एक function के रूप में बताएँ।

<details markdown="1"><summary>जाँचें</summary>

अंदर token sequence, बाहर vocabulary के हर token के लिए एक score। Generation उस function के चारों ओर एक loop है, उसका हिस्सा नहीं।

</details>

2. ▢ Base model किसी instruction का पालन करने में क्यों विफल होता है?

<details markdown="1"><summary>जाँचें</summary>

Instruction following next-token prediction के ऊपर जोड़ा गया सिखाया हुआ व्यवहार है। Base model के पास सिर्फ़ next-token objective होता है, इसलिए वह तामील करने के बजाय text को आगे बढ़ाता है।

</details>

## यह जानें

आधुनिक decoder-only model का लगभग हर parameter तीन जगहों में से किसी एक में रहता है: embedding table, एक जैसे transformer blocks का ढेर, और output projection। अधिकांश parameters blocks में होते हैं, और adapters वहीं जुड़ते हैं।

### एक block के अंदर

हर block में दो उप-परतें होती हैं, हर एक से पहले एक normalisation और चारों ओर एक residual connection।

**Attention।** चार linear projections, जिनके नाम रिवाज़ से इस आधार पर रखे गए हैं कि वे क्या बनाते हैं:

| नाम | भूमिका |
|---|---|
| `q_proj` | Queries, यह position क्या खोज रही है |
| `k_proj` | Keys, हर position मेल के रूप में क्या पेश करती है |
| `v_proj` | Values, असल में वापस मिलने वाली सामग्री |
| `o_proj` | Attention के नतीजे को वापस residual stream में मिलाता है |

**MLP** (जिसे feed-forward network भी कहते हैं)। मौजूदा models में gated activations की वजह से यह आम तौर पर दो के बजाय तीन projections होते हैं:

| नाम | भूमिका |
|---|---|
| `gate_proj` | Gate बनाता है, जो एक activation से गुज़रता है |
| `up_proj` | ऊपर, चौड़े intermediate आयाम तक project करता है |
| `down_proj` | वापस नीचे hidden आयाम तक project करता है |

MLP hidden आयाम से चौड़ा होता है, आम तौर पर लगभग 2.5× से 4×, इसलिए आपकी अपेक्षा से कम matrices होने के बावजूद **MLP में attention से ज़्यादा parameters होते हैं।** यही तथ्य पाठ 10 में target-module के चुनाव को तय करता है।

### गिनती

इनपुट आयाम `d_in` और आउटपुट आयाम `d_out` वाली linear layer में `d_in × d_out` weights होते हैं। ऐसे model के लिए जिसमें hidden size 2048, 24 layers और intermediate size 5632 है:

- प्रति layer attention, grouped-query attention को अनदेखा करते हुए: 4 × 2048 × 2048 ≈ 16.8M
- प्रति layer MLP: 3 × 2048 × 5632 ≈ 34.6M
- प्रति layer कुल ≈ 51.4M, गुणा 24 layers ≈ 1.23B
- Embeddings, 32k vocabulary के साथ: 32000 × 2048 ≈ 65.5M, और output projection untied हो तो दोगुना

यह लगभग पूरा model हो जाता है। कहीं और parameters का कोई छिपा भंडार नहीं है।

### एक जाल जिसे अभी जान लेना ठीक है

ज़्यादातर मौजूदा models **grouped-query attention** इस्तेमाल करते हैं, जहाँ कई query heads keys और values का एक ही सेट साझा करते हैं। इससे `k_proj` और `v_proj`, `q_proj` और `o_proj` से *संकरे* हो जाते हैं, अक्सर चार या आठ गुना। जो भी हिसाब मानता है कि चारों attention projections वर्गाकार हैं, वह ज़्यादा गिनेगा, और यह मान लेना कि वे एक ही आकार के हैं पाठ 8 में adapter के parameters की ग़लत गिनती देगा।

### असली नाम ढूँढना

याद की हुई module-नामों की सूची पर कभी भरोसा न करें। वे model implementation तय करता है और architectures के बीच वे अलग होते हैं। उन्हें print करें:

```text
model := load_model("<some-small-model>")
for name, module in model.modules():
    if module is a linear layer:
        print(name, module.weight.shape)
```

यह पूरे workspace में अकेला सबसे उपयोगी diagnostic है। जो fine-tune चुपचाप कुछ भी train नहीं करता, उसका मतलब आम तौर पर यह होता है कि target-module का कोई नाम किसी से मेल नहीं खाया।

## अभ्यास

1. ▢ एक सामान्य आधुनिक transformer block के सातों linear projections के नाम बताएँ।

<details markdown="1"><summary>जाँचें</summary>

Attention में `q_proj`, `k_proj`, `v_proj`, `o_proj`; MLP में `gate_proj`, `up_proj`, `down_proj`।

पुरानी या non-gated architectures में MLP के सिर्फ़ दो projections होते हैं। इसीलिए आप नाम दोहराने के बजाय उन्हें print करते हैं।

</details>

2. ▢ ऐसे model के लिए जिसका hidden size 4096 और intermediate size 11008 है, प्रति layer किसमें ज़्यादा parameters हैं, attention में या MLP में? लगभग कितने गुना?

<details markdown="1"><summary>जाँचें</summary>

MLP में, लगभग दो के मुक़ाबले एक। Attention (वर्गाकार projections) 4 × 4096² ≈ 67M है। MLP 3 × 4096 × 11008 ≈ 135M है।

Grouped-query attention के साथ फ़ासला और बढ़ जाता है, क्योंकि `k_proj` और `v_proj` सिकुड़ते हैं जबकि MLP नहीं।

</details>

3. ▢ आप अपने adapter को `["query", "value"]` पर target करते हैं, ऐसे model पर जिसके modules के नाम `q_proj` और `v_proj` हैं। क्या होता है?

<details markdown="1"><summary>जाँचें</summary>

कुछ भी मेल नहीं खाता, इसलिए या तो library error देती है, या (version के हिसाब से, और बदतर) आपको ऐसा model मिलता है जिसमें कोई trainable adapter weights हैं ही नहीं। फिर training चलती है, loss मुश्किल से हिलता है, और run टूटा हुआ नहीं बल्कि बस निराशाजनक दिखता है।

Adapter बनाने के तुरंत बाद trainable-parameter की गिनती जाँचें। पाठ 11 इसे आदत बना देता है।

</details>

4. ▢ Adapters के लिए residual stream की संरचना जानना आख़िर क्यों मायने रखता है?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि adapter एक projection के output को बदलता है, और residual connection का मतलब है कि वह बदलाव एक चलती stream में जुड़ता है, उसकी जगह नहीं लेता। Adapter का छोटा योगदान stream को मोड़ सकता है, बिना उसे नष्ट किए जो frozen layers उसमें पहले ही लिख चुकी हैं। इसीलिए adapter को ठीक शून्य से शुरू करना सुरक्षित है (पाठ 9)।

</details>

5. ▢ Grouped-query attention: आपके नोट्स मानते हैं कि चारों attention projections 2048 × 2048 हैं, पर model में 32 query heads और 4 key-value heads हैं, head dimension 64 के साथ। असली आकार क्या हैं?

<details markdown="1"><summary>जाँचें</summary>

`q_proj` और `o_proj` 2048 × 2048 ही रहते हैं (32 × 64 = 2048)। `k_proj` और `v_proj` 2048 × 256 हैं (4 × 64 = 256)।

तो attention में प्रति layer लगभग 2 × 2048² + 2 × 2048 × 256 ≈ 9.4M होता है, 16.8M नहीं। आपके अनुमान का लगभग आधा।

</details>

## असली दुनिया का अभ्यास

- [ ] ऊपर का module-सूची वाला loop चलाएँ, अपनी library के असली model-inspection call (जैसे PyTorch में `named_modules()`) से, उस सबसे छोटे model पर जिसे आप download कर सकें। सातों नाम और उनके आकार अपने नोट्स में हाथ से लिखें।
- [ ] सिर्फ़ आकारों से model के parameters की कुल गिनती निकालें। उसकी तुलना उसके model card की संख्या से करें और किसी भी फ़ासले का हिसाब दें।
- [ ] कल: किसी दूसरे परिवार के model के लिए दोहराएँ। जो भी module-नाम अलग हों, सब दर्ज करें।

## आगे बढ़ने के लिए

- [The Illustrated Transformer, Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [LLM Visualization, Brendan Bycroft](https://bbycroft.net/llm): parameter की गिनतियाँ हर matrix के हिसाब से दिखाई गई हैं
- [पेपर: "Attention Is All You Need", Vaswani et al., arXiv:1706.03762](https://arxiv.org/abs/1706.03762)
- [पाठ 10. Target Modules चुनना](0010-choosing-target-modules.md) वह जगह है जहाँ इसका फल मिलता है

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
