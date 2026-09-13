---
title: 22. Pretraining Is Usually the Wrong Default
description: A second phase of pretraining on an existing model gets most of the benefit without paying the full cost again
type: lesson
---

# Lesson 22. Pretraining Is Usually the Wrong Default

**Mission link:** "Can decide whether a stated task calls for pretraining, continued pretraining, or fine-tuning an existing base model, and defend the choice on cost" is the Success looks like bullet stage 10 closes. This lesson makes the case against the default most newcomers reach for; Lesson 23 covers defending a budget once pretraining genuinely is the right call, and Lesson 24 covers reviewing someone else's.
**Primary source:** [Paper: "Don't Stop Pretraining: Adapt Language Models to Domains and Tasks", Gururangan et al., 2020](https://arxiv.org/abs/2004.10964)
**Prerequisites:** [Lesson 21](0021-periodic-held-out-evaluation.md)

## Warm-up

1. ▢ Why did Rae et al. explicitly filter certain benchmarks out of Gopher's training set before using them as periodic evaluation checks?

<details markdown="1"><summary>Check</summary>

So that a good score on those benchmarks could not be explained by the model having simply seen and memorized that exact text during training; a benchmark the model was trained on cannot distinguish genuine capability from memorization.

</details>

2. ▢ What does evaluating periodically during training, rather than only once at the end, actually buy a team?

<details markdown="1"><summary>Check</summary>

It lets a bug, regression, or divergence in capability be caught and potentially addressed while the run is still in progress, rather than discovered only after the full compute budget is already spent.

</details>

## Know this

### Why "we need our own pretrained model" is usually the wrong instinct

Every stage of this track has been building toward one honest fact: pretraining a model from scratch is extraordinarily expensive. Stage 3's compute-optimal arithmetic alone, a 70-billion-parameter model wanting on the order of a trillion tokens, gives a sense of the scale of compute a single from-scratch run demands, before counting the engineering cost of the distributed training infrastructure Stages 4 through 6 covered, or the operational cost of the monitoring and fault-tolerance Stages 8 and 9 covered. Wanting a model that is good at a specific domain, a specific task, or a specific style does not, by itself, justify paying all of that cost again. The question worth asking first is not "how do we pretrain a model for this," but "does this actually need a new pretrained model at all."

### The evidence for a cheaper alternative

Gururangan et al. answer this directly for one common case: adapting an existing broad-coverage pretrained model to a specific domain, rather than pretraining a new one for that domain. They take RoBERTa, an existing large pretrained model, and continue pretraining it on unlabeled text from a target domain, a **second phase of pretraining** they call **domain-adaptive pretraining (DAPT)**, before evaluating on tasks from that domain. Across four domains (biomedical papers, computer science papers, news, and reviews) and eight classification tasks, they find this consistently improves performance on the target domain's tasks, in both high-resource and low-resource settings, whenever the target domain was not already well represented in the model's original pretraining. They additionally find that adapting further to a specific task's own unlabeled data, **task-adaptive pretraining (TAPT)**, improves performance again on top of DAPT, and that even a cheaper alternative, adapting to a task corpus built with simple data-selection heuristics, works well when full domain-adaptive pretraining is not affordable.

### What this argues for, and what it does not

None of this claims pretraining from scratch is never justified; it claims the default assumption should run the other way. Continuing pretraining on an existing, already broadly capable model, at a small fraction of the compute a from-scratch run would need, consistently captures a real share of the benefit a fully domain-specific model might have offered. A task that seems to call for "a model good at our domain" is, per this evidence, very often better served by continued pretraining on an existing base model, or, if the task is narrower still, by the adapter fine-tuning `llm/finetuning` covers, than by paying for a new pretraining run. Reaching for full pretraining before ruling out these cheaper options is the specific mistake this lesson argues against, the pretraining-scale version of the same discipline `llm/finetuning`'s own judgment lesson applies one level down, when adapter fine-tuning itself is not the right call either.

### When pretraining from scratch is still the right call

The cases where it genuinely is include: a target language or domain so far outside any available base model's training data and tokenizer that no amount of continued pretraining or fine-tuning can close the gap; a licensing or provenance requirement that rules out every available base model's training data; or a deliberate architectural change (Stage 6's parallelism choices, a fundamentally different attention mechanism) that an existing checkpoint cannot be adapted into after the fact. These are the exception this lesson expects a reader to be able to name, not the rule.

## Practice

1. ▢ A team wants a model that performs well on legal documents, and an existing broad-coverage base model is available. Per Gururangan et al.'s evidence, what would this lesson recommend trying before pretraining a new model from scratch?

<details markdown="1"><summary>Check</summary>

Domain-adaptive pretraining: continuing to pretrain the existing base model on unlabeled legal text, which Gururangan et al. found consistently improves target-domain performance in both high- and low-resource settings, at a fraction of the cost of a new from-scratch pretraining run.

</details>

2. ▢ Which of these is a legitimate reason to pretrain from scratch anyway, per this lesson?

    - a) The target domain is mildly different from general web text
    - b) No available base model's tokenizer or training data covers the target language or domain at all, and continued pretraining cannot close that gap
    - c) A new pretraining run would look more impressive in a report
    - d) Fine-tuning would take more than a day to set up

<details markdown="1"><summary>Check</summary>

**b)** is the genuine exception this lesson names. (a) is exactly the case Gururangan et al.'s evidence argues continued pretraining handles well, not a reason to pretrain from scratch. (c) and (d) are not defensible reasons under this lesson's cost argument.

</details>

3. ▢ What is the difference between domain-adaptive pretraining (DAPT) and task-adaptive pretraining (TAPT), per Gururangan et al.?

<details markdown="1"><summary>Check</summary>

DAPT continues pretraining on unlabeled text from a broad target domain (such as all biomedical papers). TAPT continues pretraining specifically on a given task's own unlabeled data, a narrower corpus, and Gururangan et al. found it improves performance even after DAPT has already been applied.

</details>

4. ▢ A team cannot afford a full domain-adaptive pretraining run but still wants some of its benefit. What alternative does Gururangan et al.'s work suggest?

<details markdown="1"><summary>Check</summary>

Adapting to a task corpus built using simple data-selection strategies, which Gururangan et al. found to be an effective, cheaper alternative when resources for full domain-adaptive pretraining are unavailable.

</details>

## Real-world reps

- [ ] Find a published example of a domain-adapted model (a "BioBERT," "SciBERT," "FinBERT," or similar model card or paper) and identify whether it was built via continued pretraining on an existing base model or pretrained fully from scratch.
- [ ] Read Gururangan et al.'s introduction (linked above) and write one sentence on why they specifically chose to test domain-adaptive pretraining against multiple domains, rather than just one, before drawing a general conclusion.
- [ ] Tomorrow: for a hypothetical target domain or task you choose, write one paragraph arguing for or against pretraining a new model from scratch, citing at least one piece of evidence from this lesson or an earlier stage of this track.

## Going further

- [Paper: "Don't Stop Pretraining: Adapt Language Models to Domains and Tasks", Gururangan et al., 2020](https://arxiv.org/abs/2004.10964)
- [`llm/finetuning`](../../finetuning/): the same discipline applied one level down, once continued pretraining is still more than a narrower task needs
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
