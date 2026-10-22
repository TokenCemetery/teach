---
title: "13. Adapter को Merge, Save और Ship करना"
description: "Merge सटीक है; adapter एक diff है जिसे अपना base चाहिए"
type: lesson
---

# पाठ 13. Adapter को Merge, Save और Ship करना

**मिशन से संबंध:** जो adapter सिर्फ़ training script में है, वह ship नहीं हुआ। यह चरण 3 को पूरा करता है।
**मुख्य स्रोत:** [दस्तावेज़: LoRA merging, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
**पूर्व-आवश्यकताएँ:** [पाठ 8](0008-the-low-rank-idea.md), [पाठ 12](0012-reading-a-training-run.md)

## वार्म-अप

1. ▢ Overfitting वाले run से आप कौन-सा checkpoint ship करते हैं?

<details markdown="1"><summary>जाँचें</summary>

वह जो held-out loss के न्यूनतम पर है, आख़िरी step नहीं।

</details>

2. ▢ Loss curve आपको कभी क्या नहीं दिखा सकता?

<details markdown="1"><summary>जाँचें</summary>

क्या generations इस्तेमाल लायक हैं, और क्या आपके task के distribution से बाहर की क्षमताएँ बिगड़ी हैं। दोनों के लिए तय probes के सामने असली generation चाहिए।

</details>

3. ▢ Scaling के साथ LoRA update लिखें।

<details markdown="1"><summary>जाँचें</summary>

`ΔW = (α/r) · BA`, जो frozen `W₀` में जुड़ता है।

</details>

## यह जानें

### Directory में क्या है

सहेजे गए adapter में, मोटे तौर पर, यह होता है:

```text
adapter_model.safetensors   # the A and B matrices, nothing else
adapter_config.json         # base model name, r, alpha, target_modules, task_type
README.md                   # generated model card
```

छोटा, अक्सर दसियों megabytes का। और **जान-बूझकर अधूरा**: यह एक diff है, जो अपनी config में नामित सटीक base model के बिना अर्थहीन है। Base का, या उसकी किस revision का, हिसाब खो देना adapter को कचरा बना देता है।

### Ship करने के दो तरीक़े

**Unmerged।** Base load करें, load के समय adapter लगाएँ।

```text
base := load_model("<base model>", dtype: "bfloat16")
model := load_adapter(base, "runs/first-adapter/final")
```

**Merged।** Update को weights में समेट दें और adapter की संरचना हटा दें।

```python
merged = model.merge_and_unload()
merged.save_pretrained("runs/first-adapter/merged")
tokenizer.save_pretrained("runs/first-adapter/merged")
```

Tokenizer साथ में सहेजें। Tokenizer के बिना model directory एक support ticket का इंतज़ार है।

### दोनों में से चुनना

| | Unmerged | Merged |
|---|---|---|
| Disk | Base एक बार, adapters megabytes में | हर task के लिए पूरे model की copy |
| Inference की गति | हर adapt की गई layer पर दो अतिरिक्त छोटे matmuls | Base model के बिल्कुल बराबर |
| कई tasks | एक base, कई adapters, बदले जा सकने वाले | हर एक के लिए एक पूरा model |
| Deployment | Serving stack को adapters support करने होंगे | कोई भी stack जो model load करे |
| जोड़ने की क्षमता | Adapters runtime पर बदले या तौले जा सकते हैं | Merge के समय तय |

![तीन tasks को serve करना। Merged में, तीन पूरे models हर एक base weights की अपनी copy रखते हैं, एक delta के बगल में। Unmerged में, base weights की एक copy उन्हीं तीन deltas के ऊपर बैठी है।](images/how-many-copies-of-the-base.svg)

तीनों deltas दोनों तरफ़ वही तीन हैं। जो गुणा होता है वह छाया वाला हिस्सा है, जो बड़ा हिस्सा भी है।

सहज नियम: **एक-उद्देश्य वाले deployment के लिए merge करें, एक base से कई tasks serve करते समय unmerged रखें।** पाठ 25 multi-adapter serving में ठीक से जाता है।

### Merge सटीक है, दो अपवादों के साथ

क्योंकि update जोड़ने वाला और रैखिक है, merging गणितीय रूप से सटीक है। `W₀ + (α/r)BA` वही function है जो unmerged model compute करता था। कोई अनुमान नहीं और गुणवत्ता का कोई नुक़सान नहीं।

सिवाय दो मामलों के, जिन्हें जानना सार्थक है:

**Quantized base में merge करना lossy है।** अगर base 4-bit है, तो bf16 update जोड़ने के लिए dequantise करना, जोड़ना, और requantise करना पड़ता है, और requantisation का चरण जानकारी खोता है। सही क्रम है: quantized base के सामने train करें, फिर *full-precision* base में merge करें, फिर ज़रूरत हो तो merge किए हुए नतीजे को quantise करें। सीधे quantized weights में merge करने से बेवजह गुणवत्ता बिगड़ती है। चरण 4 इस पर लौटता है।

**Dropout effective scale बदलता है।** `lora_dropout` training के दौरान सक्रिय है और inference पर निष्क्रिय। यह मानक dropout व्यवहार है और आम तौर पर हानिरहित, पर इसका मतलब है कि merge किया गया weight बिना-dropout वाले रास्ते को दर्शाता है, जो सही रास्ता है।

### Merge की जाँच करें

कभी मान न लें। Outputs की तुलना करें:

```python
prompt = "<one of your fixed probes>"
# Greedy decoding, so any difference is the weights and not the sampler.
out_unmerged = unmerged_model.generate(**inputs, do_sample=False, max_new_tokens=64)
out_merged   = merged_model.generate(**inputs, do_sample=False, max_new_tokens=64)
assert tokenizer.decode(out_unmerged[0]) == tokenizer.decode(out_merged[0])
```

Greedy decoding ही मुद्दा है: sampling चालू हो तो आप merge के bug और साधारण randomness में फ़र्क़ नहीं कर सकते। छोटे संख्यात्मक फ़र्क़ फिर भी लंबी generation में देर से अलगाव पैदा कर सकते हैं, इसलिए tokens की मामूली संख्या की तुलना करें और *शुरुआती* अलगाव की जाँच करें, देर वाले की नहीं।

### एक base पर कई adapters

PEFT कई adapters थाम सकता है और उनके बीच बदल सकता है, और उन्हें weights के साथ मिला सकता है:

```python
model.load_adapter("path/to/adapter-a", adapter_name="a")
model.load_adapter("path/to/adapter-b", adapter_name="b")
model.set_adapter("a")                       # use one
model.add_weighted_adapter(["a", "b"], weights=[0.7, 0.3], adapter_name="blend")
```

भारित संयोजन सचमुच उपयोगी औज़ार है और जादू नहीं: अलग-अलग tasks पर स्वतंत्र रूप से train हुए दो adapters भरोसेमंद ढंग से मिलकर ऐसा नहीं बनते जो दोनों करे। इसे आज़माना सार्थक है और इसे मापना पड़ता है, मान लेना नहीं। Adapter अंकगणित के बारे में किसी भी दावे को अपने task पर जाँचने की चीज़ मानें।

### क्या दर्ज करें

वह सब जो दोहराने और बाद में debug करने के लिए चाहिए:

- Base model का identifier **और revision**
- Adapter config, हू-ब-हू
- Dataset की पहचान और सटीक split
- Seed, effective batch size, learning rate, schedule, steps
- आपने कौन-सा checkpoint चुना और क्यों, यानी वह held-out संख्या जिसने उसे सही ठहराया
- Library versions
- Evaluation नतीजे, regression probes समेत

यह प्रक्रिया के लिए प्रक्रिया नहीं है। छह महीने बाद "पुराना adapter नए से बेहतर क्यों है" का जवाब सिर्फ़ ऐसे रिकॉर्ड से ही दिया जा सकता है।

## अभ्यास

1. ▢ 40 MB की adapter file अकेले बेकार क्यों है?

<details markdown="1"><summary>जाँचें</summary>

उसमें सिर्फ़ `A` और `B` matrices हैं: base weights के एक ख़ास सेट के सामने एक diff। उस सटीक base model और revision के बिना उसे लगाया नहीं जा सकता, और लगभग-सही base पर लगाने से वह चुपचाप बिगड़ता है।

</details>

2. ▢ आप एक base model के पाँच fine-tuned variants serve करते हैं। Merge करें या नहीं?

<details markdown="1"><summary>जाँचें</summary>

Merge न करें। Unmerged का मतलब है memory में base की एक copy और पाँच छोटे adapters, हर request पर बदले जा सकने वाले। Merged का मतलब है पाँच पूरे model copies।

क़ीमत है हर adapt की गई layer पर दो अतिरिक्त छोटे matmuls और ऐसा serving stack जो adapters support करे।

</details>

3. ▢ आपने 4-bit quantized base के सामने train किया। सही merge प्रक्रिया बताएँ।

<details markdown="1"><summary>जाँचें</summary>

Base को full precision में load करें, adapter लगाएँ, वहीं merge करें, और अगर quantized artifact चाहिए तो बाद में merge किए model को quantise करें।

सीधे quantized weights में merge करने के लिए dequantise-जोड़ो-requantise करना पड़ता है, और requantisation बिना फ़ायदे के जानकारी खोता है।

</details>

4. ▢ आप merge करते हैं, फिर temperature 0.8 पर sampling के साथ generations की तुलना करते हैं। Outputs अलग हैं। आपने क्या सीखा?

<details markdown="1"><summary>जाँचें</summary>

कुछ नहीं। Sampling चालू हो तो अलग outputs अपेक्षित हैं, चाहे merge सही हो या नहीं।

Greedy decoding से तुलना करें, जहाँ कोई भी अलगाव weights के नाम जाता है। फिर शुरुआती अलगावों की जाँच करें; कई tokens के बाद ही दिखने वाला फ़र्क़ साधारण संख्यात्मक बहाव हो सकता है।

</details>

5. ▢ बिना quantize किए LoRA को merge करने के बारे में क्या सही है?

    - a) यह सटीक है और inference के समय कुछ नहीं लेता
    - b) इसमें थोड़ी गुणवत्ता जाती है पर inference तेज़ होता है
    - c) यह सटीक है पर inference पर ज़्यादा memory माँगता है
    - d) यह lossy है और production इस्तेमाल में इससे बचना चाहिए

<details markdown="1"><summary>जाँचें</summary>

**a)** यह सटीक है और inference के समय कुछ नहीं लेता।

Update जोड़ने वाला और रैखिक है, इसलिए वह साधारण weight matrix में समा जाता है, वही function, वही memory और कोई अतिरिक्त matmuls नहीं। यही गुण LoRA को उससे पहले के adapter-layer तरीक़ों से अलग करता था।

</details>

6. ▢ आप `add_weighted_adapter` से formatting adapter और domain-knowledge adapter को मिलाते हैं और वह दोनों से कमज़ोर निकलता है। क्या यह हैरानी की बात है?

<details markdown="1"><summary>जाँचें</summary>

नहीं। स्वतंत्र रूप से train हुए low-rank updates असंबंधित subspaces में रहते हैं, और उनका भारित योग किसी एक task के लिए अच्छा update होने की गारंटी नहीं रखता, दोनों के लिए तो और नहीं।

यह कभी-कभी अच्छा चलता है और आज़माने लायक है। यह कभी मान लेने की चीज़ नहीं; हर adapter को अकेले चलाकर उससे नापें।

</details>

## असली दुनिया का अभ्यास

- [ ] अपना adapter merge करें और अपने तय probes पर greedy decoding से जाँचें। पुष्टि करें कि outputs मेल खाते हैं।
- [ ] Directory के आकारों की तुलना करें: अकेला adapter बनाम merged model। अनुपात नोट करें।
- [ ] एक असली run के लिए ऊपर बताया गया run रिकॉर्ड पूरा लिखें।
- [ ] कल: दो adapters को एक base पर load करें और एक ही prompt के लिए उनके बीच बदलें। फ़र्क़ देखें।

## आगे बढ़ने के लिए

- [दस्तावेज़: LoRA merging, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [दस्तावेज़: Model merging, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/model_merging)
- [पाठ 25. Adapters को Serve करना](0025-serving-adapters.md)
- [failure modes शीट](../reference/failure-modes.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
