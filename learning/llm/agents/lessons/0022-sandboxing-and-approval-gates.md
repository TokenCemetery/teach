---
title: 22. Sandboxing and Approval Gates
description: Execution boundaries and human checkpoints that protect against model mistakes
type: lesson
---

# Lesson 22. Sandboxing and Approval Gates

**Mission link:** To decide what the agent may do unattended, you need to understand the two complementary mechanisms that protect against mistakes: sandboxes enforce what the code can reach regardless of what the model asks, and approval gates add a human checkpoint before high-stakes actions.
**Primary source:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Prerequisites:** [Lesson 21](0021-provider-formats-and-discovery-at-scale.md), [Harness](../GLOSSARY.md)

## Warm-up

1. ▢ What is the difference between a client tool and a server tool, in terms of where the code runs and who controls it?

<details markdown="1"><summary>Check</summary>

A client tool runs in the harness's own code, so you control its execution entirely. A server tool runs on the provider's infrastructure on the harness's behalf, so the provider controls the execution boundary. This matters for security because a client tool's behavior depends on your code, while a server tool's behavior depends on what the provider allows.

</details>

2. ▢ In Lesson 21, we learned that instead of pre-loading every tool definition into context, the model can discover and call tools dynamically. Name one benefit of this approach and one cost it introduces.

<details markdown="1"><summary>Check</summary>

Benefit: the model's context doesn't explode with hundreds of tool definitions, so it can reason more clearly and tool definitions can be kept small or fetched on demand. Cost: the model now has to call a discovery or introspection tool first before it knows what's available, adding a round trip, or it calls a tool it guesses exists and fails if it doesn't, requiring error handling and retries.

</details>

## Know this

### A model's judgment is not a security boundary

You might hope: "The model will be smart about what it does with access I give it. I can rely on the model deciding not to delete production data or send emails without permission."

This hope breaks in several ways. A model can be wrong: it can misunderstand the consequences of a tool call. A model can be manipulated by content it reads: if a preview of a file or a user message contains adversarial text designed to trick the model, that text can influence the model's reasoning. A model can simply make a mistake: reasoning can fail at scale, especially in high-branching scenarios or under time pressure. For these reasons, whatever your harness actually allows a tool to touch (which files on disk, which network hosts, which commands to run) has to be enforced by code, not by hoping the model behaves correctly.

This is why the harness, not the model, is the security boundary.

### What a sandbox is

A sandbox is an execution boundary that the harness enforces around what a tool's code can reach, regardless of what arguments the model sent. The model's instructions are never themselves a security property.

Common sandbox boundaries include:

- **Filesystem boundary**: The tool can only read or write files within a specific directory tree (for example, `/home/user/work` but not `/etc` or `/home/other_user`). Even if the model asks the tool to access a path outside this tree, the sandbox rejects it at runtime.
- **Network isolation**: The tool has no network access at all, or it can only reach a whitelist of specific hosts. The model cannot convince the harness to let it reach arbitrary domains.
- **Resource limits**: CPU time, memory, and wall-clock time are capped. If the model's code gets stuck in an infinite loop, the sandbox terminates it rather than consuming all resources.
- **Process isolation**: The tool runs in a separate process or container with reduced privileges, so it cannot affect the harness or access system resources it wasn't explicitly granted.

The key insight is that these boundaries are enforced at execution time, in the harness code, not at the language level. A tool cannot escape a sandbox by writing clever code. The sandbox is the rule the harness applies, not a feature the tool respects.

### What an approval gate is

An approval gate is a complementary mechanism: before executing a tool call in a risky category, the harness pauses and waits for a human to review the specific call and approve or reject it.

Approval gates apply to actions with these properties:

- Irreversible or hard to undo: deleting files, sending emails, making financial transactions, publishing to the internet.
- High consequence if wrong: the stakes are real money, real damage, or real privacy exposure.
- Genuinely hard to predict: the model's decision is reasonable but not obviously correct, so human judgment is worth adding.

A gate pauses the agent loop and surfaces the pending tool call (with its arguments and expected effect) to a human, waits for approval or rejection, then resumes or stops the loop accordingly.

### Sandboxes and approval gates are complementary, not alternatives

These are two different protections that work together:

- A sandbox limits what damage any call can do, even if approved or automatically executed. If a call somehow goes wrong, the sandbox contains the blast radius. "It runs in a restricted environment" is always true.
- An approval gate adds a human decision point for the highest-stakes calls. It doesn't prevent all damage; it just ensures that the calls most likely to cause regret get human eyes first.

If you sandbox every call but never gate anything, an undetected model mistake can still cause harm within the sandbox's boundaries. If you gate every single tool call, the agent stops being autonomous and becomes a human doing all the work with extra steps, defeating the point of automation.

The right balance: gate a narrow class of genuinely high-stakes actions (delete, send, publish, spend) where human judgment is worth the latency cost, and sandbox everything so that anything outside that gate cannot escape its boundaries even if something goes wrong.

## Practice

1. ▢ You are building an agent that can read and summarize documents from a shared repository. The repository has 10,000 files, and some of them contain sensitive customer data that the agent should not access. You want to add a client tool that lets the agent read files. What sandbox boundary should you enforce, and why?

<details markdown="1"><summary>Check</summary>

You should enforce a filesystem boundary: the tool can only read files within a specific approved directory tree (for example, all files in the "public_docs" folder but nothing in the "confidential" folder). This boundary is checked at runtime when the model calls the tool; even if the model asks the tool to read a path in the confidential folder, the sandbox rejects it. This protects against the model being tricked by a file's content or making a reasoning mistake about what is safe to read. The model's judgment ("this looks public") is not the boundary; the code is.

</details>

2. ▢ Your agent can write code and execute it in a sandboxed Python interpreter. The sandbox limits CPU to 30 seconds and memory to 1 GB. The model writes a program that starts an infinite loop. Will the sandbox stop it?

<details markdown="1"><summary>Hint</summary>

Think about what happens when the CPU limit is exceeded while the code is running, and whether the harness can detect and enforce that limit.

</details>

<details markdown="1"><summary>Check</summary>

Yes, the sandbox will stop it. When the 30-second CPU limit is reached, the harness terminates the process. The model's code never runs forever; the sandbox enforces the resource limit at execution time, not at parse or compile time. This is one reason resource limits are essential in a sandbox: they prevent even well-intentioned code from consuming all resources.

</details>

3. ▢ You are designing an agent that can send emails on behalf of a user. Which of these is a good reason to add an approval gate before the agent sends an email?

    - a) The model might write a grammatically incorrect subject line.
    - b) The model might send an email to the wrong recipient or with the wrong content, and once sent, the email cannot be unsent.
    - c) The model might slow down the email server.
    - d) The model might run out of ideas for what email to send next.

<details markdown="1"><summary>Check</summary>

**b)** The model might send an email to the wrong recipient or with the wrong content, and once sent, the email cannot be unsent. This is an irreversible, high-consequence action where human judgment is worth the latency cost. Option a is not high-consequence enough (the model can draft well). Option c is not the model's mistake (it's about system load). Option d doesn't make sense (the model stops when asked to).

</details>

4. ▢ Explain why a sandbox cannot prevent all mistakes but can still be essential. Give an example.

<details markdown="1"><summary>Check</summary>

A sandbox enforces boundaries on what resources the code can reach, not on what mistakes the code makes. For example, a sandbox might prevent a tool from writing to `/etc/passwd` by rejecting the write at runtime, but it cannot prevent the model from writing the wrong content to an approved file, like overwriting a config file in `/home/user/config/` with invalid syntax. The sandbox's job is to contain damage, not to ensure correctness. Approval gates handle the high-stakes decisions that need human judgment; sandboxes handle the execution boundaries that prevent the blast radius from expanding beyond control.

</details>

## Real-world reps

- [ ] Draw a diagram of a tool call: show the model, the harness, the tool code, and the sandbox around it. Label what the model controls (its reasoning and tool choice) and what the harness controls (the boundary).
- [ ] List three tools in your own work or a system you use daily. For each one, identify one risky action (if any) that would benefit from an approval gate, and one sandbox boundary that would make sense.
- [ ] Tomorrow: Read the "Building Effective Agents" article and note one concrete example of a sandbox or gate. Explain in a sentence why that design choice matters.

## Going further

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
