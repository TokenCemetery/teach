---
title: "1. Base Model असल में क्या है"
description: "Model एक ही next-token function है; base का मतलब instruct नहीं"
type: lesson
---

# पाठ 1. Base Model असल में क्या है

**मिशन से संबंध:** जब तक आप ठीक-ठीक नहीं जानते कि model को अकेला छोड़ देने पर वह क्या करता है, तब तक आप यह नहीं परख सकते कि fine-tuning सही जवाब है या नहीं।
**मुख्य स्रोत:** [LLM Visualization, Brendan Bycroft](https://bbycroft.net/llm)
**पूर्व-आवश्यकताएँ:** कोई नहीं, यह पहला पाठ है।

## यह जानें

Language model एक function है। यह token IDs की एक sequence लेता है और अपनी vocabulary के हर token के लिए एक score लौटाता है, जो बताता है कि आगे क्या आ सकता है। पूरा ऑपरेशन बस यही है। Chat, tool calls, refusals, reasoning traces: सब कुछ इसी एक next-token step के ऊपर बना है।

इन कच्चे scores को **logits** कहते हैं। Softmax इन्हें probability distribution में बदल देता है। एक sampler उस distribution से एक token चुनता है, वह token sequence में जुड़ जाता है, और function फिर चलता है। Text एक-एक token करके सामने आता है, और इसके अलावा कुछ और नहीं हो रहा।

आगे की हर चीज़ के लिए दो नतीजे मायने रखते हैं।

**Inference के दौरान weights नहीं बदलते।** जब लगता है कि model को बातचीत में पहले की कोई बात याद है, तो वह याद उन tokens में है जो उसकी context window में पड़े हैं, model में हुआ कोई बदलाव नहीं। इस workspace में weights को बदलने वाली अकेली चीज़ fine-tuning है, और वह offline होती है, serving से पहले।

**Sampling model नहीं है।** Temperature, top-p और top-k, model के distribution बना लेने के बाद उसका आकार बदलते हैं। अगर temperature बदलने पर output की गुणवत्ता बदलती है, तो आपने अपने sampler के बारे में कुछ सीखा, अपने weights के बारे में नहीं। Training को कुछ भी श्रेय देने से पहले sampling को स्थिर रखें।

### Base बनाम instruct

**Base** model को सिर्फ़ एक objective पर train किया गया है: बहुत बड़े corpus में अगला token predict करना। वह सवालों के जवाब नहीं देता। उसे `What is the capital of France?` दिया जाए तो हो सकता है वह तीन और परीक्षा-सवालों के साथ आगे बढ़ जाए, क्योंकि उसके training data में आसपास का text ऐसा ही दिखता था।

**Instruct** या **chat** model वह base model है जिसे instructions और responses के जोड़ों पर आगे train किया गया है, यानी supervised fine-tuning, और उसके बाद आम तौर पर मानव या model की पसंद के data पर। Instruction-following का जो व्यवहार आप मानकर चलते हैं, वह एक train की गई परत है, architecture का गुण नहीं।

![वही सवाल एक base model और उसी base में instruction tuning जोड़कर बने model को दिया जा रहा है। Base और परीक्षा-सवालों के साथ आगे बढ़ता है; tuned वाला जवाब देता है।](images/one-prompt-two-continuations.svg)

एक prompt, दो continuations, और दोनों के नीचे वही next-token function। दूसरा डिब्बा पहला डिब्बा और training है, और फ़र्क़ वहीं रहता है।

आप किससे शुरू करें, यह एक असली फ़ैसला है:

| शुरुआती बिंदु | आपको विरासत में मिलता है | आपको देना पड़ता है |
|---|---|---|
| Base | कच्ची भाषा-क्षमता के सिवा कुछ नहीं | हर formatting और व्यवहार की परिपाटी |
| Instruct | Formatting, instruction following, refusal व्यवहार | सिर्फ़ आपका task, पर जो पहले से है उसके बिगड़ने का जोखिम |

ज़्यादातर adapter fine-tuning instruct model से शुरू होती है, क्योंकि छोटे dataset पर instruction following को शून्य से दोबारा बनाना घाटे का सौदा है। क़ीमत यह है कि आपका training data अब उस training से होड़ करता है जो vendor पहले कर चुका है, और आगे चलकर [catastrophic forgetting](../GLOSSARY.md) इसी होड़ से आती है।

### Training का संकेत

Training के दौरान model को एक असली sequence दिखाई जाती है और यह आँका जाता है कि असल में आए token को उसने कितनी probability दी थी। यह score **cross-entropy loss** है। कम loss का मतलब है कि model को असली continuation हैरान करने वाली नहीं लगी।

एक चेतावनी याद रखें, क्योंकि चरण 6 उसी पर बना है: loss उस text पर अगले token की हैरानी मापता है जो आपके पास पहले से है। यह नहीं मापता कि model काम का है या नहीं।

## अभ्यास

1. ▢ एक वाक्य में, "understand" शब्द के बिना, बताएँ कि language model क्या compute करता है।

<details markdown="1"><summary>जाँचें</summary>

Tokens की एक sequence दिए जाने पर, वह vocabulary के हर token के लिए एक score बनाता है जो बताता है कि आगे क्या आ सकता है।

ग़लत सहज उत्तर function के बजाय generation का वर्णन करना है ("यह text लिखता है")। Generation उस function के चारों ओर लिपटा एक loop है, जो weights के बाहर लागू होता है। दोनों को अलग रखना ही आपको यह सोचने देता है कि समस्या कहाँ रहती है।

</details>

2. ▢ आप एक model को दो बार एक ही input देते हैं और दो अलग जवाब पाते हैं। दो जगहें बताएँ जहाँ से फ़र्क़ आ सकता है, और कहें कि इनमें से किसमें weights शामिल हैं।

<details markdown="1"><summary>जाँचें</summary>

Sampler (शून्य से ऊपर का temperature उसी distribution से अलग tokens चुनता है) और context (अलग system prompt, या बातचीत का इतिहास जो आप भूल गए थे कि वहाँ है)। दोनों में weights शामिल नहीं हैं।

Inference पर weights frozen होते हैं। अगर आपने उन्हें नहीं बदला, तो वे स्पष्टीकरण नहीं हो सकते, और यह मानने से पहले सबसे पहले इसी को ख़ारिज करना चाहिए कि model असंगत है।

</details>

3. ▢ आप एक base model को prompt `Summarise this article:` और उसके बाद एक article देते हैं, और वह सार के बजाय एक और article बना देता है। क्या model टूटा हुआ है?

<details markdown="1"><summary>जाँचें</summary>

नहीं। वह ठीक अपना काम कर रहा है: संभावित text को आगे बढ़ाना। उसके training corpus में किसी article के बाद सार आने के मुक़ाबले और article आना कहीं ज़्यादा आम है।

Instruction following एक सिखाया गया व्यवहार है। Base model से इसकी उम्मीद रखना शुरुआती दौर की सबसे आम भूल है, और अक्सर इसका ग़लत निदान ख़राब model या ख़राब prompt के रूप में होता है।

</details>

4. ▢ Fine-tuning इनमें से क्या बदलती है?

    - a) Serving के समय इस्तेमाल होने वाला sampling temperature
    - b) Model के weights के अंदर store की गई संख्यात्मक values
    - c) Model की context window में मौजूद tokens
    - d) वह vocabulary size जिससे model पहले बनाया गया था

<details markdown="1"><summary>जाँचें</summary>

**b)** Model के weights के अंदर store की गई संख्यात्मक values।

Temperature serving के समय का knob है। Context हर request का input है। Vocabulary size tokenizer और embedding matrix से तय होती है, और उसे बदलना fine-tuning से कहीं ज़्यादा दख़ल वाला ऑपरेशन है। Training सिर्फ़ weight values को हिलाती है।

</details>

5. ▢ Base model के बजाय instruct model को fine-tune करने की एक वजह बताएँ, और उलटा करने की एक वजह।

<details markdown="1"><summary>जाँचें</summary>

Instruct से तब शुरू करें जब आप instruction following और सामान्य मददगारी को बनाए रखना चाहते हों जिसे आप छोटे dataset से दोबारा खड़ा नहीं कर सकते, जो लगभग हमेशा होता है।

Base से तब शुरू करें जब आपके task का output format सामान्य chat से इतना अलग हो कि विरासत में मिला chat व्यवहार सक्रिय रूप से आड़े आए: कठोर structured output, एक अकेला classification label, या ऐसा domain notation जहाँ बातचीत की भराई सिर्फ़ शोर है।

</details>

## असली दुनिया का अभ्यास

- [ ] कोई भी model चलाएँ जिस तक आप local रूप से या API से पहुँच सकते हैं। एक prompt temperature 0 पर दो बार भेजें, फिर temperature 1 पर दो बार। लिख लें कि कौन-सी जोड़ी मेल खाई और क्यों।
- [ ] Hugging Face Hub पर ऐसा model ढूँढें जिसका base और instruct, दोनों variant हों। दोनों model cards पढ़ें और ध्यान दें कि instruct वाला card क्या जोड़ा गया बताता है।
- [ ] कल: किसी base model को सीधा सवाल दें और दर्ज करें कि वह जवाब देने के बजाय क्या करता है। Output सँभालकर रखें। यह विफलता आप चरण 6 में फिर पहचानेंगे।

## आगे बढ़ने के लिए

- [LLM Visualization, Brendan Bycroft](https://bbycroft.net/llm): एक अकेले token के रास्ते पर शुरू से अंत तक click करके चलें
- [The Illustrated Transformer, Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [शब्दावली](../GLOSSARY.md): इस workspace में `fine-tuning` का मतलब हमेशा frozen-base वाला प्रकार होता है
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
