---
title: 15. Mixed Precision at Scale: bfloat16 and Stochastic Rounding
description: A numeric format with fp32's range but less precision, and what it costs to update parameters in it directly
type: lesson
---

# Lesson 15. Mixed Precision at Scale: bfloat16 and Stochastic Rounding

**Mission link:** "Given a loss curve, can say whether a spike is recoverable or needs a restart from an earlier checkpoint" is the closest Success looks like bullet this stage serves, and it starts with the numeric format the training run is even running in. Lesson 16 covers loss spikes directly; Lesson 17 covers the learning-rate schedule.
**Primary source:** [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Prerequisites:** [Lesson 14](0014-combining-all-three-when-tensor-and-pipeline-parallelism-earn-their-cost.md)

## Warm-up

1. ▢ Per Narayanan et al., why is tensor parallelism best confined within a single node, while pipeline parallelism tolerates being spread across nodes?

<details markdown="1"><summary>Check</summary>

Tensor parallelism needs an expensive all-reduce for every layer, which needs the fastest available interconnect to stay efficient. Pipeline parallelism only passes activations between a handful of stage boundaries, using much cheaper point-to-point communication that does not bottleneck the whole computation even across slower, longer-distance links.

</details>

## Know this

### Two ways to fit a 32-bit number into 16 bits

A 32-bit floating-point number (`fp32`) splits its bits between a range (the exponent) and a precision (the mantissa, the digits after the leading one). Two different 16-bit formats compress this differently. `fp16` keeps 10 mantissa bits but only 5 exponent bits, trading away much of `fp32`'s range for extra precision within a narrower range; a very large or very small gradient can overflow or underflow it. **`bfloat16`** (`bf16`) makes the opposite trade: it keeps `fp32`'s full 8 exponent bits, so it has the same dynamic range, but only 7 mantissa bits, so it is coarser within that range. That wider range is exactly why bf16 tends to be more forgiving during training: the large or tiny values that show up in gradients and activations at scale are less likely to overflow or underflow it in the first place.

### What Gopher actually did with it

Rae et al. describe using bfloat16 specifically to reduce memory and increase training throughput, but they did not apply it uniformly across every model size they trained. Models smaller than 7.1 billion parameters were trained with ordinary mixed precision: `fp32` parameters, `bf16` activations. Their two largest models, the 7.1B model and Gopher itself (280B), went further and used `bf16` for parameters as well as activations, not just activations alone.

### Why parameters in bf16 need special handling

Updating a parameter stored in bf16 directly runs into a problem ordinary mixed-precision training avoids by keeping an `fp32` master copy: bf16's coarser precision means a small update can simply vanish when rounded, if it is smaller than the gap between adjacent representable bf16 values near that parameter's current value. Rae et al. address this with **stochastic rounding**: instead of always rounding a value to its nearest representable bf16 value (which would silently discard small updates in a biased, one-directional way), stochastic rounding rounds up or down with a probability proportional to how close the true value is to each neighbor, so a small update is not lost outright; it is preserved on average across many steps, even though any single step's rounding is randomized. Rae et al. are explicit that this does not fully solve the problem: they report that stochastic rounding does not fully recover the performance of ordinary mixed-precision training, an honest limitation rather than a clean fix.

## Practice

1. ▢ A gradient value during training is unusually large, large enough to be a concern for numeric overflow. Which 16-bit format, fp16 or bf16, is more likely to represent it without overflowing, and why?

<details markdown="1"><summary>Check</summary>

bf16. It keeps the same 8 exponent bits as fp32, giving it the same dynamic range, so a large value that would overflow fp16's narrower 5-bit exponent range is less likely to overflow bf16.

</details>

2. ▢ Why does updating a parameter stored directly in bf16 (rather than keeping an fp32 master copy) risk silently losing small updates?

<details markdown="1"><summary>Check</summary>

bf16 has only 7 mantissa bits, so it is coarse within its range; a small update can be smaller than the gap between adjacent representable bf16 values near the parameter's current value, and rounding to the nearest representable value would simply discard it.

</details>

3. ▢ How does stochastic rounding address this, and what limitation did Rae et al. report even after using it?

<details markdown="1"><summary>Check</summary>

Stochastic rounding rounds up or down with a probability proportional to how close the true value is to each neighboring representable value, rather than always rounding to the nearest one, so a small update is preserved on average across many steps rather than discarded every time. Even so, Rae et al. found it does not fully recover the performance of ordinary mixed-precision training.

</details>

4. ▢ Which of Gopher's model sizes used bf16 for parameters as well as activations, per Rae et al.?

    - a) Every model size they trained
    - b) Only models smaller than 7.1 billion parameters
    - c) Only the 7.1B model and the 280B Gopher model
    - d) None; bf16 was used only for activations across all sizes

<details markdown="1"><summary>Check</summary>

**c)** Only their two largest models. Models smaller than 7.1B used ordinary mixed precision, fp32 parameters with bf16 activations, per (b)'s description, which is why (a) and (d) are both wrong: bf16 activations were used broadly, but bf16 parameters were reserved for the largest two models.

</details>

## Real-world reps

- [ ] Find where a training framework you have access to exposes a choice between fp16 and bf16 (many list both as options for mixed-precision training). Note what the documentation says about when to prefer one over the other, and check it against this lesson's dynamic-range reasoning.
- [ ] Look up the exact bit layout (sign, exponent, mantissa) for fp32, fp16, and bf16, and confirm for yourself that bf16 and fp32 share the same exponent width while fp16 does not.
- [ ] Tomorrow: without looking ahead, write a one-sentence prediction for Lesson 16: given that Gopher's two largest models needed the most careful numeric handling, would you expect loss spikes and instabilities to become more or less common as model size grows, and why?

## Going further

- [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
