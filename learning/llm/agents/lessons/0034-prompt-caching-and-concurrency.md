---
title: 34. Prompt Caching and Concurrency
description: How caching reduces per-task token cost and how concurrency increases throughput, and why conflating them is a budgeting mistake
type: lesson
---

# Lesson 34. Prompt Caching and Concurrency

**Mission link:** Budget the token cost and latency of an agentic loop, and say which part of the loop the amplification comes from.
**Primary source:** [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
**Prerequisites:** [Lesson 33](0033-token-amplification-and-cost.md)

## Warm-up

1. ▢ From Lesson 33, you learned that tool definitions are resent to the model on every loop turn, consuming tokens even though they never change. What part of the context is this, and why would caching help?

<details markdown="1"><summary>Check</summary>

The tool definitions are a stable prefix of every message to the model: they do not change mid-run. Caching helps because a cache stores that stable prefix after the first request and reuses it on later requests in the same trajectory, charging only for new content appended to it.

</details>

2. ▢ From Lesson 19, recall: does running three agents in parallel reduce the token cost of solving a problem compared to running one agent serially?

<details markdown="1"><summary>Check</summary>

No. Running three agents in parallel increases the total token cost because each agent pays its full cost independently. Parallelism reduces wall-clock time but not token cost. Each parallel agent still has to read the task, run its loop, and transmit its transcript to the model.

</details>

## Know this

### How prompt caching works

Prompt caching is a mechanism that stores a stable prefix of a request after the first call and reuses it on subsequent calls without charging full price for it again. The cache is specific to one request sequence; requests from different users or different agent runs do not share a cache.

Here is the mechanics:

1. On the first message in a trajectory, you send a full request: system prompt, tool definitions, and the task.
2. The model processes it normally and charges the full token cost.
3. The response includes metadata: "Cached 4,000 tokens" (or whatever the stable prefix was).
4. On the second message in the same trajectory, you append new content to the request: perhaps a tool result, the next instruction, or a follow-up turn.
5. The model reuses the cached prefix (system prompt, tools, task) and only charges for the newly appended content.
6. This repeats: each new turn in the same trajectory only pays for what changed since the last turn.

The cache has a cost: the first turn pays full price, and there is a small overhead charge for cache lookups and storage. But on a long trajectory, this overhead is easily justified. If you have 30 turns and the tool definitions are 2,000 tokens, the cache saves roughly 2,000 * 28 = 56,000 tokens (the definitions are not re-sent on turns 2 through 29, so you save their cost 28 times).

### What invalidates a cache

A cache is only useful if the prefix is truly stable. Several things silently invalidate a cache, which matters for harness design:

**Reordering tool definitions.** If you serialize your tool list differently on turn 1 versus turn 2 (e.g., alphabetically on turn 1, by frequency on turn 2), the prefix no longer matches and the cache is invalid. A harness must always serialize tools in the same order, every turn.

**Interpolating dynamic values into the system prompt.** If your system prompt includes a timestamp ("Current time: 2024-09-13"), a user ID, or any per-call value, that value changes between turns and the prefix is no longer stable. The cache is invalid on every single turn. This defeats caching entirely. If you need dynamic values, put them after the tools (in the non-cached part of the request).

**Editing earlier messages.** If a harness does in-place editing of old messages (as opposed to pure appending), the cache is invalidated from that edit point forward. Lesson 7 taught that the transcript is the agent's state; that philosophy argues for pure appending and never touching old messages. Prompt caching reinforces this: any edit breaks the cache.

### Caching solves the "tool definitions resent on every turn" cost from Lesson 33

The primary source "Prompt caching" docs notes that tool definitions and system prompts are exactly the kind of stable, large, repeated content that caching is built for. A 10-tool harness with 2,000 tokens of tool descriptions now costs that 2,000 tokens only once per trajectory, not once per turn. On a 50-turn trajectory, this alone saves roughly 98,000 tokens (the definitions appear 50 times without caching, 1 time with caching, so 49 * 2,000 = 98,000 tokens saved).

This is why Lesson 33 and Lesson 34 are paired: Lesson 33 identifies the waste, Lesson 34 names the fix.

### Concurrency: a separate, complementary lever

Prompt caching reduces the cost of any single agent run. Concurrency is a separate question: running multiple agent instances in parallel.

Concurrency can take several forms:

- Running the same task on the same input with multiple agents in parallel, to see if they produce different answers (useful for tasks where multiple valid solutions exist).
- Running variations of a task in parallel (fan-out from Lesson 19), where each agent solves a sub-task.
- Running multiple independent user tasks in parallel (a system serving many users, each with their own agent instance).

In each case, concurrency increases throughput: more tasks complete per unit of wall-clock time. But concurrency does NOT reduce the token cost of any single task. If you run three agents in parallel and each one costs 100,000 tokens, the total is 300,000 tokens, not 100,000 divided by 3. Parallelism trades time for tokens.

### The mistake: conflating caching and concurrency

A common budgeting mistake is assuming that running multiple agents in parallel somehow makes each one cheaper in tokens. It does not. Here is the confusion:

- Correct: Caching reduces the token cost of a single agent's long trajectory by avoiding re-sending stable prefixes.
- Correct: Concurrency reduces wall-clock time by running agents in parallel.
- Incorrect: "We run agents concurrently, so the token cost per agent is lower."

Concurrency reduces time, not tokens. Running agents faster (in parallel) does not make them cheaper (in tokens). If you need to reduce cost and you already have caching, the levers are:

- Better planning (Lesson 16) to reduce the number of turns.
- Better retrieval (Lesson 11) to reduce transcript size.
- Fewer workers (Lesson 19) to reduce multi-agent duplication.
- Failing faster (Lesson 29's diagnosis) to reduce wasted attempts.

### Token budget: two questions

When designing an agentic system, ask two separate questions:

1. **Cost per completed task:** How many tokens will one agent need to solve one task reliably? This is where caching helps, planning helps, and reflection costs.
2. **Throughput:** How many tasks do you need to complete per second or per minute? This is where concurrency helps. If you need 10 tasks per second and each task takes 1 second to complete serially, you need at least 10 agents running in parallel.

Confusing these questions leads to wrong decisions. If you are trying to reduce cost per task, adding more concurrent agents does not help. If you are trying to increase throughput and you have a deadline, adding concurrency is the right lever (but you pay in total tokens: 10 agents * cost per task = total budget).

## Practice

1. ▢ Your agent's system prompt and tool definitions total 5,000 tokens. The agent runs for 30 turns on a single task. Without prompt caching, how many times are those 5,000 tokens sent to the model? With caching, how many times?

<details markdown="1"><summary>Check</summary>

Without caching: 30 times (once per turn), for a total of 150,000 tokens of definition overhead. With caching: once on the first turn, then reused on all subsequent turns, so effectively once. (More precisely, there is a small overhead to retrieve the cache on each turn, but the full 5,000 tokens is not re-transmitted.) Caching saves roughly 145,000 tokens in this case.

</details>

2. ▢ You are implementing prompt caching in your harness. The tool list is generated dynamically: on turn 1, the agent has access to tools A, B, C; on turn 3, the harness adds tool D. The tools are serialized in the order they are generated (A, B, C on turn 1; A, B, C, D on turn 3). Will the cache from turn 1 still be valid on turn 3? Why or why not?

<details markdown="1"><summary>Hint</summary>

What has changed between turn 1's request and turn 3's request? Is that change part of the cached prefix, or after it?

</details>

<details markdown="1"><summary>Check</summary>

No, the cache is invalid. On turn 1, the prefix contains "tools: A, B, C". On turn 3, the prefix contains "tools: A, B, C, D". The prefixes do not match, so the cache does not apply. The harness has to send the full definitions again. This is why dynamic tool addition (adding a tool mid-run based on the agent's decisions) breaks caching. A harness that wants caching should either commit to a fixed tool set upfront, or accept that adding tools mid-run invalidates the cache.

</details>

3. ▢ You are designing the system prompt for a cached agent. The prompt includes "Current date: 2024-09-13" to ground the model in time. Why is this a caching problem?

    - a) The date is not relevant to the model and should be removed.
    - b) The date changes every day, so the cached prefix would become stale after one day.
    - c) The date is a dynamic value that changes between runs, which invalidates the cache on every run because the prefix no longer matches.
    - d) Dates cannot be cached by any system.

<details markdown="1"><summary>Check</summary>

**c)** The system prompt is part of the cached prefix. If you include a hardcoded date that is different on run 1 versus run 2, the cached prefix from run 1 does not match run 2's request, so the cache is useless. The solution is to exclude the date from the cached prefix (put it after the tools, in the per-turn content), or use a fixed date for all runs if the date is not actually critical. This is a common mistake: including per-run metadata in the cached part defeats caching.

</details>

4. ▢ You have two options for scaling your agent system: Option A is to optimize one agent's cost per task via caching and planning, bringing it down from 100,000 tokens to 60,000 tokens. Option B is to run ten agents in parallel without optimization, each still costing 100,000 tokens. If you need to complete 10 tasks and you have unlimited compute, which option minimizes token cost?

<details markdown="1"><summary>Check</summary>

Option A: 10 tasks * 60,000 tokens per task = 600,000 tokens total. Option B: 10 tasks * 100,000 tokens per task = 1,000,000 tokens total, even though they run in parallel. Concurrency increases speed (Option B completes in the time of one task, whereas Option A completes in 10 times that duration serially) but not cost. Option A is cheaper in tokens. If you need to complete 10 tasks as fast as possible, you would combine both: optimize each agent to 60,000 tokens (Option A's approach) and run 10 optimized agents in parallel, for a total of 600,000 tokens and the shortest wall-clock time.

</details>

## Real-world reps

- [ ] Look at an agent harness you have written or reviewed. Find where the system prompt and tool definitions are serialized. Verify that they are always serialized in the same order, and that no dynamic values (timestamps, user IDs, run-specific metadata) are interpolated into that section. If they are, note how it breaks caching.
- [ ] Estimate the token savings from prompt caching for a task you know. Guess: system prompt and tool definition size, number of turns, tokens per turn. Calculate how many tokens are saved by not re-sending definitions. Is the saving worth the complexity of implementing caching?
- [ ] Tomorrow: Design a task that benefits from concurrency (either multiple users, multiple independent sub-tasks, or multiple attempts at the same task). Estimate the total token budget if you run agents serially (one at a time) versus in parallel. Show that both budgets are the same, and explain what you gain and lose with each approach.

## Going further

- [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
