---
title: Review Checklist
description: What the tools catch, what a human must catch, and how to phrase the comment
type: reference
---

# Review Checklist

Lookup sheet for [Lesson 36](../lessons/0036-reviewing-go.md). Run the tools first; spend attention on what they cannot see.

## Before a human looks

```bash
gofmt -l .
go vet ./...
go test -race ./...
staticcheck ./...      # or golangci-lint
govulncheck ./...
```

If a comment could have been made by a tool, a tool should have made it.

## Order to look in

### 1. API surface

- [ ] Is anything exported that could stay unexported?
- [ ] Are interfaces declared in the **consumer**, with only the methods it uses?
- [ ] Does the package return concrete types and accept interfaces?
- [ ] Are the matchable errors documented? Anything documented is now API.
- [ ] Does the doc comment start with the identifier's name?
- [ ] Does anything stutter, as in `store.NewStore` or `http.HTTPServer`?

### 2. Error paths

- [ ] Every error handled **or** returned, never both.
- [ ] `%w` where a caller may match; `%v` where the cause is an implementation detail.
- [ ] No `_` discarding an error without a reason.
- [ ] No function returns a **concrete** error type.
- [ ] Third-party errors translated at the boundary.
- [ ] No `return nil, nil` where the caller will dereference.

### 3. Lifecycle

- [ ] Every `go` statement: what stops it, who waits, where does its error go?
- [ ] Every long-lived loop has `case <-ctx.Done()`.
- [ ] Every `WithCancel`/`WithTimeout` has `defer cancel()`.
- [ ] `defer` for release comes immediately after acquire, and is **not inside a loop**.
- [ ] `Close` on a writer has its error checked.
- [ ] `Shutdown` gets a **fresh** context, not the cancelled one.

### 4. Shared state

- [ ] What is reachable from more than one goroutine, and what guards it?
- [ ] No lock held across I/O.
- [ ] No map shared without synchronisation.
- [ ] No method locks and then calls another method that locks.
- [ ] Nothing containing a mutex is copied: value receivers, struct assignment, range copies.

### 5. Boundaries

- [ ] Import arrows point one way; domain imports neither transport nor storage.
- [ ] No business rules in the transport layer.
- [ ] `internal/` used for anything without an external caller.

### 6. Tests

- [ ] Failure paths covered, not only the happy one.
- [ ] Table-driven where there are more than two cases.
- [ ] Would the test fail if the logic were wrong, or only if it panicked?
- [ ] Concurrent code exercised under `-race`.

## Wrong code that compiles cleanly

The list a reviewer has to carry, because nothing else will catch it:

| Look for | Why it is wrong | Lesson |
|---|---|---|
| value receiver on a type with a mutex or a mutating method | operates on a copy; silent no-op | [6](../lessons/0006-methods-and-method-sets.md) |
| sub-slice returned with spare capacity | caller's `append` overwrites your data | [3](../lessons/0003-slices-and-the-backing-array.md) |
| concrete error type in a return position | non-nil interface on the success path | [12](../lessons/0012-the-nil-interface-trap.md) |
| `defer` inside a loop | resources accumulate until the function returns | [10](../lessons/0010-defer-panic-and-recover.md) |
| goroutine with no cancellation case | leak; blocks shutdown | [21](../lessons/0021-goroutine-leaks.md) |
| interface declared beside its one implementation | abstracts nothing, doubles maintenance | [11](../lessons/0011-implicit-interfaces.md) |
| missing `rows.Err()` after the loop | a mid-iteration failure looks like a short result | [26](../lessons/0026-talking-to-a-database.md) |
| missing `defer rows.Close()` | drains the connection pool | [26](../lessons/0026-talking-to-a-database.md) |
| `err == ErrNotFound` | breaks the day anyone wraps it | [9](../lessons/0009-wrapping-is-and-as.md) |
| method added to an exported interface | breaks every implementer you do not control | [34](../lessons/0034-api-design-and-compatibility.md) |
| `http.ListenAndServe` in production | no timeouts at all | [22](../lessons/0022-an-http-server.md) |
| unbounded `go` per item from a request | denial of service the caller triggers | [15](../lessons/0015-goroutines-and-what-they-cost.md) |

## Phrasing

Name the **consequence** and the **mechanism**, then offer the alternative.

| Instead of | Say |
|---|---|
| "bad naming" | "`store.NewStore` stutters at the call site; `store.New` reads better" |
| "use a pointer" | "value receiver copies the mutex; `go vet` flags this as `copylocks`" |
| "too many methods" | "the only consumer uses two, so a two-method interface there would do" |
| "might leak" | "if the caller returns early these sends block forever, so buffer it or add `ctx.Done()`" |
| "wrap the error" | "`%v` here breaks `errors.Is` for `ErrNotFound` two layers up" |
| "not idiomatic" | link the specific rule in [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments) |

## Before adding a goroutine

1. What stops it?
2. Who waits for it, and what happens to its error?
3. What does it share, and what protects that?
4. Is there a measurement showing concurrency is faster here?
5. Would the sequential version be simpler to read?

Four weak answers out of five means the answer is a loop.
