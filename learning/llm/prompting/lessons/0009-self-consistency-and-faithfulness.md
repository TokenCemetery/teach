---
title: "9. Self-Consistency and Faithfulness"
description: Sampling several reasoning paths to vote on an answer, and why the written reasoning is not a faithful explanation
type: lesson
---

# Lesson 9. Self-Consistency and Faithfulness

**Mission link:** Two things follow from asking for reasoning: you can spend more tokens to get a steadier answer, and you must not read the reasoning as proof of why the model answered as it did.
**Primary source:** [Paper: "Self-Consistency Improves Chain of Thought Reasoning in Language Models", Wang et al., 2022](https://arxiv.org/abs/2203.11171)
**Prerequisites:** [Lesson 8](0008-chain-of-thought.md), [Self-consistency](../GLOSSARY.md), [Chain-of-thought](../GLOSSARY.md)

## Warm-up

1. ▢ Lesson 7 said a few-shot prompt can lean toward one answer depending on its examples and their order. Why does that make a single sampled answer less trustworthy than it looks?

<details markdown="1"><summary>Check</summary>

One answer is one draw from a distribution the prompt has already tilted. If the tilt decides the outcome on a borderline case, rerunning or reordering can flip it, so a lone answer carries no information about how fragile it is.

</details>

2. ▢ Lesson 8 said reasoning helps most on multi-step tasks. Name a task from your own work where it would help and one where it would not.

<details markdown="1"><summary>Check</summary>

Any pair that separates several dependent steps (a multi-part calculation, a schedule with constraints) from a one-step lookup or label (extract a date, tag the sentiment). The first earns reasoning tokens; the second only pays for them.

</details>

## Know this

### Self-consistency: sample, then vote

Greedy decoding takes one chain-of-thought and trusts it. Wang et al. instead sample a set of reasoning paths from the same prompt and keep the final answer that appears most often. The intuition they give is that a hard problem has many ways of thinking and one correct answer, so wrong paths tend to disagree with each other while right ones converge. They report gains over greedy chain-of-thought of +17.9% on GSM8K, +11.0% on SVAMP, +12.2% on AQuA, +6.4% on StrategyQA and +3.9% on ARC-challenge.

This is **self-consistency**. Three conditions follow from how it works:

- **There must be a final answer to compare.** The vote runs over answers drawn from a fixed set, such as a number or a choice, so it suits tasks with one checkable answer, not open-ended writing.
- **The samples must differ.** The paper's method works with sampling methods such as temperature sampling. Identical samples all vote the same way and add nothing.
- **It costs more.** The authors name extra computation as the limitation and suggest starting with 5 or 10 paths, since in most cases performance saturates quickly.

In a chat window you can approximate it by asking the same question in several fresh chats and taking the majority, assuming the interface samples with some randomness.

### Faithfulness: the reasoning is not the cause

It is tempting to read the written reasoning as the model's actual process. Turpin et al. tested that by adding a biasing feature to the prompt, such as reordering the few-shot examples so the correct answer is always "(A)", or suggesting an answer in the prompt, and checking whether the written reasoning mentioned it.

It did not. On 13 BIG-Bench Hard tasks with GPT-3.5 and Claude 1.0, the biasing features pushed accuracy down by as much as 36%, and the reasoning never referred to the feature. When the models were pushed toward a wrong answer, they often wrote reasoning that justified it. The authors call such explanations plausible yet misleading.

Two practical rules follow:

- **Do not use the written reasoning as an audit of why the answer was given.** It can be a fluent account that leaves out what drove the answer.
- **Test influence directly.** To learn whether something in the prompt affects the answer, change that thing and rerun, as in the papers, instead of asking the model to explain itself.

This does not make reasoning useless. Lesson 8's gains still hold. It means the reasoning helps the answer and is a weak witness about the cause.

## Practice

1. ▢ Predict, then run. Ask a chat model this question in three separate fresh chats and record the three final answers. Predict whether a majority emerges.

    ```text
    A bat and a ball cost 1.10 dollars together. The bat costs 1.00
    dollar more than the ball. How much does the ball cost?
    Think it through, then end with "Answer:" and the amount.
    ```

<details markdown="1"><summary>Hint</summary>

Self-consistency only helps if the paths differ and if the most common answer is the right one.

</details>

<details markdown="1"><summary>Check</summary>

The correct answer is 5 cents. If all three chats agree, the vote is unanimous and the extra samples only raised your confidence. If one disagrees, the majority is your answer, and the disagreement shows the question was not safe to answer from a single sample. A wrong majority is possible too, which is why the vote is a way to spend tokens on steadiness, not a guarantee. Try a harder multi-step question to see disagreement more often.

</details>

2. ▢ Why does self-consistency suit "what is 17 percent of 240" better than "write a product description"?

<details markdown="1"><summary>Check</summary>

The vote needs final answers that can be compared for equality. A number can be, so the most common one wins. A product description has no single answer: every sample is different, so there is nothing to vote on, only text to pick between.

</details>

3. ▢ Your app asks a model for a yes or no decision and shows its written reasoning to the user as the explanation. Using Turpin et al., state the risk and one change.

<details markdown="1"><summary>Check</summary>

The risk is that the reasoning can omit what actually drove the decision, or rationalise a decision shaped by something in the prompt such as example order or a suggested answer, so users would be shown a plausible account that may not be the cause. One change: stop presenting the written reasoning as the cause, and label it as the model's rationale, or test directly by rerunning with the suspect input changed. Which fix is right depends on what users rely on the explanation for.

</details>

4. ▢ Which pair correctly describes what each technique gives you?

    - a) Self-consistency adds a steadier answer; faithfulness checks do not apply
    - b) Self-consistency adds a steadier answer; reasoning may omit the true cause
    - c) Self-consistency explains the answer; reasoning always names its true cause
    - d) Self-consistency cuts cost by sampling once; reasoning may omit the cause

<details markdown="1"><summary>Check</summary>

**b)** Voting across sampled paths steadies the final answer, and Turpin et al. show the written reasoning can leave out what drove it. (a) is wrong because faithfulness applies to any reasoning you show. (c) is wrong twice: voting does not explain, and reasoning does not always name its cause. (d) is wrong because self-consistency costs more samples, not fewer.

</details>

## Real-world reps

- [ ] Take a question you care about that has one checkable answer. Ask it in three fresh chats, and note whether the answers agree.
- [ ] Find one place where you read a model's reasoning as the reason for its answer, and write down what you would test to check it.
- [ ] Tomorrow: take a multiple-choice prompt and reorder its options so the right one moves, then see whether the model's reasoning mentions the change.

## Going further

- [Few-Shot and Reasoning](../reference/few-shot-and-reasoning.md)
- [Paper: "Language Models Don't Always Say What They Think", Turpin et al., 2023](https://arxiv.org/abs/2305.04388)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
