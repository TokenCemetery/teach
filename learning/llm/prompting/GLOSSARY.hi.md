---
title: शब्दावली
description: "Prompting के मानक शब्द"
type: glossary
---

# Prompting शब्दावली

LLM फ़ीचर के पीछे के prompts को लिखने, structure करने, version करने, मापने और सुरक्षित करने के मानक शब्द।

## शब्द

**Chain-of-thought**:
Model अपने अंतिम उत्तर से पहले जो intermediate reasoning लिखता है। इसे ऐसे examples से करवाया जाता है जो reasoning दिखाते हैं, या ऐसे instruction से जो इसे माँगता है।
_बचें_: गद्य में CoT (heading या table में ठीक है), thinking (यहाँ यह शब्द reasoning model के built-in चरण के लिए सुरक्षित है)

**Chat template**:
Model-विशिष्ट नियम जो role-tagged messages की सूची को उस एक token sequence में बदलता है जिस पर model को train किया गया था। इसमें वे special tokens भी शामिल हैं जो बताते हैं कि हर role कहाँ शुरू और ख़त्म होता है।
_बचें_: prompt format

**Constrained decoding**:
हर चरण में यह सीमित करना कि model कौन-से tokens generate कर सकता है, ताकि output किसी grammar या schema से मेल खाए, जैसा provider का लागू किया हुआ structured-output फ़ीचर करता है।
_बचें_: grammar sampling

**Delimiter**:
Prompt में वह markup, जैसे XML-style tag या fenced block, जो बताता है कि एक प्रकार का content कहाँ ख़त्म होता है और दूसरा कहाँ शुरू होता है। अक्सर इसका मक़सद data को instructions से अलग रखना होता है।
_बचें_: separator

**Few-shot prompt**:
ऐसा prompt जिसमें असली input से पहले task के worked examples होते हैं, हर example एक input और उसके वांछित output की जोड़ी होता है।
_बचें_: multishot prompt, in-context training

**Indirect prompt injection**:
ऐसा prompt injection जो उस content के ज़रिए आता है जिसे model उपयोगकर्ता की ओर से पढ़ता है, जैसे web page, email या retrieve किया गया document, न कि उस व्यक्ति के टाइप करने से जो model से बात कर रहा है।
_बचें_: second-order injection

**Instruction hierarchy**:
Instructions टकराने पर model को जो क्रम लागू करना सिखाया जाता है: system prompt user turn से ऊपर, और user turn tools या retrieval से लौटे content से ऊपर।
_बचें_: priority order

**Jailbreak**:
ऐसा input जो model से वह करवाने के लिए बनाया गया हो जिसे उसकी safety training मना करती है। यह model की अपनी सीमाओं को निशाना बनाता है, जबकि prompt injection application के instructions को निशाना बनाता है।
_बचें_: prompt injection (इसका निशाना अलग है)

**Lethal trifecta**:
तीन चीज़ों का मेल: private data तक पहुँच, untrusted content का सामना, और data बाहर भेजने का रास्ता। ये तीनों मिलकर prompt injection को exploit करने लायक बना देते हैं। इनमें से कोई एक हटाने से रास्ता बंद हो जाता है।
_बचें_: injection risk (इतना अस्पष्ट कि उस पर कार्रवाई नहीं हो सकती)

**Model snapshot**:
Model का एक तय version, जिसे एक सटीक model ID से नाम दिया जाता है और जिसके weights को provider नहीं बदलता। कोई सुविधाजनक alias समय के साथ नए snapshot की ओर इशारा कर सकता है।
_बचें_: model version (model generation से उलझन होती है)

**Paired comparison**:
दो prompts या models को एक ही inputs पर इस आधार पर तौलना कि किन cases में उनके नतीजे अलग हैं, न कि उनके दो कुल योगों के आधार पर।
_बचें_: A/B score comparison

**Prompt**:
एक call के लिए model को मिलने वाली हर चीज़: system prompt, अब तक की बातचीत का हर message, और डाला गया कोई भी content। chat template इन सबको एक token sequence में render करता है।
_बचें_: query (वह prompt के भीतर उपयोगकर्ता का सवाल है)

**Prompt caching**:
Provider का फ़ीचर जो prompt के prefix की processed state को सहेजता है, ताकि वही सटीक prefix साझा करने वाली बाद की calls उसे दोबारा compute करना छोड़ दें। इससे cost और latency घटती है।
_बचें_: response caching (यह अलग चीज़ है: पूरे उत्तर सहेजना)

**Prompt injection**:
ऐसा input जिससे model उन instructions के अलावा दूसरे instructions मानने लगे जो prompt के लेखक ने चाहे थे।
_बचें_: jailbreak (jailbreak model की safety training को निशाना बनाता है, injection application के instructions को)

**Prompt template**:
Prompt का स्थिर text, जिसमें नाम वाले slots होते हैं। call के समय इन slots में हर request के मान भरे जाते हैं, जैसे उपयोगकर्ता का message या retrieve किया गया document।
_बचें_: prompt string

**Reasoning model**:
ऐसा model जिसे दिखने वाले उत्तर से पहले आंतरिक reasoning चरण पैदा करने के लिए train किया गया है, इसलिए वह बिना कहे ही reasoning करता है।
_बचें_: thinking model

**Regression set**:
Inputs का एक तय सेट, हर एक के output पर एक जाँच के साथ, जिसे prompt में बदलाव तोड़ना नहीं चाहिए। यह ज़्यादातर असली उपयोग में दिखी विफलताओं से बनता है।
_बचें_: test prompts, golden set

**Role**:
बातचीत के हर message पर लगा label, आमतौर पर system, user या assistant, जिसे chat template special tokens में बदलता है। Role एक formatting है जिसे model ने वज़न देना सीखा है, कोई अलग input channel नहीं।
_बचें_: persona (वह इस बात का वर्णन है कि model को किस रूप में काम करना है)

**Self-consistency**:
एक ही prompt के लिए कई chain-of-thought completions sample करना और सबसे आम अंतिम उत्तर चुनना।
_बचें_: ensembling

**Structured output**:
मशीन-पठनीय format में response, आमतौर पर किसी schema से मेल खाता JSON, जिसे कोई व्यक्ति पढ़ने के बजाय कोई program parse करता है।
_बचें_: JSON mode (इसके लिए एक provider का फ़ीचर)

**System prompt**:
System role का वह message जो पूरी बातचीत के लिए model का task, constraints और context तय करता है, और instruction hierarchy में सबसे ऊपर रहता है।
_बचें_: system message, preamble

**Zero-shot prompt**:
ऐसा prompt जो बिना किसी worked example के task बताता है।
_बचें_: plain prompt
