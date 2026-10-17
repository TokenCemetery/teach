---
title: "8. Caching"
description: Key a cache on the lockfile, fall back with restore keys, and know what a cache must never be trusted to hold
type: lesson
---

# Lesson 8. Caching

**Mission link:** The mission says to prove every change in minutes. Every job starts on a fresh runner, so every job downloads its dependencies again unless something carries them over, and a cache does that safely only if you treat it as a speed-up that may vanish at any time.
**Primary source:** [Docs: "Dependency caching reference", GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)
**Prerequisites:** [Lesson 4](0004-jobs-steps-and-runners.md), [Lesson 5](0005-actions-expressions-and-outputs.md), [Lesson 7](0007-matrix-builds.md), [Cache](../GLOSSARY.md), [Artifact](../GLOSSARY.md), [Expression](../GLOSSARY.md), [Runner](../GLOSSARY.md)

## Warm-up

1. ▢ A job on a GitHub-hosted runner installs dependencies in step 3. A later job in the same workflow needs them too. Why are they not already there?

<details markdown="1"><summary>Check</summary>

Each job runs on its own fresh runner, and a hosted runner is discarded when the job ends (lesson 4). Nothing from the first job's file system reaches the second unless you pass it explicitly. A cache is one way to do that for files that only need to be faster, not guaranteed.

</details>

2. ▢ Lesson 7's matrix runs five `unit` jobs. How many times does `pip install -r requirements.txt` run, and what does that say about where caching pays?

<details markdown="1"><summary>Check</summary>

Five times, once per job, because each job is a separate runner. The same dependency set is downloaded five times per run and again on the next push, so a cache keyed on the dependency file saves the most in matrix jobs and in workflows that run on every pull request update.

</details>

3. ▢ Which expression function does a key use to turn a file's contents into text, and in which contexts is it available?

<details markdown="1"><summary>Check</summary>

`hashFiles` with a glob pattern returns a SHA-256 hash over the files that match, and it is available in step-level keys such as `with` ([Contexts reference](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts), [Expressions](https://docs.github.com/en/actions/reference/workflows-and-actions/expressions)). It is not available at the job level, which is why caching is a step, not a job setting (lesson 5).

</details>

## Know this

### What a cache is for

A [cache](../GLOSSARY.md) is a set of files saved under a key so a later run can skip the work of producing them. The rule that governs everything below: a cache may be missing or stale at any time and must only ever make a run faster. If deleting every cache could change whether your pipeline passes, something is wrong.

That rule is also what separates a cache from an [artifact](../GLOSSARY.md). An artifact is kept on purpose and relied on, and lesson 11 is about it. A cache is a courtesy that the platform can evict.

### The key decides everything

`actions/cache` takes a `path` to save and restore and a `key` to find it by. The key is the whole design: it must change exactly when the cached files would be wrong. For Python dependencies that is the contents of `requirements.txt`:

```yaml
      - uses: actions/setup-python@v7
        with:
          python-version: "3.13"
      - id: pip-dir
        shell: bash
        run: echo "dir=$(pip cache dir)" >> "$GITHUB_OUTPUT"
      - uses: actions/cache@v6
        with:
          path: ${{ steps.pip-dir.outputs.dir }}
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-
      - run: pip install -r requirements.txt
```

The path comes from `pip cache dir` because the cache directory differs by operating system, and lesson 7's matrix includes Windows. The key combines `runner.os` with the hash of the file, as the [docs](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching) do with `hashFiles('**/package-lock.json')`: a different operating system gets a different cache, and a changed dependency file gets a new one. Keys are at most 512 characters, and a longer one fails the action. Because `requirements.txt` pins exact `==` versions, its hash changes only when a pin changes. If it listed ranges, the hash would stay the same while `pip` resolved newer versions, which the [setup-python docs](https://github.com/actions/setup-python#caching-packages-dependencies) warn about.

For package managers that `setup-*` actions know, there is a shortcut. `setup-python` with `cache: pip` restores and saves the pip cache for you, using the hash of the dependency file as part of the key. Caching is off by default, and `cache-dependency-path` points the hash at other files ([setup-python README](https://github.com/actions/setup-python#caching-packages-dependencies)). Use the shortcut where it fits and the explicit action where you need to control the key.

### Hits, misses and restore keys

The action searches for an exact match to `key`. An exact match is a cache hit and the files are restored. No match is a cache miss. On a miss it tries each of `restore-keys` in order, treating each as a prefix, and restores the most recently created cache that matches. A restore-key match restores something close but not exact, so it is a partial restore, not a hit.

Three consequences come from the docs:

- The `cache-hit` output is `true` only for an exact match on `key`. After a restore-key match it is `false`, so a step guarded by `cache-hit != 'true'` still runs, and that is the point: install whatever the stale cache lacks.
- A cache cannot be changed once created. When the key matches an existing cache, no new cache is saved. A miss creates one when the job completes successfully, at the end of the job, under the key you provided.
- Restore keys go from most specific to least. A broader prefix such as `Linux-pip-` gives a warm start from the last dependency set, which is mostly right and cheaper than starting from nothing.

The log shows which case you are in:

```text
Cache not found for input keys: Linux-pip-ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb, Linux-pip-
...
Post job cleanup.
Cache saved with key: Linux-pip-ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb
```

```text
Cache restored from key: Linux-pip-ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb
```

### Which runs can see which cache

A run can restore caches created on its own branch or on the default branch. A pull request run can also restore caches from its base branch. It cannot restore caches from child or sibling branches, and caches created for different tags do not cross either ([Docs](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)). When the action searches, it tries the current branch first, then the default branch.

|Cache created by|Restorable by|
|---|---|
|A push to `main`|Runs on `main`, and runs on every branch and pull request that can see the default branch|
|A push to `feature-a`|Runs on `feature-a`, and pull requests whose base is `feature-a`|
|A `pull_request` run|Only re-runs of that same pull request, because it is created for the merge ref|

The practical pattern follows: let pushes to `main` build the caches, and pull requests restore them. A pull request's own cache helps only its re-runs, so the first run after you push a pull request relies on what `main` saved.

### Limits and eviction

GitHub removes any cache entry not accessed in over 7 days. A repository's caches share a total size limit, 10 GB by default, and past it GitHub evicts the least recently accessed caches first until the total fits. Using more than the limit can be billed, and eviction can cause thrashing, where caches are created and evicted over and over ([Docs](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)). Cache what is costly to recreate and small, and give caches keys that will actually be hit again.

A cache also costs time. Restoring downloads and unpacks the files, and saving packs and uploads them at the end of the job. Measure before and after: for the practice repository's three packages the saving is small, and the lesson is the mechanism, not the seconds.

### What a cache must never hold or decide

- **Secrets.** Anyone with read access can open a pull request and read a cache, and forks can read caches on the base branch. The docs say not to store tokens or credentials in cached paths.
- **The artifact you ship.** The thing a deploy job uses must be an artifact, which is kept on purpose. A cache can be evicted, missing or stale, and a build that depends on it is not reproducible.
- **Test results.** A cache that stores "this passed" turns a stale answer into a green check.
- **Trust from untrusted triggers.** Runs started by events someone outside the repository can influence, such as `pull_request_target`, `issue_comment` and `workflow_run`, get read-only access to the default branch's caches, so they cannot plant one for a later privileged run to restore. Only a short list of trusted triggers, such as `push`, `workflow_dispatch` and `schedule`, can write there ([Docs](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)). Lesson 16 covers why this matters.

## Practice

1. ▢ Which `key` makes a new cache exactly when the dependencies change and not otherwise?

    - a) `${{ runner.os }}-pip-${{ github.sha }}`
    - b) `${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}`
    - c) `${{ runner.os }}-pip-${{ github.run_id }}`
    - d) `${{ runner.os }}-pip-${{ github.run_attempt }}`

<details markdown="1"><summary>Check</summary>

**b)** The hash of the file changes only when a pin changes. (a) changes with every commit, so the cache never hits twice. (c) is unique to every run, so it never hits at all. (d) is a small number that restarts at 1 for every new run, so it hits only by accident and says nothing about the dependencies.

</details>

2. ▢ Predict, then run. Add the cache step from this lesson to `unit`, then run it three times: (1) push to `main`, (2) on a branch with an open pull request, change one pin in `requirements.txt` and push, (3) re-run that pull request's workflow without a new commit. For each run, say what the log reports and whether `cache-hit` is `true`.

<details markdown="1"><summary>Hint</summary>

Ask for each run whether the exact key exists, then whether a prefix matches, and what the job saves at its end.

</details>

<details markdown="1"><summary>Check</summary>

Run 1: no cache exists, so `Cache not found for input keys`, `cache-hit` is `false`, and the job saves a cache under the hash of `main`'s file. Run 2: the new hash has no exact match, but the restore key `Linux-pip-` matches the one from `main`, so the log says `Cache restored from key` with `main`'s key, `cache-hit` is still `false`, and the job saves a second cache under the new hash when it succeeds. Because a `pull_request` run creates its cache for the merge ref, only re-runs of this pull request can restore it. Run 3: that is exactly such a re-run, so the exact key is found, `cache-hit` is `true`, and nothing new is saved because a matching cache cannot be replaced.

</details>

3. ▢ Debug this. The workflow has a cache step, yet the log always says the cache was not found and a new one is saved on every run. The cache list under Actions fills with entries. Find the cause.

    ```yaml
    - uses: actions/cache@v6
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ github.sha }}
    ```

    ```text
    Cache not found for input keys: Linux-pip-2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6
    ```

<details markdown="1"><summary>Hint</summary>

Which part of the key changes on every push?

</details>

<details markdown="1"><summary>Check</summary>

`github.sha` changes with every commit, so the exact key never exists for the next run, and there is no `restore-keys` to fall back on. Key on `hashFiles('requirements.txt')` and add `restore-keys: ${{ runner.os }}-pip-`. The growing cache list is the cost: each run saves a cache nobody will use, which fills the repository's limit and evicts the caches that were useful.

</details>

4. ▢ A cache was created by a push to `feature-a`, which was branched from `main`. Which of these can restore it: a push to `main`, a pull request from `feature-c` (also branched from `main`), a pull request from `feature-b` whose base is `feature-a`, and a later push to `feature-a`?

<details markdown="1"><summary>Check</summary>

The pull request from `feature-b` and the later push to `feature-a`. The push to `main` cannot, since a cache created for a child branch is not visible from the parent. The pull request from `feature-c` cannot either, since siblings do not share caches. A pull request can restore caches from its base branch, which is why `feature-b` with base `feature-a` can ([Docs](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)).

</details>

5. ▢ A teammate adds `dist/` to the cached paths so the deploy job "reuses the build". Give two reasons this is wrong and say what to use instead.

<details markdown="1"><summary>Check</summary>

A cache can be missing, evicted after 7 days without access, or stale, so the deploy job might ship nothing or an old build. And a cache is readable by anyone who can open a pull request, so it is not a place for something you will run in production. Use an artifact, which is kept on purpose and identified so the later job gets exactly that output (lesson 11).

</details>

## Real-world reps

- [ ] Add the cache step to the `unit` job of `ci-cd-practice` and push twice with no changes in between. Open each run's cache step and find `Cache not found` in the first and `Cache restored from key` in the second. Compare the install step's time.
- [ ] In the repository's Actions tab, open the caches list and delete the cache. Re-run the latest workflow and confirm it still passes, only slower. That is the test that the cache is an optimisation and nothing more.
- [ ] Open a workflow you work on and find what it downloads on every run. Write down which key would be right for it and what would make that key wrong.
- [ ] Tomorrow: without notes, say what `cache-hit` reports after a restore-key match, which branches a pull request run can restore from, and three things a cache must never hold or decide.

## Going further

- [Fast Feedback](../reference/fast-feedback.md)
- [Docs: "Dependency caching reference", GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)
- [Repository: actions/cache, GitHub](https://github.com/actions/cache), the inputs and outputs, and the separate restore and save actions
- [Repository: actions/setup-python, GitHub](https://github.com/actions/setup-python), the built-in `cache: pip` option
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
