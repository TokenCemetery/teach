---
title: 7. PPO: Why the Update Gets Clipped
description: A big win on one batch of sampled data is not trustworthy evidence for a big step; PPO refuses to fully believe it
type: lesson
---

# Lesson 7. PPO: Why the Update Gets Clipped

**Mission link:** Deriving the RLHF objective (Lesson 6) means little without knowing what "optimize the policy against it using PPO" actually does. This lesson supplies that mechanism, which the rest of Stage 4 and the mission's judgment stage both depend on being able to name concretely rather than treat as a black box.
**Primary source:** [Paper: "Proximal Policy Optimization Algorithms", Schulman et al., 2017](https://arxiv.org/abs/1707.06347)
**Prerequisites:** [Lesson 6](0006-the-rlhf-objective-reward-minus-a-kl-penalty.md)

## Warm-up

1. ▢ In the RLHF objective, what happens to the policy as the KL-penalty coefficient `β` shrinks toward zero?

<details markdown="1"><summary>Check</summary>

The penalty for diverging from the SFT policy nearly vanishes, so the objective reduces to chasing the reward model's score with almost nothing holding the policy back, putting it at risk of the reward hacking Lesson 5 described.

</details>

2. ▢ What is the difference between "PPO" and "PPO-ptx" in Ouyang et al.'s naming, and which term distinguishes them?

<details markdown="1"><summary>Check</summary>

"PPO" sets the pretraining-gradient coefficient `γ` to 0; "PPO-ptx" uses a nonzero `γ`, mixing pretraining-data log-likelihood gradients into training, which is what reduces the alignment tax.

</details>

## Know this

### The problem an unconstrained update has

Schulman et al. start from a simpler surrogate objective, one that a "vanilla" policy-gradient method would maximize directly: `L^CPI(θ) = E[r_t(θ) · Â_t]`, where `r_t(θ) = policy(a|s) / policy_old(a|s)` is the ratio between the new and old policy's probability of the action actually taken, and `Â_t` is the estimated **advantage**, roughly, how much better or worse that action turned out than expected. Maximizing `L^CPI` with no further constraint gives the optimizer every incentive to push `r_t(θ)` as far as it can in whichever direction increases the objective. Schulman et al. state the problem directly: "without a constraint, maximization of `L^CPI` would lead to an excessively large policy update." A large estimated advantage on one sampled batch is not trustworthy evidence that an equally large step is safe to take everywhere; overreacting to it can destabilize training.

### PPO's fix: clip the ratio, then take the pessimistic case

Schulman et al.'s actual objective is:

```text
L^CLIP(θ) = E[ min( r_t(θ)·Â_t, clip(r_t(θ), 1-ε, 1+ε)·Â_t ) ]
```

with `ε` a small constant (they use `0.2`). The `clip(...)` term caps the ratio `r_t(θ)` to the interval `[1-ε, 1+ε]`, which removes the incentive to push it further outside that range. Taking the `min` of the clipped and unclipped versions, rather than the clipped version alone, is what makes this a **pessimistic bound**: Schulman et al. explain that this scheme "only ignore[s] the change in probability ratio when it would make the objective improve, and... include[s] it when it makes the objective worse." In plain terms, a move that looks like it is helping gets capped rather than fully rewarded, so the optimizer cannot extract unlimited credit from one encouraging batch, while a move that is actually hurting is not shielded by the same cap, and its full cost still counts.

### Why this is a different kind of stability control from the KL penalty

Lesson 6's KL penalty and this lesson's clipping are both stability mechanisms, but they operate at different scopes and should not be conflated. The KL penalty measures the trained policy against the original, fixed **SFT reference model**, and limits how far the whole training run is allowed to drift from that fixed point over its entire course. PPO's clipping compares the policy to **itself from just before the current update** (`policy_old`), and limits how large any single optimization step is allowed to be, regardless of where the policy currently sits relative to the SFT model. One controls total drift over the run; the other controls the size of each individual step along the way. Both are needed, and neither substitutes for the other: a small per-step clip does not prevent many small steps from eventually drifting far from the reference model, and a KL penalty against the reference model does nothing to stop any single step from being destructively large.

## Practice

1. ▢ A single batch of sampled completions produces an unusually large estimated advantage for one action, purely because of how that batch happened to be sampled. Why is it risky to let the policy update fully in proportion to that advantage, with no cap?

<details markdown="1"><summary>Check</summary>

Because one batch's estimated advantage is not reliable evidence that an equally large change is safe everywhere; overreacting to a single encouraging (or discouraging) sample can push the policy an excessively large distance in one step, which is exactly the instability PPO's clipping is built to prevent.

</details>

2. ▢ Why does PPO take the minimum of the clipped and unclipped surrogate terms, rather than just using the clipped term by itself?

    - a) Taking the minimum makes the objective a pessimistic bound: a move that looks like an improvement gets capped, while a move that looks harmful is not protected by the same cap and still counts fully
    - b) The minimum is only used for computational efficiency and has no effect on the learned policy
    - c) Using the clipped term alone would make the ratio unbounded
    - d) The minimum ensures the ratio always equals exactly 1

<details markdown="1"><summary>Check</summary>

**a)** is Schulman et al.'s own stated reasoning. (b) understates a real effect on optimization behavior. (c) has the clipping's actual purpose backwards; clipping bounds the ratio, it does not leave it unbounded. (d) misreads what clipping does; the ratio is bounded to an interval around 1, not forced to equal exactly 1.

</details>

3. ▢ A team's RLHF setup uses a large KL-penalty coefficient `β` but no per-step clipping at all (an unclipped surrogate objective). Is this setup protected against a single destructively large policy update?

<details markdown="1"><summary>Check</summary>

No. A large `β` limits how far the policy can drift from the SFT reference model over the course of training, but it does nothing to prevent any one individual update, based on one batch's estimated advantage, from being excessively large. These are two different stability controls, and removing one does not get compensated for by the other.

</details>

## Real-world reps

- [ ] Find where a PPO implementation you have access to exposes the clip parameter (often named `epsilon`, `clip_range`, or similar), and note its default value against the `0.2` Schulman et al. report using.
- [ ] Read the paragraph in the PPO paper (linked above) describing why `L^CPI` alone would lead to an excessively large update, and write one sentence in your own words explaining what specifically about an unconstrained surrogate objective causes that.
- [ ] Tomorrow: without looking ahead, write a one-sentence prediction for Lesson 8: given that RLHF now needs a policy, a frozen reference (SFT) model for the KL penalty, a reward model, and something to produce the advantage estimates this lesson's clipping formula depends on, how many separate large models do you expect to be involved in a single PPO training step?

## Going further

- [Paper: "Proximal Policy Optimization Algorithms", Schulman et al., 2017](https://arxiv.org/abs/1707.06347)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
