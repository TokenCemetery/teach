---
title: Concurrency Patterns
description: Channel rules, select shapes, context constructors and the leak checklist
type: reference
---

# Concurrency Patterns

Lookup sheet for lessons [15](../lessons/0015-goroutines-and-what-they-cost.md) through [21](../lessons/0021-goroutine-leaks.md), plus [25](../lessons/0025-graceful-shutdown.md).

## Channel operation table

| Operation | Open | Closed | Nil |
|---|---|---|---|
| send | blocks until received | **panic** | blocks forever |
| receive | blocks until sent | zero value, `ok == false` | blocks forever |
| close | ok | **panic** | **panic** |

**Only the sender closes**, and only when there is one sender. With several, a `WaitGroup` counts them and one goroutine closes after `Wait`.

Unbuffered = rendezvous, both sides synchronise. Buffered = decoupled, capacity must have a stated reason.

## select

- Several cases ready → one chosen **uniformly at random**. Order is not priority.
- `default` makes it non-blocking.
- A nil channel is never ready, so assign nil to disable a case.
- A **closed** channel is always ready. A `continue` on it spins the CPU.
- `select {}` blocks forever.

```go
for {
    select {
    case <-ctx.Done():
        return ctx.Err()
    case job := <-jobs:
        process(job)
    }
}
```

## context

| Constructor | Cancelled by |
|---|---|
| `WithCancel(parent)` | `cancel()`, or parent |
| `WithTimeout(parent, d)` | `d` elapsing, `cancel()`, or parent |
| `WithDeadline(parent, t)` | `t` passing, `cancel()`, or parent |
| `WithValue(parent, k, v)` | never, carries a value only |
| `WithoutCancel(parent)` | never, keeps values and drops cancellation |
| `WithCancelCause(parent)` | `cancel(err)`; read back with `context.Cause(ctx)` |

Rules: first parameter, named `ctx`. Always `defer cancel()`. Never nil: use `Background()` or `TODO()`. Do not store in a struct. Values are request-scoped metadata, never dependencies. Keys are an unexported type.

**Cancellation is cooperative.** A CPU-bound loop must check `ctx.Err()` itself.

## Choosing a primitive

| Situation | Use |
|---|---|
| transfer ownership of a value | channel |
| coordinate timing between goroutines | unbuffered channel |
| protect state that stays put | `sync.Mutex` |
| one counter or flag | `atomic.Int64`, `atomic.Bool` |
| run once, ever | `sync.Once` |
| wait for N goroutines | `sync.WaitGroup` (`wg.Go` from Go 1.25) |
| fan out, collect first error, cancel the rest | `errgroup.WithContext` |
| bound fan-out | `errgroup.SetLimit(n)` or a worker pool |

Mutex rules: `defer mu.Unlock()` immediately after `Lock`. Never hold across I/O. Not reentrant. `RWMutex` only pays for long, read-heavy critical sections, so measure.

## errgroup

```go
g, ctx := errgroup.WithContext(ctx)
g.SetLimit(8)
for _, id := range ids {
    g.Go(func() error { return fetch(ctx, id) })
}
if err := g.Wait(); err != nil { ... }
```

## Data races

Race = two goroutines, same memory, ≥1 write, no happens-before edge.
A race is **undefined behaviour**, not "one value or the other".

Happens-before edges you can rely on:

- send → corresponding receive completes
- close → a receive that returns because it is closed
- `Unlock` → a subsequent `Lock` returning
- `wg.Done` reaching zero → `Wait` returning
- `once.Do(f)` returning → every other `Do` returning
- an atomic write → a subsequent atomic read

```bash
go test -race ./...      # no false positives; only sees what ran
```

`testing/synctest` (Go 1.25) virtualises time so concurrent tests are deterministic.

## Leak checklist

Ask of every `go` statement: **what stops it?**

| Shape | Fix |
|---|---|
| send with no receiver (early return above) | buffer to `len(items)`, or `select` with `ctx.Done()` |
| receive with no sender | ensure the producer always sends or closes |
| loop with no cancellation case | add `case <-ctx.Done()` |
| `time.NewTicker` still referenced | `defer ticker.Stop()` |
| goroutine given `context.Background()` | pass the request's context |

```bash
curl 'localhost:6060/debug/pprof/goroutine?debug=2'   # every stack, with block duration
curl 'localhost:6060/debug/pprof/goroutineleak'       # Go 1.27: only unblockable ones
```

`go.uber.org/goleak` fails tests that finish with extra goroutines.

## Graceful shutdown order

1. `signal.NotifyContext(ctx, os.Interrupt, syscall.SIGTERM)`
2. Fail readiness, wait a few seconds for the load balancer
3. `srv.Shutdown(freshCtx)`, **never the cancelled context**
4. Wait for workers (`g.Wait()`)
5. Close dependencies in reverse construction order
6. Exit anyway at the deadline, shorter than the platform's grace period

`ListenAndServe` returns `http.ErrServerClosed` on a clean shutdown. Treat it as success.
