---
title: "24. When the Usual Answer Is Wrong"
description: "Recognise when Alpine, distroless, a pinned digest or a container at all is the wrong call, and settle it from the specification"
type: lesson
---

# Lesson 24. When the Usual Answer Is Wrong

**Mission link:** The track ends with trusting you to make the call on an image and to explain it to someone else. "Use Alpine", "use distroless", "pin the digest" and "one process per container" are the usual answers, and each is right for some services and wrong for others. This lesson is the method for finding out which, and the cases where each one fails.
**Primary source:** [Spec: OCI Image Format Specification](https://github.com/opencontainers/image-spec/blob/main/spec.md), with its [layer](https://github.com/opencontainers/image-spec/blob/main/layer.md) and [image index](https://github.com/opencontainers/image-spec/blob/main/image-index.md) documents
**Prerequisites:** [Lesson 18](0018-minimal-bases-and-scanning.md), [Lesson 21](0021-debugging-a-running-container.md), [Lesson 22](0022-reviewing-a-dockerfile.md), [Lesson 23](0023-changing-a-base-image-others-depend-on.md), [Distroless image](../GLOSSARY.md), [Digest](../GLOSSARY.md), [Image index](../GLOSSARY.md)

## Warm-up

1. ▢ A container is killed with exit code 137 and the logs show nothing wrong. What are the two things you check first, and where does each live?

<details markdown="1"><summary>Check</summary>

137 is 128 plus signal 9, so `SIGKILL` (lesson 20). Check whether the kernel OOM-killed it, in `docker inspect` under `State.OOMKilled` and in the cgroup's `memory.events`, and whether `docker stop` timed out on a process that ignored `SIGTERM` (lessons 3, 11 and 13).

</details>

2. ▢ What does a scan report for an image that contains a vulnerable package the program never loads, and what does triage do with it?

<details markdown="1"><summary>Check</summary>

The scanner matches the package list, the SBOM, against its database, so the finding appears whether or not the code can reach it. Triage asks whether the package is reachable and whether a fixed version exists, and a smaller base removes the package instead of arguing about it (lesson 18).

</details>

3. ▢ Which kernel feature gives a container its own process IDs, and which gives it a memory limit?

<details markdown="1"><summary>Check</summary>

The PID namespace gives its own process IDs, with the container's first process as PID 1, and a cgroup gives the memory limit through `memory.max` (lessons 2 and 3).

</details>

## Know this

### The method

A usual answer arrives as a slogan without its conditions. Four steps decide whether it holds for your service.

1. **Find the primary source.** The specification, the project's own README or the library's documentation, not the post that cites it.
2. **Check what it says, and what it is silent on.** A source that describes a behaviour has not recommended it.
3. **Check what your service does that the answer assumes it does not.** Static or dynamic linking, a shell in the health check, DNS, threads, someone who must log in to debug it.
4. **Test it on the real service,** and say what would change your mind.

None of the cases below says the usual answer is always wrong. Each says what the source supports and where it stops.

### Case 1: Alpine

The usual answer is a small base. Alpine's C library is musl, not glibc, and the musl project documents where they differ ([Functional differences from glibc](https://wiki.musl-libc.org/functional-differences-from-glibc.html)). Three of them can reach a service:

- **DNS.** glibc tries the nameservers in `resolv.conf` one after another. musl queries them all at once and accepts whichever answers first, so with diverse nameservers that disagree, the answer can come from a different one than you expected.
- **Thread stacks.** The default for a new thread on glibc is derived from the stack limit and "generally ends up being 2-10 MB". musl's default is 128k. Code that assumes the larger one, deep recursion in a thread, can overflow on musl.
- **Locale.** musl's default locale is always `C.UTF-8`, where glibc's default was `C` in versions up through 2.26.

None of this makes Alpine bad. A Go binary with no C library dependency does not notice, and a service that needs a library compiled against glibc does. So Alpine is the wrong call when the service, or a native dependency it loads, depends on glibc behaviour or glibc binaries, and the right way to find out is to run its own tests on it. What would change the call: a test run on the real service passing on both.

### Case 2: distroless

The usual answer is no shell, no package manager, fewer things to exploit and fewer scanner findings. The project says the same: its images "contain only your application and its runtime dependencies", and it argues that this improves the signal to noise of scanners ([distroless README](https://github.com/GoogleContainerTools/distroless)). The price is in the same README: no shell, so an `ENTRYPOINT` or `CMD` must be in exec form, and anyone who needs to look inside uses the `:debug` tag, which adds a busybox shell, or a debug container (lesson 21).

Distroless is the wrong call when something in the image's own life needs a shell or a tool that is not there: a health check that runs `curl` (the command runs inside the container, see [Health check](../GLOSSARY.md)), an entrypoint script, or a team that has no way to debug a container without one. It is also wrong when nobody can build the artifact the base requires. The cost is not zero in the other direction either: a service that needs a package must bring it itself.

### Case 3: pin the digest

A pinned digest gives the same bytes every time, even if the tag moves. Docker's page also states the cost: you opt out of automated security fixes, and updating the digest by hand is tedious ([Pin base image versions](https://docs.docker.com/build/building/best-practices/)). Its answer is a bot that bumps the pin by pull request. So pinning is the wrong call when nothing bumps it, because the image then freezes at its worst vulnerability list. Read "pin the digest" as "pin the digest and automate the bump", and in a review ask for both.

### Case 4: one process per container

The usual answer is one concern per container. Docker's own pages call it a rule of thumb that is "not a hard and fast rule": a container can spawn processes, an init process, or run a program that forks workers, and "it's ok to have multiple processes" ([Decouple applications](https://docs.docker.com/build/building/best-practices/), [Run multiple processes in a container](https://docs.docker.com/engine/containers/multi-service_container/)). The same page shows wrapper scripts and process managers for when you truly need two services together, and says what the default protects: separate areas of concern, which makes containers easier to scale and reuse. It is the wrong call when two processes cannot work apart, such as a program and a helper that share a socket or a lifecycle. It stays right when you would be running two services to save a deployment.

### Case 5: a container at all

A container shares the host's kernel (lesson 1). That is a reasoning step from the track, not a quote from one source: anything that must not share a kernel with its neighbours, such as running untrusted code from strangers, is a case for a virtual machine, and a kernel fault in a container is a fault for the whole host. A container also adds a runtime, a registry and an image lifecycle to own, and for a single static binary on a machine you already manage, copying the binary and running it under the system's service manager can be less to maintain. What this rests on: what you can operate and what the threat is. What would change it: needing the same artifact to run on many hosts, which is what an image is for.

### Settling a dispute from the primary source

Three colleagues say three things. Do not argue from memory, open the source.

- **"Once pushed, a tag always points at the same image."** The OCI distribution specification defines a tag as "a custom, human-readable pointer to a manifest" and says a manifest digest "may have zero, one, or many tags" ([distribution spec, Definitions](https://github.com/opencontainers/distribution-spec/blob/main/spec.md)). Nothing there makes a tag immutable, so only a digest names fixed content. A particular registry may add its own immutability setting. That is a feature of that registry, not of the specification.
- **"I deleted the files in the last step, so the image is smaller."** The layer specification represents a removal as a whiteout, an empty file named `.wh.` plus the basename of the path, and says whiteouts "MUST only apply to resources in lower/parent layers" ([layer spec, Whiteouts](https://github.com/opencontainers/image-spec/blob/main/layer.md#whiteouts)). The deleted bytes stay in the layer that added them, so the image is not smaller.
- **"The tag gives me the same image on my laptop and on the server."** The image index specification lets one name point to a list of manifests, each with a `platform` that holds the `architecture` and `os` ([image index spec](https://github.com/opencontainers/image-spec/blob/main/image-index.md)). A pull resolves the index to the manifest for the host, so the same tag can give a different manifest on an arm64 laptop and an amd64 server.

In each, read what the source says and stop there. A dispute is settled by the sentence, not by the colleague who is more sure.

## Practice

1. ▢ A colleague says "Alpine is always the best base because it is the smallest." Which source do you open, and what do you check in it?

<details markdown="1"><summary>Check</summary>

Open the musl project's page on its functional differences from glibc and check what your service uses: DNS resolution, threads with large stacks, locales, and any native library built for glibc. The size is real but it is one cost, and the page lists conditions under which the small base behaves differently. Then run the service's own tests on it.

</details>

2. ▢ A reviewer says "use a distroless base" about a service whose `HEALTHCHECK CMD curl -f http://localhost:8080/health` works today. What is the finding?

    - a) The check breaks because the image will not contain curl
    - b) The check works because distroless images include common tools
    - c) The check works only if the entrypoint is written in shell form
    - d) The check breaks because distroless images never run commands

<details markdown="1"><summary>Check</summary>

**a)** A health check command runs inside the container, and distroless images contain only the application and its runtime dependencies. Change the check to something the app itself can answer, or drop it where the platform probes the service from outside. (b) is wrong because the project removes those tools on purpose. (c) is wrong because shell form needs a shell, which the image lacks. (d) is wrong because commands run fine when the binary exists.

</details>

3. ▢ Predict, then run. With no shell in a distroless image, what does this print and what does `echo $?` show?

    ```console
    $ docker run --rm --entrypoint sh gcr.io/distroless/static-debian13
    $ echo $?
    ```

<details markdown="1"><summary>Hint</summary>

Lesson 20 listed exit statuses the runtime itself returns when the command cannot start.

</details>

<details markdown="1"><summary>Check</summary>

An error from the daemon ending in `exec: "sh": executable file not found in $PATH`, and `127`. The container never starts, because the entrypoint names a file the image does not contain, and 127 is the status `docker run` documents for a command that cannot be found ([docker container run, exit status](https://docs.docker.com/reference/cli/docker/container/run/)). The `:debug` tag of the same image adds a busybox shell and would start.

</details>

4. ▢ A team says "we pin every base by digest, so we are safe from supply-chain problems." Using the sources in this lesson, what is true and what is missing?

<details markdown="1"><summary>Check</summary>

True: a pinned digest guarantees the same bytes even if the tag is moved. Missing: pinning also stops security fixes arriving, and the digest says nothing about who built the image or how, which is what a signature and a provenance attestation add (lesson 19). The right question is who or what bumps the pin, and whether the new digest is verified when it is bumped.

</details>

5. ▢ Someone says "tags are immutable on our registry, so `1.4` can never change". Settle it, and say what you would need to check to know it is true for you.

<details markdown="1"><summary>Check</summary>

The OCI distribution specification defines a tag as a pointer to a manifest and makes no promise that it stays put, so immutability is not a property of tags in general. It can still be true for that registry if immutable tags are an enabled setting, so check the repository's settings or try pushing a changed manifest to an existing tag in a test repository. A digest is the only name the specification ties to fixed content.

</details>

6. ▢ You are asked whether a team that runs nothing but one static Go binary should adopt containers. Give your call, what it rests on, and what would change it.

<details markdown="1"><summary>Check</summary>

A defensible call: not by default. A single static binary on hosts the team already manages and runs under a service manager has little to package, and a container adds a runtime, a registry and an image lifecycle to own. What it rests on is the team's operations and its threat model, not the technology. What would change it: needing the same artifact on many differently configured hosts, wanting resource limits and isolation per service (lessons 3 and 17), or a platform that only runs images. A call that names its conditions is the one that can be defended.

</details>

## Real-world reps

- [ ] Take one rule you follow on images (a small base, no shell, pinned digests, one process per container) and write the source it comes from, what it covers, and one service of yours where its assumption does not hold.
- [ ] Pick a service of yours and run its tests on an Alpine variant of its base image. Write down any difference, even a small one, and whether it traces to a musl difference.
- [ ] Pull an image that publishes several platforms and look at its index with `docker buildx imagetools inspect IMAGE`. Find the manifest the specification says your host resolves to.
- [ ] Tomorrow: without notes, list the four steps for testing a usual answer, and pick the case from this lesson most likely to apply to an image you own.

## Going further

- [Dockerfile Review Checklist](../reference/dockerfile-review-checklist.md)
- [Spec: OCI Image Format Specification](https://github.com/opencontainers/image-spec/blob/main/spec.md)
- [Docs: "Functional differences from glibc", musl wiki](https://wiki.musl-libc.org/functional-differences-from-glibc.html)
- [Repo: distroless, GoogleContainerTools](https://github.com/GoogleContainerTools/distroless)
- [Docs: "Run multiple processes in a container", Docker](https://docs.docker.com/engine/containers/multi-service_container/)
- [Standard: NIST SP 800-190, "Application Container Security Guide", 2017](https://csrc.nist.gov/pubs/sp/800/190/final)
- [Resources](../RESOURCES.md)

---

This is the end of the track, and the habit it was built for is the one in this lesson: an image is a claim about a kernel's view of a process, a set of layers and a set of choices someone else will run, so find where each claim comes from, check what it covers, and test it on your own service before you defend it to anyone else.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
