---
title: 36. When Not to Build an Agent
description: The judgment to decide whether a task actually needs an agent, and the discipline to say no when one is not worth its cost
type: lesson
---

# Lesson 36. When Not to Build an Agent

**Mission link:** Build the judgment to decide whether a given task needs an agent at all rather than a fixed workflow, and to defend that call against organizational pressure and the allure of agent-shaped solutions.
**Primary source:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Prerequisites:** [Lesson 35](0035-durability-and-what-frameworks-buy.md), [Autonomy spectrum](../GLOSSARY.md)

## Warm-up

1. ▢ Recall from Lesson 2: what is the defining difference between a workflow and an agent in terms of control flow?

<details markdown="1"><summary>Check</summary>

A workflow has a path the developer fixed in advance; all branches and sequences are wired by the developer. An agent has control flow decided at run time by the model, including whether to continue or stop.

</details>

2. ▢ Recall from Lesson 2: on the autonomy spectrum, what concrete test can you apply to decide whether a task's branch count is actually enumerable?

<details markdown="1"><summary>Check</summary>

If you can list all the distinct paths a workflow would need to cover the task, the branch count is enumerable and a workflow may be sufficient. If new paths arrive faster than you can wire them, or the right path genuinely depends on information only available mid-task, the branch count is effectively unbounded and an agent is more defensible.

</details>

## Know this

### Why the decision is harder than Lesson 2 made it look

Lesson 2 taught the autonomy spectrum as a clean technical choice: is the task's shape known or unknown, enumerable or unbounded? In practice, that choice sits under real pressure.

A product manager has seen a compelling demo of an agent solving a complex problem and asks, "Can we build that for our product?" An organization feels behind on AI and wants to "add agents" to its platform. A stakeholder points to a task and says, "This looks agent-worthy," without checking whether the simpler alternative was actually tried. A workflow solving the same problem is less exciting to pitch, even when the workflow is the better engineering call.

The role of this lesson is not to re-teach Lesson 2's framework; the framework is right. The role is to name why applying it correctly is a judgment call under pressure, and to give you concrete red flags that tell you an agent is unjustified, each one tied back to a specific earlier lesson so you can spot the pattern when you see it in a proposal or architecture review.

### Red flag 1: Nobody tried the simpler workflow first

The strongest red flag is this: a stakeholder or proposal says an agent is needed, but nobody has actually built the workflow alternative to test that claim.

Lesson 2 defends each choice by naming what the option you reject would have cost. That defense only works if you actually tested the rejected option. If a proposal claims "an agent is necessary" without showing a workflow attempt and explaining why the workflow failed, the claim has not been tested against the alternative. You are being asked to accept an increase in complexity without evidence that the complexity is needed.

What this looks like in practice: a proposal says, "We need an agent to handle these customer support tickets because they branch into forty distinct categories." Without a workflow attempt, you do not know whether forty categories is actually too many to wire, or whether the proposal's author just has not tried yet. After building a workflow router and testing it on real tickets, you might find forty categories is manageable, or you might find the workflow's accuracy suffers because a rule-based classifier cannot distinguish between two categories on edge cases. Testing the workflow against the same task tells you what you are really buying by switching to an agent.

The discipline: before committing to an agent, ask "what workflow was tried, and why did it fail?" If the answer is "none was," insist on building one first. You might learn the workflow solves the problem well enough, or you might learn the workflow fails in specific ways that an agent actually would improve.

### Red flag 2: The failure mode is reliability, not capacity

Lesson 2 said an agent earns its unpredictability when you need flexibility. But flexibility has costs in reliability that stages 11-12 of this track spent lessons naming: grounding errors in computer-use agents (Lesson 25), cascading tool errors where one tool's failure brings down the next step (Lesson 28), context poisoning where a false claim enters the transcript and is silently treated as fact by every later turn (Lesson 27).

If a task's failure mode is one of these reliability classes, and the task is something where a fixed, well-tested workflow would simply never make that class of mistake, then an agent buys unpredictability at the cost of a reliability problem that did not exist before.

Example: a document classification system that must route documents to exactly one of five known categories. An agent can route flexibly and even re-categorize if it reads something in the document that changes its mind. But if the task is to classify a financial document with a fixed, auditable process, and the penalty for a misclassification is regulatory violation, then an agent's flexibility is not worth the risk of context poisoning making the agent second-guess its own prior reasoning and send a document to the wrong category. A workflow with a single routing decision per document, auditable step by step, costs predictability but gains reliability where it matters.

The discipline: for tasks where failure is expensive or where reliability is non-negotiable, name what reliability problem an agent would introduce that a workflow would not have. If that problem is severe enough, the workflow is the better choice even if it feels less sophisticated.

### Red flag 3: The lethal trifecta is all present with no benefit

Lesson 31 named the lethal trifecta: access to private data, exposure to untrusted content, and ability to communicate externally. An agent has all three conditions when it reads untrusted input and has tools that can misuse data or exfiltrate it.

Removing any one condition breaks the attack. But an agent that has all three conditions is exploitable even if an injection only succeeds sometimes. Lesson 32 taught that the defense is not to prompt the model harder, but to narrow the tool access.

If a proposed agent has all three trifecta conditions and the task does not benefit from the agent's unpredictability, then you are buying exploitability for no gain. A narrower workflow-based integration, or a tool set that deliberately lacks one of the three conditions, accomplishes the same goal without assembling the exposure.

Example: a content recommendation engine reads user profiles and external content sources to suggest items. If the engine is implemented as an agent with tools to fetch external content, query user data, and send recommendations to a messaging system, it has all three trifecta conditions. But if the engine's job is to select from a fixed set of recommendation types based on simple rules (if user has viewed A, recommend B), then a workflow does the job without exposing the user data and recommendation system to a prompt injection channel that did not exist before.

The discipline: for each trifecta condition, ask whether the task actually needs it. If an agent has all three for a task that does not require the agent's flexibility, redesign the tool set to deliberately remove at least one condition. The system will be less impressive as a demo, but it will be less exploitable and more reliable.

### Red flag 4: The token cost exceeds the task's value

Lesson 33 taught token amplification and cost per completed task, including the multi-agent multiplier. Lesson 19 showed that an orchestrator-worker system costs several times more in tokens than a single agent solving the same problem.

A concrete question: estimate the real cost per completed task, including retries, multi-agent coordination if applicable, and any token amplification from context length or caching overhead. Is that cost acceptable for what the task produces?

This question is often not asked until it is too late. A team builds an agent, launches it, and discovers the cost per task exceeds what the task is worth in business value. The agent works, but operating it is too expensive.

The discipline: before committing to an agent (especially a multi-agent system), estimate the token cost per completed task using actual turns or trajectories from a prototype. Run that estimate against the task's value. If the token cost exceeds the value, the agent is not justified, no matter how elegant the system is.

### Putting it together: ask these four questions before committing to an agent

1. Was a simpler workflow actually attempted and found insufficient?
2. Is the task's failure mode one where an agent introduces a new reliability problem that a workflow would not have?
3. Does the agent have all three trifecta conditions, and is that exposure necessary for the task?
4. Is the token cost per completed task acceptable for what the task produces?

If the answer to any of these is "no" or "we do not know," the agent may not be justified. Saying no to an agent is not failure; it is discipline. You are choosing predictability, reliability, security, or cost over the flexibility an agent would buy. That is a defensible choice, and it is the choice that lets you say yes confidently when an agent actually is justified.

## Practice

1. ▢ A product team proposes building an agent to summarize customer support tickets for internal reporting. The agent would read the ticket (untrusted user content), access the company's customer database to look up context, and post summaries to a Slack channel. A workflow alternative would have a human manually sort tickets into categories and then run a template-based summarizer on each category. The team says "an agent is more efficient." Without running the workflow, what question should you ask first?

<details markdown="1"><summary>Check</summary>

Ask them to actually build and test the workflow on real tickets. Measure how much faster the agent is, and whether the efficiency gain justifies the cost in token consumption and the exposure of the lethal trifecta (the agent reads untrusted content, accesses private customer data, and sends external messages). If the workflow is 90 percent as good and costs 10 percent as much, the workflow wins. Without testing the workflow, the claim "an agent is more efficient" is untested.

</details>

2. ▢ You are reviewing a proposal for an agent that helps analysts debug failing tests in a large codebase. The agent would have access to repository code, test results, and logs. It would call tools to search the code, run individual tests, and file bug reports. The proposal says, "An agent can explore the codebase more flexibly than a script." What reliability concern does Lesson 27 teach that is relevant to evaluating this proposal?

<details markdown="1"><summary>Hint</summary>

Think about what happens when an agent is reading the outputs of tool calls and building a model of what the code says and does. What error pattern is unique to agents?

</details>

<details markdown="1"><summary>Check</summary>

Context poisoning (Lesson 27). If the agent misinterprets a log or a code snippet and builds a false claim into its model of the bug (e.g., "this function returns None"), every later reasoning step will treat that false claim as established fact. A script with a fixed path will not second-guess its own output this way. An agent's flexibility to change its mind based on new evidence is an asset, but it also opens the door to silent confidence in wrong conclusions carried from one step to the next. Evaluate whether the task's failure mode (debugging a test) is more harmed by flexibility (better at finding novel bugs) or by the risk of context poisoning sending the agent down a false path.

</details>

3. ▢ Which of these scenarios most clearly indicates a proposed agent is unjustified?

    - a) The task can be solved by a workflow, but the workflow would require wiring a new branch every time a new document type arrives
    - b) The task has been tried as a workflow and failed to meet accuracy targets, but a prototype agent tested on the same dataset performs better
    - c) The task has never been tried as a workflow, but a stakeholder insists an agent is necessary because an AI demo they saw was impressive
    - d) The task requires reading untrusted content and accessing private data, but the agent's tool set deliberately lacks external communication

<details markdown="1"><summary>Check</summary>

**c)** The scenario where a task has never been tried as a workflow, and the proposal is driven by excitement about a demo rather than evidence that the simpler alternative fails. Scenario (a) describes a task where an agent buys ongoing flexibility; the branch count is growing, so an agent is justified. Scenario (b) shows the workflow was tested and failed, making the agent's better performance evidence in its favor. Scenario (d) describes a reasoned architecture that removes one trifecta condition, which is a justified design choice. Only (c) has no basis in testing.

</details>

4. ▢ You estimate an agent for a task would cost 5,000 tokens per completed run, including retries, and the task produces business value equivalent to 2,000 tokens' worth of compute at current market rates. Defend a choice between building the agent or choosing an alternative, naming what you are accepting by making that choice.

<details markdown="1"><summary>Check</summary>

The alternative (a workflow, a simpler system, or leaving the task manual) is justified. The agent costs 2.5x its value, which means every run costs the business more in compute than it returns in value. Building the agent anyway is defensible only if you expect the token cost to drop (cheaper models, caching strategies, faster convergence on repeated tasks), or if the business value is higher than estimated. If neither is true, the discipline is to say no. The cost you are accepting is losing the flexibility an agent would provide, but you are gaining predictability and cost-efficiency. That is the right trade-off at these numbers.

</details>

## Real-world reps

- [ ] Take a task currently solved by an agent in a system you know. Estimate the token cost per completed task and the business value of each completion. Is the ratio acceptable? If not, what would have to change to make an agent justified?
- [ ] Find a proposal (internal, or an article describing a system) that advocates for an agent. Trace whether it answers all four red-flag questions: was a workflow tried, is the failure mode reliability-sensitive, are all three trifecta conditions necessary, and is the cost acceptable? Write down which red flags the proposal addresses and which it leaves open.
- [ ] Tomorrow: Imagine a product feature you would build as an agent. Now design it as a workflow instead. Compare them: what can the workflow not do that the agent can? How much harder is the workflow to build? Do the gains justify the added complexity? Write down your honest assessment.

## Going further

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
