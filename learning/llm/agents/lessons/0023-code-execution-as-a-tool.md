---
title: 23. Code Execution as a Tool
description: Giving an agent a single sandboxed code-execution tool instead of many narrow individual tools
type: lesson
---

# Lesson 23. Code Execution as a Tool

**Mission link:** To decide whether a given task needs an agent at all, you must understand that a single code-execution tool can replace dozens of narrow tools, reducing token cost and latency while requiring robust sandbox enforcement against arbitrary code.
**Primary source:** [Article: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
**Prerequisites:** [Lesson 22](0022-sandboxing-and-approval-gates.md)

## Warm-up

1. ▢ In Lesson 22, we distinguished between a sandbox and an approval gate. What does each one do, and which one would you use to prevent the model from accidentally deleting a file?

<details markdown="1"><summary>Check</summary>

A sandbox is an execution boundary that prevents code from reaching certain resources (like files outside an allowed directory). An approval gate is a human checkpoint before risky actions. To prevent accidental deletion, you would use a sandbox that restricts the tool to only writing within a safe directory tree, so even if the model asks for deletion, the sandbox rejects it. An approval gate would pause and ask for human approval before attempting the deletion, but would not prevent it if approved.

</details>

2. ▢ Lesson 21 introduced the idea of tool discovery at scale: the model can introspect what tools exist rather than loading every definition into context. What problem does this solve?

<details markdown="1"><summary>Check</summary>

When you have hundreds of tools, pre-loading every tool's definition, name, description, and parameter schema into the model's context window exhausts tokens and makes it harder for the model to reason about which tool to call. Tool discovery lets the model request information about available tools on demand or call an introspection endpoint to explore capabilities, so the full list doesn't have to live in the initial context.

</details>

## Know this

### Code execution as an alternative to many narrow tools

Consider a data analysis scenario. Without code execution, you might expose these tools to the model:

- list_files: returns a list of files in a directory
- read_csv: reads a CSV file and returns the first N rows
- compute_mean: calculates the mean of a column
- compute_median: calculates the median of a column
- filter_rows: filters a table by a condition
- sort_by: sorts a table by a column
- write_csv: writes a table back to a file

The model now has to decide which tool to call in which order. It might call read_csv, then filter_rows, then compute_mean: three round trips through the model's loop. Each round trip burns tokens for reasoning about which tool to call next, and each tool definition costs tokens in the initial context window.

Instead, give the model one tool: a sandboxed code interpreter. The model writes a short Python program:

```
import pandas as pd

data = pd.read_csv('data.csv')
filtered = data[data['age'] > 30]
result = filtered['salary'].mean()
print(result)
```

The model runs this once and gets the answer. Advantages: one tool call instead of three, one tool definition instead of seven, and the model can chain operations in a single turn without re-reasoning about which tool to call next.

### Cost and latency benefits

This approach reduces both token cost and latency:

- Token cost: You pay for one tool definition instead of many, and the model's reasoning overhead about which tool to call collapses into ordinary code-writing, which the model already does efficiently.
- Latency: One tool call round trip instead of three or seven means the agent's wall-clock time drops proportionally.

For agents running at scale or with real-time requirements, these savings compound.

### Connection to tool discovery at scale

Lesson 21 introduced the idea that instead of pre-loading every tool definition into context, the model can explore available capabilities dynamically. Code execution is a concrete instantiation of this principle: the model doesn't need every data-transformation tool pre-loaded because it can write code to do the transformation itself. The available capabilities (functions, libraries, system utilities) are discovered when the code runs, not in the initial context.

In some systems, the code-execution tool can itself have a discovery mechanism: a function the model can call to list what libraries are available, what data sources it can reach, or what system commands are available. This layers discovery on top of discovery.

### What a sandbox must enforce against arbitrary code

In Lesson 22, we saw that a sandbox enforces boundaries around what a tool's execution can reach: filesystem paths, network hosts, resource limits. When the tool is "run arbitrary code the model wrote", the sandbox has to enforce these boundaries against code far more expressive and unpredictable than a fixed tool call with a known JSON schema.

The model might write code that:

- Attempts to escape the filesystem boundary by using symbolic links, path traversal tricks (/../..), or calling system utilities like find or ls to probe outside the boundary.
- Writes network code that tries to reach hosts outside the allowlist.
- Spawns infinite loops, recursive functions, or memory-allocating loops that try to exhaust resources.
- Calls functions or methods the code thinks exist but that the harness intends to forbid.

The sandbox must be robust enough to contain all of these. This is harder than sandboxing a fixed tool because the code's surface area is unbounded. A true code-execution sandbox often runs the code in an isolated container or process with seccomp rules, network namespaces, and resource cgroups, not just filesystem permission checks.

### When to use code execution vs. narrow tools

Code execution is powerful but introduces sandbox complexity. You should prefer it when:

- The model needs to combine many small operations that would otherwise require many round trips.
- The operations are algorithmic or data-transformation focused (filtering, aggregation, calculation, format conversion).
- The available capabilities are well-defined and relatively stable.

You should stick to narrow, purpose-built tools when:

- The operation is genuinely high-stakes and benefits from explicit human oversight (sending an email, posting publicly, spending money).
- The operation's safety depends on validating inputs or outputs in domain-specific ways that the harness understands but code doesn't.
- The operation is rare and the token savings of a single tool don't outweigh the sandbox complexity.

Both approaches can coexist: an agent might have a code-execution tool for data wrangling and narrow approval-gated tools for sending emails or publishing results.

## Practice

1. ▢ You have an agent that currently uses seven separate tools for string manipulation: split_string, join_strings, uppercase, lowercase, replace_substring, reverse_string, and trim_whitespace. Could you replace all seven with a single code-execution tool? What would you gain and what would you lose?

<details markdown="1"><summary>Check</summary>

Yes, you could. The model would gain: one tool definition instead of seven, one tool call to perform a complex string operation instead of seven round trips, and the ability to write readable code ("result = text.upper()") instead of guessing at tool names. You would lose: explicit guardrails for each operation (each tool might validate input), and deterministic latency (code execution is now variable depending on what the model writes). For string manipulation, the code-execution approach usually wins because the operations are simple and the harness can enforce a filesystem or resource boundary without domain-specific logic.

</details>

2. ▢ You are designing an agent for a healthcare system that can read patient records and generate diagnostic suggestions. Should you expose this via a code-execution tool where the model writes its own data-access code, or via narrow tools like read_patient_record, filter_by_condition, and compute_risk_score?

<details markdown="1"><summary>Hint</summary>

Consider what "safety" means in a healthcare context. What does the harness need to enforce, and can a general-purpose code sandbox enforce it, or does it need domain-specific logic?

</details>

<details markdown="1"><summary>Check</summary>

Narrow tools are better here. A healthcare system has strict compliance requirements (HIPAA, audit logging, data access control) that the harness probably enforces through domain-specific logic, not filesystem sandboxing. A narrow read_patient_record tool can include authorization checks, audit logging, and data redaction; a code-execution tool cannot easily enforce these, because the harness would have to inspect the code the model wrote, which defeats the purpose of code execution. The high stakes also make approval gates more valuable. Prefer narrow, auditable tools when the operation's safety depends on domain-specific business logic, not filesystem boundaries.

</details>

3. ▢ Which of these statements about code execution is true?

    - a) Code execution is always faster than using separate tools because it reduces round trips, even for simple single operations.
    - b) Code execution reduces token cost because one tool definition replaces many, but only saves latency if the model chains multiple operations.
    - c) Code execution eliminates the need for sandboxes because the code is trusted.
    - d) Code execution requires no approval gates because the harness can inspect the code before it runs.

<details markdown="1"><summary>Check</summary>

**b)** Code execution reduces token cost because one tool definition replaces many, but only saves latency if the model chains multiple operations. Token savings are real (one definition instead of many). Latency savings only matter if the model is doing multiple operations that would otherwise require multiple round trips; for a single operation, the time is similar or worse. Option a is wrong (single operations don't benefit). Option c is wrong (code execution needs robust sandboxes because the code is arbitrary). Option d is wrong (approval gates still make sense for high-stakes operations, and pre-inspection doesn't prevent all mistakes).

</details>

4. ▢ Explain why the sandbox's job becomes harder when the tool is "code execution" instead of a specific tool like "delete_file". What is one concrete scenario where this difficulty matters?

<details markdown="1"><summary>Check</summary>

With a specific tool, the harness knows in advance what the tool will do and can enforce a boundary at that specific point (the delete_file tool can only touch files in a safe directory). With code execution, the harness doesn't know what the code will do until it runs; the code might call system utilities, open network sockets, or use language features the harness doesn't expect. One concrete scenario: the model writes code that calls subprocess.Popen to run a shell command like "ls /../.." to probe the filesystem beyond the intended boundary. A filesystem-permission sandbox alone won't stop this; the sandbox needs seccomp rules or a container to prevent arbitrary system calls. This is why code-execution sandboxes are typically more complex than narrow-tool sandboxes.

</details>

5. ▢ Your agent uses code execution to analyze data. The model writes code that should read from a CSV file, but instead it writes code that tries to download a file from the internet. The sandbox enforces no network access. What happens, and is this a sandbox failure?

<details markdown="1"><summary>Check</summary>

The code runs, attempts the network call, and the network operation is rejected or blocks. This is not a sandbox failure; it is the sandbox working as intended. The sandbox's job is to prevent the code from reaching resources outside its boundary, not to ensure the code is correct or does what the model intended. A sandbox failure would be if the network call succeeded despite the no-network rule. The model's mistake (writing the wrong code) is separate from the harness's job (enforcing boundaries).

</details>

## Real-world reps

- [ ] List the tools your own work or a familiar system uses. Identify a cluster of three or more closely related tools and sketch how they could be replaced with a code-execution tool. What would you need to be confident in the sandbox to make this change?
- [ ] Write a simple data-analysis program (filtering a table, computing an aggregate, sorting). Imagine you are the model. How many round trips through a tool-calling loop would this take with separate tools, and how many with code execution?
- [ ] Tomorrow: Review the "Code Execution with MCP" article and identify one design choice in the sandbox (resource limit, filesystem boundary, network restriction) and explain why that particular boundary matters for the article's use case.

## Going further

- [Article: "Code Execution with MCP", Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
