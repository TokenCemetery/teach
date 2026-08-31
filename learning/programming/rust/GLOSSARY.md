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

_Added as lessons establish them._
