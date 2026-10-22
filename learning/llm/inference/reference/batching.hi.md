---
title: "Batching"
description: "Static बनाम continuous batching, request scheduling, और throughput/latency का वह trade-off जिसका configuration को बचाव करना पड़ता है"
type: reference
---

# Batching

Server [KV Cache शीट](kv-cache.md) की capacity को served throughput में कैसे बदलता है। batching configuration को tune या उसका बचाव करते समय खोजने के लिए बनाया गया।

<a id="static-batching-wastes-capacity-on-uneven-finish-times"></a>

## Static batching असमान ख़त्म होने के समय पर capacity बरबाद करती है

Decode step का memory traffic (weights और हर मौजूद sequence का cache पढ़ना) ज़्यादा नहीं बदलता चाहे वह एक sequence का अगला token compute करे या कई एक साथ, इसलिए decode steps को साथ batch करना लगभग मुफ़्त throughput है। **Static batching** requests का एक निश्चित समूह बनाती है और decode steps तब तक चलाती है जब तक सबसे लंबा ख़त्म न हो जाए; जो sequence जल्दी ख़त्म होता है वह भी पूरा समूह ख़त्म होने तक एक slot घेरे रहता है और कुछ नहीं करता।

```text
total slot-steps  = batch size × steps until the longest sequence finishes
useful slot-steps = sum of each request's actual length
wasted fraction   = (total − useful) / total
```

**हल किया उदाहरण**, चार requests जिन्हें 10, 20, 30 और 100 output tokens चाहिए:

```text
total:  4 × 100 = 400 slot-steps
useful: 10 + 20 + 30 + 100 = 160 slot-steps
wasted: (400 − 160) / 400 = 60%
```

बरबादी requests की lengths के फैलाव के साथ बढ़ती है, जो सामान्य स्थिति है।

## Continuous batching batch की सीमा हटा देती है

**Continuous batching** (iteration-level scheduling) निश्चित समूह के बजाय एक अकेले decode step के स्तर पर schedule करती है: जैसे ही कोई sequence ख़त्म होता है, उसका slot मुक्त हो जाता है और अगले ही step पर इंतज़ार कर रही कोई request दाख़िल कर ली जाती है। जो लगभग स्थिर रहता है वह batch का आकार है, किसी एक request की उम्र नहीं। फ़ायदा प्रति-step computation का तेज़ होना नहीं है; वह उन sequences पर कम slot-steps खर्च होना है जिनके पास करने को कुछ बचा नहीं था।

<a id="admission-order-and-head-of-line-blocking"></a>

## दाख़िले का क्रम और head-of-line blocking

Default दाख़िला नीति **first-come, first-served (FCFS)** है: सरल, और इस अर्थ में निष्पक्ष कि कोई request किसी बाद में आई request के पीछे इंतज़ार नहीं करती। पर batch के एक step को साझा करने वाला हर sequence साथ आगे बढ़ता है, इसलिए नई request का prefill काम अगले step में दाख़िल करना तब ठीक है जब prompt छोटा हो और तब नुक़सानदेह जब वह लंबा हो: एक step में समेटा गया बड़ा prefill उस step की latency पर हावी हो जाता है, और हर दूसरा sequence, वे भी जिन्हें सिर्फ़ तेज़ decode step चाहिए, उसका इंतज़ार करता है। यही **head-of-line blocking** है: queue ठीक है, पर जो अभी चल रहा है वह नहीं। अकेला FCFS न इसे पैदा करता है न ठीक करता है; वह सिर्फ़ यह तय करता है कि कौन दाख़िल हो, यह नहीं कि उनके prefill का कितना हिस्सा एक step में आए।

**Chunked prefill** बड़े prompt के prefill को छोटे टुकड़ों में बाँटता है और उन्हें batch के चल रहे decode steps के साथ गूँथता है, इसलिए हर step नए prefill काम की सिर्फ़ सीमित मात्रा दाख़िल करता है। नई request के अपने prefill को ख़त्म होने में ज़्यादा steps लगते हैं; batch का कोई और sequence उसके इंतज़ार में नहीं रुकता। पूरी तरह process हुए prompt का अंतिम cache आकार वही रहता है, बस वहाँ पहुँचने का काम समय पर कैसे फैला है यह बदलता है।

<a id="the-throughputlatency-trade-off"></a>

## Throughput/latency का trade-off

Batch में एक और sequence जोड़ने से throughput बढ़ता है (batch भर में जोड़कर प्रति सेकंड ज़्यादा tokens बनते हैं) और प्रति-token latency भी बढ़ती है (step का हर sequence साथ आगे बढ़ता है, इसलिए बड़ा step ज़्यादा समय लेता है)। वे साथ चलते हैं, एक-दूसरे के विरुद्ध स्वतंत्र रूप से नहीं।

| दौर | अड़चन | एक और sequence जोड़ने का असर |
|---|---|---|
| छोटा batch | Memory-bandwidth bound, सादे decode जैसा | Throughput लगभग रैखिक रूप से बढ़ता है; latency मुश्किल से हिलती है |
| बड़ा batch | Compute bound | Latency साफ़ बढ़ती है; हर जोड़ा गया sequence पिछले से कम throughput ख़रीदता है |

**हल किया उदाहरण**, चार batch sizes पर benchmark किया गया stack:

| Batch size | प्रति-token latency |
|---|---|
| 8 | 15 ms |
| 32 | 25 ms |
| 64 | 45 ms |
| 128 | 90 ms |

<a id="defending-a-configuration"></a>

## Configuration का बचाव

बचाव किया जाने वाला batch size वह सबसे बड़ा है जो दोनों स्वतंत्र बाधाओं को पूरा करे, जो भी ज़्यादा कसकर बाँधे:

- **Latency budget**: inter-token latency की बताई गई ऊपरी सीमा।
- **Capacity सीमा**: KV cache की memory से निकली अधिकतम [capacity सीमा](kv-cache.md#capacity-budget), जो latency के बारे में कुछ नहीं कहती।

```text
defended batch size = min(largest batch size within the latency budget,
                          capacity ceiling)
```

**हल किया उदाहरण**, 30 ms/token का budget, ऊपर की table से:

```text
largest batch within budget: 32 (25 ms/token); 64 and 128 exceed 30 ms

capacity ceiling 100 -> defended size 32, latency budget binds
capacity ceiling 20  -> defended size 20, capacity binds instead
```

दोनों बाधाओं से काफ़ी नीचे चुना गया batch size (जैसे 8, जब 32 भी budget पूरा करता) ग़लत नहीं है, पर वह उस throughput को मेज़ पर छोड़ देता है जो budget सह सकता था।

## संबंधित

- [पाठ 4](../lessons/0004-static-vs-continuous-batching.md), [पाठ 5](../lessons/0005-request-scheduling.md), [पाठ 6](../lessons/0006-throughput-latency-tradeoff.md)
- [KV Cache शीट](kv-cache.md): वह capacity सीमा जिस पर इस शीट का बचाव-की-गई-configuration वाला formula निर्भर है
