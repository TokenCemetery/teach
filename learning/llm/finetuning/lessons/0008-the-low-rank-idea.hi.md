---
title: "8. Low-Rank का विचार"
description: "`ΔW = BA`, और adapter की गिनती"
type: lesson
---

# पाठ 8. Low-Rank का विचार

**मिशन से संबंध:** LoRA वह तरीक़ा है जिस पर मिशन का बाक़ी हिस्सा बना है। यह पाठ तंत्र है; अगले दो पाठ फ़ैसले हैं।
**मुख्य स्रोत:** [पेपर: "LoRA: Low-Rank Adaptation of Large Language Models", Hu et al., arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
**पूर्व-आवश्यकताएँ:** [पाठ 6](0006-gradients-and-optimizer-state.md), [पाठ 7](0007-activations-and-checkpointing.md), [adapter](../GLOSSARY.md)

## वार्म-अप

1. ▢ प्रति trainable parameter और प्रति frozen parameter bytes?

<details markdown="1"><summary>जाँचें</summary>

Trainable के सोलह, frozen के दो। आठ-और-एक का यह अनुपात ही adapters के होने की वजह है।

</details>

2. ▢ आपका adapter run memory से बाहर है। आप सबसे पहले क्या बदलते हैं, और क्या नहीं बदलते?

<details markdown="1"><summary>जाँचें</summary>

Gradient checkpointing चालू करें, फिर भरपाई के लिए accumulation के साथ प्रति-device batch size घटाएँ। Rank न घटाएँ: adapter state megabytes में है जबकि activations gigabytes में।

</details>

3. ▢ Base को freeze करने से कौन-सी memory श्रेणी अप्रभावित रहती है?

<details markdown="1"><summary>जाँचें</summary>

Activations। वे batch size और sequence length के साथ scale होते हैं, इस पर नहीं कि कितने parameters trainable हैं।

</details>

## यह जानें

Full fine-tuning हर weight matrix के लिए एक update `ΔW` सीखती है, `W` जितना ही आकार। LoRA का दावा है कि इस update को full-rank होने की ज़रूरत नहीं, क्योंकि किसी task के लिए ज़रूरी बदलाव एक कम-आयामी subspace में रहता है।

तो `ΔW` को सीधे store करने के बजाय, उसका गुणनखंड करें:

```text
ΔW = B A

A : r × d_in     (down-projection, r is small)
B : d_out × r    (up-projection)
```

और adapt की गई layer यह compute करती है:

```text
h = W₀ x + (α / r) · B A x
```

`W₀` frozen है। सिर्फ़ `A` और `B` को gradients मिलते हैं।

### इससे इतनी बचत क्यों होती है

`d_in × d_out` matrix में `d_in · d_out` parameters होते हैं। उसके rank-`r` गुणनखंड में `r · (d_in + d_out)` होते हैं। rank 8 पर 2048 × 2048 projection के लिए:

```text
full        = 2048 × 2048        = 4,194,304
rank 8      = 8 × (2048 + 2048)  =    32,768
```

उस एक matrix पर 128× की कमी। पूरे model में यह बचत जुड़ती जाती है, क्योंकि जिसे आपने trainable नहीं बनाया उस हर चीज़ का gradient और दोनों optimizer moments भी आप छोड़ देते हैं।

### Adapter की गिनती

Target modules के सेट के लिए सूत्र:

```text
adapter params = Σ over targeted layers of  r × (d_in + d_out)
```

पाठ 5 के 24-layer model के लिए, जिसमें `d = 2048` और `d_kv = 256` है, rank 8, चारों attention projections को target करते हुए काम करके:

```text
q_proj: 2048 → 2048   →  8 × (2048 + 2048) = 32,768
k_proj: 2048 →  256   →  8 × (2048 +  256) = 18,432
v_proj: 2048 →  256   →  8 × (2048 +  256) = 18,432
o_proj: 2048 → 2048   →  8 × (2048 + 2048) = 32,768
per layer                                  = 102,400
× 24 layers                                = 2,457,600
```

1.12B base के सामने लगभग 2.5M trainable parameters, यानी **0.22%**। उस adapter की optimizer state 2.5e6 × 16 ≈ 39 MB है।

ध्यान दें कि grouped-query attention का संकुचन यहाँ ऐसे मायने रखता है जैसे base model में नहीं रखता था: `k_proj` और `v_proj` के adapters अनुपात में छोटे *नहीं* होते, क्योंकि `r × (d_in + d_out)` दोनों आयामों में बड़े वाले पर हावी रहता है। `d_out` को 2048 से 256 करने ने base matrix को 8× घटाया पर adapter को सिर्फ़ 1.8×।

### Low rank काफ़ी क्यों है

यह अनुभवजन्य दावा **intrinsic dimensionality** पर टिका है: यह अवलोकन कि किसी बड़े pretrained model को नए task पर fine-tune करना उसके parameter space के हैरान करने वाले ढंग से कम-आयामी subspace के भीतर हो सकता है, और यह कि बड़े और बेहतर-pretrained models का intrinsic dimension *कम* होता है, ज़्यादा नहीं (Aghajanyan et al., [arXiv:2012.13255](https://arxiv.org/abs/2012.13255))। Pretraining पहले ही features बना चुकी है; adaptation ज़्यादातर उन्हें दोबारा तौलने और दोबारा मिलाने की बात है, और वह एक छोटा ऑपरेशन है।

दो ईमानदार चेतावनियाँ:

**यह अनुभवजन्य दावा है, प्रमेय नहीं।** यह व्यवहार, शैली, format और संकरी task-क्षमता को adapt करने के लिए अच्छी तरह लागू होता है। असल में नए ज्ञान की बड़ी मात्रा डालने के लिए कम लागू होता है, जो पाठ 27 की दलीलों में से एक है।

**"कम" सापेक्ष है और खिसका है।** शुरुआती practice 8 या 16 जैसे ranks पर टिकी, कुछ हद तक इसलिए कि memory कम थी। [पाठ 10](0010-choosing-target-modules.md) में हाल का काम पाता है कि कई supervised fine-tuning tasks पर सभी linear layers को ढकने वाले उदारता से rank दिए गए adapters full fine-tuning की बराबरी करते हैं, जबकि कंजूस वाले नहीं करते। Rank 8 शुरुआती बिंदु है, नियम नहीं।

### Inference का वह गुण जो LoRA को ख़ास बनाता है

क्योंकि update *जोड़ने वाला* और रैखिक है, उसे training के बाद वापस base weight में समेटा जा सकता है:

```text
W = W₀ + (α / r) · B A
```

नतीजा एक साधारण weight matrix है। **Merge किए गए LoRA का inference overhead ठीक शून्य है**: कोई अतिरिक्त matmuls नहीं, कोई बदला architecture नहीं, serving के समय install करने को कुछ नहीं। यही गुण LoRA को उन adapter-layer तरीक़ों से अलग करता है जो उससे पहले आए, जो forward रास्ते में नए modules डालते थे और latency हमेशा के लिए चुकाते थे। पाठ 13 व्यवहार में merging को कवर करता है, और पाठ 25 कवर करता है कि कब merge *नहीं* करना चाहिए।

## अभ्यास

1. ▢ 32-layer model में, जिसमें `d = 4096` और `d_kv = 1024` है, सिर्फ़ `q_proj` और `v_proj` पर rank-16 adapter के trainable parameters निकालें।

<details markdown="1"><summary>जाँचें</summary>

`q_proj`: 16 × (4096 + 4096) = 131,072।
`v_proj`: 16 × (4096 + 1024) = 81,920।
प्रति layer: 212,992। गुणा 32 layers ≈ 6.82M।

~7B base के सामने यह 0.10% है।

</details>

2. ▢ `d × d` matrix का rank-`r` गुणनखंड `d` बड़ा होने पर इतना ज़्यादा बचत क्यों करता है?

<details markdown="1"><summary>जाँचें</summary>

पूरी matrix `d²` की तरह बढ़ती है जबकि गुणनखंड `2rd` की तरह, जो रैखिक है। इसलिए अनुपात `d / 2r` model के चौड़ा होने पर सुधरता है।

इसीलिए LoRA बड़े models पर *अपेक्षाकृत* सस्ता होता जाता है, और इसीलिए models के बढ़ने के साथ यह तरीक़ा ज़्यादा मायने रखने लगा।

</details>

3. ▢ Intrinsic dimensionality का तर्क क्या है, और उसकी सीमा क्या है?

<details markdown="1"><summary>जाँचें</summary>

कि अच्छी तरह pretrained model को किसी task पर adapt करने के लिए parameter space के सिर्फ़ कम-आयामी subspace के भीतर हिलने की ज़रूरत होती है, क्योंकि pretraining ने ज़रूरी features पहले ही बना दिए हैं।

इसकी सीमा: यह *adaptation* के बारे में अनुभवजन्य खोज है, व्यवहार और format के लिए सबसे मज़बूत और काफ़ी नया तथ्यात्मक ज्ञान डालने के लिए सबसे कमज़ोर। यह भी नहीं बताती कि आपके ख़ास task के लिए कितना rank काफ़ी है।

</details>

4. ▢ Merge किए गए LoRA का inference overhead शून्य क्यों है, जबकि पहले के adapter-layer तरीक़ों का नहीं था?

<details markdown="1"><summary>जाँचें</summary>

LoRA का update weight के उसी space में जोड़ने वाला और रैखिक है, इसलिए `W₀ + (α/r)BA` एक अकेली साधारण matrix में सिमट जाता है। Adapter-layer तरीक़ों ने forward रास्ते में नए non-linear modules डाले, जिन्हें समेटा नहीं जा सकता और इसलिए हर layer पर हमेशा latency जुड़ती है।

</details>

5. ▢ सही या ग़लत: rank-8 adapter वह हर update दर्शा सकता है जो full fine-tune बना सकती है।

<details markdown="1"><summary>जाँचें</summary>

ग़लत। `ΔW = BA` में, जहाँ `B` के `r` columns हैं, rank अधिकतम `r` होता है, इसलिए वह सिर्फ़ rank-8 subspace के भीतर के updates तक पहुँच सकता है। Full fine-tune full-rank update बना सकती है।

दाँव यह है कि आपके task को जो update चाहिए वह ऐसे subspace के क़रीब है। जब नहीं है, तो आप उसे loss की ऐसी तली के रूप में देखते हैं जिसे और training नीचे नहीं करती, और इलाज ज़्यादा epochs नहीं बल्कि ज़्यादा rank या ज़्यादा target modules है।

</details>

6. ▢ Grouped-query attention में `v_proj` का output 4096 से 512 हो जाता है। Base matrix कितने गुना सिकुड़ती है, और उसका rank-16 adapter कितने गुना?

<details markdown="1"><summary>जाँचें</summary>

Base: 4096 × 4096 → 4096 × 512, 8× की कमी।
Adapter: 16 × (4096 + 4096) = 131,072 → 16 × (4096 + 512) = 73,728, 1.8× की कमी।

Adapter की लागत आयामों के योग से तय होती है, इसलिए बड़े वाले पर हावी रहती है। छोटे आयाम को संकरा करने से मुश्किल से मदद मिलती है।

</details>

## असली दुनिया का अभ्यास

- [ ] उस model और target सेट के लिए जिसे आप सचमुच इस्तेमाल करने का इरादा रखते हैं, adapter के parameters की गिनती हाथ से निकालें। संख्या रख लें।
- [ ] Code में adapter बनाएँ और trainable parameter की गिनती print करें। वह आपके हाथ के हिसाब से मेल खानी चाहिए। न खाए, तो ढूँढें कि आपने किस module का आकार ग़लत लिया।
- [ ] कल: उसी adapter को rank 8, 32 और 128 पर दोबारा निकालें, और ध्यान दें कि base model का प्रतिशत कैसे बदलता है।

## आगे बढ़ने के लिए

- [पेपर: "LoRA: Low-Rank Adaptation of Large Language Models", Hu et al., arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
- [पेपर: "Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning", Aghajanyan et al., arXiv:2012.13255](https://arxiv.org/abs/2012.13255)
- [LoRA hyperparameters शीट](../reference/lora-hyperparameters.md)
- [पाठ 9. Rank, Alpha और Initialisation](0009-rank-alpha-and-initialisation.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
