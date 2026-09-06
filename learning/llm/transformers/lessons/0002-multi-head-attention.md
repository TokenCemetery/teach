---
title: 2. Multi-Head Attention
description: Why attention runs in several smaller subspaces at once rather than one at full dimension
type: lesson
---

# Lesson 2. Multi-Head Attention

**Mission link:** Lesson 1's equation is the operation; this lesson is how the transformer actually uses it, running it several times in parallel on different learned projections of the same input, rather than once at full dimension.
**Primary source:** [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
**Prerequisites:** [Lesson 1](0001-scaled-dot-product-attention.md), [Scaled dot-product attention](../GLOSSARY.md)

## Warm-up

1. ▢ Write the scaled dot-product attention equation from memory.

<details markdown="1"><summary>Check</summary>

`Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V`.

</details>

2. ▢ Why does the `/ sqrt(d_k)` scaling matter as `d_k` grows?

<details markdown="1"><summary>Check</summary>

The variance of the raw dot-product scores grows with `d_k`, which pushes softmax toward a near-one-hot output where its gradient is nearly flat. Dividing by `sqrt(d_k)` counteracts that growth, keeping scores in a range where softmax's gradient is still usable.

</details>

## Know this

### One attention operation gives one view

Scaled dot-product attention, computed once over the full input, produces exactly one weighted blend per query, one "view" of how each position relates to every other position. That's a real limitation: a sentence's structure carries multiple, different kinds of relationships at once (which word a pronoun refers to, which words are syntactically linked, which words are simply nearby), and forcing all of that into a single attention pattern per position means averaging relationships together that might be better kept separate.

### Project into several smaller subspaces, attend in each separately

**Multi-head attention** fixes this by running attention several times in parallel, each time on its own, separately learned projection of the input. For `h` heads, each head `i` gets its own learned weight matrices `W_Q^i`, `W_K^i`, `W_V^i`, projecting the input down to a smaller dimension `d_k = d_model / h`:

```text
Q_i = X W_Q^i,   K_i = X W_K^i,   V_i = X W_V^i
head_i = Attention(Q_i, K_i, V_i)
```

Each head applies lesson 1's exact equation, just inside its own lower-dimensional subspace. Because each head's projection matrices are learned independently, different heads are free to specialize, one might end up tracking nearby-word relationships, another something more syntactic, without anything forcing them to agree on a single shared attention pattern.

### Concatenate the heads, then project once more

The heads' outputs are concatenated back together and passed through one final learned projection, `W_O`, back to the model's full dimension:

```text
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) W_O
```

The final projection isn't optional decoration: concatenation alone just places each head's output side by side in a bigger vector, with no way for information from one head to combine with another. `W_O` is what lets the model learn how to blend the different heads' separate views back into a single, unified representation for whatever comes next in the network.

### The per-head dimension is what the scaling formula actually uses

Since each head operates at `d_k = d_model / h`, not the full `d_model`, lesson 1's `/ sqrt(d_k)` scaling uses that smaller, per-head dimension. This matters because it's easy to assume the scaling should track the model's overall size; it doesn't, it tracks whatever dimension the dot products inside that specific attention computation are actually summed over, which is the per-head dimension once attention is split across heads.

## Practice

1. ▢ A model has `d_model = 512` and uses 8 attention heads. What is `d_k`, the dimension each head operates in?

<details markdown="1"><summary>Check</summary>

`d_k = 512 / 8 = 64`.

</details>

2. ▢ Why is a final linear projection (`W_O`) applied after concatenating the heads' outputs, rather than just using the concatenated vector directly?

<details markdown="1"><summary>Check</summary>

Concatenation alone places each head's output side by side with no interaction between them. `W_O` lets the model learn how to combine information across the separate heads into one unified representation, rather than leaving the heads' outputs as disconnected chunks of a larger vector.

</details>

3. ▢ Why can different heads end up specializing in different kinds of relationships between positions, when all of them apply the exact same attention equation?

<details markdown="1"><summary>Check</summary>

Each head has its own, independently learned projection matrices (`W_Q^i`, `W_K^i`, `W_V^i`). Two heads applying the identical equation to differently projected versions of the same input can attend to entirely different aspects of the input, since the projections themselves shape what each head's queries and keys actually represent.

</details>

4. ▢ A model splits attention across `h` heads, each operating at `d_k = d_model / h`. When computing the `/ sqrt(d_k)` scaling inside one head's attention computation, should `d_k` be the per-head dimension or the full `d_model`? Why?

<details markdown="1"><summary>Hint</summary>

Ask what dimension the dot products being scaled are actually summed over.

</details>

<details markdown="1"><summary>Check</summary>

The per-head dimension. Lesson 1's scaling exists to counteract the variance growth of a dot product summed over `d_k` terms; inside one head, that dot product is summed over the head's own dimension, `d_model / h`, not the full model dimension. Using the wrong (full) dimension would under-scale the scores relative to what that head's own dot products actually need.

</details>

5. ▢ Which claim is true of multi-head attention compared to computing attention once at the full model dimension?

   - a) Multi-head attention runs attention once, then artificially splits the single output into pieces afterward
   - b) Each head has its own learned projections and computes attention independently in a smaller subspace, before all heads are concatenated and projected back
   - c) All heads share the same query, key, and value projection matrices, differing only in which positions they attend to
   - d) The final projection `W_O` is optional and can be skipped without changing what the model can represent

<details markdown="1"><summary>Check</summary>

**b)** That's exactly the mechanism this lesson describes. (a) is false: each head computes its own full attention operation independently, on its own projected inputs, not a post-hoc split of one shared computation. (c) is false: each head's projection matrices are learned independently, which is what lets heads specialize. (d) is false: without `W_O`, concatenated heads have no way to combine information across each other.

</details>

## Real-world reps

- [ ] Implement multi-head attention from raw tensor operations: per-head linear projections, lesson 1's attention equation applied independently per head, concatenation, and the final `W_O` projection. Confirm the output shape matches `d_model` regardless of how many heads you choose.
- [ ] For a small `d_model` and two different head counts (say 2 and 8), compute `d_k` for each and note how it shrinks as head count grows.
- [ ] Tomorrow: read the "Multi-Head Attention" section of the primary source paper in full, and check that every matrix in its equations matches something you named in your own implementation.

## Going further

- [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Article: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
