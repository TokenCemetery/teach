---
title: "18. DoRA: Magnitude and Direction"
description: Renormalisation decouples the two, and that is the method
type: lesson
---

# Lesson 18. DoRA: Magnitude and Direction

**Mission link:** The third method named in the mission, and the one whose mechanism is most often described wrongly.
**Primary source:** [Paper: "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
**Prerequisites:** [Lesson 8](0008-the-low-rank-idea.md), [Lesson 9](0009-rank-alpha-and-initialisation.md)

## Warm-up

1. ▢ Write the LoRA update and say which factors are trainable.

<details markdown="1"><summary>Check</summary>

`h = W₀x + (α/r)BAx`. Only `A` and `B` are trainable; `W₀` is frozen. `B` starts at zero.

</details>

2. ▢ What is the maximum rank of a LoRA update at `r = 8`?

<details markdown="1"><summary>Check</summary>

Eight. `BA` cannot exceed the rank of its inner dimension, which bounds what updates the adapter can express.

</details>

3. ▢ Why is quantisation not free on small models?

<details markdown="1"><summary>Check</summary>

Quantisation error is a fixed relative perturbation, and small models have less redundancy available to absorb it.

</details>

## Know this

### The observation

Any weight matrix can be decomposed into a **magnitude** and a **direction**. Taking it column by column:

```text
W = m · (V / ‖V‖_c)
```

where `‖·‖_c` is the per-column norm, `V / ‖V‖_c` is a matrix of unit-norm columns — pure direction — and `m` is a vector of one scalar per column, carrying magnitude.

The DoRA authors analysed how full fine-tuning and LoRA move each of these two quantities during training, and found the patterns differ. Full fine-tuning tends to make relatively large directional changes with comparatively modest magnitude changes, and shows a distinctive relationship between the two. LoRA's updates move magnitude and direction together in a more coupled way, because a single low-rank additive term changes both at once and has no way to adjust them independently.

The hypothesis: that coupling is a limitation, and decoupling the two should give LoRA learning behaviour closer to full fine-tuning.

### The method

Decompose the frozen `W₀` into its magnitude and direction. Then:

- Make the **magnitude vector `m` trainable directly.** It is one scalar per column — `d_out` parameters, negligible.
- Apply the **low-rank update to the direction**, and renormalise afterwards.

```text
W' = m · (W₀ + BA) / ‖W₀ + BA‖_c
```

Read that carefully, because it is where descriptions go wrong. `BA` is added to the weight and then the result is **renormalised to unit columns**, which strips out whatever magnitude change `BA` introduced. Magnitude is then supplied separately and explicitly by the trainable `m`.

So `BA` can no longer change magnitude even accidentally — it only steers direction — and `m` handles scale. That is the decoupling, and it is the entire contribution.

### What it costs

**Parameters:** one extra vector per adapted layer, of length `d_out`. For a 4096-wide layer that is 4096 numbers against a rank-16 adapter's 131,072. Essentially free.

**Compute:** not free. The column norm of `W₀ + BA` must be computed, and it depends on `BA`, so it changes every step and cannot be cached across updates. This makes DoRA measurably slower per step than LoRA — commonly on the order of tens of percent, varying by implementation and how much of the work the library manages to fuse or cache.

**Complexity:** merging is more involved. The merged weight is `m · (W₀ + BA)/‖W₀ + BA‖_c`, still an ordinary matrix — so a merged DoRA is exact and has zero inference overhead, exactly like LoRA. But the arithmetic to get there is not a simple addition, and the implementation matters.

### Using it

In PEFT, DoRA is a flag on the LoRA config rather than a separate method:

```python
from peft import LoraConfig

config = LoraConfig(
    use_dora=True,
    r=8,
    lora_alpha=32,
    target_modules="all-linear",
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
```

Everything you know about rank, alpha, target modules and learning rate carries over. It is a modification to how the update is applied, not a new set of decisions. Confirm the flag name against the installed version, as always.

DoRA also composes with quantisation — a quantized base plus a DoRA adapter, sometimes called QDoRA. The interaction is worth measuring rather than assuming: the renormalisation now operates on dequantised weights carrying quantisation error, which is not obviously harmless.

### The honest summary

DoRA is a well-motivated refinement with a clear mechanism, reported gains concentrated at low rank, and a real speed cost. It is not a replacement for LoRA and it is not a large effect at every setting. Lesson 19 is about predicting when it will pay for itself.

## Practice

1. ▢ Write the DoRA formula and identify every trainable quantity.

<details markdown="1"><summary>Check</summary>

`W' = m · (W₀ + BA) / ‖W₀ + BA‖_c`.

Trainable: the magnitude vector `m`, plus `A` and `B`. Frozen: `W₀`.

</details>

2. ▢ What does the renormalisation accomplish?

<details markdown="1"><summary>Check</summary>

It removes any magnitude change that `BA` introduced, leaving `BA` able to affect direction only. Magnitude is then set explicitly by the trainable `m`.

That separation is the decoupling the method is named for.

</details>

3. ▢ Why is DoRA slower than LoRA despite adding almost no parameters?

<details markdown="1"><summary>Check</summary>

The column norm of `W₀ + BA` must be computed, and because it depends on `BA` it changes every step and cannot be cached across updates. The extra parameters are negligible; the extra arithmetic is not.

</details>

4. ▢ How many extra parameters does DoRA add to a 4096 × 4096 layer, and how does that compare to a rank-16 LoRA there?

<details markdown="1"><summary>Check</summary>

4096 — one magnitude scalar per output column.

Rank-16 LoRA on that layer is 16 × (4096 + 4096) = 131,072. So DoRA's addition is about 3% on top, which is not the reason to hesitate. The step time is.

</details>

5. ▢ Does a merged DoRA have inference overhead?

<details markdown="1"><summary>Check</summary>

No. The merged result `m · (W₀ + BA)/‖W₀ + BA‖_c` is an ordinary weight matrix, so a merged DoRA is indistinguishable from any other model at inference.

The arithmetic to produce it is more involved than LoRA's simple addition, but the product is the same kind of thing.

</details>

6. ▢ Which statement describes DoRA correctly?

   - a) It adds a second low-rank update to the magnitude term
   - b) It trains magnitude directly and low-rank-updates direction
   - c) It replaces the low-rank update with a full-rank scaling
   - d) It normalises the gradients rather than the weight matrix

<details markdown="1"><summary>Check</summary>

**b)** It trains magnitude directly and low-rank-updates direction.

There is no second low-rank factor. The update is not full-rank. The normalisation is applied to the weight, not to gradients.

</details>

## Real-world reps

- [ ] Implement the decomposition by hand: take any weight matrix, compute per-column norms, split into `m` and unit-norm `V`, and verify `m · V` reconstructs it.
- [ ] Train the same configuration with `use_dora=True` and `False`. Record seconds per step for both and compute the overhead.
- [ ] Tomorrow: read section 4 of the DoRA paper, where the magnitude-direction analysis of full fine-tuning versus LoRA is presented. That analysis is the argument.

## Going further

- [Paper: "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
- [Docs: LoRA variants, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Lesson 19. When DoRA Wins, and When It Doesn't](0019-when-dora-wins.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
