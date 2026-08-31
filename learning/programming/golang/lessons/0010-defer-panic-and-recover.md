---
title: 10. defer, panic and recover
description: Arguments freeze at the defer statement, and panic is for bugs rather than for failures
type: lesson
---

# Lesson 10. defer, panic and recover

**Mission link:** `defer` is how a Go service releases what it acquired, and its two surprises — argument evaluation and loop accumulation — leak resources quietly under load.
**Primary source:** [Defer, Panic, and Recover — The Go Blog](https://go.dev/blog/defer-panic-and-recover)
**Prerequisites:** [Lesson 8](0008-errors-are-values.md)

## Warm-up

1. ▢ What breaks if a middle layer changes `%w` to `%v` when wrapping?

<details markdown="1"><summary>Check</summary>

The chain is cut, so `errors.Is` and `errors.As` above that point stop finding anything below it. The message still looks right, which is what makes it hard to spot.

</details>

2. ▢ When should you *not* wrap with `%w`?

<details markdown="1"><summary>Check</summary>

When the wrapped error is an implementation detail you do not want callers matching on — a driver error, a JSON parse failure. `%w` makes it API; `%v` keeps the message and drops the commitment.

</details>

## Know this

`defer` schedules a call to run when the surrounding **function** returns — normally or through a panic.

```go
f, err := os.Open(name)
if err != nil {
    return err
}
defer f.Close()
```

Acquire, check, defer the release, immediately. That order matters: deferring before the error check would call `Close` on a nil file.

Three rules carry all the surprise.

**Deferred calls run last-in, first-out.** Three defers unwind in reverse, which is what you want for nested acquisition.

**Arguments are evaluated when `defer` executes, not when the call runs.**

```go
i := 0
defer fmt.Println(i)   // prints 0
i = 42
```

The value `0` was captured at the `defer` line. To see the final value, defer a closure — `defer func() { fmt.Println(i) }()` — which captures the variable rather than its value.

**A deferred closure can modify named results.** This is the idiomatic way to add context to every error path at once:

```go
func load(path string) (err error) {
    defer func() {
        if err != nil {
            err = fmt.Errorf("load %s: %w", path, err)
        }
    }()
    ...
}
```

It only works with a *named* result, because the closure needs a variable to assign to.

### The loop trap

`defer` is scoped to the function, not the block:

```go
for _, name := range names {
    f, err := os.Open(name)
    if err != nil {
        return err
    }
    defer f.Close()   // 10,000 open files before any of them close
}
```

Every iteration adds a deferred call that waits for the whole function. Over a large input this exhausts file descriptors. Move the body into its own function — a small named one, or a closure called immediately — so each iteration has a function to return from.

### `Close` on a writer is not a free call

`defer f.Close()` discards the error. For a reader that is fine. For a **writer** the final flush happens in `Close`, so discarding it can lose the tail of the file and report success:

```go
defer func() {
    if cerr := f.Close(); cerr != nil && err == nil {
        err = cerr
    }
}()
```

### panic is for bugs

`panic` unwinds the stack, running deferred functions as it goes, and if nothing stops it the program exits with a stack trace. Use it for conditions that mean the program is wrong: an impossible switch branch, a required template that failed to compile at startup, an invariant a caller violated.

Do not use it for expected failures. A missing file, a rejected input and a timed-out request are all errors, and the whole of Lesson 8 is about why.

`recover` stops a panic, and only inside a **directly deferred** function:

```go
func safe() (err error) {
    defer func() {
        if r := recover(); r != nil {
            err = fmt.Errorf("recovered: %v", r)
        }
    }()
    return risky()
}
```

Two hard limits worth knowing before you rely on it:

- **A panic in a goroutine cannot be recovered from another goroutine.** Every goroutine you start needs its own recovery if a panic there must not kill the process. The stack does not connect them.
- **A fatal error is not a panic.** `concurrent map writes` and `all goroutines are asleep - deadlock!` bypass `recover` entirely and end the process, as Lesson 4 showed.

Recovery belongs at boundaries where one unit of work should not take the process down: an HTTP middleware, a worker loop, a plugin call. `net/http` already recovers panics in handlers, logs the stack, and closes the connection — so your own middleware is about turning that into a 500 and a structured log line, not about survival.

## Practice

1. ▢ Predict the output.

   ```go
   func f() {
       for i := range 3 {
           defer fmt.Print(i, " ")
       }
   }
   ```

<details markdown="1"><summary>Check</summary>

`2 1 0 ` — last-in, first-out, and each `i` was captured by value at its `defer` line.

Note that this is correct in Go 1.22 and later for a different reason than people expect: even though loop variables are now per-iteration, the argument was already evaluated eagerly, so the behaviour here never depended on that change.

</details>

2. ▢ What is wrong with this, and what is the smallest fix?

   ```go
   for _, name := range names {
       f, err := os.Open(name)
       if err != nil {
           return err
       }
       defer f.Close()
       process(f)
   }
   ```

<details markdown="1"><summary>Check</summary>

Nothing closes until the whole function returns, so a long list exhausts the file-descriptor limit.

The smallest fix is to give each iteration its own function:

```go
for _, name := range names {
    if err := func() error {
        f, err := os.Open(name)
        if err != nil {
            return err
        }
        defer f.Close()
        return process(f)
    }(); err != nil {
        return err
    }
}
```

A named helper is usually clearer than the inline closure. Either way, the point is that `defer` needs a function boundary to fire at.

</details>

3. ▢ Which use of `panic` is defensible?

   - a) A user submitted a form with an invalid email
   - b) A database connection was refused during a request
   - c) A template required at startup failed to parse
   - d) An upstream service returned a 503 response

<details markdown="1"><summary>Check</summary>

**c)** A template required at startup failed to parse.

It is a programming error, discovered before serving traffic, with no sensible way to continue — which is why `template.Must` exists and panics by design. The other three are ordinary runtime failures that a caller can act on, and each should be an error.

</details>

4. ▢ A worker goroutine panics. Your `main` has a deferred `recover`. What happens?

<details markdown="1"><summary>Check</summary>

The process exits. `recover` only works within the goroutine that panicked, and `main`'s deferred function is on a different stack entirely.

Each long-lived goroutine needs its own deferred recovery if a panic there must not be fatal. In practice this means wrapping the goroutine body in a small helper that recovers and logs, rather than calling `go doWork()` directly.

</details>

5. ▢ Interleaving Lesson 2: why does the named-result trick require `(err error)` rather than a bare `error`?

<details markdown="1"><summary>Check</summary>

The deferred closure has to assign to something. With an unnamed result there is no variable in scope to assign to — the value was already handed back — so the closure can only read its own copies.

Naming the result gives the closure a variable that is still live during unwinding, and assigning to it changes what the function actually returns. It is the one place where naming results earns its keep; elsewhere it mostly hurts readability.

</details>

## Real-world reps

- [ ] Run the LIFO example and the eager-argument example. Then change the second to a closure and watch the printed value change.
- [ ] Write a function that opens 5,000 files in a loop with `defer f.Close()` inside it, and run it. Note the exact error you get when the descriptor limit is hit — you will recognise it in a log one day.
- [ ] Tomorrow: add a recovering wrapper for one goroutine in code you own. Make it log the stack with `debug.Stack()`, not just the panic value.

## Going further

- [Defer, Panic, and Recover — The Go Blog](https://go.dev/blog/defer-panic-and-recover)
- [Go Code Review Comments — don't panic](https://go.dev/wiki/CodeReviewComments#dont-panic)
- [`runtime/debug.Stack`](https://pkg.go.dev/runtime/debug#Stack)
- [Error Handling](../reference/error-handling.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
