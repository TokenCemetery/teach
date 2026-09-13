---
title: 8. Why PPO Is Expensive and Unstable
description: Four models, not one, have to fit in memory at once, and the two that scale worst are exactly the ones RLHF adds
type: lesson
---

# Lesson 8. Why PPO Is Expensive and Unstable

**Mission link:** Deriving the RLHF objective and its clipping mechanism (Lessons 6 and 7) explains what PPO optimizes; this lesson explains what it actually costs to run, which is what makes DPO (Stage 5) worth considering as an alternative at all.
**Primary source:** [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Prerequisites:** [Lesson 7](0007-ppo-why-the-update-gets-clipped.md)

## Warm-up

1. ▢ Why does PPO clip the probability ratio between the new and old policy, rather than letting the surrogate objective grow unbounded?

<details markdown="1"><summary>Check</summary>

Because a large estimated advantage from one sampled batch is not reliable evidence that an equally large policy update is safe; clipping bounds how far a single update can move the policy in response to it, preventing a destructively large step.

</details>

2. ▢ What is the difference in scope between the KL penalty (Lesson 6) and PPO's per-step clipping (Lesson 7)?

<details markdown="1"><summary>Check</summary>

The KL penalty limits how far the policy drifts from the fixed SFT reference model over the whole training run. Clipping limits how large any single optimization step can be relative to the policy's own state just before that step. Neither substitutes for the other.

</details>

## Know this

### Four models, not one

RLHF via PPO is not one model being trained; it requires several models present at once, each doing a different job: the **policy** being trained (initialized from the SFT model); a frozen copy of the **SFT model** itself, kept around purely to compute the KL penalty (Lesson 6) against; the **reward model** (Lesson 4), which scores the policy's sampled outputs; and a **value function**, used to produce the advantage estimates PPO's clipped objective (Lesson 7) depends on. Ouyang et al. state directly that their value function is initialized from the reward model, making it a fifth full copy of a large model's worth of parameters in its own right, distinct from the reward model itself despite sharing its starting point. Four to five large models occupying memory and consuming compute simultaneously, rather than one, is a real, structural cost that has nothing to do with how well or badly training happens to be going.

### Where the instability specifically comes from

Ouyang et al. give a concrete account of where scale interacts badly with this setup. They found that a 175-billion-parameter reward model could achieve lower validation loss than a smaller one, but at two costs: its training was more unstable, which made it a worse choice to initialize a PPO value function from, and using a 175-billion-parameter reward model and value function together substantially increased PPO's compute requirements on top of the policy's own cost. Their resolution was practical rather than theoretical: they found a 6-billion-parameter reward model stable across a wide range of learning rates and just as effective for training strong PPO models, and used that single 6B reward model for every policy size they trained, including their 175B policy.

### Why this specific tradeoff is worth remembering

This is a genuinely counterintuitive result worth holding onto: a smaller reward model was not a compromise forced by lack of resources, it was the more reliable choice at the scale Ouyang et al. tested. Reward model and value function training, run at very large scale, does not automatically inherit the smoother, more predictable scaling behavior that a straightforward pretraining loss (Stage 3's scaling laws, from a different track) shows. Instability at scale is not just an inconvenience to route around; it directly shaped what Ouyang et al. actually built, and is a real reason PPO's full four-or-five-model setup, run at the largest possible scale in every part, is expensive to attempt and unreliable when attempted anyway.

## Practice

1. ▢ Name the four models (or five, counting the value function separately from the reward model it is initialized from) involved in a PPO training step for RLHF, and what each one is used for.

<details markdown="1"><summary>Check</summary>

The policy being trained; a frozen SFT model, used to compute the KL penalty; the reward model, which scores the policy's outputs; and the value function (initialized from the reward model but trained separately), which produces the advantage estimates PPO's clipped objective needs.

</details>

2. ▢ Per Ouyang et al., what two costs came with using a 175B reward model and value function, even though it achieved lower validation loss than a smaller one?

<details markdown="1"><summary>Check</summary>

Its training was more unstable, making it a worse choice to initialize a PPO value function from, and using it substantially increased PPO's compute requirements, on top of the cost of the policy itself.

</details>

3. ▢ A team assumes that a larger, more accurate reward model is always the better choice for RLHF, since it achieves lower validation loss. Per Ouyang et al.'s own finding, is this assumption safe?

    - a) Yes, a lower-loss reward model is always the better choice regardless of scale
    - b) No; a 175B reward model had more unstable training and higher compute cost, and a smaller 6B reward model was stable and just as effective for training strong PPO models
    - c) No, because larger reward models cannot be used with PPO at all
    - d) Yes, but only because Ouyang et al. never actually tested a 175B reward model

<details markdown="1"><summary>Check</summary>

**b)** is exactly Ouyang et al.'s own finding: lower validation loss did not translate into the better practical choice once training stability and compute cost were considered. (a) ignores their own reported tradeoff. (c) overstates the finding; the issue was stability and cost, not incompatibility. (d) is factually wrong; they explicitly report testing and rejecting the 175B option for these reasons.

</details>

## Real-world reps

- [ ] Find a technical report or blog post describing a real RLHF training setup, and see whether it states the relative sizes of its policy, reward model, and value function. Note whether the reward model matches the policy's size or is deliberately smaller.
- [ ] Read Ouyang et al.'s Appendix C section on reward model training (linked above) and write one sentence on what they found training was sensitive to, versus what it was not very sensitive to.
- [ ] Tomorrow: without looking ahead, write a one-sentence prediction for Stage 5: given that PPO needs a reward model, a value function, and an RL loop on top of the policy itself, what would a method that produces a similar result without a separate reward model or an RL loop actually have to do differently?

## Going further

- [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Resources](../RESOURCES.md)

---

Stage 4 covered what RLHF-PPO optimizes and what it costs to run. Stage 5 covers an alternative built specifically to need less of both: no separate reward model, and no RL loop at all.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
