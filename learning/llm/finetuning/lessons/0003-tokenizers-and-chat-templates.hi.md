---
title: "3. Tokenizers और Chat Templates"
description: "उसी rendering पर train करें जिसे आप serve करेंगे"
type: lesson
---

# पाठ 3. Tokenizers और Chat Templates

**मिशन से संबंध:** जो fine-tune साफ़-सुथरा train होता है पर बुरा बर्ताव करता है, उसका सबसे आम कारण template mismatch होता है, hyperparameter नहीं।
**मुख्य स्रोत:** [दस्तावेज़: Chat Templates, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
**पूर्व-आवश्यकताएँ:** [पाठ 1](0001-what-a-base-model-is.md), [पाठ 2](0002-where-the-weights-live.md)

## वार्म-अप

1. ▢ आधुनिक block में किसमें ज़्यादा parameters होते हैं, attention में या MLP में?

<details markdown="1"><summary>जाँचें</summary>

MLP में, क्योंकि उसका intermediate आयाम hidden size का कई गुना होता है, और grouped-query attention `k_proj` और `v_proj` को और सिकोड़ देता है।

</details>

2. ▢ Model के असली module-नाम कैसे ढूँढते हैं?

<details markdown="1"><summary>जाँचें</summary>

लोड किए गए model से `named_modules()` के ज़रिए उन्हें print करें। उन्हें कभी याद से न बताएँ; वे architecture के हिसाब से बदलते हैं।

</details>

3. ▢ Cross-entropy loss क्या मापता है?

<details markdown="1"><summary>जाँचें</summary>

यह कि असल में आए token को model ने कितनी probability दी थी। कम loss का मतलब है कि असली continuation model को हैरान करने वाली नहीं लगी।

</details>

## यह जानें

Model text नहीं देखता। वह integers देखता है। Tokenizer उनके बीच की mapping है, और वह model का हिस्सा है: किसी checkpoint का tokenizer दूसरे के tokenizer से बदला नहीं जा सकता, एक ही परिवार के भीतर भी।

### Tokenizer क्या है

आधुनिक models subword tokenization इस्तेमाल करते हैं, आम तौर पर byte-pair encoding। Tokenizer को train करने का मतलब है bytes से शुरू करना और सबसे आम पड़ोसी जोड़ी को बार-बार मिलाते जाना, जिससे ऐसी vocabulary बनती है जहाँ आम शब्द एक token होते हैं और दुर्लभ शब्द टुकड़ों में बँट जाते हैं।

तीन गुण व्यवहार में चोट करते हैं:

**Tokens शब्द नहीं होते।** ` the` (आगे space के साथ) और `the` अलग tokens हैं। Capitalisation से tokenization बदलती है। `1234` जैसी संख्या एक token हो सकती है या चार, और इसीलिए models अंकगणित में ऐसे ढंग से कमज़ोर होते हैं जो मनमाना लगता है।

**Token की गिनती character की गिनती नहीं होती।** अंग्रेज़ी में औसतन लगभग चार characters प्रति token आते हैं; code, ग़ैर-Latin scripts और असामान्य formatting कहीं कम कुशल हैं। पाठ 7 में आपका sequence-length budget tokens में मापा जाता है, इसलिए आपको अंदाज़ा नहीं, माप लेना होगा।

**Special tokens संरचना ढोते हैं।** Beginning-of-sequence, end-of-sequence, padding, और नीचे के role markers साधारण vocabulary entries हैं जिन्हें model ने संरचनात्मक मानना सीखा है। उन्हें हाथ से ग़लत ढंग से डालना syntax error नहीं है; यह चुपचाप होने वाला distribution shift है।

### Chat templates

Chat model को ऐसी बातचीत पर train किया गया था जो एक ख़ास, सटीक string format से एक सपाट token sequence में बदली गई थी। उदाहरण के लिए, किसी model को शायद कुछ इस आकार की चीज़ पर train किया गया हो:

```text
<|im_start|>system
You are helpful.<|im_end|>
<|im_start|>user
Hello<|im_end|>
<|im_start|>assistant
Hi.<|im_end|>
```

दूसरा परिवार बिल्कुल अलग markers इस्तेमाल करता है। यह format कोई ऐसी परिपाटी नहीं जिसका आप अंदाज़ा लगा सकें: यह वही distribution है जिस पर weights फ़िट हुए थे। कोई marker ग़लत लगा दें, कोई फ़ालतू newline जोड़ दें, या जहाँ model system block की उम्मीद करता है वहाँ उसे छोड़ दें, तो model अब थोड़ा off-distribution काम कर रहा है। वह तब भी धाराप्रवाह text बनाएगा, और इसीलिए यह विफलता पकड़ना कठिन है।

Template tokenizer के साथ Jinja string के रूप में आता है। Format ख़ुद लिखने के बजाय उसे इस्तेमाल करें:

```text
tokenizer := load_tokenizer("<model>")
messages := [
    {role: "system", content: "You are helpful."},
    {role: "user", content: "Hello"},
]

# For inference: leaves the sequence ready for the model to continue.
prompt := tokenizer.render(messages, add_generation_prompt: true)

# For training: the assistant turn is already present, so no generation prompt.
full := tokenizer.render(messages + [{role: "assistant", content: "Hi."}])

print(exact(prompt))
print(exact(full))
```

सटीक string print करना, संक्षिप्त दृश्य नहीं, मायने रखता है। सही और टूटे हुए template के बीच का फ़र्क़ अक्सर एक whitespace character का होता है, और साधारण print उसे छिपा सकता है। Python में इसका मतलब है string पर `print` नहीं, `repr`।

### एक नियम

**उसी rendering पर train करें जिसे आप serve करेंगे।** अगर आप अपने हाथ से बनाए format पर fine-tune करते हैं और फिर model के आधिकारिक template से serve करते हैं, तो आपने एक distribution पर train किया और दूसरा deploy किया। Loss curve ठीक दिखेगी। Model सूक्ष्म रूप से बदतर होगा, और आप एक दिन rank को दोष देने में गँवाएँगे।

`add_generation_prompt` वह जगह है जहाँ यह सबसे ज़्यादा ग़लत होता है: वह inference में आता है, जहाँ आप चाहते हैं कि model assistant के रूप में आगे बढ़े, training example में नहीं, जहाँ assistant का text उस sequence का हिस्सा है जिसे सीखा जा रहा है।

![एक बातचीत दो बार template के टुकड़ों की पट्टी के रूप में rendered। दोनों में वही तीन टुकड़े हैं जो assistant marker पर ख़त्म होते हैं; inference वाली rendering वहीं रुक जाती है, जबकि training वाली rendering में एक और टुकड़ा है, assistant का अपना text और end marker।](images/where-the-turn-begins.svg)

दोनों renderings assistant marker तक वही टुकड़े हैं, उन्हीं जगहों पर। जो अलग है वह उसके बाद वाला टुकड़ा है, जो ठीक वही है जो model को inference में बनाना है और training के दौरान सीखना है।

### Base models के पास template नहीं होता

अगर किसी base model के tokenizer में chat template नहीं है, तो यह bug नहीं है, क्योंकि सहेजने के लिए कोई बातचीत का format है ही नहीं। Format आप चुन रहे हैं, इसलिए एक चुनें, लिख लें, और training और serving में उसे एक जैसा इस्तेमाल करें।

## अभ्यास

1. ▢ आप एक ही model परिवार के दो checkpoints के बीच tokenizer क्यों नहीं बदल सकते?

<details markdown="1"><summary>जाँचें</summary>

Token IDs सीधे embedding matrix में index करते हैं। अलग vocabulary उसी integer को दूसरी पंक्ति से जोड़ देती है, इसलिए हर input चुपचाप ग़लत अनुवादित होता है। Output धाराप्रवाह बकवास होता है, या vocabulary sizes अलग हों तो crash।

</details>

2. ▢ आप एक training example बना रहे हैं। `add_generation_prompt` `True` होना चाहिए या `False`, और क्यों?

<details markdown="1"><summary>जाँचें</summary>

`False`। Generation prompt वह शुरुआती marker है जो model से कहता है "अब assistant बोलेगा", जो inference में उपयोगी है, जब assistant का turn अभी मौजूद नहीं होता। Training में assistant का turn text में मौजूद होता है, इसलिए prompt जोड़ने से marker दोहराया जाता है और sequence उस format से खिसक जाती है जिसे model जानता है।

</details>

3. ▢ आपका fine-tune कम loss तक train होता है पर serving के समय model अपने उत्तर के अंत पर रुकने के बजाय बड़बड़ाता चला जाता है। सबसे संभावित कारण बताएँ।

<details markdown="1"><summary>जाँचें</summary>

आपके training examples में end-of-turn token नहीं था, इसलिए model ने कभी नहीं सीखा कि उत्तर समाप्त होते हैं।

Loss इसे नहीं पकड़ सकता: धाराप्रवाह continuation predict करना ठीक वही है जिसके लिए आपके data पर model को इनाम मिला। यह data बनाने का bug है जिसे सिर्फ़ असली generation उजागर करती है, और यही एक वजह है कि पाठ 24 सिर्फ़ score करने के बजाय generate करने पर ज़ोर देता है।

</details>

4. ▢ एक prompt 700 अंग्रेज़ी शब्दों का है। लगभग कितने tokens, और क्या आप training budget के लिए उस अनुमान पर भरोसा करेंगे?

<details markdown="1"><summary>जाँचें</summary>

लगभग 900 से 1000 tokens, प्रति अंग्रेज़ी शब्द लगभग 1.3 tokens लेकर। नहीं, आप उस पर भरोसा नहीं करेंगे: यह अनुपात code, JSON, ग़ैर-Latin scripts और असामान्य formatting के साथ काफ़ी बदलता है, जो सब fine-tuning data में आम हैं।

असली distribution को असली tokenizer से मापें। पाठ 7 उस distribution को memory की संख्या में बदलता है।

</details>

5. ▢ Training और serving के बीच इनमें से क्या बदलना सुरक्षित है?

    - a) इस्तेमाल हुई chat template string
    - b) Model के साथ आया tokenizer
    - c) Generation के समय इस्तेमाल हुआ sampling temperature
    - d) Turn के अंत को चिह्नित करने वाला special token

<details markdown="1"><summary>जाँचें</summary>

**c)** Generation के समय इस्तेमाल हुआ sampling temperature।

Temperature तब लगता है जब model अपना distribution बना चुका होता है, इसलिए यह serving का चुनाव है। बाक़ी तीन उस distribution को परिभाषित करते हैं जिस पर weights फ़िट हुए थे; इनमें से किसी को बदलने का मतलब है उस समस्या से अलग समस्या serve करना जिस पर आपने train किया।

</details>

## असली दुनिया का अभ्यास

- [ ] एक model लें और अपनी library के असली chat-template call (जैसे Transformers में `apply_chat_template(..., tokenize=False)`) से template render करें, whitespace समेत सटीक string print करते हुए (जैसे Python का `repr`)। उसे अपने नोट्स में कॉपी करें।
- [ ] एक ही paragraph को दो अलग model परिवारों में tokenize करें और token की गिनतियों की तुलना करें। फिर JSON का एक block tokenize करें और फिर तुलना करें।
- [ ] कल: end-of-turn marker हटाकर जान-बूझकर template तोड़ें, फिर model को prompt करें। देखें कि वह क्या करता है। यही वह विफलता है जिसे पहचानना आप सीख रहे हैं।

## आगे बढ़ने के लिए

- [दस्तावेज़: Chat Templates, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
- [कोड: minbpe, Andrej Karpathy](https://github.com/karpathy/minbpe): byte-pair encoding पढ़ने लायक रूप में
- [failure modes शीट](../reference/failure-modes.md): template mismatch वहाँ आता है
- [पाठ 21. Dataset बनाना](0021-building-the-dataset.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
