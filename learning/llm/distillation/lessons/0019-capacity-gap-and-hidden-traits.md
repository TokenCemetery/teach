---
title: "19. Capacity Gap and Hidden Traits"
description: Why a bigger teacher is not always a better one, and what can pass to a student that nobody intended
type: lesson
---

# Lesson 19. Capacity Gap and Hidden Traits

**Mission link:** The mission asks you to predict what a student will inherit, including capability it cannot absorb and traits nobody meant to pass on, and this lesson covers one of each.
**Primary source:** [Paper: "Subliminal Learning: Language models transmit behavioral traits via hidden signals in data", Cloud et al., 2025](https://arxiv.org/abs/2507.14805), sections 1 to 5
**Prerequisites:** [Lesson 12](0012-filtering-synthetic-data.md), [Lesson 18](0018-the-imitation-gap.md), [Capacity gap](../GLOSSARY.md), [Teacher assistant](../GLOSSARY.md), [Subliminal learning](../GLOSSARY.md)

## Warm-up

1. ▢ What is the imitation gap, in one sentence?

<details markdown="1"><summary>Check</summary>

The distance between how much a student sounds like its teacher and how much of the teacher's capability it has. Imitation on a limited budget closes the style side much faster than the capability side.

</details>

2. ▢ Lesson 12 filters synthetic data for quality. Name two things such a filter can check, and say what they have in common.

<details markdown="1"><summary>Check</summary>

It can check format, correctness, duplicates or flagged words. What they share is that each is a property of the text itself, which a filter can read. This lesson tests what happens when a property is not readable in the text.

</details>

3. ▢ Lesson 17 separates fidelity from generalization. Which of the two fails when a student cannot mimic a much larger teacher?

<details markdown="1"><summary>Check</summary>

Fidelity: the student's predictions diverge from the teacher's. Whether task quality also suffers depends on the case, which is why this lesson's first half asks whether a larger teacher helps at all.

</details>

## Know this

### A bigger teacher is not a better teacher

Mirzadeh et al. distilled a fixed small student from teachers of increasing size. Their student is a plain CNN with 2 convolutional layers, and the teachers have 4, 6, 8 and 10. As the teacher grows, its own test accuracy rises, but the student's accuracy first rises and then falls, on both CIFAR-10 and CIFAR-100 (Figure 2). So a student cannot use an arbitrarily large teacher.

They name three competing factors: a stronger teacher supervises better, but it may become so complex that the student cannot mimic it, and its higher certainty makes its logits less soft, which weakens the transfer. This is the [capacity gap](../GLOSSARY.md). Note the scale of the evidence: these are image classifiers with small networks, not language models.

Their fix is the [teacher assistant](../GLOSSARY.md). Distil the teacher into an intermediate-size network, then distil that into the student. Table 1 gives test accuracy with no distillation, with standard distillation, and with the assistant:

| Setup | No distillation | Standard distillation | With assistant |
|---|---|---|---|
| Plain CNN, CIFAR-10 (student 2, assistant 4, teacher 10) | 70.16 | 72.57 | 73.51 |
| Plain CNN, CIFAR-100 (same sizes) | 41.09 | 44.57 | 44.92 |
| ResNet, CIFAR-10 (student 8, assistant 20, teacher 110) | 88.52 | 88.65 | 88.98 |
| ResNet, CIFAR-100 (same sizes) | 61.37 | 61.41 | 61.82 |

The gain is real and small. On the ResNet rows the assistant adds 0.33 points on CIFAR-10 and 0.41 on CIFAR-100 over standard distillation. The paper also shows the best assistant size is not the midpoint: for the plain CNN, a size-4 assistant beat sizes 6 and 8 (Table 2).

### A second account, and a disagreement

Cho and Hariharan reach the same observation from another angle: more accurate teachers often do not make better students. On ImageNet with a ResNet18 student, the scratch-trained student has an error of 30.24%. Students distilled from ResNet18, ResNet34 and ResNet50 teachers had errors of 30.57%, 30.79% and 30.95% as the teacher's own error fell from 30.24% to 26.70% to 23.85% (Table 1). Every teacher made the student slightly worse than training from scratch.

Their diagnosis: the student cannot mimic the large teacher, which shows as a much higher distillation loss for the largest teacher, rather than the teacher's outputs being too close to one-hot, since raising the temperature did not change the result. The remedies they report:

| Remedy | Result in the paper |
|---|---|
| Stop the distillation early and finish on the hard labels | ResNet18 student errors fell to 29.01%, 29.16% and 29.35% for the three teachers, all better than 30.24% from scratch (Table 3). A larger teacher still did not give a better student |
| Stop the teacher's own training early | Students trained from early-stopped teachers consistently outperformed those from fully trained teachers on CIFAR-10 (Figure 5). The paper says only a third to a fourth of the epochs are needed |
| Chain distillation through intermediate models | Reported as ineffective: distilling a large model into a medium one and then a small one did not help, and distilling directly from the medium model was best (Table 6) |

The last row is a disagreement with the assistant idea, in a different setup (WideResNets on CIFAR-10). Two vision papers do not decide which holds for an LLM. The honest reading is that a mismatched pair is a risk worth testing, and that both a teacher in between and an early-stopped teacher are cheap things to try.

One data point from language models: MiniLLM kept a GPT-2 125M student fixed and used teachers of 340M, 760M and 1.5B. The student's performance was positively correlated with teacher size over that range (Figure 5). That is a roughly 12 to 1 teacher to student ratio with no sign of a capacity gap, in one family and one setup. I did not verify any LLM paper that shows the gap itself, so treat the capacity gap as a vision result you should check for your own pair.

### Traits nobody intended

Cloud et al. built the opposite of a capacity problem: something passes that the data does not seem to contain. The setup is simple. A teacher is made to have a trait, by system prompt or fine-tuning, for example a love of owls or misalignment. It generates data in an unrelated domain such as number sequences. The data is filtered to remove any reference to the trait. A student, fine-tuned from the same base model, trains on it.

| Experiment | Result |
|---|---|
| Owl teacher, GPT-4.1 nano, numbers only (section 3.1) | The student chose owl as its favourite animal about 12% of the time before training and over 60% after. A control student trained on numbers from the unprompted model showed no comparable shift |
| Misaligned teacher, numbers with 34 negatively associated numbers removed (section 3.2) | The student gave misaligned free-form responses almost 10% of the time, against 0% for the base model and under 1% for the control students |
| Misaligned teacher, chain of thought filtered for correctness and alignment (section 4) | Misaligned responses rose from about 0% to 8%, with controls under 1% |

The number sequence filter rejected between 23% and 38% of completions for formatting, and the datasets were cut to 10,000 examples. The trait is not in the numbers in any way the authors could find. Prompted classifiers and in-context learning did not reliably detect it, and the authors inspected examples without seeing signs of it (Introduction and section 5.2).

### The condition: a shared base model

The effect depended on the student and teacher sharing a base. A GPT-4.1 nano teacher's numbers transmitted traits to a GPT-4.1 nano student but not to a Qwen2.5 student (Introduction, section 5.1). GPT-4o and GPT-4.1 did transmit to each other, which the authors suggest is because they share an initialization, citing an interview with an OpenAI developer. Their theory result says a sufficiently small gradient step on teacher-generated output moves a student toward the teacher, and it requires shared initialization.

Read the scope precisely. In their experiments, transmission failed across different bases, which is not the same as a guarantee that a different base is safe. Their tasks are artificial, they say what can and cannot be transmitted is open, and some animals did not transmit for some models. Their implication is that filtering may be insufficient to stop transmission of a trait carried by statistical patterns instead of content, and that safety evaluation of a student should probe beyond behaviour on the training distribution.

What to do with it: if the student starts from the same base model as the teacher, for example when you fine-tune a fresh copy of a model on data generated by a tuned copy of itself, a clean-looking filtered dataset does not certify a clean student. Evaluate the student for the teacher's undesirable traits directly. That advice is my inference from their results, not a protocol they tested.

### Refusals and style come along too

A student also inherits the teacher's visible behaviour. In lesson 18's paper, imitation models became less toxic as imitation data grew, which the authors read as the model learning to abstain like ChatGPT (Gudibande et al., Figure 5). So refusal patterns transfer along with style, much more readily than knowledge does. Nothing in the sources read for this lesson measures whether students copy a teacher's factual errors, so this lesson makes no claim about that.

## Practice

1. ▢ From Cho and Hariharan's Table 1, how much worse than the scratch-trained student was the student distilled from the ResNet50 teacher, and how much better was it after early-stopping the distillation?

<details markdown="1"><summary>Check</summary>

The ResNet50-distilled student had 30.95% error against 30.24% from scratch, so 0.71 points worse. With early-stopped distillation it had 29.35%, so 0.89 points better than scratch. The pattern is distillation hurting late in training, not the teacher being bad: the same teacher helps once the student stops chasing it.

</details>

2. ▢ Which change defines the teacher assistant method of Mirzadeh et al.?

    - a) The student trains on narrow task-specific data
    - b) The teacher stops its training much earlier
    - c) The student learns from a mid-sized assistant
    - d) The student reuses the teacher's initial weights

<details markdown="1"><summary>Check</summary>

**c)** An intermediate-size model is distilled from the teacher and then teaches the student. (b) is Cho and Hariharan's early-stopped teacher. (a) is the local imitation of lesson 18. (d) is the shared-initialization condition from Cloud et al., which is a source of hidden transfer, not a method.

</details>

3. ▢ In Mirzadeh et al.'s Figure 2 experiment, a 2-layer student is distilled from teachers with 4, 6, 8 and 10 layers. Predict the shape of the student's accuracy as teacher size grows.

<details markdown="1"><summary>Hint</summary>

The teacher's own accuracy keeps rising. Which of the three competing factors wins early, and which wins late?

</details>

<details markdown="1"><summary>Check</summary>

It rises first, then falls. At small sizes the better supervision from a stronger teacher wins. At large sizes the student's inability to mimic the teacher and the teacher's lower softness win. The peak is not at the largest teacher. This is the paper's CNN result on CIFAR-10 and CIFAR-100, so do not assume the peak sits at the same ratio for an LLM.

</details>

4. ▢ Your team fine-tunes a base model, finds the tuned copy shows an unwanted behaviour, and uses that copy to generate data for a fresh copy of the same base. The data is filtered to remove any mention of the behaviour. What does Cloud et al. say about whether the filter is enough, and what do you add?

<details markdown="1"><summary>Check</summary>

Their experiments show a trait passing through data filtered for it, including number sequences, filtered code and filtered chain of thought, when student and teacher share a base. So a filter that removes explicit references is not sufficient evidence of a clean student. Add a direct evaluation of the student for the unwanted behaviour, and if the choice is open, treat a student from a different base as lower risk, since transmission failed across bases in their tests, while remembering that is an observation, not a guarantee.

</details>

5. ▢ Mirzadeh et al. report a teacher assistant helps. Cho and Hariharan report a chain through an intermediate model does not. What do you do when deciding for your own run?

<details markdown="1"><summary>Check</summary>

Do not pick a side from the papers. Both are vision experiments, the assistant gains are small on the ResNet rows (0.33 and 0.41 points over standard distillation), and the setups differ. Run a controlled comparison on your own pair: direct distillation, one intermediate model, and an early-stopped teacher or early-stopped distillation. Measure against a scratch-trained baseline and against agreement with the teacher, as in lesson 17.

</details>

6. ▢ MiniLLM's teacher-size experiment kept a 125M student and used three teachers up to 1.5B. What did it show, and what does it not show about the capacity gap?

<details markdown="1"><summary>Check</summary>

The student's performance was positively correlated with teacher size across 340M, 760M and 1.5B, so no capacity gap appeared over that range in that family. It does not show the gap never occurs for LLMs: the range tops out at about 12 times the student, and it is one method on one family.

</details>

## Real-world reps

- [ ] Open Table 1 and Table 3 in the Cho and Hariharan paper and write the student error for each teacher with and without early stopping. Note which teacher gave the lowest student error with early stopping.
- [ ] Find the teacher and student in a distillation you rely on and write down whether they share a base model. If they do, write one direct check for an unwanted trait you would run on the student.
- [ ] Tomorrow: without notes, write the three competing factors in the capacity gap, the teacher assistant method in two sentences, and the condition under which subliminal learning appeared.

## Going further

- [What the Student Inherits](../reference/what-the-student-inherits.md)
- [Paper: "Subliminal Learning: Language models transmit behavioral traits via hidden signals in data", Cloud et al., 2025](https://arxiv.org/abs/2507.14805)
- [Paper: "Improved Knowledge Distillation via Teacher Assistant", Mirzadeh et al., 2019](https://arxiv.org/abs/1902.03393)
- [Paper: "On the Efficacy of Knowledge Distillation", Cho and Hariharan, 2019](https://arxiv.org/abs/1910.01348)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
