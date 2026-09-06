---
title: Transformers
description: "Build attention from scratch, so the architecture stops being a black box behind the training script"
type: topic
---

# Learning: Transformers

Be able to implement a transformer's forward pass and its training loop from raw tensors, and to read or modify real model code without the architecture being a black box behind it.

**Latest lesson:** [1. Scaled Dot-Product Attention](lessons/0001-scaled-dot-product-attention.md)

## Success looks like

- Implement scaled dot-product attention, multi-head attention, and a full transformer block from raw tensors, matching a reference implementation's output.
- Write the training loop that fits around that block from scratch and explain what each piece (loss, backward pass, optimizer step) is doing to the weights.
- Read a real model's code (a library like `transformers` or `llama.cpp`) and point to where each derived piece lives.

## Constraints

- Implementation in PyTorch, using raw tensor operations rather than `nn.Transformer` or other pre-built attention modules; autograd and GPU support are kept, only the architecture itself is hand-built.

## Out of scope

- Optimizer and scheduler variants beyond the basic loop needed to see the block train, distributed training, and the low-rank/adapter machinery built on top of it: `llm/finetuning` owns those, and this workspace derives what that workspace names in passing (tokenizers in its lesson 0003, the low-rank idea in its lesson 0008) rather than restating them.

## The arc

{N} stages, {start} to {end}. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
|---|---|---|
| 1. {Name} | {What it covers} | {The capability that closes the stage} |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-scaled-dot-product-attention.md) | Scaled Dot-Product Attention | The one equation the rest of the architecture is built around |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
