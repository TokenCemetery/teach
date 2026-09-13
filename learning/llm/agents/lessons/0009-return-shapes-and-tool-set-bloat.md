---
title: 9. Return Shapes and Tool-Set Bloat
description: A tool's return value costs context budget, and too many tools hurts the model's ability to pick correctly
type: lesson
---

# Lesson 9. Return Shapes and Tool-Set Bloat

**Mission link:** Designing an agent's tool surface includes choosing what a tool returns (its return shape) and deciding how many tools to offer, because both are design choices that affect the model's ability to decide correctly among its options and the cost of every turn that follows.
**Primary source:** [Article: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
**Prerequisites:** [Lesson 8](0008-naming-and-describing-a-tool.md)

## Warm-up

1. ▢ From Lesson 8: Why should a tool's description tell the model when and how to use it rather than just listing what parameters it accepts?

<details markdown="1"><summary>Check</summary>

Because the model has no other source of guidance for choosing among tools. A bare parameter list explains how to call a tool but not why or when to reach for it, which is the actual decision the model has to make.

</details>

2. ▢ From Lesson 8: What problem do you create if you have two tools in the same tool set with very similar names and descriptions?

<details markdown="1"><summary>Check</summary>

The model cannot reliably tell them apart, so it may call the wrong one or call both to be safe. The noise also degrades the model's ability to choose correctly among every other tool in the set, not just the two that are similar.

</details>

## Know this

### A Tool's Return Value Costs Context Budget

Every message in the transcript consumes tokens. When a tool returns a result, that result gets appended to the transcript, and the model sees it on every subsequent turn until the run ends or the transcript is truncated. A tool that returns a small focused answer costs a little. A tool that returns five thousand database rows costs real tokens on every turn for the rest of the run, whether or not the model needed all of them.

```
Bad:
Tool: fetch_user_records
Returns: [complete User record, complete User record, ...]
# 5000 rows, 50KB of JSON, ~10,000 tokens consumed per turn after this call
```

After the tool returns, the transcript balloons. The model now has to process all five thousand rows on the next turn just to read its own context. This bloats the token budget and slows down the loop.

### Design Return Shapes for Decision-Making, Not Completeness

Instead of returning everything the underlying system has, design a return shape that gives the model what it needs to decide the next step.

```
Better: Option 1 - Return a summary
Tool: fetch_user_records
Returns:
  total_count: 5000
  sample_results: [User, User, User, ...] # top 5 results
  query_was_too_broad: true
  suggestion: "Your query matches 5000 users. Narrow it with a company_id or email domain filter."

# ~500 tokens consumed per turn after this call
```

The model can now see that the query was too broad and knows what to do next: it can call the tool again with better filters. This returns a tenth of the tokens of the full dump.

```
Better: Option 2 - Let the model ask for more
Tool: fetch_user_records
Returns:
  count: 50  # number of results returned
  total_matching: 5000  # number of results if the query was not limited
  results: [User, User, ...] # just the first 50
  next_page_token: "abc123xyz"

# Model sees it got 50 of 5000. It can decide to refine the query or ask for the next page.
```

In both cases, the model gets enough information to make an informed decision without being buried in data.

### Tool-Set Bloat: More Tools Means Worse Choices

Adding a tool to an agent is not free. Every tool the model can choose from makes the choice harder for the model. This is called tool-set bloat.

With three tools, the model picks correctly most of the time:

```
Tools:
- search_documentation
- read_file
- list_directory
```

With ten tools, the model starts second-guessing itself, calling multiple tools when one would do:

```
Tools:
- search_documentation
- search_issues
- search_code
- read_file
- read_logs
- list_directory
- list_repos
- get_git_history
- get_git_diff
- get_git_status
```

Each new tool adds noise to the decision. The model has to read and consider all ten descriptions before picking one. If two are similar (search_code and search_documentation), the model might call both. The effect is quiet: every existing tool suffers slightly, not just the new one.

The cost is real: more tool calls, more tokens in the transcript, more turns wasted on redundant information.

### Adding a New Tool Versus Adding a Parameter

When you are tempted to add a tool, first ask: could this be a parameter on an existing tool?

```
Bad: Two tools
- name: list_files
- name: list_directories
```

Better: One tool with a parameter

```
Good: One tool with a parameter
- name: list_contents
  parameters:
    - name: path
    - name: type
      type: enum
      values: [files, directories, all]
```

The model chooses the type it wants, and you have not added noise to the tool set.

But sometimes a new tool makes sense. If the tools are fundamentally different (they are called in different situations, they return different shapes, they require different permissions), then a new tool with a clear name is better than an overloaded parameter:

```
Good: Two specialized tools
- name: search_database_by_id
  parameters:
    - id
    # Fast, returns a single record
- name: search_database_by_query
  parameters:
    - query
    # Might return many records
```

The model knows the difference: by_id is fast and precise, by_query is flexible but might return a lot. The names make the decision clear.

The rule: add a new tool when the tool would be called for fundamentally different reasons, or when you cannot express the distinction in parameters. Add a parameter when the tool is basically the same operation with a variation in input or output format.

### Observing Tool-Set Bloat in Practice

A subtle sign is when the model starts saying things like "I should call search first to see if it exists, then fetch if it does" when one tool could have done the whole job. This is the model trying to be safe because it is not confident about what each tool does. The problem is not the model; it is the tool set.

Another sign is repeated tool calls: the model calls the same tool multiple times in a single run, like searching twice, or listing twice. This often means the tool set is not giving the model a way to narrow down results in one call, so it has to call the tool with different parameters to find what it needs.

## Practice

1. ▢ A tool called `get_user_history` returns a JSON array of 100,000 user action events from the past month, each one detailed. The model will probably call this tool, look at the first ten events, and ignore the rest. What design change reduces the token cost on every turn after this call?

<details markdown="1"><summary>Check</summary>

Limit the return to the first N events (e.g., the first 20) and include a total_count and a way for the model to ask for more. This way the model can see what it needs without paying for all 100,000 events. Alternatively, return a summary: "50 events in the past week, 50 in the week before. Most recent: user logged in" rather than the full detail, and let the model ask for specifics if needed.

</details>

2. ▢ You have a tool set with 15 tools. The model is calling search_by_name and search_by_id in the same run even though it could express both searches as parameters to a single tool. What is the harm of having kept them as two separate tools?

<details markdown="1"><summary>Hint</summary>

Think about the model's job: it has to read fifteen descriptions and decide which tool to call. How does having similar tools make that job harder?

</details>

<details markdown="1"><summary>Check</summary>

Tool-set bloat. The model has to choose among fifteen tools. Similar tools like search_by_name and search_by_id make the choice harder. The model might call both when one would do, or waste time deciding which is appropriate. Every existing tool suffers a tiny bit because the set got noisier. The fix is to merge them into one search tool with a parameter for the search field.

</details>

3. ▢ Which of the following is a sign that a tool's return shape is too verbose?

    - a) The tool is called very frequently
    - b) The model reads the result and asks for a summary before using it
    - c) The tool takes a long time to execute
    - d) The tool requires authentication

<details markdown="1"><summary>Check</summary>

**b)** The model reads the result and asks for a summary before using it. This means the tool is returning too much information; the model has to filter or summarize what it got before it can make a decision. (a) is not related to return shape; a frequently called tool might be narrow by design. (c) is about execution speed, not tokens. (d) is about permissions, not the return shape.

</details>

4. ▢ You are designing tools for a code search agent. Should `search_code` and `get_code_diff` be one tool or two? Explain in one or two sentences.

<details markdown="1"><summary>Check</summary>

Two separate tools. They are called for different reasons (search looks for files that match a pattern, diff shows changes between versions), they return different shapes (a list of files versus a structured diff), and they solve different problems. A single overloaded tool would make the model's choice harder. If they were variations on the same operation (like search_code with different query parameters), they could be one tool with a parameter.

</details>

## Real-world reps

- [ ] Find a tool set in an LLM application or agent you have access to. Count the tools. Read the model's trajectory and mark every turn where the model called a tool. Estimate: did the model ever call two similar tools when one would have done the job? Write one sentence about whether the tool set felt bloated or well-designed.

- [ ] Pick a tool that returns structured data. Read a sample return value. Is there any part of the return that the model would likely ignore? Rewrite the return shape to exclude that data or move it to a second call, estimating how many tokens you saved.

- [ ] Tomorrow: Design a tool that could go either way (a new tool or a parameter on an existing one). For your choice, write two sentences about why you picked a separate tool or a parameter, what the alternative would cost, and when you might reconsider.

## Going further

- [Article: "Writing Effective Tools for Agents", Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
