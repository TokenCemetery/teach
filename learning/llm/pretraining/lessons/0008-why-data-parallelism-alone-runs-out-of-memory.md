---
title: 8. Why Data Parallelism Alone Runs Out of Memory
description: Counting exactly what a mixed-precision Adam optimizer holds per parameter, and where that hits a wall
type: lesson
---

# Lesson 8. Why Data Parallelism Alone Runs Out of Memory

**Mission link:** "Explain what ZeRO/FSDP shard, why data parallelism alone runs out of memory before it runs out of compute, and when tensor or pipeline parallelism is worth its communication cost" is the fourth bullet under Success looks like. Lesson 7 covered how data parallelism keeps every device's copy identical; this lesson counts exactly what "every device holds a full copy" costs, and where it breaks.
**Primary source:** [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**Prerequisites:** [Lesson 7](0007-data-parallelism-and-gradient-all-reduce.md)

## Warm-up

1. ▢ In data parallelism, what operation keeps every device's copy of the model identical after each optimizer step?

<details markdown="1"><summary>Check</summary>

The all-reduce: every device's local gradient is averaged across all devices before any device applies an update, so every device applies the same averaged gradient to an identical starting copy of the weights.

</details>

2. ▢ Does adding more data-parallel devices reduce how much memory any single device needs to hold the model? Why or why not?

<details markdown="1"><summary>Check</summary>

No. Every device still holds a full copy of the parameters, gradients, and optimizer state, exactly as if it were training alone; more devices means more copies of that same footprint, not a smaller footprint per device.

</details>

## Know this

### What "a full copy of the model" actually contains

Lesson 7 said every data-parallel device holds a full copy of the parameters, gradients, and optimizer state, without counting what that costs. Mixed-precision training, the standard approach for training large models, makes the count concrete. Using Adam as the optimizer, Rajbhandari et al. count, per parameter (`Ψ` denotes the parameter count):

- an `fp16` copy of the parameters, used for the forward and backward pass: 2 bytes per parameter
- an `fp16` copy of the gradients: 2 bytes per parameter
- an `fp32` copy of the parameters, kept by the optimizer for numerically stable updates: 4 bytes per parameter
- an `fp32` copy of Adam's momentum: 4 bytes per parameter
- an `fp32` copy of Adam's variance: 4 bytes per parameter

That totals 16 bytes per parameter, every one of which every data-parallel device holds a full copy of, regardless of how many other devices are also holding an identical copy.

### Where that hits a wall

For a 1.5-billion-parameter model (GPT-2's size), 16 bytes per parameter comes to 24 GB just for these model states, well above the 3 GB it would take to hold only the `fp16` parameters by themselves, and that is before counting activations (the intermediate values kept from the forward pass to compute gradients in the backward pass), which Rajbhandari et al. separately estimate at around 60 GB for that same model at a sequence length of 1,024 and a batch size of 32. Rajbhandari et al. state the resulting limit directly: "basic data parallelism does not reduce memory per device, and runs out of memory for models with more than 1.4B parameters on current generation of GPUs with 32 GB memory." A GPU with 32 GB has run out of room before it has run out of anything else, on a model barely larger than GPT-2, using every one of the many devices data parallelism can add.

### The shape of the fix

Every device in ordinary data parallelism holds an identical, fully redundant copy of the same 16Ψ bytes of model states. That redundancy is exactly what a different strategy can remove: instead of every device holding everything, each device could hold only its own slice of the model states, reconstructing or communicating whatever it does not hold, only when it is actually needed for a computation. That is the idea Stage 5 picks up directly, under the name ZeRO.

## Practice

1. ▢ Using the 16-bytes-per-parameter breakdown, about how much memory would the model states alone require for a 7-billion-parameter model trained in mixed precision with Adam?

<details markdown="1"><summary>Hint</summary>

Multiply the parameter count by 16 bytes, then convert bytes to gigabytes.

</details>

<details markdown="1"><summary>Check</summary>

About 112 GB (`7 × 10^9 × 16` bytes ≈ `1.12 × 10^11` bytes ≈ 112 GB). That is model states alone, well beyond a single 32 GB or even 80 GB GPU, before activations are counted at all.

</details>

2. ▢ Which of these best explains why data parallelism alone cannot fit an arbitrarily large model, no matter how many devices are added?

    - a) Communication bandwidth between devices eventually saturates
    - b) Every device holds a full, redundant copy of the same per-parameter memory cost, so adding devices adds more copies rather than shrinking any single device's requirement
    - c) The all-reduce operation itself consumes an amount of memory proportional to model size
    - d) Larger models always produce larger gradients, which overflow fp16 representation

<details markdown="1"><summary>Check</summary>

**b)** is the actual limit this lesson traces, directly from the redundant per-device memory footprint. (a) is a real concern in distributed training but is a communication-time cost, not the memory-capacity wall this lesson is about. (c) and (d) are not the mechanism ZeRO's authors identify.

</details>

3. ▢ Rajbhandari et al. state that basic data parallelism runs out of memory for models with more than 1.4B parameters on GPUs with 32 GB of memory. Per the 16-bytes-per-parameter breakdown, roughly how much memory would a 1.4B-parameter model's states alone require, and how does that compare to the 32 GB figure once activations are added?

<details markdown="1"><summary>Check</summary>

About 22.4 GB for model states alone (`1.4 × 10^9 × 16` bytes ≈ `2.24 × 10^10` bytes). That already leaves under 10 GB of a 32 GB GPU for activations, which the lesson's GPT-2 example put at roughly 60 GB at a modest sequence length and batch size, well past what remains.

</details>

## Real-world reps

- [ ] Pick a published open model's parameter count and, using the 16-bytes-per-parameter formula, estimate its model-state memory requirement under mixed-precision Adam. Compare that estimate to the GPU memory sizes commonly used for training (24, 40, 80 GB are typical figures to compare against).
- [ ] Read the paragraph in the ZeRO paper (linked above) describing residual memory (activations, temporary buffers, memory fragmentation) and write one sentence distinguishing it from the model-states memory this lesson counted.
- [ ] Tomorrow: without looking ahead, write down a one-sentence prediction for Stage 5: if the problem is that every device holds a full, redundant copy of the same 16Ψ bytes, what would a fix that removes the redundancy have to do instead, and what would it have to communicate to make up for no longer holding everything locally?

## Going further

- [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Resources](../RESOURCES.md)

---

Stage 4 established that data parallelism's redundancy, not its compute, is what runs out first. Stage 5 picks that up directly: what ZeRO and FSDP actually shard to remove it.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
