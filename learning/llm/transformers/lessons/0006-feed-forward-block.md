---
title: 6. The Position-Wise Feed-Forward Block
description: What the transformer block's second sublayer adds beyond attention, and why it never mixes information across positions
type: lesson
---

# Lesson 6. The Position-Wise Feed-Forward Block

**Mission link:** This is stage 2's capstone: attention (stages 1) and layer norm plus residuals (lesson 5) still leave one job undone, giving each position real nonlinear computing capacity of its own, which is exactly what this lesson's sublayer does.
**Primary source:** [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
**Prerequisites:** [Lesson 5](0005-layer-norm-and-residuals.md), [Scaled dot-product attention](../GLOSSARY.md)

## Warm-up

1. ▢ Why does a residual connection help train a deep stack of transformer blocks?

<details markdown="1"><summary>Check</summary>

It gives gradients a direct path through the identity `+ x` connection at every layer, regardless of what each sublayer's transformation does, keeping a usable training signal reaching even the earliest layers of a deep stack.

</details>

2. ▢ Why does layer norm normalize across each example's own features rather than across the batch, and why does that matter for autoregressive generation?

<details markdown="1"><summary>Check</summary>

Autoregressive generation often runs with a small batch, sometimes batch size 1, where batch statistics would be meaningless or unstable. Layer norm computes its statistics from a single example's own features, so it works identically regardless of batch size.

</details>

## Know this

### Attention's mixing step is actually linear

Attention computes a softmax-weighted sum of value vectors: nonlinear weights, applied to values, but the mapping from the value vectors to the output, given those weights, is a linear combination. Attention decides *where to look*, mixing information across positions, but it does not give the network a genuinely nonlinear way to reshape what a single position's own representation actually contains.

### The feed-forward block: what to do with what was gathered

The **position-wise feed-forward network (FFN)** is the transformer block's second sublayer, and it's a small two-layer network applied identically, same weights, to every position separately:

```text
FFN(x) = max(0, x W1 + b1) W2 + b2
```

(the original paper uses ReLU as its nonlinearity here; later architectures commonly swap in variants like GELU or SwiGLU, but the shape, expand, apply a nonlinearity, project back down, stays the same). This is where the network gets real nonlinear transformation capacity for a single position's own vector, complementing attention's job of mixing across positions with a distinct job: refining what a position now holds, after attention has already decided what to gather.

### Expand, then contract

The first layer projects from `d_model` up to a larger hidden dimension `d_ff`, commonly four times `d_model` (512 to 2048 in the original paper), and the second layer projects back down to `d_model` so the result can still be added into the residual stream. That expansion gives the network a much larger intermediate space to compute in for each position, before compressing back to the size the rest of the block, and the next block stacked on top of it, expects.

### Position-wise means exactly that: no cross-position mixing, ever

The same weight matrices `W1`, `b1`, `W2`, `b2` are applied separately to every position's own vector; token position 3's computation through the FFN never sees token position 5's vector, and vice versa. This is the precise complement to attention, which is the only sublayer in the block that lets information move between positions at all. A transformer block's clean division of labor: attention decides where to look and mixes across positions; the feed-forward block decides what to do with a position's own gathered representation, entirely independently of every other position.

## Practice

1. ▢ A model has `d_model = 512`. Using the original paper's 4x expansion ratio, what is `d_ff`, and describe the dimensional shape the feed-forward block's two layers take.

<details markdown="1"><summary>Check</summary>

`d_ff = 4 × 512 = 2048`. The first layer projects from 512 up to 2048, a nonlinearity is applied, and the second layer projects back down from 2048 to 512, so the output can still be added into the residual stream at the original `d_model` size.

</details>

2. ▢ Why is attention's value-mixing step considered linear, despite the nonlinear softmax used to compute its weights, and why does that make the feed-forward block necessary?

<details markdown="1"><summary>Check</summary>

Once softmax has produced the weights, the actual output is a weighted sum (a linear combination) of the value vectors; the nonlinearity lives entirely in how the weights were computed, not in how they're applied to the values. This means attention alone never gives the network a way to nonlinearly reshape a position's own representation, which is exactly the job the feed-forward block's nonlinearity performs instead.

</details>

3. ▢ Does token position 3's feed-forward computation ever use information from token position 5's vector? Contrast this with what the attention sublayer does.

<details markdown="1"><summary>Check</summary>

No. The feed-forward block applies the same weight matrices to each position's own vector independently, with no mechanism for one position's computation to see another's vector at all. Attention is the opposite: its entire purpose is mixing information across positions, computing each query's output as a weighted blend of every position's value vector.

</details>

4. ▢ Suppose a transformer block had only attention sublayers stacked many times, with no feed-forward block at all. What capability would be missing?

<details markdown="1"><summary>Hint</summary>

Consider what kind of transformation attention alone can and can't apply to a single position's own representation.

</details>

<details markdown="1"><summary>Check</summary>

The network would have no genuinely nonlinear way to reshape or refine what a single position's own representation contains; it could only ever recombine value vectors linearly across positions, stacked repeatedly. It would be missing the per-position computing capacity, feature extraction and transformation done independently of other positions, that the feed-forward block's nonlinearity specifically provides.

</details>

5. ▢ Which claim is true of the position-wise feed-forward block?

   - a) It mixes information across positions, the same way attention does
   - b) It applies the same two-layer network, with a nonlinearity, to each position's vector independently, with no cross-position mixing
   - c) Its hidden dimension is always smaller than `d_model`, to reduce computation
   - d) It replaces the need for attention entirely once stacked deep enough

<details markdown="1"><summary>Check</summary>

**b)** That's exactly its role and mechanism. (a) is false: attention is the only sublayer that mixes across positions; the feed-forward block never does. (c) is false: the hidden dimension is typically expanded, commonly 4x `d_model`, not shrunk. (d) is false: the two sublayers do different, complementary jobs, neither substitutes for the other.

</details>

## Real-world reps

- [ ] Implement the position-wise feed-forward block from raw tensor operations (two linear layers with a nonlinearity between them), and confirm its output shape matches its input shape (`d_model` in, `d_model` out).
- [ ] Combine lessons 1 to 6 into a single transformer block: attention with residual and layer norm, followed by the feed-forward block with its own residual and layer norm.
- [ ] Tomorrow: read the "Position-wise Feed-Forward Networks" section of the primary source paper in full, and check its stated `d_ff` value against the ratio you computed in practice question 1.

## Going further

- [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Article: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
