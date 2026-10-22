---
title: Glossary
description: Canonical terms for adapter fine-tuning
type: glossary
---

# Adapter Fine-Tuning Glossary

Canonical terms for this workspace. A term lands here once it can be used correctly, not when it is first mentioned, so this grows as lessons are earned.

## Usage in this workspace

Three words are used loosely across the field in ways that would make later lessons ambiguous, so they are pinned from the start:

**Fine-tuning**:
Training a small set of added or selected parameters on a task while the base model's weights stay frozen. When all weights are trained instead, this workspace always says _full fine-tuning_ explicitly.
_Avoid_: training, retraining, teaching the model

**Adapter**:
The small set of trainable weights added alongside a frozen base model, together with the configuration describing where they attach.
_Avoid_: fine-tune (as a noun), LoRA (when the method is not specifically LoRA), checkpoint

**Quantisation**:
Storing weights at lower numeric precision than they were trained in. In this workspace it always refers to the _frozen base_ unless stated otherwise: adapters stay at higher precision, and quantisation for inference is a separate concern.
_Avoid_: compression, shrinking, optimisation

## Terms

**Base model**:
A model trained on one objective only, predicting the next token across a large corpus. It continues text rather than answering it, and it has no _chat template_.
_Avoid_: raw model, pretrained model (when the distinction from an _instruct model_ matters)

**Catastrophic forgetting**:
The degradation, during fine-tuning, of abilities the training data did not reinforce, such as general instruction following. It does not show in the task's loss or held-out metric, which can improve while it happens.
_Avoid_: overfitting (a different failure, visible on the task's own _held-out set_)

**Chat template**:
The exact string format that a chat model's training conversations were rendered into, turning roles and messages into one flat token sequence. Training and serving must use the same rendering.
_Avoid_: prompt format, chat format

**Contamination**:
Test examples the model has already seen. _Your_ contamination is test examples that also appear, exactly or nearly, in your training set; _inherited_ contamination is test examples that were in the _base model_'s pretraining corpus.
_Avoid_: leakage (name which of the two kinds is meant)

**DoRA**:
A _LoRA_ variant that splits each frozen weight matrix into a magnitude vector, trained directly, and a direction, which receives the low-rank update and is renormalised afterwards. In PEFT it is a flag on the LoRA config, not a separate method.
_Avoid_: weight-decomposed LoRA (spell out only once, then say DoRA)

**Double quantisation**:
_Quantisation_ of the blockwise scales themselves: the first-level fp32 scales are grouped and stored at 8 bits with their own second-level scale.
_Avoid_: nested quantisation, 2-bit quantisation

**Effective batch size**:
The number of examples whose gradients are averaged into one optimiser step: per-device batch size × gradient accumulation steps × number of devices.
_Avoid_: batch size (when the per-device number is meant)

**Gradient checkpointing**:
Keeping only each block's input during the forward pass and re-running the block when the backward pass reaches it, so stored activations grow with roughly the square root of depth instead of linearly, for about one extra forward pass per step.
_Avoid_: checkpointing (alone, since a training checkpoint is weights saved to disk), activation recomputation

**Held-out set**:
Data the model is not trained on, used to measure whether it learned the task. In this workspace it has two parts: validation, which settings and checkpoints are chosen against, and test, touched once at the end.
_Avoid_: eval set, dev set

**Instruct model**:
A _base model_ trained further on instruction and response pairs, and usually on preference data after that. Chat model means the same thing here.
_Avoid_: aligned model, assistant model

**LoRA**:
Low-rank adaptation: an _adapter_ that learns a weight matrix's update as the product of two small matrices, `ΔW = BA`, scaled by `α/r`, while the matrix itself stays frozen.
_Avoid_: adapter (when the specific method is meant), low-rank fine-tune

**LoRA alpha**:
The fixed scalar `α` (`lora_alpha`) that scales a _LoRA_ update by `α/r`. What sets the update's scale is the ratio `α/r`, not either number alone.
_Avoid_: scaling factor (that is `α/r`, not `α`)

**Merging**:
Folding a _LoRA_ update into the base weights, `W₀ + (α/r)BA`, and discarding the adapter structure. It is exact against a full-precision base and lossy against a quantized one.
_Avoid_: exporting, baking in

**Multi-adapter serving**:
Serving several _adapters_ on one shared base by batching requests that use different adapters together: the base computation is shared across the batch, and each request's adapter contribution is computed separately.
_Avoid_: adapter swapping (the naive approach that serialises requests)

**NF4**:
NormalFloat, a 4-bit format whose 16 levels are spaced for values normally distributed around zero, as weights are, instead of at equal intervals as in plain int4. It is used inside blockwise _quantisation_, on blocks already normalised by their absmax.
_Avoid_: int4 (a different, uniformly spaced format)

**Optimiser state**:
The tensors an optimiser keeps per trainable parameter besides the weight and its gradient. For AdamW these are the first and second moments, 4 bytes each.
_Avoid_: optimizer cache, momentum (only the first moment)

**Packing**:
Concatenating short training examples into full-length sequences, so that a batch carries almost no padding.
_Avoid_: length grouping (a different remedy, which batches similarly sized sequences together)

**QLoRA**:
_LoRA_ trained against a frozen base stored in _NF4_ with _double quantisation_, which is dequantised on every forward and backward pass. It is LoRA with a cheaper base, not a method with hyperparameters of its own.
_Avoid_: 4-bit fine-tuning, quantized LoRA (when it suggests the adapter is quantized)

**Rank**:
The inner dimension `r` of the two _LoRA_ matrices, `A` being `r × d_in` and `B` being `d_out × r`. It is the adapter's capacity: it bounds how complex an update the adapter can express.
_Avoid_: size, dimension (alone)

**Regression suite**:
A fixed set of probes outside the task (general instruction following, format and behavioural compliance, safety and refusal behaviour, adjacent capability), run before and after training to detect _catastrophic forgetting_. It is a different instrument from the _held-out set_, and both are needed.
_Avoid_: benchmark, eval suite (when this specific instrument is meant)

**Target modules**:
The weight matrices an _adapter_ attaches to, named by the model's own module names.
_Avoid_: layers (an adapter attaches to specific matrices within a layer)
