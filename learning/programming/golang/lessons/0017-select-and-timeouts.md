---
title: 17 — select and Timeouts
description: Waiting on several channels at once, choosing randomly among the ready, and disabling a case with nil
type: lesson
---

# Lesson 17 — select and Timeouts

**Mission link:** `select` is what turns channels from a queue into a coordination language. Every shutdown path, timeout and worker loop in a Go service is built from it.
**Primary source:** [Go Concurrency Patterns: Pipelines and cancellation — The Go Blog](https://go.dev/blog/pipelines)
**Prerequisites:** [Lesson 16](0016-channels.md)

## Warm-up

1. ▢ Send on a closed channel, receive from a closed channel, receive from a nil channel — which panics?

<details markdown="1"><summary>Check</summary>

Only the send. A closed channel yields zero values with `ok == false`; a nil channel blocks forever.

</details>

2. ▢ Three goroutines send on one channel. How is it closed correctly?

<details markdown="1"><summary>Check</summary>

A `sync.WaitGroup` counts the senders, and one separate goroutine waits then closes. No individual sender may close, or the others panic.

</details>

## Know this

`select` waits until one of several channel operations can proceed:

```go
select {
case v := <-in:
    handle(v)
case out <- result:
    // sent
case <-ctx.Done():
    return ctx.Err()
}
```

Three properties do all the work.

**If several cases are ready, one is chosen uniformly at random.** Not in source order. This prevents a busy channel from starving a quiet one, and it means you cannot express a priority by ordering the cases. When you genuinely need priority, nest: a `select` with a `default` that checks the high-priority channel first, then a blocking `select` over both.

**A `default` case makes it non-blocking.** With `default`, `select` never waits — it takes a ready case or falls through immediately:

```go
select {
case ch <- v:
    // sent
default:
    // nobody ready; drop, count, or buffer
}
```

That is how you shed load rather than block on a full channel. Without `default`, `select` blocks until something is ready.

**A nil channel is never ready.** Assigning nil to a channel variable removes its case from consideration, permanently or temporarily:

```go
for in != nil || out != nil {
    select {
    case v, ok := <-in:
        if !ok {
            in = nil   // source exhausted — stop selecting on it
            continue
        }
        pending = append(pending, v)
    case out <- pending[0]:
        pending = pending[1:]
    }
}
```

Without that, a closed `in` would be ready forever and the loop would spin at full CPU. Recognising this — a `select` case on a closed channel that never blocks — is worth having in your review vocabulary.

### The loop shape

Nearly every long-lived goroutine in a Go service is this:

```go
func (w *Worker) Run(ctx context.Context) error {
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        case job := <-w.jobs:
            w.process(job)
        }
    }
}
```

The cancellation case is first by convention and not by effect — remember the random choice. What matters is that it exists at all, so the goroutine has a way to stop.

### Timeouts

```go
select {
case v := <-ch:
    use(v)
case <-time.After(time.Second):
    return errors.New("timeout")
}
```

Older Go advice says `time.After` leaks: before Go 1.23, an unfired timer was not collected, so a timeout in a hot loop accumulated memory until each one fired. [Go 1.23](https://go.dev/doc/go1.23#timer-changes) changed that — timers and tickers are now eligible for collection as soon as nothing references them, whether or not `Stop` was called. The behaviour follows the `go` line in `go.mod`, so a module on `go 1.22` still has the old one.

Two things did not change. A `time.Ticker` you keep a reference to still needs `defer ticker.Stop()`, because you are still referring to it. And a per-request timeout belongs in the context rather than in a bare `time.After` — `context.WithTimeout` propagates to everything downstream, where a local timer only unblocks the one `select` that reads it.

`select {}` with no cases blocks forever. It is occasionally what you want in a `main` that is entirely driven by background goroutines, and it is otherwise a deadlock waiting to be reported.

## Practice

1. ▢ Two cases are both ready. Which runs?

<details markdown="1"><summary>Check</summary>

One chosen uniformly at random. Source order does not express priority, and code that depends on it will work in testing and fail under production load.

For real priority, check the high-priority channel first in a `select` with `default`, then fall back to a blocking `select` over both.

</details>

2. ▢ This loop pins a CPU at 100%. Why?

   ```go
   for {
       select {
       case v, ok := <-in:
           if !ok {
               continue
           }
           process(v)
       case <-ctx.Done():
           return
       }
   }
   ```

<details markdown="1"><summary>Check</summary>

Once `in` is closed, receiving from it succeeds immediately and forever with `ok == false`. The `continue` goes straight back into the `select`, which is instantly ready again — a spin loop at full speed.

Fix by returning when `!ok`, or by setting `in = nil` so the case stops being selectable. A closed channel is always ready, which is exactly what makes `close` a good broadcast and a bad thing to ignore.

</details>

3. ▢ What does adding a `default` case change?

   - a) The select prefers the default over ready cases
   - b) The select never blocks and may take default
   - c) The select retries each case until one succeeds
   - d) The select blocks until every case is ready

<details markdown="1"><summary>Check</summary>

**b)** The select never blocks and may take default.

`default` runs only when no other case is ready, so it does not take precedence. There is no retry loop, and `select` never waits for more than one case — it takes exactly one.

</details>

4. ▢ Why put a timeout in the context rather than in a `time.After` case?

<details markdown="1"><summary>Check</summary>

Because a context deadline propagates. Everything downstream that accepts the context — the database query, the outbound HTTP call, the next worker — observes the same deadline and stops on its own.

A bare `time.After` unblocks only the `select` that reads it. The work it was waiting on carries on running, unaware, which turns a timeout into a leak: the caller has moved on and the goroutine is still going. Lesson 18 makes this concrete.

</details>

5. ▢ Interleaving Lesson 15: why does a worker's `select` need a `ctx.Done()` case even when nothing currently cancels it?

<details markdown="1"><summary>Check</summary>

Because "never start a goroutine without knowing how it will stop" is a property of the goroutine, not of today's callers. Without that case, the only way the worker ends is process exit.

The moment someone adds graceful shutdown — and stage 4 does — a worker without a cancellation case blocks the shutdown until the timeout expires and the process is killed. The case costs three lines when you write it and a production incident when you do not.

</details>

## Real-world reps

- [ ] Write a `select` over two channels that are both always ready, run it 1,000 times, and count the outcomes. Seeing roughly 50/50 makes the randomness real rather than theoretical.
- [ ] Build the spin loop above deliberately, watch the CPU, and fix it with `in = nil`. Then confirm the loop still exits on context cancellation.
- [ ] Tomorrow: find a long-lived goroutine in code you work with and check whether it has a cancellation case. Note what would stop it today.

## Going further

- [Go Concurrency Patterns: Pipelines and cancellation — The Go Blog](https://go.dev/blog/pipelines)
- [Go 1.23 timer changes](https://go.dev/doc/go1.23#timer-changes)
- [Select, in the language spec](https://go.dev/ref/spec#Select_statements)
- [Concurrency Patterns](../reference/concurrency-patterns.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top — this lesson compresses it, and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
