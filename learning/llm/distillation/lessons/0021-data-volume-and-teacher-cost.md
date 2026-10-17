---
title: "21. Data Volume and Teacher Cost"
description: Counting the teacher's inference in the budget, and deciding how much distillation data is enough
type: lesson
---

# Lesson 21. Data Volume and Teacher Cost

**Mission link:** The mission asks you to choose a data volume with the teacher's own cost counted in the budget, which takes a formula you can run on the back of an envelope and a clear view of which costs you are and are not paying.
**Primary source:** [Paper: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606), section 5 and Equation 9
**Prerequisites:** [Lesson 20](0020-choosing-student-size.md), [Teacher](../GLOSSARY.md), [Sequence-level distillation](../GLOSSARY.md), [Synthetic data](../GLOSSARY.md)

## Warm-up

1. ▢ Lesson 20 listed two conditions under which distillation is more efficient than supervised learning. State both.

<details markdown="1"><summary>Check</summary>

The student's total compute or tokens must not exceed a student-size-dependent threshold, and a teacher must already exist or have uses beyond a single distillation. Fail either one and the paper's result favours training the student directly.

</details>

2. ▢ Lesson 8 trained a student on the teacher's decoded outputs, and lesson 9 compared that with matching distributions. Which of the two needs the teacher's logits, and which needs only its text?

<details markdown="1"><summary>Check</summary>

[Token-level](../GLOSSARY.md) (logit) distillation needs the teacher's per-position distribution. [Sequence-level distillation](../GLOSSARY.md) needs only the text the teacher decoded, which is why it works through an API that returns nothing else. The two put the teacher's cost in different places, which this lesson prices.

</details>

3. ▢ Lesson 12 said volume does not fix bad examples. If you doubled a generated set without filtering it, what would you expect to happen to the share of bad examples in it?

<details markdown="1"><summary>Check</summary>

It would stay about the same. Doubling a set with a fixed defect rate doubles the defects along with the good examples. More data helps only after the filtering of lesson 12 has set the quality, which is why this lesson counts tokens that survive the filter.

</details>

## Know this

### Two costs, two formulas

Training cost for a dense transformer is commonly approximated as 6 FLOPs per parameter per token: about 2 for the forward pass and 4 for the backward pass. A forward pass alone is about 2 per parameter per token. These are approximations. They ignore the attention term, which grows with context length, and they count all parameters equally.

The paper says as much. It writes the supervised cost as about 6ND, uses the 2N forward approximation as the usual shorthand, and then declines to use it for its own results, for two reasons: using non-embedding parameters biases it, and for small models with long contexts the attention contribution is significant (section 5, below Equation 9). It derives a corrected per-token cost instead. For planning at order-of-magnitude level the shorthand is fine. For a number you will defend, state it as an approximation and say what you left out.

Its distillation cost (Equation 9) is the student's training plus the teacher's forward passes, where each is charged only if it applies to you. In shorthand:

```text
student training   ≈ 6 × N_student × D
teacher inference  ≈ 2 × N_teacher × D     (forward only, over the same D tokens)
```

Here N is parameters and D is the number of tokens the student trains on. The teacher term uses the same D because logit distillation runs the teacher on every token the student sees. Dividing one by the other gives a ratio worth remembering:

```text
teacher cost / student cost  ≈  N_teacher / (3 × N_student)
```

A teacher three times the student's size costs about as much to run as the student costs to train. Any larger teacher costs more than the student you are building.

### Worked example: scoring tokens with a teacher

A 1B student trains on 100B tokens, with logits from a teacher scoring those same tokens.

| Quantity | Calculation | FLOPs |
|---|---|---|
| Student training | 6 × 1e9 × 1e11 | 6.0e20 |
| 7B teacher scoring | 2 × 7e9 × 1e11 | 1.4e21 |
| 70B teacher scoring | 2 × 70e9 × 1e11 | 1.4e22 |

The 7B teacher costs about 2.3 times the student's own training, and the 70B teacher about 23 times. The supervised baseline for the same student on the same tokens costs the 6.0e20 alone. The 70B run is the same student trained at about 24 times the compute, so for that to be worth it the student's loss has to be a great deal lower than the supervised student's at equal compute, and lesson 20's threshold says how often that holds.

### Sharing the teacher's cost across students

If the teacher scores a dataset once and its logits are stored, several students can train from the same pass. With four 1B students on those 100B tokens and the 7B teacher: one student costs 1.4e21 + 6.0e20 = 2.0e21, and four cost 1.4e21 + 4 × 6.0e20 = 3.8e21, which is 9.5e20 each. This is the paper's third setting, in which the teacher's cost is spread over the students it serves (its Table 2). It leaves out what storing logits costs, a bill lesson 7 introduced and the paper treats separately.

### Worked example: generated text instead of logits

For sequence-level distillation the teacher is charged for generating, not scoring. Generating G tokens costs about 2 × N_teacher × G in FLOPs by the forward-pass approximation, and the student then trains on those G tokens for each epoch. This extends the paper's accounting and is not from it, since the paper studies logits.

A 70B teacher generates 1B tokens: 2 × 70e9 × 1e9 = 1.4e20. A 3B student trains two epochs on them: 6 × 3e9 × 1e9 × 2 = 3.6e19. The teacher's generation is about 3.9 times the student's training, and the generated set is reusable, so a second student pays the teacher nothing.

One caution about reading FLOPs as cost. Generating a token at a time keeps a GPU far from full utilisation, so wall-clock and money for generation run well above what FLOPs imply. That is general knowledge about decoding, not a result from a source here, so measure tokens per second on your hardware before you quote a budget.

### What the paper says about where the money goes

When teacher pretraining is part of the bill, the paper's Table 3 summarises how the best split moves with scale:

| Student size | Compute | Optimal allocation |
|---|---|---|
| Small (up to about 3B) | Small (up to about 1e21 FLOPs) | Mostly teacher pretraining |
| Small (up to about 3B) | Large (about 1e25 FLOPs and up) | Evenly between student training and teacher inference, much less on teacher pretraining |
| Large (about 10B and up) | Small | Mostly standard student training |
| Large (about 10B and up) | Large | Equally among student training, teacher inference and teacher pretraining |

Read these as the paper's optimum for its law, across the scenario where teacher pretraining counts. They are not a recipe for an open teacher you already have, where the pretraining column is zero.

### How much data is enough

The honest answer from the paper is that more tokens are not free and not unlimited. With a teacher fixed, distillation's advantage over supervised learning shrinks as the token budget grows, and eventually supervised learning matches or passes it (section 5.1). So "enough" is the point where an extra token is better spent on the student's own signal, and that point rises with student size.

Minitron is a useful contrast. In Table 2 of Muralidharan et al., Minitron 8B was trained on 94B tokens, against 3.8T for Nemotron-3 8B, about 40 times fewer. The comparison has two caveats. Minitron's student starts from the teacher's weights after pruning, where the paper's students start from scratch. And the 40 times figure compares a pruned-and-distilled model with a from-scratch model, not with a supervised run of the same student. So it shows how little data a good initialisation can need. It does not show how much data a from-scratch student needs.

Their family-level saving is also an accounting choice. They report 1.8 times lower compute for the 15B, 8B and 4B family (section 4.1), computed as (4.4e17 + 2.5e17 / 40 + 1.2e17 / 40) against 4.4e17 + 2.5e17 + 1.2e17, in FLOPs per training step. As written, the sum counts each model's own training steps. The sentences describing the calculation do not add a term for running the 15B teacher during the smaller models' retraining. That is the term this lesson says to count.

## Practice

1. ▢ Compute: a 1B student trains on 50B tokens with a stored-logit pass from an 8B teacher. Give the student's training FLOPs, the teacher's scoring FLOPs, and the ratio of the second to the first.

<details markdown="1"><summary>Hint</summary>

Use 6 × N × D for the student and 2 × N × D for the teacher, with the same D in both. The ratio also equals N_teacher divided by three times N_student.

</details>

<details markdown="1"><summary>Check</summary>

Student: 6 × 1e9 × 5e10 = 3.0e20. Teacher: 2 × 8e9 × 5e10 = 8.0e20. Ratio: about 2.7, which matches 8 / (3 × 1) = 2.67. Both are order-of-magnitude figures from the 6N and 2N approximations. They leave out attention and the cost of storing or moving the logits.

</details>

2. ▢ A 70B teacher generates 1B tokens of answers, and a 3B student trains on them for two epochs. Which of the two costs more FLOPs, and by what factor?

<details markdown="1"><summary>Hint</summary>

Generation is one forward pass per token at 2 × N_teacher. Training is 6 × N_student per token per epoch.

</details>

<details markdown="1"><summary>Check</summary>

Generation: 2 × 70e9 × 1e9 = 1.4e20. Training: 6 × 3e9 × 1e9 × 2 = 3.6e19. The teacher's generation costs about 3.9 times the student's training. Adding epochs raises only the student's side, so a third epoch makes the two nearly equal. Generated text can also be reused for another student at no extra teacher cost.

</details>

3. ▢ Four 1B students share one 7B-teacher scoring pass over 100B tokens. What is the average FLOPs per student, and why is it lower than for a single student?

<details markdown="1"><summary>Check</summary>

Total: 1.4e21 + 4 × 6.0e20 = 3.8e21, so 9.5e20 per student, against 2.0e21 for a lone student. The teacher's pass is paid once and divided across four. This ignores the storage and bandwidth cost of keeping the logits, which can be large for a full-vocabulary distribution at every token.

</details>

4. ▢ Which statement about the Minitron 94B-token figure is correct?

    - a) It shows a from-scratch student needs about 94B tokens when distilled from a 15B teacher.
    - b) It shows a pruned student can recover with far fewer tokens than training from scratch.
    - c) It shows distillation needs about forty times less data than supervised training of that student.
    - d) It shows the 15B teacher's inference cost was negligible against the student's training.

<details markdown="1"><summary>Check</summary>

b). The 8B student was pruned from the 15B model, so it started from the teacher's weights. a) and c) treat a pruned initialisation as if it were a from-scratch distillation. The 40 times figure compares against Nemotron-3 8B, a different model trained from scratch. d) is not shown: the family cost calculation as written does not include a teacher forward-pass term, so it says nothing about that cost either way.

</details>

5. ▢ Stage 4 interleave: you plan to generate 20B tokens of instruction data with an API-hosted teacher and distil a 3B student. Name two things the FLOPs formula does not tell you before you commit, one about cost and one from lesson 13.

<details markdown="1"><summary>Check</summary>

For cost, generation is far from FLOPs-bound, so API price or wall-clock hours on your hardware is the real figure, and the filtered yield, not the raw 20B, sets how many tokens you train on. From lesson 13, whether the provider's terms allow training a model on its outputs, which no compute estimate answers.

</details>

## Real-world reps

- [ ] Pick a teacher and student you could realistically use. Write down both parameter counts and a token budget, then compute the student's 6ND, the teacher's 2ND and their ratio.
- [ ] Open the paper's Table 2 and Equation 9 and mark which of the two teacher terms applies to your project, and which row of the table you are in.
- [ ] Tomorrow: without notes, derive the ratio N_teacher / (3 × N_student) from the two formulas, then state two costs it leaves out.

## Going further

- [Sizing and Measuring](../reference/sizing-and-measuring.md)
- [Paper: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606), Equation 9 and Tables 2 and 3
- [Paper: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679), Table 2 and section 4.1
- [Pretraining](../../pretraining/): the track for how a training compute budget is counted and what a token budget buys
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
