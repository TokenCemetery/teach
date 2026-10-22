---
title: "10. Target Modules चुनना"
description: "Attention-only 2021 का ablation है, default नहीं"
type: lesson
---

# पाठ 10. Target Modules चुनना

**मिशन से संबंध:** Target modules rank से ज़्यादा मायने रखते हैं, और उन पर चली आ रही समझ पुरानी पड़ चुकी है। यह वह जगह है जहाँ आप औसत practitioner से नापने लायक ढंग से बेहतर हो सकते हैं।
**मुख्य स्रोत:** [दस्तावेज़: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
**पूर्व-आवश्यकताएँ:** [पाठ 2](0002-where-the-weights-live.md), [पाठ 9](0009-rank-alpha-and-initialisation.md)

## वार्म-अप

1. ▢ `α/r` क्या नियंत्रित करता है, और अकेला `r` क्या नियंत्रित करता है?

<details markdown="1"><summary>जाँचें</summary>

`α/r` adapter के योगदान का scale तय करता है। अकेला `r` उसकी capacity तय करता है: वह कितना जटिल update व्यक्त कर सकता है।

</details>

2. ▢ Transformer block के ज़्यादातर parameters कौन-सी उप-परत में हैं?

<details markdown="1"><summary>जाँचें</summary>

MLP में, block का लगभग 75 से 80%, क्योंकि intermediate आयाम hidden size का कई गुना है और grouped-query attention चार में से दो attention projections को सिकोड़ देता है।

</details>

3. ▢ शून्य से initialise किया गया `B` क्या गारंटी देता है?

<details markdown="1"><summary>जाँचें</summary>

कि adapt किया गया model पहले optimizer step से पहले base model के बिल्कुल बराबर है।

</details>

## यह जानें

### मूल पेपर ने क्या किया, और वह सलाह क्यों नहीं है

LoRA के पेपर ने सिर्फ़ attention projections को adapt किया, अपने प्रयोगों में ज़्यादातर `W_q` और `W_v`, और MLP को अछूता छोड़ा। वही चुनाव सालों के tutorials में फैल गया, और `target_modules=["q_proj", "v_proj"]` वहीं से आता है।

इसके बारे में दो बातें समझनी हैं। यह memory budget के भीतर और मापे गए tasks पर एक वाजिब खोज थी। और यह इस बारे में सामान्य नतीजा **नहीं** है कि adaptation कहाँ होना चाहिए। 2021 के ablation को default मान लेना इस क्षेत्र में विरासत में मिली सबसे आम भूल है।

### MLP के पक्ष में दलील

पाठ 2 से: MLP में हर block के लगभग चार-पाँचवें parameters हैं। Interpretability के काम का एक ठोस हिस्सा MLP layers को वह जगह मानता है जहाँ model का बहुत-सा सीखा हुआ ज्ञान और feature पहचान रहती है, जबकि attention positions के बीच जानकारी पहुँचाता है। अगर आपके task को चाहिए कि model कुछ *जाने* या *वर्गीकृत करे* तो अलग ढंग से, तो उसे कूटबद्ध करने वाले parameters अनुपात से ज़्यादा MLP में हैं, और attention-only adapter उन तक पहुँच नहीं सकता।

### मौजूदा default

हाल का काम एक सीधी सिफ़ारिश पर आ मिलता है: **सभी linear layers को adapt करें**, और adapter को पर्याप्त rank दें। "LoRA without regret" नतीजे का TRL वाला लेख साफ़ है: MLP समेत हर linear layer पर LoRA लगाना, पर्याप्त rank के साथ, supervised fine-tuning कामों में full fine-tuning से फ़ासला पाट देता है, जबकि attention-only configurations नहीं पाटतीं।

```text
# The modern default: let the library find every linear layer.
config := {rank: 64, alpha: 128, target_modules: "all-linear"}

# The explicit equivalent, for a Llama-style architecture.
config := {
    rank: 64,
    alpha: 128,
    target_modules: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
}
```

`"all-linear"` दोनों में सुरक्षित है, क्योंकि वह ऐसे architecture के सामने पुराना नहीं पड़ सकता जिसके module नाम आपकी रटी हुई सूची से अलग हों। इसकी क़ीमत यह है कि आप सटीक नियंत्रण छोड़ देते हैं और आपको जाँचना चाहिए कि उसने असल में क्या मेल खाया।

यह अब किफ़ायती क्यों है: पाठ 7 से, adapter के parameters training memory का नगण्य हिस्सा हैं। Memory बचाने के लिए target modules सीमित करना 2021 में असली सौदा था और आज लगभग बेमानी है। आप असल में जिसका सौदा कर रहे हैं वह छोटे datasets पर overfitting का जोखिम है।

### फ़ैसला

| स्थिति | Targets | तर्क |
|---|---|---|
| असली task के लिए default | सभी linear layers | मेहनत के हिसाब से सबसे अच्छी गुणवत्ता; मौजूदा प्रमाण से मेल खाता है |
| छोटा dataset (< ~1k examples) | सिर्फ़ attention, कम rank | Memorisation सीमित करने के लिए जान-बूझकर capacity सीमित करें |
| सिर्फ़ style या tone | सिर्फ़ attention, कम rank | छोटे व्यवहार-बदलाव को छोटा update चाहिए |
| Task को नए भेद सीखने हैं | MLP शामिल होना ज़रूरी | Attention-only वहाँ नहीं पहुँच सकता जहाँ वे रहते हैं |
| किसी पेपर को दोहराना | ठीक वही जो पेपर ने इस्तेमाल किया | वरना आप उसे दोहरा नहीं रहे |

### दो modules जिनके बारे में लोग पूछते हैं

**Embeddings और output head।** आम तौर पर अछूते छोड़े जाते हैं। उन्हें adapt करना फ़ायदे के मुक़ाबले महँगा है, और यह वह एकमात्र जगह है जहाँ weights बदलने से हर token का अर्थ खिसक सकता है। असली अपवाद नए special tokens जोड़ना है, जिसके लिए embedding table को छूना पड़ता है और वह उसे adapt करने से अलग ऑपरेशन है।

**Bias terms।** `bias="none"` मानक setting है। Biases को भी train करना ( `"all"` या `"lora_only"`) सस्ता है पर शायद ही कभी काम करते और विफल होते run के बीच का फ़र्क़ होता है, और यह merging को जटिल बनाता है।

### वह जाँच जो असली भूल पकड़ती है

हर बार print करें कि क्या मेल खाया:

```text
model := attach_adapter(base_model, config)
print(model.trainable_parameter_count())
print(first 8 parameter names containing "lora")
```

जो target-module नाम किसी से मेल नहीं खाया, वह या तो error देता है या, version के हिसाब से, बिना किसी adapter वाला model, जो train होता है, loss log करता है, और कुछ नहीं सीखता। जो trainable-parameter गिनती आपके पाठ 8 के अंकगणित से असहमत हो, वह सबसे पहले मिल सकने वाली चेतावनी है।

## अभ्यास

1. ▢ मूल पेपर ने सिर्फ़ attention को target क्यों किया, और आज वह default क्यों नहीं है?

<details markdown="1"><summary>जाँचें</summary>

यह कसे हुए memory budget में उन tasks पर एक ablation था जिन्हें लेखकों ने मापा, ऐसे समय में जब trainable parameters सीमित रखना मायने रखता था। यह कभी इस बात का दावा नहीं था कि adaptation attention का काम है।

आज adapter की memory नगण्य है, और प्रमाण पर्याप्त rank के साथ सभी linear layers को ढकने के पक्ष में है।

</details>

2. ▢ आपके task में model को उन domain अवधारणाओं के बीच भेद करना है जिन्हें वह अभी गड्डमड्ड करता है। Attention-only या all-linear?

<details markdown="1"><summary>जाँचें</summary>

All-linear। नए भेद बनाने का मतलब है feature पहचान और store किए गए संबंधों को बदलना, जो अनुपात से ज़्यादा MLP में रहते हैं। Attention जानकारी पहुँचाता है; वह भेद वहाँ कूटबद्ध नहीं है।

</details>

3. ▢ आपके पास 400 training examples हैं। Target modules को सीमित करने के पक्ष में तर्क दें।

<details markdown="1"><summary>जाँचें</summary>

400 examples के साथ, capacity बाधा नहीं बल्कि जोखिम है। उदार rank पर पूरा all-linear adapter सेट को पूरी तरह रट सकता है: training loss शून्य के पास, held-out loss चढ़ता हुआ, और कोई generalisation नहीं।

कम rank पर attention तक सीमित करना जान-बूझकर की गई capacity की सीमा है, जो regularisation का काम करती है। बेहतर जवाब, अगर उपलब्ध हो, ज़्यादा data है।

</details>

4. ▢ वाजिब dataset वाले असली task पर गुणवत्ता बढ़ाने की सबसे ज़्यादा संभावना कौन-सा बदलाव रखता है?

    - a) Adapter rank को 16 से 64 करना
    - b) Targets को सभी linear layers तक बढ़ाना
    - c) Run में 0.05 पर LoRA dropout जोड़ना
    - d) एक और पूरा epoch train करना

<details markdown="1"><summary>जाँचें</summary>

**b)** Targets को सभी linear layers तक बढ़ाना।

यह MLP समेत लगभग चार गुना parameters को adaptation की पहुँच में ले आता है। Rank बढ़ाना उन layers के भीतर capacity जोड़ता है जिन तक आप पहले से पहुँचते हैं। Dropout फ़िट सुधारने के बजाय regularise करता है। एक अतिरिक्त epoch capacity जोड़े बिना overfitting का जोखिम लेता है।

</details>

5. ▢ आप `target_modules=["c_attn"]` रखते हैं और run train होता है पर loss मुश्किल से हिलता है। आप सबसे पहले क्या जाँचते हैं?

<details markdown="1"><summary>जाँचें</summary>

कि इस model में `c_attn` है भी या नहीं। यह GPT-2-शैली के architectures में fused attention projection है और Llama-शैली वालों में नहीं है, जो अलग `q_proj`, `k_proj`, `v_proj` इस्तेमाल करते हैं।

Module नाम print करें, फिर `print_trainable_parameters()`। शून्य के पास trainable गिनती ही जवाब है।

</details>

6. ▢ `"all-linear"` साफ़ module सूची से सुरक्षित क्यों है?

<details markdown="1"><summary>जाँचें</summary>

वह आपकी याद के बजाय लोड हुए model के सामने हल होता है, इसलिए ऐसे architecture पर चुपचाप layers छोड़ नहीं सकता जिसका नामकरण अलग हो।

इसकी क़ीमत सटीकता का नुक़सान है, इसलिए जाँचें कि उसने क्या मेल खाया और ध्यान रखें कि उसमें वे layers भी हो सकती हैं जिन्हें आप अछूता छोड़ना पसंद करते।

</details>

## असली दुनिया का अभ्यास

- [ ] एक ही model पर एक ही rank पर एक attention-only और एक all-linear adapter बनाएँ। दोनों trainable-parameter गिनतियाँ और उनका अनुपात दर्ज करें।
- [ ] Adapter के parameter नाम print करके जाँचें कि `"all-linear"` ने कौन-से modules मेल खाए। जो भी अप्रत्याशित हो, नोट करें।
- [ ] कल: ऑनलाइन प्रकाशित तीन fine-tuning configs ढूँढें और नोट करें कि कौन-से सिर्फ़ attention को target करते हैं। आँकें कि लेखक ने वह चुना था या विरासत में पाया।

## आगे बढ़ने के लिए

- [दस्तावेज़: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
- [लेख: "Practical Tips for Finetuning LLMs Using LoRA", Sebastian Raschka](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms): target-module ablations
- [LoRA hyperparameters शीट](../reference/lora-hyperparameters.md)
- [पाठ 11. आपका पहला Adapter](0011-your-first-adapter.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
