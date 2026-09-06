---
title: 5. Judge-Prompt Design and Calibration
description: How to write a judge prompt that grades consistently, and what it means for a judge to be calibrated before trusting it
type: lesson
---

# Lesson 5. Judge-Prompt Design and Calibration

**Mission link:** Stage 3 covers the tool stages 1 and 2 built toward for open-ended text: neither a fixed-answer metric nor n-gram overlap tracks quality well here, so an LLM judge fills the gap, but only once its prompt and its calibration are checked, not assumed.
**Primary source:** [Paper: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
**Prerequisites:** [Lesson 4](0004-code-execution-metrics.md), [Data contamination](../GLOSSARY.md)

## Warm-up

1. ▢ Why does functional correctness avoid the failure mode that affects exact match, F1, and BLEU/ROUGE on code?

<details markdown="1"><summary>Check</summary>

It executes the generated code against test cases and checks its actual behavior, rather than comparing its text to a reference solution. Code has an especially large number of textually different ways to be correct, so a text-comparison metric would penalize a correct-but-differently-written solution.

</details>

2. ▢ What decision principle from lesson 4 determines which metric family fits a given task?

<details markdown="1"><summary>Check</summary>

Match the metric to what "correct" means for the task: execute the output when correctness is behavioral and checkable, use exact match or F1 when correctness is a small fixed set of answers, and use BLEU/ROUGE as a coarse filter for open-ended text where surface overlap only loosely tracks quality.

</details>

## Know this

### Why an LLM judge exists at all

Open-ended generation, a chat response, a long-form answer, a piece of creative or explanatory writing, is exactly where lesson 3's BLEU and ROUGE correlate weakly with quality and lesson 4's functional correctness has nothing to execute. An **LLM-as-judge** asks a capable model to grade or compare outputs directly, and it correlates with human preference far better than n-gram overlap does on this kind of text. That advantage is not automatic, though: a judge's prompt and its measured agreement with human raters both need to be checked before its scores are trusted, which is this lesson's subject.

### Designing a judge prompt

A few concrete choices separate a judge prompt that grades consistently from one that doesn't:

- **Explicit criteria, not a vague ask.** "Which response is better?" leaves the judge to invent its own rubric, differently on every call. Naming the dimensions that matter for the task (correctness, completeness, tone, whichever apply) gives every judgment the same yardstick.
- **A reference answer, when one exists.** Reference-guided grading gives the judge something to compare against rather than judging in a vacuum, which matters especially for tasks like math or multi-step reasoning, where a wrong answer can still read as fluent and convincing without something correct to check it against.
- **Reasoning before the score.** Asking the judge to explain its reasoning first, then give a rating, produces more consistent scores than asking for a bare number, since it forces the judgment to be justified rather than emitted directly, the same way asking a person to explain a rating tends to make the rating itself more considered.
- **A structured, parseable output.** A forced scale (say, 1 to 10) or a forced pairwise choice (A, B, or tie) is easier to aggregate and audit than free-form prose grading, and it's what lets many judged examples turn into one summary number.

### Calibration: does the judge's score mean the same thing across examples

A judge is **calibrated** when its scores track actual quality consistently: an 8 out of 10 on one example should reflect roughly the same quality level as an 8 out of 10 on a different example, and the judge's relative rankings should agree with what human raters would say. A judge can fail this in a specific, common way: **score compression toward the ceiling**, where the judge rates nearly everything an 8 or 9 regardless of real quality differences, which erases the very distinctions an eval exists to catch. A judge whose scores don't spread out the way genuine quality does is not measuring quality; it's measuring its own leniency.

Calibration is not something to assume; it's something to check, the same way lesson 1 insisted a held-out set's honesty be checked rather than assumed. The check: run the judge against a small set of examples a human has already rated, and measure agreement, whether by simple agreement rate or a correlation statistic, before trusting the judge on the larger, unlabeled set the eval actually needs it for.

## Practice

1. ▢ Why does giving a judge model a reference answer, when one is available, tend to improve its grading accuracy compared to judging with no reference at all?

<details markdown="1"><summary>Check</summary>

Without a reference, the judge has nothing to check a response against beyond its own sense of plausibility, and a fluent but wrong answer, especially on math or multi-step reasoning, can read as convincing without something correct to compare it to. A reference answer gives the judge an anchor, catching errors that would otherwise slip past a judgment made in a vacuum.

</details>

2. ▢ Why does asking a judge to explain its reasoning before giving a numeric score tend to produce more consistent grading than asking for a bare score alone?

<details markdown="1"><summary>Check</summary>

Producing reasoning first forces the judgment to be justified rather than emitted directly from a snap impression, which tends to make the resulting score more considered and less arbitrary, the same effect asking a person to explain a rating has on the rating itself.

</details>

3. ▢ A team's judge model scores nearly every response 8 or 9 out of 10, including several a human rater independently called mediocre. What calibration failure does this describe, and why does it matter for a later go/no-go decision?

<details markdown="1"><summary>Hint</summary>

Think about what a score is supposed to do: distinguish quality levels from each other.

</details>

<details markdown="1"><summary>Check</summary>

This is score compression toward the ceiling: the judge's scores no longer spread out the way real quality differences do, so its ratings stop distinguishing a genuinely good response from a mediocre one. This matters for a go/no-go call because a compressed score range can make a change look like an improvement, or make a regression invisible, when the judge simply isn't discriminating between quality levels anymore.

</details>

4. ▢ What is a concrete way to check whether a judge is calibrated before trusting it on a full, unlabeled eval set?

<details markdown="1"><summary>Check</summary>

Run the judge against a smaller set of examples a human has already rated, and measure how well the judge's scores or rankings agree with the human ratings, before relying on the judge for the larger set where no human ratings exist to check against.

</details>

5. ▢ Which claim is true of a well-designed judge prompt?

   - a) It should ask a single vague question ("which is better?") to avoid biasing the judge with specific criteria
   - b) It should name explicit grading criteria, include a reference answer when available, and ask for reasoning before a score
   - c) A judge never needs a reference answer, since it can always tell a correct answer from an incorrect one unaided
   - d) Calibration is guaranteed as long as the judge model is capable enough

<details markdown="1"><summary>Check</summary>

**b)** Each of those choices is what this lesson showed improves consistency and accuracy. (a) is false: a vague ask lets the judge invent its own rubric differently each time. (c) is false: a fluent but wrong answer, especially on reasoning tasks, can fool a judge with nothing to check it against. (d) is false: calibration has to be measured against human ratings, regardless of how capable the underlying model is.

</details>

## Real-world reps

- [ ] Find or write a judge prompt for a task you evaluate, and check it against this lesson's four design points: explicit criteria, a reference answer where available, reasoning before scoring, and a structured output.
- [ ] Hand-rate a small sample (10 to 20 examples) yourself, run the same examples through your judge prompt, and measure how often they agree.
- [ ] Tomorrow: look at your judge's score distribution across a batch of graded examples and check whether it's spread out the way you'd expect real quality differences to be, or compressed toward one end.

## Going further

- [Paper: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
