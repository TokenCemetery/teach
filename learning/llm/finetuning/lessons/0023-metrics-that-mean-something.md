# Lesson 23 — Metrics That Mean Something

**Mission link:** "Prove it worked" is in the mission. A number you cannot defend is not proof.
**Primary source:** [Paper: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" — Zheng et al., arXiv:2306.05685](https://arxiv.org/abs/2306.05685)
**Prerequisites:** [Lesson 22](0022-contamination-and-held-out-design.md), [Lesson 12](0012-reading-a-training-run.md)

## Warm-up

1. ▢ Why three splits rather than two?

<details markdown="1"><summary>Check</summary>

Selecting against a set fits to it. Validation absorbs your selection; test stays untouched so it can give an unbiased estimate.

</details>

2. ▢ Roughly how many held-out examples to detect a 2-point difference?

<details markdown="1"><summary>Check</summary>

Thousands. The requirement grows quadratically as the difference shrinks.

</details>

3. ▢ Name two things loss cannot see.

<details markdown="1"><summary>Check</summary>

Whether generations are usable, and whether capabilities outside the task's distribution have degraded.

</details>

## Know this

### Why loss is not the metric

Cross-entropy loss on held-out data is genuinely useful — it is cheap, it is stable, and it is the right thing to watch during a run. It is not a measure of whether the model does your job.

Loss measures next-token surprise against one specific reference continuation. It therefore penalises a differently-worded correct answer and rewards a fluent wrong one. Two models with equal held-out loss can differ substantially in usefulness, and the direction is not predictable.

**Use loss for checkpoint selection. Use a task metric for decisions.**

### Choosing by task shape

| Task shape | Metric | Watch for |
|---|---|---|
| Classification | Accuracy; per-class precision and recall; F1 | Class imbalance makes accuracy meaningless |
| Extraction | Exact match on the field; F1 over spans | Normalise before comparing |
| Structured output | Schema validity rate, then field-level correctness | Two separate failures — measure both |
| Code | Execution against tests | Passing tests, not resembling the reference |
| Free-form generation | Rubric scoring, human or model-judged | The hard case; see below |
| Retrieval-adjacent | Groundedness, citation accuracy | Fluency masks unsupported claims |

Note what is missing: for anything with a checkable answer, **check the answer.** Execute the code. Validate the schema. Compare the extracted field. These are cheap, objective, and far better than any similarity score.

### On surface-similarity metrics

BLEU, ROUGE and their relatives measure n-gram overlap with a reference. They were built for machine translation and summarisation, and for instruction-following tasks they are weak: a correct answer phrased differently scores badly, a wrong answer that reuses the reference's vocabulary scores well.

Use them only when overlap genuinely is the thing you care about, and never as the only metric. If you find yourself optimising ROUGE on a task that is not summarisation, stop.

### Structured output: two failures, two numbers

For JSON or any schema, always report both:

1. **Validity** — did it parse and satisfy the schema?
2. **Correctness** — given that it parsed, are the values right?

Collapsing these hides which problem you have. A model at 99% validity and 60% correctness needs better data. One at 60% validity and 95% correctness needs format training, or constrained decoding at serving time, which may make the problem disappear without retraining at all.

### Model-as-judge, used carefully

For free-form output, having a strong model score against a rubric is often the only scalable option. It works, and it has documented biases you must control for:

- **Position bias** — judges favour whichever response is presented first. Mitigate by randomising order and, for pairwise comparison, evaluating both orderings.
- **Verbosity bias** — longer answers score higher regardless of quality. Watch whether your fine-tune simply got wordier.
- **Self-preference** — judges tend to favour text resembling their own output.
- **Rubric sensitivity** — small wording changes in the rubric shift scores materially.

The non-negotiable step: **calibrate the judge against human labels.** Score 50–100 examples yourself, run the judge on the same ones, and measure agreement. If agreement is poor, the judge's numbers are decoration. If it is good, you have earned the right to scale it — and you have a number quantifying how much to trust it.

A concrete, robust setup: pairwise comparison of base versus fine-tuned output, both orderings, with a rubric naming the specific criteria you care about, reported as a win rate. Pairwise judging is more reliable than absolute scoring, which drifts.

### Report uncertainty or report nothing

A single number with no spread is not a result. Minimum standard:

- **Confidence intervals** on the metric. For a proportion, bootstrap or use a binomial interval.
- **Multiple seeds** when comparing training configurations, since run-to-run variance is often larger than the effect.
- **Paired comparison** on identical examples (Lesson 22).
- **The n** the number is computed over, stated.

"71.2 versus 70.8" is not a finding. "71.2 ± 2.1 versus 70.8 ± 1.9 over n=340, three seeds" is a finding, and the finding is that you have not detected a difference.

### Read the outputs

Whatever your metric, read a sample of actual generations — including the failures — every time. Metrics compress, and the thing they compress away is usually the thing you needed to know: the model has started refusing, or emitting a preamble, or truncating, or answering a subtly different question. No aggregate reveals this. Ten minutes of reading does.

## Practice

1. ▢ Two models have identical held-out loss. Can one be substantially more useful?

<details markdown="1"><summary>Check</summary>

Yes. Loss measures agreement with one reference continuation, so it penalises correct answers phrased differently and rewards fluent wrong ones.

Equal loss is compatible with a large difference in task performance, in either direction. This is why loss selects checkpoints and task metrics make decisions.

</details>

2. ▢ Your model emits JSON. What two numbers do you report, and why not one?

<details markdown="1"><summary>Check</summary>

Schema validity rate, and field-level correctness among valid outputs.

One combined number hides which problem you have. High validity with low correctness is a data problem; low validity with high correctness is a formatting problem that constrained decoding may solve without retraining.

</details>

3. ▢ Your fine-tune's judge score rose from 6.2 to 7.1. Average response length rose from 90 to 340 tokens. Concern?

<details markdown="1"><summary>Check</summary>

Yes — verbosity bias. Judges reliably favour longer answers regardless of quality, so much of that gain may be length.

Control for it: compare at matched lengths, instruct the judge explicitly to disregard length, or check whether users actually prefer the longer output. The score alone does not distinguish "better" from "longer".

</details>

4. ▢ Which metric best evaluates a code-generation fine-tune?

   - a) ROUGE against the reference implementation provided
   - b) Execution against a test suite for each problem
   - c) Held-out cross-entropy loss on the code tokens
   - d) A model judge scoring readability and correctness

<details markdown="1"><summary>Check</summary>

**b)** Execution against a test suite for each problem.

Code has an objective correctness criterion, so use it. Overlap metrics reward resembling the reference rather than working; loss has the same problem; a judge is unnecessary indirection when you can simply run the code.

</details>

5. ▢ What single step earns the right to trust a model judge at scale?

<details markdown="1"><summary>Check</summary>

Calibrating it against human labels — scoring 50–100 examples yourself and measuring agreement with the judge on the same items.

Without that, the judge's numbers are unvalidated. With it, you have both justification and a quantified degree of trust.

</details>

6. ▢ Your classifier fine-tune reports 94% accuracy. What do you need to know before believing it means anything?

<details markdown="1"><summary>Check</summary>

The class distribution. If 94% of examples belong to one class, a model that always guesses that class scores 94% and has learned nothing.

Report per-class precision and recall, or a balanced metric. Accuracy on imbalanced data is one of the most misleading numbers in common use.

</details>

## Real-world reps

- [ ] Choose your primary metric and write one paragraph defending why it measures what you care about. Name what it misses.
- [ ] Compute a confidence interval on your current metric. Decide whether your held-out set can support the comparison you want.
- [ ] If using a model judge: hand-label 50 examples, run the judge on the same ones, and report agreement.
- [ ] Tomorrow: read twenty actual generations including every failure. Write down one thing the metric did not tell you.

## Going further

- [Paper: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" — Zheng et al., arXiv:2306.05685](https://arxiv.org/abs/2306.05685)
- [Code: lm-evaluation-harness — EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
- [Lesson 24 — The Regression Suite](0024-the-regression-suite.md)

---

Stuck on any of this, or unsure whether an answer counts? Bring it back to the session — that's what your teacher is for.
