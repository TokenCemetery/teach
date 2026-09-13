---
title: 19. Choosing Between SFT, DPO, PPO, and GRPO
description: Each method earns its added cost over the one before it only when the cheaper one genuinely cannot express the target behavior
type: lesson
---

# Lesson 19. Choosing Between SFT, DPO, PPO, and GRPO

**Mission link:** "Given a team's data, budget, and target behavior, choose between SFT alone, DPO, RLHF-PPO, and GRPO, and defend the choice against the one rejected" is the mission's central decision, and this lesson is where the whole arc's cost accounting gets assembled into one framework.
**Primary source:** [Paper: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
**Prerequisites:** [Lesson 18](0018-reward-hacking-after-the-fact.md)

## Warm-up

1. ▢ What is over-refusal, and why can a red-team, unsafe-prompt-only benchmark not detect it?

<details markdown="1"><summary>Check</summary>

A model refusing a prompt that is actually safe. A red-team benchmark built only from unsafe prompts has no safe prompts in it to be wrongly refused, so it cannot surface this specific failure.

</details>

2. ▢ What is judge bias, and what does `llm/evals` recommend checking before trusting a score gap it produced?

<details markdown="1"><summary>Check</summary>

A systematic distortion in an LLM judge's scoring, such as favoring longer answers or whichever answer is shown first. `llm/evals` recommends checking the judge's calibration against these known biases before trusting a score gap as evidence of genuine improvement.

</details>

## Know this

### Each method costs more than the last, for a reason

This track's four training approaches form a rough ladder, each adding cost only where the previous one genuinely runs out of expressive power for the target behavior:

**SFT alone (Stage 2)** is cheapest: no preference data, no reward model, no RL loop, just imitating demonstrated examples directly. It is enough exactly when the target behavior can be fully specified by showing examples of it: a fixed response format, a narrow, well-defined skill, a style change. Every later method in this ladder still starts from an SFT model; the question this lesson is really asking is how much further past SFT a given behavior needs.

**DPO (Stage 5)** earns its added cost over SFT alone once the desired behavior cannot be fully specified by direct demonstration, but *can* be specified by comparing two candidate outputs, "this one over that one." Rafailov et al. build DPO specifically to reach a preference-trained model at close to SFT's own cost: no separate reward model, no value function, no RL sampling loop, just the policy and a frozen reference model (Lesson 10). If preference data is available or collectible and there is no specific reason to need a standalone, reusable reward model, DPO is the natural next reach past SFT, not RLHF-PPO.

**RLHF-PPO (Stage 4)** earns its substantially higher cost (Lesson 8's four-or-five-model setup) specifically when a standalone reward model is worth having on its own terms: reused to score outputs outside the policy that trained against it, inspected independently, or iterated on repeatedly as more comparisons come in on the current best policy, the way Lesson 1's original three-step pipeline describes. Choosing PPO over DPO without one of these reasons is paying for machinery a simpler method already covers.

**GRPO (Stage 6)** earns its place through a different door entirely: verifiable rewards. Where DPO and PPO both need preference judgments, human or AI, GRPO's group-relative advantage works with any per-output score, including a deterministic checker's output (Lesson 12), which removes the need for a trained reward model or human preference data at all on tasks like math and code where correctness is checkable. GRPO is not a cheaper PPO in general; it is the right tool specifically when the task supplies a verifiable reward PPO or DPO would otherwise have to approximate with a trained judgment.

### Defending a rejected alternative, not just a choice

"Defend the choice against the one rejected," the mission's own phrasing, means naming which cheaper method was tried or considered first and why it fell short, not simply asserting the chosen method's benefits. A team choosing PPO should be able to say why DPO's implicit reward was not enough, specifically (needing a reusable reward model, most often). A team choosing GRPO should be able to point at the verifiable check its reward is built from, not simply cite DeepSeek-R1's results as license to use it on a task with no such check available.

## Practice

1. ▢ A team wants a model that always responds in a fixed JSON schema for a narrow, well-defined task. Which method from this ladder is the right starting point, and why?

<details markdown="1"><summary>Check</summary>

SFT alone. This is exactly the case a fixed, fully demonstrable behavior fits: examples of the correct format are enough to imitate directly, with no need for preference data or a reward signal at all.

</details>

2. ▢ A team has preference data (pairs of outputs with one marked better) and no specific need to reuse a reward model outside the training run itself. Which of DPO and PPO is the more defensible default, and why?

<details markdown="1"><summary>Check</summary>

DPO. It reaches a similar preference-trained result at close to SFT's own cost, needing only the policy and a frozen reference model, with no separate reward model or RL loop to justify unless something specific requires one.

</details>

3. ▢ A team is training a model to solve competitive programming problems, where a compiler can check whether generated code passes a fixed test suite. Which method fits this task particularly well, and what specifically makes it a good fit?

<details markdown="1"><summary>Check</summary>

GRPO, paired with a verifiable reward: the compiler's pass/fail result on the test suite is exactly the kind of deterministic, checkable score GRPO's group-relative advantage can use directly, with no trained reward model or human preference data needed at all.

</details>

4. ▢ A team chooses RLHF-PPO over DPO, citing only "PPO is the more established method." Per this lesson, is this a sufficient defense of the choice?

<details markdown="1"><summary>Check</summary>

No. Defending a choice against the one rejected means naming a specific reason DPO's cheaper approach would not have sufficed, such as needing a standalone reward model to reuse or iterate on. Citing only that PPO is established does not identify what DPO specifically lacked for this task.

</details>

## Real-world reps

- [ ] Find a published post-training technical report and identify which of SFT, DPO, PPO, or GRPO it used, and whether it states a reason for that choice over a cheaper alternative.
- [ ] For a task you are familiar with (from work, a project, or a hypothetical), walk it through this lesson's ladder one step at a time: would SFT alone suffice, and if not, why not; would DPO suffice, and if not, why not.
- [ ] Tomorrow: without looking ahead, write a one-sentence prediction for Lesson 20: given that this track's arc has covered ten distinct decisions (data masking, reward design, KL tradeoffs, group-relative advantage, verifiable rewards, alignment-tax measurement), what would reviewing someone else's finished alignment recipe actually need to check, stage by stage?

## Going further

- [Paper: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
