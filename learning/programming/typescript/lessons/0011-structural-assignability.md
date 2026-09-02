---
title: 11. Structural Assignability
description: Shape decides what goes where, except for the one check that only fires on a fresh object literal
type: lesson
---

# Lesson 11. Structural Assignability

**Mission link:** Every value crossing a typed boundary gets one verdict from the compiler, assignable or not, and knowing the rule behind that verdict is what lets you predict a diagnostic before running `tsc`.
**Primary source:** [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals)
**Prerequisites:** [Lesson 8](0008-the-types-you-write.md), [Lesson 3](0003-prototypes-and-classes.md)

## Warm-up

1. ▢ Lesson 2 established that a type is a claim checked at compile time and gone by run time. What does the compiler check a value against when it meets a written type?

<details markdown="1"><summary>Check</summary>

The value's shape: which properties it has and their types. Not a name, and not where the value came from.

</details>

2. ▢ Lesson 3 showed that a plain object with the right members satisfies a class type even though `instanceof` says no. Which question does the type checker ask, and which does `instanceof` ask?

<details markdown="1"><summary>Check</summary>

The type checker asks whether the shape matches. `instanceof` asks whether `SomeClass.prototype` is in the object's prototype chain. They can disagree, since one is about members and the other about history.

</details>

## Know this

### A type is a shape, and assignability compares shapes

Assigning a value `v` to a target typed `T` asks one question: does `v`'s shape have at least the members `T` requires, with compatible types? Nothing else matters, so two types declared in unrelated places are interchangeable once their members line up:

```ts
interface Named { name: string }
type Named2 = { name: string };

declare const n1: Named;
const n2: Named2 = n1;   // compiles, same shape
```

That is lesson 3's property bag showing up in the type system: an object is properties on a chain, nothing more, and the compiler checks only what it carries. It is why a class instance satisfies an interface it never declared, `implements` and all, as practice 1 below asks you to confirm. This is **structural typing**, and it is deliberate: goal 9 of the design document is "use a consistent, fully erasable, structural type system."

### Extra properties are fine

Once assignability is a shape comparison, one consequence follows: a value with more than the target needs still satisfies it, because "at least" already covers "more than". A function that wants `{ id: string }` accepts any object that has an `id`, however much else it carries. That is what makes structural typing usable day to day, and it is also what makes the next fact surprising.

### The exception, and it is the one worth remembering

```ts
type P = { a: number };
const p: P = { a: 1, b: 2 };
```

```text
error TS2353: Object literal may only specify known properties, and 'b' does not exist in type 'P'.
```

Rejected, even though `{ a: 1, b: 2 }` has everything `P` needs and one thing extra, exactly the shape the previous section said was fine. Route the identical value through a variable first and it compiles:

```ts
type P = { a: number };
const src = { a: 1, b: 2 };
const p: P = src;   // compiles
```

The shape did not change between the two. What changed is that the rejected one is a **fresh object literal** assigned directly to a typed target, which triggers a separate check, excess property checking, that is not part of ordinary structural assignability.

The reasoning: a fresh literal is the one place the compiler can be fairly sure what you meant, since you wrote `{ a: 1, b: 2 }` right next to a type that says `{ a: number }`. A `b` there is almost certainly a typo, or a misremembered option name, not deliberate extra data being carried through, so the check catches it where catching it costs nothing else. It cannot be the general rule, since the general rule must keep working for the case above, where a value legitimately carries more than a function needs. The same check fires anywhere a fresh literal meets a typed target, including a function call passing one directly, which practice 4 asks you to predict.

### The practical consequence

Excess property checking is a courtesy, not a guarantee, and easy to switch off by accident. Routing a literal through a variable first makes the error disappear without making the code more correct, since it only removes the one check that was looking. A colleague who "fixes" a `TS2353` this way has silenced a warning that was quite possibly a real typo, and that move deserves a second look in review rather than a shrug.

### Soundness is a non-goal

The design document is explicit that TypeScript does not aim to be sound. Non-goal 3 reads, "apply a sound or 'provably correct' type system. Instead, strike a balance between correctness and productivity." Excess property checking is that trade in miniature: generous by default, strict only where strictness is cheap. Other gaps this stage covers, a mutable value accepted where `readonly` was promised, a tuple's length enforced on read but not on `push`, are the same trade elsewhere. Stage 5 is where trusting a type at a boundary gives way to checking the value itself.

One related tool earns a pointer, not a lesson, here: `satisfies` checks a literal against a type without widening the variable's declared type the way an annotation would. Stage 4 covers it properly.

## Practice

1. ▢ Predict whether this compiles, and if it does, explain why `Point` is allowed even though it never mentions `Coord`.

   ```ts
   class Point { constructor(public x: number, public y: number) {} }
   interface Coord { x: number; y: number }
   const c: Coord = new Point(1, 2);
   ```

<details markdown="1"><summary>Check</summary>

Compiles. Assignability only compares shapes, and `Point` instances have an `x` and a `y`, everything `Coord` requires; no `implements` clause is needed.

</details>

2. ▢ Predict the exact diagnostic, with its `TS` number.

   ```ts
   type P = { a: number };
   const p: P = { a: 1, b: 2 };
   ```

<details markdown="1"><summary>Check</summary>

`error TS2353: Object literal may only specify known properties, and 'b' does not exist in type 'P'.`

`b` is not a member of `P`, and this is a fresh object literal assigned directly to a typed target, so excess property checking runs.

</details>

3. ▢ Now predict this one, and say precisely what is different from item 2.

   ```ts
   type P = { a: number };
   const src = { a: 1, b: 2 };
   const p: P = src;
   ```

<details markdown="1"><summary>Hint</summary>

The value is identical. Ask what moved between the literal and the assignment.

</details>

<details markdown="1"><summary>Check</summary>

Compiles. `src` is a variable, not a fresh literal, so ordinary structural assignability applies instead of excess property checking: it has at least what `P` needs, and the extra `b` is allowed.

</details>

4. ▢ Predict this call.

   ```ts
   type P = { a: number };
   function take(p: P) {}
   take({ a: 1, b: 2 });
   ```

<details markdown="1"><summary>Check</summary>

`error TS2353`, same as item 2. A call argument is a typed target exactly like a `const` annotation, so the same check fires.

</details>

5. ▢ A reviewer sees the error from item 2 in a pull request. The author "fixes" it by assigning the literal to a variable first, the way item 3 does, then using the variable. What, precisely, did the author fix, and what should the reviewer ask?

<details markdown="1"><summary>Check</summary>

Nothing about correctness was fixed. `b` is still there, and if it was a misspelled property, that typo is now invisible, since moving the literal into a variable switches off excess property checking without changing the shape. The reviewer should ask whether `b` was intentional and, if not, insist on removing or renaming it rather than routing around the check.

</details>

## Real-world reps

- [ ] Pass an options literal with a misspelled key straight into a function that expects a narrower type. Watch `TS2353` catch it, then assign the literal to a variable first and watch the error vanish.
- [ ] Find a class in code you know that satisfies an interface without ever writing `implements`. Confirm the compiler accepts it, then write a plain object with the same members and pass it where the class was expected.
- [ ] Tomorrow: search a codebase you work in for a literal moved into a variable right after a type error. Read the diff and decide whether the move fixed a mistake or hid one.

## Going further

- [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals): the goals and non-goals list, including structural typing and soundness as a non-goal
- [Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html): the handbook's treatment of structural shapes and excess property checks
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
