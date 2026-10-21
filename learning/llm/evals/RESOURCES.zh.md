---
title: "资源"
description: "评测的可信资料来源"
type: resources
---

# 评测资源

## 知识

- [文档：“Define success criteria and build evaluations”，Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
  从业者的实操讲解，如何把含糊的“有没有变好”这个问题，变成可度量的成功标准和留出的评测集。用途：在动手选框架之前，先设计评测本身。
- [仓库：openai/evals，OpenAI](https://github.com/openai/evals)
  把评测定义并运行为代码的官方框架：提示词、评分逻辑，以及一个可当作实例来读的现有评测注册表。用途：如何组织并运行自建的评测。
- [仓库：lm-evaluation-harness，EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  事实上的标准运行框架，用来让模型跑标准化的基准，其任务配置展示了留出集在实践中是如何组织和打分的。用途：运行或改造现有的基准，而不是从零搭建评测。
- [论文：“Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena”，Zheng 等，2023](https://arxiv.org/abs/2306.05685)
  为开放式任务引入了 LLM-as-judge，并对照人类偏好度量了它的偏差：位置偏差、冗长偏差、自我偏好偏差。用途：判断 LLM 裁判对给定情形是否可信，以及可信时需要校正什么。
- [文档：Evaluate，Hugging Face](https://huggingface.co/docs/evaluate/index)
  标准的针对具体任务的指标库（BLEU、ROUGE、精确匹配、F1 等），附每个指标的定义和失败模式。用途：指标与 LLM 裁判之争中，针对具体任务的指标这一侧。
- [论文：“Time Travel in LLMs: Tracing Data Contamination in Large Language Models”，Golchin 和 Surdeanu，2023](https://arxiv.org/abs/2308.08493)
  一种具体的方法，用来检验某个基准的数据是否泄漏进了模型的训练集，其中猜测样本其余部分的技术能抓出泄漏。用途：为留出集的诚实性辩护，抵御“模型只是背下了这些”这一具体指控。
- [论文：“Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models”（BIG-bench），Srivastava 等，2022](https://arxiv.org/abs/2206.04615)
  引入了金丝雀字符串的约定（在基准数据中嵌入一个独一无二的标记短语，请求爬虫把它从训练语料中排除），作为基准自身发布时的一种预防性抗污染技术。用途：设计自建的评测集，使它从一开始就能抵御污染，而不是事后才去检测。
- [论文：“Evaluating Large Language Models Trained on Code”（Codex），Chen 等，2021](https://arxiv.org/abs/2107.03374)
  引入了功能正确性（让生成的代码去执行测试用例，而不是比较文本）和无偏的 pass@k 估计量，其组合公式避免了直接重新采样 k 个补全所带来的高方差。用途：评测代码生成，以及凡是任务可以执行，就检查行为而不是文本相似度这一通用原则。

- [文章：“Cohen's kappa”，Wikipedia](https://en.wikipedia.org/wiki/Cohen%27s_kappa)
  经过偶然校正的评分员间一致性统计量：它的公式、为什么 kappa 为 0 意味着不比偶然好，以及它在稀有类别上低估一致性的已知倾向。用途：精确地度量人工评分员的一致性，而不是目测原始的一致百分比。
- [文章：“Inter-rater reliability”，Wikipedia](https://en.wikipedia.org/wiki/Inter-rater_reliability)
  讲解为什么原始的联合概率一致率会产生误导（被偶然性抬高，类别越少越严重），以及 Krippendorff's alpha 作为经偶然校正的一致性在任意数量评分员、任意度量层级上的推广。用途：当评分员多于两位或评分不是分类型时，选出合适的一致性统计量。
- [论文：“HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal”，Mazeika 等，2024](https://arxiv.org/abs/2402.04249)
  提出了一个标准化的框架，用来大规模、可比较地评估自动化红队方法对模型和防御的攻击，而此前这个领域缺少这样的框架。用途：把攻击成功率作为指标，以及攻击生成方法与严格评估它的方法之间的区别。
- [论文：“XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models”，Röttger 等，2023](https://arxiv.org/abs/2308.01263)
  一套安全提示词的测试集，写得像不安全的提示词，专门用来暴露过度拒答。用途：无害性（拒绝不安全的提示词）与有用性（不拒绝安全的提示词）之间的确切张力，以及度量模型在这一权衡上落点不佳的具体方法。
- [论文：“τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains”，Yao 等，2024](https://arxiv.org/abs/2406.12045)
  通过把对话结束时的数据库状态与标注的目标状态作比较来评测智能体，并引入 `pass^k`，用来度量智能体在同一任务重复试验中的可靠性。用途：为什么任务成功率胜过逐步的轨迹匹配，以及 `pass^k` 与第 4 课的 `pass@k` 之间精确而容易混淆的区别。
- [论文：“AgentBench: Evaluating LLMs as Agents”，Liu 等，2023](https://arxiv.org/abs/2308.03688)
  一个多维度的基准，覆盖 8 个不同的交互环境，测试 LLM 作为智能体的推理和决策能力，发现顶尖模型与较小模型之间，恰恰在智能体场景中存在显著差距。用途：证明智能体能力是需要单独度量的东西，不能由单轮基准的表现推知。
- [论文：“Ragas: Automated Evaluation of Retrieval Augmented Generation”，Es 等，2023](https://arxiv.org/abs/2309.15217)
  一个无参照的框架，把 RAG 系统的检索质量、忠实性和生成质量三个维度拆成相互独立的指标。用途：无需人工撰写的标准答案就能算出忠实性分数，并让检索失败和生成失败作为两个独立的问题保持可诊断。
- [论文：“Enabling Large Language Models to Generate Text with Citations”（ALCE），Gao 等，2023](https://arxiv.org/abs/2305.14627)
  引入了与人类判断相关的自动引用质量指标，并发现在一个测试集上，即便是顶尖的系统，也有大约一半的论断缺乏完整的引用支持。用途：引用正确性，作为比忠实性更严格、独立的检查。
- [论文：“Seven Rules of Thumb for Web Site Experimenters”，Kohavi 等，2014](https://exp-platform.com/Documents/2014%20experimentersRulesOfThumb.pdf)
  Kohavi 及其合著者对运行在线对照实验的从业指导，包括 OEC 的概念（可移动，并与真实结果有因果联系）和护栏指标。用途：选出经得起辩护的 OEC，而不是容易移动却没有因果关系的指标，以及为什么必须同时跟踪护栏指标。
- [指南：“Rules of Machine Learning”，Zinkevich，Google](https://developers.google.com/machine-learning/guides/rules-of-ml)
  Google 内部的机器学习工程指导，包括规则 37（把训练与服务偏差度量为几种不同的比较，而不是一种）和规则 8（新鲜度要求）。用途：离线与线上差距的几种可能成因，即普通方差、漂移或工程错误，究竟是哪一种适用，以及为什么每一种需要不同的修复。
- [论文：“The Tail at Scale”，Dean 和 Barroso，2013](https://www.barroso.org/publications/TheTailAtScale.pdf)
  关于为什么在大规模下决定实际响应速度的是尾部延迟而不是平均延迟的经典解释，尤其是一个请求扇出到许多后端调用的时候。用途：为什么在排除延迟退步之前，上线与否的判断需要百分位数（p95/p99），而不只是平均值。
- [论文：“The Leaderboard Illusion”，Singh 等，2025](https://arxiv.org/abs/2504.20879)
  记录了 Chatbot Arena 上的选择性披露：对许多模型变体做私下的发布前测试（仅 Llama 4 就有 27 个），以及对少数闭源模型服务商有利的、庞大而不对称的数据访问。用途：一个具体、当下、有详细记录的例子，说明为什么排行榜名次本身并不是中立、可信的度量。
- [文章：“Does Style Matter?”，LMArena](https://lmarena.ai/blog/style-control)
  竞技场自己的分析，显示一旦控制了回答的长度和 markdown 格式，排名就会发生明显变化。用途：确认第 6 课的冗长偏差机制，在整个排行榜的规模上同样成立，只是评分者换成了人类，而不是单个 LLM 裁判。

## 空白

- 目前还没有专门讲评测分数差异的统计显著性检验的资料（比例的标准误差，以及 McNemar 检验之类的成对显著性检验）。阶段 5 的“这个差异是真实的还是噪声”这一问题需要它；第 9 课讲授它，依据的是稳定、标准的统计方法，而不是单一的引用来源，等找到一个合适的、面向从业者的资料后，这个空白就应当补上。
