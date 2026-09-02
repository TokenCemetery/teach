---
title: 38. infer
description: Pull a type out of a position instead of asking the caller to name it
type: lesson
---

# Lesson 38. infer

**Mission link:** Owning a codebase means writing wrappers, decorators and utility types around other people's functions, and `infer` is how their return types and argument types travel into yours without anyone restating them by hand.
**Primary source:** [Handbook, Conditional Types, Microsoft](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html)
**Prerequisites:** [Lesson 37](0037-conditional-types.md), [Lesson 26](0026-generics-and-constraints.md)

## Warm-up

1. ▢ Lesson 37 built conditional types such as `T extends string ? never : T`, where the clause after `extends` is a pattern the compiler matches `T` against, and it stopped there: every example either kept `T` unchanged or returned a fixed type such as `never`, never a piece of `T` pulled out of the match itself. Guess: what would a keyword that names and captures part of the matched position let a conditional type do that a plain `extends` pattern alone cannot?

<details markdown="1"><summary>Check</summary>

It would let the true branch use a type that was never written down anywhere, one the compiler worked out from whatever shape actually matched the pattern. Lesson 37's conditionals could only answer yes or no and act on `T` as a whole; capturing a piece of the match means the answer can be a *part* of `T`, computed rather than named in advance. That keyword is `infer`, and it is this lesson's whole subject.

</details>

## Know this

### Naming what the pattern matched

A conditional type's `extends` clause is a pattern, and up to now that pattern has been something you write in full: `string`, an object shape, a fixed function signature. `infer` lets a pattern contain a blank instead: write `infer R` anywhere a type would normally go inside the `extends` clause, and if `T` matches, the compiler fills `R` in with whatever landed in that spot, then makes `R` available in the branch after the first `?`. The canonical case is pulling a function's return type out of its signature.

```ts
type Ret<T> = T extends (...a: never[]) => infer R ? R : never;

function f(): number {
  return 1;
}

type X = Ret<typeof f>;
const check: X = "not a number";
```

```text
error TS2322: Type 'string' is not assignable to type 'number'.
```

The pattern `(...a: never[]) => infer R` matches any function type, and `R` binds to whichever type sits in that function's return position; `f` returns `number`, so `R` is `number`, and the diagnostic on `check` names it directly, the same technique lesson 37 used to prove what a conditional evaluates to. Nothing here is new syntax beyond the blank: `infer R` is still just a type occupying a position inside a pattern that lesson 37 already taught you to read.

### The standard library is built from it

`ReturnType`, `Parameters` and `Awaited` are not special compiler magic sitting apart from what you just did; they are ordinary conditional types with an `infer` inside them, already sitting in the standard library, and reading their definitions is the fastest way to learn this feature because they are short and they are the real thing rather than a teaching example built to illustrate a point.

```ts
type ReturnType<T extends (...args: any) => any> = T extends (...args: any) => infer R ? R : any;
type Parameters<T extends (...args: any) => any> = T extends (...args: infer P) => any ? P : never;
```

`ReturnType` is `Ret` from the previous section with a constraint added to `T`; `Parameters` puts the `infer` on the other side, capturing the whole parameter list as a tuple instead of the return position.

```ts
function g(a: string, b: boolean): void {}
type P = Parameters<typeof g>;
const checkP: P = "nope";
```

```text
error TS2322: Type 'string' is not assignable to type '[a: string, b: boolean]'.
```

`Awaited` earns its keep on a promise.

```ts
type W = Awaited<Promise<boolean>>;
const checkW: W = "nope";
```

```text
error TS2322: Type 'string' is not assignable to type 'boolean'.
```

`Awaited<Promise<boolean>>` is `boolean`, exactly what `await`ing that promise would give you at run time. Its actual definition is longer than `ReturnType`'s, because it has to recurse through nested thenables and it uses `infer` more than once to do it; hold onto that fact, because the closing section of this lesson comes back to it.

### Constrained inference

`infer` can carry its own constraint, written `infer R extends SomeType`, which narrows what the compiler is willing to bind `R` to rather than accepting whatever showed up.

```ts
type FirstStr<T> = T extends [infer H extends string, ...unknown[]] ? H : never;

type H = FirstStr<["x", 1]>;
const checkH: H = 999;
```

```text
error TS2322: Type '999' is not assignable to type '"x"'.
```

`H` is the literal type `"x"`, the first element of the tuple, and the constraint on `infer H` is what makes the match specific to a string in that position rather than to anything at all. Drop the constraint and try the same pattern on a tuple whose first element is not a string, and the picture changes.

```ts
type First<T> = T extends [infer H, ...unknown[]] ? H : never;

type N = First<[1, 2]>;
const checkN: N = "not a number";
```

```text
error TS2322: Type '"not a number"' is not assignable to type '1'.
```

Unconstrained, `First` still matches, and `N` quietly becomes the number literal `1`; nothing in the type signals that a string was expected there, so a caller who wanted a string discovers the mismatch only later, wherever `N` gets used. Put the constraint back and feed the constrained version the same non-string tuple instead.

```ts
type NoMatch = FirstStr<[1, 2]>;
const checkNoMatch: NoMatch = "anything";
```

```text
error TS2322: Type '"anything"' is not assignable to type 'never'.
```

`FirstStr<[1, 2]>` is `never`, because the constraint made the whole pattern fail to match rather than merely bind `H` to something unwanted. That is exactly what the constraint buys: a mismatch shows up immediately as a failed match, at the type that consumes it, instead of succeeding with a type you would then have to write a second check to reject yourself.

### Inferring from a string pattern

`infer` can also sit inside a template literal type's pattern, capturing a slice of a string literal rather than a slice of a function or a tuple.

```ts
type Strip<S> = S extends `on${infer E}` ? E : never;

type E = Strip<"onClick">;
const checkE: E = 12345;
```

```text
error TS2322: Type '12345' is not assignable to type '"Click"'.
```

`E` is the literal type `"Click"`, the part of `"onClick"` after the fixed `on` prefix. What the backtick syntax itself can express and how it matches is lesson 39's material; the point here is narrower, that `infer` inside that syntax behaves exactly as it did against a function signature and a tuple: it names a position in the pattern and binds it to whatever matched there.

### The caller who benefits: a wrapper that stays in step

Here is where `infer` earns its keep rather than being a puzzle piece. Say you are writing a wrapper that adds logging around any function and must return whatever the wrapped function returns. Without `infer`, the wrapper needs a second type parameter for that return type, one the caller supplies alongside the function itself.

```ts
function withLogging<F extends (...args: never[]) => unknown, R>(
  fn: F
): (...args: Parameters<F>) => R {
  return (...args: Parameters<F>): R => {
    console.log("calling", fn.name);
    return fn(...args) as R;
  };
}

function add(a: number, b: number): number {
  return a + b;
}

const loggedAdd = withLogging<typeof add, string>(add);
const total: string = loggedAdd(1, 2);
```

This compiles, with no diagnostic at all, even though `add` returns a `number` and `total` is declared `string`. Nothing connects `R` to `F`'s own return type; `R` is a free parameter, so a caller can supply the correct one, `number`, or an incorrect one, `string`, and the compiler has no basis for objecting to either, since as far as it knows `R` might be whatever the caller says it is. Now drop `R` and let `infer` reach into `F` itself.

```ts
function withLogging<F extends (...args: never[]) => unknown>(
  fn: F
): (...args: Parameters<F>) => F extends (...args: never[]) => infer R ? R : never {
  return (...args: Parameters<F>) => {
    console.log("calling", fn.name);
    return fn(...args) as F extends (...args: never[]) => infer R ? R : never;
  };
}

const loggedAdd = withLogging(add);
const total: string = loggedAdd(1, 2);
```

```text
error TS2322: Type 'number' is not assignable to type 'string'.
```

The caller writes `withLogging(add)`, no type arguments at all; `F` is inferred from `add` the ordinary way lesson 26 already covers, and `infer R` then reaches inside that inferred `F` to name its return type, so `loggedAdd`'s return type is `add`'s return type, automatically, and moves with it if `add` is ever changed to return something else. The caller who benefits is anyone wrapping a function, for logging, retrying, memoizing or timing, who now writes one fewer type argument than the two-parameter version demanded, and who cannot make the mistake that version allowed, mismatching the wrapper's declared return type against what the wrapped function actually returns, because the parameter that mistake required no longer exists to be filled in wrong.

### Where to stop

Two things push `infer` from useful into a liability, and both are worth naming rather than discovering the hard way. The first is stacking several `infer` positions into one pattern; `Awaited`'s real definition, in the standard library itself, uses `infer` three times to recurse through nested thenables, and even there, in code written by the people who designed the feature, it is not something you read at a glance. One `infer` position, doing one job, is the shape every example in this lesson used; reach for two only when the standard library already shows you the exact shape to copy, and treat three as a sign to step back and ask whether a named helper type, built in stages, would leave a future reader less to hold in their head at once. The second is using `infer` to take apart a type nobody meant to expose, reaching into a library's internal return type or a class's private implementation shape to extract one piece of it. That piece is not a contract anyone promised to keep stable; the library's actual promise is its public API, and a type that depends on shape it never documented can break on a routine upgrade with no warning, because nothing about the change violated any promise that was actually made. Save `infer` for signatures you own or that a maintainer documents as part of the public surface, and stop before it becomes a bet on an implementation detail holding still.

## Practice

1. ▢ Predict the exact diagnostic, with its `TS` number.

   ```ts
   type Elem<T> = T extends (infer E)[] ? E : never;
   type Item = Elem<string[]>;
   const check: Item = 42;
   ```

<details markdown="1"><summary>Check</summary>

`error TS2322: Type 'number' is not assignable to type 'string'.` The pattern `(infer E)[]` matches an array type and binds `E` to its element type; `string[]`'s element type is `string`, so `Item` is `string`, and `42` fails against it.

</details>

2. ▢ A function is declared `function schedule(task: string, delayMs: number, repeat?: boolean): void {}`. Predict what `Parameters<typeof schedule>` is, then predict the diagnostic from assigning `"nope"` to a variable of that type.

<details markdown="1"><summary>Check</summary>

`Parameters<typeof schedule>` is the tuple `[task: string, delayMs: number, repeat?: boolean | undefined]`, one entry per parameter, in order, with the optional one kept optional. Assigning gives `error TS2322: Type 'string' is not assignable to type '[task: string, delayMs: number, repeat?: boolean | undefined]'.`

</details>

3. ▢ Predict whether each of these compiles, and name the diagnostic for whichever does not.

   ```ts
   type FirstNum<T> = T extends [infer A extends number, ...unknown[]] ? A : never;
   type A1 = FirstNum<[1, "y"]>;
   const checkA1: A1 = "wrong";

   type A2 = FirstNum<["y", 1]>;
   const checkA2: A2 = 0;
   ```

<details markdown="1"><summary>Hint</summary>

Ask, separately for each line, whether the tuple's first element satisfies the constraint on `infer A` before you ask what `A` becomes.

</details>

<details markdown="1"><summary>Check</summary>

Both lines fail to compile, but for different reasons. `[1, "y"]`'s first element is a `number`, so the pattern matches and `A1` becomes the literal `1`; assigning `"wrong"` gives `error TS2322: Type '"wrong"' is not assignable to type '1'.` `["y", 1]`'s first element is a `string`, which fails the `extends number` constraint on `infer A`, so the whole pattern fails to match and `A2` is `never`; assigning `0` gives `error TS2322: Type '0' is not assignable to type 'never'.`

</details>

4. ▢ Predict what `Base<"clickHandler">` is, given `` type Base<S> = S extends `${infer Name}Handler` ? Name : never; ``, and predict the diagnostic from assigning `0` to a variable of that type.

<details markdown="1"><summary>Check</summary>

`Base<"clickHandler">` is the literal type `"click"`, the part of the string before the fixed `Handler` suffix. Assigning `0` gives `error TS2322: Type '0' is not assignable to type '"click"'.`

</details>

5. ▢ This wrapper takes a function and a separate return-type parameter rather than using `infer`.

   ```ts
   function withLogging<F extends (...args: never[]) => unknown, R>(
     fn: F
   ): (...args: Parameters<F>) => R {
     return (...args: Parameters<F>): R => fn(...args) as R;
   }
   function double(n: number): number {
     return n * 2;
   }
   const loggedDouble = withLogging<typeof double, boolean>(double);
   const result: boolean = loggedDouble(4);
   ```

   Predict whether this compiles, and say what fact about the two type parameters explains your answer.

<details markdown="1"><summary>Check</summary>

Compiles, with no diagnostic at all, even though `double` returns a `number` and `result` is declared `boolean`. `R` is a free type parameter with nothing in the function's own signature connecting it to `F`'s actual return type, so the caller's choice of `R`, right or wrong, is accepted either way; this is exactly the gap `infer` closes, by computing the return type from `F` itself instead of asking the caller to name it.

</details>

## Real-world reps

- [ ] Open the declaration for one built-in utility type you use often but have never read, such as `NonNullable` or `InstanceType`, and check how many `infer` positions it uses and what each one is named.
- [ ] Find a function in a codebase you know that wraps another function and currently repeats or hard-codes that function's return type; sketch how an `infer` on the wrapped function's signature would let the caller stop supplying it.
- [ ] Tomorrow: search for a place where a type reaches into another module's non-exported shape with `infer` or an indexed access, and ask whether that shape is documented as stable or merely happened to work today.

## Going further

- [Handbook, Conditional Types, the infer keyword](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html): the section this lesson rests on, with the built-in utility types shown in their original context
- [Handbook, Utility Types](https://www.typescriptlang.org/docs/handbook/utility-types.html): every standard-library helper built this way, not only the three shown here
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
