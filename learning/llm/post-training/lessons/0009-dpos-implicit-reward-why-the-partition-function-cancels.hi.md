---
title: "9. DPO का Implicit Reward: Partition Function क्यों कट जाता है"
description: "Reward और उसकी optimal policy के बीच एक अगम्य normalizing term खड़ा है, जब तक कि दो rewards का अंतर उसे ग़ायब नहीं कर देता"
type: lesson
---

# पाठ 9. DPO का Implicit Reward: Partition Function क्यों कट जाता है

**मिशन से संबंध:** "उसी preference data से DPO का implicit reward निकालें जो RLHF इस्तेमाल करता है, और बताएँ कि RL loop हटाने से वह क्या छोड़ देता है" "सफलता कैसी दिखती है" का चौथा बिंदु है। यह पाठ ख़ुद derivation को कवर करता है; पाठ 10 नतीजे में मिले loss को और इसे कवर करता है कि वह PPO की तुलना में क्या छोड़ देता है।
**मुख्य स्रोत:** [पेपर: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
**पूर्व-आवश्यकताएँ:** [पाठ 8](0008-why-ppo-is-expensive-and-unstable.md)

## वार्म-अप

1. ▢ RLHF के लिए PPO training step में शामिल चार (या पाँच, अगर value function को अलग गिनें) models के नाम बताएँ, और हर एक किस काम आता है।

<details markdown="1"><summary>जाँचें</summary>

Train हो रही policy; एक frozen SFT model, KL penalty के लिए; reward model, जो outputs को score करता है; और value function (reward model से initialize), जो वे advantage estimates बनाता है जिनकी PPO की clipping को ज़रूरत है।

</details>

2. ▢ Ouyang et al. की अपनी खोज के अनुसार, क्या बड़ा, कम-loss वाला reward model PPO के लिए हमेशा बेहतर व्यावहारिक चुनाव था?

<details markdown="1"><summary>जाँचें</summary>

नहीं। उनके 175B reward model की training value-function के initialization के रूप में ज़्यादा अस्थिर थी और compute लागत ज़्यादा, जबकि 6B वाला उन्हें स्थिर और उतना ही कारगर मिला, इसलिए उन्होंने हर policy आकार के लिए छोटा model इस्तेमाल किया।

</details>

## यह जानें

### RLHF वाला ही शुरुआती objective

Rafailov et al. ठीक उसी KL-constrained reward-maximization objective से शुरू करते हैं जो पाठ 6 पहले ही कवर कर चुका है: policy के तहत अपेक्षित reward `r(x, y)` को maximize करें, घटा एक तय reference policy `π_ref` के विरुद्ध KL penalty (`β` से scale की हुई)। पहले का काम, जिस पर Rafailov et al. सीधे निर्माण करते हैं, दिखा चुका था कि इस objective का एक ज्ञात, closed-form optimal हल है:

```text
π_r(y|x) = (1 / Z(x)) · π_ref(y|x) · exp((1/β) · r(x, y))
```

जहाँ `Z(x)` एक **partition function** है, prompt `x` की हर संभव completion `y` पर एक normalizing योग, जो `π_r` को वैध probability distribution बनाने के लिए चाहिए। `Z(x)` को ठीक-ठीक निकालने का मतलब होगा हर उस संभावित completion पर योग लेना जो कोई language model generate कर सकता है, जो उतना ही अगम्य है जितना सुनाई देता है, और ठीक इसीलिए यह closed form, जितना सही है, अपने-आप में training विधि के रूप में सीधे इस्तेमाल के लायक़ नहीं था।

### रिश्ते को उलटना

Rafailov et al. की चाल इसी समीकरण को इस तरह पुनर्व्यवस्थित करना है कि policy की जगह reward के लिए हल निकले। दोनों ओर का logarithm लेकर पुनर्व्यवस्थित करने से मिलता है:

```text
r(x, y) = β · log( π_r(y|x) / π_ref(y|x) ) + β · log Z(x)
```

यह किसी भी policy `π_r` से निहित reward को व्यक्त करता है, उस policy, reference policy और उसी झंझट वाले partition function के रूप में, जो अब भी एक जोड़ने वाले term की तरह मौजूद है।

### Partition function का मायने रखना क्यों बंद हो जाता है

यहीं Bradley-Terry loss (पाठ 4) असली काम करता है। Bradley-Terry की preference probabilities सिर्फ़ दो completions के rewards के *अंतर* `r(x, y_1) - r(x, y_2)` पर निर्भर करती हैं, किसी एक reward के निरपेक्ष मान पर कभी नहीं। चूँकि `Z(x)` सिर्फ़ prompt `x` पर निर्भर करता है, इस पर नहीं कि कौन-सी completion `y` score हो रही है, यह `r(x, y_1)` और `r(x, y_2)` दोनों में ठीक वही जोड़ने वाला term है। उलटे किए reward व्यंजक को एक ही prompt के दो rewards के अंतर में रखने से हर `β · log Z(x)` term पूरी तरह कट जाता है। बचती है एक preference probability जो पूरी तरह policy `π_r` और तय reference policy `π_ref` के रूप में व्यक्त है, जिसमें कहीं कोई reward model या partition function नहीं है।

### Implicit reward

शब्दावली का शब्द **implicit reward** ठीक यही नाम देता है: reward function `r(x, y) = β · log(π_r(y|x) / π_ref(y|x))` (partition-function वाला term छोड़ा जा सकता है जब सिर्फ़ अंतर मायने रखते हों) जिसे कोई policy गणितीय रूप से तय करती है, बस वह policy होने भर से, एक reference के सापेक्ष। इसे पैदा करने के लिए कभी कोई अलग reward model train नहीं किया गया; यह उसी optimal-policy रिश्ते से सीधे निकल आता है जिस पर RLHF पहले से बना था। Human preference data को पूरा करने के लिए policy को सीधे train करना, अलग से train किए reward की जगह इस implicit reward का इस्तेमाल करते हुए, वही पूरा विचार है जिसके लिए DPO का नाम पड़ा।

## अभ्यास

1. ▢ Partition function `Z(x)` को सीधे निकालना अगम्य क्यों कहा जाता है?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि उसे ठीक-ठीक निकालने के लिए हर उस संभावित completion `y` पर योग लेना पड़ेगा जो language model किसी दिए prompt `x` के लिए generate कर सकता है, एक विशाल space पर योग जिसे सीधे evaluate नहीं किया जा सकता।

</details>

2. ▢ एक ही prompt की दो completions के लिए अंतर `r(x, y_1) - r(x, y_2)` निकालते समय `Z(x)` क्यों कट जाता है, पर अगर किसी एक completion का reward अकेले चाहिए होता तो नहीं कटता?

<details markdown="1"><summary>संकेत</summary>

पूछें कि `Z(x)` असल में किस पर निर्भर करता है, और क्या वह निर्भरता `y_1` और `y_2` के बीच अलग होती है।

</details>

<details markdown="1"><summary>जाँचें</summary>

`Z(x)` सिर्फ़ prompt `x` पर निर्भर करता है, इस पर नहीं कि कौन-सी completion score हो रही है, इसलिए वह `r(x, y_1)` और `r(x, y_2)` दोनों में ठीक वही जोड़ने वाला term (`β · log Z(x)`) बनकर आता है। एक को दूसरे में से घटाने पर वह पूरी तरह हट जाता है। किसी एक reward में अकेले वही बिना हटा term फिर भी बना रहता।

</details>

3. ▢ "Implicit reward" का क्या मतलब है, उस ख़ास अर्थ में जिसमें यह पाठ उसे निकालता है?

<details markdown="1"><summary>जाँचें</summary>

वह reward function `β · log(π(y|x) / π_ref(y|x))` जिसे कोई भी policy, एक तय reference policy के सापेक्ष, गणितीय रूप से तय करती है, सिर्फ़ उसी optimal-policy रिश्ते के नतीजे के रूप में जो RLHF का objective पहले से निहित करता है। इसे कभी अलग model के रूप में train नहीं किया जाता; यह सीधे policy और reference policy से ही निकल आता है।

</details>

4. ▢ इनमें से कौन-सा सबसे अच्छा बताता है कि `Z(x)` को सीधे estimate करने की ज़रूरत के सापेक्ष DPO की derivation क्या हासिल करती है?

    - a) वह `Z(x)` को approximate करने की तेज़ numerical विधि खोजती है
    - b) वह समस्या को इस तरह पुनर्गठित करती है कि जब भी सिर्फ़ दो rewards का अंतर चाहिए, `Z(x)` पूरी तरह कट जाता है, और उसे निकालने की ज़रूरत ही नहीं पड़ती
    - c) वह `Z(x)` की जगह एक दूसरा, सरल partition function रख देती है
    - d) वह दिखाती है कि language models के लिए `Z(x)` हमेशा 1 के बराबर होता है

<details markdown="1"><summary>जाँचें</summary>

**b)** ठीक वही derivation है जिससे यह पाठ गुज़रता है। (a) और (c) दोनों मानते हैं कि `Z(x)` को किसी रूप में अब भी निकालना या approximate करना है, जिसे असली derivation बिल्कुल करने से बचाती है। (d) ऐसा दावा नहीं है जो derivation करती है या जिसकी उसे ज़रूरत है।

</details>

## असली दुनिया का अभ्यास

- [ ] DPO पेपर (ऊपर link है) का derivation वाला हिस्सा पढ़ें, KL-constrained objective से partition function के कटने तक, और अपने शब्दों में हर समीकरण के लिए एक वाक्य लिखें कि उसके और उससे पहले वाले के बीच क्या बदला।
- [ ] Symbol-दर-symbol लिखें कि `β · log(π(y|x) / π_ref(y|x))` का मान क्या आएगा अगर policy और reference policy `y` को ठीक एक ही probability देती हों। पुष्टि करें कि यह आपके अंदाज़े से मेल खाता है कि "इस completion से कोई preference signal नहीं" कैसा दिखना चाहिए।
- [ ] कल: आगे देखे बिना पाठ 10 के लिए एक वाक्य की भविष्यवाणी लिखें: यह देखते हुए कि implicit reward पूरी तरह policy और reference model से तय है, और तस्वीर में कोई reward model या partition function नहीं बचा, PPO के sampling-और-optimization loop की तुलना में DPO को कौन-सा training loop चाहिए होगा, आपके अनुमान से?

## आगे बढ़ने के लिए

- [पेपर: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
