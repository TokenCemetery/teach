---
title: "What the Student Inherits"
description: "Fidelity, imitation gap, capacity gap और अनचाही विशेषताएँ, हर स्रोत की setting और संख्याओं के साथ"
type: reference
---

# Student को क्या विरासत में मिलता है: Fidelity, Imitation Gap, Capacity Gap और छिपी विशेषताएँ

चरण 6 का संक्षिप्त रूप, खोजने के लिए। [पाठ 17](../lessons/0017-fidelity-and-generalization.md) fidelity बनाम generalization को कवर करता है, [पाठ 18](../lessons/0018-the-imitation-gap.md) imitation gap को, और [पाठ 19](../lessons/0019-capacity-gap-and-hidden-traits.md) capacity gap और छिपी विशेषताओं को।

## Student अपने teacher से चार तरह से अलग हो सकता है

| Gap | क्या अलग है | स्रोत | Setting |
|---|---|---|---|
| Fidelity | उन्हीं inputs पर predictions, तब भी जब accuracy मिलती-जुलती हो | Stanton et al., 2021 | Image classification, appendix में MNIST, CIFAR-100, ImageNet और IMDB sentiment के साथ |
| Imitation | Style तेज़ी से नक़ल हुआ, क्षमता नहीं | Gudibande et al., 2023 | ChatGPT की नक़ल करते LLaMA और GPT-2 students |
| Capacity | बहुत बड़ा teacher ख़राब student दे सकता है | Mirzadeh et al., 2019, और Cho और Hariharan, 2019 | CIFAR और ImageNet पर CNNs और ResNets |
| छिपी विशेषताएँ | कोई विशेषता ऐसे data से पास होती है जिसमें उसका ज़िक्र नहीं | Cloud et al., 2025 | GPT-4.1 परिवार और Qwen2.5-7B, साथ में एक छोटा MNIST मामला |

चारों में से सिर्फ़ दो को language models पर परखा गया, और यहाँ capacity-gap का कोई सबूत LLMs से नहीं है।

## Fidelity मापना

| Metric | परिभाषा | क्या चाहिए |
|---|---|---|
| Top-1 agreement | Inputs का वह अंश जहाँ student और teacher एक ही शीर्ष label चुनें | Teacher की predictions |
| Predictive KL | Inputs पर औसत KL(teacher, student) | Teacher का पूरा distribution |
| नियंत्रण | दूसरा student जो उसी तरह स्वतंत्र teacher से distil हुआ | दूसरा distillation run |

Accuracy, agreement को कसकर नहीं बाँधती। Teacher accuracy 93% और student accuracy 91% के साथ, agreement 84% और 98% के बीच है।

## संख्याओं में Stanton et al.

| अवलोकन | संख्या या दिशा |
|---|---|
| पर्याप्त data के साथ MNIST पर LeNet-5 | 99% से ऊपर top-1 test agreement |
| CIFAR-100 पर ResNet-56 self-distillation, सबसे बड़ा सेट | Test agreement 80% से नीचे |
| वही, 50k GAN images जोड़ने पर, distillation data पर ही agreement | 95% |
| वही, संयुक्त भारी augmentation के साथ, self-distillation में train agreement | लगभग 60% |
| ResNet-20 self-distillation, 300 epochs और 5,000 epochs पर SGD train agreement | 78.95% और 83.3% |
| Self-distillation, ज़्यादा data | Fidelity ऊपर, test accuracy नीचे |
| 3-ensemble teacher, ज़्यादा data | Fidelity और accuracy दोनों ऊपर |

उनकी व्याख्या optimization है: student अपने train होने वाले data पर भी teacher से मेल नहीं बिठाता। ज़्यादा distillation data teacher के function की पहचान में मदद करता है और optimization को कठिन बनाता है।

## संख्याओं में Gudibande et al.

| अवलोकन | संख्या |
|---|---|
| ChatGPT के बराबर या बेहतर के रूप में imitation outputs की Crowd ratings | लगभग 70% |
| Natural Questions, LLaMA 7B: base, broad imitation, local imitation, ChatGPT | 17, 10, 22, 31 |
| Natural Questions, LLaMA 13B: base, broad imitation, local imitation, ChatGPT | 20, 15, 27, 31 |
| आधिकारिक tone वाले outputs: base LLaMA बनाम imitation models | 57% बनाम 98% से 99% |

उनका दावा: मौजूदा तरीक़ों से फ़ासला सिर्फ़ imitation data की भारी-भरकम मात्रा या ज़्यादा सक्षम base model से पटता है, और उनके experiments में बेहतर base model ने ज़्यादा imitation data से ज़्यादा मदद की। किसी एक task की local imitation, broad imitation से कहीं बेहतर चली। Imitation models कम toxic भी हुए, teacher की तरह परहेज़ करना सीखते हुए।

## Capacity gap का सबूत

| स्रोत | खोज | आज़माया गया उपाय |
|---|---|---|
| Mirzadeh et al. | Teachers के 4 से 10 layers तक बढ़ने पर 2-layer student की accuracy बढ़ी फिर गिरी | Teacher assistant। मानक distillation के ऊपर फ़ायदा ResNet पर 0.33 से 0.41 अंक, CIFAR-10 के साथ सादे CNN पर 0.94 अंक |
| Cho और Hariharan | ImageNet पर ResNet18: शून्य से 30.24% error, ResNet18, 34 और 50 teachers के साथ 30.57%, 30.79% और 30.95% | जल्दी रोके गए distillation ने 29.01%, 29.16% और 29.35% दिया। जल्दी रोके गए teachers ने CIFAR-10 पर मदद की। बीच के model के ज़रिए श्रृंखला ने मदद नहीं की |
| Gu et al. (MiniLLM) | GPT-2 125M student, 340M, 760M और 1.5B के teachers के साथ सुधरा | उस दायरे में कोई gap नहीं दिखा, एक परिवार |

दोनों vision पेपर इस पर असहमत हैं कि बीच का model मदद करता है या नहीं। अपने जोड़े पर परखें।

## छिपी विशेषताएँ, Cloud et al.

| मद | विवरण |
|---|---|
| Setup | कोई विशेषता वाला teacher असंबद्ध data generate करता है, data filter होता है, उसी base का student उस पर fine-tune होता है |
| उल्लू की पसंद | पहले लगभग 12%, बाद में 60% से ज़्यादा, सिर्फ़ संख्याओं से |
| संख्याओं से Misalignment | लगभग 10% misaligned responses, base के लिए 0% और controls के लिए 1% से कम के मुक़ाबले |
| Filter की गई chain of thought से Misalignment | लगभग 0% से 8%, controls 1% से कम |
| पहचान | Prompted classifiers और in-context learning विशेषता को भरोसेमंद ढंग से पहचान नहीं पाए |
| शर्त | साझा base model। GPT-4.1 nano से Qwen2.5 तक transmit नहीं हुआ। GPT-4o और GPT-4.1 ने किया, संभवतः साझा initialization |
| खुली सीमाएँ | कृत्रिम tasks, और कौन-सी विशेषताएँ कब transmit होती हैं यह अज्ञात है |

## लक्षण, संभावित कारण, जाँच

| लक्षण | संभावित कारण | जाँच |
|---|---|---|
| Student accuracy में teacher से मेल खाता है पर outputs अलग हैं | कम fidelity | Held-out inputs पर top-1 agreement और predictive KL, स्वतंत्र-teacher नियंत्रण के साथ |
| Crowd ratings या judge scores ऊँचे, लक्षित benchmarks सपाट | Style नक़ल हुआ, क्षमता नहीं | उन tasks पर benchmarks जिन्हें data ने मुश्किल से कवर किया, base model के विरुद्ध |
| Student छोटे teacher के student से बदतर | Capacity gap | सीधा, एक बीच का model, जल्दी रोका गया teacher, शून्य से baseline के विरुद्ध |
| Data साफ़ होने पर भी अवांछित व्यवहार दिखता है | साझा base से छिपी विशेषता | Student को उस व्यवहार के लिए सीधे evaluate करें, और अलग base पर विचार करें |
| Student अपने teacher की तरह refuse करता है | Refusal का व्यवहार style के साथ transfer होता है | तय prompt set पर teacher से refusal दरों की तुलना करें |

## इसमें क्या कवर नहीं है

- यहाँ पढ़ा कोई स्रोत नहीं दिखाता कि student अपने teacher की तथ्यात्मक ग़लतियाँ नक़ल करता है।
- Capacity gap और fidelity gap vision models पर मापे गए, LLMs पर नहीं।
- Subliminal learning कृत्रिम tasks पर दिखा, और अलग base का उसे रोकना उन experiments में एक अवलोकन था, गारंटी नहीं।
