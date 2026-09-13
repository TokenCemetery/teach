---
title: 15. Constitutional AI: Feedback From a Model, Not a Human
description: Zero human labels for harm, a written list of principles instead, and an assistant that explains its objections rather than deflecting
type: lesson
---

# Lesson 15. Constitutional AI: Feedback From a Model, Not a Human

**Mission link:** "Can say where feedback came from (human or AI) in a given safety-tuning pipeline and what that trades" is the Success looks like bullet this stage serves. This lesson covers Constitutional AI's two-stage method; Lesson 16 covers how well AI feedback holds up against human feedback in a direct, controlled comparison.
**Primary source:** [Paper: "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
**Prerequisites:** [Lesson 14](0014-distilling-a-reasoning-model-down.md)

## Warm-up

1. ▢ Per DeepSeek-AI's own 32B comparison, did training a small model with large-scale RL directly reach the same reasoning performance as distilling from a larger, already RL-trained model?

<details markdown="1"><summary>Check</summary>

No. Direct RL on the 32B base model reached 47.0% pass@1 on AIME 2024, well below the 72.6% the same base model reached when instead fine-tuned on the larger model's distilled reasoning traces.

</details>

2. ▢ What is a verifiable reward, and why does it not have the reward-hacking failure mode a trained reward model has?

<details markdown="1"><summary>Check</summary>

A reward produced by a deterministic checker rather than a learned model; since no learned model's quirks stand between the output and its score, there is no reward-model-specific exploit for a policy to learn.

</details>

## Know this

### Recall the failure this lesson's method is built to avoid

Lesson 5 covered a real, documented failure: RLHF policies over-optimized for harmlessness converged on blanket deflection, recommending users seek therapy at almost any remotely sensitive question, a cheap way to score well on a harmlessness reward model without being genuinely helpful. **Constitutional AI (CAI)** is built specifically to produce a harmless assistant that does not take this shortcut.

### Two stages, and where AI feedback enters each one

The supervised stage, **SL-CAI**, samples responses from an initial model, has the model generate a **self-critique** and a **revision** of its own response against a short, written list of principles (the "constitution" the method is named for), and then fine-tunes the original model on these self-revised responses, ordinary SFT (Stage 2) on data the model produced and improved on its own.

The reinforcement learning stage, **RL-CAI**, samples pairs of responses from the SL-finetuned model, and instead of having a human labeler say which one is better, **uses a model** to make that judgment. A preference model (Lesson 4's Bradley-Terry training) is trained on this dataset of AI-generated preferences, and the policy is then trained with RL against that AI-trained preference model exactly as Lesson 6's RLHF setup would use a human-trained one. Bai et al. name this general technique directly: **RL from AI Feedback (RLAIF)**.

### Zero human labels for harm, and what came out of it

Bai et al. state their result plainly: this entire pipeline trains a "non-evasive" and "relatively harmless" AI assistant "without any human feedback labels for harms" at all. The principles in the constitution, not thousands of human harmfulness judgments, are what shapes the model's behavior. The resulting assistant engages with harmful queries by explaining its objections to them, rather than refusing or deflecting outright, which is a direct answer to the specific over-optimization Lesson 5 documented: a model whose harmlessness training rewards actually engaging thoughtfully, rather than rewarding the cheapest possible refusal, has less incentive to collapse into blanket deflection in the first place.

### The comparison that makes this worth taking seriously

Bai et al. do not just claim this works; they report that crowdworkers preferred the resulting model, "RL-CAI," over models trained using previously collected human feedback labels for harmfulness. Replacing human harm labels with a written constitution and AI-generated preferences did not just match the human-labeled alternative; by their own reported comparison, it did better.

## Practice

1. ▢ In SL-CAI, what does the model do to its own sampled responses before they are used for fine-tuning?

<details markdown="1"><summary>Check</summary>

It generates a self-critique of the response against the written constitution's principles, then produces a revision of the response, and the model is fine-tuned on these revised responses.

</details>

2. ▢ In RL-CAI, what replaces the human labeler that would ordinarily judge which of two sampled responses is better?

<details markdown="1"><summary>Check</summary>

A model. An AI system judges which of two responses is better, and a preference model is trained on this dataset of AI-generated preferences, rather than on human-labeled comparisons.

</details>

3. ▢ Why does Constitutional AI's resulting assistant explaining its objections to a harmful request, rather than refusing outright, directly address the failure Lesson 5 described?

<details markdown="1"><summary>Check</summary>

Lesson 5's blanket-deflection failure arose because refusing outright was a cheap, low-sophistication way to score well on a harmlessness reward model. A training approach whose reward instead favors genuinely engaging with and explaining objections to a request removes the incentive for that cheap shortcut, since deflection alone would not be the highest-scoring option.

</details>

4. ▢ Per Bai et al.'s own comparison, how did crowdworkers rate RL-CAI against a model trained on previously collected human feedback labels for harmfulness?

<details markdown="1"><summary>Check</summary>

They preferred RL-CAI. Replacing human harm labels with a constitution and AI-generated preferences did not merely match the human-labeled alternative in their reported comparison; it was preferred over it.

</details>

## Real-world reps

- [ ] Find a published "constitution" or set of guiding principles used to train an actual model (several have been released publicly), and read three or four of its principles. Note whether they read as specific rules or as general values a model would have to interpret.
- [ ] Read the passage in the Constitutional AI paper (linked above) describing the SL-CAI self-critique-and-revision step, and write one sentence describing what would need to go wrong for a model's self-critique to fail to catch a real problem in its own response.
- [ ] Tomorrow: without looking ahead, write a one-sentence prediction for Lesson 16: given that Constitutional AI replaces human harm labels with AI-generated ones for a single method, would you expect AI feedback to work this well across other kinds of tasks too, such as summarization or general helpfulness, and why or why not?

## Going further

- [Paper: "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
