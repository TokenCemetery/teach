---
title: "27. जब आम जवाब ग़लत हो"
description: "पहचानें कि distillation कब ग़लत फ़ैसला है, और विवादित दावे का निपटारा मुख्य स्रोत से करें"
type: lesson
---

# पाठ 27. जब आम जवाब ग़लत हो

**मिशन से संबंध:** Track इस पर ख़त्म होता है कि distillation पर फ़ैसला लेने और उसे किसी और को समझाने के लिए आप पर भरोसा किया जाए। "बड़े model को छोटे में distil करो" और "forward KL मानक loss है" आम जवाब हैं, और हर एक कुछ सेटिंग्स में सच है और कुछ में झूठ। यह पाठ वे मामले हैं जहाँ distillation ग़लत फ़ैसला है, और पेपर की अपनी तालिकाओं से किसी विवाद को निपटाने की विधि।
**मुख्य स्रोत:** [पेपर: "On the Efficacy of Knowledge Distillation", Cho and Hariharan, 2019](https://arxiv.org/abs/1910.01348), sections 5.1 और 5.2
**पूर्व-आवश्यकताएँ:** [पाठ 19](0019-capacity-gap-and-hidden-traits.md), [पाठ 24](0024-distill-quantize-or-fine-tune.md), [पाठ 26](0026-replacing-a-model-others-depend-on.md), [Capacity gap](../GLOSSARY.md), [Forward KL](../GLOSSARY.md), [Reverse KL](../GLOSSARY.md)

## वार्म-अप

1. ▢ पाठ 5 ने forward और reverse KL की तुलना की। कौन student को teacher के हर mode पर फैलाता है, और कौन एक mode पर टिकता है?

<details markdown="1"><summary>जाँचें</summary>

[Forward KL](../GLOSSARY.md) student को हर mode पर फैलाता है, क्योंकि वह वहाँ कम probability रखने को दंडित करता है जहाँ teacher ज़्यादा रखता है। [Reverse KL](../GLOSSARY.md) एक mode पर टिकता है, क्योंकि वह वहाँ probability रखने को दंडित करता है जहाँ teacher कम रखता है।

</details>

2. ▢ पाठ 16 ने कवर किया कि on-policy distillation प्रति step कितना महँगा है। Teacher को वह क्या करना पड़ता है जो वह तब नहीं करता जब student तय teacher outputs पर train होता है?

<details markdown="1"><summary>जाँचें</summary>

Training के दौरान student द्वारा generate किए sequences के tokens को score करना, इसलिए हर step को ताज़ा student samples और उन पर teacher का forward pass चाहिए। तय teacher outputs एक बार generate होते हैं, और student के training steps teacher का इंतज़ार नहीं करते। [On-policy distillation](../GLOSSARY.md) देखें।

</details>

3. ▢ पाठ 13 ने terms और licenses कवर किए। जिस model के आप मालिक नहीं हैं उससे training data generate करने से पहले आपको क्या जाँचना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

क्या provider के terms या model का license उसके outputs को किसी दूसरे model को train करने के लिए इस्तेमाल करने देता है, और किन शर्तों पर। दोनों बदलने वाले दस्तावेज़ हैं, इसलिए मौजूदा text पढ़ें, उसका सार नहीं।

</details>

## यह जानें

### विधि

आम जवाब अपनी शर्तों के बिना नारे की तरह आता है। पाँच चरण तय करते हैं कि वह आपके लिए सही है या नहीं।

1. **मुख्य स्रोत ढूँढें।** पेपर, उसका हवाला देने वाली post नहीं।
2. **सेटिंग जाँचें।** Models, आकार, data, साल, और क्या मापा गया।
3. **तालिका के पीछे की setup पढ़ें।** Baselines, trials की संख्या, और बताया गया नंबर कैसे चुना गया।
4. **फ़ासले की noise से तुलना करें।** बिना फैलाव का एक-अंक का फ़ासला बहुत कम साबित करता है।
5. **उसे अपने task पर परखें**, जैसा पाठ 23 बताता है।

नीचे के मामलों में से कोई यह नहीं कहता कि distillation बुरा है। हर एक बताता है कि उसका स्रोत क्या समर्थन करता है और कहाँ रुकता है।

### जहाँ आम जवाब विफल होता है

| आम जवाब | ग़लत कब | स्रोत और सीमा |
|---|---|---|
| बड़े model को distil करो | कोई teacher आपके task पर student से बेहतर नहीं है, इसलिए नक़ल करने को कुछ नहीं | R1 पेपर, appendix F: teacher की सीमा से आगे जाने के लिए ज़्यादा मज़बूत base models और बड़े पैमाने के RL चाहिए हो सकते हैं। Gudibande et al. निष्कर्ष निकालते हैं कि open models ज़्यादा imitation data से नहीं, मज़बूत base क्षमताओं से सुधरते हैं। इसके ऊपर मेरा तर्क: नक़ल task पर अपने स्रोत को नहीं हरा सकती |
| उपलब्ध सबसे अच्छा teacher इस्तेमाल करो | Terms या license मना करते हैं | OpenAI के Terms of Use उन चीज़ों में, जो उपयोगकर्ता नहीं कर सकता, प्रतिस्पर्धी models विकसित करने के लिए output इस्तेमाल करना गिनाते हैं। Llama 3.1 license outputs पर train करने देता है पर distribute होने पर नतीजे वाले model के नाम की शुरुआत में "Llama" माँगता है। मौजूदा text पढ़ें |
| बड़ा teacher बेहतर student देता है | Student उसे सोख नहीं सकता, capacity gap | Cho और Hariharan की Table 1, Mirzadeh et al. की Figure 2, Busbridge et al. section 4.2, नीचे |
| Student वह सोख सकता है जो teacher जानता है | Task को ऐसा ज्ञान चाहिए जो student रख नहीं सकता | Gudibande et al.: imitation ने style और instruction following सुधारे पर तथ्यात्मकता, coding या problem solving नहीं, imitation data बढ़ने के साथ Natural Questions के नतीजे पीछे जाते हुए |
| Teacher outputs पर एक बार fine-tune करो | Student की अपने samples पर on-policy training बेहतर करती है | Agarwal et al. section 4.1: उनके summarization ablations में on-policy और mixed रूप supervised वालों से लगातार बेहतर रहे, और GSM8K पर on-policy GKD ने बाक़ी तरीक़ों को काफ़ी पीछे छोड़ा (Figure 9, section 4.3)। प्रति step इसकी लागत ज़्यादा है (पाठ 16) |
| Quantize करने के बजाय distill करो | Model को quantize करने से बजट पहले ही पूरा हो जाता है | Quantization शीट Kurtic et al. में हर आकार पर W8A8-FP को प्रभावी रूप से lossless बताती है, एक model परिवार पर: उसकी [review checklist शीट](../../quantization/reference/quantization-review-checklist.md) देखें |
| छोटे को सीधे train करने के बजाय distill करो | बहुत सारा task data और कोई मुफ़्त teacher नहीं | Busbridge et al.: पर्याप्त student compute या tokens दिए जाने पर supervised learning, distillation को हराती है। यह pretraining का नतीजा है, इसलिए task fine-tuning के लिए अनुमान (पाठ 24) |

दो पंक्तियाँ track की अपनी उम्मीदों के उलट चलती हैं। R1 पेपर distillation को उसी 32B base पर RL से जीतता पाता है (पाठ 24), इसलिए "छोटे model पर RL जीतता है" ऐसा मामला नहीं है जिसका यह पाठ समर्थन कर सके, और इस पाठ के लिए पढ़ा कोई स्रोत नहीं दिखाता कि मानव data पर सादा fine-tuning किसी task पर distillation को हराता है। दोनों तालिका से बाहर रहते हैं।

### Capacity gap, तालिकाओं से

Cho और Hariharan ने ImageNet student, ResNet18, को तीन teachers के साथ चलाया (Table 1, top-1 error, कम बेहतर है)। Student को शून्य से train करने पर 30.24 मिला। ResNet18, ResNet34 और ResNet50 teachers के साथ, जिनकी अपनी errors 30.24, 26.70 और 23.85 थीं, students ने 30.57, 30.79 और 30.95 score किए। Teacher जितना बेहतर हुआ student उतना बदतर हुआ, और हर distilled student बिना teacher के train हुए student से बदतर था। Text कहता है कि ResNet152 भी एक teacher था, पर जो तालिका मैंने पढ़ी वह तीन पंक्तियाँ गिनाती है। लेखक CIFAR-10 का एक संस्करण भी बताते हैं जिसमें teacher के बढ़ने पर student की accuracy बढ़ती है और फिर गिरती है, और यह कि ऊँचे temperature से teacher की probabilities को नरम करने से यह नतीजा नहीं बदला (section 5.1)।

Mirzadeh et al. CIFAR-10 और CIFAR-100 पर 4, 6, 8 और 10 layers वाले teachers के तहत 2-layer CNN student के लिए वही बढ़त और गिरावट दिखाते हैं, और तीन प्रतिस्पर्धी कारक देते हैं, तीसरा यह कि ज़्यादा निश्चित teacher कम नरम targets देता है (Figure 2)। Busbridge et al. language models के लिए प्रभाव को fit करते हैं: student cross-entropy teacher के आकार के साथ एक इष्टतम तक घटती है और फिर बढ़ती है, और वे तर्क देते हैं कि gap सीखने की क्षमता, hypothesis space और optimize करने की योग्यता का है, जिनका सापेक्ष आकार एक विशेष मामला है (sections 1 और 4.2, Figure 4)।

तीन स्रोत, तीन सेटिंग्स, एक दिशा। उनमें से कोई भी आपके models का जोड़ा नहीं है, इसलिए "बड़ा हमेशा बेहतर नहीं" एक आकार छोटे teacher को परखने का कारण है, यह नियम नहीं कि सबसे बड़ा ग़लत है।

### विवाद का निपटारा: "forward KL मानक loss है"

एक सहकर्मी कहता है कि forward KL मानक है। उन पेपरों से शुरू करें जिन्होंने उसे परखा और पढ़ें कि हर एक ने क्या मापा।

| स्रोत | सेटिंग | क्या मापा गया | नतीजा |
|---|---|---|---|
| Busbridge et al., appendix G.5, Table 7 | 1.82B teacher से 546M student, C4 | Data cross-entropy, कम बेहतर है | Forward 2.42, reverse 2.70 |
| Muralidharan et al. (Minitron), appendix A.3, Table 16 | Minitron 8B depth-pruned, distillation से दोबारा train | Validation sets पर LM loss | Forward KL 2.155, reverse KL 2.665 |
| Gu et al. (MiniLLM), abstract | Instruction following, GPT-2 और OPT students | GPT-4 feedback और दूसरे माप | Reverse KL अधिक उपयुक्त बताया गया और students की गुणवत्ता ऊँची |
| Agarwal et al. section 4.4 | FLAN-T5-XL से base, instruction tuning, MMLU और BBH | Held-out tasks पर few-shot score | Reverse KL के साथ on-policy, forward KL से काफ़ी बेहतर |
| Agarwal et al. section 4.1 | XSum summarization, T5 students | गुणवत्ता बनाम विविधता | सबसे अच्छा divergence task और sampling पर निर्भर था: mode-seeking ने temperature sampling के साथ बेहतर किया, और greedy decoding के तहत चुनाव का मुश्किल से असर था |

Columns में नीचे पढ़ें। पहले दो text पर loss मापते हैं, pretraining के क़रीब की सेटिंग्स में, और forward KL जीतता है। आख़िरी तीन instruction-following या summarization outputs की गुणवत्ता मापते हैं, और reverse KL जीतता है या विजेता decoding पर निर्भर है। Minitron का अपना text बँटवारे का नाम लेता है: वह reverse KL को instruction following के लिए बेहतर बैठने वाला और task निर्भरता के लिए Agarwal et al. का हवाला देता है, और अपने pruned base model के लिए forward KL को सबसे अच्छा पाता है।

एक पढ़त, जो मेरा अनुमान है और इन पेपरों ने नहीं परखी, यह है कि text पर loss वाला metric उस divergence का पक्ष लेता है जो उस loss के सबसे क़रीब है, और output-गुणवत्ता वाला metric उसका जो कम-probability वाली continuations से बचता है। तालिकाएँ जो समर्थन करती हैं वह छोटा है और काफ़ी है: "forward KL मानक है" यहाँ पढ़ी pretraining-जैसी सेटिंग्स के लिए सच है, दूसरों में झूठ, और दावे को अपनी सेटिंग साथ रखनी होगी। Instruction-tuned student के लिए, इन तालिकाओं का सबूत आपकी अपनी decoding के तहत reverse KL को भी परखने की ओर इशारा करता है।

ध्यान दें कि किसने निपटारा किया। किसी ने याददाश्त से नहीं पूछा। जवाब हर स्रोत की तालिका ढूँढने, यह पढ़ने कि संख्या किस चीज़ की संख्या थी, और यह देखने से आया कि सेटिंग्स साफ़ बँटती हैं।

## अभ्यास

1. ▢ Cho और Hariharan की Table 1 से, अनुमान लगाएँ कि तीन teachers में से कौन सबसे अच्छा student देता है और क्या कोई distilled student शून्य से training को हराता है, फिर चलाएँ।

    ```python
    scratch = 30.24
    for teacher, teacher_err, student_err in [
        ("ResNet18", 30.24, 30.57),
        ("ResNet34", 26.70, 30.79),
        ("ResNet50", 23.85, 30.95),
    ]:
        print(f"{teacher:9s} teacher {teacher_err:5.2f} student {student_err:5.2f} vs scratch {student_err - scratch:+.2f}")
    ```

<details markdown="1"><summary>संकेत</summary>

हर student की error की तुलना 30.24 से करें, यानी बिना teacher के train हुए student की error।

</details>

<details markdown="1"><summary>जाँचें</summary>

ResNet18 teacher सबसे अच्छा student देता है, 30.57, और हर student शून्य से बदतर है: error के 0.33, 0.55 और 0.71 अंक से। सबसे सटीक teacher ने सबसे बदतर student दिया। यह एक student वाली एक ImageNet setup है, इसलिए यह "बड़ा हमेशा बेहतर" का प्रति-उदाहरण है, कहीं और असर के आकार का माप नहीं।

</details>

2. ▢ एक टीम hosted model को ऐसे model में distil करने की योजना बनाती है जिसे वह बेचेगी। Provider के terms provider से होड़ करने वाले models विकसित करने के लिए output इस्तेमाल करने की मनाही करते हैं। आप क्या सुझाते हैं?

<details markdown="1"><summary>जाँचें</summary>

उस product के लिए उस teacher के साथ आगे न बढ़ें, और दूसरा रास्ता खोजें: ऐसा teacher जिसका license अनुमति दे, लोगों का लिखा data, या वह model quantize करना जो उनके पास पहले से है। अगर विकल्प Llama 3.1 जैसा open model है, तो उसका license outputs पर training की अनुमति देता है पर नतीजे वाले model के नाम को "Llama" से शुरू करना और distribute होने पर "Built with Llama" दिखाना माँगता है, इसलिए मौजूदा license text को product योजना के विरुद्ध पढ़ें। कोई दस्तावेज़ क़ानूनी राय नहीं है, इसलिए ship करने से पहले वकील से पूछें।

</details>

3. ▢ एक सहकर्मी कहता है "forward KL मानक loss है, इसलिए इसे हमारे instruction-tuned student के लिए इस्तेमाल करें"। तालिका से जवाब दें।

<details markdown="1"><summary>जाँचें</summary>

Forward KL वहाँ जीता जहाँ metric pretraining-जैसी सेटिंग्स में text पर loss था (Busbridge et al., Minitron), और reverse KL जीता या विजेता decoding पर निर्भर था जहाँ instruction following या summarization के output की गुणवत्ता metric थी (MiniLLM, Agarwal et al.)। आपका student instruction-tuned है, इसलिए वहाँ का सबूत default की ओर नहीं, आपकी decoding के तहत दोनों को परखने की ओर इशारा करता है।

</details>

4. ▢ कौन-सा सबूत तय करेगा कि capacity gap आपके teacher और student पर लागू होता है या नहीं?

    - a) Convergence पर student का training loss curve
    - b) Public leaderboards पर teacher के अपने scores
    - c) दो teacher आकारों के तहत आपके student का score
    - d) किसी दूसरे model परिवार की रिपोर्ट करता पेपर

<details markdown="1"><summary>जाँचें</summary>

**c)** यह वही experiment है जो तीनों पेपरों ने चलाया, आपके जोड़े और आपके task पर। (b) teacher की गुणवत्ता है, और Cho और Hariharan दिखाते हैं कि teacher की बढ़ती गुणवत्ता student की गिरती गुणवत्ता के साथ मौजूद थी। (a) training signal है, task की गुणवत्ता नहीं। (d) दिखाता है कि असर कहीं और मौजूद है, आपके लिए नहीं।

</details>

5. ▢ Mirzadeh et al. CIFAR-10 पर ResNet के लिए (Table 1), सादे distillation के लिए 88.65 और अपनी teacher assistant विधि के लिए 88.98 बताते हैं, और कहते हैं कि हर बताई संख्या 120 trials में hyperparameter optimizer द्वारा पहुँची सबसे अच्छी top-1 test accuracy है। 0.33 के फ़ासले के बारे में आप क्या कहेंगे?

<details markdown="1"><summary>जाँचें</summary>

कई trials में सबसे अच्छी test accuracy चुनना दोनों तरीक़ों के पक्ष में जाता है, और तालिका कोई फैलाव नहीं दिखाती, इसलिए अकेली इस तालिका से तिहाई अंक को जीत नहीं कहा जा सकता। यह इसका सबूत नहीं कि विधि विफल है: उसी तालिका के बड़े फ़ासले, जैसे ImageNet पर 66.60 बनाम 67.36, देखने की बेहतर जगह हैं, उसी चेतावनी के साथ। Seeds तय करके बार-बार runs माँगें और test accuracy को चुनने के लिए इस्तेमाल न करें।

</details>

## असली दुनिया का अभ्यास

- [ ] Distillation का कोई अंगूठा-नियम चुनें जिस पर आप निर्भर हैं (उदाहरण के लिए "सबसे बड़ा teacher इस्तेमाल करो") और उसे पेपर तक खोजें। Models, आकार, साल, क्या मापा गया और आपका मामला कहाँ अलग है, लिखें।
- [ ] Distillation Scaling Laws पेपर की Table 7 और Minitron पेपर का appendix A.3 खोलें और उनके तथा MiniLLM के बीच setup के अंतर एक-एक पंक्ति में लिखें, ताकि आप अगली "कौन-सा loss" बहस का जवाब तालिकाओं से दे सकें।
- [ ] कल: जो distillation आप सबसे ज़्यादा चलाना चाहेंगे उसके लिए, ऊपर की तालिका का वह एक मामला लिखें जो सबसे ज़्यादा लागू होने की संभावना रखता है, और वह माप जो दिखाएगा कि वह लागू होता है या नहीं।

## आगे बढ़ने के लिए

- [Distillation Review Checklist शीट](../reference/distillation-review-checklist.md)
- [पेपर: "On the Efficacy of Knowledge Distillation", Cho and Hariharan, 2019](https://arxiv.org/abs/1910.01348)
- [पेपर: "Improved Knowledge Distillation via Teacher Assistant", Mirzadeh et al., 2019](https://arxiv.org/abs/1902.03393)
- [पेपर: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606)
- [पेपर: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
- [पेपर: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Post-training ट्रैक](../../post-training/)
- [संसाधन](../RESOURCES.md)

---

यह track का अंत है, और जिस आदत के लिए इसे बनाया गया वही इस पाठ में है: distilled model एक teacher, एक student, एक loss, एक data set और tasks के एक सेट के बारे में दावा है, इसलिए खोजें कि दावा कहाँ से आता है, जाँचें कि उसने क्या कवर किया, और किसी और के सामने उसका बचाव करने से पहले अपने tasks पर मापें।

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
