---
title: "2. Floating-Point Formats"
description: How sign, exponent and mantissa bits split range from precision in fp32, fp16 and bf16
type: lesson
---

# Lesson 2. Floating-Point Formats

**Mission link:** Every number format later in this track is a choice of how to split a few bits between range and precision, so you need to read a bit layout and say what it can and cannot hold before you can judge what a quantized model lost.
**Primary source:** [Paper: "A Study of BFLOAT16 for Deep Learning Training", Kalamkar et al., 2019](https://arxiv.org/abs/1905.12322)
**Prerequisites:** [Lesson 1](0001-what-quantization-buys.md), [Exponent bits](../GLOSSARY.md), [Mantissa bits](../GLOSSARY.md)

## Warm-up

1. ▢ How many bytes per parameter do fp32, bf16 and int8 use, and how much memory do the weights of a 7B-parameter model take in each?

<details markdown="1"><summary>Check</summary>

fp32 uses 4 bytes (28 GB), bf16 uses 2 bytes (14 GB) and int8 uses 1 byte (7 GB). The weights alone, at the nominal bit width.

</details>

2. ▢ Why does a smaller weight format usually make batch-1 decoding faster?

<details markdown="1"><summary>Check</summary>

Decoding at batch size 1 is memory-bound: every weight is read once per token and used for little arithmetic, so fewer bytes per weight means less to read. Weight-only quantization does not make the arithmetic itself faster.

</details>

## Know this

### Three fields

A floating-point number stores a sign bit, some **exponent bits** and some **mantissa bits**. For a normal value the exponent field `e` and mantissa field `m` give

```text
value = (-1)^sign × 2^(e - bias) × (1 + m / 2^M)
```

where `M` is the number of mantissa bits and `bias` is a fixed offset that lets the exponent be negative. The exponent picks which power of two the value sits near. The mantissa picks one of 2^M evenly spaced points between that power of two and the next. An exponent field of all zeros is reserved for zero and for subnormal values, which are smaller than the smallest normal value and fill the gap down to zero with the same spacing. An exponent field of all ones is reserved in IEEE formats for infinity and NaN.

| Format | Total bits | Sign / exponent / mantissa | Bias | Largest finite | Smallest normal | Machine epsilon |
|---|---|---|---|---|---|---|
| fp32 | 32 | 1 / 8 / 23 | 127 | 3.4 × 10^38 | 1.2 × 10^-38 | 2^-23, about 1.2 × 10^-7 |
| fp16 | 16 | 1 / 5 / 10 | 15 | 65,504 | 6.1 × 10^-5 | 2^-10, about 9.8 × 10^-4 |
| bf16 | 16 | 1 / 8 / 7 | 127 | 3.4 × 10^38 | 1.2 × 10^-38 | 2^-7, about 7.8 × 10^-3 |

The 65,504 is the one Micikevicius et al. give as the largest value fp16 can represent ([Micikevicius et al., 2017](https://arxiv.org/abs/1710.03740)). The rest follow from the layouts. **Machine epsilon** is the gap between 1 and the next value above it, which is 2^-M.

Two consequences matter for the rest of the track. First, fp16 and bf16 both take 2 bytes, so choosing between them changes nothing about memory. It is a choice between three more mantissa bits and three more exponent bits. Second, bf16 is fp32 with the bottom 16 bits removed: the same sign and exponent fields and the top 7 mantissa bits. Kalamkar et al. give this as the reason bf16 is attractive: its range is the same as fp32's and conversion to and from fp32 is simple.

### Range and precision are different things

The exponent sets the **range**, the span from the smallest to the largest value. The mantissa sets the **precision**, how closely the format can approximate a value inside that span. They are independent, and every extra bit in one is a bit taken from the other.

Spacing is not constant. Between 2^k and 2^(k+1) the neighbouring values are 2^(k-M) apart, so the gap doubles at each power of two while the relative gap stays about 2^-M. In fp16, values just above 1 are about 0.001 apart, values just above 1024 are exactly 1 apart, and just above 2048 they are 2 apart. Two things follow. An addition whose result lands closer to an existing value than to a midpoint is rounded back, so `1 + 0.0004` in fp16 is still 1, and a running sum of ones in fp16 stops growing at 2048. And a rounded value is wrong by at most half the local spacing, the **rounding error** that quantization always adds.

### Why fp16 needed loss scaling and bf16 did not

fp16's 5 exponent bits make it narrow. The smallest positive value it can store is 2^-24, and anything smaller becomes zero. Micikevicius et al. measured gradient values from a training run and found about 5% of the weight gradient values had exponents below -24, which would be lost. Their fix is **loss scaling**: multiply the loss by a constant before backpropagation, so every gradient is scaled up into fp16's range, and divide the scale out before the weight update. They choose the factor so that its product with the largest absolute gradient stays under 65,504, because an overflow produces infinities and NaNs that damage the weights.

bf16 has fp32's 8 exponent bits, so the same gradients are representable. Kalamkar et al. state that keeping fp32's range means no hyper-parameter tuning is needed for convergence, and that fp16 does require it. Their emulation zeros the lower 16 bits of an fp32 value, and they compare round-to-nearest with direct truncation when converting. In one of their experiments round-to-nearest matched the fp32 baseline accuracy while truncation lost about 0.02%. The price of bf16 is the 7-bit mantissa: values are only about 0.8% apart in relative terms.

For this track the lesson is the trade itself. Quantized formats at 8 bits and below make the same trade much harder, which is why lesson 4 adds a scale.

## Practice

1. ▢ Which statement correctly compares fp16 and bf16?

    - a) fp16 has more exponent bits, so wider range
    - b) bf16 has more exponent bits, so wider range
    - c) bf16 has more mantissa bits, so finer spacing
    - d) fp16 and bf16 differ in total bit count

<details markdown="1"><summary>Check</summary>

**b)** bf16 spends 8 bits on the exponent against fp16's 5, which gives it fp32's range, and it has 7 mantissa bits against fp16's 10. (a) has the two formats swapped. (c) swaps them the other way: fp16 has the finer spacing. (d) is wrong because both are 16 bits, so memory does not separate them.

</details>

2. ▢ Predict, then run. What does each line print?

    ```python
    import numpy as np

    with np.errstate(over="ignore"):
        print(float(np.float16(65504)), float(np.float16(65519)))
        print(float(np.float16(65520)), float(np.float16(70000)))
    ```

<details markdown="1"><summary>Hint</summary>

65,504 is the largest finite fp16 value, and the next value up would be 65,536. Where is the midpoint, and which way does a number above it round?

</details>

<details markdown="1"><summary>Check</summary>

```text
65504.0 65504.0
inf inf
```

65,519 is below the midpoint between 65,504 and 65,536, so it rounds down to 65,504. From 65,520 upward the value rounds past the largest finite number and becomes infinity, which in training is how a gradient overflow starts. The `errstate` line only silences NumPy's warning about it.

</details>

3. ▢ Predict, then run. Which of the three sums equal 1 exactly?

    ```python
    import numpy as np

    one = np.float16(1)
    for d in (0.0004, 0.0005, 0.001):
        print(d, float(one + np.float16(d)))
    ```

<details markdown="1"><summary>Hint</summary>

The gap above 1 in fp16 is 2^-10, about 0.000977. A sum goes to whichever neighbour is nearer.

</details>

<details markdown="1"><summary>Check</summary>

```text
0.0004 1.0
0.0005 1.0009765625
0.001 1.0009765625
```

Only the first. The neighbours of 1 are 1 and 1.0009765625, and the midpoint is about 1.000488. 0.0004 falls below it and is lost entirely, while 0.0005 jumps up a full 2^-10. A value added to a larger one is not "a little inaccurate": below half the local spacing it vanishes.

</details>

4. ▢ Predict, then run. What does this print, and what does it say about adding up many small numbers in fp16?

    ```python
    import numpy as np

    total = np.float16(0)
    for _ in range(3000):
        total = total + np.float16(1)
    print(float(total))
    ```

<details markdown="1"><summary>Hint</summary>

Above 2048 the fp16 spacing is 2. What happens to 2048 + 1?

</details>

<details markdown="1"><summary>Check</summary>

```text
2048.0
```

At 2048 the spacing is 2, so 2049 sits exactly halfway between two representable values and rounds to the even one, 2048. The sum then stays there for the remaining 952 additions. This is why Micikevicius et al. accumulate fp16 products into fp32 rather than in fp16.

</details>

5. ▢ Predict, then run. bf16 is fp32 with the low 16 bits removed. Before running, say which of the first three values survive the cast unchanged, and what happens to 1e38 in fp16.

    ```python
    import numpy as np

    def to_bf16(x):
        bits = np.asarray(x, dtype=np.float32).view(np.uint32) & np.uint32(0xFFFF0000)
        return bits.view(np.float32)

    x = np.array([1 + 2**-7, 1 + 2**-8, 3.14159265, 1e38], dtype=np.float32)
    print([float(v) for v in to_bf16(x)])
    with np.errstate(over="ignore"):
        print(float(np.float16(1e38)))
    ```

<details markdown="1"><summary>Hint</summary>

bf16 keeps 7 mantissa bits, so 1 + 2^-7 is the first value above 1 it can hold. What is 1 + 2^-8?

</details>

<details markdown="1"><summary>Check</summary>

```text
[1.0078125, 1.0, 3.140625, 9.969209968386869e+37]
inf
```

1 + 2^-7 survives, 1 + 2^-8 truncates to exactly 1, and pi becomes 3.140625, correct to about three digits. 1e38 stays finite, roughly 9.97e37 because the mantissa is cut, but fp16 turns it into infinity. This function truncates, as Kalamkar et al. describe their emulation doing, which they compare against rounding to nearest.

</details>

6. ▢ A teammate trains in fp16 and sees the loss become NaN after a few hundred steps, then proposes switching to bf16. Explain what is likely happening, what loss scaling does about it, and what bf16 would change.

<details markdown="1"><summary>Check</summary>

fp16 tops out at 65,504, so a scaled loss or a large gradient can overflow to infinity and NaN, and small gradients below 2^-24 become zero. Loss scaling picks a constant so gradients land inside fp16's range, and the scale is divided out before the weight update. bf16 has fp32's exponent range, so neither problem arises and no scale is needed, at the cost of a coarser mantissa. Switching is a sound fix only if the NaN really is a range problem. A NaN from a bad learning rate or a bad batch survives the switch.

</details>

## Real-world reps

- [ ] In a Python session with NumPy, print `np.finfo(np.float16)` and `np.finfo(np.float32)` and find `max`, `tiny` and `eps` in them. Match each against the table above.
- [ ] Open the `config.json` of any open model on the Hugging Face Hub and read its `torch_dtype`. Say what range and spacing that choice implies.
- [ ] Tomorrow: without notes, write the sign, exponent and mantissa bit counts of fp32, fp16 and bf16, and say which of the three has the widest range and which the finest spacing.

## Going further

- [Number Formats](../reference/number-formats.md)
- [Paper: "A Study of BFLOAT16 for Deep Learning Training", Kalamkar et al., 2019](https://arxiv.org/abs/1905.12322)
- [Paper: "Mixed Precision Training", Micikevicius et al., 2017](https://arxiv.org/abs/1710.03740), sections 3.1 and 3.2 for the master copy of weights and loss scaling
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
