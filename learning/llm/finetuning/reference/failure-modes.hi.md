---
title: "Failure Modes"
description: "लक्षण से कारण तक, और चुपचाप होने वाली विफलताएँ"
type: reference
---

# Failure Modes

Diagnosis की शीट। run के दौरान इसे खुला रखें।

## किसी भी चीज़ से पहले चार जाँचें

```python
# 1. Did the adapter attach?
model.print_trainable_parameters()          # compare to your arithmetic

# 2. Is the data what you think?
print(repr(tokenizer.decode(ds[0]["input_ids"])))
print(sum(1 for l in ds[0]["labels"] if l != -100), "of", len(ds[0]["labels"]), "scored")

# 3. Does loss move?                        # logging_steps=1 over 50 steps

# 4. Can it overfit two examples?           # loss → ~0 in 100 steps, or the pipeline is broken
```

जाँच 2 एक ही बार पढ़ने में template mismatch, गुम end-of-turn tokens, masking की गड़बड़ियाँ और truncation पकड़ लेती है। यह पूरी प्रक्रिया के सबसे क़ीमती दस सेकंड हैं।

## लक्षण → कारण

![Loss बनाम steps के छह रेखाचित्र: step 1 से सपाट, एक गिरावट जो शून्य से काफ़ी ऊपर रुक जाती है, train और held-out curves का अलग होना जिनमें held-out वापस ऊपर मुड़ता है, सपाट runs और तीखी गिरावटों की सीढ़ी, एक spike से टूटी हुई गिरावट, और एक गिरावट जो अचानक NaN पर ख़त्म होती है।](images/loss-curve-shapes.svg)

नीचे की पहली ग्यारह पंक्तियाँ किसी घटना के बजाय एक curve का नाम लेती हैं, और उनमें से कई एक ही आकार साझा करती हैं: तीन कहती हैं सपाट, दो कहती हैं मुश्किल से हिलता है। रेखाचित्र से मिलान करें, फिर उस आकार का नाम लेने वाली हर पंक्ति पढ़ें, क्योंकि एक आकार के एक से ज़्यादा कारण हो सकते हैं। बारहवीं पंक्ति से लक्षण कहीं और देखा गया है, किसी output, load error या regression suite में, और मिलान करने के लिए कोई curve नहीं है।

| लक्षण | संभावित कारण | जाँच |
|---|---|---|
| Loss step 1 से बिल्कुल सपाट | Adapter किसी से मेल नहीं खाया | `print_trainable_parameters()` |
| Loss step 1 से बिल्कुल सपाट | सारे labels `-100` | Scored positions गिनें |
| Loss step 1 से बिल्कुल सपाट | LR कई परिमाण-क्रम बहुत कम | ~`1e-4` होना चाहिए |
| Loss मुश्किल से हिलता है | इस architecture के लिए target module के नाम ग़लत | `named_modules()` |
| Loss मुश्किल से हिलता है | `α/r` अनजाने में बहुत छोटा | `r` बढ़ाया, `α` भूल गए |
| Loss ऊँचाई पर थम जाता है | Capacity की छत | ज़्यादा rank या ज़्यादा targets, ज़्यादा epochs नहीं |
| Held-out बढ़ता है, train घटता है | Overfitting | Held-out का न्यूनतम वाला ship करें |
| Train तेज़ी से → 0, held-out तुरंत बढ़ता है | Capacity के हिसाब से dataset बहुत छोटा | ज़्यादा data, कम capacity |
| Epoch की सीमाओं पर loss सीढ़ी बनाता है | Memorisation | कम epochs |
| Loss spike करके लौट आता है | एक विकृत batch | बाहरी example ढूँढें |
| Loss → `NaN` | Overflow, या ख़राब data | bf16 चुनें; LR घटाएँ; warm-up जोड़ें |
| Held-out संदिग्ध रूप से अच्छा | Split के आर-पार contamination | Train बनाम test का dedup करें, सबसे ज़्यादा similarity वाले जोड़े पढ़ें |
| Model कभी generate करना बंद नहीं करता | Training data में end-of-turn token नहीं | कोई example decode करें |
| Output माँगा गया format अनदेखा करता है | Train बनाम serve में template mismatch | `repr` से तुलना करें |
| उत्तर वाक्य के बीच में कट जाते हैं | `max_length` targets को छाँट रहा है | Length का वितरण जाँचें |
| ऐसे सवालों के जवाब जो पूछे नहीं गए | Packing ने loss masking या सीमाएँ तोड़ दीं | जाँचें कि packing के बाद भी `-100` बचा रहता है |
| असंबंधित चीज़ों में बदतर | Catastrophic forgetting | Stored baseline के सामने regression suite |
| अब उसे मना नहीं करता जिसे base मना करता था | Safety regression | **Ship रोक देता है** |
| Merged ≠ unmerged output | Merge की गड़बड़ी, या sampling चालू थी | Greedy तरीक़े से दोबारा जाँचें |
| Merged model बिगड़ गया | Quantized base में merge किया | Full precision में merge करें, फिर quantise करें |
| Adapter load नहीं होता | ग़लत base model या revision | Adapter एक diff है; उसे ठीक उसका base चाहिए |
| 4-bit base पर gradient errors | `prepare_model_for_kbit_training` छोड़ दिया | इसे जोड़ें |
| Eval बढ़िया, production ख़राब | Train/serve distribution mismatch | साफ़ नहीं, असली inputs पर train करें |
| Rerun पर नतीजा ग़ायब | Seed noise, कभी असली असर नहीं | कई seeds, paired comparison |

## चुपचाप होने वाली विफलताएँ: कोई error नहीं, नतीजा ग़लत

ख़तरनाक समूह। कुछ raise नहीं होता, सब ठीक दिखता है।

1. Training और serving के बीच **Template mismatch**।
2. **गुम end-of-turn token।** ठीक से train होता है, कभी रुकता नहीं।
3. **Loss masking ग़लत।** अनजाने में prompts पर training।
4. **Contamination।** Held-out memorisation मापता है, generalisation बताता है।
5. **Group या temporal leakage।** ग़लत key से split किया।
6. **Catastrophic forgetting।** आप जो भी संख्या देख रहे हैं वह सुधरती है।
7. **Adapter किसी से नहीं जुड़ा।** Train होता है, loss log करता है, सीखता कुछ नहीं।
8. **जो ship करते हैं उससे अलग artifact का evaluation**, जैसे bf16 में eval और 4-bit में deploy।

ऊपर हर एक के लिए पहचान का एक ख़ास चरण है। कोई भी अपना ऐलान नहीं करता।

## Forgetting घटाना

सबसे सस्ता पहले:

1. कम steps, या पहले का checkpoint
2. कम learning rate
3. कम rank, या कम target modules
4. Training में कुछ प्रतिशत सामान्य instruction data मिलाएँ
5. **Adapter को unmerged रखें और route करें**, ताकि base अक्षत रहे और forgetting का मायने ही न रहे

## तुलना की सफ़ाई

- एक बार में एक चर; seed, data और split स्थिर रखें
- कई seeds, क्योंकि variance अक्सर असर से बड़ा होता है
- एक ही examples पर paired comparison
- `n` और एक अंतराल बताएँ, कभी अकेली संख्या नहीं
- हर बार असली generations पढ़ें, विफलताओं समेत

## हर run में क्या दर्ज करें

Base model **और revision** · adapter config हू-ब-हू · dataset और सटीक split · seed · effective batch size · LR और schedule · steps · चुना गया checkpoint और उसे सही ठहराने वाली संख्या · library versions · eval और regression नतीजे।

## संबंधित

- [पाठ 11](../lessons/0011-your-first-adapter.md), [पाठ 12](../lessons/0012-reading-a-training-run.md), [पाठ 22](../lessons/0022-contamination-and-held-out-design.md), [पाठ 24](../lessons/0024-the-regression-suite.md)
