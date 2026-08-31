---
title: 15. NF4 and Double Quantisation
description: The two ideas QLoRA actually contributed
type: lesson
---

# Lesson 15. NF4 and Double Quantisation

**Mission link:** These are the two ideas QLoRA contributed. Knowing them separates understanding the paper from having read the abstract.
**Primary source:** [Paper: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
**Prerequisites:** [Lesson 14](0014-quantisation-from-first-principles.md)

## Warm-up

1. ▢ Why blockwise rather than per-tensor quantisation?

<details markdown="1"><summary>Check</summary>

An outlier only sets the scale within its own block, containing the damage to 64 or 128 values instead of the whole tensor.

</details>

2. ▢ True bytes per parameter for 4-bit weights with fp32 scales at block size 64?

<details markdown="1"><summary>Check</summary>

0.5625 — that is 4.5 bits, with 0.5 bits of pure bookkeeping overhead.

</details>

3. ▢ What precision is the matmul in, for a 4-bit base?

<details markdown="1"><summary>Check</summary>

A higher one, typically bf16. Blocks are dequantised on the fly and the dequantized copies discarded.

</details>

## Know this

QLoRA contributed three things: NF4, double quantisation, and paged optimizers. The first two are ideas about representation and are the interesting ones. The third is an engineering mitigation, covered in Lesson 16.

### NF4 — NormalFloat

With 4 bits you get 16 levels. Where should you put them?

Uniform spacing — plain int4 — places them at equal intervals across the range. That is optimal if the values are uniformly distributed. **Neural network weights are not uniformly distributed.** They are approximately zero-centred and normally distributed, so most values cluster near zero and few are near the extremes.

Uniform levels therefore waste resolution: many levels sit out in the tails where almost no weights live, while the dense region near zero gets too few.

NF4's answer: place the 16 levels at the **quantiles of a standard normal distribution**, so each level covers an equal amount of *probability mass* rather than an equal amount of range. Levels are dense near zero and sparse in the tails, matching where the weights actually are. The paper describes this as information-theoretically optimal for zero-mean normally distributed data.

For this to work, each block must first be normalised into `[−1, 1]` by dividing by its absmax — which is exactly what blockwise quantisation was already storing. So NF4 is not extra machinery; it is a better choice of the 16 levels within the scheme from Lesson 14.

```text
int4:  levels evenly spaced        → resolution wasted in empty tails
nf4:   levels at normal quantiles  → resolution where the weights are
```

The consequence is that NF4 beats int4 at the same bit-width, for free. No extra storage, just a better codebook.

Two honest limits:

- The gain depends on the weights actually being close to normal. They usually are, per-block, after pretraining. It is an empirical property, not a guarantee.
- NF4 is a *weight* format. It is not the right tool for activations, which have different and less well-behaved distributions.

### Double quantisation

Return to the overhead from Lesson 14. Per parameter, at block size 64 with fp32 scales:

```text
weights            0.5     bytes
scales   4/64  =   0.0625  bytes
                  ────────
                   0.5625  bytes  (4.5 bits)
```

Those scales are themselves just numbers in a tensor, and there are a lot of them. So quantise them too.

Double quantisation takes the fp32 block scales, groups them (the paper uses blocks of 256), and stores them at 8 bits with their own second-level scale. The result:

```text
first-level scales at 8 bits:   1/64      = 0.015625 bytes/param
second-level scales:            4/(64·256) ≈ 0.000244 bytes/param
weights:                                     0.5      bytes/param
                                            ──────────
                                             0.5159   bytes/param  (~4.13 bits)
```

The paper reports the saving as approximately **0.37 bits per parameter** on average, which for a 65B model is around 3 GB. That is a real amount of memory recovered from pure bookkeeping.

Note the shape of the idea: the quantisation constants were a fixed tax on the scheme, and double quantisation reduced the tax rather than the payload. It is a small, clever, entirely mechanical win — and it is why 4-bit QLoRA lands near 4.1 bits per parameter in practice rather than 4.5.

### The memory result

Recompute Lesson 6's example with a 4-bit base. A 7B model with a 20M-parameter adapter:

| | bf16 base | 4-bit base |
|---|---|---|
| Frozen base weights | 14.0 GB | ~3.6 GB |
| Adapter state (16 B/param) | 0.32 GB | 0.32 GB |
| **Subtotal** | **14.3 GB** | **3.9 GB** |

Against 112 GB for full fine-tuning, the 4-bit adapter run's fixed cost is under 4 GB. Activations (Lesson 7) are now decisively the dominant term, which means gradient checkpointing matters more here than anywhere else in the workspace.

This is the result that made QLoRA significant: it moved fine-tuning of large models from clusters to single devices.

### The configuration

```python
import torch
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",            # not "fp4"
    bnb_4bit_use_double_quant=True,       # the 0.37 bits/param saving
    bnb_4bit_compute_dtype=torch.bfloat16,  # storage is 4-bit; compute is not
)
```

Four settings, each mapping to something in this lesson. `bnb_4bit_compute_dtype` is the one people leave at its default and should not: it is the precision the dequantised blocks are multiplied in, and leaving it at fp32 discards much of the speed benefit.

As always, confirm these names against the installed version's documentation.

## Practice

1. ▢ Why does NF4 beat int4 at the same bit-width?

<details markdown="1"><summary>Check</summary>

It places its 16 levels at the quantiles of a normal distribution rather than at uniform intervals, so resolution is concentrated where weights actually cluster — near zero — instead of being spent on empty tails.

Same storage, better codebook. The precondition is normalising each block to `[−1, 1]` first, which blockwise quantisation already does.

</details>

2. ▢ What exactly does double quantisation compress, and roughly how much does it save?

<details markdown="1"><summary>Check</summary>

The first-level block scales — the quantisation constants, not the weights. They are stored at 8 bits in groups of 256, with a small second-level scale.

The paper reports about 0.37 bits per parameter on average, roughly 3 GB for a 65B model. It takes 4-bit-with-overhead from about 4.5 bits down to about 4.1.

</details>

3. ▢ Compute total fixed memory for a 13B base in NF4 with double quantisation, plus a 30M adapter.

<details markdown="1"><summary>Check</summary>

Base: 13e9 × 0.5159 ≈ 6.7 GB. Adapter: 3e7 × 16 = 0.48 GB. About 7.2 GB fixed.

Compare 26 GB for a bf16 base plus adapter, and 208 GB for full fine-tuning. Activations then sit on top of the 7.2 GB.

</details>

4. ▢ Which QLoRA component saves the most memory?

   - a) NF4 rather than plain uniform int4 quantisation
   - b) Storing the frozen base at 4 bits rather than bf16
   - c) Double quantisation of the first-level block scales
   - d) Paged optimizers spilling state during memory spikes

<details markdown="1"><summary>Check</summary>

**b)** Storing the frozen base at 4 bits rather than bf16 — a 4× reduction on the largest fixed term.

NF4 improves quality at identical storage. Double quantisation saves about 0.37 bits per parameter. Paged optimizers prevent crashes at peaks rather than lowering steady-state use.

</details>

5. ▢ Why is NF4 inappropriate for quantising activations?

<details markdown="1"><summary>Check</summary>

Its level placement is derived from an assumption that values are zero-mean and approximately normal. Post-pretraining weights fit that reasonably; activations do not — they carry systematic large-magnitude outlier features, so normal quantiles are the wrong codebook for them.

</details>

6. ▢ You set `load_in_4bit=True` and leave `bnb_4bit_compute_dtype` at its default. What have you likely given up?

<details markdown="1"><summary>Check</summary>

Speed. Storage is still 4-bit and memory is still saved, but if the compute dtype defaults to fp32 then every dequantised block is multiplied at full precision, forfeiting much of the throughput advantage.

Set it to bf16 deliberately. Storage precision and compute precision are separate decisions.

</details>

## Real-world reps

- [ ] Work out on paper the bytes per parameter for 4-bit with and without double quantisation, at block size 64. Confirm the difference is close to 0.37 bits.
- [ ] Load the same model in bf16 and in NF4, measuring memory both times. Compare against your prediction.
- [ ] Tomorrow: generate the same prompt from both, greedily, and read the outputs side by side. Form a first impression of the quality cost — Lesson 17 makes it a measurement.

## Going further

- [Paper: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314): sections 3 and 4 are this lesson
- [Docs: bitsandbytes quantization, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
- [Memory budget](../reference/memory-budget.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
