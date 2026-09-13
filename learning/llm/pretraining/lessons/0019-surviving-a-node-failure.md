---
title: 19. Surviving a Node Failure
description: Pause, diagnose, cordon off what is broken, and resume from the last checkpoint, at whatever it costs
type: lesson
---

# Lesson 19. Surviving a Node Failure

**Mission link:** "Can design a checkpointing scheme that bounds lost progress after a node failure" is the Success looks like bullet this stage serves. Lesson 18 covered what a checkpoint has to hold and how often to save one; this lesson covers what actually happens once a failure hits.
**Primary source:** [Paper: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
**Prerequisites:** [Lesson 18](0018-what-a-checkpoint-has-to-hold.md)

## Warm-up

1. ▢ Name the four things a checkpoint needs to hold to resume a run correctly, not just approximately.

<details markdown="1"><summary>Check</summary>

Model parameters, optimizer state, the step count and learning-rate schedule position, and, for exact reproducibility, the data-loader position and random-number-generator state.

</details>

2. ▢ Over roughly two months of training OPT-175B, what did Zhang et al. report about how often hardware failures occurred?

<details markdown="1"><summary>Check</summary>

At least 35 manual restarts and the cycling of over 100 hosts, plus an estimated 70-plus additional automatic restarts, well over one restart every two days sustained across the run.

</details>

## Know this

### The procedure OPT actually followed

Zhang et al. describe a specific, repeatable sequence rather than an ad hoc scramble each time a failure hit: when a hardware problem was suspected, the training run was **paused**; a series of **diagnostic tests** was run to identify which specific nodes were behaving badly; any node the diagnostics flagged was **cordoned off**, meaning it was excluded from the pool of nodes the run would use going forward; and training then **resumed from the last saved checkpoint**, now running on the remaining, healthy nodes. This is the same pattern regardless of whether a failure was caught manually or triggered an automatic restart: diagnose, exclude the bad hardware, resume from the most recent saved state.

### Manual against automatic restarts, and why the difference matters operationally

Zhang et al. distinguish 35-plus **manual** restarts, where a person recognized a problem and intervened, from an estimated 70-plus **automatic** restarts, inferred from the gap between the number of hosts cycled out and the smaller number of manual restarts recorded. An automatic restart implies tooling that detects a failure and resumes training without waiting for a person to notice and act, which matters directly for how much progress a failure actually costs: a failure that waits for manual detection loses whatever time passes before a person intervenes, on top of whatever a checkpoint-and-resume cycle itself costs, while an automatically detected and resumed failure loses closer to just the checkpoint-interval's worth of progress Lesson 18 discussed.

### Loss divergence as a related but distinct failure to recover from

Zhang et al. also describe restarting for a different reason entirely: loss divergence, not hardware failure. When training loss diverged, lowering the learning rate and restarting from an earlier checkpoint let the run recover and continue. They noticed this correlated with two other signals: their dynamic loss scalar (part of the mixed-precision setup) crashing to zero, and the norm of the final layer's activations spiking. Rather than restarting from immediately before the divergence, they picked restart points where the loss scalar was still in a healthy state and activation norms were trending downward rather than growing unboundedly, and separately found that lowering gradient clipping from 1.0 to 0.3 helped. This is a second, genuinely different reason a checkpoint gets used to resume a run, distinct from a node dying: the hardware is fine, but the training process itself needs to roll back and continue differently, which only a kept history of checkpoints (not just the single most recent one) makes possible.

## Practice

1. ▢ Put these four steps of OPT's node-failure procedure in the order Zhang et al. describe: (a) resume training on the remaining nodes, (b) pause the training run, (c) run diagnostic tests to identify bad nodes, (d) cordon off flagged nodes.

<details markdown="1"><summary>Check</summary>

b, c, d, a: pause, diagnose, cordon off whatever the diagnostics flagged, then resume from the last saved checkpoint on the remaining healthy nodes.

</details>

2. ▢ Why does an automatically detected and resumed failure typically cost less progress than a manually detected one, even if both eventually resume from the same checkpoint?

<details markdown="1"><summary>Check</summary>

A manual restart loses whatever time passes before a person notices the problem and intervenes, on top of the checkpoint-and-resume cycle itself. An automatic restart skips that detection delay, so the total cost is closer to just the checkpoint interval's worth of progress.

</details>

3. ▢ A team's training loss diverges, but there is no hardware failure: every node is healthy. Per Zhang et al.'s account, is a checkpoint still useful here, and if so, how?

    - a) No; checkpoints only help with hardware failures, not loss divergence
    - b) Yes; restarting from an earlier checkpoint, along with lowering the learning rate, is exactly how Zhang et al. recovered from loss divergence
    - c) Yes, but only the single most recent checkpoint can ever be used, regardless of when the divergence began
    - d) No; loss divergence requires retraining the model from scratch

<details markdown="1"><summary>Hint</summary>

Zhang et al. specifically chose restart points based on the state of their loss scalar and activation norms, not simply the most recent checkpoint available.

</details>

<details markdown="1"><summary>Check</summary>

**b)** is exactly what Zhang et al. describe. (a) is false; the same checkpoint-and-resume mechanism recovers from either cause. (c) is wrong specifically because they picked a restart point based on when the loss scalar was healthy and activation norms were trending down, which may not be the single most recent checkpoint, arguing for keeping more than one recent checkpoint on hand. (d) contradicts the paper's own account of recovering without a full restart.

</details>

4. ▢ Why does recovering from a loss divergence, as Zhang et al. describe it, argue for keeping more than just the single most recent checkpoint?

<details markdown="1"><summary>Check</summary>

Because the best restart point was not always the most recent checkpoint; it was one chosen based on the loss scalar's health and the direction activation norms were trending, which could be further back than the latest save. Keeping only the newest checkpoint would remove the option to roll back to an earlier, more stable point.

</details>

## Real-world reps

- [ ] Find where a training framework or orchestration tool you have access to exposes automatic failure detection and restart (health checks, node draining, or similar terms are common). Note whether it matches the pause-diagnose-cordon-resume pattern this lesson describes.
- [ ] Read the "Loss Divergences" paragraph of the OPT paper (linked above) and write one sentence on what signal, besides the loss curve itself, the authors used to judge whether a restart point was safe to resume from.
- [ ] Tomorrow: for the checkpoint frequency you picked in Lesson 18's real-world rep, decide how many recent checkpoints you would keep on hand rather than just the latest, and write one sentence for why, given this lesson's loss-divergence recovery case.

## Going further

- [Paper: "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
- [Resources](../RESOURCES.md)

---

Stage 8 covered surviving a failure inside a single training run. Stage 9 turns to a longer-running question: watching that run's progress in the first place, and knowing whether it is on track at all.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
