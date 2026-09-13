---
title: 14. Distilling a Reasoning Model Down
description: Training a 32B model with RL directly lost to just fine-tuning it on a bigger model's own reasoning traces
type: lesson
---

# Lesson 14. Distilling a Reasoning Model Down

**Mission link:** "Can say how a reasoning model's behavior was produced, not just how to prompt it" is the Success looks like bullet this stage serves. Lesson 13 covered DeepSeek-R1-Zero's pure-RL training and its readability problem; this lesson covers DeepSeek-R1's fix, and the surprising result of distilling that fix down to smaller models.
**Primary source:** [Paper: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
**Prerequisites:** [Lesson 13](0013-chain-of-thought-rl-what-deepseek-r1-zero-did-with-rule-based-rewards.md)

## Warm-up

1. ▢ DeepSeek-R1-Zero's reasoning length grew substantially over training with no explicit reward term for it. What actually drove that growth?

<details markdown="1"><summary>Check</summary>

The accuracy reward rewarded getting the final answer right, and longer, more careful reasoning tended to produce more correct answers, so RL training selected for it as a side effect, not because reasoning length was directly rewarded.

</details>

2. ▢ DeepSeek-R1-Zero achieved strong reasoning but suffered poor readability and language mixing. Why is this unsurprising given how its reward was built?

<details markdown="1"><summary>Check</summary>

The reward only checked final-answer correctness and the presence of thinking tags; readability and staying in one language were never part of the score, so nothing in training selected for either one.

</details>

## Know this

### Fixing readability without losing the reasoning

DeepSeek-R1 is DeepSeek-AI's answer to DeepSeek-R1-Zero's readability problem: rather than pure RL from the base model, it adds **cold-start data**, a modest amount of curated data used before the reasoning-focused RL stage, plus multiple training stages built around that RL stage rather than a single pass. This gives the model a starting point already closer to producing readable, single-language output, before the same kind of rule-based, reasoning-focused RL that produced DeepSeek-R1-Zero's capabilities is applied on top of it. The result, DeepSeek-AI report, achieves performance comparable to OpenAI's o1 on reasoning tasks while avoiding the readability and language-mixing problems the pure-RL version had.

### Distillation: fine-tuning smaller models on the bigger model's own reasoning traces

Separately from training DeepSeek-R1 itself, DeepSeek-AI produce six smaller dense models, ranging from 1.5B to 70B parameters, built on existing Qwen and Llama base models. The method is direct: fine-tune each smaller base model on 800,000 curated samples generated using DeepSeek-R1's own training pipeline. This is **ordinary supervised fine-tuning** (Stage 2) on data that happens to consist of a larger reasoning model's own outputs, not a new algorithm. DeepSeek-AI are explicit that they apply only SFT to these distilled models, with no RL stage at all, even though they note an RL stage could plausibly improve them further; their goal in this instance was to demonstrate that distillation alone already works well, leaving a further RL stage for smaller models to future work.

### The result that makes this worth taking seriously

DeepSeek-AI ran a direct comparison that answers a natural question: could a smaller model reach the same reasoning capability by running the same large-scale RL directly on it, instead of distilling from a larger model that already went through that RL? They trained a 32B base model with over 10,000 steps of the same large-scale RL DeepSeek-R1-Zero used, producing "DeepSeek-R1-Zero-Qwen-32B," and compared it against "DeepSeek-R1-Distill-Qwen-32B," the same 32B base model instead fine-tuned on DeepSeek-R1's distilled reasoning traces. On the AIME 2024 math benchmark, the directly-RL-trained model reached 47.0% pass@1; the distilled model reached 72.6%, a large gap that held in the same direction across every benchmark they report. DeepSeek-AI's own conclusion: distilling a more capable model down is both economical and highly effective, while training a smaller model with large-scale RL directly demands enormous compute and may still not match what distillation achieves for free from a model that already did that work.

### The limit distillation has

DeepSeek-AI are careful not to overclaim this: distillation transfers what a stronger model already knows how to do, cheaply, but it does not by itself push capability past what that stronger model can already do. Their own second conclusion states this directly: going beyond the current frontier still requires more capable base models and larger-scale reinforcement learning applied to them, not simply more distillation of what already exists. Distillation is a cheap way to spread an existing capability to smaller models, not a way to manufacture new capability beyond what the model being distilled from already has.

## Practice

1. ▢ A team wants a small, capable reasoning model and considers two paths: distilling from an existing large reasoning model via SFT, or running large-scale RL directly on the small model from its base checkpoint. Per DeepSeek-AI's own 32B comparison, which path would they expect to reach stronger reasoning performance, and by roughly how much on AIME 2024?

<details markdown="1"><summary>Check</summary>

Distillation. DeepSeek-R1-Distill-Qwen-32B reached 72.6% pass@1 on AIME 2024, compared to 47.0% for DeepSeek-R1-Zero-Qwen-32B, trained with over 10,000 steps of large-scale RL directly on the same base model.

</details>

2. ▢ What, specifically, is "distillation" in this lesson's sense, mechanically?

    - a) A new RL algorithm applied to the smaller model
    - b) Ordinary supervised fine-tuning of a smaller base model on curated output samples generated by a larger, already RL-trained reasoning model
    - c) Compressing the larger model's weights directly into a smaller architecture
    - d) Running the larger and smaller models together at inference time

<details markdown="1"><summary>Check</summary>

**b)** is exactly the method DeepSeek-AI describe: SFT on 800k curated samples from DeepSeek-R1's own pipeline, no RL stage. (a), (c), and (d) each describe a different technique this lesson's method is not.

</details>

3. ▢ Per DeepSeek-AI's own two conclusions, could distillation alone push a small model's reasoning capability beyond what DeepSeek-R1 itself, the model being distilled from, can already do?

<details markdown="1"><summary>Check</summary>

No. Their second conclusion states directly that advancing beyond the current frontier still requires more capable base models and larger-scale RL, not more distillation; distillation spreads existing capability cheaply, it does not manufacture new capability beyond the source model's own.

</details>

4. ▢ Why did DeepSeek-R1 add cold-start data and multi-stage training rather than simply reusing DeepSeek-R1-Zero's exact recipe at a larger scale?

<details markdown="1"><summary>Check</summary>

Because DeepSeek-R1-Zero's reasoning came with poor readability and language mixing that pure rule-based RL gave the model no incentive to fix; cold-start data and multi-stage training address that readability problem directly, rather than trying to scale a recipe that never selected for it in the first place.

</details>

## Real-world reps

- [ ] Find the DeepSeek-R1 technical report's Table 6 (linked paper above) and note the gap between DeepSeek-R1-Zero-Qwen-32B and DeepSeek-R1-Distill-Qwen-32B on at least one benchmark other than AIME 2024.
- [ ] Find a published distilled reasoning model (many are released with a name indicating what it was distilled from) and check whether its model card states it was trained with SFT alone, an added RL stage, or both.
- [ ] Tomorrow: for a hypothetical project needing a small, capable reasoning model, decide whether you would reach for distillation from a larger reasoning model or direct RL on the small model itself, and write one sentence citing this lesson's evidence for your choice.

## Going further

- [Paper: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
- [Resources](../RESOURCES.md)

---

Stage 7 covered how reasoning behavior gets produced by RL, and how cheaply it can be spread to smaller models once it exists. Stage 8 turns to a different target for the same family of techniques: not reasoning capability, but safety and refusal behavior.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
