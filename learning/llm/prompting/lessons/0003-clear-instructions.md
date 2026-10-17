---
title: "3. Clear Instructions"
description: "Write an instruction a capable newcomer could follow: context, the task, the constraints, and what done looks like"
type: lesson
---

# Lesson 3. Clear Instructions

**Mission link:** Most prompts that fail are not tricked or confused models but under-specified requests, so the cheapest improvement to any prompt is to say what a capable stranger would need to know.
**Primary source:** [Docs: "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#be-clear-and-direct)
**Prerequisites:** [Lesson 2](0002-system-prompts-and-roles.md), [Zero-shot prompt](../GLOSSARY.md)

## Warm-up

1. ▢ A line says "Reply in at most three sentences." Does it belong in the system prompt or the user turn, and why?

<details markdown="1"><summary>Check</summary>

The system prompt, because it should hold on every request, not only this one.

</details>

2. ▢ The rendered prompt for a chat ends with the assistant's role marker. What does the model do from there?

<details markdown="1"><summary>Check</summary>

It continues the token sequence from that point, which is how it writes the reply.

</details>

## Know this

### The colleague test

Anthropic's guide asks you to think of the model as a brilliant but new employee who lacks context on your norms and workflows. Its golden rule: show your prompt to a colleague with minimal context on the task and ask them to follow it. If they would be confused, the model will be too.

The model cannot ask what you meant, so anything you leave out it fills in with a guess. The guide also says that if you want "above and beyond" behaviour, you should request it explicitly rather than rely on the model to infer it from a vague prompt.

### Four parts of a clear instruction

| Part | Answers | Example |
|---|---|---|
| Context | Who is this for, and why does it matter? | "These summaries go to busy support managers who read on their phones." |
| Task | What exactly should be done? | "Summarise the ticket below." |
| Constraints | What limits apply? | "At most 40 words. No customer names." |
| Done looks like | How will you know it worked? | "A manager can decide whether to open the ticket from the summary alone." |

Anthropic's guide says that giving the motivation behind an instruction, such as why a behaviour matters, can help the model deliver more targeted responses. Google's prompt design guidance likewise lists constraints and response format as things to specify. "Done looks like" is the part most often missing, and it is also the part you will need later when you test a prompt change against a regression set.

### Say what to do, and number steps that must happen in order

Anthropic's guide recommends telling the model what to do instead of what not to do: instead of "Do not use markdown", write "Your response should be composed of smoothly flowing prose paragraphs." It also suggests sequential numbered steps when the order or completeness of steps matters.

### A before and after

```text
Summarise this ticket.
```

```text
You are helping a support team triage tickets. The summaries are read by managers on their phones, who decide from the summary alone whether to open the ticket.
Summarise the ticket below in at most 40 words, in plain prose, leaving out customer names. State the problem first and the customer's requested outcome last.
```

The second prompt is longer because it carries context, constraints and a purpose. Its added length is information, not decoration.

## Practice

1. ▢ Name the four parts of a clear instruction from this lesson, and for the prompt "Write a product description." say which are missing.

<details markdown="1"><summary>Check</summary>

Context, task, constraints, and what done looks like. The prompt has only a task, and a vague one. Missing: who the description is for and where it appears, its length and tone limits, and the standard it has to meet.

</details>

2. ▢ Rewrite "Don't write long answers." so it tells the model what to do instead.

<details markdown="1"><summary>Check</summary>

For example: "Answer in two or three sentences." It names the desired behaviour and gives a measurable limit, which also makes it checkable. A negative instruction says what to avoid but leaves the model to guess the alternative.

</details>

3. ▢ Which rewrite of "Make this email better" is clearest?

    - a) Improve this email so that it reads more professionally, clearly and persuasively overall
    - b) Rewrite this email for an upset customer in under 120 words, apologising first
    - c) Fix any problems in this email and make it sound good to the reader
    - d) Edit this email as an expert writer would, with attention to quality

<details markdown="1"><summary>Check</summary>

**b)** It names the audience, a length limit and an ordering requirement, so someone else could check the result. (a), (c) and (d) restate "better" in other words without saying what better means.

</details>

4. ▢ Predict, then run. Pick a task you do often, such as "Write a short bio." Write the prompt in five words and send it. Predict three things the reply will get wrong for your purpose, then rewrite the prompt with all four parts and send it again. Which of your three predictions were fixed, and which problems appeared that you did not predict?

<details markdown="1"><summary>Hint</summary>

Hand the five-word prompt to a coworker first. Whatever they would ask you is what the model is guessing.

</details>

<details markdown="1"><summary>Check</summary>

Typical results: the first reply guesses the audience, length and tone. The second removes those guesses but may add a new problem, often a constraint that conflicts with another. Keep both replies: the difference between them is the first comparison you can show someone, and lesson 18 turns that habit into a regression set.

</details>

## Real-world reps

- [ ] Take one prompt you sent this week that gave a disappointing reply and mark which of context, task, constraints and done-looks-like it lacked.
- [ ] Give a prompt you wrote to a colleague with no background and ask them what they would have to guess. Add a line for each guess.
- [ ] Tomorrow: replace one "don't" in a prompt you use with a positive instruction and compare replies on the same input.

## Going further

- [Docs: "Prompt design strategies", Gemini API, Google](https://ai.google.dev/gemini-api/docs/prompting-strategies): a second vendor's guidance on constraints and response format.
- [Prompt Anatomy](../reference/prompt-anatomy.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
