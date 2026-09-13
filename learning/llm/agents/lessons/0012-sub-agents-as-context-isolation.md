---
title: 12. Sub-Agents as Context Isolation
description: Spinning up a sub-agent isolates long exploratory work from the parent's context budget
type: lesson
---

# Lesson 12. Sub-Agents as Context Isolation

**Mission link:** Diagnose a failing agent from its trajectory instead of adding another instruction to its prompt.
**Primary source:** [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
**Prerequisites:** [Lesson 11](0011-compaction-and-retrieval-on-demand.md)

## Warm-up

1. ▢ What is the difference between compaction and retrieval on demand?

<details markdown="1"><summary>Check</summary>

Compaction replaces old turns with a summary, saving tokens but risking information loss. Retrieval on demand keeps old detail out of context and fetches it only when the model asks for it, trading a bit of latency for a smaller resident context.

</details>

2. ▢ In compaction plus retrieval on demand, what three things does the always-resident context contain?

<details markdown="1"><summary>Check</summary>

The goal and constraints, a summary of progress, and metadata (file names, available tools, document titles). Full detail is compressed (compaction) or on demand (retrieval).

</details>

## Know this

### Sub-agents as a context-management tool

So far, lessons 10 and 11 focused on managing a single agent's transcript. But there is another approach: spin up a separate agent to do a bounded piece of work. This is stage 8 (multi-agent), but narrowly scoped here to the context-budget angle only.

A sub-agent is a fresh agent run with its own transcript, its own harness, and its own tool set. It explores, makes tool calls, accumulates its own trajectory. The parent agent, meanwhile, has not paid the cost of any of that exploration. None of the sub-agent's turns appear in the parent's transcript.

When the sub-agent finishes, it produces a final result or summary. That summary (just a few sentences or a data structure) is appended to the parent's transcript. The sub-agent's entire internal reasoning, all its dead ends, all its tool calls and failures, stays outside the parent's context.

### The key insight: a large, isolated trajectory costs nothing to the parent

Suppose a sub-agent spends 100 turns reading files, comparing patterns, hitting dead ends, and refining its analysis. Its trajectory is huge. But from the parent's perspective, all of that work is invisible. The parent only sees the final report, a few hundred tokens. Meanwhile, the parent's context stays small and cheap.

This is different from compaction and retrieval on demand, which both operate within a single transcript. A sub-agent operates outside the parent's transcript entirely. Its cost is borne by the sub-agent's harness, not the parent's.

### The trade-off: invisible reasoning means lost details

Because the sub-agent's internal reasoning is invisible to the parent, information the parent did not think to ask for can be lost. If the parent spins up a sub-agent to "read these files and summarize," the sub-agent might discover something interesting but peripheral: "I also noticed a memory leak in util.cpp." If the parent did not ask for that, the sub-agent might omit it from the report, and the parent never learns about it.

This is different from the risk of compaction, where the harness controls what gets summarized. With a sub-agent, the boundary between "what to report back" and "what to leave internal" is the sub-agent's own choice. If the sub-agent is a language model, it will estimate what the parent cares about based on the instructions it received. That estimate can be wrong.

### When a sub-agent is worth it, when it is not

A sub-agent is worth the coordination cost when:

- The sub-task is large and will accumulate a long trajectory (many turns, many tool calls, many dead ends).
- The sub-task is bounded: there is a clear stopping point and the parent will not need the sub-agent's reasoning for downstream work.
- The cost of spinning up a new agent (latency, coordination overhead) is much smaller than the cost of keeping the sub-agent's exploration in the parent's context.

For example: "Research the history of this codebase, read the git log and major PRs, and give me a three-sentence summary." That is a large, bounded task. A sub-agent exploring for 50 turns saves the parent 50 turns of context cost.

A sub-agent is not worth it when:

- The task is small (will only take a few turns anyway).
- The task requires tight coordination with the parent (the parent will ask clarifying questions, the sub-agent will need to refine its work).
- The parent will need the sub-agent's full reasoning later (to understand why a conclusion was reached, to spot an assumption, to debug a mistake).

For example: "Fetch the temperature for tomorrow." That is a few-turn task; spinning up a sub-agent costs more than just doing it in the parent.

## Practice

1. ▢ An agent is tasked with reviewing code across 50 files and producing a report. The developer has split the work: the main agent reviews 5 files, and spins up a sub-agent to review the other 45. Why is this a good use of a sub-agent?

    - a) Sub-agents are always faster than single agents
    - b) The sub-agent's long trajectory (reviewing 45 files) is isolated from the main agent's context, keeping the main context small and cheap
    - c) Sub-agents never make mistakes
    - d) The main agent can immediately see all of the sub-agent's reasoning

<details markdown="1"><summary>Check</summary>

**b)** A sub-agent lets the main agent offload a large, bounded task. The sub-agent's 100+ turns of exploration do not bloat the main agent's context. The main agent only receives the sub-agent's final report. Option a is wrong because sub-agents may add latency. Option c is wrong because sub-agents can make mistakes. Option d is wrong because the sub-agent's internal reasoning is invisible to the main agent.

</details>

2. ▢ A sub-agent is reviewing a codebase and discovers a security vulnerability. It is not directly related to the task the parent asked for (code style review), but it is critical. What risk does the sub-agent's invisibility create here?

<details markdown="1"><summary>Hint</summary>

The sub-agent's instructions told it to focus on code style. Who decides what gets reported back to the parent, and what might be lost?

</details>

<details markdown="1"><summary>Check</summary>

The sub-agent decides what to include in its final report based on its instructions. If the instructions emphasize code style, the sub-agent might not report the security issue at all, or mention it as a footnote the parent misses. Information the parent did not think to ask for can be lost because the parent never sees the sub-agent's full reasoning. The parent has to be very explicit: "Report anything critical you find, style or not."

</details>

3. ▢ Compare two approaches to a long research task:
    - Approach A: Single agent that compacts old turns and uses retrieval on demand. Takes 80 turns, resident context stays under 30,000 tokens.
    - Approach B: Main agent spins up 3 sub-agents to explore in parallel. Each takes 40 turns internally. Main agent receives a summary from each. Main agent's final context is 5,000 tokens plus coordination overhead.

Which approach has the lower total token cost (counting all agent runs), and why?

    - a) Approach A, because it avoids sub-agent overhead
    - b) Approach B, because the three explorations are isolated and cheap to the main agent
    - c) They are the same cost
    - d) Depends on how much coordination overhead there is

<details markdown="1"><summary>Check</summary>

**d)** Approach A sends 30,000 tokens to the model 80 times, roughly 2.4M tokens. Approach B sends roughly 50,000 tokens to the model 40 times across each sub-agent, plus coordination with the main agent. If coordination is minimal and the sub-agents' work is truly parallel and bounded, Approach B can be cheaper. But if coordination is expensive or the sub-agents need to refine their results iteratively, Approach A may be better. The answer depends on the actual cost of spinning up and coordinating the sub-agents.

</details>

4. ▢ You are designing an agent to "debug this failing test suite and propose a fix." Should you use a sub-agent, and why or why not?

<details markdown="1"><summary>Check</summary>

No. Debugging is a task where the parent will likely need the sub-agent's full reasoning to judge whether the proposed fix is safe, to spot assumptions, or to ask clarifying questions. It is not a bounded task with a simple report; it requires tight coordination. The sub-agent's invisible reasoning would be a liability. Better to keep debugging in the parent's main loop where the parent can follow the full trajectory.

</details>

## Real-world reps

- [ ] Describe a task where you would use a sub-agent and explain why a large, isolated trajectory is worth the coordination cost.
- [ ] Describe a task where you would not use a sub-agent, and explain what information would be lost if you did.
- [ ] Tomorrow: Sketch the parent and sub-agent responsibilities for a multi-part task (e.g., "research this library, then integrate it into our codebase"). Where does the boundary go, and what does each agent report to the other?

## Going further

- [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
