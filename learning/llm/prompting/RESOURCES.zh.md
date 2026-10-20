---
title: 资源
description: "提示词工程的可信资料来源"
type: resources
---

# 提示词工程资源

## 知识

- [文档：“Prompting best practices”，Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
  某一家厂商的综合指南：清晰的指令、示例、XML 标签、角色、思考、长上下文和输出格式，并附有改写前后的提示词对照。用途：第 2 到 6 阶段的从业者基线，请把它当作一家厂商文档记载的行为来读。
- [文档：“Prompt engineering overview”，Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
  建议在迭代之前先定义成功标准和测试，并简要提醒：并非每个失败的评测都最适合用提示词来修。用途：先度量再改的习惯。
- [文档：“Prompting best practices”，Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#long-context-prompting)
  把长文档放在问题之前，用标签包裹每份文档并附上其元数据，并先要求模型给出相关引文。用途：安排长输入的布局。
- [文档：“Structured outputs”，Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
  服务商提供的功能，可对响应强制执行 JSON schema，文档同时说明了仅靠提示词无法保证什么。用途：区分“要求结构”和“强制结构”的界线。
- [文档：“Prompt caching”，Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
  缓存的前缀如何被匹配、什么会使它失效，以及提示词要命中缓存必须保持的顺序。用途：安排提示词布局，让其中稳定的部分被缓存。
- [文档：“Model IDs and versioning”，Claude Platform Docs](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions)
  一家厂商如何命名固定的模型快照和会移动的别名，以及每个 ID 都有各自的退役时间表。用途：把提示词固定到测试它时所用的模型。
- [文档：“Extended thinking”，Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
  思考阶段的 API 机制：token 预算、其最小值，以及思考如何计入输出上限。用途：给推理模型写提示词背后的预算事实；措辞方面的建议见最佳实践指南。
- [文档：“Define success criteria and build evaluations”，Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
  把“这份提示词是不是更好”转化为成功标准和评测设计，包括边界用例以及与基线的对比。用途：在动手修改之前，先确定提示词改动应当以什么为标准来评判。
- [文档：“Mitigate jailbreaks and prompt injections”，Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks)
  提示词层面和系统层面的缓解措施，包括筛查输入和限制模型能做的事。用途：哪些防御是提示词作者应当负责的。
- [文档：“Prompt design strategies”，Gemini API，Google](https://ai.google.dev/gemini-api/docs/prompting-strategies)
  第二家厂商的指南，涵盖指令、少样本示例、前缀和任务拆解。用途：核对某项技术是通用的，还是只是某一家厂商的行为。
- [文档：“Chat templates”，Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
  一组带角色标签的消息如何被渲染成模型训练时使用的单一 token 序列，并附有真实的模板输出。用途：模型实际看到的是什么。
- [仓库：“Prompt engineering interactive tutorial”，Anthropic](https://github.com/anthropics/prompt-eng-interactive-tutorial)
  涵盖角色、把数据与指令分开、示例、逐步推理以及避免幻觉的 notebook 练习。用途：第 1 到 4 阶段的练习。
- [论文：“The Prompt Report: A Systematic Survey of Prompting Techniques”，Schulhoff 等，2024](https://arxiv.org/abs/2406.06608)
  对提示技术的综述和分类，术语一致。用途：给你在实际中遇到的某项技术定位，并厘清某个术语的含义。
- [论文：“Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design”，Sclar 等，2023](https://arxiv.org/abs/2310.11324)
  表明不改变语义的格式改动（分隔符、大小写、空格）能让少样本的准确率大幅波动。用途：为什么一次提示词编辑是需要检验的论断，而不是风格选择。
- [论文：“Rethinking the Role of Demonstrations”，Min 等，2022](https://arxiv.org/abs/2202.12837)
  发现随机替换示例的标签几乎没有影响，而格式、标签空间和输入分布才是关键。用途：少样本示例究竟教会了模型什么。
- [论文：“Calibrate Before Use: Improving Few-Shot Performance of Language Models”，Zhao 等，2021](https://arxiv.org/abs/2102.09690)
  指出少样本提示词中的多数标签偏差、近因偏差和常见 token 偏差，并提出上下文校准。用途：一组示例会带来哪些偏差。
- [论文：“Fantastically Ordered Prompts and Where to Find Them”，Lu 等，2021](https://arxiv.org/abs/2104.08786)
  表明同样的少样本示例，仅仅改变顺序，准确率就能从接近当时最佳水平摆动到接近随机。用途：为什么示例顺序是一个需要控制的变量。
- [论文：“Chain-of-Thought Prompting Elicits Reasoning in Large Language Models”，Wei 等，2022](https://arxiv.org/abs/2201.11903)
  少样本思维链最初的结果，以及其发现：只有模型规模足够大时才会出现收益。用途：何时要求推理有帮助。
- [论文：“Large Language Models are Zero-Shot Reasoners”，Kojima 等，2022](https://arxiv.org/abs/2205.11916)
  零样本思维链：仅用一句触发语，就能在没有示例的情况下引出推理。用途：不靠手写示例获得推理。
- [论文：“Self-Consistency Improves Chain of Thought Reasoning in Language Models”，Wang 等，2022](https://arxiv.org/abs/2203.11171)
  采样多条推理路径并取多数答案。用途：在答案唯一且可检验的任务上，用 token 换取准确率。
- [论文：“Language Models Don't Always Say What They Think”，Turpin 等，2023](https://arxiv.org/abs/2305.04388)
  表明模型的思维链会遗漏真正驱动其答案的那个带偏见的特征。用途：为什么写出来的推理不是忠实的解释。
- [论文：“Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models”，Tam 等，2024](https://arxiv.org/abs/2408.02442)
  测得在严格的输出格式约束下，推理准确率会下降。用途：强制格式的代价，以及如何安排字段顺序。
- [论文：“Lost in the Middle: How Language Models Use Long Contexts”，Liu 等，2023](https://arxiv.org/abs/2307.03172)
  U 形曲线：长上下文开头和结尾的信息比中间的信息被利用得更好。用途：决定文档和问题该放在哪里。
- [论文：“The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions”，Wallace 等，2024](https://arxiv.org/abs/2404.13208)
  定义了系统、用户和工具输出这几个权限级别，并训练模型在冲突时遵循更高的一级。用途：为什么指令所处的位置会改变它的分量。
- [论文：“When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models”，Zheng 等，2023](https://arxiv.org/abs/2311.10054)
  在四个模型家族和 2,410 个事实性问题上测试了系统提示词中的 162 种人设，发现与不设人设相比没有改善，人设的影响基本是随机的。用途：用数据解决关于角色提示的争论。
- [论文：“Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection”，Greshake 等，2023](https://arxiv.org/abs/2302.12173)
  提出了通过检索内容实现的间接提示词注入，并在真实应用上做了演示。用途：攻击者如何触达一个他们从未直接输入过的提示词。
- [论文：“Fine-Tuning or Retrieval? Comparing Knowledge Injection in LLMs”，Ovadia 等，2023](https://arxiv.org/abs/2312.05934)
  比较了无监督 fine-tuning 与检索在注入知识上的效果，发现无论是训练中见过的知识还是新事实，检索都始终更好。用途：在提示词、RAG 与 fine-tuning 之间做选择。
- [文章：“LLM01:2025 Prompt Injection”，OWASP Gen AI Security Project](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
  业界的风险条目：直接与间接注入、影响，以及按所处层级排序的缓解措施。用途：共同的词汇和缓解措施清单。
- [文章：“The lethal trifecta for AI agents”，Simon Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
  私有数据、不可信内容和外泄通道同时具备时，注入就会变得可被利用，去掉其中一环就是防御。用途：为什么真正的防御在提示词之外。
- [文章：“Your AI Product Needs Evals”，Hamel Husain](https://hamel.dev/blog/posts/evals/)
  一位从业者的主张：以单元测试式的检查和记录下来的真实轨迹，作为迭代提示词的基础。用途：从真实失败出发建立回归集。

## 空白

- OpenAI 的提示词工程、推理和结构化输出指南本可以提供第三家厂商的视角，但 `platform.openai.com` 和 `developers.openai.com` 上的每个页面，在脚本检查和浏览器检查中都返回 403，因此无法确认任何一个页面能够访问。等能确认其中一个可访问时再补充。
- 没有同行评审的资料直接度量提示词的版本管理或模板实践。第 15 和第 16 课依据厂商文档和普通的软件工程实践来讲这部分内容，并如实说明了这一点。
