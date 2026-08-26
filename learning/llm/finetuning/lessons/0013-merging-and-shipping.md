# Lesson 13 — Merging, Saving and Shipping an Adapter

**Mission link:** An adapter that only exists in a training script is not shipped. This closes stage 3.
**Primary source:** [Docs: LoRA merging — Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
**Prerequisites:** [Lesson 8](0008-the-low-rank-idea.md), [Lesson 12](0012-reading-a-training-run.md)

## Warm-up

1. ▢ Which checkpoint do you ship from an overfitting run?

<details markdown="1"><summary>Check</summary>

The one at the held-out loss minimum, not the final step.

</details>

2. ▢ What can a loss curve never show you?

<details markdown="1"><summary>Check</summary>

Whether generations are usable, and whether capabilities outside your task's distribution have degraded. Both need actual generation against fixed probes.

</details>

3. ▢ Write the LoRA update, with scaling.

<details markdown="1"><summary>Check</summary>

`ΔW = (α/r) · BA`, added to the frozen `W₀`.

</details>

## Know this

### What is in the directory

A saved adapter contains, roughly:

```text
adapter_model.safetensors   # the A and B matrices, nothing else
adapter_config.json         # base model name, r, alpha, target_modules, task_type
README.md                   # generated model card
```

Small — often tens of megabytes. And **incomplete by design**: it is a diff, meaningless without the exact base model named in its config. Losing track of the base, or of which revision of it, makes the adapter garbage.

### Two ways to ship

**Unmerged.** Load the base, apply the adapter at load time.

```python
from transformers import AutoModelForCausalLM
from peft import PeftModel

base = AutoModelForCausalLM.from_pretrained("<base model>", dtype="bfloat16")
model = PeftModel.from_pretrained(base, "runs/first-adapter/final")
```

**Merged.** Fold the update into the weights and discard the adapter structure.

```python
merged = model.merge_and_unload()
merged.save_pretrained("runs/first-adapter/merged")
tokenizer.save_pretrained("runs/first-adapter/merged")
```

Save the tokenizer alongside. A model directory without its tokenizer is a support ticket waiting to happen.

### Choosing between them

| | Unmerged | Merged |
|---|---|---|
| Disk | Base once, adapters in megabytes | A full model copy per task |
| Inference speed | Two extra small matmuls per adapted layer | Identical to the base model |
| Multiple tasks | One base, many adapters, switchable | One full model each |
| Deployment | Serving stack must support adapters | Any stack that loads a model |
| Composability | Adapters can be swapped or weighted at runtime | Fixed at merge time |

The rule of thumb: **merge for a single-purpose deployment, stay unmerged when serving several tasks from one base.** Lesson 25 goes into multi-adapter serving properly.

### Merging is exact — with two exceptions

Because the update is additive and linear, merging is arithmetically exact. `W₀ + (α/r)BA` is the same function the unmerged model computed. There is no approximation and no quality loss.

Except in two cases, both worth knowing:

**Merging into a quantized base is lossy.** If the base is 4-bit, adding a bf16 update requires dequantising, adding, and requantising — and the requantisation step loses information. The correct order is: train against the quantized base, then merge into the *full-precision* base, then quantise the merged result if you need to. Merging directly into the quantized weights degrades quality for no reason. Stage 4 returns to this.

**Dropout changes the effective scale.** `lora_dropout` is active during training and inactive at inference. This is standard dropout behaviour and normally harmless, but it means the merged weight reflects the no-dropout path — which is the correct one.

### Verify the merge

Never assume. Compare outputs:

```python
prompt = "<one of your fixed probes>"
# Greedy decoding, so any difference is the weights and not the sampler.
out_unmerged = unmerged_model.generate(**inputs, do_sample=False, max_new_tokens=64)
out_merged   = merged_model.generate(**inputs, do_sample=False, max_new_tokens=64)
assert tokenizer.decode(out_unmerged[0]) == tokenizer.decode(out_merged[0])
```

Greedy decoding is the point: with sampling on, you cannot tell a merge bug from ordinary randomness. Small numerical differences can still cause a divergence late in a long generation, so compare a modest number of tokens and investigate an *early* divergence rather than a late one.

### Multiple adapters on one base

PEFT can hold several adapters and switch between them, and can combine them with weights:

```python
model.load_adapter("path/to/adapter-a", adapter_name="a")
model.load_adapter("path/to/adapter-b", adapter_name="b")
model.set_adapter("a")                       # use one
model.add_weighted_adapter(["a", "b"], weights=[0.7, 0.3], adapter_name="blend")
```

Weighted combination is a genuinely useful tool and it is not magic: two adapters trained independently on different tasks do not reliably compose into one that does both. It is worth trying and it needs measuring, not assuming. Treat any claim about adapter arithmetic as something to verify on your own task.

### What to record

Everything needed to reproduce and to debug later:

- Base model identifier **and revision**
- Adapter config, verbatim
- Dataset identity and the exact split
- Seed, effective batch size, learning rate, schedule, steps
- Which checkpoint you chose and why — the held-out number that justified it
- Library versions
- Evaluation results, including the regression probes

This is not process for its own sake. Six months from now the question "why is the old adapter better than the new one" is answerable only from records like these.

## Practice

1. ▢ Why is a 40 MB adapter file useless on its own?

<details markdown="1"><summary>Check</summary>

It contains only the `A` and `B` matrices — a diff against a specific set of base weights. Without that exact base model and revision it cannot be applied, and applied to a near-miss base it silently degrades.

</details>

2. ▢ You serve five fine-tuned variants of one base model. Merge or not?

<details markdown="1"><summary>Check</summary>

Do not merge. Unmerged means one copy of the base in memory plus five small adapters, switchable per request. Merged means five full model copies.

The cost is two extra small matmuls per adapted layer and a serving stack that supports adapters.

</details>

3. ▢ You trained against a 4-bit quantized base. Describe the correct merge procedure.

<details markdown="1"><summary>Check</summary>

Load the base in full precision, apply the adapter, merge there, and quantise the merged model afterwards if you need a quantized artifact.

Merging into the quantized weights directly requires dequantise-add-requantise, and the requantisation loses information for no benefit.

</details>

4. ▢ You merge, then compare generations with sampling at temperature 0.8. Outputs differ. What have you learned?

<details markdown="1"><summary>Check</summary>

Nothing. With sampling on, different outputs are expected regardless of whether the merge is correct.

Compare with greedy decoding, where any divergence is attributable to the weights. Then investigate early divergences; a difference appearing only after many tokens can be ordinary numerical drift.

</details>

5. ▢ Which is true of merging an unquantized LoRA?

   - a) It is exact and costs nothing at inference time
   - b) It loses a little quality but speeds up inference
   - c) It is exact but requires more memory at inference
   - d) It is lossy and should be avoided in production use

<details markdown="1"><summary>Check</summary>

**a)** It is exact and costs nothing at inference time.

The update is additive and linear, so it folds into an ordinary weight matrix — same function, same memory, no extra matmuls. This property is what distinguished LoRA from the adapter-layer methods before it.

</details>

6. ▢ You combine a formatting adapter and a domain-knowledge adapter with `add_weighted_adapter` and it underperforms both. Is that surprising?

<details markdown="1"><summary>Check</summary>

No. Independently trained low-rank updates occupy unrelated subspaces, and their weighted sum is not guaranteed to be a good update for either task, let alone both.

It sometimes works well and is worth trying. It is never something to assume — measure it against each adapter alone.

</details>

## Real-world reps

- [ ] Merge your adapter and verify with greedy decoding on your fixed probes. Confirm the outputs match.
- [ ] Compare directory sizes: adapter alone versus merged model. Note the ratio.
- [ ] Write the run record described above, in full, for one real run.
- [ ] Tomorrow: load two adapters onto one base and switch between them for the same prompt. Observe the difference.

## Going further

- [Docs: LoRA merging — Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Docs: Model merging — Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/model_merging)
- [Lesson 25 — Serving Adapters](0025-serving-adapters.md)
- [Failure modes](../reference/failure-modes.md)

---

Stuck on any of this, or unsure whether an answer counts? Bring it back to the session — that's what your teacher is for.
