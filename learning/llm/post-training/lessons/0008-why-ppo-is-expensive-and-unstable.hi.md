---
title: "8. PPO महँगा और अस्थिर क्यों है"
description: "एक नहीं, चार models को एक साथ memory में समाना पड़ता है, और जो दो सबसे बुरी तरह scale होते हैं वे ठीक वही हैं जो RLHF जोड़ता है"
type: lesson
---

# पाठ 8. PPO महँगा और अस्थिर क्यों है

**मिशन से संबंध:** RLHF objective और उसके clipping तंत्र को निकालना (पाठ 6 और 7) समझाता है कि PPO क्या optimize करता है; यह पाठ समझाता है कि उसे चलाने में असल में कितना ख़र्च आता है, और इसी से DPO (चरण 5) को विकल्प के रूप में सोचना सार्थक बनता है।
**मुख्य स्रोत:** [पेपर: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**पूर्व-आवश्यकताएँ:** [पाठ 7](0007-ppo-why-the-update-gets-clipped.md)

## वार्म-अप

1. ▢ PPO नई और पुरानी policy के बीच probability ratio को clip क्यों करता है, surrogate objective को असीमित बढ़ने देने के बजाय?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि एक sample किए batch से मिला बड़ा अनुमानित advantage इस बात का भरोसेमंद सबूत नहीं है कि उतना ही बड़ा policy update सुरक्षित है; clipping सीमित करती है कि एक update उसके जवाब में policy को कितना हिला सकता है, और विनाशकारी रूप से बड़े क़दम को रोकती है।

</details>

2. ▢ KL penalty (पाठ 6) और PPO की प्रति-step clipping (पाठ 7) के दायरे में क्या फ़र्क़ है?

<details markdown="1"><summary>जाँचें</summary>

KL penalty सीमित करती है कि पूरे training run में policy तय SFT reference model से कितना भटकती है। Clipping सीमित करती है कि कोई एक optimization step उस step से ठीक पहले की policy की अपनी स्थिति के सापेक्ष कितना बड़ा हो सकता है। कोई एक दूसरी की जगह नहीं ले सकती।

</details>

## यह जानें

### चार models, एक नहीं

PPO के ज़रिए RLHF में एक model train नहीं होता; उसमें एक साथ कई models मौजूद चाहिए, हर एक अलग काम करता है: train हो रही **policy** (SFT model से initialize की गई); **SFT model** की एक frozen copy, जो सिर्फ़ KL penalty (पाठ 6) निकालने के लिए रखी जाती है; **reward model** (पाठ 4), जो policy के sample किए outputs को score करता है; और एक **value function**, जिसका इस्तेमाल उन advantage estimates के लिए होता है जिन पर PPO का clip किया objective (पाठ 7) टिका है। Ouyang et al. सीधे कहते हैं कि उनका value function reward model से initialize होता है, जिससे वह अपने-आप में एक बड़े model के parameters की एक पूरी copy बन जाता है, reward model से अलग भले ही उसका शुरुआती बिंदु वही हो। एक के बजाय चार बड़े models का एक साथ memory घेरना और compute खाना असली, संरचनात्मक लागत है, जिसका इससे कोई लेना-देना नहीं कि training कितनी अच्छी या बुरी चल रही है।

### अस्थिरता ख़ास तौर पर कहाँ से आती है

Ouyang et al. बताते हैं कि इस setup में पैमाना कहाँ बुरी तरह टकराता है। उन्होंने पाया कि 175-अरब-parameter reward model छोटे वाले से कम validation loss पा सकता था, पर दो क़ीमतों पर: उसकी training ज़्यादा अस्थिर थी, जिससे PPO का value function उससे initialize करना बुरा चुनाव बन गया, और 175-अरब-parameter reward model और value function को साथ इस्तेमाल करने से policy की अपनी लागत के ऊपर PPO की compute ज़रूरतें काफ़ी बढ़ गईं। उनका हल व्यावहारिक था, सैद्धांतिक नहीं: उन्होंने पाया कि 6-अरब-parameter reward model learning rates की चौड़ी रेंज में स्थिर था और मज़बूत PPO models train करने में उतना ही कारगर, और उन्होंने हर policy आकार के लिए वही एक 6B reward model इस्तेमाल किया, अपनी 175B policy समेत।

### यह ख़ास लेन-देन याद रखने लायक़ क्यों है

यह सचमुच उलटा-सा नतीजा है जिसे पकड़कर रखना चाहिए: छोटा reward model संसाधनों की कमी से मजबूर समझौता नहीं था, Ouyang et al. ने जिस पैमाने पर परखा वहाँ वही ज़्यादा भरोसेमंद चुनाव था। बहुत बड़े पैमाने पर चलाई गई reward model और value function की training वह ज़्यादा सहज, पूर्वानुमेय scaling व्यवहार अपने-आप विरासत में नहीं पाती जो सीधा pretraining loss दिखाता है (चरण 3 के scaling laws, किसी दूसरे track से)। पैमाने पर अस्थिरता सिर्फ़ ऐसी असुविधा नहीं जिससे बचकर निकला जाए; इसने सीधे ढाला कि Ouyang et al. ने असल में क्या बनाया, और यह PPO के पूरे चार-या-पाँच-model वाले setup के महँगा होने और फिर भी आज़माने पर अविश्वसनीय होने की असली वजह है, जब हर हिस्से को सबसे बड़े संभव पैमाने पर चलाया जाए।

## अभ्यास

1. ▢ RLHF के लिए PPO training step में शामिल चार models के नाम बताएँ, और हर एक किस काम आता है।

<details markdown="1"><summary>जाँचें</summary>

Train हो रही policy; एक frozen SFT model, जिससे KL penalty निकाली जाती है; reward model, जो policy के outputs को score करता है; और value function (reward model से initialize, पर अलग से train), जो वे advantage estimates बनाता है जिनकी PPO के clip किए objective को ज़रूरत है।

</details>

2. ▢ Ouyang et al. के अनुसार, 175B reward model और value function इस्तेमाल करने के साथ कौन-सी दो क़ीमतें आईं, भले ही उसने छोटे वाले से कम validation loss पाया?

<details markdown="1"><summary>जाँचें</summary>

उसकी training ज़्यादा अस्थिर थी, जिससे PPO का value function उससे initialize करना बुरा चुनाव बन गया, और उसे इस्तेमाल करने से policy की अपनी लागत के ऊपर PPO की compute ज़रूरतें काफ़ी बढ़ गईं।

</details>

3. ▢ एक टीम मानती है कि RLHF के लिए बड़ा, ज़्यादा सटीक reward model हमेशा बेहतर चुनाव है, क्योंकि वह कम validation loss पाता है। Ouyang et al. की अपनी खोज के अनुसार, क्या यह मान्यता सुरक्षित है?

    - a) हाँ, कम-loss वाला reward model पैमाने की परवाह किए बिना हमेशा बेहतर चुनाव है
    - b) नहीं; 175B reward model की training ज़्यादा अस्थिर थी और compute लागत ज़्यादा, और छोटा 6B reward model स्थिर था और मज़बूत PPO models train करने में उतना ही कारगर
    - c) नहीं, क्योंकि बड़े reward models को PPO के साथ इस्तेमाल ही नहीं किया जा सकता
    - d) हाँ, पर सिर्फ़ इसलिए कि Ouyang et al. ने 175B reward model को कभी असल में परखा नहीं

<details markdown="1"><summary>जाँचें</summary>

**b)** ठीक Ouyang et al. की अपनी खोज है: कम validation loss का मतलब बेहतर व्यावहारिक चुनाव नहीं निकला जब training की स्थिरता और compute लागत को गिना गया। (a) उनके अपने रिपोर्ट किए लेन-देन को अनदेखा करता है। (c) खोज को बढ़ा-चढ़ाकर कहता है; समस्या स्थिरता और लागत की थी, असंगति की नहीं। (d) तथ्य की दृष्टि से ग़लत है; वे साफ़ रिपोर्ट करते हैं कि उन्होंने इन्हीं कारणों से 175B विकल्प को परखा और नकारा।

</details>

## असली दुनिया का अभ्यास

- [ ] असली RLHF training setup का वर्णन करने वाली कोई technical report या blog post खोजें, और देखें कि क्या वह अपनी policy, reward model और value function के सापेक्ष आकार बताती है। नोट करें कि reward model policy के आकार का है या जानबूझकर छोटा।
- [ ] Ouyang et al. का Appendix C का reward model training वाला हिस्सा पढ़ें (ऊपर link है) और एक वाक्य लिखें कि उन्होंने पाया कि training किस चीज़ के प्रति संवेदनशील थी, और किसके प्रति ज़्यादा संवेदनशील नहीं थी।
- [ ] कल: आगे देखे बिना चरण 5 के लिए एक वाक्य की भविष्यवाणी लिखें: यह देखते हुए कि PPO को policy के ऊपर एक reward model, एक value function और एक RL loop चाहिए, ऐसी विधि को, जो अलग reward model या RL loop के बिना मिलता-जुलता नतीजा दे, असल में अलग क्या करना पड़ेगा?

## आगे बढ़ने के लिए

- [पेपर: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [संसाधन](../RESOURCES.md)

---

चरण 4 ने बताया कि RLHF-PPO क्या optimize करता है और उसे चलाने में कितना ख़र्च आता है। चरण 5 एक ऐसा विकल्प बताता है जो ख़ास तौर पर दोनों में कम की ज़रूरत के लिए बना: कोई अलग reward model नहीं, और कोई RL loop बिल्कुल नहीं।

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
