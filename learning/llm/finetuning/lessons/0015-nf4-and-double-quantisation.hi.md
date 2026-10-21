---
title: "15. NF4 और Double Quantisation"
description: "वे दो विचार जो QLoRA ने सचमुच दिए"
type: lesson
---

# पाठ 15. NF4 और Double Quantisation

**मिशन से संबंध:** ये वे दो विचार हैं जो QLoRA ने दिए। इन्हें जानना पेपर को समझने और सिर्फ़ abstract पढ़ लेने के बीच का फ़र्क़ है।
**मुख्य स्रोत:** [पेपर: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
**पूर्व-आवश्यकताएँ:** [पाठ 14](0014-quantisation-from-first-principles.md)

## वार्म-अप

1. ▢ Per-tensor के बजाय blockwise quantisation क्यों?

<details markdown="1"><summary>जाँचें</summary>

Outlier सिर्फ़ अपने block के भीतर scale तय करता है, जिससे नुक़सान पूरे tensor की जगह 64 या 128 values तक सीमित रहता है।

</details>

2. ▢ Block size 64 पर fp32 scales के साथ 4-bit weights के लिए प्रति parameter सच्चे bytes?

<details markdown="1"><summary>जाँचें</summary>

0.5625, यानी 4.5 bits, जिसमें 0.5 bit शुद्ध हिसाब-किताब का overhead है।

</details>

3. ▢ 4-bit base के लिए matmul किस precision में होता है?

<details markdown="1"><summary>जाँचें</summary>

ऊँची में, आम तौर पर bf16। Blocks तुरंत dequantise होते हैं और dequantise की हुई copies फेंक दी जाती हैं।

</details>

## यह जानें

QLoRA ने तीन चीज़ें दीं: NF4, double quantisation, और paged optimizers। पहले दो representation के बारे में विचार हैं और दिलचस्प वही हैं। तीसरा engineering का शमन है, जो पाठ 16 में आता है।

### NF4, यानी NormalFloat

4 bits से आपको 16 स्तर मिलते हैं। उन्हें कहाँ रखना चाहिए?

एक-समान फ़ासला, जैसे सादे int4 में, उन्हें सीमा भर में बराबर अंतराल पर रखता है। यह तब इष्टतम है जब values एक-समान रूप से बँटी हों। **Neural network के weights एक-समान रूप से नहीं बँटे होते।** वे लगभग शून्य पर केंद्रित और सामान्य (normal) रूप से बँटे होते हैं, इसलिए ज़्यादातर values शून्य के पास जमा होती हैं और कुछ ही चरम सीमाओं के पास।

इसलिए एक-समान स्तर resolution बर्बाद करते हैं: कई स्तर उन छोरों में पड़े रहते हैं जहाँ लगभग कोई weight रहता ही नहीं, जबकि शून्य के पास का घना इलाक़ा बहुत कम स्तर पाता है।

NF4 का जवाब: 16 स्तरों को standard normal distribution के **quantiles** पर रखें, ताकि हर स्तर सीमा की बराबर मात्रा के बजाय *probability mass* की बराबर मात्रा ढके। स्तर शून्य के पास घने और छोरों में विरल होते हैं, जो इससे मेल खाते हैं कि weights असल में कहाँ हैं। पेपर इसे शून्य-माध्य, सामान्य रूप से बँटे data के लिए सूचना-सिद्धांत के हिसाब से इष्टतम बताता है।

इसके काम करने के लिए, हर block को पहले अपने absmax से भाग देकर `[−1, 1]` में normalise करना होगा, जो ठीक वही है जो blockwise quantisation पहले से store कर रही थी। तो NF4 कोई अतिरिक्त मशीनरी नहीं है; यह पाठ 14 की योजना के भीतर 16 स्तरों का बेहतर चुनाव है।

```text
int4:  levels evenly spaced        → resolution wasted in empty tails
nf4:   levels at normal quantiles  → resolution where the weights are
```

नतीजा यह कि NF4 उसी bit-width पर int4 को हराता है, मुफ़्त में। कोई अतिरिक्त storage नहीं, बस बेहतर codebook।

दो ईमानदार सीमाएँ:

- फ़ायदा इस पर निर्भर है कि weights असल में normal के कितने क़रीब हैं। Pretraining के बाद, प्रति block, वे आम तौर पर होते हैं। यह अनुभवजन्य गुण है, गारंटी नहीं।
- NF4 *weight* का format है। Activations के लिए यह सही औज़ार नहीं, जिनके distributions अलग और कम सुव्यवस्थित हैं।

### Double quantisation

पाठ 14 के overhead पर लौटें। प्रति parameter, block size 64 पर fp32 scales के साथ:

```text
weights            0.5     bytes
scales   4/64  =   0.0625  bytes
                  ────────
                   0.5625  bytes  (4.5 bits)
```

वे scales ख़ुद भी बस एक tensor में संख्याएँ हैं, और बहुत सारी हैं। तो उन्हें भी quantise करें।

Double quantisation fp32 block scales को लेता है, उन्हें समूहों में बाँटता है (पेपर 256 के blocks इस्तेमाल करता है), और उन्हें 8 bits पर अपने दूसरे-स्तर के scale के साथ store करता है। नतीजा:

```text
first-level scales at 8 bits:   1/64      = 0.015625 bytes/param
second-level scales:            4/(64·256) ≈ 0.000244 bytes/param
weights:                                     0.5      bytes/param
                                            ──────────
                                             0.5159   bytes/param  (~4.13 bits)
```

पेपर औसतन लगभग **0.37 bits प्रति parameter** की बचत बताता है, जो 65B model के लिए लगभग 3 GB है। यह शुद्ध हिसाब-किताब से वापस मिली memory की असली मात्रा है।

![प्रति parameter bits की तीन पट्टियाँ। चार-bit वाला weight खंड तीनों में एक जैसा है। अकेले वह 4 bits है; fp32 block scales के साथ आधे-bit का खंड जुड़ता है, 4.5 तक पहुँचते हुए; double quantisation के साथ वह खंड लगभग एक-बटा-आठ bit तक सिकुड़ जाता है, लगभग 4.13 तक पहुँचते हुए।](images/the-tax-not-the-payload.svg)

विचार का आकार देखें: quantisation constants योजना पर एक स्थिर कर थे, और double quantisation ने माल नहीं, कर घटाया।

पट्टियाँ वही बात बिना अंकगणित के कहती हैं। धूसर खंड तीनों बार उतना ही लंबा है, क्योंकि weights के बारे में कुछ नहीं बदला; 4, 4.5 और 4.13 bits के बीच का हर फ़र्क़ अंत का वह छोटा रंगीन टुकड़ा है। जो योजना माल घटाती, उसने धूसर हिस्से को हिलाया होता। यह एक छोटी, चतुर, पूरी तरह यांत्रिक जीत है, और इसीलिए 4-bit QLoRA व्यवहार में 4.5 नहीं बल्कि लगभग 4.1 bits प्रति parameter पर उतरता है।

### Memory का नतीजा

पाठ 6 के उदाहरण को 4-bit base के साथ दोबारा निकालें। 20M-parameter adapter वाला 7B model:

| | bf16 base | 4-bit base |
|---|---|---|
| Frozen base weights | 14.0 GB | ~3.6 GB |
| Adapter state (16 B/param) | 0.32 GB | 0.32 GB |
| **उप-योग** | **14.3 GB** | **3.9 GB** |

Full fine-tuning के 112 GB के सामने, 4-bit adapter run की fixed लागत 4 GB से कम है। Activations (पाठ 7) अब निर्णायक रूप से हावी पद हैं, जिसका मतलब है कि gradient checkpointing यहाँ workspace में कहीं भी से ज़्यादा मायने रखती है।

यही वह नतीजा है जिसने QLoRA को अहम बनाया: उसने बड़े models की fine-tuning को clusters से एक अकेले device पर ला दिया।

### Configuration

```text
quant_config := {
    load_in_4bit: true,
    quant_type: "nf4",            # not "fp4"
    use_double_quant: true,       # the 0.37 bits/param saving
    compute_dtype: "bfloat16",    # storage is 4-bit; compute is not
}
```

चार settings, हर एक इस पाठ की किसी चीज़ से जुड़ी। `bnb_4bit_compute_dtype` वह है जिसे लोग default पर छोड़ देते हैं और नहीं छोड़ना चाहिए: यह वह precision है जिसमें dequantise हुए blocks गुणा होते हैं, और उसे fp32 पर छोड़ना गति के ज़्यादातर फ़ायदे को गँवा देता है।

हमेशा की तरह, इन नामों को installed version के दस्तावेज़ से जाँच लें।

## अभ्यास

1. ▢ NF4 उसी bit-width पर int4 को क्यों हराता है?

<details markdown="1"><summary>जाँचें</summary>

वह अपने 16 स्तरों को एक-समान अंतराल पर रखने के बजाय normal distribution के quantiles पर रखता है, इसलिए resolution वहाँ केंद्रित होता है जहाँ weights असल में जमा होते हैं, शून्य के पास, खाली छोरों पर ख़र्च होने के बजाय।

वही storage, बेहतर codebook। पूर्व-शर्त है हर block को पहले `[−1, 1]` में normalise करना, जो blockwise quantisation पहले से करती है।

</details>

2. ▢ Double quantisation असल में क्या compress करता है, और लगभग कितना बचाता है?

<details markdown="1"><summary>जाँचें</summary>

पहले-स्तर के block scales, यानी weights नहीं बल्कि quantisation constants। उन्हें 256 के समूहों में 8 bits पर, एक छोटे दूसरे-स्तर के scale के साथ, store किया जाता है।

पेपर औसतन लगभग 0.37 bits प्रति parameter बताता है, 65B model के लिए लगभग 3 GB। यह overhead-सहित 4-bit को लगभग 4.5 bits से घटाकर लगभग 4.1 पर लाता है।

</details>

3. ▢ Double quantisation के साथ NF4 में 13B base, और साथ में 30M adapter, के लिए कुल fixed memory निकालें।

<details markdown="1"><summary>जाँचें</summary>

Base: 13e9 × 0.5159 ≈ 6.7 GB। Adapter: 3e7 × 16 = 0.48 GB। लगभग 7.2 GB fixed।

तुलना करें bf16 base और adapter के 26 GB से, और full fine-tuning के 208 GB से। Activations फिर 7.2 GB के ऊपर आते हैं।

</details>

4. ▢ QLoRA का कौन-सा घटक सबसे ज़्यादा memory बचाता है?

    - a) सादे uniform int4 quantisation के बजाय NF4
    - b) Frozen base को bf16 के बजाय 4 bits पर store करना
    - c) पहले-स्तर के block scales का double quantisation
    - d) Memory spikes के दौरान state को बाहर फैला देने वाले paged optimizers

<details markdown="1"><summary>जाँचें</summary>

**b)** Frozen base को bf16 के बजाय 4 bits पर store करना, सबसे बड़े fixed पद पर 4× की कमी।

NF4 उसी storage पर गुणवत्ता सुधारता है। Double quantisation प्रति parameter लगभग 0.37 bits बचाता है। Paged optimizers स्थिर-अवस्था के इस्तेमाल को घटाने के बजाय चरम पर crash रोकते हैं।

</details>

5. ▢ Activations को quantise करने के लिए NF4 अनुपयुक्त क्यों है?

<details markdown="1"><summary>जाँचें</summary>

उसके स्तरों की जगह इस धारणा से निकली है कि values शून्य-माध्य और लगभग normal हैं। Pretraining के बाद के weights इससे ठीक-ठाक मेल खाते हैं; activations नहीं, क्योंकि उनमें व्यवस्थित बड़े-परिमाण वाले outlier features होते हैं, इसलिए normal quantiles उनके लिए ग़लत codebook हैं।

</details>

6. ▢ आप `load_in_4bit=True` रखते हैं और `bnb_4bit_compute_dtype` को default पर छोड़ देते हैं। आपने संभवतः क्या गँवाया?

<details markdown="1"><summary>जाँचें</summary>

गति। Storage अब भी 4-bit है और memory अब भी बच रही है, पर अगर compute dtype fp32 पर default होता है तो हर dequantise हुआ block पूरी precision पर गुणा होता है, जिससे throughput का ज़्यादातर फ़ायदा चला जाता है।

उसे जान-बूझकर bf16 पर रखें। Storage precision और compute precision अलग फ़ैसले हैं।

</details>

## असली दुनिया का अभ्यास

- [ ] Block size 64 पर double quantisation के साथ और बिना, 4-bit के लिए bytes प्रति parameter काग़ज़ पर निकालें। पुष्टि करें कि फ़र्क़ 0.37 bits के क़रीब है।
- [ ] एक ही model को bf16 और NF4 में load करें, दोनों बार memory मापें। अपने अनुमान से तुलना करें।
- [ ] कल: दोनों से एक ही prompt greedy तरीक़े से generate करें और outputs साथ-साथ पढ़ें। गुणवत्ता की क़ीमत की पहली छाप बनाएँ; पाठ 17 इसे माप बनाता है।

## आगे बढ़ने के लिए

- [पेपर: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314): sections 3 और 4 ही यह पाठ हैं
- [दस्तावेज़: bitsandbytes quantization, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
- [memory budget शीट](../reference/memory-budget.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
