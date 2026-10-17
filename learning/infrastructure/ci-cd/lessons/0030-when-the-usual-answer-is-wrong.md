---
title: "30. When the Usual Answer Is Wrong"
description: Say when continuous deployment, a canary or a pipeline default is the wrong call, and settle a disputed behaviour from the workflow syntax reference
type: lesson
---

# Lesson 30. When the Usual Answer Is Wrong

**Mission link:** The mission ends with saying when the usual delivery answer is the wrong one, and settling a dispute from the workflow syntax reference. Judgment here means a decision you can defend with a cost and a source, not a rule you remember. Every practice in this track has a case where it stops paying.
**Primary source:** [Docs: "Workflow syntax for GitHub Actions", GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
**Prerequisites:** [Lesson 1](0001-what-ci-and-cd-promise.md), [Lesson 10](0010-making-a-pipeline-fast.md), [Lesson 19](0019-deployment-strategies.md), [Lesson 20](0020-rollback-and-roll-forward.md), [Lesson 28](0028-reviewing-a-pipeline.md), [Continuous delivery](../GLOSSARY.md), [Continuous deployment](../GLOSSARY.md), [Canary](../GLOSSARY.md), [Concurrency group](../GLOSSARY.md), [Matrix](../GLOSSARY.md)

## Warm-up

1. ▢ What is the difference between continuous delivery and continuous deployment, in one sentence?

<details markdown="1"><summary>Check</summary>

Continuous delivery keeps the mainline releasable so that any passing commit can be deployed at the push of a button. Continuous deployment removes the button and deploys every passing change automatically. Fowler's [Continuous Delivery](https://martinfowler.com/bliki/ContinuousDelivery.html) page says you must be doing delivery to do deployment, not the reverse (lesson 1).

</details>

2. ▢ A canary reports "no errors". What two things must be true for that to mean the release is fine?

<details markdown="1"><summary>Check</summary>

It must have seen enough traffic to be a representative sample, and its metrics must be compared against a control running the old version, not read in isolation ([Canarying Releases](https://sre.google/workbook/canarying-releases/), lesson 19).

</details>

3. ▢ What does `cancel-in-progress: true` do to a concurrency group, and what happens without it?

<details markdown="1"><summary>Check</summary>

With it, a newer run cancels the run that is already in progress. Without it, the running run finishes, and a newer queued run waits as pending, replacing any older pending one (lesson 10, [workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)).

</details>

## Know this

### A default is a bet about the common case

Every practice in this track, from "deploy every merge" to `ubuntu-latest`, was written for a typical team. Judging one means naming the case it was built for, how yours differs, what the alternative costs, and what would change the answer. A rule you cannot argue for is a habit, and it is wrong the first time the case changes.

The sections below are judgment, not fact. The documentation gives the mechanisms. The decision rests on your service, your tests and your people, so each answer ends with what would flip it.

### When continuous deployment is wrong

Continuous deployment deploys every passing change with no human decision in between. That is only as safe as the evidence the pipeline gathers and the speed at which a bad change can be undone. It is the wrong call when any of these hold:

|Signal|Why it breaks continuous deployment|What to do instead|
|---|---|---|
|The tests cannot see what breaks in production|Green means "the tests I have passed", and nothing else checks the change|Continuous delivery: deploy on a button, and improve the tests|
|A bad release is expensive to undo|A migration or an irreversible side effect makes rollback unsafe (lessons 20 and 21)|Gate the risky changes and use expand and contract for the rest|
|A person's decision is a real control|A regulated or audited change needs a recorded approval|Keep the approval as an environment protection rule (lesson 17)|
|The release channel is slow or outside your control|You cannot ship at the speed of merges|Deliver every commit, release on the channel's schedule|

Two ideas lower the bar, and they are the usual way teams earn continuous deployment: separating deploy from release with a feature flag (lesson 20), and a deploy that is cheap to reverse. The delivery metrics from [DORA](https://dora.dev/guides/dora-metrics-four-keys/) are the neutral judge. Deployment frequency and lead time measure speed, and change fail rate and recovery time measure the cost of the bets. Fowler's page also notes that a business may choose a slower rate of deployment while still doing delivery. What would change the answer: strong tests, flags and a rehearsed rollback move you toward deploying every merge, and a missing one of those moves you away.

### When a canary is wrong

A canary is a measurement, so it works only when there is something to measure. The Site Reliability Workbook says a canary should be sizeable and last long enough to be representative, that terminating it after a handful of queries gives no useful signal for varied traffic, and that the metrics must indicate problems and be compared against a control ([Canarying Releases](https://sre.google/workbook/canarying-releases/)). That gives the cases where it is the wrong tool:

- **Low traffic.** At forty requests an hour, a five percent canary sees two. It cannot tell a regression from noise, however well the automation is wired.
- **No baseline or no metric.** Without a control version and a metric that reflects user pain, the "analysis" is a person looking at a graph.
- **Two versions cannot run side by side.** A schema or a message format that the old version cannot read makes a partial rollout dangerous (lesson 21).
- **The risk is not in request handling.** A nightly batch job or a configuration change may not meet canary traffic at all.

The alternatives each cost something. Blue-green gives a switch back, and costs a second full environment. A rolling deploy with good readiness checks costs little, and tells you only what the checks measure. A flag lets you expose a change to staff first. What would change the answer: enough traffic, a metric you trust and a control group make a canary the cheapest real evidence there is.

### When a pipeline default is wrong

|Default|Built for|When it is wrong|Instead, and what it costs|
|---|---|---|---|
|`fail-fast: true`, the default for a matrix|Stopping early to save minutes|You need the whole picture: a library that supports four Python versions, where one failing leg hides the other three|`fail-fast: false`: every leg runs, so you spend more minutes, and pair it with `continue-on-error` for an experimental leg only|
|`cancel-in-progress: true`, copied everywhere|Cancelling superseded pull request runs|On a deploy or the default branch, where cancelling a running job leaves an environment half updated|No cancel: the running deploy finishes, and the next run waits, which costs a slower queue|
|`ubuntu-latest`|Always testing on a current image|You need a reproducible build or a bisect, since an image update has no commit to blame|A named image such as `ubuntu-24.04`: stable until you move it, and you carry the work of moving it|

The facts behind the table, from the workflow syntax reference: `fail-fast` defaults to true and cancels all in-progress and queued jobs in the matrix if any one fails. By default only the *pending* run in a concurrency group is replaced, and the running one continues unless you set `cancel-in-progress`. The hosted runner docs say the `-latest` images are the latest stable images and might not be the newest operating system version ([hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)). What would change each answer: a matrix whose legs are slow and equivalent keeps fail-fast, pull request runs keep cancelling, and a team that tests on whatever is current by design keeps `-latest`.

### Settling a dispute from the source

When two engineers disagree about what a workflow does, the answer is written down, and the order of trust is fixed:

1. **The workflow syntax reference** for what a key is, its default and its allowed values.
2. **The events, contexts and expressions references** for what an event delivers and what a context holds.
3. **The how-to page** for the feature, for behaviour and the examples.
4. **A ten-line experiment** on a throwaway run: a workflow with `on: workflow_dispatch` and a few `echo` steps turns an opinion into an observation.

Memory, a blog post and "everyone does it this way" are not on the list, and neither is a model's recollection. Write the claim down as something that can be false, find the line that settles it, and put the link in the pull request.

Here is one. A colleague says: "If a workflow has both `branches` and `paths` filters on `pull_request`, it runs when either one matches." The syntax reference says that if you define both `branches` and `paths`, the workflow runs only when both filters are satisfied. So the claim is false. Check it on a throwaway workflow if the stakes justify the five minutes.

## Practice

1. ▢ Which service is the strongest candidate for continuous delivery with a gate, rather than continuous deployment?

    - a) A stateless internal tool with fast tests and instant rollback
    - b) A payments service whose changes need a recorded human approval
    - c) A documentation site rebuilt from Markdown with no state
    - d) A feature-flagged web frontend with strong monitoring and quick rollbacks

<details markdown="1"><summary>Check</summary>

**b)** The approval is a real control, not a formality the pipeline can replace, so deploys wait for a person. (a), (c) and (d) each have cheap rollback and little to lose, which is when continuous deployment pays. It is a judgment: even for (b), every commit can still be deployed to an environment that has no approval, so only production waits.

</details>

2. ▢ A service handles forty requests an hour. A teammate proposes a five percent canary with automatic comparison of error rates. What is wrong, and what do you offer instead?

<details markdown="1"><summary>Hint</summary>

How many requests will the canary serve in the first ten minutes?

</details>

<details markdown="1"><summary>Check</summary>

The canary sees about two requests an hour, which is a handful of queries, so its error rate says nothing about the release. Offer blue-green with smoke tests and a quick switch back, which costs a second environment, or a flag that shows the change to staff first. A larger share for longer is possible, but then more users carry the risk. Say what would change your mind: more traffic, or synthetic load that resembles it.

</details>

3. ▢ Predict, then run. In `ci-cd-practice`, add the workflow below and trigger it from the Actions tab. What result does each job get, and what one line makes `b` run anyway? Then find the sentence in the workflow syntax reference that settles it.

    ```yaml
    name: dispute

    on: workflow_dispatch

    jobs:
      a:
        if: ${{ false }}
        runs-on: ubuntu-latest
        steps:
          - run: echo a
      b:
        needs: a
        runs-on: ubuntu-latest
        steps:
          - run: echo b
    ```

<details markdown="1"><summary>Hint</summary>

Open `jobs.<job_id>.needs` in the reference and read what it says about a job that is skipped.

</details>

<details markdown="1"><summary>Check</summary>

Both are skipped. The reference says that if a job fails or is skipped, all jobs that need it are skipped unless they use a conditional expression that causes them to continue. Adding `if: ${{ always() }}` to `b` makes it run regardless of `a`. This is the same mechanic as the gate job in lesson 26, and the reason the gate needs `always()`.

</details>

4. ▢ A matrix tests four Python versions of a library. One leg fails on the oldest version while the other three are still running. What happens by default, why can that mislead you, and what do you change?

<details markdown="1"><summary>Check</summary>

`fail-fast` defaults to true, so the failure cancels the in-progress and queued legs, and the run shows one real failure and three cancelled legs with no result. You do not learn whether the other versions pass, which is the question a library's maintainers need answered. Set `fail-fast: false`. The cost is the minutes the remaining legs take, and for a matrix of slow, equivalent legs the default is still the better call.

</details>

5. ▢ `deploy.yml` has `concurrency: group: deploy` and `cancel-in-progress: true`, copied from `ci.yml`. Two pushes land on `main` thirty seconds apart. What can go wrong, and what do you write instead?

<details markdown="1"><summary>Hint</summary>

What does `cancel-in-progress` act on: the pending run, or the running one?

</details>

<details markdown="1"><summary>Check</summary>

The second push cancels the first deploy while it is running, which can leave an environment half updated, for example a migration applied and the new version only partly rolled out. Remove `cancel-in-progress` from the deploy group: the first deploy finishes, and the second waits as the pending run. The cost is a short queue. For pull request CI, cancelling is still right, since nobody wants the result of a superseded commit.

</details>

6. ▢ A colleague says `timeout-minutes` defaults to 60, so there is no need to set it. Settle it, and say what you would do regardless.

<details markdown="1"><summary>Check</summary>

The reference says `jobs.<job_id>.timeout-minutes` is the maximum number of minutes to let a job run before GitHub cancels it, with a default of 360. A hung job can therefore hold a runner for six hours. Set `timeout-minutes` on every job to a little above its normal duration (lesson 10), so a hang fails fast. The default is wrong in the other direction too: a legitimately long job needs a higher value, and the reference caps a step at 360 as well.

</details>

7. ▢ Someone claims that for a `pull_request` path filter, GitHub looks only at the files in the latest commit. Write the claim so it can be false, and find the line that settles it.

<details markdown="1"><summary>Check</summary>

The claim: "A path filter on `pull_request` is evaluated against the files changed in the newest commit." The reference says GitHub builds the changed-file list with a three-dot diff for pull requests, a comparison between the latest version of the topic branch and the commit where it was last synced with the base branch. So it is the whole pull request relative to that point, not the last commit. A one-line follow-up commit therefore does not narrow the filter.

</details>

## Real-world reps

- [ ] Run practice item 3 and read the reference sentence aloud next to the result. Then add `if: ${{ always() }}` to `b` and run it again.
- [ ] Add a three-leg matrix to a scratch workflow where leg 1 exits non-zero immediately and the others sleep for thirty seconds. Run it with the default, then with `fail-fast: false`, and compare what each run tells you.
- [ ] Take a pipeline you work on and write down one default it uses, the case it was built for, how your case differs, and what replacing it costs. If you cannot say what it costs, you have not yet made the case.
- [ ] Tomorrow: without notes, name the four signals against continuous deployment, the four cases where a canary is the wrong tool, and the four sources in the order you trust them.

## Going further

- [Pipeline Review Checklist](../reference/pipeline-review-checklist.md)
- [Docs: "Workflow syntax for GitHub Actions", GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [Article: "Continuous Delivery", Martin Fowler](https://martinfowler.com/bliki/ContinuousDelivery.html)
- [Book chapter: "Canarying Releases", The Site Reliability Workbook, Google](https://sre.google/workbook/canarying-releases/)
- [Guide: "DORA's software delivery metrics", DORA](https://dora.dev/guides/dora-metrics-four-keys/)
- [Resources](../RESOURCES.md)

---

That closes the arc. You can now take a change from a commit to production through a pipeline you own, give that pipeline only the access it needs, deploy in a way that limits the damage and roll back when it does not, review someone else's pipeline by naming what it costs, change a shared workflow without breaking its callers, and say when the usual answer is wrong. The tool will change, and Jenkins and GitLab CI spell every key differently, but the three habits carry over: name the cost of a choice, change an interface by adding before you remove, and settle a dispute from the primary source before you settle it by memory.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
