---
title: 34. Declaration Files
description: Types for code the compiler never sees, and what that promise is worth
type: lesson
---

# Lesson 34. Declaration Files

**Mission link:** Nearly every dependency in a real project is typed by a file the compiler trusts unchecked, and owning a codebase means knowing which of three ways that file came to exist and how far to trust it.
**Primary source:** [Handbook, Declaration Files](https://www.typescriptlang.org/docs/handbook/declaration-files/introduction.html)
**Prerequisites:** [Lesson 29](0029-nothing-survives-to-run-time.md), [Lesson 21](0021-module-resolution.md)

## Warm-up

1. ▢ Lesson 29 put `declare` in the same category as an assertion, a claim the compiler accepts with no evidence behind it. An assertion makes that claim about one value. What does a `declare module` statement make the claim about, and why does it matter more when the module belongs to a dependency rather than to your own code?

<details markdown="1"><summary>Check</summary>

A `declare module` statement claims a shape for an entire module's exported surface at once, every function, its parameters and its return type, not just one value. It matters more for a dependency because nobody who reads your code wrote that claim, and in the common case nobody who reads it can even see the implementation it is supposed to describe; the compiler trusts it exactly as it trusts any other `declare`, and there is nothing further behind the trust.

</details>

## Know this

### What a .d.ts is

A file ending `.d.ts` contains a `declare` for everything in it and nothing else: a function with a signature and no body, a variable with a type and no initialiser, a module with a list of exports and no code behind any of them. Feed one to `tsc` on its own and there is nothing to emit, because there was never an implementation to turn into JavaScript; a declaration file is pure input to checking and never output from it. Lesson 29 named `declare` as a claim taken on trust; a `.d.ts` is that claim at its widest scope, an entire file of assertions about a program the compiler will never see, usually about code that is not even TypeScript.

### Where declarations come from

A reader importing a package that is not written in TypeScript, or that ships nothing useful, meets exactly three situations. First, the package includes its own declarations, either hand-written alongside its JavaScript or produced automatically because the package is itself built from TypeScript (below); nothing further is needed. Second, the package ships no types of its own but a separate `@types` package on npm supplies them; installing it is enough, because resolving `import x from "pkg"` already falls back to `@types/pkg` automatically, through the same module resolution lesson 21 covered, with no configuration line asking for this by name. Third, nobody has written any declarations at all, not in the package and not as a separate `@types` package, and the rest of this lesson is about that case.

One setting is easy to confuse with the second case, and should not be. Lesson 19 established that `types` now defaults to `[]`, so an `@types` package is no longer pulled into every file automatically unless it is named there. That default governs a narrower thing than resolving a typed dependency: which `@types` packages contribute declarations nobody imports, such as a test framework's global `describe` and `it`, to every file regardless of whether that file asks for them. An `@types` package backing an actual import is found by the same resolution that finds the package it types, and needs no entry in `types` at all. Confusing the two means looking at the wrong setting when a global goes missing, and the right one when an import fails.

### The verified failure and its fix

Take a package called `legacy-thing`, plain JavaScript, in the third case above: no declarations of its own and no `@types` package behind it. `main.ts` writes `import { shout } from "legacy-thing";` and calls it. Running `tsc` reports:

```text
src/main.ts(1,23): error TS7016: Could not find a declaration file for module 'legacy-thing'. '.../node_modules/legacy-thing/index.js' implicitly has an 'any' type.
  Try `npm i --save-dev @types/legacy-thing` if it exists or add a new declaration (.d.ts) file containing `declare module 'legacy-thing';`
```

The message names both remaining options itself. No `@types/legacy-thing` exists, so write the declaration. Placed at `src/legacy-thing.d.ts`, inside the files the project's `include` actually reaches, since a `.d.ts` sitting outside that set is invisible to the compiler and leaves `TS7016` exactly as it was:

```ts
declare module "legacy-thing" {
  export function shout(s: string): string;
}
```

Run `tsc` again and it compiles clean.

Read the message's second suggestion twice before taking it at face value. `declare module 'legacy-thing';`, with no body at all, also silences `TS7016`, and it is tempting because it is one line instead of three. It does not describe the module, it exempts it: every name imported from `legacy-thing` becomes `any`, so `shout`, whatever else the package exports, and even a misspelled import name all pass unchecked and stay unchecked through everything built from them. That is lesson 17's fact about `any` propagating past the line it was written, met again at the scale of a dependency instead of one variable. Writing the real signature costs a few more minutes and buys a check somewhere instead of nowhere.

### Writing a declaration for a dependency you do not own

Two things decide whether a hand-written `.d.ts` is worth the minutes it costs. Where it sits: it must be part of the program the compiler actually builds, matched by `include` or `files` the way lesson 19 described, or an import into it counts for nothing. What it claims: a `declare module "name" { ... }` block attaches its exports to one specifier only, scoped exactly as narrowly as the dependency it describes, unlike the global declarations the next section covers.

The discipline worth keeping, rarely stated because it sounds like cutting corners and is not: declare only the exports you actually call. The compiler never checks a module declaration for completeness against the real package, so a `.d.ts` naming three functions out of a library's forty compiles as cleanly as one naming all forty, for a fraction of the effort. Reach for a name the declaration omits and the compiler says exactly when, `error TS2305: Module '"legacy-thing"' has no exported member 'whisper'.`, at the call site that needs it, a far better moment to add one line than guessing the whole surface up front and getting some corner of it wrong.

### Ambient declarations for things that are not modules

Not everything a declaration describes sits behind an `import`. A script tag puts a value on the page before any module runs, or a build step bakes a constant into the bundle, and both need a name the compiler will accept without an import bringing it in. A `.d.ts` file with no `import` or `export` at its own top level is read as a global script rather than a module, and anything it declares there joins the global scope everywhere in the program:

```ts
declare const __BUILD_VERSION__: string;
```

Written once, `__BUILD_VERSION__` type-checks anywhere in the project with no import at all, exactly as if some earlier line had defined it, because as far as the compiler can tell, some earlier line did. It is the same unaudited promise as a `declare module`, only unscoped: nothing here says a build tool will actually define this constant, only that the compiler will believe it if you say so.

### Declaring types for your own code

Your own code rarely needs a hand-written `.d.ts`, because the compiler writes one for you. Setting `declaration: true`, already active in the configuration `tsc --init` generates, produces a `.d.ts` alongside every emitted `.js`, derived from the source rather than composed separately from it:

```ts
export function shout(s: string): string {
  return s.toUpperCase();
}
```

```ts
export declare function shout(s: string): string;
```

The second block is what the compiler wrote from the first. It cannot disagree with the implementation, because it was never an independent claim, only the implementation's own signature copied out. That is the contrast worth carrying forward: a generated declaration is checked against something, the source it came from, and a hand-written one for someone else's code is not checked against anything at all.

### What the promise is worth

A declaration is exactly as good as whoever wrote it, and nothing in the compiler distinguishes a careful one from a careless one; both compile identically, because compiling only confirms that shapes agree with each other, never that either shape agrees with what actually runs at the far end of an import. The next lesson shows what that costs when one is simply wrong.

## Practice

1. ▢ A project imports `parse` from a package called `oldparser`, plain JavaScript, with no declarations shipped and no `@types/oldparser` on npm. Predict the exact diagnostic `tsc` reports, with its `TS` number.

<details markdown="1"><summary>Check</summary>

`error TS7016: Could not find a declaration file for module 'oldparser'. '.../node_modules/oldparser/index.js' implicitly has an 'any' type.`, and the message itself suggests installing `@types/oldparser` if it exists or writing a `.d.ts` containing `declare module 'oldparser';`.

</details>

2. ▢ Someone fixes the above by adding a real `declare module "oldparser" { ... }` block, but places the file at the project root, outside the `src` directory named in `include`. Predict whether the error still appears.

<details markdown="1"><summary>Hint</summary>

Ask where the compiler actually looks, not just whether the file exists somewhere on disk.

</details>

<details markdown="1"><summary>Check</summary>

Yes, `TS7016` is unchanged. A `.d.ts` that sits outside the files `include` reaches is invisible to the compiler, exactly as if it did not exist; only moving it inside the included set, or naming its location in `include`, fixes the error.

</details>

3. ▢ Predict what happens once `declare module "oldparser";`, with no body, is added somewhere inside the included files instead, and say what it does to a call like `parse(42).nonexistentMethod()`.

<details markdown="1"><summary>Check</summary>

Both compile with no diagnostic. The bare declaration does not describe `oldparser`, it exempts it: every name imported from it, including `parse`, becomes `any`, so a call, a property read that does not exist, and anything built from the result all pass unchecked. This is lesson 17's fact about `any` propagating past the line it was written, arriving here through a dependency instead of a variable.

</details>

4. ▢ A hand-written declaration says `declare module "oldparser" { export function parse(s: string): unknown; }`. A caller writes `import { parse, stringify } from "oldparser";`. Predict the diagnostic.

<details markdown="1"><summary>Check</summary>

`error TS2305: Module '"oldparser"' has no exported member 'stringify'.` The declaration only ever claimed `parse`; naming `stringify` at the one call site that needs it is the moment to add one more line, not evidence the whole declaration was wrong to write that way in the first place.

</details>

5. ▢ A teammate says, "our `tsconfig.json` sets `types` to `[]`, so we can never rely on an `@types` package, we have to hand-write a declaration for every dependency." Is that right?

<details markdown="1"><summary>Check</summary>

No. `types: []` only stops `@types` packages that contribute declarations nobody imports, globals such as a test framework's `describe` and `it`, from loading automatically. A dependency that is actually imported, `import x from "pkg"`, still resolves its types through `@types/pkg` if that package exists, through the same resolution that finds `pkg` itself; `types` never enters into it. Hand-writing a declaration is only needed for the third case this lesson covers, a dependency with no types of its own and no `@types` package either.

</details>

## Real-world reps

- [ ] Import a dependency in a project you use that ships no declarations and has no `@types` package behind it, and read the exact `TS7016` it produces before writing anything to fix it.
- [ ] Find a hand-written `.d.ts` in a project you work in, whether yours or a dependency's, and check whether it declares more of the module's surface than anything in the project actually calls.
- [ ] Tomorrow: pick one dependency you import and decide, before checking, which of the three cases supplies its types, then confirm it by reading its `package.json` and looking for it under `node_modules/@types`.

## Going further

- [Handbook, Declaration Files, By Example](https://www.typescriptlang.org/docs/handbook/declaration-files/by-example.html): worked examples of writing a `.d.ts` for common JavaScript shapes
- [TSConfig Reference, `declaration`](https://www.typescriptlang.org/tsconfig/#declaration): the flag that generates a `.d.ts` from your own source instead of asking you to write one
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
