---
title: 8. Errors Are Values
description: error is an ordinary interface, so failures are data you handle rather than control flow that escapes
type: lesson
---

# Lesson 8. Errors Are Values

**Mission link:** Error handling is the largest single difference between Go you can operate and Go you cannot. It is also where a habit of throwing exceptions does the most damage.
**Primary source:** [Errors are values — The Go Blog](https://go.dev/blog/errors-are-values)
**Prerequisites:** [Lesson 6](0006-methods-and-method-sets.md)

## Warm-up

1. ▢ Why does `var _ Incrementer = Counter{}` fail when `Inc` has a pointer receiver?

<details markdown="1"><summary>Check</summary>

Pointer-receiver methods are not in the method set of the value type. The interface would hold an unaddressable copy, so the language removes the method rather than let you mutate something unobservable.

</details>

2. ▢ What does a directory named `internal` do?

<details markdown="1"><summary>Check</summary>

It restricts imports to code rooted at `internal`'s parent. The toolchain enforces it, so it is a real boundary rather than a convention.

</details>

## Know this

`error` is not a language feature. It is an ordinary interface declared in the universe block:

```go
type error interface {
    Error() string
}
```

Anything with an `Error() string` method is an error. That is the whole mechanism, and everything else — wrapping, sentinels, matching — is built from ordinary Go on top of it.

Functions that can fail return an error as their **last** result, and the caller checks it immediately:

```go
f, err := os.Open(name)
if err != nil {
    return fmt.Errorf("open config: %w", err)
}
defer f.Close()
```

The convention is rigid on purpose: error last, checked immediately, and no other result is valid when `err != nil` unless the doc comment says so. `io.Reader` is the notable documented exception — `Read` can return bytes *and* an error.

### Why not exceptions

Go has `panic`, and it is not for this. The design choice is that an expected failure — a missing file, a rejected request, a timeout — is a normal outcome and should be visible in the signature and in the call site. An exception is invisible in both: nothing in a Java signature past `throws` tells you what actually propagates, and nothing at the call site marks the lines that can be skipped.

The cost is real. `if err != nil` appears constantly, and it is the most common complaint about the language. The compensation is that control flow is local: you can read a Go function top to bottom and know every path out of it.

What you must not do is make the verbosity disappear by ignoring it:

```go
data, _ := io.ReadAll(r)   // now data is silently empty on failure
```

The blank identifier is a claim that you have thought about it. `errcheck` and most linters flag it, and reviewers should too.

### Creating errors

```go
errors.New("connection closed")                  // fixed message
fmt.Errorf("parse row %d: %v", i, err)           // formatted, does not wrap
fmt.Errorf("parse row %d: %w", i, err)           // formatted, wraps — Lesson 9
```

Error strings are lowercase and end with no punctuation, because they get embedded in longer messages: `fmt.Errorf("load user: %w", err)` should read `load user: connection closed`, not `Load user: Connection closed.`. This is in [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments#error-strings) and reviewers cite it by name.

### Sentinels and types

Two ways to let a caller distinguish one failure from another.

A **sentinel** is a package-level error value, compared by identity:

```go
var ErrNotFound = errors.New("not found")

if errors.Is(err, store.ErrNotFound) { ... }
```

A **custom error type** carries data:

```go
type ValidationError struct {
    Field string
}

func (e *ValidationError) Error() string {
    return "invalid field " + e.Field
}
```

Reach for a sentinel when the caller only needs to know *which* failure. Reach for a type when the caller needs a *detail* — the field name, the retry-after, the HTTP status. Both become part of your package's API the moment a caller matches on them, which is a commitment worth making deliberately.

### Errors are values, so you can use them as values

The blog post that names this lesson makes one point: because errors are ordinary values, repetition can be removed by ordinary programming. The standard library does exactly that in `bufio.Scanner`, which accumulates any error internally and exposes it once:

```go
for scanner.Scan() {
    process(scanner.Text())
}
if err := scanner.Err(); err != nil {
    return fmt.Errorf("scan input: %w", err)
}
```

One check, not one per line. When `if err != nil` genuinely dominates a function, the fix is usually a small type that holds the error — not a new language feature.

## Practice

1. ▢ Write the signature of a function that reads a user by ID and can fail.

<details markdown="1"><summary>Check</summary>

```go
func GetUser(ctx context.Context, id string) (*User, error)
```

Error last, and `context.Context` first — the convention you will meet properly in Lesson 18. Returning `(User, error)` by value is also fine; returning `(*User, error)` lets "not found" be expressed as a nil user if you want it, though an explicit `ErrNotFound` is clearer.

</details>

2. ▢ What is wrong with each line?

   ```go
   return nil, errors.New("Failed to connect to database.")
   data, _ := io.ReadAll(r)
   ```

<details markdown="1"><summary>Check</summary>

The first is capitalised and punctuated, so it reads badly once wrapped: `load config: Failed to connect to database.`. Write `errors.New("connect to database")`.

The second discards a real failure. `data` will be whatever was read before the error — often empty — and the program continues as if nothing happened. If ignoring is genuinely correct, say so with a comment; usually it is not.

</details>

3. ▢ A caller needs to know which field failed validation. Which design gives it that?

   - a) A sentinel error value compared with `errors.Is`
   - b) A custom error type inspected with `errors.As`
   - c) A formatted message the caller parses out
   - d) A boolean second result beside the error

<details markdown="1"><summary>Check</summary>

**b)** A custom error type inspected with `errors.As`.

A sentinel says which failure but carries nothing. Parsing a message is a contract you can break by fixing a typo. A separate boolean duplicates what the error already expresses. Lesson 9 covers the matching machinery.

</details>

4. ▢ Why is `error` being an interface rather than a keyword useful in practice?

<details markdown="1"><summary>Check</summary>

Because you can implement it. Your own types can be errors, errors can carry structured data, and the matching functions in `errors` work on anything satisfying the interface — including types the standard library has never heard of.

It also means an error is just a value: storable in a struct, sendable on a channel, comparable, and returnable from a function that produces several. Nothing in the mechanism is privileged.

</details>

5. ▢ Interleaving Lesson 1: a function returns `(*User, error)`. The error is nil. Can the `*User` be nil too?

<details markdown="1"><summary>Check</summary>

Only if the function documents it. The convention is that a nil error means the other results are valid, so returning `(nil, nil)` is a trap for every caller.

If "no user" is a normal outcome, express it — return `ErrNotFound`, or return `(User, bool, error)` when absence really is not an error. Silently returning a nil pointer with a nil error produces a panic in the caller's next line, far from the function that caused it.

</details>

## Real-world reps

- [ ] Write a `store` package with `ErrNotFound` and a `Get` that returns it. Call it from `main` and handle the two cases differently.
- [ ] Take a function you have written with three or more `if err != nil` blocks in a row. Try the `bufio.Scanner` shape: hold the error in a small type and check once. Keep the result only if it is genuinely clearer.
- [ ] Tomorrow: find a `_` used to discard an error in a codebase you work with. Decide whether it is defensible, and write one sentence saying why.

## Going further

- [Errors are values — The Go Blog](https://go.dev/blog/errors-are-values)
- [Error handling and Go — The Go Blog](https://go.dev/blog/error-handling-and-go)
- [Go Code Review Comments — error strings](https://go.dev/wiki/CodeReviewComments#error-strings)
- [Error Handling](../reference/error-handling.md) — the lookup sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
