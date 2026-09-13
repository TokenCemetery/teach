---
title: 11. Compaction and Retrieval on Demand
description: Two strategies for keeping a long-running agent's context under budget while preserving what still matters
type: lesson
---

# Lesson 11. Compaction and Retrieval on Demand

**Mission link:** Budget the token cost and latency of an agentic loop, and say which part of the loop the amplification comes from.
**Primary source:** [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Prerequisites:** [Lesson 10](0010-the-context-window-as-budget.md)

## Warm-up

1. ▢ Why is naive truncation (dropping the oldest turns once a size limit is hit) risky?

<details markdown="1"><summary>Check</summary>

Naive truncation might drop a tool result, constraint, or instruction the model still needs, and the model won't know the information is missing. It will silently work from an incomplete understanding and fail in unexpected ways.

</details>

2. ▢ What is context rot?

<details markdown="1"><summary>Check</summary>

As low-relevance content accumulates in the context, the model's attention becomes noisier and it struggles to distinguish what still matters from old dead ends and abandoned reasoning. A bloated context is both expensive and less accurate.

</details>

## Know this

### Compaction: replace old turns with a summary

One strategy is periodically to replace a stretch of old transcript with a condensed summary that the model can still act on. Instead of keeping "I read file1.py and found these 50 lines," you might replace that entire sequence with "file1.py contains a database class; key methods are init, query, close."

The harness detects when the transcript has grown long and hands the old turns to a summarizer (often another model call, or a simpler extraction). The summary is inserted into the transcript in place of the original turns, keeping the transcript size under control.

**The risk:** The summary might drop a detail that turns out to matter later. If the agent later needs to know that file1.py also defined a helper function, but the summary omitted it, the agent has lost that information permanently. Unlike naive truncation (which is always risky), compaction is deliberate and reversible in theory, but the information loss is real and hard to predict.

### Retrieval on demand: give the agent a tool to re-fetch detail

Another strategy is not to keep full detail in context at all. Instead of loading and storing every file's content, the harness keeps only a summary (file name, size, modification date, a brief line-count note). When the model needs to see the full content, it calls a tool like "read_file" or "re_fetch_detail". The model gets the detail on demand and only for the file it is currently examining.

The trade-off: Each fetch adds latency (one more tool call, one more round trip). But the resident context stays much smaller. Over a long task that examines many files but only works with a few at a time, retrieval on demand is far cheaper in total tokens than keeping every file in context forever.

### Composed together: compaction + retrieval on demand

The most powerful approach combines both. The harness maintains a small, curated context that contains:

- The goal and latest constraints
- A summary of what has been done so far
- File names and metadata
- Recent findings that matter

Old detailed results are compressed into summaries (compaction). If the model needs to see the full detail of an old file or result, it can fetch it with a retrieval tool (on demand). The model's working memory is small and fast, but it has a way to reach back for the detail it needs.

In a code-review agent reviewing 100 files over 200 turns:

- A naive agent keeps every file ever read in context, growing to 500,000 tokens by turn 50. Turns 51-200 are sluggish and expensive.
- A smart agent keeps only file paths and a summary in context (5,000 tokens), with a "read_file" tool. It fetches each file on demand as it compares. Turn 50 costs about the same as turn 200. Total token cost over the whole run is a fraction of the naive approach.

## Practice

1. ▢ You summarize the first 20 turns of an agent's transcript into a paragraph: "The agent explored three codebases and found performance bottlenecks in caching." This summary replaces the original 20 turns. Later, on turn 50, the model says it wants to understand the exact query that was slow. What risk does compaction present here?

    - a) The model will refuse to work without the original turns
    - b) The summary might not have recorded the exact query details, and they may be lost forever
    - c) Compaction is always lossless so this is not a risk
    - d) The model will re-read the summary and remember the query

<details markdown="1"><summary>Check</summary>

**b)** Compaction drops details that might matter later. The summary is concise but may omit specifics the model needs downstream. Unlike truncation, compaction is deliberate, but information loss is real. Option a is wrong because the model will work with the summary, but may produce wrong results. Option c is wrong because compaction is lossy by design. Option d is wrong because the model works only with the new summary, not the original.

</details>

2. ▢ An agent is processing 200 documents, summarizing each one. Why is retrieval on demand better than keeping all 200 document contents in context from the start?

<details markdown="1"><summary>Hint</summary>

How many documents does the model typically need in its context at the same time? If it is summarizing document 45, does it need the content of documents 1 through 44 available right now?

</details>

<details markdown="1"><summary>Check</summary>

The model is usually focused on one or a few documents at a time. Keeping all 200 in context wastes tokens on content the model is not currently examining. With retrieval on demand, the harness keeps only the current document in context and a summary of previous findings. If the model needs to re-examine an old document, it fetches it. Total token cost over 200 documents is much lower than keeping all 200 in memory the whole time.

</details>

3. ▢ In a compaction plus retrieval on demand system, what three things should the always-resident context contain?

<details markdown="1"><summary>Check</summary>

The goal and constraints, a summary of progress so far, and metadata about available resources (file names, document titles, tool lists). The full detail is either compressed into summaries (compaction) or available on demand (retrieval). This keeps the resident context small and focused on what the model needs to act right now.

</details>

4. ▢ You design an agent to read technical papers and extract summaries. After reading 50 papers, the context is 60,000 tokens. Compare two approaches:
    - Approach A: Compact old paper contents into one-paragraph summaries every 10 papers. Keep all summaries in context.
    - Approach B: Keep only paper titles, authors, and findings in context. Give the agent a "re_read_paper" tool if it needs full text.

Which approach uses fewer tokens by paper 100, and why?

<details markdown="1"><summary>Check</summary>

Approach B uses fewer tokens. With Approach A, you accumulate 10 summaries each 200-300 tokens, reaching 2,000-3,000 tokens of compacted content by paper 100. With Approach B, you keep only metadata (100-200 tokens) plus the current paper's text (500 tokens), and the model rarely needs to re-read an old paper. Approach B saves tokens by not storing every old summary all the time.

</details>

## Real-world reps

- [ ] Audit a long transcript from an agent you have used or written. Identify which parts are still relevant (goal, recent constraints, outstanding problems) and which are safe to compact or delete. Write a one-sentence summary that could replace the first 30% of the turns.
- [ ] Design a hypothetical agent for a task you care about (research, coding, analysis). Sketch whether you would use compaction, retrieval on demand, or both, and why.
- [ ] Tomorrow: Take a "dumb" version of an agent that keeps everything in context, estimate its token cost over 100 turns, then redesign it with compaction and retrieval on demand and estimate the new cost.

## Going further

- [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
