---
title: "15. Constitutional AI: Feedback इंसान से नहीं, Model से"
description: "नुक़सान के लिए इंसानी labels शून्य, उनकी जगह लिखे हुए सिद्धांतों की सूची, और एक assistant जो टालने के बजाय अपनी आपत्तियाँ समझाता है"
type: lesson
---

# पाठ 15. Constitutional AI: Feedback इंसान से नहीं, Model से

**मिशन से संबंध:** "किसी दी गई safety-tuning pipeline में बता सकें कि feedback कहाँ से आया (इंसान या AI) और उसमें क्या लेन-देन है" "सफलता कैसी दिखती है" का वह बिंदु है जिसकी सेवा यह चरण करता है। यह पाठ Constitutional AI की दो-चरणों वाली विधि कवर करता है; पाठ 16 कवर करता है कि सीधी, नियंत्रित तुलना में AI feedback human feedback के सामने कितना टिकता है।
**मुख्य स्रोत:** [पेपर: "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
**पूर्व-आवश्यकताएँ:** [पाठ 14](0014-distilling-a-reasoning-model-down.md)

## वार्म-अप

1. ▢ DeepSeek-AI की अपनी 32B तुलना के अनुसार, क्या छोटे model को सीधे बड़े पैमाने की RL से train करने से वही reasoning प्रदर्शन मिला जो बड़े, पहले से RL-trained model से distil करने पर मिला?

<details markdown="1"><summary>जाँचें</summary>

नहीं। 32B base model पर सीधी RL AIME 2024 पर 47.0% pass@1 तक पहुँची, जो उस 72.6% से काफ़ी नीचे है जो वही base model तब पाता है जब उसे इसके बजाय बड़े model के distilled reasoning traces पर fine-tune किया गया।

</details>

2. ▢ Verifiable reward क्या है, और उसमें वह reward-hacking वाली विफलता क्यों नहीं है जो train किए reward model में है?

<details markdown="1"><summary>जाँचें</summary>

सीखे हुए model के बजाय deterministic checker से पैदा हुआ reward; चूँकि output और उसके score के बीच किसी सीखे हुए model की सनकें खड़ी नहीं हैं, policy के सीखने के लिए reward-model-विशेष कोई फ़ायदा उठाने का रास्ता नहीं है।

</details>

## यह जानें

### उस विफलता को याद करें जिससे बचने के लिए यह विधि बनी है

पाठ 5 ने असली, दर्ज की गई विफलता कवर की: harmlessness के लिए ज़रूरत से ज़्यादा optimize हुई RLHF policies हर बात पर टालने पर आकर टिक गईं, लगभग हर थोड़े-से भी संवेदनशील सवाल पर users को therapy लेने की सलाह देते हुए, जो harmlessness reward model पर अच्छा score पाने का सस्ता तरीक़ा है, बिना सचमुच helpful हुए। **Constitutional AI (CAI)** ख़ास तौर पर ऐसा harmless assistant बनाने के लिए बना है जो यह शॉर्टकट न ले।

### दो चरण, और हर एक में AI feedback कहाँ आता है

Supervised चरण, **SL-CAI**, एक शुरुआती model से responses sample करता है, model से उसके अपने response की एक **self-critique** और एक **revision** लिखवाता है, सिद्धांतों की छोटी, लिखी हुई सूची (वह "constitution" जिसके नाम पर विधि का नाम है) के विरुद्ध, और फिर मूल model को इन self-revised responses पर fine-tune करता है, यानी model के अपने बनाए और सुधारे data पर सामान्य SFT (चरण 2)।

Reinforcement learning चरण, **RL-CAI**, SL-finetuned model से responses के जोड़े sample करता है, और यह बताने के लिए कि कौन-सा बेहतर है, इंसान labeler से कहने के बजाय, **model से** वह फ़ैसला करवाता है। AI के बनाए preferences के इस dataset पर एक preference model (पाठ 4 की Bradley-Terry training) train होता है, और फिर policy को उस AI-trained preference model के विरुद्ध RL से train किया जाता है, ठीक वैसे जैसे पाठ 6 का RLHF setup human-trained वाले को इस्तेमाल करता। Bai et al. इस सामान्य तकनीक को सीधे नाम देते हैं: **RL from AI Feedback (RLAIF)**।

### नुक़सान के लिए इंसानी labels शून्य, और उससे क्या निकला

Bai et al. अपना नतीजा साफ़ कहते हैं: यह पूरी pipeline "non-evasive" और "relatively harmless" AI assistant को "without any human feedback labels for harms" बिल्कुल train करती है। Model के व्यवहार को constitution के सिद्धांत ढालते हैं, हज़ारों इंसानी harmfulness फ़ैसले नहीं। नतीजे में मिला assistant हानिकारक सवालों से सीधे इनकार करने या टालने के बजाय उन पर अपनी आपत्तियाँ समझाकर जुड़ता है, जो पाठ 5 में दर्ज उस ख़ास over-optimization का सीधा जवाब है: जिस model की harmlessness training सबसे सस्ते इनकार के बजाय सोच-समझकर जुड़ने को पुरस्कृत करती है, उसके पास हर बात पर टालने में ढह जाने का प्रोत्साहन शुरू से ही कम होता है।

### वह तुलना जो इसे गंभीरता से लेने लायक़ बनाती है

Bai et al. सिर्फ़ यह दावा नहीं करते कि यह काम करता है; वे रिपोर्ट करते हैं कि crowdworkers ने नतीजे में मिले model, "RL-CAI", को उन models पर तरजीह दी जो harmfulness के पहले से इकट्ठा किए इंसानी feedback labels से train हुए थे। इंसानी harm labels की जगह लिखा हुआ constitution और AI के बनाए preferences रखना सिर्फ़ इंसान-labelled विकल्प की बराबरी नहीं कर पाया; उनकी अपनी रिपोर्ट की तुलना में, उसने बेहतर किया।

## अभ्यास

1. ▢ SL-CAI में, fine-tuning में इस्तेमाल होने से पहले model अपने sample किए responses के साथ क्या करता है?

<details markdown="1"><summary>जाँचें</summary>

वह लिखे हुए constitution के सिद्धांतों के विरुद्ध response की self-critique generate करता है, फिर response की एक revision बनाता है, और model को इन revised responses पर fine-tune किया जाता है।

</details>

2. ▢ RL-CAI में, उस इंसान labeler की जगह क्या लेता है जो आम तौर पर तय करता कि दो sample किए responses में से कौन-सा बेहतर है?

<details markdown="1"><summary>जाँचें</summary>

एक model। एक AI system तय करता है कि दो responses में से कौन-सा बेहतर है, और preference model इंसान-labelled तुलनाओं के बजाय AI के बनाए preferences के इस dataset पर train होता है।

</details>

3. ▢ हानिकारक अनुरोध से सीधे इनकार करने के बजाय अपनी आपत्तियाँ समझाने वाला Constitutional AI का assistant पाठ 5 में बताई विफलता को सीधे कैसे सँभालता है?

<details markdown="1"><summary>जाँचें</summary>

पाठ 5 की हर-बात-पर-टालने वाली विफलता इसलिए पैदा हुई कि सीधे इनकार करना harmlessness reward model पर अच्छा score पाने का सस्ता, कम परिष्कार वाला तरीक़ा था। ऐसा training तरीक़ा जिसका reward इसके बजाय अनुरोध पर सचमुच जुड़ने और आपत्तियाँ समझाने को तरजीह दे, उस सस्ते शॉर्टकट का प्रोत्साहन हटा देता है, क्योंकि अकेला टालना सबसे ऊँचा score देने वाला विकल्प नहीं रहेगा।

</details>

4. ▢ Bai et al. की अपनी तुलना के अनुसार, crowdworkers ने RL-CAI को harmfulness के पहले से इकट्ठा किए इंसानी feedback labels पर train हुए model के सामने कैसे आँका?

<details markdown="1"><summary>जाँचें</summary>

उन्होंने RL-CAI को तरजीह दी। इंसानी harm labels की जगह constitution और AI के बनाए preferences रखना उनकी रिपोर्ट की तुलना में इंसान-labelled विकल्प की सिर्फ़ बराबरी नहीं कर पाया; उसे उस पर तरजीह मिली।

</details>

## असली दुनिया का अभ्यास

- [ ] असली model को train करने में इस्तेमाल हुआ प्रकाशित "constitution" या मार्गदर्शक सिद्धांतों का सेट खोजें (कई सार्वजनिक रूप से जारी हुए हैं), और उसके तीन-चार सिद्धांत पढ़ें। नोट करें कि वे ख़ास नियमों जैसे पढ़ते हैं या ऐसे सामान्य मूल्यों जैसे जिनकी व्याख्या model को करनी पड़ेगी।
- [ ] Constitutional AI पेपर (ऊपर link है) में SL-CAI के self-critique-और-revision वाले चरण का वर्णन करने वाला अंश पढ़ें, और एक वाक्य लिखें कि model की self-critique के अपने response की असली समस्या न पकड़ पाने के लिए क्या ग़लत होना पड़ेगा।
- [ ] कल: आगे देखे बिना पाठ 16 के लिए एक वाक्य की भविष्यवाणी लिखें: यह देखते हुए कि Constitutional AI एक अकेली विधि के लिए इंसानी harm labels की जगह AI के बनाए labels रखता है, क्या आप उम्मीद करेंगे कि AI feedback दूसरी तरह के tasks में भी इतना ही अच्छा चलेगा, जैसे summarization या सामान्य helpfulness, और क्यों या क्यों नहीं?

## आगे बढ़ने के लिए

- [पेपर: "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
