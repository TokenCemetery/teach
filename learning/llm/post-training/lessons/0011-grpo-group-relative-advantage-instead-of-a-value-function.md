---
title: 11. GRPO: Group-Relative Advantage Instead of a Value Function
description: Sample several answers to the same question, and let the group's own spread of rewards say which ones were better
type: lesson
---

# Lesson 11. GRPO: Group-Relative Advantage Instead of a Value Function

**Mission link:** "Explain group-relative advantage in GRPO and why a verifiable reward (a unit test, a checked math answer) changes what RL training can target" is the fifth bullet under Success looks like. This lesson covers group-relative advantage itself; Lesson 12 covers verifiable rewards, the pairing that makes GRPO especially well suited to math and code.
**Primary source:** [Paper: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
**Prerequisites:** [Lesson 10](0010-the-dpo-loss-and-what-it-drops-relative-to-ppo.md)

## Warm-up

1. ▢ What does DPO's loss need, in terms of models, that PPO's setup does not?

<details markdown="1"><summary>Check</summary>

Nothing extra; DPO needs strictly fewer models than PPO. It needs only the policy and a frozen reference model, with no separate reward model and no value function.

</details>

2. ▢ Does removing the separate reward model and RL loop in DPO also remove the KL-penalty tradeoff between staying close to the reference model and moving toward what the preference data rewards?

<details markdown="1"><summary>Check</summary>

No. The same tradeoff, controlled by the same `β`, is still present; it is simply folded directly into the implicit reward term rather than kept as a visually separate penalty.

</details>

## Know this

### The cost PPO's value function specifically adds

Stage 4 (Lesson 8) already established that PPO needs a value function alongside the reward model, initialized from it, to produce the advantage estimates its clipped objective depends on. Shao et al. name exactly why that specific piece is expensive: the value function is typically another model of comparable size to the policy itself, adding real memory and compute cost on top of everything else PPO already needs. They add a second problem specific to language models: in this setting, usually only the very last token of a completion receives a reward score at all, which makes training a value function that is accurate at every earlier token within that completion harder than it might be in a setting with reward feedback at every step.

### GRPO's substitute: let a group of samples supply its own baseline

**Group Relative Policy Optimization (GRPO)** removes the value function entirely, replacing it with something that needs no extra model at all: for a given question `q`, GRPO samples a **group** of `G` outputs, `{o_1, o_2, ..., o_G}`, all from the same (old) policy. A reward model scores each of the `G` outputs, giving `G` rewards, `r_1` through `r_G`. Rather than asking a separately trained value function "was this particular output better than expected," GRPO asks a simpler question answerable directly from the group itself: was this output better than the others sampled for the same question. The **group-relative advantage** for output `i` is the group-normalized reward:

```text
A_i = (r_i - mean(r_1, ..., r_G)) / std(r_1, ..., r_G)
```

applied uniformly to every token in that output. An output that scored above the group's average gets a positive advantage; one that scored below it gets a negative advantage; the size of the advantage is scaled by how spread out the group's rewards happened to be. No value function is trained at all, and the memory and compute cost Lesson 8 traced to it disappears along with it.

### Why this fits reward models particularly well

Shao et al. make a further point worth holding onto: this group-relative comparison is not just a cost-saving shortcut, it matches the shape of the data a reward model was trained on in the first place. A Bradley-Terry reward model (Lesson 4) is trained on comparisons between outputs to the same question; scoring several outputs to the same question and comparing them against each other, rather than against an absolute, separately learned baseline, asks the reward model to do the same kind of relative judgment it was actually trained to make.

### Where the KL penalty moves

GRPO also changes where the KL penalty sits, compared to Lesson 6's RLHF objective. Ouyang et al.'s objective added the KL penalty directly into the per-token reward, before advantages were ever computed from it. Shao et al. instead add the KL divergence between the trained policy and the reference policy as a separate term directly in the loss, alongside the clipped surrogate objective, rather than mixing it into the reward the advantage is computed from. This keeps the reward-based part of the calculation (and the group-relative advantage built from it) uncomplicated by the KL term, while still applying the same kind of restraint on how far the policy drifts from its reference.

## Practice

1. ▢ A group of 4 sampled outputs to the same question receive rewards `{2, 4, 6, 8}` from the reward model. Roughly, which output(s) get a positive group-relative advantage, and which get a negative one?

<details markdown="1"><summary>Hint</summary>

Compute the mean of the group first, then ask which rewards sit above it and which sit below.

</details>

<details markdown="1"><summary>Check</summary>

The mean is 5. The outputs scoring 6 and 8 sit above the mean and get a positive advantage; the outputs scoring 2 and 4 sit below it and get a negative advantage.

</details>

2. ▢ Per Shao et al., name two specific problems with PPO's value function that GRPO's group-relative advantage avoids.

<details markdown="1"><summary>Check</summary>

The value function is typically another model of comparable size to the policy, adding substantial memory and compute cost, and in the LLM setting where usually only the last token gets a reward score, training a value function accurate at every earlier token is harder than in settings with reward feedback at every step.

</details>

3. ▢ Why does Shao et al. describe group-relative comparison as fitting reward models especially well, beyond simply being cheaper than a value function?

<details markdown="1"><summary>Check</summary>

Because reward models are typically trained on comparisons between outputs to the same question in the first place (the same shape Lesson 4's Bradley-Terry loss uses); scoring several outputs to one question and comparing them against each other asks the reward model to make the same kind of relative judgment it was actually trained to make.

</details>

4. ▢ Where does GRPO's KL penalty sit, compared to where the KL penalty sits in Ouyang et al.'s RLHF objective (Lesson 6)?

    - a) In the same place: added directly into the per-token reward before advantages are computed
    - b) GRPO has no KL penalty at all
    - c) GRPO adds the KL divergence as a separate term directly in the loss, alongside the clipped objective, rather than mixing it into the reward
    - d) GRPO replaces the KL penalty with a second reward model

<details markdown="1"><summary>Check</summary>

**c)** is the actual placement Shao et al. describe. (a) describes Ouyang et al.'s approach, which GRPO specifically changes. (b) and (d) both misstate what GRPO does; the same kind of restraint is still present, just relocated.

</details>

## Real-world reps

- [ ] Find a GRPO implementation in a library you have access to, and check how it computes the group-normalized advantage: does it match the mean-and-standard-deviation formula this lesson gives?
- [ ] Read the paragraph in the DeepSeekMath paper (linked above) describing why the value function is costly in the LLM setting specifically, and write one sentence distinguishing the memory-cost argument from the per-token-accuracy argument.
- [ ] Tomorrow: without looking ahead, write a one-sentence prediction for Lesson 12: if a reward model can be replaced by anything that produces a reliable score for each sampled output, what kind of task would let that score come from a deterministic checker instead of a trained model at all?

## Going further

- [Paper: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
