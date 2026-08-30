---
title: 25 — Graceful Shutdown and Health
description: Catch the signal, stop accepting, drain in-flight work, then close dependencies in order
type: lesson
---

# Lesson 25 — Graceful Shutdown and Health

**Mission link:** A deploy restarts every instance. If shutdown drops in-flight requests, every deploy is a small outage — and this is the code that decides.
**Primary source:** [`http.Server.Shutdown`](https://pkg.go.dev/net/http#Server.Shutdown)
**Prerequisites:** [Lesson 23](0023-configuration-and-startup.md), [Lesson 19](0019-sync-primitives.md)

## Warm-up

1. ▢ What lets you raise log verbosity on a running process without restarting it?

<details markdown="1"><summary>Check</summary>

A `slog.LevelVar` passed to the handler, changed through an admin endpoint. The level is read per record.

</details>

2. ▢ Where does a long-lived worker learn that it should stop?

<details markdown="1"><summary>Check</summary>

From `case <-ctx.Done()` in its `select`. Cancellation is cooperative — a goroutine that never checks never stops.

</details>

## Know this

Shutdown has an order, and getting it wrong loses work:

1. **Receive the signal.** SIGTERM from the orchestrator, SIGINT from a terminal.
2. **Fail the readiness probe** so the load balancer stops sending new requests, and wait long enough for it to notice.
3. **Stop accepting connections**, while letting in-flight requests finish.
4. **Wait for background workers** to finish their current unit of work.
5. **Close dependencies** — database, queues, flush the logger — in reverse order of construction.
6. **Give up after a deadline** and exit anyway.

Step 6 is not optional. Something will eventually hang, and a process that refuses to die is worse than one that drops a request.

### Signals

```go
ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
defer stop()
```

`signal.NotifyContext` cancels the context on the first matching signal, which turns the whole of Lesson 18 into your shutdown mechanism: everything already taking this context already knows how to stop. A second signal is the operator saying they are done waiting — after `stop()`, the default behaviour returns and the next SIGINT kills the process.

### Draining the server

```go
srvErr := make(chan error, 1)
go func() { srvErr <- srv.ListenAndServe() }()

select {
case err := <-srvErr:
    return err                       // failed to start, or crashed
case <-ctx.Done():                   // signal received
}

shutdownCtx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
defer cancel()
if err := srv.Shutdown(shutdownCtx); err != nil {
    return fmt.Errorf("shutdown: %w", err)
}
```

`Shutdown` closes listeners, waits for idle keep-alive connections to close, and waits for active requests to complete. It returns when everything is done or when its context expires — which is why that context must **not** be the cancelled one. Deriving the shutdown timeout from a context that is already cancelled aborts instantly and drops every in-flight request. It is the most common bug in this code.

`ListenAndServe` returns `http.ErrServerClosed` on a clean shutdown, so treat that value as success rather than as an error.

The shutdown timeout should be shorter than the orchestrator's grace period. Kubernetes sends SIGTERM, waits `terminationGracePeriodSeconds` (30 by default), then SIGKILL. A 60-second shutdown timeout inside a 30-second grace period is a longer way of writing SIGKILL.

### Workers and dependencies

Run the server and the workers under one `errgroup` so any of them failing brings the rest down:

```go
g, gctx := errgroup.WithContext(ctx)
g.Go(func() error { return worker.Run(gctx) })
g.Go(func() error { return serve(gctx, srv) })
if err := g.Wait(); err != nil { ... }
```

Then close dependencies after `g.Wait()` returns, in reverse construction order — the database last, because a draining request may still need it. `defer db.Close()` in `run` gets this right for free, since defers unwind in reverse.

### Liveness and readiness are different questions

| Probe | Asks | Failing it means |
|---|---|---|
| Liveness | is this process wedged? | restart me |
| Readiness | should I get traffic right now? | take me out of rotation |

Getting these backwards is a classic outage: a readiness check that pings the database, wired up as liveness, restarts every instance when the database has a brief hiccup — turning a recoverable dependency blip into a full outage with a cold cache.

**Liveness should check almost nothing.** Return 200 if the process can serve. **Readiness may check dependencies** the service cannot work without, and must return failure as soon as shutdown begins, before the listener closes.

```go
mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(http.StatusOK)                  // liveness: am I alive
})
mux.HandleFunc("GET /readyz", func(w http.ResponseWriter, r *http.Request) {
    if shuttingDown.Load() || db.PingContext(r.Context()) != nil {
        w.WriteHeader(http.StatusServiceUnavailable)
        return
    }
    w.WriteHeader(http.StatusOK)
})
```

The gap between failing readiness and closing the listener matters. Load balancers notice on their own schedule, so sleeping a few seconds there — before calling `Shutdown` — is what actually prevents dropped requests during a deploy.

## Practice

1. ▢ What is wrong with `srv.Shutdown(ctx)` where `ctx` is the one cancelled by the signal?

<details markdown="1"><summary>Check</summary>

It is already cancelled, so `Shutdown` returns immediately and every in-flight request is dropped. The code looks like a graceful shutdown and behaves like an abrupt one.

Use a fresh context with its own timeout: `context.WithTimeout(context.Background(), 20*time.Second)`.

</details>

2. ▢ Why fail readiness *before* closing the listener, rather than at the same time?

<details markdown="1"><summary>Check</summary>

Because the load balancer learns about readiness on a polling interval, not instantly. Closing the listener the moment you go unready means requests already in flight toward you arrive at a closed port and fail.

Fail readiness, wait a few seconds — long enough for a poll or two — then stop accepting. That sleep is doing real work, however wrong it looks.

</details>

3. ▢ Which check belongs in the liveness probe?

   - a) That the database responds to a ping
   - b) That the process can serve a response
   - c) That the message queue has capacity
   - d) That the cache has been warmed up

<details markdown="1"><summary>Check</summary>

**b)** That the process can serve a response.

Liveness failing means "restart me", and restarting does not fix someone else's database, queue or cache. Putting a dependency check there converts a downstream blip into a restart storm across every instance at once — with cold caches and a thundering reconnect.

</details>

4. ▢ Your shutdown timeout is 60 seconds and Kubernetes' grace period is 30. What happens?

<details markdown="1"><summary>Check</summary>

At 30 seconds the process is SIGKILLed, mid-drain. Nothing after that point runs: no deferred close, no flush, no final log line.

The shutdown budget has to fit inside the platform's grace period with room to spare, or the graceful path is decoration. Both numbers belong in the same review.

</details>

5. ▢ Interleaving Lesson 21: shutdown hangs until the timeout and the process is killed. Where do you look?

<details markdown="1"><summary>Check</summary>

A goroutine that never observed the cancellation — a worker whose `select` has no `ctx.Done()` case, or one blocked on a channel send nobody will receive.

The goroutine profile at the moment of the hang names it. This is the concrete cost of Lesson 21's leaks: they are invisible in steady state and they are exactly what turns a clean deploy into a 30-second stall and dropped requests.

</details>

## Real-world reps

- [ ] Build the full shutdown path: `signal.NotifyContext`, a goroutine running `ListenAndServe`, a fresh-context `Shutdown`. Start a slow request, press ctrl-c, and confirm the request completes.
- [ ] Break it deliberately by passing the cancelled context to `Shutdown`, and watch the same request get dropped. The difference is one argument.
- [ ] Tomorrow: check the shutdown timeout and the grace period for a service you operate. If nobody knows one of the two numbers, that is the finding.

## Going further

- [`http.Server.Shutdown`](https://pkg.go.dev/net/http#Server.Shutdown)
- [`signal.NotifyContext`](https://pkg.go.dev/os/signal#NotifyContext)
- [`errgroup`](https://pkg.go.dev/golang.org/x/sync/errgroup)
- [Concurrency Patterns](../reference/concurrency-patterns.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top — this lesson compresses it, and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
