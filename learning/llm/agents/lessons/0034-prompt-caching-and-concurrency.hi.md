---
title: "34. Prompt Caching और Concurrency"
description: Caching प्रति task token cost कैसे घटाती है और concurrency throughput कैसे बढ़ाती है, और दोनों को मिला देना budgeting की ग़लती क्यों है
type: lesson
---

# पाठ 34. Prompt Caching और Concurrency

**मिशन से संबंध:** Agentic loop की token cost और latency का budget बनाएँ, और बताएँ कि amplification loop के किस हिस्से से आता है।
**मुख्य स्रोत:** [दस्तावेज़: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
**पूर्व-आवश्यकताएँ:** [पाठ 33](0033-token-amplification-and-cost.md)

## वार्म-अप

1. ▢ पाठ 33 से आपने सीखा कि tool definitions हर loop turn पर model को फिर भेजी जाती हैं, भले ही वे कभी बदलती नहीं, और tokens खाती हैं। यह context का कौन-सा हिस्सा है, और caching मदद क्यों करेगी?

<details markdown="1"><summary>जाँचें</summary>

Tool definitions model को हर message का स्थिर prefix हैं: वे run के बीच नहीं बदलतीं। Caching मदद करती है क्योंकि cache उस स्थिर prefix को पहले request के बाद सहेजता है और उसी trajectory की बाद की requests में फिर इस्तेमाल करता है, उसमें जोड़ी गई नई सामग्री का ही शुल्क लेते हुए।

</details>

2. ▢ पाठ 19 से याद करें: क्या तीन agents को parallel में चलाने से, एक agent को क्रम से चलाने की तुलना में, समस्या हल करने की token cost घटती है?

<details markdown="1"><summary>जाँचें</summary>

नहीं। तीन agents को parallel में चलाने से कुल token cost बढ़ती है क्योंकि हर agent अपनी पूरी cost स्वतंत्र रूप से चुकाता है। Parallelism wall-clock समय घटाता है, token cost नहीं। हर parallel agent को फिर भी task पढ़ना, अपना loop चलाना और अपना transcript model को भेजना पड़ता है।

</details>

## यह जानें

### Prompt caching कैसे काम करती है

Prompt caching ऐसा mechanism है जो पहली call के बाद request का स्थिर prefix सहेजता है और बाद की calls पर उसे फिर इस्तेमाल करता है, उसका पूरा दाम दोबारा लिए बिना। Cache एक request क्रम के लिए ख़ास है; अलग उपयोगकर्ताओं या अलग agent runs की requests cache साझा नहीं करतीं।

यह mechanics है:

1. Trajectory के पहले message पर, आप पूरी request भेजते हैं: system prompt, tool definitions और task।
2. Model उसे सामान्य रूप से process करता है और पूरी token cost लेता है।
3. Response में metadata होता है: "Cached 4,000 tokens" (या जो भी स्थिर prefix था)।
4. उसी trajectory के दूसरे message पर, आप request में नई सामग्री जोड़ते हैं: शायद tool का नतीजा, अगला instruction, या अगला turn।
5. Model cached prefix (system prompt, tools, task) फिर इस्तेमाल करता है और सिर्फ़ नई जोड़ी गई सामग्री का शुल्क लेता है।
6. यह दोहराता है: उसी trajectory का हर नया turn सिर्फ़ उसका भुगतान करता है जो पिछले turn से बदला।

Cache की एक क़ीमत है: पहला turn पूरा दाम चुकाता है, और cache lookups और storage के लिए छोटा अतिरिक्त शुल्क है। पर लंबी trajectory पर, यह अतिरिक्त बोझ आसानी से जायज़ है। अगर आपके 30 turns हैं और tool definitions 2,000 tokens की हैं, तो cache लगभग 2,000 * 28 = 56,000 tokens बचाता है (turns 2 से 29 में definitions फिर नहीं भेजी जातीं, इसलिए आप उनकी cost 28 बार बचाते हैं)।

### क्या cache को अमान्य करता है

Cache तभी काम का है जब prefix सचमुच स्थिर हो। कई चीज़ें चुपचाप cache को अमान्य कर देती हैं, जो harness के design के लिए मायने रखता है:

**Tool definitions का क्रम बदलना।** अगर आप tool सूची को turn 1 पर अलग और turn 2 पर अलग क्रम में serialize करते हैं (जैसे turn 1 पर वर्णमाला क्रम में, turn 2 पर आवृत्ति के क्रम में), तो prefix अब मेल नहीं खाता और cache अमान्य है। Harness को tools हमेशा, हर turn पर, एक ही क्रम में serialize करने चाहिए।

**System prompt में गतिशील मान घुसाना।** अगर आपके system prompt में timestamp ("Current time: 2024-09-13"), user ID, या कोई प्रति-call मान है, तो वह मान turns के बीच बदलता है और prefix अब स्थिर नहीं रहता। हर एक turn पर cache अमान्य है। यह caching को पूरी तरह बेकार कर देता है। अगर आपको गतिशील मान चाहिए, तो उन्हें tools के बाद (request के non-cached हिस्से में) रखें।

**पहले के messages को संपादित करना।** अगर harness पुराने messages को जगह पर ही संपादित करता है (सिर्फ़ जोड़ने के उलट), तो उस संपादन बिंदु से आगे cache अमान्य हो जाता है। पाठ 7 ने सिखाया कि transcript agent की state है; वह दर्शन सिर्फ़ जोड़ने और पुराने messages को कभी न छूने की ओर इशारा करता है। Prompt caching इसे और पक्का करती है: कोई भी संपादन cache तोड़ देता है।

### Caching पाठ 33 की "हर turn पर दोबारा भेजी जाने वाली tool definitions" की cost सुलझाती है

मुख्य स्रोत "Prompt caching" के दस्तावेज़ बताते हैं कि tool definitions और system prompts ठीक वैसी स्थिर, बड़ी, दोहराई जाने वाली सामग्री हैं जिसके लिए caching बनी है। 2,000 tokens के tool विवरणों वाला 10-tool harness अब उन 2,000 tokens की cost प्रति trajectory सिर्फ़ एक बार चुकाता है, प्रति turn नहीं। 50 turns की trajectory पर, यह अकेले लगभग 98,000 tokens बचाता है (caching के बिना definitions 50 बार आती हैं, caching के साथ 1 बार, इसलिए 49 * 2,000 = 98,000 tokens बचे)।

इसीलिए पाठ 33 और पाठ 34 जोड़ीदार हैं: पाठ 33 बर्बादी पहचानता है, पाठ 34 हल का नाम बताता है।

### Concurrency: अलग, पूरक साधन

Prompt caching किसी भी अकेले agent run की cost घटाती है। Concurrency अलग सवाल है: कई agent instances को parallel में चलाना।

Concurrency कई रूप ले सकती है:

- एक ही task को एक ही input पर कई agents से parallel में चलाना, यह देखने के लिए कि वे अलग उत्तर देते हैं या नहीं (उन tasks के लिए काम का जहाँ कई वैध हल हैं)।
- Task के रूपांतर parallel में चलाना (पाठ 19 का fan-out), जहाँ हर agent उप-कार्य हल करता है।
- कई स्वतंत्र उपयोगकर्ता tasks parallel में चलाना (कई उपयोगकर्ताओं को सेवा देने वाला system, हर एक का अपना agent instance)।

हर मामले में, concurrency throughput बढ़ाती है: wall-clock समय की प्रति इकाई ज़्यादा tasks पूरे होते हैं। पर concurrency किसी भी एक task की token cost नहीं घटाती। अगर आप तीन agents parallel में चलाते हैं और हर एक की cost 100,000 tokens है, तो कुल 300,000 tokens है, 100,000 को 3 से भाग नहीं। Parallelism समय के बदले tokens चुकाती है।

### ग़लती: caching और concurrency को मिला देना

आम budgeting की ग़लती यह मान लेना है कि कई agents को parallel में चलाने से हर एक tokens में किसी तरह सस्ता हो जाता है। ऐसा नहीं होता। उलझन यह है:

- सही: Caching स्थिर prefixes को दोबारा भेजने से बचाकर अकेले agent की लंबी trajectory की token cost घटाती है।
- सही: Concurrency agents को parallel में चलाकर wall-clock समय घटाती है।
- ग़लत: "हम agents concurrently चलाते हैं, इसलिए प्रति agent token cost कम है।"

Concurrency समय घटाती है, tokens नहीं। Agents को तेज़ चलाना (parallel में) उन्हें सस्ता नहीं बनाता (tokens में)। अगर आपको cost घटानी है और आपके पास पहले से caching है, तो साधन ये हैं:

- Turns की संख्या घटाने के लिए बेहतर planning (पाठ 16)।
- Transcript का आकार घटाने के लिए बेहतर retrieval (पाठ 11)।
- Multi-agent दोहराव घटाने के लिए कम workers (पाठ 19)।
- बर्बाद प्रयास घटाने के लिए जल्दी फेल होना (पाठ 29 का निदान)।

### Token budget: दो सवाल

Agentic system डिज़ाइन करते समय, दो अलग सवाल पूछें:

1. **Cost per completed task:** एक agent को एक task भरोसे से हल करने के लिए कितने tokens चाहिए? यहीं caching मदद करती है, planning मदद करती है, और reflection की क़ीमत लगती है।
2. **Throughput:** आपको प्रति सेकंड या प्रति मिनट कितने tasks पूरे करने हैं? यहीं concurrency मदद करती है। अगर आपको प्रति सेकंड 10 tasks चाहिए और हर task क्रम से पूरा होने में 1 सेकंड लेता है, तो आपको कम से कम 10 agents parallel में चाहिए।

इन सवालों को मिलाने से ग़लत फ़ैसले होते हैं। अगर आप प्रति task cost घटाने की कोशिश कर रहे हैं, तो और concurrent agents जोड़ना मदद नहीं करता। अगर आप throughput बढ़ाना चाहते हैं और आपके पास समय-सीमा है, तो concurrency जोड़ना सही साधन है (पर आप कुल tokens में चुकाते हैं: 10 agents * प्रति task cost = कुल budget)।

## अभ्यास

1. ▢ आपके agent का system prompt और tool definitions कुल 5,000 tokens के हैं। Agent एक task पर 30 turns चलता है। Prompt caching के बिना वे 5,000 tokens model को कितनी बार भेजे जाते हैं? Caching के साथ कितनी बार?

<details markdown="1"><summary>जाँचें</summary>

Caching के बिना: 30 बार (हर turn पर एक बार), definitions के अतिरिक्त बोझ के कुल 150,000 tokens। Caching के साथ: पहले turn पर एक बार, फिर सारे बाद के turns पर फिर इस्तेमाल, यानी प्रभावी रूप से एक बार। (ज़्यादा सटीक रूप से, हर turn पर cache निकालने का छोटा अतिरिक्त बोझ है, पर पूरे 5,000 tokens फिर प्रसारित नहीं होते।) इस मामले में caching लगभग 145,000 tokens बचाती है।

</details>

2. ▢ आप अपने harness में prompt caching लागू कर रहे हैं। Tool सूची गतिशील रूप से बनती है: turn 1 पर agent के पास tools A, B, C हैं; turn 3 पर harness tool D जोड़ता है। Tools उसी क्रम में serialize होते हैं जिसमें बने (turn 1 पर A, B, C; turn 3 पर A, B, C, D)। क्या turn 1 का cache turn 3 पर अब भी वैध रहेगा? क्यों या क्यों नहीं?

<details markdown="1"><summary>संकेत</summary>

Turn 1 की request और turn 3 की request के बीच क्या बदला है? क्या वह बदलाव cached prefix का हिस्सा है, या उसके बाद का?

</details>

<details markdown="1"><summary>जाँचें</summary>

नहीं, cache अमान्य है। Turn 1 पर prefix में "tools: A, B, C" है। Turn 3 पर prefix में "tools: A, B, C, D" है। Prefixes मेल नहीं खाते, इसलिए cache लागू नहीं होता। Harness को पूरी definitions फिर भेजनी पड़ती हैं। इसीलिए गतिशील tool जोड़ना (agent के फ़ैसलों के आधार पर run के बीच tool जोड़ना) caching तोड़ता है। जो harness caching चाहता है उसे या तो शुरू में ही तय tool सेट पर टिकना चाहिए, या मान लेना चाहिए कि run के बीच tools जोड़ने से cache अमान्य होता है।

</details>

3. ▢ आप cached agent के लिए system prompt डिज़ाइन कर रहे हैं। Prompt में model को समय में टिकाने के लिए "Current date: 2024-09-13" शामिल है। यह caching की समस्या क्यों है?

    - a) तारीख़ model के लिए प्रासंगिक नहीं है और हटा देनी चाहिए।
    - b) तारीख़ हर दिन बदलती है, इसलिए cached prefix एक दिन बाद बासी हो जाएगा।
    - c) तारीख़ गतिशील मान है जो runs के बीच बदलता है, जो हर run पर cache को अमान्य कर देता है क्योंकि prefix अब मेल नहीं खाता।
    - d) तारीख़ें किसी भी system में cache नहीं हो सकतीं।

<details markdown="1"><summary>जाँचें</summary>

**c)** System prompt cached prefix का हिस्सा है। अगर आप कोई तय तारीख़ डालते हैं जो run 1 बनाम run 2 में अलग है, तो run 1 का cached prefix run 2 की request से मेल नहीं खाता, इसलिए cache बेकार है। हल है तारीख़ को cached prefix से बाहर रखना (उसे tools के बाद, प्रति-turn सामग्री में रखें), या अगर तारीख़ असल में ज़रूरी नहीं तो सभी runs के लिए तय तारीख़ इस्तेमाल करना। यह आम ग़लती है: cached हिस्से में प्रति-run metadata डालना caching को बेकार कर देता है।

</details>

4. ▢ आपके agent system को बढ़ाने के दो विकल्प हैं: विकल्प A है एक agent की cost per task को caching और planning से अनुकूलित करना, 100,000 tokens से घटाकर 60,000 tokens तक लाना। विकल्प B है दस agents को बिना अनुकूलन के parallel में चलाना, हर एक की cost अब भी 100,000 tokens। अगर आपको 10 tasks पूरे करने हैं और आपके पास असीमित compute है, तो कौन-सा विकल्प token cost न्यूनतम करता है?

<details markdown="1"><summary>जाँचें</summary>

विकल्प A: 10 tasks \* प्रति task 60,000 tokens = कुल 600,000 tokens। विकल्प B: 10 tasks \* प्रति task 100,000 tokens = कुल 1,000,000 tokens, भले ही वे parallel में चलें। Concurrency गति बढ़ाती है (विकल्प B एक task के समय में पूरा होता है, जबकि विकल्प A क्रम से उससे 10 गुना अवधि में पूरा होता है) पर cost नहीं। विकल्प A tokens में सस्ता है। अगर आपको 10 tasks जितनी जल्दी हो सके पूरे करने हैं, तो आप दोनों मिलाएँगे: हर agent को 60,000 tokens तक अनुकूलित करें (विकल्प A का तरीक़ा) और 10 अनुकूलित agents parallel में चलाएँ, कुल 600,000 tokens और सबसे कम wall-clock समय के लिए।

</details>

## असली दुनिया का अभ्यास

- [ ] अपना लिखा या समीक्षा किया हुआ agent harness देखें। ढूँढें कि system prompt और tool definitions कहाँ serialize होते हैं। पुष्टि करें कि वे हमेशा एक ही क्रम में serialize होते हैं, और उस खंड में कोई गतिशील मान (timestamps, user IDs, run-विशिष्ट metadata) नहीं घुसाया गया। अगर घुसाया गया है, तो नोट करें कि वह caching कैसे तोड़ता है।
- [ ] किसी जाने हुए task के लिए prompt caching से token बचत का अनुमान लगाएँ। अंदाज़ा लगाएँ: system prompt और tool definition का आकार, turns की संख्या, प्रति turn tokens। गणना करें कि definitions को दोबारा न भेजने से कितने tokens बचे। क्या बचत caching लागू करने की जटिलता के लायक़ है?
- [ ] कल: ऐसा task डिज़ाइन करें जिसे concurrency से फ़ायदा हो (कई उपयोगकर्ता, कई स्वतंत्र उप-कार्य, या एक ही task पर कई प्रयास)। अगर आप agents क्रम से (एक समय में एक) बनाम parallel में चलाएँ तो कुल token budget का अनुमान लगाएँ। दिखाएँ कि दोनों budgets बराबर हैं, और समझाएँ कि हर तरीक़े से आप क्या पाते और खोते हैं।

## आगे बढ़ने के लिए

- [दस्तावेज़: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
