---
title: "24. Observations के रूप में Screenshots"
description: Computer-use agents स्क्रीन को structured data की जगह image के रूप में कैसे देखते हैं, और loop की संरचना फिर भी क्यों टिकी रहती है
type: lesson
---

# पाठ 24. Observations के रूप में Screenshots

**मिशन से संबंध:** असफल computer-use agent को उसकी trajectory से जाँचने के लिए समझना होगा कि उसके observations दृश्य हैं, संरचित नहीं, इसलिए grounding की ग़लती किसी छूटे tool argument जैसी बिल्कुल नहीं दिखती।
**मुख्य स्रोत:** [दस्तावेज़: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
**पूर्व-आवश्यकताएँ:** [पाठ 23](0023-code-execution-as-a-tool.md), [Agent loop](../GLOSSARY.md)

## वार्म-अप

1. ▢ पहले के पाठों में, जब agent tool call करता है और नतीजा पाता है, तो वह नतीजा किस रूप में होता है? क्या वह हमेशा संरचित (JSON या schema) होता है, हमेशा असंरचित text, या दोनों में से कोई भी?

<details markdown="1"><summary>जाँचें</summary>

इस track के कवर किए हर wire format में संरचित। Tool का नतीजा हमेशा उस call के id से चिह्नित होता है जिसका वह जवाब है, और उसमें हमेशा या तो tool का output होता है या error, भले ही सटीक field के नाम और आकार provider और harness के हिसाब से बदलते हों (पाठ 3 देखें)। Model को tool के नतीजे की दृश्य व्याख्या कभी नहीं करनी पड़ती जैसी screenshot की करनी पड़ती है।

</details>

2. ▢ पाठ 6 से: Agent loop के चार मुख्य चरण क्रम से क्या हैं?

<details markdown="1"><summary>जाँचें</summary>

Model को call करें, response को transcript में जोड़ें, देखें कि काम पूरा हुआ या नहीं, नहीं तो tools चलाएँ और उनके नतीजे जोड़ें, फिर शुरू में लौट जाएँ।

</details>

## यह जानें

### Observation का प्रकार बदल जाता है

पहले के पाठों में, tool-calling agent का हर action के बाद का observation harness का बनाया संरचित नतीजा है: `tool_id`, `status` और `value` जैसे fields वाला JSON object। Computer-use agent का observation बिल्कुल अलग है। जब agent स्क्रीन पर action लेता है (click, type, scroll), तो observation screenshot है: सचमुच एक image, PNG या JPEG format में, जो स्क्रीन पर अभी जो भी दिख रहा है उसकी।

क्या हुआ यह समझने के लिए model को इस image की दृश्य व्याख्या करनी पड़ती है, किसी संरचित data field को पढ़ने की जगह। यह agent के दुनिया को समझने के तरीक़े में गहरा बदलाव है।

पाठ 6 के loop की कुल बनावट बिना बदले बची रहती है: transcript भेजो, response पाओ, action चलाओ, नतीजा जोड़ो, दोहराओ। पर अब "नतीजा जोड़ो" का मतलब transcript में image जोड़ना है, और "response पाओ" का मतलब है कि model वर्णन बना रहा है कि उसे उस image में क्या दिख रहा है और आगे क्या करना है यह तय कर रहा है।

### यह क्यों मायने रखता है: व्यापकता

इस design का कारण शक्ति है। पहले के पाठों में, tool-calling agent सिर्फ़ वही tools call कर सकता है जो developer ने उसके लिए साफ़ तौर पर बनाए। अगर आप चाहते हैं कि agent ऐसे application से बातचीत करे जिसकी कोई API नहीं, तो आपको ऐसा tool लिखना होगा जो उस application की API को लपेटे। पर अगर application की कोई API ही न हो? अगर वह सिर्फ़ GUI हो?

Computer-use agent इस समस्या को किनारे कर देता है। हर application के लिए API या कस्टम tool चाहिए होने की जगह, agent स्क्रीन के ज़रिए बातचीत करता है, जैसे कोई इंसान करता। Action space तय और सामान्य है: mouse हिलाओ, click करो, text टाइप करो, keys दबाओ, scroll करो, screenshot लो। ये वही actions किसी भी operating system के किसी भी GUI application में काम करते हैं, web browser से लेकर desktop application और cloud console तक। Model स्क्रीन की चीज़ें करना सीखता है, application-विशिष्ट चीज़ें नहीं।

यही फ़ायदा है: ऐसा agent जो सचमुच किसी भी interface को चला सकता है, उन्हें भी जो agent integration का ख़याल रखे बिना बने थे।

### Loop फिर भी टिका रहता है

क्योंकि loop की संरचना अवधारणा में observation के प्रकार से अलग है, बुनियादी चक्र बचा रहता है:

1. Transcript (जिसमें अब मौजूदा screenshot शामिल है) model को भेजें।
2. Model screenshot को देखता है, समझता है कि स्क्रीन पर क्या है, और तय करता है कि आगे क्या करना है।
3. Model action भेजता है: coordinates (x, y) पर click करना, string "hello" टाइप करना, नीचे scroll करना, या एक और screenshot लेना।
4. Harness action चलाता है।
5. अगर action screenshot थी, तो harness नई image transcript में जोड़ता है।
6. चरण 1 पर लौटें।

Model अब भी तय करता है कि कब रुकना है, harness अब भी सीमाएँ लागू करता है और loop को ख़त्म करता है, transcript अब भी हर turn के साथ बढ़ता है, और पाठ 6 की stopping conditions (और actions नहीं, max turns, error की सीमा) अब भी लागू होती हैं। बस इतना बदला कि observation का data type JSON object से image हो गया।

### दृश्य observation से आई चुनौतियाँ

यह व्यापकता क़ीमत के साथ आती है। संरचित tool result असंदिग्ध है: harness ने उसे बनाया, उसका तय schema है, और model fields को नाम से पढ़ सकता है। Screenshot संदिग्ध है: model को मौजूदा image में दृश्य रूप से ढूँढना पड़ता है कि वह जो चाहता है (button, text field, menu item) कहाँ है, उसकी जगह की व्याख्या करनी पड़ती है, और तय करना पड़ता है कि कौन-सा action लेना है।

पाठ 25 में आप इस संदिग्धता को grounding नाम की ख़ास समस्या में ठोस होते देखेंगे। अभी के लिए, जान लें कि यह समझौता मौजूद है: computer-use agents ऐसी चीज़ें कर सकते हैं जो tool-calling agents नहीं कर सकते, क्योंकि वे किसी भी GUI को चला सकते हैं, पर observation को दृश्य व्याख्या चाहिए, जो ऐसे नए failure modes लाती है जो संरचित observations में नहीं होते।

## अभ्यास

1. ▢ आप web application से बातचीत करने के लिए computer-use agent बना रहे हैं। आपका सहकर्मी `click_button` नाम का tool जोड़ने का सुझाव देता है जो button का नाम string argument के रूप में लेता है, ताकि agent coordinates से जूझने की जगह `click_button("Submit")` लिख सके। क्या यह अच्छा विचार है? क्यों या क्यों नहीं?

<details markdown="1"><summary>जाँचें</summary>

नहीं है। Computer-use agent का पूरा मक़सद ही यह है कि वह बिना कस्टम tooling के किसी भी GUI के साथ काम करे। अगर आप `click_button` जैसे task-विशिष्ट tools जोड़ते हैं, तो आप पारंपरिक tool-calling interface ऊपर से चढ़ा रहे हैं, जो मक़सद ही ख़त्म कर देता है। Model को सामान्य actions लेना (coordinates पर click, type) और screenshot की दृश्य व्याख्या करना सीखना चाहिए। Wrapper tools जोड़ना जुड़ाव बढ़ाता है और agent की व्यापकता घटाता है।

</details>

2. ▢ एक computer-use agent screenshot लेता है, login form देखता है, और username को username field की जगह password field में टाइप कर देता है। यह model में bug है, harness में, या action space में ही?

<details markdown="1"><summary>संकेत</summary>

Model ने username टाइप करने का फ़ैसला किया। Harness ने action चलाया। फ़ैसले को स्क्रीन के सही हिस्से से जोड़ने में कुछ गड़बड़ हुई।

</details>

<details markdown="1"><summary>जाँचें</summary>

यह दृश्य व्याख्या की ग़लती है: model ने form देखा पर ग़लत पहचाना कि कौन-सा field कौन-सा था। Action space (यह string टाइप करो) सही काम किया। Harness ने action सही चलाया। Screenshot की model की समझ ग़लत थी। इसे grounding की ग़लती कहते हैं और यही पाठ 25 का विषय है।

</details>

3. ▢ Files पढ़ने वाला tool-calling agent `read_file(path)` नाम का tool इस्तेमाल करता है और status field वाला नतीजा पाता है। Files को text editor में खोलकर पढ़ने वाला computer-use agent editor खोलने के बाद screenshot लेता है। Harness के लिए किस observation को सफल सत्यापित करना आसान है?

    - a) Tool-calling agent, क्योंकि status field स्पष्ट है
    - b) Computer-use agent, क्योंकि screenshot सब कुछ दिखाता है
    - c) दोनों बराबर आसान हैं, बस अलग format हैं
    - d) कोई नहीं, क्योंकि सफलता सत्यापित करने के लिए model को दोनों तरह नतीजे की व्याख्या करनी पड़ती है

<details markdown="1"><summary>जाँचें</summary>

**a)** Tool-calling agent के पास स्पष्ट status field है; harness बिना संदिग्धता के `if result.status == "success"` जाँच सकता है। Computer-use agent का screenshot file की सामग्री दिखाता है, पर harness को उस screenshot को model के पास ले जाकर उससे पुष्टि करवानी पड़ती है कि file सही खुली, जो धीमा और कम भरोसेमंद है। Observation का प्रकार प्रभावित करता है कि सत्यापन कितना आसान है।

</details>

4. ▢ आप computer-use agent की trajectory पढ़ रहे हैं जिसने form भरने की कोशिश की। Agent ने आठ actions लिए: fields पर click किया, text टाइप किया, और scroll किया। आख़िरी screenshot खाली fields वाला form दिखाता है। Agent क्यों फेल हुआ इसे जाँचने के लिए आपको सबसे पहले क्या देखना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

हर click action के coordinates को हर click के बाद लिए गए screenshots से मिलाकर देखें। क्या agent ने स्क्रीन के सही हिस्से पर click किया, या clicks ग़लत जगहों पर पड़े? भले ही model ने "username field पर click करने" का फ़ैसला किया, असली click का coordinate चूका हो सकता है। यही grounding की समस्या है: model का इरादा और स्क्रीन की असली जगह अलग-अलग हो गए।

</details>

## असली दुनिया का अभ्यास

- [ ] Browser में कोई web application खोलें। हाथ से screenshot लें। स्क्रीन के तीन तत्वों (button, text field, link) के pixel coordinates (x, y) का अनुमान लगाएँ। अब browser window का आकार बदलें या scroll करें, नया screenshot लें, और वही coordinates फिर अनुमानित करें। लिखें कि coordinates कितने बदले और क्या पहले screenshot का तय coordinate दूसरे पर अब भी काम करता।

- [ ] Computer-use agent की trajectory पढ़ें (किसी सार्वजनिक उदाहरण, tool दस्तावेज़ या अपने परीक्षण से)। Run के बीच से एक screenshot चुनें। बाद के screenshots या actions देखे बिना, तीन चीज़ें लिखें जो agent आगे कर सकता है। फिर देखें कि agent ने असल में कौन-सा action लिया। क्या आपके अनुमान मेल खाए?

- [ ] कल: computer-use agent की किसी विफलता का वर्णन खोजें (blog post, GitHub issue या पेपर के सार में)। स्पष्टीकरण पढ़ने से पहले अनुमान लगाएँ कि विफलता model के task को ग़लत समझने से हुई, tool-call syntax की ग़लती से, grounding की ग़लती (ग़लत coordinates) से, या किसी और कारण से। फिर स्पष्टीकरण पढ़कर जाँचें कि आपका अनुमान सही था या नहीं।

## आगे बढ़ने के लिए

- [दस्तावेज़: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
