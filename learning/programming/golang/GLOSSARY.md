---
title: Glossary
description: Canonical terms for Go
type: glossary
---

# Go Glossary

Canonical terms for this workspace. A term lands here once it can be used correctly, not when it is first mentioned — so this grows as lessons are earned.

## Usage in this workspace

Two words mean something narrower in Go than they do in most other languages. Carrying the wider meaning across produces code that compiles and is still wrong, so both are pinned from the start:

**Interface**:
A set of method signatures that any type satisfies implicitly by having those methods. There is no declaration of intent and no `implements`.
_Avoid_: contract, abstract class, implements relationship

**Zero value**:
The usable default a variable holds when declared without initialisation — `0`, `""`, `nil`, or a struct with each field at its own zero value. Designing types so the zero value works is idiomatic Go.
_Avoid_: null, undefined, uninitialised

## Terms

**Addressable**:
A property of an expression that has a memory address, so `&x` is legal and a pointer method may be called on it. Variables and struct fields are addressable; map elements and function results are not.
_Avoid_: assignable, referenceable

**Backing array**:
The contiguous storage a **slice** points into. A slice does not own it, and two slices can share one without either knowing.
_Avoid_: underlying buffer, internal array

**Channel**:
A typed conduit that carries values between goroutines and establishes a **happens-before** edge in doing so. Unbuffered channels synchronise both sides; buffered ones decouple them.
_Avoid_: queue, pipe, stream

**Context**:
A value carrying a cancellation signal, a deadline and request-scoped metadata down a call tree. It is a parameter, never a struct field, and cancellation through it is cooperative.
_Avoid_: cancellation token, request scope, thread local

**Data race**:
Two goroutines accessing the same memory with at least one write and no **happens-before** edge between them. It is undefined behaviour, not an unpredictable-but-bounded outcome.
_Avoid*_: race condition — that is the broader logical bug, and a program can have one without a data race

**Embedding**:
Declaring a field with a type and no name, so the outer type promotes the embedded type's exported fields and methods. It is delegation the compiler writes for you, with no dynamic dispatch.
_Avoid_: inheritance, subclassing, extending

**Escape analysis**:
The compiler's proof about whether a value outlives the function that created it. A value that cannot be proven local escapes to the heap; everything else lives on the stack.
_Avoid_: heap allocation analysis, boxing

**Goroutine**:
An independently scheduled function call, multiplexed by the runtime onto operating-system threads, with a stack that grows on demand. It has no identity and no owner unless you give it one.
_Avoid_: thread, coroutine, task, green thread

**Goroutine leak**:
A goroutine blocked on something that can never happen, so the runtime can never collect it or anything its stack references.
_Avoid_: hung thread, zombie goroutine

**Happens-before**:
The ordering guarantee the [memory model](https://go.dev/ref/mem) defines between two operations. Where it exists, one goroutine is guaranteed to observe the other's writes; where it does not, there is a **data race**.
_Avoid_: synchronised, ordered, sequenced

**Method set**:
The methods a type carries for the purpose of satisfying an **interface**. `T` has only its value-receiver methods; `*T` has both, which is why a value can fail to satisfy an interface its pointer satisfies.
_Avoid_: method list, vtable, type signature

**Minimal version selection**:
The rule that resolves a build to the highest of the minimum versions required across the module graph, rather than to the newest published version. It is what makes builds reproducible without a lockfile.
_Avoid_: dependency resolution, version pinning

**Module**:
A collection of packages released and versioned together, rooted at a `go.mod`. Major version 2 and above carries the version in the module path.
_Avoid_: library, artifact, project

**Package**:
A directory of `.go` files compiled together, and the unit of both encapsulation and naming. Identifiers starting with an uppercase letter are visible to importers; everything else is not.
_Avoid_: namespace, module, folder

**Receiver**:
The value or pointer a method is called on, declared between `func` and the method name. Choose value or pointer per type rather than per method.
_Avoid_: this, self, instance

**Rune**:
An alias for `int32` holding a Unicode code point. Ranging a string yields runes with their byte offsets; indexing a string yields a byte.
_Avoid_: character, char, symbol

**Sentinel error**:
A package-level error value that callers identify with `errors.Is`. Documenting one makes it part of your API.
_Avoid_: error constant, error code, marker error

**Slice**:
A three-word header — pointer, length, capacity — describing a view into a **backing array**. It is copied by value like everything else, which is why appending inside a function does not change the caller's length.
_Avoid_: list, array, vector

**Type parameter**:
A placeholder type in a function or type declaration, bounded by a constraint. Worth introducing when the same logic is genuinely identical across types, not when behaviour differs — that is an **interface**.
_Avoid_: generic type, template parameter

**Wrapping**:
Producing an error that keeps another retrievable, with `%w` in `fmt.Errorf` or an `Unwrap` method. What you wrap becomes part of your API, because callers can match on it.
_Avoid_: chaining, nesting, causing

\* Aliases marked with an asterisk are real terms with a different meaning, listed to keep the two apart rather than because the word is wrong.
