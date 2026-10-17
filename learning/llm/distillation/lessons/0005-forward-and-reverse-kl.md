---
title: "5. Forward and Reverse KL"
description: Why forward KL spreads the student over every mode of the teacher and reverse KL makes it commit to one
type: lesson
---

# Lesson 5. Forward and Reverse KL

**Mission link:** The mission asks you to choose between forward and reverse KL, and this lesson gives the two directions, the toy case that separates them, and the papers that disagree about which to use.
**Primary source:** [Paper: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
**Prerequisites:** [Lesson 4](0004-token-level-distillation.md), [Forward KL](../GLOSSARY.md), [Reverse KL](../GLOSSARY.md), [KL divergence](../GLOSSARY.md)

## Warm-up

1. ▢ In `token_kd_loss`, over which axis is the divergence taken, and what does the mask do to the final mean?

<details markdown="1"><summary>Check</summary>

The divergence is taken over the vocabulary axis, the last one, giving one number per position. The mask zeroes the padding positions and the final division by the mask sum averages over real tokens only.

</details>

2. ▢ In lesson 2, a teacher probability of 10^-6 on a wrong class barely moved a cross-entropy loss. Which factor in the term makes it small?

<details markdown="1"><summary>Check</summary>

The term is the teacher's probability times a log ratio, so a target of 10^-6 scales it down by a millionth. Keep that in mind: the direction of the KL decides whose probability does the scaling.

</details>

## Know this

### Two directions of one divergence

The KL divergence is not symmetric. With p the teacher and q the student, the [forward KL](../GLOSSARY.md) is KL(p || q), the sum over tokens of p log(p / q). The [reverse KL](../GLOSSARY.md) is KL(q || p), the sum of q log(q / p). The only difference is whose probability multiplies the log ratio, and that decides what each punishes. GKD (Agarwal et al., 2023, section 2) uses these same names.

Forward KL weights each token by the teacher's probability. A token the teacher likes and the student gives almost no probability costs a lot, because the ratio p / q is huge. A token the teacher gives almost none and the student likes is cheap, since p is small. The student is pushed to put some mass wherever the teacher has mass, which is mode covering.

Reverse KL weights each token by the student's probability. The student is punished for putting mass where the teacher has almost none, because q log(q / p) is large there. Ignoring a teacher mode costs nothing, so the student is free to take one. That is mode seeking.

### Two modes, two students

The teacher below has two equally likely continuations and a little probability on two others. The first student spreads its mass. The second commits to one mode.

```python
import numpy as np

p = np.array([0.49, 0.01, 0.01, 0.49])        # teacher: two modes
students = {
    "spread": np.array([0.25, 0.25, 0.25, 0.25]),
    "commit": np.array([0.97, 0.01, 0.01, 0.01]),
}

def kl(a, b):
    return float(np.sum(a * np.log(a / b)))

for name, q in students.items():
    print(name, "forward %.3f" % kl(p, q), "reverse %.3f" % kl(q, p))
```

Predict which student each direction prefers, then run it. The output on NumPy 2.5:

```text
spread forward 0.595 reverse 1.273
commit forward 1.572 reverse 0.623
```

Forward KL prefers the spread student (0.595 against 1.572), which puts probability on both modes and wastes some on the two rare tokens. Reverse KL prefers the committed student (0.623 against 1.273), which sits on one mode and ignores the other. Neither student matches the teacher. Which failure you want depends on what the student will do next, which is the argument of the next two papers.

### The case for reverse KL

Gu et al. argue that standard distillation objectives minimize an approximated forward KL, which forces the student to cover all modes of the teacher. For classification, with a finite number of classes, both distributions have few modes and that works well. For open-ended generation the teacher can have many more modes than a small student can express. The paper says forward KL then makes the student assign unreasonably high probability to regions where the teacher has almost none, and produces very unlikely samples under the teacher during free-run generation (introduction). Their remedy is reverse KL, which seeks the major modes and gives low probability to the teacher's void regions. In text, they say, the student avoids learning too many long-tail variants of the teacher's distribution and focuses on correctness.

They show the effect on a toy: a Gaussian mixture fitted with a single Gaussian by each divergence (Figure 2). They optimize the reverse KL with a policy gradient on samples from the student, with extra steps for stability, which makes it an on-policy method. Lesson 15 covers it. The loss itself is simple. With the log-probabilities of the earlier snippet, the per-position reverse KL is `(s.exp() * (s - t)).sum(dim=-1)` in place of the forward line.

### The case for choosing

GKD does not pick a side. It makes the divergence a parameter. Its generalized JSD, for a coefficient beta between 0 and 1, is:

```text
JSD(beta)(P || Q) = beta * KL(P || beta*P + (1-beta)*Q) + (1-beta) * KL(Q || beta*P + (1-beta)*Q)
```

With P the teacher, it interpolates between the two directions. The gradients behave like forward KL as beta approaches 0 and like reverse KL as beta approaches 1. It is also bounded even when the supports are disjoint, which KL is not (section 2). On the same toy, with the `jsd` function written from that formula (not in the paper), the three JSD values give a crossover:

| Student | JSD(0.1) | JSD(0.5) | JSD(0.9) |
|---|---|---|---|
| spread | 0.055 | 0.177 | 0.091 |
| commit | 0.102 | 0.189 | 0.058 |

At beta = 0.1 the spread student wins and at beta = 0.9 the committed one does, which matches the direction each end is said to prefer. At 0.5 they are close. The numbers come from the toy, not from any run.

GKD's experiments say the best divergence depends on the task. On XSum summarization, moving from forward KL to reverse KL through the JSD family decreased the diversity of the output (Figure 4). On the ablations, mode-seeking divergences did better when evaluated with temperature sampling, and the choice mattered little with greedy decoding (section 4.1). On task-agnostic instruction tuning with FLAN, on-policy GKD with reverse KL substantially outperformed supervised KD and ImitKD, and reverse KL did much better than forward KL there (Figure 10). On GSM8K, forward KL performed quite well, and reverse KL did too, especially when training on a fixed dataset only. The paper's summary is that the divergence has to be chosen by the diversity and quality trade-off on the task.

The TRL implementation exposes this choice as `beta` in `GKDConfig`: at 0.0 the loss is the KL divergence, at 1.0 the inverse KL, with a default of 0.5 ([TRL GKD documentation](https://huggingface.co/docs/trl/main/en/gkd_trainer), read for this lesson).

### Evidence the other way

Minitron's authors retrain pruned base models from their unpruned teacher and tested the directions directly. On a depth-pruned Minitron 8B, the logit loss with forward KLD reached an LM loss of 2.155 against 2.665 for reverse KLD (their Table 16, appendix A.3). On the previous generation Nemotron-3 8B, the combined loss gave 2.117 with forward KLD and 2.140 with reverse (Table 15). They note that prior work found reverse KLD a better fit for supervised fine-tuning and instruction following, that Agarwal et al. say the choice is task-dependent, and that forward KLD is the best choice for their base-model setting (section 4).

So the evidence is not one rule. Reverse KL has the support of instruction-tuning results on small students in GKD, and forward KL has the support of retraining base models in Minitron. Both are single papers on their own models.

## Practice

1. ▢ In the two mode run, which student does forward KL prefer, and which does reverse KL prefer?

<details markdown="1"><summary>Hint</summary>

Ask which student has put some probability on both of the teacher's big tokens, and which ignores one of them.

</details>

<details markdown="1"><summary>Check</summary>

Forward KL prefers the spread student (0.595 against 1.572) and reverse KL the committed one (0.623 against 1.273). Forward KL punishes the committed student for a q near 0.01 where p is 0.49. Reverse KL punishes the spread student for putting 0.25 where p is 0.01.

</details>

2. ▢ What is the paper's argument against forward KL for open-ended generation?

    - a) The loss cannot be computed from the full distribution
    - b) The student must cover more modes than it can express
    - c) The gradient always vanishes when the teacher is very confident
    - d) The teacher's logits must be softened before it can work

<details markdown="1"><summary>Check</summary>

**b)** A teacher over text has many more modes than a small student can express, and forward KL forces the student to cover them, so it puts mass on regions the teacher considers void. It is not (a): both directions can be computed from the full distributions. It is not (c): that is the lesson 2 observation about small probabilities, a different problem. It is not (d): temperature is a separate choice from the direction.

</details>

3. ▢ Using the JSD table, which student does JSD(0.9) prefer, and does that match GKD's statement that beta near 1 behaves like reverse KL?

<details markdown="1"><summary>Check</summary>

The committed student (0.058 against 0.091), and yes: reverse KL also prefers it. At beta = 0.1 the spread student wins as forward KL would. The table is a toy check of the paper's description, not a result from a training run.

</details>

4. ▢ Minitron's Table 16 gives an LM loss of 2.155 with forward KLD and 2.665 with reverse KLD for a depth-pruned 8B student. Does this contradict MiniLLM and GKD?

<details markdown="1"><summary>Check</summary>

No, not directly. MiniLLM and GKD report instruction-following and summarization results on small students, with the reverse direction often on student-sampled sequences. Minitron retrains a pruned base model on a pretraining style blend and measures LM loss. The setting differs in the task, the student's starting point and the metric, so the evidence supports a task-dependent choice, as GKD says. Test both on your own task before committing.

</details>

5. ▢ Which divergence is deaf to a tiny teacher probability, as in lesson 2, and which one punishes the student for mass placed there?

<details markdown="1"><summary>Check</summary>

Forward KL is nearly deaf to a tiny teacher probability because p multiplies the log ratio, which is the lesson 2 problem. Reverse KL punishes student mass placed where the teacher has almost none, because q multiplies the log ratio. The two directions answer opposite questions about the same small number.

</details>

## Real-world reps

- [ ] Run the snippet, then change the teacher to `[0.45, 0.05, 0.05, 0.45]` and see whether the preferences of the two directions change.
- [ ] Open the GKD paper's Appendix A.7 and read the caption of the figure on mode-seeking against mode-covering KL. Write one sentence on what the unimodal student does under each direction.
- [ ] Tomorrow: without notes, say which direction each of MiniLLM, GKD and Minitron recommends and for what setting.

## Going further

- [Distillation Losses](../reference/distillation-losses.md)
- [Paper: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
- [Paper: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Documentation: "Generalized Knowledge Distillation Trainer", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gkd_trainer)
- [Paper: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
