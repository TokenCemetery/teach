---
title: 18. An Assertion Is Not a Check
description: Every way to tell the compiler to stop checking, and what each one costs when the claim is wrong
type: lesson
---

# Lesson 18. An Assertion Is Not a Check

**Mission link:** The mission asks you to keep type assertions out of code that carries weight, which requires seeing exactly what an assertion buys, what it costs, and the two mistakes it is almost always used to make.
**Primary source:** [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals)
**Prerequisites:** [Lesson 17](0017-unknown-instead-of-any.md), [Lesson 11](0011-structural-assignability.md)

## Warm-up

1. ▢ Lesson 11 showed that `{ a: 1, b: 2 }` assigned directly to a variable typed `{ a: number }` is refused with `TS2353`, but the same value routed through a plain variable first is accepted. What exactly turned the check off there, and was the value any safer afterwards?

<details markdown="1"><summary>Check</summary>

Nothing about the value changed. Routing through a variable removed the fresh literal that excess property checking looks for, so only that one extra check stopped running; ordinary structural assignability still passed, since extra members were always allowed. The value was exactly as risky before and after; only the compiler's willingness to mention it changed.

</details>

## Know this

### An assertion changes belief, not fact

Lesson 2 showed `readonly` disappearing completely at run time, because a type is a compile-time claim and nothing about it survives into the emitted JavaScript. An assertion is the same fact from the other side: a type constrains what the compiler accepts, and an assertion tells it to stop checking. `as T` and `!` both compile to nothing, so no conversion runs and no value is checked; only what the type checker believes about an expression moves. A correct belief changes nothing, since the code would have worked anyway. A wrong one leaves the program carrying a lie the compiler has agreed not to question, and it fails later, somewhere else, usually far from the assertion that introduced it.

### `as`, and the one guard it has

`as` refuses to convert between two types that share nothing:

```ts
const n = "x" as number;
```

```text
error TS2352: Conversion of type 'string' to type 'number' may be a mistake because neither type sufficiently overlaps with the other. If this was intentional, convert the expression to 'unknown' first.
```

`as` permits a conversion only when one type is assignable to the other or the two already overlap in their members; `string` and `number` share nothing, so the compiler calls it a likely mistake. The diagnostic names the way round it, and the way round it compiles:

```ts
const n = "x" as unknown as number;
```

`unknown` overlaps with everything, so routing through it satisfies the guard twice, completing the trip the single `as` refused. Call this what it is: telling the compiler that you have read its objection and would like it to be quiet, not a different feature from one assertion. It compiles cleanly and looks identical to a legitimate use of `unknown` from lesson 17. Seeing one in a diff is not a style question; it is a request for an explanation, because the guard that would have caught a mistake was just asked, twice, to stand aside.

### `!`, and the lie it is most often used to tell

The non-null assertion removes `null` and `undefined` without checking that either is actually absent. It removes `null` from `string | null` cleanly enough; the case that matters is this one, on a `string[]`:

```ts
function first(arr: string[]): string {
  return arr[0]!;
}
```

This compiles, and it is a lie whenever `arr` is empty, since there is no element at index 0 to be non-null about. Lesson 16 covers `noUncheckedIndexedAccess`, the flag that makes a read like `arr[0]` come back as `string | undefined` so this question has to be answered before use. `!` is how that decision disappears without being made: the checker is told the union is gone, the array does not care what the checker was told, and `arr[0]` on an empty array is `undefined` regardless.

### `as` silences a check that was right

This is the sharpest fact here. Lesson 11 taught that a fresh object literal assigned to a typed target triggers excess property checking, and that routing the literal through a variable defeats it without changing the value. `as` defeats the same check more directly still:

```ts
interface P {
  a: number;
}
const p = { a: 1, b: 2 } as P;
```

This compiles, no `TS2353`, nothing, even though the excess property check exists precisely to catch a stray member like `b` on a fresh literal. Put the two commonest uses of an assertion side by side and a pattern appears: one silences the null check `strictNullChecks` runs, the other silences the excess property check lesson 11 taught, both compiling cleanly because compiling cleanly is exactly what an assertion buys. Neither use makes the value correct; both just stop the compiler from saying so.

### Suppression comments, and why one of them cannot rot

`@ts-ignore` and `@ts-expect-error` both suppress the diagnostic on the next line, but diverge once the code around them changes. Above a real error, both work silently:

```ts
// @ts-expect-error
const a: number = "no";
```

Both compile clean there. The difference shows once that error goes away, say because someone fixes the assignment. `@ts-ignore` above correct code does nothing at all, forever:

```ts
// @ts-ignore
const c: number = 1;
```

Still compiles, still clean, so the comment sits there permanently with no signal to a reviewer that it is dead. `@ts-expect-error` above the same correct code is treated as a mistake in its own right:

```ts
// @ts-expect-error
const d: number = 1;
```

```text
error TS2578: Unused '@ts-expect-error' directive.
```

That is the whole argument for preferring it: `@ts-ignore` can only hide a diagnostic, so once the one it was written for is gone it sits inert, ready to hide whatever unrelated error lands on that line next. `@ts-expect-error` makes a claim, that an error exists there, and `TS2578` fires the moment that claim stops being true. It cannot go stale without announcing itself.

### What to do instead

An assertion is the fast way to make an error message disappear, and disappearing is not being fixed. Narrow the value, as in lesson 12, if a runtime check can tell a union's branches apart. Bring it in as `unknown` and check it, as in lesson 17, if the shape cannot yet be trusted. Fix the type at its source if the type was simply wrong, since asserting at the call site treats a declaration bug as a local inconvenience. Validate the value if it crossed a boundary the compiler never watched, stage 5's material. All four leave a runtime check that agrees with the claim; an assertion leaves only the claim.

The honest exception is narrow: an assertion is defensible where you hold information the compiler cannot, a framework's contract, an invariant enforced elsewhere, a value already checked one line above in a way the checker cannot see through. The standard for that is a comment stating what you know and why the compiler cannot. `arr[0]!  // arr is populated by the loop above and never empty here` is a claim a reader can check; `arr[0]!` alone is a defect, since nothing distinguishes the honest exception from the two silenced checks above.

One more tool belongs here without belonging to this lesson: `satisfies` checks a literal against a type without widening it the way an annotation would, which is often what people actually want when they reach for `as`. Stage 4 owns it.

## Practice

1. ▢ Predict the exact diagnostic, with its `TS` number, and then say what change to the code would make it compile without going through `unknown`.

   ```ts
   const flag = true as string;
   ```

<details markdown="1"><summary>Check</summary>

`error TS2352: Conversion of type 'boolean' to type 'string' may be a mistake because neither type sufficiently overlaps with the other. If this was intentional, convert the expression to 'unknown' first.` `boolean` and `string` share nothing. Asserting to a type that already overlaps, `boolean | string` say, would compile without touching `unknown` at all.

</details>

2. ▢ Predict whether this compiles, and if it does not raise a compile error, say exactly when it fails instead and what fails.

   ```ts
   function last(arr: number[]): number {
     return arr[arr.length - 1]!;
   }
   ```

<details markdown="1"><summary>Hint</summary>

Nothing here is a type error. Ask what `arr.length - 1` is when `arr` is `[]`.

</details>

<details markdown="1"><summary>Check</summary>

Compiles, no diagnostic. It fails at run time whenever `arr` is empty: `arr.length - 1` is `-1`, `arr[-1]` is `undefined`, and `!` already told the compiler that cannot happen, so the declared return type `number` is a promise unkept. `noUncheckedIndexedAccess` would have made the read `number | undefined` and forced a decision; `!` skipped it.

</details>

3. ▢ Predict whether this compiles, and say specifically which check from an earlier lesson it is switching off.

   ```ts
   type Options = { retries: number };
   function run(o: Options) {}
   run({ retries: 3, timeout: 500 } as Options);
   ```

<details markdown="1"><summary>Check</summary>

Compiles, no diagnostic. Passing `{ retries: 3, timeout: 500 }` directly to `run` would ordinarily trigger lesson 11's excess property check, since it is a fresh literal meeting a typed target and `timeout` is not a member of `Options`. `as Options` silences exactly that check, so a misspelled or misplaced `timeout` passes unremarked.

</details>

4. ▢ A file has this line, and the assignment above it is later corrected so the type error is gone. Predict what happens on the next build for each version, and name the diagnostic where one appears.

   ```ts
   // @ts-ignore
   const value: number = 5;
   ```

   ```ts
   // @ts-expect-error
   const value: number = 5;
   ```

<details markdown="1"><summary>Check</summary>

The `@ts-ignore` version still compiles clean, with nothing left to suppress and no signal that it is dead weight. The `@ts-expect-error` version reports `error TS2578: Unused '@ts-expect-error' directive.`, because its claim, that an error exists on the next line, is no longer true. That is the whole reason to prefer it: it forces removal instead of quietly rotting.

</details>

5. ▢ A pull request contains `const config = raw as Config;` with no comment, where `raw` came from `JSON.parse` two lines above. What, precisely, is wrong with this line as written, and what would make it acceptable?

<details markdown="1"><summary>Check</summary>

Nothing here has been checked; `raw` is `any` straight out of `JSON.parse`, and `as Config` only tells the compiler to believe it has the shape `Config` requires, exactly the claim an assertion cannot back up. As written it is a defect, not a shortcut, since a malformed or partial payload passes silently and fails later wherever a missing or mistyped field is read. It becomes acceptable by validating `raw` against `Config`'s shape instead, stage 5's material; short of that, a comment stating what guarantees the shape and why the compiler cannot see it would at least make the assertion reviewable.

</details>

## Real-world reps

- [ ] Search a codebase you work in for `as unknown as` and read the code around each hit; for every one, decide whether a comment nearby explains what is known that the compiler cannot see, and flag the ones that do not.
- [ ] Find a `!` on an indexed read, `arr[0]!` or similar, and trace whether the array it reads from can ever be empty at that point; if it can, replace the assertion with a check rather than removing the mark.
- [ ] Tomorrow: grep for `@ts-ignore` in a project you touch and try swapping each one for `@ts-expect-error`; any that fail to build again with `TS2578` were suppressing nothing and can be deleted outright.

## Going further

- [Everyday Types, type assertions](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html): the handbook's own framing of `as`, including the overlap rule that refuses an unrelated conversion
- [TypeScript 3.9 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-9.html): the release that introduced `@ts-expect-error` and the reasoning against `@ts-ignore`
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
