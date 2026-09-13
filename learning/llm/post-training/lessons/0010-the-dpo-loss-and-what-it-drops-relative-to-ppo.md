---
title: 10. The DPO Loss, and What It Drops Relative to PPO
description: One loss, two models, no sampling loop, and the same beta a KL penalty would have used
type: lesson
---

# Lesson 10. The DPO Loss, and What It Drops Relative to PPO

**Mission link:** "Derive DPO's implicit reward from the same preference data RLHF uses, and say what it gives up by removing the RL loop" is the fourth bullet under Success looks like. Lesson 9 covered the derivation; this lesson covers the resulting loss and states plainly what it drops relative to PPO.
**Primary source:** [Paper: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
**Prerequisites:** [Lesson 9](0009-dpos-implicit-reward-why-the-partition-function-cancels.md)

## Warm-up

1. ▢ Why does the partition function `Z(x)` cancel out when computing a difference of two rewards for the same prompt?

<details markdown="1"><summary>Check</summary>

`Z(x)` depends only on the prompt, not on which completion is being scored, so it is the exact same additive term in both rewards being subtracted, and it cancels out of the difference entirely.

</details>

2. ▢ What does "implicit reward" mean, in the sense Lesson 9 derives it?

<details markdown="1"><summary>Check</summary>

The reward function a policy mathematically defines, relative to a fixed reference policy, purely as a consequence of the optimal-policy relationship RLHF's objective already implies, without ever training a separate reward model.

</details>

## Know this

### Substituting the implicit reward into the Bradley-Terry loss

Lesson 4's Bradley-Terry loss trained a separate reward model to make a preferred completion's score exceed a rejected one's. DPO uses that exact same idea, with one substitution: everywhere the Bradley-Terry loss would use a trained reward model's output, DPO substitutes Lesson 9's implicit reward, `β · log(π(y|x) / π_ref(y|x))`, computed directly from the policy being trained and the frozen reference model. The resulting loss, exactly as Rafailov et al. give it, compares the preferred completion `y_w` and rejected completion `y_l` for the same prompt:

```text
loss = -log( sigmoid( β · [ (log π(y_w|x) - log π_ref(y_w|x)) - (log π(y_l|x) - log π_ref(y_l|x)) ] ) )
```

This is the Bradley-Terry loss from Lesson 4, with the reward model's two scores replaced by the implicit reward's two values, one for the preferred completion and one for the rejected one. Nothing about the loss's shape changed; what changed is what is standing in for a reward.

### What this loss needs, and what it no longer needs

Computing this loss requires exactly two models: the policy being trained, and a frozen copy of the reference model (ordinarily the SFT model), each evaluated on the same preferred and rejected completions to get four log-probabilities total. Contrast this against Stage 4's PPO setup (Lesson 8): no separate reward model is trained at all, since the implicit reward is computed directly from the policy and reference model. No value function is needed, since there is no advantage to estimate; DPO is not doing reinforcement learning in the sense of sampling actions and estimating returns. There is no PPO clipping (Lesson 7) either, since there is no policy-gradient update whose step size needs bounding; this loss is optimized directly, the same way any ordinary supervised loss is, with one gradient step per batch of preference pairs, no sampling loop between steps at all.

### The same beta, doing the same job

The `β` in DPO's loss is not a new hyperparameter invented for this method; it is the same KL-penalty strength from Lesson 6's RLHF objective, now baked directly into the implicit reward rather than appearing as a separate penalty term added on top of a reward model's score. A larger `β` still means staying closer to the reference model; a smaller `β` still means being freer to move away from it, exactly Lesson 6's tradeoff, just expressed inside a single loss instead of two separate terms.

### What is actually given up

DPO does not remove the tradeoffs PPO's KL penalty was managing; it removes the machinery. Rafailov et al.'s method is a mathematically exact reformulation of the same optimal-policy relationship RLHF already relies on, not an approximation of it, so nothing about the underlying preference-satisfaction goal is weakened. What is genuinely given up is a standalone reward model and the flexibility that comes with training one separately: a reward model can, in principle, be reused to score outputs it never directly trained the policy on, be inspected on its own, or be combined with additional signals beyond the original preference data. DPO's implicit reward exists only bound to a specific policy and reference model pair; there is no free-standing scoring function left over once training finishes, only the trained policy itself.

## Practice

1. ▢ A DPO loss computation for one preference pair needs four log-probabilities. Name what each of the four is a log-probability of.

<details markdown="1"><summary>Check</summary>

The policy's log-probability of the preferred completion, the reference model's log-probability of the preferred completion, the policy's log-probability of the rejected completion, and the reference model's log-probability of the rejected completion.

</details>

2. ▢ Which of PPO's components (reward model, value function, KL penalty, clipped update) does DPO's loss have no need for at all?

    - a) Only the clipped update
    - b) The reward model and the value function; the KL-penalty tradeoff is still present, just baked into the implicit reward rather than a separate term
    - c) All four, since DPO does not use a KL penalty of any kind
    - d) Only the reward model; DPO still trains a separate value function

<details markdown="1"><summary>Check</summary>

**b)** is the accurate account: DPO needs no separate reward model or value function, and has no per-step clipped update since there is no RL sampling loop, but the same beta-controlled tradeoff Lesson 6 described is still present, folded directly into the implicit reward term. (a), (c), and (d) each misstate which pieces survive.

</details>

3. ▢ A team wants to reuse their trained reward model to score a batch of completions that were never part of any policy's training run, purely for monitoring purposes. Could a team using DPO instead of PPO do the same thing with equivalent ease?

<details markdown="1"><summary>Check</summary>

Not as directly. DPO never produces a free-standing reward model; its implicit reward is defined only in terms of a specific trained policy and its reference model. Scoring arbitrary completions this way is exactly the kind of reuse a standalone reward model supports and DPO's approach does not produce as a byproduct.

</details>

4. ▢ Does `β` mean something different in DPO's loss than it did in Lesson 6's RLHF objective?

<details markdown="1"><summary>Check</summary>

No. It is the same KL-penalty strength, controlling the same tradeoff between staying close to the reference model and moving toward what the preference data rewards; DPO simply folds it directly into the implicit reward term rather than keeping it as a visually separate penalty added to a reward model's score.

</details>

## Real-world reps

- [ ] Find a DPO implementation in a library you have access to (Hugging Face's TRL is a common one) and confirm it computes the same four log-probabilities this lesson names, per preference pair.
- [ ] Using a small hypothetical example (make up plausible log-probability values for a preferred and a rejected completion under a policy and a reference model), compute the DPO loss by hand for two different values of `β`, and describe how the loss changes as `β` grows.
- [ ] Tomorrow: for a project where you might want to align a model, decide whether you would reach for PPO or DPO first, and write one sentence naming which of this lesson's tradeoffs (engineering cost, standalone reward-model reuse, RL infrastructure) drove your answer.

## Going further

- [Paper: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
- [Documentation: "TRL - Transformer Reinforcement Learning", Hugging Face](https://huggingface.co/docs/trl/index)
- [Resources](../RESOURCES.md)

---

Stage 5 covered a way to reach a similar result as RLHF without a separate reward model or an RL loop. Stage 6 covers a different departure from PPO: keeping the RL loop, but for tasks where the reward is not a matter of human preference at all, but something checkable outright.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
