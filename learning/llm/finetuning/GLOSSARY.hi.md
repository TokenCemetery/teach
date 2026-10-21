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

_पाठों के स्थापित करने के साथ जोड़े जाते हैं._
