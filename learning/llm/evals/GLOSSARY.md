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

**Drift**:
The real-world relationship between features and outcomes changing over time, so a model or eval built on older data progressively stops matching current reality. Specifically what a large gap between held-out and more-recent ("next-day") data indicates; a gap between offline and live results on the identical input is a different problem, an engineering error, not drift.
_Avoid_: training-serving skew (a broader term covering any train/serve discrepancy; drift is specifically the time-based, real-world-changed-underneath-the-model case)

**Faithfulness (groundedness)**:
Whether each claim in a generated answer is actually supported by the retrieved context it's meant to rest on, rather than fabricated, contradicted, or embellished with an unsupported detail. A claim-level check: a mostly-faithful answer can still hide one unsupported claim.
_Avoid_: citation correctness (a stricter, separate check on whether the specific cited passage for a claim is the one that actually supports it, distinct from whether the claim is grounded at all)

**Guardrail metric**:
A metric an experiment or a production system isn't trying to optimize, tracked specifically to catch a change quietly damaging it while a different metric (the OEC) is being improved. Reporting an OEC's gain without a guardrail metric checked alongside it can hide a real regression.
_Avoid_: OEC (a guardrail metric is explicitly not being optimized; conflating the two defeats the purpose of tracking either separately)

**Held-out data**:
Eval examples, or close paraphrases of them, that the model being judged never saw during training or fine-tuning. A score is only informative when the data behind it is held out.
_Avoid_: test set (ambiguous with a training-pipeline split), unseen data

**OEC (Overall Evaluation Criterion)**:
The specific metric, or small weighted combination, an experiment is actually trying to move. A good OEC candidate is both movable (sensitive enough to shift within a feasible experiment) and causally connected to the outcome that actually matters, not merely correlated with it.
_Avoid_: any metric that's easy to move but not causally tied to the real outcome (Kohavi's own example: "photos viewed" moves easily but has little causal effect on revenue)

**Over-refusal**:
A model refusing a prompt that is actually safe, typically because it resembles an unsafe prompt in wording or touches a sensitive-sounding topic without being harmful. A genuinely different failure mode from a jailbreak, and one a red-team (unsafe-prompt-only) eval cannot detect.
_Avoid_: false refusal (used interchangeably in some sources; this workspace standardizes on "over-refusal")

**Red-teaming**:
Deliberately constructing inputs designed to make a model produce unsafe output, whether by a human tester or an automated attack-generation method, then measuring how often those inputs succeed (a jailbreak) against a given model and its defenses.
_Avoid_: reporting only attack success rate as "the safety eval"; it measures nothing about over-refusal, a distinct failure mode needing its own test set

**Tail latency**:
The slowest fraction of requests (commonly reported as p95 or p99), as opposed to the average. An unchanged average latency can hide a meaningfully worse tail, and at scale, a request fanning out to many backend calls only completes once all of them finish, making the tail the thing that actually decides real-world response time.
_Avoid_: average latency (an aggregate that can stay flat while the tail, which dominates real user experience, gets meaningfully worse)

**Task success**:
Comparing an agent trajectory's actual end state against an annotated goal state, crediting any sequence of actions that reaches the correct outcome rather than only one predetermined reference sequence. More faithful than step accuracy, which can only credit the one trajectory it was given.
_Avoid_: step accuracy (a narrower, brittler measurement: matching each action to a reference trajectory, which wrongly penalizes a different, equally valid path to the same correct outcome)

**Training-serving skew**:
Any discrepancy between a model's offline (training or held-out) performance and its live, in-production performance. Google's own guidance splits this into distinct comparisons with distinct causes; a discrepancy on the identical input between an offline score and a live result specifically indicates an engineering error, not drift or a modeling problem.
_Avoid_: drift (the narrower, time-based case where the real world has changed since training; not every offline/online discrepancy is drift)

**Trajectory**:
The full sequence of tool calls, intermediate decisions, and turns an agent produces while working a task, as opposed to the single output a per-response eval scores. A per-response metric has nothing to attach to here, which is why agent evaluation needs its own metrics.
_Avoid_: response (too narrow; a trajectory is the whole multi-step, often multi-turn process, not any single output within it)
