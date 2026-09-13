---
title: 32. Least Privilege and the Confused Deputy
description: How to scope agent capabilities so that prompt injection causes contained damage instead of catastrophic breach
type: lesson
---

# Lesson 32. Least Privilege and the Confused Deputy

**Mission link:** Design the access boundaries for each agent tool so that untrusted content can trick the agent but cannot trick it into misusing capabilities it should never have had.
**Primary source:** [Reference: "OWASP Top 10 for LLM Applications", OWASP GenAI Security Project](https://genai.owasp.org/llm-top-10/)
**Prerequisites:** [Lesson 31](0031-prompt-injection-and-the-lethal-trifecta.md), [Sandbox](../GLOSSARY.md)

## Warm-up

1. ▢ Name the three conditions of the lethal trifecta from Lesson 31.

<details markdown="1"><summary>Check</summary>

Access to private data, exposure to untrusted content, and ability to communicate externally. Remove any one and the attack fails.

</details>

2. ▢ In Lesson 31, you designed a tool to avoid a prompt injection attack by breaking one trifecta condition. If you had broken the external communication condition, describe what that would look like in practice.

<details markdown="1"><summary>Check</summary>

The tool would either not be able to send information anywhere, or only to a channel the attacker cannot reach. For example, a draft_email tool that only stores emails locally instead of sending them, or a tool that can only write to a staging table that requires manual review before data is shared.

</details>

## Know this

### Least privilege: scope each tool to exactly what it needs

Least privilege is a security principle: each tool should have access to only the specific resource or action it actually needs, not broad access "just in case it might be useful later." For an agent, this means designing each tool's sandbox boundary with narrow permission.

Examples:

- A tool that reads today's schedule should only read from the calendar file, not the entire filesystem
- A tool that looks up a customer's order should only query that customer's orders, not all company orders
- A tool that sends a receipt email should only be able to send from one fixed address, not the entire mailbox
- A tool that edits a configuration file should only edit that one file, not arbitrary files in the config directory

The principle applies to credentials too. If a tool needs to authenticate with an external service, it should use a credential scoped to that service and that action, not a broad administrator account.

Why does this matter for agents? Because broad access is exactly the thing that makes an exploit costly to the organization. When an agent is tricked by an injection into calling a tool it has access to, the consequences depend on what that tool can actually reach.

### The confused deputy pattern: legitimate authority, misused

The confused deputy is a classic security pattern, first named in the 1980s, that maps directly onto agents. A confused deputy is a program that has legitimate, broad authority and gets tricked into misusing that authority on an attacker's behalf. The program is not compromised in the sense of running malicious code; it is doing exactly what its legitimate tools allow, just on behalf of instructions that were never the user's.

An agent with a confused deputy vulnerability looks like this:

1. The agent has a broad tool: send_email can send from any address in the company mailbox
2. The agent reads untrusted content: a calendar invite with an injected instruction
3. The instruction asks the agent to forward a confidential email thread to an external address
4. The agent calls send_email with the attacker's parameters
5. The tool executes the call because it is a legitimate send_email call with valid parameters. The tool does not know that the request originated from an injection, not the user's actual intent.

The email is now exfiltrated, not because the model was "hacked," but because you gave an agent a broad capability and did not scope it to a narrow task.

The fix is not to prompt the model harder. The fix is to design the tool narrowly: instead of send_email for the whole mailbox, design a tool called send_receipt that can only send to customer email addresses with a fixed template. Now an injection can still trick the model into calling send_receipt, but that call is constrained to what send_receipt is allowed to do.

### MCP supply chain: trust is transitive

Lesson 20-21 covered the Model Context Protocol (MCP) and how an agent connects to MCP servers to access tools. From a security angle, connecting to an MCP server means extending your trust boundary to include whoever operates that server.

A malicious or compromised MCP server can:

- Misrepresent tool descriptions to make harmful calls sound benign
- Return misleading data in tool results, which the agent will then reason about
- Observe every tool call the agent makes and every piece of context it sends

When your harness connects to a third-party MCP server, you are trusting that server operator as much as you trust your own code. If the server is compromised or operated by an adversary, it becomes another channel for injection.

The defense is the same as for any supply chain risk: only connect to servers you trust, and scope the connection. For example:

- Do not give an agent access to all available MCP servers; only connect to the specific servers it needs
- Use authentication and encryption for MCP connections
- Audit the tool descriptions an MCP server provides and understand what access you are granting
- Assume that the data you send to an MCP tool could become public or be misused

MCP servers are not uniquely risky; they are just another tool. The principle is the same: scope the access.

### Putting it together: permission boundaries per tool, per task

The design principle tying these lessons together is that a permission boundary should be scoped deliberately, per tool and per task, rather than a single broad credential the whole agent shares.

When you design an agent:

1. List each tool the agent needs
2. For each tool, ask: what is the minimum access this tool requires to fulfill its purpose?
3. Create a sandbox boundary for that tool that grants exactly that access, no more
4. If a tool needs to authenticate (with a database, an API, a filesystem), create a credential scoped to that tool and that access level, not a credential that can reach anything

A narrowly scoped tool is the concrete thing that turns "the model was tricked by an injection" from a catastrophic compromise into a contained, low-consequence mistake. The agent reads the injection, the model understands it, the model calls the injected tool, and the tool refuses to execute the requested action because the action is outside its scope.

## Practice

1. ▢ You are designing a tool for an agent that manages user accounts. The tool needs to update a user's email address in the company database. Your first draft gives it this credential: a database account with UPDATE permission on the entire users table.

Why is this over-scoped, and what would be a better design?

<details markdown="1"><summary>Check</summary>

The credential grants UPDATE permission on the entire table, which means the tool could update any user's information, not just the specific email address of the specific user being managed. A better design would create a stored procedure on the database that accepts only the user ID and new email, and grants the tool's credential permission to execute only that procedure. This way, even if an injection tricks the agent into calling the tool with unexpected parameters, the database will refuse to execute anything outside the procedure's scope.

</details>

2. ▢ An agent has access to a send_email tool scoped to send only from support@company.com and only to email addresses matching the pattern *@customer-*.com. An injection tries to trick it into sending a message to attacker@evil.com. What stops the attack?

<details markdown="1"><summary>Hint</summary>

The tool itself enforces the scope. Think about where this check happens and why no prompt instruction is involved.

</details>

<details markdown="1"><summary>Check</summary>

The tool's validation, which runs in the harness before the message is sent. The tool validates the recipient against its allowed pattern and refuses to send because attacker@evil.com does not match. The injection succeeded in changing the agent's behavior (the agent intended to send), but it failed because the tool's permission boundary prevented the harmful action. This is a tool-level control, not a prompting-level control, so it is reliable.

</details>

3. ▢ Your organization provides an MCP server that exposes company calendar events. You discover that a third-party company has built an MCP client that connects to your server to help manage meetings. Which of these statements is true?

    - a) This is safe as long as your MCP server only returns public calendar data
    - b) The third-party client now effectively has read access to the calendar data that your server returns
    - c) You should use encryption between your server and the client to guarantee that even your server operators cannot see the data
    - d) The third-party company cannot misuse the data because it is only calendar events, not user credentials

<details markdown="1"><summary>Check</summary>

**b)** The third-party client, and anyone operating it, can see and potentially misuse all calendar data that the server returns. Public data is still data; even if the calendar events are not secret, the third-party operator now has visibility into your organization's schedule, which could be used for corporate espionage or social engineering. Encryption (option c) would protect the data in transit, but would not prevent the client operator from seeing it. The scope of access (public vs private) does not change the security implication: you have extended your trust boundary to include the third-party operator. This is the MCP supply chain risk.

</details>

4. ▢ You are designing a tool for an agent that processes customer support tickets. The tool needs to send an email response to a customer. Describe a least-privilege design that would prevent a confused deputy attack where an injection tricks the agent into forwarding a confidential internal email thread to a customer.

<details markdown="1"><summary>Check</summary>

Instead of a generic send_email tool, design a tool called send_support_response that takes only two parameters: the ticket ID and the response text. The tool looks up the customer email address from the ticket ID, validates that the response text does not exceed a reasonable length, and sends only the response (not any attachments, not any other emails). The tool's credential only has permission to send from the support address and only to customer email addresses linked to valid tickets. Now an injection can trick the agent into calling send_support_response, but the call is constrained by the tool's scope. The agent cannot forward internal emails, cannot send to arbitrary addresses, and cannot send anything that is not a support response because the tool does not provide a way to do those things.

</details>

## Real-world reps

- [ ] Take a tool you have designed or use frequently. Map its current permissions. Write down one permission it has that exceeds what it strictly needs for its primary purpose, and one way to remove it.
- [ ] Choose an MCP server you would be willing to connect an agent to. Research or contact the operator and understand: what data does the server see, how is it used, how is it protected, who has access to the logs? Write down your confidence level and any residual risk.
- [ ] Tomorrow: Design a tool that implements least privilege deliberately by refusing a plausible but out-of-scope request. Write a specification that names the request it would receive during a confused deputy attack and explains why the tool design prevents it from succeeding.

## Going further

- [Reference: "OWASP Top 10 for LLM Applications", OWASP GenAI Security Project](https://genai.owasp.org/llm-top-10/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
