---
title: 33. Errors as Values
description: A failure in the return type is one the compiler can make you handle
type: lesson
---

# Lesson 33. Errors as Values

**Mission link:** Owning a codebase means a caller should be able to see, from a return type alone, that an operation can fail, rather than finding out from a stack trace at the moment it least suits you.
**Primary source:** [Introduction, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
**Prerequisites:** [Lesson 31](0031-parsing-instead-of-asserting.md), [Lesson 23](0023-exhaustiveness-with-never.md)

## Warm-up

1. ▢ Lesson 17 told you that a value caught in a `catch` clause is typed `unknown`, never `any`, because JavaScript can throw anything at all, and that writing `catch (e: string)` is refused outright. Predict what happens if you write `catch (e) { const message: string = e; }` under `strict`, and separately predict the diagnostic from `catch (e: string)`.

<details markdown="1"><summary>Check</summary>

The assignment fails with `error TS2322: Type 'unknown' is not assignable to type 'string'.`, since `e` is `unknown` and nothing has narrowed it. The annotation attempt fails with `error TS1196: Catch clause variable type annotation must be 'any' or 'unknown' if specified.` Both are lesson 17's fact, seen again from the angle this lesson needs: a caught value carries no information about what it is, only that something was thrown.

</details>

## Know this

### Why a thrown error is invisible to the type system

A function's type is its parameters and its return type, and a `throw` appears in neither.

```ts
function fail(message: string): number {
  throw new Error(message);
}

const n: number = fail("boom");
console.log(n);
```

This compiles clean under `strict`. `fail`'s type is `(message: string) => number`, exactly as if it returned a number, because a signature has no place to record that the body never returns. Run it and the truth shows up only at run time:

```text
Error: boom
    at fail (.../fail.js:4:11)
```

The process crashes uncaught, nothing beforehand having shown it coming. A `parseAge` that returns `number` for a good string and throws for a bad one types the same way, `(raw: string) => number`, no hint of failure in the signature either way. This is the gap lesson 17 left open: `unknown` on a `catch` variable is honest about a value the compiler cannot describe, but it says nothing about a throw the compiler never saw declared. TypeScript has no checked exceptions and no annotation for "or throws"; a caller finds out by reading the body, or by crashing.

### A failure in the return type

Lesson 31 gave you `safeParse`'s result, a two member discriminated union keyed on `success`, the shape lesson 22 taught and lesson 23 taught you to close with a `never` guard.

```ts
import { z } from "zod";

const User = z.object({ id: z.string(), age: z.number().int().min(0) });

function describe(raw: unknown): string {
  const result = User.safeParse(raw);
  switch (result.success) {
    case true:
      return `${result.data.id} is ${result.data.age}`;
    case false:
      return `invalid: ${result.error.issues.length} issue(s)`;
    default: {
      const _e: never = result;
      return _e;
    }
  }
}

console.log(describe({ id: "u1", age: 30 }));
console.log(describe({ id: "u1", age: -1 }));
```

This compiles clean and prints `u1 is 30` then `invalid: 1 issue(s)`. Delete the `case false` arm and leave everything else as written.

```text
error TS2322: Type 'ZodSafeParseError<{ id: string; age: number; }>' is not assignable to type 'never'.
```

`default` no longer sees `never`, it sees the failure shape itself, named in full, lesson 23's mechanism applied to a validation result. That is the whole argument: because the failure lives in the return type, the compiler forces the build to fail the moment a caller stops handling it, naming the exact site. Compare the weaker signal lesson 23 already showed: an `if (result.success) { return ...; }` with no `else` gives `error TS2366: Function lacks ending return statement and return type does not include 'undefined'.`, real, but naming a missing return rather than a missing case, and silent once the return type is `void`. The `never` guard names the value left over instead.

### A Result shape of your own

`safeParse`'s union belongs to Zod, and most functions run no schema, so they need a failure shape not borrowed from a validation library, the same idea lesson 22 named, written out plainly.

```ts
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

type ParseAgeError =
  | { kind: "empty" }
  | { kind: "not-a-number"; raw: string };

function parseAge(raw: string): Result<number, ParseAgeError> {
  if (raw.trim() === "") return { ok: false, error: { kind: "empty" } };
  const n = Number(raw);
  if (Number.isNaN(n)) return { ok: false, error: { kind: "not-a-number", raw } };
  return { ok: true, value: n };
}

function describeAge(raw: string): string {
  const result = parseAge(raw);
  if (result.ok) return `age is ${result.value}`;
  switch (result.error.kind) {
    case "empty":
      return "no age given";
    case "not-a-number":
      return `"${result.error.raw}" is not a number`;
    default: {
      const _e: never = result.error;
      return _e;
    }
  }
}
```

Run against `"30"`, `""` and `"abc"` and this prints `age is 30`, `no age given` and `"abc" is not a number`. `Result<T, E>` is two arms and nothing more, no `map`, no `andThen`, no chain for threading it through several calls unwrapped; libraries add that machinery, and building one is a stage beyond this.

### The typed error is the point, not the wrapper

The `never` guard on `result.error.kind` works only because `ParseAgeError` is literal kinds. Add a third kind, `{ kind: "negative"; value: number }`, and use it in `parseAge` without touching `describeAge`'s `switch`.

```text
error TS2322: Type '{ kind: "negative"; value: number; }' is not assignable to type 'never'.
```

The build breaks at the switch that stopped being exhaustive, lesson 23's proof again, now protecting a failure type. Change `Result<number, string>` instead, every failure just a message, and add the same reason as a plain string.

```ts
if (n < 0) return { ok: false, error: "negative" };
```

This compiles with no error anywhere, even though nothing in `describeAge` recognises `"negative"`, which falls through to a generic `"invalid age"`. A `string` carries no structure to reason about, so there is nothing for a `never` guard to check; the same is true of a bare `Error`. Literal kinds give the guarantee lesson 23 built; `Error` or `string` give a place to put a message and nothing more.

### When to throw anyway

A lesson that says never throw would be wrong, and ignored for being wrong. Throw for a programmer error the immediate caller cannot sensibly act on, such as a call that violates a declared precondition, or an invariant already broken, where continuing computes a wrong answer from a program no longer in a state anyone reasoned about. Throwing also suits a genuine top level boundary, a place where something above catches whatever comes up and turns it into a response, a log line or an exit code, with nothing below needing to know the shape of what went wrong. Return a value for a failure that is an expected, nameable outcome, which a boundary check almost always is: a string that fails to parse as an age is not a bug, it is one of `parseAge`'s outcomes. The test is short: can the immediate caller do something different depending on which failure occurred. If yes, it needs the failure as a value to inspect. If no, a throw loses you nothing.

### The cost, stated fairly

Putting a failure in the return type puts the handling in the caller's face, and that is the point, not a side effect to apologise for, but it is still more code: every call site that can fail now has a branch a `throw` would have let it skip. It also composes less conveniently across several layers: an exception can cross five call frames untouched and be caught once near the top, while a `Result` has to be checked and passed on at every frame by hand, since no combinator was taught here. A codebase with both styles side by side is normal; the decision belongs at each boundary, using the test above, and at a boundary the answer is almost always to return a value.

### The stage's criterion, half discharged

Stage 5 asked that no value enter the program unvalidated and that no assertion be load bearing. Lesson 31 put a parse at the edge; this lesson put that parse's failure in the return type, a value a caller can inspect rather than a throw a caller can ignore. Between the two, no value crosses the boundary unchecked, and no caller can fail to notice a value failed to validate, because the type it received says so.

## Practice

1. ▢ `function assertPositive(n: number): number { if (n <= 0) throw new RangeError("not positive"); return n; }`. Predict `assertPositive`'s inferred type, and predict whether `const x: number = assertPositive(-1);` compiles.

<details markdown="1"><summary>Check</summary>

The type is `(n: number) => number`, with no trace of the `throw`. The assignment compiles with no error, since the compiler only checks that a `number` is assigned where one is expected, never whether the call can actually produce one; the failure shows up only at run time, as an uncaught `RangeError`.

</details>

2. ▢ In the `describe` function using `safeParse`, the `case false` arm is deleted but `case true` and the `default` with `const _e: never = result;` stay. Predict the diagnostic, with its `TS` number, and say what value it names.

<details markdown="1"><summary>Check</summary>

`error TS2322: Type 'ZodSafeParseError<{ id: string; age: number; }>' is not assignable to type 'never'.` It names the failure result, since `default` now receives exactly what `case false` used to exclude.

</details>

3. ▢ Same `describe` function, but written as `if (result.success) { return ...; }` with no `else` and no `default` anywhere, return type still `string`. Predict whether this compiles, and if not, say what the diagnostic fails to tell you that item 2's did.

<details markdown="1"><summary>Check</summary>

It fails with `error TS2366: Function lacks ending return statement and return type does not include 'undefined'.` Real, but it reports a missing `return`, not a missing case, and it falls silent entirely on a `void` return type, which is why lesson 23 built the `never` guard in the first place.

</details>

4. ▢ Two versions of `parseAge` each gain a `"negative"` failure reason, one where the failure arm is `ParseAgeError` (literal kinds) and one where it is a plain `string`. Neither caller is updated. Predict which version fails to compile, and which compiles with no error anywhere.

<details markdown="1"><summary>Check</summary>

The literal kind version fails: `error TS2322: Type '{ kind: "negative"; value: number; }' is not assignable to type 'never'.` The `string` version compiles clean, since a `string` carries no structure to check against, and the new reason falls silently into the caller's catch-all branch.

</details>

5. ▢ Two situations: (a) an internal helper indexes an array at a position that should always be in range, but the position is out of range only because earlier code has a bug; (b) a function converts a user-typed date string into a `Date`, and the string is not a valid date. Apply the test "can the immediate caller do something different if this fails" to each, and say which should throw and which should return a value.

<details markdown="1"><summary>Check</summary>

(a) should throw: the caller did not cause the problem and cannot act on it differently, since an invariant is already broken and the right response is to stop. (b) should return a value: an invalid date string is an expected outcome of parsing input, and the caller can act differently, such as showing a validation message, exactly the boundary case this lesson and lesson 31 both point at.

</details>

## Real-world reps

- [ ] Find one function that throws for a condition its caller could reasonably expect, and rewrite its return type as a `Result` with a literal kind union for the failure, then update every caller.
- [ ] Find one failure currently typed `Error` or `string`, give it two or three literal kinds instead, then delete a `case` from whatever handles it and read the diagnostic naming the kind you removed.
- [ ] Tomorrow: find one boundary in a real project, an HTTP handler or a CLI entry point, and check whether what calls into your validated code is prepared to receive a failure value, or is quietly relying on nothing ever throwing.

## Going further

- [Handbook, Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html), for the discriminated union shape and the `never` guard this lesson reuses from lessons 22 and 23 rather than re-teaching
- [Zod documentation](https://zod.dev/), for the `safeParse` result type used here as the worked model
- [Effective TypeScript](https://effectivetypescript.com/), for further discussion of when a thrown error is the wrong choice for an expected outcome
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
