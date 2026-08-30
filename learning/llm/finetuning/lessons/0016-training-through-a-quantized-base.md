---
title: 16 — Training Through a Quantized Base
description: How gradients flow through frozen 4-bit weights
type: lesson
---

# Lesson 16 — Training Through a Quantized Base

**Mission link:** QLoRA in practice. This is also the one lesson where the hardware you have genuinely changes what is available to you.
**Primary source:** [Docs: bitsandbytes quantization — Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
**Prerequisites:** [Lesson 15](0015-nf4-and-double-quantisation.md), [Lesson 11](0011-your-first-adapter.md)

## Warm-up

1. ▢ What does NF4 place at normal quantiles, and why?

<details markdown="1"><summary>Check</summary>

Its 16 representable levels, so each covers equal probability mass rather than equal range — matching where normally distributed weights actually cluster.

</details>

2. ▢ What does double quantisation compress?

<details markdown="1"><summary>Check</summary>

The first-level block scales, not the weights. Roughly 0.37 bits per parameter.

</details>

3. ▢ For a 4-bit base with an adapter, which memory term dominates?

<details markdown="1"><summary>Check</summary>

Activations. The base has dropped to a few gigabytes and adapter state is a fraction of one, so batch size and sequence length now decide whether the run fits.

</details>

## Know this

### How a gradient reaches the adapter through a frozen quantized base

The apparent paradox: the base weights are 4-bit integers, and you cannot meaningfully take a gradient with respect to a 4-bit integer. So how does training work?

It works because **the base weights are not being trained.** Trace one adapted layer:

```text
forward:   h = W₀_dequant(x) + (α/r) · B A x
```

`W₀` is dequantised to bf16 for the matmul and the dequantised copy is discarded. The backward pass needs the gradient of the loss with respect to `A` and `B`, and to compute that it needs the *activations* flowing through the layer — which are bf16 — and the gradient arriving from above, which is also bf16.

The frozen weights participate in the backward pass only by **passing gradient through** to earlier layers. That requires multiplying by `W₀`, which requires dequantising it again — not differentiating with respect to it. No gradient is ever stored for a base weight, because none is requested.

So there is nothing exotic here. The quantized base is a constant in the computation graph. It has to be read at high precision, but it never has to be updated, and updating is the expensive part.

The cost is compute: dequantisation happens on every forward and again in the backward pass, on every step. QLoRA trades speed for memory, and it is meaningfully slower per step than a bf16 base.

### Preparing the model

```python
import torch
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, prepare_model_for_kbit_training, get_peft_model

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
)

model = AutoModelForCausalLM.from_pretrained("<base model>", quantization_config=bnb_config)
model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)

config = LoraConfig(r=32, lora_alpha=64, target_modules="all-linear", task_type="CAUSAL_LM")
model = get_peft_model(model, config)
model.print_trainable_parameters()
```

`prepare_model_for_kbit_training` does several small necessary things: casts layer norms and the output head to a stable precision, enables gradient checkpointing and input-gradient requirements, and makes sure nothing that must stay in higher precision was quantized. Skipping it produces runs that are unstable or that fail with gradient errors, and the cause is not obvious from the message.

### Everything else is unchanged

Rank, alpha, target modules, learning rate, schedule, held-out split, generation probes, the four checks from Lesson 11 — all identical. **QLoRA is LoRA with a cheaper base.** It is not a different method with its own hyperparameter folklore, and treating it as one is a common source of confusion.

The one adjustment worth mentioning: because the base is noisier, some practitioners use slightly more rank than they would with a bf16 base, on the theory that the adapter has to compensate for quantisation error as well as learn the task. Treat that as a hypothesis to test on your task, not a rule.

### Backends: what is actually true

This deserves care, because the widely repeated version of it is out of date.

`bitsandbytes` began as CUDA-only, and for several years "QLoRA needs an NVIDIA GPU" was simply accurate. The library has since moved to a multi-backend architecture, with dispatch for **CUDA (also covering AMD ROCm), CPU, Intel XPU, Intel Gaudi, and Apple MPS**, alongside pure-PyTorch fallbacks. The 4-bit operations — quantise, dequantise, and the 4-bit matrix-vector product — have backend implementations beyond CUDA, dispatched when the block size is one the compiled kernel supports and falling back to slower generic paths otherwise.

What follows for you:

- **CUDA remains the most complete and best optimised path.** If you have it, use it, and expect published numbers to be reproducible.
- **Other backends are viable and improving, with caveats.** Coverage varies by operation, block size and library version. Expect slower steps, and expect to check whether a specific configuration hits an optimised kernel or a fallback.
- **Paged optimizers are the genuinely CUDA-specific piece.** They rely on NVIDIA unified memory to spill optimizer state to host memory during transient spikes, avoiding an out-of-memory crash at a peak. That is a hardware feature, not a portable algorithm. It also matters least in adapter training, where optimizer state is tiny — its original purpose was full fine-tuning-scale state.
- **Verify against your installed version rather than any document.** This area has changed repeatedly and will change again. `bitsandbytes` is not the only route to 4-bit either; other quantisation backends exist with different hardware coverage.

The concepts in Lessons 14 and 15 — blockwise scales, normal-quantile levels, quantising the constants, storage precision versus compute precision — are arithmetic and are identical on every backend. Only the kernel availability and the speed differ.

### What to expect from the run

| Against a bf16 base | Effect |
|---|---|
| Fixed memory | Roughly 4× lower for the base |
| Step time | Slower — dequantisation on every forward and backward |
| Loss curve shape | Very similar; may sit marginally higher |
| Final quality | Slightly lower, task-dependent — measure it (Lesson 17) |

And the merge rule from Lesson 13 still holds, more importantly than ever: **merge into the full-precision base, not the quantized one.** Train against 4-bit, then load the base in bf16, apply the adapter, merge there. Merging into quantized weights adds a requantisation loss you have no reason to accept.

## Practice

1. ▢ How can gradients flow when the base weights are 4-bit integers?

<details markdown="1"><summary>Check</summary>

No gradient is ever taken with respect to a base weight — they are frozen constants. Gradients are taken with respect to `A` and `B`, which are high precision.

The frozen weights are needed to *propagate* gradient to earlier layers, which requires dequantising them for the multiply, not differentiating them.

</details>

2. ▢ What does `prepare_model_for_kbit_training` do, and what happens if you skip it?

<details markdown="1"><summary>Check</summary>

It casts modules that need stability — layer norms, the output head — to a higher precision, enables gradient checkpointing and input gradients, and ensures nothing that must stay high-precision was quantized.

Skipping it typically gives an unstable run or an error about gradients not being required, with a message that does not point at the cause.

</details>

3. ▢ Which is the CUDA-specific part of QLoRA, and how much does it matter for adapter training?

<details markdown="1"><summary>Check</summary>

Paged optimizers, which use NVIDIA unified memory to spill optimizer state to host memory during spikes.

It matters little for adapter training, where optimizer state is megabytes. It was designed for full fine-tuning-scale state, where a transient spike genuinely ends the run.

</details>

4. ▢ A tutorial from 2023 states that 4-bit NF4 requires an NVIDIA GPU. Is that still correct?

<details markdown="1"><summary>Check</summary>

Not as an absolute. `bitsandbytes` now dispatches 4-bit operations across CUDA/ROCm, CPU, Intel XPU, Intel Gaudi and Apple MPS, with PyTorch fallbacks where a compiled kernel is unavailable.

CUDA is still the most complete and fastest path, and coverage on other backends varies by operation, block size and version. So the correct statement is "CUDA is the best-supported path", not "CUDA is the only path" — and you verify against your installed version rather than any tutorial.

</details>

5. ▢ Which hyperparameter must you rethink when switching from LoRA to QLoRA?

   - a) The learning rate, which must be lowered substantially
   - b) The alpha value, which must be raised to compensate
   - c) None of them — the base precision is a separate concern
   - d) The batch size, which must be raised to stay stable

<details markdown="1"><summary>Check</summary>

**c)** None of them — the base precision is a separate concern.

QLoRA is LoRA with a cheaper base. Some practitioners try slightly more rank to absorb quantisation noise, but that is a hypothesis to test, not a required change.

</details>

6. ▢ You trained against a 4-bit base and want a single deployable model. Give the steps in order.

<details markdown="1"><summary>Check</summary>

Load the base in bf16 (not 4-bit), apply the trained adapter, merge, save with the tokenizer, and quantise the merged model afterwards only if you need a quantized artifact for serving.

Merging into the 4-bit base requires dequantise-add-requantise and loses quality for nothing.

</details>

## Real-world reps

- [ ] Load one base model in bf16 and in NF4. Record memory for each and compute the ratio.
- [ ] Run the same short training job against both bases. Record seconds per step and the loss curve, and note which is slower and by how much.
- [ ] Check what backend your `bitsandbytes` install is actually using, and whether your block size hits an optimised kernel or a fallback.
- [ ] Tomorrow: merge the 4-bit-trained adapter into the bf16 base and verify greedily against your probes.

## Going further

- [Docs: bitsandbytes quantization — Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
- [Code: bitsandbytes — bitsandbytes-foundation](https://github.com/bitsandbytes-foundation/bitsandbytes) — the backend directory is the authority on coverage
- [Paper: "QLoRA: Efficient Finetuning of Quantized LLMs" — Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
- [Lesson 17 — What QLoRA Actually Costs](0017-what-qlora-costs.md)

---

Not landing? Reread the primary source at the top — this lesson compresses it, and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
