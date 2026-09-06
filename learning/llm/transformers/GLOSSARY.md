---
title: Glossary
description: "Canonical terms for transformers"
type: glossary
---

# Transformers Glossary

Canonical terms for the transformer architecture, derived from raw tensors rather than a pre-built module.

## Terms

**Scaled dot-product attention**:
The operation `softmax(QK^T / sqrt(d_k)) V`: compare a query against a set of keys by dot product, scale to counteract variance growth with `d_k`, turn the scores into weights with softmax, and return the weighted sum of the corresponding values.
_Avoid_: attention mechanism (too vague once this specific form is meant)

**Self-attention**:
Scaled dot-product attention where the queries, keys and values all come from the same input sequence, so every position attends over every position in that same sequence, including itself.
_Avoid_: intra-attention
