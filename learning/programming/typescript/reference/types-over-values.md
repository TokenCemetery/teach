---
title: Types over values
description: What each annotation buys, where inference reaches, and the holes the compiler leaves open on purpose
type: reference
---

# Types over Values

Lookup sheet for stage 2. The question it exists to answer: **what does this annotation promise, and where does the compiler let it slide on purpose?**

## The annotations

| Write | For |
|---|---|
| `string`, `number`, `boolean`, `null`, `undefined`, `symbol`, `bigint` | a primitive |
| `string[]` or `Array<string>` | an array, same type either spelling |
| `[number, string]` | a tuple: fixed length, one type per position |
| `{ name: string; age: number }` | an object shape |
| `age?: number` | optional: key may be absent |
| `age: number \| undefined` | required key, value may be `undefined` |
| `(x: string) => void` | a function value |
| `string \| number` | a union: genuinely either |
| `"low" \| "medium" \| "high"` | a union of literals |
| `any` | switches checking off; a defect, not a convenience |

See [lesson 8](../lessons/0008-the-types-you-write.md) and [lesson 10](../lessons/0010-unions-and-literal-types.md).

## What the compiler checks unasked

TypeScript 7 type-checks strictly with no configuration file. Five flags, including `noImplicitAny` and `strictFunctionTypes`, default to on unless `strict` is explicitly `false`. See [lesson 8](../lessons/0008-the-types-you-write.md).

Two strict-shaped checks are still off by default:

| Flag | Would catch | Taught in |
|---|---|---|
| `noUncheckedIndexedAccess` | an out-of-bounds read typed without `undefined` | [lesson 14](../lessons/0014-what-inference-already-knows.md), named |
| `exactOptionalPropertyTypes` | a `?` property assigned `undefined` | [lesson 8](../lessons/0008-the-types-you-write.md), gap only, unnamed |

## Widening

| Expression | Inferred | Keep the literal by |
|---|---|---|
| `let s = "hello";` | `string` | `const` instead of `let`, or annotate the literal type directly |
| `const s = "hello";` | `"hello"` | already literal |
| `const o = { kind: "a" };` | `o.kind` is `string` | `as const` on the object literal |
| `const o = { kind: "a" } as const;` | `o.kind` is `"a"`, `o` is deeply `readonly` | already literal |

`let` widens because it might be reassigned; a property widens the same way even inside a `const`, since the property itself stays mutable. See [lesson 10](../lessons/0010-unions-and-literal-types.md).

## Assignability verdicts

| Source | Target | Verdict | Why |
|---|---|---|---|
| `{ a: 1, b: 2 }`, a fresh literal | `{ a: number }` | `TS2353` | excess property check, fresh literal only; a real check |
| same value routed through a variable | `{ a: number }` | compiles | structural assignability: "at least" the members needed |
| a `readonly` object | same shape, no `readonly` | compiles | `readonly` not part of object-type assignability; deliberate hole |
| `() => 42` | `() => void` | compiles | `void` means ignored, not "nothing returned"; deliberate hole |
| `(x: string) => void`, as a function-type property | `(x: string \| number) => void` | `TS2322` | contravariant, under `strictFunctionTypes`; a real check |
| the identical narrower parameter, as a method | a method signature of the wider type | compiles | method parameters checked bivariantly; deliberate exemption |

See [lesson 9](../lessons/0009-tuples-and-readonly.md), [lesson 11](../lessons/0011-structural-assignability.md) and [lesson 13](../lessons/0013-function-types.md).

## Narrowing

| Operator | Narrows on |
|---|---|
| `typeof x === "..."` | the primitive tag |
| `x instanceof C` | `C.prototype` in the chain |
| `"k" in x` | property presence, not a runtime tag |
| `x === literalValue` | one member of a literal union |
| truthiness, `if (x)` | every falsy value at once: `false, 0, -0, 0n, "", null, undefined, NaN` |
| early `return` or `throw` | the rest of the function |

| Binding | Lost when | Survives |
|---|---|---|
| local variable | reassigned anywhere later in the function, even after a closure captures it | never reassigned in the function |
| object property (`this.x`) | the read is deferred inside a closure | an arbitrary function call in between |

See [lesson 12](../lessons/0012-narrowing.md).

## Tuples

| Operation | Checked against the declared length |
|---|---|
| index read within the length | yes, typed to that position |
| index read past the length | yes, `TS2493` |
| destructure past the length | yes, `TS2493` |
| `.length` | yes, the literal count, not `number` |
| `.push`, `.pop`, `.splice` | no; array methods, never wired to the tuple's length |

See [lesson 9](../lessons/0009-tuples-and-readonly.md).

## Annotate or not

- Parameter: always, since there is no initialiser to infer from.
- Exported function's return type: annotate, since the signature is a boundary other code depends on.
- Local variable with an initialiser: leave inferred, unless the inferred type is wider than the one you mean to keep.
- Empty collection filled outside one scope, or a return type you want checked against intent rather than the body: annotate.
- Callback parameter already pinned by a declared function type at the call site: leave bare.

See [lesson 14](../lessons/0014-what-inference-already-knows.md) and [lesson 13](../lessons/0013-function-types.md).

## Diagnostics seen in this stage

| `TS` number | Meaning | Usual cause |
|---|---|---|
| `TS7006` | parameter implicitly `any` | bare parameter, no contextual type |
| `TS2322` | not assignable to the target type | widened literal, unhandled `null`/`undefined`, lost narrowing, narrower callback property |
| `TS2741` | required property missing | object literal omits a property the target requires |
| `TS2339` | property does not exist | method missing from a union member, or from a `readonly` array |
| `TS2493` | tuple index outside the declared length | reading or destructuring past the fixed length |
| `TS2540` | cannot assign to a `readonly` property | writing through the readonly-typed name itself |
| `TS2353` | excess property in an object literal | a fresh literal carries a key the target never declared |
| `TS2345` | argument not assignable to the parameter | widened or mismatched argument |
| `TS18047` | possibly `null` | union with `null`, unnarrowed |
| `TS18048` | possibly `undefined` | union with `undefined`, unnarrowed |
| `TS18049` | possibly `null` or `undefined` | union with both, unnarrowed |

## Sources

- [TypeScript Handbook: Everyday Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html)
- [TypeScript Handbook: Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)
- [TypeScript Handbook: Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [TypeScript Handbook: Functions](https://www.typescriptlang.org/docs/handbook/2/functions.html)
- [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals)
- [TSConfig Reference](https://www.typescriptlang.org/tsconfig/)
