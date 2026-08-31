---
title: 12. Reading a Training Run
description: Diagnosing by curve shape, and what loss cannot see
type: lesson
---

# Lesson 12. Reading a Training Run

**Mission link:** "Diagnose a failed run and name the cause" is on the success list. Most people read a loss curve and guess.
**Primary source:** [Blog: "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
**Prerequisites:** [Lesson 11](0011-your-first-adapter.md)

## Warm-up

1. ▢ Name the four checks to run before caring about the loss curve.

<details markdown="1"><summary>Check</summary>

Confirm the adapter attached; decode a real training example and count scored positions; confirm loss moves; confirm the pipeline can overfit two examples.

</details>

2. ▢ Why record the base model revision next to the adapter?

<details markdown="1"><summary>Check</summary>

An adapter is a diff against specific weights. Without the exact base it is unusable, and a near-miss base degrades quality silently.

</details>

3. ▢ Bytes per frozen parameter versus per trainable parameter?

<details markdown="1"><summary>Check</summary>

Two versus sixteen.

</details>

## Know this

### Training loss alone tells you almost nothing

Training loss falling means the model is fitting the data it can see. That is compatible with a model that is learning the task and with one that is memorising the training set. **You need a held-out split to distinguish them, and there is no substitute.**

Set one aside before you start:

```python
split = dataset.train_test_split(test_size=0.05, seed=0)
args = SFTConfig(..., eval_strategy="steps", eval_steps=50)
trainer = SFTTrainer(..., train_dataset=split["train"], eval_dataset=split["test"])
```

### The shapes and what they mean

| Training loss | Held-out loss | Diagnosis | Action |
|---|---|---|---|
| Falls | Falls | Learning | Continue |
| Falls | Flattens then rises | Overfitting from the turn | Stop at the minimum; more data or less capacity |
| Falls to ~0 fast | Rises immediately | Memorising | Dataset far too small for this capacity |
| Flattens high | Flattens high | Underfitting | More rank, more target modules, higher learning rate |
| Flat from step 1 | Flat | Broken pipeline | Lesson 11's four checks |
| Spikes, or `NaN` | — | Instability | Lower learning rate; check for fp16 overflow; add warm-up |

The **held-out minimum** is the useful checkpoint, not the final step. Save checkpoints periodically and keep the best one; a run that ends at step 1000 when held-out loss bottomed at step 400 has trained 600 steps of damage.

### Diagnosing by shape, more carefully

**A loss floor that more training will not lower** is a capacity ceiling. The adapter cannot express the update the task needs. Adding epochs cannot fix it; adding rank or target modules can.

**Loss that spikes and recovers** is usually a batch containing something unusual — an outlier-length example, corrupted text, a duplicated block. Find it. A single pathological example can move a small-dataset run.

**Loss that becomes `NaN`** is overflow. In fp16 this is common and is what loss scaling exists to prevent; in bf16 it usually indicates something worse, like a division by zero in the data pipeline or a learning rate high enough to send weights to infinity.

**Loss that falls in a clean staircase** with steps at epoch boundaries means the model is recognising examples it has seen before. That is memorisation showing up in the curve directly.

### What loss cannot see at all

This is the important part of the lesson.

Cross-entropy scores next-token prediction on your data distribution. It is silent on:

- **Whether generations are usable.** A model can score well and produce output that never stops, or that ignores the requested format.
- **Whether anything else broke.** [Catastrophic forgetting](../GLOSSARY.md) — degradation of abilities unrelated to your task — does not appear in your task's loss at all. Your held-out loss can improve monotonically while the model becomes worse at everything else it could do.
- **Whether the improvement is real or contamination.** If your held-out examples are near-duplicates of training examples, held-out loss is measuring memorisation and calling it generalisation.

So: **generate, every time.** Fix a small set of prompts before training. Run them through the base model and save the outputs. Run them through the adapted model at the same sampling settings and diff. Ten minutes of reading real generations catches things no metric on your curve will.

```python
PROBES = [
    "<a representative task prompt>",
    "<an edge case you care about>",
    "<something unrelated to the task, to check for forgetting>",
]
```

That third category is the one people leave out, and it is how forgetting gets shipped.

### Reproducibility

Log enough that you could re-run it: base model and revision, dataset and its exact split, seed, every hyperparameter, and library versions. Adapter fine-tuning has a large enough configuration surface that "I think it was rank 32" is not a record.

Comparing two runs is only meaningful when exactly one thing differs between them. Change rank *or* learning rate, not both, and keep the seed and data fixed. This sounds obvious and is routinely violated, usually because a run took long enough to make patience expensive.

## Practice

1. ▢ Training loss is 0.2 and falling. Held-out loss bottomed at 0.9 two hundred steps ago and is now 1.1. What is happening, and which checkpoint do you ship?

<details markdown="1"><summary>Check</summary>

Overfitting. The model is now fitting noise specific to the training set.

Ship the checkpoint from the held-out minimum, roughly two hundred steps back. Then reduce capacity, add data, or stop earlier next time.

</details>

2. ▢ Both losses flatten at a level too high to be useful. Rank 8, attention-only targets. What do you change, and what do you not?

<details markdown="1"><summary>Check</summary>

Change capacity: extend targets to all linear layers, and raise rank. Consider whether the learning rate is too low.

Do not add epochs. A capacity ceiling does not move with more passes over the same data — that is the definition of the diagnosis.

</details>

3. ▢ Held-out loss improves throughout. You ship. Users report the model has become worse at things it used to do. What did you fail to measure?

<details markdown="1"><summary>Check</summary>

Catastrophic forgetting. Your held-out set is drawn from your task's distribution, so it cannot see degradation on capabilities outside that distribution.

The fix is a regression suite covering abilities you are not training — general instruction following, refusal behaviour, other formats. That is Lesson 24, and this failure is why it exists.

</details>

4. ▢ Which observation most strongly indicates a broken pipeline rather than bad hyperparameters?

   - a) The loss curve plateaus at a value far above zero
   - b) The loss is exactly unchanged across all fifty steps
   - c) The held-out loss rises while the training loss falls
   - d) The loss spikes upward at one step and then recovers

<details markdown="1"><summary>Check</summary>

**b)** The loss is exactly unchanged across all fifty steps.

A plateau is underfitting, a diverging pair is overfitting, and a spike is usually one bad batch — all real training behaviours. Loss that does not move *at all* means no gradient is reaching any parameter, which is a wiring fault.

</details>

5. ▢ Why must at least one of your generation probes be unrelated to the task?

<details markdown="1"><summary>Check</summary>

Because it is the only cheap way to notice forgetting during a run. Task-related probes and task-related held-out loss both improve while unrelated abilities decay, so nothing you are already measuring will warn you.

</details>

6. ▢ Loss falls in a staircase with drops at each epoch boundary. Diagnose.

<details markdown="1"><summary>Check</summary>

The model is recognising examples it has already seen — memorisation, visible directly in the curve. Each new epoch produces a step down because the data is no longer novel.

Check held-out loss, which is likely flat or rising, and reduce epochs or capacity.

</details>

## Real-world reps

- [ ] Add a held-out split and periodic evaluation to your run from Lesson 11. Find the held-out minimum.
- [ ] Write three generation probes, one of them unrelated to your task. Save base-model outputs before training.
- [ ] Deliberately overfit: train a generously ranked adapter on 50 examples for many epochs and watch the two curves separate. Keep the plot.
- [ ] Tomorrow: write a one-page run record for a real run — base model, revision, data, split, seed, every hyperparameter, library versions.

## Going further

- [Blog: "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
- [Failure modes](../reference/failure-modes.md)
- [Lesson 24. The Regression Suite](0024-the-regression-suite.md): where the unrelated probe becomes a real system

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
