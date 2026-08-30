---
title: 19 — sync and errgroup
description: When sharing memory beats passing it, and the four primitives that cover almost everything
type: lesson
---

# Lesson 19 — sync and errgroup

**Mission link:** "Share memory by communicating" is good advice and a bad absolute. Knowing when a mutex is the simpler answer is part of being trusted with the design.
**Primary source:** [`sync` package documentation](https://pkg.go.dev/sync)
**Prerequisites:** [Lesson 18](0018-context-cancellation.md)

## Warm-up

1. ▢ What actually happens to a goroutine when its context is cancelled?

<details markdown="1"><summary>Check</summary>

Nothing, unless the goroutine looks. A channel closes; cancellation is cooperative and reaches only as far as your code checks.

</details>

2. ▢ Why must `cancel` always be called, even when the timeout will fire anyway?

<details markdown="1"><summary>Check</summary>

Until it runs, the child context stays attached to its parent and its timer stays live. In a per-request path that accumulates with traffic.

</details>

## Know this

The Go proverb is *do not communicate by sharing memory; share memory by communicating.* It is a default, not a law. When several goroutines need to read and update one piece of state, a mutex is usually shorter, faster and easier to review than a goroutine owning the state behind a channel.

Use a channel to transfer ownership or to coordinate timing. Use a mutex to protect state that stays where it is.

### Mutex

```go
type Cache struct {
    mu sync.Mutex
    m  map[string]int
}

func (c *Cache) Get(k string) (int, bool) {
    c.mu.Lock()
    defer c.mu.Unlock()
    v, ok := c.m[k]
    return v, ok
}
```

The field sits directly above what it guards, and a comment naming what it guards is worth writing when it is not obvious. `defer c.mu.Unlock()` immediately after `Lock` is the standard shape — it survives every early return and every panic.

Two rules that prevent most mutex incidents:

- **Never hold a lock across I/O.** A network call under a lock turns a slow dependency into a total stall. Copy what you need, unlock, then do the call.
- **Mutexes are not reentrant.** Locking twice from the same goroutine deadlocks. A method that locks must not call another method that locks; extract an unexported helper that assumes the lock is held.

`sync.RWMutex` allows many concurrent readers or one writer. It pays off with genuinely read-heavy access and long critical sections, and it is often *slower* than a plain `Mutex` for short ones, because the bookkeeping costs more than the contention it removes. Measure before switching.

### Once

```go
var once sync.Once
once.Do(func() { conn = connect() })
```

Runs exactly once, however many goroutines arrive, and every caller blocks until the first completes. Useful for lazy initialisation. It is not useful for anything that can fail and should be retried — `Do` will not run again, and the error handling has to live outside.

### WaitGroup

```go
var wg sync.WaitGroup
for _, u := range urls {
    wg.Go(func() { fetch(u) })   // Go 1.25
}
wg.Wait()
```

`WaitGroup.Go` arrived in [Go 1.25](https://go.dev/doc/go1.25) and replaces the three-line `wg.Add(1)` / `go func()` / `defer wg.Done()` dance that every codebase has. On an older toolchain, write that dance and put `defer wg.Done()` as the first line of the goroutine.

A `WaitGroup` must not be copied after first use — pass `*sync.WaitGroup`, or capture it in a closure.

### atomic

For a single counter or flag, `sync/atomic`'s typed values are simpler and faster than a mutex:

```go
var requests atomic.Int64
requests.Add(1)
fmt.Println(requests.Load())
```

The typed forms — `atomic.Int64`, `atomic.Bool`, `atomic.Pointer[T]` — arrived in Go 1.19 and should be preferred over the older `atomic.AddInt64(&n, 1)` functions, which require you to remember alignment rules on 32-bit platforms.

Atomics protect *one* variable. Two atomics updated together are not consistent with each other, and reaching for a second one is the signal to use a mutex instead.

### sync.Map is narrower than it looks

`sync.Map` is not "a map with a lock". It is optimised for two specific patterns: keys written once and read many times, and disjoint key sets per goroutine. Outside those, a plain map behind a `sync.Mutex` is typically faster and always clearer — and it keeps static types, which `sync.Map`'s `any` interface gives up.

### errgroup

`golang.org/x/sync/errgroup` is the right tool for fan-out that can fail:

```go
g, ctx := errgroup.WithContext(ctx)
g.SetLimit(8)                            // bounded concurrency

for _, id := range ids {
    g.Go(func() error {
        return fetch(ctx, id)
    })
}
if err := g.Wait(); err != nil {         // first non-nil error
    return err
}
```

`WithContext` cancels the derived context as soon as any goroutine returns an error, so the rest stop instead of finishing work nobody wants. `SetLimit` bounds the fan-out from Lesson 15. `Wait` returns the first error and waits for every goroutine either way.

This is the closest thing Go has to structured concurrency, and it is a library rather than a language feature — which is the shape of most concurrency machinery in Go.

## Practice

1. ▢ Why is `defer mu.Unlock()` written immediately after `mu.Lock()` rather than at the end of the function?

<details markdown="1"><summary>Check</summary>

So it cannot be skipped. Every early return, and every panic that unwinds through the function, still releases the lock — and a lock leaked by an error path is a deadlock that only appears when something else has already gone wrong.

Writing it adjacent to the `Lock` also makes the pairing visible in review, which is worth more than the couple of nanoseconds `defer` costs.

</details>

2. ▢ A method locks the mutex and calls another method on the same type that also locks it. What happens?

<details markdown="1"><summary>Check</summary>

Deadlock. Go's mutexes are not reentrant, and the second `Lock` blocks forever waiting for a lock its own goroutine holds.

The fix is an unexported helper that assumes the lock is held — conventionally named `getLocked` or similar — called by both the exported method and the other caller. Recursive locking is not a feature Go withholds by accident: it makes the critical section's extent impossible to see.

</details>

3. ▢ You need a request counter shared by many goroutines. Which is the best fit?

   - a) A plain int guarded by a `sync.Mutex`
   - b) An `atomic.Int64` incremented with Add
   - c) A channel that a counting goroutine reads
   - d) A `sync.Map` keyed by the counter name

<details markdown="1"><summary>Check</summary>

**b)** An `atomic.Int64` incremented with `Add`.

One variable, one operation — exactly what atomics are for, with less code and less contention than a mutex. Option a works and is heavier. Option c adds a goroutine and a channel to increment a number. Option d misuses a structure built for a different access pattern.

The answer changes the moment you need two numbers to agree: then it is a mutex.

</details>

4. ▢ What does `errgroup.WithContext` give you that a `WaitGroup` does not?

<details markdown="1"><summary>Check</summary>

Error propagation and cancellation. The first goroutine to return an error cancels the derived context, so the others stop rather than finishing work whose result will be discarded, and `Wait` returns that error.

A `WaitGroup` only counts. Collecting errors from it means a channel or a mutex-guarded slice, and there is no mechanism to tell the survivors to stop — which is why hand-rolled versions of this are usually where a leak lives.

</details>

5. ▢ Interleaving Lesson 4: your `Cache` embeds a map guarded by a mutex, and a profile shows `Get` is hot. Is `RWMutex` the fix?

<details markdown="1"><summary>Check</summary>

Maybe, and only with a measurement. `RWMutex` wins when reads dominate *and* the critical section is long enough for the extra bookkeeping to pay off. A map lookup is nanoseconds, so a plain `Mutex` frequently beats it.

Run the benchmark both ways under realistic concurrency — stage 5 gives you `benchstat` for exactly this. The trap is that a change justified by a plausible story often measures worse, and nobody goes back to check.

</details>

## Real-world reps

- [ ] Write the `Cache` with a `sync.Mutex`, then rewrite it with a goroutine owning the map and a channel of requests. Compare the line counts and decide which you would rather review.
- [ ] Convert a `wg.Add`/`go`/`defer wg.Done()` block to `wg.Go`. Confirm your `go.mod` allows Go 1.25 first.
- [ ] Tomorrow: find a lock held across a network call in a codebase you work with. If there is none, you have looked at a well-reviewed codebase; if there is one, you have found the next incident.

## Going further

- [`sync` package](https://pkg.go.dev/sync)
- [`sync/atomic` package](https://pkg.go.dev/sync/atomic)
- [`errgroup`](https://pkg.go.dev/golang.org/x/sync/errgroup)
- [Go Proverbs](https://go-proverbs.github.io/) — the "share memory by communicating" line, in context
- [Concurrency Patterns](../reference/concurrency-patterns.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top — this lesson compresses it, and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
