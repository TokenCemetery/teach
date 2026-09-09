---
title: Attention
description: "Scaled dot-product attention, multi-head attention, and causal masking, with the tensor shapes annotated at each step"
type: reference
---

# Attention: Scaled Dot-Product, Multi-Head, and Causal Masking

Stage 1 compressed for lookup. [Lesson 1](../lessons/0001-scaled-dot-product-attention.md) covers the core equation; [lesson 2](../lessons/0002-multi-head-attention.md) covers running it in parallel subspaces; [lesson 3](../lessons/0003-causal-masking.md) covers restricting it to the past. This sheet is the equations and the shapes, side by side.

## Scaled dot-product attention

```text
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

| Step | Shape in | Shape out | Note |
|---|---|---|---|
| `Q`, `K`, `V` given | n/a | `[n, d_k]`, `[m, d_k]`, `[m, d_v]` | `n` queries, `m` key/value pairs; `d_k` is the key/query dimension |
| `QK^T` | `[n, d_k] × [d_k, m]` | `[n, m]` | one similarity score per query-key pair |
| `/ sqrt(d_k)` | `[n, m]` | `[n, m]` | counteracts variance growth with `d_k`, keeps softmax's gradient usable |
| `softmax(...)` (row-wise) | `[n, m]` | `[n, m]` | each row is now a probability distribution summing to 1 |
| `× V` | `[n, m] × [m, d_v]` | `[n, d_v]` | one output vector per query, a weighted blend of the values |

Self-attention is the case where `Q`, `K`, `V` all come from the same sequence (`n = m`), each position attending to every position including itself.

**Why the scaling.** Dot-product variance grows with `d_k`, pushing softmax toward near-one-hot outputs where its gradient is nearly flat and training stalls. `/ sqrt(d_k)` counteracts that growth regardless of how large `d_k` is.

## Multi-head attention

```text
Q_i = X W_Q^i,   K_i = X W_K^i,   V_i = X W_V^i          (per head i, i = 1..h)
head_i = Attention(Q_i, K_i, V_i)
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) W_O
```

| Step | Shape in | Shape out | Note |
|---|---|---|---|
| Input `X` | n/a | `[n, d_model]` | |
| Per-head projection (`W_Q^i`, `W_K^i`, `W_V^i`) | `[n, d_model] × [d_model, d_k]` | `[n, d_k]` per head, `d_k = d_model / h` | each head's projections are learned independently |
| `head_i = Attention(Q_i, K_i, V_i)` | `[n, d_k]` each | `[n, d_k]` | the exact equation above, run once per head |
| `Concat(head_1, ..., head_h)` | `h × [n, d_k]` | `[n, d_model]` | places heads side by side, no cross-head interaction yet |
| `× W_O` | `[n, d_model] × [d_model, d_model]` | `[n, d_model]` | the only step that lets information from different heads combine |

**The scaling formula uses the per-head `d_k`, not `d_model`.** Each head's dot products are summed over its own, smaller dimension, so that is the variance the scaling has to counteract, regardless of how large the full model is.

**`W_O` is not optional.** Concatenation alone places outputs side by side with no interaction; `W_O` is the only place different heads' information can combine into one representation.

## Causal masking

Added to the raw scores, before softmax:

```text
scores = QK^T / sqrt(d_k)
scores[i, j] += -inf   for every j > i     (a fixed lower-triangular pattern)
Attention(Q, K, V) = softmax(scores) V
```

| Choice | Why |
|---|---|
| Mask before softmax, not after | Zeroing a weight after softmax already ran leaves the remaining weights summing to less than 1, not a valid distribution. Masking the score lets renormalization happen automatically inside the same softmax |
| Large negative number, not `0` | `exp(0) = 1`, an ordinary, non-negligible value that still competes for probability mass. Only a large enough negative number drives `exp(...)` to effectively zero |
| Same mask for every head and every example in a batch | The restriction (query position `i` may attend to key positions `0..i`) is a property of the task, not of any one head |

At inference, a model generates token `N` from only tokens `1..N-1`; letting position `i` attend to a later position `j` during training lets the model use an answer it will never have at generation time. Training loss looks good in that case, but the model learns nothing transferable.

## Before trusting an attention implementation

- [ ] The scaling divisor is the per-head `d_k` (`d_model / h`), not the full `d_model`.
- [ ] `W_O` is applied after concatenating heads, not skipped.
- [ ] The causal mask is added to the raw scores before softmax, not applied to the weights after.
- [ ] The mask value is a large negative number (or `-inf`), not `0`.
- [ ] Output shape is `[n, d_model]` regardless of head count, since heads only change the intermediate per-head dimension.

## Sources

- [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Article: "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
- [Article: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [Resources](../RESOURCES.md)
