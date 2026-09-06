---
title: 7. Stacking Transformer Blocks
description: Why every block preserves the same shape, why depth isn't weight sharing, and why lesson 5's residual machinery matters most once many blocks are stacked
type: lesson
---

# Lesson 7. Stacking Transformer Blocks

**Mission link:** Stage 3 opens the full model: a single transformer block (stages 1 and 2) is the repeating unit, and this lesson is how many of them become a model with real depth, rather than one block being the whole story.
**Primary source:** [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
**Prerequisites:** [Lesson 6](0006-feed-forward-block.md), [Scaled dot-product attention](../GLOSSARY.md)

## Warm-up

1. ▢ Does the feed-forward block ever let one position's computation see another position's vector? Contrast this with attention.

<details markdown="1"><summary>Check</summary>

No, the feed-forward block applies the same weights to each position's vector independently, with no cross-position mixing at all. Attention is the opposite: mixing information across positions is its entire purpose.

</details>

2. ▢ Why does a residual connection help train a deep stack of transformer blocks?

<details markdown="1"><summary>Check</summary>

It gives gradients a direct path through the identity `+ x` connection at every layer, regardless of what each sublayer's transformation does, keeping a usable training signal reaching even the earliest layers.

</details>

## Know this

### Every block keeps the same shape, in and out

A transformer block, attention plus its residual and layer norm, followed by the feed-forward block plus its own residual and layer norm, takes an input of dimension `d_model` and produces an output of the exact same dimension. That shape-preservation is what makes stacking meaningful at all: block 2's output can become block 3's input with no adapter or reshaping step needed, and the same holds true no matter how many blocks are stacked. A single running vector, often called the **residual stream**, simply passes through block after block, each one reading it and adding its own contribution back into it.

### Depth builds up composed representations

Each block gives the model one more round of "gather relevant information via attention, then transform it via the feed-forward block." Stacking many blocks lets progressively more composed, abstract representations build up layer by layer, the same way a deeper convolutional network builds higher-level visual features out of lower-level ones layer by layer. A single block can only do one round of gather-then-transform; a deep stack lets the model represent functions of the input a single block has no way to express on its own.

### Blocks are not weight-shared across depth

In the standard architecture, each block in the stack has its own, separately learned parameters: block 3's attention and feed-forward weights are entirely different from block 7's. This costs parameters directly, roughly linearly with depth, since nothing is being reused. What it buys in exchange is representational flexibility: different blocks are free to specialize at different levels of abstraction precisely because they aren't forced to share weights with each other, the same reasoning that lets different attention heads specialize (lesson 2) applied now across depth instead of within a single layer.

### Why lesson 5's machinery matters most here

A single block, or two, can train reasonably well even without much help. The residual connections and layer normalization from lesson 5 earn their keep specifically once depth grows large, real models commonly stack dozens of blocks or more, since that's exactly where an unaided gradient signal would otherwise shrink or explode passing through so many stacked transformations. Depth is what makes the residual and normalization machinery necessary in the first place, not an optional refinement.

## Practice

1. ▢ Why must every transformer block preserve the same input and output dimension (`d_model` in, `d_model` out)? What would break if one block in the middle of the stack changed the dimension?

<details markdown="1"><summary>Check</summary>

Stacking blocks means feeding one block's output directly into the next block's input; if a block changed the dimension, every later block (and the residual stream itself) would need to be built for a different size, breaking the uniform, drop-in stacking that lets the same block shape repeat any number of times without special-casing.

</details>

2. ▢ Are the weights in block 3 of a standard transformer stack the same as the weights in block 7? What does the answer cost in parameter count, and what does it buy in representational flexibility?

<details markdown="1"><summary>Check</summary>

No, each block has its own, independently learned parameters. This costs parameter count directly, roughly linearly with the number of blocks stacked, since nothing is shared or reused. In exchange, it lets different blocks specialize differently at different depths, rather than being forced to compute the identical transformation at every layer.

</details>

3. ▢ Why does lesson 5's residual-connection-and-layer-norm machinery matter more once many blocks are stacked (say, dozens) than it would for just one or two blocks?

<details markdown="1"><summary>Hint</summary>

Think about what happens to a gradient signal passing through many stacked transformations versus just one or two.

</details>

<details markdown="1"><summary>Check</summary>

A gradient passing through only one or two stacked transformations doesn't have much distance to shrink or explode over. Across dozens of stacked blocks, an unaided gradient signal degrades severely without a direct path back; the residual connections' identity path and layer norm's stable activation ranges are specifically what keep training possible at that depth, which is why they matter far more as depth grows.

</details>

4. ▢ Describe, in one or two sentences, the forward pass of a full stack of transformer blocks.

<details markdown="1"><summary>Check</summary>

A single running vector (the residual stream) is passed sequentially through each block in the stack, in order; each block reads the current residual stream, computes its attention and feed-forward contributions, and adds them back in, producing the residual stream that the next block reads in turn.

</details>

5. ▢ Which claim is true of stacking transformer blocks?

   - a) Each block must use different input and output dimensions so later blocks can specialize
   - b) All blocks in the stack share the exact same weights, the way a recurrent network reuses one set of weights across steps
   - c) Every block preserves the same input/output shape and has its own independently learned weights, letting blocks stack uniformly while still specializing at different depths
   - d) Residual connections and layer norm matter equally regardless of how many blocks are stacked

<details markdown="1"><summary>Check</summary>

**c)** Both properties, uniform shape and independent weights, are what make deep stacking both mechanically simple and representationally flexible. (a) is false: shape has to stay the same across blocks, not change. (b) is false: transformer blocks are not weight-tied across depth in the standard architecture. (d) is false: their value grows specifically as depth increases, since that's where an unaided gradient signal would otherwise degrade.

</details>

## Real-world reps

- [ ] Implement a stack of N transformer blocks (using your lesson 1 to 6 pieces) as a simple loop or list of block instances, and confirm the same code runs unchanged whether N is 2 or 12.
- [ ] Read nanoGPT's model definition and find where it stacks its transformer blocks, noting how the loop over blocks is written.
- [ ] Tomorrow: read how many layers the original paper's base model uses (its `N` value), and compare that depth to a real, current model's stated layer count.

## Going further

- [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Repo: nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
