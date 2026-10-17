---
title: "6. What Few-Shot Examples Teach"
description: Demonstrations mostly teach the format, the label space and the input distribution, which changes how you choose them
type: lesson
---

# Lesson 6. What Few-Shot Examples Teach

**Mission link:** Choosing few-shot examples well starts with knowing what the model takes from them, and the evidence says it is less the answers than the shape of the task.
**Primary source:** [Paper: "Rethinking the Role of Demonstrations", Min et al., 2022](https://arxiv.org/abs/2202.12837)
**Prerequisites:** [Lesson 5](0005-format-sensitivity.md), [Few-shot prompt](../GLOSSARY.md), [Zero-shot prompt](../GLOSSARY.md)

## Warm-up

1. ▢ Lesson 4 separated instructions from data with tags. Name one thing in a few-shot prompt that should sit inside its own tag, and why.

<details markdown="1"><summary>Check</summary>

The examples, wrapped together (for instance in an examples tag with one tag per example), so the model can tell demonstrations from instructions and from the real input. Without the tags, an example can be read as an instruction, or the real input as one more example.

</details>

2. ▢ Lesson 5 said a formatting change with no meaning can move accuracy. What does that predict about two few-shot prompts whose examples are identical but one writes `Label:` and the other `Answer:`?

<details markdown="1"><summary>Check</summary>

That their accuracy can differ, so neither is known to be better until both are tested. The edit changes no meaning, yet it changes the token sequence the model continues, which is the point of lesson 5.

</details>

## Know this

### The surprising result

A **few-shot prompt** shows the model input and output pairs before the real input. The obvious guess is that the model learns the input-to-output mapping from them, the way a classifier learns from labelled data. Min et al. tested that guess by replacing the labels in the demonstrations with random ones. Across 12 models, including GPT-3, performance barely dropped: 0 to 5% absolute for nearly all models, 2.6% on average for classification tasks and 1.7% for multi-choice tasks.

If correct labels are not what helps, something else in the demonstrations must be. The paper names three things, and each was tested by removing it:

| What the demonstration provides | What happens when it is removed |
|---|---|
| The label space: the set of answers the model may give | Replacing labels with random English words cost 5 to 16% absolute for direct models |
| The input distribution: text that looks like the real inputs | Replacing inputs with random corpus text cost 3 to 16% absolute for most of the models tested |
| The format: input then label, repeated | Dropping the pairing left performance close to or worse than no demonstrations |

### What this does not say

Three limits keep this from becoming "labels do not matter".

The models were GPT-2 Large up to GPT-3 (774M to 175B parameters), and the tasks were classification and multi-choice. The paper does not test whether a current chat model behaves the same way, so treat it as a strong prior, then test your own model.

Random labels still cost something, and the cost was not uniform: one model on classification dropped nearly 10% when every label was wrong. "Barely hurts" is an average over the models and tasks tested.

The authors also note that in-context learning may not work on a task whose input-label correspondence the model has not already captured. Demonstrations locate a task the model can mostly do. They are a weaker way to teach it a mapping it has never seen.

### How this changes the choice of examples

If the model reads format, label space and input distribution off the examples, those three are what to get right.

- **In the target format.** Every example should look exactly like the real input and the output you want, down to casing and punctuation. Lesson 5 explains why small differences are not free.
- **Covering the label space.** Show every label the model may output, so none is a surprise.
- **Like the real inputs.** Use text from the real distribution, not tidy invented sentences.

Anthropic's best-practices guide says the same in practitioner terms: make examples relevant (mirror the actual use case), diverse (cover edge cases and vary enough that the model does not pick up unintended patterns) and structured (wrapped in tags), and it suggests 3 to 5 examples. That is one vendor's documented advice, not a measured result.

None of this is a licence to ship wrong labels. Correct labels cost nothing and avoid the worst case in the paper.

## Practice

1. ▢ Predict, then run. Paste this prompt into a chat window. The labels on the three examples are deliberately wrong. Predict what the model outputs for the last review, then run it.

    ```text
    Classify each review as Positive or Negative.

    Review: The battery lasts all day and the screen is gorgeous.
    Label: Negative

    Review: It stopped working after two days and support never replied.
    Label: Positive

    Review: Arrived on time and works exactly as described.
    Label: Negative

    Review: Terrible fit, the zipper broke on the first use.
    Label:
    ```

<details markdown="1"><summary>Hint</summary>

Ask what the examples still teach even when their labels are wrong: the format, the two allowed words, and what a review looks like.

</details>

<details markdown="1"><summary>Check</summary>

Min et al. predict a one-word answer from the allowed pair, and for an unambiguous review most likely the correct one (Negative), because the model's own sense of the task survives wrong labels. A model that copies the swapped mapping instead is a finding about that model, not an error in the paper. Either way the output format (a single word after `Label:`) should hold, since the format is what the examples taught reliably.

</details>

2. ▢ Which change to a working few-shot prompt would the paper predict hurts most?

    - a) Swapping the labels so that some examples carry a wrong answer
    - b) Replacing the example inputs with random sentences from a corpus
    - c) Reordering the same examples while keeping every label correct
    - d) Adding one more example that matches the existing format

<details markdown="1"><summary>Check</summary>

**b)** Replacing inputs with out-of-distribution text cost 3 to 16% absolute for most models tested, more than wrong labels (0 to 5% for nearly all). (a) is the paper's headline: small cost. (c) is not tested in this paper; ordering is lesson 7's topic, and it is not harmless. (d) adds a demonstration in the right format, which the paper says does not much change results once there are 8 or so.

</details>

3. ▢ This prompt is meant to tag support tickets. Name every way its examples fail to teach the format, label space or input distribution, and say what you would change.

    ```text
    Tag the ticket as billing, bug or account.

    Ticket: I was charged twice this month.
    Tag: billing

    This one is a bug report: The export button does nothing.
    bug

    Ticket: How do I change my email address?
    Tag: Account.
    ```

<details markdown="1"><summary>Hint</summary>

Compare the three examples line by line. Do they share a layout? Do they share spelling and punctuation of the label? Count the labels.

</details>

<details markdown="1"><summary>Check</summary>

Format: the second example drops `Ticket:` and `Tag:` and adds a commentary phrase, so the pattern is broken once. Label space: `billing`, `bug` and `Account.` differ in casing and punctuation, so the model sees three label spellings where the task has three exact labels. The label `Account.` with a full stop teaches that punctuation is part of the answer. Input distribution: the tickets are one short line each and may not look like real tickets (which are longer and messier). Fix: one layout for every example, the exact label spelling every time, and tickets pasted from real ones.

</details>

4. ▢ A classifier must output one of Billing, Bug, Account. From this pool, pick the three examples you would use and say why you rejected the rest.

    ```text
    A. "I was charged twice for May" -> Billing
    B. "Why did my card get billed two times in May??" -> Billing
    C. "app crashes when I tap export, iOS 17, v4.2" -> Bug
    D. "Our blog post explains how crashes can be diagnosed" -> Bug
    E. "can't log in after changing my phone number" -> Account
    F. "Please update the invoice address" -> Billing
    ```

<details markdown="1"><summary>Check</summary>

One reasonable pick is A, C and E: one example per label covers the label space, they share a layout, and their rough, real-looking phrasing matches the input distribution. B is nearly a duplicate of A, so it adds nothing diverse. D is polished prose that does not look like a ticket (an input-distribution mismatch) and is labelled Bug for the wrong reason. F is fine on its own but a second Billing example before any other label risks the bias lesson 7 covers. Other picks are defensible if they cover all three labels and avoid D.

</details>

## Real-world reps

- [ ] Take a few-shot prompt you already use. List which of format, label space and input distribution each example shows, and flag any example that shows none.
- [ ] Run one prompt twice, once with real examples and once with the same examples relabelled at random, on five inputs. Note how many answers changed.
- [ ] Tomorrow: rewrite one few-shot prompt so every example shares one layout and exact label spelling, then run it on the same five inputs and compare.

## Going further

- [Few-Shot and Reasoning](../reference/few-shot-and-reasoning.md)
- [Paper: "Rethinking the Role of Demonstrations", Min et al., 2022](https://arxiv.org/abs/2202.12837)
- [Docs: "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#use-examples-effectively)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
