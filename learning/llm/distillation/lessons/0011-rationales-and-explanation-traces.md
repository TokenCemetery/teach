---
title: "11. Rationales and Explanation Traces"
description: Training on the teacher's reasoning as well as its answers, as Distilling Step-by-Step and Orca did
type: lesson
---

# Lesson 11. Rationales and Explanation Traces

**Mission link:** The mission asks you to build a distillation set worth training on, and the richest thing a teacher can write for an input is its reasoning, which the student can use as a training signal or as a trap.
**Primary source:** [Paper: "Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes", Hsieh et al., 2023](https://arxiv.org/abs/2305.02301)
**Prerequisites:** [Lesson 10](0010-distilling-from-generated-data.md), [Rationale](../GLOSSARY.md), [Teacher assistant](../GLOSSARY.md), [Capacity gap](../GLOSSARY.md)

## Warm-up

1. ▢ Self-Instruct's filter keeps a new instruction only under one condition about ROUGE-L. State it.

<details markdown="1"><summary>Check</summary>

Its ROUGE-L similarity with any instruction already in the pool must be below 0.7. The rule is about the closest existing member, which keeps the pool from filling with near-copies (lesson 10).

</details>

2. ▢ Generated-data distillation is sequence-level distillation with an extra choice. What is the choice?

<details markdown="1"><summary>Check</summary>

The inputs. In lesson 8 the inputs were a fixed training set; here the seed set, prompt and filter determine which inputs exist (lesson 10).

</details>

3. ▢ What is a [teacher assistant](../GLOSSARY.md), and what problem is it meant to ease?

<details markdown="1"><summary>Check</summary>

A model of intermediate size, distilled from the teacher and then used as the teacher for a smaller student. It is meant to ease the [capacity gap](../GLOSSARY.md): the drop in student quality that can appear when the teacher is far larger than the student.

</details>

## Know this

### A rationale is an extra target

A [rationale](../GLOSSARY.md) is the intermediate reasoning a teacher writes before its answer. Labels alone tell the student what the answer is. A rationale also shows how the teacher reached it, which gives the student more to learn from each example.

Distilling Step-by-Step (Hsieh et al., 2023) uses rationales in a particular way. It prompts a large model with a few worked examples, about 10 per task, so that it writes a rationale along with its label, here the 540B PaLM model (section 3.1 and the limitations section). It then trains a small model, T5, to output both.

### Rationales as a second task, not as an input

There are two obvious ways to use a rationale. They chose the second.

1. **As an input.** Train the student to predict the label from the text plus the rationale. That needs a large model to write a rationale at test time too, so the large model is still needed in production (section 3.2).
2. **As a second output.** Train the student to produce the label and, as a separate task, the rationale. The loss is the label loss plus a weight times the rationale loss. A task prefix tells the model which to produce: a `[label]` prefix on the input asks for the label, a `[rationale]` prefix asks for the rationale (section 3.2).

The second design means no rationale is generated at test time: the student only predicts the label, and the rationale-writing task has shaped what it learned along the way. The cost is a little extra training compute.

Treating the rationale as a second task matters. When the authors instead concatenated the rationale and the label into one target sequence, the student sometimes did worse than plain fine-tuning (Table 2, 220M T5, accuracy):

| Method | e-SNLI | ANLI | CQA | SVAMP |
|---|---|---|---|---|
| Standard fine-tuning | 88.38 | 43.58 | 62.19 | 62.63 |
| Single task, rationale and label together | 88.88 | 43.50 | 61.37 | 63.00 |
| Multi-task, label and rationale separate | 89.51 | 49.58 | 63.29 | 65.50 |

On ANLI and CQA the single-task row sits below standard fine-tuning. Their reading is that the rationales have to be treated carefully to be useful.

### What it bought

These are the paper's results on four benchmarks, three task types, T5 students and a PaLM teacher:

- **Less data.** With a 220M T5 and human labels, distilling step-by-step beat standard fine-tuning on the full e-SNLI set while using only 12.5% of it. The reductions in training examples needed to beat full-data standard fine-tuning were 75% on ANLI, 25% on CQA and 20% on SVAMP (section 4.1). With only unlabeled data, 12.5% of the unlabeled e-SNLI set was enough to beat standard task distillation on all of it.
- **Smaller than the teacher.** A fine-tuned 770M T5 outperformed the few-shot prompted 540B PaLM on ANLI using 80% of the training set, while standard fine-tuning of the same T5 could not match PaLM even with 100% (abstract; section 4.3, Figure 8). On e-SNLI a 220M model did it with 0.1% of the data.
- **A weaker rationale source still helped.** Rationales from a 20B GPT-NeoX model gave a smaller lift than those from PaLM (ANLI 48.15 against 49.58, standard fine-tuning 43.58) (Table 1).

Hold the limits in view. The benchmarks are classification and short-answer tasks, the students are task-specific T5 models and not chat models, and the comparison point is a prompted PaLM. None of it says what happens when you distill a general assistant. The paper also notes its few-shot prompting needs example demonstrations for each task.

### Orca: explanation traces at assistant scale

Orca (Mukherjee et al., 2023) applies the same instinct to general instruction following. Its motivation is that a student trained only on a teacher's final answers learns little of how the teacher thought. Two ideas:

- **Explanation tuning with system messages.** Each training example is a triple of system message, user query and teacher response. They hand-wrote 16 system messages that evoke different response styles, such as asking the model to think step by step and justify its steps, and sampled them across tasks drawn from the FLAN-v2 collection (section 3.1).
- **ChatGPT as an intermediate teacher.** They collected 5 million ChatGPT responses (FLAN-5M), then took 1 million of those queries for GPT-4 responses (FLAN-1M), and trained Orca first on the ChatGPT data and then on the GPT-4 data. Their stated reasons are the capacity gap, since a 13B student is far smaller than GPT-4, and cost and time: they collected 5 times as much from ChatGPT as from GPT-4 (section 3.1.3).

That is a [teacher assistant](../GLOSSARY.md) used on purpose, with a 5M then 1M curriculum. The authors report Orca-13B above Vicuna-13B by more than 100% on Big-Bench Hard and by 42% on AGIEval, at parity with ChatGPT on BBH, and about 4 points behind ChatGPT on professional exams when using an optimized system message (abstract). They also report that Vicuna looks close to ChatGPT under a GPT-4 judge (92%) but retains only 64% on exams and 48% on BBH against human labels, which is why they evaluated on reasoning benchmarks.

These are the Orca authors' own evaluations, on their chosen benchmarks. Whether explanation traces close a capability gap, or mainly the style gap, is the question of lesson 18.

### Reasoning models belong to the next track

Distilling a reasoning model, by fine-tuning on its long chains of thought, is taught in the [post-training](../../post-training/) track. Rationales here are short explanations that help a small task model, and reasoning-model distillation is a larger case of the same idea.

## Practice

1. ▢ In Distilling Step-by-Step, why is the rationale not needed at test time?

    - a) The rationale is hidden inside the label token itself
    - b) The student memorizes every rationale from the training set
    - c) The teacher writes each rationale again in production
    - d) The label task runs alone once the model is trained

<details markdown="1"><summary>Check</summary>

**d)** The rationale is a second output with its own prefix, trained alongside the label, so at test time you ask only for the label. (b) is not what the method does. (c) describes the rejected design where the rationale is an input, which keeps the large model in production. (a) invents a mechanism the paper does not have.

</details>

2. ▢ In Table 2, the single-task row for CQA is 61.37 and standard fine-tuning is 62.19. What does that say about adding rationales naively?

<details markdown="1"><summary>Check</summary>

Adding the rationale into the target as one sequence made the student worse than doing nothing on CQA (and slightly worse on ANLI, 43.50 against 43.58). The gain comes from how the rationale is used, as a separate task, not from having rationales at all. This is the paper's result on its setup.

</details>

3. ▢ A student gets 5 million ChatGPT responses and then 1 million GPT-4 responses. What is the ratio, and what two reasons do the authors give for the order and the size?

<details markdown="1"><summary>Check</summary>

5 to 1. They give the capacity gap, since an intermediate teacher closer to the student's ability eases imitation, and cost and time, since ChatGPT was faster and cheaper to query, so they collected 5 times as much from it as from GPT-4.

</details>

4. ▢ Your team reads the 770M T5 against 540B PaLM result and proposes distilling a general chat assistant the same way, with a 770M model. What do you answer?

<details markdown="1"><summary>Hint</summary>

Look at the kind of task, the kind of student and what the comparison is.

</details>

<details markdown="1"><summary>Check</summary>

The result is for four benchmarks, with task-specific T5 students and a few-shot prompted PaLM as the baseline, and the 80% data figure is for ANLI. It does not cover a general assistant. A proposal for a chat model needs its own evaluation on the tasks you care about, against a baseline trained without the rationales.

</details>

5. ▢ A teacher writes a confident but wrong rationale and a wrong label. Which of the two methods in this lesson would train the student on both, and what would you do before training?

<details markdown="1"><summary>Check</summary>

Both would: the rationale and the label are targets in Distilling Step-by-Step, and an explanation trace is part of the response in Orca. Filter first. Where a checker exists, keep only the examples whose answer is verified correct; otherwise sample and inspect. Lesson 12 covers that.

</details>

## Real-world reps

- [ ] Find Table 2 in the Orca paper and read the 16 system messages. Pick three and predict how the same query would be answered differently under each.
- [ ] Write a rationale prompt for a task you know, with two worked examples, and run it on any model available to you. Check one rationale by hand for an error that the final answer hides.
- [ ] Tomorrow: without notes, explain why the rationale is a second output and not an input, and what that does to test-time cost.

## Going further

- [Sequence and Synthetic Data](../reference/sequence-and-synthetic-data.md)
- [Paper: "Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes", Hsieh et al., 2023](https://arxiv.org/abs/2305.02301)
- [Paper: "Orca: Progressive Learning from Complex Explanation Traces of GPT-4", Mukherjee et al., 2023](https://arxiv.org/abs/2306.02707)
- [Post-training](../../post-training/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
