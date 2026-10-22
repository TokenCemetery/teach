---
title: "संसाधन"
description: "Inference के लिए भरोसेमंद स्रोत"
type: resources
---

# Inference संसाधन

## ज्ञान

- [दस्तावेज़: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
  उस GPU serving stack का आधिकारिक दस्तावेज़ जो यह workspace सबसे पहले खड़ा करता है: install, serve, और engine की batching व memory settings। इस्तेमाल: vLLM को खुद कैसे चलाएँ और configure करें।
- [पेपर: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
  PagedAttention का पेपर: KV cache आम memory allocators को fragment क्यों करता है और उसे paging करने से वह कैसे ठीक होता है, उन throughput संख्याओं के साथ जो vLLM के design की वजह बनीं। इस्तेमाल: यह समझना कि KV cache की क्या क़ीमत है और vLLM का memory manager क्यों मौजूद है।
- [Repo: llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp)
  उस CPU/edge serving stack का आधिकारिक repo जो यह workspace दूसरे नंबर पर खड़ा करता है: build के निर्देश, समर्थित quantization formats (GGUF), और server binary के flags। इस्तेमाल: llama.cpp को खुद कैसे चलाएँ और configure करें।
- [Pull request: "k-quants", ikawrakow, llama.cpp, 2023](https://github.com/ggml-org/llama.cpp/pull/1684)
  k-quant प्रकार, उनका super-block layout, और `S`, `M` और `L` नुस्खे लाता है जो tensors में प्रकार मिलाते हैं। इस्तेमाल: `Q4_K_M` जैसा GGUF नाम असल में क्या सहेजता है।
- [पेपर: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2023](https://arxiv.org/abs/2210.17323)
  3-4 bits तक one-shot post-training weight quantization, नापी गई accuracy की क़ीमत के साथ। इस्तेमाल: serving के लिए model quantize करने में असल में क्या छोड़ना पड़ता है, और वह सौदा कैसे नापा जाता है।
  अगर यहाँ की linear algebra अटका रही हो तो पहले नीचे दी गई [transformers गाइड](https://huggingface.co/docs/transformers/main/en/llm_optims) पढ़ें।
- [दस्तावेज़: "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
  KV cache, static बनाम dynamic batching और quantization backends की practitioner-स्तर की walkthrough, जिसके लिए पहले पेपर का गणित ज़रूरी नहीं। इस्तेमाल: ऊपर के मुख्य स्रोतों से पहले एक काम-चलाऊ mental model।
- [लेख: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
  Forward pass के पीछे का असली FLOP और memory-bandwidth का हिसाब निकालता है, जिसमें यह भी कि KV cache की memory लागत कहाँ से आती है। इस्तेमाल: benchmark दोहराने के बजाय बुनियादी सिद्धांतों से latency या memory budget निकालना।
- [लेख: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
  उन engineers ने लिखा जिन्होंने एक शुरुआती serving engine में continuous batching बनाई; समझाता है कि मिली-जुली length वाली request stream पर static batching GPU का समय क्यों बरबाद करती है और continuous batching उसे कैसे ठीक करती है। इस्तेमाल: latency/throughput के उस सौदे का batching वाला आधा हिस्सा जिसका यह workspace बचाव करता है।

- [पेपर: "Fast Inference from Transformers via Speculative Decoding", Leviathan et al., 2022](https://arxiv.org/abs/2211.17192)
  Speculative decoding की शुरुआत करता है: छोटा model कई tokens draft करता है, बड़ा model उन सबको एक parallel pass में verify करता है, एक ऐसी sampling विधि के साथ जो गारंटी देती है कि output distribution ठीक वही रहे जो अकेले बड़ा model चलाने पर होता। इस्तेमाल: यह सिर्फ़ latency का उपाय क्यों है, गुणवत्ता का trade-off नहीं, और memory-bandwidth का वह तर्क कि parallel verification लगभग मुफ़्त क्यों है।
- [पेपर: "Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads", Cai et al., 2024](https://arxiv.org/abs/2401.10774)
  Speculative decoding के अलग draft model की जगह target model में सीधे अतिरिक्त decoding heads जोड़ता है। इस्तेमाल: दूसरा model सँभालने के संचालन-भार को हल करना, जबकि verify-और-सुधारो की वही गारंटी बनी रहे।
- [पेपर: "EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty", Li et al., 2024](https://arxiv.org/abs/2401.15077)
  कच्चे tokens के बजाय model की अंदरूनी features के स्तर पर draft करता है, और एक कदम आगे के token sequence को शामिल करके feature-स्तर की पूर्वानुमान अनिश्चितता सुलझाता है। इस्तेमाल: Medusa के ऊपर एक और सुधार, जिसमें रिपोर्ट किया गया speedup बड़ा है और target model का output distribution फिर भी सुरक्षित रहता है।
- [पेपर: "Efficient Guided Generation for Large Language Models" (Outlines), Willard and Louf, 2023](https://arxiv.org/abs/2307.09702)
  Constrained generation को finite-state-machine की states के बीच transitions के रूप में देखता है, जिससे vocabulary index हर grammar के लिए एक बार पहले से बनाया जा सकता है और तेज़ प्रति-token lookup की तरह दोबारा इस्तेमाल हो सकता है। इस्तेमाल: grammar या schema से बँधी decoding प्रति token बहुत कम overhead क्यों जोड़ती है और output का structure उम्मीद से नहीं बल्कि बनावट से गारंटी क्यों देती है।
- [दस्तावेज़: "Automatic Prefix Caching", vLLM Project](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html)
  बाक़ी बेमेल requests के पार किसी साझा prefix का KV cache दोबारा इस्तेमाल करने का vLLM का अपना दस्तावेज़, उसके दो नामित उदाहरण workloads (लंबे document का QA, multi-round बातचीत), और उसकी बताई सीमा (सिर्फ़ prefill तेज़ करता है, decode कभी नहीं)। इस्तेमाल: prefix caching को PagedAttention की block-sharing कार्यप्रणाली के requests के पार विस्तार के रूप में समझना।
- [पेपर: "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism", Shoeybi et al., 2019](https://arxiv.org/abs/1909.08053)
  Tensor parallelism का मानक पेपर: एक intra-layer model-parallel योजना जो transformer layer के matrix multiplies को GPUs में बाँटती है और जिसे बस कुछ communication operations चाहिए, और जो साफ़ तौर पर pipeline parallelism से अलग और उसकी पूरक है। इस्तेमाल: `--tensor-parallel-size` (पाठ 12) layer के भीतर असल में क्या करता है।
- [पेपर: "GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism", Huang et al., 2018](https://arxiv.org/abs/1811.06965)
  Pipeline parallelism का मानक पेपर: layers की श्रृंखला के रूप में लिखे जा सकने वाले किसी भी network को लगातार समूहों में बाँटकर अलग accelerators पर रखता है, और micro-batching लाता है जो नतीजे में बनी pipeline bubble को घटाती है (मिटाती नहीं)। इस्तेमाल: tensor parallelism का वैकल्पिक split, और वह धीमा inter-device link क्यों सह लेता है।
- [दस्तावेज़: "Welcome to production-stack" और use-case guides, vLLM Production Stack](https://docs.vllm.ai/projects/production-stack)
  vLLM की reference Kubernetes-native fleet deployment का आधिकारिक दस्तावेज़: KV-cache aware request routing और `vllm:num_requests_waiting` जैसे queue-depth metrics पर चलने वाली KEDA-आधारित autoscaling। इस्तेमाल: एक server से आगे fleet के पैमाने पर routing और autoscaling असल में कैसे काम करते हैं।
- [पेपर: "ServerlessLLM: Low-Latency Serverless Inference for Large Language Models", Fu et al., OSDI 2024](https://arxiv.org/abs/2401.14351)
  नापता है कि LLM के cold starts इतने गंभीर क्यों हैं (checkpoint load का समय प्रति-token generation के समय से कहीं ज़्यादा, production traces में दसियों सेकंड) और multi-tier, GPU के पास checkpoint loading से उसे ठीक करता है। इस्तेमाल: fleet में replica जोड़ना तुरंत क्यों नहीं होता, और वह कितनी जल्दी उपयोगी बन सकती है इसे असल में क्या बाँधता है।
- [दस्तावेज़: "Metrics", vLLM Project](https://docs.vllm.ai/en/stable/design/metrics/)
  Export होने वाले Prometheus metrics की vLLM की अपनी सूची: TTFT, inter-token latency, end-to-end latency, और अलग prefill/decode समय के histograms। इस्तेमाल: production server असल में लगातार क्या export करता है, एक बार के benchmark के मुक़ाबले।
- [Google SRE Workbook: "Implementing SLOs"](https://sre.google/workbook/implementing-slos/)
  SLIs, SLOs और error budgets की मानक SRE रूपरेखा: user से जुड़ा अनुपात, उसके लिए तय लक्ष्य, और उस लक्ष्य को चूकने की सहनशीलता जो सीधे SLO से निकलती है। इस्तेमाल: raw exported metric को काम में आने लायक़ production लक्ष्य में बदलना।
- [पेपर: "YaRN: Efficient Context Window Extension of Large Language Models", Peng et al., ICLR 2024](https://arxiv.org/abs/2309.00071)
  RoPE की frequency dimensions को असमान रूप से दोबारा scale करके model की उपयोगी context length उसकी trained length से आगे बढ़ाता है, पहले के तरीक़ों की fine-tuning लागत के एक अंश पर। इस्तेमाल: RoPE scaling अधिकतम context length क्यों बदलती है और KV cache की अपनी बढ़त को क्यों नहीं छूती।
- [पेपर: "Mistral 7B", Jiang et al., 2023](https://arxiv.org/abs/2310.06825)
  Sliding-window attention और उसका जोड़ीदार rolling buffer cache लाता है: हर token पिछले tokens की ज़्यादा से ज़्यादा एक निश्चित window पर attend करता है, जिससे sequence length कुछ भी हो cache का आकार सीमित रहता है। इस्तेमाल: वह कार्यप्रणाली जो पाठ 2 की रैखिक cache बढ़त को स्थिरांक में बदल देती है।
- [पेपर: "Efficient Streaming Language Models with Attention Sinks", Xiao et al., ICLR 2024](https://arxiv.org/abs/2309.17453)
  Attention-sink की उस घटना की पहचान करता है जिसके कारण सादा sliding-window attention पुराने tokens हटते ही ढह जाता है, और शुरुआती मुट्ठी भर tokens की KV entries को स्थायी रूप से रखकर उसे ठीक करता है। इस्तेमाल: सीमित cache भी असल में असीमित stream को क्यों serve कर सकता है।

## कमियाँ

- llama.cpp के GGUF formats के लिए quantization-aware serving पर अभी कोई स्रोत नहीं है (GPTQ/AWQ के उलट, जो GPU stacks को लक्ष्य करते हैं); पाठ-design उस चरण तक पहुँचे तो mission को CPU/edge-विशिष्ट quantization तुलना चाहिए।
