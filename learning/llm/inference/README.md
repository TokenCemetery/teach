---
title: Inference
description: "Serve a model: the KV cache, batching, quantization at serve time, and a latency budget you can defend"
type: topic
---

# Learning: Inference

Be able to stand up an inference server for a real model, on GPU and on CPU/edge in turn, and defend the latency and throughput numbers it produces instead of quoting whatever the framework's defaults happen to give you.

**Latest lesson:** [2. Capacity and Batch Size](lessons/0002-capacity-and-batch-size.md)

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

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
