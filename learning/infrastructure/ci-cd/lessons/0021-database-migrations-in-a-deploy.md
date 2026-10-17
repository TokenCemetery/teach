---
title: "21. Database Migrations in a Deploy"
description: Order schema changes around code with expand and contract so every version running during a deploy works against the schema
type: lesson
---

# Lesson 21. Database Migrations in a Deploy

**Mission link:** The mission says to order database migrations around a deploy. A deploy replaces code in minutes and a rollback replaces it again, but the schema is shared by every version that is running, and it has no undo button. This lesson is about where in the pipeline a migration sits and how to split a change so that no version ever meets a schema it cannot use.
**Primary source:** [Article: "ParallelChange", Danilo Sato](https://martinfowler.com/bliki/ParallelChange.html)
**Prerequisites:** [Lesson 6](0006-build-and-test-stages.md), [Lesson 19](0019-deployment-strategies.md), [Lesson 20](0020-rollback-and-roll-forward.md), [Expand and contract](../GLOSSARY.md), [Rolling deployment](../GLOSSARY.md), [Rollback](../GLOSSARY.md), [Roll forward](../GLOSSARY.md)

## Warm-up

1. ▢ During a rolling deployment, how many versions of the code answer requests, and until when?

<details markdown="1"><summary>Check</summary>

Two, the old and the new, from the moment the first new instance is ready until the last old one is replaced (lesson 19). The glossary says exactly this: both run together until the rollout finishes ([Rolling deployment](../GLOSSARY.md)).

</details>

2. ▢ Lesson 20 named a case where a rollback is the wrong tool because code goes back and data does not. Which case was it, and what is the alternative?

<details markdown="1"><summary>Check</summary>

A schema change the old code cannot use, for example a renamed column. The rolled-back version queries a column that no longer exists. The alternative is to roll forward with a fixed release, and this lesson is how to avoid being forced into that choice.

</details>

3. ▢ In lesson 6 the `integration` job reached Postgres at `localhost:5432`. Which key of the `services` block made that possible?

<details markdown="1"><summary>Check</summary>

`ports: [5432:5432]`. A service container does not publish its ports unless the block lists them, and the health options only prove the database is up inside its container (lesson 6).

</details>

## Know this

### The schema is shared state

A deploy changes code. A migration changes the database, which every running version reads and writes, and no strategy from lesson 19 gives you two databases. Three facts follow:

- The migration runs once, at one moment, and the code rollout takes a while. Whichever goes first, there is a window in which old code runs against the new schema or new code runs against the old schema.
- A rollback (lesson 20) puts the old code back against whatever schema exists by then.
- Nothing in the pipeline can see the problem unless a test exercises that exact pairing.

So the rule is about pairs: **every version of the code that can be running must work against every schema that can exist at that moment.** A change that breaks the rule is not wrong forever, it is wrong in one step. The fix is to take smaller steps.

### Expand, migrate, contract

The pattern is called parallel change, or expand and contract. Sato describes it as breaking a backward-incompatible change into three phases, and says it fits continuous delivery because the code can be released in any of the three. He also names database refactoring as a key use, where the migrate phase is the transition period between the old and new schema ([ParallelChange](https://martinfowler.com/bliki/ParallelChange.html)). Applied to renaming a column, `name` to `full_name`:

|Deploy|Schema change|Code that runs|Why it is safe|
|---|---|---|---|
|1. Expand|Add `full_name`, keep `name`|Writes both columns, reads `full_name` and falls back to `name`|Old code ignores the new column, new code copes with rows that lack it|
|2. Migrate|Backfill `full_name` from `name`|Reads and writes `full_name` only|Every row now has the new value, and the old code is gone|
|3. Contract|Drop `name`|No code mentions `name`|Nothing reads the old column, so removing it cannot break a reader|

Each row is its own deploy, with its own green pipeline, and any of them can stop there. If deploy 2 misbehaves, a rollback returns to code that still works, because `name` still exists. The big-bang alternative, one migration that renames the column, is correct for the new code and wrong for every old instance still running, and for any rollback.

```mermaid
flowchart LR
    A["Old schema<br>and old code"] --> B["Expand: add column,<br>ship code that handles both"]
    B --> C["Migrate: backfill,<br>ship code that uses the new column"]
    C --> D["Contract: drop the old column"]
```

Two things make the table work in practice. The backfill is a data change, and on a large table it is a long write: do it in batches, as the migration safety table in the SQL track's [Operating](../../../programming/sql/reference/operating.md) sheet describes, with each statement's lock and rewrite cost listed. And contract is the only step that cannot be undone by redeploying code, so it waits until the previous version is gone and you no longer need to roll back to it. The SQL track's [migrations without downtime](../../../programming/sql/lessons/0042-migrations-without-downtime.md) lesson writes the SQL for these steps. This lesson takes the SQL as given and decides when each step runs.

### Where the migration runs in the pipeline

A migration is a deploy step with its own failure modes, so give it its own job and order it explicitly:

```mermaid
flowchart LR
    A["build<br>image digest"] --> B["migrate<br>one run, additive only"]
    B --> C["deploy<br>rolling update"]
    C --> D["smoke test"]
```

- **Run it once, before the code that needs it.** An additive migration that runs first is safe against the old code, by the rule above. A deploy that depends on a column the migration has not created yet fails.
- **One run, not one per instance.** If every new instance migrates on startup, several can start at once and race. A single job with a [concurrency group](../GLOSSARY.md) (lesson 10) serializes it: only one migration job per environment runs at a time.
- **Only expand and migrate steps ride with a code deploy.** A contract migration is its own change, merged after the code that stopped using the column has been running long enough that nobody would roll back past it.
- **Test the pair, not the end state.** Run the old version's queries against the new schema in CI, the same way lesson 6 ran integration tests against a service container. That is the test that would have caught the rename.

A migration that fails halfway is its own topic: whether the statements run in a transaction depends on the database and the tool, so check your migration tool's documentation before relying on an automatic rollback of a partly applied migration.

## Practice

1. ▢ Which statement describes the rule a safe deploy keeps for the schema?

    - a) Each version works against every schema that can exist beside it
    - b) Each schema works with the newest version that has been released
    - c) Each migration runs after the code that needs it has shipped
    - d) Each rollback restores the exact schema that the older code expects

<details markdown="1"><summary>Check</summary>

**a)** Old and new code overlap during a rollout and after a rollback, so what matters is every pairing that can occur. (b) ignores the old instances still running. (c) has the order backwards for additive changes: the column must exist before the code that uses it. (d) is the dangerous assumption, since a rollback redeploys code and leaves the schema as it is.

</details>

2. ▢ Write the three deploys for changing `accounts.plan` from a free-text column to a new column `plan_id` that holds an integer. For each deploy give the schema change and what the code does.

<details markdown="1"><summary>Check</summary>

1. Expand: add nullable `plan_id`. Code writes both `plan` and `plan_id`, and reads `plan_id` with a fallback to the text in `plan`.
2. Migrate: backfill `plan_id` from `plan` in batches, once the version that does not write `plan_id` is gone. Code reads and writes `plan_id` only.
3. Contract: drop `plan`, in a later release, after nobody would roll back to code that reads it.

A `NOT NULL` constraint on `plan_id` belongs after the backfill, never in step 1, where old code still inserts rows without it.

</details>

3. ▢ Predict, then run. This script plays the part of three versions of the code against a real Postgres. Add it as `migration_lab.py` to `ci-cd-practice`, and `migration-lab.yml` beside it. In which steps does a version fail, and with what?

    ```python
    import os

    import psycopg2

    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    conn.autocommit = True
    cur = conn.cursor()


    def versions(table):
        return {
            "old": [
                f"INSERT INTO {table} (name) VALUES ('old')",
                f"SELECT name FROM {table}",
            ],
            "bridge": [
                f"INSERT INTO {table} (name, full_name) VALUES ('bridge', 'bridge')",
                f"SELECT COALESCE(full_name, name) FROM {table}",
            ],
            "new": [
                f"INSERT INTO {table} (full_name) VALUES ('new')",
                f"SELECT full_name FROM {table}",
            ],
        }


    def check(table, which):
        for label in which:
            try:
                for statement in versions(table)[label]:
                    cur.execute(statement)
                result = "ok"
            except psycopg2.Error as error:
                result = "FAILS: " + str(error).splitlines()[0]
            print(f"  {label:<7}{result}")


    def step(table, description, statement, which):
        print(description)
        if statement:
            cur.execute(statement)
        check(table, which)


    cur.execute("DROP TABLE IF EXISTS bigbang, visitors")

    print("== One deploy: rename the column")
    cur.execute("CREATE TABLE bigbang (id serial PRIMARY KEY, name text)")
    step("bigbang", "before the migration", None, ["old"])
    step("bigbang", "after RENAME COLUMN name TO full_name", "ALTER TABLE bigbang RENAME COLUMN name TO full_name", ["old", "new"])

    print("== Three deploys: expand, migrate, contract")
    cur.execute("CREATE TABLE visitors (id serial PRIMARY KEY, name text)")
    step("visitors", "before the migration", None, ["old"])
    step("visitors", "deploy 1, expand: ADD COLUMN full_name", "ALTER TABLE visitors ADD COLUMN full_name text", ["old", "bridge"])
    step("visitors", "deploy 2, migrate: backfill, then only new code reads full_name", "UPDATE visitors SET full_name = name WHERE full_name IS NULL", ["bridge", "new"])
    step("visitors", "deploy 3, contract: DROP COLUMN name", "ALTER TABLE visitors DROP COLUMN name", ["new"])
    ```

    ```yaml
    name: Migration lab
    on: workflow_dispatch
    permissions:
      contents: read
    jobs:
      lab:
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
          - run: python migration_lab.py
    ```

<details markdown="1"><summary>Hint</summary>

Read each version's two statements as the SQL a running instance sends. A version fails in the first step where a column it names does not exist. The `bridge` version names both columns, so it needs both to exist.

</details>

<details markdown="1"><summary>Check</summary>

```text
== One deploy: rename the column
before the migration
  old    ok
after RENAME COLUMN name TO full_name
  old    FAILS: column "name" of relation "bigbang" does not exist
  new    ok
== Three deploys: expand, migrate, contract
before the migration
  old    ok
deploy 1, expand: ADD COLUMN full_name
  old    ok
  bridge ok
deploy 2, migrate: backfill, then only new code reads full_name
  bridge ok
  new    ok
deploy 3, contract: DROP COLUMN name
  new    ok
```

Only the big-bang rename fails, and it fails for the old version, which is the one still serving requests during the rollout or after a rollback. In the three-deploy run every pairing that can occur is `ok`, because each step keeps at least one column that every running version names. The `old` version is absent from the last two checks on purpose: by deploy 2 it is gone, and that is the condition that made the later steps safe.

</details>

4. ▢ Debug this. A release adds `plan text NOT NULL` to `accounts` in a `migrate` job, then rolls out the new version. For about a minute during the rollout, signups fail. Name the cause and the fix.

    ```console
    $ kubectl logs deploy/web --since=2m | grep ERROR | head -2
    ERROR: null value in column "plan" of relation "accounts" violates not-null constraint
    DETAIL: Failing row contains (4821, ada@example.com, null).
    ```

<details markdown="1"><summary>Hint</summary>

Ask which version is writing rows with no `plan`, and whether the migration job ran before or after that version stopped running.

</details>

<details markdown="1"><summary>Check</summary>

The migration ran first, as it should, but it added a `NOT NULL` column with no default. The old instances still serving requests during the rolling update do not know the column and insert rows without it, so every signup through an old instance fails until the rollout ends. The fix is to expand first: add the column nullable (or with a default), ship code that writes it, backfill, and add the constraint in a later release when no running version can omit it.

</details>

5. ▢ A team ships the new code and `DROP COLUMN name` in one release, and a bug forces a rollback an hour later. What happens, and which lesson-20 tool is left?

<details markdown="1"><summary>Check</summary>

The old version, redeployed by digest, selects and inserts `name`, which no longer exists, so it fails as soon as it starts serving. The rollback cannot restore the data in a dropped column, which is why this track calls contract the step that cannot be redeployed away. What is left is rolling forward: a fixed release, and restoring the column from a backup only if the data matters. Splitting the drop into its own later release would have kept the rollback available.

</details>

## Real-world reps

- [ ] In `ci-cd-practice`, add `migration_lab.py` and `migration-lab.yml` from practice item 3 and run the workflow from the Actions tab. Compare the log with your prediction, then change the `bigbang` step to expand first and watch the failure disappear.
- [ ] Find a migration in a repository you work in. Using the table in the SQL track's [Operating](../../../programming/sql/reference/operating.md) sheet, write down whether it is additive, whether it locks or rewrites, and which old version would break if it ran before the code rollout finished.
- [ ] Tomorrow: without notes, write the three deploys for renaming a column, say which one cannot be undone by a rollback, and say why a migration belongs in its own job.

## Going further

- [Deployments](../reference/deployments.md)
- [Article: "ParallelChange", Danilo Sato](https://martinfowler.com/bliki/ParallelChange.html)
- [Operating](../../../programming/sql/reference/operating.md), the SQL track's migration safety table
- [Workloads](../../kubernetes/reference/workloads.md), how a rolling update replaces pods
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
