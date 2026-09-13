---
title: 10. ZeRO Stage 3 and FSDP: Partitioning Parameters Too
description: Sharding the parameters themselves means reconstructing them on demand, which is the first thing this costs
type: lesson
---

# Lesson 10. ZeRO Stage 3 and FSDP: Partitioning Parameters Too

**Mission link:** "Explain what ZeRO/FSDP shard, why data parallelism alone runs out of memory before it runs out of compute, and when tensor or pipeline parallelism is worth its communication cost" is the fourth bullet under Success looks like. Lesson 9 covered the two stages that partition optimizer state and gradients for free; this lesson covers the third, which partitions the parameters themselves, and its real API.
**Primary source:** [Documentation: "Fully Sharded Data Parallel", PyTorch](https://pytorch.org/docs/stable/fsdp.html)
**Prerequisites:** [Lesson 9](0009-zero-stage-1-and-2-partitioning-optimizer-state-and-gradients.md)

## Warm-up

1. ▢ What memory reduction does ZeRO stage 2 (`P_os+g`) give, and at what communication cost relative to ordinary data parallelism?

<details markdown="1"><summary>Check</summary>

An 8x memory reduction, at the same communication volume as ordinary data parallelism: no extra data has to move, since optimizer state and gradients are only ever needed locally, by the device responsible for the corresponding shard.

</details>

2. ▢ Why can optimizer state and gradients be partitioned without added communication, in a way this lesson's subject cannot?

<details markdown="1"><summary>Check</summary>

Because only the device responsible for a given shard of the parameters ever needs that shard's optimizer state or gradient. Every device's forward and backward pass, by contrast, needs every parameter in the model, not just the ones it owns, which is what Lesson 10 has to account for.

</details>

## Know this

### The last piece: partitioning the parameters

**`P_os+g+p`**, ZeRO's third stage, partitions the parameters themselves on top of the optimizer state and gradients stage 2 already partitions: each device stores only `1/Nd` of the parameters at rest, rather than a full copy. Rajbhandari et al. report that this stage's memory reduction scales linearly with the data-parallel degree `Nd`: splitting across 64 devices yields a 64x memory reduction, and this is what makes their headline result work: they estimate a trillion-parameter model in mixed-precision Adam needs roughly 16 terabytes for its model states, which divided across 1,024 GPUs comes to about 16 GB per device, comfortably inside a 32 GB GPU.

That reduction is not free the way stages 1 and 2 were. Every device's forward and backward pass still needs every parameter, not just the `1/Nd` it stores, so whatever parameters a device does not hold have to be reconstructed from the other devices at the moment they are needed, then discarded again once that computation is done. Rajbhandari et al. report this costs a modest 50% increase in communication volume over ordinary data parallelism, in exchange for memory reduction that keeps scaling as more devices are added, rather than flattening out at 8x the way stages 1 and 2 do.

### The mechanism: gather on demand, then release

The pattern stage 3 uses is: hold only your own shard of the parameters at rest; just before a layer needs its full parameters for a forward or backward computation, **all-gather** the missing pieces from the other devices to reconstruct the full parameter tensor temporarily; once that layer's computation finishes, free the reconstructed copy and go back to holding only your own shard. This is the same all-gather collective operation as any other, just triggered far more often, once per layer per pass, rather than once per training step the way the gradient synchronization in ordinary data parallelism is.

### FSDP: the same idea, as a real API

PyTorch's `FullyShardedDataParallel`, commonly shortened to **FSDP**, implements exactly this pattern, and its own documentation says so directly: it describes itself as "inspired by ... the ZeRO Stage 3 from DeepSpeed." Wrapping a module in FSDP shards its parameters across the data-parallel devices, and during the forward and backward pass, FSDP replaces the module's parameters with reconstructed views gathered on demand, the same gather-then-release pattern this lesson just described in the abstract. FSDP also exposes lighter sharding strategies that shard only the gradients and optimizer state while leaving parameters unsharded, which is the same tradeoff stage 2 makes rather than stage 3's: less memory saved, but no added all-gather traffic for parameters during every forward and backward pass.

## Practice

1. ▢ Using ZeRO stage 3's reported scaling, about what memory reduction should a team expect from splitting a model's parameters, gradients, and optimizer state across 32 devices?

<details markdown="1"><summary>Check</summary>

About 32x, since Rajbhandari et al. report stage 3's memory reduction scales linearly with the data-parallel degree `Nd` (64 devices gives 64x in their own example, so 32 devices gives roughly half that).

</details>

2. ▢ Why does partitioning the parameters themselves require extra communication that partitioning the optimizer state and gradients did not?

    - a) Parameters are stored in a different numeric precision, which is more expensive to transmit
    - b) Every device's forward and backward pass needs the full set of parameters, not just the shard it owns, so missing shards have to be gathered from other devices on demand
    - c) Parameter partitioning requires a slower network protocol than gradient partitioning
    - d) It does not actually require extra communication; the paper's 50% figure is for a different comparison

<details markdown="1"><summary>Check</summary>

**b)** is the actual mechanism: unlike optimizer state and gradients, which only the owning device ever needs, parameters are needed by every device for every layer's forward and backward computation, so an all-gather has to reconstruct whatever shards a device does not hold. (a), (c), and (d) do not describe the actual reason.

</details>

3. ▢ A team chooses PyTorch FSDP's `SHARD_GRAD_OP` strategy instead of `FULL_SHARD`. Which ZeRO stage does this correspond to, and what tradeoff does it make relative to `FULL_SHARD`?

<details markdown="1"><summary>Hint</summary>

`SHARD_GRAD_OP` leaves parameters unsharded and exposed in their full form, sharding only gradients and optimizer state.

</details>

<details markdown="1"><summary>Check</summary>

It corresponds to ZeRO stage 2. It saves less memory than `FULL_SHARD` (stage 3), since parameters are not partitioned, but it also avoids the added all-gather traffic stage 3 needs to reconstruct parameters on demand during every forward and backward pass.

</details>

## Real-world reps

- [ ] Read PyTorch's FSDP documentation (linked above) and find the description of what happens to a wrapped module's parameters during the forward pass. Write one sentence connecting it to the "gather, then release" pattern this lesson describes.
- [ ] Using the trillion-parameter, 1,024-GPU example from this lesson (roughly 16 TB of model states, 16 GB per device), redo the same calculation for a 100-billion-parameter model split across 64 devices, and check whether it comfortably fits an 80 GB GPU.
- [ ] Tomorrow: find a configuration example (in FSDP or DeepSpeed documentation) that sets a sharding strategy explicitly, and identify which ZeRO stage that specific configuration corresponds to, using this lesson's and Lesson 9's descriptions of what each stage shards.

## Going further

- [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
