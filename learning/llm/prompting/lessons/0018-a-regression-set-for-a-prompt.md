---
title: "18. A Regression Set for a Prompt"
description: Build the small set of cases a prompt change must not break, starting from real failures
type: lesson
---

# Lesson 18. A Regression Set for a Prompt

**Mission link:** A prompt change is a claim, and a regression set is what lets a claim be checked in seconds instead of judged from the three outputs you happened to read.
**Primary source:** [Article: "Your AI Product Needs Evals", Hamel Husain](https://hamel.dev/blog/posts/evals/)
**Prerequisites:** [Lesson 17](0017-prompt-caching-and-layout.md), [Regression set](../GLOSSARY.md)

## Warm-up

1. ▢ Lesson 11 asked for structured output and then validated it. Why is a validity check a natural first assertion in a regression set?

<details markdown="1"><summary>Check</summary>

Asking for a format is not a guarantee, so output can fail to parse. A parse or schema check is cheap, needs no judgment and runs on every case, which makes it an assertion that is easy to write.

</details>

2. ▢ Lesson 5 showed that a meaning-free formatting edit can change accuracy. What does that imply about how much of a prompt change you can judge by reading a few outputs?

<details markdown="1"><summary>Check</summary>

Very little. A small edit can shift results in ways a handful of outputs will not show, so the change has to be run against a fixed set of cases and counted.

</details>

## Know this

### Start from failures you have already seen

A **regression set** is a fixed set of inputs, each with a check on the output, that a prompt change must not break. The best first cases are real ones. Hamel Husain's account of building evals for a real-estate assistant says to look critically at traces and failure modes when you cannot think of assertions, and that the team's hundreds of unit tests were updated continuously from new failures observed in the data. A trace is a logged conversation, so log them, read them, and turn each failure into a case: the input that triggered it and a check that would have caught it.

Anthropic's guide on building evaluations agrees on the target: design tests that mirror your real task distribution, include edge cases, and automate grading where you can. You do not need production traffic to begin. Hamel notes you can write educated guesses, or have a model generate inputs, and let early users refine them.

### One assertion per property

Hamel describes the checks as assertions, like you would write in pytest, kept fast and cheap so they can run on every change. Each case lists the properties its output must have.

```python
CASES = [
    {"id": "refund-not-complaint", "ticket": "I want my money back for order 118.",
     "must_contain": ["refund"], "must_not_contain": ["complaint"]},
    {"id": "no-uuid", "ticket": "Account 3f2b8c1e-9d4a-4e7b-a1c2-5d6e7f8a9b0c is locked.",
     "must_contain": [], "must_not_contain": ["3f2b8c1e"]},
]


def run_case(case: dict, call_model) -> bool:
    output = call_model(case["ticket"]).lower()
    has_all = all(s in output for s in case["must_contain"])
    has_none = not any(s in output for s in case["must_not_contain"])
    return has_all and has_none


def run_set(call_model) -> dict:
    return {c["id"]: run_case(c, call_model) for c in CASES}
```

`call_model` renders the template from lesson 15, calls the pinned model from lesson 16 and returns its text. Hamel's own example is a similar check that the output never exposes an internal UUID. Where a property cannot be a string or regex test, a model can grade it, and the evals track covers when to trust that grader.

### Small, growing and not all-or-nothing

Start with the handful of failures in front of you and add a case every time a new failure appears. The set should be representative of the failures you care about, not large for its own sake: Anthropic's guide favours volume over hand-graded quality, and Hamel's team reached hundreds of tests, so small is where it starts, not a target. Two cautions from Hamel: a good set contains cases the model struggles with, and unlike ordinary unit tests you do not necessarily need a 100% pass rate, because the pass rate is a product decision about which failures you tolerate. Track results against the prompt version so you can see whether you are making progress.

## Practice

1. ▢ A user reports that the summariser calls a refund request a "complaint". Turn that report into a case: what goes in the input, and what assertions does the output need?

<details markdown="1"><summary>Check</summary>

The input is the user's actual ticket text, or one close to it. The assertions are `must_contain` the word refund and `must_not_contain` the word complaint, as in the `refund-not-complaint` case above. The case now fails on the old prompt and passes on the fix.

</details>

2. ▢ Predict `run_case` for the `no-uuid` case when the model outputs `Account 3f2b8c1e is locked.`

<details markdown="1"><summary>Hint</summary>

Compare the output with the single `must_not_contain` string.

</details>

<details markdown="1"><summary>Check</summary>

It returns `False`. `must_contain` is empty, so `has_all` is true, but the output includes `3f2b8c1e`, so `has_none` is false and the case fails. The prompt leaked part of the ID.

</details>

3. ▢ A teammate wants to wait until there are 500 production-quality cases before building a regression set. What is wrong with that, using this lesson's sources?

<details markdown="1"><summary>Check</summary>

Nothing runs until then, so changes in the meantime are judged by vibes. The sources describe sets that grew from observed failures, and Hamel says you can start from educated guesses. Start with the failures you have and add cases as new ones appear.

</details>

4. ▢ A regression set passes 18 of 20 cases on the current prompt and the team insists on 20 of 20 before any release. Which view matches Hamel's article?

    - a) The pass rate is a product decision about tolerated failures, so 100% is not required
    - b) Every case must pass or the set is worthless as a gate before shipping
    - c) The two failing cases should be deleted so the set reflects the current prompt
    - d) The pass rate matters less than the number of cases, which should always be minimised

<details markdown="1"><summary>Check</summary>

**a)** Hamel says you do not necessarily need a 100% pass rate and that it depends on the failures you will tolerate. (b) is the ordinary unit-test habit he contrasts it with. (c) removes the failures the set exists to remember. (d) is backwards: the set is small only as a starting point.

</details>

## Real-world reps

- [ ] Pull five real or realistic failures of a prompt you run, from logs, bug reports or your own testing, and write each as an input plus one assertion.
- [ ] Put the five cases in a file in the repository next to the prompt and run them against the current prompt, noting which pass.
- [ ] Tomorrow: the next time the prompt gives a bad output, add it as a case before you fix the prompt, and confirm it fails first.

## Going further

- [Article: "Your AI Product Needs Evals", Hamel Husain](https://hamel.dev/blog/posts/evals/)
- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Prompts in Production](../reference/prompts-in-production.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
