---
title: LLM Agents
description: "Build the loop yourself: tools, context, memory, and knowing when an agent is the wrong answer"
type: topic
---

# LLM Agents

Be able to build an agent loop yourself, decide whether a given task needs an agent at all rather than a fixed workflow, and diagnose a failing agent from its trajectory instead of adding another instruction to its prompt.

**Latest lesson:** [0037. Reviewing Someone Else's Agent Design](lessons/0037-reviewing-someone-elses-agent-design.md)

## Success looks like

- Write the agent loop for a stated task, and name what every message in its context is doing and what ends the loop.
- Choose between a single prompt, a fixed workflow, and an agent for a given task, and defend the choice against the cost of the option you rejected.
- Design an agent's tool surface: names, descriptions, return shapes, and the permission boundary that decides what it may do unattended.
- Diagnose a failing agent from its trajectory, naming the cause (a loop, poisoned context, a mis-specified tool, a wrong stopping condition) rather than re-prompting at random.
- Explain why an agent that reads untrusted content cannot be secured by prompt instructions alone, and design the boundary that actually holds.
- Budget the token cost and latency of an agentic loop, and say which part of the loop the amplification comes from.

## Constraints

- Provider-neutral. Loops, tool schemas and control flow are given as Python-like pseudocode, so the material survives the tool-calling API churn that dates most agent writing.
- Wire formats are the exception, because what a tool-call message looks like on the wire is a fact rather than an algorithm. One real captured request and response pair is shown, and a second provider appears only as the diff from it.
- No framework is assumed or taught. What a framework buys (durable state, graph control flow, resumption) is covered once, near the end, as a decision rather than a tutorial.
- Reps are inspection-heavy rather than build-heavy: reading a real trace, a real tool schema, a real MCP server manifest, and marking the permission boundary of an agent that already runs.
- Assumes familiarity with what a language model is and comfort reading Python-like code. No prior agent-building experience required.

## Out of scope

- Evaluation as a discipline: see [`llm/evals`](../../llm/evals/) (lesson 0013 covers trajectories, task success against step accuracy, and `pass^k`). Carried here only as the one capability an agent builder needs, and linked to rather than restated.
- Retrieval pipeline internals: see [`llm/rag`](../../llm/rag/). Retrieval appears here as a tool an agent calls, not as chunking, embedding and reranking.
- Serving and inference internals: see [`llm/inference`](../../llm/inference/) for latency, batching and constrained decoding.
- Training a model to use tools: see [`llm/finetuning`](../../llm/finetuning/).
- Retries, idempotency and partial failure as distributed-systems problems: see [`architecture/distributed-systems`](../../architecture/distributed-systems/). Covered here only for what makes a tool call different from an ordinary remote call.

## The arc

Sixteen stages, from no prior knowledge to senior judgment. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Lessons | Covers | Done when |
| --- | --- | --- | --- |
| 1. What an agent is | 0001 to 0002 | The loop, agent against workflow against chain, the autonomy spectrum | Can classify a system and say whether "agent" is the right word for it |
| 2. Tool calling mechanics | 0003 to 0005 | The wire format of a tool call, parameter schemas, who executes what, parallel calls, errors returned as results | Can read a raw tool-call exchange and say what each message did |
| 3. The loop from scratch | 0006 to 0007 | Writing the loop, stopping conditions, the transcript as the agent's whole state | Can write an agent loop and defend where it stops |
| 4. Tool design as prompt engineering | 0008 to 0009 | Names and descriptions as prompt surface, return shapes, result token cost, tool-set bloat | Can design a tool surface and say why each description is worded as it is |
| 5. Context management | 0010 to 0012 | The window as the central budget: truncation, compaction, retrieval on demand, sub-agents as context isolation | Can plan what leaves the context, and when, for a long-running task |
| 6. Memory and state | 0013 to 0014 | Within-run scratchpad against across-run memory, files as memory, why retrieval is not memory | Can choose where a given fact lives and say what happens when the run ends |
| 7. Planning and reflection | 0015 to 0017 | ReAct, plan-then-execute, self-critique, decomposition, what reasoning models changed | Can pick a planning pattern for a task and name what it costs in tokens and latency |
| 8. Multi-agent | 0018 to 0019 | Orchestrator and worker, handoff, fan-out, coordination cost, when one agent with better tools wins | Can say whether a second agent buys anything the first could not have been given |
| 9. Protocols and interop | 0020 to 0021 | MCP's tools, resources, prompts and transports, provider function-calling formats, tool discovery at scale | Can read an MCP server's manifest and say what it exposes and what it does not standardise |
| 10. Execution environments | 0022 to 0023 | Sandboxing, code execution as a tool, filesystem access, human-in-the-loop approval gates | Can place the sandbox boundary for a stated set of tools |
| 11. Computer use and browser agents | 0024 to 0026 | Screenshots as observations, grounding an action to a coordinate, the reliability problem | Can say why a screen-driving agent fails differently from a tool-calling one |
| 12. Failure modes and observability | 0027 to 0029 | Loops, context poisoning, cascading tool errors, hallucinated arguments, tracing and trajectory replay | Given a trajectory, can name the at-fault step rather than re-prompting |
| 13. Evaluating an agent | 0030 to 0030 | Outcome against trajectory, repeated-trial reliability, what the agent benchmarks actually measure | Can say what to measure for a given agent, and hand the rest to `llm/evals` |
| 14. Security | 0031 to 0032 | Prompt injection as the defining agent problem, the lethal trifecta, least privilege, the confused deputy, MCP supply chain | Can design a permission boundary that holds when the agent reads hostile content |
| 15. Production, cost, and what frameworks buy | 0033 to 0035 | Token amplification, prompt caching, concurrency, durability and resumability, cost per completed task | Can budget a loop's cost and say which framework guarantee a deployment actually needs |
| 16. Judgment | 0036 to 0037 | When not to build an agent, reviewing someone else's agent design and naming what a choice costs, settling a disputed claim from the primary source | Trusted to make the call and to explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-the-agent-loop.md) | The Agent Loop | What makes a system an agent, and the four-step cycle that runs underneath one |
| [0002](lessons/0002-agent-workflow-or-prompt.md) | Agent, Workflow, or Just a Prompt | Where a task sits on the autonomy spectrum, and how to defend the choice |
| [0003](lessons/0003-the-wire-format-of-a-tool-call.md) | The Wire Format of a Tool Call | What a tool call and its result actually look like in the protocol between your harness and the model provider |
| [0004](lessons/0004-schemas-and-who-executes.md) | Parameter Schemas and Who Executes What | How JSON schemas constrain what a model can send, and the difference between client and server tools |
| [0005](lessons/0005-parallel-calls-and-errors-as-results.md) | Parallel Calls and Errors as Results | How a model can request multiple tools at once, and why tool errors are results, not exceptions |
| [0006](lessons/0006-writing-the-loop.md) | Writing the Loop | Building the agent loop from pseudocode and choosing stopping conditions deliberately |
| [0007](lessons/0007-the-transcript-as-state.md) | The Transcript as State | Understanding that the transcript is the agent's only persistent memory between turns |
| [0008](lessons/0008-naming-and-describing-a-tool.md) | Naming and Describing a Tool | A tool's name and description are what the model reads to decide when and how to call it |
| [0009](lessons/0009-return-shapes-and-tool-set-bloat.md) | Return Shapes and Tool-Set Bloat | A tool's return value costs context budget, and too many tools hurts the model's ability to pick correctly |
| [0010](lessons/0010-the-context-window-as-budget.md) | The Context Window as Budget | The context window is a finite resource the harness actively curates over time, not an inert log |
| [0011](lessons/0011-compaction-and-retrieval-on-demand.md) | Compaction and Retrieval on Demand | Two strategies for keeping a long-running agent's context under budget while preserving what still matters |
| [0012](lessons/0012-sub-agents-as-context-isolation.md) | Sub-Agents as Context Isolation | Spinning up a sub-agent isolates long exploratory work from the parent's context budget |
| [0013](lessons/0013-scratchpad-versus-memory.md) | Scratchpad Versus Memory | The difference between notes an agent keeps during one run and facts it needs across multiple runs |
| [0014](lessons/0014-files-as-memory.md) | Files as Memory | Using durable files as the simplest form of across-run memory for agents |
| [0015](lessons/0015-react-interleaving-reasoning-and-acting.md) | ReAct: Interleaving Reasoning and Acting | Pattern of pairing short reasoning steps with each action, so the model can observe and adapt |
| [0016](lessons/0016-plan-then-execute-and-decomposition.md) | Plan-Then-Execute and Decomposition | Explicit upfront planning as an alternative to ReAct, when to use it, and how to handle replanning |
| [0017](lessons/0017-self-critique-and-reasoning-models.md) | Self-Critique and What Reasoning Models Changed | Reflection loop as an explicit stage, its costs, and how extended internal reasoning affects when to use it |
| [0018](lessons/0018-orchestrator-and-worker.md) | Orchestrator and Worker | Design a multi-agent system where one agent plans and delegates, workers execute in parallel |
| [0019](lessons/0019-coordination-cost.md) | Coordination Cost | Understand why building multiple agents is more expensive than one well-equipped agent, and how to decide when the parallelism win is worth the cost |
| [0020](lessons/0020-mcp-tools-resources-and-prompts.md) | MCP: Tools, Resources, and Prompts | Model Context Protocol as a standardized interface for agent harnesses to discover and invoke external tools, read data, and use templates |
| [0021](lessons/0021-provider-formats-and-discovery-at-scale.md) | Provider Formats and Tool Discovery at Scale | How MCP and provider-specific wire formats are separate layers, and why loading every tool into context does not scale to many connected servers |
| [0022](lessons/0022-sandboxing-and-approval-gates.md) | Sandboxing and Approval Gates | Execution boundaries and human checkpoints that protect against model mistakes |
| [0023](lessons/0023-code-execution-as-a-tool.md) | Code Execution as a Tool | Giving an agent a single sandboxed code-execution tool instead of many narrow individual tools |
| [0024](lessons/0024-screenshots-as-observations.md) | Screenshots as Observations | How computer-use agents observe the screen as an image instead of structured data, and why the loop structure still holds |
| [0025](lessons/0025-grounding-an-action-to-a-coordinate.md) | Grounding an Action to a Coordinate | Why translating a visual intention into a pixel coordinate is harder and more fragile than a typed tool-call argument |
| [0026](lessons/0026-why-browser-agents-fail-differently.md) | Why Browser Agents Fail Differently | Screen-driven agents fail in ways tool-calling agents do not, and why WebArena created a benchmark to measure and study these failures |
| [0027](lessons/0027-loops-and-context-poisoning.md) | Loops and Context Poisoning | Two failure modes visible in a trajectory, repetitive loops and silent context poisoning, and how to spot each |
| [0028](lessons/0028-cascading-tool-errors.md) | Cascading Tool Errors and Hallucinated Arguments | One tool error leading to wrong decisions, spiraling into confusion, and well-typed but false arguments that schemas cannot catch |
| [0029](lessons/0029-tracing-and-trajectory-replay.md) | Tracing and Trajectory Replay | Using vendor-neutral trace conventions to capture agent runs, and replaying trajectories to step through failures |
| [0030](lessons/0030-evaluating-an-agent.md) | Evaluating an Agent | Measuring agent success at the outcome level versus the trajectory level, and why a single successful run does not mean the agent is reliable |
| [0031](lessons/0031-prompt-injection-and-the-lethal-trifecta.md) | Prompt Injection and the Lethal Trifecta | How agents reading untrusted content become exploitable, and why prompting alone does not secure them |
| [0032](lessons/0032-least-privilege-and-the-confused-deputy.md) | Least Privilege and the Confused Deputy | How to scope agent capabilities so that prompt injection causes contained damage instead of catastrophic breach |
| [0033](lessons/0033-token-amplification-and-cost.md) | Token Amplification and Cost per Completed Task | Why agentic systems consume far more tokens per completed task than a single prompt would, and how to budget for it |
| [0034](lessons/0034-prompt-caching-and-concurrency.md) | Prompt Caching and Concurrency | How caching reduces per-task token cost and how concurrency increases throughput, and why conflating them is a budgeting mistake |
| [0035](lessons/0035-durability-and-what-frameworks-buy.md) | Durability and What a Framework Buys | Durable, resumable agent execution as an engineering problem, what frameworks concretely offer, and a decision principle for adopting one |
| [0036](lessons/0036-when-not-to-build-an-agent.md) | When Not to Build an Agent | The judgment to decide whether a task actually needs an agent, and the discipline to say no when one is not worth its cost |
| [0037](lessons/0037-reviewing-someone-elses-agent-design.md) | Reviewing Someone Else's Agent Design | How to evaluate an agent system systematically, and how to settle a disputed claim by going back to the primary source |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
