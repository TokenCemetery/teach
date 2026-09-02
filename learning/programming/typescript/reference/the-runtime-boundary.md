---
title: The runtime boundary
description: Where values enter, what checks them, and which claims nothing checks at all
type: reference
---

# The Runtime Boundary

Lookup sheet for stage 5. The question it exists to answer: **what actually checks a value crossing into your program, and what only claims to?**

## What erases and what remains

Every type is a claim checked against a program that is then thrown away, so nothing written at the type level is present once the program runs. See [lesson 29](../lessons/0029-nothing-survives-to-run-time.md).

| Erases | Remains |
|---|---|
| `interface` and `type` declarations | function and class declarations, since both are values as well as types |
| a generic type argument, such as `<number>` | the argument and return value actually passed |
| `as`, `as unknown as`, `!`, `satisfies` | the bare expression each one wrapped |
| a brand's phantom property | the primitive or object the brand was attached to, unmarked |
| `import type { X }` | a value import that is actually used, such as `import { f }` |
| `declare const x: T` | nothing; `declare` never produces a binding at all |

The one exception is `instanceof`, which keeps working after compilation because a class's constructor has to exist at run time for the class to work as JavaScript at all. It tests only that the object came from that constructor, not that the constructor's parameters were what their types claimed. See [lesson 29](../lessons/0029-nothing-survives-to-run-time.md).

## The edges

A boundary is any point where a value enters the program from somewhere the compiler never checked. This table is the full inventory. See [lesson 30](../lessons/0030-unknown-at-the-edge.md).

| Entry point | What its declaration claims | What it can actually give you |
|---|---|---|
| `JSON.parse` | `any` | any shape at all, since `any` stops checking rather than describing |
| a network response body, such as `res.json()` | `Promise<any>`, the same lie one layer further from the call site | any shape at all |
| reading a file | `string` or `Buffer`, and genuinely one of those | a real string or buffer with no guarantee it holds valid JSON or a well-formed configuration |
| an environment variable | `string \| undefined`, already honest | the same, unless an assertion such as `as string` silences the check the declaration was giving for free |
| a command-line argument | `string`, for a fixed index | `string`, present or not; index `5` on a two-element array is `undefined` typed as `string` |
| a `catch` variable | `unknown`, enforced by the language itself | anything at all, since `throw` accepts anything |
| a callback invoked by a third party | whatever parameter types you or the library declared | whatever the invoker actually chooses to pass; the declaration is a request, not an inspection |
| a database or message-queue payload | whatever generic or row type you supplied yourself | whatever the row actually contains now, which the compiler cannot check against a live schema |

## Checked or claimed

Six shapes make a claim about a value's type. This is the whole stage reduced to one table: only one of the six is verified by anything at all.

| Claim | Anything verifies it | Where the failure surfaces if wrong |
|---|---|---|
| a parse, `.parse` or `.safeParse` | Yes; the call tests the value field by field before returning. See [lesson 31](../lessons/0031-parsing-instead-of-asserting.md) | at the parse call itself, immediately, as a thrown error or a `success: false` result |
| a type predicate, `x is T` | No; the compiler reads the claim off the signature and never compares it against the body. See [lesson 32](../lessons/0032-type-predicates-and-assertion-functions.md) | later, wherever the branch that trusted the narrowing performs an operation the real value cannot support |
| an assertion function, `asserts x is T` | The compiler requires the claim to sit on an explicit declaration, refusing an inferred `const` with `TS2775`, but nothing compares the body against the claim either. See [lesson 32](../lessons/0032-type-predicates-and-assertion-functions.md) | wherever code after the call relies on the narrowed type, for the rest of the enclosing scope |
| `as` | No; an assertion changes what the compiler believes, not what is true. See [lesson 29](../lessons/0029-nothing-survives-to-run-time.md) | wherever the value is next used in a way the claimed type allows but the actual value cannot support |
| `!` | No; it removes `null` and `undefined` from the type without checking that the value is actually present. See [lesson 29](../lessons/0029-nothing-survives-to-run-time.md) | the next operation performed on the value, if it was genuinely absent |
| a declaration file | No; the compiler treats it as ground truth and never checks it against the implementation it describes. See [lesson 34](../lessons/0034-declaration-files.md) and [lesson 35](../lessons/0035-when-the-declaration-lies.md) | at run time, at the first operation that assumes the declared shape, wherever that call site happens to be |

## Schema to types

| Call | Gives you |
|---|---|
| `Schema.parse(raw)` | the parsed, typed value, or throws |
| `Schema.safeParse(raw)` | a discriminated union keyed on `success`, holding either `data` or a structured `error` whose `path` names the field that failed |
| `z.infer<typeof Schema>` | the output type: the shape after parsing, with every default already filled in |
| `z.input<typeof Schema>` | the input type: the shape you may hand in, with any defaulted field left optional |

`z.infer` and `z.input` are identical wherever a schema has no `.default()` or transform, and diverge on exactly the fields that carry one. Using `z.infer` for a value on its way in, rather than one already parsed, is a real bug and it still type-checks, since the missing field is only enforced by the type, and only once it is annotated correctly. See [lesson 31](../lessons/0031-parsing-instead-of-asserting.md).

## Where a failure should live

1. Return a value when the failure is an expected, nameable outcome of the operation. The test: can the immediate caller do something different depending on which failure occurred. See [lesson 33](../lessons/0033-errors-as-values.md).
2. Throw when the failure is a programmer error the immediate caller cannot sensibly act on, or an invariant already broken, since continuing would compute a wrong answer from a state nobody reasoned about. See [lesson 33](../lessons/0033-errors-as-values.md).
3. Throw also at a genuine top-level boundary, a place where something above will catch whatever comes up and turn it into a response, a log line or an exit code, with nothing below needing the specific shape of what went wrong. See [lesson 33](../lessons/0033-errors-as-values.md).
4. Wherever a returned failure needs a `never` guard to force every caller to handle every case, type it as literal kinds, not `Error` or a plain `string`; a `string` carries no structure for that guard to check. See [lesson 33](../lessons/0033-errors-as-values.md).

## Declarations

| Source | What it is worth |
|---|---|
| bundled with the package, hand-written by its author or generated from the package's own TypeScript source | as good as the author's diligence; a generated one cannot disagree with the implementation, since it was copied from it rather than written independently |
| a separate `@types` package on npm | written and updated by someone other than the library's author, versioned on its own schedule; worth checking that its major version still tracks the library's |
| hand-written by you, for a dependency that ships no declarations and has no `@types` package behind it | worth exactly the care taken writing it; declaring only the exports actually called keeps the promise small and cheap to keep honest |

See [lesson 34](../lessons/0034-declaration-files.md).

## skipLibCheck

| What it does | What it is widely believed to do |
|---|---|
| checks whether the inside of a `.d.ts` file is internally consistent with itself | verifies that a declaration's claim matches the implementation it describes |

Verified with a lying declaration in place: the project reports zero errors with the flag off and zero with it on, because the flag never had access to the implementation to check the declaration against. Reaching for it expecting the second behaviour is a common and expensive misunderstanding. See [lesson 35](../lessons/0035-when-the-declaration-lies.md).

## Diagnostics seen in this stage

| `TS` number | Meaning | Usual cause |
|---|---|---|
| `TS1196` | catch clause variable type annotation must be `any` or `unknown` | a specific type named on `catch` |
| `TS2305` | module has no exported member | calling a name a hand-written declaration never listed |
| `TS2322` | not assignable | an unchecked environment variable, a `never` guard receiving an unhandled failure shape, or an output type missing a field a default has not yet supplied |
| `TS2339` | property does not exist | reading a field a schema, or a union arm, never declared |
| `TS2366` | function lacks an ending return statement | a `switch` with no `default` and no `never` guard, under a non-`void` return type |
| `TS2741` | required property missing | a schema's output type used for a value still on its way in, before a default has run |
| `TS2775` | assertions require every name in the call target to have an explicit type annotation | an assertion function assigned to a `const` without repeating its signature |
| `TS7016` | could not find a declaration file for a module | importing an untyped package with no declarations and no `@types` package |
| `TS18046` | value is of type `unknown` | used before narrowing, including a value narrowed by `in` but not yet by `typeof` |

## Sources

- [TypeScript Handbook: Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [Handbook, Declaration Files, Introduction](https://www.typescriptlang.org/docs/handbook/declaration-files/introduction.html)
- [Handbook, Declaration Files, By Example](https://www.typescriptlang.org/docs/handbook/declaration-files/by-example.html)
- [Zod documentation](https://zod.dev/)
- [TSConfig Reference](https://www.typescriptlang.org/tsconfig/)
- [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals)
- [Effective TypeScript](https://effectivetypescript.com/)
- [Node.js documentation, `process.env`](https://nodejs.org/api/process.html#processenv)
