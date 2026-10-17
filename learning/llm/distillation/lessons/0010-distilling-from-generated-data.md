---
title: "10. Distilling From Generated Data"
description: "Building an instruction set from a teacher's generations, as Self-Instruct and Alpaca did"
type: lesson
---

# Lesson 10. Distilling From Generated Data

**Mission link:** The mission asks you to distill from a teacher's generated data, which means building the inputs as well as collecting the outputs, and knowing what the build costs.
**Primary source:** [Paper: "Self-Instruct: Aligning Language Models with Self-Generated Instructions", Wang et al., 2022](https://arxiv.org/abs/2212.10560)
**Prerequisites:** [Lesson 9](0009-token-or-sequence.md), [Synthetic data](../GLOSSARY.md), [Sequence-level distillation](../GLOSSARY.md), [Teacher](../GLOSSARY.md), [Student](../GLOSSARY.md)

## Warm-up

1. ▢ In Kim and Rush's recipe, where did the inputs come from, and what did the teacher add?

<details markdown="1"><summary>Check</summary>

The inputs were the existing training sentences. The teacher added only the outputs: its beam-search translation of each input. The student trained on those input and output pairs (lesson 8).

</details>

2. ▢ A teacher sits behind an API and returns text only. Which level of distillation is open to you?

<details markdown="1"><summary>Check</summary>

Sequence level, on the text you can collect (lesson 9). Token level needs the teacher's distribution at each position, which text alone does not give you.

</details>

## Know this

### Generated-data distillation is sequence-level distillation with one more choice

In lesson 8 the inputs were given: the training set of a translation task. For a general instruction model there is no fixed set of inputs. Someone has to write the prompts.

Generated-data distillation is [sequence-level distillation](../GLOSSARY.md) where you also choose the inputs. The teacher writes the prompts or you do, the teacher writes the answers, and the student trains with plain cross-entropy on the pairs. Everything about what the student receives is decided by that data: a student can only learn behaviours the pairs show.

### Self-Instruct: the pipeline

Self-Instruct (Wang et al., 2022) builds an instruction set from a model's own generations, starting from 175 human-written seed tasks, each with one instruction and one instance. It has four steps (section 2.2):

1. **Generate instructions.** Sample 8 instructions from the task pool as in-context examples, 6 of them human-written and 2 generated in earlier rounds, and ask the model for new ones.
2. **Classify the task.** Ask the model, with a few examples (12 classification and 19 non-classification seed instructions), whether the instruction is a classification task, meaning one with a small, limited set of outputs.
3. **Generate instances.** For most tasks, input first: write an input, then the output. For classification tasks, output first: write the class label, then an input for that label. The authors added this because input-first generation produced inputs biased toward one label, for example grammatical sentences for a grammar-error task.
4. **Filter.** Keep a new instruction only if its ROUGE-L similarity with every instruction already in the pool is below 0.7. Drop instructions with keywords such as image, picture or graph that a language model cannot handle. Drop duplicate instances and instances with the same input but different outputs. Drop instances that fail simple heuristics, such as an instruction that is too long or too short, or an output that merely repeats the input.

The loop feeds back: accepted instructions join the pool and become in-context examples for later rounds. The filtering rules are the subject of lesson 12.

The result, on the GPT-3 `davinci` model, was 52,445 instructions and 82,439 instances after filtering, of which 11,584 instructions were classification tasks (Table 1). Fine-tuning GPT-3 on all of it cost $338 through the provider's fine-tuning service (appendix A.3). The same model generated the data and was then fine-tuned on it, so the teacher and the student started from one model.

Their evaluation, on unseen tasks from SuperNI measured by ROUGE-L (Table 3): vanilla GPT-3 scored 6.8, the Self-Instruct model 39.9, and the OpenAI instruction-tuned model InstructGPT001 40.8. The authors read that as a gain of 33.1 points that nearly matches InstructGPT001. It is their result on their benchmark and metric.

### Alpaca: the same recipe at a smaller scale

The Stanford CRFM team built Alpaca from Self-Instruct's idea, but changed the teacher and the student (Alpaca blog post, "Training recipe"):

- They started from the same 175 seed pairs and prompted OpenAI's text-davinci-003 to generate more.
- They simplified the generation pipeline relative to Self-Instruct, and say this reduced the cost.
- The data is 52K unique instructions with outputs, which cost less than $500 through the OpenAI API.
- They fine-tuned LLaMA 7B with supervised learning. The first run took 3 hours on 8 80GB A100s, which they put at under $100 on most cloud providers.

Their summary line is that Alpaca 7B can be reproduced for under $600. On a preliminary single-turn evaluation, they report that it behaves qualitatively similarly to text-davinci-003. Treat that as the authors' impression on a small evaluation, not a measured match; lesson 18 returns to why such impressions can mislead.

| | Self-Instruct | Alpaca |
|---|---|---|
| Teacher | GPT-3 `davinci` (the model that was then fine-tuned) | text-davinci-003 |
| Student | GPT-3 `davinci` | LLaMA 7B |
| Seed set | 175 tasks | The same 175 pairs |
| Data | 52,445 instructions, 82,439 instances | 52K instructions with outputs |
| Stated cost | $338 for the fine-tune | Under $500 for the data, under $100 for the run |

### What the data design decides

Four choices shape what the student learns, and each is yours when you generate data:

- **The seed set.** Everything is generated from 175 examples, so what they cover limits what the pool grows into.
- **The prompt.** The in-context examples and the template steer style and task mix.
- **The sampling settings.** Temperature and similar settings set how varied the outputs are.
- **The filter.** What you keep is the training set. A weak filter lets the teacher's mistakes become the student's lessons.

A student can only match what the teacher wrote, so a mistake that survives the filter is learned as if it were correct.

### Restrictions came with the data

The Alpaca post is explicit that the model is for academic research only. It gives three reasons: LLaMA has a non-commercial license, the data comes from text-davinci-003 whose terms prohibit developing models that compete with OpenAI, and they had not built adequate safety measures. Lesson 13 reads those restrictions closely. For now, note that the cost of the data was the smaller part of what it came with.

## Practice

1. ▢ Alpaca's data cost under $500 for 52K instruction and output pairs. What is the cost per example at most, and why is that not the full cost of the model?

<details markdown="1"><summary>Check</summary>

Under $500 divided by 52,000 is about $0.0096, under one cent per example. It is not the full cost: the blog separately counts the fine-tuning run (3 hours on 8 80GB A100s, under $100 on most clouds), and neither figure counts the human effort of the 175 seeds, the evaluation, or the demo. Lesson 21 counts the teacher's cost properly.

</details>

2. ▢ Self-Instruct generates classification data output first. What problem with input-first generation does that fix?

    - a) Inputs come out biased toward a single class label
    - b) Outputs come out far longer than any human answer
    - c) Instructions repeat the same input text without any change
    - d) Labels come out written in a wildly inconsistent format

<details markdown="1"><summary>Check</summary>

**a)** The paper's example: asked to write an input for grammar-error detection, the model tends to write grammatical input, so one class dominates. Writing the label first and then an input for that label balances them. (b), (c) and (d) are not the problem the authors name.

</details>

3. ▢ A new generated instruction has ROUGE-L similarity 0.74 with one instruction already in the pool and 0.2 with all the rest. Does Self-Instruct keep it, and why?

<details markdown="1"><summary>Hint</summary>

The rule is about the maximum over the pool, not the average.

</details>

<details markdown="1"><summary>Check</summary>

No. The instruction is kept only if its ROUGE-L similarity with any existing instruction is below 0.7, and 0.74 exceeds that. The rule keeps the pool diverse by rejecting a near-copy of any single member, however different the rest of the pool is.

</details>

4. ▢ Your team wants to copy Alpaca but use a teacher that outputs short, curt answers. What do you expect the student to do, and which part of the pipeline would you change first?

<details markdown="1"><summary>Check</summary>

Expect the student to answer in the same curt style, because it can only learn what the pairs show. Change the prompt or the teacher's settings first, since that is where the answer style is set, then re-run the filter and compare a sample of generated pairs by eye before training. This is a prediction from how the data determines the student, not a measured result.

</details>

5. ▢ Lesson 8 found that a sequence-level student trained on a teacher's single best output ends up peaked around that output. Does that suggest generating several outputs per prompt, or one, and what would each cost?

<details markdown="1"><summary>Check</summary>

It does not decide the matter. One output per prompt is the mode-style approach: cheap and consistent, but a single sample. Several outputs per prompt show the student more of the teacher's variety, at several times the generation cost and with more filtering to do. Kim and Rush tried sampling in place of the mode on translation and kept the mode. That is a result for their task, so test both on yours.

</details>

## Real-world reps

- [ ] Open the Self-Instruct paper and find the prompt template for instruction generation (Table 5). Write down what the in-context examples look like and how many human and model-written ones there are.
- [ ] Open the Alpaca blog post and find the sentence listing the three factors for the research-only release. Write down which of them depends on your choice of teacher.
- [ ] Tomorrow: write the four steps of the Self-Instruct pipeline and the filter threshold without notes, then compare against the paper.

## Going further

- [Sequence and Synthetic Data](../reference/sequence-and-synthetic-data.md)
- [Paper: "Self-Instruct: Aligning Language Models with Self-Generated Instructions", Wang et al., 2022](https://arxiv.org/abs/2212.10560)
- [Article: "Alpaca: A Strong, Replicable Instruction-Following Model", Stanford CRFM, 2023](https://crfm.stanford.edu/2023/03/13/alpaca.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
