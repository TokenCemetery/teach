---
title: Inference
description: "Serve a model: the KV cache, batching, quantization at serve time, and a latency budget you can defend"
type: topic
---

# Learning: Inference

Be able to stand up an inference server for a real model, on GPU and on CPU/edge in turn, and defend the latency and throughput numbers it produces instead of quoting whatever the framework's defaults happen to give you.

**Latest lesson:** [16. p99 Latency Measurement Methodology](lessons/0016-p99-latency-methodology.md)

## Success looks like

- Stand up a serving stack (vLLM on GPU, then llama.cpp on CPU/edge) for a given model and get it answering requests.
- Quote a p99 latency budget for a given batch size and model, and defend the number from the KV cache, batching and quantization choices that produced it.

## Constraints

- Assumes comfort running a Python ML environment and basic familiarity with what a language model is; no prior serving-infrastructure experience required.
- Core stacks: vLLM (GPU) and llama.cpp (CPU/edge), covered in that order. Other stacks (TGI, TensorRT-LLM) are mentioned only where a concept transfers differently.

## Out of scope

- Training or fine-tuning a model or adapter: that is `llm/finetuning`, whose lessons 0025 (serving adapters) and 0026 (cost, latency and throughput) this workspace links back to rather than restates.
- Judging output quality or building an eval for a served model: that is `llm/evals`.

## The arc

Six stages, first request to a defended latency budget. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. The KV cache | 0001 to 0003 | Why autoregressive generation is expensive, what the cache trades memory for, how cache size grows with context and batch | Can compute a model's KV cache memory footprint for a given context length and batch size |
| 2. Batching | 0004 to 0006 | Static vs continuous batching, request scheduling, the throughput/latency trade-off | Can defend a batching configuration for a stated workload |
| 3. Quantization at serve time | 0007 to 0009 | int8/int4/AWQ/GPTQ at inference time, accuracy vs speed vs memory | Can pick a serving-time quantization scheme and defend the trade-off |
| 4. vLLM in practice | 0010 to 0012 | Standing up vLLM, PagedAttention, the tuning knobs that matter | A vLLM stack is running and answering real requests |
| 5. llama.cpp on CPU/edge | 0013 to 0015 | GGUF, llama.cpp's architecture, what changes off-GPU | A llama.cpp stack is running on CPU and answering real requests |
| 6. The latency budget | 0016 to 0017 | p99 measurement methodology, tying the number back to cache, batching and quantization choices | Can quote and defend a p99 latency budget end to end |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-the-kv-cache.md) | The KV Cache | Why generation gets expensive, and what caching buys back |
| [0002](lessons/0002-capacity-and-batch-size.md) | Capacity and Batch Size | How head sharing (GQA/MQA) and batch size change the cache's real footprint |
| [0003](lessons/0003-growth-prefill-decode-precision.md) | Growth, Prefill, Decode, and Precision | How the cache grows across prefill and decode, and what lowering its precision buys back |
| [0004](lessons/0004-static-vs-continuous-batching.md) | Static vs Continuous Batching | Why batching requests together helps throughput, and why continuous batching beats the static kind |
| [0005](lessons/0005-request-scheduling.md) | Request Scheduling | How a continuous-batching scheduler picks the next request, and why a large prefill can stall everyone else |
| [0006](lessons/0006-throughput-latency-tradeoff.md) | The Throughput/Latency Trade-off | How batch size trades throughput against per-token latency, and how to defend a batching configuration against a stated latency budget |
| [0007](lessons/0007-quantization-schemes.md) | Quantization Schemes at Serve Time | What int8, int4, GPTQ and AWQ actually do to a model's weights, and why the naive version of low-bit quantization needs a fix |
| [0008](lessons/0008-accuracy-speed-memory-tradeoffs.md) | Accuracy, Speed, and Memory Trade-offs | Why memory, speed, and accuracy don't move together when a model is quantized, and how each is actually measured |
| [0009](lessons/0009-picking-a-quantization-scheme.md) | Picking and Defending a Quantization Scheme | A decision framework for choosing a serving-time quantization scheme, and the three numbers that defend it |
| [0010](lessons/0010-standing-up-vllm.md) | Standing Up vLLM | Installing vLLM, launching its server, and finding the flags that carry the concepts already taught |
| [0011](lessons/0011-pagedattention.md) | PagedAttention | The block table mechanism behind vLLM, its block-size trade-off, and how it lets sequences share a common prefix's cache |
| [0012](lessons/0012-vllm-tuning-knobs.md) | The vLLM Tuning Knobs That Matter | Two more flags, gpu-memory-utilization and tensor-parallel-size, plus a decision procedure for which knob a symptom actually points at |
| [0013](lessons/0013-gguf.md) | GGUF | What llama.cpp's single-file model format bundles together, its quantization naming, and why it can be memory-mapped instead of loaded |
| [0014](lessons/0014-llamacpp-architecture.md) | llama.cpp's Architecture | The ggml tensor library underneath llama.cpp, its backend abstraction, and how CPU threading differs from GPU batching |
| [0015](lessons/0015-what-changes-off-gpu.md) | What Changes Off-GPU | Standing up llama.cpp's server, and how batching, cache management, and quantization each look different at CPU/edge scale |
| [0016](lessons/0016-p99-latency-methodology.md) | p99 Latency Measurement Methodology | Why p99 beats an average, why TTFT and inter-token latency need separate numbers, and what makes a p99 measurement trustworthy |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
