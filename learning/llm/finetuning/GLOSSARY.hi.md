---
title: "शब्दावली"
description: "Adapter fine-tuning के मानक शब्द"
type: glossary
---

# Adapter Fine-Tuning शब्दावली

इस workspace के मानक शब्द। कोई शब्द यहाँ तब जुड़ता है जब उसे सही ढंग से इस्तेमाल किया जा सके, पहली बार ज़िक्र आने पर नहीं, इसलिए यह सूची पाठों के साथ-साथ बढ़ती है।

## इस workspace में इस्तेमाल

तीन शब्द इस क्षेत्र में इतने ढीले ढंग से इस्तेमाल होते हैं कि आगे के पाठों में भ्रम पैदा हो सकता है, इसलिए उन्हें शुरू से ही बाँध दिया गया है:

**Fine-tuning**:
किसी task पर थोड़े-से जोड़े गए या चुने गए parameters को train करना, जबकि base model के weights frozen रहते हैं। जब सारे weights train किए जाते हैं, तो यह workspace हमेशा साफ़ तौर पर _full fine-tuning_ कहता है।
_बचें_: training, retraining, teaching the model

**Adapter**:
frozen base model के साथ जोड़े गए train होने वाले weights का छोटा सेट, और वह configuration जो बताती है कि वे कहाँ जुड़ते हैं।
_बचें_: fine-tune (संज्ञा के रूप में), LoRA (जब तरीक़ा ख़ास तौर पर LoRA न हो), checkpoint

**Quantisation**:
weights को उस precision से कम numeric precision में store करना जिसमें वे train हुए थे। इस workspace में, जब तक अलग से न कहा जाए, यह हमेशा _frozen base_ को दर्शाता है: adapters ऊँची precision में रहते हैं, और inference के लिए quantisation एक अलग मुद्दा है।
_बचें_: compression, shrinking, optimisation

## शब्द

**Base model**:
ऐसा model जो सिर्फ़ एक objective पर train हुआ है: बड़े corpus में अगला token predict करना। यह text को आगे बढ़ाता है, उसका जवाब नहीं देता, और इसका कोई _chat template_ नहीं होता।
_बचें_: raw model, pretrained model (जब _instruct model_ से अंतर मायने रखता हो)

**Catastrophic forgetting**:
fine-tuning के दौरान उन क्षमताओं का बिगड़ना जिन्हें training data ने मज़बूत नहीं किया, जैसे सामान्य instruction following। यह task के loss या held-out metric में नहीं दिखता, जो इसके होते हुए भी बेहतर हो सकते हैं।
_बचें_: overfitting (एक अलग विफलता, जो task के अपने _held-out set_ पर दिखती है)

**Chat template**:
वह सटीक string format जिसमें किसी chat model की training conversations को ढाला गया था, जो roles और messages को एक सपाट token sequence में बदलता है। Training और serving में एक ही rendering इस्तेमाल होनी चाहिए।
_बचें_: prompt format, chat format

**Contamination**:
ऐसे test examples जिन्हें model पहले देख चुका है। _आपकी_ contamination वे test examples हैं जो आपके training set में भी (हू-ब-हू या लगभग) मौजूद हैं; _विरासत में मिली_ contamination वे test examples हैं जो _base model_ के pretraining corpus में थे।
_बचें_: leakage (बताएँ कि दोनों में से कौन-सी किस्म मतलब है)

**DoRA**:
एक _LoRA_ variant जो हर frozen weight matrix को एक magnitude vector, जिसे सीधे train किया जाता है, और एक direction में बाँटता है, जिसे low-rank update मिलता है और जिसे बाद में renormalise किया जाता है। PEFT में यह LoRA config का एक flag है, कोई अलग तरीक़ा नहीं।
_बचें_: weight-decomposed LoRA (एक बार पूरा लिखें, फिर DoRA कहें)

**Double quantisation**:
blockwise scales की ख़ुद की _quantisation_: पहले स्तर के fp32 scales को समूहों में बाँटकर 8 bits में store किया जाता है, उनके अपने दूसरे स्तर के scale के साथ।
_बचें_: nested quantisation, 2-bit quantisation

**Effective batch size**:
उन examples की संख्या जिनके gradients का औसत लेकर एक optimiser step बनता है: प्रति-device batch size × gradient accumulation steps × devices की संख्या।
_बचें_: batch size (जब प्रति-device संख्या मतलब हो)

**Gradient checkpointing**:
forward pass में हर block का सिर्फ़ input रखना और backward pass के उस block तक पहुँचने पर block को दोबारा चलाना, ताकि store की गई activations depth के साथ रैखिक रूप से नहीं, बल्कि लगभग उसके वर्गमूल के अनुसार बढ़ें, और बदले में हर step में लगभग एक अतिरिक्त forward pass लगे।
_बचें_: checkpointing (अकेला, क्योंकि training checkpoint disk पर सहेजे गए weights होते हैं), activation recomputation

**Held-out set**:
वह data जिस पर model train नहीं होता, और जिससे मापा जाता है कि उसने task सीखा या नहीं। इस workspace में इसके दो हिस्से हैं: validation, जिसके आधार पर settings और checkpoints चुने जाते हैं, और test, जिसे अंत में सिर्फ़ एक बार छुआ जाता है।
_बचें_: eval set, dev set

**Instruct model**:
एक _base model_ जिसे आगे instruction और response के जोड़ों पर, और आम तौर पर उसके बाद preference data पर, train किया गया हो। यहाँ chat model का मतलब भी यही है।
_बचें_: aligned model, assistant model

**LoRA**:
Low-rank adaptation: एक _adapter_ जो किसी weight matrix के update को दो छोटे matrices के गुणनफल `ΔW = BA` के रूप में सीखता है, जिसे `α/r` से scale किया जाता है, जबकि matrix ख़ुद frozen रहता है।
_बचें_: adapter (जब ख़ास तरीक़ा मतलब हो), low-rank fine-tune

**LoRA alpha**:
स्थिर scalar `α` (`lora_alpha`) जो _LoRA_ update को `α/r` से scale करता है। update का scale अनुपात `α/r` तय करता है, कोई एक संख्या अकेले नहीं।
_बचें_: scaling factor (वह `α/r` है, `α` नहीं)

**Merging**:
_LoRA_ update को base weights में मिला देना, `W₀ + (α/r)BA`, और adapter की संरचना हटा देना। full-precision base के मुक़ाबले यह सटीक है और quantized base के मुक़ाबले lossy।
_बचें_: exporting, baking in

**Multi-adapter serving**:
एक साझा base पर कई _adapters_ को serve करना, अलग-अलग adapters वाले requests को साथ batch करके: base की गणना पूरे batch में साझा होती है, और हर request के adapter का योगदान अलग से निकाला जाता है।
_बचें_: adapter swapping (भोला तरीक़ा जो requests को एक-एक करके चलाता है)

**NF4**:
NormalFloat, एक 4-bit format जिसके 16 levels शून्य के आसपास सामान्य रूप से वितरित मानों के लिए, जैसे weights होते हैं, फैलाए गए हैं, सादे int4 की तरह बराबर अंतराल पर नहीं। इसे blockwise _quantisation_ के भीतर, अपने absmax से पहले ही normalise किए गए blocks पर इस्तेमाल किया जाता है।
_बचें_: int4 (एक अलग, समान दूरी वाला format)

**Optimiser state**:
वे tensors जो optimiser हर trainable parameter के लिए weight और उसके gradient के अलावा रखता है। AdamW के लिए ये पहला और दूसरा moment हैं, हर एक 4 bytes का।
_बचें_: optimizer cache, momentum (सिर्फ़ पहला moment)

**Packing**:
छोटे training examples को पूरी लंबाई के sequences में जोड़ना, ताकि batch में लगभग कोई padding न रहे।
_बचें_: length grouping (एक अलग उपाय, जो समान आकार के sequences को साथ batch करता है)

**QLoRA**:
_LoRA_ जिसे _NF4_ में store किए गए, _double quantisation_ वाले frozen base के विरुद्ध train किया जाता है, और जिसे हर forward और backward pass पर dequantise किया जाता है। यह सस्ते base वाला LoRA है, अपने hyperparameters वाला कोई अलग तरीक़ा नहीं।
_बचें_: 4-bit fine-tuning, quantized LoRA (जब इससे लगे कि adapter quantized है)

**Rank**:
दोनों _LoRA_ matrices का भीतरी आयाम `r`, जहाँ `A` का आकार `r × d_in` और `B` का `d_out × r` है। यह adapter की क्षमता है: यह तय करती है कि adapter कितना जटिल update व्यक्त कर सकता है।
_बचें_: size, dimension (अकेला)

**Regression suite**:
task के बाहर की probes का एक स्थिर सेट (सामान्य instruction following, format और व्यवहार का पालन, safety और refusal व्यवहार, पास की क्षमता), जिसे _catastrophic forgetting_ पकड़ने के लिए training से पहले और बाद में चलाया जाता है। यह _held-out set_ से अलग औज़ार है, और दोनों ज़रूरी हैं।
_बचें_: benchmark, eval suite (जब यही ख़ास औज़ार मतलब हो)

**Target modules**:
वे weight matrices जिनसे कोई _adapter_ जुड़ता है, जिन्हें model के अपने module नामों से पुकारा जाता है।
_बचें_: layers (adapter किसी layer के भीतर के ख़ास matrices से जुड़ता है)
