---
title: "22. Pretraining अक्सर ग़लत default होता है"
description: "मौजूदा model पर pretraining का दूसरा चरण पूरी लागत दोबारा चुकाए बिना ज़्यादातर फ़ायदा दिला देता है"
type: lesson
---

# पाठ 22. Pretraining अक्सर ग़लत default होता है

**मिशन से संबंध:** "तय करें कि दिया गया task pretraining, continued pretraining या किसी मौजूदा base model की fine-tuning माँगता है, और चुनाव का बचाव लागत के आधार पर करें" "सफलता कैसी दिखती है" का वह बिंदु है जिसे चरण 10 पूरा करता है। यह पाठ उस default के ख़िलाफ़ तर्क रखता है जिसकी ओर ज़्यादातर नए लोग जाते हैं; पाठ 23 कवर करता है कि pretraining सचमुच सही फ़ैसला हो तब बजट का बचाव कैसे करें, और पाठ 24 कवर करता है कि किसी और के बजट की समीक्षा कैसे करें।
**मुख्य स्रोत:** [पेपर: "Don't Stop Pretraining: Adapt Language Models to Domains and Tasks", Gururangan et al., 2020](https://arxiv.org/abs/2004.10964)
**पूर्व-आवश्यकताएँ:** [पाठ 21](0021-periodic-held-out-evaluation.md)

## वार्म-अप

1. ▢ Rae et al. ने कुछ benchmarks को समय-समय की evaluation जाँचों के रूप में इस्तेमाल करने से पहले Gopher के training set से साफ़ तौर पर क्यों हटाया?

<details markdown="1"><summary>जाँचें</summary>

ताकि उन benchmarks पर अच्छा score इस बात से समझाया न जा सके कि model ने वही text training में बस देखा और रट लिया था; जिस benchmark पर model train हुआ हो वह असली क्षमता और रटने में फ़र्क़ नहीं कर सकता।

</details>

2. ▢ Training के दौरान समय-समय पर evaluate करना, सिर्फ़ अंत में एक बार के बजाय, team को असल में क्या देता है?

<details markdown="1"><summary>जाँचें</summary>

यह bug, regression, या क्षमता में divergence को run अभी चलते हुए पकड़ने और संभवतः संबोधित करने देता है, न कि पूरा compute budget ख़र्च हो जाने के बाद ही खोजने देता है।

</details>

## यह जानें

### "हमें अपना ही pretrained model चाहिए" आम तौर पर ग़लत सहज बुद्धि क्यों है

इस track का हर चरण एक ईमानदार तथ्य की ओर बढ़ रहा था: model को शुरू से pretrain करना असाधारण रूप से महँगा है। अकेला चरण 3 का compute-optimal हिसाब, 70-अरब-parameter model को लगभग एक खरब tokens चाहिए, अंदाज़ा देता है कि एक अकेला शुरू-से वाला run कितने पैमाने का compute माँगता है, उस distributed training infrastructure की engineering लागत गिनने से पहले जिसे चरण 4 से 6 ने कवर किया, या निगरानी और fault-tolerance की संचालन लागत से पहले जिसे चरण 8 और 9 ने कवर किया। किसी ख़ास domain, किसी ख़ास task या किसी ख़ास शैली में अच्छा model चाहना, अपने-आप में, वह सारी लागत दोबारा चुकाने को जायज़ नहीं ठहराता। पहले पूछने लायक़ सवाल "इसके लिए model कैसे pretrain करें" नहीं है, बल्कि "क्या इसे असल में नया pretrained model चाहिए भी"।

### सस्ते विकल्प के लिए सबूत

Gururangan et al. एक आम मामले के लिए इसका सीधा उत्तर देते हैं: उस domain के लिए नया model pretrain करने के बजाय किसी मौजूदा व्यापक-कवरेज वाले pretrained model को किसी ख़ास domain के लिए ढालना। वे RoBERTa, एक मौजूदा बड़ा pretrained model, लेते हैं और target domain के बिना label वाले text पर उसकी pretraining जारी रखते हैं, **pretraining का दूसरा चरण** जिसे वे **domain-adaptive pretraining (DAPT)** कहते हैं, फिर उस domain के tasks पर evaluate करते हैं। चार domains (biomedical पेपर, computer science पेपर, समाचार और reviews) और आठ classification tasks में, वे पाते हैं कि यह target domain के tasks पर प्रदर्शन को लगातार सुधारता है, ज़्यादा-संसाधन और कम-संसाधन दोनों स्थितियों में, जब भी target domain model की मूल pretraining में पहले से अच्छी तरह प्रतिनिधित्व में नहीं था। वे यह भी पाते हैं कि किसी task के अपने बिना label वाले data पर और ढालना, **task-adaptive pretraining (TAPT)**, DAPT के ऊपर प्रदर्शन को फिर सुधारता है, और यह कि एक सस्ता विकल्प भी, सरल data-selection heuristics से बने task corpus पर ढालना, अच्छा चलता है जब पूरा domain-adaptive pretraining सस्ता नहीं पड़ता।

### यह किसके पक्ष में तर्क देता है, और किसके नहीं

इसमें से कुछ भी यह दावा नहीं करता कि शुरू से pretraining कभी जायज़ नहीं है; वह दावा करता है कि default धारणा उलटी दिशा में चलनी चाहिए। किसी मौजूदा, पहले से व्यापक रूप से सक्षम model पर pretraining जारी रखना, उस compute के छोटे हिस्से पर जो शुरू-से वाले run को चाहिए, उस फ़ायदे का असली हिस्सा लगातार पकड़ लेता है जो पूरी तरह domain-विशेष model दे सकता था। "हमारे domain में अच्छा model" माँगने वाला लगता task, इस सबूत के अनुसार, बहुत बार नए pretraining run की क़ीमत चुकाने के बजाय मौजूदा base model पर continued pretraining से, या अगर task और संकरा हो तो `llm/finetuning` में कवर की गई adapter fine-tuning से बेहतर सधता है। इन सस्ते विकल्पों को ख़ारिज किए बिना पूरी pretraining की ओर जाना वह ख़ास ग़लती है जिसके ख़िलाफ़ यह पाठ तर्क देता है, यानी pretraining-पैमाने का वही अनुशासन जो `llm/finetuning` का अपना विवेक वाला पाठ एक स्तर नीचे लागू करता है, जब adapter fine-tuning भी सही फ़ैसला नहीं होता।

### जब शुरू से pretraining अब भी सही फ़ैसला है

जिन मामलों में वह सचमुच सही है उनमें शामिल हैं: कोई target भाषा या domain किसी भी उपलब्ध base model के training data और tokenizer से इतना बाहर हो कि continued pretraining या fine-tuning की कोई मात्रा अंतर को नहीं पाट सकती; कोई licensing या स्रोत-प्रमाण की शर्त जो हर उपलब्ध base model के training data को बाहर कर दे; या जान-बूझकर किया गया architectural बदलाव (चरण 6 के parallelism चुनाव, मौलिक रूप से अलग attention mechanism) जिसमें मौजूदा checkpoint को बाद में ढाला नहीं जा सकता। ये वह अपवाद हैं जिनके नाम बता पाने की उम्मीद यह पाठ पाठक से करता है, नियम नहीं।

## अभ्यास

1. ▢ एक team ऐसा model चाहती है जो क़ानूनी documents पर अच्छा प्रदर्शन करे, और एक मौजूदा व्यापक-कवरेज वाला base model उपलब्ध है। Gururangan et al. के सबूत के अनुसार, यह पाठ शुरू से नया model pretrain करने से पहले क्या आज़माने की सलाह देगा?

<details markdown="1"><summary>जाँचें</summary>

Domain-adaptive pretraining: मौजूदा base model की pretraining बिना label वाले क़ानूनी text पर जारी रखना, जिसे Gururangan et al. ने ज़्यादा-संसाधन और कम-संसाधन दोनों स्थितियों में target-domain के प्रदर्शन को लगातार सुधारता पाया, नए शुरू-से pretraining run की लागत के छोटे हिस्से पर।

</details>

2. ▢ इस पाठ के अनुसार, इनमें से कौन-सा फिर भी शुरू से pretrain करने का जायज़ कारण है?

    - a) Target domain सामान्य web text से थोड़ा-सा अलग है
    - b) कोई भी उपलब्ध base model का tokenizer या training data target भाषा या domain को बिल्कुल कवर नहीं करता, और continued pretraining उस अंतर को नहीं पाट सकती
    - c) नया pretraining run रिपोर्ट में ज़्यादा प्रभावशाली दिखेगा
    - d) Fine-tuning सेट करने में एक दिन से ज़्यादा लगेगा

<details markdown="1"><summary>जाँचें</summary>

**b)** वही असली अपवाद है जिसे यह पाठ नाम देता है। (a) ठीक वही मामला है जिसे Gururangan et al. का सबूत कहता है कि continued pretraining अच्छी तरह सँभालती है, शुरू से pretrain करने की वजह नहीं। (c) और (d) इस पाठ के लागत-तर्क के तहत बचाव लायक़ कारण नहीं हैं।

</details>

3. ▢ Gururangan et al. के अनुसार domain-adaptive pretraining (DAPT) और task-adaptive pretraining (TAPT) में क्या अंतर है?

<details markdown="1"><summary>जाँचें</summary>

DAPT व्यापक target domain (जैसे सारे biomedical पेपर) के बिना label वाले text पर pretraining जारी रखता है। TAPT ख़ास तौर पर किसी task के अपने बिना label वाले data पर, यानी संकरे corpus पर, pretraining जारी रखता है, और Gururangan et al. ने पाया कि DAPT लगाए जाने के बाद भी वह प्रदर्शन को सुधारता है।

</details>

4. ▢ एक team पूरा domain-adaptive pretraining run नहीं झेल सकती पर फिर भी उसका कुछ फ़ायदा चाहती है। Gururangan et al. का काम कौन-सा विकल्प सुझाता है?

<details markdown="1"><summary>जाँचें</summary>

सरल data-selection रणनीतियों से बने task corpus पर ढालना, जिसे Gururangan et al. ने तब प्रभावी, सस्ता विकल्प पाया जब पूरे domain-adaptive pretraining के संसाधन उपलब्ध नहीं हैं।

</details>

## असली दुनिया का अभ्यास

- [ ] किसी domain-adapted model का प्रकाशित उदाहरण खोजें (कोई "BioBERT", "SciBERT", "FinBERT" या ऐसा ही model card या पेपर) और पहचानें कि वह मौजूदा base model पर continued pretraining से बना था या पूरी तरह शुरू से pretrain हुआ था।
- [ ] Gururangan et al. का introduction (ऊपर linked) पढ़ें और एक वाक्य लिखें कि सामान्य निष्कर्ष निकालने से पहले उन्होंने domain-adaptive pretraining को सिर्फ़ एक नहीं, कई domains में ही क्यों परखा।
- [ ] कल: अपने चुने किसी काल्पनिक target domain या task के लिए, शुरू से नया model pretrain करने के पक्ष या विपक्ष में एक अनुच्छेद लिखें, इस पाठ या इस track के किसी पहले चरण से कम से कम एक सबूत का हवाला देते हुए।

## आगे बढ़ने के लिए

- [पेपर: "Don't Stop Pretraining: Adapt Language Models to Domains and Tasks", Gururangan et al., 2020](https://arxiv.org/abs/2004.10964)
- [`llm/finetuning`](../../finetuning/): वही अनुशासन एक स्तर नीचे लागू, जब continued pretraining भी संकरे task की ज़रूरत से ज़्यादा हो
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
