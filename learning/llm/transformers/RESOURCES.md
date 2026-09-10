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
- [Docs: "torch.nn.functional.cross_entropy", PyTorch](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
  Official docs for the fused softmax-plus-negative-log-likelihood operation, taking raw logits directly for numerical stability rather than requiring a separate softmax step first. Use for: how cross-entropy loss is actually computed in practice, not just its formula.
- [Paper: "Adam: A Method for Stochastic Optimization", Kingma and Ba, 2015](https://arxiv.org/abs/1412.6980)
  Introduces Adam's momentum (first moment) and adaptive per-parameter scaling (second moment) over plain gradient descent, with bias correction for both. Use for: understanding what Adam's update rule computes and why, before AdamW's weight-decay fix.
- [Paper: "Decoupled Weight Decay Regularization", Loshchilov and Hutter, 2019](https://arxiv.org/abs/1711.05101)
  Identifies why folding weight decay into the gradient in original Adam interacts badly with its adaptive scaling, and fixes it by applying decay directly to the weights instead. Use for: why AdamW, not plain Adam, is the standard optimizer for training transformers.
- [Paper: "Neural Machine Translation of Rare Words with Subword Units", Sennrich, Haddow, and Birch, 2016](https://arxiv.org/abs/1508.07909)
  Introduces byte-pair encoding for subword tokenization: iteratively merging the most frequent adjacent symbol pair to build a vocabulary from raw bytes upward. Use for: deriving the tokenizer mechanism `llm/finetuning` names in passing rather than restating it.
- [Paper: "RoFormer: Enhanced Transformer with Rotary Position Embedding", Su et al., 2021](https://arxiv.org/abs/2104.09864)
  Introduces RoPE: rotating the projected query and key vectors by an angle proportional to position, producing an attention score that depends only on relative offset. Use for: the mechanism nearly every current open model uses in place of sinusoidal or learned positional encoding.
- [Paper: "Root Mean Square Layer Normalization", Zhang and Sennrich, 2019](https://arxiv.org/abs/1910.07467)
  Introduces RMSNorm, hypothesizing that layer norm's re-centering (mean-subtraction) operation is dispensable and re-scaling alone accounts for most of its benefit. Use for: the cheaper normalization current models place inside the pre-norm branch lesson 5 derives.
- [Paper: "GLU Variants Improve Transformer", Shazeer, 2020](https://arxiv.org/abs/2002.05202)
  Tests gated linear unit variants (including the Swish-gated SwiGLU) in the transformer's feed-forward sublayer, finding some outperform the typically-used ReLU or GELU. Use for: the gated, two-up-projection design that replaces lesson 6's single-projection feed-forward block in current models.
- [Paper: "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints", Ainslie et al., 2023](https://arxiv.org/abs/2305.13245)
  Introduces grouped-query attention as a middle ground between full multi-head attention and multi-query attention's single shared key/value head, plus a cheap recipe for uptraining an existing multi-head checkpoint into one. Use for: why fewer key/value heads trade a small amount of quality for a much smaller KV cache and faster inference.
- [Paper: "The Curious Case of Neural Text Degeneration", Holtzman et al., 2019](https://arxiv.org/abs/1904.09751)
  Documents why maximizing likelihood at decoding time (greedy decoding) produces bland, repetitive text despite likelihood being a good training objective, and introduces nucleus (top-p) sampling as the fix. Use for: the precise reason a dynamic, cumulative-probability cutoff beats both greedy decoding and a fixed top-k count.
- [Paper: "On the difficulty of training Recurrent Neural Networks", Pascanu, Mikolov, and Bengio, 2013](https://arxiv.org/abs/1211.5063)
  Analyzes the vanishing and exploding gradient problems and proposes gradient norm clipping as the fix for the latter. Use for: why clipping rescales the whole gradient vector by its norm rather than capping each parameter's gradient independently.
- [Paper: "Mixed Precision Training", Micikevicius et al., 2018](https://arxiv.org/abs/1710.03740)
  Introduces training in half precision with a full-precision master weight copy and loss scaling to counter half precision's limited numerical range, reducing memory use by nearly half. Use for: exactly what has to be added to plain half-precision training to keep small updates and gradients from underflowing to zero.
- [Paper: "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", Devlin et al., 2018](https://arxiv.org/abs/1810.04805)
  Introduces the encoder-only architecture: bidirectional attention jointly conditioning on left and right context in every layer, with no causal mask. Use for: why an encoder-only model builds a representation of a complete input rather than generating text autoregressively, and can't do what this workspace's decoder-only model does.
- [Paper: "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer" (T5), Raffel et al., 2019](https://arxiv.org/abs/1910.10683)
  Casts a wide range of NLP tasks into one consistent text-to-text, encoder-decoder format. Use for: the encoder-decoder shape's cross-attention sublayer, and why it fits a task with a clean, fixed input-then-output split.

## Gaps

- No source yet on the exact learning-rate-warmup-then-decay schedule; lesson 19 derives it from the shape stated in the original transformer paper's own training details (linear warmup, then decay proportional to the inverse square root of the step number), but a direct, freshly-verified excerpt from that section wasn't obtainable through available tooling in this session (the paper's abstract page doesn't carry the training-details section, and other PDF sources for it did not extract as readable text). Revisit if a cleaner source becomes available.
