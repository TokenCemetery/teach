---
title: CI/CD
description: "Build, test and deliver every change through a pipeline and own it: workflows, fast feedback, artifacts, secrets, deployments, rollback and supply-chain security"
type: topic
---

# Learning: CI/CD

Take any service from a merged change to running in production through a pipeline you own: prove every change builds and passes its tests in minutes, produce one versioned artifact and promote that same artifact through environments, give the pipeline the access it needs without long-lived keys, deploy with a strategy that limits the damage of a bad release, and roll back when one gets out. End able to review someone else's pipeline by naming what will fail, slow down or leak first, change a workflow other teams depend on without breaking their merges, and say when the usual delivery answer is the wrong one.

**Latest lesson:** [30. When the Usual Answer Is Wrong](lessons/0030-when-the-usual-answer-is-wrong.md)

## Success looks like

- Explain what continuous integration, continuous delivery and continuous deployment each promise, and what a team has to practise for the promise to hold.
- Write a pipeline as code: triggers and events, jobs, steps and runners, actions, expressions, contexts and outputs.
- Run build and test stages that fail on the cheapest problem first, across a matrix, with caching, without trusting a flaky test, and fast enough that people wait for the result.
- Produce artifacts with a version traceable to a commit, build them once, and build, publish and reference a container image by digest.
- Give a pipeline secrets and cloud access with least privilege: scoped `GITHUB_TOKEN` permissions, OIDC instead of long-lived keys, and no path for untrusted input to reach either.
- Gate deployments with environments and approvals, and promote one artifact from staging to production.
- Deploy with rolling, blue-green and canary strategies, roll back or roll forward, order database migrations around a deploy, and choose between a push deploy and GitOps.
- Secure the supply chain: pin what the pipeline runs, and produce and verify provenance and SBOMs.
- Scale pipelines across repositories and monorepos with reusable workflows, composite actions and path filters, and debug a pipeline that fails only on the runner.
- Review someone else's pipeline, change a shared workflow or required check without breaking the teams that depend on it, say when the usual answer is wrong, and settle a disputed behaviour from the workflow syntax reference.

## Constraints

- Assumes comfort with Git, a shell and building and testing a project in one language. No prior knowledge of CI/CD. Lesson 13 assumes the [containers track](../containers/README.md) or equivalent, and lessons 19 and 22 assume the basics of the [Kubernetes track](../kubernetes/README.md).
- Teaches the tasks a pipeline performs and performs them with GitHub Actions, the way `programming/java` teaches the build lifecycle with Maven. Jenkins and GitLab CI appear only where their model genuinely differs.
- Every rep runs in a throwaway public repository on a free GitHub account, where GitHub-hosted runners cost nothing. Deployment reps deploy to a kind cluster created inside the job, so no cloud account is needed. Where a lesson depends on a cloud provider, such as an OIDC trust policy, it shows the part GitHub alone can show and marks the rest optional.

## Out of scope

- Building and testing one language's code. The language tracks own the commands a pipeline step runs, for example [Java: Testing and Build](../../programming/java/reference/testing-and-build.md), [Go: Toolchain Commands](../../programming/golang/reference/toolchain-commands.md), [Python: Project and Packaging](../../programming/python/reference/project-and-packaging.md) and [C#: Testing and Build](../../programming/csharp/reference/testing-and-build.md). This track runs those steps in a pipeline.
- Writing a Dockerfile and building an image by hand. That is the [containers track](../containers/README.md), whose [Dockerfile](../containers/reference/dockerfile.md) sheet is what lesson 13 builds in a pipeline.
- Running the workload once it is delivered: probes, rollouts as a cluster feature, packaging manifests. That is the [Kubernetes track](../kubernetes/README.md), whose [Packaging](../kubernetes/reference/packaging.md) sheet covers the manifests a deploy job applies. This track delivers the change to it, and teaches GitOps only far enough to choose it.
- Writing a migration that does not lock a table. That is [SQL](../../programming/sql/README.md), whose [Operating](../../programming/sql/reference/operating.md) sheet holds the migration safety table. This track orders migrations within a deploy.
- Installing and administering a CI server, writing JavaScript or Docker container actions, and mobile app store release.

## The arc

Ten stages, from what CI and CD promise to the judgment to review someone else's pipeline. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. What CI and CD are for | 0001 to 0002 | Integration, delivery and deployment as promises, trunk-based work, pipelines as code, the Jenkins and GitLab equivalents | Can say what a pipeline guarantees and read any workflow file as code |
| 2. Anatomy of a workflow | 0003 to 0005 | Events and filters, jobs, steps, runners, `needs`, actions, expressions, contexts and outputs | Can write a workflow that runs when intended and passes data between jobs |
| 3. Fast, trustworthy feedback | 0006 to 0010 | Stage ordering, service containers, matrices, caching, flaky tests, the critical path, concurrency and timeouts | Can run a pipeline people trust and wait for |
| 4. Artifacts and versioning | 0011 to 0013 | Artifacts against caches, build identity, build once, building and publishing an image by digest | Can produce one traceable artifact and hand the same one to every later stage |
| 5. Secrets and trust | 0014 to 0016 | Secrets, masking, `GITHUB_TOKEN` permissions, OIDC federation, script injection, `pull_request_target` | Can give a pipeline only the access it needs and keep untrusted input away from it |
| 6. Environments and promotion | 0017 to 0018 | Environments, protection rules, environment secrets, promoting one artifact with per-environment configuration | Can gate a production deploy and promote what staging tested |
| 7. Deploying and rolling back | 0019 to 0022 | Recreate, rolling, blue-green and canary, rollback, roll forward and flags, expand and contract migrations, push deploys and GitOps | Can deploy with a strategy that limits damage and undo a bad release |
| 8. Supply chain | 0023 to 0024 | Pinning actions and dependencies, Dependabot, SLSA provenance, artifact attestations, SBOMs | Can say what the pipeline ran and prove where an artifact came from |
| 9. Pipelines at scale | 0025 to 0027 | Reusable workflows, composite actions, path filters and required checks in monorepos, debug logging, runner differences | Can share pipeline logic across teams and find why a run failed |
| 10. Judgment | 0028 to 0030 | Reviewing a pipeline, changing a shared workflow or required check, when the usual answer is wrong, settling it from the workflow syntax reference | Trusted to make the call on a pipeline and to explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-what-ci-and-cd-promise.md) | What CI and CD Promise | Continuous integration keeps every change merged and proven on main, continuous delivery keeps main releasable, and continuous deployment ships every passing change |
| [0002](lessons/0002-pipelines-as-code.md) | Pipelines as Code | A workflow file in the repository is versioned, reviewed and run like the code it builds, and Jenkins and GitLab express the same idea |
| [0003](lessons/0003-triggers-and-events.md) | Triggers and Events | Start a workflow on a push, a pull request, a schedule or by hand, filter it by branch and path, and know which commit each event runs against |
| [0004](lessons/0004-jobs-steps-and-runners.md) | Jobs, Steps and Runners | Jobs run in parallel on fresh runners unless needs orders them, steps share one workspace, and hosted and self-hosted runners trade cost for control |
| [0005](lessons/0005-actions-expressions-and-outputs.md) | Actions, Expressions and Outputs | Reuse an action with uses, decide with if and expressions over contexts, and pass values between steps and jobs through outputs |
| [0006](lessons/0006-build-and-test-stages.md) | Build and Test Stages | Order lint, build, unit and integration stages so the cheapest failure comes first, with service containers for the tests that need a database |
| [0007](lessons/0007-matrix-builds.md) | Matrix Builds | Run one job across versions and platforms with a matrix, and control what fail-fast, include and exclude do to the run |
| [0008](lessons/0008-caching.md) | Caching | Key a cache on the lockfile, fall back with restore keys, and know what a cache must never be trusted to hold |
| [0009](lessons/0009-flaky-tests.md) | Flaky Tests | A test that fails without a code change destroys trust in the whole pipeline, so find its cause and quarantine it instead of hiding it behind retries |
| [0010](lessons/0010-making-a-pipeline-fast.md) | Making a Pipeline Fast | Shorten the critical path, cancel superseded runs with concurrency groups, and set timeouts so a stuck job cannot hold the queue |
| [0011](lessons/0011-artifacts.md) | Artifacts | Pass a build output between jobs and keep it after the run with artifacts, and why an artifact is not a cache |
| [0012](lessons/0012-versioning-a-build.md) | Versioning a Build | Give every build an identity traceable to its commit, and build it once so the thing tested is the thing shipped |
| [0013](lessons/0013-building-and-publishing-an-image.md) | Building and Publishing an Image | Build, tag and push a container image from a workflow, cache its layers, and hand later stages its digest |
| [0014](lessons/0014-secrets-and-the-github-token.md) | Secrets and the GITHUB_TOKEN | Store secrets per repository and environment, know what masking misses, and cut the GITHUB_TOKEN down with permissions |
| [0015](lessons/0015-oidc-instead-of-long-lived-keys.md) | OIDC Instead of Long-Lived Keys | Let a cloud trust a short-lived token issued for one run, and scope that trust with the subject claim |
| [0016](lessons/0016-untrusted-input.md) | Untrusted Input | Titles, branch names and fork code are attacker input, and pull_request_target with a checkout of the fork hands them your secrets |
| [0017](lessons/0017-environments-and-approvals.md) | Environments and Approvals | Gate a deploy with environments, required reviewers, deployment branch rules and environment secrets |
| [0018](lessons/0018-promotion-between-environments.md) | Promotion Between Environments | Move one built artifact from staging to production by digest, with configuration supplied per environment |
| [0019](lessons/0019-deployment-strategies.md) | Deployment Strategies | Recreate, rolling, blue-green and canary, what each costs in capacity and risk, and what a canary must measure to mean anything |
| [0020](lessons/0020-rollback-and-roll-forward.md) | Rollback and Roll Forward | Roll back by redeploying the last good artifact, roll forward when data has moved on, and separate deploy from release with flags |
| [0021](lessons/0021-database-migrations-in-a-deploy.md) | Database Migrations in a Deploy | Order schema changes around code with expand and contract so every version running during a deploy works against the schema |
| [0022](lessons/0022-push-deploys-and-gitops.md) | Push Deploys and GitOps | A pipeline that pushes to a cluster against an agent in the cluster that pulls from Git, and what each does to credentials and drift |
| [0023](lessons/0023-pinning-what-the-pipeline-runs.md) | Pinning What the Pipeline Runs | Pin third-party actions to a full commit SHA, lock dependencies, and keep the pins current with Dependabot |
| [0024](lessons/0024-provenance-and-sboms.md) | Provenance and SBOMs | Attest where an artifact was built and from what, list what is inside it, and verify both before it runs |
| [0025](lessons/0025-reusable-workflows-and-composite-actions.md) | Reusable Workflows and Composite Actions | Share pipeline logic across repositories with a called workflow or a composite action, and choose by what each can hold |
| [0026](lessons/0026-monorepos-and-path-filters.md) | Monorepos and Path Filters | Run only what a change touches with path filters, and why a skipped required check can block every merge |
| [0027](lessons/0027-debugging-a-pipeline.md) | Debugging a Pipeline | Read the log, rerun with debug logging, and find what differs between the runner and your machine when it passes locally |
| [0028](lessons/0028-reviewing-a-pipeline.md) | Reviewing a Pipeline | Review someone else's workflow by naming what will fail, slow down or leak first |
| [0029](lessons/0029-changing-a-shared-workflow.md) | Changing a Shared Workflow | Change a reusable workflow or a required check that other teams depend on without breaking their merges |
| [0030](lessons/0030-when-the-usual-answer-is-wrong.md) | When the Usual Answer Is Wrong | Say when continuous deployment, a canary or a pipeline default is the wrong call, and settle a disputed behaviour from the workflow syntax reference |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources, each annotated with what it covers
- [Workflow Syntax](reference/workflow-syntax.md): triggers, jobs, steps, expressions, contexts and outputs, with the Jenkins and GitLab equivalents, from stages 1 and 2
- [Fast Feedback](reference/fast-feedback.md): stage ordering, matrices, cache keys, flaky-test handling, concurrency and timeouts, from stage 3
- [Artifacts and Versioning](reference/artifacts-and-versioning.md): artifacts against caches, version schemes, build once, image tags and digests, from stage 4
- [Pipeline Security](reference/pipeline-security.md): secrets, token permissions, OIDC, untrusted input, pinning and provenance, from stages 5 and 8
- [Deployments](reference/deployments.md): environments, promotion, the four strategies, rollback, migration order and GitOps, from stages 6 and 7
- [Pipelines at Scale](reference/pipelines-at-scale.md): reusable workflows against composite actions, path filters, required checks and debugging a run, from stage 9
- [Pipeline Review Checklist](reference/pipeline-review-checklist.md): the questions to ask of someone else's pipeline, and when the usual answer is wrong, from stage 10

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
