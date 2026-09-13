---
title: 17. Warmup, Decay, and Growing the Batch Mid-Run
description: Starting slow, decaying on a schedule, and letting the batch size itself change partway through training
type: lesson
---

# Lesson 17. Warmup, Decay, and Growing the Batch Mid-Run

**Mission link:** "Given a loss curve, can say whether a spike is recoverable or needs a restart from an earlier checkpoint" is the Success looks like bullet this stage serves. Lesson 16 covered spikes and the clipping that guards against them; this lesson covers the schedule that shapes the run around that guard.
**Primary source:** [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Prerequisites:** [Lesson 16](0016-loss-spikes-and-the-optimizers-own-instabilities.md)

## Warm-up

1. ▢ What does global gradient-norm clipping do to a gradient whose norm exceeds the clipping threshold, and why did Rae et al. reduce the threshold specifically for their two largest models?

<details markdown="1"><summary>Check</summary>

It rescales the entire gradient proportionally so its norm equals the threshold, bounding how large a single update can be. Rae et al. reduced the threshold from 1 to 0.25 specifically for the 7.1B model and Gopher (280B), for improved stability at that scale.

</details>

2. ▢ Why did lowering the learning rate fail to stabilize Rae et al.'s 7.1B Adafactor run, and what did that failure indicate?

<details markdown="1"><summary>Check</summary>

The Adafactor run already used a lower learning rate than the stable Adam baseline and still showed instabilities, which indicated the instability came from the optimizer itself at that scale, not simply from too high a learning rate.

</details>

## Know this

### Starting slow on purpose

Rae et al. do not begin training at the maximum learning rate their schedule uses. Instead, they warm the learning rate up from `10^-7` to the maximum value gradually, over the first 1,500 steps, before letting it follow the rest of the schedule. A freshly initialized network's very first updates are the least informed ones in the entire run: the weights have seen no data yet, so an update computed from them is more likely to be an unhelpful, oversized correction than a later update computed once the network already fits the data reasonably well. Starting the learning rate near zero and ramping it up gives those earliest, least trustworthy updates a smaller effect on the weights, rather than letting them swing the model as hard as a fully warmed-up update would.

### Decaying afterward

Once warmup finishes, Rae et al. decay the learning rate by a factor of 10 over the rest of training, following a cosine schedule: a smooth curve that starts at the maximum learning rate and decreases toward the final value shaped like one quarter of a cosine wave, rather than dropping in sudden steps. This is a separate decision from warmup, aimed at a different point in training: while warmup protects the very beginning of the run, decay is about taking smaller, more careful steps as training progresses and the loss landscape near a good solution generally calls for finer adjustments than the large steps useful early on.

### Bigger models, lower peak learning rates

Rae et al. state this relationship plainly: as model size increases, they decrease the maximum learning rate the schedule warms up to and decays from. A learning rate that is perfectly reasonable for a small model is not automatically safe for a much larger one; picking a per-model maximum learning rate, rather than reusing one fixed value across every size trained, is part of what keeps larger runs inside the range Lesson 16's clipping and this lesson's warmup are meant to protect.

### The batch size itself can change mid-run

Alongside the learning rate schedule, Rae et al. describe an additional lever: increasing the batch size during training itself. Gopher's own batch size grew from three million to six million tokens per batch over the course of its training run, not fixed from the first step to the last. A larger batch gives a less noisy, more reliable gradient estimate at each step and better hardware utilization, but starting an entire run at the largest batch size immediately is not necessarily required to get those benefits throughout; growing into it partway through is a schedule decision in its own right, alongside the learning rate's warmup and decay, rather than something that has to be fixed for the whole run from the start.

## Practice

1. ▢ Why might starting training at the maximum learning rate immediately, with no warmup, be riskier than warming up gradually, given what a freshly initialized network's first updates look like?

<details markdown="1"><summary>Check</summary>

The network's earliest updates, computed before it has seen any data, are the least informed in the entire run and more likely to be oversized, unhelpful corrections. A full-strength learning rate applied to such an update could swing the weights hard in a bad direction; warmup limits how much effect those earliest, least trustworthy updates can have.

</details>

2. ▢ What is the practical difference between what warmup protects against and what cosine decay is aimed at?

<details markdown="1"><summary>Check</summary>

Warmup protects the very start of training, when the network's updates are least informed. Cosine decay is about later training, gradually taking smaller steps as the loss landscape near a good solution generally calls for finer adjustments than the larger steps useful earlier on. They address different points in the same run, not the same problem twice.

</details>

3. ▢ Per Rae et al., does a larger model get a higher or a lower maximum learning rate than a smaller one, all else equal?

<details markdown="1"><summary>Check</summary>

A lower maximum learning rate. Rae et al. state directly that as model size increases, they decrease the maximum learning rate the schedule uses.

</details>

4. ▢ Gopher's batch size grew from three million to six million tokens per batch over the course of training, rather than starting at six million from step one. Name one plausible reason for growing into the larger batch size instead of starting there immediately.

<details markdown="1"><summary>Check</summary>

Any reasonable account is acceptable, such as: earlier in training, when updates are already less stable (per warmup's reasoning), adding a very large batch on top of that may not be necessary to get a useful gradient estimate, and growing the batch size later takes advantage of the larger batch's benefits (a less noisy gradient, better hardware utilization) once training has already reached a more stable region.

</details>

## Real-world reps

- [ ] Find a training framework's documentation for its learning-rate scheduler options, and identify whether it exposes a warmup phase, a cosine decay phase, or both, and how each is configured.
- [ ] Sketch, on paper, a rough learning-rate-against-training-step curve combining warmup (a short ramp up from near zero) followed by cosine decay (a smooth curve down to a much smaller final value), labeling roughly where the 1,500-step warmup Rae et al. describe would sit relative to a run of, say, 300,000 total steps.
- [ ] Tomorrow: for a model size you choose (small, medium, or large, in your own terms), decide qualitatively whether you would expect its maximum learning rate to be closer to Gopher's or to a much smaller model's, and write one sentence for why, based on this lesson's model-size relationship.

## Going further

- [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [Resources](../RESOURCES.md)

---

Stage 7 covered the numerics and schedule that keep a single training run stable. Stage 8 turns to what happens across the many days such a run actually takes: how progress survives being saved, resumed, and interrupted by a failure partway through.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
