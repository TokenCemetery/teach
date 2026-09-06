---
title: 1. Chunking
description: The first pipeline choice, and the one every later stage inherits
type: lesson
---

# Lesson 1. Chunking

**Mission link:** Chunking is the first decision in the pipeline this workspace teaches, and every later stage (embeddings, hybrid search, reranking) works with whatever a chunk gave it. A bad chunking choice cannot be reranked away.
**Primary source:** [Article: "Chunking Strategies for LLM Applications", Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
**Prerequisites:** none

## Know this

### Why a document gets split at all

A retrieval pipeline doesn't embed and search whole documents. It splits each document into **chunks** first, then embeds and indexes those. Two practical reasons force this:

- An embedding model has a limited context window, so a long document may not fit at all.
- Even when it fits, embedding a long, topically mixed passage as a single vector blurs it. The vector ends up representing an average of everything the passage touches, which makes it a worse match for a query about any one specific thing inside it.

So chunking exists to keep each embedded unit focused enough that its vector actually represents what a query might be looking for.

### The core trade-off

Chunk size trades two failure modes against each other:

- **Chunks too large:** the embedding blurs multiple topics together, hurting precision, and a query about one detail inside a long chunk may not surface it as a close match. Retrieval also returns more irrelevant surrounding text along with the relevant part.
- **Chunks too small:** each chunk may lose the surrounding context that makes it interpretable, or that answers a question that spans more than one small piece. A single sentence pulled from a paragraph can be ambiguous or incomplete on its own.

There is no universal right chunk size. The right choice depends on the corpus (a legal contract's clauses read differently than a chat transcript) and the query pattern the system needs to serve (a query needing one fact behaves differently than one needing a multi-step explanation).

### Common chunking strategies

- **Fixed-size.** Split every N tokens or characters, usually with some overlap between consecutive chunks. Simple and predictable, but blind to the document's actual structure: it can split a sentence, or a table, in half.
- **Recursive / structure-aware.** Split on the document's natural boundaries first (sections, then paragraphs, then sentences), falling back to a fixed-size split only when a boundary-delimited piece is still too large. This respects the author's own organization instead of imposing an arbitrary one.
- **Semantic chunking.** Embed consecutive sentences and split where the similarity between neighbors drops sharply, on the idea that a topic shift is where a chunk boundary belongs. More expensive to compute, and it targets the actual failure mode (mixed topics inside one chunk) directly rather than by proxy.
- **Document-structure-aware.** Treat structural units the format already provides, such as a heading's section, a table, or a code block, as atomic: never split one across a chunk boundary, because doing so usually destroys its meaning.

### Overlap

Consecutive chunks commonly overlap by some number of tokens. Without overlap, a fact or a sentence that straddles exactly where two chunks split can end up fragmented, unrecoverable in full from either chunk alone. Overlap costs some redundant storage and embedding computation in exchange for not losing information at chunk boundaries.

## Practice

1. ▢ In one sentence, why does a retrieval pipeline chunk a document instead of embedding it whole?

<details markdown="1"><summary>Check</summary>

Because a long, topically mixed passage embeds as one blurred vector representing an average of everything it touches, which retrieves poorly for a query about any one specific thing inside it (and it may not even fit the embedding model's context window).

</details>

2. ▢ A corpus of long legal contracts is chunked with fixed-size 512-token pieces and no overlap. Users ask questions about specific clauses, and retrieval keeps missing clauses that got split across a chunk boundary. Name two changes to the chunking strategy that would help, and what each fixes.

<details markdown="1"><summary>Hint</summary>

One change addresses the boundary-splitting itself; the other addresses what happens when a split is unavoidable.

</details>

<details markdown="1"><summary>Check</summary>

Switch to a structure-aware (or document-structure-aware) strategy that splits on clause or section boundaries instead of a raw token count, so a clause isn't cut mid-thought in the first place. Separately, add overlap between chunks, so that even where a split does land near a clause boundary, the clause's full text still appears intact in at least one chunk.

</details>

3. ▢ A team chunks a corpus into very short, single-sentence pieces to maximize precision. What's the likely downside, and when would it show up?

<details markdown="1"><summary>Check</summary>

Individual chunks may lose the surrounding context that makes them interpretable or complete: a sentence pulled alone can be ambiguous, or a question whose answer spans more than one sentence won't be answerable from any single retrieved chunk. This shows up as retrieval technically finding "the right sentence" while the system still can't produce a correct or complete answer from it.

</details>

4. ▢ Why do consecutive chunks commonly overlap?

   - a) To make the vector index larger and more thorough
   - b) So a fact or sentence that straddles a chunk boundary isn't fragmented and unrecoverable from either chunk
   - c) Because embedding models require a minimum input length
   - d) To let the reranker compare adjacent chunks against each other

<details markdown="1"><summary>Check</summary>

**b)** So a fact or sentence that straddles a chunk boundary isn't fragmented and unrecoverable from either chunk. (a) describes a cost of overlap, not its purpose. (c) and (d) aren't why overlap exists.

</details>

## Real-world reps

- [ ] Pick a real document from a corpus you'd retrieve over. Chunk it by hand two ways (fixed-size, and structure-aware using its actual headings or sections) and compare where each strategy splits mid-thought.
- [ ] For that same document, pick one query a user might realistically ask, and check which chunking strategy's output would actually contain a complete, retrievable answer to it.
- [ ] Tomorrow: read the chunking strategies article linked below in full, and write down which strategy you'd default to for your own corpus and why.

## Going further

- [Article: "Chunking Strategies for LLM Applications", Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
