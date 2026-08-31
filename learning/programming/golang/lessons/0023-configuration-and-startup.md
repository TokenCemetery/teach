---
title: 23. Configuration and Startup
description: A main that only wires, a run function that returns an error, and validation before the first request
type: lesson
---

# Lesson 23. Configuration and Startup

**Mission link:** Most "it works on my machine" incidents are startup problems. A service that validates its configuration before accepting traffic fails in the deploy instead of in production.
**Primary source:** [Go for Industrial Programming — Peter Bourgon](https://peter.bourgon.org/go-for-industrial-programming/)
**Prerequisites:** [Lesson 22](0022-an-http-server.md), [Lesson 7](0007-packages-and-modules.md)

## Warm-up

1. ▢ Which four timeouts does an explicit `http.Server` set that `http.ListenAndServe` does not?

<details markdown="1"><summary>Check</summary>

`ReadHeaderTimeout`, `ReadTimeout`, `WriteTimeout`, `IdleTimeout` — all zero, meaning unlimited, in the default.

</details>

2. ▢ Why is `init()` a poor place to set up a dependency?

<details markdown="1"><summary>Check</summary>

It runs implicitly, cannot return an error, and cannot be skipped by a test. Explicit construction in `main` gives you an error to handle and a seam to substitute.

</details>

## Know this

### `main` wires; `run` works

The shape that makes a service testable is two functions:

```go
func main() {
    if err := run(context.Background(), os.Args[1:], os.Stdout); err != nil {
        fmt.Fprintln(os.Stderr, "error:", err)
        os.Exit(1)
    }
}

func run(ctx context.Context, args []string, stdout io.Writer) error {
    ...
}
```

`main` does exactly two things nothing else can: it exits with a code, and it prints the final error. Everything else lives in `run`, which returns an error instead of calling `os.Exit`.

That matters because `os.Exit` skips deferred functions. A `defer db.Close()` in a function that ends with `os.Exit(1)` never runs. Confining the exit to `main` means every other cleanup path works.

It also makes the whole startup testable: a test calls `run` with a cancellable context, its own arguments and a buffer, and asserts on the output.

### Flags, environment, or both

The standard library's `flag` package covers most services and needs no dependency:

```go
fs := flag.NewFlagSet("svc", flag.ContinueOnError)
addr := fs.String("addr", ":8080", "listen address")
timeout := fs.Duration("timeout", 5*time.Second, "request timeout")
if err := fs.Parse(args); err != nil {
    return err
}
```

Using a `FlagSet` rather than the package-level functions keeps `run` self-contained — the global `flag.CommandLine` is shared state that makes two tests in one binary interfere.

Environment variables are what container platforms supply, so most services read both, with flags overriding. Whichever you choose, decide once and write it down; a service that reads some settings from flags and others from the environment is a configuration bug generator.

**Secrets do not go in flags.** Command lines are visible in `ps` and in process listings. Read them from the environment, from a file, or from a secret manager.

### Validate before serving

Everything that can be checked at startup should be, and the check should be fatal:

```go
cfg, err := loadConfig(args)
if err != nil {
    return fmt.Errorf("config: %w", err)
}
```

Parse the durations, resolve the addresses, confirm the required values are present, `Ping` the database, compile the templates and the regexes. A process that fails to start is a deploy that rolls back. A process that starts and then fails on the first request that touches a bad setting is an incident, and the setting may be one used only at 3am.

The counter-rule: **do not check what you cannot control.** If a downstream service is down at startup, failing to boot may make an outage worse rather than better — start, report unready, and retry. The line is roughly whether the value is yours (configuration, credentials, files) or someone else's (their availability).

### Zero values as defaults

The zero-value discipline from Lesson 1 pays off in a config struct:

```go
type Config struct {
    Addr         string        // "" means :8080
    Timeout      time.Duration // 0 means the default
    MaxOpenConns int           // 0 means the driver default
}
```

Let the zero value mean "default", document it, and fill in defaults in one place. The alternative — every call site knowing every default — drifts within a month.

### Wiring is boring on purpose

```go
db, err := openDB(ctx, cfg)
if err != nil {
    return fmt.Errorf("open db: %w", err)
}
defer db.Close()

store := store.New(db)
api := httpapi.New(store, logger)
srv := &http.Server{Addr: cfg.Addr, Handler: api, ...}
```

Construct dependencies in order, pass them in explicitly, and let the compiler check the graph. Go has dependency-injection frameworks, and for a single service they mostly convert compile-time errors into runtime ones. Reach for one when the graph is genuinely large; write the twelve lines first.

## Practice

1. ▢ Why should `run` return an error rather than call `os.Exit` directly?

<details markdown="1"><summary>Check</summary>

`os.Exit` terminates immediately and skips every deferred function — `db.Close`, a flushed log buffer, a released lock file.

Returning the error also makes startup testable: a test can call `run` with its own arguments and context and assert on the failure, which is impossible when the function's failure mode is ending the process.

</details>

2. ▢ Where should the database password come from, and where should it not?

<details markdown="1"><summary>Check</summary>

From the environment, a mounted file, or a secret manager. Not from a command-line flag.

Flags land in the process command line, which is readable by other users through `ps` and captured by process-listing agents, crash handlers and container inspectors. It is not a subtle leak — it is one `ps aux` away.

</details>

3. ▢ Which check belongs at startup rather than at first use?

   - a) Whether the payment provider is currently reachable
   - b) Whether the configured listen address parses correctly
   - c) Whether today's partition table has been created
   - d) Whether the user submitting this request is authorised

<details markdown="1"><summary>Check</summary>

**b)** Whether the configured listen address parses correctly.

It is your configuration, it cannot change while the process runs, and finding it wrong later means the deploy already succeeded. Option a is someone else's availability — check it in a readiness probe, not a boot assertion. Options c and d are per-request or per-day concerns.

</details>

4. ▢ A service reads its port from a flag and its database URL from an environment variable. Name the concrete problem.

<details markdown="1"><summary>Check</summary>

Nobody can tell where a setting comes from without reading the source, so operators guess — and a guess that sets the wrong one fails silently, because the unread source is simply ignored.

Pick a precedence rule, apply it to every setting, and document it. "Flags override environment, environment overrides defaults" is a fine rule; having no rule is not.

</details>

5. ▢ Interleaving Lesson 18: what should `run` do with the context it receives?

<details markdown="1"><summary>Check</summary>

Derive from it and pass it down to everything that starts work — the server, the workers, the database. That single context becomes the shutdown signal for the whole process.

In practice `main` passes `context.Background()` and `run` immediately wraps it with `signal.NotifyContext`, so a SIGTERM cancels the tree. That is Lesson 25, and this is the wiring that makes it a two-line change rather than a refactor.

</details>

## Real-world reps

- [ ] Refactor a small program of yours into `main` plus `run(ctx, args, stdout)`. Write one test that calls `run` with a bad flag and asserts on the error.
- [ ] Add startup validation to a service: parse every duration, `Ping` the database, and fail with a message naming the setting. Then set one badly and read what it prints.
- [ ] Tomorrow: list every configuration value in a service you operate and mark where each is read from. Any inconsistency is a future incident.

## Going further

- [Go for Industrial Programming — Peter Bourgon](https://peter.bourgon.org/go-for-industrial-programming/)
- [`flag` package](https://pkg.go.dev/flag)
- [Lesson 25 — Graceful Shutdown](0025-graceful-shutdown.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
