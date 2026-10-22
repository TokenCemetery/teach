---
title: "10. Backward Pass और Autograd"
description: "Chain rule, रिकॉर्ड किए गए computation graph पर स्वचालित होकर, एक scalar loss को हर weight के gradient में कैसे बदलता है"
type: lesson
---

# पाठ 10. Backward Pass और Autograd

**मिशन से संबंध:** पाठ 9 का scalar loss अकेले training के किसी काम का नहीं; backward pass ही उसे model की हर एक weight के gradient में बदलता है, और यही वह असली signal है जिसे optimizer (पाठ 11) उन्हें बेहतर करने के लिए इस्तेमाल करता है।
**मुख्य स्रोत:** [दस्तावेज़: "Autograd mechanics", PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
**पूर्व-आवश्यकताएँ:** [पाठ 9](0009-cross-entropy-loss.md), [Scaled dot-product attention](../GLOSSARY.md)

## वार्म-अप

1. ▢ Cross-entropy ग़लत prediction के जुर्माने के लिए `1 - p` जैसी किसी चीज़ की जगह `-log(p)` क्यों इस्तेमाल करता है?

<details markdown="1"><summary>जाँचें</summary>

सही token को दी गई probability के 0 के क़रीब पहुँचने पर `-log(p)` बिना किसी सीमा के बढ़ता है, और आत्मविश्वास से ग़लती को लगातार ज़्यादा कड़ाई से दंडित करता है। `1 - p` 1 पर saturate हो जाता है, prediction कितनी भी आत्मविश्वास से ग़लत हो, और सिर्फ़ ग़लत prediction को विनाशकारी prediction से अलग करने के लिए कोई अतिरिक्त signal नहीं देता।

</details>

2. ▢ Residual connections transformer blocks के गहरे stack को train करने में कैसे मदद करते हैं?

<details markdown="1"><summary>जाँचें</summary>

वे gradients को हर layer पर identity `+ x` connection से सीधा रास्ता देते हैं, चाहे हर sublayer का रूपांतरण कुछ भी करे, जिससे गहरे stack की सबसे शुरुआती layers तक भी काम का training signal पहुँचता रहता है।

</details>

## यह जानें

### हर forward operation दर्ज करता है कि वह कैसे compute हुआ

Forward pass चलते समय हर operation, matrix multiply, softmax, residual connection के लिए जोड़, एक **computation graph** में दर्ज होता है: इस बात का रिकॉर्ड कि हर बीच का tensor ठीक किस operation से, और किन input tensors से बना। **Backward pass** इसी graph पर उलटी दिशा में चलता है ताकि अंतिम scalar loss का gradient हर उस tensor के प्रति compute हो सके जिसने उसमें योगदान दिया, हर train हो सकने वाली weight तक वापस।

### Chain rule, अपने-आप लगाया हुआ

इसके नीचे का तंत्र calculus के chain rule के स्वचालन के सिवा कुछ नहीं है: किसी tensor के प्रति loss का gradient, graph में उसके नीचे की ओर के हर रास्ते पर, उस निचले tensor के प्रति loss के gradient को, निचले tensor के इस tensor के प्रति स्थानीय derivative से गुणा करने का योग होता है। एक ठोस संख्यात्मक मामला: मान लें `y = 3x + 1` और `z = y^2`। `x = 2` पर `y = 7`। `dz/dy = 2y = 14`। `dy/dx = 3`। Chain rule से `dz/dx = dz/dy × dy/dx = 14 × 3 = 42`। Autograd ठीक इसी तरह का गुणा और योग करता है, बस दो छोटे समीकरणों की जगह लाखों या अरबों parameters वाले network के हर operation पर।

![y = 3x + 1 और z = y का वर्ग वाला एक worked example, x = 2 पर। Forward pass, ऊपर से नीचे और बाएँ से दाएँ खींचा हुआ, x = 2 compute करता है, फिर operation y = 3x + 1 से y = 7, फिर operation z = y का वर्ग से z। Backward pass, नीचे दाएँ से बाएँ चलता हुआ, z से शुरू होता है, y तक पहुँचने के लिए स्थानीय derivative dz/dy = 14 से गुणा करता है, फिर x तक पहुँचने के लिए स्थानीय derivative dy/dx = 3 से गुणा करता है, और chain rule से dz/dx = 14 गुणा 3 = 42 मिलता है।](images/chain-rule-worked-example.svg)

### Automatic differentiation, न symbolic और न numerical

PyTorch का **autograd** न तो symbolic differentiation है (हाथ से या computer algebra से gradient का closed-form सूत्र निकालना) और न ही numerical differentiation (finite differences से gradient का अनुमान लगाना, जो अशुद्ध है और हर parameter के लिए forward computation को कई बार दोबारा चलाना माँगता है)। इसके बजाय, हर बुनियादी operation (matrix multiply, जोड़, softmax, वग़ैरह) का हाथ से निकाला हुआ स्थानीय backward नियम पहले से लागू है, और autograd उन स्थानीय नियमों को रिकॉर्ड किए गए computation graph के हिसाब से अपने-आप जोड़कर एक ही backward traversal में सटीक gradients बनाता है।

### Residual connections असल में अपना काम कहाँ करते हैं

पाठ 5 ने तर्क दिया था कि residual connections गहरे stack में gradients को बहता रखते हैं; chain rule ठीक वह जगह है जहाँ वह तर्क यांत्रिक बन जाता है। Residual output `y = x + Sublayer(x)` के लिए, `x` के प्रति loss का gradient `d(loss)/d(y) × 1` है (identity path का स्थानीय derivative, जो ठीक 1 है) जमा `Sublayer` के अपने स्थानीय derivative से बहने वाला दूसरा पद। `Sublayer` का अपना स्थानीय derivative कितना भी छोटा या बिगड़ा हुआ हो जाए, वह पहला पद कम से कम सीधे, बिना scale हुए `d(loss)/d(y)` के योगदान को `x` तक बिना बदले पहुँचने की गारंटी देता है। यही residual connections के vanishing gradients रोकने का सटीक, यांत्रिक कारण है, "shortcuts" के बारे में कोई अनौपचारिक अंदाज़ा भर नहीं।

### एक call हर parameter का gradient भर देती है

Scalar loss compute होने के बाद, एक अकेली call, `loss.backward()`, पूरे computation graph पर चलती है और हर train हो सकने वाले parameter के `.grad` attribute में उस parameter के प्रति loss का gradient जमा कर देती है। Gradients डिफ़ॉल्ट रूप से overwrite होने के बजाय **accumulate** होते हैं, यानी `.grad` में जो पहले से था उसमें जुड़ते जाते हैं, और इसीलिए training loop को हर नए backward pass से पहले हर parameter का gradient साफ़ तौर पर शून्य करना पड़ता है; वरना हर step का gradient पिछले step के बचे हुए मानों से दूषित हो जाता।

## अभ्यास

1. ▢ मान लें `y = 3x + 1` और `z = y^2`। `x = 2` पर chain rule से `y`, `dz/dy`, `dy/dx` और `dz/dx` निकालें।

<details markdown="1"><summary>संकेत</summary>

`dz/dx = dz/dy × dy/dx`।

</details>

<details markdown="1"><summary>जाँचें</summary>

`y = 3(2) + 1 = 7`। `dz/dy = 2y = 14`। `dy/dx = 3`। `dz/dx = 14 × 3 = 42`।

</details>

2. ▢ Residual output `y = x + Sublayer(x)` के लिए, identity path `d(loss)/d(x)` में कौन-सा पद जोड़ता है, और यह इस बात की गारंटी क्यों देता है कि `Sublayer` का अपना स्थानीय derivative कितना भी छोटा हो, `x` तक कुछ gradient पहुँचता है?

<details markdown="1"><summary>जाँचें</summary>

Identity path `d(loss)/d(y) × 1` जोड़ता है, क्योंकि identity connection का स्थानीय derivative ठीक 1 है। वह पद `Sublayer` के अपने derivative पर बिल्कुल निर्भर नहीं करता, इसलिए `Sublayer` का gradient में योगदान शून्य की ओर सिकुड़ भी जाए, तब भी सीधा, बिना scale हुआ `d(loss)/d(y)` इस रास्ते से `x` तक पहुँचता है।

</details>

3. ▢ बड़े network को train करने के लिए automatic differentiation (autograd) को numerical differentiation (finite differences) पर क्यों तरजीह दी जाती है?

<details markdown="1"><summary>जाँचें</summary>

Numerical differentiation हर parameter के gradient का अनुमान उसे थोड़ा हिलाकर और forward pass दोबारा चलाकर लगाता है, जो अशुद्ध है और हर parameter के लिए अलग forward pass माँगता है, लाखों या अरबों weights वाले network के लिए बेहिसाब महँगा। Autograd इसके बजाय हर parameter के सटीक gradients रिकॉर्ड किए गए computation graph के एक ही backward traversal में compute करता है, हर operation के पहले से लागू स्थानीय backward नियम का इस्तेमाल करके।

</details>

4. ▢ `loss.backward()` बुलाने से असल में क्या भरता है, और अगली call से पहले gradients को आम तौर पर शून्य क्यों करना पड़ता है?

<details markdown="1"><summary>संकेत</summary>

सोचें कि जिस `.grad` attribute में पिछले step का मान पहले से है उसके साथ क्या होता है।

</details>

<details markdown="1"><summary>जाँचें</summary>

वह हर train हो सकने वाले parameter के `.grad` attribute को उस parameter के प्रति loss के gradient से भरता है, जो रिकॉर्ड किए गए computation graph पर चलकर compute होता है। Gradients डिफ़ॉल्ट रूप से overwrite होने के बजाय accumulate होते हैं, और `.grad` में जो मान पहले से था उसमें जुड़ते हैं; हर नए backward pass से पहले gradients को साफ़ तौर पर शून्य किए बिना, बाद के step का gradient पिछले step के बचे हुए मानों से दूषित हो जाता।

</details>

5. ▢ Gradients compute करने के autograd के तरीक़े के बारे में कौन-सा दावा सही है?

    - a) उसमें उपयोगकर्ता को हर operation के लिए closed-form gradient सूत्र निकालकर देना पड़ता है
    - b) वह finite differences से gradients का अनुमान लगाता है, हर parameter को थोड़ा हिलाकर
    - c) वह forward pass के operations को computation graph में दर्ज करता है, फिर हर operation के पहले से लागू स्थानीय backward नियम से chain rule अपने-आप लगाता है
    - d) वह gradients सिर्फ़ अंतिम output layer के लिए compute करता है, गहरे stack की पहले की layers के लिए नहीं

<details markdown="1"><summary>जाँचें</summary>

**c)** autograd ठीक इसी तरह काम करता है: न हाथ से निकालना, न finite-difference का अनुमान, बस रिकॉर्ड किए graph पर chain rule का स्वचालित इस्तेमाल। (a) ग़लत है: यह symbolic differentiation का वर्णन है, autograd के तरीक़े का नहीं। (b) ग़लत है: यह numerical differentiation का वर्णन है, जिससे autograd बचता है। (d) ग़लत है: backward pass का पूरा मक़सद ही gradients को हर layer तक वापस फैलाना है, stack कितना भी गहरा हो।

</details>

## असली दुनिया का अभ्यास

- [ ] हाथ से एक छोटा computation graph बनाएँ (दो-तीन जुड़े हुए operations, worked example जैसे) और जाँचें कि PyTorch का autograd वही gradient बनाता है जो आपकी हाथ की chain-rule गणना बनाती है।
- [ ] एक forward pass चलाएँ, बीच में gradients शून्य किए बिना `loss.backward()` को लगातार दो बार बुलाएँ, और पक्का करें कि दूसरी call के `.grad` मान नए gradient की जगह accumulation दर्शाते हैं।
- [ ] कल: मुख्य स्रोत docs का "How autograd encodes the history" खंड पढ़ें और ध्यान दें कि रिकॉर्ड किया गया graph नए forward pass और gradient tracking बंद करके चलाए गए pass के बीच कैसे अलग होता है।

## आगे बढ़ने के लिए

- [दस्तावेज़: "Autograd mechanics", PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
- [Repo: nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
- [संसाधन](../RESOURCES.md)

---

बात नहीं बन रही? ऊपर दिए मुख्य स्रोत को दोबारा पढ़ें, क्योंकि यह पाठ उसे संक्षिप्त करता है और समझ संक्षेप में ही रिसती है। जो शब्द फिसलन भरा लगे, उसके लिए [शब्दावली](../GLOSSARY.md) देखें।

अगर दिक़्क़त सामग्री की नहीं बल्कि पाठ की ही है, तो वह एक खोट है: [issue खोलें](https://github.com/TokenCemetery/teach/issues)।
