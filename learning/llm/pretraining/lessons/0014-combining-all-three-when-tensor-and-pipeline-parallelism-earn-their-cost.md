---
title: 14. Combining All Three: When Tensor and Pipeline Parallelism Earn Their Cost
description: Matching each parallelism strategy to the interconnect it tolerates, and when sharding alone is not enough
type: lesson
---

# Lesson 14. Combining All Three: When Tensor and Pipeline Parallelism Earn Their Cost

**Mission link:** "Explain what ZeRO/FSDP shard, why data parallelism alone runs out of memory before it runs out of compute, and when tensor or pipeline parallelism is worth its communication cost" is the fourth bullet under Success looks like, and this lesson is where it closes: when the extra engineering of tensor and pipeline parallelism is worth reaching for at all.
**Primary source:** [Paper: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
**Prerequisites:** [Lesson 13](0013-pipeline-parallelism-splitting-the-models-layers.md)

## Warm-up

1. ▢ What is the pipeline bubble, and what does a pipeline flush trade against it?

<details markdown="1"><summary>Check</summary>

The pipeline bubble is idle time at the start and end of a batch, while the pipeline is filling up or draining. A pipeline flush lets the pipeline drain and synchronizes every device's optimizer step together, which is what causes the bubble; the alternative would risk a microbatch's backward pass seeing a different weight version than its forward pass used.

</details>

2. ▢ In tensor parallelism's MLP split, how many all-reduce operations does the whole block need, and where does it happen?

<details markdown="1"><summary>Check</summary>

One, after the second matrix multiplication, combining each device's partial sum into the complete result.

</details>

## Know this

### Three axes, combined

Narayanan et al. call combining all three, tensor parallelism, pipeline parallelism, and data parallelism, at once **PTD-P**. Each axis splits a different thing: tensor parallelism splits what a single layer computes (Lesson 12), pipeline parallelism splits which layers a device is responsible for (Lesson 13), and data parallelism (Lessons 7 and 8, optionally sharded further with ZeRO, Lessons 9 through 11) splits the batch across replicas of whatever tensor-and-pipeline-parallel setup is being replicated. Combined this way, Narayanan et al. report training a trillion-parameter model at 502 petaFLOP/s across 3,072 GPUs, with each GPU sustaining 52% of its theoretical peak throughput, a genuinely large fraction to hold onto at that scale.

### Why the split follows the interconnect, not just the model

Narayanan et al. give a direct, practical reason for how they assign devices to each axis: tensor parallelism's all-reduce, needed once per layer as Lesson 12 described, is expensive enough that it performs best confined to devices connected by the fastest possible interconnect, within a single node (their own experiments use an 8-GPU DGX A100 server). Pipeline parallelism, by contrast, only ever passes activations between a handful of stage boundaries, using point-to-point communication that Narayanan et al. describe as "much cheaper," and which tolerates being spread across separate nodes without bottlenecking the whole computation, at the cost of the bubble Lesson 13 covered. They report peak performance specifically when the tensor-parallel size matches the number of GPUs in a single node, confirming this is not an incidental detail: it is the setup their own results say to aim for.

### Why not just use ZeRO everywhere and skip the extra engineering

Rajbhandari et al.'s ZeRO paper makes its own case directly, arguing that for the specific purpose of fitting a large model into memory, ZeRO-DP (Lessons 9 through 11) is at least as effective as model parallelism, sometimes more so, with comparable or better scaling efficiency, while being far easier to apply: data parallelism, they note, is widely usable across different workloads without changes, whereas model-parallel approaches like tensor and pipeline parallelism often require real engineering work, revising the model itself and building distributed operators for it. Tensor and pipeline parallelism are not free alternatives to sharding; they cost real development effort on top of their communication cost.

Put the two papers' own positions together, and the practical answer to "when is tensor or pipeline parallelism worth its cost" is: reach for ZeRO-style sharding first, since it solves the memory problem with the least engineering effort and no model-specific work. Reach for tensor and pipeline parallelism specifically once a training run needs to scale past what sharding alone handles efficiently, commonly at a device count and model size where communication overhead from sharding's own all-gathers becomes the bottleneck, or where a single layer's reconstructed weights are still too large for one device even after sharding. At that point, the combination is chosen deliberately to match communication pattern to interconnect: tensor parallelism's frequent, expensive all-reduces confined within a node, pipeline parallelism's infrequent, cheap point-to-point transfers spanning nodes, and data parallelism (sharded or not) filling out whatever device count remains.

## Practice

1. ▢ A team has 64 GPUs arranged as 8 nodes of 8 GPUs each, with fast intra-node interconnect and much slower inter-node links. Following Narayanan et al.'s own reported peak configuration, how would they assign tensor-parallel and pipeline-parallel degrees to this hardware?

<details markdown="1"><summary>Check</summary>

Tensor-parallel size of 8, matching the GPUs within one node, kept off the slower inter-node links; pipeline stages spanning across the 8 nodes, since pipeline parallelism's point-to-point communication tolerates the slower inter-node connection without bottlenecking the computation.

</details>

2. ▢ Per the ZeRO paper's own argument, why might a team choose ZeRO-DP over tensor or pipeline parallelism, even though both scale to very large models?

    - a) ZeRO-DP is always faster, at any device count, for every model
    - b) ZeRO-DP achieves comparable or better memory efficiency without requiring the model-specific engineering work (revised model code, distributed operators) that model-parallel approaches need
    - c) Tensor and pipeline parallelism cannot fit models larger than a single device's memory at all
    - d) ZeRO-DP eliminates the need for any form of parallelism entirely

<details markdown="1"><summary>Check</summary>

**b)** is the argument the ZeRO paper itself makes: comparable or better scaling efficiency, with far less engineering cost, since data parallelism is broadly applicable without model-specific changes. (a) overclaims a universal speed advantage the paper does not claim. (c) is the opposite of both papers' point, that model parallelism exists precisely to fit larger models. (d) contradicts ZeRO-DP's own reliance on data parallelism as its foundation.

</details>

3. ▢ Given the reasoning in this lesson, name one concrete situation where reaching for tensor or pipeline parallelism, despite their added engineering cost, would still be the right call over ZeRO-DP alone.

<details markdown="1"><summary>Check</summary>

Any answer along these lines is defensible: when sharding's own communication overhead becomes the bottleneck at very large device counts, or when a single layer's parameters remain too large to fit on one device even after ZeRO's sharding and on-demand reconstruction, forcing the computation itself, not just its storage, to be split across devices.

</details>

## Real-world reps

- [ ] Find a published training configuration for a large open model (a technical report or model card that states its parallelism setup) and identify which parts, if any, correspond to tensor parallelism, pipeline parallelism, and data parallelism or ZeRO sharding.
- [ ] Read the paragraph in the Megatron-LM paper (linked above) describing why tensor parallelism is confined within a node, and write one sentence contrasting it with the ZeRO paper's argument for preferring data parallelism where possible.
- [ ] Tomorrow: for a hypothetical cluster of your choosing (pick any number of nodes and GPUs per node), sketch a parallelism plan: what would go inside a node, what would cross nodes, and where ZeRO sharding would fit in, and write one sentence defending each choice.

## Going further

- [Paper: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
- [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Resources](../RESOURCES.md)

---

Stage 6 covered how compute gets split across devices, matched to what the interconnect between them can bear. Stage 7 turns to a different kind of failure at scale: the numerics of the training run itself, and what to do when the loss curve stops behaving.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
