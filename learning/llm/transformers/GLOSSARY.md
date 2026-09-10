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

**Gradient accumulation**:
Running forward and backward passes on several smaller micro-batches in sequence without zeroing gradients between them, letting each micro-batch's gradients add onto the previous ones, then stepping the optimizer once on the combined total. Simulates a larger effective batch size than memory could hold at once, without changing what's computed.
_Avoid_: increasing the actual batch size (the goal gradient accumulation achieves without requiring the larger batch to ever fit in memory simultaneously)

**Gradient norm clipping**:
Rescaling an entire gradient vector down so its overall norm doesn't exceed a chosen threshold, leaving its direction unchanged, whenever that norm would otherwise be larger. Guards against an occasional exploding gradient causing one destructively large update.
_Avoid_: clipping each parameter's gradient independently (distorts the direction of the combined gradient; norm-based clipping rescales the whole vector uniformly instead)

**Greedy decoding**:
Always choosing the single highest-probability token from the model's predicted distribution at each generation step. Deterministic, and despite maximizing the same quantity the model was trained to predict well, produces bland, strangely repetitive text in practice.
_Avoid_: assuming the training objective (likelihood) is automatically the right decoding objective; the two are different questions with different answers

**Grouped-query attention (GQA)**:
An attention variant using an intermediate number of key/value heads, more than one, fewer than the number of query heads, with groups of query heads sharing one key/value head each. A middle ground between full multi-head attention's per-head keys/values and multi-query attention's single shared head.
_Avoid_: multi-query attention (MQA) (the more extreme case, a single shared key/value head; GQA is the generalization that keeps more than one)

**KV cache**:
Stored key and value vectors from every previous position during autoregressive generation, reused at each new generation step instead of being recomputed from scratch. Its size scales with the number of distinct key/value head sets a model has, which is exactly what grouped-query and multi-query attention reduce.
_Avoid_: recomputing keys and values at every generation step (correct but wasteful; the cache exists specifically to avoid this)

**Learning rate warmup**:
Increasing the learning rate gradually (often linearly) over a fixed number of initial training steps before it reaches its target value, rather than applying full strength immediately. Addresses Adam's moment estimates being unreliable in the earliest steps, before enough gradients have been seen to calibrate them.
_Avoid_: applying the target learning rate from step one (risks a large, poorly-directed update before the optimizer's own statistics have stabilized)

**Mixed precision training**:
Storing weights, activations, and gradients in half precision for most of training instead of full (single) precision, cutting memory use nearly in half. Requires a full-precision master weight copy (to preserve small updates that would otherwise underflow) and loss scaling (to keep small gradients from underflowing to zero).
_Avoid_: training in half precision alone, with no master weight copy or loss scaling (risks silently losing small updates and gradients to underflow)

**Nucleus sampling (top-p)**:
Sampling from the smallest set of highest-probability tokens whose cumulative probability exceeds a threshold `p`, a set whose size varies from step to step depending on how peaked or flat the distribution is. Contrasts with top-k's fixed-size truncation, which can't adapt to that variation.
_Avoid_: top-k sampling (a fixed-count truncation; nucleus sampling's cutoff is a dynamic, cumulative-probability-based set instead)

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

**Temperature**:
A value dividing the logits before the softmax that produces a next-token distribution during generation. Below 1, it sharpens the distribution toward greedy's behavior; above 1, it flattens it. Reshapes how peaked the distribution is without deciding which tokens are eligible to be sampled at all.
_Avoid_: top-k, top-p (temperature only rescales probability sharpness; deciding the eligible set is a separate, subsequent step those methods perform)

**Top-k sampling**:
Truncating a next-token distribution to its `k` highest-probability tokens, discarding the rest, and sampling from that fixed-size, renormalized set. Unlike nucleus (top-p) sampling, the eligible set's size never adapts to how peaked or flat the distribution actually is at a given step.
_Avoid_: nucleus sampling (top-p) (a dynamically-sized alternative; top-k's cutoff count is fixed regardless of the distribution's actual shape)

**Xavier (Glorot) initialization**:
Scaling a layer's initial weight variance by its fan-in and fan-out (the number of inputs and outputs it connects), rather than using one fixed variance for every layer, so activation and gradient variance stays roughly consistent across a deep network's layers instead of compounding smaller or larger with each one.
_Avoid_: a single fixed initialization variance for every layer regardless of size (the problem Xavier initialization was specifically designed to fix)
