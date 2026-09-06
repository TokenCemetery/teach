---
title: 3. Task-Specific Metrics
description: Exact match, token-level F1, and BLEU/ROUGE, and the failure mode each one has
type: lesson
---

# Lesson 3. Task-Specific Metrics

**Mission link:** Stage 2 opens the "build the eval" half of the mission: a task-specific metric turns a held-out set (stage 1) into an actual number, and each metric this lesson covers fits some tasks well and quietly lies about others.
**Primary source:** [Docs: Evaluate, Hugging Face](https://huggingface.co/docs/evaluate/index)
**Prerequisites:** [Lesson 2](0002-designing-contamination-resistance.md), [Data contamination](../GLOSSARY.md)

## Warm-up

1. ▢ What does embedding a canary string in a custom eval set actually protect against?

<details markdown="1"><summary>Check</summary>

It signals to crawlers assembling a training corpus that the marked content should be excluded, and it gives a way to detect a leak later if the string surfaces in a model's output or an accessible corpus. It's a request, not a guarantee: it depends on crawlers respecting the convention.

</details>

2. ▢ When is an n-gram overlap check against a known corpus usable, and when does it stop being an option?

<details markdown="1"><summary>Check</summary>

It's usable when the pretraining corpus is known and accessible. It stops being an option for a closed model with undisclosed training data, where the guided-instruction test remains the available tool.

</details>

## Know this

### Exact match: strict, and brittle to anything superficial

**Exact match** scores a prediction correct only if it matches a reference answer character for character (often after light normalization like lowercasing or stripping whitespace). It suits tasks with one clearly correct answer: multiple choice, span extraction, a math result. Its failure mode is exactly what its strictness implies: a correct answer phrased differently (`"Paris"` against a reference of `"Paris, France"`) scores as wrong, penalizing correctness rather than measuring it, unless the normalization applied is generous enough to absorb that variation without also absorbing genuinely wrong answers.

### Token-level F1: partial credit, at the cost of caring about order

**F1** (as used for extractive tasks like span-based question answering) treats a prediction and a reference as bags of tokens rather than requiring an exact string match, computing precision (what fraction of the prediction's tokens are correct) and recall (what fraction of the reference's tokens were produced), then their harmonic mean. Reference "the cat sat on the mat" (tokens: `the, cat, sat, on, the, mat`) against prediction "a cat sat on the mat" (tokens: `a, cat, sat, on, the, mat`) shares five tokens (`cat, sat, on, the, mat`) out of six in each: precision `5/6`, recall `5/6`, F1 `5/6 ≈ 0.83`. This is more forgiving than exact match, which would score this pair as flatly wrong. The failure mode is what that forgiveness costs: F1 over a bag of tokens is blind to order and to whether the overlapping words actually combine into a correct answer, so a prediction that scrambles the right words into the wrong claim can still score high.

### BLEU and ROUGE: n-gram overlap against a reference, built for translation and summarization

**BLEU** (originally for machine translation) and **ROUGE** (originally for summarization) both score a generated text by how much its n-grams (contiguous token sequences of length n) overlap with one or more reference texts, rather than requiring an exact match or scoring single tokens in isolation. Their failure mode shows up hardest on open-ended generation: a valid paraphrase that says the same thing in different words, "Critics praised the show" against a reference of "The show received positive reviews from critics", shares very few n-grams with the reference despite being an equally good answer, and scores low as a result. Using multiple reference texts per example softens this, but rarely enough references exist to cover every valid phrasing, which is a large part of why these metrics correlate only loosely with human judgment on open-ended text, and why stage 3's LLM-as-judge exists as an alternative for exactly that case.

### Choosing a metric means matching it to what "correct" means for the task

Exact match and F1 fit tasks where correctness is a small, well-defined set of answers: classification, extraction, arithmetic. BLEU and ROUGE fit tasks where surface overlap with a reference correlates, loosely, with quality, useful as a coarse, cheap first-pass filter rather than a final verdict. Neither family is suited to a task where correctness is behavioral rather than textual (does the generated code actually run and produce the right output), which is lesson 4's subject, or to open-ended generation where meaning matters more than wording, which is stage 3's.

## Practice

1. ▢ A model answers a geography question with "Paris" while the reference answer is "Paris, France". Exact match scores this wrong. Is that a correct scoring outcome? Why or why not?

<details markdown="1"><summary>Check</summary>

No, not really: the answer is correct, just phrased more tersely than the reference. This is exact match's brittleness to superficial variation. The fix is either normalizing both strings before comparing (which only helps if the normalization is designed to absorb this specific kind of variation) or choosing a more forgiving metric for a task where phrasing varies this much.

</details>

2. ▢ Reference: "a fast red fox jumps". Prediction: "a red fox jumps fast". Using bag-of-tokens F1 (ignoring word order), what is the precision, recall, and F1 score?

<details markdown="1"><summary>Hint</summary>

List each side's tokens as a set and count how many are shared, regardless of position.

</details>

<details markdown="1"><summary>Check</summary>

Both sides have the same 5 tokens (`a, fast, red, fox, jumps` versus `a, red, fox, jumps, fast`), just reordered, so all 5 are shared. Precision `5/5 = 1.0`, recall `5/5 = 1.0`, F1 `1.0`. This also demonstrates F1's blindness to order: a prediction with scrambled word order scores identically to one that preserves it, even though word order can change meaning in a way F1 cannot detect.

</details>

3. ▢ A summarization model produces "Critics praised the show" for a reference summary "The show received positive reviews from critics." Would ROUGE likely score this pair high or low, and is that outcome a fair reflection of the prediction's quality?

<details markdown="1"><summary>Check</summary>

Low, since the two sentences share very few contiguous n-grams despite saying essentially the same thing in different words. This is not a fair reflection of quality: the prediction is a valid paraphrase, but ROUGE measures surface n-gram overlap, not meaning, so a correct answer phrased differently from the reference is penalized the same way a wrong answer would be.

</details>

4. ▢ A team is evaluating a model on a multiple-choice benchmark with one correct letter per question. Which metric from this lesson fits best, and why?

<details markdown="1"><summary>Check</summary>

Exact match. The task has exactly one correct answer per question with no meaningful surface variation to absorb (the answer is a single letter), which is exactly the shape of task exact match is built for, without F1's or BLEU/ROUGE's forgiveness for partial or paraphrased overlap being needed at all.

</details>

5. ▢ Which claim is true of BLEU and ROUGE compared to exact match and F1?

   - a) They require a single, unambiguous correct answer, the same as exact match
   - b) They score overlap against reference text at the n-gram level, which correlates only loosely with quality on open-ended generation
   - c) They are immune to the paraphrase problem that affects exact match
   - d) They are best used as the final verdict for any generation task, replacing human or LLM judgment

<details markdown="1"><summary>Check</summary>

**b)** N-gram overlap is a loose proxy for quality, especially where valid answers can be phrased many different ways. (a) is false: they're built for tasks with open-ended text, not a single fixed answer. (c) is false: a valid paraphrase can score low on BLEU/ROUGE for the same underlying reason it can fail exact match, differing surface wording. (d) is false: their weak correlation with human judgment on open-ended text is exactly why stage 3 introduces LLM-as-judge as an alternative.

</details>

## Real-world reps

- [ ] Pick a task you evaluate (or plan to evaluate) and decide which of exact match, F1, or BLEU/ROUGE fits its notion of "correct," writing down why.
- [ ] For an eval that currently uses BLEU or ROUGE, find one example where a clearly correct, differently-worded answer would score poorly, and note it.
- [ ] Tomorrow: read one paragraph of the Hugging Face Evaluate docs on a metric you haven't used before and note its stated failure mode.

## Going further

- [Docs: Evaluate, Hugging Face](https://huggingface.co/docs/evaluate/index)
- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
