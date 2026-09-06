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
- [Paper: "Layer Normalization", Ba, Kiros, and Hinton, 2016](https://arxiv.org/abs/1607.06450)
  Introduces layer normalization: normalizing each example's own activations across the feature dimension, independent of batch size, unlike batch normalization. Use for: understanding what layer norm actually computes and why it fits sequences of variable length and small batch sizes.
- [Paper: "On Layer Normalization in the Transformer Architecture", Xiong et al., 2020](https://arxiv.org/abs/2002.04745)
  Compares placing layer norm after the residual addition (the original paper's choice, post-norm) against placing it before each sublayer, inside the residual branch (pre-norm), and shows why pre-norm trains more stably at greater depth. Use for: understanding why most current large models use pre-norm despite the original transformer paper using post-norm.
- [Paper: "Using the Output Embedding to Improve Language Models", Press and Wolf, 2017](https://arxiv.org/abs/1608.05859)
  Argues for tying the input embedding and output projection weight matrices, since both relate a token to the same underlying representation, cutting a large fraction of a large-vocabulary model's parameters. Use for: understanding weight tying as a deliberate design choice, not just a parameter-saving trick.

## Gaps

- No source yet on rotary positional embeddings (RoPE), used by most current models in place of the original paper's sinusoidal or learned schemes; lesson 4 covers sinusoidal vs. learned from the original paper and stable, uncontested mechanics, but a RoPE comparison still needs a source once lesson design reaches it.
