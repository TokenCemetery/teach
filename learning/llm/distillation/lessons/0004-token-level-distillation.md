---
title: "4. Token-Level Distillation"
description: Matching the teacher's next-token distribution at every position of a sequence
type: lesson
---

# Lesson 4. Token-Level Distillation

**Mission link:** The mission asks you to write the token-level distillation loss for an LLM, and this lesson writes it: one divergence per position, summed or averaged over the sequence, with padding masked out.
**Primary source:** [Paper: "Sequence-Level Knowledge Distillation", Kim and Rush, 2016](https://arxiv.org/abs/1606.07947)
**Prerequisites:** [Lesson 3](0003-temperature.md), [Token-level distillation](../GLOSSARY.md), [Teacher forcing](../GLOSSARY.md), [KL divergence](../GLOSSARY.md)

## Warm-up

1. ▢ In the combined loss, which term runs at the high temperature, and what multiplies it?

<details markdown="1"><summary>Check</summary>

The cross-entropy with the teacher's soft targets runs at the high temperature T, and T squared multiplies it so that its gradients keep their size against the hard-label term as T changes. The hard-label term runs at T = 1.

</details>

2. ▢ Why is a teacher's probability of 10^-6 on a wrong class nearly invisible to the loss at T = 1?

<details markdown="1"><summary>Check</summary>

The cross-entropy term for that class is its target probability times the log of the student's probability, so a target of 10^-6 makes the term about a millionth as heavy as one near 1. A higher T lifts those targets so they count.

</details>

## Know this

### The origin: word-level distillation

Kim and Rush apply Hinton's idea to translation. A neural translation model is trained to minimize the negative log-likelihood of each target word given the source sentence and the words before it, so a teacher exists at every position of the sentence. They define the word-level loss for one sentence as a sum over positions j and over every word k in the target vocabulary V:

```text
L_WORD-KD = - sum_j sum_k q(t_j = k | s, t_<j) * log p(t_j = k | s, t_<j)
```

Here q is the teacher, p the student, s the source sentence, and the last argument of each probability is the prefix, the target words before position j. The student can also train on a mixture of this loss and the ordinary word-level negative log-likelihood. They call it word-level knowledge distillation (section 3.1). In an LLM the unit is a token, which is why this track says [token-level distillation](../GLOSSARY.md).

Note what the conditioning is. The prefix comes from the actual target sequence in the training data. The paper's Figure 1 describes it as minimizing cross-entropy between the student and teacher distributions for each word in the actual target sequence. Both models are fed the same fixed prefix and each outputs a distribution for the next word, which is [teacher forcing](../GLOSSARY.md).

On English to German WMT 2014 (Table 1), a student with 2 layers of 500 units scored 14.7 BLEU with greedy decoding and 17.6 with beam search. With word-level distillation it scored 15.4 and 17.7, gains of 0.7 and 0.1. The 4 layer, 1000 unit teacher scored 17.7 and 19.5. The authors tested mixture weights of 0.5 and 0.9 and found 0.5 better. The paper says word-level distillation improves on the baseline, and that its sequence-level method does better, which is the subject of stage 3.

### The loss for an LLM

Three recent papers write the same loss in slightly different forms. They agree on the structure: one divergence between the two next-token distributions at each position, combined over the sequence.

- Gemma 2 (Gemma Team, 2024, section 3.2) minimizes the negative log-likelihood between the teacher's and the student's probabilities, the sum over x of -P_T(x | x_c) log P_S(x | x_c), where x_c is the context.
- GKD (Agarwal et al., 2023, equation 2) averages a divergence over positions: the divergence is summed over the output positions n and divided by the output length L_y.
- Minitron (Muralidharan et al., 2024, section 3) averages over the sequence length l, with a temperature tau in the softmax.

Cross-entropy and forward KL differ by the entropy of the teacher's distribution, which does not depend on the student. Their gradients with respect to the student's parameters are the same, which is why papers use either name for one objective. The sum over the vocabulary is inside each term. So the shape of the computation is a tensor of logits per model with dimensions batch, position and vocabulary, and a divergence taken over the last axis.

```python
import torch.nn.functional as F

def token_kd_loss(student_logits, teacher_logits, mask, T=1.0):
    # logits: (batch, positions, vocab). mask: (batch, positions), 1.0 for real tokens.
    s = F.log_softmax(student_logits / T, dim=-1)
    t = F.log_softmax(teacher_logits / T, dim=-1)
    kl = (t.exp() * (t - s)).sum(dim=-1)        # (batch, positions)
    return (kl * mask).sum() / mask.sum()        # mean over real tokens
```

The teacher's logits come from a forward pass with gradients off. Three choices in that function are decisions, not facts. The mean over real tokens could be a sum, as Kim and Rush write it, and the sum scales with sequence length. The mask matters because padding positions have no meaningful target. And T = 1 is the default because of Minitron's temperature ablation in lesson 3.

### The same arithmetic, runnable

The NumPy version below does the arithmetic of the function above on three positions with four tokens, with no framework needed. The teacher and student logits agree exactly at the third position, which stands for padding.

```python
import numpy as np

def log_softmax(z):
    z = z - z.max(axis=-1, keepdims=True)
    return z - np.log(np.exp(z).sum(axis=-1, keepdims=True))

teacher = np.array([[3.0, 1.0, 0.0, -1.0],
                    [0.0, 2.5, 2.0, -2.0],
                    [1.0, 1.0, 1.0, 1.0]])
student = np.array([[2.0, 1.5, 0.5, -1.0],
                    [0.5, 2.0, 2.0, -1.0],
                    [1.0, 1.0, 1.0, 1.0]])
t, s = log_softmax(teacher), log_softmax(student)
kl = (np.exp(t) * (t - s)).sum(axis=-1)
mask = np.array([1, 1, 0])
print(np.round(kl, 4), round(kl.sum(), 4), round(kl.mean(), 4))
print(round((kl * mask).sum() / mask.sum(), 4))
```

Predict the last number against the mean of the three before you run it. The output on NumPy 2.5:

```text
[0.1998 0.0541 0.    ] 0.2539 0.0846
0.127
```

Averaging over all three positions dilutes the loss with a position that carries no signal. Averaging over the two real tokens gives 0.127.

### What the fixed sequence costs

The sequences are fixed before training, either human text or text the teacher wrote, and the student sees the teacher's distribution only along those sequences. At generation time the student continues from its own tokens, which no distribution here covered. Lesson 14 in stage 5 names this exposure bias, and lesson 15 shows the on-policy fix. The teacher also costs a forward pass for every batch, which Minitron's authors list as the extra overhead of distillation over conventional training (section 4).

## Practice

1. ▢ In the NumPy run, why does the mean over real tokens, 0.127, exceed the mean over all three positions, 0.0846?

<details markdown="1"><summary>Hint</summary>

Count the positions in each denominator, and look at what the third position contributes to the numerator.

</details>

<details markdown="1"><summary>Check</summary>

The third position adds 0 to the numerator but counts in the denominator of the plain mean: 0.2539 / 3 is 0.0846. Masked, the denominator is 2 and 0.2539 / 2 is 0.127. In a real batch with heavy padding the unmasked mean understates the loss, and the understatement changes with the amount of padding.

</details>

2. ▢ In Kim and Rush's word-level loss, which prefix do the teacher and the student both condition on?

    - a) The target words in the training data
    - b) The words the student sampled on its own
    - c) The words the teacher picked by greedy decoding
    - d) The words of the input source sentence

<details markdown="1"><summary>Check</summary>

**a)** The prefix is the actual target sequence, so both models see the same fixed words. It is not (b): that is the on-policy setting of lesson 15. It is not (c): decoding the teacher's own output is the sequence-level method of stage 3. It is not (d): the source sentence is the other conditioning input, s, not the prefix.

</details>

3. ▢ Gemma 2 minimizes a cross-entropy against the teacher's probabilities, and Minitron writes a KL divergence. Why can both describe the same training signal?

<details markdown="1"><summary>Check</summary>

Forward KL equals the cross-entropy minus the teacher's entropy, and the teacher is fixed, so that entropy is a constant with respect to the student's parameters. The two losses differ in value and not in gradient. Check any new paper for which one it means before comparing loss numbers across papers.

</details>

4. ▢ Change `token_kd_loss` so that it applies the temperature and the T squared factor from lesson 3. What two changes, and why did the function already contain one of them?

<details markdown="1"><summary>Check</summary>

The function already divides both sets of logits by T before the log-softmax, so the temperature is in. What is missing is the factor: multiply the returned loss by T ** 2 when it is combined with a hard-label term, so the soft term keeps its weight as T changes. With T = 1 the factor is 1, which is why the function above needs no change at its default.

</details>

5. ▢ A teammate reports that the distillation loss of their LLM run fell by half after they moved to batches padded to a longer length. The model has not changed. What do you check first?

<details markdown="1"><summary>Hint</summary>

Padding positions agree exactly between a model and itself, so they add zero divergence.

</details>

<details markdown="1"><summary>Check</summary>

Whether the mean divides by all positions or only real tokens. With the first, a longer pad length adds positions to the denominator and the number falls without any change in quality. Divide by the mask sum, as the function above does, and compare the two runs again.

</details>

## Real-world reps

- [ ] Run the NumPy snippet. Then change the student's logits at the first position to equal the teacher's and confirm the first entry of the per-position loss falls to 0.
- [ ] Open the GKD paper and find equation 2. Write down, next to it, whether it sums or averages over positions and how that compares with the Kim and Rush sum.
- [ ] Tomorrow: without notes, write the shape of every tensor in `token_kd_loss`, then say what the mask protects.

## Going further

- [Distillation Losses](../reference/distillation-losses.md)
- [Paper: "Sequence-Level Knowledge Distillation", Kim and Rush, 2016](https://arxiv.org/abs/1606.07947)
- [Paper: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Paper: "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
