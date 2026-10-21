---
title: "3. गैर-Assistant Tokens पर Loss Masking"
description: "Prompt पर loss को शून्य करें, वरना gradient signal उस text का अनुमान लगाना सिखाने में ख़र्च होता है जिसे model ने generate नहीं किया"
type: lesson
---

# पाठ 3. गैर-Assistant Tokens पर Loss Masking

**मिशन से संबंध:** "ऐसा SFT training loop लिखें जो non-assistant tokens पर loss को mask करे, और समझाएँ कि उस mask के बिना train किए chat model में क्या टूटता है" "सफलता कैसी दिखती है" का पहला बिंदु है, और यह पाठ वह जगह है जहाँ उसका सीधा उत्तर मिलता है।
**मुख्य स्रोत:** [पेपर: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
**पूर्व-आवश्यकताएँ:** [पाठ 2](0002-instruction-data-and-the-chat-template.md), [Loss masking](../GLOSSARY.md)

## वार्म-अप

1. ▢ Chat template क्या है, और यह क्यों मायने रखता है कि training और serving दोनों के समय वही template इस्तेमाल हो?

<details markdown="1"><summary>जाँचें</summary>

Role की सीमाओं (system, user, assistant turns) को special tokens से चिह्नित करने का एक तय, एकरूप तरीक़ा, ताकि model ऐसा ढाँचा सीख सके जिसे वह भरोसे के साथ दोबारा देखेगा। Training और serving के templates का बेमेल होना model के सामने ऐसा ढाँचा रखता है जो उसने सीखे हुए व्यवहार के साथ जुड़ा कभी नहीं देखा, जिससे उसका व्यवहार बिगड़ता या अस्थिर होता है।

</details>

2. ▢ Touvron et al. के अनुसार, SFT training data में prompt को उसके उत्तर से अलग करने के लिए वे कौन-सा special token इस्तेमाल करते हैं?

<details markdown="1"><summary>जाँचें</summary>

एक ख़ास special token जो prompt वाले हिस्से और उत्तर वाले हिस्से की सीमा चिह्नित करने के लिए ही डाला जाता है।

</details>

## यह जानें

### इस loss का सादा, बिना mask वाला रूप ग़लत होगा

सामान्य language-modeling loss model को sequence की हर position पर अगला token अनुमान करना सिखाता है, उसकी तुलना में जो sequence में वहाँ असल में है। इसे बिना किसी बदलाव के जोड़े गए prompt-और-उत्तर example पर लगाएँ तो यह model को prompt के अपने tokens का अनुमान लगाना भी सिखाएगा, सिर्फ़ उत्तर के नहीं, क्योंकि prompt भी sequence का हिस्सा है, ठीक उत्तर की तरह।

### Touvron et al. इसकी जगह असल में क्या करते हैं

Touvron et al. अपना तरीक़ा सीधे बताते हैं: "we utilize an autoregressive objective and zero-out the loss on tokens from the user prompt, so as a result, we backpropagate only on answer tokens." यही **loss masking** है: prompt का (या, multi-turn example में, किसी भी user या system turn का) हर token loss में अपना योगदान शून्य कर देता है, इसलिए सिर्फ़ वे tokens जिन्हें model को असल में generate करना है, यानी assistant का उत्तर, gradient पैदा करते हैं। यांत्रिक रूप से यह आम तौर पर ऐसे होता है कि हर masked position को ऐसा label मान दिया जाता है जिसे loss function को अनदेखा करने को कहा गया है (मानक cross-entropy loss के लिए आम परिपाटी इसे `-100` रखती है), उस token की जगह जो वहाँ असल में है।

### इसके बिना क्या टूटता है

यह masking छोड़ना सिर्फ़ थोड़ा compute बर्बाद करना नहीं है; इससे बदल जाता है कि model को असल में क्या करना सिखाया जा रहा है। सीधे दो ठोस समस्याएँ निकलती हैं:

- **Model ऐसा text predict करना सीखता है जो उसने generate नहीं किया और जिसे उसे कभी दोहराना नहीं पड़ेगा।** किसी model को user के अपने prompt को वापस उसी को सुनाना सिखाने से SFT का लक्ष्य नहीं सधता, जो यह तय करना है कि model उत्तर में क्या बनाता है, न कि वह सवाल का कितना दोहरा सकता है।
- **Prompts अक्सर उनके बाद आने वाले उत्तरों से कहीं लंबे होते हैं।** बिना mask वाला loss जितने भी prompt tokens हैं उन्हीं से भर जाता है, जो उत्तर के tokens पर gradient signal को पतला कर देता है, जबकि वही sequence का वह अकेला हिस्सा है जिसे SFT असल में ढालना चाहता है, और loss का बड़ा हिस्सा ऐसे काम (prompt predict करना) पर ख़र्च होता है जो कभी मक़सद था ही नहीं।

### नतीजा: masking objective को उस चीज़ पर केंद्रित करती है जो सिखाई जा रही है

हर non-assistant token को mask करना दोनों समस्याओं का उलटा करता है: SFT के एक step में gradient signal की हर इकाई उन tokens से आती है जिन्हें model को असल में बनाना सीखना है, और उसमें से कुछ भी ऐसे text को predict करने में नहीं जाता जो model को बस दिया गया था। इसी से SFT वही ख़ास हुनर सिखाता है जो उसे सिखाना है, यानी चाहे गए उत्तर की नक़ल, उस हुनर और किसी असंबंधित हुनर (मनमाने user text का अनुमान लगाना) के मिश्रण के बजाय, जो बस उसी training sequence में साथ आ गया।

## अभ्यास

1. ▢ एक training example में 200-token का prompt और 20-token का उत्तर जोड़ा गया है, और कोई loss masking नहीं लगी। इस example के कुल loss का लगभग कितना हिस्सा उन tokens से आता है जो SFT का असली लक्ष्य नहीं हैं?

<details markdown="1"><summary>जाँचें</summary>

220 में से लगभग 200 tokens, करीब 91%, prompt tokens होंगे जो ऐसा loss दे रहे हैं जिसका उस उत्तर से कोई लेना-देना नहीं जो SFT model को देना सिखाना चाहता है। बिना mask वाले loss का सिर्फ़ करीब 9% उत्तर से ही आएगा।

</details>

2. ▢ इनमें से कौन-सा सबसे अच्छा बताता है कि loss masking यांत्रिक रूप से असल में क्या करती है?

    - a) वह prompt tokens को input sequence से पूरी तरह हटा देती है
    - b) वह हर masked token की position को ऐसा label देती है जिसे loss function को अनदेखा करने को कहा गया है, ताकि सिर्फ़ unmasked (assistant) positions gradient दें
    - c) वह prompt tokens को process करते समय ख़ास तौर पर learning rate घटा देती है
    - d) वह सिर्फ़ prompt tokens के लिए अलग model train करती है

<details markdown="1"><summary>जाँचें</summary>

**b)** असली तंत्र है: prompt tokens अब भी input के रूप में मौजूद रहते हैं, इसलिए model अपना उत्तर उन पर आधारित कर सकता है, पर उनकी positions को खुद loss की गणना से बाहर रखा जाता है। (a) वह जानकारी हटा देता जिस पर model को अपना उत्तर टिकाना है। (c) और (d) ऐसी किसी तकनीक का वर्णन नहीं करते जो यह पाठ या उसका स्रोत बताता है।

</details>

3. ▢ Non-assistant tokens पर loss masking के बिना train किए model की तुलना उसी से की जाती है जो उसके साथ train हुआ, बिल्कुल उसी SFT data पर। एक ठोस तरीक़ा बताइए जिसमें आप उम्मीद करेंगे कि बिना mask वाले model की SFT training अलग तरह से गई होगी।

<details markdown="1"><summary>जाँचें</summary>

इसका कोई भी वाजिब रूप: gradient signal उत्तर के tokens पर पूरी तरह केंद्रित होने के बजाय prompt tokens का अनुमान लगाना सीखने में पतला हुआ या ख़र्च हुआ, इसलिए उतने ही training steps में model की सीख का कम हिस्सा असल में उसके उत्तर-generate करने के व्यवहार को ढाल रहा था, वही एक चीज़ जो SFT सिखाना चाहता है।

</details>

## असली दुनिया का अभ्यास

- [ ] देखें कि जिस training framework तक आपकी पहुँच है, वह chat-style SFT data के लिए loss masking कहाँ लागू करता है (`ignore_index`, masked positions वाला `labels` field, या ऐसा ही कुछ), और पुष्टि करें कि masked position चिह्नित करने के लिए वह कौन-सी परिपाटी इस्तेमाल करता है।
- [ ] कोई छोटी उदाहरण बातचीत लें (एक system message, एक user turn, एक assistant turn) और इस पाठ के नियम के अनुसार token-दर-token या हिस्से-दर-हिस्से चिह्नित करें कि कौन-से हिस्से mask होंगे और कौन-से loss में योगदान देंगे।
- [ ] कल: दो user turns और दो assistant turns वाली multi-turn बातचीत के लिए लिखें कि कौन-से turns mask होते हैं और कौन-से नहीं, और अपना उत्तर इस पाठ के नियम से मिलाएँ कि हर non-assistant turn mask होता है, सिर्फ़ पहला prompt नहीं।

## आगे बढ़ने के लिए

- [पेपर: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
- [दस्तावेज़: "TRL - Transformer Reinforcement Learning", Hugging Face](https://huggingface.co/docs/trl/index)
- [संसाधन](../RESOURCES.md)

---

चरण 2 ने दिखाया कि दिखाए गए उत्तर की सीधी नक़ल कैसे होती है। चरण 3 अलग तरह के signal की ओर मुड़ता है: उत्तर क्या होना चाहिए यह नहीं, बल्कि दो उत्तरों में से इंसान ने किसे पसंद किया।

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
