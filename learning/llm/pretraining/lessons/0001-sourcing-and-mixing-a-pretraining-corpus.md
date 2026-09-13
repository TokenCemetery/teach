---
title: 1. Sourcing and Mixing a Pretraining Corpus
description: What goes into a pretraining corpus, and why the mixture of sources matters more than the total byte count
type: lesson
---

# Lesson 1. Sourcing and Mixing a Pretraining Corpus

**Mission link:** "Build a deduplicated, quality-filtered pretraining corpus from raw sources, and say what each filtering step removes and why" is the first bullet under Success looks like. This lesson covers the sourcing and mixing half of that; Lesson 2 covers deduplication and quality filtering.
**Primary source:** [Paper: "The Pile: An 800GB Dataset of Diverse Text for Language Modeling", Gao et al., 2020](https://arxiv.org/abs/2101.00027)
**Prerequisites:** none

## Know this

### What a pretraining corpus is made of

A pretraining corpus is the raw collection of documents a model trains on before any of it is tokenized: web crawls, books, code repositories, academic papers, forum posts, reference sites, and more, gathered from many separate sources rather than scraped from one giant crawl. Treating "the corpus" as a single undifferentiated pile of text hides the decision that actually shapes what the model learns, which is what sources went in and how much of the final corpus each one makes up.

### Sourcing is a mixture decision, not just an inclusion decision

The Pile is a useful worked example because its authors documented the reasoning rather than just shipping the dataset. It assembles 825 GiB of text from 22 diverse, high-quality subsets, many drawn from academic or professional sources (legal filings, academic papers, technical documentation) that a general web crawl underrepresents. The paper's own evaluation makes the case concrete: GPT-2 and GPT-3, neither of which trained on the Pile, struggle on many of its components, "such as academic writing," while models trained on the Pile improve significantly over models trained on Raw Common Crawl or CC-100, across every one of the Pile's own components and on downstream evaluations as well.

That result is not really about total size. It is about which domains got included at all, and it is why "how big is the corpus" is the wrong first question to ask about a pretraining run.

### Proportion is the lever, not just presence

Once a source is included, a second decision remains: how much of the final token budget it gets. A source that dominates the raw byte count of the internet (forum chatter, marketing copy, boilerplate navigation text) is not automatically entitled to dominate the corpus, and a source that is small in raw bytes but information-dense (curated academic text, reference documentation) is not stuck at whatever share it occupies naturally. A corpus's designer chooses to upsample some sources relative to their natural size and cap others well below it, and that choice is independent of, and made after, the decision to include the source at all.

Two corpora can include the exact same list of sources and still behave differently once trained on, if their proportions differ. This is why "mixture" and "sourcing" are two separate decisions worth naming separately, even though a table of dataset names makes them look like the same thing.

### The corpus is a design artifact

Sourcing and mixing happen before a single token of training runs, and they are as consequential as any hyperparameter chosen afterward. A model trained on a badly composed corpus wastes compute relearning redundant or low-value patterns no matter how well the later stages of a pretraining run (the ZeRO sharding in Stage 5, the learning-rate schedule in Stage 7) are executed. Those later stages make training efficient; this stage decides what there is to become efficient at learning.

## Practice

1. ▢ The Pile assembled 825 GiB of text from 22 diverse sources rather than scraping a single web crawl to that same size. Per the paper's own evaluation, what did GPT-2 and GPT-3 (neither trained on the Pile) do on many of the Pile's components, and what does that result say about relying on web-crawled text alone?

<details markdown="1"><summary>Check</summary>

They struggled, particularly on components like academic writing. That is direct evidence that a corpus built mostly from general web-crawled text leaves a model with thin exposure to entire genres, regardless of how much web text it saw.

</details>

2. ▢ A team doubles the raw byte count of their web-crawl component while leaving every other source's byte count fixed, without any other change to the corpus design. What happens to the mixture?

    - a) The mixture is unchanged, since sourcing only concerns which sources are included, not how much of each
    - b) The web crawl's share of the final corpus grows, even though nobody deliberately decided to make it a larger fraction of what the model learns from
    - c) The mixture only matters for how the tokenizer is trained, not for the model itself
    - d) Doubling the size of any single source always improves downstream performance

<details markdown="1"><summary>Hint</summary>

Nothing about which sources are present changed here. Ask what changed about how much of the total each one contributes.

</details>

<details markdown="1"><summary>Check</summary>

**b)** The web crawl's share grows by default, as an accidental side effect of a byte-count change, not because anyone decided the model should learn disproportionately more from it. (a) confuses inclusion with proportion, which is exactly the distinction this lesson draws. (c) is false: mixture shapes what the model is trained on, not only how the vocabulary is built. (d) is false in general; more of a low-information source can dilute a corpus rather than improve it.

</details>

3. ▢ A newly assembled corpus repeats a small, 2 GB collection of curated legal filings several times over relative to its natural share, while capping a 400 GB raw web-crawl component well below its natural share. Both sources were already selected for inclusion before this decision was made. Is this a sourcing decision or a mixing decision, and why?

<details markdown="1"><summary>Check</summary>

A mixing decision. The set of sources did not change; both were already present. What changed is how much of the final token budget each one is allowed to contribute, which is exactly the proportion question this lesson separates from the inclusion question.

</details>

## Real-world reps

- [ ] Read the list of component sources in The Pile paper (its Table 1, in the linked paper) and note which two or three feel most surprising to see in a language-model training corpus, and why you would not have thought to include them.
- [ ] Find the documented composition of a well-known open pretraining corpus you have not examined before (RedPajama, Dolma, or FineWeb are all documented publicly). Write down roughly what fraction is general web-crawled text versus curated or structured sources.
- [ ] Tomorrow: sketch a hypothetical corpus mixture for a model you would want to be unusually good at a specific domain (legal reasoning, scientific literature, a programming language). Name four or five source types you would include, and for each say, in your own words, whether you would upsample it above its natural share, cap it below, or leave it as-is, and why.

## Going further

- [Paper: "The Pile: An 800GB Dataset of Diverse Text for Language Modeling", Gao et al., 2020](https://arxiv.org/abs/2101.00027)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
