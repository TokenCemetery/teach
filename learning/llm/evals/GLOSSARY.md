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

**Cohen's kappa**:
A statistic measuring two raters' agreement after correcting for the agreement expected by chance alone: `κ = (p_o − p_e) / (1 − p_e)`. A kappa of 0 means no better than chance; a kappa can go negative. Known to underestimate agreement when one rating category is much rarer than the others.
_Avoid_: percent agreement (the uncorrected, raw figure; kappa is specifically the chance-corrected version, and the two can tell different stories)

**Data contamination**:
Eval data, or a close paraphrase of it, ending up inside a model's training data (typically pretraining, via a benchmark scraped into web-crawl data) or a model being iteratively tuned against the same eval set until it stops measuring the underlying skill.
_Avoid_: leakage, cheating

**Held-out data**:
Eval examples, or close paraphrases of them, that the model being judged never saw during training or fine-tuning. A score is only informative when the data behind it is held out.
_Avoid_: test set (ambiguous with a training-pipeline split), unseen data

**Over-refusal**:
A model refusing a prompt that is actually safe, typically because it resembles an unsafe prompt in wording or touches a sensitive-sounding topic without being harmful. A genuinely different failure mode from a jailbreak, and one a red-team (unsafe-prompt-only) eval cannot detect.
_Avoid_: false refusal (used interchangeably in some sources; this workspace standardizes on "over-refusal")

**Red-teaming**:
Deliberately constructing inputs designed to make a model produce unsafe output, whether by a human tester or an automated attack-generation method, then measuring how often those inputs succeed (a jailbreak) against a given model and its defenses.
_Avoid_: reporting only attack success rate as "the safety eval"; it measures nothing about over-refusal, a distinct failure mode needing its own test set
