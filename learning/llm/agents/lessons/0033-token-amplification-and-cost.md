---
title: 33. Token Amplification and Cost per Completed Task
description: Why agentic systems consume far more tokens per completed task than a single prompt would, and how to budget for it
type: lesson
---

# Lesson 33. Token Amplification and Cost per Completed Task

**Mission link:** Budget the token cost and latency of an agentic loop, and say which part of the loop the amplification comes from.
**Primary source:** [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
**Prerequisites:** [Lesson 32](0032-least-privilege-and-the-confused-deputy.md), [Trajectory](../GLOSSARY.md)

## Warm-up

1. ▢ In Lesson 10, you learned that the transcript grows every turn the agent loop runs. Why does this create a cost that compounds over a trajectory?

<details markdown="1"><summary>Check</summary>

The entire transcript is sent to the model on every loop turn. A 30-turn trajectory means the first turn's content is sent to the model 30 times, the second turn's content 29 times, and so on. The token cost of a long trajectory is not just the sum of the turns; it is the sum of all the repeated transmissions of old turns.

</details>

2. ▢ From Lesson 19, recall: when an orchestrator spawns three workers in parallel, how many agent loops run in total compared to a single agent solving the same problem?

<details markdown="1"><summary>Check</summary>

Three separate agent loops run, one inside each worker, plus the orchestrator's own loop. So the total is at least three full agent runs plus the orchestrator cost, whereas a single agent solving the same problem is one run. The token cost is multiplied, not divided, by the parallelism.

</details>

## Know this

### The four sources of token amplification

An agentic system consumes far more tokens per completed task than a well-informed single prompt would. This happens because of four compounding factors. We have already named three of them in earlier lessons; this lesson pulls them together and adds the fourth.

### Source 1: Transcript regrowth (from Lesson 10)

Every loop turn appends to the transcript. On the next turn, the entire transcript is re-sent to the model. This means a 50-turn trajectory pays the token cost of turn 1 fifty times over, the cost of turn 2 forty-nine times, and so on. The total is roughly half the sum: 1 + 2 + 3 + ... + 50 = 1,275, so each turn is paid for an average of 25.5 times. A simple prompt you send once costs X tokens. The same problem solved by a 50-turn agent costs not 50X (if each turn were independent), but something closer to 1,275X in raw token transmission, even if each individual turn is cheaper than X because the model is narrowly focused.

The "Building Effective Agents" article from Anthropic notes that this regrowth is the single largest cost multiplier on long-running agents, and it is why Lesson 11 (compaction and retrieval) exists as a defense against it.

### Source 2: Multi-agent duplication (from Lesson 19)

If you decompose a problem into sub-tasks and run three workers in parallel (fan-out from Lesson 18), you pay the full transcript regrowth cost not once, but three times over. Each worker has its own 50-turn trajectory, so each pays 1,275X. The orchestrator also runs its own loop. The coordination cost multiplies the overall token cost. If your single agent would have cost 50,000 tokens, three workers at slightly lower cost each might total 130,000 tokens or more.

### Source 3: Reflection and retries (from Lesson 17)

If a first attempt at a task fails and the harness generates a reflection, then runs the agent again, you now have two full trajectories instead of one. A task that takes three attempts (one failure, one reflection, one success) costs roughly three times what a successful single attempt would cost, because each attempt is a full agent run with its own transcript regrowth. Lesson 17 teaches that reflection is only worth this cost when the failure signal is clear and a second attempt is likely to succeed.

### Source 4: Tool definitions resent on every turn (new in this lesson)

The system prompt and tool definitions are part of the context sent to the model on every loop turn. Tool definitions are typically large: each tool has a name, a human-readable description (from Lesson 8's naming work), parameter types, constraints, and examples. If you have ten tools with 200 tokens of description each, that is 2,000 tokens of tool definitions. On a 50-turn trajectory, that is 2,000 * 50 = 100,000 tokens spent re-sending the same tool definitions, even though they never changed mid-run.

This cost is distinct from the transcript regrowth (Source 1) because the tool definitions do not change; they are a stable, repeated prefix. This is exactly the problem Lesson 34 (prompt caching) addresses.

### The right unit to budget: cost per completed task

Most cost discussions focus on "cost per API call" or "cost per model invocation." But the right unit for an agentic system is "cost per completed task," which means the full sum of all attempts, all retries, all workers, all turns, until the task is done.

A task that a single prompt might solve in 5,000 tokens can cost 50,000 or more tokens in an agentic system if:

- The problem takes 20 turns to solve (regrowth multiplier: ~200x on top of single-turn cost)
- The first attempt fails and a reflection-based retry succeeds (multiply by 2)
- The task is broken into three parallel workers (multiply by 3)
- Tool definitions are large and resent every turn (add 10,000 tokens of waste)

The math is rough, but the principle is real: 5,000 base tokens can become 50,000 to 150,000 tokens in practice, because you are not paying for one call; you are paying for one task completion, which involves many calls, many turnarounds, and many repeated contexts.

### Why "cost per completed task" changes your design decisions

When you think in terms of cost per API call, a long-running agent looks expensive because of sheer number of calls. When you think in terms of cost per completed task, the question changes: does a multi-agent system solve the problem faster in wall-clock time or more reliably, in a way that justifies the token multiplier? Does reflection reduce the number of failed tasks, in a way that justifies the retry cost? Does decomposition simplify the problem enough that each worker uses fewer tokens per task than the single agent would have?

These are the real trade-off questions. Cost-per-task budgeting makes the trade-off visible.

### Illustrative example: debugging a code failure

Suppose your task is to debug a failing test. A well-informed human might write a prompt: "Here is the test, here is the error output. Find the bug." That prompt and response might cost 10,000 tokens total.

Now suppose you build an agent loop instead:

- The agent reads the test (1,000 tokens), reads the code (2,000 tokens), reasons about the error (500 tokens) = 3,500 tokens on turn 1. Re-sending those 3,500 tokens plus tool definitions (2,000 tokens) on turn 2 = 5,500 tokens. After 10 turns debugging, you have spent roughly 3,500 * 10 + (tool definitions * 10) = 55,000 tokens, because every turn re-sends the test, the code, and the tool definitions.
- The agent's first attempt guesses the wrong root cause. The harness generates a reflection and re-runs the agent. Now you have two full 10-turn runs, so roughly 110,000 tokens, not 55,000.
- The second attempt succeeds.

Cost per completed task: 110,000 tokens. Cost per successful API call: 5,500 tokens (only the last successful call). These numbers tell different stories. Budgeting per completed task is more honest.

The fix is not to avoid agents; the fix is to use Lesson 34's prompt caching to avoid re-sending tool definitions, to design Lesson 16's planning to reduce the number of turns, and to use Lesson 17's reflection only when failure signals are clear.

## Practice

1. ▢ A single-turn prompt to a model costs 5,000 tokens and solves a problem perfectly. An agent loop on the same problem takes 25 turns, and the transcript regrowth cost means each token in the early turns is paid for roughly 20 times on average. Roughly how many tokens does the agent loop cost in total?

<details markdown="1"><summary>Check</summary>

Roughly 5,000 * 20 = 100,000 tokens. The regrowth multiplier is the biggest factor. (This is an illustrative estimate; the exact number depends on how the tokens are distributed across turns, but the order of magnitude is right.)

</details>

2. ▢ You are building an agent that summarizes research papers. Tool definitions for the agent are 3,000 tokens total. On a single run, the agent examines 10 papers and produces 10 summaries, taking 40 turns total. The tool definitions never change during the run. How many tokens are spent re-sending the tool definitions, and why is this waste addressable in Lesson 34?

<details markdown="1"><summary>Hint</summary>

Count how many times the tool definitions are sent to the model. Then think about which part of the context is stable and never changes mid-run.

</details>

<details markdown="1"><summary>Check</summary>

The tool definitions are sent 40 times (once per turn), so 3,000 * 40 = 120,000 tokens spent on re-sending the exact same definitions. This is waste because the definitions never change; they are a stable prefix. Lesson 34 teaches prompt caching, which caches exactly this kind of stable prefix and only charges for it once, not 40 times.

</details>

3. ▢ A task requires three attempts. The first attempt fails, a reflection is generated, the second attempt fails, another reflection is generated, and the third attempt succeeds. Each attempt is a full 15-turn agent run. The orchestrator to coordinate all three attempts costs 5 turns. Roughly how many total turns is the trajectory?

    - a) 15 turns (only the successful attempt counts)
    - b) 35 turns (15 + 15 + 5)
    - c) 50 turns (15 + 15 + 15 + 5)
    - d) 150 turns (all three attempts times the orchestrator overhead)

<details markdown="1"><summary>Check</summary>

**c)** All three attempts run to completion, so 15 + 15 + 15 = 45 turns, plus 5 turns of orchestration = 50 turns. Option a is wrong because failures still consume full turns. Option b misses the second failed attempt. Option d miscounts by multiplying instead of adding. The trajectory includes every turn of every attempt, not just the successful one.

</details>

4. ▢ You are deciding whether to use a single agent or fan-out three workers for a research task. The single agent would take 60 turns and cost roughly 100,000 tokens. Each worker would take 25 turns and cost roughly 35,000 tokens, plus the orchestrator takes 10 turns and costs 3,000 tokens. What is the total token cost of the multi-agent system, and is it cheaper than the single agent?

<details markdown="1"><summary>Check</summary>

Total: (35,000 * 3) + 3,000 = 108,000 tokens. The multi-agent system is actually slightly more expensive in tokens (108,000 vs. 100,000) even though each worker is more efficient. This is the coordination cost from Lesson 19. The multi-agent system wins on wall-clock time (all three workers run in parallel, so the slowest worker determines the time, not the sum), not on tokens. This shows why cost-per-task budgeting is important: if you need speed, multi-agent wins; if you need tokens, single agent wins.

</details>

## Real-world reps

- [ ] Take a task you have done with an agent (or a trajectory you have seen). Walk through one loop iteration of that agent and count the tokens: transcript size, tool definitions size, model output size. Multiply by the number of turns. Now estimate what a single well-informed prompt to the model would have cost, and compare the two numbers. Record the multiplier.
- [ ] Design a small agent task (something you could run yourself). Estimate the cost per completed task by guessing: number of turns needed, number of retries, any fan-out workers. Add up the full budget using the formula (transcript_regrowth_factor) * (number_of_attempts) * (number_of_workers) * (tokens_per_turn).
- [ ] Tomorrow: Find or generate a trajectory from an agent run (at least 10 turns). Calculate the cost-per-task in tokens by summing all token costs across all turns and all attempts. Then find the cost per successful API call (only the final successful turn). Write down how much larger the cost-per-task is than the cost-per-successful-call, and explain why the difference matters for budgeting.

## Going further

- [Article: "How We Built Our Multi-Agent Research System", Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
