---
title: 9. ZeRO Stage 1 and 2: Partitioning Optimizer State and Gradients
description: Removing data parallelism's redundant copies for free, before communication cost has to grow at all
type: lesson
---

# Lesson 9. ZeRO Stage 1 and 2: Partitioning Optimizer State and Gradients

**Mission link:** "Explain what ZeRO/FSDP shard, why data parallelism alone runs out of memory before it runs out of compute, and when tensor or pipeline parallelism is worth its communication cost" is the fourth bullet under Success looks like. This lesson covers the first two of ZeRO's three stages; Lesson 10 covers the third.
**Primary source:** [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**Prerequisites:** [Lesson 8](0008-why-data-parallelism-alone-runs-out-of-memory.md)

## Warm-up

1. ▢ Under mixed-precision Adam, what are the five per-parameter memory costs that add up to 16 bytes per parameter?

<details markdown="1"><summary>Check</summary>

An fp16 copy of the parameters (2 bytes), an fp16 copy of the gradients (2 bytes), and an fp32 copy each of the parameters, momentum, and variance kept by the optimizer (4 bytes each), totaling 16 bytes.

</details>

2. ▢ Does ordinary data parallelism reduce any of those 16 bytes per device as more devices are added?

<details markdown="1"><summary>Check</summary>

No. Every device holds a full, identical 16 bytes per parameter regardless of how many other devices exist; adding devices adds more redundant copies, not a smaller footprint per device.

</details>

## Know this

### The redundancy ZeRO removes

Lesson 8 established that every data-parallel device holds a full, identical copy of the optimizer state, the gradients, and the parameters. ZeRO's core idea is that this redundancy is unnecessary: across `Nd` data-parallel devices, only one full copy of that state needs to exist in total, split into `Nd` pieces, one piece per device, with each device reconstructing or receiving whatever piece it does not hold only at the moment it is actually needed. Rajbhandari et al. call this ZeRO-DP, and define it as three stages that can be enabled cumulatively, each partitioning one more piece of the model states than the last.

### Stage 1: partitioning the optimizer state

**`P_os`** (optimizer state partitioning) splits only the optimizer state, the largest single share of the 16 bytes per parameter (the fp32 parameter copy, momentum, and variance: 12 of the 16 bytes), across the `Nd` devices, so each device holds only `1/Nd` of it instead of the whole thing. Rajbhandari et al. report this alone gives a 4x memory reduction, at the **same communication volume as ordinary data parallelism**: no additional data has to move between devices beyond what the gradient all-reduce already required, because the optimizer state is only ever needed locally, at the moment each device applies its own shard of the update.

### Stage 2: also partitioning the gradients

**`P_os+g`** adds gradient partitioning on top of stage 1: each device only ever keeps the shard of the gradient it needs to update its own shard of the optimizer state and parameters, rather than holding the full gradient for every parameter in the model. This is a natural extension of the same idea, since a device that only owns `1/Nd` of the optimizer state only ever needs `1/Nd` of the gradient to update it. Rajbhandari et al. report this reaches an 8x memory reduction, again at the **same communication volume as ordinary data parallelism**: the reduce-scatter and all-gather operations this restructures the all-reduce into move the same total amount of data as a standard all-reduce would, just addressed to the device that actually needs each shard instead of broadcasting the whole thing to everyone.

### Why these two stages are close to a free lunch

Both stages remove real memory redundancy while adding no communication cost beyond what data parallelism already paid for. That is possible because optimizer state and gradients are only ever needed by the device responsible for updating the corresponding shard of parameters; nothing else in the forward or backward pass needs to read them. Stage 3, which partitions the parameters themselves, does not get to make the same claim, because every device's forward and backward pass needs every parameter, not just the ones it owns. Lesson 10 covers what that costs.

## Practice

1. ▢ A 7-billion-parameter model is trained with ZeRO stage 1 (`P_os`) across 8 data-parallel devices. Roughly how many bytes per parameter does each device now hold for the optimizer state, compared to the 12 bytes per parameter (fp32 parameters, momentum, variance) it would hold without partitioning?

<details markdown="1"><summary>Hint</summary>

Stage 1 splits the optimizer state evenly across all `Nd` devices.

</details>

<details markdown="1"><summary>Check</summary>

1.5 bytes per parameter (`12 / 8`), down from the full 12 bytes each device would otherwise hold. The fp16 parameters and fp16 gradients (4 bytes total) are unaffected by stage 1 alone.

</details>

2. ▢ Which of these best describes why ZeRO stages 1 and 2 do not increase communication volume beyond ordinary data parallelism?

    - a) They skip the gradient synchronization step entirely
    - b) Optimizer state and gradients are only ever needed locally, by the device responsible for the corresponding shard, so restructuring who holds what does not require moving more data in total
    - c) They only work on small models where communication cost does not matter
    - d) They compress the gradients before sending them, trading accuracy for bandwidth

<details markdown="1"><summary>Check</summary>

**b)** is the actual mechanism: no device needs another device's shard of optimizer state or gradients during the forward or backward pass, only at its own update step. (a) is false; synchronization still happens, just reshaped into reduce-scatter and all-gather. (c) and (d) describe mechanisms these two stages do not use.

</details>

3. ▢ A team wants the largest memory reduction ZeRO can offer without any increase in communication volume over ordinary data parallelism. Which stage should they use, and what memory reduction does it give?

<details markdown="1"><summary>Check</summary>

Stage 2 (`P_os+g`), giving an 8x memory reduction at the same communication volume as ordinary data parallelism. Stage 3 goes further on memory but is the one Rajbhandari et al. report a communication-volume increase for.

</details>

## Real-world reps

- [ ] Find the documentation for a training framework's ZeRO or FSDP configuration (PyTorch FSDP's sharding strategies, or DeepSpeed's ZeRO stage settings) and identify which configuration option corresponds to stage 1 and which to stage 2.
- [ ] Using the 16-bytes-per-parameter breakdown, compute the per-device memory for model states for a 13-billion-parameter model under stage 2, across 8 devices, and compare it to the same model with no ZeRO partitioning at all.
- [ ] Tomorrow: without looking ahead, write down a one-sentence prediction for Lesson 10: if every device's forward and backward pass needs every parameter, not just the ones it owns, what would a device partitioning the parameters themselves have to do differently from what stages 1 and 2 do?

## Going further

- [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
