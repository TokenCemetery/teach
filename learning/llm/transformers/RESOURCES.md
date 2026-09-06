---
title: Resources
description: "Trusted sources for transformers"
type: resources
---

# Transformers Resources

## Knowledge

- [Paper: "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
  The original transformer paper: scaled dot-product attention, multi-head attention, and the full encoder-decoder block this workspace derives from raw tensors. Use for: the primary definition of every piece this workspace implements.
- [Article: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
  Visual, intuition-first walkthrough of attention and the transformer block, built to be read before the paper's notation. Use for: a working mental model before implementing anything.
- [Article: "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
  Line-by-line PyTorch implementation of the paper, from raw tensor operations, matched directly against the equations that produce them. Use for: checking a from-scratch implementation against a reference line by line.
- [Repo: nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
  Minimal, readable PyTorch implementation of a GPT-style transformer plus its training loop, small enough to read in full. Use for: the training-loop half of the mission, once the block itself works.
- [Video: "Let's build GPT: from scratch, in code, spelled out", Karpathy](https://www.youtube.com/watch?v=kCc8FmEb1nY)
  Builds attention and a GPT training loop from raw tensors on screen, step by step, deriving each piece rather than presenting it finished. Use for: watching the derivation happen before or alongside writing the code yourself.
- [Docs: "Autograd mechanics", PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
  Official explanation of how PyTorch's autograd actually computes gradients through a computation graph. Use for: understanding what the backward pass is doing to the weights, not just calling `.backward()`.
- [Repo: transformers, Hugging Face](https://github.com/huggingface/transformers)
  A real, production model library, useful once the from-scratch pieces exist. Use for: locating attention, multi-head projection, and the transformer block inside code written for production rather than for teaching.

## Gaps

- No source yet on rotary positional embeddings (RoPE), used by most current models in place of the original paper's sinusoidal or learned schemes; lesson 4 covers sinusoidal vs. learned from the original paper and stable, uncontested mechanics, but a RoPE comparison still needs a source once lesson design reaches it.
