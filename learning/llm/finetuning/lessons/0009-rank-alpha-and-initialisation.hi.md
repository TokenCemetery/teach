---
title: "9. Rank, Alpha और Initialisation"
description: "सिर्फ़ `α/r` मायने रखता है, और `B` शून्य से क्यों शुरू होता है"
type: lesson
---

# पाठ 9. Rank, Alpha और Initialisation

**मिशन से संबंध:** मिशन आपसे हर hyperparameter को task के आधार पर सही ठहराने को कहता है। यही तीन वे जगहें हैं जहाँ ज़्यादातर लोग समझ के बजाय लोक-मान्यता दोहराते हैं।
**मुख्य स्रोत:** [दस्तावेज़: LoRA, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
**पूर्व-आवश्यकताएँ:** [पाठ 8](0008-the-low-rank-idea.md)

## वार्म-अप

1. ▢ LoRA का forward समीकरण लिखें।

<details markdown="1"><summary>जाँचें</summary>

`h = W₀x + (α/r) · BAx`, जिसमें `W₀` frozen है और सिर्फ़ `A` और `B` trainable हैं।

</details>

2. ▢ एक target की गई layer के लिए adapter के parameters की गिनती?

<details markdown="1"><summary>जाँचें</summary>

`r × (d_in + d_out)`। बड़े आयाम पर हावी।

</details>

3. ▢ Merge किया गया adapter inference पर कुछ क्यों नहीं लेता?

<details markdown="1"><summary>जाँचें</summary>

Update जोड़ने वाला और रैखिक है, इसलिए वह base weight में समा जाता है और पीछे साधारण matrix छोड़ता है।

</details>

## यह जानें

### Initialisation, और यह मनमानी क्यों नहीं है

`A` को random रूप से initialise किया जाता है, Gaussian या Kaiming-uniform। `B` को **ठीक शून्य** से initialise किया जाता है।

इसलिए step शून्य पर `BA = 0`, यानी `ΔW = 0`, यानी **adapt किया गया model पहले update से पहले bit-for-bit base model ही है।** यह जान-बूझकर रखा गया और ज़रूरी गुण है:

- Training किसी परेशान किए हुए model के बजाय एक ज्ञात-अच्छे model से शुरू होती है।
- Pretrained व्यवहार को कोई शुरुआती झटका नहीं लगता, इसलिए पलटने लायक कोई शुरुआती नुक़सान नहीं।
- आप जो भी बिगाड़ देखते हैं वह training ने किया है, initialisation ने नहीं।

![B शून्यों की grid के रूप में, A अलग-अलग values की grid के रूप में, और उनका गुणनफल शून्यों की grid के रूप में, नीचे नामित दो अस्वीकृत initialisations के साथ।](images/zero-whatever-a-holds.svg)

`A` की entries दिखती हैं और उनमें से कोई मायने नहीं रखती: हर एक गुणनफल में जाते समय एक शून्य से गुणा हो जाती है।

यह असमरूपता ज़रूरी है। अगर दोनों शून्य होते, तो दोनों का gradient शून्य होता और कभी कुछ नहीं सीखा जाता: गुणनफल को संकेत ढोने के लिए एक गुणक का शून्येतर होना चाहिए। अगर दोनों random होते, तो `ΔW` हर target की गई layer में डाले गए संरचित शोर के रूप में शुरू होता।

यही वजह है कि LoRA full fine-tuning से कहीं ज़्यादा learning rates सह लेता है। आप उन weights को नहीं हिला रहे जो पहले से वह सब कुछ कूटबद्ध करते हैं जो model जानता है; आप शून्य से एक पद उगा रहे हैं।

### Alpha और scaling factor

`α` (`lora_alpha`) एक स्थिर scalar है। Update को `α/r` से scale किया जाता है।

`r` से भाग देने का मक़सद था कि effective update का परिमाण rank से लगभग स्वतंत्र हो जाए, ताकि rank बदलने पर learning rate दोबारा tune न करना पड़े। **मायने `α/r` का अनुपात रखता है, कोई एक संख्या अकेले नहीं।**

| `r` | `α` | `α/r` | असर |
|---|---|---|---|
| 8 | 16 | 2.0 | आम baseline |
| 16 | 32 | 2.0 | ज़्यादा capacity, वही update scale |
| 16 | 16 | 1.0 | ज़्यादा capacity, कमज़ोर update |
| 64 | 16 | 0.25 | बहुत ज़्यादा capacity, भारी दबा हुआ |

वह आख़िरी पंक्ति ऐसा जाल है जिसका नाम लेना ज़रूरी है: `α` को स्थिर छोड़कर rank बढ़ाने से update का scale *घटता* है। लोग ज़्यादा अभिव्यक्ति-क्षमता की आशा में rank बढ़ाते हैं, `α` भूल जाते हैं, और नतीजा निकालते हैं कि ज़्यादा rank नुक़सान करता है। उसने नहीं किया; उन्होंने चुपचाप adapter को 8× धीमा कर दिया।

रिवाज़ी शुरुआती बिंदु `α = 2r` है। इसे ऐसी परिपाटी मानें जिसका तर्क है, कोई खोज नहीं।

**rsLoRA** ([arXiv:2312.03732](https://arxiv.org/abs/2312.03732)) तर्क देता है कि `α/r` का भाजक ऊँचे rank पर ज़्यादा दबाता है और इसकी जगह `α/√r` प्रस्तावित करता है, जो rank बढ़ने पर learning को स्थिर रखता है। अगर आप rank 64 या उससे ऊपर काम करने की योजना बना रहे हैं, तो यह वह setting है जिसे जानना चाहिए:

```python
LoraConfig(r=64, lora_alpha=16, use_rslora=True, ...)
```

### Rank चुनना

Rank **capacity** है। यह तय करता है कि adapter कितना जटिल update व्यक्त कर सकता है।

| Rank | किसके लिए वाजिब |
|---|---|
| 4 से 8 | Style, tone, output format; छोटे datasets |
| 16 से 32 | कुछ हज़ार examples वाला असली task |
| 64 से 128 | कठिन tasks, बड़े datasets, reasoning-भारी व्यवहार |
| 256+ | बड़े SFT datasets पर full fine-tuning की capacity के क़रीब |

अंदाज़े से बेहतर दो diagnostics:

**Underfitting।** Training loss वहाँ से ऊपर थम जाता है जहाँ आपको चाहिए और ज़्यादा epochs मदद नहीं करते। Capacity काफ़ी नहीं: rank बढ़ाएँ, या target modules जोड़ें (आम तौर पर यही बेहतर क़दम है, पाठ 10 के अनुसार)।

**Overfitting।** Training loss गिरता रहता है जबकि held-out loss बढ़ता है। Data के लिए बहुत ज़्यादा capacity, या बहुत ज़्यादा epochs। Rank घटाएँ, dropout जोड़ें, ज़्यादा data लाएँ, या जल्दी रुकें।

Memory वाले पाठ से इस असमरूपता पर ध्यान दें: rank की memory लागत बहुत कम है (पाठ 7), इसलिए अतिरिक्त rank की क़ीमत overfitting का जोखिम और थोड़ा compute है, memory में समाने की समस्या नहीं। यह उस सहज बुद्धि को उलट देता है जो बहुत-से लोग उस दौर से लाते हैं जब memory ही बाध्यकारी बाधा थी।

### Dropout

`lora_dropout` adapter के input पर dropout लगाता है। आम values 0.0 से 0.1 हैं। इसका सहारा तब लें जब held-out loss बढ़ रहा हो और आप ज़्यादा data न पा सकें। बड़े datasets पर यह अक्सर अनावश्यक होता है और सिर्फ़ convergence धीमा करता है।

### Config

```text
config := {
    rank: 16,
    alpha: 32,               # α/r = 2
    dropout: 0.05,
    adapt_bias: false,
    target_modules: [...],   # Lesson 10
}

model := attach_adapter(model, config)
print(model.trainable_parameter_count())
```

वह आख़िरी पंक्ति वैकल्पिक नहीं है। वह इस बात की जाँच है कि आपके target modules किसी से मेल खाए भी, और उसे उस अंकगणित से सहमत होना चाहिए जो आपने पाठ 8 में किया था। Parameter नाम याद से नहीं, installed version के दस्तावेज़ से पढ़ें, क्योंकि यह सतह releases के बीच बदलती है।

## अभ्यास

1. ▢ `B` को शून्य से और `A` को random रूप से initialise क्यों किया जाता है, दोनों शून्य या दोनों random क्यों नहीं?

<details markdown="1"><summary>जाँचें</summary>

शून्य `B` शुरू में `ΔW = 0` बना देता है, इसलिए training ठीक base model से शुरू होती है और उबरने के लिए कोई गड़बड़ी नहीं होती। Random `A` गुणनफल का gradient शून्येतर रखता है, इसलिए learning शुरू हो सकती है।

दोनों शून्य: gradients ग़ायब हो जाते हैं, कुछ नहीं सीखा जाता। दोनों random: model हर target की गई layer में base-जमा-शोर के रूप में शुरू होता है।

</details>

2. ▢ आप rank 8 से 64 करते हैं और `α` को 16 पर छोड़ देते हैं। Loss मुश्किल से हिलता है। Diagnosis करें।

<details markdown="1"><summary>जाँचें</summary>

Scale `α/r` 2.0 से गिरकर 0.25 हो गया। Adapter की capacity आठ गुना और प्रभाव आठवाँ हिस्सा है, इसलिए कुल असर मज़बूत नहीं, दबा हुआ update है।

अनुपात बनाए रखने के लिए `α` को 128 करें, या `use_rslora=True` रखें ताकि भाजक `√r` हो जाए।

</details>

3. ▢ Training loss इतने ऊँचे स्तर पर सपाट हो जाता है कि काम का नहीं, और चौथा epoch मदद नहीं करता। यह क्या है, और आपके दो विकल्प क्या हैं?

<details markdown="1"><summary>जाँचें</summary>

Underfitting: adapter में ज़रूरी update को व्यक्त करने की capacity नहीं है।

Rank बढ़ाएँ, या target modules को model के और हिस्से ढकने तक बढ़ाएँ। Target modules जोड़ना आम तौर पर बेहतर पहला क़दम है, क्योंकि MLP में ज़्यादातर parameters हैं और अक्सर कमी वाली capacity वहीं होती है। ज़्यादा epochs capacity की छत को ठीक नहीं कर सकते।

</details>

4. ▢ कौन-सी जोड़ी सबसे मज़बूत update scale देती है?

    - a) `r = 8` के साथ `alpha = 8`
    - b) `r = 8` के साथ `alpha = 32`
    - c) `r = 32` के साथ `alpha = 32`
    - d) `r = 64` के साथ `alpha = 64`

<details markdown="1"><summary>जाँचें</summary>

**b)** `r = 8` के साथ `alpha = 32`, जो `α/r = 4` देता है।

बाक़ी सब `α/r = 1` हैं। उनके बीच capacity अलग है, पर update scale नहीं, और यही वह भेद है जो `α/r` वाली डिज़ाइन करना चाहती थी।

</details>

5. ▢ LoRA full fine-tuning से दस से सौ गुना ऊँचा learning rate क्यों इस्तेमाल कर सकता है?

<details markdown="1"><summary>जाँचें</summary>

Trainable parameters शून्य योगदान से शुरू होते हैं और वे ख़ुद pretrained ज्ञान का भंडार नहीं हैं। नुक़सान पहुँचाने लायक कोई जमा हुई संरचना नहीं है, और पद को शून्य से उगना है, इसलिए उचित संख्या के steps में सार्थक रूप से हिलने के लिए उसे कहीं बड़ा step चाहिए।

</details>

6. ▢ आप rank कब *नहीं* बढ़ाएँगे, भले adapter underfit कर रहा हो?

<details markdown="1"><summary>जाँचें</summary>

जब dataset छोटा हो। थोड़े examples पर अतिरिक्त capacity रटना ख़रीदती है, generalisation नहीं: training loss गिरता है, held-out loss बढ़ता है।

वहाँ सही जवाब ज़्यादा या बेहतर data, या संकरा task है, बड़ा adapter नहीं।

</details>

## असली दुनिया का अभ्यास

- [ ] तीन configs बनाएँ, `(8, 16)`, `(16, 32)` और `(64, 16)`, और हर एक का `α/r` तथा आपकी भविष्यवाणी लिखें कि क्या होगा। भविष्यवाणियाँ रख लें।
- [ ] हर एक के लिए `print_trainable_parameters()` print करें और अपने पाठ 8 के अंकगणित से मिलाएँ।
- [ ] कल: बाहर चलन में कोई प्रकाशित fine-tuning config ढूँढें, उसका `α/r` निकालें, और तय करें कि लेखक ने उसे चुना था या विरासत में पाया।

## आगे बढ़ने के लिए

- [दस्तावेज़: LoRA, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [पेपर: "A Rank Stabilization Scaling Factor for Fine-Tuning with LoRA", Kalajdzievski, arXiv:2312.03732](https://arxiv.org/abs/2312.03732)
- [लेख: "Practical Tips for Finetuning LLMs Using LoRA", Sebastian Raschka](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms)
- [LoRA hyperparameters शीट](../reference/lora-hyperparameters.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
