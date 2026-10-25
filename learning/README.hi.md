---
title: सीखने के Tracks
description: इस repository का हर विषय, domain के हिसाब से समूहों में
type: index
---

# सीखने के Tracks

Domain के हिसाब से समूहों में, हर विषय के लिए एक directory। हर विषय `teach` skill से चलने वाला अपने-आप में पूरा track है: एक mission, पाठों का क्रमबद्ध set, और वह reference सामग्री जो उन पाठों से अर्जित हुई।

## विषय

| Domain | विषय | Mission | पाठ |
|---|---|---|---|
| programming | [Bash](programming/bash/) | ऐसा shell लिखें जो production में टिका रहे: quoting, exit status, failure modes, और यह जानना कि कब रुककर असली भाषा इस्तेमाल करें | 17 |
| programming | [C#](programming/csharp/) | C# service को अपने हाथ में लें: type system, async, और आपके लिखे code के साथ CLR क्या करता है | 45 |
| programming | [Go](programming/golang/) | Team में Go को अपने हाथ में लें: production service डिज़ाइन, ship और संचालित करें | 41 |
| programming | [Java](programming/java/) | Java service को अपने हाथ में लें: उसे modern Java में model करें, फिर JVM उसके साथ जो करता है उसे संचालित करें | 52 |
| programming | [Kotlin](programming/kotlin/) | JVM पर Kotlin को अपने हाथ में लें: null safety, coroutines, और वह जगह जहाँ Java की आदत ऐसा Kotlin पैदा करती है जो compile होता है पर बुरा पढ़ा जाता है | 44 |
| programming | [Python](programming/python/) | Production में Python को अपने हाथ में लें: उसे typed, tested, packaged और profiled रूप में ship करें | 44 |
| programming | [Rust](programming/rust/) | Rust को अपने हाथ में लें: borrow checker से लड़ने के बजाय ownership के साथ डिज़ाइन करें, फिर crate ship करें | 67 |
| programming | [SQL](programming/sql/) | Database को अपने हाथ में लें: query लिखें, plan पढ़ें, schema डिज़ाइन करें, concurrency में टिके रहें | 53 |
| programming | [TypeScript](programming/typescript/) | TypeScript codebase को अपने हाथ में लें: compiler से उन states को अस्वीकार करवाएँ जो मौजूद नहीं होनी चाहिए | 49 |
| llm | [Adapter fine-tuning](llm/finetuning/) | तय करें कि fine-tune करना है या नहीं, उसे चलाएँ, साबित करें कि वह काम किया, उसे ship करें | 27 |
| llm | [Pretraining](llm/pretraining/) | बड़े पैमाने पर model को शुरू से train करें: data, tokenizer, distributed training, और ऐसा compute budget जिसका बचाव किया जा सके | 24 |
| llm | [Post-training](llm/post-training/) | Base model को align करें: SFT, reward modeling, RLHF, DPO, और GRPO, और यह जानना कि कौन-सा चुनना है | 20 |
| llm | [Inference](llm/inference/) | Model serve करें: KV cache, batching, serve के समय quantization, और ऐसा latency budget जिसका आप बचाव कर सकें | 24 |
| llm | [Evals](llm/evals/) | साबित करें कि model बदलाव से मदद मिली: eval बनाएँ, data को ईमानदारी से अलग रखें, और संख्या का contamination के सामने बचाव करें | 18 |
| llm | [RAG](llm/rag/) | Retrieval को अपने हाथ में लें: chunking, embeddings, hybrid search, reranking, और यह मापना कि सही चीज़ retrieve हुई या नहीं | 19 |
| llm | [Transformers](llm/transformers/) | Attention को शुरू से बनाएँ, ताकि architecture training script के पीछे का black box न रहे | 22 |
| llm | [Agents](llm/agents/) | Loop ख़ुद बनाएँ: tools, context, memory, और यह जानना कि कब agent ग़लत जवाब है | 37 |
| llm | [Quantization](llm/quantization/) | LLM को quantize करें और उसका बचाव करें: number formats, PTQ और QAT methods, क्या तेज़ चलता है, और यह मापना कि इसकी क्या क़ीमत रही | 27 |
| llm | [Prompting](llm/prompting/) | LLM feature के लिए prompts लिखें, version करें और ship करें, साबित करें कि prompt बदलाव से मदद मिली, और किसी और के production prompt की समीक्षा करें | 24 |
| llm | [Distillation](llm/distillation/) | बड़े model को छोटे में distill करें और उसका बचाव करें: soft targets, logit और sequence-level losses, synthetic data, on-policy training, और student ने क्या खोया | 27 |
| data | [Postgres](data/postgres/) | Postgres चलाएँ: WAL, vacuum और bloat, replication, और index को बनाए रखने की क़ीमत | 18 |
| data | [Kafka](data/kafka/) | Log को अपने हाथ में लें: partitions, consumer groups, delivery guarantees, और "exactly once" की असली क़ीमत | 16 |
| data | [Redis](data/redis/) | Redis का उपयोग उसी के लिए करें जो वह है: memory model, eviction, persistence, और वे patterns जो चुपचाप उसका दुरुपयोग करते हैं | 17 |
| data | [Warehouses](data/warehouses/) | Analytical warehouse के मालिक बनें: columnar storage और execution, compute से अलग storage, और row store की performance सलाह यहाँ क्यों लागू नहीं होती | 20 |
| architecture | [Distributed Systems](architecture/distributed-systems/) | Partial failure पर तर्क करें: network आपके साथ क्या कर सकता है, आप असल में कौन-सी consistency ख़रीद रहे हैं, और consensus महँगा क्यों है | 19 |
| architecture | [API Design](architecture/api-design/) | ऐसा interface डिज़ाइन करें जिस पर दूसरे निर्भर हों: contract, उसकी errors, और उन्हें तोड़े बिना वह कैसे बदलता है | 19 |
| infrastructure | [Containers](infrastructure/containers/) | किसी service को container image के रूप में package करें और उसे अपने हाथ में लें: kernel primitives, Dockerfiles, एक container को चलाना, सुरक्षित करना और debug करना | 24 |
| infrastructure | [Kubernetes](infrastructure/kubernetes/) | Kubernetes cluster पर services चलाएँ और उन्हें अपने हाथ में लें: reconciliation loop, workloads, networking, configuration, reliability, security, packaging और debugging | 28 |
| infrastructure | [CI/CD](infrastructure/ci-cd/) | हर बदलाव को pipeline से build, test और deliver करें और उसे अपने हाथ में लें: workflows, तेज़ feedback, artifacts, secrets, deployments, rollback और supply-chain security | 30 |

## कोई विषय शुरू करना

```bash
cp -r templates/learning-workspace learning/<domain>/<topic-slug>
```

फिर `teach` skill चलाएँ और विषय का नाम बताएँ। वह track पढ़ती है, आपसे बातचीत करके mission भरती है, और पहला पाठ लिखती है।

Domain एक समूह है, track नहीं: उसमें विषयों की directories होती हैं और कुछ नहीं। नया domain तब जोड़ें जब कोई दूसरा विषय उसे साझा करे।

## ढाँचा

```text
learning/
├── <domain>/              # programming, llm, …
│   └── <topic>/           # one track per topic
├── .nav.yml               # sidebar order/titles for the published site
└── README.md              # this index
```

हर track:

```text
learning/<domain>/<topic>/
├── README.md              # mission, success criteria, lesson index
├── GLOSSARY.md            # canonical terms for this topic
├── RESOURCES.md           # trusted sources, known gaps
├── NOTES.md               # preferences and working notes
├── lessons/               # NNNN-slug.md, one tight win each
├── reference/             # cheat sheets, built for lookup
└── learning-records/      # NNNN-slug.md, what was demonstrably learned
```

हर track में पाठों की numbering `0001` से शुरू होती है। Tracks एक-दूसरे को link कर सकते हैं, पर link एक संकेतक है, समावेश नहीं: वह किसी दूसरे विषय की सामग्री को इस mission में नहीं खींचता। पाठ के बजाय शब्दावली के किसी शब्द या reference sheet को link करना बेहतर है, क्योंकि वे lookup के लिए लिखे जाते हैं और किसी भी पाठक के काम आते हैं।

यहाँ की हर file का format `teach` skill तय करती है। किसी file को हाथ से लिखने से पहले [उसकी spec](https://github.com/TokenCemetery/teach/blob/main/.agents/skills/teach/SKILL.md) पढ़ें।

## License

इस site पर सब कुछ [CC BY 4.0](https://github.com/TokenCemetery/teach/blob/main/LICENSE-CONTENT) के तहत है। इसे copy करें, अनुवाद करें, इससे पढ़ाएँ, इस पर निर्माण करें, व्यावसायिक रूप से या नहीं। बस बताएँ कि यह कहाँ से आया।
