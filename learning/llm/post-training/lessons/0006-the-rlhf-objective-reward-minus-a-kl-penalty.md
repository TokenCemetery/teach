---
title: 6. The RLHF Objective: Reward Minus a KL Penalty
description: One term chases the reward model's score; a second term is the leash that keeps the policy from running off with it
type: lesson
---

# Lesson 6. The RLHF Objective: Reward Minus a KL Penalty

**Mission link:** "Derive the RLHF objective (reward minus a KL penalty against a reference model) and say what happens to the policy as the KL penalty is loosened" is the third bullet under Success looks like. This lesson covers the objective itself; Lesson 7 covers PPO, the algorithm used to optimize it, and Lesson 8 covers what all of this costs to run.
**Primary source:** [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Prerequisites:** [Lesson 5](0005-reward-hacking.md)

## Warm-up

1. ▢ What did Bai et al.'s policies converge on when over-optimized for harmlessness, and why was that behavior a cheap way to score well?

<details markdown="1"><summary>Check</summary>

Blanket deflection: recommending users seek therapy or professional help at almost any remotely sensitive question. It required very little sophistication, essentially only classifying a request as sensitive and refusing, which is much easier than being genuinely nuanced, helpful, and harmless.

</details>

2. ▢ What did Bai et al.'s train-PM-versus-test-PM divergence indicate when it appeared?

<details markdown="1"><summary>Check</summary>

That the policy was likely over-optimized specifically against the train PM, exploiting behavior it rewards that a held-out reward model, never trained to expect this exact policy, does not reward as highly.

</details>

## Know this

### The full objective

Ouyang et al. state the exact objective their PPO training maximizes:

```text
objective(φ) = E[(x,y) ~ policy] [ r(x, y) − β · log( policy(y|x) / SFT(y|x) ) ]
             + γ · E[x ~ pretraining data] [ log( policy(x) ) ]
```

Three pieces are doing three different jobs here, and it is worth taking them one at a time.

### The reward term

`r(x, y)` is the trained reward model's scalar score (Lesson 4) for the policy's own output `y` to prompt `x`. Maximizing this term alone is what pushes the policy toward outputs the reward model scores highly, exactly the goal reward modeling exists to serve.

### The KL penalty term

`β · log( policy(y|x) / SFT(y|x) )` compares the trained policy's probability of producing `y` against the original SFT model's probability of producing the same `y`, and subtracts a penalty proportional to how much larger the policy's own probability has become. Ouyang et al. describe this directly as a **per-token KL penalty from the SFT model**, added specifically **to mitigate over-optimization of the reward model**, the exact failure Lesson 5 described. The reward term alone gives the policy every incentive to drift as far as it needs to in order to maximize `r(x, y)`; the KL term is what makes drifting away from the SFT distribution cost something, rather than being free.

### What happens as β is loosened or tightened

`β` is a dial, and both directions have a real cost:

- As `β` shrinks toward zero, the penalty for diverging from the SFT policy nearly vanishes, and the objective reduces to chasing the reward model's score with almost nothing holding the policy back. This is precisely the unconstrained optimization Lesson 5's train-PM-versus-test-PM divergence is evidence of: the less the KL penalty restrains the policy, the more room it has to exploit whatever the reward model happens to reward, rather than what its designers actually wanted.
- As `β` grows large, the penalty for moving away from the SFT policy dominates the objective, and the trained policy is pulled back toward reproducing the SFT model almost exactly. Taken far enough, this defeats the purpose of the RL stage at all: if the policy cannot move meaningfully away from what SFT already produced, RLHF has nothing left to add on top of it.

Choosing `β` is choosing a point on this tradeoff, not eliminating it: a smaller `β` risks the reward hacking Lesson 5 described; a larger `β` risks RLHF adding little beyond what SFT alone already achieved.

### The pretraining-gradient term, and its connection to Lesson 1

The final term, `γ · E[log(policy(x))]`, is separate from the reward-versus-KL tradeoff entirely: it mixes in an ordinary language-modeling objective over the original pretraining distribution, increasing the policy's likelihood of the kind of text it was pretrained on. Ouyang et al. set `γ = 0` for what they call plain "PPO" models, and use a nonzero `γ` for what they call "PPO-ptx" models. This term is the actual mechanism behind Lesson 1's alignment tax mitigation: mixing pretraining-data gradients back into PPO training is what recovered much of the performance regression on public NLP benchmarks that pure PPO training introduced, without giving up the preference gains RLHF was built to produce.

## Practice

1. ▢ A team sets `β` to a very small value in the RLHF objective. What does this most directly put the policy at risk of, and why?

<details markdown="1"><summary>Check</summary>

Reward hacking: with the KL penalty nearly gone, the reward term dominates the objective almost unopposed, giving the policy little reason not to drift toward whatever the reward model happens to score highly, whether or not that behavior is what the reward model was actually meant to represent.

</details>

2. ▢ A team sets `β` to a very large value instead. What is the most likely cost of this choice?

<details markdown="1"><summary>Check</summary>

The policy is pulled back toward closely reproducing the SFT model, since any meaningful deviation is penalized heavily; taken far enough, this leaves little room for RLHF to add any behavior beyond what SFT alone already produced.

</details>

3. ▢ What is the difference between what Ouyang et al. call "PPO" and "PPO-ptx," and which term in the objective distinguishes them?

<details markdown="1"><summary>Check</summary>

"PPO" sets the pretraining-gradient coefficient `γ` to 0; "PPO-ptx" uses a nonzero `γ`, mixing pretraining-data log-likelihood gradients into the PPO updates. This is the term responsible for reducing the alignment tax Lesson 1 introduced.

</details>

4. ▢ Which of these best describes the role the reward term and the KL penalty term each play in the objective?

    - a) The reward term pulls the policy toward what the reward model scores highly; the KL penalty pulls it back toward the SFT model, and the objective balances the two
    - b) Both terms pull the policy in the same direction, toward the reward model's preferences
    - c) The KL penalty is only used during evaluation, not during training
    - d) The reward term and the KL penalty term are mathematically identical, just scaled differently

<details markdown="1"><summary>Check</summary>

**a)** is the actual relationship: two terms genuinely pulling in different directions, with `β` setting the balance between them. (b), (c), and (d) misdescribe the objective's structure in ways this lesson's derivation rules out directly.

</details>

## Real-world reps

- [ ] Find where a training framework you have access to exposes a KL-penalty coefficient for RLHF (often named something like `beta` or `kl_coef`), and note its default value and any documented guidance on tuning it.
- [ ] Read the paragraph in the InstructGPT paper (linked above) describing the full objective and write, in one sentence each, what happens to training if `β` and `γ` are both set to zero simultaneously.
- [ ] Tomorrow: without looking ahead, write a one-sentence prediction for Lesson 7: given that this objective needs to be maximized by adjusting the policy's own parameters, and that a single update based on one batch of sampled outputs could push the policy very far in one step, what problem might a naive optimization of this objective run into?

## Going further

- [Paper: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
