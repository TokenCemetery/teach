---
title: "资源"
description: "LLM 后训练的可信资料来源"
type: resources
---

# LLM 后训练资源

## 知识

- [论文：“Training language models to follow instructions with human feedback”，Ouyang 等，2022](https://arxiv.org/abs/2203.02155)
  InstructGPT 论文。定义了此后大多数 RLHF 工作所沿用的 SFT、奖励模型、PPO 流水线，并对照纯预训练模型度量了对齐税。用途：第 1、2、3 阶段，以及第 9 阶段对齐税的框架。
- [论文：“Proximal Policy Optimization Algorithms”，Schulman 等，2017](https://arxiv.org/abs/1707.06347)
  把 PPO 作为一个通用的强化学习算法提出，与语言模型无关。用途：第 4 阶段的核心算法，先于它在语言模型中的具体应用来读。
- [论文：“Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback”，Bai 等，2022](https://arxiv.org/abs/2204.05862)
  Anthropic 对同一套从 SFT 到 RLHF 的方案在生产规模上的介绍，包括奖励破解以及针对奖励模型的过度优化在实践中是在哪里出现的。用途：第 3 阶段的奖励破解材料，以及第 4 阶段对实际会出什么问题的叙述。
- [论文：“Direct Preference Optimization: Your Language Model is Secretly a Reward Model”，Rafailov 等，2023](https://arxiv.org/abs/2305.18290)
  推导出由策略和参考模型隐含的闭式奖励，用在偏好对上的单一监督式损失，取代了单独的奖励模型和强化学习循环。用途：第 5 阶段的核心推导。
- [论文：“DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models”，Shao 等，2024](https://arxiv.org/abs/2402.03300)
  提出了 GRPO，用针对每个提示词采样的多条补全算出的组内相对基线，取代 PPO 学习得到的价值函数。用途：第 6 阶段的核心算法。
- [论文：“DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning”，DeepSeek-AI，2025](https://arxiv.org/abs/2501.12948)
  主要通过针对可验证奖励的强化学习来训练扩展的思维链推理，并介绍了如何把由此得到的行为蒸馏进更小的模型。用途：第 7 阶段的主要来源。
- [论文：“Constitutional AI: Harmlessness from AI Feedback”，Bai 等，2022](https://arxiv.org/abs/2212.08073)
  用模型依据一组成文原则来批评并修改自己的输出，取代了人工标注的无害性偏好。用途：第 8 阶段的核心案例，即由模型而不是人产生的反馈。
- [论文：“RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback”，Lee 等，2023](https://arxiv.org/abs/2309.00267)
  在相同任务上，对 RLAIF 与 RLHF 做了直接的对照比较，报告了 AI 反馈在哪些地方与人类反馈相当，在哪些地方不相当。用途：第 8 阶段，作为 Constitutional AI 方法的实证补充。
- [论文：“Llama 2: Open Foundation and Fine-Tuned Chat Models”，Touvron 等，2023](https://arxiv.org/abs/2307.09288)
  开源模型规模上公开的一套 RLHF 方案，包括奖励模型训练的细节，以及跨多轮的迭代式 RLHF 过程。用途：用一套完整、可复现的方案，来交叉核对第 3 和第 4 阶段。
- [文档：“TRL - Transformer Reinforcement Learning”，Hugging Face](https://huggingface.co/docs/trl/index)
  本系列的 SFT 和 DPO 实验实际运行所用的库，附有每个训练器的完整配置示例。用途：第 2、4、5 阶段的动手练习。

## 空白

- 目前还没有关于偏好数据质量的一手来源：标注者之间的分歧、标注说明，以及偏好数据的收集方式如何使训练出的奖励模型产生偏差。要让第 3 阶段的数据质量材料有充分的依据，需要先补上它。
- InstructGPT 自己的报告之外，关于对齐税度量的材料很少；一份更新的、与具体模型无关的论述，会让第 9 阶段更有说服力。
- 目前还没有来自单个团队基础设施的、对 DPO、PPO 与 GRPO 成本做完整比较的生产实践报告；第 10 阶段的判断课，目前只能从各自独立的论文中综合，而不是依据一份已经做过这种比较的来源。
