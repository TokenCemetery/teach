---
title: 37. Reviewing Someone Else's Agent Design
description: How to evaluate an agent system systematically, and how to settle a disputed claim by going back to the primary source
type: lesson
---

# Lesson 37. Reviewing Someone Else's Agent Design

**Mission link:** Be trusted to review someone else's agent design and settle disputed claims about it by consulting the primary sources, not by picking a side by default or splitting the difference vaguely.
**Primary source:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Prerequisites:** [Lesson 36](0036-when-not-to-build-an-agent.md)

## Warm-up

1. ▢ What does the autonomy spectrum from Lesson 2 test to distinguish between a workflow and an agent?

<details markdown="1"><summary>Check</summary>

Whether the control flow is decided in advance by the developer, or decided at run time by the model. Not the number of tools, the complexity, or how many model calls are involved, but who chose the path.

</details>

2. ▢ From Lesson 35, what is one way a framework can reduce the cost of running an agent in production compared to writing the harness from scratch?

<details markdown="1"><summary>Check</summary>

Caching stable context (tool definitions, system prompt) so repeated tasks do not re-send those tokens, implementing durable state so an interrupted run can resume, providing built-in tracing and error handling that would take time to wire by hand. The framework buys time-to-reliability and cost reduction at the expense of flexibility or vendor lock-in.

</details>

## Know this

### The review checklist: stages in order

When you review a proposed or existing agent design, walk it through the stages of this track in order, asking the same question at each stage: is this choice justified, and is it documented?

**Stage 1-2: Autonomy spectrum and control flow**

Where does this system sit on the autonomy spectrum? Is it a single prompt, a developer-fixed workflow, or a model-directed agent? Look for the claim in the proposal or documentation. If the claim is just "this is an agent" without explaining why the autonomy is necessary, ask what the fixed-path alternative would have cost. A good design does not just name the choice; it defends it.

**Stage 3-4: Tool surface and schema**

Are the tools named and described in a way a model's reasoning will find useful? Lesson 8 taught that tool descriptions are prompt surface, not API documentation. Tool names should describe what the tool does from the model's perspective, not the underlying endpoint. Parameter descriptions should help the model decide what to pass, not just document the technical schema. Is the tool set tight (avoiding bloat from Lesson 9), or has it accreted tools that are rarely used?

**Stage 5-6: Context and memory strategy**

For a long-running task, what is the strategy? Does the design distinguish between scratchpad (the running transcript within one turn) and across-run memory (facts persisted between runs)? Lesson 11 taught compaction; does the design have a plan for how to shorten the transcript as it grows? If the task involves learning facts and carrying them forward, is there a memory mechanism named, or is the design relying on the transcript alone?

**Stage 7: Reflection and retries**

When a step fails, does the design plan a retry, and does it include explicit reflection (the agent reasoning about why it failed in natural language before trying again)? Or does it just loop and hope the model corrects itself? Lesson 17 taught that silence does not equal learning; a well-designed agent reflects after failure.

**Stage 8: Multi-agent decision**

If the design is multi-agent, does it justify that choice against the single-agent alternative? Lesson 19 taught the coordination cost: an orchestrator-worker system multiplies tokens and fragments context between workers. The design should name the specific benefit that justifies this cost. Is the benefit parallelism (wall-clock time), context isolation (each worker's transcript stays clean), or genuine sub-task independence? And does that benefit apply to this specific task?

**Stage 14: Security and the trifecta**

Does the agent read untrusted content? Does it access private data? Does it have external communication? Lesson 31 taught that all three conditions together make it exploitable. The design should name which conditions are present and which are not, or how the design deliberately removes at least one. If the design has all three but does not acknowledge it, that is a red flag.

**Stage 15: Cost and durability**

Has anyone estimated the token cost per completed task? Is that cost acceptable? If the system uses a framework, is the framework choice justified, or was it picked by default? Lesson 33 taught that real cost per task includes retries and token amplification. A good design names a cost estimate, even if the estimate is rough.

### The specific skill: settling a disputed claim from the primary source

This track presented you with two credible, opposing accounts of multi-agent systems. Lesson 18 described orchestrator-worker patterns and their benefits. Lesson 19 presented Cognition's argument that most multi-agent systems are not worth their cost, and that a single agent with better tools often wins.

Both accounts are correct for their own domains. A reviewer who has only half-remembered both might pick a side reflexively ("I read that single agents are always better, so this multi-agent design is wrong") or split the difference vaguely ("multi-agent is sometimes good"). Neither moves the conversation forward.

The actual skill is to go back to the primary sources and check whether the design's specific circumstances match the conditions under which that source's argument holds.

Anthropic's "How We Built Our Multi-Agent Research System" describes a multi-agent system that worked. The conditions that made it work, from reading that article, include: the sub-tasks were genuinely independent (each researcher focused on a separate angle), the parallelism provided a real wall-clock benefit (results needed to be synthesized under time pressure), and the team invested heavily in orchestration to keep communication clean between workers.

Cognition's "Don't Build Multi-Agents" argues the cost is not worth it for most tasks. The conditions that make their argument strongest include: when sub-tasks share context or refine each other, when you have time and context budget for a single agent to explore serial paths, and when the coordination overhead is high relative to the problem.

Now you are reviewing a design. The proposal says, "We are building a research system with an orchestrator and three researcher workers in parallel." Before you accept or reject multi-agent, ask:

- Are the three research angles genuinely independent, or do they share context and refine each other?
- Is there a real wall-clock deadline, or do you have time to have one agent explore all three angles serially?
- Has the team budgeted for orchestration work, or is coordination an afterthought?
- What would a single agent with broader tools cost in tokens compared to the multi-agent system?

The design's actual circumstances determine which source's argument applies. The job of a reviewer is not to referee between the two sources, but to trace whether the design's situation matches the conditions where one source's argument becomes stronger or weaker. If the design has no answer to these questions, it has not yet settled the question from the primary source; it has just asserted the choice.

### What a good design review accomplishes

A good review does not say "this is good" or "this is bad." It says:

"This design chooses X because Y. I traced that choice to stage Z of the track, where these questions apply. The design answers these questions clearly and these it leaves open. Before committing, the team should resolve the open questions or document the risks."

A review that names specific unanswered questions is more useful than a review that issues a pass or fail. It gives the team something to do. It also gives you leverage: you can ask follow-up questions in writing and hold the design accountable to specific claims, rather than just expressing skepticism.

## Practice

1. ▢ You are reviewing a design for an agent that processes financial documents. The design says the agent will have access to: a tool to read documents from cloud storage, a tool to query a customer database for transaction history, and a tool to file reports in an audit log. The design does not discuss security. Using Lesson 31's framework, what questions should you ask?

<details markdown="1"><summary>Check</summary>

All three conditions of the lethal trifecta are present: the agent reads untrusted content (uploaded financial documents), accesses private data (customer transaction history), and can communicate externally (file audit reports). A good review asks: Is all three trifecta conditions necessary? Can the design remove at least one? For example, can the agent read documents without filing reports directly, instead drafting reports for human approval? Or can it avoid touching the customer database by working only on summary data? The design should either justify why all three are needed, or document the specific security controls (approval gates, audit logging, sandboxing) that mitigate the risk.

</details>

2. ▢ A design proposes an orchestrator with two parallel workers: one researches competitive products, the other researches customer needs. The workers then report findings to a human analyst who synthesizes them. You suspect the single-agent alternative might be cheaper. What question from Lesson 19 should you ask to test this suspicion?

<details markdown="1"><summary>Hint</summary>

Think about what the orchestrator is doing in this design, and whether there is a task the single agent could not do as well or faster.

</details>

<details markdown="1"><summary>Check</summary>

Estimate the token cost: two worker agents plus orchestrator overhead, compared to one agent researching both angles serially. Do the two parallel workers finish faster than one serial agent (parallelism benefit)? Or does the single agent, holding both research threads in one transcript, integrate them more effectively (context coherence benefit)? If the workers finish faster but the token cost multiplier is high, and the human analyst is not time-constrained, the single agent wins. If the researchers need results urgently and the parallelism saves hours, multi-agent justifies the cost. The design should have done this calculation; if it has not, you have found an open question.

</details>

3. ▢ You are reviewing a tool definition for an agent. The tool is called query_customer_database and its description is: "Connect to the customer database and execute any SQL query provided by the user."

    - a) This is a well-designed tool because it is maximally flexible
    - b) This tool violates least privilege; it should be redesigned to execute only specific, pre-authorized queries
    - c) This tool is acceptable because the agent will not misuse it if the system prompt tells it not to
    - d) This tool is acceptable as long as the agent has no external communication ability

<details markdown="1"><summary>Check</summary>

**b)** This tool violates least privilege and should be redesigned. It grants the agent broad database access, which violates Lesson 32's principle that each tool should scope exactly to what it needs. Option (a) is wrong: flexibility for the developer is not the same as a good tool design. Option (c) is wrong: Lesson 31 taught that prompt instructions are not a reliable defense against prompt injection; the defense is architectural. Option (d) is wrong: removing external communication would break one trifecta condition, but the tool would still be over-scoped relative to what an agent actually needs. A better design: a tool called get_customer_orders that takes a customer_id and returns their orders, with no SQL injection vector at all.

</details>

4. ▢ A team is reviewing two proposals for the same task. Proposal A: a single agent with access to web search, code execution, and documentation tools. Proposal B: an orchestrator with three workers (search specialist, code specialist, docs specialist), each with one tool. The team has read Lesson 19 and is split. Two engineers argue Proposal A is better because "Cognition says single agents win." Two argue Proposal B is better because "Anthropic's research system used multi-agent." You are asked to settle this. What should your first step be?

<details markdown="1"><summary>Check</summary>

Go back to the primary sources, not the half-remembered summaries. Reread both articles and identify the specific conditions each describes: What were the characteristics of the task, the context budget, the time pressure, and the coordination complexity in each source? Then examine Proposal A and Proposal B against those conditions. Do they match the single-agent or multi-agent conditions better? Do the proposals themselves describe the task's characteristics and justify their choice against those conditions? Your review should say something like: "Proposal B matches the conditions where Anthropic's research system succeeded (independent sub-tasks, wall-clock deadline), if it can justify the coordination cost. Proposal A matches the Cognition scenario (context-refining work, open time budget), if the single agent's tool menu is broad enough to avoid tool-decision overhead." The job is not to referee the sources but to apply each to the specific task.

</details>

## Real-world reps

- [ ] Find a system you use or know that describes itself as an agent. Try to map it against the checklist in this lesson: where does it sit on the autonomy spectrum? Are the tools described for the model's reasoning or as API docs? Does it discuss security? Write down the checklist items the system addresses clearly and which it leaves silent.
- [ ] Choose one claim from Lesson 19 that Cognition or Anthropic makes about multi-agent systems. Reread the source and identify the specific conditions under which that claim holds. Write down: what task characteristics make the claim true or false? How would you test that claim on a system you are designing?
- [ ] Tomorrow: Review someone else's agent design (from work, an open-source project, or a technical proposal). Use the checklist from this lesson. Write down one open question for each stage the design does not fully address. Share the review with the design's author and see whether your questions match their own concerns.

## Going further

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
