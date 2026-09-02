---
title: 43. What Counts as a Breaking Change
description: Which edits to a published type break a consumer, and which direction each one has to travel
type: lesson
---

# Lesson 43. What Counts as a Breaking Change

**Mission link:** Owning a TypeScript codebase means the types you publish are a promise to consumers you will never watch edit their own code, so knowing which edits keep that promise and which quietly break it is what turns a version bump from a guess into a claim you can defend.
**Primary source:** [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals)
**Prerequisites:** [Lesson 41](0041-inference-for-library-apis.md), [Lesson 40](0040-variance-and-assignability.md)

## Warm-up

1. ▢ Lesson 40 named the two directions a function's own signature travels: a parameter is contravariant, a return type is covariant. A published function's signature changes between one version and the next, from `handle(x: string): void` to `handle(x: string | number): void`. Which direction did the parameter travel, and does an old call written as `handle("a")` still compile against the new version?

<details markdown="1"><summary>Check</summary>

The parameter widened, from `string` to `string | number`, the safe contravariant direction: the function now accepts everything it used to, plus more, so `handle("a")` still compiles, and a new call such as `handle(42)` compiles too, where before it could not. The opposite edit, narrowing back down to `string`, travels the unsafe direction and rejects exactly the calls that used to pass a number. This lesson turns that single case into the whole map: every edit to a published type is a question about which direction it moved, and lesson 40's four words already answer it.

</details>

## Know this

### The test, and what a version number records

Every question below reduces to one test: an edit to a published type is safe exactly when every program that compiled against the old type still compiles against the new one. That is a claim about assignability, checked in a specific direction, not a judgement about how large the edit looks on a diff; a one-character change can fail this test, and a rewrite of a whole surface can pass it, provided everything the old type accepted the new type still accepts and everything the old type promised the new type still delivers. Lesson 40 gave the four words that name a direction, covariant, contravariant, bivariant and invariant, and this lesson spends them: the direction a value or a name is allowed to travel between a wider type and a narrower one decides whether an edit is safe, and naming it turns a guess into a defensible answer. A version number records that answer once someone has worked it out; it does not work it out for you. A project that bumps a patch version for what turns out to be a breaking change, or a major version for what turns out to be harmless, has not made the edit any safer or any more dangerous, only written down the wrong claim about it.

### The direction table

The rest of this section is a small published surface, edited several ways, each edit run against a consumer file that never changes, so the diagnostic below is the compiler's own verdict, not a description of one. Start with the parameter. `handle(x: string): void` widened to `handle(x: string | number): void` changes nothing for a consumer, because contravariant means a parameter may only travel towards accepting more; reverse the edit, narrowing back down to `string`, and the same unedited consumer file that called `handle(42)` now fails.

```text
error TS2345: Argument of type 'number' is not assignable to parameter of type 'string'.
```

Nothing about the consumer changed; only the direction the parameter travelled did. A return type answers to the same word from the other side, since a return is covariant rather than contravariant: narrowing `getValue(): string | number` down to `getValue(): string` leaves every consumer that assigned the result to a `string | number` variable untouched, since `string` still satisfies that promise, but widening it further, to `string | number | boolean`, breaks that same consumer.

```text
error TS2322: Type 'string | number | boolean' is not assignable to type 'string | number'.
  Type 'boolean' is not assignable to type 'string | number'.
```

A property on an object you accept follows the same logic one level down: adding it optional costs nothing, since a call that never mentioned it is still a valid `Opts`, but adding it required turns that same call into a hole in the object literal.

```text
error TS2741: Property 'timeoutMs' is missing in type '{ retries: number; }' but required in type 'Opts'.
```

A union answers differently on each side of the function. Add a member to a union you return, and a consumer who narrowed on it exhaustively, the way lesson 23 built with a `never` guard in `default`, stops compiling the moment the new member appears: the value left over in that branch is no longer nothing.

```text
error TS2322: Type '{ kind: "triangle"; base: number; height: number; }' is not assignable to type 'never'.
```

Add a member to a union you accept instead and nothing breaks, by the same contravariant reasoning: a caller who only ever passed `"low"` or `"high"` is unaffected by `"medium"` becoming acceptable too. Removing anything, a function, a property, an exported type, is breaking without needing a direction at all: there is no direction to check, and the compiler reports that the name is simply gone.

```text
error TS2305: Module '"libpkg"' has no exported member 'reset'.
```

### Two edits that look safe and are not

Two edits look like nothing at all and still break every consumer that notices. The first is renaming a published type whose shape does not change: `export interface Config { retries: number }` becomes `export interface Options { retries: number }`, same member, same meaning, apparently a tidy-up. A consumer who wrote `import { run, type Config } from "libpkg"` and never touched the object shape is broken anyway.

```text
error TS2305: Module '"libpkg"' has no exported member 'Config'.
```

Structural assignability, lesson 11's rule, only ever asked whether two shapes matched; it never asked whether they were reached by the same name. An import statement asks by name, and a rename fails that question however identical the shape underneath: renaming a type consumers import is exactly as breaking as removing it and publishing a different one in its place.

The second trap is the honest one: making a type more correct can still be the edit that breaks the most consumers, because compatibility and correctness are separate questions with separate answers. A function published as `getValue(): any` is a false promise from the start, since `any` stops the compiler checking rather than describing what actually comes back, but every consumer has been free to abuse that promise. Tighten it to the true, narrower `getValue(): string`, the fix any reviewer would ask for, and a consumer who relied on the old looseness to treat the result as a `number` stops compiling.

```text
error TS2322: Type 'string' is not assignable to type 'number'.
```

The edit made the type honest. It also broke a consumer who was never entitled to what they were doing, and both are true at once. Being right about what a function returns and being compatible with what consumers already assumed are separate properties of an edit, and an author who ships the honest version without checking who depended on the dishonest one has shipped a breaking change while believing they only fixed a bug.

### Deciding what counts, in practice

Everything above assumes a fixed answer, and there usually is one once you name the direction. What is not fixed is who has to live with it, and that changes what the edit costs without changing which direction it travelled. A type shared only inside one repository, built as one program every time anyone runs the compiler, fails this test the instant you make the edit: the build goes red in the same pull request as the change, and every caller is a fixed, visible list you can fix in the same commit. A type published to consumers who install a version and rebuild on their own schedule fails the same test somewhere you cannot see, at a time you do not control, against callers you have never read; your own build stays green, since nothing inside it disagrees with itself, and the disagreement only exists once someone else's build runs against what you shipped. The direction table does not change between these two situations; what counts as acceptable does. A breaking change inside one team's repository is caught immediately and fixed in the same change; the identical edit shipped to a package with independent consumers is a support incident with a delay built in. Before shipping an edit to a published type, ask who reads it and whether they rebuild against your source or against a version they chose to depend on; the answer decides whether the direction you just named is something to fix before you commit or something to announce before you publish, and lesson 44 picks up from there.

## Practice

1. ▢ A published function `parseFlag(value: string): boolean` is edited to `parseFlag(value: string | boolean): boolean`. A consumer's untouched code still calls `parseFlag("true")`. Predict whether it still compiles, and name the direction that decided the answer.

<details markdown="1"><summary>Check</summary>

It still compiles. The parameter widened, the safe contravariant direction: the function now accepts everything it used to, plus more, so a call written against the narrower signature still supplies something the wider one takes.

</details>

2. ▢ A published function `readCount(): number | undefined` is edited to `readCount(): number`. A consumer's untouched code reads `const n: number | undefined = readCount();`. Predict whether it still compiles.

<details markdown="1"><summary>Check</summary>

It still compiles. The return type narrowed, the safe covariant direction: `number` satisfies a variable typed `number | undefined` just as well as the wider type did.

</details>

3. ▢ A published interface `Job { name: string }` gains a new member, `owner: string`, with no `?`. A consumer's untouched code constructs `const j: Job = { name: "build" };`. Predict the diagnostic, with its `TS` number.

<details markdown="1"><summary>Check</summary>

`error TS2741: Property 'owner' is missing in type '{ name: string; }' but required in type 'Job'.` Adding a required property is the breaking half of that row; had it been added optional instead, the same literal would still have satisfied `Job`.

</details>

4. ▢ A published union `type Status = { kind: "ok" } | { kind: "error"; message: string }`, returned from `check(): Status`, gains a third member, `{ kind: "pending" }`. A consumer's untouched code has a `switch` on `.kind` with a `default` branch that assigns the value to a variable typed `never`. Predict what happens, and name the lesson this reaches back to.

<details markdown="1"><summary>Hint</summary>

Ask what is left over inside that `default` branch once `"pending"` stops being excluded by the two existing `case` labels.

</details>

<details markdown="1"><summary>Check</summary>

`error TS2322: Type '{ kind: "pending" }' is not assignable to type 'never'.` This reaches back to lesson 23's exhaustiveness guard: adding a member to a returned union is exactly the change that guard exists to catch, and it fires at the consumer's `switch`, not inside the library.

</details>

5. ▢ The same edit, adding a required property to a published interface, is made twice: once inside a single repository where every caller is compiled in the same run as the change, and once inside a package installed by consumers who rebuild independently on their own schedule. Predict which of the two surfaces the resulting error to the author before anything ships, and which does not.

<details markdown="1"><summary>Check</summary>

The single-repository case surfaces it immediately, often in the same pull request, because every caller is compiled alongside the change. The published-package case does not: the author's own build has nothing to disagree with, and the error only appears once a consumer updates and rebuilds against the new version, on a schedule the author does not control. The edit is identically breaking in both; only who discovers it, and when, differs.

</details>

## Real-world reps

- [ ] Pick one type you publish, or one exported from a module other code in your repository imports, and classify its last edit against the direction table: parameter, return, property or union, and which way it moved.
- [ ] Find a function in something you maintain that still returns `any`, or a type looser than what it actually produces, and work out who would break if you tightened it to what the implementation really returns, before you make that edit.
- [ ] Tomorrow: find one type you own that consumers outside your own repository depend on, and write down, in one sentence, whether they rebuild against your source or against a version they pin, since that answer decides what "breaking" costs them.

## Going further

- [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals): the non-goals list that frames why a published type is judged by what still compiles rather than by how the edit looks
- [TypeScript Handbook, Declaration Files](https://www.typescriptlang.org/docs/handbook/declaration-files/introduction.html): the mechanics of the declaration this lesson treats as already published
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
