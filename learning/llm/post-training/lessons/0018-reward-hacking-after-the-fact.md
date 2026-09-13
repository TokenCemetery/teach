---
title: 18. Reward Hacking After the Fact
description: A held-out reward model can catch drift during training; a finished model needs a different kind of check
type: lesson
---

# Lesson 18. Reward Hacking After the Fact

**Mission link:** "Can separate a genuine capability gain from a reward-hacking or judge-bias artifact" is the Success looks like bullet this stage serves, and this lesson closes it, handing the full methodology off to `llm/evals` rather than restating it.
**Primary source:** [Reference: "LLM-as-Judge: Prompt Design, Calibration, and Bias", `llm/evals`](../../evals/reference/llm-as-judge.md)
**Prerequisites:** [Lesson 17](0017-measuring-the-alignment-tax.md), [Over-refusal](../../evals/GLOSSARY.md)

## Warm-up

1. ▢ Why did Ouyang et al. test InstructGPT against held-out labelers, people who contributed no training data at all?

<details markdown="1"><summary>Check</summary>

To check whether the model's aligned behavior generalizes beyond the specific people whose preferences shaped training, rather than only fitting closely to that particular group.

</details>

2. ▢ What did the 25% reduction in toxic outputs add to a fair account of the alignment tax, beyond the SQuAD/DROP/HellaSwag/WMT regressions?

<details markdown="1"><summary>Check</summary>

Evidence that alignment training measurably helped on at least one axis, not only cost something; a fair account needs both directions, not only the regressions.

</details>

## Know this

### A different question than the training-time check

Lesson 5's train-PM-versus-test-PM divergence is a check run *during* training, comparing a policy against a reward model it was never optimized against. Evaluating a *finished* aligned model asks a related but distinct question: given only the model and its evaluation scores, with no second reward model to compare against, how do you tell whether a high score reflects genuine improvement rather than an artifact of however the evaluation itself was built?

### A concrete symptom: over-refusal

`llm/evals` names a specific, well-documented failure this question is really about: **over-refusal**, a model declining a prompt that is actually safe, typically because it superficially resembles an unsafe one. A model that refuses aggressively can score deceptively well on a safety benchmark built mostly from unsafe prompts, since refusing almost everything looks identical to a genuinely careful model on that specific test, while quietly failing the much larger set of safe prompts it should have answered. This is Lesson 5 and Lesson 15's blanket-deflection failure, seen from the evaluation side rather than the training side: a red-team-style eval that only checks unsafe prompts cannot detect it, because over-refusal is a failure on the safe prompts the eval never asked.

### Judge bias is the same problem, one level up

Where an evaluation itself uses a model, rather than a fixed benchmark, to judge outputs (an increasingly common setup this track's own RLAIF and Constitutional AI lessons already depend on), that judge can be fooled in its own specific ways: preferring longer answers regardless of quality, or being swayed by which answer happens to be shown first. `llm/evals`'s reference on LLM-as-judge design covers these failure modes, and the calibration checks that catch them, in full. A high judge-assigned score is only as trustworthy as the judge's own calibration against these known biases; an uncalibrated judge can be gamed by a policy in a way that looks, from the outside, exactly like genuine improvement.

### Why this hands off rather than restates

Designing a judge prompt, checking a judge's calibration, and measuring a judge's agreement against human raters are `llm/evals`'s own subject, covered there in the depth this track does not need to repeat. What this track owns is narrower and specific to post-training: knowing that a post-training pipeline's own evaluation is exposed to exactly this risk, recognizing a concrete symptom like over-refusal when it appears, and treating a suspiciously high safety or preference score with the same skepticism Lesson 5's train-PM-versus-test-PM comparison already modeled during training.

## Practice

1. ▢ A safety benchmark consisting entirely of unsafe prompts reports that a model refuses 98% of them, an apparently excellent score. What does this benchmark, by itself, fail to tell you about the model?

<details markdown="1"><summary>Check</summary>

Whether the model also refuses prompts that are actually safe. A benchmark built only from unsafe prompts cannot detect over-refusal, since a model that refuses nearly everything looks identical to a genuinely careful one on this specific test.

</details>

2. ▢ Why is a model refusing an actually-safe prompt a genuinely different failure from a jailbreak succeeding?

<details markdown="1"><summary>Check</summary>

A jailbreak is the model failing to refuse something it should have refused; over-refusal is the model refusing something it should not have refused. They are opposite-direction failures, and an eval built to catch one (a red-team, unsafe-prompt-only benchmark) cannot detect the other.

</details>

3. ▢ An evaluation uses a language model as a judge to score which of two aligned model outputs is better. What does this lesson say you should check before trusting a large gap between two models' scores?

<details markdown="1"><summary>Check</summary>

Whether the judge itself is calibrated against known biases (such as favoring longer answers or whichever answer appears first), per `llm/evals`'s LLM-as-judge material; an uncalibrated judge can be gamed in a way that produces a score gap that looks like genuine improvement but is not.

</details>

## Real-world reps

- [ ] Read `llm/evals`'s [LLM-as-Judge reference sheet](../../evals/reference/llm-as-judge.md) and identify one calibration check it recommends that you would apply to a post-training evaluation before trusting its results.
- [ ] Find a published safety evaluation for an aligned model and check whether it reports an over-refusal rate on safe prompts, in addition to a refusal rate on unsafe ones. Note which one, if either, is missing.
- [ ] Tomorrow: for an evaluation you have access to or can imagine (a safety benchmark, a preference-judge setup), name one concrete symptom, like over-refusal or a known judge bias, you would check for before trusting a headline score from it.

## Going further

- [Reference: "LLM-as-Judge: Prompt Design, Calibration, and Bias", `llm/evals`](../../evals/reference/llm-as-judge.md)
- [Resources](../RESOURCES.md)

---

Stage 9 covered separating a genuine alignment gain from an artifact, at training time and after the fact. Stage 10 closes the arc: choosing between everything this track has covered, for a stated budget, and defending that choice.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
