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

- [Paper: "Fast Inference from Transformers via Speculative Decoding", Leviathan et al., 2022](https://arxiv.org/abs/2211.17192)
  Introduces speculative decoding: a small model drafts several tokens, the large model verifies them all in one parallel pass, with a sampling method that guarantees the exact same output distribution as running the large model alone. Use for: why this is a pure latency lever, not a quality trade-off, and the memory-bandwidth argument for why parallel verification is nearly free.
- [Paper: "Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads", Cai et al., 2024](https://arxiv.org/abs/2401.10774)
  Replaces speculative decoding's separate draft model with extra decoding heads added directly to the target model. Use for: solving the operational burden of maintaining a second model, while keeping the same verify-and-correct guarantee.
- [Paper: "EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty", Li et al., 2024](https://arxiv.org/abs/2401.15077)
  Drafts at the level of the model's internal features rather than raw tokens, resolving feature-level prediction uncertainty by incorporating a one-step-ahead token sequence. Use for: a further refinement over Medusa, with a larger reported speedup while still preserving the target model's output distribution.
- [Paper: "Efficient Guided Generation for Large Language Models" (Outlines), Willard and Louf, 2023](https://arxiv.org/abs/2307.09702)
  Reframes constrained generation as transitions between finite-state-machine states, letting a vocabulary index be precomputed once per grammar and reused as a fast per-token lookup. Use for: why grammar- or schema-constrained decoding adds little per-token overhead and guarantees output structure by construction rather than by hope.
- [Docs: "Automatic Prefix Caching", vLLM Project](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html)
  vLLM's own documentation for reusing a shared prefix's KV cache across otherwise unrelated requests, its two named example workloads (long-document QA, multi-round conversation), and its stated limit (speeds up prefill only, never decode). Use for: prefix caching as PagedAttention's block-sharing mechanism extended across requests.

## Gaps

- No source yet on quantization-aware serving specifically for llama.cpp's GGUF formats (as opposed to GPTQ/AWQ, which target GPU stacks); the mission needs a CPU/edge-specific quantization comparison once lesson design reaches that stage.
