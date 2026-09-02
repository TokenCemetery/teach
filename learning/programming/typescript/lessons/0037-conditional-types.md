---
title: 37. Conditional Types
description: A type that branches, and a union it quietly takes apart first
type: lesson
---

# Lesson 37. Conditional Types

**Mission link:** Owning a codebase means a function's return type sometimes has to track the type of the argument that produced it, and a conditional type says so without the caller writing an assertion or the library growing a second function for the same job.
**Primary source:** [Conditional Types, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html)
**Prerequisites:** [Lesson 36](0036-mapped-types.md), [Lesson 23](0023-exhaustiveness-with-never.md)

## Warm-up

1. ▢ Lesson 36 filtered a mapped type by remapping a key that failed a test to `never`, and that property vanished from the result entirely rather than staying present with type `never`. Predict: if the same trick were run once per member of a *union* instead of once per key of an object, what would decide, member by member, whether that member survives?

<details markdown="1"><summary>Check</summary>

Some per-member test, the same shape as the `T[K] extends number ? K : never` test lesson 36 ran on each key. This lesson runs that test on each member of a union instead of each key of an object: `T extends U ? X : Y`, with `never` again marking the branch that removes rather than keeps. What makes that happen at the union level is the subject below.

</details>

## Know this

### The form, and what `extends` is asking

A conditional type has exactly this shape: `T extends U ? X : Y`. Read it as a question about assignability, not inheritance: is whatever `T` turns out to be assignable to `U`? If yes, the type is `X`; if no, it is `Y`. This is lesson 11's structural rule, applied at the type level: `extends` here is not the `extends` on an `interface`, a relationship declared once and for good, it is a question the compiler answers fresh every time the type is used, and the answer can differ for different callers of the same generic.

```ts
type IsString<T> = T extends string ? true : false;

type A = IsString<"hi">;
type B = IsString<number>;

const t: A = true;
const f: B = false;
```

This compiles with no diagnostic: `A` evaluated to `true` and `B` to `false`, and both assignments matched. Swap either assignment for the other value and the compiler objects, naming the literal type it expected. That is the technique this lesson leans on throughout: assign a value to a computed type and read what the diagnostic calls it, since the diagnostic names what the type actually evaluated to, not what you hoped for.

### `never`, the branch that produces nothing

Lesson 23 gave you `never` as the type with no values, the type an exhaustiveness guard assigns a genuinely impossible leftover to. A conditional type reuses that meaning for a branch: writing `never` as one arm says that arm produces nothing. On its own, a type computed to a value nobody can hold looks pointless, but a `never` branch stops being strange the moment it meets a union, because a union with a `never` member is the same union with that member gone. A per-member test paired with a `never` branch that removes rather than keeps is what the next section demonstrates.

### Distribution: the compiler takes the union apart

This is the part of a conditional type that surprises people, and it is worth demonstrating rather than taking on faith.

```ts
type NoStr<T> = T extends string ? never : T;
type R = NoStr<string | number>;

const a: R = "x";
```

```text
error TS2322: Type 'string' is not assignable to type 'number'.
```

Read that diagnostic literally: it says `R` is `number`, not `string | number`. That is proof `NoStr` did not run once against the whole union and ask whether *that* is assignable to `string`; it ran once per member, `string extends string ? never : string` and `number extends string ? never : number`, giving `never | number`, and a union absorbs `never` the way lesson 36's filtered key vanished, leaving plain `number`. The diagnostic names the survivor, evidence the union was taken apart member by member and the matching one dropped. Assign the type that actually survived, `const b: R = 1;`, and it compiles with nothing to report: `NoStr<string | number>` really is `number`, checked on its own, not `string | number` with `string` merely disallowed at the assignment.

A naked type parameter on the left of `extends`, the position `T` occupies above, is what triggers this. When TypeScript sees a bare type parameter there and the substituted type is a union, it distributes: it evaluates the whole conditional once per member and unions the results back together, rather than evaluating it once against the union as a whole.

### Turning distribution off

Sometimes you want the second reading, the union tested once as a whole, and TypeScript gives you a way to ask for it: wrap both sides in a one-element tuple.

```ts
type NoStrTuple<T> = [T] extends [string] ? never : T;
type R2 = NoStrTuple<string | number>;

const c: R2 = "x";
```

This compiles. `[T]` is no longer naked, it is a tuple that happens to contain one, so distribution does not fire; the compiler asks once whether `string | number` as a whole is assignable to `string`, the answer is no, so the whole union survives as `R2`, and `"x"` is comfortably a member of it. The rule to carry forward: a naked type parameter on the left of `extends` distributes member by member; the same parameter wrapped in a tuple on both sides is tested once, over the whole union. Which one you want is a decision to make on purpose, not a surprise to discover from a confusing result.

### The standard library is built from exactly this

`Exclude<T, U>`, which removes every member of `T` assignable to `U`, is `NoStr` generalised, and it is distributive for the same reason.

```ts
type E = Exclude<string | number | boolean, string>;

const d: E = 1;
const e: E = true;
const f2: E = "x";
```

The first two assignments compile; the third gives `error TS2322: Type '"x"' is not assignable to type 'E'.`, because `E` evaluated to `number | boolean`, `string` dropped exactly the way `NoStr` dropped it above. Recognising `Exclude`, `Extract` and `NonNullable` as this same mechanism, not separate magic, is most of what there is to know about the built-in conditional types.

### The caller who benefits

The honest case for reaching for a conditional type is narrow, so make it concrete rather than abstract. Here is one: a function that parses a raw string and, depending on a flag the caller passes, hands back either a `number` or a `string`.

```ts
function parse<T extends boolean>(raw: string, asNumber: T): T extends true ? number : string {
  return (asNumber ? Number(raw) : raw) as T extends true ? number : string;
}

const price = parse("42", true);
const label = parse("42", false);

const total: number = price;
const text: string = label;
```

Every line compiles, and neither caller wrote an assertion. `price` is `number`, inferred from the literal `true` passed for `asNumber`; `label` is `string`, inferred from `false`; each precise enough that assigning `price` where a `string` was expected fails with `error TS2322: Type 'number' is not assignable to type 'string'.`, naming the exact type the conditional computed. Compare the signature this replaces: without the conditional, `parse` would declare `number | string`, and every caller would need to narrow or assert before using a result their own argument already determined. That is the caller who benefits: one who gets back the precise type with nothing to assert and nothing to narrow. Without a caller like that, a plain union return type or two separately named functions is the better design; that is lesson 26's question, what does the caller learn that a simpler signature could not have said, asked one level up. Pulling a type out of the matched branch, rather than returning the branch itself, needs `infer`, which lesson 38 owns entirely.

### Where this stops paying

A single conditional, tested against a caller like `parse` above, earns its place. The moment stops paying once a conditional's branch is itself another conditional, sitting inside the value position of a mapped type: three layers of branching a reader has to hold at once to answer "what is the type of this one property." At that depth nobody can read the type back into English without a compiler, so nobody can review it either, and stage 6's whole point is to stop before that: an API's types serve the callers reading the signature, not a trick for its own sake. Notice yourself nesting a conditional inside a conditional inside a mapped type, and that is the line; step back to a named helper type, a plain union, or two functions, and ask again whether a caller is still better off.

## Practice

1. ▢ `type IsArray<T> = T extends unknown[] ? true : false;` then `type A = IsArray<string[]>;` and `type B = IsArray<string>;`. Predict whether `const a: A = true;` and `const b: B = true;` each compile.

<details markdown="1"><summary>Check</summary>

`const a: A = true;` compiles: `A` evaluated to `true`. `const b: B = true;` fails with `error TS2322: Type 'true' is not assignable to type 'false'.`: `B` evaluated to `false`, and the diagnostic names it.

</details>

2. ▢ `type OnlyNum<T> = T extends number ? T : never;` then `type R = OnlyNum<string | number | boolean>;`. Predict what `R` is, and what happens when you write `const x: R = "x";`.

<details markdown="1"><summary>Hint</summary>

Distribution runs the conditional once per member of the three-member union, and a `never` result disappears from what is unioned back together.

</details>

<details markdown="1"><summary>Check</summary>

`R` is `number`: `string` and `boolean` each hit the `never` branch and vanish, leaving only the member that matched. `const x: R = "x";` fails with `error TS2322: Type 'string' is not assignable to type 'number'.`, which names the survivor and is the proof that both other members were tested and dropped.

</details>

3. ▢ `type Check<T> = [T] extends [number] ? true : false;` then `type R = Check<string | number>;`. Predict whether `const y: R = true;` compiles, and say why this differs from item 2.

<details markdown="1"><summary>Check</summary>

It fails with `error TS2322: Type 'true' is not assignable to type 'false'.` The tuple stops distribution, so the conditional runs once against the whole union, which is not assignable to `number`, giving `false` for the entire type rather than testing each member the way item 2 did.

</details>

4. ▢ `type E = Exclude<"a" | "b" | "c", "a">;`. Predict what compiles: `const p: E = "b";` and `const q: E = "a";`.

<details markdown="1"><summary>Check</summary>

`const p: E = "b";` compiles, since `"b"` was never excluded. `const q: E = "a";` fails with `error TS2322: Type '"a"' is not assignable to type 'E'.`, since `Exclude` dropped it, and `E` is `"b" | "c"`.

</details>

5. ▢ A teammate proposes rewriting `parse`'s return type as `T extends true ? (T extends true ? number : never) : string`, calling it "more explicit." Say what is wrong with this, independent of whether it type-checks.

<details markdown="1"><summary>Check</summary>

The inner conditional is redundant: nested inside a branch that already established `T extends true`, it can only ever take its own `true` arm. The real problem is the habit it demonstrates: nesting a conditional inside a conditional with no caller-visible payoff is exactly the depth this lesson said to stop at, and the flatter version is the one lesson 26's question would keep.

</details>

## Real-world reps

- [ ] Find, or write, one conditional type in real code and check whether its left-hand side is naked or wrapped, and say which behaviour that choice buys.
- [ ] Pick one function you use that returns a union such as `number | string`, and check whether any call site narrows or asserts right after calling it; that call site is the caller a conditional type would have served.
- [ ] Tomorrow: find one use of `Exclude`, `Extract` or `NonNullable` in a real project and rewrite what it does in your own words, without naming the utility, to check you can see the conditional underneath it.

## Going further

- [TypeScript Handbook, Conditional Types](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html): the source this lesson compresses, including the distributive conditional types section it draws from
- [TypeScript Handbook, Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html): the constraint and inference vocabulary this lesson's caller example leans on
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
