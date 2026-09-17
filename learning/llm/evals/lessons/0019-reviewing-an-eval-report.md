---
title: 19. Reviewing an Eval Report
description: Name specifically what would make an eval report's number untrustworthy (contamination, an uncalibrated judge, a single run with no variance estimate, a leaderboard rank standing in for a task-specific call), rather than saying it feels thin
type: lesson
---

# Lesson 19. Reviewing an Eval Report

**Mission link:** Every skill in this arc builds toward one thing: a number you can personally defend. This lesson is the complementary skill: reviewing someone else's number and saying, specifically and from the material, what would make it untrustworthy instead of just feeling incomplete. An eval suite, once built, is shared infrastructure: other teams gate ships on its number, and changing a judge, threshold, or metric silently invalidates decisions already made. Reviewing and maintaining one honestly is a senior judgment call.
**Primary source:** [Paper: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
**Prerequisites:** [Lesson 6](0006-judge-bias-and-human-agreement.md), [Lesson 9](0009-statistical-significance-vs-noise.md), [Lesson 10](0010-defending-the-go-no-go-call.md), [Lesson 18](0018-public-benchmarks.md)

## Warm-up

1. ▢ What does it mean for a judge to be calibrated, and what specific failure does lesson 5 describe as score compression?

<details markdown="1"><summary>Check</summary>

A calibrated judge's scores track real quality consistently across examples. Score compression toward the ceiling is a failure where the judge rates nearly everything highly regardless of real quality differences, erasing the distinctions an eval exists to catch.

</details>

2. ▢ What is the honest conclusion when an eval score difference falls inside the estimated noise, and what are two ways to get a clearer answer?

<details markdown="1"><summary>Check</summary>

The honest conclusion is not "no difference" but "not yet enough evidence to say." Two ways to clarify: run the eval on more examples (shrinking the standard error), or run a proper paired significance test on the specific examples where variants disagree.

</details>

3. ▢ A leaderboard rank aggregates preferences across which three things that might not match your actual task?

<details markdown="1"><summary>Check</summary>

Users, tasks, and use cases that are not yours. A leaderboard position can be a reasonable first filter for which models to evaluate further, but it fails the OEC test lesson 15 established because it isn't causally tied to your specific decision.

</details>

## Know this

### The review checklist: what makes a number untrustworthy

When someone presents an eval report or harness design, work through these questions in order. Where the report has no answer, you have found the gap that makes the number untrustworthy, specifically and named.

**Stages 1-2: Is the held-out set actually held out?**

Ask: What evidence is there that the eval data is held out? Has the team checked for contamination using the techniques lesson 2 taught (canary strings, guessing-the-rest-of-the-instance tests, or both)? If the report says "the data is from a public benchmark," it should also report on whether that benchmark's saturation (ceiling performance with no real improvement) or contamination is already documented in the wild. If neither contamination check nor saturation evidence is reported, the number could be inflated by the model simply having seen the questions before in training or by memorizing a heavily-tuned benchmark rather than learning the underlying skill.

**Stage 2: Is the metric actually matched to the task?**

Ask: Why is this metric being used for this task? If the report says "accuracy," is that the right metric (lesson 3 covers what each metric's failure modes are), or would F1, BLEU, code-execution, or something else actually measure what matters? If a custom metric was built, what is the evidence it correlates with the real outcome (e.g., human preference, task success)? A report that doesn't justify its metric choice has made a guess dressed up as a decision.

**Stages 3 and 6: If an LLM judge is used, is it actually trustworthy?**

Ask three things:
- **Design:** What is the judge prompt, and what did the team do to calibrate it before running it at scale? Does the prompt give the judge a reference answer when one is available? Lesson 5 teaches calibration; if the report doesn't mention it, the judge may be suffering from score compression or other uncalibrated failure modes.
- **Bias checks:** Was the judge checked for position bias (does the same pairwise comparison flip if you swap the order)? Was verbosity bias checked (does the judge prefer length independent of correctness)? Lesson 6 covers these biases; if the report doesn't mention checking for them, they could be silently inflating or deflating numbers.
- **Human agreement:** What is the judge's agreement rate with human raters on a sample, and what is the human-versus-human agreement on the same sample? A judge at 82% agreement sounds weak until you learn human raters agree at 80% with each other, in which case the judge is performing about as well as another human would. A report that claims an LLM judge without measuring it against human judgment is claiming a shortcut without evidence it works.

**Stages 5 and 9-10: Is the number backed by variance, or is it one run?**

Ask: How many times was the eval run, and what was the spread? If it's one number from one run at a nonzero temperature, the noise in that number (lesson 9's standard error) is invisible. Did the team measure a standard error or run a significance test to confirm the observed gap is clearly larger than the noise? If an improvement is reported without a significance estimate, you can't tell whether it's a real win or a statistical coincidence. Also check whether the threshold was set before the eval ran or after, and whether it respects the noise floor: lesson 10 teaches that a threshold tighter than the eval can actually resolve is a coin flip dressed up as a decision.

**Stage 11: Does it account for cost and latency?**

Ask: Is the reported improvement weighed against what it costs to serve? Per-request cost and per-token cost for models with a different input/output split: are these mentioned, and is the quality gain actually worth that multiplier? If latency was measured, was it tail latency (p95/p99) or just an average? Lesson 17 teaches why an unchanged average can hide a meaningfully worse tail. If the report says "quality improved" without cost or latency, half the go/no-go call is missing.

**Stage 12: Is it leaning on a leaderboard instead of a task-specific number?**

Ask: Does the report say "this model ranks X on MMLU" or "this model scores X on our task-specific eval"? If it's leaning on a public benchmark or leaderboard position as evidence, lesson 18 establishes that a leaderboard rank fails the test a real OEC needs: it isn't causally tied to your specific decision, and it carries documented gaming vectors (selective disclosure, style bias). A task-specific go/no-go call doesn't replace a leaderboard check, but a leaderboard position doesn't replace a task-specific number either.

### The specific skill: settling whether an LLM judge can stand in for a task-specific go/no-go call

This workspace has presented two credible accounts of LLM judges. Lesson 5 and 6 taught how to build and calibrate one, finding them useful for open-ended tasks when built carefully. But a legitimate question hangs over the whole idea: is an LLM judge ever trustworthy enough to stand in for a task-specific eval, or is it fundamentally limited to pre-screening or correlation checking?

The Zheng et al. 2023 paper "Judging LLM-as-a-Judge" establishes that LLM judges can measure human preferences well on open-ended tasks (on Chatbot Arena, a judge's pairwise preference matches human preferences around 80% of the time), and that this is good enough to use in practice, but *only* when you check for and correct known biases (position, verbosity, self-enhancement) and only when you measure the judge against human agreement rather than an imagined perfect standard.

Here's the move a reviewer needs to make when this question comes up in a real conversation. Two people, both citing plausible sources, disagree:

**Engineer A says:** "Zheng et al. showed judges work; we can use an LLM judge for our go/no-go call."

**Engineer B says:** "Yeah, but Zheng also showed judges are biased; a task-specific metric would be more honest."

Both are citing the same paper. The difference is in what they're extracting from it.

The right move is not to pick a side by vibes, and not to split the difference vaguely ("sometimes judges work, use your judgment"). The right move is to go back to the paper and check whether the conditions under which Zheng's findings hold match your actual situation:

**Zheng's conditions:** The judges measured best on pairwise preference comparisons for open-ended tasks (writing, reasoning, creativity). The comparison was pairwise, not pointwise (not grading on a 1-to-10 scale). Human raters on the same task were themselves at around 80% agreement with each other. The judge was checked for multiple biases and corrections were applied. The verdict was used as a filter or a signal, not as a final, unreviewed go/no-go call.

**Now, your situation:** Is your task open-ended, or does it have a crisp right answer? Are you grading pairwise or on a numeric scale? Have you measured human agreement on this task, and if so, what is it? Have you checked the judge for position, verbosity, and self-enhancement bias, and do you have a plan to correct for them if found? Is this judge's output being reviewed by a human before it drives a decision, or is it standing alone?

If your situation matches Zheng's conditions closely, the finding that "judges work when built carefully" applies more directly. If your task is crisp, or if you haven't measured human agreement on it, or if the judge output drives the call unreviewed, the weight of the evidence shifts. The skill is not "remember what Zheng says" but "check whether the conditions that made that finding true apply to what you're building."

### What good judgment sounds like when reviewing an eval report

> "The report claims a 5-point improvement on their task-specific eval with an LLM judge, but it doesn't say how many runs were done or what the standard error is on a 100-example set at a 70% baseline; that's probably 4 to 5 points of noise, which means this gap might be real or might not be. They also didn't mention checking the judge for position or verbosity bias, and they don't cite human agreement on the same samples. Before we ship based on this number, we need the standard error computed, a bias check on the judge, and measurement against human agreement on a sample of the task. Or, if the task is crisp enough, they should have used a task-specific metric instead of a judge in the first place."

Nothing in that is a fact you looked up. It is the shape of skepticism this workspace was for.

### Maintaining an eval suite others depend on

Once you have built an eval, and other teams gate ships on its number, the eval becomes shared infrastructure. Changing the judge, metric, threshold, or dataset shape silently invalidates decisions already made on the old version. A team that shipped on "eval version 1.0 showed improvement of 3 points" has made a decision tied to that specific eval. If you change the judge and re-run eval version 2.0, a 2-point improvement is not comparable: the team relied on version 1.0's number, not 2.0's.

When you need to change an eval suite:

**Option 1: Run old and new side by side.** Before you cut over, measure a reasonable sample of recent model changes against both the old judge/metric/version and the new one. This gives other teams a conversion factor and shows them the impact. A report saying "switching judges changes the score by about 2 points on average across these models" is honest and actionable; switching silently is a breaking change.

**Option 2: Version the eval formally.** If you're releasing eval 2.0 with a different judge, metric, or threshold, version it clearly. Other teams can keep running 1.0 until they're ready to migrate. Document what changed and why. This is how stable tools do it.

**Option 3: Don't change what others depend on without communication.** If a change is necessary (the old judge is provably broken, a metric is no longer appropriate), announce it. Give teams time to re-evaluate their last few ship decisions under both versions. A surprise change in what an eval means is how you lose trust in evals entirely.

## Practice

1. ▢ A team reports a model improved 6 points on their eval, with an LLM judge scoring pairwise comparisons. The report doesn't mention how many examples are in the eval or whether the judge was checked against human agreement. What should you ask?

<details markdown="1"><summary>Check</summary>

On what eval set size? The standard error on a 100-example set at a typical baseline is 4 to 5 points; a 6-point gap might be real or might be noise. Have you measured the judge's agreement with human raters on a sample of your task? Without knowing human-versus-human agreement, you can't tell whether an 80% judge-human agreement is good or mediocre. Also: was the judge checked for position bias (order swapped) and verbosity bias? Without those checks, the improvement could be an artifact of how the judge was prompted.

</details>

2. ▢ A team says "we use an LLM judge because Zheng et al. showed judges work." But they haven't measured human agreement on their own task, and they're using pointwise (1-to-10 scale) scoring, not pairwise. Does Zheng's finding apply directly to their situation?

<details markdown="1"><summary>Check</summary>

Not directly. Zheng's findings held for pairwise preference comparisons on open-ended tasks where human raters themselves were at 80% agreement. Pointwise scoring is a different mode (more prone to scale interpretation issues), and without measuring human agreement on this specific task, you don't know what baseline to expect from the judge. The team should either measure human agreement on their task and compare the judge against it, or switch to a task-specific metric if the task allows one.

</details>

3. ▢ Your eval suite has been running for six months, and other teams gate ships on it. You want to switch to a different, better-calibrated judge because the current one has score compression. What should you do before making the change?

<details markdown="1"><summary>Check</summary>

Run old and new judges side by side on a sample of recent model changes. Show other teams what the judge swap does to the scores they've been relying on. If it's a 2-point shift on average, they can recalibrate; if it's a 10-point shift, they need to re-evaluate recent decisions. Announce the change clearly, and consider versioning the eval (eval 1.0 with the old judge, eval 2.0 with the new one) so other teams can migrate on their own schedule instead of being surprised by a breaking change.

</details>

4. ▢ An engineer reviewing an eval report says, "The report claims a 4-point improvement with no significance test reported. The eval set is 50 examples, and the baseline is 68%. Should we trust this number?" What's your analysis?

<details markdown="1"><summary>Check</summary>

Not without more information. At N=50 and p=0.68, the standard error is roughly `sqrt(0.68 × 0.32 / 50) ≈ 0.066`, or about 6.6 percentage points. A 4-point gap is well within the noise; it's not clearly larger than what sampling alone could produce. The team should either run more examples (shrinking the standard error) or run a paired significance test on the specific examples where they disagree, not just report the raw difference and hope it looks convincing.

</details>

5. ▢ Which situation would make you most skeptical of an eval report claiming an improvement?

    - a) The eval uses a task-specific metric, ran 500 examples, and reports a 3-point improvement with a paired significance test showing p < 0.05
    - b) The eval uses an LLM judge, ran 100 examples, reports a 4-point improvement, but doesn't mention whether the judge was checked for position bias or whether human agreement was measured
    - c) The eval reports a leaderboard ranking on MMLU as the main evidence of improvement
    - d) The eval cost and latency alongside quality in the go/no-go call

<details markdown="1"><summary>Check</summary>

**b)** and **c)** are red flags. (b) is incomplete: without bias checks or human-agreement measurement, you can't tell if the judge is trustworthy. (c) is a failure to measure what matters: a leaderboard rank isn't a task-specific go/no-go signal. (a) hits all the right notes: a task-specific metric, large sample, significance test. (d) is good practice, not a reason to be skeptical. The most skeptical flag is a report that doesn't answer the questions this lesson teaches to ask.

</details>

## Real-world reps

- [ ] Find an eval report from your own work or a colleague's. Run the review checklist from this lesson against it. Write down which checklist items the report addresses clearly and which it leaves silent. Share the list with the report's author.
- [ ] On the question "can an LLM judge stand in for a task-specific eval," reread the Zheng et al. paper yourself and identify the specific conditions under which their findings held. Jot down: what task characteristics, sample sizes, and measurement practices did they use? How would you test whether those conditions apply to a new situation?
- [ ] Tomorrow: Propose a change to an eval suite you maintain or know. Write down how you would communicate that change to other teams who gate ships on it, and whether you would run old and new side by side, version formally, or both.

## Going further

- [Paper: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
- [Lesson 6: Judge Bias and Human Agreement](0006-judge-bias-and-human-agreement.md), for the biases to check
- [Lesson 10: Defending the Go/No-Go Call](0010-defending-the-go-no-go-call.md), for what a complete defense must cite
- [Lesson 18: Public Benchmarks](0018-public-benchmarks.md), for why a leaderboard rank isn't a substitute for a task-specific call
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
