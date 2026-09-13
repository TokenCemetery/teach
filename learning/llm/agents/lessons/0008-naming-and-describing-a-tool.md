---
title: 8. Naming and Describing a Tool
description: A tool's name and description are what the model reads to decide when and how to call it
type: lesson
---

# Lesson 8. Naming and Describing a Tool

**Mission link:** Designing an agent's tool surface (names, descriptions, return shapes, and the permission boundary that decides what it may do unattended) starts with understanding that names and descriptions are not API documentation for a human: they are prompt surface the model reads to decide when and how to call a tool.
**Primary source:** [Article: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
**Prerequisites:** [Lesson 7](0007-the-transcript-as-state.md), [Tool](../GLOSSARY.md)

## Warm-up

1. ▢ From Lesson 7: How does the model "remember" what happened on a previous turn of the agent loop?

<details markdown="1"><summary>Check</summary>

It does not remember independently. The harness re-sends the full transcript on every call, so what looks like memory is really the model re-reading everything it was shown before.

</details>

2. ▢ From Lesson 7: Why is the transcript the agent's whole state, and not some other data structure the harness holds separately?

<details markdown="1"><summary>Check</summary>

Because the model only ever sees the transcript. Any fact the harness knows but never appends to it is invisible to the model, no matter what else the harness tracks internally.

</details>

## Know this

### A Tool Description Is Not API Documentation

A mistake every builder makes once: write a tool description the way you would write a REST endpoint docstring.

```
Bad:
name: fetch_user
description: Fetches user data
```

This is too terse for a model deciding among several tools. The model has no context for when to use `fetch_user` versus `get_user` versus `lookup_user`. It does not know what data comes back or what goes in. It cannot reason about whether to call it now or later. When the model sees three tools and no clear guidance, it guesses, and guesses wrong more often than a human would.

Here is the same tool described for a model:

```
Better:
name: fetch_user
description: Look up a user profile by their numeric ID. Returns the user's name, email, account status, and the current version number of their profile. Use this before calling update_user, since update_user requires you to pass the profile's current version number to prevent write conflicts. Returns null if the user ID does not exist.
```

Now the model can see the full picture: when to call it (before update_user), what it needs (a numeric ID), and what it gives back (enough information to decide the next step). This description serves the model's decision-making, not a human reading API docs.

The difference is this: a REST docstring tells a human programmer how to use a tool. A tool description in an agent prompt tells a model when and why to call a tool, what to pass, and what result to expect. The model does not have a manual; your description is its only guide.

### Naming Distinctly From Other Tools

The model picks among tools by reading their names and descriptions with no other signal. If two tools sound similar, the model will call the wrong one or call both to be safe.

```
Bad:
- name: list_files
  description: Lists files in a directory
- name: list_file_contents
  description: Lists the contents of a file
```

The model might confuse these or call both when it only needs one. The names are too close.

```
Better:
- name: list_directory
  description: List all files and subdirectories in a directory. Shows names and file sizes. Does not show file contents.
- name: read_file
  description: Read the complete contents of a single file. Returns text as a string.
```

Now the names are distinct (list_directory versus read_file) and the descriptions make clear what each does and does not do. The model will pick the right one.

The rule: a tool's name should say what it does in a way that cannot be confused with any other tool in the same tool set. If you have multiple search tools, do not call them all `search`. Call them `search_documentation`, `search_code`, `search_logs`.

### Parameter Descriptions Matter the Same Way

The top-level tool description gets the most attention, but parameter descriptions are just as important for correctness.

```
Bad:
name: create_issue
description: Creates a GitHub issue
parameters:
  - name: title
    type: string
    description: Issue title
  - name: body
    type: string
    description: Issue body
```

The model does not know what format the title should be, how long it can be, whether it should be a question or a statement. The body is even worse: is it Markdown? Plain text? How detailed? Does the model describe the problem or the solution?

```
Better:
name: create_issue
description: Create a new issue in the repository
parameters:
  - name: title
    type: string
    description: A one-line summary of the problem or feature request. Be specific and actionable. Examples: "Handle null config values in startup" or "Add support for JSON output format".
  - name: body
    type: string
    description: Detailed description in Markdown. Include what you tried, what failed, and what you expect to happen. If it is a feature request, explain why it matters. If it is a bug, include steps to reproduce.
```

Now the model knows what kind of title to write and what level of detail to include in the body. It will produce better results.

### A Common Failure: Similar Tools Confusing the Model

The worst case is when two tools are similar enough that the model cannot tell them apart, even with descriptions.

```
Very bad:
- name: update_user
  description: Update user information
- name: change_user
  description: Modify user data
```

These names and descriptions say almost the same thing. The model might call both, or call the wrong one, or waste time asking. You have given it no way to choose.

The fix is to make the names and descriptions so different that only one makes sense for the task at hand:

```
Better:
- name: update_user_profile
  description: Change a user's displayed name, email, or profile picture. Requires the profile version number to prevent conflicts.
- name: update_user_permissions
  description: Grant or revoke access roles for a user, such as admin, editor, or viewer. Only callable by the current account's admin.
```

Now the model can see that the first tool is for personal information and the second is for access control. It will pick the right one.

## Practice

1. ▢ You have two tools: `send_email` and `send_notification`. The model sometimes calls both when it only needs one. Write one sentence for each tool that makes it clear to the model which one to use and when.

<details markdown="1"><summary>Check</summary>

Possible answers: `send_email` might be "Send an email message to an email address. Use this for messages longer than a few lines or when you need to include attachments or formatted text." `send_notification` might be "Send a brief in-app notification to a user. Use this for short status updates or alerts that do not require the user to leave the application." The key is that the description tells the model what kind of message each tool expects, so it can choose correctly.

</details>

2. ▢ Your `get_user` tool returns all fields in a user record: id, name, email, phone, address, company, biography, preferences, subscription tier, and ten more. A parameter description should guide the model on what to pass. What should you NOT put in the description?

<details markdown="1"><summary>Hint</summary>

Think about what the model needs to know to call the tool correctly, versus what is nice to know but not required for the call itself.

</details>

<details markdown="1"><summary>Check</summary>

You should NOT list every field the tool returns. The tool's description says what the model gets back; the parameter description says what the model must provide to call it. For a `user_id` parameter, the description should say something like "The numeric ID of the user. If you do not have the ID, call search_users first." Do not list what fields come back in the parameter description; that goes in the top-level tool description.

</details>

3. ▢ Which of the following is the best reason to write detailed descriptions for a tool's parameters?

    - a) To comply with API documentation standards
    - b) To help human engineers who read the code later
    - c) To help the model decide what value to pass and when to call the tool at all
    - d) To reduce the number of tool calls the user needs to make

<details markdown="1"><summary>Check</summary>

**c)** To help the model decide what value to pass and when to call the tool at all. The model reads parameter descriptions to understand what arguments a tool expects and what will happen if it passes the wrong value. (a) is irrelevant; this is prompt engineering, not API design. (b) might be a side benefit, but it is not the primary reason. (d) misses the point: detailed descriptions help the model make fewer wrong calls, not fewer calls overall.

</details>

4. ▢ You are building a tool called `search`. You also have a tool called `search_documents`, `search_issues`, and `search_users`. Why is this tool naming a problem, and what should you do instead?

<details markdown="1"><summary>Check</summary>

The tool `search` is too generic. The model will not know which search tool to call when it needs to search. It might call all of them, or pick at random. Instead, rename `search` to something specific like `search_logs` or `search_comments` or `search_code`. The rule is: each tool name should be specific enough that the model knows what it does, and different enough from other tool names that the model will not confuse it.

</details>

## Real-world reps

- [ ] Find the tool definitions (name and description) for an LLM application or agent framework you use. Read the description for each tool. Write down one tool that has a description clear enough that you understand when the model should call it, and one tool whose description is too vague. Note why the first one works and what is missing from the second.

- [ ] Pick a tool you use regularly in the command line (like `grep` or `find`). Imagine you had to describe it for a model that knows nothing about your filesystem. Write a one-sentence description that tells the model what the tool does and when to use it instead of a similar tool.

- [ ] Tomorrow: Take a tool description from a real agent or API documentation that you think is poorly written. Rewrite it for a model that is choosing among several similar tools. Make it at least twice as long, include an example of when to use it, and say one thing it is NOT good for.

## Going further

- [Article: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
