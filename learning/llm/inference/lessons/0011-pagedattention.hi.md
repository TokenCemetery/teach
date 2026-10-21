---
title: "11. PagedAttention"
description: "vLLM के पीछे की block table की कार्यप्रणाली, उसका block-size trade-off, और वह sequences को साझा prefix का cache कैसे बाँटने देती है"
type: lesson
---

# पाठ 11. PagedAttention

**मिशन से संबंध:** vLLM का memory manager वह तंत्र है जो पाठ 2 की capacity सीमा को हर sequence की निश्चित लागत के बजाय एक बदलता, साझा हो सकने वाला लक्ष्य बनाता है, और यह पाठ वह जगह है जहाँ उस तंत्र का पूरा नाम लिया जाता है।
**मुख्य स्रोत:** [पेपर: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
**पूर्व-आवश्यकताएँ:** [पाठ 10](0010-standing-up-vllm.md), [KV cache](../GLOSSARY.md)

## वार्म-अप

1. ▢ Naive, सटे हुए, अधिकतम-length के आकार वाले KV cache आवंटन में fragmentation की कौन-सी दो क़िस्में थीं (पाठ 1)?

<details markdown="1"><summary>जाँचें</summary>

Internal fragmentation: जो sequence छोटा रहकर ख़त्म होता है वह फिर भी उस अधिकतम length के लिए आरक्षित memory पकड़े रहता है जो उसने कभी इस्तेमाल नहीं की। External fragmentation: अलग-अलग आकार के आरक्षित blocks के बीच की ख़ाली जगहें जिनमें किसी और sequence का cache समा नहीं सकता।

</details>

2. ▢ एक वाक्य में बताएँ, पाठ 1 के अनुसार PagedAttention operating-system की virtual memory से क्या उधार लेता है?

<details markdown="1"><summary>जाँचें</summary>

Cache को निश्चित आकार के blocks में बाँटना, बिना सटे रखना, और हर sequence की उस table से address करना जो logical positions को physical blocks से जोड़ती है, यानी OS page tables वाला ही विचार।

</details>

## यह जानें

### Block table, एक स्तर और गहराई में

हर sequence का KV cache निश्चित आकार के **blocks** में बँटा होता है, जिनमें से हर एक में tokens की तय संख्या के keys और values होते हैं। Sequence की **block table** उसके logical token positions को memory में physical block locations से जोड़ती है, वे जहाँ भी पड़े हों। किसी sequence का attention अपने blocks को इस table से खोजता है, यह मानकर नहीं कि वे सटे हुए हैं, और यही नीचे के memory manager को blocks वहाँ रखने देता है जहाँ उसे जगह मिले, ठीक वैसे जैसे OS page table किसी process के memory pages को physical RAM में कहीं भी रहने देती है।

### Block size एक trade-off है, मुफ़्त parameter नहीं

बड़े block size का मतलब है प्रति sequence कम blocks और कम block-table bookkeeping, पर उस sequence के आख़िरी, आंशिक रूप से भरे block में ज़्यादा बरबाद जगह जिसकी length बराबर नहीं बँटती (internal fragmentation, बस पाठ 1 के naive, पूरे-sequence वाले रूप से बहुत छोटे पैमाने पर)। छोटे block size से प्रति sequence कम जगह बरबाद होती है पर ज़्यादा blocks, और ज़्यादा block-table entries, ट्रैक करनी पड़ती हैं। vLLM का default block size (16 tokens) इन दोनों लागतों के बीच चुना हुआ बीच का रास्ता है, कोई मनमानी संख्या नहीं।

### Sequences के पार blocks साझा करना

क्योंकि किसी sequence के blocks तक पहुँच परोक्ष है, उसकी block table से, किसी निश्चित physical layout को मानकर नहीं, इसलिए दो अलग sequences की block tables एक ही physical block की ओर इशारा कर सकती हैं जब उसकी सामग्री एक जैसी हो, सबसे आम तौर पर साझा prompt prefix। Parallel sampling (एक ही prompt के कई completions माँगना) या beam search सबसे साफ़ मामले हैं: हर sample prompt के tokens का एक जैसा cache साझा करता है, इसलिए prompt के blocks को physically सिर्फ़ एक बार होना चाहिए, हर sample की block table उनकी ओर इशारा करती है। जब किसी sample का generation बाक़ियों से अलग हो जाता है (कोई भी नया, sample-विशिष्ट token), तो **copy-on-write** उस sample के लिए उस block की अपनी निजी copy बनाता है जिसे बदला जा रहा है, ठीक वही तंत्र जो operating system तब इस्तेमाल करता है जब दो processes memory pages तब तक साझा करते हैं जब तक उनमें से कोई लिख न दे।

![दो block tables, बाईं ओर sequence A और दाईं ओर sequence B, हर एक चार logical positions को physical block numbers से जोड़ती है। Positions 0 से 2 के लिए दोनों tables उन्हीं तीन साझा physical blocks की ओर इशारा करती हैं जिनमें एक जैसा prompt prefix है, इसलिए उस prefix का cache memory में सिर्फ़ एक बार है। Position 3 पर दोनों sequences ने अलग tokens generate किए हैं, इसलिए copy-on-write ने हर एक को उसका अपना निजी block दे दिया है: sequence A का block 9 और sequence B का block 3, जिनमें से कोई भी दूसरे के साथ साझा नहीं।](images/block-table-sharing.svg)

## अभ्यास

1. ▢ 16 tokens के block size के साथ, एक sequence 40 tokens का output generate करता है। वह कितने blocks इस्तेमाल करता है, और आख़िरी में कितनी जगह बरबाद होती है?

<details markdown="1"><summary>संकेत</summary>

40 को 16 से भाग दें और blocks की पूरी संख्या तक ऊपर गोल करें; बरबादी वह है जो आख़िरी, आंशिक रूप से भरे block में बिना इस्तेमाल बची।

</details>

<details markdown="1"><summary>जाँचें</summary>

`40 / 16 = 2.5`, ऊपर गोल करके 3 blocks। पहले दो में 32 tokens हैं; तीसरे में बचे 8, और उस block के बाक़ी 8 slots बरबाद, यानी पूरे sequence के बजाय एक block के पैमाने पर internal fragmentation।

</details>

2. ▢ छोटा block size उस बरबाद जगह को क्यों घटाता है, और बदले में उसकी क्या क़ीमत है?

<details markdown="1"><summary>जाँचें</summary>

छोटे block size का मतलब है कि आख़िरी, आंशिक रूप से भरे block में बरबाद करने को कम ख़ाली slots होते हैं, क्योंकि हर block में शुरू से ही कम positions हैं। क़ीमत यह कि कुल मिलाकर प्रति sequence ज़्यादा blocks होते हैं, और इसलिए memory manager को ज़्यादा block-table entries ट्रैक करनी और खोजनी पड़ती हैं।

</details>

3. ▢ 200-token के एक ही prompt से दस parallel samples माँगे गए हैं, block size 16 tokens है। Block sharing के साथ और उसके बिना prompt के cache को कितने physical blocks चाहिए?

<details markdown="1"><summary>संकेत</summary>

पहले निकालें कि 200-token के prompt की एक copy को कितने blocks चाहिए, फिर तय करें कि हर स्थिति में कितनी copies मौजूद हैं।

</details>

<details markdown="1"><summary>जाँचें</summary>

`200 / 16 = 12.5`, ऊपर गोल करके prompt की एक copy के लिए 13 blocks। साझा किए बिना, सभी 10 samples हर एक अपनी copy रखता है: `13 × 10 = 130` blocks। साझा करने पर, हर sample की block table साझा prompt के लिए उन्हीं 13 physical blocks की ओर इशारा करती है, इसलिए जब तक कोई sample अपने अलग tokens generate करना शुरू न करे, सिर्फ़ 13 blocks चाहिए।

</details>

4. ▢ प्रश्न 3 के दस samples में से एक ऐसा token generate करता है जो उस position पर किसी और sample के generate किए token से अलग है। उस बिंदु पर उस sample के cache का क्या होता है?

<details markdown="1"><summary>जाँचें</summary>

Copy-on-write चालू होता है: उस sample को उस block की अपनी निजी copy मिलती है जिस पर लिखा जा रहा है, उस साझा block को बदलने के बजाय जिसकी ओर बाक़ी हर sample की table अब भी इशारा कर रही है। सिर्फ़ अलग हुआ sample नए block की क़ीमत चुकाता है; बाक़ी नौ मूल को साझा करते रहते हैं।

</details>

5. ▢ vLLM के block size के चुनाव के बारे में कौन-सा दावा सही है?

    - a) बड़े blocks हमेशा छोटे blocks से ज़्यादा memory बरबाद करते हैं, बिना किसी बराबर के फ़ायदे के
    - b) Block size internal fragmentation और block-table bookkeeping के overhead के बीच सौदा करता है
    - c) Block size सिर्फ़ parallel sampling workloads को प्रभावित करता है, single-request serving को नहीं
    - d) छोटा block size हमेशा कुल memory उपयोग बढ़ाता है

<details markdown="1"><summary>जाँचें</summary>

**b)** छोटे blocks आख़िरी आंशिक रूप से भरे block में कम जगह बरबाद करते हैं पर ज़्यादा block-table entries ट्रैक करनी पड़ती हैं; बड़े blocks उल्टा करते हैं। (a) ग़लत है: बड़े blocks bookkeeping overhead घटाते हैं, जो असली फ़ायदा है। (c) ग़लत है: हर sequence, साझा हो या नहीं, blocks में बँटा होता है और fragmentation/bookkeeping का trade-off चुकाता है। (d) ग़लत है: छोटे blocks internal fragmentation घटाते हैं, जो कुल memory उपयोग को घटा सकता है, हमेशा बढ़ाता नहीं।

</details>

## असली दुनिया का अभ्यास

- [ ] vLLM के दस्तावेज़ों में उसका block-size flag या config option ढूँढें और पढ़ें कि उसकी default value क्या है और उसे बदलने के बारे में दस्तावेज़ क्या कहते हैं।
- [ ] अगर आप server चला सकते हैं, तो एक ही prompt के लिए कई parallel sampling requests (`n` एक से बड़ा) भेजें, और देखें कि दस्तावेज़ या logs prefix या block sharing के बारे में कुछ बताते हैं या नहीं।
- [ ] कल: prefix caching (बाक़ी बेमेल requests के पार किसी साझा system prompt के blocks को दोबारा इस्तेमाल करना) पर एक अनुच्छेद पढ़ें और नोट करें कि यह वही block-sharing का विचार है जो एक के भीतर के बजाय requests के पार लगाया गया है।

## आगे बढ़ने के लिए

- [पेपर: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
- [दस्तावेज़: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
