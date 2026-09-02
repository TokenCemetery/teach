---
title: 10. Choosing Target Modules
description: Attention-only is a 2021 ablation, not a default
type: lesson
---

# Lesson 10. Choosing Target Modules

**Mission link:** Target modules matter more than rank, and the received wisdom on them is out of date. This is a place where you can be measurably better than the average practitioner.
**Primary source:** [Docs: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
**Prerequisites:** [Lesson 2](0002-where-the-weights-live.md), [Lesson 9](0009-rank-alpha-and-initialisation.md)

## Warm-up

1. ▢ What does `α/r` control, and what does `r` alone control?

<details markdown="1"><summary>Check</summary>

`α/r` sets the scale of the adapter's contribution. `r` alone sets its capacity: how complex an update it can express.

</details>

2. ▢ Which sublayer holds most of a transformer block's parameters?

<details markdown="1"><summary>Check</summary>

The MLP, roughly 75 to 80% of the block, because the intermediate dimension is several times the hidden size and grouped-query attention shrinks two of the four attention projections.

</details>

3. ▢ What does zero-initialised `B` guarantee?

<details markdown="1"><summary>Check</summary>

That the adapted model is identical to the base model before the first optimizer step.

</details>

## Know this

### What the original paper did, and why that is not advice

The LoRA paper adapted only the attention projections, in its experiments mostly `W_q` and `W_v`, and left the MLP alone. That choice propagated into years of tutorials, and it is where `target_modules=["q_proj", "v_proj"]` comes from.

Two things to understand about it. It was a reasonable finding under a memory budget and on the tasks measured. And it is **not** a general result about where adaptation should happen. Treating a 2021 ablation as a default is the single most common inherited mistake in this field.

### The case for the MLP

From Lesson 2: the MLP holds roughly four fifths of each block's parameters. There is a substantial body of interpretability work treating MLP layers as where much of a model's learned knowledge and feature detection lives, while attention routes information between positions. If your task needs the model to *know* or *classify* something differently, the parameters that encode that are disproportionately in the MLP, and an attention-only adapter cannot reach them.

### The current default

Recent work converges on a blunt recommendation: **adapt all linear layers**, and give the adapter enough rank. The TRL write-up of the "LoRA without regret" result is explicit: applying LoRA to every linear layer, including the MLP, with sufficient rank, closes the gap to full fine-tuning on supervised fine-tuning workloads, while attention-only configurations do not.

```python
from peft import LoraConfig

# The modern default: let the library find every linear layer.
config = LoraConfig(r=64, lora_alpha=128, target_modules="all-linear")

# The explicit equivalent, for a Llama-style architecture.
config = LoraConfig(
    r=64,
    lora_alpha=128,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
)
```

`"all-linear"` is the safer of the two, because it cannot go stale against an architecture whose module names differ from the list you memorised. Its cost is that you give up precise control and should check what it actually matched.

Why this is affordable now: from Lesson 7, adapter parameters are a negligible share of training memory. Restricting target modules to save memory was a real trade in 2021 and is close to a non-trade today. What you are actually trading is overfitting risk on small datasets.

### The decision

| Situation | Targets | Reasoning |
|---|---|---|
| Default for a real task | All linear layers | Best quality per unit of effort; matches current evidence |
| Small dataset (< ~1k examples) | Attention only, low rank | Deliberately limit capacity to limit memorisation |
| Style or tone only | Attention only, low rank | A small behavioural change needs a small update |
| Task needs new discriminations | Must include MLP | Attention-only cannot reach where those live |
| Reproducing a paper | Exactly what the paper used | Otherwise you are not reproducing it |

### Two modules people ask about

**Embeddings and the output head.** Usually left alone. Adapting them is expensive relative to benefit, and it is the one place where changing weights can shift the meaning of every token. The genuine exception is adding new special tokens, which requires touching the embedding table and is a different operation from adapting it.

**Bias terms.** `bias="none"` is the standard setting. Training biases as well ( `"all"` or `"lora_only"`) is cheap but rarely the difference between a working and a failing run, and it complicates merging.

### The check that catches the real error

Print what matched, every time:

```python
model = get_peft_model(base_model, config)
model.print_trainable_parameters()
print([n for n, _ in model.named_parameters() if "lora" in n][:8])
```

A target-module name that matched nothing produces either an error or, depending on version, a model with no adapter at all, which trains, logs a loss, and learns nothing. A trainable-parameter count that disagrees with your Lesson 8 arithmetic is the earliest possible warning.

## Practice

1. ▢ Why did the original paper target attention only, and why is that not a default today?

<details markdown="1"><summary>Check</summary>

It was an ablation under a tight memory budget on the tasks the authors measured, at a time when limiting trainable parameters mattered. It was never a claim that attention is where adaptation belongs.

Today adapter memory is negligible, and the evidence favours covering all linear layers with adequate rank.

</details>

2. ▢ Your task requires the model to distinguish between domain concepts it currently conflates. Attention-only or all-linear?

<details markdown="1"><summary>Check</summary>

All-linear. Making new discriminations means changing feature detection and stored associations, which live disproportionately in the MLP. Attention routes information; it is not where that distinction is encoded.

</details>

3. ▢ You have 400 training examples. Argue for restricting target modules.

<details markdown="1"><summary>Check</summary>

With 400 examples, capacity is the risk rather than the constraint. A full all-linear adapter at generous rank can memorise the set outright: training loss near zero, held-out loss climbing, and no generalisation.

Restricting to attention at low rank is a deliberate capacity limit, which functions as regularisation. The better answer, if available, is more data.

</details>

4. ▢ Which change is most likely to raise quality on a real task with a reasonable dataset?

   - a) Raising the adapter rank from 16 to 64
   - b) Extending targets to all linear layers
   - c) Adding LoRA dropout at 0.05 to the run
   - d) Training for one additional full epoch

<details markdown="1"><summary>Check</summary>

**b)** Extending targets to all linear layers.

It brings roughly four times as many parameters within reach of adaptation, including the MLP. Raising rank adds capacity within the layers you already reach. Dropout regularises rather than improves fit. An extra epoch risks overfitting without adding capacity.

</details>

5. ▢ You set `target_modules=["c_attn"]` and the run trains with loss barely moving. What do you check first?

<details markdown="1"><summary>Check</summary>

Whether `c_attn` exists in this model. It is the fused attention projection in GPT-2-style architectures and does not exist in Llama-style ones, which use separate `q_proj`, `k_proj`, `v_proj`.

Print the module names, then `print_trainable_parameters()`. A near-zero trainable count is the answer.

</details>

6. ▢ Why is `"all-linear"` safer than an explicit module list?

<details markdown="1"><summary>Check</summary>

It resolves against the loaded model rather than against your memory, so it cannot silently miss layers on an architecture whose naming differs.

Its cost is loss of precision, so verify what it matched and note that it may include layers you would rather leave alone.

</details>

## Real-world reps

- [ ] Build an attention-only and an all-linear adapter at the same rank on the same model. Record both trainable-parameter counts and the ratio.
- [ ] Verify which modules `"all-linear"` matched by printing adapter parameter names. Note anything unexpected.
- [ ] Tomorrow: find three fine-tuning configs published online and note which target attention only. Judge whether the author chose that or inherited it.

## Going further

- [Docs: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
- [Blog: "Practical Tips for Finetuning LLMs Using LoRA", Sebastian Raschka](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms): the target-module ablations
- [LoRA hyperparameters](../reference/lora-hyperparameters.md)
- [Lesson 11. Your First Adapter](0011-your-first-adapter.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
