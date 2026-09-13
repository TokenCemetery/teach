---
title: 16. Loss Spikes and the Optimizer's Own Instabilities
description: The same spike can come from a bad batch or from the optimizer itself, and telling them apart takes a controlled comparison
type: lesson
---

# Lesson 16. Loss Spikes and the Optimizer's Own Instabilities

**Mission link:** "Given a loss curve, can say whether a spike is recoverable or needs a restart from an earlier checkpoint" is the Success looks like bullet this stage serves. This lesson covers what a loss spike can actually come from, and the standard mitigation; Lesson 17 covers the schedule that shapes training around it.
**Primary source:** [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Prerequisites:** [Lesson 15](0015-mixed-precision-at-scale-bfloat16-and-stochastic-rounding.md), [Loss spike](../GLOSSARY.md)

## Warm-up

1. ▢ Why does bf16's wider exponent range make it more forgiving during training than fp16, even though bf16 has less precision?

<details markdown="1"><summary>Check</summary>

bf16 keeps fp32's full 8 exponent bits, giving it the same dynamic range as fp32, so large or small values that show up in gradients and activations at scale are less likely to overflow or underflow it, even though it represents values less precisely within that range than fp16 does.

</details>

2. ▢ What limitation did Rae et al. report even after using stochastic rounding for bf16 parameter updates?

<details markdown="1"><summary>Check</summary>

Stochastic rounding does not fully recover the performance of ordinary mixed-precision training; it is a mitigation, not a complete fix.

</details>

## Know this

### A loss spike does not announce its own cause

A **loss spike**, a sudden, sharp rise in training loss partway through a run, can come from more than one place: a single unusually difficult or malformed batch, a numeric precision issue like the ones Lesson 15 described, or something about the optimizer itself becoming unstable at the scale being trained. Reading a spike off a loss curve tells you it happened; it does not by itself tell you which of these caused it, and the right response, a restart, a hyperparameter change, or nothing at all, depends on knowing which.

### A concrete case: Adafactor against Adam at scale

Rae et al. give a worked example of exactly this kind of investigation. Adafactor is an optimizer that uses less memory than Adam, which matters directly for the memory budget Lesson 8 counted: a smaller optimizer-state footprint could mean fitting a larger model, or fitting the same model with less sharding. At smaller scales, Rae et al. found Adafactor pretraining stable and performant. At 7.1 billion parameters, that stopped holding: they observed loss divergences training with Adafactor that they had not seen at 1.4 billion parameters, even though the Adafactor run used a lower maximum learning rate (`6 × 10^-5`) than the stable Adam baseline it was compared against (`1.2 × 10^-4`). A lower learning rate is normally the first thing to try against instability; here it was not enough, which is what let Rae et al. conclude the instability was coming from the optimizer itself at this scale, not simply from the learning rate being set too high.

### The standard mitigation: clipping by the global gradient norm

Whatever an instability's underlying cause, the most direct mitigation Rae et al. use is **gradient clipping** by global norm: compute the norm (overall magnitude) of the full gradient vector across every parameter in the model, and if that norm exceeds a chosen threshold, rescale the entire gradient down proportionally so its norm equals the threshold exactly, before the optimizer step uses it. This bounds how large a single step's update can be, regardless of what produced an unusually large gradient in the first place. Rae et al. use a clipping value of 1 for most of their models, but reduce it to 0.25 specifically for their two largest, the 7.1B model and Gopher itself, for improved stability, a direct, concrete example of tightening this safeguard as scale increases rather than leaving it fixed.

## Practice

1. ▢ A team observes a loss spike partway through a training run. Name two different underlying causes this lesson describes that could produce the same visible spike.

<details markdown="1"><summary>Check</summary>

Any two of: a single unusually difficult or malformed batch, a numeric precision issue (such as an overflow or a rounding problem in bf16 training), or an instability coming from the optimizer itself becoming unstable at the scale being trained.

</details>

2. ▢ Why did lowering the learning rate fail to stabilize the 7.1B Adafactor run, and what did Rae et al. conclude from that failure?

<details markdown="1"><summary>Hint</summary>

The Adafactor run already used a lower learning rate than the stable Adam baseline it was compared against.

</details>

<details markdown="1"><summary>Check</summary>

The Adafactor run used a maximum learning rate of `6 × 10^-5`, lower than the stable Adam baseline's `1.2 × 10^-4`, and still showed instabilities. Since a lower learning rate did not fix it, Rae et al. concluded the instability was coming from the optimizer itself at this scale, not simply from too high a learning rate.

</details>

3. ▢ What does global gradient-norm clipping actually do to a gradient whose norm exceeds the clipping threshold?

    - a) It discards that gradient entirely and skips the optimizer step for that batch
    - b) It rescales the entire gradient vector proportionally so its norm equals the threshold
    - c) It rounds the gradient's values to a lower-precision format
    - d) It permanently lowers the learning rate for the rest of training

<details markdown="1"><summary>Check</summary>

**b)** is exactly the mechanism: proportional rescaling to bring the norm down to the threshold, not a discard, a precision change, or a permanent schedule change. (a), (c), and (d) each describe a different, unrelated intervention.

</details>

4. ▢ Rae et al. use a clipping value of 1 for most model sizes but reduce it to 0.25 specifically for the 7.1B model and Gopher (280B). What does this concrete choice illustrate about how stability safeguards are set?

<details markdown="1"><summary>Check</summary>

That a safeguard like gradient clipping is not necessarily a fixed constant across every scale; here it was tightened specifically for the largest models, where instability risk was greatest, rather than left at the same value used for smaller, more stable runs.

</details>

## Real-world reps

- [ ] Find where gradient clipping is exposed as a configuration option in a training framework you have access to, and note its default clipping value, if any is set.
- [ ] Read the paragraph in the Gopher paper (linked above) describing the Adafactor-versus-Adam comparison, and write one sentence stating what evidence, specifically, ruled out "the learning rate was simply too high" as the explanation.
- [ ] Tomorrow: without looking ahead, write a one-sentence prediction for Lesson 17: given that Rae et al. warm up the learning rate slowly at the very start of training rather than starting at the maximum value immediately, what problem might starting at full learning rate from a freshly initialized, untrained network cause?

## Going further

- [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
