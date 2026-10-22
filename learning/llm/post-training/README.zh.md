---
title: "LLM 后训练"
description: "对齐一个基座模型：SFT、奖励建模、RLHF、DPO 和 GRPO，并知道该选哪一个"
type: topic
---

# LLM 后训练

能把一个预训练的基座模型，带到一个经过对齐、能遵循指令的助手：正确写出 SFT、奖励和偏好三类目标；针对一个团队的预算和数据，在 RLHF-PPO、DPO 和 GRPO 之间做出选择，并为这个选择辩护，包括它在对齐税上付出了多少，又在哪些地方容易受到奖励破解的影响。

**最新课程：** [20. 评审别人的对齐方案](lessons/0020-reviewing-someone-elses-alignment-recipe.md)

## 成功的标准

- 写出一个对非助手 token 做损失掩码的 SFT 训练循环，并解释不加这个掩码训练出来的聊天模型会出什么问题。
- 用 Bradley-Terry 损失在偏好对上训练一个奖励模型，并从针对它训练出的策略中，找出一条被奖励破解的补全。
- 推导 RLHF 的目标（奖励减去针对参考模型的 KL 惩罚），并说明放松 KL 惩罚时策略会发生什么。
- 从 RLHF 所用的同一份偏好数据推导出 DPO 的隐式奖励，并说明去掉强化学习循环后它放弃了什么。
- 解释 GRPO 中的组内相对优势，以及为什么可验证奖励（单元测试、核对过的数学答案）会改变强化学习训练可以瞄准的目标。
- 给定一个团队的数据、预算和目标行为，在单独的 SFT、DPO、RLHF-PPO 和 GRPO 之间做出选择，并针对被否决的那一个为这个选择辩护。
- 阅读一个已对齐模型的评测结果，把真正的能力提升，与奖励破解或评判者偏差造成的假象区分开。

## 约束

- 以算法为先，而不是论文综述。每个阶段都从损失函数出发，由内向外讲一个训练目标：在最大化什么、梯度做了什么，而不是概括一串论文；论文则作为每个阶段的主要来源，起到锚定作用。
- 小规模练习：在一个小型开源模型上运行 SFT 和 DPO，沿用 `llm/finetuning` 所用的规模纪律，再由此推理所引前沿论文报告的结果。
- 假定你学过 `llm/transformers`（交叉熵损失、反向传播、AdamW），并熟悉 `llm/finetuning` 中的适配器机制，因为本系列会复用这些内容，而不是重新推导参数高效性。
- 没有哪一课会在前沿规模上端到端地训练完整的 RLHF 流水线；PPO 的成本在小规模上演示，再推理到所引论文报告的规模。

## 范围之外

- 参数高效的机制（LoRA 的秩和 alpha、QLoRA、DoRA、目标模块）：见 [`llm/finetuning`](../../llm/finetuning/)。本系列负责训练目标，`llm/finetuning` 负责如何把它应用到更少的参数上。
- 交叉熵损失、反向传播和 AdamW：见 [`llm/transformers`](../../llm/transformers/)。这里是默认已掌握，不再重新讲授。
- LLM 作为评判者的机制和人工评估方法：见 [`llm/evals`](../../llm/evals/)。这里只把它当作已对齐模型所需要的一项能力，用来判断对齐训练是否有帮助，并链接过去，而不重述。
- 给推理模型写提示词，或围绕它构建智能体：见 [`llm/agents`](../../llm/agents/)（第 0017 课）。本系列讲的是推理行为如何通过强化学习训练产生，而不是如何从外部使用它。
- 从随机初始化开始训练一个模型：见 [`llm/pretraining`](../../llm/pretraining/)。
- 一般意义上的蒸馏，超出推理模型这一情形的部分：见 [`llm/distillation`](../../llm/distillation/)。这里的第 0014 课仍然只讲推理模型这个特例，并链接过去查看一般方法。
- 通过提示词从外部使用指令遵循和推理能力：见 [`llm/prompting`](../../llm/prompting/)。本系列讲的是这些行为如何被训练进模型。

## 学习路线

共十个阶段，从毫无基础到资深的判断力。这不是一份课程清单：一个阶段包含若干课程，边界并不严格。

| 阶段 | 课程 | 内容 | 完成的标志 |
| --- | --- | --- | --- |
| 1. 后训练能带来什么 | 0001 至 0001 | 基座模型对比指令/聊天模型，SFT/RLHF/DPO/GRPO 的全景 | 能把一个已对齐模型的行为，对应到产生它的那个后训练阶段上 |
| 2. SFT | 0002 至 0003 | 指令数据集、聊天模板、非助手 token 上的损失掩码 | 能写出带正确损失掩码的 SFT 循环，并说明没有它会出什么问题 |
| 3. 奖励建模 | 0004 至 0005 | 偏好数据的收集、Bradley-Terry 损失、奖励破解 | 能训练一个奖励模型，并针对它找出一条被奖励破解的补全 |
| 4. 通过 PPO 做 RLHF | 0006 至 0008 | 强化学习目标、针对参考模型的 KL 惩罚、PPO 为什么昂贵又不稳定 | 能推导 RLHF 的目标，并说明放松 KL 惩罚会让策略发生什么 |
| 5. 直接偏好优化 | 0009 至 0010 | DPO 的隐式奖励、它相对 PPO 舍弃了什么，以及为什么这通常没有问题 | 能推导 DPO 的隐式奖励，并说明它相对 PPO 放弃了什么 |
| 6. GRPO 与可验证奖励的强化学习 | 0011 至 0012 | 组内相对优势，以及它为什么适合数学和代码 | 能解释组内相对优势，以及为什么可验证奖励会改变强化学习可以瞄准的目标 |
| 7. 推理模型 | 0013 至 0014 | 思维链强化学习、DeepSeek-R1 带来了什么改变、把推理模型蒸馏下去 | 能说清一个推理模型的行为是如何产生的，而不只是如何给它写提示词 |
| 8. 安全与拒答调优 | 0015 至 0016 | 红队测试数据、Constitutional AI、RLAIF | 能说清在一条给定的安全调优流水线里，反馈来自哪里（人还是 AI），以及这样做是在权衡什么 |
| 9. 评估已对齐的模型 | 0017 至 0018 | 对齐税、奖励破解的检测、链接到 `llm/evals` | 能把真正的能力提升，与奖励破解或评判者偏差造成的假象区分开 |
| 10. 判断 | 0019 至 0020 | 针对给定预算比较 DPO、PPO 与 GRPO、何时单独用 SFT 就够、评审别人的对齐方案 | 值得信任去做出决定，并向他人解释清楚 |

## 课程

请按顺序学习。

| # | 课程 | 内容 |
|---|---|---|
| [0001](lessons/0001-what-post-training-buys.md) | 后训练能带来什么 | 一个小 100 倍的已对齐模型，在做用户真正想要的事情上，胜过了原始的基座模型 |
| [0002](lessons/0002-instruction-data-and-the-chat-template.md) | 指令数据与聊天模板 | 一个特殊 token 标出提示词在哪里结束、回答从哪里开始，而这条边界在训练和服务时必须一致 |
| [0003](lessons/0003-loss-masking-on-non-assistant-tokens.md) | 非助手 token 上的损失掩码 | 把提示词上的损失置零，否则就会把梯度信号浪费在教模型预测它并没有生成的文本上 |
| [0004](lessons/0004-training-a-reward-model-the-bradley-terry-loss.md) | 训练奖励模型：Bradley-Terry 损失 | 奖励模型在训练中从不会看到绝对分数，只知道两条补全里人更喜欢哪一条 |
| [0005](lessons/0005-reward-hacking.md) | 奖励破解 | 一个策略学会了对几乎所有问题都说“我无法回答这个问题”，因为这样得分很高，却并没有真正做到有用或无害 |
| [0006](lessons/0006-the-rlhf-objective-reward-minus-a-kl-penalty.md) | RLHF 目标：奖励减去 KL 惩罚 | 一项追逐奖励模型的分数；另一项则是拴住策略的缰绳，不让它带着分数跑偏 |
| [0007](lessons/0007-ppo-why-the-update-gets-clipped.md) | PPO：为什么更新要被裁剪 | 在一批采样数据上的大幅胜利，并不是迈出大步的可靠证据；PPO 拒绝对它完全相信 |
| [0008](lessons/0008-why-ppo-is-expensive-and-unstable.md) | 为什么 PPO 昂贵又不稳定 | 需要同时把四个模型而不是一个放进内存，而其中扩展性最差的两个，恰恰就是 RLHF 新增的那两个 |
| [0009](lessons/0009-dpos-implicit-reward-why-the-partition-function-cancels.md) | DPO 的隐式奖励：为什么配分函数会抵消 | 一个无法计算的归一化项挡在奖励与它的最优策略之间，直到两个奖励相减，才让它消失 |
| [0010](lessons/0010-the-dpo-loss-and-what-it-drops-relative-to-ppo.md) | DPO 损失，以及它相对 PPO 舍弃了什么 | 一个损失，两个模型，没有采样循环，beta 与 KL 惩罚本来会用的那个完全相同 |
| [0011](lessons/0011-grpo-group-relative-advantage-instead-of-a-value-function.md) | GRPO：用组内相对优势取代价值函数 | 对同一个问题采样多个答案，让这一组奖励自身的分布，来说明哪些答案更好 |
| [0012](lessons/0012-verifiable-rewards-when-a-checker-replaces-the-reward-model.md) | 可验证奖励：当检查器取代奖励模型 | 训练出来的奖励模型是对人会偏好什么的一种猜测；单元测试或匹配的答案则完全不是猜测 |
| [0013](lessons/0013-chain-of-thought-rl-what-deepseek-r1-zero-did-with-rule-based-rewards.md) | 思维链强化学习：DeepSeek-R1-Zero 用基于规则的奖励做了什么 | 没有学习得到的奖励模型，也没有事先的 SFT 步骤，扩展的推理依然出现了，因为它能让更多答案做对 |
| [0014](lessons/0014-distilling-a-reasoning-model-down.md) | 蒸馏一个推理模型 | 直接用强化学习训练一个 32B 模型，输给了只在更大模型自己的推理轨迹上做微调 |
| [0015](lessons/0015-constitutional-ai-feedback-from-a-model-not-a-human.md) | Constitutional AI：来自模型而非人的反馈 | 有害性方面没有任何人工标签，只用一份成文的原则清单，得到的助手会解释自己为什么反对，而不是敷衍回避 |
| [0016](lessons/0016-rlaif-how-well-ai-feedback-actually-matches-human-feedback.md) | RLAIF：AI 反馈与人类反馈究竟有多吻合 | 一个模型以自己的规模评判自己的输出，依然胜过了单纯的监督微调 |
| [0017](lessons/0017-measuring-the-alignment-tax.md) | 度量对齐税 | 这笔税并不会在所有地方同时出现，甚至有一个维度测出的是提升而不是下降 |
| [0018](lessons/0018-reward-hacking-after-the-fact.md) | 事后的奖励破解 | 留出的奖励模型可以在训练过程中发现漂移；已经完成的模型则需要另一种检查 |
| [0019](lessons/0019-choosing-between-sft-dpo-ppo-and-grpo.md) | 在 SFT、DPO、PPO 和 GRPO 之间做选择 | 只有当更便宜的那种方法确实无法表达目标行为时，每种方法比前一种多花的成本才算值得 |
| [0020](lessons/0020-reviewing-someone-elses-alignment-recipe.md) | 评审别人的对齐方案 | 按顺序走完本系列涵盖的流水线的每一个阶段，并且依据来源，而不是一次自信的复述，来裁定有争议的声明 |

## 参考

- [术语表](GLOSSARY.md)：本主题的规范术语
- [资源](RESOURCES.md)：可信的资料来源

## 使用方式

每节课都简短且自成一体。答案默认折叠：先自己回忆，再展开查看。真实场景中的练习比阅读更重要，而把练习间隔开来正是关键。课程结束时仍不清楚的地方，值得先追溯到一手资料再继续往下学。
