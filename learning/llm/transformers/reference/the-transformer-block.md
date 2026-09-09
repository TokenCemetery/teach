---
title: The Transformer Block
description: "Positional encoding, layer norm and residual connections, the feed-forward block, and stacking blocks into the full model with embedding, output, and weight tying"
type: reference
---

# The Transformer Block: From One Block to the Full Model

Stages 2 and 3 compressed for lookup. [Lesson 4](../lessons/0004-positional-encoding.md) covers injecting position into the embeddings; [lesson 5](../lessons/0005-layer-norm-and-residuals.md) covers residuals and layer norm; [lesson 6](../lessons/0006-feed-forward-block.md) covers the feed-forward sublayer; [lesson 7](../lessons/0007-stacking-blocks.md) covers stacking blocks into depth; [lesson 8](../lessons/0008-embedding-output-and-weight-tying.md) covers entering and leaving the model's vector space. This sheet is the formulas, the shapes, and the choices, side by side.

## Positional encoding

Attention has no notion of order on its own; swapping two positions just relabels the output. Position has to be baked into the embeddings themselves, before attention ever runs.

```text
PE(pos, 2i)   = sin(pos / 10000^(2i / d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i / d_model))
```

| Scheme | Generalizes to unseen sequence lengths | Implementation |
|---|---|---|
| Sinusoidal (fixed formula) | Yes, the formula evaluates at any position | No parameters to learn |
| Learned position embedding | No, only has rows for positions seen in training | A lookup table, trained like any other parameter |

## Residual connections and layer norm

```text
post-norm: LayerNorm(x + Sublayer(x))
pre-norm:  x + Sublayer(LayerNorm(x))
```

| Piece | Solves | Independent of |
|---|---|---|
| Residual (`+ x`) | Gradient shrinking or exploding across a deep stack, by giving it a direct identity path at every layer | The sublayer's own transformation |
| Layer norm | Activation scale drifting layer to layer, by normalizing each token's own feature vector (mean/variance across features, then a learned scale and shift) | Batch size, unlike batch norm, which needs many examples' statistics |

**Pre-norm over post-norm.** Pre-norm keeps the residual path itself completely unnormalized end to end, an unobstructed identity connection; post-norm normalizes the residual sum at every layer, disrupting that path. Pre-norm is what most current large models use, despite the original paper's post-norm choice.

## The feed-forward block

```text
FFN(x) = max(0, x W1 + b1) W2 + b2
```

| Step | Shape in | Shape out | Note |
|---|---|---|---|
| `x W1 + b1`, nonlinearity | `[n, d_model] × [d_model, d_ff]` | `[n, d_ff]` | `d_ff` commonly 4x `d_model` (512 to 2048 in the original paper); ReLU originally, GELU/SwiGLU in later architectures |
| `... W2 + b2` | `[n, d_ff] × [d_ff, d_model]` | `[n, d_model]` | projects back down so the result adds into the residual stream |

Applied identically, same weights, to every position separately, no position ever sees another position's vector here. This is the precise complement to attention: attention mixes across positions but is linear in the values once its weights are computed; the feed-forward block is where a single position's own representation gets a genuinely nonlinear reshape.

## Stacking blocks

| Property | What it means | Why it matters |
|---|---|---|
| Shape-preserving | Every block takes `d_model` in, produces `d_model` out | Block N's output becomes block N+1's input with no adapter; the same block shape stacks any number of times |
| Not weight-shared | Each block has its own, independently learned parameters | Costs parameters roughly linearly with depth; buys different blocks specializing at different depths |
| Residual stream | One running vector passes through every block, each adding its own contribution | This is exactly what lesson 5's residual/layer-norm machinery protects as depth grows into dozens of blocks |

## Embedding, output, and weight tying

| Layer | Shape | Role |
|---|---|---|
| Input embedding | `vocab_size × d_model` | Row `i` is token `i`'s learned vector; looking it up is a lookup, not a computed transformation |
| Output projection | `d_model × vocab_size` | Produces one logit per vocabulary token per position |

The two shapes are transposes of each other. **Weight tying** reuses the embedding matrix, transposed, as the output projection (`logits = h @ W_embedding^T`) instead of learning a second matrix, on the reasoning that both layers relate a token to the same underlying representation.

Worked example: vocabulary 50,000, `d_model = 768`. Embedding table: `50,000 × 768 = 38,400,000` parameters. An untied output layer needs a second matrix that size; tying eliminates it, saving roughly 38.4 million parameters here for no quality loss, and often a measurable gain.

## Before trusting an implementation of the full model

- [ ] Positional encoding is added to the token embeddings before the first block, not injected some other way into attention.
- [ ] Every sublayer is wrapped in a residual connection, and layer norm placement (pre- or post-) is a deliberate choice, not whatever a tutorial happened to use.
- [ ] The feed-forward block's two layers expand then contract (`d_model` to `d_ff` to `d_model`), and its weights are never shared across positions.
- [ ] Every block in the stack takes and returns `d_model`, and each has its own independently learned weights.
- [ ] If weight tying is used, the output projection is the embedding matrix transposed, not a second learned matrix.

## Sources

- [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Paper: "Layer Normalization", Ba, Kiros, and Hinton, 2016](https://arxiv.org/abs/1607.06450)
- [Paper: "On Layer Normalization in the Transformer Architecture", Xiong et al., 2020](https://arxiv.org/abs/2002.04745)
- [Paper: "Using the Output Embedding to Improve Language Models", Press and Wolf, 2017](https://arxiv.org/abs/1608.05859)
- [Resources](../RESOURCES.md)
