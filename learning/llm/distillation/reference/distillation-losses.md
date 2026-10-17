---
title: Distillation Losses
description: Soft targets, temperature, the combined loss, the token-level loss, forward and reverse KL, the tokenizer constraint and the cost of storing logits
type: reference
---

# Distillation Losses: Stages 1 and 2 for Lookup

Stages 1 and 2 compressed for lookup. [Lessons 1 to 3](../lessons/0001-what-distillation-buys.md) cover soft targets and temperature, [lesson 4](../lessons/0004-token-level-distillation.md) the token-level loss, [lesson 5](../lessons/0005-forward-and-reverse-kl.md) the direction of the divergence, [lesson 6](../lessons/0006-the-tokenizer-constraint.md) the tokenizer constraint and [lesson 7](../lessons/0007-distilling-during-pretraining.md) the cost of the teacher's distribution at scale.

## Soft targets and temperature

| Term | Definition | Source |
|---|---|---|
| Soft targets | The teacher's probabilities over every class, used as the target in place of or beside the hard label | Hinton et al., 2015, section 1 |
| Softmax with temperature | q_i = exp(z_i / T) / sum_j exp(z_j / T). T = 1 is the normal softmax, a higher T gives a softer distribution | Hinton et al., equation 1 |
| Where T is used | The same high T for teacher and student during training. The student runs at T = 1 afterwards | Hinton et al., section 2 |
| Gradient at temperature T | dC/dz_i = (1/T)(q_i - p_i). For large T and zero-meaned logits it is about (1/(N T^2))(z_i - v_i), so matching logits is a special case | Hinton et al., section 2.1 |
| The T squared factor | Soft-target gradients scale as 1/T^2, so multiply the soft loss by T^2 when combining it with the hard loss | Hinton et al., section 2 |

The factor in a run, from the logits `[9, 4, 2, 0, -4]` against `[6, 5, 0, 1, -2]`: the largest gradient entry is 0.2663 at T = 1 and 0.0017 at T = 20, and multiplied by T squared it stays between 0.64 and 0.84 from T = 2 to T = 20 ([lesson 3](../lessons/0003-temperature.md)).

## The combined loss

```text
loss = lambda * T^2 * CE(teacher at T, student at T) + (1 - lambda) * CE(label, student at 1)
```

The notation is this track's. Hinton et al. describe a weighted average of the two cross-entropies and found the best results generally with a considerably lower weight on the hard-label one.

| Setting | Value | Source and scope |
|---|---|---|
| Speech, relative weight on the hard term | 0.5 | Hinton et al., section 4.1, one acoustic model |
| Speech, temperatures tried | 1, 2, 5, 10 | Hinton et al., section 4.1 |
| MNIST, 800 unit student, soft targets at T = 20 | 74 test errors, against 146 alone and 67 for the teacher | Hinton et al., section 3 |
| MNIST, 30 unit student, best temperatures | 2.5 to 4 | Hinton et al., section 3 |
| Kim and Rush word-level mixture weights tried | 0.5 and 0.9, 0.5 better | Kim and Rush, 2016, section 4 |
| LLM pruning retraining, temperatures tried | 0.1, 0.5, 1.0, 3.0, best at 1.0 | Muralidharan et al., 2024, appendix A.3 |
| LLM pretraining, temperatures tried | 0.5 to 10, best at 1 across scales | Busbridge et al., 2025, appendix G.2 |
| LLM pruning retraining, loss mix | Logit loss alone better than mixing in the language modeling loss | Muralidharan et al., 2024, section 4 |

Each row is one paper on its own setup. The two LLM temperature rows disagree with the classifier ones, so sweep T, including 1, on your own pair.

## The token-level loss

| Item | Choice |
|---|---|
| Logit shapes | Student and teacher, each (batch, positions, vocab) |
| Divergence axis | The last one, the vocabulary, giving (batch, positions) |
| Prefix | A fixed sequence, human text or teacher text, fed to both models (teacher forcing) |
| Teacher | Forward pass with gradients off |
| Reduction | Kim and Rush sum over positions. GKD and Minitron divide by the length. Mask padding and divide by the mask sum |
| Temperature | Divide both logits by T before the log-softmax, multiply the loss by T^2 if mixed with a hard term |

```python
import torch.nn.functional as F

def token_kd_loss(student_logits, teacher_logits, mask, T=1.0):
    s = F.log_softmax(student_logits / T, dim=-1)
    t = F.log_softmax(teacher_logits / T, dim=-1)
    kl = (t.exp() * (t - s)).sum(dim=-1)
    return (kl * mask).sum() / mask.sum()
```

Cross-entropy against the teacher and forward KL differ by the teacher's entropy, a constant for the student, so they have the same gradients. Gemma 2 writes the sum of -P_T(x | x_c) log P_S(x | x_c) (section 3.2).

## Forward and reverse KL

| | Forward KL | Reverse KL |
|---|---|---|
| Expression | KL(p \|\| q) = sum p log(p / q) | KL(q \|\| p) = sum q log(q / p) |
| p is the teacher, q the student | Weighted by the teacher | Weighted by the student |
| Punishes | A student that gives little mass where the teacher has much | A student that gives mass where the teacher has little |
| Behaviour | Mode covering, spreads over every mode | Mode seeking, commits to one |
| On the lesson 5 toy | Prefers the spread student, 0.595 against 1.572 | Prefers the committed student, 0.623 against 1.273 |

| Source | Finding | Scope |
|---|---|---|
| MiniLLM, Gu et al., 2023 | Reverse KL for generative distillation, since forward KL gives mass to the teacher's void regions | Instruction following, policy-gradient on student samples |
| GKD, Agarwal et al., 2023 | The best divergence is task-dependent. Generalized JSD(beta) interpolates, forward-like near 0, reverse-like near 1. Reverse KL much better than forward on FLAN instruction tuning | T5 students, XSum, WMT, GSM8K, FLAN |
| Minitron, Muralidharan et al., 2024 | Forward KLD best: LM loss 2.155 against 2.665 for reverse on a depth-pruned 8B | Retraining pruned base models |

TRL's `GKDConfig` exposes the choice as `beta`: 0.0 is the KL divergence, 1.0 the inverse KL, default 0.5.

## The tokenizer constraint

| Situation | What works | What it costs |
|---|---|---|
| Same tokenizer | Token-level loss | Needs the teacher's logits |
| Student built from the teacher (DistilBERT, Minitron) | Token-level loss | Student constrained to the teacher's design |
| Different tokenizers, logits available | ULD loss, or TRL's GOLD trainer | Loses token identity in the distance term, uniform cost assumption, crude position alignment |
| Only the teacher's text | Train on its generated sequences (stage 3) | The student never sees the teacher's distributions |

ULD (Boizard et al., 2024): L = sum over t of CE(t) + lambda * W1(student, teacher), lambda 1.5, with W1 as the sum of absolute differences of the probability vectors sorted in decreasing order (section 3). A student that puts its mass on the wrong token can score 0 on W1, so the gold-token cross-entropy carries the identity signal.

TRL, as read for lesson 6: `GKDTrainer` takes one tokenizer as `processing_class` and has no teacher tokenizer argument. GOLD is documented as supporting different tokenizers, with `use_uld_loss=True` and `teacher_tokenizer_name_or_path`, and is in `trl.experimental`.

## The cost of storing the teacher's logits

Arithmetic of [lesson 7](../lessons/0007-distilling-during-pretraining.md), with Gemma 2's vocabulary of 256,128 (Table 1). The 2 bytes per probability and the k = 256 with a 4-byte index are assumptions, not figures from the report.

| Quantity | Value |
|---|---|
| Full distribution per token, bf16 | 512,256 bytes |
| Full distribution per 8,192-token sequence | 4.20 GB |
| Full for 2T tokens (the 2B run) | 1.02 EB |
| Full for 8T tokens (the 9B run) | 4.10 EB |
| Top-256 per token, 6 bytes per entry | 1,536 bytes, 333.5 times smaller |
| Top-256 for 2T tokens | 3.07 PB |
| Top-256 for 8T tokens | 12.29 PB |

The Gemma 2 report does not describe how the teacher's distribution was supplied. Minitron computes the teacher in a forward pass alongside training and compares runs at equal compute. Minitron's top-K test found a significant accuracy drop for K up to 100 and no gain from truncating at larger K, on one pruned-model retraining setup.

## Where to read more

- [Resources](../RESOURCES.md)
- [Glossary](../GLOSSARY.md)
