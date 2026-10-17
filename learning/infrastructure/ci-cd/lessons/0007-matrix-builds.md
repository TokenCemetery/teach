---
title: "7. Matrix Builds"
description: Run one job across versions and platforms with a matrix, and control what fail-fast, include and exclude do to the run
type: lesson
---

# Lesson 7. Matrix Builds

**Mission link:** The mission says to prove every change builds and passes on what you ship to. A matrix runs the same tests on every runtime and platform you support without copying the job, and the options around it decide how much of the picture you see when something fails.
**Primary source:** [Docs: "Running variations of jobs in a workflow", GitHub](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations)
**Prerequisites:** [Lesson 4](0004-jobs-steps-and-runners.md), [Lesson 5](0005-actions-expressions-and-outputs.md), [Lesson 6](0006-build-and-test-stages.md), [Matrix](../GLOSSARY.md), [Job](../GLOSSARY.md), [Runner](../GLOSSARY.md)

## Warm-up

1. ▢ Does a `needs` dependency or a matrix change how many runners a job uses? What does each job in a workflow get?

<details markdown="1"><summary>Check</summary>

Each job gets its own fresh runner, whatever it needs or however it was produced (lesson 4). `needs` only orders jobs. A matrix, as this lesson shows, produces several jobs from one definition, and each of them gets its own runner too.

</details>

2. ▢ Which context carries the current value of a matrix variable, and where can an expression read it?

<details markdown="1"><summary>Check</summary>

The `matrix` context, for example `matrix.python-version` (lesson 5). It is available in the job's `runs-on`, `name` and `steps`, because the job is expanded before it runs ([Contexts reference](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts)).

</details>

3. ▢ Why does the `integration` job from lesson 6 not belong in a matrix that includes `windows-latest`?

<details markdown="1"><summary>Check</summary>

It uses a service container, and service containers need a Linux runner: on GitHub-hosted runners that means an `ubuntu-*` label ([Using Docker service containers](https://docs.github.com/en/actions/tutorials/use-containerized-services/use-docker-service-containers)). The unit tier has no such constraint, so that is where the matrix goes.

</details>

## Know this

### One definition, many jobs

A [matrix](../GLOSSARY.md) lists values for one or more variables, and GitHub Actions creates one job for every combination ([Docs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations)). The practice repository claims to support three Python versions, and a service that runs on Linux in production should at least be tested on the platform developers use. Here is the `unit` job from lesson 6 as a matrix:

```yaml
  unit:
    needs: check
    name: unit (${{ matrix.os }}, py${{ matrix.python-version }})
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ["3.12", "3.13", "3.14"]
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements.txt
      - run: pytest -m "not integration"
```

Two variables with two and three values make six jobs, and `runs-on: ${{ matrix.os }}` and the `setup-python` input both read from the `matrix` context. The `name` key can use the `matrix` context too ([Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)), which gives each job a readable label in the run and in the checks list.

Quote version numbers. YAML reads an unquoted `3.10` as the number 3.1, so a matrix that lists `[3.9, 3.10]` asks for Python 3.9 and 3.1. The `setup-python` docs write matrix versions as quoted strings for this reason, for example `['3.9', '3.10', '3.11']` ([Advanced usage](https://github.com/actions/setup-python/blob/main/docs/advanced-usage.md)).

A matrix generates at most 256 jobs per workflow run, on hosted and self-hosted runners alike ([Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [Actions limits](https://docs.github.com/en/actions/reference/limits)). By default GitHub runs as many as runner availability allows, and `strategy.max-parallel` lowers that number when you need to be gentler on a shared resource.

Jenkins expresses this with a `matrix` directive in declarative pipelines and GitLab CI with `parallel: matrix`. The idea is the same: one definition, a job per combination ([Jenkins](https://www.jenkins.io/doc/book/pipeline/syntax/#declarative-matrix), [GitLab](https://docs.gitlab.com/ci/yaml/)).

### Include and exclude

A full grid is rarely what you want. Two keys shape it:

- `exclude` removes combinations. An excluded entry only has to match partially: `{os: windows-latest}` removes every combination on Windows.
- `include` adds to the matrix. Each entry has its keys merged into every original combination it can join without overwriting an original value. If it cannot join any combination without overwriting, it becomes a new combination.

All `include` entries are processed after `exclude`, so `include` can add back something that was excluded ([Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)). A matrix with no variables of its own and only `include` entries runs exactly those entries.

```yaml
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ["3.12", "3.13", "3.14"]
        exclude:
          - os: windows-latest
            python-version: "3.12"
        include:
          - os: ubuntu-latest
            python-version: "3.13"
            coverage: true
```

This runs five jobs: the six combinations minus Windows with 3.12. The `include` entry joins the existing Ubuntu and 3.13 job and adds a `coverage` value to it without creating a sixth. A step can then act on it, such as `if: ${{ matrix.coverage }}`, so one job does extra work the others skip.

### What fail-fast does

`strategy.fail-fast` defaults to `true`. When any job in the matrix fails, GitHub cancels every in-progress and queued job in the matrix ([Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)). That saves minutes and gets the first red result quickly, but it hides the shape of the failure: you cannot tell whether one platform or all of them are broken, because the others never finished.

|Setting|Effect|Choose it when|
|---|---|---|
|`fail-fast: true` (default)|The first failure cancels the rest of the matrix|Any red result means you will fix the code before anything else|
|`fail-fast: false`|Every job runs to its end|You need to know which cells fail to diagnose, or runs are cheap|
|`continue-on-error: true` on a job|That job may fail without failing the run or cancelling siblings|A cell is experimental, such as a pre-release version|

`continue-on-error` is per job, and the docs' pattern drives it from the matrix, for example `continue-on-error: ${{ matrix.experimental }}` with an `experimental: true` entry added by `include`. The two settings combine: a failing job with `continue-on-error: false` still cancels the matrix under `fail-fast: true`, while a failing experimental job affects nobody.

A matrix is also a cost multiplier. Five jobs each installing dependencies is five installs, and lesson 8 makes each of them cheaper. A matrix cell should exist because a real user is on it, not because the grid was easy to write.

## Practice

1. ▢ A matrix has `os` with three values and `python-version` with three values, an `exclude` of `{os: ubuntu-24.04, python-version: "3.12"}`, an `exclude` of `{os: windows-latest}`, an `include` of `{os: ubuntu-latest, python-version: "3.11"}`, and an `include` of `{os: ubuntu-latest, python-version: "3.13", coverage: true}`. The OS values are `ubuntu-latest`, `ubuntu-24.04` and `windows-latest`, and the Python values are `3.12`, `3.13` and `3.14`. How many jobs run?

<details markdown="1"><summary>Hint</summary>

Count the full grid, subtract each exclusion (the second removes a whole operating system), then decide for each include whether it can join an existing combination without overwriting a value.

</details>

<details markdown="1"><summary>Check</summary>

Six. The grid has 9. The first exclude removes 1 (`ubuntu-24.04` with 3.12) and the second removes the 3 Windows combinations, leaving 5. The `python-version: "3.11"` include cannot join any original combination without overwriting `python-version`, so it becomes a sixth job. The `coverage` include matches Ubuntu with 3.13 exactly, so it adds a key to that job without making a new one.

</details>

2. ▢ With the default settings, one matrix job fails. What happens to the sibling jobs?

    - a) Only the queued siblings get cancelled
    - b) Every sibling keeps running to completion
    - c) Queued and running siblings get cancelled
    - d) The failed job is retried automatically

<details markdown="1"><summary>Check</summary>

**c)** `fail-fast` defaults to `true` and cancels every in-progress and queued job in the matrix. (a) forgets the running ones. (b) is the behaviour of `fail-fast: false`. (d) nothing in the matrix settings retries a failed job.

</details>

3. ▢ Predict, then run. Add this test to `ci-cd-practice` on a branch, push it, and open a pull request with the five-job matrix from this lesson.

    ```python
    import sys


    def test_posix_only():
        assert sys.platform != "win32"
    ```

    What do the five jobs show with the default settings? Then add `fail-fast: false` under `strategy`, push again, and say what changes.

<details markdown="1"><summary>Hint</summary>

Only the two Windows jobs can fail. Ask what fail-fast does to a job that is still running when the first failure lands.

</details>

<details markdown="1"><summary>Check</summary>

With the default, the two Windows jobs fail, and any Ubuntu job still running or queued at that moment shows as cancelled. Which Ubuntu jobs finished first depends on timing, so the exact mix of green and cancelled varies between runs. With `fail-fast: false`, all five jobs run: three Ubuntu jobs pass and two Windows jobs fail. Now the pattern is visible, one platform is broken and the versions are fine, which is the information you needed. The cost is that the run is as slow as its slowest job, even though it was already red.

</details>

4. ▢ Debug this. A teammate widens the matrix to cover Python 3.10, and one job fails in `setup-python`. That job is named `unit (ubuntu-latest, py3.1)`. Find the bug.

    ```yaml
    matrix:
      os: [ubuntu-latest]
      python-version: [3.10, 3.12, 3.13]
    ```

<details markdown="1"><summary>Hint</summary>

Look at the job name. Which number ended up in the `matrix` context?

</details>

<details markdown="1"><summary>Check</summary>

YAML reads the unquoted `3.10` as the number 3.1, so the job asks for Python 3.1, which is not what was meant (the failing job is the one named `py3.1`). Quote every version: `["3.10", "3.12", "3.13"]`. The name template made the mistake visible, which is a good reason to put matrix values in job names. Note that `3.12` and `3.13` are unaffected: they have no trailing zero to lose, so the bug only appears for versions such as 3.10.

</details>

5. ▢ A required status check is configured for the job called `unit`. After you add the matrix, merges are blocked and nothing ever turns green. What changed, and what would you do?

<details markdown="1"><summary>Check</summary>

Required status checks match a job by its name, and the job no longer has that name: the matrix produced jobs with names such as `unit (ubuntu-latest, py3.13)`, and nothing is called `unit` anymore, so the required check stays pending (lesson 26 covers this in depth). Update the required checks to the new job names, or add one final job that `needs` the whole matrix and require only that. Pick the second when the matrix will change often, since the required name then never changes.

</details>

## Real-world reps

- [ ] Turn the `unit` job of `ci-cd-practice` into the five-job matrix from this lesson, push, and read the run. Confirm each job's name shows its operating system and Python version.
- [ ] Run practice item 3 on a branch and compare the default result with `fail-fast: false`. Write down which one you would want on a pull request and which on a nightly run, and why.
- [ ] Look at a repository you work in and list which platform and runtime versions its users run. Compare that with the versions its pipeline tests, and note any cell that exists with no user behind it.
- [ ] Tomorrow: without notes, say what `include` does that `exclude` cannot, state the default of `fail-fast`, and name the key that lets one matrix job fail without failing the run.

## Going further

- [Fast Feedback](../reference/fast-feedback.md)
- [Docs: "Running variations of jobs in a workflow", GitHub](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations)
- [Docs: "Workflow syntax for GitHub Actions", GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), the `strategy` keys with their defaults
- [Docs: "Actions limits", GitHub](https://docs.github.com/en/actions/reference/limits)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
