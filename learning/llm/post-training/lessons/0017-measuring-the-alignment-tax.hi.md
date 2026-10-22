---
title: "17. Alignment Tax को मापना"
description: "Tax हर जगह एक साथ नहीं दिखता, और एक axis पर तो गिरावट की जगह सुधार मापा गया"
type: lesson
---

# पाठ 17. Alignment Tax को मापना

**मिशन से संबंध:** "असली क्षमता-वृद्धि को reward-hacking या judge-bias की उपज से अलग कर सकें" "सफलता कैसी दिखती है" का वह बिंदु है जिसकी सेवा यह चरण करता है। यह पाठ कवर करता है कि alignment tax असल में कैसे मापा जाता है, सिर्फ़ यह नहीं कि वह क्या है; पाठ 18 training ख़त्म होने के बाद reward hacking की पहचान कवर करता है, और पूरी पद्धति के लिए `llm/evals` को सौंप देता है।
**मुख्य स्रोत:** [पेपर: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**पूर्व-आवश्यकताएँ:** [पाठ 16](0016-rlaif-how-well-ai-feedback-actually-matches-human-feedback.md), [Alignment tax](../GLOSSARY.md)

## वार्म-अप

1. ▢ Direct-RLAIF (d-RLAIF) क्या है, और Lee et al. के अनुसार उसका प्रदर्शन canonical RLAIF से कैसा रहा?

<details markdown="1"><summary>जाँचें</summary>

ऐसी तकनीक जो अलग reward model train करना छोड़ देती है, RL के दौरान सीधे किसी तैयार language model से reward score पूछती है। Lee et al. को वह canonical RLAIF से बेहतर प्रदर्शन पाता मिला, सिर्फ़ कम लागत पर तुलनीय प्रदर्शन नहीं।

</details>

2. ▢ Lee et al. के परखे तीन tasks में से किस पर RLAIF ने RLHF को सिर्फ़ बराबरी देने के बजाय पीछे छोड़ा?

<details markdown="1"><summary>जाँचें</summary>

Harmless dialogue generation।

</details>

## यह जानें

### Tax एक संख्या नहीं है; यह अलग-अलग मापों का सेट है

पाठ 1 ने alignment tax को असली, मापी गई लागत के रूप में पेश किया, बिना यह बताए कि वह असल में कैसे मापा जाता है। Ouyang et al. ने ऐसा अपने aligned model को मौजूदा public NLP benchmarks की पूरी कतार पर चलाकर और नतीजे की तुलना unaligned base model से, हर benchmark पर अलग-अलग, करके किया, सबको एक अकेले tax आँकड़े में समेटने के बजाय। वे कुछ benchmarks पर ख़ास गिरावटें रिपोर्ट करते हैं, ख़ासकर SQuAD, DROP, HellaSwag और WMT 2015 फ़्रेंच-से-अंग्रेज़ी translation, और, अहम बात, दो और जिन्हें उन्होंने जाँचा, Winogender और CrowSPairs (bias-संबंधी benchmarks), पर **कोई महत्वपूर्ण बदलाव नहीं**। Tax कुछ axes पर दिखा और कुछ पर नहीं; उसे एक एकसमान लागत मान लेने से यह पैटर्न छिप जाता।

### Alignment ने मापा हुआ फ़ायदा भी दिया, सिर्फ़ लागत नहीं

उसी evaluation कतार में एक axis ऐसा भी था जहाँ alignment training लागत के बजाय सुधार के रूप में मापी गई: RealToxicityPrompts dataset इस्तेमाल करके Ouyang et al. रिपोर्ट करते हैं कि जब respectful होने को कहा गया तो InstructGPT ने GPT-3 से लगभग 25% कम toxic outputs generate किए। Alignment training ने model की मापी गई क्षमताओं के साथ क्या किया, इसके निष्पक्ष हिसाब में गिरावटों के साथ ऐसे नतीजे को भी शामिल करना पड़ता है; सिर्फ़ tax रिपोर्ट करना और वहाँ को अनदेखा करना जहाँ उसी training ने मदद की, उतना ही भ्रामक होगा जितना यह रिपोर्ट करना कि कोई tax था ही नहीं।

### इलाज, और उसकी क्या क़ीमत नहीं पड़ी

पाठ 6 ने तंत्र का नाम पहले ही ले लिया था: PPO updates को उन updates के साथ मिलाना जो मूल pretraining distribution की likelihood बढ़ाते हैं (PPO-ptx) ने SQuAD, DROP, HellaSwag और WMT पर मापी गई गिरावटों को बहुत घटा दिया। Ouyang et al. साफ़ कहते हैं कि यह वापसी **labeler preference scores से समझौता किए बिना** हुई, यानी इलाज ने alignment के फ़ायदे बस खोए हुए benchmark प्रदर्शन के बदले वापस नहीं दे दिए; दोनों को अलग-अलग मापा गया, और इलाज ने एक को सुधारा बिना दूसरे को दिखने लायक़ नुक़सान पहुँचाए।

### अलग, नक़ल करने में कठिन generalization जाँच: held-out labelers

Benchmark गिरावटों से आगे, Ouyang et al. ऐसी जाँच चलाते हैं जो अलग सवाल पर है: क्या model का aligned व्यवहार उन ख़ास लोगों से आगे generalize होता है जिनकी पसंद ने उसे ढाला, या उसने बस अपने training data के ख़ास labelers को ख़ुश करना सीखा? वे इसे **held-out labelers** से परखते हैं, ऐसे लोग जिन्होंने model को train करने में इस्तेमाल हुआ कोई data दिया ही नहीं, और पाते हैं कि इन held-out labelers ने भी InstructGPT के outputs को तरजीह दी। यह वही बुनियादी विचार है जिसके लिए `llm/pretraining` और `llm/evals` दोनों held-out data इस्तेमाल करते हैं: कोई नतीजा तभी वही मतलब रखता है जो वह कहता है जब उसे उन्हीं ख़ास data (या लोगों) पर fit होकर, जिन्होंने training को ढाला, पैदा नहीं किया जा सकता था।

## अभ्यास

1. ▢ Ouyang et al. SQuAD, DROP, HellaSwag और WMT translation पर गिरावटें रिपोर्ट करते हैं, पर Winogender और CrowSPairs पर कोई महत्वपूर्ण बदलाव नहीं। Alignment tax को एक कुल संख्या मानने से इस नतीजे के बारे में क्या छिप जाता?

<details markdown="1"><summary>जाँचें</summary>

यह कि tax एकसमान लागू नहीं हुआ; वह कुछ benchmarks पर साफ़ दिखा और कुछ पर बिल्कुल नहीं। एक अकेली समेटी हुई संख्या इस असमान पैटर्न को ऐसे दिखाती जैसे वह हर क्षमता पर एक-सी लागत हो।

</details>

2. ▢ Alignment tax के निष्पक्ष हिसाब के लिए toxic outputs में 25% की कमी क्यों मायने रखती है, सिर्फ़ SQuAD/DROP/HellaSwag/WMT की गिरावटें रिपोर्ट करने के बजाय?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि इस axis पर alignment training से मापने लायक़ फ़ायदा हुआ, कोई लागत नहीं; सिर्फ़ गिरावटें रिपोर्ट करना और इस नतीजे को छोड़ देना training ने असल में क्या किया उसे कम आँकता, उसी तरह जैसे कोई tax न रिपोर्ट करना उसे ज़्यादा आँकता।

</details>

3. ▢ Ouyang et al. ने alignment tax के लिए PPO-ptx के इलाज के बारे में, benchmark गिरावटें घटाने से आगे, ख़ास तौर पर क्या सत्यापित किया?

<details markdown="1"><summary>जाँचें</summary>

कि उसने यह labeler preference scores से समझौता किए बिना किया; benchmark प्रदर्शन की वापसी उन alignment फ़ायदों को लौटाकर नहीं चुकाई गई जिनके ऊपर PPO-ptx जोड़ा गया था।

</details>

4. ▢ Held-out labelers से परखना, यानी ऐसे लोग जिन्होंने training data नहीं दिया, benchmark-गिरावट के मापों से अलग सवाल का जवाब क्यों देता है?

<details markdown="1"><summary>जाँचें</summary>

Benchmark गिरावटें मापती हैं कि क्या ख़ास क्षमताएँ बुरी हुईं। Held-out labelers परखते हैं कि क्या model का aligned व्यवहार असल में उन ख़ास लोगों से आगे की पसंद तक generalize होता है जिन्होंने training को ढाला, बजाय इसके कि वह उसी ख़ास समूह पर क़रीब से fit हुआ हो; जो नतीजा सिर्फ़ मूल labelers के लिए टिकता, वह उसी generalization दावे को सहारा नहीं देता।

</details>

## असली दुनिया का अभ्यास

- [ ] कोई प्रकाशित post-training technical report खोजें और जाँचें कि वह benchmark कतार पर गिरावटें और सुधार दोनों रिपोर्ट करती है, या सिर्फ़ एक दिशा। नोट करें कि किन benchmarks पर, अगर किसी पर, कोई महत्वपूर्ण बदलाव नहीं दिखा।
- [ ] InstructGPT पेपर (ऊपर link है) में held-out-labeler प्रयोग का वर्णन करने वाला अनुच्छेद पढ़ें, और एक वाक्य लिखें कि कौन-सा नतीजा आपको शक में डालता कि model की alignment अपने training labelers से आगे generalize हुई।
- [ ] कल: आगे देखे बिना पाठ 18 के लिए एक वाक्य की भविष्यवाणी लिखें: यह देखते हुए कि reward model या AI judge को चकमा दिया जा सकता है (पाठ 5), training ख़त्म होने के बाद *तैयार* aligned model का मूल्यांकन करने के लिए किस चीज़ की जाँच करनी पड़ेगी जिसे training के समय की train-PM-बनाम-test-PM तुलना नहीं जाँच सकती थी?

## आगे बढ़ने के लिए

- [पेपर: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
