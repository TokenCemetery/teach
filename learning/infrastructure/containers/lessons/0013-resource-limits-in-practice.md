---
title: "13. Resource Limits in Practice"
description: Set memory and CPU limits, read an OOM kill and CPU throttling, and check the runtime inside sees the limit
type: lesson
---

# Lesson 13. Resource Limits in Practice

**Mission link:** The mission says a container must stay within memory and CPU limits that the runtime inside it respects. A limit nobody set lets one container take a host down, and a limit the language runtime does not know about makes the service crash or crawl.
**Primary source:** [Docs: "Resource constraints", Docker](https://docs.docker.com/engine/containers/resource_constraints/)
**Prerequisites:** [Lesson 3](0003-cgroups.md), [Lesson 12](0012-health-checks-and-restart-policies.md), [Cgroup](../GLOSSARY.md), [OOM kill](../GLOSSARY.md), [Throttling](../GLOSSARY.md)

## Warm-up

1. ▢ Which cgroup v2 file caps a process tree's memory, and what does the kernel do when usage reaches it and cannot be reduced?

<details markdown="1"><summary>Check</summary>

`memory.max`. When usage reaches it and the kernel cannot reclaim enough, the OOM killer runs inside that cgroup and kills a process there, never one outside it ([kernel cgroup v2 documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html), lesson 3).

</details>

2. ▢ `cpu.max` contains `50000 100000`. What does it allow?

<details markdown="1"><summary>Check</summary>

The group may use 50,000 microseconds of CPU time in each 100,000 microsecond period, so half of one CPU. Once it has used its quota the kernel pauses it until the next period (lesson 3).

</details>

3. ▢ A restart policy of `always` is set and the process is killed by the OOM killer. Does the container come back, and does a health check have any part in that?

<details markdown="1"><summary>Check</summary>

Yes, it comes back: the policy sees the process exit and restarts it after the backoff delay. The health check plays no part, since health is reported and never drives a restart (lesson 12). A restart does not fix the cause, so an OOM-killed service that restarts will probably be killed again.

</details>

## Know this

### Without a limit there is none

By default a container has no resource constraints and can use as much of a resource as the host's kernel scheduler allows ([Resource constraints](https://docs.docker.com/engine/containers/resource_constraints/)). One runaway service then takes the memory other services and the host need, and the kernel's OOM killer, running on the whole host, may pick a victim that is not the culprit. A limit confines the damage to the container that caused it.

### Memory

`--memory` (`-m`) sets the hard limit, with a minimum of 6 MB, and Docker writes it to the container's `memory.max`. Memory-swap behaves in a way that surprises people:

|Flags|Effect|
|---|---|
|`--memory 300m` only|The container can use 300 MB of RAM and, if the host has swap, as much swap again: 600 MB in total|
|`--memory 300m --memory-swap 1g`|`--memory-swap` is the total of RAM plus swap: 300 MB RAM and 700 MB swap|
|`--memory 300m --memory-swap 300m`|No swap at all|
|`--memory-swap -1`|Unlimited swap, up to what the host has|

For a service you want to fail fast and visibly rather than thrash on swap, set `--memory-swap` equal to `--memory`. `--memory-reservation` is a soft limit that only applies when the host is short of memory and does not stop a container exceeding it.

When a container reaches `memory.max` and nothing can be reclaimed, the kernel's OOM killer sends `SIGKILL` to a process in the cgroup. The process gets no signal it can handle, so it logs nothing about it. If that was the container's main process, the container exits with code 137 (lesson 11). The evidence is outside the process:

```console
$ docker inspect --format '{{.State.OOMKilled}} {{.State.ExitCode}}' hog
true 137

$ cat /sys/fs/cgroup/<container cgroup path>/memory.events
low 0
high 0
max 12
oom 1
oom_kill 1
```

`oom_kill` counts the processes in the cgroup killed by any OOM killer ([kernel cgroup v2 documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html)). Exit code 137 alone is ambiguous, because `docker stop` that had to kill the process also ends with 137. `OOMKilled` true is what separates a memory kill from a stop timeout. The state flag records that an OOM kill happened to the container, and the `dmesg` line `Memory cgroup out of memory: Killed process` on the host is a second confirmation.

### CPU

`--cpus 1.5` is shorthand for a CFS period of 100,000 microseconds and a quota of 150,000. Docker writes that to the cgroup's `cpu.max` (`150000 100000`), and `--cpu-period` and `--cpu-quota` set the two numbers directly ([Resource constraints](https://docs.docker.com/engine/containers/resource_constraints/)). A CPU limit does not kill anything. When the container has used its quota for a period, the kernel pauses its processes until the next one, which is **throttling**. It shows as latency, never as an error. The counters are in `cpu.stat`:

```console
$ cat /sys/fs/cgroup/cpu.stat
usage_usec 8123456
user_usec 8000012
system_usec 123444
nr_periods 410
nr_throttled 387
throttled_usec 21004455
```

`nr_throttled` against `nr_periods` is the share of periods in which the container hit its quota, and `throttled_usec` is the total time spent paused ([kernel cgroup v2 documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html)). A service with a tight `--cpus` and many threads can burn its quota in the first few milliseconds of a period and sit paused for the rest, so p99 latency suffers while average CPU looks low. `--cpu-shares` is a different thing: a relative weight that matters only when containers compete.

### Does the runtime inside see the limit?

Inside the container, `/sys/fs/cgroup/memory.max` and `cpu.max` show the limit, because on cgroup v2 a container gets its own view of the hierarchy. A language runtime has to read them and many used to read the host's numbers instead. `nproc` and the CPU count a library reports are about which CPUs the process may run on, and a CFS quota changes the time, not the CPUs, so a container with `--cpus 1` on a 32-core host often still reports 32.

The consequences are concrete. A runtime that sizes its thread pool or its garbage-collector workers from the CPU count starts too many and spends its quota on contention. One that sizes its heap from the host's memory aims above the container's limit and gets OOM killed. Go 1.25 changed this for CPU: on Linux the runtime considers the cgroup's CPU bandwidth limit and sets `GOMAXPROCS` to the lower of that limit and the logical CPU count ([Go 1.25 release notes](https://go.dev/doc/go1.25)). Older Go, and any runtime you have not checked, may not, so read its documentation for how it reads the cgroup, and test with the real limit.

## Practice

1. ▢ A container exits with code 137 right after you stopped it. Which observation proves the cause was an OOM kill rather than a stop timeout?

    - a) The exit code is 137 in inspect
    - b) The container stopped faster than ten seconds
    - c) The OOMKilled flag is true in inspect
    - d) The host showed high load during stop

<details markdown="1"><summary>Check</summary>

**c)** The `OOMKilled` state is set when the kernel killed the container's processes for exceeding its memory limit. (a) is wrong because a stop timeout also ends in 137. (b) proves nothing, since an OOM kill can coincide with a stop. (d) is correlation and says nothing about which process was killed or why.

</details>

2. ▢ Predict, then run. What do these two commands print?

    ```console
    $ docker run --rm --memory 256m alpine cat /sys/fs/cgroup/memory.max
    $ docker run --rm --cpus 1.5 alpine cat /sys/fs/cgroup/cpu.max
    ```

<details markdown="1"><summary>Hint</summary>

256 MiB is 256 × 1024 × 1024 bytes. `--cpus` is a quota against a 100,000 microsecond period.

</details>

<details markdown="1"><summary>Check</summary>

```text
268435456
150000 100000
```

On a host with cgroup v2. The first is 256 MiB in bytes, and the second is the quota and period for one and a half CPUs. On a cgroup v1 host the files are at different paths, which is why this track uses v2.

</details>

3. ▢ Predict, then run. The container below tries to hold 200 MB under a 64 MB limit with no swap. What is printed, what is `echo $?` after the first command, and what does the inspect line print?

    ```console
    $ docker run --name hog --memory 64m --memory-swap 64m python:3.13-slim python -c "b = b'x' * (200 * 1024 * 1024); print('allocated')"
    $ echo $?
    $ docker inspect --format '{{.State.OOMKilled}} {{.State.ExitCode}}' hog
    ```

<details markdown="1"><summary>Hint</summary>

The kernel enforces `memory.max` while the pages are filled in. Does the Python code get a chance to print anything?

</details>

<details markdown="1"><summary>Check</summary>

The first command prints nothing, `echo $?` prints `137`, and inspect prints `true 137`. The kernel kills Python with `SIGKILL` while the bytes object is being filled in, so the `print` never runs and no Python exception is raised. Without `--memory-swap 64m`, a host with swap would allow 128 MB in total here, still under 200 MB, so the kill would come later and after some thrashing.

</details>

4. ▢ A service runs fine on a laptop and shows p99 latency spikes in a container started with `--cpus 1`. CPU usage is only 40% on the dashboard. What do you check, and what does it mean?

<details markdown="1"><summary>Check</summary>

Read `cpu.stat` in the container's cgroup, or `docker stats` over time. A rising `nr_throttled` and `throttled_usec` means the container is hitting its quota and being paused. A multi-threaded service can use its whole 100 ms quota in a few milliseconds and wait for the rest of the period, and an average over seconds hides it. The fixes are a higher `--cpus`, fewer worker threads, or a runtime that sizes itself from the quota.

</details>

5. ▢ A service starts 32 worker threads, one per CPU it sees, in a container limited to `--cpus 2` on a 32-core host, and is slow under load. What is the most likely cause, and what do you check first?

<details markdown="1"><summary>Check</summary>

The runtime read the host's CPU count instead of the quota, so it started far more workers than two CPUs can run, and they spend the quota contending. Check what CPU count the runtime thinks it has and how its version reads the cgroup. Go 1.25 and later set `GOMAXPROCS` from the cgroup limit ([release notes](https://go.dev/doc/go1.25)); for another runtime read its documentation or set the thread count explicitly.

</details>

6. ▢ You are told to give a database container a memory limit equal to what it uses today "to be safe". Explain what can go wrong and how you would pick the number.

<details markdown="1"><summary>Check</summary>

A limit equal to current usage leaves nothing for growth, caches or a spike, and the OOM kill hits the process that holds your data. Measure peak usage over a realistic load and a full day, add headroom, and check the limit against what the software itself is configured to use (a database's buffer settings count against it). Set `--memory-swap` equal to `--memory` so it fails visibly instead of swapping. Treat each OOM kill as a number to raise or a leak to fix, not as noise.

</details>

## Real-world reps

- [ ] Start any container with `--memory 128m --cpus 0.5` and read `memory.max` and `cpu.max` from inside. Match them to the flags.
- [ ] Run a CPU-bound loop in a container with `--cpus 0.5`, watch `docker stats`, and read `nr_throttled` in `cpu.stat` before and after.
- [ ] Tomorrow: without notes, say how to tell an OOM kill from a stop timeout when both exit with 137, and what throttling looks like from the outside.

## Going further

- [Running Containers](../reference/running-containers.md)
- [Docs: "Resource constraints", Docker](https://docs.docker.com/engine/containers/resource_constraints/)
- [Docs: "Control Group v2", Linux kernel documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html), the `memory.max`, `memory.events`, `cpu.max` and `cpu.stat` entries
- [Docs: Go 1.25 release notes, The Go Project](https://go.dev/doc/go1.25), the container-aware `GOMAXPROCS` entry
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
