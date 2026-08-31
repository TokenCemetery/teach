---
title: 11. Your First Adapter
description: A run that proves the pipeline before it proves anything else
type: lesson
---

# Lesson 11. Your First Adapter

**Mission link:** "Run it" is in the mission. Everything before this was the reading; this is the run.
**Primary source:** [Docs: SFTTrainer — Hugging Face TRL](https://huggingface.co/docs/trl/main/en/sft_trainer)
**Prerequisites:** [Lesson 3](0003-tokenizers-and-chat-templates.md), [Lesson 9](0009-rank-alpha-and-initialisation.md), [Lesson 10](0010-choosing-target-modules.md)

## Warm-up

1. ▢ What is the modern default for target modules, and why is it affordable?

<details markdown="1"><summary>Check</summary>

All linear layers, at generous rank. Adapter parameters are negligible against activation memory, so restricting them no longer buys much.

</details>

2. ▢ Which line of code catches a target-module name that matched nothing?

<details markdown="1"><summary>Check</summary>

`model.print_trainable_parameters()`. A near-zero count means the adapter attached to nothing.

</details>

3. ▢ Training or inference — where does `add_generation_prompt=True` belong?

<details markdown="1"><summary>Check</summary>

Inference. In training the assistant turn is already in the text, so adding the prompt duplicates the marker.

</details>

## Know this

### Pick the smallest thing that can fail informatively

Your first run's purpose is **not** a good model. It is to prove the pipeline is wired correctly. So make it cheap enough that a mistake costs minutes:

- A base model in the 0.5B–3B class. Small models train fast and expose data bugs just as well as large ones.
- A few hundred examples. Enough to see loss move.
- `max_steps` around 20–50, not epochs. You want it finished quickly.

Optimising anything before the pipeline is proven is wasted effort, and it hides which change caused which effect.

### A minimal run

```python
import torch
from datasets import load_dataset
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig

dataset = load_dataset("<a small instruction dataset>", split="train[:500]")

peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules="all-linear",
)

args = SFTConfig(
    output_dir="runs/first-adapter",
    max_steps=50,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,      # effective batch size 8
    learning_rate=2e-4,
    warmup_steps=5,
    lr_scheduler_type="cosine",
    logging_steps=1,                     # every step, for the first run
    max_length=1024,
    gradient_checkpointing=True,
    bf16=True,
    report_to="none",
)

trainer = SFTTrainer(
    model="<a small base model>",
    train_dataset=dataset,
    peft_config=peft_config,
    args=args,
)

trainer.train()
trainer.save_model("runs/first-adapter/final")
```

Two notes on this API surface. `SFTTrainer` accepts a model *string* and will load it for you. Sequence length is `max_length` on `SFTConfig`. Both of these have changed across releases — **read the installed version's documentation rather than trusting this snippet or your memory.** That instruction is not boilerplate; it is the most reliable source of wasted afternoons in this whole workspace.

### Precision, hardware, and what actually varies

`bf16=True` requires hardware support for bfloat16, which is widespread on modern accelerators but not universal. On older devices you may need fp16 with loss scaling, and on some backends full fp32 is the only option. The principle from Lesson 5 is unchanged; only the available formats differ.

Similarly, the specific accelerator behind this script is not part of the method. The concepts, the arithmetic and the failure modes are identical across CUDA, ROCm, Intel, Apple Silicon and CPU. What differs is which kernels are optimised, which precisions are supported, and how fast a step takes. Where a backend genuinely constrains the method, this workspace says so explicitly — see [Lesson 16](0016-training-through-a-quantized-base.md).

### The four checks, in order

Run these before you care about the loss curve.

**1. Does the adapter exist?**

```python
trainer.model.print_trainable_parameters()
```

Compare against your Lesson 8 arithmetic. A count of zero, or one that disagrees by more than rounding, means stop and fix.

**2. Is the data what you think it is?**

```python
example = trainer.train_dataset[0]
print(repr(tokenizer.decode(example["input_ids"])))
labels = example["labels"]
print(sum(1 for l in labels if l != -100), "of", len(labels), "positions scored")
```

Decode one real training example and read it. This one check catches template mismatches, missing end-of-turn tokens, a masking bug, and truncation mid-answer — four of the five most common causes of a bad fine-tune. **Do not skip it.** It is the highest-value ten seconds in the process.

**3. Does loss move?**

Over 50 steps with `logging_steps=1`, loss should visibly fall. Flat loss from step one means the adapter is not attached, the learning rate is far too low, or nothing is being scored.

**4. Can it overfit two examples?**

The strongest smoke test available. Train on two examples for a hundred steps. Loss should approach zero. If it cannot memorise two examples, the pipeline is broken — and you have learned that in two minutes rather than after a six-hour run.

### Save what you will need to reproduce it

The adapter directory is small — usually single-digit to low-hundreds of megabytes — and contains only the adapter weights plus a config recording the base model, rank, alpha and target modules. It is useless without that exact base model, so record the base model identifier and its revision alongside it.

Also record the library versions. A config that trained cleanly six months ago may not load the same way, and "which version was this" is not recoverable after the fact.

## Practice

1. ▢ You have 50,000 examples and a large base model available. Why is that the wrong first run?

<details markdown="1"><summary>Check</summary>

Because the first run's job is to prove the pipeline, and a long expensive run gives the same information as a short cheap one — just much later and at higher cost.

Worse, if something is wrong you learn it after hours instead of minutes, and you cannot tell which of several changes mattered.

</details>

2. ▢ Loss is completely flat from step one. Name three causes in the order you would check them.

<details markdown="1"><summary>Check</summary>

1. The adapter attached to nothing — check `print_trainable_parameters()`.
2. Every label is `-100`, so nothing is being scored — check the label count on a real example.
3. The learning rate is orders of magnitude too low — check it is around `1e-4`, not `1e-5` or lower.

All three are one line to rule out, which is why they come before anything subtle.

</details>

3. ▢ Why decode a training example rather than trusting the dataset?

<details markdown="1"><summary>Check</summary>

Because the failures that matter are invisible in the dataset and visible in the decoded text: a wrong chat template, a missing end-of-turn token, prompt tokens that were meant to be masked and are not, an answer truncated mid-sentence by `max_length`.

None of these raise an error. All of them produce a run that looks fine and a model that is not.

</details>

4. ▢ Your adapter cannot drive loss near zero on two examples in a hundred steps. What does that tell you?

<details markdown="1"><summary>Check</summary>

That the pipeline is broken, not that the task is hard. Two examples are trivially memorisable by any working adapter.

Look for an unattached adapter, fully masked labels, a learning rate near zero, or a data collator producing something other than what you expect.

</details>

5. ▢ You have the adapter directory and nothing else. Can you use it?

<details markdown="1"><summary>Check</summary>

Only if you can identify the exact base model it was trained against, which the adapter config records by name. Applied to a different base — even another checkpoint of the same family — the result is at best degraded and at worst nonsense.

Record the base model identifier, its revision, and your library versions. An adapter is a diff, and a diff needs its base.

</details>

6. ▢ Effective batch size for `per_device_train_batch_size=2`, `gradient_accumulation_steps=8`, on 4 devices?

<details markdown="1"><summary>Check</summary>

2 × 8 × 4 = 64.

Report this number, not the per-device one. Comparing runs by per-device batch size is a reliable way to draw a false conclusion.

</details>

## Real-world reps

- [ ] Run the two-example overfitting test before any real training. Confirm loss approaches zero.
- [ ] Decode and read one training example in full. Count how many positions are scored versus masked.
- [ ] Complete a 50-step run end to end and save the adapter. Note its size on disk.
- [ ] Tomorrow: write down the base model identifier, revision, and every library version, in a file next to the adapter.

## Going further

- [Docs: SFTTrainer — Hugging Face TRL](https://huggingface.co/docs/trl/main/en/sft_trainer)
- [Docs: LoRA — Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Failure modes](../reference/failure-modes.md) — keep this open during the run
- [Lesson 12 — Reading a Training Run](0012-reading-a-training-run.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
