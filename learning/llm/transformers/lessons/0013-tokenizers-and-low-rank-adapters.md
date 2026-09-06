---
title: 13. Tokenizers and Low-Rank Adapters
description: Deriving byte-pair encoding, and where a low-rank adapter actually attaches to a weight matrix this workspace built from scratch
type: lesson
---

# Lesson 13. Tokenizers and Low-Rank Adapters

**Mission link:** This is the final lesson of the arc: `llm/finetuning` names tokenizers and the low-rank idea in passing, this workspace derives them, the tokenizer's algorithm itself and the exact place a low-rank update attaches to a weight matrix this workspace built from raw tensors.
**Primary source:** [Paper: "Neural Machine Translation of Rare Words with Subword Units", Sennrich, Haddow, and Birch, 2016](https://arxiv.org/abs/1508.07909)
**Prerequisites:** [Lesson 12](0012-reading-real-model-code.md), [Scaled dot-product attention](../GLOSSARY.md)

## Warm-up

1. ▢ Name the three common small deviations from the original paper found in most modern real implementations.

<details markdown="1"><summary>Check</summary>

Learned or rotary position embeddings instead of sinusoidal, GELU instead of ReLU in the feed-forward block, and pre-norm instead of post-norm placement.

</details>

2. ▢ Why must every transformer block preserve the same input and output dimension?

<details markdown="1"><summary>Check</summary>

Stacking means one block's output feeds directly into the next block's input; a block that changed the dimension would break the uniform, drop-in stacking that lets the same block shape repeat any number of times.

</details>

## Know this

### Deriving the tokenizer: byte-pair encoding

`llm/finetuning` treats the tokenizer as something a model already ships with, noting only that modern models use subword tokenization, built by "starting from bytes and repeatedly merging the most frequent adjacent pair." Here is that algorithm, in full: **byte-pair encoding (BPE)** starts by representing every piece of training text as a sequence of raw bytes (or characters), each its own vocabulary entry. It then repeats one step: count every adjacent pair of symbols across the whole corpus, find the single most frequent pair, and merge it into one new symbol, added to the vocabulary. This repeats until the vocabulary reaches a chosen target size.

A tiny worked example: given the corpus `"low low lower"` (spaces mark word boundaries, kept separate), starting from individual characters, the pair `l, o` might be the most frequent adjacent pair across the corpus, so it merges into a new symbol `lo`. The next round finds the next most frequent pair among the updated symbols, `lo, w`, and merges that into `low`. Each merge round shrinks how many symbols represent common substrings and grows the vocabulary by exactly one entry. Iterating this enough times produces a vocabulary where frequent words compress to a single token and rare words fall back to smaller, more frequent pieces, exactly the property `llm/finetuning`'s tokenizer coverage observed: "tokens are not words."

This is also where lesson 8's `vocab_size` actually comes from: it's however many merges (plus the starting symbols) the tokenizer's training was run for, fixed once training finishes, and the input embedding and output layers this workspace derived are sized to whatever number that training produced.

### Deriving the low-rank idea: where it attaches to a real weight matrix

`llm/finetuning`'s own coverage of the low-rank idea already derives the mechanism in full: freeze a weight matrix `W₀`, and instead of learning a full update for it, factor the update into two small matrices, `ΔW = BA`, with `A` projecting down to a small rank `r` and `B` projecting back up, so `h = W₀x + (α/r) BAx`. What that coverage doesn't need to show, because its mission is the adapter, not the architecture underneath it, is exactly which matrix `W₀` is, concretely, inside a transformer this workspace built from raw tensors.

Take lesson 2's per-head query projection, `W_Q^i`, one of the learned matrices producing `Q_i = X W_Q^i`. Applying a low-rank adapter to it means freezing `W_Q^i` exactly as it was after pretraining, and computing:

```text
Q_i = X (W_Q^i + (α / r) B_i A_i)
```

`A_i` and `B_i` are new, small matrices, sized by rank `r`, and only they receive gradients during adapter training; `W_Q^i` never changes. Everything downstream, the rest of attention, layer norm, the feed-forward block, stacking, the output layer, runs exactly as this workspace derived it, entirely unaware that `Q_i` came from a frozen matrix plus a small additive correction rather than a single learned matrix. That's the concrete answer to "where does a low-rank adapter attach": at the exact same matrix multiply this workspace wrote out from raw tensors in lesson 2, with one term of that multiply split into a frozen part and a trainable low-rank part.

Because the update is additive and linear in exactly the same way lesson 2's projection itself is linear, `W_Q^i + (α/r) B_i A_i` collapses into one ordinary matrix after training, which is `llm/finetuning`'s point about zero inference overhead: nothing about the forward pass this workspace built has to change to serve a merged adapter, since the merged result is just another `W_Q^i`.

## Practice

1. ▢ Starting from the corpus `"low low lower"` represented as individual characters, describe what the first merge step of byte-pair encoding does, in general terms.

<details markdown="1"><summary>Check</summary>

Count every adjacent pair of symbols across the corpus, find whichever pair occurs most frequently (for example, `l` followed by `o`), and merge that pair into one new symbol, adding it to the vocabulary. Every future occurrence of that adjacent pair in the corpus is now represented by the single new symbol instead of two separate ones.

</details>

2. ▢ How does the tokenizer's training determine `vocab_size`, and what does that number then fix inside the model architecture this workspace derived?

<details markdown="1"><summary>Check</summary>

`vocab_size` is however many starting symbols plus merge steps the tokenizer's BPE training was run for, fixed once that training finishes. That number then sizes lesson 8's input embedding table and output projection layer directly, since both are shaped by `vocab_size`.

</details>

3. ▢ Using lesson 2's per-head query projection `Q_i = X W_Q^i`, write the modified computation once a low-rank adapter is attached to `W_Q^i`, and state which matrices receive gradients during adapter training.

<details markdown="1"><summary>Hint</summary>

The frozen matrix and the low-rank correction are both part of the same multiply.

</details>

<details markdown="1"><summary>Check</summary>

`Q_i = X (W_Q^i + (α/r) B_i A_i)`. Only `A_i` and `B_i` receive gradients; `W_Q^i` stays frozen throughout adapter training.

</details>

4. ▢ Why does `W_Q^i + (α/r) B_i A_i` collapse into a single ordinary matrix after training, and what does that mean for the forward pass this workspace derived?

<details markdown="1"><summary>Check</summary>

Both the frozen matrix and the low-rank correction are linear, additive terms in the same matrix multiply, so their sum is just another matrix of the same shape as `W_Q^i`. Nothing about the forward pass this workspace built has to change to use it: the merged result plugs directly into `Q_i = X W_Q^i` as an ordinary projection matrix, with zero added computation at inference time.

</details>

5. ▢ Which claim is true of how this workspace's derivations connect to `llm/finetuning`'s coverage of tokenizers and low-rank adapters?

   - a) `llm/finetuning` and this workspace teach the exact same content, so one is redundant
   - b) This workspace derives the mechanisms (BPE's merge algorithm, the exact matrix a low-rank update attaches to) that `llm/finetuning` names in passing without deriving
   - c) A low-rank adapter can only attach to the output layer, never to an attention projection
   - d) `vocab_size` is chosen independently of the tokenizer and has no effect on the embedding or output layers

<details markdown="1"><summary>Check</summary>

**b)** That's precisely the boundary this workspace's mission drew from the start. (a) is false: `llm/finetuning` covers why and when to use these techniques; this workspace covers the mechanism and where it attaches. (c) is false: this lesson attached a low-rank update to an attention projection (`W_Q^i`) specifically, though it can attach to other weight matrices too. (d) is false: `vocab_size` comes directly from the tokenizer's training and fixes both the embedding table and output layer's shapes.

</details>

## Real-world reps

- [ ] Run a byte-pair encoding merge step by hand on a short piece of text you choose, tracking the pair counts and the resulting vocabulary after two or three merges.
- [ ] In your from-scratch transformer implementation, add a low-rank adapter to one attention projection matrix, freezing the original and training only the new `A` and `B` matrices.
- [ ] Tomorrow: revisit this workspace's mission in `README.md` and confirm, in your own words, that you can implement a full transformer's forward pass and training loop from raw tensors, and locate each derived piece in real model code.

## Going further

- [Paper: "Neural Machine Translation of Rare Words with Subword Units", Sennrich, Haddow, and Birch, 2016](https://arxiv.org/abs/1508.07909)
- [Adapter](../../finetuning/GLOSSARY.md): `llm/finetuning`'s canonical term for the frozen-base-plus-small-trainable-weights pattern this lesson attaches to a concrete matrix
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
