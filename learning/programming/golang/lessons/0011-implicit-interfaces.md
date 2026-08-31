---
title: 11. Interfaces Are Satisfied Implicitly
description: The consumer declares the interface, the implementation never mentions it, and small is the point
type: lesson
---

# Lesson 11. Interfaces Are Satisfied Implicitly

**Mission link:** This is the habit Java punishes hardest. Declaring interfaces next to implementations produces Go that compiles, works, and that every reviewer will describe as written in the wrong language.
**Primary source:** [Effective Go — Interfaces](https://go.dev/doc/effective_go#interfaces)
**Prerequisites:** [Lesson 6](0006-methods-and-method-sets.md), [Lesson 7](0007-packages-and-modules.md)

## Warm-up

1. ▢ When are the arguments to a deferred call evaluated?

<details markdown="1"><summary>Check</summary>

At the `defer` statement, not when the call runs. Defer a closure if you need the value as it is at return time.

</details>

2. ▢ Where must `recover` be called for it to work?

<details markdown="1"><summary>Check</summary>

Inside a function deferred directly by the function that panicked, and in the same goroutine. It cannot reach across goroutines, and it cannot stop a fatal runtime error.

</details>

## Know this

There is no `implements`. A type satisfies an interface by having the methods, and the compiler checks this at the point where the value is used as the interface:

```go
type Stringer interface{ String() string }

type Celsius float64
func (c Celsius) String() string { return "..." }   // never mentions Stringer

var s Stringer = Celsius(20)                        // satisfied, checked here
```

`Celsius` does not import the package that declares `Stringer` and does not know it exists. That decoupling is the whole design.

### The interface belongs to the consumer

Because satisfaction is implicit, the interface can be declared where it is *used* rather than where it is implemented. That is the idiom, and it inverts the habit from Java:

```go
// package report — the consumer
type UserStore interface {
    GetUser(ctx context.Context, id string) (*User, error)
}

func Generate(ctx context.Context, s UserStore) error { ... }
```

`store.Postgres` satisfies `report.UserStore` without importing `report`. The dependency arrow points from the consumer to the implementation, so:

- The consumer's interface has exactly the methods that consumer needs — often one — instead of everything the implementation offers.
- Tests substitute a fake by writing a type with one method, in the test file, with no mocking framework.
- The implementation package stays free of abstractions it does not use.
- The import cycle from Lesson 7 goes away, because the arrow only points one way.

The corollary is the phrase you will hear in review: **accept interfaces, return structs.** Take the narrowest interface you can use as a parameter; return the concrete type, so callers keep every method and can decide their own abstraction.

### Small is not a slogan

`io.Reader` is one method, and it is the most reused abstraction in the language — files, network connections, HTTP bodies, gzip streams, `strings.Reader`, and anything that will ever be written all satisfy it. `error` is one method. `fmt.Stringer` is one method. `sort.Interface` is three and is already at the edge.

Rob Pike's proverb states the reason: *the bigger the interface, the weaker the abstraction.* Each method you add excludes implementations and buys the caller nothing it asked for. A five-method `UserService` interface with exactly one implementation is not an abstraction; it is a second copy of the type's signature that must now be kept in sync.

Interface embedding composes small ones instead of growing large ones:

```go
type ReadWriter interface {
    Reader
    Writer
}
```

### When to declare one at all

Do not declare an interface because a type exists. Declare one when you have a reason:

- A consumer needs to work with more than one implementation — including a test double that is not a mocking framework artefact.
- You want to narrow a large dependency down to the two methods you use.
- You are publishing a plugin point that outside code must implement.

One implementation and no test need means no interface yet. Adding one later costs a single line, precisely because implementations never name it — which is the argument for waiting.

`any` is an alias for `interface{}`, added in Go 1.18. It says "any type", which means it says nothing; each use is a place the compiler stopped helping.

### Compile-time assertions

Since implementations do not name their interfaces, nothing normally fails when a method signature drifts. Pin the ones that matter:

```go
var _ http.Handler = (*Server)(nil)
```

Zero runtime cost, and the build breaks at the type rather than at the distant call site.

## Practice

1. ▢ Package `mailer` sends email using `store.Postgres` to look up addresses. Where should the interface be declared, and what should it contain?

<details markdown="1"><summary>Check</summary>

In `mailer`, containing only the methods `mailer` calls — probably `AddressFor(ctx, id) (string, error)` alone.

Declaring it in `store` beside the implementation is the Java reflex. It forces `store` to anticipate consumers, produces an interface with every method the type has, and makes `mailer` depend on `store` for its abstraction as well as its implementation.

</details>

2. ▢ Why does `func Save(w io.Writer, v Record) error` beat `func Save(f *os.File, v Record) error`?

<details markdown="1"><summary>Check</summary>

`io.Writer` is one method, so the same function serves a file, a network connection, an HTTP response, a gzip stream, and a `bytes.Buffer` in a test — with no mock and no interface declared by anyone.

The `*os.File` version can only be tested by touching a real filesystem, which is why "accept interfaces" is a testability argument before it is a design one.

</details>

3. ▢ Which is the strongest reason to declare an interface in Go?

   - a) The type will probably gain a second implementation eventually
   - b) A consumer needs only two of the type's fourteen methods
   - c) Every service type in the codebase already has one
   - d) The team standard says implementations should have interfaces

<details markdown="1"><summary>Check</summary>

**b)** A consumer needs only two of the type's fourteen methods.

That narrowing is real value available today: a smaller dependency, a trivial test double, and a signature that documents exactly what the function touches. Option a is speculation the language lets you defer at no cost, and c and d are habits rather than reasons.

</details>

4. ▢ A colleague's PR adds `type UserService interface` with eight methods, next to the single `userService` struct that implements it. Name the concrete problem, not the style objection.

<details markdown="1"><summary>Check</summary>

The interface has no consumer that needs eight methods, so it abstracts nothing — it duplicates the struct's surface and now has to be updated in two places for every change. Any test double must implement all eight to call one.

Concretely: it adds maintenance cost and removes compiler help, in exchange for a substitutability nobody has asked for. If a test needs a fake, the fix is a one-method interface in the *consumer*.

</details>

5. ▢ Interleaving Lesson 6: `Postgres` has `func (p *Postgres) GetUser(...)`. Does `Postgres{}` satisfy `UserStore`?

<details markdown="1"><summary>Check</summary>

No — `GetUser` has a pointer receiver, so it is only in the method set of `*Postgres`. `&Postgres{}` satisfies it.

This is the most common way method sets bite in real code: the interface is fine, the implementation is fine, and the assignment fails at a line far from either. `var _ UserStore = (*Postgres)(nil)` in the implementation package catches it at the definition.

</details>

## Real-world reps

- [ ] Write a function taking `io.Writer`, and call it three ways: with `os.Stdout`, with a `bytes.Buffer` in a test, and with an `http.ResponseWriter`. No mocking library.
- [ ] Take a service type you own with more than five methods. Write the interface its *biggest consumer* actually needs, and count the methods. It will be smaller than you expect.
- [ ] Tomorrow: find an interface in a codebase with exactly one implementation and no test double. Decide whether deleting it would lose anything.

## Going further

- [Effective Go — Interfaces](https://go.dev/doc/effective_go#interfaces)
- [Go Proverbs — Rob Pike](https://go-proverbs.github.io/) — "the bigger the interface, the weaker the abstraction", with the talk behind it
- [Go Code Review Comments — interfaces](https://go.dev/wiki/CodeReviewComments#interfaces)
- [Lesson 12 — The Nil Interface Trap](0012-the-nil-interface-trap.md) — what an interface value actually holds
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
