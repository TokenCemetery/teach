---
title: 4 — What Training Actually Changes
description: The four operations in one training step
type: lesson
---

# Lesson 4 — What Training Actually Changes

**Mission link:** Every memory argument, hyperparameter and failure mode in this workspace follows from what one training step does.
**Primary source:** [Paper: "Decoupled Weight Decay Regularization" (AdamW) — Loshchilov & Hutter, arXiv:1711.05101](https://arxiv.org/abs/1711.05101)
**Prerequisites:** [Lesson 1](0001-what-a-base-model-is.md), [Lesson 3](0003-tokenizers-and-chat-templates.md)

## Warm-up

1. ▢ Why must training and serving use the identical chat template?

<details markdown="1"><summary>Check</summary>

The template defines the token distribution the weights are fit to. Training on one rendering and serving another means deploying a different problem — and loss will not reveal it.

</details>

2. ▢ What is a residual connection doing around each sublayer?

<details markdown="1"><summary>Check</summary>

Adding the sublayer's output back onto the running stream instead of replacing it, so each block contributes an increment rather than a rewrite.

</details>

3. ▢ Name the two MLP projections that widen and narrow the hidden dimension.

<details markdown="1"><summary>Check</summary>

`up_proj` widens to the intermediate dimension, `down_proj` returns to the hidden dimension. `gate_proj` produces the gate applied in between.

</details>

## Know this

One training step is four operations. Every memory cost in stage 2 is one of these four holding something in memory.

**1. Forward pass.** Run a batch of sequences through the model and compute the loss. To make step 3 possible, the intermediate results at each layer — the **activations** — must be kept, not discarded. This is why training needs far more memory than inference.

**2. Loss.** Cross-entropy between the predicted distribution and the actual next token, averaged over every position that counts. Which positions count is your choice, and it matters:

- **Full-sequence loss** scores every token, including the user's prompt. The model learns to predict prompts as well as answers.
- **Completion-only loss** masks the prompt tokens out, scoring only the assistant's response.

Masking is done by setting the label to `-100` at positions to ignore, a convention the loss function reads as "skip". For instruction tuning, completion-only is usually what you want: you are teaching responses, not teaching the model to imagine user questions.

**3. Backward pass.** Work backwards through the graph applying the chain rule, producing for every trainable parameter a **gradient**: the direction and magnitude by which that parameter should change to reduce the loss. One gradient per trainable parameter — the same shape as the parameter itself. Remember that; it is half of Lesson 6.

**4. Optimizer step.** Update the parameters using the gradients. Plain gradient descent would be `w ← w − lr · g`. Nobody uses that. **AdamW** maintains two running averages per parameter:

| State | Tracks | Effect |
|---|---|---|
| First moment | Mean of recent gradients | Momentum — smooths noisy directions |
| Second moment | Mean of recent squared gradients | Per-parameter step scaling |

Two extra tensors, each the size of the parameters. That is the other half of Lesson 6, and it is the reason full fine-tuning is so expensive.

### Learning rate and schedule

The learning rate scales the step. Too high and the update overshoots, destroying pretrained structure — this is what catastrophic forgetting looks like mechanically. Too low and nothing moves.

Two standard refinements:

- **Warm-up:** start near zero and ramp up over the first few hundred steps, so early noisy gradients do not wreck the weights.
- **Decay:** reduce the rate over training, typically on a cosine curve, so late steps refine rather than thrash.

Adapter fine-tuning tolerates learning rates one to two orders of magnitude higher than full fine-tuning — commonly around `1e-4` to `2e-4` rather than `1e-5`. Lesson 9 explains why.

### Batch size, real and effective

Gradients are averaged over a batch. Bigger batches give less noisy gradients but cost proportionally more activation memory. **Gradient accumulation** buys the averaging without the memory: run several small batches, sum the gradients, step once.

```text
effective batch size = per_device_batch_size × gradient_accumulation_steps × num_devices
```

Report and reason about the effective number. A run with batch size 1 and 16 accumulation steps is a batch-16 run, and comparing it to a batch-1 run as though they were equivalent is a common way to draw a false conclusion.

### An epoch is not a unit of learning

One epoch is one pass over the dataset. On a small instruction dataset, two or three epochs is a typical range and more than that usually memorises. The number of *steps* is what the optimizer sees, and steps depend on dataset size and effective batch size together — so "3 epochs" means something completely different on 500 examples than on 500,000.

## Practice

1. ▢ Why does training need much more memory than inference, even at the same batch size and sequence length?

<details markdown="1"><summary>Check</summary>

Training must keep the forward pass's activations so the backward pass can compute gradients, and it must store gradients and optimizer state. Inference discards each layer's intermediates as soon as the next layer has consumed them.

</details>

2. ▢ You are fine-tuning on question-and-answer pairs. Should loss be computed over the whole sequence or only the answer? Give the consequence of the wrong choice.

<details markdown="1"><summary>Check</summary>

Only the answer, in most cases. Scoring the prompt too spends capacity teaching the model to generate plausible user questions, which is not the task, and it dilutes the gradient signal on the part you care about.

The exception is when prompts are highly stylised and you want the model to internalise the domain's language generally. Decide deliberately; do not let the default decide for you.

</details>

3. ▢ AdamW stores how many extra tensors per trainable parameter, and what are they?

<details markdown="1"><summary>Check</summary>

Two: a running mean of gradients (first moment) and a running mean of squared gradients (second moment). Each is the same shape as the parameter.

Plus the gradient itself, which is a third same-shaped tensor but is not optimizer state. Keeping those three straight is exactly what Lesson 6 asks you to do.

</details>

4. ▢ Run A: batch size 8, accumulation 1. Run B: batch size 1, accumulation 8. Same data, same seed, same learning rate. Are the optimizer steps equivalent?

<details markdown="1"><summary>Check</summary>

Effectively yes — both average gradients over 8 examples before stepping, so the update is essentially the same, and B uses far less activation memory. Small differences remain from how padding and per-batch normalisation interact.

Gradient accumulation is the standard way to get a large effective batch on constrained memory. What is *not* equivalent is comparing B against a genuine batch-1 run, which steps eight times as often on noisier gradients.

</details>

5. ▢ A colleague sets the learning rate for a LoRA run to `1e-5` "because that is what full fine-tuning uses". What do you expect, and what do you say?

<details markdown="1"><summary>Check</summary>

Expect underfitting: loss drops slowly, the model barely changes, and the run looks like evidence that the method does not work.

Adapters start from zero contribution and hold a tiny fraction of the parameters, so they need a much larger rate to move at all — usually `1e-4` to `2e-4`. Importing a full fine-tuning learning rate is one of the most common reasons a first LoRA run disappoints.

</details>

6. ▢ Why is warm-up more than a superstition?

<details markdown="1"><summary>Check</summary>

Early in training, AdamW's second-moment estimate is built from very few samples, so its per-parameter scaling is unreliable and can produce enormous steps. Ramping the learning rate up limits the damage those first steps can do to pretrained weights.

</details>

## Real-world reps

- [ ] Write out the four operations of a training step from memory, then check them against this lesson.
- [ ] Take any published fine-tuning script and identify its effective batch size, learning rate, warm-up and schedule. Write the four numbers down.
- [ ] Tomorrow: find a training config where you disagree with one of those four numbers, and write one sentence on what you would change and why.

## Going further

- [Paper: "Decoupled Weight Decay Regularization" (AdamW) — Loshchilov & Hutter, arXiv:1711.05101](https://arxiv.org/abs/1711.05101)
- [Paper: "Adam: A Method for Stochastic Optimization" — Kingma & Ba, arXiv:1412.6980](https://arxiv.org/abs/1412.6980)
- [Blog: "A Recipe for Training Neural Networks" — Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
- [Memory budget](../reference/memory-budget.md) — stage 2 turns these four steps into bytes

---

Not landing? Reread the primary source at the top — this lesson compresses it, and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
