---
title: Resources
description: "Trusted sources for inference"
type: resources
---

# Inference Resources

## Knowledge

- [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
  Official docs for the GPU serving stack this workspace stands up first: install, serve, and the engine's batching and memory settings. Use for: how to run and configure vLLM itself.
- [Paper: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
  The PagedAttention paper: why the KV cache fragments ordinary memory allocators and how paging it fixes that, with the throughput numbers that motivate vLLM's design. Use for: understanding what the KV cache costs and why vLLM's memory manager exists.
- [Repo: llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp)
  Official repo for the CPU/edge serving stack this workspace stands up second: build instructions, supported quantization formats (GGUF), and the server binary's flags. Use for: how to run and configure llama.cpp itself.
- [Paper: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2023](https://arxiv.org/abs/2210.17323)
  One-shot post-training weight quantization down to 3-4 bits with a measured accuracy cost. Use for: what quantizing a model for serving actually trades away, and how the trade is measured.
  Read the [transformers guide](https://huggingface.co/docs/transformers/main/en/llm_optims) below first if the linear algebra here is the sticking point.
- [Docs: "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
  Practitioner-level walkthrough of the KV cache, static vs dynamic batching, and quantization backends, without requiring the paper math first. Use for: a working mental model before the primary sources above.
- [Article: "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
  Derives the actual FLOP and memory-bandwidth arithmetic behind a forward pass, including where the KV cache's memory cost comes from. Use for: computing a latency or memory budget from first principles rather than quoting a benchmark.
- [Article: "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
  Written by engineers who built continuous batching into an early serving engine; explains why static batching wastes GPU time on a mixed-length request stream and how continuous batching fixes it. Use for: the batching half of the latency/throughput trade this workspace defends.

## Gaps

- No source yet on quantization-aware serving specifically for llama.cpp's GGUF formats (as opposed to GPTQ/AWQ, which target GPU stacks); the mission needs a CPU/edge-specific quantization comparison once lesson design reaches that stage.
