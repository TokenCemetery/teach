---
title: "6. Granularity"
description: Per-tensor, per-channel and per-group scales, and what each costs in stored bits
type: lesson
---

# Lesson 6. Granularity

**Mission link:** Predicting a quantized tensor's error also means knowing how many values share each scale, because a scale is set by the largest value in its share and every extra scale costs stored bits.
**Primary source:** [Paper: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295), sections 2.2.3 and 2.4.2
**Prerequisites:** [Lesson 5](0005-choosing-the-range.md), [Granularity](../GLOSSARY.md), [Group size](../GLOSSARY.md), [Effective bits per weight](../GLOSSARY.md)

## Warm-up

1. ▢ With min-max range setting, what decides a quantizer's scale, and what does one outlier do to it?

<details markdown="1"><summary>Check</summary>

The range, which is set by the largest and smallest values, divided by the number of steps. One outlier widens the range, so the scale grows and the step gets coarser for every other value, which can round most of them to zero (lesson 5).

</details>

2. ▢ A 4-bit scheme stores one 16-bit scale per group of 32 weights. What are its effective bits per weight?

<details markdown="1"><summary>Check</summary>

4.5. The scale adds 16 / 32 = 0.5 bits per weight to the 4 bits of each value (lesson 1).

</details>

3. ▢ Why does a symmetric grid need only a scale, and what is the cost of dropping the zero point?

<details markdown="1"><summary>Check</summary>

Symmetric quantization fixes the zero point at zero, so there is nothing else to store. The cost is that the grid is centred on zero, so a one-sided tensor wastes the levels on the empty side (lesson 4).

</details>

## Know this

### What shares a scale

**Granularity** is how many values share one scale and zero point. A small scale-sharing set means a small range, so an outlier only ruins the set it sits in. The cost is that every set needs its own stored scale.

```text
W: output channels (rows) x input features (columns)

per-tensor    one scale for the whole matrix
per-channel   one scale per row (per output channel of a weight matrix)
per-group     one scale per `group size` consecutive values within a row, such as 64 or 128
per-token     one scale per row of an activation matrix X (tokens x features)
```

Nagel et al. note that per-tensor quantization is standard because every fixed-point accelerator supports it, and that per-channel quantization of the weights helps most when the weight distribution varies a lot from channel to channel. They also describe applying a quantizer per group of weights or activations, and say that finer groups generally improve accuracy at the cost of extra overhead.

### Why per-channel works for weights and not for activations

A linear layer computes each output as a sum over input features. With quantized values written as scale times integer, the scales can leave the sum only if they are constant across it:

```text
y[i] = sum over k of (s_w[i] * W_int[i,k]) * (s_x * x_int[k])
     = s_w[i] * s_x * (sum over k of W_int[i,k] * x_int[k])
```

The bracket is a pure integer dot product, which is what the hardware accelerates, and the two scales multiply the result once at the end. A per-output-channel weight scale `s_w[i]` is constant over the sum, because `i` names the output and `k` is summed. Nagel et al. conclude that per-channel weight quantization can be applied with a separate per-channel scale, without rescaling the accumulator.

A per-input-channel activation scale would be `s_x[k]`, which changes with the summed index. It cannot leave the sum, and Nagel et al. say it "would therefore require rescaling the accumulator for each input channel". Per-channel activation quantization is much harder to implement for that reason. A per-token activation scale, one per row of `X`, is constant across the sum for a given token and costs nothing: [Dettmers et al.](https://arxiv.org/abs/2208.07339) use exactly this in their vector-wise quantization, one constant per row of the activations and one per column of the weights, and undo both with the outer product of the constants. Lesson 7 shows why that is not enough for LLMs: the outliers sit in feature dimensions, which is the axis a per-token scale does not separate.

Per-group quantization has the same issue for the integer accumulator, since the scale changes inside the sum. The accumulator limit in the paper is why Nagel et al. leave group scales out. In weight-only schemes, the weights are dequantized to 16-bit inside the kernel and multiplied in 16-bit (see [weight-only quantization](../GLOSSARY.md)), so no integer accumulator carries mixed scales and a group scale is free to vary.

### What the scales cost

Each group adds its scale, and any zero point, to the checkpoint. The **effective bits per weight** is the value's bit width plus the metadata shared out over the group:

```text
effective bits = b + (scale bits + zero point bits) / group size
```

| Group size | Overhead with a 16-bit scale | Effective bits for 4-bit weights |
|---|---|---|
| 1024 | 0.0156 | 4.0156 |
| 256 | 0.0625 | 4.0625 |
| 128 | 0.125 | 4.125 |
| 64 | 0.25 | 4.25 |
| 32 | 0.5 | 4.5 |

Per-channel is just a group whose size is the row length, and per-tensor is a group of every weight: both cost almost nothing. The lesson 1 figure for group 32 is the last row.

### What small groups buy

The experiment in Practice quantizes a synthetic weight matrix at 4 bits, with rows of different scales and heavy tails. Error falls steadily as the groups shrink, and per-tensor is the worst by far. One group of 64 has only 64 chances to contain an outlier, and the outlier affects only those 64 values.

The largest empirical study of this is [Dettmers and Zettlemoyer](https://arxiv.org/abs/2212.09720): more than 35,000 zero-shot experiments with 3 to 8 bits across LLMs from 19M to 176B parameters. They find it hard to improve the trade between model size in bits and accuracy at all, with only two things helping: a small block size (their term for group size) and the data type. For 4-bit Pythia models, going from a block size of 1024 to 64 adds 0.24 bits per parameter and improves zero-shot accuracy almost as much as going from 4 to 5 bits. A 16-bit constant per block costs 16 / 64 - 16 / 1024 = 0.23 bits, close to the paper's figure. Small groups are the cheap bits.

## Practice

1. ▢ A 4-bit scheme stores a 16-bit scale and a 4-bit zero point per group of 64 weights. What are its effective bits per weight?

<details markdown="1"><summary>Check</summary>

4 + (16 + 4) / 64 = 4.3125, about 4.31. The zero point adds 4 / 64 = 0.0625 on top of the scale's 0.25. A symmetric scheme would drop that 0.0625 and land on 4.25.

</details>

2. ▢ What makes a per-output-channel weight scale compatible with an integer matrix multiplication while a per-input-channel activation scale is not?

    - a) The weight scale fits in only eight bits
    - b) The weight scale needs a separate offset term
    - c) The weight scale is constant across the summation
    - d) The weight scale changes value between output channels

<details markdown="1"><summary>Check</summary>

**c)** The scale for output `i` multiplies the whole sum over `k`, so it leaves the sum and is applied once after the integer accumulation. An activation scale indexed by input channel changes inside the sum, so the accumulator would need rescaling at every input channel. (a) is about storage and does not decide where a scale can be applied. (b) confuses a scale with a zero point, and symmetric weights need none. (d) is true but is the reason there are many scales, not the reason they can be factored out.

</details>

3. ▢ Predict, then run. Before running, order per-tensor, per-channel and the group sizes by error, from worst to best, and say whether error falls steadily. Then compute the effective bits for group 32.

    ```python
    import numpy as np

    rng = np.random.default_rng(0)
    rows, cols, b = 256, 1024, 4
    qmax = 2 ** (b - 1) - 1
    row_scale = rng.lognormal(0.0, 0.7, size=(rows, 1)) * 0.02
    W = rng.standard_t(df=4, size=(rows, cols)) * row_scale


    def quantize(W, group):
        """Symmetric absmax, one scale per `group` consecutive values in a row.
        group=None means one scale for the whole tensor."""
        G = W.reshape(1, -1) if group is None else W.reshape(-1, group)
        s = np.abs(G).max(axis=1, keepdims=True) / qmax
        Q = s * np.clip(np.round(G / s), -qmax, qmax)
        return Q.reshape(W.shape)


    print("granularity    rel. error   effective bits (16-bit scales)")
    for name, group in [("per-tensor", None), ("per-channel", cols), ("group 256", 256),
                        ("group 128", 128), ("group 64", 64), ("group 32", 32)]:
        err = np.mean((quantize(W, group) - W) ** 2) / np.mean(W ** 2)
        n_scales = 1 if group is None else W.size // group
        print(f"{name:13s}  {err:.4f}       {b + 16 * n_scales / W.size:.3f}")
    ```

<details markdown="1"><summary>Hint</summary>

Each step down in group size means more scales, and each scale is set by a smaller set of values. Then ask what a per-tensor scale does to a matrix whose rows differ in size.

</details>

<details markdown="1"><summary>Check</summary>

```text
granularity    rel. error   effective bits (16-bit scales)
per-tensor     0.7047       4.000
per-channel    0.1291       4.016
group 256      0.0599       4.062
group 128      0.0395       4.125
group 64       0.0267       4.250
group 32       0.0179       4.500
```

Error falls at every step: per-tensor leaves an error about 70 percent the size of the signal's own energy, per-channel removes most of that by giving every row its own scale, and each halving of the group cuts the error by about a third. Group 32 costs 4.5 effective bits. The data is synthetic, so read the ordering and the rough ratios, not the absolute numbers.

</details>

4. ▢ Going from group size 1024 to 64 adds how many bits per weight with a 16-bit scale? Compare that with the cost of moving the weights from 4 to 5 bits, and say what Dettmers and Zettlemoyer found about the benefits.

<details markdown="1"><summary>Check</summary>

16 / 64 - 16 / 1024 = 0.234 bits, against 1 full bit for 5-bit weights. In the paper, the smaller block size improved the zero-shot accuracy of 4-bit Pythia models almost as much as the extra bit would have. So shrinking the group is a much cheaper way to buy accuracy than adding a bit to every weight. The paper's headline result is that 4 bits is almost universally optimal for total model bits and zero-shot accuracy.

</details>

5. ▢ A team quantizes activations to 8 bits with one scale per token and still loses accuracy, because one feature dimension is huge at every token. Why does the per-token scale not help, and what axis would separate the outlier?

<details markdown="1"><summary>Check</summary>

Each token's scale is set by that token's largest value, and the huge feature dimension is the largest at almost every token, so every row's scale is inflated the same way. Dettmers et al. make this point: row-wise and vector-wise quantization scale the sequence dimension, and the outliers sit in the feature dimension, so both fail to isolate them. Only a per-feature-dimension scale would separate the outlier, and that is the per-input-channel activation scale from this lesson, which an integer matrix multiplication cannot apply cheaply.

</details>

## Real-world reps

- [ ] In the experiment, change `0.7` in `rng.lognormal(0.0, 0.7, ...)` to `0.0`, so every row has the same scale, and rerun. Record how much of per-channel's advantage over per-tensor remains, and explain it.
- [ ] Open the model card or config of any 4-bit GPTQ or AWQ checkpoint on the Hugging Face Hub, find its group size, and compute its effective bits per weight and its checkpoint size for the model's parameter count.
- [ ] Tomorrow: without notes, rebuild the table of group sizes against effective bits for a 16-bit scale and for an 8-bit scale, and say in one sentence why per-channel weight scales fit an integer matmul and per-channel activation scales do not.

## Going further

- [The Quantization Mapping](../reference/quantization-mapping.md)
- [Paper: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295)
- [Paper: "The case for 4-bit precision: k-bit Inference Scaling Laws", Dettmers and Zettlemoyer, 2022](https://arxiv.org/abs/2212.09720)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
