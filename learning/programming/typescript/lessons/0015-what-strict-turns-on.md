---
title: 15. What strict Turns On
description: Seven checks behind one flag, each with a failure it exists to catch
type: lesson
---

# Lesson 15. What strict Turns On

**Mission link:** Owning a codebase means being able to say which of seven checks caught a given error, since that is what decides whether the error is a bug worth fixing or a check worth reconsidering.
**Primary source:** [TSConfig Reference, TypeScript](https://www.typescriptlang.org/tsconfig/#strict)
**Prerequisites:** [Lesson 14](0014-what-inference-already-knows.md), [Lesson 8](0008-the-types-you-write.md)

## Warm-up

1. ▢ Lesson 8 ran `tsc` with no configuration file and no flags at all, and it still reported `TS7006` for an untyped parameter and `TS2322` for `null` assigned to `string`. What was already switched on to make that happen?

<details markdown="1"><summary>Check</summary>

Nothing was switched on by hand. `noImplicitAny` and `strictNullChecks` both default to `true` unless `strict` is explicitly set to `false`, so a compiler with no configuration at all is already checking both. This lesson names the rest of what was already running and takes each piece apart on its own.

</details>

## Know this

### `strict` is a set, not a level

`strict` is not a checking behaviour of its own. It is a single switch that turns on a named group of individually addressable flags, each checking something different, each of which can be turned off on its own while every other one stays on. The group is not fixed, either: running `tsc --all` against this compiler lists eight flags carrying the note "default: true, unless strict is false", one more than the seven catalogued below, because `strictBuiltinIteratorReturn` has joined the family, and the family has grown before across TypeScript's history. So `strict: true` in a configuration does not mean the same thing across compiler versions, since upgrading can quietly add a check that was never there before.

### The seven checks, catalogued

Each of these fails on its own, with `strict false` everywhere else, and each fails for a different reason. This is a catalogue to look things up in, not seven essays.

**`noImplicitAny`** (`TS7006`). `function f(x) { return x; }` leaves `x` with no annotation and nothing to infer it from. It catches a parameter that silently became `any`, so every call to `f` is unchecked, because nobody said what would arrive.

**`strictNullChecks`** (`TS2322`). `const s: string = null;` assigns `null` to a type that never said it could hold one. It catches the most common runtime crash in ordinary JavaScript: reading a property off a value that turned out to be `null` or `undefined`.

**`strictFunctionTypes`** (`TS2322`).

```ts
type H = (x: string | number) => void;
const h: H = (x: string) => {};
```

`H` promises callers they may pass a `string` or a `number`; `h` only handles a `string`. It catches a callback that cannot handle everything its own declared type promises callers may send.

**`strictBindCallApply`** (`TS2345`). `f.call(undefined, "no")`, where `f` takes a `number`, checks arguments passed through `call`, `bind`, and `apply` against the original function's parameters. It catches the mismatch a direct call, `f("no")`, would already report, which these three methods would otherwise wave through untyped.

**`strictPropertyInitialization`** (`TS2564`). `class C { a: number; }` declares a field with no initialiser and nothing setting it in the constructor. It catches a field that reads as `number` everywhere in the class body but is actually `undefined` until some code path remembers to set it.

**`noImplicitThis`** (`TS2683`). `this.v`, used inside a plain nested function with no receiver at its call site, has no declared type for `this` to check against. It catches a `this` about to be `undefined` at runtime, before it gets there.

**`useUnknownInCatchVariables`** (`TS2322`). `catch (e) { const s: string = e; }` assigns a caught value, whose shape nobody can predict, straight into a `string`. It catches code that assumes the shape of whatever got thrown; lesson 17 covers narrowing it safely.

### The one that is load-bearing

Six of those seven add a check on top of a type system that otherwise stays the same. `strictNullChecks` is different: turn it off and `null` and `undefined` become members of every type in the program, not merely unchecked against them.

```ts
class Widget {}
let w: Widget = null;
let n: number = undefined;
```

With `strict false`, both lines compile, not because a check was skipped but because nothing in the type system distinguishes `Widget` from `Widget | null` any more. Turn `strictNullChecks` back on and both fail with `TS2322`. This is also why some of the other flags cannot even be asked for without it: `strictPropertyInitialization` only means something once `undefined` is distinguishable from an initialised field, and asking for it while `strictNullChecks` is off is refused outright:

```text
error TS5052: Option 'strictPropertyInitialization' cannot be specified without specifying option 'strictNullChecks'.
```

Lesson 16 has the full dependency graph. The fact to keep here is smaller: of the seven, `strictNullChecks` is not a check bolted onto an unchanged type system, it is the difference between `null` and `undefined` existing in that type system at all.

### Two you have already met

`strictFunctionTypes` is the flag behind lesson 13's contravariant parameter check. The `H`/`h` example above is the same shape lesson 13 used to show that a function type checks its parameters in the stricter direction: a caller who trusts `H`'s promise may pass a `number`, `h` cannot handle one, so the assignment is rejected. That rejection was never a property of function types in general; it is one flag, and turning it off makes the same assignment compile with no complaint.

`noImplicitThis` is the flag that catches lesson 4's extracted-method bug at compile time, in the one shape lesson 4 admitted it could: a plain function that reads `this` and is called with nothing to the left of the parentheses reports `TS2683`, because `this` has no declared type and no way to acquire one from how the function is called, before that `this` turns out to be `undefined` at runtime. Lesson 4's limit still holds: a method extracted and handed to a callback usually type-checks fine, since the method's own signature says nothing about needing a receiver. Practice 4 below works through the exact shape the flag does catch.

### They are already on, so the decision is whether to turn one off

Per section 5.1, every one of these seven ships true. You do not enable them; you inherit them the moment you run the compiler, the same way lesson 8's bare `tsc` already reported `TS7006` and `TS2322` before this lesson named what caused it. The only decision left is whether to ever turn one off, and the honest answer is that doing so is a project-wide loss to buy a local convenience. `useUnknownInCatchVariables: false` does not just skip the one catch block that was annoying to fix; it makes every catch variable in the entire project `any` again, at every call site written so far and every one written after that. The alternative is almost always to fix the code the check flagged, or, when a value genuinely needs to escape checking, to narrow the suppression to one line instead of the whole project. Lesson 18 covers how; a flag on by default is not an obstacle to route around, it is the thing this stage is teaching you to read.

## Practice

1. ▢ Predict the diagnostic, with its `TS` number, and name the flag responsible.

   ```ts
   function double(x) {
     return x * 2;
   }
   ```

<details markdown="1"><summary>Check</summary>

`error TS7006: Parameter 'x' implicitly has an 'any' type.` The flag is `noImplicitAny`: `x` carries no annotation and nothing in the declaration gives the compiler a type to infer.

</details>

2. ▢ Does this class compile under plain `strict`? If not, which field is the problem and which flag catches it?

   ```ts
   class Order {
     id: string;
     total: number;
     constructor(id: string) { this.id = id; }
   }
   ```

<details markdown="1"><summary>Hint</summary>

Check what the constructor actually assigns, not what the class declares.

</details>

<details markdown="1"><summary>Check</summary>

It does not compile. `total` is declared but never assigned anywhere in the constructor, so `strictPropertyInitialization` reports `error TS2564: Property 'total' has no initializer and is not definitely assigned in the constructor.` `id` is fine, since the constructor sets it directly.

</details>

3. ▢ Predict whether this compiles, and name the flag that decides it.

   ```ts
   type Sink = (x: string | number) => void;
   const numbersOnly: Sink = (x: number) => {};
   ```

<details markdown="1"><summary>Check</summary>

It fails: `error TS2322: Type '(x: number) => void' is not assignable to type 'Sink'.`, with the parameter types reported incompatible underneath. `Sink` promises callers they may pass a `string`, and `numbersOnly` only handles a `number`. The flag is `strictFunctionTypes`, the same one behind lesson 13's contravariant parameter check, mirrored here with the types swapped.

</details>

4. ▢ Predict the diagnostic and name the flag, then say which of lesson 4's four `this` rules is in play.

   ```ts
   class Timer {
     seconds = 0;
     start() {
       function tick() {
         this.seconds++;
       }
       tick();
     }
   }
   ```

<details markdown="1"><summary>Check</summary>

`error TS2683: 'this' implicitly has type 'any' because it does not have a type annotation.` The flag is `noImplicitThis`. `tick()` is a plain call with nothing to the left of the parentheses, lesson 4's default rule, so `this` would be `undefined` at runtime, and the flag reports it before that happens.

</details>

5. ▢ A teammate proposes adding `useUnknownInCatchVariables: false` to stop rewriting a handful of catch blocks, arguing it is just one flag. Give the strongest argument against, and what you would do instead.

<details markdown="1"><summary>Check</summary>

The flag is already on project-wide, so turning it off does not just fix the handful of catch blocks in mind; it makes every catch variable in the whole codebase `any` again, past and future, for as long as the setting stays. That is a permanent, global loss to buy a temporary, local convenience. The alternative is almost always to fix the flagged code directly, narrowing each caught value with `instanceof` before using it, or, where a line genuinely needs to escape the check, to suppress that one line rather than the whole project.

</details>

## Real-world reps

- [ ] Open a real `tsconfig.json` you use and check whether any of the seven flags in this lesson's catalogue is explicitly set to `false`. If one is, find the line it was added to silence and decide whether that line should be fixed instead.
- [ ] Run `tsc --all` and count how many flags carry the note that they default to `true` unless `strict` is `false`. Compare the count against the seven this lesson catalogued.
- [ ] Tomorrow: pick one compile error you or a teammate hit recently and name, from memory before checking, which of the seven flags reported it.

## Going further

- [TSConfig Reference: `strict`](https://www.typescriptlang.org/tsconfig/#strict): the option-by-option list this lesson catalogues, kept current as the set changes
- [TypeScript Handbook: Everyday Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html): the annotation vocabulary these checks are enforcing
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
