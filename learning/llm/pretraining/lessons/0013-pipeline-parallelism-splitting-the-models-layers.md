---
title: 13. Pipeline Parallelism: Splitting the Model's Layers
description: Assigning consecutive layers to different devices, and the idle time that costs at the start and end of every batch
type: lesson
---

# Lesson 13. Pipeline Parallelism: Splitting the Model's Layers

**Mission link:** "Explain what ZeRO/FSDP shard, why data parallelism alone runs out of memory before it runs out of compute, and when tensor or pipeline parallelism is worth its communication cost" is the fourth bullet under Success looks like. Lesson 12 covered splitting a layer's own computation across devices; this lesson covers splitting the model's layers across devices instead.
**Primary source:** [Paper: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
**Prerequisites:** [Lesson 12](0012-tensor-parallelism-splitting-a-layers-matrices.md)

## Warm-up

1. ▢ In tensor parallelism's MLP split, why does splitting the first weight matrix along its columns, rather than its rows, avoid needing a synchronization step before applying `GeLU`?

<details markdown="1"><summary>Check</summary>

A column split divides the output dimension, so each device's slice of the result is already complete and correct; a row split would divide the dimension being summed over, leaving each device with only a partial sum, and `GeLU` cannot be correctly applied to a partial sum since it is nonlinear.

</details>

## Know this

### Splitting the model's depth, not a single layer's width

**Pipeline parallelism** takes a third approach, different from both ZeRO (Stage 5) and tensor parallelism (Lesson 12): rather than splitting what any one layer computes, it shards the model's layers themselves across devices. For a model built from the same transformer block repeated many times, this is straightforward: each device, or **pipeline stage**, is assigned an equal, contiguous run of transformer layers, and a training example's forward pass moves through the devices in sequence, stage by stage, the way a physical assembly line moves a part from station to station.

### Why a batch gets split into microbatches

If an entire batch had to pass completely through stage 1 before stage 2 could start any work on it, every stage but one would sit idle almost all the time; there would be nothing pipelined about it. Narayanan et al.'s approach instead splits a batch into smaller **microbatches** and pipelines their execution: while stage 1 works on microbatch 2, stage 2 can simultaneously be working on microbatch 1's output, the same way a real assembly line has several parts in progress across its stations at once, rather than finishing one part completely before starting the next.

### The pipeline bubble

Even with microbatches staggered through the pipeline, there is unavoidable idle time at the start of a batch, before every stage has anything to work on yet, and at the end, after the last microbatch has left the earlier stages and only later stages still have work left to finish. Narayanan et al. call this idle time the **pipeline bubble**, and it is a genuine cost: the more pipeline stages there are, the more of this idle time accumulates relative to useful computation, unless enough microbatches are used per batch to keep the pipeline fuller for longer between the unavoidable fill-up and drain-out at each end.

### Why pipelining needs periodic flushes

A subtlety Narayanan et al. are careful about: naive pipelining, run purely for throughput with no other constraint, can let a microbatch's backward pass see a different, already-updated version of the weights than its own forward pass used, if other microbatches further along the pipeline finished their optimizer step first. That breaks the ordinary, synchronous meaning of a training step, where every example in a batch is supposed to see one consistent set of weights across its own forward and backward pass. To keep that guarantee exactly, Narayanan et al. introduce periodic **pipeline flushes**: points where the pipeline is allowed to drain completely and every device's optimizer step happens together, synchronized, before the next batch's microbatches start filling the pipeline again. This flush is also where the bubble described above actually occurs; it is the price paid for keeping synchronous optimizer semantics rather than letting weight versions drift across microbatches.

## Practice

1. ▢ A model with 8 transformer layers is split into 4 pipeline stages, 2 layers each. If a whole batch had to complete stage 1 entirely before stage 2 could begin any work, what would happen to stages 2 through 4 while stage 1 is working?

<details markdown="1"><summary>Check</summary>

They would sit idle, since none of them would have anything to compute until stage 1 finished the entire batch and handed its output onward. This is exactly the problem splitting a batch into microbatches is meant to avoid.

</details>

2. ▢ Which of these best describes what the pipeline bubble is?

    - a) The extra memory used to store activations at pipeline stage boundaries
    - b) Idle time at the start and end of a batch, while the pipeline is filling up or draining, that adds no useful computation
    - c) The communication delay between a tensor-parallel all-reduce and the next matrix multiplication
    - d) A deliberate pause inserted to let devices cool down between batches

<details markdown="1"><summary>Check</summary>

**b)** is exactly what Narayanan et al. name it. (a) describes a real cost of pipelining but not the bubble specifically. (c) describes a tensor-parallelism concern, not a pipeline-parallelism one. (d) is not a real reason for the idle time.

</details>

3. ▢ Why do periodic pipeline flushes matter for correctness, not just for throughput?

<details markdown="1"><summary>Hint</summary>

Ask what could go wrong for one specific microbatch's backward pass if other microbatches further along the pipeline had already triggered an optimizer step.

</details>

<details markdown="1"><summary>Check</summary>

Without a flush, a microbatch's backward pass could see a different, already-updated version of the weights than its own forward pass used, if other microbatches completed their optimizer step first. That breaks synchronous optimizer semantics, where every example in a batch is meant to see one consistent set of weights across its own forward and backward pass. A flush lets the pipeline drain and every device's optimizer step happen together, preserving that guarantee at the cost of the bubble.

</details>

4. ▢ A team increases the number of microbatches per batch without changing the number of pipeline stages. What effect would this have on the fraction of time lost to the pipeline bubble?

<details markdown="1"><summary>Check</summary>

It would shrink the fraction of time lost to the bubble, since the fixed fill-up and drain-out cost gets amortized over more useful microbatch computation in between. The bubble itself does not disappear, but it becomes a smaller share of the total time spent per batch.

</details>

## Real-world reps

- [ ] Draw, on paper, four pipeline stages and four microbatches, and sketch a timeline showing which stage is working on which microbatch at each time step, including the idle cells at the start and end that represent the bubble.
- [ ] Read the section of the Megatron-LM paper (linked above) describing pipeline flushes, and write one sentence in your own words distinguishing what a flush guarantees from what microbatching alone guarantees.
- [ ] Tomorrow: without looking ahead, write a one-sentence prediction for Lesson 14: given that tensor parallelism needs an all-reduce for every layer while pipeline parallelism only needs to pass activations between a handful of stage boundaries, which one would you expect to tolerate a slower, longer-distance network connection between devices better?

## Going further

- [Paper: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
