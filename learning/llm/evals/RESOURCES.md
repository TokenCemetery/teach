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
