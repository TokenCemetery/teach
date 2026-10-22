---
title: "22. Sandboxing और Approval Gates"
description: Execution की सीमाएँ और मानवीय चौकियाँ जो model की ग़लतियों से बचाती हैं
type: lesson
---

# पाठ 22. Sandboxing और Approval Gates

**मिशन से संबंध:** यह तय करने के लिए कि agent बिना निगरानी के क्या कर सकता है, आपको ग़लतियों से बचाने वाले दो पूरक mechanisms समझने होंगे: sandbox लागू करता है कि code क्या छू सकता है, चाहे model ने कुछ भी माँगा हो, और approval gates ऊँचे दाँव वाले actions से पहले मानवीय चौकी जोड़ते हैं।
**मुख्य स्रोत:** [लेख: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**पूर्व-आवश्यकताएँ:** [पाठ 21](0021-provider-formats-and-discovery-at-scale.md), [Harness](../GLOSSARY.md)

## वार्म-अप

1. ▢ Client tool और server tool में क्या अंतर है, इस नज़रिए से कि code कहाँ चलता है और उसे कौन नियंत्रित करता है?

<details markdown="1"><summary>जाँचें</summary>

Client tool harness के अपने code में चलता है, इसलिए उसके execution पर आपका पूरा नियंत्रण है। Server tool harness की ओर से provider के infrastructure पर चलता है, इसलिए execution की सीमा provider नियंत्रित करता है। यह security के लिए मायने रखता है क्योंकि client tool का व्यवहार आपके code पर निर्भर है, जबकि server tool का व्यवहार इस पर कि provider क्या इजाज़त देता है।

</details>

2. ▢ पाठ 21 में हमने सीखा कि हर tool definition को पहले से context में लोड करने की जगह, model tools को गतिशील रूप से खोज और call कर सकता है। इस तरीक़े का एक फ़ायदा और एक क़ीमत बताएँ जो यह लाता है।

<details markdown="1"><summary>जाँचें</summary>

फ़ायदा: model का context सैकड़ों tool definitions से नहीं फूलता, इसलिए वह ज़्यादा साफ़ तर्क कर सकता है और tool definitions छोटी रखी जा सकती हैं या माँगने पर लाई जा सकती हैं। क़ीमत: model को अब जानने से पहले discovery या introspection tool call करना पड़ता है कि क्या उपलब्ध है, जो एक round trip जोड़ता है, या वह ऐसा tool call करता है जिसके होने का वह अंदाज़ा लगाता है और अगर वह नहीं है तो फेल होता है, जिसके लिए error handling और retries चाहिए।

</details>

## यह जानें

### Model का विवेक security की सीमा नहीं है

आप उम्मीद कर सकते हैं: "Model समझदारी से तय करेगा कि मेरी दी हुई पहुँच का क्या करना है। मैं इस पर भरोसा कर सकता हूँ कि model production data न मिटाने या बिना इजाज़त emails न भेजने का फ़ैसला करेगा।"

यह उम्मीद कई तरह से टूटती है। Model ग़लत हो सकता है: वह tool call के नतीजे ग़लत समझ सकता है। Model उस content से बहकाया जा सकता है जो वह पढ़ता है: अगर किसी file के preview या उपयोगकर्ता के message में model को चकमा देने के लिए बनाया गया विरोधी text है, तो वह text model की reasoning को प्रभावित कर सकता है। Model बस ग़लती भी कर सकता है: reasoning बड़े पैमाने पर फेल हो सकती है, ख़ासकर बहुत शाखाओं वाले परिदृश्यों में या समय के दबाव में। इन कारणों से, आपका harness tool को जो भी छूने देता है (disk की कौन-सी files, कौन-से network hosts, कौन-से commands चलाने हैं) उसे code से लागू करना होगा, इस उम्मीद से नहीं कि model सही व्यवहार करेगा।

इसीलिए security की सीमा model नहीं, harness है।

### Sandbox क्या है

Sandbox ऐसी execution सीमा है जिसे harness इस पर लागू करता है कि tool का code क्या छू सकता है, चाहे model ने कौन-से arguments भेजे हों। Model के instructions कभी अपने आप में security का गुण नहीं होते।

आम sandbox सीमाओं में शामिल हैं:

- **Filesystem की सीमा**: Tool सिर्फ़ किसी ख़ास directory tree के भीतर files पढ़ या लिख सकता है (उदाहरण के लिए, `/home/user/work` पर पर `/etc` या `/home/other_user` पर नहीं)। भले ही model tool से इस tree के बाहर के path तक पहुँचने को कहे, sandbox runtime पर उसे ठुकरा देता है।
- **Network का अलगाव**: Tool के पास network पहुँच बिल्कुल नहीं है, या वह सिर्फ़ ख़ास hosts की अनुमत सूची तक पहुँच सकता है। Model harness को मनाकर मनमाने domains तक पहुँच नहीं पा सकता।
- **Resource की सीमाएँ**: CPU समय, memory और wall-clock समय की सीमा तय है। अगर model का code अनंत loop में फँस जाए, तो sandbox उसे सारे resources खाने की जगह बंद कर देता है।
- **Process का अलगाव**: Tool घटे हुए अधिकारों के साथ अलग process या container में चलता है, इसलिए वह harness को प्रभावित नहीं कर सकता या उन system resources तक नहीं पहुँच सकता जो उसे साफ़ तौर पर नहीं दिए गए।

मुख्य अंतर्दृष्टि यह है कि ये सीमाएँ execution के समय, harness के code में लागू की जाती हैं, भाषा के स्तर पर नहीं। Tool चतुर code लिखकर sandbox से नहीं निकल सकता। Sandbox वह नियम है जो harness लागू करता है, ऐसी ख़ूबी नहीं जिसका tool सम्मान करे।

### Approval gate क्या है

Approval gate पूरक mechanism है: जोखिम भरी श्रेणी की tool call चलाने से पहले, harness रुकता है और इंतज़ार करता है कि कोई इंसान उस ख़ास call की समीक्षा करके उसे मंज़ूर या नामंज़ूर करे।

Approval gates इन गुणों वाले actions पर लागू होते हैं:

- जिन्हें पलटा नहीं जा सकता या पलटना कठिन है: files मिटाना, emails भेजना, आर्थिक लेन-देन करना, इंटरनेट पर प्रकाशित करना।
- ग़लत होने पर भारी नतीजा: दाँव पर असली पैसा, असली नुक़सान, या असली privacy का उजागर होना है।
- सचमुच अनुमान लगाना कठिन: model का फ़ैसला उचित तो है पर साफ़ तौर पर सही नहीं, इसलिए इंसानी विवेक जोड़ना कीमती है।

Gate agent loop को रोकता है और लंबित tool call को (उसके arguments और अपेक्षित असर के साथ) किसी इंसान के सामने रखता है, मंज़ूरी या नामंज़ूरी का इंतज़ार करता है, फिर उसी हिसाब से loop जारी रखता या रोकता है।

### Sandboxes और approval gates पूरक हैं, विकल्प नहीं

ये दो अलग सुरक्षाएँ हैं जो साथ काम करती हैं:

- Sandbox सीमित करता है कि कोई भी call कितना नुक़सान कर सकती है, भले ही मंज़ूर हो या अपने आप चली हो। अगर कोई call किसी तरह ग़लत हो जाए, तो sandbox नुक़सान का दायरा थामे रखता है। "यह सीमित माहौल में चलता है" हमेशा सच है।
- Approval gate सबसे ऊँचे दाँव वाली calls के लिए इंसानी फ़ैसले का बिंदु जोड़ता है। वह सारा नुक़सान नहीं रोकता; बस यह पक्का करता है कि जिन calls से पछतावा होने की सबसे ज़्यादा संभावना है उन पर पहले इंसानी नज़र पड़े।

अगर आप हर call को sandbox करें पर कुछ भी gate न करें, तो model की अनदेखी ग़लती sandbox की सीमाओं के भीतर फिर भी नुक़सान कर सकती है। अगर आप हर एक tool call को gate करें, तो agent स्वायत्त नहीं रहता और अतिरिक्त चरणों के साथ इंसान ही सारा काम करने लगता है, जिससे automation का मक़सद ख़त्म हो जाता है।

सही संतुलन: सचमुच ऊँचे दाँव वाले actions (मिटाना, भेजना, प्रकाशित करना, ख़र्च करना) की संकरी श्रेणी को gate करें जहाँ इंसानी विवेक latency की क़ीमत के लायक़ है, और बाक़ी सबको sandbox करें ताकि उस gate के बाहर की कोई भी चीज़ कुछ ग़लत होने पर भी अपनी सीमाओं से बाहर न निकल सके।

## अभ्यास

1. ▢ आप ऐसा agent बना रहे हैं जो साझा repository से documents पढ़कर उनका सारांश बना सकता है। Repository में 10,000 files हैं, और उनमें से कुछ में संवेदनशील ग्राहक data है जिस तक agent की पहुँच नहीं होनी चाहिए। आप ऐसा client tool जोड़ना चाहते हैं जो agent को files पढ़ने दे। आपको कौन-सी sandbox सीमा लागू करनी चाहिए, और क्यों?

<details markdown="1"><summary>जाँचें</summary>

आपको filesystem की सीमा लागू करनी चाहिए: tool सिर्फ़ किसी ख़ास मंज़ूर directory tree के भीतर की files पढ़ सकता है (उदाहरण के लिए, "public_docs" folder की सारी files पर "confidential" folder की कोई भी नहीं)। यह सीमा runtime पर तब जाँची जाती है जब model tool call करता है; भले ही model tool से confidential folder के path को पढ़ने को कहे, sandbox उसे ठुकरा देता है। यह model के file की सामग्री से बहक जाने या यह तय करने में reasoning की ग़लती करने से बचाता है कि क्या पढ़ना सुरक्षित है। Model का विवेक ("यह public लग रहा है") सीमा नहीं है; code सीमा है।

</details>

2. ▢ आपका agent code लिख सकता है और उसे sandboxed Python interpreter में चला सकता है। Sandbox CPU को 30 सेकंड और memory को 1 GB तक सीमित करता है। Model ऐसा program लिखता है जो अनंत loop शुरू करता है। क्या sandbox उसे रोकेगा?

<details markdown="1"><summary>संकेत</summary>

सोचें कि code के चलते समय CPU की सीमा पार होने पर क्या होता है, और क्या harness उस सीमा को पहचानकर लागू कर सकता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

हाँ, sandbox उसे रोक देगा। जब 30 सेकंड की CPU सीमा आती है, तो harness process बंद कर देता है। Model का code कभी हमेशा के लिए नहीं चलता; sandbox resource की सीमा execution के समय लागू करता है, parse या compile के समय नहीं। यही एक कारण है कि sandbox में resource की सीमाएँ ज़रूरी हैं: वे नेक इरादे वाले code को भी सारे resources खाने से रोकती हैं।

</details>

3. ▢ आप ऐसा agent डिज़ाइन कर रहे हैं जो उपयोगकर्ता की ओर से emails भेज सकता है। Agent के email भेजने से पहले approval gate जोड़ने का अच्छा कारण इनमें से कौन-सा है?

    - a) Model शायद subject line व्याकरण की दृष्टि से ग़लत लिख दे।
    - b) Model शायद ग़लत प्राप्तकर्ता को या ग़लत सामग्री के साथ email भेज दे, और एक बार भेजने के बाद email वापस नहीं लिया जा सकता।
    - c) Model शायद email server को धीमा कर दे।
    - d) Model के पास शायद अगला email भेजने के लिए विचार ख़त्म हो जाएँ।

<details markdown="1"><summary>जाँचें</summary>

**b)** Model शायद ग़लत प्राप्तकर्ता को या ग़लत सामग्री के साथ email भेज दे, और एक बार भेजने के बाद email वापस नहीं लिया जा सकता। यह ऐसा अपरिवर्तनीय, भारी नतीजे वाला action है जहाँ इंसानी विवेक latency की क़ीमत के लायक़ है। विकल्प a पर्याप्त भारी नतीजे वाला नहीं है (model अच्छा draft बना सकता है)। विकल्प c model की ग़लती नहीं है (यह system के बोझ के बारे में है)। विकल्प d का कोई अर्थ नहीं बनता (कहने पर model रुक जाता है)।

</details>

4. ▢ समझाएँ कि sandbox सारी ग़लतियाँ क्यों नहीं रोक सकता पर फिर भी ज़रूरी क्यों है। एक उदाहरण दें।

<details markdown="1"><summary>जाँचें</summary>

Sandbox इस पर सीमाएँ लागू करता है कि code किन resources तक पहुँच सकता है, इस पर नहीं कि code क्या ग़लतियाँ करता है। उदाहरण के लिए, sandbox किसी tool को `/etc/passwd` पर लिखने से runtime पर लिखना ठुकराकर रोक सकता है, पर वह model को मंज़ूर file में ग़लत सामग्री लिखने से नहीं रोक सकता, जैसे `/home/user/config/` की config file को अमान्य syntax से ओवरराइट कर देना। Sandbox का काम नुक़सान को थामना है, सही होना पक्का करना नहीं। Approval gates उन ऊँचे दाँव वाले फ़ैसलों को सँभालते हैं जिन्हें इंसानी विवेक चाहिए; sandboxes उन execution सीमाओं को सँभालते हैं जो नुक़सान के दायरे को क़ाबू से बाहर बढ़ने से रोकती हैं।

</details>

## असली दुनिया का अभ्यास

- [ ] Tool call का चित्र बनाएँ: model, harness, tool का code, और उसके चारों ओर sandbox दिखाएँ। लिखें कि model क्या नियंत्रित करता है (उसकी reasoning और tool का चुनाव) और harness क्या नियंत्रित करता है (सीमा)।
- [ ] अपने काम या रोज़ इस्तेमाल होने वाले system के तीन tools सूचीबद्ध करें। हर एक के लिए एक जोखिम भरा action (अगर हो) पहचानें जिसे approval gate से फ़ायदा होता, और एक sandbox सीमा जो समझदारी भरी होती।
- [ ] कल: "Building Effective Agents" का लेख पढ़ें और sandbox या gate का एक ठोस उदाहरण नोट करें। एक वाक्य में समझाएँ कि वह design चुनाव क्यों मायने रखता है।

## आगे बढ़ने के लिए

- [लेख: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
