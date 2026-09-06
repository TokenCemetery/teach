---
title: 8. Embedding and Output Layers, Weight Tying
description: How tokens enter and leave the transformer's vector space, and why the two layers that do it can share one matrix
type: lesson
---

# Lesson 8. Embedding and Output Layers, Weight Tying

**Mission link:** This is stage 3's capstone: the stacked blocks (lesson 7) operate entirely in `d_model`-dimensional vectors, so something has to convert discrete tokens into that space on the way in, and back into vocabulary scores on the way out, closing the loop from raw token IDs to a full forward pass.
**Primary source:** [Paper: "Using the Output Embedding to Improve Language Models", Press and Wolf, 2017](https://arxiv.org/abs/1608.05859)
**Prerequisites:** [Lesson 7](0007-stacking-blocks.md), [Scaled dot-product attention](../GLOSSARY.md)

## Warm-up

1. ▢ Why must every transformer block preserve the same input and output dimension (`d_model` in, `d_model` out)?

<details markdown="1"><summary>Check</summary>

Stacking means one block's output feeds directly into the next block's input; if a block changed the dimension, every later block and the residual stream would need to be built for a different size, breaking the uniform stacking that lets the same block shape repeat any number of times.

</details>

2. ▢ Are the weights in one block of a standard transformer stack the same as the weights in another block? What does that cost, and what does it buy?

<details markdown="1"><summary>Check</summary>

No, each block has its own independently learned parameters. This costs parameter count roughly linearly with depth, since nothing is shared, but it lets different blocks specialize differently at different depths rather than all computing the identical transformation.

</details>

## Know this

### The input embedding: a lookup from token ID to vector

A tokenizer (named in passing here; `llm/finetuning`'s territory to derive further) produces a sequence of integer token IDs, each an index into a fixed vocabulary. The **input embedding layer** is a learned matrix of shape `vocab_size × d_model`: row `i` is the dense vector representation of token `i`. Looking up a token's embedding is simply reading its row. This is where discrete, symbolic tokens enter the continuous vector space every later piece, attention, the feed-forward block, positional encoding, actually operates on.

### The output layer: projecting back to vocabulary scores

After the final stacked block produces its output, still `d_model`-dimensional per position, the model needs one more step to turn that vector back into a prediction over the vocabulary. The **output layer** is a linear projection of shape `d_model × vocab_size`, producing one raw score, called a **logit**, per vocabulary token at each position. Those logits (turned into a probability distribution by the next lesson's cross-entropy loss) are what "predict the next token" actually means numerically: a vector of vocabulary-sized scores, one per possible token.

### The two layers' shapes are transposes of each other

The input embedding matrix is `vocab_size × d_model`; the output projection is `d_model × vocab_size`, exactly the transpose shape. **Weight tying** takes advantage of this directly: instead of learning a wholly separate output matrix, the model reuses the same embedding matrix, transposed, to compute output logits (`logits = h @ W_embedding^T`). This isn't just a coincidence being exploited for convenience; both layers relate a token to essentially the same underlying question, the input embedding answers "what vector represents token X," and the output layer answers "how likely is token X," and tying treats those as sharing one representation rather than learning two separate, unrelated ones.

### What tying actually saves

For a vocabulary of 50,000 tokens and `d_model = 768`, the embedding table alone holds `50,000 × 768 = 38,400,000` parameters. An untied model would need a second matrix of the same size for the output projection, another 38.4 million parameters doing a closely related job. Tying eliminates that entire second matrix, and for models with large vocabularies relative to their hidden size, that's a substantial fraction of the model's total parameter count saved for essentially no loss, and often a measurable gain, in quality.

## Practice

1. ▢ What shape is the input embedding layer's weight matrix, and what does looking up a specific token's embedding correspond to structurally?

<details markdown="1"><summary>Check</summary>

`vocab_size × d_model`. Looking up a token's embedding is reading the row of the matrix at that token's index, a direct lookup rather than a computed transformation.

</details>

2. ▢ How does the output layer's shape relate to the input embedding layer's shape, and what does that relationship make possible?

<details markdown="1"><summary>Check</summary>

The output layer's shape (`d_model × vocab_size`) is the transpose of the input embedding's shape (`vocab_size × d_model`). That relationship is what makes weight tying possible: the same matrix, used one way as a lookup table and the other way (transposed) as a projection, can serve both roles instead of needing two separately learned matrices.

</details>

3. ▢ For a vocabulary of 50,000 tokens and `d_model = 768`, compute the embedding table's parameter count, and explain what weight tying saves relative to an untied model.

<details markdown="1"><summary>Hint</summary>

The embedding table's parameter count is `vocab_size × d_model`. An untied output layer would need a matrix of the same size.

</details>

<details markdown="1"><summary>Check</summary>

`50,000 × 768 = 38,400,000` parameters for the embedding table. An untied model would need a second, separately learned matrix of that same size for the output projection; tying eliminates that entire second matrix, saving roughly 38.4 million parameters for this vocabulary and hidden size.

</details>

4. ▢ Beyond saving parameters, what's the underlying reasoning for why tying the input and output weight matrices makes sense, rather than just being a convenient trick?

<details markdown="1"><summary>Check</summary>

Both layers relate a token to fundamentally the same representation: the input embedding answers "what vector represents this token," and the output layer answers "how likely is this token, given the current representation." Since both questions are about the same token-to-vector relationship, sharing one learned representation between them is a reasonable inductive bias, not merely a way to cut parameters.

</details>

5. ▢ Which claim is true of the input embedding and output layers?

   - a) They must always be learned as two entirely separate matrices, since they serve unrelated purposes
   - b) Their shapes are transposes of each other, which is what makes weight tying, reusing one matrix for both, possible
   - c) Weight tying only saves parameters and provides no other benefit
   - d) The output layer's shape depends on `vocab_size` alone, with no relationship to `d_model`

<details markdown="1"><summary>Check</summary>

**b)** The transposed-shape relationship is exactly what tying exploits. (a) is false: that's precisely what tying avoids needing. (c) is false: tying is also argued to help quality, since both layers relate to the same underlying token representation. (d) is false: the output layer's shape is `d_model × vocab_size`, depending on both.

</details>

## Real-world reps

- [ ] Implement the input embedding lookup and the output projection as separate matrices first, then modify your implementation to tie them and confirm the output logits' shape is unchanged.
- [ ] For a model you're familiar with, look up its vocabulary size and `d_model`, and compute how many parameters weight tying would save compared to an untied version.
- [ ] Tomorrow: check whether a real model implementation you have access to (in the `transformers` library or elsewhere) ties its embedding and output weights, and find where that's configured in the code.

## Going further

- [Paper: "Using the Output Embedding to Improve Language Models", Press and Wolf, 2017](https://arxiv.org/abs/1608.05859)
- [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
