---
title: Resources
description: "Trusted sources for building, testing and delivering changes through a pipeline"
type: resources
---

# CI/CD Resources

## Knowledge

### What CI and CD are for

- [Article: "Continuous Integration", Martin Fowler](https://martinfowler.com/articles/continuousIntegration.html)
  The practices that make integration continuous: one mainline, a self-testing build, committing daily, fixing a broken build at once. Use for: lesson 1, and what a pipeline alone cannot give a team.
- [Article: "Continuous Delivery", Martin Fowler](https://martinfowler.com/bliki/ContinuousDelivery.html)
  Delivery against deployment in one page: software that is always releasable, against software that is always released. Use for: lesson 1.
- [Site: "Continuous Delivery", Jez Humble](https://continuousdelivery.com/)
  The principles and the deployment pipeline from the authors of the book of the same name. Use for: lesson 1, the deployment pipeline as a whole.
- [Site: "Continuous Delivery: patterns", Jez Humble](https://continuousdelivery.com/implementing/patterns/)
  Build packages once, deploy the same way to every environment, smoke test, decouple deployment from release. Use for: lessons 12, 18 and 20.
- [Guide: "DORA's software delivery metrics", DORA](https://dora.dev/guides/dora-metrics-four-keys/)
  The five software delivery metrics, grouped into throughput (change lead time, deployment frequency, failed deployment recovery time) and instability (change fail rate, deployment rework rate). Use for: lessons 1 and 30, judging a pipeline by outcomes rather than by features.
- [Docs: "Understanding GitHub Actions", GitHub](https://docs.github.com/en/actions/get-started/understand-github-actions)
  Workflows, events, jobs, steps, actions and runners, and how they fit together. Use for: lessons 2 and 4.
- [Docs: "Pipeline", Jenkins User Documentation](https://www.jenkins.io/doc/book/pipeline/)
  The Jenkinsfile, declarative and scripted pipelines, stages and agents. Use for: lesson 2, where Jenkins differs from a hosted workflow service.
- [Docs: "Pipeline Syntax", Jenkins User Documentation](https://www.jenkins.io/doc/book/pipeline/syntax/)
  `agent`, `stages`, `triggers`, `when`, `post`, `parallel` and `matrix` in Declarative Pipeline. Use for: lesson 2 and the Jenkins column of the workflow syntax sheet.
- [Docs: "CI/CD YAML syntax reference", GitLab](https://docs.gitlab.com/ci/yaml/)
  Every keyword in `.gitlab-ci.yml`: stages, jobs, rules, needs, artifacts and environments. Use for: lessons 2 and 4, the GitLab model of stages.
- [Docs: "CI/CD pipelines", GitLab](https://docs.gitlab.com/ci/pipelines/)
  Pipelines as stages run in sequence, with the jobs in one stage run in parallel. Use for: lessons 2 and 6.

### Anatomy of a workflow

- [Docs: "Workflow syntax for GitHub Actions", GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
  Every key a workflow file accepts, with defaults. Use for: every lesson, and the source that settles a disputed behaviour in lesson 30.
- [Docs: "Events that trigger workflows", GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
  Each event, its activity types, and the `GITHUB_SHA` and `GITHUB_REF` it runs against. Use for: lessons 3 and 16.
- [Docs: "Triggering a workflow", GitHub](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)
  Branch, tag and path filters, and when events from a workflow do not start another one. Use for: lessons 3 and 26.
- [Docs: "Using jobs in a workflow", GitHub](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs)
  Job IDs, `needs`, and how dependent jobs are skipped when one fails. Use for: lesson 4.
- [Docs: "GitHub-hosted runners", GitHub](https://docs.github.com/en/actions/concepts/runners/github-hosted-runners)
  The images, the fresh virtual machine per job, and the preinstalled software. Use for: lessons 4 and 27.
- [Docs: "Self-hosted runners", GitHub](https://docs.github.com/en/actions/concepts/runners/self-hosted-runners)
  Running your own runners, and why they persist state between jobs. Use for: lessons 4 and 16.
- [Docs: "GitHub-hosted runners reference", GitHub](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
  Runner labels and images, and that a `-latest` label is the latest stable image, not always the newest operating system. Use for: lessons 27 and 30.
- [Docs: "Contexts reference", GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts)
  The `github`, `env`, `job`, `steps`, `needs`, `matrix` and `secrets` contexts, and where each is available. Use for: lesson 5.
- [Docs: "Evaluate expressions in workflows and actions", GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/expressions)
  Operators, functions and the status check functions `success()`, `failure()`, `always()` and `cancelled()`. Use for: lesson 5.
- [Docs: "Passing information between jobs", GitHub](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/pass-job-outputs)
  Step outputs through `GITHUB_OUTPUT` and job outputs read through `needs`. Use for: lesson 5.
- [Docs: "Workflow commands for GitHub Actions", GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands)
  `GITHUB_OUTPUT`, `GITHUB_ENV`, masking a value and grouping log lines. Use for: lessons 5, 14 and 27.
- [Docs: "Store information in variables", GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/variables)
  The default environment variables and configuration variables. Use for: lessons 5 and 12.

### Fast, trustworthy feedback

- [Docs: "Using Docker service containers", GitHub](https://docs.github.com/en/actions/tutorials/use-containerized-services/use-docker-service-containers)
  Running a database beside a job, its health check and how the job reaches it. Use for: lesson 6.
- [Docs: "Creating PostgreSQL service containers", GitHub](https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers)
  A worked Postgres service with health options and port mapping. Use for: lesson 6.
- [Docs: "Running variations of jobs in a workflow", GitHub](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations)
  Matrix strategies, `include`, `exclude`, `fail-fast` and `max-parallel`. Use for: lesson 7.
- [Docs: "Dependency caching reference", GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching)
  Cache keys, restore keys, which branches a run may read a cache from, the read-only caches of low-trust triggers, size limits and eviction. Use for: lesson 8.
- [Repository: actions/cache, GitHub](https://github.com/actions/cache)
  The cache action's inputs and outputs, including `cache-hit`. Use for: lesson 8.
- [Repository: actions/setup-python, GitHub](https://github.com/actions/setup-python)
  The built-in `cache: pip` option and quoting Python versions in a matrix. Use for: lessons 7 and 8.
- [Article: "Flaky Tests at Google and How We Mitigate Them", John Micco, Google Testing Blog](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html)
  How common flakiness is at scale and the mitigations that work. Use for: lesson 9.
- [Article: "Eradicating Non-Determinism in Tests", Martin Fowler](https://martinfowler.com/articles/nonDeterminism.html)
  Why a non-deterministic test is worse than none, quarantine, and the usual causes: isolation, async, remote services, time. Use for: lesson 9.
- [Docs: pytest-randomly, PyPI](https://pypi.org/project/pytest-randomly/)
  Shuffles test order, prints the seed, and replays an order with `--randomly-seed`. Use for: lesson 9, exposing order-dependent tests.
- [Docs: pytest-rerunfailures, PyPI](https://pypi.org/project/pytest-rerunfailures/)
  Rerunning failed tests with `--reruns`, the retry that hides flakiness when left on. Use for: lesson 9.
- [Docs: "Control the concurrency of workflows and jobs", GitHub](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)
  Concurrency groups and `cancel-in-progress`. Use for: lessons 10 and 17.
- [Docs: "Actions limits", GitHub](https://docs.github.com/en/actions/reference/limits)
  Job execution time, concurrency, matrix size and other limits. Use for: lessons 7 and 10.

### Artifacts and versioning

- [Docs: "Workflow artifacts", GitHub](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts)
  What an artifact is, retention, and how it differs from a cache. Use for: lesson 11.
- [Docs: "Store and share data with workflow artifacts", GitHub](https://docs.github.com/en/actions/tutorials/store-and-share-data)
  Uploading in one job and downloading in another. Use for: lesson 11.
- [Repository: actions/upload-artifact, GitHub](https://github.com/actions/upload-artifact)
  The upload action's inputs, retention and the rule that an artifact name is immutable within a run. Use for: lesson 11.
- [Docs: "Removing workflow artifacts", GitHub](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/remove-workflow-artifacts)
  Default retention, per-artifact retention and deleting artifacts. Use for: lesson 11.
- [Docs: "Recording tests and artifacts", Jenkins pipeline tour](https://www.jenkins.io/doc/pipeline/tour/tests-and-artifacts/)
  The `archiveArtifacts` step and fingerprinting, the Jenkins counterpart of uploading an artifact. Use for: lesson 11.
- [Specification: "Semantic Versioning 2.0.0"](https://semver.org/)
  What major, minor and patch promise, and pre-release and build metadata. Use for: lesson 12, and lesson 29 when versioning a shared workflow.
- [Docs: "GitHub Actions", Docker Docs](https://docs.docker.com/build/ci/github-actions/)
  The official Docker actions for logging in, building, tagging and pushing with BuildKit. Use for: lesson 13.
- [Docs: "Cache management with GitHub Actions", Docker Docs](https://docs.docker.com/build/ci/github-actions/cache/)
  The `gha` and registry cache backends for BuildKit layers. Use for: lesson 13.
- [Docs: "Publishing Docker images", GitHub](https://docs.github.com/en/actions/how-tos/use-cases-and-examples/publishing-packages/publishing-docker-images)
  Pushing to GitHub Container Registry with the `GITHUB_TOKEN`, with tags from metadata. Use for: lesson 13.
- [Docs: "Working with the Container registry", GitHub](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
  Default private visibility, linking a package to a repository, and why the `GITHUB_TOKEN` may be refused on a package pushed earlier. Use for: lessons 13 and 18.
- [Repository: docker/metadata-action](https://github.com/docker/metadata-action)
  Tag types, the `latest` rule and image name sanitizing. Use for: lesson 13.

### Secrets and trust

- [Docs: "Secrets", GitHub](https://docs.github.com/en/actions/concepts/security/secrets)
  Repository, environment and organization secrets, redaction in logs, and why fork pull requests receive none. Use for: lesson 14.
- [Docs: "Using secrets in GitHub Actions", GitHub](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets)
  Creating secrets and passing them to steps. Use for: lesson 14.
- [Docs: "GITHUB_TOKEN", GitHub](https://docs.github.com/en/actions/concepts/security/github_token)
  The per-job token, its lifetime, its default permissions and the `permissions` key. Use for: lesson 14.
- [Docs: "Use GITHUB_TOKEN for authentication in workflows", GitHub](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token)
  Passing the token to actions and the API, and that any action in the job can read it. Use for: lesson 14.
- [Docs: "OpenID Connect", GitHub](https://docs.github.com/en/actions/concepts/security/openid-connect)
  How a job requests an ID token and a cloud provider exchanges it for short-lived credentials. Use for: lesson 15.
- [Docs: "OpenID Connect reference", GitHub](https://docs.github.com/en/actions/reference/security/oidc)
  The token's claims, the subject formats per event, and customizing them. Use for: lesson 15.
- [Docs: "Configuring OpenID Connect in Amazon Web Services", GitHub](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws)
  A complete trust policy with audience and subject conditions, as one worked provider. Use for: lesson 15.
- [Docs: "Secure use reference", GitHub](https://docs.github.com/en/actions/reference/security/secure-use)
  Hardening guidance: script injection, pinning, token permissions, self-hosted runner risk. Use for: lessons 16, 23 and 28.
- [Docs: "Script injections", GitHub](https://docs.github.com/en/actions/concepts/security/script-injections)
  Which contexts carry attacker-controlled text and why an intermediate environment variable stops it. Use for: lesson 16.
- [Article: "Keeping your GitHub Actions and workflows secure Part 1: Preventing pwn requests", GitHub Security Lab](https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/)
  Why `pull_request_target` and `workflow_run` with a checkout of fork code expose secrets. Use for: lesson 16.
- [Docs: "Securely using pull_request_target", GitHub](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)
  What the event can reach, the checkout protections, and the safe patterns for workflows that must use it. Use for: lesson 16.
- [Article: "Keeping your GitHub Actions and workflows secure Part 2: Untrusted input", GitHub Security Lab](https://securitylab.github.com/resources/github-actions-untrusted-input/)
  Worked injection attacks through titles, bodies and branch names. Use for: lesson 16.

### Environments and promotion

- [Docs: "Deployment environments", GitHub](https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments)
  Protection rules, required reviewers, wait timers, deployment branches and environment secrets. Use for: lesson 17.
- [Docs: "Managing environments for deployment", GitHub](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)
  Creating and configuring an environment. Use for: lesson 17.
- [Docs: "Deployments and environments", GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
  Referencing an environment from a job and the deployment history it records. Use for: lessons 17 and 18.

### Deploying and rolling back

- [Book chapter: "Canarying Releases", The Site Reliability Workbook, Google](https://sre.google/workbook/canarying-releases/)
  Canary population, duration, the metrics to compare and why a canary must be evaluated against a control. Use for: lesson 19.
- [Book chapter: "Release Engineering", Site Reliability Engineering, Google](https://sre.google/sre-book/release-engineering/)
  Hermetic builds, self-service releases and why the release process is code. Use for: lessons 12 and 20.
- [Article: "BlueGreenDeployment", Martin Fowler](https://martinfowler.com/bliki/BlueGreenDeployment.html)
  Two production environments and switching the router between them. Use for: lesson 19.
- [Repository: helm/kind-action](https://github.com/helm/kind-action)
  Creating a kind cluster inside a job, the target every deployment rep in this track uses. Use for: lessons 18 to 22.
- [Article: "CanaryRelease", Danilo Sato](https://martinfowler.com/bliki/CanaryRelease.html)
  Routing a small share of users to a new version first, and what it needs. Use for: lesson 19.
- [Article: "Feature Toggles (aka Feature Flags)", Pete Hodgson](https://martinfowler.com/articles/feature-toggles.html)
  Release, experiment, ops and permission toggles, and what each costs to keep. Use for: lesson 20, separating deploy from release.
- [Article: "ParallelChange", Danilo Sato](https://martinfowler.com/bliki/ParallelChange.html)
  Expand, migrate and contract, the pattern behind changing an interface without a coordinated cut-over. Use for: lesson 21.
- [Site: "OpenGitOps Principles", OpenGitOps, CNCF](https://opengitops.dev/)
  The four GitOps principles: declarative, versioned, pulled automatically, continuously reconciled. Use for: lesson 22.
- [Docs: "Declarative Management of Kubernetes Objects Using Configuration Files", Kubernetes](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/declarative-config/)
  How `kubectl apply` merges a file into the live object and what it does to a field edited by hand. Use for: lesson 22, the drift a push deploy leaves.
- [Docs: "Argo CD", Argo Project](https://argo-cd.readthedocs.io/en/stable/)
  An agent in the cluster that syncs it to manifests in Git and reports drift. Use for: lesson 22.
- [Docs: "Core Concepts", Flux](https://fluxcd.io/flux/concepts/)
  Sources, reconciliation and drift in the other widely used GitOps agent. Use for: lesson 22.

### Supply chain

- [Docs: "Keeping your actions up to date with Dependabot", GitHub](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/keeping-your-actions-up-to-date-with-dependabot)
  A `github-actions` ecosystem entry that opens pull requests to bump pinned actions. Use for: lesson 23.
- [Advisory: "Supply Chain Compromise of Third-Party tj-actions/changed-files (CVE-2025-30066) and reviewdog/action-setup@v1 (CVE-2025-30154)", CISA](https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-tj-actionschanged-files-cve-2025-30066-and-reviewdogaction)
  A widely used action compromised to leak the secrets of every workflow that ran it, with the exposure window and the rotation advice. Use for: lesson 23, what a compromised action costs.
- [Advisory: "tj-actions changed-files through 45.0.7 allows remote attackers to discover secrets by reading actions logs", GitHub Advisory Database](https://github.com/advisories/GHSA-mrrh-fwg8-r2c3)
  The version tags retroactively moved to a malicious commit that printed secrets to logs. Use for: lesson 23, why a tag is not a pin.
- [Docs: "Workflow dependency lockfiles", GitHub](https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles)
  Locking the actions a workflow resolves to, a feature in public preview. Use for: lesson 23.
- [Docs: "Secure installs", pip](https://pip.pypa.io/en/stable/topics/secure-installs/)
  Hash-checking mode and `--require-hashes`, locking a dependency to its content. Use for: lesson 23.
- [Specification: "SLSA Security Levels", SLSA v1.0](https://slsa.dev/spec/v1.0/levels)
  The build track levels and what each one guarantees about provenance. Use for: lesson 24.
- [Docs: "Artifact attestations", GitHub](https://docs.github.com/en/actions/concepts/security/artifact-attestations)
  Signed build provenance and SBOM attestations, and the SLSA level they reach. Use for: lesson 24.
- [Docs: "Using artifact attestations to establish provenance for builds", GitHub](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations)
  Generating an attestation in a workflow and verifying it with `gh attestation verify`. Use for: lesson 24.
- [Repository: actions/attest, GitHub](https://github.com/actions/attest)
  The attestation action's inputs, SBOM attestations and required permissions. Use for: lesson 24.
- [Docs: "gh attestation verify", GitHub CLI manual](https://cli.github.com/manual/gh_attestation_verify)
  Verification policy flags such as `--repo`, `--signer-workflow` and `--predicate-type`. Use for: lesson 24.
- [Specification: CycloneDX, OWASP](https://cyclonedx.org/)
  One of the two common SBOM formats. Use for: lesson 24.
- [Specification: SPDX, Linux Foundation](https://spdx.dev/)
  The other common SBOM format, an ISO standard. Use for: lesson 24.
- [Repository: OpenSSF Scorecard](https://github.com/ossf/scorecard)
  Automated checks of a repository's practices, including pinned dependencies and token permissions in workflows. Use for: lessons 23 and 28.
- [Docs: "Checks", OpenSSF Scorecard](https://github.com/ossf/scorecard/blob/main/docs/checks.md)
  What Token-Permissions, Pinned-Dependencies and Dangerous-Workflow each look for and why. Use for: lesson 28.

### Pipelines at scale

- [Docs: "Reusing workflow configurations", GitHub](https://docs.github.com/en/actions/concepts/workflows-and-actions/reusing-workflow-configurations)
  Reusable workflows against composite actions and what each one can contain. Use for: lesson 25.
- [Docs: "Reuse workflows", GitHub](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)
  `workflow_call`, inputs, secrets, outputs and how a caller references a version. Use for: lessons 25 and 29.
- [Docs: "Reusable workflows reference", GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/reusable-workflows)
  Nesting limits, which contexts pass through, and how permissions flow. Use for: lessons 25 and 29.
- [Docs: "Creating a composite action", GitHub](https://docs.github.com/en/actions/tutorials/create-actions/create-a-composite-action)
  An `action.yml` that bundles steps. Use for: lesson 25.
- [Docs: "Troubleshooting required status checks", GitHub](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)
  Why a check skipped by a path filter stays pending and blocks a merge, and the job-level alternative. Use for: lessons 26 and 29.
- [Docs: "About status checks", GitHub](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks)
  Check states, and that a job skipped by a condition reports success. Use for: lesson 26.
- [Docs: "About protected branches", GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
  Required status checks and how a check is matched by name. Use for: lessons 26 and 29.
- [Docs: "Enabling debug logging", GitHub](https://docs.github.com/en/actions/how-tos/monitor-workflows/enable-debug-logging)
  Runner and step debug logs and the variables that turn them on. Use for: lesson 27.
- [Docs: "Using workflow run logs", GitHub](https://docs.github.com/en/actions/how-tos/monitor-workflows/use-workflow-run-logs)
  Reading, searching and downloading the log of a run. Use for: lesson 27.
- [Docs: "Re-running workflows and jobs", GitHub](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs)
  Rerunning all jobs or only the failed ones, with debug logging. Use for: lessons 9 and 27.
- [Repository: actionlint](https://github.com/rhysd/actionlint)
  A static checker for workflow files, including expression types and shell scripts in `run`. Use for: lessons 27 and 28.
- [Repository: act](https://github.com/nektos/act)
  Runs workflows locally in containers, with the differences from a hosted runner it documents. Use for: lesson 27.

## Gaps

- No vendor-neutral primary source defines a pipeline review checklist. Lesson 28 assembles one from GitHub's secure use reference, OpenSSF Scorecard checks and the practices in Fowler's continuous integration article, and says where an item is judgment rather than fact.
- GitHub Actions changes often: runner images, default token permissions and attestation features move between announcements. The lessons cite the current docs page for each behaviour, and that page, not the lesson, is the source when they disagree.
- Deployment strategies are documented per platform. Lessons 19 and 20 teach them from the SRE Workbook and Fowler's articles and show them with Kubernetes objects, and a different target platform's documentation is the source for how it implements each one.
