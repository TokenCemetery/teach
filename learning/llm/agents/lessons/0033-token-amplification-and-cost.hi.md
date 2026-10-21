---
title: "33. Token Amplification और Cost per Completed Task"
description: Agentic systems एक अकेले prompt से कहीं ज़्यादा tokens प्रति पूरे हुए task पर क्यों खाते हैं, और उसका budget कैसे बनाएँ
type: lesson
---

# पाठ 33. Token Amplification और Cost per Completed Task

**मिशन से संबंध:** Agentic loop की token cost और latency का budget बनाएँ, और बताएँ कि amplification loop के किस हिस्से से आता है।
**मुख्य स्रोत:** [लेख: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
**पूर्व-आवश्यकताएँ:** [पाठ 32](0032-least-privilege-and-the-confused-deputy.md), [Trajectory](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 10 में आपने सीखा कि agent loop के चलने वाले हर turn में transcript बढ़ता है। यह ऐसी cost क्यों बनाता है जो trajectory भर में जुड़ती जाती है?

<details markdown="1"><summary>जाँचें</summary>

पूरा transcript हर loop turn पर model को भेजा जाता है। 30 turns की trajectory का मतलब है कि पहले turn की सामग्री model को 30 बार भेजी जाती है, दूसरे turn की 29 बार, और आगे भी। लंबी trajectory की token cost सिर्फ़ turns का योग नहीं है; वह पुराने turns के बार-बार भेजे जाने का योग है।

</details>

2. ▢ पाठ 19 से याद करें: जब orchestrator तीन workers parallel में चलाता है, तो उसी समस्या को हल करने वाले अकेले agent की तुलना में कुल कितने agent loops चलते हैं?

<details markdown="1"><summary>जाँचें</summary>

तीन अलग agent loops चलते हैं, हर worker के भीतर एक, साथ में orchestrator का अपना loop। इसलिए कुल कम से कम तीन पूरे agent runs और orchestrator की cost है, जबकि उसी समस्या को हल करने वाला अकेला agent एक run है। Token cost parallelism से बँटती नहीं, गुणित होती है।

</details>

## यह जानें

### Token amplification के चार स्रोत

Agentic system एक सुविज्ञ अकेले prompt से कहीं ज़्यादा tokens प्रति पूरे हुए task खाता है। यह चार जुड़ते कारकों की वजह से होता है। उनमें से तीन का नाम हम पहले के पाठों में ले चुके हैं; यह पाठ उन्हें एक साथ लाता है और चौथा जोड़ता है।

### स्रोत 1: Transcript का दोबारा बढ़ना (पाठ 10 से)

हर loop turn transcript में कुछ जोड़ता है। अगले turn में पूरा transcript model को फिर भेजा जाता है। इसका मतलब है कि 50 turns की trajectory turn 1 की token cost पचास बार चुकाती है, turn 2 की उनचास बार, और आगे भी। कुल योग का लगभग आधा बनता है: 1 + 2 + 3 + ... + 50 = 1,275, इसलिए हर turn का औसतन 25.5 बार भुगतान होता है। एक बार भेजा गया सादा prompt X tokens का है। वही समस्या 50 turns वाले agent से हल हो तो उसकी cost 50X नहीं (अगर हर turn स्वतंत्र होता), बल्कि कच्चे token प्रसारण में 1,275X के आसपास है, भले ही हर अलग turn X से सस्ता हो क्योंकि model संकरे दायरे पर केंद्रित है।

Anthropic का "Building Effective Agents" लेख बताता है कि यह दोबारा बढ़ना लंबे चलने वाले agents पर सबसे बड़ा cost का गुणक है, और इसीलिए पाठ 11 (compaction और retrieval) इसके विरुद्ध बचाव के रूप में मौजूद है।

### स्रोत 2: Multi-agent का दोहराव (पाठ 19 से)

अगर आप समस्या को उप-कार्यों में तोड़कर तीन workers parallel में चलाते हैं (पाठ 18 का fan-out), तो आप transcript के दोबारा बढ़ने की पूरी cost एक बार नहीं, तीन बार चुकाते हैं। हर worker की अपनी 50-turn trajectory है, इसलिए हर एक 1,275X चुकाता है। Orchestrator भी अपना loop चलाता है। Coordination की cost कुल token cost को गुणित करती है। अगर आपके अकेले agent की cost 50,000 tokens होती, तो हर एक थोड़ी कम cost वाले तीन workers का योग 130,000 tokens या उससे ज़्यादा हो सकता है।

### स्रोत 3: Reflection और retries (पाठ 17 से)

अगर task का पहला प्रयास फेल होता है और harness reflection बनाकर agent को फिर चलाता है, तो अब आपके पास एक की जगह दो पूरी trajectories हैं। जिस task में तीन प्रयास लगते हैं (एक विफलता, एक reflection, एक सफलता) उसकी cost लगभग उतनी होती है जितनी एक सफल अकेले प्रयास की तीन गुना, क्योंकि हर प्रयास अपने transcript के दोबारा बढ़ने के साथ पूरा agent run है। पाठ 17 सिखाता है कि reflection इस cost के लायक़ तभी है जब विफलता का संकेत साफ़ हो और दूसरे प्रयास के सफल होने की संभावना हो।

### स्रोत 4: हर turn पर दोबारा भेजी जाने वाली tool definitions (इस पाठ में नया)

System prompt और tool definitions उस context का हिस्सा हैं जो model को हर loop turn पर भेजा जाता है। Tool definitions आमतौर पर बड़ी होती हैं: हर tool का नाम, इंसान के पढ़ने लायक़ विवरण (पाठ 8 के नाम रखने के काम से), parameter types, बंदिशें और उदाहरण होते हैं। अगर आपके पास दस tools हैं जिनमें हर एक का 200 tokens का विवरण है, तो वह 2,000 tokens की tool definitions हैं। 50 turns की trajectory पर, यह 2,000 * 50 = 100,000 tokens उसी tool definitions को फिर भेजने में ख़र्च हुए, भले ही वे run के बीच कभी बदलीं नहीं।

यह cost transcript के दोबारा बढ़ने (स्रोत 1) से अलग है क्योंकि tool definitions बदलती नहीं हैं; वे स्थिर, दोहराया जाने वाला prefix हैं। यही वह समस्या है जिसे पाठ 34 (prompt caching) संबोधित करता है।

### Budget बनाने की सही इकाई: cost per completed task

ज़्यादातर cost की चर्चाएँ "cost per API call" या "cost per model invocation" पर केंद्रित होती हैं। पर agentic system के लिए सही इकाई "cost per completed task" है, जिसका मतलब है task पूरा होने तक सारे प्रयासों, सारी retries, सारे workers, सारे turns का पूरा योग।

जिस task को एक अकेला prompt 5,000 tokens में हल कर सकता है, वह agentic system में 50,000 या ज़्यादा tokens का हो सकता है अगर:

- समस्या हल करने में 20 turns लगें (दोबारा बढ़ने का गुणक: एकल-turn cost के ऊपर ~200 गुना)
- पहला प्रयास फेल हो और reflection-आधारित retry सफल हो (2 से गुणा करें)
- Task तीन parallel workers में टूटा हो (3 से गुणा करें)
- Tool definitions बड़ी हों और हर turn दोबारा भेजी जाएँ (10,000 tokens की बर्बादी जोड़ें)

गणित मोटा है, पर सिद्धांत असली है: 5,000 के आधार tokens व्यवहार में 50,000 से 150,000 tokens बन सकते हैं, क्योंकि आप एक call का भुगतान नहीं कर रहे; आप एक task पूरा होने का भुगतान कर रहे हैं, जिसमें कई calls, कई लौटाव और कई दोहराए context शामिल हैं।

### "Cost per completed task" आपके design के फ़ैसले क्यों बदलता है

जब आप cost per API call के हिसाब से सोचते हैं, तो लंबे चलने वाला agent calls की भारी संख्या की वजह से महँगा दिखता है। जब आप cost per completed task के हिसाब से सोचते हैं, तो सवाल बदल जाता है: क्या multi-agent system समस्या को wall-clock समय में तेज़ी से या ज़्यादा भरोसे से हल करता है, इस तरह कि token का गुणक जायज़ ठहरे? क्या reflection असफल tasks की संख्या घटाता है, इस तरह कि retry की cost जायज़ ठहरे? क्या decomposition समस्या को इतना सरल बनाता है कि हर worker प्रति task अकेले agent से कम tokens इस्तेमाल करे?

ये असली समझौते वाले सवाल हैं। Cost-per-task का budget समझौते को दिखने वाला बनाता है।

### उदाहरण: code की विफलता को debug करना

मान लें आपका task फेल होते test को debug करना है। सुविज्ञ इंसान prompt लिख सकता है: "यह test है, यह error output है। Bug खोजो।" वह prompt और response कुल 10,000 tokens का हो सकता है।

अब मान लें आप इसके बजाय agent loop बनाते हैं:

- Agent test पढ़ता है (1,000 tokens), code पढ़ता है (2,000 tokens), error पर तर्क करता है (500 tokens) = turn 1 पर 3,500 tokens। उन 3,500 tokens को tool definitions (2,000 tokens) के साथ turn 2 पर फिर भेजना = 5,500 tokens। 10 turns debug करने के बाद, आपने लगभग 3,500 \* 10 + (tool definitions \* 10) = 55,000 tokens ख़र्च किए, क्योंकि हर turn test, code और tool definitions को फिर भेजता है।
- Agent का पहला प्रयास ग़लत मूल कारण का अंदाज़ा लगाता है। Harness reflection बनाता है और agent को फिर चलाता है। अब आपके पास दो पूरे 10-turn runs हैं, इसलिए लगभग 110,000 tokens, 55,000 नहीं।
- दूसरा प्रयास सफल होता है।

Cost per completed task: 110,000 tokens। Cost per successful API call: 5,500 tokens (सिर्फ़ आख़िरी सफल call)। ये संख्याएँ अलग कहानियाँ कहती हैं। Cost per completed task के हिसाब से budget बनाना ज़्यादा ईमानदार है।

हल agents से बचना नहीं है; हल है पाठ 34 की prompt caching इस्तेमाल करके tool definitions को फिर भेजने से बचना, पाठ 16 की planning को turns की संख्या घटाने के लिए डिज़ाइन करना, और पाठ 17 की reflection सिर्फ़ तब इस्तेमाल करना जब विफलता के संकेत साफ़ हों।

## अभ्यास

1. ▢ Model को एकल-turn prompt की cost 5,000 tokens है और वह समस्या पूरी तरह हल करता है। उसी समस्या पर agent loop में 25 turns लगते हैं, और transcript के दोबारा बढ़ने की cost का मतलब है कि शुरुआती turns का हर token औसतन लगभग 20 बार चुकाया जाता है। Agent loop की कुल cost लगभग कितने tokens है?

<details markdown="1"><summary>जाँचें</summary>

लगभग 5,000 * 20 = 100,000 tokens। दोबारा बढ़ने का गुणक सबसे बड़ा कारक है। (यह उदाहरण के लिए अनुमान है; सटीक संख्या इस पर निर्भर है कि tokens turns में कैसे बँटे हैं, पर परिमाण का क्रम सही है।)

</details>

2. ▢ आप ऐसा agent बना रहे हैं जो शोध पेपरों का सारांश बनाता है। Agent के लिए tool definitions कुल 3,000 tokens की हैं। एक run में, agent 10 पेपर जाँचता है और 10 सारांश बनाता है, कुल 40 turns लेते हुए। Run के दौरान tool definitions कभी नहीं बदलतीं। Tool definitions को फिर भेजने में कितने tokens ख़र्च हुए, और पाठ 34 में यह बर्बादी सुधारने लायक़ क्यों है?

<details markdown="1"><summary>संकेत</summary>

गिनें कि tool definitions model को कितनी बार भेजी जाती हैं। फिर सोचें कि context का कौन-सा हिस्सा स्थिर है और run के बीच कभी नहीं बदलता।

</details>

<details markdown="1"><summary>जाँचें</summary>

Tool definitions 40 बार भेजी जाती हैं (हर turn पर एक बार), इसलिए 3,000 * 40 = 120,000 tokens ठीक उन्हीं definitions को फिर भेजने में ख़र्च हुए। यह बर्बादी है क्योंकि definitions कभी बदलती नहीं; वे स्थिर prefix हैं। पाठ 34 prompt caching सिखाता है, जो ठीक इसी तरह के स्थिर prefix को cache करती है और उसका भुगतान सिर्फ़ एक बार लेती है, 40 बार नहीं।

</details>

3. ▢ किसी task में तीन प्रयास लगते हैं। पहला प्रयास फेल होता है, reflection बनता है, दूसरा प्रयास फेल होता है, एक और reflection बनता है, और तीसरा प्रयास सफल होता है। हर प्रयास पूरा 15-turn का agent run है। तीनों प्रयासों का तालमेल बिठाने वाला orchestrator 5 turns लेता है। Trajectory में कुल लगभग कितने turns हैं?

    - a) 15 turns (सिर्फ़ सफल प्रयास गिना जाता है)
    - b) 35 turns (15 + 15 + 5)
    - c) 50 turns (15 + 15 + 15 + 5)
    - d) 150 turns (तीनों प्रयास गुणा orchestrator का अतिरिक्त बोझ)

<details markdown="1"><summary>जाँचें</summary>

**c)** तीनों प्रयास पूरे चलते हैं, इसलिए 15 + 15 + 15 = 45 turns, साथ में orchestration के 5 turns = 50 turns। विकल्प a ग़लत है क्योंकि विफलताएँ भी पूरे turns खाती हैं। विकल्प b दूसरे असफल प्रयास को चूक जाता है। विकल्प d जोड़ने की जगह गुणा करके ग़लत गिनता है। Trajectory में हर प्रयास का हर turn शामिल है, सिर्फ़ सफल वाला नहीं।

</details>

4. ▢ आप शोध task के लिए अकेला agent इस्तेमाल करें या तीन workers का fan-out, यह तय कर रहे हैं। अकेले agent को 60 turns लगेंगे और लगभग 100,000 tokens की cost आएगी। हर worker को 25 turns लगेंगे और लगभग 35,000 tokens की cost आएगी, साथ में orchestrator 10 turns लेता है और उसकी cost 3,000 tokens है। Multi-agent system की कुल token cost क्या है, और क्या वह अकेले agent से सस्ती है?

<details markdown="1"><summary>जाँचें</summary>

कुल: (35,000 * 3) + 3,000 = 108,000 tokens। Multi-agent system असल में tokens में थोड़ा महँगा है (108,000 बनाम 100,000) भले ही हर worker ज़्यादा कुशल है। यह पाठ 19 की coordination cost है। Multi-agent system wall-clock समय में जीतता है (तीनों workers parallel में चलते हैं, इसलिए समय सबसे धीमा worker तय करता है, योग नहीं), tokens में नहीं। यह दिखाता है कि cost-per-task का budget क्यों ज़रूरी है: अगर आपको गति चाहिए, तो multi-agent जीतता है; अगर tokens चाहिए, तो अकेला agent जीतता है।

</details>

## असली दुनिया का अभ्यास

- [ ] कोई task लें जो आपने agent से किया है (या कोई trajectory जो आपने देखी है)। उस agent के एक loop iteration को खंगालें और tokens गिनें: transcript का आकार, tool definitions का आकार, model के output का आकार। Turns की संख्या से गुणा करें। अब अनुमान लगाएँ कि model को एक सुविज्ञ अकेला prompt कितने का पड़ता, और दोनों संख्याओं की तुलना करें। गुणक दर्ज करें।
- [ ] छोटा agent task डिज़ाइन करें (कुछ जो आप ख़ुद चला सकें)। अनुमान लगाकर cost per completed task निकालें: कितने turns चाहिए, कितनी retries, कोई fan-out workers। सूत्र (transcript_regrowth_factor) \* (number_of_attempts) \* (number_of_workers) \* (tokens_per_turn) से पूरा budget जोड़ें।
- [ ] कल: Agent run की trajectory खोजें या बनाएँ (कम से कम 10 turns)। सारे turns और सारे प्रयासों में सारी token costs जोड़कर tokens में cost-per-task निकालें। फिर cost per successful API call निकालें (सिर्फ़ आख़िरी सफल turn)। लिखें कि cost-per-task cost-per-successful-call से कितनी बड़ी है, और समझाएँ कि यह अंतर budget बनाने के लिए क्यों मायने रखता है।

## आगे बढ़ने के लिए

- [लेख: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
