---
title: 4. Code-Execution Metrics and Choosing a Metric
description: Functional correctness, the pass@k estimator, and a decision principle for picking a metric per task
type: lesson
---

# Lesson 4. Code-Execution Metrics and Choosing a Metric

**Mission link:** This is stage 2's capstone: code is the one task type where correctness can be checked by running it rather than comparing it to text, and picking the right metric family, across this lesson and lesson 3, is what makes an eval number mean what it claims to mean.
**Primary source:** [Paper: "Evaluating Large Language Models Trained on Code" (Codex), Chen et al., 2021](https://arxiv.org/abs/2107.03374)
**Prerequisites:** [Lesson 3](0003-task-specific-metrics.md), [Data contamination](../GLOSSARY.md)

## Warm-up

1. ▢ Reference: "a fast red fox jumps". Prediction: "a red fox jumps fast". Why does bag-of-tokens F1 score this pair as a perfect match, and what does that reveal about F1's blind spot?

<details markdown="1"><summary>Check</summary>

Both share the same five tokens, just reordered, so F1 scores it 1.0. This reveals F1 is blind to word order: a prediction that scrambles the right words into a different, possibly wrong, claim can score identically to one that preserves the correct order and meaning.

</details>

2. ▢ Why would ROUGE likely score "Critics praised the show" low against a reference of "The show received positive reviews from critics," even though both say the same thing?

<details markdown="1"><summary>Check</summary>

The two sentences share very few contiguous n-grams despite matching in meaning, and ROUGE measures n-gram overlap, not meaning. A valid paraphrase is penalized the same way a wrong answer would be.

</details>

## Know this

### Functional correctness: execute the code instead of comparing it to text

Code has an enormous number of textually different ways to be correct: two solutions to the same problem can differ in variable names, structure, and approach while both being exactly right. Applying exact match, F1, or BLEU/ROUGE (lesson 3) to generated code would penalize a correct-but-differently-written solution exactly the way lesson 3 showed those metrics penalizing a valid paraphrase, only worse, since code has far more equivalent forms than prose usually does. **Functional correctness** sidesteps this entirely: run the generated code against a held-out suite of test cases and check whether it actually produces the right behavior. Correctness becomes a fact about what the code does, not about how closely its text resembles a reference solution.

### pass@k: correctness under sampling

An LLM's code generation is stochastic: asking the same question twice can produce a working solution once and a broken one another time. **pass@k** asks a sharper question than "did the one sample work": out of *k* sampled solutions to a problem, what is the probability that at least one of them passes all tests? Naively, this could be estimated by generating exactly *k* samples per problem and checking whether any pass, but that estimate is noisy, especially for small *k*, since which particular *k* samples got drawn matters a lot.

The Codex paper's fix: generate a larger number *n* of samples per problem, count how many, *c*, are correct, and compute the probability analytically that at least one of a hypothetical *k*-sample draw from those *n* would be correct, without needing to actually draw fewer:

```text
pass@k = 1 − C(n−c, k) / C(n, k)
```

`C(n−c, k) / C(n, k)` is the probability that a random draw of *k* solutions, without replacement, from the *n* generated, misses all *c* correct ones; subtracting that from 1 gives the probability at least one correct solution is included. This uses every generated sample to compute pass@k for any value of *k* up to *n*, rather than re-sampling and re-running the model for each *k* separately, which is both cheaper and lower-variance.

### Choosing a metric per task, tying stage 2 together

The choice runs in order of what "correct" actually means for the task. When correctness is behavioral and checkable by running something, execute it: functional correctness and pass@k, this lesson's subject. When correctness is one of a small, well-defined set of answers, exact match or F1 fit (lesson 3). When correctness is open-ended text where surface overlap with a reference only loosely tracks quality, BLEU or ROUGE (lesson 3) serve as a coarse, cheap first-pass filter, not a final verdict, since neither can be checked structurally or executed. Where a task is open-ended and nothing here can check it, the mission's next stage, LLM-as-judge, is what's left.

## Practice

1. ▢ Why would using exact match or BLEU to score generated code penalize a correct solution more often than it would for prose?

<details markdown="1"><summary>Check</summary>

Code has an especially large number of textually different ways to be correct (different variable names, structure, or approach solving the same problem), so a correct solution written differently from a reference is even more likely to be penalized by a text-comparison metric than a correct prose paraphrase would be, since the space of valid alternative phrasings is larger.

</details>

2. ▢ A model generates 10 samples for a coding problem (n = 10), 3 of which pass all tests (c = 3). Compute pass@1 and pass@5 using the formula from this lesson.

<details markdown="1"><summary>Hint</summary>

`C(n−c, k)` and `C(n, k)` are combinations: `C(a, b) = a! / (b! × (a−b)!)`. For pass@1, this should reduce to something familiar.

</details>

<details markdown="1"><summary>Check</summary>

pass@1: `1 − C(7,1)/C(10,1) = 1 − 7/10 = 0.3`, the same as simply `c/n`, as expected when k = 1. pass@5: `C(7,5) = 21`, `C(10,5) = 252`, so `1 − 21/252 ≈ 1 − 0.083 = 0.917`. pass@5 is much higher than pass@1, since drawing 5 samples gives far more chances to include at least one of the 3 correct ones.

</details>

3. ▢ Why does the Codex paper's estimator generate a large `n` and compute pass@k analytically over combinations, rather than just generating exactly `k` samples per problem and checking whether any pass?

<details markdown="1"><summary>Check</summary>

Generating exactly k samples and checking them directly is a single noisy draw, especially when k is small: which particular k samples happen to get generated varies a lot between runs. Generating a larger n once and computing the combinatorial estimator reuses all n samples to produce a lower-variance, unbiased estimate of pass@k for any k up to n, without needing to re-sample or re-run the model separately for each k.

</details>

4. ▢ Match each task to the metric family from lessons 3 and 4 that fits it best: (a) a multiple-choice quiz with one correct letter per question, (b) generating a Python function that must pass a test suite, (c) generating a short summary of a news article.

<details markdown="1"><summary>Check</summary>

(a) Exact match: one clearly correct answer, no meaningful surface variation to absorb. (b) Functional correctness / pass@k: correctness is behavioral and directly checkable by running the code. (c) BLEU or ROUGE, as a coarse first-pass filter, since summary quality is open-ended text where surface overlap only loosely tracks correctness; a fuller judgment would need something closer to human or LLM-as-judge evaluation.

</details>

5. ▢ Which claim is true of functional correctness compared to text-comparison metrics for code?

   - a) It requires generated code to match a reference solution's exact text
   - b) It checks whether the code's actual behavior, run against test cases, is correct, regardless of how it's written
   - c) It cannot be combined with sampling multiple completions per problem
   - d) It is a variant of BLEU adapted for programming languages

<details markdown="1"><summary>Check</summary>

**b)** That is the entire point: behavior, not text, determines correctness. (a) is false: that describes exact match, which functional correctness specifically avoids. (c) is false: pass@k is exactly functional correctness combined with sampling. (d) is false: functional correctness executes code rather than comparing n-grams at all.

</details>

## Real-world reps

- [ ] For a code-generation task you evaluate or plan to, find or write a small test suite that checks behavior rather than comparing generated code to a single reference solution's text.
- [ ] If you have access to a code model, generate several samples for one problem, and compute pass@1 and pass@3 by hand from how many pass, using this lesson's formula.
- [ ] Tomorrow: for three tasks you care about, write down which metric family (exact match/F1, BLEU/ROUGE, or functional correctness) fits each one's notion of "correct," and why.

## Going further

- [Paper: "Evaluating Large Language Models Trained on Code" (Codex), Chen et al., 2021](https://arxiv.org/abs/2107.03374)
- [Docs: Evaluate, Hugging Face](https://huggingface.co/docs/evaluate/index)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
