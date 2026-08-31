---
title: 6. Gradients and Optimizer State
description: Sixteen bytes per trainable parameter, two per frozen
type: lesson
---

# Lesson 6. Gradients and Optimizer State

**Mission link:** This is the argument for adapters. Once you can derive the sixteen-bytes-per-parameter figure, LoRA stops being a trick and becomes the obvious response.
**Primary source:** [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., arXiv:1910.02054](https://arxiv.org/abs/1910.02054)
**Prerequisites:** [Lesson 4](0004-what-training-changes.md), [Lesson 5](0005-counting-parameters-and-bytes.md)

## Warm-up

1. ▢ Weights of a 7B model in bf16 — how many gigabytes?

<details markdown="1"><summary>Check</summary>

About 14 GB. Two bytes per parameter, so bf16 gigabytes are roughly twice the billions of parameters.

</details>

2. ▢ Which two tensors does AdamW keep per trainable parameter?

<details markdown="1"><summary>Check</summary>

A running mean of gradients and a running mean of squared gradients — the first and second moments. Each is parameter-shaped.

</details>

3. ▢ Why does bf16 beat fp16 for training?

<details markdown="1"><summary>Check</summary>

Its exponent range matches fp32, so values do not overflow to infinity. Rounding error is survivable; `NaN` is not.

</details>

## Know this

Everything a trainable parameter costs, per parameter:

| Category | fp32 training | Mixed precision (bf16 compute, fp32 master) |
|---|---|---|
| Weights | 4 | 2 (bf16) + 4 (fp32 master copy) |
| Gradients | 4 | 2 |
| AdamW first moment | 4 | 4 |
| AdamW second moment | 4 | 4 |
| **Total** | **16 bytes** | **16 bytes** |

The right-hand column is the part that surprises people. **Mixed precision does not reduce the total.** It halves the weight and gradient tensors, then adds back an fp32 master copy of the weights, because accumulating tiny updates into a bf16 value silently loses them. Optimizer moments stay in fp32 for the same reason. The win from mixed precision is arithmetic throughput, not memory.

So: **16 bytes per trainable parameter**, before a single activation.

### What that means

```text
1.5B trainable × 16 bytes = 24 GB
7B   trainable × 16 bytes = 112 GB
70B  trainable × 16 bytes = 1120 GB
```

Full fine-tuning a 7B model needs 112 GB of optimizer-and-weight state alone, then activations on top. That is multi-GPU territory for a model whose weights are 14 GB. The gap between "the model fits" and "training the model fits" is a factor of eight, and it is entirely gradients and optimizer state.

### The escape

Look again at the table and notice what the 16 bytes are multiplied by: the number of **trainable** parameters, not total parameters. Frozen parameters cost 2 bytes each — their weights — and nothing more. No gradient. No moments.

That is the whole argument for adapters:

```text
frozen parameter   = 2 bytes  (bf16 weights only)
trainable parameter = 16 bytes (weights + master + grad + 2 moments)
```

Freeze the base model, add a few million trainable parameters, and the second term nearly vanishes. Worked for a 7B base with 4M trainable adapter parameters:

```text
frozen base    7B  × 2  = 14.0 GB
trainable      4M  × 16 = 0.064 GB
```

The adapter's optimizer state is 64 MB. It has become a rounding error against the base weights — and the base weights are the one part you can attack separately, with quantisation, in stage 4.

### Partial measures, and why they are not enough

Before adapters existed, people reduced this cost in other ways. They are all still available and all still bounded:

| Technique | What it saves | What it costs |
|---|---|---|
| 8-bit optimizer | Moments at 1 byte instead of 4: 16 → 10 bytes | Slight quality risk; still linear in trainable count |
| SGD with momentum | One moment instead of two: 16 → 12 bytes | Noticeably worse convergence for transformers |
| Optimizer sharding (ZeRO) | Divides state across N devices | Needs N devices and fast interconnect |
| Offload to CPU | Moves state off the accelerator | Bandwidth-bound; much slower steps |

Every one of these scales the constant. None of them changes the fact that the cost is proportional to the number of trainable parameters. Adapters attack the multiplier instead, which is why they win by orders of magnitude rather than by factors.

### Why the moments cannot simply be dropped

A reasonable question: if AdamW's two moments are two thirds of the cost, why not use plain SGD? Because transformer training depends on Adam's per-parameter step scaling. Gradient magnitudes vary enormously across a transformer's parameters, and a single global learning rate serves them badly. The second moment is what lets each parameter take an appropriately sized step. This is empirical, consistent, and not a tuning problem you can wish away.

## Practice

1. ▢ Derive the memory needed to full fine-tune a 3B model with AdamW in mixed precision, excluding activations.

<details markdown="1"><summary>Check</summary>

16 bytes per trainable parameter × 3e9 = 48 GB.

Breaking it out: 6 GB bf16 weights + 12 GB fp32 master + 6 GB bf16 gradients + 12 GB first moment + 12 GB second moment = 48 GB.

</details>

2. ▢ Why doesn't mixed precision reduce total training memory?

<details markdown="1"><summary>Check</summary>

It halves weights and gradients but adds an fp32 master copy of the weights, and leaves both optimizer moments in fp32. The savings and the addition cancel, landing back at 16 bytes.

The master copy is not optional: repeatedly adding a very small update to a bf16 value rounds to no change at all, so the update is lost.

</details>

3. ▢ A 7B base is frozen in bf16 and you train a 20M-parameter adapter. Total, excluding activations?

<details markdown="1"><summary>Check</summary>

14 GB for the frozen base (7e9 × 2) plus 0.32 GB for the adapter (2e7 × 16) — about 14.3 GB.

Against 112 GB for full fine-tuning: a 7.8× reduction, and almost all of what remains is the frozen base. Stage 4 attacks that remainder.

</details>

4. ▢ Which change reduces optimizer memory most for a fixed model?

   - a) Switching the optimizer from AdamW to SGD
   - b) Switching the compute precision to bf16
   - c) Freezing the base and training an adapter
   - d) Switching to completion-only loss masking

<details markdown="1"><summary>Check</summary>

**c)** Freezing the base and training an adapter.

(a) removes one moment of two, saving a quarter. (b) saves nothing overall, as above. (d) changes which positions contribute to loss, not how many parameters have state. Only (c) attacks the number of trainable parameters, which is the multiplier on everything.

</details>

5. ▢ Someone proposes an 8-bit optimizer so they can full fine-tune a 70B model on one 80 GB accelerator. Do the arithmetic and respond.

<details markdown="1"><summary>Check</summary>

8-bit moments give 2 + 4 + 2 + 1 + 1 = 10 bytes per parameter. 70e9 × 10 = 700 GB. Still nearly nine times an 80 GB device, before activations.

The technique is real and useful; the plan is off by an order of magnitude. This is the value of doing the arithmetic before the experiment.

</details>

6. ▢ In one sentence: why do frozen parameters cost so much less than trainable ones?

<details markdown="1"><summary>Check</summary>

A frozen parameter needs only its own value stored for the forward pass, while a trainable one additionally needs a gradient, two optimizer moments, and a high-precision master copy — eight times as much.

</details>

## Real-world reps

- [ ] Build the 16-bytes table from memory on paper. Then compute total training memory for three model sizes you actually care about.
- [ ] Load a small model, run one training step with AdamW on all parameters, and record peak memory. Compare to your prediction.
- [ ] Tomorrow: repeat with the base frozen and only a small adapter trainable. The ratio you measure is the argument for stage 3.

## Going further

- [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., arXiv:1910.02054](https://arxiv.org/abs/1910.02054): the canonical accounting of these categories
- [Paper: "8-bit Optimizers via Block-wise Quantization", Dettmers et al., arXiv:2110.02861](https://arxiv.org/abs/2110.02861)
- [Memory budget](../reference/memory-budget.md)
- [Lesson 8. The Low-Rank Idea](0008-the-low-rank-idea.md): the response to this lesson

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
