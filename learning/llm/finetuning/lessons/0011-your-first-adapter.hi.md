---
title: "11. आपका पहला Adapter"
description: "ऐसा run जो किसी और चीज़ को साबित करने से पहले pipeline को साबित करे"
type: lesson
---

# पाठ 11. आपका पहला Adapter

**मिशन से संबंध:** "इसे चलाएँ" मिशन में है। इससे पहले का सब कुछ पढ़ाई थी; यह run है।
**मुख्य स्रोत:** [दस्तावेज़: SFTTrainer, Hugging Face TRL](https://huggingface.co/docs/trl/main/en/sft_trainer)
**पूर्व-आवश्यकताएँ:** [पाठ 3](0003-tokenizers-and-chat-templates.md), [पाठ 9](0009-rank-alpha-and-initialisation.md), [पाठ 10](0010-choosing-target-modules.md)

## वार्म-अप

1. ▢ Target modules के लिए आधुनिक default क्या है, और वह किफ़ायती क्यों है?

<details markdown="1"><summary>जाँचें</summary>

सभी linear layers, उदार rank पर। Adapter के parameters activation memory के सामने नगण्य हैं, इसलिए उन्हें सीमित करने से अब ज़्यादा कुछ नहीं बचता।

</details>

2. ▢ Code की कौन-सी पंक्ति उस target-module नाम को पकड़ती है जो किसी से मेल नहीं खाया?

<details markdown="1"><summary>जाँचें</summary>

`model.print_trainable_parameters()`। शून्य के पास गिनती का मतलब है कि adapter किसी से नहीं जुड़ा।

</details>

3. ▢ Training या inference: `add_generation_prompt=True` कहाँ आता है?

<details markdown="1"><summary>जाँचें</summary>

Inference में। Training में assistant का turn पहले से text में है, इसलिए prompt जोड़ने से marker दोहराया जाता है।

</details>

## यह जानें

### सबसे छोटी चीज़ चुनें जो जानकारी देते हुए विफल हो सके

आपके पहले run का मक़सद अच्छा model **नहीं** है। वह यह साबित करना है कि pipeline सही जुड़ा है। इसलिए उसे इतना सस्ता बनाएँ कि ग़लती की क़ीमत मिनटों में चुके:

- 0.5B से 3B वर्ग का base model। छोटे models तेज़ train होते हैं और data के bugs को बड़ों जितनी ही अच्छी तरह उजागर करते हैं।
- कुछ सौ examples। इतने कि loss को हिलते देखा जा सके।
- `max_steps` लगभग 20 से 50, epochs नहीं। आप चाहते हैं कि वह जल्दी ख़त्म हो।

Pipeline के साबित होने से पहले कुछ भी optimise करना बेकार मेहनत है, और यह छिपा देता है कि कौन-से बदलाव से कौन-सा असर हुआ।

### एक न्यूनतम run

```text
dataset := load_dataset("<a small instruction dataset>", split: "train[:500]")

adapter_config := {
    rank: 16,
    alpha: 32,
    dropout: 0.05,
    adapt_bias: false,
    target_modules: "all-linear",
}

run_config := {
    output_dir: "runs/first-adapter",
    max_steps: 50,
    per_device_batch_size: 1,
    gradient_accumulation_steps: 8,      # effective batch size 8
    learning_rate: 2e-4,
    warmup_steps: 5,
    lr_schedule: "cosine",
    logging_steps: 1,                    # every step, for the first run
    max_length: 1024,
    gradient_checkpointing: true,
    precision: "bf16",
}

trainer := new_trainer(
    model: "<a small base model>",
    train_dataset: dataset,
    adapter_config: adapter_config,
    run_config: run_config,
)

trainer.train()
trainer.save("runs/first-adapter/final")
```

इस API सतह पर दो टिप्पणियाँ। `SFTTrainer` model की *string* स्वीकार करता है और उसे आपके लिए load कर देगा। Sequence length `SFTConfig` पर `max_length` है। ये दोनों releases के बीच बदल चुके हैं, इसलिए **इस snippet या अपनी याद पर भरोसा करने के बजाय installed version का दस्तावेज़ पढ़ें।** यह निर्देश खानापूर्ति नहीं है; यह इस पूरे workspace में बर्बाद दोपहरों का सबसे भरोसेमंद स्रोत है।

### Precision, hardware, और असल में क्या बदलता है

`bf16=True` के लिए bfloat16 का hardware support चाहिए, जो आधुनिक accelerators पर व्यापक है पर सार्वभौमिक नहीं। पुराने devices पर आपको loss scaling के साथ fp16 की ज़रूरत पड़ सकती है, और कुछ backends पर full fp32 ही एकमात्र विकल्प है। पाठ 5 का सिद्धांत वही है; सिर्फ़ उपलब्ध formats अलग हैं।

इसी तरह, इस script के पीछे का ख़ास accelerator तरीक़े का हिस्सा नहीं है। अवधारणाएँ, अंकगणित और विफलता के तरीक़े CUDA, ROCm, Intel, Apple Silicon और CPU पर एक जैसे हैं। जो अलग है वह यह कि कौन-से kernels optimised हैं, कौन-सी precisions support होती हैं, और एक step में कितना समय लगता है। जहाँ कोई backend तरीक़े को सचमुच बाँधता है, यह workspace साफ़ कहता है; [पाठ 16](0016-training-through-a-quantized-base.md) देखें।

### चार जाँचें, क्रम से

इन्हें तब चलाएँ जब आप loss curve की परवाह करें उससे पहले।

**1. क्या adapter मौजूद है?**

```python
trainer.model.print_trainable_parameters()
```

अपने पाठ 8 के अंकगणित से मिलाएँ। शून्य गिनती, या वह जो rounding से ज़्यादा अलग हो, का मतलब है रुकें और ठीक करें।

**2. क्या data वैसा है जैसा आप सोचते हैं?**

```python
example = trainer.train_dataset[0]
print(repr(tokenizer.decode(example["input_ids"])))
labels = example["labels"]
print(sum(1 for l in labels if l != -100), "of", len(labels), "positions scored")
```

एक असली training example decode करें और उसे पढ़ें। यह एक जाँच template mismatch, गुम end-of-turn tokens, masking का bug, और उत्तर के बीच में truncation पकड़ लेती है: ख़राब fine-tune के पाँच सबसे आम कारणों में से चार। **इसे न छोड़ें।** यह पूरी प्रक्रिया के सबसे क़ीमती दस सेकंड हैं।

**3. क्या loss हिलता है?**

`logging_steps=1` के साथ 50 steps में, loss साफ़ गिरना चाहिए। Step एक से सपाट loss का मतलब है कि adapter जुड़ा नहीं है, learning rate बहुत ही कम है, या कुछ score नहीं हो रहा।

**4. क्या वह दो examples पर overfit कर सकता है?**

उपलब्ध सबसे मज़बूत smoke test। दो examples पर सौ steps train करें। Loss को शून्य के पास पहुँचना चाहिए। अगर वह दो examples रट नहीं सकता, तो pipeline टूटा है, और आपने यह छह घंटे के run के बाद नहीं, दो मिनट में जान लिया।

### जो दोहराने के लिए चाहिए उसे सहेजें

Adapter directory छोटी होती है, आम तौर पर एक अंक से लेकर कुछ सौ megabytes, और उसमें सिर्फ़ adapter के weights और एक config होती है जो base model, rank, alpha और target modules दर्ज करती है। उस सटीक base model के बिना वह बेकार है, इसलिए base model का identifier और उसकी revision उसके साथ दर्ज करें।

Library versions भी दर्ज करें। जो config छह महीने पहले साफ़ train हुई थी वह शायद उसी तरह load न हो, और "यह कौन-सा version था" बाद में वापस नहीं मिलता।

## अभ्यास

1. ▢ आपके पास 50,000 examples और एक बड़ा base model उपलब्ध है। वह पहला run ग़लत क्यों है?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि पहले run का काम pipeline को साबित करना है, और लंबा महँगा run वही जानकारी देता है जो छोटा सस्ता, बस बहुत देर से और ऊँची क़ीमत पर।

बदतर, अगर कुछ ग़लत है तो आप मिनटों के बजाय घंटों बाद जानते हैं, और आप नहीं बता सकते कि कई बदलावों में से कौन-सा मायने रखता था।

</details>

2. ▢ Loss step एक से पूरी तरह सपाट है। तीन कारण बताएँ, उस क्रम में जिसमें आप उन्हें जाँचेंगे।

<details markdown="1"><summary>जाँचें</summary>

1. Adapter किसी से नहीं जुड़ा; `print_trainable_parameters()` जाँचें।
2. हर label `-100` है, इसलिए कुछ score नहीं हो रहा; किसी असली example पर label की गिनती जाँचें।
3. Learning rate कई परिमाण-क्रम बहुत कम है; जाँचें कि वह लगभग `1e-4` है, `1e-5` या उससे कम नहीं।

तीनों को ख़ारिज करना एक पंक्ति का काम है, इसीलिए वे किसी भी सूक्ष्म चीज़ से पहले आते हैं।

</details>

3. ▢ Dataset पर भरोसा करने के बजाय training example को decode क्यों करें?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि जो विफलताएँ मायने रखती हैं वे dataset में अदृश्य हैं और decode किए text में दिखती हैं: ग़लत chat template, गुम end-of-turn token, वे prompt tokens जिन्हें mask होना था और नहीं हैं, `max_length` से वाक्य के बीच में कटा उत्तर।

इनमें से कोई error नहीं देता। सब ऐसा run बनाते हैं जो ठीक दिखता है और ऐसा model जो नहीं है।

</details>

4. ▢ आपका adapter सौ steps में दो examples पर loss को शून्य के पास नहीं ला सकता। यह आपको क्या बताता है?

<details markdown="1"><summary>जाँचें</summary>

कि pipeline टूटा है, task कठिन नहीं है। दो examples को कोई भी चलता हुआ adapter आसानी से रट सकता है।

बिना जुड़ा adapter, पूरी तरह mask किए labels, शून्य के पास learning rate, या ऐसा data collator ढूँढें जो वह नहीं बना रहा जिसकी आप उम्मीद करते हैं।

</details>

5. ▢ आपके पास adapter directory है और कुछ नहीं। क्या आप उसे इस्तेमाल कर सकते हैं?

<details markdown="1"><summary>जाँचें</summary>

तभी जब आप वह सटीक base model पहचान सकें जिसके सामने उसे train किया गया था, जिसे adapter config नाम से दर्ज करती है। किसी दूसरे base पर लगाने पर, उसी परिवार के किसी और checkpoint पर भी, नतीजा ज़्यादा से ज़्यादा बिगड़ा हुआ और बदतर में बकवास है।

Base model का identifier, उसकी revision, और अपने library versions दर्ज करें। Adapter एक diff है, और diff को अपना base चाहिए।

</details>

6. ▢ 4 devices पर `per_device_train_batch_size=2`, `gradient_accumulation_steps=8` के लिए effective batch size?

<details markdown="1"><summary>जाँचें</summary>

2 × 8 × 4 = 64।

यह संख्या बताएँ, प्रति-device वाली नहीं। Runs की तुलना प्रति-device batch size से करना ग़लत नतीजे पर पहुँचने का भरोसेमंद तरीक़ा है।

</details>

## असली दुनिया का अभ्यास

- [ ] किसी भी असली training से पहले दो-example वाला overfitting test चलाएँ। पुष्टि करें कि loss शून्य के पास पहुँचता है।
- [ ] एक training example को पूरा decode करके पढ़ें। गिनें कि कितने positions score होते हैं और कितने mask।
- [ ] 50-step का run शुरू से अंत तक पूरा करें और adapter सहेजें। Disk पर उसका आकार नोट करें।
- [ ] कल: base model का identifier, revision और हर library version, adapter के बगल की एक file में लिख लें।

## आगे बढ़ने के लिए

- [दस्तावेज़: SFTTrainer, Hugging Face TRL](https://huggingface.co/docs/trl/main/en/sft_trainer)
- [दस्तावेज़: LoRA, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [failure modes शीट](../reference/failure-modes.md): run के दौरान इसे खुला रखें
- [पाठ 12. Training Run को पढ़ना](0012-reading-a-training-run.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
