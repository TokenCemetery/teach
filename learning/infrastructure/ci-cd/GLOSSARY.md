---
title: Glossary
description: "Canonical terms for building, testing and delivering changes through a pipeline"
type: glossary
---

# CI/CD Glossary

Canonical terms for the pipeline, the artifacts it produces and the deployments it performs. In this workspace "the pipeline" means every workflow that takes a change from a commit to production, "a run" is one execution of one workflow, and GitHub Actions keys are written in code as the workflow file spells them (`needs`, `runs-on`) when the key itself is meant.

## Terms

**Action**:
A reusable unit of steps, referenced from a step with `uses` and an owner, repository and version, such as `actions/checkout@<sha>`. A JavaScript, Docker container or composite action all look the same to the caller.
_Avoid_: plugin, task, step (a step may run an action, it is not one)

**Artifact**:
A file or set of files a run produces and keeps, such as a built binary, a test report or an image, identified so that later jobs and later stages use exactly that output.
_Avoid_: build output (vague), cache (a different thing)

**Artifact attestation**:
A signed statement, bound to an artifact's digest, recording what built it, from which commit and in which workflow. GitHub Actions generates and stores one with `actions/attest`, which `actions/attest-build-provenance` wraps from its version 4.
_Avoid_: signature (it signs a claim about the artifact, not only the artifact)

**Blue-green deployment**:
A deployment strategy that runs the new version beside the old one at full size and switches all traffic between them at once, so rollback is switching back.
_Avoid_: red-black, A/B deployment (A/B testing is an experiment, not a deployment)

**Build once**:
The rule that one build produces the artifact every later stage tests, promotes and deploys, so nothing shipped was rebuilt after it was tested.
_Avoid_: rebuild per environment

**Cache**:
Files saved by key so a later run can skip work, such as a dependency directory restored from the lockfile's hash. A cache may be missing or stale at any time and must only ever make a run faster.
_Avoid_: artifact (an artifact is kept on purpose and relied on)

**Canary**:
A deployment strategy that sends a small share of real traffic to the new version, compares its health against the old version, and widens or rolls back on that evidence.
_Avoid_: smoke test (no real traffic), beta

**Composite action**:
An action defined in an `action.yml` whose `runs` holds a list of steps, which run inside the caller's job and on the caller's runner.
_Avoid_: reusable workflow (a whole workflow of jobs)

**Concurrency group**:
A name under which GitHub Actions allows at most one running and one pending run or job, optionally cancelling the one in progress when a newer one arrives.
_Avoid_: lock, mutex, queue

**Continuous delivery**:
The practice of keeping the mainline releasable at all times, so any commit that passes the pipeline can be deployed to production at the push of a button.
_Avoid_: continuous deployment (that removes the button)

**Continuous deployment**:
The practice of deploying every change that passes the pipeline to production automatically, with no human decision in between.
_Avoid_: continuous delivery (that keeps the decision)

**Continuous integration**:
The practice of merging every developer's work into one mainline at least daily, with each merge proven by an automated build and test run that the team fixes at once when it breaks.
_Avoid_: CI server, running tests on pull requests (both are tools for it, not the practice)

**Critical path**:
The longest chain of dependent jobs in a run, which sets the run's wall-clock time however much else runs in parallel.
_Avoid_: total minutes (that is cost, not wait)

**Deployment strategy**:
The way a new version replaces the old one in an environment: recreate, rolling, blue-green or canary, each with its own cost in spare capacity and its own blast radius.
_Avoid_: release strategy (a release can happen after the deploy, through a flag)

**Digest**:
The content hash that identifies an image or other artifact exactly, such as `sha256:4f1c…`. Unlike a tag, it cannot be moved to different content.
_Avoid_: image ID, tag, version

**Environment**:
In GitHub Actions, a named deployment target, such as `staging` or `production`, with its own protection rules, secrets and variables, that a job enters with the `environment` key.
_Avoid_: stage (a stage is part of the pipeline), server

**Event**:
The activity on GitHub, or the schedule or manual dispatch, that starts a workflow run, such as `push` or `pull_request`, carrying a payload and a commit to run against.
_Avoid_: hook, trigger (use for the `on` key that names events)

**Expand and contract**:
Changing a schema in three deploys: add the new shape alongside the old one, move code and data to it, then remove the old one, so every version running during a deploy works.
_Avoid_: parallel change (the general pattern this applies), big-bang migration

**Expression**:
A `${{ ... }}` value in a workflow file, evaluated by GitHub Actions before a step runs, over contexts, literals, operators and functions.
_Avoid_: variable, template

**Feature flag**:
A runtime switch that turns code paths on or off without a deploy, which separates deploying a change from releasing it to users.
_Avoid_: toggle (alias, prefer one), config

**Flaky test**:
A test that passes and fails on the same code, because its result depends on timing, order, shared state or something outside the code under test.
_Avoid_: intermittent failure (that may be a real bug), random failure

**Gate job**:
A job that always runs, needs the jobs behind it, and fails when any of them failed or was cancelled, so it can be the one required status check a branch rule names.
_Avoid_: required workflow, summary job

**GitHub token**:
The `GITHUB_TOKEN` secret GitHub creates for each job, valid for that job only, with the permissions the workflow's `permissions` key grants it.
_Avoid_: personal access token (a long-lived token tied to a person)

**GitOps**:
Delivering changes by committing the desired state of an environment to Git, where an agent running in that environment pulls it and reconciles toward it continuously.
_Avoid_: push deploy, infrastructure as code (a broader idea)

**Job**:
A set of steps that runs on one runner. Jobs in a workflow run in parallel unless `needs` orders them, and share nothing but what they pass explicitly.
_Avoid_: stage (GitLab and Jenkins group jobs into stages), build

**Matrix**:
A job strategy that expands one job definition into one job per combination of the listed values, such as each runtime version on each operating system.
_Avoid_: loop, fan-out

**OIDC federation**:
Trust set up between a cloud provider and GitHub's OpenID Connect issuer, so a job exchanges a short-lived ID token, whose claims name its repository, branch and environment, for short-lived cloud credentials.
_Avoid_: keyless (something still signs), OIDC login

**Pin**:
To reference an action, image or dependency by an immutable identifier, a full commit SHA, a digest or a locked version with its hash, so the code that runs cannot change under the same reference.
_Avoid_: lock to a tag, version constraint (a range is not a pin)

**Pipeline**:
The automated path a change takes from a commit to production, made of one or more workflows: build, test, publish, deploy and verify.
_Avoid_: build (one part of it), CI (one practice it serves)

**Promotion**:
Deploying an artifact that has already passed one environment to the next, by its digest or version, without rebuilding it.
_Avoid_: redeploy, rebuild for production

**Provenance**:
Verifiable information about where, when and how an artifact was built: the source commit, the build workflow, the builder and its inputs. SLSA defines its format and levels.
_Avoid_: metadata (too general), SBOM (what is in it, not how it was made)

**Quarantine**:
Moving a flaky test out of the required checks into a job that does not block merging, with an owner and an issue, so its failures stay visible while it is fixed.
_Avoid_: skipping, disabling (both hide the failure)

**Required status check**:
A check, matched by name, that a branch protection rule or ruleset requires to succeed before a pull request can merge into a protected branch.
_Avoid_: required workflow (the check is per job name, not per workflow file)

**Reusable workflow**:
A workflow triggered by `workflow_call` that other workflows call as a job with `uses`, passing inputs and secrets, and that runs its own jobs on its own runners.
_Avoid_: composite action, template

**Roll forward**:
Fixing a bad release by deploying a new version with the fix, chosen when rolling back would break data or contracts that have already moved on.
_Avoid_: hotfix (one way to roll forward), fail forward

**Rollback**:
Returning an environment to the last version known to be good, by redeploying that version's artifact.
_Avoid_: revert (a Git operation that produces a new version), undo

**Rolling deployment**:
A deployment strategy that replaces instances of the old version with the new one a few at a time, so both run together until the rollout finishes.
_Avoid_: rolling restart (same version), incremental deploy

**Runner**:
The machine that executes a job, either a fresh GitHub-hosted virtual machine per job or a self-hosted machine that can keep state between jobs.
_Avoid_: agent (Jenkins term), executor, worker

**SBOM**:
A software bill of materials: a machine-readable list of the components, versions and licences inside an artifact, in a format such as SPDX or CycloneDX.
_Avoid_: dependency list, lockfile (a lockfile is an input, an SBOM describes the output)

**Script injection**:
An attack in which text an outsider controls, such as a pull request title, is expanded by an expression into a `run` script and executed as shell code on the runner.
_Avoid_: command injection (the general class), XSS

**Secret**:
An encrypted value stored in a repository, environment or organization, exposed to a job only when the workflow references it, and redacted from logs when printed verbatim.
_Avoid_: variable (configuration variables are not encrypted), credential (a secret may hold one)

**Step**:
One command or action inside a job. Steps run in order on the same runner and share its file system and environment.
_Avoid_: task, job

**Workflow**:
A YAML file in `.github/workflows/` that names the events it runs on and the jobs it runs.
_Avoid_: pipeline (the pipeline may span several workflows), action
