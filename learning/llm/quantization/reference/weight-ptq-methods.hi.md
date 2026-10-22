---
title: "Weight PTQ Methods"
description: "Round-to-nearest, GPTQ और AWQ साथ-साथ, और calibration set क्या करता है"
type: reference
---

# Weight PTQ Methods: Round-to-Nearest, GPTQ और AWQ की तुलना

चरण 4 का संक्षेप, देखने के लिए। [पाठ 9](../lessons/0009-round-to-nearest.md) round-to-nearest (RTN) बताता है, [पाठ 10](../lessons/0010-gptq.md) GPTQ, [पाठ 11](../lessons/0011-awq.md) AWQ, और [पाठ 12](../lessons/0012-the-calibration-set.md) calibration set।

## तीनों methods साथ-साथ

| | Round-to-nearest | GPTQ | AWQ |
|---|---|---|---|
| विचार | हर weight को उसके सबसे नज़दीकी level पर round करें | Columns को क्रम से round करें, हर error को उन columns पर धकेलें जो अभी round नहीं हुए | Round करने से पहले अहम input channels को scale से बढ़ाएँ, activation को उसी scale से भाग दें |
| Data से क्या पढ़ता है | कुछ नहीं | Layer के inputs, जिनका योग `H = 2 X X^T` बनता है | प्रति channel औसत activation magnitude, और हर `alpha` को आँकने के लिए layer के outputs |
| Weight values बदलता है | नहीं | हाँ, हर round के बाद बाद के सभी columns | हाँ, प्रति-channel scale `s = s_X^alpha` से, फिर nearest पर round करता है |
| Objective | हर weight की अपनी error | हर layer पर `argmin \|\| W X - Ŵ X \|\|^2` | वही layer-output error, `alpha` पर [0, 1] में search की गई |
| Backpropagation | नहीं | नहीं | नहीं |
| लागत | नगण्य | 175B parameters के लिए लगभग 4 GPU घंटे (पेपर) | हर layer पर `alpha` के 20 values का grid (पेपर) |
| Grid | हर row या group पर एक scale | Loop से पहले तय; group का scale तब तय होता है जब loop उस group पर पहुँचता है | Per-group, पेपर में 128 |
| मुख्य जोखिम | Per-row scales के साथ 3 bits पर ढह जाता है | छोटे या बेमेल calibration set पर overfit होता है | बहुत ज़ोर से scale करने से गैर-अहम channels को नुक़सान होता है |

## हर एक संख्याओं पर क्या करता है

| WikiText-2 perplexity | 16-bit | RTN | GPTQ | AWQ |
|---|---|---|---|---|
| OPT-175B, 4 bits, per-row grid | 8.34 | 10.54 | 8.37 | वहाँ रिपोर्ट नहीं |
| OPT-175B, 3 bits, per-row grid | 8.34 | 7,300 | 8.68 | वहाँ रिपोर्ट नहीं |
| Llama-2 7B, 4 bits, 128 के groups | 5.47 | 5.73 | 5.69 | 5.60 |
| Llama-2 7B, 3 bits, 128 के groups | 5.47 | 6.66 | 6.43 | 6.24 |

पहली दो पंक्तियाँ GPTQ के पेपर से हैं और आख़िरी दो AWQ के पेपर से। Grids और models अलग हैं, इसलिए एक पंक्ति के भीतर तुलना करें और पंक्तियों के बीच आकार देखें, संख्याएँ आर-पार नहीं। हर पेपर अपने method को दूसरे के मुक़ाबले परखता है, इसलिए फ़र्क़ को लेखकों के runs की तरह पढ़ें।

## Error ऐसा बर्ताव क्यों करती है

| तथ्य | नतीजा |
|---|---|
| हटाया गया हर bit step को लगभग दोगुना कर देता है | Round-to-nearest की error हर bit पर लगभग दोगुनी होती है |
| पाठ 9 के खिलौने में error के अनुपात step के अनुपात के बराबर हैं: 8 से 4 bits पर 127 / 7 = 18.1, 4 से 3 पर 7 / 3 = 2.3 | आख़िरी bits सबसे महँगे हैं |
| Round-to-nearest हर weight की error घटाता है, layer के output की error नहीं | सहसंबद्ध खिलौना layer पर 2000 में से 919 random roundings इससे बेहतर निकलीं |
| GPTQ का फ़ायदा सहसंबद्ध inputs से आता है | स्वतंत्र inputs के साथ यह लगभग ग़ायब हो जाता है (खिलौने में 0.2680 बनाम 0.2595) |
| अहम weight उसकी activation से चुना जाता है, उसके आकार से नहीं | OPT-6.7B पर 3 bits पर 1% activation से चुनने पर 11.39, weight के आकार से 22.37, सादा round-to-nearest 23.54 |
| Channel को `s` से scale करने पर उसकी सापेक्ष error लगभग `1 / s` घटती है | बहुत बड़ा `s` group के बाक़ी channels का step बढ़ा देता है |

## GPTQ के तीन scaling बदलाव और act-order

| बदलाव | क्या ठीक करता है |
|---|---|
| हर row के लिए columns का वही क्रम | हर column के लिए एक inverse update सभी rows के काम आता है |
| Lazy batch updates, एक बार में 128 columns | Update memory-bound है, इसलिए batch करने से GPU काम में आता है |
| Diagonal के औसत का 1% dampening, साथ में Cholesky factor | संख्यात्मक error जो inverse को indefinite बना सकती है |
| Act-order (लेखकों का code, पेपर नहीं): columns `H` के diagonal के हिसाब से, सबसे बड़ा पहले | OPT-66B 3 bits पर जैसे बुरे नतीजे ठीक करता है (14.16 से 9.95); static groups न हों तो inference में बदलाव चाहिए हो सकते हैं |

## Calibration set क्या करता है

| | GPTQ | AWQ |
|---|---|---|
| सामान्य आकार | पेपर: C4 से 2048 tokens के 128 segments | AWQ 16 sequences पर OPT-6.7B, 3 bits में GPTQ को 192 पर हराता है (लेखकों का run) |
| llm-compressor | 128 से 512 samples आम हैं, 128 से 256 से शुरू करें | वही सलाह; इसका उदाहरण 256 इस्तेमाल करता है |
| ज़्यादा data क्यों चाहिए | यह features के सह-विचरण का पूरा matrix आँकता है | यह प्रति channel एक औसत आँकता है |
| बेमेल का दंड, OPT-6.7B, 3 bits (AWQ पेपर) | perplexity 2.3 से 4.9 ख़राब | 0.5 से 0.6 ख़राब |

- Round-to-nearest data-free है। GPTQ और AWQ को calibration set चाहिए। दोनों में से कोई उसमें से backpropagate नहीं करता।
- Calibration set training data नहीं है, और उसका domain नतीजे में दिखता है।
- Set को लक्ष्य उपयोग से मिलाएँ: सामान्य model के लिए सामान्य text, instruction model के लिए instruction data, coding model के लिए code (llm-compressor)।
- Calibration domain के रोके हुए text पर, और आप जिन दूसरे domains को serve करते हैं उनके text पर evaluate करें। एक में फ़ायदा और दूसरे में नुक़सान बेमेल है।
- जिस text से set लिया गया उसी पर मापी गई perplexity बढ़ा-चढ़ाकर दिखती है। GPTQ का पेपर इसी वजह से कहता है कि उसके C4 नतीजे पूरी तरह zero-shot नहीं हैं।
- पाठ 12 के खिलौने में बहुत कम samples (128 features के लिए 64) ने GPTQ को in-domain भी round-to-nearest से बदतर बना दिया।

## Weight-PTQ checkpoint पर भरोसा करने से पहले

- कौन-सा method, कौन-सी bit width, और कौन-सा group size या grid।
- कौन-सा calibration set, कितने samples, और कितने लंबे। अगर model card नहीं बताता, तो यह कमी है।
- क्या बताई गई perplexity calibration domain पर है।
- क्या उसी grid पर एक data-free baseline उसी evaluation पर मापा गया।
- Act-order और groups वाले GPTQ के लिए, क्या उसे inference में बदलाव चाहिए जो speed की क़ीमत ले सकते हैं, या वह static groups से बना था।
