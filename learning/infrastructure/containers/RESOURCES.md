---
title: Resources
description: "Trusted sources for containers and container images"
type: resources
---

# Containers Resources

## Knowledge

### Kernel primitives

- [Man page: namespaces(7), Linux man-pages project](https://man7.org/linux/man-pages/man7/namespaces.7.html)
  The kernel's own description of every namespace type, what each isolates, and the `/proc/<pid>/ns` files. Use for: lesson 2, and settling what a namespace does and does not hide.
- [Man page: user_namespaces(7), Linux man-pages project](https://man7.org/linux/man-pages/man7/user_namespaces.7.html)
  How UID and GID mappings work and what capabilities mean inside a user namespace. Use for: rootless mode and why root in a container need not be root on the host.
- [Man page: unshare(1), Linux man-pages project](https://man7.org/linux/man-pages/man1/unshare.1.html)
  The command that runs a program in new namespaces. Use for: the stage 1 reps that build a container's isolation by hand.
- [Man page: nsenter(1), Linux man-pages project](https://man7.org/linux/man-pages/man1/nsenter.1.html)
  The command that runs a program inside an existing process's namespaces. Use for: lesson 21, debugging a container from the host.
- [Man page: cgroups(7), Linux man-pages project](https://man7.org/linux/man-pages/man7/cgroups.7.html)
  The overview of cgroups v1 and v2, controllers and the cgroup filesystem. Use for: lesson 3, before the kernel's v2 document.
- [Docs: "Control Group v2", Linux kernel documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html)
  The authoritative description of cgroup v2: the unified hierarchy, `memory.max`, `memory.events`, `cpu.max` and `cpu.stat`. Use for: what a limit file means and what the kernel does when it is hit, in lessons 3 and 13.
- [Man page: capabilities(7), Linux man-pages project](https://man7.org/linux/man-pages/man7/capabilities.7.html)
  Every Linux capability and what it permits. Use for: lesson 17, deciding which capabilities a container can drop.
- [Docs: "Overlay Filesystem", Linux kernel documentation](https://docs.kernel.org/filesystems/overlayfs.html)
  How overlayfs merges lower and upper directories, copy-up and whiteouts. Use for: lesson 4, what happens to a file a container changes or deletes.
- [Article: "Namespaces in operation, part 1", Michael Kerrisk, LWN.net, 2013](https://lwn.net/Articles/531114/)
  The start of a series by the man-pages maintainer that walks through each namespace with small C programs. Use for: a deeper read on namespaces after lesson 2.
- [Talk: "Containers From Scratch", Liz Rice, GOTO 2018](https://www.youtube.com/watch?v=8fi7uSYlOdc)
  A container built live in a few dozen lines of Go from namespaces, chroot and cgroups. Use for: seeing stage 1 assembled end to end.
- [Article: "What even is a container: namespaces and cgroups", Julia Evans, 2016](https://jvns.ca/blog/2016/10/10/what-even-is-a-container/)
  A short, plain-language tour of the pieces a container is made of. Use for: a second explanation of lesson 1 if the first did not land.
- [Article series: "Learning Containers From the Bottom Up", Ivan Velichko](https://iximiuz.com/en/posts/container-learning-path/)
  A curated path through container internals, runtimes, images and networking, with diagrams and hands-on experiments. Use for: going deeper than a lesson on any of stages 1, 2 and 5.

### The OCI specifications

- [Spec: OCI Image Format Specification](https://github.com/opencontainers/image-spec/blob/main/spec.md)
  The standard for what an image is. Use for: settling any question about images from the source, in lessons 4, 6 and 24.
- [Spec: OCI Image Manifest](https://github.com/opencontainers/image-spec/blob/main/manifest.md)
  The fields of a manifest and how it points at a config and layers by digest. Use for: lesson 4, reading a manifest.
- [Spec: OCI Image Index](https://github.com/opencontainers/image-spec/blob/main/image-index.md)
  The multi-platform index that resolves one name to a per-platform manifest. Use for: lesson 6, why the same tag pulls different bytes on different hosts.
- [Spec: OCI Image Layer Filesystem Changeset](https://github.com/opencontainers/image-spec/blob/main/layer.md)
  How a layer encodes additions, changes and deletions, including whiteout files. Use for: why deleting a file in a later layer does not shrink an image.
- [Spec: OCI Image Configuration](https://github.com/opencontainers/image-spec/blob/main/config.md)
  The config fields (`Entrypoint`, `Cmd`, `Env`, `User`, `rootfs.diff_ids`) and their meaning. Use for: lesson 4, and what an image says about how to run it.
- [Spec: OCI Runtime Specification](https://github.com/opencontainers/runtime-spec/blob/main/spec.md)
  The bundle, the `config.json` and the lifecycle a runtime such as runc implements. Use for: lesson 5, what happens between "create" and "start".
- [Spec: OCI Distribution Specification](https://github.com/opencontainers/distribution-spec/blob/main/spec.md)
  The HTTP API a registry serves for pulling and pushing by tag and by digest. Use for: lesson 6, what a pull actually requests.
- [Repo: runc, Open Container Initiative](https://github.com/opencontainers/runc)
  The reference low-level runtime that creates namespaces and cgroups from an OCI bundle. Use for: lesson 5, the bottom of the runtime stack.

### Building images

- [Docs: Dockerfile reference, Docker](https://docs.docker.com/reference/dockerfile/)
  Every instruction, shell form against exec form, how `ENTRYPOINT` and `CMD` interact, `HEALTHCHECK`, `USER` and `ARG` scope. Use for: the authority on any Dockerfile question, from lesson 7 on.
- [Docs: "Docker build cache", Docker](https://docs.docker.com/build/cache/)
  How layer caching works and what invalidates it. Use for: lesson 8.
- [Docs: "Build cache invalidation", Docker](https://docs.docker.com/build/cache/invalidation/)
  The exact rules for when an instruction's cache entry is reused: file checksums for `COPY` and `ADD`, the command string for `RUN`, and how a miss cascades. Use for: lesson 8, predicting a rebuild.
- [Docs: "Build context", Docker](https://docs.docker.com/build/concepts/context/)
  What the build context is, local against remote contexts, and the `.dockerignore` syntax. Use for: lesson 7.
- [Docs: "Optimize cache usage in builds", Docker](https://docs.docker.com/build/cache/optimize/)
  Ordering instructions, keeping the context small, cache mounts and bind mounts in `RUN`. Use for: lesson 8, making a rebuild fast.
- [Docs: "Multi-stage builds", Docker](https://docs.docker.com/build/building/multi-stage/)
  Named stages, `COPY --from`, building a single target. Use for: lesson 9.
- [Docs: "Building best practices", Docker](https://docs.docker.com/build/building/best-practices/)
  Docker's own guidance on bases, pinning, `.dockerignore`, package installs and `USER`. Use for: lessons 7 to 10 and as one input to the review checklist in lesson 22.
- [Docs: "Multi-platform builds", Docker](https://docs.docker.com/build/building/multi-platform/)
  Building one image for several architectures into an image index. Use for: lesson 6, where the index comes from.
- [Docs: "Reproducible builds with GitHub Actions", Docker](https://docs.docker.com/build/ci/github-actions/reproducible-builds/)
  How BuildKit uses `SOURCE_DATE_EPOCH` to set timestamps in an image. Use for: lesson 10, the timestamp half of reproducibility.
- [Docs: "Build reproducibility", BuildKit](https://github.com/moby/buildkit/blob/master/docs/build-repro.md)
  How BuildKit applies `SOURCE_DATE_EPOCH` to image metadata and, with `rewrite-timestamp=true`, to file timestamps in layers. Use for: lesson 10, the exact switches behind a reproducible image.
- [Docs: "SOURCE_DATE_EPOCH", Reproducible Builds project](https://reproducible-builds.org/docs/source-date-epoch/)
  The convention for a fixed build timestamp, and why timestamps are the most common source of difference. Use for: lesson 10.
- [Docs: Build checks, Docker](https://docs.docker.com/reference/build-checks/)
  The rules BuildKit's built-in linter checks a Dockerfile against, each with an explanation. Use for: lesson 22, a mechanical first pass before human review.
- [Repo: hadolint](https://github.com/hadolint/hadolint)
  A widely used Dockerfile linter that also checks the shell inside `RUN` with ShellCheck. Use for: lesson 22, a second mechanical pass.
- [Repo: dive, Alex Goodman](https://github.com/wagoodman/dive)
  A tool for exploring each layer of an image and finding wasted space. Use for: lessons 4 and 9, seeing what each layer added.

### Running containers

- [Docs: "docker container run", Docker CLI reference](https://docs.docker.com/reference/cli/docker/container/run/)
  Every flag of `docker run`, including `--init`, `--user`, `--cap-drop` and `--read-only`. Use for: lessons 11, 17 and 20.
- [Docs: "docker container stop", Docker CLI reference](https://docs.docker.com/reference/cli/docker/container/stop/)
  The stop signal, the grace period and the `SIGKILL` after it. Use for: lesson 11.
- [Docs: "Resource constraints", Docker](https://docs.docker.com/engine/containers/resource_constraints/)
  Memory, swap and CPU flags and how they map to cgroup limits. Use for: lesson 13.
- [Docs: "Start containers automatically", Docker](https://docs.docker.com/engine/containers/start-containers-automatically/)
  The restart policies and how they interact with the daemon restarting. Use for: lesson 12.
- [Docs: "Run multiple processes in a container", Docker](https://docs.docker.com/engine/containers/multi-service_container/)
  Why one process per container is the default, and what to do when you need more. Use for: lesson 11, and when the usual answer is wrong.
- [Man page: pid_namespaces(7), Linux man-pages project](https://man7.org/linux/man-pages/man7/pid_namespaces.7.html)
  The init process of a PID namespace, and the rule that it only receives signals it has a handler for, apart from `SIGKILL` and `SIGSTOP`. Use for: lesson 11, why PID 1 ignores `SIGTERM`.
- [Docs: "docker volume prune", Docker CLI reference](https://docs.docker.com/reference/cli/docker/volume/prune/)
  What prune removes: anonymous volumes by default, named ones only with `--all`. Use for: lesson 15, cleaning up without losing data.
- [Docs: "Networking in Compose", Docker](https://docs.docker.com/compose/how-tos/networking/)
  The default network Compose creates per project and how services find each other by name. Use for: lesson 16.
- [Docs: "The Compose application model", Docker](https://docs.docker.com/compose/intro/compose-application-model/)
  Services, networks, volumes and the `compose.yaml` file convention. Use for: lesson 16, the shape of a Compose file.
- [Docs: "docker compose up", Docker CLI reference](https://docs.docker.com/reference/cli/docker/compose/up/)
  Starting a project, including `--wait` for healthy services. Use for: lesson 16.
- [Docs: "docker compose down", Docker CLI reference](https://docs.docker.com/reference/cli/docker/compose/down/)
  What `down` removes, and how `-v` also removes named volumes. Use for: lesson 16, not deleting a database by accident.
- [Repo: tini, Thomas Orozco](https://github.com/krallin/tini)
  The minimal init that `docker run --init` injects, with an explanation of signal forwarding and zombie reaping. Use for: lesson 11.
- [Docs: Go 1.25 release notes, The Go Project](https://go.dev/doc/go1.25)
  Records that the Go runtime sets `GOMAXPROCS` from a cgroup CPU limit from Go 1.25. Use for: lesson 13, an example of a runtime that reads its container's limit.
- [Docs: "Networking overview", Docker](https://docs.docker.com/engine/network/)
  Network drivers, published ports, container DNS on user-defined networks. Use for: lesson 14.
- [Docs: "Bridge network driver", Docker](https://docs.docker.com/engine/network/drivers/bridge/)
  The default bridge against user-defined bridges, and why the latter resolve container names. Use for: lesson 14.
- [Docs: "Volumes", Docker](https://docs.docker.com/engine/storage/volumes/)
  Named volumes, how they are created and populated, and when to prefer them. Use for: lesson 15.
- [Docs: "Bind mounts", Docker](https://docs.docker.com/engine/storage/bind-mounts/)
  Bind mounts, read-only mounts, and how they hide what was at the mount point. Use for: lesson 15.
- [Docs: "Storage drivers", Docker](https://docs.docker.com/engine/storage/drivers/)
  Images, layers and the writable layer from Docker's side, and copy-on-write. Use for: lessons 4 and 5.
- [Docs: "OverlayFS storage driver", Docker](https://docs.docker.com/engine/storage/drivers/overlayfs-driver/)
  How `overlay2` lays layers out on disk with overlayfs. Use for: lesson 4, finding the layers on a host.
- [Spec: Compose file reference, Docker](https://docs.docker.com/reference/compose-file/)
  The Compose specification: services, networks, volumes, `depends_on` conditions and `healthcheck`. Use for: lesson 16.
- [Docs: "Control startup and shutdown order in Compose", Docker](https://docs.docker.com/compose/how-tos/startup-order/)
  Why a started dependency is not a ready one, and `condition: service_healthy`. Use for: lesson 16.
- [Docs: Podman documentation](https://docs.podman.io/en/latest/)
  A daemonless, rootless-by-default container tool with a Docker-compatible CLI. Use for: running the track's commands without Docker, and rootless mode in lesson 17.

### Security

- [Docs: "Running containers", Docker](https://docs.docker.com/engine/containers/run/)
  The reference for runtime options: the exit statuses 125, 126 and 127, how `--entrypoint` clears the image's `CMD`, the default capability list and exactly what `--privileged` grants. Use for: lesson 17, deciding what to drop and why privileged mode is root on the host, and lesson 20, reading an exit code.
- [Docs: "Docker Engine security", Docker](https://docs.docker.com/engine/security/)
  The kernel features Docker relies on, the daemon's attack surface, and why access to the daemon is root. Use for: lesson 17.
- [Docs: "Rootless mode", Docker](https://docs.docker.com/engine/security/rootless/)
  Running the daemon and containers as an unprivileged user, and its limitations. Use for: lesson 17.
- [Docs: "Isolate containers with a user namespace", Docker](https://docs.docker.com/engine/security/userns-remap/)
  Remapping container root to an unprivileged host range with `userns-remap`. Use for: lesson 17.
- [Docs: Docker Security Cheat Sheet, OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
  A rule list covering the socket, users, capabilities, read-only filesystems, resource limits and scanning. Use for: lessons 17 to 19 and the review checklist.
- [Standard: NIST SP 800-190, "Application Container Security Guide", 2017](https://csrc.nist.gov/pubs/sp/800/190/final)
  The risks to images, registries, runtimes and hosts and the countermeasures for each. Use for: a structured threat model behind stage 6.
- [Book: "Container Security", Liz Rice, O'Reilly, 2020](https://containersecurity.tech/)
  How each isolation mechanism works and fails, image security, and runtime defences, by an author who builds them live. Use for: the depth behind stage 6.
- [Repo: distroless, GoogleContainerTools](https://github.com/GoogleContainerTools/distroless)
  The distroless base images, what each contains, and how to debug one with the `debug` tags. Use for: lessons 9, 18 and 21.
- [Docs: distroless `static` and `base` images, GoogleContainerTools](https://github.com/GoogleContainerTools/distroless/blob/main/base/README.md)
  The package list of the `static` and `base` images, and which kinds of binary each suits. Use for: lesson 9, choosing between them.
- [Docs: Trivy, Aqua Security](https://trivy.dev/docs/latest/)
  An open-source scanner for vulnerabilities, misconfigurations and secrets in images, with SBOM output. Use for: lesson 18, running and reading a scan.
- [Repo: Grype, Anchore](https://github.com/anchore/grype)
  An open-source image vulnerability scanner that reads SBOMs. Use for: lesson 18, a second scanner to compare findings with.
- [Docs: "SBOM attestations", Docker](https://docs.docker.com/build/metadata/attestations/sbom/)
  Generating an SBOM at build time and attaching it to the image. Use for: lesson 18.
- [Docs: "Build secrets", Docker](https://docs.docker.com/build/building/secrets/)
  Secret mounts and SSH mounts that give a build step a credential without writing it into a layer. Use for: lesson 19.
- [Docs: "Signing containers", Sigstore](https://docs.sigstore.dev/cosign/signing/signing_with_containers/)
  Signing and verifying an image by digest with cosign, keyless or with a key. Use for: lesson 19.
- [Spec: SLSA v1.0](https://slsa.dev/spec/v1.0/)
  The supply-chain levels and the provenance format that records how an artifact was built. Use for: lesson 19, what a provenance attestation proves.
- [Docs: "Provenance attestations", Docker](https://docs.docker.com/build/metadata/attestations/slsa-provenance/)
  How BuildKit records SLSA provenance for an image and what `mode=max` adds. Use for: lesson 19.

### Debugging and judgment

- [Docs: "docker container exec", Docker CLI reference](https://docs.docker.com/reference/cli/docker/container/exec/)
  Running a command in a running container, as another user or with extra privileges. Use for: lesson 21.
- [Docs: "docker container logs", Docker CLI reference](https://docs.docker.com/reference/cli/docker/container/logs/)
  Reading a container's output, with `--tail`, `--since`, `--until` and timestamps. Use for: lesson 20, the first thing to read after the exit code.
- [Docs: "docker system events", Docker CLI reference](https://docs.docker.com/reference/cli/docker/system/events/)
  The stream of container events, including `die` with its exit code. Use for: lesson 20, catching a restart loop as it happens.
- [Docs: "docker container cp", Docker CLI reference](https://docs.docker.com/reference/cli/docker/container/cp/)
  Copying files out of a running or stopped container. Use for: lessons 20 and 21, reading a config or log from a container that has no shell.
- [Docs: "docker container top", Docker CLI reference](https://docs.docker.com/reference/cli/docker/container/top/)
  A container's processes as the host sees them, with host PIDs. Use for: lesson 21, finding the PID to pass to nsenter.
- [Man page: proc_pid_root(5), Linux man-pages project](https://man7.org/linux/man-pages/man5/proc_pid_root.5.html)
  `/proc/<pid>/root`, the process's view of the filesystem. Use for: lesson 21, reading a container's files from the host.
- [Docs: "Functional differences from glibc", musl wiki](https://wiki.musl-libc.org/functional-differences-from-glibc.html)
  Where musl, the C library in Alpine, behaves differently from glibc: DNS resolution, locales, thread stack size. Use for: lesson 24, when Alpine is the wrong base.

## Gaps

- No single current, vendor-neutral source compares base-image families (Debian slim, Alpine, distroless, Wolfi-based images) on size, CVE counts and C library compatibility. Lessons 9, 18 and 24 assemble the comparison from each project's own documentation, which changes with every release.
- Scanner triage, deciding which findings matter for a given image, has no neutral primary source. Lesson 18 teaches it from the scanners' documentation and NIST SP 800-190, and says where that is a judgment rather than a rule.
