---
title: 21. Goroutine Leaks
description: A goroutine blocked forever is never collected, and neither is anything it holds
type: lesson
---

# Lesson 21. Goroutine Leaks

**Mission link:** This is the failure that closes stage 3: finding a leak in code you did not write, and naming the guarantee that was missed. It is also the most common Go production bug.
**Primary source:** [Never start a goroutine without knowing how it will stop, Dave Cheney](https://dave.cheney.net/2016/12/22/never-start-a-goroutine-without-knowing-how-it-will-stop)
**Prerequisites:** [Lesson 20](0020-memory-model-and-races.md)

## Warm-up

1. ▢ What are the three conditions for a data race?

<details markdown="1"><summary>Check</summary>

Two goroutines access the same memory, at least one access is a write, and nothing establishes a happens-before ordering between them.

</details>

2. ▢ `go test -race` passes. What does that prove?

<details markdown="1"><summary>Check</summary>

That no race occurred in the interleavings that ran. The detector has no false positives and plenty of blind spots.

</details>

## Know this

A **goroutine leak** is a goroutine that will never finish, because it is blocked on something that will never happen. The runtime cannot collect it, so its stack stays, and so does every object its stack references. A leak that grows with traffic is a slow memory leak with a scheduler cost attached.

Unlike a deadlock, nothing reports it. `all goroutines are asleep` fires only when *every* goroutine is blocked, and a leaking service has a perfectly healthy HTTP listener.

### The four shapes

**Send with no receiver.** The most common one, and it hides behind an early return:

```go
func search(ctx context.Context, queries []string) (string, error) {
    ch := make(chan string)          // unbuffered
    for _, q := range queries {
        go func() { ch <- lookup(q) }()   // blocks until someone receives
    }
    return <-ch, nil                 // takes the first, abandons the rest
}
```

The first result returns. Every other goroutine is parked on its send forever. Fix by giving the channel capacity `len(queries)` so every send completes, or by cancelling the rest with a context.

**Receive with no sender.** A goroutine ranging a channel nobody closes, or waiting on a result the producer failed to send because it returned an error first.

**No cancellation case.** A worker `select`ing only on its job channel: when shutdown comes, nothing tells it to stop, so the process hangs until the shutdown timeout kills it.

**A forgotten `Ticker`.** `time.NewTicker` without `defer ticker.Stop()` while you still hold the reference. Since Go 1.23 an *unreferenced* timer is collected, but a ticker held in a struct field is referenced, and the goroutine reading it never ends.

### Finding them

The goroutine profile is the first tool, and it works on a running service:

```bash
curl 'http://localhost:6060/debug/pprof/goroutine?debug=2' > goroutines.txt
```

`debug=2` prints every goroutine's full stack with how long it has been blocked. A leak looks like ten thousand goroutines parked on the same line of your code. Take two profiles ten minutes apart and diff the counts: a leak grows, normal load does not.

Since [Go 1.27](https://go.dev/doc/go1.27) there is a purpose-built profile: `goroutineleak`, in `runtime/pprof` and at `/debug/pprof/goroutineleak`. The runtime uses the garbage collector to find goroutines blocked on a primitive that is unreachable from any runnable goroutine, which cannot possibly be unblocked, and is therefore leaked rather than merely slow. It was an experiment in Go 1.26 and is generally available in 1.27. It does not find every leak: a channel still reachable through a global, or through a running goroutine's locals, looks live to the collector.

In tests, [`go.uber.org/goleak`](https://pkg.go.dev/go.uber.org/goleak) fails a test that finishes with goroutines it did not start. One line in `TestMain` covers a whole package.

### Not leaking, by construction

- Every goroutine gets a `ctx`, and every long-lived loop has a `case <-ctx.Done()`.
- Every send has a receiver that is guaranteed to arrive, or a buffer big enough that it cannot block, or a `select` with `ctx.Done()`.
- Whoever starts a goroutine is responsible for its shutdown. `errgroup` makes that ownership explicit; a bare `go f()` in the middle of a function usually does not.
- Close response bodies. `defer resp.Body.Close()` is a connection leak rather than a goroutine leak, and it shows up in the same incident.

The question to ask in review is the one in the title of the primary source: **how does this goroutine stop?** If the answer takes more than a sentence, it probably does not.

## Practice

1. ▢ Find the leak.

   ```go
   ch := make(chan string)
   for _, q := range queries {
       go func() { ch <- lookup(q) }()
   }
   return <-ch
   ```

<details markdown="1"><summary>Check</summary>

The channel is unbuffered and only one value is received. Every other goroutine blocks on its send forever, holding its stack, its captured `q`, and whatever `lookup` allocated.

Two fixes. `make(chan string, len(queries))` lets every send complete so each goroutine exits after sending. Or derive a cancellable context, `select` on `ctx.Done()` in the send, and cancel once you have your answer, which also stops the redundant `lookup` calls.

</details>

2. ▢ Why does the runtime not report this, when it reports `all goroutines are asleep - deadlock!`?

<details markdown="1"><summary>Check</summary>

That check fires only when *every* goroutine in the process is blocked. Here `main` returned a value and carried on, and in a real service the HTTP listener is always runnable.

This asymmetry is why leaks are found with profiles rather than crashes: the program keeps working correctly while consuming more memory every minute.

</details>

3. ▢ Which command shows you goroutines blocked in your service right now?

   - a) `go test -race ./... -count 1`
   - b) `curl localhost:6060/debug/pprof/goroutine?debug=2`
   - c) `go build -gcflags=-m ./... 2>&1`
   - d) `GODEBUG=gctrace=1 ./svc 2>&1 | tail`

<details markdown="1"><summary>Check</summary>

**b)** `curl localhost:6060/debug/pprof/goroutine?debug=2`.

The race detector finds unsynchronised access, not blocked goroutines. `-gcflags=-m` prints escape analysis, which is Lesson 32, and `gctrace` reports collections. Only the goroutine profile shows what is parked and where.

</details>

4. ▢ A worker `select`s only on its job channel. Shutdown hangs for 30 seconds and then the process is killed. Explain the sequence.

<details markdown="1"><summary>Check</summary>

Shutdown cancels the context, but the worker never looks at it. Its `select` has one case, and the job channel is empty, so it stays blocked. Whatever is waiting for the worker to finish waits forever, until the shutdown timeout expires and the supervisor kills the process.

The cost is not just the delay: killing mid-flight skips every deferred cleanup, so in-flight requests are dropped rather than drained. Adding `case <-ctx.Done(): return ctx.Err()` fixes both.

</details>

5. ▢ Interleaving Lesson 18: a request times out after 2 seconds. Three goroutines it started are still running 30 seconds later. Is this a leak?

<details markdown="1"><summary>Check</summary>

Yes, in the sense that matters: work continues that nobody will use, holding memory and consuming CPU under load that is already failing.

They will eventually exit, so a goroutine profile taken once looks fine. Two profiles under sustained load will not: the count climbs with request rate and stays high. The cause is a goroutine that did not receive the request's context, or received `context.Background()` instead.

</details>

## Real-world reps

- [ ] Write the leaking `search` function, print `runtime.NumGoroutine()` before and after, and watch the number stay high. Then fix it with a buffer and watch it drop.
- [ ] Add `net/http/pprof` to a scratch service, leak a hundred goroutines deliberately, and read `?debug=2`. Learning to read that output when nothing is on fire is the point.
- [ ] Tomorrow: add `goleak.VerifyTestMain(m)` to one package you own and run its tests. Whatever it reports was already there.

## Going further

- [Never start a goroutine without knowing how it will stop, Dave Cheney](https://dave.cheney.net/2016/12/22/never-start-a-goroutine-without-knowing-how-it-will-stop)
- [Go 1.27 goroutine leak profile](https://go.dev/doc/go1.27)
- [`net/http/pprof`](https://pkg.go.dev/net/http/pprof)
- [`go.uber.org/goleak`](https://pkg.go.dev/go.uber.org/goleak)
- [Concurrency Patterns](../reference/concurrency-patterns.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
