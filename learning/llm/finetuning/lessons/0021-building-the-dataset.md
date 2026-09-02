---
title: 21. Building the Dataset
description: Data beats every hyperparameter in this workspace
type: lesson
---

# Lesson 21. Building the Dataset

**Mission link:** Data quality dominates every hyperparameter in this workspace. Stage 3 taught you to turn a knob; this stage teaches you what actually moves the result.
**Primary source:** [Paper: "LIMA: Less Is More for Alignment", Zhou et al., arXiv:2305.11206](https://arxiv.org/abs/2305.11206)
**Prerequisites:** [Lesson 3](0003-tokenizers-and-chat-templates.md), [Lesson 12](0012-reading-a-training-run.md)

## Warm-up

1. ▢ What is the highest-value check to run before a training job?

<details markdown="1"><summary>Check</summary>

Decode one real training example and read it, counting scored versus masked positions. It catches template mismatch, missing end-of-turn tokens, masking bugs and truncation at once.

</details>

2. ▢ What does a staircase loss curve with drops at epoch boundaries mean?

<details markdown="1"><summary>Check</summary>

Memorisation: the model is recognising examples it has already seen.

</details>

3. ▢ Which loss variant should instruction tuning normally use?

<details markdown="1"><summary>Check</summary>

Completion-only. Prompt positions are masked to `-100` so only the assistant response is scored.

</details>

## Know this

### The uncomfortable ratio

If you have limited time, spend it on data. The gap between a mediocre dataset and a good one is larger than the gap between rank 8 and rank 128, larger than LoRA versus DoRA, and larger than most things you could tune. Hyperparameters are legible and satisfying to adjust, which is why they absorb attention out of proportion to their effect.

The LIMA result is the sharpest published statement of this: a small number of carefully curated examples, on the order of a thousand, produced strong instruction-following, supporting the view that supervised fine-tuning mostly teaches *format and style* while capability comes from pretraining. Treat the exact number as setting-specific; take the direction seriously.

### What fine-tuning teaches well, and badly

| Teaches well | Teaches badly |
|---|---|
| Output format and structure | New facts about the world |
| Tone, register, domain voice | Reasoning ability not already present |
| Consistent adherence to a schema | Anything requiring current information |
| Narrow classification and extraction | Long-tail knowledge with a single mention |
| Tool-call and function syntax | Arithmetic and precise calculation |

The right column is why [Lesson 27](0027-when-not-to-fine-tune.md) exists. A dataset built to install facts is doing the thing fine-tuning is worst at, and each fact would need many varied examples to stick, at which point retrieval is cheaper, more accurate and updatable.

### Designing examples

**Match the deployment distribution.** Your training inputs should look like real inputs. Clean, well-formed, uniform-length training prompts produce a model that degrades on the messy reality it meets in production, and your held-out split, drawn from the same clean pool, will not warn you.

**Include the hard cases deliberately.** Ambiguous inputs, edge cases, and the cases where the correct answer is a refusal or "insufficient information". If every training answer is confident and complete, you have trained confident completeness, including on inputs that do not warrant it.

**Be consistent about format.** If half your examples end with a period and half do not, the model learns the inconsistency. Every arbitrary variation you leave in is capacity spent on noise.

**Make the outputs exemplary.** The model imitates its targets. A dataset of adequate answers produces adequate answers, and no hyperparameter recovers from that.

**Vary the surface, not the substance.** Multiple phrasings of the same request teach robustness to phrasing. Multiple near-identical examples teach memorisation.

### Deduplication

Near-duplicates are the most common serious defect in assembled datasets, and they cause two harms at once: over-weighting whatever the duplicated content teaches, and, if duplicates land on both sides of your split, a held-out score that measures recall rather than generalisation.

Exact-match deduplication is not enough. Use normalised hashing, then a similarity measure such as MinHash or embedding distance for near-duplicates. Do it *before* splitting, not after.

### Size and balance

A rough orientation, not a rule:

| Examples | Realistic target |
|---|---|
| 50 to 200 | Style, tone, a fixed output format |
| 500 to 2,000 | A well-defined task with narrow scope |
| 5,000 to 50,000 | A broad task, or several capabilities at once |
| 100,000+ | Diminishing returns for adapters; consider whether the task is really one task |

Where categories exist, imbalance becomes a bias. A dataset that is 90% one class teaches the model to guess that class. Either balance it or account for the imbalance in your metric, per Lesson 23.

### Synthetic data

Generating training data with a stronger model is standard, effective, and has two specific hazards.

**Inherited errors.** The generator's mistakes and biases become your training targets, and they will be fluent and consistent, which makes them hard to spot by skimming. Sample and read.

**Distribution collapse.** Generated data tends to be more uniform than real data: similar structures, similar lengths, similar register. You train a model that handles a narrow slice cleanly and real variation poorly. Seed generation from real inputs where you can, and vary prompts deliberately.

Also: check the licence and terms of the model you generate from. Whether outputs may be used to train another model is a real constraint, not a formality.

### Formatting

Get the mechanics right, once:

- Render through the model's own chat template (Lesson 3). Verify with `repr`.
- Mask prompt positions unless you deliberately want them scored.
- Include the end-of-turn token, or the model will not learn to stop.
- Check the token-length distribution and set `max_length` from its high percentile, not its maximum and not a guess.
- Confirm truncation is not cutting answers in half. A silently truncated target teaches the model to stop mid-sentence.

## Practice

1. ▢ You want the model to know your company's 400 product SKUs. Is a fine-tuning dataset the right tool?

<details markdown="1"><summary>Check</summary>

No. Those are facts, which fine-tuning installs unreliably: each would need many varied examples, and the result is unverifiable and stale the moment the catalogue changes.

Retrieval is the right tool: accurate, citable, and updated by editing a document rather than retraining. What fine-tuning *could* usefully teach here is the format for presenting product information.

</details>

2. ▢ All your training prompts are clean, well-punctuated sentences. Production inputs are terse and full of typos. What happens, and why won't your held-out set catch it?

<details markdown="1"><summary>Check</summary>

The model performs well on clean input and degrades on real input, because it never saw real input.

Your held-out split is drawn from the same clean pool, so it shares the defect. It measures performance on the wrong distribution and reports success. The fix is training and evaluation data drawn from actual deployment traffic.

</details>

3. ▢ Why deduplicate before splitting rather than after?

<details markdown="1"><summary>Check</summary>

Because a duplicate pair straddling the split puts a training example into the held-out set. Held-out performance then measures memorisation and reports it as generalisation, which is the single most effective way to fool yourself about a fine-tune.

Deduplicating after the split leaves cross-split pairs intact, which is exactly the case that matters.

</details>

4. ▢ Which dataset defect is most likely to produce a model that never says "I don't know"?

   - a) A class imbalance favouring one category strongly
   - b) Every single answer being confident and complete
   - c) Near-duplicate examples appearing across the split
   - d) A token-length distribution with a very long tail

<details markdown="1"><summary>Check</summary>

**b)** Every single answer being confident and complete.

The model imitates its targets. With no example of appropriate uncertainty or refusal, confident completeness is the only behaviour it has been shown, including for inputs that do not support it.

</details>

5. ▢ Name the two hazards of synthetic data and one mitigation for each.

<details markdown="1"><summary>Check</summary>

Inherited errors: the generator's mistakes become fluent, consistent training targets. Mitigate by sampling and reading a real fraction, and by validating against ground truth where any exists.

Distribution collapse: generated data is more uniform than real data. Mitigate by seeding generation from real inputs and deliberately varying the generation prompts.

</details>

6. ▢ Your dataset's token lengths run from 50 to 8000, with the 95th percentile at 1200. What `max_length` do you set, and what do you check?

<details markdown="1"><summary>Check</summary>

Around 1200 to 1500. Setting 8000 wastes activation memory on padding for almost every example; setting 512 truncates a substantial fraction.

Then check what truncation actually does to the examples above the limit. If it cuts answers in half you are teaching the model to stop mid-sentence, so either raise the limit or drop those examples deliberately.

</details>

## Real-world reps

- [ ] Read twenty examples of your dataset in full, decoded through the chat template. Note every inconsistency you find.
- [ ] Run near-duplicate detection across the whole set before splitting. Record how many you found and remove them.
- [ ] Plot the token-length distribution and pick `max_length` from it. Inspect three examples that would be truncated.
- [ ] Tomorrow: add ten deliberately hard examples: ambiguous, edge-case, or where the right answer is a refusal.

## Going further

- [Paper: "LIMA: Less Is More for Alignment", Zhou et al., arXiv:2305.11206](https://arxiv.org/abs/2305.11206)
- [Docs: Dataset formats, Hugging Face TRL](https://huggingface.co/docs/trl/main/en/dataset_formats)
- [Lesson 22. Contamination and Held-Out Design](0022-contamination-and-held-out-design.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
