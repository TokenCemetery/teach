---
title: 1. Scaled Dot-Product Attention
description: The one equation the rest of the architecture is built around
type: lesson
---

# Lesson 1. Scaled Dot-Product Attention

**Mission link:** "Build attention from scratch" starts with the single equation every later piece (multi-head attention, the transformer block) wraps around. Nothing past this lesson makes sense until this operation does.
**Primary source:** [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
**Prerequisites:** none

## Know this

### Attention as a soft lookup

Attention takes three inputs: a **query** vector, a set of **key** vectors, and a set of **value** vectors, one key paired with each value. It compares the query against every key to get a score per key, turns those scores into weights that sum to 1, then returns the weighted sum of the values using those weights.

That's the whole idea: a lookup table where, instead of finding one exact matching key and returning its value, you blend every value together, weighted by how well each key matched the query. A hard lookup returns one value. Attention returns a blend, and it's differentiable, which is what lets it sit inside a network trained by gradient descent.

### The equation

For a set of queries, keys and values packed into matrices `Q`, `K`, `V` (one row per query, key or value), scaled dot-product attention is:

`Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V`

Reading it left to right:

- `QK^T` computes every query's dot product against every key. A dot product is large when two vectors point in a similar direction, so this step produces one similarity score per query-key pair.
- `/ sqrt(d_k)` scales those scores down, where `d_k` is the dimension of each key vector. This step exists for a specific, checkable reason (below), not as a stylistic choice.
- `softmax(...)` turns each query's row of scores into a probability distribution: non-negative, summing to 1.
- Multiplying by `V` uses those per-query weight distributions to compute a weighted sum of the value vectors. That weighted sum is the output for each query.

### Why the scaling factor matters

Assume the entries of `Q` and `K` are roughly independent with variance 1. Each dot product `q · k` sums `d_k` such products, so its variance grows with `d_k`, meaning the raw scores get larger in magnitude as the key dimension grows.

Large-magnitude scores push softmax toward a near-one-hot output: one weight close to 1 and the rest close to 0. That sounds harmless, but it puts softmax in a region where its gradient is nearly flat, so the network gets almost no learning signal from that attention step. Dividing by `sqrt(d_k)` counteracts the variance growth, keeping scores in a range where softmax's gradient is actually usable regardless of how large `d_k` is.

### Why it's called "self"-attention specifically here

In this lesson, `Q`, `K`, and `V` are just given inputs; where they come from isn't the point yet, that's next lesson's linear projections. When they come from the same sequence (each position attending to every position in the same input, including itself), the mechanism is called **self-attention**. That's the case this workspace builds first.

## Practice

1. ▢ In one sentence, what does the softmax step accomplish in scaled dot-product attention?

<details markdown="1"><summary>Check</summary>

It converts each query's raw similarity scores against every key into a probability distribution (non-negative, summing to 1), which is what lets the output be a weighted blend of the values rather than an unbounded sum.

</details>

2. ▢ A single query `q = [1, 0]` attends over two keys `k1 = [1, 0]` and `k2 = [0, 1]`, paired with values `v1 = [10, 0]` and `v2 = [0, 20]`. `d_k = 2`. Predict which value the output leans toward before computing anything, then work out the scaled scores, the softmax weights, and the final output.

<details markdown="1"><summary>Hint</summary>

Compute `q · k1` and `q · k2` first, then divide both by `sqrt(2)` before applying softmax.

</details>

<details markdown="1"><summary>Check</summary>

`q · k1 = 1`, `q · k2 = 0`. Scaled: `1 / sqrt(2) ≈ 0.71` and `0`.

Softmax([0.71, 0]) ≈ [0.67, 0.33].

Output ≈ `0.67 × [10, 0] + 0.33 × [0, 20] ≈ [6.70, 6.60]`.

The query aligns more with `k1` (dot product 1 vs. 0), so the output leans toward `v1`, but not overwhelmingly: the scores were close enough that both values contribute a meaningful share.

</details>

3. ▢ A colleague implements attention without the `/ sqrt(d_k)` scaling and it trains fine at `d_k = 8`, but stalls and barely updates once they scale the model up to `d_k = 512`. Explain why, using what this lesson covered.

<details markdown="1"><summary>Check</summary>

Without scaling, the variance of the dot-product scores grows with `d_k`. At `d_k = 512` the scores are large enough that softmax saturates toward near-one-hot outputs, landing in a region where its gradient is nearly flat. The network gets almost no learning signal through that attention step, which looks like stalled training. Scaling by `sqrt(d_k)` keeps the scores in a range where this doesn't happen, regardless of dimension.

</details>

4. ▢ Which best describes the output of scaled dot-product attention for one query?

   - a) The single value vector paired with the highest-scoring key
   - b) A weighted sum of all value vectors, weighted by softmax over the query-key scores
   - c) The average of the query and key vectors, scaled by the value vectors
   - d) The value vector with the largest magnitude, unweighted

<details markdown="1"><summary>Check</summary>

**b)** A weighted sum of all value vectors, weighted by softmax over the query-key scores. (a) describes a hard lookup, which attention specifically isn't. (c) and (d) don't match the equation at all.

</details>

## Real-world reps

- [ ] Implement `Attention(Q, K, V)` from raw tensor operations (matrix multiply, scale, softmax, matrix multiply again), no attention-specific library function, for a small hand-chosen `Q`, `K`, `V`. Confirm your output matches the worked example's arithmetic style, computed by hand for a case you pick.
- [ ] Remove the `/ sqrt(d_k)` scaling from your implementation and compare the softmax output's spread (how close to one-hot it gets) at a small `d_k` versus a large one, using the same `Q` and `K` scaled up.
- [ ] Tomorrow: read the "Scaled Dot-Product Attention" section of the primary source paper in full, and check that every symbol in its equation matches something you can name in your own implementation.

## Going further

- [Article: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [Article: "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
