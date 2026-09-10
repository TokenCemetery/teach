---
title: Glossary
description: "Canonical terms for transformers"
type: glossary
---

# Transformers Glossary

Canonical terms for the transformer architecture, derived from raw tensors rather than a pre-built module.

## Terms

**Gated linear unit (GLU)**:
The elementwise product of two linear projections of the same input, with a nonlinearity (originally sigmoid) applied to one of them first. That projection acts as a gate, scaling the other projection's output element by element rather than applying one fixed nonlinearity uniformly.
_Avoid_: SwiGLU (a specific GLU variant, gated with Swish/SiLU; "GLU" is the general family, not this one member of it)

**Grouped-query attention (GQA)**:
An attention variant using an intermediate number of key/value heads, more than one, fewer than the number of query heads, with groups of query heads sharing one key/value head each. A middle ground between full multi-head attention's per-head keys/values and multi-query attention's single shared head.
_Avoid_: multi-query attention (MQA) (the more extreme case, a single shared key/value head; GQA is the generalization that keeps more than one)

**KV cache**:
Stored key and value vectors from every previous position during autoregressive generation, reused at each new generation step instead of being recomputed from scratch. Its size scales with the number of distinct key/value head sets a model has, which is exactly what grouped-query and multi-query attention reduce.
_Avoid_: recomputing keys and values at every generation step (correct but wasteful; the cache exists specifically to avoid this)

**RMSNorm**:
A normalization that divides an activation vector by its root mean square and applies a learned scale, keeping layer norm's re-scaling operation while dropping its re-centering (mean-subtraction) step entirely. Cheaper than layer norm, with comparable task performance in practice.
_Avoid_: layer norm (the mean-and-variance-based normalization RMSNorm simplifies; RMSNorm never computes or subtracts a mean at all)

**Rotary position embedding (RoPE)**:
A positional mechanism that rotates the projected query and key vectors by an angle proportional to their position, rather than adding a fixed vector to the embedding beforehand. Because rotations compose by adding angles, the resulting attention score depends only on the relative offset between two positions, not either absolute position.
_Avoid_: sinusoidal encoding (a different, additive mechanism applied to the embedding before projection; RoPE is multiplicative and applied to Q and K after projection, inside the attention computation itself)

**Scaled dot-product attention**:
The operation `softmax(QK^T / sqrt(d_k)) V`: compare a query against a set of keys by dot product, scale to counteract variance growth with `d_k`, turn the scores into weights with softmax, and return the weighted sum of the corresponding values.
_Avoid_: attention mechanism (too vague once this specific form is meant)

**Self-attention**:
Scaled dot-product attention where the queries, keys and values all come from the same input sequence, so every position attends over every position in that same sequence, including itself.
_Avoid_: intra-attention

**SwiGLU**:
The GLU variant gated with the Swish (SiLU) activation, used in the feed-forward sublayer of most current open models in place of a plain ReLU or GELU nonlinearity. Uses three weight matrices (two up-projections, one down-projection) rather than a plain feed-forward block's two.
_Avoid_: GELU, ReLU (the fixed, single-projection nonlinearities SwiGLU's gated, two-projection design replaces in current models)
