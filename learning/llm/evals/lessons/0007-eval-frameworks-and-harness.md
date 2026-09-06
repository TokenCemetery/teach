---
title: 7. Eval Frameworks and Building a Harness
description: The four stages every eval harness has, and choosing between building custom eval-as-code and reusing a standardized benchmark harness
type: lesson
---

# Lesson 7. Eval Frameworks and Building a Harness

**Mission link:** Stages 1 to 3 designed what to measure, how to hold data out, and how to score it; stage 4 is where that design becomes a runnable pipeline that produces the same number the same way every time, rather than a one-off script nobody can rerun.
**Primary source:** [Repo: openai/evals, OpenAI](https://github.com/openai/evals)
**Prerequisites:** [Lesson 6](0006-judge-bias-and-human-agreement.md), [Data contamination](../GLOSSARY.md)

## Warm-up

1. ▢ How do you test whether a pairwise judge is exhibiting position bias?

<details markdown="1"><summary>Check</summary>

Rerun the same comparison with the two responses' order swapped and check whether the verdict is consistent. If the judge picks whichever response comes first regardless of which one that is, the verdict is unreliable.

</details>

2. ▢ What is the right bar to compare a judge's agreement with human raters against?

<details markdown="1"><summary>Check</summary>

Human-versus-human agreement on the same comparisons, not a perfect 100% ceiling, since human raters don't agree with each other every time either.

</details>

## Know this

### Why a harness, not a one-off script

Every design decision from stages 1 to 3, which data is held out, which metric or judge grades a response, how a score is aggregated, only matters if it gets applied the same way every time an eval runs. A **harness** formalizes that pipeline into reusable, auditable code, so a rerun six months later on a new model checkpoint applies the exact same held-out set and grading logic as the first run did, rather than reconstructing it from memory or a half-remembered notebook cell. The harness is what turns a one-time analysis into a repeatable measurement.

### Four stages, in every harness

Regardless of which framework builds it, an eval harness breaks into the same four stages: **load** the held-out eval set (stage 1's discipline about what's in it and why it's trustworthy); **generate**, running the model under test against each example to produce its outputs; **grade**, applying the chosen metric or judge (stages 2 and 3) to each output; and **aggregate**, turning per-example scores into one summary number, a mean, a pass rate, whatever the mission calls for. Naming these stages explicitly matters because each one can undermine the final number independently: a contaminated load stage produces a number that means nothing regardless of how careful the grading is, a broken generation stage (the wrong model, a truncated response) produces garbage no metric can rescue, a miscalibrated grading stage (lesson 5's score compression, lesson 6's biases) corrupts otherwise-good outputs, and an aggregation stage that hides variance behind a single mean can make an unreliable result look solid.

### Two established frameworks, two different jobs

**openai/evals** is built for defining a custom eval as code: a completion function wraps whatever model is under test, an eval spec names the dataset and the grading logic, and a registry of existing evals shows the shape a working one takes. It fits a mission-specific task nobody has built an eval for yet. **lm-evaluation-harness** (EleutherAI) instead runs a model against a large library of pre-built, standardized benchmarks through declarative task configs, without writing a completion function or grading logic from scratch. It fits reusing an existing benchmark, especially when comparability with published numbers on that same benchmark matters more than tailoring the eval to a specific mission.

The choice follows the same principle as choosing a metric (lesson 4): match the tool to what the task actually needs. A brand-new capability with no existing benchmark needs custom eval-as-code. A capability a standardized benchmark already measures well needs the harness built to run that benchmark, not a hand-rolled reimplementation of it.

## Practice

1. ▢ A team evaluates each new model checkpoint by having someone manually run a script, tweak a few parameters by hand, and read the output. Six months later, a different person tries to reproduce a past result and gets a different number. What does building a harness, as opposed to this ad hoc process, actually fix?

<details markdown="1"><summary>Check</summary>

A harness formalizes the pipeline (which held-out data, which grading logic, how scores aggregate) into code that runs the same way every time, so a rerun months later by a different person applies the identical process rather than reconstructing it from memory, which is exactly where the reproducibility failure in this scenario came from.

</details>

2. ▢ Name the four stages every eval harness has, and give one way each stage could undermine the final number even if the other three are done well.

<details markdown="1"><summary>Check</summary>

Load: a contaminated or non-held-out eval set (stage 1) makes the number meaningless regardless of grading quality. Generate: running the wrong model version or truncating outputs produces garbage no metric can fix. Grade: a miscalibrated metric or judge (lessons 3-6) corrupts scoring of otherwise-fine outputs. Aggregate: collapsing per-example scores into a single mean can hide high variance or a few catastrophic failures behind a number that looks solid.

</details>

3. ▢ A team wants to evaluate a genuinely new capability their model targets, one no public benchmark currently measures. Should they reach for openai/evals or lm-evaluation-harness, and why?

<details markdown="1"><summary>Check</summary>

openai/evals, since it's built for defining a custom eval as code, a completion function plus a grading spec, when no existing benchmark covers the task. lm-evaluation-harness is built to run pre-existing, standardized benchmarks through declarative configs, which doesn't help when the capability being measured has no such benchmark yet.

</details>

4. ▢ A team wants to compare their model's performance on a well-known public benchmark against published numbers from other models. Should they reach for openai/evals or lm-evaluation-harness, and why?

<details markdown="1"><summary>Check</summary>

lm-evaluation-harness, since it runs a model against standardized, pre-built benchmark task configs the way other reported numbers on that same benchmark were produced, making the comparison meaningful. Hand-rolling the same benchmark in openai/evals risks subtle implementation differences that break comparability with published results.

</details>

5. ▢ Which claim is true of the four-stage shape (load, generate, grade, aggregate) an eval harness has?

   - a) Only the grading stage matters; load, generate, and aggregate are implementation details with no effect on trustworthiness
   - b) Each stage can independently undermine the final number, so a trustworthy result requires all four to be sound, not just the grading logic
   - c) The four stages only apply to LLM-as-judge evals, not task-specific-metric evals
   - d) Aggregation is unnecessary if the grading stage produces a single score per example

<details markdown="1"><summary>Check</summary>

**b)** Every stage is a place trust can break, independent of the others, as the worked examples in this lesson showed. (a) is false: a contaminated load stage or a broken generation stage ruins the result regardless of grading quality. (c) is false: the same four stages apply whether grading uses exact match, functional correctness, or an LLM judge. (d) is false: aggregation still has to turn many per-example scores into the one summary number an eval actually reports, and how that's done (a mean versus something that reports variance) affects how much the summary number can be trusted.

</details>

## Real-world reps

- [ ] For an eval you run or plan to run, write down its four stages explicitly (what's loaded, what generates outputs, what grades them, how they aggregate) even if it currently lives in a single script.
- [ ] Look at one existing eval in the openai/evals registry or an lm-evaluation-harness task config, and identify its load, generate, grade, and aggregate stages in the actual code or config.
- [ ] Tomorrow: decide, for a capability you want to evaluate, whether a standardized benchmark already covers it well enough to reuse, or whether it needs a custom eval built from scratch.

## Going further

- [Repo: openai/evals, OpenAI](https://github.com/openai/evals)
- [Repo: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
