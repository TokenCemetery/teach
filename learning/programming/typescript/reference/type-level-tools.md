---
title: Type-level tools
description: Which construct computes which type, and the test a clever one has to pass
type: reference
---

# Type-level Tools

Lookup sheet for stage 6. The question it exists to answer: **which construct computes which type, and the test a clever one has to pass?**

## Which construct for which job

| Construct | What it computes | The one-line case for it |
|---|---|---|
| Mapped type | A new object type, one property per key of another type | A "partial update" or "getters" shape that stays in step with its source. See [lesson 36](../lessons/0036-mapped-types.md) |
| Conditional type | A type chosen by an assignability test, decided fresh on each use | A return type that depends on the caller's argument, with nothing left to narrow or assert. See [lesson 37](../lessons/0037-conditional-types.md) |
| `infer` | A blank inside a conditional type's `extends` pattern, bound to whatever matched there | A wrapper's return type that tracks the wrapped function's own, instead of a second type argument. See [lesson 38](../lessons/0038-infer.md) |
| Template literal type | A backtick pattern in type position, each `${...}` holding a type instead of a value | An event name where a typo is rejected at the call, not a handler that silently never fires. See [lesson 39](../lessons/0039-template-literal-types.md) |

The four compose: a template literal type can sit inside a key remapping, and `infer` inside any conditional type's pattern.

## Mapped type syntax

| Form | Written | Effect |
|---|---|---|
| Iteration | `{ [K in keyof T]: T[K] }` | one property per key of `T`, value unchanged |
| Add a modifier | `{ [K in keyof T]?: T[K] }` | every property becomes optional |
| Remove a modifier | `{ -readonly [K in keyof T]-?: T[K] }` | strips `readonly` and `?`; `Required` strips only `-?`, the same trick |
| Key remapping | `` { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] } `` | the key changes; `string & K` guards against a key that is a `number` or `symbol` |
| Filtering | `{ [K in keyof T as Test extends true ? K : never]: T[K] }` | remapping a key to `never` removes it, which is how a mapped type selects rather than only transforms |

See [lesson 36](../lessons/0036-mapped-types.md).

## Conditional types

| Question | Answer |
|---|---|
| Form | `T extends U ? X : Y`, a question about assignability, re-asked at every use rather than declared once |
| `never` as the empty branch | one arm produces nothing; a union that absorbs a `never` member is the same union with that member gone |
| Distribution over a union | a naked type parameter on the left of `extends`, substituted with a union, runs once per member and unions the results back together |
| Switching distribution off | wrap both sides in a one-element tuple, `[T] extends [U] ? X : Y`; the union is then tested once, as a whole |
| Built from exactly this | `Exclude`, `Extract` and `NonNullable`: ordinary conditional types, no separate mechanism |

See [lesson 37](../lessons/0037-conditional-types.md).

## `infer` positions

| Position | Captures | Standard-library type built on it |
|---|---|---|
| Return position, `(...a: never[]) => infer R` | the function's return type | `ReturnType` |
| Parameter list, `(...a: infer P) => any` | the whole parameter list, as a tuple | `Parameters` |
| A promise's inner type, matched recursively | the eventually resolved type | `Awaited`, using `infer` more than once |
| An array pattern, `(infer E)[]` | the element type | not named, same shape |
| A tuple slot, `[infer H, ...unknown[]]`, optionally `infer H extends string` | one element, matched only if it satisfies the constraint | not named; the constraint decides whether the pattern matches |
| A slot inside a template literal, `` `on${infer E}` `` | the captured slice of the string literal | not named, same binding behaviour |

See [lesson 38](../lessons/0038-infer.md).

## Variance

| Position | Variance | Reader-facing consequence |
|---|---|---|
| Return type | covariant | a function returning a narrower type may stand in for one declared to return something wider |
| Function parameter, written as a property | contravariant | a handler narrower than the promised parameter is rejected, `TS2322` |
| Function parameter, written as a method | bivariant | neither narrowing nor widening is caught; a deliberate exemption, not an oversight |
| A type parameter used in both a getter and a setter | invariant | must match exactly, since no direction of substitution is safe for both positions at once |
| Array element type | covariant, and unsound; **this is deliberate** | a narrower array assigned to a wider name can be mutated through that name, and the narrower name then reads a value its own type never promised |
| Variance annotation, `in`, `out`, or both | documents variance the checker already computes | a hint to the checker and to a reader, not a new capability; a wrong claim is caught, at the declaration, as `TS2636` |

See [lesson 40](../lessons/0040-variance-and-assignability.md).

## Signature design

- A type parameter is inferred when it appears in a parameter position the call actually fills, fixing it before the return type is considered.
- A type parameter is not inferred when it appears only in the return position, or the function is called with no arguments; every call then needs it written by hand.
- First signal a signature is wrong: the caller must write the type argument on every call, costing exactly what an explicit cast would have cost.
- Second signal a signature is wrong: a wrong call's error names the type's own machinery, such as an intermediate alias, rather than the caller's mistake.
- `const` on a type parameter moves the cost of keeping a literal type, otherwise `as const` at every call site, into the signature, paid once by the author.

See [lesson 41](../lessons/0041-inference-for-library-apis.md).

## Cost and limits

| Question | Answer |
|---|---|
| How to measure | `tsc --diagnostics` or `--extendedDiagnostics` for a summary; `--generateTrace` to find the responsible type once the summary says something is worth chasing |
| What to read | the instantiation count, not check time; instantiations grow without bound as recursion or a union grows, while check time can stay small for a while |
| The exact ceiling | a tail-recursive tuple-building type compiles at a target length of 999, fails at 1000 with `TS2589`, and the ceiling held again at 1500 |
| Why check time is the weaker argument now | close to half a million instantiations checked in under half a second; "will slow the build down" now needs a `--diagnostics` run behind it |
| The stronger argument | maintenance: a long, truncated error against a clever type costs every reader, whether or not the build itself is fast |

See [lesson 42](../lessons/0042-knowing-when-to-stop.md).

## The stopping test

- Cover the type's definition, look only at where it is used, and say what it evaluates to for a new input, in under a minute.
- Name the caller plainly: a colleague reviewing the change, or the same author in six months, having forgotten today's trick.
- Ask what that caller writes, and what they see when they get it wrong; a signature can satisfy the first and still fail the second.
- If a technique cannot be tied to a caller who writes less, gets a better error, or cannot make a mistake they could otherwise make, it does not earn its place.

See [lesson 41](../lessons/0041-inference-for-library-apis.md) and [lesson 42](../lessons/0042-knowing-when-to-stop.md).

## Diagnostics seen in this stage

| `TS` number | Meaning | Usual cause |
|---|---|---|
| `TS2322` | not assignable | the survivor a conditional type computed, a rejected template literal pattern, or a mismatched `infer` capture |
| `TS2339` | property does not exist | a key remapped to `never`, or a property a filtering mapped type dropped |
| `TS2345` | argument not assignable | a callback narrower than a promised parameter, or a key a conditional type rejected |
| `TS2589` | type instantiation excessively deep | recursion past the compiler's depth limit, exact at 1000 for a tail-recursive tuple build |
| `TS2636` | contradicts a stated variance annotation | `in` or `out` claimed on a generic not actually used that way |
| `TS2741` | required property missing | a mapped type computed from a type that has since grown a field |
| `TS18046` | value is of type `unknown` | a type parameter with nowhere in the call to infer it from |

## Sources

- [TypeScript Handbook, Mapped Types](https://www.typescriptlang.org/docs/handbook/2/mapped-types.html)
- [TypeScript Handbook, Conditional Types](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html)
- [TypeScript Handbook, Template Literal Types](https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html)
- [TypeScript Handbook, Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html)
- [TypeScript Handbook, Keyof Type Operator](https://www.typescriptlang.org/docs/handbook/2/keyof-types.html) and [Indexed Access Types](https://www.typescriptlang.org/docs/handbook/2/indexed-access-types.html)
- [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals)
- [TypeScript wiki, Performance](https://github.com/microsoft/TypeScript/wiki/Performance)
- [TSConfig Reference](https://www.typescriptlang.org/tsconfig/)
