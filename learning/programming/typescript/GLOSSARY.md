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

**Annotation**:
A type written explicitly at a variable, parameter or return position, which the compiler checks against what it would have inferred there. It constrains rather than informs: an annotation wider than the inferred type throws information away.
_Avoid_: declaration, type hint, cast

**any**:
A type that switches checking off for the value it is applied to, rather than a type that safely matches everything. It propagates: every expression derived from an `any` is unchecked too, so one of them removes checking from a region rather than from a line.
_Avoid_: wildcard, dynamic, untyped, object

**as const**:
An assertion that keeps a literal at its literal type instead of widening it, and additionally makes arrays and object properties readonly. It changes what the compiler infers and nothing about the value at run time.
_Avoid_: freeze, immutable, constant

**Closure**:
A function together with the scope it was created in, which stays reachable after the enclosing function returns. It captures the binding rather than a copy of the value, which is why a `var` loop variable gives every callback the same final value.
_Avoid_: callback, capture, lambda

**Coercion**:
The implicit conversion an operator performs on its operands before comparing or combining them. `==` and `+` both do it, `===` does not, and the conversions are specified rather than intuitive.
_Avoid_: casting, conversion, parsing

**Contextual typing**:
The type an expression receives from the position it appears in, such as a callback taking its parameter types from the signature it is passed to. It flows a type inwards, where inference reads one outwards, which is why a well-typed callback needs no annotation at all.
_Avoid_: inference, narrowing, duck typing

**Control-flow analysis**:
The compiler's tracking of what a value's type must be at each position, given the branches taken to reach it. A type is therefore a property of a position in the code rather than of a declaration.
_Avoid_: type inference, static analysis, data flow

**Excess property checking**:
The check that rejects members a target type does not declare, firing only when a fresh object literal is assigned or passed directly to a typed position. It is not part of structural assignability and is defeated by routing the same object through a variable.
_Avoid_: strict object checking, structural assignability, exact types

**Falsy**:
A property of a value rather than of a comparison: `false`, `0`, `-0`, `0n`, `""`, `null`, `undefined` and `NaN` all test false in a condition. Every other value tests true, including `[]`, `{}` and `"0"`.
_Avoid_: empty, null, unset, invalid

**Literal type**:
A type inhabited by exactly one value, such as `"circle"` or `42`, most useful as one member of a union. It is what makes a union able to say which strings are allowed rather than only that a string is allowed.
_Avoid_: enum, constant, string literal, value type

**Live binding**:
The relationship an `import` creates with the exporting module's declaration, so a later change in that module is visible through the import. CommonJS destructuring copies a value instead, which is why the two disagree about a counter.
_Avoid_: reference, alias, shared state

**Microtask**:
Work queued by a promise reaction or an `await` continuation, drained completely before the next task runs. That priority is why a promise callback always precedes a zero-delay timer.
_Avoid_: tick, job, callback, async task

**Narrowing**:
A type refinement the compiler derives from a condition, valid only at positions reachable through that branch. It is lost when a local is reassigned anywhere afterwards, and when a property's use is deferred into a closure.
_Avoid_: casting, assertion, type guard, validation

**Own property**:
A property stored on the object itself, as opposed to one found on its **prototype**. Reads walk the prototype chain and writes always create an own property, which is why assigning to an inherited property shadows it rather than changing it.
_Avoid_: instance field, local property, direct property

**Prototype**:
The object a property lookup falls back to when the property is not an own property, forming a chain that ends at `null`. `class` syntax builds one, and `instanceof` asks whether a particular prototype appears in it.
_Avoid_: parent class, base, superclass, `__proto__`

**Soundness**:
The property of a type system that a passing check guarantees the absence of a class of runtime error. TypeScript declares it a non-goal, so some assignments the compiler accepts are unsafe on purpose, in exchange for accepting the JavaScript people actually write.
_Avoid_: correctness, safety, strictness

**Temporal dead zone**:
The region between the top of a block and a `let` or `const` declaration in it, where the binding exists and reading it throws. It is also what a cyclic module import runs into.
_Avoid_: hoisting error, uninitialised, undefined

**Tuple**:
An array type with a fixed length and a type per position. The length is enforced when the compiler reads an index and not when array methods such as `push` are called, because the value is an ordinary array at run time.
_Avoid_: array, fixed array, record, struct

**Type alias**:
A name bound to an existing type with `type`, which introduces no new type of its own. Two aliases for the same shape are the same type, and an alias never appears in the emitted JavaScript.
_Avoid_: interface, class, new type, wrapper

**Union type**:
A type describing a value that may be any one of several listed types. Before narrowing, only the capabilities every member shares are usable, which is a promise about what the value might be rather than a restriction the compiler invented.
_Avoid_: sum type, optional type, any, variant

**Widening**:
The compiler's replacement of a literal type with its general type where the value could later change, so a `let` initialised with `"a"` becomes `string` while a `const` keeps `"a"`. It is why a literal type sometimes has to be asked for.
_Avoid_: coercion, upcasting, generalisation, type erasure
