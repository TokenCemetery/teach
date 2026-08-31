---
title: TypeScript
description: "Own a TypeScript codebase: make the compiler reject the states that should not exist"
type: topic
---

# Learning: TypeScript

Become the engineer trusted to own a TypeScript codebase on a team: able to model a domain so the compiler rejects the states that should not exist, keep type assertions out of code that carries weight, validate what crosses a runtime boundary rather than assuming the types held, and review someone's types and say concretely why a clever generic is costing more than it gives.

**Latest lesson:** _none yet_

## Success looks like

- Predict what JavaScript does with coercion, closures, `this` and the event loop, before running the code and without the type system's help.
- Turn a set of illegal states into a type the compiler rejects, and prove exhaustiveness with `never`.
- Read a generic's error message to its cause instead of reaching for `as`.
- Say exactly what survives compilation and what erases, and validate every value entering the program from outside it.
- Configure the compiler with intent: name what each strictness flag buys and why the module and target settings are what they are.
- Write a generic function whose inference works, so callers annotate nothing.
- Publish a package whose types are usable by consumers, including the declaration output and the exports it advertises.
- Review a pull request and say precisely why a conditional type, an assertion, or an `enum` is the wrong tool there.

## Constraints

- Assumes no prior TypeScript, and no more JavaScript than the arc teaches. TypeScript is a type system over JavaScript, so JavaScript semantics are taught wherever they explain the behaviour a type cannot.
- The compile-time and runtime boundary is treated as a hard line throughout, because almost every serious TypeScript mistake is a claim about runtime that only the compiler ever checked.
- Needs only a JavaScript runtime and a terminal on any supported OS, with the online playground standing in for both when a rep only needs to see a type. No paid tooling, no cloud account, no framework.
- Reps are small programs and small type experiments that fit one sitting.
- TypeScript releases every few months and the type system gains real expressiveness in those releases. Version-sensitive claims are checked against the release notes, and any lesson that depends on a version says which one.

## Out of scope

- Frameworks and UI libraries as subjects in their own right: React, Angular, Vue, Svelte, Next.js.
- Bundlers and monorepo tooling as subjects: webpack, Vite, esbuild, Turborepo. Module resolution is taught from the compiler's own model, which is what those tools have to agree with.
- Other runtimes as subjects: Deno, Bun, the browser platform. They appear only where behaviour genuinely differs.
- Node.js as a platform in its own right: streams, clustering, native addons.
- Type-level programming as sport. Mapped and conditional types are taught to the point where they serve a caller, and stage 6 says explicitly where that point is.

## The arc

Seven stages, zero to senior. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
|---|---|---|
| 1. The JavaScript underneath | Values and coercion, objects and prototypes, closures, `this`, modules, the event loop, promises and async | Can predict what a program does at runtime, with no types involved |
| 2. Types over values | Primitives, arrays and tuples, unions, literal types, structural assignability, narrowing, function types, `readonly`, what inference already knows | Annotates only where inference cannot reach |
| 3. Strictness and the compiler | The `strict` family flag by flag, `unknown` versus `any`, assertions versus declarations, `tsconfig`, module resolution, `target` and `lib` | Turns the strict flags on and fixes what appears instead of suppressing it |
| 4. Modelling | Discriminated unions, exhaustiveness with `never`, branded types, generics and constraints, `satisfies`, interface versus type alias | Illegal states are unrepresentable, and the compiler is what proves it |
| 5. The runtime boundary | What erases, declaration files, validating input at the edge, errors as values, consuming untyped and wrongly typed dependencies | No value enters the program unvalidated, and no assertion is load-bearing |
| 6. Type-level tools | Mapped and conditional types, `infer`, template literal types, variance and assignability, inference for library APIs, compiler performance | Writes an API whose types serve its callers, and stops before cleverness |
| 7. Judgment | Publishing a public type surface, what counts as a breaking change in types, review, reading the release notes and the compiler's own declarations | Trusted to make the call and to explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| _none yet_ | | |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources, each annotated with what it covers

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
