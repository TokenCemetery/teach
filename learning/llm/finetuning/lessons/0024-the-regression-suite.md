# Lesson 24 — The Regression Suite

**Mission link:** "Build an eval that catches a regression before shipping" is the mission's own wording. This is that lesson.
**Primary source:** [Paper: "An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-tuning" — Luo et al., arXiv:2308.08747](https://arxiv.org/abs/2308.08747)
**Prerequisites:** [Lesson 23](0023-metrics-that-mean-something.md), [Lesson 22](0022-contamination-and-held-out-design.md)

## Warm-up

1. ▢ Why is loss the wrong basis for a decision?

<details markdown="1"><summary>Check</summary>

It scores agreement with one reference continuation, penalising correct alternatives and rewarding fluent errors. Use it for checkpoint selection, not decisions.

</details>

2. ▢ Two documented biases of model judges, and their mitigations?

<details markdown="1"><summary>Check</summary>

Position bias — randomise order and evaluate both orderings. Verbosity bias — compare at matched lengths or instruct the judge to disregard length.

</details>

3. ▢ Why is your task's held-out set blind to catastrophic forgetting?

<details markdown="1"><summary>Check</summary>

It is drawn from your task's distribution, so it cannot observe degradation on capabilities outside that distribution.

</details>

## Know this

### The failure this exists to catch

Fine-tuning moves weights toward your task. Abilities that were not reinforced can degrade, and this is **catastrophic forgetting**. The empirical literature finds it is not a rare edge case in continual fine-tuning of language models — general capabilities including instruction following measurably decline, and the effect can grow with model scale rather than shrinking.

The dangerous property is that **every number you are already looking at goes the right way.** Training loss falls, your held-out task metric improves, your probes look good — and the model has become worse at things you never measured. You ship, and the reports come from a direction your evaluation could not see.

A held-out set measures whether you learned the task. A regression suite measures whether you broke anything else. **They are different instruments and you need both.**

### What goes in it

Four categories. All four, not a selection.

**1. General instruction following.** Can it still follow an ordinary instruction with no relation to your task? Summarise something, answer a general question, follow a multi-step request.

**2. Format and behavioural compliance.** Does it still respect a system prompt? Still produce valid JSON when asked? Still stop when it should? A model trained on one rigid format sometimes loses the ability to produce any other.

**3. Safety and refusal behaviour.** If the base model refused certain requests, does the fine-tune still refuse them? **Fine-tuning on benign data can degrade safety alignment as a side effect** — this is a documented and repeatedly reproduced result, not a hypothetical. If you inherited alignment behaviour from an instruct model, you inherited a responsibility to check it survived.

**4. Adjacent capability.** Things near your task that you did not train. Fine-tuned on English support tickets? Check another language. Fine-tuned on one document type? Check another.

### Building it

Small, fixed, and read by a human.

```text
regression/
├── instruction-following.jsonl   # 20 general instructions
├── format-compliance.jsonl       # 20 schema and system-prompt cases
├── safety.jsonl                  # 20 cases the base refused
├── adjacent.jsonl                # 20 near-task, untrained cases
└── baseline/                     # base model outputs, committed
```

Eighty examples total. That is deliberately small — enough to catch a real regression, small enough that a person actually reads the diffs.

The critical, frequently-omitted step: **record the base model's outputs before you train, and commit them.** A regression is a *change*, so you need the before. Without a stored baseline you are left comparing against your memory of how the model used to behave, which is not evidence.

```python
# Run once, before any training. Commit the result.
for case in regression_cases:
    out = base_model.generate(**tok(case["prompt"]), do_sample=False, max_new_tokens=256)
    baseline[case["id"]] = tok.decode(out[0], skip_special_tokens=True)
```

Greedy decoding, so a diff means a weight change rather than a sampler roll.

### Reading it

Run the suite on every candidate checkpoint. Diff against the baseline. Then classify each change:

| Verdict | Meaning |
|---|---|
| Unchanged | Fine |
| Changed, still correct | Note it; fine |
| Changed, now wrong | **Regression — blocks the ship** |
| Changed, now better | A bonus, and worth understanding |

The third row is the whole point. One clear regression in safety or instruction following outweighs a couple of points on your task metric, because the failure mode is unbounded and the gain is not.

### Reducing forgetting, when you find it

Options roughly in order of what they cost you:

1. **Fewer steps, or an earlier checkpoint.** Forgetting grows with training. Often the cheapest fix, and it usually costs little task performance.
2. **Lower learning rate.** Smaller updates disturb less.
3. **Lower rank, or fewer target modules.** Less capacity to overwrite with.
4. **Mix in general instruction data.** A few percent of general instruction-following examples alongside your task data. Effective and well-established, and it costs you dataset purity rather than model quality.
5. **Keep the adapter unmerged and route.** The most complete answer: apply the adapter only for requests that need it, and serve the untouched base for everything else. Forgetting becomes irrelevant because the base is still there. Lesson 25.

Option 5 is the one people overlook, and it is often the correct architecture. If your fine-tune serves one narrow purpose inside a larger product, you do not need one model that does everything.

### Automate it

The suite should run on every checkpoint, unprompted, and refuse to pass on a regression. An evaluation that depends on someone remembering to run it will be skipped on the run where it mattered — the one under deadline pressure.

## Practice

1. ▢ Why does a held-out task metric that improves monotonically fail to rule out a regression?

<details markdown="1"><summary>Check</summary>

It is drawn from your task's distribution and therefore only observes your task. Capabilities outside that distribution are invisible to it, and those are exactly what forgetting damages.

You need a separate instrument aimed at what you are *not* training.

</details>

2. ▢ Name the four regression categories.

<details markdown="1"><summary>Check</summary>

General instruction following, format and behavioural compliance, safety and refusal behaviour, adjacent untrained capability.

Safety is the one most often left out, and fine-tuning on entirely benign data can degrade it.

</details>

3. ▢ You have a regression suite but no stored baseline. What can you conclude from running it?

<details markdown="1"><summary>Check</summary>

Very little. A regression is a change from prior behaviour, so without the prior behaviour you cannot identify one — only judge outputs in isolation, which will not reveal a subtle degradation.

Record and commit base-model outputs before training. This is the step that makes the suite work.

</details>

4. ▢ Task metric up 3 points; the model no longer refuses a request the base refused. Ship?

<details markdown="1"><summary>Check</summary>

No. A safety regression blocks the ship regardless of task gains — the downside is unbounded while three points is not.

Investigate: try an earlier checkpoint, a lower learning rate, mixing in general instruction data, or keeping the adapter unmerged and routing only relevant traffic to it.

</details>

5. ▢ Which most completely eliminates the forgetting problem?

   - a) Mixing general instruction data into the training set
   - b) Serving the base model unmerged and routing by request
   - c) Lowering the learning rate and training for fewer steps
   - d) Reducing the adapter rank and the target module count

<details markdown="1"><summary>Check</summary>

**b)** Serving the base model unmerged and routing by request.

The others reduce how much forgetting occurs. Routing means the unmodified base is still available for everything outside your task, so forgetting in the adapted path stops mattering.

</details>

6. ▢ Why greedy decoding for the regression suite?

<details markdown="1"><summary>Check</summary>

So that a difference from the baseline is attributable to changed weights rather than to sampling. With temperature above zero, every run differs and the diff carries no information.

</details>

## Real-world reps

- [ ] Write 20 regression cases — five in each category. Include at least one the base model refuses.
- [ ] Generate and commit base-model baseline outputs, greedily, before any training.
- [ ] Run the suite on your existing adapter and diff. Classify every change into the four verdicts.
- [ ] Tomorrow: wire the suite into your training script so it runs on every checkpoint without being asked.

## Going further

- [Paper: "An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-tuning" — Luo et al., arXiv:2308.08747](https://arxiv.org/abs/2308.08747)
- [Paper: "Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To!" — Qi et al., arXiv:2310.03693](https://arxiv.org/abs/2310.03693)
- [Failure modes](../reference/failure-modes.md)
- [Lesson 25 — Serving Adapters](0025-serving-adapters.md)

---

Stuck on any of this, or unsure whether an answer counts? Bring it back to the session — that's what your teacher is for.
