---
title: "11. GRPO: Value Function की जगह Group-Relative Advantage"
description: "एक ही सवाल के कई उत्तर sample करें, और group के rewards के अपने फैलाव को बताने दें कि कौन-से बेहतर थे"
type: lesson
---

# पाठ 11. GRPO: Value Function की जगह Group-Relative Advantage

**मिशन से संबंध:** "GRPO में group-relative advantage समझाएँ, और बताएँ कि verifiable reward (unit test, जाँचा हुआ गणित का उत्तर) से RL training किसे निशाना बना सकती है, यह कैसे बदल जाता है" "सफलता कैसी दिखती है" का पाँचवाँ बिंदु है। यह पाठ ख़ुद group-relative advantage को कवर करता है; पाठ 12 verifiable rewards को कवर करता है, वह जोड़ी जो GRPO को गणित और code के लिए ख़ास तौर पर उपयुक्त बनाती है।
**मुख्य स्रोत:** [पेपर: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
**पूर्व-आवश्यकताएँ:** [पाठ 10](0010-the-dpo-loss-and-what-it-drops-relative-to-ppo.md)

## वार्म-अप

1. ▢ Models के लिहाज़ से, DPO के loss को ऐसा क्या चाहिए जो PPO के setup को नहीं चाहिए?

<details markdown="1"><summary>जाँचें</summary>

कुछ अतिरिक्त नहीं; DPO को PPO से सख़्ती से कम models चाहिए। उसे सिर्फ़ policy और एक frozen reference model चाहिए, कोई अलग reward model और कोई value function नहीं।

</details>

2. ▢ क्या DPO में अलग reward model और RL loop हटाने से reference model के क़रीब रहने और उस ओर बढ़ने के बीच का KL-penalty वाला लेन-देन भी हट जाता है जिसे preference data पुरस्कृत करता है?

<details markdown="1"><summary>जाँचें</summary>

नहीं। वही लेन-देन, उसी `β` से नियंत्रित, अब भी मौजूद है; वह बस सीधे implicit reward term में समेट दिया गया है, दृश्य रूप से अलग penalty के रूप में रखने के बजाय।

</details>

## यह जानें

### वह लागत जो PPO का value function ख़ास तौर पर जोड़ता है

चरण 4 (पाठ 8) पहले ही स्थापित कर चुका है कि PPO को reward model के साथ-साथ एक value function चाहिए, उसी से initialize किया हुआ, ताकि वह उन advantage estimates को बना सके जिन पर उसका clip किया objective टिका है। Shao et al. ठीक बताते हैं कि वही ख़ास हिस्सा महँगा क्यों है: value function आम तौर पर policy के बराबर आकार का एक और model होता है, जो PPO को पहले से जो कुछ चाहिए उसके ऊपर असली memory और compute लागत जोड़ता है। वे language models की एक दूसरी ख़ास समस्या जोड़ते हैं: इस setting में आम तौर पर completion का सिर्फ़ बिल्कुल आख़िरी token ही कोई reward score पाता है, जिससे उस completion के हर पहले वाले token पर सटीक value function train करना उस setting से कठिन हो जाता है जिसमें हर step पर reward feedback मिलता है।

### GRPO का विकल्प: samples के group को अपना baseline देने दें

**Group Relative Policy Optimization (GRPO)** value function को पूरी तरह हटा देता है, और उसकी जगह ऐसी चीज़ रखता है जिसे कोई अतिरिक्त model चाहिए ही नहीं: किसी सवाल `q` के लिए GRPO उसी (पुरानी) policy से `G` outputs का एक **group**, `{o_1, o_2, ..., o_G}`, sample करता है। एक reward model `G` outputs में से हर एक को score करता है, जिससे `G` rewards मिलते हैं, `r_1` से `r_G` तक। अलग से train किए value function से यह पूछने के बजाय कि "क्या यह ख़ास output अपेक्षा से बेहतर था," GRPO एक सरल सवाल पूछता है जिसका उत्तर सीधे group से मिल जाता है: क्या यह output उसी सवाल के लिए sample किए गए बाक़ी outputs से बेहतर था। Output `i` का **group-relative advantage** group-normalized reward है:

```text
A_i = (r_i - mean(r_1, ..., r_G)) / std(r_1, ..., r_G)
```

जो उस output के हर token पर एक-सा लगता है। जो output group के औसत से ऊपर score करता है उसे धनात्मक advantage मिलता है; जो उससे नीचे score करता है उसे ऋणात्मक advantage; advantage का आकार इस पर scale होता है कि group के rewards संयोग से कितने फैले हुए थे। कोई value function बिल्कुल train नहीं होता, और पाठ 8 ने जो memory और compute लागत उसके सिर मढ़ी थी वह उसके साथ ग़ायब हो जाती है।

### यह reward models के साथ ख़ास तौर पर क्यों फ़िट बैठता है

Shao et al. एक और बात कहते हैं जो पकड़कर रखने लायक़ है: यह group-relative तुलना सिर्फ़ लागत बचाने का शॉर्टकट नहीं है, यह उस data की बनावट से मेल खाती है जिस पर reward model शुरू में train हुआ था। Bradley-Terry reward model (पाठ 4) एक ही सवाल के outputs की आपसी तुलनाओं पर train होता है; एक ही सवाल के कई outputs को score करना और उनकी तुलना निरपेक्ष, अलग से सीखे baseline के बजाय एक-दूसरे से करना, reward model से उसी तरह का सापेक्ष फ़ैसला करवाना है जो करना उसे असल में सिखाया गया था।

### KL penalty कहाँ चली जाती है

GRPO पाठ 6 के RLHF objective की तुलना में KL penalty की जगह भी बदलता है। Ouyang et al. के objective ने KL penalty को सीधे per-token reward में जोड़ा था, उससे advantages निकलने से पहले ही। Shao et al. इसके बजाय train हुई policy और reference policy के बीच के KL divergence को loss में सीधे एक अलग term के रूप में जोड़ते हैं, clip किए surrogate objective के साथ, उसे उस reward में मिलाने के बजाय जिससे advantage निकलता है। इससे गणना का reward-आधारित हिस्सा (और उससे बना group-relative advantage) KL term से उलझा नहीं रहता, जबकि policy अपने reference से कितना भटके इस पर उसी तरह की रोक फिर भी लगती है।

## अभ्यास

1. ▢ एक ही सवाल के 4 sample किए outputs के group को reward model से rewards `{2, 4, 6, 8}` मिलते हैं। मोटे तौर पर, किन outputs को धनात्मक group-relative advantage मिलता है, और किन्हें ऋणात्मक?

<details markdown="1"><summary>संकेत</summary>

पहले group का औसत निकालें, फिर पूछें कि कौन-से rewards उससे ऊपर हैं और कौन-से नीचे।

</details>

<details markdown="1"><summary>जाँचें</summary>

औसत 5 है। 6 और 8 score करने वाले outputs औसत से ऊपर हैं और उन्हें धनात्मक advantage मिलता है; 2 और 4 score करने वाले outputs उससे नीचे हैं और उन्हें ऋणात्मक advantage मिलता है।

</details>

2. ▢ Shao et al. के अनुसार, PPO के value function की दो ख़ास समस्याएँ बताएँ जिनसे GRPO का group-relative advantage बचता है।

<details markdown="1"><summary>जाँचें</summary>

Value function आम तौर पर policy के बराबर आकार का एक और model होता है, जो काफ़ी memory और compute लागत जोड़ता है, और LLM setting में, जहाँ आम तौर पर सिर्फ़ आख़िरी token को reward score मिलता है, हर पहले वाले token पर सटीक value function train करना उन settings से कठिन है जिनमें हर step पर reward feedback मिलता है।

</details>

3. ▢ Shao et al. group-relative तुलना को reward models के साथ ख़ास तौर पर फ़िट क्यों बताते हैं, value function से सिर्फ़ सस्ती होने से आगे?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि reward models आम तौर पर एक ही सवाल के outputs की आपसी तुलनाओं पर ही train होते हैं (वही बनावट जो पाठ 4 का Bradley-Terry loss इस्तेमाल करता है); एक सवाल के कई outputs को score करना और उनकी तुलना एक-दूसरे से करना reward model से उसी तरह का सापेक्ष फ़ैसला करवाना है जो करना उसे असल में सिखाया गया था।

</details>

4. ▢ GRPO की KL penalty कहाँ बैठती है, Ouyang et al. के RLHF objective (पाठ 6) में KL penalty की जगह की तुलना में?

    - a) उसी जगह: advantages निकलने से पहले सीधे per-token reward में जोड़ी गई
    - b) GRPO में कोई KL penalty है ही नहीं
    - c) GRPO KL divergence को loss में सीधे अलग term के रूप में जोड़ता है, clip किए objective के साथ, उसे reward में मिलाने के बजाय
    - d) GRPO KL penalty की जगह दूसरा reward model रख देता है

<details markdown="1"><summary>जाँचें</summary>

**c)** वह असली जगह है जो Shao et al. बताते हैं। (a) Ouyang et al. के तरीक़े का वर्णन है, जिसे GRPO ख़ास तौर पर बदलता है। (b) और (d) दोनों ग़लत बताते हैं कि GRPO क्या करता है; उसी तरह की रोक अब भी मौजूद है, बस दूसरी जगह ले जाई गई।

</details>

## असली दुनिया का अभ्यास

- [ ] जिस library तक आपकी पहुँच है उसमें GRPO implementation खोजें, और देखें कि वह group-normalized advantage कैसे निकालता है: क्या वह इस पाठ के दिए औसत-और-standard-deviation वाले formula से मेल खाता है?
- [ ] DeepSeekMath पेपर (ऊपर link है) में वह अनुच्छेद पढ़ें जो बताता है कि value function ख़ास तौर पर LLM setting में महँगा क्यों है, और एक वाक्य लिखें जो memory-लागत वाली दलील को प्रति-token-सटीकता वाली दलील से अलग करे।
- [ ] कल: आगे देखे बिना पाठ 12 के लिए एक वाक्य की भविष्यवाणी लिखें: अगर reward model की जगह कोई भी ऐसी चीज़ ले सकती है जो हर sample किए output के लिए भरोसेमंद score दे, तो किस तरह का task उस score को train किए model के बजाय deterministic checker से आने देगा?

## आगे बढ़ने के लिए

- [पेपर: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
