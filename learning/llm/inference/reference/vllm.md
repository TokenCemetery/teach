---
title: vLLM
description: Standing up vLLM, the flags that carry stages 1-3's concepts, PagedAttention's block table, and a symptom-to-knob decision procedure
type: reference
---

# vLLM

The GPU serving stack. Built for lookup when standing up or tuning a server.

## Standing up a server

```bash
pip install vllm
vllm serve meta-llama/Llama-2-7b-hf
```

Starts an OpenAI-compatible HTTP server on port 8000. A request looks like any OpenAI chat completion call:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "meta-llama/Llama-2-7b-hf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

The `"model"` field in the request has to match the model the server was started with.

## Flags that carry the arithmetic from stages 1-3

| Flag | Carries |
|---|---|
| `--max-num-seqs` | The batch size cap [defended against a latency budget](batching.md#defending-a-configuration) |
| `--kv-cache-dtype` | [Cache precision](kv-cache.md#cache-precision-is-a-lever-independent-of-the-models-own-weights), e.g. `fp8`, independent of the model's own weight precision |
| `--quantization` | The scheme (`gptq`, `awq`, ...) [chosen and defended](quantization-at-serve-time.md) for an already-quantized checkpoint |

Continuous batching and chunked prefill are on by default; there is no flag to turn the basic mechanism off, only ones to tune around it (such as the chunk size). Omitting `--quantization` serves the checkpoint at whatever precision it was saved in, most commonly fp16 or bf16; nothing gets quantized on load.

## PagedAttention

Each sequence's cache is split into fixed-size **blocks** (16 tokens by default); a per-sequence **block table** maps logical token positions to physical block locations, the same idea as an OS page table.

**Block size is a trade-off:**

| Block size | Wasted space in the last, partially-filled block | Block-table bookkeeping |
|---|---|---|
| Larger | More | Less |
| Smaller | Less | More |

**Worked example**: a 40-token sequence at a 16-token block size uses `ceil(40/16) = 3` blocks; the third holds 8 tokens and wastes the other 8 slots.

**Block sharing**: two sequences' block tables can point at the same physical block when the content is identical, most commonly a shared prompt prefix. Parallel sampling and beam search are the clearest cases: every sample's table points at the same prompt blocks until a sample's own generated token diverges, at which point a **copy-on-write** gives only that sample a private copy of the block being modified.

**Worked example**, 10 parallel samples of the same 200-token prompt, 16-token blocks: one copy needs `ceil(200/16) = 13` blocks. Without sharing: `13 × 10 = 130` blocks. With sharing: 13 blocks, until any sample starts diverging.

## Two more tuning knobs

| Flag | What it controls | Trade-off |
|---|---|---|
| `--gpu-memory-utilization` | Fraction of a GPU's memory vLLM may use for weights, cache, and its own overhead (default ~0.9) | Raising it toward 1.0 grows the cache's capacity ceiling but leaves less headroom for anything else sharing the GPU |
| `--tensor-parallel-size` | Splits a model's weights and compute across multiple GPUs | Spreads the model rather than shrinking it (no accuracy cost, unlike quantization); combinable with quantization when neither alone is enough |

`--gpu-memory-utilization` changes what "total memory" means in [the capacity-ceiling formula](kv-cache.md#capacity-budget): on an 80 GB GPU at the ~0.9 default, only ~72 GB, not 80 GB, is what the formula should use.

## Symptom to knob

| Symptom | Check |
|---|---|
| Won't start, or reports too little memory for cache | `--gpu-memory-utilization` first; if it still doesn't fit at 100%, that's [the memory-constrained case](quantization-at-serve-time.md#picking-a-scheme-name-the-binding-constraint-first): quantize, add `--tensor-parallel-size`, or both |
| Decode slower than the latency budget | `--max-num-seqs` against [the defended batch size](batching.md#the-throughputlatency-trade-off), then whether quantizing weights or `--kv-cache-dtype` is justified by measured numbers |
| One request stalls every other sequence's tokens | [Head-of-line blocking](batching.md#admission-order-and-head-of-line-blocking): check the chunked-prefill chunk size, not the batch size |
| Memory looks wasted across parallel samples of the same prompt | Block sharing above: verify it's actually happening before touching batch size or memory utilization |

## Related

- [Lesson 10](../lessons/0010-standing-up-vllm.md), [Lesson 11](../lessons/0011-pagedattention.md), [Lesson 12](../lessons/0012-vllm-tuning-knobs.md)
- [KV cache](kv-cache.md), [Batching](batching.md), [Quantization at Serve Time](quantization-at-serve-time.md): the concepts these flags carry
