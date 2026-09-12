---
title: Transformers
description: "Build attention from scratch, so the architecture stops being a black box behind the training script"
type: topic
---

# Learning: Transformers

Be able to implement a transformer's forward pass and its training loop from raw tensors, and to read or modify real model code without the architecture being a black box behind it.

**Latest lesson:** [22. Mixture-of-Experts and FlashAttention](lessons/0022-mixture-of-experts-and-flashattention.md)

## Success looks like

- Implement scaled dot-product attention, multi-head attention, and a full transformer block from raw tensors, matching a reference implementation's output.
- Write the training loop that fits around that block from scratch and explain what each piece (loss, backward pass, optimizer step) is doing to the weights.
- Read a real model's code (a library like `transformers` or `llama.cpp`) and point to where each derived piece lives.

## Constraints

- Assumes comfort with Python and basic PyTorch tensor operations, and matrix multiplication as the only mathematics taken for granted; no prior deep-learning background required.
- Implementation in PyTorch, using raw tensor operations rather than `nn.Transformer` or other pre-built attention modules; autograd and GPU support are kept, only the architecture itself is hand-built.

## Out of scope

- Optimizer and scheduler variants beyond the basic loop needed to see the block train, distributed training, and the low-rank/adapter machinery built on top of it: see the [ownership table](../../README.md#ownership) for the `llm/finetuning` boundary. This workspace derives what that workspace names in passing (tokenizers in its lesson 0003, the low-rank idea in its lesson 0008) rather than restating them.

## The arc

Twelve stages, one equation to reading and generating from real model code at any scale. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Attention | 0001 to 0003 | Scaled dot-product attention, multi-head attention, causal masking | Multi-head attention is implemented from raw tensors, matching a reference implementation |
| 2. The transformer block | 0004 to 0006 | Positional encoding, layer norm and residual connections, the feed-forward block | A full transformer block is implemented from raw tensors |
| 3. The full model | 0007 to 0008 | Stacking blocks, embedding and output layers, weight tying | A full forward pass matches a reference implementation's output |
| 4. The training loop | 0009 to 0011 | Cross-entropy loss over the vocabulary, the backward pass, the AdamW optimizer step | The model trains from scratch and the loss decreases as expected |
| 5. Reading real model code | 0012 to 0013 | Mapping each derived piece to a real library (`transformers` or `llama.cpp`), tokenizers and low-rank adapters named in passing | Can point to where each derived piece lives in real model code |
| 6. Modern positional encoding and normalization | 0014 to 0015 | Rotary position embeddings, RMSNorm | Can derive RoPE's relative-position property and explain what RMSNorm drops from layer norm |
| 7. Modern feed-forward and attention variants | 0016 to 0017 | SwiGLU/the gated feed-forward, grouped-query and multi-query attention, KV caching | Can derive a gated feed-forward block and explain why fewer KV heads trade quality for cache size |
| 8. Generation and sampling | 0018 | Greedy decoding, temperature, top-k and top-p sampling, running the model forward to produce text | Can generate text from the hand-built model and explain why greedy decoding degenerates |
| 9. The training loop's practicalities | 0019 to 0020 | Xavier initialization, learning-rate warmup and decay, gradient clipping, mixed precision, gradient accumulation | Can explain what each practicality guards against and add them to a working training loop |
| 10. Encoder-decoder and encoder-only architectures | 0021 | BERT's bidirectional encoder, T5's encoder-decoder with cross-attention, placing this workspace's decoder-only model | Can explain why each architecture does or doesn't use a causal mask, and where cross-attention fits |
| 11. Mixture-of-experts and FlashAttention | 0022 | Sparsely-activated MoE routing, FlashAttention's IO-aware tiling | Can explain how MoE decouples parameters from per-token compute, and why FlashAttention is exact, not approximate |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-scaled-dot-product-attention.md) | Scaled Dot-Product Attention | The one equation the rest of the architecture is built around |
| [0002](lessons/0002-multi-head-attention.md) | Multi-Head Attention | Why attention runs in several smaller subspaces at once rather than one at full dimension |
| [0003](lessons/0003-causal-masking.md) | Causal Masking | Why a query position must not attend to future positions, and why the mask is applied before softmax, not after |
| [0004](lessons/0004-positional-encoding.md) | Positional Encoding | Why attention is blind to order on its own, and how sinusoidal encoding gives every position a distinguishable signature |
| [0005](lessons/0005-layer-norm-and-residuals.md) | Layer Norm and Residual Connections | Why stacking many transformer blocks needs a clean gradient path and stable activation ranges, and how residuals and layer norm each provide one |
| [0006](lessons/0006-feed-forward-block.md) | The Position-Wise Feed-Forward Block | What the transformer block's second sublayer adds beyond attention, and why it never mixes information across positions |
| [0007](lessons/0007-stacking-blocks.md) | Stacking Transformer Blocks | Why every block preserves the same shape, why depth isn't weight sharing, and why lesson 5's residual machinery matters most once many blocks are stacked |
| [0008](lessons/0008-embedding-output-and-weight-tying.md) | Embedding and Output Layers, Weight Tying | How tokens enter and leave the transformer's vector space, and why the two layers that do it can share one matrix |
| [0009](lessons/0009-cross-entropy-loss.md) | Cross-Entropy Loss Over the Vocabulary | How logits become one trainable number, and why the loss is the negative log probability of the actual next token |
| [0010](lessons/0010-backward-pass-and-autograd.md) | The Backward Pass and Autograd | How the chain rule, automated over a recorded computation graph, turns one scalar loss into a gradient for every weight |
| [0011](lessons/0011-adamw-optimizer.md) | The AdamW Optimizer Step | What Adam's momentum and adaptive scaling add over plain gradient descent, and why AdamW decouples weight decay from the gradient update |
| [0012](lessons/0012-reading-real-model-code.md) | Reading Real Model Code | Where each derived piece lives in a production model library, and the small, common deviations from the original paper worth recognizing rather than being confused by |
| [0013](lessons/0013-tokenizers-and-low-rank-adapters.md) | Tokenizers and Low-Rank Adapters | Deriving byte-pair encoding, and where a low-rank adapter actually attaches to a weight matrix this workspace built from scratch |
| [0014](lessons/0014-rotary-position-embeddings.md) | Rotary Position Embeddings | Sinusoidal encoding adds a fixed vector to the embedding before attention ever runs; RoPE instead rotates Q and K themselves, and that one change is what makes a dot product between two rotated vectors depend only on their relative distance |
| [0015](lessons/0015-rmsnorm.md) | RMSNorm | LayerNorm does two things, re-centering and re-scaling, and RMSNorm exists because the re-centering half turns out to be dispensable, leaving a cheaper normalization that current models use inside the pre-norm branch lesson 5 already derived |
| [0016](lessons/0016-swiglu-and-the-gated-feed-forward.md) | SwiGLU and the Gated Feed-Forward Block | Lesson 6's feed-forward block expands, applies one nonlinearity, and contracts; a gated variant computes two projections instead of one and multiplies them together, letting the network learn how much of its own computation to let through |
| [0017](lessons/0017-grouped-query-attention-and-kv-caching.md) | Grouped-Query Attention and KV Caching | Autoregressive generation makes attention recompute keys and values it already has, and once caching them becomes the obvious fix, the cache's own size is what makes fewer key/value heads worth trading a small amount of quality for |
| [0018](lessons/0018-generation-and-sampling.md) | Generation and Sampling | The model this workspace built and trained has never once produced text, because training and generation ask it two different questions, and always taking the single most likely next token turns out to be a worse answer to the second question than a well-chosen amount of randomness |
| [0019](lessons/0019-initialization-warmup-and-gradient-clipping.md) | Initialization, Warmup, and Gradient Clipping | A model this deep can fail before training even starts if its initial weights are scaled wrong, and the AdamW step lesson 11 derived still needs two more guardrails, a slow start and a hard ceiling on the gradient, to actually survive real training |
| [0020](lessons/0020-mixed-precision-and-gradient-accumulation.md) | Mixed Precision and Gradient Accumulation | Both techniques exist to fit a bigger effective training run into hardware smaller than the run seems to need, one by shrinking every number's footprint, the other by simulating a batch larger than memory could ever hold at once |
| [0021](lessons/0021-encoder-decoder-and-encoder-only-architectures.md) | Encoder-Decoder and Encoder-Only Architectures | This workspace built one stream with a causal mask because it only ever needed to do one thing, generate the next token, and the other two architecture shapes exist because BERT and the original translation model needed a structurally different guarantee instead |
| [0022](lessons/0022-mixture-of-experts-and-flashattention.md) | Mixture-of-Experts and FlashAttention | MoE grows a model's total parameters without growing what any single token actually pays to be processed, and FlashAttention computes lesson 1's exact same equation faster by rewriting how it touches memory, not what it computes |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources
- [Attention](reference/attention.md): scaled dot-product attention, multi-head attention and causal masking, with the tensor shapes annotated at each step
- [The Transformer Block](reference/the-transformer-block.md): positional encoding, layer norm and residuals, the feed-forward block, stacking, and weight tying
- [The Training Loop](reference/the-training-loop.md): cross-entropy loss, the backward pass and autograd, and the AdamW optimizer step, with the worked chain-rule and gradient-descent examples
- [Mapping to Real Code](reference/mapping-to-real-code.md): the transformers/llama.cpp name mapping, the three standard deviations from the original paper, byte-pair encoding, and where a low-rank adapter attaches

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
