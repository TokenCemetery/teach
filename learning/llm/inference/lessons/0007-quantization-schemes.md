---
title: 7. Quantization Schemes at Serve Time
description: What int8, int4, GPTQ and AWQ actually do to a model's weights, and why the naive version of low-bit quantization needs a fix
type: lesson
---

# Lesson 7. Quantization Schemes at Serve Time

**Mission link:** Weights, not just the KV cache, sit in memory and get read every decode step; quantizing them is the third lever this workspace covers, alongside batching and the cache itself.
**Primary source:** [Docs: "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
**Prerequisites:** [Lesson 6](0006-throughput-latency-tradeoff.md), [KV cache](../GLOSSARY.md)

## Warm-up

1. ▢ Why is a decode step memory-bandwidth bound rather than compute bound?

<details markdown="1"><summary>Check</summary>

Each decode step computes only one new token, so the amount of new compute per step is small relative to the memory traffic needed to read the weights and the KV cache back.

</details>

2. ▢ Lesson 3 introduced fp8 as a KV cache precision independent of the model's own weight precision. What did halving `bytes_per_value` do to the cache's footprint?

<details markdown="1"><summary>Check</summary>

It halved the cache's per-token size outright, with no change to `num_kv_heads`, context length, or anything about the model itself.

</details>

## Know this

### Weights get read every step too, so quantizing them speeds up decode directly

A 7B model's weights take about 14 GB in fp16 (lesson 1). Every decode step reads all of them back, and since decode is memory-bandwidth bound, the time that takes is close to the actual bottleneck of the step. Quantizing the weights to a lower precision shrinks how many bytes a step has to read, which speeds up decode for the same reason a smaller KV cache does: less memory traffic per step, not less compute.

### The straightforward schemes: int8 and int4

**int8** stores each weight in one byte instead of fp16's two, halving the weight memory outright, with a small and usually tolerable accuracy cost. **int4** goes further, packing two weights per byte, quartering the fp16 footprint. The catch is that naively rounding every weight to the nearest representable 4-bit value (**round-to-nearest quantization**) degrades accuracy more sharply than int8 does, because 4 bits leaves far fewer values to represent a weight's original range. At 8-bit, naive rounding is usually fine. At 4-bit, it usually is not, without something smarter than uniform rounding.

### GPTQ and AWQ are the "something smarter"

**GPTQ** quantizes a model layer by layer, one weight column at a time, and after quantizing each column it adjusts the remaining, not-yet-quantized weights in that layer to compensate for the error just introduced, using second-order information about how sensitive the layer's output is to each weight. That correction step is what lets it reach 3 to 4 bits with far less accuracy loss than naive rounding.

**AWQ** (activation-aware weight quantization) takes a different angle: it observes which weight channels see the largest activation magnitudes during a calibration pass, on the theory that a channel multiplied by large activations contributes more to the layer's output and so is more sensitive to quantization error. It scales those salient channels to protect them from as much quantization error, rather than correcting for error after the fact the way GPTQ does. Both target the same result, an accurate model at 4-bit weights, by different mechanisms: GPTQ compensates error after quantizing each column, AWQ protects the weights most likely to matter before quantizing at all.

## Practice

1. ▢ A model's fp16 weights take 14 GB. Roughly how much memory would int8 and int4 versions of the same weights take?

<details markdown="1"><summary>Check</summary>

int8: about 7 GB, half of fp16. int4: about 3.5 GB, a quarter of fp16.

</details>

2. ▢ Why does quantizing weights from fp16 to int8 speed up decode, given that decode's bottleneck is memory bandwidth, not compute?

<details markdown="1"><summary>Check</summary>

Every decode step reads the weights back from memory. Halving their size halves the memory traffic that step has to do, which directly reduces the time a memory-bandwidth-bound step takes, independent of any change to how much compute the step performs.

</details>

3. ▢ Why does naive round-to-nearest quantization hold up reasonably well at int8 but degrade more sharply at int4?

<details markdown="1"><summary>Hint</summary>

Think about how many distinct values are available to represent a weight's original range at each bit width.

</details>

<details markdown="1"><summary>Check</summary>

int8 has 256 representable values to spread across a weight's range; int4 has only 16. The coarser the available grid, the more each weight's rounding error grows, and at 4 bits that error is large enough to hurt accuracy noticeably without a smarter scheme.

</details>

4. ▢ What is the key difference between how GPTQ and AWQ decide which weights to protect from quantization error?

<details markdown="1"><summary>Check</summary>

GPTQ quantizes column by column and corrects the not-yet-quantized remainder of a layer afterward, compensating for error already introduced. AWQ instead looks at activation magnitudes during a calibration pass beforehand, identifies the weight channels that matter most, and protects those channels from as much error before quantizing, rather than correcting after the fact.

</details>

5. ▢ Which claim is true of GPTQ and AWQ compared to naive round-to-nearest quantization at 4-bit?

   - a) They avoid quantizing the model's weights at all, only its activations
   - b) They use calibration or per-layer correction to preserve more accuracy at the same bit width
   - c) They only work when paired with a lower-precision KV cache
   - d) They reduce the model's memory footprint below what int4 alone achieves

<details markdown="1"><summary>Check</summary>

**b)** Both use extra information, second-order correction for GPTQ, activation-magnitude calibration for AWQ, to preserve accuracy that naive rounding would lose at the same bit width. (a) is false: both quantize the weights themselves. (c) is false: weight quantization and KV cache precision are independent levers, as lesson 3 established. (d) is false: the bit width, and so the memory footprint, is the same 4-bit target; what differs is how much accuracy survives getting there.

</details>

## Real-world reps

- [ ] Find a quantized checkpoint of a model you know (search for "GPTQ" or "AWQ" in its name on a model hub) and read its model card for what bit width and calibration dataset were used.
- [ ] Find your serving stack's flag for loading a quantized model (vLLM supports GPTQ and AWQ checkpoints directly) and read what it says about supported formats.
- [ ] Tomorrow: read one paragraph comparing GPTQ and AWQ's reported accuracy at the same bit width, on a benchmark you can find, and note which one held up better for that specific model.

## Going further

- [Paper: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2023](https://arxiv.org/abs/2210.17323)
- [Docs: "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
