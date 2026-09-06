---
title: 12. Prompt Construction and Context-Window Budget
description: Why retrieved chunks compete for a shared context-window budget, and why where a chunk sits in the prompt matters as much as whether it was retrieved
type: lesson
---

# Lesson 12. Prompt Construction and Context-Window Budget

**Mission link:** Stage 7 opens the last leg of the mission: even a perfectly diagnosed, well-tuned retrieval pipeline (stages 1 to 6) can still fail the user if the retrieved chunks are assembled into a prompt badly, which is a distinct failure point from retrieval itself.
**Primary source:** [Paper: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
**Prerequisites:** [Lesson 11](0011-diagnosing-the-pipeline.md), [Chunk](../GLOSSARY.md)

## Warm-up

1. ▢ What is the first stage to check when diagnosing wrong retrieved context, and why is it checked before anything else?

<details markdown="1"><summary>Check</summary>

Chunking: pull up the chunk that should have answered the query and check whether the relevant information exists coherently in one place. If chunking split or buried the answer, no later stage (embedding, index, hybrid weighting, reranking) can retrieve what was never given a usable representation in the first place.

</details>

2. ▢ Why is diagnosing across a small set of known-failing queries more reliable than debugging a single anecdotal failure?

<details markdown="1"><summary>Check</summary>

A single failing query might fail for an unusual, one-off reason that doesn't reflect a systemic problem. Measuring recall@k and MRR across a representative set of failures reveals where the aggregate biggest drop-off happens, pointing at a stage that's systematically losing information.

</details>

## Know this

### Retrieved chunks are one line item in a shared budget

Once chunks are retrieved and ranked (stages 1 to 6), they still have to become part of an actual prompt: typically a system or instruction message, the retrieved chunks themselves, and the user's own question, all inside one finite **context window**. That window is a real, shared budget: retrieved chunks compete for space with the system prompt, any conversation history, and the question itself, not just with each other. Retrieving more chunks (a larger *k*) isn't free even when every one of them is genuinely relevant, since each one consumes context-window budget that something else, more conversation history, a longer system prompt, could otherwise use.

### Being in the prompt doesn't mean being used

A model's ability to use information depends on more than whether that information is technically present in the context window. Liu et al.'s **"lost in the middle"** finding shows models use information placed near the very beginning or the very end of a long context far more reliably than information buried in the middle, even when the buried information is entirely within the model's stated context limit. A highly relevant chunk placed in the middle of a long, chunk-stuffed prompt can be effectively invisible to generation, producing a wrong or incomplete answer that looks like a retrieval failure but isn't: the chunk was retrieved correctly; it just wasn't positioned somewhere the model reliably reads from.

### The practical consequence for assembling a prompt

Two consequences follow directly. First, stuffing many marginal, lower-relevance chunks into context "to be safe" has a cost beyond token budget: it can bury a genuinely good chunk in the middle of the prompt, making the answer worse, not just more expensive. Second, chunk placement is a deliberate choice, not an accident of insertion order: placing the most relevant chunk (or chunks) near the beginning or end of the assembled context, rather than wherever it happened to land after concatenation, matters for whether generation actually draws on it.

## Practice

1. ▢ Why is context-window budget a whole-request concern rather than something retrieval can reason about on its own?

<details markdown="1"><summary>Check</summary>

Retrieved chunks share the context window with the system prompt, any conversation history, and the user's question; the budget available for retrieved chunks depends on how much everything else in the request is using, not on retrieval quality alone.

</details>

2. ▢ Describe the "lost in the middle" phenomenon and one practical implication it has for building a RAG prompt.

<details markdown="1"><summary>Check</summary>

Models use information at the beginning or end of a long context far more reliably than information buried in the middle, even when it's technically within the context window. A practical implication: the most relevant retrieved chunk should be placed near the start or end of the assembled prompt, not left wherever concatenation order happened to put it, and padding the prompt with many marginal extra chunks risks burying a genuinely useful one in the middle.

</details>

3. ▢ A team retrieves the top 20 chunks "to be safe," places them in relevance order, but concatenates them so the single most relevant chunk ends up in the middle of the assembled context. Generation misses an answer that was actually present in that chunk. What likely went wrong, and what's one fix?

<details markdown="1"><summary>Hint</summary>

Consider whether this is a retrieval failure or something that happens after retrieval succeeded.

</details>

<details markdown="1"><summary>Check</summary>

This isn't a retrieval failure: the correct chunk was retrieved. It's a prompt-construction failure caused by the lost-in-the-middle effect, since the most relevant chunk ended up positioned in the middle of a long context where models are least reliable at using information. A fix: reorder the assembled prompt so the most relevant chunk sits near the beginning or end, or reduce the number of chunks included so the good one isn't buried among many lower-relevance ones.

</details>

4. ▢ Why are "did retrieval find the right chunk" (stage 6's question) and "did the assembled prompt cause the model to actually use it" different failure points, even though both can produce the same symptom (a wrong final answer)?

<details markdown="1"><summary>Check</summary>

Stage 6's diagnostic procedure checks whether the correct chunk was retrieved and ranked highly enough to reach generation at all; it's entirely about the pipeline up to that point. Whether the model actually uses a chunk that did reach the prompt is a separate question, governed by where that chunk sits in the assembled context, which lost-in-the-middle shows matters independently of retrieval quality. A wrong answer can result from either failure, but they require different fixes.

</details>

5. ▢ Which claim is true of context-window budget and chunk placement in a RAG prompt?

   - a) Retrieving more chunks is always better, since more context can only help the model
   - b) A chunk technically inside the context window is guaranteed to be used the same way regardless of where it sits
   - c) Retrieved chunks compete for a shared budget with the rest of the request, and where a chunk is placed in the assembled prompt affects whether the model actually uses it
   - d) Lost-in-the-middle only affects very long documents, not a prompt assembled from several separate retrieved chunks

<details markdown="1"><summary>Check</summary>

**c)** Both the shared-budget point and the placement point are established in this lesson. (a) is false: more chunks cost budget and can bury a good chunk in the middle, hurting rather than helping. (b) is false: that's exactly what lost-in-the-middle disproves. (d) is false: the effect is about position within the overall context, regardless of whether that context came from one long document or several concatenated chunks.

</details>

## Real-world reps

- [ ] For a RAG system you run or plan to run, check where in the assembled prompt the most relevant retrieved chunk typically ends up, and whether that's a deliberate choice or an accident of concatenation order.
- [ ] Compute how much of your context window's total budget is spent on the system prompt and conversation history versus retrieved chunks, for a typical request.
- [ ] Tomorrow: try reducing the number of chunks you retrieve for a query where generation currently seems to miss relevant information, and check whether that alone changes the answer's quality.

## Going further

- [Paper: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
- [Article: "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
