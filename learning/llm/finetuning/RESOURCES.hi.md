---
title: "संसाधन"
description: "Adapter fine-tuning के लिए भरोसेमंद स्रोत और समुदाय"
type: resources
---

# Adapter Fine-Tuning संसाधन

## ज्ञान

### तीन तरीक़े

- [पेपर: "LoRA: Low-Rank Adaptation of Large Language Models", Hu et al., arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
  मूल low-rank adapter तरीक़ा, और intrinsic-dimensionality का वह तर्क कि यह काम क्यों करता है। इस्तेमाल: चरण 3 के लिए, और यह समझने के लिए कि rank और alpha असल में क्या नियंत्रित करते हैं।

- [पेपर: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
  NF4, double quantisation और paged optimizers, memory का हिसाब खोलकर समझाते हुए। इस्तेमाल: चरण 4 के लिए, और इस संदर्भ के रूप में कि quantized base की गुणवत्ता में क्या क़ीमत लगती है। limitations वाला हिस्सा ज़रूर पढ़ें।

- [पेपर: "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
  Weights को magnitude और direction में बाँटता है और direction को adapt करता है। इस्तेमाल: चरण 5 के लिए। Section 4 का यह विश्लेषण कि full fine-tuning और LoRA हर राशि को कैसे हिलाते हैं, ही असली तर्क है।

- [पेपर: "Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning", Aghajanyan et al., arXiv:2012.13255](https://arxiv.org/abs/2012.13255)
  Adaptation किसी कम-आयामी subspace में रह भी कैसे सकता है। इस्तेमाल: LoRA के नीचे की वजह के लिए, उसके तंत्र के लिए नहीं।

### मौजूदा practice

- [दस्तावेज़: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
  यह तर्क कि पर्याप्त rank वाले all-linear targets full fine-tuning से फ़ासला पाट देते हैं। इस्तेमाल: target-module और rank के चुनाव के लिए, और उस baseline के रूप में जिसे हर नए variant को हराना होगा। यह मूल पेपर से विरासत में मिली attention-only परिपाटी की जगह लेता है।

- [लेख: "Practical Tips for Finetuning LLMs Using LoRA", Sebastian Raschka, Ahead of AI](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms)
  Rank, alpha और target modules पर ablations, प्रयोग दिखाते हुए। इस्तेमाल: hyperparameter की लोक-मान्यताओं को मापे गए नतीजों से परखने के लिए।

- [दस्तावेज़: PEFT, Hugging Face](https://huggingface.co/docs/peft)
  तीनों तरीक़ों का reference implementation और वह configuration जो वे सामने रखते हैं। इस्तेमाल: यह जानने के लिए कि व्यवहार में किसी hyperparameter का नाम क्या है, और कौन-से variants इतने स्थापित हैं कि flag बन चुके हैं। Version पर निर्भर है, इसलिए याददाश्त के बजाय installed release से मिलाकर देखें।

- [दस्तावेज़: SFTTrainer, Hugging Face TRL](https://huggingface.co/docs/trl/main/en/sft_trainer)
  मानक supervised fine-tuning loop और उसके dataset formats। इस्तेमाल: चरण 3 से आगे। Version पर निर्भर; parameter के नाम releases के बीच बदले हैं।

### बुनियाद

- [इंटरैक्टिव: LLM Visualization, Brendan Bycroft](https://bbycroft.net/llm)
  एक अकेले token के रास्ते पर, हर matrix के parameter गिनती के साथ, click करके चलें। इस्तेमाल: चरण 1 के लिए, और "parameters कहाँ रहते हैं" का उपलब्ध सबसे अच्छा जवाब।

- [लेख: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
  Architecture की मानक चित्रात्मक व्याख्या। इस्तेमाल: चरण 1 के लिए, जब block की संरचना अब तक समझ न आई हो।

- [दस्तावेज़: Chat Templates, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
  बातचीत को token sequences में कैसे बदला जाता है, और model का अपना template कैसे लगाएँ। इस्तेमाल: fine-tuning की सबसे आम चुपचाप होने वाली विफलता के लिए।

- [पेपर: "Decoupled Weight Decay Regularization" (AdamW), Loshchilov & Hutter, arXiv:1711.05101](https://arxiv.org/abs/1711.05101)
  वह optimizer जो यहाँ हर जगह इस्तेमाल होता है, और उसका weight decay Adam के weight decay से अलग क्यों है। इस्तेमाल: चरण 2 की memory वाली दलील के लिए।

- [पेपर: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., arXiv:1910.02054](https://arxiv.org/abs/1910.02054)
  Weights, gradients और optimizer state को अलग-अलग memory श्रेणियाँ मानकर किया गया मानक हिसाब। इस्तेमाल: प्रति parameter सोलह bytes का आँकड़ा निकालने के लिए।

- [पेपर: "Training Deep Nets with Sublinear Memory Cost", Chen et al., arXiv:1604.06174](https://arxiv.org/abs/1604.06174)
  Gradient checkpointing, और वह सौदा जो यह compute के बदले memory का करता है। इस्तेमाल: चरण 2 के लिए, और उस सेटिंग के लिए जिसे आप हमेशा के लिए चालू रखेंगे।

- [लेख: "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
  प्रयोग इस तरह कैसे चलाएँ कि उनके नतीजों का कोई मतलब हो। इस्तेमाल: चरण 3 के diagnosis वाले पाठ के लिए, और दो examples पर overfit करने वाले smoke test के लिए।

### Quantisation

- [पेपर: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., arXiv:2208.07339](https://arxiv.org/abs/2208.07339)
  Outlier-feature की वह समस्या जो transformer quantisation को अंकगणित के अनुमान से ज़्यादा कठिन बनाती है। इस्तेमाल: यह समझने के लिए कि blockwise, per-tensor से बेहतर क्यों है।

- [दस्तावेज़: bitsandbytes quantization, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
  4-bit configuration व्यवहार में कैसी दिखती है। इस्तेमाल: चरण 4 के setup के लिए।

- [कोड: bitsandbytes, bitsandbytes-foundation](https://github.com/bitsandbytes-foundation/bitsandbytes)
  `backends/` directory ही इस बात का अधिकार है कि कौन-सा hardware कौन-सा operation support करता है। इस्तेमाल: hardware support का सवाल किसी tutorial के बजाय source से सुलझाने के लिए, क्योंकि इस क्षेत्र में tutorial आम तौर पर पुराने पड़ चुके होते हैं।

### Data और evaluation

- [पेपर: "LIMA: Less Is More for Alignment", Zhou et al., arXiv:2305.11206](https://arxiv.org/abs/2305.11206)
  इस बात का प्रमाण कि छोटा, सावधानी से चुना गया dataset बड़े लापरवाह dataset से बेहतर निकलता है, और SFT ज़्यादातर format सिखाता है। इस्तेमाल: चरण 6 की शुरुआती दलील के लिए।

- [पेपर: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., arXiv:2306.05685](https://arxiv.org/abs/2306.05685)
  Model-as-judge evaluation, उसके biases (position, verbosity, self-preference) के वर्णन के साथ। इस्तेमाल: खुले-सिरे वाली generation की metrics के लिए, और यह समझने के लिए कि judge को मानव labels के सामने calibrate क्यों करना पड़ता है।

- [पेपर: "An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-tuning", Luo et al., arXiv:2308.08747](https://arxiv.org/abs/2308.08747)
  कि forgetting मापी जा सकती है, आम है, और सिर्फ़ किनारे के मामलों तक सीमित नहीं। इस्तेमाल: regression suite को उसे भी जँचाने के लिए जो इसे फ़ालतू बोझ समझता है।

- [पेपर: "Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To!", Qi et al., arXiv:2310.03693](https://arxiv.org/abs/2310.03693)
  सामान्य data पर fine-tuning से safety व्यवहार का बिगड़ना। इस्तेमाल: यह समझने के लिए कि regression suite में refusal वाले मामले क्यों होने चाहिए।

- [कोड: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  मानक benchmark implementations और वे contamination समस्याएँ जिन्हें वे दर्ज करते हैं। इस्तेमाल: eval बनाने के लिए, और प्रकाशित scores को संदेह के साथ पढ़ने के लिए।

### Serving

- [दस्तावेज़: LoRA adapters, vLLM](https://docs.vllm.ai/en/latest/features/lora.html)
  Production में adapters serve करना, multi-adapter routing समेत। इस्तेमाल: चरण 7 के लिए। अधिकतम rank और अधिकतम adapters की सीमाएँ installed version से मिलाकर देखें।

- [पेपर: "S-LoRA: Serving Thousands of Concurrent LoRA Adapters", Sheng et al., arXiv:2311.03285](https://arxiv.org/abs/2311.03285)
  बहुत-से adapters को एक साझा base के सामने कुशलता से कैसे batch किया जाता है। इस्तेमाल: यह समझने के लिए कि multi-adapter serving हल हो चुकी समस्या है, कोई शोध-विचार नहीं।

- [लेख: "LLM Inference Performance Engineering: Best Practices", Databricks](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices)
  Prefill बनाम decode, और हर चरण किससे बँधा होता है। इस्तेमाल: चरण 7 के cost के हिसाब के लिए।

### विकल्प

- [पेपर: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", Lewis et al., arXiv:2005.11401](https://arxiv.org/abs/2005.11401)
  उस तरीक़े का मूल कथन जिसे आम तौर पर तब चुनना चाहिए जब समस्या ज्ञान की हो। इस्तेमाल: आख़िरी पाठ की दलील के लिए, और fine-tuning के ख़िलाफ़ विश्वसनीय ढंग से अपनी बात रखने के लिए।

## अनुभव (Communities)

- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/)
  Consumer hardware पर fine-tune करने वाले लोगों की सबसे बड़ी जमघट, हर backend पर। इस्तेमाल: यह खोजने के लिए कि memory budget के भीतर पहले क्या काम कर चुका है, कौन-सी लोक-मान्यताएँ परखने लायक हैं, और नए तरीक़ों पर दोहराने की रिपोर्टें। archive पढ़ें; post करना एक अभ्यास है, स्रोत नहीं।

- [Hugging Face Forums](https://discuss.huggingface.co/)
  खोजने योग्य और archived, library के लेखक मौजूद। इस्तेमाल: PEFT, TRL और `transformers` का वह व्यवहार जिसे docs अस्पष्ट छोड़ते हैं।

- [EleutherAI Blog](https://blog.eleuther.ai/)
  उस समूह के लेख जो अपने ही क्षेत्र को आलोचनात्मक ढंग से पढ़ता है, नकारात्मक नतीजों समेत। इस्तेमाल: चरण 5 और 7 के उन फ़ैसलों के लिए कि कोई दावा किया गया नतीजा आम तौर पर लागू होगा या नहीं। इन पर चर्चा पहले उनके Discord पर होती है, जिसे जान-बूझकर सूचीबद्ध नहीं किया गया: वहाँ कही गई कोई बात बाद में दोबारा नहीं निकाली जा सकती।

- [MLX Discussions, ml-explore/mlx](https://github.com/ml-explore/mlx/discussions)
  सार्वजनिक, खोजने योग्य, और maintainers के जवाबों के साथ। इस्तेमाल: यह पढ़ने के लिए कि कोई ख़ास operation Apple Silicon पर अब तक support होता है या नहीं, जो आम तौर पर पहले ही पूछा जा चुका होता है।

## कमियाँ

- कोई स्रोत यह दर्ज नहीं करता कि किसी दिए Python version और platform पर `torch`, PEFT, TRL और quantisation-library के कौन-से versions असल में साथ काम करते हैं। यह कोई भी अवधारणा से ज़्यादा बार पहली run को रोकता है, और हर environment को मान लेने के बजाय release notes से जाँचना पड़ता है।
- 4-bit operations के लिए hardware backend की coverage हर release में बदलती है। यहाँ कोई दस्तावेज़ भरोसेमंद नहीं; library का source ही अकेला अधिकार है, और hardware ज़रूरतों के बारे में किसी भी tutorial के दावे को समाप्त हो चुका मानना चाहिए।
- छोटे model के task adaptation के लिए evaluation डिज़ाइन पर अभी कोई भरोसेमंद स्रोत नहीं। यह चरण 6 की सबसे कमज़ोर कड़ी और मिशन का सबसे कठिन हिस्सा है। सामान्य evaluation साहित्य foundation models की benchmarking के लिए है, यह साबित करने के लिए नहीं कि कोई संकरा adapter काम आया।
- प्रकाशित LoRA hyperparameter सलाह में से ज़्यादातर 7B और उससे बड़े models के लिए है। बहुत कम में यह देखा गया है कि वह 1B से 3B वर्ग पर लागू होती है या नहीं, जहाँ से ज़्यादातर लोग असल में शुरू करते हैं।
- DoRA के लिए उस पैमाने की कोई स्वतंत्र पुनरावृत्ति नहीं मिली जो LoRA और QLoRA को हासिल है। उसके बताए फ़ायदों को स्थानीय माप की ज़रूरत वाला मानें।
- constrained decoding के लिए कोई स्रोत नहीं चुना गया, जिसे पाठ 27 schema-validity की समस्याओं का सही जवाब बताता है। उसका नाम लिया गया है, पर पीछे कोई संदर्भ नहीं है।
