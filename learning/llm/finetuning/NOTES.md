# Adapter Fine-Tuning Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- Mission is the full arc: zero to senior specialist. No assumed background in transformers, training, or PyTorch.
- Knowledge-heavy topic, unlike the Go workspace. Most lessons are derivation and reading; runs confirm the reading rather than carrying it.
- Strong engineering background (Java, TypeScript, Docker, local inference already running), so infrastructure explanation can be brief. The maths cannot.

## Curriculum arc

Seven stages, zero to senior. One stage takes several lessons.

| Stage | Covers | Done when |
|---|---|---|
| 1. Ground floor | What a forward pass computes, where the weight matrices live (attention `q,k,v,o`; MLP up/down), tokenizers, chat templates, what training changes | Can point at which tensors an adapter would touch and why |
| 2. The memory argument | Parameters vs gradients vs optimizer state, AdamW's two moments, activation memory, gradient checkpointing | Can compute why full fine-tuning fails on this machine, in bytes |
| 3. LoRA | `ΔW = BA`, rank, alpha and scaling, initialisation, target module choice, merging, the intrinsic-dimensionality argument | Trains an adapter and can defend every hyperparameter |
| 4. Quantisation and QLoRA | int8/int4, NF4, double quantisation, paged optimizers, backprop through a frozen quantized base, what degrades | Ran real NF4 on rented hardware and can say what it cost in quality |
| 5. DoRA and the variant landscape | Magnitude/direction decomposition, why it helps most at low rank, how to assess a new variant's claim | Can predict when DoRA beats LoRA before running it |
| 6. Data and evaluation | Dataset construction and formatting, contamination, held-out design, task metrics vs loss, regression suites | Has an eval that has actually caught a regression |
| 7. Operate and judge | Serving adapters vs merged weights, multi-adapter serving, cost and latency, when *not* to fine-tune, reading papers critically | Trusted to decide whether a task should be fine-tuned at all |

## Setup blockers to resolve before lesson 0001

These are environment facts, not teaching decisions, and at least the first is load-bearing:

- Python 3.14.7 with no `torch`. Verify wheel availability for the chosen stack on arm64 before promising any run; likely answer is a pinned 3.11/3.12 environment, and `uv` is not installed either.
- No model downloaded yet. Pick the stage 3 base model early — something in the 1–3B class fits 16 GB for adapter training.
- GPU rental provider not chosen. Needed by stage 4, not before, so it should not block the start.

## Fidelity boundary

Worth being explicit, because blurring it would teach something false: MLX quantized LoRA is QLoRA *in spirit*, not QLoRA. NF4 and double quantisation are precisely the parts that do not transfer, and they are the interesting parts of the paper. Stage 4 is the one stage that needs real CUDA hardware. Stages 3 and 5 are honest locally.

## Scope pressure to resist

The slug says `finetuning`, which is broader than the mission. Expect drift toward full fine-tuning, DPO, and quantisation-for-inference. The `## Out of scope` list in `README.md` is the defence; revisit it rather than quietly widening.

## Open threads

- No task chosen yet. The mission works without one, but stage 6 becomes abstract unless a real task with a real metric appears by then.
- Unclear whether the end goal includes serving multiple adapters, which would change stage 7 substantially.
