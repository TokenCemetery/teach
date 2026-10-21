---
title: "7. Activations, Batch Size और Checkpointing"
description: "Adapter run फिर भी memory से बाहर क्यों हो जाता है"
type: lesson
---

# पाठ 7. Activations, Batch Size और Checkpointing

**मिशन से संबंध:** Adapters optimizer की लागत हटाते हैं, activation की लागत नहीं, इसीलिए LoRA run फिर भी memory से बाहर हो सकता है। यही वह हिस्सा है जो लोगों को चौंकाता है।
**मुख्य स्रोत:** [पेपर: "Training Deep Nets with Sublinear Memory Cost", Chen et al., arXiv:1604.06174](https://arxiv.org/abs/1604.06174)
**पूर्व-आवश्यकताएँ:** [पाठ 6](0006-gradients-and-optimizer-state.md)

## वार्म-अप

1. ▢ AdamW, mixed precision में प्रति trainable parameter bytes?

<details markdown="1"><summary>जाँचें</summary>

सोलह bytes: bf16 weights के दो, fp32 master copy के चार, bf16 gradient के दो, और दोनों moments के चार-चार।

</details>

2. ▢ प्रति frozen parameter bytes?

<details markdown="1"><summary>जाँचें</summary>

दो, bf16 में, सिर्फ़ weight value के लिए। कोई gradient नहीं, कोई moments नहीं, कोई master copy नहीं।

</details>

3. ▢ Transformers के लिए AdamW के moments को सीधे हटाया क्यों नहीं जा सकता?

<details markdown="1"><summary>जाँचें</summary>

Transformer के parameters में gradient का परिमाण बहुत ज़्यादा बदलता है, और second moment वह प्रति-parameter step scaling देता है जो एक अकेला global learning rate नहीं दे सकता।

</details>

## यह जानें

Gradients और optimizer state **parameter की गिनती** के साथ scale होते हैं। Activations **batch size और sequence length** के साथ scale होते हैं, और इस पर लगभग निर्भर नहीं करते कि कितने parameters trainable हैं। Base को freeze करना यहाँ बिल्कुल मदद नहीं करता।

### Activations होते क्यों हैं

Backward pass को उस layer का gradient compute करने के लिए हर layer का input चाहिए। इसलिए forward pass अपने बीच के नतीजे फेंकने के बजाय रखता है। हर रखा गया tensor लगभग इतना होता है:

```text
batch_size × sequence_length × hidden_size × bytes_per_element
```

प्रति tensor, और एक transformer block ऐसे लगभग एक दर्जन रखता है: हर normalisation के बाद, हर projection के बाद, attention output, अपने चौड़े आयाम पर MLP का बीच वाला नतीजा, और इसी तरह। इसे layers की संख्या से गुणा करें।

bf16 transformer block के लिए एक मोटा काम-चलाऊ आँकड़ा, उल्लेखनीय tensors गिनकर:

```text
activations ≈ n_layers × batch × seq_len × hidden × ~20 bytes
```

Constant को नापने की शुरुआती जगह मानें, नियम नहीं, क्योंकि यह attention implementation, activation function, और framework operations को fuse करता है या नहीं, इसके साथ बदलता है। मायने यह रखता है कि सूत्र का *आकार* क्या है।

### आकार के नतीजे

**Batch size में रैखिक।** Batch दोगुना, activation memory दोगुनी। यही वह knob है जिस तक आप सबसे पहले पहुँचते हैं, और gradient accumulation (पाठ 4) memory के हिसाब से मुफ़्त में effective batch size वापस दे देता है।

Stored activations के लिए **sequence length में रैखिक**, और attention score matrix के लिए वर्गीय, जब तक आप memory-efficient attention kernel इस्तेमाल न करें। FlashAttention जैसी आधुनिक implementations पूरी `seq_len × seq_len` matrix को materialise करने से बचती हैं, जिससे वर्गीय पद हट जाता है। अगर लंबी sequences पर आप अब भी वर्गीय उछाल से टकरा रहे हैं, तो इलाज attention implementation है, batch size नहीं।

24-layer model के लिए, hidden size 2048, batch 4, sequence length 2048, काम करके:

```text
24 × 4 × 2048 × 2048 × 20 bytes ≈ 8.0 GB
```

आठ gigabytes activations, लगभग 2.2 GB frozen bf16 weights और adapter state के कुछ दर्जन megabytes के सामने। **अब activations ही हावी लागत हैं।** यह एक सामान्य adapter run का memory profile है, और पाठ 6 के full fine-tuning profile का उलटा है।

### Gradient checkpointing

इसे ठीक करने वाला सौदा: ज़्यादातर activations को store मत करो। कुछ store करो, और बाक़ी backward pass के दौरान दोबारा compute करो।

हर block का input रखें (एक *checkpoint*), उसके अंदर की हर चीज़ फेंक दें, और जब backward pass उस block तक पहुँचे, तो जो चाहिए उसे फिर से बनाने के लिए उसका forward pass दोबारा चलाएँ। Storage गहराई में लगभग रैखिक से घटकर लगभग उसके वर्गमूल पर आ जाती है, एक अतिरिक्त forward pass की क़ीमत पर, आम तौर पर प्रति step 20 से 40% धीमा।

![गहराई पर दो curves। Checkpointing के बिना, stored activations layers की गिनती के साथ सीधी रेखा में बढ़ते हैं। Checkpointing के साथ वे वर्गमूल का अनुसरण करते हैं और लगभग तुरंत सपाट हो जाते हैं। 24 layers पर दोनों के बीच लगभग पाँच गुने का फ़ासला है।](images/linear-against-square-root.svg)

इस सौदे का आकार ही वजह है कि यह लगभग default है। दो या तीन layers पर सीधी रेखा और वर्गमूल मुश्किल से अलग होते हैं, इसलिए खिलौना model पर यह तकनीक बेमानी लगती है; काम किए गए उदाहरण की 24 layers पर फ़ासला लगभग पाँच गुना है और बढ़ता जाता है, और model चाहे जितना गहरा हो, क़ीमत एक अतिरिक्त forward pass ही रहती है।

```python
model.gradient_checkpointing_enable()
model.config.use_cache = False  # incompatible with checkpointing during training
```

वह दूसरी पंक्ति मायने रखती है। KV cache autoregressive *generation* को तेज़ करने के लिए है और training में उसकी कोई भूमिका नहीं; उसे checkpointing के साथ चालू छोड़ने से, कम से कम, warnings आती हैं, और ज़्यादा से ज़्यादा memory बर्बाद होती है।

**Gradient checkpointing, adapter fine-tuning के लिए लगभग default है।** यह ऊपर के profile की सबसे बड़ी अकेली लागत वापस ख़रीद लेता है, और धीमापन लगभग हमेशा सहने लायक होता है।

### Padding और packing

Batch की हर sequence को batch के सबसे लंबे सदस्य तक padding दी जाती है, और padding बिना कुछ योगदान दिए activation memory खाती है। दो उपाय:

- **Length grouping।** लगभग बराबर आकार की sequences को साथ batch करें, ताकि कम padding लगे।
- **Packing।** छोटे examples को पूरी लंबाई की sequences में जोड़ दें, जिससे padding लगभग पूरी तरह ख़त्म हो जाती है।

छोटे examples वाले datasets पर packing असली कुशलता की जीत है, और उसकी सही होने की एक शर्त है: साथ packed examples को अपनी सीमाओं के आर-पार attend नहीं करना चाहिए। Implementations इसे position resets और सीमा-सचेत attention से सँभालती हैं। अगर आप packing चालू करते हैं, तो जाँचें कि आपकी loss masking उसमें बची रहती है: packed sequence को अपने `-100` labels अक्षत रखने होंगे, वरना completion-only loss चुपचाप full-sequence loss बन जाता है।

### चीज़ें आज़माने का क्रम

जब run memory में न समाए, इस क्रम में कि आप क्या छोड़ते हैं:

1. Gradient checkpointing चालू करें, जो सिर्फ़ समय की क़ीमत लेती है
2. प्रति-device batch size घटाएँ और gradient accumulation बढ़ाएँ, जो थोड़ा समय लेता है और सांख्यिकीय रूप से कुछ नहीं बदलता
3. Sequence length घटाएँ, जो task बदल देता है, इसलिए पहले अपना token-length वितरण जाँचें
4. Base model को quantise करें, जो चरण 4 है और कुछ गुणवत्ता की क़ीमत लेता है
5. Adapter rank घटाएँ, जो capacity की क़ीमत लेता है और यहाँ के सभी विकल्पों में सबसे कम बचाता है

आख़िरी बात पर रुकना ठीक है। Rank वह knob है जिस तक लोग सबसे पहले पहुँचते हैं और वह लगभग *सबसे कम* असरदार है, क्योंकि adapter के parameters कुल का बहुत छोटा अंश हैं। 4M-parameter adapter पर rank आधा करने से 32 MB बचता है।

## अभ्यास

1. ▢ इनमें से कौन trainable parameter की गिनती के साथ scale होते हैं, और कौन batch व sequence length के साथ: gradients, activations, optimizer moments, frozen weights?

<details markdown="1"><summary>जाँचें</summary>

Trainable parameter की गिनती: gradients, optimizer moments। सिर्फ़ model का आकार: frozen weights। Batch और sequence length: activations।

कि activations बिल्कुल अलग अक्ष के हैं, यही इस पाठ का मुद्दा है, और यही वजह है कि adapters उन्हें हल नहीं करते।

</details>

2. ▢ 32-layer model, hidden size 4096, batch 2, sequence length 4096, bf16 के लिए activation memory का अनुमान लगाएँ।

<details markdown="1"><summary>जाँचें</summary>

32 × 2 × 4096 × 4096 × 20 ≈ 21 GB।

14 GB के frozen 7B base के सामने विशाल। Gradient checkpointing के साथ यह लगभग एक परिमाण-क्रम घट जाता है, जो run को एक अकेले device पर संभव बनाता है।

</details>

3. ▢ आपका LoRA run memory से बाहर हो जाता है। एक सहकर्मी सुझाता है कि rank 64 से 8 कर दें। मूल्यांकन करें।

<details markdown="1"><summary>जाँचें</summary>

इससे मुश्किल से मदद मिलेगी। 7B model पर rank 64 से 8 करने पर adapter state और gradients के लगभग सौ megabytes बचते हैं, जबकि activations gigabytes में नापे जाते हैं।

पहले gradient checkpointing चालू करें और प्रति-device batch size घटाएँ। Rank capacity का फ़ैसला है, और उसे उस memory पर ख़र्च करना जिसकी आपके पास कमी नहीं थी, बुरा सौदा है।

</details>

4. ▢ Gradient checkpointing चालू होने पर `use_cache` बंद क्यों करना ज़रूरी है?

<details markdown="1"><summary>जाँचें</summary>

KV cache पिछले keys और values store करता है ताकि autoregressive generation में उन्हें दोबारा compute न करना पड़े। Training एक पूरी sequence पर एक अकेला forward pass करती है, इसलिए cache का कोई फ़ायदा नहीं, और वह checkpointing की दोबारा-compute वाली रणनीति से टकराता है और memory भी खाता है।

</details>

5. ▢ Gradient checkpointing दोनों दिशाओं में क्या सौदा करता है?

<details markdown="1"><summary>जाँचें</summary>

यह compute के बदले memory का सौदा करता है: activation storage गहराई में लगभग रैखिक से घटकर लगभग उसके वर्गमूल पर आ जाती है, बदले में प्रति step लगभग एक अतिरिक्त forward pass, आम तौर पर 20 से 40% धीमा।

</details>

6. ▢ आप packing चालू करते हैं और आपका model ऐसे सवालों के जवाब देने लगता है जो किसी ने पूछे नहीं। क्या ग़लत हुआ?

<details markdown="1"><summary>जाँचें</summary>

सबसे संभव है कि loss mask packing में बची नहीं, इसलिए अब prompt tokens पर training हो रही है, या examples अपनी सीमाओं के आर-पार attend कर रहे हैं और सीख रहे हैं कि उत्तर के बाद असंबंधित text आता है।

जाँचें कि `-100` labels packing चरण में सुरक्षित रहते हैं और implementation सीमा-सचेत है। Packing कुशलता का अनुकूलन है जिसकी सही होने की एक पूर्व-शर्त है।

</details>

## असली दुनिया का अभ्यास

- [ ] एक training step batch 1 पर चलाएँ, फिर batch 2, फिर batch 4, हर बार peak memory दर्ज करते हुए। पुष्टि करें कि संबंध रैखिक है।
- [ ] Gradient checkpointing चालू करके दोहराएँ। बची memory और खोए गए seconds-प्रति-step, दोनों दर्ज करें, और तय करें कि क्या आप यह सौदा लेंगे।
- [ ] कल: असली tokenizer से किसी असली dataset का token-length वितरण मापें। 95वाँ percentile ढूँढें। वही, अधिकतम नहीं, आपकी sequence length है।

## आगे बढ़ने के लिए

- [पेपर: "Training Deep Nets with Sublinear Memory Cost", Chen et al., arXiv:1604.06174](https://arxiv.org/abs/1604.06174)
- [पेपर: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness", Dao et al., arXiv:2205.14135](https://arxiv.org/abs/2205.14135)
- [दस्तावेज़: Methods and tools for efficient training on a single GPU, Hugging Face](https://huggingface.co/docs/transformers/main/en/perf_train_gpu_one)
- [memory budget शीट](../reference/memory-budget.md): अब इस्तेमाल करने लायक पूरी हो चुकी है

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
