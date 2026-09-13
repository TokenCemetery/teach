---
title: 14. Files as Memory
description: Using durable files as the simplest form of across-run memory for agents
type: lesson
---

# Lesson 14. Files as Memory

**Mission link:** Diagnose a failing agent from its trajectory instead of adding another instruction to its prompt, by building systems where the agent's memory is inspectable and the harness can curate what persists.
**Primary source:** [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
**Prerequisites:** [Lesson 13](0013-scratchpad-versus-memory.md)

## Warm-up

1. ▢ You start an agent with a fresh transcript for the second time. What does the empty transcript tell you?

<details markdown="1"><summary>Check</summary>

That the agent is starting a new run with no memory of the previous run unless the harness deliberately loaded facts back in before the loop started.

</details>

2. ▢ An agent wrote notes to a file during its last run. If you want those notes to influence the agent's behavior in the new run, what must the harness do?

<details markdown="1"><summary>Check</summary>

The harness must read the file, or relevant parts of it, and include the content in the initial context or prompt for the new run, so the model can see and act on it.

</details>

## Know this

Writing facts to a plain file, or similar durable store, the harness reads back in on a later run is the simplest working form of across-run memory. The pattern is straightforward: give the agent a tool to write a note, a markdown file, a JSON record, or a small structured log, and at the start of a later run, the harness reads relevant parts of that file back into the new transcript before the loop starts.

This is deliberately simple and inspectable compared to, say, a vector database. A human can open the file and read exactly what the agent "remembers". You can edit it by hand if needed. You can see stale or wrong entries and fix them without re-training anything.

The risk is real, though. An agent that keeps appending to a memory file without ever pruning or updating it accumulates stale or contradictory notes over time. A note that was true last month might be false today. Two different facts might contradict each other. This is the same context rot problem lessons 10 and 11 addressed for a growing transcript within a single run. Memory needs the same active curation: periodic review, archival of old entries, consolidation of duplicates, removal of facts that no longer apply.

One important clarification: retrieval on demand, from lesson 11, fetching detail from a corpus of documents or prior work by search, is not the same as memory, even though both involve "fetching text into context". Retrieval answers the question "what is relevant to this specific query right now?" by searching a large corpus. Memory is a small, deliberately curated set of facts the agent, or its designer, decided are worth carrying forward regardless of the current query. A coding assistant might retrieve examples of the user's past work to illustrate a style, but it also needs memory that says "user prefers async/await over callbacks" as a standing fact, not a query result. The retrieval corpus is about answering specific questions; the memory file is about standing context.

The honest caveat from [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) is this: agent memory across runs is a newer and less-settled area. Production systems for across-run memory are still evolving. This lesson covers the file-based pattern, which is simple and human-inspectable, but not necessarily the definitive approach your production system will use years from now.

## Practice

1. ▢ An agent is helping a user learn to cook. The agent notes that the user dislikes cilantro and suggests recipes without it. When you restart the agent the next day for a new cooking session, should the harness load the cilantro note back in from the memory file?

<details markdown="1"><summary>Check</summary>

Yes. The preference is a standing fact about the user that applies across sessions. The harness should read the memory file at start-time and include "user dislikes cilantro" in the initial context so the model can use it when generating new recipes.

</details>

2. ▢ During a run, an agent writes to a scratchpad "files checked so far: api.py, utils.py, config.py" to avoid re-analyzing them. The run ends. Should this scratchpad entry be saved to the across-run memory file?

<details markdown="1"><summary>Hint</summary>

Does that particular information, the list of files checked in this specific run, need to carry forward to future runs, or was it just useful bookkeeping within the one task?

</details>

<details markdown="1"><summary>Check</summary>

Probably not, unless the task spans multiple agent runs. If each code review is a fresh, independent task, the list of files checked in Run A is not relevant to Run B. Saving every scratchpad entry would clutter the memory file with ephemeral details. A good heuristic: only save facts to memory if a future run will need them.

</details>

3. ▢ You notice the agent's memory file now contains conflicting advice: "user prefers tabs" and "user prefers spaces" written weeks apart. What should you do?

    - a) Delete the memory file entirely so the agent starts fresh.
    - b) Manually review and edit the file to fix the contradiction.
    - c) Add a new tool to the agent so it can resolve conflicts automatically.
    - d) Ignore it, since the model will figure out which one is current.

<details markdown="1"><summary>Check</summary>

**b)** Manually review and edit the file. Memory curation is a human responsibility. You need to understand which entry is stale, fix or remove it, and keep the file clean and authoritative. Deleting the whole file loses other valuable facts. Automating conflict resolution without human judgment risks encoding the wrong preference. The model should not have to guess or reason about contradictions in its own memory.

</details>

4. ▢ How is a file-based memory system different from a retrieval system that searches a corpus of the agent's past work?

<details markdown="1"><summary>Check</summary>

A retrieval system answers "what from my past work is relevant to this query?" and pulls material based on keyword or semantic match. A memory system holds a small set of standing facts the harness loads regardless of query. Memory is curated and durable; retrieval is query-driven. You might retrieve past code examples when the user asks "show me how I solved this before", but you remember "user prefers async/await" as a standing preference all the time.

</details>

## Real-world reps

- [ ] If you have an agent that runs more than once, check whether the harness loads any stored facts before the first call to the model. If not, add a print statement or log to see what is happening at run-start time.
- [ ] Design a simple memory file format for a task you know well. What facts would you write? How would you know when to update or remove an entry?
- [ ] Tomorrow: Build a one-run agent that writes one fact to a memory file, any format: JSON, markdown, or plain text. Then build a second run of the same agent that reads that file and uses it. No vector database, no search, just durable storage and harness-managed loading.

## Going further

- [Article: "Effective Context Engineering for AI Agents", Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
