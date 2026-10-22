---
title: "25. Distillation के दावे की समीक्षा"
description: "\"हमारा छोटा model बड़े के बराबर है\" की समीक्षा यह बताकर करना कि माप ने क्या छिपाया"
type: lesson
---

# पाठ 25. Distillation के दावे की समीक्षा

**मिशन से संबंध:** मिशन इस पर ख़त्म होता है कि किसी और के इस दावे की समीक्षा करें कि distilled model "teacher के बराबर" है। जो समीक्षा कहती है "मुझे भरोसा नहीं" उसे अनदेखा कर दिया जाता है, और जो बताती है कि माप के किस हिस्से ने क्या छिपाया, और पता लगाने में क्या लगेगा, उस पर अमल होता है।
**मुख्य स्रोत:** [पेपर: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717), sections 1 और 4
**पूर्व-आवश्यकताएँ:** [पाठ 22](0022-student-against-teacher.md), [पाठ 23](0023-an-honest-distillation-eval.md), [Fidelity](../GLOSSARY.md), [Imitation gap](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 17 ने दो चीज़ें अलग कीं जिनमें student अच्छा हो सकता है। उनके नाम बताएँ और बताएँ कि Stanton et al. ने किसे कम पाया, तब भी जब student teacher से मेल बिठा सकता था।

<details markdown="1"><summary>जाँचें</summary>

[Fidelity](../GLOSSARY.md), यानी student की predictions teacher की predictions से कितनी मिलती हैं, और generalization, यानी student task पर कितना अच्छा करता है। Stanton et al. बताते हैं कि teacher और student के predictive distributions के बीच बड़ा अंतर अक्सर तब भी बना रहता है जब student में teacher से ठीक-ठीक मेल बिठाने की capacity हो, और बेहतर generalization के लिए बेहतर fidelity ज़रूरी नहीं ([पेपर](https://arxiv.org/abs/2106.05945), abstract)।

</details>

2. ▢ पाठ 23 ने उन baselines की सूची दी जो "teacher के बराबर" वाली संख्या को बचाव-योग्य बनाते हैं। कौन-सा baseline बताता है कि teacher ने क्या दिया, उसके विपरीत जो student का आकार और data वैसे भी दे देते?

<details markdown="1"><summary>जाँचें</summary>

Student के आकार का model जो teacher के बिना, उसी task data पर train हुआ। उसके बिना, अच्छा score वही हो सकता है जो उस आकार का कोई भी student पाता, और teacher को उस काम का श्रेय मिल जाता है जो उसने किया नहीं।

</details>

3. ▢ पाठ 18 ने imitation gap का नाम लिया। एक वाक्य में, वह style की तुलना में क्षमता पर student के फ़ासला पाटने की गति के बारे में क्या कहता है?

<details markdown="1"><summary>जाँचें</summary>

सीमित बजट पर नक़ल, क्षमता की तुलना में style पर फ़ासला कहीं तेज़ी से पाटती है, इसलिए student वह करने लायक़ बनने से बहुत पहले अपने teacher जैसा सुनाई दे सकता है जो teacher करता है।

</details>

## यह जानें

### दावे के हिस्से होते हैं

"हमारा 7B teacher के बराबर है" एक वाक्य में पाँच दावे हैं: एक model, एक माप, एक baseline, inputs की एक आबादी और एक लागत। समीक्षा उसे खोलती है और हर हिस्से के बारे में पूछती है कि दावे के विफल होने के लिए क्या चाहिए। सबसे उपयोगी समीक्षाएँ यह भी बताती हैं कि क्या ठीक है, ताकि लेखक उसे रखे।

### प्रतिशत क्या मापता है: DistilBERT

Sanh et al. कहते हैं कि DistilBERT 40% छोटा और 60% तेज़ है और "अपनी language understanding क्षमताओं का 97% बनाए रखता है" ([पेपर](https://arxiv.org/abs/1910.01108), abstract)। Section 4 और Table 1 बताती हैं कि वह वाक्य क्या मापता है: GLUE benchmark के नौ tasks, dev sets पर, हर model को fine-tune करने के बाद, BERT और DistilBERT के नतीजे अलग seeds वाले 5 runs की medians हैं। छपे macro-scores BERT-base के लिए 79.5 और DistilBERT के लिए 77.0 हैं, और 77.0 को 79.5 से भाग देने पर 96.9% आता है।

इसलिए 97% दो औसतों का अनुपात है, एक benchmark suite पर, एक teacher के विरुद्ध। प्रति task, Table 1 अलग तस्वीर देती है: CoLA पर DistilBERT 51.3 score करता है जबकि BERT 56.3, जो 91.1% है, और RTE पर 59.9 जबकि 69.3, जो 86.4% है। WNLI पर वह 56.3 score करता है जबकि 53.5, teacher से ऊपर। शीर्षक ग़लत नहीं है। वह एक औसत है जिसमें दो कमज़ोर tasks और कुछ लगभग-बराबरियाँ घुली हुई हैं, और जिस पाठक का workload RTE जैसा दिखता है उसे RTE की पंक्ति पढ़नी चाहिए।

पेपर से तीन और तथ्य समीक्षा में आते हैं। Student को teacher से हर दो में से एक layer लेकर initialize किया गया था (section 3), जो डिज़ाइन का चुनाव है जिसे दावे को बताना चाहिए। उसे BERT के जैसे ही corpus पर train किया गया, इसलिए teacher के data और student के data के बीच कोई shift नहीं है। और compute लगभग 90 घंटे के लिए 8 V100 GPUs था (section 3), जिसमें teacher पहले से train हुआ था और उस आँकड़े में गिना नहीं गया।

### Preference rating क्या छिपाती है: Gudibande et al.

Gudibande et al. ने 1.5B से 13B parameters के models को ChatGPT की नक़ल के लिए fine-tune किया और उन्हें दो तरह से आँका। Crowdworkers ने, लगभग 70 ने, 255 held-out prompts आँके, और imitation models के लगभग 70% outputs ChatGPT के बराबर या बेहतर आँके गए (section 4, Figure 1 बाएँ)। Leakage सीमित करने के लिए उन्होंने वे queries हटा दीं जिनका किसी भी training example के विरुद्ध BLEU score 20% से ऊपर था, और उन्होंने coding और non-English prompts हटा दिए जिन्हें raters आँक नहीं सकते थे।

लक्षित स्वचालित evaluations ने अलग कहानी बताई। लेखक बताते हैं कि imitation models ने उन tasks पर base model और ChatGPT के बीच के फ़ासले का कम या कुछ भी नहीं पाटा जिन्हें imitation data में ज़्यादा सहारा नहीं था, और ज़्यादा imitation data ने उसे नहीं पाटा, कुछ नतीजे, जैसे Natural Questions का तथ्यात्मक ज्ञान, पीछे गए (Figure 1 बीच में)। उनकी व्याख्या है कि models ने ChatGPT का style सीखा, आत्मविश्वासी और अच्छी तरह संरचित, और domain की विशेषज्ञता या तथ्य जाँचने के समय के बिना raters ग़लतियाँ चूक जाते हैं (section 4.4)।

यह एक पेपर का नतीजा है, 13B parameters तक के models से ChatGPT की नक़ल के लिए। जो बात दूसरी जगह भी लागू होती है वह यह नहीं कि preference ratings बेकार हैं। वह यह है कि rating वही मापती है जो rater आँक सकता है, और जो rater एक मिनट में आँक सकता है वह अक्सर style होता है।

### पूछने के सवाल

| दावे का हिस्सा | पूछें | यह क्यों मायने रखता है |
|---|---|---|
| Tasks | कौन-से tasks, और क्या औसत कमज़ोर वाले छिपा रहा है? | DistilBERT का 97% 86% और 91% वाली पंक्तियों के ऊपर बैठा है |
| आबादी | क्या test inputs held-out हैं, या distillation distribution से लिए गए हैं? | Gudibande et al. पाते हैं कि फ़ासला उन tasks पर दिखता है जिन्हें imitation data सहारा नहीं देता |
| Baseline | किसके विरुद्ध: teacher, उसके बिना train हुआ उसी आकार का model, base model? | पहला बताता है कितनी दूर, दूसरा बताता है कि teacher ने क्या जोड़ा |
| Contamination | Test data को distillation prompts से बाहर कैसे रखा गया? | BLEU overlap filter एक ठोस जवाब है, और जिस दावे में कोई नहीं वह एक कमी है |
| Rater | मानव, judge model या metric, और क्या वे तथ्य जाँच सकते थे? | Judge या भीड़ style को पुरस्कृत कर सकते हैं |
| Decoding | Greedy या sampled, कौन-सा temperature, दोनों models के लिए एक-सा? | Agarwal et al. बताते हैं कि mode-seeking divergences ने temperature sampling के तहत बेहतर किया जबकि greedy decoding के तहत चुनाव का मुश्किल से असर था ([पेपर](https://arxiv.org/abs/2306.13649), section 4.1), इसलिए decoding क्रम बदल सकती है |
| Noise | कितने seeds, और run-to-run फैलाव के मुक़ाबले फ़ासला कितना बड़ा है? | DistilBERT 5 runs की medians बताता है, और कई दावे एक बताते हैं |
| लागत | क्या teacher का inference, data generation और filtering गिने गए हैं? | DistilBERT के 90 GPU hours में teacher की pretraining शामिल नहीं है |

दो पंक्तियाँ इस बारे में सवाल हैं कि writeup में क्या ग़ायब है, इस बारे में नहीं कि उसमें क्या ग़लत है। ग़ायब जवाब को दोष नहीं, खुली मद मानें: उसे लिख लें और माँगें।

### समीक्षा लिखना

पहले कहें कि क्या ठीक है। हर छिपे हिस्से को एक लागत की तरह कहें: "औसत उन tasks को छिपाता है जहाँ वह 10 अंक या ज़्यादा गिरा" ठोस है, और "मुझे औसत पर भरोसा नहीं" नहीं है। फिर वह माप बताएँ जो मामला निपटा देगा, उसकी क़ीमत के साथ, ताकि लेखक हाँ या ना कह सके। पाठ 23 के baselines, held-out tasks और contamination जाँचें आम जवाब हैं।

## अभ्यास

1. ▢ अनुमान लगाएँ कि DistilBERT के नौ GLUE tasks में से किन दो में student-से-teacher अनुपात सबसे कम है, फिर इसे Table 1 की संख्याओं पर चलाएँ।

    ```python
    bert = dict(CoLA=56.3, MNLI=86.7, MRPC=88.6, QNLI=91.8, QQP=89.6,
                RTE=69.3, SST2=92.7, STSB=89.0, WNLI=53.5)
    distil = dict(CoLA=51.3, MNLI=82.2, MRPC=87.5, QNLI=89.2, QQP=88.5,
                  RTE=59.9, SST2=91.3, STSB=86.9, WNLI=56.3)
    for task in sorted(bert, key=lambda t: distil[t] / bert[t]):
        print(f"{task:5s} {100 * distil[task] / bert[task]:.1f}")
    print(f"mean of entries {sum(bert.values()) / 9:.1f} and {sum(distil.values()) / 9:.1f}")
    ```

<details markdown="1"><summary>संकेत</summary>

उन tasks को देखें जहाँ teacher ने 100 से बहुत नीचे score किया और student और नीचे गिरा।

</details>

<details markdown="1"><summary>जाँचें</summary>

RTE 86.4 पर और CoLA 91.1 पर सबसे कम हैं, और WNLI 105.2 पर सबसे ऊँचा है। आख़िरी पंक्ति 79.7 और 77.0 print करती है। पेपर BERT-base के लिए 79.5 छापता है, जो उसकी अपनी नौ entries के माध्य के क़रीब है पर बराबर नहीं, और मैं यह तय नहीं कर पाया कि क्यों। दोनों में से कोई भी आँकड़ा कुल मिलाकर लगभग 97% देता है, जो मुद्दा है: शीर्षक आँकड़ा उद्धृत करने से पहले उसे तालिका से दोबारा निकालें।

</details>

2. ▢ एक पेपर बताता है कि crowdworkers ने student के लगभग 70% outputs को उसके teacher के बराबर या बेहतर आँका। आप क्षमता के बारे में क्या निष्कर्ष निकालते हैं, और क्या माँगेंगे?

<details markdown="1"><summary>जाँचें</summary>

क्षमता के बारे में कुछ पक्का नहीं। Gudibande et al. में उसी तरह की rating उन tasks पर फ़ासले के कम पटने के साथ मौजूद रही जिन्हें imitation data सहारा नहीं देता था, क्योंकि raters उस style को पुरस्कृत करते हैं जिसे student ने नक़ल किया। Held-out tasks पर लक्षित स्वचालित evaluations माँगें, और ऐसे raters या जाँच जो तथ्य सत्यापित कर सके।

</details>

3. ▢ काल्पनिक दावा: "हमारा 7B student teacher के बराबर है। 500 prompts पर, एक judge model ने 62% तुलनाओं में student को पसंद किया या बराबर रखा।" Prompts उसी generator से आए जिससे distillation prompts, decoding student के लिए greedy और teacher के लिए sampled थी, और लागत नहीं बताई गई। अपने सवाल सूचीबद्ध करें, जो फ़ैसला सबसे ज़्यादा बदलता हो वह पहले।

<details markdown="1"><summary>जाँचें</summary>

पहले, आबादी: distillation generator के prompts in-distribution हैं, इसलिए held-out tasks माँगें। दूसरा, decoding: दोनों models को एक ही तरह decode किया जाना चाहिए, क्योंकि सेटिंग क्रम बदल सकती है। तीसरा, judge: कौन-सा model, style bias के लिए जाँचा हुआ, और tie rate को preference से अलग। चौथा, baseline: teacher के बिना train हुआ उसी आकार का model। आख़िर में, लागत: teacher की generation और filtering गिनी हुई। यह भी कहें कि क्या ठीक है: 500 prompts पर judge की गई तुलना एक उचित पहली नज़र है।

</details>

4. ▢ कौन-सी जाँच इस बात का सबूत है कि distillation prompts test set में leak नहीं हुए?

    - a) किसी बड़े judge का उसे ऊँचा score देना
    - b) Test prompts पर overlap filter
    - c) कई seeds पर scores का औसत लेना
    - d) Teacher outputs पर ज़्यादा लंबा run

<details markdown="1"><summary>जाँचें</summary>

**b)** वह उसी चीज़ को जाँचता है जिस पर सवाल है, जैसा Gudibande et al. ने किसी भी training example के विरुद्ध 20% पर BLEU filter से किया। (a) और (c) score को आँकने या औसत लेने का तरीक़ा बदलते हैं, यह नहीं कि inputs देखे गए थे या नहीं। (d) overlap के लिए नहीं जाँचता, और उन्हीं prompts का और ज़्यादा उसे बढ़ा सकता है।

</details>

5. ▢ दो पेपर students के लिए forward और reverse KL की तुलना करते हैं। एक greedy decoding से evaluate करता है और थोड़ा अंतर पाता है, दूसरा ऊँचे temperature पर sample करता है और reverse KL को साफ़ बेहतर पाता है। क्या दोनों सही हो सकते हैं, और आप पहले क्या जाँचते हैं?

<details markdown="1"><summary>जाँचें</summary>

हाँ। Agarwal et al. बताते हैं कि mode-seeking divergences ने temperature sampling के तहत बेहतर किया और greedy decoding के तहत चुनाव का मुश्किल से असर था, जो यही बँटवारा है। दोनों को विरोधाभास मानने से पहले हर evaluation की decoding सेटिंग पहले जाँचें, फिर task और model आकार।

</details>

## असली दुनिया का अभ्यास

- [ ] कोई model card या blog post ढूँढें जो दावा करे कि छोटा model बड़े के बराबर है, और सवालों की तालिका की हर पंक्ति के लिए एक पंक्ति लिखें: post जो जवाब देती है, या "नहीं बताया"।
- [ ] उस post की किसी results तालिका से, तालिका की अपनी संख्याओं से, एक प्रतिशत दोबारा निकालें और लिखें कि वह दोहराया जाता है या नहीं।
- [ ] कल: उस दावे की समीक्षा पाँच वाक्यों में लिखें, जो ठीक है उससे शुरू करके और उस एक माप पर ख़त्म करके जो आप माँगेंगे।

## आगे बढ़ने के लिए

- [Distillation Review Checklist शीट](../reference/distillation-review-checklist.md)
- [आकार तय करना और मापना शीट](../reference/sizing-and-measuring.md)
- [पेपर: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717)
- [पेपर: "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter", Sanh et al., 2019](https://arxiv.org/abs/1910.01108)
- [पेपर: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
