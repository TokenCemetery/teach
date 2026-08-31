---
title: 9. Wrapping, Is and As
description: %w builds a chain, Is and As search it, and wrapping is an API commitment
type: lesson
---

# Lesson 9. Wrapping, Is and As

**Mission link:** An error that arrives at your log line with no context wastes an on-call hour. An error wrapped at every layer with no thought wastes the same hour differently. This is the difference.
**Primary source:** [Working with Errors in Go 1.13 — The Go Blog](https://go.dev/blog/go1.13-errors)
**Prerequisites:** [Lesson 8](0008-errors-are-values.md)

## Warm-up

1. ▢ What is the entire definition of the `error` interface?

<details markdown="1"><summary>Check</summary>

```go
type error interface{ Error() string }
```

One method. Everything else is built on top of it in ordinary Go.

</details>

2. ▢ Why are Go error strings written lowercase with no trailing period?

<details markdown="1"><summary>Check</summary>

Because they get embedded inside longer messages. `fmt.Errorf("load user: %w", err)` should read as one sentence, not as two half-capitalised ones.

</details>

## Know this

`%w` in `fmt.Errorf` produces an error that **wraps** another, keeping it retrievable:

```go
if err != nil {
    return fmt.Errorf("load user %s: %w", id, err)
}
```

The result's message is the concatenation, and the original is still reachable underneath. The mechanism is a method:

```go
func (e *wrapError) Unwrap() error { return e.err }
```

Anything implementing `Unwrap() error` participates. That is the whole protocol.

### `errors.Is` compares, `errors.As` extracts

```go
errors.Is(err, sql.ErrNoRows)     // is this specific error anywhere in the chain?

var verr *ValidationError
if errors.As(err, &verr) {        // is there an error of this type in the chain?
    log.Info("bad field", "field", verr.Field)
}
```

Both walk the chain by calling `Unwrap` repeatedly, so they find the target however many layers were added on the way up. Two things to keep straight:

- `errors.Is` is for **sentinel values**. Never use `err == ErrNotFound`, which breaks the moment anyone wraps it — and someone will.
- `errors.As` takes a **pointer to a variable of the target type**. `errors.As(err, &verr)` where `verr` is `*ValidationError`. Passing a non-pointer panics, which is deliberate: it is a programming error, not a runtime condition.

A type can also opt into `Is` or `As` by implementing them, which is how `os.ErrNotExist` matches errors from several different syscall layers.

### Joining

`errors.Join` (Go 1.20) combines several errors into one, and `errors.Is`/`As` search all branches:

```go
var errs error
for _, f := range files {
    if err := process(f); err != nil {
        errs = errors.Join(errs, fmt.Errorf("%s: %w", f, err))
    }
}
return errs   // nil if nothing was joined
```

`fmt.Errorf` also accepts multiple `%w` verbs since Go 1.20. Joined errors implement `Unwrap() []error` — the plural form — which is why you should never write chain-walking code by hand.

### When to wrap, and when not to

Wrapping is not free: **`%w` makes the wrapped error part of your API.** A caller can now match on it, and removing it later, or swapping the underlying library, is a breaking change nothing will catch. `%v` formats the message without exposing the value.

A workable rule:

| Situation | Verb |
|---|---|
| The caller may reasonably match on the cause — `ErrNotFound`, `context.DeadlineExceeded` | `%w` |
| The cause is an implementation detail — the driver, the JSON library, the file layout | `%v` |
| You are the top of the stack and about to log | neither; log it |

And wrap with **context the error does not already carry**. `fmt.Errorf("failed to open file: %w", err)` adds nothing — the wrapped error already says it failed to open a file. `fmt.Errorf("load config %s: %w", path, err)` adds the path and the operation, which is what the on-call engineer needs.

Wrap once per meaningful layer, not once per function. A message reading `handler: service: repository: query: exec: dial tcp: connection refused` is five layers agreeing that the database is down.

### Handle an error exactly once

Logging an error and returning it means it gets logged again by your caller, and again above that. Pick one:

- **Handle it** — recover, retry, substitute a default — and do not return it.
- **Return it**, wrapped with context, and say nothing.

Log only where the error stops, which in a service is the HTTP middleware or `main`.

## Practice

1. ▢ Rewrite this so the caller can still detect a not-found condition.

   ```go
   if err != nil {
       return fmt.Errorf("get user: %v", err)
   }
   ```

<details markdown="1"><summary>Check</summary>

```go
return fmt.Errorf("get user %s: %w", id, err)
```

`%v` flattens the error to a string, breaking the chain — `errors.Is(err, ErrNotFound)` above will return false. `%w` preserves it. Adding the id is the second half: context the wrapped error could not have.

</details>

2. ▢ Why is `err == ErrNotFound` a latent bug even when it works today?

<details markdown="1"><summary>Check</summary>

It compares the top of the chain only. The day any layer between the source and this check adds `fmt.Errorf("...: %w", err)`, the comparison silently becomes false and the not-found branch stops running.

`errors.Is(err, ErrNotFound)` walks the chain and keeps working. There is no case where `==` on errors is preferable, which is why linters flag it.

</details>

3. ▢ You want the `*ValidationError` out of a wrapped chain. Which call is right?

   - a) `errors.As(err, &verr)` with `verr` declared as `*ValidationError`
   - b) `errors.As(err, verr)` with `verr` declared as `*ValidationError`
   - c) `errors.Is(err, &verr)` with `verr` declared as `*ValidationError`
   - d) `errors.As(&err, verr)` with `verr` declared as `*ValidationError`

<details markdown="1"><summary>Check</summary>

**a)** `errors.As(err, &verr)` with `verr` declared as `*ValidationError`.

`As` needs somewhere to store what it finds, so the second argument is a pointer to your target variable — a `**ValidationError` here. Option b passes the value and panics. `Is` in option c compares rather than extracts. Option d takes the address of the wrong argument.

</details>

4. ▢ A repository wraps a `pq.Error` from its Postgres driver with `%w`. Name the risk.

<details markdown="1"><summary>Check</summary>

The driver's error type is now part of the repository's public API. Callers can — and will — write `errors.As(err, &pqErr)` and match on Postgres error codes, so switching to another driver or another database becomes a breaking change with no compile error to warn you.

The alternative is to translate at the boundary: match the driver error inside the repository and return your own `ErrDuplicateKey`. That is what the boundary is for, and it costs one small type.

</details>

5. ▢ Interleaving Lesson 8: a handler logs `err` and then returns it to its caller, which also logs it. What is the rule being broken?

<details markdown="1"><summary>Check</summary>

Handle an error once. Logging is handling; returning is delegating. Doing both produces duplicate lines that look like two failures and make the real count of incidents unknowable.

Return the error with context, and log at the single place where the error stops travelling — the top-level middleware or `main`.

</details>

## Real-world reps

- [ ] Build a three-layer chain — repository, service, handler — each wrapping with `%w`. Print the final message, then assert `errors.Is` finds the sentinel from the bottom layer.
- [ ] Change one layer's `%w` to `%v` and watch the `errors.Is` assertion fail. That failure is the shape of the bug in production.
- [ ] Tomorrow: pick one error path in a service you operate and read what it would print at the top. Ask whether it names the operation and the identifier, or only the failure.

## Going further

- [Working with Errors in Go 1.13 — The Go Blog](https://go.dev/blog/go1.13-errors)
- [`errors` package](https://pkg.go.dev/errors) — `Is`, `As`, `Join`, `Unwrap`
- [Don't just check errors, handle them gracefully — Dave Cheney](https://dave.cheney.net/2016/04/27/dont-just-check-errors-handle-them-gracefully)
- [Error Handling](../reference/error-handling.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
