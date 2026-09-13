---
title: 5. Parallel Calls and Errors as Results
description: How a model can request multiple tools at once, and why tool errors are results, not exceptions
type: lesson
---

# Lesson 5. Parallel Calls and Errors as Results

**Mission link:** Write the agent loop for a stated task, and name what every message in its context is doing and what ends the loop.
**Primary source:** [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
**Prerequisites:** [Lesson 4](0004-schemas-and-who-executes.md)

## Warm-up

1. ▢ In a single model turn, can the model request more than one tool call at the same time?

<details markdown="1"><summary>Check</summary>

Yes. The model can emit multiple tool-use blocks in one response, each with a unique id. The harness executes all of them (possibly in parallel) and gathers the results before sending them back as the next message.

</details>

2. ▢ When a tool fails, what does the harness do: throw an exception that crashes the loop, or return the error to the model?

<details markdown="1"><summary>Check</summary>

Return the error to the model as a tool result. The loop continues; the model gets a chance to retry, use a different tool, or explain the failure.

</details>

## Know this

### Parallel tool calls in one turn

The agent loop is send, execute, append, repeat. A single model response can include multiple tool calls:

```json
{
  "role": "assistant",
  "content": [
    {"type": "text", "text": "I'll gather that data for you."},
    {
      "type": "tool_use",
      "id": "toolu_01XYZ",
      "name": "get_weather",
      "input": {"city": "Lisbon"}
    },
    {
      "type": "tool_use",
      "id": "toolu_02ABC",
      "name": "get_weather",
      "input": {"city": "Madrid"}
    }
  ],
  "stop_reason": "tool_use"
}
```

Each call has its own unique id. The model has decided: "I need weather for both Lisbon and Madrid." Your harness can now:

1. Execute both tools in sequence (one after the other), or
2. Execute them in parallel (both at the same time), depending on your implementation.

The choice is yours. If they are independent and fast, parallel saves latency. If they compete for resources or one depends on the other, sequential is simpler.

### Gathering results before the next turn

Once all tool calls are done, the harness collects the results and sends them back in a single message. Each result is tagged with the id of the call it answers:

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01XYZ",
      "content": "18C, partly cloudy"
    },
    {
      "type": "tool_result",
      "tool_use_id": "toolu_02ABC",
      "content": "22C, sunny"
    }
  ]
}
```

The model now has both results, knows which is which (by id), and decides what to do next. This is the key: all results come back together in one message, so the model processes them as a pair.

### Treating errors as results

When a tool fails, the harness does not crash the loop. Instead, it captures the error and sends it back to the model as a result, just like a successful result. An error tool result looks like this:

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01XYZ",
  "content": "Error: city not found",
  "is_error": true
}
```

The `is_error` field tells the model this result represents a failure, not success. The model reads it and has to decide: retry the same tool with a different city, try a different tool, or give up and explain the error to the user.

### Why errors are results, not exceptions

In many systems, a failed function call raises an exception and stops execution. In an agent loop, a failed tool call is just information: data returned to the model. Why this design?

Because the model is in charge. The model called the tool; it should decide what to do if the tool fails. Maybe it wants to retry. Maybe it wants to use a different tool. Maybe it wants to ask the user for more information. An exception would take that choice away.

This is not forgiving bad code. It is a design choice: treat the model as the orchestrator, not as another function in a call stack. The harness's job is to execute what the model asks, collect the result (success or failure), and hand it back for the model to interpret.

### Errors come from many places

A tool call can fail for many reasons:

- The client tool's code raised an exception (database down, invalid input, timeout).
- A server tool executed but returned an error (API rate limit, file not found, permission denied).
- The harness itself rejected the call (schema validation failed, missing required field).
- The network failed (provider unreachable, connection dropped).

All of these become tool results carrying error messages, not crashes.

## Practice

1. ▢ A model makes two tool calls in one turn: one succeeds, one fails. How does the harness send both results back to the model?

<details markdown="1"><summary>Check</summary>

In a single user-role message with two tool_result blocks, each tagged with the corresponding call's id. One result has `is_error: true` or an error message; the other carries success data. The model gets both in one turn and decides what to do next.

</details>

2. ▢ You have a tool that searches a database. The model calls it with a search that times out. What should your harness do?

<details markdown="1"><summary>Hint</summary>

Think about whose job it is to handle the timeout and what the model needs to know.

</details>

<details markdown="1"><summary>Check</summary>

Catch the timeout, capture the error message (e.g. "Error: search timed out after 30s"), and send it back to the model as a tool result with `is_error: true`. The model then decides: retry with a simpler query, try a different tool, or give up. The loop does not crash.

</details>

3. ▢ The model makes three parallel tool calls. The harness should:

    - a) Execute them one after another so it can stop early if one fails
    - b) Execute them in parallel and wait for all results before sending them back
    - c) Return successful results immediately and only send failed results later
    - d) Cancel the remaining calls as soon as one fails

<details markdown="1"><summary>Check</summary>

**b)** Execute them in parallel and wait for all results. The model asked for three things; it should get three results (success or failure). Stopping early (a) or canceling (d) prevents the model from knowing what happened. Returning results at different times (c) breaks the protocol: results come back in one message together.

</details>

4. ▢ You write a client tool that multiplies two numbers. A model calls it with `x=5, y="hello"`. The harness tries to execute it, the function raises a type error. What is the harness's next step?

<details markdown="1"><summary>Check</summary>

Catch the exception, format the error (e.g. "Error: cannot multiply number by string"), and send it back to the model as a tool result. The model now knows the call failed and can retry with valid inputs or try a different approach. The loop continues.

</details>

## Real-world reps

- [ ] Write or find an agent that makes parallel tool calls. Trace through one execution where the model requests two tools at once. Verify that both results come back together in one message and carry their own ids.
- [ ] Deliberately make a tool fail (call a database that is down, trigger a validation error, or send a tool invalid input). Observe how the harness formats the error and sends it to the model. Watch what the model does next.
- [ ] Tomorrow: write a harness that executes tool calls in parallel (use threading, async, or your language's concurrency model) and collects the results. Verify that it sends all results back in one message even if some tools fail.

## Going further

- [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
