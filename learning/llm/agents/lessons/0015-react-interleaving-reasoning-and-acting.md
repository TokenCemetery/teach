---
title: 15. ReAct: Interleaving Reasoning and Acting
description: Pattern of pairing short reasoning steps with each action, so the model can observe and adapt
type: lesson
---

# Lesson 15. ReAct: Interleaving Reasoning and Acting

**Mission link:** To diagnose a failing agent, you will recognize whether it is executing actions without visible reasoning (where the root cause hides), following a rigid upfront plan (where environment surprises cause cascading failures), or interleaving reasoning with observation (where failure signals flow back into the next decision).
**Primary source:** [Paper: "ReAct: Synergizing Reasoning and Acting in Language Models", Yao et al., 2022](https://arxiv.org/abs/2210.03629)
**Prerequisites:** [Lesson 14](0014-files-as-memory.md), [Agent loop](../GLOSSARY.md)

## Warm-up

1. ▢ When you store an agent's memory in a file across runs (say, a chat transcript or a log of past decisions), what becomes easier to debug and verify about the agent's behavior?

<details markdown="1"><summary>Check</summary>

A file-based memory lets you read the exact state the agent saw before each decision, so you can replay its reasoning and check whether it made a sensible choice given the information available at that moment. If the agent seems broken, you can read its prior trajectory to find the exact step where it went wrong, rather than guessing.

</details>

2. ▢ Name one risk of storing large memories in files: what happens if the agent never prunes or compacts the file?

<details markdown="1"><summary>Check</summary>

The file grows without bound, consuming disk space and context budget when it is passed to the model. The agent eventually cannot fit the entire history into the context window, forcing the harness to choose which older memories to drop and which to keep.

</details>

## Know this

### Three shapes for reasoning and acting

The agent loop naturally supports several different patterns for when reasoning happens relative to when actions run. The ReAct paper identifies three, and understanding the trade-offs between them is key to diagnosing agent failures.

**Act-only:** The model receives the current task and state, and immediately emits a tool call with no stated reasoning. The harness executes the tool, appends the result, and loops. This is the simplest structure.

The risk: When something goes wrong, you cannot tell why the model chose this action. Did it misunderstand the task? Did it think it was calling a different tool? Without a reasoning trace, debugging is guesswork. You end up adding clarifications to the prompt ("Think step by step", "Verify your answer"), but the model still produces no visible reasoning for you to inspect, so the clarifications may not help.

**Reason-then-act-once:** The model reads the task, reasons through the entire plan upfront in text (call this the "thought" phase), then commits to a sequence of tool calls to execute the plan. Once the plan is committed, the harness runs all the steps without replanning.

This avoids the blank-slate guessing of act-only, since you can see the model's full reasoning. But it has a hidden cost: the plan is made before any tool runs. If a tool call fails or returns unexpected data, the plan becomes stale. The model cannot react to surprises because it has already committed to the sequence. You end up having to re-run the agent and hope the new reasoning phase corrects itself.

**ReAct (Interleaved reason-act-observe):** The model reasons aloud about what to do next (a short "thought" or "reasoning" text), then emits a tool call. The harness executes the tool, appends the result to the transcript, and loops. The next turn, the model reads the previous thought, the action it chose, and the actual result, then reasons about the next step based on what it now sees.

This is the ReAct pattern. The model's reasoning is visible (you can debug it), but more importantly, the reasoning at each step can incorporate the actual outcome of the last step. If a search returned no results, the next thought can pivot to a different search. If an API call failed, the next thought can reflect that and try a workaround. The reasoning is not a rigid upfront plan; it is an observation of what just happened, feeding into what happens next.

### Why ReAct wins when the environment surprises you

Reason-then-act-once works well in closed-world scenarios where the plan's assumptions are guaranteed to hold. Real tool-calling happens in open-world scenarios: files are missing, searches return nothing, APIs are down, users give contradictory instructions. In those cases, ReAct's step-by-step adaptation is cheaper and more robust than re-running the full reason-then-act cycle.

Think about the agent loop itself, from Lesson 6. A model turn produces text (which may include reasoning) and a tool call. That tool call is executed, and the result is appended to the transcript. The next turn, the model sees the result and emits new text and a new tool call. By design, the agent loop already supports ReAct: any reasoning text the model emits is preserved in the transcript, the next turn can observe it, and the next turn can emit new reasoning that reacts to the observed result.

"Does my harness support ReAct?" is really just "Does my harness keep the model's reasoning text in the transcript and feed it back in the next turn?" The answer, in nearly every harness worth using, is yes.

### Diagnosing act-only and plan-then-act-once failures

If you inspect an agent's trajectory and see no reasoning text before tool calls, you have an act-only agent. Failures are hard to diagnose. Adding more data to the context (longer task descriptions, more examples) might help, but without reasoning text, you have no visibility. The fix is to prompt the model to emit reasoning (a "thought" field, a "reasoning" section in the tool call, anything) and preserve it in the transcript. Then you move into ReAct and debugging becomes possible.

If you see a big reasoning block at the start, followed by a sequence of actions with no intermediate reasoning, you have plan-then-act-once. When the agent fails, you are likely seeing a plan that did not survive contact with reality. The fix is to allow replanning: after each tool result, emit new reasoning before the next action. Again, this moves you into ReAct. Some failures will vanish because the model can now adapt.

## Practice

1. ▢ An agent is told to "Search for information about climate change, then summarize the top 5 results." It emits one search tool call with no preceding reasoning text. The search returns 10 results about climate science, and the agent next emits a summarization tool call with no reasoning in between. The summary is inaccurate. Why is it hard to tell whether the model misunderstood the task, misunderstood the results, or made a genuine error in reasoning?

<details markdown="1"><summary>Check</summary>

There is no reasoning text in the transcript, so you cannot see what the model's internal "goal" was or how it interpreted the search results. The missing reasoning makes it impossible to distinguish between, for example, "the model did not realize the search returned 10 results and thought it needed to search again" versus "the model saw the 10 results and misunderstood the task as summarizing all of them, not the top 5." Adding reasoning text before the summarization step (a ReAct-style thought) would let you see which misunderstanding occurred and fix the prompt accordingly.

</details>

2. ▢ You are building an agent that takes user feedback and refines a document. The agent's plan (emitted upfront) is "Fix grammar, then add examples, then check length." The first pass succeeds. But the user feedback in the second run is "I do not like the new examples you added, but keep the grammar fixes." The agent re-uses the upfront plan unchanged and adds examples again, ignoring the feedback.

<details markdown="1"><summary>Hint</summary>

What makes the plan stale in this scenario? What information is the agent not seeing when it is planning?

</details>

<details markdown="1"><summary>Check</summary>

The plan was made without seeing the user's feedback. In plan-then-act-once, the reasoning phase happens before any tool runs, so it cannot incorporate new information that arrives mid-trajectory. The fix is to allow reasoning and replanning after each tool result (here, after each refinement step), so the agent's plan can adapt when user feedback contradicts the original assumptions.

</details>

3. ▢ Which of the following is a sign that you should move an agent from act-only to ReAct?

    - a) The agent is too slow and you need to speed up tool calls.
    - b) The agent's failures are hard to diagnose because you cannot see why it chose each action.
    - c) The agent needs to use 10 tools instead of 5.
    - d) The agent's context window is almost full.

<details markdown="1"><summary>Check</summary>

**b)** Act-only agents produce no reasoning text, so their failures are opaque. Switching to ReAct (adding a reasoning step before each action) makes the model's reasoning visible, which is the core win for debugging. a) is wrong because ReAct does not speed up tool calls, it adds reasoning text which takes time. c) is wrong, tool count is unrelated. d) is wrong, context pressure is a separate concern from whether the agent reasons aloud.

</details>

4. ▢ An agent searches for "best pizza restaurants in Portland" and receives 5 results. If the agent is running in ReAct mode, what should happen next in the transcript?

<details markdown="1"><summary>Check</summary>

The agent should emit a reasoning step (a "thought" or "reasoning" section) that observes the search results and decides what to do next (e.g., "These results look good, I now have enough information to answer. I will summarize them" or "I need more details about restaurant hours, I will fetch those next"). This reasoning is based on what the search actually returned, not on an upfront plan. By including it in the transcript, the next tool call (if any) can be grounded in the actual result.

</details>

## Real-world reps

- [ ] Take an existing agent you have built or are familiar with. Read its trajectory (one full run). Count how many tool calls have reasoning text immediately before them. If fewer than 80% have reasoning text, rewrite the prompt or the tool schema to emit reasoning, then run it again.
- [ ] Deliberately break a tool an agent relies on (e.g., make a search API return an empty result). Run the agent on a task it would normally succeed at. Read the trajectory. Did the agent emit reasoning that acknowledged the broken tool and pivoted to a different approach? If not, add a prompt instruction for reasoning and retry.
- [ ] Tomorrow: Ask a colleague to read an agent's trajectory without seeing the task. Can they infer what the agent was trying to do at each step from the reasoning text alone? If they cannot, add reasoning prompts.

## Going further

- [Paper: "ReAct: Synergizing Reasoning and Acting in Language Models", Yao et al., 2022](https://arxiv.org/abs/2210.03629)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
