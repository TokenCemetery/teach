---
title: Adapter Fine-Tuning
description: Decide whether to fine-tune, run it, prove it worked, ship it
type: topic
---

# Learning: Adapter Fine-Tuning (LoRA, QLoRA, DoRA)

Be the person who can take a base model and a task, decide whether adapter fine-tuning is the right answer at all, run it, prove it worked with an eval that would catch a regression, and ship it — and who can argue convincingly for prompting or retrieval instead when those would do the job better.

**Start here:** [0001 — What a Base Model Actually Is](lessons/0001-what-a-base-model-is.md)
**Latest lesson:** [0027 — When Not to Fine-Tune](lessons/0027-when-not-to-fine-tune.md)

## Success looks like

- Derive the memory cost of full fine-tuning versus LoRA for a given model and account for every byte.
- Choose rank, alpha, target modules and learning rate for a new task and justify each from the task rather than from a blog post's defaults.
- Train LoRA, QLoRA and DoRA adapters on the same task and explain the measured differences, not the advertised ones.
- Build an eval that catches a regression before shipping, instead of reading a loss curve and hoping.
- Serve an adapter through an inference stack and measure what it cost in quality and latency.
- Diagnose a failed run and name the cause: overfitting, catastrophic forgetting, wrong chat template, tokenizer mismatch, wrong target modules.
- Read a new PEFT paper and judge whether its claimed win would survive on your own task.

## Constraints

- Assumes no prior machine-learning background. Matrix multiplication is the only mathematics taken for granted; everything above it is taught where it is needed.
- Adapter training on a base model in the 1–3B class fits roughly 16 GB of accelerator or unified memory, which puts the whole arc within reach of ordinary single-device hardware.
- Backend support is uneven, not exclusive. CUDA remains the most complete and best-optimised path and is where published numbers reproduce most reliably; other backends work with varying kernel coverage and slower steps. Every concept transfers unchanged — only speed and kernel availability differ.
- Reps are long-latency: a training run takes minutes to hours, so sessions batch rather than fitting an evening, with reading in between.
- The tooling moves faster than any book. Library APIs are read from the installed version's documentation, never recalled.
- Nothing in the arc requires paid infrastructure, though renting a larger accelerator will make some comparisons faster.

## Out of scope

- Full fine-tuning at scale, and pretraining.
- RLHF, DPO and preference optimisation — adjacent, and a separate workspace later.
- Inference quantisation and distillation as topics in their own right; touched only where QLoRA needs them.
- Building serving infrastructure, beyond running an adapter through an existing stack.
- Training a model from scratch.

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-what-a-base-model-is.md) | What a Base Model Actually Is | The model is one next-token function; base is not instruct |
| [0002](lessons/0002-where-the-weights-live.md) | Where the Weights Live | Naming every projection an adapter could attach to |
| [0003](lessons/0003-tokenizers-and-chat-templates.md) | Tokenizers and Chat Templates | Train on the rendering you will serve |
| [0004](lessons/0004-what-training-changes.md) | What Training Actually Changes | The four operations in one training step |
| [0005](lessons/0005-counting-parameters-and-bytes.md) | Counting Parameters and Bytes | Turning a model config into gigabytes |
| [0006](lessons/0006-gradients-and-optimizer-state.md) | Gradients and Optimizer State | Sixteen bytes per trainable parameter, two per frozen |
| [0007](lessons/0007-activations-and-checkpointing.md) | Activations, Batch Size and Checkpointing | Why an adapter run still runs out of memory |
| [0008](lessons/0008-the-low-rank-idea.md) | The Low-Rank Idea | `ΔW = BA`, and counting an adapter |
| [0009](lessons/0009-rank-alpha-and-initialisation.md) | Rank, Alpha and Initialisation | Only `α/r` matters, and why `B` starts at zero |
| [0010](lessons/0010-choosing-target-modules.md) | Choosing Target Modules | Attention-only is a 2021 ablation, not a default |
| [0011](lessons/0011-your-first-adapter.md) | Your First Adapter | A run that proves the pipeline before it proves anything else |
| [0012](lessons/0012-reading-a-training-run.md) | Reading a Training Run | Diagnosing by curve shape, and what loss cannot see |
| [0013](lessons/0013-merging-and-shipping.md) | Merging, Saving and Shipping an Adapter | Merged is exact; an adapter is a diff that needs its base |
| [0014](lessons/0014-quantisation-from-first-principles.md) | Quantisation from First Principles | Blockwise scales, and why one outlier ruins a tensor |
| [0015](lessons/0015-nf4-and-double-quantisation.md) | NF4 and Double Quantisation | The two ideas QLoRA actually contributed |
| [0016](lessons/0016-training-through-a-quantized-base.md) | Training Through a Quantized Base | How gradients flow through frozen 4-bit weights |
| [0017](lessons/0017-what-qlora-costs.md) | What QLoRA Actually Costs | Separating base degradation from training degradation |
| [0018](lessons/0018-dora-magnitude-and-direction.md) | DoRA: Magnitude and Direction | Renormalisation decouples the two, and that is the method |
| [0019](lessons/0019-when-dora-wins.md) | When DoRA Wins, and When It Doesn't | Predicting the win before running it |
| [0020](lessons/0020-judging-a-new-variant.md) | Judging a New PEFT Variant | Six triage questions, and the baseline to beat |
| [0021](lessons/0021-building-the-dataset.md) | Building the Dataset | Data beats every hyperparameter in this workspace |
| [0022](lessons/0022-contamination-and-held-out-design.md) | Contamination and Held-Out Design | Splitting by the right key, and sizing for the question |
| [0023](lessons/0023-metrics-that-mean-something.md) | Metrics That Mean Something | Loss selects checkpoints; task metrics make decisions |
| [0024](lessons/0024-the-regression-suite.md) | The Regression Suite | Catching the damage every other number hides |
| [0025](lessons/0025-serving-adapters.md) | Serving Adapters | Merge for one task, route for many |
| [0026](lessons/0026-cost-latency-and-throughput.md) | Cost, Latency and Throughput | Prefill versus decode, and where the money actually goes |
| [0027](lessons/0027-when-not-to-fine-tune.md) | When Not to Fine-Tune | Fine-tuning is sixth on the list, and why that matters |

## Reference

- [Glossary](GLOSSARY.md) — canonical terms for this topic
- [Resources](RESOURCES.md) — trusted sources and communities
- [Memory budget](reference/memory-budget.md) — byte accounting, and what to try when a run will not fit
- [LoRA hyperparameters](reference/lora-hyperparameters.md) — rank, alpha, targets, learning rate, variants
- [Failure modes](reference/failure-modes.md) — symptom to cause, and the silent failures

## How this works

Each lesson is short and self-contained. Answer keys are collapsed — recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
