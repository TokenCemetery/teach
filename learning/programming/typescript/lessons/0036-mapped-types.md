---
title: 36. Mapped Types
description: Transform every property of a type at once, and remove the ones you do not want
type: lesson
---

# Lesson 36. Mapped Types

**Mission link:** A type copied by hand from another drifts the moment the source gains a field the copy does not, and a mapped type is how a codebase you own turns that drift into a compile error instead of a silent gap.
**Primary source:** [Mapped Types, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/2/mapped-types.html)
**Prerequisites:** [Lesson 26](0026-generics-and-constraints.md), [Lesson 28](0028-interface-or-type.md)

## Warm-up

1. ▢ Lesson 26 asked, of a type parameter, what the caller learns from it that a concrete type could not have said directly. Every generic you have written so far used a type parameter to stand for one value's type in one function signature. What would it mean for a type parameter to stand for a whole type, so the thing produced is a new type rather than a new value?

<details markdown="1"><summary>Check</summary>

It means writing something that takes a type as its argument and hands back a type, rather than a function that takes a value and hands back a value. That is a mapped type: it looks like a generic, `Opt<T>` or `Getters<T>` below, but what comes out is a shape, not a number or a string. The benefit is lesson 26's test aimed at a type instead of a value: nobody reading `Opt<Config>` has to trust someone kept it in step with `Config`, because it is computed from `Config` every time.

</details>

## Know this

### `keyof` and indexed access

Two operators do all the work in this lesson.

```ts
type Pair = { a: number; b: string };
type Keys = keyof Pair;
type AType = Pair["a"];

const bad: Keys = "z";
const wrong: AType = "not a number";
```

```text
error TS2322: Type '"z"' is not assignable to type 'keyof Pair'.
error TS2322: Type 'string' is not assignable to type 'number'.
```

`keyof Pair` is the union of `Pair`'s property names, `"a" | "b"`, and the first diagnostic proves it: `"z"` is rejected as not one of the two names `Pair` declares, even though the message names the union by its alias rather than spelling the literals out. `Pair["a"]` is `number`, so the second diagnostic rejects a `string` just as it would against a bare `number`. `keyof T` for the names and `T[K]` for a property's type are the pair every mapped type is made of.

### The mapped type: transforming every property at once

`{ [K in keyof T]: ... }` iterates every key `keyof T` produces, describing the whole shape once rather than property by property.

```ts
type Opt<T> = { [K in keyof T]?: T[K] };
type OptPair = Opt<Pair>;

const p: OptPair = {};
```

This compiles with no diagnostic. `Pair` itself would refuse `{}`, since both properties are required, but `OptPair` accepts it because the `?` inside the mapped type made every property optional.

A modifier written with a leading `-` removes it instead of adding it, which matters when the source already carries one you want gone:

```ts
type Source = { readonly a?: number };
type Mut<T> = { -readonly [K in keyof T]-?: T[K] };
type MutSource = Mut<Source>;

const s: Source = { a: 1 };
const bad: number = s.a;
s.a = 2;

const m: MutSource = { a: 1 };
const n: number = m.a;
m.a = 2;
```

```text
error TS2322: Type 'number | undefined' is not assignable to type 'number'.
error TS2540: Cannot assign to 'a' because it is a read-only property.
```

Both diagnostics are on `s`: it is optional, so reading it is `number | undefined`, and it is `readonly`, so assigning to it fails. `m` has neither problem, because `-?` and `-readonly` removed both modifiers, leaving a plain, writable `number`. This is not a novelty: the standard library's own `Required<T>` is `{ [P in keyof T]-?: T[P] }`, the same subtraction just verified, and a "mutable" variant dropping `readonly` is the identical trick the other direction.

### Key remapping with `as`

Everything so far kept the same keys and changed only what each one may hold. Adding `as` after the loop variable changes the key itself:

```ts
type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };
type PairGetters = Getters<Pair>;

declare const g: PairGetters;
const wrong: string = g.getA();
```

```text
error TS2322: Type 'number' is not assignable to type 'string'.
```

`PairGetters` has no `a` or `b`; it has `getA` and `getB`, each a function returning the original property's type, so `g.getA()` is `number` and the assignment to `string` is refused. (`string & K` guards against `keyof T` including `number` or `symbol`, since `Capitalize` needs a `string`.) The backtick template that builds the new name is a template literal type, which lesson 39 covers on its own; here it is only the tool that spells the new key. `as` is where a mapped type stops merely transforming values and starts changing the shape's keys.

### Filtering by remapping to `never`

Remapping a key to `never` makes it vanish, and it is the single most useful thing in this lesson because it turns a mapped type from something that only transforms into something that selects.

```ts
type OnlyNums<T> = { [K in keyof T as T[K] extends number ? K : never]: T[K] };

function useOnlyNums<P>(o: OnlyNums<P>) {
  const y = o.b;
}
```

```text
error TS2339: Property 'b' does not exist on type 'OnlyNums<P>'.
```

`T[K] extends number ? K : never` is a conditional type; lesson 37 owns how one works and how it behaves over a union. Here it is only the switch, decided per key, between keeping the name (`K`) and discarding it (`never`). A key remapped to `never` is dropped entirely, so `OnlyNums<T>` keeps only the numeric properties, and reading anything else is a compile error naming the property, not a runtime surprise.

### The caller who benefits

Take a config type that grows over time.

```ts
type Config = { host: string; port: number; retries: number };

type ConfigPatchByHand = {
  host?: string;
  port?: number;
};

function applyByHand(patch: ConfigPatchByHand) {}

const fullUpdate = { host: "x", port: 1, retries: 5 };
applyByHand(fullUpdate);
```

This compiles with no diagnostic. `ConfigPatchByHand` was written when `Config` had only `host` and `port`; `retries` arrived later, and nobody updated the hand-written patch type. Passing `fullUpdate`, which carries `retries`, produces no warning: the field is structurally invisible, silently accepted and then ignored. The mapped alternative:

```ts
type PatchHandlers<T> = { [K in keyof T]: (value: T[K]) => void };

const handlers: PatchHandlers<Config> = {
  host: (v: string) => {},
  port: (v: number) => {},
};
```

```text
error TS2741: Property 'retries' is missing in type '{ host: (v: string) => void; port: (v: number) => void; }' but required in type 'PatchHandlers<Config>'.
```

`PatchHandlers<Config>` is computed from `Config` directly, so its third property arrived with no edit needed. That is the caller's benefit: with the hand-written type, a new field on `Config` is a silent gap; with the mapped type, the same change is a compile error at every place that has not handled it yet.

### Where to stop

Every example above passes a test worth naming: can you say what the type does in one sentence. `Opt<T>` makes every property optional; `OnlyNums<T>` keeps only the numeric ones; `Getters<T>` turns each property into a method returning it. Each earned that sentence by doing one thing, not several at once. Layering `as`, a conditional and a template literal together can still verify correctly and still cost more to read than the duplication it removed would have cost to maintain; stage 6's job is an API whose types serve their callers and stop before cleverness, and this is where that stopping starts. Lesson 28 already established that a mapped type, like a conditional type, is not a shape `interface` can express, so here `type` is not merely preferred, it is the only option. Lesson 37 takes up the conditional type itself, lesson 38 covers `infer`, and lesson 39 covers the template literal type used above as its own subject.

## Practice

1. ▢ Predict the diagnostic, including its `TS` number.

   ```ts
   type Point = { x: number; y: number };
   type Coord = keyof Point;
   type XType = Point["x"];
   const bad: XType = "nope";
   ```

<details markdown="1"><summary>Check</summary>

`error TS2322: Type 'string' is not assignable to type 'number'.` `Point["x"]` is `number`, so assigning a string literal to it fails the same way it would against a bare `number` annotation.

</details>

2. ▢ Predict whether each of these compiles.

   ```ts
   type User = { id: number; name: string };
   type Opt<T> = { [K in keyof T]?: T[K] };
   type OptUser = Opt<User>;

   const u1: OptUser = {};
   const u2: User = {};
   ```

<details markdown="1"><summary>Check</summary>

`u1` compiles: `Opt<T>` made every property of `User` optional, so `OptUser` accepts `{}`. `u2` fails with `error TS2739: Type '{}' is missing the following properties from type 'User': id, name`, because plain `User` still requires both.

</details>

3. ▢ Predict whether this compiles, then say what changes if `-readonly` is removed from `Mut` but `-?` stays.

   ```ts
   type Flags = { readonly enabled?: boolean };
   type Mut<T> = { -readonly [K in keyof T]-?: T[K] };
   type MutFlags = Mut<Flags>;

   const f: MutFlags = { enabled: true };
   f.enabled = false;
   ```

<details markdown="1"><summary>Check</summary>

It compiles with no diagnostic: `-readonly` and `-?` each removed one modifier, so `enabled` is a plain, writable `boolean`. Keeping `-?` but dropping `-readonly` would leave `enabled` required but still `readonly`, so `f.enabled = false` would fail with `error TS2540: Cannot assign to 'enabled' because it is a read-only property.`

</details>

4. ▢ Predict the type of `g.getWidth()` and whether the last line compiles.

   ```ts
   type Shape = { width: number; height: number };
   type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };
   type ShapeGetters = Getters<Shape>;

   declare const g: ShapeGetters;
   const w: number = g.getWidth();
   const wrong: string = g.getHeight();
   ```

<details markdown="1"><summary>Check</summary>

`g.getWidth()` is `number`, matching `width`'s type, so `const w` compiles. `getHeight` also returns `number`, since `height` is `number`, so assigning its result to a `string` fails: `error TS2322: Type 'number' is not assignable to type 'string'.` `ShapeGetters` has no property named `width` or `height` at all; both were remapped.

</details>

5. ▢ Predict the diagnostic, including its `TS` number, and say why the property named in it is missing rather than merely optional.

   ```ts
   type OnlyStrings<T> = { [K in keyof T as T[K] extends string ? K : never]: T[K] };

   function useOnlyStrings<S>(o: OnlyStrings<S>) {
     const y = o.count;
   }
   ```

<details markdown="1"><summary>Hint</summary>

Ask what happens to a key when the conditional in its `as` clause evaluates to `never`, rather than to a value that happens to be absent at runtime.

</details>

<details markdown="1"><summary>Check</summary>

`error TS2339: Property 'count' does not exist on type 'OnlyStrings<S>'.` A key remapped to `never` is not an optional property that might be `undefined`; it is removed from the keys entirely, the same way `b` disappeared from `OnlyNums` above. `count` survives only if its value type extends `string`, which a count almost never does.

</details>

## Real-world reps

- [ ] Find one type you maintain that was copied by hand from another, such as a "partial update" or "public view" shape, and check whether a mapped type built from the original would have caught its last drift.
- [ ] Take one mapped type you write this week and apply the one-sentence test from "Where to stop"; if you cannot write the sentence, look for the single `as` clause or conditional doing too much at once.
- [ ] Tomorrow: pick one built-in you have used without reading its definition, `Partial`, `Required`, `Readonly` or `Pick`, and open its source to see which of today's techniques it is built from.

## Going further

- [TypeScript Handbook, Keyof Type Operator](https://www.typescriptlang.org/docs/handbook/2/keyof-types.html) and [Indexed Access Types](https://www.typescriptlang.org/docs/handbook/2/indexed-access-types.html): the two operators this lesson opened with
- [Type Challenges](https://github.com/type-challenges/type-challenges): exercise for the mechanism, not a model for a type you would put in front of a reviewer
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
