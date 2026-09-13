---
title: 12. Verifiable Rewards: When a Checker Replaces the Reward Model
description: A trained reward model is a guess at what a human would prefer; a unit test or a matched answer is not a guess at all
type: lesson
---

# Lesson 12. Verifiable Rewards: When a Checker Replaces the Reward Model

**Mission link:** "Explain group-relative advantage in GRPO and why a verifiable reward (a unit test, a checked math answer) changes what RL training can target" is the fifth bullet under Success looks like, and this lesson closes it.
**Primary source:** [Paper: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
**Prerequisites:** [Lesson 11](0011-grpo-group-relative-advantage-instead-of-a-value-function.md), [Verifiable reward](../GLOSSARY.md)

## Warm-up

1. ▢ A group of 4 sampled outputs to the same question receive rewards `{2, 4, 6, 8}`. Which outputs get a positive group-relative advantage, and which get a negative one?

<details markdown="1"><summary>Check</summary>

The mean is 5; outputs scoring 6 and 8 sit above it and get a positive advantage, outputs scoring 2 and 4 sit below it and get a negative advantage.

</details>

2. ▢ Why does Shao et al. describe group-relative comparison as fitting reward models especially well?

<details markdown="1"><summary>Check</summary>

Reward models are typically trained on comparisons between outputs to the same question in the first place, so scoring several outputs to one question and comparing them against each other asks the reward model to make the same kind of relative judgment it was actually trained to make.

</details>

## Know this

### What GRPO actually needs from a reward

Nothing about Lesson 11's group-relative advantage requires the score for each sampled output to come from a trained reward model specifically. All the group-normalization formula, `A_i = (r_i - mean(r)) / std(r)`, needs is a number per sampled output, `r_1` through `r_G`, that reflects how good each one was. A trained reward model is one way to produce that number, the way Shao et al.'s own GRPO training does. It is not the only way.

### What a verifiable reward is

A **verifiable reward** is a reward signal produced by a deterministic checker rather than by a learned model: whether a piece of generated code passes a fixed unit test, whether a math problem's final numeric answer exactly matches the known correct one, whether a generated proof or program satisfies a formal check. Nothing about computing a verifiable reward involves guessing at what a human would have preferred; it is a direct, checkable fact about the output, computed the same way every time, with no model of preference standing between the output and its score at all.

### Why this changes what RL training can target

A trained reward model, however well trained, is still fitting a preference judgment: Lesson 5 covered directly how a policy can find ways to score well against it without actually producing the behavior it was meant to reward. A verifiable reward has no analogous failure mode of that shape: a unit test either passes or it does not, and there is no reward-model-specific quirk for a policy to learn to exploit, because there is no learned model standing in for the judgment at all. This opens RL training to targets that were previously hard to reach through human preference alone: a policy can be pushed, group by sampled group, toward outputs that are more often exactly, checkably correct on tasks like mathematics and code, rather than merely more often preferred by a judge (human or model) making a subjective call.

### What this does not change

A verifiable reward is not a free upgrade over a trained reward model in every respect; it only applies where a check for correctness actually exists. Plenty of the behavior post-training is meant to shape (helpfulness, tone, safety, open-ended writing quality) has no deterministic checker that could stand in for a human or model preference judgment; there is no unit test for "this reply was appropriately empathetic." Verifiable rewards fit specifically the tasks where correctness is checkable in the first place, which is why math and code are the domains this combination is built around, not a general replacement for preference-based reward modeling everywhere else.

## Practice

1. ▢ A team wants to train a policy to solve algebra word problems using GRPO. Rather than training a reward model on human preferences between solutions, what could they use instead, and why would it avoid the reward-hacking risk Lesson 5 described?

<details markdown="1"><summary>Check</summary>

A verifiable reward: checking whether the policy's final numeric answer exactly matches the known correct answer. This avoids reward hacking in the reward-model sense because there is no learned model's quirks to exploit; the check is a direct, deterministic fact about the output rather than a trained judgment a policy could learn to game.

</details>

2. ▢ Why would a verifiable reward be a poor fit for training a policy to write more empathetic customer-support replies?

    - a) Verifiable rewards can only be computed for numeric outputs
    - b) There is no deterministic checker for "this reply was appropriately empathetic"; correctness of that kind is not the kind of property a checker can test
    - c) Verifiable rewards always require a separate reward model to interpret them
    - d) GRPO cannot be used with verifiable rewards at all

<details markdown="1"><summary>Check</summary>

**b)** is the actual limitation: verifiable rewards fit tasks where correctness is checkable in the first place, and empathetic tone has no such deterministic check. (a) is too narrow; code correctness is a non-numeric example that still verifies. (c) contradicts the entire point of a verifiable reward, which needs no reward model at all. (d) is false; GRPO's group-normalization machinery works with any per-output score, verifiable or model-produced.

</details>

3. ▢ Does using a verifiable reward change anything about how the group-relative advantage in Lesson 11 is computed?

<details markdown="1"><summary>Check</summary>

No. The same normalization, subtracting the group mean and dividing by the group standard deviation, applies regardless of whether the underlying per-output score, `r_i`, came from a trained reward model or a deterministic checker. What changes is only where that score comes from, not what GRPO does with it.

</details>

## Real-world reps

- [ ] Find a published RL-for-reasoning training setup (a paper, technical report, or open training script) and identify exactly what its verifiable reward checks: an exact-match answer, a unit test suite, a formal proof checker, or something else.
- [ ] Pick a task you find plausible for verifiable rewards (a coding task, a math problem set) and a task you find implausible (an open-ended writing or conversational task), and write one sentence each explaining what a deterministic checker would or would not be able to test.
- [ ] Tomorrow: without looking ahead, write a one-sentence prediction for Stage 7: if verifiable rewards let RL training push a policy toward more often being exactly correct, what kind of new model behavior would you expect to emerge from training heavily on math and code problems this way, beyond just getting more answers right?

## Going further

- [Paper: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
- [Resources](../RESOURCES.md)

---

Stage 6 covered the mechanism (group-relative advantage) and the reward that pairs especially well with it (verifiable checks). Stage 7 covers what happens when this combination is scaled up as the primary way a model is trained: reasoning models, and what training on verifiable rewards at scale actually produces.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
