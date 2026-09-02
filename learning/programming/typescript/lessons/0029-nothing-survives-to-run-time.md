---
title: 29. Nothing Survives to Run Time
description: Every type is a claim about a program that no longer exists when the claim would matter
type: lesson
---

# Lesson 29. Nothing Survives to Run Time

**Mission link:** Owning a codebase means knowing, for any value in front of you while the program runs, which of the last twenty-eight lessons' guarantees are still true, and this lesson is where the honest answer gets said.
**Primary source:** [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals)
**Prerequisites:** [Lesson 28](0028-interface-or-type.md), [Lesson 2](0002-objects-are-references.md)

## Warm-up

1. ▢ Lesson 2 said `readonly` is a compile-time claim that disappears at run time, lesson 18 said an assertion changes what the compiler believes rather than what is true, and lesson 25 said a brand's phantom property is missing from every value that has ever existed while a program ran. State, in one sentence, what all three have in common.

<details markdown="1"><summary>Check</summary>

Each one is checked exactly once, against the program as it is compiled, by a compiler that then goes away, so none of the three checks happens again, or happens at all, once the program is actually running.

</details>

## Know this

### What erases and what remains

Rather than take this on faith, compile something that uses most of what the last four stages taught and read what comes out the other side.

```ts
interface Point { x: number; y: number }
type UserId = string & { readonly __brand: "UserId" };

function makeUserId(raw: string): UserId {
  return raw as UserId;
}
function identity<T>(value: T): T {
  return value;
}
class Box {
  constructor(public value: number) {}
}

const p: Point = { x: 1, y: 2 };
const id = makeUserId("u-1");
const n = identity<number>(42);
const b = new Box(3);
const asserted = n as unknown as string;
const nonNull = p.x!;
const checked = { x: 1, y: 2 } satisfies Point;
```

Compiled with `tsc --outDir out`, this is the file `tsc` actually writes, byte for byte:

```js
function makeUserId(raw) {
    return raw;
}
function identity(value) {
    return value;
}
class Box {
    value;
    constructor(value) {
        this.value = value;
    }
}
const p = { x: 1, y: 2 };
const id = makeUserId("u-1");
const n = identity(42);
const b = new Box(3);
const asserted = n;
const nonNull = p.x;
const checked = { x: 1, y: 2 };
```

`interface Point` and `type UserId` leave no trace, not even a comment. The annotation `: Point`, the intersection and phantom `__brand`, the generic argument `<number>`, `as unknown as string`, the trailing `!`, and `satisfies Point` are all gone the same way, collapsing to the bare expression underneath. What survives is what was also a value: two functions, a class, three object literals, four calls. Imports obey the same rule: in a two-file project, `import type { Config } from "./types.js"` compiles away entirely, while `import { defaultConfig } from "./types.js"` remains, since `defaultConfig` is called on the next line, and a value used is emitted.

### The consequence, stated plainly

A type is a claim, checked against a program that is then thrown away. The moment a value arrives, from a network response, a file, or a caller who never ran a type checker at all, nothing written across the last twenty-eight lessons is present to object. The interfaces are gone, the brands are gone, the generic constraints are gone, and the assertions never did anything to begin with, since lesson 18 already showed an assertion changing belief rather than fact, and belief is exactly what does not survive compilation. Whatever shape a type declared, the running program remembers only the value in front of it, not the declaration. This is the premise the rest of stage 5 stands on: illegal states made unrepresentable, a branded identifier, a union narrowed to one arm, each an argument made to a compiler that will not be in the room when the claim is actually tested.

### The design goal behind it

This is not an accident of implementation, it is a stated goal. The design document lists, among its goals, "use a consistent, fully erasable, structural type system", and among its non-goals, "apply a sound or provably correct type system. Instead, strike a balance between correctness and productivity." Lesson 11 already used that second line for structural assignability; here the two lines meet, since the document that refuses to guarantee every accepted program is safe also commits, in the same breath, to a type system that leaves nothing behind once the program runs. They are not independent: a language promising to preserve JavaScript's runtime behaviour cannot also add run-time type information without breaking that promise. Erasure is the trade that keeps it, a checker that costs nothing once the program executes, for one that cannot stand behind its own verdicts once it has run. Calling this a flaw mistakes a chosen trade for an oversight.

### `declare` as a pure claim

One more shape of claim is worth naming: `declare const mystery: string;` tells the compiler that something called `mystery` exists somewhere, without writing anything that produces it. It compiles cleanly, and so does a line that uses it as if the promise were kept.

```ts
declare const mystery: string;
console.log(mystery.toUpperCase());
```

Run it, and nothing is there to catch the toUpperCase call, because nothing ever created `mystery` in the first place.

```text
ReferenceError: mystery is not defined
```

`declare` is a claim the compiler cannot audit, in the same family as an assertion: it changes what the checker believes without checking whether the belief is true. This lesson only names the category; lesson 34 covers declaration files, where this claim does most of its real work.

### Where erasure bites in ordinary code

Three small demonstrations, each one a habit that meets the fact just established. `typeof` cannot recover a type, because there was never a type at run time to recover, and a brand's phantom property is genuinely absent, not merely inaccessible.

```ts
type Meters = number;
const distance: Meters = 5;
console.log(typeof distance);

const id = makeUserId("u-123");
console.log(Object.hasOwn(id as unknown as object, "__brand"));
console.log(JSON.stringify({ id }));
```

```text
number
false
{"id":"u-123"}
```

`Meters` never existed once compiled, so `typeof` reports only JavaScript's own primitive tag, the same tag it would have reported with no alias written at all. No `__brand` was ever set on any string a program has produced, so the direct property check finds nothing, and serialising `id` shows exactly what it was underneath: a plain string, with the brand missing.

A `catch` variable can hold anything, because `throw` accepts anything.

```ts
for (const thrown of [new Error("boom"), "plain string", 42, { code: 7 }]) {
  try {
    throwSomething(thrown);
  } catch (e) {
    console.log(typeof e, e instanceof Error);
  }
}
```

```text
object true
string false
number false
object false
```

Lesson 17 already told you the caught variable's type is `unknown`; this is why that is accuracy rather than caution. Nothing in JavaScript restricts what an expression may throw, so a `catch` block that assumes an `Error` is one unusual throw away from reading a property off a number.

### The one thing that does not erase

Everything above erases because it was only ever a claim. A class is the one construct that is not, because it is a value in the same statement that makes it a type: its `constructor` has to exist at run time for the class to work as JavaScript at all, so `instanceof`, alone among everything tested above, keeps working.

```ts
class Box {
  constructor(public value: number) {}
}
const b: unknown = new Box(9);
console.log(b instanceof Box);
```

```text
true
```

Do not read this as a reason to prefer classes; it is the exception that proves the rule, not a workaround for it. `instanceof` tests one narrow fact, that `Box.prototype` sits in `b`'s prototype chain, and it can be true while a `UserId` field brought in through an unchecked `as` is wrong underneath. Surviving as a real object tells you it was built by that constructor; it says nothing about whether the constructor's parameters were what their types claimed, since those types erased along with everyone else's.

### The stage's job

If nothing survives, then no type stands guard on its own once the program runs, which means something else has to do the standing: an explicit check, placed where a value that was never checked meets code that assumes it was. The rest of stage 5 is about where those places are and what a real check looks like. This lesson's job was narrower and comes first: making sure you no longer expect the type system to be present at the one moment it would matter most.

## Practice

1. ▢ Predict the compiled JavaScript, then predict what running it prints.

   ```ts
   interface Shape {
     radius: number;
   }
   function area<T extends Shape>(s: T): number {
     return Math.PI * s.radius ** 2;
   }
   const s = { radius: 2 } satisfies Shape;
   console.log(area<Shape>(s)!);
   ```

<details markdown="1"><summary>Check</summary>

`interface Shape` produces no output, the constraint `extends Shape` and the type argument `<Shape>` both disappear, and `satisfies Shape` and the trailing `!` both collapse to the bare expression, leaving `function area(s) { return Math.PI * s.radius ** 2; }` called as `area(s)`. Running it prints `12.566370614359172`. Nothing about the type-level machinery changed the arithmetic; it only changed what the compiler was willing to accept on the way there.

</details>

2. ▢ Predict the output.

   ```ts
   type Meters = number;
   const distance: Meters = 5;
   console.log(typeof distance);
   ```

<details markdown="1"><summary>Check</summary>

`number`. `Meters` is an alias, erased entirely by the time this runs, so `typeof` reports the one fact it has ever been able to report about a number: JavaScript's own primitive tag.

</details>

3. ▢ Predict both lines of output.

   ```ts
   type UserId = string & { readonly __brand: "UserId" };
   function makeUserId(raw: string): UserId {
     return raw as UserId;
   }
   const id = makeUserId("u-123");
   console.log(Object.hasOwn(id as unknown as object, "__brand"));
   console.log(JSON.stringify({ id }));
   ```

<details markdown="1"><summary>Check</summary>

`false`, then `{"id":"u-123"}`. `as UserId` only changed what the compiler believed about `raw`; it never wrote a `__brand` property onto the string, so the direct check finds nothing, and the serialised value shows a plain string with no trace of the type that once wrapped it.

</details>

4. ▢ Predict whether this compiles, and if it does, predict exactly what happens when it runs.

   ```ts
   declare const mystery: string;
   console.log(mystery.toUpperCase());
   ```

<details markdown="1"><summary>Check</summary>

Compiles with no diagnostic: `declare` only tells the checker that a `string` called `mystery` exists somewhere, and `.toUpperCase()` is a fine thing to call on a `string`. Running it throws `ReferenceError: mystery is not defined`, because `declare` never produced a binding, it only asserted one, and nothing else in the file created `mystery` for real.

</details>

5. ▢ A reviewer, looking at this class, writes: "the constructor parameter is typed `UserId`, and `instanceof Order` passes in our tests, so by the time we're inside a method this instance is already known-good." What is right about that claim and what is wrong?

   ```ts
   class Order {
     constructor(public id: UserId, public total: number) {}
   }
   const raw: unknown = "u-1";
   const o = new Order(raw as UserId, 10);
   console.log(o instanceof Order);
   ```

<details markdown="1"><summary>Check</summary>

Right: `o instanceof Order` genuinely prints `true`, because `Order` is a class, a value as well as a type, so the check that `Order.prototype` sits in `o`'s prototype chain survives compilation and means what it says. Wrong: that check says nothing about `id`. `raw as UserId` is an unchecked assertion, and the `UserId` brand it claims erased on compilation like every other type here, so `instanceof` confirms the object came from this constructor and is silent about whether `id` was ever validated. Reading `instanceof` as proof of the parameter's shape is the exact mistake this lesson warns against: the exception that survives is narrower than it looks.

</details>

## Real-world reps

- [ ] Compile a file you already have with `--outDir` and open the emitted file next to the source; find one construct that vanished and one that did not, and say in a sentence why each went the way it did.
- [ ] Find a `catch` block in code you can see and check whether it assumes the caught value is an `Error` before confirming it with `instanceof`; if it does, it is one non-`Error` throw away from lesson 17's `unknown` mattering.
- [ ] Tomorrow: pick one value in a codebase you own that arrives from outside your own function calls and write down, honestly, what has actually been checked about it by the time your code first reads a property off it.

## Going further

- [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals): the primary source, including the full numbered lists of goals and non-goals this lesson quotes from
- [Declaration Files, Introduction, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/declaration-files/introduction.html): the handbook's own framing of a declaration as a claim about code the compiler did not check, before lesson 34 goes further
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
