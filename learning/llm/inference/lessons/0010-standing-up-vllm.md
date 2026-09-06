---
title: 10. Standing Up vLLM
description: Installing vLLM, launching its server, and finding the flags that carry the concepts already taught
type: lesson
---

# Lesson 10. Standing Up vLLM

**Mission link:** Every formula from stages 1 to 3, the cache footprint, the batch size, the quantization scheme, becomes a real flag on a real command in this lesson; this is where the arithmetic turns into a server answering requests.
**Primary source:** [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Prerequisites:** [Lesson 9](0009-picking-a-quantization-scheme.md), [KV cache](../GLOSSARY.md)

## Warm-up

1. ▢ A server is above its latency budget at the current batch size. Which flag, from lesson 6's reasoning, is the first one to check?

<details markdown="1"><summary>Check</summary>

The maximum batch size setting: the largest batch size that still satisfies the latency budget is what lesson 6 defended, so that is the knob that directly controls it.

</details>

2. ▢ Why would a serving-time choice to use fp8 for the KV cache, rather than the model's own weight precision, ever make sense (lesson 3)?

<details markdown="1"><summary>Check</summary>

Cache precision is a lever independent of the model's own weight precision. Halving the cache's `bytes_per_value` halves its footprint outright, with no change to the model itself, buying back capacity the same way a smaller model would.

</details>

## Know this

### Installing vLLM

vLLM installs as a Python package, `pip install vllm`, and requires a CUDA-capable GPU; it is the GPU half of this workspace's mission, with llama.cpp covering CPU and edge in the stage that follows. The install pulls in a matching PyTorch and CUDA toolchain automatically for common configurations, which is worth checking against the installed CUDA driver version before assuming a failed install is something else.

### Launching the server

`vllm serve <model>` starts an OpenAI-compatible HTTP server for the named model (a local path or a Hugging Face Hub identifier), listening on port 8000 by default:

```text
vllm serve meta-llama/Llama-2-7b-hf
```

This single command does the download (if needed), the weight loading, and the server startup that everything in stages 1 to 3 was reasoning about the memory and latency consequences of.

### Sending a request

Because the server speaks the OpenAI API shape, a request looks like any OpenAI chat completion call, aimed at the local server instead:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "meta-llama/Llama-2-7b-hf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

### Where the concepts already taught show up as flags

The command line is where stages 1 to 3 stop being arithmetic and become configuration:

- `--max-num-seqs`: the batch size cap lesson 6 taught how to defend against a latency budget.
- `--kv-cache-dtype`: the cache precision lesson 3 introduced as a lever independent of the model's own weights (for example, `fp8`).
- `--quantization`: names the scheme, such as `gptq` or `awq`, that lessons 7 to 9 taught how to choose and defend, when serving an already-quantized checkpoint.
- Continuous batching and chunked prefill (lessons 4 and 5) are on by default; there is no flag to turn the basic mechanism off, only ones to tune around it, such as the chunk size.

## Practice

1. ▢ A team runs `vllm serve some-model --max-num-seqs 32 --kv-cache-dtype fp8`. In terms of lessons 6 and 3, what does each of these two flags actually control?

<details markdown="1"><summary>Check</summary>

`--max-num-seqs 32` caps the batch size at 32, the number lesson 6 would defend against a stated latency budget and lesson 2's capacity ceiling. `--kv-cache-dtype fp8` stores the KV cache in fp8 instead of the default, halving its per-token footprint independent of the model's own weight precision, exactly the lever lesson 3 described.

</details>

2. ▢ A team starts a server with `vllm serve some-model`, naming no `--quantization` flag at all. What precision does the server serve the model at, and why?

<details markdown="1"><summary>Check</summary>

Whatever precision the checkpoint itself was saved in, most commonly fp16 or bf16, since no quantization scheme was requested. `--quantization` only applies when serving a checkpoint that was quantized ahead of time or that the flag tells vLLM to quantize on load; omitting it means nothing is quantized.

</details>

3. ▢ Predict, before checking: after running `vllm serve` successfully, what single piece of information from the curl request in this lesson's Know this section has to match something the server was actually started with, or the request will fail?

<details markdown="1"><summary>Hint</summary>

Look at the `"model"` field in the curl command.

</details>

<details markdown="1"><summary>Check</summary>

The `"model"` field in the request body has to match the model name (or path) the server was started with. The server is serving one model at a time; naming a different one in the request is what most commonly produces an error on an otherwise-correctly-formed call.

</details>

4. ▢ Which claim is true of vLLM's default behavior when no batching or cache flags are given?

   - a) It falls back to static batching until `--max-num-seqs` is set
   - b) Continuous batching and chunked prefill run by default; the flags only tune them further
   - c) It refuses to start until a KV cache dtype is explicitly chosen
   - d) It serves at the lowest precision the hardware supports by default

<details markdown="1"><summary>Check</summary>

**b)** Continuous batching and chunked prefill are the default mechanism, not something a flag turns on; the available flags tune parameters around them, like the maximum batch size or a chunk size. (a) is false: there is no static-batching fallback. (c) is false: a default cache dtype is used if none is named. (d) is false: the default is the checkpoint's own saved precision, not the lowest the hardware supports.

</details>

## Real-world reps

- [ ] Install vLLM (`pip install vllm`) on a machine with a CUDA-capable GPU, and run `vllm serve` with a small model you can afford to download.
- [ ] Send the curl request from this lesson against your running server, and confirm you get a real completion back, not an error.
- [ ] Tomorrow: restart the server with `--max-num-seqs` set to a small number (like 2) and to a large one, and see whether you can observe a difference in how it behaves under a few concurrent requests.

## Going further

- [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
