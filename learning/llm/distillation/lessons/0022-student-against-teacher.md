---
title: "22. Student Against Teacher"
description: Measuring agreement with the teacher separately from task quality, one capability at a time
type: lesson
---

# Lesson 22. Student Against Teacher

**Mission link:** The mission asks you to measure what a student lost against its teacher, and the first step is to stop treating "agrees with the teacher" and "does the task well" as one number.
**Primary source:** [Paper: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945), sections 3.2 and 4 to 5
**Prerequisites:** [Lesson 17](0017-fidelity-and-generalization.md), [Lesson 18](0018-the-imitation-gap.md), [Fidelity](../GLOSSARY.md), [Top-1 agreement](../GLOSSARY.md), [Imitation gap](../GLOSSARY.md)

## Warm-up

1. ▢ Lesson 17 said a student that generalizes well can still disagree with its teacher. Which of the two did the lesson say you need, and what decides it?

<details markdown="1"><summary>Check</summary>

It depends on what the student is for. If you need the teacher's behaviour reproduced, as in a replacement that others depend on, fidelity is the goal. If you need a model that does the task well, task quality is, and a student can beat a flawed teacher by disagreeing with it. Neither stands in for the other.

</details>

2. ▢ Lesson 18 gave the imitation gap. What does a student imitate fastest, and what does a human preference rating reward?

<details markdown="1"><summary>Check</summary>

It imitates style fastest: fluent, confident, well-structured answers. A preference rating rewards how an answer reads, so a student can score well on it while lagging on capability. Capability is slower to copy.

</details>

3. ▢ Lesson 21 costed a teacher's scoring pass. Which per-token quantity from that pass would you also need to measure fidelity, and what extra cost does using it add?

<details markdown="1"><summary>Check</summary>

The teacher's output distribution (or its top choice) at each position, which the scoring pass already produces. Measuring fidelity means running the teacher over the evaluation prompts as well, a small extra cost against training, because the evaluation set is far smaller than the training set.

</details>

## Know this

### Two things to measure

[Fidelity](../GLOSSARY.md) is how closely a student's predictions track its teacher's on the same inputs. Task quality is how well the student does the job, judged against the right answer. Stanton et al. define two fidelity metrics (section 3.2), and both carry over to a language model position by position:

- **[Top-1 agreement](../GLOSSARY.md):** the share of inputs on which the student's highest-probability answer is the teacher's highest-probability answer.
- **Average predictive KL:** the mean KL divergence from the teacher's distribution to the student's, sensitive to every answer, not only the top one.

The paper defines both for classifiers. Applying them to an LLM means scoring both models' next-token distributions on the same prefixes of held-out prompts, which is this track's adaptation and not something the paper ran. Decide up front which prefix you use: the teacher's text, which isolates the prediction, or each model's own generation, which also measures how the two diverge once they have chosen different words.

### Why they come apart

Stanton et al. give three results that explain why a student's agreement and its task quality can move independently.

First, agreement is bounded by accuracy. Their example (section 3.2): two independent models scoring 55 percent and 95 percent can agree on at most 60 percent of points. A measured agreement of 60 percent between those two says nothing about distillation. They add a control for exactly this reason: also measure a student distilled the same way from an independent teacher, and compare the two agreements. If both students agree with the teacher about equally, the agreement comes from both generalizing well, not from the distillation.

Second, a student can beat its teacher by failing to copy it. In self-distillation on CIFAR-100, where the student has the teacher's architecture, the student's accuracy can exceed the teacher's, which the paper notes is possible only because distillation fails: a perfect copy could not do better (sections 4.1 and 4.2). In that experiment, raising fidelity lowered the student's accuracy when the distillation set was small.

Third, higher fidelity does not always buy higher accuracy even when the teacher is far better. In section 5 they split CIFAR-100, distil one student on the teacher's own training half (s0) and one on unseen data (s1). The student on unseen data agrees with the teacher more, yet the student on the teacher's data has the higher test accuracy. The paper's own summary is that the gain in fidelity did not carry through to replicating the teacher's accuracy.

They also report that it is hard to reach high fidelity at all. On MNIST with LeNet-5 the student reached over 99 percent top-1 test agreement (section 4.1). On CIFAR-100 with ResNet-56 students, the best test agreement they report is about 86 percent, with mixup augmentation (section 5).

Scope: these are mostly image-classification experiments, with text classifiers in the appendix. They show that the two quantities are separable. They are not measurements of an LLM, and no agreement figure from them is a target for yours.

### Why a preference rating is the wrong stand-in

Gudibande et al. fine-tuned LLaMA models of 7B and 13B parameters on ChatGPT outputs and compared two kinds of evaluation. Crowdworkers rated about 70 percent of the imitation models' outputs as equal to or better than ChatGPT's (their Figure 1). On targeted benchmarks, the imitation models closed little to none of the gap between the base model and ChatGPT for tasks the imitation data did not heavily cover.

Their Table 1 shows it per capability, using Natural Questions as the task:

| Model | Imitation data | NQ score |
|---|---|---|
| LLaMA 7B | none | 17 |
| LLaMA 7B | ShareGPT-Mix (broad) | 10 |
| LLaMA 7B | NQ-Synthetic (targeted) | 22 |
| LLaMA 13B | none | 20 |
| LLaMA 13B | ShareGPT-Mix (broad) | 15 |
| LLaMA 13B | NQ-Synthetic (targeted) | 27 |
| ChatGPT | not applicable | 31 |

The broad imitation data lowered the NQ score of both sizes, and targeted data raised it to within four points of the teacher at 13B. The paper's explanation for the rating gap is style: imitation models are fluent and confident, and a rater without domain expertise or time to check facts misses the errors. They also found, in their Table 2, that the style of outputs grew more similar to ChatGPT's as imitation data was added, which is the same effect measured on the output text.

The lesson for measuring is not that preference ratings are useless. It is that a single aggregate, whether a rating or an average accuracy, hides the capabilities that moved in opposite directions.

### One capability at a time

So the measurement is a grid. Pick the capabilities you care about, such as short factual answers, arithmetic, code, instruction following and refusals. For each, compute two columns: agreement with the teacher on prompts of that kind, and task quality against the correct answer on the same prompts. A student can look high on the first and low on the second for some rows and the reverse for others, and the pattern is what tells you what was and was not transferred.

| Capability | Agreement with teacher | Task quality, student | Task quality, teacher | Reading |
|---|---|---|---|---|
| Hypothetical row A | High | Near teacher | High | Copied well |
| Hypothetical row B | High | Far below teacher | High | Copied the style, lost the capability |
| Hypothetical row C | Low | Above teacher | Moderate | Disagrees, and the teacher was the weaker one |

The rows are an illustration of how to read the grid, not data from a source. Lesson 23 adds the missing column, a model of the same size trained without distillation, which this grid cannot judge on its own.

## Practice

1. ▢ A teacher scores 90 percent accuracy on a task. An independent model scores 70 percent. What is the highest top-1 agreement the two can have, and what does that imply for reading a student's agreement score?

<details markdown="1"><summary>Hint</summary>

Two models can agree on a point only if they are both right or both wrong. Work out the most overlap the accuracies allow, following the paper's 55 and 95 example.

</details>

<details markdown="1"><summary>Check</summary>

At most 80 percent, since the 20-point accuracy gap forces them to disagree on at least 20 percent of points. So a student whose accuracy is 70 percent cannot show agreement above 80 percent with this teacher, and a 75 percent agreement means something different from the same figure for a student at 88 percent. Compare a student's agreement with an independent student's from the paper's control before drawing conclusions.

</details>

2. ▢ A student has 94 percent top-1 agreement with its teacher on general chat prompts and 61 percent on multi-step arithmetic prompts. The teacher's arithmetic accuracy is 78 percent. What do you measure next before saying anything about the student's arithmetic?

<details markdown="1"><summary>Hint</summary>

The agreement number says how often the two match, not how often either is right.

</details>

<details markdown="1"><summary>Check</summary>

The student's arithmetic accuracy against the correct answers, on the same prompts, plus the teacher's per-prompt correctness. If the student's accuracy is 61 percent and the teacher's is 78 percent, the gap is a capability loss. If the two disagree mainly where the teacher is wrong, the student may be fine. The 94 percent on chat says only that style transferred, which the imitation gap predicts.

</details>

3. ▢ Which result most directly shows that fidelity and task quality can separate?

    - a) A student's agreement with its teacher fell as heavy augmentation was applied to its inputs.
    - b) A student trained on more distillation data reached higher test agreement with its teacher.
    - c) A student with the teacher's architecture reached the teacher's accuracy at some data size.
    - d) A student distilled from unseen data agreed more with its teacher but was less accurate.

<details markdown="1"><summary>Check</summary>

d). It is the s1 versus s0 result of section 5: higher fidelity with lower test accuracy. b) shows fidelity rising with data, which is expected and does not separate the two. c) is a statement about accuracy alone. a) is a result about how agreement falls under augmentation, which reports a fidelity change without a task-quality comparison.

</details>

4. ▢ A model card says a distilled 3B model "is rated nearly as good as the 70B by human raters". Using Gudibande et al., list two follow-up questions you would ask before accepting that the student kept the 70B's capabilities.

<details markdown="1"><summary>Check</summary>

Which prompts the raters saw, and whether any rater could check facts or code, since style can win a rating the capability would not. And what the student scores on targeted per-capability benchmarks against both the teacher and the undistilled base, including tasks the distillation data barely covered. A rating that agrees with benchmarks is evidence. A rating alone is not.

</details>

5. ▢ Lesson 19 covered capacity. A student matches its teacher's top-1 answer on 97 percent of easy prompts and 52 percent on hard ones. Name one reading that fits the capacity gap and one that does not need it.

<details markdown="1"><summary>Check</summary>

Fits: the student lacks the capacity to model the teacher's behaviour on hard inputs, so the gap is concentrated where the teacher does the most work. Does not need it: hard prompts are few in the distillation data, so the student saw little signal there, and more data on them would help. The two predict different fixes, so test it by adding hard-prompt data to a copy of the run and measuring again.

</details>

## Real-world reps

- [ ] Choose two small open models that share a tokenizer. On 50 prompts, record each model's next-token top choice at one chosen position per prompt and count how often they match.
- [ ] Open the Gudibande et al. paper and find Table 1. Write one sentence on what the broad-coverage rows say about reading an average score.
- [ ] Tomorrow: without notes, draw the capability grid from this lesson for a project of yours, with the two columns, and name the capability where you expect agreement and quality to differ most.

## Going further

- [Sizing and Measuring](../reference/sizing-and-measuring.md)
- [Paper: "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945), sections 3.2 and 5
- [Paper: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717), sections 4.2 and 4.4
- [Evals](../../evals/): the track for building the task-quality side of this grid
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
