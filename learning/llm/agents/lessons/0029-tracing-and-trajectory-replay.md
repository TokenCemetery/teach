---
title: 29. Tracing and Trajectory Replay
description: Using vendor-neutral trace conventions to capture agent runs, and replaying trajectories to step through failures
type: lesson
---

# Lesson 29. Tracing and Trajectory Replay

**Mission link:** Recording agent runs using structured, standardized traces and the ability to replay a saved trajectory lets you hand a colleague the exact point of failure, step through it independently, and move production diagnosis from "let me look at the logs" to "let me step through the trajectory".
**Primary source:** [Specification: "Semantic Conventions for Generative AI", OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
**Prerequisites:** [Lesson 28](0028-cascading-tool-errors.md), [Trajectory](../GLOSSARY.md)

## Warm-up

1. ▢ From Lesson 28: What is the difference between a schema validation error and a hallucinated argument?

<details markdown="1"><summary>Check</summary>

A schema validation error occurs immediately when a required field is missing or a value is the wrong type; the model gets explicit feedback. A hallucinated argument is a well-typed value that passes validation but does not correspond to anything real, so the error happens downstream and the model might misdiagnose why it failed.

</details>

2. ▢ From Lesson 7: What is the one piece of state you need to persist to resume an agent run from turn N?

<details markdown="1"><summary>Check</summary>

The transcript: the full conversation history through turn N, including every model response, tool call, and tool result. When you resume, feed this transcript back into the model and continue the loop from turn N+1.

</details>

## Know this

### Traces, Spans, and Vendor-Neutral Conventions

A trace is a structured, timestamped record of what happened during an agent run. It is made of spans, each representing a discrete operation:

- One span per model call (input: transcript; output: model response and tool calls; timing; tokens used)
- One span per tool execution (input: tool name and arguments; output: result or error; timing)
- One span per loop iteration (start time, end time, turn number)

Without a shared convention, every team and every vendor names these differently. One tool might call a model call's input "prompt", another calls it "messages", another calls it "input". One tool calls the output "response", another calls it "generated_text". This makes traces incomparable: a team using vendor A's tools cannot easily read vendor B's traces, and moving from one vendor to another means rewriting all your trace parsing.

The OpenTelemetry GenAI semantic conventions define a vendor-neutral vocabulary for these spans and attributes. They standardize what information each span should carry:

A model call span includes: model name, total tokens in the input, total tokens in the output, the reasoning effort (if set), tool calls requested, stopping reason.

A tool execution span includes: tool name, whether it is a client tool or server tool, tool result status (success or error), whether there was a cost (for server tools), error message if it failed.

The transaction span wraps everything and includes: agent loop turn number, wall-clock start and end times, whether the turn succeeded or failed, any stopping decision made.

Because these are standardized, a trace produced by one harness can be read by any OpenTelemetry-compatible tool. The same dashboard, analysis script, or visualization that works with one team's traces works with another's. This is the same principle that standardized the tool-call wire formats in Lesson 3: all the underlying concepts (agent loop, model call, tool call) are the same across providers, so a standard vocabulary lets you move between them.

### Why Structured Traces Matter for Diagnosis

The loops and poisoning from Lesson 27, and the cascades from Lesson 28, are all found by reading a trajectory carefully. But a careful read is only tractable if the trajectory is well-structured.

Imagine you are trying to diagnose a failure in an agent run with 47 turns and hundreds of lines of log output. You have print statements mixed with error messages, tool results printed as JSON, and timestamps that may or may not be accurate. You are reading line by line, trying to piece together what happened.

Now imagine the same run represented as a structured trace: each span is tagged with a turn number, each model call is labeled with the model name, each tool call is labeled with the tool name. You can query the trace: "show me all tool calls that failed on turn 10 and beyond" or "show me the reasoning text the model used on turn 23" or "show me a timeline of which spans ran in parallel". This is dramatically faster to diagnose.

Moreover, structured traces let you automate some diagnosis: a simple rule can flag "detect repetitive loops by finding consecutive spans with the same tool name". A post-run analysis can flag "detect cascading failures by looking for error spans followed by different-tool-name spans in close sequence". These patterns are hard to detect in freeform logs; they are straightforward with structured data.

### Trajectory Replay: Testing Hypotheses

Because the transcript is the agent's only persistent state (Lesson 7), you can save a trajectory and feed it back into a fresh run at any point. This is called trajectory replay.

Here is what becomes possible:

**Reproduce the exact conditions**: A customer reports that an agent failed. You save their trajectory (the transcript through the failure point) and feed it into a fresh harness run. The fresh run sees exactly what the original run saw, so if it reproduces the same failure, you have confirmed it. If it succeeds, you have found an issue with the original harness or environment, not the agent logic.

**Step forward from a failure**: You identify the turn where things went wrong (turn 12). You save the trajectory through turn 11, then modify it slightly (maybe add a note in the transcript, or change a tool result) and replay from turn 12. The model, seeing the modified input, might take a different path. This lets you test "what if that tool result had been clearer?" without re-running the whole agent from turn 1.

**Collaborate on diagnosis**: A colleague asks "why did the agent fail at turn 28?" You hand them the trajectory through turn 27 and a description of what you want them to look at. They can replay it themselves, independent of you, and come to their own conclusion. You are sharing the exact state, not just a description of it.

**Build a regression test**: You found a bug and fixed it. Save the trajectory that triggered the bug, replay it with the fixed harness, and verify it now succeeds. Add this to your test suite so the bug does not come back.

### Practical Replay Design

When designing trajectory replay, a few details matter:

**Save the full transcript**, including every turn, every tool call, every result, every error. Do not truncate or sample; the model needs the full context to reason correctly on replay.

**Include harness metadata in a separate, structured section**: the turn number, token counts, error counts, stopping conditions that were checked. This helps you reconstruct the exact state, even if you did not save everything in the transcript.

**Timestamp each span** so you can see how long each operation took and whether there are any unexplained gaps (network latency, retries, backoffs).

**Make replay configurable**: allow someone to replay from turn N, or replay with a modified transcript (to test hypotheticals), or replay with a different model to see whether behavior changes.

### Relationship to Other Diagnostic Tools

Structured traces do not replace careful reading of trajectories. They complement it. You still need to understand the failure modes from Lessons 27 and 28 (loops, poisoning, cascades) to know what patterns you are looking for. But a structured trace makes the patterns easier to see and faster to extract.

Combined, they form a discipline: use traces to navigate the trajectory quickly, use your knowledge of failure modes to spot what matters, and use replay to verify your diagnosis.

## Practice

1. ▢ You are reading a structured trace of an agent run. The trace shows: turn 1 (model call), turn 2 (tool call to search_files), turn 3 (model call), turn 4 (tool call to search_files with identical arguments), turn 5 (model call), turn 6 (tool call to search_files again). You check the tool result for each span and they are identical. Based on the structure of the trace alone, what failure mode should you suspect?

<details markdown="1"><summary>Check</summary>

This looks like a repetitive loop from Lesson 27: the same tool is being called with identical arguments across turns 2, 4, and 6, and the results are identical. The structured trace makes this obvious because each turn and tool call is labeled. In an unstructured log, you would have to manually search for the tool name and arguments across many lines.

</details>

2. ▢ You are replaying a trajectory from turn 15 to debug a failure on turn 30. You feed the transcript through turn 14 back into the model and ask it to continue. On your replay, the agent takes a different path than it did originally and succeeds. What does this tell you about the original failure?

<details markdown="1"><summary>Hint</summary>

Think about what changed between the original run and the replay, besides the model's decision.

</details>

<details markdown="1"><summary>Check</summary>

The original failure was likely caused by something in the harness or environment on turns 15 to 29, not by the model's reasoning. Possible causes: a tool that behaved differently than expected on the original run, a transient failure (network issue, service downtime, quota exceeded), or a nondeterministic element (randomness in tool results or model sampling). Since the replay succeeded with the same transcript and model, the problem was not the model's training or reasoning; it was external conditions. This is diagnostic insight you would not get from just re-reading the trajectory.

</details>

3. ▢ You are designing a structured trace schema for your agent harness using OpenTelemetry conventions. For a tool call span, which of these attributes is most important for diagnosing a cascade failure (Lesson 28)?

    - a) The tool name and arguments
    - b) The tool result or error message
    - c) The wall-clock duration of the tool call
    - d) The model version that called the tool

<details markdown="1"><summary>Check</summary>

**b)** The tool result or error message is most important for diagnosing cascades. A cascade starts when the model misdiagnoses an error, so you need to see exactly what error message was returned. With a clear error message, you can verify whether the model's next decision was a reasonable response to that error. The tool name and arguments (a) are secondary; they show what the model tried, but not whether it understood the failure. Duration (c) and model version (d) are useful for performance analysis and regression detection, but not primary for cascade diagnosis.

</details>

4. ▢ You saved a trajectory through turn 10, and you want to test a hypothesis: "if the tool result on turn 5 had included the customer ID, the agent would have succeeded instead of entering a loop on turns 6 through 10." How would you modify the trajectory and replay to test this hypothesis?

<details markdown="1"><summary>Check</summary>

You would edit the transcript: find the tool result on turn 5, and add the customer ID information to it. For example, change "Tool result: success" to "Tool result: successfully created account; customer ID is 98765". Then replay from turn 6 with this modified transcript. If the agent now succeeds, your hypothesis is confirmed: the missing information was the root cause. If it still loops, the problem is elsewhere.

</details>

## Real-world reps

- [ ] Set up a basic trace capture for an agent you have access to. For at least one run, export the trace and examine its structure. Identify: does it follow a consistent schema? Can you quickly find all the model calls and all the tool calls? Would a query language (like filtering for "all failed tool calls") be useful for debugging?

- [ ] Save a trajectory from an agent run (at least 5 turns). Replay it from the middle (turn 3 or 4) and observe whether the replay produces the same or different results. If different, investigate why.

- [ ] Tomorrow: Design an automated rule that would detect one failure mode from Lesson 27 or 28 in a structured trace. Write pseudocode or SQL that queries the trace and flags the failure. For example, "flag if the same tool is called more than twice in consecutive turns with identical arguments".

## Going further

- [Specification: "Semantic Conventions for Generative AI", OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
