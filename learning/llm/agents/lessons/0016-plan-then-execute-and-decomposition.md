---
title: 16. Plan-Then-Execute and Decomposition
description: Explicit upfront planning as an alternative to ReAct, when to use it, and how to handle replanning
type: lesson
---

# Lesson 16. Plan-Then-Execute and Decomposition

**Mission link:** To choose between a single prompt, a fixed workflow, and an agent for a given task, you need to recognize when the extra structure of an explicit plan is worth its cost versus when ReAct's flexibility is cheaper.
**Primary source:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Prerequisites:** [Lesson 15](0015-react-interleaving-reasoning-and-acting.md)

## Warm-up

1. ▢ In ReAct, what happens after a tool call executes and the harness appends the result to the transcript?

<details markdown="1"><summary>Check</summary>

The model's next turn receives the transcript including the tool call and its result. The model can then emit new reasoning that reacts to what the tool actually returned, rather than sticking to a pre-made plan.

</details>

2. ▢ Describe one scenario where ReAct's step-by-step adaptation is an advantage over a rigid upfront plan.

<details markdown="1"><summary>Check</summary>

Any scenario where the environment can surprise the agent: a search returns nothing (not the expected data), a tool fails, a user provides feedback that contradicts assumptions, or new information arrives mid-task. In these cases, ReAct allows the model to observe the surprise and adapt, while a rigid upfront plan would blindly execute the original steps and fail or produce wrong results.

</details>

## Know this

### Explicit planning and decomposition

Plan-then-execute is a distinct approach from ReAct. Instead of interleaving reasoning and action, the agent's first step is to produce an explicit, ordered list of subtasks or actions. The model (or a separate planner) outputs a plan in natural language or structured form. The harness then executes the plan step by step. If replanning is supported, the harness can ask for a new plan if a step fails.

Decomposition is the general idea behind this: breaking a large ambiguous task into several smaller, well-defined ones. A smaller subtask is easier for the model to execute correctly, and easier for a human to verify. Whether decomposition happens explicitly (with a written plan) or implicitly (in ReAct's reasoning at each step), the principle is the same.

### When explicit planning earns its cost

An explicit plan takes up space in the transcript and requires an extra model turn (at least one) before any action runs. This is overhead. When is that overhead worth paying?

**Human review before execution:** If a task involves high stakes (calling an API that costs money, sending an email, deleting data), a human can read the plan before the harness runs any tool. The human can reject the plan, ask for changes, or approve it with confidence. By contrast, ReAct runs the first action before a human has visibility into what is about to happen. For tasks where human approval is required or reduces risk, an explicit plan is a good trade.

**Multi-step tasks with high cost to wrong actions:** If each step is expensive to undo or runs high risk, committing to a plan upfront and having a human review it before execution reduces the chance of costly mistakes. An exploratory task where steps are cheap (reading data, making queries that cost nothing) does not need this overhead.

**Tasks with a clear, stable structure:** Some tasks decompose into an obvious sequence that does not change: "Download file A, parse it, transform it, upload the result." If the steps are unlikely to change mid-execution, writing them out upfront and executing them is simpler and cheaper than reasoning about each step anew.

### The stale plan problem and replanning

Here is the risk: the plan was made before any tool ran. If step 1 was supposed to find a file, but it does not exist, step 2's plan assumes the file is there. Step 2 will fail or produce wrong results. The harness then has two choices: blindly continue executing the stale plan (and likely fail) or trigger replanning (ask the model to emit a new plan given the new state).

Replanning is not free: it costs another model turn, and the trajectory now shows multiple plan stages, which uses context. But replanning is often cheaper than ReAct for high-structure tasks, because the model can think through the new path quickly instead of reasoning step by step.

If replanning is not supported, a plan-then-execute harness will fail silently or loudly when reality does not match the plan. This is why "do you support replanning?" is a key design question for plan-then-execute agents.

### Decomposition without explicit planning

Note that decomposition and explicit planning are separate ideas. An agent can decompose tasks implicitly, through ReAct-style reasoning at each step. The model reasons "to solve this, I need to do X, then Y, then Z" and then does X, observes the result, reasons again, and moves to Y. This is implicit decomposition. An explicit plan writes that "X, Y, Z" list down as a structured artifact before execution starts.

For many tasks, implicit decomposition (ReAct) is simpler and more robust. Use explicit planning when the overhead (human review, clarity, structure) is worth the cost.

### Comparing the three patterns

Act-only is the simplest but hardest to debug. ReAct adds reasoning and observation, making it visible and adaptive. Plan-then-execute adds an upfront structure that can be reviewed before any action runs, at the cost of an extra model turn and potential staleness if the plan's assumptions break.

Choose based on your task and constraints:

- Short exploratory task, no high stakes? Use ReAct.
- Task with clear steps that are unlikely to change? Use plan-then-execute.
- Task where a human needs to review before execution starts? Use plan-then-execute with an approval gate.
- Task where steps are expensive and failures are costly? Use plan-then-execute with replanning support.

## Practice

1. ▢ A task is "File a complaint with the city, check that it was received, and notify the user." This involves filling out a form (not free to redo), checking a confirmation email, and sending an email. Would explicit planning or ReAct be better for this task? Why?

<details markdown="1"><summary>Check</summary>

Explicit planning is better. The steps are clear and stable: fill form, check confirmation, send email. There is no reason to expect this sequence to change mid-execution. A human should review the plan before the form is filled out, since that step is not easy to undo. ReAct would work but would run the form-filling step before a human can review it, adding risk.

</details>

2. ▢ You are building an agent that investigates why a user's account is locked. The agent might check account status, search logs for failed logins, look for a security flag, or query support tickets, depending on what it finds. Would explicit planning or ReAct be better?

<details markdown="1"><summary>Hint</summary>

Think about whether the sequence of steps is known in advance or whether it depends on what earlier steps return.

</details>

<details markdown="1"><summary>Check</summary>

ReAct is better. The steps depend on what the agent finds at each stage. If the account status shows a security flag, the next step is to check that. If it shows a different error, the next step is different. The sequence cannot be written down upfront. ReAct's step-by-step reasoning and observation is more natural than trying to plan all possible branches.

</details>

3. ▢ Which of the following best describes when replanning becomes necessary in a plan-then-execute agent?

    - a) Whenever the agent encounters any tool call with a parameter the plan did not mention.
    - b) When a tool call fails or returns unexpected data that contradicts an assumption in the original plan.
    - c) Whenever the user changes their mind about the task.
    - d) After every single tool call, to ensure the plan stays fresh.

<details markdown="1"><summary>Check</summary>

**b)** Replanning is triggered by actual failures or surprises: a tool returned nothing when the plan expected data, an API call failed, or a search did not find what was expected. a) is wrong, tools often have parameters the plan did not list; that is not an error. c) is wrong, user changes are a task-level issue, not specific to plan-then-execute versus ReAct. d) is wrong, replanning after every step defeats the purpose of having a plan and is inefficient.

</details>

4. ▢ An agent's explicit plan is "Step 1: Search for user input. Step 2: Summarize results. Step 3: Compare summary to user's original question." After step 1, the search returns no results. The harness does not support replanning. What will likely happen?

<details markdown="1"><summary>Check</summary>

Step 2 (summarize results) will fail or produce wrong output because there are no results to summarize. The agent will either hang, return an error, or produce a summary of nothing. The harness will have no way to pivot: it was committed to the plan from the start. This is the cost of a plan-then-execute harness without replanning support. The fix is either to add replanning (ask the model to make a new plan when step 1 fails) or to switch to ReAct, where the model would reason after step 1's result and decide to try a different search.

</details>

## Real-world reps

- [ ] Take a multi-step task you do regularly (e.g., process an order, investigate an issue, review a document for compliance). Write out the steps you actually follow. Do the steps always happen in the same order, or does the order depend on what you find at each step? If the order is fixed, that is a candidate for plan-then-execute with explicit approval. If the order is adaptive, that is a candidate for ReAct.
- [ ] Build a small plan-then-execute agent for a fixed-sequence task (e.g., downloading a file, parsing it, transforming it, uploading it). Run it five times on different inputs and read the trajectories. Did the agent ever fail because the original plan did not match reality? If yes, add a replanning gate after tool calls that might fail.
- [ ] Tomorrow: Find an existing agent you have built or used. Classify it as act-only, ReAct, or plan-then-execute based on its trajectory. Write a one-sentence note about why that pattern fits the task.

## Going further

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
