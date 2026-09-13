---
title: LLM Post-Training
description: "Align a base model: SFT, reward modeling, RLHF, DPO, and GRPO, and knowing which one to pick"
type: topic
---

# LLM Post-Training

Be able to take a pretrained base model to an aligned, instruction-following assistant: write the SFT, reward, and preference objectives correctly, choose between RLHF-PPO, DPO, and GRPO for a given team's budget and data, and defend that choice, including what it cost in alignment tax and where it is exposed to reward hacking.

**Latest lesson:** [0020. Reviewing Someone Else's Alignment Recipe](lessons/0020-reviewing-someone-elses-alignment-recipe.md)

## Success looks like

- Write an SFT training loop that masks loss on non-assistant tokens, and explain what breaks in a chat model trained without that mask.
- Train a reward model on preference pairs using the Bradley-Terry loss, and identify a reward-hacked completion from a policy trained against it.
- Derive the RLHF objective (reward minus a KL penalty against a reference model) and say what happens to the policy as the KL penalty is loosened.
- Derive DPO's implicit reward from the same preference data RLHF uses, and say what it gives up by removing the RL loop.
- Explain group-relative advantage in GRPO and why a verifiable reward (a unit test, a checked math answer) changes what RL training can target.
- Given a team's data, budget, and target behavior, choose between SFT alone, DPO, RLHF-PPO, and GRPO, and defend the choice against the one rejected.
- Read an aligned model's evaluation results and separate a genuine capability gain from an artifact of reward hacking or judge bias.

## Constraints

- Algorithm-first, not paper-survey. Each stage teaches one training objective from its loss function outward, what is being maximized and what the gradient does, rather than summarizing a list of papers; the papers anchor each stage as its primary source.
- Small-scale reps: labs run SFT and DPO on a small open model, the same scale discipline `llm/finetuning` uses, and reason from there to what the cited frontier papers report.
- Assumes `llm/transformers` (cross-entropy loss, the backward pass, AdamW) and familiarity with `llm/finetuning`'s adapter mechanics, since this track reuses them rather than re-deriving parameter efficiency.
- No lesson trains a full RLHF pipeline end to end at frontier scale; PPO's cost is demonstrated at small scale and then reasoned about at the scale the cited papers report.

## Out of scope

- Parameter-efficient mechanics (LoRA rank and alpha, QLoRA, DoRA, target modules): see [`llm/finetuning`](../../llm/finetuning/). This track owns the training objective; `llm/finetuning` owns how it gets applied to fewer parameters.
- Cross-entropy loss, the backward pass, and AdamW: see [`llm/transformers`](../../llm/transformers/). Assumed here, not re-taught.
- LLM-as-judge mechanics and human evaluation methodology: see [`llm/evals`](../../llm/evals/). Carried here only as the one capability an aligned model needs, to judge whether alignment training helped, and linked to rather than restated.
- Prompting a reasoning model, or building an agent around one: see [`llm/agents`](../../llm/agents/) (lesson 0017). This track covers how the reasoning behavior is produced by RL training, not how to use it from outside.
- Training a model from random initialization: see [`llm/pretraining`](../../llm/pretraining/).

## The arc

Ten stages, from no prior knowledge to senior judgment. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Lessons | Covers | Done when |
| --- | --- | --- | --- |
| 1. What post-training buys | 0001 to 0001 | Base against instruct/chat model, the SFT/RLHF/DPO/GRPO landscape | Can place a given aligned model's behavior against what post-training stage produced it |
| 2. SFT | 0002 to 0003 | Instruction datasets, chat templates, loss masking on non-assistant tokens | Can write an SFT loop with correct loss masking and explain what breaks without it |
| 3. Reward modeling | 0004 to 0005 | Preference data collection, the Bradley-Terry loss, reward hacking | Can train a reward model and identify a reward-hacked completion against it |
| 4. RLHF via PPO | 0006 to 0008 | The RL objective, the KL penalty against a reference model, why PPO is expensive and unstable | Can derive the RLHF objective and say what loosening the KL penalty does to the policy |
| 5. Direct Preference Optimization | 0009 to 0010 | DPO's implicit reward, what it drops relative to PPO and why that is usually fine | Can derive DPO's implicit reward and say what it gives up relative to PPO |
| 6. GRPO and RL with verifiable rewards | 0011 to 0012 | Group-relative advantage, why it fits math and code | Can explain group-relative advantage and why a verifiable reward changes what RL can target |
| 7. Reasoning models | 0013 to 0014 | Chain-of-thought RL, what DeepSeek-R1 changed, distilling a reasoning model down | Can say how a reasoning model's behavior was produced, not just how to prompt it |
| 8. Safety and refusal tuning | 0015 to 0016 | Red-teaming data, Constitutional AI, RLAIF | Can say where feedback came from (human or AI) in a given safety-tuning pipeline and what that trades |
| 9. Evaluating an aligned model | 0017 to 0018 | Alignment tax, reward hacking detection, linking to `llm/evals` | Can separate a genuine capability gain from a reward-hacking or judge-bias artifact |
| 10. Judgment | 0019 to 0020 | DPO against PPO against GRPO for a given budget, when SFT alone is enough, reviewing someone else's alignment recipe | Trusted to make the call and to explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-what-post-training-buys.md) | What Post-Training Buys | A 100x smaller aligned model beat a raw base model at doing what users actually wanted |
| [0002](lessons/0002-instruction-data-and-the-chat-template.md) | Instruction Data and the Chat Template | A special token marks where a prompt ends and an answer begins, and that boundary has to match at training and serving time |
| [0003](lessons/0003-loss-masking-on-non-assistant-tokens.md) | Loss Masking on Non-Assistant Tokens | Zero out the loss on the prompt, or spend gradient signal teaching the model to predict text it did not generate |
| [0004](lessons/0004-training-a-reward-model-the-bradley-terry-loss.md) | Training a Reward Model: The Bradley-Terry Loss | A reward model never sees an absolute score in training, only which of two completions a human liked more |
| [0005](lessons/0005-reward-hacking.md) | Reward Hacking | A policy learned to say "I can't answer that" to almost everything, because that scored well without being genuinely helpful or harmless |
| [0006](lessons/0006-the-rlhf-objective-reward-minus-a-kl-penalty.md) | The RLHF Objective: Reward Minus a KL Penalty | One term chases the reward model's score; a second term is the leash that keeps the policy from running off with it |
| [0007](lessons/0007-ppo-why-the-update-gets-clipped.md) | PPO: Why the Update Gets Clipped | A big win on one batch of sampled data is not trustworthy evidence for a big step; PPO refuses to fully believe it |
| [0008](lessons/0008-why-ppo-is-expensive-and-unstable.md) | Why PPO Is Expensive and Unstable | Four models, not one, have to fit in memory at once, and the two that scale worst are exactly the ones RLHF adds |
| [0009](lessons/0009-dpos-implicit-reward-why-the-partition-function-cancels.md) | DPO's Implicit Reward: Why the Partition Function Cancels | An intractable normalizing term stands between a reward and its optimal policy, until a difference of two rewards makes it vanish |
| [0010](lessons/0010-the-dpo-loss-and-what-it-drops-relative-to-ppo.md) | The DPO Loss, and What It Drops Relative to PPO | One loss, two models, no sampling loop, and the same beta a KL penalty would have used |
| [0011](lessons/0011-grpo-group-relative-advantage-instead-of-a-value-function.md) | GRPO: Group-Relative Advantage Instead of a Value Function | Sample several answers to the same question, and let the group's own spread of rewards say which ones were better |
| [0012](lessons/0012-verifiable-rewards-when-a-checker-replaces-the-reward-model.md) | Verifiable Rewards: When a Checker Replaces the Reward Model | A trained reward model is a guess at what a human would prefer; a unit test or a matched answer is not a guess at all |
| [0013](lessons/0013-chain-of-thought-rl-what-deepseek-r1-zero-did-with-rule-based-rewards.md) | Chain-of-Thought RL: What DeepSeek-R1-Zero Did With Rule-Based Rewards | No learned reward model, no SFT step first, and extended reasoning emerged anyway because it kept getting more answers right |
| [0014](lessons/0014-distilling-a-reasoning-model-down.md) | Distilling a Reasoning Model Down | Training a 32B model with RL directly lost to just fine-tuning it on a bigger model's own reasoning traces |
| [0015](lessons/0015-constitutional-ai-feedback-from-a-model-not-a-human.md) | Constitutional AI: Feedback From a Model, Not a Human | Zero human labels for harm, a written list of principles instead, and an assistant that explains its objections rather than deflecting |
| [0016](lessons/0016-rlaif-how-well-ai-feedback-actually-matches-human-feedback.md) | RLAIF: How Well AI Feedback Actually Matches Human Feedback | A model judging its own outputs, at its own size, still beat plain supervised fine-tuning |
| [0017](lessons/0017-measuring-the-alignment-tax.md) | Measuring the Alignment Tax | The tax does not show up everywhere at once, and one axis even measured an improvement instead |
| [0018](lessons/0018-reward-hacking-after-the-fact.md) | Reward Hacking After the Fact | A held-out reward model can catch drift during training; a finished model needs a different kind of check |
| [0019](lessons/0019-choosing-between-sft-dpo-ppo-and-grpo.md) | Choosing Between SFT, DPO, PPO, and GRPO | Each method earns its added cost over the one before it only when the cheaper one genuinely cannot express the target behavior |
| [0020](lessons/0020-reviewing-someone-elses-alignment-recipe.md) | Reviewing Someone Else's Alignment Recipe | Walk the pipeline through every stage this track covered, in order, and settle a disputed claim from the source rather than a confident restatement |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
