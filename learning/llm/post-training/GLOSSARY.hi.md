---
title: "शब्दावली"
description: "LLM post-training के मानक शब्द"
type: glossary
---

# LLM Post-Training शब्दावली

pretrained model को align करने के मानक शब्द: हर training objective क्या maximize करता है, और objective जब text की नक़ल से बदलकर reward को optimize करने की ओर जाता है तो क्या बदलता है।

## शब्द

**Alignment tax**:
क्षमता का वह नुक़सान (आम तौर पर pretraining-style benchmarks पर मापा जाता है) जो helpfulness या safety के लिए optimize करने के साइड-इफ़ेक्ट के रूप में post-training से आ सकता है।
_बचें_: regression (regression कोई भी क्षमता गिरना है; alignment tax उस ख़ास गिरावट का नाम है जो alignment के बदले चुकाई जाती है)

**Bradley-Terry loss**:
Pairwise preference data पर reward model को train करने के लिए इस्तेमाल होने वाला loss function, जो इस संभावना को कि एक completion दूसरे से ज़्यादा पसंद की गई, उनके scalar reward scores के अंतर का फलन मानता है।
_बचें_: preference loss (इस क्षेत्र में कई objectives के लिए ढीले ढंग से इस्तेमाल होता है, DPO के लिए भी; Bradley-Terry उस ख़ास pairwise-comparison model का नाम है जो reward modeling इस्तेमाल करती है)

**Group-relative advantage**:
सीखे हुए value function की जगह GRPO का विकल्प: एक ही prompt के लिए sample की गई completions के group में, किसी एक completion का advantage उसका reward घटा group का औसत reward होता है, जिसे group के standard deviation से भाग दिया जाता है, और जो उस completion के हर token पर लगता है।
_बचें_: baseline (baseline सामान्य RL की अवधारणा है जिसका काम group का औसत करता है; GRPO के दायरे में आने के बाद यह workspace ख़ास नाम इस्तेमाल करता है)

**Implicit reward**:
वह reward function जिसे DPO दिखाता है कि वह policy और reference model से गणितीय रूप से तय होता है, उसे निकालने के लिए अलग reward model कभी train किए बिना।
_बचें_: reward model (DPO की पूरी दलील यही है कि उसे अलग reward model नहीं चाहिए; दोनों को मिला देने से वह फ़र्क़ मिट जाता है जो चरण 5 सिखाने के लिए है)

**KL penalty**:
RL objective में जोड़ा गया वह term जो train हो रही policy को एक fixed reference model के output distribution से भटकने पर दंडित करता है, ताकि reward model के विरुद्ध optimization बिगड़ा हुआ text न बनाए।
_बचें_: regularization (सही है पर सामान्य; RLHF के दायरे में आने के बाद ख़ास penalty का नाम लें)

**Loss masking**:
उन tokens पर training loss को शून्य कर देना जिन्हें model को बनाना नहीं सीखना चाहिए, जैसे prompt या system message, ताकि gradient updates सिर्फ़ उन tokens से आएँ जिन्हें model को generate करना है।
_बचें_: prompt masking (masking सिर्फ़ prompt पर ही लागू नहीं होती, multi-turn example के हर non-assistant turn पर भी होती है)

**Preference pair**:
एक ही prompt की दो completions, जिनमें से एक को दूसरे से बेहतर चिह्नित किया गया हो; यह वह इकाई है जिस पर reward modeling और DPO दोनों train होते हैं।
_बचें_: comparison (साहित्य में इसी चीज़ के लिए इस्तेमाल होता है; यह workspace preference pair पर टिका है)

**Reward hacking**:
Policy का ऐसा रास्ता खोज लेना जिससे वह reward model या verifiable reward signal के विरुद्ध अच्छा score करे, बिना वह व्यवहार पैदा किए जिसे मापने के लिए reward बनाया गया था।
_बचें_: gaming, overoptimization (दोनों एक ही विफलता की ओर इशारा करते हैं; यह workspace हर जगह reward hacking इस्तेमाल करता है)

**RLAIF**:
AI feedback से reinforcement learning: preference labels या reward signal जो इंसान के बजाय किसी model ने बनाया हो, और RLHF की जगह या उसके साथ इस्तेमाल हुआ हो।
_बचें_: self-improvement (RLAIF एक ख़ास labeling तरीक़ा है; self-improvement नतीजे के बारे में कहीं ज़्यादा बड़ा और धुँधला दावा है)

**Verifiable reward**:
ऐसा reward signal जिसे कोई deterministic checker निकालता है, जैसे unit test का नतीजा या मेल खाता अंतिम numeric उत्तर, सीखे हुए reward model के बजाय।
_बचें_: ground truth (ground truth वह उत्तर है जिससे मिलान होता है; verifiable reward उस जाँच से निकला signal है)
