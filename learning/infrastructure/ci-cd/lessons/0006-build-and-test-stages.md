---
title: "6. Build and Test Stages"
description: Order lint, build, unit and integration stages so the cheapest failure comes first, with service containers for the tests that need a database
type: lesson
---

# Lesson 6. Build and Test Stages

**Mission link:** The mission says to prove every change builds and passes its tests in minutes. How you order the stages decides what a failure costs: a typo should fail in seconds, and only a change that survives the cheap checks should earn the expensive ones.
**Primary source:** [Docs: "Using Docker service containers", GitHub](https://docs.github.com/en/actions/tutorials/use-containerized-services/use-docker-service-containers)
**Prerequisites:** [Lesson 3](0003-triggers-and-events.md), [Lesson 4](0004-jobs-steps-and-runners.md), [Lesson 5](0005-actions-expressions-and-outputs.md), [Job](../GLOSSARY.md), [Step](../GLOSSARY.md), [Runner](../GLOSSARY.md), [Critical path](../GLOSSARY.md)

## Warm-up

1. ▢ Two jobs in one workflow, `unit` and `integration`, must run in that order. Which key does that, and what happens to `integration` when `unit` fails?

<details markdown="1"><summary>Check</summary>

`needs: unit` on the `integration` job (lesson 4). Without it both jobs start at once on separate runners. When a needed job fails or is skipped, every job that needs it is skipped too, unless it carries a conditional expression that lets it continue ([Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)).

</details>

2. ▢ A `pull_request` event starts a run. Which commit does the runner check out, and why does that matter for a test result?

<details markdown="1"><summary>Check</summary>

The last merge commit on the pull request's merge branch, `refs/pull/PULL_REQUEST_NUMBER/merge`, which is the head of the branch merged into its base. `GITHUB_SHA` holds that merge commit, not the tip of your branch ([Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)). The test result therefore describes what main would look like after the merge, which is the thing continuous integration cares about (lesson 3).

</details>

3. ▢ Continuous integration promises that a broken mainline is fixed at once. Why does the speed of the failing stage matter to that promise?

<details markdown="1"><summary>Check</summary>

The signal is only useful while the author still remembers the change. A failure that arrives after twenty minutes gets read after the author has moved on, so the fix slows down and the mainline stays broken longer (lesson 1). This lesson is about getting the failure to the author as early and as cheaply as the pipeline can.

</details>

## Know this

### Fail on the cheapest problem first

A pipeline is a series of checks, and each one answers a different question at a different price. The rule is simple: run the check that is cheapest and most likely to fail first, and make the expensive checks wait for it. A syntax error should never cost you a database startup.

For the practice repository the stages, cheapest first, are:

|Stage|Question|Typical cost|
|---|---|---|
|Check|Does the code parse and lint clean?|Seconds, no dependencies to install|
|Unit|Does each function behave, with nothing external?|Tens of seconds|
|Integration|Does the code work against a real database?|A minute or more: a service container to start|

These numbers are illustrative, but the shape is the point: cost rises as you go down the table, and so does the fraction of failures that are not simple mistakes. Stage ordering is a bet that the cheap, common failures are caught before the slow, rare ones are paid for.

```mermaid
flowchart LR
    A["check<br>seconds"] -->|passes| B["unit<br>tens of seconds"]
    B -->|passes| C["integration<br>a minute or more"]
    A -->|fails| X["integration and unit skipped"]
    B -->|fails| Y["integration skipped"]
```

In GitHub Actions you express this with `needs`. A job whose needed job fails or is skipped is skipped itself, so a failing `check` leaves `unit` and `integration` unrun and costing nothing ([Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)). Jenkins and GitLab CI call these groups stages and run them in sequence, so a stage starts only after the one before it succeeded ([Jenkins](https://www.jenkins.io/doc/book/pipeline/), [GitLab](https://docs.gitlab.com/ci/yaml/)). In GitHub Actions the unit of ordering is the job, so a "stage" is one job or a few jobs that share a `needs`.

The cost of this ordering is latency on the green path: three jobs in a row take the sum of their times, where three in parallel would take only the longest. Lesson 10 returns to that trade-off. Ordering is right when failures are common and runner minutes matter, and wrong when everything usually passes and people are waiting.

### Unit tests and integration tests

A unit test needs nothing outside the process: no network, no database, no clock you do not control. An integration test uses a real external piece, here Postgres, to prove the wiring works. Keeping them separate lets the cheap tier run first. With pytest the usual way to separate them is a marker, registered in `pytest.ini` so a typo in the name is not silently accepted:

```ini
[pytest]
markers =
    integration: needs a running Postgres, set through DATABASE_URL
```

```python
# test_integration.py
import os

import psycopg2
import pytest

pytestmark = pytest.mark.integration


def test_database_roundtrip():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            assert cur.fetchone() == (1,)
    finally:
        conn.close()
```

`pytest -m "not integration"` runs the unit tier and `pytest -m integration` runs the other one. The language track owns pytest itself, see [Python: Project and Packaging](../../../programming/python/reference/project-and-packaging.md). The pipeline's job is to run the two commands in the right order.

### Service containers

An integration job needs a database that exists for the length of the job and is gone afterwards. A [service container](https://docs.github.com/en/actions/tutorials/use-containerized-services/use-docker-service-containers) is a Docker container the runner starts beside your steps and destroys when the job ends. You declare it under `services`, and each service is created fresh for each job.

Three rules from the docs decide whether your steps can reach it:

- Service containers need a Linux runner. On GitHub-hosted runners that means an `ubuntu-*` label, which is why this job does not join a Windows matrix in lesson 7.
- When the job runs directly on the runner, as ours does, the service's ports are not exposed by default. You map them with `ports`, and the service is then reachable at `localhost:<port>`.
- When the job itself runs in a container, the service is reachable by its label as a hostname and no port mapping is needed.

A health check matters because a container being started is not the same as Postgres accepting connections. The docs' PostgreSQL example uses `options` to pass Docker health flags so the job waits until the database is ready before the first step runs ([Creating PostgreSQL service containers](https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers)).

### The workflow for the practice repository

```yaml
name: ci

on:
  push:
    branches: [main]
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.13"
      - run: python -m compileall -q app.py test_app.py test_integration.py

  unit:
    needs: check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.13"
      - run: pip install -r requirements.txt
      - run: pytest -m "not integration"

  integration:
    needs: unit
    runs-on: ubuntu-latest
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
    env:
      DATABASE_URL: postgresql://postgres:postgres@localhost:5432/postgres
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.13"
      - run: pip install -r requirements.txt
      - run: pytest -m integration
```

`python -m compileall` is the cheapest check that needs no installed packages: it compiles each file and fails on a syntax error. A linter such as Ruff would sit in the same stage. The database password here is a throwaway value for a container that lives for one job, which is the one place a literal credential in a workflow is acceptable. Lesson 14 covers real secrets.

## Practice

1. ▢ Which stage order fails fastest on the mistakes people make most often?

    - a) Unit, integration, check
    - b) Integration, unit, check
    - c) Check, unit, integration
    - d) Integration, check, unit

<details markdown="1"><summary>Check</summary>

**c)** Cheapest and most common failures first. (a) and (b) put the check, which is a few seconds, last, so a typo waits behind a database startup. (d) runs the most expensive stage before a unit test could have caught the same bug in tens of seconds.

</details>

2. ▢ Write the `services` block for a Postgres 17 container, with the password `postgres`, for a job that runs directly on the runner and connects at `localhost:5432`.

<details markdown="1"><summary>Hint</summary>

Two things have to be true for `localhost` to work: the container must be healthy before step one, and its port must be published to the runner.

</details>

<details markdown="1"><summary>Check</summary>

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

The `ports` line maps container port 5432 to port 5432 on the runner. Without it the database exists but nothing on the runner can reach it. Without the health options the first step may run while Postgres is still starting.

</details>

3. ▢ Predict, then run. In `ci-cd-practice`, create a branch, delete a closing parenthesis in `app.py`, and open a pull request. Which of the three jobs fail, which are skipped, and roughly how long does the run take compared with a green one?

<details markdown="1"><summary>Hint</summary>

Look at the `needs` chain and ask which job is the first one that can fail.

</details>

<details markdown="1"><summary>Check</summary>

`check` fails, `unit` and `integration` are skipped. In the log of `check`:

```text
Run python -m compileall -q app.py test_app.py test_integration.py
*** Error compiling 'app.py'...
  File "app.py", line 9
    def version(
               ^
SyntaxError: '(' was never closed
Error: Process completed with exit code 1.
```

The run ends in well under a minute because the two later jobs never get a runner. The same mistake in a pipeline where all jobs run in parallel would still fail `unit`, but only after installing dependencies and starting a database nobody needed.

</details>

4. ▢ Debug this. The `integration` job fails on its first test, yet the `services` block starts Postgres and passes its health check. Find the cause.

    ```yaml
    integration:
      needs: unit
      runs-on: ubuntu-latest
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
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/postgres
    ```

    ```text
    psycopg2.OperationalError: connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused
    	Is the server running on that host and accepting connections on that port?
    ```

<details markdown="1"><summary>Hint</summary>

The job runs on the runner, not inside a container. What does the docs say about ports in that case?

</details>

<details markdown="1"><summary>Check</summary>

The `ports` mapping is missing. A job that runs directly on the runner reaches a service through `localhost:<port>`, but a service container does not publish its ports unless you list them. Add `ports: [5432:5432]` under `postgres`. The health check passing proves the database is up inside its container, not that the runner can reach it.

</details>

5. ▢ `check` takes 12 seconds, `unit` 38 seconds and `integration` 55 seconds. How long does a green run take with the chain from this lesson, and how long if all three ran in parallel? Say when you would take the slower one anyway.

<details markdown="1"><summary>Check</summary>

Chained, the critical path is 12 + 38 + 55 = 105 seconds, ignoring the few seconds each job spends waiting for a runner. In parallel it is the longest job, 55 seconds. Take the chain when failures are frequent enough that skipping later jobs saves more minutes than the green path loses, or when runners are scarce. Take parallel when most runs are green and waiting is the cost. Lesson 10 shows how to get the best of both with a short check stage and a parallel fan-out after it.

</details>

## Real-world reps

- [ ] In `ci-cd-practice`, add `test_integration.py`, `pytest.ini` and the three-job `ci.yml` from this lesson. Install the driver with `pip install psycopg2-binary`, pin it by appending the line from `pip freeze | grep -i psycopg2` to `requirements.txt`, and push. Open the run and confirm the jobs run in order.
- [ ] Break `app.py` as in practice item 3, open a pull request, and read which jobs ran. Then fix it and confirm all three go green.
- [ ] Open the workflow of a repository you work in and list its stages with a rough duration for each. Write down whether the cheapest check runs first.
- [ ] Tomorrow: without notes, write the three stages in order with the question each one answers, and name the two things a service container needs so a job on the runner can reach it.

## Going further

- [Fast Feedback](../reference/fast-feedback.md)
- [Docs: "Using Docker service containers", GitHub](https://docs.github.com/en/actions/tutorials/use-containerized-services/use-docker-service-containers)
- [Docs: "Creating PostgreSQL service containers", GitHub](https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers)
- [Python: Project and Packaging](../../../programming/python/reference/project-and-packaging.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
