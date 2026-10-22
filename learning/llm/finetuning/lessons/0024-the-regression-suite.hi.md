---
title: "24. Regression Suite"
description: "वह नुक़सान पकड़ना जो बाक़ी हर संख्या छिपा देती है"
type: lesson
---

# पाठ 24. Regression Suite

**मिशन से संबंध:** "ship करने से पहले regression पकड़ने वाला eval बनाएँ" मिशन के अपने शब्द हैं। यह वही पाठ है।
**मुख्य स्रोत:** [पेपर: "An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-tuning", Luo et al., arXiv:2308.08747](https://arxiv.org/abs/2308.08747)
**पूर्व-आवश्यकताएँ:** [पाठ 23](0023-metrics-that-mean-something.md), [पाठ 22](0022-contamination-and-held-out-design.md)

## वार्म-अप

1. ▢ Loss फ़ैसले का ग़लत आधार क्यों है?

<details markdown="1"><summary>जाँचें</summary>

वह एक reference continuation से सहमति को score करता है, सही विकल्पों को दंडित करता है और धाराप्रवाह ग़लतियों को इनाम देता है। उसे checkpoint चुनने के लिए इस्तेमाल करें, फ़ैसलों के लिए नहीं।

</details>

2. ▢ Model judges के दो दर्ज biases, और उनके शमन?

<details markdown="1"><summary>जाँचें</summary>

Position bias: क्रम को random करें और दोनों क्रमों को evaluate करें। Verbosity bias: बराबर लंबाई पर तुलना करें या judge को लंबाई अनदेखी करने का निर्देश दें।

</details>

3. ▢ आपके task का held-out सेट catastrophic forgetting के प्रति अंधा क्यों है?

<details markdown="1"><summary>जाँचें</summary>

वह आपके task के distribution से लिया गया है, इसलिए उस distribution के बाहर की क्षमताओं में बिगाड़ नहीं देख सकता।

</details>

## यह जानें

### वह विफलता जिसे पकड़ने के लिए यह है

Fine-tuning weights को आपके task की ओर खिसकाती है। जिन क्षमताओं को बल नहीं मिला वे बिगड़ सकती हैं, और यही **catastrophic forgetting** है। अनुभवजन्य साहित्य पाता है कि language models की continual fine-tuning में यह दुर्लभ किनारे का मामला नहीं है: instruction following समेत सामान्य क्षमताएँ नापने लायक ढंग से घटती हैं, और असर model के पैमाने के साथ सिकुड़ने के बजाय बढ़ सकता है।

ख़तरनाक गुण यह है कि **जो भी संख्या आप पहले से देख रहे हैं वह सही दिशा में जाती है।** Training loss गिरता है, आपकी held-out task metric सुधरती है, आपके probes अच्छे दिखते हैं, और model उन चीज़ों में बदतर हो गया है जिन्हें आपने कभी मापा नहीं। आप ship करते हैं, और रिपोर्टें उस दिशा से आती हैं जो आपका evaluation देख नहीं सकता था।

Held-out सेट मापता है कि आपने task सीखा या नहीं। Regression suite मापता है कि आपने और कुछ तोड़ा तो नहीं। **ये अलग उपकरण हैं और आपको दोनों चाहिए।**

### इसमें क्या जाता है

चार श्रेणियाँ। चारों, चुनाव नहीं।

**1. सामान्य instruction following।** क्या वह अब भी ऐसा साधारण instruction मान सकता है जिसका आपके task से कोई संबंध न हो? कुछ का सार बनाएँ, कोई सामान्य सवाल हल करें, बहु-चरण अनुरोध का पालन करें।

**2. Format और व्यवहार का अनुपालन।** क्या वह अब भी system prompt का सम्मान करता है? माँगे जाने पर अब भी valid JSON बनाता है? जब रुकना चाहिए तब अब भी रुकता है? एक कठोर format पर train हुआ model कभी-कभी कोई और format बनाने की क्षमता खो देता है।

**3. Safety और इनकार का व्यवहार।** अगर base model ने कुछ अनुरोधों से इनकार किया था, तो क्या fine-tune अब भी उनसे इनकार करता है? **सामान्य data पर fine-tuning साइड-इफ़ेक्ट के रूप में safety alignment बिगाड़ सकती है।** यह दर्ज और बार-बार दोहराया गया नतीजा है, काल्पनिक नहीं। अगर आपने alignment व्यवहार किसी instruct model से विरासत में पाया है, तो आपने यह जाँचने की ज़िम्मेदारी भी विरासत में पाई कि वह बचा या नहीं।

**4. निकटवर्ती क्षमता।** आपके task के पास की वे चीज़ें जिन पर आपने train नहीं किया। अंग्रेज़ी support tickets पर fine-tune किया? कोई दूसरी भाषा जाँचें। एक प्रकार के document पर fine-tune किया? दूसरा जाँचें।

### इसे बनाना

छोटा, तय, और इंसान द्वारा पढ़ा हुआ।

```text
regression/
├── instruction-following.jsonl   # 20 general instructions
├── format-compliance.jsonl       # 20 schema and system-prompt cases
├── safety.jsonl                  # 20 cases the base refused
├── adjacent.jsonl                # 20 near-task, untrained cases
└── baseline/                     # base model outputs, committed
```

कुल अस्सी examples। यह जान-बूझकर छोटा है: असली regression पकड़ने भर का, इतना छोटा कि कोई व्यक्ति सचमुच diffs पढ़े।

अहम, अक्सर छोड़ा जाने वाला क़दम: **training से पहले base model के outputs दर्ज करें, और उन्हें commit करें।** Regression एक *बदलाव* है, इसलिए आपको "पहले" चाहिए। सहेजे गए baseline के बिना आप इस याद से तुलना करते रह जाते हैं कि model पहले कैसा व्यवहार करता था, जो सबूत नहीं है।

```python
# Run once, before any training. Commit the result.
for case in regression_cases:
    out = base_model.generate(**tok(case["prompt"]), do_sample=False, max_new_tokens=256)
    baseline[case["id"]] = tok.decode(out[0], skip_special_tokens=True)
```

Greedy decoding, ताकि diff का मतलब sampler का पासा नहीं बल्कि weights का बदलाव हो।

### इसे पढ़ना

हर उम्मीदवार checkpoint पर suite चलाएँ। Baseline से diff निकालें। फिर हर बदलाव को वर्गीकृत करें:

| फ़ैसला | मतलब |
|---|---|
| अपरिवर्तित | ठीक |
| बदला, अब भी सही | नोट करें; ठीक |
| बदला, अब ग़लत | **Regression, ship रोक देता है** |
| बदला, अब बेहतर | बोनस, और समझने लायक |

तीसरी पंक्ति ही पूरा मुद्दा है। Safety या instruction following में एक साफ़ regression आपकी task metric के दो-एक अंकों पर भारी पड़ता है, क्योंकि विफलता की सीमा अनंत है और फ़ायदे की नहीं।

### Forgetting को घटाना, जब वह मिले

विकल्प, मोटे तौर पर इस क्रम में कि वे आपको क्या क़ीमत देते हैं:

1. **कम steps, या पहले का checkpoint।** Forgetting training के साथ बढ़ती है। अक्सर सबसे सस्ता इलाज, और आम तौर पर task प्रदर्शन की थोड़ी ही क़ीमत।
2. **कम learning rate।** छोटे updates कम बिगाड़ते हैं।
3. **कम rank, या कम target modules।** ऊपर से लिखने के लिए कम capacity।
4. **सामान्य instruction data मिलाएँ।** आपके task data के साथ सामान्य instruction-following examples का कुछ प्रतिशत। असरदार और भली-भाँति स्थापित, और यह आपको model की गुणवत्ता नहीं बल्कि dataset की शुद्धता की क़ीमत देता है।
5. **Adapter को unmerged रखें और route करें।** सबसे पूरा जवाब: adapter सिर्फ़ उन अनुरोधों के लिए लगाएँ जिन्हें उसकी ज़रूरत है, और बाक़ी सबके लिए अछूता base serve करें। Forgetting अप्रासंगिक हो जाती है क्योंकि base अब भी वहाँ है। पाठ 25।

विकल्प 5 वह है जिसे लोग अनदेखा करते हैं, और अक्सर वही सही architecture है। अगर आपका fine-tune किसी बड़े product के भीतर एक संकरे उद्देश्य की सेवा करता है, तो आपको ऐसा एक model नहीं चाहिए जो सब करे।

### इसे automate करें

Suite को हर checkpoint पर, बिना कहे, चलना चाहिए और regression पर पास होने से इनकार करना चाहिए। जो evaluation किसी के चलाना याद रखने पर निर्भर है, वह उस run पर छूट जाएगा जिस पर वह मायने रखता था, यानी जो समय की तंगी में हो।

## अभ्यास

1. ▢ लगातार सुधरती held-out task metric regression को ख़ारिज क्यों नहीं कर पाती?

<details markdown="1"><summary>जाँचें</summary>

वह आपके task के distribution से लिया गया है और इसलिए सिर्फ़ आपका task देखता है। उस distribution के बाहर की क्षमताएँ उसके लिए अदृश्य हैं, और forgetting ठीक उन्हीं को नुक़सान पहुँचाती है।

आपको अलग उपकरण चाहिए जिसका निशाना वह हो जिस पर आप train *नहीं* कर रहे।

</details>

2. ▢ चारों regression श्रेणियों के नाम बताएँ।

<details markdown="1"><summary>जाँचें</summary>

सामान्य instruction following, format और व्यवहार का अनुपालन, safety और इनकार का व्यवहार, निकटवर्ती बिना-train की क्षमता।

Safety वह है जो सबसे ज़्यादा छूटती है, और पूरी तरह सामान्य data पर fine-tuning उसे बिगाड़ सकती है।

</details>

3. ▢ आपके पास regression suite है पर कोई सहेजा हुआ baseline नहीं। उसे चलाने से आप क्या निष्कर्ष निकाल सकते हैं?

<details markdown="1"><summary>जाँचें</summary>

बहुत कम। Regression पिछले व्यवहार से बदलाव है, इसलिए पिछले व्यवहार के बिना आप कोई पहचान नहीं सकते, सिर्फ़ outputs को अलग-थलग आँक सकते हैं, जो सूक्ष्म बिगाड़ को उजागर नहीं करेगा।

Training से पहले base-model के outputs दर्ज करें और commit करें। यही वह क़दम है जो suite को काम करने लायक बनाता है।

</details>

4. ▢ Task metric 3 अंक ऊपर; model अब उस अनुरोध से इनकार नहीं करता जिससे base ने किया था। Ship करें?

<details markdown="1"><summary>जाँचें</summary>

नहीं। Safety regression task के फ़ायदों की परवाह किए बिना ship रोकता है: नुकसान की सीमा अनंत है जबकि तीन अंक नहीं हैं।

जाँच करें: पहले का checkpoint आज़माएँ, कम learning rate, सामान्य instruction data मिलाएँ, या adapter को unmerged रखें और सिर्फ़ प्रासंगिक traffic उसकी ओर route करें।

</details>

5. ▢ Forgetting की समस्या को सबसे पूरी तरह कौन-सा उपाय मिटाता है?

    - a) Training सेट में सामान्य instruction data मिलाना
    - b) Base model को unmerged serve करना और अनुरोध के हिसाब से route करना
    - c) Learning rate घटाना और कम steps के लिए train करना
    - d) Adapter rank और target module की गिनती घटाना

<details markdown="1"><summary>जाँचें</summary>

**b)** Base model को unmerged serve करना और अनुरोध के हिसाब से route करना।

बाक़ी इसे घटाते हैं कि कितनी forgetting होती है। Routing का मतलब है कि आपके task के बाहर की हर चीज़ के लिए अपरिवर्तित base अब भी उपलब्ध है, इसलिए adapt किए रास्ते में forgetting मायने रखना बंद कर देती है।

</details>

6. ▢ Regression suite के लिए greedy decoding क्यों?

<details markdown="1"><summary>जाँचें</summary>

ताकि baseline से फ़र्क़ sampling के बजाय बदले हुए weights के नाम जाए। शून्य से ऊपर के temperature पर हर run अलग होता है और diff कोई जानकारी नहीं ढोता।

</details>

## असली दुनिया का अभ्यास

- [ ] 20 regression मामले लिखें, हर श्रेणी में पाँच। कम से कम एक ऐसा शामिल करें जिससे base model इनकार करता है।
- [ ] किसी भी training से पहले, greedy तरीक़े से, base-model के baseline outputs बनाएँ और commit करें।
- [ ] अपने मौजूदा adapter पर suite चलाएँ और diff निकालें। हर बदलाव को चारों फ़ैसलों में वर्गीकृत करें।
- [ ] कल: suite को अपनी training script में जोड़ें ताकि वह हर checkpoint पर बिना माँगे चले।

## आगे बढ़ने के लिए

- [पेपर: "An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-tuning", Luo et al., arXiv:2308.08747](https://arxiv.org/abs/2308.08747)
- [पेपर: "Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To!", Qi et al., arXiv:2310.03693](https://arxiv.org/abs/2310.03693)
- [failure modes शीट](../reference/failure-modes.md)
- [पाठ 25. Adapters को Serve करना](0025-serving-adapters.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
