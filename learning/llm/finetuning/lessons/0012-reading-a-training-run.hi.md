---
title: "12. Training Run को पढ़ना"
description: "Curve के आकार से diagnosis, और वह जो loss देख नहीं सकता"
type: lesson
---

# पाठ 12. Training Run को पढ़ना

**मिशन से संबंध:** "विफल run का diagnosis करें और कारण का नाम बताएँ" सफलता-सूची में है। ज़्यादातर लोग loss curve पढ़ते हैं और अंदाज़ा लगाते हैं।
**मुख्य स्रोत:** [लेख: "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
**पूर्व-आवश्यकताएँ:** [पाठ 11](0011-your-first-adapter.md)

## वार्म-अप

1. ▢ Loss curve की परवाह करने से पहले चलाई जाने वाली चार जाँचों के नाम बताएँ।

<details markdown="1"><summary>जाँचें</summary>

पुष्टि करें कि adapter जुड़ा; एक असली training example decode करके scored positions गिनें; पुष्टि करें कि loss हिलता है; पुष्टि करें कि pipeline दो examples पर overfit कर सकता है।

</details>

2. ▢ Base model की revision को adapter के बगल में क्यों दर्ज करें?

<details markdown="1"><summary>जाँचें</summary>

Adapter ख़ास weights के सामने एक diff है। सटीक base के बिना वह बेकार है, और लगभग-सही base चुपचाप गुणवत्ता बिगाड़ता है।

</details>

3. ▢ प्रति frozen parameter बनाम प्रति trainable parameter bytes?

<details markdown="1"><summary>जाँचें</summary>

दो बनाम सोलह।

</details>

## यह जानें

### अकेला training loss लगभग कुछ नहीं बताता

Training loss का गिरना बताता है कि model उस data पर फ़िट हो रहा है जो वह देख सकता है। यह उस model से भी मेल खाता है जो task सीख रहा है और उससे भी जो training set रट रहा है। **इन्हें अलग करने के लिए आपको held-out split चाहिए, और इसका कोई विकल्प नहीं।**

शुरू करने से पहले एक अलग रख लें:

```python
split = dataset.train_test_split(test_size=0.05, seed=0)
args = SFTConfig(..., eval_strategy="steps", eval_steps=50)
trainer = SFTTrainer(..., train_dataset=split["train"], eval_dataset=split["test"])
```

### आकार और उनके मतलब

| Training loss | Held-out loss | Diagnosis | कार्रवाई |
|---|---|---|---|
| गिरता है | गिरता है | सीख रहा है | जारी रखें |
| गिरता है | सपाट होकर बढ़ता है | मोड़ से overfitting | न्यूनतम पर रुकें; ज़्यादा data या कम capacity |
| तेज़ी से ~0 तक गिरता है | तुरंत बढ़ता है | रट रहा है | इस capacity के लिए dataset बहुत छोटा |
| ऊँचा सपाट | ऊँचा सपाट | Underfitting | ज़्यादा rank, ज़्यादा target modules, ऊँचा learning rate |
| Step 1 से सपाट | सपाट | टूटा pipeline | पाठ 11 की चार जाँचें |
| Spikes, या `NaN` | अप्रासंगिक | अस्थिरता | Learning rate घटाएँ; fp16 overflow जाँचें; warm-up जोड़ें |

**Held-out का न्यूनतम** काम का checkpoint है, आख़िरी step नहीं। Checkpoints समय-समय पर सहेजें और सबसे अच्छा रखें; जो run step 1000 पर ख़त्म होता है जबकि held-out loss step 400 पर सबसे नीचे था, उसने 600 steps का नुक़सान train किया है।

### आकार से diagnosis, ज़्यादा सावधानी से

**Loss की ऐसी तली जिसे और training नीचे नहीं करेगी** capacity की छत है। Adapter वह update व्यक्त नहीं कर सकता जो task को चाहिए। Epochs जोड़ना इसे ठीक नहीं कर सकता; rank या target modules जोड़ना कर सकता है।

**Loss जो spike करके लौट आता है** आम तौर पर ऐसे batch की निशानी है जिसमें कुछ असामान्य है: बाहरी लंबाई वाला example, बिगड़ा text, दोहराया गया block। उसे ढूँढें। एक अकेला विकृत example छोटे-dataset वाले run को हिला सकता है।

**Loss जो `NaN` हो जाता है** overflow है। fp16 में यह आम है और loss scaling इसी को रोकने के लिए है; bf16 में यह आम तौर पर कुछ बदतर का संकेत है, जैसे data pipeline में शून्य से भाग, या इतना ऊँचा learning rate जो weights को infinity भेज दे।

**Loss जो साफ़ सीढ़ी में गिरता है**, epoch की सीमाओं पर steps के साथ, इसका मतलब है कि model उन examples को पहचान रहा है जो वह पहले देख चुका है। यह memorisation का सीधे curve में दिखना है।

### वह जो loss बिल्कुल नहीं देख सकता

यह पाठ का अहम हिस्सा है।

Cross-entropy आपके data distribution पर अगले-token की भविष्यवाणी को score करता है। वह इन पर चुप है:

- **क्या generations इस्तेमाल लायक हैं।** Model अच्छा score कर सकता है और ऐसा output बना सकता है जो कभी रुकता नहीं, या जो माँगे गए format को अनदेखा करता है।
- **क्या कुछ और टूटा।** [Catastrophic forgetting](../GLOSSARY.md), यानी आपके task से असंबंधित क्षमताओं का बिगड़ना, आपके task के loss में बिल्कुल नहीं दिखता। आपका held-out loss लगातार सुधर सकता है जबकि model बाक़ी हर उस चीज़ में बदतर होता जाए जो वह कर सकता था।
- **क्या सुधार असली है या contamination।** अगर आपके held-out examples training examples के लगभग-दोहरे हैं, तो held-out loss memorisation माप रहा है और उसे generalisation कह रहा है।

तो: **हर बार generate करें।** Training से पहले prompts का एक छोटा सेट तय कर लें। उन्हें base model से चलाएँ और outputs सहेजें। उन्हें adapt किए गए model से उन्हीं sampling settings पर चलाएँ और फ़र्क़ देखें। असली generations पढ़ने के दस मिनट वह पकड़ लेते हैं जो आपके curve की कोई metric नहीं पकड़ेगी।

```python
PROBES = [
    "<a representative task prompt>",
    "<an edge case you care about>",
    "<something unrelated to the task, to check for forgetting>",
]
```

वह तीसरी श्रेणी वही है जिसे लोग छोड़ देते हैं, और इसी तरह forgetting ship हो जाती है।

### दोहराए जाने की क्षमता

इतना log करें कि आप उसे फिर चला सकें: base model और revision, dataset और उसका सटीक split, seed, हर hyperparameter, और library versions। Adapter fine-tuning की configuration सतह इतनी बड़ी है कि "मुझे लगता है वह rank 32 था" कोई रिकॉर्ड नहीं है।

दो runs की तुलना तभी सार्थक है जब उनके बीच ठीक एक चीज़ अलग हो। Rank *या* learning rate बदलें, दोनों नहीं, और seed और data स्थिर रखें। यह स्पष्ट लगता है और नियमित रूप से तोड़ा जाता है, आम तौर पर इसलिए कि run इतना लंबा चला कि धैर्य महँगा पड़ गया।

## अभ्यास

1. ▢ Training loss 0.2 है और गिर रहा है। Held-out loss दो सौ steps पहले 0.9 पर सबसे नीचे था और अब 1.1 है। क्या हो रहा है, और आप कौन-सा checkpoint ship करते हैं?

<details markdown="1"><summary>जाँचें</summary>

Overfitting। Model अब training set के ख़ास शोर पर फ़िट हो रहा है।

Held-out के न्यूनतम वाला checkpoint ship करें, लगभग दो सौ steps पीछे। फिर अगली बार capacity घटाएँ, data जोड़ें, या जल्दी रुकें।

</details>

2. ▢ दोनों losses इतने ऊँचे स्तर पर सपाट हो जाते हैं कि काम के नहीं। Rank 8, attention-only targets। आप क्या बदलते हैं, और क्या नहीं?

<details markdown="1"><summary>जाँचें</summary>

Capacity बदलें: targets को सभी linear layers तक बढ़ाएँ, और rank बढ़ाएँ। विचार करें कि learning rate बहुत कम तो नहीं।

Epochs न जोड़ें। Capacity की छत उसी data पर और pass करने से नहीं हिलती। diagnosis की परिभाषा ही यही है।

</details>

3. ▢ Held-out loss पूरे समय सुधरता है। आप ship करते हैं। Users बताते हैं कि model उन चीज़ों में बदतर हो गया है जो वह पहले करता था। आपने क्या मापने में चूक की?

<details markdown="1"><summary>जाँचें</summary>

Catastrophic forgetting। आपका held-out सेट आपके task के distribution से लिया गया है, इसलिए वह उस distribution के बाहर की क्षमताओं में बिगाड़ नहीं देख सकता।

इलाज एक regression suite है जो उन क्षमताओं को ढके जिन पर आप train नहीं कर रहे: सामान्य instruction following, refusal व्यवहार, अन्य formats। यही पाठ 24 है, और यही विफलता उसके होने की वजह है।

</details>

4. ▢ कौन-सा अवलोकन ख़राब hyperparameters के बजाय टूटे pipeline का सबसे मज़बूत संकेत है?

    - a) Loss curve शून्य से बहुत ऊपर के मान पर थम जाता है
    - b) पचास के पचास steps में loss बिल्कुल अपरिवर्तित है
    - c) Training loss गिरता है जबकि held-out loss बढ़ता है
    - d) Loss एक step पर ऊपर spike करता है और फिर लौट आता है

<details markdown="1"><summary>जाँचें</summary>

**b)** पचास के पचास steps में loss बिल्कुल अपरिवर्तित है।

थमना underfitting है, अलग होती जोड़ी overfitting है, और spike आम तौर पर एक ख़राब batch है, जो सब असली training व्यवहार हैं। Loss जो *बिल्कुल* नहीं हिलता, उसका मतलब है कि कोई gradient किसी parameter तक नहीं पहुँच रहा, जो wiring की गड़बड़ी है।

</details>

5. ▢ आपके generation probes में से कम से कम एक task से असंबंधित क्यों होना चाहिए?

<details markdown="1"><summary>जाँचें</summary>

क्योंकि run के दौरान forgetting को भाँपने का यही अकेला सस्ता तरीक़ा है। Task से जुड़े probes और task से जुड़ा held-out loss, दोनों सुधरते हैं जबकि असंबंधित क्षमताएँ घटती हैं, इसलिए जो कुछ आप पहले से माप रहे हैं वह आपको चेताएगा नहीं।

</details>

6. ▢ Loss सीढ़ी में गिरता है, हर epoch की सीमा पर गिरावट के साथ। Diagnosis करें।

<details markdown="1"><summary>जाँचें</summary>

Model उन examples को पहचान रहा है जो वह पहले देख चुका है। यह memorisation है, सीधे curve में दिखता हुआ। हर नया epoch एक सीढ़ी नीचे लाता है क्योंकि data अब नया नहीं रहा।

Held-out loss जाँचें, जो संभवतः सपाट या बढ़ता हुआ है, और epochs या capacity घटाएँ।

</details>

## असली दुनिया का अभ्यास

- [ ] पाठ 11 के अपने run में held-out split और समय-समय पर evaluation जोड़ें। Held-out का न्यूनतम ढूँढें।
- [ ] तीन generation probes लिखें, एक आपके task से असंबंधित। Training से पहले base-model के outputs सहेजें।
- [ ] जान-बूझकर overfit करें: उदार rank वाले adapter को 50 examples पर कई epochs तक train करें और दोनों curves को अलग होते देखें। Plot रख लें।
- [ ] कल: किसी असली run के लिए एक पन्ने का run रिकॉर्ड लिखें: base model, revision, data, split, seed, हर hyperparameter, library versions।

## आगे बढ़ने के लिए

- [लेख: "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
- [failure modes शीट](../reference/failure-modes.md)
- [पाठ 24. Regression Suite](0024-the-regression-suite.md): जहाँ असंबंधित probe एक असली system बन जाता है

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
