# Lesson 25 — Serving Adapters

**Mission link:** "Ship it" is in the mission. An adapter in a directory is not shipped.
**Primary source:** [Docs: LoRA adapters — vLLM](https://docs.vllm.ai/en/latest/features/lora.html)
**Prerequisites:** [Lesson 13](0013-merging-and-shipping.md), [Lesson 24](0024-the-regression-suite.md)

## Warm-up

1. ▢ Which serving choice makes catastrophic forgetting irrelevant?

<details markdown="1"><summary>Check</summary>

Keeping the adapter unmerged and routing only relevant requests through it, leaving the untouched base available for everything else.

</details>

2. ▢ Where should an adapter trained against a quantized base be merged?

<details markdown="1"><summary>Check</summary>

Into the full-precision base, then quantised afterwards if a quantized artifact is needed.

</details>

3. ▢ Why greedy decoding when verifying a merge?

<details markdown="1"><summary>Check</summary>

So any output difference is attributable to weights rather than sampling.

</details>

## Know this

### Three deployment shapes

**Merged model.** One artifact, indistinguishable from any other model. Any serving stack loads it. Zero adapter machinery.

**Unmerged, single adapter.** Base plus adapter applied at load. Adds two small matmuls per adapted layer.

**Unmerged, multiple adapters.** One base in memory, many adapters, selected per request. This is the shape that makes adapters economically interesting and it needs explicit runtime support.

### Choosing

| | Merged | Unmerged, multi-adapter |
|---|---|---|
| Memory for N tasks | N full models | One base + N small adapters |
| Per-request overhead | None | Small, and larger under mixed batching |
| Serving stack | Anything | Must support adapters |
| Switching tasks | Load a different model | Change a request field |
| Adding a task | Deploy another model | Drop in a file |
| Base still available | No | Yes |
| Rollback | Redeploy | Stop routing to that adapter |

Decision rule: **one task and simple operations → merge. Several tasks, or the base still needed → do not merge.**

That last row is underrated. With an unmerged adapter, rolling back a bad fine-tune is a routing change rather than a deployment, and the base model is always there as a fallback.

### How multi-adapter serving works

The naive approach — swap adapter weights between requests — serialises everything and destroys throughput, because batching is where inference efficiency comes from.

Real implementations batch requests using *different* adapters together. The base model computation is shared across the whole batch, since it is identical for everyone, and the adapter contributions are computed per-request with specialised kernels that handle a batch of small heterogeneous matmuls. The S-LoRA work ([arXiv:2311.03285](https://arxiv.org/abs/2311.03285)) is the reference point for serving many adapters concurrently, including keeping inactive adapters in host memory and paging them in.

What this means practically:

- Serving dozens of adapters from one base is a solved problem with real implementations, not a research idea.
- The overhead is small but real, and it grows with how many *distinct* adapters appear in a batch.
- Adapters should share rank and target modules where possible. Heterogeneous shapes are harder to batch efficiently.

In vLLM the shape is roughly: enable LoRA support, register adapters, and name one per request. Check the current flags and the maximum-rank and maximum-adapters limits in the installed version's documentation — this surface changes, and the limits are set at server start.

### Quantisation at serving time, kept separate

A decision independent of everything above, and worth restating because the two get conflated:

- **Training-time quantisation** (stage 4) is a memory budget for the training run.
- **Serving-time quantisation** shrinks the model you deploy, and its quality cost is permanent for every request.

You can train against a 4-bit base and serve in bf16. You can train in bf16 and serve quantized. They are unrelated choices with unrelated trade-offs, and neither implies the other.

If you serve quantized, evaluate the quantized artifact. Evaluating a bf16 model and shipping a 4-bit one means your numbers describe something you did not deploy — which is a surprisingly common mistake.

### Operational essentials

**Version everything.** Base model and revision, adapter, tokenizer, serving stack. A response should be traceable to the exact configuration that produced it.

**Pin the sampling parameters.** Temperature, top-p, max tokens, stop sequences. These change output quality as much as fine-tuning does, and an undocumented default drift will be misdiagnosed as a model regression.

**Log inputs and outputs.** Production traffic is the best source of your next training set and of your next held-out set, because it is drawn from the real distribution rather than the one you imagined. Observe the obvious privacy and retention constraints; the point is to collect deliberately rather than discover later that you did not.

**Monitor the distribution, not just latency.** Input length, output length, refusal rate, schema validity. A drift in input distribution is the leading indicator that your fine-tune's assumptions have expired.

**Keep the base reachable.** Whether as a fallback route, a comparison endpoint, or both. Being able to A/B the base against the fine-tune in production is the strongest evidence available about whether the fine-tune helps.

### Sampling is not a fix

One caution, because it is a common trap. If a fine-tune underperforms, temperature and top-p are not the repair. They change the distribution's shape, not its content. Tuning sampling to compensate for a training problem hides it and makes the next comparison uninterpretable — you no longer know which of two variables produced a difference.

Fix training in training. Pin sampling and leave it alone.

## Practice

1. ▢ Five tasks, one base model. Merged or unmerged, and what does the choice cost?

<details markdown="1"><summary>Check</summary>

Unmerged. One base in memory plus five small adapters, versus five full model copies.

Costs: the serving stack must support adapters, and there is a small per-request overhead that grows with the number of distinct adapters in a batch.

</details>

2. ▢ Why does naive adapter swapping between requests destroy throughput?

<details markdown="1"><summary>Check</summary>

It serialises requests by adapter, preventing the batching that inference efficiency depends on.

Real implementations batch requests with different adapters together, sharing the base computation and computing adapter contributions per-request with specialised kernels.

</details>

3. ▢ You trained against a 4-bit base. Must you serve 4-bit?

<details markdown="1"><summary>Check</summary>

No. Training precision and serving precision are independent. Merge into the full-precision base and serve bf16 if you have the memory.

Training-time quantisation was a budget for the run. It need not follow the artifact into production.

</details>

4. ▢ Your fine-tune underperforms in production. A colleague suggests lowering temperature. Evaluate.

<details markdown="1"><summary>Check</summary>

It may improve outputs, and it does not address the problem. Sampling reshapes the distribution the model produced; it cannot add capability the model lacks.

Worse, it introduces a second changed variable, so the next comparison is uninterpretable. Pin sampling, diagnose training.

</details>

5. ▢ Which advantage of unmerged serving matters most operationally?

   - a) The reduced memory footprint when serving many tasks
   - b) The ability to roll back by changing a routing rule
   - c) The absence of any per-request computational overhead
   - d) The compatibility with every existing inference server

<details markdown="1"><summary>Check</summary>

**b)** The ability to roll back by changing a routing rule.

(a) is real and often the headline reason, but (b) is what you want at two in the morning. (c) is false — unmerged adds small overhead. (d) is backwards; merged is the universally compatible option.

</details>

6. ▢ You evaluated in bf16 and shipped a 4-bit quantized model. What is wrong?

<details markdown="1"><summary>Check</summary>

Your numbers describe a model you did not deploy. Serving-time quantisation carries a permanent quality cost on every request, and it was never measured.

Evaluate the artifact you ship. Always.

</details>

## Real-world reps

- [ ] Serve your adapter through an inference server and get one real completion through the full path.
- [ ] Load two adapters on one base and switch between them by request field. Confirm outputs differ appropriately.
- [ ] Measure latency for merged, unmerged single-adapter, and unmerged multi-adapter. Record the overhead.
- [ ] Tomorrow: write down every version and sampling parameter in your serving path, in one file.

## Going further

- [Docs: LoRA adapters — vLLM](https://docs.vllm.ai/en/latest/features/lora.html)
- [Paper: "S-LoRA: Serving Thousands of Concurrent LoRA Adapters" — Sheng et al., arXiv:2311.03285](https://arxiv.org/abs/2311.03285)
- [Lesson 26 — Cost, Latency and Throughput](0026-cost-latency-and-throughput.md)

---

Stuck on any of this, or unsure whether an answer counts? Bring it back to the session — that's what your teacher is for.
