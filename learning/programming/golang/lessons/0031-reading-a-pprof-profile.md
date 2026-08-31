---
title: 31. Reading a pprof Profile
description: Find where the time and the memory actually go, before changing a single line
type: lesson
---

# Lesson 31. Reading a pprof Profile

**Mission link:** Optimising from a profile rather than from a hunch is the habit that separates a performance claim from a performance result.
**Primary source:** [Profiling Go Programs — The Go Blog](https://go.dev/blog/pprof)
**Prerequisites:** [Lesson 30](0030-benchmarks-you-can-trust.md)

## Warm-up

1. ▢ Which benchmark metric reproduces across machines?

<details markdown="1"><summary>Check</summary>

Allocations per operation. Timing moves with the CPU and the load; allocation count is a property of the code.

</details>

2. ▢ What does `benchstat` add over reading two benchmark outputs?

<details markdown="1"><summary>Check</summary>

A statistical verdict: the difference with a confidence interval, and an explicit "indistinguishable from noise" when that is the truth.

</details>

## Know this

`pprof` samples a running program and tells you where it spent its time or its memory. Two ways in.

**From a test or benchmark:**

```bash
go test -bench=BenchmarkProcess -cpuprofile=cpu.out -memprofile=mem.out ./...
go tool pprof cpu.out
```

**From a running service** — import for the side effect, and the handlers register themselves:

```go
import _ "net/http/pprof"

go func() {
    log.Println(http.ListenAndServe("localhost:6060", nil))
}()
```

```bash
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
```

Bind it to localhost or put it behind auth on a separate port. `/debug/pprof` exposes your source paths, your goroutine stacks, and a way to make the process do work — it is not something to serve publicly.

### The profiles you will use

| Profile | Answers |
|---|---|
| `profile` (CPU) | where is wall-clock CPU time going, sampled at 100 Hz |
| `heap` | what is allocating, and what is still held |
| `goroutine` | what is every goroutine doing right now — the leak tool from Lesson 21 |
| `block` | where goroutines wait on synchronisation (must be enabled) |
| `mutex` | where lock contention is (must be enabled) |
| `allocs` | every allocation since start, not just live ones |

`block` and `mutex` need `runtime.SetBlockProfileRate` and `runtime.SetMutexProfileFraction` turned on, because sampling them always costs something. Both are worth enabling temporarily when a service is slow but the CPU is idle — that combination means waiting, and CPU profiles cannot see waiting.

### Reading it

Inside `go tool pprof`:

```text
(pprof) top            # heaviest functions
(pprof) top -cum       # heaviest including everything they call
(pprof) list Process   # line-by-line cost inside one function
(pprof) web            # a callgraph in the browser (needs graphviz)
```

`flat` versus `cum` is the distinction to internalise. **Flat** is time spent in that function's own code. **Cumulative** includes everything it called. A function with a huge `cum` and a tiny `flat` is a router, not a bottleneck — its callees are where the work is. Sorting by `flat` finds the code doing the work; sorting by `cum` finds the subsystem responsible.

`list` is the command that actually changes decisions: it annotates the source line by line, so "this function is slow" becomes "this line allocates a map on every call".

A flame graph is available with `go tool pprof -http=:8080 cpu.out`, which serves an interactive view — width is cumulative cost, and the shape makes deep call chains obvious at a glance.

### Heap profiles have four views

`inuse_space` is the default: memory currently held. That is the one for a suspected leak. `alloc_space` counts everything ever allocated, including what has been freed — that is the one for garbage-collection pressure, where the problem is allocation *rate* rather than retained bytes. `inuse_objects` and `alloc_objects` are the same two by count, and a small number of bytes in a huge number of objects is a different problem from the reverse.

Choosing the wrong view sends you after the wrong bug. A service with 200 MB held and a slow GC usually has an `alloc_space` problem, not an `inuse_space` one.

### The discipline

1. Reproduce the symptom under realistic load.
2. Take a profile *while it is happening*.
3. Read `top` and `list` before forming a theory.
4. Change one thing.
5. Prove it with `benchstat`, and re-profile to confirm the hotspot moved.

Step 5 catches the case where you made the function faster and the system no worse than before. That happens more often than anyone expects, because removing a bottleneck usually just relocates it.

## Practice

1. ▢ A function shows a large `cum` and near-zero `flat`. What does that mean?

<details markdown="1"><summary>Check</summary>

It calls expensive things but does almost nothing itself — a handler, a wrapper, a dispatcher.

Optimising it is pointless; the cost is in its callees. Use `top -cum` to find which subsystem is expensive, then `top` and `list` to find the specific code inside it.

</details>

2. ▢ Your service is slow, and a CPU profile shows almost no time anywhere. What next?

<details markdown="1"><summary>Check</summary>

It is waiting, not computing. A CPU profile samples running goroutines and cannot see blocked ones.

Enable the block and mutex profiles, and take a goroutine profile. The answer is usually lock contention, an unbuffered channel, or a slow dependency — and the goroutine profile shows all three as a pile of stacks parked on the same line.

</details>

3. ▢ You suspect a memory leak. Which heap view do you open?

   - a) `alloc_space`, every byte ever allocated
   - b) `inuse_space`, the bytes currently held
   - c) `alloc_objects`, every object ever created
   - d) `inuse_objects`, the objects currently held

<details markdown="1"><summary>Check</summary>

**b)** `inuse_space`, the bytes currently held.

A leak is memory that is retained, which is exactly what `inuse_space` shows. The `alloc_*` views include everything already collected, so a busy-but-healthy service dominates them.

`inuse_objects` is the right follow-up when the bytes look small but the count is enormous — many tiny retained objects is a distinct failure with a different fix.

</details>

4. ▢ Why should `/debug/pprof` not be exposed publicly?

<details markdown="1"><summary>Check</summary>

It reveals source file paths, function names and full goroutine stacks — a map of your internals — and the endpoints let an unauthenticated caller make the process do expensive work on demand.

Bind it to localhost and reach it through a tunnel, or serve it on a separate port that is only reachable from inside the cluster. It is a debugging interface, not an API.

</details>

5. ▢ Interleaving Lesson 21: which profile do you take when a deploy hangs during shutdown?

<details markdown="1"><summary>Check</summary>

The goroutine profile, at `?debug=2`, while it is hanging. It prints every stack with how long it has been blocked, and the goroutine that never saw the cancellation will be sitting on an identifiable line.

The window is short, so it is worth having the pprof endpoint already wired and the command already in the runbook. Discovering you need it during an incident is how the incident gets longer.

</details>

## Real-world reps

- [ ] Profile a benchmark of a function you wrote. Run `top`, then `top -cum`, then `list` on the heaviest function, and note how the picture changes at each step.
- [ ] Add `net/http/pprof` on localhost to a scratch service, put it under load, and capture a 30-second CPU profile. Open it with `-http=:8080` and read the flame graph.
- [ ] Tomorrow: write the pprof capture commands into a runbook for a service you operate — CPU, heap and goroutine. Three lines you will be glad to have.

## Going further

- [Profiling Go Programs — The Go Blog](https://go.dev/blog/pprof)
- [Diagnostics — The Go Authors](https://go.dev/doc/diagnostics) — profiling, tracing and debugging in one place
- [`net/http/pprof`](https://pkg.go.dev/net/http/pprof)
- [Toolchain Commands](../reference/toolchain-commands.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
