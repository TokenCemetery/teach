---
title: Glossary
description: "Canonical terms for prompting"
type: glossary
---

# Prompting Glossary

Canonical terms for writing, structuring, versioning, measuring and securing the prompts behind an LLM feature.

## Terms

**Chain-of-thought**:
Intermediate reasoning the model writes before its final answer, elicited by examples that show it or by an instruction that asks for it.
_Avoid_: CoT in prose (fine in a heading or table), thinking (reserved here for a reasoning model's built-in phase)

**Chat template**:
The model-specific rule that renders a list of role-tagged messages into the single token sequence the model was trained on, including the special tokens that mark where each role begins and ends.
_Avoid_: prompt format

**Constrained decoding**:
Limiting which tokens the model may generate at each step so the output must match a grammar or schema, as a provider's enforced structured-output feature does.
_Avoid_: grammar sampling

**Delimiter**:
Markup in a prompt, such as an XML-style tag or a fenced block, that marks where one kind of content ends and another begins, most often to keep data apart from instructions.
_Avoid_: separator

**Few-shot prompt**:
A prompt that includes worked examples of the task, each an input paired with the desired output, before the real input.
_Avoid_: multishot prompt, in-context training

**Indirect prompt injection**:
Prompt injection carried by content the model reads on the user's behalf, such as a web page, an email or a retrieved document, rather than typed by the person talking to it.
_Avoid_: second-order injection

**Instruction hierarchy**:
The ranking a model is trained to apply when instructions conflict: system prompt above user turn, user turn above content returned by tools or retrieval.
_Avoid_: priority order

**Jailbreak**:
Input crafted to make a model produce what its safety training refuses. It targets the model's own limits, where prompt injection targets the application's instructions.
_Avoid_: prompt injection (a different target)

**Lethal trifecta**:
The combination of access to private data, exposure to untrusted content and a way to send data out, which together make prompt injection exploitable. Removing any one of the three closes the route.
_Avoid_: injection risk (too vague to act on)

**Model snapshot**:
A fixed version of a model, named by an exact model ID, whose weights the provider does not change. A convenience alias may point to a newer snapshot over time.
_Avoid_: model version (ambiguous with a model generation)

**Paired comparison**:
Comparing two prompts or models on the same inputs by the cases where their results differ, rather than by their two totals.
_Avoid_: A/B score comparison

**Prompt**:
Everything the model receives for one call: the system prompt, every message in the conversation so far, and any inserted content, rendered by the chat template into one token sequence.
_Avoid_: query (that is the user's question within the prompt)

**Prompt caching**:
A provider feature that stores the processed state of a prompt prefix so later calls sharing that exact prefix skip recomputing it, cutting cost and latency.
_Avoid_: response caching (a different thing: storing whole answers)

**Prompt injection**:
Input that causes the model to follow instructions other than the ones the prompt's author intended.
_Avoid_: jailbreak (a jailbreak targets the model's safety training; injection targets the application's instructions)

**Prompt template**:
The fixed text of a prompt with named slots that are filled with per-request values, such as the user's message or a retrieved document, at call time.
_Avoid_: prompt string

**Reasoning model**:
A model trained to produce an internal reasoning phase before its visible answer, so it reasons without being asked to.
_Avoid_: thinking model

**Regression set**:
A fixed set of inputs, each with a check on the output, that a prompt change must not break, built mostly from failures seen in real use.
_Avoid_: test prompts, golden set

**Role**:
The label on each message in a conversation, usually system, user or assistant, that the chat template turns into special tokens. A role is formatting the model learned to weight, not a separate input channel.
_Avoid_: persona (that is a description of who the model should act as)

**Self-consistency**:
Sampling several chain-of-thought completions for the same prompt and taking the most common final answer.
_Avoid_: ensembling

**Structured output**:
A response in a machine-readable format, usually JSON matching a schema, that a program parses instead of a person reading it.
_Avoid_: JSON mode (one provider feature for it)

**System prompt**:
The message, in the system role, that sets the model's task, constraints and context for the whole conversation, and sits highest in the instruction hierarchy.
_Avoid_: system message, preamble

**Zero-shot prompt**:
A prompt that states the task without any worked examples.
_Avoid_: plain prompt
