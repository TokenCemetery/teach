---
title: 3. Causal Masking
description: Why a query position must not attend to future positions, and why the mask is applied before softmax, not after
type: lesson
---

# Lesson 3. Causal Masking

**Mission link:** This is stage 1's capstone: multi-head attention (lesson 2) lets every position attend to every other position, which is exactly wrong for the autoregressive generation this workspace's model will eventually do, and this lesson is the fix.
**Primary source:** [Article: "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
**Prerequisites:** [Lesson 2](0002-multi-head-attention.md), [Scaled dot-product attention](../GLOSSARY.md)

## Warm-up

1. ▢ In multi-head attention, when computing the `/ sqrt(d_k)` scaling inside one head, should `d_k` be the per-head dimension or the full model dimension?

<details markdown="1"><summary>Check</summary>

The per-head dimension (`d_model / h`). The scaling counteracts the variance growth of a dot product summed over `d_k` terms, and inside one head that dot product is summed over the head's own, smaller dimension.

</details>

2. ▢ What does the softmax step accomplish in scaled dot-product attention?

<details markdown="1"><summary>Check</summary>

It converts each query's raw similarity scores against every key into a probability distribution, non-negative and summing to 1, which is what makes the output a weighted blend of the values.

</details>

## Know this

### Why attending to the future is a problem at all

A model that generates text one token at a time produces token *N* using only tokens 1 through *N-1*; token *N+1* doesn't exist yet at that point. If self-attention during training lets position *i* attend to position *j* greater than *i*, the model can use the very token it's supposed to predict, and every token after it, as part of computing that prediction. Training loss looks great, since the model is effectively copying an answer it can already see, but the model learns nothing useful, because at actual generation time those future tokens are never available. **Causal masking** is what keeps training honest: it restricts each position to attending only to itself and earlier positions, matching exactly what will be available when the model actually generates text one token at a time.

### The mask is applied to the scores, before softmax

The fix happens inside the equation itself, before the softmax step: a mask is added to the raw `QK^T / sqrt(d_k)` scores, setting every entry where the key position is later than the query position to a very large negative number (in practice, negative infinity or something numerically equivalent, like -1e9). After that masked score passes through `exp(...)` inside softmax, a very large negative number becomes a value indistinguishable from zero, so that position contributes essentially nothing to the final weighted sum, and the remaining, unmasked positions' weights renormalize among themselves to still sum to 1.

### Why not just zero out the weights after softmax

Setting a future position's weight to zero *after* softmax has already run doesn't work correctly: the other weights were already computed assuming that position was a real competitor for probability mass, and zeroing it afterward leaves the remaining weights not summing to 1 anymore, which is not a valid probability distribution. Masking has to happen before softmax specifically so the renormalization happens automatically as part of the same computation.

### Why the raw score can't just be set to plain 0 either

Setting a future position's raw score to 0, rather than a large negative number, doesn't exclude it: `exp(0) = 1`, which is a perfectly ordinary, non-negligible contribution to the softmax denominator, not "no attention" at all. A score of 0 reads as a neutral, average similarity, competing on equal footing with every other position's actual score. Only a large enough negative number drives its exponential down to effectively zero, which is what correctly removes that position from the weighted sum.

### The mask's shape: a fixed lower-triangular pattern

For a sequence of length *n*, the causal mask is the same lower-triangular pattern every time: query position *i* is allowed to attend to key positions 0 through *i* (inclusive), and masked from every position after *i*. The same mask shape applies across every attention head and every example in a batch, added once to the score matrix before softmax runs.

## Practice

1. ▢ Why must position *i*'s attention not include any position *j* greater than *i*, given how the model will actually be used at inference time?

<details markdown="1"><summary>Check</summary>

At inference, the model generates one token at a time using only the tokens that came before it; tokens after the current position don't exist yet when it's being predicted. If training let position *i* attend to a later position *j*, the model would learn to rely on information that will never be available at actual generation time.

</details>

2. ▢ Why is the causal mask applied to the raw scores before softmax, rather than by zeroing attention weights after softmax has already run?

<details markdown="1"><summary>Check</summary>

Softmax's output weights are computed together and sum to 1 across whatever scores it was given. Zeroing a weight after the fact leaves the remaining weights summing to something less than 1, which isn't a valid probability distribution anymore. Masking before softmax, by contrast, lets the renormalization among the remaining, unmasked positions happen automatically as part of the same computation.

</details>

3. ▢ Why doesn't setting a future position's raw score to plain 0 (instead of a large negative number) correctly exclude it from attention?

<details markdown="1"><summary>Hint</summary>

Think about what `exp(0)` evaluates to, and what that means for softmax's denominator.

</details>

<details markdown="1"><summary>Check</summary>

`exp(0) = 1`, which is an entirely ordinary, non-negligible value that still competes for probability mass in softmax's denominator. A score of 0 reads as an average, neutral similarity, not "exclude this position." Only a sufficiently large negative number drives its exponential effectively to zero, which is what actually removes that position's contribution.

</details>

4. ▢ For a 4-token sequence (positions 0 to 3), which key positions can query position 2 attend to under a causal mask?

<details markdown="1"><summary>Check</summary>

Positions 0, 1, and 2. Position 3, being later than position 2, is masked out.

</details>

5. ▢ Which claim is true of how causal masking is implemented?

   - a) It zeros out attention weights after softmax has already computed them
   - b) It adds a large negative number to future positions' raw scores before softmax, so their exponentials become negligible and the remaining weights renormalize automatically
   - c) It only applies to the first attention head, since later heads don't need the restriction
   - d) Setting a future position's score to 0 is equivalent to masking it out

<details markdown="1"><summary>Check</summary>

**b)** That's exactly the mechanism, and why it has to happen before softmax. (a) is false: zeroing after softmax leaves the remaining weights not summing to 1. (c) is false: the same mask applies identically to every head. (d) is false: a score of 0 still contributes a full, ordinary weight via `exp(0) = 1`, it doesn't exclude the position at all.

</details>

## Real-world reps

- [ ] Add causal masking to your multi-head attention implementation from lesson 2: build a lower-triangular mask for a chosen sequence length and add it to the scores before softmax.
- [ ] For a small sequence, print out the softmax weights for one query position with and without the mask applied, and confirm the masked version has essentially zero weight on future positions.
- [ ] Tomorrow: read the masking section of the primary source's code alongside your own implementation, and confirm the mask is applied at the same point in the computation (before softmax, added to the scores).

## Going further

- [Article: "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
- [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
