---
title: 20. Reviewing Someone Else's Alignment Recipe
description: Walk the pipeline through every stage this track covered, in order, and settle a disputed claim from the source rather than a confident restatement
type: lesson
---

# Lesson 20. Reviewing Someone Else's Alignment Recipe

**Mission link:** This closes the arc. Every earlier stage produced one thing to check in someone else's post-training pipeline; this lesson is the checklist, plus the discipline of settling a specific, genuinely common conflation from the primary source rather than a confident secondary restatement.
**Primary source:** [Paper: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
**Prerequisites:** every previous lesson in this track, since this one is the synthesis.

## Warm-up

1. ▢ A team has preference data and no specific need to reuse a reward model outside training. Which of DPO and PPO is the more defensible default, and why?

<details markdown="1"><summary>Check</summary>

DPO. It reaches a similar preference-trained result at close to SFT's own cost, needing only the policy and a frozen reference model, with no separate reward model or RL loop to justify unless something specific requires one.

</details>

2. ▢ What does "defend the choice against the one rejected" require, beyond stating the chosen method's benefits?

<details markdown="1"><summary>Check</summary>

Naming which cheaper method was considered first and why it specifically fell short for the task, not merely asserting why the chosen method is good.

</details>

## Know this

### The review checklist: stages in order

When reviewing a proposed or existing post-training pipeline, walk it through the stages of this track in order, asking the same question at each one: is this choice stated and justified, or merely assumed?

**Stage 1, the landscape.** Does the pipeline state which of the SFT/RLHF/DPO/GRPO landscape it is building toward, and does that match the target behavior described, or is "we post-trained the model" left unspecified about which of these was actually used?

**Stage 2, SFT.** Is loss masking on non-assistant tokens actually applied (Lesson 3), and is the chat template used at training time documented clearly enough that serving can reproduce it exactly (Lesson 2)? A pipeline that is vague about either is exposed to a real, previously documented failure mode, not a hypothetical one.

**Stage 3, reward modeling.** If a reward model is trained, is preference data collected as rankings decomposed into pairs, per Lesson 4's method, or as isolated comparisons risking the overfitting Ouyang et al. found? Is reward hacking (Lesson 5) checked for, ideally with something like a held-out preference model, rather than assumed away?

**Stage 4, RLHF-PPO, if used.** Is the KL-penalty coefficient stated and its tradeoff (Lesson 6) acknowledged? Does the pipeline name the models it is running simultaneously and their sizes (Lesson 8), given how directly reward-model and value-function scale affected Ouyang et al.'s own stability?

**Stage 5, DPO, if used.** Is the reference model clearly identified, and is beta's role (the same KL-strength tradeoff as PPO's, per Lesson 10) stated rather than left as an unexplained hyperparameter?

**Stage 6, GRPO, if used.** Is the per-output reward a trained model's score or a verifiable check? This distinction matters enough that it is worth its own check, covered directly below.

**Stage 7, reasoning training, if used.** Is extended reasoning behavior attributed to what actually produced it (RL against a reward, verifiable or not), rather than described as something explicitly programmed in?

**Stage 8, safety tuning, if used.** Does the pipeline state whether harmlessness feedback came from humans or from a model (Lesson 15), and if performance is compared against a human-feedback baseline, is that comparison actually reported, per Bai et al.'s own precedent, rather than assumed favorable?

**Stage 9, evaluation.** Is the alignment tax measured per-benchmark rather than as one collapsed number (Lesson 17), and is an over-refusal or judge-bias check present alongside whatever headline safety or preference score is reported (Lesson 18)?

A pipeline that answers all of these with a stated, defensible choice is a pipeline that has done the work this track describes. A pipeline that answers several of them with silence has not, whatever its final benchmark numbers look like.

### Settling a disputed claim from the source, not from a blog post

A specific, easy-to-make conflation is worth walking through directly, because this track's own Stage 6 notes had to catch it while being written. It is sometimes claimed, casually, that "GRPO trains on verifiable rewards," as though the two were inseparable. Checking Shao et al.'s own paper, the one that introduces GRPO, directly refutes this as stated: DeepSeekMath's GRPO trains against a reward produced by `r_φ`, an explicitly trained reward model, initialized and trained the same way Lesson 4 describes, with no rule-based or ground-truth checker anywhere in its method. The pairing of GRPO with verifiable, rule-based rewards is real and well-documented, but it belongs to DeepSeek-R1 (Lesson 13), a different paper, applying GRPO's group-relative mechanism to a different kind of reward than the one GRPO was introduced with. A secondary source that states "GRPO uses verifiable rewards" as a general fact about the algorithm is quietly merging two separate papers' contributions into one; going back to DeepSeekMath's own method section, rather than trusting the confident merged claim, is what catches it. The mechanism (group-relative advantage) and the reward source (verifiable check versus trained model) are two independent choices, not one inseparable package, and a pipeline that gets this distinction right is a pipeline whose author actually read the sources rather than repeating what "everyone knows" about GRPO.

## Practice

1. ▢ A proposed pipeline states "we use GRPO with verifiable rewards for our math benchmark task" and cites the DeepSeekMath paper as its sole source. Is this citation accurate to what DeepSeekMath's own method actually describes?

<details markdown="1"><summary>Check</summary>

Not entirely. DeepSeekMath's own GRPO trains against a reward from a trained reward model, not a verifiable, rule-based check. The verifiable-reward pairing with GRPO is DeepSeek-R1's contribution, a different paper. The pipeline's actual method (GRPO with a verifiable reward) may well be reasonable, but citing DeepSeekMath alone as its source misattributes where that specific combination comes from.

</details>

2. ▢ A pipeline document says only "we applied RLHF" with no further detail. Using this lesson's checklist, name two specific things that statement leaves unstated that a reviewer should ask about.

<details markdown="1"><summary>Check</summary>

Any two of: the KL-penalty coefficient and whether its tradeoff was considered; the sizes of the models involved (policy, reference, reward model, value function) and whether reward-model scale was chosen deliberately; how preference data was collected and whether reward hacking was checked for; whether the resulting alignment tax was measured, and against what benchmarks.

</details>

3. ▢ A pipeline reports a high safety score from an LLM-as-judge evaluation with no other detail. Per Lesson 18 and this lesson's stage-9 check, what should a reviewer ask for before trusting that score?

<details markdown="1"><summary>Check</summary>

Whether the judge was checked for calibration against known biases (position, verbosity), and whether an over-refusal check exists alongside the safety score, so a high score reflects genuine safety rather than blanket refusal or an exploitable judge.

</details>

## Real-world reps

- [ ] Find a real, published post-training technical report and run it through this lesson's checklist, stage by stage, noting which items are stated explicitly and which are left silent.
- [ ] Find a claim about post-training methods (DPO, PPO, GRPO, or RLAIF) stated confidently in a blog post, tutorial, or forum answer, and check it against the primary paper it should trace back to. Note whether it holds up, is a simplification, or is a genuine conflation like this lesson's GRPO example.
- [ ] Tomorrow: write a short review, three to five sentences, of a real or hypothetical post-training pipeline, naming at least one specific choice you would challenge and what you would ask the person defending it to justify.

## Going further

- [Paper: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
