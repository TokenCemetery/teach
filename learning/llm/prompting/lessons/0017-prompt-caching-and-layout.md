---
title: "17. Prompt Caching and Layout"
description: Order a prompt with the stable parts first so the provider can cache the prefix
type: lesson
---

# Lesson 17. Prompt Caching and Layout

**Mission link:** A prompt template that puts its stable text first lets the provider skip reprocessing it on every call, so layout is a cost and latency decision made in the template, not an afterthought.
**Primary source:** [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
**Prerequisites:** [Lesson 16](0016-versioning-prompts.md), [Prompt caching](../GLOSSARY.md)

## Warm-up

1. ▢ Lesson 13 said where a long document and the question go in one prompt. Which comes first, and does that order agree with putting stable content first for caching?

<details markdown="1"><summary>Check</summary>

The long documents come first and the question last. It agrees: a document reused across requests is stable, and the question changes every time, so the two goals point the same way.

</details>

2. ▢ Lesson 15's template has fixed text and slots. Which of the two is a candidate for the cached prefix, and which can never be?

<details markdown="1"><summary>Check</summary>

The fixed text is a candidate, since it is identical on every call. The per-request slot values change, so anything that contains one cannot be part of a reused prefix.

</details>

## Know this

### The prefix is what gets cached

**Prompt caching** stores the processed state of a prompt prefix so a later call sharing that exact prefix skips recomputing it. Anthropic's documentation describes its version: the cached prefix covers the whole request in a fixed order, `tools`, then `system`, then `messages`, up to and including the block marked with `cache_control`. The hash behind a cache entry is cumulative, so changing any block at or before the marked one produces a different hash on the next request, and the entry does not match.

Other providers implement caching differently, so check their rules. The principle here, a reused exact prefix, is the part to carry over.

### Layout follows from that

Put what never changes first and what changes per request last: tool definitions, then the system prompt, then long documents and few-shot examples, then the per-request question. The documentation says to place static content at the beginning and mark the end of the reusable part.

```python
def build_request(system: str, documents: str, question: str) -> dict:
    return {
        "system": system,
        "messages": [
            {
                "role": "user",
                "content": [
                    # stable: the end of this block is where a cache marker goes
                    {"type": "text", "text": documents},
                    # per request: after the marker, never part of the prefix
                    {"type": "text", "text": question},
                ],
            },
        ],
    }
```

Here `documents` is shared across calls and `question` is not, so the shared text leads, and they are separate blocks so the marker can sit after the documents and before the question. In Anthropic's API that marker is a `cache_control` field on the documents block, the other vendor-specific part of this sketch. The documentation's own example of a mistake is a block that holds a timestamp and the user message, with the cache marker on it: the prefix hash includes the timestamp, so every request writes a new entry and never reads one. Keep a timestamp, a request ID or a user name out of the stable part. Anthropic's fix is to put the marker on the last block that is identical across requests.

### What breaks a hit, and the limits

- A prefix shorter than the model's minimum is not cached, and no error is returned. The documented minimum depends on the model and ranges from 512 to 4,096 tokens. If `cache_creation_input_tokens` and `cache_read_input_tokens` in the response usage are both 0, the prompt was not cached.
- Changing tool definitions invalidates the whole cache. The documentation's invalidation table also lists changes to the tool-choice setting, images and some thinking and effort settings, which invalidate the messages part.
- The default lifetime is 5 minutes, refreshed each time the entry is read. A 1-hour option exists at additional cost.
- A cache entry is available only after the first response begins, so parallel first requests do not share it. For concurrent and agent workloads, see [lesson 34 of the agents track](../../agents/lessons/0034-prompt-caching-and-concurrency.md).

Reads are cheaper than uncached input and writes cost more: the documentation lists 5-minute writes at 1.25 times the base input price and reads at 0.1 times, with per-model exceptions on reads. So a layout that never hits costs slightly more than no caching at all.

## Practice

1. ▢ A template starts with `Current time: {now}`, then a 3,000-token style guide, then the user's question. Why does caching never help it, and what is the fix?

<details markdown="1"><summary>Check</summary>

The timestamp is the first block, so the prefix hash changes on every request and no later block can be read from cache. Move the style guide and any other fixed text ahead of the timestamp, or drop the timestamp from the prompt if the task does not need it, and keep the question last.

</details>

2. ▢ First request: `cache_read_input_tokens` is 0, `cache_creation_input_tokens` is 2,400, `input_tokens` is 60. Second request, same prefix, a 75-token question: what do the three fields show if caching worked, and what is the total input?

<details markdown="1"><summary>Hint</summary>

The documentation says `input_tokens` counts only what comes after the last cache breakpoint.

</details>

<details markdown="1"><summary>Check</summary>

`cache_read_input_tokens` is 2,400, `cache_creation_input_tokens` is 0 and `input_tokens` is 75. Total input is the sum, 2,475 tokens. The prefix was read from cache instead of written again, and only the new question was processed fresh.

</details>

3. ▢ A team adds a 600-token system prompt on a model whose minimum is 1,024 tokens, marks it for caching, and sees both usage counters at 0. What happened, and is something broken?

<details markdown="1"><summary>Check</summary>

The prompt is under the minimum, so it was processed without caching and no error was returned. Nothing is broken. Add more stable content, such as examples, to reach the minimum, or accept uncached calls.

</details>

4. ▢ Which prompt layout is best for caching a support bot that answers many questions about one long policy document?

    - a) Question, then the policy document, then the system prompt
    - b) System prompt, then the question, then the policy document
    - c) System prompt, then the policy document, then the question
    - d) System prompt, then the user's name, then the policy document

<details markdown="1"><summary>Check</summary>

**c)** The system prompt and the document are identical across requests and lead, and the question comes last. (a) and (b) put the changing question ahead of the stable text, so the prefix differs every call. (d) puts a per-user value ahead of the document, which breaks the shared prefix for every different user.

</details>

## Real-world reps

- [ ] Take one prompt you run and mark each part as stable, changes daily, or changes per request, then check the stable parts sit first.
- [ ] Make one call twice with the same prefix on a provider that reports cache usage and read the counters for both calls.
- [ ] Tomorrow: find any timestamp, ID or name inside a prompt's stable region and move it to the end.

## Going further

- [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Lesson 34 of the agents track: Prompt Caching and Concurrency](../../agents/lessons/0034-prompt-caching-and-concurrency.md)
- [Prompts in Production](../reference/prompts-in-production.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
