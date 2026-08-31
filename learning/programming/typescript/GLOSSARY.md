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

**Closure**:
A function together with the scope it was created in, which stays reachable after the enclosing function returns. It captures the binding rather than a copy of the value, which is why a `var` loop variable gives every callback the same final value.
_Avoid_: callback, capture, lambda

**Coercion**:
The implicit conversion an operator performs on its operands before comparing or combining them. `==` and `+` both do it, `===` does not, and the conversions are specified rather than intuitive.
_Avoid_: casting, conversion, parsing

**Falsy**:
A property of a value rather than of a comparison: `false`, `0`, `-0`, `0n`, `""`, `null`, `undefined` and `NaN` all test false in a condition. Every other value tests true, including `[]`, `{}` and `"0"`.
_Avoid_: empty, null, unset, invalid

**Live binding**:
The relationship an `import` creates with the exporting module's declaration, so a later change in that module is visible through the import. CommonJS destructuring copies a value instead, which is why the two disagree about a counter.
_Avoid_: reference, alias, shared state

**Microtask**:
Work queued by a promise reaction or an `await` continuation, drained completely before the next task runs. That priority is why a promise callback always precedes a zero-delay timer.
_Avoid_: tick, job, callback, async task

**Own property**:
A property stored on the object itself, as opposed to one found on its **prototype**. Reads walk the prototype chain and writes always create an own property, which is why assigning to an inherited property shadows it rather than changing it.
_Avoid_: instance field, local property, direct property

**Prototype**:
The object a property lookup falls back to when the property is not an own property, forming a chain that ends at `null`. `class` syntax builds one, and `instanceof` asks whether a particular prototype appears in it.
_Avoid_: parent class, base, superclass, `__proto__`

**Temporal dead zone**:
The region between the top of a block and a `let` or `const` declaration in it, where the binding exists and reading it throws. It is also what a cyclic module import runs into.
_Avoid_: hoisting error, uninitialised, undefined
