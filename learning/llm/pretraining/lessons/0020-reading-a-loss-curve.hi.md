---
title: "20. Loss Curve पढ़ना"
description: "अकेला training loss curve गड़बड़ी को कम दिखाता है; दो दूसरे signals वह पकड़ लेते हैं जो वह चूक जाता है, और जल्दी पकड़ते हैं"
type: lesson
---

# पाठ 20. Loss Curve पढ़ना

**मिशन से संबंध:** "Training dashboard पढ़कर बता सकें कि run सही राह पर है या नहीं" "सफलता कैसी दिखती है" का वह बिंदु है जिसे यह चरण पूरा करता है। यह पाठ कवर करता है कि live dashboard पर असल में क्या देखना है; पाठ 21 कवर करता है कि सहेजे checkpoints को held-out data के विरुद्ध कैसे परखा जाए।
**मुख्य स्रोत:** [पेपर: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**पूर्व-आवश्यकताएँ:** [पाठ 19](0019-surviving-a-node-failure.md)

## वार्म-अप

1. ▢ OPT-175B की training के दौरान Zhang et al. ने loss curve के अलावा और क्या देखा जो loss divergence से जुड़ा था?

<details markdown="1"><summary>जाँचें</summary>

उनका dynamic loss scalar (mixed-precision setup का हिस्सा) शून्य पर गिर जाना, और final layer के activations के norm का उछल जाना।

</details>

2. ▢ Loss divergence से उबरना सिर्फ़ अकेला सबसे हाल का checkpoint रखने के बजाय एक से ज़्यादा रखने के पक्ष में तर्क क्यों देता है?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि सबसे अच्छा restart बिंदु loss scalar की सेहत और activation norm के रुझान के आधार पर चुना गया था, जो हमेशा सबसे हाल का checkpoint नहीं था; सिर्फ़ सबसे नया रखने से और पीछे लौटने का विकल्प ख़त्म हो जाता।

</details>

## यह जानें

### Training loss curve, और उसके लिए "स्वस्थ" का मतलब

Training dashboard जो सबसे बुनियादी चीज़ दिखाता है वह training loss ख़ुद है, training step या token count के विरुद्ध plot किया हुआ। चरण 3 के scaling laws उसके आकार की असली अपेक्षा देते हैं: जैसे-जैसे compute और tokens जमा होते हैं, loss सहजता से गिरना चाहिए, मोटे तौर पर power-law जैसे curve का पालन करते हुए, न सीधी रेखा में और न असंबंधित छलाँगों की श्रृंखला में। जो curve इस सामान्य आकार का पालन करता है वह अपेक्षा के अनुसार बर्ताव कर रहा है; जो curve scaling-law के अनुमानित पथ से कहीं पहले समतल हो जाए, या जिसमें अचानक तेज़ उछाल दिखे (loss spike, पाठ 16), वह ऐसा training loss curve है जो कुछ ऐसा बता रहा है जिसकी जाँच करना ज़रूरी है, यह मान लेने से पहले कि run बस सही राह पर है।

### दो signals जो loss curve के साफ़ दिखाने से पहले गड़बड़ी पकड़ लेते हैं

अकेला training loss देखना काफ़ी नहीं है, क्योंकि जब तक loss में ही spike दिखता है, तब तक अंतर्निहित समस्या कुछ समय से बन रही हो सकती है। OPT-175B का Zhang et al. का ब्योरा दो और signals देता है जिन्होंने उसी गड़बड़ी की पहले चेतावनी दी जो loss curve ने आख़िर में दिखाई: उनका **dynamic loss scalar**, जो mixed-precision setup का हिस्सा है, शून्य की ओर गिरना, और **final layer के activations के norm** का ऊपर की ओर उछलना। दोनों अस्थिरता की ओर बढ़ते training run के लक्षण हैं, जो loss के साफ़ diverge होने से पहले या उसके साथ-साथ दिखते हैं, और ठीक इसीलिए Zhang et al. ने यह आँकने में सिर्फ़ loss curve नहीं, इन्हें भी इस्तेमाल किया कि training का कोई बिंदु restart के लिए सुरक्षित था या नहीं।

### Gradient norm, समय के साथ देखा हुआ

पाठ 16 ने gradient-norm clipping को प्रति-step सुरक्षा के रूप में कवर किया, जो किसी एक update के बड़े होने की सीमा बाँधती है। वही gradient norm, जब हर step पर सिर्फ़ clipping सीमा से जाँचने के बजाय training के दौरान एक curve के रूप में देखा जाए, अपने-आप में उपयोगी signal है: जो gradient norm समय के साथ ऊपर की ओर जा रहा हो, या clipping के बाद भी बार-बार उछल रहा हो, वह उसी तरह की अस्थिरता का शुरुआती संकेत हो सकता है जिसे loss spike आख़िर में ज़्यादा नाटकीय ढंग से दिखाता, जिससे पूरे divergence के restart मजबूर करने से पहले दख़ल देने का मौक़ा मिलता है, जैसे learning rate घटाकर।

### लगातार देखते रहना

इनमें से कोई भी signal मदद नहीं करता अगर कोई, या कोई automated चीज़, उन्हें असल में देख ही नहीं रही। चरण 8 ने स्थापित किया कि विफलताएँ और अस्थिरताएँ बड़े training run का नियमित, बार-बार होने वाला हिस्सा हैं, दुर्लभ घटना नहीं; loss, gradient norm और loss scalar जैसे संख्यात्मक-स्थिरता signal को दिखाने वाला dashboard तभी उपयोगी है जब उसे इतनी बार जाँचा जाए, या वह इतने स्वचालित ढंग से alert करे, कि विकसित होती समस्या उस क़ीमत से पहले पकड़ ली जाए जो उसे जल्दी पकड़ने की तुलना में कहीं ज़्यादा progress ख़र्च कराती।

## अभ्यास

1. ▢ एक team का training loss curve घट रहा है, पर चरण 3 के scaling-law संबंधों के उनके model size और अब तक के token count के लिए अनुमान से साफ़ तौर पर धीमे। क्या यह ज़रूरी रूप से समस्या का संकेत है, या स्वस्थ run से मेल खा सकता है?

<details markdown="1"><summary>संकेत</summary>

Scaling laws अनुभव-आधारित fits हैं जिनमें असली variance है, हर अलग run के लिए सटीक गारंटी नहीं।

</details>

<details markdown="1"><summary>जाँचें</summary>

इसे ठीक मान लेने के बजाय जाँचना चाहिए, पर यह अपने-आप समस्या का सबूत नहीं है; scaling laws variance वाले fit किए हुए रुझान हैं, हर run के लिए सटीक गारंटी नहीं। अपेक्षित पथ से सार्थक, टिकने वाला अंतर दूसरे signals (gradient norm, mixed precision इस्तेमाल हो तो loss scalar, या data pipeline ख़ुद) जाँचने की जायज़ वजह है, बजाय यह मानने के कि अकेला curve किसी भी तरफ़ सवाल निपटा देता है।

</details>

2. ▢ Loss scalar का शून्य की ओर गिरना, या activation norm का उछलना, अस्थिरता की चेतावनी training loss curve से पहले क्यों दे सकता है?

<details markdown="1"><summary>जाँचें</summary>

ये अंतर्निहित संख्यात्मक समस्या के विकसित होने के लक्षण हैं, जो उसके इतना बड़ा होने से पहले दिख सकते हैं कि loss curve को साफ़ तौर पर बिगाड़े। जब तक loss में ही spike साफ़ दिखता है, तब तक समस्या कुछ समय से बन रही हो सकती है।

</details>

3. ▢ इनमें से कौन-सा सबसे अच्छा बताता है कि loss, gradient norm और loss scalar जैसे स्थिरता signal को दिखाने वाला dashboard व्यवहार में तभी उपयोगी है जब उसकी निगरानी बार-बार हो?

    - a) ये metrics पूरे training run में सिर्फ़ एक बार, बिल्कुल अंत में, सार्थक होते हैं
    - b) बड़े पैमाने पर विफलताएँ और अस्थिरताएँ बार-बार होने वाली, नियमित घटनाएँ हैं (चरण 8), इसलिए देर से पकड़ी गई समस्या उसी समस्या के जल्दी पकड़े जाने से कहीं ज़्यादा खोई progress की क़ीमत लेती है
    - c) Metrics का अर्थ ही बदल जाता है अगर उन्हें बहुत बार जाँचा जाए
    - d) बार-बार निगरानी सिर्फ़ बहुत छोटे models के लिए उपयोगी है

<details markdown="1"><summary>जाँचें</summary>

**b)** यही असली तर्क है: यह देखते हुए कि बड़े पैमाने पर विफलताएँ और अस्थिरताएँ कितनी बार होती हैं, dashboard का मूल्य सीधे इससे जुड़ा है कि विकसित होती समस्या कितनी जल्दी नोटिस हो। (a), (c) और (d) उसमें से कुछ नहीं दर्शाते जो यह पाठ या चरण 8 ने स्थापित किया।

</details>

## असली दुनिया का अभ्यास

- [ ] किसी training framework या experiment-tracking tool का dashboard खोजें (Weights & Biases, TensorBoard या ऐसा ही) और पहचानें कि इस पाठ के signals (loss, gradient norm, संख्यात्मक-स्थिरता संकेतक) में से कौन-से वह default रूप से दिखाता है, और किन्हें साफ़ तौर पर जोड़ना पड़ेगा।
- [ ] OPT पेपर (ऊपर linked) का वह अनुच्छेद पढ़ें जो loss divergence को loss scalar और activation norm से जोड़ता है, और एक वाक्य लिखें कि अगर तीनों उपलब्ध हों वाले dashboard पर आपको loss spike दिखे तो आप सबसे पहले कौन-सा signal जाँचेंगे।
- [ ] कल: आगे देखे बिना, पाठ 21 के लिए एक वाक्य में अनुमान लिखें: अगर अकेला training loss यह नहीं बताता कि model उन tasks पर कितना अच्छा प्रदर्शन करता है जिनके लिए लोग उसे असल में इस्तेमाल करेंगे, तो training के दौरान, सिर्फ़ उसके ख़त्म होने के बाद नहीं, इसे जाँचने के लिए क्या अलग तरह से नापना पड़ेगा?

## आगे बढ़ने के लिए

- [पेपर: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [पेपर: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
