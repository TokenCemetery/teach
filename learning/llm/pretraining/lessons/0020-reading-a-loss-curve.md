---
title: 20. Reading a Loss Curve
description: The training loss curve alone under-reports trouble; two other signals catch what it misses, and catch it earlier
type: lesson
---

# Lesson 20. Reading a Loss Curve

**Mission link:** "Can read a training dashboard and say whether the run is on track" is the Success looks like bullet this stage serves. This lesson covers what to actually watch on a live dashboard; Lesson 21 covers evaluating saved checkpoints against held-out data.
**Primary source:** [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Prerequisites:** [Lesson 19](0019-surviving-a-node-failure.md)

## Warm-up

1. ▢ What did Zhang et al. notice was correlated with loss divergence during OPT-175B's training, besides the loss curve itself?

<details markdown="1"><summary>Check</summary>

Their dynamic loss scalar (part of the mixed-precision setup) crashing to zero, and the norm of the final layer's activations spiking.

</details>

2. ▢ Why does recovering from a loss divergence argue for keeping more than just the single most recent checkpoint?

<details markdown="1"><summary>Check</summary>

Because the best restart point was chosen based on the loss scalar's health and the activation norm's trend, which was not always the most recent checkpoint; keeping only the newest one would remove the option to roll back further.

</details>

## Know this

### The training loss curve, and what "healthy" means for it

The most basic thing a training dashboard shows is the training loss itself, plotted against training step or token count. Stage 3's scaling laws give a real expectation for its shape: loss should fall off smoothly, roughly following a power-law-like curve as compute and tokens accumulate, not in a straight line and not in a series of unrelated jumps. A curve that tracks this general shape is behaving as expected; a curve that flattens out far earlier than the scaling-law trajectory would predict, or one that shows a sudden sharp rise (a loss spike, Lesson 16), is a training loss curve reporting something worth investigating, before assuming the run is simply on track.

### Two signals that catch trouble before the loss curve clearly shows it

Watching training loss alone is not enough, because by the time a spike is visible in the loss itself, the underlying problem may already have been building for a while. Zhang et al.'s account of OPT-175B gives two other signals that gave earlier warning of the same trouble the loss curve eventually showed: their **dynamic loss scalar**, part of the mixed-precision setup, crashing toward zero, and the **norm of the final layer's activations** spiking upward. Both are symptoms of a training run heading toward instability, visible before, or alongside, the loss itself clearly diverging, which is exactly why Zhang et al. used them, not just the loss curve, to judge whether a given point in training was a safe one to restart from.

### The gradient norm, watched over time

Lesson 16 covered gradient-norm clipping as a per-step safeguard, bounding how large any single update can be. The same gradient norm, watched as a curve over the course of training rather than only checked against the clipping threshold at each step, is itself a useful signal: a gradient norm that is trending upward over time, or spiking repeatedly even after clipping, can be an early sign of the same kind of instability a loss spike would eventually show more dramatically, giving a chance to intervene, such as by lowering the learning rate, before a full divergence forces a restart.

### Watching, continuously

None of these signals help if nobody, or nothing automated, is actually looking at them. Stage 8 established that failures and instabilities are a routine, frequent part of a large training run, not a rare event; a dashboard showing loss, gradient norm, and a numeric-stability signal like a loss scalar is only useful if it is checked often enough, or alerts automatically enough, to catch a developing problem before it costs far more progress than an earlier catch would have.

## Practice

1. ▢ A team's training loss curve is decreasing, but noticeably more slowly than Stage 3's scaling-law relationships would predict for their model size and token count so far. Is this necessarily a sign of a problem, or could it be consistent with a healthy run?

<details markdown="1"><summary>Hint</summary>

Scaling laws are empirical fits with real variance, not an exact guarantee for every individual run.

</details>

<details markdown="1"><summary>Check</summary>

It is worth investigating rather than assumed to be fine, but not automatically proof of a problem; scaling laws are fitted trends with variance, not an exact per-run guarantee. A meaningful, sustained gap from the expected trajectory is a legitimate reason to check other signals (gradient norm, a loss scalar if using mixed precision, or the data pipeline itself) rather than assuming the curve alone settles the question either way.

</details>

2. ▢ Why might a loss scalar crashing toward zero, or an activation norm spiking, give earlier warning of instability than the training loss curve itself?

<details markdown="1"><summary>Check</summary>

These are symptoms of the underlying numerical problem developing, which can appear before it grows large enough to visibly disturb the loss curve. By the time a spike is clearly visible in the loss itself, the problem may already have been building for some time.

</details>

3. ▢ Which of these best describes why a dashboard tracking loss, gradient norm, and a stability signal like a loss scalar is only useful in practice if it is monitored frequently?

    - a) These metrics are only meaningful once per training run, at the very end
    - b) Failures and instabilities are frequent, routine events at scale (Stage 8), so a problem caught late costs far more lost progress than the same problem caught early
    - c) The metrics themselves change their meaning if checked too often
    - d) Frequent monitoring is only useful for very small models

<details markdown="1"><summary>Check</summary>

**b)** is the actual reasoning: given how often failures and instabilities occur at scale, the value of a dashboard is directly tied to how quickly a developing problem gets noticed. (a), (c), and (d) do not reflect anything this lesson or Stage 8 established.

</details>

## Real-world reps

- [ ] Find a training framework's or experiment-tracking tool's dashboard (Weights & Biases, TensorBoard, or similar) and identify which of this lesson's signals (loss, gradient norm, a numeric-stability indicator) it surfaces by default, and which would need to be added explicitly.
- [ ] Read the paragraph in the OPT paper (linked above) connecting loss divergence to the loss scalar and activation norm, and write one sentence on which signal you would check first if you saw a loss spike on a dashboard with all three available.
- [ ] Tomorrow: without looking ahead, write a one-sentence prediction for Lesson 21: if training loss alone does not tell you how well a model performs on the tasks people will actually use it for, what would need to be measured differently to check that during training, rather than only after it finishes?

## Going further

- [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [Paper: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
