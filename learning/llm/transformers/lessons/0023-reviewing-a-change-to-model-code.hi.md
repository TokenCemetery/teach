---
title: "23. Model Code में बदलाव की समीक्षा"
description: "किसी और के model code में किए बदलाव की समीक्षा करें और बताएँ कि वह क्या तोड़ता है या उसकी क्या क़ीमत है, विवरण पर भरोसा न करें"
type: lesson
---

# पाठ 23. Model Code में बदलाव की समीक्षा

**मिशन से संबंध:** मिशन तब ख़त्म होता है जब आप असली model code को पढ़ या बदल सकें और architecture उसके पीछे काला डिब्बा न रहे; इस कौशल का वरिष्ठ रूप है किसी और के उसमें किए बदलाव की समीक्षा करना और विवरण पर भरोसा करने के बजाय ठीक-ठीक बताना कि उसकी क्या क़ीमत है।
**मुख्य स्रोत:** [पेपर: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness", Dao et al., 2022](https://arxiv.org/abs/2205.14135), जिसका exactness वाला दावा (पाठ 22) इस पाठ के लिए नमूना है कि किसी भी "तेज़, output वही" दावे की जाँच कैसे करें।
**पूर्व-आवश्यकताएँ:** [0001-0003](0001-scaled-dot-product-attention.md) (attention), [0004-0011](0004-positional-encoding.md) (transformer blocks और training), [0012](0012-reading-real-model-code.md) (असली code पढ़ना), [0014, 0017](0014-rotary-position-embeddings.md) (आधुनिक variants), [0022](0022-mixture-of-experts-and-flashattention.md) (exactness)

## वार्म-अप

1. ▢ एक pull request दावा करती है "धीमे attention की जगह तेज़ attention लगाया, output वही।" इस दावे पर भरोसा करने से पहले आप सबसे पहले क्या जाँचते हैं?

<details markdown="1"><summary>जाँचें</summary>

यह कि output असल में मूल से floating-point सहनसीमा के भीतर संख्यात्मक रूप से मेल खाता है या नहीं। "तेज़" का अक्सर चुपचाप मतलब होता है "अलग": कोई सरलीकृत गणना या approximation जो थोड़ी ग़लत है। पाठ 22 ने FlashAttention के लिए ख़ास तौर पर exactness को कसौटी इसलिए बनाया क्योंकि यह ग़लती आम है।

</details>

2. ▢ एक diff positional encoding को sinusoidal से rotary में बदलता है। क्या आप पेपर पढ़े बिना देख सकते हैं कि बदलाव असल में क्या क़ीमत लेता है?

<details markdown="1"><summary>जाँचें</summary>

आप पाठ 14 से निकाल सकते हैं कि rotary encodings क्या करते हैं: वे attention चलने से पहले query और key vectors को घुमाते हैं, और इसी से वे position-सापेक्ष dot products पाते हैं। फिर आप जाँच सकते हैं कि diff वह rotation सही ढंग से लागू करता है या नहीं, और परख सकते हैं कि outputs किसी reference (पाठ 0001 के समीकरण) से मेल खाते हैं या नहीं।

</details>

3. ▢ एक बदलाव ablation का दावा करता है: "हमने weight decay पद हटाया और training अब भी converge होती है।" आप कौन-सा सवाल पूछते हैं?

<details markdown="1"><summary>जाँचें</summary>

क्या लेखक ने उसे नापा? क्या दावा उनके अपने training run से समर्थित है, या किसी blog post में किसी पेपर के सारांश से दोहराया गया है? Ablation का दावा उतना ही मज़बूत है जितना उसके पीछे का माप।

</details>

## यह जानें

### समीक्षा की जाँच-सूची: model-code के हर बदलाव को चार चीज़ें चाहिए

जिस समीक्षक ने transformer raw tensors से बनाया है उसके पास वह फ़ायदा है जो ज़्यादातर code समीक्षकों के पास नहीं: आप दावे को असली गणित से जाँच सकते हैं, सिर्फ़ यह देखकर नहीं कि code विश्वसनीय लगता है।

**1. क्या shapes सही ढंग से आगे चलते हैं?**

इस workspace की बार-बार आने वाली परंपरा: हर operation sequence length और embedding आयाम को बनाए रखता है। attention में कोई भी बदलाव (पाठ 3 का mask, पाठ 14 का RoPE, पाठ 17 का grouped-query) उसे तोड़ना नहीं चाहिए। जाँचें:

- Operation का input: shape `(batch, seq_len, d_model)` या `(batch, num_heads, seq_len, d_k)` जैसे घटक।
- Output: बाहर वही shape।
- दो layers आगे, क्या shape तोड़ने वाली गड़बड़ी छिपी है? ग़लत कोण से घुमाने वाला rotary embedding शायद तब तक फ़ेल न हो जब तक attention के dot-products बेमतलब न हो जाएँ। आगे के tests जाँचें या model को किसी ज्ञात input के साथ forward चलाएँ और बीच के shapes सत्यापित करें।

**2. अगर तेज़ी का दावा है, तो क्या output संख्यात्मक रूप से मेल खाता है?**

पाठ 22 ने यह रटवाया: FlashAttention exact है, approximate नहीं। वह वही समीकरण compute करता है, बस memory को अलग ढंग से छूकर। उसे floating-point सहनसीमा के भीतर वही `output` देना **चाहिए**।

जब कोई diff output बदले बिना तेज़ होने का दावा करे:

- पुराने code और नए code के साथ model को उसी random input पर चलाएँ। Attention outputs निकालें (या पूरा forward pass, अगर diff उससे ऊपर की ओर है)।
- Outputs की तत्व-दर-तत्व तुलना करें। उन्हें floating-point rounding के भीतर मेल खाना चाहिए, आम तौर पर precision के हिसाब से 1e-5 से 1e-4। अगर वे इससे ज़्यादा अलग हों, तो बदलाव पारदर्शी speedup नहीं है; वह अलग गणना है जो ख़ुद को वही बता रही है।

**3. क्या बदलाव उसके सामने उचित है जिसे वह बदलता है?**

पाठ 5 (layer norm, residuals) और 19 (initialization, warmup, gradient clipping, mixed precision) सुरक्षा-रेखाएँ हैं: हर एक किसी ऐसी चीज़ से बचाती है जिस पर इसके बिना training loop फ़ेल हो सकता है। इनमें से किसी में भी बदलाव को यह उचित ठहराना होगा कि नई सुरक्षा पर्याप्त क्यों है।

उदाहरण:

- "हमने layer norm की जगह RMSNorm लगाया": RMSNorm re-centering हटा देता है। क्या code दिखाता है कि वह अब भी pre-norm (पाठ 5) की तरह इस्तेमाल हो रहा है, जहाँ centering पहले से वैकल्पिक थी?
- "हमने learning rate schedule बढ़ाई": क्या बदलाव में उसका हिसाब है जिससे warmup, gradient clipping और mixed precision बचा रहे थे?
- "हमने gradient clipping हटाई": क्या आप पहले असल में clip कर रहे थे? क्या आप अब loss के उछाल या training की अस्थिरता देखने को तैयार हैं?

एक आम ग़लती: किसी असंबंधित model से config मान कॉपी करना और बाक़ी कुछ न बदलना। "हमारा model 7B parameters का है; मैं उस 70B model की learning rate इस्तेमाल करूँगा जो मुझे मिला।" वह rate 70B के लिए चुनी गई थी; context, batch size और loss की वक्रता सब अलग हैं।

उचित बदलाव या तो पुरानी सुरक्षा-रेखा का मक़सद समझाता है और यह कि नए setup को उसकी ज़रूरत क्यों नहीं, या माप दिखाता है कि training loop उसके बिना टिकता है।

**4. क्या ablation का दावा असली माप से समर्थित है?**

फिर पाठ 22: "FlashAttention identical output देता है" ऐसा दावा है जिसे आप outputs की तुलना करके सत्यापित कर सकते हैं। पर "हमने weight decay हटाया और training उतनी ही अच्छी है" अलग है: यह प्रायोगिक नतीजा है जो दावा करता है कि हटाया गया घटक मायने नहीं रखता था।

जाँचें:

- क्या बदलाव का लेखक वही है जिसने उसे नापा? किस dataset पर, किस random seed के साथ, कितने steps के लिए नापा?
- या दावा किसी पेपर के सारांश, blog post या किसी और के experiment से दोहराया गया है? अगर हाँ, तो क्या नया संदर्भ (आपके model का आकार, architecture, learning rate, batch size, dataset) मूल माप से मेल खाता है?

असली ablation को दूसरे हाथ के अधिकार पर मान लेना जोखिम भरा है, ख़ासकर अगर नया training run महँगा हो और नाकामी की क़ीमत भारी हो।

### अच्छा विवेक कैसा सुनाई देता है

Model-code के बदलाव की समीक्षा करते समय, वरिष्ठ इंजीनियर विवरण पर भरोसा करने के बजाय ठीक-ठीक बताता है कि किसी चुनाव की क्या क़ीमत या जोखिम है।

**इसके बजाय:** "मुझे यह ग़लत लगता है।"

**बेहतर:** "पाठ 14 निकालता है कि RoPE Q और K को `position * dimension_index` के अनुपात वाले कोण से घुमाता है। यह diff `position * constant` से घुमाता है। वह अलग function है। पेपर का सापेक्ष-position वाला गुण नहीं बनेगा। मर्ज करने से पहले मैं देखना चाहूँगा कि outputs किसी reference से मेल खाते हैं।"

**इसके बजाय:** "यह चलना चाहिए।"

**बेहतर:** "बदलाव residuals को वापस जोड़ने से पहले का `residual_scale` गुणक हटा देता है। पाठ 7 ने दिखाया था कि residual को scale करना ही वह तरीक़ा है जिससे पाठ 5 का pre-norm variant गहरे models में activation फूलने से बचता है। मैं training के दौरान हर layer पर gradient histograms देखना चाहूँगा, या समझना चाहूँगा कि यह ख़ास model बिना scaling के स्थिर क्यों रहता है।"

**इसके बजाय:** "लेखक कहते हैं कि यह काम करता है।"

**बेहतर:** "यह RMSNorm है, जिसे पेपर pre-norm में लगाता है। हमारा code post-norm (पाठ 5) इस्तेमाल करता है। Re-centering के बिना RMSNorm pre-norm में ठीक हो सकता है पर post-norm में जोखिम भरा। मैं या तो pre-norm में बदलना चाहूँगा या outputs की सावधानी से तुलना करना।"

फ़र्क़: यह नाम लेना कि बदलाव क्या करता है, वह किससे बचाता है या उसकी क्या क़ीमत है, और कौन-सा सबूत सवाल का निपटारा करेगा, यह कहने के बजाय कि बदलाव सही या ग़लत लगता है।

## अभ्यास

1. ▢ एक diff sinusoidal positional encoding (पाठ 4) को rotary (पाठ 14) से बदलता है। आपकी जाँचें: कौन-से shapes अब भी मेल खाने चाहिए, और आप सबसे पहले क्या परखते हैं?

<details markdown="1"><summary>जाँचें</summary>

Shapes: input `(batch, seq_len, d_model)`, output `(batch, seq_len, d_model)`। Rotation attention से पहले Q और K पर लगता है, इसलिए attention के input shapes नहीं बदलते, और attention का output shape अब भी `(batch, seq_len, d_model)` है।

सबसे पहले परखें: पुराने code और नए code के बीच, उसी random input पर, attention outputs (या अगर साफ़ तौर पर अलग कर सकें तो पूरे forward-pass outputs) की तुलना करें। अगर वे सहनसीमा के भीतर मेल खाते हैं, तो बदलाव गणना को बनाए रखता है। अगर वे अलग हैं, तो rotation के गणित में कुछ ग़लत है।

</details>

2. ▢ एक बदलाव दावा करता है "multi-head attention → grouped-query attention (पाठ 17), output में कोई अंतर नहीं।" आपका पहला शंकालु सवाल क्या है?

<details markdown="1"><summary>जाँचें</summary>

Grouped-query attention में key और value heads, query heads से कम होते हैं, इसलिए गणना सचमुच अलग है, भले ही वह multi-head के output का अनुमान लगाने के लिए बनी हो। "output में कोई अंतर नहीं" वाला दावा *बहुत मज़बूत* है। सही दावा है "output इतना क़रीब है कि आगे का प्रदर्शन नहीं बिगड़ता।"

आपकी जाँच: क्या outputs उस सहनसीमा के भीतर संख्यात्मक रूप से मेल खाते हैं जो आप मानने को तैयार हैं? शायद 1e-4 या उससे कसी हुई। अगर वे ठीक-ठीक मेल खाते हैं, तो शायद कुछ ग़लत है (हो सकता है आपने multi-head code कहीं ग़लती से सक्रिय छोड़ दिया हो)।

</details>

3. ▢ एक PR learning-rate warmup (पाठ 19) हटाती है। लेखक कहता है "model इसके बिना ठीक train होता है।" आप क्या पूछते हैं?

<details markdown="1"><summary>जाँचें</summary>

- क्या उन्होंने उसे नापा? इसी model, dataset और batch size पर?
- Warmup शुरू होने से पहले learning rate क्या थी? अगर शुरुआती rate अब कम है, तो हो सकता है बदलाव असल में warmup का फ़ायदा हटा ही नहीं रहा।
- क्या उन्होंने gradient के उछाल, मरी हुई layers, या असामान्य loss वक्र देखे? Warmup इन्हें रोकता है। अगर लेखक ने देखा नहीं, तो शायद उसने ग़ौर न किया हो।

आपके असली setup पर माप के बिना, आप अंदाज़ा लगा रहे हैं। Warmup सस्ता है; अगर वह काम करता है, तो रखें।

</details>

4. ▢ Model-code के बदलाव की समीक्षा के बारे में कौन-सा कथन सबसे उपयोगी दिशानिर्देश है?

    - a) लेखक के विवरण पर भरोसा करें और इसके बजाय code की शैली पर ध्यान दें
    - b) attention या training loop में हर बदलाव को अस्वीकार करें; इन्हें बदलना बहुत जोखिम भरा है
    - c) जब बदलाव दावा करे कि वह output नहीं बदलता तो outputs की संख्यात्मक तुलना करें, और जब बदलता है तो ख़ास क़ीमत का नाम लें
    - d) माँग करें कि हर ablation नतीजा किसी प्रकाशित पेपर से समर्थित हो, तभी स्वीकार किया जाए

<details markdown="1"><summary>जाँचें</summary>

**c)** जब बदलाव दावा करे कि वह output नहीं बदलता तो outputs की संख्यात्मक तुलना करें, और जब बदलता है तो ख़ास क़ीमत का नाम लें।

(a) इसी तरह ग़लतियाँ शिप होती हैं। (b) हद से ज़्यादा सतर्क है; पूरा मक़सद ही बदलावों को ध्यान से परखने में सक्षम होना है। (d) बहुत सख़्त है; कोई उपयोगी बदलाव प्रकाशन से पहले आ सकता है, और आपके असली setup पर माप अक्सर किसी पेपर के अलग पैमाने पर माप से ज़्यादा प्रासंगिक होता है।

</details>

5. ▢ एक diff RMSNorm (पाठ 15) की जगह post-norm से pre-norm (पाठ 5) में बदलता है। बदलाव पर भरोसा करने से पहले आप एक कौन-सी चीज़ सत्यापित करते हैं?

<details markdown="1"><summary>संकेत</summary>

सोचें कि पाठ 5 के अनुसार हर जगह किसलिए है, और RMSNorm layer norm की तुलना में क्या छोड़ देता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

Pre-norm RMSNorm इसलिए काम करता है कि RMSNorm सिर्फ़ re-scale करता है (re-center नहीं), और pre-norm को activation फूलने से रोकने के लिए re-centering की ज़रूरत नहीं: अगले block में जाने वाला residual असीमित है, पर *उस* block का normalization उसे सँभाल लेता है।

Post-norm अलग है: residual output असीमित है, और layer norm की re-centering आंशिक रूप से इसकी वजह थी कि post-norm स्थिर रहा। RMSNorm re-centering छोड़ देता है। आप activation histograms की तुलना करना चाहेंगे (क्या वे फूल रहे हैं?), training वक्र (क्या अस्थिरता दिखती है?), या कम से कम कोई त्वरित परीक्षण चलाना चाहेंगे कि बदलाव से पहले और बाद loss वक्र मेल खाते हैं या नहीं।

</details>

## असली दुनिया का अभ्यास

- [ ] अगली बार जब आप किसी model में, जिस पर आप काम करते हैं या जिसे समझते हैं, attention, positional encoding या training loop बदलने वाली PR देखें, तो ऊपर की चार-बिंदु जाँच-सूची इस्तेमाल करें: shapes, output की exactness, जिसे वह बदलता है उसके सामने औचित्य, और ablation के किसी भी दावे के पीछे का माप।
- [ ] उसी PR पर (या अपनी ही), ऐसी समीक्षा टिप्पणी लिखने का अभ्यास करें जो ठीक-ठीक बताए कि बदलाव क्या करता है और कौन-सी चीज़ सवाल का निपटारा करेगी, यह कहने के बजाय कि वह सही या ग़लत लगता है।
- [ ] कल: अगर आप इस हफ़्ते अपना model code बदलते हैं (layer बदलना, activation की अदला-बदली, schedule समायोजित करना), तो जाँचें कि क्या आप जमा करने से पहले shapes और outputs को संख्यात्मक रूप से सत्यापित कर सकते हैं। अगर नहीं कर सकते, तो आपको असल में पता नहीं कि आपने कुछ ज़रूरी बदला या कुछ भी नहीं।
- [ ] कल: attention, embeddings या training की किसी तरकीब के बारे में कोई सुना हुआ दावा दोबारा देखें। मूल पेपर पर जाएँ (blog post के सारांश पर नहीं) और जाँचें कि दावा पेपर के असली समीकरणों से मेल खाता है या नहीं। पाठ 12 ने दिखाया कि असली code कैसे ढूँढें; अब वह कौशल और [संसाधन](../RESOURCES.md) में दिए पेपर एक विवादित बिंदु का निपटारा करने में इस्तेमाल करें।

## आगे बढ़ने के लिए

- [पेपर: "RoFormer: Enhanced Transformer with Rotary Position Embedding"](https://arxiv.org/abs/2104.09864), Su et al.। इस्तेमाल: rotary embeddings का मूल गणित, दावों को पेपर के असल कथन से जाँचने के लिए।
- [पेपर: "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints"](https://arxiv.org/abs/2305.13245), Ainslie et al.। इस्तेमाल: grouped-query attention का design, approximation वाले दावे को जाँचने और यह समझने के लिए कि वह कौन-सा सौदा करता है।
- [पेपर: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness"](https://arxiv.org/abs/2205.14135), Dao et al.। इस्तेमाल: यह पक्का करने के लिए कि FlashAttention exact है, approximate नहीं, और यह देखने के लिए कि वे उसे reference implementations से कैसे सत्यापित करते हैं।
- जब आप learning rate, gradient clipping या mixed precision में बदलावों की समीक्षा कर रहे हों, तब [training loop के पाठ](0019-initialization-warmup-and-gradient-clipping.md) दोबारा देखें। उन पाठों के "आगे बढ़ने के लिए" खंड हर सुरक्षा-रेखा के पीछे के पेपरों से जोड़ते हैं।
- जो शब्द फिसलन भरा लगे उसके लिए [शब्दावली](../GLOSSARY.md)।
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
