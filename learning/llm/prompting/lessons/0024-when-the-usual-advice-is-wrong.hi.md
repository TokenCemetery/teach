---
title: 24. जब आम सलाह ग़लत हो
description: पहचानें कि किसी model या task के लिए prompting की मानक सलाह कब नाकाम होती है, और विवाद का निपटारा primary source से करें
type: lesson
---

# पाठ 24. जब आम सलाह ग़लत हो

**मिशन से संबंध:** यह track इस पर ख़त्म होता है कि आप पर भरोसा किया जाए कि आप किसी prompt पर फ़ैसला ले सकें और उसे किसी और को समझा सकें। Prompting की सलाह नारों की तरह फैलती है, और नारा कुछ models, tasks और तारीख़ों के लिए सच होता है और दूसरों के लिए झूठ। यह पाठ उसका तरीक़ा है कि पता कैसे लगाएँ कि कौन-सा।
**मुख्य स्रोत:** [Paper: "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models", Zheng et al., 2023](https://arxiv.org/abs/2311.10054)
**पूर्व-आवश्यकताएँ:** [पाठ 2](0002-system-prompts-and-roles.md), [पाठ 7](0007-few-shot-biases.md), [पाठ 10](0010-prompting-reasoning-models.md), [पाठ 18](0018-a-regression-set-for-a-prompt.md), [पाठ 23](0023-reviewing-a-production-prompt.md)

## वार्म-अप

1. ▢ Reasoning model के prompt में लिखे हुए चरणों के बजाय लक्ष्य और constraints क्यों दिए जाते हैं?

<details markdown="1"><summary>जाँचें</summary>

Model पहले से अपना reasoning चरण पैदा करता है, इसलिए हाथ से लिखी योजना उसे उस रास्ते से बदतर रास्ते तक सीमित कर सकती है जो वह ख़ुद खोज लेता। बताएँ कि उत्तर को क्या पूरा करना है और उसे तय करने दें कि वहाँ कैसे पहुँचना है।

</details>

2. ▢ पाठ 6 के अनुसार few-shot examples ज़्यादातर क्या सिखाते हैं?

<details markdown="1"><summary>जाँचें</summary>

Format, label space और input distribution, हर label की शुद्धता से ज़्यादा। इसीलिए उन्हें कवरेज और क्रम के लिए चुनना हर एक को चमकाने से ज़्यादा मायने रखता है।

</details>

3. ▢ Regression set में क्या जाता है, और prompt के बारे में विवाद में वह किस काम का है?

<details markdown="1"><summary>जाँचें</summary>

ज़्यादातर असली विफलताओं से बने inputs, हर एक के output पर जाँच के साथ। विवाद में वह तटस्थ ज़मीन है: अलग-अलग पेपरों से तर्क कर रहे दो लोग दोनों अपना पसंदीदा prompt उस पर चलाकर तुलना कर सकते हैं।

</details>

## यह जानें

### तरीक़ा

"model को role दें" या "हमेशा step-by-step instruction जोड़ें" जैसा नारा अपनी शर्तों के बिना आता है। यह तय करने का तरीक़ा कि वह आपके लिए सही है या नहीं, चार चरणों का है:

1. **Primary source खोजें।** उसका हवाला देने वाली blog post नहीं। पेपर या vendor का दस्तावेज़, यह पढ़ते हुए कि असल में क्या मापा गया।
2. **Model और तारीख़ जाँचें।** कौन-से models, कौन-सा task, कौन-सा साल। एक model परिवार के बारे में 2022 की सलाह उस model का वर्णन नहीं कर सकती जिसे आप आज call करते हैं, और vendor की गाइड उसी vendor के models का वर्णन करती है।
3. **जाँचें कि दावा क्या कवर करता है।** तथ्यात्मक सवालों पर accuracy, tone नहीं है। छोटे classification पर नतीजा, मसौदा लिखने पर नतीजा नहीं है।
4. **अपने regression set पर परखें।** अगर स्रोत और आपका मामला अलग हो सकते हैं, तो जो नतीजा फ़ैसला करता है वह आपका अपना है (पाठ 18 और 19)।

नीचे के हर मामले में यही लागू होता है। इनमें से कोई यह नहीं कहता कि आम सलाह हमेशा ग़लत है। हर एक बताता है कि primary source क्या समर्थित करता है।

### मामला 1: "Model को role दें"

Anthropic की गाइड कहती है: "Setting a role in the system prompt focuses Claude's behavior and tone for your use case" ([Anthropic: prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices))। Zheng et al. ने परखा कि क्या personas वस्तुनिष्ठ tasks पर मदद करते हैं। उन्होंने 6 प्रकार के पारस्परिक संबंधों और 8 विशेषज्ञता क्षेत्रों में 162 roles चुने और LLMs के 4 परिवारों को 2,410 तथ्यात्मक सवालों पर परखा। उनकी खोज: persona जोड़ना "does not improve model performance across a range of questions compared to the control setting where no persona is added"। Persona का लिंग, प्रकार और क्षेत्र फिर भी accuracy बदल सकते हैं, इसलिए असर "can be largely random" है, और किसी सवाल के लिए सबसे अच्छा persona अपने-आप चुनना "often no better than random selection" था।

दोनों एक-दूसरे का खंडन नहीं करते, क्योंकि वे अलग चीज़ें दावा करते हैं: tone और व्यवहार बनाम तथ्यात्मक सवालों पर accuracy। जो पढ़ाई दोनों के बाद बचती है: जहाँ आप आवाज़ या दायरा चाहें वहाँ role रखें, उम्मीद न करें कि वह तथ्यों को ज़्यादा सटीक बनाएगा, और जब कोई कहे कि persona "accuracy सुधारता है" तो परीक्षण माँगें। पेपर के models 2023 के हैं, इसलिए उत्तर का तारीख़ वाला हिस्सा है "उन models और सवालों के लिए"।

### मामला 2: "Think step by step"

यह वाक्यांश zero-shot reasoning के नतीजे (Kojima et al., 2022, [संसाधन](../RESOURCES.md) में सूचीबद्ध) से आता है, जो built-in thinking वाले models से पहले का है। जो model उत्तर से पहले सोचता है, उसके लिए मौजूदा Anthropic गाइड उलटी आदत की सिफ़ारिश करती है: "A prompt like 'think thoroughly' often produces better reasoning than a hand-written step-by-step plan", और कई नामित models के लिए वह built-in thinking पर निर्भर रहने को कहती है, क्योंकि model से अपनी reasoning लिखने को कहने वाला prompt "may be declined" हो सकता है। वह manual chain-of-thought को सिर्फ़ तब के fallback के रूप में रखती है जब thinking बंद हो। पाठ 10 इसका तंत्र कवर करता है।

इसलिए जिस विवाद को सुलझाना है वह है "कौन-सा model, thinking चालू या बंद के साथ"। उत्तर model के अपने दस्तावेज़ से आता है, तारीख़ के साथ, और फिर आपके regression set से।

### मामला 3: "ज़रूरी नियमों पर चिल्लाएँ"

Capital letters में ज़ोर देना किसी नियम पर बल देने का आम तरीक़ा है। Anthropic की गाइड कहती है कि बाद के models "more responsive to the system prompt than previous models" हैं, और कि undertriggering घटाने के लिए लिखे prompts "may now overtrigger" कर सकते हैं। उसका सुधार: "dial back any aggressive language", इसलिए जहाँ आपने "CRITICAL: You MUST use this tool when..." लिखा होता, वहाँ "Use this tool when..." इस्तेमाल करें। गाइड इसके लिए Claude Opus 4.5 और Claude Opus 4.6 का नाम लेती है, और उदाहरण tool के इस्तेमाल के बारे में है।

दायरा पढ़ें। दावा दो नामित models और tools को चलाने के बारे में है, "capitals कभी काम नहीं करते" के बारे में नहीं। पुराने model के लिए लिखा prompt जो नए पर ले जाया गया हो, वह मामला है जहाँ विरासत में मिले ज़ोर को परखना बनता है, सादे रूप को तुलना के रूप में रखकर। पाठ 23 उसी कारण से ज़ोरदार शब्दावली को सवाल करने लायक़ क़ीमत के रूप में गिनाता है।

### मामला 4: "ज़्यादा examples बेहतर हैं"

Anthropic की गाइड 3 से 5 examples शामिल करने और उन्हें प्रासंगिक, विविध और संरचित बनाने की सिफ़ारिश करती है। दो पेपर वह जोड़ते हैं जो गिनती नहीं कह सकती। Lu et al. दिखाते हैं कि "the order in which the samples are provided can make the difference between near state-of-the-art and random guess performance", कि यह "across model sizes" सही है, और कि एक model के लिए अच्छा permutation दूसरे पर transferable नहीं है। Sclar et al. पाते हैं कि formatting की संवेदनशीलता "remains even when increasing... the number of few-shot examples"।

इसलिए गिनती वह उपाय नहीं है जो नारा जताता है। वही examples दूसरे क्रम में, या अलग format में, उतना ही मायने रख सकते हैं जितना और जोड़ना, और एक model पर ट्यून किया क्रम अगले पर नहीं जाता। क्रम और format को परखने लायक variables मानें, जो पाठ 7 का निष्कर्ष और मज़बूत बनाकर कहना है।

### बातचीत में इसे सुलझाना

दो इंजीनियर एक ही पेपर का हवाला देते हैं। ज़्यादा आत्मविश्वासी को न चुनें, और बीच का रास्ता भी न निकालें। चार चीज़ें माँगें: अंश, models और तारीख़, क्या मापा गया, और regression set पर एक run। अगर दावा और आपका मामला मेल खाते हैं, तो स्रोत लागू होता है। अगर नहीं, तो स्रोत आपके मामले के बारे में प्रमाण नहीं है, और run है।

## अभ्यास

1. ▢ एक सहकर्मी कहता है "Zheng et al. ने साबित कर दिया कि roles बेकार हैं, इसलिए हर system prompt से role वाली पंक्ति हटा दो।" पेपर क्या समर्थित करता है, और आप क्या करेंगे?

<details markdown="1"><summary>जाँचें</summary>

पेपर बताता है कि persona जोड़ने से LLMs के 4 परिवारों में 2,410 तथ्यात्मक सवालों पर बिना persona की तुलना में performance नहीं सुधरा। वह tone या दायरे को नहीं मापता, और वह बताता है कि असर persona के हिसाब से बदलता है, यह नहीं कि हर मामले में शून्य है। इसलिए "उन models पर तथ्यात्मक accuracy के लिए बेकार" समर्थित है, और "हर जगह हटाओ" नहीं। Prompt को role के साथ और उसके बिना regression set पर चलाएँ और पंक्ति सिर्फ़ वहाँ हटाएँ जहाँ संख्याएँ कुछ न दिखाएँ, क्योंकि हटाने से tokens भी बचते हैं।

</details>

2. ▢ आपको एक prompt विरासत में मिलता है जो कहता है "CRITICAL: you MUST call the search tool before every answer", पुराने model पर ट्यून किया हुआ, और नया model अब मामूली सवालों के लिए भी search करता है। कौन-सी कार्रवाई स्रोत को मानती है?

    - a) पुराने शब्दों के सामने सादा "Use the search tool when" रूप परखें
    - b) दूसरा capital वाला नियम जोड़ें जो उसे मामूली बातों के लिए search करने से रोके
    - c) पुराने model पर लौटें और शब्द वही रखें
    - d) Instruction हटा दें और उम्मीद करें कि नया model नीति ख़ुद समझ लेगा

<details markdown="1"><summary>जाँचें</summary>

a)। Anthropic की गाइड नामित नए models के लिए इस overtriggering का वर्णन करती है और आक्रामक भाषा घटाने की सलाह देती है, इसलिए सादे शब्द उम्मीदवार हैं, और regression set फ़ैसला करता है। b) ज़ोर पर ज़ोर चढ़ाता है। c) नए model को फेंक देता है। d) वह नीति हटा देता है जिसकी आपको ज़रूरत हो सकती है, और बिना परखे।

</details>

3. ▢ एक blog post कहती है "हर prompt में 'think step by step' जोड़ें।" आप built-in thinking चालू वाला model इस्तेमाल करते हैं। prompt को छूने से पहले चलाई जाने वाली पहली दो जाँचें बताएँ।

<details markdown="1"><summary>जाँचें</summary>

पहली, मूल नतीजा खोजें और देखें कि वह कौन-से models और साल कवर करता है: zero-shot reasoning वाला पेपर 2022 का है, built-in thinking वाले models से पहले का। दूसरी, अपने model का दस्तावेज़ पढ़ें: Anthropic की गाइड thinking चालू होने पर निर्देशात्मक चरणों के बजाय सामान्य instructions की सिफ़ारिश करती है, और कहती है कि कुछ नामित models पर लिखी हुई reasoning माँगना ठुकराया जा सकता है। फिर regression set पर उस वाक्यांश के साथ और उसके बिना परखें, क्योंकि गाइड एक vendor का अपने models का वृत्तांत है।

</details>

4. ▢ आपके prompt में पाँच examples हैं जिनमें दुर्लभ label आख़िर में है, और उन्हें फेंटने पर accuracy बदलती है। किस स्रोत ने इसकी भविष्यवाणी की थी, और 3 से 5 examples इस्तेमाल करने की सलाह के बारे में यह क्या बदलता है?

<details markdown="1"><summary>जाँचें</summary>

Lu et al. दिखाते हैं कि अकेला examples का क्रम नतीजों को state of the art के क़रीब से संयोग के क़रीब तक हिला सकता है, और कि एक model के लिए अच्छा क्रम दूसरे पर transferable नहीं है। गिनती वाली सलाह शुरुआती बिंदु बनी रहती है, पर काफ़ी नहीं है: क्रम और format prompt के व्यवहार का हिस्सा हैं, इसलिए जो क्रम pass हुआ उसे दर्ज करें और model snapshot बदलने पर दोबारा परखें (पाठ 16)।

</details>

5. ▢ Design review में "personas accuracy सुधारते हैं" को मानने से पहले आप जो तीन सवाल पूछेंगे उन्हें लिखें, और वह एक नतीजा जो आपके product के लिए इसे सुलझाएगा।

<details markdown="1"><summary>जाँचें</summary>

यह किन models और किन सवालों पर मापा गया था? क्या baseline बिना persona वाला prompt था? क्या माप accuracy था या tone? आपके product के लिए जो इसे सुलझाता है वह persona के साथ और उसके बिना prompt की आपके regression set पर paired तुलना है, अंतर को हर-run के noise के सामने परखते हुए (पाठ 19)। जो स्रोत आपकी किसी शर्त से मेल नहीं खाता वह पृष्ठभूमि है, प्रमाण नहीं।

</details>

## असली दुनिया का अभ्यास

- [ ] Prompting की कोई एक सलाह चुनें जिसे आप उसका स्रोत जाने बिना मानते हैं और उसे किसी पेपर या vendor दस्तावेज़ तक पहुँचाएँ। लिखें कि models, तारीख़ और क्या मापा गया।
- [ ] अपने संभाले किसी prompt में एक persona या ज़ोरदार instruction लें और वह दो-prompt तुलना लिखें जो उसे परखेगी, भले ही आप उसे अभी न चलाएँ।
- [ ] कल: उस तुलना को regression set पर चलाएँ, या उसके लिए पाँच cases का ख़ाका बनाएँ, और नतीजा prompt के बदलाव-नोट्स में दर्ज करें।

## आगे बढ़ने के लिए

- [Prompt Review Checklist](../reference/prompt-review-checklist.md)
- [Paper: "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models", Zheng et al., 2023](https://arxiv.org/abs/2311.10054)
- [Docs: "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Paper: "Fantastically Ordered Prompts and Where to Find Them", Lu et al., 2021](https://arxiv.org/abs/2104.08786)
- [संसाधन](../RESOURCES.md)

---

यह track का अंत है, और जिस आदत के लिए इसे बनाया गया वह इसी पाठ की है: prompt एक model के बारे में दावा है, इसलिए खोजें कि दावा कहाँ से आता है, जाँचें कि उसने क्या कवर किया, और उसे किसी और के सामने बचाने से पहले अपने cases पर परखें।

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
