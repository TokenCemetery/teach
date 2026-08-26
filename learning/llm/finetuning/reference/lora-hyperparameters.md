# LoRA Hyperparameters

Decision sheet. Read the installed library version for exact parameter names — this surface changes between releases.

## The equation

```text
h = W₀x + (α/r) · BAx
```

`A` random, `B` zero, so `ΔW = 0` at step 0 and the model starts identical to the base.

## Rank

Capacity. Bounds how complex an update the adapter can express.

| Rank | Suits |
|---|---|
| 4–8 | Style, tone, output format; small datasets |
| 16–32 | A real task, a few thousand examples |
| 64–128 | Harder tasks, larger data, reasoning-heavy behaviour |
| 256+ | Approaching full fine-tuning capacity on large SFT data |

Rank costs almost no memory. Its real cost is overfitting risk on small data.

## Alpha

**Only `α/r` matters.** Convention is `α = 2r`.

| `r` | `α` | `α/r` | |
|---|---|---|---|
| 8 | 16 | 2.0 | baseline |
| 16 | 32 | 2.0 | more capacity, same scale |
| 16 | 16 | 1.0 | weaker update |
| 64 | 16 | 0.25 | **trap** — capacity up, influence down 8× |

Raising `r` without raising `α` turns the adapter *down*. At rank ≥ 64 consider `use_rslora=True`, which uses `α/√r`.

## Target modules

| Situation | Targets |
|---|---|
| Default for a real task | all linear |
| Small dataset (< ~1k) | attention only, low rank |
| Style or tone only | attention only, low rank |
| Needs new discriminations | must include MLP |
| Reproducing a paper | exactly theirs |

`"all-linear"` resolves against the loaded model, so it cannot go stale against unfamiliar naming. Attention-only is a 2021 ablation, not a default.

Typical names — **verify with `named_modules()`**:

```text
attention: q_proj  k_proj  v_proj  o_proj
mlp:       gate_proj  up_proj  down_proj
```

## Learning rate

| Method | Range |
|---|---|
| Adapter fine-tuning | `1e-4` to `2e-4` |
| Full fine-tuning | `1e-5` to `5e-5` |

Importing a full fine-tuning rate into an adapter run is a leading cause of a disappointing first result. Use warm-up (a few hundred steps) and cosine decay.

## Other settings

| Setting | Default | Notes |
|---|---|---|
| `lora_dropout` | 0.0–0.05 | Raise only if held-out loss is rising |
| `bias` | `"none"` | Rarely decisive; complicates merging |
| Epochs | 2–3 | On small instruction data; more usually memorises |
| Gradient checkpointing | on | Nearly a default for adapters |
| `use_cache` | off in training | Conflicts with checkpointing; useless for training |

## Variants, by axis

| Axis | Method | Helps when |
|---|---|---|
| Scaling | rsLoRA | High rank |
| Learning rates | LoRA+ | Separate rates for `A` and `B` |
| Init | PiSSA, OLoRA | Faster convergence; gives up zero-init |
| Init | LoftQ | Training against a quantized base |
| Structure | DoRA | Rank pinned low for another reason |
| Structure | AdaLoRA | Layers need unequal rank |
| Structure | VeRA | Adapter size is the binding constraint |

**Baseline to beat:** all-linear, adequate rank, tuned learning rate. Most variants do not clear it by more than seed noise.

## Quantized base (QLoRA)

```python
BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",             # not "fp4"
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,  # do not leave at default
)
```

Then `prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)` — skipping it gives unstable runs or opaque gradient errors.

Every other hyperparameter is unchanged. **QLoRA is LoRA with a cheaper base.**

Merge into the **full-precision** base, never the quantized one.

## Diagnosis by curve

| Train | Held-out | Diagnosis | Action |
|---|---|---|---|
| ↓ | ↓ | Learning | Continue |
| ↓ | ↑ after a dip | Overfitting | Ship the minimum; less capacity or more data |
| → high | → high | Underfitting | More rank, more targets, higher LR |
| Flat from step 1 | Flat | Broken | Check the adapter attached and labels are not all `-100` |
| `NaN` | — | Overflow | Lower LR; add warm-up; prefer bf16 |

## Related

- [Lesson 9](../lessons/0009-rank-alpha-and-initialisation.md), [Lesson 10](../lessons/0010-choosing-target-modules.md), [Lesson 19](../lessons/0019-when-dora-wins.md), [Lesson 20](../lessons/0020-judging-a-new-variant.md)
