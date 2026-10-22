---
title: "4. Training असल में क्या बदलती है"
description: "एक training step के चार ऑपरेशन"
type: lesson
---

# पाठ 4. Training असल में क्या बदलती है

**मिशन से संबंध:** इस workspace का हर memory तर्क, hyperparameter और विफलता का तरीक़ा इस बात से निकलता है कि एक training step क्या करता है।
**मुख्य स्रोत:** [पेपर: "Decoupled Weight Decay Regularization" (AdamW), Loshchilov & Hutter, arXiv:1711.05101](https://arxiv.org/abs/1711.05101)
**पूर्व-आवश्यकताएँ:** [पाठ 1](0001-what-a-base-model-is.md), [पाठ 3](0003-tokenizers-and-chat-templates.md)

## वार्म-अप

1. ▢ Training और serving में एक ही chat template क्यों इस्तेमाल होना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

Template उस token distribution को परिभाषित करता है जिस पर weights फ़िट होते हैं। एक rendering पर train करके दूसरी serve करने का मतलब है अलग समस्या deploy करना, और loss इसे उजागर नहीं करेगा।

</details>

2. ▢ हर उप-परत के चारों ओर residual connection क्या कर रहा है?

<details markdown="1"><summary>जाँचें</summary>

उप-परत के output को चलती stream में बदलने के बजाय उस पर जोड़ देना, ताकि हर block दोबारा लिखने के बजाय एक वृद्धि का योगदान दे।

</details>

3. ▢ उन दो MLP projections के नाम बताएँ जो hidden आयाम को चौड़ा और संकरा करते हैं।

<details markdown="1"><summary>जाँचें</summary>

`up_proj` intermediate आयाम तक चौड़ा करता है, `down_proj` वापस hidden आयाम पर लौटाता है। `gate_proj` बीच में लगने वाला gate बनाता है।

</details>

## यह जानें

एक training step चार ऑपरेशन है। चरण 2 की हर memory लागत इन चारों में से किसी एक का memory में कुछ थामे रखना है।

**1. Forward pass।** Sequences का एक batch model से गुज़ारें और loss compute करें। चरण 3 को संभव बनाने के लिए, हर layer के बीच के नतीजे, यानी **activations**, फेंकने के बजाय रखे जाने चाहिए। इसीलिए training को inference से कहीं ज़्यादा memory चाहिए।

**2. Loss।** Predict किए गए distribution और असली अगले token के बीच cross-entropy, हर उस position पर औसत जो गिना जाता है। कौन-से positions गिने जाएँ, यह आपका चुनाव है, और यह मायने रखता है:

- **Full-sequence loss** हर token को score करता है, user के prompt समेत। Model उत्तरों के साथ prompts भी predict करना सीखता है।
- **Completion-only loss** prompt tokens को mask कर देता है, सिर्फ़ assistant के response को score करता है।

Masking उन positions पर label को `-100` रखकर की जाती है जिन्हें अनदेखा करना है, एक परिपाटी जिसे loss function "छोड़ दो" पढ़ता है। Instruction tuning के लिए आम तौर पर completion-only ही चाहिए होता है: आप responses सिखा रहे हैं, model को user के सवालों की कल्पना करना नहीं सिखा रहे।

**3. Backward pass।** Graph में चेन नियम लगाते हुए पीछे की ओर चलें, जो हर trainable parameter के लिए एक **gradient** बनाता है: वह दिशा और परिमाण जिससे loss घटाने के लिए उस parameter को बदलना चाहिए। हर trainable parameter के लिए एक gradient, parameter जितना ही आकार। इसे याद रखें; यह पाठ 6 का आधा हिस्सा है।

**4. Optimizer step।** Gradients का इस्तेमाल करके parameters को update करें। सादा gradient descent `w ← w − lr · g` होता। कोई उसे इस्तेमाल नहीं करता। **AdamW** हर parameter के लिए दो चलते औसत रखता है:

| State | क्या ट्रैक करता है | असर |
|---|---|---|
| First moment | हाल के gradients का औसत | Momentum, शोर वाली दिशाओं को चिकना करता है |
| Second moment | हाल के gradients के वर्गों का औसत | हर parameter के लिए step की scaling |

दो अतिरिक्त tensors, हर एक parameters जितना बड़ा। यह पाठ 6 का दूसरा आधा हिस्सा है, और यही वजह है कि full fine-tuning इतनी महँगी है।

### Learning rate और schedule

Learning rate step को scale करता है। बहुत ज़्यादा हो तो update आगे निकल जाता है और pretrained संरचना नष्ट कर देता है। यांत्रिक रूप से catastrophic forgetting ऐसा ही दिखता है। बहुत कम हो तो कुछ हिलता नहीं।

दो मानक सुधार:

- **Warm-up:** शून्य के पास से शुरू करें और पहले कुछ सौ steps में बढ़ाएँ, ताकि शुरुआती शोर वाले gradients weights को बिगाड़ न दें।
- **Decay:** training के दौरान rate घटाएँ, आम तौर पर cosine curve पर, ताकि बाद के steps छटपटाने के बजाय सुधार करें।

Adapter fine-tuning, full fine-tuning से एक से दो परिमाण-क्रम ज़्यादा learning rates सह लेती है, आम तौर पर `1e-5` के बजाय लगभग `1e-4` से `2e-4`। पाठ 9 बताता है क्यों।

### Batch size, असली और effective

Gradients एक batch पर औसत किए जाते हैं। बड़े batches कम शोर वाले gradients देते हैं पर activation memory उसी अनुपात में ज़्यादा लगती है। **Gradient accumulation** memory के बिना औसत ख़रीदता है: कई छोटे batches चलाएँ, gradients जोड़ें, एक बार step लें।

```text
effective batch size = per_device_batch_size × gradient_accumulation_steps × num_devices
```

Effective संख्या ही बताएँ और उसी पर तर्क करें। Batch size 1 और 16 accumulation steps वाला run batch-16 का run है, और उसकी तुलना batch-1 के run से ऐसे करना मानो दोनों समतुल्य हों, ग़लत नतीजे पर पहुँचने का आम तरीक़ा है।

### Epoch सीखने की इकाई नहीं है

एक epoch dataset पर एक पूरा pass है। छोटे instruction dataset पर दो या तीन epochs सामान्य सीमा है और उससे ज़्यादा आम तौर पर रट जाता है। Optimizer *steps* की संख्या देखता है, और steps dataset के आकार और effective batch size, दोनों पर साथ निर्भर करते हैं, इसलिए "3 epochs" का मतलब 500 examples पर 5,00,000 examples से बिल्कुल अलग होता है।

## अभ्यास

1. ▢ एक ही batch size और sequence length पर भी, training को inference से बहुत ज़्यादा memory क्यों चाहिए?

<details markdown="1"><summary>जाँचें</summary>

Training को forward pass के activations रखने पड़ते हैं ताकि backward pass gradients compute कर सके, और उसे gradients और optimizer state store करना पड़ता है। Inference हर layer के बीच के नतीजे तभी फेंक देता है जब अगली layer उन्हें इस्तेमाल कर चुकी होती है।

</details>

2. ▢ आप question-and-answer जोड़ों पर fine-tune कर रहे हैं। Loss पूरी sequence पर compute होना चाहिए या सिर्फ़ उत्तर पर? ग़लत चुनाव का नतीजा बताएँ।

<details markdown="1"><summary>जाँचें</summary>

ज़्यादातर मामलों में सिर्फ़ उत्तर पर। Prompt को भी score करने से capacity इसमें ख़र्च होती है कि model संभावित user सवाल generate करना सीखे, जो task नहीं है, और उस हिस्से पर gradient का संकेत पतला हो जाता है जिसकी आपको परवाह है।

अपवाद तब है जब prompts बहुत शैलीबद्ध हों और आप चाहें कि model domain की भाषा को आम तौर पर आत्मसात कर ले। सोच-समझकर तय करें; default को अपने लिए तय न करने दें।

</details>

3. ▢ AdamW प्रति trainable parameter कितने अतिरिक्त tensors store करता है, और वे क्या हैं?

<details markdown="1"><summary>जाँचें</summary>

दो: gradients का चलता औसत (first moment) और gradients के वर्गों का चलता औसत (second moment)। हर एक का आकार parameter जितना ही है।

साथ में gradient ख़ुद, जो तीसरा उसी आकार का tensor है पर optimizer state नहीं है। इन तीनों को अलग-अलग रखना ठीक वही है जो पाठ 6 आपसे करवाता है।

</details>

4. ▢ Run A: batch size 8, accumulation 1। Run B: batch size 1, accumulation 8। वही data, वही seed, वही learning rate। क्या optimizer steps समतुल्य हैं?

<details markdown="1"><summary>जाँचें</summary>

असल में हाँ: दोनों step लेने से पहले 8 examples पर gradients औसत करते हैं, इसलिए update लगभग वही है, और B बहुत कम activation memory इस्तेमाल करता है। छोटे फ़र्क़ इस बात से रह जाते हैं कि padding और प्रति-batch normalisation आपस में कैसे असर डालते हैं।

Gradient accumulation सीमित memory पर बड़ा effective batch पाने का मानक तरीक़ा है। जो समतुल्य *नहीं* है, वह है B की तुलना असली batch-1 run से करना, जो ज़्यादा शोर वाले gradients पर आठ गुना ज़्यादा बार step लेता है।

</details>

5. ▢ एक सहकर्मी LoRA run का learning rate `1e-5` रखता है "क्योंकि full fine-tuning यही इस्तेमाल करती है"। आप क्या उम्मीद करते हैं, और आप क्या कहते हैं?

<details markdown="1"><summary>जाँचें</summary>

Underfitting की उम्मीद करें: loss धीरे घटता है, model मुश्किल से बदलता है, और run इस बात का सबूत जैसा दिखता है कि यह तरीक़ा काम नहीं करता।

Adapters शून्य योगदान से शुरू होते हैं और parameters का बहुत छोटा अंश थामते हैं, इसलिए उन्हें हिलने तक के लिए कहीं बड़ा rate चाहिए, आम तौर पर `1e-4` से `2e-4`। Full fine-tuning का learning rate ले आना, पहले LoRA run के निराश करने की सबसे आम वजहों में से एक है।

</details>

6. ▢ Warm-up अंधविश्वास से ज़्यादा क्यों है?

<details markdown="1"><summary>जाँचें</summary>

Training की शुरुआत में AdamW का second-moment अनुमान बहुत कम samples से बनता है, इसलिए उसकी प्रति-parameter scaling अविश्वसनीय होती है और बहुत बड़े steps दे सकती है। Learning rate को धीरे-धीरे बढ़ाना उस नुक़सान को सीमित करता है जो वे पहले steps pretrained weights को पहुँचा सकते हैं।

</details>

## असली दुनिया का अभ्यास

- [ ] Training step के चारों ऑपरेशन याद से लिखें, फिर उन्हें इस पाठ से मिलाकर जाँचें।
- [ ] कोई भी प्रकाशित fine-tuning script लें और उसका effective batch size, learning rate, warm-up और schedule पहचानें। चारों संख्याएँ लिख लें।
- [ ] कल: कोई ऐसा training config ढूँढें जहाँ आप उन चार संख्याओं में से किसी एक से असहमत हों, और एक वाक्य में लिखें कि आप क्या बदलते और क्यों।

## आगे बढ़ने के लिए

- [पेपर: "Decoupled Weight Decay Regularization" (AdamW), Loshchilov & Hutter, arXiv:1711.05101](https://arxiv.org/abs/1711.05101)
- [पेपर: "Adam: A Method for Stochastic Optimization", Kingma & Ba, arXiv:1412.6980](https://arxiv.org/abs/1412.6980)
- [लेख: "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
- [memory budget शीट](../reference/memory-budget.md): चरण 2 इन चार steps को bytes में बदलता है

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
