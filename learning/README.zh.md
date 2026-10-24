---
title: 学习路线总览
description: 本仓库中的所有主题，按领域分组
type: index
---

# 学习路线总览

按领域分组，每个主题一个目录。每个主题都是一条由 `teach` skill 驱动、自成一体的学习路线：一个目标、一组按顺序排列的课程，以及这些课程沉淀下来的参考资料。

## 主题

| 领域 | 主题 | 目标 | 课程数 |
|---|---|---|---|
| programming | [Bash](programming/bash/) | 编写能在生产环境中经受考验的 shell：引号、退出状态、失败模式，以及知道何时停手改用真正的编程语言 | 17 |
| programming | [C#](programming/csharp/) | 掌控一个 C# 服务：类型系统、async，以及 CLR 如何处理你写下的代码 | 45 |
| programming | [Go](programming/golang/) | 在团队中对 Go 负责：设计、发布并运维一个生产服务 | 41 |
| programming | [Java](programming/java/) | 掌控一个 Java 服务：用现代 Java 为它建模，再运维 JVM 对它所做的一切 | 52 |
| programming | [Kotlin](programming/kotlin/) | 在 JVM 上掌控 Kotlin：空安全、协程，以及 Java 习惯在哪里会写出能编译、读起来却很糟的 Kotlin | 44 |
| programming | [Python](programming/python/) | 在生产环境中掌控 Python：带着类型、测试、打包和性能剖析把它交付出去 | 44 |
| programming | [Rust](programming/rust/) | 掌握 Rust：用所有权来设计，而不是与借用检查器较劲，然后发布 crate | 67 |
| programming | [SQL](programming/sql/) | 掌握数据库：写出查询，读懂执行计划，设计 schema，扛住并发 | 53 |
| programming | [TypeScript](programming/typescript/) | 掌握 TypeScript 代码库：让编译器拒绝那些本不该存在的状态 | 49 |
| llm | [适配器微调](llm/finetuning/) | 判断要不要微调，把它跑起来，证明它有效，并把它发布出去 | 27 |
| llm | [LLM 预训练](llm/pretraining/) | 大规模从零训练一个模型：数据、分词器、分布式训练，以及一份站得住脚的算力预算 | 24 |
| llm | [LLM 后训练](llm/post-training/) | 对齐一个基座模型：SFT、奖励建模、RLHF、DPO 和 GRPO，并知道该选哪一个 | 20 |
| llm | [推理服务](llm/inference/) | 为模型提供服务：KV 缓存、批处理、服务时的量化，以及一个你能为之辩护的延迟预算 | 24 |
| llm | [评测](llm/evals/) | 证明模型的改动确实有效：搭建评测，诚实地留出数据，并为这个数字抵御数据污染辩护 | 18 |
| llm | [RAG](llm/rag/) | 掌握检索：分块、嵌入、混合检索、重排序，以及度量是否检索到了正确的内容 | 19 |
| llm | [Transformer](llm/transformers/) | 从零搭建注意力，让这个架构不再是训练脚本背后的黑箱 | 22 |
| llm | [LLM 智能体](llm/agents/) | 亲手构建循环：工具、上下文、记忆，以及看清什么时候智能体是错误的答案 | 37 |
| llm | [量化](llm/quantization/) | 量化一个 LLM 并为之辩护：数值格式、训练后量化与量化感知训练的方法、什么真正跑得更快，以及度量它的代价 | 27 |
| llm | [提示词工程](llm/prompting/) | 为 LLM 功能编写、版本管理并上线提示词，证明一次提示词改动确实有效，并评审别人的生产提示词 | 24 |
| llm | [蒸馏](llm/distillation/) | 把大模型蒸馏成小模型并为之辩护：软目标、logit 与序列级损失、合成数据、在策略训练，以及学生丢掉了什么 | 27 |
| data | [Postgres](data/postgres/) | 运维 Postgres：WAL、vacuum 与膨胀、复制，以及维护一个索引的代价 | 18 |
| data | [Kafka](data/kafka/) | 掌握日志：分区、消费者组、投递保证，以及“恰好一次”实际的代价 | 16 |
| data | [Redis](data/redis/) | 按 Redis 的本来面目使用它：内存模型、淘汰、持久化，以及那些悄悄误用它的模式 | 17 |
| architecture | [分布式系统](architecture/distributed-systems/) | 对部分失败进行推理：网络能对你做什么，你实际买到的是哪种一致性，以及共识为什么昂贵 | 19 |
| architecture | [API 设计](architecture/api-design/) | 设计别人依赖的接口：契约、它的错误，以及如何在不破坏使用方的前提下演进 | 19 |
| infrastructure | [容器](infrastructure/containers/) | 把服务打包成容器镜像并对它负责：内核原语、Dockerfile，以及运行、加固和调试单个容器 | 24 |
| infrastructure | [Kubernetes](infrastructure/kubernetes/) | 在 Kubernetes 集群上运行服务并对它们负责：协调循环、工作负载、网络、配置、可靠性、安全、打包与调试 | 28 |
| infrastructure | [CI/CD](infrastructure/ci-cd/) | 通过流水线构建、测试并交付每一次改动，并对它负责：工作流、快速反馈、制品、密钥、部署、回滚与供应链安全 | 30 |

## 开始一个主题

```bash
cp -r templates/learning-workspace learning/<domain>/<topic-slug>
```

然后运行 `teach` skill 并说出主题名称。它会读取这条学习路线，通过向你提问来填写目标，并写出第一节课。

领域只是一个分组，而不是一条学习路线：它只包含主题目录，别无其他。当第二个主题也会归入同一领域时，再新建这个领域。

## 目录结构

```text
learning/
├── <domain>/              # programming, llm, …
│   └── <topic>/           # one track per topic
├── .nav.yml               # sidebar order/titles for the published site
└── README.md              # this index
```

每条学习路线：

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

每条学习路线中的课程都从 `0001` 开始编号。学习路线之间可以相互链接，但链接只是一个指向，而不是纳入：它不会把另一个主题的内容拉进本路线的目标。与其链接一节课，不如链接一个术语表条目或一份参考速查表，因为它们本就是为查阅而写的，任何读者点进去都能看懂。

这里每个文件的格式都由 `teach` skill 决定。手工编写之前，请先阅读[它的规范](https://github.com/TokenCemetery/teach/blob/main/.agents/skills/teach/SKILL.md)。

## 许可

本站的所有内容均采用 [CC BY 4.0](https://github.com/TokenCemetery/teach/blob/main/LICENSE-CONTENT) 许可。可以复制、翻译、用来教学、在其基础上创作，商业用途与否均可。只需注明出处。
