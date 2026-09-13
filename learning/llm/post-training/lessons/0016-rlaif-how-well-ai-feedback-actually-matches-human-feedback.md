---
title: 16. RLAIF: How Well AI Feedback Actually Matches Human Feedback
description: A model judging its own outputs, at its own size, still beat plain supervised fine-tuning
type: lesson
---

# Lesson 16. RLAIF: How Well AI Feedback Actually Matches Human Feedback

**Mission link:** "Can say where feedback came from (human or AI) in a given safety-tuning pipeline and what that trades" is the Success looks like bullet this stage serves. Lesson 15 covered one method built on AI feedback; this lesson covers the direct, controlled comparison of AI feedback against human feedback across several tasks.
**Primary source:** [Paper: "RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback", Lee et al., 2023](https://arxiv.org/abs/2309.00267)
**Prerequisites:** [Lesson 15](0015-constitutional-ai-feedback-from-a-model-not-a-human.md)

## Warm-up

1. ▢ In RL-CAI, what replaces the human labeler that would ordinarily judge which of two sampled responses is better?

<details markdown="1"><summary>Check</summary>

A model. An AI system judges which response is better, and a preference model is trained on this dataset of AI-generated preferences.

</details>

2. ▢ Per Bai et al.'s own comparison, how did crowdworkers rate RL-CAI against a model trained on previously collected human harmfulness labels?

<details markdown="1"><summary>Check</summary>

They preferred RL-CAI over the model trained on human-labeled comparisons.

</details>

## Know this

### A controlled, head-to-head comparison

Lee et al. run a direct comparison Constitutional AI's own results only hinted at: across three separate tasks, summarization, helpful dialogue generation, and harmless dialogue generation, they train one policy with ordinary RLHF and a second with **RLAIF**, an off-the-shelf language model producing the preference labels instead of a human, holding everything else about the setup comparable. Human evaluators then judge the results.

### The result: comparable on two tasks, better on the third

For summarization and helpful dialogue generation, both RLAIF and RLHF are strongly preferred over a plain SFT baseline (winning against it 63% and 64% of the time respectively), and a direct head-to-head comparison between RLAIF and RLHF shows the two equally preferred, with no statistically significant difference between them. For harmless dialogue generation, Lee et al. report that RLAIF actually **outperforms** RLHF, rated by human evaluators as more harmless. Across all three tasks, replacing a human-labeled preference dataset with an AI-labeled one did not produce a worse result; on two tasks it matched RLHF, and on the third it beat it.

### The more surprising result: a model judging its own size, or itself

Lee et al. push further, toward what they call "self-improvement": RLAIF still outperformed the plain SFT baseline even when the AI labeler generating preferences was the same size as the policy being trained, or in the most extreme case, the exact same checkpoint the policy started from. A model can be made to improve using preference judgments produced by a model no more capable than the one being trained, including judgments produced by an earlier copy of itself.

### Skipping the reward model entirely: direct-RLAIF

Lee et al. introduce one further simplification: **direct-RLAIF (d-RLAIF)**, which skips training a separate preference model altogether and instead queries an off-the-shelf language model for a reward score directly, during RL training itself. Removing an entire trained model from the pipeline, the reward model that Lesson 8 already flagged as a real cost driver in ordinary RLHF, did not hurt performance in their results; they report d-RLAIF achieves better performance than canonical RLAIF, not merely comparable performance at lower cost.

### What this argues for, taken together with Lesson 15

Between Constitutional AI's result (an AI-feedback pipeline preferred over a human-feedback one) and Lee et al.'s controlled comparison (AI feedback matching or beating human feedback across three separate tasks, holding up even at reduced labeler scale, and tolerating the removal of a whole reward model), the case that "AI feedback" is a lesser, fallback substitute for human feedback does not hold up well against either result. Lee et al. state their own conclusion directly: RLAIF offers a potential solution to the scalability limitations of collecting human feedback, not merely a cheaper approximation of it.

## Practice

1. ▢ Across summarization and helpful dialogue generation, how did RLAIF's win rate against a plain SFT baseline compare to RLHF's, per Lee et al.?

<details markdown="1"><summary>Check</summary>

Not statistically significantly different: both won against the SFT baseline at similar rates (63% and 64%), and a direct head-to-head between RLAIF and RLHF showed no significant preference for either.

</details>

2. ▢ For which of the three tasks Lee et al. tested did RLAIF outperform RLHF, rather than merely match it?

<details markdown="1"><summary>Check</summary>

Harmless dialogue generation. Human evaluators rated RLAIF's responses as more harmless than RLHF's on this task specifically.

</details>

3. ▢ What is surprising about RLAIF still outperforming an SFT baseline even when the AI labeler is the exact same checkpoint as the policy being trained?

<details markdown="1"><summary>Check</summary>

It means a model's own preference judgments about outputs, from a model no more capable than the one being improved, can still produce a genuine improvement over plain supervised fine-tuning, rather than needing feedback from something more capable or from a human.

</details>

4. ▢ What does direct-RLAIF (d-RLAIF) remove from the standard RLAIF pipeline, and what did Lee et al. find about its performance?

    - a) It removes the policy model itself; it found worse performance
    - b) It removes the separate trained preference/reward model, querying an off-the-shelf LLM for a reward score directly during RL; it found better performance than canonical RLAIF
    - c) It removes the RL stage entirely, leaving only SFT; performance was unchanged
    - d) It removes the need for any language model at all, using a purely rule-based reward instead

<details markdown="1"><summary>Check</summary>

**b)** is exactly what Lee et al. describe and report. (a), (c), and (d) each describe a different, unrelated change to the pipeline.

</details>

## Real-world reps

- [ ] Find where a training framework or research pipeline you have access to exposes an AI-feedback or LLM-as-judge preference-labeling option, and check whether it more closely resembles canonical RLAIF (a trained preference model) or direct-RLAIF (a reward queried live from an LLM).
- [ ] Read the passage in Lee et al.'s paper (linked above) describing the "self-improvement" result and write, in one sentence, why this result is more surprising than RLAIF simply matching RLHF using a larger, more capable AI labeler.
- [ ] Tomorrow: for a task you might want to align a model on, decide whether you would reach for RLHF, RLAIF, or direct-RLAIF first, and write one sentence naming which of this lesson's results (comparable quality, self-improvement at matched scale, or lower pipeline cost) drove your answer.

## Going further

- [Paper: "RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback", Lee et al., 2023](https://arxiv.org/abs/2309.00267)
- [Paper: "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
- [Resources](../RESOURCES.md)

---

Stage 8 covered feedback that comes from a model rather than a human, and how well it actually holds up. Stage 9 turns to a harder question sitting underneath everything this track has covered: once a model is aligned, how do you tell whether the number measuring that alignment is measuring the real thing.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
