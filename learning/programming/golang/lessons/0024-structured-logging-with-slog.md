---
title: 24 — Structured Logging with slog
description: Key-value attributes, one logger passed as a dependency, and levels you can change without a deploy
type: lesson
---

# Lesson 24 — Structured Logging with slog

**Mission link:** Logs are the first thing you reach for at 3am and the last thing anyone designs. Structured output is what makes a log searchable instead of grep-able.
**Primary source:** [Structured Logging with slog — The Go Blog](https://go.dev/blog/slog)
**Prerequisites:** [Lesson 23](0023-configuration-and-startup.md)

## Warm-up

1. ▢ Why does `run(ctx, args, stdout) error` beat calling `os.Exit` deeper in the program?

<details markdown="1"><summary>Check</summary>

`os.Exit` skips deferred functions, so cleanup never runs. Returning an error keeps `os.Exit` confined to `main` and makes startup testable.

</details>

2. ▢ Which startup checks should be fatal?

<details markdown="1"><summary>Check</summary>

The ones about things you control — configuration parsing, credentials, files, templates. A downstream service being unavailable belongs in a readiness probe, not a boot assertion.

</details>

## Know this

`log/slog` arrived in Go 1.21 and is the standard answer for structured logging. A log record is a message plus **attributes**:

```go
slog.Info("request handled", "method", r.Method, "status", 200, "duration", d)
```

The output is machine-parseable rather than a sentence to be regex'd:

```json
{"time":"...","level":"INFO","msg":"request handled","method":"GET","status":200,"duration":"1.2ms"}
```

The point is that `status` is a field. You can filter, aggregate, and alert on it without writing a parser that breaks when someone edits the message.

### Handlers decide the format

```go
h := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
})
logger := slog.New(h)
```

`slog.NewTextHandler` gives `key=value` for local development; `slog.NewJSONHandler` gives JSON for anything that ships logs somewhere. The choice belongs in `run`, driven by a flag, so a developer gets readable output and production gets parseable output from the same binary.

`slog.SetDefault(logger)` makes the package-level `slog.Info` use it — convenient, and still global state. Pass the `*slog.Logger` explicitly to the types that log; set the default as well so that libraries logging through the package functions land in the same stream.

### Attributes, and the two ways to write them

The alternating form is convenient. The typed form is faster and harder to get wrong:

```go
slog.Info("saved", "id", id, "bytes", n)                        // convenient
slog.LogAttrs(ctx, slog.LevelInfo, "saved",
    slog.String("id", id), slog.Int("bytes", n))                // explicit, no boxing
```

A mismatched key-value pair — an odd number of arguments, or a non-string key — produces a broken record rather than a compile error. Since Go 1.22 `go vet` reports these, which is the main reason to keep `vet` in CI.

Use `With` to bind attributes once instead of repeating them:

```go
log := logger.With("component", "store")
log.Info("query", "rows", n)   // component is included
```

In a request path, bind the request id once in middleware and pass the logger — or the context — down. The `Context` variants (`InfoContext`, `LogAttrs`) exist so a custom handler can pull the trace id out of the context and attach it to every record automatically. That is the cleanest way to get correlation without threading an argument through every function.

### Levels you can change at runtime

```go
var lvl slog.LevelVar          // defaults to Info
lvl.Set(slog.LevelDebug)       // safe to call from a handler, at any time

h := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: &lvl})
```

A `LevelVar` behind an admin endpoint lets you turn on debug logging for five minutes on a running process. Without it, debugging a production-only problem needs a deploy — and the problem usually stops reproducing.

### What to log

- **Error once**, where it stops travelling — the rule from Lesson 9. A logged-and-returned error is logged again by every layer above.
- **Attributes, not sentences.** `slog.Info("upload failed", "err", err, "user", id)` beats `slog.Info(fmt.Sprintf("upload failed for %s: %v", id, err))`, because the second is only searchable as text.
- **No secrets, no personal data you would not put in a database.** Logs are copied to more places than any other output, and redaction after the fact does not work. A type with a `LogValue() slog.Value` method controls its own representation, which is the right hook for wrapping a token or a card number.
- **Not in a tight loop.** Logging is I/O, and a debug line per iteration is how a profile ends up dominated by the logger.

## Practice

1. ▢ Rewrite this as a structured record.

   ```go
   log.Printf("user %s uploaded %d bytes in %v", id, n, d)
   ```

<details markdown="1"><summary>Check</summary>

```go
slog.Info("upload complete", "user", id, "bytes", n, "duration", d)
```

Now `bytes` is a number you can aggregate and `user` is a field you can filter on, without a regex that breaks the first time someone rewords the message.

</details>

2. ▢ What does `go vet` catch in `slog.Info("saved", "id")`?

<details markdown="1"><summary>Check</summary>

The missing value for the final key. The alternating form is convenient precisely because it is untyped, so the compiler cannot check it — the vet analyser added in Go 1.22 fills that gap.

It also reports a key that is neither a string nor a `slog.Attr`. Both produce a malformed record at runtime rather than a failure, which is why they survive to production without `vet` in CI.

</details>

3. ▢ You need debug logs from one running production instance, now.

   - a) Deploy a build with the level set lower
   - b) Change a `slog.LevelVar` through an endpoint
   - c) Restart the process with a debug flag
   - d) Attach a debugger to the running process

<details markdown="1"><summary>Check</summary>

**b)** Change a `slog.LevelVar` through an endpoint.

It takes effect immediately, on the instance that is misbehaving, without losing its state. The other three all restart or replace the process — and the fastest way to stop reproducing a bug is to restart the thing doing it.

</details>

4. ▢ Why prefer passing a `*slog.Logger` to a type over calling `slog.Info` directly?

<details markdown="1"><summary>Check</summary>

Because the logger is then a dependency you can substitute: a test can capture output into a buffer and assert on it, and a component can carry bound attributes like `component=store` that its call sites do not have to repeat.

Package-level `slog.Info` is global state with the usual costs — no substitution, no per-component context, and any test that changes the default affects the others. Setting the default as well is still worth doing, so third-party libraries land in the same stream.

</details>

5. ▢ Interleaving Lesson 18: how does a request id reach a log line ten calls deep without being a parameter?

<details markdown="1"><summary>Check</summary>

Middleware puts it in the context, the code calls the `Context` variants — `logger.InfoContext(ctx, ...)` — and a custom `slog.Handler` reads it from the context in `Handle` and adds it to every record.

This is the legitimate use of `context.Value` from Lesson 18: request-scoped metadata that crosses layers which do not care about it. A logger *handle* would be a dependency and belongs in a parameter; the request id is metadata and does not.

</details>

## Real-world reps

- [ ] Build a service that logs JSON in production mode and text locally, chosen by a flag. Confirm both from one binary.
- [ ] Write a `slog.Handler` that pulls a request id out of the context and adds it to each record. It is about forty lines, and it is the piece that makes logs correlatable.
- [ ] Tomorrow: find a log line in a service you operate that would be useless during an incident because the interesting value is inside the message string. Convert it to an attribute.

## Going further

- [Structured Logging with slog — The Go Blog](https://go.dev/blog/slog)
- [`log/slog` package](https://pkg.go.dev/log/slog) — the `Handler` interface is the extension point
- [`slog.LogValuer`](https://pkg.go.dev/log/slog#LogValuer) — controlling how a sensitive type prints
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top — this lesson compresses it, and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
