---
title: Resources
description: "Trusted sources for evals"
type: resources
---

# Evals Resources

## Knowledge

- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
  Practitioner walkthrough of turning a vague "did it get better" question into measurable success criteria and a held-out eval set. Use for: designing the eval itself before reaching for a framework.
- [Repo: openai/evals, OpenAI](https://github.com/openai/evals)
  Official framework for defining and running an eval as code: prompts, grading logic, and a registry of existing evals to read as worked examples. Use for: how to structure and run a custom eval.
- [Repo: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  The de facto standard harness for running a model against standardized benchmarks, with the task configs showing how held-out sets are structured and scored in practice. Use for: running or adapting an existing benchmark rather than building an eval from zero.
- [Paper: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., 2023](https://arxiv.org/abs/2306.05685)
  Introduces LLM-as-judge for open-ended tasks and measures its biases against human preference: position bias, verbosity bias, self-enhancement bias. Use for: deciding whether an LLM judge is trustworthy for a given case, and what to correct for if it is.
- [Docs: Evaluate, Hugging Face](https://huggingface.co/docs/evaluate/index)
  Library of standard task-specific metrics (BLEU, ROUGE, exact match, F1, and more) with the definition and failure modes of each. Use for: the task-specific-metric side of the metric-vs-LLM-judge comparison.
- [Paper: "Time Travel in LLMs: Tracing Data Contamination in Large Language Models", Golchin and Surdeanu, 2023](https://arxiv.org/abs/2308.08493)
  A concrete method for testing whether a benchmark's data leaked into a model's training set, with the guessing-the-rest-of-the-instance technique that catches it. Use for: defending a held-out set's honesty against the specific claim "the model just memorized this".
- [Paper: "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models" (BIG-bench), Srivastava et al., 2022](https://arxiv.org/abs/2206.04615)
  Introduces the canary-string convention (a unique marker phrase embedded in benchmark data, asking crawlers to exclude it from training corpora) as a preventive contamination-resistance technique for a benchmark's own release. Use for: designing a custom eval set to resist contamination from the start, rather than detecting it after the fact.
- [Paper: "Evaluating Large Language Models Trained on Code" (Codex), Chen et al., 2021](https://arxiv.org/abs/2107.03374)
  Introduces functional correctness (execute generated code against test cases rather than comparing text) and the unbiased pass@k estimator, with the combinatorial formula that avoids the high variance of directly re-sampling k completions. Use for: evaluating code generation, and for the general principle of checking behavior over text similarity wherever a task is executable.

- [Article: "Cohen's kappa", Wikipedia](https://en.wikipedia.org/wiki/Cohen%27s_kappa)
  The chance-corrected inter-rater agreement statistic: its formula, why a kappa of 0 means no better than chance, and its known tendency to underestimate agreement on a rare category. Use for: measuring human-rater agreement precisely instead of eyeballing a raw agreement percentage.
- [Article: "Inter-rater reliability", Wikipedia](https://en.wikipedia.org/wiki/Inter-rater_reliability)
  Covers why raw joint-probability agreement is misleading (inflated by chance, worse with fewer categories) and Krippendorff's alpha as the generalization of chance-corrected agreement to any number of raters and any level of measurement. Use for: choosing the right agreement statistic for more than two raters or non-categorical ratings.
- [Paper: "HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal", Mazeika et al., 2024](https://arxiv.org/abs/2402.04249)
  Introduces a standardized framework for evaluating automated red-teaming methods against models and defenses, at scale and comparably, where the field previously lacked one. Use for: attack success rate as a metric, and the distinction between an attack-generation method and a rigorous way to evaluate it.
- [Paper: "XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models", Röttger et al., 2023](https://arxiv.org/abs/2308.01263)
  A test suite of safe prompts written to resemble unsafe ones, specifically to surface over-refusal. Use for: the precise tension between harmlessness (refuse unsafe prompts) and helpfulness (don't refuse safe ones), and a concrete way to measure a model landing badly on that trade-off.
- [Paper: "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains", Yao et al., 2024](https://arxiv.org/abs/2406.12045)
  Evaluates agents by comparing the end-of-conversation database state to an annotated goal state, and introduces `pass^k` for measuring an agent's reliability across repeated trials of the same task. Use for: why task success beats step-by-step trajectory matching, and the precise, easy-to-confuse distinction between `pass^k` and lesson 4's `pass@k`.
- [Paper: "AgentBench: Evaluating LLMs as Agents", Liu et al., 2023](https://arxiv.org/abs/2308.03688)
  A multi-dimensional benchmark across 8 distinct interactive environments testing an LLM's reasoning and decision-making as an agent, finding a significant gap between top models and smaller ones specifically in agentic settings. Use for: evidence that agentic capability is a distinct thing to measure, not implied by single-turn benchmark performance.

## Gaps

- No dedicated source yet on statistical significance testing for eval score differences (standard error of a proportion, paired significance tests like McNemar's). The mission needs this for stage 5's "is this difference real or noise" question; lesson 9 teaches it from stable, standard statistical method rather than a single cited source, and this gap should close once a good practitioner-level source is found.
