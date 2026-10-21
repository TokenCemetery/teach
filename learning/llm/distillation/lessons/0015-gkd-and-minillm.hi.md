---
title: "15. GKD और MiniLLM"
description: "Student से sample करना और teacher से score करवाना, और उसके साथ आने वाले divergence और मिश्रण के चुनाव"
type: lesson
---

# पाठ 15. GKD और MiniLLM

**मिशन से संबंध:** मिशन आपसे माँगता है कि आप on-policy distillation चलाएँ और उसकी settings चुनें, जिसके लिए जानना ज़रूरी है कि GKD के दो knobs क्या करते हैं, MiniLLM क्या अलग करता है, और कौन-से नतीजे किस task से आए।
**मुख्य स्रोत:** [पेपर: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649), sections 2 से 4
**पूर्व-आवश्यकताएँ:** [पाठ 5](0005-forward-and-reverse-kl.md), [पाठ 14](0014-exposure-bias.md), [Generalized knowledge distillation](../GLOSSARY.md), [On-policy distillation](../GLOSSARY.md), [Reverse KL](../GLOSSARY.md)

## वार्म-अप

1. ▢ On-policy distillation का एक step किन sequences पर train करता है, और उन्हें कौन-सा model तय करता है?

<details markdown="1"><summary>जाँचें</summary>

वे sequences जो student training के दौरान generate करता है, इसलिए student उन्हें तय करता है। Teacher सिर्फ़ student के चुने हर token को score करता है। तय sequences पर training, चाहे मानव या teacher के लिखे हों, [off-policy](../GLOSSARY.md) है।

</details>

2. ▢ Forward KL student को teacher के हर mode को कवर करने के लिए धकेलता है और reverse KL एक पर टिकने के लिए। दोनों में से किसमें उस text पर probability रखने का जोखिम है जिसे teacher असंभावित मानता है?

<details markdown="1"><summary>जाँचें</summary>

Forward KL में, क्योंकि वह teacher जिस भी क्षेत्र को कवर करता है उसे चूकने पर दंडित करता है, इसलिए छोटा student उन क्षेत्रों पर फैल जाता है जिन्हें वह अच्छी तरह model नहीं कर सकता। Reverse KL वहाँ probability पर दंडित करता है जहाँ teacher के पास कम है, इसलिए वह विविधता की क़ीमत पर इससे बचता है।

</details>

3. ▢ Exposure bias और student के बस बहुत छोटे होने में क्या फ़र्क़ है?

<details markdown="1"><summary>जाँचें</summary>

Exposure bias prefixes के बारे में है: student किसी और के लिखे prefixes पर train होता है और अपने prefixes से generate करता है। बहुत छोटे student पर इस बात की capacity सीमा होती है कि वह क्या represent कर सकता है, जो तब भी रहती भले हर prefix उसका अपना होता। On-policy training पहली को संबोधित करती है और दूसरी को हटा नहीं सकती।

</details>

## यह जानें

### GKD: दो knobs वाला एक loop

Generalized knowledge distillation (GKD) दो hyperparameters वाला एक algorithm है (Agarwal et al., Algorithm 1)। हर step पर वह एक random संख्या निकालता है। Probability lambda के साथ वह prompts के batch के लिए student से sequences generate करता है। वरना वह ground-truth या teacher-लिखित sequences के तय dataset से एक batch लेता है। फिर वह student को update करता है ताकि teacher और student के token distributions के बीच एक divergence कम हो, positions पर औसत लेकर, sampling के आर-पार gradient के बिना।

Lambda **student data fraction** है। Lambda 0 साधारण supervised distillation है और lambda 1 पूरी तरह on-policy। पेपर के "mixed" रूप 0.5 इस्तेमाल करते हैं। Training के दौरान student अपने sequences को विविध रखने के लिए temperature 1 पर sample करता है।

दूसरा knob divergence है। GKD generalized Jensen-Shannon divergence, JSD(beta), इस्तेमाल करता है, जो दोनों KL दिशाओं का bounded मेल है। पेपर की परिपाटी के साथ, 0 के पास beta forward KL की तरह बर्ताव करता है और 1 के पास reverse KL की तरह, इसलिए 0.1, 0.5 और 0.9 उस रेखा पर बिंदु हैं। TRL का trainer वही दिशा दर्ज करता है: beta 0.0 लगभग forward KL है और beta 1.0 reverse KL।

### पेपर ने क्या पाया, task-दर-task

Students T5-small (77M), T5-base (250M) और T5-large (800M) parameters के हैं, लगभग 3B के fine-tuned T5-XL से distil किए गए, इसलिए teacher 38 गुना, 12 गुना और 3.8 गुना बड़ा है। नतीजे T5 पर पेपर के अपने हैं, LLMs के बारे में सामान्य तथ्य नहीं।

| Task | Metric | क्या काम किया | पेपर में स्रोत |
|---|---|---|---|
| XSum summarization | ROUGE-2 | JSD(0.9) वाले on-policy GKD ने greedy और temperature sampling के तहत अतिरिक्त baselines ImitKD और f-distill को हराया। Mode-seeking divergences ने temperature sampling के तहत बेहतर किया, और greedy decoding के तहत divergence का असर कम था | Section 4.1, Figures 3 और 4 |
| WMT14 अंग्रेज़ी से जर्मन | BLEU | Generalized JSD ने forward और reverse KL को हराया, बड़े student के लिए छोटे अंतर के साथ। सिर्फ़ student-generated data ने दूसरे data मिश्रणों को हराया। Figure 1 ने JSD(0.1) इस्तेमाल किया | Section 4.2, Figure 6 |
| Chain of thought के साथ GSM8K | accuracy | अकेली student-generated chains ने तय या मिश्रित data को हराया। Forward KL ने अच्छा किया, और reverse KL ने भी। फ़ायदे तब बने रहे जब कम से कम 25% data on-policy था | Section 4.3, Figures 8 और 9 |
| FLAN पर instruction tuning | held-out MMLU और BBH | Reverse KL वाले on-policy GKD ने forward KL को साफ़ तौर पर हराया | Section 4.4, Figure 10 |

लेखकों का सार यह है कि सबसे अच्छा divergence task पर निर्भर है, जबकि on-policy और mixed data लगातार तय data को हराते हैं। दो और नतीजे जानने लायक़ हैं। T5-small के साथ XSum पर, 5% उपनमूने पर on-policy GKD ने, बिना ground-truth summaries के, पूरे dataset पर train हुए supervised KD और ImitKD को हराया (section 4.1)। Student आकारों पर औसत लेने पर, शुरुआती student के मुक़ाबले प्रदर्शन का फ़ायदा baseline KD से summarization पर 2.1 गुना, translation पर 1.7 गुना और अंकगणितीय reasoning पर 1.9 गुना था (Introduction)।

Instruction tuning के लिए पेपर का text और उसकी Figure 10 का caption इस पर असहमत हैं कि student T5-base है या T5-large, इसलिए यह पाठ उस task के लिए student का आकार उद्धृत नहीं करता। Teacher MMLU पर 52.4% और BBH पर 41% तक पहुँचा। लेखक परिकल्पना करते हैं कि reverse KL वहाँ इसलिए काम करता है कि उसकी mode-seeking प्रकृति model को instruction के मुख्य इरादे पर केंद्रित कर देती है, और वे इसे परिकल्पना के रूप में रखते हैं, खोज के रूप में नहीं।

### MiniLLM: policy की तरह optimise किया गया reverse KL

Gu et al. (MiniLLM) on-policy training तक दूसरी दिशा से पहुँचते हैं। वे तर्क देते हैं कि forward KL कम-capacity वाले student से teacher के कम-probability वाले क्षेत्रों को ज़्यादा आँकवाता है, और इसके बजाय पूरे sequences पर reverse KL कम करते हैं। क्योंकि expectation student के अपने distribution के तहत है, वे gradient को policy gradient theorem से निकालते हैं और प्रति-token signal के रूप में teacher से student probability के log-अनुपात के साथ, reinforcement learning की तरह train करते हैं।

सादे policy gradient में समस्याएँ हैं, और पेपर तीन उपाय जोड़ता है:

| समस्या | उपाय | विवरण |
|---|---|---|
| ऊँचा variance | Single-step decomposition | प्रति-token term sampling के बजाय vocabulary पर योग लेकर निकाला जाता है |
| Reward hacking: दोहराए वाक्यांश जैसा बिगड़ा text teacher के साथ अच्छा score करता है | Teacher-mixed sampling | हर चरण पर alpha गुणा teacher और (1 घटा alpha) गुणा student से sample करें, experiments में alpha 0.2 के साथ |
| लंबे outputs को जमा हुए छोटे rewards मिलते हैं, इसलिए student बहुत छोटे या ख़ाली उत्तर देना सीख लेता है | Length normalisation | जमा हुए reward को बची हुई लंबाई से normalise करें |

वह clipping और pretraining text पर language-modelling loss भी जोड़ता है ताकि सामान्य benchmark प्रदर्शन बना रहे। Training task data पर fine-tune किए student से शुरू होती है। GKD से अंतर नोट करें: MiniLLM के samples कुछ हद तक mixing के ज़रिए teacher से आते हैं, इसलिए वह पूरी तरह on-policy नहीं है, और वह sequence-level objective optimise करता है जहाँ GKD token-level divergence का औसत लेता है।

### MiniLLM के नतीजे

Setup 15K Dolly examples पर instruction following है, training के लिए लगभग 12.5K, GPT-2 (120M से 760M, teacher GPT-2 1.5B), OPT (1.3B से 6.7B, teacher OPT 13B) और LLaMA (7B, teacher LLaMA 13B) के students के साथ। Table 1 के कुछ cells, DollyEval पर औसत GPT-4 feedback score:

| Student | सिर्फ़ fine-tuned | Standard KD | SeqKD | MiniLLM | Teacher |
|---|---|---|---|---|---|
| OPT 1.3B | 52.6 | 52.7 | 51.0 | 60.7 | 70.3 |
| OPT 6.7B | 67.9 | 68.6 | 69.6 | 70.8 | 70.3 |
| LLaMA 7B | 73.0 | 73.7 | 73.6 | 76.4 | 79.0 |

GPT-4 metric, model के उत्तर के लिए GPT-4 के score का reference उत्तर के score से अनुपात है, इसलिए वह सापेक्ष है, निरपेक्ष नहीं। लेखक यह भी बताते हैं कि students कभी-कभी Rouge-L पर teacher को हरा देते हैं और अनुमान लगाते हैं कि यह teacher में exposure bias को दर्शाता है। Calibration पर, student MiniLLM की error forward-KL baselines से कम थी पर teacher से अब भी ऊपर: SST2 पर, ECE 0.099, जबकि teacher की 0.025 और standard KD की 0.191 (Table 2)।

### आप क्या निष्कर्ष नहीं निकाल सकते

हर पेपर ने अपनी विधि को अपने students, teachers और metrics पर tune किया, इसलिए ऊपर की संख्याएँ GKD को MiniLLM के विरुद्ध क्रमबद्ध नहीं करतीं। मुझे किसी भी पेपर में आमने-सामने की तुलना नहीं मिली। उनके विचारों की तुलना करें, और दोनों को अपने जोड़े पर परखें।

### चलाने योग्य configuration

TRL का `GKDTrainer` दोनों knobs को `GKDConfig` पर `lmbda` और `beta` के रूप में देता है। उसके दर्ज defaults हर एक के लिए 0.5 हैं, generation के लिए `temperature` 0.9 और `max_new_tokens` 128 के साथ, और `seq_kd` बंद। नीचे का docs उदाहरण Qwen2-1.5B-Instruct को Qwen2-0.5B-Instruct में distil करता है। मैंने इसे चलाया नहीं है, इसलिए import path को अपने install किए TRL version से जाँचें, क्योंकि मौजूदा docs GKD को `trl.experimental` के अंतर्गत रखते हैं।

```python
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl.experimental.gkd import GKDConfig, GKDTrainer

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
student = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
teacher = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-1.5B-Instruct")

train = Dataset.from_dict({"messages": [[
    {"role": "user", "content": "Hi, how are you?"},
    {"role": "assistant", "content": "I'm great thanks"},
]] * 100})

args = GKDConfig(
    output_dir="gkd-model",
    per_device_train_batch_size=1,
    lmbda=1.0,  # purely on-policy: every batch is student-generated
    beta=1.0,   # generalized JSD at the reverse-KL end
)
trainer = GKDTrainer(model=student, teacher_model=teacher, args=args,
                     processing_class=tokenizer, train_dataset=train)
trainer.train()
```

दोनों models एक tokenizer साझा करते हैं क्योंकि वे एक ही परिवार के हैं, जो पाठ 6 ने समझाया कि logit distillation के लिए ज़रूरी है। TRL पेज का अपना मार्गदर्शन पेपर से मेल खाता है: on-policy data (ऊँचा `lmbda`) बेहतर करता है, और सबसे अच्छा `beta` task और evaluation विधि पर निर्भर है।

## अभ्यास

1. ▢ GKD में, lambda और divergence की कौन-सी settings (a) supervised distillation और (b) on-policy KD को दोहराती हैं, जैसे पेपर उन्हें परिभाषित करता है?

<details markdown="1"><summary>जाँचें</summary>

दोनों forward KL इस्तेमाल करते हैं। Lambda 0 supervised KD देता है, जहाँ student कभी generate नहीं करता, और lambda 1 on-policy KD देता है, जहाँ हर sequence student का है। बीच के मान mixed रूप हैं। Divergence और data स्रोत स्वतंत्र knobs हैं, इसीलिए वही forward KL दोनों में दिखता है।

</details>

2. ▢ FLAN पर GKD के instruction-tuning experiment में, पेपर ने किस जोड़ी को अपने forward-KL समकक्ष से साफ़ बेहतर पाया?

    - a) Forward KL, student samples
    - b) Reverse KL, student samples
    - c) Forward KL, तय sequences
    - d) Reverse KL, तय sequences

<details markdown="1"><summary>जाँचें</summary>

**b)** Reverse KL वाले on-policy GKD ने section 4.4 में बाक़ी तरीक़ों को पीछे छोड़ा। (a) greedy decoding के साथ XSum और GSM8K के लिए पेपर का चुनाव है, instruction tuning के लिए नहीं। (c) और (d) तय data इस्तेमाल करते हैं, जिसे पेपर ने student-generated data से लगातार कमज़ोर पाया।

</details>

3. ▢ हर MiniLLM उपाय को उस विफलता से मिलाएँ जिसे वह रोकता है: (1) teacher-mixed sampling, (2) length normalisation, (3) single-step decomposition। विफलताएँ: A, student बहुत छोटे या ख़ाली उत्तर देता है। B, gradient में ऊँचा variance। C, student को ऐसा बिगड़ा text मिलता है जिसे teacher अच्छा score देता है।

<details markdown="1"><summary>जाँचें</summary>

(1) का मेल C से है, (2) का A से, (3) का B से। Teacher-mixed sampling, sampling distribution में teacher को मिलाकर बिगड़े samples को दबाती है। Length normalisation लंबे sequences को जमा हुए छोटे rewards से दंडित होने से रोकती है। Single-step decomposition प्रति-token term को sampling के बजाय पूरी vocabulary पर निकालती है, जिससे variance घटता है।

</details>

4. ▢ MiniLLM-शैली के objective से train हुआ student एक दोहराया वाक्यांश निकालना शुरू कर देता है जिसे teacher ऊँची probability देता है। कौन-सी तरकीब इसे निशाना बनाती है, और पेपर ने कौन-सा मान इस्तेमाल किया?

<details markdown="1"><summary>संकेत</summary>

Teacher का score ही reward है। जो बिगड़ा sample teacher को पसंद है वह उस reward का फ़ायदा उठा रहा है।

</details>

<details markdown="1"><summary>जाँचें</summary>

Teacher-mixed sampling, जिसे पेपर reward hacking के विरुद्ध पेश करता है, अपने सारे experiments में alpha 0.2 के साथ (section 3.1)। यह मान उस पेपर का अपनी setup पर चुनाव है, इसलिए इसे शुरुआती बिंदु मानें, स्थिरांक नहीं।

</details>

5. ▢ ऊपर की Table 1 से, सिर्फ़-fine-tuned student और teacher के बीच के फ़ासले का कितना हिस्सा MiniLLM OPT 1.3B और LLaMA 7B के लिए पाटता है? OPT 6.7B वाली पंक्ति से आप क्या निष्कर्ष नहीं निकाल सकते?

<details markdown="1"><summary>जाँचें</summary>

OPT 1.3B: फ़ासला 70.3 घटा 52.6 है, यानी 17.7, और MiniLLM 8.1 पाता है, लगभग 46%। LLaMA 7B: फ़ासला 6.0 है और MiniLLM 3.4 पाता है, लगभग 57%। OPT 6.7B पंक्ति में MiniLLM teacher के 70.3 के मुक़ाबले 70.8 score करता है, पर इससे यह नहीं दिखता कि student बेहतर है: metric reference उत्तरों के सापेक्ष है, अंतर आधा अंक है, और यह एक model जोड़ा है।

</details>

6. ▢ आप TRL में reverse KL के साथ शुद्ध on-policy run चाहते हैं। आप कौन-से दो config मान सेट करेंगे, और अगर आपके पास सिर्फ़ teacher का text हो तो क्या आप उसे चला सकते हैं?

<details markdown="1"><summary>जाँचें</summary>

`lmbda=1.0` और `beta=1.0`। नहीं: divergence को student के sequence के हर position पर teacher का distribution चाहिए, इसलिए आपको teacher model ख़ुद चाहिए, संग्रहीत text dump नहीं। सिर्फ़ text के साथ आप sequence level पर लौट आएँगे (पाठ 8)। TRL का `seq_kd` विकल्प इसे नहीं बदलता, क्योंकि teacher फिर भी token-विशिष्ट प्रतिक्रिया देता है।

</details>

## असली दुनिया का अभ्यास

- [ ] GKD पेपर का section 3.1 पढ़ें। Loss को एक पंक्ति में लिखें, फिर गोला लगाएँ कि lambda और divergence हर एक कहाँ आते हैं।
- [ ] MiniLLM पेपर की Table 1 खोलें और ऐसा एक student चुनें जहाँ MiniLLM हर column में teacher को नहीं हरा पाया। लिखें कि वह किस metric पर हारा और कितने से।
- [ ] कल: बिना नोट्स के लिखें कि lambda और beta हर एक क्या नियंत्रित करते हैं, GKD में एक ऐसा task बताएँ जहाँ reverse KL जीता, और MiniLLM के तीन उपायों के नाम लें।

## आगे बढ़ने के लिए

- [On-Policy Distillation शीट](../reference/on-policy-distillation.md)
- [पेपर: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [पेपर: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
- [दस्तावेज़: "Generalized Knowledge Distillation Trainer", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gkd_trainer)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
