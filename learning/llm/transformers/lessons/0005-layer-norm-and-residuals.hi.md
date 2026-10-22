---
title: "5. Layer Norm और Residual Connections"
description: "कई transformer blocks को stack करने के लिए साफ़ gradient path और स्थिर activation ranges क्यों चाहिए, और residuals तथा layer norm उनमें से एक-एक कैसे देते हैं"
type: lesson
---

# पाठ 5. Layer Norm और Residual Connections

**मिशन से संबंध:** अकेला attention (चरण 1) अपने-आप गहरे, train हो सकने वाले network में stack नहीं होता; residual connections और layer normalization वे दो हिस्से हैं जो कई transformer blocks को stack करना (चरण 3) अस्थिर होने के बजाय व्यावहारिक बनाते हैं।
**मुख्य स्रोत:** [पेपर: "Layer Normalization", Ba, Kiros, and Hinton, 2016](https://arxiv.org/abs/1607.06450)
**पूर्व-आवश्यकताएँ:** [पाठ 4](0004-positional-encoding.md), [Scaled dot-product attention](../GLOSSARY.md)

## वार्म-अप

1. ▢ Attention का समीकरण अपने-आप जो compute करता है, उसे देखते हुए positional encoding की ज़रूरत ही क्यों है?

<details markdown="1"><summary>जाँचें</summary>

Attention अपने input को अक्रमित सेट मानता है: दो positions की अदला-बदली किसी compute किए संबंध को बदले बिना बस output को दोबारा नामित कर देती है। Positional encoding position को token embeddings के भीतर ही डालता है, और attention के dot products के क्रम के प्रति संवेदनशील होने का यही एकमात्र तरीक़ा है।

</details>

2. ▢ Mask की गई position का कच्चा score सादे 0 पर रखने से उसे attention से सही ढंग से बाहर क्यों नहीं किया जा सकता?

<details markdown="1"><summary>जाँचें</summary>

`exp(0) = 1`, जो बिल्कुल सामान्य मान है और softmax के हर में अब भी probability mass के लिए होड़ करता है। सिर्फ़ बड़ी ऋणात्मक संख्या ही उसके exponential को असरदार रूप से शून्य तक ले जाती है, और वही असल में उस position का योगदान हटाती है।

</details>

## यह जानें

### Residual connections gradients को सीधा रास्ता देते हैं

Transformer की sublayer (attention, या अगले पाठ का feed-forward block) एक **residual connection** में लिपटी होती है: block का output `x + Sublayer(x)` होता है, अकेला `Sublayer(x)` नहीं। यह तब मायने रखता है जब ऐसे कई blocks stack किए जाएँ (चरण 3 का विषय): `+ x` पद के बिना, training के दौरान पीछे की ओर बहता gradient हर layer पर हर sublayer के रूपांतरण से गुज़रता है, और गहरे stack में वह रास्ता शून्य की ओर सिकुड़ सकता है या फट सकता है, जिससे network को ठीक से train करना कठिन या नामुमकिन हो जाता है। Residual पद होने पर gradient के पास हर layer पर identity `+ x` connection से सीधे गुज़रने वाला दूसरा, सीधा रास्ता होता है, चाहे sublayer ख़ुद कुछ भी कर रही हो, जिससे गहरे stack की सबसे शुरुआती layers तक भी काम का training signal पहुँचता रहता है।

### Layer normalization हर layer के activations को अनुमान-योग्य दायरे में रखता है

**Layer normalization** एक अकेले token के अपने activation vector को normalize करता है: उसका mean घटाकर और उसके standard deviation से भाग देकर, जो उसी vector की अपनी features पर compute होते हैं, और फिर एक सीखा हुआ scale (`gamma`) और shift (`beta`) लगाता है ताकि network काम का दायरा अब भी represent कर सके, mean 0 और इकाई variance पर अटके रहने की जगह। यह **batch normalization** से अलग है, जो इसके बजाय batch आयाम पर normalize करता है और कई examples के साथ मिलाकर आँकड़े compute करता है। Layer norm की प्रति-example गणना sequence models के लिए ख़ास तौर पर मायने रखती है: वह batch size चाहे जो हो, एक के batch में भी, एक जैसा काम करती है, और autoregressive generation में ठीक यही स्थिति होती है, जहाँ एक अकेली generate की जा रही sequence पर compute किए गए batch statistics निरर्थक या अस्थिर होते।

व्यावहारिक असर: layer norm हर sublayer के input को एक-से, अनुमान-योग्य संख्यात्मक दायरे में रखता है, इसलिए कई blocks के stack में गहरी बैठी sublayer को input के पास वाली sublayer से बहुत अलग activation scales नहीं मिलते। इससे training उसी तरह स्थिर होती है जिस तरह पाठ 1 के scaling factor ने attention scores को उस दायरे में रखा था जहाँ softmax का gradient काम का बना रहा।

### Norm कहाँ बैठता है: post-norm बनाम pre-norm

मूल transformer पेपर layer norm को residual जोड़ के *बाद* रखता है, `LayerNorm(x + Sublayer(x))`, जिसे **post-norm** कहते हैं। बाद के काम में पाया गया कि norm को sublayer से *पहले*, उसके बजाय residual शाखा के भीतर रखना, `x + Sublayer(LayerNorm(x))`, जिसे **pre-norm** कहते हैं, models के बहुत गहरे होने पर ज़्यादा स्थिरता से train होता है। कारण: pre-norm residual path को पूरे network में बिल्कुल साफ़ और बिना normalize किए छोड़ देता है, यानी सिरे से सिरे तक बेरोक identity connection, जबकि post-norm की जगह का मतलब है कि residual योग ख़ुद हर layer पर normalize होता है, जो उस साफ़ gradient राजमार्ग को गँदला करता है। इसीलिए मूल पेपर के post-norm के चुनाव के बावजूद ज़्यादातर मौजूदा बड़े models pre-norm इस्तेमाल करते हैं।

![Residual शाखा के दो अगल-बगल बने diagrams। बाईं ओर post-norm: x एक bypass रेखा और sublayer से गुज़रती रेखा में बँटता है, दोनों को जोड़ा जाता है, और उस योग को layer norm से गुज़ारा जाता है, इसलिए residual path ख़ुद हर layer पर normalize होता है। दाईं ओर pre-norm: x एक bypass रेखा और ऐसी रेखा में बँटता है जो sublayer से पहले layer norm से गुज़रती है, दोनों को जोड़ा जाता है, और output को बिना किसी और normalization के सीधे इस्तेमाल किया जाता है, इसलिए ऊपर से नीचे चलने वाला residual path सिरे से सिरे तक बिल्कुल साफ़ और बेरोक रहता है।](images/pre-norm-vs-post-norm.svg)

## अभ्यास

1. ▢ Backpropagation के दौरान gradients के साथ क्या होता है, इस लिहाज़ से residual connection transformer blocks के गहरे stack को train करने में कैसे मदद करता है?

<details markdown="1"><summary>जाँचें</summary>

Residual के बिना, पीछे की ओर बहता gradient हर stacked layer पर हर sublayer के रूपांतरण से गुज़रता है, जो कई layers में सिकुड़ या फट सकता है। Residual का `+ x` पद gradient को हर layer पर identity connection से सीधे गुज़रने वाला दूसरा, सीधा रास्ता देता है, जिससे सबसे शुरुआती layers तक भी काम का signal पहुँचता रहता है, चाहे हर sublayer का रूपांतरण उसके साथ कुछ भी करे।

</details>

2. ▢ Layer norm का batch norm की तरह batch आयाम पर नहीं, बल्कि feature आयाम पर normalize करने का चुनाव, autoregressive generation करने वाले sequence model के लिए ख़ास तौर पर क्यों मायने रखता है?

<details markdown="1"><summary>जाँचें</summary>

Autoregressive generation आम तौर पर छोटे batch के साथ चलती है, अक्सर batch size 1। Batch normalization अपने आँकड़े batch आयाम पर compute करता है, जो इतने कम (या एक) examples से आँकड़े निकालने पर निरर्थक या अस्थिर होता है। Layer norm अपने आँकड़े एक अकेले example की अपनी features से compute करता है, इसलिए batch कितना भी बड़ा या छोटा हो, वह एक जैसा काम करता है।

</details>

3. ▢ Post-norm और pre-norm की जगह की तुलना करें, और समझाएँ कि बहुत गहरे models के लिए आम तौर पर pre-norm क्यों पसंद किया जाता है।

<details markdown="1"><summary>संकेत</summary>

सोचें कि कौन-सी जगह residual path को सिरे से सिरे तक बिल्कुल बिना normalize किए रखती है।

</details>

<details markdown="1"><summary>जाँचें</summary>

Post-norm layer norm को residual जोड़ने के बाद लगाता है, `LayerNorm(x + Sublayer(x))`; pre-norm उसे sublayer से पहले, residual शाखा के भीतर लगाता है, `x + Sublayer(LayerNorm(x))`। Pre-norm residual path को पूरे network में बिल्कुल साफ़ और बिना normalize किए छोड़ता है, यानी सिरे से सिरे तक बेरोक identity connection, जबकि post-norm की जगह हर layer पर residual योग को normalize करती है और उस साफ़ gradient path में बाधा डालती है। इसीलिए गहराई बढ़ने पर pre-norm ज़्यादा स्थिरता से train होता है।

</details>

4. ▢ लंबाई-4 का एक activation vector `[2, 4, 4, 6]` है। उसका mean और variance निकालें, फिर normalized (scale और shift से पहले का) layer norm output निकालें।

<details markdown="1"><summary>संकेत</summary>

Mean औसत होता है; variance mean से वर्ग-विचलन का औसत होता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

Mean: `(2+4+4+6)/4 = 4`। Mean से विचलन: `-2, 0, 0, 2`। Variance: `(4+0+0+4)/4 = 2`। Standard deviation: `sqrt(2) ≈ 1.414`। Normalized: `[-2, 0, 0, 2] / 1.414 ≈ [-1.414, 0, 0, 1.414]`, सीखे हुए scale (`gamma`) और shift (`beta`) लगने से पहले।

</details>

5. ▢ Transformer block में residual connections और layer normalization के बारे में कौन-सा दावा सही है?

    - a) Residual connections layer normalization की ज़रूरत को पूरी तरह बदल देते हैं
    - b) Layer norm हमेशा batch आयाम पर normalize करता है, batch norm की ही तरह
    - c) Residual connections gradients को गहरे stack में सीधा रास्ता देते हैं, और layer norm हर layer के activations को स्थिर, अनुमान-योग्य दायरे में रखता है, batch size से स्वतंत्र
    - d) Pre-norm और post-norm की जगह का किसी भी गहराई पर training की स्थिरता पर कोई असर नहीं पड़ता

<details markdown="1"><summary>जाँचें</summary>

**c)** हर हिस्सा अलग समस्या हल करता है: residuals गहराई के आर-पार gradient के प्रवाह को सँभालते हैं, layer norm batch size से स्वतंत्र activation scale को। (a) ग़लत है: वे अलग समस्याएँ हल करते हैं और दोनों मानक block में साथ आते हैं। (b) ग़लत है: layer norm और batch norm में यही तो फ़र्क़ है। (d) ग़लत है: pre-norm का post-norm पर फ़ायदा ख़ास तौर पर models के गहरे होने पर दिखता है।

</details>

## असली दुनिया का अभ्यास

- [ ] एक छोटे activation vector के लिए layer normalization को raw tensor operations (mean, variance, normalize, सीखा हुआ scale और shift) से लागू करें, और पक्का करें कि वह इस पाठ के worked example जैसी हाथ की गणना से मेल खाता है।
- [ ] पाठ 1 से 3 के अपने attention implementation को residual connection और layer norm में लपेटें, pre-norm या post-norm में से कोई एक जगह चुनकर, और लिख लें कि आपने कौन-सा चुना और क्यों।
- [ ] कल: "Layer Normalization" पेपर का abstract और परिचय पढ़ें, और ध्यान दें कि sequence models के लिए batch normalization की किस समस्या को हल करने के लिए वह मूल रूप से लिखा गया था।

## आगे बढ़ने के लिए

- [पेपर: "Layer Normalization", Ba, Kiros, and Hinton, 2016](https://arxiv.org/abs/1607.06450)
- [पेपर: "On Layer Normalization in the Transformer Architecture", Xiong et al., 2020](https://arxiv.org/abs/2002.04745)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
