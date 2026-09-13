---
title: 9. DPO's Implicit Reward: Why the Partition Function Cancels
description: An intractable normalizing term stands between a reward and its optimal policy, until a difference of two rewards makes it vanish
type: lesson
---

# Lesson 9. DPO's Implicit Reward: Why the Partition Function Cancels

**Mission link:** "Derive DPO's implicit reward from the same preference data RLHF uses, and say what it gives up by removing the RL loop" is the fourth bullet under Success looks like. This lesson covers the derivation itself; Lesson 10 covers the resulting loss and what it drops relative to PPO.
**Primary source:** [Paper: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
**Prerequisites:** [Lesson 8](0008-why-ppo-is-expensive-and-unstable.md)

## Warm-up

1. ▢ Name the four (or five, counting the value function separately) models involved in a PPO training step for RLHF, and what each is used for.

<details markdown="1"><summary>Check</summary>

The policy being trained; a frozen SFT model, for the KL penalty; the reward model, which scores outputs; and the value function (initialized from the reward model), which produces the advantage estimates PPO's clipping needs.

</details>

2. ▢ Per Ouyang et al.'s own finding, was a larger, lower-loss reward model always the better practical choice for PPO?

<details markdown="1"><summary>Check</summary>

No. Their 175B reward model had more unstable training and higher compute cost as a value-function initialization than their 6B one, which they found stable and just as effective, so they used the smaller model for every policy size.

</details>

## Know this

### The same starting objective as RLHF

Rafailov et al. start from exactly the KL-constrained reward-maximization objective Lesson 6 already covers: maximize the expected reward `r(x, y)` under the policy, minus a KL penalty (scaled by `β`) against a fixed reference policy `π_ref`. Prior work, which Rafailov et al. build directly on, showed that this objective has a known, closed-form optimal solution:

```text
π_r(y|x) = (1 / Z(x)) · π_ref(y|x) · exp((1/β) · r(x, y))
```

where `Z(x)` is a **partition function**, a normalizing sum over every possible completion `y` to the prompt `x`, needed to make `π_r` a valid probability distribution. Computing `Z(x)` exactly would mean summing over every possible completion a language model could generate, which is exactly as intractable as it sounds, and is exactly why this closed form, correct as it is, was not directly usable as a training method on its own.

### Inverting the relationship

Rafailov et al.'s move is to rearrange this same equation to solve for the reward instead of the policy. Taking the logarithm of both sides and rearranging gives:

```text
r(x, y) = β · log( π_r(y|x) / π_ref(y|x) ) + β · log Z(x)
```

This expresses the reward implied by any policy `π_r`, in terms of that policy, the reference policy, and the same troublesome partition function, still present as an additive term.

### Why the partition function stops mattering

This is where the Bradley-Terry loss (Lesson 4) does real work. Bradley-Terry preference probabilities depend only on the *difference* between two completions' rewards, `r(x, y_1) - r(x, y_2)`, never on either reward's absolute value. Since `Z(x)` depends only on the prompt `x`, not on which completion `y` is being scored, it is exactly the same additive term in `r(x, y_1)` and in `r(x, y_2)`. Substituting the inverted reward expression into a difference of two rewards for the same prompt makes every `β · log Z(x)` term cancel out completely. What is left is a preference probability expressed purely in terms of the policy `π_r` and the fixed reference policy `π_ref`, with no reward model, and no partition function, appearing anywhere in it.

### The implicit reward

This is exactly what Lesson 4's glossary term **implicit reward** names: the reward function `r(x, y) = β · log(π_r(y|x) / π_ref(y|x))` (the partition-function term can be dropped once only differences matter) that a policy mathematically defines, just by being the policy it is, relative to a reference. No separate reward model was ever trained to produce it; it falls directly out of the same optimal-policy relationship RLHF was already built on. Training a policy to satisfy human preference data directly, using this implicit reward in place of a separately trained one, is the entire idea DPO is named for.

## Practice

1. ▢ Why is the partition function `Z(x)` described as intractable to compute directly?

<details markdown="1"><summary>Check</summary>

Because computing it exactly requires summing over every possible completion `y` a language model could generate for a given prompt `x`, a sum over an enormous space that cannot be evaluated directly.

</details>

2. ▢ Why does `Z(x)` cancel out when computing the difference `r(x, y_1) - r(x, y_2)` for two completions to the same prompt, but would not cancel if the reward for a single completion were needed on its own?

<details markdown="1"><summary>Hint</summary>

Ask what `Z(x)` actually depends on, and whether that dependence differs between `y_1` and `y_2`.

</details>

<details markdown="1"><summary>Check</summary>

`Z(x)` depends only on the prompt `x`, not on which completion is being scored, so it appears as the exact same additive term (`β · log Z(x)`) in both `r(x, y_1)` and `r(x, y_2)`. Subtracting one from the other removes it entirely. A single reward on its own would still carry that same unremoved term.

</details>

3. ▢ What does "implicit reward" mean, in the specific sense this lesson derives it?

<details markdown="1"><summary>Check</summary>

The reward function `β · log(π(y|x) / π_ref(y|x))` that any policy mathematically defines, relative to a fixed reference policy, purely as a consequence of the same optimal-policy relationship RLHF's objective already implies. It is never trained as a separate model; it falls directly out of the policy and reference policy themselves.

</details>

4. ▢ Which of these best describes what DPO's derivation accomplishes, relative to needing to estimate `Z(x)` directly?

    - a) It finds a faster numerical method for approximating `Z(x)`
    - b) It restructures the problem so that `Z(x)` cancels out entirely whenever only a difference of two rewards is needed, avoiding the need to compute it at all
    - c) It replaces `Z(x)` with a second, simpler partition function
    - d) It shows that `Z(x)` is always equal to 1 for language models

<details markdown="1"><summary>Check</summary>

**b)** is exactly the derivation this lesson walks through. (a) and (c) both assume `Z(x)` still needs to be computed or approximated in some form, which the actual derivation avoids doing at all. (d) is not a claim the derivation makes or needs.

</details>

## Real-world reps

- [ ] Read the derivation section of the DPO paper (linked above), from the KL-constrained objective through the cancellation of the partition function, and write, in your own words, one sentence per equation naming what changed between it and the one before it.
- [ ] Write out, symbol by symbol, what `β · log(π(y|x) / π_ref(y|x))` would evaluate to if the policy and reference policy assigned the exact same probability to `y`. Confirm this matches your intuition for what "no preference signal from this completion" should look like.
- [ ] Tomorrow: without looking ahead, write a one-sentence prediction for Lesson 10: given that the implicit reward is defined purely from the policy and the reference model, with no reward model or partition function left in the picture, what training loop do you expect DPO to need, compared to PPO's sampling-and-optimization loop?

## Going further

- [Paper: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
