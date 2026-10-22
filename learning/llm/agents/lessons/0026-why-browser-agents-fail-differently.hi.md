---
title: "26. Browser Agents अलग तरह से क्यों फेल होते हैं"
description: Screen चलाने वाले agents ऐसे तरीक़ों से फेल होते हैं जिनसे tool-calling agents नहीं होते, और WebArena ने इन विफलताओं को मापने और पढ़ने के लिए benchmark क्यों बनाया
type: lesson
---

# पाठ 26. Browser Agents अलग तरह से क्यों फेल होते हैं

**मिशन से संबंध:** Screen चलाने वाले agents को बनाने और जाँचने के लिए समझना ज़रूरी है कि उनके failure modes संरचनात्मक हैं, सिर्फ़ बेहतर prompting की बात नहीं, ताकि आप prompt से छेड़छाड़ की जगह उपाय की रणनीतियों में निवेश करें।
**मुख्य स्रोत:** [पेपर: "WebArena: A Realistic Web Environment for Building Autonomous Agents", Zhou et al., 2023](https://arxiv.org/abs/2307.13854)
**पूर्व-आवश्यकताएँ:** [पाठ 25](0025-grounding-an-action-to-a-coordinate.md)

## वार्म-अप

1. ▢ पाठ 24 से: Computer-use agent को नामित tool calls की जगह pixels और screenshots के साथ क्यों काम करना पड़ता है?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि उसे किसी भी GUI application को चलाना है, उन्हें भी जो API या agent integration का ख़याल रखे बिना बने थे। Computer-use agent स्क्रीन के ज़रिए बातचीत करता है जैसे इंसान करता है, इसलिए वह हर जगह काम करता है।

</details>

2. ▢ पाठ 25 से: एक कारण बताएँ कि pixel coordinate tool-call argument से ज़्यादा नाज़ुक संदर्भ क्यों है।

<details markdown="1"><summary>जाँचें</summary>

Layout बदलने पर (window का आकार, page scroll, zoom का स्तर) coordinate टूट जाता है, पर user ID या record के नाम जैसा argument टिकता है। Coordinate जब ग़लत चीज़ पर पड़ता है तब चुपचाप भी टूट जाता है, जबकि tool call को साफ़ error मिलता है।

</details>

## यह जानें

### स्क्रीन चलाने वाले agents के अनोखे failure modes

Tool-calling agent तब फेल होता है जब वह ग़लत tool call करे, ग़लत arguments दे, या turns ख़त्म हो जाएँ। स्क्रीन चलाने वाला agent (browser-आधारित या computer-use) इन सभी तरीक़ों से फेल होता है और ऐसे तरीक़ों से भी जो tool-calling agents के साथ हो ही नहीं सकते।

**Grounding की ग़लतियाँ** (पाठ 25): Model का इरादा सही है पर coordinates ग़लत हैं, जिससे click ग़लत element या ख़ाली जगह पर पड़ता है। Tool-calling agent को यह समस्या नहीं होती क्योंकि वह चीज़ों को नाम से संदर्भित करता है।

**माहौल की रुकावटें**: Popup, cookie banner, loading spinner, modal dialog या error संदेश agent के अगले action को रोक सकता है। Tool-calling agent का इनसे शायद कभी सामना न हो क्योंकि API call बस साफ़ तौर पर सफल या फेल होती है। स्क्रीन चलाने वाले agent को असली task आगे बढ़ाने से पहले रुकावटों के आसपास रास्ता निकालना पड़ता है।

**सत्यापन की जटिलता**: जब tool call पूरी होती है, तो harness को status field वाला संरचित नतीजा मिलता है। Harness तुरंत जानता है कि वह सफल हुई या नहीं। जब computer-use agent button click करता है, तो तुरंत कुछ नहीं होता सिवाय इसके कि स्क्रीन बदलती है। Harness को नया screenshot लेना होता है, उसे model को भेजना होता है, और model से तर्क करवाना होता है कि button का click काम किया या नहीं। यह व्याख्या का चरण संरचित status code से धीमा और कम भरोसेमंद है।

**Layout की भिन्नता**: एक ही web application स्क्रीन के आकार, browser, zoom के स्तर, CSS framework और server की स्थिति के हिसाब से अलग दिखता है। जो agent सामान्य zoom पर desktop पर train या test हुआ वह मोबाइल फ़ोन पर या 150 प्रतिशत zoom पर फेल हो सकता है। Layout के बदलाव coordinates तोड़ देते हैं और दोबारा grounding माँगते हैं।

ये विफलताएँ बुरे model या अपर्याप्त prompting की वजह से नहीं हैं। ये APIs की जगह pixels के ज़रिए देखने और कार्रवाई करने के संरचनात्मक नतीजे हैं।

### WebArena क्यों मायने रखता है

सालों तक computer-use agents का मूल्यांकन क़िस्सों पर होता रहा: कोई vendor agent के कुछ प्रभावशाली करने का वीडियो दिखाता था, पर यह मापने का कोई व्यवस्थित तरीक़ा नहीं था कि agents सचमुच बेहतर हो रहे हैं या नहीं, या सबसे बड़ी विश्वसनीयता की समस्याएँ कहाँ हैं। अलग vendors अलग environments इस्तेमाल करते थे, इसलिए नतीजे तुलनीय नहीं थे। इससे असली प्रगति को marketing से अलग करना कठिन था।

WebArena पेपर (Zhou et al., 2023) ने मानकीकृत, self-hosted benchmark environment बनाया: निजी server पर खड़ी की गई websites और web applications का यथार्थवादी सेट, task के निर्देशों और सहीपन की जाँचों के साथ। Agent का काम है flight book करना, review पोस्ट करना या setting configure करना जैसे tasks पूरे करना। Task तभी सफल माना जाता है जब agent के actions सही, सत्यापन योग्य नतीजा दें (flight book हो गई, review पोस्ट हो गया)।

WebArena ने तीन चीज़ें संभव कीं:

पहला, उसने विश्वसनीयता का असली अंतर उजागर किया। जो स्क्रीन चलाने वाले agents marketing वीडियो में प्रभावशाली दिखते थे उनकी यथार्थवादी, कई-चरणों वाले web tasks पर सफलता दर 10-20 प्रतिशत के दायरे में थी। यह चेतावनी थी: तकनीक क़िस्सों के सुझाव से कहीं कम भरोसेमंद थी।

दूसरा, उसने शोधकर्ताओं को मापने दिया कि कौन-से failure modes हावी हैं। कई agent trajectories चलाकर और विफलताओं को वर्गीकृत करके, शोधकर्ताओं ने पाया कि grounding की ग़लतियाँ, माहौल की रुकावटें और layout के खिसकाव विफलताओं के बड़े हिस्से के लिए ज़िम्मेदार थे, तर्क की ग़लतियाँ या reasoning की कमी नहीं। इससे मेहनत उन उपायों की ओर गई जो सचमुच मदद करते हैं।

तीसरा, उसने साझा मानक दिया। अलग टीमें अपने agents को उसी benchmark पर चलाकर नतीजों की तुलना कर सकती थीं। प्रगति दावा नहीं, मापने लायक़ बन गई।

### उपाय और समझौते

कई रणनीतियाँ स्क्रीन चलाने वाले agent की विफलताएँ घटाती हैं, हर एक की क़ीमत के साथ:

**संरचना-जागरूक tools** (पाठ 25 में बताए): सिर्फ़ कच्चे screenshot की जगह, tool page के तत्वों (buttons, form fields, उनके नाम और स्थान) की संरचित जानकारी लौटाता है। Model तत्वों को coordinates की जगह नाम से संदर्भित करता है। Harness नाम को action के समय coordinates में बदलता है। इससे विश्वसनीयता लौटती है क्योंकि layout बदलने पर harness coordinates दोबारा निकाल सकता है, model से दोबारा अनुमान लगवाए बिना।

समझौता: आप "किसी भी GUI पर काम करता है" वाली व्यापकता खो देते हैं। संरचना-जागरूक tools semantic HTML वाले web pages के लिए काम करते हैं पर desktop applications, PDFs, games या उन interfaces के लिए फेल होते हैं जिनके लिए tool बना नहीं था।

**तत्व के साथ स्पष्ट बातचीत**: pixel coordinates भेजने की जगह, model "id submit_button वाले element पर click करो" या "email लेबल वाला field भरो" जैसा संदर्भ भेजता है। Harness element खोजने और उससे बातचीत करने के लिए browser APIs (JavaScript, accessibility trees, या DOM inspection) इस्तेमाल करता है।

समझौता: Harness फिर application-विशिष्ट हो जाता है। जिस platform की आपको परवाह है (web, desktop, mobile) उसके लिए tooling बनानी पड़ती है।

**रुकावट की पहचान और वापसी**: Agent समय-समय पर जाँचता है कि कोई popup या banner interface को रोक तो नहीं रहा, और आगे बढ़ने से पहले उसे बंद या हटाने के क़दम उठाता है।

समझौता: जटिलता और latency जोड़ता है; agent से ऐसी रुकावटें पहचानने की माँग करता है जिनके बारे में उसे साफ़ तौर पर बताया नहीं गया था।

**बहु-चरणीय सत्यापन**: हर action के बाद, agent screenshot लेता है और आगे बढ़ने से पहले यह जाँचने के लिए अतिरिक्त reasoning turn (मुख्य task के turns में नहीं गिना जाता) लेता है कि action इरादे के मुताबिक़ सफल हुआ।

समझौता: token इस्तेमाल और latency बढ़ाता है।

मुख्य अंतर्दृष्टि यह है कि कोई एक उपाय सारी विफलताएँ ठीक नहीं करता। हर एक एक-दो failure modes सँभालता है पर नई जटिलता लाता है या व्यापकता खोता है। Production system अक्सर कई को मिलाता है।

### यह निदान को कैसे ढालता है

जब स्क्रीन चलाने वाला agent फेल होता है, तो इन failure modes को जानना आपके निदान को ढालता है:

- अगर trajectory में clicks का ऐसा क्रम दिखे जो समझ में आता है पर ग़लत जगहों पर पड़ता है, तो grounding की ग़लतियों और layout की भिन्नता पर शक करें।
- अगर trajectory में agent ऐसा action लेता दिखे जो काम करना चाहिए था पर अगला screenshot कोई बदलाव नहीं दिखाता, तो रुकावटों (popups, loading spinners) की जाँच करें या सत्यापित करें कि action असल में चला या नहीं।
- अगर agent एक मशीन या zoom के स्तर पर चला पर अलग setup पर वैसे ही task पर फेल हुआ, तो माहौल-विशिष्ट rendering पर शक करें।
- अगर agent वही task 80 प्रतिशत बार सफलतापूर्वक पूरा करता है पर कभी-कभी एक जैसी परिस्थितियों में फेल होता है, तो timing की वजह से अस्थिरता पर शक करें (कोई गतिशील element अभी लोड नहीं हुआ) या ऐसे layout रूपांतर पर जो आपने नहीं देखा।

यह निदान का अनुशासन है: संभावित failure modes जानना आपको बिना सोचे prompts जोड़ने से रोकता है और असली समस्या की ओर इशारा करता है।

## अभ्यास

1. ▢ एक agent आपके desktop पर सामान्य zoom स्तर पर task सफलतापूर्वक पूरा करता है। जब आप वही agent ठीक उसी website पर browser zoom 125 प्रतिशत करके चलाते हैं, तो वह पहले click पर फेल हो जाता है। सबसे संभावित failure mode क्या है?

<details markdown="1"><summary>जाँचें</summary>

Grounding की ग़लती और layout की भिन्नता का मेल। सामान्य zoom पर coordinates सही थे। 125 प्रतिशत zoom पर वही element अलग coordinates पर दिखा। Agent ने नए zoom स्तर पर दृश्य रूप के आधार पर coordinates का अनुमान लगाया पर शायद ग़लत लगाया, या उसने पुराने zoom स्तर के cache किए screenshot के coordinates फिर इस्तेमाल किए। हल बेहतर reasoning नहीं है; वह या तो संरचना-जागरूक tooling है जो coordinates दोबारा निकालती है, या यह पक्का करना कि agent मौजूदा zoom स्तर पर नया screenshot ले।

</details>

2. ▢ एक agent की trajectory दिखाती है कि उसने turn तीन में button सफलतापूर्वक click किया। Turn चार के screenshot में button अब दिखता नहीं; modal dialog आ गया। Turn चार में agent उसी button को उन्हीं coordinates पर click करने की कोशिश करता है, और click modal पर पड़ता है। फिर agent शिकायत करता है कि उसे button नहीं मिल रहा। क्या यह विफलता grounding की ग़लती है?

<details markdown="1"><summary>संकेत</summary>

Turn चार में grounding असल में सही थी; coordinates अब भी वहीं इशारा कर रहे थे जहाँ button पहले था। समस्या coordinates ख़ुद नहीं हैं।

</details>

<details markdown="1"><summary>जाँचें</summary>

नहीं, यह रुकावट की समस्या है, grounding की ग़लती नहीं। Agent का तर्क ठोस था: उसने तय किया कि button अब भी click करने लायक़ होना चाहिए। Grounding सटीक थी: coordinates सही तरह button की पिछली जगह की ओर इशारा कर रहे थे। पर माहौल बदल गया (modal आ गया), और agent ने रुकावट को पहचाना या सँभाला नहीं। हल रुकावट की पहचान और वापसी है, बेहतर coordinate अनुमान नहीं।

</details>

3. ▢ आप तय कर रहे हैं कि अपने agent के लिए संरचना-जागरूक browser tool (जो element के नाम और स्थान लौटाता है) इस्तेमाल करें या कच्चा screenshot tool। आपका application कस्टम JavaScript dashboard है जिसमें गतिशील रूप से बने elements हैं, कोई semantic HTML संरचना नहीं है, और बातचीत के दौरान elements खिसकते हैं। Tool का दस्तावेज़ कहता है संरचना-जागरूक tools "semantic, मानक web applications" पर सबसे अच्छा काम करते हैं। आपको कौन-सा चुनना चाहिए?

    - a) संरचना-जागरूक tool, क्योंकि वह नया और ज़्यादा परिष्कृत है
    - b) कच्चा screenshot tool, क्योंकि आपका application semantic HTML नहीं है
    - c) फिर भी संरचना-जागरूक tool, और उसे कस्टम JavaScript से बढ़ाएँ
    - d) स्क्रीन चलाने वाले agents के लिए दोनों बराबर हैं

<details markdown="1"><summary>जाँचें</summary>

**b)** गैर-मानक, गतिशील, कस्टम application के लिए कच्चा screenshot tool बेहतर चुनाव है। संरचना-जागरूक tools semantic HTML और स्थिर IDs पर निर्भर करते हैं, जो आपके dashboard में शायद न हों। कच्चा screenshot model को गतिशील interface की दृश्य व्याख्या करने देता है। समझौता grounding की नाज़ुकता है, पर असमर्थित interface पर संरचना-जागरूक tooling इस्तेमाल करने की कोशिश शायद वैसे भी फेल होती। **a)** ग़लत है क्योंकि नया होने का मतलब आपके use case के लिए बेहतर होना नहीं। **c)** जटिलता जोड़ता है; अगर tool आपके interface का अच्छा समर्थन नहीं करता, तो कस्टम बढ़ोतरी मदद नहीं कर सकती। **d)** ग़लत है क्योंकि अलग तरह के applications के लिए tools के failure modes अलग हैं।

</details>

4. ▢ आप agent को WebArena के benchmark पर चलाते हैं और वह 15 प्रतिशत tasks में सफल होता है। आप system prompt को साफ़ instructions और reasoning संकेतों से बेहतर करते हैं। दोबारा परीक्षा में वह 16 प्रतिशत में सफल होता है। यह छोटा सुधार बाक़ी विफलताओं के संभावित कारण के बारे में क्या बताता है?

<details markdown="1"><summary>जाँचें</summary>

यह सुझाता है कि ज़्यादातर विफलताएँ reasoning या instructions की स्पष्टता की वजह से नहीं हैं। Prompting के सुधारों से बहुत कम फ़ायदा मिला। विफलताएँ शायद संरचनात्मक हैं: grounding की ग़लतियाँ, layout की भिन्नता, रुकावटें, सत्यापन की समस्याएँ, या दूसरे कारक जिन्हें अकेले बेहतर instructions ठीक नहीं कर सकते। और सुधारने के लिए आपको जाँचना होगा कि कौन-से failure modes असल में हावी हैं (trajectories पढ़कर) और फिर लक्षित उपाय लगाने होंगे जैसे संरचना-जागरूक tooling, रुकावट की पहचान, या बेहतर coordinate अनुमान।

</details>

## असली दुनिया का अभ्यास

- [ ] WebArena पेपर का सार और परिचय पढ़ें (arxiv.org/abs/2307.13854)। बताई गई तीन task श्रेणियाँ सूचीबद्ध करें और हर एक में वर्णित एक failure mode का उदाहरण नोट करें।

- [ ] किसी सार्वजनिक स्रोत (दस्तावेज़, blog, GitHub) से computer-use या browser agent की trajectory लें। हर विफलता (अगर कोई हो) को इनमें से वर्गीकृत करें: grounding की ग़लती, माहौल की रुकावट, सत्यापन की विफलता, layout की भिन्नता, या तर्क की ग़लती। कौन-सी श्रेणी सबसे ज़्यादा दिखती है?

- [ ] कल: ऐसा परीक्षण परिदृश्य डिज़ाइन करें जो ख़ास तौर पर grounding की ग़लतियाँ उजागर करे। परीक्षण के web page या interface में कौन-से गुण चाहिए? फिर अलग परिदृश्य डिज़ाइन करें जो रुकावट सँभालने की विफलताएँ उजागर करे। एक अनुच्छेद लिखें कि आप कैसे मापेंगे कि agent रुकावटें सही सँभालता है या नहीं।

## आगे बढ़ने के लिए

- [पेपर: "WebArena: A Realistic Web Environment for Building Autonomous Agents", Zhou et al., 2023](https://arxiv.org/abs/2307.13854)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
