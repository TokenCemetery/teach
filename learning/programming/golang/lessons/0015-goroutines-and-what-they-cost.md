---
title: 15 — Goroutines and What They Cost
description: Cheap enough to start thousands, never free enough to start without a plan to stop
type: lesson
---

# Lesson 15 — Goroutines and What They Cost

**Mission link:** Predicting what a concurrent program does starts with knowing what `go` actually creates, what schedules it, and what happens to it when `main` returns.
**Primary source:** [Concurrency is not parallelism — Rob Pike](https://go.dev/blog/waza-talk)
**Prerequisites:** [Lesson 10](0010-defer-panic-and-recover.md)

## Warm-up

1. ▢ What does embedding `sync.Mutex` in an exported struct add to your API?

<details markdown="1"><summary>Check</summary>

Exported `Lock` and `Unlock` methods, callable by anyone. Use a named `mu sync.Mutex` field instead.

</details>

2. ▢ Where should a package's sentinel errors be documented, and why does it matter?

<details markdown="1"><summary>Check</summary>

In the doc comment of the function that returns them. Once documented they are API — callers match on them with `errors.Is`, and changing them is a breaking change nothing will catch at compile time.

</details>

## Know this

`go f()` starts a **goroutine**: an independently scheduled function call. The statement returns immediately, and `f` runs concurrently.

```go
go handle(conn)   // returns now; handle runs somewhere
```

The runtime multiplexes many goroutines onto few OS threads. `GOMAXPROCS` sets how many can run Go code simultaneously and defaults to the CPUs available to the process. A goroutine that blocks on a channel, a mutex or a syscall does not hold a thread hostage — the scheduler parks it and runs something else. Since Go 1.14 preemption is asynchronous, so even a tight loop with no function calls can be interrupted.

The cost is a few kilobytes of stack, which grows and shrinks on demand rather than being reserved up front. Ten thousand goroutines is ordinary; one per incoming request is what `net/http` already does for you.

### What "cheap" does not mean

Cheap per goroutine is not free in aggregate, and three costs bite in production:

- **Memory.** Each goroutine holds its stack plus everything the stack references. A million blocked goroutines each holding a 4 KB buffer is four gigabytes — the buffers are the problem, not the goroutines.
- **Unbounded fan-out.** `for _, item := range items { go process(item) }` over a caller-controlled list is a denial of service you wrote yourself. Bound it with a worker pool or `errgroup.SetLimit`.
- **Leaks.** A goroutine blocked forever is never collected, and neither is anything it references. That is [Lesson 21](0021-goroutine-leaks.md), and it is the most common Go production bug there is.

The discipline that prevents all three: **never start a goroutine without knowing how it will stop.**

### `main` does not wait

When `main` returns the process exits, and every remaining goroutine dies wherever it happens to be, with no deferred functions run:

```go
func main() {
    go fmt.Println("hello")   // usually prints nothing
}
```

There is no `Join`. Coordination is explicit — a channel, a `sync.WaitGroup`, or an `errgroup` — and choosing between them is most of stage 3.

### Coming from Java 21

Goroutines and virtual threads are the same idea: many lightweight tasks multiplexed onto a small pool of carrier threads, where a blocking call parks the task rather than the thread. The instincts that transfer:

- Blocking is fine. Do not build callback chains to avoid it.
- Thread-per-request becomes task-per-request, and the count can be very large.

The instincts that do not:

| | Java 21 virtual threads | Goroutines |
|---|---|---|
| Cancellation | `Thread.interrupt`, or a structured concurrency scope | `context.Context`, passed explicitly as an argument |
| Coordination | Futures, `StructuredTaskScope` | Channels and `select` |
| Task-local state | `ThreadLocal` works, `ScopedValue` preferred | No equivalent, deliberately |
| Identity | `Thread.currentThread()` | No goroutine id is exposed |

The missing goroutine identity is a decision rather than an omission. It makes task-local state impossible, which forces every dependency to appear in a signature. When you find yourself wanting a `ThreadLocal`, the Go answer is a `ctx` argument or a struct field.

### The loop variable, before and after Go 1.22

This was the language's most notorious gotcha, and it is worth knowing because you will read older code and older blog posts:

```go
for _, v := range items {
    go func() { fmt.Println(v) }()
}
```

Before Go 1.22 `v` was a single variable reused by every iteration, so the goroutines usually all printed the last item. The workarounds — `v := v` shadowing, or passing `v` as an argument — are everywhere in existing codebases.

Since [Go 1.22](https://go.dev/doc/go1.22#language) each iteration creates a new variable and this code is correct. The semantics are selected by the `go` directive in `go.mod`, so a module still declaring `go 1.21` gets the old behaviour from a new toolchain. Check the directive before trusting the loop.

## Practice

1. ▢ Why does this usually print nothing?

   ```go
   func main() {
       go fmt.Println("hello")
   }
   ```

<details markdown="1"><summary>Check</summary>

`main` returns immediately, and when `main` returns the process exits — killing every other goroutine wherever it happens to be, without running deferred functions.

"Usually" rather than "always" because the goroutine occasionally gets scheduled first. That non-determinism is the point: adding a `time.Sleep` makes it print and is still wrong, because it is a race you happened to win.

</details>

2. ▢ A handler starts one goroutine per item in a request body. Name the failure mode and one bounded alternative.

<details markdown="1"><summary>Check</summary>

Unbounded fan-out: a request with a million items starts a million goroutines, each with a stack and whatever it captured. Memory and scheduler pressure take the process down, and a client can trigger it at will.

Bounded alternatives: a worker pool of fixed size reading from a channel, or `errgroup.Group` with `SetLimit(n)`. Both cap concurrency at a number you chose rather than one the caller chose.

</details>

3. ▢ Which is the accurate statement about goroutine cost?

   - a) Each one reserves a full operating-system thread stack
   - b) Each one starts small and grows its stack on demand
   - c) Each one is pooled and reused after the function returns
   - d) Each one is free until it performs blocking input or output

<details markdown="1"><summary>Check</summary>

**b)** Each one starts small and grows its stack on demand.

Goroutines are multiplexed onto threads rather than mapped to them, so a describes the model they exist to avoid. There is no goroutine pool in the runtime, and nothing is free — the aggregate memory of what the stacks reference is what shows up in a heap profile.

</details>

4. ▢ Coming from Java: where does per-request state go, if there is no `ThreadLocal`?

<details markdown="1"><summary>Check</summary>

Into `context.Context` when it is genuinely request-scoped metadata — a request id, a deadline, an auth subject — and into an ordinary parameter or struct field for everything else.

The absence is deliberate. Implicit task-local state makes dependencies invisible, which is exactly what makes it hard to reason about who reads what. Go pays for the explicitness with longer signatures and buys back the ability to see the dependency at the call site. Lesson 18 covers what may and may not live in a context.

</details>

5. ▢ Interleaving Lesson 2: in Go 1.22 and later, is `go func() { use(v) }()` inside a range loop safe?

<details markdown="1"><summary>Check</summary>

Yes for the loop variable — each iteration now has its own `v`, so nothing is shared between iterations.

It is not safe for anything else the closure captures: a shared map, a slice being appended to, a counter. The loop-variable fix removed one specific bug, not the need to think about what a closure captures. And if `go.mod` says `go 1.21` or lower, even the loop variable is still shared.

</details>

## Real-world reps

- [ ] Run the `go fmt.Println("hello")` program ten times. Then add a `sync.WaitGroup` and make it deterministic.
- [ ] Start 100,000 goroutines that each block on an empty channel, and watch the process memory with `runtime.NumGoroutine()` and a heap profile. That is the shape of a leak, made deliberately.
- [ ] Tomorrow: check the `go` directive in a `go.mod` you work with. If it is below `1.22`, every closure in a loop in that module is worth a second look.

## Going further

- [Concurrency is not parallelism — Rob Pike](https://go.dev/blog/waza-talk)
- [Go 1.22 loop variable change](https://go.dev/blog/loopvar-preview)
- [`golang.org/x/sync/errgroup`](https://pkg.go.dev/golang.org/x/sync/errgroup) — `SetLimit` is the bounded fan-out primitive
- [Concurrency Patterns](../reference/concurrency-patterns.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top — this lesson compresses it, and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
