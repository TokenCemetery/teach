---
title: 8 — The Low-Rank Idea
description: "`ΔW = BA`, and counting an adapter"
type: lesson
---

# Lesson 8 — The Low-Rank Idea

**Mission link:** LoRA is the method the rest of the mission is built on. This lesson is the mechanism; the next two are the decisions.
**Primary source:** [Paper: "LoRA: Low-Rank Adaptation of Large Language Models" — Hu et al., arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
**Prerequisites:** [Lesson 6](0006-gradients-and-optimizer-state.md), [Lesson 7](0007-activations-and-checkpointing.md), [adapter](../GLOSSARY.md)

## Warm-up

1. ▢ Bytes per trainable parameter, and per frozen parameter?

<details markdown="1"><summary>Check</summary>

Sixteen trainable, two frozen. The eight-to-one ratio is the reason adapters exist.

</details>

2. ▢ Your adapter run is out of memory. What do you change first, and what do you not change?

<details markdown="1"><summary>Check</summary>

Enable gradient checkpointing, then cut per-device batch size with accumulation to compensate. Do not cut rank — adapter state is megabytes against gigabytes of activations.

</details>

3. ▢ Which memory category is unaffected by freezing the base?

<details markdown="1"><summary>Check</summary>

Activations. They scale with batch size and sequence length, not with how many parameters are trainable.

</details>

## Know this

Full fine-tuning learns an update `ΔW` for every weight matrix, the same shape as `W`. LoRA's claim is that this update does not need to be full-rank, because the change a task requires occupies a low-dimensional subspace.

So instead of storing `ΔW` directly, factor it:

```text
ΔW = B A

A : r × d_in     (down-projection, r is small)
B : d_out × r    (up-projection)
```

and the adapted layer computes:

```text
h = W₀ x + (α / r) · B A x
```

`W₀` is frozen. Only `A` and `B` receive gradients.

### Why this saves so much

A `d_in × d_out` matrix holds `d_in · d_out` parameters. Its rank-`r` factorisation holds `r · (d_in + d_out)`. For a 2048 × 2048 projection at rank 8:

```text
full        = 2048 × 2048        = 4,194,304
rank 8      = 8 × (2048 + 2048)  =    32,768
```

A 128× reduction on that one matrix. Across a whole model the saving compounds, because you also skip the gradient and both optimizer moments for everything you did not make trainable.

### Counting an adapter

The formula, for a set of target modules:

```text
adapter params = Σ over targeted layers of  r × (d_in + d_out)
```

Worked, for the 24-layer model with `d = 2048` and `d_kv = 256` from Lesson 5, rank 8, targeting all four attention projections:

```text
q_proj: 2048 → 2048   →  8 × (2048 + 2048) = 32,768
k_proj: 2048 →  256   →  8 × (2048 +  256) = 18,432
v_proj: 2048 →  256   →  8 × (2048 +  256) = 18,432
o_proj: 2048 → 2048   →  8 × (2048 + 2048) = 32,768
per layer                                  = 102,400
× 24 layers                                = 2,457,600
```

About 2.5M trainable parameters against a 1.12B base — **0.22%**. Optimizer state for that adapter is 2.5e6 × 16 ≈ 39 MB.

Note that the grouped-query attention narrowing matters here in a way it did not for the base model: the `k_proj` and `v_proj` adapters are *not* proportionally smaller, because `r × (d_in + d_out)` is dominated by the larger of the two dimensions. Shrinking `d_out` from 2048 to 256 cut the base matrix by 8× but the adapter by only 1.8×.

### Why low rank is enough

The empirical claim rests on **intrinsic dimensionality**: the observation that fine-tuning a large pretrained model to a new task can be done within a surprisingly low-dimensional subspace of its parameter space, and that larger and better-pretrained models have *lower* intrinsic dimension, not higher (Aghajanyan et al., [arXiv:2012.13255](https://arxiv.org/abs/2012.13255)). Pretraining has already built the features; adaptation is largely a matter of reweighting and recombining them, and that is a small operation.

Two honest caveats:

**It is an empirical claim, not a theorem.** It holds well for adapting behaviour, style, format and narrow task competence. It holds less well for installing large volumes of genuinely new knowledge, which is one of the arguments in Lesson 27.

**"Low" is relative and has moved.** Early practice settled on ranks like 8 or 16, partly because memory was scarce. More recent work — see [Lesson 10](0010-choosing-target-modules.md) — finds that on many supervised fine-tuning tasks, generously ranked adapters covering all linear layers match full fine-tuning, while stingy ones do not. Rank 8 is a starting point, not a law.

### The inference property that makes LoRA special

Because the update is *additive* and linear, it can be folded back into the base weight after training:

```text
W = W₀ + (α / r) · B A
```

The result is an ordinary weight matrix. **A merged LoRA has exactly zero inference overhead** — no extra matmuls, no changed architecture, nothing to install at serving time. This is the property that distinguishes LoRA from the adapter-layer methods that preceded it, which inserted new modules into the forward path and paid latency forever. Lesson 13 covers merging in practice, and Lesson 25 covers when *not* to merge.

## Practice

1. ▢ Compute the trainable parameters for a rank-16 adapter on `q_proj` and `v_proj` only, in a 32-layer model with `d = 4096` and `d_kv = 1024`.

<details markdown="1"><summary>Check</summary>

`q_proj`: 16 × (4096 + 4096) = 131,072.
`v_proj`: 16 × (4096 + 1024) = 81,920.
Per layer: 212,992. Times 32 layers ≈ 6.82M.

Against a ~7B base, that is 0.10%.

</details>

2. ▢ Why does a rank-`r` factorisation of a `d × d` matrix save so much more when `d` is large?

<details markdown="1"><summary>Check</summary>

The full matrix grows as `d²` while the factorisation grows as `2rd` — linearly. The ratio `d / 2r` therefore improves as the model widens.

Which is why LoRA gets *relatively* cheaper on bigger models, and why the method mattered more as models grew.

</details>

3. ▢ What is the intrinsic dimensionality argument, and what is its limit?

<details markdown="1"><summary>Check</summary>

That adapting a well-pretrained model to a task requires movement only within a low-dimensional subspace of parameter space, because pretraining already built the necessary features.

Its limit: it is an empirical finding about *adaptation*, strongest for behaviour and format and weakest for installing substantial new factual knowledge. It also does not tell you what rank is sufficient for your specific task.

</details>

4. ▢ Why does a merged LoRA have zero inference overhead, when the earlier adapter-layer methods did not?

<details markdown="1"><summary>Check</summary>

LoRA's update is additive and linear in the same space as the weight, so `W₀ + (α/r)BA` collapses into a single ordinary matrix. Adapter-layer methods inserted new non-linear modules into the forward path, which cannot be folded away and so add latency at every layer forever.

</details>

5. ▢ True or false: a rank-8 adapter can represent any update a full fine-tune could.

<details markdown="1"><summary>Check</summary>

False. `ΔW = BA` with `B` of `r` columns has rank at most `r`, so it can only reach updates within a rank-8 subspace. A full fine-tune can produce a full-rank update.

The bet is that the update your task needs lies close to such a subspace. When it does not, you see it as a loss floor that more training does not lower — and the fix is more rank or more target modules, not more epochs.

</details>

6. ▢ Under grouped-query attention, `v_proj` output shrinks from 4096 to 512. By what factor does the base matrix shrink, and by what factor does its rank-16 adapter shrink?

<details markdown="1"><summary>Check</summary>

Base: 4096 × 4096 → 4096 × 512, an 8× reduction.
Adapter: 16 × (4096 + 4096) = 131,072 → 16 × (4096 + 512) = 73,728, a 1.8× reduction.

The adapter cost is driven by the sum of dimensions, so it is dominated by the larger one. Narrowing the smaller dimension barely helps.

</details>

## Real-world reps

- [ ] Compute by hand the adapter parameter count for a model and target set you actually intend to use. Keep the number.
- [ ] Build the adapter in code and print the trainable parameter count. It should match your hand calculation. If it does not, find out which module you mis-sized.
- [ ] Tomorrow: recompute the same adapter at rank 8, 32 and 128, and note how the percentage of the base model changes.

## Going further

- [Paper: "LoRA: Low-Rank Adaptation of Large Language Models" — Hu et al., arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
- [Paper: "Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning" — Aghajanyan et al., arXiv:2012.13255](https://arxiv.org/abs/2012.13255)
- [LoRA hyperparameters](../reference/lora-hyperparameters.md)
- [Lesson 9 — Rank, Alpha and Initialisation](0009-rank-alpha-and-initialisation.md)

---

Stuck on any of this, or unsure whether an answer counts? Bring it back to the session — that's what your teacher is for.
