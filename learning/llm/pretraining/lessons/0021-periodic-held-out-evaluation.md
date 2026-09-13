---
title: 21. Periodic Held-Out Evaluation
description: Training loss says the model is fitting its own training data; only a held-out check says anything about the rest
type: lesson
---

# Lesson 21. Periodic Held-Out Evaluation

**Mission link:** "Can read a training dashboard and say whether the run is on track" is the Success looks like bullet this stage serves. Lesson 20 covered watching the training run's own internal signals; this lesson covers checking saved checkpoints against something training loss cannot tell you, and hands that measurement off to where it is taught in full.
**Primary source:** [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Prerequisites:** [Lesson 20](0020-reading-a-loss-curve.md), [Held-out data](../../evals/GLOSSARY.md)

## Warm-up

1. ▢ Why might a loss scalar crashing toward zero, or an activation norm spiking, give earlier warning of instability than the training loss curve itself?

<details markdown="1"><summary>Check</summary>

These are symptoms of the underlying numerical problem developing, which can appear before it grows large enough to visibly disturb the loss curve; by the time a spike is clearly visible in the loss itself, the problem may already have been building for some time.

</details>

2. ▢ Why is a dashboard tracking loss, gradient norm, and a stability signal only useful in practice if it is monitored frequently?

<details markdown="1"><summary>Check</summary>

Because failures and instabilities are frequent, routine events at scale (Stage 8), so a problem caught late costs far more lost progress than the same problem caught early.

</details>

## Know this

### What training loss cannot tell you

Training loss measures how well a model fits the specific batches it is currently being trained on. A smoothly decreasing training loss is necessary for a healthy run, but it is not the same thing as the model being good at anything a person outside the training loop will actually ask it to do, and it says nothing at all about whether that improvement would hold up on text the model has never been trained on. A training loss curve that looks perfectly healthy can still sit on top of a model that is quietly overfitting to quirks specific to its own training mixture.

### What Gopher's own periodic evaluation looked like

Rae et al. did not wait until training finished to check this. They report evaluation curves calculated periodically during training, on four language-modeling benchmarks (Wikitext103, LAMBADA, Curation Corpus, and C4) that they explicitly filtered out of the training set beforehand, precisely so that a good score on them could not be explained by the model having simply seen that exact text during training. Checking a benchmark like this periodically, rather than only once at the very end, is what actually lets a team catch a problem, a bug in the data pipeline, a regression from a configuration change, an unexpected divergence in capability, while the run is still in progress and something can still be done about it, rather than discovering it only after the full compute budget has already been spent.

### Why "filtered from the training set" is doing real work

The phrase Rae et al. use, benchmarks "explicitly filtered from the training set," is the same idea Lesson 1 of this track's data pipeline material was built around, applied to evaluation instead of training: a score only means something about generalization if the model could not have gotten it right by having memorized the exact text being tested. This is precisely what **held-out data** means, and it is a large enough topic, with its own contamination pathways, detection methods, and design techniques, that it has an entire track built around it.

### Where this hands off

`llm/evals` owns evaluation methodology in full: how to build a held-out set that resists contamination, what makes a metric trustworthy, and how to turn a number into a defensible decision. This track's only claim on that material is the one made in this lesson: a pretraining run needs periodic checks against held-out data, on saved checkpoints, not only at the end. For everything past that, [`llm/evals`'s held-out data and contamination reference](../../evals/reference/held-out-data-and-contamination.md) is the sheet to read next, not a restatement of it here.

## Practice

1. ▢ A model's training loss has been decreasing smoothly for the entire run. Does this, by itself, tell you whether the model performs well on tasks it was not directly trained to fit?

<details markdown="1"><summary>Check</summary>

No. Training loss measures fit to the model's own training batches; a smoothly decreasing training loss is necessary for a healthy run but does not by itself say anything about performance on data or tasks the model has not been trained on, which is what a held-out evaluation is for.

</details>

2. ▢ Why did Rae et al. explicitly filter Wikitext103, LAMBADA, Curation Corpus, and C4 out of Gopher's training set before using them as periodic evaluation benchmarks?

<details markdown="1"><summary>Check</summary>

So that a good score on those benchmarks could not be explained by the model having simply seen and memorized that exact text during training. A benchmark the model was trained on cannot distinguish genuine capability from memorization, which is what makes a held-out benchmark meaningful evidence in a way a contaminated one is not.

</details>

3. ▢ What does evaluating periodically during training, rather than only once at the end, actually buy a team, given how expensive a full training run is?

    - a) It has no advantage over a single evaluation at the end; the final result is what matters
    - b) It lets a bug, regression, or divergence in capability be caught and potentially addressed while the run is still in progress, rather than discovered only after the full compute budget is already spent
    - c) It replaces the need for held-out data entirely
    - d) It only matters for very short training runs

<details markdown="1"><summary>Check</summary>

**b)** is the direct practical payoff: catching a problem early, while there is still compute budget left to respond to it, rather than finding out only after the run is complete. (a) ignores this entirely. (c) reverses the relationship; periodic evaluation still needs to be held out to mean anything. (d) is backwards, since a longer, more expensive run has more to lose from a late-caught problem.

</details>

## Real-world reps

- [ ] Find how a training framework or experiment-tracking setup you have access to schedules periodic evaluation during training (an evaluation interval measured in steps or tokens is common), and note what benchmarks or metrics it evaluates by default.
- [ ] Read `llm/evals`'s [held-out data and contamination reference sheet](../../evals/reference/held-out-data-and-contamination.md) and identify which of its two contamination pathways (pretraining absorption, or iterative overfitting) is the one Gopher's "explicitly filtered from the training set" language is guarding against.
- [ ] Tomorrow: for a hypothetical pretraining run of your own choosing, decide on an evaluation interval (how often, in tokens or steps, you would check held-out performance) and name one benchmark or held-out set you would check it against, and why.

## Going further

- [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [`llm/evals`: Held-out data and contamination reference](../../evals/reference/held-out-data-and-contamination.md)
- [Resources](../RESOURCES.md)

---

Stage 9 covered watching a run while it happens, both its own internals and its checkpoints against something external. Stage 10 closes the arc: deciding whether to run one of these at all, and defending that call to someone else.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
