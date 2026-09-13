---
title: 4. Training a Reward Model: The Bradley-Terry Loss
description: A reward model never sees an absolute score in training, only which of two completions a human liked more
type: lesson
---

# Lesson 4. Training a Reward Model: The Bradley-Terry Loss

**Mission link:** "Train a reward model on preference pairs using the Bradley-Terry loss, and identify a reward-hacked completion from a policy trained against it" is the second bullet under Success looks like. This lesson covers training the reward model; Lesson 5 covers what can go wrong once a policy is optimized against it.
**Primary source:** [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Prerequisites:** [Lesson 3](0003-loss-masking-on-non-assistant-tokens.md)

## Warm-up

1. ▢ What does loss masking on non-assistant tokens actually do, mechanically, during SFT training?

<details markdown="1"><summary>Check</summary>

It gives each prompt or non-assistant token's position a label the loss function is told to ignore, so only assistant (answer) positions contribute a gradient, even though the prompt tokens are still present as input the model conditions on.

</details>

2. ▢ What breaks in SFT training if this masking is skipped?

<details markdown="1"><summary>Check</summary>

Gradient signal gets spent, or diluted, on learning to predict the prompt's own tokens, which is not the skill SFT is meant to teach, rather than concentrated entirely on the answer tokens the model should actually learn to produce.

</details>

## Know this

### Collecting preference data

A reward model needs data that says which of two model outputs is better, not what the best output should have been word for word. Ouyang et al. collect this by presenting labelers with several outputs (they use between 4 and 9) to the same prompt and having them rank the whole set, rather than only ever comparing two at a time. A ranking over `K` outputs produces every pairwise comparison within that ranking, `K` choose 2 of them, so a single ranking task yields many training pairs at once.

### Where the reward model comes from

A reward model is not trained from a blank slate. Ouyang et al. describe starting from the SFT model itself, with its final unembedding layer, the part that turns a hidden state into next-token probabilities, removed and replaced with a layer that outputs a single scalar. The reward model reuses everything the SFT model already learned about language and about the target behavior, repurposed to output one number, a score, for a given prompt and completion, instead of a distribution over the next token.

### The Bradley-Terry loss

Given a preferred completion `y_w` ("winner") and a rejected completion `y_l` ("loser") for the same prompt `x`, and the reward model's scalar outputs `r(x, y_w)` and `r(x, y_l)` for each, Ouyang et al. train the reward model with this loss:

```text
loss(θ) = -E[log(σ(r_θ(x, y_w) - r_θ(x, y_l)))]
```

where `σ` is the logistic sigmoid function. This is the **Bradley-Terry loss**: it treats the probability that a human would prefer `y_w` over `y_l` as the sigmoid of the difference between their two scores, and trains the reward model to make that predicted probability match what the human labeler actually chose. Pushing this loss down means pushing `r(x, y_w) - r(x, y_l)` up: the model is trained to make the preferred completion's score higher than the rejected one's, by a margin proportional to how confidently the sigmoid needs to favor it.

### Why the reward's absolute scale is not meaningful on its own

Notice that the loss depends only on the *difference* between the two scores, never on either score by itself. Adding the same constant to every reward the model ever outputs would leave every difference, and therefore the entire loss, completely unchanged. This means nothing about training forces the reward model's scores onto any particular absolute scale; only the relative ordering (and the size of gaps) between preferred and rejected completions is ever constrained. Ouyang et al. handle this directly: since the loss is invariant to a shift, they normalize the reward model with a bias so that labeler demonstrations score a mean of 0, before using it in reinforcement learning, giving the otherwise-arbitrary scale a fixed anchor to be measured against.

### Why comparisons from one ranking are kept together

Treating every one of the `K` choose 2 comparisons from a single ranking task as an independent, separately shuffled training example causes a specific problem: since the same small set of completions reappears across many of those comparisons, a single pass over data built this way tends to overfit, each completion effectively gets reused across `K - 1` correlated comparisons. Ouyang et al.'s fix is to treat all the comparisons from one ranking task as a single batch element during training, rather than shuffling them independently into the wider dataset, which they found improved validation accuracy and loss compared to treating each pairwise comparison as fully independent.

## Practice

1. ▢ A reward model outputs `r(x, y_w) = 2.0` and `r(x, y_l) = 1.0` for one pair, and `r(x, y_w) = 12.0` and `r(x, y_l) = 11.0` for a second pair, from a different prompt. Does the Bradley-Terry loss treat these two pairs differently?

<details markdown="1"><summary>Hint</summary>

The loss is a function of `r(x, y_w) - r(x, y_l)`, not of either value on its own.

</details>

<details markdown="1"><summary>Check</summary>

No. Both pairs have the same difference, `1.0`, and the loss depends only on that difference, not on the absolute scores. This is exactly why the reward model's absolute scale is not meaningful without an external anchor.

</details>

2. ▢ Where does a reward model's initial weights actually come from, per Ouyang et al.?

<details markdown="1"><summary>Check</summary>

The SFT model, with its final unembedding layer removed and replaced by a layer that outputs a single scalar, rather than a fresh, randomly initialized model.

</details>

3. ▢ A labeler ranks 4 completions (`K = 4`) for a single prompt. How many pairwise comparisons does this one ranking task produce for training?

<details markdown="1"><summary>Check</summary>

6 (`4` choose `2`, which is `(4 × 3) / 2 = 6`).

</details>

4. ▢ Why do Ouyang et al. keep all comparisons from one ranking task together as a single batch element, rather than shuffling each pairwise comparison independently into the training set?

    - a) It makes the reward model train faster with no effect on accuracy
    - b) Shuffling them independently causes overfitting, since the same small set of completions is reused across many correlated comparisons within one ranking task
    - c) The Bradley-Terry loss cannot be computed unless comparisons are grouped this way
    - d) It is required so the reward model's scores fall in a fixed numeric range

<details markdown="1"><summary>Check</summary>

**b)** is the reason Ouyang et al. give directly: correlated, reused completions across a ranking task's comparisons cause a single pass to overfit if shuffled independently. (a), (c), and (d) do not describe the actual issue or its fix.

</details>

## Real-world reps

- [ ] Find a public preference dataset (many are published for training reward models) and check how many completions are ranked per prompt, and whether the released format already reflects pairwise comparisons or a full ranking.
- [ ] Compute, by hand, the Bradley-Terry loss's sigmoid term for a reward difference of `0` (no preference signal at all) and for a large positive difference, and describe in one sentence how the loss behaves at each extreme.
- [ ] Tomorrow: without looking ahead, write a one-sentence prediction for Lesson 5: if a reward model is only ever trained to rank the completions humans have actually shown it, what might go wrong once a policy is free to generate any completion at all, searching for whatever scores highest?

## Going further

- [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
