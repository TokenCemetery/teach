---
title: 28. interface or type
description: One reports a conflicting member where you wrote it and the other reports it somewhere else
type: lesson
---

# Lesson 28. interface or type

**Mission link:** Choosing `interface` or `type` is a decision every reviewer eventually challenges, and owning a codebase means answering with the one difference that decides it rather than a list of preferences.
**Primary source:** [Declaration Merging, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/declaration-merging.html)
**Prerequisites:** [Lesson 11](0011-structural-assignability.md), [Lesson 26](0026-generics-and-constraints.md)

## Warm-up

1. ▢ Lesson 11 showed `interface Named { name: string }` and `type Named2 = { name: string }` assignable to each other, since assignability compares members rather than names. Given that, do `interface` and `type` differ almost everywhere, or almost nowhere?

<details markdown="1"><summary>Check</summary>

Almost nowhere. The compiler checks shapes, not the keyword that introduced them, so this is mostly one feature with two spellings. The few real differences are what this lesson is about.

</details>

## Know this

### Most of the difference is imaginary

Both `interface` and `type` describe an object shape, checked structurally by lesson 11's rule regardless of keyword, erased completely by run time, and able to take a type parameter exactly as lesson 26 describes for a function. Both can be extended, `interface` with `extends` and `type` with `&`, and one can even extend the other:

```ts
type A = { a: number };
interface B extends A { b: string }
```

This compiles: an `interface` and a `type` alias of an object type are one shape wearing two keywords, and lesson 11's rule looks at the shape, not the keyword. Clearing this away leaves a short list of real differences, and only one of them decides most cases in practice.

### The difference that decides most cases

Build a type by extending another and get a member wrong, and the two forms disagree about when you find out.

```ts
interface A { a: number }
interface B extends A { a: string }
```

```text
error TS2430: Interface 'B' incorrectly extends interface 'A'.
  Types of property 'a' are incompatible.
    Type 'string' is not assignable to type 'number'.
```

Rejected at the declaration, naming the property and both conflicting types. The equivalent with `type` and `&` compiles.

```ts
type A = { a: number };
type B = A & { a: string };
```

No diagnostic. `&` composes rather than checks, and where both sides claim a property, that property's type is the intersection of the two claims: `number & string` has no inhabitants, so `B`'s `a` becomes `never`, and the declaration has nothing wrong with it to report. The trouble surfaces only once something builds a value.

```ts
const b: B = { a: 1 };
```

```text
error TS2322: Type 'number' is not assignable to type 'never'.
```

A `string` gives the identical shape of error. This `never` is not lesson 23's exhaustiveness guard, written on purpose to prove every case of a union was handled; this one arrives uninvited, forced onto a property two conflicting declarations both claimed, and it tells you, late and from the wrong place, that the type cannot be constructed. `interface extends` reports a conflict where you wrote it; `&` reports it later, at whichever call site first builds a value, as a `never` that gives no hint an intersection caused it.

### Declaration merging, and its one real use

Two `interface` declarations with the same name do not conflict; they merge.

```ts
interface I { a: number }
interface I { b: string }
const v: I = { a: 1, b: "x" };
```

Compiles, and `v` needs both members. The same pattern with `type` is refused outright.

```ts
type T = { a: number };
type T = { b: string };
```

```text
error TS2300: Duplicate identifier 'T'.
```

A `type` alias binds a name once; a second binding is a redeclaration, not a contribution. This is the mechanism behind module augmentation, and the reason it exists. Given `export interface Config { host: string }` in one module, a second module can add to that `Config` without owning the first:

```ts
// extra.ts
declare module "./base.js" {
  interface Config { port: number }
}
import { Config } from "./base.js";
const c: Config = { host: "a", port: 1 };
```

Compiles across the two files, and `Config` now needs both members. This is why a library's public types are usually interfaces: a consumer can widen a shape the library owns without forking it. It cuts both ways: a type you did not want extended can be extended the same way, invisibly, away from the declaration that introduced it.

### What only a type can do

A `type` alias can name anything, including things that are not object shapes.

```ts
type U = string | number;
```

Compiles. The equivalent as an `interface` has no syntax at all.

```ts
interface I = string | number;
```

```text
error TS1005: '{' expected.
```

`interface` expects a body of members after the name; it cannot say "one type or another." The same limit rules out a tuple, a plain primitive alias, and, once stage 6 introduces them, a conditional or mapped type: none is an object shape. This usually settles the choice before the extension question above even comes up: if what you are naming is not a shape, `type` is not preferred, it is the only option.

### The decision rule

Four lines, in order; the first that applies wins.

1. If the type is not an object shape, say a union or a tuple, it must be a `type`, because `interface` has no syntax for it.
2. If it is public and other code may need to add to it later without your involvement, prefer `interface`, since only `interface` merges, including declarations written elsewhere via augmentation.
3. If you are building it by extension and want a conflict caught where you introduced it, prefer `interface extends` over `&`.
4. Otherwise either works, and matching what the codebase already does matters more than the choice itself.

A review comment asserting one is always correct is wrong on its face: rule 1 forces `type` where rules 2 and 3 cannot reach, and rules 2 and 3 favour `interface` where rule 1 never touches. The useful comment names which line applies, "this needs to merge across modules, make it an interface", a claim a reviewer can check, rather than a preference.

### Closing stage 4

Lesson 22 narrowed a discriminated union so each branch sees only its own members, against optional fields describing states the domain does not have. Lesson 23 made the compiler enforce their absence, a `never` failing by name when a case is unhandled, a different `never` from the one this lesson produced by accident. Lesson 25 branded a value once its invariant was established, so the type carries proof a check ran. Lesson 26 parameterised a function so the caller's own type returns rather than being widened away. Lesson 27 checked a literal without losing the narrower type actually written. That is the completion criterion this stage opened with: illegal states are unrepresentable, and the compiler proves it. Stage 5 changes the ground under it: every guarantee above assumes a value already has the shape its type claims, and a value arriving from outside the program, a network response, a file, a command-line argument, has not earned that claim yet.

## Practice

1. ▢ Predict the exact diagnostic, with its `TS` number.

   ```ts
   interface A { a: number }
   interface B extends A { a: string }
   ```

<details markdown="1"><summary>Check</summary>

`error TS2430: Interface 'B' incorrectly extends interface 'A'.`, with a further line naming `a` and saying `string` is not assignable to `number`. The conflict is caught at the declaration of `B`.

</details>

2. ▢ Predict whether the declaration below produces an error, and if it does not, predict the exact diagnostic on the line after it.

   ```ts
   type A = { a: number };
   type B = A & { a: string };
   const b: B = { a: 1 };
   ```

<details markdown="1"><summary>Hint</summary>

Ask what `number & string` reduces to, since that is what `B`'s property `a` becomes.

</details>

<details markdown="1"><summary>Check</summary>

No error on the declaration. `B`'s `a` is `number & string`, and nothing is both, so the property's type is `never`. The assignment fails with `error TS2322: Type 'number' is not assignable to type 'never'.`, reported at the construction site rather than at the declaration that caused it.

</details>

3. ▢ Predict whether this compiles, and what happens if both declarations used `type Shape = ...` instead.

   ```ts
   interface Shape { area: number }
   interface Shape { color: string }
   const s: Shape = { area: 4, color: "red" };
   ```

<details markdown="1"><summary>Check</summary>

Compiles as written: the two `interface Shape` declarations merge, needing both `area` and `color`. With `type` instead, the second declaration is a redeclaration rather than a contribution, and the compiler reports `error TS2300: Duplicate identifier 'Shape'.` on both.

</details>

4. ▢ Predict whether `extra.ts` compiles, given `export interface Config { host: string }` in `base.ts`.

   ```ts
   // extra.ts
   declare module "./base.js" {
     interface Config { port: number }
   }
   import { Config } from "./base.js";
   const c: Config = { host: "a", port: 1 };
   ```

<details markdown="1"><summary>Check</summary>

Compiles. The `declare module` block augments the `Config` interface `base.ts` exports, adding `port`, and the merge applies wherever `Config` is used afterwards, so a value needing both members satisfies it. Writing `Config` as a `type` alias in `base.ts` would remove this option, since a `type` cannot be added to from another file.

</details>

5. ▢ A pull request adds `export type Result<T> = { ok: true; value: T } | { ok: false; error: string };`. A reviewer comments, "always use `interface`, it reads clearer." Is that correct, and what should they have said instead?

<details markdown="1"><summary>Check</summary>

Wrong, and not just a matter of taste: `Result<T>` is a union of two shapes, not one, so `interface Result<T> = ...` is not even valid syntax. Rule 1 settles this before rule 2 or 3 is reached. A useful comment would ask whether `Result` needs augmenting from elsewhere, which a union returned from a function normally does not, rather than assert a blanket preference this example already contradicts.

</details>

## Real-world reps

- [ ] Search a codebase you work in for a `type` built with `&` over another named type, and check whether a member could conflict; if the compiler stays silent, construct a value and see whether a property comes back typed `never`.
- [ ] Find a public `interface` in a library you depend on and check its declaration files for more than one declaration of that name, evidence that something is using module augmentation to add to it.
- [ ] Tomorrow: pick one `interface` or `type` choice in code you own, apply the rule from this lesson, and write the one sentence you would give a reviewer who challenges it.

## Going further

- [Declaration Merging, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/declaration-merging.html): the primary source, including the module augmentation pattern this lesson verifies across two files
- [Object Types, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/2/objects.html): the handbook's own treatment of `interface` and `type` as two spellings of an object shape
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
