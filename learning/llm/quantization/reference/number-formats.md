---
title: Number Formats
description: Bit layouts, range and precision of each format, and memory arithmetic
type: reference
---

# Number Formats: Layouts, Range, Precision and Memory

Stage 1 compressed for lookup. [Lesson 1](../lessons/0001-what-quantization-buys.md) covers what quantization buys and the memory arithmetic, [lesson 2](../lessons/0002-floating-point-formats.md) the floating-point formats fp32, fp16 and bf16, and [lesson 3](../lessons/0003-low-bit-formats.md) fp8, int8, int4 and the block-scaled formats.

## Reading a floating-point layout

```text
value = (-1)^sign × 2^(e - bias) × (1 + m / 2^M)
```

- `e` is the exponent field, `m` the mantissa field, `M` the number of mantissa bits.
- Exponent field all zeros: zero and subnormal values, `(m / 2^M) × 2^(1 - bias)`.
- Exponent field all ones: infinity and NaN in IEEE formats. E4M3 is the exception and uses it for ordinary values.
- Exponent bits set the range. Mantissa bits set the precision. Machine epsilon is `2^-M`.
- Between `2^k` and `2^(k+1)` neighbouring values are `2^(k-M)` apart: the gap doubles at every power of two.

## Floating-point formats

|Format|Bits|Sign / exponent / mantissa|Bias|Largest finite|Smallest normal|Machine epsilon|
|---|---|---|---|---|---|---|
|fp32|32|1 / 8 / 23|127|3.4 × 10^38|1.2 × 10^-38|2^-23, about 1.2 × 10^-7|
|fp16|16|1 / 5 / 10|15|65,504|6.1 × 10^-5|2^-10, about 9.8 × 10^-4|
|bf16|16|1 / 8 / 7|127|3.4 × 10^38|1.2 × 10^-38|2^-7, about 7.8 × 10^-3|
|fp8 E4M3|8|1 / 4 / 3|7|448|2^-6|2^-3|
|fp8 E5M2|8|1 / 5 / 2|15|57,344|2^-14|2^-2|
|FP4 E2M1|4|1 / 2 / 1|1|6|1|2^-1|

- fp16 has a smallest subnormal of `2^-24`. Smaller values become zero.
- E4M3 smallest subnormal `2^-9`, E5M2 `2^-16`.
- E4M3 has no infinities and one NaN pattern (S.1111.111). E5M2 follows IEEE with infinities and NaNs.
- bf16 is fp32 with the low 16 bits removed.
- The E4M3, E5M2 and fp16 rows are from the lesson sources. The FP4 E2M1 row is derived from its layout and the bias of 1 used in lesson 3. Machine epsilon for the fp8 and FP4 rows is `2^-M` by the same rule.

## Which format for what

|Format|Seen in|Why|
|---|---|---|
|fp32|Baseline, and accumulation in mixed precision|Wide range and fine spacing, 4 bytes|
|fp16|Mixed-precision training with loss scaling|Fine spacing, narrow range: training needs loss scaling|
|bf16|Training without loss scaling|fp32's range, so no loss scaling, coarse mantissa|
|E4M3|Weights and activations|Finer spacing, range to 448|
|E5M2|Gradients|Wider range, coarse spacing|

## Integer grids

|Format|Levels|Range|Spacing|
|---|---|---|---|
|int8|256|-128 to 127|1 everywhere|
|int4|16|-8 to 7|1 everywhere|

- Values are `scale × integer`. Without a scale an integer grid holds only whole numbers.
- A float grid brings its own range and needs a scale to place it. An integer grid gets its whole range from the scale.
- Values smaller than half a step round to zero, with or without a scale.

## Block-scaled formats

|Format|Block size|Scale|Element|Element bits|Effective bits per weight|
|---|---|---|---|---|---|
|MXFP8|32|E8M0|E4M3 or E5M2|8|8.25|
|MXFP6|32|E8M0|E2M3 or E3M2|6|6.25|
|MXFP4|32|E8M0|E2M1|4|4.25|
|MXINT8|32|E8M0|int8|8|8.25|
|NVFP4|16|E4M3, plus an FP32 scale per tensor|E2M1|4|4.5, per-tensor scalar ignored|

- Each element's value is `X × P`: the shared scale times the stored element.
- E8M0 is an exponent only, so an MX scale is always a power of two. An E4M3 scale in NVFP4 can be a fractional multiple.
- The positive E2M1 values: 0, 0.5, 1, 1.5, 2, 3, 4, 6.
- One large value in a block sets the scale for the whole block and can round its neighbours to zero.
- NVFP4 details are from NVIDIA's own blog post, which is vendor documentation.

## Memory arithmetic

Weight memory in GB is `parameters in billions × effective bits per weight / 8`. Effective bits per weight is the bit width plus the scale bits divided by the group or block size.

|Format|Effective bits|8B model|70B model|
|---|---|---|---|
|fp32|32|32 GB|280 GB|
|fp16 or bf16|16|16 GB|140 GB|
|fp8 or int8|8|8 GB|70 GB|
|MXFP4|4.25|4.25 GB|about 37.2 GB|
|NVFP4|4.5|4.5 GB|about 39.4 GB|
|int4, 16-bit scale per 128|4.125|4.125 GB|about 36.1 GB|
|int4, 16-bit scale per 32|4.5|4.5 GB|about 39.4 GB|

- These are weights only. The KV cache and activations come on top.
- Scale overhead: `scale bits / group size`. A 16-bit scale per 128 weights adds 0.125 bits, and per 32 adds 0.5 bits.
