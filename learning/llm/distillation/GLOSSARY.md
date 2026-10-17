---
title: Glossary
description: "Canonical terms for knowledge distillation of LLMs"
type: glossary
---

# Distillation Glossary

Canonical terms for training a smaller model from a larger one's outputs, the losses and data that carry the signal, and how the result is judged. In this workspace "distillation" always means knowledge distillation from a teacher model to a student model; it never means dataset distillation or distilling a prompt.

## Terms

**Beam search**:
A decoding method that keeps the few highest-scoring partial sequences at each step and returns the best complete one, as an approximation to the most probable sequence.
_Avoid_: greedy search (that is beam size 1), best-first decoding

**Capacity gap**:
The drop in student quality that can appear when the teacher is much larger than the student, so that a stronger teacher produces a worse student than a weaker one would.
_Avoid_: teacher too smart, size mismatch

**Combined loss**:
A distillation loss that adds the cross-entropy against the hard labels to the divergence from the teacher's soft targets, weighted by a mixing coefficient.
_Avoid_: hybrid loss, dual loss

**Cross-tokenizer distillation**:
Logit distillation between a teacher and a student whose vocabularies differ, done by aligning or comparing their distributions without a shared token index.
_Avoid_: tokenizer-free distillation, vocabulary transfer

**Decontamination**:
Removing from training data the examples that match or closely resemble an evaluation set, so that a benchmark score does not measure memorized items.
_Avoid_: cleaning (too broad), deduplication (that removes repeats within the training set)

**Distillation**:
Training a student model to reproduce the behaviour of a teacher model, using the teacher's output distributions or generated text as the training signal.
_Avoid_: compression (too broad), model copying

**Distillation scaling law**:
A fitted relationship, from Busbridge et al., that predicts a student's cross-entropy from its size, the number of distillation tokens and the teacher's cross-entropy.
_Avoid_: distillation law, KD scaling

**Exposure bias**:
The mismatch between training on prefixes someone else wrote and generating from prefixes the model wrote itself, so that its own early mistakes put it in states it never trained on.
_Avoid_: train-test mismatch (too broad), drift

**Fidelity**:
How closely a student's predictions agree with its teacher's, measured on the same inputs, as opposed to how well either does on the task.
_Avoid_: accuracy, faithfulness

**Forward KL**:
The divergence KL(teacher ‖ student), averaged under the teacher's distribution, which penalises the student for putting little probability where the teacher puts much and so pushes it to cover every mode.
_Avoid_: mode-covering KL without naming the direction, plain KL

**Generalized knowledge distillation**:
The on-policy method of Agarwal et al. that trains the student on a mix of fixed and student-generated sequences, scored token by token against the teacher with a chosen divergence. Abbreviated GKD.
_Avoid_: generalised KD, generic distillation

**Hard label**:
The single correct class or token used as a training target, with all its probability on one answer.
_Avoid_: ground truth (it may be the teacher's argmax), one-hot target without context

**Imitation gap**:
The distance between how much a student sounds like its teacher and how much of the teacher's capability it actually has, which imitation on a limited budget closes on style much faster than on capability.
_Avoid_: false promise (the paper's title, not a term), style transfer

**KL divergence**:
For two distributions P and Q over the same tokens, the sum over tokens of P log(P / Q): a measure of how far Q is from P that is not symmetric. Its two directions in distillation are forward KL and reverse KL.
_Avoid_: KL distance, relative entropy without introducing the term

**Logit**:
A model's raw, unnormalised score for one class or token before the softmax turns the scores into probabilities.
_Avoid_: score (ambiguous), log-probability (that is after the softmax)

**Logit distillation**:
Distillation whose training signal is the teacher's full output distribution at each position, which requires access to the teacher's logits and a shared vocabulary.
_Avoid_: white-box distillation (accepted alias, but use one term), soft distillation

**Off-policy distillation**:
Distillation on sequences the student did not generate: human data or the teacher's own outputs, fixed before training.
_Avoid_: offline distillation, supervised distillation

**On-policy distillation**:
Distillation on sequences the student generates during training, with the teacher scoring each token the student chose, so the student trains on its own mistakes.
_Avoid_: online distillation (also used for teachers trained alongside the student), self-distillation

**Rationale**:
The intermediate reasoning a teacher writes before or alongside its answer, used as an extra training target so the student learns how the answer was reached.
_Avoid_: explanation (fine in prose, not as the term), chain of thought (the prompting technique that produces it)

**Rejection sampling**:
Drawing several candidate outputs from a model for each prompt and keeping only those that pass a check, such as a correct final answer.
_Avoid_: filtering (too broad), best-of-n (that keeps one winner rather than discarding by a check)

**Reverse KL**:
The divergence KL(student ‖ teacher), averaged under the student's distribution, which penalises the student for putting probability where the teacher puts little and so pushes it to commit to one mode.
_Avoid_: mode-seeking KL without naming the direction, backward KL

**Sequence-level distillation**:
Distillation in which the student is trained with ordinary cross-entropy on whole sequences the teacher decoded, rather than on the teacher's per-token distributions.
_Avoid_: hard distillation, black-box distillation (that also covers generated-data distillation)

**Soft targets**:
The teacher's full probability distribution over classes or tokens, used as the training target in place of or alongside the hard label.
_Avoid_: soft labels (accepted alias, but use one term), dark knowledge (the information they carry, not the targets)

**Student**:
The model being trained in a distillation, usually smaller or cheaper to run than the teacher.
_Avoid_: distilled model before training is done, child model

**Subliminal learning**:
A student acquiring a trait of its teacher from data that is semantically unrelated to the trait, observed by Cloud et al. when the two share the same base model.
_Avoid_: hidden distillation, data poisoning (that is deliberate)

**Supervised baseline**:
A model of the student's size trained without distillation, on the same data or the same compute, used as the comparison that shows whether distillation caused a result.
_Avoid_: control model (too broad), plain model

**Synthetic data**:
Training examples generated by a model rather than written by people. In this workspace it means data generated by the teacher for the student.
_Avoid_: fake data, augmented data (augmentation transforms existing examples)

**Teacher**:
The model whose outputs are the training signal in a distillation. It is fixed during training and usually larger or more capable than the student.
_Avoid_: oracle, parent model

**Teacher assistant**:
A model of intermediate size distilled from the teacher and then used as the teacher for a smaller student, to bridge a capacity gap.
_Avoid_: intermediate teacher without introducing the term, TA model

**Teacher forcing**:
Feeding a model a fixed prefix rather than its own earlier outputs, so one forward pass yields a next-token distribution at every position of a sequence.
_Avoid_: teacher-forced decoding, free running (that is the opposite)

**Temperature**:
The divisor T applied to logits before the softmax. T above 1 flattens the distribution and raises the probabilities of unlikely answers so the student can learn from them. That was the classifier-era default; the LLM distillation runs in this workspace's sources found T of 1 best.
_Avoid_: sampling temperature (same operation, different purpose), softness

**Token-level distillation**:
Logit distillation applied at every position of a sequence, minimising a divergence between the teacher's and the student's next-token distributions.
_Avoid_: word-level distillation (the original paper's name), per-token KD

**Top-1 agreement**:
The share of inputs on which a student's highest-probability answer is the same as its teacher's, one of the two fidelity metrics in Stanton et al.
_Avoid_: accuracy (that is against the correct answer), match rate

**Top-k logits**:
The k largest entries of a teacher's output distribution at a position, kept with their token indices in place of the full vocabulary row, to cut storage.
_Avoid_: sparse logits, truncated softmax without saying what happens to the dropped mass
