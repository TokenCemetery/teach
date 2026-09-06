---
title: 3. Embedding Dimensionality Trade-offs
description: Why a bigger embedding vector isn't free, and when it's safe to truncate one instead of choosing a smaller model
type: lesson
---

# Lesson 3. Embedding Dimensionality Trade-offs

**Mission link:** This is stage 2's capstone: choosing an embedding model (lesson 2) isn't finished until its output size is weighed against what a corpus's storage and latency budget can actually afford.
**Primary source:** [Paper: "Matryoshka Representation Learning", Kusupati et al., 2022](https://arxiv.org/abs/2205.13147)
**Prerequisites:** [Lesson 2](0002-embedding-models-and-similarity.md), [Chunk](../GLOSSARY.md)

## Warm-up

1. ▢ Why does a bi-encoder embed a query and a passage separately rather than jointly?

<details markdown="1"><summary>Check</summary>

So every passage can be embedded once, ahead of time, and stored; only the query needs embedding at search time, letting it be compared cheaply against precomputed passage vectors. Embedding jointly (a cross-encoder) requires running the model on every pair, which doesn't scale to a large corpus.

</details>

2. ▢ Why do cosine similarity and dot product produce the same ranking only when vectors are normalized to unit length?

<details markdown="1"><summary>Check</summary>

Dot product is cosine similarity scaled by the two vectors' magnitudes. When both are fixed at unit length, that scaling factor is identical across every pair, so the two metrics rank identically; when magnitudes vary, dot product implicitly rewards larger vectors.

</details>

## Know this

### Dimensionality is a cost, not a free quality knob

A higher-dimensional embedding can encode more nuance, but every one of its dimensions costs something concrete: storage scales linearly with dimension (a 1536-dimension vector in float32 takes `1536 × 4 bytes = 6,144 bytes`, about 6 KB, versus a 256-dimension vector's `256 × 4 = 1,024 bytes`, about 1 KB, six times less), and both index memory and per-candidate distance computation scale the same way. Across a million chunks, that difference is 6 GB versus 1 GB just for the vectors themselves, before an index's own overhead. A bigger embedding is not automatically the better choice; it's a choice that has to be justified against what it costs, the same way a larger KV cache or a larger batch size had to be justified against a workload's actual budget in other serving contexts.

### Matryoshka Representation Learning: truncation as a designed feature, not a hack

Ordinarily, truncating an embedding vector to fewer dimensions is not safe: nothing in how a standard embedding model was trained orders its dimensions by importance, so cutting a normal 768-dimension vector down to 256 could discard information unpredictably and degrade quality far more than the dimension count alone would suggest. **Matryoshka Representation Learning (MRL)** trains a model differently: its loss explicitly optimizes prefixes of the full vector (the first 256 dimensions of a 1536-dimension embedding, say) to themselves be usable, meaningful embeddings, nested inside the full one like the smaller dolls inside a matryoshka doll. This means a model trained with MRL can be truncated after the fact, with a bounded, predictable quality cost, letting dimensionality be traded against storage and latency without retraining or re-embedding the whole corpus at a different size. This only holds for models actually trained this way; truncating a model that wasn't is back to the unsafe, unpredictable case.

### Deciding the right dimensionality means measuring, not assuming

The right dimensionality for a given corpus isn't a number to guess at; it's a number to measure. Using an MRL model (or comparing several candidate model sizes), retrieval quality, most directly recall@k against a labeled or synthetic query set (stage 6's subject), can be measured at each candidate dimensionality on the actual corpus and query pattern in question. The dimensionality worth shipping is the smallest one that still clears the quality bar the workload needs, not the largest available, and not a default picked without checking what it costs against what it buys.

## Practice

1. ▢ A corpus has 2 million chunks. Compute the storage difference, in gigabytes, between embedding it at 1536 dimensions and at 256 dimensions, both in float32.

<details markdown="1"><summary>Hint</summary>

Bytes per vector is `dimensions × 4 bytes`. Multiply by 2 million, then convert to gigabytes.

</details>

<details markdown="1"><summary>Check</summary>

1536 dimensions: `1536 × 4 = 6,144 bytes` per vector, `× 2,000,000 ≈ 12.3 GB`. 256 dimensions: `256 × 4 = 1,024 bytes` per vector, `× 2,000,000 ≈ 2.0 GB`. The difference is roughly 10.3 GB, about six times less storage at 256 dimensions.

</details>

2. ▢ A team truncates a standard (non-MRL) 768-dimension embedding model's vectors down to 256 dimensions to save storage, and retrieval quality collapses far more than the dimension reduction alone would suggest. What's the likely mistake?

<details markdown="1"><summary>Check</summary>

The model wasn't trained with Matryoshka Representation Learning, so nothing ordered its dimensions by importance or made any prefix of the vector a meaningful embedding on its own. Truncating it discards information unpredictably rather than in the bounded, designed way an MRL-trained model's truncation would.

</details>

3. ▢ What does an MRL-trained embedding model let a team do that a standard embedding model doesn't?

<details markdown="1"><summary>Check</summary>

Truncate the full embedding vector to a smaller dimensionality after the fact, with a bounded and predictable quality cost, trading storage and latency against quality without retraining the model or re-embedding the corpus at a different fixed size.

</details>

4. ▢ How should a team decide what embedding dimensionality to actually use for their corpus, rather than defaulting to whatever a model's full output size is?

<details markdown="1"><summary>Check</summary>

Measure retrieval quality, most directly something like recall@k against a labeled or synthetic query set representative of the actual corpus and query pattern, at several candidate dimensionalities, and choose the smallest one that still clears the quality bar the workload needs, rather than assuming the largest available dimensionality is necessary or that a smaller one is automatically "good enough."

</details>

5. ▢ Which claim is true of embedding dimensionality?

   - a) A larger embedding dimensionality always improves retrieval quality enough to justify its cost
   - b) Truncating any embedding model's vectors is equally safe, regardless of how the model was trained
   - c) Dimensionality is a cost (storage, index memory, per-candidate compute) that should be sized to the smallest value that meets a measured quality bar
   - d) MRL-trained models cannot be truncated; they only offer a fixed, single output size

<details markdown="1"><summary>Check</summary>

**c)** Storage and compute costs scale with dimensionality, so the right size is whatever the smallest value is that a measured quality bar actually needs. (a) is false: cost has to be weighed against measured benefit, not assumed. (b) is false: truncating a non-MRL model is unpredictable and can destroy far more signal than the dimension count implies. (d) is false: that flexible truncation is exactly what MRL training is built to allow.

</details>

## Real-world reps

- [ ] Check whether the embedding model you use (or plan to use) was trained with Matryoshka Representation Learning, and if so, what dimensionalities it supports truncating to.
- [ ] Compute the storage cost, in bytes per vector and for your actual corpus size, at your model's full dimensionality and at one smaller candidate size.
- [ ] Tomorrow: if you have a labeled or synthetic query set, measure recall at two different embedding dimensionalities and compare the quality difference against the storage difference.

## Going further

- [Paper: "Matryoshka Representation Learning", Kusupati et al., 2022](https://arxiv.org/abs/2205.13147)
- [Paper: "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks", Reimers and Gurevych, 2019](https://arxiv.org/abs/1908.10084)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
