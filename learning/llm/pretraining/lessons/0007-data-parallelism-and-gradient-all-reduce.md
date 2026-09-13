---
title: 7. Data Parallelism and Gradient All-Reduce
description: Splitting a batch across devices that each hold a full copy of the model, and what keeps every copy identical
type: lesson
---

# Lesson 7. Data Parallelism and Gradient All-Reduce

**Mission link:** "Explain what ZeRO/FSDP shard, why data parallelism alone runs out of memory before it runs out of compute, and when tensor or pipeline parallelism is worth its communication cost" is the fourth bullet under Success looks like. This lesson covers what data parallelism is and how it stays correct; Lesson 8 covers why it runs out of memory.
**Primary source:** [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**Prerequisites:** [Lesson 6](0006-chinchilla-the-compute-optimal-correction.md)

## Warm-up

1. ▢ Using `FLOPs(N, D) ≈ 6ND`, about how many tokens can a compute budget of `6 × 10^21` FLOPs afford for a 5-billion-parameter model?

<details markdown="1"><summary>Check</summary>

200 billion tokens: `6 × 10^21 / (6 × 5 × 10^9) = 2 × 10^11`.

</details>

## Know this

### Splitting the batch, not the model

**Data parallelism** is the simplest way to put more than one device to work on the same training run: every device holds a full, identical copy of the model, and a single large batch is split into smaller per-device chunks, one per device. Each device runs its own forward and backward pass on its own chunk, entirely independently of the others, computing its own local gradient.

### Keeping every copy identical

If each device simply applied its own local gradient to its own copy of the weights, the copies would drift apart after one step, and "N devices training one model" would quietly become "N devices training N different models." Data parallelism avoids this with a synchronization step before the optimizer runs: every device's local gradient is averaged together across all devices, via a collective communication operation called an **all-reduce**, and every device receives back the same averaged gradient. Because every device then applies the identical averaged gradient to an identical starting copy of the weights, all copies stay identical after the optimizer step, step after step, without ever having to compare the weights themselves.

A common way to implement this efficiently is a **ring all-reduce**: devices are arranged in a logical ring, and each one only ever exchanges data with its two neighbors, in a sequence of steps that guarantees every device ends up with the full sum (and then the average) without ever needing one device to collect everything from everyone else directly. This keeps the communication volume per device roughly constant as more devices are added, rather than growing with the device count, which is what makes data parallelism scale reasonably well in the first place.

### What this buys, and what it does not touch

Data parallelism's whole benefit is throughput: with `k` devices, `k` times as much data can be processed per unit of wall-clock time, since each device is doing independent work on its own slice of the batch. Nothing about this changes how much memory any single device needs. Every device still holds a full copy of the model's parameters, its gradients, and its optimizer state, exactly as if it were training alone; adding more data-parallel devices adds more copies of the same memory footprint, not less of it per device. Data parallelism is a way to process more of a fixed-size model's training faster; on its own, it is not a way to fit a larger model than a single device could otherwise hold. Lesson 8 makes that limit concrete.

## Practice

1. ▢ Four devices train one model with data parallelism. Device 3 computes a local gradient that happens to be unusually large compared to the other three devices' gradients that step, due to whatever happened to be in its slice of the batch. What keeps this from making device 3's copy of the weights drift away from the other three?

<details markdown="1"><summary>Check</summary>

The all-reduce step. Every device's local gradient, including device 3's unusually large one, gets averaged together across all four devices before any device applies an update, so every device applies the same averaged gradient to an identical starting copy of the weights, keeping all four copies identical.

</details>

2. ▢ Which of these best describes what adding more data-parallel devices changes about a training run?

    - a) It reduces the amount of memory each device needs to hold the model
    - b) It lets more of the batch be processed per unit of time, without changing how much memory any single device needs
    - c) It removes the need for an optimizer step entirely
    - d) It automatically increases the model's parameter count

<details markdown="1"><summary>Hint</summary>

Ask what actually gets split across devices in data parallelism: the model, or the batch?

</details>

<details markdown="1"><summary>Check</summary>

**b)** Data parallelism splits the batch, not the model, so throughput scales with device count while per-device memory does not shrink. (a) is exactly backwards, which Lesson 8 makes concrete. (c) and (d) describe changes data parallelism does not make at all.

</details>

3. ▢ In a ring all-reduce, why does each device only ever communicate with its two neighbors in the ring, rather than every device sending its gradient to every other device directly?

<details markdown="1"><summary>Check</summary>

So the communication volume any single device has to handle stays roughly constant as more devices join the ring, rather than growing with the number of devices, which is what lets this approach scale to many devices without communication itself becoming the bottleneck.

</details>

## Real-world reps

- [ ] Find the documentation for a data-parallel training API you have access to (PyTorch's `DistributedDataParallel` is a common one) and locate where it describes the gradient-synchronization step. Note what it calls the operation, and whether the description matches "all-reduce" as this lesson describes it.
- [ ] Sketch, on paper, four devices arranged in a ring, and trace through by hand what a single device sends and receives in a ring all-reduce over a few steps, using a toy 4-number gradient vector split one number per device.
- [ ] Tomorrow: without looking ahead, write down a one-sentence prediction for Lesson 8: if every data-parallel device must hold a full copy of the model's parameters, gradients, and optimizer state, what happens as the model gets larger while the number of devices stays fixed?

## Going further

- [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
