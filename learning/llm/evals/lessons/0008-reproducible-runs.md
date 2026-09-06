---
title: 8. Reproducible Runs
description: Why the same eval can produce different numbers on different runs, and what a trustworthy result has to log alongside the score
type: lesson
---

# Lesson 8. Reproducible Runs

**Mission link:** This is the stage 4 capstone: a harness (lesson 7) is only half the job. A number it produces is trustworthy only once its run-to-run variance is understood and what produced it is logged, which is what lets a later comparison mean anything.
**Primary source:** [Repo: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
**Prerequisites:** [Lesson 7](0007-eval-frameworks-and-harness.md), [Data contamination](../GLOSSARY.md)

## Warm-up

1. ▢ Name the four stages every eval harness has.

<details markdown="1"><summary>Check</summary>

Load the held-out eval set, generate the model's outputs, grade them with the chosen metric or judge, and aggregate per-example scores into one summary number.

</details>

2. ▢ When should a team reach for openai/evals rather than lm-evaluation-harness?

<details markdown="1"><summary>Check</summary>

When evaluating a mission-specific capability no existing standardized benchmark covers, since openai/evals is built for defining a custom eval as code, where lm-evaluation-harness is built to run pre-existing benchmark configs.

</details>

## Know this

### Why the same eval can give two different numbers

A model sampled at a nonzero temperature produces different completions on different runs, even against the identical prompt, which means different per-example scores and a different aggregate number each time the eval runs, with nothing wrong having happened. If grading also uses an LLM judge (stage 3), that adds a second layer of sampling noise on top of the model-under-test's own variance. None of this is a bug in the harness; it's the harness faithfully reporting a stochastic process, and it means a single run's number is a sample from a distribution, not a fixed fact about the model.

### The determinism trade-off

Setting temperature to 0 (greedy decoding) removes generation-side randomness and makes runs far more repeatable, which is attractive for an eval whose grading depends on exact reproducibility, like exact match. The cost: greedy decoding may not reflect how the model actually behaves in deployment, if the deployed system samples at a nonzero temperature. An eval run entirely greedy can be measuring a mode the real system rarely uses. Where the deployed behavior genuinely samples, the more honest approach is running multiple samples per example at the deployment temperature (the same idea lesson 4's pass@k used for code) and reporting the spread across them, not just a single run's point value.

### A seed helps, but does not guarantee identical results

Fixing a random seed for generation reduces variance between runs on the same setup, but it is not a guarantee of bit-identical results across different hardware, different library versions, or different batch compositions, since floating-point computation is not perfectly associative across all of those. A seed is a real, useful control, not an absolute one; treating "we set a seed" as proof two runs are directly comparable is overclaiming what a seed can promise.

### What makes a reported number defensible later

A number alone, with nothing about how it was produced, cannot be compared honestly against a later number, from a rerun, a different checkpoint, or a different eval cycle: any difference between them could be a real change or just pipeline variance, and nothing in a bare score can tell which. A defensible result logs, alongside the score, what actually produced it: the random seed used, the generation temperature, the model and framework versions, the eval set's version, and, when multiple samples were run, the spread across them, not only their mean. This is what a later comparison, or the go/no-go call stage 5 builds toward, actually needs to be honest about whether an observed difference reflects the model or the noise.

## Practice

1. ▢ A team runs the same eval against the same model twice, at temperature 0.7, and gets two different aggregate scores. Is this evidence the harness is broken? Why or why not?

<details markdown="1"><summary>Check</summary>

No. A nonzero temperature makes generation stochastic, so different completions, and so different per-example scores, are expected across runs even with nothing wrong. The harness is faithfully reporting a stochastic process; the single-run number is a sample, not a fixed fact.

</details>

2. ▢ What does setting temperature to 0 for an eval buy, and what does it cost, if the deployed system actually samples at temperature 0.7?

<details markdown="1"><summary>Check</summary>

It buys repeatability: greedy decoding removes generation-side randomness, so runs become far more consistent. It costs realism: the eval is measuring a decoding mode (greedy) the real system rarely uses, so the result may not reflect how the model actually behaves when deployed at 0.7.

</details>

3. ▢ Why doesn't fixing a random seed guarantee two eval runs will produce identical results?

<details markdown="1"><summary>Hint</summary>

Think about what else could differ between two runs besides the seed.

</details>

<details markdown="1"><summary>Check</summary>

A seed controls the randomness within a given setup, but floating-point computation isn't perfectly associative across different hardware, library versions, or batch compositions, so those differences can still produce different results even with the same seed. A seed is a real control, not an absolute guarantee of bit-identical output.

</details>

4. ▢ Team A reports an eval score of 72.3 for a model. A month later, team B reruns "the same eval" on the same model and gets 69.8, with no seed, temperature, or version information logged from team A's original run. What can honestly be concluded from the 2.5-point gap?

<details markdown="1"><summary>Check</summary>

Very little, on its own. Without knowing the temperature, seed, model and framework versions, and eval set version team A used, there's no way to tell whether the gap reflects a real change (a different checkpoint, a different eval set version) or ordinary run-to-run variance from sampling. The honest conclusion is that the comparison is not yet meaningful until both runs' production details are known and matched, or the variance across repeated runs is measured directly.

</details>

5. ▢ Which claim is true of what makes a reported eval number defensible?

   - a) A single run's score is sufficient on its own, as long as the harness ran without errors
   - b) The score should be reported alongside what produced it (seed, temperature, versions, eval set version) and, when relevant, its spread across multiple runs
   - c) Setting a random seed guarantees identical results across any hardware or library version
   - d) Greedy decoding should always be used for evals, regardless of the deployed system's actual sampling temperature

<details markdown="1"><summary>Check</summary>

**b)** Logging the production details and, where sampling is involved, the spread across runs, is what lets a later comparison distinguish a real change from noise. (a) is false: a lone number can't be compared against anything later without knowing what produced it. (c) is false: a seed reduces but doesn't eliminate variance across different hardware or versions. (d) is false: greedy decoding trades away realism when the deployed system actually samples, which is a real cost, not a free choice.

</details>

## Real-world reps

- [ ] For an eval you run, check whether its harness currently logs the seed, temperature, and model/framework versions alongside the score, and add whatever is missing.
- [ ] If your eval samples at a nonzero temperature, run it multiple times (or multiple samples per example) and record the spread across runs, not just one number.
- [ ] Tomorrow: find a past eval result you or your team reported, and check whether enough was logged alongside it to know if a future rerun would be directly comparable.

## Going further

- [Repo: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
- [Repo: openai/evals, OpenAI](https://github.com/openai/evals)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
