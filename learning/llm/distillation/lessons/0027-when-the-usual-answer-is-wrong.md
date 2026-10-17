---
title: "27. When the Usual Answer Is Wrong"
description: Recognise when distillation is the wrong call, and settle a disputed claim from the primary source
type: lesson
---

# Lesson 27. When the Usual Answer Is Wrong

**Mission link:** The track ends with trusting you to make the call on a distillation and to explain it to someone else. "Distill the big model into a small one" and "forward KL is the standard loss" are the usual answers, and each is true in some settings and false in others. This lesson is the cases where distillation is the wrong call, and a method for settling a dispute from the paper's own tables.
**Primary source:** [Paper: "On the Efficacy of Knowledge Distillation", Cho and Hariharan, 2019](https://arxiv.org/abs/1910.01348), sections 5.1 and 5.2
**Prerequisites:** [Lesson 19](0019-capacity-gap-and-hidden-traits.md), [Lesson 24](0024-distill-quantize-or-fine-tune.md), [Lesson 26](0026-replacing-a-model-others-depend-on.md), [Capacity gap](../GLOSSARY.md), [Forward KL](../GLOSSARY.md), [Reverse KL](../GLOSSARY.md)

## Warm-up

1. ▢ Lesson 5 contrasted forward and reverse KL. Which one spreads the student over every mode of the teacher, and which one commits to a single mode?

<details markdown="1"><summary>Check</summary>

[Forward KL](../GLOSSARY.md) spreads the student over every mode, because it penalises putting little probability where the teacher puts much. [Reverse KL](../GLOSSARY.md) commits to one mode, because it penalises putting probability where the teacher puts little.

</details>

2. ▢ Lesson 16 covered what on-policy distillation costs per step. What does the teacher have to do that it does not do when the student trains on fixed teacher outputs?

<details markdown="1"><summary>Check</summary>

Score the tokens of sequences the student generates during training, so every step needs fresh student samples and a teacher forward pass over them. Fixed teacher outputs are generated once, and the student's training steps do not wait on the teacher. See [on-policy distillation](../GLOSSARY.md).

</details>

3. ▢ Lesson 13 covered terms and licenses. What must you check before generating training data from a model you do not own?

<details markdown="1"><summary>Check</summary>

Whether the provider's terms or the model's license allow using its outputs to train another model, and on what conditions. Both are documents that change, so read the current text, not a summary of it.

</details>

## Know this

### The method

A usual answer arrives as a slogan without its conditions. Five steps decide whether it holds for you.

1. **Find the primary source.** The paper, not the post that cites it.
2. **Check the setting.** Models, sizes, data, year, and what was measured.
3. **Read the setup behind the table.** Baselines, number of trials, and how the reported number was picked.
4. **Compare the gap with the noise.** A one-point gap with no spread proves little.
5. **Test it on your task**, as lesson 23 describes.

None of the cases below says distillation is bad. Each says what its source supports and where it stops.

### Where the usual answer fails

| Usual answer | Wrong when | Source and limit |
|---|---|---|
| Distill the big model | No teacher is better than the student at your task, so there is nothing to imitate | R1 paper, appendix F: going beyond the teacher's frontier may need stronger base models and larger-scale RL. Gudibande et al. conclude that stronger base capabilities, not more imitation data, is how open models improve. My reasoning on top: imitation cannot beat its source on the task |
| Use the best available teacher | The terms or license forbid it | OpenAI's Terms of Use list using output to develop competing models among the things a user cannot do. The Llama 3.1 license lets you train on outputs but requires "Llama" at the start of the resulting model's name when distributed. Read the current text |
| A bigger teacher gives a better student | The student cannot absorb it, the capacity gap | Cho and Hariharan Table 1, Mirzadeh et al. Figure 2, Busbridge et al. section 4.2, below |
| A student can absorb what the teacher knows | The task needs knowledge the student cannot hold | Gudibande et al.: imitation improved style and instruction following but not factuality, coding or problem solving, with Natural Questions results regressing as imitation data grew |
| Fine-tune on teacher outputs once | On-policy training of the student on its own samples does better | Agarwal et al. section 4.1: on-policy and mixed variants consistently outperformed supervised ones in their summarization ablations, and on GSM8K on-policy GKD substantially outperformed the other approaches (Figure 9, section 4.3). It costs more per step (lesson 16) |
| Distill rather than quantize | Quantizing the model already meets the budget | The quantization sheet reports W8A8-FP effectively lossless at every size in Kurtic et al., on one model family: see its [review checklist](../../quantization/reference/quantization-review-checklist.md) |
| Distill rather than train small directly | Plenty of task data and no free teacher | Busbridge et al.: supervised learning outperforms distillation given enough student compute or tokens. A pretraining result, so an inference for task fine-tuning (lesson 24) |

Two rows run against the track's own hopes. The R1 paper finds distillation beating RL on the same 32B base (lesson 24), so "RL on the small model wins" is not a case this lesson can support, and no source read for this lesson shows plain fine-tuning on human data beating distillation on a task. Both stay out of the table.

### The capacity gap, from the tables

Cho and Hariharan ran an ImageNet student, ResNet18, with three teachers (Table 1, top-1 error, lower is better). Training the student from scratch gave 30.24. With ResNet18, ResNet34 and ResNet50 teachers, whose own errors were 30.24, 26.70 and 23.85, the students scored 30.57, 30.79 and 30.95. The better the teacher got, the worse the student got, and every distilled student was worse than the one trained without a teacher. The text says ResNet152 was also a teacher, but the table I read lists three rows. The authors also report a CIFAR-10 version in which student accuracy rises and then falls as the teacher grows, and that softening the teacher's probabilities with a higher temperature did not change this result (section 5.1).

Mirzadeh et al. show the same rise and fall for a 2-layer CNN student under teachers of 4, 6, 8 and 10 layers on CIFAR-10 and CIFAR-100, and give three competing factors, the third being that a more certain teacher gives less soft targets (Figure 2). Busbridge et al. fit the effect for language models: student cross-entropy decreases to an optimum and then rises with teacher size, and they argue the gap is one of learning capacity, hypothesis space and ability to optimize, of which relative size is a special case (sections 1 and 4.2, Figure 4).

Three sources, three settings, one direction. None of them is your pair of models, so "bigger is not always better" is a reason to test a teacher one size down, not a rule that the biggest is wrong.

### Settling a dispute: "forward KL is the standard loss"

A colleague says forward KL is standard. Start with the papers that tested it and read what each measured.

| Source | Setting | What was measured | Result |
|---|---|---|---|
| Busbridge et al., appendix G.5, Table 7 | 1.82B teacher to 546M student, C4 | Data cross-entropy, lower is better | Forward 2.42, reverse 2.70 |
| Muralidharan et al. (Minitron), appendix A.3, Table 16 | Minitron 8B depth-pruned, retrained with distillation | LM loss on validation sets | Forward KL 2.155, reverse KL 2.665 |
| Gu et al. (MiniLLM), abstract | Instruction following, GPT-2 and OPT students | GPT-4 feedback and other measures | Reverse KL reported as more suitable and the students higher quality |
| Agarwal et al. section 4.4 | FLAN-T5-XL to base, instruction tuning, MMLU and BBH | Few-shot score on held-out tasks | On-policy with reverse KL much better than forward KL |
| Agarwal et al. section 4.1 | XSum summarization, T5 students | Quality against diversity | The best divergence depended on task and on sampling: mode-seeking did better with temperature sampling, and the choice barely mattered under greedy decoding |

Read down the columns. The first two measure a loss on text, in settings close to pretraining, and forward KL wins. The last three measure the quality of instruction-following or summarization outputs, and reverse KL wins or the winner depends on decoding. Minitron's own text names the split: it cites reverse KL as a better fit for instruction following and Agarwal et al. for the task dependence, and finds forward KL best for its pruned base model.

One reading, which is my inference and not something these papers tested, is that a loss-on-text metric favours the divergence that is closest to that loss, and an output-quality metric favours the one that avoids low-probability continuations. What the tables support is smaller and enough: "forward KL is standard" is true of the pretraining-like settings read here, false in others, and the claim has to carry its setting. For an instruction-tuned student, the evidence in these tables points at testing reverse KL as well, under your own decoding.

Notice what settled it. Nobody consulted memory. The answer came from finding each source's table, reading what the number was a number of, and noticing that the settings split cleanly.

## Practice

1. ▢ Using Cho and Hariharan's Table 1, predict which of the three teachers gives the best student and whether any distilled student beats training from scratch, then run it.

    ```python
    scratch = 30.24
    for teacher, teacher_err, student_err in [
        ("ResNet18", 30.24, 30.57),
        ("ResNet34", 26.70, 30.79),
        ("ResNet50", 23.85, 30.95),
    ]:
        print(f"{teacher:9s} teacher {teacher_err:5.2f} student {student_err:5.2f} vs scratch {student_err - scratch:+.2f}")
    ```

<details markdown="1"><summary>Hint</summary>

Compare each student's error with 30.24, the error of the student trained without a teacher.

</details>

<details markdown="1"><summary>Check</summary>

The ResNet18 teacher gives the best student, 30.57, and every student is worse than scratch: by 0.33, 0.55 and 0.71 points of error. The most accurate teacher gave the worst student. This is one ImageNet setup with one student, so it is a counterexample to "bigger is always better", not a measure of the size of the effect elsewhere.

</details>

2. ▢ A team plans to distill a hosted model into a model it will sell. The provider's terms bar using output to develop models that compete with the provider. What do you recommend?

<details markdown="1"><summary>Check</summary>

Not to proceed with that teacher for that product, and to look for another route: a teacher whose license allows it, data written by people, or quantizing the model they already have. If the alternative is an open model such as Llama 3.1, its license allows training on outputs but requires the resulting model's name to begin with "Llama" and "Built with Llama" to be shown when it is distributed, so read the current license text against the product plan. Neither document is a legal opinion, so ask counsel before shipping.

</details>

3. ▢ A colleague says "forward KL is the standard loss, so use it for our instruction-tuned student". Answer from the table.

<details markdown="1"><summary>Check</summary>

Forward KL won where the metric was a loss on text in pretraining-like settings (Busbridge et al., Minitron), and reverse KL won or the winner depended on decoding where output quality of instruction following or summarization was the metric (MiniLLM, Agarwal et al.). Your student is instruction-tuned, so the evidence there points at testing both under your decoding, rather than at the default.

</details>

4. ▢ Which evidence would settle whether the capacity gap applies to your teacher and student?

    - a) The student's training loss curve at convergence
    - b) The teacher's own scores on public leaderboards
    - c) Your student's score under two teacher sizes
    - d) A paper reporting a different model family

<details markdown="1"><summary>Check</summary>

**c)** It is the experiment the three papers ran, on your pair and your task. (b) is the teacher's quality, and Cho and Hariharan show that rising teacher quality coexisted with falling student quality. (a) is a training signal, not task quality. (d) shows the effect exists elsewhere, not for you.

</details>

5. ▢ Mirzadeh et al. report, for a ResNet on CIFAR-10 (Table 1), 88.65 for plain distillation and 88.98 for their teacher assistant method, and say each reported number is the best top-1 test accuracy reached by the hyperparameter optimizer over 120 trials. What do you say about the 0.33 gap?

<details markdown="1"><summary>Check</summary>

Picking the best test accuracy over many trials favours both methods, and the table shows no spread, so a third of a point cannot be called a win from this table alone. It is not evidence the method fails: the larger gaps in the same table, such as 66.60 against 67.36 on ImageNet, are a better place to look, with the same caveat. Ask for repeated runs with seeds fixed and test accuracy not used to select.

</details>

## Real-world reps

- [ ] Take one distillation rule of thumb you rely on (for example "use the biggest teacher") and trace it to the paper. Write the models, the sizes, the year, what was measured and where your case differs.
- [ ] Open Table 7 of the Distillation Scaling Laws paper and appendix A.3 of the Minitron paper and write the one-line setup differences between them and MiniLLM, so you can answer the next "which loss" argument from the tables.
- [ ] Tomorrow: for the distillation you would most like to run, write the one case from the table above most likely to apply, and the measurement that would show whether it does.

## Going further

- [Distillation Review Checklist](../reference/distillation-review-checklist.md)
- [Paper: "On the Efficacy of Knowledge Distillation", Cho and Hariharan, 2019](https://arxiv.org/abs/1910.01348)
- [Paper: "Improved Knowledge Distillation via Teacher Assistant", Mirzadeh et al., 2019](https://arxiv.org/abs/1902.03393)
- [Paper: "Distillation Scaling Laws", Busbridge et al., 2025](https://arxiv.org/abs/2502.08606)
- [Paper: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
- [Paper: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Post-training](../../post-training/)
- [Resources](../RESOURCES.md)

---

This is the end of the track, and the habit it was built for is the one in this lesson: a distilled model is a claim about a teacher, a student, a loss, a data set and a set of tasks, so find where the claim comes from, check what it covered, and measure on your own tasks before you defend it to anyone else.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
