---
title: 17. Defending a Latency Budget End to End
description: A diagnostic order for a missed p99 budget, and the three things a final defended configuration must cite
type: lesson
---

# Lesson 17. Defending a Latency Budget End to End

**Mission link:** This is the mission's final lesson: quoting and defending a p99 latency budget end to end means diagnosing a miss by walking back through cache, batching, and quantization in the right order, and defending the fix with the numbers each of those lessons taught how to measure.
**Primary source:** [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Prerequisites:** [Lesson 16](0016-p99-latency-methodology.md), [Lesson 9](0009-picking-a-quantization-scheme.md), [Lesson 2](0002-capacity-and-batch-size.md), [KV cache](../GLOSSARY.md)

## Warm-up

1. ▢ Write lesson 2's capacity ceiling formula from memory.

<details markdown="1"><summary>Check</summary>

`max concurrent sequences = (total memory − weights − overhead) / (bytes per token × context length)`.

</details>

2. ▢ What three numbers does lesson 9 say a quantization choice needs to be defended with?

<details markdown="1"><summary>Check</summary>

The memory figure that made quantization necessary (or shows it wasn't), the accuracy number measured for the chosen scheme, and the speed number actually measured for the phase that matters.

</details>

## Know this

### Diagnosis follows the phase, then the lever

A missed p99 budget is a symptom, not a diagnosis. The first split is which phase is missing budget: p99 TTFT points at prefill and scheduling (lesson 5's head-of-line blocking, chunked prefill's chunk size), while p99 inter-token latency points at decode (lesson 6's batch size, lesson 3's cache precision, lessons 7 to 9's weight quantization). Checking the wrong phase's levers wastes effort: tuning the chunk size does nothing for a decode-bound ITL problem, and shrinking the batch does nothing for a TTFT problem caused by a large prefill stalling the queue.

Once the phase is identified, the lever order follows cost: the cheapest fix that doesn't cost accuracy comes first (batch size, since lesson 6 already showed how to compute the largest batch a budget allows), then a cache-precision change (lesson 3's fp8 KV cache, which costs no weight accuracy), then weight quantization (lessons 7 to 9, which does cost measured accuracy and should only be reached for once the cheaper levers are exhausted or insufficient).

### A worked chain

A server serving a 13B model on one 80 GB GPU measures, from a realistic 2,000-request benchmark (lesson 16), a p99 TTFT comfortably under budget and a p99 inter-token latency of 80 ms against a 50 ms budget. TTFT being fine rules out lesson 5's scheduling problems; this is a decode-phase, ITL problem. The team checks the batch size first: it's already at the figure lesson 6 would defend for this workload, so shrinking it further would cost throughput the workload needs. Next, they quantize the weights to int8 (lesson 7), which lowers ITL to 65 ms, measuring the accuracy delta against the unquantized model as lesson 9 requires. Still over budget, they weigh two remaining options: drop the batch size further (free of accuracy cost, but costs throughput) or quantize to int4 with AWQ (frees more decode time, at a further, measured accuracy cost). Lesson 9's framework decides it: whichever option closes the remaining gap without paying for more than the budget actually needs. If a smaller batch size still meets the workload's required concurrency, that is the cheaper fix; only if it doesn't does the further accuracy cost of int4 get paid.

### What the final defense has to cite

A configuration that now meets its p99 budget is not yet defended until it names three things: the **measured p99 figures** themselves, from a sample large and realistic enough to be trustworthy (lesson 16); the **memory and batch-size reasoning** behind whatever capacity ceiling and batch size the configuration settled on (lessons 2 and 6); and the **accuracy number** measured for whatever quantization, if any, was applied to get there (lesson 9). A configuration that hits its latency target by luck, with none of these three written down, is exactly as undefended as one that misses it.

## Practice

1. ▢ A server's p99 inter-token latency is 80 ms against a 50 ms budget, while p99 TTFT is comfortably under budget. Name the first two things worth checking, in order, and why in that order.

<details markdown="1"><summary>Check</summary>

First, the batch size against lesson 6's defended figure: ITL is a decode-phase, batch-size-sensitive number, and adjusting batch size costs nothing in accuracy, making it the cheapest lever to check. Second, weight quantization (lessons 7 to 9), since decode is memory-bandwidth bound and a smaller weight footprint reduces per-step latency directly, at a measured accuracy cost that only gets paid once the free lever has been checked. TTFT being fine rules out checking chunked-prefill or scheduling first, since those are lesson 5's TTFT-side levers.

</details>

2. ▢ After quantizing to int8, p99 ITL drops to 65 ms, still above the 50 ms budget. The team is deciding between shrinking the batch size further or quantizing to int4. What does lesson 9's framework say should decide between them?

<details markdown="1"><summary>Check</summary>

Whichever option closes the remaining gap without paying for more than the budget needs. If a smaller batch size still meets the workload's required concurrency and clears the 50 ms budget, that's the better choice, since it costs no further accuracy. Only if a smaller batch can't clear the budget, or can't do so without dropping below the concurrency the workload requires, does the further, measured accuracy cost of int4 become justified.

</details>

3. ▢ The team settles on int8 quantization with a batch size that keeps concurrency where the workload needs it, achieving p99 ITL of 48 ms and p99 TTFT of 210 ms, both measured from 2,000 requests with a prompt-length distribution matching production traffic. What three things does their final defense need to cite?

<details markdown="1"><summary>Check</summary>

The measured p99 figures themselves, from a sample large and realistically shaped enough to trust (lesson 16). The memory and batch-size reasoning behind the chosen configuration, tying the batch size to lesson 2's capacity ceiling and lesson 6's defended figure. The accuracy number measured for the int8 checkpoint against the unquantized model (lesson 9), showing the quantization step was checked, not assumed free.

</details>

4. ▢ Which claim is true of diagnosing a missed p99 latency budget end to end?

   - a) Any flag can be changed at random until the measured number improves
   - b) The diagnostic order follows which phase is missing budget, then which lever that phase's mechanics point to, cheapest first
   - c) A single benchmark run is sufficient evidence to defend a configuration change
   - d) Quantization should always be the first thing tried, regardless of which phase is missing budget

<details markdown="1"><summary>Check</summary>

**b)** Phase first (TTFT versus ITL), then the cheapest lever that phase's mechanics implicate, is the order this lesson's worked chain followed. (a) is false: undirected tinkering isn't diagnosis and wastes effort on the wrong phase's levers. (c) is false: lesson 16 requires enough samples and realistic request-length variance for a p99 to be trustworthy at all. (d) is false: quantization costs measured accuracy and should be reached for after cheaper, accuracy-free levers like batch size, not before checking whether they suffice.

</details>

## Real-world reps

- [ ] For a workload you have in mind, or a real one you're serving, walk this lesson's diagnostic order end to end: identify which phase (if either) is missing budget, check the cheapest lever first, and write down the three things your final defense would need to cite.
- [ ] If you've been building a real deployment across this workspace's lessons, gather its actual measured p99 TTFT and p99 ITL, from a benchmark sized and shaped the way lesson 16 describes, and check them against a latency budget you'd defend.
- [ ] Tomorrow: revisit this workspace's mission in `README.md` and confirm, in your own words, that you can now do what it describes: stand up a serving stack and defend the latency budget it produces.

## Going further

- [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Article: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
