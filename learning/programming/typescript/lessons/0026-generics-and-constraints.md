---
title: 26. Generics and Constraints
description: A type parameter is a promise to the caller, and a constraint is what lets you keep it
type: lesson
---

# Lesson 26. Generics and Constraints

**Mission link:** A codebase accumulates type parameters that promise nothing to the caller reading them, and telling a generic that earns its place from one that is decoration keeps a signature honest for whoever calls it next.
**Primary source:** [Generics, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/2/generics.html)
**Prerequisites:** [Lesson 13](0013-function-types.md), [Lesson 14](0014-what-inference-already-knows.md)

## Warm-up

1. ▢ Lesson 10 said a union type permits only the operations every member supports, nothing more. Given `function bothLength(x: string | number[]): number { return x.length; }`, why does this compile even though `x` might be either a `string` or a `number[]`?

<details markdown="1"><summary>Check</summary>

Because `.length` is a member both `string` and `number[]` have, so it survives being read through the union; a member only one branch had would be refused. A type parameter with no constraint is this problem at its worst: it stands for a union of every type there is, so its shared surface is almost empty. This lesson is about what changes that, and about noticing when a type parameter was never buying anything at all.

</details>

## Know this

### What a type parameter is for

A value parameter names something the rest of the function can use; a type parameter names a type the rest of the *signature* can refer to, so it ties two or more positions together instead of describing either one alone. The smallest honest example:

```ts
function first<T>(xs: T[]): T {
  return xs[0];
}

const value = first([1, 2, 3]);
const label: string = value;
```

```text
error TS2322: Type 'number' is not assignable to type 'string'.
```

Nobody annotated anything. `first`'s parameter is typed `T[]`, the argument `[1, 2, 3]` is `number[]`, so `T` unifies with `number`, and the return type, also written as `T`, inherits that answer; assigning it to a `string` fails. This is lesson 14's contextual typing run in reverse: there, a position told the compiler what a bare callback parameter had to be; here, an argument tells the compiler what a type parameter has to be, and a caller who wrote no annotation still gets back a type precise enough to be rejected for the right reason.

### Why an unconstrained parameter can do almost nothing

```ts
function report<T>(x: T) {
  return x.length;
}
```

```text
error TS2339: Property 'length' does not exist on type 'T'.
```

Inside `report`, `T` stands for whatever type a caller chooses, so the compiler must accept this body running with `T` as `number`, `boolean`, `{}`, anything. `.length` is not guaranteed by every one of those, so it is refused, the same discipline lesson 10 applied to a union. That is why `first` above could only take a `T[]` in and hand a `T` back out, never touching what was inside.

### Constraints

```ts
function report<T extends { length: number }>(x: T) {
  return x.length;
}

report(42);
```

```text
error TS2345: Argument of type 'number' is not assignable to parameter of type '{ length: number; }'.
```

`report(x)` now compiles, because `x.length` is legal under the constraint: `T extends { length: number }` promises that whatever fills `T` has a `.length` that is a `number`. Calling with `42` is rejected, since a plain `number` has no such shape. A constraint is not a restriction on what the function may do; it is the contract you need in order to keep the promise the parameter made, sized to exactly what the body uses. `{ length: number }` is honest for a function that only reads `.length`; reaching for something wider buys nothing.

### The test: is this generic earning its place

Ask, of any type parameter: what does the caller learn from it that a concrete type or a union could not have said directly? If the answer is nothing, the parameter is decoration.

**First failure: the parameter appears once.**

```ts
function describe<T>(x: T): string {
  return typeof x;
}

const a: string = describe(42);
const b: string = describe("hi");
const c: string = describe({ n: 1 });
```

All three compile, and all three return a plain `string`. Nothing about `T` ever reaches the caller, because the return type is `string`, never `T`. Replace it with the concrete type that says exactly as much:

```ts
function describe(x: unknown): string {
  return typeof x;
}
```

The same three calls compile the same way, with the same result. `T` was never used for anything a plain `unknown` parameter could not do, so it was decoration, one more thing to read for nothing gained.

**Second failure: the caller must always supply the type argument by hand.**

```ts
function createEmptyList<T>(): T[] {
  return [];
}

const list = createEmptyList();
const n: number = list[0];
```

```text
error TS2322: Type 'unknown' is not assignable to type 'number'.
```

`createEmptyList` takes no argument, so nothing tells the compiler what `T` should be; it falls back to `unknown`, and `list[0]` is checked against that, not the `number` you had in mind. The call that does compile has to spell `T` out every time, `createEmptyList<number>()`, and if every call needs that, the type parameter saved nothing. The simpler signature skips the function entirely:

```ts
const list: number[] = [];
```

Same result, no type parameter, no function. This is lesson 14's own rule, restated for generics: an empty structure with a caller-chosen element type is exactly the case lesson 14 named for annotating.

Two tells that a type parameter is not earning its place: it appears once in the signature, or no call site can ever infer it. Either one means a concrete type, or the union from lesson 10, was the honest signature all along.

### Type argument inference and when to annotate it

Inference from an argument, as in `first` above, is the common case and usually needs no help. Occasionally it reaches an answer that is technically consistent but not the one you meant:

```ts
function firstOf<T>(xs: T[]): T {
  return xs[0];
}

const empty = firstOf([]);
const asNumber: number = empty;
const asString: string = empty;
```

Both compile, with no complaint about disagreeing on what `empty` is. `[]` carries no elements to infer from, so `T` unifies with `never`, the type inhabited by nothing, and `never` is assignable to every type, so both lines pass despite contradicting each other. Writing the type argument by hand fixes it:

```ts
const empty = firstOf<number>([]);
const asString: string = empty;
```

```text
error TS2322: Type 'number' is not assignable to type 'string'.
```

`empty` is genuinely `number` now, and the second assignment is correctly rejected. Needing this on every call, though, is the same signal as above: if inference can never reach the answer alone, ask again whether the type parameter earns its place.

### Defaults and multiple parameters

A type parameter can carry a default, used when nothing else determines it:

```ts
function makeSet<T = string>(items: T[] = []): Set<T> {
  return new Set(items);
}

const words = makeSet();
const nums = makeSet([1, 2, 3]);
```

`words` is `Set<string>`, from the default; `nums` is `Set<number>`, from the argument overriding it. A default is a stated fallback, a choice you wrote down, not a guess the compiler reached for the way it reached for `never` above.

Two type parameters compile the same way as one:

```ts
function pair<A, B>(a: A, b: B): [A, B] {
  return [a, b];
}
```

Nothing about the mechanics changes, but the earlier test now applies twice, separately. A second parameter earns its place only if it, too, appears more than once and ties together something the first did not already tie; adding one because a function takes two arguments is the single-use mistake wearing a second badge. Run the test on each letter in turn, never once for the pair.

Everything here stayed a plain function signature. A type parameter can also describe a transformation of a whole type rather than one call, which is what mapped types and conditional types do, and that goes wrong in new ways a constraint cannot catch. Stage 6 is where the arc returns to generics for that, and where the limit on how much type-level cleverness a signature should carry gets drawn.

## Practice

1. ▢ Predict the diagnostic, including its `TS` number.

   ```ts
   function last<T>(xs: T[]): T {
     return xs[xs.length - 1];
   }
   const value = last(["a", "b", "c"]);
   const n: number = value;
   ```

<details markdown="1"><summary>Check</summary>

`error TS2322: Type 'string' is not assignable to type 'number'.` The argument `["a", "b", "c"]` is `string[]`, so `T` unifies with `string`, and the return type inherits it. Nothing was annotated; the call site alone decided it.

</details>

2. ▢ Predict the diagnostic.

   ```ts
   function double<T>(x: T) {
     return x + x;
   }
   ```

<details markdown="1"><summary>Check</summary>

`error TS2365: Operator '+' cannot be applied to types 'T' and 'T'.` `T` could be substituted with a type `+` does not support, such as a plain object, so the operator is refused for all of them.

</details>

3. ▢ Predict whether each call compiles.

   ```ts
   function loud<T extends { toUpperCase(): string }>(x: T): string {
     return x.toUpperCase();
   }
   loud("hi");
   loud(42);
   ```

<details markdown="1"><summary>Check</summary>

`loud("hi")` compiles, since `string` has a matching `toUpperCase`. `loud(42)` gives `error TS2345: Argument of type 'number' is not assignable to parameter of type '{ toUpperCase(): string; }'.`, since a plain `number` does not.

</details>

4. ▢ This compiles with no error at all. Say what is wrong with it anyway, and give the simpler signature that replaces it.

   ```ts
   function idish<T>(x: T): boolean {
     return x !== null;
   }
   ```

<details markdown="1"><summary>Hint</summary>

Ask what a caller learns from `T` that a concrete parameter type would not have told them.

</details>

<details markdown="1"><summary>Check</summary>

Nothing. `T` appears once, in the parameter, and the return type is `boolean` regardless of what fills it, so no call learns anything from `T` it did not already know. The simpler signature is `function idish(x: unknown): boolean`, accepting the same calls with the same result.

</details>

5. ▢ Predict whether each `push` compiles, and say why.

   ```ts
   function wrap<T>(): T[] {
     return [];
   }
   const w = wrap();
   w.push(4);
   w.push("no");
   ```

<details markdown="1"><summary>Hint</summary>

Ask what, in this call, gives the compiler anything to infer `T` from.

</details>

<details markdown="1"><summary>Check</summary>

Both compile. `wrap` takes no argument, so nothing tells the compiler what `T` should be, and it falls back to `unknown`; `w` is `unknown[]`, and `push` accepts anything assignable to `unknown`, which is everything. Nothing caught the mismatch between `4` and `"no"`, the same failure `createEmptyList` had, and the same fixes apply: write `wrap<number>()` explicitly, or skip the function and write `const w: number[] = []` directly.

</details>

## Real-world reps

- [ ] Find one generic function you use and check whether its type parameter appears more than once; if it appears once, note what a concrete type or a union would have cost you instead.
- [ ] Find one call site that writes an explicit type argument, such as `<number>`, and check whether removing it still infers the same type, or whether the call genuinely could not have reached it alone.
- [ ] Tomorrow: pick one generic function that takes no arguments and returns something built from its type parameter, and see whether every call site is forced to write the type argument by hand.

## Going further

- [TypeScript Handbook, Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html): the source this lesson compresses, including generic interfaces and classes, left for later
- [TypeScript Handbook, Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html): the object-type shapes a constraint such as `{ length: number }` is drawn from
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
