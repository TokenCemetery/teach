---
title: Inference
description: "Serve a model: the KV cache, batching, quantization at serve time, and a latency budget you can defend"
type: topic
---

# Learning: Inference

Be able to stand up an inference server for a real model, on GPU and on CPU/edge in turn, and defend the latency and throughput numbers it produces instead of quoting whatever the framework's defaults happen to give you.

**Latest lesson:** _none yet_

## Success looks like

- Stand up a serving stack (vLLM on GPU, then llama.cpp on CPU/edge) for a given model and get it answering requests.
- Quote a p99 latency budget for a given batch size and model, and defend the number from the KV cache, batching and quantization choices that produced it.

## Constraints

- Core stacks: vLLM (GPU) and llama.cpp (CPU/edge), covered in that order. Other stacks (TGI, TensorRT-LLM) are mentioned only where a concept transfers differently.

## Out of scope

- Training or fine-tuning a model or adapter: that is `llm/finetuning`, whose lessons 0025 (serving adapters) and 0026 (cost, latency and throughput) this workspace links back to rather than restates.
- Judging output quality or building an eval for a served model: that is `llm/evals`.

## The arc

{N} stages, {start} to {end}. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
|---|---|---|
| 1. {Name} | {What it covers} | {The capability that closes the stage} |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| _none yet_ | | |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
