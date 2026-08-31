---
title: 18. context and Cancellation
description: One value that carries a deadline and a stop signal down every call it touches
type: lesson
---

# Lesson 18. context and Cancellation

**Mission link:** Cancellation that propagates is the difference between a service that sheds load and one that piles up goroutines until it dies. Nothing in Java or Promise-land transfers cleanly.
**Primary source:** [Go Concurrency Patterns: Context — The Go Blog](https://go.dev/blog/context)
**Prerequisites:** [Lesson 17](0017-select-and-timeouts.md)

## Warm-up

1. ▢ Two `select` cases are ready. Which one runs?

<details markdown="1"><summary>Check</summary>

One chosen uniformly at random. Case order carries no priority.

</details>

2. ▢ What does a `default` case do to a `select`?

<details markdown="1"><summary>Check</summary>

Makes it non-blocking: it takes a ready case if there is one, otherwise `default`. It never waits.

</details>

## Know this

`context.Context` is a value carrying three things down a call tree: a **cancellation signal**, a **deadline**, and **request-scoped values**. Its interface is four methods, and the one that matters is:

```go
func (c Context) Done() <-chan struct{}
```

A channel that is **closed** when the work should stop. Closing broadcasts to every receiver at once — the property from Lesson 16 — which is what makes one cancel reach a hundred goroutines.

### The tree

Contexts derive from one another, forming a tree. Cancelling a node cancels its whole subtree, never its parent:

```go
ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
defer cancel()

rows, err := db.QueryContext(ctx, q)   // the query observes the same deadline
```

| Constructor | Cancels when |
|---|---|
| `WithCancel(parent)` | you call `cancel`, or the parent is cancelled |
| `WithTimeout(parent, d)` | after `d`, or you call `cancel`, or the parent is cancelled |
| `WithDeadline(parent, t)` | at `t`, or you call `cancel`, or the parent is cancelled |
| `WithValue(parent, k, v)` | never — it only carries a value |

**Always call `cancel`.** `defer cancel()` immediately after the constructor is not optional politeness: until cancel runs, the child stays attached to the parent and the timer stays live. `go vet`'s `lostcancel` check reports the ones it can see.

`ctx.Err()` says why it stopped — `context.Canceled` or `context.DeadlineExceeded` — and both are matchable with `errors.Is` through any amount of wrapping.

### The conventions

- **First parameter, named `ctx`, typed `context.Context`.** `func Get(ctx context.Context, id string) (*User, error)`. It goes first in every function that takes one.
- **Do not store it in a struct.** A context describes one operation's lifetime; a struct outlives the operation. The narrow exception is a type whose whole purpose is one request, and it is rarer than people assume.
- **Never pass nil.** Use `context.Background()` at the top of `main` and in tests, and `context.TODO()` to mark a call site you have not wired up yet.
- **Values are for request-scoped metadata, not for dependencies.** A request id, a trace span, an authenticated subject. Not your database handle, your logger's configuration, or an optional argument — those go in parameters or struct fields, where the compiler can see them.
- **Keys must be an unexported type.** `type ctxKey struct{}` avoids collisions with other packages using the same string.

### Cancellation is cooperative

Nothing is interrupted. A context being cancelled changes exactly one thing: a channel closes. Code that never checks keeps running to completion.

So every blocking operation needs a context-aware form, and the standard library provides them: `db.QueryContext`, `http.NewRequestWithContext`, `net.Dialer.DialContext`. A loop that computes rather than blocks has to check for itself:

```go
for _, item := range items {
    if err := ctx.Err(); err != nil {
        return err
    }
    process(item)
}
```

This is where the Java instinct misleads. `Thread.interrupt` sets a flag the runtime honours at defined interruption points, and `Future.cancel(true)` acts on the task from the outside. A Go context has no reach into a running goroutine at all — cancellation propagates only as far as your code chooses to look.

### Worth knowing

`context.WithCancelCause` (Go 1.20) attaches a reason, retrieved with `context.Cause(ctx)`, so a timeout can say *which* timeout. `context.WithoutCancel` (Go 1.21) derives a context that keeps the values but drops the cancellation — for the audit write that must finish after the request is abandoned. `context.AfterFunc` (Go 1.21) registers a callback to run on cancellation, which is how you attach cleanup without a goroutine parked in a `select`.

## Practice

1. ▢ What is wrong with this?

   ```go
   ctx, _ := context.WithTimeout(context.Background(), time.Second)
   rows, err := db.QueryContext(ctx, q)
   ```

<details markdown="1"><summary>Check</summary>

The cancel function is discarded, so the context stays attached to its parent and its timer stays live until the deadline passes. In a per-request path that accumulates — a leak that grows with traffic and disappears when traffic stops, which makes it hard to reproduce.

Write `ctx, cancel := ...` followed by `defer cancel()`. `go vet` reports this one as `lostcancel`.

</details>

2. ▢ A handler's context is cancelled when the client disconnects. Your handler is halfway through a 30-second CPU-bound loop. What happens?

<details markdown="1"><summary>Check</summary>

The loop runs to completion. Cancellation closes a channel; it does not interrupt anything.

To respond to it, the loop has to check `ctx.Err()` — or `ctx.Done()` in a `select` — at a granularity that makes sense for the work. This is the single most important difference from `Thread.interrupt`, which the runtime honours at defined points without the author writing anything.

</details>

3. ▢ Which belongs in a `context.Value`?

   - a) The database handle the request will query
   - b) The trace id assigned to this request
   - c) The retry count configured for this service
   - d) The logger the handler should write to

<details markdown="1"><summary>Check</summary>

**b)** The trace id assigned to this request.

It is metadata about this one operation, it crosses layers that do not care about it, and no signature needs to mention it. The other three are dependencies or configuration: they belong in parameters or struct fields, where the compiler checks them and a reader can see them.

The rule of thumb — if leaving it out would be a compile error in a well-designed API, it does not belong in a context.

</details>

4. ▢ A request times out after 2 seconds, but the goroutine it started keeps running for 30. Where is the bug?

<details markdown="1"><summary>Check</summary>

The goroutine was not given the context, or was given one derived from `context.Background()` instead of the request's.

Both break the tree, so cancellation stops at the boundary. Detaching is sometimes deliberate — work that must outlive the request — and then the right tool is `context.WithoutCancel(ctx)`, which says so explicitly and keeps the values.

</details>

5. ▢ Interleaving Lesson 9: `db.QueryContext` returns an error after a timeout. How do you detect that it was the deadline?

<details markdown="1"><summary>Check</summary>

`errors.Is(err, context.DeadlineExceeded)`. Drivers wrap it, so `==` fails and `errors.Is` walks the chain.

Distinguishing it matters operationally: a deadline means you gave up, and a `context.Canceled` usually means the client did. Those are different pages in a runbook, and the same 500 in a log if you do not separate them.

</details>

## Real-world reps

- [ ] Write a handler that does a 5-second sleep in a loop, checking `ctx.Err()` each second. Curl it and press ctrl-c mid-request. Watch it stop.
- [ ] Remove the `ctx.Err()` check and repeat. The handler now runs to completion after the client has gone — that is the shape of a service that cannot shed load.
- [ ] Tomorrow: find a `go someWork()` in a codebase you work with and check which context it receives. If it is `context.Background()`, ask whether that was a decision.

## Going further

- [Go Concurrency Patterns: Context — The Go Blog](https://go.dev/blog/context)
- [`context` package](https://pkg.go.dev/context) — read the package doc in full; it is short and it is the specification
- [Contexts and structs — The Go Blog](https://go.dev/blog/context-and-structs) — why it is a parameter and not a field
- [Concurrency Patterns](../reference/concurrency-patterns.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
