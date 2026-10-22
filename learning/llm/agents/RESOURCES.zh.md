---
title: 资源
description: "LLM 智能体的可信资料来源"
type: resources
---

# LLM 智能体资源

## 知识

- [文章：“Building Effective Agents”，Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
  划清了本系列所依据的工作流与智能体之间的区别，随后列出常见的可组合模式（提示词链、路由、并行化、编排者与工作者、评估者与优化者），并主张采用能奏效的最简单的那一种。用途：第 1 阶段的术语，以及第 16 阶段中不构建智能体的理由。
- [指南：“A Practical Guide to Building Agents”，OpenAI](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
  另一家厂商对同一批内容的阐述，涵盖什么样的任务值得用智能体、工具的类别、单智能体与多智能体的编排，以及护栏。用途：核对第 1 阶段或第 8 阶段中的某个说法讲的是智能体本身，而不是某一家服务商的产品。
- [文章：“Writing Effective Tools for Agents”，Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
  把工具的名称、描述、参数 schema 和返回形态当作提示词界面，而不是 API 契约，包括工具的输出如何消耗上下文预算。用途：第 4 阶段，以及为什么按 REST 端点方式设计的工具反而是更差的工具。
- [文章：“Effective Context Engineering for AI Agents”，Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  主张把上下文窗口当作需要精心整理的有限预算，涵盖压缩、把笔记记入外部记忆，以及作为上下文隔离的子智能体。用途：第 5 和第 6 阶段。
- [论文：“ReAct: Synergizing Reasoning and Acting in Language Models”，Yao 等，2022](https://arxiv.org/abs/2210.03629)
  提出在同一个循环中把推理轨迹与工具动作交错进行，而不是完全预先规划，或不加推理地行动。用途：第 7 阶段，以及这个至今仍被多数智能体循环实现的模式的命名由来。
- [论文：“Reflexion: Language Agents with Verbal Reinforcement Learning”，Shinn 等，2023](https://arxiv.org/abs/2303.11366)
  提出把自我批评作为循环中明确的一个阶段：智能体用自然语言反思一次失败的尝试，并把这份反思带入重试。用途：第 7 阶段的反思内容，以及自我批评在 token 上的成本。
- [论文：“Toolformer: Language Models Can Teach Themselves to Use Tools”，Schick 等，2023](https://arxiv.org/abs/2302.04761)
  展示了工具使用是由模型学会的，而不是靠提示词引导的，这正是本系列与 `llm/finetuning` 之间的分界。用途：第 2 阶段对模型为什么会发出工具调用的解释。
- [文档：“Tool use with Claude”，Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
  一家服务商自己对工具调用传输格式的说明：工具定义采用的 JSON schema、工具调用请求及其结果如何表示为消息，以及并行工具调用。用途：第 2 阶段抓取的请求与响应对，下面的 OpenAI 指南则作为差异来对照阅读。
- [指南：“Function calling”，OpenAI](https://developers.openai.com/api/docs/guides/function-calling)
  第二家服务商针对同一机制的传输格式，包括从单一函数调用转向通用工具调用约定的变化。用途：第 2 阶段，作为第二个服务商，其格式只作为与第一个的差异出现。
- [规范：Model Context Protocol](https://modelcontextprotocol.io/specification)
  MCP 的规范性文本：工具、资源、提示词、采样、传输方式和服务器生命周期。用途：第 9 阶段，以及用源头而不是某个客户端的文档来裁定任何关于 MCP 的说法。
- [文章：“Code Execution with MCP”，Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
  主张把工具呈现为智能体对着编写代码的接口，而不是加载进上下文的一个个单独的工具定义，这会改变大型工具集的成本。用途：第 9 阶段的大规模工具发现问题，以及第 10 阶段的代码执行内容。
- [文章：“How We Built Our Multi-Agent Research System”，Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
  对一个编排者与工作者系统的生产实践说明，包括相对单个智能体的 token 成本倍数，以及协调究竟在哪里出了问题。用途：第 8 阶段的论点，即多智能体换来的是并行和上下文隔离，价格是可度量的。
- [文章：“Don't Build Multi-Agents”，Cognition](https://cognition.ai/blog/dont-build-multi-agents)
  相反的观点，认为把工作分给多个智能体会割裂上下文，产生相互冲突的决策。用途：第 8 阶段，与上面 Anthropic 的说明对照着读，而不是取而代之。
- [文章：“The Lethal Trifecta for AI Agents”，Simon Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
  指出让智能体变得可被利用的那种组合：可访问私有数据、会接触不可信内容、能够向外部通信。用途：第 14 阶段的核心框架，以及为什么提示词里的指令不是防御手段。
- [参考：“OWASP Top 10 for LLM Applications”，OWASP GenAI Security Project](https://genai.owasp.org/llm-top-10/)
  LLM 应用风险的共识性目录，包括提示词注入、过度授权（excessive agency）和供应链暴露，每项都附有缓解措施。用途：第 14 阶段的检查清单，以及安全评审者已经在使用的术语。
- [规范：“Semantic Conventions for Generative AI”，OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
  智能体一次运行所产生的 span 和属性的、与厂商无关的约定，这使得一个追踪后端的轨迹视图在另一个后端里也能读懂。用途：第 12 阶段，作为“追踪应包含什么”的、与服务商无关的答案。
- [论文：“tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains”，Yao 等，2024](https://arxiv.org/abs/2406.12045)
  在模拟用户和领域策略之下，评估智能体的多轮工具使用，并提出一种基于重复试验的可靠性度量，而不是单次试验的成功率。用途：第 13 阶段中“成功一次”与“可靠地成功”的区别。
- [论文：“SWE-bench: Can Language Models Resolve Real-World GitHub Issues?”，Jimenez 等，2023](https://arxiv.org/abs/2310.06770)
  在真实的代码仓库 issue 上评估智能体，以项目自己的测试作为结果检查。用途：第 13 阶段中，按结果评分、轨迹不受约束的基准测试的例子。
- [文档：“Computer use tool”，Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
  描述了使用计算机的智能体所运行的“截图加动作”循环：观察是一张截图，而不是工具结果；动作是屏幕坐标或一次按键，而不是函数参数。用途：第 11 阶段中把动作落到坐标上的内容，以及为什么这个循环需要一套与调用工具的循环不同的可靠性方案。
- [论文：“WebArena: A Realistic Web Environment for Building Autonomous Agents”，Zhou 等，2023](https://arxiv.org/abs/2307.13854)
  一个自托管的网页环境，带有功能正确性检查，专为通过浏览器行动的智能体而建。用途：第 11 阶段，作为衡量浏览器智能体可靠性主张所依据的标准。
- [论文：“GAIA: A Benchmark for General AI Assistants”，Mialon 等，2023](https://arxiv.org/abs/2311.12983)
  对人来说容易、对智能体来说困难的问题，需要多步工具使用，且只有唯一明确的答案。用途：第 13 阶段，用来平衡那些模型不必行动就能通过的基准测试。
- [文档：“Prompt caching”，Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
  缓存提示词前缀以降低重复的成本和延迟，包括为什么智能体稳定的工具定义和系统提示词恰恰是值得缓存的前缀，以及什么会悄悄让缓存失效。用途：第 15 阶段的 token 放大与成本内容。

## 空白

- 目前没有与服务商无关的、关于工具调用传输格式的参考资料。每家服务商只记录自己的格式，所以本系列展示的请求与响应对，只能取自服务商文档并手工对齐。
- 持久且可恢复的智能体执行主要记录在各个框架内部，既不与服务商无关，也还不够稳定，不适合列出。第 15 阶段需要一份两者都不是的来源。
- 计算机使用与浏览器智能体的发展速度快过关于它们的任何文字。所列的基准测试论文讲的是如何评估这类智能体，而不是当前构建它们的实践，所以第 11 阶段是整条学习路线中资料最薄弱的部分。
- 目前所列的内容，没有一份把跨运行的智能体记忆当作一个设计出来的系统来讲，而不是当作产品功能。第 6 阶段需要这样一份。
