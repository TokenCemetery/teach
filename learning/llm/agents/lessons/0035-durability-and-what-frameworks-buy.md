---
title: 35. Durability and What a Framework Buys
description: Durable, resumable agent execution as an engineering problem, what frameworks concretely offer, and a decision principle for adopting one
type: lesson
---

# Lesson 35. Durability and What a Framework Buys

**Mission link:** Decide whether to write an agent harness yourself or adopt a framework, based on what guarantees you actually need for deployment.
**Primary source:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Prerequisites:** [Lesson 34](0034-prompt-caching-and-concurrency.md), [Harness](../GLOSSARY.md)

## Warm-up

1. ▢ From Lesson 7, you learned that because the transcript is an agent's whole state, resuming a run means feeding the saved transcript back to the model. What does this mean in terms of whether a run is "resumable in principle"?

<details markdown="1"><summary>Check</summary>

In principle, any agent run is resumable because the transcript captures everything the agent knows. If you save the transcript after every turn and a crash happens, you can load the saved transcript, append the last failed or incomplete turn, and continue. The transcript is the whole state, so resumption requires nothing else.

</details>

2. ▢ From Lesson 33, you learned that a cost-per-task budget sums the full cost of all attempts, retries, and reflections until a task succeeds. If an agent crashes mid-run and you have to restart from the beginning, how does that affect the cost-per-task budget?

<details markdown="1"><summary>Check</summary>

The restart adds a full additional attempt to the budget. If an agent crashes on turn 15 of a 30-turn run, you have lost 15 turns of work and have to pay for all 30 turns again. The cost-per-task budget is now roughly doubled (two full 30-turn runs instead of one). This is a significant cost penalty, which is why durability (avoiding crashes and resuming automatically from the last saved state) matters for cost control.

</details>

## Know this

### Durability is distinct from resumability in principle

Lesson 7 established that agent runs are resumable in principle: the transcript is the state. But "resumable in principle" and "resumable in production" are different things. Resumability in principle says "if a human manually saves the transcript and restarts the agent, it will continue." Durability in production says:

- The transcript is automatically persisted to durable storage (a database, a file system with backups, not just memory) after every turn.
- If the process crashes, the last persisted state is automatically loaded and the run resumes without manual intervention.
- If multiple agents run concurrently, each one's state is tracked independently so a crash in one does not lose work in another.
- If a tool call times out or the network fails, the agent retries or rolls back gracefully, not leaving partial state.

This infrastructure work is distinct from the agent loop itself (Lesson 6). The loop does not care about durability; it just processes what it is given. The harness (the code around the loop) has to build durability as an explicit concern.

### What crashes and failures look like without durability

Without durable state, here are the failure modes:

- Process crash mid-run: the agent's entire transcript is lost (if it was only in memory). The user has to restart the task from the beginning. The cost-per-task budget is doubled.
- Network timeout on a tool call: the harness does not know if the tool succeeded or failed. It might retry, it might not. The transcript might have a result appended, or it might not, depending on the harness's error handling. The state becomes inconsistent.
- Agent hangs waiting for a tool result: the process is stuck and must be killed manually. No checkpoint is saved. The entire run is lost.
- Multiple agents running concurrently, one crashes: the other agents continue, but there is no visibility into which part of the system failed or how to resume the failed one.

Each of these is a real deployment problem. "Durable execution" is the practice of building systems that handle these failures automatically and correctly.

### What a framework concretely provides

When you adopt a framework for agent development, it typically includes some or all of these guarantees:

**Durable state and automatic checkpointing.** The framework automatically persists the transcript (and any agent state) to durable storage after every turn. If the process crashes, the next run automatically loads the last checkpoint and resumes from there. You do not have to write the persistence logic yourself.

**Graph-based control flow.** Instead of writing a loop manually (Lesson 6), you describe the agent's structure as a graph: "After this step, if the result is X, go here; if Y, go there." The framework handles the control flow and persistence, so you focus on the nodes (the steps) rather than the loop itself. This is useful for agents with complex branching or conditional logic.

**Built-in retry and backoff policies.** When a tool call fails (a network error, a timeout, a rate limit), the framework has a configured retry strategy: wait a bit, try again, exponential backoff. You do not have to implement retries in your own harness.

**Integrated tracing and observability.** The framework automatically generates Lesson 29's structured traces: timestamped events, spans, metadata about each step. You can query this trace without wiring it up yourself. Some frameworks integrate with observability backends (like a tracing service) so you can see agent runs in a dashboard.

**Rollback and compensation.** Some frameworks allow you to define compensating actions: if step A succeeded but step B failed, automatically undo A. This is useful for agents that make changes to external systems and need to recover if later steps fail.

Not all frameworks offer all of these. Some are minimal (checkpointing plus retries). Some are comprehensive (all of the above plus more). The decision principle (below) is about which capabilities you actually need.

### What frameworks do NOT buy

It is important to be clear about what frameworks do not solve:

- The agent loop itself is still the same (from Lesson 6). The framework does not make the loop simpler or faster; it just wraps it with durability and observability.
- Token cost is not reduced by using a framework. A framework does not make agents cheaper; it makes them more reliable and observable.
- Agent reasoning quality is not improved by a framework. A framework does not make the model better at decisions; you still have to design the tools, the prompts, and the planning (Lessons 8, 9, 16) yourself.
- The framework is not neutral. Adopting a framework commits you to its abstractions (graph-based control flow, its configuration format, its observability model, its deployment constraints). Switching frameworks later is expensive.

### The decision principle: when to adopt a framework

The "Building Effective Agents" article notes that many teams build a minimal agent loop (Lesson 6) first and only later realize they need durability. The decision to adopt a framework should be based on whether the framework's guarantees solve a deployment problem you have, not on whether writing the loop felt hard (the loop is the easy part).

Adopt a framework when:

- **You need durable execution.** Your agents will run for long enough (or be important enough) that crashes losing work is unacceptable. A simple loop with no persistence is not suitable for production tasks.
- **You need observability at scale.** You have multiple agents running concurrently and need to see what each one is doing, trace failures, and correlate logs. A basic print-statement harness will not scale.
- **You have complex control flow.** Your agent needs conditional branching or loops (e.g., "if this condition, call this set of tools; otherwise call this other set"). A framework's graph-based model is cleaner than hand-coded conditionals.
- **You want built-in retry and backoff.** You are calling external APIs that might fail temporarily, and you want the framework to handle retries automatically with exponential backoff. Writing this yourself is tedious and error-prone.

Do NOT adopt a framework when:

- **You are experimenting.** In research or prototyping, a simple loop is faster to iterate on than learning a framework. Come back to the framework decision once the approach is stable.
- **Your agent is simple.** A single agent with a few tool calls and a straightforward goal does not need the complexity of a framework. A loop plus a transcript file might be all you need.
- **You have unusual deployment constraints.** Some frameworks assume specific environments (cloud, Docker, etc.) or have performance characteristics that do not fit your constraints. You might need a custom harness.
- **The framework is immature or tightly coupled to a vendor.** Durable execution patterns are still evolving. Some frameworks are well-established and documented (search for reviews and production deployments); others are not. And some are tightly coupled to one vendor's API, which limits your flexibility later.

### How to evaluate a framework

If you decide to adopt a framework, here are the questions to ask:

- Does it support checkpointing and resumption? How often? Is the checkpoint granularity (per turn, per attempt, per task) what you need?
- What observability does it provide? Can you query traces? Can you integrate with your existing logging and monitoring?
- What control flow abstractions does it support? Does it match your agent's structure, or would you have to bend your agent to fit?
- What is the failure mode if the framework crashes? Can you recover your transcripts and continue without the framework?
- How does it handle concurrency? Can multiple agents run independently without interfering?
- What vendor lock-in is there? If you need to switch later, how much work would it be?

The last question is important: there is no single authoritative, vendor-neutral source for durable agent execution the way there is for, say, the MCP specification (Lesson 20). Durable execution patterns are documented mainly inside individual frameworks' own guides. So treat this lesson as the vocabulary and decision framework, not a framework comparison. When you evaluate a specific framework, read its own documentation to understand its specific guarantees.

### The end-to-end story: from loop to production

Here is the arc of a typical agent system:

1. **Development (Lesson 6).** Write a loop that sends the transcript to the model and executes tools. This is fast to prototype.
2. **Testing (Lesson 29).** Build traces and diagnosis to understand what your agent is doing, when it fails, and why. Learn where your agent is fragile.
3. **Optimization (Lessons 10-34).** Implement context management, prompt caching, better planning. Reduce token cost and latency.
4. **Deployment.** You now have to decide: what does production look like? If it is a one-off task or an experiment, a script plus a transcript file might be enough. If it is a service serving users, a simple loop is not suitable. You need durability, observability, retry policies, and a way to track many concurrent agents. This is where the framework decision comes in.

A framework is not the start; it is the answer to "who builds and maintains the durability and observability layer?" You build it yourself (a custom harness plus infrastructure), or you adopt a framework's answer (accept its abstractions and constraints). Both are legitimate choices. The framework decision is not "can I write an agent loop" (Lesson 6 already answered that yes). The question is "do I want to build this production infrastructure myself, or adopt an existing framework's solution?"

## Practice

1. ▢ You are running an agent to process 1,000 customer support tickets. Each ticket takes an agent 20 turns to handle. If the agent crashes on turn 10 of ticket 500 and you have no checkpointing, how many total turns are lost or wasted?

<details markdown="1"><summary>Check</summary>

You lose 10 turns of work on ticket 500. When the process restarts, you have to re-run the entire ticket from the beginning, wasting another 20 turns. You also have to re-run tickets 1-499 (which did complete but are still in memory/lost if the process crashed). If you had checkpointing, you would save after each ticket, so losing one ticket costs 20 turns, not more. For 1,000 tickets * 20 turns = 20,000 turns total. Without checkpointing, a crash mid-task wastes roughly 10,000 turns (half of the remaining work plus re-running the task that crashed). This is why durability matters for large-scale tasks.

</details>

2. ▢ You have two options for your agent system: Option A is to write a custom harness with durability (checkpointing, retries, observability). This takes 2 weeks to build and debug. Option B is to adopt an existing framework (which handles all of this for you) and spend 1 week learning it. Both systems will run the same agent logic. Why might Option B still be more expensive in the long run?

<details markdown="1"><summary>Hint</summary>

Think about flexibility, maintenance, and what happens if your requirements change or you want to switch systems.

</details>

<details markdown="1"><summary>Check</summary>

Option B commits you to the framework's abstractions and implementation. If your requirements change (e.g., you need a different control flow or a different storage backend), you are constrained by what the framework supports. If you want to switch frameworks later, you have to port all your agent definitions and workflows. Option A (custom harness) is more flexible but more expensive upfront and to maintain. The trade-off is: Option B saves time initially but locks you in; Option A costs more initially but gives you long-term flexibility. The break-even point depends on your expectations of how long the system will run and how likely requirements are to change.

</details>

3. ▢ You are evaluating two frameworks for agent development. Framework X provides checkpointing and retries but no integrated observability (you have to wire up tracing yourself). Framework Y provides all of that plus a graph-based control flow builder, but requires all agents to be defined in its proprietary DSL. Which framework should you choose if your main concern is avoiding work when an agent crashes and automatically resuming?

    - a) Framework X, because it is simpler and forces you to learn less.
    - b) Framework Y, because its integrated observability will help you debug crashes faster.
    - c) Either one provides the core checkpointing feature you need; the choice depends on your other constraints.
    - d) Neither; you should build a custom harness so you are not locked in.

<details markdown="1"><summary>Check</summary>

**c)** Both frameworks provide checkpointing and automatic resumption, which is your primary concern. The differences (observability, DSL) are secondary. If you need integrated observability or like the graph-based model, Framework Y might be worth the lock-in. If you prefer to wire up observability yourself or you have existing agent code in Python/Go/etc., Framework X is fine. Neither is wrong; it depends on your other constraints. Option a is wrong because simplicity alone is not the deciding factor. Option b conflates observability (nice to have) with durability (the requirement you stated). Option d is not wrong (a custom harness always gives you flexibility) but it avoids the question; if durability is important, you need some solution, and the decision is whether that solution is a framework or custom.

</details>

4. ▢ You have built an agent using a simple loop (Lesson 6) with no persistence. The agent works well in testing. You now want to deploy it to production to handle real user requests. What is the minimum infrastructure you need to add before you can confidently say the agent is durable in production?

<details markdown="1"><summary>Check</summary>

At minimum: (1) Automatic persistence of the transcript to durable storage (a database or filesystem with backups) after every loop turn. (2) Automatic loading of the last persisted transcript on process restart, so the agent resumes from the last checkpoint, not the beginning. (3) Graceful error handling for tool calls: if a tool times out or returns an error, the agent either retries with a backoff policy or explicitly records the failure in the transcript (so the state is consistent). (4) For concurrent agents, each agent must have its own isolated transcript and checkpoint. These four pieces turn a development loop into something that can survive crashes and serve production traffic.

</details>

## Real-world reps

- [ ] Review the documentation of one production agent framework (e.g., LangGraph, CrewAI, Anthropic's Managed Agents, or another framework you know). Write down the specific durability guarantees it provides: what is persisted, how often, and how is recovery handled?
- [ ] Design the durability layer for a simple agent. Write out the pieces you would need to build: checkpointing (what and when), resumption (how and when), error handling (retries, backoff), observability (what to log). Estimate how many lines of code this would take to build and test correctly.
- [ ] Tomorrow: Sketch a hypothetical agent task and estimate its deployment requirements. Would a simple loop plus a transcript file be acceptable for your use case, or would you need framework-level durability and observability? Write down the decision and the reasoning.

## Going further

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
