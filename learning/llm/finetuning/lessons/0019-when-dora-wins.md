# Lesson 19 — When DoRA Wins, and When It Doesn't

**Mission link:** "Can predict when DoRA beats LoRA before running it" is the bar for this stage. Prediction, not experiment.
**Primary source:** [Paper: "DoRA: Weight-Decomposed Low-Rank Adaptation" — Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
**Prerequisites:** [Lesson 18](0018-dora-magnitude-and-direction.md), [Lesson 17](0017-what-qlora-costs.md)

## Warm-up

1. ▢ What does DoRA's renormalisation prevent `BA` from doing?

<details markdown="1"><summary>Check</summary>

Changing magnitude. After renormalisation `BA` affects direction only, and magnitude comes from the separately trained `m`.

</details>

2. ▢ Why can't the column norm be cached between steps?

<details markdown="1"><summary>Check</summary>

It is the norm of `W₀ + BA`, and `BA` changes at every optimizer step.

</details>

3. ▢ Why must a quality comparison use several seeds?

<details markdown="1"><summary>Check</summary>

Because seed-to-seed variation frequently exceeds the effect being measured, so a single-seed difference cannot be distinguished from noise.

</details>

## Know this

### The reported pattern

DoRA's gains over LoRA are **largest at low rank and shrink as rank increases.**

The reasoning follows directly from the mechanism. At rank 4 or 8, the low-rank update has very little capacity, and any of that capacity spent on magnitude adjustment is capacity not spent on direction. DoRA hands magnitude to a separate, cheap, dedicated parameter, freeing the whole low-rank budget for direction. At rank 128 the budget is no longer scarce, so freeing a little of it changes less.

So the prediction rule is not "DoRA is better" but:

> **DoRA helps most exactly where LoRA's capacity is tightest.**

### When to expect a win

| Situation | Expect | Because |
|---|---|---|
| Very low rank (4–16) | Meaningful gain | Capacity is scarce; decoupling frees some |
| Rank forced low by constraints | Meaningful gain | Same reason, and you have no alternative |
| Mid rank (32–64) | Smaller gain | Capacity less scarce |
| High rank (128+) | Little or none | Capacity is not the binding limit |
| You could just raise rank instead | Raise the rank | Cheaper in wall-clock than DoRA's per-step cost |
| Step time is your constraint | Skip DoRA | You are paying tens of percent for a small gain |

That fifth row is the one worth internalising. If rank is a free variable, **raising rank is usually the better move than switching to DoRA**, because extra rank costs almost no memory (Lesson 7) and almost no time, while DoRA costs real time on every step. DoRA earns its place when rank is *not* free — when something other than memory is holding it down.

### What actually holds rank down

Worth being concrete, since the whole recommendation hinges on it:

- **Overfitting on a small dataset.** More rank means more memorisation. Here you genuinely cannot raise rank, and DoRA is a real option — you get better use of a rank you are deliberately keeping small.
- **A serving constraint on adapter size.** Rare, but if you distribute adapters or hold many in memory at once, size can bind.
- **Reproducing a published configuration.** You are pinned to their rank.
- **Total training time budget.** Note this one cuts *against* DoRA, not for it — DoRA is slower per step.

If none of these apply, rank is free, and the simpler action is available.

### Reading the claim critically

The DoRA paper reports gains across several tasks and model families, with the magnitude-direction analysis as its mechanistic argument. That analysis is genuinely illuminating and the method is well-motivated.

Three things to hold in mind:

**Reported gains are often small in absolute terms** — a point or two on a benchmark. Compare that against your seed noise before treating it as real on your task.

**The comparison baseline matters.** DoRA at rank 8 versus LoRA at rank 8 is the paper's comparison and is the right one for isolating the mechanism. DoRA at rank 8 versus LoRA at rank 32 is the comparison *you* face when deciding what to run, and it is a different question with possibly a different answer.

**Independent replication is thinner than for LoRA or QLoRA.** LoRA has years of practitioner evidence across countless tasks. DoRA has less. That is not a criticism of the method; it is a reason to measure on your own task rather than importing a conclusion.

### The decision procedure

1. Is rank free to raise? → Raise it. Do not use DoRA.
2. Is rank pinned low, and by what? → If by overfitting risk or a hard constraint, DoRA is a real candidate.
3. Is step time already the binding constraint? → Do not use DoRA.
4. Otherwise: run both, same seed set, same everything else, and compare against seed noise.

Step 4 is not a failure of the procedure. Being able to say "the expected effect here is small and I need to measure it" *is* the senior answer, and it is a much better position than either believing the paper uncritically or dismissing it.

## Practice

1. ▢ Why do DoRA's gains shrink as rank rises?

<details markdown="1"><summary>Check</summary>

Its benefit is freeing low-rank capacity from having to represent magnitude changes. When rank is scarce that freed capacity matters proportionally a lot; when rank is generous the capacity was not the limiting factor, so freeing some of it changes little.

</details>

2. ▢ You are at rank 8 and can raise rank freely. DoRA or more rank?

<details markdown="1"><summary>Check</summary>

More rank. It costs almost no memory and almost no time, whereas DoRA costs a per-step penalty on every step of every future run.

Reach for DoRA when rank is pinned by something — usually overfitting risk on a small dataset — not when it is a free variable.

</details>

3. ▢ 600 training examples, rank held at 8 to limit memorisation. Is DoRA worth trying?

<details markdown="1"><summary>Check</summary>

Yes. This is the case the method is best suited to: rank is deliberately low for a reason you cannot remove, so making better use of it is the only available improvement.

Measure it against LoRA at the same rank with several seeds, since the expected effect is small.

</details>

4. ▢ Distinguish the paper's comparison from yours.

<details markdown="1"><summary>Check</summary>

The paper compares DoRA and LoRA at matched rank, which correctly isolates the mechanism.

Your decision is between DoRA at the rank you can afford and LoRA at the rank you can afford — and since LoRA is faster per step, you may be able to afford more rank with it. Same numbers, different question.

</details>

5. ▢ Which most reliably predicts a DoRA win?

   - a) A large training dataset with many diverse examples
   - b) A low rank that cannot be raised for other reasons
   - c) A quantized base model in four-bit NF4 precision
   - d) A target module set covering all the linear layers

<details markdown="1"><summary>Check</summary>

**b)** A low rank that cannot be raised for other reasons.

Dataset size, base precision and target module coverage are all orthogonal to the mechanism. Scarcity of low-rank capacity is the thing DoRA relieves.

</details>

6. ▢ Your measured DoRA gain is 0.6 points, with seed spread of 1.4 points. What do you conclude and what do you do?

<details markdown="1"><summary>Check</summary>

That you have not detected an effect. The difference is well inside noise.

Either run enough seeds to resolve a difference that small — which may be many — or accept that the effect is too small to matter here and take the faster method. Deciding it is not worth resolving is a legitimate and often correct outcome.

</details>

## Real-world reps

- [ ] Run LoRA and DoRA at rank 8, three seeds each, everything else fixed. Compare the difference against the seed spread.
- [ ] Run LoRA at rank 32 for the same wall-clock budget as DoRA at rank 8. Note which produced the better model per unit of time.
- [ ] Tomorrow: write down, before running anything, your prediction for whether DoRA will help on your actual task and why. Keep it and check it later.

## Going further

- [Paper: "DoRA: Weight-Decomposed Low-Rank Adaptation" — Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
- [LoRA hyperparameters](../reference/lora-hyperparameters.md)
- [Lesson 20 — Judging a New PEFT Variant](0020-judging-a-new-variant.md)

---

Stuck on any of this, or unsure whether an answer counts? Bring it back to the session — that's what your teacher is for.
