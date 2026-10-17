---
title: "23. Pinning What the Pipeline Runs"
description: Pin third-party actions to a full commit SHA, lock dependencies, and keep the pins current with Dependabot
type: lesson
---

# Lesson 23. Pinning What the Pipeline Runs

**Mission link:** The mission says to secure the supply chain by pinning what the pipeline runs. Every `uses:` line and every `pip install` fetches code written by someone else and runs it next to your secrets and your token. A pin is the difference between running the code you reviewed and running whatever a name points at today.
**Primary source:** [Docs: "Secure use reference", GitHub](https://docs.github.com/en/actions/reference/security/secure-use)
**Prerequisites:** [Lesson 13](0013-building-and-publishing-an-image.md), [Lesson 14](0014-secrets-and-the-github-token.md), [Lesson 16](0016-untrusted-input.md), [Pin](../GLOSSARY.md), [Action](../GLOSSARY.md), [Digest](../GLOSSARY.md), [GitHub token](../GLOSSARY.md)

## Warm-up

1. ▢ Lesson 13 said tags move and digests do not. Which of `ghcr.io/octocat/ci-cd-practice:main` and `ghcr.io/octocat/ci-cd-practice@sha256:...` names one exact image, and why?

<details markdown="1"><summary>Check</summary>

The digest. A digest is the hash of the content, so it cannot refer to anything else, while `main` is moved by every push. Pinning an action is the same idea applied to code you run rather than code you ship.

</details>

2. ▢ Lesson 14 said the `GITHUB_TOKEN`'s permissions are the cap on what a compromised action can do to the repository. Why does a third-party action get to use it at all?

<details markdown="1"><summary>Check</summary>

An action can read `github.token` even when the workflow never passed the token to it, so every action a job uses inherits what the token can do (lesson 14). An action in a job also shares the runner with the job's other steps and sees what they put in the environment.

</details>

3. ▢ What does lesson 16's fix for script injection do with an expression, and does pinning replace it?

<details markdown="1"><summary>Check</summary>

It assigns the expression to an environment variable, so the value is never pasted into the script text. Pinning does not replace it: pinning controls which code runs, not what that code does with attacker-controlled input.

</details>

## Know this

### A tag is a promise, a SHA is a fact

When a workflow says `uses: octo-org/deploy-action@v3`, GitHub Actions resolves the reference to whatever commit the tag points at when the job starts. The secure use reference states the risk plainly: a compromise of a single action in a workflow can be very significant, because the action has access to all secrets configured on the repository and may be able to use the `GITHUB_TOKEN` to write to the repository. It also says a tag can be moved or deleted if a bad actor gains access to the repository storing the action, even when you trust its author ([Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)).

This happened. In March 2025 the widely used `tj-actions/changed-files` action was compromised. The GitHub advisory says attackers retroactively modified multiple version tags to point at a malicious commit, and that the injected code extracted secrets from the runner process and printed them in workflow logs, which are public for public repositories ([GitHub advisory GHSA-mrrh-fwg8-r2c3](https://github.com/advisories/GHSA-mrrh-fwg8-r2c3)). CISA's alert lists what could leak: valid access keys, GitHub personal access tokens, npm tokens and private RSA keys. It tells affected organizations to identify the repositories that ran the action in the window, treat any exposed secrets as compromised, and rotate them immediately. It also notes the compromise may have been enabled by a compromise of a second action, `reviewdog/action-setup@v1`, a reminder that one action's trust extends to whatever it uses ([CISA alert](https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-tj-actionschanged-files-cve-2025-30066-and-reviewdogaction)). A workflow that named the action by one of the moved tags and ran in that window ran the malicious code, with no change to its workflow file.

### Pin to a full commit SHA

The docs' recommendation for actions is to pin to a full-length commit SHA. An attacker who controls the repository would need a SHA-1 collision on a valid Git object to substitute other code under that reference. Two details in the docs matter in review: use the full-length SHA, and verify that it comes from the action's own repository and not a fork ([Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)).

```yaml
steps:
  - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
  - uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
    with:
      python-version: "3.13"
```

The trailing comment is for people, and for Dependabot, which updates it when it is on the same line ([Keeping your actions up to date](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/keeping-your-actions-up-to-date-with-dependabot)). Those two SHAs are what the tags `v7.0.1` and `v7.0.0` pointed at when this lesson was written. Find the one for the version you want yourself:

```console
$ git ls-remote --tags https://github.com/actions/checkout 'v7*'
3d3c42e5aac5ba805825da76410c181273ba90b1	refs/tags/v7
9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0	refs/tags/v7.0.0
3d3c42e5aac5ba805825da76410c181273ba90b1	refs/tags/v7.0.1
```

Here the moving `v7` tag and `v7.0.1` share a SHA because `v7.0.1` was the newest release. A newer release moves `v7` and leaves the older tag alone, which is exactly the behaviour a pin avoids. If a tag is annotated, the output has a second line ending in `^{}`, and the SHA on that line is the commit.

What the docs say about the alternative: pin to a tag only if you trust the creator, and the Verified creator badge on the Marketplace is a useful signal, but there is risk even then. The repository setting **Require actions to be pinned to a full-length commit SHA**, under Actions permissions, enforces the policy: with it on, all actions must be pinned, including those authored by GitHub, though reusable workflows can still be referenced by tag ([Managing GitHub Actions settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)). Reusable workflows from other repositories carry the same risk and the docs apply the same advice to them.

GitHub is also building a stronger mechanism, a workflow dependency lockfile at `.github/workflows/actions.lock`, generated by the `gh actions-lock` extension. It records the exact commit for every action a workflow uses, including transitive dependencies, and the secure use reference calls it the strongest protection available. The page marks it as a public preview that may change, so read it before relying on it ([Workflow dependency lockfiles](https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles)). A plain SHA pin fixes only the action you name. If that action is a composite action that calls other actions, those are resolved by its own `uses` lines.

### Pins go stale, so automate the update

A pin that nobody updates means missing fixes forever, so the pin needs a process. Dependabot version updates support the `github-actions` ecosystem: with `directory: "/"`, it checks the workflow files in `.github/workflows` and opens a pull request when a newer version is out ([Keeping your actions up to date](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/keeping-your-actions-up-to-date-with-dependabot)).

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

Dependabot supports `uses` with a tag or a commit and ignores locally referenced actions such as `./.github/actions/foo`. If the pinned commit is not associated with any tag, it updates to the latest commit, which might not be the latest release, and the docs warn about that ([Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)). Dependabot alerts, the ones that warn of a vulnerable action, are only created for actions that use semantic versioning, and not for actions pinned to SHA values ([Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)), so version updates are how a SHA pin stays current. The pull request is where the review happens: read what changed between the two versions before merging.

### Lock what the code installs

An action is one source of third-party code. The other is the packages your steps install. Lesson 12 asked for exact `==` versions in `requirements.txt`, which stops a new release from sneaking in, but a version is a name too: a release can be replaced or tampered with after you chose it, and each of your packages has dependencies that `==` does not mention. pip's hash-checking mode closes both: hashes embedded in the requirements file protect against remote tampering, and the mode applies to every requirement and every dependency, so a file that is missing any of them is an error ([pip: Secure installs](https://pip.pypa.io/en/stable/topics/secure-installs/)).

```text
FooProject == 1.2 \
  --hash=sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824 \
  --hash=sha256:486ea46224d1bb4fb680f34f7c9ad96a8f24ec88be73ea8e5a6c65260e9cb8a7
```

That is the example from pip's documentation: one `--hash` per distribution file the package offers.

Writing those by hand is not realistic. `pip-compile --generate-hashes requirements.in` from pip-tools resolves the whole tree and writes every pin with its hashes ([pip-tools](https://github.com/jazzband/pip-tools)). Then `pip install --require-hashes -r requirements.txt` in the workflow refuses anything that does not match. The same rule applies to the container image from lesson 13: a base image named by a tag moves, and one named by digest does not, as the containers track's [container security](../../containers/reference/container-security.md) sheet explains.

|What runs|Movable reference|Pinned reference|
|---|---|---|
|An action|`actions/checkout@v7`|`actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1`|
|A reusable workflow|`org/repo/.github/workflows/ci.yml@v1`|The same path, ending in `@` and the full SHA|
|A Python package|`flask>=3`, or `flask==3.1.2` alone|`flask==3.1.2` with `--hash` lines|
|A base image|`python:3.13-slim`|`python@sha256:...`|

A pin protects against change, not against a bad original. If the code you pinned was malicious on the day you chose it, you are running it reliably. Reading the action's source before the first pin, and the diff on each update, is the part no tool does.

## Practice

1. ▢ Why does pinning an action to `@v7` not protect a repository from a compromised maintainer?

    - a) Tags can be moved to different commits later
    - b) Tags cannot be used in a reusable workflow
    - c) Tags are ignored when the runner fetches code
    - d) Tags are rewritten whenever the action is cached

<details markdown="1"><summary>Check</summary>

**a)** The runner resolves the tag when the job starts, so moving the tag changes what runs without any change to your workflow file, which is what happened to `tj-actions/changed-files`. (b) is false, a reusable workflow can be referenced by tag or by SHA. (c) is false, the tag is exactly what is used. (d) invents a behaviour.

</details>

2. ▢ Which of these lines is pinned as the secure use reference means it, and what is wrong with each of the others?

    ```yaml
    - uses: actions/checkout@v7
    - uses: example-org/lint@3d3c42e5aac5ba805825da76410c181273ba90b1 # v2.4.0
    - uses: example-org/lint@main
    - uses: example-org/lint@3d3c42e
    ```

<details markdown="1"><summary>Check</summary>

Only the second. `@v7` is a tag, which can be moved. `@main` is a branch, which moves with every push. `@3d3c42e` is an abbreviated SHA, and the recommendation is a full-length commit SHA, so it is not a pin that names exactly one commit.

</details>

3. ▢ Predict, then run. In `ci-cd-practice`, change the install step of the `build` job in `ci.yml` to `pip install --require-hashes -r requirements.txt` and push. Does the step pass, and what do you do about the result?

<details markdown="1"><summary>Hint</summary>

Hash-checking mode wants a hash for every requirement and every dependency. Look at what `requirements.txt` has from lesson 2.

</details>

<details markdown="1"><summary>Check</summary>

The step fails with a pip error about `--require-hashes`. The file has exact `==` versions and no `--hash` lines, and Flask and pytest each bring dependencies the file does not list at all. Fix it by moving your direct requirements to `requirements.in`, running `pip-compile --generate-hashes requirements.in` to write `requirements.txt`, committing both, and pushing again. The step then passes and installs the same versions as before. If you later bump a version in `requirements.in`, you recompile the file and review the new hashes in the diff.

</details>

4. ▢ Debug this. A repository that is public has `uses: tj-actions/changed-files@v44.5.1` in a workflow that runs on every push. A maintainer notices a long base64 string in a log from 14 March 2025 and has not changed the workflow since 2024. Explain how the code changed, what to do with the secrets, and what to change in the file.

<details markdown="1"><summary>Hint</summary>

The workflow file did not change. Ask what did.

</details>

<details markdown="1"><summary>Check</summary>

The tag `v44.5.1` was one of the version tags the attacker moved to a malicious commit, so the same reference ran different code on the next push, and the code printed the secrets the job could read into the public log. Treat every secret available to that job as compromised and rotate it (CISA's alert says so), because deleting the log does not unsee the value. In the file, pin to the full SHA of a commit you have reviewed, with the version as a comment, and let Dependabot propose updates. Also give the job `permissions` no wider than it needs, since the `GITHUB_TOKEN` was exposed too.

</details>

5. ▢ Dependabot opens a pull request changing `actions/setup-python@5fda3b95... # v7.0.0` to a new SHA with `# v7.1.0`. List two checks before merging.

<details markdown="1"><summary>Check</summary>

Compare the two versions in the action's repository, with the release notes and the diff between the tags, and confirm the new SHA belongs to that repository and to the tagged release rather than to a fork. Then let the pipeline run on the pull request, since the tests are the only check of whether the new version still works with your workflow. Merging it unread turns the pin back into a tag with extra steps.

</details>

## Real-world reps

- [ ] In `ci-cd-practice`, replace each `uses:` line in `ci.yml` with the full-SHA form, using `git ls-remote --tags` to find each SHA, keep the version as a comment, and push. Confirm the run still passes.
- [ ] Add `.github/dependabot.yml` from this lesson to `ci-cd-practice`. When the first pull request arrives, read what it changes and check the SHA against the action's repository before you merge it.
- [ ] Tomorrow: without notes, say why a tag is not a pin, what the tj-actions incident did, and what you do about a pinned action that has not changed in a year.

## Going further

- [Pipeline Security](../reference/pipeline-security.md)
- [Docs: "Secure use reference", GitHub](https://docs.github.com/en/actions/reference/security/secure-use)
- [Docs: "Keeping your actions up to date with Dependabot", GitHub](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/keeping-your-actions-up-to-date-with-dependabot)
- [Advisory: "Supply Chain Compromise of Third-Party tj-actions/changed-files", CISA](https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-tj-actionschanged-files-cve-2025-30066-and-reviewdogaction)
- [Repository: OpenSSF Scorecard](https://github.com/ossf/scorecard), which checks pinned dependencies and token permissions
- [Container Security](../../containers/reference/container-security.md), pinning a base image by digest
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
