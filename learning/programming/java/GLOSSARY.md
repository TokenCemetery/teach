---
title: Glossary
description: Canonical terms for Java
type: glossary
---

# Java Glossary

Canonical terms for this workspace. A term lands here once it can be used correctly, not when it is first mentioned, so this grows as lessons are earned.

## Usage in this workspace

Three words are used loosely in ways that would make later lessons ambiguous, and each one hides a mistake that compiles cleanly, so all three are pinned from the start:

**Reference**:
A value that refers to an object, held in a variable, a field, or an array slot. Everything in Java is passed by value, and for objects the value passed is the reference, which is why a method can mutate what it was given and can never rebind the caller's variable.
_Avoid_: pointer, handle, alias

**Final**:
A promise that a variable, field or parameter will not be reassigned. It says nothing about the object on the other end, so a `final` list can still be cleared.
_Avoid_: immutable, constant, read-only

**Thread-safe**:
A property of a class relative to a stated contract: correct behaviour when accessed concurrently, with the contract saying what "correct" means. It is not a synonym for using `synchronized`, and a class built entirely from thread-safe parts is not automatically one.
_Avoid_: synchronised, atomic, concurrent

## Terms

_Added as lessons establish them._
