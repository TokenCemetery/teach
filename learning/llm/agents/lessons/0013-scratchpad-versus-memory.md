---
title: 13. Scratchpad Versus Memory
description: The difference between notes an agent keeps during one run and facts it needs across multiple runs
type: lesson
---

# Lesson 13. Scratchpad Versus Memory

**Mission link:** Diagnose a failing agent from its trajectory instead of adding another instruction to its prompt, by understanding what information persists across runs versus what vanishes when a run ends.
**Primary source:** [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Prerequisites:** [Lesson 12](0012-sub-agents-as-context-isolation.md), [Trajectory](../GLOSSARY.md)

## Warm-up

1. ▢ What does a trajectory record?

<details markdown="1"><summary>Check</summary>

The full ordered record of one agent run: every message sent to the model, every tool call the model made, and every result the harness appended back.

</details>

2. ▢ When you spin up a sub-agent to handle a bounded piece of work, does the sub-agent see the full parent transcript?

<details markdown="1"><summary>Check</summary>

No. The sub-agent gets its own fresh transcript with an empty history. It may receive a summary or specific context the parent agent passes to it as the initial prompt, but it does not inherit the parent's full trajectory.

</details>

## Know this

A **scratchpad** is really just part of the transcript, or a note the agent writes to and reads back within a single run. During one long task, the agent might use a scratchpad to track a running total, a multi-step plan, or intermediate findings so the model does not have to re-derive them each turn. The scratchpad is ephemeral: when the harness stops the loop and the run ends, the scratchpad lives in the trajectory but nowhere else. If you start a new agent run an hour later to continue the work, the scratchpad is gone.

This is where a common confusion sets in. An agent kept a scratchpad during a run and "remembered" something. That same agent, restarted fresh, will not remember it. The model might use the same name for the scratchpad tool or file, but the content is gone because the run is gone.

**Across-run memory** is fundamentally different. A new run starts with an empty transcript, so anything the model needs to know from a previous run has to live somewhere outside any single trajectory and be deliberately loaded back in when the next run starts. The harness reads from durable storage, a file or database or retrieval system, before the loop begins, and puts relevant facts into the initial prompt or context so the model can act on them.

Here is a concrete example: An agent is doing code review of a large pull request. During the one-hour run, it keeps a scratchpad listing every file it has already checked, so when the model considers a new file, it can glance at the scratchpad and avoid re-analyzing work it has done. The scratchpad is part of the transcript. When the run ends, the review is done, and the scratchpad is archived as part of the trajectory.

Now picture a different scenario: A coding assistant helps a single user write code across many separate sessions over weeks. The user has a strong preference for a certain code style, naming convention, and library. If the assistant is restarted for each session, it begins with no knowledge of those preferences. The assistant needs across-run memory: a file or note the harness reads at the start of each session that says "User prefers X, uses Y, avoids Z." That fact is not in any single trajectory; it is stored durably and loaded in at run-start.

The key insight from [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) is that these are two separate mechanisms. A scratchpad is a tool or artifact the agent manipulates during a run. Across-run memory is a data layer outside the agent loop, managed by the harness.

## Practice

1. ▢ An agent is solving a multi-step math problem. During the run, it writes its working notes to a scratchpad file. At the end, it appends the final answer to a results file. Days later, you start the same agent again with a different problem. Which will still be there?

    - a) The scratchpad notes.
    - b) The results file.
    - c) Both, because they are both files.
    - d) Neither, because files are cleared on each run.

<details markdown="1"><summary>Check</summary>

**b)** The results file will still be there because it is durable storage outside the run. The scratchpad notes, even though they were written to a file, are only relevant to the old run and are not automatically loaded into the new transcript. If the agent needs those old notes in the new run, the harness must deliberately read them and include them in the initial prompt.

</details>

2. ▢ You are designing an agent that must remember the names of files it has already processed. Would you use a scratchpad or across-run memory?

<details markdown="1"><summary>Hint</summary>

Think about whether the information is used within a single run or across multiple separate runs.

</details>

<details markdown="1"><summary>Check</summary>

If the files are all processed in one long run, a scratchpad is enough. The agent checks the scratchpad each time and avoids re-processing. If the work is split across multiple agent runs, maybe restarted each day or one run per user request, then you need across-run memory so a new run can see what was done before.

</details>

3. ▢ What is the fundamental reason an agent restarted with a fresh harness cannot see notes it wrote to a scratchpad in the previous run?

<details markdown="1"><summary>Check</summary>

Because the scratchpad is part of the transcript, and a new run starts with an empty transcript. The old trajectory is archived but not loaded into the new run. To make scratchpad content visible in a new run, the harness would have to read it from storage and insert it into the initial prompt, which moves it from scratchpad to deliberate across-run memory.

</details>

4. ▢ You are building an agent that helps a user manage a personal task list. The agent adds tasks, completes them, and filters by tag. Should the task list be a scratchpad, local to one run, or across-run memory, persisted between runs? Why?

<details markdown="1"><summary>Check</summary>

Across-run memory. A task list needs to persist beyond one session. If the user starts the agent tomorrow and asks "show me my tasks", the agent must still see today's list. A scratchpad would vanish when the run ends, and the user's data would be lost.

</details>

## Real-world reps

- [ ] Spend two minutes tracing through your own agent code. Find where the harness creates a fresh transcript, empty or with only an initial prompt. Write down what you see.
- [ ] Look for any "memory" or "state" your agent currently saves. Is it loaded by the harness before the loop starts, or only referenced during the run? If it is only during the run, it is a scratchpad. If loaded at start-time, it is across-run memory.
- [ ] Tomorrow: Find or write one scratchpad use, where an agent writes a note, reads it back, then the run ends. Separately, find or imagine one across-run use, where an agent needs a fact from last week's run to answer today's question.

## Going further

- [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
