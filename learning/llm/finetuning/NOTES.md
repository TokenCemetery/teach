# Adapter Fine-Tuning Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- Mission is the full arc: zero to senior specialist. No assumed background in transformers, training, or PyTorch.
- Knowledge-heavy topic, unlike the Go workspace. Most lessons are derivation and reading; runs confirm the reading rather than carrying it.
- Strong engineering background (Java, TypeScript, Docker, local inference already running), so infrastructure explanation can be brief. The maths cannot.
- **Lessons are written for a general reader, deliberately.** No machine, OS, accelerator or installed version appears in any lesson, reference sheet, `README.md` or `RESOURCES.md`. Personal calibration stays in this file. Requested explicitly; do not re-personalise the lesson material.

## Curriculum arc

Seven stages, zero to senior. All 27 lessons are written.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Ground floor | 0001–0004 | What a forward pass computes, where the weight matrices live, tokenizers, chat templates, what training changes | Can point at which tensors an adapter would touch and why |
| 2. The memory argument | 0005–0007 | Parameters vs gradients vs optimizer state, AdamW's two moments, activation memory, gradient checkpointing | Can compute why full fine-tuning fails on a given device, in bytes |
| 3. LoRA | 0008–0013 | `ΔW = BA`, rank, alpha and scaling, initialisation, target module choice, running it, reading the run, merging | Trains an adapter and can defend every hyperparameter |
| 4. Quantisation and QLoRA | 0014–0017 | int8/int4, NF4, double quantisation, backprop through a frozen quantized base, what degrades | Ran real NF4 and can say what it cost in quality |
| 5. DoRA and the variant landscape | 0018–0020 | Magnitude/direction decomposition, why it helps most at low rank, how to assess a new variant's claim | Can predict when DoRA beats LoRA before running it |
| 6. Data and evaluation | 0021–0024 | Dataset construction, contamination, held-out design, task metrics vs loss, regression suites | Has an eval that has actually caught a regression |
| 7. Operate and judge | 0025–0027 | Serving adapters vs merged, multi-adapter serving, cost and latency, when *not* to fine-tune | Trusted to decide whether a task should be fine-tuned at all |

Written upfront rather than one per session. The trade: the `README.md` index is complete and non-drifted, but no lesson has been calibrated against demonstrated knowledge yet. Expect to revise individual lessons once real answers come back — particularly the practice difficulty, which is currently guessed.

## Corrected: the CUDA claim

An earlier version of this file and of `README.md` asserted that 4-bit NF4 is CUDA-only, and therefore that stage 4 could not be learned honestly without NVIDIA hardware. **That is out of date and has been removed.**

Checked against the `bitsandbytes` source and architecture notes: the library now dispatches across CUDA (covering AMD ROCm), CPU, Intel XPU, Intel Gaudi and Apple MPS, with a `backends/mps/ops.py` providing `quantize_4bit`, `dequantize_4bit` and `gemv_4bit` for supported block sizes and pure-PyTorch fallbacks otherwise. CUDA remains described as the most complete and optimised backend.

What survives of the old boundary:

- **Paged optimizers really are CUDA-specific** — they use NVIDIA unified memory. They also matter least for adapter training, where optimizer state is megabytes.
- **Kernel coverage varies** by operation, block size and version, so non-CUDA paths can silently fall back to something slow.
- **Published numbers reproduce most reliably on CUDA.**

Lesson 0016 states this accurately, including the instruction to check the installed version rather than any document. Recheck periodically; this area moves.

## Setup blockers to resolve before running anything

Environment facts, not teaching decisions:

- No `torch` installed. Verify wheel availability for the chosen stack and platform before promising any run; a pinned Python version is likely, and `uv` is not installed either.
- No base model downloaded. Pick the stage 3 base early — something in the 1–3B class per the README constraint.
- Renting a larger accelerator is now optional rather than required, given the correction above. Worth it for speed on stage 4 and 6 comparisons, not for correctness.

## Scope pressure to resist

The slug says `finetuning`, which is broader than the mission. Expect drift toward full fine-tuning, DPO, and quantisation-for-inference. The `## Out of scope` list in `README.md` is the defence; revisit it rather than quietly widening.

## Open threads

- No task chosen yet. The mission works without one, but stage 6 becomes abstract unless a real task with a real metric appears by then. Lessons 0021–0024 are written generically and will land much harder against a concrete task.
- Unclear whether the end goal includes serving multiple adapters, which would change the emphasis in 0025.
- `GLOSSARY.md` still has an empty `## Terms` section by design — terms land there when they can be used correctly, and nothing has been demonstrated yet. The three pinned usage terms are there because the skill sanctions resolving loose field usage explicitly.
- No learning records yet. First one should capture disclosed prior knowledge so stage 1 is not re-taught unnecessarily.
