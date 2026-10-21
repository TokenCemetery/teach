---
title: "25. Action को Coordinate से जोड़ना (Grounding)"
description: दृश्य इरादे को pixel coordinate में बदलना typed tool-call argument से कठिन और नाज़ुक क्यों है
type: lesson
---

# पाठ 25. Action को Coordinate से जोड़ना (Grounding)

**मिशन से संबंध:** असफल computer-use agent को जाँचने के लिए grounding की ग़लतियों (coordinate का चूकना) को tool के दुरुपयोग या तर्क की ग़लतियों से अलग पहचानना ज़रूरी है, ताकि आप सही समस्या ठीक करें।
**मुख्य स्रोत:** [दस्तावेज़: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
**पूर्व-आवश्यकताएँ:** [पाठ 24](0024-screenshots-as-observations.md)

## वार्म-अप

1. ▢ Tool-calling agent में, जब model को किसी user को अपडेट करना होता है, तो वह harness को क्या भेजता है, और harness कैसे जानता है कि कौन-सा ख़ास user अपडेट करना है?

<details markdown="1"><summary>जाँचें</summary>

Model `user_id: "u_123"` जैसे argument वाली tool call भेजता है, जो स्थिर, अनोखा पहचानकर्ता है। Harness यह पहचानकर्ता पढ़ता है और बिना किसी संदिग्धता के ID से user अपडेट करता है।

</details>

2. ▢ Computer-use agent में, जब model को screenshot में दिखने वाला button click करना होता है, तो वह harness को क्या भेजता है, और harness कैसे जानता है कि कौन-सा button click करना है?

<details markdown="1"><summary>जाँचें</summary>

Model `click(x=450, y=200)` जैसे pixel coordinate पर click करने का action भेजता है। Harness coordinate पढ़ता है और स्क्रीन पर ठीक उसी जगह click करता है।

</details>

## यह जानें

### Grounding की समस्या

Grounding model के इरादे को असली screen coordinate में बदलने का चरण है। जब tool-calling agent को record अपडेट करना होता है, तो वह record को स्थिर ID, नाम, या ऐसे अनोखे पहचानकर्ता से बताता है जिस पर harness सीधे कार्रवाई कर सके। कोई संदिग्धता नहीं: harness को record मिलता है या नहीं मिलता।

जब computer-use agent को button click करना होता है, तो उसे मौजूदा screenshot में उस button को दृश्य रूप से खोजना होता है, उसके pixel coordinates का अनुमान लगाना होता है, और `(x, y)` जैसा coordinate tuple भेजना होता है। यह चार तरह से ज़्यादा कठिन है।

**पहला, कोई स्थिर संदर्भ नहीं है।** एक screenshot में pixel 450, 200 पर मौजूद button दूसरे screenshot में दूसरा button है (या कोई button ही नहीं) अगर window का आकार बदले, page scroll हो, या सामग्री खिसके। ID layout बदलने पर भी टिकती है; coordinate नहीं टिकता। Tool-calling agent button को नाम से माँगता, computer-use agent button को जगह से माँगता है, जो नाज़ुक है।

**दूसरा, model मदद नहीं माँग सकता।** Tool-calling agent में, अगर harness किसी argument को नहीं समझता, तो वह साफ़ error लौटाता है: "user_id u_999 not found" या "invalid format for date_field"। Model error पढ़कर अपना argument सुधार लेता है। Computer-use agent में, ग़लत coordinate पर click बस ग़लत चीज़ (या ख़ाली जगह) से टकराता है। Model को कोई error संदेश नहीं मिलता। उसे अगले screenshot पर ही पता चलता है कि click ग़लत जगह पड़ा, और तब भी, उसे दृश्य जाँच से अनुमान लगाना पड़ता है कि click चूक गया।

**तीसरा, feedback loop धीमा है।** Tool-calling agent की ग़लती के बाद उसे typed error संदेश मिलता है। Computer-use agent की ग़लती के बाद उसे एक और पूरा screenshot लेना होता है, उसे model को भेजना होता है, model के नई image की व्याख्या करने और सोचने तक इंतज़ार करना होता है कि क्या ग़लत हुआ, और फिर कोशिश करनी होती है। हर grounding की ग़लती को खोजने और सुधारने में model का पूरा round-trip लगता है।

**चौथा, छोटे माहौल के बदलाव चलते हुए क्रमों को तोड़ देते हैं।** User को ID से नाम देने वाली tool call तब भी काम करती है जब user का नाम, email या विभाग बदल जाए। Coordinates पर click तब टूट जाता है जब button कुछ pixels भी खिसके। 13-inch laptop screen, 27-inch monitor, browser zoom, font rendering और CSS breakpoints, सब एक ही button को अलग coordinates पर ले जा सकते हैं। जो trajectory एक मशीन पर बिल्कुल ठीक चली वह दूसरी पर चुपचाप फेल हो सकती है।

### Grounding नाज़ुक क्यों है

कल्पना करें कि agent सामान्य zoom वाले desktop browser पर search box को (300, 150) पर सफलतापूर्वक click करता है। वही web page मोबाइल फ़ोन पर देखें या browser zoom 125 प्रतिशत पर रखें, तो search box (225, 112) या (375, 188) पर दिख सकता है। Coordinate अब सही नहीं है। Click किसी चीज़ पर न पड़े, या बिल्कुल अलग element पर पड़े।

Agent का तर्क ठोस था। Model ने समझदारी का फ़ैसला किया। Action का प्रकार (click) सही था। पर coordinate ग़लत था, क्योंकि माहौल बदल गया। `search` नाम का tool माँगने वाले tool-calling agent को यह समस्या नहीं होती, क्योंकि tool का नाम स्थिर है।

इसीलिए grounding की ग़लतियाँ स्क्रीन चलाने वाले agents की अनोखी विफलता श्रेणी हैं। वे tool-calling agents में नहीं होतीं, क्योंकि tool-calling agents चीज़ों को जगह से नहीं, नाम से संदर्भित करते हैं।

### आंशिक उपाय: संरचना-जागरूक tools

कुछ browser या computer-use tools बीच का रास्ता देकर grounding की नाज़ुकता घटाने की कोशिश करते हैं: सिर्फ़ screenshot की जगह, tool page के तत्वों की संरचित जानकारी भी लौटाता है: हर button, link और form field के नाम, भूमिकाएँ, स्थान और bounding boxes।

फिर model कह सकता है "'Submit' लेबल वाला button click करो" या "email वाली पंक्ति का text field click करो", और harness उस नामित संदर्भ को click के समय coordinate में बदलता है, model से pixels से coordinates का अनुमान लगाने को कहने की जगह। इससे कुछ स्थिरता लौटती है: अगर button खिसके, तो harness नए coordinates अपने आप निकाल लेता है, model को दोबारा अनुमान लगाने की ज़रूरत नहीं।

यह एक समझौता है। आप विश्वसनीयता पाते हैं और "किसी भी GUI पर काम करता है" वाली वह व्यापकता कुछ खोते हैं जो शुद्ध screenshot-आधारित action देता है। संरचना-जागरूक tool web pages के लिए अच्छा काम करता है, जहाँ HTML elements की अर्थपूर्ण भूमिकाएँ और स्थिर IDs होती हैं, पर वह desktop GUI applications, games या उन अस्पष्ट applications के लिए काम नहीं कर सकता जिनके लिए tool बना नहीं था। शुद्ध screenshot-आधारित actions की यह सीमा नहीं है, पर वे ज़्यादा नाज़ुक हैं।

### Trajectory में grounding की ग़लतियाँ कैसे पहचानें

जब आप computer-use agent की trajectory पढ़ें, तो इन patterns को देखें:

- Model का इरादा समझ में आता है (उसने कुछ खोजने, field भरने आदि का फ़ैसला किया), पर action ने अपेक्षित नतीजा नहीं दिया।
- लगातार कई clicks ग़लत जगह पड़ते हैं।
- वही action एक screenshot पर काम करता है पर अगले पर फेल होता है।
- Coordinates किसी दिखने वाले element से दूर हैं।

ये grounding की ग़लती के लक्षण हैं। Model सही तर्क कर रहा था कि क्या करना है, पर coordinates स्क्रीन से मेल नहीं खाए। यह तर्क की ग़लती (model ने ग़लत चीज़ करने का फ़ैसला किया) या tool की विफलता (tool crash हुआ) से अलग है।

## अभ्यास

1. ▢ एक agent form submit करने के लिए coordinates (500, 250) पर click करता है। Click से पहले का screenshot Submit button को लगभग (500, 250) पर केंद्रित दिखाता है। Action सफल होता है और form submit हो जाता है। अगले turn में, agent उसी Submit button को उन्हीं coordinates (500, 250) पर फिर click करने की कोशिश करता है, पर form अब ग़ायब है और loading संदेश दिख रहा है। दूसरा click किसी चीज़ पर नहीं पड़ता। क्या यह grounding की ग़लती है?

<details markdown="1"><summary>जाँचें</summary>

नहीं। पहला click सही grounded था। दूसरा click इसलिए चूका कि स्क्रीन बदल गई, इसलिए नहीं कि model ने coordinate का ग़लत अनुमान लगाया। Grounding की ग़लतियाँ तब होती हैं जब coordinate उस screenshot पर इच्छित लक्ष्य से मेल नहीं खाता जिसे model अभी देख रहा है। Page की सामग्री बदलने पर coordinate बासी हो गया, पर यह agent के निर्णय लेने में grounding की ग़लती नहीं है; यह सही व्यवहार है: agent ने ऐसी चीज़ पर click करने की कोशिश की जो अब वहाँ नहीं थी।

</details>

2. ▢ एक agent दो fields वाले login page का screenshot पढ़ता है: ऊपर username और उसके नीचे password। Agent password टाइप करने का फ़ैसला करता है, अनुमान लगाता है कि password field लगभग (350, 180) पर है, और action `type(x=350, y=180)` भेजता है। Harness (350, 180) पर click करता है, जो असल में username field है, और password username field में टाइप हो जाता है। फिर agent को नया screenshot दिखता है जिसमें username field अब password से भरा है। यह grounding की ग़लती है, तर्क की ग़लती है, या दोनों?

<details markdown="1"><summary>संकेत</summary>

दो सवाल अलग-अलग पूछें: (1) क्या model ने क्या करना है इस पर समझदारी का फ़ैसला किया? (2) क्या model ने coordinates सही पाए?

</details>

<details markdown="1"><summary>जाँचें</summary>

यह grounding की ग़लती है, तर्क की ग़लती नहीं। Model का फ़ैसला सही था: उसने password टाइप करने का फ़ैसला किया। पर model ने password field के coordinates का ग़लत अनुमान लगाया। Coordinate (350, 180) ग़लत था; password field असल में स्क्रीन पर नीचे था, शायद (350, 240) पर। Model सही लक्ष्य पर click करना चाहता था पर action को ग़लत ढंग से ground किया।

</details>

3. ▢ एक computer-use agent क्रम से दो अलग web applications से बातचीत करता है। पहले application पर वह (400, 300) पर field पर click करके form सफलतापूर्वक भरता है। दूसरे application पर वह स्क्रीन पर लगभग उसी जगह दिखने वाले text input field पर click करने की कोशिश करता है, जो भी (400, 300) पर है, पर दूसरे application में वह coordinate ख़ाली जगह है और click कहीं नहीं पड़ता। क्या दूसरा click grounding की ग़लती है?

    - a) हाँ, क्योंकि coordinate दूसरे application के screenshot पर इच्छित लक्ष्य से मेल नहीं खाता था
    - b) नहीं, क्योंकि model ने दोनों applications के लिए वही तर्क इस्तेमाल किया
    - c) नहीं, क्योंकि coordinate पहली बार सही काम किया था, इसलिए दूसरे application में UI की गड़बड़ होगी
    - d) नहीं, क्योंकि grounding की ग़लतियाँ तभी होती हैं जब model जानबूझकर ग़लत चीज़ पर click करने की कोशिश करे

<details markdown="1"><summary>जाँचें</summary>

**a)** Click ग़लत ground हुआ: coordinate दूसरे application के मौजूदा screenshot पर इच्छित लक्ष्य से मेल नहीं खाता था। यह तथ्य कि वही coordinate दूसरे application पर काम किया था, अप्रासंगिक है; grounding इस बारे में है कि model के सामने अभी जो स्क्रीन है उस पर इरादे और coordinate का मेल हुआ या नहीं। **b)** ग़लत है क्योंकि model का तर्क यह तय नहीं करता कि click grounded है या नहीं, सिर्फ़ यह कि coordinate इच्छित लक्ष्य पर पड़ता है या नहीं। **c)** ग़लत है क्योंकि coordinate का एक बार काम करना आपको नहीं बताता कि वह दूसरी स्क्रीन पर सही है या नहीं; model ने वह स्थिरता मान ली जो उसे नहीं माननी थी। **d)** ग़लत है क्योंकि grounding की ग़लतियाँ भूलें हैं, जानबूझकर के चुनाव नहीं।

</details>

4. ▢ आप ऐसी trajectory पढ़ रहे हैं जहाँ agent task पूरा करने में नाकाम रहा। Turn सात में agent ने (1200, 50) पर click किया, स्क्रीन के ऊपर दाएँ कोने में। वहाँ कुछ दिखने वाला नहीं है और click का कोई असर नहीं हुआ। फिर model ने कहा कि उसे वह button नहीं मिला जिसे वह ढूँढ रहा था। अगले turn में agent ने (150, 50) पर, ऊपर बाएँ कोने में, click किया और button मिल गया। Turn सात में क्या ग़लत हुआ, इस पर परिकल्पना बनाएँ।

<details markdown="1"><summary>जाँचें</summary>

Agent ने शायद button की स्थिति ग़लत समझी और click को बहुत ज़्यादा दाईं ओर ground किया। Button असल में स्क्रीन के बाईं ओर था, पर model ने अनुमान लगाया कि वह दाईं ओर है। यह grounding की क्लासिक ग़लती है: model का इरादा (button खोजना और click करना) सही था, पर coordinate ग़लत था। Agent ने अगले turn में ख़ुद को सुधारा, शायद screenshot को दोबारा पढ़कर या अपना अनुमान फिर सोचकर।

</details>

## असली दुनिया का अभ्यास

- [ ] सामान्य zoom पर web page का screenshot लें। कोई button चुनें और अपने अनुमान से उसके pixel coordinates लिखें। अब browser को 25 प्रतिशत zoom करें और नया screenshot लें। अपने browser के developer tools से (element inspect करके और उसका bounding box देखकर) zoom किए हुए screenshot पर उसी button के coordinates खोजें। नए coordinates लिखें। पहले screenshot पर आपका अनुमान असली coordinates से कितना दूर था? Zoom ने स्थिति कैसे बदली?

- [ ] Computer-use agent की trajectory देखें या पढ़ें (किसी blog, tool दस्तावेज़ या उदाहरण से)। लगातार तीन actions के लिए, मिलाएँ कि agent क्या करना चाहता था (context या prompt से) बनाम उसके भेजे coordinates और उसके बाद का screenshot। क्या grounding इरादे से मेल खाई? अगर नहीं, तो coordinates किस वजह से बदले?

- [ ] कल: सरल web form डिज़ाइन करें (मन में या code में) जो आपके हिसाब से computer-use agent के लिए सही ground करना कठिन होगा। Form के कौन-से गुण grounding को नाज़ुक बनाते हैं? फिर उसी form का दूसरा संस्करण डिज़ाइन करें जिसे ground करना आसान होगा, और समझाएँ कि आपने क्या बदला।

## आगे बढ़ने के लिए

- [दस्तावेज़: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
