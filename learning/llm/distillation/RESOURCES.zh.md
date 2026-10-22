---
title: "资源"
description: "LLM 知识蒸馏的可信资料来源"
type: resources
---

# 蒸馏资源

## 知识

### 基础

- [论文：“Distilling the Knowledge in a Neural Network”，Hinton、Vinyals 和 Dean，2015](https://arxiv.org/abs/1503.02531)
  为这种方法命名的论文：软目标、温度、T 平方的梯度修正和组合损失，附有 MNIST 与语音实验。用途：第 1 阶段，直接读原始来源。
- [论文：“A Survey on Knowledge Distillation of Large Language Models”，Xu 等，2024](https://arxiv.org/abs/2402.13116)
  一张 LLM 蒸馏的地图，按从教师那里引出什么、以及学生如何在其上训练来组织。用途：在阅读某个方法自己的论文之前，先把它放进更大的方法族里。
- [论文：“DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter”，Sanh 等，2019](https://arxiv.org/abs/1910.01108)
  在预训练期间对 Transformer 做蒸馏的完整实例，使用由蒸馏、掩码语言建模和余弦嵌入三项组成的三重损失。用途：一份完整的配方，并对每一项损失做了消融。

### logit 蒸馏与序列级蒸馏

- [论文：“Sequence-Level Knowledge Distillation”，Kim 和 Rush，2016](https://arxiv.org/abs/1606.07947)
  在翻译任务上比较词级与序列级蒸馏，以及在教师的束搜索输出上训练。用途：第 2 和第 3 阶段，两个层级最初的提法。
- [论文：“MiniLLM: On-Policy Distillation of Large Language Models”，Gu 等，2023](https://arxiv.org/abs/2306.08543)
  在生成式蒸馏中使用反向 KL 的论证，用策略梯度方法在学生的样本上优化。用途：前向 KL 与反向 KL 的对比，以及在策略蒸馏的一种形式。
- [论文：“Towards Cross-Tokenizer Distillation: the Universal Logit Distillation Loss for LLMs”，Boizard 等，2024](https://arxiv.org/abs/2402.12030)
  一种基于最优传输的损失，比较排序后的概率向量，使教师与学生不必共享词表。用途：跨分词器蒸馏做了什么、又放弃了什么。
- [论文：“Gemma 2: Improving Open Language Models at a Practical Size”，Gemma Team，2024](https://arxiv.org/abs/2408.00118)
  用来自更大教师的知识蒸馏，而不是下一个 token 预测，来训练 2B 和 9B 模型。用途：作为预训练信号的蒸馏。
- [论文：“Compact Language Models via Pruning and Knowledge Distillation”，Muralidharan 等，2024](https://arxiv.org/abs/2407.14679)
  Minitron：对训练好的模型做剪枝，再用来自原模型的蒸馏对它重新训练，只用原始训练 token 的一小部分。用途：作为剪枝之后恢复步骤的蒸馏。
- [论文：“LLM Pruning and Distillation in Practice: The Minitron Approach”，Sreenivas 等，2024](https://arxiv.org/abs/2408.11796)
  把 Minitron 的配方应用到 Llama 3.1 8B 和 Mistral NeMo 12B 上，其中包括先在蒸馏数据上校正教师。用途：同一份配方的第二次、也是更新的一次运行。

### 合成数据蒸馏

- [论文：“Self-Instruct: Aligning Language Models with Self-Generated Instructions”，Wang 等，2022](https://arxiv.org/abs/2212.10560)
  用模型自己的生成结果自举出指令数据，并过滤近似重复和无效的样本。用途：生成式指令数据集是怎样构建的。
- [文章：“Alpaca: A Strong, Replicable Instruction-Following Model”，Stanford CRFM，2023](https://crfm.stanford.edu/2023/03/13/alpaca.html)
  用 Self-Instruct 方法，在 text-davinci-003 生成的 5.2 万条指令上微调 LLaMA 7B，包括它的成本，以及它自己声明的局限和许可限制。用途：典型的低成本模仿运行。
- [论文：“Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes”，Hsieh 等，2023](https://arxiv.org/abs/2305.02301)
  训练小模型在产出标签的同时，把产出教师的推理依据作为第二项任务。用途：推理依据相比只用标签多出了什么。
- [论文：“Orca: Progressive Learning from Complex Explanation Traces of GPT-4”，Mukherjee 等，2023](https://arxiv.org/abs/2306.02707)
  模仿用系统提示词引出的解释轨迹，并以 ChatGPT 作为 GPT-4 之前的中间教师。用途：LLM 规模上的解释轨迹与助教模型。
- [论文：“Textbooks Are All You Need”，Gunasekar 等，2023](https://arxiv.org/abs/2306.11644)
  phi-1：一个小型代码模型，用过滤后的网络数据，以及由 GPT-3.5 生成的合成教科书和习题来训练。用途：数据质量与数据数量的对比。
- [论文：“DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning”，DeepSeek-AI，2025](https://arxiv.org/abs/2501.12948)
  通过在其精选样本上微调，把推理模型蒸馏进更小的 Qwen 和 Llama 模型，并与直接在小模型上运行强化学习做比较（附录 F.1）。用途：经过拒绝采样的合成数据，以及本系列所链接的后训练那一课。

### 在策略蒸馏

- [论文：“On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes”，Agarwal 等，2023](https://arxiv.org/abs/2306.13649)
  广义知识蒸馏：在学生生成的序列上训练，可以选择散度，并混合固定数据与在策略数据。用途：第 5 阶段，直接读原始来源。
- [论文：“Qwen3 Technical Report”，Qwen Team，2025](https://arxiv.org/abs/2505.09388)
  小型 Qwen3 模型的由强到弱蒸馏，先是离策略阶段，再是在策略阶段，并与在这些模型上做强化学习作了比较。用途：生产级模型家族中的在策略蒸馏。
- [文档：“Generalized Knowledge Distillation Trainer”，Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gkd_trainer)
  GKD 在 TRL 中的实现，以及它的 `lmbda`、`beta` 和 `seq_kd` 参数。用途：亲手运行在策略蒸馏，而不是只读文字介绍。
- [文档：“General Online Logit Distillation (GOLD) Trainer”，Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gold_trainer)
  TRL 中用通用 logit 蒸馏损失扩展 GKD 的训练器，通过对齐文本片段，使教师和学生可以使用不同的分词器。用途：一次跨分词器的在策略运行需要什么。

### 学生继承什么

- [论文：“Does Knowledge Distillation Really Work?”，Stanton 等，2021](https://arxiv.org/abs/2106.05945)
  学生即使有足够的容量，也常常无法与教师匹配，而更好的泛化并不需要更高的保真度。实验大多是图像分类，另有一项文本任务。用途：把保真度与任务质量分开。
- [论文：“The False Promise of Imitating Proprietary LLMs”，Gudibande 等，2023](https://arxiv.org/abs/2305.15717)
  被众包标注者评为接近 ChatGPT 的模仿模型，在针对性的基准上几乎没有缩小差距。用途：模仿差距，以及人类偏好评分如何把它掩盖了。
- [论文：“Improved Knowledge Distillation via Teacher Assistant”，Mirzadeh 等，2019](https://arxiv.org/abs/1902.03393)
  教师与学生的差距变得过大时，学生质量会下降，而一个中等规模的助教能挽回一部分；它在视觉实验中的收益很小。用途：容量差距。
- [论文：“On the Efficacy of Knowledge Distillation”，Cho 和 Hariharan，2019](https://arxiv.org/abs/1910.01348)
  更准确的教师并不总能训练出更好的学生，而提前停止教师的训练可能有帮助。用途：对容量差距的第二种解释。
- [论文：“Subliminal Learning: Language models transmit behavioral traits via hidden signals in data”，Cloud 等，2025](https://arxiv.org/abs/2507.14805)
  在教师生成的数字序列上训练的学生，在二者共用同一个基础模型时，习得了教师的特质。用途：过滤数据也去除不掉的东西。

### 确定规模

- [论文：“Distillation Scaling Laws”，Busbridge 等，2025](https://arxiv.org/abs/2502.08606)
  把学生质量表示为学生规模、蒸馏 token 数和教师质量的函数的缩放定律，以及蒸馏何时胜过对同一个学生的监督训练。它还报告说，在其设置中最佳的蒸馏温度是 1（附录 G.2）。用途：第 7 阶段，直接读原始来源，也是对 LLM 上温度大于 1 这一做法的反例。

### 许可与条款

- [条款：“Terms of Use”，OpenAI](https://openai.com/policies/row-terms-of-use/)
  OpenAI 面向欧洲经济区、瑞士和英国以外用户的消费者条款，其中把使用输出来开发与 OpenAI 竞争的模型，列为用户不得做的事情之一。用途：托管服务商的条款对用它的输出做训练是怎么说的。
- [许可：“Llama 3.1 Community License Agreement”，Meta](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE)
  一份开放权重的许可，允许用模型的输出来改进另一个模型，条件是最终模型在分发时，其名称以 “Llama” 开头。用途：开源模型的许可对用它的输出做训练是怎么说的。

## 空白

- Thinking Machines 那篇关于在策略蒸馏的文章，因与强化学习的成本比较而被广泛引用，但它的站点拒绝脚本化读取和应用内读取，所以这里没有采用它的任何数字。第 5 阶段改为依据 GKD、MiniLLM 和 Qwen3 的论文。
- 使用条款和许可的变动没有课程可以固定的版本号。第 0013 课引用的是编写本系列时读到的内容；依赖它之前，请重新核对来源。
