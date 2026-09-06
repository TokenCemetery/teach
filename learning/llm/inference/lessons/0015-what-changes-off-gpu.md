---
title: 15. What Changes Off-GPU
description: Standing up llama.cpp's server, and how batching, cache management, and quantization each look different at CPU/edge scale
type: lesson
---

# Lesson 15. What Changes Off-GPU

**Mission link:** This is the stage 5 capstone and the second half of the mission's success criteria: a llama.cpp stack running on CPU and answering real requests, with every concept from stages 1 to 4 re-examined for what actually still applies at this scale.
**Primary source:** [Repo: llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp)
**Prerequisites:** [Lesson 14](0014-llamacpp-architecture.md), [KV cache](../GLOSSARY.md)

## Warm-up

1. ▢ What does `--threads` control in llama.cpp, and how is that different from vLLM's `--max-num-seqs`?

<details markdown="1"><summary>Check</summary>

`--threads` splits a single sequence's own matrix multiplies across the CPU's physical cores. `--max-num-seqs` instead caps how many concurrent sequences share a GPU batch step, amortizing memory traffic across them. One speeds up one sequence's compute; the other spreads memory bandwidth cost across many.

</details>

2. ▢ Decode the quantization name `Q4_K_M` into its three parts.

<details markdown="1"><summary>Check</summary>

`Q4`: roughly 4 bits per weight. `K`: a k-quant method that mixes precision within a tensor. `M`: the medium preset among that method's size/quality configurations.

</details>

## Know this

### Standing up the server

llama.cpp's own server, `llama-server`, loads a GGUF file and exposes an OpenAI-compatible HTTP endpoint, the same request shape lesson 10 used against vLLM:

```text
llama-server -m model.Q4_K_M.gguf --threads 8
```

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "model.Q4_K_M.gguf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

The request and response shape is familiar. What changes is everything underneath it.

### Batching matters less at this scale

vLLM's continuous batching (lessons 4 and 5) exists to amortize a GPU's memory-bandwidth cost across hundreds of concurrent strangers' requests. A CPU has no equivalent of thousands of parallel cores to spread that cost across; llama.cpp's server does support a handful of parallel request slots, but at a scale of single digits to low tens, not hundreds. This isn't a missing feature: an edge deployment's typical workload, one device serving its own user, rarely has hundreds of concurrent requests to batch in the first place. Heavy batching solves a problem CPU/edge serving usually doesn't have.

### The cache doesn't need paging at this scale either

PagedAttention (lesson 11) exists to let many sequences share memory efficiently and to avoid fragmentation across a large, constantly-changing pool of concurrent requests. At CPU/edge scale, with few concurrent sequences and no large shared pool to fragment, a simpler, contiguous per-sequence cache allocation is common and adequate. The problem PagedAttention solves doesn't disappear in principle, it just rarely reaches the scale where its complexity pays for itself.

### The quantization decision already happened

On vLLM, `--quantization` is a serve-time flag: the scheme gets chosen when the server starts, from an already-quantized checkpoint or one to quantize on load. On llama.cpp, that decision was made earlier, when a GGUF file was picked (or produced) at a specific quant level, such as `Q4_K_M`. There is no serve-time flag to change it; changing quantization means downloading or producing a different GGUF file. The trade-off from lessons 7 to 9, memory against accuracy against speed, still applies, it's just settled before the server ever starts, not configured at startup.

## Practice

1. ▢ Three requests arrive at a `llama-server` instance at the same time, all from a single edge device's own users. Predict, before checking: what happens to each request's throughput, and why does this differ from what continuous batching does on a GPU?

<details markdown="1"><summary>Check</summary>

Each request's throughput drops roughly in proportion to how many threads it now has to share, since the CPU's fixed core count gets split across the concurrent requests rather than each getting the full thread count to itself. This differs from GPU continuous batching, which amortizes an already-necessary memory-bandwidth cost across concurrent sequences at little extra cost per sequence; splitting CPU compute across requests has no equivalent "already paying for it anyway" cost to amortize.

</details>

2. ▢ Why does heavy, vLLM-style continuous batching matter less for a typical CPU/edge deployment than for a GPU server?

<details markdown="1"><summary>Check</summary>

Continuous batching earns its complexity when many concurrent strangers' requests share a GPU's memory-bandwidth cost. A typical edge deployment, one device serving its own user, rarely has that many concurrent requests to batch in the first place, so the problem the mechanism solves usually isn't present at this scale.

</details>

3. ▢ Where did the quantization decision get made for a llama.cpp deployment, compared to where it gets made for a vLLM deployment?

<details markdown="1"><summary>Check</summary>

For llama.cpp, it was made when a specific GGUF file (at a specific quant level, such as `Q4_K_M`) was picked or produced, before the server ever starts; changing it means using a different file. For vLLM, it's a serve-time flag, `--quantization`, chosen when the server is launched. The trade-off itself is the same one lessons 7 to 9 taught; only when the decision gets locked in differs.

</details>

4. ▢ Which claim is true of why PagedAttention-style memory management is less commonly needed at CPU/edge scale?

   - a) CPU hardware makes paging technically impossible
   - b) The typical workload has few enough concurrent sequences that a simpler, contiguous per-sequence cache is adequate
   - c) llama.cpp's GGUF format is incompatible with any form of paged memory
   - d) KV caches don't exist at all in CPU serving

<details markdown="1"><summary>Check</summary>

**b)** With few concurrent sequences and no large shared pool to fragment, a simpler allocation scheme is usually enough; the problem PagedAttention solves rarely reaches the scale where its complexity pays for itself. (a) is false: nothing about CPU hardware rules out paging, it's a design trade-off, not a limitation. (c) is false: GGUF describes the model file, not the runtime's cache layout. (d) is false: decode still needs a KV cache on CPU, for the same reason lesson 1 established; it's just usually managed more simply.

</details>

## Real-world reps

- [ ] Build or install llama.cpp, download a small GGUF model, and run `llama-server` with a thread count matched to your CPU's core count.
- [ ] Send the curl request from this lesson against your running server, and confirm you get a real completion back.
- [ ] Tomorrow: send two or three requests to your running server at the same time and observe, informally, whether each one feels slower than when it's the only request in flight.

## Going further

- [Repo: llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp)
- [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
