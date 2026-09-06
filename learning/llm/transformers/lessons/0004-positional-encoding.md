---
title: 4. Positional Encoding
description: Why attention is blind to order on its own, and how sinusoidal encoding gives every position a distinguishable signature
type: lesson
---

# Lesson 4. Positional Encoding

**Mission link:** Stage 2 opens the pieces that surround attention (lessons 1 to 3) to make it into a full transformer block; positional encoding is the first of them, and without it, attention would be blind to the one thing language depends on most: order.
**Primary source:** [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
**Prerequisites:** [Lesson 3](0003-causal-masking.md), [Scaled dot-product attention](../GLOSSARY.md)

## Warm-up

1. ▢ Why is the causal mask applied to the raw scores before softmax, rather than by zeroing weights after softmax has already run?

<details markdown="1"><summary>Check</summary>

Softmax's weights are computed together and already sum to 1; zeroing one afterward leaves the rest not summing to 1 anymore. Masking before softmax lets the remaining, unmasked weights renormalize automatically as part of the same computation.

</details>

2. ▢ Write the scaled dot-product attention equation from memory.

<details markdown="1"><summary>Check</summary>

`Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V`.

</details>

## Know this

### Attention has no notion of order built in

Scaled dot-product attention computes its output from dot products between queries and keys, weighted sums over values, nothing in that computation references where a token sits in the sequence. Swap the positions of two input tokens (and correspondingly, the rows of `Q`, `K`, and `V` that came from them), and every other position's attention output is identical, just relabeled to match the swap: the actual content-based relationships and weights the computation produces don't change at all. Attention treats its input as an unordered set of vectors, not a sequence, even though language plainly isn't order-independent: "dog bites man" and "man bites dog" share every word and mean something entirely different.

### Position has to be baked into the vectors themselves

Attention's equation only ever sees `Q`, `K`, and `V`; there's no side channel for "and by the way, here's what position each of these came from." The only way attention becomes sensitive to position at all is if position is already encoded inside the vectors that produce `Q`, `K`, and `V` in the first place, meaning inside the token embeddings before they ever reach the attention computation. A **positional encoding** vector, added to each token's embedding, gives two tokens with the identical word but different positions numerically distinguishable embeddings, which is what lets attention's dot products end up implicitly sensitive to position.

### Sinusoidal encoding: a unique, structured signature per position

The original paper's choice constructs each position's encoding from sine and cosine functions at different frequencies, one pair of dimensions per frequency:

```text
PE(pos, 2i)   = sin(pos / 10000^(2i / d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i / d_model))
```

Low-index dimension pairs (small `i`) oscillate slowly across positions (a long wavelength); high-index pairs oscillate quickly (a short wavelength). Every position gets a unique combination across all these frequencies, and critically, a fixed offset between two positions can be expressed as a linear function of the encoding at one of them (since `sin` and `cos` of a sum decompose into linear combinations of `sin` and `cos` of the parts). That structure is part of why the paper argues this scheme can generalize to relative position, and potentially to sequence lengths not seen during training, rather than only memorizing a fixed set of absolute positions.

### The simpler alternative: a learned position embedding

Instead of a fixed formula, a position can be encoded with an ordinary learned embedding table, indexed by position the same way a token embedding table is indexed by vocabulary, and trained by gradient descent like any other parameter. This is simpler to implement and requires no frequency reasoning, but it has no formula to fall back on for a position beyond whatever the table was sized for during training: there's no row in the table for a position the model never saw, where sinusoidal encoding's formula can still be evaluated at any position at all.

## Practice

1. ▢ Two input tokens are swapped in position (and their corresponding rows in `Q`, `K`, `V` swapped along with them). What happens to a third position's attention output that queries both of them?

<details markdown="1"><summary>Check</summary>

Nothing about the actual content-based weights or the computed output changes; the result is simply relabeled to track which physical position the swapped tokens now occupy. This demonstrates attention's permutation invariance: it computes relationships based on content (the dot products), with no reference to position at all.

</details>

2. ▢ Why must position be encoded into the token embeddings themselves, rather than passed to the attention computation as some separate signal alongside `Q`, `K`, and `V`?

<details markdown="1"><summary>Check</summary>

Attention's equation only ever operates on `Q`, `K`, and `V`; there's no additional input for position information to enter through. The only way the computation can become sensitive to position is if position is already baked into the vectors that produce `Q`, `K`, and `V` before attention runs.

</details>

3. ▢ Describe the frequency structure across sinusoidal positional encoding's dimension pairs, and what it buys compared to just using the raw position integer directly.

<details markdown="1"><summary>Hint</summary>

Think about what varying the frequency across dimension pairs achieves that a single raw number couldn't.

</details>

<details markdown="1"><summary>Check</summary>

Different dimension pairs oscillate at different frequencies, from slow (low index) to fast (high index) across positions, giving every position a unique combination of values across all the frequencies rather than one raw scalar. This structured, multi-frequency encoding is also what lets a fixed positional offset be expressed as a linear function of another position's encoding, a property a single raw integer wouldn't have in a form attention's linear operations could exploit as directly.

</details>

4. ▢ Why can sinusoidal positional encoding be evaluated for a sequence length longer than anything seen during training, where a learned position embedding table cannot?

<details markdown="1"><summary>Check</summary>

Sinusoidal encoding is a formula, evaluable at any position value at all, including ones never encountered during training. A learned embedding table only has rows for the positions it was sized and trained for; a position beyond that range has no corresponding row to look up.

</details>

5. ▢ Which claim is true of why positional encoding exists?

   - a) Attention's dot products already account for relative position without any extra input
   - b) Attention treats its input as an unordered set, so position has to be injected into the embeddings for the model to be sensitive to word order at all
   - c) Positional encoding is only needed for very long sequences, not short ones
   - d) A learned position embedding generalizes better to unseen sequence lengths than sinusoidal encoding does

<details markdown="1"><summary>Check</summary>

**b)** That's the entire reason positional encoding exists at all. (a) is false: attention's equation has no reference to position whatsoever on its own. (c) is false: even a short sequence's meaning depends on word order, so the same blindness applies regardless of length. (d) is false: it's the reverse, sinusoidal encoding's formula can be evaluated at any position, where a learned table is fixed to what it was trained with.

</details>

## Real-world reps

- [ ] Implement sinusoidal positional encoding from the formula for a small `d_model`, and plot or print a few positions' encoding vectors to see the different oscillation frequencies across dimension pairs.
- [ ] Add your positional encoding to a set of token embeddings and confirm that the same token at two different positions now produces numerically different vectors.
- [ ] Tomorrow: read the "Positional Encoding" section of the primary source paper in full, and check the claim about generalizing to longer sequences against what your own implementation would actually produce beyond its training range.

## Going further

- [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Article: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
