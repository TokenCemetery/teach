---
title: "Distillation"
description: "बड़े model को छोटे में distil करें और उसका बचाव करें: soft targets, logit और sequence-level losses, synthetic data, on-policy training, और student ने क्या खो दिया"
type: topic
---

# सीखना: Distillation

बड़े model के outputs से सीखकर छोटे model को वही करना सिखाएँ जो बड़ा model करता है, और जानें कि distillation का हर रूप क्या transfer करता है और क्या नहीं कर सकता। अंत में किसी दिए task और बजट के लिए तय कर सकें कि distill करना है, quantize करना है या छोटे model को सीधे train करना है, ईमानदारी से माप सकें कि student ने क्या खोया, और किसी और के इस दावे की समीक्षा कर सकें कि distilled model "teacher के बराबर है"।

**नवीनतम पाठ:** [27. जब आम जवाब ग़लत हो](lessons/0027-when-the-usual-answer-is-wrong.md)

## सफलता कैसी दिखती है

- समझाएँ कि teacher के soft targets में hard labels से ज़्यादा training signal क्यों होता है, और distillation run का temperature और loss weights तय करें।
- LLM के लिए token-level distillation loss लिखें, forward और reverse KL में से चुनें, और बताएँ कि tokenizer mismatch कब logit distillation को नामुमकिन कर देता है।
- Sequence level पर या teacher के generate किए data से distill करें, और बताएँ कि हर तरीक़ा वह क्या transfer करता है जो दूसरा नहीं करता।
- गुणवत्ता के लिए filter किया हुआ synthetic distillation set बनाएँ, और जाँचें कि teacher का license और terms उसके outputs पर training की अनुमति देते हैं या नहीं।
- Exposure bias समझाएँ, और बताएँ कि fixed teacher outputs पर training के मुक़ाबले on-policy distillation अपनी लागत के लायक़ कब है।
- अनुमान लगाएँ कि student अपने teacher से क्या पाएगा और क्या नहीं, जिसमें वह क्षमता भी शामिल है जिसे वह सोख नहीं सकता और वे विशेषताएँ भी जो किसी ने पास करने की सोची नहीं थी।
- Teacher की अपनी लागत को बजट में गिनकर student का आकार और data की मात्रा चुनें।
- माप सकें कि student ने अपने teacher के मुक़ाबले क्या खोया, और उस model के मुक़ाबले भी जो उसी आकार का है पर बिना teacher के train हुआ।
- तय करें कि distill करना है, quantize करना है या छोटे model को सीधे fine-tune करना है, किसी और के distillation दावे की समीक्षा उसमें छिपी बात का नाम लेकर करें, किसी ऐसे model को student से बदलें जिस पर दूसरे निर्भर हैं, और बताएँ कि आम जवाब कब ग़लत होता है।

## सीमाएँ

- मानकर चला गया है कि आप Python और PyTorch पढ़ने में सहज हैं, और जानते हैं कि cross-entropy loss, softmax और training loop क्या हैं। Distillation का कोई पूर्व ज्ञान नहीं चाहिए, और reinforcement learning का भी नहीं, सिवाय इस विचार के कि model से sample किया जा सकता है।
- पेपर और model reports पर आधारित। जहाँ कोई संख्या एक पेपर के अपने setup का नतीजा है, पाठ यह कहता है, क्योंकि distillation के नतीजे teacher, student और data पर बहुत निर्भर करते हैं।
- चरण 1 और 2 का अभ्यास laptop पर चलता है, एक ऐसे classifier के साथ जो CPU के लिए काफ़ी छोटा हो। बाद के अभ्यास दो छोटे open models के बीच distill करते हैं, जिनके लिए मुफ़्त GPU notebook काफ़ी है।

## दायरे से बाहर

- किसी reasoning model को उसकी लंबी chains of thought पर fine-tune करके distil करना: [`llm/post-training`](../../llm/post-training/) का पाठ 0014 देखें। वह पाठ reasoning-model का मामला बना रहता है; यह track सामान्य रूप से distillation सिखाता है और उसे दोहराने के बजाय उसकी ओर link करता है।
- LoRA या QLoRA adapters से supervised fine-tuning चलाना: [`llm/finetuning`](../../llm/finetuning/) देखें। यह track distillation का objective और data सँभालता है; training को कम parameters पर कैसे लगाया जाता है, यह वहीं रहता है।
- Pretraining run चलाना: [`llm/pretraining`](../../llm/pretraining/) देखें। Pretraining signal के रूप में distillation यहाँ loss और data के चुनाव की तरह सिखाया जाता है (पाठ 0007), pretraining run की तरह नहीं।
- Eval बनाना: [`llm/evals`](../../llm/evals/) और उसकी [Go/No-Go शीट](../../llm/evals/reference/go-no-go.md) देखें। यह track student की teacher से तुलना के लिए eval इस्तेमाल करता है और eval बनाना दोबारा नहीं सिखाता।
- Model की precision घटाकर उसे छोटा करना: [`llm/quantization`](../../llm/quantization/) देखें। Model को छोटा करने का दूसरा तरीक़ा यह track है, कम parameters के साथ, और दोनों की तुलना चरण 9 का हिस्सा है।
- Pruning अपने आप में एक विधि के रूप में। पाठ 0007 इसे Minitron में distillation के साथ जोड़कर दिखाता है, और सिर्फ़ distillation वाला आधा हिस्सा सिखाता है।

## पूरी रूपरेखा

नौ चरण, इस बात से कि छोटा model बड़े से कैसे सीख सकता है, किसी और के distillation की समीक्षा करने के विवेक तक। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. Distillation क्यों काम करता है | 0001 से 0003 | Teacher और student, soft targets और वे क्या ढोते हैं, temperature और combined loss | बता सकें कि soft targets hard labels से ज़्यादा क्यों सिखाते हैं और temperature तय कर सकें |
| 2. LLMs के लिए logit distillation | 0004 से 0007 | Token-level distillation, forward और reverse KL, साझा-tokenizer की बाध्यता, pretraining signal के रूप में distillation | Token-level loss लिख सकें और बता सकें कि उसे कब इस्तेमाल नहीं किया जा सकता |
| 3. Sequence-level distillation | 0008 से 0009 | Teacher के decode किए outputs पर training, और token तथा sequence level में से चुनना | बता सकें कि हर level क्या transfer करता है और teacher जो कुछ उपलब्ध कराता है उसके आधार पर एक चुन सकें |
| 4. Synthetic-data distillation | 0010 से 0013 | Generate किया गया instruction data, rationales और explanation traces, filtering, licensing और terms | Filter किया हुआ distillation set बना सकें और जाँच सकें कि उसका इस्तेमाल अनुमत है |
| 5. On-policy distillation | 0014 से 0016 | Exposure bias, GKD और MiniLLM, on-policy training की लागत और उससे मिलने वाला फ़ायदा | बता सकें कि on-policy distillation अपनी लागत कब वसूल करता है |
| 6. Student को विरासत में क्या मिलता है | 0017 से 0019 | Fidelity बनाम generalization, imitation gap, capacity gap, अनजाने में पास हुई विशेषताएँ | अनुमान लगा सकें कि student अपने teacher से क्या उठाएगा और क्या नहीं |
| 7. आकार तय करना | 0020 से 0021 | Distillation scaling laws, data की मात्रा, बजट में teacher की लागत | Student का आकार और data की मात्रा चुन सकें और compute का बचाव कर सकें |
| 8. जो खोया उसे मापना | 0022 से 0023 | Task की गुणवत्ता के मुक़ाबले teacher से सहमति, baselines, held-out tasks, contamination | माप सकें कि student ने क्या खोया और उस संख्या का बचाव कर सकें |
| 9. विवेक | 0024 से 0027 | Distill, quantize या छोटा fine-tune, किसी दावे की समीक्षा, ऐसे model को बदलना जिस पर दूसरे निर्भर हैं, जब आम जवाब ग़लत हो | भरोसेमंद हों कि distillation पर फ़ैसला ले सकें और उसे किसी और को समझा सकें |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-what-distillation-buys.md) | Distillation से क्या मिलता है | बड़े teacher की नक़ल करने के लिए train किया गया छोटा student, और नक़ल अकेले labels पर student को train करने से बेहतर क्यों हो सकती है |
| [0002](lessons/0002-soft-targets.md) | Soft Targets | गलत उत्तरों को teacher जो probabilities देता है उनमें क्या होता है, और वे hard label से समृद्ध training signal क्यों हैं |
| [0003](lessons/0003-temperature.md) | Temperature | दोनों distributions को temperature से नरम करना, T squared सुधार, और hard-label loss को मिलाना |
| [0004](lessons/0004-token-level-distillation.md) | Token-Level Distillation | Sequence के हर position पर teacher के next-token distribution से मेल बिठाना |
| [0005](lessons/0005-forward-and-reverse-kl.md) | Forward और Reverse KL | Forward KL student को teacher के हर mode पर क्यों फैला देता है और reverse KL उसे एक पर क्यों टिका देता है |
| [0006](lessons/0006-the-tokenizer-constraint.md) | Tokenizer की बाध्यता | Logit distillation को साझा vocabulary क्यों चाहिए, और cross-tokenizer तरीक़े क्या छोड़ देते हैं |
| [0007](lessons/0007-distilling-during-pretraining.md) | Pretraining के दौरान Distillation | Gemma 2 और Minitron ने बड़े पैमाने पर teacher के distribution को training signal कैसे बनाया, और logits सहेजने में क्या लागत आती है |
| [0008](lessons/0008-sequence-level-distillation.md) | Sequence-Level Distillation | Student को teacher के distributions के बजाय उसके decode किए outputs पर train करना |
| [0009](lessons/0009-token-or-sequence.md) | Token या Sequence | हर level क्या transfer करता है, दोनों को जोड़ना, और इस आधार पर चुनना कि teacher logits देता है या सिर्फ़ text |
| [0010](lessons/0010-distilling-from-generated-data.md) | Generated Data से Distillation | Teacher की generations से instruction set बनाना, जैसा Self-Instruct और Alpaca ने किया |
| [0011](lessons/0011-rationales-and-explanation-traces.md) | Rationales और Explanation Traces | Teacher के उत्तरों के साथ उसकी reasoning पर भी train करना, जैसा Distilling Step-by-Step और Orca ने किया |
| [0012](lessons/0012-filtering-synthetic-data.md) | Synthetic Data को Filter करना | Generate किए data पर train करने से पहले उसे जाँचना, filter करना और deduplicate करना, क्योंकि मात्रा ख़राब examples को ठीक नहीं करती |
| [0013](lessons/0013-licensing-and-terms.md) | Licensing और Terms | किसी provider के terms और किसी open model का license उसके outputs के साथ आपको क्या करने देते हैं |
| [0014](lessons/0014-exposure-bias.md) | Exposure Bias | Teacher के prefixes पर train हुआ student inference में अपनी ग़लतियों से क्यों टकराता है जबकि उन पर train नहीं हुआ था |
| [0015](lessons/0015-gkd-and-minillm.md) | GKD और MiniLLM | Student से sample करना और teacher से score करवाना, और उसके साथ आने वाले divergence और मिश्रण के चुनाव |
| [0016](lessons/0016-on-policy-distillation-in-practice.md) | व्यवहार में On-Policy Distillation | On-policy distillation प्रति step कितना महँगा है, क्या देता है, और Qwen3 ने अपने छोटे models के लिए इसे कैसे इस्तेमाल किया |
| [0017](lessons/0017-fidelity-and-generalization.md) | Fidelity और Generalization | अच्छी तरह generalize करने वाला student अपने teacher से असहमत क्यों हो सकता है, और दोनों में से आपको कौन-सा चाहिए |
| [0018](lessons/0018-the-imitation-gap.md) | Imitation Gap | किसी मज़बूत model की नक़ल उसकी क्षमता की तुलना में उसका style कहीं तेज़ी से क्यों उतार लेती है |
| [0019](lessons/0019-capacity-gap-and-hidden-traits.md) | Capacity Gap और छिपी विशेषताएँ | बड़ा teacher हमेशा बेहतर क्यों नहीं होता, और student तक ऐसा क्या पहुँच सकता है जो किसी ने चाहा नहीं था |
| [0020](lessons/0020-choosing-student-size.md) | Student का आकार चुनना | Distillation scaling laws क्या कहते हैं कि distilling कब student को सीधे train करने से बेहतर है |
| [0021](lessons/0021-data-volume-and-teacher-cost.md) | Data की मात्रा और Teacher की लागत | बजट में teacher के inference को गिनना, और तय करना कि distillation data कितना काफ़ी है |
| [0022](lessons/0022-student-against-teacher.md) | Student बनाम Teacher | Teacher से सहमति को task की गुणवत्ता से अलग मापना, एक-एक क्षमता करके |
| [0023](lessons/0023-an-honest-distillation-eval.md) | ईमानदार Distillation Eval | वे baselines, held-out tasks और contamination जाँचें जो "teacher के बराबर" वाली संख्या का बचाव करने लायक़ बनाती हैं |
| [0024](lessons/0024-distill-quantize-or-fine-tune.md) | Distill करें, Quantize करें या Fine-Tune करें | Task और बजट से चुनना कि कम parameters, कम bits या छोटे model की सीधी training में से क्या अपनाएँ |
| [0025](lessons/0025-reviewing-a-distillation-claim.md) | Distillation के दावे की समीक्षा | "हमारा छोटा model बड़े के बराबर है" की समीक्षा यह बताकर करना कि माप ने क्या छिपाया |
| [0026](lessons/0026-replacing-a-model-others-depend-on.md) | ऐसे Model को बदलना जिस पर दूसरे निर्भर हैं | Student को उसके teacher की जगह इस तरह लाना कि उसके व्यवहार पर निर्भर लोगों का कुछ न टूटे |
| [0027](lessons/0027-when-the-usual-answer-is-wrong.md) | जब आम जवाब ग़लत हो | पहचानें कि distillation कब ग़लत फ़ैसला है, और विवादित दावे का निपटारा मुख्य स्रोत से करें |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत, हर एक के साथ टिप्पणी कि वह क्या कवर करता है
- [Distillation Losses शीट](reference/distillation-losses.md): soft targets, temperature, combined loss, दोनों दिशाओं में token-level KL और tokenizer की बाध्यता, चरण 1 और 2 से
- [Sequence और Synthetic Data शीट](reference/sequence-and-synthetic-data.md): sequence-level distillation, generated data, rationales, filtering और license के सवाल, चरण 3 और 4 से
- [On-Policy Distillation शीट](reference/on-policy-distillation.md): exposure bias, GKD और MiniLLM आमने-सामने, और on-policy training कब फ़ायदेमंद है, चरण 5 से
- [Student को क्या विरासत में मिलता है शीट](reference/what-the-student-inherits.md): fidelity, imitation gap, capacity gap और अनचाही विशेषताएँ, चरण 6 से
- [आकार तय करना और मापना शीट](reference/sizing-and-measuring.md): teacher की लागत के साथ student का आकार और data की मात्रा चुनना, और ईमानदार student-बनाम-teacher eval, चरण 7 और 8 से
- [Distillation Review Checklist शीट](reference/distillation-review-checklist.md): distill, quantize और fine-tune में से चुनना, और किसी और के distillation दावे से पूछने के सवाल, चरण 9 से

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके मुख्य स्रोत तक खंगालना ठीक रहेगा।
