---
title: 17. Measuring the Alignment Tax
description: The tax does not show up everywhere at once, and one axis even measured an improvement instead
type: lesson
---

# Lesson 17. Measuring the Alignment Tax

**Mission link:** "Can separate a genuine capability gain from a reward-hacking or judge-bias artifact" is the Success looks like bullet this stage serves. This lesson covers how the alignment tax is actually measured, not just what it is; Lesson 18 covers detecting reward hacking after training is finished, and hands off to `llm/evals` for the full methodology.
**Primary source:** [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Prerequisites:** [Lesson 16](0016-rlaif-how-well-ai-feedback-actually-matches-human-feedback.md), [Alignment tax](../GLOSSARY.md)

## Warm-up

1. ▢ What is direct-RLAIF (d-RLAIF), and how did its performance compare to canonical RLAIF, per Lee et al.?

<details markdown="1"><summary>Check</summary>

A technique that skips training a separate reward model, querying an off-the-shelf language model for a reward score directly during RL. Lee et al. found it achieved better performance than canonical RLAIF, not merely comparable performance at lower cost.

</details>

2. ▢ For which of the three tasks Lee et al. tested did RLAIF outperform RLHF, rather than merely match it?

<details markdown="1"><summary>Check</summary>

Harmless dialogue generation.

</details>

## Know this

### The tax is not one number; it is a set of separate measurements

Lesson 1 introduced the alignment tax as a real, measured cost, without detailing how it is actually measured. Ouyang et al. did it by running their aligned model against a battery of existing public NLP benchmarks and comparing the result to the unaligned base model, on each benchmark separately, rather than collapsing everything into a single tax figure. They report specific regressions on certain benchmarks, notably SQuAD, DROP, HellaSwag, and WMT 2015 French-to-English translation, and, importantly, **no significant change** on two others they also checked, Winogender and CrowSPairs (bias-related benchmarks). The tax showed up on some axes and not others; treating it as one uniform cost would have hidden that pattern.

### Alignment also produced a measured gain, not only a cost

The same evaluation battery included an axis where alignment training measured as an improvement rather than a cost: using the RealToxicityPrompts dataset, Ouyang et al. report InstructGPT generating about 25% fewer toxic outputs than GPT-3 when prompted to be respectful. A fair accounting of what alignment training did to a model's measured capabilities has to include this kind of result alongside the regressions; reporting only the tax and ignoring where the same training helped would be just as misleading as reporting no tax at all.

### The fix, and what it did not cost

Lesson 6 already named the mechanism: mixing PPO updates with updates that increase the likelihood of the original pretraining distribution (PPO-ptx) greatly reduced the measured regressions on SQuAD, DROP, HellaSwag, and WMT. Ouyang et al. are specific that this recovery came **without compromising labeler preference scores**, meaning the fix did not simply trade the alignment gains back for the lost benchmark performance; both were measured, separately, and the fix improved one without visibly costing the other.

### A different, harder-to-fake generalization check: held-out labelers

Beyond benchmark regressions, Ouyang et al. run a check aimed at a different question: does the model's aligned behavior generalize beyond the specific people whose preferences shaped it, or did it just learn to please the particular labelers in its training data? They test this with **held-out labelers**, people who contributed no data used to train the model at all, and find that these held-out labelers still preferred InstructGPT's outputs. This is the same underlying idea `llm/pretraining` and `llm/evals` both use held-out data for: a result only means what it claims to mean if it could not have been produced by simply fitting to the specific data (or people) that shaped training.

## Practice

1. ▢ Ouyang et al. report regressions on SQuAD, DROP, HellaSwag, and WMT translation, but no significant change on Winogender and CrowSPairs. What would treating the alignment tax as a single overall number have hidden about this result?

<details markdown="1"><summary>Check</summary>

That the tax did not apply uniformly; it showed up clearly on some benchmarks and not at all on others. A single collapsed number would present this uneven pattern as if it were one consistent cost across every capability.

</details>

2. ▢ Why does the 25% reduction in toxic outputs matter for a fair account of the alignment tax, rather than only reporting the SQuAD/DROP/HellaSwag/WMT regressions?

<details markdown="1"><summary>Check</summary>

Because alignment training measurably helped on this axis rather than costing anything; reporting only the regressions and omitting this result would understate what the training actually did, in the same way reporting no tax at all would overstate it.

</details>

3. ▢ What specifically did Ouyang et al. verify about PPO-ptx's fix for the alignment tax, beyond simply reducing the benchmark regressions?

<details markdown="1"><summary>Check</summary>

That it did so without compromising labeler preference scores; the recovery in benchmark performance was not paid for by giving back the alignment gains that PPO-ptx was added on top of.

</details>

4. ▢ Why does testing with held-out labelers, people who contributed no training data, answer a different question than the benchmark-regression measurements do?

<details markdown="1"><summary>Check</summary>

Benchmark regressions measure whether specific capabilities got worse. Held-out labelers test whether the model's aligned behavior actually generalizes to preferences beyond the specific people who shaped training, rather than merely fitting closely to that particular group; a result that held only for the original labelers would not support the same generalization claim.

</details>

## Real-world reps

- [ ] Find a published post-training technical report and check whether it reports both regressions and improvements across a benchmark battery, or only one direction. Note which benchmarks, if any, showed no significant change.
- [ ] Read the paragraph in the InstructGPT paper (linked above) describing the held-out-labeler experiment, and write one sentence stating what result would have made you doubt the model's alignment generalized beyond its training labelers.
- [ ] Tomorrow: without looking ahead, write a one-sentence prediction for Lesson 18: given that a reward model or an AI judge can be gamed (Lesson 5), what would evaluating a *finished* aligned model, after training is over, need to check for that a training-time train-PM-versus-test-PM comparison could not?

## Going further

- [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
