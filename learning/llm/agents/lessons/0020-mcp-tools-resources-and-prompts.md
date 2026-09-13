---
title: 20. MCP: Tools, Resources, and Prompts
description: Model Context Protocol as a standardized interface for agent harnesses to discover and invoke external tools, read data, and use templates
type: lesson
---

# Lesson 20. MCP: Tools, Resources, and Prompts

**Mission link:** Understand MCP as a provider-neutral protocol that solves the integration problem, so you can reason about which tools an agent can access and how to add new ones without rewriting the harness.
**Primary source:** [Specification: Model Context Protocol](https://modelcontextprotocol.io/specification)
**Prerequisites:** [Lesson 19](0019-coordination-cost.md), [Tool](../GLOSSARY.md)

## Warm-up

1. ▢ In Lesson 3, you learned that a tool has a name, description, and parameter schema. When your harness runs, where does it get those definitions: from the model, from the harness code, or from somewhere else?

<details markdown="1"><summary>Check</summary>

From the harness code. The harness author writes tool definitions by hand or loads them from a configuration file, then tells the model about them before the loop starts.

</details>

2. ▢ When you connect an agent to a new data source (a database, an API, a file store), who does the work: the model, the harness, or both?

<details markdown="1"><summary>Check</summary>

Both. The harness author writes code to integrate the data source (fetch it, parse it, handle errors), then tells the model about it by adding a tool definition. The model decides whether and when to call it.

</details>

## Know this

### The M times N problem

Without a shared standard, connecting an agent harness to external tools and data sources requires custom integration work. If your harness can invoke N different tools or data sources, and there are M different agent-building teams or frameworks, you get M*N separate integrations: each team writes bespoke code to talk to each tool or data source.

MCP (Model Context Protocol) solves this by creating a shared interface that both the harness side and the tool side can implement. A tool or data source implements one MCP server. Any MCP-compatible harness can connect to it. A harness implements one MCP client. Any MCP-compatible server can expose capabilities to it. Now you have M+N integrations instead of M*N.

This matters because without it, scaling an agent to use more tools means quadratic growth in custom code. With MCP, scaling means building or connecting to more standard servers.

### Three primitives

MCP defines three kinds of capabilities a server can expose to a client:

**Tools** (comparable to the tools from Lesson 3): actions the model can invoke. A tool has a name, description, and input schema. When the model decides to call it, the client sends the request to the server, which executes the action and returns a result. The model sees the result and continues. This is exactly like the client and server tools you already know, but the interface is standardized so either side can be swapped out.

**Resources**: data that the MCP client can read directly without the model invoking it as a tool call. A resource might be a file, a database record, a web page, or a live API response. The client can list available resources and fetch one by name. This is different from a tool because the model does not invoke it; the harness reads it and decides whether to put the data into context or what to do with it. Resources let the harness pull in relevant information without blocking the model's turn or adding tool-call overhead.

**Prompts** (prompt templates): reusable prompt templates that an MCP server exposes for a client to fill in and use. A prompt template might be "analyze this code for security issues" or "summarize this document." The client can list available prompt templates, fetch one by name, and fill in parameters. This is distinct from tools and resources: instead of executing an action or fetching data, the harness uses the template to construct a message to send to the model, embedding it into the agent's own instructions or reasoning steps.

### Basic lifecycle

A client connects to a server. They negotiate capabilities: which of tools, resources, and prompts this particular server actually supports. The server advertises what it has; the client decides what to use.

Then, depending on what the client supports and what the harness needs:
- The client can list available tools and fetch their schemas, then present them to the model.
- The client can list available resources and fetch data proactively, using what it learns to inform the agent's decisions.
- The client can list available prompt templates and use them to construct instructions or reflection steps.

A single server can expose all three, or just one or two. The protocol is symmetric: both the client and the server know the interface, so either side can be generic.

### Transports

MCP servers can run locally (over stdio, a simple process-to-pipe channel between the harness and the server on the same machine) or remotely (over an HTTP-based transport, where the server runs on a different machine or cloud service). The transport affects latency, deployment, and failure modes, but not the protocol itself. A harness that supports both transports can connect to a locally-running MCP server for fast iteration and to a remote MCP server for resilience or cross-team collaboration.

## Practice

1. ▢ You are building an agent that needs to read from a database and call a web API. Your team's database has an MCP server. The web API does not. Do you have to write custom integration code for both, or just one?

<details markdown="1"><summary>Check</summary>

Just one. The harness can connect to the database's MCP server without custom code. For the web API, your team still writes a wrapper (either in the harness or as a new MCP server around the API). This is the M+N principle: the MCP server did half the work for you.

</details>

2. ▢ Your agent needs to check the weather and then decide whether to suggest an outdoor activity. Should this be a tool (which the model invokes) or a resource (which the harness reads proactively)?

<details markdown="1"><summary>Hint</summary>

Think about when the harness learns the weather and when the model needs to know it. Does the model decide whether to ask, or does the harness always fetch it?

</details>

<details markdown="1"><summary>Check</summary>

It depends. If the weather is always relevant to the decision, make it a resource: the harness fetches it before every turn and includes it in context. If the weather is only relevant when the model is considering outdoor activities, make it a tool: the model asks for it when it needs it. A tool lets the model decide when to look; a resource feeds information that the harness always wants the model to have.

</details>

3. ▢ Your agent uses three MCP servers: one for email, one for a calendar, and one for a document store. The email server supports tools and resources. The calendar server supports only tools. The document server supports tools, resources, and prompts. Which of the following can the harness do?

    - a) Use resources from all three servers, since all three support at least tools
    - b) Use tools from all three, resources from email and documents only, and prompts only from documents
    - c) Use prompts from all three servers
    - d) Use tools and resources from all servers equally

<details markdown="1"><summary>Check</summary>

b) The harness can only use what each server actually exposes. Email supports tools and resources, so the harness can use both from email. Calendar supports only tools. Documents support tools, resources, and prompts. The harness negotiates capability per server and only calls what is advertised. Prompts are only available from the documents server, so c is wrong. All servers do not support resources, so a and d are wrong.

</details>

4. ▢ You are deciding whether to deploy an MCP server locally (stdio) or remotely (HTTP). What is the trade-off you should consider?

<details markdown="1"><summary>Check</summary>

Local (stdio) is faster and simpler to set up on the same machine, but couples the harness to the server process. Remote (HTTP) means the server can run anywhere and survive harness crashes, but adds network latency and failure modes (the server might be slow or unreachable). Neither changes the MCP protocol itself; both work the same way to the client. Choose based on how much latency you can tolerate and whether you need resilience or cross-machine access.

</details>

## Real-world reps

- [ ] Read the Model Context Protocol specification at modelcontextprotocol.io and identify one MCP server that already exists for something in your domain (email, documents, databases, code repositories).
- [ ] Sketch the M*N vs M+N comparison for your own work: list M harnesses or teams and N tools or data sources you care about, then estimate how much custom integration code the M+N approach would save.
- [ ] Tomorrow: Try connecting to an existing MCP server (via a client that supports it) and observe how the three primitives (tools, resources, prompts) are actually used in practice.

## Going further

- [Specification: Model Context Protocol](https://modelcontextprotocol.io/specification)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
