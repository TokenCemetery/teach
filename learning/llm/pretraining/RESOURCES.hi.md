---
title: "संसाधन"
description: "LLM pretraining के लिए भरोसेमंद स्रोत"
type: resources
---

# LLM Pretraining संसाधन

## ज्ञान

- [पेपर: "Scaling Laws for Neural Language Models", Kaplan et al., 2020](https://arxiv.org/abs/2001.08361)
  Loss, compute, parameter count और data के बीच के मूल power-law संबंधों को fit करता है, और तर्क देता है कि parameters को data से तेज़ बढ़ाना चाहिए। इस्तेमाल: चरण 3 के लिए, उस आधार-रेखा के रूप में जिसे Chinchilla बाद में सुधारता है।
- [पेपर: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
  Chinchilla का पेपर। यह ज़्यादा चौड़े sweep के साथ scaling laws को दोबारा fit करता है और पाता है कि parameters और tokens को साथ-साथ बढ़ना चाहिए, लगभग बीस tokens प्रति parameter, जिससे Kaplan की parameter-भारी सिफ़ारिश पलट जाती है। इस्तेमाल: चरण 3 के केंद्रीय नतीजे के लिए, और उस token budget के लिए जिसे ज़्यादातर आधुनिक training runs असल में अपनाते हैं।
- [पेपर: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
  तीन ZeRO stages को परिभाषित करता है: data-parallel devices में पहले optimizer state, फिर gradients, फिर parameters की sharding। इस्तेमाल: चरण 5 की केंद्रीय तकनीक के लिए, जिसे FSDP लागू करता है।
- [दस्तावेज़: "Fully Sharded Data Parallel", PyTorch](https://pytorch.org/docs/stable/fsdp.html)
  PyTorch की ZeRO-stage-3 जैसी sharding का API reference, जिसमें वे sharding strategies और wrapping policies शामिल हैं जो किसी पाठ का lab असल में चलाता है। इस्तेमाल: चरण 5 के hands-on अभ्यासों के लिए।
- [पेपर: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
  Tensor parallelism, pipeline parallelism और data parallelism को एक system में जोड़ता है, और हर एक के throughput और memory tradeoffs को बाक़ियों के विरुद्ध नापता है। इस्तेमाल: चरण 6 की केंद्रीय तकनीक और उसके हल किए हुए आँकड़ों के लिए।
- [दस्तावेज़: "DeepSpeed", Microsoft](https://github.com/microsoft/DeepSpeed)
  3D parallelism के साथ ZeRO का दूसरा production implementation, जिसके configuration examples को कोई पाठ FSDP और Megatron-LM के बग़ल में दूसरे ठोस system के रूप में दिखा सकता है। इस्तेमाल: चरण 5 और 6 के लिए, यह दोबारा जाँचने के लिए कि कोई दावा तकनीक के बारे में है, किसी एक library के API के बारे में नहीं।
- [पेपर: "The Pile: An 800GB Dataset of Diverse Text for Language Modeling", Gao et al., 2020](https://arxiv.org/abs/2101.00027)
  पूरी तरह दर्ज किया हुआ pretraining corpus: कौन-से स्रोत गए, किस अनुपात में, और क्यों। इस्तेमाल: चरण 1 के लिए, data-mixing के ऐसे फ़ैसले के हल किए हुए उदाहरण के रूप में जिसे साफ़ लिखा गया है।
- [पेपर: "Deduplicating Training Data Makes Language Models Better", Lee et al., 2021](https://arxiv.org/abs/2107.06499)
  दिखाता है कि लगभग-एक-जैसा text और लंबी दोहराई गई substrings हू-ब-हू memorization की वजह बनती हैं, और दो deduplication तकनीकें देता है (suffix array से हू-ब-हू substring matching, और MinHash से लगभग-एक-जैसे का matching), हर एक को असली corpus पर नापा गया है। इस्तेमाल: चरण 1 की deduplication सामग्री के लिए, पहले-बाद की ठोस संख्याओं के साथ।
- [पेपर: "Language Models are Few-Shot Learners", Brown et al., 2020](https://arxiv.org/abs/2005.14165)
  GPT-3 का पेपर। Appendix A में एक ठोस quality-filtering pipeline दर्ज है: एक classifier जो छाँटे हुए text और कच्चे Common Crawl में फ़र्क़ करना सीखता है, और जिसका इस्तेमाल Common Crawl को ज़्यादा score वाले documents की ओर दोबारा sample करने में होता है, साथ में अलग fuzzy-deduplication pass। इस्तेमाल: चरण 1 की quality-filtering सामग्री के लिए, उस हल किए हुए उदाहरण के रूप में जो ऊपर का deduplication पेपर ख़ुद नहीं देता।
- [पेपर: "Neural Machine Translation of Rare Words with Subword Units", Sennrich et al., 2015](https://arxiv.org/abs/1508.07909)
  Subword tokenization के लिए byte-pair encoding पेश करता है, वह algorithm जिस पर ज़्यादातर आधुनिक tokenizers आज भी टिके हैं। इस्तेमाल: चरण 2 के मूल algorithm के लिए।
- [पेपर: "SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing", Kudo and Richardson, 2018](https://arxiv.org/abs/1808.06226)
  Tokenization को सीधे कच्चे text पर चलने वाली चीज़ मानता है, भाषा-विशेष pre-tokenization चरण के बिना, और BPE के विकल्प के रूप में unigram-language-model tokenization को भी कवर करता है। इस्तेमाल: चरण 2 के दूसरे algorithm और vocabulary-size के tradeoff के लिए।
- [पेपर: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
  बड़े training run का विस्तृत और ईमानदार ब्योरा, जिसमें यह भी है कि loss spikes और अस्थिरता कहाँ आई और लेखकों ने उसके बारे में क्या किया। इस्तेमाल: चरण 7 के केंद्रीय case study के लिए।
- [पेपर: "LLaMA: Open and Efficient Foundation Language Models", Touvron et al., 2023](https://arxiv.org/abs/2302.13971)
  प्रकाशित, दोहराई जा सकने वाली training recipe: data mixture, tokenizer, schedule और hyperparameters, इतने साफ़ लिखे हुए कि किसी पाठ के दावों को उनसे मिलाकर जाँचा जा सके। इस्तेमाल: चरण 1 से 3 और 7 को असली, पूरी recipe से मिलाकर जाँचने के लिए।
- [पेपर: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
  उन infrastructure समस्याओं की सार्वजनिक logbook के साथ जारी हुआ जो लेखकों को 175B model train करते समय असल में झेलनी पड़ीं: hardware failures, हाथ से और अपने-आप होने वाले restarts, loss divergences, और हर एक के लिए अपनाई गई ठोस recovery प्रक्रिया। इस्तेमाल: चरण 8 के केंद्रीय case study के लिए, और चरण 7 में आए loss-divergence पैटर्न के दूसरे असली उदाहरण के लिए।
- [पेपर: "Don't Stop Pretraining: Adapt Language Models to Domains and Tasks", Gururangan et al., 2020](https://arxiv.org/abs/2004.10964)
  दिखाता है कि मौजूदा व्यापक-कवरेज वाले model पर pretraining जारी रखने (domain-adaptive pretraining) से चार domains और आठ tasks में target-domain का प्रदर्शन लगातार सुधरता है, ज़्यादा और कम संसाधन वाली दोनों स्थितियों में, बिना शुरू से नया model train किए। इस्तेमाल: चरण 10 के केंद्रीय तर्क के लिए कि शुरू से pretraining करना अक्सर ग़लत default होता है।

## कमियाँ

- OPT का पेपर असली failure frequency और recovery प्रक्रिया दर्ज करता है, पर कोई ख़ास checkpoint-interval नीति नहीं बताता (यानी checkpoints असल में कितनी बार save हुए)। चरण 8 का checkpoint-frequency tradeoff बताई गई नीति के बजाय सामान्य engineering तर्क से सिखाया गया है; ठोस interval वाला कोई मुख्य स्रोत इसे मज़बूत करेगा।
- GPT-3 की classifier-आधारित filtering (2020) अब तक सूचीबद्ध इकलौता हल किया हुआ quality-filtering उदाहरण है। 2023 के बाद बने corpora (FineWeb, Dolma) कहीं ज़्यादा सख़्ती से filter करते हैं और उसे ज़्यादा गहराई से दर्ज करते हैं; कोई ज़्यादा हालिया मुख्य स्रोत चरण 1 को मज़बूत करेगा।
