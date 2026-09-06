---
title: 1. Held-out Data and Contamination
description: Why an eval number is only as trustworthy as what the model never saw
type: lesson
---

# Lesson 1. Held-out Data and Contamination

**Mission link:** "Defend the number against contamination" is half the mission, and it starts here: a number from a compromised eval set is not a number worth defending.
**Primary source:** [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
**Prerequisites:** none

## Know this

### What "held out" means

An eval set is **held out** when the model being judged never saw those exact examples, or close paraphrases of them, during training or fine-tuning. That single property is what lets a good score mean "this generalizes" rather than "this was memorized". Without it, a high score is uninformative: it cannot distinguish a model that learned the underlying skill from one that simply learned the answer key.

This is the same discipline as a held-out test set in any machine learning workflow, and it is easy to state and surprisingly easy to violate in practice.

### Contamination: two different failure modes

**Data contamination** is when eval examples, or near-duplicates of them, end up inside what the model was trained on. Two distinct paths cause it:

1. **Pretraining absorption.** Public benchmarks get posted online, scraped into web-crawl datasets, and end up inside a base model's pretraining corpus before anyone builds an eval on top of it. The model never saw your eval set specifically, but it may have seen the exact questions and answers of a benchmark you're relying on.
2. **Iterative overfitting to the eval.** No literal data leakage occurs, but a team runs the same eval set repeatedly while tuning a model or a prompt, and gradually shapes the system to pass the specific examples in front of them rather than the underlying capability. This is Goodhart's law in eval form: the eval set stops measuring the thing it was built to measure once it becomes the target of optimization.

Both produce the same symptom: a number that looks good and does not predict real-world behavior. They need different fixes. The first is addressed by choosing or building eval data unlikely to appear in a pretraining corpus (or by testing for its presence). The second is addressed by refreshing the eval set, or holding back a further slice of it, so it cannot be optimized against indefinitely.

### Testing for pretraining contamination

You can often detect the first failure mode directly. Golchin and Surdeanu's guided-instruction method gives a model the first part of a benchmark instance and asks it to complete the rest verbatim. A model that reproduces a benchmark item's exact continuation, beyond what a plausible guess would produce, is strong evidence that instance was in its training data. The same idea generalizes: if a model can reconstruct specifics of your eval set that a description alone would not give away (an unusual phrasing, an exact number, a rare proper noun), suspect contamination.

### What "defend the number" requires

Before quoting an eval score as evidence a change helped, you need an answer to: *why couldn't the model have gotten this right by memorization or by having been tuned against this exact set?* If you cannot answer that, the number describes the eval, not the model.

## Practice

1. ▢ A team fine-tunes a model and evaluates it on a well-known public benchmark, then reports a high score as proof the fine-tune helped. What question should you ask before trusting that score?

<details markdown="1"><summary>Check</summary>

Whether that benchmark's data (or close paraphrases of it) could plausibly be present in the model's pretraining corpus, since public benchmarks routinely get scraped into web-crawl training data. A high score on a contaminated benchmark says nothing about the fine-tune.

</details>

2. ▢ Distinguish: a model was never trained on your eval set's exact text, but your team has run that same 50-example eval set every week for six months while tuning prompts against it. Is this eval still trustworthy? Why or why not?

<details markdown="1"><summary>Hint</summary>

No literal data leakage is required for an eval to stop being informative.

</details>

<details markdown="1"><summary>Check</summary>

No, or at least it's now suspect. This is the second contamination pathway: iterative overfitting to the eval. Six months of tuning against the same 50 examples likely shaped the system to pass those specific examples rather than the underlying task, even with zero literal data leakage. The fix is refreshing the set or holding back an untouched portion of it.

</details>

3. ▢ You want to check whether a specific benchmark leaked into a model's pretraining data. Describe a test you could run, using the guided-instruction idea from this lesson.

<details markdown="1"><summary>Check</summary>

Give the model the first part of a benchmark instance (a question, or the start of a passage) and ask it to complete the rest verbatim. If it reproduces the exact continuation, including specifics a plausible guess wouldn't recover (precise wording, an unusual number, a rare name), that's strong evidence the instance was in its training data.

</details>

4. ▢ Which of these best states what "held out" means for an eval set?

   - a) The eval set is kept in a separate file from the training data
   - b) The model being judged never saw those examples, or close paraphrases, during training
   - c) The eval set was written by someone other than the model's developer
   - d) The eval set uses a different format than the training data

<details markdown="1"><summary>Check</summary>

**b)** The model being judged never saw those examples, or close paraphrases, during training. (a), (c) and (d) describe organizational or stylistic facts that don't, by themselves, prevent contamination.

</details>

## Real-world reps

- [ ] Pick an eval or benchmark you currently rely on. Ask, in writing: is it plausible this data appeared in the pretraining corpus of the model you're evaluating? Write down your reasoning either way.
- [ ] For that same eval, check whether it's been reused enough times, or tuned against enough, that Goodhart's law is a live risk. If so, note what you'd hold back or refresh.
- [ ] Tomorrow: try the guided-instruction completion test from this lesson on one benchmark instance against a model you have access to, and record what you find.

## Going further

- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Paper: "Time Travel in LLMs: Tracing Data Contamination in Large Language Models", Golchin and Surdeanu, 2023](https://arxiv.org/abs/2308.08493)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
