---
title: 5. Layer Norm and Residual Connections
description: Why stacking many transformer blocks needs a clean gradient path and stable activation ranges, and how residuals and layer norm each provide one
type: lesson
---

# Lesson 5. Layer Norm and Residual Connections

**Mission link:** Attention alone (stages 1) doesn't stack into a deep, trainable network by itself; residual connections and layer normalization are the two pieces that make stacking many transformer blocks (stage 3) practical rather than unstable.
**Primary source:** [Paper: "Layer Normalization", Ba, Kiros, and Hinton, 2016](https://arxiv.org/abs/1607.06450)
**Prerequisites:** [Lesson 4](0004-positional-encoding.md), [Scaled dot-product attention](../GLOSSARY.md)

## Warm-up

1. ▢ Why is positional encoding needed at all, given what attention's equation computes on its own?

<details markdown="1"><summary>Check</summary>

Attention treats its input as an unordered set: swapping two positions just relabels the output without changing any computed relationship. Positional encoding injects position into the token embeddings themselves, which is the only way attention's dot products can become sensitive to order.

</details>

2. ▢ Why doesn't setting a masked position's raw score to plain 0 correctly exclude it from attention?

<details markdown="1"><summary>Check</summary>

`exp(0) = 1`, an entirely ordinary value that still competes for probability mass in softmax's denominator. Only a large negative number drives its exponential effectively to zero, which is what actually removes that position's contribution.

</details>

## Know this

### Residual connections give gradients a direct path

A transformer sublayer (attention, or the feed-forward block from the next lesson) is wrapped in a **residual connection**: the block's output is `x + Sublayer(x)`, not just `Sublayer(x)` on its own. This matters once many such blocks are stacked (stage 3's subject): without the `+ x` term, a gradient flowing backward during training has to pass through every sublayer's transformation at every layer, and in a deep stack that path can shrink toward zero or blow up, making the network hard or impossible to train well. With the residual term, gradient has a second, direct route straight through the identity `+ x` connection at every layer, regardless of what the sublayer itself is doing, which keeps a usable training signal reaching even the earliest layers of a deep stack.

### Layer normalization keeps each layer's activations in a predictable range

**Layer normalization** normalizes a single token's own activation vector, subtracting its mean and dividing by its standard deviation, computed across that vector's own features, then applying a learned scale (`gamma`) and shift (`beta`) so the network can still represent a useful range rather than being stuck at mean 0, unit variance. This differs from **batch normalization**, which instead normalizes across the batch dimension, computing statistics from many examples together. Layer norm's per-example computation matters specifically for sequence models: it works identically regardless of batch size, including a batch of one, which is exactly the case during autoregressive generation, where batch statistics computed across a single generated sequence would be meaningless or unstable.

The practical effect: layer norm keeps every sublayer's input in a similar, predictable numerical range, so a sublayer deep in a stack of many blocks isn't fed wildly different activation scales than one near the input, which stabilizes training the same way lesson 1's scaling factor kept attention scores in a range where softmax's gradient stayed usable.

### Where the norm sits: post-norm versus pre-norm

The original transformer paper places layer norm *after* the residual addition, `LayerNorm(x + Sublayer(x))`, called **post-norm**. Later work found that placing the norm *before* the sublayer, inside the residual branch instead, `x + Sublayer(LayerNorm(x))`, called **pre-norm**, trains more stably as models get much deeper. The reason: pre-norm leaves the residual path itself completely clean and unnormalized all the way through the network, an unobstructed identity connection end to end, where post-norm's placement means the residual sum itself gets normalized at every layer, muddying that clean gradient highway. This is why most current large models use pre-norm, despite the original paper's choice of post-norm.

## Practice

1. ▢ Why does a residual connection help train a deep stack of transformer blocks, in terms of what happens to gradients during backpropagation?

<details markdown="1"><summary>Check</summary>

Without a residual, a gradient flowing backward has to pass through every sublayer's transformation at every stacked layer, which can shrink or explode across many layers. The residual's `+ x` term gives gradient a second, direct path straight through the identity connection at each layer, keeping a usable signal reaching even the earliest layers regardless of what each sublayer's transformation does to it.

</details>

2. ▢ Why does layer norm's choice to normalize across the feature dimension, rather than across the batch dimension like batch norm, matter specifically for a sequence model doing autoregressive generation?

<details markdown="1"><summary>Check</summary>

Autoregressive generation commonly runs with a small batch, often batch size 1. Batch normalization computes its statistics across the batch dimension, which is meaningless or unstable with so few (or one) examples to compute statistics from. Layer norm computes its statistics from a single example's own features, so it works identically no matter how large or small the batch is.

</details>

3. ▢ Contrast post-norm and pre-norm placement, and explain why pre-norm is generally preferred for very deep models.

<details markdown="1"><summary>Hint</summary>

Think about which placement keeps the residual path itself completely unnormalized end to end.

</details>

<details markdown="1"><summary>Check</summary>

Post-norm applies layer norm after adding the residual, `LayerNorm(x + Sublayer(x))`; pre-norm applies it before the sublayer, inside the residual branch, `x + Sublayer(LayerNorm(x))`. Pre-norm leaves the residual path itself completely clean and unnormalized all the way through the network, an unobstructed identity connection end to end, while post-norm's placement normalizes the residual sum at every layer, disrupting that clean gradient path. This is why pre-norm trains more stably as depth increases.

</details>

4. ▢ A length-4 activation vector is `[2, 4, 4, 6]`. Compute its mean and variance, then the normalized (pre-scale, pre-shift) layer norm output.

<details markdown="1"><summary>Hint</summary>

Mean is the average; variance is the average squared deviation from the mean.

</details>

<details markdown="1"><summary>Check</summary>

Mean: `(2+4+4+6)/4 = 4`. Deviations from the mean: `-2, 0, 0, 2`. Variance: `(4+0+0+4)/4 = 2`. Standard deviation: `sqrt(2) ≈ 1.414`. Normalized: `[-2, 0, 0, 2] / 1.414 ≈ [-1.414, 0, 0, 1.414]`, before the learned scale (`gamma`) and shift (`beta`) are applied.

</details>

5. ▢ Which claim is true of residual connections and layer normalization in a transformer block?

   - a) Residual connections replace the need for layer normalization entirely
   - b) Layer norm always normalizes across the batch dimension, the same way batch norm does
   - c) Residual connections give gradients a direct path through a deep stack, and layer norm keeps each layer's activations in a stable, predictable range, independent of batch size
   - d) Pre-norm and post-norm placement have no effect on training stability at any depth

<details markdown="1"><summary>Check</summary>

**c)** Each piece solves a distinct problem: residuals address gradient flow across depth, layer norm addresses activation scale independent of batch size. (a) is false: they solve different problems and both appear together in a standard block. (b) is false: that's exactly what distinguishes layer norm from batch norm. (d) is false: pre-norm's advantage over post-norm shows up specifically as models get deeper.

</details>

## Real-world reps

- [ ] Implement layer normalization from raw tensor operations (mean, variance, normalize, learned scale and shift) for a small activation vector, and confirm it matches a by-hand calculation like this lesson's worked example.
- [ ] Wrap your lesson 1-3 attention implementation in a residual connection and a layer norm, choosing either pre-norm or post-norm placement, and note which one you picked and why.
- [ ] Tomorrow: read the "Layer Normalization" paper's abstract and introduction, and note what problem with batch normalization for sequence models it was originally written to solve.

## Going further

- [Paper: "Layer Normalization", Ba, Kiros, and Hinton, 2016](https://arxiv.org/abs/1607.06450)
- [Paper: "On Layer Normalization in the Transformer Architecture", Xiong et al., 2020](https://arxiv.org/abs/2002.04745)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
