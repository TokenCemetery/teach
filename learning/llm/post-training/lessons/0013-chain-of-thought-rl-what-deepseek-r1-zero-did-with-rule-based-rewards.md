---
title: 13. Chain-of-Thought RL: What DeepSeek-R1-Zero Did With Rule-Based Rewards
description: No learned reward model, no SFT step first, and extended reasoning emerged anyway because it kept getting more answers right
type: lesson
---

# Lesson 13. Chain-of-Thought RL: What DeepSeek-R1-Zero Did With Rule-Based Rewards

**Mission link:** "Can say how a reasoning model's behavior was produced, not just how to prompt it" is the Success looks like bullet this stage serves. This lesson covers DeepSeek-R1-Zero's pure-RL training and what emerged from it; Lesson 14 covers the fix that turned it into a usable model, and what distillation bought on top of that.
**Primary source:** [Paper: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
**Prerequisites:** [Lesson 12](0012-verifiable-rewards-when-a-checker-replaces-the-reward-model.md)

## Warm-up

1. ▢ What is a verifiable reward, and why does it not have the same reward-hacking failure mode a trained reward model has?

<details markdown="1"><summary>Check</summary>

A reward signal produced by a deterministic checker rather than a learned model; since no learned model's quirks stand between the output and its score, there is no reward-model-specific exploit for a policy to learn, the way there is with a trained reward model.

</details>

2. ▢ Why is a verifiable reward a poor fit for training more empathetic customer-support replies?

<details markdown="1"><summary>Check</summary>

There is no deterministic checker for "this reply was appropriately empathetic"; verifiable rewards fit tasks where correctness is checkable in the first place, and tone is not that kind of property.

</details>

## Know this

### Training directly on a base model, with no SFT step first

DeepSeek-R1-Zero is trained with large-scale RL applied directly to a pretrained base model, with no SFT step beforehand at all, the first stage of Lesson 1's usual three-step pipeline skipped entirely. The reward it trains against is purely **rule-based**, built from exactly two checks: an **accuracy reward**, which for math problems checks whether the final answer, given in a specified format such as inside a box, exactly matches the correct one, or for coding problems runs a compiler against predefined test cases; and a **format reward**, which checks only that the model's thinking process is placed between a pair of tags marking where it begins and ends. DeepSeek-AI state directly that they apply neither an outcome nor a process neural reward model at all: no trained reward model of any kind stands between the model's output and its score.

### Extended reasoning emerged, it was not programmed in

Nothing in this reward design explicitly instructs the model to reason for longer, show intermediate steps, or reconsider a wrong turn. DeepSeek-AI report that these behaviors emerged anyway, over the course of RL training: because a rule-based accuracy reward simply rewards getting the final answer right, and longer, more careful reasoning tends to get more final answers right, RL training naturally selected for more of it, without anyone specifying "reason longer" as a target.

### The "aha moment"

DeepSeek-AI describe a specific, striking instance of this: at an intermediate point during training, DeepSeek-R1-Zero began allocating more thinking time to a problem specifically by reevaluating its own initial approach midway through, a self-correction behavior nobody wrote a reward term for directly. They describe this as "not only an 'aha moment' for the model but also for the researchers observing its behavior," and frame it as a demonstration of what RL training makes possible that direct instruction does not: rather than explicitly teaching the model how to solve a problem, rule-based rewards supplied the right incentive, and a genuinely new problem-solving behavior emerged from optimizing against it.

### What pure RL alone did not fix

DeepSeek-R1-Zero's reasoning capability came with real costs DeepSeek-AI do not hide: poor readability, and language mixing (switching between languages within a single response in a way no user asked for). Nothing about a purely rule-based, correctness-only reward gives the model any incentive to be readable or to stay in one language; those checks were never part of the score at all, so nothing selected for them. DeepSeek-R1 itself, the model built to fix this, is the subject of Lesson 14.

## Practice

1. ▢ DeepSeek-R1-Zero's reward has no explicit term rewarding longer chains of reasoning, yet the model's reasoning length grew substantially over training. What does this lesson's account say actually drove that growth?

<details markdown="1"><summary>Check</summary>

The accuracy reward simply rewards getting the final answer right, and longer, more careful reasoning tended to produce more correct final answers, so RL training selected for it as a side effect of optimizing for correctness, not because reasoning length was directly rewarded.

</details>

2. ▢ Why does DeepSeek-AI describe the accuracy reward as "rule-based" rather than as a reward model?

    - a) It is still a trained neural network, just a smaller one
    - b) It is a deterministic check (exact-match against a known answer, or a compiler running fixed test cases), with no learned model involved in producing the score at all
    - c) It is rule-based only for code problems, and a neural reward model is used for math
    - d) "Rule-based" and "reward model" mean the same thing in this paper

<details markdown="1"><summary>Check</summary>

**b)** is exactly what DeepSeek-AI state: no outcome or process neural reward model is applied at all. (a) and (c) both assume a learned component that the paper explicitly says is absent. (d) collapses a distinction the paper is careful to draw.

</details>

3. ▢ DeepSeek-R1-Zero achieves strong reasoning performance but suffers from poor readability and language mixing. Given how its reward was constructed, is this surprising?

<details markdown="1"><summary>Check</summary>

No. The reward only checked final-answer correctness and the presence of thinking tags; nothing about readability or staying in one language was ever part of the score, so RL training had no incentive to select for either one, regardless of how good the model's reasoning became.

</details>

## Real-world reps

- [ ] Read the "Aha Moment" passage in the DeepSeek-R1 paper (linked above, Table 3's surrounding text) and write, in your own words, what specific behavior the model exhibited that the researchers had not explicitly trained it to do.
- [ ] Find a documented example (in this paper or elsewhere) of a model trained with a narrowly specified reward producing an unintended emergent behavior, and compare it to the "aha moment": was the emergent behavior beneficial, harmful, or both?
- [ ] Tomorrow: without looking ahead, write a one-sentence prediction for Lesson 14: given that DeepSeek-R1-Zero's pure rule-based RL produced strong reasoning but poor readability, what would you add to the training process, and at what stage, to fix readability without losing the reasoning capability?

## Going further

- [Paper: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
