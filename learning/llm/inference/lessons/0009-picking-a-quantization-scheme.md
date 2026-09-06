---
title: 9. Picking and Defending a Quantization Scheme
description: A decision framework for choosing a serving-time quantization scheme, and the three numbers that defend it
type: lesson
---

# Lesson 9. Picking and Defending a Quantization Scheme

**Mission link:** This is the stage 3 capstone: picking a quantization scheme and defending the trade-off means naming which constraint forced the choice and citing the memory, accuracy, and speed numbers lessons 7 and 8 taught how to find.
**Primary source:** [Docs: "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
**Prerequisites:** [Lesson 8](0008-accuracy-speed-memory-tradeoffs.md), [Lesson 2](0002-capacity-and-batch-size.md), [KV cache](../GLOSSARY.md)

## Warm-up

1. ▢ What is the key difference between how GPTQ and AWQ decide which weights to protect from quantization error?

<details markdown="1"><summary>Check</summary>

GPTQ quantizes column by column and corrects the not-yet-quantized remainder of a layer afterward. AWQ instead calibrates on activation magnitudes beforehand and protects the channels that matter most from error before quantizing.

</details>

2. ▢ Why might a quantized model's measured decode speedup fall short of its memory-savings ratio?

<details markdown="1"><summary>Check</summary>

The quantized weights often need dequantizing back to a higher precision right before the matrix multiply, and that overhead eats into the theoretical speedup unless the kernel operates on the quantized format directly.

</details>

## Know this

### Start by asking whether fp16 already works

Quantization is not a default step; it is a fix for a constraint fp16 fails to meet. If the model's fp16 weights already fit the memory budget and the server already meets its latency budget (lesson 6), quantizing buys nothing the workload needs, at a real, measured cost to accuracy. The first question is not "which scheme," it is "does anything actually need fixing."

### Identify which constraint is binding

When something does need fixing, name what it is, because it decides how far to go:

- **Memory-constrained**: the model's weights, plus the KV cache capacity lesson 2 requires, don't fit the available memory at all. Quantize enough to fit, and no further: int8 first, since it costs the least measured accuracy, and only drop to int4 with GPTQ or AWQ if int8 alone still doesn't leave room for the cache capacity the workload needs.
- **Latency-constrained**: the model fits in memory, but decode is slower than the stated budget allows. Since decode is memory-bandwidth bound, a smaller weight footprint from int8 or int4 can help, but the actual speedup has to be measured (lesson 8), not assumed from the bit width.
- **Accuracy-constrained**: the workload has a benchmark score or perplexity ceiling it cannot cross. This constraint doesn't rule out quantization, but it rules out picking a scheme by memory or speed alone: GPTQ and AWQ hold up differently on different models, so the one that preserves more accuracy has to be measured for this model, not assumed from which paper's numbers looked better in general.

### Defending the choice means citing three numbers, not one

A defensible answer to "why this scheme" names:

1. **The memory figure** that made quantization necessary in the first place, or the one that shows it wasn't (fp16 already fit).
2. **The accuracy number** measured for the chosen scheme at the chosen bit width: a perplexity delta or a benchmark score change against the unquantized model, not an impression from sample outputs.
3. **The speed number** actually measured for the phase the budget cares about, since lesson 8 showed the wall-clock gain does not follow the memory ratio automatically.

A choice defended by only one of these is not defended; it is guessed and got lucky on the axes nobody checked.

## Practice

1. ▢ A team serves a model on a single 80 GB GPU. Its fp16 weights take 70 GB, leaving 10 GB for KV cache and framework overhead. Using lesson 2's reasoning, what problem does this create, and what constraint is binding?

<details markdown="1"><summary>Check</summary>

10 GB of cache headroom supports very few concurrent sequences at any meaningful context length, per lesson 2's capacity formula. This is a memory constraint: the weights alone are crowding out the cache capacity the workload needs.

</details>

2. ▢ The team quantizes those weights to int8, dropping them to about 35 GB. What does this buy back, in terms of lesson 2's capacity ceiling?

<details markdown="1"><summary>Check</summary>

Roughly 45 GB now available for KV cache and overhead instead of 10 GB, which raises the capacity ceiling (the maximum concurrent sequences the cache budget allows) substantially, since that ceiling is computed from whatever memory is left after weights.

</details>

3. ▢ After moving to int8, the team's measured capacity and latency now both meet the workload's targets. Should they proceed to int4 anyway, since it would free even more memory? Why or why not?

<details markdown="1"><summary>Check</summary>

No. Once int8 already satisfies both the capacity and latency constraints, dropping further to int4 buys memory nobody needs at a real, measured accuracy cost that lesson 8 showed grows faster below int8. Quantizing further than the binding constraint requires is the same mistake as quantizing when fp16 already fit: paying an accuracy cost for a target that was already met.

</details>

4. ▢ A colleague defends a quantization choice by saying "int4 with AWQ gives the best memory savings, so that's what we used." What is missing from that defense?

<details markdown="1"><summary>Check</summary>

The other two numbers. Memory savings alone doesn't say whether the constraint that was actually binding needed int4 rather than int8, whether AWQ's accuracy held up for this specific model (measured, not assumed), or whether the decode speedup this workload's latency budget cares about was actually checked. "Best memory savings" defends one axis while leaving the other two unexamined.

</details>

5. ▢ Which claim is true of choosing between int8 and int4 for a latency-constrained workload?

   - a) int4 should always be preferred, since it frees more memory
   - b) The choice should be based on which one's measured speedup, for the phase the budget covers, actually meets the target
   - c) Bit width alone determines the speedup, so the memory ratio can be used directly
   - d) Latency-constrained workloads should never quantize weights, only the KV cache

<details markdown="1"><summary>Check</summary>

**b)** The measured speedup for the relevant phase, decode in most latency-bound cases, is what should decide it, since lesson 8 showed the wall-clock gain does not track the memory ratio automatically. (a) is false: more memory freed than the constraint needs is a cost, not a benefit. (c) is false, for the same reason as (a). (d) is false: weight quantization directly speeds up decode, since decode is memory-bandwidth bound on the weights as well as the cache.

</details>

## Real-world reps

- [ ] For a model and hardware budget you have in mind, work out whether fp16 weights actually fit alongside a KV cache capacity you'd need, using lesson 2's formula, before assuming quantization is necessary.
- [ ] If quantization is necessary, name in writing which constraint (memory, latency, or accuracy) is binding, and what the target number for that constraint is.
- [ ] Tomorrow: find a real serving deployment's documented quantization choice (a model card, a blog post, an engineering write-up) and check whether it cites a memory, accuracy, and speed number, or just one of the three.

## Going further

- [Docs: "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
- [Paper: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2023](https://arxiv.org/abs/2210.17323)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
