---
title: 18. What a Checkpoint Has to Hold
description: A checkpoint that only saves weights cannot resume a run exactly, and choosing how often to save is its own tradeoff
type: lesson
---

# Lesson 18. What a Checkpoint Has to Hold

**Mission link:** "Can design a checkpointing scheme that bounds lost progress after a node failure" is the Success looks like bullet this stage serves. This lesson covers what a checkpoint needs to contain and how often to save one; Lesson 19 covers what actually happens when a node fails mid-run.
**Primary source:** [Paper: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
**Prerequisites:** [Lesson 17](0017-warmup-decay-and-growing-the-batch-mid-run.md)

## Warm-up

1. ▢ Per Rae et al., does a larger model get a higher or a lower maximum learning rate than a smaller one, all else equal?

<details markdown="1"><summary>Check</summary>

A lower maximum learning rate. Rae et al. state directly that as model size increases, they decrease the maximum learning rate the schedule uses.

</details>

2. ▢ What does global gradient-norm clipping do to a gradient whose norm exceeds the clipping threshold?

<details markdown="1"><summary>Check</summary>

It rescales the entire gradient vector proportionally so its norm equals the threshold, bounding how large a single update can be, rather than discarding the gradient or changing the learning rate.

</details>

## Know this

### A checkpoint is more than the weights

Saving only a model's parameters is not enough to resume training exactly where it left off. Resuming a training run correctly needs, at minimum: the model's **parameters**; the **optimizer state** (for Adam, the momentum and variance Lesson 8 counted, without which the optimizer effectively restarts cold); the **step count and learning-rate schedule position**, so warmup and decay (Lesson 17) continue from the right point rather than restarting; and, for exact reproducibility, the **data-loader position and random-number-generator state**, so the run does not silently reprocess or skip data around the restart point. A checkpoint missing any of these does not fail loudly; it resumes into a run that looks like it continued, while quietly training somewhat differently than an uninterrupted run would have.

### Why checkpoint frequency is its own tradeoff

However complete a checkpoint's contents, saving one costs time and storage: writing a large model's full state to durable storage takes real wall-clock time, during which the training run is typically paused or at least not making full progress, and each checkpoint occupies real disk space, especially if several recent ones are kept rather than only the latest. Checkpointing more frequently bounds how much progress a failure can destroy, since only the work since the last checkpoint is ever at risk. Checkpointing less frequently spends less overall time and storage on checkpoints themselves, at the cost of losing more progress on the same failure. Neither extreme is right in general: the correct frequency depends on how often failures are actually expected, weighed against how expensive each checkpoint actually is to write.

### How often failures actually happen, in a real run

Zhang et al.'s account of training OPT-175B makes the "how often are failures expected" side of that tradeoff concrete rather than hypothetical. Over roughly two months of training, hardware failures contributed to at least 35 manual restarts and the cycling of over 100 hosts, and the authors estimate more than 70 additional automatic restarts on top of that, on a single training run. That is well over one restart every two days on average, sustained for the run's entire duration. A checkpointing scheme built around the assumption that failures are rare, occasional events would have been badly wrong for this run; a scheme that assumes failures are a routine, expected part of the process, and checkpoints accordingly, is what a run at this scale actually needs.

## Practice

1. ▢ A team resumes a training run from a checkpoint that saved model parameters but not optimizer state. What goes wrong, even if the resumed run otherwise looks like it is continuing normally?

<details markdown="1"><summary>Check</summary>

The optimizer effectively restarts cold: for Adam, the momentum and variance accumulated before the checkpoint are lost, so the very first updates after resuming behave differently than they would have if training had never been interrupted, even though the parameters themselves are correct.

</details>

2. ▢ Why does checkpointing more frequently reduce the amount of progress a failure can destroy, and what does it cost to get that benefit?

<details markdown="1"><summary>Check</summary>

Only the work done since the most recent checkpoint is ever at risk if a failure happens, so a more recent checkpoint bounds the loss more tightly. The cost is the time spent writing each checkpoint (during which training is typically paused) and the storage each one occupies, both of which accumulate faster the more often checkpoints are saved.

</details>

3. ▢ Zhang et al. report at least 35 manual restarts, over 100 cycled hosts, and an estimated 70-plus automatic restarts across roughly two months of training OPT-175B. What does this figure argue for in a checkpointing scheme for a run of similar scale and duration?

<details markdown="1"><summary>Check</summary>

That failures should be treated as routine and frequent, not as rare exceptions, when choosing how often to checkpoint. At well over one restart every two days sustained across the whole run, a checkpointing scheme built for occasional failures would leave far too much progress exposed at any given moment.

</details>

## Real-world reps

- [ ] Find how a training framework you have access to defines what goes into a saved checkpoint (parameters, optimizer state, step count, RNG state), and check whether any of the four this lesson names are missing or optional in its default configuration.
- [ ] Read the "Hardware Failures" section of the OPT paper (linked above) and write one sentence describing the operational procedure the authors followed once a failure was detected, before Lesson 19 covers it directly.
- [ ] Tomorrow: for a hypothetical run of your own choosing (any duration and scale), estimate a checkpoint frequency you would pick, and write one sentence justifying it against both the cost of checkpointing too often and the risk of checkpointing too rarely.

## Going further

- [Paper: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
