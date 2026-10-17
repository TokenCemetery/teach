---
title: Glossary
description: "Canonical terms for containers and container images"
type: glossary
---

# Containers Glossary

Canonical terms for the kernel primitives a container is made of, the images it starts from, and how it is built, run, secured and debugged. In this workspace "container" always means a running or stopped instance of an image on one host; "Docker" names one tool, never the concept.

## Terms

**Base image**:
The image a Dockerfile's `FROM` line starts from, whose layers become the bottom of the new image. Everything in it, including its vulnerabilities, ships in every image built on it.
_Avoid_: parent image (Docker's older term), OS image

**Bind mount**:
A mount of an existing host path into a container's filesystem. The host owns the path, its contents and its file ownership.
_Avoid_: host volume, volume (a named volume is different)

**Bridge network**:
A software switch on the host, a Linux bridge device, that connects containers' network namespaces through veth pairs and routes their traffic out through NAT. Docker's default network is one.
_Avoid_: docker0 (that is the default bridge's device name), NAT network

**Build cache**:
The store of layers from earlier builds that the builder reuses when an instruction and everything it depends on are unchanged. A miss at one instruction rebuilds every instruction after it.
_Avoid_: layer cache (accepted alias, but use one term), Docker cache

**Build context**:
The set of files sent to the builder with a build, usually the directory passed to `docker build`. `COPY` and `ADD` can only read from it, and `.dockerignore` excludes paths from it.
_Avoid_: build directory, source folder

**BuildKit**:
The builder behind `docker build` since Docker Engine 23.0. It builds independent stages in parallel, skips unused ones, and supports cache mounts, secret mounts and attestations.
_Avoid_: buildx (the CLI plugin that drives BuildKit), the new builder

**Capability**:
One of the slices the Linux kernel divides root's privileges into, such as `CAP_NET_BIND_SERVICE` or `CAP_SYS_ADMIN`. A container process gets a reduced default set, which can be narrowed further.
_Avoid_: permission, privilege (too broad)

**Cgroup**:
A control group: a kernel mechanism that organises processes into a hierarchy and limits and accounts for their memory, CPU, I/O and process count. In this workspace it means cgroup v2 unless a lesson says otherwise.
_Avoid_: control group (fine once, then use the short form), resource group

**Compose**:
A tool and file format that describes a set of containers, their networks and their volumes in one YAML file and runs them together on one host.
_Avoid_: docker-compose (the retired v1 command), stack

**Container**:
A process, or process tree, that the kernel runs in its own set of namespaces and cgroups on a root filesystem made from an image's layers plus a writable layer. It shares the host's kernel.
_Avoid_: lightweight VM, Docker (a tool, not the concept)

**Container runtime**:
The software that turns an image and a configuration into a running container. In this workspace a low-level runtime such as runc creates the namespaces and cgroups and starts the process, and a high-level runtime such as containerd manages images and the low-level runtime.
_Avoid_: engine (ambiguous), Docker (a client of the runtime)

**Copy-on-write**:
The strategy by which a file from a read-only layer is copied up into the writable layer the first time a container modifies it, so the image's layers are never changed.
_Avoid_: CoW without introducing it, snapshotting

**Digest**:
The content address of an image, manifest or layer: an algorithm and a hash of its bytes, such as `sha256:` followed by 64 hex digits. The same digest always names the same content.
_Avoid_: image ID (a local, different hash), checksum

**Distroless image**:
A base image that contains a language runtime or only the libraries a program needs, with no shell and no package manager. Google's distroless images are the original family.
_Avoid_: minimal image (broader), scratch image (scratch is empty)

**Entrypoint**:
The executable an image's config says to run when a container starts. `CMD` supplies its default arguments, or the whole command when there is no entrypoint.
_Avoid_: start command, main process (that is the result)

**Exec form**:
A `RUN`, `CMD` or `ENTRYPOINT` written as a JSON array, such as `["app", "--port", "8080"]`, which runs the executable directly with no shell in between.
_Avoid_: array form, JSON syntax (accepted in the Dockerfile reference)

**Exit code**:
The number a container's main process returns when it ends, which the runtime records as the container's exit status. Codes above 128 mean the process was killed by signal number code minus 128.
_Avoid_: return value, status (ambiguous with the container's state)

**Health check**:
A command the runtime runs inside a container on an interval to decide whether the service is working, which marks the container healthy or unhealthy. Docker reports the state and does not restart on it.
_Avoid_: liveness probe (a Kubernetes concept), ping

**Image**:
An immutable, content-addressed package of filesystem layers and a config that says how to run them. A container is started from one.
_Avoid_: container image (accepted in full), snapshot

**Image config**:
The JSON document in an image that records how to run it (entrypoint, command, environment, user, working directory, exposed ports) and the ordered list of its layers' uncompressed digests.
_Avoid_: metadata (vague), Dockerfile (the source, not the result)

**Image index**:
An OCI document that lists several manifests for one image, one per platform such as linux/amd64 and linux/arm64, so a single name resolves to the right one for the host.
_Avoid_: manifest list (Docker's older name, accepted), fat manifest

**Layer**:
A tarball of filesystem changes, files added, changed or deleted, that one build step produced. An image's layers are stacked in order to form its root filesystem.
_Avoid_: image layer (redundant), diff

**Manifest**:
The OCI document that names one image for one platform by listing the digest of its config and of each layer. Pulling an image starts by fetching it.
_Avoid_: image manifest (accepted in full), descriptor (one entry within it)

**Multi-stage build**:
A Dockerfile with more than one `FROM`, where later stages copy chosen files out of earlier ones, so build tools stay out of the final image.
_Avoid_: builder pattern (the older manual workaround), two-step build

**Named volume**:
Storage that the container runtime creates and manages under its own directory, referred to by name and mounted into containers. It outlives any container that uses it.
_Avoid_: data volume, volume (fine once the kind is clear)

**Namespace**:
A kernel feature that gives a set of processes their own instance of one kind of global resource, such as process IDs, mounts or the network stack. A container is a process placed in several at once.
_Avoid_: sandbox, jail (a different BSD mechanism)

**OCI**:
The Open Container Initiative, whose image, runtime and distribution specifications define what an image is, how a runtime starts one, and how a registry serves one, independently of any tool.
_Avoid_: Docker format (OCI grew out of it but is the standard now)

**OOM kill**:
The kernel ending a process because its cgroup reached its memory limit and nothing could be reclaimed. The process gets `SIGKILL`, so a container killed this way exits with code 137.
_Avoid_: crash, out-of-memory error (the process may never see one)

**Overlay filesystem**:
The Linux filesystem, overlayfs, that presents several directories as one by stacking read-only lower layers under a writable upper layer. It is how a container's root filesystem is assembled from an image's layers.
_Avoid_: union filesystem (the general family, fine in passing), overlay2 (Docker's storage driver built on it)

**PID 1**:
The first process in a PID namespace. The kernel does not apply default signal actions to it, so it ignores `SIGTERM` unless it installs a handler, and it must reap orphaned child processes.
_Avoid_: init (only when the process is an init system), main process

**Port publishing**:
Mapping a port on the host to a port in a container's network namespace, so traffic from outside the host can reach it. Docker implements it with NAT rules and, by default, binds every host address.
_Avoid_: port forwarding (accepted in speech), exposing (`EXPOSE` only documents a port)

**Privileged container**:
A container started with `--privileged`, which gets every capability, access to all host devices and most security restrictions lifted. It is root on the host in all but name.
_Avoid_: root container (a non-privileged container can run as root)

**Provenance attestation**:
A signed statement, usually in the SLSA format, recording how and from what an image was built: the builder, the source and the build parameters. It is stored alongside the image and verified before trusting it.
_Avoid_: build log, signature (a signature proves who, provenance records how)

**Registry**:
A server that stores images and serves them over the OCI distribution API, addressed by repository name plus a tag or digest.
_Avoid_: repository (one image name within a registry), hub

**Reproducible build**:
A build that produces byte-identical output, and so the same digest, from the same source and inputs whenever and wherever it runs.
_Avoid_: deterministic build (accepted alias), repeatable build (weaker: the same behaviour, not the same bytes)

**Restart policy**:
The rule the container runtime applies when a container's main process exits: never restart, always, unless stopped, or on failure up to a limit.
_Avoid_: auto-restart, supervisor

**Rootless mode**:
Running the container runtime itself as an unprivileged user, inside a user namespace, so that root in a container and even the daemon have no root privileges on the host.
_Avoid_: non-root container (that is about the user inside, not the runtime)

**SBOM**:
A software bill of materials: a machine-readable list of every package and version in an image, which a scanner matches against vulnerability databases.
_Avoid_: dependency list, manifest (an OCI manifest is something else)

**Shell form**:
A `RUN`, `CMD` or `ENTRYPOINT` written as a plain string, which the builder or runtime runs through `/bin/sh -c`. The shell, not the program, becomes the process that receives signals.
_Avoid_: string form

**Tag**:
A human-readable name for a manifest within a repository, such as `1.27-alpine` or `latest`. A tag can be moved to point at different content at any time.
_Avoid_: version (a tag may not be one), label (Docker labels are key-value metadata)

**Throttling**:
The kernel pausing a cgroup's processes for the rest of a scheduling period once they have used their CPU quota for it. It shows up as latency, not as an error.
_Avoid_: CPU limit (the cause, not the effect), slowdown

**User namespace**:
A namespace that maps user and group IDs inside it to different IDs outside, so a process can be root inside a container and an unprivileged user on the host.
_Avoid_: userns without introducing it, UID remapping (one use of it)

**Veth pair**:
Two virtual network interfaces joined like the ends of a cable, so packets sent into one come out of the other. One end sits in a container's network namespace, the other on the host's bridge.
_Avoid_: virtual NIC, tunnel

**Writable layer**:
The empty upper layer the runtime puts over an image's layers for each container, where every file the container creates or modifies lives. It is deleted with the container.
_Avoid_: container layer (accepted alias), scratch space
