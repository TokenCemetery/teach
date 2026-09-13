---
title: 5. Scaling Laws: What Kaplan Predicted
description: An empirical power law lets you forecast a training run's loss before paying for it, and what that predicted for how to spend a compute budget
type: lesson
---

# Lesson 5. Scaling Laws: What Kaplan Predicted

**Mission link:** "Given a parameter count and a compute budget, compute the compute-optimal token count and defend it against a Kaplan-style undertrained alternative" is the third bullet under Success looks like. This lesson covers what Kaplan et al. found and recommended; Lesson 6 covers the correction that changed the recommendation.
**Primary source:** [Paper: "Scaling Laws for Neural Language Models", Kaplan et al., 2020](https://arxiv.org/abs/2001.08361)
**Prerequisites:** [Lesson 4](0004-sentencepiece-and-the-vocabulary-size-tradeoff.md)

## Warm-up

1. ▢ Name one axis on which a larger tokenizer vocabulary is worse than a smaller one.

<details markdown="1"><summary>Check</summary>

A larger vocabulary means a larger embedding and output-projection table (pure parameter count), and it spreads training signal more thinly across more distinct tokens, so any one specific token is seen less often per pass over the same corpus.

</details>

## Know this

### What a scaling law actually is

A **scaling law**, in this context, is an empirical power-law relationship: a model's held-out loss falls off smoothly as a function of model size, dataset size, or training compute, over a range wide enough to be useful for forecasting. Kaplan et al. fit exactly this, finding that loss scales as a power law with each of these three quantities individually, holding across trends spanning more than seven orders of magnitude in scale. Other architectural choices, such as how a fixed parameter budget is split between width and depth, turned out to matter comparatively little within a wide range once model size itself was accounted for.

The practical value of a scaling law is prediction: if loss follows a smooth, fitted curve against model size, dataset size, and compute, a team can forecast roughly how well a training run of a given size and budget will perform before spending the compute to run it, rather than finding out only after the fact.

### Bigger models learn more per token

One of Kaplan et al.'s central findings is that larger models are significantly more sample-efficient: to reach a given loss, a larger model needs to see less data than a smaller model would need to reach that same loss. Combined with their fitted relationships between loss, compute, and the two things compute buys (a bigger model, or more data to train it on), this implies a specific answer to how to spend a fixed compute budget: optimally compute-efficient training means training a very large model on a comparatively modest amount of data, and stopping well short of converging on that data, rather than training a smaller model to convergence on more of it.

### What that recommendation looked like in practice

This finding shaped how a generation of large models were actually trained: scale the parameter count aggressively, and hold the token count comparatively fixed or only modestly increased. GPT-3, for instance, trained a 175-billion-parameter model on 300 billion tokens. This lesson leaves that number sitting here without further comment; Lesson 6 returns to it directly once there is a second scaling law to compare it against.

## Practice

1. ▢ What does it mean, precisely, for loss to "scale as a power law" with model size, in the sense Kaplan et al. use it?

    - a) Loss decreases by exactly the same fixed amount for every fixed increase in model size
    - b) Loss falls off smoothly following a fitted curve, holding across a wide range of model sizes, which is what makes it possible to forecast
    - c) Loss becomes zero once the model is large enough
    - d) Loss depends only on model size and not at all on the amount of training data

<details markdown="1"><summary>Check</summary>

**b)** A power-law fit smooth enough, and validated across enough orders of magnitude, to forecast from. (a) describes a linear relationship, not a power law. (c) is not claimed anywhere in the paper. (d) contradicts the paper's own separate finding of a scaling law with dataset size.

</details>

2. ▢ Per Kaplan et al., which reaches a fixed target loss using less training data: a larger model or a smaller one?

<details markdown="1"><summary>Check</summary>

A larger model. Larger models are more sample-efficient, meaning they need less data to reach the same loss a smaller model would need more data to reach.

</details>

3. ▢ Given a fixed compute budget and Kaplan et al.'s findings, which allocation does their analysis recommend: a very large model trained on comparatively little data and stopped well short of convergence, or a smaller model trained to convergence on as much data as the budget allows?

<details markdown="1"><summary>Hint</summary>

This follows directly from combining "larger models are more sample-efficient" with a fixed compute budget: compute spent on data is compute not spent on model size, and the paper found one of those two uses of compute paid off more than the other.

</details>

<details markdown="1"><summary>Check</summary>

The very large model trained on comparatively little data, stopped before convergence. That is Kaplan et al.'s own stated recommendation for optimally compute-efficient training under a fixed budget.

</details>

## Real-world reps

- [ ] Find the parameter count and reported training-token count for two or three well-known models released within a year or two of the Kaplan paper (2020 to roughly 2022). Note whether their token counts stayed roughly fixed while parameter counts grew, which is what following this lesson's recommendation would look like.
- [ ] Read the Kaplan paper's abstract (linked above) once more and, in one sentence, state what "stopping significantly before convergence" means for a training run: what would keep training further actually buy, that this recommendation says is not worth its compute?
- [ ] Tomorrow: without looking ahead to Lesson 6, write down a one-sentence prediction: given that dataset construction (Stage 1 of this track) is expensive and slow to scale, and pure parameter count is comparatively easy to scale by adding more accelerators, what practical pressure might have pushed real training runs toward Kaplan's recommendation even harder than the loss curves alone would justify?

## Going further

- [Paper: "Scaling Laws for Neural Language Models", Kaplan et al., 2020](https://arxiv.org/abs/2001.08361)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
