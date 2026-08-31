---
title: 35. When Not to Use a Goroutine
description: Concurrency is a structure, not a speedup, and the sequential version is often the right answer
type: lesson
---

# Lesson 35. When Not to Use a Goroutine

**Mission link:** Knowing when *not* to reach for a goroutine is named in the mission. It is the judgment that separates someone who can use Go's concurrency from someone who should be trusted with it.
**Primary source:** [Concurrency is not parallelism, Rob Pike](https://go.dev/blog/waza-talk)
**Prerequisites:** [Lesson 21](0021-goroutine-leaks.md), [Lesson 31](0031-reading-a-pprof-profile.md)

## Warm-up

1. ▢ Which is safe: adding a method to an interface, or adding a method to a struct?

<details markdown="1"><summary>Check</summary>

The struct. Nothing implements a struct, so nothing can break. An interface constrains every implementer, including ones you cannot see.

</details>

2. ▢ Why is a documented sentinel error part of your compatibility surface?

<details markdown="1"><summary>Check</summary>

Callers match on it with `errors.Is`. Removing it or ceasing to wrap it breaks their branch with no compile error.

</details>

## Know this

Go makes goroutines cheap, which makes them easy to add, which is not the same as free to own. Every one you start adds:

- a **lifecycle** you must design: how it stops, who waits for it, what happens on shutdown ([Lesson 21](0021-goroutine-leaks.md));
- a **synchronisation surface**, because anything it touches is now shared and shared plus written is a race ([Lesson 20](0020-memory-model-and-races.md));
- **non-determinism in tests**, which is where flakes come from;
- **harder debugging**, because a stack trace no longer tells the whole story.

That cost is worth paying when concurrency buys you something. Frequently it does not.

### Concurrency is not parallelism

Concurrency is a way to *structure* a program as independently executing parts. Parallelism is *executing* things simultaneously. Concurrent structure enables parallel execution when there is hardware for it, and structuring something concurrently does not, by itself, make it faster.

The measurable costs of splitting work up: channel operations and lock acquisitions, scheduler switches, and cache locality lost when data moves between cores. For small units of work these dominate, and the concurrent version is **slower** than the sequential one. That is not a rare edge case: it is the usual result for anything CPU-light with a small input.

### The cases where sequential wins

**The work is small.** A hundred items of pure computation is faster in a loop than fanned out. The coordination costs more than the work.

**The result is needed immediately anyway.** Starting a goroutine and blocking on its result is a slower function call with extra failure modes.

```go
ch := make(chan Result)
go func() { ch <- compute() }()
r := <-ch                      // this is compute(), with steps
```

**The work is already parallel one level up.** An HTTP server already runs one goroutine per request. Fanning out inside a handler multiplies concurrency by request rate, so under load that is thousands of goroutines competing for the same CPUs, and total throughput usually drops.

**Ordering matters.** If results must be ordered, you fan out and then reassemble, and the reassembly is the code most likely to be wrong.

**It is fire-and-forget.** `go audit(event)` with nothing waiting on it: nobody sees the error, nobody knows if it finished, and shutdown cannot wait for it. If the work matters, give it a lifecycle: a queue, a worker with a context. If it does not matter, question whether to do it at all.

### The cases where it earns its place

- **Genuinely independent I/O**, where waiting dominates: five API calls that can overlap turn 500 ms into 100 ms.
- **Background work with a real lifecycle**, such as a ticker, a queue consumer or a cache refresher, started at boot and stopped at shutdown.
- **Producer/consumer structure** where the concurrency makes the program *clearer*, not merely faster. A pipeline reading, transforming and writing is easier to read as three stages than one interleaved loop.
- **Bounded parallelism over a large CPU-bound workload**, sized to `GOMAXPROCS`, proven with a benchmark.

### The questions to ask in review

1. What stops this goroutine?
2. Who waits for it, and what happens to its error?
3. What does it share, and what protects that?
4. Is there a measurement showing the concurrent version is faster?
5. Would the sequential version be simpler to read?

If four of the five have no good answer, the answer is a loop.

## Practice

1. ▢ A handler fans out to process 50 items concurrently and returns when all are done. Under load, latency gets worse. Why?

<details markdown="1"><summary>Check</summary>

The server already runs one goroutine per request. With 200 concurrent requests, the fan-out means 10,000 goroutines competing for the same cores, plus the scheduling, coordination and cache thrash to go with it.

Total throughput on a saturated machine is bounded by the CPUs, not by the goroutine count. Adding concurrency inside a request only helps when each request is waiting rather than computing.

</details>

2. ▢ What is wrong with `go audit(event)` in a handler?

<details markdown="1"><summary>Check</summary>

No lifecycle. Its error goes nowhere, nothing knows whether it ran, and shutdown will not wait for it, so the last few events before every deploy are silently lost. A panic inside it takes the process down, because nothing recovers there.

If the audit matters, it needs an owner: a queue with a worker that has a context and is drained at shutdown. If it does not matter enough to justify that, it probably should not exist.

</details>

3. ▢ Which is the strongest case for a goroutine?

   - a) Five independent HTTP calls whose latency overlaps
   - b) A hundred integer conversions inside one loop
   - c) A single computation whose result is needed next
   - d) An audit write that nobody waits on or checks

<details markdown="1"><summary>Check</summary>

**a)** Five independent HTTP calls whose latency overlaps.

Waiting dominates, the calls do not depend on each other, and the win is real: roughly the slowest call instead of the sum. Option b is dominated by coordination cost, c is a function call with extra steps, and d is a leak with no error handling.

</details>

4. ▢ Someone claims their concurrent version is faster. What do you ask for?

<details markdown="1"><summary>Check</summary>

A benchmark of both, `-count=10`, through `benchstat`, at a realistic input size and a realistic level of external concurrency.

Concurrency has a fixed coordination cost and a variable benefit, so the answer usually depends on the input size, and a benchmark at one size can support either conclusion. Ask which sizes were measured.

</details>

5. ▢ Interleaving Lesson 25: how does an extra goroutine complicate shutdown?

<details markdown="1"><summary>Check</summary>

Shutdown has to know it exists, be able to tell it to stop, and wait for it. Otherwise the drain either misses it or hangs on it.

That is three things to get right per goroutine, which is why `errgroup` and a single cancellable context are worth the structure: they make ownership explicit and give shutdown one thing to wait on rather than a set nobody has enumerated.

</details>

## Real-world reps

- [ ] Benchmark summing a slice sequentially against a fan-out version, at 100, 10,000 and 1,000,000 elements. Find the size where concurrency starts to win. It will be larger than you expect.
- [ ] Find a `go` statement in code you work with and answer the five review questions for it. If any answer is "nothing", you have found something.
- [ ] Tomorrow: take the most concurrent function you have written and write the sequential version beside it. Decide honestly which you would rather debug at 3am.

## Going further

- [Concurrency is not parallelism, Rob Pike](https://go.dev/blog/waza-talk)
- [Go Proverbs](https://go-proverbs.github.io/): several are about restraint
- [Review Checklist](../reference/review-checklist.md)
- [Concurrency Patterns](../reference/concurrency-patterns.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
