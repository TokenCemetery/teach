# Learning: Adapter Fine-Tuning (LoRA, QLoRA, DoRA)

Be the person who can take a base model and a task, decide whether adapter fine-tuning is the right answer at all, run it, prove it worked with an eval that would catch a regression, and ship it — and who can argue convincingly for prompting or retrieval instead when those would do the job better.

**Latest lesson:** _none yet_

## Success looks like

- Derive the memory cost of full fine-tuning versus LoRA for a given model and account for every byte.
- Choose rank, alpha, target modules and learning rate for a new task and justify each from the task rather than from a blog post's defaults.
- Train LoRA, QLoRA and DoRA adapters on the same task and explain the measured differences, not the advertised ones.
- Build an eval that catches a regression before shipping, instead of reading a loss curve and hoping.
- Serve an adapter through a local inference stack and measure what it cost in quality and latency.
- Diagnose a failed run and name the cause: overfitting, catastrophic forgetting, wrong chat template, tokenizer mismatch, wrong target modules.
- Read a new PEFT paper and judge whether its claimed win would survive on your own task.

## Constraints

- Assumes no prior machine-learning background. Matrix multiplication is the only mathematics taken for granted; everything above it is taught where it is needed.
- Adapter training on a 1–3B base model fits roughly 16 GB of GPU or unified memory, which makes stages 1–3 and 5 reachable on ordinary hardware, including Apple Silicon.
- **Stage 4 needs an NVIDIA GPU**, owned or rented. 4-bit NF4 runs through CUDA-only kernels, so QLoRA cannot be learned honestly anywhere else — a local approximation teaches the wrong thing about the one part that matters.
- Some spend is unavoidable at stage 4 unless CUDA hardware is already to hand. Nothing else in the arc costs money.
- Reps are long-latency: a training run takes minutes to hours, so sessions batch rather than fitting an evening, with reading in between.
- The tooling moves faster than any book. Library APIs are read from the installed version's documentation, never recalled.

## Out of scope

- Full fine-tuning at scale, and pretraining.
- RLHF, DPO and preference optimisation — adjacent, and a separate workspace later.
- Inference quantisation and distillation as topics in their own right; touched only where QLoRA needs them.
- Serving infrastructure beyond a single local stack.
- Training a model from scratch.

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| _none yet_ | | |

## Reference

- [Glossary](GLOSSARY.md) — canonical terms for this topic
- [Resources](RESOURCES.md) — trusted sources and communities

## How this works

Each lesson is short and self-contained. Answer keys are collapsed — recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Bring anything unclear back to the teaching session.
