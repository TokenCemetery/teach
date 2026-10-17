---
title: "3. Temperature"
description: Softening both distributions with a temperature, the T squared correction, and mixing in the hard-label loss
type: lesson
---

# Lesson 3. Temperature

**Mission link:** The mission asks you to set the temperature and loss weights of a distillation run, and this lesson gives the three pieces of that setting: the temperature, the T squared factor, and the weight on the hard-label loss.
**Primary source:** [Paper: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals and Dean, 2015](https://arxiv.org/abs/1503.02531)
**Prerequisites:** [Lesson 2](0002-soft-targets.md), [Temperature](../GLOSSARY.md), [Combined loss](../GLOSSARY.md), [Logit](../GLOSSARY.md)

## Warm-up

1. ▢ At temperature 1, a student gave a 2 a probability of 0.98 and a 3 a probability of 0.01, and the teacher gave them 1.0 and 10^-6. Why did the 3 barely move the loss?

<details markdown="1"><summary>Check</summary>

Each cross-entropy term is the target probability times the log of the student's probability. The 3's target of 10^-6 makes its term over 4,000 times smaller than the 2's, so the information in it is present and almost unheard.

</details>

2. ▢ What does a hard label say about the similarity of a 2 to a 7, and where is that information in a distillation?

<details markdown="1"><summary>Check</summary>

It says nothing. The similarity lives in the small probabilities the [teacher](../GLOSSARY.md) puts on the wrong classes, the [soft targets](../GLOSSARY.md).

</details>

## Know this

### The temperature

The paper replaces the softmax with one that divides every [logit](../GLOSSARY.md) by a temperature T before normalizing: q_i = exp(z_i / T) / sum_j exp(z_j / T). T is normally 1. A higher T gives a softer distribution over classes. The paper's recipe is to raise T until the teacher produces suitably soft targets, then train the student at the same high T to match them. After training the student uses T = 1.

```python
import numpy as np

def softmax(z, T=1.0):
    z = np.asarray(z, float) / T
    e = np.exp(z - z.max())
    return e / e.sum()

logits = [9.0, 4.0, 2.0, 0.0, -4.0]   # classes: 2, 3, 7, 8, 0
np.set_printoptions(suppress=True, precision=4)
for T in (1, 2, 5, 20):
    print("T =", T, softmax(logits, T))
```

Predict the probability of the first class at T = 5 before running it. The output on NumPy 2.5:

```text
T = 1 [0.9923 0.0067 0.0009 0.0001 0.    ]
T = 2 [0.889  0.073  0.0268 0.0099 0.0013]
T = 5 [0.5394 0.1984 0.133  0.0892 0.0401]
T = 20 [0.2745 0.2138 0.1934 0.175  0.1433]
```

At T = 1 the wrong classes sum to under 1%. At T = 5 they carry nearly half the probability, and the order 3, 7, 8, 0 is still visible. At T = 20 the distribution is almost flat, and the differences the student has to match are small.

### Why the loss is multiplied by T squared

The gradient of the cross-entropy with respect to a student logit z_i, when the teacher has logits v_i and both use temperature T, is (1/T)(q_i - p_i). The paper's equation 2 gives it. If T is large compared with the logits and the logits are zero-meaned per example, the paper shows this is approximately (1/(N T^2))(z_i - v_i), where N is the number of classes. So in the high temperature limit, distillation is equivalent to minimizing 1/2 (z_i - v_i)^2, the logit matching of Caruana and collaborators. Matching logits is a special case of distillation.

The factor that matters in practice is the 1/T^2. The paper says the magnitudes of the soft target gradients scale as 1/T^2, so it is important to multiply them by T^2 when using both hard and soft targets. That keeps the relative contributions of the two roughly unchanged when you change T while experimenting with the other settings.

```python
import numpy as np

def softmax(z, T=1.0):
    z = np.asarray(z, float) / T
    e = np.exp(z - z.max())
    return e / e.sum()

teacher = np.array([9.0, 4.0, 2.0, 0.0, -4.0])
student = np.array([6.0, 5.0, 0.0, 1.0, -2.0])
for T in (1, 2, 5, 10, 20):
    grad = (softmax(student, T) - softmax(teacher, T)) / T
    print(T, "%.4f" % np.abs(grad).max(), "%.4f" % (np.abs(grad).max() * T**2))
```

The output shows the largest gradient entry shrinking from 0.2663 at T = 1 to 0.0017 at T = 20. Multiplied by T squared it stays between 0.64 and 0.84 from T = 2 up to T = 20. The T = 1 row is not a fair comparison, since the high temperature approximation does not hold there.

### The combined loss

When correct labels exist for the transfer set, the paper finds that training on the soft targets alone is improved by also training the student to produce the correct labels. It tried modifying the soft targets with the labels and found a weighted average of two objectives better. The first is the cross-entropy with the soft targets, computed at the high T. The second is the cross-entropy with the correct labels, computed from the same student logits at T = 1. The paper found the best results generally with a considerably lower weight on the second objective.

Written out, with the notation of this track and not the paper's, with lambda the weight on the soft term:

```text
loss = lambda * T^2 * CE(teacher at T, student at T) + (1 - lambda) * CE(label, student at 1)
```

That is a [combined loss](../GLOSSARY.md). The paper's speech experiments used a relative weight of 0.5 on the hard-label term, and temperatures of 1, 2, 5 and 10. The reason for the small hard-label term is practical: the student usually cannot match the soft targets exactly, and the paper says erring toward the correct answer turns out to be helpful.

DistilBERT follows the same pattern. It applies a softmax with temperature to teacher and student during training, sets T to 1 at inference, and adds its own terms to the soft-target loss as a linear combination with the masked language modeling loss and a cosine embedding loss.

### Choosing T

The paper gives two observations on MNIST. When the distilled net had 300 or more units in each of two hidden layers, all temperatures above 8 gave fairly similar results. When the layers were cut to 30 units, temperatures from 2.5 to 4 worked significantly better than higher or lower ones. The authors suggest that, when the student is too small to capture all of the teacher's knowledge, ignoring the very negative logits that a lower temperature discounts can help.

Do not carry a temperature from a classifier to a language model. Minitron's authors tried temperatures 0.1, 0.5, 1.0 and 3.0 when retraining a pruned LLM from its teacher and report the best results at 1.0 (appendix A.3). They give a reason for including values below 1: LLM logit distributions have higher entropy than the spiky ones of vision models, so they expected softening to matter less. A second, larger study agrees. Busbridge et al. (2025) swept the temperature from 0.5 to 10 for students of 198M to 1.82B parameters, each distilled from a teacher of 546M to 7.75B, and found the best performance at 1 across all scales (appendix G.2). Temperatures above 3 hurt, and the smaller students suffered most. In appendix B.3 they say that, contrary to the literature they cite, the optimal temperature is one, and they hypothesize the difference is that earlier work used repeated tokens while their setup does not repeat data. The hypothesis is theirs and the paper does not test it here. Both findings are one lab's pretraining-style setups, so read them as a strong reason to include T = 1 in any sweep, not as a proof that higher temperatures never help.

Minitron's ablation is one setup too. In their final recipe they also found the logit loss alone better than a weighted mix with the language modeling loss, which is a reminder that the weight is a setting to test and not a constant.

## Practice

1. ▢ Using logits 9, 4, 2, 0 and -4, about what probability does the first class get at T = 5?

    - a) About 0.99
    - b) About 0.54
    - c) About 0.20
    - d) About 0.01

<details markdown="1"><summary>Hint</summary>

Divide the logits by 5, exponentiate each, and divide the first by the sum of all five.

</details>

<details markdown="1"><summary>Check</summary>

**b)** The scaled logits are 1.8, 0.8, 0.4, 0 and -0.8. Their exponentials are about 6.05, 2.23, 1.49, 1.00 and 0.45, which sum to about 11.22, and 6.05 / 11.22 is 0.54. Choice (a) is the T = 1 answer. Choice (c) is the second class, 0.198 at T = 5, not the first.

</details>

2. ▢ You raise T from 4 to 8 and change nothing else. Why does the paper multiply the soft term by T squared?

    - a) To cancel out the teacher's own temperature setting
    - b) To make sure soft targets sum to one
    - c) To raise the student's confidence at test time
    - d) To keep soft and hard gradients in balance

<details markdown="1"><summary>Check</summary>

**d)** The soft gradients shrink as 1/T^2, so without the factor the soft term would fade against the hard term as T grew. It is not (b): the softmax already normalizes. It is not (c): at inference the student runs at T = 1 and nothing is multiplied. It is not (a): teacher and student share the same T and neither is cancelled.

</details>

3. ▢ In the paper's combined loss, which term runs at the high temperature, which runs at T = 1, and which usually gets the lower weight?

<details markdown="1"><summary>Check</summary>

The cross-entropy with the teacher's soft targets runs at the high T, using the student's logits divided by T. The cross-entropy with the correct labels runs on the same logits at T = 1. The paper found the best results generally with a considerably lower weight on the hard-label term. The weights are the setting you tune, so say which one a result used.

</details>

4. ▢ A colleague copies the MNIST setting of T = 20 into an LLM distillation and gets a worse student. What in this lesson suggests why, and what should they do?

<details markdown="1"><summary>Check</summary>

Minitron's ablation over 0.1, 0.5, 1.0 and 3.0 and the Busbridge sweep from 0.5 to 10 both found the best results at 1, and Minitron's authors say LLM logit distributions have higher entropy than the spiky ones of vision models. At T = 20 the targets in the snippet above are almost flat, so the differences the student must learn are small. They should run a short sweep that includes T = 1 against their own teacher and student. Both findings come from one setup each, so they are a place to start, not a rule.

</details>

5. ▢ In the paper's MNIST experiments, which student was more sensitive to the choice of temperature, the one with 300 or more hidden units or the one with 30, and what range worked for the sensitive one?

<details markdown="1"><summary>Check</summary>

The 30 unit student. Temperatures from 2.5 to 4 worked significantly better than higher or lower for it, while with 300 or more units everything above 8 gave fairly similar results. The paper reads this as ignoring very negative logits helping when the student is too small to hold all the teacher's knowledge.

</details>

## Real-world reps

- [ ] Run both scripts. Change the temperatures to 3 and 8 in the second one and check that the last column stays in the same range.
- [ ] Write the combined loss as a NumPy function of the student logits, teacher logits, label index, T and lambda, and check that with lambda = 0 it equals the plain cross-entropy on the label.
- [ ] Tomorrow: without notes, state the formula of the softmax with temperature, say which terms of the combined loss run at which temperature, and say why the T squared factor is there.

## Going further

- [Distillation Losses](../reference/distillation-losses.md)
- [Paper: "Distilling the Knowledge in a Neural Network", Hinton, Vinyals and Dean, 2015](https://arxiv.org/abs/1503.02531)
- [Paper: "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter", Sanh et al., 2019](https://arxiv.org/abs/1910.01108)
- [Paper: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [Paper: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
