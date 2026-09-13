---
title: 12. Tensor Parallelism: Splitting a Layer's Matrices
description: Choosing which axis to split a weight matrix along so an entire transformer block needs only one all-reduce
type: lesson
---

# Lesson 12. Tensor Parallelism: Splitting a Layer's Matrices

**Mission link:** "Explain what ZeRO/FSDP shard, why data parallelism alone runs out of memory before it runs out of compute, and when tensor or pipeline parallelism is worth its communication cost" is the fourth bullet under Success looks like. This lesson covers what tensor parallelism actually splits and why; Lesson 13 covers pipeline parallelism, and Lesson 14 covers when either is worth its cost.
**Primary source:** [Paper: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
**Prerequisites:** [Lesson 11](0011-activation-memory-and-zero-r.md)

## Warm-up

1. ▢ ZeRO stage 3 shards parameters at rest but reconstructs the full parameter tensor on demand before a layer's forward or backward pass, via all-gather. Does every device compute the same full layer once the parameters are reconstructed, or does each device compute a different part of the layer's math?

<details markdown="1"><summary>Check</summary>

Every device computes the same full layer, using its own reconstructed full copy of that layer's parameters. ZeRO shards where the parameters live at rest; it does not split the computation of any single layer across devices.

</details>

## Know this

### Splitting the computation, not just where weights live

**Tensor parallelism** takes a different approach from anything in Stage 5: rather than reconstructing a full layer's weights on any one device, it splits an individual layer's weight matrices across devices so that each device only ever holds, and only ever computes with, its own slice of the layer. No device ever needs the full weight matrix at once.

### A worked example: the MLP block

A transformer's MLP block computes `Y = GeLU(XA)` followed by `Z = Dropout(YB)`, two matrix multiplications with a nonlinearity in between. Narayanan et al. describe the specific way Megatron splits this that keeps communication to a minimum: split the first weight matrix `A` **along its columns**, `A = [A1, A2]`, giving each device a complete, independently computable output slice, `Y1 = GeLU(XA1)` and `Y2 = GeLU(XA2)`, with no synchronization needed between the two devices to compute them. This works because splitting along columns splits the *output* dimension, not the dimension being summed over, so each device's slice of `Y` is already the true, complete answer for its columns, and `GeLU`, applied elementwise, can be applied to each complete slice independently.

The second weight matrix, `B`, is then split **along its rows** to match, `B = [B1; B2]`, so each device computes `Yi @ Bi` using only its own local slice of `Y` and `B`. This gives every device a partial sum toward the true output `Z`; the two devices' partial sums are combined with a single all-reduce, and only then does dropout apply to the complete, correct result.

### Why column, then row, and not the other way around

If `A` were instead split along its rows (splitting the dimension being summed over, rather than the output dimension), each device's slice of `X @ A` would only be a **partial sum** toward the true pre-activation values, not a complete answer, since summing over only part of the contraction dimension does not give the right numbers for any output column. `GeLU` cannot be applied correctly to a partial sum and then combined afterward, because `GeLU` is nonlinear: `GeLU(a + b)` is not `GeLU(a) + GeLU(b)`. Splitting `A` by columns avoids ever needing to apply a nonlinearity to a partial sum in the first place, which is exactly the reason Narayanan et al. give for choosing it. The column-then-row pairing is what lets the entire two-matrix MLP block need only **one** all-reduce, right at the end, rather than a synchronization step in between the two matrix multiplications as well.

### The same pattern applies to attention

Multi-head attention already has a natural place to split: the query, key, and value projections are partitioned column-parallel, so each device handles a subset of attention heads independently, with no cross-device coordination needed during the attention computation itself. The output projection that follows is then split along its rows to match, the same column-then-row pairing as the MLP block, needing one all-reduce at the end of the attention block.

## Practice

1. ▢ A transformer's MLP block is split with `A` along its columns and `B` along its rows, as this lesson describes. How many all-reduce operations does this scheme need for the entire block, from `X` to the final `Z`?

<details markdown="1"><summary>Check</summary>

One, right after the second matrix multiplication, to combine each device's partial sum of `Z` into the complete result. The column split of `A` avoids needing any synchronization between the two matrix multiplications.

</details>

2. ▢ If `A` were split along its rows instead of its columns, what would go wrong with applying `GeLU` immediately after the first matrix multiplication?

<details markdown="1"><summary>Hint</summary>

Ask what each device's local result actually represents when the dimension being summed over is the one that got split, rather than the output dimension.

</details>

<details markdown="1"><summary>Check</summary>

Each device would only hold a partial sum toward the true pre-activation values, not the complete values, since only part of the contraction dimension was included in each device's local computation. `GeLU` is nonlinear, so applying it to a partial sum and later combining the results does not give the same answer as applying it to the complete sum, meaning a synchronization step would be needed before `GeLU` could correctly run at all.

</details>

3. ▢ In the attention block, how are the query, key, and value projections split, and what natural feature of multi-head attention makes that split convenient?

<details markdown="1"><summary>Check</summary>

They are split column-parallel, the same way `A` is split in the MLP block. Multi-head attention already computes each head's attention independently of the others, so assigning different heads (or groups of heads) to different devices requires no coordination during the attention computation itself, the same way splitting the MLP's output dimension required none.

</details>

4. ▢ Why does tensor parallelism, as this lesson describes it, never need to reconstruct a layer's full weight matrix on any single device, unlike ZeRO stage 3?

<details markdown="1"><summary>Check</summary>

Because each device only ever computes with its own slice of the weight matrix; the column-then-row split is specifically chosen so that every intermediate computation on each device is either a complete, independent result (after the column split) or a partial sum that gets combined by an all-reduce (after the row split), rather than requiring the full matrix to exist anywhere.

</details>

## Real-world reps

- [ ] Read the description of tensor parallelism in the Megatron-LM paper (linked above), and find the figure showing the MLP and attention block splits. Trace, in your own words, where each `f` and `g` operator (the paper's notation for the forward/backward identity-versus-all-reduce pair) sits in the diagram.
- [ ] Sketch, on paper, a 4-row-by-2-column weight matrix `A` and a 2-row-by-4-column input `X`, and work out by hand what `X @ A` looks like when `A` is split by columns into two 4-row-by-1-column pieces, versus split by rows into two 2-row-by-4-column pieces. Confirm which split gives each device a complete answer.
- [ ] Tomorrow: without looking ahead, write a one-sentence prediction for Lesson 13: if tensor parallelism needs an all-reduce for every transformer layer, what kind of interconnect would that likely require between devices, and would you expect it to work equally well between devices in different physical server racks?

## Going further

- [Paper: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
