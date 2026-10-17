---
title: "17. Fidelity and Generalization"
description: Why a student that generalizes well can still disagree with its teacher, and which of the two you need
type: lesson
---

# Lesson 17. Fidelity and Generalization

**Mission link:** The mission asks you to predict what a student will inherit, and to measure what it lost, which starts with separating how closely it copies the teacher from how well it does the task.
**Primary source:** [Paper: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945), sections 3 to 7
**Prerequisites:** [Lesson 3](0003-temperature.md), [Lesson 16](0016-on-policy-distillation-in-practice.md), [Fidelity](../GLOSSARY.md), [Forward KL](../GLOSSARY.md), [Combined loss](../GLOSSARY.md)

## Warm-up

1. ▢ The combined loss adds two terms. Which one pulls the student toward the teacher and which toward the labels?

<details markdown="1"><summary>Check</summary>

The divergence from the teacher's [soft targets](../GLOSSARY.md) pulls it toward the teacher, and the cross-entropy against the [hard labels](../GLOSSARY.md) pulls it toward the data. A mixing coefficient weights them.

</details>

2. ▢ Qwen3's on-policy phase minimises KL between student and teacher on the student's own samples. Which direction of KL is the teacher-to-student form, and what does it penalise?

<details markdown="1"><summary>Check</summary>

KL(teacher || student) is forward KL. It penalises the student for putting little probability where the teacher puts much, so it pushes the student to cover everything the teacher covers.

</details>

3. ▢ In lesson 16, Qwen3's student beat the RL-trained checkpoint on benchmarks. Does that tell you the student's predictions match its teacher's?

<details markdown="1"><summary>Check</summary>

No. Benchmark scores measure the task. Whether the student agrees with its teacher's predictions is a separate measurement, and this lesson is about why the two can come apart.

</details>

## Know this

### Two things distillation could mean it improved

Stanton et al. separate two quantities that the distillation literature usually blurs. **Fidelity** is the ability of a student to match the teacher's predictions. **Generalization** is the student's performance on unseen, in-distribution data. They measure fidelity with two numbers on the same inputs, both defined in section 3.2:

| Metric | What it measures |
|---|---|
| Average top-1 agreement | The fraction of inputs where student and teacher pick the same top label |
| Average predictive KL | The mean KL(teacher || student), sensitive to every class, not only the top one |

Accuracy cannot stand in for agreement. The paper's own example: three independent models with 55%, 75% and 95% test accuracy. The first and third can agree on at most 60% of inputs, while the second and third agree on at least 70%, yet no one would say the 75% model is a better distillation of the 95% model, since they were trained independently.

### The control for "they agree because both are good"

Agreement rises just because models are accurate. To separate a general improvement from a specific improvement in matching, the paper also trains a second student, distilled by the identical procedure from an independent teacher. If both students agree with the first teacher about equally, the agreement is explained by generalization. If the real student agrees with its own teacher more, that is fidelity.

### What they found

Their experiments are mostly image classification with ResNets on CIFAR-100, plus MNIST, ImageNet and one text classification dataset (IMDB sentiment) in the appendix. They are not experiments on language-model generation, so read them as a result about distillation in general and then test it on your own LLM pair.

| Finding | Evidence in the paper |
|---|---|
| Easy case: matching works | LeNet-5 on MNIST reached over 99% top-1 test agreement with enough distillation data (section 4.1) |
| Harder case: it often does not | ResNet-56 self-distillation on CIFAR-100 stayed below 80% test agreement even with the largest distillation set (section 6.1) |
| Better generalization can come with worse fidelity | In self-distillation, enlarging the data with GAN samples raised fidelity and lowered test accuracy, because a student that fails to match the teacher can generalize better (Figure 1a, section 4.2) |
| With a stronger teacher the two align | Distilling a 3-component ensemble, fidelity and test accuracy both rose with more data (Figure 1b) |
| It is not capacity | Low fidelity appears even in self-distillation, where the student has the teacher's own capacity, and enlarging the student barely changed it when distilling an ensemble (section 4.4) |
| It is not one architecture, scale or domain | Similar results with VGG, on ImageNet and on IMDB (section 4.4) |

### The explanation: optimization

The paper tests two hypotheses for the failure. One is identifiability: the distillation data is too small to pin down the teacher's function. More data helps test agreement, so this is part of the story. The other is optimization: the student cannot even match the teacher on the distillation data it trains on.

The second holds up. With 50k synthetic images added, a student with the same capacity as its teacher reached only 95% agreement on the distillation data itself. With heavy data augmentation, train agreement was between 80% and 90% for three augmentations and dropped to about 60% in self-distillation for the combination of all three (section 6.1). Training longer helped a little: for a ResNet-20 self-distillation, 5,000 epochs of SGD reached 83.3% train agreement against 78.95% at 300 epochs, and switching to Adam reduced fidelity (section 6.2).

The paper's summary is a trade-off. Adding examples beyond the teacher's training data gives the student more teacher labels to identify the function, and also makes an already hard optimization problem harder. In the paper's words, good fidelity is directly aligned with solving an exceptionally difficult optimization problem, where ordinary training is saved by not needing to solve it well.

### What this changes for you

If you evaluate a distilled LLM only by task accuracy, you cannot tell how much of the teacher you inherited. Two students can score the same and differ greatly in agreement. Stage 8 builds the full measurement, and the minimum habit is this: report agreement with the teacher on held-out inputs next to task quality, and compare against a student distilled from a different teacher or trained without one.

Fidelity is not always the goal. The paper's own self-distillation result shows a student that fails to match its teacher yet generalizes better. Fidelity matters when you want to inherit properties beyond accuracy: the paper lists transferring calibration or robustness so a smaller model can safely replace a larger one (section 4.3). It also found that the highest-fidelity student was always the best calibrated when distilling ensembles.

A pure-Python sketch of the two measurements, which prints the output shown in the comments:

```python
import math

def softmax(z):
    m = max(z)
    e = [math.exp(v - m) for v in z]
    s = sum(e)
    return [v / s for v in e]

def argmax(z):
    return max(range(len(z)), key=lambda i: z[i])

def kl(p, q):
    return sum(pi * (math.log(pi) - math.log(qi)) for pi, qi in zip(p, q))

# One row per example: logits over three classes, plus the true label.
teacher = [[3.0, 1.0, 0.0], [0.5, 2.5, 0.0], [0.0, 0.5, 3.0], [1.0, 2.0, 0.0]]
student = [[2.0, 1.5, 0.0], [0.0, 1.0, 2.0], [0.0, 0.5, 2.5], [2.0, 1.5, 0.0]]
labels = [0, 1, 2, 0]

agreement = sum(argmax(t) == argmax(s) for t, s in zip(teacher, student)) / len(labels)
mean_kl = sum(kl(softmax(t), softmax(s)) for t, s in zip(teacher, student)) / len(labels)
teacher_acc = sum(argmax(t) == y for t, y in zip(teacher, labels)) / len(labels)
student_acc = sum(argmax(s) == y for s, y in zip(student, labels)) / len(labels)

print(f"agreement {agreement:.2f}  mean KL {mean_kl:.3f}")      # agreement 0.50  mean KL 0.321
print(f"teacher accuracy {teacher_acc:.2f}  student accuracy {student_acc:.2f}")  # both 0.75
```

Both models score 0.75, and they agree on only half the inputs.

## Practice

1. ▢ A teacher has 93% accuracy and a student has 91%, on the same test set. Between what bounds must their top-1 agreement lie?

<details markdown="1"><summary>Hint</summary>

The student is wrong on 9% of inputs and the teacher on 7%. How much can the two sets of mistakes overlap, and how little?

</details>

<details markdown="1"><summary>Check</summary>

Between 84% and 98%. They agree wherever both are right, and the worst case is that their errors never overlap, which leaves 100 minus 7 minus 9, so 84% at least. They can agree on at most 98%: the student is wrong on 2 percentage points more inputs than the teacher, so at least 2% of inputs have the teacher right and the student wrong. Matching accuracy tells you very little about agreement, which is the lesson's point.

</details>

2. ▢ In the paper's control, why train a second student from an independent teacher?

    - a) It verifies the teacher trained correctly
    - b) It separates fidelity from shared skill
    - c) It raises the first student's accuracy
    - d) It reduces the compute needed overall

<details markdown="1"><summary>Check</summary>

**b)** If a student agrees with an independent teacher about as much as with its own, the agreement is explained by both being good, not by copying. (a) is not tested here. (c) and (d) are false: the second student is a measurement tool and changes nothing about the first.

</details>

3. ▢ In CIFAR-100 self-distillation with a ResNet-56 student and teacher, the distillation set is enlarged with GAN-generated images. Predict the direction of student fidelity and of student test accuracy.

<details markdown="1"><summary>Hint</summary>

Self-distillation is the case where the student already has the capacity to match the teacher, and the paper notes that failing to match can itself help.

</details>

<details markdown="1"><summary>Check</summary>

Fidelity increases and test accuracy decreases (Figure 1a). In self-distillation the student that matches the teacher less closely generalizes better, so more fidelity costs accuracy. With a 3-ensemble teacher the direction flips: both rise (Figure 1b). Which one applies to you depends on whether your teacher generalizes much better than an independently trained student.

</details>

4. ▢ A distilled student with the teacher's own architecture still disagrees with it on 20% of held-out inputs. List the hypotheses the paper tests and say which it supports.

<details markdown="1"><summary>Check</summary>

Student capacity, architecture, dataset scale, data domain, identifiability and optimization (section 4.4). The paper rules out capacity, since the student has the teacher's capacity, and the others on its evidence. It supports optimization as a key reason: the student does not match the teacher even on its own training inputs. Identifiability is part of the picture too, since more data raised test agreement. The paper found the large agreement gap in image tasks, so check it on your LLM pair before assuming it carries over.

</details>

5. ▢ Which of these LLM measurements is the closest analogue of the paper's average predictive KL, and what does it need that agreement does not?

<details markdown="1"><summary>Check</summary>

The mean per-position KL(teacher || student) on held-out sequences, which is the forward-KL token-level distillation loss from stage 2 evaluated on data not used for training. It needs the teacher's full distribution at each position, which agreement on the top token does not. Top-token agreement is the cheaper analogue of top-1 agreement. This mapping from the paper's classification setting to token level is my adaptation, not an experiment from the paper.

</details>

## Real-world reps

- [ ] Run the sketch above, then change one student logit row so the two models disagree on a different example while accuracy stays at 0.75. Note what happened to agreement and to mean KL.
- [ ] Read section 3.2 of the Stanton paper and write the formula for average top-1 agreement in one line. Then write what the control student s-prime tells you.
- [ ] Tomorrow: without notes, state the difference between fidelity and generalization, one case where more fidelity lowers accuracy, and the paper's main explanation for low fidelity.

## Going further

- [What the Student Inherits](../reference/what-the-student-inherits.md)
- [Paper: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
