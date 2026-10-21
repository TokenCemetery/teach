---
title: "शब्दावली"
description: "LLMs के knowledge distillation के मानक शब्द"
type: glossary
---

# Distillation शब्दावली

बड़े model के outputs से छोटा model train करने के मानक शब्द: वे losses और data जो signal ढोते हैं, और नतीजे को कैसे आँका जाता है। इस workspace में "distillation" का मतलब हमेशा teacher model से student model तक knowledge distillation है; इसका मतलब कभी dataset distillation या prompt को distil करना नहीं है।

## शब्द

**Beam search**:
Decoding का ऐसा तरीक़ा जो हर चरण पर सबसे ऊँचे score वाले कुछ आंशिक sequences रखता है और सबसे अच्छा पूरा sequence लौटाता है, सबसे संभावित sequence के सन्निकटन के रूप में।
_बचें_: greedy search (वह beam size 1 है), best-first decoding

**Capacity gap**:
Student की गुणवत्ता में वह गिरावट जो तब आ सकती है जब teacher, student से बहुत बड़ा हो, जिससे ज़्यादा मज़बूत teacher कमज़ोर teacher के मुक़ाबले ख़राब student बनाता है।
_बचें_: teacher too smart, size mismatch

**Combined loss**:
ऐसा distillation loss जो hard labels के विरुद्ध cross-entropy में teacher के soft targets से divergence जोड़ता है, एक मिश्रण गुणांक से भारित करके।
_बचें_: hybrid loss, dual loss

**Cross-tokenizer distillation**:
ऐसे teacher और student के बीच logit distillation जिनकी vocabularies अलग हैं, साझा token index के बिना उनके distributions को align या तुलना करके किया जाता है।
_बचें_: tokenizer-free distillation, vocabulary transfer

**Decontamination**:
Training data से वे examples हटाना जो किसी evaluation set से मेल खाते हों या उसके बहुत क़रीब हों, ताकि benchmark score याद किए हुए items को न मापे।
_बचें_: cleaning (बहुत व्यापक), deduplication (वह training set के भीतर दोहराव हटाता है)

**Distillation**:
Student model को teacher model का व्यवहार दोहराने के लिए train करना, teacher के output distributions या generate किए गए text को training signal बनाकर।
_बचें_: compression (बहुत व्यापक), model copying

**Distillation scaling law**:
Busbridge et al. का एक fitted संबंध, जो student की cross-entropy का अनुमान उसके आकार, distillation tokens की संख्या और teacher की cross-entropy से लगाता है।
_बचें_: distillation law, KD scaling

**Exposure bias**:
उन prefixes पर training जो किसी और ने लिखे हों और उन prefixes से generate करने के बीच का बेमेल, जो model ने ख़ुद लिखे हों, जिससे उसकी अपनी शुरुआती ग़लतियाँ उसे ऐसी स्थितियों में पहुँचा देती हैं जिन पर उसने कभी train नहीं किया।
_बचें_: train-test mismatch (बहुत व्यापक), drift

**Fidelity**:
Student की predictions उसके teacher की predictions से कितनी मिलती हैं, उन्हीं inputs पर मापा हुआ, इसके विपरीत कि दोनों task पर कितना अच्छा करते हैं।
_बचें_: accuracy, faithfulness

**Forward KL**:
Divergence KL(teacher ‖ student), जो teacher के distribution के तहत औसत लिया जाता है। यह student को तब दंडित करता है जब वह वहाँ कम probability रखे जहाँ teacher ज़्यादा रखता है, और इसलिए उसे हर mode को कवर करने की ओर धकेलता है।
_बचें_: दिशा का नाम लिए बिना mode-covering KL, सादा KL

**Generalized knowledge distillation**:
Agarwal et al. की on-policy विधि, जो student को तय और student-generated sequences के मिश्रण पर train करती है, और चुने हुए divergence से teacher के विरुद्ध हर token को अलग-अलग score करती है। संक्षेप में GKD।
_बचें_: generalised KD, generic distillation

**Hard label**:
Training target के रूप में इस्तेमाल होने वाला अकेला सही class या token, जिसकी पूरी probability एक ही उत्तर पर होती है।
_बचें_: ground truth (वह teacher का argmax भी हो सकता है), संदर्भ के बिना one-hot target

**Imitation gap**:
Student कितना अपने teacher जैसा सुनाई देता है और teacher की क्षमता का कितना हिस्सा उसमें सचमुच है, इन दोनों के बीच की दूरी। सीमित बजट पर नक़ल style पर क्षमता की तुलना में कहीं तेज़ी से यह दूरी पाटती है।
_बचें_: false promise (यह पेपर का शीर्षक है, शब्द नहीं), style transfer

**KL divergence**:
एक ही tokens पर दो distributions P और Q के लिए, tokens पर P log(P / Q) का योग: यह नापता है कि Q, P से कितना दूर है, और यह सममित नहीं है। Distillation में इसकी दो दिशाएँ forward KL और reverse KL हैं।
_बचें_: KL distance, शब्द को परिचित कराए बिना relative entropy

**Logit**:
किसी class या token के लिए model का कच्चा, बिना normalise किया हुआ score, उससे पहले कि softmax scores को probabilities में बदले।
_बचें_: score (अस्पष्ट), log-probability (वह softmax के बाद की चीज़ है)

**Logit distillation**:
ऐसा distillation जिसका training signal हर position पर teacher का पूरा output distribution होता है, जिसके लिए teacher के logits तक पहुँच और साझा vocabulary चाहिए।
_बचें_: white-box distillation (स्वीकृत पर्याय, पर एक ही शब्द रखें), soft distillation

**Off-policy distillation**:
उन sequences पर distillation जो student ने generate नहीं किए: मानव data या teacher के अपने outputs, जो training से पहले तय हों।
_बचें_: offline distillation, supervised distillation

**On-policy distillation**:
उन sequences पर distillation जो student training के दौरान ख़ुद generate करता है, और teacher student के चुने हर token को score करता है, ताकि student अपनी ही ग़लतियों पर train हो।
_बचें_: online distillation (यह उन teachers के लिए भी इस्तेमाल होता है जो student के साथ-साथ train होते हैं), self-distillation

**Rationale**:
वह intermediate reasoning जो teacher अपने उत्तर से पहले या उसके साथ लिखता है, और जिसे अतिरिक्त training target की तरह इस्तेमाल किया जाता है ताकि student सीखे कि उत्तर तक कैसे पहुँचा गया।
_बचें_: explanation (गद्य में ठीक है, शब्द के रूप में नहीं), chain of thought (वह prompting तकनीक जो इसे पैदा करती है)

**Rejection sampling**:
हर prompt के लिए model से कई candidate outputs निकालना और सिर्फ़ वे रखना जो किसी जाँच को पास करें, जैसे सही अंतिम उत्तर।
_बचें_: filtering (बहुत व्यापक), best-of-n (वह जाँच से छाँटने के बजाय एक विजेता रखता है)

**Reverse KL**:
Divergence KL(student ‖ teacher), जो student के distribution के तहत औसत लिया जाता है। यह student को तब दंडित करता है जब वह वहाँ probability रखे जहाँ teacher कम रखता है, और इसलिए उसे एक mode पर टिकने की ओर धकेलता है।
_बचें_: दिशा का नाम लिए बिना mode-seeking KL, backward KL

**Sequence-level distillation**:
ऐसा distillation जिसमें student को teacher के per-token distributions के बजाय, teacher द्वारा decode किए गए पूरे sequences पर साधारण cross-entropy से train किया जाता है।
_बचें_: hard distillation, black-box distillation (उसमें generated-data distillation भी आता है)

**Soft targets**:
Classes या tokens पर teacher का पूरा probability distribution, जिसे hard label की जगह या उसके साथ training target के रूप में इस्तेमाल किया जाता है।
_बचें_: soft labels (स्वीकृत पर्याय, पर एक ही शब्द रखें), dark knowledge (वह जानकारी जो वे ढोते हैं, targets नहीं)

**Student**:
Distillation में जिस model को train किया जा रहा है, जो आमतौर पर teacher से छोटा या चलाने में सस्ता होता है।
_बचें_: training पूरी होने से पहले distilled model, child model

**Subliminal learning**:
Student का अपने teacher की कोई विशेषता ऐसे data से पा लेना जिसका उस विशेषता से अर्थ के स्तर पर कोई संबंध नहीं है। Cloud et al. ने इसे तब देखा जब दोनों का base model एक ही था।
_बचें_: hidden distillation, data poisoning (वह जानबूझकर किया जाता है)

**Supervised baseline**:
Student के आकार का ऐसा model जो distillation के बिना, उसी data या उसी compute पर train हुआ हो, और जिसे तुलना के रूप में इस्तेमाल किया जाता है जो दिखाए कि नतीजा distillation की वजह से आया या नहीं।
_बचें_: control model (बहुत व्यापक), plain model

**Synthetic data**:
ऐसे training examples जो लोगों के लिखने के बजाय किसी model ने generate किए हों। इस workspace में इसका मतलब है student के लिए teacher द्वारा generate किया गया data।
_बचें_: fake data, augmented data (augmentation मौजूदा examples को बदलता है)

**Teacher**:
वह model जिसके outputs distillation में training signal होते हैं। यह training के दौरान तय (fixed) रहता है और आमतौर पर student से बड़ा या ज़्यादा सक्षम होता है।
_बचें_: oracle, parent model

**Teacher assistant**:
बीच के आकार का model जो teacher से distil किया गया हो और फिर किसी छोटे student के लिए teacher के रूप में इस्तेमाल हो, ताकि capacity gap को पाटा जा सके।
_बचें_: शब्द को परिचित कराए बिना intermediate teacher, TA model

**Teacher forcing**:
Model को उसके अपने पिछले outputs के बजाय कोई तय prefix खिलाना, जिससे एक forward pass में sequence के हर position पर next-token distribution मिल जाता है।
_बचें_: teacher-forced decoding, free running (वह इसका उलटा है)

**Temperature**:
Softmax से पहले logits पर लगाया जाने वाला भाजक T। T का 1 से ऊपर होना distribution को चपटा करता है और कम संभावित उत्तरों की probabilities बढ़ाता है ताकि student उनसे सीख सके। यह classifier-युग का default था; इस workspace के स्रोतों में LLM distillation के runs में T = 1 सबसे अच्छा निकला।
_बचें_: sampling temperature (वही ऑपरेशन, पर मक़सद अलग), softness

**Token-level distillation**:
Sequence के हर position पर लगाया गया logit distillation, जो teacher और student के next-token distributions के बीच divergence को कम करता है।
_बचें_: word-level distillation (मूल पेपर का नाम), per-token KD

**Top-1 agreement**:
Inputs का वह हिस्सा जिन पर student का सबसे ऊँची probability वाला उत्तर उसके teacher के उत्तर जैसा ही हो। यह Stanton et al. के दो fidelity metrics में से एक है।
_बचें_: accuracy (वह सही उत्तर के विरुद्ध होती है), match rate

**Top-k logits**:
किसी position पर teacher के output distribution की k सबसे बड़ी प्रविष्टियाँ, जो भंडारण घटाने के लिए पूरी vocabulary पंक्ति की जगह अपने token indices के साथ रखी जाती हैं।
_बचें_: sparse logits, यह बताए बिना कि छोड़ा गया द्रव्यमान (mass) कहाँ जाता है, truncated softmax
