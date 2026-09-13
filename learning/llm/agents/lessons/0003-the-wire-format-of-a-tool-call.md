---
title: 3. The Wire Format of a Tool Call
description: What a tool call and its result actually look like in the protocol between your harness and the model provider
type: lesson
---

# Lesson 3. The Wire Format of a Tool Call

**Mission link:** Write the agent loop for a stated task, and name what every message in its context is doing and what ends the loop.
**Primary source:** [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
**Prerequisites:** [Lesson 2](0002-agent-workflow-or-prompt.md), [Tool](../GLOSSARY.md)

## Warm-up

1. ▢ What is the difference between a harness calling a model and a harness executing a tool?

<details markdown="1"><summary>Check</summary>

The harness calls the model by sending it a request (the transcript plus tools) over the network to a provider's API; the model runs inside the provider's infrastructure and returns structured output. A tool is called when the model asks for it by emitting a structured tool-call block; the harness executes it, usually by invoking a function in the same codebase or on the same network.

</details>

2. ▢ In what case might the model send plain text instead of a tool call?

<details markdown="1"><summary>Check</summary>

When the model has finished the task it was working on and is ready to return a final answer to the user, or when it decides (within the limits you set) that it does not need to call a tool for this turn.

</details>

## Know this

### The tool call on the wire

When you send a request to a model provider asking it to use tools, the request includes three things: the model name, the list of available tools (with their names, descriptions, and parameter schemas), and the conversation transcript so far.

A tool definition looks like this: a name, a human-readable description, and a JSON Schema that constrains the parameters the model can send. Here is an Anthropic request with a single tool:

```json
{
  "model": "claude-sonnet-5",
  "max_tokens": 1024,
  "tools": [
    {
      "name": "get_weather",
      "description": "Get the current weather for a given city",
      "input_schema": {
        "type": "object",
        "properties": {
          "city": {"type": "string", "description": "The city name"}
        },
        "required": ["city"]
      }
    }
  ],
  "messages": [
    {"role": "user", "content": "What's the weather in Lisbon?"}
  ]
}
```

When the model decides to call a tool, it does not execute it. Instead, it returns a structured block describing what tool to call and what arguments to pass. The provider stops sending output and signals this with a `stop_reason` field. Here is the full Anthropic response:

```json
{
  "id": "msg_01ABC",
  "type": "message",
  "role": "assistant",
  "content": [
    {"type": "text", "text": "I'll check that for you."},
    {
      "type": "tool_use",
      "id": "toolu_01XYZ",
      "name": "get_weather",
      "input": {"city": "Lisbon"}
    }
  ],
  "stop_reason": "tool_use"
}
```

Notice: the `input` field is already parsed JSON, not a string. Each tool call gets a unique id (here `toolu_01XYZ`) so the harness can tell the model which result answers which call. The assistant may also include plain text before or after the tool call block.

### From wire to execution

Your harness sees this response and knows it must execute `get_weather` with the argument `{"city": "Lisbon"}`. How you do that depends on your tool:

- If it is a **client tool** (a function in your own code), you call it directly: `weather_result = get_weather(city="Lisbon")`.
- If it is a **server tool** (something the provider runs for you, like a hosted web search), the provider already executed it before returning. You extract the result from the response.

### Sending the result back

Once the harness has a result (either from executing the function or from reading the provider's response), it sends it back to the model in a new message, tagged with the tool call's id. The Anthropic format nests it inside a `user`-role message:

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01XYZ",
      "content": "18C, partly cloudy"
    }
  ]
}
```

This message goes into the transcript as a new turn. The model now has both the tool call it made and the result, and it decides what to do next: call another tool, call the same tool with different arguments, or return a final answer.

### OpenAI's wire format (the diff)

OpenAI's API uses the same concepts but different field names and shapes. Rather than restating the whole exchange, here is what differs:

Tool parameters nest under `function.parameters` instead of a bare `input_schema`. The model's tool-call arguments arrive as a JSON-encoded string in `function.arguments`, not a pre-parsed object, so your harness must parse it. The stop signal is `finish_reason: "tool_calls"` instead of `stop_reason: "tool_use"`. The result comes back as a dedicated `role: "tool"` message carrying the `tool_call_id`, not wrapped in a `user` message. Here is an abbreviated example using the same weather task:

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {"name": "get_weather", "arguments": "{\"city\": \"Lisbon\"}"}
      }]
    },
    "finish_reason": "tool_calls"
  }]
}
```

Followed by the result as a `role: "tool"` message:

```json
{"role": "tool", "tool_call_id": "call_abc123", "content": "18C, partly cloudy"}
```

The pattern is identical: tool definition, tool call with id, result tagged with the same id. The names and shapes differ, but any harness that handles one can be adapted to the other by mapping these fields.

## Practice

1. ▢ In the Anthropic response shown above, why does the `input` field contain a parsed JSON object instead of a JSON string?

<details markdown="1"><summary>Check</summary>

The Anthropic API parses tool call arguments on the provider's side before returning them, reducing work for the harness. Your code receives ready-to-use values, not a string to parse. OpenAI sends arguments as a string instead, so you must call `json.parse()` or equivalent in your harness before using them.

</details>

2. ▢ When you send the tool result back to the model, why does it include the `tool_use_id` field?

<details markdown="1"><summary>Check</summary>

The model may have asked for multiple tools in a single turn. The id lets the model match each result to the corresponding call it made, so it knows which answer came from which request.

</details>

3. ▢ In Anthropic's protocol, a tool result travels inside a `user`-role message. In OpenAI's, it travels as a `role: "tool"` message. Why does this difference not matter for the agent loop's logic?

    - a) Because the harness does not need to distinguish them when building the transcript
    - b) Because the model always processes them the same way regardless of role
    - c) Because one protocol is clearly wrong and should be avoided
    - d) Because tool results are not part of the official transcript

<details markdown="1"><summary>Check</summary>

**b)** The model processes them the same way regardless of the role label or message structure. The logic is: here is a result from a tool call you made; what do you want to do now? The protocol detail (inside a user message or as a tool message) does not change that logic. (a) is close but misses the point: role does not matter to the loop itself.

</details>

4. ▢ A harness receives this OpenAI response: `"arguments": "{\"city\": \"Paris\"}"`. How must the harness process this before passing it to the tool?

<details markdown="1"><summary>Check</summary>

Parse it as JSON: `json.loads("{\"city\": \"Paris\"}") yields {"city": "Paris"}`. OpenAI returns a string, and the harness must deserialize it to a dictionary (or object) before unpacking the arguments to the function call.

</details>

## Real-world reps

- [ ] Open a real agent framework's code or documentation (LangChain, Vercel AI, or Claude's own Python SDK) and find where it sends a tool definition to the model. Identify the name, description, and parameter schema. Mark where each one comes from in the code.
- [ ] Trace through one complete tool-call cycle in that same codebase: find where it parses the model's tool-use response, executes the tool, and sends the result back. Mark how the id is used to match them.
- [ ] Tomorrow: write a minimal harness (20 lines or less, pseudocode is fine) that sends a single tool to a model provider, parses the tool-call response, and sends the result back. Do not use a framework.

## Going further

- [Docs: "Tool use with Claude", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Guide: "Function calling", OpenAI](https://developers.openai.com/api/docs/guides/function-calling)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
