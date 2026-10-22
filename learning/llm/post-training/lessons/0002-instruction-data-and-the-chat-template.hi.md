---
title: "2. Instruction Data और Chat Template"
description: "एक special token बताता है कि prompt कहाँ ख़त्म होता है और उत्तर कहाँ शुरू, और यह सीमा training और serving के समय एक जैसी होनी चाहिए"
type: lesson
---

# पाठ 2. Instruction Data और Chat Template

**मिशन से संबंध:** "ऐसा SFT training loop लिखें जो non-assistant tokens पर loss को mask करे, और समझाएँ कि उस mask के बिना train किए chat model में क्या टूटता है" "सफलता कैसी दिखती है" का पहला बिंदु है। यह पाठ बताता है कि SFT data कैसा दिखता है और उसके हिस्से कैसे चिह्नित होते हैं; masking ख़ुद पाठ 3 का विषय है।
**मुख्य स्रोत:** [पेपर: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
**पूर्व-आवश्यकताएँ:** [पाठ 1](0001-what-post-training-buys.md)

## वार्म-अप

1. ▢ Alignment tax क्या है, और Ouyang et al. को क्या मिला जो उसे आंशिक रूप से संतुलित कर सकता था?

<details markdown="1"><summary>जाँचें</summary>

कुछ public NLP benchmarks पर प्रदर्शन में मापी गई गिरावट, जो post-training के alignment फ़ायदों के साथ आई। PPO updates को उन updates के साथ मिलाने (PPO-ptx) से, जो मूल pretraining data की likelihood बढ़ाते हैं, खोया हुआ ज़्यादातर प्रदर्शन लौट आया और preference फ़ायदे छोड़ने नहीं पड़े।

</details>

## यह जानें

### SFT data असल में कैसा दिखता है

**Supervised fine-tuning (SFT)** data prompt-और-उत्तर के जोड़ों का सेट है, ठीक वही आकार जो पाठ 1 के चरण 1 ने बताया था। Touvron et al. Llama 2 के अपने SFT annotation से असली उदाहरण देते हैं: एक prompt जो आवर्त सारणी के पहले दस तत्वों पर कविता माँगता है, और उसके साथ annotator की लिखी कविता जो उसका उत्तर देती है; एक prompt जो जानबूझकर क्रूर "roast" माँगता है, और उसके साथ annotator का लिखा इनकार जो बताता है कि क्यों। दोनों बस एक prompt हैं और वह ठीक-ठीक उत्तर जो annotator चाहता है कि model उसके लिए देना सीखे।

### यह चिह्नित करना कि एक हिस्सा कहाँ ख़त्म होता है और अगला कहाँ शुरू

इस data पर training का मतलब है कई prompt-और-उत्तर जोड़ों को training corpus में जोड़ देना, और model को किसी तरह पता चलना चाहिए कि prompt कहाँ ख़त्म होता है और उसका उत्तर कहाँ शुरू, क्योंकि सादे text में कुछ भी इस सीमा को अपने-आप चिह्नित नहीं करता। Touvron et al. ठीक यही बताते हैं: "a special token is utilized to separate the prompt and answer segments." यही उसका बीज है जिसे **chat template** कहा जाता है: role की सीमाओं (prompt वाला हिस्सा, उत्तर वाला हिस्सा, और multi-turn बातचीत में system message और हर अगला turn) को special tokens से चिह्नित करने का एक तय, एकरूप तरीक़ा, ताकि वही ढाँचा training में हर बार दिखे और serving के समय ठीक वैसा ही दोहराया जा सके।

### सीमा training और serving के समय एक जैसी क्यों होनी चाहिए

Chat template सिर्फ़ formatting की सुविधा नहीं है; वह उसका हिस्सा है जिस पर model असल में train हुआ। Model ने "यहाँ से उत्तर शुरू होता है" चिह्नित करने वाले special tokens को उस तरह के उत्तर देने से जोड़ना सीखा जो training में उन tokens के बाद आता था। Model को अलग template, अलग special tokens, roles का अलग क्रम, या system-message की छूटी हुई परिपाटी के साथ serve करने पर उसके सामने ऐसा ढाँचा आता है जो उसने सीखे हुए व्यवहार के साथ जुड़ा कभी देखा नहीं, और नतीजे में उसका व्यवहार बिगड़ता है या अनिश्चित हो जाता है। Serving के समय training वाला template ठीक वैसा ही दोहराना कोई वैकल्पिक सफ़ाई नहीं है; यह model को सही ढंग से इस्तेमाल करने का ही हिस्सा है।

### Multi-turn वही विचार है, दोहराया हुआ

Multi-turn बातचीत इसी हिस्से-चिह्नित-करने के विचार को एक से ज़्यादा आदान-प्रदान तक फैलाती है: system message (अगर हो), फिर बारी-बारी से user और assistant के turns, हर एक उसी तरह के special tokens से चिह्नित जैसे किसी एक prompt को उसके उत्तर से अलग करते हैं। Multi-turn के लिए कुछ नया नहीं गढ़ा जाता; यह वही सीमा-चिह्नित-करने का सिद्धांत है, जो हर example पर एक बार के बजाय हर turn पर एक बार लगता है।

## अभ्यास

1. ▢ Model, किसी तरह के marker के बिना, सिर्फ़ जोड़े गए सादे text से यह क्यों नहीं सीख सकता कि prompt कहाँ ख़त्म होता है और उसका उत्तर कहाँ शुरू?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि सादे text में ऐसा कोई अंतर्निहित signal नहीं होता जो "यह वह है जो पूछा गया था" को "यह वह उत्तर है जो मुझे देना सीखना है" से अलग करे; marker के बिना दोनों के बीच की सीमा training data में कहीं दर्ज ही नहीं होती।

</details>

2. ▢ एक टीम एक chat template से model को fine-tune करती है, पर production में उसे दूसरे template के साथ serve करती है (role की सीमाएँ चिह्नित करने वाले अलग special tokens)। सबसे संभावित नतीजा क्या है?

    - a) कोई असर नहीं; model formatting को पूरी तरह अनदेखा करता है
    - b) Model का व्यवहार बिगड़ता है या अनिश्चित हो जाता है, क्योंकि उसके सामने ऐसा ढाँचा है जो उसने training में सीखे व्यवहार के साथ जुड़ा कभी नहीं देखा
    - c) Model अपने-आप नए template को पहचानकर उसके हिसाब से ढल जाता है
    - d) सिर्फ़ system message पर असर पड़ता है; user और assistant turns सामान्य रूप से काम करते हैं

<details markdown="1"><summary>जाँचें</summary>

**b)** असली नतीजा है: chat template उसका हिस्सा है जिस पर model train हुआ, कोई सजावटी आवरण नहीं, इसलिए बेमेल होने पर model के सामने ऐसा ढाँचा आता है जिस पर वह train नहीं हुआ। (a), (c) और (d) सब template के बेमेल होने के प्रति ऐसी मज़बूती मान लेते हैं जिसकी training कोई वजह नहीं देती।

</details>

3. ▢ Multi-turn बातचीत का chat template उस सिंगल prompt-और-उत्तर template से कैसे जुड़ा है जिसे Touvron et al. SFT के लिए बताते हैं?

<details markdown="1"><summary>जाँचें</summary>

यह वही हिस्से-चिह्नित-करने का विचार है, बार-बार लगाया हुआ: system message अगर हो, फिर क्रम से हर user और assistant turn, हर एक उसी तरह के special tokens से चिह्नित जैसे किसी एक prompt को उसके उत्तर से अलग करते हैं, बजाय इसके कि कोई बुनियादी रूप से अलग तंत्र चाहिए हो।

</details>

## असली दुनिया का अभ्यास

- [ ] किसी ऐसे open model का chat template खोजें जिस तक आपकी पहुँच है (कई template file के रूप में छपे होते हैं या सीधे दस्तावेज़ में बताए जाते हैं), और पहचानें कि system message, user turn और assistant turn चिह्नित करने के लिए वह कौन-से special tokens इस्तेमाल करता है।
- [ ] Touvron et al. के दो उदाहरण SFT annotations पढ़ें (ऊपर link है, Table 5) और roast-इनकार वाले उदाहरण के आधार पर अपने शब्दों में लिखें कि अच्छे SFT उत्तर को सिर्फ़ विश्वसनीय सुनाई देने वाले उत्तर से क्या अलग करता है।
- [ ] कल: आगे देखे बिना पाठ 3 के लिए एक वाक्य की भविष्यवाणी लिखें: अगर कोई chat template prompt और उत्तर को बिना किसी अंतराल के एक sequence में जोड़ दे, और training पूरे sequence पर सामान्य next-token-prediction loss इस्तेमाल करे, तो model prompt tokens के साथ ख़ुद क्या करना सीखने लगेगा जो उसे नहीं सीखना चाहिए?

## आगे बढ़ने के लिए

- [पेपर: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
