---
title: "Number Formats"
description: "हर format का bit layout, range और precision, और memory का हिसाब"
type: reference
---

# Number Formats: Layout, Range, Precision और Memory

चरण 1 का संक्षेप, देखने के लिए। [पाठ 1](../lessons/0001-what-quantization-buys.md) बताता है कि quantization से क्या मिलता है और memory का हिसाब, [पाठ 2](../lessons/0002-floating-point-formats.md) floating-point formats fp32, fp16 और bf16, और [पाठ 3](../lessons/0003-low-bit-formats.md) fp8, int8, int4 और block-scaled formats।

## Floating-point layout पढ़ना

```text
value = (-1)^sign × 2^(e - bias) × (1 + m / 2^M)
```

- `e` exponent field है, `m` mantissa field, और `M` mantissa bits की संख्या।
- Exponent field सब शून्य: शून्य और subnormal values, `(m / 2^M) × 2^(1 - bias)`।
- Exponent field सब एक: IEEE formats में infinity और NaN। E4M3 अपवाद है और इसे सामान्य values के लिए इस्तेमाल करता है।
- Exponent bits range तय करते हैं। Mantissa bits precision तय करते हैं। Machine epsilon `2^-M` है।
- `2^k` और `2^(k+1)` के बीच पास-पास की values `2^(k-M)` की दूरी पर होती हैं: यह दूरी हर दो की घात पर दोगुनी हो जाती है।

## Floating-point formats

|Format|Bits|Sign / exponent / mantissa|Bias|सबसे बड़ी finite value|सबसे छोटी normal value|Machine epsilon|
|---|---|---|---|---|---|---|
|fp32|32|1 / 8 / 23|127|3.4 × 10^38|1.2 × 10^-38|2^-23, लगभग 1.2 × 10^-7|
|fp16|16|1 / 5 / 10|15|65,504|6.1 × 10^-5|2^-10, लगभग 9.8 × 10^-4|
|bf16|16|1 / 8 / 7|127|3.4 × 10^38|1.2 × 10^-38|2^-7, लगभग 7.8 × 10^-3|
|fp8 E4M3|8|1 / 4 / 3|7|448|2^-6|2^-3|
|fp8 E5M2|8|1 / 5 / 2|15|57,344|2^-14|2^-2|
|FP4 E2M1|4|1 / 2 / 1|1|6|1|2^-1|

- fp16 की सबसे छोटी subnormal `2^-24` है। इससे छोटी values शून्य हो जाती हैं।
- E4M3 की सबसे छोटी subnormal `2^-9` है, E5M2 की `2^-16`।
- E4M3 में infinities नहीं हैं और NaN का एक ही pattern है (S.1111.111)। E5M2 IEEE का पालन करता है, infinities और NaNs के साथ।
- bf16 वह fp32 है जिसके निचले 16 bits हटा दिए गए हैं।
- E4M3, E5M2 और fp16 की पंक्तियाँ पाठों के स्रोतों से हैं। FP4 E2M1 की पंक्ति उसके layout और पाठ 3 में इस्तेमाल हुए bias 1 से निकाली गई है। fp8 और FP4 पंक्तियों का machine epsilon भी उसी नियम से `2^-M` है।

## कौन-सा format किस काम के लिए

|Format|कहाँ दिखता है|क्यों|
|---|---|---|
|fp32|Baseline, और mixed precision में accumulation|चौड़ी range और महीन spacing, 4 bytes|
|fp16|Loss scaling के साथ mixed-precision training|महीन spacing, संकरी range: training को loss scaling चाहिए|
|bf16|Loss scaling के बिना training|fp32 जैसी range, इसलिए loss scaling नहीं, मोटा mantissa|
|E4M3|Weights और activations|महीन spacing, range 448 तक|
|E5M2|Gradients|चौड़ी range, मोटी spacing|

## Integer grids

|Format|Levels|Range|Spacing|
|---|---|---|---|
|int8|256|-128 से 127|हर जगह 1|
|int4|16|-8 से 7|हर जगह 1|

- Values `scale × integer` होती हैं। Scale के बिना integer grid में सिर्फ़ पूर्ण संख्याएँ आती हैं।
- Float grid अपनी range ख़ुद लाता है और उसे जगह देने के लिए scale चाहिए। Integer grid को पूरी range scale से मिलती है।
- आधे step से छोटी values शून्य पर round हो जाती हैं, scale हो या न हो।

## Block-scaled formats

|Format|Block size|Scale|Element|Element bits|प्रति weight effective bits|
|---|---|---|---|---|---|
|MXFP8|32|E8M0|E4M3 या E5M2|8|8.25|
|MXFP6|32|E8M0|E2M3 या E3M2|6|6.25|
|MXFP4|32|E8M0|E2M1|4|4.25|
|MXINT8|32|E8M0|int8|8|8.25|
|NVFP4|16|E4M3, साथ में प्रति tensor एक FP32 scale|E2M1|4|4.5, प्रति tensor scalar को छोड़कर|

- हर element की value `X × P` है: साझा scale गुणा store किया हुआ element।
- E8M0 सिर्फ़ exponent है, इसलिए MX scale हमेशा दो की घात होता है। NVFP4 में E4M3 scale भिन्नात्मक गुणक हो सकता है।
- E2M1 की धनात्मक values: 0, 0.5, 1, 1.5, 2, 3, 4, 6।
- Block में एक बड़ी value पूरे block का scale तय कर देती है और अपने पड़ोसियों को शून्य पर round करा सकती है।
- NVFP4 के ब्योरे NVIDIA के अपने blog post से हैं, जो vendor का दस्तावेज़ है।

## Memory का हिसाब

GB में weight memory है `parameters in billions × effective bits per weight / 8`। प्रति weight effective bits का मतलब bit width में scale bits को group या block size से भाग देकर जोड़ना।

|Format|Effective bits|8B model|70B model|
|---|---|---|---|
|fp32|32|32 GB|280 GB|
|fp16 या bf16|16|16 GB|140 GB|
|fp8 या int8|8|8 GB|70 GB|
|MXFP4|4.25|4.25 GB|लगभग 37.2 GB|
|NVFP4|4.5|4.5 GB|लगभग 39.4 GB|
|int4, हर 128 पर 16-bit scale|4.125|4.125 GB|लगभग 36.1 GB|
|int4, हर 32 पर 16-bit scale|4.5|4.5 GB|लगभग 39.4 GB|

- ये सिर्फ़ weights हैं। KV cache और activations इसके ऊपर आते हैं।
- Scale का overhead: `scale bits / group size`। हर 128 weights पर 16-bit scale 0.125 bits जोड़ता है, और हर 32 पर 0.5 bits।
