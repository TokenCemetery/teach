---
title: "Held-Out Data और Contamination"
description: "Eval सेट के लिए train/test split का अनुशासन, contamination के दो रास्ते, हर एक को कैसे पकड़ें, और उनका सामना करने वाला custom सेट कैसे डिज़ाइन करें"
type: reference
---

# Held-Out Data और Contamination

चरण 1, खोजने के लिए संक्षिप्त। [पाठ 1](../lessons/0001-held-out-and-contamination.md) contamination के दो रास्तों और उन्हें पकड़ने के guided-instruction test को कवर करता है; [पाठ 2](../lessons/0002-designing-contamination-resistance.md) कवर करता है कि custom eval सेट को शुरू से ही contamination का सामना करने लायक कैसे डिज़ाइन करें। यह शीट परिभाषाएँ, रास्ते और रोकथाम के औज़ार साथ-साथ देती है।

## "Held out" होने के लिए क्या चाहिए

Eval सेट held out तब है जब परखे जा रहे model ने training या fine-tuning के दौरान वही सटीक examples, या उनके क़रीबी paraphrases, कभी नहीं देखे। यही अकेली ख़ूबी किसी अच्छे score का मतलब "यह generalize करता है" बनाती है, "यह रटा गया था" नहीं। किसी score को प्रमाण के रूप में उद्धृत करने से पहले जवाब दें: *model यह रटकर, या ठीक इसी सेट के विरुद्ध tune होकर सही क्यों नहीं कर सकता था?* अगर कोई जवाब नहीं है, तो संख्या eval का वर्णन करती है, model का नहीं।

## Contamination के दो रास्ते

| रास्ता | क्या होता है | शाब्दिक रिसाव? | सुधार |
|---|---|---|---|
| Pretraining में समा जाना | किसी के उस पर eval बनाने से पहले benchmark web-crawl training data में खींच लिया जाता है | हाँ | ऐसा data चुनें या बनाएँ जिसके pretraining corpus में आने की संभावना कम हो, या उसकी मौजूदगी की जाँच करें |
| बार-बार का overfitting | Model या prompt को tune करते समय वही eval सेट बार-बार चलाया जाता है, जिससे system धीरे-धीरे उन्हीं ख़ास examples को पास करने के आकार में ढल जाता है | नहीं | सेट को ताज़ा करें, या उसका एक अछूता हिस्सा अलग रखें |

दोनों एक ही लक्षण पैदा करते हैं: अच्छी दिखने वाली संख्या जो असली दुनिया के व्यवहार की भविष्यवाणी नहीं करती। सुधार अलग हैं क्योंकि कारण अलग हैं; एक को दूसरे का विकल्प मान लेने से बिना इलाज वाला रास्ता खुला रह जाता है।

## Pretraining में समाने को पकड़ना: guided-instruction test

Model को benchmark instance का पहला हिस्सा दें और उससे बाक़ी हिस्सा ज्यों का त्यों पूरा करने को कहें। ऐसे ब्योरे दोहराना जिन्हें कोई समझदार अनुमान नहीं पा सकता, यानी सटीक शब्दावली, कोई असामान्य संख्या, कोई दुर्लभ व्यक्तिवाचक संज्ञा, इस बात का पक्का प्रमाण है कि वह instance उसके training data में था (Golchin and Surdeanu, 2023)। यह सिर्फ़ समा जाने की जाँच करता है; बार-बार के overfitting के बारे में कुछ नहीं कहता, जो ऐसा कोई निशान नहीं छोड़ता।

## Custom सेट बनाते समय contamination रोकना

| Technique | क्या करती है | कब लागू होती है | सीमाएँ |
|---|---|---|---|
| Training cutoff के बाद की तारीख़ | Eval data को model के बताए training cutoff के बाद बनी सामग्री से लें | सटीक, सत्यापित cutoff तारीख़ चाहिए, marketing का दावा नहीं | सिर्फ़ समा जाने से बचाती है; पुराना पड़ चुका eval सेट अब भी बार-बार के overfitting का जोखिम रखता है |
| Canary string (BIG-bench परंपरा) | अनोखा चिह्न-वाक्यांश डालें जो किसी भी crawler से चिह्नित सामग्री को बाहर रखने को कहता है | कोई भी प्रकाशित सेट | अनुरोध है, लागू करवाने की व्यवस्था नहीं; crawler के सहयोग पर निर्भर |
| n-gram overlap जाँच | Eval data और किसी ज्ञात corpus के बीच सीधा overlap मापें | सिर्फ़ तब जब pretraining corpus ज्ञात और उपलब्ध हो | ऐसे closed model के लिए बेकार जिसका training data बताया नहीं गया |
| सेट को अप्रकाशित रखें | उसे कभी सार्वजनिक रूप से पोस्ट न करें | हमेशा उपलब्ध | सबसे मज़बूत रोकथाम, पर reproducibility और बाहरी जाँच की क़ीमत पर |

पहली तीन किसी चीज़ पर निर्भर हैं (सटीक cutoff, crawler का सहयोग, corpus तक पहुँच); सेट को निजी रखना अकेली technique है जिसकी कोई पूर्व-शर्त नहीं, इसीलिए जब बाक़ी लागू न हों तब वही आख़िरी सहारा है।

## Score पर भरोसा करने से पहले

- Eval सेट की contamination वाली कहानी बताई गई है, मानी नहीं गई: कौन-सा रास्ता जाँचा गया, और कैसे।
- उधार लिया गया public benchmark guided-instruction तरीक़े से परखा गया है, या दर्ज कारण मौजूद है कि वह जोखिम कम क्यों है।
- Custom eval सेट बताता है कि उस पर कौन-सी रोकथाम की technique(s) लागू हैं, और उनकी सीमाएँ पता हैं, सिर्फ़ उनकी मौजूदगी नहीं।
- जो eval सेट महीनों की tuning में दोबारा इस्तेमाल हुआ है उसे ताज़ा किया गया है, या अलग रखा हुआ ऐसा हिस्सा मौजूद है जिसे छुआ नहीं गया।

## स्रोत

- [दस्तावेज़: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [पेपर: "Time Travel in LLMs: Tracing Data Contamination in Large Language Models", Golchin and Surdeanu, 2023](https://arxiv.org/abs/2308.08493)
- [पेपर: "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models" (BIG-bench), Srivastava et al., 2022](https://arxiv.org/abs/2206.04615)
- [संसाधन](../RESOURCES.md)
