---
title: "12. Verifiable Rewards: जब Checker, Reward Model की जगह ले लेता है"
description: "Train किया हुआ reward model इस बात का अंदाज़ा है कि इंसान को क्या पसंद आएगा; unit test या मेल खाता उत्तर अंदाज़ा बिल्कुल नहीं है"
type: lesson
---

# पाठ 12. Verifiable Rewards: जब Checker, Reward Model की जगह ले लेता है

**मिशन से संबंध:** "GRPO में group-relative advantage समझाएँ, और बताएँ कि verifiable reward (unit test, जाँचा हुआ गणित का उत्तर) से RL training किसे निशाना बना सकती है, यह कैसे बदल जाता है" "सफलता कैसी दिखती है" का पाँचवाँ बिंदु है, और यह पाठ उसे पूरा करता है।
**मुख्य स्रोत:** [पेपर: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
**पूर्व-आवश्यकताएँ:** [पाठ 11](0011-grpo-group-relative-advantage-instead-of-a-value-function.md), [Verifiable reward](../GLOSSARY.md)

## वार्म-अप

1. ▢ एक ही सवाल के 4 sample किए outputs को rewards `{2, 4, 6, 8}` मिलते हैं। किन outputs को धनात्मक group-relative advantage मिलता है, और किन्हें ऋणात्मक?

<details markdown="1"><summary>जाँचें</summary>

औसत 5 है; 6 और 8 score करने वाले outputs उससे ऊपर हैं और उन्हें धनात्मक advantage मिलता है, 2 और 4 score करने वाले outputs उससे नीचे हैं और उन्हें ऋणात्मक advantage मिलता है।

</details>

2. ▢ Shao et al. group-relative तुलना को reward models के साथ ख़ास तौर पर फ़िट क्यों बताते हैं?

<details markdown="1"><summary>जाँचें</summary>

Reward models आम तौर पर एक ही सवाल के outputs की आपसी तुलनाओं पर ही train होते हैं, इसलिए एक सवाल के कई outputs को score करना और उनकी तुलना एक-दूसरे से करना reward model से उसी तरह का सापेक्ष फ़ैसला करवाना है जो करना उसे असल में सिखाया गया था।

</details>

## यह जानें

### GRPO को reward से असल में क्या चाहिए

पाठ 11 के group-relative advantage में कुछ भी यह नहीं माँगता कि हर sample किए output का score ख़ास तौर पर train किए reward model से ही आए। Group-normalization के formula, `A_i = (r_i - mean(r)) / std(r)`, को बस हर sample किए output के लिए एक संख्या चाहिए, `r_1` से `r_G` तक, जो दर्शाती हो कि हर एक कितना अच्छा था। Train किया reward model उस संख्या को पैदा करने का एक तरीक़ा है, वही जो Shao et al. की अपनी GRPO training में है। यह अकेला तरीक़ा नहीं है।

### Verifiable reward क्या है

**Verifiable reward** ऐसा reward signal है जिसे सीखे हुए model के बजाय कोई deterministic checker पैदा करता है: generate किया गया code किसी तय unit test को पास करता है या नहीं, गणित की समस्या का अंतिम numeric उत्तर ज्ञात सही उत्तर से ठीक-ठीक मेल खाता है या नहीं, generate किया गया proof या program कोई formal जाँच पूरी करता है या नहीं। Verifiable reward निकालने में इस बारे में कोई अंदाज़ा लगाना शामिल नहीं कि इंसान क्या पसंद करता; यह output के बारे में सीधा, जाँचा जा सकने वाला तथ्य है, हर बार एक ही तरह निकाला जाता है, और output तथा उसके score के बीच पसंद का कोई model बिल्कुल खड़ा नहीं होता।

### यह क्यों बदल देता है कि RL training किसे निशाना बना सकती है

Train किया reward model, चाहे जितना अच्छा train हुआ हो, फिर भी एक पसंद के फ़ैसले को fit कर रहा है: पाठ 5 ने सीधे कवर किया कि policy उसके विरुद्ध अच्छा score पाने के रास्ते कैसे खोज सकती है, बिना वह व्यवहार पैदा किए जिसे पुरस्कृत करने के लिए वह बना था। Verifiable reward में इस आकार की कोई समान विफलता नहीं है: unit test या तो पास होता है या नहीं, और policy के सीखकर फ़ायदा उठाने के लिए कोई reward-model-विशेष सनक नहीं है, क्योंकि फ़ैसले की जगह खड़ा कोई सीखा हुआ model है ही नहीं। इससे RL training के लिए ऐसे लक्ष्य खुल जाते हैं जिन तक अकेली human preference से पहुँचना कठिन था: policy को, sample किए हर group के साथ, ऐसे outputs की ओर धकेला जा सकता है जो गणित और code जैसे tasks पर ज़्यादा बार ठीक-ठीक, जाँचने लायक़ रूप से सही हों, न कि सिर्फ़ ज़्यादा बार किसी judge (इंसान या model) की व्यक्तिपरक पसंद के हों।

### यह क्या नहीं बदलता

Verifiable reward हर लिहाज़ से train किए reward model पर मुफ़्त सुधार नहीं है; यह सिर्फ़ वहाँ लागू होता है जहाँ शुद्धता की जाँच सचमुच मौजूद हो। Post-training जिस व्यवहार को ढालने के लिए है, उसका बहुत-सा हिस्सा (helpfulness, लहजा, safety, खुले सिरे की लेखन गुणवत्ता) ऐसा है जिसमें कोई deterministic checker इंसान या model की पसंद के फ़ैसले की जगह नहीं ले सकता; "यह जवाब उचित रूप से सहानुभूतिपूर्ण था" के लिए कोई unit test नहीं है। Verifiable rewards ख़ास तौर पर उन tasks में फ़िट बैठते हैं जहाँ शुद्धता पहले से जाँची जा सकती है, इसीलिए गणित और code वे क्षेत्र हैं जिनके इर्द-गिर्द यह जोड़ी बनी है, बाक़ी हर जगह preference-आधारित reward modeling का सामान्य विकल्प नहीं।

## अभ्यास

1. ▢ एक टीम GRPO से algebra के शब्द-समस्याएँ हल करने के लिए policy train करना चाहती है। समाधानों के बीच human preferences पर reward model train करने के बजाय वे इसकी जगह क्या इस्तेमाल कर सकते हैं, और वह पाठ 5 में बताए reward-hacking के जोखिम से क्यों बचेगा?

<details markdown="1"><summary>जाँचें</summary>

Verifiable reward: यह जाँचना कि policy का अंतिम numeric उत्तर ज्ञात सही उत्तर से ठीक-ठीक मेल खाता है या नहीं। यह reward-model वाले अर्थ में reward hacking से बचता है क्योंकि फ़ायदा उठाने के लिए किसी सीखे हुए model की सनकें नहीं हैं; जाँच output के बारे में सीधा, deterministic तथ्य है, न कि train किया हुआ फ़ैसला जिसे policy चकमा देना सीख ले।

</details>

2. ▢ Policy को ज़्यादा सहानुभूतिपूर्ण customer-support जवाब लिखना सिखाने के लिए verifiable reward ख़राब फ़िट क्यों होगा?

    - a) Verifiable rewards सिर्फ़ numeric outputs के लिए निकाले जा सकते हैं
    - b) "यह जवाब उचित रूप से सहानुभूतिपूर्ण था" के लिए कोई deterministic checker नहीं है; उस तरह की शुद्धता ऐसी विशेषता नहीं जिसे checker परख सके
    - c) Verifiable rewards को समझने के लिए हमेशा अलग reward model चाहिए
    - d) GRPO को verifiable rewards के साथ इस्तेमाल ही नहीं किया जा सकता

<details markdown="1"><summary>जाँचें</summary>

**b)** असली सीमा है: verifiable rewards उन tasks में फ़िट बैठते हैं जहाँ शुद्धता पहले से जाँची जा सकती है, और सहानुभूतिपूर्ण लहजे के लिए ऐसी कोई deterministic जाँच नहीं है। (a) बहुत संकरा है; code की शुद्धता ग़ैर-numeric उदाहरण है जो फिर भी सत्यापित होता है। (c) verifiable reward के पूरे मक़सद का उलटा है, जिसे कोई reward model चाहिए ही नहीं। (d) ग़लत है; GRPO का group-normalization तंत्र किसी भी प्रति-output score के साथ काम करता है, चाहे वह verifiable हो या model से बना।

</details>

3. ▢ क्या verifiable reward इस्तेमाल करने से पाठ 11 के group-relative advantage की गणना के तरीक़े में कुछ बदलता है?

<details markdown="1"><summary>जाँचें</summary>

नहीं। वही normalization, group का औसत घटाना और group के standard deviation से भाग देना, लागू होता है चाहे अंतर्निहित प्रति-output score, `r_i`, train किए reward model से आया हो या deterministic checker से। बदलता सिर्फ़ यह है कि वह score कहाँ से आता है, यह नहीं कि GRPO उसके साथ क्या करता है।

</details>

## असली दुनिया का अभ्यास

- [ ] RL-for-reasoning की कोई प्रकाशित training setup खोजें (पेपर, technical report या open training script) और पहचानें कि उसका verifiable reward ठीक क्या जाँचता है: exact-match उत्तर, unit test suite, formal proof checker, या कुछ और।
- [ ] एक ऐसा task चुनें जो आपको verifiable rewards के लिए वाजिब लगे (कोई coding task, गणित की समस्याओं का सेट) और एक जो अवाजिब लगे (खुले सिरे का लेखन या बातचीत वाला task), और एक-एक वाक्य लिखें कि deterministic checker क्या परख पाएगा या नहीं परख पाएगा।
- [ ] कल: आगे देखे बिना चरण 7 के लिए एक वाक्य की भविष्यवाणी लिखें: अगर verifiable rewards RL training को policy को ज़्यादा बार ठीक-ठीक सही होने की ओर धकेलने देते हैं, तो इस तरह गणित और code की समस्याओं पर भारी training से सिर्फ़ ज़्यादा उत्तर सही होने से आगे, model के किस नए व्यवहार के उभरने की उम्मीद करेंगे?

## आगे बढ़ने के लिए

- [पेपर: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
- [संसाधन](../RESOURCES.md)

---

चरण 6 ने तंत्र (group-relative advantage) और वह reward कवर किया जो उसके साथ ख़ास तौर पर जोड़ी बनाता है (verifiable जाँचें)। चरण 7 बताता है कि जब इस जोड़ी को model train करने के मुख्य तरीक़े के रूप में बड़े पैमाने पर चलाया जाता है तो क्या होता है: reasoning models, और पैमाने पर verifiable rewards पर training असल में क्या पैदा करती है।

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
