---
title: Glossary
description: "Canonical terms for LLM pretraining"
type: glossary
---

# LLM Pretraining Glossary

Canonical terms for training a model from random initialization at scale: what the data and compute budget are made of, and how memory and computation get split across many devices.

## Terms

**Activation checkpointing**:
Discarding intermediate activations during the forward pass and recomputing them during the backward pass, trading extra compute for lower memory use.
_Avoid_: gradient checkpointing (the more common name in practice, but it checkpoints activations, not gradients, and the imprecise name misleads about what is being traded)

**Compute-optimal**:
The point on the tradeoff between parameter count and training tokens that minimizes loss for a fixed training compute budget, as opposed to a larger model trained on fewer tokens than that point implies.
_Avoid_: optimal (ambiguous about optimal for what; always pair with "compute" or "inference" to say which budget is fixed)

**Data parallelism**:
Splitting a training batch across devices that each hold a full copy of the model, computing gradients independently, and synchronizing them with an all-reduce before the optimizer step.
_Avoid_: distributed training (data parallelism is one form of it; the general term hides which resource is being split)

**Deduplication**:
Removing near-duplicate or exact-duplicate documents from a training corpus before tokenization, because repeated text is a leading cause of memorization and wasted compute.
_Avoid_: dedup (fine informally, but the glossary spells it out once the concept is pinned)

**Loss spike**:
A sudden, sharp rise in training loss partway through a run, usually caused by a numerically unstable batch or an accumulated optimizer-state drift, and distinguished from ordinary noise by whether the loss recovers on its own.
_Avoid_: divergence (divergence is the outcome when a loss spike does not recover; the two are not the same event)

**Pipeline parallelism**:
Splitting a model's layers across devices, with each device holding a contiguous slice of the stack and passing activations to the next, pipelining multiple micro-batches through it to keep every device busy.
_Avoid_: model parallelism (the broader term this and tensor parallelism both fall under; use the specific one once the distinction matters)

**Scaling law**:
An empirical power-law relationship between a model's loss and the compute, parameter count, or data it was trained with, used to predict the loss of a training run before it is paid for.
_Avoid_: scaling curve (a scaling law is the fitted relationship; a curve is one plot of it)

**Tensor parallelism**:
Splitting an individual layer's weight matrices across devices, so a single matrix multiplication is computed as a sum of partial products from each device, at the cost of a communication step per split layer.
_Avoid_: model parallelism (the broader term this and pipeline parallelism both fall under)

**Tokens-per-parameter ratio**:
The number of training tokens divided by the model's parameter count, the single number a compute-optimal training plan is built around.
_Avoid_: data-to-model ratio (used inconsistently in the literature for the inverse quantity; this workspace always means tokens divided by parameters)

**ZeRO stage**:
One of three increasing levels of state sharded across data-parallel devices: optimizer state (stage 1), optimizer state and gradients (stage 2), or optimizer state, gradients, and parameters (stage 3), each trading more communication for less per-device memory.
_Avoid_: FSDP (FSDP is PyTorch's implementation of ZeRO stage 3-style sharding; ZeRO is the underlying technique, and this workspace uses the technique's name when discussing the idea and FSDP when discussing the API)
