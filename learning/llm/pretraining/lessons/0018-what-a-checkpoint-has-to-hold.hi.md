---
title: "18. Checkpoint में क्या रखना ज़रूरी है"
description: "जो checkpoint सिर्फ़ weights सहेजता है वह run को हू-ब-हू resume नहीं कर सकता, और कितनी बार save करें यह चुनना अपने आप में एक tradeoff है"
type: lesson
---

# पाठ 18. Checkpoint में क्या रखना ज़रूरी है

**मिशन से संबंध:** "ऐसी checkpointing योजना बना सकें जो node failure के बाद खोई हुई progress को सीमित रखे" "सफलता कैसी दिखती है" का वह बिंदु है जिसे यह चरण पूरा करता है। यह पाठ कवर करता है कि checkpoint में क्या होना चाहिए और कितनी बार save करना है; पाठ 19 कवर करता है कि run के बीच में node के विफल होने पर असल में क्या होता है।
**मुख्य स्रोत:** [पेपर: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
**पूर्व-आवश्यकताएँ:** [पाठ 17](0017-warmup-decay-and-growing-the-batch-mid-run.md)

## वार्म-अप

1. ▢ Rae et al. के अनुसार, बाक़ी सब बराबर होने पर, बड़े model को छोटे model से ऊँचा अधिकतम learning rate मिलता है या नीचा?

<details markdown="1"><summary>जाँचें</summary>

नीचा अधिकतम learning rate। Rae et al. सीधे कहते हैं कि जैसे-जैसे model size बढ़ता है, वे schedule का इस्तेमाल किया अधिकतम learning rate घटाते हैं।

</details>

2. ▢ Global gradient-norm clipping उस gradient का क्या करती है जिसका norm clipping सीमा से ऊपर जाता है?

<details markdown="1"><summary>जाँचें</summary>

वह पूरे gradient vector को अनुपात में rescale करती है ताकि उसका norm सीमा के बराबर हो जाए, जिससे एक अकेला update कितना बड़ा हो सकता है उस पर रोक लगती है, gradient को छोड़ने या learning rate बदलने के बजाय।

</details>

## यह जानें

### Checkpoint सिर्फ़ weights से ज़्यादा है

सिर्फ़ model के parameters सहेजना training को ठीक वहीं से resume करने के लिए काफ़ी नहीं है जहाँ वह रुकी थी। Training run को सही ढंग से resume करने के लिए कम से कम ये चाहिए: model के **parameters**; **optimizer state** (Adam के लिए, पाठ 8 में गिने momentum और variance, जिनके बिना optimizer असल में ठंडे सिरे से शुरू होता है); **step count और learning-rate schedule की स्थिति**, ताकि warmup और decay (पाठ 17) दोबारा शुरू होने के बजाय सही बिंदु से आगे चलें; और, हू-ब-हू दोहराव के लिए, **data-loader की स्थिति और random-number-generator state**, ताकि run restart बिंदु के आसपास चुपचाप data को दोबारा process न करे या छोड़ न दे। इनमें से कुछ भी छूटा हुआ checkpoint ज़ोर से विफल नहीं होता; वह ऐसे run में resume होता है जो जारी रहा लगता है, जबकि चुपचाप बिना रुके चले run से कुछ अलग train हो रहा होता है।

### Checkpoint की आवृत्ति अपने आप में tradeoff क्यों है

Checkpoint की सामग्री कितनी भी पूरी हो, एक save करने में समय और storage लगता है: बड़े model की पूरी state को टिकाऊ storage में लिखने में असली wall-clock समय लगता है, जिस दौरान training आम तौर पर रुकी होती है या कम से कम पूरी progress नहीं कर रही होती, और हर checkpoint असली disk space घेरता है, ख़ासकर अगर सिर्फ़ आख़िरी के बजाय कई हाल के रखे जाएँ। ज़्यादा बार checkpoint करने से यह सीमित रहता है कि विफलता कितनी progress नष्ट कर सकती है, क्योंकि सिर्फ़ आख़िरी checkpoint के बाद का काम ही जोखिम में रहता है। कम बार checkpoint करने से checkpoints पर कुल समय और storage कम ख़र्च होता है, उसी विफलता पर ज़्यादा progress खोने की क़ीमत पर। कोई भी छोर आम तौर पर सही नहीं है: सही आवृत्ति इस पर निर्भर करती है कि विफलताएँ असल में कितनी बार होने की उम्मीद है, उसे इससे तौलकर कि हर checkpoint लिखना असल में कितना महँगा है।

### असली run में विफलताएँ असल में कितनी बार होती हैं

OPT-175B की training का Zhang et al. का ब्योरा उस tradeoff के "विफलताएँ कितनी बार अपेक्षित हैं" वाले पक्ष को काल्पनिक के बजाय ठोस बनाता है। लगभग दो महीने की training में, hardware विफलताओं ने कम से कम 35 manual restarts और 100 से ज़्यादा hosts को बारी-बारी से बदलने में योगदान दिया, और लेखकों का अनुमान है कि उसके ऊपर 70 से ज़्यादा automatic restarts और हुए, एक अकेले training run पर। यह औसतन हर दो दिन में एक restart से कहीं ज़्यादा है, run की पूरी अवधि में लगातार। जो checkpointing योजना यह मानकर बनी हो कि विफलताएँ दुर्लभ, कभी-कभार की घटनाएँ हैं वह इस run के लिए बुरी तरह ग़लत होती; जो योजना मानती है कि विफलताएँ प्रक्रिया का नियमित, अपेक्षित हिस्सा हैं, और उसी हिसाब से checkpoint करती है, वही इस पैमाने के run को असल में चाहिए।

## अभ्यास

1. ▢ एक team training run को ऐसे checkpoint से resume करती है जिसमें model parameters सहेजे गए थे पर optimizer state नहीं। क्या ग़लत होता है, भले resumed run बाक़ी तरह से सामान्य रूप से जारी दिखे?

<details markdown="1"><summary>जाँचें</summary>

Optimizer असल में ठंडे सिरे से शुरू होता है: Adam के लिए, checkpoint से पहले जमा हुए momentum और variance खो जाते हैं, इसलिए resume करने के बाद के बिल्कुल पहले updates उससे अलग बर्ताव करते हैं जैसा training कभी न रुकने पर करते, भले parameters ख़ुद सही हों।

</details>

2. ▢ ज़्यादा बार checkpoint करने से विफलता कितनी progress नष्ट कर सकती है यह क्यों घटता है, और वह फ़ायदा पाने की क्या क़ीमत है?

<details markdown="1"><summary>जाँचें</summary>

विफलता होने पर सिर्फ़ सबसे हाल के checkpoint के बाद किया गया काम ही जोखिम में रहता है, इसलिए ज़्यादा हाल का checkpoint नुक़सान को ज़्यादा कसकर सीमित करता है। क़ीमत है हर checkpoint लिखने में लगा समय (जिस दौरान training आम तौर पर रुकी होती है) और हर एक का घेरा storage, दोनों जो जितनी ज़्यादा बार checkpoints save हों उतनी तेज़ी से जमा होते हैं।

</details>

3. ▢ Zhang et al. OPT-175B की लगभग दो महीने की training में कम से कम 35 manual restarts, 100 से ज़्यादा बदले गए hosts, और अनुमानित 70 से ज़्यादा automatic restarts बताते हैं। यह आँकड़ा समान पैमाने और अवधि के run की checkpointing योजना के पक्ष में क्या तर्क देता है?

<details markdown="1"><summary>जाँचें</summary>

यह कि checkpoint करने की आवृत्ति चुनते समय विफलताओं को नियमित और बार-बार होने वाली मानना चाहिए, दुर्लभ अपवाद नहीं। पूरे run में लगातार हर दो दिन में एक restart से कहीं ज़्यादा पर, कभी-कभार की विफलताओं के लिए बनी checkpointing योजना किसी भी समय बहुत ज़्यादा progress को खुला छोड़ देती।

</details>

## असली दुनिया का अभ्यास

- [ ] देखें कि आपकी पहुँच वाला training framework परिभाषित करता है कि सहेजे checkpoint में क्या जाता है (parameters, optimizer state, step count, RNG state), और जाँचें कि इस पाठ में बताई गई चारों में से कोई उसकी default configuration में छूटी हुई या वैकल्पिक है या नहीं।
- [ ] OPT पेपर (ऊपर linked) का "Hardware Failures" खंड पढ़ें और एक वाक्य लिखें कि विफलता पकड़े जाने के बाद लेखकों ने कौन-सी संचालन प्रक्रिया अपनाई, इससे पहले कि पाठ 19 उसे सीधे कवर करे।
- [ ] कल: अपने चुने किसी काल्पनिक run के लिए (कोई भी अवधि और पैमाना), checkpoint की वह आवृत्ति आँकें जो आप चुनेंगे, और एक वाक्य लिखें जो उसे बहुत ज़्यादा बार checkpoint करने की क़ीमत और बहुत कम बार checkpoint करने के जोखिम, दोनों के विरुद्ध सही ठहराए।

## आगे बढ़ने के लिए

- [पेपर: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
