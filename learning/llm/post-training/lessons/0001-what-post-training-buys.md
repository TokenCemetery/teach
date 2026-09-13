---
title: 1. What Post-Training Buys
description: A 100x smaller aligned model beat a raw base model at doing what users actually wanted
type: lesson
---

# Lesson 1. What Post-Training Buys

**Mission link:** "Given a team's data, budget, and target behavior, choose between SFT alone, DPO, RLHF-PPO, and GRPO, and defend the choice" is the mission's central decision, and it starts with knowing what problem post-training solves that pretraining alone does not.
**Primary source:** [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Prerequisites:** none

## Know this

### A base model is not automatically a good assistant

A pretrained base model, the product of `llm/pretraining`'s entire arc, is trained to predict likely next tokens given whatever distribution of text it saw. That is not the same skill as following a user's actual instructions, and making a base model bigger does not close that gap by itself. Ouyang et al. state this plainly: "making language models bigger does not inherently make them better at following a user's intent." A large base model can produce outputs that are untruthful, unhelpful, or simply not what was asked for, not because it lacks capability, but because nothing in pretraining specifically trained it to use that capability the way a user wants.

### The headline result

Ouyang et al.'s central result makes the size of this gap concrete: in human evaluations, outputs from their 1.3-billion-parameter **InstructGPT** model were preferred over outputs from the 175-billion-parameter GPT-3 model it started from, despite having roughly 100 times fewer parameters. Post-training did not make the model bigger or smarter in any raw sense; it changed what the model's existing capability was aimed at, and that aim mattered more to human raters than another two orders of magnitude of scale.

### The three-step pipeline

Ouyang et al.'s recipe, still the reference shape most later RLHF work is described against, has three steps:

1. **Collect demonstrations, train a supervised policy.** Human labelers write examples of the desired behavior for a range of prompts; the base model is fine-tuned on these with ordinary supervised learning. This step is **SFT** (supervised fine-tuning), Stage 2's subject.
2. **Collect comparisons, train a reward model.** Labelers rank multiple outputs from the SFT model for the same prompt; a separate model, the **reward model**, is trained to predict which output a human would prefer. This is Stage 3's subject.
3. **Optimize the policy against the reward model with PPO.** The SFT model is further fine-tuned using reinforcement learning, treating the reward model's score as the reward signal to maximize. This is Stage 4's subject, and steps 2 and 3 can be repeated, collecting more comparisons on the current best policy to train a new reward model and a new policy in turn.

### Alignment tax, introduced

Post-training is not free of cost even when it works. Ouyang et al. found their aligned models performed slightly worse on some public NLP benchmarks (a reading-comprehension benchmark, a discrete-reasoning benchmark, a commonsense benchmark, and a translation benchmark, among others) than the original base model had. They name this an **alignment tax**: a real, measured cost to certain capabilities, paid in exchange for behavior humans preferred overall. They also found a partial fix: mixing the PPO updates with updates that increase the likelihood of the original pretraining data (which they call **PPO-ptx**) recovered much of that lost performance without giving up the preference gains post-training was built to produce. The tax is not fixed or unavoidable; it is a measured tradeoff that later techniques can partially pay down.

### The landscape ahead

SFT alone (Stage 2) is the cheapest step and already changes a lot of behavior. Reward modeling and RLHF via PPO (Stages 3 and 4) add a second, reinforcement-learning phase on top of it, at real added cost and complexity. Direct Preference Optimization (Stage 5) later reaches for a similar result without a separate reward model or an RL loop at all. GRPO (Stage 6) adapts the RL approach to tasks with a verifiable, checkable answer, such as math or code, rather than a human preference judgment. Safety-specific tuning (Stage 8) applies the same family of techniques to a different target. Each of these is a different answer to the same underlying question this lesson opened: how does a model's existing capability get aimed at what a person actually wants, and at what cost.

## Practice

1. ▢ InstructGPT's 1.3-billion-parameter model was preferred over the 175-billion-parameter GPT-3 model in human evaluations. What does this result argue about the relationship between raw parameter count and being good at following a user's intent?

<details markdown="1"><summary>Check</summary>

That they are not the same thing. A much smaller model, aimed at the task through post-training, beat a much larger model that had not been. Scale alone did not produce the behavior humans preferred; how the model's capability was aimed did.

</details>

2. ▢ Put these three steps of Ouyang et al.'s pipeline in order: (a) train a reward model on human comparisons of model outputs, (b) fine-tune the policy against the reward model using PPO, (c) fine-tune a base model on human-written demonstrations.

<details markdown="1"><summary>Check</summary>

c, a, b: first collect demonstrations and train a supervised policy (SFT), then collect comparisons and train a reward model, then optimize the policy against that reward model with PPO.

</details>

3. ▢ What is an alignment tax, per Ouyang et al.'s own finding, and what did they find could partially offset it?

<details markdown="1"><summary>Check</summary>

A measured drop in performance on certain public NLP benchmarks that came with post-training's alignment gains, even though human raters preferred the aligned model overall. Mixing PPO updates with updates that increase the likelihood of the original pretraining data (PPO-ptx) recovered much of that lost performance without giving up the preference gains.

</details>

4. ▢ Which of these best describes what SFT, reward modeling, and RLHF-PPO each do in Ouyang et al.'s pipeline?

    - a) SFT imitates human-written demonstrations directly; reward modeling learns to predict human preference between outputs; RLHF-PPO optimizes the policy against that learned preference signal
    - b) All three steps train the reward model, at increasing scale
    - c) SFT and RLHF-PPO are the same step, run twice for stability
    - d) Reward modeling replaces the base model entirely before PPO begins

<details markdown="1"><summary>Check</summary>

**a)** is the actual division of labor across the three steps. (b), (c), and (d) each collapse steps that do genuinely different things: imitating demonstrations, learning a preference signal, and optimizing against that signal are three separate steps, not one repeated.

</details>

## Real-world reps

- [ ] Find a model card or technical report for an open "instruct" or "chat" model, and note which of Ouyang et al.'s three steps it explicitly says it used (SFT, a reward model, and/or RL), and which, if any, it substitutes with a different method.
- [ ] Read the abstract of the InstructGPT paper (linked above) and write, in one sentence, what specific harms (beyond simply "unhelpful") Ouyang et al. name as motivating the need for alignment.
- [ ] Tomorrow: without looking ahead, write a one-sentence prediction for Stage 2: given that SFT is described as imitating human-written demonstrations directly, what kind of mistake would you expect a naive SFT implementation to make if it trained on every token in a training example, including the prompt itself?

## Going further

- [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
