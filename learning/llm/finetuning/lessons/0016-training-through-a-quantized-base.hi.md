---
title: "16. Quantized Base के आर-पार Training"
description: "Frozen 4-bit weights से gradients कैसे बहते हैं"
type: lesson
---

# पाठ 16. Quantized Base के आर-पार Training

**मिशन से संबंध:** व्यवहार में QLoRA। यह वह अकेला पाठ भी है जहाँ आपके पास जो hardware है वह सचमुच बदल देता है कि आपके लिए क्या उपलब्ध है।
**मुख्य स्रोत:** [दस्तावेज़: bitsandbytes quantization, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
**पूर्व-आवश्यकताएँ:** [पाठ 15](0015-nf4-and-double-quantisation.md), [पाठ 11](0011-your-first-adapter.md)

## वार्म-अप

1. ▢ NF4 किसे normal quantiles पर रखता है, और क्यों?

<details markdown="1"><summary>जाँचें</summary>

अपने 16 representable स्तरों को, ताकि हर एक सीमा की बराबर मात्रा के बजाय probability mass की बराबर मात्रा ढके, जो इससे मेल खाता है कि सामान्य रूप से बँटे weights असल में कहाँ जमा होते हैं।

</details>

2. ▢ Double quantisation क्या compress करता है?

<details markdown="1"><summary>जाँचें</summary>

पहले-स्तर के block scales, weights नहीं। लगभग 0.37 bits प्रति parameter।

</details>

3. ▢ Adapter वाले 4-bit base के लिए, कौन-सा memory पद हावी है?

<details markdown="1"><summary>जाँचें</summary>

Activations। Base कुछ gigabytes पर आ गया है और adapter state उसका एक अंश है, इसलिए batch size और sequence length अब तय करते हैं कि run समाता है या नहीं।

</details>

## यह जानें

### Frozen quantized base के आर-पार adapter तक gradient कैसे पहुँचता है

प्रत्यक्ष विरोधाभास: base weights 4-bit integers हैं, और आप 4-bit integer के सापेक्ष सार्थक ढंग से gradient नहीं ले सकते। तो training काम कैसे करती है?

यह इसलिए काम करती है कि **base weights train नहीं हो रहे।** एक adapt की गई layer का पीछा करें:

```text
forward:   h = W₀_dequant(x) + (α/r) · B A x
```

`W₀` को matmul के लिए bf16 में dequantise किया जाता है और dequantise की हुई copy फेंक दी जाती है। Backward pass को `A` और `B` के सापेक्ष loss का gradient चाहिए, और उसे compute करने के लिए उसे layer से गुज़रते *activations* चाहिए, जो bf16 हैं, और ऊपर से आता gradient, जो भी bf16 है।

Frozen weights backward pass में सिर्फ़ पहले की layers तक gradient **पहुँचाने** में भाग लेते हैं। इसके लिए `W₀` से गुणा करना पड़ता है, जिसके लिए उसे फिर से dequantise करना होता है, उसके सापेक्ष derivative लेना नहीं। किसी base weight के लिए कभी कोई gradient store नहीं होता, क्योंकि कोई माँगा ही नहीं जाता।

![एक adapt की गई layer एक ही चार डिब्बों के साथ दो बार बनी। Forward में, इनपुट 4-bit base और bf16 adapter दोनों तक पहुँचता है और वे output पर मिलते हैं; backward में, gradient उन्हीं किनारों पर उलटी दिशा में चलता है, पर सिर्फ़ adapter के लिए gradient store होता है।](images/a-constant-in-the-graph.svg)

दोनों पटल एक ही डिब्बे एक ही जगह रखते हैं, और backward के किनारे forward वालों के उलटे हैं। Base दोनों में दिखता है, दोनों में काम करता है, और किसी में से कुछ नहीं रखता।

तो यहाँ कुछ अनोखा नहीं है। Quantized base computation graph में एक constant है। उसे ऊँची precision पर पढ़ना पड़ता है, पर उसे कभी update नहीं करना पड़ता, और update करना ही महँगा हिस्सा है।

क़ीमत compute की है: dequantisation हर forward में और backward pass में फिर, हर step पर होता है। QLoRA गति के बदले memory का सौदा करता है, और यह bf16 base से प्रति step उल्लेखनीय रूप से धीमा है।

### Model तैयार करना

```text
quant_config := {
    load_in_4bit: true,
    quant_type: "nf4",
    use_double_quant: true,
    compute_dtype: "bfloat16",
}

model := load_model("<base model>", quantization: quant_config)
model := prepare_for_quantized_training(model, gradient_checkpointing: true)

adapter_config := {rank: 32, alpha: 64, target_modules: "all-linear"}
model := attach_adapter(model, adapter_config)
print(model.trainable_parameter_count())
```

`prepare_model_for_kbit_training` कई छोटी ज़रूरी चीज़ें करता है: layer norms और output head को स्थिर precision पर cast करता है, gradient checkpointing और input-gradient की ज़रूरतें चालू करता है, और सुनिश्चित करता है कि जिस चीज़ को ऊँची precision में रहना चाहिए वह quantize न हुई हो। इसे छोड़ने से ऐसे runs बनते हैं जो अस्थिर हैं या gradient errors के साथ विफल होते हैं, और कारण संदेश से स्पष्ट नहीं होता।

### बाक़ी सब कुछ वैसा ही

Rank, alpha, target modules, learning rate, schedule, held-out split, generation probes, पाठ 11 की चार जाँचें: सब एक जैसे। **QLoRA सस्ते base वाला LoRA है।** यह अपनी hyperparameter लोक-मान्यताओं वाला अलग तरीक़ा नहीं है, और इसे वैसा मानना भ्रम का आम स्रोत है।

एक समायोजन जिसका ज़िक्र करना ठीक है: क्योंकि base ज़्यादा शोर वाला है, कुछ practitioners bf16 base के मुक़ाबले थोड़ा ज़्यादा rank इस सोच से इस्तेमाल करते हैं कि adapter को task सीखने के साथ quantisation की त्रुटि की भरपाई भी करनी है। इसे अपने task पर परखने की परिकल्पना मानें, नियम नहीं।

### Backends: असल में क्या सच है

यह सावधानी माँगता है, क्योंकि इसका बार-बार दोहराया जाने वाला रूप पुराना पड़ चुका है।

`bitsandbytes` CUDA-only के रूप में शुरू हुआ, और कई सालों तक "QLoRA को NVIDIA GPU चाहिए" बस सही था। तब से library multi-backend architecture पर आ गई है, **CUDA (AMD ROCm को भी ढकते हुए), CPU, Intel XPU, Intel Gaudi, और Apple MPS** के लिए dispatch के साथ, शुद्ध-PyTorch fallbacks के साथ। 4-bit operations, यानी quantise, dequantise और 4-bit matrix-vector गुणनफल, के CUDA से आगे backend implementations हैं, जो तब dispatch होती हैं जब block size वह हो जिसे compiled kernel support करता है और वरना धीमे generic रास्तों पर लौट जाती हैं।

आपके लिए इसका नतीजा:

- **CUDA सबसे पूरा और सबसे अच्छी तरह optimised रास्ता बना हुआ है।** अगर आपके पास है तो उसे इस्तेमाल करें, और उम्मीद करें कि प्रकाशित संख्याएँ दोहराई जा सकेंगी।
- **अन्य backends चलने लायक और सुधरते हुए हैं, कुछ शर्तों के साथ।** Coverage operation, block size और library version के हिसाब से बदलती है। धीमे steps की उम्मीद रखें, और यह जाँचने की भी कि कोई ख़ास configuration optimised kernel पर पड़ती है या fallback पर।
- **Paged optimizers सचमुच CUDA-विशिष्ट हिस्सा हैं।** वे क्षणिक spikes के दौरान optimizer state को host memory में फैलाने के लिए NVIDIA unified memory पर निर्भर करते हैं, चरम पर out-of-memory crash से बचते हुए। यह hardware की सुविधा है, पोर्टेबल algorithm नहीं। Adapter training में यह सबसे कम मायने रखता है, जहाँ optimizer state नन्ही है; इसका मूल उद्देश्य full fine-tuning के पैमाने की state थी।
- **किसी भी दस्तावेज़ के बजाय अपने installed version से जाँचें।** यह क्षेत्र बार-बार बदला है और फिर बदलेगा। `bitsandbytes` 4-bit तक का अकेला रास्ता भी नहीं; दूसरे quantisation backends भी हैं जिनकी hardware coverage अलग है।

पाठ 14 और 15 की अवधारणाएँ, यानी blockwise scales, normal-quantile स्तर, constants को quantise करना और storage precision बनाम compute precision, अंकगणित हैं और हर backend पर एक जैसी हैं। सिर्फ़ kernel की उपलब्धता और गति अलग है।

### Run से क्या उम्मीद रखें

| bf16 base के मुक़ाबले | असर |
|---|---|
| Fixed memory | Base के लिए लगभग 4× कम |
| Step का समय | धीमा, हर forward और backward में dequantisation |
| Loss curve का आकार | बहुत मिलता-जुलता; थोड़ा ऊपर बैठ सकता है |
| अंतिम गुणवत्ता | थोड़ी कम, task पर निर्भर, इसलिए इसे मापें (पाठ 17) |

और पाठ 13 का merge नियम अब भी लागू है, पहले से भी ज़्यादा अहम: **full-precision base में merge करें, quantized में नहीं।** 4-bit के सामने train करें, फिर base को bf16 में load करें, adapter लगाएँ, वहीं merge करें। Quantized weights में merge करना requantisation की वह हानि जोड़ता है जिसे स्वीकार करने की आपके पास कोई वजह नहीं।

## अभ्यास

1. ▢ जब base weights 4-bit integers हैं तो gradients कैसे बह सकते हैं?

<details markdown="1"><summary>जाँचें</summary>

किसी base weight के सापेक्ष कभी gradient नहीं लिया जाता: वे frozen constants हैं। Gradients `A` और `B` के सापेक्ष लिए जाते हैं, जो ऊँची precision के हैं।

Frozen weights पहले की layers तक gradient *पहुँचाने* के लिए चाहिए, जिसके लिए गुणा के वास्ते उन्हें dequantise करना पड़ता है, उनका derivative लेना नहीं।

</details>

2. ▢ `prepare_model_for_kbit_training` क्या करता है, और इसे छोड़ने पर क्या होता है?

<details markdown="1"><summary>जाँचें</summary>

वह उन modules को, जिन्हें स्थिरता चाहिए, जैसे layer norms और output head, ऊँची precision पर cast करता है, gradient checkpointing और input gradients चालू करता है, और सुनिश्चित करता है कि जो ऊँची-precision में रहना चाहिए वह quantize न हुआ हो।

इसे छोड़ने पर आम तौर पर अस्थिर run या gradients की ज़रूरत न होने के बारे में error मिलता है, ऐसे संदेश के साथ जो कारण की ओर इशारा नहीं करता।

</details>

3. ▢ QLoRA का कौन-सा हिस्सा CUDA-विशिष्ट है, और adapter training के लिए वह कितना मायने रखता है?

<details markdown="1"><summary>जाँचें</summary>

Paged optimizers, जो spikes के दौरान optimizer state को host memory में फैलाने के लिए NVIDIA unified memory इस्तेमाल करते हैं।

Adapter training के लिए यह कम मायने रखता है, जहाँ optimizer state megabytes की है। इसे full fine-tuning के पैमाने की state के लिए बनाया गया था, जहाँ क्षणिक spike सचमुच run ख़त्म कर देता है।

</details>

4. ▢ 2023 का एक tutorial कहता है कि 4-bit NF4 के लिए NVIDIA GPU चाहिए। क्या यह अब भी सही है?

<details markdown="1"><summary>जाँचें</summary>

निरपेक्ष रूप में नहीं। `bitsandbytes` अब 4-bit operations को CUDA/ROCm, CPU, Intel XPU, Intel Gaudi और Apple MPS में dispatch करता है, जहाँ compiled kernel उपलब्ध न हो वहाँ PyTorch fallbacks के साथ।

CUDA अब भी सबसे पूरा और सबसे तेज़ रास्ता है, और अन्य backends पर coverage operation, block size और version के हिसाब से बदलती है। तो सही कथन है "CUDA सबसे अच्छी तरह supported रास्ता है", "CUDA अकेला रास्ता है" नहीं, और आप किसी tutorial के बजाय अपने installed version से जाँचते हैं।

</details>

5. ▢ LoRA से QLoRA पर जाते समय आपको कौन-सा hyperparameter दोबारा सोचना होगा?

    - a) Learning rate, जिसे काफ़ी घटाना होगा
    - b) Alpha value, जिसे भरपाई के लिए बढ़ाना होगा
    - c) कोई नहीं, base precision अलग मामला है
    - d) Batch size, जिसे स्थिर रहने के लिए बढ़ाना होगा

<details markdown="1"><summary>जाँचें</summary>

**c)** कोई नहीं। Base precision अलग मामला है।

QLoRA सस्ते base वाला LoRA है। कुछ practitioners quantisation के शोर को सोखने के लिए थोड़ा ज़्यादा rank आज़माते हैं, पर वह परखने की परिकल्पना है, ज़रूरी बदलाव नहीं।

</details>

6. ▢ आपने 4-bit base के सामने train किया और एक अकेला deploy करने लायक model चाहते हैं। क्रम से चरण बताएँ।

<details markdown="1"><summary>जाँचें</summary>

Base को bf16 में load करें (4-bit नहीं), trained adapter लगाएँ, merge करें, tokenizer के साथ सहेजें, और merge किए model को बाद में तभी quantise करें जब serving के लिए quantized artifact चाहिए।

4-bit base में merge करने के लिए dequantise-जोड़ो-requantise करना पड़ता है और बिना किसी बात के गुणवत्ता जाती है।

</details>

## असली दुनिया का अभ्यास

- [ ] एक base model को bf16 और NF4 में load करें। हर एक की memory दर्ज करें और अनुपात निकालें।
- [ ] दोनों bases के सामने वही छोटी training job चलाएँ। Seconds प्रति step और loss curve दर्ज करें, और नोट करें कि कौन-सा धीमा है और कितना।
- [ ] जाँचें कि आपका `bitsandbytes` install असल में कौन-सा backend इस्तेमाल कर रहा है, और आपका block size optimised kernel पर पड़ता है या fallback पर।
- [ ] कल: 4-bit में train हुए adapter को bf16 base में merge करें और अपने probes के सामने greedy तरीक़े से जाँचें।

## आगे बढ़ने के लिए

- [दस्तावेज़: bitsandbytes quantization, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
- [कोड: bitsandbytes, bitsandbytes-foundation](https://github.com/bitsandbytes-foundation/bitsandbytes): backend directory ही coverage का अधिकार है
- [पेपर: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
- [पाठ 17. QLoRA की असली क़ीमत](0017-what-qlora-costs.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
