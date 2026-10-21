---
title: "10. DPO Loss, और PPO की तुलना में वह क्या छोड़ देता है"
description: "एक loss, दो models, कोई sampling loop नहीं, और वही beta जो KL penalty इस्तेमाल करता"
type: lesson
---

# पाठ 10. DPO Loss, और PPO की तुलना में वह क्या छोड़ देता है

**मिशन से संबंध:** "उसी preference data से DPO का implicit reward निकालें जो RLHF इस्तेमाल करता है, और बताएँ कि RL loop हटाने से वह क्या छोड़ देता है" "सफलता कैसी दिखती है" का चौथा बिंदु है। पाठ 9 ने derivation कवर की; यह पाठ नतीजे में मिले loss को कवर करता है और साफ़ कहता है कि वह PPO की तुलना में क्या छोड़ देता है।
**मुख्य स्रोत:** [पेपर: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
**पूर्व-आवश्यकताएँ:** [पाठ 9](0009-dpos-implicit-reward-why-the-partition-function-cancels.md)

## वार्म-अप

1. ▢ एक ही prompt के दो rewards का अंतर निकालते समय partition function `Z(x)` क्यों कट जाता है?

<details markdown="1"><summary>जाँचें</summary>

`Z(x)` सिर्फ़ prompt पर निर्भर करता है, इस पर नहीं कि कौन-सी completion score हो रही है, इसलिए वह घटाए जा रहे दोनों rewards में ठीक वही जोड़ने वाला term है, और अंतर से पूरी तरह कट जाता है।

</details>

2. ▢ "Implicit reward" का क्या मतलब है, उस अर्थ में जिसमें पाठ 9 उसे निकालता है?

<details markdown="1"><summary>जाँचें</summary>

वह reward function जिसे कोई policy, एक तय reference policy के सापेक्ष, गणितीय रूप से तय करती है, सिर्फ़ उस optimal-policy रिश्ते के नतीजे के रूप में जो RLHF का objective पहले से निहित करता है, अलग reward model कभी train किए बिना।

</details>

## यह जानें

### Implicit reward को Bradley-Terry loss में रखना

पाठ 4 के Bradley-Terry loss ने अलग reward model को इस तरह train किया कि पसंद की गई completion का score नकारी गई completion से ऊँचा हो। DPO ठीक वही विचार इस्तेमाल करता है, एक प्रतिस्थापन के साथ: जहाँ-जहाँ Bradley-Terry loss train किए reward model का output इस्तेमाल करता, DPO वहाँ पाठ 9 का implicit reward, `β · log(π(y|x) / π_ref(y|x))`, रख देता है, जो सीधे train हो रही policy और frozen reference model से निकलता है। नतीजे में मिला loss, ठीक वैसा जैसा Rafailov et al. देते हैं, एक ही prompt की पसंद की गई completion `y_w` और नकारी गई completion `y_l` की तुलना करता है:

```text
loss = -log( sigmoid( β · [ (log π(y_w|x) - log π_ref(y_w|x)) - (log π(y_l|x) - log π_ref(y_l|x)) ] ) )
```

यह पाठ 4 का Bradley-Terry loss है, जिसमें reward model के दो scores की जगह implicit reward के दो मान हैं, एक पसंद की गई completion का और एक नकारी गई का। Loss की बनावट में कुछ नहीं बदला; जो बदला वह यह है कि reward की जगह कौन खड़ा है।

### इस loss को क्या चाहिए, और अब क्या नहीं चाहिए

इस loss को निकालने के लिए ठीक दो models चाहिए: train हो रही policy, और reference model की frozen copy (आम तौर पर SFT model), हर एक उन्हीं पसंद की गई और नकारी गई completions पर evaluate होकर कुल चार log-probabilities देता है। इसकी तुलना चरण 4 के PPO setup (पाठ 8) से करें: कोई अलग reward model बिल्कुल train नहीं होता, क्योंकि implicit reward सीधे policy और reference model से निकलता है। कोई value function नहीं चाहिए, क्योंकि estimate करने को कोई advantage नहीं है; DPO उस अर्थ में reinforcement learning नहीं कर रहा जिसमें actions sample किए जाते हैं और returns estimate होते हैं। PPO clipping (पाठ 7) भी नहीं है, क्योंकि कोई policy-gradient update नहीं है जिसके step के आकार को सीमित करना पड़े; यह loss सीधे optimize होता है, जैसे कोई भी सामान्य supervised loss, preference pairs के हर batch पर एक gradient step के साथ, steps के बीच कोई sampling loop बिल्कुल नहीं।

### वही beta, वही काम करता हुआ

DPO के loss का `β` इस विधि के लिए गढ़ा गया नया hyperparameter नहीं है; यह पाठ 6 के RLHF objective वाली वही KL-penalty की ताक़त है, जो अब सीधे implicit reward में पकाई गई है, reward model के score के ऊपर जोड़े अलग penalty term की तरह दिखने के बजाय। बड़े `β` का मतलब अब भी reference model के क़रीब रहना है; छोटे `β` का मतलब अब भी उससे दूर जाने की ज़्यादा आज़ादी, ठीक पाठ 6 का लेन-देन, बस दो अलग terms के बजाय एक ही loss के भीतर व्यक्त।

### असल में क्या छोड़ा जाता है

DPO उन लेन-देनों को नहीं हटाता जिन्हें PPO की KL penalty सँभाल रही थी; वह मशीनरी को हटाता है। Rafailov et al. की विधि उसी optimal-policy रिश्ते का गणितीय रूप से सटीक पुनर्सूत्रीकरण है जिस पर RLHF पहले से टिका है, उसका सन्निकटन नहीं, इसलिए preference-संतुष्टि के बुनियादी लक्ष्य में कुछ भी कमज़ोर नहीं होता। जो सचमुच छोड़ा जाता है वह है अलग से खड़ा reward model और उसे अलग से train करने से आने वाली लचीलापन: reward model को, सिद्धांत में, उन outputs को score करने के लिए दोबारा इस्तेमाल किया जा सकता है जिन पर उसने policy को सीधे कभी train नहीं किया, उसे अकेले जाँचा जा सकता है, या मूल preference data से आगे के अतिरिक्त signals के साथ जोड़ा जा सकता है। DPO का implicit reward सिर्फ़ किसी ख़ास policy और reference model की जोड़ी से बँधा हुआ मौजूद रहता है; training ख़त्म होने के बाद कोई स्वतंत्र scoring function नहीं बचता, सिर्फ़ train हुई policy ख़ुद।

## अभ्यास

1. ▢ एक preference pair के लिए DPO loss की गणना में चार log-probabilities चाहिए। बताएँ कि चारों में से हर एक किसकी log-probability है।

<details markdown="1"><summary>जाँचें</summary>

पसंद की गई completion की policy की log-probability, पसंद की गई completion की reference model की log-probability, नकारी गई completion की policy की log-probability, और नकारी गई completion की reference model की log-probability।

</details>

2. ▢ PPO के components (reward model, value function, KL penalty, clip किया update) में से किनकी DPO के loss को बिल्कुल ज़रूरत नहीं?

    - a) सिर्फ़ clip किए update की
    - b) Reward model और value function की; KL-penalty का लेन-देन अब भी मौजूद है, बस अलग term के बजाय implicit reward में पकाया हुआ
    - c) चारों की, क्योंकि DPO किसी भी तरह की KL penalty इस्तेमाल नहीं करता
    - d) सिर्फ़ reward model की; DPO अब भी अलग value function train करता है

<details markdown="1"><summary>जाँचें</summary>

**b)** सही ब्योरा है: DPO को अलग reward model या value function नहीं चाहिए, और कोई प्रति-step clip किया update नहीं है क्योंकि कोई RL sampling loop नहीं है, पर पाठ 6 में बताया वही beta-नियंत्रित लेन-देन अब भी मौजूद है, सीधे implicit reward term में समाया हुआ। (a), (c) और (d) हर एक ग़लत बताते हैं कि कौन-से हिस्से बचे रहते हैं।

</details>

3. ▢ एक टीम अपने train किए reward model को दोबारा इस्तेमाल करके completions के ऐसे batch को score करना चाहती है जो किसी policy के training run का हिस्सा कभी नहीं थे, सिर्फ़ monitoring के लिए। क्या PPO के बजाय DPO इस्तेमाल करने वाली टीम वही काम बराबर आसानी से कर सकती है?

<details markdown="1"><summary>जाँचें</summary>

उतनी सीधे नहीं। DPO कभी स्वतंत्र reward model नहीं बनाता; उसका implicit reward सिर्फ़ किसी ख़ास train हुई policy और उसके reference model के रूप में परिभाषित है। मनमानी completions को इस तरह score करना ठीक उसी तरह का दोबारा इस्तेमाल है जिसे स्वतंत्र reward model सहारा देता है और DPO का तरीक़ा उपोत्पाद के रूप में नहीं देता।

</details>

4. ▢ क्या DPO के loss में `β` का मतलब पाठ 6 के RLHF objective वाले `β` से कुछ अलग है?

<details markdown="1"><summary>जाँचें</summary>

नहीं। यह वही KL-penalty की ताक़त है, जो उसी लेन-देन को नियंत्रित करती है: reference model के क़रीब रहने और उस ओर बढ़ने के बीच जिसे preference data पुरस्कृत करता है; DPO बस उसे सीधे implicit reward term में समेट देता है, reward model के score में जोड़े गए दृश्य रूप से अलग penalty के रूप में रखने के बजाय।

</details>

## असली दुनिया का अभ्यास

- [ ] जिस library तक आपकी पहुँच है उसमें DPO implementation खोजें (Hugging Face का TRL आम है) और पुष्टि करें कि वह प्रति preference pair वही चार log-probabilities निकालता है जो यह पाठ बताता है।
- [ ] छोटे काल्पनिक उदाहरण से (policy और reference model के तहत पसंद की गई और नकारी गई completion के लिए मान्य-से log-probability मान बना लें) `β` के दो अलग मानों के लिए हाथ से DPO loss निकालें, और बताएँ कि `β` बढ़ने पर loss कैसे बदलता है।
- [ ] कल: किसी ऐसे project के लिए जिसमें आप model को align करना चाहेंगे, तय करें कि पहले PPO अपनाएँगे या DPO, और एक वाक्य लिखें कि इस पाठ के किन लेन-देनों (engineering लागत, स्वतंत्र reward model का दोबारा इस्तेमाल, RL infrastructure) ने आपका जवाब तय किया।

## आगे बढ़ने के लिए

- [पेपर: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
- [दस्तावेज़: "TRL - Transformer Reinforcement Learning", Hugging Face](https://huggingface.co/docs/trl/index)
- [संसाधन](../RESOURCES.md)

---

चरण 5 ने RLHF जैसे ही नतीजे तक पहुँचने का तरीक़ा बताया, बिना अलग reward model या RL loop के। चरण 6 PPO से एक अलग विचलन कवर करता है: RL loop को रखना, पर ऐसे tasks के लिए जहाँ reward इंसान की पसंद का मामला बिल्कुल नहीं, बल्कि सीधे जाँचा जा सकने वाली चीज़ है।

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
