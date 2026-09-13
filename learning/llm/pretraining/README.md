---
title: LLM Pretraining
description: "Train a model from scratch at scale: data, tokenizer, distributed training, and a defensible compute budget"
type: topic
---

# LLM Pretraining

Be able to plan and run a pretraining job from random initialization: build the data pipeline, train the tokenizer, pick a compute-optimal token budget for a given parameter count, keep a multi-day distributed run from diverging or stalling on a node failure, and defend that whole set of choices to someone who would otherwise have just fine-tuned an existing base model instead.

**Latest lesson:** [0014. Combining All Three: When Tensor and Pipeline Parallelism Earn Their Cost](lessons/0014-combining-all-three-when-tensor-and-pipeline-parallelism-earn-their-cost.md)

## Success looks like

- Build a deduplicated, quality-filtered pretraining corpus from raw sources, and say what each filtering step removes and why.
- Train a tokenizer and defend a vocabulary size against its effect on sequence length and embedding table size.
- Given a parameter count and a compute budget, compute the compute-optimal token count and defend it against a Kaplan-style undertrained alternative.
- Explain what ZeRO/FSDP shard, why data parallelism alone runs out of memory before it runs out of compute, and when tensor or pipeline parallelism is worth its communication cost.
- Read a training run's loss curve and gradient norms, and say whether a spike is recoverable or means restarting from an earlier checkpoint.
- Design a checkpointing scheme for a multi-day run that survives a node failure without losing more than a few minutes of progress.
- Decide whether a stated task calls for pretraining, continued pretraining, or fine-tuning an existing base model, and defend the choice on cost.

## Constraints

- Framework-adjacent, not framework-agnostic. Distributed-training techniques (ZeRO sharding, tensor and pipeline parallelism) are stable enough that lessons name the real library and API being described, unlike the provider-neutral pseudocode `llm/agents` uses for a faster-churning surface.
- No lesson trains a frontier-scale model. Reps run small (a GPT-2-scale model on a handful of GPUs, or a simulated multi-node setup) and reason from there to what changes at the scale the cited papers describe.
- Assumes `llm/transformers`: the attention mechanism, the training loop, cross-entropy loss, AdamW, mixed precision, and gradient clipping are prerequisites, not review.
- Access to multiple GPUs (even two, or a multi-process CPU simulation of the collective operations) is assumed for the distributed-training reps.

## Out of scope

- The transformer architecture itself, cross-entropy loss, the backward pass, AdamW, mixed precision, and gradient clipping: see [`llm/transformers`](../../llm/transformers/). This track picks up once that loop needs to run on hundreds of GPUs against trillions of tokens, not before.
- Adapting an existing base model with LoRA, QLoRA, or DoRA: see [`llm/finetuning`](../../llm/finetuning/). Pretraining starts from random weights, not a checkpoint, and the two are the two ways a model's weights change, covered as siblings rather than one including the other.
- Parallelism and quantization at serve time: see [`llm/inference`](../../llm/inference/). This track covers the training-time versions of parallelism (gradient synchronization, activation and optimizer sharding), not serving.
- Evaluation methodology and held-out data design: see [`llm/evals`](../../llm/evals/). Carried here only as the one capability a pretraining run needs, to validate a checkpoint mid-run, and linked to rather than restated.
- Aligning a pretrained model into an assistant: see [`llm/post-training`](../../llm/post-training/).

## The arc

Ten stages, from no prior knowledge to senior judgment. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
| --- | --- | --- |
| 1. Data pipeline | Sourcing, deduplication, quality filtering | Can build a filtered, deduplicated corpus from raw sources and defend what each step removed |
| 2. Tokenizer training | BPE and SentencePiece from scratch, vocabulary size tradeoffs | Can train a tokenizer and defend a vocabulary size choice |
| 3. Scaling laws | Kaplan against Chinchilla, the compute-optimal token-to-parameter ratio | Given a compute budget, can derive a compute-optimal token count and defend it |
| 4. Data parallelism | Gradient all-reduce, why it stops scaling alone | Can say why data parallelism alone runs out of memory before it runs out of compute |
| 5. Sharding memory | ZeRO stages 1 to 3, FSDP, activation and optimizer sharding | Can say what each ZeRO stage shards and what it costs in communication |
| 6. Model parallelism | Tensor and pipeline parallelism for training | Can decide when tensor or pipeline parallelism earns its communication cost over sharding alone |
| 7. Numerics and stability at scale | Mixed precision at scale, loss spikes, gradient norms, warmup and decay schedules | Given a loss curve, can say whether a spike is recoverable or needs a restart from an earlier checkpoint |
| 8. Checkpointing and fault tolerance | Saving and resuming a multi-day run, surviving a node failure | Can design a checkpointing scheme that bounds lost progress after a node failure |
| 9. Monitoring a training run | Loss curves, periodic eval checkpoints, linking to `llm/evals` | Can read a training dashboard and say whether the run is on track |
| 10. Judgment | Pretrain against continue-pretrain against fine-tune, defending a compute budget, reviewing someone else's training run config | Trusted to make the call and to explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-sourcing-and-mixing-a-pretraining-corpus.md) | Sourcing and Mixing a Pretraining Corpus | What goes into a pretraining corpus, and why the mixture of sources matters more than the total byte count |
| [0002](lessons/0002-deduplication-and-quality-filtering.md) | Deduplication and Quality Filtering | Why near-duplicate text and low-quality documents get removed before training, and what it costs to skip that step |
| [0003](lessons/0003-byte-pair-encoding-from-scratch.md) | Byte-Pair Encoding From Scratch | The algorithm that turns rare and unknown words into sequences of learned subword units, worked by hand |
| [0004](lessons/0004-sentencepiece-and-the-vocabulary-size-tradeoff.md) | SentencePiece and the Vocabulary Size Tradeoff | Tokenizing raw text without a pre-tokenizer, and what a larger or smaller vocabulary actually costs |
| [0005](lessons/0005-scaling-laws-what-kaplan-predicted.md) | Scaling Laws: What Kaplan Predicted | An empirical power law lets you forecast a training run's loss before paying for it, and what that predicted for how to spend a compute budget |
| [0006](lessons/0006-chinchilla-the-compute-optimal-correction.md) | Chinchilla: The Compute-Optimal Correction | Why model size and token count should scale together, and how to turn a compute budget into a token count |
| [0007](lessons/0007-data-parallelism-and-gradient-all-reduce.md) | Data Parallelism and Gradient All-Reduce | Splitting a batch across devices that each hold a full copy of the model, and what keeps every copy identical |
| [0008](lessons/0008-why-data-parallelism-alone-runs-out-of-memory.md) | Why Data Parallelism Alone Runs Out of Memory | Counting exactly what a mixed-precision Adam optimizer holds per parameter, and where that hits a wall |
| [0009](lessons/0009-zero-stage-1-and-2-partitioning-optimizer-state-and-gradients.md) | ZeRO Stage 1 and 2: Partitioning Optimizer State and Gradients | Removing data parallelism's redundant copies for free, before communication cost has to grow at all |
| [0010](lessons/0010-zero-stage-3-and-fsdp-partitioning-parameters-too.md) | ZeRO Stage 3 and FSDP: Partitioning Parameters Too | Sharding the parameters themselves means reconstructing them on demand, which is the first thing this costs |
| [0011](lessons/0011-activation-memory-and-zero-r.md) | Activation Memory and ZeRO-R | Sharding model states solves one memory problem and leaves a second one, activations, standing |
| [0012](lessons/0012-tensor-parallelism-splitting-a-layers-matrices.md) | Tensor Parallelism: Splitting a Layer's Matrices | Choosing which axis to split a weight matrix along so an entire transformer block needs only one all-reduce |
| [0013](lessons/0013-pipeline-parallelism-splitting-the-models-layers.md) | Pipeline Parallelism: Splitting the Model's Layers | Assigning consecutive layers to different devices, and the idle time that costs at the start and end of every batch |
| [0014](lessons/0014-combining-all-three-when-tensor-and-pipeline-parallelism-earn-their-cost.md) | Combining All Three: When Tensor and Pipeline Parallelism Earn Their Cost | Matching each parallelism strategy to the interconnect it tolerates, and when sharding alone is not enough |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
