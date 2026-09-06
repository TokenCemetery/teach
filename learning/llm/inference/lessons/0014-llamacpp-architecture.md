---
title: 14. llama.cpp's Architecture
description: The ggml tensor library underneath llama.cpp, its backend abstraction, and how CPU threading differs from GPU batching
type: lesson
---

# Lesson 14. llama.cpp's Architecture

**Mission link:** Standing up llama.cpp (the next lesson) means understanding what's actually running underneath it first: a codebase built to run the same model on a phone's CPU, a laptop's GPU, or a server, which is a different kind of portability than vLLM's GPU-only design ever needed to solve.
**Primary source:** [Repo: llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp)
**Prerequisites:** [Lesson 13](0013-gguf.md), [KV cache](../GLOSSARY.md)

## Warm-up

1. ▢ What does memory-mapping a GGUF file let llama.cpp avoid doing at startup?

<details markdown="1"><summary>Check</summary>

Eagerly reading the entire file into RAM and deserializing it upfront; instead, the OS reads pages from disk only as they're touched, managing what stays resident.

</details>

2. ▢ Why is decode memory-bandwidth bound rather than compute bound?

<details markdown="1"><summary>Check</summary>

Each decode step computes only one new token, so the memory traffic needed to read the weights and cache back dominates the small amount of new compute per step.

</details>

## Know this

### ggml: a tensor library with no dependencies

llama.cpp is built on **ggml**, a C tensor library written to have no external dependencies, not even a full BLAS library is required. A computation, a forward pass through the model, is represented as a static graph of tensor operations, built once and then executed, rather than the operation-by-operation eager execution PyTorch (and so vLLM) uses by default. That graph representation is what lets ggml separate "what computation to run" from "what hardware runs it": the same graph can be handed to different backends without the model-level code changing at all.

### One codebase, many backends

ggml supports multiple **backends**, CPU (using SIMD instructions like AVX2 or NEON depending on the processor), CUDA, Metal, and Vulkan among others, all implementing the same graph interface. This is the architectural reason llama.cpp can run the same GGUF file on a phone's ARM CPU, a Mac's Metal GPU, and a Raspberry Pi, from one codebase with no Python runtime required, where vLLM's design is built around CUDA specifically and cannot run without an NVIDIA GPU at all. Portability across hardware, not raw GPU throughput, is what ggml's architecture optimizes for.

### Threads take the place batching held on a GPU

On a GPU server, lesson 4's batching amortizes memory-bandwidth cost across many concurrent sequences sharing the same GPU. A CPU has no equivalent of thousands of parallel GPU cores to batch requests across; instead, llama.cpp's main lever is **threads**, splitting a single sequence's matrix multiplies across the CPU's own cores. The `--threads` flag controls how many CPU threads are used for this, and the number that helps is bounded by the CPU's physical core count, not by how many concurrent requests are being served the way `--max-num-seqs` was. Threading speeds up one sequence's own compute; it is not the same lever as GPU batching, which spreads memory traffic across multiple sequences at once.

## Practice

1. ▢ Why can ggml run the same model on a phone's CPU, a Mac's Metal GPU, and a Raspberry Pi from one codebase, when vLLM requires an NVIDIA GPU specifically?

<details markdown="1"><summary>Check</summary>

ggml represents a model's computation as a static graph of tensor operations, separate from which backend executes it. Multiple backends (CPU with SIMD, CUDA, Metal, Vulkan) implement the same graph interface, so the model-level code doesn't change across hardware. vLLM's design is built around CUDA specifically, with no equivalent backend abstraction letting it target other hardware.

</details>

2. ▢ What does `--threads` actually control in llama.cpp, and how is that different from what `--max-num-seqs` controls in vLLM?

<details markdown="1"><summary>Hint</summary>

Think about whether each flag is spreading work across concurrent requests or across a CPU's own cores.

</details>

<details markdown="1"><summary>Check</summary>

`--threads` sets how many CPU threads split a single sequence's matrix multiplies across the CPU's own cores, bounded by the physical core count. `--max-num-seqs` instead caps how many concurrent sequences share a GPU batch step, amortizing memory-bandwidth cost across them. One speeds up one sequence's own compute; the other spreads memory traffic across multiple sequences.

</details>

3. ▢ Why does ggml build a static computation graph rather than executing operations eagerly, one at a time, the way PyTorch does by default?

<details markdown="1"><summary>Check</summary>

Building the graph once, separate from execution, is what lets the same graph be handed to different backends (CPU, CUDA, Metal, Vulkan) without changing the model-level code. Eager, operation-by-operation execution ties the computation more tightly to whatever backend is running each operation as it happens.

</details>

4. ▢ Which claim is true of ggml's architecture compared to vLLM's?

   - a) Both require CUDA and cannot run on CPU-only hardware
   - b) ggml separates the computation graph from the backend that executes it, letting one codebase target CPU, CUDA, Metal, and Vulkan
   - c) ggml requires a full BLAS library and a Python runtime to operate
   - d) Threading in llama.cpp serves the same purpose as batching in vLLM

<details markdown="1"><summary>Check</summary>

**b)** That backend abstraction is exactly what lets llama.cpp target diverse hardware from one codebase. (a) is false: vLLM requires CUDA, but ggml explicitly does not. (c) is false: ggml is written to have no external dependencies, not even a full BLAS library, and needs no Python runtime. (d) is false: threading splits one sequence's own compute across CPU cores; batching amortizes memory traffic across multiple concurrent sequences, a different mechanism entirely.

</details>

## Real-world reps

- [ ] Find the list of backends ggml or llama.cpp currently supports in its docs or repository, and note which ones apply to hardware you have access to.
- [ ] Find the `--threads` flag in llama.cpp's docs and read what it recommends setting it to relative to a CPU's physical core count.
- [ ] Tomorrow: read one paragraph on how llama.cpp decides which backend to use when more than one is available on the same machine (for example, a laptop with both a CPU and a Metal GPU).

## Going further

- [Repo: llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp)
- [Docs: "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
