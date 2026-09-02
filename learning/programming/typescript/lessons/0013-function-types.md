---
title: 13. Function Types
description: Parameters are checked in the direction you expect, unless you wrote a method
type: lesson
---

# Lesson 13. Function Types

**Mission link:** A callback is the shape through which most of a codebase's contracts travel, and whether the compiler catches a caller's mistake in one turns out to depend on a declaration-style choice most people never notice they made.
**Primary source:** [Functions, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/2/functions.html)
**Prerequisites:** [Lesson 11](0011-structural-assignability.md), [Lesson 4](0004-this-and-the-call-site.md)

## Warm-up

1. ▢ In lesson 4, `const fn = svc.describe; fn();` threw instead of returning the name. Why?

<details markdown="1"><summary>Check</summary>

`this` is decided by the call site, not by where a function was written, and extracting `describe` threw the receiver away.

A function's *type* has nothing to say about that: two functions with identical parameters and return type can differ in whether they need a receiver, and the type system does not see it. This lesson stays with what a function type does check, parameters and return values, and one of those two checks holds a real surprise.

</details>

## Know this

### Writing a function type

A parameter gets an annotation the same way a variable does, and so does a return value, written after the closing parenthesis:

```ts
function pad(s: string, width: number = 10): string {
  return s.padStart(width);
}
```

A default value, `width: number = 10`, makes the parameter optional and gives the compiler a type even if you never wrote one. `?` does the same without a default: `greeting?: string` means callers may omit it, and inside the function its type includes `undefined`. A rest parameter collects the remaining arguments into an array: `function sum(...nums: number[]): number`. When a function type is the type of a value rather than a declaration, it is written as an arrow: `const add: (a: number, b: number) => number = (a, b) => a + b`. All of that compiles as written; it is vocabulary, not the interesting part.

### Contextual typing: the parameter you never annotated

Pass a callback to a function whose parameter type is already known, and the callback's own parameters need no annotation at all:

```ts
declare function each(xs: string[], cb: (x: string) => void): void;
each(["a"], x => {
  const n: number = x;
});
```

```text
error TS2322: Type 'string' is not assignable to type 'number'.
```

Nobody wrote a type for `x`, and the compiler still knew it was `string`, because `each`'s declared parameter told it what shape a call there would have to fill. That is contextual typing: the position supplied the type. The error proves it, since an `any` parameter would have accepted `n: number` with no complaint. This is the reader's first look at a theme lesson 14 argues in full, that a lot of annotation is unnecessary because the surrounding code already pins the type down.

### The first surprise: a `void` return accepts anything

```ts
const f: () => void = () => 42;
```

This compiles. A function typed to return nothing is satisfied by a function that returns `42`. That has to be true, because otherwise `array.forEach` could not exist as it does: `forEach`'s callback parameter is typed `(value: T) => void`, and everyday code passes it callbacks like `x => list.push(x)`, where `push` returns the new length. If a `void`-returning parameter type demanded a function that truly returns nothing, that ordinary line would fail every time. So the rule bends the other way: a `void` return type does not promise the function returns nothing, only that whatever it returns will be ignored. Read a `void` parameter as "the caller does not care what comes back," not as "nothing comes back."

### The second surprise: parameters are checked the other way round

```ts
type H = (x: string | number) => void;
const h: H = (x: string) => {};
```

```text
error TS2322: Type '(x: string) => void' is not assignable to type 'H'.
  Types of parameters 'x' and 'x' are incompatible.
    Type 'string | number' is not assignable to type 'string'.
```

`H` promises callers they may pass either a `string` or a `number`. `h` only knows how to handle a `string`, so a caller who follows `H`'s promise and passes a number would reach code that never expected one. The compiler rejects the assignment for the same reason lesson 11 rejects a value that does not live up to its target's demand. Notice the direction is the mirror image of the return-type surprise above. A function may return *less* than its type promises, since the caller only reads what it needs, but it must accept *everything* its type promises callers may send, since the caller decides what to send. Parameters are checked in the stricter direction; return types are checked in the looser one.

### The third surprise: writing it as a method turns the check off

```ts
interface Box {
  on(cb: (x: string | number) => void): void;
}
const b: Box = {
  on(cb: (x: string) => void) {},
};
```

This compiles. The parameter is exactly as narrow as the one that just failed, and this time nothing is reported. The only difference is how `on` was declared: `on(cb: ...): void` is method syntax, and a method's own parameters are checked more permissively than the identical parameter written as a stand-alone function type. This is a deliberate exemption, not an oversight, kept because a huge amount of the standard library describes callback-taking members as methods, and tightening the check there would break working code for a benefit the TypeScript team judged not worth it. The identical mistake is caught in one spelling and missed in the other, and which spelling you are reading decides whether the compiler is helping you on that line at all.

### The practical rule

Writing a callback member yourself, declare it with the property arrow form, `on: (cb: (x: string | number) => void) => void`, so a caller's narrower callback gets caught. Reading a library's declaration file, expect the method form, and remember it will wave through a callback narrower than the interface promises. A few declarations use overload signatures for the same member instead; that belongs with declaration files, in stage 5.

## Practice

1. ▢ Predict whether this compiles, and say why `push`'s return value is not a problem.

   ```ts
   const list: number[] = [];
   [1, 2, 3].forEach(x => list.push(x));
   ```

<details markdown="1"><summary>Check</summary>

It compiles. `forEach`'s callback parameter is typed to return `void`, and a `void` return type does not require the function to return nothing, only that its return value will be ignored. `push` returns the array's new length, and that number is simply discarded.

</details>

2. ▢ Predict the diagnostic, including its `TS` number.

   ```ts
   type Handler = (x: string | number) => void;
   const onValue: Handler = (x: string) => {};
   ```

<details markdown="1"><summary>Hint</summary>

Ask what a caller who believes `Handler`'s promise is allowed to pass, and whether `onValue` can handle it.

</details>

<details markdown="1"><summary>Check</summary>

`error TS2322: Type '(x: string) => void' is not assignable to type 'Handler'.` `Handler` promises callers they may pass a `number`, and `onValue` only handles a `string`, so a caller who trusts the type would reach unhandled code. Parameters are checked against everything the type promises callers may send.

</details>

3. ▢ Same mistake, different declaration. Does this compile?

   ```ts
   interface Emitter {
     on(x: string | number): void;
   }
   const e: Emitter = {
     on(x: string) {},
   };
   ```

<details markdown="1"><summary>Check</summary>

Yes, with no error at all. `on` is written as a method, checked more permissively than the identical parameter written as a property holding a function type, which item 2 showed being rejected. This is a deliberate exemption, made for the standard library's own declarations, not an oversight.

</details>

4. ▢ Predict the diagnostic, and say what supplied the type that made it possible.

   ```ts
   declare function withEach(xs: number[], cb: (n: number) => void): void;
   withEach([1, 2], n => {
     const s: string = n;
   });
   ```

<details markdown="1"><summary>Check</summary>

`error TS2322: Type 'number' is not assignable to type 'string'.` Nothing annotated `n`, yet the compiler knew it was `number`, because `withEach`'s declared parameter told it what filled that position. That is contextual typing, and the error is the proof it was really there.

</details>

5. ▢ A teammate declares `onError: (err: Error | string) => void` on one interface and `onError(err: Error | string): void` on another, otherwise identical. A handler written to accept only `Error` is assigned to each. Which assignment does the compiler reject?

<details markdown="1"><summary>Check</summary>

Only the first, the property form. It is checked in the strict parameter direction, so a handler that only accepts `Error` is rejected, since a caller may pass a plain `string`. The method form is checked permissively, so the identical narrower handler is accepted with no complaint. Same mistake, same intended type, two verdicts, decided entirely by which form the teammate happened to write.

</details>

## Real-world reps

- [ ] Take an interface you use that declares a callback member as a method, rewrite the member as a property arrow instead, and reassign the same implementation to see whether a previously silent mistake is now reported.
- [ ] Find a place in code you know that passes a callback to something like `forEach`, `map`, or an event listener, and check whether the callback's return value is used or silently ignored by a `void` parameter type.
- [ ] Tomorrow: open one declaration file from a library you depend on and note, for each callback-taking member, whether it is written as a method or as a property, since that choice already decided whether the compiler will catch a narrower callback there.

## Going further

- [TypeScript Handbook: Functions](https://www.typescriptlang.org/docs/handbook/2/functions.html): parameter and return annotations, contextual typing, and the method-versus-property distinction argued in full
- [TSConfig Reference: `strictFunctionTypes`](https://www.typescriptlang.org/tsconfig/#strictFunctionTypes): the flag that enables the parameter-direction check for function-type properties, and states that method parameters are exempt
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
