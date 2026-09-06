---
title: 6. Judge Bias and Human Agreement
description: Position bias and verbosity bias in LLM-as-judge, and how to measure a judge's agreement with human raters
type: lesson
---

# Lesson 6. Judge Bias and Human Agreement

**Mission link:** This is stage 3's capstone: a judge prompt can be well designed (lesson 5) and still mislead in specific, known ways, and defending a judge's verdict means checking for those biases and measuring agreement against human judgment rather than assuming the judge is right.
**Primary source:** [Paper: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
**Prerequisites:** [Lesson 5](0005-judge-prompt-design-and-calibration.md), [Data contamination](../GLOSSARY.md)

## Warm-up

1. ▢ What does it mean for a judge to be calibrated, and what specific failure did lesson 5 describe as score compression?

<details markdown="1"><summary>Check</summary>

A calibrated judge's scores track real quality consistently across examples. Score compression toward the ceiling is a failure where the judge rates nearly everything highly regardless of real quality differences, erasing the distinctions an eval exists to catch.

</details>

2. ▢ Why does giving a judge a reference answer, when available, tend to improve its grading accuracy?

<details markdown="1"><summary>Check</summary>

Without a reference, a fluent but wrong answer can read as convincing, especially on math or reasoning tasks. A reference gives the judge something correct to check the response against, rather than judging in a vacuum.

</details>

## Know this

### Position bias: favoring where a response sits, not what it says

When a judge compares two responses side by side (pairwise grading), it can systematically favor whichever one appears first, or in some models, second, in the prompt, independent of actual quality. This is **position bias**, and it means a single pairwise call can't be trusted at face value: the verdict might reflect where a response was placed rather than what it said. The check is direct: run the same comparison twice, with the two responses' order swapped, and see whether the verdict is consistent. If the judge picks whichever response comes first regardless of which one that is, the verdict is unreliable and should be treated as a tie or discarded rather than trusted.

### Verbosity bias: favoring length over correctness

A separate, equally common failure is **verbosity bias**: a judge tends to prefer a longer response even when the extra length adds nothing, over a shorter response that is equally, or more, correct and complete. This rewards padding and penalizes concision, which is exactly backwards for most real tasks. Mitigating it means either instructing the judge explicitly not to reward length on its own, designing criteria that name completeness and correctness rather than length as what to grade, or checking, after the fact, whether the judge's preferences correlate suspiciously well with response length across many comparisons.

### Measuring agreement with human judgment

Lesson 5's calibration check compared a judge's scores to human ratings on a small sample. The same idea, applied to pairwise comparisons, is measuring **agreement**: the fraction of comparisons where the judge's choice matches what a human rater (or a majority of several) would have chosen. The number to compare this against is not a perfect 100% ceiling, since human raters don't agree with each other 100% of the time either. The right comparison is judge-versus-human agreement against human-versus-human agreement: a judge whose agreement rate with humans is close to how often humans agree with each other is doing about as well as another human rater would, which is a meaningful bar to clear. A judge measured only against an assumed perfect standard is being held to a standard nothing meets.

## Practice

1. ▢ A judge is asked to compare response A against response B and picks A. The team then reruns the same comparison with the order swapped (B first, A second), and the judge now picks whichever response was placed first again. What does this reveal, and what should the team do with this comparison's verdict?

<details markdown="1"><summary>Check</summary>

It reveals position bias: the judge's choice tracks which response came first in the prompt, not which one was actually better. The team should not trust the original verdict as evidence of quality; a comparison that flips with order should be treated as a tie or discarded rather than counted as a real preference.

</details>

2. ▢ Why would a judge prefer a longer response even when a shorter response is equally correct and complete, and name one way to mitigate this?

<details markdown="1"><summary>Check</summary>

Verbosity bias: length itself correlates with the judge's preference more than actual quality does, rewarding padding over concision. Mitigations include instructing the judge explicitly not to favor length, writing grading criteria that name correctness and completeness rather than length, or checking after the fact whether the judge's preferences correlate suspiciously well with response length across many comparisons.

</details>

3. ▢ A team measures their judge's agreement with human raters at 82%. Is that good enough to trust the judge? What additional number do they need before answering that?

<details markdown="1"><summary>Hint</summary>

Think about what the judge's agreement rate should be compared against, besides a perfect score.

</details>

<details markdown="1"><summary>Check</summary>

82% alone doesn't say enough. They need the human-versus-human agreement rate on the same comparisons, since human raters don't agree with each other 100% of the time either. If human raters agree with each other around 80 to 85% of the time, an 82% judge-human agreement is doing about as well as another human rater would, a meaningful bar to clear. Measured only against a perfect 100% ceiling, the same 82% would look like a shortfall it isn't.

</details>

4. ▢ A team compares a 300-word response (A) against an 80-word response (B), both correct and complete, in a single pairwise judge call, and the judge picks A. What two things from this lesson should they check before trusting that verdict?

<details markdown="1"><summary>Check</summary>

Position bias, by rerunning the comparison with the responses' order swapped and checking whether the verdict holds. Verbosity bias, by considering whether the judge favored A simply for being longer rather than for being more correct or complete, especially since B is described as equally correct and complete despite being much shorter.

</details>

5. ▢ Which claim is true of checking an LLM judge's pairwise verdicts for position bias?

   - a) Position bias only affects judges grading code, not prose
   - b) Rerunning a comparison with response order swapped and checking for a consistent verdict is a direct way to detect it
   - c) A judge that explains its reasoning before choosing is automatically immune to position bias
   - d) Position bias is eliminated by using a numeric 1-to-10 scale instead of a pairwise choice

<details markdown="1"><summary>Check</summary>

**b)** Swapping the order and checking for a consistent choice is exactly the direct test this lesson describes. (a) is false: nothing limits position bias to code grading. (c) is false: reasoning before a score helps calibration (lesson 5) but doesn't by itself rule out the verdict tracking position. (d) is false: position bias is specifically a pairwise-comparison phenomenon; switching to a different output format changes the failure mode being tested, not this one directly, and a numeric scale has its own calibration concerns from lesson 5.

</details>

## Real-world reps

- [ ] For a pairwise judge setup you use or plan to use, rerun a handful of comparisons with response order swapped and check how often the verdict flips.
- [ ] Take a set of judged comparisons and check whether the judge's preferred response is longer than the alternative more often than chance would predict.
- [ ] Tomorrow: if you have human-rated comparisons available, compute your judge's agreement rate with those humans, and separately estimate how often the humans agreed with each other, before deciding whether the judge clears that bar.

## Going further

- [Paper: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
