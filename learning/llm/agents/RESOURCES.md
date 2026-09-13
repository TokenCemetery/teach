---
title: Resources
description: "Trusted sources for LLM agents"
type: resources
---

# LLM Agents Resources

## Knowledge

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
  Draws the workflow against agent distinction this track is built on, then names the common composable patterns (prompt chaining, routing, parallelisation, orchestrator and workers, evaluator and optimiser) and argues for the simplest one that works. Use for: stage 1's vocabulary, and stage 16's case for not building an agent.
- [Guide: "A Practical Guide to Building Agents", OpenAI](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
  A second vendor's framing of the same material, covering when a task warrants an agent, tool categories, orchestration for one agent against many, and guardrails. Use for: checking that a claim in stage 1 or stage 8 is about agents rather than about one provider's product.
- [Article: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
  Treats a tool's name, description, parameter schema and return shape as prompt surface rather than as an API contract, including how a tool's output consumes the context budget. Use for: stage 4, and for why a tool designed like a REST endpoint makes a worse tool.
- [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  Argues for treating the context window as a finite budget to be curated, and covers compaction, note-taking to external memory, and sub-agents as context isolation. Use for: stages 5 and 6.
- [Paper: "ReAct: Synergizing Reasoning and Acting in Language Models", Yao et al., 2022](https://arxiv.org/abs/2210.03629)
  Introduces interleaving reasoning traces with tool actions in one loop, rather than planning fully upfront or acting without reasoning. Use for: stage 7, and for the naming of the pattern most agent loops still implement.
- [Paper: "Reflexion: Language Agents with Verbal Reinforcement Learning", Shinn et al., 2023](https://arxiv.org/abs/2303.11366)
  Introduces self-critique as an explicit loop stage: the agent reflects on a failed attempt in natural language and carries that reflection into the retry. Use for: stage 7's reflection material, and for what self-critique costs in tokens.
- [Paper: "Toolformer: Language Models Can Teach Themselves to Use Tools", Schick et al., 2023](https://arxiv.org/abs/2302.04761)
  Shows tool use being learned by the model rather than prompted, which is the boundary between this track and `llm/finetuning`. Use for: stage 2's explanation of why a model emits a tool call at all.
- [Specification: Model Context Protocol](https://modelcontextprotocol.io/specification)
  The normative specification for MCP: tools, resources, prompts, sampling, the transports, and the server lifecycle. Use for: stage 9, and for settling any MCP claim from the source rather than from a client's documentation.
- [Article: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
  Argues that presenting tools as code an agent writes against, rather than as individual tool definitions loaded into context, changes what a large tool set costs. Use for: stage 9's tool-discovery-at-scale problem and stage 10's code-execution material.
- [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
  A production account of an orchestrator and worker system, including the token cost multiple relative to a single agent and where coordination actually broke. Use for: stage 8's argument that multi-agent buys parallelism and context isolation, at a measured price.
- [Article: "Don't Build Multi-Agents", Cognition](https://cognition.ai/blog/dont-build-multi-agents)
  The opposing case, arguing that splitting work across agents fragments context and produces decisions that conflict. Use for: stage 8, read against the Anthropic account above rather than instead of it.
- [Article: "The Lethal Trifecta for AI Agents", Simon Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
  Names the combination that makes an agent exploitable: access to private data, exposure to untrusted content, and the ability to communicate externally. Use for: stage 14's central framing, and for why prompt instructions are not a defence.
- [Reference: "OWASP Top 10 for LLM Applications", OWASP GenAI Security Project](https://genai.owasp.org/llm-top-10/)
  The consensus catalogue of LLM application risks, including prompt injection, excessive agency and supply chain exposure, each with mitigations. Use for: stage 14's checklist, and for the vocabulary a security reviewer will already be using.
- [Specification: "Semantic Conventions for Generative AI", OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
  Vendor-neutral conventions for the spans and attributes an agent run emits, which is what makes one tracing backend's trajectory view readable in another. Use for: stage 12, as the provider-neutral answer to what a trace should contain.
- [Paper: "tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Yao et al., 2024](https://arxiv.org/abs/2406.12045)
  Evaluates agents on multi-turn tool use against a simulated user and a domain policy, and introduces a repeated-trial reliability measure rather than single-trial success. Use for: stage 13's distinction between succeeding once and succeeding reliably.
- [Paper: "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?", Jimenez et al., 2023](https://arxiv.org/abs/2310.06770)
  Evaluates agents on real repository issues with the project's own tests as the outcome check. Use for: stage 13's example of an outcome-graded benchmark where the trajectory is unconstrained.
- [Paper: "WebArena: A Realistic Web Environment for Building Autonomous Agents", Zhou et al., 2023](https://arxiv.org/abs/2307.13854)
  A self-hosted web environment with functional correctness checks, built for agents that act through a browser. Use for: stage 11, as the standard against which browser-agent reliability claims are made.
- [Paper: "GAIA: A Benchmark for General AI Assistants", Mialon et al., 2023](https://arxiv.org/abs/2311.12983)
  Questions that are easy for a person and hard for an agent, requiring multi-step tool use with a single unambiguous answer. Use for: stage 13, as the counterweight to benchmarks a model can pass without acting.

## Gaps

- No provider-neutral reference exists for tool-calling wire formats. Each provider documents only its own, so the captured request and response pairs this track shows have to be taken from provider documentation and reconciled by hand.
- Durable and resumable agent execution is documented mainly inside individual frameworks, which is neither provider-neutral nor stable enough to list yet. Stage 15 needs a source that is neither.
- Computer use and browser agents move faster than anything written about them. The listed benchmark papers cover how to evaluate one, not current practice for building one, so stage 11 is the thinnest-sourced part of the arc.
- Nothing listed yet covers agent memory across runs as a designed system rather than as a product feature. Stage 6 needs one.
