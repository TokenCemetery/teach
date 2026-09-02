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

**Binding mode**:
The implicit `ref`, `ref mut` or move state a sub-pattern inherits when a non-reference pattern is matched against a reference, which is why matching `&record` gives you borrowed fields without writing `&` anywhere. From the 2024 edition an explicit `&` pattern may not be layered on top of an implicit borrow.
_Avoid_: dereference, ref keyword as the only way, move, coercion

**Closure**:
An anonymous function that captures what its body uses from the enclosing scope, by shared borrow, mutable borrow or move, whichever is the least it needs. Which of `Fn`, `FnMut` and `FnOnce` it satisfies follows from what it does with the capture rather than from how it is written.
_Avoid_: lambda as a synonym for its type, function pointer, block, thunk

**Combinator**:
A method on `Option` or `Result` that transforms or inspects the value inside without unwrapping it, such as `map`, `and_then` or `ok_or`. Each answers one question, and a chain of them is the alternative to a `match` rather than a replacement for thinking about the absent case.
_Avoid_: helper, functor, adapter, which is an iterator's word, chaining as a style

**Copy**:
A marker trait for types that are duplicated rather than moved on assignment, because they are plain data with nothing to free. It requires `Clone` and is incompatible with `Drop`, and `&T` has it while `&mut T` deliberately does not.
_Avoid_: value type, primitive, cheap type

**Deref coercion**:
The compiler's automatic conversion from a reference to an owning type into a reference to what it derefs to, such as `&String` into `&str`. It is why taking the borrowed type in a signature costs callers nothing.
_Avoid_: implicit cast, auto-conversion, upcasting

**Discriminant**:
The value an enum stores to say which variant it holds. It costs space unless the compiler can hide it in a bit pattern the payload cannot use, so an enum is generally its largest variant plus the discriminant, rounded to the alignment its fields demand.
_Avoid_: tag as a synonym for the whole value, index, type id, variant

**Disjoint capture**:
A closure capturing individual fields of a struct rather than the whole struct, from the 2021 edition onward, so touching one field leaves the others usable. It removes a `clone` the older whole-struct rule used to force.
_Avoid_: partial move, field borrow as a general rule, split borrow of a slice, move

**Drop**:
The point at which a value's owner goes out of scope and its destructor runs, releasing whatever it owns. It happens in reverse declaration order within a scope, which makes it the defined moment a lock is released or a file is closed.
_Avoid_: free, garbage collection, finalisation

**Exhaustiveness**:
The compiler's requirement that a `match` account for every possible value, which is what makes adding an enum variant a compile error rather than a silent gap. Satisfying it with a catch-all on an enum you own gives the guarantee away.
_Avoid_: completeness, default case, total function, coverage in the testing sense

**Iterator**:
A type with a `next` method returning `Option<Item>`, which is where absence and iteration meet. Adapters build a new iterator and do nothing until a consumer asks for items, so a chain with no consumer runs no code at all.
_Avoid_: loop, generator, stream, which is async, collection

**Move**:
The transfer of ownership that assignment or argument passing performs on a non-**Copy** type, after which the source binding is unusable. It is compile-time bookkeeping rather than a runtime operation.
_Avoid_: transfer, copy, reassignment

**Niche optimisation**:
The compiler's use of an impossible bit pattern in a payload to store an enum's discriminant, which is why `Option<&T>` and `Option<Box<T>>` are the same size as the pointer they wrap. The standard library documents that guarantee for those cases; other sizes are not promised.
_Avoid_: compression, packing, null pointer as a value, alignment

**Non-lexical lifetimes**:
The analysis under which a borrow ends at its last use rather than at the end of its enclosing scope. It is why many borrow errors are fixed by moving one line instead of restructuring.
_Avoid_: scope-based borrows, lexical scoping

**Option**:
The standard library's enum for a value that may be absent, `Some(T)` or `None`, which replaces null by making absence a different type from presence. A signature therefore says where absence can arrive, and the compiler will not let one stand in for the other.
_Avoid_: null, nullable, default value, error

**Panic**:
The failure path for a broken invariant in your own code, which unwinds the thread with a message, a file and a line rather than returning anything. It is not the same event as an `Err`, which returns normally and prints nothing on its own.
_Avoid_: exception, error, crash, abort

**Reborrow**:
Producing a new borrow from an existing one, which the compiler inserts implicitly when a `&mut T` is passed to a function so the original stays usable. Where it does not fire, such as storing a `&mut` in a struct, the move is real.
_Avoid_: copy, pass-through, nested borrow

**Refutable pattern**:
A pattern that may fail to match some value of its type, which is why it is allowed in `if let`, `while let` and `let ... else` and rejected in a plain `let` or a function parameter. An irrefutable pattern always matches, and the distinction decides which construct will accept it.
_Avoid_: invalid pattern, optional match, guard, wildcard

**Result**:
The standard library's enum for an operation that may fail, `Ok(T)` or `Err(E)`, used when the caller could reasonably do something about the failure. The `?` operator returns early on `Err`, which is what makes propagating one cheap enough to do everywhere.
_Avoid_: exception, panic, Option, status code

**Shadowing**:
Declaring a new binding with the name of an existing one, so the earlier binding becomes unreachable. It is not mutation: the type may change, and no `mut` is required.
_Avoid_: reassignment, overwriting, redeclaration

**Slice**:
A borrowed view into a contiguous sequence, carrying a pointer and a length and owning nothing. `&str` and `&[T]` are the two that appear constantly, and both are what a signature should ask for.
_Avoid_: array, view, range, substring

**Variant**:
One of the shapes an enum's value may take, which may carry no data, a tuple payload or named fields. A payload is owned by the value the way a struct's field is, so constructing a variant moves what you put in it.
_Avoid_: case as a synonym for the enum, subclass, tag, member
