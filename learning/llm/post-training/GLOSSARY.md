---
title: Glossary
description: "Canonical terms for LLM post-training"
type: glossary
---

# LLM Post-Training Glossary

Canonical terms for aligning a pretrained model: what each training objective maximizes, and what changes as the objective moves from imitating text to optimizing a reward.

## Terms

**Alignment tax**:
The loss of capability (typically measured on pretraining-style benchmarks) that post-training can introduce as a side effect of optimizing for helpfulness or safety.
_Avoid_: regression (a regression is any capability drop; alignment tax names the specific one traded for alignment)

**Bradley-Terry loss**:
The loss function used to train a reward model on pairwise preference data, treating the probability that one completion is preferred over another as a function of the difference between their scalar reward scores.
_Avoid_: preference loss (used loosely for several objectives in this space, including DPO's; Bradley-Terry names the specific pairwise-comparison model reward modeling uses)

**Group-relative advantage**:
GRPO's replacement for a learned value function: for a group of completions sampled for the same prompt, one completion's advantage is its reward minus the group's mean reward, divided by the group's standard deviation, applied to every token in that completion.
_Avoid_: baseline (a baseline is the general RL concept a group mean serves as; this workspace uses the specific name once GRPO is in scope)

**Implicit reward**:
The reward function DPO shows is mathematically implied by a policy and a reference model, without ever training a separate reward model to compute it.
_Avoid_: reward model (DPO's whole argument is that it needs no separate one; conflating the two erases the distinction stage 5 exists to teach)

**KL penalty**:
A term added to an RL objective that penalizes the trained policy for diverging from a fixed reference model's output distribution, keeping optimization against a reward model from producing degenerate text.
_Avoid_: regularization (accurate but generic; name the specific penalty once RLHF is in scope)

**Loss masking**:
Zeroing out the training loss on tokens the model should not learn to produce, such as a prompt or a system message, so gradient updates come only from the tokens the model is meant to generate.
_Avoid_: prompt masking (masking applies to more than the prompt alone, including any non-assistant turn in a multi-turn example)

**Preference pair**:
Two completions to the same prompt, one marked preferred over the other, the unit of data both reward modeling and DPO train on.
_Avoid_: comparison (used across the literature for the same thing; this workspace standardizes on preference pair)

**Reward hacking**:
A policy finding a way to score well against a reward model or a verifiable reward signal without actually producing the behavior the reward was meant to measure.
_Avoid_: gaming, overoptimization (both point at the same failure; this workspace uses reward hacking as the one to use everywhere)

**RLAIF**:
Reinforcement learning from AI feedback: preference labels or a reward signal produced by a model rather than by a human, used in place of or alongside RLHF.
_Avoid_: self-improvement (RLAIF is a specific labeling method; self-improvement is a broader and vaguer claim about what the result is)

**Verifiable reward**:
A reward signal computed by a deterministic checker, such as a unit test result or a matched final numeric answer, rather than by a learned reward model.
_Avoid_: ground truth (ground truth is the answer being checked against; verifiable reward is the signal derived from that check)
