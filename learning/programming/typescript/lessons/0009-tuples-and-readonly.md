---
title: 9. Tuples and readonly
description: A fixed length the compiler enforces on reads and forgets on push
type: lesson
---

# Lesson 9. Tuples and readonly

**Mission link:** Tuple lengths and `readonly` are confident-looking claims, and knowing exactly where each stops holding is what keeps you from trusting a guarantee that was never there.
**Primary source:** [Object Types, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/2/objects.html)
**Prerequisites:** [Lesson 8](0008-the-types-you-write.md), [Lesson 2](0002-objects-are-references.md)

## Warm-up

1. ▢ Lesson 2 showed that `readonly` erases at run time, so a rejected write is not itself protection against mutation. What tool from that lesson actually stops a mutation at run time, and what is its limit?

<details markdown="1"><summary>Check</summary>

`Object.freeze`. Its limit is that it is shallow: it freezes an object's own properties, not whatever those properties refer to.

</details>

## Know this

### Tuple types

A tuple type is an array type with a fixed length and a type pinned to each position:

```ts
const t: [number, string] = [1, "a"];
```

`t[0]` is `number`, `t[1]` is `string`, and there is no third position. A tuple element can be marked optional with `?` (`[number, string?]`), and a tuple can end with a rest element (`[string, ...number[]]`), the same syntax a function's parameter list uses. That is as far as this lesson goes with them.

### Where the length is enforced

Reading `.length` off a tuple gives the literal count, not `number`:

```ts
const t: [number, string] = [1, "a"];
const n: 2 = t.length;   // compiles: length is the literal type 2
```

An ordinary array's `.length` is `number`, since the array could be any size; a tuple's is a specific literal, since the compiler knows exactly how many positions it declared.

That same bookkeeping rejects a read past the end:

```ts
const x = t[5];
```

```text
error TS2493: Tuple type '[number, string]' of length '2' has no element at index '5'.
```

And it rejects pulling a third binding out of a two-element tuple by destructuring, for the same reason:

```ts
const [a, b, c] = t;
```

```text
error TS2493: Tuple type '[number, string]' of length '2' has no element at index '2'.
```

Both diagnostics name the length and the offending index, because both are the same check: is this position inside the tuple.

### Where it stops being enforced

```ts
t.push(3);
```

This compiles. No diagnostic, though it visibly grows the tuple past the length just enforced above.

A tuple has no separate existence at run time: `[1, "a"]` is an ordinary JavaScript array, and the fixed length is something the compiler tracks about indexing, not a fact stamped onto the value. `push` is a method the array type gives to every array, tuples included, and it was never wired to check a tuple's promised length. Reads go through index checking; `push`, `pop` and `splice` go through the array type's own methods, untouched by it.

That is lesson 2's pattern under a different name: a compile-time restriction with no run-time counterpart. There it vanished once a value left type-checked code; here it never covered `push` at all, even inside type-checked code, because the fixed length is enforced about specific operations, not the value as a whole.

### readonly

`readonly` on an array type removes the mutating methods rather than shrinking anything:

```ts
const a: readonly number[] = [1, 2];
a.push(3);
```

```text
error TS2339: Property 'push' does not exist on type 'readonly number[]'.
```

`readonly number[]` simply never declared `push`, so this is an ordinary "no such property" error, not a special mutation check.

On an object property, `readonly` blocks the assignment directly:

```ts
type P = { readonly a: number };
const p: P = { a: 1 };
p.a = 2;
```

```text
error TS2540: Cannot assign to 'a' because it is a read-only property.
```

### The hole in readonly

This part is worth slowing down for. Take a value whose type is readonly and hand it to something typed without the modifier:

```ts
type RO = { readonly a: number };
type MU = { a: number };
declare const ro: RO;
const m: MU = ro;
m.a = 99;   // no error anywhere in this file
```

That compiles, and the mutation through `m` draws no diagnostic either. `readonly` is not part of what the compiler checks when deciding whether one object type is assignable to another; it checks that the properties exist and line up in type, and drops the modifier at the boundary. Lesson 11 names the general rule this is one instance of; for now, the instance is enough: a function accepting the mutable shape can receive your readonly object and mutate it, unreported.

Do not generalise that hole further than it goes, because it is specific to object properties. A readonly **array** is not assignable to a mutable one, verified:

```text
error TS4104: The type 'readonly number[]' is 'readonly' and cannot be assigned to the mutable type 'number[]'
```

A readonly tuple gives the same `TS4104`. The reverse direction compiles, as it should, since handing a mutable array to something that promises not to change it is safe. So `readonly` is part of assignability for arrays and tuples and is not part of it for object properties, which is worth holding as two separate facts rather than one rule: the modifier you are most likely to reach for on an object is the one the compiler will forget at the boundary.

Combined with lesson 2's fact that `readonly` erases at run time, the guarantee's shape is precise: enforced where you use a value under its readonly-typed name, forgotten where it is handed to code typed without the modifier. It documents intent and catches your own accidental writes rather than defending a boundary. Stage 5 takes that defence seriously; this lesson only asks you to stop expecting `readonly` to provide it alone.

### as const

`as const` gets you a literal type and a readonly type on a value at once, instead of choosing between them:

```ts
const point = [3, 4] as const;
```

`point` is not `number[]`, and not even a mutable tuple; its type is `readonly [3, 4]`, a readonly tuple with each element narrowed to its own literal value.

```ts
point.push(5);
```

```text
error TS2339: Property 'push' does not exist on type 'readonly [3, 4]'.
```

```ts
point[0] = 9;
```

```text
error TS2540: Cannot assign to '0' because it is a read-only property.
```

Both diagnostics are the ones already explained; `as const` introduces no new rule, only a compact way to ask for a tuple that is fixed, readonly and literal at once. Lesson 10 owns literal types; here it is only the label on `3` and `4`.

## Practice

1. ▢ Predict the result of each line.

   ```ts
   const t: [number, string, boolean] = [1, "a", true];
   const n: 3 = t.length;
   const x = t[3];
   ```

<details markdown="1"><summary>Check</summary>

Line 2 compiles: `t.length` is the literal type `3`. Line 3 fails:

```text
error TS2493: Tuple type '[number, string, boolean]' of length '3' has no element at index '3'.
```

</details>

2. ▢ Predict what happens, including what `t` looks like afterwards.

   ```ts
   const t: [number, string] = [1, "a"];
   t.push(99);
   console.log(t);
   ```

<details markdown="1"><summary>Check</summary>

It compiles with no diagnostic, and prints `[ 1, 'a', 99 ]`. `push` belongs to the array type, never checked against the declared length, so the array genuinely grows while its type still claims two.

</details>

3. ▢ Which line fails, and with what diagnostic?

   ```ts
   function sumAll(nums: readonly number[]): number {
     nums.sort();
     return nums.reduce((total, n) => total + n, 0);
   }
   ```

<details markdown="1"><summary>Check</summary>

`nums.sort()` fails:

```text
error TS2339: Property 'sort' does not exist on type 'readonly number[]'.
```

`reduce` is fine, since it only reads. `readonly number[]` simply has no `sort`, `push`, `splice` or any other mutating method.

</details>

4. ▢ Predict whether this compiles, and what it prints.

   ```ts
   type Point = { readonly x: number; readonly y: number };

   function shiftRight(p: { x: number; y: number }) {
     p.x += 10;
   }

   const origin: Point = { x: 0, y: 0 };
   shiftRight(origin);
   console.log(origin.x);
   ```

<details markdown="1"><summary>Hint</summary>

Ask whether `readonly` is one of the things the compiler checks when deciding if `Point` is assignable to `shiftRight`'s parameter type.

</details>

<details markdown="1"><summary>Check</summary>

It compiles with no diagnostic, and prints `10`. `readonly` is not part of object-type assignability, so `Point` is assignable to the unmarked parameter type, `shiftRight` mutates `origin.x` through it, and `origin` really changes despite its own type declaring `x` readonly.

</details>

5. ▢ Predict which lines compile.

   ```ts
   const rgb = [255, 0, 128] as const;
   const [r, g, b] = rgb;
   rgb.push(1);
   ```

<details markdown="1"><summary>Check</summary>

The destructuring compiles: `rgb`'s type is the three-element readonly tuple `readonly [255, 0, 128]`, so pulling out three bindings is exactly at the length. `rgb.push(1)` fails:

```text
error TS2339: Property 'push' does not exist on type 'readonly [255, 0, 128]'.
```

</details>

## Real-world reps

- [ ] Take a tuple type you would write for a real pair, such as `[string, number]`, and call `.push` on a value of that type. Confirm it compiles, then decide whether you would rely on that tuple staying at its declared length.
- [ ] Find a function in code you know that takes an object type without `readonly`, and check whether anything passes it a value whose own type marks that property `readonly`. If so, that is this lesson's hole, live.
- [ ] Tomorrow: take one array or tuple returned from a function you own, add `readonly` to its return type, and see what breaks, or quietly does not, at every call site.

## Going further

- [Object Types, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/2/objects.html): tuples, `readonly` properties, `ReadonlyArray` and `readonly` tuple types, in full
- [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals): why the type system accepts holes like this rather than chasing full soundness
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
