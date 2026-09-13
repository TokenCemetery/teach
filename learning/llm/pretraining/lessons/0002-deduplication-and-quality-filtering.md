---
title: 2. Deduplication and Quality Filtering
description: Why near-duplicate text and low-quality documents get removed before training, and what it costs to skip that step
type: lesson
---

# Lesson 2. Deduplication and Quality Filtering

**Mission link:** "Build a deduplicated, quality-filtered pretraining corpus from raw sources, and say what each filtering step removes and why" is the first bullet under Success looks like. Lesson 1 covered sourcing and mixing; this lesson covers the deduplication and filtering half.
**Primary source:** [Paper: "Deduplicating Training Data Makes Language Models Better", Lee et al., 2021](https://arxiv.org/abs/2107.06499)
**Prerequisites:** [Lesson 1](0001-sourcing-and-mixing-a-pretraining-corpus.md)

## Warm-up

1. ▢ What is the difference between a sourcing decision and a mixing decision for a pretraining corpus?

<details markdown="1"><summary>Check</summary>

Sourcing decides which sources are included at all. Mixing decides how much of the final token budget each included source gets, independent of which sources were chosen.

</details>

2. ▢ Per The Pile paper, why is "how big is the corpus" the wrong first question to ask about a pretraining run?

<details markdown="1"><summary>Check</summary>

Because GPT-2 and GPT-3, trained on enormous amounts of web text, still struggled on components like academic writing that a general web crawl underrepresents. What sources are included, not the total byte count, is what determines which domains a model actually learns.

</details>

## Know this

### Duplicates are not just wasted disk space

A corpus assembled from many sources, especially anything touching the open web, ends up with the same text appearing more than once: syndicated news articles, boilerplate legal disclaimers, template emails with only a name swapped in. Lee et al. found this is not a minor inefficiency. In C4, a widely used web-crawl-derived corpus, a single 61-word English sentence appears more than 60,000 times. More strikingly, over 1% of the unprompted output of language models trained on such datasets is copied verbatim from the training data: the model is not generalizing there, it is quoting something it saw enough times to memorize.

### Two different ways to find a duplicate

Deduplication has to catch two different shapes of repetition, and one technique does not catch both:

- **Exact substring matching** finds verbatim repeated spans of text, even ones that only make up part of a document or cross document boundaries. Lee et al. implement this efficiently with a suffix array, which lets a repeated span of any length be found without comparing every document to every other document directly.
- **Near-duplicate matching** finds documents that are mostly the same but differ in small ways, such as a form email with a different recipient's name, or a news wire story picked up with minor edits by many outlets. Lee et al. use MinHash: a technique that estimates how similar two documents are without comparing them token by token, by comparing compact hash-based summaries instead.

Both matter, because a corpus can be free of one kind of duplication while still full of the other.

### What deduplication actually buys

Lee et al. give concrete evidence rather than an intuition. Deduplicating the training data made models emit memorized text roughly ten times less frequently, and let those models reach the same or better accuracy in fewer training steps. It also reduces train-test overlap, which the paper found affects over 4% of the validation set in standard benchmarks; text that leaked from a benchmark's own validation set into training makes an evaluation number look better than the model's real generalization deserves, a concern this track will return to when it links to `llm/evals`'s treatment of contamination.

### Quality filtering is a separate, later step

Deduplication removes redundant copies of text that is already present. Quality filtering removes text that is low-value even without being a duplicate of anything: spam, boilerplate navigation menus, machine-generated text, or documents so garbled they carry little signal. GPT-3's authors describe a concrete version of this in their appendix on Common Crawl filtering: they trained a classifier, using logistic regression over simple bag-of-words-style features, to distinguish curated text (WebText, Wikipedia, a books corpus) from raw, unfiltered Common Crawl. That classifier's score was then used to re-sample Common Crawl so that documents predicted to be higher quality were kept more often, while still keeping some lower-scoring documents rather than discarding them outright. The same appendix also describes a separate fuzzy-deduplication pass with MinHash, which by itself reduced their dataset size by about 10%.

Quality filtering and deduplication are frequently run as separate passes over the same corpus, in either order, and neither substitutes for the other: a corpus can be free of exact duplicates and still full of low-value boilerplate, and it can be uniformly high-quality prose and still contain the same paragraph repeated sixty thousand times.

## Practice

1. ▢ A dataset contains 61 words repeated verbatim in over 60,000 different documents, each time with different surrounding text. Would exact substring matching or near-duplicate matching (MinHash) be the right tool to find and remove just that repeated span, and why?

<details markdown="1"><summary>Hint</summary>

Ask what MinHash actually compares: whole documents against each other, or spans of text that might only be part of a document.

</details>

<details markdown="1"><summary>Check</summary>

Exact substring matching. MinHash estimates similarity between whole documents; a 61-word span repeated inside otherwise-different documents is exactly the kind of partial, cross-document repetition that a suffix-array-based exact substring search is built to catch, while two documents that share only 61 words out of many thousands might not register as near-duplicates of each other at all.

</details>

2. ▢ Which of these is closest to what Lee et al. actually measured, rather than merely argued?

    - a) Deduplication makes a model philosophically more original
    - b) Deduplicated training let models reach the same or better accuracy in fewer steps, and emit memorized text about ten times less often
    - c) Deduplication is only useful for reducing storage costs, with no effect on model behavior
    - d) Near-duplicate matching alone is sufficient to remove all forms of repeated text

<details markdown="1"><summary>Check</summary>

**b)** is the paper's actual measured result. (a) is not a measurable claim. (c) contradicts the memorization and training-efficiency findings directly. (d) is false, since exact substring matching catches a different shape of repetition than near-duplicate matching does, as this lesson's first practice item shows.

</details>

3. ▢ A document is not a duplicate of anything else in the corpus, but it is mostly auto-generated boilerplate with almost no informative content. Would deduplication remove it? What would?

<details markdown="1"><summary>Check</summary>

No, deduplication would not remove it, since deduplication only targets repeated text and this document is unique. Quality filtering, such as the classifier-based re-sampling GPT-3's authors describe, is the step aimed at exactly this case: low-value text that is not a copy of anything else.

</details>

4. ▢ GPT-3's Common Crawl quality classifier was trained to distinguish which of these pairs of things?

    - a) English text from non-English text
    - b) Curated text (WebText, Wikipedia, a books corpus) from raw, unfiltered Common Crawl
    - c) Long documents from short documents
    - d) Duplicated text from unique text

<details markdown="1"><summary>Check</summary>

**b)** Curated text against raw Common Crawl. (d) describes deduplication, which GPT-3's authors ran as a separate MinHash pass, not what the quality classifier itself was trained to detect.

</details>

## Real-world reps

- [ ] Pick a sentence or short phrase you'd expect to be common in web text (a disclaimer, a stock phrase, a common recipe instruction) and search for it verbatim online. Note roughly how many distinct pages you find it on, as a felt sense of how repetition shows up in real crawled text.
- [ ] Read the abstract and introduction of Lee et al.'s paper (linked above) and write, in one sentence each, what exact substring matching and near-duplicate matching are each good at catching that the other is not.
- [ ] Tomorrow: take a corpus you sketched a mixture for in Lesson 1's real-world rep, and for each source type, name one plausible source of duplication (syndication, templated boilerplate, re-posting) and one plausible source of low quality that deduplication alone would not catch.

## Going further

- [Paper: "Deduplicating Training Data Makes Language Models Better", Lee et al., 2021](https://arxiv.org/abs/2107.06499)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
