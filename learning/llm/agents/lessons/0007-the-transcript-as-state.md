---
title: 7. The Transcript as State
description: Understanding that the transcript is the agent's only persistent memory between turns
type: lesson
---

# Lesson 7. The Transcript as State

**Mission link:** Recognizing the transcript as the agent's sole state helps you diagnose a failing agent from its trajectory instead of guessing why the model is confused or repetitive, which serves the mission to "diagnose a failing agent from its trajectory."
**Primary source:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Prerequisites:** [Lesson 6](0006-writing-the-loop.md), [Trajectory](../GLOSSARY.md)

## Warm-up

1. ▢ From Lesson 6: After the harness calls the model and receives a response, what must happen before the harness executes any tool calls?

<details markdown="1"><summary>Check</summary>

The response must be appended to the transcript immediately, before any tool is executed. Otherwise the model's own request is never recorded, and a later turn will not show why a tool result is present.

</details>

2. ▢ From Lesson 6: Name two different stopping conditions a harness can check to end the agent loop.

<details markdown="1"><summary>Check</summary>

Any two of: the model returns a turn with no tool call, a max-turns or token-budget limit is hit, the model calls an explicit stop tool, or an error-count threshold is exceeded.

</details>

## Know this

### The Transcript Is All That Persists

Between one call to the model and the next, the harness holds two things:

1. The transcript: the full conversation history, including every model response, tool call, and tool result.
2. Harness metadata: counters (turn count, error count), limits (max turns, max errors), tool registrations, configuration.

The model does not see the harness metadata. The model only sees the transcript. If a fact is not in the transcript, the model does not know it happened.

This is both simple and profound. It means:

- The model cannot reason about something the harness decided internally unless the harness puts it in the transcript.
- Between turns, nothing else persists. No internal flags, no hidden state, no variables outside the harness metadata.
- Replaying an agent run means feeding the same transcript back into the model and continuing from there.

### Trajectory Diverges from Transcript

A trajectory is the full record of what happened: every turn, decision, log, and side effect. A transcript is what the model was shown. They are not the same.

For example:

- The harness executes a tool call, gets a 100KB result, but decides the result is too long and truncates it before appending to the transcript. The trajectory says "tool call succeeded, result was 100KB"; the transcript says "tool call succeeded, result was the first 10KB". The model only knows the second version.
- The harness makes a decision to retry a tool because the first attempt failed. The decision log goes to a file for a human to debug later. But the harness never appends "I am going to retry" to the transcript. On the next turn, the model does not know a retry happened; it only sees the results.
- A tool call fails silently. The harness logs it but does not append an error message to the transcript because the harness designer forgot. The model never learns that the tool failed. On the next turn, the model might ask for the same tool again, confused about why it did not work.

The consequence is that you can look at a trajectory and conclude "the harness made a sensible decision", but if you only look at the transcript, you see a confused model. The model is not confused. The model just was not told.

### A Worked Example: The Tool Result That Never Was

Imagine this scenario:

The agent is supposed to look up a price, then apply a discount, then confirm. On turn two, the model calls a tool to fetch the price. The tool returns "Item XYZ costs $100". The harness executes the tool, gets the result, and appends it to the transcript:

```
Agent turn 1: "I will find the price of item XYZ"
Agent turn 1 tool call: fetch_price(item="XYZ")
Tool result: "Item XYZ costs $100"

Agent turn 2: "I will apply a 10% discount. $100 - 10% = $90."
Agent turn 2 tool call: confirm_price(item="XYZ", price="$90")
```

This works. The model saw the result and reasoned correctly.

Now imagine a variant: the harness is logging results to a database for monitoring. The log insert fails. The harness logs the error to a file, but the developer never appended anything to the transcript. The next turn starts like this:

```
Agent turn 1: "I will find the price of item XYZ"
Agent turn 1 tool call: fetch_price(item="XYZ")

Agent turn 2: "I need to fetch the price. Let me call fetch_price again."
Agent turn 2 tool call: fetch_price(item="XYZ")
```

The model asks for the price again. It is not being stubborn or stupid. The transcript never shows the result from turn one. The model has no way to know the call succeeded. This is called a divergence: the trajectory says "the result was obtained and logged", but the transcript says "nothing happened".

The fix is to always append to the transcript before moving on, even if side effects fail:

```
Tool result (appended immediately): "Item XYZ costs $100"

[Later, harness logs to database, but the append already happened]
Log to database failed [this error never goes in the transcript]
```

Now the model knows the result happened, regardless of downstream errors.

### Why the Transcript as State Makes Resumption Easy

Suppose an agent run gets interrupted. The harness crashes, the network drops, the quota is hit. You want to resume the agent from where it left off.

If the agent stores state in internal variables, flags, and decisions scattered across the harness, resumption is hard. You have to save all of that state, restore it, and hope you did not miss anything.

If the agent's state is just the transcript, resumption is trivial: save the transcript, then start a new run by feeding the same transcript back into the model and continuing the loop from the next turn. The model will see everything it saw before, and it will continue reasoning. No hidden state to reconstruct, no flags to restore, no variables to track. The transcript is the contract.

Similarly, you can replay an agent run to debug it. Feed the trajectory (the full log of what happened) back as a transcript, and see what the model would do next. You can even manually edit the transcript to test what the model would do in a hypothetical situation.

## Practice

1. ▢ An agent is supposed to search for a document, read it, and summarize it. On turn two, it calls a search tool and the tool returns 10 results. Before appending the result to the transcript, the harness filters the results down to the three most relevant ones and appends only those. What does the model see, and why is this design choice visible when you read the transcript?

<details markdown="1"><summary>Check</summary>

The model sees three results, not ten. It does not know that the harness filtered; it only knows what is in the transcript. This is acceptable design if it is intentional: the harness chose to reduce token usage by filtering. The key is that by reading the transcript, you can see exactly what the model saw (three results) and reason about whether the model's next decision was sensible given that information. You are not confused by the fact that ten results existed; the transcript shows the world from the model's perspective.

</details>

2. ▢ A harness developer wants to log which tools were called and how many times. Should they store this count in a harness-only variable, or append a summary to the transcript before each model call?

<details markdown="1"><summary>Hint</summary>

Think about what the model needs to know to make decisions, and what information would only be useful for post-run debugging by a human.

</details>

<details markdown="1"><summary>Check</summary>

It depends on the use case. If the model needs to know "you have already called search three times, maybe try a different tool", then the count must go in the transcript. If the count is purely for monitoring and the model does not need to adjust its behavior based on it, a harness-only variable is fine. But if the model might benefit from knowing the count, put it in the transcript so the model can see it on the next turn. A safe default is to append anything that might affect the model's next decision.

</details>

3. ▢ You are debugging an agent run. You read the trajectory and see that a tool call succeeded and the result was appended. You read the transcript the model actually saw and the result is not there. What happened?

    - a) The harness appended the result, then later removed it from the transcript before calling the model again
    - b) The trajectory and transcript are supposed to be different; the transcript is a summary and the trajectory is complete
    - c) The result was appended to the harness logs but not to the transcript; the model never saw it
    - d) The tool call actually failed and the trajectory is wrong

<details markdown="1"><summary>Check</summary>

**c)** The result was appended to the harness logs but not to the transcript; the model never saw it. Trajectories and transcripts should be nearly identical for the model's perspective (though transcripts might be truncated or sampled for efficiency). If the trajectory says something happened but the transcript does not show it, the most likely cause is that the harness logged it but did not append it to the transcript. This is the bug shown in the worked example. Removing from the transcript after appending (a) would be unusual and defeat the purpose. Transcripts are not summaries; they should be the conversation history (b). A trajectory error (d) is possible but less common than a logging bug.

</details>

4. ▢ You want to build a resumable agent. The run is interrupted after five turns. Write a one-sentence description of what you need to persist to disk to resume the agent from turn six.

<details markdown="1"><summary>Check</summary>

You need to persist the transcript (the conversation history through turn five, including every model response, tool call, and tool result). When you resume, feed this transcript to the model as the starting context, call the model, and continue the loop. The harness metadata (turn counter, error counter, etc.) can be reconstructed or reset; only the transcript is essential.

</details>

## Real-world reps

- [ ] Run an agent (from a library you use or one you write) that makes at least three tool calls. Inspect the transcript it generated. For each tool result, verify that the result is present in what the model would see on the next turn. If any result is missing, trace why (is it because it was not appended, or truncated, or filtered?).

- [ ] Find a place in your agent code or harness where information is logged but not appended to the transcript. Ask yourself: does the model need to know this to make better decisions? If yes, add it to the transcript. If no, leave it as a harness-only log.

- [ ] Tomorrow: Design a resumable agent from scratch. Write pseudocode for the run function that takes a transcript as input and resumes from the next turn. Verify that you do not rely on any harness-only state to make decisions.

## Going further

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
