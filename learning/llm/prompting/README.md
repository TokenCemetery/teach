---
title: Prompting
description: "Write, version and ship prompts for an LLM feature, prove a prompt change helped, and review someone else's production prompt"
type: topic
---

# Learning: Prompting

Write the prompts behind an LLM feature so that they do what was intended, live in the codebase as versioned templates, and change only when a regression set says the change helped. End able to review someone else's production prompt and name what each choice in it costs, instead of saying it reads oddly.

**Latest lesson:** [24. When the Usual Advice Is Wrong](lessons/0024-when-the-usual-advice-is-wrong.md)

## Success looks like

- Write a prompt whose roles, instructions and structure a colleague can read and the model follows, and say what the model actually receives from it.
- Choose, order and audit few-shot examples, naming the bias each choice risks.
- Decide when to ask for reasoning, prompt a reasoning model differently from a standard one, and explain why the written reasoning is not an explanation of the answer.
- Get structured output a program can parse, and lay out a long context so the model uses what is in it.
- Keep prompts in a codebase as versioned templates, ordered so the stable prefix can be cached.
- Show with a regression set and a paired comparison whether a prompt change helped, rather than judging it from a handful of outputs.
- Design a prompt that handles untrusted input, and say which risks the prompt cannot defend against on its own.
- Choose between a better prompt, retrieval and fine-tuning for a given failure, and review someone else's production prompt by naming what each choice costs.

## Constraints

- App-first, usable from a chat window: stages 1 to 6 work in any chat interface, stages 7 to 10 assume the prompt lives in code.
- No fixed provider or model. Examples are provider-neutral; where a technique is one vendor's documented behaviour, the lesson says so.
- No prior knowledge of prompting assumed. Knowing what an LLM is, at the level of "it predicts the next token", is enough.

## Out of scope

- Prompt construction over retrieved context and the context-window budget: see [`llm/rag`](../../llm/rag/) and its [generation-from-retrieval sheet](../../llm/rag/reference/generation-from-retrieval.md). This track teaches prompting in general and links there for the retrieval case.
- Tool descriptions as prompt surface, prompt injection in an agent with tools, and prompt caching under concurrency: see [`llm/agents`](../../llm/agents/). This track covers prompting without tools and links those lessons rather than restating them.
- Judge-prompt design and eval methodology: see [`llm/evals`](../../llm/evals/) and its [go/no-go sheet](../../llm/evals/reference/go-no-go.md). This track uses an eval to measure a prompt change and does not teach how to build one.
- Constrained decoding, the serving side of structured output: see [`llm/inference`](../../llm/inference/). This track asks for structure from the prompt side.
- How instruction-following and reasoning are trained into a model: see [`llm/post-training`](../../llm/post-training/). This track covers how to use them from outside.

## The arc

Ten stages, from what a prompt is to the model to the judgment to review someone else's. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. What a prompt is to the model | 0001 to 0002 | Tokens, chat templates, roles, the system prompt and the instruction hierarchy | Can say what sequence the model receives for a given conversation and where each instruction belongs |
| 2. Instructions and structure | 0003 to 0005 | Clear instructions, delimiters and tags, sensitivity to formatting | Can write a prompt a newcomer could follow and that keeps instructions apart from data |
| 3. Few-shot examples | 0006 to 0007 | What demonstrations teach, majority-label, recency and ordering biases | Can choose and order examples and name the bias each choice risks |
| 4. Reasoning | 0008 to 0010 | Chain-of-thought, self-consistency, faithfulness, prompting reasoning models | Can decide whether to ask for reasoning and how, for a given model and task |
| 5. Structured output | 0011 to 0012 | Asking for a schema, validating it, format constraints against reasoning quality | Gets output a program parses, without paying for it in answer quality |
| 6. Long context | 0013 to 0014 | Position effects, document layout, quote extraction | Can lay out a long context so the model uses what is in the middle of it |
| 7. Prompts in a codebase | 0015 to 0017 | Templates, versioning against a model snapshot, layout for prompt caching | Keeps prompts as versioned templates whose stable prefix is cacheable |
| 8. Measuring a prompt change | 0018 to 0019 | Regression sets from real failures, paired comparison against noise | Can show with a number whether prompt B beats prompt A |
| 9. Prompt security | 0020 to 0021 | Direct and indirect prompt injection, what the prompt can and cannot defend | Can design a prompt for untrusted input and name the risks it leaves to the system |
| 10. Judgment | 0022 to 0024 | Prompt against RAG against fine-tune, reviewing a production prompt, changing a prompt others depend on, when the usual advice is wrong | Trusted to make the call on a prompt and to explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-what-the-model-sees.md) | What the Model Sees | A prompt reaches the model as one token sequence built by a chat template, so roles are formatting the model was trained on, not separate channels |
| [0002](lessons/0002-system-prompts-and-roles.md) | System Prompts and Roles | What belongs in the system prompt and what in the user turn, and why the model ranks instructions by where they sit |
| [0003](lessons/0003-clear-instructions.md) | Clear Instructions | Write an instruction a capable newcomer could follow: context, the task, the constraints, and what done looks like |
| [0004](lessons/0004-structure-and-delimiters.md) | Structure and Delimiters | Separate instructions from data with tags and sections so the model can tell which is which |
| [0005](lessons/0005-format-sensitivity.md) | Format Sensitivity | Why a formatting change with no meaning can move accuracy, and why that makes every prompt edit a claim to test |
| [0006](lessons/0006-what-examples-teach.md) | What Few-Shot Examples Teach | Demonstrations mostly teach the format, the label space and the input distribution, which changes how you choose them |
| [0007](lessons/0007-few-shot-biases.md) | Few-Shot Biases | Majority-label, recency and ordering biases in few-shot prompts, and how to choose and order examples against them |
| [0008](lessons/0008-chain-of-thought.md) | Chain-of-Thought | When asking for intermediate reasoning improves an answer, and when it only adds tokens |
| [0009](lessons/0009-self-consistency-and-faithfulness.md) | Self-Consistency and Faithfulness | Sampling several reasoning paths to vote on an answer, and why the written reasoning is not a faithful explanation |
| [0010](lessons/0010-prompting-reasoning-models.md) | Prompting Reasoning Models | Why a model that already thinks needs goals and constraints rather than scripted steps |
| [0011](lessons/0011-structured-output-from-the-prompt.md) | Structured Output from the Prompt | Ask for output a program can parse, then validate it, because asking is not a guarantee |
| [0012](lessons/0012-format-constraints-and-reasoning.md) | Format Constraints and Reasoning | A strict output format can cost reasoning quality, and how to order fields so the answer comes after the thinking |
| [0013](lessons/0013-position-in-long-context.md) | Position in Long Context | Models use information at the edges of a long context better than the middle, which decides where documents and the question go |
| [0014](lessons/0014-working-with-long-documents.md) | Working with Long Documents | Tag documents with their metadata and have the model extract quotes before it answers |
| [0015](lessons/0015-prompt-templates.md) | Prompt Templates | Split a prompt into a fixed template and the variables filled per request, and keep untrusted input from breaking the structure |
| [0016](lessons/0016-versioning-prompts.md) | Versioning Prompts | Treat a prompt as code: pinned to a model snapshot, versioned, reviewed and rolled back like any other change |
| [0017](lessons/0017-prompt-caching-and-layout.md) | Prompt Caching and Layout | Order a prompt with the stable parts first so the provider can cache the prefix |
| [0018](lessons/0018-a-regression-set-for-a-prompt.md) | A Regression Set for a Prompt | Build the small set of cases a prompt change must not break, starting from real failures |
| [0019](lessons/0019-comparing-two-prompts.md) | Comparing Two Prompts | Decide whether prompt B beats prompt A with a paired comparison that separates the change from run-to-run noise |
| [0020](lessons/0020-prompt-injection.md) | Prompt Injection | How text in the input can override the author's instructions, directly or hidden in content the model reads |
| [0021](lessons/0021-what-a-prompt-cannot-defend.md) | What a Prompt Cannot Defend | Which defences belong in the prompt, and why the real ones sit in what the system lets the model do |
| [0022](lessons/0022-prompt-rag-or-fine-tune.md) | Prompt, RAG or Fine-Tune | Choose between a better prompt, retrieval and fine-tuning by what the failure actually is |
| [0023](lessons/0023-reviewing-a-production-prompt.md) | Reviewing a Production Prompt | Review someone else's prompt by naming what each choice costs, and change a prompt others depend on without breaking them |
| [0024](lessons/0024-when-the-usual-advice-is-wrong.md) | When the Usual Advice Is Wrong | Recognise when standard prompting advice fails for a given model or task, and settle the dispute from the primary source |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources, each annotated with what it covers
- [Prompt Anatomy](reference/prompt-anatomy.md): roles, what goes where, and the structure checklist from stages 1 and 2
- [Few-Shot and Reasoning](reference/few-shot-and-reasoning.md): choosing and ordering examples, and when to ask for reasoning, from stages 3 and 4
- [Structured Output and Long Context](reference/structured-output-and-long-context.md): getting parseable output and laying out long inputs, from stages 5 and 6
- [Prompts in Production](reference/prompts-in-production.md): templates, versioning, cache-friendly layout and the measurement loop, from stages 7 and 8
- [Prompt Security](reference/prompt-security.md): injection routes and which defence sits where, from stage 9
- [Prompt Review Checklist](reference/prompt-review-checklist.md): the questions to ask of someone else's prompt, and prompt against RAG against fine-tune, from stage 10

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
