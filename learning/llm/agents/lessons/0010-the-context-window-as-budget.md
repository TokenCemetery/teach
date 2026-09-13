---
title: 10. The Context Window as Budget
description: The context window is a finite resource the harness actively curates over time, not an inert log
type: lesson
---

# Lesson 10. The Context Window as Budget

**Mission link:** Budget the token cost and latency of an agentic loop, and say which part of the loop the amplification comes from.
**Primary source:** [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Prerequisites:** [Lesson 9](0009-return-shapes-and-tool-set-bloat.md), [Trajectory](../GLOSSARY.md)

## Warm-up

1. ▢ In the agent loop from Lesson 6, at what point does the harness decide which tool call to execute?

<details markdown="1"><summary>Check</summary>

The model outputs a tool-call block (name, parameters), and the harness parses it and executes the tool. The model decides which tool by processing the transcript it receives.

</details>

2. ▢ What happens to the transcript every time a tool finishes?

<details markdown="1"><summary>Check</summary>

The result (or error) is appended to the transcript, and the new transcript is sent back to the model on the next loop iteration.

</details>

## Know this

### The transcript grows every turn, and grows expensive fast

Every iteration of the agent loop appends to the transcript. After an agent runs for 10, 20, or 100 turns, the transcript contains every message, every tool call, and every result from the entire run. On the next loop iteration, that entire transcript goes back to the model. On the iteration after that, it goes back again, longer by one more turn.

This means two costs both grow with trajectory length even when nothing new is happening:

- **Token cost**: Every message to the model re-sends all the old turns. A five-turn trajectory costs 5x fewer tokens per call than a 100-turn trajectory. On a long-running agent, this becomes the dominant cost.
- **Latency**: Longer context means more tokens to process, which is slower. The agent waits longer for each response.

### Context rot: model attention degrades as cruft accumulates

As more low-relevance content accumulates in the context, the model's attention becomes noisier. The model's ability to distinguish what still matters (the goal, recent constraints, results it hasn't acted on yet) degrades when it is buried in a large pile of old dead ends and abandoned lines of reasoning. This is sometimes called "context rot". A bloated context is not just expensive: it makes the model worse at the task.

### Naive truncation is risky

The simplest instinct is to drop the oldest turns once the context hits a size limit. But naive truncation risks silently losing critical information. If the truncation boundary falls in the middle of:

- A multi-step instruction the model still needs to follow
- A result the model has not acted on yet
- A constraint or goal statement
- Part of a system prompt or example

then the agent silently becomes broken in ways the harness has no way to detect. The model will not know a key instruction was removed; it will just work with an incomplete understanding and fail in unexpected ways.

### Active curation is a deliberate design choice

Because naive truncation is dangerous and cost grows with trajectory length, the harness cannot treat the transcript as an inert log that just grows. "What stays in context and what goes" has to be a deliberate design decision, built into the harness. The trajectory still exists, but the harness decides what portion of it the model sees on each call.

There are two main strategies for this (covered in the next lesson): compaction and retrieval on demand.

## Practice

1. ▢ An agent makes 50 tool calls over a long research task. On call 51, the model is sent a 20,000-token transcript. On call 52, how many tokens does the model receive in the transcript (roughly)?

    - a) 20,000 tokens
    - b) 20,000 plus the tokens of the new call 51 result
    - c) 40,000 tokens
    - d) Depends on the size of the result from call 51

<details markdown="1"><summary>Check</summary>

**b)** The model receives the original 20,000-token transcript plus the new result appended. If the result from call 51 was 500 tokens, the model gets roughly 20,500 tokens. Token cost grows with each turn, and on very long runs this becomes a serious expense. Option c is wrong because the model doesn't receive the call 51 result twice; option a ignores the new append; option d is correct in spirit (the result size matters) but b is the more precise answer.

</details>

2. ▢ You are designing an agent for a code-review task. The agent reads files, compares them, makes notes, and produces a summary. Why is it risky to just drop the oldest tool results once the transcript hits a 50,000-token limit?

<details markdown="1"><summary>Hint</summary>

What if the boundary of the truncation falls between an old file read and a comparison the model hasn't finished yet? What if a constraint about file scope is in the part you dropped?

</details>

<details markdown="1"><summary>Check</summary>

Naive truncation might drop a tool result (like a file's content) that the model still needs to reference, or a constraint (like "only review files in src/core/") that the model needs to remember. The model won't know the information is missing; it will silently work from an incomplete picture and produce wrong conclusions. The harness must be smarter than just cutting at the token limit.

</details>

3. ▢ Which of the following is true about context rot?

    - a) Context rot only happens if the transcript contains errors
    - b) Context rot is prevented by formatting tool results nicely
    - c) A large transcript with many irrelevant old turns makes the model less accurate, even if no critical information is truncated
    - d) Context rot is not a real problem in modern models

<details markdown="1"><summary>Check</summary>

**c)** The model's attention degrades as low-relevance content accumulates. A big, messy transcript makes it harder for the model to find and prioritize what matters. Option a is wrong because dead ends and completed tasks create noise even without errors. Option b is wrong because nice formatting doesn't solve the signal-to-noise problem. Option d is wrong because context rot is well-documented in long-context tasks.

</details>

4. ▢ You observe that an agent's latency increases as its trajectory grows. Name two reasons why this happens.

<details markdown="1"><summary>Check</summary>

First, the model receives more tokens on each call, which takes longer to process. Second, the model has to sift through more low-relevance content (context rot) to find the information that matters, which affects its reasoning quality and may cause it to make mistakes that waste turns.

</details>

## Real-world reps

- [ ] Describe to someone else (or a note) why you cannot just keep dropping the oldest turns from a transcript once it gets too long. Use an example from a real task you would want an agent to do.
- [ ] Open a transcript from a long multi-turn conversation you have had with a language model, and note how many turns in, the model starts to struggle to remember constraints from the beginning.
- [ ] Tomorrow: Plan a research task an agent might do (read 20 files, compare patterns, produce a summary), and sketch how large the transcript would be if the agent kept every file's full content in memory the whole time versus if it only kept file paths and fetched content on demand.

## Going further

- [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
