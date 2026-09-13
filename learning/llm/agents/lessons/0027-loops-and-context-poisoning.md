---
title: 27. Loops and Context Poisoning
description: Two failure modes visible in a trajectory, repetitive loops and silent context poisoning, and how to spot each
type: lesson
---

# Lesson 27. Loops and Context Poisoning

**Mission link:** Diagnosing a failing agent from its trajectory requires recognizing when an agent is stuck repeating the same action versus silently building on a false claim, so you can fix the root cause rather than adding more instructions.
**Primary source:** [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Prerequisites:** [Lesson 26](0026-why-browser-agents-fail-differently.md), [Trajectory](../GLOSSARY.md)

## Warm-up

1. ▢ From Lesson 26: Why does a screen-driven agent fail more often than a tool-calling agent with identical reasoning?

<details markdown="1"><summary>Check</summary>

A screen-driven agent observes through pixels and acts through coordinates, which are fragile references that break with layout changes, loading states, and obstacles. These failure modes are structural and persist even with better prompting.

</details>

2. ▢ From Lesson 7: If a harness appends a tool result to its internal logs but never appends it to the transcript, what does the model know about that result?

<details markdown="1"><summary>Check</summary>

Nothing. The model only sees the transcript. Logging is not enough; the result must be appended to the transcript for the model to know it happened on the next turn.

</details>

## Know this

### Repetitive Loops: When an Agent Gets Stuck

A repetitive loop is when an agent calls the same tool with the same or nearly identical arguments turn after turn, even as the task makes no progress. It is loud and visible in a trajectory.

The underlying cause is usually one of two things:

First, the agent does not notice that a result contradicted or failed to support its plan. The model issued a command expecting a certain outcome, received a different or null result, but did not update its internal model of the world. On the next turn, it tries the same thing again, hoping for a different result.

Example: An agent wants to create a file at `config.json` in a directory. The tool call fails with "permission denied". The harness appends this error. But on the next turn, the model calls the same tool with the same path, as if the error never happened. The model's reasoning was something like "I will try creating the file", and when that returned an error, it did not shift to "I should try a different path or request permission". This is a reasoning failure made visible by the repetition.

Second, the harness's stopping conditions are too loose. The loop keeps running because no condition triggered to stop it. With tight error-count guards (Lesson 6), the loop exits after a few failed attempts and surfaces the failure for diagnosis. With loose guards, the loop continues, repeating the same failing action ten or twenty times before finally stopping.

How to spot a repetitive loop in a trajectory:

1. Scan for consecutive turns with the same tool name.
2. Compare the arguments: are they identical or near-identical?
3. Check the results: are they identical, unchanged, or all failures?
4. Look for repeated reasoning text: does the model use the same phrasing and reasoning across multiple turns?

If all three are true, the agent is in a repetitive loop.

### Context Poisoning: When False Claims Become Ground Truth

Context poisoning is different. Unlike a repetitive loop, which is loud and visible, poisoning is quiet: the model states something false or hallucinated once, and then every later turn treats it as an established fact.

Here is how it happens:

On turn five, the model says: "I checked the database and found that the customer ID is 12345." But no tool call retrieved this fact. Nothing in any prior tool result actually said the customer ID. The model invented it, or misremembered it, or guessed based on a pattern.

That statement gets appended to the transcript like anything else. It looks like ground truth: it is right there in the conversation history, stated as a fact.

On turn six, the model builds on it: "Now I will look up the account for customer 12345." It calls a tool with that ID. The tool might fail ("customer 12345 does not exist"), or worse, it might succeed and act on the wrong customer.

On turn seven, the model has committed further: "I see the account for customer 12345 shows a balance of..." and the cascade continues.

By turn fifteen, you are reading the trajectory and see an enormous chain of reasoning and decisions, all anchored on the false claim that the customer ID is 12345. The model is not being stupid. The model is being consistent: the transcript says the customer ID is 12345, so the model reasons based on that. But the transcript is poisoned.

Why this is different from a hallucinated tool argument (Lesson 28): when a model invents a function argument like a file path, the tool usually fails with an explicit error ("file not found"). Poisoning is worse because it often does not get caught immediately. A false claim in natural language can sit in the transcript unchallenged, and the model will build on it.

How to spot poisoning in a trajectory:

1. Look for a turn where the model states a specific fact (a number, a name, a date, an ID) with high confidence and no hedge.
2. Trace backward: did any prior tool call or tool result actually support this claim? Or did the model state it out of nowhere?
3. If it was unsupported, trace forward: do later turns depend on this claim? Do later tool calls use this value as an argument?
4. If yes on both counts, the context is poisoned.

The diagnostic discipline this lesson is building: a loop is diagnosed by looking at what repeats; poisoning is diagnosed by tracing a false claim back to its origin and forward to its consequences.

### Why Context Rot Compounds Poisoning

Context rot (Lesson 11) is the broader problem: as the transcript grows, old turns become less relevant, the model's attention shifts, and accuracy degrades. Context rot happens to every long agent run, even a healthy one.

Poisoning is more severe. A single false claim in the transcript can anchor all downstream reasoning, and if the claim is buried among dozens of turns, it is hard to spot. The model cannot easily reject a claim that is already in its own transcript; instead, it treats it as established fact.

The mitigation is diagnostic and preventive:

- Read trajectories carefully and watch for unsupported claims the model makes in natural language.
- When designing tools, have them echo back what was resolved: instead of just "success", return "successfully updated customer ID 67890", so the model confirms the actual value.
- Use tight stopping conditions and error counts so loops exit quickly and prevent cascades of bad decisions built on early poisoning.

## Practice

1. ▢ You read an agent trajectory and see the same tool call, get_user_by_email(email="bob@example.com"), repeated on turns 3, 5, 7, and 9. Each time, the result is "user not found". On turn 10, the model calls send_email(recipient="bob@example.com"). Is this a repetitive loop?

<details markdown="1"><summary>Check</summary>

No, this is not a repetitive loop. The agent is repeatedly calling the same lookup tool and getting the same failure, but then it diverged and called a different tool (send_email). The agent did adapt its strategy after the lookup failed. A repetitive loop would be if the model kept calling get_user_by_email on turns 10, 11, 12. This is more like context poisoning: the agent may have made a false assumption on turn 2 (like "I have the user's email") that was never confirmed, and is now acting on it. Read the full trajectory context to identify whether turn 2 or earlier made an unsupported claim about Bob's email.

</details>

2. ▢ An agent is writing a file. On turn three, it calls write_file(path="output.txt", content="...") and gets an error "permission denied". On turn four, the model says "I will try a different approach" and calls create_directory(path="/tmp/") which succeeds. Then on turn five, it calls write_file(path="/tmp/myfile.txt", content="..."). Is this a repetitive loop?

<details markdown="1"><summary>Hint</summary>

Look at whether the model is calling the same tool with the same arguments, and whether its reasoning changed between turns.

</details>

<details markdown="1"><summary>Check</summary>

No, this is not a repetitive loop. Even though the agent encountered an error, it adapted: it changed its reasoning ("try a different approach"), called a different tool, and changed the file path on the write attempt. The model's strategy evolved. A repetitive loop would show the same write_file call with "output.txt" repeated without changes. This agent showed a reasonable problem-solving path, even if the ultimate goal (writing to the original location) was abandoned.

</details>

3. ▢ You are reading a trajectory where on turn 12, the model states "The API key for this service is sk-1234567890". You search back through turns 1 to 11 and find no tool call that returned this key. You search forward through turns 13 to 20 and find that turns 15, 17, and 19 all use this key in API calls. What has happened?

    - a) The model reasoned correctly and inferred the key from context
    - b) The context is poisoned: an unsupported claim is now grounding multiple downstream tool calls
    - c) The model is in a repetitive loop, calling the same API tool repeatedly
    - d) The harness failed to append a tool result that contained the key

<details markdown="1"><summary>Check</summary>

**b)** The context is poisoned. The model stated a fact (the API key) with no prior tool call to support it, and then multiple later turns depend on that claim. This is the textbook definition of poisoning: an unsupported claim becomes the basis for downstream reasoning. You cannot tell from the trajectory alone whether the harness failed to append a result (d) or the model hallucinated; either way, the transcript is now poisoned. **a)** is wrong because inference is not the same as ground truth verification. **c)** is wrong; this is not a repetitive loop because the tool calls are not identical and the model is not repeating the same action.

</details>

4. ▢ A colleague shows you a failing agent trajectory. The first three turns succeeded. On turn four, the model is stuck in a loop calling list_files(directory="/data") repeatedly with no change. The model's reasoning text says "I need to find the target file". What is the most likely root cause: a logic error in the model's reasoning, or a tight stopping condition that should allow more turns?

<details markdown="1"><summary>Check</summary>

This is a logic error in the model's reasoning, not a stopping condition problem. The stopping condition is not tight enough (the loop is repeating), but the fix is not to loosen it further. The problem is that the model called the same tool repeatedly without changing the argument or reasoning. Loosening the stopping condition would just let it repeat more. The fix is to diagnose why the model did not understand the result of the first call to list_files, or did not know how to proceed. The stopping condition should be tightened to exit after one or two failed repetitions, surfacing the problem for human diagnosis rather than letting it repeat endlessly.

</details>

## Real-world reps

- [ ] Find an agent trajectory online (from documentation, a GitHub repository, or a blog post). Read it and identify: does it show any repetitive loops? Does it show context poisoning? Write a paragraph describing what you found and how you spotted it.

- [ ] Run an agent through a task that you expect will fail. Deliberately examine the trajectory for any unsupported claims the model makes in natural language (claims not backed by prior tool results). For each one, note what would happen if the agent proceeded based on that false claim.

- [ ] Tomorrow: Design a tool that would help prevent context poisoning. It could echo back resolved values, add checksums, include timestamps, or validate against a known set. Write a paragraph describing your tool's design and explain how it makes poisoned claims easier to spot in a trajectory.

## Going further

- [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
