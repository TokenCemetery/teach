---
title: 11. Activation Memory and ZeRO-R
description: Sharding model states solves one memory problem and leaves a second one, activations, standing
type: lesson
---

# Lesson 11. Activation Memory and ZeRO-R

**Mission link:** "Explain what ZeRO/FSDP shard, why data parallelism alone runs out of memory before it runs out of compute, and when tensor or pipeline parallelism is worth its communication cost" is the fourth bullet under Success looks like. Lessons 9 and 10 covered ZeRO-DP's three stages, which shard model states; this lesson covers the separate memory problem those three stages do not touch.
**Primary source:** [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**Prerequisites:** [Lesson 10](0010-zero-stage-3-and-fsdp-partitioning-parameters-too.md), [Activation checkpointing](../GLOSSARY.md)

## Warm-up

1. ▢ PyTorch's FSDP documentation describes itself as inspired by which ZeRO stage?

<details markdown="1"><summary>Check</summary>

ZeRO stage 3 (`P_os+g+p`), the stage that partitions parameters on top of optimizer state and gradients.

</details>

2. ▢ Why does partitioning parameters (stage 3) add communication that partitioning optimizer state and gradients (stages 1 and 2) does not?

<details markdown="1"><summary>Check</summary>

Because every device's forward and backward pass needs every parameter, not just the shard it owns, so missing shards have to be gathered from other devices on demand, unlike optimizer state and gradients, which only the owning device ever needs.

</details>

## Know this

### Solving model states leaves a second problem standing

Lessons 9 and 10 covered **ZeRO-DP**: the three stages that partition optimizer state, gradients, and parameters, the 16 bytes per parameter Lesson 8 counted. Rajbhandari et al. are explicit that this is not the whole memory picture. Once model states stop dominating, what they call **residual memory**, activations kept from the forward pass to compute gradients in the backward pass, temporary buffers, and memory lost to fragmentation, becomes the next bottleneck. Lesson 8's own GPT-2 example showed this is not a small effect: about 60 GB of activation memory at a sequence length of 1,024 and a batch size of 32, on a model whose model states alone came to only 24 GB. The three ZeRO-DP stages do nothing about that 60 GB; they only address the 24 GB. **ZeRO-R** is Rajbhandari et al.'s separate answer to the residual side.

### Checkpointing helps, but is not enough by itself

Activation checkpointing, the glossary term this lesson links to, discards most intermediate activations during the forward pass and recomputes them during the backward pass instead of keeping all of them in memory the whole time, trading extra compute for lower memory. Rajbhandari et al. note that checkpointing helps but is not sufficient on its own for the largest models: even the reduced set of activations checkpointing keeps can still be large, and, in setups that combine data parallelism with model parallelism, that reduced set is often needlessly replicated across model-parallel ranks that could instead be sharing it.

### What ZeRO-R adds on top

ZeRO-R attacks residual memory on three fronts, each aimed at a different part of it:

- **Activation partitioning.** Where model-parallel training would otherwise keep a redundant copy of the same activations on every model-parallel rank, ZeRO-R identifies and removes that replication, partitioning activations the same way ZeRO-DP partitions model states, and can additionally **offload** partitioned activations to CPU memory when that trade is worth making.
- **Right-sized temporary buffers.** Large temporary buffers used during training are given a deliberately chosen size, balancing memory use against computational efficiency, rather than being left to grow as large as a naive implementation would allow.
- **Defragmentation.** Tensors with very different lifetimes (some live for a whole training step, others only for a moment) create fragmented memory over time, which can cause a memory allocation to fail even when the total free memory would otherwise be enough. ZeRO-R manages memory proactively based on each tensor's expected lifetime, to prevent that fragmentation from accumulating.

Combined, Rajbhandari et al. refer to ZeRO-DP and ZeRO-R together simply as **ZeRO**: one half removing the redundancy in model states, the other half controlling everything else that training keeps in memory.

## Practice

1. ▢ A team has already applied ZeRO stage 3 to a model, reducing its model-state memory well within budget, but the run still runs out of memory during the forward pass on a long sequence length. Is this most likely a model-states problem or a residual-memory problem, and what is one thing that could address it?

<details markdown="1"><summary>Check</summary>

A residual-memory problem, most likely activation memory, which is sensitive to sequence length in a way model states are not. Activation checkpointing, activation partitioning, or offloading activations to CPU are all residual-memory techniques that could address it; adding more ZeRO-DP sharding would not, since model states were not the bottleneck here.

</details>

2. ▢ Which of these best describes why activation checkpointing alone is described as insufficient for the largest models?

    - a) Checkpointing is incompatible with ZeRO-DP and cannot be used alongside it
    - b) Even the reduced set of activations checkpointing keeps can still be large, and can be needlessly replicated across model-parallel ranks without further optimization
    - c) Checkpointing increases memory use in exchange for less compute
    - d) Checkpointing only works for models trained without mixed precision

<details markdown="1"><summary>Check</summary>

**b)** is the paper's own reasoning. (a) is false; ZeRO-R is described as complementary to checkpointing, not a replacement that conflicts with it. (c) reverses the actual tradeoff, which is less memory for more recomputation. (d) is not a constraint the paper describes.

</details>

3. ▢ Name the three things ZeRO-R optimizes, and match each to the residual-memory problem it targets: needlessly replicated activations across model-parallel ranks, memory allocation failing despite enough total free memory, and temporary buffers left to grow larger than necessary.

<details markdown="1"><summary>Check</summary>

Activation partitioning (and offload) addresses replicated activations across model-parallel ranks. Defragmentation, based on each tensor's expected lifetime, addresses allocation failures from fragmented memory. Right-sized temporary buffers address buffers growing larger than a balance of memory and compute efficiency would call for.

</details>

## Real-world reps

- [ ] Find where activation checkpointing (sometimes called gradient checkpointing) is exposed as an option in a training framework you have access to, and note what it costs in extra compute, if the documentation states it.
- [ ] Using Lesson 8's GPT-2 activation-memory example (about 60 GB at sequence length 1,024, batch size 32), predict qualitatively what happens to that number if the sequence length is doubled, and check your prediction against any formula or explanation the framework's documentation gives for activation memory scaling.
- [ ] Tomorrow: for a model and hardware setup you have access to (or a hypothetical one), decide which residual-memory technique (checkpointing, activation partitioning, CPU offload, or some combination) you would reach for first, and write one sentence for why, given what each one trades away.

## Going further

- [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Resources](../RESOURCES.md)

---

Stage 5 covered how one training run's memory gets sharded across devices that are all doing the same kind of work. Stage 6 covers a different kind of split: dividing the model itself across devices that each do a different part of the computation.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
