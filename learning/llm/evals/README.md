---
title: Evals
description: "Prove a model change helped: build the eval, hold out the data honestly, and defend the number against contamination"
type: topic
---

# Learning: Evals

Be able to build an eval that catches a regression a vibe check would miss, and use it to make a go/no-go call on a model change (a fine-tune, a prompt change, a RAG change) that you can defend with a number instead of a feeling.

**Latest lesson:** [6. Judge Bias and Human Agreement](lessons/0006-judge-bias-and-human-agreement.md)

## Success looks like

- Design a held-out eval set for a given model change that resists contamination and would catch a regression a casual read-through would miss.
- Use that eval to make and defend a go/no-go call on shipping the change, naming the number and why it is trustworthy.
- Compare an LLM-as-judge approach against task-specific metrics for a given case, and choose between them on the merits rather than by default.

## Constraints

- No domain restriction: covers evaluating fine-tunes, prompt changes, and RAG changes alike, since the same eval discipline applies to all three.
- No fixed stack or prior-experience assumption.

## Out of scope

- Judging a variant, held-out design, metrics and the regression suite as taught inside one fine-tuning arc: `llm/finetuning` lessons 0020-0024 already own that, subordinated to fine-tuning specifically. This workspace owns evaluation as the subject and links back rather than restating.

## The arc

Five stages, a trustworthy eval to a defended go/no-go call. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Held-out data and contamination | 0001 to 0002 | Train/test split discipline, contamination detection and its sources | Can design a held-out set that resists contamination |
| 2. Task-specific metrics | 0003 to 0004 | Exact match, F1, BLEU/ROUGE, code-execution metrics, choosing per task | Can pick and justify a metric for a stated task |
| 3. LLM-as-judge | 0005 to 0006 | Judge-prompt design, calibration, position and verbosity bias, agreement with humans | Can build a judge prompt and name its failure modes |
| 4. Building the harness | 0007 to 0008 | Eval frameworks, reproducible runs, turning a design into a number | Has a runnable eval harness that produces a trustworthy number |
| 5. The go/no-go call | 0009 to 0010 | Statistical significance vs noise, regression thresholds, communicating the decision | Can defend a ship/no-ship call with a number and say why it's trustworthy |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-held-out-and-contamination.md) | Held-out Data and Contamination | Why an eval number is only as trustworthy as what the model never saw |
| [0002](lessons/0002-designing-contamination-resistance.md) | Designing Contamination Resistance | Preventing contamination in a custom eval set from the start, instead of only detecting it after the fact |
| [0003](lessons/0003-task-specific-metrics.md) | Task-Specific Metrics | Exact match, token-level F1, and BLEU/ROUGE, and the failure mode each one has |
| [0004](lessons/0004-code-execution-metrics.md) | Code-Execution Metrics and Choosing a Metric | Functional correctness, the pass@k estimator, and a decision principle for picking a metric per task |
| [0005](lessons/0005-judge-prompt-design-and-calibration.md) | Judge-Prompt Design and Calibration | How to write a judge prompt that grades consistently, and what it means for a judge to be calibrated before trusting it |
| [0006](lessons/0006-judge-bias-and-human-agreement.md) | Judge Bias and Human Agreement | Position bias and verbosity bias in LLM-as-judge, and how to measure a judge's agreement with human raters |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
