---
title: "27. Fine-Tuning कब न करें"
description: "Fine-tuning सूची में छठे नंबर पर है, और यह क्यों मायने रखता है"
type: lesson
---

# पाठ 27. Fine-Tuning कब न करें

**मिशन से संबंध:** मिशन यहीं ख़त्म होता है: *"और जो prompting या retrieval के पक्ष में विश्वसनीय ढंग से तर्क दे सके जब वे काम को बेहतर करते हों।"* वरिष्ठ कौशल काम को मना करना है।
**मुख्य स्रोत:** [दस्तावेज़: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
**पूर्व-आवश्यकताएँ:** हर पिछला पाठ, क्योंकि यह पाठ संश्लेषण है।

## वार्म-अप

1. ▢ कौन-सा inference चरण bandwidth-bound है, और यह छोटे models के पक्ष में क्यों जाता है?

<details markdown="1"><summary>जाँचें</summary>

Decode। हर step एक token बनाने के लिए सारे weights पढ़ता है, इसलिए गति memory bandwidth के साथ चलती है और छोटा model लगभग अपने आकार के अनुपात में तेज़ है।

</details>

2. ▢ चारों regression श्रेणियों के नाम बताएँ।

<details markdown="1"><summary>जाँचें</summary>

सामान्य instruction following, format और व्यवहार का अनुपालन, safety और इनकार का व्यवहार, निकटवर्ती बिना-train की क्षमता।

</details>

3. ▢ वह baseline क्या है जिसे नए PEFT variant को हराना होगा?

<details markdown="1"><summary>जाँचें</summary>

पर्याप्त rank पर सभी linear layers में LoRA, tune किए हुए learning rate के साथ।

</details>

## यह जानें

### फ़ैसला, क्रम से

इस सूची में नीचे की ओर काम करें। पहली उस पंक्ति पर रुकें जो आपकी समस्या हल करे।

| तरीक़ा | क्या हल करता है | क़ीमत |
|---|---|---|
| बेहतर prompt | ज़्यादातर format और व्यवहार की समस्याएँ | मिनट |
| Few-shot examples | Format की एकरूपता, output का आकार | प्रति अनुरोध prompt tokens |
| Retrieval | गुम या बदलता ज्ञान | Retrieval infrastructure |
| Tool use | गणना, lookup, क्रियाएँ | Tool infrastructure |
| Constrained decoding | Schema validity, पूर्ण रूप से | Serving support |
| **Fine-tuning** | एकसार व्यवहार, prompt की लागत, छोटे model का पर्याप्त होना | Data, evaluation, रखरखाव |
| Full fine-tuning | बहुत बड़े व्यवहारिक बदलाव | हर चीज़ की काफ़ी ज़्यादा मात्रा |

Fine-tuning छठे नंबर पर है। **ज़्यादातर लोग जो fine-tune करना चाहते हैं उनकी समस्या पहली पाँच में से किसी एक से हल होती है, तेज़ी से और ज़्यादा भरोसेमंद ढंग से।** पंक्तियाँ एक से पाँच ख़त्म किए बिना पंक्ति छह तक पहुँचना इस क्षेत्र की सबसे आम महँगी भूल है।

ख़ासकर ध्यान दें कि **constrained decoding schema validity को पूरी तरह हल करती है**, क्योंकि grammar-constrained generation invalid JSON बना ही नहीं सकती। अगर आपकी पूरी समस्या बिगड़ा output है, तो आपको कुछ train करने की ज़रूरत नहीं।

### तीन सवाल जो तय करते हैं

**1. समस्या ज्ञान की है या व्यवहार की?**

ज्ञान, यानी तथ्य और documents और वह सब जो बदलता है, retrieval का काम है। Fine-tuning तथ्य अविश्वसनीय ढंग से, असत्यापनीय रूप से डालती है, और पुराना पड़ने पर retraining चाहिए। Retrieval सटीक है, उद्धरण-योग्य है, और एक document संपादित करके update होता है।

व्यवहार, यानी format और tone और संरचना और एकरूपता और फ़ैसले की सीमा, fine-tuning का काम है। यहीं वह सचमुच उत्कृष्ट है और कोई और चीज़ उतनी अच्छी नहीं।

जाल: "model को हमारे product के बारे में पता नहीं" training की समस्या जैसी सुनाई देती है और retrieval की समस्या है। "मैं जैसे भी prompt करूँ, model हमारी house style में एकसार उत्तर नहीं देता" prompting की समस्या जैसी सुनाई देती है और training की समस्या है।

**2. क्या आपने सचमुच prompting ख़त्म की है?**

"कुछ prompts आज़माए" नहीं। ख़त्म की: व्यवस्थित iteration, few-shot examples, संरचित system prompt, और **उसी held-out सेट पर मापा जिसे आप fine-tune को आँकने के लिए इस्तेमाल करेंगे।** ज़्यादातर यह दावे कि prompting विफल रही, इस बात के दावे हैं कि मुट्ठी-भर बिना-मापे प्रयास विफल रहे।

अगर आप अपने held-out सेट पर prompting का score नहीं बता सकते, तो आपके पास baseline नहीं है, और baseline के बिना आप यह नहीं दिखा सकते कि fine-tune ने मदद की।

**3. क्या आप इसे सँभालेंगे?**

Fine-tune जीवित artifact है। Base models की जगह नए आ जाते हैं, ज़रूरतें खिसकती हैं, distributions बहकते हैं, evaluations को update चाहिए। अगर कोई इसका मालिक नहीं, तो आप ऐसी चीज़ बना रहे हैं जो काम करती दिखते हुए चुपचाप सड़ेगी, और पुराना पड़ा fine-tune बिना fine-tune से बदतर है, क्योंकि उस पर भरोसा किया जाता है।

### जब fine-tuning साफ़ तौर पर सही हो

तरीक़े के साथ न्याय करने के लिए, ये असली और आम हैं:

- **ऊँचा volume और लंबा prompt।** Prompt की सामग्री को weights में ले जाना हर अनुरोध पर ख़ुद को वसूल करता है (पाठ 26)।
- **तब छोटा model काफ़ी हो सकता है।** सबसे मज़बूत मामला, क्योंकि यह लागत और latency को साथ घटाता है।
- **ऐसा व्यवहार जो prompting से नहीं मानता।** कोई tone, format, या फ़ैसले की सीमा जिसे model आप जैसे भी पूछें एकसार नहीं रखेगा।
- **ढेर सारे examples वाला संकरा task।** Classification, extraction, संरचित रूपांतरण: fine-tuning बढ़िया है और अक्सर कहीं बड़े prompted model को हराती है।
- **Latency-अहम रास्ते।** छोटे prompts और छोटे models, दोनों सीधे मदद करते हैं।
- **Domain-विशिष्ट notation या syntax** जो pretraining में सचमुच कम दर्शाई गई हो।

### चुनने के बजाय मिलाना

"fine-tune करें या retrieve करें" वाला ढाँचा आम तौर पर ग़लत है। सबसे मज़बूत systems अलग-अलग कामों के लिए दोनों करते हैं:

**Retrieval तथ्य देता है। Fine-tuning सिखाती है कि उनका क्या करना है.**

ऐसा model जो retrieved context को अच्छी तरह इस्तेमाल करने के लिए fine-tune किया गया हो, उसका हवाला देते हुए, उसका सम्मान करते हुए, अपर्याप्त होने पर मान लेते हुए और उसके आगे गढ़ने से मना करते हुए, और retrieval जो ताज़ा सटीक तथ्य दे, दोनों में से अकेले से बेहतर है। वह एक architecture है, और उसे पहचानना इस फ़ैसले का वरिष्ठ रूप है।

### क्षमता पर सधी हुई स्थिति

आपने यहाँ बारीक नज़रिया कमाया है, इसलिए उसे सटीक रखें।

पुराना ढाँचा, "LoRA सस्ता अनुमान है, full fine-tuning असली चीज़ है", बड़े पैमाने पर अप्रचलित है। सभी linear layers पर पर्याप्त rank और ठीक से tune किए learning rate के साथ, LoRA सामान्य supervised fine-tuning कामों पर full fine-tuning की बराबरी करता है। **ज़्यादातर लोग जिस व्यवस्था में काम करते हैं उसके लिए क्षमता का फ़ासला मोटे तौर पर पट चुका है।**

जिसका मतलब है: अगर आपने fine-tune करना तय किया है, तो adapters लगभग निश्चित रूप से सही तरीक़ा हैं। Full fine-tuning बहुत बड़े व्यवहारिक बदलावों के लिए है, बड़े पैमाने पर नए domain या भाषा पर continued pretraining के लिए, या ऐसे शोध के लिए जहाँ आपको पूरा parameter space चाहिए। बचा सवाल "adapter या full" नहीं बल्कि "क्या इसे train करना भी चाहिए" है।

### अच्छा विवेक कैसा सुनाई देता है

> "बताई गई सारी विफलताएँ तथ्यों के पुराने पड़ने की हैं, इसलिए यह retrieval है, training नहीं। मुझे पहले held-out सेट पर prompted baseline मापने दें। अगर retrieval के बाद बची समस्या दिन में 40,000 अनुरोधों पर format की एकरूपता है, तो 3B model पर rank-32 all-linear adapter की लागत निकालना सार्थक है, उस व्यक्ति समेत जो छह महीने में उसे retrain करेगा। Ship करने से पहले मैं safety और सामान्य instruction following को ढकने वाला regression suite चाहूँगा, क्योंकि हम एक instruct model को adapt कर रहे होंगे।"

उसमें कुछ भी ऐसा तथ्य नहीं जो आपने ढूँढा हो। यह उस तर्क का आकार है जिसके लिए यह workspace था।

## अभ्यास

1. ▢ "हमारे support bot को इस तिमाही लॉन्च हुए products के बारे में पता नहीं।" Fine-tune करें या नहीं?

<details markdown="1"><summary>जाँचें</summary>

नहीं। यह ज्ञान है, और जो ज्ञान हर तिमाही बदलता है वह fine-tuning के लिए सबसे बुरा संभव मेल है, जो तथ्य अविश्वसनीय ढंग से डालती है और तुरंत पुरानी पड़ जाती है।

Retrieval: सटीक, उद्धरण-योग्य, catalogue संपादित करके update होने वाला। Fine-tuning अलग से bot को retrieved product data को अच्छी तरह *इस्तेमाल करना* सिखाने के लिए सार्थक हो सकती है।

</details>

2. ▢ "Prompting काम नहीं आई।" आप क्या पूछते हैं?

<details markdown="1"><summary>जाँचें</summary>

क्या मापा गया, किस held-out सेट पर, किस score के साथ। और: क्या few-shot examples आज़माए गए, क्या संरचित system prompt आज़माया गया, क्या format की समस्या के लिए constrained decoding आज़माई गई।

मापे गए prompted baseline के बिना fine-tune की तुलना करने को कुछ नहीं, इसलिए आप सुधार दिखा नहीं सकते भले आप उसे हासिल कर लें।

</details>

3. ▢ आपकी पूरी समस्या यह है कि 12% outputs invalid JSON हैं। सबसे सस्ता इलाज?

<details markdown="1"><summary>जाँचें</summary>

Constrained decoding। Grammar-constrained generation invalid JSON बना ही नहीं सकती, और यह serving-पक्ष का बदलाव है जिसमें बिल्कुल training नहीं।

Fine-tuning 99% validity तक पहुँच सकती है। Constrained decoding बनावट से 100% पर पहुँचती है। Fine-tune तभी करें जब *values* भी ग़लत हों, जो अलग समस्या है।

</details>

4. ▢ कौन-सी स्थिति fine-tuning के सबसे ज़्यादा पक्ष में है?

    - a) Model को आपके आंतरिक दस्तावेज़ों का ज्ञान नहीं
    - b) ऊँचा अनुरोध-volume और बहुत लंबा system prompt
    - c) Model कभी-कभी output में अंकगणित की ग़लतियाँ करता है
    - d) Model को इसी हफ़्ते की घटनाओं की जानकारी चाहिए

<details markdown="1"><summary>जाँचें</summary>

**b)** ऊँचा अनुरोध-volume और बहुत लंबा system prompt।

Prompt की सामग्री को weights में ले जाना हर अनुरोध का prefill ख़र्च हटाता है, और बचत volume के साथ scale होती है। (a) और (d) retrieval हैं। (c) tool use है: उसे calculator दें।

</details>

5. ▢ क्या LoRA, full fine-tuning के मुक़ाबले समझौता है?

<details markdown="1"><summary>जाँचें</summary>

ज़्यादातर नहीं, उस व्यवस्था में जिसमें अधिकांश लोग काम करते हैं। सभी linear layers पर पर्याप्त rank और tune किए learning rate के साथ, LoRA सामान्य supervised fine-tuning कामों पर full fine-tuning की बराबरी करता है।

Full fine-tuning बहुत बड़े व्यवहारिक बदलावों, बड़े पैमाने पर continued pretraining, या पूरे parameter space की ज़रूरत वाले शोध के लिए उपयुक्त रहती है। साधारण task adaptation के लिए, adapters सही तरीक़ा हैं, रियायत नहीं।

</details>

6. ▢ आपका retrieval काम कर रहा है और model फिर भी retrieved context को अनदेखा करके जवाब गढ़ता है। अब क्या?

<details markdown="1"><summary>जाँचें</summary>

अब fine-tuning अच्छी तरह प्रेरित है, और यह तरीक़ों के बीच चुनाव के बजाय मिला-जुला architecture है।

समस्या व्यवहार की है: दिए गए context में टिकना, उसका सम्मान करना, उसका हवाला देना, और अपर्याप्त होने पर मना करना। Retrieval तथ्य देता है; training सिखाती है कि उनका क्या करना है। Dataset असली retrieved contexts से बनाएँ, सही grounded responses के साथ, उन मामलों समेत जहाँ सही उत्तर है "दिया गया context इसे नहीं ढकता"।

</details>

## असली दुनिया का अभ्यास

- [ ] कोई fine-tuning प्रस्ताव लें, आपका या किसी और का, और उस पर तीनों सवाल लगाएँ। एक अनुच्छेद का फ़ैसला लिखें।
- [ ] अपने held-out सेट पर prompted baseline ठीक से मापें। कुछ भी train करने से पहले संख्या दर्ज करें।
- [ ] एक fine-tune के पूरे जीवनकाल की लागत निकालें: data, evaluation, serving, retraining, स्वामित्व। बचत से तुलना करें।
- [ ] कल: ऐसा मामला ढूँढें जहाँ आप fine-tune करने से मना करेंगे, और विकल्प के पक्ष में तर्क एक ऐसे अनुच्छेद में लिखें जिस पर कोई और कार्रवाई कर सके।

## आगे बढ़ने के लिए

- [दस्तावेज़: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
- [पेपर: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", Lewis et al., arXiv:2005.11401](https://arxiv.org/abs/2005.11401)
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/): उसमें वे मामले खोजें जहाँ practitioners ने fine-tuning के विरुद्ध फ़ैसला किया, और उन्होंने इसके बदले क्या ship किया
- [failure modes शीट](../reference/failure-modes.md), [LoRA hyperparameters शीट](../reference/lora-hyperparameters.md), [memory budget शीट](../reference/memory-budget.md)

---

यही पूरी रूपरेखा है। यहाँ से आगे काम असली tasks पर अभ्यास है, और मिशन की आख़िरी पंक्ति वही है जिसे रखना है: fine-tuning के *विरुद्ध* विश्वसनीय ढंग से तर्क दे पाना ही उसके *पक्ष* के तर्क को किसी काम का बनाता है।

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
