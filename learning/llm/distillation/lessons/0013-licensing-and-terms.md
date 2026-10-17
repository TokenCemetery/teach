---
title: "13. Licensing and Terms"
description: What a provider's terms and an open model's license allow you to do with its outputs
type: lesson
---

# Lesson 13. Licensing and Terms

**Mission link:** The mission asks you to check that a distillation set's use is permitted, which means reading the documents that govern the teacher before generating data from it, and recording what you found.
**Primary source:** [Terms: "Terms of Use", OpenAI](https://openai.com/policies/row-terms-of-use/)
**Prerequisites:** [Lesson 12](0012-filtering-synthetic-data.md), [Lesson 10](0010-distilling-from-generated-data.md), [Synthetic data](../GLOSSARY.md), [Teacher](../GLOSSARY.md)

This lesson is not legal advice. It reads two documents, quotes what they say, and offers a checklist of what to look for. It makes no claim about what a document means for your case, whether a clause is enforceable, or which document governs you. Terms and licenses change without a version a lesson can pin, so the quotes below carry the date they were read, and you should read the current text before relying on any of them. For a real decision, ask a lawyer.

## Warm-up

1. ▢ phi-1's authors pruned their exercises against HumanEval with n-grams, embeddings and AST matching. Why did they not stop at n-gram overlap?

<details markdown="1"><summary>Check</summary>

A 13-gram check flagged only four questions, all false positives, and was too coarse to find similar code, so they added embedding and AST comparison (lesson 12).

</details>

2. ▢ Alpaca's data came from text-davinci-003 and its model was fine-tuned from LLaMA 7B. Which two things does it therefore depend on that someone else owns or controls?

<details markdown="1"><summary>Check</summary>

The teacher that generated the data (OpenAI's text-davinci-003, under OpenAI's terms) and the base model (LLaMA, under its license). Both are inputs to the student, and each comes with its own conditions (lesson 10).

</details>

3. ▢ Name the filter that checks a generated answer against ground truth by rule, and one thing it cannot judge.

<details markdown="1"><summary>Check</summary>

Rejection sampling with a checker, where only samples that pass are kept. It cannot judge open-ended answers or style, where there is nothing to check against (lesson 12).

</details>

## Know this

### Three documents, three questions

When you generate data from a teacher you can be bound by up to three different kinds of document, and each answers a different question.

| Document | Question it answers |
|---|---|
| The provider's terms of use, for a hosted model | What may I do with the outputs I get from this service? |
| The license of open weights | What may I do with the model, and with what it produces? |
| The license or terms of the prompts and seed data | What may I do with the inputs I fed it, and with data I built from them? |

Each is a separate text with its own date and scope. Reading one does not tell you what another says.

### What a hosted provider's terms say

OpenAI's Terms of Use for the rest of the world, effective January 1, 2026, list things a user cannot do. Among them is this line, as read when this track was written, in October 2026. The site blocks scripted reads, so recheck the page in a browser:

> "Use Output to develop models that compete with OpenAI."

Three things to note, and no more. The sentence is in the section of prohibited uses. It speaks of developing models that compete with OpenAI, which is a narrower thing than developing any model. And it is one document: your use may fall under a different edition, or a separate agreement for an API or enterprise service, and this lesson has not read those.

### What an open-weights license says

The Llama 3.1 Community License Agreement from Meta says, in section 1.b.i (Redistribution and Use), as read from the repository text on October 17, 2026:

> "If you use the Llama Materials or any outputs or results of the Llama Materials to create, train, fine tune, or otherwise improve an AI model, which is distributed or made available, you shall also include “Llama” at the beginning of any such AI model name."

The same paragraph also requires that if you distribute the Llama Materials, or a product or service containing them, including another AI model, you provide a copy of the agreement and prominently display "Built with Llama" on a related website, user interface, blogpost, about page or product documentation. Separately, the license says use of the Llama Materials must comply with applicable laws and with an Acceptable Use Policy it incorporates by reference.

The text attaches a condition about the model's name to using outputs this way when the resulting model is distributed or made available. This lesson claims nothing beyond the words. Other Llama versions and other open models have their own licenses, and some say different things.

### How one project dealt with it

The Alpaca authors state that their model is intended only for academic research and any commercial use is prohibited, and give three factors: LLaMA has a non-commercial license, so they inherit it; the instruction data comes from text-davinci-003, whose terms of use, they say, prohibit developing models that compete with OpenAI; and they had not built adequate safety measures. They also write that their demo was restricted to non-commercial uses and to uses that follow LLaMA's license (Alpaca blog post, "Overview" and "Release decision"). Note what they did: they named each source of restriction and tied the release to it. That is the habit to copy, whatever your own documents say.

### Before you generate: a checklist

Read and record, in this order:

1. **The teacher's terms.** Find the exact document that applies to the way you access the model. Note its name, URL, date or version, and the sentences about using outputs to train other models.
2. **The weights' license, if the teacher is open.** Note the version, any clause about training on outputs, any naming or attribution requirement, and any use policy it incorporates.
3. **The prompts and seed data.** The license of whatever you feed the teacher, such as seed tasks, documents or scraped text, governs the inputs. Check it separately from the teacher.
4. **Naming and attribution.** If a document requires a model name prefix or a credit line, decide now, before the model has a name.
5. **How the student will be used and shared.** Many clauses depend on whether the model is distributed, made available, or sold, and on what it competes with. Write down your intended use.
6. **The date.** Record when you read each document and when you generated each batch, because the terms in force at generation time may differ from the terms today.

Keep this record next to the dataset, one line per source, so that the question "where did this come from?" has an answer a year later. A provenance field on each example, naming the teacher, version and generation date, costs almost nothing.

```text
teacher: <name and version>
access: <hosted service or local weights>
terms read: <document, URL, date read, effective date if stated>
license: <name and version, if open weights>
prompt and seed data: <source, license>
naming or attribution duties: <list, or none found>
intended use: <research, internal, distributed, commercial>
generated on: <date range>
```

The `<...>` entries are fields to fill in for your own project.

### What this lesson cannot tell you

It cannot say whether a given project breaks a clause. That depends on the full text, the facts, the jurisdiction and what the provider and the license holder will do, none of which are in a quote. The point of the exercise is narrower: make sure you have read the documents, know what they literally say, and have a dated record of it.

## Practice

1. ▢ A team fine-tunes a model on outputs from Llama 3.1 and will make it available. According to the quoted license text, what must be true of the new model's name?

    - a) It must end with the word "Llama"
    - b) It must contain no mention of Llama
    - c) It must begin with the word "Llama"
    - d) It must be registered with the licensor

<details markdown="1"><summary>Check</summary>

**c)** The quoted sentence says "Llama" at the beginning of the AI model name, for a model that is distributed or made available. (a) reverses the position. (b) is the opposite of what it says. (d) is not in the quoted text.

</details>

2. ▢ The quoted OpenAI line is about using output "to develop models that compete with OpenAI". A colleague summarizes it as "OpenAI bans training on its outputs". What is wrong with the summary?

<details markdown="1"><summary>Check</summary>

The line is narrower than the summary: it concerns developing models that compete with OpenAI, not all model development. It is also one document, from one edition of the terms, on one date. Quote the sentence and its date instead of a paraphrase, and check what applies to your access route. Whether your project competes is a legal question this lesson does not answer.

</details>

3. ▢ You generated 200,000 examples from a hosted model in March. In October the provider changes its terms. What do you do first?

<details markdown="1"><summary>Check</summary>

Read the new terms and the terms in force when you generated the data, both from the provider's own page, and look at what your record says about which version you read. The record is why you wrote the date down. What follows is a legal question about which terms apply to data already generated, so take it to someone qualified, not to a guess.

</details>

4. ▢ Alpaca's authors give three factors for a research-only release. Which one depends on the choice of teacher, and which on the choice of student base?

<details markdown="1"><summary>Check</summary>

The teacher factor is that the data comes from text-davinci-003, whose terms prohibit developing models that compete with OpenAI. The base factor is that LLaMA has a non-commercial license, so Alpaca inherits it. The third, missing safety measures, is about neither.

</details>

5. ▢ Your seed prompts come from a public dataset and your teacher is an open model under a permissive license. Name two documents you still need to read before you ship the student.

<details markdown="1"><summary>Check</summary>

The license of the seed dataset, since it governs the inputs, and the open model's own license, for any clause about training on its outputs, naming, attribution or use policy. Also check the license of any base model the student starts from. A permissive license on one source does not carry over to the others.

</details>

## Real-world reps

- [ ] Open the OpenAI Terms of Use and the Llama 3.1 license and find the exact sentences quoted above. Copy the effective date of each into a note.
- [ ] Pick a public synthetic dataset on a hub you use. Find which teacher it says it was generated from, and write down the terms or license of that teacher as stated on the dataset page.
- [ ] Tomorrow: fill in the checklist record above for a hypothetical dataset from a teacher of your choice, and mark each field you could not fill from a primary document.

## Going further

- [Sequence and Synthetic Data](../reference/sequence-and-synthetic-data.md)
- [Terms: "Terms of Use", OpenAI](https://openai.com/policies/row-terms-of-use/)
- [License: "Llama 3.1 Community License Agreement", Meta](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE)
- [Article: "Alpaca: A Strong, Replicable Instruction-Following Model", Stanford CRFM, 2023](https://crfm.stanford.edu/2023/03/13/alpaca.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
