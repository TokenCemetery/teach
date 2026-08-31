---
title: 12. The Nil Interface Trap
description: An interface holds a type and a value, so a nil pointer inside it is not a nil interface
type: lesson
---

# Lesson 12. The Nil Interface Trap

**Mission link:** This one bug has shipped in more Go services than any other on this list. It turns a success path into an error path, and the code that causes it reads as obviously correct.
**Primary source:** [Go FAQ — Why is my nil error value not equal to nil?](https://go.dev/doc/faq#nil_error)
**Prerequisites:** [Lesson 11](0011-implicit-interfaces.md)

## Warm-up

1. ▢ Where should an interface be declared — beside the implementation, or in the consumer?

<details markdown="1"><summary>Check</summary>

In the consumer, containing only the methods that consumer uses. Implementations never name the interfaces they satisfy, so the dependency arrow points one way.

</details>

2. ▢ What does `var _ http.Handler = (*Server)(nil)` buy you?

<details markdown="1"><summary>Check</summary>

A compile-time check that `*Server` still satisfies `http.Handler`, at zero runtime cost. The build breaks at the type definition rather than at some distant call site.

</details>

## Know this

An interface value is **two words**: a dynamic type and a dynamic value.

```text
┌──────────────┬───────────────┐
│ dynamic type │ dynamic value │
└──────────────┴───────────────┘
```

An interface is `nil` only when **both** words are nil — when it holds nothing at all. Put a nil `*MyError` into it and the type word is `*MyError`, the value word is nil, and the interface is not nil.

```go
var p *MyError = nil
var err error = p

fmt.Println(p == nil)     // true
fmt.Println(err == nil)   // false — the interface holds a type
```

Both lines are correct and they disagree, because they are asking different questions. `p == nil` asks whether the pointer is nil. `err == nil` asks whether the interface is empty.

### How it reaches production

Almost always through a concrete error type used as a return variable:

```go
func do() error {
    var err *MyError        // concrete type — this is the bug
    if somethingFailed() {
        err = &MyError{}
    }
    return err              // wrapped in a non-nil interface either way
}

if err := do(); err != nil {
    // always taken, even on success
}
```

On the success path `err` is a nil `*MyError`, and returning it produces a non-nil `error`. Every caller now takes the failure branch on a successful call. Nothing panics until something dereferences it, so the symptom appears far from the cause.

The same shape appears with any interface, not just `error`: a nil `*bytes.Buffer` returned as an `io.Writer`, a nil `*Config` returned as a `Provider`.

### Three ways to not have this bug

**Declare the variable as the interface type.** This is the fix that generalises:

```go
func do() error {
    var err error           // interface type — nil stays nil
    if somethingFailed() {
        err = &MyError{}
    }
    return err
}
```

**Return literals on each path.** Explicit `return nil` on success, `return &MyError{}` on failure, no shared variable to be careless with.

**Never give a function a concrete error return type.** `func do() *MyError` is the source of the whole family. Return `error` and let `errors.As` recover the type — which is what Lesson 9 gave you.

`go vet` has a `nilness` analyser that finds some cases, and staticcheck's `SA4023` finds more. Neither catches all of them, so the rule is a habit rather than a tool.

### The related surprise

A nil interface **method call** panics, but a nil *pointer* inside an interface does not, provided the method does not dereference it:

```go
type T struct{}
func (t *T) Ping() string { return "pong" }

var t *T
var i interface{ Ping() string } = t
fmt.Println(i.Ping())   // "pong" — the receiver is nil, and Ping never touches it
```

This is legitimate and occasionally useful: methods on nil receivers are how a nil `*Tree` can be a valid empty tree. It also means a nil check on an interface does not guarantee a usable value.

## Practice

1. ▢ Predict both printed values, then explain the difference in one sentence.

   ```go
   var p *MyError
   var err error = p
   fmt.Println(p == nil, err == nil)
   ```

<details markdown="1"><summary>Check</summary>

`true false`.

`p` is a nil pointer; `err` is an interface holding the type `*MyError` and a nil value, so it is not empty. The wrong instinct is to think the assignment "passes the nil through" — it wraps it.

</details>

2. ▢ Fix this function, and say why your fix works.

   ```go
   func validate(s string) error {
       var e *ValidationError
       if s == "" {
           e = &ValidationError{Field: "name"}
       }
       return e
   }
   ```

<details markdown="1"><summary>Check</summary>

Declare `e` as `error`, or return literals:

```go
func validate(s string) error {
    if s == "" {
        return &ValidationError{Field: "name"}
    }
    return nil
}
```

Both work because nothing ever converts a nil concrete pointer into the interface. In the original, `return e` performs that conversion on every path, including the success path.

</details>

3. ▢ When is an interface value equal to `nil`?

   - a) When the value it holds is nil
   - b) When the type it holds is nil
   - c) When both type and value are nil
   - d) When it was never assigned to

<details markdown="1"><summary>Check</summary>

**c)** When both type and value are nil.

Option a is precisely the misconception this lesson exists to break. Option b cannot happen on its own — a type word with no value word is not a state you can produce by assignment. Option d is a true consequence rather than the rule, since an unassigned interface has both words nil.

</details>

4. ▢ A handler returns 500 for every request, and the logged error line reads `<nil>`. What do you look for first?

<details markdown="1"><summary>Check</summary>

A function returning a concrete error type, or assigning to a concrete-typed variable and returning it as `error`. The branch runs because the interface is non-nil; the `<nil>` comes from the value inside it.

That exact output is worth understanding, because it is not `fmt` printing a nil interface. `fmt` called `Error()` on a nil receiver, the method dereferenced a field and panicked, and `fmt` recovered and printed `<nil>` because the argument was a nil pointer. An error type whose `Error()` does *not* touch its fields prints its message normally — so a healthy-looking log line does not rule this out.

Grep for `*SomeError` in return positions and for `var err *`. This bug hides in exactly those two shapes.

</details>

5. ▢ Interleaving Lesson 6: does this bug have anything to do with method sets?

<details markdown="1"><summary>Check</summary>

No, and separating them is worth doing explicitly. Method sets decide *whether* a type satisfies an interface, at compile time. This trap is about *what an interface value contains* once a type has been stored in it, at run time.

They meet only in that both come from the same fact — an interface holds a copy of a value along with its type. One consequence is checked by the compiler; the other is not checked at all.

</details>

## Real-world reps

- [ ] Reproduce the bug in ten lines and run it. Then print `fmt.Printf("%T %v\n", err, err)` on the returned error to see the type word and the value word separately.
- [ ] Write a `*Tree` type with a `Sum() int` method that works on a nil receiver. It is the same mechanism used deliberately, and holding both in mind is what makes the rule stick.
- [ ] Tomorrow: grep a codebase you work with for functions returning a concrete error type rather than `error`. Each is a latent instance.

## Going further

- [Go FAQ — why is my nil error value not equal to nil?](https://go.dev/doc/faq#nil_error)
- [The Laws of Reflection — The Go Blog](https://go.dev/blog/laws-of-reflection) — the type/value pair, from the other direction
- [Typed nils in Go 2 — Dave Cheney](https://dave.cheney.net/2017/08/09/typed-nils-in-go-2)
- [Error Handling](../reference/error-handling.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
