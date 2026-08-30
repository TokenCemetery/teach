---
title: Failure Modes
description: Symptom to cause, and the silent failures
type: reference
---

# Failure Modes

Diagnostic sheet. Keep it open during a run.

## The four checks, before anything else

```python
# 1. Did the adapter attach?
model.print_trainable_parameters()          # compare to your arithmetic

# 2. Is the data what you think?
print(repr(tokenizer.decode(ds[0]["input_ids"])))
print(sum(1 for l in ds[0]["labels"] if l != -100), "of", len(ds[0]["labels"]), "scored")

# 3. Does loss move?                        # logging_steps=1 over 50 steps

# 4. Can it overfit two examples?           # loss → ~0 in 100 steps, or the pipeline is broken
```

Check 2 catches template mismatch, missing end-of-turn tokens, masking bugs and truncation in one read. It is the highest-value ten seconds in the process.

## Symptom → cause

| Symptom | Likely cause | Check |
|---|---|---|
| Loss exactly flat from step 1 | Adapter matched nothing | `print_trainable_parameters()` |
| Loss exactly flat from step 1 | All labels `-100` | Count scored positions |
| Loss exactly flat from step 1 | LR orders of magnitude too low | Should be ~`1e-4` |
| Loss barely moves | Target module names wrong for this architecture | `named_modules()` |
| Loss barely moves | `α/r` accidentally tiny | Raised `r`, forgot `α` |
| Loss plateaus high | Capacity ceiling | More rank or more targets — not more epochs |
| Held-out rises, train falls | Overfitting | Ship the held-out minimum |
| Train → 0 fast, held-out rises at once | Dataset far too small for capacity | More data, less capacity |
| Loss staircases at epoch boundaries | Memorisation | Fewer epochs |
| Loss spikes then recovers | One pathological batch | Find the outlier example |
| Loss → `NaN` | Overflow, or bad data | Prefer bf16; lower LR; add warm-up |
| Held-out suspiciously good | Contamination across the split | Dedup train vs test, read top-similarity pairs |
| Model never stops generating | No end-of-turn token in training data | Decode an example |
| Output ignores requested format | Template mismatch train vs serve | Compare with `repr` |
| Answers cut off mid-sentence | `max_length` truncating targets | Check the length distribution |
| Answers to questions not asked | Packing broke loss masking or boundaries | Verify `-100` survives packing |
| Worse at unrelated things | Catastrophic forgetting | Regression suite vs stored baseline |
| No longer refuses what base refused | Safety regression | **Blocks the ship** |
| Merged ≠ unmerged output | Merge bug, or sampling was on | Re-verify greedily |
| Merged model degraded | Merged into a quantized base | Merge into full precision, then quantise |
| Adapter will not load | Wrong base model or revision | An adapter is a diff; it needs its exact base |
| Gradient errors on a 4-bit base | Skipped `prepare_model_for_kbit_training` | Add it |
| Great eval, bad production | Train/serve distribution mismatch | Train on real inputs, not clean ones |
| Result vanished on rerun | Seed noise, never a real effect | Multiple seeds, paired comparison |

## Silent failures — no error, wrong result

The dangerous set. Nothing raises, everything looks fine.

1. **Template mismatch** between training and serving.
2. **Missing end-of-turn token** — trains fine, never stops.
3. **Loss masking wrong** — training on prompts unintentionally.
4. **Contamination** — held-out measures memorisation, reports generalisation.
5. **Group or temporal leakage** — split by the wrong key.
6. **Catastrophic forgetting** — every number you watch improves.
7. **Adapter attached to nothing** — trains, logs a loss, learns nothing.
8. **Evaluating a different artifact than you ship** — e.g. bf16 eval, 4-bit deploy.

Each has a specific detection step above. None announces itself.

## Reducing forgetting

Cheapest first:

1. Fewer steps, or an earlier checkpoint
2. Lower learning rate
3. Lower rank, or fewer target modules
4. Mix a few percent general instruction data into training
5. **Keep the adapter unmerged and route** — the base stays intact, so forgetting stops mattering

## Comparison hygiene

- One variable at a time; fix seed, data and split
- Multiple seeds — variance often exceeds the effect
- Paired comparison on identical examples
- Report `n` and an interval, never a bare number
- Read actual generations, including failures, every time

## What to record per run

Base model **and revision** · adapter config verbatim · dataset and exact split · seed · effective batch size · LR and schedule · steps · chosen checkpoint and the number justifying it · library versions · eval and regression results.

## Related

- [Lesson 11](../lessons/0011-your-first-adapter.md), [Lesson 12](../lessons/0012-reading-a-training-run.md), [Lesson 22](../lessons/0022-contamination-and-held-out-design.md), [Lesson 24](../lessons/0024-the-regression-suite.md)
