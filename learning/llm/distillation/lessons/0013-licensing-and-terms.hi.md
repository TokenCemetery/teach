---
title: "13. Licensing और Terms"
description: "किसी provider के terms और किसी open model का license उसके outputs के साथ आपको क्या करने देते हैं"
type: lesson
---

# पाठ 13. Licensing और Terms

**मिशन से संबंध:** मिशन आपसे माँगता है कि आप जाँचें कि distillation set का इस्तेमाल अनुमत है, यानी teacher से data generate करने से पहले उन दस्तावेज़ों को पढ़ें जो उसे नियंत्रित करते हैं, और जो पाया उसे दर्ज करें।
**मुख्य स्रोत:** [शर्तें: "Terms of Use", OpenAI](https://openai.com/policies/row-terms-of-use/)
**पूर्व-आवश्यकताएँ:** [पाठ 12](0012-filtering-synthetic-data.md), [पाठ 10](0010-distilling-from-generated-data.md), [Synthetic data](../GLOSSARY.md), [Teacher](../GLOSSARY.md)

यह पाठ क़ानूनी सलाह नहीं है। यह दो दस्तावेज़ पढ़ता है, उनमें जो लिखा है उसे उद्धृत करता है, और क्या देखना है इसकी एक checklist देता है। यह इस बारे में कोई दावा नहीं करता कि कोई दस्तावेज़ आपके मामले के लिए क्या मायने रखता है, कोई clause लागू करने योग्य है या नहीं, या कौन-सा दस्तावेज़ आप पर लागू होता है। Terms और licenses बिना ऐसे version के बदलते हैं जिसे कोई पाठ pin कर सके, इसलिए नीचे के उद्धरणों पर वह तारीख़ है जब वे पढ़े गए थे, और किसी पर भी भरोसा करने से पहले आपको मौजूदा text पढ़ना चाहिए। असली फ़ैसले के लिए किसी वकील से पूछें।

## वार्म-अप

1. ▢ phi-1 के लेखकों ने अपने exercises को HumanEval के विरुद्ध n-grams, embeddings और AST matching से prune किया। वे n-gram overlap पर ही क्यों नहीं रुके?

<details markdown="1"><summary>जाँचें</summary>

13-gram जाँच ने सिर्फ़ चार सवाल चिह्नित किए, सब false positives, और वह समान code ढूँढने के लिए बहुत मोटी थी, इसलिए उन्होंने embedding और AST तुलना जोड़ी (पाठ 12)।

</details>

2. ▢ Alpaca का data text-davinci-003 से आया और उसका model LLaMA 7B से fine-tune हुआ। इसलिए वह किन दो चीज़ों पर निर्भर है जिनका मालिक या नियंत्रक कोई और है?

<details markdown="1"><summary>जाँचें</summary>

वह teacher जिसने data generate किया (OpenAI का text-davinci-003, OpenAI के terms के तहत) और base model (LLaMA, उसके license के तहत)। दोनों student के inputs हैं, और हर एक अपनी शर्तों के साथ आता है (पाठ 10)।

</details>

3. ▢ उस filter का नाम बताएँ जो generate किए उत्तर को ground truth से नियम द्वारा जाँचता है, और एक चीज़ जो वह नहीं आँक सकता।

<details markdown="1"><summary>जाँचें</summary>

Checker के साथ rejection sampling, जहाँ सिर्फ़ वे samples रखे जाते हैं जो पास हों। वह खुले-अंत वाले उत्तर या style नहीं आँक सकता, जहाँ जाँचने के लिए कुछ नहीं होता (पाठ 12)।

</details>

## यह जानें

### तीन दस्तावेज़, तीन सवाल

जब आप किसी teacher से data generate करते हैं तो आप तीन अलग तरह के दस्तावेज़ों तक से बँधे हो सकते हैं, और हर एक अलग सवाल का जवाब देता है।

| दस्तावेज़ | वह किस सवाल का जवाब देता है |
|---|---|
| Hosted model के लिए provider के terms of use | इस सेवा से मिले outputs के साथ मैं क्या कर सकता हूँ? |
| Open weights का license | मैं model के साथ, और उससे जो बनता है उसके साथ, क्या कर सकता हूँ? |
| Prompts और seed data का license या terms | जो inputs मैंने उसे खिलाए, और उनसे जो data मैंने बनाया, उसके साथ मैं क्या कर सकता हूँ? |

हर एक अपनी तारीख़ और दायरे वाला अलग text है। एक को पढ़ने से आपको नहीं पता चलता कि दूसरा क्या कहता है।

### Hosted provider के terms क्या कहते हैं

बाक़ी दुनिया के लिए OpenAI के Terms of Use, जो 1 जनवरी 2026 से प्रभावी हैं, उन चीज़ों की सूची देते हैं जो उपयोगकर्ता नहीं कर सकता। उनमें यह पंक्ति है, जैसी इस track को लिखते समय, अक्टूबर 2026 में, पढ़ी गई थी। Site scripted पढ़ने को रोकती है, इसलिए पेज को browser में दोबारा जाँचें (मूल अंग्रेज़ी उद्धरण):

> "Use Output to develop models that compete with OpenAI."

तीन बातें ध्यान दें, और इससे ज़्यादा नहीं। वाक्य निषिद्ध उपयोगों वाले भाग में है। वह ऐसे models विकसित करने की बात करता है जो OpenAI से होड़ करते हैं, जो किसी भी model को विकसित करने से संकरी बात है। और यह एक दस्तावेज़ है: आपका उपयोग किसी दूसरे edition या API या enterprise सेवा के अलग अनुबंध के तहत आ सकता है, और इस पाठ ने उन्हें नहीं पढ़ा है।

### Open-weights license क्या कहता है

Meta का Llama 3.1 Community License Agreement section 1.b.i (Redistribution and Use) में कहता है, जैसा 17 अक्टूबर 2026 को repository के text से पढ़ा गया (मूल अंग्रेज़ी उद्धरण):

> "If you use the Llama Materials or any outputs or results of the Llama Materials to create, train, fine tune, or otherwise improve an AI model, which is distributed or made available, you shall also include “Llama” at the beginning of any such AI model name."

उसी paragraph में यह भी ज़रूरी है कि अगर आप Llama Materials, या उन्हें रखने वाला कोई product या सेवा, जिसमें दूसरा AI model भी शामिल है, distribute करते हैं, तो आप अनुबंध की एक प्रति दें और किसी संबंधित website, user interface, blogpost, about page या product documentation पर "Built with Llama" प्रमुखता से दिखाएँ। अलग से, license कहता है कि Llama Materials का उपयोग लागू क़ानूनों और एक Acceptable Use Policy का पालन करे जिसे वह संदर्भ से शामिल करता है।

Text, outputs को इस तरह इस्तेमाल करने पर model के नाम के बारे में एक शर्त जोड़ता है, जब नतीजे वाला model distribute किया जाए या उपलब्ध कराया जाए। यह पाठ शब्दों से आगे कोई दावा नहीं करता। दूसरे Llama versions और दूसरे open models के अपने licenses हैं, और कुछ अलग बातें कहते हैं।

### एक project ने इससे कैसे निपटा

Alpaca के लेखक कहते हैं कि उनका model सिर्फ़ academic research के लिए है और कोई भी व्यावसायिक उपयोग निषिद्ध है, और तीन कारक देते हैं: LLaMA का license non-commercial है, इसलिए वे उसे विरासत में पाते हैं; instruction data text-davinci-003 से आता है, जिसके terms of use, वे कहते हैं, OpenAI से होड़ करने वाले models विकसित करने की मनाही करते हैं; और उन्होंने पर्याप्त सुरक्षा उपाय नहीं बनाए थे। वे यह भी लिखते हैं कि उनका demo non-commercial उपयोगों और उन उपयोगों तक सीमित था जो LLaMA के license का पालन करते हैं (Alpaca blog post, "Overview" और "Release decision")। ध्यान दें कि उन्होंने क्या किया: उन्होंने पाबंदी के हर स्रोत का नाम लिया और release को उससे बाँधा। यह वह आदत है जिसे अपनाना चाहिए, आपके अपने दस्तावेज़ जो भी कहें।

### Generate करने से पहले: एक checklist

इस क्रम में पढ़ें और दर्ज करें:

1. **Teacher के terms.** वह ठीक-ठीक दस्तावेज़ ढूँढें जो आपके model तक पहुँचने के तरीक़े पर लागू होता है। उसका नाम, URL, तारीख़ या version, और दूसरे models को train करने के लिए outputs इस्तेमाल करने के बारे में वाक्य नोट करें।
2. **Weights का license, अगर teacher open है।** Version, outputs पर training के बारे में कोई clause, कोई नामकरण या attribution की ज़रूरत, और जो भी use policy वह शामिल करता है, नोट करें।
3. **Prompts और seed data.** आप teacher को जो भी खिलाते हैं, जैसे seed tasks, documents या scrape किया text, उसका license inputs को नियंत्रित करता है। उसे teacher से अलग जाँचें।
4. **नामकरण और attribution.** अगर कोई दस्तावेज़ model के नाम का prefix या credit पंक्ति माँगता है, तो अभी तय करें, model के नाम पाने से पहले।
5. **Student कैसे इस्तेमाल और साझा होगा.** कई clauses इस पर निर्भर करते हैं कि model distribute किया गया, उपलब्ध कराया गया या बेचा गया, और वह किससे होड़ करता है। अपना इरादा किया उपयोग लिख लें।
6. **तारीख़.** दर्ज करें कि आपने हर दस्तावेज़ कब पढ़ा और हर batch कब generate किया, क्योंकि generation के समय लागू terms आज के terms से अलग हो सकते हैं।

इस रिकॉर्ड को dataset के बग़ल में रखें, हर स्रोत की एक पंक्ति, ताकि "यह कहाँ से आया?" का एक साल बाद भी जवाब हो। हर example पर एक provenance field, जिसमें teacher, version और generation की तारीख़ हो, लगभग कुछ नहीं ख़र्चता।

```text
teacher: <name and version>
access: <hosted service or local weights>
terms read: <document, URL, date read, effective date if stated>
license: <name and version, if open weights>
prompt and seed data: <source, license>
naming or attribution duties: <list, or none found>
intended use: <research, internal, distributed, commercial>
generated on: <date range>
```

`<...>` वाली entries आपके अपने project के लिए भरे जाने वाले fields हैं।

### यह पाठ आपको क्या नहीं बता सकता

यह नहीं कह सकता कि कोई दिया हुआ project किसी clause को तोड़ता है या नहीं। यह पूरे text, तथ्यों, क्षेत्राधिकार और इस पर निर्भर करता है कि provider और license धारक क्या करेंगे, जिनमें से कुछ भी किसी उद्धरण में नहीं है। अभ्यास का मक़सद संकरा है: पक्का करें कि आपने दस्तावेज़ पढ़े हैं, जानते हैं कि वे शाब्दिक रूप से क्या कहते हैं, और उसका तारीख़ वाला रिकॉर्ड है।

## अभ्यास

1. ▢ एक टीम Llama 3.1 के outputs पर model fine-tune करती है और उसे उपलब्ध कराएगी। उद्धृत license text के अनुसार, नए model के नाम के बारे में क्या सच होना चाहिए?

    - a) वह "Llama" शब्द पर ख़त्म होना चाहिए
    - b) उसमें Llama का कोई ज़िक्र नहीं होना चाहिए
    - c) वह "Llama" शब्द से शुरू होना चाहिए
    - d) उसे licensor के पास पंजीकृत होना चाहिए

<details markdown="1"><summary>जाँचें</summary>

**c)** उद्धृत वाक्य कहता है AI model के नाम की शुरुआत में "Llama", उस model के लिए जो distribute किया या उपलब्ध कराया जाए। (a) स्थिति उलट देता है। (b) उसका उलटा है जो वह कहता है। (d) उद्धृत text में नहीं है।

</details>

2. ▢ उद्धृत OpenAI पंक्ति output को "OpenAI से होड़ करने वाले models विकसित करने" के लिए इस्तेमाल करने के बारे में है। एक सहकर्मी इसका सार "OpenAI अपने outputs पर training पर रोक लगाता है" बताता है। सार में क्या ग़लत है?

<details markdown="1"><summary>जाँचें</summary>

पंक्ति सार से संकरी है: वह ऐसे models विकसित करने के बारे में है जो OpenAI से होड़ करते हैं, सारे model विकास के बारे में नहीं। वह terms के एक edition से, एक तारीख़ पर, एक दस्तावेज़ भी है। Paraphrase की जगह वाक्य और उसकी तारीख़ उद्धृत करें, और जाँचें कि आपके पहुँच के रास्ते पर क्या लागू होता है। आपका project होड़ करता है या नहीं, यह क़ानूनी सवाल है जिसका जवाब यह पाठ नहीं देता।

</details>

3. ▢ आपने मार्च में hosted model से 200,000 examples generate किए। अक्टूबर में provider अपने terms बदल देता है। आप सबसे पहले क्या करते हैं?

<details markdown="1"><summary>जाँचें</summary>

नए terms और वे terms जो data generate करते समय लागू थे, दोनों provider के अपने पेज से पढ़ें, और देखें कि आपका रिकॉर्ड बताता है कि आपने कौन-सा version पढ़ा था। इसीलिए आपने तारीख़ लिखी थी। उसके आगे का सवाल क़ानूनी है कि पहले से generate हो चुके data पर कौन-से terms लागू होते हैं, इसलिए उसे किसी योग्य व्यक्ति के पास ले जाएँ, अंदाज़े के पास नहीं।

</details>

4. ▢ Alpaca के लेखक research-only release के लिए तीन कारक देते हैं। कौन-सा teacher के चुनाव पर निर्भर है, और कौन-सा student के base के चुनाव पर?

<details markdown="1"><summary>जाँचें</summary>

Teacher वाला कारक यह है कि data text-davinci-003 से आता है, जिसके terms OpenAI से होड़ करने वाले models विकसित करने की मनाही करते हैं। Base वाला कारक यह है कि LLaMA का license non-commercial है, इसलिए Alpaca उसे विरासत में पाता है। तीसरा, सुरक्षा उपायों की कमी, दोनों में से किसी के बारे में नहीं है।

</details>

5. ▢ आपके seed prompts किसी public dataset से आते हैं और आपका teacher permissive license वाला open model है। Student ship करने से पहले दो दस्तावेज़ों के नाम बताएँ जिन्हें आपको अब भी पढ़ना है।

<details markdown="1"><summary>जाँचें</summary>

Seed dataset का license, क्योंकि वह inputs को नियंत्रित करता है, और open model का अपना license, outputs पर training, नामकरण, attribution या use policy के किसी clause के लिए। उस किसी भी base model का license भी जाँचें जिससे student शुरू होता है। एक स्रोत पर permissive license बाक़ियों पर लागू नहीं होता।

</details>

## असली दुनिया का अभ्यास

- [ ] OpenAI Terms of Use और Llama 3.1 license खोलें और ऊपर उद्धृत ठीक वाक्य ढूँढें। हर एक की प्रभावी तारीख़ एक नोट में उतार लें।
- [ ] जो hub आप इस्तेमाल करते हैं उस पर कोई public synthetic dataset चुनें। ढूँढें कि वह किस teacher से generate हुआ बताता है, और dataset पेज पर बताए अनुसार उस teacher के terms या license लिख लें।
- [ ] कल: अपनी पसंद के teacher से बने किसी काल्पनिक dataset के लिए ऊपर का checklist रिकॉर्ड भरें, और हर उस field को चिह्नित करें जिसे आप मुख्य दस्तावेज़ से नहीं भर सके।

## आगे बढ़ने के लिए

- [Sequence और Synthetic Data शीट](../reference/sequence-and-synthetic-data.md)
- [शर्तें: "Terms of Use", OpenAI](https://openai.com/policies/row-terms-of-use/)
- [License: "Llama 3.1 Community License Agreement", Meta](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE)
- [लेख: "Alpaca: A Strong, Replicable Instruction-Following Model", Stanford CRFM, 2023](https://crfm.stanford.edu/2023/03/13/alpaca.html)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
