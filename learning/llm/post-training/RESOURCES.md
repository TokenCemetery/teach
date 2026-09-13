---
title: Resources
description: "Trusted sources for LLM post-training"
type: resources
---

# LLM Post-Training Resources

## Knowledge

- [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
  The InstructGPT paper. Defines the SFT, reward-model, PPO pipeline most RLHF work since has followed, and measures the alignment tax against a purely pretrained model. Use for: stages 1, 2, 3, and 9's alignment-tax framing.
- [Paper: "Proximal Policy Optimization Algorithms", Schulman et al., 2017](https://arxiv.org/abs/1707.06347)
  Introduces PPO as a general reinforcement-learning algorithm, independent of language models. Use for: stage 4's core algorithm, read before its language-model-specific application.
- [Paper: "Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback", Bai et al., 2022](https://arxiv.org/abs/2204.05862)
  Anthropic's account of the same SFT-to-RLHF recipe at production scale, including where reward hacking and over-optimization against the reward model showed up in practice. Use for: stage 3's reward-hacking material and stage 4's account of what actually goes wrong.
- [Paper: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
  Derives a closed-form reward implied by a policy and a reference model, replacing the separate reward model and RL loop with a single supervised-style loss on preference pairs. Use for: stage 5's central derivation.
- [Paper: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
  Introduces GRPO, replacing PPO's learned value function with a group-relative baseline computed from multiple sampled completions per prompt. Use for: stage 6's central algorithm.
- [Paper: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
  Trains extended chain-of-thought reasoning primarily through RL against verifiable rewards, and describes distilling the resulting behavior into smaller models. Use for: stage 7's primary source.
- [Paper: "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
  Replaces human-labeled harmlessness preferences with a model critiquing and revising its own outputs against a written set of principles. Use for: stage 8's central case of feedback produced by a model rather than a human.
- [Paper: "RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback", Lee et al., 2023](https://arxiv.org/abs/2309.00267)
  A direct, controlled comparison of RLAIF against RLHF on the same tasks, reporting where AI feedback matches human feedback and where it does not. Use for: stage 8, as the empirical complement to Constitutional AI's method.
- [Paper: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
  A published RLHF recipe at open-model scale, including reward model training details and an iterative RLHF process across multiple rounds. Use for: cross-checking stages 3 and 4 against a complete, reproducible recipe.
- [Documentation: "TRL - Transformer Reinforcement Learning", Hugging Face](https://huggingface.co/docs/trl/index)
  The library this track's SFT and DPO labs actually run, with worked configuration for each trainer. Use for: stages 2, 4, and 5's hands-on reps.

## Gaps

- No primary source yet on preference-data quality: annotator disagreement, labeling instructions, and how preference-data collection choices bias a trained reward model. Needed before stage 3's data-quality material can be fully grounded.
- Alignment-tax measurement beyond InstructGPT's own report is thin; a more recent, model-agnostic treatment would strengthen stage 9.
- No production account yet of a full DPO-versus-PPO-versus-GRPO cost comparison from a single team's infrastructure; stage 10's judgment lesson currently has to synthesize this from separate papers rather than one source that already made the comparison.
