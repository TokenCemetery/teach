---
title: 10. Defending the Go/No-Go Call
description: How to set a regression threshold honestly, and everything a complete go/no-go defense has to cite
type: lesson
---

# Lesson 10. Defending the Go/No-Go Call

**Mission link:** This is the mission's final lesson: proving a model change helped ends in a ship or don't-ship call, and defending that call means naming a threshold set before the result was seen and citing every upstream choice, from held-out data to statistical significance, that makes the number behind it trustworthy.
**Primary source:** [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
**Prerequisites:** [Lesson 9](0009-statistical-significance-vs-noise.md), [Data contamination](../GLOSSARY.md)

## Warm-up

1. ▢ A baseline model passes 70 out of 100 eval examples; a new variant passes 76 out of 100. Is the six-point gap clearly larger than the noise, based on the standard error of each proportion?

<details markdown="1"><summary>Check</summary>

Not clearly. Each proportion's standard error is roughly 4 to 5 points at N = 100, so a six-point gap is not obviously larger than the combined noise; it's suggestive, not conclusive, on this sample size alone.

</details>

2. ▢ What should be logged alongside a reported eval score to make a later comparison meaningful?

<details markdown="1"><summary>Check</summary>

The random seed, generation temperature, model and framework versions, eval set version, and, when multiple samples were run, the spread across them, not just their mean.

</details>

## Know this

### A threshold set after seeing the result isn't a threshold

A **regression threshold** names, in advance, how much a metric is allowed to drop, or how much it must improve, for a change to ship. Setting it before the eval runs matters as much as having one at all: a threshold chosen after seeing the number is free to bend toward whatever answer someone wanted, the same failure lesson 1 described for an eval set tuned against repeatedly until it stops measuring anything real. A threshold decided in advance, tied to what the product actually needs (how much a regression on this metric would cost users, how much improvement would matter), is the only kind that can honestly be defended later.

### A threshold has to respect the noise floor

Lesson 9 showed that a score's standard error depends on sample size; a threshold tighter than that noise floor is not a real threshold, it's a coin flip dressed up as a decision. Demanding "no regression larger than 1 point" on a metric whose standard error is 4 points at the current sample size means the eval cannot actually tell a 1-point regression from ordinary noise, so the threshold cannot be honestly enforced without either loosening it to something the eval can resolve, or growing the sample size until it can.

### An inconclusive result is not a default answer

When an observed difference falls inside the noise (lesson 9), the honest conclusion is that there isn't enough evidence yet, not "ship it, since it's not clearly worse" and not "block it, since it's not clearly better." Both of those treat an absence of evidence as evidence of something, which it isn't. The correct response to an inconclusive result is to gather more data, more eval examples, more samples, whichever lesson 9's math says would tighten the estimate, not to pick whichever default happens to be more convenient.

### What a complete defense has to cite

A go/no-go call is defended, not merely reported, when it names: the metric and why it fits the task (lessons 3 and 4); why the held-out set is honest against contamination (lessons 1 and 2); if an LLM judge was used, its prompt design and its measured calibration and bias checks (lessons 5 and 6); the harness that produced the number and what was logged to make it reproducible (lessons 7 and 8); and the statistical case that the observed difference clears a threshold set in advance and is clearly larger than the noise the sample size could produce (lesson 9 and this lesson). A call that only states a headline number, with none of this, is a vibe with decimal places; that is precisely the outcome the mission set out to prevent.

## Practice

1. ▢ A team sets its regression threshold ("no more than 1 point of regression allowed") only after seeing that their new model scored exactly 1.2 points below baseline. What's wrong with this threshold, regardless of whether 1.2 points is a real regression?

<details markdown="1"><summary>Check</summary>

The threshold was chosen after seeing the result, which means it can be, and in this case plausibly was, bent to justify whatever answer was already wanted. A threshold only defends a decision when it was fixed in advance, tied to what the product actually needs, not adjusted retroactively to fit the observed number.

</details>

2. ▢ A team's metric has a standard error of about 4 points at their current sample size, and they want to enforce a threshold of "no more than 1 point of regression." What's wrong with defending a go/no-go call against this threshold as currently measured?

<details markdown="1"><summary>Hint</summary>

Compare the size of the threshold to the size of the noise the eval can actually resolve.

</details>

<details markdown="1"><summary>Check</summary>

The eval cannot reliably distinguish a 1-point regression from ordinary sampling noise when the standard error is 4 points; a measured 1-point difference in either direction is well within what chance alone could produce. The threshold needs to be loosened to something the current sample size can actually resolve, or the sample size needs to grow until a 1-point difference becomes distinguishable from noise.

</details>

3. ▢ An eval shows a score difference that falls inside the estimated noise: not clearly an improvement, not clearly a regression. A teammate argues "let's ship it, since it's not clearly worse." What's the problem with that reasoning?

<details markdown="1"><summary>Check</summary>

An inconclusive result is evidence of not having enough data yet, not evidence that nothing changed. Treating "not clearly worse" as license to ship is treating an absence of evidence as evidence of safety, which the noise-floor reasoning doesn't support; the honest move is to gather more evidence (a larger sample, more runs) rather than defaulting to either ship or block.

</details>

4. ▢ List what a complete go/no-go defense needs to cite, pulling one thing from each of this workspace's earlier stages.

<details markdown="1"><summary>Check</summary>

The metric chosen and why it fits the task (stage 2). Why the held-out eval set is honest against contamination (stage 1). If an LLM judge graded the result, its prompt design and measured calibration and bias checks (stage 3). The harness that produced the number and what was logged for reproducibility (stage 4). The statistical case that the difference clears a pre-registered threshold and is clearly larger than the noise the sample size allows (stage 5, this lesson and lesson 9).

</details>

5. ▢ Which claim is true of a defensible regression threshold?

   - a) It should be set after seeing the eval result, to reflect what actually happened
   - b) It should be fixed before the eval runs and set no tighter than the noise floor the sample size can resolve
   - c) A looser threshold is always more defensible than a stricter one, regardless of what the product needs
   - d) An inconclusive result should default to whichever outcome (ship or block) is more convenient for the team

<details markdown="1"><summary>Check</summary>

**b)** Both conditions, set in advance and respecting the noise floor, are what make a threshold enforceable rather than decorative. (a) is false: a post-hoc threshold can be bent to fit whatever result appeared. (c) is false: the right threshold reflects what the product actually needs, not a blanket preference for looseness. (d) is false: an inconclusive result calls for more evidence, not a default answer picked for convenience.

</details>

## Real-world reps

- [ ] For a model change you're evaluating or plan to evaluate, write down the regression threshold before running the eval, and check it against the current sample size's estimated noise floor from lesson 9.
- [ ] Draft a full go/no-go defense for a past or hypothetical result, explicitly citing the metric choice, the held-out set's honesty, any judge calibration checks, the harness's reproducibility logging, and the statistical case, one line each.
- [ ] Tomorrow: revisit this workspace's mission in `README.md` and confirm, in your own words, that you can now do what it describes: prove a model change helped, holding the data out honestly and defending the number against contamination.

## Going further

- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Paper: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
