---
title: 40. Variance and Assignability
description: Which direction a type may travel, and the array that gets it wrong on purpose
type: lesson
---

# Lesson 40. Variance and Assignability

**Mission link:** Owning a codebase means reading an assignability error and naming which direction it violated, so the fix changes the design instead of silencing the compiler with an assertion.
**Primary source:** [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals)
**Prerequisites:** [Lesson 13](0013-function-types.md), [Lesson 11](0011-structural-assignability.md)

## Warm-up

1. ▢ Lesson 13 ran the identical mistake, a handler accepting only `string` assigned where `string | number` was promised, through two spellings: `type H = (x: string | number) => void; const h: H = (x: string) => {};` failed with `TS2322`, but the same parameter written as a method inside `interface Box { on(cb: (x: string) => void): void }` compiled with nothing reported. Both checks are real. What differs between them, and what should each be called?

<details markdown="1"><summary>Check</summary>

The property form checks the parameter against everything the type promises callers may send, and rejects a narrower handler; that direction of check is **contravariant**. The method form is a deliberate exemption, checked so loosely that neither narrowing nor widening the parameter is caught; that is **bivariant**. This lesson names both precisely and adds the two directions lesson 13 did not need a word for: **covariant**, for a return type, and **invariant**, for a position pinned in both directions at once.

</details>

## Know this

### The vocabulary, earned rather than introduced

Four words name the direction a type may travel between a wider type and a narrower one, wherever it occupies a position inside a larger type. **Covariant** means a position travels the same direction as its container: since `Dog` is narrower than `Animal`, a function returning `Dog` may stand in for one typed to return `Animal`, because a caller only reads what comes back and a `Dog` satisfies anyone asking for an `Animal`. A return type is covariant.

```ts
interface Animal { name: string }
interface Dog extends Animal { bark(): void }
type Supplier = () => Animal;
const giveDog: Supplier = () => ({ name: "Rex", bark() {} });
```

Verified: this compiles. **Contravariant** means a position travels the opposite direction, and lesson 13 already verified it: a function-typed parameter, written as a property, had to accept everything the wider type promised, so a handler narrowed to `string` was rejected while one widened to accept anything would have passed. A function-typed parameter, written as a property, is contravariant. **Bivariant** means the check passes in either direction with no rejection, exactly the exemption lesson 13 verified for a method's own parameter. A method parameter is bivariant. **Invariant** means neither direction is permitted: a position must match exactly, which happens whenever the same type parameter appears in both a covariant and a contravariant position on one type, so neither widening nor narrowing it can be safe in both places at once. An interface with a getter and a setter for the same `T` is the ordinary case, and the variance annotations section below names it precisely.

### Why parameters go the other way

The rule is not arbitrary; it falls out of what a function's type promises. Accepting is a promise made to every caller, so a function standing in for a wider parameter type must handle every value that type's callers may send: narrowing what it accepts breaks that promise, which is why a handler accepting only `string` cannot stand in for a type promising callers a `number` would also work. Returning is a promise read by one caller at a time, so a function may return something more specific than promised: a caller expecting an `Animal` is satisfied by a `Dog`, since everything it can do with an `Animal` a `Dog` can also do. Accept at least as much, return at least as little, is why parameters and return types travel in opposite directions, and it is the same reasoning lesson 13 applied without naming it.

### The array, and the hole the compiler leaves open on purpose

Arrays are the case every discussion of TypeScript's variance eventually reaches, because arrays are both mutable and covariant, and that combination is unsound. Watch the sequence:

```ts
const strs: string[] = ["a", "b"];
const mixed: (string | number)[] = strs;
mixed.push(42);
console.log(strs[2].toUpperCase());
```

Verified: this compiles with no diagnostic at any line. `strs` is a `string[]`, and TypeScript allows assigning it to `mixed`, typed `(string | number)[]`, treating an array's element type the same covariant way a return type travels: `string` is narrower than `string | number`, so the narrower array is accepted where the wider type is expected. The assignment makes no copy; `mixed` and `strs` name the same array, and the wider name licenses `mixed.push(42)`, adding a value `strs`'s own type never promised. The last line still reads through `strs`, still typed `string[]`, and calls `.toUpperCase()` on index 2, because nothing told the compiler that a push through the other name changed what is sitting there. Running it, rather than merely checking it, proves the hole is real: `TypeError: strs[2].toUpperCase is not a function`, since the value at that index is the number `42`, not a string.

Arrays are covariant in their element type, and that covariance is what let a `string[]` alias itself as something wider and then be mutated through the wider name. This is unsound, and deliberate: lesson 11 already told you soundness was traded away. TypeScript's design goals state a non-goal, to "apply a sound or 'provably correct' type system," choosing instead "a balance between correctness and productivity." Array covariance is that trade in its most quoted form, kept because forbidding it would reject ordinary code that passes a `string[]` somewhere a `(string | number)[]` is only ever read, which is safe, and the checker has no cheap way to separate that case from this one, which is not. The word covariant lets you say precisely what happened, rather than remembering only that arrays are "a bit dangerous."

### Variance annotations, `in` and `out`

TypeScript accepts an annotation on a generic type parameter: `in` for a position meant to be contravariant, `out` for one meant to be covariant, both together for one meant to be invariant.

```ts
interface Box<in out T> {
  get(): T;
  set(v: T): void;
}
```

Verified: this compiles and behaves exactly as the interface would without the annotation, since `Box` already had a getter and a setter for `T` and was already invariant by construction. The annotation is not decoration, though: the compiler checks it against the variance it actually computes, and reports a mismatch. Declaring `out T` on an interface that also takes a `T` in is a wrong claim, and it is caught at the declaration, with no assignment anywhere needed to provoke it:

```ts
interface BadProducer<out T> {
  get(): T;
  set: (v: T) => void;
}
```

```text
error TS2636: Type 'BadProducer<sub-T>' is not assignable to type 'BadProducer<super-T>' as implied by variance annotation.
  Types of property 'set' are incompatible.
    Type '(v: sub-T) => void' is not assignable to type '(v: super-T) => void'.
      Types of parameters 'v' and 'v' are incompatible.
        Type 'super-T' is not assignable to type 'sub-T'.
```

**And write that same setter as a method and the whole thing goes quiet.** Verified: with `set(v: T): void` instead of `set: (v: T) => void`, the identical `out T` claim compiles with no diagnostic at all. This is lesson 13's exemption resurfacing one stage later: a method's parameter is checked bivariantly, so it never contradicts the `out` claim, while the same parameter written as a function-typed property is checked contravariantly and does. If you reproduce this example with method syntax and see nothing, the annotation is not being ignored; the position you put `T` in stopped being contravariant.


Treat these annotations as a hint to the checker and documentation on the declaration, not a capability you would otherwise lack: without one, TypeScript works out the correct variance itself from how `T` is used, and gets it right for ordinary interfaces. They matter mainly on large generic interfaces, where working variance out from usage is expensive to recompute on every check, and stating it up front lets the checker skip that work. Treat that last claim as the compiler team's rather than as something demonstrated here: it is the reason the annotations exist, per the performance notes linked below, and nothing in this stage measures the saving, so do not repeat it as a measured result. Do not add `in` or `out` to your own generics just because you have learned the words: they earn a place on a handful of library-scale interfaces, and on the interface you wrote yesterday the compiler already gets the variance right unasked, so an annotation there only documents what nobody doubted.

### The caller who benefits

Put the contravariant direction to work reading an error rather than avoiding one. A registration function expects a handler that can cope with any `Animal`, and a caller supplies one narrowed to `Dog`:

```ts
type Handler = (a: Dog) => void;
declare function registerAnimalHandler(h: (a: Animal) => void): void;
const handleDog: Handler = (a) => { a.bark(); };
registerAnimalHandler(handleDog);
```

```text
error TS2345: Argument of type 'Handler' is not assignable to parameter of type '(a: Animal) => void'.
  Types of parameters 'a' and 'a' are incompatible.
    Property 'bark' is missing in type 'Animal' but required in type 'Dog'.
```

Read this with the vocabulary above and the cause is immediate: `registerAnimalHandler` needs a handler accepting every `Animal`, `handleDog` only accepts a `Dog`, and this is the contravariant parameter check rejecting the direction it exists to reject. A caller without the word reaches for `handleDog as (a: Animal) => void` and moves on, lesson 18's silenced check reappearing: the assertion compiles, and the first non-dog animal reaching `a.bark()` at run time is the bug the error warned about. A caller who has the word instead asks whether the registry genuinely only sees dogs, and if so fixes the design by typing it over `Dog` rather than widening a promise `handleDog` cannot keep; naming which direction failed turns "make the red line go away" into "change the right thing."

### Where to stop

Reasoning about variance earns its keep at one moment: when an assignability error needs explaining, and naming covariant, contravariant, bivariant or invariant tells you which direction was violated and why. It stops earning its keep the moment you design a type whose whole purpose is to enforce a variance relationship of your own, a wrapper generic built to be "properly" covariant or to ban a direction a plain interface would already get right. That is the trap in handing you words powerful enough to feel like a tool: the compiler already computes variance correctly for almost everything you write, an annotation only documents what it computed, and a caller gains nothing from a variance-enforcing wrapper that the plain interface underneath it did not already give them. Designing a signature so a caller never has to think about direction at all is lesson 41's job.

## Practice

1. ▢ Predict whether this compiles, and name the direction involved.

   ```ts
   interface Shape { area(): number }
   interface Circle extends Shape { radius: number }
   type MakeShape = () => Shape;
   const makeCircle: MakeShape = () => ({ area: () => 1, radius: 1 });
   ```

<details markdown="1"><summary>Check</summary>

Compiles. `MakeShape` promises callers a `Shape` back, and a `Circle` is a `Shape` plus more; a caller reading only what it asked for is satisfied. This is the return-type direction, covariant.

</details>

2. ▢ Predict the diagnostic, with its `TS` number, and name the direction violated.

   ```ts
   interface Shape { area(): number }
   interface Circle extends Shape { radius: number }
   type Sink = (x: Circle) => void;
   declare function needsWideSink(s: (x: Shape) => void): void;
   const onlyCircle: Sink = (c) => {};
   needsWideSink(onlyCircle);
   ```

<details markdown="1"><summary>Hint</summary>

Ask what `needsWideSink` promises callers it can handle, and whether `onlyCircle` can handle everything that promise covers.

</details>

<details markdown="1"><summary>Check</summary>

`error TS2345: Argument of type 'Sink' is not assignable to parameter of type '(x: Shape) => void'.` with the parameter types reported incompatible underneath. `needsWideSink` wants a function accepting any `Shape`; `onlyCircle` only accepts a `Circle`. That is the parameter direction, contravariant, the same shape of mistake lesson 13's `H`/`h` example made.

</details>

3. ▢ The array example used a mutable target type. Predict this variant, which uses a `readonly` one instead.

   ```ts
   const strs: string[] = ["a", "b"];
   const safe: readonly (string | number)[] = strs;
   safe.push(42);
   ```

<details markdown="1"><summary>Check</summary>

`error TS2339: Property 'push' does not exist on type 'readonly (string | number)[]'.` The assignment to `safe` is still covariant and still permitted, but `readonly` removes every mutating method from the type, so there is no longer a way through the wider name to write a value the narrower name's own type disallows. This is the safe half of array covariance: read-only widening cannot reopen the hole, because nothing can push through it.

</details>

4. ▢ Predict whether this compiles, and if not, which part of the diagnostic names the mistake.

   ```ts
   interface WrongConsumer<in T> {
     get(): T;
   }
   declare const w: WrongConsumer<string | number>;
   const w2: WrongConsumer<string> = w;
   ```

<details markdown="1"><summary>Check</summary>

It fails: `error TS2636: Type 'WrongConsumer<super-T>' is not assignable to type 'WrongConsumer<sub-T>' as implied by variance annotation.` with `get()`'s return types reported incompatible underneath. `get` only returns `T`, a covariant position, but the interface claimed `in`, contravariant. The annotation is a claim the checker verifies against real usage, and here the claim was wrong.

</details>

5. ▢ A teammate proposes a generic `SafeCallback<T>` wrapper whose entire purpose is to reject, at the type level, any callback that is not exactly invariant in `T`, "so nobody has to reason about variance again." What should a reviewer ask before approving it?

<details markdown="1"><summary>Check</summary>

Whether any real caller is harmed by ordinary variance, since the compiler already computes the correct variance for a plain callback type unasked, and a wrapper enforcing a stricter relationship than callers need only adds a type nobody asked for on top of one that already worked. This is the over-application the lesson warns about: variance is worth reasoning about to explain an existing error, not worth building new machinery to police.

</details>

## Real-world reps

- [ ] Find an assignability error that mentions incompatible parameter or return types, and name which direction, covariant, contravariant or bivariant, the diagnostic is actually reporting before deciding how to fix it.
- [ ] Search a codebase for a callback member declared as a method rather than a property, the way lesson 13 practiced, and check whether tightening it to the property form would now catch a narrower callback variance alone predicts is unsafe.
- [ ] Tomorrow: find one place where a narrower array is assigned to a wider one and then mutated through the wider name, and decide whether marking the wider reference `readonly` would close that hole without changing what the code needs to do.

## Going further

- [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals): the non-goals list, including soundness traded for productivity, which is what array covariance spends
- [TSConfig Reference: `strictFunctionTypes`](https://www.typescriptlang.org/tsconfig/#strictFunctionTypes): the flag behind the contravariant parameter check this lesson names
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
