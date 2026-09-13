---
title: Glossary
description: "Canonical terms for LLM agents"
type: glossary
---

# LLM Agents Glossary

Canonical terms for building agents: what the loop is made of, and what to call each part in a field that routinely uses four words for one thing.

## Terms

**Across-run memory**:
Facts stored outside any single trajectory and deliberately loaded back into a new run's initial context, since a fresh run starts with an empty transcript.
_Avoid_: scratchpad (the two are separate mechanisms and confusing them is the most common mistake here), state (too generic)

**Agent**:
A system that runs a language model in a loop with tools, letting the model decide which tool to call, when, and when to stop, rather than following a path the developer fixed in advance.
_Avoid_: assistant, bot, copilot (product words that say nothing about whether the control flow is fixed or model-decided)

**Agent loop**:
The cycle a running agent repeats: send the transcript to the model, execute whatever tool call comes back, append the result to the transcript, repeat until a stopping condition fires.
_Avoid_: chain, pipeline (both name a fixed sequence, which is exactly what an agent loop is not)

**Approval gate**:
A harness-level checkpoint that pauses the loop before executing a call in a risky category until a human approves or rejects it.
_Avoid_: human-in-the-loop (too broad; approval gate names this specific mechanism)

**Autonomy spectrum**:
The range from a single prompt, through a developer-fixed workflow, to a model-directed agent, ordered by how much of the control flow the model gets to choose at run time rather than a developer choosing it in advance.
_Avoid_: "how agentic" something is (treats autonomy as a single fuzzy quantity rather than a control-flow question with a checkable answer)

**Client tool**:
A tool whose implementation runs in the harness's own code, so the harness executes it directly when the model requests it.
_Avoid_: local tool, custom tool

**Compaction**:
Replacing a stretch of old transcript with a condensed summary the model can still act on, trading some information loss for a smaller resident context.
_Avoid_: summarization (too generic; compaction specifically targets an agent's own transcript, not arbitrary text)

**Confused deputy**:
A component with legitimate authority that gets tricked, via untrusted content, into misusing that authority on an attacker's behalf, rather than being compromised itself.
_Avoid_: "the model was hacked" (nothing was compromised; the tool did exactly what it was built to allow)

**Context poisoning**:
An unsupported or false claim entering the transcript and then being silently treated as established fact by every later turn.
_Avoid_: hallucination (too broad; this names specifically a claim that has entered and persists in the transcript, not any single wrong output)

**Context rot**:
The model's attention and accuracy degrading as low-relevance content accumulates in the context, even when no needed information has been truncated.
_Avoid_: "the context is full" (conflates a hard token limit with a softer accuracy problem that starts well before the limit)

**Cost per completed task**:
The token cost of every attempt, retry, and worker a task actually needed to succeed, not just the cost of the final successful call.
_Avoid_: cost per API call (undercounts a task that needed more than one attempt to succeed)

**Fan-out**:
An orchestrator spawning multiple workers on variations of the same problem at once, trading token cost for parallel wall-clock time.
_Avoid_: parallelism (too generic; fan-out is the specific multi-agent shape that produces it here)

**Grounding**:
Translating the model's intent into an actual screen coordinate or on-screen target, a step that can fail on its own even when the model's underlying decision was correct.
_Avoid_: click accuracy (too narrow; grounding covers any observation-to-action mapping, not just clicking)

**Handoff**:
One agent finishing its portion of a task and passing a clean, bounded context, not its full trajectory, to a second specialized agent for the next phase.
_Avoid_: fan-out (handoff is sequential, fan-out is parallel, see this lesson's contrast)

**Harness**:
The code around the model that holds the transcript, executes tool calls, enforces limits, and decides when the loop ends. The model chooses; the harness acts.
_Avoid_: runtime, framework (a framework is one possible harness, not the concept)

**Least privilege**:
Scoping each tool to only the access it actually needs, rather than broad access granted "just in case."
_Avoid_: sandboxing (a sandbox enforces a boundary; least privilege is the design principle that decides how narrow that boundary should be)

**Lethal trifecta**:
The combination of access to private data, exposure to untrusted content, and the ability to communicate externally that together make an agent exploitable. Removing any one of the three breaks the attack.
_Avoid_: "security risk" (too vague to act on; the trifecta names the three specific conditions to check)

**Orchestrator**:
The agent in a multi-agent system that decomposes a task, assigns sub-tasks to workers, and synthesizes their reports; it does not do the sub-task work itself.
_Avoid_: manager, coordinator (generic terms that do not distinguish this role from a worker)

**Prompt injection**:
Content an agent reads that contains instructions designed to hijack its behavior, exploiting the fact that the model cannot structurally distinguish data from instructions.
_Avoid_: jailbreak (a jailbreak targets the model's own refusal training directly; injection hides instructions inside content the agent was asked to process)

**ReAct**:
The pattern of interleaving a short reasoning step with each action, so each step's reasoning can react to the actual result of the step before it.
_Avoid_: chain-of-thought (that names reasoning text alone; ReAct specifically interleaves it with tool actions and their observed results)

**Reflection**:
An explicit stage where the agent evaluates a failed attempt in natural language and carries that evaluation into the next attempt, as distinct from a plain retry with the same context.
_Avoid_: self-correction (used loosely for whatever a model does internally; reflection names the external, stored, carried-forward version)

**Retrieval on demand**:
Keeping only a summary or reference resident in context and fetching the full detail back in with a tool call only when the model actually needs it.
_Avoid_: RAG (RAG retrieves from an external corpus; this retrieves detail the agent already produced or has direct access to)

**Sandbox**:
The execution boundary the harness enforces around what a tool's code can reach (filesystem, network, resources), regardless of what the model asked for.
_Avoid_: permission (a permission is what you grant; a sandbox is the mechanism that enforces the grant even against a malformed or adversarial call)

**Scratchpad**:
Notes an agent writes to and reads back within a single run. It is really just part of the transcript, and it is gone once the run ends.
_Avoid_: memory (a scratchpad does not survive past the run it was written in)

**Server tool**:
A tool a provider executes on its own infrastructure on the harness's behalf, such as a hosted web search or sandboxed code execution. The harness never runs its implementation, only reads the result from the provider's response.
_Avoid_: hosted tool, built-in tool

**Sub-agent**:
A separate agent run, with its own transcript and harness, spun up to do a bounded piece of work whose only effect on the parent's context is the summary it reports back.
_Avoid_: worker outside an orchestrator-worker system (worker names a sub-agent given a bounded task by an orchestrator; the mechanism is the same, the term picks out the role)

**Token amplification**:
How much more a task costs in tokens as an agentic loop than as a single prompt, from transcript regrowth, multi-agent duplication, and retries compounding together.
_Avoid_: "agents are expensive" (too vague; amplification names the specific multiplier and where each piece of it comes from)

**Tool**:
A capability offered to the model as a name, a description and a parameter schema, which the model can ask for and the harness executes on its behalf.
_Avoid_: function call (that names the message the model emits, not the capability), plugin, skill

**Trace**:
A structured, timestamped record of an agent run made of spans, using vendor-neutral conventions so one tool's trace is readable in another.
_Avoid_: log (an unstructured log is what a trace replaces; a trace has a defined schema a tool can query)

**Trajectory**:
The full ordered record of one agent run: every model turn, tool call, tool result and stopping decision. It is what gets read when diagnosing a failure, rather than the final answer alone.
_Avoid_: transcript (the message list the model actually sees, which omits the harness's own decisions), history, log

**Worker**:
A sub-agent given a bounded sub-task by an orchestrator, running its own loop and transcript in isolation from other workers.
_Avoid_: sub-agent for the orchestration role (sub-agent names the mechanism; worker names this specific role inside it)

**Workflow**:
A system where a developer fixed the sequence of model calls and tool calls in advance. It may contain branches and loops, but the model does not choose the path.
_Avoid_: agent (the distinction between the two is the point of stage 1), chain
