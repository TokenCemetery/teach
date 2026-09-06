---
title: Evals
description: "Prove a model change helped: build the eval, hold out the data honestly, and defend the number against contamination"
type: topic
---

# Learning: Evals

Be able to build an eval that catches a regression a vibe check would miss, and use it to make a go/no-go call on a model change — a fine-tune, a prompt change, a RAG change — that you can defend with a number instead of a feeling.

**Latest lesson:** _none yet_

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

{N} stages, {start} to {end}. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
|---|---|---|
| 1. {Name} | {What it covers} | {The capability that closes the stage} |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| _none yet_ | | |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
