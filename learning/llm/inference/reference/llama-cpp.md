---
title: llama.cpp
description: GGUF's format and quantization naming, ggml's backend abstraction, and what changes when serving moves off-GPU
type: reference
---

# llama.cpp

The CPU/edge serving stack. Built for lookup when standing up or reasoning about a llama.cpp deployment.

## GGUF

A single binary file bundling weights, tokenizer, and architecture metadata, in place of the several separate files (`config.json`, tokenizer, weights) a Hugging Face checkpoint ships as. The bundling matters most for edge deployment: shipping one file to run with a small, dependency-light binary, with no Python or Hugging Face ecosystem installed to reassemble the pieces.

Because GGUF lays weights out in a format the OS can read directly, llama.cpp can **memory-map** the file (`mmap`) instead of eagerly reading it into RAM and deserializing it. Pages are read from disk only as something touches them, and the OS's own page cache manages what stays resident. This matters most where RAM is the tightest resource, CPU and edge hardware, less on a GPU server with generous system RAM.

### Quantization naming

GGUF carries llama.cpp's own quantization family, separate from GPU-oriented GPTQ and AWQ. Decoding a name like `Q4_K_M`:

| Part | Meaning |
|---|---|
| `Q4` | Bit width: roughly 4 bits per weight (also `Q5`, `Q8`, and others) |
| `K` | A **k-quant** method: mixes precision within a tensor rather than quantizing every weight uniformly, spending more bits where it matters more |
| `M` | The preset among that method's size/quality configurations: `S` (small), `M` (medium), `L` (large) |

## ggml: one codebase, many backends

llama.cpp is built on **ggml**, a dependency-free C tensor library (no external BLAS required). A forward pass is a static computation graph, built once and then executed, rather than PyTorch's operation-by-operation eager execution. That separation of "what to compute" from "what runs it" is what lets the same graph target multiple **backends**, CPU (AVX2/NEON), CUDA, Metal, Vulkan, from one codebase with no Python runtime, on hardware from a phone's ARM CPU to a Mac's Metal GPU to a Raspberry Pi. vLLM's design, by contrast, is CUDA-specific and cannot run without an NVIDIA GPU.

## Threads replace GPU batching

| | Spreads | Bounded by |
|---|---|---|
| GPU batching (`--max-num-seqs`) | Memory-bandwidth cost across concurrent sequences | Cache capacity and the latency budget |
| CPU threads (`--threads`) | One sequence's own matrix multiplies across cores | The CPU's physical core count |

Threading speeds up one sequence's own compute; it has no equivalent of "already paying for the memory read anyway" to amortize across strangers' requests the way GPU batching does.

## Standing up the server

```text
llama-server -m model.Q4_K_M.gguf --threads 8
```

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "model.Q4_K_M.gguf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

Same OpenAI-compatible request shape as [vLLM](vllm.md); what changes is everything underneath it.

## What changes off-GPU

| Mechanism | On a GPU (vLLM) | At CPU/edge scale (llama.cpp) |
|---|---|---|
| Concurrency | [Continuous batching](batching.md) amortizes memory bandwidth across hundreds of concurrent strangers' requests | A handful of parallel slots (single digits to low tens); a typical edge workload, one device serving its own user, rarely has hundreds of concurrent requests to batch |
| Cache management | [PagedAttention](vllm.md#pagedattention) manages a large, constantly-changing shared pool | A simpler, contiguous per-sequence cache is adequate; the problem PagedAttention solves rarely reaches the scale where its complexity pays off |
| Quantization timing | A serve-time flag (`--quantization`), chosen at launch | Already locked in when a specific GGUF quant level was picked or produced; changing it means using a different file, not a flag |

The trade-offs themselves ([memory, speed, and accuracy](quantization-at-serve-time.md)) are unchanged; only when each decision gets made, and at what concurrency it pays off, differs.

## Related

- [Lesson 13](../lessons/0013-gguf.md), [Lesson 14](../lessons/0014-llamacpp-architecture.md), [Lesson 15](../lessons/0015-what-changes-off-gpu.md)
- [vLLM](vllm.md), [Batching](batching.md), [Quantization at Serve Time](quantization-at-serve-time.md): the GPU-side mechanisms this sheet contrasts against
