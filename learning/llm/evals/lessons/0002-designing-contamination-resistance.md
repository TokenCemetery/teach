---
title: 2. Designing Contamination Resistance
description: Preventing contamination in a custom eval set from the start, instead of only detecting it after the fact
type: lesson
---

# Lesson 2. Designing Contamination Resistance

**Mission link:** Lesson 1's guided-instruction test detects contamination in an eval you didn't build, after the fact. Building your own eval set means you can design against contamination happening at all, which is cheaper than catching it later.
**Primary source:** [Paper: "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models" (BIG-bench), Srivastava et al., 2022](https://arxiv.org/abs/2206.04615)
**Prerequisites:** [Lesson 1](0001-held-out-and-contamination.md), [Data contamination](../GLOSSARY.md)

## Warm-up

1. ▢ What are the two distinct pathways lesson 1 named for data contamination?

<details markdown="1"><summary>Check</summary>

Pretraining absorption: a benchmark gets scraped into web-crawl training data before anyone builds an eval on it. Iterative overfitting to the eval: no literal data leakage, but a team tunes repeatedly against the same eval set until it stops measuring the underlying skill.

</details>

2. ▢ What does the guided-instruction test from lesson 1 actually check for, and how does it work?

<details markdown="1"><summary>Check</summary>

It checks whether a specific benchmark instance was in a model's training data, by giving the model the first part of the instance and asking it to complete the rest verbatim. Reproducing specifics a plausible guess wouldn't recover is strong evidence of contamination.

</details>

## Know this

### Detecting contamination is not the same job as preventing it

Lesson 1's guided-instruction test is a detection tool: it tells you, after the fact, whether contamination probably already happened to a benchmark you didn't control. When you're building your own eval set instead of borrowing someone else's, the better position is preventing contamination from ever occurring, since that is far cheaper than discovering it later and having to rebuild the set.

### Use data that postdates the model's training cutoff

The most direct prevention: build eval examples from material that did not exist before the model's training data was collected. Pretraining absorption requires the data to have existed and been crawlable before training happened; data created after that cutoff cannot possibly be in it. This requires knowing, or getting a reliable statement of, the model's actual training cutoff date, not guessing at it, since the technique only works if the cutoff claim is accurate.

### Canary strings signal "do not train on this"

BIG-bench introduced the **canary string** convention: a unique, distinctive marker phrase embedded alongside benchmark data, explicitly asking any crawler assembling a training corpus to exclude content containing it. This does two things. First, it is a preventive signal: crawlers and dataset curators that respect the convention exclude the marked data before training ever happens, rather than after. Second, it doubles as a detection tool of last resort: if a canary string later surfaces in a model's output or in an accessible training corpus, that is direct evidence the exclusion request was not honored, without needing the guided-instruction test's inference from a completion. A canary string is a request, not an enforcement mechanism: it depends on crawlers choosing to respect it, so it reduces risk rather than eliminating it.

### Checking against a known corpus, when you can

When the pretraining corpus behind a model is known or accessible (an open corpus like a public web-crawl dataset), a direct **n-gram overlap check** between your eval data and that corpus can measure contamination risk before the eval ever gets used, rather than inferring it from model behavior the way lesson 1's guided-instruction test does. This only works when the corpus is actually available to check against; for a closed model whose training data is undisclosed, the guided-instruction test remains the tool available.

### Keeping the set private is the simplest prevention of all

Pretraining absorption happens because benchmarks get published, then scraped. An eval set that is never posted publicly, kept internal to the team using it, cannot be scraped into anyone's future pretraining corpus. This is the strongest prevention available and the reason a held-out set worth trusting for a long time is often one nobody outside the team has ever seen, at the cost of losing the reproducibility and external scrutiny a published benchmark offers.

## Practice

1. ▢ A team wants to build an eval resistant to pretraining absorption. They consider sourcing questions from articles published after the model's stated training cutoff. Why does this work, and what do they need to verify first?

<details markdown="1"><summary>Check</summary>

It works because pretraining absorption requires the data to have existed and been crawlable before training happened; data created after the cutoff cannot be in a corpus collected before it existed. They need to verify the model's actual training cutoff is accurate and not just an approximate or marketing claim, since the technique only protects against contamination if the cutoff date is trustworthy.

</details>

2. ▢ What does embedding a canary string in a custom eval set actually protect against, and what does it not guarantee?

<details markdown="1"><summary>Hint</summary>

Think about whether a canary string is a request or an enforcement mechanism.

</details>

<details markdown="1"><summary>Check</summary>

It signals to any crawler assembling a training corpus that the marked content should be excluded, preventing contamination before training happens if the convention is respected, and it gives a direct way to detect a leak later if the string surfaces in a model's output or an accessible corpus. It does not guarantee exclusion: it depends on crawlers choosing to honor the convention, so it reduces risk rather than eliminating it.

</details>

3. ▢ When is an n-gram overlap check against a known corpus a better tool than lesson 1's guided-instruction test, and when does it stop being usable at all?

<details markdown="1"><summary>Check</summary>

It's better when the pretraining corpus is known and accessible, since it measures overlap directly rather than inferring contamination from model behavior, and can be run before the eval is ever used. It stops being usable when the corpus is undisclosed or inaccessible, which is the normal case for a closed model, and the guided-instruction test remains the available option there.

</details>

4. ▢ A team keeps their custom eval set entirely private, never posting it publicly. What contamination pathway does this most directly prevent, and what does it cost them in exchange?

<details markdown="1"><summary>Check</summary>

It prevents pretraining absorption most directly, since that pathway depends on a benchmark being published and then scraped; an unpublished set cannot be scraped. The cost is losing the reproducibility and external scrutiny that a published benchmark offers, since nobody outside the team can verify or reuse it.

</details>

5. ▢ Which claim is true of canary strings and n-gram overlap checks compared to lesson 1's guided-instruction test?

   - a) Both are detection methods identical in mechanism to the guided-instruction test
   - b) They are preventive or corpus-dependent techniques, usable when building a custom eval or when the training corpus is accessible, unlike the guided-instruction test which works on any model's behavior
   - c) They only apply to code-execution evals, not text-based ones
   - d) Canary strings guarantee a benchmark will never be trained on

<details markdown="1"><summary>Check</summary>

**b)** A canary string is preventive (a request to exclude, checked before or after the fact), and an n-gram overlap check requires an accessible corpus; the guided-instruction test instead infers contamination from any model's completions, needing no corpus access. (a) is false: the mechanisms differ, as the lesson describes. (c) is false: nothing about either technique restricts it to code. (d) is false: a canary string is a request that depends on crawler cooperation, not a guarantee.

</details>

## Real-world reps

- [ ] For a custom eval set you're building or maintaining, check whether it's ever been posted publicly, and if so, treat any high score on it with the same suspicion lesson 1 applied to contaminated public benchmarks.
- [ ] Draft a canary string for an eval set you control, following BIG-bench's convention, and add it to the set's data.
- [ ] Tomorrow: find out the actual training cutoff date for a model you evaluate regularly, from its documentation rather than assumption, and note whether any of your eval data predates it.

## Going further

- [Paper: "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models" (BIG-bench), Srivastava et al., 2022](https://arxiv.org/abs/2206.04615)
- [Paper: "Time Travel in LLMs: Tracing Data Contamination in Large Language Models", Golchin and Surdeanu, 2023](https://arxiv.org/abs/2308.08493)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
