---
title: 39. Template Literal Types
description: A string pattern the compiler checks, and the key names it can build
type: lesson
---

# Lesson 39. Template Literal Types

**Mission link:** Owning a codebase means a colleague who mistypes an event name or a CSS property finds out at the call site, from the compiler, rather than watching a handler silently never fire.
**Primary source:** [Template Literal Types, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/2/template-literal-types.html)
**Prerequisites:** [Lesson 38](0038-infer.md), [Lesson 10](0010-unions-and-literal-types.md)

## Warm-up

1. ▢ Lesson 10 gave you a literal type, one exact string standing as its own type, and a union of literals such as `"click" | "hover"` as the finite set of strings a variable may hold. Predict whether `` type Ev = `on${string}` `` describes a finite set of literals the same way, and say what happens when `"onClick"`, `"onclick"` and `"off"` are each assigned to it.

<details markdown="1"><summary>Check</summary>

It does not enumerate anything. `"click" | "hover"` is two named members and nothing else is a member; `` `on${string}` `` is a shape, every string that starts with `on` followed by any further characters, an effectively open-ended set rather than a short list. Verified: `const a: Ev = "onClick";` and `const b: Ev = "onclick";` both compile, since both start with `on`; `const c: Ev = "off";` fails:

```text
error TS2322: Type '"off"' is not assignable to type '`on${string}`'.
```

A template literal type is the pattern form of the literal type lesson 10 gave you: instead of naming one string, it names a shape of string, and the compiler checks a candidate against that shape the same way it checked a candidate against a literal.

</details>

## Know this

### The form: a pattern, not a value

A template literal type is written with backticks and `${...}` exactly like a JavaScript template string, except it appears in type position and every interpolated slot holds a type instead of a value. Tighten the warm-up's pattern using one of the intrinsic string types the next section introduces:

```ts
type Ev = `on${Capitalize<string>}`;
const good: Ev = "onClick";
const bad: Ev = "click";
```

`good` compiles. `bad` fails, verified on TypeScript 7.0.2:

```text
error TS2322: Type '"click"' is not assignable to type '`on${Capitalize<string>}`'.
```

Read that diagnostic closely, because it is unusually generous. It does not say "wrong type" or point at some internal representation; it prints the pattern itself, backticks and all, so the message is legible without opening the declaration that produced it. That is not true of most computed types, and it is one reason a template literal type is pleasant to work with even before it catches anything: when it rejects a value, the rejection reads like the rule it is enforcing.

### The intrinsic string types

Four case transforms exist purely as building blocks for template literal types: `Uppercase<S>`, `Lowercase<S>`, `Capitalize<S>` and `Uncapitalize<S>`. Verified: `Capitalize<"abc">` is `"Abc"`, `Uncapitalize<"Abc">` is `"abc"`, `Uppercase<"abc">` is `"ABC"`, `Lowercase<"ABC">` is `"abc"`. Nobody wrote these as ordinary generic types; they are compiler intrinsics, built in the same way `keyof` is, because the transform they perform is not expressible with the mapped and conditional machinery lessons 36 and 37 gave you. Treat them as fixed vocabulary rather than as a pattern to imitate.

### Composition with a union: where the combinatorics come from

Interpolating a union of literals, rather than plain `string`, produces the cross product of the arms. A small case, an event source crossed with an action:

```ts
type DomainEvent = "user" | "order" | "payment";
type Action = "created" | "updated" | "deleted";
type EventName = `${DomainEvent}:${Action}`;
```

`EventName` is not one pattern with two open slots; it is the nine concrete literals `"user:created"`, `"user:updated"`, and so on for every pairing. Verified by trying to assign a near miss:

```text
error TS2345: Argument of type '"user:createed"' is not assignable to parameter of type '"order:created" | "order:deleted" | "order:updated" | "payment:created" | "payment:deleted" | "payment:updated" | "user:created" | "user:deleted" | "user:updated"'.
```

The diagnostic lists all nine, in full, because that is genuinely what `EventName` is once both slots are literal unions: three members times three members. This is the mechanism to keep in view, because it is also the cost. Two unions of ten members each interpolated together produce not twenty but a hundred, and a third slot multiplies again. That multiplication, not any single evaluation, is how a template literal type turns expensive: the type itself grows combinatorially even though every individual member is trivial. Measuring what a particular type actually costs to check is lesson 42's job; the qualitative fact to carry from here is that composing several open-ended unions inside one template literal type is the design that runs into that cost, so reach for it with a bounded number of slots and arms you can picture, not as a way to enumerate something naturally unbounded.

### Building key names: the syntax behind lesson 36's getters

Lesson 36 showed a mapped type that renamed each key with `` `get${Capitalize<string & K>}` `` in its `as` clause and asked you to trust the result without asking how the renaming worked. Here is how. A template literal type can appear inside a mapped type's `as` clause, and when it does, it runs once per key, computing a new key name from the old one rather than transforming the value stored at that key:

```ts
interface Point { a: number; b: string }
type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };
declare const g: Getters<Point>;
const n: number = g.getA();
const s: string = g.getB();
```

Verified: this compiles, and `g.getA()` returns `number` while `g.getB()` returns `string`, exactly as lesson 36 showed. Assign `g.getA()` to a `string` and the mismatch surfaces as `error TS2322: Type 'number' is not assignable to type 'string'.`, which is the ordinary type check running on the value; the interesting part already happened at the key. The `string & K` is there because `keyof T` can include `number` and `symbol` alongside `string`, and `Capitalize` only accepts a string; intersecting with `string` narrows `K` to the string keys before capitalizing, and a non-string key silently contributes nothing to the mapped type rather than erroring. The mapped type itself, the `[K in keyof T as ...]` shape, belongs to lesson 36; this lesson only owns the template literal sitting inside the `as` clause.

### The caller who benefits

Return to `EventName` from the composition section, and give it a real call site:

```ts
function on(name: EventName, handler: () => void): void {
  // registers handler
}
on("user:created", () => {});
on("order:deleted", () => {});
on("user:createed", () => {});
```

The last call is a typo, one extra `e`, and it is rejected with the `TS2345` quoted above, at the call, before anything runs. Compare the alternative signature `function onLoose(name: string, handler: () => void): void {}`: the identical typo compiles cleanly, and the bug becomes a handler that never fires, discovered later and only by noticing an event nobody ever received. A hand-written union naming all nine combinations would have caught the same typo, but it has to be listed and kept in sync by hand every time a domain event or an action is added; `EventName` is generated from the two short unions it is built from, so adding `"refunded"` to `Action` widens every valid combination automatically. The caller here, whoever calls `on`, gets a better error for exactly the same amount of typing a `string` parameter would have asked for, and nobody has to maintain the expanded list separately. That is the whole case for this technique: it turns a class of typo from a silent runtime gap into a compile-time rejection, at no cost to how the call site is written.

### Where to stop

A template literal type can be paired with `infer`, lesson 38's subject, to take a string apart piece by piece: strip a prefix, pull out one section, recurse over the rest. That is real, and it is also the fastest way to turn this lesson's caller-benefit story into cleverness with no caller. A type that parses a route pattern, a format string, or a URL character by character is impressive to write and expensive to read, and the person maintaining it later inherits a type-level parser with none of the tooling a runtime parser has: no stack trace, no debugger, only a diagnostic naming whatever partial pattern it got stuck on. If a string genuinely needs to be parsed and validated, do that at run time, at the boundary lesson 31 already gave you a place for, with a real parser producing a real error message. Keep the template literal type for shapes you can state directly, a fixed prefix, a suffix, a small union crossed with another small union, and stop before it becomes a parser wearing a type declaration.

## Practice

1. ▢ Given `` type Slug = `${Lowercase<string>}-${number}` ``, predict whether `const a: Slug = "post-1"` and `const b: Slug = "Post-1"` each compile.

<details markdown="1"><summary>Check</summary>

`a` compiles: `"post"` is lowercase and `1` matches the `number` slot. `b` fails:

```text
error TS2322: Type '"Post-1"' is not assignable to type '`${Lowercase<string>}-${number}`'.
```

The reason is that `"Post"` has an uppercase letter and `Lowercase<string>` only matches strings already in lowercase: the intrinsic checks the shape of the literal, it does not lowercase it for you.

</details>

2. ▢ Given `type Size = "sm" | "md" | "lg"` and `type Variant = "primary" | "secondary"` and `` type Cls = `btn-${Size}-${Variant}` ``, predict how many distinct string literals `Cls` accepts.

<details markdown="1"><summary>Hint</summary>

Count the arms on each side of the interpolation separately, then combine them the way the composition section combined `DomainEvent` and `Action`.

</details>

<details markdown="1"><summary>Check</summary>

Six: three sizes times two variants, the cross product, the same mechanism as `EventName`. Assigning a near miss such as `"btn-sm-tertiary"` names all six in the diagnostic, exactly as the nine-member `EventName` diagnostic did.

</details>

3. ▢ The `Getters` mapped type from Know this is applied to `interface Empty {}`, an interface with no properties. Predict what `keyof Getters<Empty>` is.

<details markdown="1"><summary>Check</summary>

`never`. With no keys in `keyof Empty`, the mapped type's `as` clause has nothing to run the template literal on, so it produces no properties at all, and the resulting type's key set is empty, which TypeScript reports as `never`. The template literal only ever runs once per existing key; it cannot invent keys where there were none.

</details>

4. ▢ A teammate proposes replacing `EventName` with a plain `string` parameter "to keep things simple", arguing the runtime code already checks the event name against a list before dispatching. Name what the caller loses by that change, given the `on("user:createed", ...)` example from Know this.

<details markdown="1"><summary>Check</summary>

The caller loses the compile-time rejection at the call site; the typo becomes a value that type-checks fine and is only caught later, by whatever runtime check exists, if one runs before the handler is registered rather than after. Simplifying the type does not remove the mistake, it only moves the moment it is caught from the editor, before the code ships, to whenever the runtime list happens to run, which is strictly later and strictly more expensive to trace back to its cause.

</details>

5. ▢ A pull request adds `` type Route = `/${string}/${string}` `` together with a type using nested conditional types and `infer` to pull the two path segments back out as separate named types for use elsewhere. Say what is wrong with reviewing this as ordinary type-level work, and what the reviewer should ask for instead.

<details markdown="1"><summary>Check</summary>

This is the boundary the Where to stop section named: a type-level parser taking a string apart piece by piece, built from `infer` on a pattern, which is exactly the shape that is expensive to read and impossible to debug with ordinary tools when it goes wrong. The reviewer should ask why the two segments cannot be produced by parsing the actual route string at run time, at whatever boundary the routes arrive at, the way lesson 31 already taught, and reserve the template literal type for validating the shape of the whole string rather than for extracting its parts.

</details>

## Real-world reps

- [ ] Search a codebase for a function or component prop typed `string` where the actual values only ever come from a small, known set, such as an event name, a CSS class prefix, or an API path segment, and check whether a template literal type built from the existing literal unions would catch a typo a plain `string` currently accepts.
- [ ] Find a hand-written union that enumerates every combination of two smaller sets, such as a size crossed with a variant, and check whether replacing it with a template literal type over the two smaller unions keeps the same members while removing the need to update the combined list by hand.
- [ ] Tomorrow: find one type in a project you touch that takes a string apart with nested conditional types and `infer` rather than validating its shape, and ask whether a runtime parse at the boundary would serve the same caller with a debuggable error instead.

## Going further

- [Total TypeScript](https://www.totaltypescript.com/): worked examples building string-pattern types for real APIs, including where the pattern approach stops paying
- [Type Challenges](https://github.com/type-challenges/type-challenges): template literal puzzles worth doing as exercise, not as a model for a type a teammate has to review
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
