---
title: 36 — Reviewing Go
description: Let the tools find style, spend your attention on lifecycle, boundaries and what the compiler cannot check
type: lesson
---

# Lesson 36 — Reviewing Go

**Mission link:** Reviewing a colleague's PR and saying precisely why a design is wrong is the mission's own wording. This lesson is the vocabulary and the order to look in.
**Primary source:** [Go Code Review Comments — The Go Authors](https://go.dev/wiki/CodeReviewComments)
**Prerequisites:** every lesson before it — this is where they get used together

## Warm-up

1. ▢ Name two of the five questions to ask about any new goroutine.

<details markdown="1"><summary>Check</summary>

What stops it; who waits for it and handles its error; what it shares and what protects that; is there a measurement; would sequential be simpler.

</details>

2. ▢ Why does "concurrent" not imply "faster"?

<details markdown="1"><summary>Check</summary>

Coordination, scheduling and lost cache locality are fixed costs. For small units of work they exceed the benefit, and the sequential version wins.

</details>

## Know this

### Let the machine do the mechanical part

If a comment could have been made by a tool, a tool should have made it. Before review:

```bash
gofmt -l .            # formatting — not a matter of opinion
go vet ./...          # copylocks, lostcancel, printf, slog pairs, tests
go test -race ./...   # races in the paths the tests cover
staticcheck ./...     # or golangci-lint, in CI
govulncheck ./...     # known vulnerabilities you actually reach
```

Reviewing formatting and naming by hand burns the attention needed for what tools cannot see: lifecycle, boundaries, error semantics, and whether the design is right.

### What to look at, in order

**1. The API surface.** What is exported? Could it be smaller? Does the interface belong to the consumer? Are the errors that callers may match on documented? These decisions are the hardest to change later, so they get looked at first ([Lesson 14](0014-designing-a-package.md), [Lesson 34](0034-api-design-and-compatibility.md)).

**2. Error paths.** Is every error handled or returned, never both? Does `%w` appear where a caller may match, and `%v` where the cause is an implementation detail? Does any error get discarded with `_`? Does any function return a concrete error type ([Lesson 12](0012-the-nil-interface-trap.md))?

**3. Lifecycle.** For every `go` statement: what stops it, who waits, where does its error go? For every context: is it passed down, is `cancel` deferred, is a fresh one used for shutdown? For every acquired resource: is the release deferred immediately, and is it inside a loop ([Lesson 10](0010-defer-panic-and-recover.md))?

**4. Shared state.** What is reachable from more than one goroutine? What guards it? Is a lock held across I/O? Is a map shared without one?

**5. The boundaries.** Does the repository leak `sql.ErrNoRows`? Does the transport layer contain business rules? Do the import arrows point one way?

**6. Tests.** Do they cover the failure paths, not just the happy one? Would they fail if the logic were wrong, or only if it panicked? Is there a table, and is the case you would add already there?

### The comments worth making

Cite the rule and give the alternative. "This could be nicer" is not reviewable; the following are:

| Instead of | Say |
|---|---|
| "bad naming" | "`store.NewStore` stutters at the call site — `store.New` reads better" |
| "use a pointer" | "value receiver copies the mutex; `go vet` flags this as `copylocks`" |
| "too many methods" | "the only consumer uses two of these — a two-method interface in the consumer would do" |
| "this might leak" | "if the caller returns early, these sends block forever — buffer the channel or add `ctx.Done()`" |
| "wrap the error" | "`%v` here breaks `errors.Is` for `ErrNotFound` two layers up" |

The pattern: name the concrete consequence, and name the mechanism. That is what makes a review teachable rather than a matter of taste — and it is what [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments) is for. Linking it settles arguments without making them personal.

### The Go-specific things that pass review too easily

Wrong code that compiles cleanly is the theme of this whole workspace, and these are the ones a reviewer has to catch because nothing else will:

- A value receiver on a type with a mutex, or with any mutating method ([Lesson 6](0006-methods-and-method-sets.md)).
- A sub-slice handed out with spare capacity ([Lesson 3](0003-slices-and-the-backing-array.md)).
- A concrete error type in a return position ([Lesson 12](0012-the-nil-interface-trap.md)).
- `defer` inside a loop ([Lesson 10](0010-defer-panic-and-recover.md)).
- A goroutine with no cancellation case ([Lesson 21](0021-goroutine-leaks.md)).
- `Shutdown` given the already-cancelled context ([Lesson 25](0025-graceful-shutdown.md)).
- An interface declared next to its single implementation ([Lesson 11](0011-implicit-interfaces.md)).
- `rows.Err()` missing after the loop ([Lesson 26](0026-talking-to-a-database.md)).

### Reviewing as the author

Read your own diff before sending it, and answer the questions above. Say what you were unsure about — "I could not decide between an options struct and functional options" gets you a better review than silence, because it tells the reviewer where their judgment is worth spending.

## Practice

1. ▢ A PR adds a five-method interface next to the struct implementing it. What do you say?

<details markdown="1"><summary>Check</summary>

Ask which consumer needs five methods. If the answer is "none — it is for tests", the interface belongs in the consumer package with only the methods that consumer calls.

Name the cost concretely: two declarations to keep in sync, every test double must implement all five, and the abstraction constrains nothing because there is one implementation. That is reviewable; "this is not idiomatic" is not.

</details>

2. ▢ A reviewer comments on gofmt spacing and misses an unclosed `rows`. What went wrong with the process?

<details markdown="1"><summary>Check</summary>

Formatting reached review at all. `gofmt` and `go vet` in CI make that comment impossible, which frees the reviewer's attention for the leak — the thing no tool in the standard set will catch.

Human attention is the scarce resource in review. Spending it on what a tool decides is the most common reason real defects get through.

</details>

3. ▢ Which finding should a *tool* catch rather than a reviewer?

   - a) A value receiver copying an embedded mutex
   - b) An interface declared beside its one implementation
   - c) A goroutine with no path that stops it
   - d) A repository leaking a driver-specific error

<details markdown="1"><summary>Check</summary>

**a)** A value receiver copying an embedded mutex.

`go vet`'s `copylocks` reports it, so it should never reach a human. The other three are design judgments that no analyser makes reliably — which is exactly why they are what review is for.

</details>

4. ▢ Rewrite this review comment so it is actionable: "this error handling looks wrong".

<details markdown="1"><summary>Check</summary>

"This logs the error and returns it, so the handler above logs it again — one incident becomes two log lines. Either handle it here and return nil, or return it wrapped and let the middleware log it."

Name the consequence, name the rule, offer both fixes. The author can act on that without a round trip, and they learn the rule rather than the instance.

</details>

5. ▢ Interleaving Lesson 3: what do you look for in a function returning a sub-slice of its input?

<details markdown="1"><summary>Check</summary>

Whether the returned slice has spare capacity into storage the caller still holds. `return s[:2]` lets the caller's next `append` overwrite `s[2]` — silently, and only when capacity happens to allow it.

The fix is `s[0:2:2]` or `slices.Clone`. This is worth checking every time because it produces no panic, no race report, and no test failure unless someone thought to write that specific test.

</details>

## Real-world reps

- [ ] Review one of your own older PRs against the six-point order above. Note which category you had never explicitly checked.
- [ ] Add `gofmt -l`, `go vet` and `go test -race` to a repository's CI if any is missing, so those comments stop reaching humans.
- [ ] Tomorrow: on your next review, write one comment that names the mechanism and links the rule. Notice whether the conversation is shorter.

## Going further

- [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)
- [Effective Go](https://go.dev/doc/effective_go)
- [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md) — decisions the official docs leave open
- [Review Checklist](../reference/review-checklist.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top — this lesson compresses it, and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
