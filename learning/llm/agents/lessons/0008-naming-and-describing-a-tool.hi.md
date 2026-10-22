---
title: "8. Tool का नाम रखना और उसे बयान करना"
description: Tool का नाम और विवरण ही वह है जिसे पढ़कर model तय करता है कि उसे कब और कैसे call करना है
type: lesson
---

# पाठ 8. Tool का नाम रखना और उसे बयान करना

**मिशन से संबंध:** Agent की tool सतह डिज़ाइन करना (नाम, विवरण, return shapes, और वह permission सीमा जो तय करती है कि वह बिना निगरानी के क्या कर सकता है) इस समझ से शुरू होता है कि नाम और विवरण किसी इंसान के लिए API दस्तावेज़ नहीं हैं: वे prompt सतह हैं जिन्हें model पढ़कर तय करता है कि tool को कब और कैसे call करना है।
**मुख्य स्रोत:** [लेख: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
**पूर्व-आवश्यकताएँ:** [पाठ 7](0007-the-transcript-as-state.md), [Tool](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 7 से: Model agent loop के पिछले turn में जो हुआ उसे "याद" कैसे रखता है?

<details markdown="1"><summary>जाँचें</summary>

वह अपने आप याद नहीं रखता। Harness हर call पर पूरा transcript दोबारा भेजता है, इसलिए जो memory जैसा दिखता है वह असल में model का वह सब फिर से पढ़ना है जो उसे पहले दिखाया गया था।

</details>

2. ▢ पाठ 7 से: Transcript ही agent की पूरी state क्यों है, harness की अलग से रखी कोई और data structure क्यों नहीं?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि model सिर्फ़ transcript देखता है। जो भी तथ्य harness जानता है पर उसमें कभी नहीं जोड़ता, वह model के लिए अदृश्य है, चाहे harness भीतर और जो भी ट्रैक करे।

</details>

## यह जानें

### Tool का विवरण API दस्तावेज़ नहीं है

एक ग़लती जो हर builder एक बार करता है: tool का विवरण ऐसे लिखना जैसे आप REST endpoint का docstring लिखते।

```text
Bad:
name: fetch_user
description: Fetches user data
```

कई tools में से चुनने वाले model के लिए यह बहुत संक्षिप्त है। Model के पास कोई संदर्भ नहीं कि `fetch_user` बनाम `get_user` बनाम `lookup_user` कब इस्तेमाल करना है। वह नहीं जानता कि कौन-सा data लौटता है या क्या देना होता है। वह तर्क नहीं कर सकता कि इसे अभी call करे या बाद में। जब model को तीन tools दिखते हैं और कोई साफ़ मार्गदर्शन नहीं, तो वह अंदाज़ा लगाता है, और इंसान से ज़्यादा बार ग़लत लगाता है।

वही tool model के लिए बयान किया हुआ:

```text
Better:
name: fetch_user
description: Look up a user profile by their numeric ID. Returns the user's name, email, account status, and the current version number of their profile. Use this before calling update_user, since update_user requires you to pass the profile's current version number to prevent write conflicts. Returns null if the user ID does not exist.
```

अब model पूरी तस्वीर देख सकता है: इसे कब call करना है (update_user से पहले), इसे क्या चाहिए (numeric ID), और यह क्या लौटाता है (अगला क़दम तय करने के लिए काफ़ी जानकारी)। यह विवरण model के फ़ैसले लेने की सेवा करता है, API docs पढ़ते किसी इंसान की नहीं।

अंतर यह है: REST docstring इंसानी programmer को बताता है कि tool कैसे इस्तेमाल करें। Agent prompt में tool का विवरण model को बताता है कि tool को कब और क्यों call करना है, क्या देना है, और कौन-सा नतीजा अपेक्षित है। Model के पास manual नहीं है; आपका विवरण ही उसका एकमात्र मार्गदर्शक है।

### दूसरे tools से अलग नाम देना

Model tools को उनके नाम और विवरण पढ़कर चुनता है, और कोई संकेत नहीं होता। अगर दो tools एक जैसे सुनाई दें, तो model ग़लत वाला call करेगा या सुरक्षा के लिए दोनों call करेगा।

```text
Bad:
- name: list_files
  description: Lists files in a directory
- name: list_file_contents
  description: Lists the contents of a file
```

Model इन्हें गड़बड़ा सकता है या सिर्फ़ एक चाहिए होने पर भी दोनों call कर सकता है। नाम बहुत क़रीब हैं।

```text
Better:
- name: list_directory
  description: List all files and subdirectories in a directory. Shows names and file sizes. Does not show file contents.
- name: read_file
  description: Read the complete contents of a single file. Returns text as a string.
```

अब नाम अलग हैं (list_directory बनाम read_file) और विवरण साफ़ बताते हैं कि हर एक क्या करता है और क्या नहीं। Model सही वाला चुनेगा।

नियम: tool का नाम इस तरह बताए कि वह क्या करता है कि उसी tool set के किसी दूसरे tool से गड़बड़ाया न जा सके। अगर आपके कई search tools हैं, तो सबको `search` न कहें। उन्हें `search_documentation`, `search_code`, `search_logs` कहें।

### Parameter के विवरण भी उतने ही मायने रखते हैं

सबसे ऊपर का tool विवरण सबसे ज़्यादा ध्यान पाता है, पर parameter के विवरण भी सही नतीजों के लिए उतने ही ज़रूरी हैं।

```text
Bad:
name: create_issue
description: Creates a GitHub issue
parameters:
  - name: title
    type: string
    description: Issue title
  - name: body
    type: string
    description: Issue body
```

Model नहीं जानता कि title किस format में होना चाहिए, कितना लंबा हो सकता है, सवाल होना चाहिए या कथन। Body तो और बुरा है: Markdown है? सादा text? कितना विस्तृत? क्या model समस्या बताए या हल?

```text
Better:
name: create_issue
description: Create a new issue in the repository
parameters:
  - name: title
    type: string
    description: A one-line summary of the problem or feature request. Be specific and actionable. Examples: "Handle null config values in startup" or "Add support for JSON output format".
  - name: body
    type: string
    description: Detailed description in Markdown. Include what you tried, what failed, and what you expect to happen. If it is a feature request, explain why it matters. If it is a bug, include steps to reproduce.
```

अब model जानता है कि किस तरह का title लिखना है और body में कितना ब्योरा देना है। वह बेहतर नतीजे देगा।

### आम विफलता: मिलते-जुलते tools का model को उलझाना

सबसे बुरी स्थिति तब है जब दो tools इतने मिलते-जुलते हों कि विवरणों के बावजूद model उन्हें अलग न कर सके।

```text
Very bad:
- name: update_user
  description: Update user information
- name: change_user
  description: Modify user data
```

ये नाम और विवरण लगभग एक ही बात कहते हैं। Model दोनों call कर सकता है, या ग़लत वाला, या पूछने में समय बर्बाद कर सकता है। आपने उसे चुनने का कोई तरीक़ा नहीं दिया।

हल है नामों और विवरणों को इतना अलग बनाना कि हाथ के काम के लिए सिर्फ़ एक ही समझ में आए:

```text
Better:
- name: update_user_profile
  description: Change a user's displayed name, email, or profile picture. Requires the profile version number to prevent conflicts.
- name: update_user_permissions
  description: Grant or revoke access roles for a user, such as admin, editor, or viewer. Only callable by the current account's admin.
```

अब model देख सकता है कि पहला tool निजी जानकारी के लिए है और दूसरा access control के लिए। वह सही वाला चुनेगा।

## अभ्यास

1. ▢ आपके पास दो tools हैं: `send_email` और `send_notification`। Model कभी-कभी सिर्फ़ एक चाहिए होने पर दोनों call करता है। हर tool के लिए एक-एक वाक्य लिखें जो model को साफ़ कर दे कि कौन-सा कब इस्तेमाल करना है।

<details markdown="1"><summary>जाँचें</summary>

संभावित उत्तर: `send_email` हो सकता है "Send an email message to an email address. Use this for messages longer than a few lines or when you need to include attachments or formatted text." `send_notification` हो सकता है "Send a brief in-app notification to a user. Use this for short status updates or alerts that do not require the user to leave the application." मुख्य बात यह है कि विवरण model को बताता है कि हर tool किस तरह का message अपेक्षित करता है, ताकि वह सही चुन सके।

</details>

2. ▢ आपका `get_user` tool user record के सारे fields लौटाता है: id, name, email, phone, address, company, biography, preferences, subscription tier, और दस और। Parameter का विवरण model को बताए कि क्या देना है। विवरण में आपको क्या नहीं डालना चाहिए?

<details markdown="1"><summary>संकेत</summary>

सोचें कि tool को सही तरह call करने के लिए model को क्या जानना चाहिए, और क्या जानना अच्छा तो है पर call के लिए ज़रूरी नहीं।

</details>

<details markdown="1"><summary>जाँचें</summary>

आपको tool के लौटाए हर field की सूची नहीं डालनी चाहिए। Tool का विवरण बताता है कि model को क्या वापस मिलता है; parameter का विवरण बताता है कि call करने के लिए model को क्या देना होगा। `user_id` parameter के लिए विवरण कुछ ऐसा कहे: "The numeric ID of the user. If you do not have the ID, call search_users first." Parameter के विवरण में यह न लिखें कि कौन-से fields लौटते हैं; वह सबसे ऊपर के tool विवरण में जाता है।

</details>

3. ▢ Tool के parameters के लिए विस्तृत विवरण लिखने का सबसे अच्छा कारण इनमें से कौन-सा है?

    - a) API दस्तावेज़ीकरण के मानकों का पालन करना
    - b) बाद में code पढ़ने वाले इंसानी engineers की मदद करना
    - c) Model को यह तय करने में मदद करना कि कौन-सा मान देना है और tool को call करना भी है या नहीं
    - d) उपयोगकर्ता को जितनी tool calls करनी पड़ें उनकी संख्या घटाना

<details markdown="1"><summary>जाँचें</summary>

**c)** Model को यह तय करने में मदद करना कि कौन-सा मान देना है और tool को call करना भी है या नहीं। Model parameter के विवरण पढ़कर समझता है कि tool कौन-से arguments अपेक्षित करता है और ग़लत मान देने पर क्या होगा। (a) अप्रासंगिक है; यह prompt engineering है, API design नहीं। (b) साथ में मिलने वाला फ़ायदा हो सकता है, पर प्राथमिक कारण नहीं। (d) बात चूक जाता है: विस्तृत विवरण model को कम ग़लत calls करने में मदद करते हैं, कुल calls कम करने में नहीं।

</details>

4. ▢ आप `search` नाम का tool बना रहे हैं। आपके पास `search_documents`, `search_issues` और `search_users` नाम के tools भी हैं। यह tool का नाम समस्या क्यों है, और इसके बजाय आपको क्या करना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

Tool `search` बहुत सामान्य है। जब model को search करना होगा तो उसे पता नहीं चलेगा कि कौन-सा search tool call करे। वह सबको call कर सकता है, या बेतरतीब चुन सकता है। इसके बजाय `search` का नाम बदलकर कुछ ख़ास रखें जैसे `search_logs` या `search_comments` या `search_code`। नियम है: हर tool का नाम इतना ख़ास हो कि model जाने वह क्या करता है, और दूसरे tool नामों से इतना अलग कि model उसे गड़बड़ाए नहीं।

</details>

## असली दुनिया का अभ्यास

- [ ] किसी LLM application या agent framework के लिए जिसे आप इस्तेमाल करते हैं, tool definitions (नाम और विवरण) खोजें। हर tool का विवरण पढ़ें। एक ऐसा tool लिखें जिसका विवरण इतना साफ़ है कि आप समझते हैं model को उसे कब call करना चाहिए, और एक ऐसा जिसका विवरण बहुत अस्पष्ट है। नोट करें कि पहला क्यों काम करता है और दूसरे में क्या छूटा है।

- [ ] कमांड लाइन का कोई tool चुनें जिसे आप नियमित इस्तेमाल करते हैं (जैसे `grep` या `find`)। कल्पना करें कि आपको उसे ऐसे model के लिए बयान करना है जो आपके filesystem के बारे में कुछ नहीं जानता। एक वाक्य का विवरण लिखें जो model को बताए कि tool क्या करता है और मिलते-जुलते tool की जगह उसे कब इस्तेमाल करना है।

- [ ] कल: किसी असली agent या API दस्तावेज़ का ऐसा tool विवरण लें जो आपको ख़राब लिखा लगता है। उसे ऐसे model के लिए दोबारा लिखें जो कई मिलते-जुलते tools में से चुन रहा है। उसे कम से कम दोगुना लंबा बनाएँ, इस्तेमाल करने के मौक़े का एक उदाहरण दें, और एक चीज़ बताएँ जिसके लिए वह अच्छा नहीं है।

## आगे बढ़ने के लिए

- [लेख: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
