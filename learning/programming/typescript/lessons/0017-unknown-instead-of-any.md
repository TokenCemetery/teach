---
title: 17. unknown Instead of any
description: One type accepts everything and lets you do nothing, the other accepts everything and checks nothing
type: lesson
---

# Lesson 17. unknown Instead of any

**Mission link:** Owning a codebase means being able to point at any value that arrived from outside your own code and say exactly what has been checked about it so far, and `unknown` is the type that keeps that answer honest instead of erased.
**Primary source:** [More on Functions, Other Types to Know About, TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/2/functions.html#unknown)
**Prerequisites:** [Lesson 12](0012-narrowing.md), [Lesson 8](0008-the-types-you-write.md)

## Warm-up

1. ▢ Lesson 8 typed `x` as `any` and ran `x.toUpperCase()` while `x` held `42`. Predict whether the compiler objects, and say in one sentence what `any` did to make that so.

<details markdown="1"><summary>Check</summary>

No objection. `any` switches off checking for whatever value carries it, so a method call that makes no sense for a number compiles anyway, and fails only when the program actually runs. This lesson gives you the type that behaves the opposite way.

</details>

## Know this

### The asymmetry

`unknown` and `any` both accept every value on the way in. `let u: unknown; u = 1; u = "x"; u = {};` compiles for all three assignments, exactly as it would with `any`. The difference is what happens on the way out. Assign `unknown` into a typed variable and the compiler stops you:

```ts
let u: unknown = "x";
const s: string = u;
// error TS2322: Type 'unknown' is not assignable to type 'string'.
```

`any` never does that. Assign `any` anywhere and it fits, silently, in both directions. `unknown` is compatible with every type in one direction only: values flow in freely, nothing flows out until you have shown the compiler what it actually is. That asymmetry is the whole idea. `unknown` is the honest type for a value you have not yet established anything about; `any` is not a type for not-yet-established, it is an instruction to stop asking.

### Nothing flows out, not even a method call

The restriction is not limited to assignment. Reading a property or calling an `unknown` value is refused before the assignment question even arises:

```ts
let u: unknown = "x";
u.length;
// error TS18046: 'u' is of type 'unknown'.
u();
// error TS18046: 'u' is of type 'unknown'.
```

Same diagnostic for a property read and for a call: the compiler treats `unknown` as carrying no operations at all until something narrows it, a stronger position than merely disallowing assignment, and one `any` never takes.

### Narrowing is how you leave `unknown`

Lesson 12 covered the narrowing operators. They are exactly what removes the restriction here, `typeof` included:

```ts
let u: unknown = "x";
if (typeof u === "string") {
  const s: string = u;
}
```

Inside the branch, `u` is `string`, the same way a `typeof` check narrowed a union in lesson 12. `unknown` is not a special case for narrowing; it behaves like any other type the checker can narrow with control flow, `instanceof`, `in`, or an equality check against a literal. The only thing unusual about `unknown` is how little it lets you do before you narrow it, which is the entire point of choosing it.

### `any` propagates, and does so silently

`any` differs from this in a way that is easy to underestimate. Every expression derived from an `any` value is itself `any`, and this is true no matter how far you chain it:

```ts
let a: any = { whatever: { deeply: { nested: "x" } } };
const n: number = a.whatever.deeply.nested;
// compiles
a();
// compiles
```

Reading a five-level-deep property that does not exist on any reasonable declared shape compiles, assigning it into a `number` compiles, and calling the whole thing as a function compiles. One `any`, placed anywhere in a chain, removes checking from every expression built on top of it, not just from the line where it was written, and there is no diagnostic for this, because there is no check that ran and failed; the check never happened. A codebase with an unexplained `any` near its edge is a codebase where a whole region has quietly stopped being checked, and nothing in the compiler's output will point at the region for you. That silence is the danger `unknown` avoids: every attempt to use an `unknown` value before narrowing it produces a diagnostic you can see, `TS18046`, right at the line where checking would otherwise have stopped.

### Catch variables

This is where most readers meet `unknown` first, whether they went looking for it or not. Under strict checking, the variable a `catch` block binds is typed `unknown`, controlled by the flag `useUnknownInCatchVariables`, on by default in the strict family, so using it as if it were a known shape fails the same way any other unnarrowed `unknown` does:

```ts
try {
  riskyOperation();
} catch (e) {
  const s: string = e;
  // error TS2322: Type 'unknown' is not assignable to type 'string'.
}
```

Narrow it and it behaves exactly like the earlier examples:

```ts
try {
  riskyOperation();
} catch (e) {
  if (e instanceof Error) {
    console.log(e.message);
    // compiles
  }
}
```

You can still write `catch (e: any)`, and the compiler allows it, which switches off checking for `e` the same way `any` does everywhere else. What you cannot write is a claim that the caught value is something more specific than `any` or `unknown`:

```ts
try {
  riskyOperation();
} catch (e: string) {
  console.log(e);
}
// error TS1196: Catch clause variable type annotation must be 'any' or 'unknown' if specified.
```

That refusal is worth a moment's thought. The language will not let you annotate a catch variable as `string`, or as any other specific type, because nothing can guarantee it: stage 1 covered the fact that makes this unavoidable, that JavaScript's `throw` accepts any value at all, not only `Error` instances, so a `catch` block has no basis for assuming a shape. `unknown` is the only honest answer, and `any` is the only other one the syntax permits.

### The practical rule

Reach for `unknown` at every point where a value arrives from outside your own code and you have not yet checked it: a parsed response, a caught exception, a value read out of storage, an argument on a boundary you do not control. Narrow it before you use it, with the same operators lesson 12 gave you. Lesson 18 covers what happens when someone reaches for an assertion instead of narrowing. Stage 5 is where narrowing an `unknown` value from a real boundary becomes the whole subject.

### Where `any` is still defensible

None of this makes `any` a mistake in every appearance. It is a reasonable, deliberate escape hatch in two situations: a boundary you are about to validate anyway, and a third-party type declaration you cannot fix yourself. Both are worth a comment saying which one it is and why. The defect this lesson argues against is not the keyword; it is an unexplained `any`, indistinguishable from one nobody noticed.

## Practice

1. ▢ Predict the diagnostic, with its `TS` number.

   ```ts
   function parse(raw: string): unknown {
     return JSON.parse(raw);
   }
   const value = parse("42");
   console.log(value.toFixed(2));
   ```

<details markdown="1"><summary>Check</summary>

`error TS18046: 'value' is of type 'unknown'.` `parse` returns `unknown`, so calling `.toFixed` on the result is refused before assignability even comes into it, the same way `u.length` was refused above.

</details>

2. ▢ Predict the diagnostic, with its `TS` number.

   ```ts
   function parse(raw: string): unknown {
     return JSON.parse(raw);
   }
   const value = parse("42");
   const n: number = value;
   ```

<details markdown="1"><summary>Check</summary>

`error TS2322: Type 'unknown' is not assignable to type 'number'.` `unknown` accepted the value coming out of `parse` with no complaint, but leaving `unknown` for a specific type on assignment is exactly what it refuses until you narrow.

</details>

3. ▢ Does this compile?

   ```ts
   function parse(raw: string): unknown {
     return JSON.parse(raw);
   }
   const value = parse('"hello"');
   if (typeof value === "string") {
     console.log(value.toUpperCase());
   }
   ```

<details markdown="1"><summary>Hint</summary>

Ask what lesson 12's `typeof` narrowing did to a union, then ask whether `unknown` is any different once you are inside the branch it narrows.

</details>

<details markdown="1"><summary>Check</summary>

Yes. Inside the `if`, `value` is narrowed to `string`, exactly as `typeof` narrowed a union in lesson 12, so `.toUpperCase()` is a check the compiler can verify rather than a guess.

</details>

4. ▢ Compare this with practice item 1. Predict whether either line reports anything.

   ```ts
   function parseAny(raw: string): any {
     return JSON.parse(raw);
   }
   const value = parseAny("42");
   console.log(value.toFixed(2));
   value();
   ```

<details markdown="1"><summary>Check</summary>

Neither line reports anything. `value` is `any`, so `.toFixed(2)` compiles regardless of whether the parsed value is actually a number, and calling `value()` as a function compiles too. Change only the return type from `unknown` to `any` and the diagnostic from item 1 disappears, not because the code became safer but because checking stopped.

</details>

5. ▢ Predict the diagnostic, with its `TS` number, and say which flag is responsible for `e`'s type before the annotation was added.

   ```ts
   function risky(): void {}
   try {
     risky();
   } catch (e: string) {
     console.log(e);
   }
   ```

<details markdown="1"><summary>Check</summary>

`error TS1196: Catch clause variable type annotation must be 'any' or 'unknown' if specified.` Without the annotation, `useUnknownInCatchVariables` (on by default under `strict`) makes `e` `unknown`, and the language accepts only `any` or `unknown` as an explicit override, never a more specific claim, because nothing about a `throw` guarantees what was thrown.

</details>

## Real-world reps

- [ ] Find a `catch` block in your own code and check what it does with the caught value before any narrowing. If it reads a property straight off it, that code is one non-`Error` throw away from a runtime failure the type checker would have caught as `unknown`.
- [ ] Find every `any` in a project you can see, including ones inside third-party type declarations you cannot edit, and for each one write, or confirm there already is, a comment saying whether it is a boundary you are about to validate or a declaration you cannot fix.
- [ ] Tomorrow: take one function that currently returns or accepts `any` and change the annotation to `unknown`. Fix every use the compiler now objects to, and notice how many of those objections point at a check your code was silently skipping.

## Going further

- [TypeScript Handbook: Everyday Types, `any`](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#any), for how `any` is introduced before this lesson contrasts it
- [TypeScript Design Goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals), for why an escape hatch exists at all rather than being removed
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
