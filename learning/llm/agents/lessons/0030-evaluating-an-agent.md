---
title: 30. Evaluating an Agent
description: Measuring agent success at the outcome level versus the trajectory level, and why a single successful run does not mean the agent is reliable
type: lesson
---

# Lesson 30. Evaluating an Agent

**Mission link:** Diagnose a failing agent from its trajectory, naming the cause (a loop, poisoned context, a mis-specified tool, a wrong stopping condition) rather than re-prompting at random.
**Primary source:** [Paper: "tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Yao et al., 2024](https://arxiv.org/abs/2406.12045)
**Prerequisites:** [Lesson 29](0029-tracing-and-trajectory-replay.md), [Trajectory](../GLOSSARY.md)

## Warm-up

1. ▢ From Lesson 29: When you read an agent's trajectory to diagnose a failure, what two things should you look for first: the decision the model made, or the actual outcome that decision produced?

<details markdown="1"><summary>Check</summary>

Both, but in this order: first, the decision the model made at each step (which tool did it choose, what arguments did it pass). Second, what the tool actually returned. A reasonable decision with a wrong result points to a tool implementation problem. An unreasonable decision with a reasonable result points to a reasoning failure. Mixing them up is where diagnosis gets stuck.

</details>

2. ▢ From Lesson 29: If a trajectory shows the model making the right decision five times in a row but the agent fails to complete the task, what does that pattern suggest is broken?

<details markdown="1"><summary>Check</summary>

It suggests the harness or the tool implementations themselves are broken, not the model's reasoning. The model is choosing correctly, but something else in the loop is not executing as intended. This could be a tool that claims success but does not actually perform the action, a harness that cuts the loop off too early, or a result being appended to the transcript incorrectly.

</details>

## Know this

### Outcome versus Trajectory

When you evaluate an agent, you can measure two different things, and they are not the same.

**Outcome success** means: Did the agent reach the correct final state? The file was updated correctly. The ticket was triaged into the right category. The user's question was answered accurately. You check the outcome by inspecting the result the user sees.

**Trajectory correctness** means: Did the agent take the right sequence of steps to get there? It called the right tools in the right order with sensible arguments, interpreted results accurately, and avoided circular loops.

An agent task often has many valid paths to the same correct outcome. Grading against one single reference trajectory is usually wrong; grading the outcome (did the file actually get updated, did the ticket actually get correctly triaged) is usually right. However, trajectory still matters: it is how you diagnose *why* something failed, which is what lessons 27 through 29 in this track teach. Outcome tells you whether the agent succeeded; trajectory tells you why it failed.

### pass^k: Reliability Across Repeated Trials

A single successful run does not tell you the agent is reliable. The same agent on the same task can fail on a second attempt due to the stochastic nature of an agent's many decision points compounding across a long trajectory. pass^k measures the probability the agent succeeds on all of k independent trials of the same task. If an agent passes 8 out of 10 times on a task, you know more than if it passed once: you have evidence it is roughly 80 percent reliable on that task. Do not confuse this with task accuracy; it is a much stronger and more honest reliability bar than a single pass or fail run. For the full treatment of how to design and calculate pass^k in your own evaluations, see the lesson that follows this one.

### What Benchmark Papers Actually Measure

Three papers anchor the sources for this stage, and each one represents a different choice in how to grade agents:

**tau-bench** (Yao et al., 2024) evaluates multi-turn tool use against a simulated user (a language model acting as a human) and a domain policy (rules about what constitutes success). It uses repeated-trial reliability measures, so you see pass^k scores, not one-shot results.

**SWE-bench** (Jimenez et al., 2023) evaluates agents on real repository issues with the project's own test suite as the outcome check. If the tests pass, the agent solved the issue. The trajectory is not constrained or graded at all; only the outcome matters.

**GAIA** (Mialon et al., 2023) poses questions that are easy for a person and hard for an agent, requiring multi-step tool use to reach one unambiguous answer. It measures whether the agent lands on the right answer, not whether its reasoning was elegant.

All three prioritize outcome success over trajectory elegance, and all three use repeated-trial evaluation or multiple test cases to move beyond single-run luck.

### The Handoff to Depth

This lesson gives you the vocabulary: outcome versus trajectory, pass^k, task success. The full treatment of building an agent eval lives in the llm/evals track, lesson 13, Evaluating Agents and Tool Use. That lesson covers metrics, judge design, how to build a held-out test set, what statistical significance means, and how to avoid accidentally evaluating the wrong thing. This track's job is only to make sure you know what to measure going in. Read this lesson to know the concepts; read llm/evals lesson 13 for the depth.

## Practice

1. ▢ An agent successfully files a ticket in your issue tracker on the first try. You run it again on a different ticket, and it fails silently, creating an empty ticket with no text. You run it a third time and it succeeds. Is the agent ready for production based on this data?

<details markdown="1"><summary>Check</summary>

No. You have one success, one failure, and another success. That is 2 successes out of 3 trials, suggesting roughly 67 percent reliability. You do not have enough data yet, and 67 percent is too low for most production use. You need at least 10 to 20 trials on diverse tickets to establish a reliable pass^k. The wrong instinct is to assume the one failure was a fluke and the agent is fine; the right one is to treat pass^k seriously.

</details>

2. ▢ You are diagnosing an agent that failed to update a database record. You look at the trajectory and see the model chose the right update_record tool with the correct record ID and new values. The tool returned success: "ok, record updated". But when you check the database, the record was not actually updated. What level should you be looking at to fix this?

<details markdown="1"><summary>Hint</summary>

The model's decision and the trajectory both look correct. The problem is not in the reasoning or the decision making.

</details>

<details markdown="1"><summary>Check</summary>

You should inspect the tool implementation itself. The trajectory shows the model made the right choice and the tool claimed success, but the outcome is wrong. Something between the tool's return value and the actual database state is broken. This could be a tool that logs success but does not actually execute, a harness that does not wait for the tool to finish, or a database connection issue. Trajectory diagnosis here means looking past the words the tool returned and checking what actually happened.

</details>

3. ▢ You are evaluating agents using SWE-bench (real GitHub issues, project test suites as the outcome check). An agent's trajectory shows it made a decision you think is not optimal, taking extra tool calls compared to a more direct path. But the issue's test suite passes. Should you lower the agent's score for the non-optimal trajectory?

    - a) Yes, because the trajectory shows inefficiency
    - b) No, because only the test suite passing matters in SWE-bench
    - c) Score the outcome as pass but flag the trajectory for future optimization
    - d) Only if the non-optimal path took more tokens than a baseline

<details markdown="1"><summary>Check</summary>

**b)** No, because only the test suite passing matters in SWE-bench. SWE-bench is designed to grade outcomes, not trajectories. If the tests pass, the agent solved the issue, regardless of whether it took the most elegant path. The wrong instinct is to grade trajectory elegance on top of outcome; that conflates two separate evaluations. **a)** would shift you toward a metric SWE-bench does not use. **c)** adds complexity that SWE-bench does not require for its primary goal. **d)** introduces a separate constraint (token budget) that is not part of SWE-bench's design.

</details>

4. ▢ You are evaluating an agent on a task by outcome alone: either it reaches the correct final state, or it does not. You run it 100 times, and it succeeds 73 times. You improve the system prompt and retest. Now it succeeds 75 times out of 100. The improvement is small. What does this pattern suggest you should do next?

<details markdown="1"><summary>Check</summary>

It suggests that prompting improvements alone are not sufficient to address the root failures. The 73 to 75 percent gain is modest; most failures persist despite better instructions. You should read trajectories from the failing runs to identify the actual failure mode (a misused tool, a logic error, a context issue, an obstacle the agent does not handle) and then fix that specific problem. Alternatively, the task may simply be too hard for the current model or tool set, and no prompt change will help. Trajectory diagnosis tells you which is true.

</details>

## Real-world reps

- [ ] Pick a simple, repeatable agent task (e.g. "look up a person in a directory", "convert a file format", "answer a factual question using a tool"). Run the agent 10 times and record pass or fail each time. Calculate the empirical pass^k and write down what that number tells you that a single run would not.

- [ ] Take a published benchmark paper on agents (tau-bench, SWE-bench, GAIA, WebArena, or another). Read its evaluation section and identify: what is the outcome metric, is the trajectory constrained or free-form, and what reliability measure does it use.

- [ ] Tomorrow: Find an agent trajectory from a public source (documentation, blog, GitHub). Rewrite an evaluation rubric that grades the trajectory on outcome alone (did the final state match the goal), and a separate rubric that grades on trajectory (did it take sensible steps). Run both rubrics on the same trajectory and compare the scores. Write one paragraph on whether outcome or trajectory told you more about whether the agent worked.

## Going further

- [Lesson 13: Evaluating Agents and Tool Use](../../evals/lessons/0013-evaluating-agents-and-tool-use.md)
- [Paper: "tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Yao et al., 2024](https://arxiv.org/abs/2406.12045)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
