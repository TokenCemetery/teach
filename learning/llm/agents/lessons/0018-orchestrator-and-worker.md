---
title: 18. Orchestrator and Worker
description: Design a multi-agent system where one agent plans and delegates, workers execute in parallel
type: lesson
---

# Lesson 18. Orchestrator and Worker

**Mission link:** To choose between a single well-equipped agent and a multi-agent system, you need to understand what multi-agent systems can do that single agents cannot, starting with the orchestrator-worker pattern that powers most multi-agent research and planning systems.
**Primary source:** [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
**Prerequisites:** [Lesson 17](0017-self-critique-and-reasoning-models.md), [Sub-agent](../GLOSSARY.md)

## Warm-up

1. ▢ From Lesson 17, recall: what does an explicit reflection loop do after a failed attempt, and why does a model with extended internal reasoning need that external loop less than a standard model does?

<details markdown="1"><summary>Check</summary>

An explicit reflection loop generates a natural-language critique of why the attempt failed and carries that critique into the next attempt, as a step separate from the model's own turn. A model that does extended internal reasoning before answering can catch some of the same mistakes inside a single turn, so the external loop earns its cost less often, though it still helps when the failure signal (a tool error, a test result) only exists after the model has already acted.

</details>

2. ▢ From Lesson 12, recall: what is a sub-agent, and what problem does its separate transcript solve?

<details markdown="1"><summary>Check</summary>

A sub-agent is a separate agent run with its own harness and transcript. It solves context isolation: you can spin up a focused sub-agent on a bounded task without that task's transcript bloating the parent agent's context, keeping the parent's reasoning clear for synthesis and coordination.

</details>

## Know this

### The orchestrator-worker pattern

When a task is too broad for one agent's context or needs parallel exploration, the orchestrator-worker pattern splits the work: one agent (the orchestrator) breaks the task into bounded sub-tasks, decides which worker gets which sub-task, then synthesizes their results into a final answer. Each worker is a sub-agent with its own transcript and tools, running independently (and often in parallel).

Think of it like a team lead who doesn't do the work directly but coordinates: the lead breaks down a project, assigns pieces to team members, and pulls together their deliverables. The workers never see each other's full reasoning; the orchestrator only sees their final reports.

### What workers do

Workers are not interchangeable. Each worker typically has:
- A bounded, specific mission (e.g., "research this one angle", "evaluate this candidate approach")
- Tools tailored to that mission (e.g., retrieval for a research worker, code execution for an evaluation worker)
- Its own agent loop and transcript, insulated from other workers

Because workers run their own loops, they can explore independently. A worker does not need to know what other workers are doing; it only knows its own task. This independence is what makes parallelism possible: many workers can run at once, wall-clock time is bounded by the slowest worker, not the sum of all workers' times.

### Fan-out: parallel exploration

Fan-out is a sub-case of orchestrator-worker where the orchestrator spawns multiple workers on variations of the same question. For example:
- One worker researches angle A, another researches angle B, a third researches angle C, all in parallel, to get broader coverage faster than one agent working through them serially.
- Three workers each try to solve the same coding problem with different strategies, and the orchestrator picks the best solution or combines insights.

The speed-up is real: instead of a single agent spending 10 turns on problem-A then 10 turns on problem-B then 10 turns on problem-C (30 turns total), three workers tackle A, B, and C in parallel (10 turns of latency instead of 30). The catch (explored in Lesson 19) is that you pay the token cost for all three workers' full runs, not just one agent's run.

### Handoff: sequential specialization

Handoff is a different multi-agent pattern, also using sub-agents but with sequential phases instead of parallel workers. In handoff:
1. Agent A finishes its portion of the task.
2. Agent A hands off to Agent B by giving it a clean, bounded context: typically just the task definition and Agent A's final findings, not Agent A's full trajectory.
3. Agent B picks up from there, using its own specialized tools and reasoning.

Handoff is useful when a task naturally splits into sequential phases handled by different specialists. For example: an orchestrator finds that a problem needs both deep research and implementation, so it hands off the findings to a specialized coder; or a planner finishes a plan and hands it to an executor with just the plan, not the messy reasoning about why that plan was chosen.

Handoff and fan-out are opposite in rhythm: fan-out is many-parallel, handoff is one-after-another. Both are multi-agent; both isolate context using sub-agents; both are taught in this lesson because they both answer the question "when is one agent not enough?"

### Why orchestrator-worker systems deliver value in practice

The primary source details a concrete multi-agent research system built at Anthropic: breaking down a complex research task into many independent sub-research tasks, spawning a worker for each, retrieving and analyzing sources in parallel, then synthesizing findings into a cohesive answer. The key wins were:

- Parallelism in wall-clock time: complex research that a single agent would spend 50+ turns on could happen faster with 5 workers, each on 15 turns, running concurrently.
- Specialized tools per worker: a retrieval worker can focus on search and ranking without context bloat from code execution; a synthesis worker has a different goal and different tools.
- Independent reasoning: each worker reasons about its own slice of the problem; workers do not get distracted by information intended for other workers.

This pattern emerged as a practical solution to a real constraint: a model's ability to do good reasoning on a complex task is bounded partly by context length and partly by the need to keep reasoning focused. Splitting the work lets you add more reasoning power (more workers, each with its own context budget) without a single agent running out of focus or context.

## Practice

1. ▢ You are building a system to answer user questions about a large codebase. You consider two designs: (A) a single agent with access to code search tools and documentation tools, or (B) an orchestrator that delegates to a search worker and a documentation worker in parallel. Which design more naturally fits the orchestrator-worker pattern, and why?

<details markdown="1"><summary>Check</summary>

Design (B) fits the pattern. The search worker and documentation worker have independent tasks: one searches code, the other searches docs. They can run in parallel without needing each other's results mid-task. The orchestrator's job is clear: formulate queries for each worker, then combine their findings.

Design (A) could work too, but the single agent would have to decide mid-task which tool to use next; there is no parallelism gain. You would choose (B) when you expect the search and documentation queries to be independent and benefit from parallel exploration; you would choose (A) if the queries depend on each other (search results inform which documentation to fetch) or if the overhead of spawning two sub-agents outweighs the speed gain (a simpler task).

</details>

2. ▢ In an orchestrator-worker system, why cannot a worker directly see the reasoning of another worker mid-task?

<details markdown="1"><summary>Hint</summary>

Think about the structure: each worker has its own transcript and harness. What does that isolation prevent?

</details>

<details markdown="1"><summary>Check</summary>

Each worker runs its own agent loop with its own transcript. Worker A's reasoning is recorded in Worker A's transcript, and Worker B's reasoning is in Worker B's transcript. The harness does not merge them. Workers do not have access to each other's transcripts during their runs; they can only read the final reports the orchestrator gives them (if the orchestrator passes them). This isolation keeps each worker's context focused and is the reason sub-agents solve context problems. The trade-off is fragmentation: a decision that needs both workers' full reasoning cannot be made by either worker alone (covered in Lesson 19).

</details>

3. ▢ You are designing a research system. Scenario: one worker is researching the history of a technology, and a second worker is researching current applications of that technology. Can these workers' tasks run in parallel?

    - a) No, because the applications worker needs to know the history first.
    - b) Yes, both workers can research independently; the orchestrator can synthesize findings about history and applications regardless of order.
    - c) No, because they are researching the same technology.
    - d) Yes, only if the history worker finishes before the applications worker starts.

<details markdown="1"><summary>Check</summary>

**b)** Both tasks are independent: a worker researching history does not need the other worker's findings to do good research on history, and vice versa. The orchestrator will have both results when both workers finish and can synthesize them into a complete answer. (a) is wrong: dependencies would run one-after-another (handoff), not fan-out; here there is no dependency. (c) is wrong: researching the same technology is not a blocker to parallelism; in fact, that is why fan-out is useful, to get multiple angles on the same topic. (d) is wrong: parallelism means they run at the same time, not one-after-another.

</details>

4. ▢ A handoff differs from fan-out in what way?

<details markdown="1"><summary>Check</summary>

Fan-out is parallel: the orchestrator spawns multiple workers on variations of the same problem at once. Handoff is sequential: one agent finishes, then passes off its findings to a second agent tailored to the next phase. Fan-out asks "how can we explore more angles in parallel?"; handoff asks "how can we split a sequential process into specialized phases?" Both use sub-agents; both isolate context; both answer "when is one agent not enough?" but in different rhythms.

</details>

## Real-world reps

- [ ] Next time you see a complex task (research, planning, debugging), sketch whether it fits orchestrator-worker (are there independent sub-tasks that can run in parallel?), handoff (are there sequential phases for different specialists?), or a single agent with more tools (can one agent do it with better tools and more turns?). Do not build anything; just practice the shape-recognition.
- [ ] Read the primary source article: "How We Built Our Multi-Agent Research System". Focus on the section describing what the orchestrator did, what each worker did, and what would have changed if they had used a single agent instead. Take notes on one concrete win from parallelism they reported.
- [ ] Tomorrow: describe a real task from your own work or study that would benefit from fan-out (multiple workers exploring the same problem in parallel). What angle would each worker take? What tools would each need?

## Going further

- [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
