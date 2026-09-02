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

**Ambient declaration**:
A `declare` at the top level of a file with no import or export, which adds a name to the global scope rather than to a module's exports. It asserts that something exists without producing it, so nothing audits the claim.
_Avoid_: module declaration, global variable, polyfill, shim

**Annotation**:
A type written explicitly at a variable, parameter or return position, which the compiler checks against what it would have inferred there. It constrains rather than informs: an annotation wider than the inferred type throws information away.
_Avoid_: declaration, type hint, cast

**any**:
A type that switches checking off for the value it is applied to, rather than a type that safely matches everything. It propagates: every expression derived from an `any` is unchecked too, so one of them removes checking from a region rather than from a line.
_Avoid_: wildcard, dynamic, untyped, object

**as const**:
An assertion that keeps a literal at its literal type instead of widening it, and additionally makes arrays and object properties readonly. It changes what the compiler infers and nothing about the value at run time.
_Avoid_: freeze, immutable, constant

**Assertion function**:
A function whose return type is `asserts x is T`, which narrows its argument for everything after the call rather than inside a branch. Its body is not checked against the claim, and the compiler requires the call target to have an explicit type annotation.
_Avoid_: type predicate, validator, guard, assert statement

**Bivariant**:
A position the compiler accepts in either direction, rejecting neither the wider nor the narrower type. A method's parameter is checked this way while the same parameter written as a function-typed property is not, which is a deliberate exemption rather than general looseness.
_Avoid_: covariant, contravariant, any, loose typing

**Branded type**:
A primitive intersected with an object type carrying a property no runtime value has, so that two otherwise identical primitives stop being interchangeable. It gives nominal typing in one direction only: the value flows out to the underlying type freely and cannot flow in without an assertion.
_Avoid_: wrapper type, tagged type, newtype, validated type

**Breaking change**:
An edit that stops a consumer's existing code from compiling or running against a new version of your package, decided by what a caller can still write rather than by how large the edit looks. Renaming a type of identical shape breaks an import while replacing a whole implementation may break nothing.
_Avoid_: major version, refactor, incompatible change, regression

**Closure**:
A function together with the scope it was created in, which stays reachable after the enclosing function returns. It captures the binding rather than a copy of the value, which is why a `var` loop variable gives every callback the same final value.
_Avoid_: callback, capture, lambda

**Coercion**:
The implicit conversion an operator performs on its operands before comparing or combining them. `==` and `+` both do it, `===` does not, and the conversions are specified rather than intuitive.
_Avoid_: casting, conversion, parsing

**Conditional type**:
A type of the form `T extends U ? X : Y`, where `extends` asks about assignability rather than about inheritance. It is how a type branches, and `never` is how a branch produces nothing.
_Avoid_: type guard, ternary, overload, union

**const type parameter**:
A type parameter declared `const`, which preserves the literal types and readonly-ness of what the caller passed without the caller writing `as const`. It moves the decision from every call site to the signature.
_Avoid_: const declaration, as const, readonly, literal type

**Constraint**:
The `extends` clause on a type parameter, stating the minimum a substitution must satisfy. It is what lets the body use a member at all, and it should be sized to what the body actually needs rather than to what the caller happens to pass.
_Avoid_: bound, restriction, interface requirement, base class

**Contextual typing**:
The type an expression receives from the position it appears in, such as a callback taking its parameter types from the signature it is passed to. It flows a type inwards, where inference reads one outwards, which is why a well-typed callback needs no annotation at all.
_Avoid_: inference, narrowing, duck typing

**Contravariant**:
A position that may travel only in the opposite direction to its container, so a wider type is accepted where a narrower one was promised. A function-typed parameter is checked this way, because a function must accept everything its type says it accepts.
_Avoid_: covariant, bivariant, inverted, reversed

**Control-flow analysis**:
The compiler's tracking of what a value's type must be at each position, given the branches taken to reach it. A type is therefore a property of a position in the code rather than of a declaration.
_Avoid_: type inference, static analysis, data flow

**Covariant**:
A position that may travel only in the same direction as its container, so a narrower type is accepted where a wider one was promised. A return type is checked this way; an array is too, which is unsound and deliberate.
_Avoid_: contravariant, bivariant, subtype, assignable

**Declaration file**:
A `.d.ts` holding types with no implementation, which produces no output and which the compiler takes entirely on trust. One written by hand for code you do not own is a promise nothing verifies; one generated from your own source cannot disagree with it.
_Avoid_: type definition, header file, interface file, stub

**Declaration merging**:
Two declarations of the same interface name combining into one shape, which `type` cannot do. Its real purpose is module augmentation rather than convenience within a file.
_Avoid_: module augmentation, overloading, inheritance, redeclaration

**Discriminant**:
The property every arm of a union carries, holding a distinct literal type in each, so that one equality check narrows the union to a single arm. It has to be a literal type: once it widens to `string`, narrowing on it stops working.
_Avoid_: tag, flag, type field, discriminated union

**Distributive conditional type**:
A conditional type whose checked type is a naked type parameter, which makes the compiler split a union, test each member separately and rejoin the results. Wrapping the check in a tuple turns it off, and the choice between the two is deliberate rather than incidental.
_Avoid_: union, mapped type, iteration, broadcast

**Double assertion**:
The `as unknown as T` form, used to reach a type that a single `as` refuses because the two types do not sufficiently overlap. It is a statement that you have read the compiler's objection and would like it set aside, so seeing one is a request for an explanation rather than a matter of style.
_Avoid_: cast, conversion, coercion, type guard

**Emit**:
The JavaScript the compiler writes out, as distinct from the checking it performs. `target` changes it and the type system does not depend on it, which is why the same source can type-check identically and produce different output.
_Avoid_: compile, build, transpile, output type

**Erasure**:
The removal of everything type-only when the compiler emits JavaScript, so annotations, interfaces, type arguments, assertions and brands are all gone before any value arrives. It is a stated design goal rather than a limitation, and it is why a type cannot check anything at run time.
_Avoid_: compilation, minification, stripping, transpilation

**Excess property checking**:
The check that rejects members a target type does not declare, firing only when a fresh object literal is assigned or passed directly to a typed position. It is not part of structural assignability and is defeated by routing the same object through a variable.
_Avoid_: strict object checking, structural assignability, exact types

**Exhaustiveness check**:
A compile-time proof that every member of a union has been handled, obtained by assigning whatever is left to `never` in a `default` or final `else`. Its value is that adding a member to the union then fails at every site that ignored it, and the diagnostic names the member.
_Avoid_: default case, validation, switch coverage, assertion

**Falsy**:
A property of a value rather than of a comparison: `false`, `0`, `-0`, `0n`, `""`, `null`, `undefined` and `NaN` all test false in a condition. Every other value tests true, including `[]`, `{}` and `"0"`.
_Avoid_: empty, null, unset, invalid

**infer**:
A name declared inside a conditional type's `extends` clause, which the compiler fills in from whatever matched that position and which is usable in the true branch. It is how a type is extracted from a shape rather than supplied by a caller.
_Avoid_: generic, inference, destructuring, extract

**Invariant**:
A position where neither direction is safe, so only an exact match is accepted. It has nothing to do with immutability or with an invariant in the sense of a rule a value must satisfy.
_Avoid_: readonly, immutable, constant, exact

**Key remapping**:
The `as` clause inside a mapped type, which renames the key being produced or, by producing `never`, removes it. Remapping to `never` is how a mapped type selects rather than only transforms.
_Avoid_: rename, alias, index signature, pick

**Literal type**:
A type inhabited by exactly one value, such as `"circle"` or `42`, most useful as one member of a union. It is what makes a union able to say which strings are allowed rather than only that a string is allowed.
_Avoid_: enum, constant, string literal, value type

**Live binding**:
The relationship an `import` creates with the exporting module's declaration, so a later change in that module is visible through the import. CommonJS destructuring copies a value instead, which is why the two disagree about a counter.
_Avoid_: reference, alias, shared state

**Mapped type**:
A type built by iterating another type's keys, written `[K in keyof T]`, optionally adding or removing the `readonly` and optional modifiers. It keeps a derived type in step with its source, so the source gaining a property is a compile error wherever that was not handled.
_Avoid_: generic, index signature, iteration, transform

**Microtask**:
Work queued by a promise reaction or an `await` continuation, drained completely before the next task runs. That priority is why a promise callback always precedes a zero-delay timer.
_Avoid_: tick, job, callback, async task

**Module augmentation**:
Adding members to an interface another module owns, by declaring it again inside `declare module`. It is the reason interfaces merge at all, and the reason a library's public types are usually interfaces rather than aliases.
_Avoid_: declaration merging, monkey patching, inheritance, overriding

**Module declaration**:
A `declare module "specifier"` block, which supplies types for exactly the import string it names. It is scoped to that specifier rather than to the global scope, and with an empty body it types the whole module `any`.
_Avoid_: ambient declaration, module augmentation, namespace, import alias

**Module resolution**:
The process of turning an import specifier into a particular file, decided by `moduleResolution` together with the nearest `package.json`. It is a separate question from what `module` controls, which is only the import syntax that gets emitted.
_Avoid_: module, import, bundling, path mapping

**Narrowing**:
A type refinement the compiler derives from a condition, valid only at positions reachable through that branch. It is lost when a local is reassigned anywhere afterwards, and when a property's use is deferred into a closure.
_Avoid_: casting, assertion, type guard, validation

**never**:
The type with no values, which is why nothing is assignable to it. That makes it useful deliberately, as the assertion behind an exhaustiveness check, and it also appears accidentally, as the property type left by an intersection of two conflicting members.
_Avoid_: void, undefined, unknown, any

**Nominal typing**:
Assignability decided by declared identity rather than by shape. TypeScript is structural and does not have it, which is why obtaining it requires the deliberate trick a branded type performs.
_Avoid_: structural typing, class identity, instanceof, sealed type

**Own property**:
A property stored on the object itself, as opposed to one found on its **prototype**. Reads walk the prototype chain and writes always create an own property, which is why assigning to an inherited property shadows it rather than changing it.
_Avoid_: instance field, local property, direct property

**Parameter property**:
A constructor parameter carrying a visibility modifier, which the compiler expands into a field declaration and an assignment nothing in the source wrote. It generates run-time code, which is why `erasableSyntaxOnly` refuses it.
_Avoid_: shorthand constructor, field, initialiser, sugar

**Phantom property**:
A member that exists only in a type and is never present on any value, used to change assignability rather than to hold data. It cannot be checked at run time, so it records that a check happened rather than performing one.
_Avoid_: marker, metadata, hidden field, symbol

**Prototype**:
The object a property lookup falls back to when the property is not an own property, forming a chain that ends at `null`. `class` syntax builds one, and `instanceof` asks whether a particular prototype appears in it.
_Avoid_: parent class, base, superclass, `__proto__`

**Reverse mapping**:
The value-to-name direction an `enum` builds into its emitted object, so that a numeric member can be looked up as `Colour[0]`. Nothing in the source asks for it and an object literal never produces it, so it is a run-time cost carried whether or not the code reads it.
_Avoid_: lookup, index signature, forward mapping, key access

**satisfies**:
An operator that checks an expression against a type without replacing the expression's own inferred type, which is what an annotation does instead. It is the same check as an annotation without the widening, and unlike `as` it does not switch the check off.
_Avoid_: assertion, cast, annotation, type guard

**Schema**:
A value that describes a shape and can both check a runtime value against it and yield the static type of what it accepts. Because one declaration produces the check and the type, the two cannot drift apart, which is the property that distinguishes it from a type plus a separate hand-written check.
_Avoid_: type, interface, validator, model

**Soundness**:
The property of a type system that a passing check guarantees the absence of a class of runtime error. TypeScript declares it a non-goal, so some assignments the compiler accepts are unsafe on purpose, in exchange for accepting the JavaScript people actually write.
_Avoid_: correctness, safety, strictness

**Standard decorator**:
The calling convention from the ECMAScript decorator proposal, which the compiler implements by default. It is a different dialect from the pre-standard convention behind `experimentalDecorators`, sharing only the `@` syntax, so enabling that flag breaks code written for this one.
_Avoid_: decorator, annotation, legacy decorator, attribute

**Strict family**:
The named group of checking options that `strict` enables together. It is a set rather than a level, each member can be switched off on its own, and the membership grows between releases, so `strict: true` does not mean the same thing across versions.
_Avoid_: strict mode, level, preset, linting

**Suppression comment**:
A directive that hides a diagnostic on the following line, either `@ts-ignore` or `@ts-expect-error`. Only the second is reported when the error it suppresses goes away, so only the second cannot rot silently.
_Avoid_: assertion, disable, lint rule, pragma

**Template literal type**:
A type written with backtick interpolation that describes a shape of string rather than one string, and which the compiler checks a literal against. It composes with `infer` and with a mapped type's key remapping, and interpolating unions multiplies out, which is where it gets expensive.
_Avoid_: template string, string interpolation, regular expression, pattern

**Temporal dead zone**:
The region between the top of a block and a `let` or `const` declaration in it, where the binding exists and reading it throws. It is also what a cyclic module import runs into.
_Avoid_: hoisting error, uninitialised, undefined

**Tuple**:
An array type with a fixed length and a type per position. The length is enforced when the compiler reads an index and not when array methods such as `push` are called, because the value is an ordinary array at run time.
_Avoid_: array, fixed array, record, struct

**Type alias**:
A name bound to an existing type with `type`, which introduces no new type of its own. Two aliases for the same shape are the same type, and an alias never appears in the emitted JavaScript.
_Avoid_: interface, class, new type, wrapper

**Type parameter**:
A name in a signature standing for a type supplied or inferred at the call site, which ties positions in that signature together. It earns its place only when the caller learns something from it, so one appearing exactly once should usually be a concrete type instead.
_Avoid_: generic, placeholder, template, wildcard

**Type predicate**:
A return type of the form `x is T`, which makes a function usable as a narrowing operator. The compiler never checks the body against the claim, so it is an assertion in a function signature and inherits the same standard.
_Avoid_: type guard, validator, assertion function, check

**Type surface**:
Every type a package's exported signatures expose to a consumer, including a type that is merely mentioned and never exported. A signature naming an internal type puts that type's shape in the surface, whatever the export statements say.
_Avoid_: exports, public API, declaration file, type definitions

**Type-only import**:
An import written with `import type` or an inline `type` specifier, which is erased and emits no run-time import. Making it explicit is what lets the emitted import statements be exactly what was written, rather than depending on whether the compiler could tell a name was a type.
_Avoid_: import, side-effect import, dynamic import

**Union type**:
A type describing a value that may be any one of several listed types. Before narrowing, only the capabilities every member shares are usable, which is a promise about what the value might be rather than a restriction the compiler invented.
_Avoid_: sum type, optional type, any, variant

**unknown**:
A type that accepts any value on the way in and permits no operation on it until it has been narrowed. It is the honest type for a value nothing has established anything about yet, and it differs from `any` precisely by refusing the way out.
_Avoid_: any, object, mixed, untyped

**Widening**:
The compiler's replacement of a literal type with its general type where the value could later change, so a `let` initialised with `"a"` becomes `string` while a `const` keeps `"a"`. It is why a literal type sometimes has to be asked for.
_Avoid_: coercion, upcasting, generalisation, type erasure
