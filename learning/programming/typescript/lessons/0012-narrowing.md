---
title: 12. Narrowing
description: Control flow tells the compiler what a union has become, and exactly two things take it back
type: lesson
---

# Lesson 12. Narrowing

**Mission link:** Owning a codebase means reading a union type and knowing, at the exact line you are standing on, what the compiler currently believes it could be, and knowing precisely which two things make that belief disappear.
**Primary source:** [Narrowing, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
**Prerequisites:** [Lesson 10](0010-unions-and-literal-types.md), [Lesson 5](0005-scope-and-closures.md)

## Warm-up

1. ▢ Lesson 10 gave you a union such as `string | number`. Predict what happens when you call `.toUpperCase()` on a value of that type with no check first.

<details markdown="1"><summary>Check</summary>

`error TS2339: Property 'toUpperCase' does not exist on type 'string | number'.` (with a second line naming `number` as the member that fails). The compiler will not call a method that not every member of the union has, and a union you cannot narrow is a union you can barely use.

</details>

## Know this

### Control flow decides the type

Narrowing is not something you do to a variable once; it is a property of a position in the code. The checker walks the same branches your code takes at runtime and, at each point, works out what a value's type must still be, given the branches taken to reach it. The same variable can be `string | number` on one line and `string` on the next, with nothing written to the variable itself, only a branch taken around it.

### The narrowing operators

Each of these narrows for the rest of the block or function it guards.

`typeof`:

```ts
function f(x: string | number) {
  if (typeof x === "string") {
    x.toUpperCase(); // x is string here
  }
}
```

`instanceof`:

```ts
function f(x: Date | string) {
  if (x instanceof Date) {
    x.getFullYear(); // x is Date here
  }
}
```

`in`, checking for a property rather than a runtime tag:

```ts
type A = { a: number };
type B = { b: string };
function f(x: A | B) {
  if ("a" in x) {
    x.a; // x is A here
  }
}
```

Equality against a literal:

```ts
function f(x: "a" | "b" | number) {
  if (x === "a") {
    // x is the literal type "a" here
  }
}
```

Truthiness:

```ts
function f(x: string | null) {
  if (x) {
    x.toUpperCase(); // x is string here
  }
}
```

An early `return` narrows everything after it, for the rest of the function:

```ts
function f(x: string | null) {
  if (x === null) return;
  x.toUpperCase(); // x is string from here to the end of f
}
```

You may meet code that writes its own function to do this check and calls it a type guard. That is a separate, later idea, one where the compiler trusts a claim about the runtime rather than checking one itself, and it waits until you can weigh that trust properly.

### Truthiness is a trap

Lesson 1 listed the values a condition treats as false: `false`, `0`, `-0`, `0n`, `""`, `null`, `undefined`, `NaN`. Narrowing on truthiness uses exactly that list, which is fine when the only thing you are excluding is `null` or `undefined`, and wrong the moment `0` or `""` is a value you needed to keep. Run this:

```ts
function describe(s: string | null): string {
  if (s) {
    return `got: "${s}"`;
  }
  return "nothing";
}
console.log(describe(""));
console.log(describe(null));
```

Both calls print `nothing`. The type narrows correctly, `s` really is `string` inside the branch, but `""` is a legitimate string that truthiness discards along with `null`. When zero or the empty string is a value the caller may legitimately send, test what you actually mean, such as `s !== null`, and reserve truthiness for cases where every falsy value should genuinely be treated alike.

### When narrowing is lost

This is the part worth being exact about, because the common story about it is wrong in two places, verified by running each case rather than assumed.

**A narrowed local survives a closure, provided it is never reassigned.** The question that decides it is whether the variable is ever reassigned anywhere in the function, not whether it is declared `let` or `const`.

```ts
function f(x: string | null) {
  if (x === null) return;
  const closure = () => {
    const s: string = x; // compiles: x is never reassigned
  };
  closure();
}
```

Reassign it anywhere afterwards, even after the closure is written, and both a direct use and the closure use lose the narrowing, with the same diagnostic:

```ts
function f(x: string | null, y: string | null) {
  if (x === null) return;
  const closure = () => {
    const s: string = x;
    // error TS2322: Type 'string | null' is not assignable to type 'string'.
  };
  x = y;
  const s2: string = x;
  // error TS2322: same diagnostic, direct use
  closure();
}
```

The compiler cannot know when `closure` will run relative to the reassignment, so a later reassignment anywhere in the function poisons every use, whether direct or deferred.

**A narrowed property survives an arbitrary function call, which is not what most people expect.** The usual belief is that calling any function invalidates narrowing on a property, on the theory that the call might mutate it. Checked against the compiler, that belief is false:

```ts
function unrelated() {}

class Box {
  value: string | null = null;
  f() {
    if (this.value === null) return;
    unrelated();
    const s: string = this.value; // compiles: the call did not lose it
  }
}
```

What does lose it is a closure, for the same reason a closure loses a reassigned local: the closure may run later, after `this.value` has changed.

```ts
class Box {
  value: string | null = null;
  f() {
    if (this.value === null) return;
    const closure = () => {
      const s: string = this.value;
      // error TS2322: Type 'string | null' is not assignable to type 'string'.
    };
    closure();
  }
}
```

Two different questions govern two different kinds of binding: for a local, whether it is ever reassigned; for a property, whether the use is deferred into a closure, not whether anything was called along the way. The fix that follows from the second rule, rather than from superstition about calls, is to copy the narrowed property into a local before the closure captures it:

```ts
class Box {
  value: string | null = null;
  f() {
    if (this.value === null) return;
    const value = this.value; // now a local, and never reassigned
    const closure = () => {
      const s: string = value; // compiles
    };
    closure();
  }
}
```

`value` is a fresh local that is never reassigned, so the first rule applies to it and the closure keeps the narrowing.

## Practice

1. ▢ Predict the output of both calls.

   ```ts
   function count(n: number | null): string {
     if (n) {
       return `count: ${n}`;
     }
     return "no count";
   }
   console.log(count(0));
   console.log(count(null));
   ```

<details markdown="1"><summary>Check</summary>

Both print `no count`. `0` is a legitimate count, but truthiness treats it like `null`. The narrowing itself is correct, `n` is `number` inside the branch; the test was simply the wrong one for a value where zero matters.

</details>

2. ▢ Predict the diagnostic, with its `TS` number.

   ```ts
   function f(x: string | null, y: string | null) {
     if (x === null) return;
     x = y;
     const s: string = x;
   }
   ```

<details markdown="1"><summary>Hint</summary>

Ask whether `x` is reassigned anywhere after the narrowing check, not whether it was declared with `let`.

</details>

<details markdown="1"><summary>Check</summary>

`error TS2322: Type 'string | null' is not assignable to type 'string'.` The reassignment wipes out the narrowing the `return` established, because `x` can now hold whatever `y` held.

</details>

3. ▢ Compare these two functions. One compiles, one does not. Which, and why?

   ```ts
   function a(x: string | null) {
     if (x === null) return;
     const c = () => {
       const s: string = x;
     };
     c();
   }

   function b(x: string | null, y: string | null) {
     if (x === null) return;
     const c = () => {
       const s: string = x;
     };
     x = y;
     c();
   }
   ```

<details markdown="1"><summary>Check</summary>

`a` compiles. `b` fails with `error TS2322: Type 'string | null' is not assignable to type 'string'.` on the line inside `c`, because `x` is reassigned later, even though that happens after `c` is defined. What decides it is never the runtime order, only whether a reassignment exists anywhere in the function.

</details>

4. ▢ Does this compile?

   ```ts
   function unrelated() {}
   class Box {
     value: string | null = null;
     f() {
       if (this.value === null) return;
       unrelated();
       this.value.toUpperCase();
     }
   }
   ```

<details markdown="1"><summary>Hint</summary>

This is the case the folklore gets backwards. Ask what actually invalidates a narrowed property, not what people usually assume does.

</details>

<details markdown="1"><summary>Check</summary>

Yes, it compiles. Calling `unrelated()` between the check and the use does not invalidate the narrowing on `this.value`, contrary to the common belief that any call in between does.

</details>

5. ▢ This fails. Predict the diagnostic, then fix it by copying `this.value` into a local before the closure.

   ```ts
   class Box {
     value: string | null = null;
     f() {
       if (this.value === null) return;
       const c = () => {
         const s: string = this.value;
       };
       c();
     }
   }
   ```

<details markdown="1"><summary>Check</summary>

`error TS2322: Type 'string | null' is not assignable to type 'string'.` on the line inside `c`. The closure may run later, after `this.value` has changed, so the narrowing does not carry into it. Fix: `const value = this.value;` before defining `c`, then use `value` inside it. That local is never reassigned, so the closure keeps its narrowing.

</details>

## Real-world reps

- [ ] Find a spot in your own code, or write one, where a property is narrowed with a check and then used inside a callback, an event handler, or a `.then()`. Predict whether it compiles before you check.
- [ ] Take a function with a narrowed local and add a reassignment somewhere after the check, anywhere in the function, even nowhere near the use. Watch the diagnostic appear at the use, not at the reassignment.
- [ ] Tomorrow: search a real project for `if (x)` where `x` is typed to include `0`, `""`, or a union with one of those as a member. Decide whether truthiness was the right test or an accidental trap.

## Going further

- [TypeScript Handbook: Everyday Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html), for the union and literal types this lesson narrows
- [Effective TypeScript](https://effectivetypescript.com/), for more on distinguishing the type-level story from the runtime one
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
