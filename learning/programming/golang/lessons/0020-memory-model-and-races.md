---
title: 20 — The Memory Model and Races
description: A data race is undefined behaviour, not a coin flip, and the detector only sees what runs
type: lesson
---

# Lesson 20 — The Memory Model and Races

**Mission link:** Reasoning about concurrency from the memory model instead of from experiment is what lets you say a design is wrong before it has failed in production.
**Primary source:** [The Go Memory Model — The Go Authors](https://go.dev/ref/mem)
**Prerequisites:** [Lesson 19](0019-sync-primitives.md)

## Warm-up

1. ▢ Why must a lock never be held across a network call?

<details markdown="1"><summary>Check</summary>

Because a slow dependency becomes a total stall — every goroutine wanting the lock queues behind one remote call. Copy what you need, unlock, then make the call.

</details>

2. ▢ What does `errgroup.WithContext` add over a `WaitGroup`?

<details markdown="1"><summary>Check</summary>

The first error cancels the shared context so the other goroutines stop, and `Wait` returns that error. A `WaitGroup` only counts.

</details>

## Know this

A **data race** is: two goroutines access the same memory location, at least one access is a write, and there is no synchronisation ordering them.

All three parts matter. Concurrent reads are fine. Writes to *different* variables are fine. A write and a read with a happens-before edge between them are fine — and providing that edge is what every primitive in Lesson 19 is for.

### A race is undefined behaviour

The instinct to resist is that a racy counter "loses some increments" or that a racy read "gets the old value or the new one". Neither is guaranteed. The [memory model](https://go.dev/ref/mem) says a program with a data race has no defined behaviour, and in practice the compiler and CPU are allowed to:

- reorder reads and writes, because nothing said they were ordered;
- keep a variable in a register across a loop, so an update from another goroutine is never observed and the loop never ends;
- tear a multi-word value — a slice header or an interface — so a reader sees a new pointer with an old length.

That last one is why a raced interface or slice can produce a segmentation fault rather than a wrong answer. "It has worked so far" is a statement about one compiler version on one architecture under one load.

### Happens-before, briefly

The memory model defines when one goroutine is guaranteed to observe another's writes. The edges you actually use:

| This… | …happens before this |
|---|---|
| A send on a channel | the corresponding receive completes |
| A receive from an unbuffered channel | the corresponding send completes |
| Closing a channel | a receive that returns because it is closed |
| `mu.Unlock()` | a subsequent `mu.Lock()` returning |
| `once.Do(f)` returning in one goroutine | every other `Do` on that `Once` returning |
| `wg.Done()` calls reaching zero | `wg.Wait()` returning |
| An atomic write | a subsequent atomic read of that value |

Everything the writing goroutine did *before* the edge is visible to the reader *after* it. That is the guarantee, and it is why sending a pointer over a channel safely transfers everything it points to.

`sync/atomic` operations are sequentially consistent, documented as such since the 2022 revision of the memory model. So an `atomic.Bool` flag genuinely does establish ordering — unlike a plain `bool`, where the compiler may never reread it at all.

### The race detector

```bash
go test -race ./...
```

It is a dynamic analysis built on ThreadSanitizer. Two properties define how to use it:

- **No false positives.** When it reports a race, there is a race. Do not argue with it.
- **Only what executes.** It sees the accesses that actually happened in that run. Code paths not taken, and interleavings that did not occur, are invisible. A clean run is evidence, not proof.

Cost is real — roughly 2–20× slower and 5–10× more memory — so it belongs in CI and in load tests against a staging build, not in production. Because coverage is the limiting factor, a race detector run over a *test suite that exercises concurrency* is worth far more than one over unit tests that run everything on one goroutine.

### Making concurrent tests deterministic

`testing/synctest`, generally available since [Go 1.25](https://go.dev/doc/go1.25#testing-synctest), runs a test inside a bubble where the `time` package is virtualised: the clock jumps forward instantly when every goroutine in the bubble is blocked, and `synctest.Wait` blocks until they all are.

```go
func TestTimeout(t *testing.T) {
    synctest.Test(t, func(t *testing.T) {
        // a one-hour timeout resolves immediately, deterministically
    })
}
```

This removes the two worst habits in concurrent tests — `time.Sleep` to "let it settle", and generous timeouts that turn a real failure into a flake.

## Practice

1. ▢ Two goroutines each run `counter++` a thousand times with no synchronisation. What is the final value?

<details markdown="1"><summary>Check</summary>

Undefined. Not "somewhere between 1000 and 2000" — that is a mental model of an interleaved read-modify-write, and it assumes an ordering the language does not provide.

In practice you will often see a number in that range, which is exactly what makes the bug survive review. The correct statement is that the program has no defined behaviour, and the correct fix is an `atomic.Int64` or a mutex.

</details>

2. ▢ A goroutine spins on `for !done {}` where `done` is a plain `bool` set by another goroutine. Why might it never exit even after `done` is set?

<details markdown="1"><summary>Check</summary>

Nothing orders the write against the read, so the compiler is free to load `done` once into a register and reuse it — the loop tests a value that can never change.

Fix with an `atomic.Bool`, or better, with a channel closed to signal completion. This is the concrete reason "it is only a bool, a race cannot hurt" is wrong.

</details>

3. ▢ `go test -race ./...` passes. What have you established?

   - a) The code under test contains no data races
   - b) No race occurred in the paths that ran
   - c) The detector found races but tolerated them
   - d) The code is safe for concurrent use everywhere

<details markdown="1"><summary>Check</summary>

**b)** No race occurred in the paths that ran.

The detector has no false positives, so a report is always real — but it observes only executed accesses in one interleaving. Claims a and d overstate a dynamic tool, and c misdescribes it: it never tolerates a race it sees.

The practical consequence is that improving concurrent test coverage improves the detector's reach more than rerunning it does.

</details>

4. ▢ You send a `*Config` over a channel to another goroutine, which reads its fields. Is that a race?

<details markdown="1"><summary>Check</summary>

No, provided the sender does not touch it afterwards. The send happens before the receive completes, so everything the sender wrote to that struct before sending is visible to the receiver.

It becomes a race the moment the sender keeps the pointer and writes to it again. Sending a pointer transfers ownership by convention, and the convention is the only thing enforcing it — the compiler will not stop you writing to it.

</details>

5. ▢ Interleaving Lesson 4: a service crashes with `fatal error: concurrent map writes` in production, and `-race` finds nothing in CI. What do you conclude?

<details markdown="1"><summary>Check</summary>

That the tests never exercise the concurrent path, not that the race is absent. The runtime's map detector fired on real traffic; the race detector had no such interleaving to observe.

Next step is a test that hits the map from several goroutines under `-race`, which will find it in seconds. The production crash already told you where to look — the fatal error names the goroutines' stacks.

</details>

## Real-world reps

- [ ] Write the two-goroutine counter with no synchronisation, run it under `-race`, and read the report. Note that it names both stacks and the variable.
- [ ] Write the `for !done {}` spin loop and run it with optimisations on. If it exits, try it with more work in the loop — then fix it with a channel and stop relying on luck.
- [ ] Tomorrow: check whether `-race` runs in your CI. If it does not, that is a one-line change with a larger payoff than most refactors.

## Going further

- [The Go Memory Model](https://go.dev/ref/mem)
- [Introducing the Go Race Detector — The Go Blog](https://go.dev/blog/race-detector)
- [Testing concurrent code with testing/synctest — The Go Blog](https://go.dev/blog/synctest)
- [Concurrency Patterns](../reference/concurrency-patterns.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top — this lesson compresses it, and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
