---
title: "8. Reproducible Runs"
description: "एक ही eval अलग runs पर अलग संख्याएँ क्यों दे सकता है, और भरोसेमंद नतीजे को score के साथ क्या log करना चाहिए"
type: lesson
---

# पाठ 8. Reproducible Runs

**मिशन से संबंध:** यह चरण 4 का समापन है: harness (पाठ 7) आधा ही काम है। उससे निकली संख्या तभी भरोसेमंद है जब उसका run-दर-run variance समझा जाए और यह log हो कि उसे किसने पैदा किया, और यही बाद की किसी तुलना को कोई मायने देता है।
**मुख्य स्रोत:** [Repo: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
**पूर्व-आवश्यकताएँ:** [पाठ 7](0007-eval-frameworks-and-harness.md), [Data contamination](../GLOSSARY.md)

## वार्म-अप

1. ▢ हर eval harness के चार चरणों के नाम बताएँ।

<details markdown="1"><summary>जाँचें</summary>

Held-out eval सेट load करना, model के outputs generate करना, उन्हें चुनी हुई metric या judge से grade करना, और हर-example के scores को एक सारांश संख्या में aggregate करना।

</details>

2. ▢ टीम को lm-evaluation-harness के बजाय openai/evals की ओर कब जाना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

जब किसी मिशन-विशिष्ट क्षमता को परखना हो जिसे कोई मौजूदा मानकीकृत benchmark नहीं ढकता, क्योंकि openai/evals custom eval को code के रूप में परिभाषित करने के लिए बना है, जबकि lm-evaluation-harness पहले से मौजूद benchmark configs चलाने के लिए बना है।

</details>

## यह जानें

### एक ही eval दो अलग संख्याएँ क्यों दे सकता है

गैर-शून्य temperature पर sample किया गया model अलग runs पर अलग completions बनाता है, भले prompt एक ही हो, जिसका मतलब है कि eval के हर बार चलने पर अलग हर-example scores और अलग aggregate संख्या, बिना कुछ ग़लत हुए। अगर grading में भी LLM judge है (चरण 3), तो वह परखे जा रहे model के अपने variance के ऊपर sampling noise की दूसरी परत जोड़ देता है। इनमें से कुछ भी harness का bug नहीं है; यह harness का एक stochastic प्रक्रिया को ईमानदारी से बताना है, और इसका मतलब है कि एक अकेले run की संख्या किसी वितरण से लिया गया sample है, model के बारे में कोई तय तथ्य नहीं।

### Determinism का trade-off

Temperature को 0 पर रखना (greedy decoding) generation-पक्ष की यादृच्छिकता हटा देता है और runs को कहीं ज़्यादा दोहराने योग्य बनाता है, जो ऐसे eval के लिए आकर्षक है जिसकी grading सटीक reproducibility पर निर्भर है, जैसे exact match। क़ीमत: greedy decoding शायद वह न दर्शाए कि model deployment में असल में कैसे बर्ताव करता है, अगर deploy किया गया system गैर-शून्य temperature पर sample करता है। पूरी तरह greedy चलाया गया eval ऐसा मोड माप रहा हो सकता है जिसे असली system शायद ही कभी इस्तेमाल करता है। जहाँ deploy किया गया व्यवहार सचमुच sample करता है, वहाँ ज़्यादा ईमानदार तरीक़ा है deployment temperature पर हर example के कई samples चलाना (वही विचार जो पाठ 4 के pass@k ने code के लिए इस्तेमाल किया) और उनके बीच का फैलाव बताना, सिर्फ़ एक अकेले run का बिंदु-मान नहीं।

### Seed मदद करता है, पर एक जैसे नतीजों की गारंटी नहीं देता

Generation के लिए random seed तय करना एक ही setup के runs के बीच variance घटाता है, पर अलग hardware, अलग library versions या अलग batch composition पर bit-दर-bit एक जैसे नतीजों की गारंटी नहीं है, क्योंकि floating-point गणना इन सब पर पूरी तरह associative नहीं होती। Seed असली, उपयोगी नियंत्रण है, पर पूर्ण नहीं; "हमने seed तय किया था" को इस सबूत के रूप में लेना कि दो runs सीधे तुलनीय हैं, seed जो वादा कर सकता है उससे ज़्यादा का दावा करना है।

### बताई गई संख्या को बाद में बचाव-योग्य क्या बनाता है

कोई संख्या अकेली, यह बताए बिना कि वह कैसे बनी, बाद की किसी संख्या से, चाहे दोबारा run हो, अलग checkpoint हो या अलग eval चक्र, ईमानदारी से तुलना नहीं की जा सकती: उनके बीच का कोई भी फ़र्क़ असली बदलाव हो सकता है या महज़ pipeline का variance, और खाली score में कुछ नहीं जो बता सके कि कौन-सा। बचाव-योग्य नतीजा score के साथ यह log करता है कि उसे असल में किसने पैदा किया: इस्तेमाल हुआ random seed, generation temperature, model और framework versions, eval सेट का version, और जब कई samples चलाए गए हों, उनके बीच का फैलाव, सिर्फ़ उनका औसत नहीं। यही वह चीज़ है जो बाद की तुलना, या वह go/no-go फ़ैसला जिस ओर चरण 5 बढ़ता है, को चाहिए ताकि वह ईमानदारी से बता सके कि देखा गया फ़र्क़ model को दर्शाता है या noise को।

## अभ्यास

1. ▢ एक टीम एक ही model पर एक ही eval temperature 0.7 पर दो बार चलाती है और दो अलग aggregate scores पाती है। क्या यह इस बात का प्रमाण है कि harness टूटा है? क्यों या क्यों नहीं?

<details markdown="1"><summary>जाँचें</summary>

नहीं। गैर-शून्य temperature generation को stochastic बनाता है, इसलिए runs के बीच अलग completions, और इसलिए अलग हर-example scores, बिना कुछ ग़लत हुए भी अपेक्षित हैं। Harness एक stochastic प्रक्रिया को ईमानदारी से बता रहा है; एक अकेले run की संख्या sample है, कोई तय तथ्य नहीं।

</details>

2. ▢ Eval के लिए temperature 0 रखने से क्या मिलता है, और क्या देना पड़ता है, अगर deploy किया गया system असल में temperature 0.7 पर sample करता है?

<details markdown="1"><summary>जाँचें</summary>

इससे दोहराव मिलता है: greedy decoding generation-पक्ष की यादृच्छिकता हटा देता है, इसलिए runs कहीं ज़्यादा एकसार हो जाते हैं। क़ीमत यथार्थ की है: eval ऐसा decoding मोड (greedy) माप रहा है जिसे असली system शायद ही कभी इस्तेमाल करता है, इसलिए नतीजा शायद वह न दर्शाए कि model 0.7 पर deploy होने पर असल में कैसे बर्ताव करता है।

</details>

3. ▢ Random seed तय करना दो eval runs के एक जैसे नतीजे देने की गारंटी क्यों नहीं देता?

<details markdown="1"><summary>संकेत</summary>

सोचें कि दो runs के बीच seed के अलावा और क्या अलग हो सकता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

Seed किसी दिए setup के भीतर की यादृच्छिकता को नियंत्रित करता है, पर floating-point गणना अलग hardware, library versions या batch composition पर पूरी तरह associative नहीं होती, इसलिए वही seed होने पर भी वे अंतर अलग नतीजे दे सकते हैं। Seed असली नियंत्रण है, bit-दर-bit एक जैसे output की पूर्ण गारंटी नहीं।

</details>

4. ▢ Team A एक model के लिए 72.3 का eval score बताती है। एक महीने बाद, team B उसी model पर "वही eval" दोबारा चलाती है और 69.8 पाती है, जबकि team A के मूल run से कोई seed, temperature या version जानकारी log नहीं हुई थी। 2.5 अंक के फ़ासले से ईमानदारी से क्या निष्कर्ष निकाला जा सकता है?

<details markdown="1"><summary>जाँचें</summary>

अपने-आप में बहुत कम। यह जाने बिना कि team A ने कौन-सा temperature, seed, model और framework versions, और eval सेट version इस्तेमाल किया, यह बताने का कोई तरीक़ा नहीं कि फ़ासला असली बदलाव को दर्शाता है (अलग checkpoint, eval सेट का अलग version) या sampling से होने वाले सामान्य run-दर-run variance को। ईमानदार निष्कर्ष यह है कि तुलना तब तक सार्थक नहीं जब तक दोनों runs के बनने का ब्योरा ज्ञात और मिलाया न जाए, या दोहराए गए runs के बीच का variance सीधे न मापा जाए।

</details>

5. ▢ बताई गई eval संख्या को बचाव-योग्य क्या बनाता है, इसके बारे में कौन-सा दावा सही है?

    - a) एक अकेले run का score अपने-आप में काफ़ी है, जब तक harness बिना त्रुटि के चला
    - b) Score को उसके साथ बताना चाहिए जिसने उसे पैदा किया (seed, temperature, versions, eval सेट का version) और, जहाँ प्रासंगिक हो, कई runs में उसका फैलाव
    - c) Random seed तय करना किसी भी hardware या library version पर एक जैसे नतीजों की गारंटी देता है
    - d) Evals के लिए हमेशा greedy decoding इस्तेमाल होनी चाहिए, deploy किए गए system के असल sampling temperature की परवाह किए बिना

<details markdown="1"><summary>जाँचें</summary>

**b)** बनाने का ब्योरा log करना और, जहाँ sampling शामिल है, runs के बीच का फैलाव, वही है जो बाद की तुलना को असली बदलाव और noise में फ़र्क़ करने देता है। (a) ग़लत है: अकेली संख्या की बाद में किसी चीज़ से तुलना नहीं हो सकती, यह जाने बिना कि उसे किसने बनाया। (c) ग़लत है: seed अलग hardware या versions पर variance घटाता है, मिटाता नहीं। (d) ग़लत है: जब deploy किया गया system असल में sample करता है तब greedy decoding यथार्थ का सौदा करता है, जो असली क़ीमत है, मुफ़्त चुनाव नहीं।

</details>

## असली दुनिया का अभ्यास

- [ ] जो eval आप चलाते हैं, उसके लिए जाँचें कि क्या उसका harness अभी score के साथ seed, temperature और model/framework versions log करता है, और जो कुछ छूटा है उसे जोड़ें।
- [ ] अगर आपका eval गैर-शून्य temperature पर sample करता है, तो उसे कई बार चलाएँ (या हर example के कई samples), और सिर्फ़ एक संख्या नहीं बल्कि runs के बीच का फैलाव दर्ज करें।
- [ ] कल: आपकी या आपकी टीम की बताई कोई पुरानी eval रिपोर्ट खोजें, और जाँचें कि उसके साथ इतना log हुआ था या नहीं कि पता चल सके कि भविष्य का दोबारा run सीधे तुलनीय होता या नहीं।

## आगे बढ़ने के लिए

- [Repo: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
- [Repo: openai/evals, OpenAI](https://github.com/openai/evals)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
