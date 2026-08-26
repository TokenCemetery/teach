# Lesson 14 — Quantisation from First Principles

**Mission link:** QLoRA is LoRA plus one idea. This lesson is that idea, taught on its own so the next one is short.
**Primary source:** [Paper: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale" — Dettmers et al., arXiv:2208.07339](https://arxiv.org/abs/2208.07339)
**Prerequisites:** [Lesson 5](0005-counting-parameters-and-bytes.md), [quantisation](../GLOSSARY.md)

## Warm-up

1. ▢ Bytes per parameter in fp32, bf16 and 4-bit?

<details markdown="1"><summary>Check</summary>

Four, two, and one half — plus quantisation constants in the 4-bit case, which this lesson explains.

</details>

2. ▢ For a 7B base with a 20M adapter, where does the training memory go?

<details markdown="1"><summary>Check</summary>

14 GB frozen base weights, ~0.3 GB adapter state, and activations that can exceed both. The frozen base is the largest fixed term — and this stage attacks it.

</details>

3. ▢ Why does merging into a quantized base lose quality?

<details markdown="1"><summary>Check</summary>

It requires dequantising, adding the update, and requantising. The requantisation step discards information.

</details>

## Know this

Quantisation stores numbers using fewer bits than they were trained in. Recall from the [glossary](../GLOSSARY.md) that in this workspace it always refers to the **frozen base**, not the adapter.

### The mechanism

To store a high-precision tensor in a small integer type, you need a mapping between the real range and the integer range. Two schemes:

**Symmetric, absmax.** Take the largest absolute value, scale so it lands at the integer maximum.

```text
s = absmax(x) / 127          # for int8
q = round(x / s)             # store q, an int8
x̂ = q · s                    # recover, approximately
```

**Asymmetric, affine.** Also store a zero-point offset, so the range need not be centred on zero.

```text
s = (max(x) − min(x)) / 255
z = round(−min(x) / s)
q = round(x / s) + z
```

Weight distributions in transformers are roughly symmetric and centred near zero, so symmetric absmax is the common choice for weights.

Either way, the error is **rounding error**: each value moves to the nearest representable level. Sixteen levels for 4-bit, 256 for 8-bit.

### The outlier problem

Here is what makes naive quantisation fail on transformers. A single very large value in a tensor sets `absmax`, which sets the scale, which spreads all the representable levels out to cover a range that almost every other value never uses. The typical values then all round into a handful of levels, and most of the tensor's information is destroyed by one outlier.

This is not hypothetical. Transformer activations develop systematic large-magnitude features, and this observation is the core of the LLM.int8() work: a small number of outlier dimensions carry disproportionate importance, and handling them naively destroys quality at scale.

### Blockwise quantisation, the fix

Do not quantise a whole tensor with one scale. Split it into small contiguous **blocks** — 64, 128 or 256 elements — and give each block its own scale.

```text
per-tensor:  one absmax  → one outlier ruins everything
per-block:   one absmax per 64 → one outlier ruins 64 values
```

The damage is contained. This is why blockwise quantisation is standard and per-tensor quantisation is not.

It has a cost, and this cost is the whole subject of the next lesson. Each block needs its scale stored, and that scale is a real number:

```text
4-bit weights, block size 64, fp32 scales:
  weights = 0.5 bytes/param
  scales  = 4 bytes per 64 params = 0.0625 bytes/param
  total   = 0.5625 bytes/param, i.e. 4.5 bits, not 4
```

Twelve percent overhead on top of a 4-bit budget, purely for bookkeeping. Hold that number.

### Storage precision versus compute precision

A quantized weight is not used in its quantized form. The forward pass **dequantises a block back to bf16, does the matmul, and discards the dequantized copy.**

```text
stored:   4-bit + per-block scale
computed: bf16
```

So quantisation buys memory, and costs compute — a dequantisation step per block, per forward pass. Whether the net effect is faster or slower depends entirely on whether you were memory-bound or compute-bound, and on how well the dequantisation kernel is optimised for the hardware you are on.

That last point is where hardware genuinely enters. The *arithmetic* is identical everywhere. What differs by backend is whether a fused, optimised kernel exists for a given bit-width and block size, or whether the library falls back to a slower generic path. Lesson 16 gives the current picture.

### What quantisation is for, here

Two uses that must not be confused:

**Quantisation for inference** shrinks a model so it fits and serves cheaply. The weights are quantized and that is the artifact you ship. This is out of scope for this workspace as a topic in its own right.

**Quantisation for training** — what QLoRA does — shrinks the *frozen base* so that adapter training fits. The adapter stays at higher precision, and the artifact you ship may be merged into a full-precision base afterwards. The base's precision is a training-time budget decision, not a property of the result.

## Practice

1. ▢ Quantise the values `[0.1, −0.3, 0.2, 8.0]` to int8 with symmetric absmax. What happens to the first three?

<details markdown="1"><summary>Check</summary>

`absmax = 8.0`, so `s = 8.0/127 ≈ 0.063`. The values map to `round(0.1/0.063) = 2`, `round(−0.3/0.063) = −5`, `round(0.2/0.063) = 3`, and `127`.

Recovered: 0.126, −0.315, 0.189, 8.0. The small values now carry substantial relative error, because one outlier consumed the range. At 4-bit — sixteen levels — the first three would collapse to nearly the same value.

</details>

2. ▢ Why does blockwise quantisation help, and what does it cost?

<details markdown="1"><summary>Check</summary>

An outlier only sets the scale for its own block, so it damages 64 values instead of the whole tensor.

The cost is storing one scale per block. At block size 64 with fp32 scales, that is 0.0625 bytes per parameter — about 12% overhead on a 4-bit budget.

</details>

3. ▢ Total bytes per parameter for 4-bit weights, block size 128, fp32 scales?

<details markdown="1"><summary>Check</summary>

0.5 + 4/128 = 0.5 + 0.03125 = 0.53125 bytes, or 4.25 bits.

Larger blocks mean less scale overhead and worse outlier containment. That is the trade-off the block size sets.

</details>

4. ▢ In a quantized forward pass, which precision is the matmul done in?

<details markdown="1"><summary>Check</summary>

A higher one — typically bf16. Each block is dequantised to bf16, multiplied, and the dequantized copy discarded.

Quantisation is a *storage* decision. The compute precision is separate and is configured separately.

</details>

5. ▢ Why is transformer quantisation harder than it looks from the arithmetic alone?

<details markdown="1"><summary>Check</summary>

Because of systematic outlier features. A few dimensions carry very large magnitudes and disproportionate importance, so a scheme that treats all values as interchangeable — one scale per tensor — destroys the ordinary values while preserving the outliers.

Blockwise quantisation, and in LLM.int8()'s case separating outlier dimensions into higher precision entirely, is the response.

</details>

6. ▢ Distinguish quantisation for inference from quantisation for training.

<details markdown="1"><summary>Check</summary>

For inference, the quantized weights *are* the artifact — you ship them, and the quality cost is permanent.

For training, quantising the frozen base is a memory budget decision. The adapter stays high-precision, and the shipped result can be merged into a full-precision base, so the quantisation cost need not survive into the artifact at all.

</details>

## Real-world reps

- [ ] Implement absmax int8 quantisation and dequantisation for a tensor by hand in a few lines. Measure the maximum and mean error.
- [ ] Insert one large outlier and measure the error again. Then redo it blockwise with block size 64 and compare.
- [ ] Tomorrow: compute the true bytes-per-parameter for 4-bit with block sizes 32, 64, 128 and 256, and note where the overhead becomes negligible.

## Going further

- [Paper: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale" — Dettmers et al., arXiv:2208.07339](https://arxiv.org/abs/2208.07339)
- [Paper: "8-bit Optimizers via Block-wise Quantization" — Dettmers et al., arXiv:2110.02861](https://arxiv.org/abs/2110.02861)
- [Lesson 15 — NF4 and Double Quantisation](0015-nf4-and-double-quantisation.md)

---

Stuck on any of this, or unsure whether an answer counts? Bring it back to the session — that's what your teacher is for.
