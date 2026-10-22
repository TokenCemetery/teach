---
title: "22. Contamination और Held-Out Design"
description: "सही key से split करना, और सवाल के हिसाब से आकार तय करना"
type: lesson
---

# पाठ 22. Contamination और Held-Out Design

**मिशन से संबंध:** जिस held-out सेट पर आप भरोसा नहीं कर सकते वह बिना सेट के से बदतर है, क्योंकि वह आत्मविश्वास भरे ग़लत फ़ैसले पैदा करता है।
**मुख्य स्रोत:** [कोड: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
**पूर्व-आवश्यकताएँ:** [पाठ 21](0021-building-the-dataset.md)

## वार्म-अप

1. ▢ Split करने से पहले deduplicate क्यों करें?

<details markdown="1"><summary>जाँचें</summary>

Split के आर-पार पड़ने वाला दोहरा जोड़ा एक training example को held-out सेट में रख देता है, इसलिए held-out प्रदर्शन memorisation मापता है।

</details>

2. ▢ Fine-tuning क्या बुरा सिखाती है?

<details markdown="1"><summary>जाँचें</summary>

नए तथ्य, ऐसी reasoning जो पहले से मौजूद न हो, ताज़ा जानकारी, और सटीक गणना। वह format, tone और एकरूपता अच्छा सिखाती है।

</details>

3. ▢ आप कौन-सा checkpoint ship करते हैं?

<details markdown="1"><summary>जाँचें</summary>

वह जो held-out के न्यूनतम पर है, जो मानकर चलता है कि आपके पास ऐसा held-out सेट है जिस पर भरोसा किया जा सके।

</details>

## यह जानें

### Contamination के दो प्रकार

**आपकी contamination।** Test examples जो आपके training सेट में भी हूबहू या लगभग वैसे ही मौजूद हैं। पूरी तरह आपके नियंत्रण में, और जब हो तो पूरी तरह आपकी ग़लती।

**विरासत में मिली contamination।** Test examples जो base model के *pretraining* corpus में आए थे। आपके नियंत्रण में नहीं, बाहर से बड़े पैमाने पर अपहचानने योग्य, और यही वजह है कि public benchmark scores को संदेह से पढ़ना चाहिए। अगर कोई benchmark base model से पहले का है और public web पर रहता है, तो मान लें कि कुछ जोखिम हुआ है।

व्यावहारिक नतीजा: **public benchmark आपके फ़ैसले के लिए कमज़ोर संकेत है।** वह उस चीज़ की याद माप सकता है जो base पहले ही देख चुका है। आपका अपना, ताज़ा बनाया held-out data मज़बूत संकेत है, और वही अकेली चीज़ है जिस पर आप सचमुच भरोसा कर सकते हैं।

### ठीक से split करना

Random splitting default है और अक्सर ग़लत होती है। आप *किस आधार पर* split करते हैं, वह तय करता है कि आप कौन-सी generalisation माप रहे हैं।

| किस आधार पर split | क्या मापता है | कब इस्तेमाल करें |
|---|---|---|
| Random example | नए examples पर generalisation | Examples सचमुच स्वतंत्र हों |
| Group या entity | नई entities पर generalisation | कई examples एक customer, document, लेखक साझा करें |
| समय | भविष्य पर generalisation | Data में थोड़ी भी समय की संरचना हो |

**Group leakage** क्लासिक चुपचाप होने वाली विफलता है। एक source document से निकले दस examples, random split में, कुछ train में और कुछ test में डालते हैं। Model उस document की सामग्री देख चुका है और उसका held-out score उसे दर्शाता है। Document के आधार पर split करें।

![छह examples, चार document A से और दो B से, दो तरह से split। Random split में, A के examples train bin और test bin दोनों में पड़ते हैं; document के आधार पर split में, पूरा A एक bin में और पूरा B दूसरे में।](images/on-both-sides.svg)

वही छह examples दोनों पटलों में हैं; सिर्फ़ बँटवारा बदलता है। बाईं ओर एक document दोनों bins में है, जो रिसाव है, और कहीं और का कोई भी held-out अनुशासन उसे नहीं मिटाता।

**Temporal leakage** दूसरा है। अपने test अवधि के बाद के data पर training का मतलब है कि model भविष्य देख चुका है, और आपका score ऐसे आशावादी ढंग से ऊँचा है जो deployment में नहीं टिकेगा। समय का आयाम रखने वाले किसी भी dataset को समय से split करना चाहिए, और यही वह split है जिसे लोग सबसे ज़्यादा छोड़ते हैं क्योंकि random आसान है।

### दो नहीं, तीन splits

- **Train।** जिस पर model फ़िट होता है।
- **Validation।** जिसे आप checkpoints, rank, learning rate और बाक़ी सब कुछ चुनने के लिए इस्तेमाल करते हैं।
- **Test।** अंत में एक बार छुआ जाता है, असली प्रदर्शन का अनुमान लगाने के लिए।

तीन की वजह यह है कि किसी सेट के विरुद्ध चुनाव करना उस पर फ़िट होना है। Validation से checkpoint चुनें, validation पर बीस configurations की तुलना करें, सबसे अच्छी चुनें, और validation score अब उतना आशावादी है जितने चुनाव आपने उसके विरुद्ध किए। इसीलिए test सेट है और इसीलिए उसे एक बार इस्तेमाल किया जाता है।

**व्यवहार में लोग दो इस्तेमाल करते हैं, फिर सोचते हैं कि deployment उनके evaluation से कम क्यों निकलता है।** फ़ासला ठीक उतना है जितना चुनाव उन्होंने किया।

### अपनी contamination पहचानना

Deduplication को सिर्फ़ training सेट के भीतर नहीं, test सेट के विरुद्ध भी साफ़ तौर पर करें:

1. Normalise करें: lowercase, whitespace समेटें, विराम-चिह्न हटाएँ।
2. Train और test के आर-पार exact-match hash। Train से हर टकराव हटाएँ।
3. MinHash या embedding similarity से लगभग-दोहरे की पहचान, ऐसी सीमा के साथ जिसे आपने हाथ से देखा हो।
4. **सबसे ज़्यादा similarity वाले जोड़े ख़ुद पढ़ें।** सीमाएँ अंदाज़े हैं; आपकी आँखें calibration हैं।

चरण 4 वह है जिसे लोग छोड़ते हैं और वही असली समस्याएँ ढूँढता है।

### Held-out सेट का आकार तय करना

Held-out सेट आम तौर पर उन निष्कर्षों का समर्थन करने के लिए बहुत छोटे होते हैं जो उनसे निकाले जाते हैं। मोटा आकार: छोटे फ़र्क़ पहचानने के लिए बहुत examples चाहिए, और जिस फ़र्क़ की आपको परवाह है उसके सिकुड़ने पर संख्या वर्गीय रूप से बढ़ती है।

| जो फ़र्क़ पहचानना चाहते हैं | ज़रूरी मोटा पैमाना |
|---|---|
| 10 प्रतिशत अंक | कुछ सैकड़े |
| 5 प्रतिशत अंक | लगभग एक हज़ार |
| 1 से 2 प्रतिशत अंक | हज़ारों से दसियों हज़ार |

ये आँकड़े हर model के लिए हैं, लगभग 70% accuracy पर, दो स्वतंत्र samples की तुलना करते हुए, सामान्य 5% significance level और 80% power के साथ: 10 अंकों के लिए लगभग 290 examples, 5 के लिए लगभग 1,250, और 2 के लिए लगभग 8,000। उन्हीं examples पर paired comparison (नीचे) को कम चाहिए।

तो 50-example वाला held-out सेट आपको बता सकता है कि model बिल्कुल काम करता है या नहीं। वह नहीं बता सकता कि rank 32 ने rank 16 को दो अंक से हराया या नहीं, और उसे ऐसा मानना जैसे वह बता सकता है बहुत आम भूल है।

उसका निष्कर्ष: अगर आपके पास 200 held-out examples हैं, तो बारह-configuration का sweep न चलाएँ। Sweep का विजेता ज़्यादातर noise है, और आपने एक random configuration चुनने में compute ख़र्च किया।

### Paired comparison

दो models की तुलना करते समय, दोनों को **एक ही examples** पर evaluate करें और प्रति-example तुलना करें। Paired comparison, example की कठिनाई से आने वाला variance हटाता है और दो स्वतंत्र औसतों की तुलना से कम examples के साथ छोटे फ़र्क़ पहचानता है। इसकी क़ीमत बस हिसाब-किताब है।

प्रति-example नतीजे रखें, सिर्फ़ कुल नहीं। "Model B 3 अंक बेहतर है" "B ने A के ग़लत किए 14 examples ठीक किए और A के सही 6 बिगाड़ दिए" से कहीं कम उपयोगी है, और वे छह वहाँ हैं जहाँ आप कुछ सीखते हैं।

## अभ्यास

1. ▢ आपकी contamination और विरासत में मिली contamination में भेद बताएँ, और कहें कि हर एक का क्या मतलब है।

<details markdown="1"><summary>जाँचें</summary>

आपकी: test examples जो आपके training सेट में भी हैं। रोकी जा सकने वाली, पहचानने योग्य, आपकी ज़िम्मेदारी।

विरासत में मिली: test examples जो base model के pretraining corpus में हैं। नियंत्रित नहीं, बड़े पैमाने पर अपहचानी, और यही वजह है कि public benchmark scores आपके फ़ैसले के लिए कमज़ोर सबूत हैं।

मतलब यह कि किसी भी public benchmark से ज़्यादा ताज़ा बनाए गए निजी held-out data पर भरोसा करें।

</details>

2. ▢ आपके dataset में 50 source documents से निकले 500 examples हैं। आप random split करते हैं और 96% held-out accuracy पाते हैं। क्या ग़लत है?

<details markdown="1"><summary>जाँचें</summary>

Group leakage। एक ही document के examples दोनों splits में हैं, इसलिए model उस document की सामग्री देख चुका है और score याद को दर्शाता है।

Document के आधार पर split करें: एक document के सारे examples एक तरफ़ जाएँ। ईमानदार संख्या के काफ़ी कम निकलने की उम्मीद रखें।

</details>

3. ▢ दो के बजाय तीन splits क्यों?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि किसी सेट के विरुद्ध चुनाव करना उस पर फ़िट होना है। Validation पर किया गया हर checkpoint चुनाव और configuration तुलना validation score को आशावादी बनाती है।

Test सेट अंत तक अछूता रहता है, इसलिए निष्पक्ष अनुमान देता है। सिर्फ़ दो splits के साथ, आपकी बताई संख्या में आपका सारा चुनाव शामिल है, जो ठीक वही फ़ासला है जो लोग evaluation और deployment के बीच देखते हैं।

</details>

4. ▢ आपके पास 80 held-out examples हैं और आप जानना चाहते हैं कि rank 64 ने rank 16 को हराया या नहीं। क्या आप जान सकते हैं?

<details markdown="1"><summary>जाँचें</summary>

तब तक नहीं जब तक फ़र्क़ बहुत बड़ा न हो। तालिका की मान्यताओं के तहत, अस्सी examples सिर्फ़ लगभग बीस अंकों का झटका पहचान सकते हैं; दो वाजिब ranks के बीच का फ़र्क़ आम तौर पर ज़्यादा से ज़्यादा कुछ अंक होता है।

या तो ज़्यादा held-out data लाएँ या मान लें कि आपके पास जो है उससे यह सवाल अनुत्तरणीय है। फिर भी जवाब देना आत्मविश्वास भरा ग़लत फ़ैसला पैदा करता है।

</details>

5. ▢ कौन-सा split सबसे ज़्यादा छोड़ा जाता है, और छोड़ने की क्या क़ीमत है?

    - a) Data समय-क्रम में हो तब उसे समय से split करना
    - b) Data को सभी उपलब्ध examples में random split करना
    - c) Data को output की लंबाई से संतुलित buckets में split करना
    - d) Data को इस आधार पर split करना कि label किस annotator ने बनाया

<details markdown="1"><summary>जाँचें</summary>

**a)** Data समय-क्रम में हो तब उसे समय से split करना।

Random आसान है और default है, इसलिए समय की संरचना अनदेखी रह जाती है। क़ीमत है test अवधि के बाद के data पर training: model ने भविष्य देख लिया है, और score deployment में नहीं टिक सकता।

</details>

6. ▢ दो औसतों की तुलना से paired comparison बेहतर क्यों है?

<details markdown="1"><summary>जाँचें</summary>

वह दोनों models की तुलना एक ही items पर करके example की कठिनाई से आने वाला variance हटा देता है, इसलिए कम examples के साथ छोटे फ़र्क़ पहचानता है।

वह ज़्यादा उपयोगी नतीजा भी देता है: कौन-से ख़ास examples सुधरे और कौन-से बिगड़े। बिगड़े हुए ही वह जगह हैं जहाँ सीख है।

</details>

## असली दुनिया का अभ्यास

- [ ] अपने dataset में समूह की संरचना जाँचें: document, customer, लेखक, session। अगर कोई है, तो उसके आधार पर दोबारा split करें और दोनों held-out संख्याओं की तुलना करें।
- [ ] Train और test के बीच लगभग-दोहरे की पहचान चलाएँ। सबसे ज़्यादा similarity वाले बीस जोड़े हाथ से पढ़ें।
- [ ] तीन सेट में split करें और लिख लें कि हर एक किसके लिए इस्तेमाल हो सकता है। फिर उस पर टिके रहें।
- [ ] कल: निकालें कि जिस फ़र्क़ की आपको सचमुच परवाह है उसे पहचानने के लिए कितने held-out examples चाहिए होंगे। उसकी तुलना अपने पास मौजूद संख्या से करें।

## आगे बढ़ने के लिए

- [कोड: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
- [दस्तावेज़: Splitting datasets, Hugging Face Datasets](https://huggingface.co/docs/datasets/main/en/process)
- [पाठ 23. ऐसी Metrics जिनका मतलब हो](0023-metrics-that-mean-something.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
