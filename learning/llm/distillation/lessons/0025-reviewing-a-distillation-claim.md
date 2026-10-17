---
title: "25. Reviewing a Distillation Claim"
description: Review "our small model matches the large one" by naming what the measurement hid
type: lesson
---

# Lesson 25. Reviewing a Distillation Claim

**Mission link:** The mission ends with reviewing someone else's claim that a distilled model "matches the teacher". A review that says "I don't trust it" gets ignored, and one that names which part of the measurement hid what, and what it would cost to find out, gets acted on.
**Primary source:** [Paper: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717), sections 1 and 4
**Prerequisites:** [Lesson 22](0022-student-against-teacher.md), [Lesson 23](0023-an-honest-distillation-eval.md), [Fidelity](../GLOSSARY.md), [Imitation gap](../GLOSSARY.md)

## Warm-up

1. ▢ Lesson 17 separated two things a student can be good at. Name them and say which one Stanton et al. found to be low even when the student could match the teacher.

<details markdown="1"><summary>Check</summary>

[Fidelity](../GLOSSARY.md), how closely the student's predictions agree with the teacher's, and generalization, how well the student does on the task. Stanton et al. report that a large discrepancy between teacher and student predictive distributions often remains even when the student has the capacity to match the teacher exactly, and that better generalization does not require better fidelity ([paper](https://arxiv.org/abs/2106.05945), abstract).

</details>

2. ▢ Lesson 23 listed baselines that make a "matches the teacher" number defensible. Which baseline tells you what the teacher contributed, as opposed to what the student's size and data would have given anyway?

<details markdown="1"><summary>Check</summary>

A model of the student's size trained without the teacher, on the same task data. Without it, a good score may be what any student of that size reaches, and the teacher gets credit for work it did not do.

</details>

3. ▢ Lesson 18 named the imitation gap. In one sentence, what does it say about how fast a student closes the gap on style compared with capability?

<details markdown="1"><summary>Check</summary>

Imitation on a limited budget closes the gap on style much faster than on capability, so a student can sound like its teacher long before it can do what the teacher does.

</details>

## Know this

### A claim has parts

"Our 7B matches the teacher" is five claims in one sentence: a model, a measurement, a baseline, a population of inputs and a cost. A review takes it apart and asks of each part what it would take for the claim to fail. The most useful reviews also say what is fine, so that the author keeps it.

### What a percentage measures: DistilBERT

Sanh et al. say DistilBERT is 40% smaller and 60% faster and "retains 97% of its language understanding capabilities" ([paper](https://arxiv.org/abs/1910.01108), abstract). Section 4 and Table 1 say what that sentence measures: the GLUE benchmark's nine tasks, on dev sets, after fine-tuning each model, with BERT and DistilBERT results being medians of 5 runs with different seeds. The printed macro-scores are 79.5 for BERT-base and 77.0 for DistilBERT, and 77.0 over 79.5 is 96.9%.

So 97% is a ratio of two averages, on one benchmark suite, against one teacher. Per task, Table 1 gives a different picture: DistilBERT scores 51.3 on CoLA against BERT's 56.3, which is 91.1%, and 59.9 on RTE against 69.3, which is 86.4%. On WNLI it scores 56.3 against 53.5, above the teacher. The headline is not wrong. It is an average that two weak tasks and a few near-ties are folded into, and a reader whose workload looks like RTE should read the RTE row.

Three more facts from the paper belong in a review. The student was initialized from the teacher by taking one layer out of two (section 3), which is a design choice a claim should disclose. It was trained on the same corpus as BERT, so there is no shift between the teacher's data and the student's. And the compute was 8 V100 GPUs for about 90 hours (section 3), with the teacher already trained and not counted in that figure.

### What a preference rating hides: Gudibande et al.

Gudibande et al. fine-tuned models from 1.5B to 13B parameters to imitate ChatGPT and rated them two ways. Crowdworkers, about 70 of them, judged 255 held-out prompts, and roughly 70% of the imitation models' outputs were rated equal to or better than ChatGPT's (section 4, Figure 1 left). To limit leakage they dropped queries whose BLEU score against any training example exceeded 20%, and they dropped coding and non-English prompts that raters could not judge.

Targeted automatic evaluations told a different story. The authors report that the imitation models closed little to none of the gap between the base model and ChatGPT on tasks that were not heavily supported in the imitation data, and that more imitation data did not close it, with some results such as Natural Questions factual knowledge regressing (Figure 1 center). Their explanation is that the models learned ChatGPT's style, confident and well structured, and that raters without domain expertise or time to check facts miss the errors (section 4.4).

This is one paper's result, for imitating ChatGPT with models up to 13B parameters. The transferable point is not that preference ratings are useless. It is that a rating measures what the rater can judge, and what a rater can judge in a minute is often style.

### The questions to ask

| Part of the claim | Ask | Why it matters |
|---|---|---|
| Tasks | Which tasks, and is the average hiding the weak ones? | DistilBERT's 97% sits over rows at 86% and 91% |
| Population | Are the test inputs held out, or drawn from the distillation distribution? | Gudibande et al. find the gap shows on tasks the imitation data does not support |
| Baseline | Against what: the teacher, a same-size model trained without it, the base model? | The first tells how far, the second tells what the teacher added |
| Contamination | How was test data kept out of the distillation prompts? | A BLEU overlap filter is one concrete answer, and a claim with none is a gap |
| Rater | Humans, a judge model, or a metric, and could they check facts? | A judge or crowd can reward style |
| Decoding | Greedy or sampled, which temperature, the same for both models? | Agarwal et al. report that mode-seeking divergences did better under temperature sampling while the choice barely mattered under greedy decoding ([paper](https://arxiv.org/abs/2306.13649), section 4.1), so the decoding can change the ranking |
| Noise | How many seeds, and how big is the gap against run-to-run spread? | DistilBERT reports medians of 5 runs, and many claims report one |
| Cost | Is the teacher's inference, the data generation and the filtering counted? | DistilBERT's 90 GPU hours excludes the teacher's pretraining |

Two of the rows are questions about what is missing from the writeup, not about what is wrong with it. Treat a missing answer as an open item, not as a fault: write it down and ask for it.

### Writing the review

Say what is fine first. State each hidden part as a cost: "the average hides the tasks where it fell by 10 points or more" is concrete, and "I don't trust the average" is not. Then name the measurement that would settle it, with its price, so the author can say yes or no. Lesson 23's baselines, held-out tasks and contamination checks are the usual answers.

## Practice

1. ▢ Predict which two of DistilBERT's nine GLUE tasks have the lowest student-to-teacher ratio, then run this on Table 1's numbers.

    ```python
    bert = dict(CoLA=56.3, MNLI=86.7, MRPC=88.6, QNLI=91.8, QQP=89.6,
                RTE=69.3, SST2=92.7, STSB=89.0, WNLI=53.5)
    distil = dict(CoLA=51.3, MNLI=82.2, MRPC=87.5, QNLI=89.2, QQP=88.5,
                  RTE=59.9, SST2=91.3, STSB=86.9, WNLI=56.3)
    for task in sorted(bert, key=lambda t: distil[t] / bert[t]):
        print(f"{task:5s} {100 * distil[task] / bert[task]:.1f}")
    print(f"mean of entries {sum(bert.values()) / 9:.1f} and {sum(distil.values()) / 9:.1f}")
    ```

<details markdown="1"><summary>Hint</summary>

Look for the tasks where the teacher scored far below 100 and the student fell further.

</details>

<details markdown="1"><summary>Check</summary>

RTE at 86.4 and CoLA at 91.1 are the lowest, and WNLI at 105.2 is the highest. The last line prints 79.7 and 77.0. The paper prints 79.5 for BERT-base, close to but not equal to the mean of its own nine entries, and I could not establish why. Either figure gives about 97% overall, which is the point: recompute a headline from the table before you quote it.

</details>

2. ▢ A paper reports that crowdworkers rated about 70% of a student's outputs as equal to or better than its teacher's. What do you conclude about capability, and what would you ask for?

<details markdown="1"><summary>Check</summary>

Nothing firm about capability. In Gudibande et al. the same kind of rating coexisted with little closing of the gap on tasks the imitation data did not support, because raters reward the style the student copied. Ask for targeted automatic evaluations on held-out tasks, and for raters or a check that can verify facts.

</details>

3. ▢ Hypothetical claim: "Our 7B student matches the teacher. On 500 prompts, a judge model preferred the student or tied in 62% of comparisons." The prompts came from the same generator as the distillation prompts, decoding was greedy for the student and sampled for the teacher, and cost is not stated. List the questions you would ask, most decision-changing first.

<details markdown="1"><summary>Check</summary>

First, population: prompts from the distillation generator are in-distribution, so ask for held-out tasks. Second, decoding: the two models should be decoded the same way, because the setting can move the ranking. Third, the judge: which model, checked for style bias, and a tie rate separated from preference. Fourth, baseline: a same-size model trained without the teacher. Last, cost: the teacher's generation and filtering counted. Also say what is fine: a judged comparison at 500 prompts is a reasonable first look.

</details>

4. ▢ Which check is evidence that distillation prompts did not leak into the test set?

    - a) A bigger judge scoring it higher
    - b) An overlap filter on test prompts
    - c) Averaging the scores over several seeds
    - d) A longer run on teacher outputs

<details markdown="1"><summary>Check</summary>

**b)** It checks the thing in question, as Gudibande et al. did with a BLEU filter at 20% against any training example. (a) and (c) change how the score is judged or averaged, not whether the inputs were seen. (d) does not test for overlap, and more of the same prompts can add to it.

</details>

5. ▢ Two papers compare forward and reverse KL for students. One evaluates with greedy decoding and finds little difference, the other samples at a high temperature and finds reverse KL clearly better. Can both be right, and what do you check first?

<details markdown="1"><summary>Check</summary>

Yes. Agarwal et al. report that mode-seeking divergences did better under temperature sampling and that the choice barely mattered under greedy decoding, which is the same split. Check the decoding setting of each evaluation first, then the task and model sizes, before treating the two as a contradiction.

</details>

## Real-world reps

- [ ] Find a model card or blog post that claims a small model matches a large one, and write one line for each row of the question table: the answer the post gives, or "not stated".
- [ ] Recompute one percentage from a results table in that post, using the table's own numbers, and write whether it reproduces.
- [ ] Tomorrow: write the review of that claim in five sentences, starting with what is fine and ending with the one measurement you would ask for.

## Going further

- [Distillation Review Checklist](../reference/distillation-review-checklist.md)
- [Sizing and Measuring](../reference/sizing-and-measuring.md)
- [Paper: "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717)
- [Paper: "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter", Sanh et al., 2019](https://arxiv.org/abs/1910.01108)
- [Paper: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
