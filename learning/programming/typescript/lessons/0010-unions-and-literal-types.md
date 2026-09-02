---
title: 10. Unions and Literal Types
description: A value with more than one possible type, and the widening that throws the interesting one away
type: lesson
---

# Lesson 10. Unions and Literal Types

**Mission link:** Most values in a codebase are one of a few known shapes, not any single fixed type, and a union is how you write that down honestly.
**Primary source:** [Everyday Types, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html)
**Prerequisites:** [Lesson 8](0008-the-types-you-write.md), [Lesson 1](0001-values-and-coercion.md)

## Warm-up

1. ▢ Lesson 1 gave you `null` and `undefined` as two different kinds of nothing. Which one does the language produce on its own, and which one does a programmer write deliberately?

<details markdown="1"><summary>Check</summary>

`undefined` is what the language produces: an unassigned variable, a missing property, a function with no `return`. `null` is what a programmer writes to mean "deliberately empty". That distinction matters again below, where both can appear as members of a union.

</details>

## Know this

### A union is a promise about what a value might be

`string | number` reads as "a string or a number", the ordinary way to type a value that can genuinely arrive as either:

```ts
function formatId(id: string | number) {
  console.log(id.toString());
}
```

That compiles. This does not:

```ts
function shout(id: string | number) {
  console.log(id.toUpperCase());
}
// error TS2339: Property 'toUpperCase' does not exist on type 'string | number'.
//   Property 'toUpperCase' does not exist on type 'number'.
```

The rule is not arbitrary: `id` might be a `number` at run time, and `toUpperCase` does not exist on `number`, so calling it would fail for half the values the type admits. The compiler only lets you use what every member of a union supports in common. Getting the rest back means narrowing to one member first, lesson 12's job. For now, a union costs you access until you shrink it, and that cost is the point: it forces code that handles a union to actually handle every member.

### Literal types: a value as a type

Lesson 8 covered `string`, `number` and `boolean` as types. A specific string, number or boolean value can be a type too:

```ts
let ok: true = true;
ok = false;
// error TS2322: Type 'false' is not assignable to type 'true'.

let n: 42 = 42;
n = 43;
// error TS2322: Type '43' is not assignable to type '42'.
```

`true` and `42` are types with exactly one value each, not very useful alone. What is useful is a union of several literals, since it says "one of these specific values" rather than "any string at all":

```ts
type Level = "low" | "medium" | "high";
let lv: Level = "medium";
lv = "extreme";
// error TS2322: Type '"extreme"' is not assignable to type 'Level'.
```

`Level` accepts exactly three strings and no others. This is the single shape you will reach for most in ordinary TypeScript, for a status, a mode, a size, anywhere the real set of legal values is small and known. It reads better than `string` and catches a typo that `string` never would.

### Widening: why a `let` throws the literal away

Assign a literal to a `let` and something happens that a beginner rarely expects:

```ts
let s = "hello";
const t: "hello" = s;
// error TS2322: Type 'string' is not assignable to type '"hello"'.
```

`s` was initialised with the literal `"hello"`, yet its inferred type is the general `string`. That is widening, not the compiler failing to notice the literal: `s` is a `let`, so it can be reassigned to any other string later, and inferring `"hello"` for a binding that might soon hold `"goodbye"` would make every later use of `s` fight the type. The compiler infers a type that stays true for the binding's whole life.

Change one keyword and the picture reverses:

```ts
const s = "hello";
const t: "hello" = s;
```

This compiles. A `const` cannot be reassigned, so `"hello"` is not just its current value but the only value `s` will ever hold, and the compiler keeps the literal it has no reason to discard.

### Widening inside an object literal, even one held in a `const`

The same thing happens to a property, and here the `const` on the outside does not help:

```ts
const o = { kind: "a" };
const k: "a" = o.kind;
// error TS2322: Type 'string' is not assignable to type '"a"'.
```

`o` itself cannot be reassigned, but `o.kind` is an ordinary mutable property, and nothing stops `o.kind = "b"` on the next line. So `kind` widens to `string` for the same reason `s` did: its type has to stay true for as long as the property can hold a different value.

`as const` fixes it by removing the mutability the widening rule was reacting to:

```ts
const o = { kind: "a" } as const;
const k: "a" = o.kind;
```

This compiles. `as const` marks every property, recursively, as `readonly` and infers each one's literal type instead of its general type. With no assignment possible, there is nothing left for the general type to protect against, so the compiler keeps `"a"`. That is as far as this lesson takes `as const`; the assignability hole in `readonly` itself is lesson 9's.

### Where this bites in practice

The commonest place a beginner meets widening is a function that returns a plain object, passed to another that wants a specific literal:

```ts
type Shape = { kind: "circle"; radius: number };
function area(s: Shape) { /* ... */ }

function makeCircle(radius: number) {
  return { kind: "circle", radius };
}

area(makeCircle(2));
// error TS2345: Argument of type '{ kind: string; radius: number; }' is not assignable to parameter of type 'Shape'.
//   Types of property 'kind' are incompatible.
//     Type 'string' is not assignable to type '"circle"'.
```

`string` and `"circle"` look like they should obviously match, since the object plainly holds `"circle"`. The mismatch is `makeCircle`'s inferred return type, where `kind` widened to `string` with no reason to stay narrow. Add `as const` to the returned object, or annotate the return type as `Shape`, and the call compiles.

### `null` and `undefined` in a union

Lesson 1's two empties can sit inside a union like any other member, and lesson 8's strictness means neither is silently accepted where it was not asked for:

```ts
function greet(name: string | null) {
  return name.toUpperCase();
}
// error TS18047: 'name' is possibly 'null'.
```

`string | null` means exactly that: a string, or `null`, and nothing entitles you to call a string method until `null` is ruled out, which is lesson 12's job. Without the union, plain `string` refuses `null` outright:

```ts
let a: string;
a = null;
// error TS2322: Type 'null' is not assignable to type 'string'.
```

Both diagnostics come from the same strict defaults lesson 8 established. Neither empty gets a free pass into a type that did not ask for it.

## Practice

1. ▢ Given `function id(x: string | boolean) { return x; }`, which of these compiles inside the function body: `x.length`, `x.toString()`, `x.valueOf()`?

<details markdown="1"><summary>Check</summary>

Only `x.toString()` and `x.valueOf()`. Both `string` and `boolean` have those methods, so the union's common ground includes them. `length` exists on `string` but not `boolean`, so `x.length` fails: `error TS2339: Property 'length' does not exist on type 'string | boolean'.  Property 'length' does not exist on type 'false'.`

</details>

2. ▢ `type Weekday = "mon" | "tue" | "wed" | "thu" | "fri";` Predict whether each compiles: `let d: Weekday = "mon";` and `d = "sat";`.

<details markdown="1"><summary>Check</summary>

The first line compiles. The second reports `error TS2322: Type '"sat"' is not assignable to type 'Weekday'.`, because `"sat"` is not one of the five literals the union names.

</details>

3. ▢ Predict the result of each line.

   ```ts
   let x = 10;
   const y: 10 = x;
   ```

<details markdown="1"><summary>Hint</summary>

Ask whether `x` can be reassigned, and what that means for the type the compiler infers for it.

</details>

<details markdown="1"><summary>Check</summary>

`error TS2322: Type 'number' is not assignable to type '10'.` `x` is a `let`, so the compiler widens its inferred type to `number` rather than keeping `10`, since `x` might be reassigned to any other number later.

</details>

4. ▢ Predict whether this compiles, and if not, name the fix that requires the smallest change.

   ```ts
   const settings = { mode: "dark" };
   const m: "dark" = settings.mode;
   ```

<details markdown="1"><summary>Check</summary>

It does not compile: `error TS2322: Type 'string' is not assignable to type '"dark"'.` `settings` is a `const`, but `settings.mode` is still a mutable property, so it widens to `string` regardless. Change the literal to `{ mode: "dark" } as const` and the property keeps its literal type, so the assignment compiles.

</details>

5. ▢ Predict both diagnostics, with their `TS` numbers.

   ```ts
   function show(v: string | null | undefined) {
     console.log(v.length);
   }
   let s: string = undefined;
   ```

<details markdown="1"><summary>Check</summary>

`error TS18049: 'v' is possibly 'null' or 'undefined'.` and `error TS2322: Type 'undefined' is not assignable to type 'string'.` A union missing only one empty reports a narrower diagnostic, `TS18047` for `null` alone or `TS18048` for `undefined` alone, which is why the number changes with the union.

</details>

## Real-world reps

- [ ] Find a function that accepts more than one type for a parameter, whether written as a union already or as `any` standing in for one. Write it as an explicit union and see what the compiler now refuses in the function body.
- [ ] Take a status or category field currently typed `string` and replace it with a union of the literal values it actually takes. Read every call site that now fails, since each was a value the field was never meant to hold.
- [ ] Tomorrow: write a function that builds and returns an object with a fixed `kind`-like property, call it somewhere expecting a specific literal, and read the diagnostic naming the widened type before adding `as const`.

## Going further

- [TypeScript Handbook: Everyday Types, Literal Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#literal-types): the section this lesson compresses
- [TypeScript Handbook: Everyday Types, Working with Union Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#working-with-union-types): the same restriction this lesson teaches, from the source
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
