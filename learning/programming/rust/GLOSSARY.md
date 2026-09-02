---
title: Glossary
description: Canonical terms for Rust
type: glossary
---

# Rust Glossary

Canonical terms for this workspace. A term lands here once it can be used correctly, not when it is first mentioned, so this grows as lessons are earned.

## Usage in this workspace

Four words carry a meaning from other languages that Rust does not share, and each mistranslation is one of the reasons the borrow checker feels arbitrary, so all four are pinned from the start:

**Ownership**:
The property that exactly one binding is responsible for a value and for releasing it, transferred by assignment or by passing it on. It is a compile-time rule about responsibility, enforced with no runtime bookkeeping.
_Avoid_: reference counting, garbage collection, scope

**Borrow**:
A temporary access to a value that someone else still owns, created with `&` or `&mut`. Shared borrows may coexist, a mutable borrow may not coexist with any other, and both are checked at compile time.
_Avoid_: pointer, alias, reference (in the C++ sense), view

**Lifetime**:
A region of code over which a borrow must remain valid, and a constraint the compiler checks rather than a duration it measures. Annotating one relates the lifetimes of inputs and outputs; it never makes a value live longer.
_Avoid_: scope, duration, retention, allocation

**Unsafe**:
A promise from the author that the compiler's usual proof obligations are met by hand, in a block or function where a few extra operations become available. It disables specific checks and never disables the borrow checker or the rules about undefined behaviour.
_Avoid_: unchecked, dangerous, raw, escape hatch

## Terms

**Copy**:
A marker trait for types that are duplicated rather than moved on assignment, because they are plain data with nothing to free. It requires `Clone` and is incompatible with `Drop`, and `&T` has it while `&mut T` deliberately does not.
_Avoid_: value type, primitive, cheap type

**Deref coercion**:
The compiler's automatic conversion from a reference to an owning type into a reference to what it derefs to, such as `&String` into `&str`. It is why taking the borrowed type in a signature costs callers nothing.
_Avoid_: implicit cast, auto-conversion, upcasting

**Drop**:
The point at which a value's owner goes out of scope and its destructor runs, releasing whatever it owns. It happens in reverse declaration order within a scope, which makes it the defined moment a lock is released or a file is closed.
_Avoid_: free, garbage collection, finalisation

**Move**:
The transfer of ownership that assignment or argument passing performs on a non-**Copy** type, after which the source binding is unusable. It is compile-time bookkeeping rather than a runtime operation.
_Avoid_: transfer, copy, reassignment

**Non-lexical lifetimes**:
The analysis under which a borrow ends at its last use rather than at the end of its enclosing scope. It is why many borrow errors are fixed by moving one line instead of restructuring.
_Avoid_: scope-based borrows, lexical scoping

**Reborrow**:
Producing a new borrow from an existing one, which the compiler inserts implicitly when a `&mut T` is passed to a function so the original stays usable. Where it does not fire, such as storing a `&mut` in a struct, the move is real.
_Avoid_: copy, pass-through, nested borrow

**Shadowing**:
Declaring a new binding with the name of an existing one, so the earlier binding becomes unreachable. It is not mutation: the type may change, and no `mut` is required.
_Avoid_: reassignment, overwriting, redeclaration

**Slice**:
A borrowed view into a contiguous sequence, carrying a pointer and a length and owning nothing. `&str` and `&[T]` are the two that appear constantly, and both are what a signature should ask for.
_Avoid_: array, view, range, substring
