---
title: "संसाधन"
description: "LLMs के knowledge distillation के लिए भरोसेमंद स्रोत"
type: resources
---

# Distillation संसाधन

## ज्ञान

### बुनियाद

- [पेपर: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals and Dean, 2015](https://arxiv.org/abs/1503.02531)
  वह पेपर जिसने इस विधि को नाम दिया: soft targets, temperature, T squared gradient सुधार और combined loss, MNIST और speech experiments के साथ। इस्तेमाल: चरण 1 के लिए, स्रोत से सीधे।
- [पेपर: "A Survey on Knowledge Distillation of Large Language Models", Xu et al., 2024](https://arxiv.org/abs/2402.13116)
  LLM distillation का नक़्शा, इस आधार पर बँटा हुआ कि teacher से क्या निकाला जाता है और student को उस पर कैसे train किया जाता है। इस्तेमाल: किसी विधि का अपना पेपर पढ़ने से पहले उसे बड़े परिवार में रखकर देखने के लिए।
- [पेपर: "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter", Sanh et al., 2019](https://arxiv.org/abs/1910.01108)
  Pretraining के दौरान transformer का एक पूरा हल किया हुआ distillation, जिसमें distillation, masked language modelling और cosine embedding की तीन loss terms हैं। इस्तेमाल: ऐसी पूरी विधि के लिए जिसमें हर loss term का ablation मौजूद है।

### Logit और sequence-level distillation

- [पेपर: "Sequence-Level Knowledge Distillation", Kim and Rush, 2016](https://arxiv.org/abs/1606.07947)
  Translation के लिए word-level बनाम sequence-level distillation, और teacher के beam-search output पर training। इस्तेमाल: चरण 2 और 3 के लिए, दोनों levels की मूल रूपरेखा।
- [पेपर: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
  Generative distillation में reverse KL के पक्ष में तर्क, जिसे student के samples पर policy-gradient विधि से optimise किया गया है। इस्तेमाल: forward बनाम reverse KL, और on-policy distillation के एक रूप के लिए।
- [पेपर: "Towards Cross-Tokenizer Distillation: the Universal Logit Distillation Loss for LLMs", Boizard et al., 2024](https://arxiv.org/abs/2402.12030)
  Optimal transport पर आधारित loss जो sorted probability vectors की तुलना करता है, ताकि teacher और student को vocabulary साझा न करनी पड़े। इस्तेमाल: cross-tokenizer distillation क्या करता है और क्या छोड़ता है।
- [पेपर: "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
  2B और 9B models को next-token prediction के बजाय बड़े teacher से knowledge distillation के साथ train करना। इस्तेमाल: pretraining signal के रूप में distillation।
- [पेपर: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
  Minitron: किसी train किए हुए model को prune करना और मूल model से distillation के साथ उसे दोबारा train करना, मूल training tokens के बहुत छोटे हिस्से पर। इस्तेमाल: pruning के बाद की रिकवरी के चरण के रूप में distillation।
- [पेपर: "LLM Pruning and Distillation in Practice: The Minitron Approach", Sreenivas et al., 2024](https://arxiv.org/abs/2408.11796)
  Minitron की विधि Llama 3.1 8B और Mistral NeMo 12B पर लागू की गई, जिसमें पहले distillation data पर teacher को सुधारना भी शामिल है। इस्तेमाल: उसी विधि का दूसरा, ज़्यादा हाल का run।

### Synthetic-data distillation

- [पेपर: "Self-Instruct: Aligning Language Models with Self-Generated Instructions", Wang et al., 2022](https://arxiv.org/abs/2212.10560)
  Model की अपनी generations से instruction data खड़ा करना, near-duplicates और अमान्य examples को filter करके। इस्तेमाल: generated instruction set कैसे बनता है।
- [लेख: "Alpaca: A Strong, Replicable Instruction-Following Model", Stanford CRFM, 2023](https://crfm.stanford.edu/2023/03/13/alpaca.html)
  LLaMA 7B को Self-Instruct विधि से text-davinci-003 के generate किए 52K instructions पर fine-tune करना, उसकी लागत, और उसकी बताई सीमाएँ और license पाबंदियाँ। इस्तेमाल: नक़ल का मानक सस्ता run।
- [पेपर: "Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes", Hsieh et al., 2023](https://arxiv.org/abs/2305.02301)
  छोटे model को labels के साथ दूसरे task के रूप में teacher की rationales बनाना सिखाना। इस्तेमाल: अकेले labels के ऊपर rationales क्या जोड़ती हैं।
- [पेपर: "Orca: Progressive Learning from Complex Explanation Traces of GPT-4", Mukherjee et al., 2023](https://arxiv.org/abs/2306.02707)
  System prompts से निकाले गए explanation traces की नक़ल, GPT-4 से पहले ChatGPT को बीच के teacher की तरह रखकर। इस्तेमाल: LLM पैमाने पर explanation traces और teacher assistant।
- [पेपर: "Textbooks Are All You Need", Gunasekar et al., 2023](https://arxiv.org/abs/2306.11644)
  phi-1: filter किए गए web data और GPT-3.5 के generate किए synthetic textbooks और exercises पर train किया गया छोटा code model। इस्तेमाल: data की गुणवत्ता बनाम data की मात्रा।
- [पेपर: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
  किसी reasoning model को उसके चुने हुए samples पर fine-tune करके छोटे Qwen और Llama models में distil करना, और छोटे model पर सीधे RL चलाने से उसकी तुलना (appendix F.1)। इस्तेमाल: rejection-sampled synthetic data, और वह post-training पाठ जिसकी ओर यह track link करता है।

### On-policy distillation

- [पेपर: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
  Generalized knowledge distillation: student के generate किए sequences पर training, divergence के चुनाव और तय तथा on-policy data के मिश्रण के साथ। इस्तेमाल: चरण 5 के लिए, स्रोत से सीधे।
- [पेपर: "Qwen3 Technical Report", Qwen Team, 2025](https://arxiv.org/abs/2505.09388)
  छोटे Qwen3 models का strong-to-weak distillation, जिसमें off-policy चरण के बाद on-policy चरण आता है, और उसी models पर RL से तुलना की गई है। इस्तेमाल: production model परिवार में on-policy distillation।
- [दस्तावेज़: "Generalized Knowledge Distillation Trainer", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gkd_trainer)
  GKD का TRL implementation और उसके `lmbda`, `beta` और `seq_kd` parameters। इस्तेमाल: on-policy distillation के बारे में पढ़ने के बजाय उसे चलाने के लिए।
- [दस्तावेज़: "General Online Logit Distillation (GOLD) Trainer", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gold_trainer)
  TRL का trainer जो GKD को Universal Logit Distillation loss के साथ बढ़ाता है, text spans को align करके ताकि teacher और student अलग tokenizers इस्तेमाल कर सकें। इस्तेमाल: cross-tokenizer on-policy run को क्या चाहिए।

### Student को क्या विरासत में मिलता है

- [पेपर: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945)
  Students अक्सर अपने teachers से मेल नहीं खा पाते, तब भी जब उनमें इसकी क्षमता हो, और बेहतर generalization के लिए बेहतर fidelity ज़रूरी नहीं। Experiments ज़्यादातर image classification के हैं, एक text task के साथ। इस्तेमाल: fidelity को task की गुणवत्ता से अलग करने के लिए।
- [पेपर: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717)
  जिन imitation models को crowdworkers ने ChatGPT के क़रीब आँका, उन्होंने लक्षित benchmarks पर फ़ासले का बहुत कम हिस्सा पाटा। इस्तेमाल: imitation gap, और यह कि मानव preference ratings ने उसे कैसे छिपाया।
- [पेपर: "Improved Knowledge Distillation via Teacher Assistant", Mirzadeh et al., 2019](https://arxiv.org/abs/1902.03393)
  Teacher और student के बीच फ़ासला बहुत बढ़ने पर student की गुणवत्ता गिरती है, और बीच के आकार का assistant उसका कुछ हिस्सा लौटा देता है; इसके vision experiments में फ़ायदे छोटे हैं। इस्तेमाल: capacity gap।
- [पेपर: "On the Efficacy of Knowledge Distillation", Cho and Hariharan, 2019](https://arxiv.org/abs/1910.01348)
  ज़्यादा सटीक teachers हमेशा बेहतर students नहीं बनाते, और teacher को जल्दी रोक देने से मदद मिल सकती है। इस्तेमाल: capacity gap का दूसरा विवरण।
- [पेपर: "Subliminal Learning: Language models transmit behavioral traits via hidden signals in data", Cloud et al., 2025](https://arxiv.org/abs/2507.14805)
  Teacher के संख्या-sequences पर train हुए student ने teacher की विशेषताएँ उठा लीं, जब दोनों का base model एक ही था। इस्तेमाल: data को filter करके भी क्या नहीं हटाया जा सकता।

### आकार तय करना

- [पेपर: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606)
  Student की गुणवत्ता का scaling law, student के आकार, distillation tokens और teacher की गुणवत्ता के फ़ंक्शन के रूप में, और distillation कब उसी student की supervised training को हराता है। यह भी बताता है कि उसके setup में सबसे अच्छा distillation temperature 1 था (appendix G.2)। इस्तेमाल: चरण 7 के लिए स्रोत से सीधे, और LLM पर 1 से ऊपर के temperature का प्रतिवाद।

### Licensing और terms

- [शर्तें: "Terms of Use", OpenAI](https://openai.com/policies/row-terms-of-use/)
  EEA, स्विट्ज़रलैंड और UK के बाहर के उपयोगकर्ताओं के लिए OpenAI की consumer शर्तें, जिनमें OpenAI से होड़ करने वाले models विकसित करने के लिए output इस्तेमाल करना उन चीज़ों में गिना गया है जो उपयोगकर्ता नहीं कर सकता। इस्तेमाल: किसी hosted provider की शर्तें उसके outputs पर training के बारे में क्या कहती हैं।
- [License: "Llama 3.1 Community License Agreement", Meta](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE)
  Open-weights license जो model के outputs को किसी दूसरे model को सुधारने में इस्तेमाल करने देता है, इस शर्त पर कि बँटते समय नतीजे वाले model का नाम "Llama" से शुरू हो। इस्तेमाल: किसी open model का license उसके outputs पर training के बारे में क्या कहता है।

## कमियाँ

- Thinking Machines की on-policy distillation वाली post, RL से अपनी लागत-तुलना के लिए बहुत उद्धृत की जाती है, पर उसकी site scripted और in-app reads को मना करती है, इसलिए यहाँ उससे कोई संख्या इस्तेमाल नहीं की गई। चरण 5 इसके बजाय GKD, MiniLLM और Qwen3 पेपरों पर टिका है।
- Terms of use और licenses बिना ऐसे version के बदल जाते हैं जिसे कोई पाठ pin कर सके। पाठ 0013 उन्हें वैसे ही उद्धृत करता है जैसे इस track को लिखते समय पढ़ा गया था; भरोसा करने से पहले स्रोत दोबारा जाँचें।
