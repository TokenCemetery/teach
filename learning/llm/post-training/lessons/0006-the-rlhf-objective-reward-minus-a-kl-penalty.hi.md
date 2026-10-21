---
title: "6. RLHF Objective: Reward में से KL Penalty घटाना"
description: "एक term reward model का score बटोरता है; दूसरा term वह पट्टा है जो policy को उसे लेकर भाग जाने से रोकता है"
type: lesson
---

# पाठ 6. RLHF Objective: Reward में से KL Penalty घटाना

**मिशन से संबंध:** "RLHF objective निकालें (reward में से reference model के विरुद्ध KL penalty घटाना), और बताएँ कि KL penalty ढीला करने पर policy का क्या होता है" "सफलता कैसी दिखती है" का तीसरा बिंदु है। यह पाठ ख़ुद objective को कवर करता है; पाठ 7 PPO को कवर करता है, जो उसे optimize करने वाला algorithm है, और पाठ 8 बताता है कि यह सब चलाने में कितना ख़र्च आता है।
**मुख्य स्रोत:** [पेपर: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**पूर्व-आवश्यकताएँ:** [पाठ 5](0005-reward-hacking.md)

## वार्म-अप

1. ▢ harmlessness के लिए ज़रूरत से ज़्यादा optimize होने पर Bai et al. की policies किस पर आकर टिकीं, और वह व्यवहार अच्छा score पाने का सस्ता तरीक़ा क्यों था?

<details markdown="1"><summary>जाँचें</summary>

हर बात पर टालना: लगभग हर थोड़े-से भी संवेदनशील सवाल पर users को therapy या पेशेवर मदद लेने की सलाह देना। इसमें बहुत कम परिष्कार चाहिए था, बस अनुरोध को संवेदनशील के रूप में वर्गीकृत करके मना कर देना, जो सचमुच बारीक, helpful और harmless होने से कहीं आसान है।

</details>

2. ▢ Bai et al. का train-PM-बनाम-test-PM अलगाव, जब वह दिखा, तो किस बात का संकेत था?

<details markdown="1"><summary>जाँचें</summary>

कि policy की संभावना है कि ख़ास तौर पर train PM के विरुद्ध ज़रूरत से ज़्यादा optimize हुई थी, उस व्यवहार का फ़ायदा उठाते हुए जिसे वह पुरस्कृत करता है पर held-out reward model, जिसे ठीक यही policy देखने की उम्मीद करना कभी सिखाया नहीं गया, उतना ऊँचा पुरस्कृत नहीं करता।

</details>

## यह जानें

### पूरा objective

Ouyang et al. वह ठीक objective बताते हैं जिसे उनकी PPO training maximize करती है:

```text
objective(φ) = E[(x,y) ~ policy] [ r(x, y) − β · log( policy(y|x) / SFT(y|x) ) ]
             + γ · E[x ~ pretraining data] [ log( policy(x) ) ]
```

यहाँ तीन हिस्से तीन अलग काम कर रहे हैं, और उन्हें एक-एक करके लेना ठीक रहेगा।

### Reward term

`r(x, y)` prompt `x` पर policy के अपने output `y` के लिए train किए reward model का scalar score (पाठ 4) है। अकेले इस term को maximize करना ही policy को उन outputs की ओर धकेलता है जिन्हें reward model ऊँचा score देता है, ठीक वही लक्ष्य जिसे साधने के लिए reward modeling है।

### KL penalty term

`β · log( policy(y|x) / SFT(y|x) )` train हुई policy के `y` बनाने की संभावना की तुलना मूल SFT model के उसी `y` को बनाने की संभावना से करता है, और policy की अपनी संभावना जितनी बड़ी हो गई है उसके अनुपात में penalty घटाता है। Ouyang et al. इसे सीधे **SFT model से per-token KL penalty** बताते हैं, जिसे ख़ास तौर पर **reward model के over-optimization को कम करने** के लिए जोड़ा गया, यानी पाठ 5 में बताई गई ठीक वही विफलता। अकेला reward term policy को हर प्रोत्साहन देता है कि `r(x, y)` को maximize करने के लिए जितना ज़रूरी हो उतना भटक जाए; KL term वह है जो SFT distribution से दूर भटकने की कुछ क़ीमत लगाता है, बजाय इसके कि वह मुफ़्त हो।

### β ढीला या कसा जाने पर क्या होता है

`β` एक डायल है, और दोनों दिशाओं की असली क़ीमत है:

- जैसे-जैसे `β` शून्य की ओर घटता है, SFT policy से अलग होने की penalty लगभग ग़ायब हो जाती है, और objective सिर्फ़ reward model के score का पीछा करने तक सिमट जाता है, जिसमें policy को रोकने वाला लगभग कुछ नहीं बचता। यह ठीक वही बेलगाम optimization है जिसका सबूत पाठ 5 का train-PM-बनाम-test-PM अलगाव है: KL penalty policy को जितना कम रोकती है, उसके पास उतनी ज़्यादा गुंजाइश होती है कि reward model संयोग से जो पुरस्कृत करे उसका फ़ायदा उठाए, न कि वह जो उसके designers असल में चाहते थे।
- जैसे-जैसे `β` बड़ा होता है, SFT policy से दूर जाने की penalty objective पर हावी हो जाती है, और train हुई policy लगभग ठीक SFT model को दोहराने की ओर खिंच जाती है। इसे काफ़ी आगे ले जाएँ तो यह RL चरण का मक़सद ही ख़त्म कर देता है: अगर policy SFT के पहले से दिए नतीजे से सार्थक रूप से दूर नहीं जा सकती, तो RLHF के पास उसके ऊपर जोड़ने को कुछ नहीं बचता।

`β` चुनना इस लेन-देन पर एक बिंदु चुनना है, उसे ख़त्म करना नहीं: छोटा `β` उस reward hacking का जोखिम लेता है जो पाठ 5 ने बताया; बड़ा `β` इस जोखिम को कि RLHF उससे ज़्यादा कुछ न जोड़े जो अकेला SFT पहले ही पा चुका था।

### Pretraining-gradient term, और पाठ 1 से उसका संबंध

अंतिम term, `γ · E[log(policy(x))]`, reward-बनाम-KL के लेन-देन से बिल्कुल अलग है: यह मूल pretraining distribution पर सामान्य language-modeling objective मिला देता है, जिससे policy की उस तरह के text की likelihood बढ़ती है जिस पर वह pretrained थी। Ouyang et al. जिन्हें सादा "PPO" models कहते हैं उनके लिए `γ = 0` रखते हैं, और जिन्हें "PPO-ptx" models कहते हैं उनके लिए शून्येतर `γ`। यह term पाठ 1 के alignment tax को घटाने के पीछे का असली तंत्र है: PPO training में pretraining-data के gradients वापस मिलाने से ही public NLP benchmarks पर प्रदर्शन की वह गिरावट ज़्यादातर लौटी जो सादी PPO training लाई थी, और RLHF जिन preference फ़ायदों के लिए बना था उन्हें छोड़ना नहीं पड़ा।

## अभ्यास

1. ▢ एक टीम RLHF objective में `β` को बहुत छोटा मान देती है। यह policy को सबसे सीधे किस जोखिम में डालता है, और क्यों?

<details markdown="1"><summary>जाँचें</summary>

Reward hacking: KL penalty लगभग ग़ायब होने से reward term लगभग बिना विरोध के objective पर हावी हो जाता है, जिससे policy के पास उस ओर भटकने से रुकने की कम वजह रहती है जिसे reward model संयोग से ऊँचा score देता है, चाहे वह व्यवहार वही हो या न हो जिसे reward model को असल में दर्शाना था।

</details>

2. ▢ इसके बजाय एक टीम `β` को बहुत बड़ा मान देती है। इस चुनाव की सबसे संभावित क़ीमत क्या है?

<details markdown="1"><summary>जाँचें</summary>

Policy SFT model को क़रीब-क़रीब दोहराने की ओर खिंच जाती है, क्योंकि कोई भी सार्थक विचलन भारी penalty पाता है; इसे काफ़ी आगे ले जाएँ तो RLHF के पास उससे ज़्यादा कोई व्यवहार जोड़ने की गुंजाइश नहीं बचती जो अकेला SFT पहले ही दे चुका था।

</details>

3. ▢ Ouyang et al. जिसे "PPO" और "PPO-ptx" कहते हैं उनमें क्या फ़र्क़ है, और objective का कौन-सा term उन्हें अलग करता है?

<details markdown="1"><summary>जाँचें</summary>

"PPO" pretraining-gradient गुणांक `γ` को 0 रखता है; "PPO-ptx" शून्येतर `γ` इस्तेमाल करता है, जिससे PPO updates में pretraining-data की log-likelihood के gradients मिल जाते हैं। यही वह term है जो पाठ 1 के बताए alignment tax को घटाने के लिए ज़िम्मेदार है।

</details>

4. ▢ इनमें से कौन-सा सबसे अच्छा बताता है कि reward term और KL penalty term हर एक objective में क्या भूमिका निभाता है?

    - a) Reward term policy को उसकी ओर खींचता है जिसे reward model ऊँचा score देता है; KL penalty उसे वापस SFT model की ओर खींचता है, और objective दोनों में संतुलन बिठाता है
    - b) दोनों terms policy को एक ही दिशा में, reward model की पसंद की ओर, खींचते हैं
    - c) KL penalty सिर्फ़ evaluation के दौरान इस्तेमाल होता है, training के दौरान नहीं
    - d) Reward term और KL penalty term गणितीय रूप से एक जैसे हैं, बस अलग पैमाने पर

<details markdown="1"><summary>जाँचें</summary>

**a)** असली रिश्ता है: दो terms जो सचमुच अलग दिशाओं में खींचते हैं, और `β` उनके बीच संतुलन तय करता है। (b), (c) और (d) objective की बनावट को ऐसे ग़लत बताते हैं जिन्हें इस पाठ की derivation सीधे नकार देती है।

</details>

## असली दुनिया का अभ्यास

- [ ] देखें कि जिस training framework तक आपकी पहुँच है, वह RLHF के लिए KL-penalty गुणांक कहाँ उपलब्ध कराता है (अक्सर `beta` या `kl_coef` जैसे नाम से), और उसका default मान और उसे tune करने के बारे में दर्ज मार्गदर्शन नोट करें।
- [ ] InstructGPT पेपर (ऊपर link है) में पूरे objective का वर्णन करने वाला अनुच्छेद पढ़ें और एक-एक वाक्य में लिखें कि `β` और `γ` दोनों को एक साथ शून्य रखने पर training का क्या होता है।
- [ ] कल: आगे देखे बिना पाठ 7 के लिए एक वाक्य की भविष्यवाणी लिखें: यह देखते हुए कि इस objective को policy के अपने parameters समायोजित करके maximize करना है, और sample किए outputs के एक batch पर आधारित एक अकेला update policy को एक ही क़दम में बहुत दूर धकेल सकता है, इस objective का naive optimization किस समस्या में फँस सकता है?

## आगे बढ़ने के लिए

- [पेपर: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
