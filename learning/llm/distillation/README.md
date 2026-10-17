---
title: Distillation
description: "Distill a large model into a smaller one and defend it: soft targets, logit and sequence-level losses, synthetic data, on-policy training, and what the student lost"
type: topic
---

# Learning: Distillation

Train a smaller model to do what a larger one does by learning from the larger model's outputs, knowing what each form of distillation transfers and what it cannot. End able to choose between distilling, quantizing and training a small model directly for a given task and budget, measure honestly what the student lost, and review someone else's claim that a distilled model "matches the teacher".

**Latest lesson:** [27. When the Usual Answer Is Wrong](lessons/0027-when-the-usual-answer-is-wrong.md)

## Success looks like

- Explain why a teacher's soft targets carry more training signal than hard labels, and set the temperature and loss weights of a distillation run.
- Write the token-level distillation loss for an LLM, choose between forward and reverse KL, and say when a tokenizer mismatch rules logit distillation out.
- Distill at sequence level or from a teacher's generated data, and say what each transfers that the other does not.
- Build a synthetic distillation set filtered for quality, and check whether the teacher's license and terms permit training on its outputs.
- Explain exposure bias, and say when on-policy distillation is worth its cost over training on fixed teacher outputs.
- Predict what a student will and will not inherit from its teacher, including capability it cannot absorb and traits nobody intended to pass on.
- Choose a student size and a data volume with the teacher's own cost counted in the budget.
- Measure what a student lost against its teacher and against a model of the same size trained without one.
- Choose between distilling, quantizing and fine-tuning a small model directly, review someone else's distillation claim by naming what it hides, replace a model others depend on with a student, and say when the usual answer is the wrong one.

## Constraints

- Assumes comfort reading Python and PyTorch, and knowing what cross-entropy loss, a softmax and a training loop are. No prior knowledge of distillation, and no reinforcement learning beyond the idea of sampling from a model.
- Grounded in papers and model reports. Where a number is one paper's result on its own setup, the lesson says so, because distillation results depend heavily on the teacher, the student and the data.
- Practice runs on a laptop for stages 1 and 2, with a classifier small enough for a CPU. Later reps distill between two small open models, which a free GPU notebook is enough for.

## Out of scope

- Distilling a reasoning model by fine-tuning on its long chains of thought: see [`llm/post-training`](../../llm/post-training/), lesson 0014. That lesson stays as the reasoning-model case; this track teaches distillation in general and links to it rather than restating it.
- Running supervised fine-tuning through LoRA or QLoRA adapters: see [`llm/finetuning`](../../llm/finetuning/). This track owns the distillation objective and data; how the training is applied to fewer parameters stays there.
- Running a pretraining run: see [`llm/pretraining`](../../llm/pretraining/). Distillation as a pretraining signal is taught here as a loss and a data choice (lesson 0007), not as a pretraining run.
- Building an eval: see [`llm/evals`](../../llm/evals/) and its [go/no-go sheet](../../llm/evals/reference/go-no-go.md). This track uses an eval to compare a student with its teacher and does not re-teach how to build one.
- Shrinking a model by lowering its precision: see [`llm/quantization`](../../llm/quantization/). This track is the other way to shrink a model, with fewer parameters, and the comparison between the two is part of stage 9.
- Pruning as a method in its own right. Lesson 0007 shows it paired with distillation in Minitron, and teaches only the distillation half.

## The arc

Nine stages, from why a small model can learn from a large one to the judgment to review someone else's distillation. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Why distillation works | 0001 to 0003 | Teacher and student, soft targets and what they carry, temperature and the combined loss | Can say why soft targets teach more than hard labels and set the temperature |
| 2. Logit distillation for LLMs | 0004 to 0007 | Token-level distillation, forward and reverse KL, the shared-tokenizer constraint, distillation as a pretraining signal | Can write the token-level loss and say when it cannot be used |
| 3. Sequence-level distillation | 0008 to 0009 | Training on the teacher's decoded outputs, and choosing between token and sequence level | Can say what each level transfers and pick one from what the teacher exposes |
| 4. Synthetic-data distillation | 0010 to 0013 | Generated instruction data, rationales and explanation traces, filtering, licensing and terms | Can build a filtered distillation set and check that its use is permitted |
| 5. On-policy distillation | 0014 to 0016 | Exposure bias, GKD and MiniLLM, what on-policy training costs and buys | Can say when on-policy distillation earns its cost |
| 6. What the student inherits | 0017 to 0019 | Fidelity against generalization, the imitation gap, the capacity gap, traits passed on unintentionally | Can predict what a student will and will not pick up from its teacher |
| 7. Sizing | 0020 to 0021 | Distillation scaling laws, data volume, the teacher's cost in the budget | Can choose a student size and data volume and defend the compute |
| 8. Measuring what was lost | 0022 to 0023 | Agreement with the teacher against task quality, baselines, held-out tasks, contamination | Can measure what a student lost and defend the number |
| 9. Judgment | 0024 to 0027 | Distill, quantize or fine-tune small, reviewing a claim, replacing a model others depend on, when the usual answer is wrong | Trusted to make the call on a distillation and to explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-what-distillation-buys.md) | What Distillation Buys | A small student trained to imitate a large teacher, and why imitation can beat training the student on the labels alone |
| [0002](lessons/0002-soft-targets.md) | Soft Targets | What the probabilities a teacher gives to wrong answers carry, and why they are a richer training signal than a hard label |
| [0003](lessons/0003-temperature.md) | Temperature | Softening both distributions with a temperature, the T squared correction, and mixing in the hard-label loss |
| [0004](lessons/0004-token-level-distillation.md) | Token-Level Distillation | Matching the teacher's next-token distribution at every position of a sequence |
| [0005](lessons/0005-forward-and-reverse-kl.md) | Forward and Reverse KL | Why forward KL spreads the student over every mode of the teacher and reverse KL makes it commit to one |
| [0006](lessons/0006-the-tokenizer-constraint.md) | The Tokenizer Constraint | Why logit distillation needs a shared vocabulary, and what cross-tokenizer methods give up |
| [0007](lessons/0007-distilling-during-pretraining.md) | Distilling During Pretraining | How Gemma 2 and Minitron used a teacher's distribution as a training signal at scale, and what storing logits costs |
| [0008](lessons/0008-sequence-level-distillation.md) | Sequence-Level Distillation | Training the student on the teacher's decoded outputs instead of on its distributions |
| [0009](lessons/0009-token-or-sequence.md) | Token or Sequence | What each level transfers, combining them, and choosing from whether the teacher exposes logits or only text |
| [0010](lessons/0010-distilling-from-generated-data.md) | Distilling From Generated Data | Building an instruction set from a teacher's generations, as Self-Instruct and Alpaca did |
| [0011](lessons/0011-rationales-and-explanation-traces.md) | Rationales and Explanation Traces | Training on the teacher's reasoning as well as its answers, as Distilling Step-by-Step and Orca did |
| [0012](lessons/0012-filtering-synthetic-data.md) | Filtering Synthetic Data | Checking, filtering and deduplicating generated data before training on it, because volume does not fix bad examples |
| [0013](lessons/0013-licensing-and-terms.md) | Licensing and Terms | What a provider's terms and an open model's license allow you to do with its outputs |
| [0014](lessons/0014-exposure-bias.md) | Exposure Bias | Why a student trained on teacher prefixes meets its own mistakes at inference without having trained on them |
| [0015](lessons/0015-gkd-and-minillm.md) | GKD and MiniLLM | Sampling from the student and scoring with the teacher, and the divergence and mixing choices that come with it |
| [0016](lessons/0016-on-policy-distillation-in-practice.md) | On-Policy Distillation in Practice | What on-policy distillation costs per step, what it buys, and how Qwen3 used it for its small models |
| [0017](lessons/0017-fidelity-and-generalization.md) | Fidelity and Generalization | Why a student that generalizes well can still disagree with its teacher, and which of the two you need |
| [0018](lessons/0018-the-imitation-gap.md) | The Imitation Gap | Why imitating a stronger model copies its style much faster than its capability |
| [0019](lessons/0019-capacity-gap-and-hidden-traits.md) | Capacity Gap and Hidden Traits | Why a bigger teacher is not always a better one, and what can pass to a student that nobody intended |
| [0020](lessons/0020-choosing-student-size.md) | Choosing Student Size | What distillation scaling laws say about when distilling beats training the student directly |
| [0021](lessons/0021-data-volume-and-teacher-cost.md) | Data Volume and Teacher Cost | Counting the teacher's inference in the budget, and deciding how much distillation data is enough |
| [0022](lessons/0022-student-against-teacher.md) | Student Against Teacher | Measuring agreement with the teacher separately from task quality, one capability at a time |
| [0023](lessons/0023-an-honest-distillation-eval.md) | An Honest Distillation Eval | The baselines, held-out tasks and contamination checks that make a "matches the teacher" number defensible |
| [0024](lessons/0024-distill-quantize-or-fine-tune.md) | Distill, Quantize or Fine-Tune | Choosing between fewer parameters, fewer bits and training a small model directly, from the task and the budget |
| [0025](lessons/0025-reviewing-a-distillation-claim.md) | Reviewing a Distillation Claim | Review "our small model matches the large one" by naming what the measurement hid |
| [0026](lessons/0026-replacing-a-model-others-depend-on.md) | Replacing a Model Others Depend On | Rolling a student out in place of its teacher without breaking the people who depend on its behaviour |
| [0027](lessons/0027-when-the-usual-answer-is-wrong.md) | When the Usual Answer Is Wrong | Recognise when distillation is the wrong call, and settle a disputed claim from the primary source |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources, each annotated with what it covers
- [Distillation Losses](reference/distillation-losses.md): soft targets, temperature, the combined loss, token-level KL in both directions and the tokenizer constraint, from stages 1 and 2
- [Sequence and Synthetic Data](reference/sequence-and-synthetic-data.md): sequence-level distillation, generated data, rationales, filtering and the license questions, from stages 3 and 4
- [On-Policy Distillation](reference/on-policy-distillation.md): exposure bias, GKD and MiniLLM side by side, and when on-policy training pays, from stage 5
- [What the Student Inherits](reference/what-the-student-inherits.md): fidelity, the imitation gap, the capacity gap and unintended traits, from stage 6
- [Sizing and Measuring](reference/sizing-and-measuring.md): choosing student size and data volume with the teacher's cost, and an honest student-against-teacher eval, from stages 7 and 8
- [Distillation Review Checklist](reference/distillation-review-checklist.md): choosing between distilling, quantizing and fine-tuning, and the questions to ask of someone else's distillation claim, from stage 9

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
