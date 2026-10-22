---
title: "10. Generated Data से Distillation"
description: "Teacher की generations से instruction set बनाना, जैसा Self-Instruct और Alpaca ने किया"
type: lesson
---

# पाठ 10. Generated Data से Distillation

**मिशन से संबंध:** मिशन आपसे माँगता है कि आप teacher के generate किए data से distill करें, यानी outputs इकट्ठा करने के साथ inputs भी बनाएँ, और जानें कि इस निर्माण की क्या क़ीमत है।
**मुख्य स्रोत:** [पेपर: "Self-Instruct: Aligning Language Models with Self-Generated Instructions", Wang et al., 2022](https://arxiv.org/abs/2212.10560)
**पूर्व-आवश्यकताएँ:** [पाठ 9](0009-token-or-sequence.md), [Synthetic data](../GLOSSARY.md), [Sequence-level distillation](../GLOSSARY.md), [Teacher](../GLOSSARY.md), [Student](../GLOSSARY.md)

## वार्म-अप

1. ▢ Kim और Rush की विधि में inputs कहाँ से आए, और teacher ने क्या जोड़ा?

<details markdown="1"><summary>जाँचें</summary>

Inputs मौजूदा training वाक्य थे। Teacher ने सिर्फ़ outputs जोड़े: हर input का उसका beam-search translation। Student इन input और output जोड़ों पर train हुआ (पाठ 8)।

</details>

2. ▢ एक teacher API के पीछे है और सिर्फ़ text लौटाता है। Distillation का कौन-सा level आपके लिए खुला है?

<details markdown="1"><summary>जाँचें</summary>

Sequence level, उस text पर जो आप इकट्ठा कर सकते हैं (पाठ 9)। Token level को हर position पर teacher का distribution चाहिए, जो अकेला text नहीं देता।

</details>

## यह जानें

### Generated-data distillation, एक और चुनाव वाला sequence-level distillation है

पाठ 8 में inputs दिए हुए थे: एक translation task का training set। सामान्य instruction model के लिए inputs का कोई तय सेट नहीं होता। किसी को prompts लिखने होते हैं।

Generated-data distillation वह [sequence-level distillation](../GLOSSARY.md) है जिसमें आप inputs भी चुनते हैं। Prompts teacher लिखता है या आप, उत्तर teacher लिखता है, और student जोड़ों पर सादे cross-entropy से train होता है। Student को जो कुछ मिलता है उसका हर पहलू उसी data से तय होता है: student सिर्फ़ वे व्यवहार सीख सकता है जो जोड़े दिखाते हैं।

### Self-Instruct: pipeline

Self-Instruct (Wang et al., 2022) model की अपनी generations से instruction set बनाता है, 175 मानव-लिखित seed tasks से शुरू करके, हर एक में एक instruction और एक instance। इसके चार चरण हैं (section 2.2):

1. **Instructions generate करें।** Task pool से 8 instructions in-context examples के रूप में sample करें, उनमें 6 मानव-लिखित और 2 पहले के rounds में generate हुए, और model से नए माँगें।
2. **Task को वर्गीकृत करें।** Model से, कुछ examples (12 classification और 19 non-classification seed instructions) के साथ, पूछें कि instruction classification task है या नहीं, यानी ऐसा जिसके outputs का छोटा, सीमित सेट हो।
3. **Instances generate करें।** ज़्यादातर tasks के लिए, पहले input: एक input लिखें, फिर output। Classification tasks के लिए, पहले output: class label लिखें, फिर उस label के लिए एक input। लेखकों ने यह इसलिए जोड़ा क्योंकि input-first generation ने किसी एक label की ओर झुके inputs बनाए, उदाहरण के लिए grammar-error task के लिए व्याकरणिक रूप से सही वाक्य।
4. **Filter करें।** नया instruction तभी रखें जब pool में पहले से मौजूद हर instruction के साथ उसकी ROUGE-L समानता 0.7 से नीचे हो। ऐसे keywords वाले instructions हटा दें, जैसे image, picture या graph, जिन्हें language model सँभाल नहीं सकता। दोहराए गए instances हटाएँ और वे instances भी जिनका input वही है पर outputs अलग। वे instances हटाएँ जो सरल heuristics में फेल हों, जैसे बहुत लंबा या बहुत छोटा instruction, या ऐसा output जो बस input को दोहराता हो।

लूप वापस खिलाता है: स्वीकृत instructions pool में जुड़ जाते हैं और बाद के rounds के लिए in-context examples बन जाते हैं। Filtering के नियम पाठ 12 का विषय हैं।

GPT-3 `davinci` model पर नतीजा, filtering के बाद 52,445 instructions और 82,439 instances था, जिनमें से 11,584 instructions classification tasks थे (Table 1)। इस सबका GPT-3 पर fine-tuning provider की fine-tuning सेवा के ज़रिए $338 की पड़ी (appendix A.3)। उसी model ने data generate किया और फिर उसी पर fine-tune हुआ, इसलिए teacher और student एक ही model से शुरू हुए।

उनका evaluation, SuperNI के अनदेखे tasks पर ROUGE-L से मापा गया (Table 3): vanilla GPT-3 ने 6.8, Self-Instruct model ने 39.9, और OpenAI के instruction-tuned model InstructGPT001 ने 40.8 score किया। लेखक इसे 33.1 अंक के फ़ायदे के रूप में पढ़ते हैं जो InstructGPT001 के लगभग बराबर है। यह उनका अपने benchmark और metric पर नतीजा है।

### Alpaca: वही विधि छोटे पैमाने पर

Stanford CRFM टीम ने Alpaca को Self-Instruct के विचार से बनाया, पर teacher और student बदल दिए (Alpaca blog post, "Training recipe"):

- उन्होंने वही 175 seed जोड़े लेकर शुरू किया और OpenAI के text-davinci-003 से और generate करवाए।
- उन्होंने Self-Instruct के मुक़ाबले generation pipeline को सरल किया, और कहते हैं कि इससे लागत घटी।
- Data outputs सहित 52K अनोखे instructions है, जिसकी लागत OpenAI API से $500 से कम रही।
- उन्होंने LLaMA 7B को supervised learning से fine-tune किया। पहले run में 8 80GB A100s पर 3 घंटे लगे, जिसे वे ज़्यादातर cloud providers पर $100 से कम बताते हैं।

उनकी सार-पंक्ति यह है कि Alpaca 7B को $600 से कम में दोहराया जा सकता है। प्रारंभिक single-turn evaluation पर वे बताते हैं कि वह text-davinci-003 जैसा ही गुणात्मक रूप से बर्ताव करता है। इसे छोटे evaluation पर लेखकों की धारणा मानें, मापा हुआ मेल नहीं; पाठ 18 लौटकर बताता है कि ऐसी धारणाएँ भटका क्यों सकती हैं।

| | Self-Instruct | Alpaca |
|---|---|---|
| Teacher | GPT-3 `davinci` (वही model जिसे बाद में fine-tune किया गया) | text-davinci-003 |
| Student | GPT-3 `davinci` | LLaMA 7B |
| Seed set | 175 tasks | वही 175 जोड़े |
| Data | 52,445 instructions, 82,439 instances | outputs सहित 52K instructions |
| बताई गई लागत | Fine-tune के लिए $338 | Data के लिए $500 से कम, run के लिए $100 से कम |

### Data की रचना क्या तय करती है

चार चुनाव तय करते हैं कि student क्या सीखता है, और data generate करते समय हर एक आपका है:

- **Seed set.** सब कुछ 175 examples से generate होता है, इसलिए वे जो कवर करते हैं वही सीमा तय करता है कि pool किस दिशा में बढ़ेगा।
- **Prompt.** In-context examples और template style और task के मिश्रण को दिशा देते हैं।
- **Sampling settings.** Temperature और ऐसी settings तय करती हैं कि outputs कितने विविध हैं।
- **Filter.** जो आप रखते हैं वही training set है। कमज़ोर filter teacher की ग़लतियों को student के सबक़ बनने देता है।

Student सिर्फ़ वही मिला सकता है जो teacher ने लिखा, इसलिए जो ग़लती filter से बच जाए वह ऐसे सीखी जाती है मानो सही हो।

### Data के साथ पाबंदियाँ भी आईं

Alpaca की post साफ़ कहती है कि model सिर्फ़ academic research के लिए है। वह तीन कारण देती है: LLaMA का license non-commercial है, data text-davinci-003 से आता है जिसकी शर्तें OpenAI से होड़ करने वाले models विकसित करने की मनाही करती हैं, और उन्होंने पर्याप्त सुरक्षा उपाय नहीं बनाए थे। पाठ 13 इन पाबंदियों को क़रीब से पढ़ता है। अभी बस यह ध्यान दें कि data की लागत उस सबका छोटा हिस्सा थी जिसके साथ वह आया।

## अभ्यास

1. ▢ Alpaca के data पर 52K instruction और output जोड़ों के लिए $500 से कम ख़र्च हुए। प्रति example अधिकतम लागत क्या है, और वह model की पूरी लागत क्यों नहीं है?

<details markdown="1"><summary>जाँचें</summary>

$500 से कम को 52,000 से भाग देने पर लगभग $0.0096 आता है, प्रति example एक सेंट से कम। यह पूरी लागत नहीं है: blog fine-tuning run को अलग से गिनता है (8 80GB A100s पर 3 घंटे, ज़्यादातर clouds पर $100 से कम), और कोई आँकड़ा 175 seeds, evaluation या demo के मानव प्रयास को नहीं गिनता। पाठ 21 teacher की लागत को ठीक से गिनता है।

</details>

2. ▢ Self-Instruct classification data को पहले output से generate करता है। इससे input-first generation की कौन-सी समस्या ठीक होती है?

    - a) Inputs किसी एक class label की ओर झुके निकलते हैं
    - b) Outputs किसी भी मानव उत्तर से कहीं लंबे निकलते हैं
    - c) Instructions बिना किसी बदलाव के वही input text दोहराते हैं
    - d) Labels बेहद असंगत format में लिखे निकलते हैं

<details markdown="1"><summary>जाँचें</summary>

**a)** पेपर का उदाहरण: grammar-error detection के लिए input लिखने को कहने पर model व्याकरणिक रूप से सही input लिखने की ओर झुकता है, इसलिए एक class हावी रहती है। पहले label और फिर उस label के लिए input लिखने से वे संतुलित होते हैं। (b), (c) और (d) वह समस्या नहीं हैं जिसका लेखक नाम लेते हैं।

</details>

3. ▢ एक नए generate किए instruction की pool के एक मौजूदा instruction के साथ ROUGE-L समानता 0.74 है और बाक़ी सबके साथ 0.2। क्या Self-Instruct उसे रखता है, और क्यों?

<details markdown="1"><summary>संकेत</summary>

नियम pool पर अधिकतम के बारे में है, औसत के बारे में नहीं।

</details>

<details markdown="1"><summary>जाँचें</summary>

नहीं। Instruction तभी रखा जाता है जब किसी भी मौजूदा instruction के साथ उसकी ROUGE-L समानता 0.7 से नीचे हो, और 0.74 उससे ऊपर है। नियम pool को विविध रखता है, किसी एक सदस्य की लगभग-नक़ल को ठुकराकर, चाहे pool का बाक़ी हिस्सा कितना भी अलग हो।

</details>

4. ▢ आपकी टीम Alpaca की नक़ल करना चाहती है पर ऐसे teacher के साथ जो छोटे, रूखे उत्तर देता है। आप student से क्या करने की उम्मीद करते हैं, और pipeline का कौन-सा हिस्सा सबसे पहले बदलेंगे?

<details markdown="1"><summary>जाँचें</summary>

उम्मीद करें कि student उसी रूखे style में उत्तर देगा, क्योंकि वह वही सीख सकता है जो जोड़े दिखाते हैं। सबसे पहले prompt या teacher की settings बदलें, क्योंकि उत्तर का style वहीं तय होता है, फिर filter दोबारा चलाएँ और training से पहले generate किए जोड़ों के नमूने को आँख से तुलना करें। यह इस बात से निकली भविष्यवाणी है कि data student को कैसे तय करता है, मापा हुआ नतीजा नहीं।

</details>

5. ▢ पाठ 8 ने पाया कि teacher के अकेले सबसे अच्छे output पर train हुआ sequence-level student उसी output के आसपास नुकीला हो जाता है। क्या यह हर prompt के लिए कई outputs generate करने का सुझाव देता है, या एक, और हर एक की क्या क़ीमत होगी?

<details markdown="1"><summary>जाँचें</summary>

यह मामला तय नहीं करता। हर prompt पर एक output mode-शैली का तरीक़ा है: सस्ता और संगत, पर एक अकेला sample। हर prompt पर कई outputs student को teacher की ज़्यादा विविधता दिखाते हैं, generation लागत के कई गुना पर और ज़्यादा filtering के साथ। Kim और Rush ने translation पर mode की जगह sampling आज़माई और mode रखा। वह उनके task का नतीजा है, इसलिए दोनों को अपने पर परखें।

</details>

## असली दुनिया का अभ्यास

- [ ] Self-Instruct पेपर खोलें और instruction generation का prompt template ढूँढें (Table 5)। लिखें कि in-context examples कैसे दिखते हैं और मानव तथा model-लिखित कितने हैं।
- [ ] Alpaca blog post खोलें और वह वाक्य ढूँढें जो research-only release के तीन कारकों को सूचीबद्ध करता है। लिखें कि उनमें से कौन-सा आपके teacher के चुनाव पर निर्भर है।
- [ ] कल: Self-Instruct pipeline के चार चरण और filter की सीमा बिना नोट्स के लिखें, फिर पेपर से मिलाएँ।

## आगे बढ़ने के लिए

- [Sequence और Synthetic Data शीट](../reference/sequence-and-synthetic-data.md)
- [पेपर: "Self-Instruct: Aligning Language Models with Self-Generated Instructions", Wang et al., 2022](https://arxiv.org/abs/2212.10560)
- [लेख: "Alpaca: A Strong, Replicable Instruction-Following Model", Stanford CRFM, 2023](https://crfm.stanford.edu/2023/03/13/alpaca.html)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
