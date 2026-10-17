---
title: "2. Soft Targets"
description: What the probabilities a teacher gives to wrong answers carry, and why they are a richer training signal than a hard label
type: lesson
---

# Lesson 2. Soft Targets

**Mission link:** The mission asks you to explain why a teacher's soft targets carry more training signal than hard labels, and this lesson is that explanation, with a run you can check it against.
**Primary source:** [Paper: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals and Dean, 2015](https://arxiv.org/abs/1503.02531)
**Prerequisites:** [Lesson 1](0001-what-distillation-buys.md), [Soft targets](../GLOSSARY.md), [Hard label](../GLOSSARY.md), [Logit](../GLOSSARY.md)

## Warm-up

1. ▢ In a distillation, which model's weights change during training, and which model is the training signal?

<details markdown="1"><summary>Check</summary>

Only the [student](../GLOSSARY.md) learns. The [teacher](../GLOSSARY.md) is fixed and supplies the targets. Mixing these up is the usual first error when reading a distillation loss.

</details>

2. ▢ The 800 unit MNIST net made 146 errors alone and 74 when it also matched the 1200 unit net's outputs. What did the 74 show about what the targets carried?

<details markdown="1"><summary>Check</summary>

The targets carried knowledge about how to generalize, learned by the teacher from jittered training data, which the student never saw in its own transfer set. A hard label for each image holds none of that.

</details>

## Know this

### What a hard label throws away

A trained classifier gives most images a probability near 1 for the right class. The tiny probabilities on the wrong classes still differ from image to image. Hinton et al. give an example from MNIST: one version of a 2 may get a probability of 10^-6 of being a 3 and 10^-9 of being a 7, and another version of a 2 may get it the other way round. That says which 2s look like 3s and which look like 7s, a similarity structure over the data. A [hard label](../GLOSSARY.md) says only "2" for both.

The paper's term for the training target built from these probabilities is soft targets. The information they carry is sometimes called dark knowledge, a name that does not appear in this paper. This track says [soft targets](../GLOSSARY.md) for the target and avoids the other phrase.

### The catch: small numbers barely move the loss

The same passage names the problem. Probabilities that close to zero have very little influence on the cross-entropy cost during transfer. Take a student that gives the 2 a probability of 0.98 and the 3 a probability of 0.01, against a teacher with 1.0 and 10^-6. The 2 contributes about 0.0202 to the loss and the 3 about 0.0000046, which is over 4,000 times less. The signal is there and the loss is deaf to it.

Caruana and collaborators, the paper says, avoided this by matching logits with a squared error instead of matching probabilities. Hinton et al.'s more general answer is to raise the temperature until the targets are soft enough to matter, which is lesson 3.

### See it run

The script builds a teacher over five digit classes, then two students. Both predict "2" with the same confidence. Student A swaps the order of 3 and 7 relative to the teacher, and student B keeps the teacher's order.

```python
import numpy as np

def softmax(z, T=1.0):
    z = np.asarray(z, float) / T
    e = np.exp(z - z.max())
    return e / e.sum()

def kl(p, q):
    return float(np.sum(p * np.log(p / q)))

teacher = [9.0, 4.0, 2.0, 0.0, -4.0]    # classes: 2, 3, 7, 8, 0
student_a = [9.0, 1.0, 4.0, 0.0, -4.0]  # same top class, 3 and 7 swapped
student_b = [9.0, 4.0, 2.5, 0.0, -4.0]  # same ranking as the teacher

for T in (1, 5):
    p = softmax(teacher, T)
    print("T =", T)
    for name, z in (("A", student_a), ("B", student_b)):
        q = softmax(z, T)
        ce = -np.log(softmax(z)[0])
        print("  student", name, "hard-label CE %.4f" % ce, "KL(teacher||student) %.4f" % kl(p, q))
```

Predict before you run it: which student does the hard-label cross-entropy against the label "2" prefer, and which does the divergence from the teacher prefer? It prints this, on NumPy 2.5:

```text
T = 1
  student A hard-label CE 0.0072 KL(teacher||student) 0.0177
  student B hard-label CE 0.0083 KL(teacher||student) 0.0001
T = 5
  student A hard-label CE 0.0072 KL(teacher||student) 0.0414
  student B hard-label CE 0.0083 KL(teacher||student) 0.0006
```

The hard label slightly prefers A, the student with the wrong similarity structure. The divergence from the teacher prefers B by a wide margin. The numbers are constructed for the demonstration, so read the direction and not the sizes. The `KL` divergence is the [KL divergence](../GLOSSARY.md) of the teacher's distribution from the student's.

### Why this matters more for a language model

The paper's passage on entropy applies to a language model directly. When the soft targets have high entropy they give much more information per training case than hard targets. A next-token distribution is rarely near one-hot: many continuations are plausible. Minitron's authors say, in an appendix on the distillation loss, that LLM logit distributions have higher entropy than the spiky ones of classification models (Muralidharan et al., 2024, appendix A.3). Their observation is about that setup, but it points the same way.

### Information about a class the student never saw

The paper removed every 3 from the transfer set, so the student never saw one. It still made only 206 test errors, 133 of them on the 1010 test 3s. Most of the errors came from the learned bias of the 3 class being too low. With that bias raised by 3.5, a choice made to optimize overall test performance, it made 109 errors, 14 on 3s, and got 98.6% of the test 3s right. The knowledge of what a 3 looks like arrived through the soft targets of the other digits.

## Practice

1. ▢ In the run above, which student does the hard-label cross-entropy prefer at T = 1, and which does the teacher divergence prefer?

<details markdown="1"><summary>Hint</summary>

Compare the two CE numbers first, then the two KL numbers, and ask what each loss can see.

</details>

<details markdown="1"><summary>Check</summary>

Cross-entropy against the label "2" prefers A (0.0072 against 0.0083). The teacher divergence prefers B (0.0001 against 0.0177). The hard label sees only the probability of "2". A's wrong order of 3 and 7 is invisible to it, and that order is what the soft target carries.

</details>

2. ▢ Why do the teacher's tiny probabilities on wrong classes barely help when the student is trained at temperature 1?

    - a) Only the correct class entry enters the loss
    - b) Wrong class entries are dropped before the loss
    - c) Each term is scaled by its target probability
    - d) The student softmax cannot output very tiny values

<details markdown="1"><summary>Check</summary>

**c)** Each term of the cross-entropy is the target probability times the log of the student's. A target of 10^-6 is weighted a millionth as much as a target near 1. It is not (b): nothing removes them. It is not (a): that describes the hard-label loss, not the soft-target one. It is not (d): a softmax can output 10^-9 without trouble.

</details>

3. ▢ A student trained on a transfer set with no 3s gets 98.6% of the test 3s right once its bias for the 3 class is raised. How can it know what a 3 is?

<details markdown="1"><summary>Check</summary>

The teacher's soft targets on other digits, 2s, 5s and 8s for example, put small probability on 3. Those probabilities teach the student which features raise the score of a 3, without a single 3 as a training example. The learned bias for the class was far too low, so the knowledge was there and the offset was wrong. The result is the paper's, on MNIST, with one adjusted bias.

</details>

4. ▢ A teacher gives a 2 a probability of 1.0 and a 3 a probability of 10^-6. A student gives them 0.98 and 0.01. About how many times smaller is the 3's term in the cross-entropy than the 2's?

<details markdown="1"><summary>Hint</summary>

Each term is the teacher's probability times the negative natural log of the student's.

</details>

<details markdown="1"><summary>Check</summary>

The 2's term is -1.0 * ln(0.98), about 0.0202. The 3's term is -10^-6 * ln(0.01), about 0.0000046. The ratio is about 4,400, so over 4,000 times smaller. This is why raising the temperature, not simply trusting the loss, is the paper's route to making these entries count.

</details>

## Real-world reps

- [ ] Run the script. Then change student A so that the 3 stays above the 7 (for example `[9.0, 3.0, 2.5, 0.0, -4.0]`) and watch the two KL numbers fall toward student B's.
- [ ] Find a classifier you can load, print its softmax for five images at temperature 1, and write down the second and third highest classes. Do they look like the true class's neighbours?
- [ ] Tomorrow: without notes, explain in two sentences why a hard label cannot carry the similarity between a 2 and a 7.

## Going further

- [Distillation Losses](../reference/distillation-losses.md)
- [Paper: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals and Dean, 2015](https://arxiv.org/abs/1503.02531)
- [Paper: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
