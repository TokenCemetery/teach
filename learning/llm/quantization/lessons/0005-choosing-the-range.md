---
title: "5. Choosing the Range"
description: Why clipping the range trades a little clipping error for much less rounding error
type: lesson
---

# Lesson 5. Choosing the Range

**Mission link:** Predicting where a quantization error comes from means knowing which of its two parts a given clipping range makes large, and the range is the choice that moves one into the other.
**Primary source:** [Paper: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295), section 3.1
**Prerequisites:** [Lesson 4](0004-quantize-and-dequantize.md), [Clipping range](../GLOSSARY.md), [Clipping error](../GLOSSARY.md), [Rounding error](../GLOSSARY.md)

## Warm-up

1. ▢ A 4-bit affine quantizer covers the range -1 to 3. What are its step and its largest rounding error?

<details markdown="1"><summary>Check</summary>

The step is `s = 4 / 15 = 0.267` and the largest rounding error is `s/2 = 0.133`. The range is divided into 2^4 - 1 = 15 steps, and a value inside the range moves at most half a step.

</details>

2. ▢ A value lies outside a quantizer's grid limits. Is its error bounded by `s/2`? What is the error called?

<details markdown="1"><summary>Check</summary>

No. The value is clamped to the nearest grid limit, and the distance it travels is **clipping error**, which has no bound of `s/2` and grows with how far the value lies outside the range.

</details>

3. ▢ Why do quantizers usually pair symmetric weights with asymmetric activations?

<details markdown="1"><summary>Check</summary>

Asymmetric weights multiplied by asymmetric activations produce a term that depends on the input data, which costs latency and power at run time (Nagel et al., section 2.4.1). A symmetric weight grid removes that term, so only the activations keep the extra zero point.

</details>

## Know this

### Two errors pulling in opposite directions

The **clipping range** is the interval of real values that the integer grid covers, from `q_min` to `q_max`. Nagel et al. name the whole trade in one sentence of section 2.2: widening the range reduces clipping error, but it needs a bigger scale, and the rounding error, which lies between -s/2 and s/2, grows with it.

| Range | Clipping error | Rounding error | What goes wrong |
|---|---|---|---|
| Too narrow | Large: outliers are clamped | Small | The largest values are replaced by the range's edge |
| Too wide | None | Large: the step is big | Typical values fall into a few levels or round to zero |

Section 3.1 of the paper calls this the key trade-off in range setting, and says each method gives a different balance between the two errors. Weights are known ahead of time, so their range usually needs no data. An activation's range depends on the input, so Nagel et al. say it usually needs a few batches of calibration data, which is the job of the [calibration set](../GLOSSARY.md).

### The methods

**Min-max.** Take the smallest and largest value as `q_min` and `q_max`. This has no clipping error, and Nagel et al. warn that it is sensitive to outliers, because a strong outlier forces a large step and so excessive rounding error. It is what lesson 4 used.

**Mean squared error.** Search for the `q_min` and `q_max` that minimize the mean squared error between the original and the quantized tensor. The paper lists grid search, the golden section method and closed-form approximations as ways to solve it, and says the variants in the literature are all very similar. It is the method to reach for when outliers inflate the min-max range.

**Percentile.** Set the range to a high percentile of the absolute values, such as the 99.9th, so that a fixed fraction of the values is clipped. This is a simple heuristic, not one of the methods in section 3.1, and the experiment below uses it so you can see what a fixed fraction costs and buys.

Section 3.1 lists two more for special cases: minimizing cross-entropy for the final layer's logits, where the order of the largest values matters more than the many small ones, and a batch-normalization-based range for activations. This track quantizes LLMs without batch normalization, so it uses the first three.

Nagel et al. compare the first two on ImageNet classifiers in their Table 1, with weights quantized per tensor and activations left in floating point. For ResNet18 at 8 bits, min-max and MSE are about level: 69.57 against 69.45 top-1 accuracy. At 4 bits, min-max falls to 0.12 and MSE keeps 18.82. These are vision models, so read the shape of the result, not the numbers: with few levels, the range choice decides whether the model works at all.

### What the experiment shows

The Practice experiment quantizes a heavy-tailed tensor to 4 bits. Its largest value is 1.506 and its standard deviation is 0.034, a ratio of about 44. With the min-max range, the step is `1.506 / 7 = 0.215`, half of it is 0.108, which is more than three standard deviations, so almost every value rounds to zero. Clipping the 0.35 percent of values the MSE search clips cuts the error about six times. The grid is spent on a range that almost no value visits.

### Why this is not the whole answer for LLMs

MSE counts every value's squared error equally. Nagel et al. make the same point about logits: MSE may not suit values that are unequally important, because it weighs all the values equally. In an LLM the few largest values can be the important ones. [Dettmers et al.](https://arxiv.org/abs/2208.07339) report that setting the outlier feature dimensions to zero degraded validation perplexity by 600 to 1000 percent, although they make up about 0.1 percent of the features. A range that clips them has a tiny effect on the tensor's MSE and can have a large effect on the model. Lesson 7 explains where those values come from, and lesson 8 gives the fixes that do not clip them.

## Practice

1. ▢ A 4-bit signed symmetric quantizer with grid -7 to 7 has a min-max range of 1.506 on a tensor with standard deviation 0.034. What is `s`, and which values round to zero?

<details markdown="1"><summary>Check</summary>

`s = 1.506 / 7 = 0.215`. Any value with absolute value below `s/2 = 0.108` rounds to the integer 0, which is more than three standard deviations. For a bell-shaped tensor that is nearly every value, so one distant maximum has erased the tensor.

</details>

2. ▢ Which statement describes widening the clipping range?

    - a) Clipping error and rounding error both fall
    - b) Clipping error and rounding error both rise
    - c) Clipping error falls while rounding error rises
    - d) Clipping error rises while rounding error falls

<details markdown="1"><summary>Check</summary>

**c)** A wider range clamps fewer values, so clipping error falls, but the same number of levels now spans more distance, so the step and the rounding error grow. (a) would make range choice trivial, since you would always widen. (b) gets both wrong, since widening cannot raise clipping error. (d) describes narrowing the range, not widening it.

</details>

3. ▢ Predict, then run. This quantizes 100,000 heavy-tailed values to 4 bits under four ranges. Before running, predict which range has the lowest mean squared error, and whether min-max rounds more or less than half of all values to zero.

    ```python
    import numpy as np

    rng = np.random.default_rng(0)
    x = rng.standard_t(df=3, size=100_000) * 0.02   # heavy-tailed
    qmax = 7                                        # 4-bit signed symmetric grid: -7..7 times the scale


    def quantize(x, c):
        s = c / qmax
        return s * np.clip(np.round(x / s), -qmax, qmax)


    def mse(x, c):
        return np.mean((quantize(x, c) - x) ** 2)


    grid = np.linspace(0.01, np.abs(x).max(), 400)
    ranges = {
        "min-max": np.abs(x).max(),
        "p99.9": np.percentile(np.abs(x), 99.9),
        "p99": np.percentile(np.abs(x), 99),
        "MSE search": grid[np.argmin([mse(x, c) for c in grid])],
    }
    print("max |x| =", round(np.abs(x).max(), 3), " std =", round(x.std(), 3))
    for name, c in ranges.items():
        q = quantize(x, c)
        print(f"{name:10s} c={c:.3f}  mse={mse(x, c):.2e}  clipped={np.mean(np.abs(x) > c):6.2%}  rounded to zero={np.mean(q == 0):6.2%}")
    ```

<details markdown="1"><summary>Hint</summary>

Work out the step for min-max first, as in item 1, and compare half of it with the standard deviation.

</details>

<details markdown="1"><summary>Check</summary>

```text
max |x| = 1.506  std = 0.034
min-max    c=1.506  mse=8.15e-04  clipped= 0.00%  rounded to zero=98.72%
p99.9      c=0.252  mse=1.61e-04  clipped= 0.10%  rounded to zero=56.61%
p99        c=0.117  mse=1.53e-04  clipped= 1.00%  rounded to zero=29.40%
MSE search c=0.171  mse=1.35e-04  clipped= 0.35%  rounded to zero=41.52%
```

The MSE search wins, and min-max is worst, about six times higher, with 98.7 percent of the values rounded to zero. Clipping only 0.10 percent of values (p99.9) already cuts the error five times. Clipping 1 percent (p99) is slightly worse than the search (1.53e-04 against 1.35e-04), because the clipped values now cost more than the rounding saved: the best range sits between the extremes.

</details>

4. ▢ Predict, then run. Change `qmax = 7` to `qmax = 127`, which makes it an 8-bit grid, and rerun. Will clipping still win? What range does the MSE search now choose?

<details markdown="1"><summary>Check</summary>

```text
max |x| = 1.506  std = 0.034
min-max    c=1.506  mse=1.17e-05  clipped= 0.00%  rounded to zero=21.23%
p99.9      c=0.252  mse=5.51e-05  clipped= 0.10%  rounded to zero= 3.65%
p99        c=0.117  mse=1.30e-04  clipped= 1.00%  rounded to zero= 1.69%
MSE search c=1.019  mse=7.72e-06  clipped= 0.00%  rounded to zero=14.52%
```

Clipping no longer wins: min-max beats both percentile ranges, and the MSE search picks 1.019, close to the full range, with under 0.005 percent of values clipped. With 127 levels per side the step is small enough that outliers cost little rounding error, while clipping them costs a lot. This is the same shape as Nagel et al.'s Table 1, where min-max and MSE are level at 8 bits: the fewer the levels, the more a tight range pays.

</details>

5. ▢ A team sets each LLM activation's range by minimizing MSE, and perplexity jumps. Use this lesson to give the most likely mechanism, and say what the MSE could not see.

<details markdown="1"><summary>Check</summary>

The range clipped the outlier features. They are a tiny share of the values, so clamping them changes the tensor's MSE very little, but they matter far more than their number: Dettmers et al. measured 600 to 1000 percent higher perplexity when those dimensions were set to zero. MSE weighs every value equally, and Nagel et al. note that this is the wrong weighting when values differ in importance. The range-setting objective is a local proxy for the task loss, and here it points the wrong way. Keeping outliers out of the clipped set is lesson 8's subject.

</details>

## Real-world reps

- [ ] Rerun the experiment with `df=10`, then with `rng.normal` instead of `standard_t`. Record the best clip from the MSE search as a multiple of the standard deviation each time, and note how it moves as the tails get lighter.
- [ ] Take one weight matrix from a small open model and print its maximum absolute value alongside its 99th and 99.9th percentiles of absolute value. Decide whether min-max would waste most of a 4-bit grid on it.
- [ ] Tomorrow: without notes, say what min-max, MSE and percentile each optimize, and which bit width makes the choice matter most. Then reread section 3.1 and check whether you named the right trade-off.

## Going further

- [The Quantization Mapping](../reference/quantization-mapping.md)
- [Paper: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295)
- [Paper: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., 2022](https://arxiv.org/abs/2208.07339), section 4.2, for why clipping outliers is dangerous
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
