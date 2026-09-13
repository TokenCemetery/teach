---
title: 21. Provider Formats and Tool Discovery at Scale
description: How MCP and provider-specific wire formats are separate layers, and why loading every tool into context does not scale to many connected servers
type: lesson
---

# Lesson 21. Provider Formats and Tool Discovery at Scale

**Mission link:** Understand the limits of naive tool discovery when an agent connects to many MCP servers, and recognize when to trade eager tool loading for lazy or programmatic discovery.
**Primary source:** [Article: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
**Prerequisites:** [Lesson 20](0020-mcp-tools-resources-and-prompts.md)

## Warm-up

1. ▢ In Lesson 3 you learned two wire formats: Anthropic represents a tool call with `input_schema`, and OpenAI uses a different shape called `function.parameters`. If you switch from Anthropic's API to OpenAI's, do you need to change your MCP server, your MCP client, or both?

<details markdown="1"><summary>Check</summary>

Neither. Your MCP server stays the same (it knows how to expose tools in MCP format). Your harness changes, because it has to translate MCP tool definitions into whichever provider's wire format the model expects. The model provider changes, but the MCP protocol does not.

</details>

2. ▢ In Lesson 9, you learned about tool-set bloat: if you present the model with too many tool definitions, it slows down, gets confused, or forgets which tool to use. When an agent connects to five MCP servers with ten tools each, does the model see fifty tool definitions up front?

<details markdown="1"><summary>Check</summary>

Only if the harness loads all fifty definitions into context before the loop starts. That is the naive approach. But there are other ways: the harness could load tools only when the model asks for them, or translate the tool definitions into code the model can explore and call programmatically.

</details>

## Know this

### Two independent layers

MCP is a protocol between an agent harness and external tools or data sources. It defines how a client and server talk to each other and what capabilities a server can expose. But MCP does not care what wire format the model uses.

At the same time, the model has a provider, and that provider has a specific way of representing tool calls. Anthropic's API accepts tools in one shape. OpenAI's API accepts them in another. This wire format is a separate layer between the harness and the model.

These two layers are independent:
- The MCP client (harness side) speaks MCP to the MCP server. The MCP server is agnostic about which model will eventually use these tools.
- The harness then translates the MCP tool definitions into whichever provider's wire format the model expects. Anthropic? Use `input_schema`. OpenAI? Use `function.parameters`.

The harness has to do the translation, because it sits in the middle. But changing one layer does not require rewriting the other. If you switch model providers, you do not rewrite your MCP servers. If you connect to a new MCP server, the wire format between harness and model does not change.

### Tool discovery at scale

On a single agent, you might hand-wire two or three tools into context at the start. Tool-set bloat (Lesson 9) sets in around five to ten tools. But what if the harness is connected to a dozen MCP servers, each with ten to twenty tools? Hundreds of tool definitions.

The naive approach is to load every tool definition at startup, translate each one into the provider's wire format, and hand them all to the model in its initial context. This reproduces tool-set bloat at a much larger scale. The model reads hundreds of definitions, wastes tokens on descriptions it does not need, and slows down on every turn because every tool is in context. And if a new tool is added to a connected server, the entire context and model behavior changes.

This is the tool discovery problem at scale: you can connect to many servers, but not by loading everything up front.

### The code execution idea

The Anthropic Engineering article "Code Execution with MCP" proposes a solution: instead of loading tool definitions into context, present the available tools as code the agent can discover and call programmatically.

For example:
- The harness defines a helper function list_available_tools() that queries the connected MCP servers and returns a directory of callable functions: their names, descriptions, and parameters.
- The harness defines a helper function call_tool(name, args) that takes a tool name and arguments, finds the tool on the connected servers, and invokes it.
- Instead of giving the model fifty tool definitions up front, the harness tells the model: "You can call list_available_tools() to see what you can do, or call_tool(name, args) to do something specific."

Now the model has two meta-tools: tools for discovering and calling other tools. It can explore the tool space without loading every definition into context at the start. It calls list_available_tools() when it needs to find a tool, learns what is available in that moment, and then uses what it needs. The resident context stays small.

This trades eager loading for lazy discovery. The model has to spend a turn calling list_available_tools() before it can call a specific tool, so there is a latency cost. But if the harness is connected to fifty servers, the tokens saved by not keeping every tool definition in context outweigh the cost of the extra turn.

### When to use each approach

Eager loading (put every tool in context at startup) works when:
- You have a small fixed set of tools (two to ten).
- The tools are relevant to every agent task.
- Context is not constrained.

Lazy loading (define list_available_tools() and call_tool() and let the model discover what it needs) works when:
- You have many tools (dozens or more).
- Tools are specialized and not all relevant to every task.
- Context is constrained and every token matters.
- The latency cost of an extra turn is acceptable.

Programmatic discovery (present tools as code the model can read and run) combines both ideas: small initial context (just the discovery functions) and the ability to explore the tool space without hand-loading definitions.

## Practice

1. ▢ You are using Anthropic's API with three MCP servers. You switch to OpenAI's API. Do you need to update your MCP servers, your harness, or both?

<details markdown="1"><summary>Check</summary>

Only your harness. The MCP servers do not change; they still expose tools in MCP format. Your harness was already translating MCP definitions to Anthropic's wire format; now it translates them to OpenAI's format instead. The translation layer changes, but the servers and the protocol do not.

</details>

2. ▢ Your agent is connected to ten MCP servers with a total of one hundred fifty tools. You want to use the "code execution with MCP" idea: define list_available_tools() and let the model discover what it needs. What are two consequences of this design?

<details markdown="1"><summary>Hint</summary>

Think about context size and latency. When does the model ask for the list? What does that cost?

</details>

<details markdown="1"><summary>Check</summary>

Context is smaller because you are not loading one hundred fifty tool definitions up front, only two functions and maybe a brief description of what they do. Latency increases because the model has to call list_available_tools() on a turn when it wants to explore, adding at least one extra turn before it can call a specific tool. This is a worthwhile trade-off if context is tight or tools are rarely all needed together.

</details>

3. ▢ Your harness has only three tools, and they are all relevant to every task the agent performs. Should you use eager loading, lazy loading, or programmatic discovery?

    - a) Lazy loading with list_available_tools()
    - b) Eager loading: put all three in context at the start
    - c) Programmatic discovery with call_tool() functions
    - d) Rotate which tools are in context to save tokens

<details markdown="1"><summary>Check</summary>

b) With a small set of tools that are always relevant, eager loading is simplest and fastest. You waste no tokens on discovery functions, you add no latency, and the model always has the tools it needs. Lazy and programmatic discovery add overhead without benefit when the tool set is small and universal. Option d is an antipattern: rotating tools in and out creates confusion and non-determinism.

</details>

4. ▢ You define list_available_tools() to query all connected MCP servers and return their tool names and descriptions. When the model calls this function, does the call count toward your API tokens?

<details markdown="1"><summary>Check</summary>

Yes. Calling list_available_tools() costs tokens just like calling any other function: the model sends the call, the harness executes it, and the result comes back in the transcript. You are trading off the tokens spent on upfront tool definitions against the tokens spent on discovery calls. With many tools, the trade is usually positive.

</details>

## Real-world reps

- [ ] Draw a diagram showing the two layers: MCP protocol on one side (harness to external servers), provider wire format on the other side (harness to model). Label what happens if you switch providers vs switch MCP servers.
- [ ] Estimate the token cost difference between eager loading (put one hundred tools in context) and lazy loading (list_available_tools() on demand) for your own agent. Does laziness make sense?
- [ ] Tomorrow: Implement a simple list_available_tools() function that queries a real MCP server you have access to and returns a summary the model can read.

## Going further

- [Article: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Specification: Model Context Protocol](https://modelcontextprotocol.io/specification)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
