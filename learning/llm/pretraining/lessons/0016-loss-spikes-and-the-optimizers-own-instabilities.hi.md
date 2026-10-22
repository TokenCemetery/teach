---
title: "16. Loss Spikes और Optimizer की अपनी अस्थिरताएँ"
description: "वही spike किसी ख़राब batch से भी आ सकता है और optimizer से भी, और दोनों में फ़र्क़ करने के लिए नियंत्रित तुलना चाहिए"
type: lesson
---

# पाठ 16. Loss Spikes और Optimizer की अपनी अस्थिरताएँ

**मिशन से संबंध:** "Loss curve देखकर बता सकें कि spike recover होने लायक़ है या पुराने checkpoint से restart चाहिए" "पूरी रूपरेखा" में इस चरण के "कब पूरा माना जाए" खाने में लिखा है। यह पाठ कवर करता है कि loss spike असल में कहाँ से आ सकता है, और मानक उपाय; पाठ 17 उस schedule को कवर करता है जो training को उसके इर्द-गिर्द ढालता है।
**मुख्य स्रोत:** [पेपर: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**पूर्व-आवश्यकताएँ:** [पाठ 15](0015-mixed-precision-at-scale-bfloat16-and-stochastic-rounding.md), [Loss spike](../GLOSSARY.md)

## वार्म-अप

1. ▢ bf16 की चौड़ी exponent range उसे training के दौरान fp16 से ज़्यादा क्षमाशील क्यों बनाती है, भले bf16 की precision कम है?

<details markdown="1"><summary>जाँचें</summary>

bf16 fp32 के पूरे 8 exponent bits रखता है, जिससे उसकी dynamic range fp32 जैसी ही है, इसलिए बड़े पैमाने पर gradients और activations में जो बड़े या छोटे मान दिखते हैं उनके उसमें overflow या underflow होने की संभावना कम होती है, भले वह उस range के भीतर मानों को fp16 से कम सटीकता से दर्शाता है।

</details>

2. ▢ bf16 parameter updates के लिए stochastic rounding इस्तेमाल करने के बाद भी Rae et al. ने कौन-सी सीमा बताई?

<details markdown="1"><summary>जाँचें</summary>

Stochastic rounding साधारण mixed-precision training के प्रदर्शन को पूरी तरह वापस नहीं पाता; वह एक राहत है, पूरा हल नहीं।

</details>

## यह जानें

### Loss spike अपनी वजह ख़ुद नहीं बताता

**Loss spike**, यानी run के बीच में training loss का अचानक और तेज़ उछाल, एक से ज़्यादा जगहों से आ सकता है: कोई एक असामान्य रूप से कठिन या बिगड़ा हुआ batch, पाठ 15 में बताई जैसी संख्यात्मक precision की समस्या, या optimizer में ही कुछ जो जिस पैमाने पर train हो रहा है वहाँ अस्थिर हो जाए। Loss curve से spike पढ़ने पर पता चलता है कि वह हुआ; अपने-आप यह नहीं पता चलता कि इनमें से कौन-सा उसका कारण था, और सही प्रतिक्रिया, यानी restart, hyperparameter में बदलाव, या कुछ भी नहीं, इस पर निर्भर करती है कि कौन-सा था।

### एक ठोस मामला: बड़े पैमाने पर Adafactor बनाम Adam

Rae et al. ठीक इसी तरह की जाँच का हल किया हुआ उदाहरण देते हैं। Adafactor ऐसा optimizer है जो Adam से कम memory इस्तेमाल करता है, जो सीधे उस memory budget के लिए मायने रखता है जो पाठ 8 ने गिना: छोटे optimizer-state footprint का मतलब हो सकता है बड़ा model fit करना, या उसी model को कम sharding के साथ fit करना। छोटे पैमानों पर, Rae et al. ने Adafactor pretraining को स्थिर और अच्छे प्रदर्शन वाला पाया। 7.1 अरब parameters पर यह टिकना बंद हो गया: उन्होंने Adafactor से train करते हुए loss divergences देखे जो उन्होंने 1.4 अरब parameters पर नहीं देखे थे, जबकि Adafactor run ने उस स्थिर Adam baseline से कम अधिकतम learning rate (`6 × 10^-5`) इस्तेमाल किया था जिससे उसकी तुलना हुई (`1.2 × 10^-4`)। अस्थिरता के विरुद्ध सामान्यतः आज़माई जाने वाली पहली चीज़ कम learning rate होती है; यहाँ वह काफ़ी नहीं थी, और इसी से Rae et al. यह निष्कर्ष निकाल पाए कि इस पैमाने पर अस्थिरता optimizer से ही आ रही थी, सिर्फ़ इसलिए नहीं कि learning rate बहुत ऊँचा रखा गया था।

### मानक उपाय: global gradient norm से clipping

अस्थिरता का मूल कारण जो भी हो, Rae et al. का सबसे सीधा उपाय global norm से **gradient clipping** है: model के हर parameter में पूरे gradient vector का norm (कुल परिमाण) निकालें, और अगर वह norm चुनी हुई सीमा से ऊपर जाए, तो optimizer step के उसे इस्तेमाल करने से पहले पूरे gradient को अनुपात में नीचे rescale करें ताकि उसका norm ठीक सीमा के बराबर हो। यह एक अकेले step का update कितना बड़ा हो सकता है उस पर रोक लगाता है, चाहे असामान्य रूप से बड़ा gradient किसी भी वजह से बना हो। Rae et al. अपने ज़्यादातर models के लिए clipping मान 1 रखते हैं, पर ख़ास तौर पर अपने दो सबसे बड़े, 7.1B model और ख़ुद Gopher, के लिए बेहतर स्थिरता के लिए उसे घटाकर 0.25 कर देते हैं, यह इसका सीधा, ठोस उदाहरण है कि इस सुरक्षा उपाय को पैमाना बढ़ने पर कसा जाता है, तय नहीं छोड़ा जाता।

## अभ्यास

1. ▢ एक team को training run के बीच में loss spike दिखता है। इस पाठ में बताए दो अलग मूल कारण बताइए जो वही दिखने वाला spike पैदा कर सकते हैं।

<details markdown="1"><summary>जाँचें</summary>

इनमें से कोई भी दो: कोई एक असामान्य रूप से कठिन या बिगड़ा हुआ batch, संख्यात्मक precision की समस्या (जैसे bf16 training में overflow या rounding की समस्या), या optimizer में ही अस्थिरता जो जिस पैमाने पर train हो रहा है वहाँ अस्थिर हो जाए।

</details>

2. ▢ कम learning rate 7.1B Adafactor run को स्थिर क्यों नहीं कर पाया, और उस विफलता से Rae et al. ने क्या निष्कर्ष निकाला?

<details markdown="1"><summary>संकेत</summary>

Adafactor run ने पहले ही उस स्थिर Adam baseline से कम learning rate इस्तेमाल किया था जिससे उसकी तुलना हुई।

</details>

<details markdown="1"><summary>जाँचें</summary>

Adafactor run का अधिकतम learning rate `6 × 10^-5` था, स्थिर Adam baseline के `1.2 × 10^-4` से कम, और फिर भी उसमें अस्थिरताएँ दिखीं। चूँकि कम learning rate ने इसे ठीक नहीं किया, Rae et al. ने निष्कर्ष निकाला कि अस्थिरता इस पैमाने पर optimizer से ही आ रही थी, सिर्फ़ ज़्यादा ऊँचे learning rate से नहीं।

</details>

3. ▢ Global gradient-norm clipping उस gradient का असल में क्या करती है जिसका norm clipping सीमा से ऊपर जाता है?

    - a) वह उस gradient को पूरी तरह छोड़ देती है और उस batch के लिए optimizer step छोड़ देती है
    - b) वह पूरे gradient vector को अनुपात में rescale करती है ताकि उसका norm सीमा के बराबर हो जाए
    - c) वह gradient के मानों को कम-precision format में round कर देती है
    - d) वह बाक़ी training के लिए learning rate को स्थायी रूप से घटा देती है

<details markdown="1"><summary>जाँचें</summary>

**b)** यही सटीक तंत्र है: norm को सीमा तक लाने के लिए अनुपात में rescaling, न कि छोड़ देना, precision में बदलाव, या schedule में स्थायी बदलाव। (a), (c) और (d) हर एक अलग, असंबंधित हस्तक्षेप का वर्णन करते हैं।

</details>

4. ▢ Rae et al. ज़्यादातर model sizes के लिए clipping मान 1 रखते हैं पर ख़ास तौर पर 7.1B model और Gopher (280B) के लिए उसे घटाकर 0.25 कर देते हैं। यह ठोस चुनाव इस बारे में क्या दर्शाता है कि स्थिरता के सुरक्षा उपाय कैसे तय किए जाते हैं?

<details markdown="1"><summary>जाँचें</summary>

यह कि gradient clipping जैसा सुरक्षा उपाय हर पैमाने पर ज़रूरी रूप से तय स्थिरांक नहीं होता; यहाँ उसे ख़ास तौर पर सबसे बड़े models के लिए कसा गया, जहाँ अस्थिरता का जोखिम सबसे ज़्यादा था, न कि उसी मान पर छोड़ा गया जो छोटे, ज़्यादा स्थिर runs के लिए इस्तेमाल हुआ।

</details>

## असली दुनिया का अभ्यास

- [ ] खोजें कि आपकी पहुँच वाले training framework में gradient clipping configuration option के रूप में कहाँ दिया गया है, और अगर कोई तय है तो उसका default clipping मान नोट करें।
- [ ] Gopher पेपर (ऊपर linked) का वह अनुच्छेद पढ़ें जो Adafactor-बनाम-Adam तुलना का वर्णन करता है, और एक वाक्य लिखें कि कौन-सा सबूत ख़ास तौर पर इस स्पष्टीकरण को ख़ारिज करता है कि "learning rate बस बहुत ऊँचा था"।
- [ ] कल: आगे देखे बिना, पाठ 17 के लिए एक वाक्य में अनुमान लिखें: यह देखते हुए कि Rae et al. training की बिल्कुल शुरुआत में learning rate को तुरंत अधिकतम मान से शुरू करने के बजाय धीरे-धीरे warm up करते हैं, ताज़ा initialize हुए, बिना train किए network पर पूरे learning rate से शुरू करने से क्या समस्या हो सकती है?

## आगे बढ़ने के लिए

- [पेपर: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
