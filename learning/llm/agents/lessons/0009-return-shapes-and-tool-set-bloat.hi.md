---
title: "9. Return Shapes और Tool-Set का फूलना"
description: Tool का return value context budget से क़ीमत वसूलता है, और बहुत ज़्यादा tools model की सही चुनने की क्षमता बिगाड़ते हैं
type: lesson
---

# पाठ 9. Return Shapes और Tool-Set का फूलना

**मिशन से संबंध:** Agent की tool सतह डिज़ाइन करने में यह चुनना शामिल है कि tool क्या लौटाता है (उसकी return shape) और कितने tools देने हैं, क्योंकि दोनों डिज़ाइन के ऐसे चुनाव हैं जो model की अपने विकल्पों में से सही चुनने की क्षमता और उसके बाद के हर turn की cost को प्रभावित करते हैं।
**मुख्य स्रोत:** [लेख: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
**पूर्व-आवश्यकताएँ:** [पाठ 8](0008-naming-and-describing-a-tool.md)

## वार्म-अप

1. ▢ पाठ 8 से: Tool के विवरण को model को यह क्यों बताना चाहिए कि उसे कब और कैसे इस्तेमाल करना है, बजाय सिर्फ़ यह गिनाने के कि वह कौन-से parameters लेता है?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि tools में से चुनने के लिए model के पास मार्गदर्शन का कोई और स्रोत नहीं है। सिर्फ़ parameter सूची बताती है कि tool को कैसे call करना है, पर यह नहीं कि उसे क्यों या कब उठाना है, जबकि model को असल में यही फ़ैसला लेना होता है।

</details>

2. ▢ पाठ 8 से: अगर एक ही tool set में बहुत मिलते-जुलते नामों और विवरणों वाले दो tools हों तो आप कौन-सी समस्या पैदा करते हैं?

<details markdown="1"><summary>जाँचें</summary>

Model उन्हें भरोसे से अलग नहीं कर सकता, इसलिए वह ग़लत वाला call कर सकता है या सुरक्षा के लिए दोनों call कर सकता है। यह शोर सेट के बाक़ी हर tool में से सही चुनने की model की क्षमता भी बिगाड़ता है, सिर्फ़ उन दो की नहीं जो मिलते-जुलते हैं।

</details>

## यह जानें

### Tool का return value context budget से क़ीमत वसूलता है

Transcript का हर message tokens खाता है। जब कोई tool नतीजा लौटाता है, तो वह नतीजा transcript में जुड़ता है, और model उसे हर अगले turn में देखता है, run ख़त्म होने या transcript के कटने तक। छोटा, केंद्रित उत्तर लौटाने वाला tool थोड़ी क़ीमत लेता है। पाँच हज़ार database rows लौटाने वाला tool run के बाक़ी हर turn पर असली tokens की क़ीमत लेता है, चाहे model को वे सब चाहिए थे या नहीं।

```text
Bad:
Tool: fetch_user_records
Returns: [complete User record, complete User record, ...]
# 5000 rows, 50KB of JSON, ~10,000 tokens consumed per turn after this call
```

Tool के लौटने के बाद transcript फूल जाता है। अब model को अगले turn पर अपना ही context पढ़ने के लिए सारी पाँच हज़ार rows process करनी पड़ती हैं। यह token budget को फुलाता है और loop को धीमा करता है।

### Return shapes को पूर्णता के लिए नहीं, फ़ैसले के लिए डिज़ाइन करें

अंदर के system के पास जो कुछ है वह सब लौटाने की जगह, ऐसी return shape बनाएँ जो model को वह दे जो अगला क़दम तय करने के लिए चाहिए।

```text
Better: Option 1 - Return a summary
Tool: fetch_user_records
Returns:
  total_count: 5000
  sample_results: [User, User, User, ...] # top 5 results
  query_was_too_broad: true
  suggestion: "Your query matches 5000 users. Narrow it with a company_id or email domain filter."

# ~500 tokens consumed per turn after this call
```

Model अब देख सकता है कि query बहुत व्यापक थी और जानता है कि आगे क्या करना है: वह tool को बेहतर filters के साथ फिर call कर सकता है। यह पूरे dump के दसवें हिस्से के बराबर tokens लौटाता है।

```text
Better: Option 2 - Let the model ask for more
Tool: fetch_user_records
Returns:
  count: 50  # number of results returned
  total_matching: 5000  # number of results if the query was not limited
  results: [User, User, ...] # just the first 50
  next_page_token: "abc123xyz"

# Model sees it got 50 of 5000. It can decide to refine the query or ask for the next page.
```

दोनों में model को सोच-समझकर फ़ैसला लेने के लिए काफ़ी जानकारी मिलती है, data के नीचे दबे बिना।

### Tool-Set का फूलना: ज़्यादा tools मतलब बदतर चुनाव

Agent में tool जोड़ना मुफ़्त नहीं है। Model जिन tools में से चुन सकता है, उनमें से हर एक model के लिए चुनाव कठिन बनाता है। इसे tool-set bloat कहते हैं।

तीन tools के साथ model ज़्यादातर बार सही चुनता है:

```text
Tools:
- search_documentation
- read_file
- list_directory
```

दस tools के साथ model ख़ुद पर शक करने लगता है, जब एक काफ़ी होता तब भी कई tools call करता है:

```text
Tools:
- search_documentation
- search_issues
- search_code
- read_file
- read_logs
- list_directory
- list_repos
- get_git_history
- get_git_diff
- get_git_status
```

हर नया tool फ़ैसले में शोर जोड़ता है। Model को एक चुनने से पहले दसों विवरण पढ़ने और तौलने पड़ते हैं। अगर दो मिलते-जुलते हों (search_code और search_documentation), तो model दोनों call कर सकता है। असर चुपचाप होता है: मौजूदा हर tool थोड़ा-थोड़ा बिगड़ता है, सिर्फ़ नया नहीं।

क़ीमत असली है: ज़्यादा tool calls, transcript में ज़्यादा tokens, फ़ालतू जानकारी पर बर्बाद ज़्यादा turns।

### नया Tool जोड़ना बनाम Parameter जोड़ना

जब आपका मन tool जोड़ने का हो, तो पहले पूछें: क्या यह मौजूदा tool पर parameter हो सकता है?

```text
Bad: Two tools
- name: list_files
- name: list_directories
```

बेहतर: parameter वाला एक tool

```text
Good: One tool with a parameter
- name: list_contents
  parameters:
    - name: path
    - name: type
      type: enum
      values: [files, directories, all]
```

Model अपना चाहा type चुनता है, और आपने tool set में शोर नहीं जोड़ा।

पर कभी-कभी नया tool जोड़ना सही होता है। अगर tools मूल रूप से अलग हैं (वे अलग स्थितियों में call होते हैं, अलग आकार लौटाते हैं, अलग permissions माँगते हैं), तो साफ़ नाम वाला नया tool ठूँसे हुए parameter से बेहतर है:

```text
Good: Two specialized tools
- name: search_database_by_id
  parameters:
    - id
    # Fast, returns a single record
- name: search_database_by_query
  parameters:
    - query
    # Might return many records
```

Model अंतर जानता है: by_id तेज़ और सटीक है, by_query लचीला है पर बहुत कुछ लौटा सकता है। नाम फ़ैसला साफ़ कर देते हैं।

नियम: नया tool तब जोड़ें जब tool मूल रूप से अलग कारणों से call किया जाएगा, या जब आप अंतर को parameters में व्यक्त न कर सकें। Parameter तब जोड़ें जब tool मूल रूप से वही ऑपरेशन हो और input या output के format में बस बदलाव हो।

### व्यवहार में Tool-Set का फूलना पहचानना

एक बारीक संकेत तब है जब model ऐसी बातें कहने लगे जैसे "मुझे पहले search call करना चाहिए कि वह मौजूद है या नहीं, फिर मौजूद हो तो fetch करूँ" जबकि एक tool पूरा काम कर सकता था। यह model का सुरक्षित रहने की कोशिश करना है क्योंकि उसे भरोसा नहीं कि हर tool क्या करता है। समस्या model की नहीं है; वह tool set की है।

दूसरा संकेत है बार-बार की tool calls: model एक ही run में वही tool कई बार call करता है, जैसे दो बार search या दो बार list। इसका अक्सर मतलब होता है कि tool set model को एक ही call में नतीजे सँकरे करने का तरीक़ा नहीं दे रहा, इसलिए उसे जो चाहिए वह पाने के लिए tool को अलग parameters के साथ call करना पड़ता है।

## अभ्यास

1. ▢ `get_user_history` नाम का tool पिछले महीने के 100,000 user action events का JSON array लौटाता है, हर एक विस्तृत। Model शायद इस tool को call करेगा, पहले दस events देखेगा, और बाक़ी को अनदेखा कर देगा। इस call के बाद के हर turn पर token cost घटाने के लिए कौन-सा design बदलाव काम करता है?

<details markdown="1"><summary>जाँचें</summary>

Return को पहले N events तक सीमित करें (जैसे पहले 20) और total_count जोड़ें, साथ में model के लिए और माँगने का तरीक़ा। इस तरह model को जो चाहिए वह दिख जाता है और सारे 100,000 events की क़ीमत नहीं चुकानी पड़ती। या फिर, पूरे ब्योरे की जगह सारांश लौटाएँ: "पिछले हफ़्ते 50 events, उससे पहले के हफ़्ते 50। सबसे हाल का: user ने login किया", और ज़रूरत पड़ने पर model को ख़ास ब्योरा माँगने दें।

</details>

2. ▢ आपके tool set में 15 tools हैं। Model एक ही run में search_by_name और search_by_id दोनों call कर रहा है, जबकि वह दोनों searches को एक अकेले tool के parameters के रूप में व्यक्त कर सकता था। उन्हें दो अलग tools रखने से क्या नुक़सान है?

<details markdown="1"><summary>संकेत</summary>

Model के काम के बारे में सोचें: उसे पंद्रह विवरण पढ़कर तय करना है कि कौन-सा tool call करे। मिलते-जुलते tools होने से वह काम कैसे कठिन होता है?

</details>

<details markdown="1"><summary>जाँचें</summary>

Tool-set bloat। Model को पंद्रह tools में से चुनना है। search_by_name और search_by_id जैसे मिलते-जुलते tools चुनाव कठिन बनाते हैं। Model एक काफ़ी होने पर दोनों call कर सकता है, या यह तय करने में समय गँवा सकता है कि कौन-सा उचित है। मौजूदा हर tool थोड़ा-सा बिगड़ता है क्योंकि सेट ज़्यादा शोरभरा हो गया। हल है उन्हें search field के लिए parameter वाले एक search tool में मिला देना।

</details>

3. ▢ इनमें से कौन-सा संकेत है कि tool की return shape बहुत ज़्यादा शब्दबहुल है?

    - a) Tool बहुत बार call होता है
    - b) Model नतीजा पढ़ता है और उसे इस्तेमाल करने से पहले सारांश माँगता है
    - c) Tool को चलने में लंबा समय लगता है
    - d) Tool को authentication चाहिए

<details markdown="1"><summary>जाँचें</summary>

**b)** Model नतीजा पढ़ता है और उसे इस्तेमाल करने से पहले सारांश माँगता है। इसका मतलब tool बहुत ज़्यादा जानकारी लौटा रहा है; फ़ैसला लेने से पहले model को जो मिला उसे छानना या संक्षिप्त करना पड़ता है। (a) return shape से जुड़ा नहीं है; बार-बार call होने वाला tool डिज़ाइन से संकरा हो सकता है। (c) execution की गति के बारे में है, tokens के बारे में नहीं। (d) permissions के बारे में है, return shape के बारे में नहीं।

</details>

4. ▢ आप code search agent के लिए tools डिज़ाइन कर रहे हैं। क्या `search_code` और `get_code_diff` एक tool होने चाहिए या दो? एक-दो वाक्यों में समझाएँ।

<details markdown="1"><summary>जाँचें</summary>

दो अलग tools। उन्हें अलग कारणों से call किया जाता है (search किसी pattern से मेल खाती files ढूँढता है, diff versions के बीच के बदलाव दिखाता है), वे अलग आकार लौटाते हैं (files की सूची बनाम संरचित diff), और वे अलग समस्याएँ सुलझाते हैं। एक ठूँसा हुआ tool model का चुनाव कठिन बनाता। अगर वे उसी ऑपरेशन के रूपांतर होते (जैसे अलग query parameters के साथ search_code), तो वे parameter वाला एक tool हो सकते थे।

</details>

## असली दुनिया का अभ्यास

- [ ] किसी LLM application या agent में, जिस तक आपकी पहुँच है, tool set खोजें। Tools गिनें। Model की trajectory पढ़ें और हर वह turn चिह्नित करें जहाँ model ने tool call किया। अनुमान लगाएँ: क्या model ने कभी दो मिलते-जुलते tools call किए जब एक से काम हो जाता? एक वाक्य लिखें कि tool set फूला हुआ लगा या अच्छी तरह डिज़ाइन किया हुआ।

- [ ] कोई tool चुनें जो संरचित data लौटाता है। एक नमूना return value पढ़ें। क्या return का कोई हिस्सा है जिसे model शायद अनदेखा कर देता? Return shape को दोबारा लिखें ताकि वह data बाहर रहे या दूसरी call में चला जाए, और अनुमान लगाएँ कि आपने कितने tokens बचाए।

- [ ] कल: ऐसा tool डिज़ाइन करें जो दोनों तरफ़ जा सकता है (नया tool या मौजूदा tool पर parameter)। अपने चुनाव के लिए दो वाक्य लिखें कि आपने अलग tool या parameter क्यों चुना, विकल्प की क्या क़ीमत होती, और आप कब दोबारा सोच सकते हैं।

## आगे बढ़ने के लिए

- [लेख: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
