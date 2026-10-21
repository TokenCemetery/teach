---
title: "7. PPO: Update को Clip क्यों किया जाता है"
description: "Sample किए data के एक batch पर बड़ी जीत बड़े क़दम का भरोसेमंद सबूत नहीं है; PPO उस पर पूरा यक़ीन करने से इनकार करता है"
type: lesson
---

# पाठ 7. PPO: Update को Clip क्यों किया जाता है

**मिशन से संबंध:** RLHF objective निकालने (पाठ 6) का तब तक ज़्यादा मतलब नहीं जब तक पता न हो कि "PPO से policy को उसके विरुद्ध optimize करें" असल में क्या करता है। यह पाठ वह तंत्र देता है, जिसे चरण 4 का बाक़ी हिस्सा और मिशन का विवेक वाला चरण दोनों इस पर टिके हैं कि उसे black box मानने के बजाय ठोस रूप से नाम दिया जा सके।
**मुख्य स्रोत:** [पेपर: "Proximal Policy Optimization Algorithms", Schulman et al., 2017](https://arxiv.org/abs/1707.06347)
**पूर्व-आवश्यकताएँ:** [पाठ 6](0006-the-rlhf-objective-reward-minus-a-kl-penalty.md)

## वार्म-अप

1. ▢ RLHF objective में, जैसे-जैसे KL-penalty गुणांक `β` शून्य की ओर घटता है, policy का क्या होता है?

<details markdown="1"><summary>जाँचें</summary>

SFT policy से अलग होने की penalty लगभग ग़ायब हो जाती है, इसलिए objective सिर्फ़ reward model के score का पीछा करने तक सिमट जाता है, जिसमें policy को रोकने वाला लगभग कुछ नहीं बचता, और वह उस reward hacking के जोखिम में आ जाती है जो पाठ 5 ने बताया।

</details>

2. ▢ Ouyang et al. के नामकरण में "PPO" और "PPO-ptx" में क्या फ़र्क़ है, और कौन-सा term उन्हें अलग करता है?

<details markdown="1"><summary>जाँचें</summary>

"PPO" pretraining-gradient गुणांक `γ` को 0 रखता है; "PPO-ptx" शून्येतर `γ` इस्तेमाल करता है, जिससे training में pretraining-data की log-likelihood के gradients मिल जाते हैं, और यही alignment tax को घटाता है।

</details>

## यह जानें

### बेलगाम update की समस्या

Schulman et al. एक सरल surrogate objective से शुरू करते हैं, जिसे "vanilla" policy-gradient विधि सीधे maximize करती: `L^CPI(θ) = E[r_t(θ) · Â_t]`, जहाँ `r_t(θ) = policy(a|s) / policy_old(a|s)` असल में लिए गए action की संभावना का नई और पुरानी policy के बीच अनुपात है, और `Â_t` अनुमानित **advantage** है, मोटे तौर पर, कि वह action अपेक्षा से कितना बेहतर या बुरा निकला। `L^CPI` को बिना किसी और रोक के maximize करना optimizer को हर प्रोत्साहन देता है कि `r_t(θ)` को उस दिशा में जितना हो सके धकेले जिससे objective बढ़ता है। Schulman et al. समस्या को सीधे कहते हैं: "without a constraint, maximization of `L^CPI` would lead to an excessively large policy update." Sample किए एक batch पर बड़ा अनुमानित advantage इस बात का भरोसेमंद सबूत नहीं है कि उतना ही बड़ा क़दम हर जगह लेना सुरक्षित है; उस पर ज़रूरत से ज़्यादा प्रतिक्रिया training को अस्थिर कर सकती है।

### PPO का इलाज: ratio को clip करें, फिर निराशावादी मामला लें

Schulman et al. का असली objective यह है:

```text
L^CLIP(θ) = E[ min( r_t(θ)·Â_t, clip(r_t(θ), 1-ε, 1+ε)·Â_t ) ]
```

जहाँ `ε` एक छोटा स्थिरांक है (वे `0.2` इस्तेमाल करते हैं)। `clip(...)` term ratio `r_t(θ)` को अंतराल `[1-ε, 1+ε]` में सीमित कर देता है, जो उसे उस सीमा से बाहर और धकेलने का प्रोत्साहन हटा देता है। Clip किए और बिना clip किए रूपों का `min` लेना, अकेले clip किए रूप के बजाय, ही इसे **निराशावादी सीमा (pessimistic bound)** बनाता है: Schulman et al. समझाते हैं कि यह योजना "only ignore[s] the change in probability ratio when it would make the objective improve, and... include[s] it when it makes the objective worse." सीधे शब्दों में, जो चाल मददगार दिखती है उसे पूरा पुरस्कृत करने के बजाय सीमित कर दिया जाता है, इसलिए optimizer एक उत्साहजनक batch से असीमित श्रेय नहीं निचोड़ सकता, जबकि जो चाल असल में नुक़सान कर रही है उसे उसी सीमा से बचाया नहीं जाता, और उसकी पूरी क़ीमत फिर भी गिनी जाती है।

### यह KL penalty से अलग तरह का स्थिरता-नियंत्रण क्यों है

पाठ 6 की KL penalty और इस पाठ की clipping दोनों स्थिरता के तंत्र हैं, पर वे अलग दायरों में काम करते हैं और उन्हें मिलाना नहीं चाहिए। KL penalty train हुई policy को मूल, तय **SFT reference model** के सामने मापती है, और सीमित करती है कि पूरा training run अपनी पूरी राह में उस तय बिंदु से कितना भटक सकता है। PPO की clipping policy की तुलना **मौजूदा update से ठीक पहले की अपनी ही स्थिति** (`policy_old`) से करती है, और सीमित करती है कि कोई एक optimization step कितना बड़ा हो सकता है, इसकी परवाह किए बिना कि policy अभी SFT model के सापेक्ष कहाँ बैठी है। एक पूरे run में कुल भटकाव को क़ाबू करती है; दूसरी रास्ते के हर अलग step के आकार को। दोनों चाहिए, और कोई एक दूसरे की जगह नहीं ले सकती: प्रति-step की छोटी clip कई छोटे steps को आख़िरकार reference model से दूर भटकने से नहीं रोकती, और reference model के विरुद्ध KL penalty किसी एक step को विनाशकारी रूप से बड़ा होने से रोकने के लिए कुछ नहीं करती।

## अभ्यास

1. ▢ Sample की गई completions का एक अकेला batch, सिर्फ़ इस वजह से कि वह batch संयोग से कैसे sample हुआ, एक action के लिए असामान्य रूप से बड़ा अनुमानित advantage पैदा करता है। बिना किसी सीमा के, policy को उस advantage के अनुपात में पूरी तरह update होने देना जोखिम भरा क्यों है?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि एक batch का अनुमानित advantage इस बात का भरोसेमंद सबूत नहीं है कि उतना ही बड़ा बदलाव हर जगह सुरक्षित है; किसी एक उत्साहजनक (या हतोत्साहित करने वाले) sample पर ज़रूरत से ज़्यादा प्रतिक्रिया policy को एक ही step में बहुत बड़ी दूरी तक धकेल सकती है, ठीक वही अस्थिरता जिसे रोकने के लिए PPO की clipping बनी है।

</details>

2. ▢ PPO clip किए और बिना clip किए surrogate terms का न्यूनतम क्यों लेता है, अकेले clip किए term को इस्तेमाल करने के बजाय?

    - a) न्यूनतम लेने से objective निराशावादी सीमा बन जाता है: जो चाल सुधार जैसी दिखती है वह सीमित हो जाती है, जबकि जो चाल हानिकारक दिखती है उसे उसी सीमा से सुरक्षा नहीं मिलती और वह पूरी गिनी जाती है
    - b) न्यूनतम सिर्फ़ computational दक्षता के लिए इस्तेमाल होता है और सीखी गई policy पर उसका कोई असर नहीं
    - c) अकेले clip किया term इस्तेमाल करने से ratio असीमित हो जाता
    - d) न्यूनतम यह सुनिश्चित करता है कि ratio हमेशा ठीक 1 के बराबर रहे

<details markdown="1"><summary>जाँचें</summary>

**a)** Schulman et al. का अपना बताया तर्क है। (b) optimization के व्यवहार पर असली असर को कम आँकता है। (c) clipping का असली मक़सद उलटा समझता है; clipping ratio को सीमित करती है, उसे असीमित नहीं छोड़ती। (d) गलत समझता है कि clipping क्या करती है; ratio को 1 के आसपास के अंतराल में सीमित किया जाता है, ठीक 1 के बराबर रहने को मजबूर नहीं किया जाता।

</details>

3. ▢ एक टीम के RLHF setup में बड़ा KL-penalty गुणांक `β` है पर प्रति-step clipping बिल्कुल नहीं है (बिना clip वाला surrogate objective)। क्या यह setup किसी एक विनाशकारी रूप से बड़े policy update से सुरक्षित है?

<details markdown="1"><summary>जाँचें</summary>

नहीं। बड़ा `β` सीमित करता है कि training के दौरान policy SFT reference model से कितना भटक सकती है, पर यह किसी एक अलग update को, जो एक batch के अनुमानित advantage पर आधारित है, ज़रूरत से ज़्यादा बड़ा होने से रोकने के लिए कुछ नहीं करता। ये दो अलग स्थिरता-नियंत्रण हैं, और एक को हटाने की भरपाई दूसरा नहीं करता।

</details>

## असली दुनिया का अभ्यास

- [ ] देखें कि जिस PPO implementation तक आपकी पहुँच है, वह clip parameter कहाँ उपलब्ध कराता है (अक्सर `epsilon`, `clip_range` या ऐसे नाम से), और उसका default मान Schulman et al. के रिपोर्ट किए `0.2` से मिलाकर नोट करें।
- [ ] PPO पेपर (ऊपर link है) में वह अनुच्छेद पढ़ें जो बताता है कि अकेला `L^CPI` अत्यधिक बड़े update की ओर क्यों ले जाएगा, और अपने शब्दों में एक वाक्य लिखें कि बेलगाम surrogate objective की ठीक कौन-सी बात इसकी वजह है।
- [ ] कल: आगे देखे बिना पाठ 8 के लिए एक वाक्य की भविष्यवाणी लिखें: यह देखते हुए कि RLHF को अब एक policy, KL penalty के लिए एक frozen reference (SFT) model, एक reward model, और advantage estimates बनाने के लिए कुछ और चाहिए जिन पर इस पाठ का clipping formula टिका है, एक PPO training step में आपको कितने अलग बड़े models शामिल होने की उम्मीद है?

## आगे बढ़ने के लिए

- [पेपर: "Proximal Policy Optimization Algorithms", Schulman et al., 2017](https://arxiv.org/abs/1707.06347)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
