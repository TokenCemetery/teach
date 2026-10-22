---
title: "28. Cascading Tool Errors और Hallucinated Arguments"
description: एक tool error का ग़लत फ़ैसलों तक ले जाना और उलझन में बदल जाना, और ऐसे सही type वाले पर झूठे arguments जिन्हें schemas नहीं पकड़ सकते
type: lesson
---

# पाठ 28. Cascading Tool Errors और Hallucinated Arguments

**मिशन से संबंध:** Trajectory में एक के बाद एक आने वाली विफलताओं और गढ़े हुए arguments को पहचानने से आप agent की विफलताओं का निदान उनकी असली जड़ पर कर पाते हैं, श्रृंखला को बिगड़ने से पहले तोड़ते हुए, आगे के लक्षणों पर पैबंद लगाने की जगह।
**मुख्य स्रोत:** [लेख: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**पूर्व-आवश्यकताएँ:** [पाठ 27](0027-loops-and-context-poisoning.md)

## वार्म-अप

1. ▢ पाठ 27 से: दोहराव वाले loop और context poisoning में क्या अंतर है?

<details markdown="1"><summary>जाँचें</summary>

दोहराव वाला loop शोरभरा है: agent वही tool वही arguments के साथ बार-बार call करता है, कोई प्रगति नहीं करता। Poisoning चुपचाप होती है: model एक बार कोई झूठा या गढ़ा हुआ तथ्य कहता है, और हर आगे का turn चुपचाप उसे स्थापित सच मानता है।

</details>

2. ▢ पाठ 4 से: Tool का JSON schema क्या validate करता है?

<details markdown="1"><summary>जाँचें</summary>

Schema argument की संरचना और type validate करता है: कि ज़रूरी fields मौजूद हैं, कि मान घोषित type (string, number, boolean) से मेल खाते हैं, कि सूचियों में सही element type है, और कि enum या minLength जैसी बंदिशें पूरी होती हैं। वह यह validate नहीं करता कि मान सच है या किसी असली चीज़ की ओर इशारा करता है।

</details>

## यह जानें

### Cascading विफलताएँ: एक error दूसरे तक ले जाता है

Cascading विफलता तब है जब एक tool error ग़लत अगला फ़ैसला करवाता है, जो दूसरी error तक ले जाता है, और task से दूर घूमता जाता है। हर विफलता उलझन को सुलझाने की जगह बढ़ाती है।

यह चरण-दर-चरण उदाहरण है:

Turn 2: Agent configuration file खोजने के लिए search_files(directory="/config") call करता है। Directory मौजूद नहीं है। Tool error लौटाता है: "directory not found"।

Harness यह error transcript में जोड़ता है। अब तक ठीक है।

Turn 3: Model error पढ़कर तय करता है: "मानक home directory मौजूद नहीं है। मैं किसी अलग environment में होऊँगा। मैं /etc/config आज़माता हूँ।" यह अधूरी जानकारी पर आधारित समझदार reasoning है। Model search_files(directory="/etc/config") call करता है।

Turn 4: Search सफल होती है, पर ऐसे नतीजे लौटाती है जो agent की तलाश से मेल नहीं खाते। Model, जो turn 3 से /etc/config path पर टिक चुका है, तय करता है: "ये नतीजे लगभग ठीक हैं। मैं पहले वाले को इस्तेमाल करूँगा।" Model के पास अब ग़लत file है।

Turn 5: Agent ग़लत file पढ़ता है। सामग्री उसकी अपेक्षा से मेल नहीं खाती। बेमेल को पहचानने की जगह, model तय करता है: "File का format बदल गया होगा। मैं इसे ज़्यादा उदार तरीक़े से parse करूँगा।" Agent चलता रहता है, अब भी ग़लत नींव पर आगे बनाते हुए।

Turn 6 से N तक: हर फ़ैसला मूल error को और बढ़ाता है। Agent अब झूठे आधार से तर्क कर रहा है और काफ़ी पीछे लौटे बिना सँभल नहीं सकता।

Cascading विफलताएँ क्यों होती हैं: जब tool error लौटाता है, तो model को अंदाज़ा लगाना पड़ता है कि क्यों। क्या directory ग़ायब है? क्या permission की error है? क्या path की syntax ग़लत है? Model अंदाज़ा लगाकर आगे बढ़ता है। अगर अंदाज़ा ग़लत है, तो अगली tool call उसी ग़लत धारणा पर बनती है। और वहाँ से श्रृंखला नीचे चली जाती है।

पाठ 6 का error-count guard आख़िर में loop रोकेगा, पर cascade के बढ़ जाने के बाद रोकेगा, जड़ पर नहीं।

### Hallucinated arguments: सही type वाले पर झूठे

Hallucinated argument तब है जब model tool argument के लिए सुनने में ठीक लगने वाला पर तथ्य में ग़लत मान गढ़ता है। मान सही बना हुआ है और schema validation पार कर लेता है, पर वह किसी असली चीज़ से मेल नहीं खाता।

यह missing-required-field error (पाठ 3-5) से अलग है। छूटा हुआ field साफ़ schema-validation error बनाता है जिसे model देख सकता है और जिस पर प्रतिक्रिया दे सकता है। Hallucinated argument चुपचाप validation पार कर लेता है।

उदाहरण:

- Model को username से user खोजना है। वह get_user(username="alice_smith") call करता है, पर असली username "asmith" है। Schema string स्वीकार करता है; call आगे फेल होती है क्योंकि username मौजूद नहीं है।
- Model को API endpoint call करना है और path गढ़ देता है: call_api(endpoint="/api/v2/users/search")। Endpoint मौजूद नहीं है, पर वह ठीक-सा लगता है। Schema उसे string के रूप में validate कर देता है; HTTP call 404 के साथ फेल होती है।
- Model से नाम से function call करने को कहा जाता है और वह नाम गढ़ देता है: call_function(name="validate_order")। Function मौजूद नहीं है, पर string ठीक बनी है। Call सिर्फ़ runtime पर "function not found" के साथ फेल होती है।

यह schema validation error से बदतर क्यों है: जब schema कुछ ठुकराता है (छूटा field, ग़लत type), तो model को तुरंत प्रतिक्रिया मिलती है और वह उसे ठीक कर सकता है। जब argument सही type का है पर झूठा, तो error आगे जाकर होती है, अक्सर गूढ़ रूप में ("user not found", "404 not found", "function not found")। Model तुरंत नहीं समझता कि उसका गढ़ा मान ही समस्या थी; वह इसके बजाय service को दोष दे सकता है ("user database टूटा है") या माहौल को ("API चल नहीं रही") और उस ग़लत निदान के आधार पर ग़लत फ़ैसला ले सकता है।

अगर पिछले खंड का cascading विफलता का सिलसिला hallucinated argument से शुरू होता है, तो cascade और बुरा है: model ऐसे मान पर तर्क की श्रृंखला बना रहा है जो उसने गढ़ा और जिसे वह नहीं जानता कि उसने गढ़ा।

### उपाय: Validation और Echo

मुख्य उपाय है hallucinated arguments को जल्दी और साफ़ तौर पर फेल कराना, और model को दिखाना कि असल में क्या हुआ।

**जाने हुए सेट के विरुद्ध validate करें**: अगर tool ऐसा argument लेता है जो किसी असली चीज़ की ओर इशारा करे (username, function का नाम, endpoint), तो tool को validate करना चाहिए कि वह मौजूद है। आगे चुपचाप फेल होने की जगह, tool साफ़ error लौटाता है: "user alice_smith not found; valid users are: alice_s, alice_brown, alicia_m"। इससे model को तुरंत प्रतिक्रिया और चुनने के लिए विकल्पों का सेट मिलता है।

**सुलझाया गया मान दोहराएँ**: Tool call सफल होने के बाद, सिर्फ़ "success" न लौटाएँ। वह लौटाएँ जिस पर असल में कार्रवाई हुई। उदाहरण:

इसकी जगह:

```text
Tool result: Success
```

यह लौटाएँ:

```text
Tool result: Successfully updated order 12345. Order status is now CONFIRMED.
```

इस तरह, अगर model का argument गढ़ा हुआ था पर संयोग से किसी अनचाही चीज़ से मेल खा गया, तो echo बेमेल को दिखा देता है। Model देखता है "मैंने order ID 12345 के साथ call किया, और tool ने order 12345 अपडेट करने की रिपोर्ट दी", और नोट कर सकता है कि वे मेल खाते हैं या नहीं।

**ऊँचे दाँव वाले operations के लिए स्पष्ट पुष्टि माँगें**: अगर tool call data बदलेगी या कोई action लेगी, तो harness चलाने से पहले model से असली मान की पुष्टि करवाए। Model देखता है "आप user username_alice_smith को अपडेट करने वाले हैं; पुष्टि करें?" और उस बिंदु पर hallucination पकड़ सकता है।

### Trajectory में Cascading विफलताएँ

जब आप trajectory पढ़ें और cascade देखें:

1. पहली error पहचानें (turn N): tool अप्रत्याशित नतीजा या error लौटाता है।
2. Turn N+1 जाँचें: model ने error के होने के कारण के बारे में क्या धारणा बनाई?
3. आगे जाँचें: क्या model का अगला फ़ैसला उस धारणा से निकलता है?
4. अगर धारणा ग़लत थी, तो cascade शुरू हो चुका है।

निदान का सबक़: turn N की error वह समस्या नहीं है जिसे आपको दोबारा prompt करके ठीक करना चाहिए। समस्या है turn N+1 में model का error का ग़लत निदान। Tool को ज़्यादा साफ़ बनाएँ कि क्या ग़लत हुआ, या model को उस तरह की error सँभालने के बेहतर विकल्प दें, या stopping conditions कसें ताकि cascade बढ़े नहीं।

## अभ्यास

1. ▢ एक agent CSV file से data import कर रहा है। Turn तीन में वह parse_csv(filename="data.csv") call करता है। Tool error लौटाता है: "file not found"। Turn चार में model कहता है "File compressed होगी। मैं पहले उसे decompress करूँगा" और decompress(filename="data.csv.gz") call करता है। यह tool भी "file not found" के साथ फेल होता है। Turn पाँच में model error की अलग व्याख्या आज़माता है: "शायद file किसी subdirectory में है" और search_for_file(pattern="data*") call करता है। यह सफल होता है और "data_backup.csv" पाता है। Turn छह में वह backup file parse करता है, जिसमें अपेक्षा से अलग columns हैं, और parsing सफल होती है पर बेकार output बनाती है। क्या यह cascading विफलता है, और यह कहाँ से शुरू हुई?

<details markdown="1"><summary>जाँचें</summary>

हाँ, यह cascading विफलता है। यह turn 3 में शुरू हुई जब शुरुआती parse_csv फेल हुआ। Model ने error का ग़लत निदान किया: उसने मान लिया कि file compressed या हटाई गई है, जबकि असली समस्या शायद बस filename या path थी। हर turn में model ने अलग धारणा बनाई, और हर धारणा अलग action तक ले गई, जिनमें से किसी ने भी मूल समस्या ठीक नहीं की। Turn 6 तक agent ग़लत file के साथ काम कर रहा है (data.csv की जगह data_backup.csv), और बेकार output उसका नतीजा है। हल model में बेहतर reasoning नहीं है; वह शुरुआती error संदेश को ज़्यादा साफ़ बनाना है। Tool को लौटाना चाहिए "file data.csv not found in current directory; files found: data_backup.csv, old_data.csv"। उस जानकारी के साथ, model turn 4 में backup file को साफ़ तौर पर चुन सकता था, turns 4 और 5 के ग़लत निदान से गुज़रने की जगह।

</details>

2. ▢ एक agent customer records अपडेट कर रहा है। Turn दो में model update_customer(customer_id=987654, status="inactive") call करता है। Schema integer और string स्वीकार करता है। Tool लौटाता है "customer not found"। Turn तीन में model, उलझा हुआ, list_customers() call करता है। यह सभी customers की सूची लौटाता है। Turn चार में model सूची से पहला customer चुनता है और update_customer(customer_id=100001, status="inactive") call करता है। यह सफल होता है। पर agent को customer 987654 अपडेट करना था, 100001 नहीं। Turn दो का hallucinated argument ऐसी साफ़ error क्यों नहीं बना सका जिस पर model प्रतिक्रिया दे पाता?

<details markdown="1"><summary>संकेत</summary>

Schema validation error और सही type पर अमान्य मान दिए जाने पर tool के runtime व्यवहार के अंतर के बारे में सोचें।

</details>

<details markdown="1"><summary>जाँचें</summary>

Schema ने argument नहीं ठुकराया क्योंकि 987654 वैध integer है। Tool ने उसे स्वीकार किया और खोजा, और सिर्फ़ runtime पर "customer not found" के साथ फेल हुआ। Error संदेश साफ़ था ("customer not found"), पर model ने उसे ग़लत समझा: "customer 987654 मौजूद नहीं है, मुझे सही ID खोजनी होगी" निष्कर्ष निकालने की जगह, उसने निष्कर्ष निकाला "मेरे query करने के तरीक़े में कुछ ग़लत है, मैं दूसरा तरीक़ा आज़माता हूँ"। बेहतर tool design लौटाता: "customer 987654 not found; customers exist in the range 100001 to 150000"। इससे बेमेल साफ़ हो जाता और model को काम करने के लिए ठोस दायरा मिलता, cascade रुक जाता।

</details>

3. ▢ आप ऐसा tool बना रहे हैं जो file path को argument के रूप में लेता है। Schema कहता है path string होना चाहिए। आप उम्मीद करते हैं कि models कभी-कभी ऐसे paths गढ़ेंगे जो मौजूद नहीं। इनमें से कौन-सा design चुनाव hallucinated arguments को cascading विफलताएँ बनाने से सबसे अच्छी तरह रोकेगा?

    - a) कोई भी string path स्वीकार करें और path मौजूद न होने पर सामान्य "file error" के साथ फेल करें
    - b) Path को अनुमत directories की सूची के विरुद्ध validate करें; अनुमत सूची के बाहर के paths को साफ़ error के साथ ठुकराएँ
    - c) कोई भी path स्वीकार करें और file मौजूद न होने पर भी success संदेश लौटाएँ, ताकि model सोचे कि operation सफल रहा
    - d) Model से दो arguments देने को कहें: path और boolean जो पुष्टि करे कि path सही है

<details markdown="1"><summary>जाँचें</summary>

**b)** अनुमत directories की सूची के विरुद्ध validate करें और अमान्य paths को साफ़ error के साथ ठुकराएँ। इससे गढ़े हुए paths जल्दी और साफ़ तौर पर फेल होते हैं, model को तुरंत प्रतिक्रिया मिलती है। Model फिर अनुमत सूची में से चुन सकता है। **a)** फिर भी cascade को बढ़ने देता है क्योंकि error सामान्य है और model को समझने में मदद नहीं करता कि क्या ग़लत हुआ। **c)** ख़तरनाक है; वह समस्या को छिपाता है और cascades तक ले जाता है क्योंकि model सोचता है कि वह सफल हुआ जबकि नहीं हुआ। **d)** को harness का अतिरिक्त तर्क चाहिए और वह समस्या नहीं सुलझाता; model path भी गढ़ सकता है और उसकी पुष्टि भी कर सकता है।

</details>

4. ▢ एक agent को API से data लाना है। Turn दो में वह fetch_api(endpoint="/api/v1/customers/123") call करता है। Endpoint मौजूद नहीं है, और tool 404 error लौटाता है। Turn तीन में model कहता है "API server बंद होगा" और check_service_health() call करता है। यह लौटाता है "service is up and responding"। Turn चार में model कहता है "API बदल गई होगी। मैं version number के बिना आज़माता हूँ" और fetch_api(endpoint="/api/customers/123") call करता है। यह भी 404 के साथ फेल होता है। पहले tool में कौन-सा design बदलाव cascade रोक देता?

<details markdown="1"><summary>जाँचें</summary>

पहली tool call को सिर्फ़ "404 not found" से ज़्यादा जानकारी लौटानी चाहिए थी। वह लौटा सकता है: "endpoint /api/v1/customers/123 not found (404); valid endpoints include: /api/v2/customers/{id}, /api/v2/orders/{id}"। इस जानकारी के साथ, model तुरंत समझ जाता कि version number ग़लत था, service नहीं, और वह cascade के turns 3 और 4 की जगह turn 3 में endpoint सुधार सकता था। Cascade इसलिए हुआ कि error संदेश ने असली समस्या नहीं समझाई।

</details>

## असली दुनिया का अभ्यास

- [ ] ऐसी agent trajectory खोजें जो विफलता दिखाती है। उसे पढ़ें और पहचानें: क्या फ़ैसलों की cascading श्रृंखला है, जहाँ हर फ़ैसला उलझन बढ़ाता है? अगर हाँ, तो cascade किस turn पर शुरू हुआ? साफ़ error संदेश ने क्या किया होता?

- [ ] Tool डिज़ाइन करें (कोई भी tool चुनें जिसके साथ आप काम करते हैं या जिसे डिज़ाइन किया है)। लिखें कि आम विफलता के मामले में tool अभी कौन-सा error संदेश लौटाता है। अब उसे ऐसे दोबारा लिखें कि उसमें शामिल हो: क्या ग़लत था, क्या अपेक्षित था, और वैध विकल्प क्या हैं। यह साफ़ error संदेश model की समस्या का निदान करने की क्षमता कैसे बदलेगा?

- [ ] कल: छोटा test harness बनाएँ जो tool को hallucinated argument (ऐसा मान जिसे tool नहीं पहचानता) के साथ call करे। Tool का लौटाया error संदेश देखें। फिर tool को जाने हुए सेट के विरुद्ध validate करने और साफ़ error लौटाने के लिए बदलें। वही hallucinated argument फिर चलाएँ और दोनों error संदेशों की तुलना करें। एक अनुच्छेद लिखें कि साफ़ error विफलता के बारे में agent का निदान कैसे बदलती।

## आगे बढ़ने के लिए

- [लेख: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
