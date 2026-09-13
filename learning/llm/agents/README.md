---
title: LLM Agents
description: "Build the loop yourself: tools, context, memory, and knowing when an agent is the wrong answer"
type: topic
---

# LLM Agents

Be able to build an agent loop yourself, decide whether a given task needs an agent at all rather than a fixed workflow, and diagnose a failing agent from its trajectory instead of adding another instruction to its prompt.

**Latest lesson:** _none yet_

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

| Stage | Covers | Done when |
| --- | --- | --- |
| 1. What an agent is | The loop, agent against workflow against chain, the autonomy spectrum | Can classify a system and say whether "agent" is the right word for it |
| 2. Tool calling mechanics | The wire format of a tool call, parameter schemas, who executes what, parallel calls, errors returned as results | Can read a raw tool-call exchange and say what each message did |
| 3. The loop from scratch | Writing the loop, stopping conditions, the transcript as the agent's whole state | Can write an agent loop and defend where it stops |
| 4. Tool design as prompt engineering | Names and descriptions as prompt surface, return shapes, result token cost, tool-set bloat | Can design a tool surface and say why each description is worded as it is |
| 5. Context management | The window as the central budget: truncation, compaction, retrieval on demand, sub-agents as context isolation | Can plan what leaves the context, and when, for a long-running task |
| 6. Memory and state | Within-run scratchpad against across-run memory, files as memory, why retrieval is not memory | Can choose where a given fact lives and say what happens when the run ends |
| 7. Planning and reflection | ReAct, plan-then-execute, self-critique, decomposition, what reasoning models changed | Can pick a planning pattern for a task and name what it costs in tokens and latency |
| 8. Multi-agent | Orchestrator and worker, handoff, fan-out, coordination cost, when one agent with better tools wins | Can say whether a second agent buys anything the first could not have been given |
| 9. Protocols and interop | MCP's tools, resources, prompts and transports, provider function-calling formats, tool discovery at scale | Can read an MCP server's manifest and say what it exposes and what it does not standardise |
| 10. Execution environments | Sandboxing, code execution as a tool, filesystem access, human-in-the-loop approval gates | Can place the sandbox boundary for a stated set of tools |
| 11. Computer use and browser agents | Screenshots as observations, grounding an action to a coordinate, the reliability problem | Can say why a screen-driving agent fails differently from a tool-calling one |
| 12. Failure modes and observability | Loops, context poisoning, cascading tool errors, hallucinated arguments, tracing and trajectory replay | Given a trajectory, can name the at-fault step rather than re-prompting |
| 13. Evaluating an agent | Outcome against trajectory, repeated-trial reliability, what the agent benchmarks actually measure | Can say what to measure for a given agent, and hand the rest to `llm/evals` |
| 14. Security | Prompt injection as the defining agent problem, the lethal trifecta, least privilege, the confused deputy, MCP supply chain | Can design a permission boundary that holds when the agent reads hostile content |
| 15. Production, cost, and what frameworks buy | Token amplification, prompt caching, concurrency, durability and resumability, cost per completed task | Can budget a loop's cost and say which framework guarantee a deployment actually needs |
| 16. Judgment | When not to build an agent, reviewing someone else's agent design and naming what a choice costs, settling a disputed claim from the primary source | Trusted to make the call and to explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| _none yet_ | | |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
