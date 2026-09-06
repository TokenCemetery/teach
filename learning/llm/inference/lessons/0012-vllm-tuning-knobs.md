---
title: 12. The vLLM Tuning Knobs That Matter
description: Two more flags, gpu-memory-utilization and tensor-parallel-size, plus a decision procedure for which knob a symptom actually points at
type: lesson
---

# Lesson 12. The vLLM Tuning Knobs That Matter

**Mission link:** This is the stage 4 capstone: a vLLM stack answering real requests (lesson 10) still needs tuning against whatever symptom a real workload produces, and that means knowing which of this workspace's concepts a given symptom actually points back to.
**Primary source:** [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Prerequisites:** [Lesson 11](0011-pagedattention.md), [Lesson 2](0002-capacity-and-batch-size.md), [KV cache](../GLOSSARY.md)

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

### A flag that changes what "total memory" means

Lesson 2's formula assumes "total memory" is whatever the server has to work with, but vLLM doesn't default to claiming an entire GPU: `--gpu-memory-utilization` sets the fraction of a GPU's memory vLLM is allowed to use for weights, KV cache, and its own overhead, defaulting to about 0.9. On an 80 GB GPU, that default means roughly 72 GB is the "total memory" lesson 2's formula should actually use, not 80 GB. Raising this fraction toward 1.0 gives the cache more room, which raises the capacity ceiling, but leaves less headroom for anything else sharing the GPU (other processes, allocator overhead, a memory spike), trading capacity for safety margin.

### A flag for when the weights themselves don't fit anywhere

Quantization (lessons 7 to 9) is one answer to weights that don't fit; `--tensor-parallel-size` is another, orthogonal one. It splits a model's weights, and the compute over them, across multiple GPUs, so a 70B model whose fp16 weights need 140 GB can run across two 80 GB GPUs (`--tensor-parallel-size 2`) even though neither GPU alone could hold it. This does not shrink the model the way quantization does; it spreads it, and it can be combined with quantization rather than substituted for it, when a single GPU's memory, even after quantizing, still isn't enough.

### A decision procedure: match the symptom to the knob

Tuning a running server is diagnosis, not guessing. Each symptom below points at a specific lesson's concept, not a random flag to try:

- **Server won't start, or reports too little memory for the cache**: check `--gpu-memory-utilization` first; the artificial ceiling it sets may be lower than the GPU's real free memory. If even 100% utilization can't fit the weights, that's lesson 9's memory-constrained case: quantize, add `--tensor-parallel-size`, or both.
- **Decode is slower than the latency budget**: check `--max-num-seqs` against lesson 6's defended batch size, then check whether quantizing the weights (lessons 7 to 9) or the cache (`--kv-cache-dtype`, lesson 3) is what the measured numbers actually justify.
- **One request stalls every other sequence's tokens**: that's lesson 5's head-of-line blocking; check the chunked-prefill chunk size, not the batch size.
- **Memory looks wasted across many parallel samples of the same prompt**: that's lesson 11's block sharing; verify it's actually happening rather than reaching for a batch-size or memory-utilization change first.

## Practice

1. ▢ A server fails to start with "not enough memory for KV cache," even though its 80 GB GPU has only 20 GB of weights loaded. What flag is the first thing to check, and what does raising it trade away?

<details markdown="1"><summary>Hint</summary>

Ask what fraction of the GPU's memory vLLM was actually told it could use.

</details>

<details markdown="1"><summary>Check</summary>

`--gpu-memory-utilization`. At its default of about 0.9, only around 72 GB of the 80 GB is available to vLLM at all, so the cache may be starved by an artificial ceiling rather than a real shortage. Raising it toward 1.0 frees more of the GPU for weights and cache, but leaves less headroom for anything else on that GPU, risking an out-of-memory failure if something else needs memory too.

</details>

2. ▢ A 70B model's fp16 weights (about 140 GB) don't fit on a single 80 GB GPU at all, even before considering any KV cache. Besides quantizing the weights, what other vLLM flag addresses this, and how does it differ from quantization?

<details markdown="1"><summary>Check</summary>

`--tensor-parallel-size`, set to split the model across multiple GPUs (for example, 2 for two 80 GB GPUs). It differs from quantization in mechanism: quantization shrinks the model itself, at an accuracy cost; tensor parallelism spreads the same, unshrunk model's weights and compute across more GPUs' combined memory, with no accuracy cost, at the cost of needing more GPUs.

</details>

3. ▢ A server's decode latency is fine, but one particular request with a very long prompt causes every other in-flight request's next token to arrive late. Which flag from this workspace addresses that symptom, and which one does not?

<details markdown="1"><summary>Check</summary>

The chunked-prefill chunk size addresses it, since this is lesson 5's head-of-line blocking: a large prefill folded into one atomic batch step delays everyone sharing that step. `--max-num-seqs` does not address it; the batch size cap controls how many sequences share a step, not how much of any one sequence's prefill work lands in a single step.

</details>

4. ▢ Which claim is true of `--gpu-memory-utilization` and `--tensor-parallel-size`?

   - a) Both reduce the model's own memory footprint, the way quantization does
   - b) `--gpu-memory-utilization` sets how much of one GPU vLLM may use; `--tensor-parallel-size` spreads the model across multiple GPUs
   - c) `--tensor-parallel-size` is only useful for CPU serving stacks like llama.cpp
   - d) Raising `--gpu-memory-utilization` has no trade-off; it should always be set to 1.0

<details markdown="1"><summary>Check</summary>

**b)** That is exactly what each flag does. (a) is false: neither shrinks the model; one bounds a single GPU's usable fraction, the other spreads the unshrunk model across GPUs. (c) is false: tensor parallelism is a GPU multi-device serving technique. (d) is false: raising it toward 1.0 trades away headroom for anything else that might need memory on that GPU.

</details>

## Real-world reps

- [ ] Find `--gpu-memory-utilization` and `--tensor-parallel-size` in vLLM's docs and read what each one's default value and warnings say.
- [ ] For a model and GPU count you have in mind, work out whether tensor parallelism, quantization, or both would be needed to fit the weights at all, using the plain arithmetic from lesson 1.
- [ ] Tomorrow: if you have a running server, deliberately lower `--gpu-memory-utilization` to something small (like 0.5) and observe what happens to the capacity ceiling or startup behavior.

## Going further

- [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Paper: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
