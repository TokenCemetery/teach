---
title: "18. LLMs के लिए QAT"
description: "LLM पर quantization-aware training की क्या लागत आती है, वह क्या वापस लाती है, और PTQ कब काफ़ी है"
type: lesson
---

# पाठ 18. LLMs के लिए QAT

**मिशन से संबंध:** मिशन आपसे माँगता है कि आप बता सकें कि post-training quantization के मुक़ाबले quantization-aware training अपनी लागत कब वसूल करती है, जिसके लिए क़ीमत का पर्चा, मापा गया फ़ायदा, और वे मामले चाहिए जहाँ फ़ायदा zero है।
**मुख्य स्रोत:** [पेपर: "LLM-QAT: Data-Free Quantization Aware Training for Large Language Models", Liu et al., 2023](https://arxiv.org/abs/2305.17888)
**पूर्व-आवश्यकताएँ:** [पाठ 17](0017-fake-quantization-and-the-ste.md), [Quantization-aware training](../GLOSSARY.md), [Post-training quantization](../GLOSSARY.md), [Weight-only quantization](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 9 ने round-to-nearest की तुलना 8 bits और 4 या उससे कम पर की थी। दोनों में से वह किस पर टिकता है, और दूसरे पर क्यों फिसलता है?

<details markdown="1"><summary>जाँचें</summary>

वह 8 bits पर टिकता है, जहाँ grid में 256 levels हैं और प्रति weight [rounding error](../GLOSSARY.md) छोटी है। 4 bits पर 16 levels हैं, हर weight कहीं बड़े step के आधे तक चूक सकता है, और सादी rounding के पास errors की भरपाई करने को कुछ नहीं। यही फ़ासला वह जगह है जिसमें GPTQ, AWQ और QAT होड़ करते हैं।

</details>

2. ▢ Training loop सीधे `round` के आर-पार differentiate क्यों नहीं कर सकता, और fake quantization इसके बारे में क्या करती है?

<details markdown="1"><summary>जाँचें</summary>

Round का derivative लगभग हर जगह zero है, इसलिए weights तक कोई gradient नहीं पहुँचता। Fake quantization float master copy रखती है, forward pass में quantize और dequantize लगाती है, और backward pass में gradient को rounding step के पार भेजने के लिए [straight-through estimator](../GLOSSARY.md) इस्तेमाल करती है, उन values के लिए zero gradient के साथ जिन्हें clamp ने काट दिया।

</details>

## यह जानें

### LLM पर QAT की क्या लागत है

QAT fake quantization डालकर की गई सामान्य training है, इसलिए वह training की लागतें विरासत में पाती है। Nagel et al. उन्हें गिनाते हैं: लंबी training, data की ज़रूरत, और hyper-parameter search ([व्हाइट पेपर](https://arxiv.org/abs/2106.08295), section 4)। दो LLM-विशिष्ट मापें इसे ठोस बनाती हैं।

PyTorch team ने इसे अपने torchao QAT flow से Llama3-8B पर मापा, int8 per-token dynamic activations और int4 grouped weights के साथ। 225 linear layers में से हर एक को कम से कम एक fake quantize operation मिलता है। उनके microbenchmarks में QAT fine-tuning सामान्य full fine-tuning से लगभग 34% धीमी थी, और activation checkpointing के साथ memory का इस्तेमाल प्रति GPU लगभग 2.35 GB बढ़ा ([PyTorch ब्लॉग](https://pytorch.org/blog/quantization-aware-training/))। 20 घंटे का fine-tune लगभग 27 घंटे का हो जाता है। ये उनकी setup पर उनकी संख्याएँ हैं, इसलिए इन्हें परिमाण के क्रम की तरह लें।

दूसरी लागत data है। Liu et al. ध्यान दिलाते हैं कि LLM का मूल training data अक्सर उपलब्ध नहीं होता, और models अक्सर कई चरणों में train होते हैं (instruction tuning, reinforcement learning) जिन्हें QAT के दौरान दोहराना कठिन होगा। उनका उत्तर **data-free** training है: full-precision model ख़ुद text generate करता है, पहले कुछ tokens लालची ढंग से चुनकर और बाक़ी sample करके, और quantized model को इसके लिए train किया जाता है कि वह full-precision model से, उसे teacher मानकर, मेल खाए। वे बताते हैं कि quantized models को सिर्फ़ 100,000 sampled sequences के छोटे set से distil किया गया, एक अकेले 8-GPU node पर। Sequences 1,024 tokens पर सीमित थीं, इसलिए पूरा set ज़्यादा से ज़्यादा लगभग 10 करोड़ tokens का है, एक संख्या जो उनकी दो संख्याओं से निकलती है, उनकी बताई हुई नहीं।

### यह क्या वापस लाती है

LLM-QAT weights, activations और KV cache को quantize करता है, जिसे bits में W-A-KV लिखा जाता है। उनकी Table 1 सात common-sense tasks पर औसत zero-shot accuracy बताती है। LLaMA-7B के लिए full-precision औसत 66.2 है।

| Setting (W-A-KV) | RTN | SmoothQuant | LLM-QAT |
|---|---|---|---|
| 8-8-8 | 65.6 | 66.3 | 66.0 |
| 4-16-16 (सिर्फ़ 4-bit weights) | 63.0 | रिपोर्ट नहीं किया गया | 64.4 |
| 4-8-4 | 41.2 | 43.2 | 60.7 |

8 bits पर हर method full precision के एक अंक के भीतर है। सिर्फ़-weights 4-bit RTN के नीचे पहले से टिकता है, और QAT 1.4 अंक जोड़ती है। 4-bit activations और KV-cache वाली setting वह जगह है जहाँ PTQ methods ढह जाते हैं और QAT 5.5 अंक के भीतर बनी रहती है। LLaMA-30B पर full-precision औसत 71.4 है: 4-8-4 RTN के साथ 42.5 और SmoothQuant के साथ 40.7 देता है जबकि LLM-QAT के लिए 69.9, पर सिर्फ़ 4-bit weights RTN के साथ 70.1, GPTQ के साथ 70.3 और LLM-QAT के साथ 70.1 देते हैं। पेपर का अपना सार भी सहमत है: सभी methods 8 bits पर अच्छे हैं, और जब weights, activations या KV cache 8 bits से नीचे जाते हैं तो PTQ methods accuracy खोते हैं जबकि LLM-QAT कहीं बेहतर टिकता है। यहाँ PTQ baselines RTN, GPTQ और SmoothQuant हैं। पाठ 15 के rotation methods बाद में आए और इस तुलना में नहीं हैं।

torchao ब्लॉग training की ओर से वही pattern बताता है। 8da4w scheme के साथ Llama3-8B पर, QAT ने PTQ की तुलना में hellaswag पर normalized-accuracy गिरावट का 96% और wikitext पर word-perplexity गिरावट का 68% वापस पाया। 2-bit weights पर PTQ model की wikitext word perplexity 603,336 थी। पहली 3 और आख़िरी 2 layers को छोड़ने से वह 6,766 हो गई, और उसमें QAT जोड़ने से 30। उन layers को छोड़े बिना QAT कहीं कम असरदार रही, इसलिए QAT ने अकेले 2 bits को नहीं बचाया।

### QLoRA पड़ोसी है, QAT नहीं

[QLoRA](https://arxiv.org/abs/2305.14314) भी quantized model को train करता है, पर वह frozen 4-bit base के आर-पार low-rank adapters तक backpropagate करता है। Base weights कभी नहीं बदलते, इसलिए model अपनी ही rounding से बचना नहीं सीख रहा: quantization इसलिए है कि fine-tune memory में समा जाए। यह track इसे नहीं सिखाता। finetuning track सिखाता है, और उसकी [memory budget](../../finetuning/reference/memory-budget.md) शीट bytes गिनती है।

### PTQ कब काफ़ी है, और QAT कब फ़ायदेमंद है

| स्थिति | सबूत | Default |
|---|---|---|
| 8-bit weights और activations | ऊपर की Table 1; [Kurtic et al.](https://arxiv.org/abs/2411.02355) बताते हैं कि Llama 3.1 के सभी आकारों पर FP8 प्रभावी रूप से lossless है और ठीक से tune किया INT8 1 से 3% गिरावट पर | PTQ |
| सिर्फ़ 4-bit weights, बड़ा model | ऊपर की LLaMA-30B पंक्ति; Kurtic et al. पाते हैं कि INT4 weight-only 8-bit को टक्कर देता है | PTQ, फिर मापें |
| सिर्फ़ 4-bit weights, छोटा model | LLaMA-7B: RTN 3.2 अंक खोता है, QAT 1.8 | PTQ आज़माएँ, फ़ासला मायने रखे तो QAT |
| 4-bit activations या KV cache | LLaMA-30B 4-8-4: RTN 42.5, LLM-QAT 69.9 | QAT, या पाठ 15 के rotations, परखकर |
| 3 bits या उससे कम | torchao के 2-bit और 3-bit experiments | QAT और संवेदनशील layers को रखना |
| बहुत ज़्यादा data पर train हुआ model | [Kumar et al.](https://arxiv.org/abs/2411.04330) पाते हैं कि जैसे-जैसे model ज़्यादा data देखता है, PTQ गिरावट बढ़ती है | PTQ को जल्दी परखें, बड़े फ़ासले की उम्मीद रखें |

Kumar का नतीजा 26B tokens तक पर train हुए 1.7B parameters तक के models से आता है, इसलिए वह बताता है कि कहाँ देखना है, यह नहीं कि बड़े model के लिए फ़ासला कितना है। हर पंक्ति आपकी अपनी baseline के मुक़ाबले परखने का default है, नियम नहीं।

## अभ्यास

1. ▢ LLaMA-30B (full precision 71.4) के ऊपर के LLM-QAT आँकड़ों से, सिर्फ़ 4-bit weights के साथ RTN कितने अंक खोता है, और 4-8-4 के साथ कितने? क्या हर मामले में QAT अपनी लागत के लायक़ है?

<details markdown="1"><summary>जाँचें</summary>

RTN सिर्फ़ 4-bit weights के साथ 1.3 अंक खोता है (70.1) और 4-8-4 पर 28.9 अंक (42.5)। सिर्फ़ weights के साथ, LLM-QAT भी 70.1 score करता है, इसलिए यहाँ वह कुछ नहीं ख़रीदता और PTQ काफ़ी है। 4-8-4 पर, LLM-QAT 69.9 score करता है, full precision से 1.5 अंक नीचे, इसलिए training की लागत खोई हुई accuracy का लगभग सारा हिस्सा ख़रीद लेती है। QAT तब फ़ायदेमंद है जब activations या KV cache 4 bits पर जाएँ, तब नहीं जब सिर्फ़ weights जाएँ।

</details>

2. ▢ आपके model का full fine-tune 20 घंटे लेता है। torchao microbenchmark का इस्तेमाल करके, QAT के साथ वही run लगभग कितना समय लेगा, और और क्या बढ़ता है?

<details markdown="1"><summary>जाँचें</summary>

लगभग 27 घंटे (20 गुना 1.34 यानी 26.8)। Activation checkpointing चालू होने पर memory भी प्रति GPU लगभग 2.35 GB बढ़ती है, क्योंकि fake quantization लगने से पहले weights को clone करना पड़ता है। यह Llama3-8B पर एक मापी हुई setup है, इसलिए आपका run अलग हो सकता है।

</details>

3. ▢ इनमें से कौन QLoRA का वर्णन करता है?

    - a) Frozen 4-bit base model के आर-पार adapters को train करना
    - b) Straight-through rounding step के पीछे सारे weights को update करना
    - c) Model को उसी के generate किए text पर distil करना
    - d) Model को fine-tune करते समय KV cache को quantize करना

<details markdown="1"><summary>जाँचें</summary>

**a)** QLoRA quantized base को frozen रखता है और उसके आर-पार छोटे adapters को train करता है। (b) आम तौर पर QAT का वर्णन है: weights बदलते हैं ताकि वे rounding से बच जाएँ। (c) LLM-QAT का data-free distillation है। (d) कुछ ऐसा है जो LLM-QAT भी करता है, और QLoRA नहीं करता।

</details>

4. ▢ torchao के 2-bit experiment में, QAT ने wikitext word perplexity को 6,766 से 30 पर पहुँचाया। क्या इससे दिखता है कि अकेली QAT 2-bit weights को काम करने लायक़ बना देती है?

<details markdown="1"><summary>संकेत</summary>

देखें कि QAT जोड़ने से पहले model के साथ क्या किया जा चुका था, और उसके बिना क्या हुआ।

</details>

<details markdown="1"><summary>जाँचें</summary>

नहीं। उस model की पहली 3 और आख़िरी 2 layers पहले से quantize नहीं की गई थीं, एक क़दम जिसमें model का आकार चुकाना पड़ा था और जिसने perplexity को 603,336 से 6,766 पर पहुँचाया था। उन layers को छोड़े बिना QAT कहीं कम असरदार थी। बहुत कम bits पर QAT एक सामग्री है, संवेदनशील layers को ऊँची precision में रखने के बग़ल में, जो इसका फ़ैसला है कि क्या quantize करना है और कैसे भी।

</details>

5. ▢ आपकी team का PTQ int4 model ठीक है, पर अगला model जो आप train करते हैं उस पर तीन गुना ज़्यादा data से train हुआ है और उसका int4 version साफ़ बदतर score करता है। इस पाठ का साहित्य क्या सुझाता है, और आपको क्या निष्कर्ष नहीं निकालना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

Kumar et al. बताते हैं कि जैसे-जैसे model ज़्यादा data पर train होता है PTQ गिरावट बढ़ती है, इसलिए लंबी training के बाद बड़ा फ़ासला वही है जो scaling-law का सबूत अनुमान लगाता है। परखने के विकल्प हैं ऊँची bit width, मज़बूत PTQ method, या QAT। यह निष्कर्ष न निकालें कि यह अपरिहार्य है और न उसका आकार बताएँ: उनका सबूत 1.7B parameters और 26B tokens तक के models के लिए है, इसलिए तुलना अपने model पर full-precision baseline के मुक़ाबले चलाएँ।

</details>

## असली दुनिया का अभ्यास

- [ ] PyTorch QAT ब्लॉग खोलें और वह वाक्य खोजें कि convert चरण PTQ flow की तुलना में क्या बनाता है। लिखें कि QAT model को PTQ वाले जैसे ही kernels पर deploy करने के लिए इसका क्या मतलब है।
- [ ] कोई quantized open model चुनें जिसे आप deploy कर सकते हैं और उसका model card पढ़ें: क्या वह बताता है कि weights PTQ से आए या QAT से, और कौन-सा calibration या training data इस्तेमाल हुआ?
- [ ] कल: बिना नोट्स के QAT की तीन लागतें, वे स्थितियाँ जहाँ PTQ काफ़ी है, और वह स्थिति जहाँ QAT फ़ायदेमंद है, लिखें।

## आगे बढ़ने के लिए

- [QAT और Hardware शीट](../reference/qat-and-hardware.md)
- [ब्लॉग: "Quantization-Aware Training for Large Language Models with PyTorch", PyTorch, 2024](https://pytorch.org/blog/quantization-aware-training/)
- [पेपर: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., 2023](https://arxiv.org/abs/2305.14314)
- [Finetuning: Memory Budget](../../finetuning/reference/memory-budget.md)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
