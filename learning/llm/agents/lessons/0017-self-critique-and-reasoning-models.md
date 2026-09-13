---
title: 17. Self-Critique and What Reasoning Models Changed
description: Reflection loop as an explicit stage, its costs, and how extended internal reasoning affects when to use it
type: lesson
---

# Lesson 17. Self-Critique and What Reasoning Models Changed

**Mission link:** To diagnose a failing agent, you need to recognize when to add a reflection stage (a separate loop that evaluates past failures and carries lessons forward) versus when the model's own internal reasoning makes that loop redundant.
**Primary source:** [Paper: "Reflexion: Language Agents with Verbal Reinforcement Learning", Shinn et al., 2023](https://arxiv.org/abs/2303.11366)
**Prerequisites:** [Lesson 16](0016-plan-then-execute-and-decomposition.md)

## Warm-up

1. ▢ In a plan-then-execute agent, what happens if a step fails and the harness does not support replanning?

<details markdown="1"><summary>Check</summary>

The harness has no way to adapt. It either continues blindly with the original plan (which will likely fail again), or halts. The agent cannot learn from the failure or pivot to a different approach because the plan was locked in upfront and there is no mechanism to update it.

</details>

2. ▢ What is the advantage of explicit replanning over just running the agent again from the start?

<details markdown="1"><summary>Check</summary>

Replanning allows the model to see the exact failure and reason about it in context. If you just re-run the agent, it might produce the same plan again. With replanning, the harness appends the failure to the transcript and asks the model to make a new plan, so the model can see what went wrong and adjust.

</details>

## Know this

### Reflexion: Adding a reflection loop

The Reflexion paper introduces an explicit reflection stage into the agent loop. After an attempt fails (the agent's answer is wrong, a task does not complete, a test fails), the harness does not immediately retry. Instead, it generates a natural-language reflection on what went wrong. This reflection is stored (often in a file or memory buffer) and included in the context for the next attempt.

The loop looks like this:

1. Run the agent on a task.
2. Check whether the task succeeded (a test passes, a human evaluates the answer as correct).
3. If it failed, generate a reflection: "I tried X, but X failed because Y."
4. Store the reflection in a persistent memory.
5. Run the agent again, this time including the stored reflection in the context.
6. Go back to step 2.

This is different from a simple retry. A simple retry runs the agent again with the same context. Reflexion runs the agent again with the reflection in context, so the second attempt can learn from the first attempt's failure.

### Why reflection is not free

Reflexion costs extra model calls. If the first attempt fails, you now need a call to generate the reflection, then another call to run the second attempt. For tasks with low failure rates, this overhead is not worth paying. For tasks where many attempts are needed, the cumulative cost is high.

Reflection also consumes context budget. Each reflection takes tokens in the context window. If you build up many reflections across attempts, you eventually have to prune or summarize them. This is a different version of the context-management problem from earlier lessons.

Reflection makes sense only if the reflection itself is grounded in real information: a test that failed, an error message, a human evaluation. If the task has no clear failure signal, reflection has nothing concrete to react to and may simply rationalize the previous wrong answer.

### Models with extended internal reasoning

In recent years, some frontier models have gained the ability to do extended internal reasoning before producing an answer. This reasoning is not visible in the transcript (it happens inside a single model turn, before the output is returned) but it allows the model to self-correct, double-check its work, and catch obvious mistakes before they appear in the output.

This changes, but does not eliminate, the case for explicit reflection loops. Some of what a reflection loop used to provide (catching an obviously wrong intermediate step) now happens inside the model's own reasoning, so adding a reflection loop on top provides less marginal benefit than it used to.

However, explicit reflection still has an advantage that internal reasoning does not: it can incorporate information that only exists after a tool call was made. If a tool call returns "Permission denied" or a test fails, the model's internal reasoning cannot have seen that failure signal during its original reasoning phase, because the tool had not run yet. An explicit reflection loop can observe the tool's actual result and incorporate it into the next attempt.

So the question is not "reflection or internal reasoning," but rather "when does the extra cost of external reflection earn its keep despite internal reasoning?"

### When explicit self-critique earns its cost

Use external reflection when:

- The task has a clear, checkable failure signal (a test suite passes or fails, an API returns an error, a human rates the answer as wrong or right).
- A second or third attempt, informed by the failure, is likely to succeed where the first attempt failed.
- The task is worth retrying: high enough value that the extra model calls are justified.

Do not add reflection when:

- The task has no clear failure signal (e.g., "write a summary" with no test or rubric to check correctness).
- The failure is not the model's fault (e.g., a required API is down, not something the model can fix).
- The first attempt is already very likely to succeed and failures are rare.

### Designing reflection signals

Reflection is only as good as the signal it receives. If you tell the harness "this task failed because the user said so," the reflection might generate "I tried to write a summary but the user did not like it." That is too vague for the next attempt to act on. A better failure signal would be "the summary is missing the customer's stated requirements" or "the summary is longer than the 100-word limit."

When building a reflecting agent, design the failure check carefully. What does success look like? What concrete evidence proves failure? That evidence is what the reflection will react to.

## Practice

1. ▢ An agent writes code to solve a LeetCode problem. The test suite runs the code and reports either "All tests pass" or prints a specific failing test case. After a failure, the harness generates a reflection and runs the agent again with the reflection in context. Why is this a good fit for Reflexion?

<details markdown="1"><summary>Check</summary>

There is a clear failure signal: the test suite. The reflection can say "Test case [input] expected [output] but I produced [wrong_output]." That is concrete and actionable. The model can read this in the next attempt and specifically debug the failing case. Code generation is also iterative by nature; multiple attempts are expected and worth the cost.

</details>

2. ▢ An agent is asked to write product copy for an e-commerce site. The agent produces copy and submits it. There is no test suite, no rubric, and no automatic check. A human marketing manager reads it and says "This is not right, try again." Would Reflexion help here?

<details markdown="1"><summary>Hint</summary>

What feedback does the reflection loop have to work with? Is it concrete enough for the next attempt to act on?

</details>

<details markdown="1"><summary>Check</summary>

Reflexion would not help much. The feedback "This is not right" is too vague. The reflection would be something like "The marketing manager did not like my copy." The agent's next attempt would have no concrete change to make. A better approach would be to get specific feedback from the manager (e.g., "Make it shorter and add a price comparison") and include that in the next prompt, rather than relying on a reflection loop.

</details>

3. ▢ A model with extended internal reasoning can now self-correct during its own reasoning phase. Which of the following is still an advantage of an explicit external reflection loop in this context?

    - a) External reflection is always faster than internal reasoning.
    - b) External reflection can incorporate information (like a tool error or test failure) that only exists after the model's first attempt.
    - c) External reflection is cheaper in context tokens than internal reasoning.
    - d) External reflection works with all models, even those without internal reasoning capability.

<details markdown="1"><summary>Check</summary>

**b)** Internal reasoning happens before any tool runs, so it cannot observe a tool's actual result or a test failure. An explicit reflection loop can incorporate that information, so it provides value even with models that have internal reasoning. a) is false, internal reasoning is often faster than running an extra loop. c) is false, external reflection consumes context tokens (the reflection text and the next attempt both take space). d) is true but not the key insight; the question is about what reflection adds when internal reasoning is present.

</details>

4. ▢ You are building an agent that processes job applications. The harness has a clear signal: approved or rejected by a hiring manager. You want to use Reflexion to improve the agent's decisions over multiple attempts. What should each reflection capture to be useful for the next attempt?

<details markdown="1"><summary>Check</summary>

The reflection should capture the specific reasons for the rejection or approval, if available. For example, "Application rejected because: missing required certification. Next attempt, check for required certifications before approving." Or "Application approved because: strong experience in required skills and good communication in cover letter." The reflection should be specific to the application, not generic advice. This gives the next attempt something concrete to act on. If the hiring manager provides only a yes/no with no reasons, the reflection is less actionable.

</details>

## Real-world reps

- [ ] Take a task that involves iteration and has a clear pass/fail signal (e.g., solving a problem, passing a test, meeting a rubric). Implement a reflecting agent loop: attempt, check failure, generate reflection, retry with reflection in context. Run it five times and count how many attempts the agent needs with reflection versus without. Record the difference.
- [ ] Find a task in your work that has no clear failure signal (e.g., writing, design, creative work). Describe how you would add one (e.g., "compare against a rubric," "have a peer review," "check specific criteria"). Would adding a failure signal make a reflecting agent useful, or is the task better handled with a human loop?
- [ ] Tomorrow: Read a Reflexion trajectory (from a paper, a blog post, or something you built). Identify the reflection text. Would the reflection have been useful if the model had internal reasoning? Why or why not?

## Going further

- [Paper: "Reflexion: Language Agents with Verbal Reinforcement Learning", Shinn et al., 2023](https://arxiv.org/abs/2303.11366)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
