---
title: 8. Accuracy, Speed, and Memory Trade-offs
description: Why memory, speed, and accuracy don't move together when a model is quantized, and how each is actually measured
type: lesson
---

# Lesson 8. Accuracy, Speed, and Memory Trade-offs

**Mission link:** Lesson 7 named the schemes; this lesson is what makes a quantization choice defensible, because memory, speed, and accuracy each move by a different amount and for a different reason when weights get quantized.
**Primary source:** [Paper: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2023](https://arxiv.org/abs/2210.17323)
**Prerequisites:** [Lesson 7](0007-quantization-schemes.md), [KV cache](../GLOSSARY.md)

## Warm-up

1. ▢ Why does quantizing a model's weights speed up decode specifically, rather than inference in general?

<details markdown="1"><summary>Check</summary>

Decode is memory-bandwidth bound: each step reads the weights back from memory, and quantizing them reduces how many bytes that read has to move. The speedup comes from less memory traffic per step, the exact bottleneck decode has.

</details>

2. ▢ Roughly what fraction of fp16 weight memory does int4 quantization use?

<details markdown="1"><summary>Check</summary>

About a quarter, since int4 packs two weights per byte where fp16 used two bytes per weight, an 8x reduction: to a quarter of fp16, then halved again from int8.

</details>

## Know this

### Memory is the most predictable of the three

Memory savings from quantization are close to arithmetic: int8 halves fp16's footprint, int4 quarters it, because the bit width directly sets how many bytes a weight occupies. This is the one axis lesson 7's numbers apply to cleanly, and it holds regardless of which scheme, naive rounding, GPTQ, or AWQ, produced the quantized weights.

### Speed does not follow the same ratio

A quantized weight often has to be **dequantized** back to a higher precision immediately before the actual matrix multiply runs, because the multiply hardware expects that precision. When that dequantization step itself costs time, the wall-clock speedup can fall well short of the memory-savings ratio: a 4x smaller weight does not automatically mean a 4x faster step, only a step with 4x less data to move before whatever overhead dequantizing it adds. Serving stacks close this gap with kernels written to operate on the quantized format directly, but how much of the theoretical memory speedup survives depends on the kernel, not just the bit width.

Speed also does not benefit evenly across a request. Decode, being memory-bandwidth bound, is where a smaller weight footprint pays off: less to read, less time spent reading it. Prefill, being compute-bound (lesson 3), spends its time on the matrix multiply itself, not on reading weights repeatedly, so the same quantization that meaningfully speeds up decode buys prefill much less, sometimes close to nothing.

### Accuracy needs a number, not an impression

A quantized model producing plausible-looking text is not evidence its accuracy held up: fluency is cheap, and a model can read as coherent while still measurably worse than its fp16 original at the task that matters. Accuracy loss from quantization is measured, typically as **perplexity** (how well the model predicts held-out text; higher means worse) on a standard evaluation set, or as the score change on a task-specific benchmark the workload actually cares about. GPTQ's own evaluation reports exactly this: perplexity measured against the unquantized model at each bit width, not a qualitative read of sample outputs.

### The three axes trade off, but not in lockstep

Going from fp16 to int8 typically costs very little measured accuracy for a full halving of memory. Going from int8 to int4 buys another large memory reduction but usually costs disproportionately more accuracy than the int8 step did, which is exactly why GPTQ and AWQ exist: to keep that int4 accuracy cost as small as naive rounding cannot. None of the three axes is free, and none scales with the others in a fixed ratio, which is why a defensible choice needs a number for each, not an assumption that shrinking one shrinks the others by the same amount.

## Practice

1. ▢ A team quantizes a model to int4 and observes it still writes fluent, coherent text on a handful of manual prompts. Is that sufficient evidence the quantization didn't hurt accuracy? Why or why not?

<details markdown="1"><summary>Check</summary>

No. Fluency is not the same as correctness or task accuracy; a model can read as coherent while scoring measurably worse on perplexity or a task benchmark. Accuracy loss needs a measured number, such as perplexity against the unquantized model or a benchmark score delta, not a qualitative read of a few outputs.

</details>

2. ▢ A model is quantized to int4, giving a theoretical 4x memory reduction versus fp16. Why might the measured decode speedup be less than 4x?

<details markdown="1"><summary>Hint</summary>

Think about what has to happen to a quantized weight immediately before the matrix multiply that uses it.

</details>

<details markdown="1"><summary>Check</summary>

The quantized weights often need dequantizing back to a higher precision right before the multiply runs, since the multiply hardware expects that precision. If that dequantization step itself takes time, it eats into the speedup the smaller memory footprint would otherwise buy, so the wall-clock gain can fall short of the memory ratio unless the kernel operates on the quantized format directly.

</details>

3. ▢ The same int4 quantization is applied to a request's prefill phase and its decode phase. Which phase sees the bigger speedup, and why?

<details markdown="1"><summary>Check</summary>

Decode. It is memory-bandwidth bound, so reading a smaller weight footprint directly shortens the step. Prefill is compute-bound: its time is dominated by the matrix multiply itself, not by reading weights, so the same memory reduction buys it much less speedup, sometimes close to none.

</details>

4. ▢ Which claim is true of the accuracy, speed, and memory trade-off when moving from int8 to int4?

   - a) All three improve by the same factor, since both are 8-bit steps down from fp16
   - b) Memory improves predictably, but the speed gain and the accuracy cost don't scale with it in the same ratio
   - c) Speed and memory improve together, and accuracy is unaffected below 8 bits
   - d) Accuracy loss is fixed regardless of bit width, so only memory and speed trade off

<details markdown="1"><summary>Check</summary>

**b)** Memory drops by a predictable, arithmetic ratio, but the wall-clock speedup depends on dequantization overhead and kernel support, and the accuracy cost typically grows faster than it did at the int8 step. (a) is false: int8 to int4 is one step, not two equal 8-bit steps, and the gains are not uniform across axes. (c) is false: int4 accuracy loss is measurable and usually larger than int8's, which is why GPTQ and AWQ exist. (d) is false: accuracy loss generally grows as bit width drops, it is not fixed.

</details>

## Real-world reps

- [ ] Find a published benchmark comparing a model's perplexity or task score at fp16, int8, and int4 (a model card or a paper's evaluation table) and note how much each step actually cost, in the paper's own numbers.
- [ ] Find your serving stack's benchmark or docs page comparing measured throughput at different quantization levels, and compare the reported speedup to the theoretical memory-ratio you'd expect.
- [ ] Tomorrow: for a workload you have in mind, write down what accuracy metric you would actually check before shipping a quantized model, and what score drop you would consider acceptable.

## Going further

- [Paper: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2023](https://arxiv.org/abs/2210.17323)
- [Docs: "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
