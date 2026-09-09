---
title: Mapping to Real Code
description: "Where each derived piece lives in transformers or llama.cpp, the three standard deviations from the original paper, byte-pair encoding, and where a low-rank adapter attaches"
type: reference
---

# Mapping to Real Code

Stage 5 compressed for lookup. [Lesson 12](../lessons/0012-reading-real-model-code.md) covers translating this workspace's derivations into Hugging Face `transformers` and llama.cpp naming; [lesson 13](../lessons/0013-tokenizers-and-low-rank-adapters.md) covers deriving byte-pair encoding and where a low-rank adapter attaches to a weight matrix. This sheet is the name mapping, the standard deviations, and the two derivations, side by side.

## Naming in Hugging Face `transformers`

| Real-code name | Derived in | What it is |
|---|---|---|
| `GPT2Attention` (or similar) | Lessons 1-2 | Scaled dot-product attention, often via one fused QKV linear layer split apart afterward, a batched-matmul efficiency detail, not a different operation |
| A registered lower-triangular mask buffer | Lesson 3 | Causal masking, precomputed once since the mask depends only on sequence length, not on input values, and reused or sliced per call |
| `wte` (word token embedding) | Lesson 8 | The input embedding table |
| `wpe` (word position embedding) | Lesson 4 | Positional encoding, here commonly a learned table rather than the sinusoidal formula |
| A `ModuleList` of blocks, iterated in a for loop | Lesson 7 | Stacked transformer blocks |
| `lm_head`, tied to `wte`'s weights | Lesson 8 | The output projection, via weight tying |
| The training script or `Trainer`, not the model class | Lessons 9-11 | Cross-entropy loss, `.backward()`, the optimizer step; the model class only defines the forward pass to logits |

## Three standard deviations from the original paper

| Piece | Original paper | Common in production models | Still the same underlying lesson |
|---|---|---|---|
| Position embedding | Sinusoidal formula | A learned table, or rotary embeddings | Lesson 4's learned alternative, or a further variant |
| Activation function | ReLU | GELU (or SwiGLU) | Lesson 6's expand-then-contract shape, a different nonlinearity |
| Norm placement | Post-norm | Pre-norm | Lesson 5's pre-norm alternative |

None of these change the architecture this workspace derived; they are standard variations found across nearly every real implementation, not a different design.

## The same mathematics, a different codebase: llama.cpp

llama.cpp (C, via the `ggml` tensor library) builds an explicit computation graph through function calls rather than `nn.Module` classes with a `forward` method. It computes the same mathematical objects: attention, positional encoding (commonly rotary), normalization (commonly RMSNorm, a simplified layer norm variant), and a feed-forward block (commonly SwiGLU). The difference is entirely in how the computation graph is constructed and run, not in what it computes.

## Deriving the tokenizer: byte-pair encoding (BPE)

1. Represent training text as a sequence of raw bytes or characters, each its own vocabulary entry.
2. Count every adjacent pair of symbols across the corpus.
3. Merge the single most frequent pair into one new symbol, added to the vocabulary.
4. Repeat until the vocabulary reaches a chosen target size.

Worked example, corpus `"low low lower"`: the pair `l, o` is frequent and merges into `lo`; the next round finds `lo, w` and merges into `low`. Frequent words compress toward a single token; rare words fall back to smaller, more frequent pieces.

`vocab_size` is however many starting symbols plus merge steps the tokenizer's training ran for, fixed once training finishes; it is exactly what sizes lesson 8's input embedding table and output layer.

## Where a low-rank adapter attaches

`llm/finetuning`'s adapter mechanism, `ΔW = BA` with `A` projecting down to rank `r` and `B` projecting back up, attaches to a concrete weight matrix this workspace derived, for example lesson 2's per-head query projection:

```text
Q_i = X (W_Q^i + (alpha / r) B_i A_i)
```

| Matrix | Frozen? | Receives gradients during adapter training? |
|---|---|---|
| `W_Q^i` | Yes, exactly as pretrained | No |
| `A_i`, `B_i` | No, newly added, sized by rank `r` | Yes |

Because the update is additive and linear, exactly as the original projection is, `W_Q^i + (alpha/r) B_i A_i` collapses into one ordinary matrix after training. Nothing about the forward pass changes to serve the merged result, since it plugs into `Q_i = X W_Q^i` as an ordinary projection matrix, zero added inference computation.

## Before reading or attaching to a real model's code

- [ ] A fused QKV linear layer that gets split apart is recognized as an efficiency detail, not a different operation from per-head projections.
- [ ] The mask buffer, if precomputed, is understood to depend only on sequence length, not to change the masking mechanism itself.
- [ ] Position embedding, activation, and norm-placement choices are checked against the three standard deviations before being treated as a different architecture.
- [ ] A low-rank adapter's attachment point is named as a specific weight matrix (which projection, in which layer), not just "the model."

## Sources

- [Repo: transformers, Hugging Face](https://github.com/huggingface/transformers)
- [Repo: nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
- [Paper: "Neural Machine Translation of Rare Words with Subword Units", Sennrich, Haddow, and Birch, 2016](https://arxiv.org/abs/1508.07909)
- [Adapter](../../finetuning/GLOSSARY.md): `llm/finetuning`'s canonical term for the frozen-base-plus-small-trainable-weights pattern
- [Resources](../RESOURCES.md)
