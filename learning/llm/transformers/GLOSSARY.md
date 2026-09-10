---
title: Glossary
description: "Canonical terms for transformers"
type: glossary
---

# Transformers Glossary

Canonical terms for the transformer architecture, derived from raw tensors rather than a pre-built module.

## Terms

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
