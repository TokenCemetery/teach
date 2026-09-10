---
title: Glossary
description: "Canonical terms for evals"
type: glossary
---

# Evals Glossary

Canonical terms for proving whether a model change helped, and for defending that a number reflects it.

## Terms

**Annotation guideline**:
A written definition of each rating category, with concrete borderline examples and how they were resolved, given to every human rater before they start. Low inter-rater agreement often signals a missing or ambiguous guideline rather than unreliable raters.
_Avoid_: rating rubric (used interchangeably elsewhere; this workspace uses "annotation guideline" as the term)

**Citation correctness**:
Whether the specific passage cited for a claim actually supports that claim, a stricter, per-citation check than faithfulness. A claim can be faithful (grounded in the retrieved set somewhere) while still being attributed to the wrong citation, or to none at all.
_Avoid_: faithfulness (a related but separate check; faithfulness asks whether a claim is supported by the retrieved context at all, citation correctness asks whether its specific cited source actually supports it)

**Cohen's kappa**:
A statistic measuring two raters' agreement after correcting for the agreement expected by chance alone: `κ = (p_o − p_e) / (1 − p_e)`. A kappa of 0 means no better than chance; a kappa can go negative. Known to underestimate agreement when one rating category is much rarer than the others.
_Avoid_: percent agreement (the uncorrected, raw figure; kappa is specifically the chance-corrected version, and the two can tell different stories)

**Data contamination**:
Eval data, or a close paraphrase of it, ending up inside a model's training data (typically pretraining, via a benchmark scraped into web-crawl data) or a model being iteratively tuned against the same eval set until it stops measuring the underlying skill.
_Avoid_: leakage, cheating

**Faithfulness (groundedness)**:
Whether each claim in a generated answer is actually supported by the retrieved context it's meant to rest on, rather than fabricated, contradicted, or embellished with an unsupported detail. A claim-level check: a mostly-faithful answer can still hide one unsupported claim.
_Avoid_: citation correctness (a stricter, separate check on whether the specific cited passage for a claim is the one that actually supports it, distinct from whether the claim is grounded at all)

**Held-out data**:
Eval examples, or close paraphrases of them, that the model being judged never saw during training or fine-tuning. A score is only informative when the data behind it is held out.
_Avoid_: test set (ambiguous with a training-pipeline split), unseen data

**Over-refusal**:
A model refusing a prompt that is actually safe, typically because it resembles an unsafe prompt in wording or touches a sensitive-sounding topic without being harmful. A genuinely different failure mode from a jailbreak, and one a red-team (unsafe-prompt-only) eval cannot detect.
_Avoid_: false refusal (used interchangeably in some sources; this workspace standardizes on "over-refusal")

**Red-teaming**:
Deliberately constructing inputs designed to make a model produce unsafe output, whether by a human tester or an automated attack-generation method, then measuring how often those inputs succeed (a jailbreak) against a given model and its defenses.
_Avoid_: reporting only attack success rate as "the safety eval"; it measures nothing about over-refusal, a distinct failure mode needing its own test set

**Task success**:
Comparing an agent trajectory's actual end state against an annotated goal state, crediting any sequence of actions that reaches the correct outcome rather than only one predetermined reference sequence. More faithful than step accuracy, which can only credit the one trajectory it was given.
_Avoid_: step accuracy (a narrower, brittler measurement: matching each action to a reference trajectory, which wrongly penalizes a different, equally valid path to the same correct outcome)

**Trajectory**:
The full sequence of tool calls, intermediate decisions, and turns an agent produces while working a task, as opposed to the single output a per-response eval scores. A per-response metric has nothing to attach to here, which is why agent evaluation needs its own metrics.
_Avoid_: response (too narrow; a trajectory is the whole multi-step, often multi-turn process, not any single output within it)
