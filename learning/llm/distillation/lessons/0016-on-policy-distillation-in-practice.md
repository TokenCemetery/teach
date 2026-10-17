---
title: "16. On-Policy Distillation in Practice"
description: What on-policy distillation costs per step, what it buys, and how Qwen3 used it for its small models
type: lesson
---

# Lesson 16. On-Policy Distillation in Practice

**Mission link:** The mission asks you to say when on-policy distillation earns its cost, which means counting what one step costs, what signal it returns, and what a production team measured against the alternative.
**Primary source:** [Paper: "Qwen3 Technical Report", Qwen Team, 2025](https://arxiv.org/abs/2505.09388), section 4.5 and the on-policy distillation discussion in section 4.7
**Prerequisites:** [Lesson 8](0008-sequence-level-distillation.md), [Lesson 14](0014-exposure-bias.md), [Lesson 15](0015-gkd-and-minillm.md), [Off-policy distillation](../GLOSSARY.md), [On-policy distillation](../GLOSSARY.md)

## Warm-up

1. ▢ What does the student data fraction lambda control in GKD, and what are its two extreme values?

<details markdown="1"><summary>Check</summary>

It is the probability that a step trains on student-generated sequences instead of a fixed dataset. Lambda 0 is supervised distillation on fixed data and lambda 1 is purely on-policy.

</details>

2. ▢ Qwen3's first distillation phase trains on outputs the teacher generated. Which lesson-8 term names that, and is it on-policy?

<details markdown="1"><summary>Check</summary>

Sequence-level distillation, in the Qwen3 report's words "response distillation". It is off-policy: the sequences were fixed by the teacher, not written by the student.

</details>

3. ▢ Exposure bias is a mismatch in whose prefixes the student sees. Name the one component an on-policy step needs from the teacher that a fixed-text step does not.

<details markdown="1"><summary>Check</summary>

Its distribution over tokens at every position of the student's own sequence, which means the teacher model must be run on the student's output during training. Text the teacher already wrote does not provide that.

</details>

## Know this

### What one step costs

An off-policy step with stored teacher text costs one student forward and backward pass over fixed sequences. An off-policy step with stored teacher logits adds a read from disk, and the storage cost belongs to lesson 7.

An on-policy step adds work, and it is worth listing in order:

| Step | Work | Notes |
|---|---|---|
| 1 | The student generates a sequence for each prompt | Sequential decoding. Cheaper than the teacher doing it, because the student is smaller (GKD, section 3.1) |
| 2 | The teacher runs one forward pass over the finished sequence | One parallel pass, not generation. Needs the teacher in memory or reachable |
| 3 | The student runs forward and backward and the divergence is computed | The same as an off-policy step |

The first two lines have no off-policy counterpart with fixed text. The paper's own efficiency note concerns SeqKD instead: in the instruction-tuning experiment GKD did not run SeqKD "due to its computational inefficiency for generating data from the teacher during training" (section 4.4). Step 1 here uses the small model, which is the cheaper side of that trade. That cost comparison is the paper's statement, and the three-row table above is my accounting of the work.

### Dense signal against a sparse reward

Distillation is not the only way to improve a small model on its own samples. Reinforcement learning also trains on the model's own sequences, but it scores each whole sequence with a scalar reward. GKD's section 3.2 writes the combined objective with the reward as `r(y)`, a single number per sequence.

On-policy distillation returns a score for every token, taken from the teacher's distribution at that position. That is a denser signal per sample. Dense means more information per generated sequence. It does not mean the teacher is right, which lesson 18 comes back to.

The practical consequence runs one way. RL can improve a model with no stronger model available, because it needs only a reward. On-policy distillation needs a stronger teacher to exist.

### How Qwen3 used it

The Qwen3 report describes a four-stage post-training pipeline for its flagship models, and a separate "strong-to-weak distillation" for the lightweight ones: five dense models (0.6B, 1.7B, 4B, 8B and 14B) and one mixture-of-experts model (30B-A3B). The motivation was cost: distillation "eliminates the necessity of performing an exhaustive four-stage training process individually for every small-scale model" (section 4).

The small models are distilled in two phases (section 4.5):

| Phase | Data | Training signal |
|---|---|---|
| Off-policy | Teacher outputs generated in both thinking and non-thinking modes | Response distillation, to give basic reasoning skill and the ability to switch modes |
| On-policy | The student generates responses in either mode | The student is fine-tuned by aligning its logits with the teacher's (Qwen3-32B or Qwen3-235B-A22B) to minimise KL divergence |

Read the order. The off-policy phase comes first, and the report says it lays "a solid foundation" for the on-policy one. That matches GKD's remark that on-policy training assumes a student that can already generate acceptable sequences. This is a two-stage schedule, not the per-batch lambda mix of GKD.

### The comparison against RL

Section 4.7 compares on-policy distillation with direct reinforcement learning on Qwen3-8B. Both start from the same off-policy distilled checkpoint, and the comparison uses only math and code queries. Table 21 reports, with pass@64 in parentheses where the report gives one:

| Method | AIME'24 | AIME'25 | MATH500 | LiveCodeBench v5 | MMLU-Redux | GPQA-Diamond | GPU hours |
|---|---|---|---|---|---|---|---|
| Off-policy distillation | 55.0 (90.0) | 42.8 (83.3) | 92.4 | 42.0 | 86.4 | 55.6 | not given |
| plus reinforcement learning | 67.6 (90.0) | 55.5 (83.3) | 94.8 | 52.9 | 86.9 | 61.3 | 17,920 |
| plus on-policy distillation | 74.4 (93.3) | 65.5 (86.7) | 97.0 | 60.3 | 88.3 | 63.3 | 1,800 |

On every benchmark in the table, on-policy distillation scored higher than RL, and it used about one tenth of the GPU hours: 17,920 divided by 1,800 is 9.96. The report reads this as significantly better performance than RL at roughly one tenth of the GPU hours. It also notes that pass@64 on AIME rose after distillation and did not change after RL, which it takes as evidence that distilling from teacher logits expands the student's exploration space.

### How far to trust that table

It is one report, one student size, math and code queries only, and the authors compared their own two methods. The report does not say which teacher was used for the 8B comparison. I did not find a statement of whether the GPU-hour figures include running the teacher, so do not assume they do. The RL recipe is not described in the comparison, so a better-tuned RL run might close some of the gap. The result is strong evidence that distillation was cheaper and better in Qwen3's setting, and not evidence about every setting.

Note also what the comparison leaves out. The teachers themselves came out of the four-stage pipeline, which includes RL. The saving is real, but it assumes someone already paid for the teacher.

## Practice

1. ▢ From Table 21, how many points did RL and on-policy distillation each add on LiveCodeBench v5 over the off-policy checkpoint, and how many GPU hours per point did each use?

<details markdown="1"><summary>Check</summary>

RL went from 42.0 to 52.9, so +10.9 points, and 17,920 divided by 10.9 is about 1,640 GPU hours per point. On-policy distillation went to 60.3, so +18.3 points, and 1,800 divided by 18.3 is about 98 GPU hours per point. The ratio is about 17 to 1 on this benchmark, larger than the headline 10 to 1, because distillation also gained more points. Both numbers are for one student size and one set of queries.

</details>

2. ▢ Which cost is present in an on-policy distillation step and absent from an off-policy step on stored teacher text?

    - a) Backpropagating through the student model
    - b) Computing a loss at every token position
    - c) Running the teacher over student output
    - d) Tokenizing the prompts before training starts

<details markdown="1"><summary>Check</summary>

**c)** The teacher must score sequences that did not exist until the student generated them. (b), (a) and (d) happen in off-policy steps too.

</details>

3. ▢ Pass@1 improved after both RL and on-policy distillation. What did pass@64 on AIME show for each, and what does the report conclude?

<details markdown="1"><summary>Hint</summary>

Look at the parenthesised numbers in the AIME columns for the RL row.

</details>

<details markdown="1"><summary>Check</summary>

For RL pass@64 stayed at 90.0 on AIME'24 and 83.3 on AIME'25, unchanged from the starting checkpoint. After on-policy distillation it rose to 93.3 and 86.7. The report concludes that distilling from teacher logits expanded the student's exploration space while RL did not. That is the authors' interpretation of one comparison.

</details>

4. ▢ You have an 8B student, a stronger teacher with the same tokenizer, a math task with a checkable answer, and a limited GPU budget. Does the Qwen3 table settle whether to use RL or on-policy distillation?

<details markdown="1"><summary>Check</summary>

It points toward distillation and does not settle it. It supports that, with a strong teacher already available and the student first warmed up by off-policy distillation, on-policy distillation was cheaper and better in Qwen3's runs. It does not cover your task, your teacher, or whether the GPU-hour figures include the teacher. If no stronger teacher exists, distillation is not available at all and RL is the route, which is how Qwen3's teachers were built.

</details>

5. ▢ Why does Qwen3 run the off-policy phase before the on-policy one, and what in GKD supports that order?

<details markdown="1"><summary>Check</summary>

The off-policy phase gives the student basic reasoning ability and mode switching, which the report says lays a foundation for on-policy training. GKD makes the same assumption: it needs a student that can already generate sequences of adequate quality for the teacher's feedback to mean something, and its students began as supervised fine-tuned checkpoints.

</details>

## Real-world reps

- [ ] Open section 4.7 of the Qwen3 report and find Table 21. Copy the three GPU-hour and AIME'24 cells into a note and compute the points-per-hour for each method from them.
- [ ] Write the per-step cost of your own planned run in three lines: who generates, who scores, who updates. Then mark which model is large enough to need its own GPU.
- [ ] Tomorrow: without notes, write the two Qwen3 phases, what each trains on, and two reasons not to generalise the 1/10 figure.

## Going further

- [On-Policy Distillation](../reference/on-policy-distillation.md)
- [Paper: "Qwen3 Technical Report", Qwen Team, 2025](https://arxiv.org/abs/2505.09388)
- [Post-training](../../post-training/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
