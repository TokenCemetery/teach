---
title: Containers
description: "Package a service as a container image and own it: kernel primitives, Dockerfiles, running, securing and debugging one container"
type: topic
---

# Learning: Containers

Package any service as a container image and own what happens to it on one host: know what the kernel is doing when a container runs, write a Dockerfile that builds a small, reproducible image, run it so it shuts down cleanly and stays inside its limits, harden it, and debug it when it will not start. End able to review someone else's Dockerfile and image by naming what each choice costs.

**Latest lesson:** [24. When the Usual Answer Is Wrong](lessons/0024-when-the-usual-answer-is-wrong.md)

## Success looks like

- Explain what a container is in kernel terms (namespaces, cgroups and a layered root filesystem) and how that differs from a virtual machine.
- Read an image: its manifest, config and layers, the difference between a tag and a digest, and pull exactly the image that was tested.
- Write a Dockerfile that builds a small, cache-friendly and reproducible image, using a multi-stage build.
- Run a container that shuts down cleanly on a signal, reports its health, and stays within memory and CPU limits that the runtime inside it respects.
- Connect containers on one host: networking, published ports, volumes for state, and Compose for local development.
- Harden an image: a non-root user, the fewest privileges, a minimal base, a triaged vulnerability scan, secrets kept out of layers, and a signature and provenance to verify.
- Debug a container that will not start or misbehaves, from its exit code to inside its namespaces, including one with no shell.
- Review someone else's Dockerfile and image, roll a base-image change through the services that depend on it, and say when the usual answer is the wrong one.

## Constraints

- Assumes comfort on a Linux command line and having built and run a service in some language. No prior knowledge of containers.
- Uses the Docker CLI with BuildKit, because it is what most documentation and most teams use. Where a behaviour belongs to the OCI specifications rather than to Docker, the lesson says so, and the same commands mostly work in Podman.
- Stage 1 reps need a Linux shell with root, such as a Linux machine or virtual machine. On a laptop running Docker Desktop, the containers themselves run inside a Linux virtual machine that Docker Desktop manages.

## Out of scope

- Building the runnable artifact for one language. The language tracks own that and this track puts their output into an image: [Go: Toolchain Commands](../../programming/golang/reference/toolchain-commands.md) for static binaries, [Java: Testing and Build](../../programming/java/reference/testing-and-build.md) and [The Module System](../../programming/java/reference/the-module-system.md) for runnable artifacts and `jlink`, [C#: Shipping the Service](../../programming/csharp/reference/shipping-the-service.md), and [Python: Project and Packaging](../../programming/python/reference/project-and-packaging.md) for wheels.
- Orchestrating containers across a cluster: scheduling, services, rollouts, probes as a cluster feature. That is the [Kubernetes track](../kubernetes/README.md). This track stops at one container, or a handful, on one host.
- Building and publishing images in a pipeline. That is a planned `infrastructure/ci-cd` track ([#159](https://github.com/TokenCemetery/teach/issues/159)). This track builds images by hand so that what a pipeline automates is understood first.
- Windows containers, and writing a container runtime.

## The arc

Eight stages, from what a container is to the judgment to review someone else's image. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. What a container is | 0001 to 0003 | A container as a process, namespaces, cgroups, the difference from a virtual machine | Can build a container's isolation by hand and say what each piece hides or limits |
| 2. Images | 0004 to 0006 | Manifest, config and layers, overlayfs, the runtime stack and lifecycle, registries, tags and digests | Can read an image and pull exactly the one that was tested |
| 3. Building images | 0007 to 0010 | Dockerfile instructions and the build context, the build cache, multi-stage builds and base images, reproducibility | Can write a Dockerfile that builds a small, cache-friendly, reproducible image |
| 4. Running one container | 0011 to 0013 | PID 1 and signals, health checks and restart policies, memory and CPU limits | Can run a container that stops cleanly, reports its health and respects its limits |
| 5. Networking, storage and Compose | 0014 to 0016 | Bridge networks and published ports, volumes and bind mounts, Compose for local development | Can run a service and its dependencies together on one host with state that survives |
| 6. Security | 0017 to 0019 | Non-root, capabilities and privilege, minimal bases and scanning, build secrets, signing and provenance | Can harden an image and verify where one came from |
| 7. Debugging | 0020 to 0021 | Exit codes, logs and inspect, overriding the entrypoint, joining a container's namespaces | Can find out why a container will not start or misbehaves, even without a shell |
| 8. Judgment | 0022 to 0024 | Reviewing a Dockerfile, changing a base image others depend on, when the usual answer is wrong, settling it from the specification | Trusted to make the call on an image and to explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-a-container-is-a-process.md) | A Container Is a Process | A container is an ordinary Linux process the kernel shows a restricted view of the machine, not a small virtual machine |
| [0002](lessons/0002-namespaces.md) | Namespaces | Each namespace type hides one kind of global resource, and unshare builds a container's view one namespace at a time |
| [0003](lessons/0003-cgroups.md) | Cgroups | Control groups cap and account for a process tree's memory, CPU and PIDs, and what the kernel does when a limit is hit |
| [0004](lessons/0004-images-and-layers.md) | Images and Layers | An OCI image is a manifest, a config and a stack of layer tarballs that overlayfs merges into one root filesystem |
| [0005](lessons/0005-from-image-to-running-container.md) | From Image to Running Container | What docker run does between the image and the process: the runtime stack, the writable layer and the lifecycle |
| [0006](lessons/0006-registries-tags-and-digests.md) | Registries, Tags and Digests | A tag is a movable name and a digest is the content's hash, so pull by digest to run exactly what was tested |
| [0007](lessons/0007-your-first-dockerfile.md) | Your First Dockerfile | The instructions that build an image, the build context, and what .dockerignore keeps out of it |
| [0008](lessons/0008-the-build-cache.md) | The Build Cache | When a cached layer is reused, what invalidates it and every layer after it, and how instruction order decides rebuild time |
| [0009](lessons/0009-multi-stage-builds.md) | Multi-Stage Builds | Build in one stage, copy only the artifact into a minimal final stage, and what each base image choice costs |
| [0010](lessons/0010-reproducible-builds.md) | Reproducible Builds | What makes two builds of the same Dockerfile differ, and pinning bases, packages and timestamps so they do not |
| [0011](lessons/0011-pid-1-and-signals.md) | PID 1 and Signals | Why a container ignores SIGTERM when its process is PID 1 or wrapped in a shell, and how to shut down gracefully |
| [0012](lessons/0012-health-checks-and-restart-policies.md) | Health Checks and Restart Policies | Report whether the process inside is actually working, and decide what the runtime does when it stops |
| [0013](lessons/0013-resource-limits-in-practice.md) | Resource Limits in Practice | Set memory and CPU limits, read an OOM kill and CPU throttling, and check the runtime inside sees the limit |
| [0014](lessons/0014-container-networking.md) | Container Networking | Network namespaces, veth pairs and a bridge connect containers, and publishing a port adds a NAT rule on the host |
| [0015](lessons/0015-volumes-and-state.md) | Volumes and State | Where data outlives a container in named volumes, bind mounts and tmpfs, and the file-ownership trap between host and container |
| [0016](lessons/0016-compose-for-local-development.md) | Compose for Local Development | Describe a service and its dependencies in one Compose file, and wait for a dependency to be healthy rather than started |
| [0017](lessons/0017-least-privilege.md) | Least Privilege | Run as a non-root user, drop capabilities, keep the root filesystem read-only, and know what privileged mode and the Docker socket hand over |
| [0018](lessons/0018-minimal-bases-and-scanning.md) | Minimal Bases and Scanning | Shrink what an image contains, read a vulnerability scan, and triage its findings instead of chasing a zero count |
| [0019](lessons/0019-secrets-signing-and-provenance.md) | Secrets, Signing and Provenance | Keep secrets out of layers, sign an image by digest, and verify where it was built before running it |
| [0020](lessons/0020-a-container-that-will-not-start.md) | A Container That Will Not Start | Read the exit code, the logs and the inspect output, then override the entrypoint to find out why it stopped |
| [0021](lessons/0021-debugging-a-running-container.md) | Debugging a Running Container | Get inside a container that has no shell by joining its namespaces from a debug container or from the host |
| [0022](lessons/0022-reviewing-a-dockerfile.md) | Reviewing a Dockerfile | Review someone else's Dockerfile and image by naming what each choice costs in size, rebuild time, security and reliability |
| [0023](lessons/0023-changing-a-base-image-others-depend-on.md) | Changing a Base Image Others Depend On | Roll a shared base image forward without breaking the services built on it, using tags, digests, rebuilds and deprecation |
| [0024](lessons/0024-when-the-usual-answer-is-wrong.md) | When the Usual Answer Is Wrong | Recognise when Alpine, distroless, a pinned digest or a container at all is the wrong call, and settle it from the specification |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources, each annotated with what it covers
- [Container Primitives](reference/container-primitives.md): namespaces, cgroups, the image layout and tags against digests, from stages 1 and 2
- [Dockerfile](reference/dockerfile.md): instructions, cache rules, multi-stage patterns, base images and reproducibility, from stage 3
- [Running Containers](reference/running-containers.md): signals, health checks, limits, networking, volumes and Compose, from stages 4 and 5
- [Container Security](reference/container-security.md): privileges, minimal bases, scan triage, build secrets, signing and provenance, from stage 6
- [Debugging Containers](reference/debugging-containers.md): exit codes, the commands to run in order, and how to get inside a container without a shell, from stage 7
- [Dockerfile Review Checklist](reference/dockerfile-review-checklist.md): the questions to ask of someone else's Dockerfile and image, and when the usual answer is wrong, from stage 8

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
