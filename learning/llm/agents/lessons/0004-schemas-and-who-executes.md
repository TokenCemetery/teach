---
title: 4. Parameter Schemas and Who Executes What
description: How JSON schemas constrain what a model can send, and the difference between client and server tools
type: lesson
---

# Lesson 4. Parameter Schemas and Who Executes What

**Mission link:** Write the agent loop for a stated task, and name what every message in its context is doing and what ends the loop.
**Primary source:** [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
**Prerequisites:** [Lesson 3](0003-the-wire-format-of-a-tool-call.md)

## Warm-up

1. ▢ When you send a tool definition to a model provider, what role does the JSON schema play?

<details markdown="1"><summary>Check</summary>

It describes what arguments the tool accepts: names, types, and constraints. The model uses the schema to decide what to send when it calls the tool. A well-formed schema prevents the model from sending invalid or malformed arguments.

</details>

2. ▢ When a model calls a tool and the harness receives the call, how does the harness know whether to execute it locally or send it to a provider?

<details markdown="1"><summary>Check</summary>

You must tell the harness when you define the tool: mark it as a client tool (execute locally) or a server tool (the provider handles it). The model never knows the difference; it only sees the name and schema.

</details>

## Know this

### Schemas as a guardrail

A JSON schema does two jobs. First, it documents what the tool expects: property names, types, whether each property is optional or required. Here is a simple example:

```json
{
  "type": "object",
  "properties": {
    "city": {"type": "string", "description": "The city name"},
    "units": {"type": "string", "enum": ["celsius", "fahrenheit"], "description": "Temperature scale"}
  },
  "required": ["city"]
}
```

This schema says: a tool takes an object with a required `city` (string) and an optional `units` (either "celsius" or "fahrenheit"). The model reads this and knows it must always provide a city but may omit units.

Second, a schema acts as a constraint. When a model calls the tool, it can only send values that match the schema. If the schema says `units` must be one of two strings, the model cannot send "kelvin" or a number. Strict schemas prevent entire categories of malformed calls without the harness having to validate them.

### What happens when required fields are missing

If a model omits a required field, the provider's API raises an error. Most frameworks catch this and send the error back to the model as a tool result: "Error: missing required field 'city'". The model then has a chance to fix it. This is not a crash; it is a normal part of the loop. A well-described schema reduces how often this happens, because the model reads the schema carefully.

### Client tools and server tools

A **client tool** is a function in your own code that the harness executes. You own the implementation:

```python
def get_weather(city: str, units: str = "celsius"):
    # Your code to fetch weather
    return f"18{units[0]}, partly cloudy"
```

When the model calls `get_weather`, your harness runs your function and collects the result.

A **server tool** is something the provider executes on its own infrastructure: a web search, code execution in a sandbox, file system access, or a hosted API call. You define what it does (name and schema), but you never write the implementation. The provider runs it, collects the result, and the harness reads it from the response.

### Why the distinction matters

When you say "the model called a tool," you are being loose with language. The model never executes anything. It emits a structured request saying "run this tool with these arguments." A harness receives that request and executes it, either by:

1. Calling a function you wrote (client tool), or
2. Asking the provider to run something hosted (server tool), or
3. Sending it to a third-party service over the network.

The model does not care which one it is. The distinction is yours: it affects where the code lives, how you write it, and where failures can occur.

### Why this matters for the loop

In an agent loop, the model generates tool calls and the harness executes them. If a tool fails, the result is a tool result carrying an error, not an exception that crashes the loop. This is true whether the tool is client or server:

- A client tool returns an error because the network was down, the database query failed, or your validation logic rejected the input.
- A server tool returns an error because the provider's sandbox timed out, the code raised an exception, or the API rate limit was hit.

Either way, the error is just another tool result, and the model decides what to do next.

### Permissions and server tools

A server tool adds a question: does the model have permission to call it? If you give a model access to code execution, file read, or web access, you are trusting it (within the boundary the schema sets) to use that capability safely. This is a security decision, not a technical one. The schema enforces what arguments the tool can receive, but the schema cannot prevent the model from using the capability for something you did not intend. That is why tool-set design matters, and why not every tool is appropriate for every agent.

## Practice

1. ▢ A tool schema requires a `query` field (string) but has no `max_results` field defined. Can the model send a `max_results` argument? Why or why not?

<details markdown="1"><summary>Check</summary>

No, in a strict schema. JSON schema definitions can allow or disallow extra properties. If the schema does not mention `max_results`, the model cannot send it (or it will be rejected by the provider). The schema is exhaustive: only the properties listed may appear, unless the schema explicitly allows additional properties.

</details>

2. ▢ You have a client tool that queries a database. The schema says `user_id` is required, but the model sends a call without it. What happens next?

<details markdown="1"><summary>Hint</summary>

What does the harness do when the provider rejects a malformed call?

</details>

<details markdown="1"><summary>Check</summary>

The provider rejects it, and the harness sends the error back to the model as a tool result: "Error: missing required field 'user_id'". The model reads this error and has a chance to correct the call. The loop does not crash; the error is a normal result.

</details>

3. ▢ Which statement best describes what happens when a model calls a server tool versus a client tool?

    - a) A server tool runs on your infrastructure; a client tool runs on the provider's infrastructure
    - b) The model sends a request for the tool; the harness decides where to execute it
    - c) A server tool always finishes faster because the provider optimizes it
    - d) You write the implementation for both, but differently

<details markdown="1"><summary>Check</summary>

**b)** The model emits the same structured request either way. The harness reads the tool definition, decides whether it is client or server, and routes the execution accordingly. (a) is backwards: client tools are yours, server tools are the provider's. (c) is false: speed depends on implementation, not whether it is server or client. (d) is partly right but misses that you never write server tools, only define them.

</details>

4. ▢ You define a server tool for "search_the_web" with a schema that requires only a `query` field. The model calls it with `query="python", limit=5`. What does the provider do?

<details markdown="1"><summary>Check</summary>

Either executes the call with just the query and ignores the limit, or rejects the call because the schema does not allow the extra `limit` field. The outcome depends on whether the schema's definition allows additional properties. If the schema is strict (the default), the extra field is an error.

</details>

## Real-world reps

- [ ] Find or write a tool schema for a real task (search, retrieve, compute, or fetch). Mark which fields are required, which have constraints (enums, string length, number ranges), and which are optional. Rewrite one field's description to be clearer.
- [ ] Run an agent or write a harness that calls a tool and intentionally send it an invalid argument (omit a required field, send the wrong type, send a value outside an enum). Observe how the provider responds and how your harness or framework handles it.
- [ ] Tomorrow: design a client tool and a server tool for the same task (e.g. "list files"). Write schemas for both. Explain one trade-off between where each tool lives.

## Going further

- [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
