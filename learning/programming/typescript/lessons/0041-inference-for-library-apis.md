---
title: 41. Inference for Library APIs
description: Design the signature so the caller annotates nothing
type: lesson
---

# Lesson 41. Inference for Library APIs

**Mission link:** A signature you publish gets called from code you will never read, so whether it serves that caller has to be decided at the point you write it, not discovered from a support ticket.
**Primary source:** [Generics, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/2/generics.html)
**Prerequisites:** [Lesson 26](0026-generics-and-constraints.md), [Lesson 14](0014-what-inference-already-knows.md)

## Warm-up

1. ▢ Lesson 26's `createEmptyList<T>()` forced every caller to write the type argument by hand, `createEmptyList<number>()`, because no call ever gave the compiler anything to infer `T` from. `first<T>(xs: T[]): T` needed no such help. What did `first` have that `createEmptyList` did not?

<details markdown="1"><summary>Check</summary>

A parameter typed `T[]`. The argument at the call site, `[1, 2, 3]`, gave the compiler something to unify `T` against before it ever reached the return type. `createEmptyList` takes no argument, so `T` never appears anywhere the compiler reads before it has to decide what `T` is, and it falls back to `unknown` or `never` rather than guessing right. This lesson is about writing the first kind of signature on purpose.

</details>

## Know this

### The standard

A signature is good when the caller writes no annotation and gets back a type precise enough to be worth having, and when a wrong call produces an error naming the caller's own mistake rather than the plumbing you built to catch it. Both halves matter. The first is the one people aim for; the second is the one they forget, and a signature can satisfy the first while failing the second badly enough that the first stops mattering. Lesson 14's "annotate boundaries, let bodies infer" was advice for a caller writing code against someone else's function. This lesson is the same rule from the other side of that boundary: you decide what the caller has to write, and everything below checks whether you decided well.

### Where inference comes from

Inference runs from arguments. A type parameter that appears in a parameter position has something to unify against; a type parameter that appears only in a return position has nothing, no matter how it is written down.

```ts
function identity<T>(x: T): T {
  return x;
}
const a = identity(42);
const s: string = a;
```

```text
error TS2322: Type 'number' is not assignable to type 'string'.
```

Nobody annotated `a`. The argument `42` told the compiler `T` is `number`, and the diagnostic proves it by naming `number`, exactly the way lesson 26's `first` worked. Now take the type parameter out of the parameter list entirely:

```ts
function parseValue<T>(raw: string): T {
  return JSON.parse(raw);
}
const config = parseValue("{}");
config.host;
```

```text
error TS18046: 'config' is of type 'unknown'.
```

`raw` is a `string` whichever `T` a caller has in mind, so nothing in this call fixes `T` to anything, and the compiler settles on `unknown` rather than pretend to know. Reading `config.host` at all now needs `parseValue<{ host: string }>("{}")`, the type argument written out by hand. Compare the cost: `identity`'s caller wrote nothing and still got a type worth having; `parseValue`'s caller has to write the type argument on every single call, or get `unknown` and start narrowing by hand. Where a type parameter sits in the signature decided that difference completely.

### Two ways a signature fails its caller

**The type argument nobody can skip.** This is `parseValue` again, as a design mistake rather than a fact about inference. A caller who always has to write `<...>` gained nothing from the type parameter, since a plain `unknown` parameter and a cast at the call site would have cost the same typing. The fix, when the value the type describes really does exist somewhere in the call, is to move the parameter onto something the caller passes:

```ts
function wrap<T>(): { value: T } {
  return { value: undefined as T };
}
const w1 = wrap<number>();

function wrapValue<T>(value: T): { value: T } {
  return { value };
}
const w2 = wrapValue(42);
const label: string = w2.value;
```

```text
error TS2322: Type 'number' is not assignable to type 'string'.
```

`wrap` needed the caller to spell out `<number>` because nothing else could tell it. `wrapValue` needed nothing: the argument `42` fixed `T`, and the caller who tries to treat the result as a `string` gets told, correctly, that it is a `number`. When a type parameter can only ever be filled in by hand, that is not a caller being careless, it is the parameter sitting in the wrong place in your signature.

**The error that names your machinery instead of the mistake.** This failure survives even when inference works perfectly, because the problem is what the diagnostic says once it fires. Here is a signature that enforces, at compile time, that a caller may only pick properties whose value is a number, built from lesson 36's key remapping and lesson 37's conditional types:

```ts
type KeysMatching<T, V> = { [K in keyof T]: T[K] extends V ? K : never }[keyof T];

function pickNumberKeys<T>(obj: T, keys: KeysMatching<T, number>[]): Pick<T, KeysMatching<T, number>> {
  const result = {} as Pick<T, KeysMatching<T, number>>;
  for (const k of keys) result[k] = obj[k];
  return result;
}

const person = { name: "Ann", age: 30 };
pickNumberKeys(person, ["salary"]);
```

```text
error TS2322: Type '"salary"' is not assignable to type '"age"'.
```

`"salary"` really is wrong, but the message never says why: it compares the typo against `"age"` alone, because `person` happens to have exactly one number-valued property, and gives no hint that the rule is "must name a property whose value is a number" or that `"name"` was ever a candidate. A caller debugging this has to read `KeysMatching` itself to learn what the error means. Here is the plain signature doing a smaller, honest job, with the same caller and the same typo:

```ts
function pick<T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> {
  const result = {} as Pick<T, K>;
  for (const k of keys) result[k] = obj[k];
  return result;
}
pick(person, ["salary"]);
```

```text
error TS2322: Type '"salary"' is not assignable to type '"age" | "name"'.
```

Same mistake, same caller, and this message names both real properties of `person`, which is exactly what the caller needs to fix the typo. The number-only rule that `pickNumberKeys` tried to buy was real, but it cost an error nobody could read without opening the type alias, while the plain version's error explains itself. That is the trade to weigh every time a clever constraint tempts you: what the caller sees when they get it wrong is part of the price, not a footnote to it.

### `const` type parameters

A plain type parameter, filled from an array literal, widens the way lesson 10 said any `let` does:

```ts
function tag<T>(value: T): T {
  return value;
}
const plain = tag(["a", "b"]);
const p: "a" = plain[0];
```

```text
error TS2322: Type 'string' is not assignable to type '"a"'.
```

`plain[0]` is a plain `string`, so the literal `"a"` is gone. Before this feature, keeping it meant asking the caller to write `tag(["a", "b"] as const)` themselves, every time. Marking the type parameter `const` instead moves that cost into the signature, once:

```ts
function tagConst<const T>(value: T): T {
  return value;
}
const literal = tagConst(["a", "b"]);
const l: "a" = literal[0];
const wrong: "z" = literal[0];
literal.push("c");
```

```text
error TS2322: Type '"a"' is not assignable to type '"z"'.
error TS2339: Property 'push' does not exist on type 'readonly ["a", "b"]'.
```

`l` compiles: `literal[0]` really is the literal `"a"`, proven by the second assignment naming `"a"` rather than accepting `"z"`. `push` is refused, so `const T` also made the array `readonly`, the same pair of effects lesson 10's `as const` has always had, now inferred with no annotation at all. Nothing new is reachable here that `as const` at the call site could not already do; what changes is who pays. `satisfies`, from lesson 27, still asks the caller to write one more word to keep their own literal. `const T` gets the same precision with the caller writing nothing, because the author paid for it once, in the signature.

### Where to stop

Every technique above earned its place because a call site showed a caller better off: less to write, or a wrong call naming what they actually did wrong. That is the review question, in two halves: what does the caller write, and what do they see when they get it wrong. `pickNumberKeys` answered the first well and the second badly, and the second sank it. A type serving the caller on both counts is worth almost any internal complexity; a type serving only the author's sense of elegance is worth none, however satisfying it was to write. Run both halves before a clever signature ships, not after someone hits the error it produces.

## Practice

1. ▢ `function firstEl<T>(xs: readonly T[]): T { return xs[0]; }`. A caller writes `const x = firstEl([1, 2, 3]);` then `const s: string = x;`. Predict the diagnostic, and say which position let the compiler skip asking the caller for help.

<details markdown="1"><summary>Check</summary>

`error TS2322: Type 'number' is not assignable to type 'string'.` The parameter `xs: readonly T[]` gave the compiler the argument `[1, 2, 3]` to unify `T` against, fixing `T` as `number` before the return type was ever considered, so `x` is `number` with nothing written down.

</details>

2. ▢ `function makeMap<K, V>(): Map<K, V> { return new Map(); }`. Predict what a caller has to write to use this usefully, and why.

<details markdown="1"><summary>Hint</summary>

Ask what, in a call with no arguments, could ever tell the compiler what `K` and `V` are.

</details>

<details markdown="1"><summary>Check</summary>

Both type arguments, by hand, every time: `makeMap<string, number>()`. `makeMap` takes no argument and neither `K` nor `V` appears anywhere else for the compiler to infer from. That is the first failure from this lesson: a type parameter with nowhere to be inferred from should either take a parameter to infer from, or be dropped in favour of `const m: Map<string, number> = new Map();`.

</details>

3. ▢ A teammate writes `function firstMatch<T, R extends T extends string ? RegExpMatchArray : never>(value: T, pattern: T extends string ? RegExp : never): R`, to make the parameter and return type disagree loudly if `value` is ever not a string. Predict, without running it, what a caller who mistakenly passes a `number` for `value` is likely to see, and why that is the second failure from this lesson rather than the first.

<details markdown="1"><summary>Check</summary>

Likely to name the computed conditional type itself, rather than saying plainly "value must be a string." Inference is not the problem: `T` and `R` can both be inferred from `value`. The problem is legibility, nesting a conditional inside both the parameter and return position, which hides the actual rule behind machinery the caller was never shown, the same way `KeysMatching` hid "must be number-valued" behind a lone surviving literal.

</details>

4. ▢ `function first<const T extends readonly unknown[]>(xs: T): T[0] { return xs[0]; }` is called as `const h = first(["x", "y"]);` then `const check: "x" = h;`. Predict whether `check` compiles, and say what would have to change in the call for it to fail.

<details markdown="1"><summary>Check</summary>

It compiles. `const T` kept the argument's literal types, so `T` is `readonly ["x", "y"]` and `T[0]` is the literal `"x"`, exactly what `check` expects. It would fail if the array literal were replaced with a variable typed `string[]` before being passed in, since there would be no literal for `const T` to preserve.

</details>

5. ▢ Two signatures do the same job: `function firstA<T>(xs: T[]): T` and `function firstB<T>(): (xs: T[]) => T`. A caller writes `firstA([1, 2])` and, separately, `firstB()([1, 2])`. Predict which caller has to write a type argument, and which does not.

<details markdown="1"><summary>Check</summary>

`firstA([1, 2])` infers `T` as `number` directly and needs nothing from the caller. `firstB()` is called with no argument, so `T` has nothing to unify against there, forcing `firstB<number>()([1, 2])`, even though the two signatures do the same job. Returning a function is not the mistake; putting the type parameter on the call that carries no argument is.

</details>

## Real-world reps

- [ ] Find one generic function you have written or use and check whether every type parameter appears in a parameter position; for any that only appear in the return type, write down what a caller currently has to type to use it.
- [ ] Take one function that returns a union such as `string | number` and rewrite one caller's post-call narrowing as the error message you would want instead, then check whether a conditional return type would actually produce that message or a worse one.
- [ ] Tomorrow: find one place in real code where `as const` is written at a call site to a function you also control, and check whether marking that function's type parameter `const` removes it.

## Going further

- [TypeScript Handbook, Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html): the source this lesson compresses, including the handbook's own account of type argument inference
- [TypeScript Handbook, Type Manipulation](https://www.typescriptlang.org/docs/handbook/2/keyof-types.html): `keyof` and indexed access, the vocabulary the `pick` examples above are built from
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
