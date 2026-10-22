---
title: "16. RLAIF: AI Feedback असल में Human Feedback से कितना मेल खाता है"
description: "अपने ही आकार का model, अपने ही outputs को परखकर, फिर भी सादे supervised fine-tuning से बेहतर निकला"
type: lesson
---

# पाठ 16. RLAIF: AI Feedback असल में Human Feedback से कितना मेल खाता है

**मिशन से संबंध:** "किसी दी गई safety-tuning pipeline में बता सकें कि feedback कहाँ से आया (इंसान या AI) और उसमें क्या लेन-देन है" "सफलता कैसी दिखती है" का वह बिंदु है जिसकी सेवा यह चरण करता है। पाठ 15 ने AI feedback पर बनी एक विधि कवर की; यह पाठ कई tasks पर AI feedback की human feedback से सीधी, नियंत्रित तुलना कवर करता है।
**मुख्य स्रोत:** [पेपर: "RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback", Lee et al., 2023](https://arxiv.org/abs/2309.00267)
**पूर्व-आवश्यकताएँ:** [पाठ 15](0015-constitutional-ai-feedback-from-a-model-not-a-human.md)

## वार्म-अप

1. ▢ RL-CAI में, उस इंसान labeler की जगह क्या लेता है जो आम तौर पर तय करता कि दो sample किए responses में से कौन-सा बेहतर है?

<details markdown="1"><summary>जाँचें</summary>

एक model। एक AI system तय करता है कि कौन-सा response बेहतर है, और preference model AI के बनाए preferences के इस dataset पर train होता है।

</details>

2. ▢ Bai et al. की अपनी तुलना के अनुसार, crowdworkers ने RL-CAI को पहले से इकट्ठा किए इंसानी harmfulness labels पर train हुए model के सामने कैसे आँका?

<details markdown="1"><summary>जाँचें</summary>

उन्होंने RL-CAI को इंसान-labelled तुलनाओं पर train हुए model पर तरजीह दी।

</details>

## यह जानें

### नियंत्रित, आमने-सामने की तुलना

Lee et al. वह सीधी तुलना करते हैं जिसका Constitutional AI के अपने नतीजों ने सिर्फ़ संकेत दिया था: तीन अलग tasks पर, summarization, helpful dialogue generation और harmless dialogue generation, वे एक policy को सामान्य RLHF से train करते हैं और दूसरी को **RLAIF** से, जिसमें preference labels इंसान के बजाय कोई तैयार (off-the-shelf) language model बनाता है, setup की बाक़ी हर चीज़ को तुलनीय रखते हुए। फिर human evaluators नतीजों को परखते हैं।

### नतीजा: दो tasks पर बराबर, तीसरे पर बेहतर

Summarization और helpful dialogue generation के लिए, RLAIF और RLHF दोनों को सादे SFT baseline पर कड़ी तरजीह मिलती है (उसके सामने क्रमशः 63% और 64% बार जीतते हुए), और RLAIF तथा RLHF की सीधी आमने-सामने तुलना दिखाती है कि दोनों को बराबर पसंद किया गया, उनके बीच कोई सांख्यिकीय रूप से महत्वपूर्ण अंतर नहीं। Harmless dialogue generation के लिए, Lee et al. रिपोर्ट करते हैं कि RLAIF असल में RLHF से **बेहतर** निकलता है, human evaluators ने उसे ज़्यादा harmless आँका। तीनों tasks में, इंसान-labelled preference dataset की जगह AI-labelled रखने से नतीजा बुरा नहीं हुआ; दो tasks पर वह RLHF के बराबर रहा, और तीसरे पर उससे आगे निकला।

### ज़्यादा चौंकाने वाला नतीजा: अपने ही आकार का, या अपना ही, model परखने वाला

Lee et al. और आगे बढ़ते हैं, उसकी ओर जिसे वे "self-improvement" कहते हैं: RLAIF तब भी सादे SFT baseline से बेहतर रहा जब preferences बनाने वाला AI labeler उसी आकार का था जिस policy को train किया जा रहा था, या सबसे चरम मामले में, ठीक वही checkpoint जिससे policy शुरू हुई थी। किसी model को ऐसे model के बनाए preference फ़ैसलों से बेहतर बनाया जा सकता है जो train हो रहे model से ज़्यादा सक्षम नहीं है, जिसमें उसकी अपनी पहले की copy के बनाए फ़ैसले भी शामिल हैं।

### Reward model को पूरी तरह छोड़ देना: direct-RLAIF

Lee et al. एक और सरलीकरण पेश करते हैं: **direct-RLAIF (d-RLAIF)**, जो अलग preference model train करना पूरी तरह छोड़ देता है और इसके बजाय RL training के दौरान ही सीधे किसी तैयार language model से reward score पूछता है। Pipeline से एक पूरा train किया हुआ model हटाना, वही reward model जिसे पाठ 8 पहले ही सामान्य RLHF में लागत बढ़ाने वाला असली कारण बता चुका है, उनके नतीजों में प्रदर्शन को नुक़सान नहीं पहुँचाया; वे रिपोर्ट करते हैं कि d-RLAIF canonical RLAIF से बेहतर प्रदर्शन पाता है, सिर्फ़ कम लागत पर तुलनीय प्रदर्शन नहीं।

### पाठ 15 के साथ मिलाकर यह किस पक्ष में दलील देता है

Constitutional AI के नतीजे (AI-feedback pipeline को human-feedback वाली पर तरजीह) और Lee et al. की नियंत्रित तुलना (तीन अलग tasks पर AI feedback का human feedback के बराबर या उससे बेहतर रहना, कम labeler पैमाने पर भी टिके रहना, और पूरे reward model के हटाए जाने को सह लेना) के बीच, यह दलील कि "AI feedback" human feedback का कमतर, मजबूरी वाला विकल्प है, किसी भी नतीजे के सामने ठीक से नहीं टिकती। Lee et al. अपना निष्कर्ष सीधे कहते हैं: RLAIF human feedback इकट्ठा करने की scalability सीमाओं का संभावित समाधान देता है, उसका महज़ सस्ता सन्निकटन नहीं।

## अभ्यास

1. ▢ Summarization और helpful dialogue generation में, Lee et al. के अनुसार, सादे SFT baseline के सामने RLAIF की जीत की दर RLHF की दर से कैसी रही?

<details markdown="1"><summary>जाँचें</summary>

सांख्यिकीय रूप से महत्वपूर्ण अंतर नहीं: दोनों SFT baseline के सामने मिलती-जुलती दरों (63% और 64%) पर जीते, और RLAIF तथा RLHF की सीधी आमने-सामने तुलना ने किसी एक के लिए भी महत्वपूर्ण तरजीह नहीं दिखाई।

</details>

2. ▢ Lee et al. के परखे तीन tasks में से किस पर RLAIF ने RLHF को सिर्फ़ बराबरी देने के बजाय पीछे छोड़ा?

<details markdown="1"><summary>जाँचें</summary>

Harmless dialogue generation। Human evaluators ने ख़ास तौर पर इस task पर RLAIF के responses को RLHF के responses से ज़्यादा harmless आँका।

</details>

3. ▢ इसमें चौंकाने वाली क्या बात है कि RLAIF तब भी SFT baseline से बेहतर रहा जब AI labeler ठीक वही checkpoint है जिस policy को train किया जा रहा है?

<details markdown="1"><summary>जाँचें</summary>

इसका मतलब है कि किसी model के अपने outputs के बारे में अपने ही preference फ़ैसले, ऐसे model से जो सुधारे जा रहे model से ज़्यादा सक्षम नहीं है, फिर भी सादे supervised fine-tuning पर असली सुधार पैदा कर सकते हैं, बजाय इसके कि उन्हें किसी ज़्यादा सक्षम चीज़ से या इंसान से feedback चाहिए हो।

</details>

4. ▢ Direct-RLAIF (d-RLAIF) मानक RLAIF pipeline से क्या हटाता है, और Lee et al. को उसके प्रदर्शन के बारे में क्या मिला?

    - a) वह policy model को ही हटा देता है; उन्हें ख़राब प्रदर्शन मिला
    - b) वह अलग train किया preference/reward model हटा देता है, RL के दौरान सीधे किसी तैयार LLM से reward score पूछता है; उन्हें canonical RLAIF से बेहतर प्रदर्शन मिला
    - c) वह RL चरण को पूरी तरह हटाकर सिर्फ़ SFT छोड़ देता है; प्रदर्शन अपरिवर्तित रहा
    - d) वह किसी भी language model की ज़रूरत हटा देता है, इसके बजाय पूरी तरह rule-based reward इस्तेमाल करता है

<details markdown="1"><summary>जाँचें</summary>

**b)** ठीक वही है जो Lee et al. बताते और रिपोर्ट करते हैं। (a), (c) और (d) हर एक pipeline में अलग, असंबंधित बदलाव का वर्णन करते हैं।

</details>

## असली दुनिया का अभ्यास

- [ ] देखें कि जिस training framework या शोध pipeline तक आपकी पहुँच है, वह AI-feedback या LLM-as-judge preference-labeling का विकल्प कहाँ देता है, और जाँचें कि वह canonical RLAIF (train किया preference model) से ज़्यादा मिलता है या direct-RLAIF (LLM से लाइव पूछा गया reward) से।
- [ ] Lee et al. के पेपर (ऊपर link है) में "self-improvement" नतीजे का वर्णन करने वाला अंश पढ़ें और एक वाक्य में लिखें कि यह नतीजा इससे ज़्यादा चौंकाने वाला क्यों है कि RLAIF बस बड़े, ज़्यादा सक्षम AI labeler के साथ RLHF की बराबरी कर ले।
- [ ] कल: किसी ऐसे task के लिए जिस पर आप model को align करना चाहेंगे, तय करें कि पहले RLHF अपनाएँगे, RLAIF, या direct-RLAIF, और एक वाक्य लिखें कि इस पाठ के किन नतीजों (तुलनीय गुणवत्ता, मिलते-जुलते पैमाने पर self-improvement, या कम pipeline लागत) ने आपका जवाब तय किया।

## आगे बढ़ने के लिए

- [पेपर: "RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback", Lee et al., 2023](https://arxiv.org/abs/2309.00267)
- [पेपर: "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
- [संसाधन](../RESOURCES.md)

---

चरण 8 ने वह feedback कवर किया जो इंसान के बजाय model से आता है, और वह असल में कितना टिकता है। चरण 9 उस कठिन सवाल की ओर मुड़ता है जो इस track में कवर की हर चीज़ के नीचे बैठा है: जब model align हो चुका हो, तो आप कैसे बताएँगे कि उस alignment को मापने वाली संख्या असली चीज़ माप रही है या नहीं।

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
