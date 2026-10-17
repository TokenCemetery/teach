---
title: Weight PTQ Methods
description: Round-to-nearest, GPTQ and AWQ side by side, and what the calibration set does
type: reference
---

# Weight PTQ Methods: Round-to-Nearest, GPTQ and AWQ Compared

Stage 4 compressed for lookup. [Lesson 9](../lessons/0009-round-to-nearest.md) covers round-to-nearest (RTN), [lesson 10](../lessons/0010-gptq.md) GPTQ, [lesson 11](../lessons/0011-awq.md) AWQ, and [lesson 12](../lessons/0012-the-calibration-set.md) the calibration set.

## The three methods side by side

| | Round-to-nearest | GPTQ | AWQ |
|---|---|---|---|
| Idea | Round each weight to its nearest level | Round columns in order, push each error onto the columns not yet rounded | Scale salient input channels up before rounding, divide the activation by the same scale |
| Reads from data | Nothing | Layer inputs, summed into `H = 2 X X^T` | Mean activation magnitude per channel, plus layer outputs to score each `alpha` |
| Changes weight values | No | Yes, every later column after each rounding | Yes, by the per-channel scale `s = s_X^alpha`, then rounds to nearest |
| Objective | Each weight's own error | `argmin \|\| W X - Ŵ X \|\|^2` per layer | The same layer-output error, searched over `alpha` in [0, 1] |
| Backpropagation | None | None | None |
| Cost | Negligible | About 4 GPU hours for 175B parameters (paper) | A grid of 20 values of `alpha` per layer (paper) |
| Grid | One scale per row or per group | Fixed before the loop; per-group scale set when the loop reaches the group | Per-group, 128 in the paper |
| Main risk | Collapses at 3 bits with per-row scales | Overfits a small or mismatched calibration set | Scaling too hard hurts the non-salient channels |

## What each does to the numbers

| WikiText-2 perplexity | 16-bit | RTN | GPTQ | AWQ |
|---|---|---|---|---|
| OPT-175B, 4 bits, per-row grid | 8.34 | 10.54 | 8.37 | not reported there |
| OPT-175B, 3 bits, per-row grid | 8.34 | 7,300 | 8.68 | not reported there |
| Llama-2 7B, 4 bits, groups of 128 | 5.47 | 5.73 | 5.69 | 5.60 |
| Llama-2 7B, 3 bits, groups of 128 | 5.47 | 6.66 | 6.43 | 6.24 |

The first two rows come from the GPTQ paper and the last two from the AWQ paper. The grids and models differ, so compare within a row and the shape between rows, not the numbers across them. Each paper evaluates its own method against the other, so read the gaps as the authors' runs.

## Why the error behaves as it does

| Fact | Consequence |
|---|---|
| Each removed bit roughly doubles the step | Round-to-nearest error roughly doubles per bit |
| In the toy of lesson 9, error ratios equal the step ratios: 127 / 7 = 18.1 from 8 to 4 bits, 7 / 3 = 2.3 from 4 to 3 | The last bits are the expensive ones |
| Round-to-nearest minimises each weight's error, not the layer output's error | 919 of 2000 random roundings beat it on a correlated toy layer |
| GPTQ's gain comes from correlated inputs | With independent inputs it nearly vanishes (0.2680 against 0.2595 in the toy) |
| A salient weight is picked by its activation, not its size | On OPT-6.7B at 3 bits, 1% chosen by activation gives 11.39, by weight size 22.37, plain round-to-nearest 23.54 |
| Scaling a channel by `s` shrinks its relative error by about `1 / s` | Too large an `s` raises the step for the other channels in the group |

## GPTQ's three scaling changes and act-order

| Change | What it fixes |
|---|---|
| Same column order for every row | One inverse update per column serves all rows |
| Lazy batch updates, 128 columns at a time | The update is memory-bound, so batching it uses the GPU |
| Dampening of 1% of the mean diagonal, plus a Cholesky factor | Numerical error that can make the inverse indefinite |
| Act-order (authors' code, not the paper): columns sorted by `H`'s diagonal, largest first | Fixes bad results such as OPT-66B at 3 bits (14.16 to 9.95); may need inference changes unless static groups are used |

## What the calibration set does

| | GPTQ | AWQ |
|---|---|---|
| Typical size | Paper: 128 segments of 2048 tokens, from C4 | AWQ at 16 sequences beats GPTQ at 192 on OPT-6.7B, 3 bits (authors' run) |
| llm-compressor | 128 to 512 samples is typical, start with 128 to 256 | Same advice; its example uses 256 |
| Needs more data because | It estimates a whole matrix of feature co-variation | It estimates one mean per channel |
| Mismatch penalty, OPT-6.7B, 3 bits (AWQ paper) | 2.3 to 4.9 perplexity worse | 0.5 to 0.6 worse |

- Round-to-nearest is data-free. GPTQ and AWQ need a calibration set. Neither backpropagates through it.
- A calibration set is not training data, and its domain shows up in the result.
- Match the set to the target use: general text for a general model, instruction data for an instruction model, code for a coding model (llm-compressor).
- Evaluate on held-out text from the calibration domain and on text from the other domains you serve. A gain in one and a loss in the other is a mismatch.
- A perplexity measured on the text the set was drawn from is flattered. The GPTQ paper says its C4 results are not fully zero-shot for this reason.
- In the lesson 12 toy, too few samples (64 for 128 features) made GPTQ worse than round-to-nearest even in-domain.

## Before you trust a weight-PTQ checkpoint

- Which method, which bit width, and which group size or grid.
- Which calibration set, how many samples, and how long. If the model card does not say, that is a gap.
- Whether the quoted perplexity is on the calibration domain.
- Whether a data-free baseline at the same grid was measured on the same evaluation.
- For GPTQ with act-order and groups, whether it needs inference changes that can cost speed, or was made with static groups.
