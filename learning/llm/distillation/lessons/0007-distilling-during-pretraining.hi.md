---
title: "7. Pretraining के दौरान Distillation"
description: "Gemma 2 और Minitron ने बड़े पैमाने पर teacher के distribution को training signal कैसे बनाया, और logits सहेजने में क्या लागत आती है"
type: lesson
---

# पाठ 7. Pretraining के दौरान Distillation

**मिशन से संबंध:** मिशन आपसे माँगता है कि आप token-level loss लिखें और बताएँ कि उसे कब इस्तेमाल नहीं किया जा सकता, और यह पाठ उस loss को दो असली model परिवारों के training signal के रूप में दिखाता है, teacher के distributions रखने की लागत को bytes में गिनकर।
**मुख्य स्रोत:** [पेपर: "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
**पूर्व-आवश्यकताएँ:** [पाठ 6](0006-the-tokenizer-constraint.md), [Token-level distillation](../GLOSSARY.md), [Logit](../GLOSSARY.md), [Top-k logits](../GLOSSARY.md)

## वार्म-अप

1. ▢ Qwen teacher के साथ Llama student सादे token-level loss को नामुमकिन क्यों कर देता है, तब भी जब दोनों पूरे logits देते हों?

<details markdown="1"><summary>जाँचें</summary>

Loss student की पंक्ति की probability i की तुलना teacher की probability i से करता है, और अलग tokenizers index i को अलग token बना देते हैं, संभवतः अलग आकारों और positions के साथ। चरण 2 के उपाय हैं: cross-tokenizer loss, या teacher के परिवार से student।

</details>

2. ▢ Mode-covering student KL की कौन-सी दिशा को कम करता है, और Minitron ने किस सेटिंग में उसे सबसे अच्छा पाया?

<details markdown="1"><summary>जाँचें</summary>

[Forward KL](../GLOSSARY.md)। Minitron ने prune किए base models को दोबारा train करते समय उसे reverse KL से बेहतर पाया, depth-pruned Minitron 8B के लिए 2.155 बनाम 2.665 के LM loss के साथ (उनके पेपर की Table 16)। यह एक सेटिंग है, और पाठ 5 दूसरी दिशा के लिए instruction-tuning का सबूत देता है।

</details>

## यह जानें

यह पाठ दो training विधियों का distillation वाला आधा हिस्सा सिखाता है। Pretraining run data से hardware तक कैसे संगठित होता है, वह [Pretraining ट्रैक](../../pretraining/) का विषय है, और pruning एक विधि के रूप में किसी का नहीं।

### Pretraining के objective के रूप में Distillation: Gemma 2

Gemma 2 की report अपने 2B और 9B models को next token prediction की जगह knowledge distillation से train करती है। प्रेरणा यह है कि next-token training data के साथ सिर्फ़ logarithmic रूप से scale होती है, और छोटे models को बेहतर होने के लिए बहुत लंबे runs चाहिए। Distillation हर token पर one-hot vector की जगह बड़े model के next tokens का distribution रख देता है, जो report के अनुसार ज़्यादा समृद्ध gradients देता है। उसका बताया उद्देश्य है कि distillation के साथ बहुत बड़ी संख्या में tokens पर train करके उपलब्ध tokens की संख्या से आगे की training का अनुकरण किया जाए (introduction)।

Report जो तथ्य देती है:

- 2B model 2 trillion tokens पर train हुआ, 9B 8 trillion पर, और 27B 13 trillion पर (section 3.1)। 27B को शून्य से train किया गया, distillation के बिना।
- 2B और 9B के token counts, Hoffmann et al. द्वारा अनुमानित compute-optimal मात्रा से 50 गुना से ज़्यादा हैं (introduction)।
- Loss, हर token की उसके context में teacher की probability और student की probability के बीच negative log-likelihood है, जिसे student पर कम किया जाता है: -P_T(x | x_c) log P_S(x | x_c) का योग (section 3.2)। यह पाठ 4 का loss temperature 1 पर है।
- Vocabulary में 256,128 entries हैं (Table 1), जो Gemini से विरासत में मिली हैं, और context length 8,192 tokens है (section 2)।

इसके ablations 7B teacher इस्तेमाल करते हैं, अंतिम वाला नहीं। 500B tokens पर train हुआ 2B student, जो report के अनुसार 2B के लिए compute-optimal संख्या का 10 गुना है, तीन benchmarks पर शून्य से train होने पर औसतन 60.3 और distilled होने पर 67.7 score करता है (Table 6)। Teacher को 7B पर तय रखकर, 200M, 400M और 1B parameters पर validation perplexity शून्य से train होने पर 23, 19 और 17 थी और distilled होने पर 21, 17 और 15 (Table 7)। Report यह भी कहती है कि 2T tokens वाला नया 2B, 3T tokens वाले Gemma 1 के 2B से काफ़ी सुधरा है (section 6.1)। ये Google की अपनी तुलनाएँ हैं।

### Report क्या नहीं कहती

Report अंतिम 2B और 9B models के teacher का नाम नहीं बताती और न उसका आकार। वह यह नहीं बताती कि teacher का distribution student को कैसे दिया गया: सहेजा गया, training के साथ compute हुआ, या अनुमानित। Gemma 2 में sampled या truncated top-k के बारे में कथन report में नहीं हैं। अगला भाग गणना करता है कि हर विकल्प की क्या लागत है, ताकि आप चुनाव के स्रोत के बिना भी इस पर तर्क कर सकें।

### Teacher को सहेजने की क्या लागत है

हर training token के लिए vocabulary पर एक distribution बड़ा होता है। Script Gemma 2 की vocabulary और token counts इस्तेमाल करती है, और इस पाठ की दो मान्यताएँ: 2 bytes पर bf16 probabilities, और truncated संस्करण के लिए 4-byte token index के साथ k का एक उदाहरणात्मक मान 256।

```python
vocab = 256_128            # Gemma 2 vocabulary size (Table 1 of the report)
tokens = {"2B run": 2e12, "9B run": 8e12}

full = vocab * 2           # bf16: 2 bytes per probability
k = 256                    # an illustrative k, not a number from any paper
topk = k * (2 + 4)         # 2-byte probability + 4-byte token index

print("full per token: %d bytes" % full)
print("top-%d per token: %d bytes (%.1fx smaller)" % (k, topk, full / topk))
print("full per 8192-token sequence: %.2f GB" % (full * 8192 / 1e9))
for name, n in tokens.items():
    print(name, "full: %.2f EB" % (full * n / 1e18), " top-%d: %.2f PB" % (k, topk * n / 1e15))
```

चलाने से पहले 2B run के पूरे-distribution वाली लागत के परिमाण-क्रम का अनुमान लगाएँ। Output:

```text
full per token: 512256 bytes
top-256 per token: 1536 bytes (333.5x smaller)
full per 8192-token sequence: 4.20 GB
2B run full: 1.02 EB  top-256: 3.07 PB
9B run full: 4.10 EB  top-256: 12.29 PB
```

2B run के लिए पूरे distributions सहेजना लगभग एक exabyte है, और 9B run के लिए लगभग चार। हर token पर 256 entries रखने से यह 333.5 के factor से घटकर petabytes में आ जाता है, और यह आँकड़ा training tokens को एक बार गिनता है, बिना epochs दोहराए। Truncation की भी क़ीमत है। जो tail mass छोड़ दिया गया उसे सँभालना पड़ता है, renormalize करके या एक bucket मानकर, और वह चुनाव target बदल देता है।

एक विकल्प है जो कुछ नहीं सहेजता: teacher को student के साथ चलाएँ और उसका distribution forward pass से पढ़ें। Minitron वही रास्ता लेता है, और ध्यान दिलाता है कि distillation teacher पर अतिरिक्त forward pass का overhead जोड़ता है, इसलिए वे अपने distilled और conventional runs की तुलना बराबर compute पर करते हैं (section 4)। किसी lab ने कौन-सा रास्ता लिया, यह इस पाठ का दावा नहीं है।

Minitron के लेखकों ने truncation को भी सीधे परखा। Distillation पर उनके appendix (A.3) में, K को 100 तक रखकर सिर्फ़ शीर्ष K teacher और student logits रखने से accuracy में उल्लेखनीय गिरावट आई। बड़े K के लिए गिरावट ग़ायब हो गई, पर नतीजे truncate न करने से बेहतर नहीं थे। यह एक pruned-model को दोबारा train करने की setup है, और जिस K पर truncation नुक़सान करना बंद करता है वह vocabulary और model के अनुसार अलग होगा।

### Pruning और distillation: Minitron

Minitron (Muralidharan et al., 2024) Nemotron-4 15B को prune करके और मूल model को teacher बनाकर दोबारा train करके accuracy लौटाते हुए उसे संकुचित करता है। उसका student एक pruned नक़ल के रूप में शुरू होता है, इसलिए निर्माण से ही teacher का tokenizer साझा करता है। यह पाठ सिर्फ़ distillation वाला आधा हिस्सा लेता है।

- **Tokens.** Minitron 8B और 4B models को हर एक को 94 billion tokens पर दोबारा train किया गया। पेपर Minitron 8B की तुलना Nemotron-3 8B से करता है, जो 3.8 trillion पर train हुआ था, और बचत को 40 गुना कम tokens बताता है (Table 2)।
- **Distillation बनाम सामान्य retraining.** 4B model के लिए वे बराबर compute पर तुलना करते हैं (Table 11)। 150B tokens पर शून्य से training ने HellaSwag 46.22 और MMLU 24.36 दिया। 15B को 4B तक prune करके 150B पर सामान्य तरीक़े से दोबारा train करने से 50.85 और 24.57 मिले। 100B tokens पर distillation के साथ prune और दोबारा train करने से 51.04 और 37.81 मिले। Distilled run 150B के बजाय 100B tokens इस्तेमाल करता है क्योंकि teacher का अतिरिक्त forward pass है। यह शून्य से training की तुलना में HellaSwag पर 4.8 अंक और MMLU पर 13.5 का फ़ायदा है।
- **Loss.** Logits पर forward KL, temperature 1 पर, जिसमें अकेला logit loss, language modeling loss के साथ भारित मिश्रण से बेहतर है, और top K तक truncate करने से कोई फ़ायदा नहीं (section 4 और appendix A.3)।

अगला पेपर (Sreenivas et al., 2024) यह विधि Llama 3.1 8B और Mistral NeMo 12B पर लागू करता है। वह distillation से पहले एक चरण जोड़ता है: teacher correction। जब मूल pretraining data उपलब्ध नहीं होता, तो teacher अलग dataset पर घटिया मार्गदर्शन देता है, जिसका कारण लेखक sub-word tokens के distribution में बदलाव को बताते हैं। इसलिए वे पहले teacher को distillation data के लगभग 100B tokens पर fine-tune करते हैं, warm-up और कम learning rates के साथ। फिर वे सिर्फ़ logits पर forward KL के साथ prune और distil करते हैं। Llama-3.1-Minitron 4B को 94B tokens पर और MN-Minitron-8B को 380B पर दोबारा train किया गया (Table 4)। पेपर कहता है कि 4B, Llama 3.1 8B से 150 गुना कम tokens, 94B बनाम 15T, के साथ अच्छी तुलना करता है, और 8B, Llama 3.1 8B से 40 गुना कम, 380B बनाम 15T, के साथ बेहतर करता है (section 5.1)। ये NVIDIA की अपने evaluation पर तुलनाएँ हैं।

## अभ्यास

1. ▢ Report में, Gemma 2 के कौन-से models distillation से train हुए, और हर एक ने कितने tokens देखे?

    - a) 8T पर 2B और 2T पर 27B
    - b) 8T पर 9B और 13T पर 27B
    - c) तीनों models हर एक 13T tokens पर train हुए
    - d) 2T पर 2B और 8T पर 9B

<details markdown="1"><summary>जाँचें</summary>

**d)** 27B को शून्य से 13T tokens पर train किया गया, इसलिए (b) और (c) ग़लती से उसे शामिल करते हैं। विकल्प (a) token counts की अदला-बदली करता है। Report गिनतियाँ section 3.1 में बताती है।

</details>

2. ▢ 256,128 की vocabulary और प्रति probability 2 bytes के साथ, एक पूरा next-token distribution कितने bytes लेता है, और एक 8,192-token sequence के लिए वह कितने gigabytes बनता है?

<details markdown="1"><summary>संकेत</summary>

Vocabulary को प्रति entry bytes से गुणा करें, फिर sequence की लंबाई से, फिर एक अरब से भाग दें।

</details>

<details markdown="1"><summary>जाँचें</summary>

256,128 गुणा 2 है प्रति token 512,256 bytes। गुणा 8,192 करने पर 4,196,401,152 bytes मिलते हैं, एक sequence के लिए लगभग 4.20 GB। एक training run में ऐसे कई लाखों sequences होते हैं, इसीलिए सहेजने बनाम दोबारा compute करने का सवाल मौजूद है।

</details>

3. ▢ शीर्ष 256 entries रखने पर, हर एक 2-byte probability और 4-byte index के साथ, एक token का record कितना बड़ा है, और वह पूरे distribution से कितना छोटा है?

<details markdown="1"><summary>जाँचें</summary>

256 गुणा 6 है 1,536 bytes, जो 512,256 से 333.5 गुना छोटा है। 256 का k और byte आकार इस पाठ की मान्यताएँ हैं, Gemma 2 के आँकड़े नहीं। Record distribution की tail को भी छोड़ देता है, जिसे renormalize या bucket करना पड़ता है, और वह चुनाव target बदल देता है।

</details>

4. ▢ एक forum post कहती है कि Gemma 2 को सहेजे गए top-256 teacher distribution पर train किया गया। आप उस दावे का क्या करते हैं?

<details markdown="1"><summary>जाँचें</summary>

उसे report में ढूँढें। Report loss, token counts और ablations बताती है, और यह नहीं बताती कि distribution कैसे दिया गया। इसलिए दावा report से असत्यापित है। उसे असमर्थित मानें, लिख लें कि क्या ग़ायब है, और उस पर भरोसा करने से पहले लेखकों के text जैसा कोई मुख्य स्रोत खोजें।

</details>

5. ▢ Minitron की Table 11 में, pruning के साथ सामान्य retraining MMLU 24.57 तक पहुँची और pruning के साथ distillation 37.81 तक, distillation कम tokens पर। Token counts 150B और 100B क्यों हैं, और तालिका की सीमा क्या है?

<details markdown="1"><summary>जाँचें</summary>

वे बराबर compute पर तुलना करते हैं, और distillation अपने बजट का कुछ हिस्सा teacher के forward pass पर ख़र्च करता है, इसलिए उसे 150B के मुक़ाबले 100B tokens मिलते हैं। तालिका Nemotron-4 15B से prune किया गया एक 4B model है। लेखक इसे यह दिखाने के लिए इस्तेमाल करते हैं कि pruning के बाद distillation सामान्य retraining को हराता है। यह दूसरे teachers, आकारों या benchmarks के लिए फ़ायदा नहीं दिखाती।

</details>

6. ▢ अगले Minitron पेपर में teacher correction, distil करने से पहले teacher को लगभग 100B tokens पर fine-tune करता है। यह कब ज़रूरी है, और छोड़ने पर लेखक किसे दोष देते हैं?

<details markdown="1"><summary>जाँचें</summary>

यह तब ज़रूरी है जब teacher का मूल pretraining data उपलब्ध न हो, इसलिए distillation data का distribution अलग है। लेखक कहते हैं कि तब teacher घटिया मार्गदर्शन देता है, और अनुमान लगाते हैं कि कारण यह है कि teacher के मूल data और distil करने के लिए इस्तेमाल हुए data के बीच sub-word tokens का distribution अलग है। यह व्याख्या उनकी परिकल्पना है।

</details>

## असली दुनिया का अभ्यास

- [ ] Storage script को अपनी vocabulary आकार के साथ और k को 64 और 1,024 रखकर चलाएँ, और तीनों लागत अनुपात लिख लें।
- [ ] Minitron पेपर की Table 11 खोलें और iso-compute चिह्न ढूँढें। लिखें कि किस पंक्ति ने teacher इस्तेमाल किया और उसने कितने tokens देखे।
- [ ] कल: बिना नोट्स के Gemma 2 के तीनों token counts और एक token का storage गणित बताएँ, फिर बताएँ कि report teacher के बारे में क्या अनकहा छोड़ती है।

## आगे बढ़ने के लिए

- [Distillation Losses शीट](../reference/distillation-losses.md)
- [पेपर: "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
- [पेपर: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [पेपर: "LLM Pruning and Distillation in Practice: The Minitron Approach", Sreenivas et al., 2024](https://arxiv.org/abs/2408.11796)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
