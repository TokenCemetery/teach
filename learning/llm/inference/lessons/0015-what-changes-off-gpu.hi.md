---
title: "15. GPU से बाहर क्या बदलता है"
description: "llama.cpp का server खड़ा करना, और batching, cache management और quantization हर एक CPU/edge के पैमाने पर कैसे अलग दिखते हैं"
type: lesson
---

# पाठ 15. GPU से बाहर क्या बदलता है

**मिशन से संबंध:** यह चरण 5 का समापन है और मिशन के सफलता-मापदंडों का दूसरा आधा: CPU पर चलता और असली requests का जवाब देता llama.cpp stack, जिसमें चरण 1 से 4 की हर अवधारणा को दोबारा परखा गया है कि इस पैमाने पर असल में क्या अब भी लागू होता है।
**मुख्य स्रोत:** [Repo: llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp)
**पूर्व-आवश्यकताएँ:** [पाठ 14](0014-llamacpp-architecture.md), [KV cache](../GLOSSARY.md)

## वार्म-अप

1. ▢ llama.cpp में `--threads` क्या नियंत्रित करता है, और यह vLLM के `--max-num-seqs` से कैसे अलग है?

<details markdown="1"><summary>जाँचें</summary>

`--threads` एक अकेले sequence के अपने matrix multiplies को CPU के physical cores में बाँटता है। `--max-num-seqs` इसके बजाय सीमित करता है कि कितने concurrent sequences एक GPU batch step साझा करें, और उनमें memory traffic बाँटता है। एक एक sequence के compute को तेज़ करता है; दूसरा memory bandwidth की लागत कई में फैलाता है।

</details>

2. ▢ Quantization नाम `Q4_K_M` को उसके तीन हिस्सों में खोलें।

<details markdown="1"><summary>जाँचें</summary>

`Q4`: लगभग 4 bits प्रति weight। `K`: k-quant विधि जो एक tensor के भीतर precision मिलाती है। `M`: उस विधि की आकार/गुणवत्ता configurations में से मध्यम preset।

</details>

## यह जानें

### Server खड़ा करना

llama.cpp का अपना server, `llama-server`, GGUF file load करता है और OpenAI-compatible HTTP endpoint खोलता है, वही request का आकार जो पाठ 10 ने vLLM के विरुद्ध इस्तेमाल किया:

```text
llama-server -m model.Q4_K_M.gguf --threads 8
```

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "model.Q4_K_M.gguf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

Request और response का आकार जाना-पहचाना है। जो बदलता है वह उसके नीचे की हर चीज़ है।

![तीन पंक्तियों की तुलना। Batching: GPU पर continuous batching memory bandwidth को सैकड़ों concurrent requests में बाँटती है; CPU/edge के पैमाने पर, जहाँ concurrent requests इकाई अंकों से लेकर कुछ दर्जन ही हैं, एक sequence के compute को cores में बाँटने वाले threads उसकी जगह लेते हैं। Cache management: GPU पर PagedAttention एक बड़े, लगातार बदलते साझा pool को सँभालता है; CPU/edge के पैमाने पर प्रति-sequence सादा, सटा हुआ cache काफ़ी है। Quantization का समय: vLLM के साथ GPU पर scheme launch के समय चुना गया serve-time flag है; llama.cpp पर फ़ैसला तभी तय हो चुका था जब किसी ख़ास GGUF quant स्तर को चुना गया, server के शुरू होने से पहले।](images/gpu-vs-cpu-edge-mechanisms.svg)

### इस पैमाने पर batching कम मायने रखती है

vLLM की continuous batching (पाठ 4 और 5) इसलिए है कि GPU की memory-bandwidth की लागत को सैकड़ों concurrent अजनबियों की requests में बाँटा जा सके। CPU के पास उस लागत को बाँटने के लिए हज़ारों parallel cores जैसा कुछ नहीं है; llama.cpp का server मुट्ठी भर parallel request slots support करता है, पर इकाई अंकों से कुछ दर्जन के पैमाने पर, सैकड़ों नहीं। यह कोई कमी वाला feature नहीं है: edge deployment का आम workload, एक device जो अपने ही user को serve करता है, में batch करने को सैकड़ों concurrent requests शायद ही कभी होती हैं। भारी batching ऐसी समस्या हल करती है जो CPU/edge serving में आम तौर पर होती ही नहीं।

### इस पैमाने पर cache को paging की भी ज़रूरत नहीं

PagedAttention (पाठ 11) इसलिए है कि कई sequences memory को कुशलता से साझा कर सकें और concurrent requests के बड़े, लगातार बदलते pool में fragmentation से बचा जा सके। CPU/edge के पैमाने पर, जहाँ कम concurrent sequences हैं और fragment होने को कोई बड़ा साझा pool नहीं, प्रति-sequence सादा, सटा हुआ cache आवंटन आम और काफ़ी है। जिस समस्या को PagedAttention हल करता है वह सिद्धांत में ग़ायब नहीं होती, बस शायद ही कभी उस पैमाने तक पहुँचती है जहाँ उसकी जटिलता अपनी क़ीमत वसूल करे।

### Quantization का फ़ैसला पहले ही हो चुका है

vLLM पर `--quantization` serve-time का flag है: scheme तब चुनी जाती है जब server शुरू होता है, पहले से quantized checkpoint से या load पर quantize होने वाले से। llama.cpp पर वह फ़ैसला पहले हो चुका था, जब किसी ख़ास quant स्तर पर GGUF file चुनी (या बनाई) गई, जैसे `Q4_K_M`। उसे बदलने के लिए कोई serve-time flag नहीं है; quantization बदलने का मतलब है दूसरी GGUF file download करना या बनाना। पाठ 7 से 9 का trade-off, memory बनाम accuracy बनाम speed, अब भी लागू है, बस वह server के शुरू होने से पहले तय हो चुका है, startup पर configure नहीं होता।

## अभ्यास

1. ▢ एक `llama-server` instance पर एक ही समय में तीन requests आती हैं, सब एक अकेले edge device के अपने users से। जाँचने से पहले अनुमान लगाएँ: हर request के throughput का क्या होता है, और यह GPU पर continuous batching जो करती है उससे अलग क्यों है?

<details markdown="1"><summary>जाँचें</summary>

हर request का throughput लगभग उतने अनुपात में गिरता है जितने threads उसे अब साझा करने पड़ते हैं, क्योंकि CPU की तय core संख्या concurrent requests में बँट जाती है, हर एक को पूरी thread संख्या अपने लिए नहीं मिलती। यह GPU की continuous batching से अलग है, जो पहले से ज़रूरी memory-bandwidth की लागत को concurrent sequences में प्रति sequence थोड़ी अतिरिक्त क़ीमत पर बाँट देती है; CPU compute को requests में बाँटने में ऐसी कोई "वैसे भी चुकाई जा रही" लागत नहीं जिसे बाँटा जा सके।

</details>

2. ▢ भारी, vLLM-शैली की continuous batching आम CPU/edge deployment के लिए GPU server की तुलना में कम मायने क्यों रखती है?

<details markdown="1"><summary>जाँचें</summary>

Continuous batching अपनी जटिलता की क़ीमत तब वसूल करती है जब कई concurrent अजनबियों की requests GPU की memory-bandwidth की लागत साझा करती हैं। आम edge deployment, एक device जो अपने user को serve करता है, में batch करने को इतनी concurrent requests शायद ही कभी होती हैं, इसलिए जिस समस्या को यह तंत्र हल करता है वह इस पैमाने पर आम तौर पर मौजूद ही नहीं।

</details>

3. ▢ llama.cpp deployment के लिए quantization का फ़ैसला कहाँ हुआ, इसकी तुलना में कि vLLM deployment के लिए वह कहाँ होता है?

<details markdown="1"><summary>जाँचें</summary>

llama.cpp के लिए वह तब हुआ जब कोई ख़ास GGUF file (किसी ख़ास quant स्तर पर, जैसे `Q4_K_M`) चुनी या बनाई गई, server के शुरू होने से पहले; उसे बदलने का मतलब दूसरी file इस्तेमाल करना है। vLLM के लिए वह serve-time का flag, `--quantization`, है जो server launch करते समय चुना जाता है। Trade-off वही है जो पाठ 7 से 9 ने सिखाया; फ़र्क़ सिर्फ़ इसमें है कि फ़ैसला कब पक्का हो जाता है।

</details>

4. ▢ PagedAttention-शैली का memory management CPU/edge के पैमाने पर कम ज़रूरी क्यों होता है, इस बारे में कौन-सा दावा सही है?

    - a) CPU hardware paging को तकनीकी रूप से असंभव बना देता है
    - b) आम workload में इतने कम concurrent sequences होते हैं कि प्रति-sequence सादा, सटा हुआ cache काफ़ी है
    - c) llama.cpp का GGUF format किसी भी तरह की paged memory के साथ असंगत है
    - d) CPU serving में KV caches होते ही नहीं

<details markdown="1"><summary>जाँचें</summary>

**b)** कम concurrent sequences और fragment होने को कोई बड़ा साझा pool न होने पर सादा आवंटन आम तौर पर काफ़ी है; जिस समस्या को PagedAttention हल करता है वह शायद ही कभी उस पैमाने तक पहुँचती है जहाँ उसकी जटिलता अपनी क़ीमत वसूल करे। (a) ग़लत है: CPU hardware में कुछ भी paging को नकारता नहीं, यह design का trade-off है, सीमा नहीं। (c) ग़लत है: GGUF model file का वर्णन करता है, runtime के cache layout का नहीं। (d) ग़लत है: CPU पर भी decode को KV cache चाहिए, उसी कारण से जो पाठ 1 ने स्थापित किया; बस उसे आम तौर पर ज़्यादा सादे ढंग से सँभाला जाता है।

</details>

## असली दुनिया का अभ्यास

- [ ] llama.cpp को build या install करें, कोई छोटा GGUF model download करें, और अपने CPU की core संख्या से मेल खाते thread count के साथ `llama-server` चलाएँ।
- [ ] इस पाठ की curl request अपने चलते server के विरुद्ध भेजें, और पुष्टि करें कि आपको असली completion वापस मिलता है।
- [ ] कल: अपने चलते server को एक ही समय में दो या तीन requests भेजें और अनौपचारिक रूप से देखें कि हर एक उस समय से धीमी लगती है या नहीं जब वह अकेली चल रही request होती है।

## आगे बढ़ने के लिए

- [Repo: llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp)
- [दस्तावेज़: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
