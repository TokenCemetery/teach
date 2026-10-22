---
title: "23. Tool के रूप में Code Execution"
description: कई संकरे अलग-अलग tools की जगह agent को एक sandboxed code-execution tool देना
type: lesson
---

# पाठ 23. Tool के रूप में Code Execution

**मिशन से संबंध:** यह तय करने के लिए कि किसी task को agent की ज़रूरत है भी या नहीं, आपको समझना होगा कि एक अकेला code-execution tool दर्जनों संकरे tools की जगह ले सकता है, token cost और latency घटाते हुए, पर मनमाने code के विरुद्ध मज़बूत sandbox लागू करना ज़रूरी हो जाता है।
**मुख्य स्रोत:** [लेख: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
**पूर्व-आवश्यकताएँ:** [पाठ 22](0022-sandboxing-and-approval-gates.md)

## वार्म-अप

1. ▢ पाठ 22 में हमने sandbox और approval gate में फ़र्क़ किया। हर एक क्या करता है, और model को ग़लती से file मिटाने से रोकने के लिए आप कौन-सा इस्तेमाल करेंगे?

<details markdown="1"><summary>जाँचें</summary>

Sandbox ऐसी execution सीमा है जो code को कुछ resources तक पहुँचने से रोकती है (जैसे अनुमत directory के बाहर की files)। Approval gate जोखिम भरे actions से पहले मानवीय चौकी है। ग़लती से मिटाने से रोकने के लिए आप ऐसा sandbox इस्तेमाल करेंगे जो tool को सिर्फ़ सुरक्षित directory tree के भीतर लिखने तक सीमित करे, ताकि model मिटाने को कहे तब भी sandbox उसे ठुकरा दे। Approval gate मिटाने की कोशिश से पहले रुककर इंसानी मंज़ूरी माँगता, पर मंज़ूर होने पर उसे रोकता नहीं।

</details>

2. ▢ पाठ 21 ने बड़े पैमाने पर tool discovery का विचार दिया: model हर definition को context में लोड करने की जगह जाँच सकता है कि कौन-से tools मौजूद हैं। यह कौन-सी समस्या हल करता है?

<details markdown="1"><summary>जाँचें</summary>

जब आपके पास सैकड़ों tools हों, तो हर tool की definition, नाम, विवरण और parameter schema को model की context window में पहले से लोड करना tokens ख़त्म कर देता है और model के लिए तर्क करना कठिन बनाता है कि कौन-सा tool call करे। Tool discovery model को उपलब्ध tools की जानकारी माँगने पर माँगने देती है या क्षमताएँ खोजने के लिए introspection endpoint call करने देती है, इसलिए पूरी सूची को शुरुआती context में रहना ज़रूरी नहीं।

</details>

## यह जानें

### कई संकरे tools के विकल्प के रूप में code execution

Data विश्लेषण के परिदृश्य पर सोचें। Code execution के बिना, आप model को ये tools दे सकते हैं:

- list_files: directory की files की सूची लौटाता है
- read_csv: CSV file पढ़कर पहली N पंक्तियाँ लौटाता है
- compute_mean: column का औसत निकालता है
- compute_median: column की माध्यिका निकालता है
- filter_rows: शर्त से table को छानता है
- sort_by: table को column के हिसाब से क्रमबद्ध करता है
- write_csv: table को वापस file में लिखता है

Model को अब तय करना है कि कौन-सा tool किस क्रम में call करे। वह read_csv, फिर filter_rows, फिर compute_mean call कर सकता है: model के loop से तीन round trips। हर round trip यह तर्क करने में tokens जलाता है कि अगला कौन-सा tool call करना है, और हर tool definition शुरुआती context window में tokens खाती है।

इसके बजाय model को एक tool दें: sandboxed code interpreter। Model छोटा Python program लिखता है:

```python
import pandas as pd

data = pd.read_csv('data.csv')
filtered = data[data['age'] > 30]
result = filtered['salary'].mean()
print(result)
```

Model इसे एक बार चलाता है और जवाब पा लेता है। फ़ायदे: तीन की जगह एक tool call, सात की जगह एक tool definition, और model अगला कौन-सा tool call करना है यह दोबारा तर्क किए बिना एक ही turn में operations जोड़ सकता है।

### Cost और latency के फ़ायदे

यह तरीक़ा token cost और latency दोनों घटाता है:

- Token cost: आप कई की जगह एक tool definition का ख़र्च चुकाते हैं, और कौन-सा tool call करना है इस पर model का reasoning का बोझ सामान्य code लिखने में सिमट जाता है, जो model पहले से कुशलता से करता है।
- Latency: तीन या सात की जगह एक tool call का round trip होने से agent का wall-clock समय अनुपात में घटता है।

बड़े पैमाने पर या real-time ज़रूरतों वाले agents के लिए ये बचतें जुड़ती जाती हैं।

### बड़े पैमाने पर tool discovery से संबंध

पाठ 21 ने विचार दिया कि हर tool definition को पहले से context में लोड करने की जगह, model उपलब्ध क्षमताओं को गतिशील रूप से खँगाल सकता है। Code execution इस सिद्धांत का ठोस रूप है: model को हर data-transformation tool पहले से लोड नहीं चाहिए क्योंकि वह transformation करने का code ख़ुद लिख सकता है। उपलब्ध क्षमताएँ (functions, libraries, system utilities) code के चलने पर खोजी जाती हैं, शुरुआती context में नहीं।

कुछ systems में, code-execution tool का अपना discovery mechanism हो सकता है: ऐसा function जिसे model बुलाकर देख सके कि कौन-सी libraries उपलब्ध हैं, कौन-से data sources तक पहुँच सकता है, या कौन-से system commands उपलब्ध हैं। यह discovery के ऊपर discovery की परत लगाता है।

### मनमाने code के विरुद्ध sandbox को क्या लागू करना होगा

पाठ 22 में हमने देखा कि sandbox tool के execution की पहुँच के आसपास सीमाएँ लागू करता है: filesystem paths, network hosts, resource की सीमाएँ। जब tool "model का लिखा मनमाना code चलाओ" है, तो sandbox को ये सीमाएँ ऐसे code के विरुद्ध लागू करनी होती हैं जो जाने हुए JSON schema वाली तय tool call से कहीं ज़्यादा अभिव्यंजक और अप्रत्याशित है।

Model ऐसा code लिख सकता है जो:

- symbolic links, path traversal की चालें (/../..), या सीमा के बाहर टटोलने के लिए find या ls जैसी system utilities बुलाकर filesystem की सीमा से निकलने की कोशिश करे।
- ऐसा network code लिखे जो allowlist के बाहर के hosts तक पहुँचने की कोशिश करे।
- अनंत loops, recursive functions, या resources ख़त्म करने की कोशिश करने वाले memory-allocate करते loops चलाए।
- ऐसे functions या methods बुलाए जिनके होने की code को उम्मीद है पर जिन्हें harness मना करना चाहता है।

Sandbox इन सबको थामने के लिए पर्याप्त मज़बूत होना चाहिए। यह तय tool को sandbox करने से कठिन है क्योंकि code की सतह असीमित है। सच्चा code-execution sandbox अक्सर code को अलग किए हुए container या process में seccomp नियमों, network namespaces और resource cgroups के साथ चलाता है, सिर्फ़ filesystem permission जाँचों से नहीं।

### Code execution बनाम संकरे tools कब

Code execution शक्तिशाली है पर sandbox की जटिलता लाता है। आपको इसे तब पसंद करना चाहिए जब:

- Model को कई छोटे operations जोड़ने हैं जिनके लिए वरना कई round trips चाहिए।
- Operations एल्गोरिदमिक या data-transformation पर केंद्रित हैं (छानना, एकत्रीकरण, गणना, format बदलना)।
- उपलब्ध क्षमताएँ भली-भाँति परिभाषित और अपेक्षाकृत स्थिर हैं।

आपको संकरे, ख़ास मक़सद के tools पर टिके रहना चाहिए जब:

- Operation सचमुच ऊँचे दाँव वाला है और स्पष्ट मानवीय निगरानी से फ़ायदा पाता है (email भेजना, सार्वजनिक रूप से पोस्ट करना, पैसे ख़र्च करना)।
- Operation की सुरक्षा inputs या outputs को ऐसे domain-विशिष्ट तरीक़ों से validate करने पर निर्भर है जिन्हें harness समझता है पर code नहीं।
- Operation दुर्लभ है और एक tool की token बचत sandbox की जटिलता से ज़्यादा नहीं।

दोनों तरीक़े साथ रह सकते हैं: agent के पास data सँभालने के लिए code-execution tool और emails भेजने या नतीजे प्रकाशित करने के लिए संकरे approval-gated tools हो सकते हैं।

## अभ्यास

1. ▢ आपके agent में अभी string हेरफेर के लिए सात अलग tools हैं: split_string, join_strings, uppercase, lowercase, replace_substring, reverse_string और trim_whitespace। क्या आप सातों को एक अकेले code-execution tool से बदल सकते हैं? आप क्या पाएँगे और क्या खोएँगे?

<details markdown="1"><summary>जाँचें</summary>

हाँ, बदल सकते हैं। Model पाएगा: सात की जगह एक tool definition, जटिल string operation के लिए सात round trips की जगह एक tool call, और tool के नाम का अंदाज़ा लगाने की जगह पढ़ने लायक़ code ("result = text.upper()") लिखने की क्षमता। आप खोएँगे: हर operation के लिए स्पष्ट guardrails (हर tool input validate कर सकता है), और अनुमान लायक़ latency (code execution अब इस पर निर्भर होकर बदलता है कि model क्या लिखता है)। String हेरफेर के लिए code-execution तरीक़ा आमतौर पर जीतता है क्योंकि operations सरल हैं और harness domain-विशिष्ट तर्क के बिना filesystem या resource की सीमा लागू कर सकता है।

</details>

2. ▢ आप स्वास्थ्य-सेवा system के लिए agent डिज़ाइन कर रहे हैं जो मरीज़ों के records पढ़कर निदान के सुझाव बना सकता है। क्या आपको इसे ऐसे code-execution tool से देना चाहिए जहाँ model अपना data-access code लिखे, या read_patient_record, filter_by_condition और compute_risk_score जैसे संकरे tools से?

<details markdown="1"><summary>संकेत</summary>

सोचें कि स्वास्थ्य-सेवा के संदर्भ में "सुरक्षा" का क्या मतलब है। Harness को क्या लागू करना है, और क्या सामान्य-उद्देश्य वाला code sandbox उसे लागू कर सकता है, या उसे domain-विशिष्ट तर्क चाहिए?

</details>

<details markdown="1"><summary>जाँचें</summary>

यहाँ संकरे tools बेहतर हैं। स्वास्थ्य-सेवा system की सख़्त compliance ज़रूरतें हैं (HIPAA, audit logging, data access control) जिन्हें harness शायद domain-विशिष्ट तर्क से लागू करता है, filesystem sandboxing से नहीं। संकरे read_patient_record tool में authorization जाँच, audit logging और data redaction हो सकते हैं; code-execution tool इन्हें आसानी से लागू नहीं कर सकता, क्योंकि harness को model का लिखा code जाँचना पड़ेगा, जो code execution का मक़सद ही ख़त्म कर देता है। ऊँचे दाँव approval gates को भी ज़्यादा कीमती बनाते हैं। जब operation की सुरक्षा filesystem की सीमाओं पर नहीं बल्कि domain-विशिष्ट business logic पर निर्भर हो, तब संकरे, ऑडिट योग्य tools पसंद करें।

</details>

3. ▢ Code execution के बारे में इनमें से कौन-सा कथन सच है?

    - a) Code execution अलग tools से हमेशा तेज़ है क्योंकि वह round trips घटाता है, सरल एकल operations के लिए भी।
    - b) Code execution token cost घटाता है क्योंकि एक tool definition कई की जगह लेती है, पर latency तभी बचाता है जब model कई operations जोड़े।
    - c) Code execution sandboxes की ज़रूरत ख़त्म कर देता है क्योंकि code भरोसेमंद है।
    - d) Code execution को approval gates नहीं चाहिए क्योंकि harness code चलने से पहले उसे जाँच सकता है।

<details markdown="1"><summary>जाँचें</summary>

**b)** Code execution token cost घटाता है क्योंकि एक tool definition कई की जगह लेती है, पर latency तभी बचाता है जब model कई operations जोड़े। Token की बचत असली है (कई की जगह एक definition)। Latency की बचत तभी मायने रखती है जब model कई operations कर रहा हो जिनके लिए वरना कई round trips चाहिए; एक operation के लिए समय बराबर या बदतर है। विकल्प a ग़लत है (एकल operations को फ़ायदा नहीं)। विकल्प c ग़लत है (code execution को मज़बूत sandboxes चाहिए क्योंकि code मनमाना है)। विकल्प d ग़लत है (ऊँचे दाँव वाले operations के लिए approval gates अब भी सही हैं, और पहले से जाँचना सारी ग़लतियाँ नहीं रोकता)।

</details>

4. ▢ समझाएँ कि जब tool "delete_file" जैसे ख़ास tool की जगह "code execution" हो तो sandbox का काम कठिन क्यों हो जाता है। एक ठोस परिदृश्य बताएँ जहाँ यह कठिनाई मायने रखती है।

<details markdown="1"><summary>जाँचें</summary>

ख़ास tool के साथ, harness पहले से जानता है कि tool क्या करेगा और उस ख़ास बिंदु पर सीमा लागू कर सकता है (delete_file tool सिर्फ़ सुरक्षित directory की files छू सकता है)। Code execution में, harness तब तक नहीं जानता कि code क्या करेगा जब तक वह चल न जाए; code system utilities बुला सकता है, network sockets खोल सकता है, या ऐसी भाषा की सुविधाएँ इस्तेमाल कर सकता है जिनकी harness को उम्मीद नहीं। एक ठोस परिदृश्य: model ऐसा code लिखता है जो subprocess.Popen बुलाकर "ls /../.." जैसा shell command चलाता है ताकि इच्छित सीमा से आगे filesystem को टटोले। सिर्फ़ filesystem-permission sandbox इसे नहीं रोकेगा; sandbox को मनमाने system calls रोकने के लिए seccomp नियम या container चाहिए। इसीलिए code-execution sandboxes आमतौर पर संकरे-tool sandboxes से ज़्यादा जटिल होते हैं।

</details>

5. ▢ आपका agent data का विश्लेषण करने के लिए code execution इस्तेमाल करता है। Model ऐसा code लिखता है जिसे CSV file से पढ़ना चाहिए था, पर इसके बजाय वह ऐसा code लिखता है जो इंटरनेट से file डाउनलोड करने की कोशिश करता है। Sandbox network पहुँच बिल्कुल नहीं देता। क्या होता है, और क्या यह sandbox की विफलता है?

<details markdown="1"><summary>जाँचें</summary>

Code चलता है, network call की कोशिश करता है, और network operation ठुकरा दिया जाता है या अटक जाता है। यह sandbox की विफलता नहीं है; यह sandbox का इरादे के मुताबिक़ काम करना है। Sandbox का काम code को अपनी सीमा के बाहर के resources तक पहुँचने से रोकना है, यह पक्का करना नहीं कि code सही है या वही करता है जो model ने चाहा था। Sandbox की विफलता तब होती जब no-network नियम के बावजूद network call सफल हो जाती। Model की ग़लती (ग़लत code लिखना) harness के काम (सीमाएँ लागू करना) से अलग है।

</details>

## असली दुनिया का अभ्यास

- [ ] अपने काम या किसी जाने-पहचाने system के इस्तेमाल होने वाले tools सूचीबद्ध करें। तीन या ज़्यादा आपस में जुड़े tools का समूह पहचानें और खींचें कि उन्हें code-execution tool से कैसे बदला जा सकता है। यह बदलाव करने के लिए sandbox पर भरोसा करने को आपको क्या चाहिए होगा?
- [ ] एक सरल data-विश्लेषण program लिखें (table छानना, एकत्रीकरण निकालना, क्रमबद्ध करना)। कल्पना करें कि आप model हैं। अलग tools के साथ tool-calling loop से कितने round trips लगते, और code execution के साथ कितने?
- [ ] कल: "Code Execution with MCP" लेख की समीक्षा करें और sandbox में एक design चुनाव पहचानें (resource की सीमा, filesystem की सीमा, network की पाबंदी) और समझाएँ कि वह ख़ास सीमा लेख के use case के लिए क्यों मायने रखती है।

## आगे बढ़ने के लिए

- [लेख: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए primary source को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
