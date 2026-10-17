---
title: Resources
description: "Trusted sources for prompting"
type: resources
---

# Prompting Resources

## Knowledge

- [Docs: "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
  One vendor's consolidated guide: clear instructions, examples, XML tags, roles, thinking, long context and output format, with before-and-after prompts. Use for: the practitioner baseline for stages 2 to 6, read as one vendor's documented behaviour.
- [Docs: "Prompt engineering overview", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
  The advice to define success criteria and tests before iterating, and a short note that not every failing eval is best fixed by prompting. Use for: the measure-first habit.
- [Docs: "Long context prompting", section of Prompting best practices, Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#long-context-prompting)
  Placing long documents before the query, wrapping each in tags with its metadata, and asking for relevant quotes first. Use for: laying out a long input.
- [Docs: "Structured outputs", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
  A provider feature that enforces a JSON schema on the response, documented alongside what the prompt alone does not guarantee. Use for: the boundary between asking for structure and enforcing it.
- [Docs: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
  How a cached prefix is matched, what invalidates it, and the order the prompt must keep for a hit. Use for: laying a prompt out so its stable parts cache.
- [Docs: "Model IDs and versioning", Claude Platform Docs](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions)
  How one vendor names fixed snapshots and moving aliases, and that each ID has its own retirement schedule. Use for: pinning a prompt to the model it was tested against.
- [Docs: "Extended thinking", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
  The API mechanics of a thinking phase: the token budget, its minimum, and how thinking counts toward the output limit. Use for: the budget facts behind prompting a reasoning model; the wording advice is in the best-practices guide.
- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
  Turning "is this prompt better" into success criteria and an eval design, including edge cases and comparison against a baseline. Use for: deciding what a prompt change must be judged against before changing anything.
- [Docs: "Mitigate jailbreaks and prompt injections", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks)
  Prompt-level and system-level mitigations, including screening input and limiting what the model can do. Use for: which defences a prompt author owns.
- [Docs: "Prompt design strategies", Gemini API, Google](https://ai.google.dev/gemini-api/docs/prompting-strategies)
  A second vendor's guide to instructions, few-shot examples, prefixes and breaking down a task. Use for: checking whether a technique is general or one vendor's behaviour.
- [Docs: "Chat templates", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
  How a list of role-tagged messages is rendered into the single token sequence a model was trained on, with real template output. Use for: what the model actually sees.
- [Repo: "Prompt engineering interactive tutorial", Anthropic](https://github.com/anthropics/prompt-eng-interactive-tutorial)
  Notebook exercises covering roles, separating data from instructions, examples, step-by-step reasoning and avoiding hallucination. Use for: practice reps on stages 1 to 4.
- [Paper: "The Prompt Report: A Systematic Survey of Prompting Techniques", Schulhoff et al., 2024](https://arxiv.org/abs/2406.06608)
  A survey and taxonomy of prompting techniques with consistent vocabulary. Use for: placing a technique you meet in the wild, and settling what a term means.
- [Paper: "Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design", Sclar et al., 2023](https://arxiv.org/abs/2310.11324)
  Shows meaning-preserving formatting changes (separators, casing, spacing) moving few-shot accuracy by large margins. Use for: why a prompt edit is a claim to test, not a style choice.
- [Paper: "Rethinking the Role of Demonstrations", Min et al., 2022](https://arxiv.org/abs/2202.12837)
  Finds that randomly replacing demonstration labels barely hurts, while format, label space and input distribution matter. Use for: what few-shot examples actually teach.
- [Paper: "Calibrate Before Use: Improving Few-Shot Performance of Language Models", Zhao et al., 2021](https://arxiv.org/abs/2102.09690)
  Names majority-label, recency and common-token bias in few-shot prompts and proposes contextual calibration. Use for: the biases a set of examples brings.
- [Paper: "Fantastically Ordered Prompts and Where to Find Them", Lu et al., 2021](https://arxiv.org/abs/2104.08786)
  Shows the order of the same few-shot examples swinging accuracy from near state of the art to near chance. Use for: why example order is a variable to control.
- [Paper: "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", Wei et al., 2022](https://arxiv.org/abs/2201.11903)
  The original few-shot chain-of-thought result, and its finding that the gain appears only at sufficient model scale. Use for: when asking for reasoning helps.
- [Paper: "Large Language Models are Zero-Shot Reasoners", Kojima et al., 2022](https://arxiv.org/abs/2205.11916)
  Zero-shot chain-of-thought: a single trigger phrase eliciting reasoning without examples. Use for: reasoning without hand-written demonstrations.
- [Paper: "Self-Consistency Improves Chain of Thought Reasoning in Language Models", Wang et al., 2022](https://arxiv.org/abs/2203.11171)
  Sampling several reasoning paths and taking the majority answer. Use for: trading tokens for accuracy on a task with one checkable answer.
- [Paper: "Language Models Don't Always Say What They Think", Turpin et al., 2023](https://arxiv.org/abs/2305.04388)
  Shows a model's chain-of-thought omitting the biasing feature that actually drove its answer. Use for: why written reasoning is not a faithful explanation.
- [Paper: "Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models", Tam et al., 2024](https://arxiv.org/abs/2408.02442)
  Measures reasoning accuracy dropping under strict output-format constraints. Use for: the cost of forcing a format, and how to order fields.
- [Paper: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
  The U-shaped curve: information at the start and end of a long context is used better than information in the middle. Use for: deciding where documents and the question go.
- [Paper: "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions", Wallace et al., 2024](https://arxiv.org/abs/2404.13208)
  Defines the system, user and tool-output privilege levels and trains a model to follow the higher one on conflict. Use for: why where an instruction sits changes its weight.
- [Paper: "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models", Zheng et al., 2023](https://arxiv.org/abs/2311.10054)
  Tests 162 personas in system prompts across four model families and 2,410 factual questions and finds no improvement over no persona, with a persona's effect largely random. Use for: settling the role-prompting dispute from data.
- [Paper: "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection", Greshake et al., 2023](https://arxiv.org/abs/2302.12173)
  Introduces indirect prompt injection through retrieved content and demonstrates it against real applications. Use for: how an attacker reaches a prompt they never type into.
- [Paper: "Fine-Tuning or Retrieval? Comparing Knowledge Injection in LLMs", Ovadia et al., 2023](https://arxiv.org/abs/2312.05934)
  Compares unsupervised fine-tuning against retrieval for adding knowledge and finds retrieval consistently better, for knowledge seen in training and for new facts alike. Use for: the prompt, RAG or fine-tune call.
- [Article: "LLM01:2025 Prompt Injection", OWASP Gen AI Security Project](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
  The industry risk entry: direct and indirect injection, impacts, and mitigations ranked by where they sit. Use for: the shared vocabulary and mitigation list.
- [Article: "The lethal trifecta for AI agents", Simon Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
  Private data, untrusted content and an exfiltration channel together make injection exploitable, and removing one leg is the defence. Use for: why the real defence sits outside the prompt.
- [Article: "Your AI Product Needs Evals", Hamel Husain](https://hamel.dev/blog/posts/evals/)
  A practitioner case for unit-test-style checks and logged real traces as the base of iterating on a prompt. Use for: building a regression set from real failures.

## Gaps

- OpenAI's prompt engineering, reasoning and structured-output guides would be a third vendor view, but every page on `platform.openai.com` and `developers.openai.com` answered a scripted and a browser check with 403, so none could be verified to resolve. Add them once one can be.
- No peer-reviewed source measures prompt versioning or template practice directly. Lessons 15 and 16 teach it from vendor documentation and ordinary software-engineering practice, and say so.
