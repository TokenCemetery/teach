---
title: 14. Designing a Package
description: Doc comments, a small exported surface, and a dependency arrow that points one way
type: lesson
---

# Lesson 14. Designing a Package

**Mission link:** Reviewing someone's Go and naming why a design is wrong starts here. Most package-level mistakes are visible before you read a single function body.
**Primary source:** [Go Doc Comments, The Go Authors](https://go.dev/doc/comment)
**Prerequisites:** [Lesson 7](0007-packages-and-modules.md), [Lesson 11](0011-implicit-interfaces.md)

## Warm-up

1. ▢ `Base.Greet` calls `b.Name()`. `Child` embeds `Base` and defines its own `Name`. Which runs?

<details markdown="1"><summary>Check</summary>

`Base.Name`. The receiver inside `Greet` is a `Base`, and it has no knowledge of the `Child` containing it. There is no virtual dispatch.

</details>

2. ▢ Why is a five-method interface with one implementation a smell?

<details markdown="1"><summary>Check</summary>

It abstracts nothing: it duplicates the type's surface and must be kept in sync, while forcing any test double to implement all five. Interfaces earn their place by narrowing a dependency for a consumer.

</details>

## Know this

A package is a unit of *meaning*, not a folder of related files. The test is whether you can finish this sentence without "and": **this package does ___.** `store`, `jwt`, `httpapi` pass. `util`, `models`, `helpers` do not, which is why they grow without limit.

### The exported surface is the whole design

Everything you export is a promise. Everything you do not can change freely. So the design question for a package is not "what does it contain" but "what does a caller have to know".

Practical consequences:

- **Start unexported.** Export when a caller genuinely needs it. Widening is additive; narrowing is a breaking change.
- **Export behaviour, not state.** An exported struct field can be set to anything at any time by anyone. A method can validate.
- **Return concrete types.** Callers get every method, and you can add methods later without breaking anyone.
- **Take the narrowest parameter you can use.** `io.Writer` over `*os.File`, `context.Context` first.
- **Make the zero value work** where you can, so the API has one fewer thing to get wrong.

The functions a package exports should read as a vocabulary. `store.Get`, `store.Put`, `store.Delete`, not `store.DoStoreOperation(op int)`.

### Doc comments are the API

`go doc` and [pkg.go.dev](https://pkg.go.dev) render the comment immediately above each exported identifier. There is exactly one convention: **start with the identifier's name** and write full sentences.

```go
// Get returns the user with the given id.
// It returns ErrNotFound if no such user exists.
func (s *Store) Get(ctx context.Context, id string) (*User, error)
```

Starting with the name is what makes the generated docs read correctly and what makes `go doc Get` useful. "This function gets a user" fails both.

A package needs a package comment, conventionally in a `doc.go` when it runs to more than a line:

```go
// Package store persists users in Postgres.
//
// A Store is safe for concurrent use. The zero value is not usable;
// call New.
package store
```

Document what a caller cannot see from the signature: which errors are returned, whether the type is safe for concurrent use, whether the zero value works, whether a returned slice may be retained. Those four cover most of what people get wrong.

### Examples are tests that are also documentation

A function named `ExampleGet` in a `_test.go` file appears in the rendered docs *and* runs under `go test`:

```go
func ExampleStore_Get() {
    s := store.New(db)
    u, err := s.Get(context.Background(), "u1")
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println(u.Name)
    // Output: Ada
}
```

The `// Output:` comment makes it an assertion. Documentation that cannot rot is worth more than documentation that reads better.

### Dependency direction

Two rules do most of the work:

**Consumers declare interfaces** (Lesson 11), so the arrow points from the code that needs a thing to the code that provides it. Never the other way.

**Import cycles are a design error, not an obstacle.** When `a` and `b` want each other, one of three things is true: they are really one package, a shared type belongs in a third, or one of them should accept an interface instead of importing.

The layering that follows for a service is boring and works:

```text
cmd/svc          → wiring, flags, main
internal/httpapi → transport: decode, call, encode
internal/user    → domain types and rules; imports neither of the above
internal/store   → persistence; satisfies interfaces declared in user or httpapi
```

Domain in the middle, imported by everything, importing nothing of yours.

### Configuration surface

A constructor with more than three or four parameters wants a config struct:

```go
type Options struct {
    Timeout time.Duration
    Retries int
}

func New(db *sql.DB, opts Options) *Store
```

A struct keeps call sites readable, lets the zero value mean "defaults", and adds fields without breaking callers. Functional options, as in `New(db, WithTimeout(d))`, are the other established answer, and they cost a function per setting; they earn their place in libraries with many optional knobs and a long compatibility horizon, which is [Lesson 34](0034-api-design-and-compatibility.md).

## Practice

1. ▢ Rewrite this doc comment.

   ```go
   // This function will parse the token and give back the claims inside it.
   func ParseToken(s string) (*Claims, error)
   ```

<details markdown="1"><summary>Check</summary>

```go
// ParseToken parses a signed token and returns its claims.
// It returns ErrExpired if the token is well-formed but no longer valid.
```

Start with the name, so `go doc` and pkg.go.dev read properly. Then add what the signature cannot say: which sentinel errors a caller can match on.

</details>

2. ▢ A package exports a struct with all fields public and no constructor. Name two concrete risks.

<details markdown="1"><summary>Check</summary>

Any caller can construct an invalid value, half-filled or with a nil map field or with a timeout of zero meaning "never", and your methods have to defend against every combination.

And every field is now a compatibility commitment. Renaming or removing one breaks callers, so the struct's internals are frozen the moment it is published.

The fix is not automatic getters. It is exporting only what callers need to set, and validating in a constructor when the zero value cannot be made to work.

</details>

3. ▢ Which package name is worth objecting to in review?

   - a) `package token`
   - b) `package httpapi`
   - c) `package models`
   - d) `package store`

<details markdown="1"><summary>Check</summary>

**c)** `package models`.

It names a category rather than a subject, so nothing is ever out of place in it and it accumulates every type in the system. Call sites read `models.User` where `user.User` stutters and `user.Profile` reads well. The naming problem is usually telling you the package boundary is wrong.

</details>

4. ▢ `store` needs to publish events and `events` needs to record delivery in the store. The build fails with an import cycle. Give two ways out and say which you would pick.

<details markdown="1"><summary>Check</summary>

Extract the shared type into a third package both import, or have `store` accept a narrow `Publisher` interface it declares itself, satisfied by `events`.

Prefer the interface. It costs one declaration, keeps the arrow pointing one way, and makes `store` testable without an event system. The third package is right when the shared thing is genuinely a domain type rather than a behaviour.

Merging them is the third option and is right more often than people admit: two packages that each need the other may be one package.

</details>

5. ▢ Interleaving Lesson 8: what belongs in a package's doc comment about errors?

<details markdown="1"><summary>Check</summary>

Which sentinel errors and error types callers are allowed to match on. That set is API: once documented, `errors.Is(err, store.ErrNotFound)` is a contract you have to keep.

Errors you do not document are free to change. This is the cheapest way to keep the wrapping decision from Lesson 9 honest: write down what is matchable, and translate everything else at the boundary.

</details>

## Real-world reps

- [ ] Run `go doc ./...` on a package you have written. Read it as a stranger would and note every place the docs do not answer "which errors?" or "is it safe to use concurrently?".
- [ ] Write one `Example` function with an `// Output:` comment and run `go test`. Watch it fail when you change the output, that is the property that makes it worth writing.
- [ ] Tomorrow: draw the import arrows for one service you work on. Any arrow pointing from domain code toward transport or storage is a finding.

## Going further

- [Go Doc Comments](https://go.dev/doc/comment)
- [Organizing a Go module](https://go.dev/doc/modules/layout)
- [Go for Industrial Programming, Peter Bourgon](https://peter.bourgon.org/go-for-industrial-programming/): package boundaries and wiring in services that are operated
- [Lesson 34. API Design and Compatibility](0034-api-design-and-compatibility.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
