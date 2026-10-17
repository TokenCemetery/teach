---
title: Fast Feedback
description: Stage ordering, matrices, cache keys, flaky-test handling, concurrency and timeouts
type: reference
---

# Fast Feedback: Stages, Matrices, Caches, Flaky Tests, Concurrency and Timeouts

Stage 3 compressed for lookup. [Lesson 6](../lessons/0006-build-and-test-stages.md) covers stage ordering and service containers, [lesson 7](../lessons/0007-matrix-builds.md) matrices, [lesson 8](../lessons/0008-caching.md) caching, [lesson 9](../lessons/0009-flaky-tests.md) flaky tests, and [lesson 10](../lessons/0010-making-a-pipeline-fast.md) the critical path, concurrency and timeouts.

## Stage ordering

|Rule|Detail|
|---|---|
|Cheapest and most likely to fail first|Check (parse, lint), then unit, then integration|
|`needs` orders jobs|A job whose needed job fails or is skipped is skipped, unless it has a condition that lets it continue|
|Chained jobs cost the sum|Three chained jobs of 12, 38 and 55 seconds take 105 seconds, in parallel 55 seconds|
|Keep the cheap gate, parallelise the rest|`check` first, then `unit` and `integration` both `needs: check`: 12 + 55 = 67 seconds|
|Separate tiers with a marker|`pytest -m "not integration"` and `pytest -m integration`, markers registered in `pytest.ini`|

## Service containers

|Situation|How the job reaches the service|
|---|---|
|Job runs directly on the runner|`localhost:<port>`, and `ports` must map it, for example `- 5432:5432`|
|Job runs in a container|The service label is the hostname, no `ports` needed|
|Runner|Linux only: an `ubuntu-*` label on hosted runners|
|Readiness|Pass `--health-cmd pg_isready` with interval, timeout and retries through `options`|
|Lifetime|Created fresh for each job, destroyed when it ends|

```yaml
services:
  postgres:
    image: postgres:17
    env:
      POSTGRES_PASSWORD: postgres
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
    ports:
      - 5432:5432
```

## Matrices

|Key|Effect|
|---|---|
|`strategy.matrix.<var>: [..]`|One job per combination of the variables|
|`exclude`|Removes combinations, and a partial match is enough|
|`include`|Merges keys into combinations it can join without overwriting, otherwise adds a new one, and runs after `exclude`|
|`fail-fast` (default `true`)|The first failure cancels all in-progress and queued jobs in the matrix|
|`continue-on-error`|Per job: it may fail without failing the run or cancelling siblings|
|`max-parallel`|Lowers how many matrix jobs run at once|
|Limit|256 jobs per workflow run|

- Quote versions: `["3.10", "3.12"]`, because YAML reads an unquoted `3.10` as 3.1.
- Put matrix values in `name` so each cell is readable: `name: unit (${{ matrix.os }}, py${{ matrix.python-version }})`.
- `matrix` is available in `runs-on`, `name`, `with` and `if`.
- A matrix renames the jobs, so a required status check that names the old job stops matching ([lesson 26](../lessons/0026-monorepos-and-path-filters.md)).

## Cache keys

```yaml
- uses: actions/cache@v6
  with:
    path: ${{ steps.pip-dir.outputs.dir }}
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

|Question|Answer|
|---|---|
|What goes in the key|What the cached files depend on: `runner.os` and `hashFiles` of the lockfile|
|Exact match on `key`|Cache hit, `cache-hit` is `true`|
|Prefix match on a restore key|Most recent matching cache restored, `cache-hit` is `false`|
|Is a cache saved|At job end, on success, when the exact key was not found|
|Can a cache be changed|No: a new key makes a new cache|
|Key length|Up to 512 characters|
|Shortcut for pip|`actions/setup-python` with `cache: pip`, off by default|

|Run|Can restore caches from|
|---|---|
|Any branch run|Its own branch, then the default branch|
|A pull request run|Also its base branch|
|Any run|Never child or sibling branches, never other tags|
|A `pull_request` run saves|To the merge ref, so only re-runs of that pull request restore it|

|Limit|Value|
|---|---|
|Unused entry removed|After 7 days without access|
|Total size|10 GB per repository by default, least recently accessed evicted first|

|Never put in a cache|Why|
|---|---|
|Secrets|Anyone who can open a pull request can read a cache|
|The artifact you ship|A cache can be missing, evicted or stale: use an artifact ([lesson 11](../lessons/0011-artifacts.md))|
|A test result|It turns a stale answer into a green check|

Low-trust triggers such as `pull_request_target`, `issue_comment` and `workflow_run` get read-only access to the default branch's caches. `push`, `workflow_dispatch` and `schedule` can write there.

## Flaky tests

|Step|Action|
|---|---|
|Confirm|Re-run failed jobs: the re-run keeps the same `GITHUB_SHA`, so a pass proves the code did not change the outcome|
|Reproduce|Loop the one test, shuffle order with `pytest-randomly`, replay with `--randomly-seed=<seed>`|
|Fix the cause|Wait for the condition not a sleep, isolate state with `monkeypatch`, fake the clock, seed randomness|
|If it cannot be fixed soon|Quarantine: marker, separate non-required job, owner, issue, size or age limit|
|Retries|Triage only: report every retried test so the flake is counted|

- A suite of `N` independent tests with a per-test flake rate `p` is green with probability `(1 - p)^N`: 50 tests at 1% is about 60%.
- Quarantine can mask a real race, so keep the quarantine job running and visible.
- `continue-on-error: true` lets the run pass when that job fails. The job must not be a required check.

## Concurrency and timeouts

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  integration:
    timeout-minutes: 10
```

|Setting|Behaviour|
|---|---|
|Group|One running and one pending run or job per group, name case insensitive|
|Default|A new run waits as pending and replaces an older pending run, the running one continues|
|`cancel-in-progress: true`|The running one is cancelled too|
|`cancel-in-progress` as an expression|Cancel on pull requests, finish on `main`|
|`queue: max`|Up to 100 pending, cannot combine with `cancel-in-progress: true`|
|Group contexts|`github`, `inputs` and `vars` only|
|Unique per workflow|Include `github.workflow`, or workflows cancel each other|
|`timeout-minutes` (job)|Default 360, which is also the hosted runner job limit|
|`timeout-minutes` (step)|Per step, maximum 360|

|Number to know|Value|
|---|---|
|Critical path|The longest chain of `needs`, which is the wait, not total minutes|
|Matrix jobs per run|256|
|Workflow run time|35 days including waiting and approval|

## Sources

- [Docs: "Using Docker service containers", GitHub](https://docs.github.com/en/actions/tutorials/use-containerized-services/use-docker-service-containers)
- [Docs: "Creating PostgreSQL service containers", GitHub](https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers)
- [Docs: "Running variations of jobs in a workflow", GitHub](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations)
- [Docs: "Workflow syntax for GitHub Actions", GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [Docs: "Dependency caching reference", GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)
- [Repository: actions/cache, GitHub](https://github.com/actions/cache)
- [Repository: actions/setup-python, GitHub](https://github.com/actions/setup-python)
- [Article: "Flaky Tests at Google and How We Mitigate Them", John Micco, Google Testing Blog](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)
- [Docs: "Re-running workflows and jobs", GitHub](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs)
- [Docs: "Control the concurrency of workflows and jobs", GitHub](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)
- [Docs: "Actions limits", GitHub](https://docs.github.com/en/actions/reference/limits)
- [Resources](../RESOURCES.md)
