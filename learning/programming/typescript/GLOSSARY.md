---
title: Glossary
description: Canonical terms for TypeScript
type: glossary
---

# TypeScript Glossary

Canonical terms for this workspace. A term lands here once it can be used correctly, not when it is first mentioned, so this grows as lessons are earned.

## Usage in this workspace

Three words carry a wider meaning elsewhere, and each wider meaning is exactly the mistake this workspace exists to prevent, so all three are pinned from the start:

**Type**:
A compile-time description of what a value may be, which the compiler checks and then erases. It constrains what the compiler accepts and never constrains what arrives at runtime.
_Avoid_: class, schema, shape, validation

**Structural assignability**:
The rule that decides whether one type may be used where another is expected, by comparing members rather than declared names. Two unrelated types with the same members are interchangeable.
_Avoid_: duck typing, implements relationship, inheritance

**Assertion**:
A claim made with `as` or `!` that tells the compiler to stop checking. Nothing is converted, nothing is validated, and if the claim is wrong the program fails later and somewhere else.
_Avoid_: cast, conversion, coercion, type guard

## Terms

_Added as lessons establish them._
