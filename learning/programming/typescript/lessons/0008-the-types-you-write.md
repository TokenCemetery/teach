---
title: 8. The Types You Write
description: The annotation vocabulary, and a compiler that already objects before you configure it
type: lesson
---

# Lesson 8. The Types You Write

**Mission link:** Owning a codebase means knowing whether an annotation in it is load-bearing or noise, which starts with knowing exactly what each piece of type syntax claims.
**Primary source:** [Everyday Types, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html)
**Prerequisites:** [Lesson 7](0007-modules.md), [Lesson 1](0001-values-and-coercion.md)

## Warm-up

1. ▢ Name the seven primitive types lesson 1 gave you.

<details markdown="1"><summary>Check</summary>

`undefined`, `null`, `boolean`, `number`, `bigint`, `string`, `symbol`. Every one of them is also a type name, which is where this lesson starts.

</details>

## Know this

### The compiler already checks strictly

Run this with no flags and no configuration file anywhere near it:

```ts
function greet(x) {
  return x;
}
let s: string = null;
```

The compiler reports both of these, unasked:

```text
error TS7006: Parameter 'x' implicitly has an 'any' type.
error TS2322: Type 'null' is not assignable to type 'string'.
```

Nobody turned anything on. `tsc --all` states the mechanism: `noImplicitAny`, `noImplicitThis`, `strictBindCallApply`, `strictBuiltinIteratorReturn` and `strictFunctionTypes` default to `true` unless `strict` is explicitly set to `false`, an active choice against a strict default rather than a default you switch on.

A lot of writing about TypeScript, including older tutorials, tells you to flip strictness on as an early improvement. Against a current compiler there is nothing left to flip. Stage 3 takes the whole strictness configuration apart, flag by flag; stage 2 simply assumes strictness throughout, the way this example already does.

### The primitive annotations

Every primitive type from lesson 1 is also a type name. As an annotation, each one names the type of the thing on the left:

```ts
let name: string = "Ada";
let count: number = 12;
let done: boolean = false;
let cleared: null = null;
let missing: undefined = undefined;
let tag: symbol = Symbol("tag");
let big: bigint = 12n;
```

None of this is new about the values, only a new way to write down what lesson 1 already taught you to recognise.

### `any`, named and refused

`any` is also a type you can write, and it does something different from every other type here: it switches off checking for whatever value carries it.

```ts
let x: any = 42;
x.toUpperCase();   // no error, even though 42 has no such method
x = "hello";        // no error, any accepts any assignment
x();                 // no error, even calling a string
```

None of those three lines is caught, on a compiler that just caught a bare implicit parameter. `any` is not a wildcard type that matches everything safely; it is a hole in the type system, precisely where you put one. This arc treats reaching for `any` as a defect that needs explaining, not a tool you reach for when a type is inconvenient to write. Stage 3 teaches the type built for "unknown shape, must be checked before use", which behaves nothing like `any`.

### Array types

An array of strings can be written two ways, and they are the same type:

```ts
const a: string[] = ["x"];
const b: Array<string> = ["y"];
let c: string[] = b;   // compiles: same type either way
let d: Array<string> = a;
```

`string[]` is shorthand for `Array<string>`. Most code favours the shorthand; reach for `Array<T>` when the element type itself is awkward to write with brackets.

### Object types, and one gap worth seeing early

An object type can be written inline, listing each property's name and type:

```ts
type A = { name: string; age?: number };
type B = { name: string; age: number | undefined };

const a1: A = { name: "Ada" };   // compiles: age may simply be absent
const b1: B = { name: "Ada" };   // error TS2741: Property 'age' is missing
                                  // in type '{ name: string; }' but required in type 'B'
```

`age?: number` says the property may not exist at all. `age: number | undefined` says the property must exist, and its value may be `undefined`. Those read as near-synonyms and are not, which is exactly why `b1` fails while `a1` compiles. A stricter reading of the optional form exists, controlled by `exactOptionalPropertyTypes`, which is not part of `strict` and which stage 3 owns; with it on, the second form above is rejected with `TS2375`.

### Naming a shape with `type`

Writing the same inline object type at every call site is how a typo turns into three separate bugs. Give it a name once instead:

```ts
type User = { id: string; name: string };

function greet(user: User): string {
  return "hello " + user.name;
}

greet({ id: "1" });
// error TS2741: Property 'name' is missing in type '{ id: string; }' but required in type 'User'
```

The alias is not a new kind of type, only a name for one, and the diagnostic quotes that name back at you, which is most of the value: a mistake against `User` reads as a mistake against `User` everywhere it happens, rather than as a fresh unnamed mismatch each time.

### Where an annotation goes, and what it means there

A variable's annotation is a constraint the initialiser has to satisfy, checked once, right there:

```ts
let count: number = "five";
// error TS2322: Type 'string' is not assignable to type 'number'
```

`greet`'s parameter above is a different check. `user: User` is a demand on whoever calls `greet`, checked afresh at every call site, which is why `greet({ id: "1" })` fails at the call, not inside `greet`. A variable annotation checks one value; a parameter annotation checks every caller, for as long as the function exists. Lesson 14 argues for writing fewer of them than you might expect, once inference has been covered.

## Practice

1. ▢ Predict what each line reports, with no configuration file present.

   ```ts
   function id(x) {
     return x;
   }
   let n: number = undefined;
   ```

<details markdown="1"><summary>Check</summary>

`error TS7006: Parameter 'x' implicitly has an 'any' type.` and `error TS2322: Type 'undefined' is not assignable to type 'number'.`

Both fire with no flags set, because `noImplicitAny` and `strictNullChecks` are already on by default. There is nothing here to switch on.

</details>

2. ▢ Which of these compiles?

   ```ts
   let p: Array<number> = [1, 2, 3];
   let q: number[] = p;
   let r: Array<number> = q;
   ```

<details markdown="1"><summary>Hint</summary>

Ask whether `T[]` and `Array&lt;T&gt;` are two types or one written two ways.

</details>

<details markdown="1"><summary>Check</summary>

All three lines compile. `number[]` and `Array<number>` are the same type under two spellings, so every assignment between them is trivially fine.

</details>

3. ▢ Given `type Item = { sku: string; note?: string };`, which of these compiles?

   - a) `const i: Item = { sku: "a1" };`
   - b) `const i: Item = { sku: "a1", note: undefined };`
   - c) `const i: Item = { sku: "a1", note: "x" };`

<details markdown="1"><summary>Check</summary>

All three compile. `note?: string` permits the key to be absent (a), present with `undefined` (b), or present with a string (c); only a value of some other type is refused. A flag stage 3 covers can reject (b) too.

</details>

4. ▢ Predict the diagnostic, including its `TS` number.

   ```ts
   type Config = { host: string; port: number };
   function connect(c: Config) {}
   connect({ host: "localhost" });
   ```

<details markdown="1"><summary>Check</summary>

`error TS2741: Property 'port' is missing in type '{ host: string; }' but required in type 'Config'.`

The parameter's annotation is a demand on the caller, and this caller did not meet it. The alias name `Config` appears in the message because that is the type the demand was written against.

</details>

5. ▢ Why does this compile with no error at all, and what should you do instead?

   ```ts
   function total(items: any) {
     return items.length + items.price;
   }
   total("not a list of items");
   ```

<details markdown="1"><summary>Check</summary>

`any` switches off checking for `items` entirely, so `.length`, `.price`, and the call with a plain string all pass with no complaint, right up until this fails at runtime instead.

Write the real shape, such as `items: { price: number }[]`, and let the compiler check the body and every call site against it.

</details>

## Real-world reps

- [ ] Take a function you have written in plain JavaScript and add a parameter annotation and a return annotation to it. Then call it once with a value that violates each, and read the two diagnostics.
- [ ] Find a spot in code you know that reaches for `any`, or write one deliberately, and replace it with the narrowest object or array type that actually describes the value.
- [ ] Tomorrow: open a project that has no `tsconfig.json` and run the compiler on one of its files directly. Note every diagnostic that appears with no configuration at all, since that is the floor stage 3 builds on.

## Going further

- [TypeScript Handbook: The Basics](https://www.typescriptlang.org/docs/handbook/2/basic-types.html): how the compiler builds a type for a value before you annotate anything
- [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals): why `any` exists as an escape hatch rather than being removed
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
