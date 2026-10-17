---
title: 24. When the Usual Advice Is Wrong
description: Recognise when standard prompting advice fails for a given model or task, and settle the dispute from the primary source
type: lesson
---

# Lesson 24. When the Usual Advice Is Wrong

**Mission link:** The track ends with trusting you to make the call on a prompt and to explain it to someone else. Prompting advice spreads as slogans, and a slogan is true for some models, tasks and dates and false for others. This lesson is the method for finding out which.
**Primary source:** [Paper: "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models", Zheng et al., 2023](https://arxiv.org/abs/2311.10054)
**Prerequisites:** [Lesson 2](0002-system-prompts-and-roles.md), [Lesson 7](0007-few-shot-biases.md), [Lesson 10](0010-prompting-reasoning-models.md), [Lesson 18](0018-a-regression-set-for-a-prompt.md), [Lesson 23](0023-reviewing-a-production-prompt.md)

## Warm-up

1. ▢ Why does a prompt for a reasoning model give goals and constraints rather than scripted steps?

<details markdown="1"><summary>Check</summary>

The model already produces its own reasoning phase, so a hand-written plan can constrain it to a worse path than it would find itself. Say what the answer must satisfy and let it decide how to get there.

</details>

2. ▢ What do few-shot examples mostly teach, according to lesson 6?

<details markdown="1"><summary>Check</summary>

The format, the label space and the input distribution, more than the correctness of each label. That is why choosing them for coverage and order matters more than polishing each one.

</details>

3. ▢ What goes in a regression set, and what is it for in a dispute about a prompt?

<details markdown="1"><summary>Check</summary>

Inputs built mostly from real failures, each with a check on the output. In a dispute it is the neutral ground: two people arguing from different papers can both run their preferred prompt on it and compare.

</details>

## Know this

### The method

A slogan such as "give the model a role" or "always add a step-by-step instruction" arrives without its conditions. The method for deciding whether it holds for you has four steps:

1. **Find the primary source.** Not the blog post that cites it. The paper or the vendor documentation, read for what was actually measured.
2. **Check the model and the date.** Which models, which task, which year. Advice from 2022 about one model family may not describe the model you call today, and a vendor's guide describes that vendor's models.
3. **Check what the claim covers.** Accuracy on factual questions is not tone. A result on short classification is not a result on drafting.
4. **Test on your regression set.** If the source and your case could differ, the result that settles it is yours (lessons 18 and 19).

The cases below each apply this. None of them says the usual advice is always wrong. Each says what the primary source supports.

### Case 1: "Give the model a role"

Anthropic's guide says: "Setting a role in the system prompt focuses Claude's behavior and tone for your use case" ([Anthropic: prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)). Zheng et al. tested whether personas help on objective tasks. They curated 162 roles across 6 types of interpersonal relationship and 8 domains of expertise and tested 4 families of LLMs on 2,410 factual questions. Their finding: adding a persona "does not improve model performance across a range of questions compared to the control setting where no persona is added". Gender, type and domain of the persona can still change the accuracy, so the effect "can be largely random", and automatically picking the best persona for a question was "often no better than random selection".

The two do not contradict, because they claim different things: tone and behaviour against accuracy on factual questions. The reading that survives both: keep a role where you want a voice or a scope, do not expect it to make facts more accurate, and when someone says a persona "improves accuracy", ask for the test. The paper's models are those of 2023, so the dated part of the answer is "for those models and questions".

### Case 2: "Think step by step"

The phrase comes from the zero-shot reasoning result (Kojima et al., 2022, listed in [Resources](../RESOURCES.md)), which predates models with built-in thinking. For a model that thinks before answering, the current Anthropic guide recommends the opposite habit: "A prompt like 'think thoroughly' often produces better reasoning than a hand-written step-by-step plan", and for several named models it says to rely on built-in thinking, because a prompt asking the model to write out its reasoning "may be declined". It keeps manual chain-of-thought as a fallback only for when thinking is off. Lesson 10 covers the mechanics.

The dispute to settle is therefore "which model, with thinking on or off". The answer comes from the model's own documentation, dated, and then your regression set.

### Case 3: "Shout the important rules"

Emphasis in capitals is a common way to stress a rule. Anthropic's guide says the later models are "more responsive to the system prompt than previous models", and that prompts written to reduce undertriggering "may now overtrigger". Its fix: "dial back any aggressive language", so where you might have written "CRITICAL: You MUST use this tool when...", use "Use this tool when...". The guide names Claude Opus 4.5 and Claude Opus 4.6 for this, and the example is about tool use.

Read the scope. The claim is about two named models and about triggering tools, not "capitals never work". A prompt written for an older model and moved to a newer one is the case where inherited emphasis is worth testing, with the plain version as the comparison. Lesson 23 lists emphatic wording as a cost to question for the same reason.

### Case 4: "More examples are better"

Anthropic's guide recommends including 3 to 5 examples and making them relevant, diverse and structured. Two papers add what a count cannot say. Lu et al. show that "the order in which the samples are provided can make the difference between near state-of-the-art and random guess performance", that this holds "across model sizes", and that a good permutation for one model is not transferable to another. Sclar et al. find that formatting sensitivity "remains even when increasing... the number of few-shot examples".

So the count is not the lever the slogan implies. The same examples in another order, or in a different format, can matter as much as adding more, and an ordering tuned on one model does not carry to the next. Treat order and format as variables to test, which is lesson 7's conclusion made stronger.

### Settling it in a conversation

Two engineers cite the same paper. Do not pick the more confident one, and do not split the difference. Ask for four things: the passage, the models and date, what was measured, and a run on the regression set. If the claim and your case match, the source applies. If they do not, the source is not evidence about your case, and the run is.

## Practice

1. ▢ A colleague says "Zheng et al. proved roles are useless, so delete the role line from every system prompt." What does the paper support, and what would you do?

<details markdown="1"><summary>Check</summary>

The paper reports that adding a persona did not improve performance on 2,410 factual questions across 4 families of LLMs, compared with no persona. It does not measure tone or scope, and it reports that the effect varies by persona, not that it is zero for every case. So "useless for factual accuracy on those models" is supported, and "delete everywhere" is not. Run the prompt with and without the role on the regression set and delete the line only where the numbers show nothing, since removing it also saves tokens.

</details>

2. ▢ You inherit a prompt that says "CRITICAL: you MUST call the search tool before every answer", tuned on an older model, and the newer model now searches for trivial questions. Which action follows the source?

    - a) Test a plain "Use the search tool when" version against the old wording
    - b) Add a second capitalised rule telling it not to search for trivia
    - c) Switch back to the older model and keep the wording the same
    - d) Remove the instruction and expect the newer model to infer the policy

<details markdown="1"><summary>Check</summary>

a). Anthropic's guide describes this overtriggering for named newer models and advises dialling back aggressive language, so the plain wording is the candidate, and the regression set decides. b) piles emphasis on emphasis. c) throws away the newer model. d) removes policy you may need, and untested.

</details>

3. ▢ A blog post says "add 'think step by step' to every prompt." You use a model with built-in thinking switched on. Give the first two checks you run before touching the prompt.

<details markdown="1"><summary>Check</summary>

First, find the original result and see which models and year it covers: the zero-shot reasoning paper is from 2022, before models with built-in thinking. Second, read the documentation for your model: Anthropic's guide recommends general instructions over prescribed steps with thinking on, and says that asking for written-out reasoning may be declined on some named models. Then test with and without the phrase on the regression set, because the guide is one vendor's account of its own models.

</details>

4. ▢ Your prompt has five examples with the rare label last, and accuracy changes when you shuffle them. Which source predicted this, and what does it change about the advice to use 3 to 5 examples?

<details markdown="1"><summary>Check</summary>

Lu et al. show example order alone can move results between near state of the art and near chance, and that a good order for one model is not transferable to another. The count advice stays a starting point, but it is not enough: the order and the format are part of the prompt's behaviour, so record the order that passed and re-test it when the model snapshot changes (lesson 16).

</details>

5. ▢ Write the three questions you would ask before accepting "personas improve accuracy" in a design review, and the single result that would settle it for your product.

<details markdown="1"><summary>Check</summary>

Which models and which questions was it measured on? Was the baseline a prompt with no persona? Was the measure accuracy or tone? What settles it for your product is a paired comparison on your regression set of the prompt with and without the persona, with the difference judged against run-to-run noise (lesson 19). A source that matches none of your conditions is background, not evidence.

</details>

## Real-world reps

- [ ] Pick one piece of prompting advice you follow without knowing its source and trace it to a paper or a vendor document. Write down the models, the date and what was measured.
- [ ] Take one persona or emphatic instruction in a prompt you maintain and write the two-prompt comparison that would test it, even if you do not run it yet.
- [ ] Tomorrow: Run that comparison on a regression set, or sketch five cases for one, and record the result in the prompt's change notes.

## Going further

- [Prompt Review Checklist](../reference/prompt-review-checklist.md)
- [Paper: "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models", Zheng et al., 2023](https://arxiv.org/abs/2311.10054)
- [Docs: "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Paper: "Fantastically Ordered Prompts and Where to Find Them", Lu et al., 2021](https://arxiv.org/abs/2104.08786)
- [Resources](../RESOURCES.md)

---

This is the end of the track, and the habit it was built for is the one in this lesson: a prompt is a claim about a model, so find where the claim comes from, check what it covered, and test it on your own cases before you defend it to anyone else.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
