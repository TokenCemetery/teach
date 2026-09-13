---
title: 6. Writing the Loop
description: Building the agent loop from pseudocode and choosing stopping conditions deliberately
type: lesson
---

# Lesson 6. Writing the Loop

**Mission link:** Writing the agent loop is the core skill for building an agent yourself, which directly serves the mission to "write the agent loop for a stated task, and name what every message in its context is doing and what ends the loop."
**Primary source:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Prerequisites:** [Lesson 5](0005-parallel-calls-and-errors-as-results.md), [Agent loop](../GLOSSARY.md)

## Warm-up

1. ▢ From Lesson 5: What gets appended to the transcript when a tool call fails?

<details markdown="1"><summary>Check</summary>

An error tool result, tagged with the failed call's id and marked as an error, appended just like a successful result would be. The loop does not crash; the model sees the failure as a normal turn.

</details>

2. ▢ From Lesson 5: Why is it safe for a model to ask for two tools in parallel rather than one after the other?

<details markdown="1"><summary>Check</summary>

Because each tool call gets its own unique id, and the harness returns each result tagged with that same id. The model can always match a result back to the call that produced it, regardless of execution order.

</details>

## Know this

### The Agent Loop as Code

At its core, an agent loop is simple. Here it is as pseudocode:

```
function run_agent(model, tools, transcript, max_turns):
    for turn_count in range(max_turns):
        response = call_model(model, transcript)
        transcript.append(response)

        if response.has_no_tool_calls():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)
            transcript.append(result)

    return "Max turns reached"
```

This is the harness. The model chooses which tool to ask for and when to stop asking. The harness enforces the limits and mechanics.

Notice the structure: **call the model, append the response, check if we're done, otherwise execute tools and append their results, then loop back to the top**. Every turn, the transcript grows. Nothing is held in memory outside the transcript.

### Why the Transcript Must Grow on Every Turn

Beginners sometimes build a loop that looks like this:

```
function run_agent_wrong(model, tools, transcript, max_turns):
    for turn_count in range(max_turns):
        response = call_model(model, transcript)

        if response.has_no_tool_calls():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)
            transcript.append(result)  # Only append results, not the model's request
```

This is a bug. If you do not append the model's tool-call response to the transcript before executing the tool, the model will not "remember" asking for the tool on the next turn. When the harness calls the model again, the transcript does not say "the model asked for search" or "the model asked for calculator". The model might ask for the same tool again, confused. This is called forgetting the request in the literature. The transcript becomes incoherent.

The fix is to append the response **immediately** after calling the model, before doing anything else:

```
function run_agent_correct(model, tools, transcript, max_turns):
    for turn_count in range(max_turns):
        response = call_model(model, transcript)
        transcript.append(response)  # Append right away

        if response.has_no_tool_calls():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)
            transcript.append(result)
```

Now when the loop repeats and calls the model again, the transcript includes "the model said it would call search", and the model can reason about the result.

### Stopping Conditions: Choosing Deliberately

An agent loop needs to stop. There are several places to choose:

**Max turns**: The outer loop counts turns and exits if the count exceeds a limit. This is a safety guard. Without it, a broken model or tool loop could run forever.

**No tool calls**: The model response contains no tool calls. This is the "happy path" stop: the model has decided to answer. Check this after appending the model's response.

**Explicit stop tool**: You can offer a tool called `stop` or `finish` that the model can call to exit explicitly. The harness checks for this and returns. This is useful if the task is open-ended and the model needs an explicit "I am done" action. If you offer this tool, document it clearly so the model understands when to use it.

**Error count guard**: If a tool call fails, the harness appends the error as a result. If too many tool calls fail in a row, the harness stops and returns an error trajectory instead of continuing forever. This prevents retry loops.

These are not mutually exclusive. A production harness might check all of them:

```
function run_agent_with_guards(model, tools, transcript, max_turns, max_errors):
    error_count = 0

    for turn_count in range(max_turns):
        response = call_model(model, transcript)
        transcript.append(response)

        if response.has_no_tool_calls():
            return response.text

        if response.has_explicit_stop_tool_call():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)

            if result.is_error():
                error_count += 1
                if error_count > max_errors:
                    return "Too many errors"
            else:
                error_count = 0

            transcript.append(result)

    return "Max turns reached"
```

The point is that these decisions should be visible in your code, not hidden or accidental. You choose when to stop, and you choose how many chances the agent gets to recover.

## Practice

1. ▢ In the pseudocode loop shown above, why must `transcript.append(response)` happen before the `if response.has_no_tool_calls()` check?

<details markdown="1"><summary>Check</summary>

The transcript must include the model's response so that later turns (or an observer reading the trajectory) can see what the model said and decided. If you check for stopping before appending, you return the model's text, but the transcript never shows that the model responded at all. Also, other information in the response (like which tools the model considered but decided not to call) would be lost.

</details>

2. ▢ A model calls a tool and the harness executes it successfully, returning a result. The result gets appended to the transcript. On the next loop iteration, the harness calls the model again. What does the model see in the transcript that it did not see on the previous turn?

<details markdown="1"><summary>Hint</summary>

Think about what was appended on the previous loop iteration, just after the model was called the first time.

</details>

<details markdown="1"><summary>Check</summary>

The model sees its own tool-call response appended before the loop executed the tool. On the second turn, the transcript includes both that response and the tool's result. Without the response being appended first, the model would only see the result, as if the tool had been called by something other than the model.

</details>

3. ▢ You are building a harness with a max-errors guard: if three tool calls fail in a row, stop the loop. What do you need to reset the error counter to zero?

    - a) When max turns is reached
    - b) When a tool call succeeds and returns a non-error result
    - c) When the loop starts
    - d) When the model response contains no tool calls

<details markdown="1"><summary>Check</summary>

**b)** When a tool call succeeds. The guard is to catch a pattern of repeated failures. If one tool fails, then the next one succeeds, the retry loop is broken and you want to allow more failures. If you reset only at the start (c), you could never stop; if you reset at max-turns or no-tool-calls (a, d), the guard does not work. Resetting on success is the pattern: one success resets the counter.

</details>

4. ▢ Your model is supposed to search, read a document, and then summarize. On the third turn, it asks for the same search tool again. The search was successful the first time. What is the most likely bug in your harness, given what you know about how transcripts work?

<details markdown="1"><summary>Check</summary>

The harness is not appending the model's tool-call response to the transcript after the model is called. The model never sees its own request for the search tool from the first turn. When it is called on the third turn, the transcript shows the search result but not the request, so the model does not know why the result is there and asks for search again. The fix is to append the response immediately after calling the model, before executing the tool.

</details>

## Real-world reps

- [ ] Write the basic agent loop pseudocode from memory without looking at the lesson. Compare it to the pseudocode shown under "The Agent Loop as Code". Check: do you append the response before checking for no tool calls?

- [ ] Find an agent implementation in any open-source project (a library you use or a public repository). Read the loop code. Identify where the transcript is built and where the stopping condition is checked. Note whether stopping conditions are explicit (visible in an if statement) or hidden (in a condition buried in a call to another function).

- [ ] Tomorrow: Sketch the four stopping conditions (max turns, no tool calls, explicit stop, error count guard) in pseudocode. For each one, write one sentence about why it matters: what problem does it solve?

## Going further

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
