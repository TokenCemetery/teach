---
title: 19. Coordination Cost
description: Understand why building multiple agents is more expensive than one well-equipped agent, and how to decide when the parallelism win is worth the cost
type: lesson
---

# Lesson 19. Coordination Cost

**Mission link:** To choose between a single well-equipped agent and a multi-agent system, you need to know what orchestrator-worker systems cost in tokens, reasoning, and fragmented context, and how to judge whether a second agent buys anything the first agent could not have been given directly.
**Primary source:** [Article: "Don't Build Multi-Agents", Cognition](https://cognition.ai/blog/dont-build-multi-agents)
**Prerequisites:** [Lesson 18](0018-orchestrator-and-worker.md)

## Warm-up

1. ▢ From Lesson 18, recall: in an orchestrator-worker system, can a worker see the full reasoning trajectory of another worker while the other worker is running?

<details markdown="1"><summary>Check</summary>

No. Each worker runs its own agent loop with its own isolated transcript. Workers only see each other's findings if the orchestrator explicitly passes them, and only the final reports, not the full reasoning. This isolation is a feature (it keeps context clean) and a cost (workers cannot share mid-task insights).

</details>

2. ▢ From Lesson 18, recall: what is the difference between fan-out and handoff?

<details markdown="1"><summary>Check</summary>

Fan-out spawns multiple workers on variations of the same problem in parallel, exploring different angles at once for broader coverage and parallelism. Handoff is sequential: one agent finishes its task and passes a clean context to a second agent specialized for the next phase. Both are multi-agent patterns; fan-out uses time, handoff uses specialization.

</details>

## Know this

### Token cost: many agents cost many times more

Every agent run has a cost. An orchestrator-worker system pays that cost multiple times over.

Suppose a single agent solves a problem in 10,000 tokens: say, 20 turns with 500 tokens per turn. Now suppose the same problem is split into three independent sub-tasks, each solved by a worker in 8,000 tokens (slightly less, because each worker has a narrower focus). The orchestrator itself uses 2,000 tokens to break down the task and synthesize results.

Total cost: 8,000 + 8,000 + 8,000 + 2,000 = 26,000 tokens. The multi-agent system cost 2.6x what the single agent cost, even though each worker was slightly more efficient than the single agent would have been on their portion alone. The workers explore in parallel, so wall-clock time is faster, but token cost is multiplied.

This math gets worse if the workers run inefficiently or if the orchestrator has to coordinate more than once (e.g., orchestrator realizes workers missed a dependency, spawns new workers, or asks workers to run again with new instructions). The Cognition article flags this as the core question: is the parallelism speed-up worth paying several times the token cost?

### Fragmented context: workers cannot see each other

When a single agent runs a long task, it builds up context: it knows what it has tried, what worked, what did not, and why. A multi-agent system fragments this context. Workers A and B might research overlapping ground (e.g., both trying to understand a constraint), but Worker A does not see Worker B's reasoning about that constraint; it only sees the final report.

Concretely: Worker A realizes mid-task that a constraint has a subtle implication. Worker A reasons through it, builds intuition, and reports back. The orchestrator reads the report and passes it to Worker B. Worker B now knows the conclusion but not the reasoning that led to it. Worker B cannot refine or challenge that reasoning mid-task, because it does not see Worker A's thinking. Worker B either accepts the report and uses it (losing the chance to refine it) or ignores it and re-derives the same insight (wasting tokens).

For tasks where the best answer emerges from back-and-forth refinement between multiple lines of reasoning, fragmented context is a real limitation. A single agent with enough turns can hold all its reasoning in one place and integrate insights as they develop.

### Conflicting conclusions: independent exploration leads to disagreement

When two workers explore the same ground independently, they can reach different conclusions. This is not necessarily wrong; they might have found genuinely different (and both valid) interpretations. But it also might mean one worker made an error, or missed something the other caught.

The orchestrator sees both reports and has to reconcile them. If the conflict is semantic or factual, the orchestrator has a problem: it has only the workers' summaries, not their full reasoning, so it cannot easily trace where the disagreement came from. The orchestrator might run a new agent (a "judge" or "synthesizer" sub-agent) to reconcile, which adds more cost.

The single-agent alternative avoids this: a single agent working through the same ground serially integrates each new finding into its running mental model, so it can spot contradictions as they arise and resolve them within its own reasoning loop.

### The decision principle: when is multi-agent cheaper?

The primary source from Cognition argues that most multi-agent systems are not cheaper, in tokens or reasoning quality, than a single agent with better tools. The question is not "is parallelism faster?" (yes) but "does parallelism buy something a single agent could not have had for less cost?"

Apply this decision principle:

**Multi-agent makes sense when:**
- The sub-tasks are truly independent (no shared context, no dependency on each other's results mid-task).
- The sub-tasks are each simpler than the original task (each worker solves a genuinely narrower problem, so the sum of workers' efficiency gain outweighs the duplication cost).
- You need the parallelism speed-up (the time savings justify the token multiplier; you have a wall-clock deadline you cannot meet with one agent and more turns).
- The tools for each worker are specialized enough that a shared tool suite would slow each worker down with irrelevant options.

**Single agent with more resources usually wins when:**
- The sub-tasks share context or refine each other (a single agent keeps all its reasoning connected; a multi-agent system has to re-derive or re-communicate).
- You have room in the context budget (give the single agent a bigger context window, better retrieval, more tools, more turns).
- The sub-tasks are interdependent or require back-and-forth refinement between multiple lines of thinking.
- The coordination overhead (orchestrator time, communication, reconciliation of conflicting conclusions) is high relative to the problem.

Said plainly: a single agent with better tools, a longer context, and more turns often solves the same problem cheaper and with better reasoning quality than multiple agents with fragmented context. The speedup from parallelism is real but not free.

## Practice

1. ▢ You are building a question-answering system. Option A: one agent with search, code execution, and documentation tools. Option B: an orchestrator that spawns three workers in parallel, each with one specialized tool (search worker, code worker, docs worker). Both aim to answer complex user questions. Under what circumstances does Option B's token cost become cheaper than Option A's?

<details markdown="1"><summary>Check</summary>

This is a trap. In most circumstances, Option B costs more in tokens because you are paying the full agent cost three times, plus orchestrator overhead. Option B's token cost becomes cheaper than Option A only if the specialization gain is enormous, or if the three workers can each finish so quickly (fewer turns) that 3x cheap beats 1x expensive. More likely: Option A (one agent with multiple tools) is more expensive in tokens than either option, because the single agent has to deliberate about which tool to use. Option B could beat Option C (a slower agent) but rarely beats a single agent of equal quality and tool access. The trade-off is wall-clock time (Option B is faster due to parallelism) vs. tokens (Option A is cheaper). You choose Option B for speed, not cost.

</details>

2. ▢ In the orchestrator-worker system from Lesson 18 (parallel research workers), suppose two workers end up researching the same source and reach different conclusions about what it says. The orchestrator has both reports. What is the orchestrator missing that a single agent would have had?

<details markdown="1"><summary>Hint</summary>

Think about what is in each worker's transcript vs. what is in a single agent's transcript at the moment of reasoning about that source.

</details>

<details markdown="1"><summary>Check</summary>

The orchestrator sees two conclusions but not the reasoning that led to each. A single agent, having read the same source, would have all its reasoning about that source in one transcript: how it interpreted the text, what nuance it noticed, what it considered and rejected. The single agent's reasoning is fully traceable. The orchestrator can only ask "why did you reach that conclusion?" and a worker would have to re-explain, or the orchestrator would have to spawn a new agent to trace the disagreement. This is fragmented context.

</details>

3. ▢ You are deciding whether to use fan-out (orchestrator-worker) or a single agent for a task. The task is: given a dataset and a question, clean the data, explore it, build a model, and report findings. Will the phases (cleaning, exploring, modeling, reporting) run in parallel under fan-out, or sequentially?

    - a) Parallel, because fan-out spawns all workers at once.
    - b) Sequentially, because exploring depends on cleaning, modeling depends on exploring.
    - c) Parallel, but the work can be split so each worker does all phases independently.
    - d) It depends on whether the workers have access to the same dataset.

<details markdown="1"><summary>Check</summary>

**b)** This task is not a good fit for fan-out because the phases are sequential: you cannot explore dirty data well, you cannot model without understanding the data, etc. Each phase depends on the previous one. Fan-out shines on tasks with independent sub-tasks (research angle A, research angle B, research angle C in parallel). For sequential work, handoff (Lesson 18) is a better fit than fan-out, or a single agent with enough turns is simpler. (a) is wrong: parallelism does not create magic; dependencies still exist. (c) is possible but defeats the purpose of specialization; each worker would need all tools and knowledge. (d) is a red herring; data access is not the limiting factor here.

</details>

4. ▢ The Cognition article argues that a single agent with better retrieval or more capable tools often solves problems cheaper in tokens than an orchestrator-worker system. What is the core reason for this claim?

<details markdown="1"><summary>Check</summary>

A single agent holds all its reasoning in one transcript, so it integrates findings, spots contradictions, and refines conclusions within one reasoning loop. An orchestrator-worker system pays the token cost of many agent loops, and fragments context between them, so workers re-derive or re-communicate insights. The single agent's efficiency gain from keeping context unified and reasoning connected often outweighs the multi-agent system's parallelism speed-up, especially when the question has dependencies or benefits from integrated reasoning. Giving one agent more tools or better retrieval (both cheaper than running multiple agents) often wins.

</details>

5. ▢ You are building a system to debug a failing program. You consider fan-out: spawn three workers, each trying a different debugging strategy in parallel, then have the orchestrator pick the best insight. What is a cost this design does not capture that Lesson 19 teaches?

<details markdown="1"><summary>Check</summary>

Token cost multiplied by three (each worker is a full agent run), fragmented context (no worker sees the other workers' explorations, so they might re-derive the same dead end three times instead of learning from each other), and the orchestrator has to reconcile potentially conflicting conclusions about what the bug is. A single agent trying all three strategies serially would build a unified model of the bug as it goes. The three workers cannot do that without the orchestrator running a reconciliation step (another agent, more cost). Fan-out buys speed (three workers finish in the time of the slowest worker, not the sum of all three), but the costs are high for a task like debugging where insight builds on insight.

</details>

## Real-world reps

- [ ] Take a problem you have solved before (debugging, analysis, planning, research, whatever). Mentally run through it as a single agent with many turns vs. as three fan-out workers. Where would parallelism win you wall-clock time? Where would fragmented context cost you and force re-derivation or reconciliation work?
- [ ] Read the Cognition article "Don't Build Multi-Agents" at least once. Look for the section where the author argues single agent plus better tools beats orchestrator-worker. Write down one concrete example they give and what made the single agent cheaper.
- [ ] Tomorrow: sketch a task you might build into an agent system. For that task, estimate: how many tokens would a single agent use? How many would a fan-out system cost (guess three workers, each running at slightly less token cost than the single agent's per-task slice)? Is the speed-up worth the token multiplier to you?

## Going further

- [Article: "Don't Build Multi-Agents", Cognition](https://cognition.ai/blog/dont-build-multi-agents)
- [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
